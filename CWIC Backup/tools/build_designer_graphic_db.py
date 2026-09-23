#!/usr/bin/env python3
"""Regenerate gfx/interface/equipmentdesigner/graphic_db/00_tank_icons.txt.

Art comes from the non-NSB technology sprite library (GFX_<TAG>_<legacy tech>_medium and the
generic GFX_<legacy tech>_medium). Each designer generation's Equipment Match is the legacy tier
the national names on that hull come from (the ROLES ladders), so a hull's picture and its
historical names share one legacy row. Models already in the file are preserved.

    python3 "CWIC Backup/tools/build_designer_graphic_db.py" [--check]
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "Cold War Iron Curtain"
VANILLA = Path.home() / ".local/share/Steam/steamapps/common/Hearts of Iron IV"
TARGET = MOD / "gfx/interface/equipmentdesigner/graphic_db/00_tank_icons.txt"

LIGHT_TANKS = [(f"light_tanks_{n}", y) for n, y in zip(range(1, 7), [1942, 1944, 1947, 1960, 1975, 1995])]
MAIN_BATTLE_TANKS = [("main_battle_tanks", 1942)] + [
    (f"main_battle_tanks_{n}", y)
    for n, y in zip(range(1, 10), [1944, 1947, 1950, 1960, 1965, 1975, 1985, 1995, 2005])
]
HEAVY_TANKS = [(f"heavy_tanks_{n}", y) for n, y in zip(range(1, 6), [1942, 1944, 1947, 1955, 1955])]
SPAAG = [(f"spaag_{n}", y) for n, y in zip(range(1, 6), [1940, 1955, 1970, 1985, 2000])]
LIGHT_SPG = [(f"light_sp_artillery_{n}", y) for n, y in zip(range(1, 6), [1945, 1960, 1975, 1990, 2005])]
MEDIUM_SPG = [(f"sp_artillery_{n}", y) for n, y in zip(range(1, 6), [1940, 1955, 1970, 1985, 2000])]
HEAVY_SPG = [(f"heavy_sp_artillery_{n}", y) for n, y in zip(range(1, 6), [1945, 1960, 1975, 1990, 2005])]
TANK_DESTROYER = [(f"tank_destroyer_{n}", y) for n, y in zip(range(1, 6), [1950, 1960, 1970, 1985, 1995])]
ATGM_CARRIER = [(f"atgm_carrier_{n}", y) for n, y in zip(range(0, 5), [1960, 1970, 1980, 1990, 2000])]
APC = [("mechanized_infantry", 1942)] + [
    (f"mechanized_infantry{n}", y)
    for n, y in zip(range(2, 11), [1944, 1947, 1950, 1960, 1965, 1975, 1985, 1995, 2005])
]
IFV = [("mechanized_heavy_infantry", 1947)] + [
    (f"mechanized_heavy_infantry{n}", y)
    for n, y in zip(range(2, 9), [1950, 1955, 1965, 1975, 1985, 1995, 2005])
]

# (role, art tiers, ladder). A ladder entry is the 1-based position in the art tiers of each
# hull generation's Equipment Match: the legacy row the national names on that hull come from
# (heavy SP artillery 4 takes the earlier of its two rows, so every named design's own art stays
# offered); a generation with no names takes the nearest tier by year between its named
# neighbours, and an unnamed role mirrors its named sibling.
ROLES = [
    ("light_tank_chassis", LIGHT_TANKS, (1, 1, 2, 3, 4, 5, 5, 6, 6, 6)),
    ("medium_tank_chassis", MAIN_BATTLE_TANKS, (1, 2, 3, 4, 5, 6, 7, 9, 10, 10)),
    ("heavy_tank_chassis", HEAVY_TANKS, (1, 1, 2, 3, 4)),
    ("light_tank_aa_chassis", SPAAG, (1, 1, 2, 3, 3, 3, 4, 4, 5, 5)),
    ("medium_tank_aa_chassis", SPAAG, (1, 1, 2, 3, 3, 3, 4, 4, 5, 5)),
    ("light_tank_artillery_chassis", LIGHT_SPG, (1, 1, 2, 3, 2, 3, 3, 4, 5, 5)),
    ("medium_tank_artillery_chassis", MEDIUM_SPG, (1, 1, 2, 3, 3, 3, 4, 4, 5, 5)),
    ("heavy_tank_artillery_chassis", HEAVY_SPG, (1, 1, 1, 3, 4)),
    ("light_tank_destroyer_chassis", TANK_DESTROYER[:1] + ATGM_CARRIER, (1, 1, 1, 1, 2, 3, 4, 5, 6, 6)),
    ("medium_tank_destroyer_chassis", TANK_DESTROYER, (1, 1, 2, 3, 2, 3, 4, 5, 5, 5)),
    ("heavy_tank_destroyer_chassis", TANK_DESTROYER, (1, 1, 2, 3, 2)),
    ("light_tank_apc_chassis", APC, (1, 1, 3, 4, 6, 7, 8, 9, 10, 10)),
    ("medium_tank_apc_chassis", APC, (1, 1, 3, 4, 6, 7, 8, 9, 10, 10)),
    ("light_tank_ifv_chassis", IFV, (1, 1, 1, 3, 4, 5, 6, 7, 8, 8)),
    ("medium_tank_ifv_chassis", IFV, (1, 1, 1, 3, 4, 5, 6, 7, 8, 8)),
]

# Legacy equipment id -> its art tier, so a named design takes the picture of the row its name
# came from. mechanized_marine_equipment has no art in the APC family and is absent.
LEGACY_ART = {
    **{f"lt_equipment_{n}": tech for n, (tech, _) in enumerate(LIGHT_TANKS, 1)},
    **{f"mbt_equipment_{n}": tech for n, (tech, _) in enumerate(MAIN_BATTLE_TANKS)},
    **{f"ht_equipment_{n}": tech for n, (tech, _) in enumerate(HEAVY_TANKS, 1)},
    **{f"spaag_equipment_{n}": tech for n, (tech, _) in enumerate(SPAAG, 1)},
    **{f"light_sp_artillery_equipment_{n}": tech for n, (tech, _) in enumerate(LIGHT_SPG, 1)},
    **{f"sp_artillery_equipment_{n}": tech for n, (tech, _) in enumerate(MEDIUM_SPG, 1)},
    **{f"heavy_sp_artillery_equipment_{n}": tech for n, (tech, _) in enumerate(HEAVY_SPG, 1)},
    **{f"medium_tank_destroyer_equipment_{n}": tech for n, (tech, _) in enumerate(TANK_DESTROYER, 1)},
    **{f"atgm_carrier_equipment_{n}": tech for n, (tech, _) in enumerate(ATGM_CARRIER)},
    **{f"mechanized_equipment_{n}": tech for n, (tech, _) in enumerate(APC, 1)},
    **{f"mechanized_heavy_equipment_{n}": tech for n, (tech, _) in enumerate(IFV, 1)},
}

COUNTRY_TOLERANCE = 10
ALTERNATE_WEIGHT = 0.5

HEADER = """\
# Cold War Iron Curtain tank designer graphic database.
# Generated by CWIC Backup/tools/build_designer_graphic_db.py - edit the tool, not this file.
#
# Keyed on the exact per-generation equipment type. The first pool is the Equipment Match: the
# non-NSB technology art of the legacy row the generation's national names come from. The
# weight 0.5 pool offers the rest of that role family's art as selectable alternates.
# "default" carries the generic art, so a country without its own art for a role still gets
# that role's picture instead of falling through to the plain tank hull.
"""


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def registered_sprites() -> set[str]:
    sprites = set()
    for path in sorted((MOD / "interface").rglob("*.gfx")):
        body = read(path)
        for block in re.finditer(r"spriteType\s*=\s*\{(.*?)\}", body, re.S | re.I):
            name = re.search(r'name\s*=\s*"(GFX_[A-Za-z0-9_]+)"', block.group(1))
            texture = re.search(r'texturefile\s*=\s*"([^"]+)"', block.group(1), re.I)
            if not name or not texture:
                continue
            relative = texture.group(1).replace("\\", "/")
            if (MOD / relative).is_file() or (VANILLA / relative).is_file():
                sprites.add(name.group(1))
    return sprites


def existing_models() -> dict[tuple[str, str], list[str]]:
    models: dict[tuple[str, str], list[str]] = {}
    if not TARGET.exists():
        return models
    tag = None
    key = None
    in_models = False
    for line in read(TARGET).splitlines():
        if m := re.match(r"^(\w+) = \{", line):
            tag = m.group(1)
        elif m := re.match(r"^\t(\w+) = \{", line):
            key = m.group(1)
        elif re.match(r"^\t{3}models = \{", line):
            in_models = True
        elif in_models and re.match(r"^\t{3}\}", line):
            in_models = False
        elif in_models and (m := re.match(r"^\t{4}(\w+)", line)):
            models.setdefault((tag, key), []).append(m.group(1))
    return models


def nearest(tiers: list[tuple[str, int]], year: int) -> tuple[str, int]:
    return min(tiers, key=lambda tier: (abs(tier[1] - year), tier[1]))


def sprite(tag: str | None, tech: str) -> str:
    return f"GFX_{tag}_{tech}_medium" if tag else f"GFX_{tech}_medium"


def art(tag: str | None, tiers: list[tuple[str, int]], target: tuple[str, int], sprites: set[str]) -> str | None:
    """The tag's picture for a target tier: its own art for that tier, else its art nearest in
    year within COUNTRY_TOLERANCE. The generic block always takes its own art for the tier."""
    owned = [tier for tier in tiers if sprite(tag, tier[0]) in sprites]
    if not owned:
        return None
    match = target if target in owned else nearest(owned, target[1])
    if tag is None or abs(match[1] - target[1]) <= COUNTRY_TOLERANCE:
        return sprite(tag, match[0])
    return None


def build() -> str:
    sprites = registered_sprites()
    models = existing_models()
    tags = sorted(
        {
            m.group(1)
            for name in sprites
            if (m := re.match(r"GFX_([A-Z][A-Z0-9]{2})_(\w+)_medium$", name))
            and any(m.group(2) == tech for _, tiers, _ in ROLES for tech, _ in tiers)
        }
        | {tag for tag, _ in models}
    )

    out = [HEADER]
    for tag in [None] + tags:
        lines = []
        for role, tiers, ladder in ROLES:
            owned = [sprite(tag, tech) for tech, _ in tiers if sprite(tag, tech) in sprites]
            for generation, position in enumerate(ladder):
                key = f"{role}_{generation}"
                icons = []
                match = art(tag, tiers, tiers[position - 1], sprites)
                if match:
                    icons = [match] + [icon for icon in owned if icon != match]
                pool_models = models.get((tag, key), []) if tag else []
                if not icons and not pool_models:
                    continue
                lines.append(f"\t{key} = {{")
                lines.append("\t\tpool = {")
                if icons:
                    lines += ["\t\t\ticons = {", f"\t\t\t\t{icons[0]}", "\t\t\t}"]
                if pool_models:
                    lines += ["\t\t\tmodels = {"] + [f"\t\t\t\t{m}" for m in pool_models] + ["\t\t\t}"]
                lines.append("\t\t}")
                if len(icons) > 1:
                    lines.append("\t\tpool = {")
                    lines.append(f"\t\t\tweight = {ALTERNATE_WEIGHT}")
                    lines += ["\t\t\ticons = {"] + [f"\t\t\t\t{i}" for i in reversed(icons[1:])] + ["\t\t\t}"]
                    lines.append("\t\t}")
                lines.append("\t}")
        if lines:
            out.append(f"{tag or 'default'} = {{")
            out += lines
            out.append("}")
            out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    body = build()
    if "--check" in sys.argv:
        current = TARGET.read_bytes().decode("utf-8") if TARGET.exists() else ""
        if current != body:
            print(f"{TARGET.relative_to(ROOT)} is stale; rerun without --check")
            sys.exit(1)
        print("designer graphic database is current")
    else:
        TARGET.write_bytes(body.encode("utf-8"))
        print(f"wrote {TARGET.relative_to(ROOT)}: {body.count('pool = {')} pools")
