"""Split land strategic regions that mix clearly different climates (a region's weather is the mean over all of it, so
the Mojave shared snow with the Rockies). Each split piece is contiguous and keeps a real share of the region; the
biggest piece keeps the old id (scripts referencing it still work), the others get new ids.

Run from the mod root:  python _tools/heightmap/climsplit.py <worldclim_dir> [--write]
Then rerun weather.py so the pieces get their own weather.
Writes: map/strategicregions/*, map/weatherpositions.txt, common/ai_areas/default.txt,
localisation/*/cwic_climate_regions_l_*.yml. Without --write it only lists the splits.
"""
import glob, re, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
import proj
from gcps import land_mask_and_ids
from mapfix import adjacency
from weather import worldclim

STEP = 2              # sample every 2nd pixel
SCALE = np.array([6.0, 6.0, 0.55, 1.5])  # coldest-month C, warmest-month C, log(annual precip + 250 mm): one unit = a clear
# difference (the +250 keeps desert-vs-desert rain differences, meaningless for weather, from counting); months below
# freezing, 1.5 months (what decides whether a region gets snow at all)
MIN_GAP = 1.6         # centroid distance (scaled) worth a split, e.g. ~10 C colder winters, or 2.6x the rain
MIN_SHARE, MIN_PROVS = 0.15, 4
SNOW_SHARE, SNOW_PROVS = 0.06, 3  # a frost-free corner of a snowy region (Las Vegas in the Rockies) may be small
DEPTH = 2             # at most 4 pieces per region
# compass names N, NE, E, SE, S, SW, W, NW and the name pattern, per language
DIRS = {"english": (("North", "North-East", "East", "South-East", "South", "South-West", "West", "North-West"), "{n} ({d})"),
        "french": (("Nord", "Nord-Est", "Est", "Sud-Est", "Sud", "Sud-Ouest", "Ouest", "Nord-Ouest"), "{n} ({d})"),
        "japanese": (("北部", "北東部", "東部", "南東部", "南部", "南西部", "西部", "北西部"), "{n}{d}"),
        "russian": (("Север", "Северо-Восток", "Восток", "Юго-Восток", "Юг", "Юго-Запад", "Запад", "Северо-Запад"), "{n} ({d})")}


def features(ids, kinds, wc_dir):
    lo, la = proj.grid()
    s = (slice(None, None, STEP), slice(None, None, STEP))
    pid, lo, la = ids[s], lo[s], la[s]
    land = np.isin(pid, [k for k, v in kinds.items() if v == "land"])
    rows, cols = (90 - la) * 6 - .5, (lo + 180) % 360 * 6 - .5
    month = {}
    for var in ("tmin", "tmax", "prec"):
        a = worldclim(wc_dir, var)
        month[var] = np.stack([nd.map_coordinates(m, [rows, cols], order=0, mode="wrap", cval=np.nan) for m in a])
    ok = land & np.isfinite(month["tmin"]).all(0) & np.isfinite(month["prec"]).all(0)
    tmean = (month["tmin"] + month["tmax"]) / 2
    f = np.stack([tmean.min(0), tmean.max(0), np.log(month["prec"].sum(0) + 250.0), (tmean < 0).sum(0)], -1)
    n = int(ids.max()) + 1
    w = np.bincount(pid[ok], minlength=n).astype(float)
    feat = np.stack([np.bincount(pid[ok], weights=f[..., i][ok], minlength=n) for i in range(4)], -1) / np.maximum(w, 1)[:, None]
    return feat / SCALE, w


def split2(ps, feat, w, nb):
    """two contiguous climate pieces of province list ps, or None: first frost-free vs freezing winters, else 2-means."""
    X, ww = feat[ps], w[ps]
    if ww.sum() == 0 or len(ps) < 2 * SNOW_PROVS:
        return None
    freeze = X[:, 3] * SCALE[3]
    if (freeze < 0.5).any() and (freeze >= 2).any():
        r = finish(ps, (freeze < 1.25).astype(int), X, ww, nb, SNOW_SHARE, SNOW_PROVS, 1.4)
        if r and abs(r[2][0][0] - r[2][1][0]) >= 3.0:  # at least 3 C apart in the coldest month
            return r
    if len(ps) < 2 * MIN_PROVS:
        return None
    # farthest-pair init, weighted 2-means
    a = np.argmax(((X - np.average(X, 0, ww)) ** 2).sum(1) * (ww > 0))
    b = np.argmax(((X - X[a]) ** 2).sum(1) * (ww > 0))
    c = np.stack([X[a], X[b]])
    for _ in range(20):
        lab = ((X[:, None] - c[None]) ** 2).sum(2).argmin(1)
        if lab.min() == lab.max():
            return None
        c = np.stack([np.average(X[lab == k], 0, ww[lab == k] + 1e-9) for k in (0, 1)])
    return finish(ps, lab, X, ww, nb, MIN_SHARE, MIN_PROVS, MIN_GAP)


def finish(ps, lab, X, ww, nb, min_share, min_provs, min_gap):
    """make both sides of a 0/1 labelling contiguous and check sizes and climate gap."""
    w = dict(zip(ps, ww))
    # contiguity: each cluster keeps its largest connected part; the rest joins the side it touches most
    idx = {p: i for i, p in enumerate(ps)}
    for _ in range(5):
        moved = False
        for k in (0, 1):
            mem = {p for p in ps if lab[idx[p]] == k}
            parts, seen = [], set()
            for p in mem:
                if p in seen:
                    continue
                part, todo = set(), [p]
                while todo:
                    x = todo.pop()
                    if x not in part:
                        part.add(x); todo += [q for q in nb.get(x, {}) if q in mem and q not in part]
                seen |= part; parts.append(part)
            parts.sort(key=lambda s: -sum(w[p] for p in s))
            for part in parts[1:]:
                for p in part:
                    lab[idx[p]] = 1 - k
                moved = True
        if not moved:
            break
    shares = np.array([ww[lab == k].sum() for k in (0, 1)]) / ww.sum()
    counts = np.array([(lab == k).sum() for k in (0, 1)])
    if shares.min() < min_share or counts.min() < min_provs:
        return None
    c = np.stack([np.average(X[lab == k], 0, ww[lab == k] + 1e-9) for k in (0, 1)])
    gap = np.sqrt(((c[0] - c[1]) ** 2).sum())
    if gap < min_gap:
        return None
    return [[p for p in ps if lab[idx[p]] == k] for k in (0, 1)], gap, c * SCALE


def main(wc_dir, write=False):
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    nb = adjacency(ids)
    feat, w = features(ids, kinds, wc_dir)
    regions = {}
    for f in glob.glob("map/strategicregions/*.txt"):
        t = open(f, "rb").read().decode("utf-8", "surrogateescape")
        rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        regions[rid] = (f, t, [int(v) for v in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()])
    names = {}
    for l in open("localisation/english/strategic_region_names_l_english.yml", encoding="utf-8-sig"):
        m = re.match(r'\s*STRATEGICREGION_(\d+):\d*\s*"(.*)"', l)
        if m:
            names[int(m.group(1))] = m.group(2)
    loc_names = {lang: {} for lang in DIRS}
    for lang in DIRS:
        for f in glob.glob(f"localisation/{lang}/*.yml"):
            for l in open(f, encoding="utf-8-sig", errors="ignore"):
                m = re.match(r'\s*STRATEGICREGION_(\d+):\d*\s*"(.*)"', l)
                if m and m.group(2):
                    loc_names[lang][int(m.group(1))] = m.group(2)

    cx = nd.mean(np.broadcast_to(np.arange(W) + .5, ids.shape), ids, np.arange(ids.max() + 1))
    cy = nd.mean(np.broadcast_to((np.arange(H) + .5)[:, None], ids.shape), ids, np.arange(ids.max() + 1))
    cx, cy = np.nan_to_num(cx), np.nan_to_num(cy)

    next_id = max(regions) + 1
    new = []  # (parent, new id, provinces, direction index)
    keep = {}
    for rid, (f, t, ps) in sorted(regions.items()):
        land = [p for p in ps if kinds.get(p) == "land"]
        if len(land) * 2 <= len(ps) or cy[land].mean() > H * 0.93:  # sea regions; Antarctica (impassable) needs no weather detail
            continue
        pieces = [land]
        for _ in range(DEPTH):
            nxt = []
            for pc in pieces:
                r = split2(pc, feat, w, nb)
                if r:
                    (a, b), gap, c = r
                    print(f"  {rid:3d} {names.get(rid, '?')[:24]:24s} split gap {gap:.1f}: winter {c[0][0]:5.1f}/{c[1][0]:5.1f} C"
                          f"  summer {c[0][1]:5.1f}/{c[1][1]:5.1f} C  rain {np.exp(c[0][2]) - 250:5.0f}/{np.exp(c[1][2]) - 250:5.0f} mm"
                          f"  provs {len(a)}/{len(b)}")
                    nxt += [a, b]
                else:
                    nxt.append(pc)
            pieces = nxt
        if len(pieces) == 1:
            continue
        pieces.sort(key=lambda pc: -w[pc].sum())
        rest = [p for p in ps if p not in set(land)]  # water/lake provinces stay with the main piece
        keep[rid] = pieces[0] + rest
        mx, my = np.average(cx[pieces[0]], weights=w[pieces[0]] + 1), np.average(cy[pieces[0]], weights=w[pieces[0]] + 1)
        for pc in pieces[1:]:
            px, py = np.average(cx[pc], weights=w[pc] + 1), np.average(cy[pc], weights=w[pc] + 1)
            dx, dy = px - mx, py - my
            d = int(np.round(np.degrees(np.arctan2(dx, -dy)) / 45)) % 8  # image y grows south
            new.append((rid, next_id, pc, d)); next_id += 1
    print(f"{len(keep)} regions split into {len(keep) + len(new)} ({len(new)} new, ids {max(regions) + 1}..{next_id - 1})")
    if not write:
        return

    # region files
    for rid, ps in keep.items():
        f, t, _ = regions[rid]
        t2 = re.sub(r"(provinces\s*=\s*\{)[^}]*(\})", lambda m: f"{m.group(1)}\r\n\t\t{' '.join(map(str, sorted(ps)))} \r\n\t{m.group(2)}", t, count=1)
        open(f, "wb").write(t2.encode("utf-8", "surrogateescape"))
    for parent, nid, ps, d in new:
        f, t, _ = regions[parent]
        t2 = re.sub(r"(provinces\s*=\s*\{)[^}]*(\})", lambda m: f"{m.group(1)}\r\n\t\t{' '.join(map(str, sorted(ps)))} \r\n\t{m.group(2)}", t, count=1)
        t2 = re.sub(r"\bid\s*=\s*\d+", f"id = {nid}", t2, count=1)
        t2 = re.sub(r'name\s*=\s*"[^"]*"', f'name = "STRATEGICREGION_{nid}"', t2, count=1)
        fname = re.sub(r'[\\/:*?"<>|]', "", f"{nid}-{names.get(parent, 'Region')} {DIRS['english'][0][d]}")
        open(f"map/strategicregions/{fname}.txt", "wb").write(t2.encode("utf-8", "surrogateescape"))

    # weather positions: every point goes to the region its pixel is in now; a region without one gets one
    region_of = {p: r for r, (_, _, ps) in regions.items() for p in ps}
    for rid, ps in keep.items():
        for p in ps:
            region_of[p] = rid
    for parent, nid, ps, _ in new:
        for p in ps:
            region_of[p] = nid
    family = {r: r for r in keep}
    family.update({nid: parent for parent, nid, _, _ in new})
    hm = np.asarray(Image.open("map/heightmap.bmp"))
    lines = [l for l in open("map/weatherpositions.txt", encoding="utf-8").read().splitlines() if l.strip()]
    out, have = [], set()
    for l in lines:
        q = l.split(";")
        x, z = float(q[1]), float(q[3])
        r = region_of.get(int(ids[min(H - 1, max(0, H - 1 - int(z))), int(x) % W]))
        if family.get(r) == int(q[0]):  # a point of a split region moves to the piece it stands in
            q[0] = str(r)
        have.add(int(q[0])); out.append(";".join(q))
    for parent, nid, ps, _ in [(r, r, keep[r], 0) for r in keep] + new:
        if nid in have:
            continue
        big = max(ps, key=lambda p: w[p])
        yy, xx = np.nonzero(ids == big)
        i = np.argmin((xx - cx[big]) ** 2 + (yy - cy[big]) ** 2)
        out.append(f"{nid};{xx[i] + .5:.2f};{max(hm[yy[i], xx[i]] / 10, 9.5):.2f};{H - yy[i] - .5:.2f};small")
        have.add(nid)
    out.sort(key=lambda l: int(l.split(";")[0]))
    open("map/weatherpositions.txt", "w", encoding="utf-8", newline="\n").write("\n".join(out) + "\n")

    # AI areas: a new piece joins every area its parent is in
    p = "common/ai_areas/default.txt"
    t = open(p, encoding="utf-8").read()
    for parent, nid, _, _ in new:
        t = re.sub(rf"(strategic_regions\s*=\s*\{{[^}}]*?)(\b{parent}\b)", rf"\g<1>\g<2> {nid}", t)
    open(p, "w", encoding="utf-8", newline="").write(t)

    for lang, (compass, pat) in DIRS.items():
        rows, used = [f"l_{lang}:"], {}
        for parent, nid, _, d in new:
            base = loc_names[lang].get(parent) or names.get(parent, f"Region {parent}")
            key = (parent, d)
            used[key] = used.get(key, 0) + 1
            label = compass[d] + (f" {used[key]}" if used[key] > 1 else "")  # same direction twice: numbered
            rows.append(f' STRATEGICREGION_{nid}:0 "{pat.format(n=base, d=label)}"')
        open(f"localisation/{lang}/cwic_climate_regions_l_{lang}.yml", "w", encoding="utf-8-sig", newline="\r\n").write("\n".join(rows) + "\n")
    print("written")


if __name__ == "__main__":
    main(sys.argv[1], "--write" in sys.argv[2:])
