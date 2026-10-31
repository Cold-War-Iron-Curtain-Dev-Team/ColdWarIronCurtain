# Rebuild every map layer from real data in the current projection (proj.py). Run from anywhere:
#   bash _tools/heightmap/rebuild_all.sh <data_dir>
# data_dir holds dem/etopo2.nc, lakes, glaciers, bm, ghs, seaice, wc, rivers, ibtracs and warp_old_5632.npz (old-layout warp).
set -e -o pipefail
cd "$(dirname "$0")/../.."
export PYTHONPATH=_tools/heightmap
S="${1:?data dir}"; O="$S/out_patterson"; D="$S/dem/etopo2.nc"; GHS="$S/ghs/GHS_POP_E1975_GLOBE_R2023A_4326_30ss_V1_0.tif.ovr"
mkdir -p "$O" "$S/old_patterson"
export CWIC_OLD_LAYERS="$S/old_patterson"
py _tools/heightmap/oldlayers.py "$S/warp_old_5632.npz" "$CWIC_OLD_LAYERS"
py -c "import numpy as np, proj; lo, la = proj.grid(); np.savez(r'$S/warp_patterson.npz', lo=lo, la=la)"
echo build; py _tools/heightmap/build.py "$D" "$O" "$S/lakes" "$S/glaciers" | tail -1; cp "$O"/{heightmap,world_normal,terrain}.bmp map/
echo colormap; py _tools/heightmap/colormap.py "$D" "$S/bm/world.200407.jpg" "$O" "$GHS" | tail -1; cp "$O/colormap_rgb_cityemissivemask_a.dds" map/terrain/
echo terrainmap; py _tools/heightmap/terrainmap.py "$D" "$GHS" "$O" >/dev/null; cp "$O/terrain.bmp" map/
echo trees; py _tools/heightmap/trees.py "$D" "$O" >/dev/null; cp "$O/trees.bmp" map/; cp "$O/Tree_season.bmp" map/terrain/
echo water; py _tools/heightmap/water.py "$D" "$O" >/dev/null; cp "$O"/colormap_water_{0,1,2}.dds map/terrain/
echo seaice; py _tools/heightmap/seaice.py "$D" "$S/seaice" "$O" >/dev/null; cp "$O/fow_rgb_waterspec_a.dds" map/terrain/
echo weather; py _tools/heightmap/weather.py "$D" "$S/wc" --write | tail -1
echo rivers; py _tools/heightmap/rivers.py "$D" "$S/rivers/ne_10m_rivers_lake_centerlines.geojson" "$O" | tail -3; cp "$O/rivers.bmp" map/rivers.bmp
echo storms; py _tools/heightmap/storms.py "$S/warp_patterson.npz" "$S/ibtracs/ibtracs.since1980.list.v04r01.csv" "$O" | tail -1; cp "$O/cwic_cyclone.dds" gfx/particles/
echo positions; py _tools/heightmap/positions.py "$S/warp_patterson.npz" --write
echo ALL-DONE
