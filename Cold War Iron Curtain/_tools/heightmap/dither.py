"""Soft terrain transitions in map/terrain.bmp, the way vanilla's painters do it: ordered (Bayer) dither between classes.

pdxmap.shader only blends the 4 nearest terrain.bmp texels, so a class edge is a hard 1 px line. Here each land pixel
takes class k with the share of k in its gaussian neighbourhood (SIGMA px), thresholded by a 4x4 Bayer matrix: a 50/50
edge becomes a checkerboard, a class thinning out becomes sparser dots. Sea, lakes (14) and ice sheets (23) are left
as they are and never spread. Not idempotent (each run widens the bands): terrainmap.py runs it once on fresh output.

Run from the mod root:  python _tools/heightmap/dither.py   (rewrites map/terrain.bmp in place)
"""
import io
import numpy as np
from PIL import Image
from scipy import ndimage as nd
from build import WRAP, LAKE_TERRAIN, ICE_TERRAIN

SIGMA = 2.4  # px; the mixed band is ~4 sigma wide (~80 km at the equator): a long dot-density gradient
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 + 1 / 32


def dither(t, free, sigma=SIGMA):
    """t: terrain indices; free: bool mask of pixels that may change (and that count as neighbours)."""
    H, W = t.shape
    th = np.tile(BAYER, (H // 4 + 1, W // 4 + 1))[:H, :W]
    norm = np.maximum(nd.gaussian_filter(free.astype(np.float32), sigma, mode=WRAP), 1e-6)
    out, cum, done = t.copy(), np.zeros(t.shape, np.float32), ~free
    for k in np.unique(t[free]):
        cum += nd.gaussian_filter((free & (t == k)).astype(np.float32), sigma, mode=WRAP) / norm
        pick = ~done & (cum > th)
        out[pick], done = k, done | pick
    out[~done] = t[~done]  # float rounding at cum ~1
    return out


def _selfcheck():
    t = np.zeros((64, 64), np.uint8); t[:, 32:] = 1; t[:, :4] = 15
    free = t != 15
    d = dither(t, free, 1.6)
    assert (d[~free] == 15).all() and (d[:, 8:20] == 0).all() and (d[:, 44:60] == 1).all()
    assert 0.35 < (d[:, 31:33] == 1).mean() < 0.65  # the edge itself is ~half and half (checkered)


def main():
    import sys
    sys.path.insert(0, "_tools/heightmap")
    from gcps import land_mask_and_ids
    _selfcheck()
    ids, kinds = land_mask_and_ids()
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    img = Image.open(io.BytesIO(open("map/terrain.bmp", "rb").read()))  # PIL mmaps a file path; Windows can't truncate it
    t, pal = np.array(img), img.getpalette()
    free = land & ~np.isin(t, (LAKE_TERRAIN, ICE_TERRAIN))
    new = dither(t, free)
    o = Image.fromarray(new, "P"); o.putpalette(pal); o.save("map/terrain.bmp")
    print("changed px:", int((new != t).sum()), "of", int(free.sum()), "free land px")


if __name__ == "__main__":
    main()
