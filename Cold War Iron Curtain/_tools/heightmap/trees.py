"""Rebuild map/trees.bmp and map/terrain/Tree_season.bmp (1650x600 tree-mesh indices, gfx/entities/trees.gfx) from the rebuilt map/terrain.bmp.

Run from the mod root, after terrainmap.py is installed:  python _tools/heightmap/trees.py <etopo.nc> <out_dir>
Each tree pixel covers ~3.4x3.4 terrain pixels; its forest share picks dense vs edge ("blend") meshes, latitude picks
the kind. Visual only: province terrain comes from definition.csv.
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from build import warp
from gcps import land_mask_and_ids
from terrainmap import FOREST, DARK_FOREST, JUNGLE, GRASS, SCRUB

TW, TH = 1650, 600
PALM, PALM_EDGE, NORTH_EDGE, NORTH, BEECH_EDGE, BEECH = 2, 3, 5, 6, 28, 29  # trees.gfx mapobject_N
SAVANNA = (7, 8, 9)


def main(dem_path, out):
    ids, kinds = land_mask_and_ids()
    lo, la, _, _ = warp(dem_path, np.isin(ids, [k for k, v in kinds.items() if v == "sea"]))
    del lo
    t = np.asarray(Image.open("map/terrain.bmp"))
    zoom = (TH / t.shape[0], TW / t.shape[1])
    share = lambda m: np.clip(nd.zoom(nd.uniform_filter(m.astype(np.float32), 3, mode=("nearest", "wrap")), zoom, order=1), 0, 1)
    tropic, temperate = share(t == JUNGLE), share(np.isin(t, (FOREST, DARK_FOREST)))
    open_land = share(np.isin(t, (GRASS, SCRUB)))
    alat = np.abs(nd.zoom(la, zoom, order=1))
    rng = np.random.default_rng(0)

    tr = np.zeros((TH, TW), np.uint8)
    # savanna: scattered trees on open tropical land (Sahel, East Africa, cerrado, northern Australia)
    sav = (open_land > 0.6) & (alat < 20) & (rng.random(tr.shape) < 0.18)
    tr[sav] = rng.choice(SAVANNA, sav.sum())
    tr[temperate > 0.25] = NORTH_EDGE
    tr[temperate > 0.6] = NORTH
    sub = (temperate > 0.25) & (alat < 35)  # warm broadleaf woods (south China, Gulf coast, Brazil highlands)
    tr[sub] = np.where(temperate[sub] > 0.6, BEECH, BEECH_EDGE)
    tr[tropic > 0.25] = BEECH_EDGE
    tr[tropic > 0.6] = BEECH
    edge = (tropic > 0.1) & (tropic <= 0.25) & (tr == 0)  # palms fringe the rainforest
    tr[edge] = np.where(rng.random(edge.sum()) < 0.5, PALM, PALM_EDGE)
    tr[share(np.isin(ids, [k for k, v in kinds.items() if v == "land"])) < 0.5] = 0  # sea/lake pixels keep old terrain marks

    old = Image.open("map/trees.bmp")
    img = Image.fromarray(tr, "P")
    img.putpalette(old.getpalette())
    img.save(f"{out}/trees.bmp")
    v, c = np.unique(tr, return_counts=True)
    old_v, old_c = np.unique(np.asarray(old), return_counts=True)
    print("new:", dict(zip(v.tolist(), c.tolist())), "\nold:", dict(zip(old_v.tolist(), old_c.tolist())))
    season_bmp(out)


def season_bmp(out):
    """map/terrain/Tree_season.bmp: 8 columns = the tree_* dates in seasons.txt (winter, winter2, spring, spring2,
    summer, summer2, autumn, autumn2), 16 rows = random per-tree variants. tree.shader adds max(rgb - 128, 0) to the
    tree colour (northern half only, see TREE_SEASON_* in constants.fxh). Vanilla is ~128 everywhere, i.e. no seasons."""
    conifer = {0, 3, 6, 9, 12, 14}  # rows that stay green all year
    autumn = [(60, 45, 0), (70, 25, 0), (70, 6, 0), (42, 24, 4), (64, 38, 0)]  # yellow, orange, red, brown, gold
    a = np.zeros((16, 8, 3), np.int32)
    for r in range(16):
        if r in conifer:
            a[r] = [(6, 6, 9), (6, 6, 9), (2, 8, 0), (2, 6, 0), (0, 2, 0), (0, 0, 0), (0, 0, 0), (2, 2, 3)]
        else:
            au = np.array(autumn[r % len(autumn)])
            a[r] = [(28, 22, 16), (30, 24, 18), (10, 28, 4), (6, 20, 2), (0, 3, 0), (0, 0, 0), au, au * 3 // 4 + (8, 4, 2)]
    Image.fromarray((128 + a).astype(np.uint8), "RGB").save(f"{out}/Tree_season.bmp")


if __name__ == "__main__":
    main(*sys.argv[1:])
