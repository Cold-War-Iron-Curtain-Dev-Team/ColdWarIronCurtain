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


def main(warp_npz, write=False):
    ids, kinds = land_mask_and_ids()
    H, W = ids.shape
    hm = np.asarray(Image.open("map/heightmap.bmp")).astype(np.float32)
    st = np.zeros(ids.max() + 1, np.int32)
    for f in glob.glob("history/states/*.txt"):
        t = open(f, encoding="utf-8", errors="ignore").read()
        m, pr = re.search(r"\bid\s*=\s*(\d+)", t), re.search(r"provinces\s*=\s*\{([^}]*)\}", t)
        if m and pr:
            st[[int(q) for q in pr.group(1).split() if q.isdigit() and int(q) < len(st)]] = int(m.group(1))
    states = st[ids]
    water = np.isin(ids, [k for k, v in kinds.items() if v in ("sea", "lake")])
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

    def height(x, z):
        return max(hm[min(H - 1, max(0, int(H - z))), int(x) % W] / 10.0, WATER_Y)

    for path, by_state in (("map/unitstacks.txt", False), ("map/buildings.txt", True)):
        if by_state and state_sets is None:
            state_sets = pixel_sets(states)
        lines = open(path, encoding="utf-8").read().splitlines()
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
                py, px = min(H - 1, max(0, int(H - z))), int(x) % W
                # positions often sit exactly on a pixel edge: inside if any pixel touching that corner is the state's
                near = states[max(0, py - 1):py + 1, [px, (px - 1) % W]] if by_state else owner
                if by_state and owner not in near and owner in state_sets and not water[py, px]:
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
