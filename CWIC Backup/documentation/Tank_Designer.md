# Tank Designer - Developer Guide

How the NSB tank designer is wired, and how to change its models, icons, names and modules.
All game paths are under `Cold War Iron Curtain/`. Tools and their data live in `CWIC Backup/tools/`.

## Structure

Every armoured vehicle is a **role on one of three hulls**. A role is a `duplicate_archetypes` root in
`common/units/equipment/x_tank_chassis.txt`, and the hull tiers are in `tank_chassis.txt`.

| Hull | Tiers | Roles |
| --- | --- | --- |
| `light_tank_chassis` | 0-9 (1939-2010) | tank, APC, IFV, tank destroyer / ATGM, SP artillery, SPAA |
| `medium_tank_chassis` | 0-9 | MBT, Heavy APC, Heavy IFV, tank destroyer / ATGM, SP artillery, SPAA |
| `heavy_tank_chassis` | 0-4 (1939-1955) | tank, tank destroyer, SP artillery |

- Legacy (non-NSB) rows were moved into these families with `archetype = <role root>`. So one
  sub-unit `need` serves both DLC profiles.
- **Role tokens are hardcoded in the binary.** Only six tokens become selectable roles:
  `anti_tank` (TD/ATGM), `artillery`, `anti_air`, `flame` (= APC), `rocket` (= IFV), and
  `amphibious` (unused). The dropdown label is our localisation (`designer_l_english.yml`). Custom
  `type` tokens such as `light_armor` work for module eligibility, but never become a role.
- A module's `allow_equipment_type` / `forbid_equipment_type` decides which roles it enables. Every
  gun forbids `flame rocket`, so a gun-armed tank cannot switch to APC or IFV. This is vanilla behaviour.
- A role root is a family only if at least one plain equipment row has `archetype = <root>`.
  Otherwise any sub-unit that needs it silently disappears from the division designer.
- Each new root **and** every derived tier id must be listed in `common/script_enums.txt` under
  `script_enum_equipment_bonus_type`.
- Equipment bonuses name the designer family (`medium_tank_chassis`), never a legacy archetype
  (`mbt_equipment` has no members). Technology bonuses use `armor_light/medium/heavy` or
  `infantry_vehicles_apc`.

## Slots

The layout is 5 mandatory slots plus `tank_special_slot_1..15`. **20 positions is an engine cap**:
`pos_custom_module_slot_window_20` never renders. Every special slot is dedicated to specific
categories. Slots that must be mutually exclusive share one slot, because there is no
`conflicts_with` key.

- Never use `special_type_slot_N` in tank content (it collides with plane airframes).
- Each blueprint file under `interface/equipmentdesigner/tanks/` lists its own slots. A slot change
  has to touch every one of those files. A missing slot errors only when that hull's designer opens.
- A new module category needs its slot and a single-category `count < 2` limit on the archetypes, in
  the same edit. Multi-category limits are rejected.

## Modules

- All modules are in `common/units/equipment/modules/00_tank_modules.txt`.
- Unlock them **only** from `common/technologies/NSB_armor.txt` or `NSB_armor_modules.txt`. The
  validator scans nothing else.
- Module technologies unlock modules only, never `enable_subunits`.
- The icon is `GFX_SMI_<module>`, declared in `interface/cwic_tank_rework_icons.gfx`.
- If a module multiplies attack stats, AI recipes that use it must also carry AP and HE ammunition.
- AI recipes live in `common/ai_equipment/generic_tank.txt`: one recipe per hull, gated on that hull's own tech.
- Balance values in the validator are hardcoded. Grep the module id in
  `validate_military_reworks.py` before you change a stat.

## Scripted designs

| File | What it creates |
| --- | --- |
| `CWIC_tank_designer_effects.txt` | `cwic_create_starting_tank_variants`: the bookmark dispatcher. Calls national helpers in ascending tier order. |
| `CWIC_national_tank_presets.txt` | USA/SOV medium presets and APC/IFV carrier presets |
| `CWIC_national_armour_naming_presets.txt` | Historical designs for tiers a bookmark reaches |
| `CWIC_research_armour_naming.txt` | Historical designs for later tiers, fired by `on_research_complete` in `NSB_armor.txt` |
| `CWIC_armour_supply_effects.txt` | `cwic_supply_<legacy tier>`: producer designs for focus/event/decision hand-overs |
| `CWIC_tank_bookmark_research.txt` | 1980 major-producer tech grants |

Every block is guarded the same way:

```
if = {
	limit = { has_dlc = "No Step Back" tag = XXX NOT = { has_country_flag = cwic_named_<gen>_created } }
	create_equipment_variant = { ... show_position = no icon = GFX_... allow_without_tech = yes }
	set_country_flag = cwic_named_<gen>_created   # after creation, never before
}
```

- `show_position = no` is required. Without it the name gains a `Mk0` suffix.
- `icon` is required. Without it the designer offers the pool, but the design does not take it.
- Use exactly one `has_tech` per guard. `allow_without_tech` already covers the modules.
- Only one system creates a given (producer, generation): bookmark tiers go in naming presets, later
  tiers go in research naming.
- Bookmark bootstrap order in country history: `set_technology` (chassis techs) ->
  `cwic_create_starting_tank_variants = yes` -> any `cwic_supply_*` calls -> `set_oob`. Variants
  created inside an OOB are too late.
- A design belongs to its **producer**. The producer resolves as producer, then creator, then owner,
  then OOB tag. Look up and bootstrap the tech on that tag.
- `add_equipment_to_stockpile` takes `type amount variant_name producer`. It does **not** take
  `creator`, and passing it silently drops the whole grant.
- For a legacy armour hand-over (focus, event, decision), add an
  `if = { limit = { has_dlc = "No Step Back" } }` branch that calls `cwic_supply_<tier>`. Then hand
  over by `variant_name`, and keep the legacy `else`. A legacy `set_technology` for
  `main_battle_tanks_N` / `light_tanks_N` / `heavy_tanks_N` needs its `nsb_*` counterpart.

### Manifests

The preset effect files are pinned by JSON manifests in `CWIC Backup/tools/tank_designer_data/`:

- `National_Tank_Preset_Manifest.json`
- `APC_IFV_Preset_Manifest.json`
- `Tank_Naming_Preset_Manifest.json`
- `Research_Naming_Manifest.json`
- `Armour_Supply_Manifest.json`

**Edit the manifest and the effect file together.** The validator fails on any divergence.
Recipes are shared per generation; only the name differs per country.

## Names and localisation

- A national design's name is the live string of `<TAG>_<legacy_family>_<index>`, in
  `equipment_country_l_english.yml` or `<TAG>_equipment_l_english.yml`. The manifests record file
  and line, and the validator re-reads them.
- **To fix a name, fix that loc key.** Then update the manifest row, the preset `variant_name`, and
  the icon. There is no override list.
- Hull, module and technology names: `tank_modules_l_english.yml`, `nsb_armor_l_english.yml`,
  `designer_l_english.yml`.
- Loc is ASCII and English only. Only section-sign colour codes are allowed as non-ASCII.
- `.yml` files keep their UTF-8 BOM. Script and GUI files must never have one. Check the bytes.

## Icons (designer and production)

- `gfx/interface/equipmentdesigner/graphic_db/00_tank_icons.txt` is **generated**. Edit `ROLES` or
  the rules in `build_designer_graphic_db.py`, then run:
  `python3 "CWIC Backup/tools/build_designer_graphic_db.py"` (add `--check` to verify only).
  Never blank this file: a zero-byte file at a base-game path deletes vanilla's pools.
- Pools are keyed on the exact per-generation type (`light_tank_destroyer_chassis_3`). The art comes
  from the non-NSB tech sprite families (`light_tanks_N`, `spaag_N`, `mechanized_infantryN`, ...).
  - The first pool is the Equipment Match: the row the hull's national names come from.
  - A weight-0.5 pool lists the country's alternates.
  - A country uses its own art only within 10 years of the tier. Otherwise the mandatory `default`
    block applies.
- The designer repaints from equipment type when the role changes. Do not script it.
- Per-country tech icons are `GFX_<TAG>_<technology>_medium` in `interface/<TAG>_techs.gfx`. Match
  texture names case-insensitively.
- The production line uses the family's legacy art, not the NSB tech sprite. Do not add per-country
  `nsb_*` sprites.

## Blueprints

- The designer background is `GFX_cwic_tank_blueprint_background` (`interface/tank_designer_view.gui`).
- A custom outline is window `equipment_designer_<type>_<tag>` in
  `interface/equipmentdesigner/tanks/tank_chassis_<type>_<tag>.gui`, drawing `GFX_TC_<type>_<tag>`.
  Lookup order is `<type>[_TAG]`, then `<archetype>[_TAG]`.
- Art is drawn at 508x206 and shipped at 508x248, padded at the bottom. Use uncompressed 32-bit BGRA
  DDS with no mips.

## 3D models

- The battlefield model is `<TAG>_<sub_unit>_<visual_level>_entity`. A missing entity is silent and
  leaves the default-model selector empty.
- National models live in `gfx/entities/<TAG>_*.asset`.
  `gfx/entities/zz_CWIC_armor_entity_aliases.asset` fills gaps by cloning. The `zz_` prefix makes it
  load last.
- **Never alias a name that a national asset already declares.** The alias would overwrite the
  national model. Aliasing over *vanilla* WWII entities is intended.
- Troop carriers clone `mechanized_entity` (marines: `mechanized_marine_entity`), never a tank.
- Level count is the consumed hull's max `visual_level` + 1, including vanilla rows. IFV reaches 7;
  light AA and heavy reach 4.
- To force a model on a template, use `override_model`.

## Tech tree

- Chassis columns are in `NSB_armor.txt`, and each tech's `@year` row must match its `start_year`.
  `y = @1955` and `y = 6` are the same cell, so resolve the anchors before checking for collisions.
- Gridbox contents render offset from their declared x. Place year labels by measuring a capture.
  When condensing, shift whole blocks, never a single column.

## Validation

```bash
python3 "CWIC Backup/tools/validate_military_reworks.py" --tank-self-test
python3 "CWIC Backup/tools/validate_military_reworks.py" --tank-balance-report --tank-module-balance-report --tank-envelope-report
```

- This is static verification only; it says nothing about balance. Test in game with a fresh
  campaign, because saves are not migrated.
- Don't run the validator while a `-debug` game is open. Its negative fixtures temporarily rewrite
  `mechanized*.txt`, and the game hot-reloads them.
- The balance workbook in `tank_designer_data/` is frozen. Never rewrite it with `openpyxl`, which
  drops the cached formula values.
- The balance-report command currently fails because 20 newer modules (night vision, ploughs,
  RWS, AA ammo, ...) have no row in the frozen workbook. That failure is expected.

Known ignorable log lines:

- `equipmentdesignerview.cpp:3657 Failed to change role` when the design is already in that role.
- `Unknown equipment type: modern_tank_chassis / super_heavy_tank_chassis`, and other base-game
  graphic-db references to chassis this mod removed.
