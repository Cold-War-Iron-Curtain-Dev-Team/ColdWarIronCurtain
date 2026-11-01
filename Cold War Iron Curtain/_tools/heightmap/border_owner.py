"""Which land provinces does the mod give to a different country than the real one on 23 May 1949 (CShapes 2.0)?

Run from the mod root:  python _tools/heightmap/border_owner.py <data_dir> [--new] [--write]
--new: only provinces that are new since development-branch (the reprojection's Arctic, Antarctic and seam cells);
the rest of the map is the mod's deliberate 1949 setup (civil-war factions, occupation zones) and must not be "fixed".
data_dir holds cshapes/CShapes-2.0.geojson. Each real country maps to the mod tag owning most of its land (so colonies,
puppets and the mod's own tags line up). A province counts as wrong when >= 60% of it lies in one real country whose tag
is not its state's owner. With --write a wrong province moves to the nearest state of the right owner (adjacent first,
else the closest by distance, for islands); a state that is wrong as a whole changes owner instead (owner, controller
and cores). Run mapfix.py and positions.py afterwards (regions, ports, buildings).
"""
import glob, json, re, sys, numpy as np
from collections import Counter, defaultdict
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.spatial import cKDTree
import proj
from gcps import land_mask_and_ids
from mapfix import adjacency

DATE = (1949, 5, 23)
RES = 20      # real-border raster cells per degree
SHARE = 0.6   # a province is "in" a real country when this share of it is


def real_raster(S):
    feats = json.load(open(f"{S}/cshapes/CShapes-2.0.geojson", encoding="utf-8"))["features"]
    p = lambda f, k: (f["properties"][k + "year"], f["properties"][k + "month"], f["properties"][k + "day"])
    alive = [f for f in feats if p(f, "gws") <= DATE <= p(f, "gwe")]
    img = Image.new("I", (360 * RES, 180 * RES), 0)
    dr = ImageDraw.Draw(img)
    for i, f in enumerate(alive, 1):
        g = f["geometry"]
        for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
            ring = [((lo + 180) * RES, (90 - la) * RES) for lo, la in poly[0]]
            if len(ring) > 2:
                dr.polygon(ring, fill=i)
    return np.asarray(img, np.int32), {i: f["properties"]["cntry_name"] for i, f in enumerate(alive, 1)}


def load_states():
    files, st, owner = {}, {}, {}
    for f in glob.glob("history/states/*.txt"):
        t = open(f, encoding="utf-8", errors="ignore").read()
        m, pr = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"provinces\s*=\s*\{([^}]*)\}", re.sub(r"#[^\n]*", "", t))
        if not (m and pr):
            continue
        sid = int(m.group(1))
        files[sid] = f
        for q in pr.group(1).split():
            if q.isdigit():
                st[int(q)] = sid
        h = re.split(r"\n\s*\d{4}\.\d+\.\d+\s*=\s*\{", t[t.find("history"):])[0]  # the 1949 start, not dated blocks
        o = re.search(r"\bowner\s*=\s*([A-Z0-9]{3})", h)
        owner[sid] = o.group(1) if o else None
    return files, st, owner


def new_provinces(ref="development-branch"):
    import subprocess
    rows = lambda t: {l.split(";")[0]: l.split(";")[1:4] for l in t.splitlines() if l[:1].isdigit()}
    old = rows(subprocess.run(["git", "show", f"{ref}:./map/definition.csv"], capture_output=True, check=True).stdout.decode("latin-1"))
    new = rows(open("map/definition.csv", encoding="latin-1").read())
    return {int(k) for k, v in new.items() if old.get(k) != v}


def main(S, write=False, only_new=False):
    real_ll, names = real_raster(S)
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    lo, la = proj.grid()
    s = (slice(None, None, 2), slice(None, None, 2))
    pid = ids[s]
    real = real_ll[np.clip(((90 - la[s]) * RES).astype(int), 0, 180 * RES - 1), ((lo[s] + 180) % 360 * RES).astype(int) % (360 * RES)]
    del lo, la
    files, st, owner = load_states()
    land = np.isin(pid, [k for k, v in kinds.items() if v == "land"])

    # per province: pixel count per real country
    pr_real = defaultdict(Counter)
    for p, r in zip(pid[land].ravel(), real[land].ravel()):
        pr_real[int(p)][int(r)] += 1
    # real country -> mod tag owning most of its land
    vote = defaultdict(Counter)
    for p, c in pr_real.items():
        o = owner.get(st.get(p))
        for r, n in c.items():
            if r and o:
                vote[r][o] += n
    tag_of = {r: v.most_common(1)[0][0] for r, v in vote.items()}

    wrong = {}  # province -> right tag
    scope = new_provinces() if only_new else None
    for p, c in pr_real.items():
        if scope is not None and p not in scope:
            continue
        tot = sum(c.values())
        r, n = c.most_common(1)[0]
        o = owner.get(st.get(p))
        if r and n >= SHARE * tot and o and tag_of.get(r) and tag_of[r] != o:
            wrong[p] = tag_of[r]
    by_pair = Counter((owner[st[p]], t) for p, t in wrong.items())
    print(f"{len(wrong)} land provinces owned by another country than in 1949:")
    for (a, b), n in by_pair.most_common(40):
        ex = next(p for p, t in wrong.items() if t == b and owner[st[p]] == a)
        print(f"  {a} has {n:3d} of {b}'s   e.g. province {ex} in state {st[ex]} ({files[st[ex]].replace(chr(92), '/').split('/')[-1][:-4]})")
    if not write or not wrong:
        return

    # whole states: every land province of the state is wrong toward the same tag -> change the owner
    by_state = defaultdict(list)
    for p, sid in st.items():
        if kinds.get(p) == "land":
            by_state[sid].append(p)
    retag = {}
    for sid, ps in by_state.items():
        ts = {wrong.get(p) for p in ps}
        if len(ts) == 1 and None not in ts:
            retag[sid] = ts.pop()
    for sid, t in retag.items():
        f = files[sid]
        txt = open(f, "rb").read().decode("utf-8", "surrogateescape")
        old = owner[sid]
        txt = re.sub(rf"\b(owner|controller)(\s*=\s*){old}\b", rf"\g<1>\g<2>{t}", txt, count=2)
        txt = re.sub(rf"\badd_core_of(\s*=\s*){old}\b", rf"add_core_of\g<1>{t}", txt)
        open(f, "wb").write(txt.encode("utf-8", "surrogateescape"))
        owner[sid] = t
        print(f"  state {sid} ({f.replace(chr(92), '/').split('/')[-1][:-4]}): owner {old} -> {t}")
    moves = {p: t for p, t in wrong.items() if st[p] not in retag}

    # single provinces: to an adjacent state of the right owner, else the nearest one
    nb = adjacency(ids)
    cy = nd.mean(np.broadcast_to((np.arange(H) + .5)[:, None], ids.shape), ids, np.arange(ids.max() + 1))
    cx = nd.mean(np.broadcast_to(np.arange(W) + .5, ids.shape), ids, np.arange(ids.max() + 1))
    target = {}
    for p, t in moves.items():
        adj = Counter({st[q]: n for q, n in nb.get(p, {}).items() if q in st and owner.get(st[q]) == t and q not in moves})
        if adj:
            target[p] = adj.most_common(1)[0][0]
            continue
        cand = [q for q, sid in st.items() if owner.get(sid) == t and q not in moves and kinds.get(q) == "land"]
        if not cand:
            continue
        pts = np.c_[cx[cand], cy[cand]]
        # wrap: compare across the seam too
        d = np.minimum(np.abs(pts[:, 0] - cx[p]), W - np.abs(pts[:, 0] - cx[p])) ** 2 + (pts[:, 1] - cy[p]) ** 2
        target[p] = st[cand[int(np.argmin(d))]]
    edits = defaultdict(lambda: [set(), set()])  # state -> [remove, add]
    for p, sid in target.items():
        edits[st[p]][0].add(p); edits[sid][1].add(p)
    for sid, (rem, add) in edits.items():
        f = files[sid]
        txt = open(f, "rb").read().decode("utf-8", "surrogateescape")
        m = re.search(r"(provinces\s*=\s*\{)([^}]*)(\})", txt)
        cur = [q for q in m.group(2).split() if q.isdigit() and int(q) not in rem] + [str(q) for q in sorted(add)]
        assert cur, f"state {sid} would be emptied"
        txt = txt[:m.start()] + m.group(1) + "\n\t\t" + " ".join(cur) + "\n\t" + m.group(3) + txt[m.end():]
        open(f, "wb").write(txt.encode("utf-8", "surrogateescape"))
    print(f"  {len(retag)} states changed owner, {len(target)} provinces moved between {len(edits)} states")


if __name__ == "__main__":
    main(sys.argv[1], "--write" in sys.argv[2:], "--new" in sys.argv[2:])
