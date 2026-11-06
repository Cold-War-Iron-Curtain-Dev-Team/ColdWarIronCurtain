"""Rebuild map/terrain.bmp texture indices from real data (no copying from the old painting).

Run from the mod root, after build.py and colormap.py are installed:
    python _tools/heightmap/terrainmap.py <etopo.nc> <ghs_pop_1975.tif.ovr> <out_dir>
Rules on NASA colour (from the colormap), 1975 population, heightmap ruggedness and latitude. Thresholds were set
from sampled biomes (Sahara, taiga, Amazon, steppe, Great Plains, Alps, Tibet...). Visual only: province terrain
comes from definition.csv. Marsh keeps the old painting (no wetland data) and lake/ice marks from build.py stay.
"""
import io, subprocess, sys, numpy as np, tifffile
from PIL import Image
from scipy import ndimage as nd
from build import OLD_COMMIT, WRAP, old_map, LAKE_TERRAIN, ICE_TERRAIN, LAND_MIN, HEIGHT_SCALE, warp
from gcps import land_mask_and_ids

# terrain.bmp indices (00_terrain.txt) -> atlas texture
GRASS, FOREST, DESERT_MTN, SAND, DARK_FOREST, FARMLAND = 0, 1, 2, 3, 4, 5      # tex 1, 4, 3, 9, 5, 0
ROCK, DESERT, DESERT_HILLS, MARSH, SCRUB, ARID_FARM = 6, 7, 8, 9, 10, 12        # tex 11, 12, 14, 6, 13, 8
URBAN, HILLS, MOUNTAIN, JUNGLE, ROCKY_HILLS = 13, 17, 18, 21, 31                # tex 10, 2, 7, 4, 15
# Revolution Realized atlas tiles 16-24 (00_terrain.txt entries added with them)
RED_DESERT, MTN_VALLEY, MTN_VALLEY_DRY, RICE, SUBURB, VILLAGES, PARKLAND = 24, 25, 26, 29, 30, 32, 33  # tex 17, 18, 19, 16, 23, 24, 22
TUNDRA, POLAR_DESERT = 34, 35  # tex 3 (sparse low growth), 21 (snowy rock)
SAVANNA, STEPPE = 36, 37  # tex 17, 5 (atlas_tiles.py); DARK_FOREST now draws tex 14 (taiga), JUNGLE tex 20 (rainforest)


def treeline(t, la):
    """Latitude of the northern treeline per map column: the northernmost row still ~20% forest over ~15 px, smoothed
    along the columns (Hudson Bay ~58N, Scandinavia/Siberia ~67-72N come out of the forest itself)."""
    f = nd.gaussian_filter(np.isin(t, (FOREST, DARK_FOREST)).astype(np.float32), 8, mode=WRAP) > 0.2
    f &= la > 45
    top = np.where(f.any(0), la[np.where(f.any(0), f.argmax(0), 0), np.arange(t.shape[1])], 90.0)
    return nd.median_filter(top, 151, mode="wrap")


def streaky(m, win=41):
    """Pixels of mask m whose surroundings have almost only vertical edges: the old painting stretched past its edge."""
    m = m.astype(np.float32)
    ex, ey = np.zeros_like(m), np.zeros_like(m)
    ex[:, 1:], ey[1:] = np.abs(np.diff(m, axis=1)), np.abs(np.diff(m, axis=0))
    return (m > 0) & (nd.uniform_filter(ex, win, mode=WRAP) > 3 * nd.uniform_filter(ey, win, mode=WRAP) + 0.01)


def tundra(t, la, land, lo):
    """Open northern land beyond the treeline -> tundra; ice-free land from 75N -> polar desert. Hills, mountains and ice
    keep their own look; Siberian marsh stays (real wetland), but the old painting's marsh streaks go, and so does its
    marsh block over Nunavut/Kivalliq (dry tundra). Run on undithered terrain (before dither)."""
    north = la > treeline(t, la)[None, :] - 0.5
    t = t.copy()
    sea_on_land = land & (t == 15)  # land with the ocean index (Greenland lines): nearest land terrain
    idx = nd.distance_transform_edt(sea_on_land | ~land, return_distances=False, return_indices=True)
    t[sea_on_land] = t[tuple(idx)][sea_on_land]
    t[land & streaky(t == MARSH)] = GRASS
    t[land & north & (t == MARSH) & (((lo + 180) % 360 - 180) < -50)] = GRASS
    open_ = land & np.isin(t, (GRASS, SCRUB, STEPPE, PARKLAND, FARMLAND, ARID_FARM))
    t[open_ & north] = TUNDRA
    t[land & (la >= 75) & ~np.isin(t, (ICE_TERRAIN, LAKE_TERRAIN))] = POLAR_DESERT
    return t


def classify(V, veg, red, dens, rough, hm, alat, lon):
    t = np.full(V.shape, GRASS, np.uint8)
    arid = (V >= 85) & (veg < 0.93)  # was 95/.9: Taklamakan, Thar, Mojave, Patagonia came out green
    t[(V >= 60) & (veg < 0.91)] = SCRUB                       # steppe / semi-desert (Kazakhstan, Gobi, outback)
    t[(V >= 110) & (veg < 0.93)] = DESERT
    t[(V >= 140) & (veg < 0.86)] = SAND                       # Sahara, Arabian and Libyan sand seas
    forest = (V < 40) & (veg > 1.05)
    farm = (dens > 20) & (V < 120) & ~((V < 26) & forest)     # populated open land; only the darkest woods survive
    t[forest] = np.where(alat[forest] < 23, JUNGLE, np.where(alat[forest] > 52, DARK_FOREST, FOREST))
    t[farm] = np.where(veg[farm] < 0.9, ARID_FARM, FARMLAND)
    hills, mtn = rough > 3, rough > 6
    t[hills & ~forest] = np.where(arid[hills & ~forest], DESERT_HILLS, HILLS)
    t[(hm > 200) & arid & ~mtn] = ROCKY_HILLS                 # high plateaus (Tibet, Altiplano)
    t[mtn] = np.where(arid[mtn], DESERT_MTN, MOUNTAIN)
    t[mtn & (hm > 215)] = ROCK
    # variety from the bigger atlas; thresholds from sampled biomes (outback veg .59-.72 red 2.2-2.7, Sahara/Kalahari
    # .78-.86 red <2; rice: Ganges/Bengal/Mekong/Yangtze/Java farmland veg .96-1.34)
    t[(V >= 55) & (V < 125) & (veg < 0.75) & (red > 2.0) & ~mtn] = RED_DESERT
    t[(t == MOUNTAIN) & (rough <= 8.5)] = MTN_VALLEY             # gentler ranges: green valleys between ridges
    t[(t == DESERT_MTN) & (rough <= 8.5)] = MTN_VALLEY_DRY
    t[np.isin(t, (GRASS, SCRUB, HILLS)) & (alat < 24) & (veg > 0.7) & (veg < 0.98) & (V >= 45) & (V < 110)] = SAVANNA
    t[(t == GRASS) & (alat >= 24) & (alat < 58) & (veg >= 0.98) & (veg < 1.1) & (V >= 40) & (V < 75)] = PARKLAND  # forest steppe, prairie edge
    lon = lon % 360
    t[(t == FARMLAND) & (alat < 35) & (lon > 68) & (lon < 125) & (veg > 0.95)] = RICE
    t[(t == FARMLAND) & (dens > 80)] = VILLAGES                  # densely settled farmland reads as villages and fields
    t[(t == SCRUB) & (alat >= 35)] = STEPPE  # dry grassland; warmer scrub (outback, Karoo, Mexico) keeps the scrub tile
    return t


def regional(dens, sigma):
    """Mean density of the surrounding inhabited land only: the sea would make island and coastal farmland (Java, Bengal
    delta) look denser than its region."""
    return nd.gaussian_filter(dens, sigma, mode=WRAP) / np.maximum(nd.gaussian_filter((dens > 0).astype(np.float32), sigma, mode=WRAP), 1e-3)


def urban(dens):
    """Towns over 300 people/km2 (GHS 1975) that stand out from the surrounding ~100 km (dense farmland in Bengal/Java
    is 300+ too), or any core over 5000; drop 1-2 px specks unless a real core (>1500)."""
    bg = regional(dens, 16)
    lab, n = nd.label(((dens > 300) & (dens > 2.0 * bg)) | (dens > 5000))
    keep = (np.bincount(lab.ravel()) >= 3) | (np.append(0, nd.maximum(dens, lab, np.arange(1, n + 1))) > 1500)
    keep[0] = False
    return keep[lab]


def sprawl(dens, s=1.0):
    """0..1 metro footprint. Population blurred over ~4*s px only stays at city level around big cities (a one-pixel
    town spreads out below it), so the footprint grows with the city's total size; it must also stand out from the
    regional background (16*s px) so dense farmland (Ganges, Java, the North China Plain) stays rural. Ragged edges from
    blurred noise. s = map pixels per dens pixel (1 for full-res terrain, 0.5 for the half-res colormap)."""
    wide = np.log10(np.maximum(nd.gaussian_filter(dens, 4 * s, mode=WRAP), 1.0))
    bg = np.log10(np.maximum(regional(dens, 16 * s), 1.0))
    f = np.clip((wide - np.log10(60)) / (np.log10(500) - np.log10(60)), 0, 1) * np.clip((wide - bg) / 0.3, 0, 1)
    n = nd.gaussian_filter(np.random.default_rng(1).random(dens.shape, np.float32), 1.5 * s, mode=WRAP)
    n = np.clip(0.5 + (n - n.mean()) / n.std() * 0.2, 0, 1)
    return np.clip(f * 1.5 - 0.7 * n, 0, 1)


def blue_marble(bm_path, lo, la):
    """Blue Marble RGB (float32) at every map pixel. bm_path: one month, or several comma-separated and averaged per
    pixel over the months that aren't snow there (late snow in June, early snow in August/September); white in every
    month (ice sheets, glaciers) stays white. uint8 in, float32 out per channel: a month as a float array is ~2.8 GB."""
    Image.MAX_IMAGE_PIXELS = None
    total, weight, plain = 0, 0, 0
    paths = bm_path.split(",")
    for path in paths:
        bm = np.asarray(Image.open(path).convert("RGB"))
        rows, cols = (90 - la) * bm.shape[0] / 180 - .5, (lo + 180) % 360 * bm.shape[1] / 360 - .5
        m = np.stack([nd.map_coordinates(bm[..., c], [rows, cols], output=np.float32, order=1, mode="wrap")
                      for c in range(3)], -1)
        del bm, rows, cols
        w = ~((m.min(-1) > 110) & (m.max(-1) - m.min(-1) < 45))  # snow: bright and colourless
        total, weight, plain = total + m * w[..., None], weight + w, plain + m / len(paths)
    return np.where(weight[..., None] > 0, total / np.maximum(weight, 1)[..., None], plain)


def main(dem_path, pop_path, out, bm_path=None):
    """bm_path: the Blue Marble month(s) the class thresholds were tuned on (July 2004); without it, the installed
    colormap's colours (only right while the colormap is that same July image)."""
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    lo, la, _, _ = warp(dem_path, sea)

    pop = nd.gaussian_filter(tifffile.imread(pop_path, key=0).astype(np.float32), 1.0)  # GHS 1975, 1 arc-minute
    dens = nd.map_coordinates(pop, [(89.0996 - la) * 60 - .5, (lo + 180.0079) % 360 * 60 - .5], order=1, mode="constant")
    del pop
    t1 = np.full((40, 40), 20, np.float32); t1[20, 5:8], t1[20, 12], t1[20, 30] = 400, 2000, 400
    assert urban(t1)[20, [5, 6, 7, 12, 30]].tolist() == [True, True, True, True, False]  # town, core, lone speck
    assert not urban(np.full((40, 40), 600, np.float32)).any()  # uniform dense farmland stays rural

    if bm_path:
        rgb = blue_marble(bm_path, lo, la)
        rgb = nd.zoom(rgb.reshape(rgb.shape[0] // 2, 2, rgb.shape[1] // 2, 2, 3).mean((1, 3)), (2, 2, 1), order=1)  # as via the colormap
    else:
        rgb = np.asarray(Image.open("map/terrain/colormap_rgb_cityemissivemask_a.dds").convert("RGB")).astype(np.float32)
        rgb = nd.zoom(rgb, (2, 2, 1), order=1)
    V, veg, red = rgb.mean(2), rgb[..., 1] / (rgb[..., 0] + 1), rgb[..., 0] / (rgb[..., 2] + 1)
    del rgb
    hm = np.asarray(Image.open("map/heightmap.bmp")).astype(np.float32)
    hm = np.where(hm >= LAND_MIN, LAND_MIN + (hm - LAND_MIN) / HEIGHT_SCALE, hm)  # thresholds are on the full relief
    hl = np.maximum(hm, 95)  # sea floor clamped to the shore so the coast drop doesn't count as rugged
    rough = np.sqrt(np.maximum(nd.uniform_filter(hl * hl, 7, mode=WRAP) - nd.uniform_filter(hl, 7, mode=WRAP) ** 2, 0)) / 0.84
    # / 0.84: build.HEIGHT_BLUR (1 px) lowers this 7x7 roughness by ~16% at every percentile; thresholds predate it
    # latitude jittered +-4 deg so the jungle/forest/taiga switches don't draw straight lines
    new = classify(V, veg, red, dens, rough, hm, np.abs(la) + np.random.default_rng(0).uniform(-4, 4, la.shape), lo)

    # 3x3 majority filter: per-pixel thresholds leave salt-and-pepper
    score, smooth = np.zeros(new.shape, np.float32), new.copy()
    for v in np.unique(new[land]):
        c = nd.uniform_filter((new == v).astype(np.float32), 3, mode=WRAP)
        better = c > score
        score[better], smooth[better] = c[better], v

    old_t = old_map("terrain")  # pre-rebuild terrain.bmp in the current projection
    old = np.asarray(old_t)
    t = np.array(Image.open("map/terrain.bmp"))  # carries the lake/ice marks from build.py
    paint = land & ~np.isin(t, (LAKE_TERRAIN, ICE_TERRAIN)) & (old != MARSH)
    t[paint] = smooth[paint]
    town, sp = urban(dens), sprawl(dens)
    t[paint & (sp > 0.2) & ~town] = SUBURB  # suburbs ring the metro footprint
    t[paint & (town | (sp > 0.5))] = URBAN  # after the majority filter, which would erase towns
    t[land & (old == MARSH) & ~np.isin(t, (LAKE_TERRAIN, ICE_TERRAIN))] = MARSH
    t = tundra(t, la, land, lo)
    # no dither: lone pixels render as hard texture squares; pdxmap.shader's TERRAIN_EDGE_JITTER softens class edges
    img = Image.fromarray(t, "P")
    img.putpalette(old_t.getpalette())
    img.save(f"{out}/terrain.bmp")
    v, c = np.unique(t[paint], return_counts=True)
    print("share of land:", {int(a): round(b / paint.sum() * 100, 1) for a, b in zip(v, c)})


if __name__ == "__main__":
    main(*sys.argv[1:])
