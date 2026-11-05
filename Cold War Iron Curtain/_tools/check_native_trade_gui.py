"""Check the native trade windows required by the engine despite CWIC's GUI override."""
import argparse
from pathlib import Path
import sys

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD / '_tools/mio'))
from validate_mios import parse, walk


def definitions(path):
    return {n.get('name'): n for root in parse(path).children('guiTypes')
            for n in root.children() if n.get('name')}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--game-dir', type=Path, required=True)
    args = cli.parse_args()
    native = definitions(args.game_dir / 'interface/countrytradeview.gui')
    active = definitions(MOD / 'interface/countrytradeview.gui')
    compatibility = definitions(MOD / 'interface/CWIC_trade_compatibility.gui')
    assert not active.keys() & compatibility.keys(), 'Duplicate native GUI types'
    active.update(compatibility)
    assert native.keys() <= active.keys(), sorted(native.keys() - active.keys())
    for name in ['auto_import_priority_window', 'auto_import_priority_entry']:
        children = lambda node: {n.get('name') for n in walk(node) if n.get('name')}
        assert children(native[name]) <= children(active[name]), name
    print('PASS: all native trade GUI types resolve; priority window and entry retain every required child widget.')


if __name__ == '__main__':
    main()
