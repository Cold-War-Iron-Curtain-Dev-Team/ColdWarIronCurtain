"""Build missing name lists and DLC-independent operative portrait pools.

Use --game-dir with the installed HOI4 directory; --check validates without writes.
Names reuse CWIC lists or vanilla lists for the same people where available.
Regional substitutes are explicit below; they are not newly researched name sets.
Temporary civil-war tags must have no hard-coded names, matching vanilla.
"""

import argparse
from copy import deepcopy
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
from repair_portraits import MOD, TOKEN, get, parse, render, sprite_index


# Source -> target tags. v: denotes a vanilla list (tag meanings differ in CWIC).
NAME_SOURCES = {
    "v:FSM": "AAM MIC KIR",
    "INO": "ACH LAR",
    "GEO": "ADJ",
    "v:KBK": "ADY CHR KAB",
    "v:BYA": "AGA BUR UOB",
    "v:ALT": "ALT",
    "SPR": "AND",
    "IRQ": "ARB",
    "v:DAG": "AVR DAG LEZ",
    "TAJ": "BDK",
    "v:CKK": "CKT KRY",
    "COL": "CLL CLM ELN FRC MNE",
    "v:SAM": "COI TUV",
    "BRM": "CPB KND PAO TLK",
    "v:CRI": "CRI",
    "DOM": "DMC DML",
    "NGA": "ECO",
    "SIK": "ETR",
    "v:EVE": "EVE",
    "MAD": "FRM",
    "v:KHM": "HMA",
    "AST": "HTT",
    "CHE": "ING",
    "SIA": "ISA TYU",
    "ARM": "JAV",
    "SOV": "JEW",  # Soviet regional fallback; no dedicated Yiddish list exists.
    "v:KHA": "KHK",
    "UZB": "KKP",
    "AZR": "NAK TLM",
    "PNG": "NCE",  # Existing Melanesian regional list, not French officials.
    "v:NEN": "NEN",
    "v:NOA": "NOS",
    "v:TAH": "PLY",
    "VIE": "PQC",
    "JAP": "RYU",
    "PHI": "SLU",
    "FRA": "TAF",
    "v:TAY": "TAY",
    "v:UDM": "UDM",
    "LIB": "ULM",
    "v:VAN": "VAN",
    "v:YAK": "YAK",
    "v:YAM": "YAM",
}

CONTINENTS = {
    "europe": "Europe", "north_america": "Europe", "south_america": "LatinAmerica",
    "australia": "Europe", "africa": "Africa", "asia": "East_Asian", "middle_east": "MiddleEast",
}
FEMALE_REGION = {
    "Europe": "europe", "Eastern_Europe": "europe", "Africa": "africa",
    "East_Asian": "asia", "Steppe": "asia", "South_Asian": "india",
    "MiddleEast": "arabia", "LatinAmerica": "southamerica",
}
OPERATIVE_EXCEPTIONS = {
    "MiddleEast": "AFG TAL BAL WAZ LOP SEE MOR TUN ALG TNG WES CSA SMI",
    "South_Asian": "RAJ PAK BAN SRL ASA TML SIN MAU TWP MNP",
    "Steppe": "KAZ UZB KYR TMS TAJ MON TAN YAK BUR AGA UOB ALT KHK",
    "Africa": "HAI RNA CAY CAR ANC BOP VND CSK",
    "East_Asian": "KPA KOR KSR MAO",
    "Europe": "ALE HWI SAR",
}


def person_fields(body):
    return deepcopy([(k, v) for k, v in body if k in ("male", "female", "surnames", "callsigns")])


def render_names(nodes, depth=0):
    """Keep long person lists readable without one line per name."""
    lines = []
    for key, value in nodes:
        prefix = "\t" * depth
        if isinstance(value, list) and all(k is None and isinstance(v, str) for k, v in value):
            line = prefix + key + " = {"
            for _, word in value:
                if len(line) + len(word) > 110:
                    lines.append(line)
                    line = prefix + "\t" + word
                else:
                    line += " " + word
            lines.append(line + " }")
        elif isinstance(value, list):
            lines.append(prefix + key + " = {")
            lines.extend(render_names(value, depth + 1))
            lines.append(prefix + "}")
        else:
            lines.append(prefix + key + " = " + value)
    return lines


def top_spans(text):
    """Locate complete top-level assignments without changing other formatting."""
    tokens = [(m.group(), m.start(), m.end()) for m in TOKEN.finditer(text)
              if not m.group().startswith("#") and m.group() != "\ufeff"]
    result = {}
    depth = 0
    for i, (token, start, end) in enumerate(tokens):
        if depth == 0 and i + 2 < len(tokens) and tokens[i+1][0] == "=" and tokens[i+2][0] == "{":
            key, begin = token, start
        if token == "{":
            depth += 1
        elif token == "}":
            depth -= 1
            if depth == 0:
                result[key] = (begin, end)
    assert depth == 0
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--game-dir", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    game = args.game_dir
    names_path = MOD / "common/names/00_names.txt"
    names = dict(parse(names_path))
    base_names = dict(parse(game / "common/names/00_names.txt"))
    tags = {}
    for path in (MOD / "common/country_tags").glob("*.txt"):
        tags.update((k, v.strip('"')) for k, v in parse(path) if re.fullmatch(r"[A-Z0-9]{3}", k))

    # Strip only the Dxx overrides, and correct two Indian lists copied from USA.
    text = names_path.read_bytes().decode("utf-8")
    spans = top_spans(text.lstrip("\ufeff"))
    bom = "\ufeff" if text.startswith("\ufeff") else ""
    text = text.lstrip("\ufeff")
    newline = "\r\n" if "\r\n" in text else "\n"
    changes = []
    for tag, (start, end) in spans.items():
        if re.fullmatch(r"D\d\d", tag):
            changes.append((start, end, ""))
        elif tag in ("TWP", "MNP"):
            changes.append((start, end, newline.join(render_names([(tag, person_fields(names["RAJ"]))]))))
    for start, end, replacement in sorted(changes, reverse=True):
        text = text[:start] + replacement + text[end:]
    text = re.sub(r'(\r?\n){4,}', newline * 3, text)
    expected_names = (bom + text).encode("utf-8")

    additions = []
    assigned = set()
    for source, targets in NAME_SOURCES.items():
        body = (base_names if source.startswith("v:") else names)[source.removeprefix("v:")]
        for tag in targets.split():
            assert tag in tags and tag not in assigned and tag not in names, tag
            assigned.add(tag)
            additions.append((tag, person_fields(body)))
    static_tags = {tag for tag in tags if not re.fullmatch(r"D\d\d", tag)}
    assert static_tags <= names.keys() | assigned, sorted(static_tags - names.keys() - assigned)
    for tag, body in additions:
        for sex in ("male", "female"):
            assert get(get(body, sex, []), "names"), (tag, sex)
        assert get(body, "surnames") or get(get(body, "male", []), "surnames"), tag
    new_names = ("# Generated by _tools/portraits/repair_identity.py.\n"
                 "# Existing CWIC/vanilla regional name lists; see NAME_SOURCES for provenance.\n"
                 "# Dxx civil-war countries deliberately use native parent/fallback behavior.\n" +
                 "\n\n".join("\n".join(render_names([b])) for b in sorted(additions)) + "\n")

    base_sprites = sprite_index((game / "interface").rglob("*.gfx"))
    profiles = {}
    sprite_defs = []
    for region, female_region in FEMALE_REGION.items():
        folder = MOD / "gfx/leaders/_espionage" / region
        # Use explicitly labelled generic operatives, not named historical people
        # or the unclassified novelty/military costume portraits in this folder.
        candidates = {}
        for path in sorted(folder.iterdir()):
            if "generic_operative" in path.stem or path.stem.startswith("generic_south_asian_operative"):
                if path.suffix.lower() in (".dds", ".png", ".tga"):
                    candidates.setdefault(path.stem.lower(), path)
        male = []
        ordered = sorted(candidates.values(), key=lambda p: int(re.search(r"(\d+)$", p.stem)[1]))
        for i, path in enumerate(ordered[:4], 1):
            name = f"GFX_CWIC_operative_{region}_{i}"
            sprite_defs.append(("spriteType", [("name", f'"{name}"'),
                ("texturefile", f'"{path.relative_to(MOD).as_posix()}"')]))
            male.append((None, f'"{name}"'))
        # Base-game generic civilian faces cover genders/regions without suitable
        # CWIC operative art. Reuse sprites; do not copy vanilla image files.
        if not male:
            male = [(None, f'"GFX_portrait_generic_{female_region}_male_{i:02}"') for i in range(2, 6)]
        female = [(None, f'"GFX_portrait_generic_{female_region}_female_{i:02}"') for i in range(2, 6)]
        for _, ref in male + female:
            if not ref.startswith('"GFX_CWIC_'):
                _, texture = base_sprites[ref.strip('"').lower()]
                assert (game / texture).is_file(), texture
        profiles[region] = [("male", male), ("female", female)]

    # A neutral last resort, using the engine's existing operative silhouette.
    sprite_defs.append(("spriteType", [("name", '"GFX_CWIC_operative_unknown"'),
                         ("texturefile", '"gfx/leaders/operative_unknown.dds"')]))
    operative = [("default", [("operative", [(sex, [(None, '"GFX_CWIC_operative_unknown"')])
                                            for sex in ("male", "female")])])]
    for continent, region in CONTINENTS.items():
        operative.append(("continent", [("name", continent), ("operative", profiles[region])]))
    specific = {}
    for tag, country_path in tags.items():
        path = MOD / "common" / country_path
        if not path.exists():
            continue
        culture = re.search(r"graphical_culture_2d\s*=\s*(\w+)", path.read_text(encoding="utf-8-sig"))
        if culture and culture[1].startswith("eastern_european"):
            specific[tag] = "Eastern_Europe"
        elif culture and culture[1] == "indian_2d":
            specific[tag] = "South_Asian"
    for region, target_tags in OPERATIVE_EXCEPTIONS.items():
        for tag in target_tags.split():
            assert tag in tags, tag
            specific[tag] = region
    for tag, region in sorted(specific.items()):
        operative.append((tag, [("operative", profiles[region])]))
    op_text = ("# Generated by _tools/portraits/repair_identity.py; identical with or without DLC.\n"
               "# Native operative pools, with CWIC generic art and inherited vanilla civilian fallbacks.\n" +
               "\n\n".join("\n".join(render([b])) for b in operative) + "\n")

    thumbnails = {}
    for person in ("Qassem_Munaser", "Mohamed_bin_Hussein"):
        source = f"gfx/leaders/CSA/Royalists_Commander_{person}.dds"
        dest = f"gfx/interface/ideas/CWIC_generic/{person}.dds"
        thumbnails[dest] = source
        for suffix, texture in (("", source), ("_small", dest)):
            sprite_defs.append(("spriteType", [("name", f'"GFX_CWIC_{person}{suffix}"'),
                                                ("texturefile", f'"{texture}"')]))
    gfx_text = ("# Generated by _tools/portraits/repair_identity.py.\n" +
                "\n".join(render([("spriteTypes", sprite_defs)])) + "\n")
    outputs = {
        names_path: expected_names,
        MOD / "common/names/10_cwic_names.txt": new_names.encode("utf-8"),
        MOD / "portraits/10_cwic_operative_portraits.txt": op_text.encode("utf-8"),
        MOD / "interface/CWIC_identity_portraits.gfx": gfx_text.encode("utf-8"),
    }
    if args.check:
        for path, data in outputs.items():
            assert path.read_bytes() == data, f"Needs regeneration: {path}"
    else:
        for path, data in outputs.items():
            path.write_bytes(data)
        from PIL import Image, ImageOps
        for dest, source in thumbnails.items():
            with Image.open(MOD / source) as im:
                ImageOps.fit(im.convert("RGBA"), (65, 67), Image.Resampling.LANCZOS,
                             centering=(0.5, 0.15)).save(MOD / dest, pixel_format="DXT5")
    for dest, source in thumbnails.items():
        assert (MOD / dest).is_file() and (MOD / source).is_file()
        import struct
        header = (MOD / dest).read_bytes()[:128]
        assert header[:4] == b"DDS " and struct.unpack_from("<II", header, 12) == (67, 65)

    # Check the actual virtual filesystem, including whole .gfx files hidden by
    # same-path mod overrides. No DLC directories are part of this validation.
    sprites = sprite_index(p for p in (game / "interface").rglob("*.gfx")
                           if not (MOD / p.relative_to(game)).exists())
    sprites.update(sprite_index((MOD / "interface").rglob("*.gfx")))

    def validate_portrait(ref, context):
        ref = ref.strip('"')
        texture = ref if ref.lower().startswith("gfx/") else sprites.get(ref.lower(), (None, None))[1]
        assert texture and ((MOD / texture).is_file() or (game / texture).is_file()), (context, ref, texture)

    for key, body in parse(MOD / "portraits/10_cwic_operative_portraits.txt"):
        for sex in ("male", "female"):
            pool = get(get(body, "operative", []), sex)
            assert pool, (key, sex)
            for _, ref in pool:
                validate_portrait(ref, (key, sex))
    character_count = 0
    for path in (MOD / "common/characters").glob("*.txt"):
        for key, characters in parse(path):
            if key != "characters":
                continue
            for token, body in characters:
                character_count += 1
                for role, slots in get(body, "portraits", []):
                    for size, ref in slots:
                        if isinstance(ref, str) and ref.strip('"'):
                            validate_portrait(ref, (path.name, token, role, size))
    assert not any(re.fullmatch(r"D\d\d", k) for k, _ in parse(names_path))
    print(f"Validated {len(static_tags)} permanent tags with name lists; {len(additions)} supplemental lists.")
    print(f"Operatives: 7 continents, {len(specific)} country exceptions, both genders, no DLC dependencies.")
    print(f"All nonempty portrait references resolve for {character_count} named characters without DLC.")


if __name__ == "__main__":
    main()
