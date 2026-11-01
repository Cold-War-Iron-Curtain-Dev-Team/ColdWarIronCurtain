"""Redraw one country's land border in provinces.bmp onto the real 23 May 1949 line (CShapes, see border_owner.py).

Run from the mod root:  python _tools/heightmap/border_redraw.py <data_dir> TAG [--write]
Along TAG's border, a land pixel on the wrong side of the real line passes to the 4-neighbouring province of the owner
that holds that side (grown from the right side, so provinces stay in one piece). Only pairs where both owners border
each other move; a province never drops below 40% of its pixels. Run mapfix.py and positions.py afterwards.
"""
import io, sys, numpy as np
from collections import Counter, defaultdict
from PIL import Image
from scipy import ndimage as nd
import proj
from gcps import land_mask_and_ids
from border_owner import real_raster, load_states, RES

KEEP = 0.4


def heal(I, own, provs):
    """A province the redraw cut in pieces keeps its biggest piece; the others go to the same-owner neighbour they touch
    most (any neighbour if none). I is changed in place; returns pixels moved."""
    moved = 0
    for p in provs:
        lab, n = nd.label(I == p)
        if n < 2:
            continue
        keep = np.argmax(np.bincount(lab.ravel())[1:]) + 1
        for k in range(1, n + 1):
            if k == keep:
                continue
            m = lab == k
            ring = nd.binary_dilation(m) & ~m
            c = Counter(I[ring].tolist())
            c.pop(p, None)
            same = Counter({q: v for q, v in c.items() if own[q] == own[p]})
            to = (same or c).most_common(1)[0][0]
            I[m] = to; moved += int(m.sum())
    return moved


def main(S, tag, write=False):
    real_ll, names = real_raster(S)
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    files, st, owner = load_states()
    lo, la = proj.grid()
    own = np.zeros(ids.max() + 1, "U3")
    for p, s in st.items():
        own[p] = owner.get(s) or ""
    ys, xs = np.nonzero(own[ids] == tag)
    y0, y1, x0, x1 = max(ys.min() - 20, 0), min(ys.max() + 21, H), max(xs.min() - 20, 0), xs.max() + 21
    assert x1 <= W, "country crosses the seam"
    I = ids[y0:y1, x0:x1].copy()
    R = real_ll[np.clip(((90 - la[y0:y1, x0:x1]) * RES).astype(int), 0, 180 * RES - 1),
                ((lo[y0:y1, x0:x1] + 180) % 360 * RES).astype(int) % (360 * RES)]
    land = np.isin(I, [p for p, v in kinds.items() if v == "land"])
    # real country -> tag (majority of its pixels here)
    vote = defaultdict(Counter)
    for r, o in zip(R[land].ravel(), own[I[land]].ravel()):
        if r and o:
            vote[int(r)][o] += 1
    tag_of = np.zeros(len(names) + 1, "U3")
    for r, c in vote.items():
        tag_of[r] = c.most_common(1)[0][0]
    want = tag_of[R]  # owner the real line says
    size0 = Counter(I[land].ravel().tolist())
    size = dict(size0)
    moved = Counter()
    for _ in range(40):
        O = own[I]
        bad = land & (want != "") & (O != want) & ((O == tag) | (want == tag))
        step = 0
        for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
            N = np.roll(I, (dy, dx), (0, 1))
            ok = bad & land & np.roll(land, (dy, dx), (0, 1)) & (own[N] == want)
            for y, x in zip(*np.nonzero(ok)):
                p, q = int(I[y, x]), int(N[y, x])
                if own[I[y, x]] == want[y, x] or size[p] - 1 < KEEP * size0[p]:
                    continue
                I[y, x] = q; size[p] -= 1; size[q] = size.get(q, 0) + 1
                moved[(own[p], own[q])] += 1; step += 1
        if not step:
            break
    healed = heal(I, own, {int(q) for q in np.unique(I[I != ids[y0:y1, x0:x1]])} | {int(q) for q in np.unique(ids[y0:y1, x0:x1][I != ids[y0:y1, x0:x1]])})
    print(f"pieces healed: {healed} px")
    left = (land & (want != "") & (own[I] != want) & ((own[I] == tag) | (want == tag))).sum()
    print(f"{tag}: moved {sum(moved.values())} px {dict(moved)}; {left} px still off the line (no neighbour of the right owner, or size floor)")
    if not write:
        return
    raw = open("map/provinces.bmp", "rb").read()
    rgb = np.array(Image.open(io.BytesIO(raw)).convert("RGB"))
    lut = {int(l.split(";")[0]): tuple(map(int, l.split(";")[1:4])) for l in open("map/definition.csv", encoding="latin-1") if l[:1].isdigit()}
    ch = I != ids[y0:y1, x0:x1]
    sub = rgb[y0:y1, x0:x1]
    for y, x in zip(*np.nonzero(ch)):
        sub[y, x] = lut[int(I[y, x])]
    b = io.BytesIO(); Image.fromarray(rgb, "RGB").save(b, "BMP"); assert len(b.getvalue()) == len(raw)
    open("map/provinces.bmp", "wb").write(b.getvalue())


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], "--write" in sys.argv[3:])
