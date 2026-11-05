#!/usr/bin/env python3
"""
C3 policy idea codemod (economy rework Pass 2b, docs/economy_map/PLAN.md section 4.4).

Moves content off the policy_<family>_temp_N ideas onto the content API (docs/economy_map/API.md):
  add_idea(s) = policy_F_temp_N, same family removed in the same block subtree
                                                    -> set_temp_variable + cwic_set_<F>_level
  lone add_idea(s) = policy_F_temp_N                -> same call (setting the level is the intent)
  swap_ideas = { remove_idea = A add_idea = B }     -> same call (same family)
  lone remove_idea(s) of F, followed by a setter of F in the same block -> dropped
  has_idea = policy_F_temp_N                        -> check_variable = { <level_var> = N }
Anything else is left untouched and written to the report with action 'residue'.

  python _tools/economy_migration/codemod_policy_ideas.py            dry run, writes the report only
  python _tools/economy_migration/codemod_policy_ideas.py --apply    rewrites the files
"""
import csv, glob, os, re, sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT = os.path.join(MOD, '..', 'docs', 'economy_map', 'codemod_policy_report.csv')

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codemod_money import CORE

CONTENT_DIRS = ['common', 'events']
OWNED_ELSEWHERE = {
    'PRC_50s.txt', 'FRA_1950s.txt', 'GDR_1960s.txt', 'SOV_Kaganovich.txt', 'SWE_50s.txt', 'YUG_70s.txt',
    'influence_scripted_diplomatic_actions.txt', 'CWIC_Crisis_Manager_Effects_with_Ideas.txt',
    'CWIC_Insurgency_Economy_Effects.txt', 'FRA_scripted_effects.txt', 'VIE_Effects.txt',
    'line_graph_scripted_effects.txt', 'Finance_Tab.txt', 'Indonesia.txt',
}

# idea family -> (cwic setter suffix, level variable, one-step setters)
FAMILY = {
    'military': ('army', 'army_level_value', ('increase_military_policy', 'decrease_military_policy')),
    'navy': ('navy', 'navy_level_value', ('increase_navy_policy', 'decrease_navy_policy')),
    'air': ('air', 'air_level_value', ('increase_air_policy', 'decrease_air_policy')),
    'space': ('space', 'space_level_value', ('increase_space_policy', 'decrease_space_policy')),
    'special': ('strategic_forces', 'strategic_forces_level_value',
                ('increase_strategic_forces_policy', 'decrease_strategic_forces_policy')),
    'healthcare': ('healthcare', 'healthcare_level_value', ('increase_healthcare_rate', 'lower_healthcare_rate')),
    'welfare': ('welfare', 'welfare_level_value', ('increase_welfare_rate', 'reduce_welfare_rate')),
    'education': ('education', 'education_level_value', ('increase_education_rate', 'decrease_education_rate')),
    'services': ('services', 'public_services_level_value', ('increase_service_policy', 'decrease_service_policy')),
    'cpi': ('policing', 'policing_level_value', ('increase_cpi_policy', 'decrease_cpi_policy')),
    'taxrate': ('tax', 'upper_tax_level_value', ('increase_tax_rate', 'lower_tax_rate')),
}
IDEA = re.compile(r'policy_(' + '|'.join(FAMILY) + r')_temp_(\d+)$')
TOKEN = re.compile(r'#[^\n]*|"[^"\n]*"|[{}=<>]|[^\s{}=<>#"]+')
ADDS = ('add_ideas', 'add_idea')
REMOVES = ('remove_ideas', 'remove_idea')


class Node:
    __slots__ = ('key', 'start', 'end', 'val', 'children', 'parent')

    def __init__(self, key, start):
        self.key, self.start, self.end = key, start, start + len(key)
        self.val, self.children, self.parent = None, None, None


def parse(text):
    toks = [(m.start(), m.end(), m.group()) for m in TOKEN.finditer(text) if m.group()[0] != '#']
    pos = [0]

    def block():
        out = []
        while pos[0] < len(toks):
            s, e, t = toks[pos[0]]
            if t == '}':
                return out
            pos[0] += 1
            if t in ('{', '=', '<', '>'):
                continue
            node = Node(t, s)
            node.end = e
            if pos[0] < len(toks) and toks[pos[0]][2] in ('=', '<', '>'):
                pos[0] += 1
                if pos[0] < len(toks):
                    vs, ve, vt = toks[pos[0]]
                    if vt == '{':
                        pos[0] += 1
                        node.children = block()
                        node.end = toks[pos[0]][1] if pos[0] < len(toks) else len(text)
                        pos[0] += 1
                    else:
                        pos[0] += 1
                        node.val, node.end = vt, ve
            out.append(node)
        return out

    root = Node('ROOT', 0)
    root.end = len(text)
    root.children = []
    while pos[0] < len(toks):
        root.children.extend(block())
        pos[0] += 1

    def link(n):
        for c in n.children or []:
            c.parent = n
            link(c)
    link(root)
    return root


def walk_nodes(node):
    for c in node.children or []:
        yield c
        yield from walk_nodes(c)


def line_of(text, pos):
    return text.count('\n', 0, pos) + 1


def call(fam, n):
    return 'set_temp_variable = { policy_level_target_temp = %d } cwic_set_%s_level = yes' % (n, FAMILY[fam][0])


def fam_of(name):
    m = IDEA.match(name or '')
    return (m.group(1), int(m.group(2))) if m else None


def convert(text, rel, rows):
    edits = []  # (start, end, replacement); replacement None = delete the statement
    used = set()
    root = parse(text)
    allnodes = list(walk_nodes(root))

    def rec(kind, n, detail):
        rows.append((rel, line_of(text, n.start), kind, detail))

    def in_span(n, scope):
        return scope.start <= n.start and n.end <= scope.end

    swap_inner = set()
    for n in allnodes:
        if n.key == 'swap_ideas' and n.children is not None:
            swap_inner.update(id(c) for c in n.children)

    adds, rems = [], []
    for n in allnodes:
        if id(n) in swap_inner:
            continue
        if n.key == 'swap_ideas' and n.children is not None:
            items = [(c.key, c.val) for c in n.children]
            if not any(fam_of(v) for k, v in items):
                continue
            ok = len(items) == 2 and all(k in ADDS + REMOVES and v for k, v in items)
            if ok:
                (k1, v1), (k2, v2) = items
                f1, f2 = fam_of(v1), fam_of(v2)
                addv = v1 if k1 in ADDS else (v2 if k2 in ADDS else None)
                if f1 and f2 and f1[0] == f2[0] and addv and k1 != k2:
                    used.add(id(n))
                    fam, lvl = fam_of(addv)
                    edits.append((n.start, n.end, call(fam, lvl)))
                    rec('set-level', n, 'swap_ideas -> %s level %d' % (FAMILY[fam][0], lvl))
                    continue
            used.add(id(n))
            rec('residue', n, 'swap_ideas not a single same-family swap')
            continue
        if n.key in ADDS + REMOVES:
            if n.children is not None:
                if any(fam_of(c.key) for c in n.children):
                    used.add(id(n))
                    rec('residue', n, 'list form %s with policy ideas' % n.key)
                continue
            f = fam_of(n.val)
            if f:
                (adds if n.key in ADDS else rems).append((n, f))
        elif n.key == 'has_idea' and n.children is None:
            f = fam_of(n.val)
            if f:
                used.add(id(n))
                edits.append((n.start, n.end, 'check_variable = { %s = %d }' % (FAMILY[f[0]][1], f[1])))
                rec('has_idea', n, '%s -> %s' % (n.val, FAMILY[f[0]][1]))

    # Adds: one set-level per add, claiming the same family's removes in the add's parent block subtree.
    for a, (fam, lvl) in adds:
        if id(a) in used:
            continue
        scope = a.parent
        same_add = [x for x, f in adds if f[0] == fam and id(x) not in used and x.parent is scope]
        same_rem = [x for x, f in rems if f[0] == fam and id(x) not in used and in_span(x, scope)]
        if len(same_add) > 1:
            for x in same_add + same_rem:
                used.add(id(x))
                rec('residue', x, 'family %s has %d adds in one block' % (fam, len(same_add)))
            continue
        used.add(id(a))
        edits.append((a.start, a.end, call(fam, lvl)))
        rec('set-level', a, '%s -> %s level %d (%d paired removes dropped)' % (a.val, FAMILY[fam][0], lvl, len(same_rem)))
        for r in same_rem:
            used.add(id(r))
            edits.append((r.start, r.end, None))

    # Lone removes: dropped when a setter of the family follows in the same block, else residue.
    for r, (fam, lvl) in rems:
        if id(r) in used:
            continue
        used.add(id(r))
        setters = set(FAMILY[fam][2]) | {'cwic_set_%s_level' % FAMILY[fam][0]}
        siblings = r.parent.children
        after = siblings[siblings.index(r) + 1:]
        if any(s.key in setters for s in after):
            edits.append((r.start, r.end, None))
            rec('drop-remove', r, '%s removed before a %s setter call' % (r.val, fam))
        else:
            rec('residue', r, 'lone remove of %s with no add and no later setter' % r.val)

    resolved = []
    for s, e, r in edits:
        if r is None:
            ls = text.rfind('\n', 0, s) + 1
            en = e
            while en < len(text) and text[en] in ' \t':
                en += 1
            if not text[ls:s].strip() and (en >= len(text) or text[en] in '\r\n'):
                s = ls
                if text[en:en + 2] == '\r\n':
                    en += 2
                elif text[en:en + 1] == '\n':
                    en += 1
            else:
                en = e
            resolved.append((s, en, ''))
        else:
            resolved.append((s, e, r))
    resolved.sort(key=lambda x: (x[0], x[1]))
    pieces, last = [], 0
    for s, e, r in resolved:
        if s < last:
            raise RuntimeError('overlapping edits in %s at line %d' % (rel, line_of(text, s)))
        pieces.append(text[last:s])
        pieces.append(r)
        last = e
    pieces.append(text[last:])
    return ''.join(pieces), len(resolved)


def main():
    apply = '--apply' in sys.argv
    rows, files, edits_total = [], 0, 0
    for d in CONTENT_DIRS:
        for path in sorted(glob.glob(os.path.join(MOD, d, '**', '*.txt'), recursive=True)):
            rel = os.path.relpath(path, MOD).replace(os.sep, '/')
            if os.path.normpath(rel) in CORE or os.path.basename(rel) in OWNED_ELSEWHERE:
                continue
            raw = open(path, 'rb').read()
            bom = raw.startswith(b'\xef\xbb\xbf')
            text = raw.decode('utf-8-sig', errors='surrogateescape')
            if 'policy_' not in text:
                continue
            n_before = len(rows)
            new, n = convert(text, rel, rows)
            if new != text:
                files += 1
                edits_total += n
                if apply:
                    data = new.encode('utf-8', errors='surrogateescape')
                    with open(path, 'wb') as f:
                        f.write((b'\xef\xbb\xbf' if bom else b'') + data)
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'line', 'action', 'detail'])
        w.writerows(rows)
    kinds = {}
    for r in rows:
        kinds[r[2]] = kinds.get(r[2], 0) + 1
    print('%s: %d files, %d edits, %s' % ('applied' if apply else 'dry run', files, edits_total, kinds))


if __name__ == '__main__':
    main()
