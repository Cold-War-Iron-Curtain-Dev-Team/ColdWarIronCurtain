"""Build the Burma struggle map cutouts: one 7-frame sprite per Burma state.

  python _tools/burma_struggle_map/build_burma_map.py

Frames: 1 active (hatch), 2 integrated (flat), 3 subjugated (desaturated),
4 autonomous (blue stripes), 5 joined BCP, 6 unknown, 7 Union-held / no group.
Every sprite shares one canvas (the cropped Burma bounding box at SCALE), so all
cutouts sit at the same x/y in the window.

Outputs:
  gfx/Scripted_GUI_Special/Struggle/Burma_Map/BUR_state_<id>.png
  gfx/Scripted_GUI_Special/Struggle/Burma_Map/BUR_map_panel_bg.png
  interface/Burma_Struggle_Map.gfx
  _tools/burma_struggle_map/report.json, preview.png
"""

import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
MOD = HERE.parents[1] / "Cold War Iron Curtain"
ART_REL = "gfx/Scripted_GUI_Special/Struggle/Burma_Map"
GFX_FILE = MOD / "interface/Burma_Struggle_Map.gfx"

TARGET_HEIGHT = 560
MARGIN = 2
PANEL_W, PANEL_H = 560, 560
FRAMES = 7

GROUPS = {
    "Communists": "#b8322e", "Karen": "#3f7f8c", "Karenni": "#5a9aa8", "Mon": "#c68a3a",
    "Shan": "#7d9a3f", "Arakanese": "#8a5a9c", "Rohingya": "#3d8a5c", "Kokang": "#b07a8e",
    "Kachin": "#4f6aa8", "Chin": "#a89a4f", "Kuomintang": "#2f4f7f", "Pa-O": "#9c6a4a",
}
STATES = {
    1263: "Communists", 1558: "Communists", 1264: "Karen", 1267: "Karen", 1212: None,
    1265: "Karenni", 1266: "Mon", 1190: "Shan", 1186: "Arakanese", 1559: "Rohingya",
    1985: "Kokang", 1964: "Kokang", 640: "Kachin", 1817: "Kachin", 1896: "Kachin",
    1260: "Chin", 788: "Kuomintang", 787: "Kuomintang", 1996: "Pa-O",
    288: None, 1259: None, 1261: None, 1262: None,
}
BCP_RED = (0x6E, 0x14, 0x14)
UNKNOWN = (0x3A, 0x3A, 0x38)
UNION = (0x6D, 0x6F, 0x73)
AUTONOMY_BLUE = (0x5A, 0xA0, 0xE0)
BORDER_DARK = (0x0C, 0x0D, 0x0E)
BORDER_LIGHT = (0xD8, 0xD6, 0xCF)


def hex_rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def state_provinces():
    out = {}
    for f in (MOD / "history/states").glob("*.txt"):
        text = f.read_text(encoding="utf-8-sig", errors="replace")
        m = re.search(r"\bid\s*=\s*(\d+)", text)
        if not m or int(m.group(1)) not in STATES:
            continue
        p = re.search(r"\bprovinces\s*=\s*\{([^}]*)\}", text)
        out[int(m.group(1))] = [int(x) for x in p.group(1).split()]
    missing = set(STATES) - set(out)
    if missing:
        raise SystemExit(f"states not found: {sorted(missing)}")
    return out


def label_map(provs):
    prov_state = {p: s for s, ps in provs.items() for p in ps}
    colour_state = {}
    for line in (MOD / "map/definition.csv").read_text(encoding="utf-8", errors="replace").splitlines():
        parts = line.split(";")
        if len(parts) < 4 or not parts[0].isdigit():
            continue
        pid = int(parts[0])
        if pid in prov_state:
            r, g, b = int(parts[1]), int(parts[2]), int(parts[3])
            colour_state[(r << 16) | (g << 8) | b] = prov_state[pid]
    img = np.asarray(Image.open(MOD / "map/provinces.bmp").convert("RGB"), dtype=np.uint32)
    key = (img[..., 0] << 16) | (img[..., 1] << 8) | img[..., 2]
    labels = np.zeros(key.shape, dtype=np.int32)
    for k, sid in colour_state.items():
        labels[key == k] = sid
    return labels


def crop(labels):
    ys, xs = np.nonzero(labels)
    y0, y1 = max(ys.min() - MARGIN, 0), ys.max() + MARGIN + 1
    x0, x1 = max(xs.min() - MARGIN, 0), xs.max() + MARGIN + 1
    return labels[y0:y1, x0:x1], (int(x0), int(y0))


def smooth_upscale(labels, scale):
    """Nearest-neighbour upscale, then a per-pixel majority filter to round the stair steps."""
    big = labels.repeat(scale, 0).repeat(scale, 1)
    ids = sorted(STATES) + [0]
    best = np.zeros(big.shape, dtype=np.float32) - 1
    out = np.zeros_like(big)
    radius = max(scale // 2, 1) | 1
    for sid in ids:
        m = Image.fromarray(((big == sid) * 255).astype(np.uint8))
        m = np.asarray(m.filter(ImageFilter.BoxBlur(radius)), dtype=np.float32)
        take = m > best
        out[take] = sid
        best[take] = m[take]
    return out


def edges(big):
    """Return (inner, outer): 1 px state-to-state border and 2 px coast/outer border."""
    pad = np.pad(big, 1, constant_values=0)
    c = pad[1:-1, 1:-1]
    inner = np.zeros(c.shape, bool)
    outer = np.zeros(c.shape, bool)
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        n = pad[1 + dy:pad.shape[0] - 1 + dy, 1 + dx:pad.shape[1] - 1 + dx]
        inner |= (c != 0) & (n != 0) & (n != c)
        outer |= (c != 0) & (n == 0)
    grow = np.pad(outer, 1)
    outer2 = outer.copy()
    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        outer2 |= grow[1 + dy:grow.shape[0] - 1 + dy, 1 + dx:grow.shape[1] - 1 + dx]
    return inner, outer2 & (c != 0)


def frame_colours(group, h, w):
    yy, xx = np.mgrid[0:h, 0:w]
    if group is None:
        flat = np.broadcast_to(np.array(UNION, np.float32), (h, w, 3))
        return [flat] * FRAMES
    base = np.array(hex_rgb(GROUPS[group]), np.float32)
    flat = np.broadcast_to(base, (h, w, 3)).copy()
    hatch = flat.copy()
    hatch[((xx + yy) % 10) < 3] = base * 0.62
    grey = base.mean()
    desat = np.broadcast_to(base * 0.25 + grey * 0.75, (h, w, 3)) * 0.7
    auto = flat.copy()
    auto[((xx - yy) % 12) < 3] = AUTONOMY_BLUE
    return [hatch, flat, desat.copy(),
            auto, np.broadcast_to(np.array(BCP_RED, np.float32), (h, w, 3)),
            np.broadcast_to(np.array(UNKNOWN, np.float32), (h, w, 3)),
            np.broadcast_to(np.array(UNION, np.float32), (h, w, 3))]


def render_state(sid, big, inner, outer):
    h, w = big.shape
    mask = big == sid
    strip = np.zeros((h, w * FRAMES, 4), np.uint8)
    for i, col in enumerate(frame_colours(STATES[sid], h, w)):
        rgb = np.array(col, np.float32)
        rgb[inner] = BORDER_DARK
        rgb[outer] = BORDER_LIGHT
        tile = np.zeros((h, w, 4), np.uint8)
        tile[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        tile[..., 3] = mask * 255
        strip[:, i * w:(i + 1) * w] = tile
    return Image.fromarray(strip, "RGBA")


def panel_bg():
    bg = np.full((PANEL_H, PANEL_W, 3), (0x14, 0x16, 0x18), np.float32)
    bg[2::3] *= 0.78
    bg[0, :] = bg[-1, :] = bg[:, 0] = bg[:, -1] = (0x5A, 0x60, 0x66)
    bg[1, 1:-1] = bg[-2, 1:-1] = bg[1:-1, 1] = bg[1:-1, -2] = (0x05, 0x06, 0x07)
    return Image.fromarray(bg.astype(np.uint8), "RGB")


def swatch_strip(frames, w, h):
    strip = Image.new("RGBA", (w * len(frames), h))
    for i, fill in enumerate(frames):
        tile = Image.new("RGBA", (w, h), fill)
        strip.paste(tile, (i * w, 0))
    return strip


def write_window_swatches():
    win = MOD / "gfx/Scripted_GUI_Special/Struggle/Burma_Window"
    win.mkdir(parents=True, exist_ok=True)
    groups = [hex_rgb(c) + (255,) for c in GROUPS.values()]
    groups.append(UNKNOWN + (255,))
    swatch_strip(groups, 12, 12).save(win / "BUR_group_swatch.png")
    lw, lh = 22, 14
    sample = frame_colours("Mon", lh, lw)
    strip = np.zeros((lh, lw * 7, 4), np.uint8)
    for i, col in enumerate(sample):
        tile = np.array(col, np.float32)
        tile[0, :] = tile[-1, :] = tile[:, 0] = tile[:, -1] = BORDER_LIGHT
        strip[:, i * lw:(i + 1) * lw, :3] = np.clip(tile, 0, 255).astype(np.uint8)
        strip[:, i * lw:(i + 1) * lw, 3] = 255
    Image.fromarray(strip, "RGBA").save(win / "BUR_legend_swatch.png")


def stretch3(src, width, left, right):
    im = Image.open(src).convert("RGBA")
    w, h = im.size
    mid = im.crop((left, 0, w - right, h)).resize((width - left - right, h), Image.BILINEAR)
    out = Image.new("RGBA", (width, h))
    out.paste(im.crop((0, 0, left, h)), (0, 0))
    out.paste(mid, (left, 0))
    out.paste(im.crop((w - right, 0, w, h)), (width - right, 0))
    return out


def window_bg(width, height):
    base = np.full((height, width, 3), (0x12, 0x14, 0x16), np.float32)
    photo = Image.open(MOD / "gfx/Scripted_GUI_Special/Struggle/Burma_Top_BG.png").convert("L")
    s = max(width / photo.width, height / photo.height)
    photo = photo.resize((round(photo.width * s), round(photo.height * s)), Image.LANCZOS)
    left, top = (photo.width - width) // 2, (photo.height - height) // 2
    photo = np.asarray(photo.crop((left, top, left + width, top + height)), np.float32)[..., None]
    fade = np.linspace(0.30, 0.12, height, dtype=np.float32)[:, None, None]
    out = base * (1 - fade) + photo * fade
    out[2::3] *= 0.8
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGB")


WINDOW_W, WINDOW_H = 1150, 1068


def write_window_chrome():
    win = MOD / "gfx/Scripted_GUI_Special/Struggle/Burma_Window"
    win.mkdir(parents=True, exist_ok=True)
    title = stretch3(MOD / "gfx/interface/struggle_header_bg.dds", WINDOW_W - 10, 8, 60)
    frame = Image.new("RGBA", (WINDOW_W, WINDOW_H), (0x05, 0x06, 0x07, 255))
    inner = Image.new("RGBA", (WINDOW_W - 2, WINDOW_H - 2), (0x3C, 0x42, 0x48, 255))
    frame.paste(inner, (1, 1))
    frame.paste(window_bg(WINDOW_W - 6, WINDOW_H - 6).convert("RGBA"), (3, 3))
    frame.alpha_composite(title, (5, 5))
    frame.save(win / "BUR_window_bg.png")
    title.save(win / "BUR_title_bar.png")
    hdr = MOD / "gfx/Scripted_GUI_Special/Struggle/struggle_header.png"
    stretch3(hdr, 1120, 8, 8).save(win / "BUR_header_wide.png")
    stretch3(hdr, 545, 8, 8).save(win / "BUR_header_col.png")
    rel = "gfx/Scripted_GUI_Special/Struggle/Burma_Window"
    return [("GFX_BUR_window_bg", f"{rel}/BUR_window_bg.png", 1),
            ("GFX_BUR_title_bar", f"{rel}/BUR_title_bar.png", 1),
            ("GFX_BUR_header_wide", f"{rel}/BUR_header_wide.png", 1),
            ("GFX_BUR_header_col", f"{rel}/BUR_header_col.png", 1)]


def main():
    write_window_swatches()
    provs = state_provinces()
    labels, origin = crop(label_map(provs))
    scale = max(1, round(TARGET_HEIGHT / labels.shape[0]))
    big = smooth_upscale(labels, scale)
    inner, outer = edges(big)
    h, w = big.shape

    art = MOD / ART_REL
    art.mkdir(parents=True, exist_ok=True)
    for old in art.glob("*.png"):
        old.unlink()

    report = {"scale": scale, "frame_width": w, "frame_height": h,
              "source_origin": list(origin), "panel": [PANEL_W, PANEL_H], "states": {}}
    sprites = []
    preview = panel_bg()
    preview.save(art / "BUR_map_panel_bg.png")
    ox, oy = (PANEL_W - w) // 2, (PANEL_H - h) // 2
    preview = preview.convert("RGBA")
    for sid in sorted(STATES):
        ys, xs = np.nonzero(big == sid)
        if len(xs) == 0:
            raise SystemExit(f"state {sid} has no pixels on the map")
        pad = 2
        x0, y0 = max(0, int(xs.min()) - pad), max(0, int(ys.min()) - pad)
        x1, y1 = min(w, int(xs.max()) + 1 + pad), min(h, int(ys.max()) + 1 + pad)
        full = render_state(sid, big, inner, outer)
        fw, fh = x1 - x0, y1 - y0
        strip = Image.new("RGBA", (fw * FRAMES, fh))
        for i in range(FRAMES):
            strip.paste(full.crop((i * w + x0, y0, i * w + x1, y1)), (i * fw, 0))
        strip.save(art / f"BUR_state_{sid}.png")
        sprites.append((f"GFX_BUR_state_{sid}", f"{ART_REL}/BUR_state_{sid}.png", FRAMES))
        report["states"][str(sid)] = {
            "group": STATES[sid],
            "bbox": [int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1],
            "offset": [x0, y0],
            "size": [fw, fh],
            "centroid": [int(round(xs.mean())), int(round(ys.mean()))],
        }
        preview.alpha_composite(strip.crop((0, 0, fw, fh)), (ox + x0, oy + y0))
    sprites.append(("GFX_BUR_map_panel_bg", f"{ART_REL}/BUR_map_panel_bg.png", 1))
    sprites += write_window_chrome()

    lines = ["spriteTypes = {"]
    for name, tex, n in sprites:
        extra = f" noOfFrames = {n}" if n > 1 else ""
        lines.append(f'\tspriteType = {{ name = "{name}" textureFile = "{tex}"{extra} }}')
    lines.append("}")
    GFX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    preview.convert("RGB").save(HERE / "preview.png")
    print(f"scale {scale}, frame {w}x{h}, {len(sprites)} sprites -> {GFX_FILE.relative_to(MOD)}")


if __name__ == "__main__":
    main()
