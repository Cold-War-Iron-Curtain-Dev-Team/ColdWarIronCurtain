"""Engine-validity pass over the province map after reprojection / new areas (fixes what error.log reports).

Run from the mod root:  python _tools/heightmap/mapfix.py
- provinces.bmp: one-pixel specks, 'X crossings' (2x2 diagonal checkerboards) and pieces under 3 px fold into a neighbour
  (a province is never removed: its last piece grows instead)
- provinces.bmp: no four provinces meeting at one corner; no land province touching sea only at a corner
- definition.csv: coastal flag recomputed from the bitmap (land touching sea / sea touching land)
- strategicregions: a state's provinces all go to its main region; land never sits in a sea region; a sea region's
  pieces cut off from its main body join the sea region they touch most
- unitstacks.txt: positions wrapped across the east/west seam go back next to their province
"""
import glob, re, numpy as np
from PIL import Image
from scipy import ndimage as nd

P = "map/provinces.bmp"


def keys(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def to_rgb(k):
    return np.stack([(k >> 16) & 255, (k >> 8) & 255, k & 255], -1).astype(np.uint8)


def nbrs(k):
    """the four neighbours of every pixel (east/west wrap, north/south edge repeats)."""
    up = np.vstack([k[:1], k[:-1]]); dn = np.vstack([k[1:], k[-1:]])
    return up, dn, np.roll(k, 1, 1), np.roll(k, -1, 1)


def majority_neighbour(k, y, x):
    H, W = k.shape
    c = [k[yy, xx % W] for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)) if 0 <= yy < H and k[yy, xx % W] != k[y, x]]
    return max(set(c), key=c.count) if c else k[y, x]


def clean(k):
    H, W = k.shape
    for it in range(30):
        n = 0
        # X crossings: A B / B A  -> recolour the bottom-right pixel to B
        A, B, C, D = k[:-1, :-1], k[:-1, 1:], k[1:, :-1], k[1:, 1:]
        ys, xs = np.nonzero((A == D) & (B == C) & (A != B))
        for y, x in zip(ys, xs):
            if k[y, x] == k[y + 1, x + 1] and k[y, x + 1] == k[y + 1, x] and k[y, x] != k[y, x + 1]:
                k[y + 1, x + 1] = k[y, x + 1]; n += 1
        # small 4-connected pieces (< 3 px) that are not their province's largest piece; lone specks of any province
        total = dict(zip(*np.unique(k, return_counts=True)))
        same = np.zeros(k.shape, bool)
        for nb in nbrs(k):
            same |= nb == k
        for y, x in zip(*np.nonzero(~same)):
            if total.get(k[y, x], 0) > 1:
                v = majority_neighbour(k, y, x); total[k[y, x]] -= 1; k[y, x] = v; n += 1
        # four provinces meeting at one corner (the engine's "invalid X crossing"), across the seam too: the pixel of
        # the biggest of the four takes its vertical neighbour's colour
        kw = np.concatenate([k, k[:, :1]], 1)
        A, B, C, D = kw[:-1, :-1], kw[:-1, 1:], kw[1:, :-1], kw[1:, 1:]
        ys, xs = np.nonzero((A != B) & (A != C) & (A != D) & (B != C) & (B != D) & (C != D))
        for y, x in zip(ys, xs):
            x1 = (x + 1) % W  # vertical partner: never copies a colour across the seam
            cells = [(y, x, (y + 1, x)), (y, x1, (y + 1, x1)), (y + 1, x, (y, x)), (y + 1, x1, (y, x1))]
            if len({k[a, b] for a, b, _ in cells}) < 4:
                continue
            a, b, (c, d) = max(cells, key=lambda t: total.get(k[t[0], t[1]], 0))
            total[k[a, b]] -= 1; k[a, b] = k[c, d]; n += 1
        # pieces under 3 px: fold extra pieces, grow a province whose only piece is that small
        from skimage.measure import label
        lab = label(k + 1, connectivity=1, background=0)
        sizes = np.bincount(lab.ravel())
        small = 0
        for l in np.flatnonzero(sizes[1:] < 3) + 1:
            ys, xs = np.nonzero(lab == l) if sizes[l] else ((), ())
            if not len(ys):
                continue
            key = k[ys[0], xs[0]]
            if (k == key).sum() > sizes[l]:  # another piece exists: fold this one
                for y, x in zip(ys, xs):
                    k[y, x] = majority_neighbour(k, y, x); small += 1
            else:  # its only piece: grow into the 3x3, never taking from a small province
                for y, x in [(ys[0] + dy, xs[0] + dx) for dy in (0, 1, -1) for dx in (0, 1, -1)]:
                    if 0 <= y < H and k[y, x % W] != key and (k == k[y, x % W]).sum() > 8:
                        k[y, x % W] = key; small += 1
        n += small
        print(f"  pass {it}: {n} pixels changed")
        if not n:
            break
    return k


def adjacency(ids):
    pairs = np.concatenate([np.c_[ids[:, :].ravel(), np.roll(ids, -1, 1).ravel()],
                            np.c_[ids[:-1].ravel(), ids[1:].ravel()]])
    pairs = pairs[pairs[:, 0] != pairs[:, 1]]
    pairs = np.sort(pairs, 1)
    u, c = np.unique(pairs, axis=0, return_counts=True)
    nb = {}
    for (p, q), n in zip(u, c):
        nb.setdefault(int(p), {})[int(q)] = int(n); nb.setdefault(int(q), {})[int(p)] = int(n)
    return nb


def main():
    print("provinces.bmp")
    im = Image.open(P)
    k = clean(keys(np.asarray(im.convert("RGB"))))
    Image.fromarray(to_rgb(k), "RGB").save(P)

    lines = open("map/definition.csv", "rb").read().decode("latin-1").split("\r\n")
    lut, kind, row = {}, {}, {}
    for i, l in enumerate(lines):
        p = l.split(";")
        if len(p) > 5 and p[0].isdigit() and p[0] != "0":
            lut[(int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])] = int(p[0]); kind[int(p[0])] = p[4]; row[int(p[0])] = i
    uk, inv = np.unique(k, return_inverse=True)
    ids = np.array([lut[int(v)] for v in uk])[inv].reshape(k.shape)
    H, W = ids.shape
    # the engine calls a land province coastal when it touches sea even at a corner; a corner-only contact gives it
    # no shore for a port, so that corner sea pixel joins the land beside it
    fixed = 0
    for _ in range(10):
        sea = np.isin(ids, [q for q, v in kind.items() if v == "sea"])
        land = np.isin(ids, [q for q, v in kind.items() if v == "land"])
        sh = lambda a, dy, dx: np.roll(np.roll(a, -dy, 0), -dx, 1)
        c4 = set(np.unique(ids[land & (sh(sea, 1, 0) | sh(sea, -1, 0) | sh(sea, 0, 1) | sh(sea, 0, -1))]))
        bad = []
        for dy, dx in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
            m = land & sh(sea, dy, dx) & ~np.isin(ids, list(c4))
            m[[0, -1]] = False
            bad += [(y + dy, (x + dx) % W, y, (x + dx) % W) for y, x in zip(*np.nonzero(m))]
        if not bad:
            break
        for sy, sx, ly, lx in bad:
            ids[sy, sx] = ids[ly, lx]; k[sy, sx] = k[ly, lx]; fixed += 1
    print("corner-only sea contacts filled:", fixed)
    Image.fromarray(to_rgb(k), "RGB").save(P)
    nb = adjacency(ids)

    # a sea pocket with no sea neighbour cuts its naval region in two: make it a lake
    lakes = 0
    for pid, i in row.items():
        if kind[pid] == "sea" and not any(kind.get(q) == "sea" for q in nb.get(pid, {})):
            p = lines[i].split(";")
            p[4], p[5], p[6], p[7] = "lake", "false", "lakes", "0"
            lines[i] = ";".join(p); kind[pid] = "lake"; lakes += 1
    print("enclosed sea provinces made lakes:", lakes)

    changed = 0
    for pid, i in row.items():
        p = lines[i].split(";")
        other = "sea" if kind[pid] == "land" else "land" if kind[pid] == "sea" else None
        if other is None:
            continue
        c = "true" if any(kind.get(q) == other for q in nb.get(pid, {})) else "false"
        if p[5] != c:
            p[5] = c; lines[i] = ";".join(p); changed += 1
    open("map/definition.csv", "wb").write("\r\n".join(lines).encode("latin-1"))
    print("definition.csv coastal flags changed:", changed)

    # ---- strategic regions
    region_of, files = {}, {}
    for f in glob.glob("map/strategicregions/*.txt"):
        t = open(f, "rb").read().decode("utf-8", "surrogateescape")
        rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        files[rid] = f
        for v in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split():
            region_of[int(v)] = rid
    size = dict(zip(*np.unique(ids, return_counts=True)))
    members = lambda r: [p for p, q in region_of.items() if q == r]
    is_sea_region = {r: sum(kind.get(p) == "sea" for p in members(r)) * 2 > len(members(r)) for r in files}
    moved = 0
    # only the reprojection's new provinces: climsplit.py splits regions across states on purpose
    from border_owner import new_provinces; fresh = new_provinces()
    for f in glob.glob("history/states/*.txt"):
        t = re.sub(r"#[^\n]*", "", open(f, encoding="utf-8", errors="ignore").read())
        pr = re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
        if not pr:
            continue
        ps = [int(v) for v in pr.group(1).split() if v.isdigit()]
        w = {}
        for p in ps:
            if p in region_of and not is_sea_region[region_of[p]]:
                w[region_of[p]] = w.get(region_of[p], 0) + size.get(p, 0)
        if not w:
            continue
        main_r = max(w, key=w.get)
        for p in ps:
            if p in fresh and region_of.get(p) != main_r:
                region_of[p] = main_r; moved += 1
    print("provinces moved to their state's region:", moved)
    # a land region holding a few sea provinces counts as naval for the engine, which then wants it in one piece
    # (adjacencies.csv crossings count): if it is not, its sea provinces go to the sea region they touch most
    links = {}
    for l in open("map/adjacencies.csv", encoding="utf-8", errors="ignore"):
        q = l.split(";")
        if len(q) > 2 and q[0].isdigit() and q[1].isdigit() and q[2] != "impassable":
            links.setdefault(int(q[0]), set()).add(int(q[1])); links.setdefault(int(q[1]), set()).add(int(q[0]))
    for r in files:
        ms = set(members(r))
        seas = [p for p in ms if kind.get(p) == "sea"]
        if not seas or is_sea_region[r]:
            continue
        part, todo = set(), [next(iter(ms))]
        while todo:
            x = todo.pop()
            if x not in part:
                part.add(x); todo += [q for q in set(nb.get(x, {})) | links.get(x, set()) if q in ms and q not in part]
        if len(part) == len(ms):
            continue
        for p in seas:
            w = {region_of[q]: n for q, n in nb.get(p, {}).items() if kind.get(q) == "sea" and region_of.get(q, r) != r and is_sea_region[region_of[q]]}
            if w:
                region_of[p] = max(w, key=w.get); print("  sea", p, "out of split land region", r, "->", region_of[p])
    cut = 0
    for r in [r for r in files if is_sea_region[r]]:
        ms = set(members(r))
        seen, parts = set(), []
        for s in ms:
            if s in seen:
                continue
            part, todo = set(), [s]
            while todo:
                x = todo.pop()
                if x in part:
                    continue
                part.add(x); todo += [q for q in nb.get(x, {}) if q in ms and q not in part]
            seen |= part; parts.append(part)
        parts.sort(key=lambda s: -sum(size.get(p, 0) for p in s))
        for part in parts[1:]:
            w = {}
            for p in part:
                for q, n in nb.get(p, {}).items():
                    rq = region_of.get(q)
                    if rq not in (None, r) and is_sea_region.get(rq) and kind.get(q) == "sea":
                        w[rq] = w.get(rq, 0) + n
            if w:
                best = max(w, key=w.get)
                for p in part:
                    region_of[p] = best; cut += 1
    print("cut-off sea provinces moved:", cut)
    for p in [p for p in region_of if kind.get(p) == "lake" and is_sea_region[region_of[p]]]:
        land = {q: n for q, n in nb.get(p, {}).items() if kind.get(q) == "land" and q in region_of}
        if land:
            region_of[p] = region_of[max(land, key=land.get)]; print("  lake", p, "-> region", region_of[p])
    for r, f in files.items():
        t = open(f, "rb").read().decode("utf-8", "surrogateescape")
        ps = " ".join(str(p) for p in sorted(p for p, q in region_of.items() if q == r))
        assert ps, f"region {r} emptied"
        if set(ps.split()) == set(re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()):
            continue
        t2 = re.sub(r"(provinces\s*=\s*\{)[^}]*(\})", lambda m: f"{m.group(1)}\r\n\t\t{ps} \r\n\t{m.group(2)}" if "\r\n" in t
                    else f"{m.group(1)}\n\t\t{ps} \n\t{m.group(2)}", t, count=1)
        if t2 != t:
            open(f, "wb").write(t2.encode("utf-8", "surrogateescape"))

    # ---- unit stacks far from their province (seam wraps, seam-split provinces): to the province pixel nearest its centre
    H, W = ids.shape
    pl = list(row)
    xs = np.broadcast_to(np.arange(W) + .5, ids.shape)
    zs = np.broadcast_to((H - np.arange(H) - .5)[:, None], ids.shape)
    cx, cz = dict(zip(pl, nd.mean(xs, ids, pl))), dict(zip(pl, nd.mean(zs, ids, pl)))  # no province straddles the seam
    spot = {}
    raw = open("map/unitstacks.txt", "rb").read().decode("utf-8")
    out, fixed = [], 0
    for l in raw.split("\n"):
        p = l.split(";")
        if len(p) > 4 and p[0].isdigit() and int(p[0]) in cx:
            q = int(p[0])
            if np.hypot(float(p[2]) - cx[q], float(p[4]) - cz[q]) > max(40, 3 * np.sqrt(size[q])):
                if q not in spot:
                    yy, xx = np.nonzero(ids == q)
                    i = np.argmin((xx + .5 - cx[q]) ** 2 + (H - yy - .5 - cz[q]) ** 2)
                    spot[q] = (xx[i] + .5, H - yy[i] - .5)
                p[2], p[4] = f"{spot[q][0]:.2f}", f"{spot[q][1]:.2f}"; l = ";".join(p); fixed += 1
        out.append(l)
    open("map/unitstacks.txt", "wb").write("\n".join(out).encode("utf-8"))
    print(f"unit stacks put back in their province: {fixed} ({len(spot)} provinces)")


if __name__ == "__main__":
    main()
