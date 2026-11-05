"""Make province terrain (definition.csv, what combat uses) agree with the drawn terrain.bmp where it clearly doesn't.

Only the clear desert cases; the rest of the gameplay terrain is hand-tuned and stays:
- plains/forest/jungle provinces drawn >= SHARE as desert (sand, rocky, red desert, desert hills) -> desert
- desert provinces drawn >= SHARE as green land (grass, farms, villages, parkland, forest, jungle, towns) -> plains
Run from the mod root:  python _tools/heightmap/terrain_sync.py [--write]
"""
import sys, numpy as np
from PIL import Image
from gcps import land_mask_and_ids

SHARE = 0.75
DES = [3, 7, 24, 8]
GREEN = [0, 5, 12, 29, 30, 32, 33, 36, 1, 4, 21, 13]


def changes(ids, t, defs):
    n = int(ids.max()) + 1
    tot = np.maximum(np.bincount(ids.ravel(), minlength=n), 1)
    des = np.bincount(ids[np.isin(t, DES)], minlength=n) / tot
    grn = np.bincount(ids[np.isin(t, GREEN)], minlength=n) / tot
    out = {p: "desert" for p, g in defs.items() if g in ("plains", "forest", "jungle") and des[p] >= SHARE}
    out.update({p: "plains" for p, g in defs.items() if g == "desert" and grn[p] >= SHARE})
    return out


def main(write):
    ids, _ = land_mask_and_ids()
    t = np.array(Image.open("map/terrain.bmp"))
    raw = open("map/definition.csv", "rb").read()
    nl = b"\r\n" if b"\r\n" in raw else b"\n"
    rows = [l.split(b";") for l in raw.split(nl)]
    defs = {int(p[0]): p[6].decode() for p in rows if len(p) > 6 and p[0].isdigit() and p[4] == b"land"}
    want = changes(ids, t, defs)
    for p in rows:
        if len(p) > 6 and p[0].isdigit() and int(p[0]) in want:
            p[6] = want[int(p[0])].encode()
    print("to desert:", sum(v == "desert" for v in want.values()), "to plains:", sum(v == "plains" for v in want.values()))
    if write:
        open("map/definition.csv", "wb").write(nl.join(b";".join(p) for p in rows))


if __name__ == "__main__":
    ids = np.array([[1, 1, 2, 2]]); t = np.array([[3, 3, 0, 0]])
    assert changes(ids, t, {1: "plains", 2: "desert"}) == {1: "desert", 2: "plains"}
    main("--write" in sys.argv[1:])
