"""Even out the brightness of the terrain atlas tiles (map/terrain/atlas0-2.dds, a 5x5 grid at 3 resolutions).

The atlas' green tiles average ~50-75 luminance against ~140-170 for its deserts; a single shader gain
(TERRAIN_ATLAS_GAIN) can't fix that, it lifts the deserts to near white along with the greens. Each tile's RGB is
scaled so its mean luminance becomes TARGET(lum): the spread shrinks to ~40% around a vanilla-like level, the detail
inside a tile keeps its contrast, alpha is untouched. Reads the atlas from SOURCE (git), so reruns don't stack.
Run from the mod root:  python _tools/heightmap/atlas_levels.py   (then TERRAIN_ATLAS_GAIN = 1.0 in gfx/FX/constants.fxh)
"""
import io, subprocess, numpy as np
from PIL import Image
from colormap import dxt5_with_mips

SOURCE = "7ef2d2164e"  # last commit that changed the atlas
GRID = 5
LUM = np.array([0.299, 0.587, 0.114])


def target(lum):
    return 128 + 0.4 * (lum - 90)


def gains(a0):
    t = a0.shape[0] // GRID
    out = {}
    for i in range(GRID * GRID):
        y, x = divmod(i, GRID)
        lum = (a0[y * t:(y + 1) * t, x * t:(x + 1) * t, :3] @ LUM).mean()
        out[i] = target(lum) / max(lum, 1)
    return out


def apply(a, g):
    a = a.astype(np.float32).copy()
    t = a.shape[0] // GRID
    for i, k in g.items():
        y, x = divmod(i, GRID)
        a[y * t:(y + 1) * t, x * t:(x + 1) * t, :3] *= k
    return Image.fromarray(np.clip(np.rint(a), 0, 255).astype(np.uint8), "RGBA")


def main():
    src = {n: subprocess.check_output(["git", "show", f"{SOURCE}:./map/terrain/{n}.dds"]) for n in ("atlas0", "atlas1", "atlas2")}
    g = gains(np.asarray(Image.open(io.BytesIO(src["atlas0"])).convert("RGBA")).astype(np.float32))
    for n, raw in src.items():
        img = apply(np.asarray(Image.open(io.BytesIO(raw)).convert("RGBA")), g)
        open(f"map/terrain/{n}.dds", "wb").write(dxt5_with_mips(img, raw[:128]))
    print("tile gains:", {i: round(float(k), 2) for i, k in g.items()})


if __name__ == "__main__":
    assert abs(target(90) - 128) < 1e-9 and target(50) < target(160) < 160  # darkest up, brightest down, order kept
    a = np.full((10, 10, 4), 50, np.uint8)
    out = np.asarray(apply(a, gains(a.astype(np.float32))))
    assert abs(out[..., :3].mean() - target(50)) < 1 and (out[..., 3] == 50).all()
    main()
