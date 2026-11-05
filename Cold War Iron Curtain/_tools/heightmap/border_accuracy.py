"""How well do the mod's 1949 borders match the real ones (CShapes 2.0, 23 May 1949)? Run from the mod root.
python _tools/heightmap/border_accuracy.py <data_dir>   (data_dir holds cshapes/CShapes-2.0.geojson and dem/*.warp.npz)"""
import glob, json, re, sys, numpy as np
from collections import Counter
from PIL import Image, ImageDraw
from scipy import ndimage as nd
sys.path.insert(0, "_tools/heightmap")
from gcps import land_mask_and_ids

S = sys.argv[1]
DATE = (1949, 5, 23)
RES = 20  # cells per degree for the real-border raster

# --- real 1949 units -> label raster in lon/lat
feats = json.load(open(f"{S}/cshapes/CShapes-2.0.geojson", encoding="utf-8"))["features"]
alive = [f for f in feats if (f["properties"]["gwsyear"], f["properties"]["gwsmonth"], f["properties"]["gwsday"]) <= DATE
         <= (f["properties"]["gweyear"], f["properties"]["gwemonth"], f["properties"]["gweday"])]
names = {i + 1: f["properties"]["cntry_name"] for i, f in enumerate(alive)}
img = Image.new("I", (360 * RES, 180 * RES), 0)
dr = ImageDraw.Draw(img)
for i, f in enumerate(alive, 1):
    g = f["geometry"]
    for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
        ring = [((lo + 180) * RES, (90 - la) * RES) for lo, la in poly[0]]
        if len(ring) > 2:
            dr.polygon(ring, fill=i)
real_ll = np.asarray(img, np.int32)
print("real units alive on 1949-05-23:", len(alive))

# --- map pixels
ids, kinds = land_mask_and_ids()
w = np.load(glob.glob(f"{S}/dem/*.warp.npz")[0])
lo, la = w["lo"], w["la"]
real = real_ll[np.clip(((90 - la) * RES).astype(int), 0, 180 * RES - 1), ((lo + 180) % 360 * RES).astype(int)]
land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])

st, owner, sname = np.zeros(ids.max() + 1, np.int32), {}, {}
for f in glob.glob("history/states/*.txt"):
    t = open(f, encoding="utf-8", errors="ignore").read()
    m, pr = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
    if not (m and pr):
        continue
    sid = int(m.group(1))
    st[[int(p) for p in pr.group(1).split() if p.isdigit() and int(p) < len(st)]] = sid
    h = t[t.find("history"):]
    h = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=\s*\{", h)[0]  # top-level history = the 1949 start
    o = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", h)
    owner[sid] = o.group(1) if o else "???"
    sname[sid] = f.replace("\\", "/").split("/")[-1][:-4]
S_ = st[ids]
tags = sorted(set(owner.values()))
tid = {t: i + 1 for i, t in enumerate(tags)}
own = np.zeros(st.max() + 1, np.int32)
for sid, t in owner.items():
    own[sid] = tid[t]
O = np.where(land, own[S_], 0)


def edges(L):
    b = np.zeros(L.shape, bool)
    for ax in (0, 1):
        d = (np.roll(L, 1, ax) != L) & (L > 0) & (np.roll(L, 1, ax) > 0)
        b |= d
    return b & land & np.roll(land, 1, 0) & np.roll(land, 1, 1)


mod_b, state_b, real_b = edges(O), edges(np.where(land, S_, 0)), edges(np.where(land, real, 0))
d_real, (iy, ix) = nd.distance_transform_edt(~real_b, return_indices=True)
d_state = nd.distance_transform_edt(~state_b)


def km(y0, x0, y1, x1):
    p0, p1, l0, l1 = map(np.radians, (la[y0, x0], la[y1, x1], lo[y0, x0], lo[y1, x1]))
    a = np.sin((p1 - p0) / 2) ** 2 + np.cos(p0) * np.cos(p1) * np.sin((l1 - l0) / 2) ** 2
    return 6371 * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


ys, xs = np.nonzero(mod_b)
dk = km(ys, xs, iy[ys, xs], ix[ys, xs])
dp = d_real[ys, xs]
print(f"\nmod 1949 country borders: {len(ys)} px")
print(f"  distance to the real 1949 border: median {np.median(dk):.0f} km ({np.median(dp):.1f} px), "
      f"within 10 km {np.mean(dk <= 10):.0%}, within 25 km {np.mean(dk <= 25):.0%}, over 50 km {np.mean(dk > 50):.0%}")
ry, rx = np.nonzero(real_b)
print(f"real 1949 borders: {len(ry)} px; a mod state border within 3 px: {np.mean(d_state[ry, rx] <= 3):.0%}")

# worst stretches by country pair: mod border px more than 25 km from any real border
bad = np.zeros(ids.shape, bool)
bad[ys[dk > 25], xs[dk > 25]] = True
lab, n = nd.label(nd.binary_dilation(bad, iterations=2))
cnt = Counter()
where = {}
for y, x in zip(*np.nonzero(bad)):
    a = O[y, x]
    nb = [O[y + dy, (x + dx) % O.shape[1]] for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)) if 0 <= y + dy < O.shape[0]]
    other = next((b for b in nb if b and b != a), 0)
    if other:
        pair = tuple(sorted((tags[a - 1], tags[other - 1])))
        cnt[pair] += 1
        where.setdefault(pair, (y, x))
print("\nmod borders more than 25 km off the real 1949 line, by country pair (px):")
for pair, c in cnt.most_common(30):
    y, x = where[pair]
    print(f"  {pair[0]}-{pair[1]}: {c:4d} px  e.g. lon {lo[y, x]:7.2f} lat {la[y, x]:6.2f}  (state {sname.get(S_[y, x], '?')})")

# per country: share of its border within 10 km
per = Counter(); good = Counter()
for y, x, k in zip(ys, xs, dk):
    t = tags[O[y, x] - 1]
    per[t] += 1
    good[t] += k <= 10
print("\nlargest countries by border length, share within 10 km of the real 1949 border:")
for t, c in per.most_common(25):
    print(f"  {t}: {c:5d} px  {good[t] / c:.0%}")
Image.fromarray(np.where(mod_b[..., None], np.array([200, 30, 30], np.uint8),
                         np.where(real_b[..., None], np.array([30, 30, 200], np.uint8),
                                  np.where(land[..., None], np.uint8(235), np.uint8(170))))).save(f"{S}/borders_1949.png")
