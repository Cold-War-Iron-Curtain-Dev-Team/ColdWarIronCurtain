#!/usr/bin/env python3
"""
Removes the legacy money tooltip carriers that duplicate cwic_change_money's own tooltip:
  set_temp_variable = { x = N tooltip = adjust_money_tt | adjust_money_mil_tt }
A carrier is removed only when its enclosing block also changes money (cwic_change_money,
add_money_with_tooltip_effect or cwic_take_loan) and nothing else in that block reads x.

  python _tools/economy_migration/strip_money_tooltips.py            dry run
  python _tools/economy_migration/strip_money_tooltips.py --apply    rewrite
"""
import glob, os, re, sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'Cold War Iron Curtain'))
CARRIER = re.compile(r'[ \t]*set_temp_variable\s*=\s*\{\s*x\s*=\s*-?[\d.]+\s*tooltip\s*=\s*adjust_money(?:_mil)?_tt\s*\}[ \t]*\r?\n?')
MONEY = re.compile(r'cwic_change_money = yes|add_money_with_tooltip_effect = yes|cwic_take_loan = yes')
USES_X = re.compile(r'=\s*x(?![\w.])|(?<![\w.])x\s*[<>]|\[\?x[|\]]')


def block_bounds(text, pos):
    depth, start = 0, 0
    for i in range(pos - 1, -1, -1):
        if text[i] == '}':
            depth += 1
        elif text[i] == '{':
            if depth == 0:
                start = i
                break
            depth -= 1
    depth, end = 0, len(text)
    for i in range(pos, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            if depth == 0:
                end = i
                break
            depth -= 1
    return start, end


def main(apply):
    removed, kept = 0, []
    for path in sorted(glob.glob(os.path.join(MOD, 'common', '**', '*.txt'), recursive=True) +
                       glob.glob(os.path.join(MOD, 'events', '**', '*.txt'), recursive=True)):
        raw = open(path, 'rb').read()
        bom = raw.startswith(b'\xef\xbb\xbf')
        text = raw.decode('utf-8-sig', errors='surrogateescape')
        spans = []
        for m in CARRIER.finditer(text):
            if text.rfind('#', text.rfind('\n', 0, m.start()) + 1, m.start()) != -1:
                continue
            s, e = block_bounds(text, m.start())
            rest = text[s:m.start()] + text[m.end():e]
            line = text.count('\n', 0, m.start()) + 1
            if MONEY.search(rest) and not USES_X.search(re.sub(r'#[^\n]*', '', rest)):
                spans.append((m.start(), m.end()))
            else:
                kept.append('%s:%d' % (os.path.relpath(path, MOD), line))
        if spans and apply:
            out, last = [], 0
            for s, e in spans:
                out += [text[last:s]]
                last = e
            out.append(text[last:])
            open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + ''.join(out).encode('utf-8', errors='surrogateescape'))
        removed += len(spans)
    print('%d carriers %s; %d kept:' % (removed, 'removed' if apply else 'removable (dry run)', len(kept)))
    for k in kept:
        print('  ' + k)


if __name__ == '__main__':
    main('--apply' in sys.argv)
