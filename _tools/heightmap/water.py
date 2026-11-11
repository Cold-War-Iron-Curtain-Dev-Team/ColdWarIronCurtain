"""Rebuild map/terrain/colormap_water_{0,1,2}.dds (seabed tint for the underwater pass in pdxmap.shader) from depth.

Run from the mod root:  python ../_tools/heightmap/water.py <etopo.nc> <out_dir> [marine_polys.geojson] [lakes_dir]
Shallows -> shelf -> navy deep ocean by depth, greyer toward the poles, soft hillshade so ridges and trenches read.
Shallows are turquoise in warm seas, grey-green on cold shelves. With the Natural Earth marine polygons and lakes,
named seas and lakes take their real true-colour look (SEAS, LAKES), kept darker where deeper. The shader multiplies it by WATER_COLOR_LIGHTNESS (0.7). All three files get the same image
(the mod's _1/_2 were identical painted art on the old coastline); each keeps its format, one mip level like before.
"""
import json, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from build import WRAP, warp
from gcps import land_mask_and_ids
import proj

# depth (m) -> sRGB
STOPS = [(0, (80, 200, 195)), (30, (58, 172, 182)), (200, (40, 125, 165)), (1000, (34, 92, 140)),
         (3000, (26, 64, 116)), (6000, (18, 46, 94))]  # deep ocean ~vanilla brightness (was half of it)
COLD_SHALLOW = [(0, (72, 138, 134)), (30, (56, 118, 128)), (200, (40, 104, 140))]  # cold shelves: grey-green
POLAR = np.array((48, 84, 100), np.float32)  # cold-water grey-teal
LAKE = np.array((30, 76, 94), np.float32)  # lakes without their own colour
RIVER = np.array((34, 58, 60), np.float32)  # inland water base; rivers sample this map, not the sea
REF_LUM = 105.0  # ~luminance of the 200 m shelf colour; region colours are scaled by local luminance relative to it

# real true-colour look of named seas (Natural Earth marine polygon names): colour, strength
_MED = ((22, 72, 152), 0.5)
_NORTH = ((46, 94, 98), 0.5)
_BALTIC = ((36, 74, 70), 0.6)
_ARCTIC = ((44, 80, 94), 0.45)
_ESTUARY = ((96, 98, 74), 0.6)
SEAS = {
    **{n: _MED for n in ("Mediterranean Sea", "Adriatic Sea", "Aegean Sea", "Ionian Sea", "Tyrrhenian Sea", "Ligurian Sea",
                         "Balearic Sea", "Alboran Sea", "Sea of Crete", "Gulf of Sidra", "Golfe du Lion", "Gulf of Gabès")},
    "Sea of Marmara": ((30, 80, 120), 0.5),
    "Black Sea": ((22, 62, 92), 0.6), "Sea of Azov": ((80, 106, 74), 0.65),
    "Caspian Sea": ((30, 86, 110), 0.5), "Garabogaz Bay": ((70, 150, 140), 0.6),
    **{n: _BALTIC for n in ("Baltic Sea", "Gulf of Bothnia", "Gulf of Finland", "Gulf of Riga")},
    **{n: _NORTH for n in ("North Sea", "Skagerrak", "Kattegat", "Waddenzee", "English Channel", "Irish Sea", "Bristol Channel")},
    "White Sea": ((42, 68, 64), 0.55),
    **{n: _ARCTIC for n in ("Barents Sea", "Kara Sea", "Laptev Sea", "East Siberian Sea", "Chukchi Sea", "Beaufort Sea",
                            "Arctic Ocean", "Greenland Sea", "Lincoln Sea", "Baffin Bay", "The North Western Passages")},
    **{n: _ESTUARY for n in ("Gulf of Ob", "Yenisey Gulf", "Mackenzie Bay")},
    **{n: ((34, 66, 90), 0.5) for n in ("Hudson Bay", "James Bay", "Foxe Basin", "Hudson Strait", "Ungava Bay")},
    "Gulf of Saint Lawrence": ((38, 76, 88), 0.45),
    "Yellow Sea": ((70, 106, 92), 0.45), "Bo Hai": ((86, 106, 84), 0.55), "East China Sea": ((44, 100, 120), 0.3),
    "Hangzhou Bay": ((124, 110, 78), 0.7), "Yangtze River": ((124, 110, 78), 0.7),
    "Persian Gulf": ((50, 140, 135), 0.5), "Gulf of Oman": ((30, 92, 128), 0.35),
    **{n: ((24, 78, 142), 0.45) for n in ("Red Sea", "Gulf of Aqaba", "Gulf of Suez", "Gulf of Aden")},
    **{n: ((20, 80, 152), 0.3) for n in ("Caribbean Sea", "Coral Sea", "Sulu Sea", "Celebes Sea", "Banda Sea")},
    "Gulf of Mexico": ((28, 82, 130), 0.3),
    **{n: ((128, 110, 76), 0.7) for n in ("Río de la Plata", "Amazon River")},
    "Bay of Bengal": ((40, 92, 118), 0.3),
    **{n: ((32, 66, 96), 0.4) for n in ("Sea of Okhotsk", "Bering Sea", "Gulf of Alaska")},
    "Sea of Japan": ((26, 70, 120), 0.3), "Arabian Sea": ((28, 80, 128), 0.25),
    # no "SOUTHERN OCEAN": its polygon ends on a straight 60°S line; the polar tint already greys it
    **{n: ((30, 60, 88), 0.4) for n in ("Weddell Sea", "Ross Sea", "Amundsen Sea", "Bellingshausen Sea")},
    "Java Sea": ((34, 104, 120), 0.35), "Gulf of Thailand": ((36, 104, 116), 0.35), "Gulf of Tonkin": ((44, 100, 104), 0.4),
}
# lakes (Natural Earth lake names): colour, strength; applied to the map's lake water near each real outline
LAKES = {
    "Lake Baikal": ((20, 62, 104), 0.85), "Lake Ladoga": ((40, 58, 58), 0.8), "Lake Onega": ((40, 58, 58), 0.8),
    "Lake Superior": ((26, 70, 108), 0.8), "Lake Michigan": ((34, 92, 122), 0.8), "Lake Huron": ((34, 92, 122), 0.8),
    "Lake Erie": ((52, 110, 100), 0.8), "Lake Ontario": ((34, 86, 112), 0.8), "Lake Victoria": ((48, 98, 72), 0.8),
    "Lake Tanganyika": ((22, 66, 112), 0.8), "Lake Malawi": ((22, 66, 112), 0.8), "Lake Balkhash": ((66, 122, 110), 0.8),
    "Issyk-Kul": ((28, 90, 142), 0.85), "Lago Titicaca": ((32, 80, 112), 0.8), "Lake Chad": ((92, 110, 72), 0.8),
    "Great Bear Lake": ((30, 70, 98), 0.8), "Great Slave Lake": ((30, 70, 98), 0.8), "Lake Winnipeg": ((70, 94, 76), 0.8),
    "Vänern": ((34, 70, 80), 0.8), "Lake Peipus": ((48, 66, 58), 0.8), "Lake Turkana": ((56, 112, 92), 0.8),
    "Lake Van": ((30, 86, 130), 0.8), "Lake Urmia": ((80, 120, 110), 0.8), "Qinghai Hu": ((36, 96, 126), 0.8),
    "Lago de Nicaragua": ((66, 100, 84), 0.8),
}
ARAL = ((50, 130, 138), 0.85, (58.0, 62.5, 43.3, 47.0))  # 1960s Aral = lake water in this lon/lat box (NE has today's)
TURBID = (100, 118, 84)  # the shallow northern Caspian (< 12 m) is silty yellow-green


def polygons(path, names, shape):
    """{name: bool mask} at shape (half res). Rings are unwrapped across the map seam and drawn at x-W, x, x+W;
    a ring around a pole is closed along the top or bottom edge."""
    H, W = shape
    out = {}
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        n, g = f["properties"].get("name"), f["geometry"]
        if n not in names or not g:
            continue
        im = Image.new("L", (W, H))
        d = ImageDraw.Draw(im)
        for poly in [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]:
            for k, ring in enumerate(poly):
                c = np.array(ring, np.float64)
                x, y = proj.to_px(c[:, 0], c[:, 1])
                x, y = np.asarray(x, np.float64) / 2, np.asarray(y, np.float64) / 2
                x = x + W * np.concatenate([[0], np.cumsum(np.round(-np.diff(x) / W))])
                pts = list(zip(x, y))
                if abs(x[-1] - x[0]) > W / 2:
                    edge = 0 if y.mean() < H / 2 else H
                    pts += [(x[-1], edge), (x[0], edge)]
                for sh in (-W, 0, W):
                    d.polygon([(px + sh, py) for px, py in pts], fill=0 if k else 255)
        out[n] = out.get(n, False) | (np.array(im) > 0)
    return out


def tint(rgb, mask, colour, strength, soft=7.0):
    """pull rgb toward colour inside mask (soft edges), keeping the depth shading: darker where deeper."""
    w = np.clip(nd.gaussian_filter(mask.astype(np.float32), soft, mode=WRAP) * 1.3, 0, 1)[..., None] * strength
    lum = (rgb @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
    target = np.array(colour, np.float32) * np.clip(lum / REF_LUM, 0.55, 1.35)
    return rgb + w * (target - rgb)


def main(dem_path, out, marine=None, lakes_dir=None):
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
    cold = COLD_SHALLOW + STOPS[3:]
    cd, cc = np.array([s[0] for s in cold], np.float32), np.array([s[1] for s in cold], np.float32)
    rgb_cold = np.stack([np.interp(x, np.log1p(cd), cc[:, c]) for c in range(3)], -1)
    rgb = rgb + np.clip((alat - 28) / 22, 0, 1)[..., None] * (rgb_cold - rgb)  # reef turquoise only in warm seas
    shallow = np.clip(1 - depth / 300, 0, 1)[..., None]  # polar tint mostly on the shelves
    pol = (np.clip((alat - 45) / 25, 0, 1)[..., None] * (0.35 + 0.4 * shallow))
    rgb = rgb + pol * (POLAR - rgb)
    # hillshade from the northwest, same side as the map sun
    gy, gx = np.gradient(nd.gaussian_filter(np.log1p(depth), 2.0, mode=WRAP))
    rgb *= np.clip(1 + 6.0 * (gx + gy), 0.8, 1.2)[..., None]
    lk = nd.gaussian_filter(lake.astype(np.float32), 1.0, mode=WRAP)[..., None]
    rgb = rgb + lk * (LAKE - rgb)
    water = sea | lake
    if marine:
        masks = polygons(marine, set(SEAS), sea.shape)
        for n, (colour, strength) in SEAS.items():
            if n in masks:
                rgb = tint(rgb, masks[n] & water, colour, strength)
        if "Caspian Sea" in masks:
            rgb = tint(rgb, masks["Caspian Sea"] & water & (depth < 12), TURBID, 0.6, soft=2.5)
        print("sea colours:", len(masks), "of", len(SEAS), "missing:", sorted(set(SEAS) - set(masks)))
    if lakes_dir:
        masks = polygons(f"{lakes_dir}/ne_10m_lakes.geojson", set(LAKES), sea.shape)
        for n, (colour, strength) in LAKES.items():
            if n in masks:  # lake provinces sit a few px off the real outline
                rgb = tint(rgb, nd.binary_dilation(masks[n], iterations=4) & lake, colour, strength, soft=1.5)
        colour, strength, (lo0, lo1, la0, la1) = ARAL
        (x0, x1), (y0, y1) = (np.asarray(v) / 2 for v in proj.to_px(np.array([lo0, lo1]), np.array([la1, la0])))
        box = np.zeros_like(lake)
        box[int(y0):int(y1) + 1, int(x0):int(x1) + 1] = True
        rgb = tint(rgb, box & lake, colour, strength, soft=1.5)
        print("lake colours:", len(masks), "of", len(LAKES), "missing:", sorted(set(LAKES) - set(masks)))
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
    t = tint(np.full((20, 20, 3), 100, np.float32), np.ones((20, 20), bool), (0, 0, 200), 1.0, soft=0.5)
    assert abs(t[10, 10, 2] - 200 * 100 / REF_LUM) < 2 and t[10, 10, 0] < 1  # full strength: luminance-scaled colour
    main(*sys.argv[1:5])
