"""Redraw the Soviet Arctic coast from Natural Earth 10m land, and clean the vertical streaks above the old map's edge.

The old (vanilla-layout) map ended around 72-74N; reprojection cut Yamal, Gydan, Taymyr and the Lena delta flat at that
edge and stretched the old terrain painting (marsh) upwards in streaks. Inside BOX:
- real land that is sea on the map joins the land province it touches (only pieces connected to existing land)
- map land that is sea in reality joins the sea province it touches
- no province loses more than KEEP of its pixels, lakes are left alone
- terrain.bmp: a horizontal majority filter on land wipes the vertical streaks; new land takes the nearest land terrain;
  all sea beyond 60N/60S gets the ocean index
- heightmap / colormap / rivers / world_normal: changed pixels take the nearest value of their new kind
Then run mapfix.py (coastal flags, regions), positions.py, then terrainmap.py (or the rest of rebuild_all.sh).

Run from the mod root:  python _tools/heightmap/arctic_coast.py <ne_10m_land.geojson> <undithered terrain.bmp> [LON0 LON1 LAT0]
(run once per box; North America + Greenland was -170 -10 58)
"""
import io, json, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
import proj
from gcps import land_mask_and_ids
from newareas import grow
from colormap import dds_header, dxt5_with_mips

LON0, LON1, LAT0 = 25.0, 190.0, 66.0   # Soviet Arctic coast, Kola to Chukotka
KEEP = 0.5                              # a province keeps at least this share of its pixels
SEA_T = 15                              # terrain.bmp index on sea
STREAK_W = 9                            # px, horizontal majority window for the streaks


def ne_land(path, rows):
    """Natural Earth land polygons -> bool mask of the top `rows` map rows."""
    img = Image.new("L", (proj.W, rows), 0)
    d = ImageDraw.Draw(img)
    for f in json.load(open(path))["features"]:
        g = f["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            for i, ring in enumerate(poly):
                r = np.asarray(ring, np.float64)
                if r[:, 1].max() < LAT0 - 2:
                    continue
                x, y = proj.to_px(r[:, 0], np.clip(r[:, 1], -89.9, 89.9))
                x = np.unwrap(x * (2 * np.pi / proj.W)) * (proj.W / (2 * np.pi))  # no jump across the seam
                for off in (-proj.W, 0, proj.W):
                    d.polygon(list(zip(x + off, y)), fill=0 if i else 1)
    return np.asarray(img) > 0


def nearest(a, valid):
    """every pixel takes the value of the nearest valid pixel."""
    idx = nd.distance_transform_edt(~valid, return_distances=False, return_indices=True)
    return a[tuple(idx)]


def capped(changed, ids, lost_ids):
    """drop changes that would take more than 1-KEEP of a province."""
    tot = np.bincount(ids.ravel(), minlength=ids.max() + 1)
    lost = np.bincount(lost_ids[changed], minlength=tot.size)
    bad = lost > (1 - KEEP) * np.maximum(tot, 1)
    return changed & ~bad[lost_ids], int(bad.sum())


def coastal(ids, land, sea):
    """ids of land provinces with a sea 4-neighbour (east/west wrap)."""
    s = np.zeros_like(sea)
    for sh, ax in ((1, 0), (-1, 0), (1, 1), (-1, 1)):
        s |= np.roll(sea, sh, ax)
    return set(np.unique(ids[land & s]).tolist())


def read_img(path):
    return Image.open(io.BytesIO(open(path, "rb").read()))  # PIL mmaps a file path; Windows can't overwrite it then


def main(geojson, terrain_src, lon0=LON0, lon1=LON1, lat0=LAT0):
    global LON0, LON1, LAT0
    LON0, LON1, LAT0 = float(lon0), float(lon1), float(lat0)
    ids_full, kinds = land_mask_and_ids()
    lo, la = proj.to_lonlat(np.arange(proj.W)[None, :] + 0.5, np.arange(proj.H)[:, None] + 0.5)
    R = (int(np.argmax(la[:, 0] < LAT0 - 1)) + 1) & ~1  # rows down to just below LAT0, even for the half-res layers
    ids, lo, la = ids_full[:R].copy(), np.broadcast_to(lo, (R, proj.W)), la[:R]
    box = (((lo - LON0) % 360) < (LON1 - LON0)) & (la >= LAT0)
    kind = np.vectorize(lambda i: kinds.get(i, ""), otypes=[object])
    k = kind(ids)
    land, sea = k == "land", k == "sea"
    ne = nd.median_filter(ne_land(geojson, R).astype(np.uint8), 3, mode="wrap") > 0  # no 1 px crumbs

    add = box & ne & sea
    lab = grow(np.where(land, ids, 0), add | land)  # unbounded: only pieces connected to land
    add &= lab > 0
    add, n1 = capped(add, ids_full, ids)
    rem = box & ~ne & land
    slab = grow(np.where(sea, ids, 0), rem | sea)
    rem &= slab > 0
    rem, n2 = capped(rem, ids_full, ids)
    # no province may lose its coast (Murmansk's naval base: the 10m coastline closes Kola Bay): new land near one that
    # would is dropped, until none does
    before = coastal(ids, land, sea)
    for _ in range(20):
        new = ids.copy()
        new[add], new[rem] = lab[add], slab[rem]
        lost = before - coastal(new, (land | add) & ~rem, (sea | rem) & ~add)
        if not lost:
            break
        add &= ~nd.binary_dilation(np.isin(ids, list(lost)), iterations=8)
    assert not lost, lost
    print(f"new land px {int(add.sum())}, new sea px {int(rem.sum())}; provinces held back by KEEP: {n1}+{n2}")

    # provinces.bmp
    rgb_of = {}
    for line in open("map/definition.csv", encoding="utf-8", errors="ignore"):
        p = line.strip().split(";")
        if len(p) >= 4 and p[0].isdigit():
            rgb_of[int(p[0])] = (int(p[1]), int(p[2]), int(p[3]))
    prov = np.array(read_img("map/provinces.bmp").convert("RGB"))
    ch = add | rem
    prov[:R][ch] = np.array([rgb_of[i] for i in new[ch]], np.uint8).reshape(-1, 3)
    Image.fromarray(prov, "RGB").save("map/provinces.bmp")
    land_n = (land | add) & ~rem

    # heightmap: nearest value of the new kind, land never below the 96 floor
    hm = np.array(read_img("map/heightmap.bmp"))
    top = hm[:R]
    top[add] = np.maximum(nearest(top, land & ~add)[add], 97)
    top[rem] = np.minimum(nearest(top, sea & ~rem)[rem], 88)
    Image.fromarray(hm, "L").save("map/heightmap.bmp")

    # terrain (undithered source): streaks out, then new land / sea
    ti = read_img(terrain_src)
    t, pal = np.array(ti), ti.getpalette()
    tt = t[:R]
    fixed = np.isin(tt, (14, 23)) | ~land_n  # lakes, ice sheets and water keep their index
    streak = box & land_n & ~fixed
    score, best = np.zeros(tt.shape, np.float32), tt.copy()
    for v in np.unique(tt[streak]):
        c = nd.uniform_filter1d(((tt == v) & streak).astype(np.float32), STREAK_W, axis=1, mode="wrap")
        b = c > score
        score[b], best[b] = c[b], v
    tt[streak] = best[streak]
    tt[add] = nearest(tt, land & ~add & ~np.isin(tt, (14,)))[add]
    tt[rem] = SEA_T
    # polar sea floor: stretched old painting and the new polar areas left land indices under the water, which the
    # underwater fog shows through in the shallows as streaks
    _, lat_full = proj.to_lonlat(0.0, np.arange(proj.H)[:, None] + 0.5)
    t[(np.isin(ids_full, [i for i, v in kinds.items() if v == "sea"]) & (np.abs(lat_full) >= 60)) & (t != SEA_T)] = SEA_T
    o = Image.fromarray(t, "P"); o.putpalette(pal); o.save("map/terrain.bmp")

    # rivers: 254 = water, 255 = land without river
    ri = read_img("map/rivers.bmp")
    r, rpal = np.array(ri), ri.getpalette()
    r[:R][add], r[:R][rem] = 255, 254
    o = Image.fromarray(r, "P"); o.putpalette(rpal); o.save("map/rivers.bmp")

    # half-res layers: colormap (RGB from the nearest land/sea texel, city-light alpha kept) and world_normal (flat)
    a2, r2 = add[::2, ::2] | add[1::2, 1::2], rem[::2, ::2] | rem[1::2, 1::2]
    land2 = land_n[::2, ::2]
    cm = np.array(Image.open("map/terrain/colormap_rgb_cityemissivemask_a.dds").convert("RGBA"))
    R2 = R // 2
    ctop = cm[:R2]
    for m, valid in ((a2, land2 & ~a2), (r2, ~land2 & ~r2)):
        for c in range(3):
            ctop[..., c][m] = nearest(ctop[..., c], valid)[m]
    img = Image.fromarray(cm, "RGBA")
    open("map/terrain/colormap_rgb_cityemissivemask_a.dds", "wb").write(dxt5_with_mips(img, dds_header(img)))
    nm = np.array(read_img("map/world_normal.bmp"))
    nm[:R2][a2 | r2] = (128, 128, 255)
    Image.fromarray(nm, "RGB").save("map/world_normal.bmp")


if __name__ == "__main__":
    t = np.array([[0, 0, 5], [0, 7, 0]]); assert (nearest(t, t > 0) > 0).all()
    main(*sys.argv[1:6])
