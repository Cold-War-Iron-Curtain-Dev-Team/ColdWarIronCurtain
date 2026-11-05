"""Map border textures (map/terrain/border_<kind>_<zoom>.dds), drawn from a cross-section profile.

gfx/FX/border.shader samples tex2D(uv.y * BORDER_TILE, uv.x): image x runs along the border, y across it; colour and
alpha are used as-is. Zoom 0 is the closest camera. Uncompressed BGRA with a full mip chain like vanilla's.
  country     solid dark core with a soft dark halo
  state       dark dashed line (gaps stay visible, so it never reads as a country border)
  province    thin, clearly visible line
  impassable  rust-brown band with diagonal hatching and dark rims, the same at every zoom (was red bar / vanilla teeth)
Run from the mod root:  python _tools/heightmap/borders.py
"""
import struct, sys, numpy as np
from PIL import Image

SIZES = {"country": [(256, 128), (128, 64), (64, 32)], "state": [(128, 64), (64, 32), (32, 16)],
         "province": [(64, 32), (32, 16), (16, 8)], "impassable": [(128, 64), (64, 32), (32, 16)]}
SS = 8  # supersampling: edges are anti-aliased, not stair-stepped


def band(v, a, b, soft=0.02):
    """1 inside [a, b] across the border, smooth falloff `soft` wide."""
    return np.clip((v - a) / soft + 0.5, 0, 1) * np.clip((b - v) / soft + 0.5, 0, 1)


def texture(kind, w, h):
    u = (np.arange(w * SS) + 0.5) / (w * SS)
    v = (np.arange(h * SS) + 0.5) / (h * SS)
    U, V = np.meshgrid(u, v)
    rgb = np.zeros(U.shape + (3,))
    a = np.zeros(U.shape)

    def lay(alpha, colour):  # paint over what is below
        nonlocal rgb, a
        rgb = rgb * (1 - alpha[..., None]) + np.array(colour, float) / 255 * alpha[..., None]
        a = a + alpha * (1 - a)

    if kind == "country":
        lay(band(V, 0.26, 0.74, 0.05) * 0.45, (20, 20, 24))   # soft dark halo, no hard edge
        lay(band(V, 0.36, 0.64, 0.025), (26, 26, 30))         # solid core
    elif kind == "state":
        dash = band((U * 2) % 1, 0.08, 0.72, 0.03)            # 2 dashes per tile
        lay(band(V, 0.4, 0.6, 0.03) * (0.6 + 0.35 * dash), (22, 22, 24))
    elif kind == "province":
        lay(band(V, 0.42, 0.58, 0.03) * 0.62, (28, 28, 28))
    elif kind == "impassable":
        hatch = band(((U * w / h * 2 + V) * 2) % 1, 0.0, 0.45, 0.06)  # 45-degree stripes
        lay(band(V, 0.27, 0.73, 0.03) * 0.5, (30, 26, 22))
        body = band(V, 0.3, 0.7)
        lay(body * 0.95, (118, 66, 40))
        lay(body * hatch * 0.85, (186, 132, 88))
        lay(band(V, 0.29, 0.34), (34, 22, 16))           # dark rims keep it crisp
        lay(band(V, 0.66, 0.71), (34, 22, 16))
    out = np.concatenate([rgb, a[..., None]], -1).reshape(h, SS, w, SS, 4).mean((1, 3))
    return Image.fromarray(np.clip(np.rint(out * 255), 0, 255).astype(np.uint8), "RGBA")


def write_dds(img, path):
    """Uncompressed 32-bit BGRA DDS with a full mip chain (box filtered)."""
    w, h = img.size
    mips, levels, cur = 0, [], np.asarray(img).astype(np.float32)
    while True:
        levels.append(np.clip(np.rint(cur), 0, 255).astype(np.uint8)[..., [2, 1, 0, 3]].tobytes())
        mips += 1
        if cur.shape[0] == 1 and cur.shape[1] == 1:
            break
        hh, ww = max(cur.shape[0] // 2, 1), max(cur.shape[1] // 2, 1)
        cur = cur[:hh * 2 if cur.shape[0] > 1 else 1, :ww * 2 if cur.shape[1] > 1 else 1]
        cur = cur.reshape(hh, -1, ww, cur.shape[1] // ww, 4).mean((1, 3))
    hdr = struct.pack("<4s7I44x", b"DDS ", 124, 0x1 | 0x2 | 0x4 | 0x8 | 0x1000 | 0x20000, h, w, w * 4, 0, mips)
    hdr += struct.pack("<2I4s5I", 32, 0x41, b"\0\0\0\0", 32, 0xFF0000, 0xFF00, 0xFF, 0xFF000000)
    hdr += struct.pack("<5I", 0x1000 | 0x8 | 0x400000, 0, 0, 0, 0)
    assert len(hdr) == 128
    open(path, "wb").write(hdr + b"".join(levels))


def main():
    for kind, sizes in SIZES.items():
        for z, (w, h) in enumerate(sizes):
            write_dds(texture(kind, w, h), f"map/terrain/border_{kind}_{z}.dds")
    print("wrote", sum(map(len, SIZES.values())), "border textures")


if __name__ == "__main__":
    t = texture("country", 64, 32)
    a = np.asarray(t)[:, 0, 3]
    assert a[0] == 0 and a[16] == 255 and a[-1] == 0  # transparent outside, opaque core
    main()
