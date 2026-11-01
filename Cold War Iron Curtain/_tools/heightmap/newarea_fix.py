"""Second pass over the provinces the reprojection created (Arctic/Antarctic/seam cells, see border_owner.new_provinces).

Run from the mod root:  python _tools/heightmap/newarea_fix.py <data_dir> [--write]
1. a new land province lying across a real 1949 country border (CShapes) gives the part on the other side to the
   neighbouring province of that country (provinces.bmp)
2. a new mainland province joins the neighbouring older state of the same owner (the 'join nearby states' rule), so the
   Arctic coast strip belongs to Yukon/NWT/Nunavut etc. instead of one giant island state; a new state is never emptied
3. a moved province's line in the state's machine-generated vp_provinces/vp_values arrays moves with it
Run mapfix.py and positions.py afterwards.
"""
import io, re, sys, numpy as np
from collections import Counter, defaultdict
from PIL import Image
import proj
from gcps import land_mask_and_ids
from mapfix import adjacency
from border_owner import new_provinces, load_states, real_raster, RES


def vp_sync(files, moved):
    """a moved province's line in the machine-generated vp_provinces/vp_values arrays moves with it (the arrays list
    only some provinces of a state, so nothing else is touched)."""
    entry = re.compile(r"[ \t]*add_to_array = \{ THIS\.vp_provinces = (\d+) \} add_to_array = \{ THIS\.vp_values = ([\d.]+) \}\r?\n")
    txt = {s: open(files[s], "rb").read().decode("utf-8", "surrogateescape") for ab in moved.values() for s in ab}
    for p, (a, b) in moved.items():
        m = next((m for m in entry.finditer(txt[a]) if int(m.group(1)) == p), None)
        if not m:
            continue
        txt[a] = txt[a][:m.start()] + txt[a][m.end():]
        txt[b] = re.sub(r"([ \t]*### END OF MACHINE-GENERATED SECTION ###)", lambda e: m.group(0) + e.group(1), txt[b], count=1)
    for s, t in txt.items():
        open(files[s], "wb").write(t.encode("utf-8", "surrogateescape"))


def main(S, write=False):
    real_ll, names = real_raster(S)
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    new = new_provinces()
    files, st, owner = load_states()
    lo, la = proj.grid()
    realat = lambda y, x: real_ll[np.clip(((90 - la[y, x]) * RES).astype(int), 0, 180 * RES - 1),
                                  ((lo[y, x] + 180) % 360 * RES).astype(int) % (360 * RES)]
    land = {p for p, v in kinds.items() if v == "land"}
    # real country -> owner tag, from the old provinces
    vote = defaultdict(Counter)
    for p in [q for q in land if q not in new and q in st][::7]:
        y, x = np.nonzero(ids == p)
        for r, n in Counter(realat(y[::9], x[::9]).tolist()).items():
            if r:
                vote[r][owner[st[p]]] += n
    tag_of = {r: v.most_common(1)[0][0] for r, v in vote.items()}

    # 1. straddlers
    raw = open("map/provinces.bmp", "rb").read()
    rgb = np.array(Image.open(io.BytesIO(raw)).convert("RGB"))
    lut = {int(l.split(";")[0]): tuple(map(int, l.split(";")[1:4])) for l in open("map/definition.csv", encoding="latin-1") if l[:1].isdigit()}
    moved_px, real_tag = 0, {}
    for p in sorted(q for q in new if q in land):
        y, x = np.nonzero(ids == p)
        r = realat(y, x)
        c = Counter(r[r > 0].tolist())
        if c:
            real_tag[p] = tag_of.get(c.most_common(1)[0][0])
        if len(c) < 2:
            continue
        keep = c.most_common(1)[0][0]
        for other, n in c.most_common()[1:]:
            t = tag_of.get(other)
            m = r == other
            yy, xx = y[m], x[m]
            nbs = Counter()
            for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
                q = ids[np.clip(yy + dy, 0, H - 1), (xx + dx) % W]
                for v in q[(q != p)].tolist():
                    if v in land and owner.get(st.get(v)) == t:
                        nbs[v] += 1
            if not nbs:
                print(f"  {p}: part in {names[other]} has no {t} neighbour, left")
                continue
            to = nbs.most_common(1)[0][0]
            print(f"  {p}: {n} px in {names[other]} -> province {to} ({t}); rest stays {names[keep]}")
            ids[yy, xx] = to
            rgb[yy, xx] = lut[to]
            moved_px += n

    # 2. mainland new provinces join the neighbouring older state of the same owner
    nb = adjacency(ids)
    newstate = {s for s in set(st[p] for p in new if p in st) if all(p in new for p, s2 in st.items() if s2 == s)}
    settled = {p for p in land if p not in new}
    moved = {}
    for _ in range(20):
        step = 0
        for p in sorted(q for q in new if q in land and st.get(q) in newstate and q not in moved):
            o = real_tag.get(p) or owner[st[p]]  # a straddler's remnant follows its real country
            cand = Counter({st[q]: n for q, n in nb.get(p, {}).items() if (q in settled or q in moved) and q in st
                            and owner.get(st[q]) == o and st[q] not in newstate})
            if not cand:
                continue
            left = [q for q, s in st.items() if s == st[p] and q != p]
            if not left:
                continue  # never empty a state
            to = cand.most_common(1)[0][0]
            moved[p] = (st[p], to)
            st[p] = to
            step += 1
        if not step:
            break
    for p, (a, b) in sorted(moved.items()):
        print(f"  province {p}: state {a} -> {b} ({files[b].replace(chr(92), '/').split('/')[-1][:-4]})")
    print(f"{moved_px} px moved across real borders, {len(moved)} new provinces joined older states")
    if not write:
        return
    if moved_px:
        b = io.BytesIO(); Image.fromarray(rgb, "RGB").save(b, "BMP"); assert len(b.getvalue()) == len(raw)
        open("map/provinces.bmp", "wb").write(b.getvalue())
    for sid in {x for ab in moved.values() for x in ab}:
        f = files[sid]
        t = open(f, "rb").read().decode("utf-8", "surrogateescape")
        m = re.search(r"(provinces\s*=\s*\{)([^}]*)(\})", t)
        cur = sorted({int(q) for q in m.group(2).split() if q.isdigit() and st.get(int(q)) == sid} |
                     {p for p, s in st.items() if s == sid})
        t = t[:m.start()] + m.group(1) + "\n\t\t" + " ".join(map(str, cur)) + "\n\t" + m.group(3) + t[m.end():]
        open(f, "wb").write(t.encode("utf-8", "surrogateescape"))
    vp_sync(files, moved)


if __name__ == "__main__":
    main(sys.argv[1], "--write" in sys.argv[2:])
