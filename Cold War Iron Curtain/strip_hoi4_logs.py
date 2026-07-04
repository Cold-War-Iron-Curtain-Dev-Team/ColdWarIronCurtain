#!/usr/bin/env python3
"""
Fast Git-backed HOI4 log stripper for CWIC.

Run from the playable mod folder:
  py strip_hoi4_logs.py dry-run
  py strip_hoi4_logs.py strip
  py strip_hoi4_logs.py restore

Only tracked .txt files under the selected scope are touched. Restore uses Git,
so it resets the stripped files back to HEAD rather than copying backups.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


STATE_DIR = ".cwic-log-strip"
MANIFEST = "last-strip.json"
RESTORE_PATHS = "restore-paths.tmp"
LOG_RE = re.compile(rb'(^|[^\w#])log\s*=\s*"([^"\\]|\\.)*"')


def run_git(args: list[str], cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def find_git_root(start: Path) -> Path:
    result = run_git(["rev-parse", "--show-toplevel"], start)
    return Path(result.stdout.decode("utf-8", errors="replace").strip()).resolve()


def to_git_path(path: Path) -> str:
    return path.as_posix()


def scope_prefix(git_root: Path, scope_root: Path) -> str:
    try:
        rel = scope_root.relative_to(git_root)
    except ValueError:
        raise SystemExit(f"Scope root is not inside Git repo: {scope_root}")
    rel_text = to_git_path(rel)
    return "" if rel_text == "." else rel_text


def display_path(git_root: Path, scope_root: Path, repo_path: str) -> str:
    full = git_root / repo_path
    try:
        return to_git_path(full.relative_to(scope_root))
    except ValueError:
        return repo_path


def git_tracked_txt_files(git_root: Path, scope_root: Path, path_filters: list[str]) -> list[str]:
    prefix = scope_prefix(git_root, scope_root)

    args = ["ls-files", "-z", "--"]
    if path_filters:
        for path_filter in path_filters:
            normalized = path_filter.replace("\\", "/").strip("/")
            args.append(f"{prefix}/{normalized}" if prefix else normalized)
    elif prefix:
        args.append(prefix)

    result = run_git(args, git_root)
    paths = [p.decode("utf-8", errors="surrogateescape") for p in result.stdout.split(b"\0") if p]
    paths = [p for p in paths if p.lower().endswith(".txt")]

    if prefix:
        allowed = prefix.rstrip("/") + "/"
        paths = [p for p in paths if p == prefix or p.startswith(allowed)]

    return paths


def dirty_tracked_files(git_root: Path) -> set[str]:
    result = run_git(["status", "--porcelain=v1", "-z", "--untracked-files=no"], git_root)
    dirty: set[str] = set()
    entries = [e for e in result.stdout.split(b"\0") if e]
    for entry in entries:
        text = entry.decode("utf-8", errors="surrogateescape")
        path = text[3:] if len(text) > 3 else text
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        dirty.add(path.replace("\\", "/"))
    return dirty


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def comment_start(line: bytes) -> int:
    in_string = False
    escaped = False
    for i, byte in enumerate(line):
        if in_string:
            if escaped:
                escaped = False
            elif byte == 0x5C:
                escaped = True
            elif byte == 0x22:
                in_string = False
        else:
            if byte == 0x22:
                in_string = True
            elif byte == 0x23:
                return i
    return -1


def strip_logs_from_line(line: bytes) -> tuple[bytes | None, int]:
    newline = b""
    body = line
    if body.endswith(b"\r\n"):
        body = body[:-2]
        newline = b"\r\n"
    elif body.endswith(b"\n"):
        body = body[:-1]
        newline = b"\n"
    elif body.endswith(b"\r"):
        body = body[:-1]
        newline = b"\r"

    idx = comment_start(body)
    if idx >= 0:
        code = body[:idx]
        comment = body[idx:]
    else:
        code = body
        comment = b""

    matches = list(LOG_RE.finditer(code))
    if not matches:
        return line, 0

    new_code = LOG_RE.sub(lambda m: m.group(1), code)
    new_code = re.sub(rb"\{\s*\}", b"{ }", new_code)

    if not new_code.strip():
        if comment.strip():
            return comment + newline, len(matches)
        return None, len(matches)

    return new_code + comment + newline, len(matches)


def strip_logs(data: bytes) -> tuple[bytes, int]:
    removed = 0
    out: list[bytes] = []
    for line in data.splitlines(keepends=True):
        new_line, count = strip_logs_from_line(line)
        removed += count
        if new_line is not None:
            out.append(new_line)
    return b"".join(out), removed


def scan(git_root: Path, paths: list[str]) -> list[dict[str, object]]:
    changes: list[dict[str, object]] = []
    for repo_path in paths:
        full = git_root / repo_path
        try:
            original = full.read_bytes()
        except OSError as exc:
            print(f"warning: could not read {repo_path}: {exc}", file=sys.stderr)
            continue

        stripped, removed = strip_logs(original)
        if removed:
            changes.append(
                {
                    "path": repo_path,
                    "removedLogs": removed,
                    "originalHash": sha256_bytes(original),
                    "strippedHash": sha256_bytes(stripped),
                    "strippedBytes": stripped,
                }
            )
    return changes


def write_manifest(scope_root: Path, git_root: Path, changes: list[dict[str, object]]) -> Path:
    state = scope_root / STATE_DIR
    state.mkdir(exist_ok=True)
    manifest_path = state / MANIFEST
    manifest = {
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "gitRoot": str(git_root),
        "scopeRoot": str(scope_root),
        "removedLogs": sum(int(c["removedLogs"]) for c in changes),
        "files": [
            {
                "path": c["path"],
                "removedLogs": c["removedLogs"],
                "originalHash": c["originalHash"],
                "strippedHash": c["strippedHash"],
            }
            for c in changes
        ],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest_path


def load_manifest(scope_root: Path) -> dict[str, object]:
    manifest_path = scope_root / STATE_DIR / MANIFEST
    if not manifest_path.exists():
        raise SystemExit("No strip manifest found. Run `py strip_hoi4_logs.py strip` first.")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def total_removed(changes: list[dict[str, object]]) -> int:
    return sum(int(c["removedLogs"]) for c in changes)


def command_dry_run(git_root: Path, scope_root: Path, args: argparse.Namespace) -> int:
    paths = git_tracked_txt_files(git_root, scope_root, args.paths)
    changes = scan(git_root, paths)
    dirty_targets = dirty_tracked_files(git_root).intersection(str(c["path"]) for c in changes)

    if args.list_files:
        for change in changes:
            mark = " DIRTY" if change["path"] in dirty_targets else ""
            shown = display_path(git_root, scope_root, str(change["path"]))
            print(f'{shown}: {change["removedLogs"]} log statement(s){mark}')

    print(f"Dry run: would remove {total_removed(changes)} log statement(s) from {len(changes)} file(s).")
    if dirty_targets:
        print(f"Blocked target files already dirty: {len(dirty_targets)}. Strip would refuse unless --allow-dirty is used.")
    return 0


def command_strip(git_root: Path, scope_root: Path, args: argparse.Namespace) -> int:
    paths = git_tracked_txt_files(git_root, scope_root, args.paths)
    changes = scan(git_root, paths)
    if not changes:
        print("No active log statements found in tracked .txt files.")
        return 0

    dirty_targets = dirty_tracked_files(git_root).intersection(str(c["path"]) for c in changes)
    if dirty_targets and not args.allow_dirty:
        print("Refusing to strip because target files already have uncommitted changes.", file=sys.stderr)
        print("These would be unsafe to restore with Git:", file=sys.stderr)
        for path in sorted(dirty_targets)[:50]:
            print(f"  {display_path(git_root, scope_root, path)}", file=sys.stderr)
        if len(dirty_targets) > 50:
            print(f"  ... and {len(dirty_targets) - 50} more", file=sys.stderr)
        print("Commit/stash those changes, or rerun with --allow-dirty if you accept the risk.", file=sys.stderr)
        return 2

    for change in changes:
        (git_root / str(change["path"])).write_bytes(change["strippedBytes"])  # type: ignore[arg-type]

    manifest_path = write_manifest(scope_root, git_root, changes)
    if args.list_files:
        for change in changes:
            shown = display_path(git_root, scope_root, str(change["path"]))
            print(f'{shown}: {change["removedLogs"]} log statement(s)')

    print(f"Stripped {total_removed(changes)} log statement(s) from {len(changes)} file(s).")
    print(f"Manifest: {manifest_path}")
    print("Restore with: py strip_hoi4_logs.py restore")
    return 0


def command_status(git_root: Path, scope_root: Path, args: argparse.Namespace) -> int:
    try:
        manifest = load_manifest(scope_root)
    except SystemExit as exc:
        print(exc)
        return 0

    files = list(manifest.get("files", []))
    changed_since_strip = 0
    missing = 0
    for entry in files:
        repo_path = str(entry["path"])
        full = git_root / repo_path
        if not full.exists():
            missing += 1
        elif sha256_bytes(full.read_bytes()) != entry.get("strippedHash"):
            changed_since_strip += 1

    print(f'Last strip: {manifest.get("createdAt")}')
    print(f"Files: {len(files)}")
    print(f'Removed logs: {manifest.get("removedLogs")}')
    print(f"Changed since strip: {changed_since_strip}")
    print(f"Missing stripped files: {missing}")
    if args.list_files:
        for entry in files:
            shown = display_path(git_root, scope_root, str(entry["path"]))
            print(f'{shown}: {entry["removedLogs"]} log statement(s)')
    return 0


def command_restore(git_root: Path, scope_root: Path, args: argparse.Namespace) -> int:
    manifest = load_manifest(scope_root)
    restore_paths: list[str] = []
    skipped: list[str] = []

    for entry in manifest.get("files", []):
        repo_path = str(entry["path"])
        full = git_root / repo_path
        if not full.exists():
            restore_paths.append(repo_path)
            continue
        if not args.force and sha256_bytes(full.read_bytes()) != entry.get("strippedHash"):
            skipped.append(repo_path)
            continue
        restore_paths.append(repo_path)

    if not restore_paths:
        print("No files restored.")
        if skipped:
            print(f"Skipped changed files: {len(skipped)}. Use --force to restore them anyway.")
        return 1 if skipped else 0

    state = scope_root / STATE_DIR
    state.mkdir(exist_ok=True)
    pathspec = state / RESTORE_PATHS
    pathspec.write_bytes(b"\0".join(p.encode("utf-8", errors="surrogateescape") for p in restore_paths) + b"\0")
    try:
        run_git(["restore", "--pathspec-from-file", str(pathspec), "--pathspec-file-nul"], git_root)
    finally:
        try:
            pathspec.unlink()
        except OSError:
            pass

    if args.list_files:
        for path in restore_paths:
            print(f"restored {display_path(git_root, scope_root, path)}")
        for path in skipped:
            print(f"skipped changed {display_path(git_root, scope_root, path)}")

    print(f"Restored {len(restore_paths)} file(s) with git restore.")
    if skipped:
        print(f"Skipped changed files: {len(skipped)}. Use --force to restore them anyway.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Fast Git-backed HOI4 log stripper.")
    parser.add_argument("action", choices=["status", "dry-run", "strip", "restore"], nargs="?", default="status")
    parser.add_argument("--root", default=".", help="Scope root. Defaults to current directory.")
    parser.add_argument("--paths", nargs="*", default=[], help="Optional tracked path filters under the scope, e.g. common events.")
    parser.add_argument("--list-files", action="store_true", help="Print per-file details.")
    parser.add_argument("--allow-dirty", action="store_true", help="Allow stripping files that were already dirty.")
    parser.add_argument("--force", action="store_true", help="Restore even if stripped files changed after stripping.")
    return parser


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    scope_root = Path(args.root).resolve()
    git_root = find_git_root(scope_root)

    if args.action == "dry-run":
        return command_dry_run(git_root, scope_root, args)
    if args.action == "strip":
        return command_strip(git_root, scope_root, args)
    if args.action == "restore":
        return command_restore(git_root, scope_root, args)
    if args.action == "status":
        return command_status(git_root, scope_root, args)
    raise AssertionError(args.action)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
