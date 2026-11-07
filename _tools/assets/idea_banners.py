"""Build 339x101 politics-view banners in the style of the policy cards.

They follow the look of e.g. gfx/GUI/Minorities/3_Limited_Rights.png: a toned
photo with 2px scanlines, a darkened lower edge and a wide white caps label.

- Manufacturer slots: the politics view draws the engine-assigned
  GFX_<type>_mio_roster sprite on each industrial_org_entry, so the tank, ship,
  aircraft and materiel banners replace vanilla's <type>_mio_roster.dds by path
  (GFX_idea_slot_<slot> points at the same files). Industrial concern is a plain
  idea slot and uses gfx/interface/idea_slot_industrial_concern.dds.
- Laws that had no banner art (isolation, undisturbed isolation, feudal mobilization).

Sources are photos already in the mod (MIO backgrounds, loading screens, event pictures).

    python _tools/assets/idea_banners.py            # write the DDS files
    python _tools/assets/idea_banners.py --preview out.png
"""
import argparse
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFont, ImageOps

MOD = Path(__file__).resolve().parents[2] / "Cold War Iron Curtain"
MIO = "gfx/interface/military_industrial_organization/"
W, H = 339, 101
FONT = Path("C:/Windows/Fonts/bahnschrift.ttf")
SEPIA = ((32, 24, 14), (234, 214, 174))
RED = ((40, 14, 12), (238, 196, 176))

# output (relative to the mod) -> (source, crop box in source pixels, label, (tint dark, tint light))
BANNERS = {
    MIO + "tank_mio_roster.dds":
        (MIO + "mio_details_background_tank.dds", (0, 110, 945, 391), "TANK MANUFACTURER", SEPIA),
    MIO + "aircraft_mio_roster.dds":
        (MIO + "mio_details_background_plane.dds", (20, 280, 945, 556), "AIRCRAFT MANUFACTURER", SEPIA),
    MIO + "ship_mio_roster.dds":
        (MIO + "mio_details_background_ship.dds", (0, 330, 945, 611), "NAVAL MANUFACTURER", SEPIA),
    MIO + "material_mio_roster.dds":
        (MIO + "mio_details_background_factory.dds", (0, 20, 945, 301), "MATERIEL MANUFACTURER", SEPIA),
    "gfx/interface/idea_slot_industrial_concern.dds":
        (MIO + "mio_details_background.dds", (0, 300, 945, 581), "INDUSTRIAL CONCERN", SEPIA),
    "gfx/interface/ideas/idea_isolation.dds":
        ("gfx/event_pictures/Border.png", (15, 42, 200, 97), "ISOLATION", SEPIA),
    "gfx/interface/ideas/idea_undisturbed_isolation.dds":
        ("gfx/event_pictures/GFX_news_event_Berlin_wall.dds", (0, 212, 185, 267), "UNDISTURBED ISOLATION", SEPIA),
    "gfx/interface/ideas/idea_feudal_mobilization.dds":
        ("gfx/loadingscreens/load_33.dds", (250, 330, 1350, 657), "FEUDAL MOBILIZATION", RED),
}


def photo(src, box, tint):
    dark, light = tint
    im = Image.open(MOD / src).convert("L").crop(box).resize((W, H), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Contrast(im).enhance(1.1)
    rgb = ImageOps.colorize(im, dark, light)
    # Scanlines: 2 dark rows, 2 light rows, matching the policy banners.
    lines = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(lines)
    for y in range(H):
        if y % 4 < 2:
            d.line([(0, y), (W, y)], fill=212)
    rgb = ImageChops.multiply(rgb, Image.merge("RGB", [lines] * 3))
    # Darken the lower band and the edges so the label reads.
    shade = Image.new("L", (W, H), 255)
    d = ImageDraw.Draw(shade)
    for y in range(H):
        t = max(0.0, (y - 40) / (H - 40))
        d.line([(0, y), (W, y)], fill=int(255 - 150 * t ** 1.4))
    # Soft dark border on all four sides, like the policy cards: about 25% brightness
    # at the edge, easing back to full over EDGE px, with a wider gentle fade at the sides.
    EDGE = 13
    edge = Image.new("L", (W, H), 255)
    px = edge.load()
    for y in range(H):
        for x in range(W):
            dist = min(x, W - 1 - x, y, H - 1 - y)
            t = min(1.0, dist / EDGE)
            near = 0.25 + 0.75 * (t * t * (3 - 2 * t))
            side = 1 - 0.25 * max(0.0, 1 - min(x, W - 1 - x) / 45) ** 2
            px[x, y] = int(255 * near * side)
    shade = ImageChops.multiply(shade, edge)
    return ImageChops.multiply(rgb, Image.merge("RGB", [shade] * 3))


def label(text):
    font = ImageFont.truetype(str(FONT), 96)
    try:
        font.set_variation_by_name("Bold")
    except (OSError, ValueError):
        pass
    l, t, r, b = font.getbbox(text)
    mask = Image.new("L", (r - l + 8, b - t + 8), 0)
    ImageDraw.Draw(mask).text((4 - l, 4 - t), text, font=font, fill=255)
    # Wide, squat lettering like the policy banners.
    cap = 15
    scale = cap / (b - t)
    w = min(int(mask.width * scale * 1.32), W - 14)
    return mask.resize((w, int(mask.height * scale)), Image.LANCZOS)


def banner(src, box, text, tint):
    return put_label(photo(src, box, tint).convert("RGBA"), text)


# Empty Rocketry slots: a dimmed schematic from the space art with its own label
# erased, so an empty slot reads as "pick a launch vehicle" rather than a blank box.
SPACE = "gfx/interface/ideas/spaceideas/"
SPACE_SLOTS = {
    SPACE + "slot_booster.dds": (SPACE + "Saturn_5.dds", "LAUNCH VEHICLE"),
    SPACE + "slot_upper_stages.dds": (SPACE + "Centaur_C.dds", "UPPER STAGE"),
    SPACE + "slot_mission.dds": (SPACE + "Space_Shuttle.dds", "MISSION"),
    SPACE + "slot_supplementaries.dds": (SPACE + "SRBS_4x.dds", "SUPPLEMENTARY"),
}
SPACE_BG = (22, 26, 22)


def space_slot(src, text):
    im = Image.open(MOD / src).convert("RGB")
    im = ImageEnhance.Brightness(im).enhance(0.45)
    bg = Image.new("RGB", im.size, SPACE_BG)
    # Fade the lower band (where the source's own label sits) into the background.
    mask = Image.new("L", im.size, 0)
    d = ImageDraw.Draw(mask)
    for y in range(H):
        t = min(1.0, max(0.0, (y - 58) / 14))
        d.line([(0, y), (W, y)], fill=int(255 * t))
    im = Image.composite(bg, im, mask)
    return put_label(im.convert("RGBA"), text)


def put_label(im, text):
    mask = label(text)
    x, y = 6, H - mask.height - 6
    shadow = Image.new("RGBA", im.size, (0, 0, 0, 0))
    blk = Image.new("RGBA", mask.size, (20, 18, 16, 255))
    for dx, dy, a in ((2, 2, 230), (1, 1, 255), (-1, 0, 150), (0, -1, 150), (1, 0, 150), (0, 1, 150)):
        m = mask.point(lambda v, a=a: v * a // 255)
        shadow.paste(blk, (x + dx, y + dy), m)
    im = Image.alpha_composite(im, shadow)
    grad = Image.new("RGBA", mask.size)
    gd = ImageDraw.Draw(grad)
    for yy in range(mask.height):
        t = yy / max(1, mask.height - 1)
        c = int(255 - 70 * t)
        gd.line([(0, yy), (mask.width, yy)], fill=(c, c, c, 255))
    text_layer = Image.new("RGBA", im.size, (0, 0, 0, 0))
    text_layer.paste(grad, (x, y), mask)
    return Image.alpha_composite(im, text_layer)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="write a contact sheet instead of the DDS files")
    args = ap.parse_args()
    images = {out: banner(*spec) for out, spec in BANNERS.items()}
    images.update({out: space_slot(*spec) for out, spec in SPACE_SLOTS.items()})
    if args.preview:
        sheet = Image.new("RGBA", (W, H * len(images)))
        for i, im in enumerate(images.values()):
            sheet.paste(im, (0, i * H))
        sheet.resize((W * 2, H * 2 * len(images)), Image.NEAREST).save(args.preview)
        return
    for out, im in images.items():
        im.save(MOD / out, "DDS")  # uncompressed RGBA, like the policy idea banners
        print("wrote", out)


if __name__ == "__main__":
    main()
