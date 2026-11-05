#!/usr/bin/env python3
"""Restore audited vanilla English keys without overwriting existing CWIC text."""

import argparse
from collections import defaultdict
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
MOD = HERE.parents[1]
OUTPUT = MOD / 'localisation/english/CWIC_vanilla_recovery_l_english.yml'
SCRIPT_OUTPUT = MOD / 'common/scripted_localisation/CWIC_vanilla_loc_recovery.txt'
ENTRY = re.compile(r'^\s*([^\s:#]+):\d*[ \t]*(.*)$')
HEADER = re.compile(r'^\s*(l_[a-z_]+):\s*(?:#.*)?$')
ALIAS = re.compile(r'\$([A-Za-z_][A-Za-z0-9_.-]*)(?:\|[^$\n]*)?\$')
BRACKET = re.compile(r'\[([^\[\]]+)\]')
NAME = re.compile(r'\bname\s*=\s*"?([A-Za-z_][A-Za-z0-9_]*)')
BLOCK_TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}]')


def scan_localisation(root, excluded=()):
    definitions = defaultdict(list)
    files = set()
    for path in sorted(root.rglob('*.yml')):
        if 'english' not in path.name.lower():
            continue
        relative = path.relative_to(root).as_posix().lower()
        files.add(relative)  # Empty overrides also hide the vanilla file.
        if path in excluded:
            continue
        language = None
        for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
            header = HEADER.match(line)
            if header:
                language = header[1]
                continue
            match = ENTRY.match(line)
            if language == 'l_english' and match:
                definitions[match[1]].append({
                    'value': match[2].rstrip(), 'source': relative, 'line': number,
                })
    return definitions, files


def function_index(root, excluded=()):
    result = {}
    for path in sorted(root.glob('*.txt')):
        if path in excluded:
            continue
        text = path.read_text(encoding='utf-8-sig')
        for match in NAME.finditer(text):
            result[match[1]] = (path, match.start())
    return result


def function_block(name, location):
    path, offset = location
    text = path.read_text(encoding='utf-8-sig')
    starts = list(re.finditer(r'\bdefined_text\s*=\s*\{', text[:offset]))
    if not starts:
        raise ValueError(f'No defined_text block for {name}')
    start = starts[-1].start()
    depth = 0
    for match in BLOCK_TOKENS.finditer(text, start):
        if match[0] == '{':
            depth += 1
        elif match[0] == '}':
            depth -= 1
            if depth == 0:
                block = text[start:match.end()]
                if NAME.search(block)[1] != name:
                    raise ValueError(f'Wrong block extracted for {name}')
                return block
    raise ValueError(f'Unclosed defined_text block for {name}')


def bracket_functions(value):
    return {part.split('|', 1)[0].split('.')[-1] for part in BRACKET.findall(value)
            if not part.startswith('?')}


def build(game):
    seeds = {line.strip() for line in (HERE / 'recovery_keys.txt').read_text().splitlines()
             if line.strip() and not line.lstrip().startswith('#')}
    overrides = json.loads((HERE / 'cwic_aliases.json').read_text())
    assert set(overrides) <= seeds
    mod, mod_files = scan_localisation(MOD / 'localisation', excluded=(OUTPUT,))
    vanilla, _ = scan_localisation(game / 'localisation')
    inherited = {key for key, entries in vanilla.items()
                 if any(entry['source'] not in mod_files for entry in entries)}
    available = set(mod) | inherited
    selected = {}
    functions = {}
    mod_functions = function_index(MOD / 'common/scripted_localisation', excluded=(SCRIPT_OUTPUT,))
    vanilla_functions = function_index(game / 'common/scripted_localisation')
    skipped = sorted(seeds & available)
    pending = set(seeds - available)
    while pending:
        key = min(pending)
        pending.remove(key)
        if key in available or key in selected:
            continue
        if key not in vanilla:
            raise ValueError(f'Audited/dependency key is missing from installed vanilla: {key}')
        entries = vanilla[key]
        values = {entry['value'] for entry in entries}
        if len(values) != 1:
            raise ValueError(f'Ambiguous vanilla definitions for {key}')
        source = entries[-1]
        value = overrides.get(key, source['value'])
        if not value.startswith('"') or not value.endswith('"'):
            raise ValueError(f'Invalid quoted value: {key}')
        selected[key] = {
            'value': value, 'source': source['source'], 'source_line': source['line'],
            'cwic_alias': key in overrides, 'dependency': key not in seeds,
        }
        for match in ALIAS.finditer(value):
            alias = match[1]
            # Unknown names are engine runtime parameters, not text dependencies.
            if alias in vanilla and alias not in available and alias not in selected:
                pending.add(alias)
            if key in overrides and alias not in available and alias not in selected:
                raise ValueError(f'CWIC alias target is not available: {key} -> {alias}')
        needed_functions = bracket_functions(value) & set(vanilla_functions)
        for name in needed_functions - set(mod_functions) - set(functions):
            block = function_block(name, vanilla_functions[name])
            functions[name] = {'block': block, 'source': vanilla_functions[name][0].name}
            for text_key in re.findall(r'\blocalization_key\s*=\s*"?([A-Za-z0-9_.-]+)', block):
                if text_key not in available and text_key not in selected:
                    pending.add(text_key)

    assert seeds <= available | set(selected)
    for key, record in selected.items():
        assert key not in available
        for match in ALIAS.finditer(record['value']):
            if match[1] in vanilla:
                assert match[1] in available or match[1] in selected, (key, match[1])
    # Reject cycles among newly restored aliases rather than shipping a loop.
    visited, visiting = set(), set()
    def visit(key):
        if key in visiting:
            raise ValueError(f'Localisation alias cycle involving {key}')
        if key in visited:
            return
        visiting.add(key)
        for match in ALIAS.finditer(selected[key]['value']):
            if match[1] in selected:
                visit(match[1])
        visiting.remove(key)
        visited.add(key)
    for key in selected:
        visit(key)

    grouped = defaultdict(list)
    for key, record in selected.items():
        grouped[record['source']].append(key)
    lines = ['l_english:', '# Generated by _tools/localisation/restore_vanilla.py.',
             '# Missing audited keys only; existing CWIC text remains authoritative.',
             '# Source comments refer to the installed game localisation directory.']
    for source in sorted(grouped):
        lines.extend(['', '# Vanilla source: ' + source])
        for key in sorted(grouped[source]):
            record = selected[key]
            if record['cwic_alias']:
                lines.append(' # CWIC context: use the existing country name or 1949 history.')
            lines.append(f' {key}:0 {record["value"]}')
    output = ('\n'.join(lines) + '\n').encode('utf-8-sig')
    script = ['# Generated by _tools/localisation/restore_vanilla.py.',
              '# Localisation functions required by the restored vanilla text; no effects.']
    for name in sorted(functions):
        script.extend(['', '# Vanilla source: ' + functions[name]['source'], functions[name]['block']])
    script_output = ('\n'.join(script) + '\n').encode('utf-8') if functions else b''
    report = {
        'audited_keys': len(seeds), 'restored_entries': len(selected),
        'audited_entries_restored': len(seeds & set(selected)),
        'already_available_audited_keys': skipped,
        'additional_dependencies': sorted(set(selected) - seeds),
        'cwic_context_aliases': {key: overrides[key] for key in sorted(selected) if key in overrides},
        'scripted_localisation_functions': sorted(functions),
        'source_key_counts': {source: len(grouped[source]) for source in sorted(grouped)},
        'records': selected,
    }
    return output, script_output, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path,
                        default=Path('D:/SteamLibrary/steamapps/common/Hearts of Iron IV'))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output, script, report = build(args.game_dir)
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(output)
        if script:
            SCRIPT_OUTPUT.write_bytes(script)
        (HERE / 'recovery_manifest.json').write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    else:
        assert OUTPUT.read_bytes() == output, 'Recovery localisation needs regeneration'
        if script:
            assert SCRIPT_OUTPUT.read_bytes() == script, 'Scripted localisation needs regeneration'
    print(json.dumps({
        'audited_keys': report['audited_keys'],
        'audited_entries_restored': report['audited_entries_restored'],
        'already_available_audited_keys': len(report['already_available_audited_keys']),
        'restored_entries': report['restored_entries'],
        'additional_dependencies': report['additional_dependencies'],
        'cwic_context_aliases': len(report['cwic_context_aliases']),
        'scripted_localisation_functions': report['scripted_localisation_functions'],
    }, indent=2, ensure_ascii=False))
    print('Verified: all audited keys covered, no CWIC/inherited key collisions, '
          'vanilla aliases resolved, and no new alias cycles.')


if __name__ == '__main__':
    main()
