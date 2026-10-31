"""Build map/heightmap.bmp + map/world_normal.bmp from a real DEM (ETOPO1, netCDF3 from NOAA ERDDAP).

Run from the mod root:  python _tools/heightmap/build.py <etopo.nc> <out_dir> [lakes_geojson_dir] [glaciers_geojson_dir]
Warp: thin-plate spline through victory-point cities (gcps.json), then a demons pass that
snaps the DEM coastline onto provinces.bmp so land/sea always agree with the provinces.
"""
import glob, io, json, os, re, subprocess, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.io import netcdf_file
from scipy.interpolate import RBFInterpolator
from gcps import land_mask_and_ids
import proj

W, H, Q = proj.W, proj.H, 4      # Q = registration downscale
SEA_COAST, LAND_MIN = 90, 96     # vanilla: flat sea at 88, land starts ~96; >91 triggers shore foam
LAKE_RES = 60                    # lake raster cells per degree
OLD_COMMIT = "99834bcd35"
HIGH_LAKE = 105                  # bank grey (~230 m) above which a lake is drawn by the terrain shader, not as a pit
ICE_TERRAIN = 23                 # terrain.bmp ice_sheet (00_terrain.txt, texture = 254), drawn as ice by pdxmap.shader
LAKE_TERRAIN = 14                # terrain.bmp index; 00_terrain.txt gives it texture = 255, which the shader keys on
BORDER_RES, BORDER_REACH = 20, 3  # CShapes raster cells/degree; coarse px (~75 km) beyond which borders don't pull
RIVER_REACH = 2                   # coarse px: a river farther than this from a river border is another river
DROP = {"Brest", "Noumea", "Mahé"}  # name matches the wrong province (Belarus Brest, Indian Mahé, Noumea VP sits in Africa)


def load_dem(path):
    f = netcdf_file(path, mmap=False)
    lat, lon, z = (f.variables[k].data.copy() for k in ("latitude", "longitude", "altitude"))
    z = z.astype(np.float32)
    # ocean = water connected to the open sea; Caspian/Dead Sea/inland depressions count as land
    lab, _ = nd.label(z <= 0)
    ocean = np.isin(lab, np.unique(lab[np.r_[0, len(lat) // 2], :]))  # south pole row + equator row
    ocean &= lab > 0
    return lat, lon, z, ocean


def sampler(lat, lon):
    dl = lat[1] - lat[0]
    def rc(lo, la):
        return (la - lat[0]) / dl, ((lo - lon[0]) % 360.0) / dl
    return rc


def polygon_raster(d):
    """Natural Earth polygons (*.geojson in d) -> bool grid, row = (90-lat)*LAKE_RES, col = (lon+180)*LAKE_RES."""
    img = Image.new("1", (360 * LAKE_RES, 180 * LAKE_RES), 0)
    draw = ImageDraw.Draw(img)
    pt = lambda ring: [((x + 180) * LAKE_RES, (90 - y) * LAKE_RES) for x, y in ring]
    for f in glob.glob(f"{d}/*.geojson"):
        for feat in json.load(open(f, encoding="utf-8"))["features"]:
            if feat["properties"].get("featurecla") == "Alkaline Lake" or not feat["geometry"]:
                continue  # seasonal salt pans (Eyre, Chad basin) would show as permanent water
            g = feat["geometry"]
            for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
                draw.polygon(pt(poly[0]), fill=1)
                for hole in poly[1:]:
                    draw.polygon(pt(hole), fill=0)
    return np.asarray(img, dtype=np.uint8)  # uint8: a float grid at this size is ~1 GB


def old_map(name):
    # map/<name>.bmp from before the DEM rebuild (hand-made lake pits, unmarked terrain.bmp), resampled into the
    # current projection by oldlayers.py
    return Image.open(os.path.join(os.environ["CWIC_OLD_LAYERS"], f"{name}.bmp"))


WRAP = ("nearest", "wrap")  # filter modes per axis: rows clamp, columns wrap (the map is a cylinder)


def grad(a):
    """np.gradient with the x derivative wrapping across the map seam."""
    return np.gradient(a, axis=0), (np.roll(a, -1, 1) - np.roll(a, 1, 1)) / 2


def masked_blur(a, m, s):
    return nd.gaussian_filter(np.where(m, a, 0), s, mode=WRAP) / np.maximum(nd.gaussian_filter(m.astype(np.float32), s, mode=WRAP), 1e-3)


def sdf(mask):
    return np.clip(nd.distance_transform_edt(mask) - nd.distance_transform_edt(~mask), -24, 24)


def border_maps(cshapes, sea):
    """Real 1949 country labels (CShapes 2.0 on 23 May 1949, lon/lat raster at BORDER_RES cells/degree), the mod's
    1949 owner label per map pixel (state history before any dated block) and the state id per map pixel."""
    feats = json.load(open(cshapes, encoding="utf-8"))["features"]
    day = lambda p, k: (p[f"g{k}year"], p[f"g{k}month"], p[f"g{k}day"])
    img = Image.new("I", (360 * BORDER_RES, 180 * BORDER_RES), 0)
    dr = ImageDraw.Draw(img)
    for i, f in enumerate([f for f in feats if day(f["properties"], "ws") <= (1949, 5, 23) <= day(f["properties"], "we")], 1):
        g = f["geometry"]
        for poly in g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]:
            if len(poly[0]) > 2:
                dr.polygon([((x + 180) * BORDER_RES, (90 - y) * BORDER_RES) for x, y in poly[0]], fill=i)
    ids, kinds = land_mask_and_ids()
    st, sid, tags = np.zeros(ids.max() + 1, np.int32), np.zeros(ids.max() + 1, np.int32), {}
    for f in glob.glob("history/states/*.txt"):
        t = open(f, encoding="utf-8", errors="ignore").read()
        m, pr = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
        o = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=\s*\{", t)[0])
        if m and pr and o:
            ps = [int(q) for q in pr.group(1).split() if q.isdigit() and int(q) < len(st)]
            st[ps], sid[ps] = tags.setdefault(o.group(1), len(tags) + 1), int(m.group(1))
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    return np.asarray(img, np.int32), np.where(land, st[ids], 0), np.where(land, sid[ids], 0)


def river_raster(path, max_rank=10):
    """Natural Earth river centerlines -> bool lon/lat raster at BORDER_RES cells/degree."""
    img = Image.new("1", (360 * BORDER_RES, 180 * BORDER_RES), 0)
    dr = ImageDraw.Draw(img)
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        p, g = f["properties"], f["geometry"]
        if p["featurecla"] not in ("River", "Lake Centerline") or p["scalerank"] is None or p["scalerank"] > max_rank:
            continue
        for part in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            if len(part) > 1:
                dr.line([((x + 180) * BORDER_RES, (90 - y) * BORDER_RES) for x, y in part], fill=1)
    return np.asarray(img, bool)


def pull(d, target, src, reach):
    """Demons step pulling the warped `target` lines (coarse bool) onto the mod's `src` lines where they are within
    `reach` coarse px; the sparse pull is spread over its neighbourhood and fades out away from it."""
    B = nd.distance_transform_edt(~target)
    by, bx = grad(B)
    f = src & (B < reach)
    den = bx * bx + by * by + B * B + 1e-6
    wt = nd.gaussian_filter(f.astype(np.float32), 3, mode=WRAP)
    for c, g in ((0, by), (1, bx)):
        d[c] -= masked_blur(B * g / den, f, 3) * np.clip(wt / 0.05, 0, 1)
    return np.median(B[f]) * Q if f.any() else 0.0


def label_edges(L):
    b = np.zeros(L.shape, bool)
    for ax in (0, 1):
        b |= (np.roll(L, 1, ax) != L) & (L > 0) & (np.roll(L, 1, ax) > 0)
    return b


def warp(dem_path, sea):
    """lon/lat of every map pixel (exact: the map is Patterson since the reprojection, see proj.py). Returns lo, la, dem, dem sampler.
    The old map's spline + coast-snapping warp lives in git history (before reproject.py); its result is the cached
    old-layout npz that reproject.py and oldlayers.py read."""
    lat, lon, z, ocean = load_dem(dem_path)
    lo, la = proj.grid()
    return lo, la, z, sampler(lat, lon)


def main(dem_path, out, lakes_dir=None, glaciers_dir=None):
    ids, kinds = land_mask_and_ids()
    sea_ids = [k for k, v in kinds.items() if v == "sea"]
    lake_ids = [k for k, v in kinds.items() if v == "lake"]
    sea, lake = np.isin(ids, sea_ids), np.isin(ids, lake_ids)
    lo, la, z, rc = warp(dem_path, sea)
    elev = nd.map_coordinates(z, rc(lo, la), order=1, mode="wrap")
    def sample(d):  # polygon raster -> bool at every map pixel
        if not d:
            return np.zeros_like(sea)
        return nd.map_coordinates(polygon_raster(d), [(90 - la) * LAKE_RES, (lo + 180) % 360 * LAKE_RES], order=0, mode="wrap") > 0
    wet, ice = sample(lakes_dir), sample(glaciers_dir)
    del lo, la

    # elevation -> grey. mild power curve; matches vanilla spread (median ~106, peaks ~230)
    land_g = LAND_MIN + 140 * (np.clip(elev, 0, 6000) / 5000) ** 0.85
    # sea: real depth over grey 90..32. gfx/FX/pdxmap.shader PixelShaderUnderwater fogs the floor from grey 30 (opaque) to 98
    sea_g = SEA_COAST - 58 * (np.clip(-elev, 0, 6000) / 6000) ** 0.6
    hm = nd.gaussian_filter(np.where(sea, sea_g, land_g), 0.8, mode=WRAP)

    # local contrast, land and sea blurred separately so the coast step doesn't leak in.
    # mountains get up to 1.6x ridge/valley detail, plains keep >=60% (river valleys read well); sea floor 1.5x
    base = np.where(sea, masked_blur(hm, sea, 5), masked_blur(hm, ~sea, 5))
    det = hm - base
    rough = np.sqrt(nd.gaussian_filter(det * det, 12, mode=WRAP))
    hm = base + det * np.where(sea, 1.5, np.clip(rough / 2.5, 0.6, 1.6))

    # lakes: one global water plane (grey ~95), so every lake is a pit. keep the old map's decorative pits,
    # add real lakes that don't duplicate one of them
    old = np.asarray(old_map("heightmap")).astype(np.float32)
    decor = (old < LAND_MIN - 1) & ~sea & ~lake
    decor &= ~nd.binary_dilation(sea, iterations=2)  # low coastal strips are not lakes
    lab, n = nd.label(wet & ~sea & ~lake)
    dup = np.unique(lab[nd.binary_dilation(decor, iterations=6) & (lab > 0)])
    pits = decor | ((lab > 0) & ~np.isin(lab, dup))
    # the water plane sits at one height, so a lake with high banks becomes a crater. those become a flat surface at
    # bank height marked terrain.bmp index 14, which gfx/FX/pdxmap.shader draws as water. low lakes stay real-water pits
    water = pits | lake
    wl, nw = nd.label(water)
    ring = nd.binary_dilation(water, iterations=2) & ~water & ~sea
    ringlab = np.where(ring, nd.grey_dilation(wl, size=5), 0)
    bank = np.r_[0, nd.labeled_comprehension(hm, ringlab, np.arange(1, nw + 1), lambda v: np.percentile(v, 10), np.float64, 0)]
    high = (bank > HIGH_LAKE)[wl] & water
    hm = np.where(pits & ~high, np.where(decor, old, 88), hm)
    hm = np.where(high, np.maximum(bank[wl] - 1, HIGH_LAKE - 1), hm)
    hm = np.where(sea, np.clip(hm, 20, SEA_COAST),
                  np.where(high, hm, np.where(pits, np.minimum(hm, SEA_COAST), np.maximum(hm, LAND_MIN))))  # 95 = water plane: drowned
    hm = np.where(lake & ~high, old, hm)  # low lake provinces keep hand-made water depth
    ter = old_map("terrain")
    t = np.array(ter)
    t[high] = LAKE_TERRAIN
    t[ice & ~sea & ~water] = ICE_TERRAIN
    t_img = Image.fromarray(t, "P")
    t_img.putpalette(ter.getpalette())
    t_img.save(f"{out}/terrain.bmp")
    hmf = hm.astype(np.float32)
    hm = np.clip(np.rint(hm), 0, 255).astype(np.uint8)
    Image.fromarray(hm, "L").save(f"{out}/heightmap.bmp")

    # world_normal: half res from the unrounded heights (rounded ones band into contour lines). R/G = -/+ k*slope, B = 255
    h2 = hmf.reshape(H // 2, 2, W // 2, 2).mean((1, 3))
    gy, gx = grad(nd.gaussian_filter(h2, .7, mode=WRAP))
    k = np.where(sea[::2, ::2], 18, 12)  # sea floor lit harder so ridges/trenches read through the water
    nm = np.stack([128 - k * gx, 128 + k * gy, np.full_like(gx, 255)], -1)
    Image.fromarray(np.clip(np.rint(nm), 0, 255).astype(np.uint8), "RGB").save(f"{out}/world_normal.bmp")
    print("lake pits:", decor.sum(), "old decorative px +", ((lab > 0) & ~np.isin(lab, dup)).sum(), "new real-lake px;",
          high.sum(), "px drawn as high lakes;", (ice & ~sea & ~water).sum(), "px ice sheet")

    assert hm.shape == (H, W) and hm[sea].max() <= SEA_COAST and hm[~sea & ~lake & ~pits].min() >= LAND_MIN
    print("wrote", out, "| land grey pct", np.percentile(hm[~sea & ~lake & ~pits], [1, 50, 95, 99, 100]))


if __name__ == "__main__":
    main(*sys.argv[1:])
