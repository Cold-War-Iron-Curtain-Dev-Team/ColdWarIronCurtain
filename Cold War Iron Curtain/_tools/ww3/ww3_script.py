"""Small ordered Clausewitz reader used by the WW3 generator and offline tests."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def tokenize(text):
    return re.findall(r'"(?:\\.|[^"\\])*"|[{}=<>]|[^\s{}=<>]+', re.sub(r'#[^\n]*', '', text))


def parse(text):
    ts = tokenize(text)
    pos = 0

    def read(nested=False):
        nonlocal pos
        result = []
        while pos < len(ts):
            key = ts[pos]
            pos += 1
            if key == '}':
                assert nested, 'Unexpected closing brace'
                return result
            if key == '{':
                result.append(read(True))
            elif pos < len(ts) and ts[pos] in ('=', '<', '>'):
                op = ts[pos]
                value = ts[pos+1]
                pos += 2
                if value == '{':
                    value = read(True)
                result.append((key, op, value))
            else:
                result.append(key)
        assert not nested, 'Unclosed block'
        return result
    return read()


def pairs(tree):
    return [n for n in tree if isinstance(n, tuple)]


def named(tree, key):
    return [v for k, _, v in pairs(tree) if k == key]


def one(tree, key, default=None):
    values = named(tree, key)
    assert len(values) <= 1, ('Duplicate key', key)
    return values[0] if values else default


def write(path, text, bom=False):
    """Preserve existing newline style and BOM when editing an existing file."""
    path = ROOT/path
    raw = path.read_bytes() if path.exists() else b''
    newline = '\r\n' if b'\r\n' in raw else '\n'
    prefix = b'\xef\xbb\xbf' if bom or raw.startswith(b'\xef\xbb\xbf') else b''
    path.write_bytes(prefix + text.replace('\r\n', '\n').replace('\n', newline).encode('utf-8'))


def replace_block(text, name, replacement):
    """Replace a uniquely named block without reformatting the rest of its file."""
    matches = list(re.finditer(r'(?m)^[ \t]*'+re.escape(name)+r'\s*=\s*\{', text))
    assert len(matches) == 1, (name, len(matches))
    start = matches[0].start()
    brace = text.index('{', matches[0].start())
    depth = 0
    for m in re.finditer(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}]', text[brace:]):
        if m[0] not in ('{', '}'):
            continue
        depth += 1 if m[0] == '{' else -1
        if not depth:
            return text[:start] + replacement.rstrip() + text[brace+m.end():]
    raise AssertionError(('Unclosed block', name))
