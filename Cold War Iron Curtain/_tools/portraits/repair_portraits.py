"""Rebuild CWIC military pools from an installed HOI4, using base-game assets.

Usage: python _tools/portraits/repair_portraits.py --game-dir ".../Hearts of Iron IV"
       python _tools/portraits/repair_portraits.py --game-dir "..." --check

The 00_portraits.txt override is necessary: vanilla SAR/SMI/TML mean different
countries in CWIC, and vanilla's pools reference optional DLC sprites. Import only
military pairs available without DLC; retain CWIC's political pools. Never copy
vanilla textures or restore the DLC pool files suppressed for multiplayer.
Pillow is required only when rebuilding the thumbnails of existing CWIC art.
"""

import argparse
from copy import deepcopy
from pathlib import Path
import re

MOD = Path(__file__).resolve().parents[2]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|[{}=]|[^\s{}=#]+')


def parse(path):
    tokens = [m.group() for m in TOKEN.finditer(path.read_text(encoding="utf-8-sig"))
              if not m.group().startswith("#")]

    def block(i, nested=False):
        result = []
        while i < len(tokens):
            key = tokens[i]
            i += 1
            if key == "}":
                assert nested, f"Unexpected closing brace in {path}"
                return result, i
            if i < len(tokens) and tokens[i] == "=":
                i += 1
                value = tokens[i]
                i += 1
                if value == "{":
                    value, i = block(i, True)
                result.append((key, value))
            else:
                result.append((None, key))
        assert not nested, f"Unclosed block in {path}"
        return result, i

    return block(0)[0]


def get(nodes, key, default=None):
    return next((v for k, v in nodes if k == key), default)


def render(nodes, depth=0):
    lines = []
    for key, value in nodes:
        prefix = "\t" * depth
        if isinstance(value, list):
            lines.append(f"{prefix}{key} = {{")
            lines.extend(render(value, depth + 1))
            lines.append(prefix + "}")
        else:
            lines.append(prefix + (f"{key} = " if key else "") + value)
    return lines


def sprite_index(paths):
    result = {}
    for path in sorted(paths):
        # Scan static sprite headers independently of unrelated animated/UI
        # blocks; some shipped .gfx files have malformed outer braces.
        text = re.sub(r'#[^\n]*', '', path.read_text(encoding="utf-8-sig", errors="replace"))
        for body in re.findall(r'\bspriteType\s*=\s*\{([^{}]*)', text, re.I):
            name = re.search(r'\bname\s*=\s*"?([^"\s}]+)', body)
            texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', body, re.I)
            if name and texture:
                result[name[1].lower()] = (name[1], texture[1])
    return result


# Only exceptions to native continental fallback. Country-specific uniforms are
# used for successor tags; region-specific pools handle capital/continent borders.
# Do not derive ethnicity from CWIC religious graphical cultures: some of those
# deliberately describe religion or colonial administration rather than people.
SUPPLEMENTS = {
    "GER": "WGR DDR GSR SAR",
    "SOV": "RUS RNU CPS USO RLG LBR RNC ECR RFE SKU CUM",
    "USA": "CAL CSD TEX HWI",
    "FRA": "FRE ALE",
    "RAJ": "SRL BAN ASA MAU SIN TML",
    "INS": "INO BRU SGP SWK MLA VIN VIE NLF FUL CAM LAO LOS BRM BCP KNN ARA SHA CHN KAC KND TLK TIM",
    "continent:europe": "ARM SOS NGK",
    "continent:africa": "HAI RNA CAY CAR ANC BOP VND CSK",
    "continent:middle_east": "MOR TUN ALG TNG WES TAL BAL WAZ LOP SEE CSA SMI",
    "continent:south_america": "ZAP IND",
    "continent:asia": "KPA KSR MAO",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-dir", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    game = args.game_dir.resolve()
    base_path = game / "portraits/00_portraits.txt"
    base = parse(base_path)
    current_path = MOD / "portraits/00_portraits.txt"
    current = parse(current_path)
    vanilla = sprite_index((game / "interface").rglob("*.gfx"))
    generated_gfx = MOD / "interface/CWIC_generic_portrait_pairs.gfx"
    # Exclude our previous output when rebuilding: otherwise masked vanilla
    # definitions would disappear on alternate runs.
    custom = sprite_index(p for p in (MOD / "interface").rglob("*.gfx") if p != generated_gfx)
    visible = sprite_index(p for p in (game / "interface").rglob("*.gfx")
                           if not (MOD / p.relative_to(game)).exists())
    visible.update(custom)

    def texture_exists(texture):
        return (MOD / texture).is_file() or (game / texture).is_file()

    def has_base_pair(name):
        return all((info := vanilla.get(key.lower())) and texture_exists(info[1])
                   for key in (name, name + "_small"))

    sources = {}
    excluded = set()
    for key, body in base:
        source = "continent:" + get(body, "name") if key == "continent" else key
        military = []
        for role, genders in body:
            if role not in ("army", "navy"):
                continue
            clean_genders = []
            for gender, entries in genders:
                clean = []
                for _, entry in entries:
                    name = entry.strip('"')
                    if has_base_pair(name):
                        clean.append((None, entry))
                    else:
                        excluded.add(name)
                if clean:
                    clean_genders.append((gender, clean))
            if clean_genders:
                military.append((role, clean_genders))
        if military:
            sources[source] = military

    # The current vanilla Indian navy lists contain only DLC entries.
    # Older Indian generic admirals remain in the base game with complete pairs.
    indian_navy = [("male", [(None, f'"GFX_Portrait_The_Raj_Generic_navy_{i}"')
                             for i in (1, 2)])]
    for source in ("RAJ", "PAK"):
        if not get(sources[source], "navy"):
            sources[source].append(("navy", deepcopy(indian_navy)))

    tags = {}
    for path in sorted((MOD / "common/country_tags").glob("*.txt")):
        tags.update((k, v) for k, v in parse(path) if re.fullmatch(r"[A-Z0-9]{3}", k))

    # Preserve political/default behavior, but give the old texture reference a
    # proper sprite pair so small-portrait conversion no longer guesses a path.
    def named_placeholder(nodes):
        return [(k, named_placeholder(v) if isinstance(v, list) else
                 v.replace('"gfx/leaders/Giga_Panther.dds"', '"GFX_CWIC_generic_placeholder"'))
                for k, v in nodes]

    default = [(k, v) for k, v in get(current, "default") if k not in ("army", "navy")]
    default = named_placeholder(default)
    for role in ("army", "navy"):
        default.append((role, [
            ("male", [(None, '"GFX_CWIC_military_unknown"')]),
            ("female", [(None, '"GFX_CWIC_military_unknown"')]),
        ]))
    output = [("default", default)]
    for key, body in current:
        if key == "continent":
            name = get(body, "name")
            output.append((key, [("name", name)] + deepcopy(sources["continent:" + name]) +
                           named_placeholder([(k, v) for k, v in body if k not in ("name", "army", "navy")])))

    countries = {key: deepcopy(pool) for key, pool in sources.items() if key in tags}
    for source, target_tags in SUPPLEMENTS.items():
        for tag in target_tags.split():
            assert tag in tags, f"Unknown supplement tag {tag}"
            countries[tag] = deepcopy(sources[source])

    # South Korea retains its own generic army art and uses the regional navy.
    countries["KOR"] = [("army", deepcopy(get(get(current, "KOR"), "army"))),
                        ("navy", deepcopy(get(sources["continent:asia"], "navy")))]
    output.extend(sorted(countries.items()))

    pairs = {}
    thumbnails = {}
    def add_pair(name, large, small):
        pairs[name.lower()] = (name, large)
        pairs[(name + "_small").lower()] = (name + "_small", small)

    # CWIC's idea_unknown.dds is a "NO ICON?" debug banner, not a portrait.
    # Use the neutral silhouette at both sizes for unsupported military genders.
    unknown_small = "gfx/interface/ideas/CWIC_generic/military_unknown.dds"
    add_pair("GFX_CWIC_military_unknown", "gfx/leaders/leader_unknown.dds", unknown_small)
    thumbnails[unknown_small] = "gfx/leaders/leader_unknown.dds"
    placeholder_small = "gfx/interface/ideas/CWIC_generic/placeholder.dds"
    add_pair("GFX_CWIC_generic_placeholder", "gfx/leaders/Giga_Panther.dds", placeholder_small)
    thumbnails[placeholder_small] = "gfx/leaders/Giga_Panther.dds"
    for gender, entries in get(countries["KOR"], "army"):
        for _, ref in entries:
            name = ref.strip('"')
            texture = custom[name.lower()][1]
            small = "gfx/interface/ideas/CWIC_generic/" + Path(texture).name
            pairs[(name + "_small").lower()] = (name + "_small", small)
            thumbnails[small] = texture

    def references(nodes):
        for key, value in nodes:
            if isinstance(value, list):
                yield from references(value)
            elif key is None:
                yield value.strip('"')

    # Restore just the required definitions hidden by CWIC's replacement .gfx
    # files. Reuse vanilla texture paths; do not import unrelated WW2 characters.
    for name in references(output):
        for key in (name.lower(), (name + "_small").lower()):
            if key not in visible and key not in pairs:
                assert key in vanilla, f"Unresolved sprite {name}"
                pairs[key] = vanilla[key]

    header = (
        "# Military pools imported from vanilla by _tools/portraits/repair_portraits.py.\n"
        "# Keep this override: CWIC reuses tags (SAR, SMI, TML) and requires DLC-independent pools.\n"
        "# Vanilla textures/sprites are reused; only CWIC exceptions and hidden sprite pairs are supplied.\n"
        "# CWIC political pools and the separate multiplayer DLC-pool suppressions are preserved.\n"
    )
    pool_text = header + "\n\n".join("\n".join(render([node])) for node in output) + "\n"
    gfx_text = ("# Required pairs hidden by CWIC .gfx overrides, and small versions of CWIC art.\n"
                "# Generated by _tools/portraits/repair_portraits.py; vanilla textures remain inherited.\n" +
                "\n".join(render([("spriteTypes", [("spriteType", [("name", f'"{name}"'),
                    ("texturefile", f'"{texture}"')]) for _, (name, texture) in sorted(pairs.items())])])) + "\n")

    if args.check:
        assert current_path.read_text(encoding="utf-8-sig") == pool_text, "Portrait pools need regeneration"
        assert generated_gfx.read_text(encoding="utf-8-sig") == gfx_text, "Sprite pairs need regeneration"
    else:
        current_path.write_text(pool_text, encoding="utf-8", newline="\n")
        generated_gfx.write_text(gfx_text, encoding="utf-8", newline="\n")
        from PIL import Image, ImageOps
        for target, source in thumbnails.items():
            dest = MOD / target
            dest.parent.mkdir(parents=True, exist_ok=True)
            with Image.open(MOD / source) as original:
                # Match HOI4's 65x67 small portrait slots. Keep the upper portrait
                # (face/shoulders) instead of compressing the whole 156x210 image.
                small = ImageOps.fit(original.convert("RGBA"), (65, 67), Image.Resampling.LANCZOS,
                                     centering=(0.5, 0.15))
                small.save(dest, pixel_format="DXT5")

    resolved = visible | pairs
    for name in references(output):
        for key in (name.lower(), (name + "_small").lower()):
            assert key in resolved, f"Missing sprite: {key}"
            assert texture_exists(resolved[key][1]), f"Missing texture: {resolved[key]}"
    # Read the compiled DDS headers without requiring Pillow in check mode.
    import struct
    for target in thumbnails:
        header = (MOD / target).read_bytes()[:128]
        assert header[:4] == b"DDS " and struct.unpack_from("<II", header, 12) == (67, 65), target
    # Keep pool membership the same regardless of which DLC a player owns.
    for filename in ("01_anniversary_portraits.txt", "027_lar_portraits.txt",
                     "05_bba_portraits.txt", "046_goe_portraits.txt"):
        assert not parse(MOD / "portraits" / filename), f"DLC pools are no longer suppressed: {filename}"
    for tag, body in countries.items():
        for role in ("army", "navy"):
            assert get(get(body, role, []), "male"), f"Missing {role} male pool: {tag}"
    # The most important regression: US generals and captains must use US pools.
    for role in ("army", "navy"):
        assert all("usa" in name.lower() for name in references(get(countries["USA"], role)))
    assert countries["SAR"] == sources["GER"]
    assert countries["SMI"] == sources["continent:middle_east"]  # Imamate of Oman, not Sami
    assert countries["TML"] == sources["RAJ"]  # Tamil, not Timor-Leste
    assert all("giga" not in name.lower() and "placeholder" not in name.lower()
               for _, body in output for role, pool in body if role in ("army", "navy")
               for name in references(pool))
    print(f"Validated {len(tags)} country tags: {len(countries)} national military pools, 7 continental fallbacks.")
    print(f"Validated {len(set(references(output)))} portrait pairs without DLC; {len(thumbnails)} CWIC thumbnails.")
    print(f"Omitted {len(excluded)} vanilla entries without a complete base-game sprite pair.")


if __name__ == "__main__":
    main()
