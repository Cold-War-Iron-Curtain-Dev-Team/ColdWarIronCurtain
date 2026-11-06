"""Move state borders flagged by border_geo.py (feature "river") onto their river in map/provinces.bmp.

Near the border (BAND px of both the border and the river) the river pixels split the land into bank pieces. A piece
that is mostly one state but holds a strip of the other (the strip between the old border and the river) gives that
strip to the majority state, each pixel to the nearest province of it. A piece with no clear majority (the river ends
inside the band, so both banks join) is skipped. A pair is undone if any province it touches would split, vanish or
lose more than half its pixels.
Run from the mod root:  python ../_tools/heightmap/border_snap.py <border_geo.csv> [--write]
"""
import csv, io, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from gcps import land_mask_and_ids
from border_geo import states

BAND, MINORITY = 6, 0.35


def snap(P, S, river, a, b):
    """New province ids for crop P (states S) moving a|b onto the river; returns (P', moved px) or (P, 0)."""
    ab = (S == a) | (S == b)
    border = ab & ((nd.grey_dilation(S, 3) != S) | (nd.grey_erosion(S, 3) != S)) & (
        nd.binary_dilation(S == a) & nd.binary_dilation(S == b))
    band = ab & (nd.distance_transform_edt(~border) <= BAND) & (nd.distance_transform_edt(~river) <= BAND) & ~river
    lab, n = nd.label(band)
    take = np.zeros(S.shape, bool)
    owner = np.zeros(S.shape, np.int64)
    for c in range(1, n + 1):
        m = lab == c
        na, nb = (S[m] == a).sum(), (S[m] == b).sum()
        minority = min(na, nb) / (na + nb)
        if 0 < minority <= MINORITY:
            win = a if na > nb else b
            mv = m & (S != win)
            take |= mv
            owner[mv] = win
    if not take.any():
        return P, 0
    out = P.copy()
    for win in np.unique(owner[take]):
        mv = take & (owner == win)
        src = (S == win) & ~take
        _, (iy, ix) = nd.distance_transform_edt(~src, return_indices=True)
        out[mv] = P[iy[mv], ix[mv]]
    return out, int(take.sum())


def ok(before, after):
    for p in np.unique(before[before != after]):
        n0, n1 = (before == p).sum(), (after == p).sum()
        if n1 < 0.5 * n0 or nd.label(after == p)[1] > nd.label(before == p)[1]:
            return False
    return True


def main(csv_path, write):
    ids, kinds = land_mask_and_ids()
    st, info = states()
    name = {v[0]: s for s, v in info.items()}
    river = np.array(Image.open(io.BytesIO(open("map/rivers.bmp", "rb").read()))) <= 11
    S = np.vectorize(lambda p: st.get(p, 0) if kinds.get(p) == "land" else 0, otypes=[np.int64])(ids)
    new = ids.copy()
    rows = [r for r in csv.DictReader(open(csv_path, encoding="utf-8")) if r["feature"] == "river"]
    done = 0
    for r in rows:
        a, b = name[r["state_a"]], name[r["state_b"]]
        ys, xs = np.nonzero(((S == a) & nd.binary_dilation(S == b)) | ((S == b) & nd.binary_dilation(S == a)))
        if not len(ys):
            continue
        s = np.s_[max(ys.min() - 20, 0):ys.max() + 21, max(xs.min() - 20, 0):xs.max() + 21]  # no x wrap: none at the seam
        P2, moved = snap(new[s], S[s], river[s], a, b)
        # contiguity is judged on the crop padded by 20 px; provinces are rarely larger than that around a border
        if moved and ok(new[s], P2):
            new[s] = P2
            S[s] = np.vectorize(lambda p: st.get(p, 0) if kinds.get(p) == "land" else 0, otypes=[np.int64])(P2)
            done += 1
            print(f"{r['state_a']} | {r['state_b']}: {moved} px moved onto the river")
        else:
            print(f"{r['state_a']} | {r['state_b']}: skipped ({'no clear bank' if not moved else 'would split/shrink a province'})")
    print(f"snapped {done}/{len(rows)}")
    if write and done:
        col = {}
        for l in open("map/definition.csv", encoding="latin-1"):
            q = l.split(";")
            if q[0].isdigit():
                col[int(q[0])] = (int(q[1]), int(q[2]), int(q[3]))
        pm = np.array(Image.open(io.BytesIO(open("map/provinces.bmp", "rb").read())).convert("RGB"))
        ch = new != ids
        pm[ch] = np.array([col[int(v)] for v in new[ch]], np.uint8)
        Image.fromarray(pm).save("map/provinces.bmp")
        print("wrote map/provinces.bmp,", int(ch.sum()), "px")


if __name__ == "__main__":
    # border at x=4|5, river at x=7: the strip x=5..6 is state 2 on state 1's bank -> becomes state 1
    S = np.array([[1] * 5 + [2] * 7] * 20)
    P = S * 10
    river = np.zeros(S.shape, bool); river[:, 7] = True
    P2, n = snap(P, S, river, 1, 2)
    assert n == 40 and (P2[:, :7] == 10).all() and (P2[:, 8:] == 20).all(), P2[0]
    main(sys.argv[1], "--write" in sys.argv[2:])
