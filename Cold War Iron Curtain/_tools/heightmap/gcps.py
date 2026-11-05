"""Build HOI4-pixel <-> lat/lon control points from victory point names. Writes gcps.json."""
import json, re, glob, numpy as np
from PIL import Image
from cities import CITIES

MAP = "map"
names = {}
for f in glob.glob("localisation/english/**/*.yml", recursive=True):
    for m in re.finditer(r'VICTORY_POINTS_(\d+):\d* "([^"]+)"', open(f, encoding="utf-8-sig", errors="ignore").read()):
        names.setdefault(m.group(2), int(m.group(1)))

def land_mask_and_ids():
    rgb = np.asarray(Image.open(f"{MAP}/provinces.bmp").convert("RGB")).astype(np.int32)
    key = (rgb[..., 0] << 16) | (rgb[..., 1] << 8) | rgb[..., 2]
    lut, kinds = {}, {}
    for line in open(f"{MAP}/definition.csv", encoding="utf-8", errors="ignore"):
        p = line.strip().split(";")
        if len(p) < 5 or not p[0].isdigit():
            continue
        k = (int(p[1]) << 16) | (int(p[2]) << 8) | int(p[3])
        lut[k] = int(p[0]); kinds[int(p[0])] = p[4]
    uk, inv = np.unique(key, return_inverse=True)
    ids = np.array([lut.get(int(k), 0) for k in uk])[inv].reshape(key.shape)
    return ids, kinds

if __name__ == "__main__":
    ids, kinds = land_mask_and_ids()
    h = ids.shape[0]
    out = []
    for name, (lat, lon) in CITIES.items():
        pid = names.get(name)
        if pid is None:
            continue
        ys, xs = np.nonzero(ids == pid)
        if len(xs) == 0:
            continue
        out.append({"name": name, "x": float(xs.mean()), "y": float(ys.mean()), "lat": lat, "lon": lon})
    json.dump(out, open("_tools/heightmap/gcps.json", "w"), indent=1)
    print(len(out), "of", len(CITIES), "matched;", "missing:", sorted(set(CITIES) - {o["name"] for o in out}))
