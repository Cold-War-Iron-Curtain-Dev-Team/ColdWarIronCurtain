"""Mend map/railways.txt links between provinces that don't touch (after province edits/reprojection): each gap gets the
shortest chain of touching land provinces in between. Gaps needing more than MAX_HOPS new provinces are only reported.
Run from the mod root:  python ../_tools/heightmap/railfix.py [--write]
"""
import sys, numpy as np
from collections import deque
from gcps import land_mask_and_ids

MAX_HOPS = 4


def land_graph(ids, kinds):
    nb = {}
    for a, b in ((ids[:, :-1], ids[:, 1:]), (ids[:-1], ids[1:]), (ids[:, -1:], ids[:, :1])):
        m = a != b
        for p, q in set(zip(a[m].tolist(), b[m].tolist())):
            if kinds.get(p) == kinds.get(q) == "land":
                nb.setdefault(p, set()).add(q); nb.setdefault(q, set()).add(p)
    return nb


def path(nb, a, b, limit=MAX_HOPS + 1):
    prev, frontier = {a: None}, [a]
    for _ in range(limit):
        nxt = []
        for p in frontier:
            for q in sorted(nb.get(p, ())):
                if q in prev:
                    continue
                prev[q] = p
                if q == b:
                    out = [b]
                    while prev[out[-1]] is not None:
                        out.append(prev[out[-1]])
                    return out[::-1]
                nxt.append(q)
        frontier = nxt
    return None


def mend(lines, nb, adj):
    fixed, left = 0, []
    out = []
    for lv, ps in lines:
        new = ps[:1]
        for a, b in zip(ps, ps[1:]):
            if (a, b) in adj:
                new.append(b)
                continue
            p = path(nb, a, b)
            if p:
                new += p[1:]; fixed += 1
            else:
                new.append(b); left.append((a, b))
        while True:  # A B A: the detour went into a spur province and back; the spur becomes its own short line
            i = next((i for i in range(len(new) - 2) if new[i] == new[i + 2]), None)
            if i is None:
                break
            out.append((lv, new[i:i + 2]))
            del new[i + 1:i + 3]
        out.append((lv, new))
    return out, fixed, left


def main(write):
    ids, kinds = land_mask_and_ids()
    nb = land_graph(ids, kinds)
    adj = {(p, q) for p, s in nb.items() for q in s}
    for l in open("map/adjacencies.csv", encoding="latin-1").read().splitlines()[1:]:
        q = l.split(";")
        if len(q) > 2 and q[0].isdigit():
            adj |= {(int(q[0]), int(q[1])), (int(q[1]), int(q[0]))}
    raw = open("map/railways.txt", "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    lines = [(int(v[0]), list(map(int, v[2:]))) for v in (l.split() for l in raw.split(nl)) if v]
    out, fixed, left = mend(lines, nb, adj)
    print("gaps mended", fixed, "left (too far apart, fix by hand)", left)
    if write:
        open("map/railways.txt", "wb").write(nl.join(f"{lv} {len(ps)} {' '.join(map(str, ps))} ".encode() for lv, ps in out) + nl)


if __name__ == "__main__":
    nb = {1: {2}, 2: {1, 3}, 3: {2}}
    assert mend([(3, [1, 3])], nb, {(1, 2), (2, 1), (2, 3), (3, 2)})[0] == [(3, [1, 2, 3])]
    nb = {5: {6, 7}, 6: {5}, 7: {5}}  # gap 6->7 routes back through 5: spur 6 becomes its own line
    assert mend([(3, [5, 6, 7])], nb, {(a, b) for a, t in nb.items() for b in t})[0] == [(3, [5, 6]), (3, [5, 7])]
    main("--write" in sys.argv[1:])
