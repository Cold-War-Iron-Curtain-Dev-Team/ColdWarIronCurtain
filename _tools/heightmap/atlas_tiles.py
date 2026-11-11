"""Fill the unused terrain atlas slots (map/terrain/atlas{0,1,2}.dds + atlas_normal{0,1,2}.dds, 5x5 grid of 512 px tiles at
atlas0) with tiles cut from real imagery. The atlas size stays 2560 px: the engine refuses bigger ones (MAX_TEXTURE_SIZE).

Imagery: NASA GIBS Landsat WELD annual true-colour composites (~30 m, public domain), cached in <data_dir>/landsat. Each
crop has its large light gradients flattened, is made seamless by cross-fading a margin, levelled like the old tiles
(atlas_levels.target), given their detail contrast and warmer palette; the normal map comes from the tile's brightness,
alpha = gloss (diffuse) and specular (normal). Reads the atlas from SOURCE (git), so reruns don't stack.
Run from the mod root:  python ../_tools/heightmap/atlas_tiles.py <data_dir>
"""
import io, os, subprocess, sys, urllib.request, numpy as np
from PIL import Image
from scipy import ndimage as nd
from colormap import dxt5_with_mips
from atlas_levels import target, LUM

SOURCE = "b1180848d7"  # last commit that changed the atlas
GRID, T = 5, 512
LAYER = "Landsat_WELD_CorrectedReflectance_TrueColor_Global_Annual"
# slot: (name, lon, lat, year, crop x, crop y, crop size in the 1024 px 2x2-tile block, relief, specular)
TILES = {
    1: ("grassland", -58.0, -36.5, 1985, 0, 0, 1024, 1.0, 100),  # Salado pampas (was a neon painted grass, 13% of land)
    4: ("forest", -91.5, 37.0, 1985, 420, 530, 494, 1.0, 110),   # Ozarks broadleaf, south of the highway (was green with painted yellow flecks)
    5: ("steppe", -104.0, 46.5, 1985, 0, 300, 560, 1.2, 60),  # Montana prairie (old slot: generic dark forest, unused)
    14: ("taiga", 60.0, 62.0, 2000, 0, 0, 1024, 1.0, 110),      # west of the Urals
    17: ("savanna", 30.0, 11.0, 1985, 0, 0, 1024, 1.0, 70),     # Kordofan, Sudan
    20: ("rainforest", 23.0, 0.8, 2000, 0, 0, 1024, 1.0, 110),  # Congo basin (replaces an unused joke photo)
}
OLD_MEAN = np.array([111.0, 128.0, 70.0])  # mean colour of the painted land tiles
CONTRAST, WARM, SAT = 30.0, 0.4, 0.85
# vegetation seen from above is darker and duller than atlas_levels.target lifts it (players: 'too green, too bright'):
# slot -> (mean luminance, saturation) instead of (target(lum), SAT)
LOOK = {1: (108, 0.75), 4: (92, 0.75), 14: (95, 0.75), 20: (92, 0.75)}
# the painted green tiles that stay: luminance and saturation scaled in place
CALM = {0: (0.92, 0.85), 2: (0.92, 0.85), 3: (0.95, 0.85), 6: (0.95, 0.85), 16: (0.92, 0.8), 22: (0.92, 0.8)}


def landsat_block(cache, lon, lat, year, z=11):
    """2x2 GIBS tiles (1024 px, ~30 km) whose top-left tile holds lon/lat."""
    n = 2560 * 2 ** (z - 11)
    col, row = int((lon + 180) / 360 * n), int((90 - lat) / 180 * (n / 2))
    out = Image.new("RGB", (1024, 1024))
    for dy in (0, 1):
        for dx in (0, 1):
            p = f"{cache}/{year}_{z}_{row + dy}_{col + dx}.jpg"
            if not os.path.exists(p):
                url = f"https://gibs.earthdata.nasa.gov/wmts/epsg4326/best/{LAYER}/default/{year}-12-01/31.25m/{z}/{row + dy}/{col + dx}.jpg"
                open(p, "wb").write(urllib.request.urlopen(url, timeout=60).read())
            out.paste(Image.open(p).convert("RGB"), (dx * 512, dy * 512))
    return out


def seamless(a, margin):
    """a: (n+margin, n+margin, c) float -> (n, n, c) that tiles: the extra margin is cross-faded over the start."""
    n = a.shape[0] - margin
    w = np.clip(np.arange(margin) / (margin - 1), 0, 1)
    w = (w * w * (3 - 2 * w))[:, None]  # smoothstep
    a = a.copy()
    a[:margin] = a[:margin] * w[..., None] + a[n:] * (1 - w[..., None])
    a = a[:n]
    a[:, :margin] = a[:, :margin] * w[None, :, :] + a[:, n:] * (1 - w[None, :, :])
    return a[:, :n]


def make_tile(img, crop, relief, spec, look=None):
    """look: (mean luminance, saturation) overriding atlas_levels.target and SAT."""
    x, y, s = crop
    margin = T // 4
    a = np.asarray(img.crop((x, y, x + s, y + s)).resize((T + margin,) * 2, Image.LANCZOS), np.float32)
    low = nd.gaussian_filter(a, (T / 8, T / 8, 0), mode="reflect")  # scene seams, haze: the repeat would show them
    a = seamless(a - 0.8 * (low - a.reshape(-1, 3).mean(0)), margin)
    lum = a @ LUM
    want, sat = look or (target(lum.mean()), SAT)
    a *= want / max(lum.mean(), 1)
    # the painted tiles' detail contrast (lum std ~40-60 vs ~10-25 here), warmer palette and saturation
    lum = a @ LUM
    dev = lum - nd.gaussian_filter(lum, 24, mode="wrap")
    a += (np.clip(CONTRAST / max(dev.std(), 1e-3), 1, 2.2) - 1) * dev[..., None]
    m = a.reshape(-1, 3).mean(0)
    a += WARM * (OLD_MEAN * (m @ LUM) / (OLD_MEAN @ LUM) - m)
    lum = a @ LUM
    a = np.clip(lum[..., None] + sat * (a - lum[..., None]), 0, 255)
    lum = a @ LUM
    h = nd.gaussian_filter(lum, 1.2, mode="wrap") / 255.0
    gy, gx = np.gradient(h)
    k = 6.0 * relief * 255 / 32  # flat painted tiles: normal x/y std ~7-12 of 255
    nx, ny = -gx * k, -gy * k
    norm = np.sqrt(nx * nx + ny * ny + 1)
    nrm = np.stack([nx / norm, ny / norm, 1 / norm], -1) * 127.5 + 127.5
    diffuse = np.dstack([a, np.clip(20 + 0.6 * lum, 0, 255)]).astype(np.uint8)
    normal = np.dstack([nrm, np.full(h.shape, spec, np.float32)]).clip(0, 255).astype(np.uint8)
    return diffuse, normal


def calm(tile, scale, sat):
    """Darker, duller painted tile: RGB (float) luminance * scale, saturation * sat."""
    lum = tile @ LUM
    return np.clip((lum[..., None] + sat * (tile - lum[..., None])) * scale, 0, 255)


def put(atlas, k, tile):
    t = atlas.shape[0] // GRID
    y, x = divmod(k, GRID)
    atlas[y * t:(y + 1) * t, x * t:(x + 1) * t] = tile


def main(data_dir):
    cache = f"{data_dir}/landsat"
    os.makedirs(cache, exist_ok=True)
    made = {k: make_tile(landsat_block(cache, lon, lat, yr), (x, y, s), rel, sp, LOOK.get(k))
            for k, (name, lon, lat, yr, x, y, s, rel, sp) in TILES.items()}
    for kind, i in (("atlas", 0), ("atlas_normal", 1)):
        raw = subprocess.check_output(["git", "show", f"{SOURCE}:./map/terrain/{kind}0.dds"])
        a = np.array(Image.open(io.BytesIO(raw)).convert("RGBA"))
        assert a.shape[0] == GRID * T
        if kind == "atlas":
            for k, (scale, sat) in CALM.items():
                y, x = divmod(k, GRID)
                c = a[y * T:(y + 1) * T, x * T:(x + 1) * T]
                c[..., :3] = calm(c[..., :3].astype(np.float32), scale, sat).astype(np.uint8)
        for k, tiles in made.items():
            put(a, k, tiles[i])
        full = Image.fromarray(a, "RGBA")
        for lvl in range(3):
            img = full if lvl == 0 else full.resize((full.width >> lvl,) * 2, Image.LANCZOS)
            hdr = subprocess.check_output(["git", "show", f"{SOURCE}:./map/terrain/{kind}{lvl}.dds"])[:128]  # same size as before
            open(f"map/terrain/{kind}{lvl}.dds", "wb").write(dxt5_with_mips(img, hdr))
    print("slots:", {k: v[0] for k, v in TILES.items()})


def _selfcheck():
    a = np.random.default_rng(0).random((80, 80, 3)).astype(np.float32)
    s = seamless(a, 16)
    assert s.shape == (64, 64, 3) and np.allclose(s[16:, 16:], a[16:64, 16:64])
    assert np.allclose(s[16:, 0], a[16:64, 64]) and np.allclose(s[16:, -1], a[16:64, 63])  # wraps as in the source
    g = np.zeros((10, 10, 1), np.uint8)
    put(g, 17, np.full((2, 2, 1), 9, np.uint8))
    assert g[6, 4, 0] == 9 and g.sum() == 36
    c = calm(np.array([[[100.0, 160.0, 40.0]]]), 0.9, 0.5)[0, 0]
    assert abs(c @ LUM - 0.9 * (np.array([100.0, 160.0, 40.0]) @ LUM)) < 1e-6 and c.max() - c.min() < 60  # darker, duller


if __name__ == "__main__":
    _selfcheck()
    main(sys.argv[1])
