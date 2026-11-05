"""Bake gfx/particles/cwic_cyclone.dds for the CwicCyclone particle effect (gfx/FX/particle.shader).

Run from the mod root:  python _tools/heightmap/storms.py <warp.npz> <ibtracs.csv> <out_dir>
2048x1024 atlas:
- left half: a tropical cyclone seen from above (eye, eyewall, two main rain bands), northern-hemisphere spin; the
  shader mirrors it south of the equator
- right half, top 1024xMH rows: red = chance that a heavy-storm province shows a cyclone, from IBTrACS days per year
  with a tropical storm, 0 on land. The shader samples it at the particle centre.
Also prints CWIC_EQUATOR_Z for the shader (world z of the equator, median over the map).
"""
import sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from colormap import dds_header, dxt5_with_mips
from gcps import land_mask_and_ids
from weather import cyclone_days
import proj

S, MW = 1024, 1024             # sprite size, mask width
MH = round(MW * proj.H / proj.W)  # mask rows (539 for 4864x2560); must match the shader
FULL_DAYS = 4.0               # storm days per year that give the top chance (Philippine Sea peaks ~7 after smoothing)
TOP = 1.0                     # top chance: every heavy storm in typhoon alley is a cyclone (heavy storms are rare enough)


def sprite(seed=1):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:S, 0:S]
    x, y = (xx - S / 2 + .5) / (S / 2), -(yy - S / 2 + .5) / (S / 2)  # y up, so theta runs counter-clockwise
    r, th = np.hypot(x, y), np.arctan2(y, x)

    def fbm(*sig):
        f = sum(nd.gaussian_filter(rng.standard_normal((S, S)), s, mode="wrap") * s for s in sig)
        return (f - f.mean()) / f.std()

    n1, n2 = fbm(64, 24), fbm(10, 5)
    # arms follow theta = c - k ln r: moving inward they turn counter-clockwise, like northern-hemisphere inflow
    arms = 0.5 + 0.5 * np.cos(2 * (th + 3.0 * np.log(r + 0.03)) + 0.6 * n1)
    bands = arms ** 3 * np.clip((1.05 - r) / 0.55, 0, 1) * np.clip((r - 0.1) / 0.2, 0, 1)
    core = np.exp(-(r / 0.3) ** 2)
    wall = np.exp(-((r - 0.075) / 0.035) ** 2)
    eye = np.clip((r - 0.035) / 0.035, 0, 1)
    d = (core + 1.2 * bands + 0.4 * wall) * eye * (0.88 + 0.12 * n2) * (0.85 + 0.2 * n1)
    d = nd.gaussian_filter(d, 2.0)
    a = np.clip(1.3 * d, 0, 1) * np.clip((0.97 - r) / 0.12, 0, 1)
    shade = np.clip(0.7 + 0.3 * d + 0.03 * n2, 0, 1)
    rgb = np.stack([shade * 246, shade * 248, shade * 252], -1)
    out = np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8)
    assert out[S // 2, S // 2, 3] < 40 and out[0, 0, 3] == 0 and out[S // 2, int(S * .62), 3] > 150  # eye clear, edge empty, core dense
    return out


def mask(warp_npz, ibtracs):
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    H, W = sea.shape
    w = np.load(warp_npz)
    lo, la = w["lo"], w["la"]
    days = cyclone_days(ibtracs).sum(0)  # (180, 360) per year
    v = nd.map_coordinates(days, [90 - la - .5, (lo + 180) % 360 - .5], order=1, mode="wrap")
    chance = np.clip(v / FULL_DAYS, 0, 1) * TOP * sea
    small = nd.zoom(chance, (MH / H, MW / W), order=1)[:MH, :MW]
    seafrac = nd.zoom(sea.astype(np.float32), (MH / H, MW / W), order=1)[:MH, :MW]
    small = np.where(seafrac > 0.5, small, 0.0)
    # equator: per column the first row from the top where latitude goes below 0
    rows = (la < 0).argmax(0)
    eq_z = H - np.median(rows)
    return small, eq_z


def main(warp_npz, ibtracs, out):
    atlas = np.zeros((1024, 2048, 4), np.uint8)
    atlas[:, :S] = sprite()
    m, eq_z = mask(warp_npz, ibtracs)
    atlas[:MH, 1024:1024 + MW, 0] = np.rint(m * 255)
    atlas[:MH, 1024:1024 + MW, 3] = 255
    img = Image.fromarray(atlas, "RGBA")
    img.save(f"{out}/cwic_cyclone_preview.png")
    open(f"{out}/cwic_cyclone.dds", "wb").write(dxt5_with_mips(img, dds_header(img)))
    print(f"mask texels with a chance: {(m > 0.02).sum()}, max {m.max():.2f} | CWIC_EQUATOR_Z = {eq_z:.0f}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
