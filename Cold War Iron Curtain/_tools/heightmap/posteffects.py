"""Reproject vanilla gfx/posteffect_volumes.txt (regional colour grading boxes) onto the current map projection.

Run from the mod root:  python _tools/heightmap/posteffects.py <vanilla_gfx/posteffect_volumes.txt> <warp_old_5632.npz>
Vanilla places each posteffect_volume box (position = centre x y z, size = x y z extents) in its 5632x2048 map; every
box's footprint goes through lon/lat (old-layout warp) to the bounding box of the same ground in the current map.
Height (y) and fade distances stay. Writes gfx/posteffect_volumes.txt.
"""
import re, sys, numpy as np
import proj


def main(src, warp):
    d = np.load(warp); lo, la = d["lo"], d["la"]
    H0, W0 = lo.shape
    t = open(src, "rb").read().decode("utf-8")

    def box(m):
        body = m.group(0)
        p = re.search(r"position\s*=\s*\{\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\}", body)
        s = re.search(r"size\s*=\s*\{\s*([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s*\}", body)
        if not (p and s):
            return body
        cx, cy, cz = map(float, p.groups()); sx, sy, sz = map(float, s.groups())
        xs = np.clip(np.linspace(cx - sx / 2, cx + sx / 2, 40), 0, W0 - 1).astype(int)
        rows = np.clip(H0 - 1 - np.linspace(cz - sz / 2, cz + sz / 2, 40), 0, H0 - 1).astype(int)
        X, Y = proj.to_px(lo[np.ix_(rows, xs)], la[np.ix_(rows, xs)])
        X = np.unwrap(X.ravel() / proj.W * 2 * np.pi) / (2 * np.pi) * proj.W  # boxes crossing the seam stay in one piece
        z = proj.H - Y.ravel()
        nx, nz = (X.min() + X.max()) / 2 % proj.W, (z.min() + z.max()) / 2
        body = body[:p.start()] + f"position = {{ {nx:.1f} {cy:.1f} {nz:.1f} }}" + body[p.end():]
        s = re.search(r"size\s*=\s*\{[^}]*\}", body)
        return body[:s.start()] + f"size = {{ {X.max() - X.min():.1f} {sy:.1f} {z.max() - z.min():.1f} }}" + body[s.end():]

    # only uncommented volume blocks (a commented one starts with '#')
    out, n = re.subn(r"(?m)^[ \t]*posteffect_volume\s*=\s*\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", box, t)
    # the Patterson map adds Antarctica (south of 62S): winter grading over the whole band
    _, ytop = proj.to_px(0, -62.0)
    z1 = proj.H - float(ytop)
    ant = ("\n\tposteffect_volume = {\n\t\tname = cwic_antarctica\n\t\tposteffect_values_day = winter_values_day\n"
           "\t\tposteffect_values_night = winter_values_night\n"
           f"\t\tposition = {{ {proj.W / 2:.1f} 300.0 {z1 / 2:.1f} }}\n\t\tsize = {{ {proj.W:.1f} 800.0 {z1:.1f} }}\n"
           "\t\tfade_distance = 60.0\n\t}\n")
    k = out.rstrip().rfind("}")  # closing brace of posteffect_volumes
    out = out[:k] + ant + out[k:]
    head = "# CWIC: vanilla volumes reprojected onto the Patterson map by _tools/heightmap/posteffects.py\n"
    open("gfx/posteffect_volumes.txt", "wb").write((head + out).encode("utf-8"))
    print(f"{n} volumes reprojected")


if __name__ == "__main__":
    main(*sys.argv[1:])
