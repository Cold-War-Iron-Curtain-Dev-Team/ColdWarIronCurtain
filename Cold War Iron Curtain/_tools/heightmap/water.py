"""Rebuild map/terrain/colormap_water_{0,1,2}.dds (seabed tint for the underwater pass in pdxmap.shader) from depth.

Run from the mod root:  python _tools/heightmap/water.py <etopo.nc> <out_dir>
Turquoise shallows -> teal shelf -> navy deep ocean, a little greyer toward the poles, dark lakes, soft hillshade so
ridges and trenches read. The shader multiplies it by WATER_COLOR_LIGHTNESS (0.7). All three files get the same image
(the mod's _1/_2 were identical painted art on the old coastline); each keeps its format, one mip level like before.
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from build import WRAP, warp
from gcps import land_mask_and_ids

# depth (m) -> sRGB
STOPS = [(0, (80, 200, 195)), (30, (55, 170, 180)), (200, (34, 115, 155)), (1000, (24, 72, 122)),
         (3000, (15, 44, 92)), (6000, (9, 28, 66))]
POLAR = np.array((48, 84, 100), np.float32)  # cold-water grey-teal
LAKE = np.array((24, 62, 74), np.float32)
RIVER = np.array((34, 58, 60), np.float32)  # inland water base; rivers sample this map, not the sea


def main(dem_path, out):
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    lake = np.isin(ids, [k for k, v in kinds.items() if v == "lake"])
    lo, la, z, rc = warp(dem_path, sea)
    depth = -nd.map_coordinates(z, rc(lo, la), order=1, mode="wrap").astype(np.float32)
    half = lambda a: a.reshape(a.shape[0] // 2, 2, a.shape[1] // 2, 2).mean((1, 3))
    depth, alat = half(depth), np.abs(half(la))
    sea, lake = half(sea.astype(np.float32)) > .5, half(lake.astype(np.float32)) > .5
    del lo, la, z

    # sea pixels the DEM calls land (warp error on the coast) are shallow; land is shallow too so coasts blend
    depth = nd.gaussian_filter(np.where(sea, np.maximum(depth, 2.0), 2.0), 1.0, mode=WRAP)

    d, cols = np.array([s[0] for s in STOPS], np.float32), np.array([s[1] for s in STOPS], np.float32)
    x = np.log1p(np.clip(depth, 0, 6000))
    rgb = np.stack([np.interp(x, np.log1p(d), cols[:, c]) for c in range(3)], -1)
    shallow = np.clip(1 - depth / 300, 0, 1)[..., None]  # polar tint mostly on the shelves
    pol = (np.clip((alat - 45) / 25, 0, 1)[..., None] * (0.35 + 0.4 * shallow))
    rgb = rgb + pol * (POLAR - rgb)
    # hillshade from the northwest, same side as the map sun
    gy, gx = np.gradient(nd.gaussian_filter(np.log1p(depth), 2.0, mode=WRAP))
    rgb *= np.clip(1 + 6.0 * (gx + gy), 0.8, 1.2)[..., None]
    lk = nd.gaussian_filter(lake.astype(np.float32), 1.0, mode=WRAP)[..., None]
    rgb = rgb + lk * (LAKE - rgb)
    # inland (rivers): a dark river base mixed with the local land colour (muddy in deserts, dark green in forests)
    # instead of the shallow-reef turquoise; a 1.5 px blend keeps the coast and river mouths smooth
    landc = np.asarray(Image.open("map/terrain/colormap_rgb_cityemissivemask_a.dds").convert("RGB")).astype(np.float32)
    assert landc.shape[:2] == rgb.shape[:2], (landc.shape, rgb.shape)
    river = 0.6 * RIVER + 0.4 * 0.55 * landc
    lw = np.clip(nd.gaussian_filter((~sea & ~lake).astype(np.float32), 1.5, mode=WRAP) * 1.6 - 0.3, 0, 1)[..., None]
    rgb = rgb + lw * (river - rgb)

    img = Image.fromarray(np.clip(np.rint(rgb), 0, 255).astype(np.uint8), "RGB")
    img.save(f"{out}/water_preview.png")
    for i in range(3):
        fmt = open(f"map/terrain/colormap_water_{i}.dds", "rb").read(128)[84:88].decode()
        img.convert("RGBA").save(f"{out}/colormap_water_{i}.dds", "DDS", pixel_format=fmt)
    print("mean sea colour", rgb[sea].mean(0).round(1))


if __name__ == "__main__":
    main(*sys.argv[1:])
