"""Rebuild the land colours of map/terrain/colormap_rgb_cityemissivemask_a.dds from NASA Blue Marble.

Run from the mod root:  python _tools/heightmap/colormap.py <etopo.nc> <bluemarble.jpg> <out_dir> [ghs_pop_1975.tif.ovr]
Uses the same warp as build.py. Sea and lake-province colours are kept; the alpha channel (city lights) is rebuilt from 1975 population if given; Blue Marble land is
colour-matched to the old colormap's land so the overlay strength in the shaders still fits.
"""
import io, subprocess, sys, numpy as np, tifffile
from PIL import Image
from scipy import ndimage as nd
from build import WRAP, OLD_COMMIT, warp
from gcps import land_mask_and_ids
from terrainmap import sprawl

DDS = "map/terrain/colormap_rgb_cityemissivemask_a.dds"
MATCH = 0.0  # how far land colours are pulled toward the old colormap's mean/contrast (0 = raw NASA)


def dxt5_with_mips(img, header):
    """DXT5 + full mip chain; header is reused from the original file (same size, format and mip count)."""
    out, w, h = [header], img.width, img.height
    while True:
        pw, ph = -(-w // 4) * 4, -(-h // 4) * 4  # blocks cover ceil(w/4) x ceil(h/4)
        lvl = img.resize((w, h), Image.LANCZOS)
        if (pw, ph) != (w, h):
            pad = Image.new("RGBA", (pw, ph))
            pad.paste(lvl)
            lvl = pad
        buf = io.BytesIO()
        lvl.save(buf, "DDS", pixel_format="DXT5")
        out.append(buf.getvalue()[128:])
        if w == 1 and h == 1:
            break
        w, h = max(1, w // 2), max(1, h // 2)
    return b"".join(out)


def main(dem_path, bm_path, out, pop_path=None):
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    lake = np.isin(ids, [k for k, v in kinds.items() if v == "lake"])  # 2004 imagery: Aral/Chad already shrunk, keep old
    lo, la, _, _ = warp(dem_path, sea)

    Image.MAX_IMAGE_PIXELS = None
    bm = np.asarray(Image.open(bm_path).convert("RGB")).astype(np.float32)
    rows, cols = (90 - la) * bm.shape[0] / 180 - .5, (lo + 180) % 360 * bm.shape[1] / 360 - .5
    rgb = np.stack([nd.map_coordinates(bm[..., c], [rows, cols], order=1, mode="wrap") for c in range(3)], -1)
    del bm, rows, cols
    if pop_path:  # GHS-POP 1975 .tif.ovr, level 0 = 1 arc-minute (people per cell), top-left at (-180.0079, 89.0996)
        pop = nd.gaussian_filter(tifffile.imread(pop_path, key=0).astype(np.float32), 2.0)  # overview is point-sampled
        dens = nd.map_coordinates(pop, [(89.0996 - la) * 60 - .5, (lo + 180.0079) % 360 * 60 - .5], order=1, mode="constant")
        del pop
        dens = dens.reshape(dens.shape[0] // 2, 2, dens.shape[1] // 2, 2).mean((1, 3))
    del lo, la
    rgb = rgb.reshape(rgb.shape[0] // 2, 2, rgb.shape[1] // 2, 2, 3).mean((1, 3))  # half res, box-filtered

    raw = subprocess.run(["git", "show", f"{OLD_COMMIT}:./{DDS}"], capture_output=True, check=True).stdout  # pre-rebuild file
    old = np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA")).astype(np.float32)
    land = ~(sea | lake).reshape(old.shape[0], 2, old.shape[1], 2).any((1, 3))
    m0, s0 = rgb[land].mean(0), rgb[land].std(0)
    m1, s1 = old[land][:, :3].mean(0), old[land][:, :3].std(0)
    matched = (rgb - m0) / s0 * s1 + m1
    rgb = rgb + MATCH * (matched - rgb)

    w = nd.gaussian_filter(land.astype(np.float32), 1.0, mode=WRAP)[..., None]  # feathered coast
    new = old.copy()
    new[..., :3] = w * rgb + (1 - w) * old[..., :3]
    if pop_path:
        # city lights: log-scaled from ~120 people/km2 (small town) to ~1200 (city), so most cities read at night
        ld = np.log10(np.maximum(dens, 1.0))
        lo_t, hi_t = np.log10(120), np.log10(1200)
        core = np.clip((ld - lo_t) / (hi_t - lo_t), 0, 1)
        # only where denser than the surrounding ~80 km, so cities glow but dense farmland (Ganges, China) doesn't
        bg = np.log10(np.maximum(nd.gaussian_filter(dens, 8, mode=WRAP), 1.0))
        core *= np.clip((ld - bg - 0.1) / 0.4, 0, 1)
        glow = np.clip(nd.gaussian_filter(core, 2.0, mode=WRAP) * 3.0, 0, 1)  # halo so cities read at map zoom
        new[..., 3] = 255 * np.maximum(np.maximum(core, glow), sprawl(dens, 1.0)) * land  # suburbs: twice the urban-terrain reach
    img = Image.fromarray(np.clip(np.rint(new), 0, 255).astype(np.uint8), "RGBA")
    img.save(f"{out}/colormap_preview.png")
    open(f"{out}/colormap_rgb_cityemissivemask_a.dds", "wb").write(dxt5_with_mips(img, raw[:128]))
    print("land mean old", m1.round(1), "nasa", m0.round(1))


if __name__ == "__main__":
    main(*sys.argv[1:])
