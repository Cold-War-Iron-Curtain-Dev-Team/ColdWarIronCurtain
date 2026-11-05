"""Generate and validate native state-history experimental facilities.

Run from anywhere: python build_starting_facilities.py [--check]
No save files are edited. Dated history applies to bookmark initialization only.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import re

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('starting_facilities.csv')
BEGIN = '\t\t# BEGIN CWIC HISTORICAL EXPERIMENTAL FACILITIES'
END = '\t\t# END CWIC HISTORICAL EXPERIMENTAL FACILITIES'
TYPES = {'nuclear', 'air', 'land', 'naval', 'space'}
BOOKMARKS = ('1949.5.23', '1980.1.1')
# Centralize the four pre-existing, ungated grants in the same generated format.
# The generic Murmansk naval grant is replaced by the Krylov research site.
LEGACY = {213: ('naval', 3134), 219: ('nuclear', 6380),
          244: ('air', 9348), 653: ('land', 7228)}


def date(value):
    return tuple(map(int, value.split('.')[:3]))


def tokens(text):
    return [m for m in re.finditer(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}="#]+', text)
            if not m[0].startswith('#')]


def block(text, name):
    ts = tokens(text)
    for i in range(len(ts)-2):
        if [t[0] for t in ts[i:i+3]] == [name, '=', '{']:
            depth = 1
            for t in ts[i+3:]:
                depth += (t[0] == '{') - (t[0] == '}')
                if depth == 0:
                    return ts[i+2].end(), t.start()
    raise ValueError('Missing/unclosed block: ' + name)


def strip_generated(text):
    return re.sub(r'\n' + re.escape(BEGIN) + r'.*?' + re.escape(END) + r'\n', '\n', text, flags=re.S)


def load():
    states, provinces = {}, {}
    for path in (ROOT/'history/states').glob('*.txt'):
        text = path.read_text(encoding='utf-8-sig')
        ident = int(re.search(r'\bid\s*=\s*(\d+)', text)[1])
        assert ident not in states, ('Duplicate state ID', ident)
        states[ident] = (path, text)
        a, b = block(text, 'provinces')
        for province in re.findall(r'\d+', re.sub(r'#[^\n]*', '', text[a:b])):
            pid = int(province)
            assert pid not in provinces, ('Province in multiple states', pid)
            provinces[pid] = ident
    terrain = {}
    for line in (ROOT/'map/definition.csv').read_text().splitlines():
        cells = line.split(';')
        if len(cells) >= 6:
            terrain[int(cells[0])] = cells[4:6]
    with CATALOG.open(encoding='utf-8', newline='') as f:
        entries = list(csv.DictReader(f))
    by_state = defaultdict(list)
    for row in entries:
        pid = int(row['province'])
        assert row['specialization'] in TYPES
        assert terrain[pid][0] == 'land', ('Not a land province', row)
        if row['specialization'] == 'naval':
            assert terrain[pid][1] == 'true', ('Naval facility must be coastal', row)
        assert row['source'] and row['notes']
        date(row['available_from'])
        by_state[provinces[pid]].append(row)
    # The five facility types share a single per-state slot in this mod.
    for bookmark in BOOKMARKS:
        for ident, rows in by_state.items():
            assert sum(date(r['available_from']) <= date(bookmark) for r in rows) <= 1, (
                'Shared facility cap exceeded', ident, bookmark)
    return states, by_state, entries


def render(rows):
    lines = [BEGIN,
             '\t\t# Generated from _tools/facilities/starting_facilities.csv.',
             '\t\t# DLC-gated research infrastructure only; no scientists, weapons or project rewards.']
    for row in sorted(rows, key=lambda r: date(r['available_from'])):
        lines += [f"\t\t# {row['country']}: {row['site']}",
                  f"\t\t# Source: {row['source']}",
                  f"\t\t# {row['notes']}",
                  f"\t\t{row['available_from']} = {{",
                  '\t\t\tbuildings = {',
                  f"\t\t\t\t{row['province']} = {{",
                  f"\t\t\t\t\t{row['specialization']}_facility = {{",
                  '\t\t\t\t\t\tlevel = 1',
                  '\t\t\t\t\t\tallowed = { has_dlc = "Gotterdammerung" }',
                  '\t\t\t\t\t}', '\t\t\t\t}', '\t\t\t}', '\t\t}']
    lines += [END]
    return '\n'.join(lines) + '\n'


def desired(text, ident, rows):
    text = strip_generated(text)
    if ident in LEGACY:
        kind, province = LEGACY[ident]
        text = re.sub(r'\b' + kind + r'_facility\s*=\s*1\b\s*', '', text)
        # Remove the now-empty legacy province container, preserving adjacent buildings.
        text = re.sub(r'(?m)^\s*' + str(province) + r'\s*=\s*\{\s*\}\s*\n', '', text)
    if rows:
        _, end = block(text, 'history')
        # Keep the closing brace's existing indentation outside the generated block.
        start = text.rfind('\n', 0, end) + 1
        assert not text[start:end].strip()
        text = text[:start] + render(rows) + text[start:]
    return text


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true', help='Verify without writing')
    args = ap.parse_args()
    states, by_state, entries = load()
    changed = []
    for ident in sorted(set(by_state) | set(LEGACY)):
        path, text = states[ident]
        expected = desired(text, ident, by_state.get(ident, []))
        if text != expected:
            changed.append(path.name)
            if not args.check:
                raw = path.read_bytes()
                newline = '\r\n' if b'\r\n' in raw else '\n'
                bom = b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b''
                path.write_bytes(bom + expected.replace('\n', newline).encode('utf-8'))
    for bookmark in BOOKMARKS:
        active = [r for r in entries if date(r['available_from']) <= date(bookmark)]
        print(bookmark, len(active), 'facilities:', dict(sorted(Counter(r['country'] for r in active).items())))
    print(('OUT OF DATE: ' if args.check else 'Updated: ') + str(len(changed)) + ' state files')
    if args.check and changed:
        raise SystemExit('\n'.join(changed))


if __name__ == '__main__':
    main()
