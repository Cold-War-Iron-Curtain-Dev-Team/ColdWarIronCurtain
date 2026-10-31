"""Rebuild map/rivers.bmp from Natural Earth 10m river centerlines (ne_10m_rivers_lake_centerlines.geojson).

Run from the mod root:  python _tools/heightmap/rivers.py <etopo.nc> <rivers.geojson> <out_dir> [max_scalerank=10]
GAMEPLAY: rivers.bmp also sets river crossings for combat, so this changes more than visuals.
Palette rules (vanilla): 0 source, 1 flow-in (tributary's last pixel, next to the river it joins), 2 flow-out (branch
start, next to the river it leaves), 3..11 width narrow->wide, 255 land, 254 water. Rivers are 1 px wide and
4-connected. Natural Earth splits rivers at confluences, so segments are first chained back into whole rivers (main
stem = biggest incoming segment) and drawn after the river they flow into; each is walked from its source downstream,
stops at sea/lake, and ends with a flow-in where it meets that river. One green per connected system (wiki example).
"""
import json, sys, numpy as np
from collections import defaultdict
from PIL import Image
from scipy import ndimage as nd
from scipy.spatial import cKDTree
from build import warp
from gcps import land_mask_and_ids

SOURCE, FLOW_IN, FLOW_OUT, LAND, WATER = 0, 1, 2, 255, 254  # vanilla: 255 white land, 254 grey sea
VANILLA = "F:/SteamLibrary/steamapps/common/Hearts of Iron IV/map/rivers.bmp"
N4 = ((0, 1), (0, -1), (1, 0), (-1, 0))


def width(rank):
    return {0: 11, 1: 11, 2: 10, 3: 9, 4: 7, 5: 6, 6: 6, 7: 4}.get(int(rank), 3)


def unit(lo, la):
    lo, la = np.radians(lo), np.radians(la)
    return np.stack([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)], -1)


def segments(path, max_rank, elev):
    """(rank, coords) per river line, oriented from the higher end."""
    for f in json.load(open(path, encoding="utf-8"))["features"]:
        p = f["properties"]
        if p["featurecla"] not in ("River", "Lake Centerline") or p["scalerank"] is None or p["scalerank"] > max_rank:
            continue
        g = f["geometry"]
        for part in (g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]):
            c = np.array(part, np.float64)
            e = elev(c[[0, -1]])
            yield p["scalerank"], (c if e[0] >= e[1] else c[::-1])


def chains(segs, elev, tol=0.03):
    """Join Natural Earth segments into whole rivers and order them so every river is drawn after the one it flows
    into. Endpoints within `tol` degrees are one node. Returns [(coords, per-point rank)].
    Flat segments (ends < 20 m apart, e.g. the lower Amazon) are oriented by the network instead of the DEM: an end on
    another river's line (confluences are often mid-segment, not nodes) or at sea level is the mouth."""
    n = len(segs)
    P = np.array([c[0] for _, c in segs] + [c[-1] for _, c in segs])
    parent = list(range(2 * n))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    for a, b in cKDTree(P).query_pairs(tol):
        parent[find(a)] = find(b)
    node = [find(a) for a in range(2 * n)]
    deg = defaultdict(int)
    for a in node:
        deg[a] += 1
    segs = list(segs)
    sn, en = node[:n], node[n:]
    vseg = np.concatenate([np.full(len(c), i) for i, (_, c) in enumerate(segs)])
    vtree = cKDTree(np.concatenate([c for _, c in segs]))
    on_other = lambda pt, own: {int(vseg[j]) for j in vtree.query_ball_point(pt, 0.05)} - set(own)
    # an end within ~10 km of ocean (DEM below sea level) is a mouth, whatever the DEM noise on a delta says
    off = np.stack(np.meshgrid(np.linspace(-.1, .1, 5), np.linspace(-.1, .1, 5)), -1).reshape(-1, 2)
    coastal = lambda pt: bool((elev(pt + off) < 0).any())
    for i, (r, c) in enumerate(segs):
        e = elev(c[[0, -1]])
        cst = coastal(c[0]), coastal(c[-1])
        if cst[0] != cst[1]:
            if cst[0]:
                segs[i] = (r, c[::-1])
                sn[i], en[i] = en[i], sn[i]
        elif abs(e[0] - e[1]) < 20:
            mouth = [bool(on_other(c[k], [i]) and deg[(sn, en)[k == -1][i]] == 1) or e[k] < 5 for k in (0, -1)]
            if mouth[0] and not mouth[1]:
                segs[i] = (r, c[::-1])
                sn[i], en[i] = en[i], sn[i]

    starts, ends = defaultdict(list), defaultdict(list)
    for i in range(n):
        starts[sn[i]].append(i)
        ends[en[i]].append(i)
    nxt = {}
    for nd_, down in starts.items():
        if len(down) == 1 and ends.get(nd_):
            nxt[min(ends[nd_], key=lambda i: segs[i][0])] = down[0]  # main stem continues, tributaries join
    heads = sorted(set(range(n)) - set(nxt.values()))
    linked = set()
    for h in heads:
        i = h
        while i is not None and i not in linked:
            linked.add(i)
            i = nxt.get(i)
    for i in range(n):  # segments only reachable through a loop in the data: start a chain there
        if i not in linked:
            heads.append(i)
            while i is not None and i not in linked:
                linked.add(i)
                i = nxt.get(i)
    ch, chain_of_node = [], defaultdict(set)
    for h in heads:
        ids, i = [], h
        while i is not None and i not in ids and (i == h or i not in heads):
            ids.append(i)
            i = nxt.get(i)
        k = len(ch)
        ch.append(ids)
        for i in ids:
            chain_of_node[sn[i]].add(k)
            chain_of_node[en[i]].add(k)
    rank = [min(segs[i][0] for i in ids) for ids in ch]
    # parent = the river this one flows into (another chain through its last node)
    kids, roots = defaultdict(list), []
    chain_of_seg = {i: k for k, ids in enumerate(ch) for i in ids}
    for k, ids in enumerate(ch):
        others = ({chain_of_seg[i] for i in on_other(segs[ids[-1]][1][-1], ids)} | chain_of_node[en[ids[-1]]]) - {k}
        if others:
            kids[min(others, key=lambda o: rank[o])].append(k)
        else:
            roots.append(k)
    order, seen, queue = [], set(), sorted(roots, key=lambda k: rank[k])
    while queue:
        k = queue.pop(0)
        if k in seen:
            continue
        seen.add(k)
        order.append(k)
        queue += sorted(kids[k], key=lambda o: rank[o])
    order += sorted(set(range(len(ch))) - seen, key=lambda k: rank[k])  # cycles in the data
    # biggest rivers first: a river stops where it touches one already drawn, so a late main stem (the Rhine counts as
    # a Maas tributary in the delta) would be cut off by its own small tributaries; parents first within a rank
    order.sort(key=lambda k: rank[k])
    out = []
    for k in order:
        c = np.concatenate([segs[i][1] for i in ch[k]])
        r = np.concatenate([np.full(len(segs[i][1]), segs[i][0]) for i in ch[k]])
        out.append((c, np.minimum.accumulate(r)))  # never narrower downstream
    return out


def densify(c, r, step=0.02):
    pts, rk = [c[:1]], [r[:1]]
    for k, (a, b) in enumerate(zip(c[:-1], c[1:])):
        n = max(1, int(np.ceil(np.abs(b - a).max() / step)))
        pts.append(a + (b - a) * (np.arange(1, n + 1)[:, None] / n))
        rk.append(np.full(n, r[k + 1]))
    return np.concatenate(pts), np.concatenate(rk)


def four_connect(px, W):
    """Consecutive (y, x, rank) pixels -> 4-connected path; x may run past the seam, caller wraps it."""
    out = [px[0]]
    for y1, x1, r in px[1:]:
        y0, x0, _ = out[-1]
        x1 += W * round((x0 - x1) / W)  # cross the east-west seam the short way
        while (y0, x0) != (y1, x1):
            if abs(x1 - x0) >= abs(y1 - y0) and x1 != x0:
                x0 += 1 if x1 > x0 else -1
            else:
                y0 += 1 if y1 > y0 else -1
            out.append((y0, x0, r))
    return out


def main(dem_path, geojson, out, max_rank=10):
    ids, kinds = land_mask_and_ids()
    land = np.isin(ids, [k for k, v in kinds.items() if v == "land"])
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    lo, la, z, rc = warp(dem_path, sea)
    H, W = land.shape
    tree = cKDTree(unit(lo.ravel(), la.ravel()).astype(np.float32))
    # river name at a map pixel (nearest Natural Earth vertex): two heads only merge if they are the same river
    names, verts = [], []
    for f in json.load(open(geojson, encoding="utf-8"))["features"]:
        g = f["geometry"]
        for part in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            verts += part
            names += [f["properties"].get("name") or ""] * len(part)
    vt = cKDTree(unit(*np.array(verts, np.float64).T).astype(np.float32))
    name_at = lambda q: names[vt.query(unit(lo[q], la[q]).astype(np.float32))[1]]
    same_river = lambda a, b: name_at(a) != "" and name_at(a) == name_at(b)
    elev = lambda c: nd.map_coordinates(z, rc(c[:, 0], c[:, 1]), order=1, mode="wrap")
    rivers = chains(list(segments(geojson, float(max_rank), elev)), elev)
    # real elevation (m) per map pixel: the heightmap carves every lake into the same pit, which hides the steps of a
    # reservoir cascade (Dnieper: Kremenchuk ~81 m, Dnipro ~51 m, Kakhovka ~16 m) that orient the river pieces between
    hm = nd.map_coordinates(z, rc(lo, la), order=1, mode="wrap").astype(np.float32)

    img = np.where(land, LAND, WATER).astype(np.uint8)
    river = np.zeros((H, W), bool)
    nbrs = lambda q: [(q[0] + dy, (q[1] + dx) % W) for dy, dx in N4 if 0 <= q[0] + dy < H]  # x wraps, y doesn't
    stats = {"drawn": 0, "joined": 0}

    def draw(piece):
        """Walk one land-only (y, x, width) path downstream; stop on contact with an earlier river (flow-in)."""
        pts, ranks, own, end_join = [], [], {}, False
        for y, x, r in piece:
            if (y, x) in own:  # path doubled back: cut the loop
                del pts[own[(y, x)] + 1:], ranks[own[(y, x)] + 1:]
                own = {p: i for i, p in enumerate(pts)}
                continue
            nb = nbrs((y, x))
            if any(p in own and own[p] != len(pts) - 1 for p in nb):
                k = min(own[p] for p in nb if p in own)  # touches itself: shortcut through the older pixel
                del pts[k + 1:], ranks[k + 1:]
                own = {p: i for i, p in enumerate(pts)}
            hits = [p for p in [(y, x)] + nb if river[p]]
            if hits and len(pts) < 3:  # starts against an earlier river (e.g. leaving a lake where another ends):
                pts, ranks, own = [], [], {}  # start past the contact instead of dropping the whole river
                continue
            src = [p for p in hits if img[p] == SOURCE and sum(river[q] for q in nbrs(p)) == 1]
            if pts and src:
                # reached the head of a river drawn earlier (same river split in the data): continue into it
                sp = src[0]
                if (y, x) == sp:
                    img[sp] = next(img[q] for q in nbrs(sp) if river[q])
                    break
                if hits == [sp] and not any(p in own and p != pts[-1] for p in nb):
                    own[(y, x)] = len(pts)
                    pts.append((y, x))
                    ranks.append(r)
                    img[sp] = next(img[q] for q in nbrs(sp) if river[q])
                    break
            if hits and all(retract(p, img, river, nbrs) for p in hits):
                pass  # ran into loose tributary tails: they were pulled back, keep going (gap pass reconnects them)
            elif hits:
                # flow-in: touches exactly one plain river pixel and none of its own but its base; back up a few
                # pixels if the river it meets runs diagonally here (no single-contact pixel)
                for back in range(min(4, len(pts))):
                    base = pts[-1 - back]
                    cands = ([(y, x)] if back == 0 else []) + nbrs(base)
                    hit = next((cd for cd in cands if not river[cd] and land[cd] and cd not in own
                                and base in nbrs(cd)
                                and [img[p] > 2 for p in nbrs(cd) if river[p]] == [True]
                                and not any(p in own and p != base for p in nbrs(cd))), None)
                    if hit:
                        del pts[len(pts) - back:], ranks[len(ranks) - back:]
                        pts.append(hit)
                        ranks.append(ranks[-1])
                        end_join = True
                        break
                break
            own[(y, x)] = len(pts)
            pts.append((y, x))
            ranks.append(r)
        if len(pts) < 4:
            return
        ys, xs = np.array(pts).T
        img[ys, xs] = ranks
        river[ys, xs] = True
        img[pts[0]] = SOURCE  # markers are re-derived per system in normalize()
        if end_join:
            img[pts[-1]] = FLOW_IN
            stats["joined"] += 1
        stats["drawn"] += 1

    for c, rk in rivers:
        d, dr = densify(c, rk)
        _, idx = tree.query(unit(d[:, 0], d[:, 1]).astype(np.float32))
        px = [(int(i // W), int(i % W), width(r)) for i, r in zip(idx, dr)]
        px = [p for i, p in enumerate(px) if i == 0 or p[:2] != px[i - 1][:2]]
        if len(px) < 2:
            continue
        cur = []
        for y, x, r in four_connect(px, W):
            x %= W
            if not land[y, x]:  # sea mouth or lake: end this piece, restart on the far side
                if cur:
                    draw(cur)
                cur = []
                continue
            cur.append((y, x, r))
        if cur:
            draw(cur)

    drawn, joined = stats["drawn"], stats["joined"]

    print("gaps closed:", close_gaps(img, river, land, nbrs, same_river))
    del lo, la
    print("systems normalised (mouths bridged, markers skipped):", normalize(img, land, hm, nbrs))
    # leftover forks normalize() could not mark (arm forks right at the junction): flow-in on the narrowest arm
    roll4 = lambda m: sum(np.roll(m, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1)))
    plain = (img > 2) & (img <= 11)
    for q in map(tuple, np.argwhere(plain & (roll4(plain) > 2))):
        arms = [n for n in nbrs(q) if 2 < img[n] <= 11]
        img[min(arms, key=lambda n: (img[n], min(int(img[t]) for t in nbrs(n) if t != q and img[t] <= 11) if any(t != q and img[t] <= 11 for t in nbrs(n)) else 0))] = FLOW_IN
    check(img)
    old = Image.open(VANILLA)
    # vanilla header + palette bytes as-is: Pillow's BMP (colours used/important = 256) gives
    # "MAP_ERROR: Palette in rivers.bmp is probably not correct"
    raw = open(VANILLA, "rb").read()
    off, n = int.from_bytes(raw[10:14], "little"), W * H  # width is a multiple of 4: no row padding
    assert W % 4 == 0
    hdr = bytearray(raw[:off])  # vanilla's palette, this map's size
    hdr[2:6], hdr[18:22], hdr[22:26], hdr[34:38] = ((off + n).to_bytes(4, "little"), W.to_bytes(4, "little"),
                                                    H.to_bytes(4, "little"), n.to_bytes(4, "little"))
    open(f"{out}/rivers.bmp", "wb").write(bytes(hdr) + np.ascontiguousarray(img[::-1]).tobytes())
    print(f"rivers drawn: {drawn} ({joined} join another), river px: {int((img <= 11).sum())} (old {int((np.asarray(old) <= 11).sum())})")


def retract(c, img, river, nbrs, reach=4):
    """If plain pixel c is within `reach` of a loose river end (not at water, not a marker), erase c..end and one more
    pixel behind c. Returns False (nothing changed) otherwise."""
    if img[c] <= 2:
        return False
    for start in [p for p in nbrs(c) if river[p]] + [None]:
        path, prev, cur = [c], start, c  # walk away from `start`
        while len(path) <= reach:
            nx = [p for p in nbrs(cur) if river[p] and p != prev]
            if not nx:
                if img[cur] > 2 and not any(img[p] == WATER for p in nbrs(cur)):
                    behind = [p for p in nbrs(c) if river[p] and p not in path and img[p] > 2]
                    for p in path + behind[:1]:  # the new end is left plain; the gap pass gives it a flow-in
                        img[p], river[p] = LAND, False
                    return True
                break
            if len(nx) > 1 or img[nx[0]] <= 2:
                break
            prev, cur = cur, nx[0]
            path.append(cur)
    return False


def close_gaps(img, river, land, nbrs, same_river, reach=20):
    """Bridge loose river ends (plain, one neighbour, not at water) to a nearby river with a short 4-connected path
    ending in a flow-in that touches exactly one plain pixel of the other river."""
    H, W = img.shape
    lab, _ = nd.label(img <= 11)
    roll4 = lambda m: sum(np.roll(m, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1)))
    # loose ends, sources included: a flat reservoir stretch can orient two pieces of one river away from each other
    ends = np.argwhere(((img > 2) & (img <= 11) | (img == SOURCE)) & (roll4(img <= 11) == 1) & (roll4(img == WATER) == 0))
    closed = 0
    for e in map(tuple, ends):
        me, colour = lab[e], img[e] if img[e] > 2 else next((img[n] for n in nbrs(e) if 2 < img[n] <= 11), 3)
        if not river[e] or sum(river[p] for p in nbrs(e)) != 1:
            continue  # erased, or an earlier bridge already reached it
        is_src = img[e] == SOURCE  # a source only joins another river's head right next to it (never across a watershed)
        prev = {e: None}
        frontier, found, coast = [e], None, False
        for _ in range(3 if is_src else reach):
            nxt = []
            for q in frontier:
                for p in nbrs(q):
                    if p in prev or river[p] or not land[p]:
                        continue
                    others = [n for n in nbrs(p) if river[n] and n != q]
                    if not others and not is_src and any(img[n] == WATER for n in nbrs(p)):  # reached the coast / a lake shore
                        if not any(n in prev and n != q for n in nbrs(p)):
                            prev[p], found, coast = q, p, True
                            break
                    elif not others:
                        prev[p] = q
                        nxt.append(p)
                    elif (len(others) == 1 and lab[others[0]] != me
                          and ((img[others[0]] > 2 and not is_src) or (img[others[0]] == SOURCE and sum(river[t] for t in nbrs(others[0])) == 1
                                                                         and (not is_src or same_river(e, others[0]))))
                          and not any(n in prev and n != q for n in nbrs(p))):
                        prev[p] = q
                        found = p
                        break
                if found:
                    break
            if found:
                break
            frontier = nxt
        if not found:
            continue
        path, q = [], found
        while q != e:
            path.append(q)
            q = prev[q]
        # the bridge must not touch itself except along its own chain
        if any(sum(n in path or n == e for n in nbrs(p)) > 2 for p in path):
            continue
        for p in path:
            img[p], river[p] = colour, True
        head = next((n for n in nbrs(found) if img[n] == SOURCE and n != e), None)
        if head:  # ran into another river's head (one river split in two, e.g. touching only diagonally): continue into it
            img[head] = colour
        elif not coast:
            img[found] = FLOW_IN
        closed += 1
    return closed


def normalize(img, land, elev, nbrs, reach=20):
    """Re-derive all markers per river system from the finished raster, independent of how the data was digitised.
    Mouth = lowest end near water (bridged to the coast if within `reach` px), else the lowest end (`elev`, metres).
    Green on the end of the longest path upstream from the mouth; at every fork the longest arm continues and each
    other arm gets a flow-in on its pixel next to the fork (a flow-out if the arm reaches water: a delta branch)."""
    H, W = img.shape
    for m in (SOURCE, FLOW_IN, FLOW_OUT):  # start from plain rivers
        for q in map(tuple, np.argwhere(img == m)):
            img[q] = next((img[n] for n in nbrs(q) if 2 < img[n] <= 11), 3)
    dw = nd.distance_transform_edt(img != WATER)
    lab, n = nd.label(img <= 11)
    objs = nd.find_objects(lab)
    bridged = skipped = 0
    for k in range(1, n + 1):
        sl = objs[k - 1]
        pix = [(int(y) + sl[0].start, int(x) + sl[1].start) for y, x in np.argwhere(lab[sl] == k)]
        if len(pix) < 4:  # specks left by trimming
            for q in pix:
                img[q] = LAND if land[q] else WATER
            continue
        S = set(pix)
        adj = {q: [p for p in nbrs(q) if p in S] for q in pix}
        ends = [q for q in pix if len(adj[q]) == 1] or pix[:1]
        # lowest end near water (the Rhine touches Lake Constance and the North Sea), then the widest (widths only grow
        # downstream, so a narrow lake-side tributary end is not the mouth); with no end near water, the lowest end
        mouth = min(ends, key=lambda q: (dw[q] > reach, int(elev[q]) // 5, -int(img[q]), dw[q]))
        if 1 < dw[mouth] <= reach:  # bridge to the coast without touching other rivers
            prev, frontier, hit = {mouth: None}, [mouth], None
            while frontier and not hit:
                nxt = []
                for q in frontier:
                    for p in nbrs(q):
                        if p in prev or img[p] <= 11 or not land[p] or abs(p[0] - mouth[0]) + abs(p[1] - mouth[1]) > reach * 2:
                            continue
                        if any(img[t] <= 11 and t != q for t in nbrs(p)) or any(t in prev and t != q for t in nbrs(p)):
                            continue
                        prev[p] = q
                        if dw[p] <= 1:
                            hit = p
                            break
                        nxt.append(p)
                    if hit:
                        break
                frontier = nxt
            if hit:
                q, c = hit, img[mouth]
                while q != mouth:
                    img[q] = c
                    adj.setdefault(q, [])
                    S.add(q)
                    q = prev[q]
                q = hit
                while q != mouth:  # rebuild adjacency along the bridge
                    adj[q] = [p for p in nbrs(q) if p in S]
                    q = prev[q]
                adj[mouth] = [p for p in nbrs(mouth) if p in S]
                mouth = hit
                bridged += 1
        # root the tree at the mouth; loops (two pieces joined twice) are cut by dropping a loop pixel with no branch
        for _ in range(100):
            parent, order, loop = {mouth: None}, [mouth], None
            for q in order:
                for p in adj[q]:
                    if p not in parent:
                        parent[p] = q
                        order.append(p)
                    elif p != parent[q] and parent.get(p) != q and loop is None:
                        loop = (q, p)
            if loop is None:
                break
            drop = min(loop, key=lambda t: (t == mouth, len(adj[t])))
            img[drop] = LAND if land[drop] else WATER
            for t in adj.pop(drop):
                adj[t].remove(drop)
            S.discard(drop)
        kids = defaultdict(list)
        for q in order[1:]:
            kids[parent[q]].append(q)
        height, wet = {}, {}
        for q in reversed(order):
            height[q] = 1 + max((height[c] for c in kids[q]), default=0)
            wet[q] = any(wet[c] for c in kids[q]) or (not kids[q] and q != mouth and dw[q] <= 1)
        q = mouth
        while kids[q]:
            q = max(kids[q], key=lambda c: height[c])
        img[q] = SOURCE
        for q in order:
            if len(kids[q]) > 1:
                main_kid = max(kids[q], key=lambda c: height[c])
                for c in kids[q]:
                    if c == main_kid:
                        continue
                    if len(kids[c]) == 1:
                        img[c] = FLOW_OUT if wet[c] else FLOW_IN
                    elif not kids[c]:
                        img[c] = LAND if land[c] else WATER  # one-pixel arm: drop it
                    else:
                        skipped += 1  # arm forks right at the junction: no valid marker spot
    return bridged, skipped


def check(img):
    """Report breaks of the vanilla rules (a junction pixel also touches its flow-in marker, so only plain pixels count)."""
    roll4 = lambda m: sum(np.roll(m, s, a) for s, a in ((1, 0), (-1, 0), (1, 1), (-1, 1)))
    r, plain = img <= 11, (img <= 11) & (img > 2)
    bad_branch = int((plain & (roll4(plain) > 2)).sum())
    block = int((r & np.roll(r, 1, 0) & np.roll(r, 1, 1) & np.roll(np.roll(r, 1, 0), 1, 1)).sum())
    mid_source = int(((img == SOURCE) & (roll4(r) > 1)).sum())
    lab, n = nd.label(r)
    greens = np.bincount(lab[img == SOURCE], minlength=n + 1)[1:]
    print(f"systems: {n}, with no green {int((greens == 0).sum())}, with >1 green {int((greens > 1).sum())}")
    dangling = int((plain & (roll4(r) == 1) & (roll4(img == WATER) == 0)).sum())
    print(f"check: plain px with >2 neighbours {bad_branch}, 2x2 blocks {block}, sources mid-river {mid_source}, "
          f"dry ends (tributary heads + rivers ending inland) {dangling}")


if __name__ == "__main__":
    main(*sys.argv[1:])
