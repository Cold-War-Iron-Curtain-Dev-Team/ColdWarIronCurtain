"""Add sea-crossing adjacencies (straits) between separate landmasses, like the hand-made Indonesian ones.

Run from the mod root:
    python _tools/heightmap/straits.py LON0 LON1 LAT0 LAT1 MAX_KM TAG "Comment" [--write]
Inside the lon/lat box, land provinces of TAG's states on different landmasses (4-connected land) are linked across
water no wider than MAX_KM: the straight line between their nearest shore pixels must cross only sea, and its 'through'
province is the sea province on that line touching both shores (else the one covering most of the line). Per pair of
landmasses at most PER_PAIR (2) links, each 150 km+ from the others; province pairs already in adjacencies.csv are skipped.
"""
import sys, numpy as np
from collections import Counter
from scipy import ndimage as nd
from scipy.spatial import cKDTree
import proj
from gcps import land_mask_and_ids
from border_owner import load_states
from mapfix import adjacency

PER_PAIR, SPREAD_KM, R = 2, 150.0, 6371.0


def xyz(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)] * R


def line(y0, x0, y1, x1):
    n = int(max(abs(y1 - y0), abs(x1 - x0))) + 1
    return np.rint(np.linspace(y0, y1, n)).astype(int), np.rint(np.linspace(x0, x1, n)).astype(int)


def main(lon0, lon1, lat0, lat1, max_km, tag, comment, write=False):
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    files, st, owner = load_states()
    lo, la = proj.grid()
    box = (lo >= lon0) & (lo <= lon1) & (la >= lat0) & (la <= lat1)
    land_ids = {p for p, v in kinds.items() if v == "land"}
    mine = {p for p in land_ids if owner.get(st.get(p)) == tag}
    land = np.isin(ids, list(land_ids))
    comp, _ = nd.label(land)
    sea = np.isin(ids, [p for p, v in kinds.items() if v == "sea"])
    coast = land & box & np.isin(ids, list(mine)) & (nd.binary_dilation(sea) & ~sea)
    ys, xs = np.nonzero(coast)
    P = xyz(lo[ys, xs], la[ys, xs])
    tree = cKDTree(P)
    nb = adjacency(ids)
    have = set()
    for l in open("map/adjacencies.csv", encoding="utf-8", errors="ignore"):
        q = l.split(";")
        if len(q) > 2 and q[0].isdigit() and q[1].isdigit():
            have |= {(int(q[0]), int(q[1])), (int(q[1]), int(q[0]))}
    cand = []
    for i, j in tree.query_pairs(max_km):
        a, b = (ys[i], xs[i]), (ys[j], xs[j])
        if comp[a] == comp[b]:
            continue
        cand.append((float(np.linalg.norm(P[i] - P[j])), a, b))
    cand.sort()
    best = {}  # province pair -> shortest link
    for d, a, b in cand:
        k = (int(ids[a]), int(ids[b]))
        if k not in best and k[::-1] not in best:
            best[k] = (d, a, b)
    picked, per = [], Counter()
    for k, (d, a, b) in sorted(best.items(), key=lambda kv: kv[1][0]):
        cp = tuple(sorted((int(comp[a]), int(comp[b]))))
        if per[cp] >= PER_PAIR or k in have or k[0] == k[1]:
            continue
        ya, xa = line(a[0], a[1], b[0], b[1])
        on = ids[ya, xa % W]
        mid = on[(on != k[0]) & (on != k[1])]
        if len(mid) == 0 or not all(kinds.get(int(v)) == "sea" for v in mid):
            continue  # crosses other land (or touches directly)
        ea, eb = xyz(lo[a], la[a])[0], xyz(lo[b], la[b])[0]
        if any(min(np.linalg.norm(ea - q[0]), np.linalg.norm(eb - q[1])) < SPREAD_KM or
               min(np.linalg.norm(ea - q[1]), np.linalg.norm(eb - q[0])) < SPREAD_KM for q in
               [x[3] for x in picked if x[2] == cp]):
            continue
        c = Counter(int(v) for v in mid)
        both = [s for s in c if nb.get(k[0], {}).get(s) and nb.get(k[1], {}).get(s)]
        through = max(both, key=c.get) if both else c.most_common(1)[0][0]
        picked.append((k, through, cp, (ea, eb), d))
        per[cp] += 1
    for k, t, cp, _, d in picked:
        print(f"  {k[0]};{k[1]} through {t}  {d:.0f} km  ({st.get(k[0])} - {st.get(k[1])})")
    print(f"{len(picked)} straits")
    if write and picked:
        raw = open("map/adjacencies.csv", "rb").read()
        nl = b"\r\n" if b"\r\n" in raw else b"\n"
        lines = raw.split(nl)
        end = next(i for i in range(len(lines) - 1, -1, -1) if lines[i].strip() and not lines[i].startswith(b"-1"))
        rows = [f"{k[0]};{k[1]};sea;{t};-1;-1;-1;-1;;{comment}".encode() for k, t, _, _, _ in picked]
        open("map/adjacencies.csv", "wb").write(nl.join(lines[:end + 1] + rows + lines[end + 1:]))


if __name__ == "__main__":
    a = sys.argv[1:]
    main(float(a[0]), float(a[1]), float(a[2]), float(a[3]), float(a[4]), a[5], a[6], "--write" in a[7:])
