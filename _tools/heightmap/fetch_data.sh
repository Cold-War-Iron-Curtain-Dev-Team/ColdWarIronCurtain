# Download every public dataset rebuild_all.sh reads (~750 MB) into <data_dir>, laid out the way it expects.
#   bash ../_tools/heightmap/fetch_data.sh <data_dir>
# Re-runs skip files already there. Keep data_dir outside the git repo.
set -e -o pipefail
S="${1:?data dir}"
get() { [ -s "$2" ] || { mkdir -p "$(dirname "$2")"; echo "get $(basename "$2")"; curl -fsSL --retry 3 -o "$2.part" "$1" && mv "$2.part" "$2"; }; }
NE=https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson
BM=https://eoimages.gsfc.nasa.gov/images/imagerecords

# ETOPO1 at 2 arc-minutes, netCDF3 (latitude, longitude, altitude) from ERDDAP
get "https://upwell.pfeg.noaa.gov/erddap/griddap/etopo180.nc?altitude%5B(-90.0):2:(90.0)%5D%5B(-180.0):2:(180.0)%5D" "$S/dem/etopo2.nc"
get "$NE/ne_10m_lakes.geojson" "$S/lakes/ne_10m_lakes.geojson"
get "$NE/ne_10m_lakes_europe.geojson" "$S/lakes/ne_10m_lakes_europe.geojson"
get "$NE/ne_10m_lakes_north_america.geojson" "$S/lakes/ne_10m_lakes_north_america.geojson"
get "$NE/ne_10m_geography_marine_polys.geojson" "$S/marine/ne_10m_geography_marine_polys.geojson"  # sea colours (water.py)
get "$NE/ne_10m_glaciated_areas.geojson" "$S/glaciers/ne_10m_glaciated_areas.geojson"
get "$NE/ne_10m_rivers_lake_centerlines.geojson" "$S/rivers/ne_10m_rivers_lake_centerlines.geojson"
get "$NE/ne_10m_land.geojson" "$S/land/ne_10m_land.geojson"   # arctic_coast.py
# HydroRIVERS v1.0 (Lehner & Grill 2013, HydroSHEDS; attribution required): every river reach with discharge, for the
# smaller rivers Natural Earth lacks (hydrorivers.py); ~540 MB zip
get "https://data.hydrosheds.org/file/HydroRIVERS/HydroRIVERS_v10_shp.zip" "$S/hydrorivers/HydroRIVERS_v10_shp.zip"
[ -n "$(ls "$S"/hydrorivers/*/*.shp "$S"/hydrorivers/*.shp 2>/dev/null)" ] || unzip -qn "$S/hydrorivers/HydroRIVERS_v10_shp.zip" -d "$S/hydrorivers"
# Blue Marble Next Generation 2004 (no snow, shallow water): June-August are averaged without snow by colormap.py; July alone is what terrainmap.py classifies on
get "$BM/76000/76487/world.200406.3x21600x10800.jpg" "$S/bm/world.200406.jpg"
get "$BM/74000/74117/world.200408.3x21600x10800.jpg" "$S/bm/world.200408.jpg"
get "$BM/74000/74092/world.200407.3x21600x10800.jpg" "$S/bm/world.200407.jpg"
# GHS-POP 1975, 30 arc-seconds
get "https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E1975_GLOBE_R2023A_4326_30ss/V1-0/GHS_POP_E1975_GLOBE_R2023A_4326_30ss_V1_0.zip" "$S/ghs/ghs.zip"
[ -n "$(ls "$S"/ghs/*.tif 2>/dev/null)" ] || unzip -oq "$S/ghs/ghs.zip" -d "$S/ghs"
# WorldClim 2.1, 10 arc-minutes
for v in tmin tmax prec; do get "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_$v.zip" "$S/wc/$v.zip"; unzip -qn "$S/wc/$v.zip" -d "$S/wc"; done
get "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_10m_wind.zip" "$S/wcwind/wind.zip"; unzip -qn "$S/wcwind/wind.zip" -d "$S/wcwind"
get "https://downloads.psl.noaa.gov/Datasets/ncep.reanalysis.derived/surface/wspd.mon.ltm.nc" "$S/ncep/wspd.mon.ltm.nc"
get "https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r01/access/csv/ibtracs.since1980.list.v04r01.csv" "$S/ibtracs/ibtracs.since1980.list.v04r01.csv"
# NSIDC sea ice index (G02135) monthly concentration 1979, renamed to <pole>_1979MM.tif (seaice.py)
M=(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec)
for i in $(seq 1 12); do mm=$(printf %02d $i)
  for pole in N S; do dir=$([ $pole = N ] && echo north || echo south)
    get "https://noaadata.apps.nsidc.org/NOAA/G02135/$dir/monthly/geotiff/${mm}_${M[$((i-1))]}/${pole}_1979${mm}_concentration_v4.0.tif" "$S/seaice/${pole}_1979${mm}.tif"
  done
done
echo FETCH-DONE
