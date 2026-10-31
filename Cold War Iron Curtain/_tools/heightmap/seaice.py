"""Bake sea-ice freeze potential into map/terrain/fow_rgb_waterspec_a.dds (blue channel) for gfx/FX/pdxwater.shader.

Run from the mod root:  python _tools/heightmap/seaice.py <etopo.nc> <nsidc_dir> <out_dir> [worldclim_dir]
With worldclim_dir, inland water also gets a freeze potential: the share of months with a mean below -2 C (lakes, and
seas the sea-ice data doesn't reach, like Ladoga and Onega, which the mod defines as sea provinces).
nsidc_dir holds N_1979MM_concentration_v4.0 GeoTIFFs (renamed N_1979MM.tif), NSIDC G02135 polar stereographic north.
Potential = share of 1979 months with >=15% ice; blue = 255 - 72 * potential. Red/green stay 255, alpha (wave
strength) is taken from the vanilla file because the mod's copy had it at 0, which switched waves off.
"""
import glob, sys, numpy as np, tifffile
from PIL import Image
from scipy import ndimage as nd
from build import WRAP, warp
from colormap import dxt5_with_mips
from gcps import land_mask_and_ids

DDS = "map/terrain/fow_rgb_waterspec_a.dds"
VANILLA = "F:/SteamLibrary/steamapps/common/Hearts of Iron IV/map/terrain/fow_rgb_waterspec_a.dds"
SCALE = 72  # blue drop at potential 1; shader decodes (1 - b) * 255 / 72


def potential(d):
    months = sorted(glob.glob(f"{d}/N_1979??.tif"))
    assert len(months) == 12, months
    ice = sum(((a >= 150) & (a <= 1000)) | (a == 2510) for a in (tifffile.imread(f) for f in months)) / 12.0
    valid = tifffile.imread(months[0]) <= 2510  # 2530 coast / 2540 land / 2550 missing
    _, (iy, ix) = nd.distance_transform_edt(~valid, return_indices=True)
    return ice[iy, ix]  # land cells take the nearest ocean value so coastal map pixels aren't left at 0


def polar_stereo_north(lon, lat):
    """EPSG:3411 (Hughes 1980 ellipsoid, true scale 70N, lon0 -45) -> metres."""
    a, e = 6378273.0, 0.081816153
    t = lambda p: np.tan(np.pi / 4 - p / 2) / ((1 - e * np.sin(p)) / (1 + e * np.sin(p))) ** (e / 2)
    pc = np.radians(70.0)
    mc = np.cos(pc) / np.sqrt(1 - e * e * np.sin(pc) ** 2)
    rho = a * mc * t(np.radians(lat)) / t(pc)
    dl = np.radians(lon + 45.0)
    return rho * np.sin(dl), -rho * np.cos(dl)


def main(dem_path, nsidc_dir, out, wc_dir=None):
    ids, kinds = land_mask_and_ids()
    sea = np.isin(ids, [k for k, v in kinds.items() if v == "sea"])
    lake = np.isin(ids, [k for k, v in kinds.items() if v == "lake"])[::2, ::2]
    lo, la, _, _ = warp(dem_path, sea)
    lo, la, sea = lo[::2, ::2], la[::2, ::2], sea[::2, ::2]

    x, y = polar_stereo_north(lo, np.maximum(la, 0.0))
    pot = nd.map_coordinates(potential(nsidc_dir), [(5850000 - y) / 25000 - .5, (x + 3850000) / 25000 - .5],
                             order=1, mode="constant", cval=0.0)
    pot = np.where(sea & (la > 30), pot, 0.0)
    if wc_dir:  # months below -2 C (WorldClim tmin/tmax means), e.g. Ladoga ~5/12, Great Lakes ~3/12
        from weather import worldclim
        rows, cols = (90 - la) * 6 - .5, (lo + 180) % 360 * 6 - .5
        tmean = (worldclim(wc_dir, "tmin") + worldclim(wc_dir, "tmax")) / 2
        frozen = sum(nd.map_coordinates(np.nan_to_num(t, nan=99.0), [rows, cols], order=1, mode="wrap") < -2 for t in tmean) / 12.0
        pot = np.maximum(pot, np.where(sea | lake, frozen, 0.0))  # open ocean has no WorldClim data: stays NSIDC
        sea = sea | lake
    pot = nd.gaussian_filter(pot, 1.5, mode=WRAP) * sea  # soft ice edge, nothing on land

    van = np.asarray(Image.open(VANILLA).convert("RGBA"))
    rgba = np.full(van.shape, 255, np.uint8)
    rgba[..., 2] = np.clip(np.rint(255 - SCALE * pot), 0, 255)
    rgba[..., 3] = van[..., 3]
    img = Image.fromarray(rgba, "RGBA")
    img.save(f"{out}/seaice_preview.png")
    open(f"{out}/fow_rgb_waterspec_a.dds", "wb").write(dxt5_with_mips(img, open(DDS, "rb").read(128)))
    print("sea px with any ice:", int((pot > .05).sum()), "| always frozen:", int((pot > .95).sum()))


if __name__ == "__main__":
    main(*sys.argv[1:])
