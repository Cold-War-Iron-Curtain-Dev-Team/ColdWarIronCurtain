#!/usr/bin/env python3
"""Losslessly trim Japanese font atlases and archive editable source artwork."""

import argparse
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct


MOD = Path(__file__).resolve().parents[2]
REPO = MOD.parent
FONTS = MOD / 'gfx/fonts/japanese'
ARCHIVE = REPO / 'CWIC Backup/Source Art Moved From Active Mod'
SOURCE_ARCHIVE = ARCHIVE / MOD.name
STATE = REPO / '_local/mod-package-reduction'
MANIFEST = ARCHIVE / 'asset_cleanup_manifest.json'
MARGIN = 4
FIELDS = re.compile(rb'(\w+)=\s*(-?\d+)')
SCALE_H = re.compile(rb'(?m)^(common[^\r\n]*\bscaleH=)\d+')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fields(line):
    return {key.decode('ascii'): int(value) for key, value in FIELDS.findall(line)}


def contained(path, root):
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f'Path is outside the intended directory: {path}')
    return path


def font_info(fnt):
    metadata = fnt.read_bytes()
    common = re.search(rb'(?m)^common[^\r\n]*', metadata)
    if common is None:
        raise ValueError(f'No font dimensions: {fnt}')
    info = fields(common[0])
    # These are separate per-page descriptors with a shared atlas size. Leave
    # their page layout intact rather than give a page a different UV scale.
    if info['pages'] != 1:
        return None
    dds = fnt.with_suffix('.dds')
    if not dds.exists():
        raise ValueError(f'Missing sibling atlas: {dds}')
    with dds.open('rb') as stream:
        header = stream.read(128)
    if header[:4] != b'DDS ' or header[84:88] != b'DXT5':
        return None
    height, width = struct.unpack_from('<II', header, 12)
    mip_count = struct.unpack_from('<I', header, 28)[0]
    caps2 = struct.unpack_from('<I', header, 112)[0]
    if width % 4 or height % 4 or mip_count > 1 or caps2:
        raise ValueError(f'Unsupported DXT5 layout: {dds}')
    if (width, height) != (info['scaleW'], info['scaleH']):
        raise ValueError(f'Font/atlas dimension mismatch: {fnt}')
    expected = 128 + (width // 4) * (height // 4) * 16
    if dds.stat().st_size != expected:
        raise ValueError(f'Unexpected atlas data size: {dds}')
    chars = [fields(line) for line in metadata.splitlines() if line.startswith(b'char ')]
    declared = re.search(rb'(?m)^chars count=(\d+)', metadata)
    if not chars or declared is None or len(chars) != int(declared[1]):
        raise ValueError(f'Font character count mismatch: {fnt}')
    for char in chars:
        if (char['page'] != 0 or min(char['x'], char['y'], char['width'], char['height']) < 0
                or char['x'] + char['width'] > width
                or char['y'] + char['height'] > height):
            raise ValueError(f'Glyph outside its atlas: {fnt}, {char["id"]}')
    bottom = max(char['y'] + char['height'] for char in chars)
    new_height = min(height, ((bottom + MARGIN + 3) // 4) * 4)
    return {
        'fnt': fnt, 'dds': dds, 'metadata': metadata,
        'width': width, 'height': height, 'new_height': new_height,
        'glyph_count': len(chars), 'bottom': bottom,
        'saved': width * (height - new_height),
    }


def plan():
    fonts = []
    for fnt in sorted(FONTS.glob('*.fnt')):
        info = font_info(fnt)
        if info is not None and info['saved']:
            fonts.append(info)
    sources = []
    for base, _, names in os.walk(MOD):
        for name in names:
            source = Path(base) / name
            if source.suffix.lower() not in {'.psd', '.pdn'}:
                continue
            if source.is_symlink():
                raise ValueError(f'Source artwork is a symbolic link: {source}')
            contained(source, MOD)
            destination = contained(SOURCE_ARCHIVE / source.relative_to(MOD), SOURCE_ARCHIVE)
            contained(destination, REPO)
            if destination.exists():
                raise FileExistsError(f'Archive destination already exists: {destination}')
            sources.append({'source': source, 'destination': destination,
                            'bytes': source.stat().st_size, 'sha256': file_sha(source)})
    return fonts, sorted(sources, key=lambda row: str(row['source']))


def remove_temporary(path):
    contained(path, STATE)
    if path.parent.resolve() != STATE.resolve() or path.name not in {'staging', 'backup'}:
        raise ValueError(f'Unexpected temporary directory: {path}')
    if path.is_symlink():
        raise ValueError(f'Temporary directory is a link: {path}')
    def retry_readonly(func, name, error):
        if not isinstance(error, PermissionError):
            raise error
        os.chmod(name, stat.S_IWRITE | stat.S_IREAD)
        func(name)
    if path.exists():
        shutil.rmtree(path, onexc=retry_readonly)


def verify_pixels(original, cropped, width, height):
    # Independent decoding also catches header mistakes. The crop itself copies
    # original compressed blocks; Pillow is never used to encode an image.
    from PIL import Image, ImageChops
    with Image.open(BytesIO(original)) as old, Image.open(BytesIO(cropped)) as new:
        old.load()
        new.load()
        if new.size != (width, height):
            raise ValueError('Decoded cropped dimensions are incorrect')
        retained = old.crop((0, 0, width, height))
        difference = ImageChops.difference(retained, new)
        if any(minimum or maximum for minimum, maximum in difference.getextrema()):
            raise ValueError('Decoded font pixels changed')


def apply(fonts, sources):
    if not fonts and not sources:
        print('Already compact; no changes needed.')
        return
    staging, backup = STATE / 'staging', STATE / 'backup'
    if staging.exists() or backup.exists():
        raise FileExistsError(f'Previous staging/backup exists; inspect {STATE} before retrying')
    staging.mkdir(parents=True)
    backup.mkdir()
    font_records = []
    for item in fonts:
        fnt, dds = item['fnt'], item['dds']
        original = dds.read_bytes()
        size = item['width'] * item['new_height']
        header = bytearray(original[:128])
        struct.pack_into('<I', header, 12, item['new_height'])
        struct.pack_into('<I', header, 20, size)
        cropped = bytes(header) + original[128:128 + size]
        assert cropped[128:] == original[128:128 + size]
        metadata, substitutions = SCALE_H.subn(
            lambda match: match[1] + str(item['new_height']).encode(), item['metadata'])
        assert substitutions == 1
        assert SCALE_H.sub(rb'\g<1>HEIGHT', metadata) == SCALE_H.sub(
            rb'\g<1>HEIGHT', item['metadata'])
        verify_pixels(original, cropped, item['width'], item['new_height'])
        for path, old, new in ((dds, original, cropped), (fnt, item['metadata'], metadata)):
            (backup / path.name).write_bytes(old)
            (staging / path.name).write_bytes(new)
        font_records.append({
            'dds': dds.relative_to(REPO).as_posix(), 'fnt': fnt.relative_to(REPO).as_posix(),
            'width': item['width'], 'old_height': item['height'],
            'new_height': item['new_height'], 'glyph_count': item['glyph_count'],
            'glyph_bottom': item['bottom'], 'dds_before_sha256': sha(original),
            'dds_after_sha256': sha(cropped), 'fnt_before_sha256': sha(item['metadata']),
            'fnt_after_sha256': sha(metadata), 'bytes_saved': len(original) - len(cropped),
            'metadata_without_height_sha256': sha(SCALE_H.sub(rb'\g<1>HEIGHT', metadata)),
            'decoded_retained_pixels_identical': True,
        })
    for item in fonts:
        for path in (item['dds'], item['fnt']):
            assert file_sha(path) == file_sha(backup / path.name), f'File changed during staging: {path}'
    for item in sources:
        assert file_sha(item['source']) == item['sha256']

    changed_fonts, moved_sources = [], []
    previous_manifest = MANIFEST.read_bytes() if MANIFEST.exists() else None
    manifest_written = False
    try:
        for item in fonts:
            for path in (item['dds'], item['fnt']):
                os.replace(staging / path.name, path)
                changed_fonts.append(path)
        for item in sources:
            source, destination = item['source'], item['destination']
            contained(source, MOD)
            contained(destination, SOURCE_ARCHIVE)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists():
                raise FileExistsError(destination)
            source.rename(destination)
            moved_sources.append(item)
            assert file_sha(destination) == item['sha256']
        source_records = [{
            'original': item['source'].relative_to(REPO).as_posix(),
            'archived': item['destination'].relative_to(REPO).as_posix(),
            'bytes': item['bytes'], 'sha256': item['sha256'],
        } for item in sources]
        report = {
            'timestamp_utc': datetime.now(timezone.utc).isoformat(),
            'font_bytes_removed': sum(item['saved'] for item in fonts),
            'source_bytes_relocated': sum(item['bytes'] for item in sources),
            'fonts': font_records, 'source_art': source_records,
        }
        document = json.loads(MANIFEST.read_text(encoding='utf-8')) if MANIFEST.exists() else {'runs': []}
        document['runs'].append(report)
        ARCHIVE.mkdir(parents=True, exist_ok=True)
        temporary_manifest = MANIFEST.with_suffix('.json.tmp')
        temporary_manifest.write_text(json.dumps(document, indent=2) + '\n', encoding='utf-8')
        os.replace(temporary_manifest, MANIFEST)
        manifest_written = True
        check()
    except BaseException:
        for item in reversed(moved_sources):
            assert not item['source'].exists()
            item['destination'].rename(item['source'])
        for path in reversed(changed_fonts):
            os.replace(backup / path.name, path)
        if manifest_written:
            if previous_manifest is None:
                MANIFEST.unlink()
            else:
                MANIFEST.write_bytes(previous_manifest)
        raise
    remove_temporary(staging)
    remove_temporary(backup)


def check():
    document = json.loads(MANIFEST.read_text(encoding='utf-8'))
    latest_fonts, source_art = {}, {}
    for run in document['runs']:
        latest_fonts.update((item['dds'], item) for item in run['fonts'])
        source_art.update((item['archived'], item) for item in run['source_art'])
    glyphs = 0
    for record in latest_fonts.values():
        dds, fnt = REPO / record['dds'], REPO / record['fnt']
        contained(dds, FONTS)
        contained(fnt, FONTS)
        assert file_sha(dds) == record['dds_after_sha256'], dds
        assert file_sha(fnt) == record['fnt_after_sha256'], fnt
        item = font_info(fnt)
        assert item is not None and item['height'] == record['new_height']
        assert item['glyph_count'] == record['glyph_count']
        assert item['bottom'] + MARGIN <= item['height']
        assert sha(SCALE_H.sub(rb'\g<1>HEIGHT', item['metadata'])) == record['metadata_without_height_sha256']
        glyphs += item['glyph_count']
    for record in source_art.values():
        original, archived = REPO / record['original'], REPO / record['archived']
        contained(original, MOD)
        contained(archived, SOURCE_ARCHIVE)
        assert not original.exists(), original
        assert archived.stat().st_size == record['bytes'], archived
        assert file_sha(archived) == record['sha256'], archived
    print(f'Verified {len(latest_fonts)} atlases, {glyphs} glyph rectangles, '
          f'and {len(source_art)} archived originals.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--apply', action='store_true', help='Trim fonts and move PSD/PDN originals')
    mode.add_argument('--check', action='store_true', help='Verify changes against the saved manifest')
    args = parser.parse_args()
    if args.check:
        check()
        return
    fonts, sources = plan()
    font_bytes = sum(item['saved'] for item in fonts)
    source_bytes = sum(item['bytes'] for item in sources)
    print(f'Font cropping: {len(fonts)} atlases, {font_bytes:,} bytes ({font_bytes / 1024**2:.1f} MiB).')
    print(f'Source art: {len(sources)} files, {source_bytes:,} bytes ({source_bytes / 1024**2:.1f} MiB).')
    if args.apply:
        apply(fonts, sources)
    else:
        print('Dry run; use --apply to perform these changes.')


if __name__ == '__main__':
    main()
