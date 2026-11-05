"""More control points: every named victory point matched to GeoNames by name near where the current warp puts it.

Run from the mod root:  python _tools/heightmap/vp_gcps.py <cities1000.txt> <warp.npz> [radius_km=300]
Position = the VP icon in map/unitstacks.txt (type 38). A match needs the same name (GeoNames name, ascii or alternate
names, so historical spellings count) within radius_km of the prediction; the most populous wins, and a name with two
similar-sized candidates far apart is skipped. Points whose spline residual stays far off are dropped as wrong matches or
deliberately moved cities. Writes gcps_vp.json; build.warp() uses it together with gcps.json.
"""
import json, re, sys, unicodedata, numpy as np
from collections import defaultdict
from scipy.interpolate import RBFInterpolator
from scipy.spatial import cKDTree

W, H = 5632, 2048
R_EARTH = 6371.0


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def unit(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def km(lo0, la0, lo1, la1):
    return R_EARTH * np.linalg.norm(unit(lo0, la0) - unit(lo1, la1), axis=-1)  # chord ~ arc at these distances


def vps():
    names = {}
    import glob
    for f in glob.glob("localisation/english/**/*.yml", recursive=True):
        for m in re.finditer(r'VICTORY_POINTS_(\d+):\d* "([^"]+)"', open(f, encoding="utf-8-sig", errors="ignore").read()):
            names.setdefault(int(m.group(1)), m.group(2))
    pos = {}
    for line in open("map/unitstacks.txt"):
        p = line.split(";")
        if len(p) > 4 and p[1] == "38":
            pos[int(p[0])] = (float(p[2]), H - float(p[4]))
    return [(pid, n, *pos[pid]) for pid, n in names.items() if pid in pos]


def fit(P, LL, smoothing):
    """pixel -> lon/lat spline with seam copies (as build.warp)."""
    P2 = np.r_[P, P[P[:, 0] < W / 4] + (W, 0), P[P[:, 0] > W * 3 / 4] - (W, 0)]
    L2 = np.r_[LL, LL[P[:, 0] < W / 4] + (360, 0), LL[P[:, 0] > W * 3 / 4] - (360, 0)]
    return RBFInterpolator(P2, L2, kernel="thin_plate_spline", smoothing=smoothing)


def main(geonames, warp_npz, radius=300.0):
    w = np.load(warp_npz)
    lo_w, la_w = w["lo"], w["la"]
    by_name = defaultdict(list)
    G = []
    for line in open(geonames, encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        k = len(G)
        G.append((float(f[5]), float(f[4]), int(f[14] or 0)))
        for n in {norm(f[1]), norm(f[2]), *(norm(a) for a in f[3].split(",") if a)}:
            if n:
                by_name[n].append(k)
    G = np.array(G)

    pts = []
    for pid, name, x, y in vps():
        cand = by_name.get(norm(name), [])
        if not cand:
            continue
        plo, pla = lo_w[int(y), int(x) % W], la_w[int(y), int(x) % W]
        c = np.array(cand)
        d = km(plo, pla, G[c, 0], G[c, 1])
        c, d = c[d < radius], d[d < radius]
        if not len(c):
            continue
        best = c[np.argmax(G[c, 2])]
        rivals = c[(G[c, 2] > 0.5 * G[best, 2]) & (km(G[best, 0], G[best, 1], G[c, 0], G[c, 1]) > 50)]
        if len(rivals):
            continue  # two towns of that name in reach: ambiguous
        glo = plo + (G[best, 0] - plo + 180) % 360 - 180  # keep lon continuous with the map (seam)
        pts.append((pid, name, x, y, glo, G[best, 1], int(G[best, 2])))
    print("victory points matched:", len(pts))

    P = np.array([p[2:4] for p in pts], np.float64)
    LL = np.array([p[4:6] for p in pts], np.float64)
    keep = np.ones(len(P), bool)
    for it in range(4):  # robust refit: drop points far off the spline through the others
        f = fit(P[keep], LL[keep], 5.0)
        r = km(*f(P).T, *LL.T)
        lim = max(80.0, 3 * np.median(r[keep]))
        print(f"pass {it}: kept {keep.sum()}, median residual {np.median(r[keep]):.0f} km, limit {lim:.0f} km")
        keep = r < lim

    # held-out check: 10 folds, error of the new fit vs the current warp at points it did not see
    rng = np.random.default_rng(0)
    fold = rng.integers(0, 10, len(P))
    K = np.nonzero(keep)[0]
    for s in (1.0, 5.0, 20.0):
        e_new = np.zeros(len(P))
        for k in range(10):
            tr, te = K[fold[K] != k], K[fold[K] == k]
            e_new[te] = km(*fit(P[tr], LL[tr], s)(P[te]).T, *LL[te].T)
        print(f"held-out error, smoothing {s}: median {np.median(e_new[K]):.0f} km, 90% {np.percentile(e_new[K], 90):.0f} km")
    e_old = km(lo_w[P[K, 1].astype(int), P[K, 0].astype(int) % W], la_w[P[K, 1].astype(int), P[K, 0].astype(int) % W], *LL[K].T)
    print(f"current warp at the same points: median {np.median(e_old):.0f} km, 90% {np.percentile(e_old, 90):.0f} km")

    json.dump([{"name": pts[i][1], "x": pts[i][2], "y": pts[i][3], "lon": pts[i][4], "lat": pts[i][5]} for i in K],
              open("_tools/heightmap/gcps_vp.json", "w"), indent=0)
    dropped = sorted((r[i], pts[i][1]) for i in np.nonzero(~keep)[0])[::-1][:15]
    print("largest dropped:", ", ".join(f"{n} {d:.0f} km" for d, n in dropped))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], *map(float, sys.argv[3:]))
