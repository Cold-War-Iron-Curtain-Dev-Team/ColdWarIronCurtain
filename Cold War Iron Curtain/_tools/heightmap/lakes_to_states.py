"""Put lake provinces into states, as vanilla does, so they take their country's colour and fill the holes that
otherwise bend the country/faction name curve around them.

Run from the mod root:  python _tools/heightmap/lakes_to_states.py [--write]   then mapfix.py (moves each lake into its
state's strategic region).
- a lake touching one country goes whole to the state of that country with the longest shore on it
- a lake of SPLIT_MIN px or more touching several countries is split down the middle (each lake pixel to the country
  of the nearest land pixel); the biggest piece keeps the province id, the others become new lake provinces. Pieces under
  PIECE_MIN px, or detached bits, join the piece they touch most. Smaller shared lakes go whole to the longest shore.
- SKIP: the lakes vanilla also leaves out of states (Caspian, Ob and Yenisei gulfs), and lakes that are a strategic
  region on their own (the region would otherwise grab land states).
"""
import io, re, sys, numpy as np
from collections import Counter
from PIL import Image
from scipy import ndimage as nd
from gcps import land_mask_and_ids
from border_owner import load_states

SKIP = {843, 1050, 1271, 1496, 2703, 5918, 9125, 11827, 2332, 1721}  # + Ladoga, Aral: their own strategic region
SPLIT_MIN, PIECE_MIN, PAD = 150, 30, 40


def split(I, p, land, own):
    """lake p in crop I -> {owner: mask}, pieces connected and at least PIECE_MIN px."""
    m = I == p
    _, (iy, ix) = nd.distance_transform_edt(~land, return_indices=True)
    O = np.where(m, own[iy, ix], "")
    for _ in range(20):
        changed = False
        for o in [o for o in np.unique(O[m]) if o]:
            lab, n = nd.label(O == o)
            sizes = np.bincount(lab.ravel())[1:]
            keep = np.argmax(sizes) + 1
            for k in range(1, n + 1):
                if k != keep and sizes[k - 1] or sizes[k - 1] < PIECE_MIN:
                    piece = lab == k
                    c = Counter(O[nd.binary_dilation(piece) & m & ~piece].tolist())
                    c.pop(o, None); c.pop("", None)
                    if c:
                        O[piece] = c.most_common(1)[0][0]; changed = True
        if not changed:
            break
    return {o: O == o for o in np.unique(O[m]) if o}


def main(write=False):
    ids, kind = land_mask_and_ids()
    H, W = ids.shape
    files, st, owner = load_states()
    own_of = np.zeros(ids.max() + 1, "U3")
    for q, s in st.items():
        if kind.get(q) == "land":
            own_of[q] = owner.get(s) or ""
    out = ids.copy()
    lines = open("map/definition.csv", "rb").read().decode("latin-1").split("\r\n")
    row = {int(l.split(";")[0]): i for i, l in enumerate(lines) if l[:1].isdigit()}
    used = {tuple(map(int, lines[i].split(";")[1:4])) for i in row.values()}
    next_id = max(row) + 1
    rng = np.random.default_rng(1949)
    add = {}  # state -> [provinces]
    region_add = []  # (new id, original lake)
    S = nd.find_objects(ids)
    for p in sorted(q for q, v in kind.items() if v == "lake" and q not in SKIP and q not in st):
        if p - 1 >= len(S) or S[p - 1] is None:
            continue
        ys, xs = S[p - 1]
        assert xs.stop - xs.start < W // 2, f"lake {p} crosses the seam"
        sl = (slice(max(ys.start - PAD, 0), min(ys.stop + PAD, H)), slice(max(xs.start - PAD, 0), min(xs.stop + PAD, W)))
        I = ids[sl]
        land = np.isin(I, np.nonzero(own_of != "")[0])
        own = own_of[I]
        m = I == p
        shore = nd.binary_dilation(m) & ~m & land
        if not shore.any():
            print(f"  lake {p}: no owned shore, left out"); continue
        owners = Counter(own[shore].tolist())
        if len(owners) > 1 and m.sum() >= SPLIT_MIN:
            pieces = split(I, p, land, own)
        else:
            pieces = {owners.most_common(1)[0][0]: m}
        first = True
        for o, pm in sorted(pieces.items(), key=lambda kv: -kv[1].sum()):
            ring = nd.binary_dilation(pm) & ~pm & land & (own == o)
            sid = Counter(st[int(q)] for q in I[ring]).most_common(1)[0][0] if ring.any() else \
                Counter(st[int(q)] for q in I[shore] if owner.get(st[int(q)]) == o).most_common(1)[0][0]
            if first:
                pid, first = p, False
            else:
                pid = next_id; next_id += 1
                while True:
                    c = tuple(int(v) for v in rng.integers(1, 255, 3))
                    if c not in used:
                        used.add(c); break
                q = lines[row[p]].split(";")
                q[0], q[1], q[2], q[3] = str(pid), *map(str, c)
                lines.insert(max(row.values()) + 1, ";".join(q)); row[pid] = max(row.values()) + 1
                out[sl][pm] = pid
                region_add.append((pid, p))
            add.setdefault(sid, []).append(pid)
            print(f"  lake {p} ({pm.sum()} px) -> {o} state {sid}" + (f" as new province {pid}" if pid != p else ""))
    print(f"{sum(map(len, add.values()))} lake provinces into {len(add)} states, {len(region_add)} new from splits")
    assert sorted(row) == list(range(len(row))), "province ids not continuous"
    if not write:
        return
    # provinces.bmp: only the split pieces change colour
    raw = open("map/provinces.bmp", "rb").read()
    rgb = np.array(Image.open(io.BytesIO(raw)).convert("RGB"))
    for pid, _ in region_add:
        rgb[out == pid] = tuple(map(int, lines[row[pid]].split(";")[1:4]))
    b = io.BytesIO(); Image.fromarray(rgb, "RGB").save(b, "BMP"); assert len(b.getvalue()) == len(raw)
    open("map/provinces.bmp", "wb").write(b.getvalue())
    open("map/definition.csv", "wb").write("\r\n".join(lines).encode("latin-1"))
    for sid, ps in add.items():
        t = open(files[sid], "rb").read().decode("utf-8", "surrogateescape")
        t2 = re.sub(r"(provinces\s*=\s*\{)([^}]*)\}", lambda m: m.group(1) + m.group(2).rstrip() + " " + " ".join(map(str, ps)) + " }",
                    t, count=1)
        assert t2 != t, files[sid]
        open(files[sid], "wb").write(t2.encode("utf-8", "surrogateescape"))
    # a new piece starts in its original lake's strategic region; mapfix then moves every lake to its state's region
    import glob
    for f in glob.glob("map/strategicregions/*.txt"):
        t = open(f, "rb").read().decode("utf-8", "surrogateescape")
        body = re.search(r"provinces\s*=\s*\{([^}]*)\}", t).group(1).split()
        extra = [str(n) for n, p in region_add if str(p) in body]
        if extra:
            t = re.sub(r"(provinces\s*=\s*\{)([^}]*)\}", lambda m: m.group(1) + m.group(2).rstrip() + " " + " ".join(extra) + " \n\t}", t, count=1)
            open(f, "wb").write(t.encode("utf-8", "surrogateescape"))


if __name__ == "__main__":
    main("--write" in sys.argv[1:])
