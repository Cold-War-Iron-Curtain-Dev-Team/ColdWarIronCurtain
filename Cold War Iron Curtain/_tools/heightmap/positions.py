"""Refresh map/unitstacks.txt and map/buildings.txt after the heightmap or provinces.bmp change.

Run from the mod root:  python _tools/heightmap/positions.py <warp.npz> [--write]
- height (4th column) = new heightmap grey / 10, never below the 9.5 water plane (how the existing files were made)
- a building outside its own state (column 1) moves to the nearest pixel inside it; buildings standing on water (naval,
  floating harbours) stay. Unit stacks are not moved: ships in port, movement and attack spots sit off their province
- victory point markers (unitstacks type 38) move to the real city (gcps_vp.json, located through the warp), or the
  nearest point inside the province when the real spot falls outside it
x/z, rotation and the rest of each line are kept. Without --write it only prints what would change.
"""
import glob, json, re, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from scipy.spatial import cKDTree
from gcps import land_mask_and_ids

WATER_Y = 9.5


def pixel_sets(lab):
    """label -> (ys, xs) of its pixels, and of its interior (1 px in from the edge) when it has one."""
    order = np.argsort(lab, axis=None, kind="stable")
    flat = lab.ravel()[order]
    edge = np.zeros(lab.shape, bool)
    for ax in (0, 1):
        for s in (1, -1):
            edge |= np.roll(lab, s, ax) != lab
    inner = ~edge.ravel()[order]
    cuts = np.flatnonzero(np.diff(flat)) + 1
    out = {}
    for a, b in zip(np.r_[0, cuts], np.r_[cuts, len(flat)]):
        idx = order[a:b]
        keep = idx[inner[a:b]] if inner[a:b].any() else idx
        out[int(flat[a])] = np.divmod(keep, lab.shape[1])
    return out


def nearest_inside(sets, label, x, y):
    ys, xs = sets[label]
    k = np.argmin((ys - y) ** 2 + (xs - x) ** 2)
    return xs[k] + 0.5, ys[k] + 0.5


PER_COAST = ("naval_base_spawn", "coastal_bunker", "naval_headquarters", "naval_supply_hub")  # one per coastal province


def naval_rebuild(lines, ids, kinds, st, height):
    """One entry of each PER_COAST type per coastal land province (the engine's nudger wants a port in every one),
    standing on a shore pixel of that province facing its sea. Existing entries are reused (nearest shore of their
    state); missing ones are added. Returns the new line list."""
    H, W = ids.shape
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    cy, cx, cs = [], [], []
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        sh = np.roll(np.roll(ids, -dy, 0), -dx, 1)
        ssh = np.roll(np.roll(sea, -dy, 0), -dx, 1)
        m = land & ssh
        if dy == -1: m[0] = False
        if dy == 1: m[-1] = False
        y, x = np.nonzero(m)
        cy.append(y); cx.append(x); cs.append(sh[y, x])
    cy, cx, cs = np.concatenate(cy), np.concatenate(cx), np.concatenate(cs)
    cp = ids[cy, cx]
    cst = st[cp]
    tree = {}
    for s in np.unique(cst):
        i = np.flatnonzero(cst == s)
        tree[int(s)] = (cKDTree(np.c_[cx[i], cy[i]]), i)
    by_prov = {}
    for i, q in enumerate(cp):
        by_prov.setdefault(int(q), []).append(i)

    def place(i, owner, typ, rot=None):
        x, y, s = cx[i], cy[i], int(cs[i])
        if rot is None:  # face the sea (vanilla convention: atan2(dz, dx) + pi/2)
            sy, sx = np.nonzero(sea[max(0, y - 3):y + 4, max(0, x - 3):x + 4] & (ids[max(0, y - 3):y + 4, max(0, x - 3):x + 4] == s))
            dx, dz = sx.mean() - min(3, x), -(sy.mean() - min(3, y))
            rot = np.arctan2(dz, dx) + np.pi / 2
        X, Z = x + .5, H - y - .5
        return f"{owner};{typ};{X:.2f};{height(X, Z):.2f};{Z:.2f};{rot:.2f};{s if typ == 'naval_base_spawn' else 0}"

    keep, rest = {}, []
    for n, line in enumerate(lines):
        p = line.split(";")
        if len(p) < 7 or p[1] not in PER_COAST:
            rest.append(line); continue
        owner = int(p[0])
        if owner not in tree:
            continue  # state has no coast now: drop
        t, idx = tree[owner]
        x, y = float(p[2]), H - float(p[4])
        d, j = t.query([x - .5, y - .5])
        i = idx[j]
        key = (int(cp[i]), p[1])
        if key not in keep or d < keep[key][0]:
            want = int(p[6]) if p[1] == "naval_base_spawn" and p[6].isdigit() else None
            if want is not None:  # keep the port's sea if this shore touches it
                alt = [k for k in by_prov[int(cp[i])] if int(cs[k]) == want]
                if alt:
                    i = min(alt, key=lambda k: (cx[k] - x) ** 2 + (cy[k] - y) ** 2)
            keep[key] = (d, place(i, owner, p[1], float(p[5])))
    added = 0
    for q, ii in by_prov.items():
        if st[q] == 0:
            continue
        seas = np.bincount(cs[ii])
        best_sea = np.argmax(seas)
        on = [i for i in ii if cs[i] == best_sea]
        mid = on[len(on) // 2]
        for typ in PER_COAST:
            if (q, typ) not in keep:
                keep[(q, typ)] = (0, place(mid, int(st[q]), typ)); added += 1
    print(f"  coastal provinces {len(by_prov)}, per-province naval entries {len(keep)} ({added} added)")
    return rest + [v for _, v in sorted(keep.values(), key=lambda t: int(t[1].split(';')[0]))]


def main(warp_npz, write=False):
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    hm = np.asarray(Image.open("map/heightmap.bmp")).astype(np.float32)
    st = np.zeros(ids.max() + 1, np.int32)
    for f in glob.glob("history/states/*.txt"):
        t = re.sub(r"#[^\n]*", "", open(f, encoding="utf-8", errors="ignore").read())
        m, pr = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
        if m and pr:
            st[[int(q) for q in pr.group(1).split() if q.isdigit() and int(q) < len(st)]] = int(m.group(1))
    states = st[ids]
    dry = np.where(hm >= WATER_Y * 10 + 1, states, 0)  # the engine wants buildings over land: province and heightmap
    prov_sets, state_sets = pixel_sets(ids), None

    # real city spot per VP province: lon/lat -> nearest map pixel through the warp
    w = np.load(warp_npz)
    lo, la = np.radians(w["lo"].ravel()), np.radians(w["la"].ravel())
    tree = cKDTree(np.c_[np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)].astype(np.float32))
    del lo, la, w
    vp_target = {}
    for o in json.load(open("_tools/heightmap/gcps_vp.json")):
        lo1, la1 = np.radians(o["lon"]), np.radians(o["lat"])
        _, i = tree.query([np.cos(la1) * np.cos(lo1), np.cos(la1) * np.sin(lo1), np.sin(la1)])
        pid = int(ids[int(o["y"]), int(o["x"]) % W])  # the province whose VP was matched
        vp_target[pid] = (i % W + 0.5, i // W + 0.5)
    del tree

    row = lambda z: min(H - 1, max(0, H - 1 - int(np.floor(z))))  # game z counts pixel rows from the bottom

    def height(x, z):
        return max(hm[row(z), int(x) % W] / 10.0, WATER_Y)

    for path, by_state in (("map/unitstacks.txt", False), ("map/buildings.txt", True)):
        if by_state and state_sets is None:
            state_sets = pixel_sets(dry)
        lines = open(path, encoding="utf-8").read().splitlines()
        if by_state:
            lines = naval_rebuild(lines, ids, kinds, st, height)
        moved = vp = dy = 0
        out = []
        for line in lines:
            p = line.split(";")
            if len(p) < 6:
                out.append(line)
                continue
            owner, x, z = int(p[0]), float(p[2]), float(p[4])
            if not by_state and p[1] == "38" and owner in vp_target:
                tx, ty = vp_target[owner]
                if ids[int(ty), int(tx) % W] != owner:
                    tx, ty = nearest_inside(prov_sets, owner, tx, ty)
                x, z = tx, H - ty
                vp += 1
            else:
                py, px = row(z), int(x) % W
                if by_state and p[1] not in PER_COAST + ("floating_harbor",) and dry[py, px] != owner and owner in state_sets:
                    nx, ny = nearest_inside(state_sets, owner, px, py)
                    x, z = nx, H - ny
                    moved += 1
            y = height(x, z)
            dy += abs(y - float(p[3])) > 0.05
            p[2], p[3], p[4] = f"{x:.2f}", f"{y:.2f}", f"{z:.2f}"
            out.append(";".join(p))
        print(f"{path}: {len(lines)} entries, height changed {dy}, moved back inside {moved}, victory points placed {vp}")
        if write:
            open(path, "w", encoding="utf-8", newline="\r\n").write("\n".join(out) + "\n")


if __name__ == "__main__":
    main(sys.argv[1], "--write" in sys.argv[2:])
