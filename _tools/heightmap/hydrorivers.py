"""Natural Earth rivers + the smaller rivers it lacks (Dong Nai...) from HydroRIVERS, as one geojson for rivers.py.

Run from the mod root:
    python _tools/heightmap/hydrorivers.py <HydroRIVERS_v10.shp> <ne_10m_rivers_lake_centerlines.geojson> <out.geojson>
                                           [min_upland_km2=8000] [min_discharge_m3s=120]
HydroRIVERS (Lehner & Grill 2013, HydroSHEDS, attribution required) reaches with an upstream basin >= min_upland (and
>= MIN_FLOW mean flow) or a mean discharge >= min_discharge are added, unless most of the reach lies within NEAR
degrees of a Natural Earth river
(the same river, already drawn with its curated name and width). Added reaches are "River" with a scalerank from
discharge, so rivers.py draws them after, and narrower than, Natural Earth's; they stop where they meet one (flow-in).
Needs pyshp (pip install pyshp).
"""
import json, sys, numpy as np
from collections import defaultdict
import shapefile
from scipy.spatial import cKDTree

MIN_FLOW = 15  # m3/s: a big basin with less mean flow is a dry wadi (Sahel, Arabia), not a river line on the map
NEAR = 0.12  # degrees (~13 km): a reach mostly this close to a Natural Earth river is that river


def rank(dis):
    """scalerank for rivers.width(): >= 3000 m3/s 6, >= 1000 7, else 8+ (narrowest)."""
    return 6.0 if dis >= 3000 else 7.0 if dis >= 1000 else 8.0 if dis >= 300 else 9.0


def ne_vertices(ne):
    pts = []
    for f in ne["features"]:
        g = f["geometry"]
        if not g:
            continue
        for part in g["coordinates"] if g["type"] == "MultiLineString" else [g["coordinates"]]:
            c = np.array(part, np.float64)
            for a, b in zip(c[:-1], c[1:]):  # densify to ~2 km so long straight segments still count
                n = max(1, int(np.abs(b - a).max() / 0.02))
                pts.append(a + (b - a) * (np.arange(n)[:, None] / n))
            pts.append(c[-1:])
    return np.concatenate(pts)


def lines(reaches):
    """Join reaches (id -> (coords, next_down, discharge)) into whole river lines, split at confluences like Natural
    Earth's: a reach continues into its next_down while that one has no other selected upstream. Joined first because
    rivers.py orients each line by the DEM at its two ends, which is noise on a 2 km reach in flat country."""
    ups = defaultdict(int)
    for _, (_, nxt, _) in reaches.items():
        if nxt in reaches:
            ups[nxt] += 1
    for h in (i for i in reaches if ups[i] != 1):  # sources and reaches just below a confluence start a line
        pts, i = [], h
        while True:
            c, nxt, dis = reaches[i]
            pts.append(c if not pts else c[1:])
            if nxt not in reaches or ups[nxt] != 1:
                break
            i = nxt
        yield np.concatenate(pts), dis  # discharge of the most downstream reach


def main(shp, ne_path, out, min_upland=8000, min_dis=120):
    min_upland, min_dis = float(min_upland), float(min_dis)
    ne = json.load(open(ne_path, encoding="utf-8"))
    tree = cKDTree(ne_vertices(ne))
    r = shapefile.Reader(shp)
    reaches, skipped = {}, 0
    for sr in r.iterShapeRecords(fields=["HYRIV_ID", "NEXT_DOWN", "UPLAND_SKM", "DIS_AV_CMS"]):
        d = sr.record.as_dict()
        if d["DIS_AV_CMS"] < min_dis and (d["UPLAND_SKM"] < min_upland or d["DIS_AV_CMS"] < MIN_FLOW):
            continue
        c = np.asarray(sr.shape.points, np.float64)
        if len(c) < 2:
            continue
        dist, _ = tree.query(c, distance_upper_bound=NEAR)
        if np.isfinite(dist).mean() > 0.5:
            skipped += 1
            continue
        reaches[d["HYRIV_ID"]] = (c, d["NEXT_DOWN"], d["DIS_AV_CMS"])
    added = [{"type": "Feature", "geometry": {"type": "LineString", "coordinates": c.round(5).tolist()},
              "properties": {"featurecla": "River", "scalerank": rank(dis), "name": "", "source": "HydroRIVERS"}}
             for c, dis in lines(reaches)]
    ne["features"] += added
    json.dump(ne, open(out, "w", encoding="utf-8"))
    print(f"HydroRIVERS reaches kept {len(reaches)} as {len(added)} lines, skipped as Natural Earth duplicates {skipped}")


if __name__ == "__main__":
    assert rank(5000) == 6 and rank(500) == 8 and rank(50) == 9
    sq = lambda *p: np.array(p, float)
    t = {1: (sq([0, 0], [1, 0]), 2, 5), 2: (sq([1, 0], [2, 0]), 4, 9), 3: (sq([1, 1], [1.5, 0.5]), 4, 3), 4: (sq([2, 0], [3, 0]), 0, 20)}
    got = sorted((len(c), d) for c, d in lines(t))
    assert got == [(2, 3), (2, 20), (3, 9)], got  # 1+2 joined; 3 joins at 4, which starts after the confluence
    main(*sys.argv[1:6])
