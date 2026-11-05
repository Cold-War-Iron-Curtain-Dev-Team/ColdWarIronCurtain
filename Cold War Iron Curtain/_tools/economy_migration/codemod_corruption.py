#!/usr/bin/env python3
"""
C5 corruption codemod (economy rework Pass 2b). Rewrites content writes to CorruptionLevel
into cwic_change_corruption (docs/economy_map/API.md). history/ is starting data and is skipped.

  python _tools/economy_migration/codemod_corruption.py            dry run
  python _tools/economy_migration/codemod_corruption.py --apply    rewrite
"""
import glob, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codemod_money import CONTENT_DIRS, CORE, MOD, SCOPE, TT

WRITE = re.compile(r'(add_to_variable|subtract_from_variable|set_variable)\s*=\s*\{\s*' + TT + r'(?:var\s*=\s*)?' + SCOPE +
                   r'CorruptionLevel\s*=\s*([-\w.@^:]+)\s*' + TT + r'\}')


def main(apply):
    total, files = 0, 0
    for d in CONTENT_DIRS:
        for path in sorted(glob.glob(os.path.join(MOD, d, '**', '*.txt'), recursive=True)):
            rel = os.path.normpath(os.path.relpath(path, MOD))
            if rel in CORE:
                continue
            raw = open(path, 'rb').read()
            bom = raw.startswith(b'\xef\xbb\xbf')
            text = raw.decode('utf-8-sig', errors='surrogateescape')
            out, last, n = [], 0, 0
            for m in WRITE.finditer(text):
                if text.rfind('#', text.rfind('\n', 0, m.start()) + 1, m.start()) != -1:
                    continue
                op, scope, value = m.group(1), m.group(2), m.group(3)
                body = 'set_temp_variable = { corruption_change_temp = %s }' % value
                if op == 'subtract_from_variable':
                    body += ' multiply_temp_variable = { corruption_change_temp = -1 }'
                elif op == 'set_variable':
                    body += ' subtract_from_temp_variable = { corruption_change_temp = CorruptionLevel }'
                body += ' cwic_change_corruption = yes'
                if scope:
                    body = '%s = { %s }' % (scope[:-1], body)
                print('%s:%d  %s' % (rel, text.count('\n', 0, m.start()) + 1, ' '.join(m.group(0).split())))
                out += [text[last:m.start()], body]
                last = m.end()
                n += 1
            if n:
                total += n
                files += 1
                if apply:
                    out.append(text[last:])
                    open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') +
                                           ''.join(out).encode('utf-8', errors='surrogateescape'))
    print('%d writes in %d files%s' % (total, files, ', applied' if apply else ' (dry run)'))


if __name__ == '__main__':
    main('--apply' in sys.argv)
