"""Offline checks of the generated native history for both CWIC bookmarks."""
from collections import Counter
import re

from build_starting_facilities import ROOT, TYPES, BOOKMARKS, date, load, tokens, desired


def parse(text):
    ts = [m[0] for m in tokens(text)]
    pos = 0

    def read(nested=False):
        nonlocal pos
        result = []
        while pos < len(ts):
            key = ts[pos]
            pos += 1
            if key == '}':
                assert nested, 'Unexpected close'
                return result
            if key == '{':
                result.append(read(True))
            elif pos < len(ts) and ts[pos] == '=':
                pos += 1
                value = ts[pos]
                pos += 1
                if value == '{':
                    value = read(True)
                result.append((key, value))
            else:
                result.append(key)
        assert not nested, 'Unclosed block'
        return result

    return read()


def pairs(tree):
    return [node for node in tree if isinstance(node, tuple)]


def named(tree, key):
    return [v for k, v in pairs(tree) if k == key]


def one(tree, key):
    values = named(tree, key)
    assert len(values) == 1, (key, len(values))
    return values[0]


def evaluate(history, bookmark, dlc):
    building_types = {kind + '_facility' for kind in TYPES}
    owner = None
    facilities = {}
    changes = sorted([(date(k), v) for k, v in pairs(history)
                      if re.fullmatch(r'\d{4}\.\d+\.\d+', k) and date(k) <= date(bookmark)],
                     key=lambda item: item[0])
    for section in [history] + [v for _, v in changes]:
        for key, value in pairs(section):
            if key == 'owner':
                owner = value
            if key != 'buildings':
                continue
            for province, buildings in pairs(value):
                assert province not in building_types, 'Facility must be province-scoped'
                if not province.isdigit():
                    continue
                for kind, levels in pairs(buildings):
                    if kind not in building_types:
                        continue
                    # Every grant must use the native, conditional building-level form.
                    assert one(levels, 'level') == '1'
                    assert pairs(one(levels, 'allowed')) == [('has_dlc', '"Gotterdammerung"')]
                    if dlc:
                        facilities[(int(province), kind)] = 1
    return owner, facilities


def check_map_spawns(entries):
    # The final buildings.txt column is a sea-zone link, NOT a land province ID.
    # Resolve the actual spawn coordinates against the province bitmap instead.
    from PIL import Image
    image = Image.open(ROOT/'map/provinces.bmp').convert('RGB')
    colors = {}
    for line in (ROOT/'map/definition.csv').read_text().splitlines():
        cells = line.split(';')
        if len(cells) >= 6:
            colors[tuple(map(int, cells[1:4]))] = int(cells[0])
    spawns = set()
    for line in (ROOT/'map/buildings.txt').read_text().splitlines():
        cells = line.split(';')
        if len(cells) <= 6 or cells[1] not in ('special_project_facility_spawn', 'naval_base_spawn'):
            continue
        x, y = round(float(cells[2])), image.height-round(float(cells[4]))
        # Coast spawns sit on the land/sea edge; account for rounding at that edge.
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if 0 <= x+dx < image.width and 0 <= y+dy < image.height:
                    spawns.add((cells[1], colors.get(image.getpixel((x+dx, y+dy)))))
    for row in entries:
        kind = 'naval_base_spawn' if row['specialization'] == 'naval' else 'special_project_facility_spawn'
        assert (kind, int(row['province'])) in spawns, ('Missing map spawn', row['site'])
    print('PASS map spawn coordinates against actual province bitmap.')


def main():
    states, by_state, entries = load()
    # Include any facility grants outside the catalogue, rather than silently ignoring them.
    histories = {}
    for ident, (path, text) in states.items():
        if ident in by_state or re.search(r'\b(?:nuclear|air|land|naval|space)_facility\s*=', text):
            state = one(parse(text), 'state')
            assert one(state, 'id') == str(ident)
            histories[ident] = one(state, 'history')
    for bookmark in BOOKMARKS:
        expected = { (int(r['province']), r['specialization'] + '_facility'): r
                     for r in entries if date(r['available_from']) <= date(bookmark) }
        for dlc in (False, True):
            actual = {}
            countries = Counter()
            for ident, history in histories.items():
                owner, facilities = evaluate(history, bookmark, dlc)
                assert len(facilities) <= 1, ('Shared state facility cap', ident, bookmark)
                for key, value in facilities.items():
                    assert key not in actual
                    assert key in expected, ('Unexpected facility', ident, key)
                    assert owner == expected[key]['country'], ('Wrong owner', key, owner, expected[key]['country'])
                    actual[key] = value
                    countries[owner] += 1
            assert set(actual) == (set(expected) if dlc else set()), (bookmark, dlc)
            print('PASS', bookmark, 'DLC=' + str(dlc), len(actual), 'facilities', dict(sorted(countries.items())))
    # The rendered history is deterministic and regeneration does not alter it.
    for ident, rows in by_state.items():
        path, text = states[ident]
        assert desired(text, ident, rows) == text, ('Out of date', path)
    print('PASS province membership, coastal requirements, actual state IDs, ownership,')
    print('date eligibility, DLC conditions, shared state caps, balanced history and regeneration.')
    check_map_spawns(entries)


if __name__ == '__main__':
    main()
