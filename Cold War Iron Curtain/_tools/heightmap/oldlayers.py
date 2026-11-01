"""The pre-rebuild rasters (build.OLD_COMMIT: hand-made lake pits, lake depths, marsh, the old colormap) resampled into
the current projection, so the build tools can keep using them. Pixels the old map never showed take the nearest old
pixel (heightmap: neutral land, so no fake lake pits).

Run from the mod root:  python _tools/heightmap/oldlayers.py <old_warp.npz> <out_dir>
                   or:  python _tools/heightmap/oldlayers.py --snapshot <out_dir>
Set CWIC_OLD_LAYERS=<out_dir> when running the build tools.
--snapshot: the old warp (warp_old_5632.npz) is lost, so the committed map files (already in this projection, with the
hand-made pits, lake depths and marsh carried forward) stand in for the old layers. Marsh is un-dithered first.
"""
import io, subprocess, sys, numpy as np
from PIL import Image
from scipy import ndimage as nd
from reproject import inverse_field
from build import OLD_COMMIT
import proj

DDS = "map/terrain/colormap_rgb_cityemissivemask_a.dds"
VANILLA_FOW = "F:/SteamLibrary/steamapps/common/Hearts of Iron IV/map/terrain/fow_rgb_waterspec_a.dds"
NEUTRAL_LAND = 100


def old_bytes(path):
    return subprocess.run(["git", "show", f"{OLD_COMMIT}:./{path}"], capture_output=True, check=True).stdout


def sample(img, sx, sy, newarea):
    H0, W0 = img.shape[:2]
    out = img[np.clip(sy.astype(np.int64), 0, H0 - 1), sx.astype(np.int64) % W0]
    return out


def main(warp_npz, out):
    w = np.load(warp_npz)
    sx, sy, newarea = inverse_field(w["lo"], w["la"])
    for name in ("heightmap", "terrain", "rivers"):
        im = Image.open(io.BytesIO(old_bytes(f"map/{name}.bmp")))
        a = sample(np.asarray(im), sx, sy, newarea)
        if name == "heightmap":
            a = np.where(newarea, NEUTRAL_LAND, a).astype(np.uint8)
        elif name == "rivers":
            a = np.where(newarea, 255, a).astype(np.uint8)  # 255 = no river
        o = Image.fromarray(a, im.mode)
        if im.mode == "P":
            o.putpalette(im.getpalette())
        o.save(f"{out}/{name}.bmp")
    # colormap is half resolution: sample the field at every second pixel
    im = np.asarray(Image.open(io.BytesIO(old_bytes(DDS))).convert("RGBA"))
    hx, hy = sx[1::2, 1::2] / 2, sy[1::2, 1::2] / 2
    Image.fromarray(sample(im, hx, hy, newarea[1::2, 1::2]), "RGBA").save(f"{out}/colormap_rgb_cityemissivemask_a.png")
    # vanilla wave strength (alpha of fow_rgb_waterspec_a.dds, half resolution; vanilla layout = the old mod layout)
    van = np.asarray(Image.open(VANILLA_FOW).convert("RGBA"))[..., 3]
    Image.fromarray(sample(van, hx, hy, None), "L").save(f"{out}/waterspec_alpha.png")
    print("old layers written to", out, "| new-area px", int(newarea.sum()))


def snapshot(out):
    def git_img(path):
        return Image.open(io.BytesIO(subprocess.run(["git", "show", f"HEAD:./{path}"], capture_output=True, check=True).stdout))
    Image.fromarray(np.array(git_img("map/heightmap.bmp")), "L").save(f"{out}/heightmap.bmp")
    ter = git_img("map/terrain.bmp")
    t = np.array(ter)
    marsh = nd.uniform_filter((t == 9).astype(np.float32), 5, mode="wrap") > 0.5  # dither dots -> solid marsh again
    t[(t == 9) & ~marsh] = 0
    t[marsh & (t != 15) & (t != 14)] = 9
    o = Image.fromarray(t, "P"); o.putpalette(ter.getpalette()); o.save(f"{out}/terrain.bmp")
    ri = git_img("map/rivers.bmp"); o = Image.fromarray(np.array(ri), "P"); o.putpalette(ri.getpalette()); o.save(f"{out}/rivers.bmp")
    git_img(DDS).convert("RGBA").save(f"{out}/colormap_rgb_cityemissivemask_a.png")
    git_img("map/terrain/fow_rgb_waterspec_a.dds").convert("RGBA").getchannel("A").save(f"{out}/waterspec_alpha.png")
    print("old layers (snapshot of HEAD) written to", out)


if __name__ == "__main__":
    snapshot(sys.argv[2]) if sys.argv[1] == "--snapshot" else main(*sys.argv[1:3])
