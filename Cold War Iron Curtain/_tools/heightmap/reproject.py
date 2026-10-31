"""One-shot move of the map from the old hand-warped 5632x2048 layout to Patterson 4864x2560 (proj.py).

Run from the mod root:  python _tools/heightmap/reproject.py <old_warp.npz> <out_dir>
Reads the old files from git (SRC_REF), so it can be re-run. Each old pixel's lon/lat comes from the old warp (the
same one the heightmap tools used), so provinces land where the real geography is.
Writes into the mod:
  map/provinces.bmp      old provinces resampled; pixels the old map never covered get NEW_RGB (filled by newareas.py)
  map/cities.bmp         city-mesh palette map, resampled
  map/buildings.txt, unitstacks.txt, weatherpositions.txt, ambient_object.txt, adjacencies.csv: x/z moved
and <out_dir>/newarea.npy (bool mask of the uncovered pixels).
"""
import io, subprocess, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
import proj

SRC_REF = "development-branch"
GIT_ROOT = "Cold War Iron Curtain/"
VANILLA = "F:/SteamLibrary/steamapps/common/Hearts of Iron IV/map/"
NEW_RGB = (1, 2, 3)  # placeholder colour for not-yet-provinced pixels; not in definition.csv
FILL_PX = 4          # gaps up to this far from a resampled pixel take its value; farther = new area


def git_bytes(path):
    return subprocess.run(["git", "show", f"{SRC_REF}:{GIT_ROOT}{path}"], capture_output=True, check=True).stdout


def old_text(path):
    try:
        return git_bytes(path).decode("utf-8", "surrogateescape")
    except subprocess.CalledProcessError:  # the mod never shipped it: vanilla's
        return open(VANILLA + path.split("map/", 1)[1], encoding="utf-8", errors="surrogateescape").read()


class Mover:
    """old game (x, z) -> new game (x, z) through the old warp, bilinear on unit vectors so the seam is safe."""

    def __init__(self, lo, la):
        self.H, self.W = lo.shape
        r = np.radians(lo.astype(np.float64))
        self.c, self.s, self.la = np.cos(r), np.sin(r), la.astype(np.float64)

    def lonlat_img(self, x, y):
        x, y = np.asarray(x, np.float64) - .5, np.asarray(y, np.float64) - .5
        x0, y0 = np.floor(x).astype(int), np.clip(np.floor(y).astype(int), 0, self.H - 2)
        fx, fy = x - x0, np.clip(y - y0, 0, 1)
        def bil(a):
            g = lambda yy, xx: a[yy, xx % self.W]
            return (g(y0, x0) * (1 - fx) + g(y0, x0 + 1) * fx) * (1 - fy) + (g(y0 + 1, x0) * (1 - fx) + g(y0 + 1, x0 + 1) * fx) * fy
        return np.degrees(np.arctan2(bil(self.s), bil(self.c))), bil(self.la)

    def __call__(self, x, z):
        lo, la = self.lonlat_img(x, self.H - np.asarray(z, np.float64))
        nx, ny = proj.to_px(lo, la)
        return nx, proj.H - ny


def inverse_field(lo, la):
    """For every new pixel, the old pixel (float x, y) it comes from, and a mask of new pixels the old map never covered.
    Splat old pixel coordinates onto the new grid, then normalised gaussian smoothing: the warp is smooth, so this is a
    sub-pixel inverse without per-pixel jitter."""
    H0, W0 = lo.shape
    tx, ty = proj.to_px(lo, la)
    tx, ty = np.floor(tx).astype(np.int64) % proj.W, np.floor(ty).astype(np.int64)
    ok = (ty >= 0) & (ty < proj.H)
    yy, xx = np.mgrid[0:H0, 0:W0]
    ang = (xx + .5) * (2 * np.pi / W0)  # old x as an angle: averages safely across the seam
    idx = ty[ok] * proj.W + tx[ok]
    n = proj.H * proj.W
    acc = [np.bincount(idx, weights=v[ok], minlength=n).reshape(proj.H, proj.W)
           for v in (np.ones_like(ang), np.cos(ang), np.sin(ang), (yy + .5).astype(np.float64))]
    P, S = 16, 1.2
    sm = lambda a: nd.gaussian_filter(np.concatenate([a[:, -P:], a, a[:, :P]], 1), S)[:, P:-P]
    cnt, c, s, y = (sm(a) for a in acc)
    covered = cnt > 0.05
    # past the old edge: hold the nearest covered value (only used for pixels inside FILL_PX)
    d, (iy, ix) = nd.distance_transform_edt(~covered, return_indices=True)
    cnt, c, s, y = (np.where(covered, a, a[iy, ix]) for a in (cnt, c, s, y))
    sx = (np.arctan2(s, c) % (2 * np.pi)) * (W0 / (2 * np.pi))
    return sx, y / cnt, d > FILL_PX


def resample(img, field):
    """Nearest-neighbour sample of an old label/palette image through the inverse field."""
    sx, sy, _ = field
    H0, W0 = img.shape[:2]
    return img[np.clip(sy.astype(np.int64), 0, H0 - 1), sx.astype(np.int64) % W0]


def pieces(k):
    """8-connected pieces: (label image, size per label, key per label)."""
    from skimage.measure import label
    lab = label(k + 1, connectivity=2, background=0)
    sizes = np.bincount(lab.ravel())
    key_of = np.zeros(len(sizes), np.int64)
    key_of[lab.ravel()] = k.ravel()
    return lab, sizes, key_of


def despeckle(new_rgb, old_key, max_px=30):
    """Resampling crumbs: a province with more pieces than on the old map gives its smallest extra pieces (<= max_px)
    to the neighbour they touch most. Returns how many pieces moved."""
    _, s0, k0 = pieces(old_key)
    had = dict(zip(*np.unique(k0[1:], return_counts=True)))
    key = province_keys(new_rgb)
    lab, sizes, key_of = pieces(key)
    moved = 0
    by_key = {}
    for l in range(1, len(sizes)):
        by_key.setdefault(int(key_of[l]), []).append(l)
    objs = nd.find_objects(lab)
    for k, ls in by_key.items():
        extra = len(ls) - had.get(k, 1)
        if extra <= 0:
            continue
        for l in sorted(ls, key=lambda l: sizes[l])[:extra]:
            if sizes[l] > max_px:
                break
            sl = tuple(slice(max(0, s.start - 1), s.stop + 1) for s in objs[l - 1])
            m = lab[sl] == l
            ring = nd.binary_dilation(m, structure=np.ones((3, 3))) & ~m
            nb = key[sl][ring]
            nb = nb[nb != k]
            if not len(nb):
                continue
            v, c = np.unique(nb, return_counts=True)
            win = v[np.argmax(c)]
            new_rgb[sl][m] = ((win >> 16) & 255, (win >> 8) & 255, win & 255)
            key[sl][m] = win
            moved += 1
    return moved


def province_keys(rgb):
    rgb = rgb.astype(np.int64)
    return (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]


def move_lines(text, cols, mover, sep=";"):
    """move the (x, z) column pairs in cols of each data line; returns new text and count."""
    lines = text.split("\n")
    n = 0
    for i, l in enumerate(lines):
        p = l.split(sep)
        try:
            vals = [(float(p[a]), float(p[b])) for a, b in cols]
        except (ValueError, IndexError):
            continue
        for (a, b), (x, z) in zip(cols, vals):
            if x < 0 or z < 0:  # adjacencies: -1 = engine picks
                continue
            nx, nz = mover(x, z)
            dec = len(p[a].split(".")[1]) if "." in p[a] else 0
            p[a], p[b] = f"{float(nx):.{dec}f}", f"{float(nz):.{dec}f}"
        lines[i] = sep.join(p)
        n += 1
    return "\n".join(lines), n


def main(warp_npz, out_dir):
    w = np.load(warp_npz)
    lo, la = w["lo"], w["la"]
    mover = Mover(lo, la)

    field = inverse_field(lo, la)
    new_area = field[2]
    rgb = np.asarray(Image.open(io.BytesIO(git_bytes("map/provinces.bmp"))).convert("RGB"))
    key = province_keys(rgb)
    uk = np.unique(key)
    new_rgb = resample(rgb, field)
    new_rgb[new_area] = NEW_RGB
    for _ in range(3):
        print("despeckle: pieces folded into neighbours", despeckle(new_rgb, key))
    nk = province_keys(new_rgb)
    lost = np.setdiff1d(uk, nk)
    for k in lost:  # a sliver squeezed out by neighbours: put back one pixel at its old centre
        ys, xs = np.nonzero(key == k)
        i = len(ys) // 2
        nx, ny = proj.to_px(*mover.lonlat_img(xs[i] + .5, ys[i] + .5))
        new_rgb[int(ny), int(nx) % proj.W] = rgb[ys[i], xs[i]]
    nk = province_keys(new_rgb)
    assert not len(np.setdiff1d(uk, nk)), "provinces lost"
    Image.fromarray(new_rgb, "RGB").save("map/provinces.bmp")
    np.save(f"{out_dir}/newarea.npy", new_area)
    print(f"provinces: {len(uk)} kept ({len(lost)} restored by hand), new-area px {new_area.sum()}")

    # cities.bmp (palette): mod has none, so vanilla's, which matches the old layout
    cb = Image.open(VANILLA + "cities.bmp")
    pal = cb.getpalette()
    ca = np.asarray(cb)
    cnew = resample(ca, field)
    im = Image.fromarray(cnew, "P"); im.putpalette(pal); im.save("map/cities.bmp")

    for path, cols, sep in [("map/buildings.txt", [(2, 4)], ";"), ("map/unitstacks.txt", [(2, 4)], ";"),
                            ("map/weatherpositions.txt", [(1, 3)], ";"), ("map/adjacencies.csv", [(4, 5), (6, 7)], ";")]:
        txt, n = move_lines(old_text(path), cols, mover, sep)
        open(path, "w", encoding="utf-8", errors="surrogateescape", newline="").write(txt)
        print(f"{path}: {n} lines moved")

    # ambient_object.txt: 'position={ x y z }' blocks
    import re
    amb = old_text("map/ambient_object.txt")
    def rep(m):
        x, y, z = (float(v) for v in m.group(2).split())
        if x == 0 and z == 0:
            return m.group(0)
        nx, nz = mover(x, z)
        return f"{m.group(1)}{float(nx):.2f} {y:g} {float(nz):.2f} "
    amb, n = re.subn(r"(position=\{\s*)([-\d.]+\s+[-\d.]+\s+[-\d.]+)\s*", rep, amb)
    open("map/ambient_object.txt", "w", encoding="utf-8", newline="").write(amb)
    print(f"map/ambient_object.txt: {n} positions")


if __name__ == "__main__":
    main(*sys.argv[1:3])
