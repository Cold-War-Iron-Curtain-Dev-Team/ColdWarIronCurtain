"""Check deterministic generator output and unique ownership of generated effects without writes."""
from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

MOD = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(MOD / '_tools/mio'))
from validate_mios import parse


def main():
    checked = 0
    generated_effects = set()
    with TemporaryDirectory(prefix='cwic-generators-') as tmp:
        for name in ['companies', 'goods', 'cultures', 'religions', 'super_events']:
            script = MOD / '_tools' / name / ('build_' + name + '.py')
            spec = importlib.util.spec_from_file_location('check_' + name, script)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            outputs = []
            if hasattr(module, 'OUTPUTS'):
                replacements = []
                for template, dest in module.OUTPUTS:
                    actual = Path(dest)
                    target = Path(tmp) / actual.relative_to(MOD)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    replacements.append((template, str(target)))
                    outputs.append((actual, target))
                module.OUTPUTS = replacements
            for key, value in list(vars(module).items()):
                if key == 'OUT' or key.startswith('OUT_'):
                    actual = Path(value)
                    target = Path(tmp) / actual.relative_to(MOD)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    setattr(module, key, str(target))
                    outputs.append((actual, target))
            with redirect_stdout(io.StringIO()):
                try:
                    module.main()
                except SystemExit as exc:
                    if exc.code:
                        raise
            for actual, target in outputs:
                assert actual.read_bytes().replace(b'\r\n',b'\n') == target.read_bytes().replace(b'\r\n',b'\n'), f'Stale generated file: {actual}'
                checked += 1
                if actual.parent.name == 'scripted_effects':
                    generated_effects.update(n.key for n in parse(actual).children() if n.key)
    owners = {key: [] for key in generated_effects}
    for path in (MOD / 'common/scripted_effects').rglob('*.txt'):
        for node in parse(path).children():
            if node.key in owners: owners[node.key].append(str(path.relative_to(MOD)))
    duplicates = {key: paths for key,paths in owners.items() if len(paths) != 1}
    assert not duplicates, duplicates
    print(f'PASS: {checked} generated files reproduce exactly; {len(owners)} generated effects have one definition each.')


if __name__ == '__main__':
    main()
