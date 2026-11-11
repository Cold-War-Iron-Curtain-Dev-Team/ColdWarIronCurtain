"""Make terrain atlas tiles wrap again (map/terrain/atlas{0,1,2}.dds + atlas_normal{0,1,2}.dds).

A tile whose opposite edges don't match shows a hard line every repeat on the map. For each tile whose wrap edge differs
from its interior much more than neighbouring pixels do, the tile is cross-faded over its own margin (atlas_tiles.seamless)
and scaled back to 512 px; the normal tile gets the same treatment so relief stays aligned. Levels 1 and 2 are rebuilt
from level 0. Reads the current files, so only run it once per art drop.
Run from the mod root:  python ../_tools/heightmap/atlas_seams.py
"""
import numpy as np
from PIL import Image
from colormap import dxt5_with_mips
from atlas_tiles import seamless, put, GRID, T

MARGIN, RATIO = 48, 1.5


def seam_ratio(t):
    t = t[..., :3].astype(np.float32)
    edge = (abs(t[0] - t[-1]).mean() + abs(t[:, 0] - t[:, -1]).mean()) / 2
    inner = (abs(t[1] - t[2]).mean() + abs(t[:, 1] - t[:, 2]).mean()) / 2
    return edge / max(inner, 1.0)


def fix(t):
    s = seamless(t.astype(np.float32), MARGIN)
    return np.array(Image.fromarray(np.clip(s, 0, 255).astype(np.uint8), "RGBA").resize((T, T), Image.LANCZOS))


def main():
    files = {k: open(f"map/terrain/{k}0.dds", "rb").read() for k in ("atlas", "atlas_normal")}
    atl = {k: np.array(Image.open(f"map/terrain/{k}0.dds").convert("RGBA")) for k in files}
    tile = lambda a, k: a[k // GRID * T:(k // GRID + 1) * T, k % GRID * T:(k % GRID + 1) * T]
    bad = [k for k in range(GRID * GRID) if seam_ratio(tile(atl["atlas"], k)) > RATIO]
    for kind, a in atl.items():
        for k in bad:
            put(a, k, fix(tile(a, k)))
        full = Image.fromarray(a, "RGBA")
        for lvl in range(3):
            path = f"map/terrain/{kind}{lvl}.dds"
            hdr = open(path, "rb").read(128)  # same size, format and mip count as before
            img = full if lvl == 0 else full.resize((full.width >> lvl,) * 2, Image.LANCZOS)
            open(path, "wb").write(dxt5_with_mips(img, hdr))
    print("made seamless:", bad)


def _selfcheck():
    rng = np.random.default_rng(0)
    t = np.dstack([np.tile(np.linspace(0, 255, T), (T, 1))] * 3 + [np.full((T, T), 255.0)]).astype(np.uint8)  # ramp: hard wrap
    assert seam_ratio(t) > RATIO and seam_ratio(fix(t)) < RATIO
    n = (rng.random((T, T, 4)) * 255).astype(np.uint8)
    assert fix(n).shape == (T, T, 4)


if __name__ == "__main__":
    _selfcheck()
    main()
