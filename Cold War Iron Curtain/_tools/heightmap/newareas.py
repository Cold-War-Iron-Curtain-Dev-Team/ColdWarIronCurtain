"""Second step of the reprojection (after reproject.py): give every pixel a real province again.

Run from the mod root:  python _tools/heightmap/newareas.py <etopo.nc> <newarea.npy>
1. Seam: provinces cut by the new east-west seam (x = 0) keep their bigger part; a cut-off part of SPLIT_MIN px or more
   becomes a new province in the same state / strategic region, smaller ones join the neighbour they touch most.
2. New area (pixels the old map never showed): land/sea from ETOPO. Strips next to existing provinces of the same kind
   extend them (GROW px, or entirely for small pieces); the rest is cut into new provinces (geodesic Voronoi).
   Antarctica = impassable wasteland states by 1940s claim sector; new Arctic islands = wasteland states of the 1949
   owner; new seas = new strategic regions by sector.
3. Himalaya/Pamir: the impassable states stay (Kashmir scripts transfer them) but lose impassable = yes; every border
   of their provinces becomes an impassable adjacency instead, so the map shows no hatching.
Writes map/provinces.bmp, definition.csv, continent.txt, adjacencies.csv, unitstacks.txt, weatherpositions.txt,
history/states/*, map/strategicregions/*, localisation/*/cwic_new_map_areas_l_*.yml.
"""
import glob, os, re, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
import proj
from build import load_dem, sampler

NEW_KEY = (1 << 16) | (2 << 8) | 3
SPLIT_MIN = 300
GROW = 24
FULL_GROW = 120
SMALL = {"sea": 3000, "land": 800}
SPACING = {"sea": 110, "land": 80}
SPECK = 40  # land/sea specks below this take the other kind
HIMALAYA_STATES = [1332, 1333] + list(range(1337, 1347))
LANGS = ["english", "french", "japanese", "russian"]
rng = np.random.default_rng(1949)

# (lon from, lon to, name, owner, cores) -- Antarctic claims as of the late 1940s; Marie Byrd Land was unclaimed
ANT_STATES = [(-80, -53, "Graham Land", "ENG", ["ENG", "ARG", "CHL"]), (-53, -20, "Coats Land", "ENG", ["ENG", "ARG"]),
              (-20, 45, "Queen Maud Land", "NOR", ["NOR"]), (45, 90, "Enderby Land", "AST", ["AST"]),
              (90, 136, "Wilkes Land", "AST", ["AST"]), (136, 142, "Adelie Land", "FRA", ["FRA"]),
              (142, 160, "George V Land", "AST", ["AST"]), (160, 210, "Ross Dependency", "NZL", ["NZL"]),
              (-150, -90, "Marie Byrd Land", "USA", ["USA"]), (-90, -80, "Ellsworth Land", "CHL", ["CHL"])]
ANT_REGIONS = [(-150, -20, "West Antarctica"), (-20, 45, "Queen Maud Land"), (45, 136, "East Antarctica"),
               (136, 210, "Victoria Land")]
SOUTH_SEAS = [(-70, -20, "Weddell Sea"), (-20, 30, "Queen Maud Sea"), (30, 75, "Enderby Sea"), (75, 110, "Davis Sea"),
              (110, 150, "D'Urville Sea"), (150, 200, "Ross Sea"), (-160, -110, "Amundsen Sea"),
              (-110, -70, "Bellingshausen Sea")]
ARCTIC_SEAS = [(-169, -100, "Arctic Ocean (Beaufort)"), (-100, -30, "Arctic Ocean (Lincoln)"),
               (-30, 60, "Arctic Ocean (Barents)"), (60, 191, "Arctic Ocean (Siberian)")]
ARCTIC_LAND = [(-141, -73, "Queen Elizabeth Islands", "CAN", 2), (-73, -10, "Peary Land", "DEN", 2),
               (-10, 35, "Northern Svalbard", "NOR", 1), (35, 75, "Franz Josef Land", "SOV", 6),
               (75, 125, "Severnaya Zemlya", "SOV", 6), (125, 191, "New Siberian Islands", "SOV", 6),
               (-169, -141, "Wrangel Island", "SOV", 6)]


def in_sector(lon, a, b):
    return ((lon - a) % 360) < ((b - a) % 360 or 360)


def sector(lon, table):
    for row in table:
        if in_sector(lon, row[0], row[1]):
            return row
    return table[-1]


# ---------- file helpers (CRLF kept) ----------
def read(path):
    b = open(path, "rb").read()
    bom = b.startswith(b"\xef\xbb\xbf")
    t = b.decode("utf-8-sig", "surrogateescape")
    return t.replace("\r\n", "\n"), ("\r\n" if b"\r\n" in b else "\n"), bom


def write(path, text, nl="\r\n", bom=False):
    data = text.replace("\n", nl).encode("utf-8", "surrogateescape")
    open(path, "wb").write((b"\xef\xbb\xbf" if bom else b"") + data)


def keys_of(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def wrap_neighbours(lab):
    """pairs of differing labels across 4-neighbour edges (east-west wraps)."""
    out = set()
    for a, b in ((lab, np.roll(lab, -1, 1)), (lab[:-1], lab[1:])):
        m = a != b
        out |= set(zip(a[m].tolist(), b[m].tolist()))
    return out


def grow(lab, mask, steps=None):
    """geodesic growth: unlabelled (0) pixels in mask take a labelled 4-neighbour's label, up to steps rounds."""
    lab = lab.copy()
    n = 0
    while steps is None or n < steps:
        free = (lab == 0) & mask
        if not free.any():
            break
        cand = np.zeros_like(lab)
        for sh in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            r = np.roll(lab, sh, (0, 1))
            if sh[0] == 1:
                r[0] = 0
            if sh[0] == -1:
                r[-1] = 0
            if sh[1] == 1:  # never across the east-west seam: no province may straddle it
                r[:, 0] = 0
            if sh[1] == -1:
                r[:, -1] = 0
            cand = np.where((cand == 0) & (r > 0), r, cand)
        take = free & (cand > 0)
        if not take.any():
            break
        lab[take] = cand[take]
        n += 1
    return lab


def interior_point(mask):
    d = nd.distance_transform_edt(np.pad(mask, 1))[1:-1, 1:-1]
    y, x = np.unravel_index(np.argmax(d), d.shape)
    return x + .5, y + .5


REF_RE = r"(?:\b[a-z_]*state[a-z_]*\s*=\s*{sid}\b|^\s*{sid}\s*=\s*\{{)"
SCRIPT_DIRS = ["common", "events", "history/countries", "history/units"]


def script_files():
    for d in SCRIPT_DIRS:
        for f in glob.glob(f"{d}/**/*.txt", recursive=True):
            yield f


def script_refs(sids):
    """state id -> other state ids referenced within 15 lines of it in scripts (what it is transferred together with)."""
    out = {}
    any_state = re.compile(r"\b[a-z_]*state[a-z_]*\s*=\s*(\d+)\b|^\s*(\d+)\s*=\s*\{", re.M)
    for f in script_files():
        t = read(f)[0]
        if not any(str(s) in t for s in sids):
            continue
        lines = t.split("\n")
        for i, l in enumerate(lines):
            for s in sids:
                if re.search(REF_RE.format(sid=s), l):
                    win = "\n".join(lines[max(0, i - 15):i + 16])
                    out.setdefault(s, set()).update(int(a or b) for a, b in any_state.findall(win))
    return out


def rewrite_script_refs(merge_into):
    """reference to a removed state -> its merge target when that target is referenced nearby (same block); else the
    line goes (it would otherwise hit the Antarctic state that reuses the id). Returns a log."""
    log = []
    for f in script_files():
        t, nl, bom = read(f)
        if not any(str(s) in t for s in merge_into):
            continue
        lines = t.split("\n")
        changed = False
        for i in range(len(lines)):
            for s, tgt in merge_into.items():
                rx = re.compile(REF_RE.format(sid=s))
                if not rx.search(lines[i]):
                    continue
                win = "\n".join(lines[max(0, i - 15):i + 16])
                block = re.match(r"^\s*\d+\s*=\s*\{", lines[i])
                if re.search(rf"\b{tgt}\b", win) or block:
                    lines[i] = re.sub(rf"\b{s}\b", str(tgt), lines[i])
                    log.append(f"{f}:{i + 1}: {s} -> {tgt}")
                else:
                    log.append(f"{f}:{i + 1}: removed '{lines[i].strip()}'")
                    lines[i] = None
                changed = True
                break
            if lines[i] is None:
                continue
        if changed:
            write(f, "\n".join(l for l in lines if l is not None), nl, bom)
    return log


def main(dem_path, newarea_npy):
    rgb = np.array(Image.open("map/provinces.bmp").convert("RGB"))
    K = keys_of(rgb)
    H, W = K.shape
    assert (W, H) == (proj.W, proj.H)

    deftxt, _, _ = read("map/definition.csv")
    defs, key2id = {}, {}
    for l in deftxt.split("\n"):
        p = l.split(";")
        if len(p) >= 8 and p[0].isdigit():
            defs[int(p[0])] = p
            key2id[(int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])] = int(p[0])
    used_keys = set(key2id)
    max_old = max(defs)

    # id image (0 = unassigned)
    uk, inv = np.unique(K, return_inverse=True)
    P = np.array([key2id.get(int(k), 0) for k in uk], np.int64)[inv.reshape(K.shape)]
    assert ((P == 0) == (K == NEW_KEY)).all(), "unknown colours in provinces.bmp"

    state_of, region_of, state_file, region_file = {}, {}, {}, {}
    for f in glob.glob("history/states/*.txt"):
        t = re.sub(r"#.*", "", read(f)[0])
        sid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        state_file[sid] = f
        for v in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split():
            state_of[int(v)] = sid
    for f in glob.glob("map/strategicregions/*.txt"):
        t = re.sub(r"#.*", "", read(f)[0])
        rid = int(re.search(r"\bid\s*=\s*(\d+)", t).group(1))
        region_file[rid] = f
        for v in re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split():
            region_of[int(v)] = rid

    kind_of = lambda i: defs[i][4] if i in defs else new_prov[i]["kind"]
    new_prov = {}  # temp id -> dict(kind, terrain, continent, parent); final ids are given at the end
    add_to_state, add_to_region = {}, {}
    TMP0 = 1_000_000
    next_id = TMP0

    def new_id(kind, terrain, continent, parent=None):
        nonlocal next_id
        i = next_id
        next_id += 1
        new_prov[i] = dict(kind=kind, terrain=terrain, continent=continent, parent=parent)
        return i

    # ---------- 0. Himalaya/Pamir states go; their land joins a neighbouring state ----------
    pairs_before = {tuple(sorted(p)) for p in wrap_neighbours(P)}
    refs = script_refs(HIMALAYA_STATES)
    freed_prov, gained, freed_region = [], set(), {}
    merge_into = {}
    for sid in HIMALAYA_STATES:
        provs = [p for p, s in state_of.items() if s == sid]
        contact = {}
        for a, b in pairs_before:
            for x, y in ((a, b), (b, a)):
                t = state_of.get(y)
                if x in provs and t and t != sid and t not in HIMALAYA_STATES:
                    contact[t] = contact.get(t, 0) + 1
        co = {t: c for t, c in contact.items() if t in refs.get(sid, set())}
        target = max(co or contact, key=lambda t: (co or contact)[t])
        merge_into[sid] = target
        area = np.isin(P, provs)
        ys, xs = np.nonzero(area)
        y0, y1, x0, x1 = max(0, ys.min() - 2), ys.max() + 3, max(0, xs.min() - 2), xs.max() + 3
        sub = P[y0:y1, x0:x1]
        tprovs = [p for p, s in state_of.items() if s == target]
        seed = np.where(np.isin(sub, tprovs), sub, 0)
        g = grow(seed, area[y0:y1, x0:x1] | (seed > 0))
        a = area[y0:y1, x0:x1]
        if not (g[a] > 0).all():  # a separate piece of the state: its own land neighbours take it
            other = np.isin(sub, [p for p, s in state_of.items() if s in HIMALAYA_STATES])
            landn = np.isin(sub, [i for i in defs if defs[i][4] == "land"]) & ~other
            g = grow(np.where(a, g, np.where(landn, sub, 0)), a | landn)
        assert (g[a] > 0).all(), f"state {sid}: target {target} does not reach all of it"
        gained |= set(np.unique(g[a]).tolist())
        sub[a] = g[a]
        for p in provs:
            freed_prov.append(p)
            del state_of[p]
            if p in region_of:
                freed_region[p] = region_of.pop(p)
            del defs[p]
        print(f"state {sid} -> merged into {target}")
    pairs_after = {tuple(sorted(p)) for p in wrap_neighbours(P)}
    him_pairs = sorted(p for p in pairs_after - pairs_before if p[0] in gained or p[1] in gained)
    freed_state = sorted(HIMALAYA_STATES)

    # ---------- 1. seam ----------
    # a province with parts on both sides of the seam (box wider than W/8): the parts on the far side from its main
    # body become one new province in the same state/region, or join a same-kind neighbour if they are a sliver
    split = merged = 0
    for pid, ob in enumerate(nd.find_objects(P), 1):
        if ob is None or ob[1].stop - ob[1].start <= W // 8 or pid not in defs:
            continue
        lab, n = nd.label(P == pid, structure=np.ones((3, 3)))
        sizes = np.bincount(lab.ravel())[1:]
        cx = nd.center_of_mass(np.ones_like(lab), lab, range(1, n + 1))
        main_l = int(np.argmax(sizes))
        far = [l + 1 for l in range(n) if abs(cx[l][1] - cx[main_l][1]) > W / 2]
        m = np.isin(lab, far)
        ring = nd.binary_dilation(m, np.ones((3, 3))) & ~m
        nb = P[ring]
        nb = nb[(nb != pid) & (nb > 0) & np.array([kind_of(int(x)) == defs[pid][4] for x in nb], bool)]
        if m.sum() >= SPLIT_MIN or not len(nb):  # big, or islands with no same-kind neighbour
            d = defs[pid]
            P[m] = new_id(d[4], d[6], d[7], parent=pid)
            split += 1
        else:
            v, c = np.unique(nb, return_counts=True)
            P[m] = v[np.argmax(c)]
            merged += 1
    print(f"seam: {split} parts became provinces, {merged} slivers merged")

    # ---------- 2. new area ----------
    new = np.load(newarea_npy) & (P == 0)
    lon, lat = proj.grid()
    dlat, dlon, z, ocean = load_dem(dem_path)
    rc = sampler(dlat, dlon)
    land = nd.map_coordinates(ocean.astype(np.float32), rc(lon, lat), order=0, mode="wrap") < .5
    del z
    for kind_mask in (land, ~land):  # specks take the other kind
        lab, n = nd.label(kind_mask & new)
        if n:
            s = np.bincount(lab.ravel())
            small = (s < SPECK)
            small[0] = False
            land ^= small[lab] & new
    for kind, km in (("land", land & new), ("sea", ~land & new)):
        of_kind = [i for i in set(defs) | set(new_prov) if kind_of(i) == kind]
        seedlab = np.where(np.isin(P, of_kind), P, 0)
        g = grow(seedlab, km | (seedlab > 0), GROW)
        # small leftovers that touch the grown area: grow all the way
        left = km & (g == 0)
        lab, n = nd.label(left)
        sizes = np.bincount(lab.ravel())
        small_ids = [l for l in range(1, n + 1) if sizes[l] < SMALL[kind]]
        if small_ids:
            sm = np.isin(lab, small_ids)
            g = grow(g, (g > 0) | sm, FULL_GROW)  # capped: a thin strip must not let one province run along it
        P = np.where(km & (g > 0), g, P)
        left = km & (P == 0)
        lab, n = nd.label(left)
        sizes = np.bincount(lab.ravel())
        # big or isolated pieces: geodesic Voronoi from jittered seeds
        S = SPACING[kind]
        seeds = np.zeros_like(P)
        cell_ids = []
        objs = nd.find_objects(lab)
        for l, ob in enumerate(objs, 1):
            m = lab[ob] == l
            ys, xs = np.nonzero(m)
            if sizes[l] < S * S * 0.6:
                pts = [(ys[len(ys) // 2], xs[len(xs) // 2])]
            else:
                pts = []
                y0, x0 = ob[0].start, ob[1].start
                for gy in range(0, m.shape[0], S):
                    for gx in range(0, m.shape[1], S):
                        jy = gy + rng.integers(S // 4, 3 * S // 4)
                        jx = gx + rng.integers(S // 4, 3 * S // 4)
                        if jy < m.shape[0] and jx < m.shape[1] and m[jy, jx]:
                            pts.append((jy, jx))
                if not pts:
                    pts = [(ys[len(ys) // 2], xs[len(xs) // 2])]
            for (yy, xx) in pts:
                y, x = yy + ob[0].start, xx + ob[1].start
                terrain = "ocean" if kind == "sea" else ("mountain" if lat[y, x] < 0 else "hills")
                cont = "0" if kind == "sea" else ("8" if lat[y, x] < 0 else str(sector(lon[y, x], ARCTIC_LAND)[4]))
                nid = new_id(kind, terrain, cont)
                seeds[y, x] = nid
                cell_ids.append(nid)
        cells = grow(seeds, left)
        P = np.where(left, cells, P)
        # cells that got cut off from their seed's piece (shouldn't happen with geodesic growth) are fine as they are
        print(f"new {kind}: {len(cell_ids)} provinces")
    assert (P > 0).all(), "unassigned pixels left"

    # drop new ids that ended up with no pixels
    present = np.bincount(P.ravel(), minlength=next_id + 1)
    for i in list(new_prov):
        if present[i] == 0:
            del new_prov[i]
    # ids must stay continuous: freed Himalaya ids first, then after the old last id
    assert len(new_prov) >= len(freed_prov)
    final = sorted(freed_prov) + list(range(max_old + 1, max_old + 1 + len(new_prov) - len(freed_prov)))
    remap = np.arange(next_id + 1)
    for n_, i in zip(final, sorted(new_prov)):
        remap[i] = n_
    new_prov = {int(remap[i]): p for i, p in new_prov.items()}
    P = remap[P]
    next_id = max(final) + 1

    # ---------- province facts ----------
    objs = nd.find_objects(P)
    info = {}
    for i in new_prov:
        ob = objs[i - 1]
        m = P[ob] == i
        x, y = interior_point(m)
        x, y = x + ob[1].start, y + ob[0].start
        info[i] = dict(x=x, y=y, lon=float(lon[int(y), int(x) % W]), lat=float(lat[int(y), int(x)]))
        bw, bh = ob[1].stop - ob[1].start, ob[0].stop - ob[0].start
        assert bw <= W // 8 and bh <= H // 8, f"province {i} box {bw}x{bh} too large"
    nb_pairs = wrap_neighbours(P)
    nbs = {}
    for a, b in nb_pairs:
        nbs.setdefault(a, set()).add(b)
        nbs.setdefault(b, set()).add(a)

    # ---------- grouping ----------
    new_states, new_regions = {}, {}  # name -> dict(...)
    state_pool = list(freed_state) + list(range(max(state_file) + 1, max(state_file) + 100))
    next_region = max(region_file) + 1

    def state_for(name, owner, cores, impassable):
        if name not in new_states:
            new_states[name] = dict(id=state_pool.pop(0), owner=owner, cores=cores, impassable=impassable, provs=[])
        return new_states[name]

    def region_for(name, kind):
        nonlocal next_region
        if name not in new_regions:
            new_regions[name] = dict(id=next_region, kind=kind, provs=[])
            next_region += 1
        return new_regions[name]

    def nearest_existing_region(i, kind):
        frontier, seen = {i}, {i}
        for _ in range(60):
            nxt = set()
            for a in frontier:
                for b in nbs.get(a, ()):
                    if b in seen:
                        continue
                    seen.add(b)
                    if b in region_of and kind_of(b) == kind:
                        return region_of[b]
                    nxt.add(b)
            frontier = nxt
        return None

    for i, p in new_prov.items():
        f = info[i]
        if p["parent"]:
            par = p["parent"]
            if par in state_of:
                add_to_state.setdefault(state_of[par], []).append(i)
            if par in region_of:
                add_to_region.setdefault(region_of[par], []).append(i)
            continue
        if p["kind"] == "sea":
            name = sector(f["lon"], SOUTH_SEAS)[2] if f["lat"] < 0 else sector(f["lon"], ARCTIC_SEAS)[2]
            region_for(name, "sea")["provs"].append(i)
        elif f["lat"] < 0:
            a, b, name, owner, cores = sector(f["lon"], ANT_STATES)
            state_for(name, owner, cores, True)["provs"].append(i)
            region_for(sector(f["lon"], ANT_REGIONS)[2], "land")["provs"].append(i)
        else:
            a, b, name, owner, cont = sector(f["lon"], ARCTIC_LAND)
            state_for(name, owner, [owner], False)["provs"].append(i)
            r = nearest_existing_region(i, "land")
            if r is None:
                region_for("Arctic Islands", "land")["provs"].append(i)
            else:
                add_to_region.setdefault(r, []).append(i)

    # ---------- write: provinces.bmp + definition.csv ----------
    colors = {}
    for i in sorted(new_prov):
        while True:
            c = tuple(int(v) for v in rng.integers(1, 255, 3))
            k = (c[0] << 16) | (c[1] << 8) | c[2]
            if k not in used_keys and k != NEW_KEY:
                used_keys.add(k)
                colors[i] = c
                break
    lutr = np.zeros((next_id + 1, 3), np.uint8)
    for k, i in key2id.items():
        lutr[i] = ((k >> 16) & 255, (k >> 8) & 255, k & 255)
    for i, c in colors.items():
        lutr[i] = c
    Image.fromarray(lutr[P], "RGB").save("map/provinces.bmp")

    rows = {i: ";".join(p) for i, p in defs.items()}
    for i in sorted(new_prov):
        p = new_prov[i]
        other = "sea" if p["kind"] == "land" else "land"
        coastal = "true" if any(kind_of(n) == other for n in nbs.get(i, ())) else "false"
        c = colors[i]
        rows[i] = f"{i};{c[0]};{c[1]};{c[2]};{p['kind']};{coastal};{p['terrain']};{p['continent']}"
    assert sorted(rows) == list(range(len(rows))), "province ids not continuous"
    t, nl, bom = read("map/definition.csv")
    write("map/definition.csv", "\n".join(rows[i] for i in sorted(rows)) + "\n", "\r\n", bom)
    print(f"definition.csv: {len(new_prov)} new provinces ({len(freed_prov)} reuse Himalaya ids), last id {max(rows)}")

    t, nl, bom = read("map/continent.txt")
    if "antarctica" not in t:
        write("map/continent.txt", t.replace("\tmiddle_east\n", "\tmiddle_east\n\tantarctica\n"), nl, bom)

    # ---------- states ----------
    tpl = read("history/states/1670-Gronlands indlandsis.txt")[0]
    culture_of = {}
    for f in glob.glob("history/states/*.txt"):
        t = read(f)[0]
        m = re.search(r"owner\s*=\s*(\w+)", t)
        if m and m.group(1) not in culture_of:
            cl = re.findall(r"add_to_array\s*=\s*\{\s*culture\s*=\s*\d+\s*\}", t)
            if cl:
                culture_of[m.group(1)] = cl

    def state_text(sid, owner, cores, provs, impassable):
        t = tpl
        t = re.sub(r"\bid=1670", f"id={sid}", t)
        t = t.replace('"STATE_1670"', f'"STATE_{sid}"')
        vp = "\n".join(f"\t\tadd_to_array = {{ THIS.vp_provinces = {p} }} add_to_array = {{ THIS.vp_values = 0 }}" for p in provs)
        t = re.sub(r"(### MACHINE-GENERATED SECTION ###\n(?:\t\t#[^\n]*\n)*)(?:[^\n]*vp_provinces[^\n]*\n)+", lambda m: m.group(1) + vp + "\n", t)
        t = re.sub(r"owner = DEN", f"owner = {owner}", t)
        t = re.sub(r"(\t\tadd_core_of = \w+\n)+", "".join(f"\t\tadd_core_of = {c}\n" for c in cores), t, count=1)
        cl = culture_of.get(owner)
        if cl:
            t = re.sub(r"(add_to_array = \{ culture = \d+ \}[ \t]*\n\t*)+", "\n\t\t".join(cl) + "\n\t\t", t, count=1)
        if not impassable:
            t = t.replace("\timpassable = yes\n", "")
        t = re.sub(r"provinces=\{[^}]*\}", "provinces={\n\t\t" + " ".join(map(str, provs)) + " \n\t}", t)
        return t

    loc = {}
    assert len(new_states) >= len(freed_state), "fewer new states than freed ids: state ids would have a gap"
    for sid in freed_state:
        os.remove(state_file[sid])
    for name, s in new_states.items():
        fn = f"history/states/{s['id']}-{name}.txt"
        write(fn, state_text(s["id"], s["owner"], s["cores"], s["provs"], s["impassable"]))
        loc[f"STATE_{s['id']}"] = name
    for sid, add in add_to_state.items():
        f = state_file[sid]
        t, nl, bom = read(f)
        t = re.sub(r"(provinces\s*=\s*\{)([^}]*)\}", lambda m: m.group(1) + m.group(2).rstrip() + " " + " ".join(map(str, add)) + " \n\t}", t, count=1)
        write(f, t, nl, bom)
    print(f"states: {len(new_states)} new, {len(add_to_state)} extended")

    # ---------- strategic regions ----------
    def weather_from(rid):
        t = read(region_file[rid])[0]
        return t[t.index("\tweather"):t.rindex("}")]

    south_tpl = next(r for r, f in region_file.items() if "Super Southern" in f)
    arctic_tpl = next((r for r, f in region_file.items() if re.search(r"Arctic|Barents|Kara", f)), south_tpl)
    land_tpl = next(r for r, f in region_file.items() if "Greenland" in f or "Gronland" in f) if any(
        "Greenland" in f or "Gronland" in f for f in region_file.values()) else arctic_tpl
    for name, r in new_regions.items():
        lat0 = np.mean([info[i]["lat"] for i in r["provs"]])
        tplr = (south_tpl if lat0 < 0 else arctic_tpl) if r["kind"] == "sea" else land_tpl
        body = (f"strategic_region = {{\n\tid = {r['id']}\n\tname = \"STRATEGICREGION_{r['id']}\"\n\n"
                + ("\tnaval_terrain = water_deep_ocean\n" if r["kind"] == "sea" else "")
                + "\tprovinces = {\n\t\t" + " ".join(map(str, r["provs"])) + " \n\t}\n\n"
                + weather_from(tplr) + "}\n")
        write(f"map/strategicregions/{r['id']}-{name}.txt", body)
        loc[f"STRATEGICREGION_{r['id']}"] = name
    for p, rid in freed_region.items():
        f = region_file[rid]
        t, nl, bom = read(f)
        t = re.sub(r"(provinces\s*=\s*\{[^}]*)\}", lambda m: re.sub(rf"(?<![\d#]){p}\b ?", "", m.group(1)) + "}", t, count=1)
        write(f, t, nl, bom)
    for rid, add in add_to_region.items():
        f = region_file[rid]
        t, nl, bom = read(f)
        t = re.sub(r"(provinces\s*=\s*\{)([^}]*)\}", lambda m: m.group(1) + m.group(2).rstrip() + " " + " ".join(map(str, add)) + " \n\t}", t, count=1)
        write(f, t, nl, bom)
    print(f"strategic regions: {len(new_regions)} new, {len(add_to_region)} extended")

    # ---------- weather positions / unit stacks ----------
    t, nl, bom = read("map/weatherpositions.txt")
    extra = []
    for name, r in new_regions.items():
        ps = r["provs"]
        for j, kind in ((0, "big"), (len(ps) // 2, "small")):
            f = info[ps[j]]
            extra.append(f"{r['id']};{f['x']:.2f};9.50;{H - f['y']:.2f};{kind}")
    write("map/weatherpositions.txt", t.rstrip("\n") + "\n" + "\n".join(extra) + "\n", nl, bom)

    t, nl, bom = read("map/unitstacks.txt")
    fp = {str(p) for p in freed_prov}
    t = "\n".join(l for l in t.split("\n") if l.split(";")[0] not in fp)
    types = {"sea": [], "land": []}
    for l in t.split("\n"):
        p = l.split(";")
        if len(p) > 2 and p[0] == "4":
            types["sea"].append(p[1])
        if len(p) > 2 and p[0] == "2" and p[1] not in types["land"]:
            types["land"].append(p[1])
    extra = []
    for i, p in new_prov.items():
        f = info[i]
        for ty in types[p["kind"]]:
            extra.append(f"{i};{ty};{f['x']:.2f};9.50;{H - f['y']:.2f};0.00;0.00")
    write("map/unitstacks.txt", t.rstrip("\n") + "\n" + "\n".join(extra) + "\n", nl, bom)

    # ---------- Himalaya: borders that the removed states used to separate become impassable ----------
    t, nl, bom = read("map/adjacencies.csv")
    lines = [l for l in t.split("\n") if not (l.split(";")[0] in fp or (len(l.split(";")) > 1 and l.split(";")[1] in fp))]
    have = {tuple(sorted((int(p[0]), int(p[1])))) for p in (l.split(";") for l in lines) if len(p) > 2 and p[0].isdigit() and p[2] == "impassable"}
    rows_adj = [f"{a};{b};impassable;-1;-1;-1;-1;-1;;Himalaya" for a, b in him_pairs if (a, b) not in have]
    term = max(i for i, l in enumerate(lines) if l.startswith("-1;"))
    lines[term:term] = rows_adj
    write("map/adjacencies.csv", "\n".join(lines), nl, bom)
    t, nl, bom = read("map/buildings.txt")
    fs = {str(x) for x in freed_state}
    write("map/buildings.txt", "\n".join(l for l in t.split("\n") if l.split(";")[0] not in fs), nl, bom)
    for line in rewrite_script_refs(merge_into):
        print("  script:", line)
    print(f"himalaya: {len(freed_prov)} provinces merged away, {len(rows_adj)} impassable adjacencies, states {freed_state} reused")

    # ---------- localisation ----------
    loc["antarctica"] = "Antarctica"
    for lang in LANGS:  # keys that already exist (the reused STATE_ ids) are rewritten where they are
        rest = dict(loc)
        for f in glob.glob(f"localisation/{lang}/**/*.yml", recursive=True):
            if "cwic_new_map_areas" in f:
                continue
            t, nl, bom = read(f)
            hit = False
            for k in list(rest):
                rx = rf'^(\s*{re.escape(k)}:\d*\s*)"[^"\n]*"'
                if re.search(rx, t, re.M):
                    t = re.sub(rx, lambda m, v=rest[k]: f'{m.group(1)}"{v}"', t, flags=re.M)
                    del rest[k]
                    hit = True
            if hit:
                write(f, t, nl, bom)
        body = f"l_{lang}:\n" + "".join(f' {k}:0 "{v}"\n' for k, v in rest.items())
        write(f"localisation/{lang}/cwic_new_map_areas_l_{lang}.yml", body, "\r\n", True)


if __name__ == "__main__":
    main(*sys.argv[1:3])
