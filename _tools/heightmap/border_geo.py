"""Report state borders that should follow a river, lake or mountain crest but miss it.

"Should" comes from real boundaries (Natural Earth admin-0 + admin-1 lines): a mod border that lies on a real boundary
(>= REAL_SHARE of its pixels within REAL_PX) is checked against the features that real boundary follows. Flagged when
the real line runs on a feature (>= FOLLOW of its pixels) and the mod border does not (< MISS of its pixels).
  river  rivers.bmp pixels (all widths)
  lake   lake provinces and terrain index 14 (lakes drawn as water); a border may only run along the shore, so "on" is
         within LAKE_PX of the water
  crest  heightmap ridges: a local maximum across the ridge (DoG, sigma 1 vs 4) on high ground (>= RIDGE_MIN grey)
Borders that sit 2-6 px beside their real boundary for most of their length are listed as "offset".
Run from the mod root:
    python _tools/heightmap/border_geo.py <admin0_lines.geojson> <admin1_lines.geojson> [out_dir]
writes border_geo.csv (one row per flagged state pair, with location) and border_geo.png (overview).
"""
import csv, glob, io, json, re, sys, numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from gcps import land_mask_and_ids
import proj

ON_PX, LAKE_PX, REAL_PX, MIN_LEN = 1.5, 2.5, 4.0, 20
REAL_SHARE, FOLLOW, MISS = 0.6, 0.6, 0.4
RIDGE_MIN = 130
COLOURS = {"river": (220, 0, 0), "lake": (0, 90, 255), "crest": (255, 140, 0), "offset": (160, 0, 200)}


def read(p):
    return np.array(Image.open(io.BytesIO(open(p, "rb").read())))


def states():
    st, info = {}, {}
    for f in glob.glob("history/states/*.txt"):
        t = open(f, encoding="utf-8-sig", errors="replace").read()
        m, sid = re.search(r"provinces\s*=\s*\{([^}]*)\}", t), re.search(r"\bid\s*=\s*(\d+)", t)
        if not (m and sid):
            continue
        s = int(sid.group(1))
        o = re.search(r"\bowner\s*=\s*(\w+)", t)
        info[s] = (f.replace("\\", "/").split("/")[-1][:-4], o.group(1) if o else "")
        for p in map(int, re.findall(r"\d+", m.group(1))):
            st[p] = s
    return st, info


def real_lines(paths, shape):
    """Real boundaries rasterised 1 px wide in map pixels; segments jumping across the map edge are skipped."""
    H, W = shape
    im = Image.new("L", (W, H))
    d = ImageDraw.Draw(im)
    for p in paths:
        for f in json.load(open(p, encoding="utf-8"))["features"]:
            g = f["geometry"]
            if not g:
                continue
            for part in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
                c = np.array(part, np.float64)
                n = np.maximum(1, (np.abs(np.diff(c, axis=0)).max(1) / 0.02).astype(int))
                c = np.concatenate([a + (b - a) * (np.arange(k)[:, None] / k) for a, b, k in zip(c[:-1], c[1:], n)] + [c[-1:]])
                x, y = proj.to_px(c[:, 0], c[:, 1])
                for i in range(len(x) - 1):
                    if abs(x[i + 1] - x[i]) < W / 2:
                        d.line([(x[i], y[i]), (x[i + 1], y[i + 1])], fill=255)
    return np.array(im) > 0


def boundary_pairs(S):
    """(y, x, a, b) for every pixel whose right/down neighbour is another land state."""
    out = []
    for dy, dx in ((0, 1), (1, 0)):
        a, b = S[: S.shape[0] - dy, : S.shape[1] - dx], S[dy:, dx:]
        m = (a != b) & (a > 0) & (b > 0)
        ys, xs = np.nonzero(m)
        out.append(np.stack([ys, xs, np.minimum(a[m], b[m]), np.maximum(a[m], b[m])], 1))
    return np.concatenate(out)


def judge(border_d_real, border_d, real_d, on):
    """One border against one feature. border_d_real: border px -> distance to the real line; border_d / real_d: border
    px / nearby real-line px -> distance to the feature. Returns (flag, real share, real on feature, border on feature)."""
    real_share = (border_d_real <= REAL_PX).mean()
    real_on = (real_d <= on).mean() if len(real_d) else 0.0
    border_on = (border_d <= on).mean()
    return real_share >= REAL_SHARE and real_on >= FOLLOW and border_on < MISS, real_share, real_on, border_on


def main(admin0, admin1, out="."):
    ids, kinds = land_mask_and_ids()
    st, info = states()
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    S = np.where(land, np.vectorize(lambda p: st.get(p, 0), otypes=[np.int64])(ids), 0)
    riv, ter = read("map/rivers.bmp"), read("map/terrain.bmp")
    hm = read("map/heightmap.bmp").astype(np.float32)
    lake = np.isin(ids, [k for k, v in kinds.items() if v == "lake"]) | (ter == 14)
    dog = nd.gaussian_filter(hm, 1) - nd.gaussian_filter(hm, 4)
    feats = {"river": (riv <= 11), "lake": lake, "crest": (hm >= RIDGE_MIN) & (dog > 2) & land}
    on = {"river": ON_PX, "lake": LAKE_PX, "crest": ON_PX}
    dist = {n: nd.distance_transform_edt(~m) for n, m in feats.items()}
    real = real_lines([admin0, admin1], S.shape)
    d_real = nd.distance_transform_edt(~real)
    pairs = boundary_pairs(S)
    keys = pairs[:, 2] * 100000 + pairs[:, 3]
    order = np.argsort(keys, kind="stable")
    pairs, keys = pairs[order], keys[order]
    flags = []
    for grp in np.split(np.arange(len(keys)), np.flatnonzero(np.diff(keys)) + 1):
        if len(grp) < MIN_LEN:
            continue
        ys, xs = pairs[grp, 0], pairs[grp, 1]
        a, b = int(pairs[grp[0], 2]), int(pairs[grp[0], 3])
        y0, y1, x0, x1 = max(ys.min() - 6, 0), min(ys.max() + 7, S.shape[0]), max(xs.min() - 6, 0), min(xs.max() + 7, S.shape[1])
        bm = np.zeros((y1 - y0, x1 - x0), bool)
        bm[ys - y0, xs - x0] = True
        near_real = nd.binary_dilation(bm, iterations=int(REAL_PX)) & real[y0:y1, x0:x1]
        ry, rx = np.nonzero(near_real)
        bdr = d_real[ys, xs]
        lo, la = proj.to_lonlat(float(xs.mean()), float(ys.mean()))
        row = [info[a][0], info[b][0], info[a][1], info[b][1]]
        for n in feats:
            f, rs, ro, bo = judge(bdr, dist[n][ys, xs], dist[n][ry + y0, rx + x0], on[n])
            if f:
                flags.append(row + [n, len(grp), round(rs, 2), round(ro, 2), round(bo, 2), round(float(lo), 2), round(float(la), 2), a, b])
        off = ((bdr > 1.5) & (bdr <= 6)).mean()
        if off >= 0.6 and (bdr <= 1.5).mean() < 0.25:
            flags.append(row + ["offset", len(grp), round(off, 2), "", "", round(float(lo), 2), round(float(la), 2), a, b])
    flags.sort(key=lambda r: (r[4], -r[5]))
    with open(f"{out}/border_geo.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["state_a", "state_b", "owner_a", "owner_b", "feature", "border_px", "real_share", "real_on_feature",
                    "border_on_feature", "lon", "lat"])
        w.writerows(r[:-2] for r in flags)
    img = np.where(land, 205, 95).astype(np.uint8)[..., None].repeat(3, -1)
    img[real & land] = (150, 150, 150)
    for r in flags:
        m = (pairs[:, 2] == r[-2]) & (pairs[:, 3] == r[-1])
        img[pairs[m, 0], pairs[m, 1]] = COLOURS[r[4]]
    Image.fromarray(nd.grey_dilation(img, size=(3, 3, 1))).save(f"{out}/border_geo.png")
    print("flagged state borders:", {k: sum(r[4] == k for r in flags) for k in COLOURS},
          "| between different owners:", sum(r[2] != r[3] for r in flags))


if __name__ == "__main__":
    # border on the real line, real line on a river 2 px away from the border -> flagged; border on the river -> not
    assert judge(np.zeros(30), np.full(30, 2.0), np.zeros(30), ON_PX)[0]
    assert not judge(np.zeros(30), np.zeros(30), np.zeros(30), ON_PX)[0]
    assert not judge(np.full(30, 9.0), np.full(30, 2.0), np.zeros(30), ON_PX)[0]  # not a real boundary: no claim
    main(*sys.argv[1:4])
