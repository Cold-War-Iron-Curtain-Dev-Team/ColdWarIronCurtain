"""Set strategic-region weather from real climate, per period (month).

Run from the mod root:
    python _tools/heightmap/weather.py <etopo.nc> <worldclim_dir> [wind=<dir>] [ncep=<wspd.mon.ltm.nc>] [ibtracs=<csv>] [--write]
Land (WorldClim 2.1, 1970-2000, 10 arc-minute): temperature, no_phenomenon, rain_light, rain_heavy, snow, blizzard,
min_snow_level; with wind= (WorldClim wind_MM.tif) also sandstorm (windy x dry x bare desert share of the region, from
map/terrain.bmp) and mud (rain plus snowmelt from a degree-day snowpack, so the spring thaw lands in the right month).
Sea (with ncep= and ibtracs=): rain_heavy = storms, from NCEP monthly mean wind (gales above ~8.5 m/s) plus tropical
cyclone days per month (IBTrACS since 1980, winds >= 34 kt); no_phenomenon makes room. Other sea values stay.
Without --write it only prints a before/after table. Province pixels are placed with the heightmap warp.
"""
import csv, glob, re, subprocess, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from build import OLD_COMMIT, warp
from gcps import land_mask_and_ids

DIR = "map/strategicregions"
PERIOD = re.compile(rb"period\s*=\s*\{.*?\n\t\t\}", re.S)


def worldclim(d, var):
    a = np.stack([np.asarray(Image.open(f"{d}/wc2.1_10m_{var}_{m:02d}.tif")) for m in range(1, 13)]).astype(np.float32)
    a[a < -1000] = np.nan  # nodata: -3.4e38 in the float files, -32768 in prec
    return a  # (12, 1080, 2160), row 0 = 90N, col 0 = 180W


def climate_to_weather(tmin, tmax, prec):
    """Monthly means -> HOI4 period values (weights; the engine normalises them)."""
    tmean = (tmin + tmax) / 2
    # share of days with precipitation; cold air snows lightly on many days even when the monthly total is small
    wet = np.clip(prec / 120.0 + 0.4 * np.clip(-tmean / 15.0, 0, 1), 0.05, 0.75)
    snow_share = np.clip((1.5 - tmean) / 5.0, 0, 1)       # all snow below about -3.5 C, all rain above 1.5 C
    heavy = np.clip((prec - 40.0) / 200.0, 0.05, 0.4)
    rain, snow = wet * (1 - snow_share), wet * snow_share
    bliz = snow * np.clip((-8.0 - tmean) / 10.0, 0, 0.4)
    # snow-cover floor (share of the 80 max) so cold months stay white through thaws; capped below the 20 (0.25)
    # "medium ground snow" level, so it is visual plus at most light snow in gameplay
    floor = np.clip((-1.0 - tmean) / 10.0, 0, 1) * 0.2 if prec > 5 else 0.0
    return {
        "temperature": (round(tmin - 4), round(tmax)),  # cold nights beyond the mean; warm end kept so thaws stay rare
        "no_phenomenon": 1 - wet, "rain_light": rain * (1 - heavy), "rain_heavy": rain * heavy,
        "snow": snow - bliz, "blizzard": bliz, "min_snow_level": floor,
    }


def snowmelt(tmean, prec):
    """Monthly snowmelt (mm water) from a degree-day snowpack run twice round the year (second pass = steady state)."""
    pack, melt = 0.0, np.zeros(12)
    for _ in range(2):
        for m in range(12):
            pack += prec[m] * np.clip((1.5 - tmean[m]) / 5.0, 0, 1)  # same rain/snow split as climate_to_weather
            melt[m] = min(pack, max(tmean[m], 0.0) * 3.0 * 30)       # 3 mm per degree-day above 0 C
            pack -= melt[m]
    return melt


def land_extras(tmean, prec, wind, bare, melt):
    """sandstorm and mud for one month. mud is the engine's per-region mud multiplier (mod values 0.3-1.6)."""
    sand = 0.35 * np.clip((wind - 2.5) / 3.0, 0, 1) * np.clip((40.0 - prec) / 35.0, 0, 1) * bare
    # rain counts up to double in cool months (little evaporation): the autumn rasputitsa, not just the spring thaw
    wet = prec / 100.0 * (1 + np.clip((15.0 - tmean) / 15.0, 0, 1))
    mud = 0.5 if tmean < -3 else np.clip(0.4 + wet + melt / 60.0, 0.3, 2.0)  # frozen: the engine freezes mud anyway
    return {"sandstorm": sand, "mud": mud}


def sea_storms(base, wind, tc_days):
    """rain_heavy (lightning storms) at sea: the mod's own value (tropical convection) plus gales from the monthly mean
    wind plus tropical cyclones."""
    return np.clip(0.7 * base + np.clip((wind - 8.5) / 5.0, 0, 0.35) + np.clip(tc_days / 2.0, 0, 0.45), 0.01, 0.6)


def cyclone_days(path):
    """(12, 180, 360) mean days per month with a tropical cyclone (>= 34 kt) nearby, 1 degree grid."""
    grid, years = np.zeros((12, 180, 360)), set()
    with open(path, newline="") as f:
        r = csv.reader(f)
        head = next(r)
        next(r)  # units row
        c = {k: head.index(k) for k in ("SEASON", "ISO_TIME", "LAT", "LON", "TRACK_TYPE", "USA_WIND", "WMO_WIND")}
        for row in r:
            if row[c["TRACK_TYPE"]] != "main":
                continue
            wind = row[c["USA_WIND"]].strip() or row[c["WMO_WIND"]].strip()
            if not wind or float(wind) < 34:
                continue
            years.add(row[c["SEASON"]])
            la, lo = float(row[c["LAT"]]), float(row[c["LON"]])
            grid[int(row[c["ISO_TIME"]][5:7]) - 1, min(179, int(90 - la)), int((lo + 180) % 360)] += 3 / 24  # 3-hourly
    grid /= max(len(years) - 1, 1)
    # a storm's gale field is ~2 degrees across: spread each fix over that, keeping the per-cell day count
    return np.stack([nd.gaussian_filter(g, 2.0, mode=("nearest", "wrap")) * (2 * np.pi * 4) for g in grid])


def fmt(v):
    return f"{v:.2f}".rstrip("0").rstrip(".") if v else "0"


def set_period(block, w):
    if "temperature" in w:
        block = re.sub(rb"temperature\s*=\s*\{[^}]*\}", f"temperature = {{ {w['temperature'][0]} {w['temperature'][1]} }}".encode(), block)
    for k in ("no_phenomenon", "rain_light", "rain_heavy", "snow", "blizzard", "min_snow_level", "sandstorm", "mud"):
        if k in w:
            block = re.sub(rb"(\b" + k.encode() + rb"\s*=\s*)[-\d.]+", lambda m: m.group(1) + fmt(w[k]).encode(), block)
    return block


def main(dem_path, wc_dir, *flags):
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    lo, la, _, _ = warp(dem_path, sea)
    s = (slice(None, None, 3), slice(None, None, 3))  # every 3rd pixel is plenty for region means
    pid, lo, la, land = ids[s], lo[s], la[s], ~sea[s]
    rows, cols = (90 - la) * 6 - .5, (lo + 180) % 360 * 6 - .5

    regions = {}
    for f in glob.glob(f"{DIR}/*.txt"):
        raw = open(f, "rb").read()
        rid = int(re.search(rb"\bid\s*=\s*(\d+)", raw).group(1))
        provs = [int(x) for x in re.search(rb"provinces\s*=\s*\{([^}]*)\}", raw).group(1).split()]
        regions[rid] = (f, raw, provs)
    lut = np.zeros(ids.max() + 1, np.int64)
    for rid, (_, _, provs) in regions.items():
        lut[[p for p in provs if p < len(lut)]] = rid
    reg = np.where(land, lut[pid], 0)

    clim = {}
    for var in ("tmin", "tmax", "prec"):
        a = worldclim(wc_dir, var)
        vals = np.stack([nd.map_coordinates(np.nan_to_num(m, nan=0.0), [rows, cols], order=0, mode="wrap") for m in a])
        ok = np.isfinite(np.stack([nd.map_coordinates(np.where(np.isnan(m), np.nan, 0.0), [rows, cols], order=0, mode="wrap") for m in a]))
        clim[var] = (vals, ok)
    counts = np.bincount(reg.ravel(), weights=(clim["tmin"][1][0] & land).ravel(), minlength=max(regions) + 1)
    # sea regions: most of their province pixels are sea (a few coastal/lake provinces must not make them "land")
    reg_all = lut[pid]
    water = np.isin(pid, [k for k, v in kinds.items() if v in ("sea", "lake")])  # the Caspian is lake provinces
    sea_share = (np.bincount(reg_all.ravel(), weights=water.ravel(), minlength=len(counts))
                 / np.maximum(np.bincount(reg_all.ravel(), minlength=len(counts)), 1))

    def region_mean(var):
        vals, ok = clim[var]
        w = (ok & land).astype(np.float64)
        return np.stack([np.bincount(reg.ravel(), weights=(vals[m] * w[m]).ravel(), minlength=len(counts)) /
                         np.maximum(np.bincount(reg.ravel(), weights=w[m].ravel(), minlength=len(counts)), 1) for m in range(12)])
    tmin, tmax, prec = (region_mean(v) for v in ("tmin", "tmax", "prec"))
    opt = dict(f.split("=", 1) for f in flags if "=" in f)

    wind = bare = None
    if "wind" in opt:
        vals = np.stack([nd.map_coordinates(np.nan_to_num(m, nan=0.0), [rows, cols], order=0, mode="wrap")
                         for m in worldclim(opt["wind"], "wind")])
        clim["wind"] = (vals, clim["tmin"][1])
        wind = region_mean("wind")
        # bare desert share per region (terrain.bmp: desert mountains, sand, desert, desert hills, high plateau; scrub half)
        t = np.asarray(Image.open("map/terrain.bmp"))[s]
        b = np.isin(t, (2, 3, 7, 8, 31)) + 0.5 * (t == 10)
        bare = np.bincount(reg.ravel(), weights=(b * land).ravel(), minlength=len(counts)) / np.maximum(
            np.bincount(reg.ravel(), weights=land.ravel().astype(float), minlength=len(counts)), 1)

    sea_wind = tc = None
    if "ncep" in opt and "ibtracs" in opt:
        import h5py  # NCEP long-term means are netCDF4 (HDF5)
        with h5py.File(opt["ncep"], "r") as f:
            ws = f["wspd"][:].astype(np.float32)  # (12, 73, 144), 90N..90S, 0..357.5E, 2.5 deg
        tcd = cyclone_days(opt["ibtracs"])
        reg_sea = np.where(water, reg_all, 0)
        sea_mean = lambda grids, rr, cc: np.stack([np.bincount(reg_sea.ravel(), weights=nd.map_coordinates(g, [rr, cc], order=1, mode="wrap").ravel(), minlength=len(counts))
                                                   / np.maximum(np.bincount(reg_sea.ravel(), minlength=len(counts)), 1) for g in grids])
        sea_wind = sea_mean(ws, (90 - la) / 2.5, (lo % 360) / 2.5)
        tc = sea_mean(tcd, 90 - la - .5, (lo + 180) % 360 - .5)

    write = "--write" in flags
    changed = 0
    show = {"Southern England", "Western Poland", "Northern Norway", "Moscow", "Sahara", "Bengal", "Siberia"}
    for rid, (f, raw, _) in sorted(regions.items()):
        at_sea = sea_share[rid] > 0.5
        if at_sea and sea_wind is None or not at_sea and counts[rid] < 5:
            continue  # sea region without sea data, or no climate coverage
        periods = list(PERIOD.finditer(raw))
        if len(periods) != 12:
            print("skip (not 12 periods):", f)
            continue
        if not at_sea and wind is not None:
            melt = snowmelt((tmin[:, rid] + tmax[:, rid]) / 2, prec[:, rid])
        if at_sea:  # the mod's own storm values before this tool, so reruns don't stack
            old = subprocess.run(["git", "show", f"{OLD_COMMIT}:./{f}".replace("\\", "/")], capture_output=True).stdout
            base = [float(x) for x in re.findall(rb"\brain_heavy\s*=\s*([-\d.]+)", old)]
            base = base if len(base) == 12 else None
        out, pos = [], 0
        for m, per in enumerate(periods):
            month = int(re.search(rb"between\s*=\s*\{\s*[\d]+\.(\d+)", per.group(0)).group(1))
            if at_sea:
                light = float(re.search(rb"\brain_light\s*=\s*([-\d.]+)", per.group(0)).group(1))
                heavy = sea_storms(base[m] if base else 0.0, sea_wind[month, rid], tc[month, rid])
                w = {"rain_heavy": heavy, "no_phenomenon": max(0.1, 1 - light - heavy)}
            else:
                w = climate_to_weather(tmin[month, rid], tmax[month, rid], prec[month, rid])
                if wind is not None:
                    w.update(land_extras((tmin[month, rid] + tmax[month, rid]) / 2, prec[month, rid], wind[month, rid], bare[rid], melt[month]))
            out += [raw[pos:per.start()], set_period(per.group(0), w)]
            pos = per.end()
            name = f.replace("\\", "/").split("/")[-1][:-4].split("-", 1)[1]
            if not at_sea and month in (0, 6) and any(k.lower() in name.lower() for k in show):
                old = re.search(rb"temperature\s*=\s*\{([^}]*)\}", per.group(0)).group(1).decode().split()
                osn = re.search(rb"\bsnow\s*=\s*([-\d.]+)", per.group(0)).group(1).decode()
                print(f"{name[:22]:22s} {'Jan' if month == 0 else 'Jul'}  temp {old[0]:>4}..{old[1]:<4} -> {w['temperature'][0]:>4}..{w['temperature'][1]:<4}"
                      f"  snow {osn:>5} -> {fmt(w['snow']):<5}  rain {fmt(w['rain_light'] + w['rain_heavy']):<5} none {fmt(w['no_phenomenon'])}")
        out.append(raw[pos:])
        new = b"".join(out)
        if new != raw:
            changed += 1
            if write:
                open(f, "wb").write(new)
    print(f"{changed} regions {'written' if write else 'would change (dry run, pass --write)'}")


if __name__ == "__main__":
    main(*sys.argv[1:])
