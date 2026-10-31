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

W, H, Q = 5632, 2048, 4          # Q = registration downscale
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
    # map/<name>.bmp from before the DEM rebuild (hand-made lake pits, unmarked terrain.bmp)
    raw = subprocess.run(["git", "show", f"{OLD_COMMIT}:./map/{name}.bmp"], capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(raw))


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
    """lon/lat of every map pixel: city-point spline, then coast snapped onto provinces.bmp. Returns lo, la, dem, dem sampler."""
    lat, lon, z, ocean = load_dem(dem_path)
    rc = sampler(lat, lon)
    cache = dem_path + ".warp.npz"  # shortcut: not keyed on gcps.json/DROP, delete it after changing control points
    if os.path.exists(cache):
        c = np.load(cache)
        return c["lo"], c["la"], z, rc

    g = [o for o in json.load(open("_tools/heightmap/gcps.json")) if o["name"] not in DROP]
    if os.path.exists("_tools/heightmap/gcps_vp.json"):  # ~2900 victory points matched to GeoNames (vp_gcps.py)
        g += json.load(open("_tools/heightmap/gcps_vp.json"))
    # the map wraps east-west: copy points near each edge across the seam so both edges get the same fit
    pts = [(o["x"], o["y"], o["lon"], o["lat"]) for o in g]
    pts += [(x + W, y, lo + 360, la) for x, y, lo, la in pts if x < W / 4] + [(x - W, y, lo - 360, la) for x, y, lo, la in pts if x > W * 3 / 4]
    pts = np.array(pts)
    tps = RBFInterpolator(pts[:, :2], pts[:, 2:],
                          kernel="thin_plate_spline", smoothing=1e4)  # mod cities scatter ~35 km: fit the trend, not each one

    # coarse grid lon/lat
    h, w = H // Q, W // Q
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float64)
    ll = tps(np.c_[(xx.ravel() + .5) * Q, (yy.ravel() + .5) * Q]).reshape(h, w, 2)
    ll[..., 1] = np.clip(ll[..., 1], -89.9, 89.9)

    # demons: displacement d (coarse px) so that DEM land at (x+d) matches province land at x
    F = sdf(~sea.reshape(h, Q, w, Q).mean((1, 3)).__ge__(.5))
    oc = ocean.astype(np.float32)
    d = np.zeros((2, h, w))
    # borders: once the coast is in, also pull the real 1949 borders onto the mod's country borders where they are
    # within BORDER_REACH coarse px of each other (farther apart = a deliberate mod divergence, left alone)
    cs = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(dem_path))), "cshapes", "CShapes-2.0.geojson")
    real_ll = riv_ll = None
    if os.path.exists(cs):
        real_ll, owner, state = border_maps(cs, sea)
        mod_b = label_edges(owner[Q // 2::Q, Q // 2::Q])
        # river borders: state borders the old hand-drawn rivers ran along (only says WHICH borders are rivers; the
        # river lines themselves are real data, pulled onto those borders)
        rv = os.path.join(os.path.dirname(cs), "..", "rivers", "ne_10m_rivers_lake_centerlines.geojson")
        if os.path.exists(rv):
            riv_ll = river_raster(rv)
            rb = label_edges(state) & nd.binary_dilation(np.asarray(old_map("rivers")) <= 11, iterations=2)
            mod_rb = rb.reshape(h, Q, w, Q).any((1, 3))
            del rb
        del owner, state
    n_it = 250 if real_ll is not None else 150
    for it in range(n_it):
        lo = nd.map_coordinates(ll[..., 0], [yy + d[0], xx + d[1]], order=1, mode="nearest")
        la = nd.map_coordinates(ll[..., 1], [yy + d[0], xx + d[1]], order=1, mode="nearest")
        M = sdf(nd.map_coordinates(oc, rc(lo, la), order=1, mode="wrap") < .5)
        gy, gx = grad(M)
        diff = M - F
        den = gx * gx + gy * gy + diff * diff + 1e-6
        d[0] -= diff * gy / den
        d[1] -= diff * gx / den
        if real_ll is not None and it >= 150:
            rr, cc = np.clip(((90 - la) * BORDER_RES).astype(int), 0, 180 * BORDER_RES - 1), ((lo + 180) % 360 * BORDER_RES).astype(int)
            off_b = pull(d, label_edges(real_ll[rr, cc]) & (F > 0), mod_b, BORDER_REACH)
            if riv_ll is not None:
                off_r = pull(d, riv_ll[rr, cc] & (F > 0), mod_rb, RIVER_REACH)
        sig = 8 if it < 100 else 4  # coarse-to-fine regularisation
        d = np.stack([nd.gaussian_filter(c, sig, mode=WRAP) for c in d])
        if it % 25 == 0 or it == n_it - 1:
            if real_ll is not None and it >= 150:
                print(f"  offset at mod borders: median {off_b:.1f} px" + (f", rivers at river borders {off_r:.1f} px" if riv_ll is not None else ""), flush=True)
            print(f"iter {it}: coast mismatch {np.mean((M > 0) != (F > 0)) * 100:.2f}% of pixels", flush=True)

    # full-res lon/lat through the refined warp
    Y, X = np.mgrid[0:H, 0:W].astype(np.float32)
    cy, cx = (Y + .5) / Q - .5, (X + .5) / Q - .5
    dy = nd.map_coordinates(d[0], [cy, cx], order=1, mode="nearest")
    dx = nd.map_coordinates(d[1], [cy, cx], order=1, mode="nearest")
    del Y, X
    lo = nd.map_coordinates(ll[..., 0], [cy + dy, cx + dx], order=1, mode="nearest")
    la = nd.map_coordinates(ll[..., 1], [cy + dy, cx + dx], order=1, mode="nearest")
    del cy, cx, dy, dx
    np.savez(cache, lo=lo.astype(np.float32), la=la.astype(np.float32))
    return lo, la, z, rc


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
                  np.where(high, hm, np.where(pits, np.minimum(hm, SEA_COAST), np.maximum(hm, LAND_MIN - 1))))
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

    assert hm.shape == (H, W) and hm[sea].max() <= SEA_COAST and hm[~sea & ~lake & ~pits].min() >= LAND_MIN - 1
    print("wrote", out, "| land grey pct", np.percentile(hm[~sea & ~lake & ~pits], [1, 50, 95, 99, 100]))


if __name__ == "__main__":
    main(*sys.argv[1:])
