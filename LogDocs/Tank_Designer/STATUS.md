# Status

Branch `tank-designer-and-doctrine-rework-test`. Last updated 2026-09-24.

## Where the project stands

Tier 1 and Tier 2 of the original completion plan are shipped and stable. Bookmark
presets and the NSB OOB migration are committed, and the 20-position designer is live
and confirmed in game.

**The three-hull restructure is shipped and owner-QA-accepted as of 2026-09-12.** Every
armoured ground vehicle is a role on the light, medium or heavy hull; the two standalone
carrier designer families are retired; the designer is 20 positions with fifteen fully
specialized special slots; and designer carrier output reaches the battlefield through the
six rewired carrier battalions. Phases 1-5 of Finding 16's implementation order are done
and confirmed in game on all four USA profiles. `DECISIONS.md` carries the architecture,
Finding 16 the measured blast radius.

What remains is the mass non-NSB to NSB conversion - historical OOBs, naming, 2D art and
entities - plus the historical coverage sweep and the deferred focus-grant variant mapping.
**The artillery/AA convergence shipped 2026-09-13 (Finding 26), so no standalone armour family
is left: every armoured ground vehicle is a role on the light, medium or heavy hull.** Sixty-seven
legacy rows are DLC-gated, leaving seven ratified exceptions. The amphibious thread is closed for
good by the owner's 2026-09-13 ruling: marines and paratroopers get no custom vehicles, every APC
and IFV serves them, and no amphibious role will be authored.

**All twelve role families now have a consuming battalion AND a plain equipment member, as of
2026-09-17 (Findings 31 and 33).** The Heavy APC and Heavy IFV roles gained
`heavy_mechanized_infantry` and `heavy_armored_infantry`. Chasing why those two would not appear
in game found the deeper defect: **a `duplicate_archetypes` role root whose only members are
derived tiers cannot satisfy a sub-unit's `need`**, which had also left `medium_sp_anti_air_brigade`
and `heavy_tank_destroyer_brigade` unequippable since 2026-09-13. Six plain equipment rows and a
new validator contract close it. The session also found the baseline red on an untouched tree
from a stale negative fixture - Finding 32.

**Conversion tranche 1 and research-time naming shipped 2026-09-17 (Findings 35 and 36).** All
fifteen chassis families now have a bookmark starting design - five had none at any tier, which
meant five battalions began every campaign with nothing to build - and historical names are no
longer limited to tiers a bookmark date reaches: 386 named designs across 22 generations arrive
on research completion. The 2026-09-13 conversion measurement is superseded; the naming debt
was 672 rows, not 979, and only 4 of them were ever addable under the bookmark contract.

**Every armour hand-over in focuses, events and decisions now works on NSB and names a real
vehicle, as of 2026-09-24 (Finding 53).** `BUL_Soviet_T55s` hands over Comecon's `T-55`, not
`CWIC Export Main Battle Tank 1950`. The sweep also found 437 event and decision grants that awarded
nothing on NSB (the whole weapon-purchasing market included), 175 equipment bonuses and 11
technology bonuses that reach nothing on either profile, and 26 legacy tank-technology references
with no NSB counterpart. All of them are fixed, and owner in-game QA accepted them 2026-09-24.

### Committed checkpoints

| Commit | Change |
| --- | --- |
| `a997a48e0e` | Tools moved under `CWIC Backup/tools/`; root `tools/` paths are stale |
| `368fa4815c` | All ten tank special slots renamed `tank_special_slot_1..10`, avoiding plane localisation collisions |
| `b2cd5694b9` | `zz_CWIC_armor_entity_aliases.asset` (3,019 aliases) replaces the old level-0-only file |
| `88c94a5b1c` | Fourteen USA/SOV national medium presets, producer-aware OOB names, duplicate guards, module estimator correction |
| `80304e2030` | Newest bookmark design only in the default production tab |
| `660f8984ae` | APC designer family |
| `faddc3dd5e` | IFV designer family |
| `eb708e3691` | APC/IFV bookmark presets and NSB carrier OOB migration (Step 2) |
| `2636424db7` | APC designer role moved to the `flame` token, freeing `amphibious`; phases 6 and 7 landed with it |

### Step 2 acceptance, 2026-09-08

Owner QA passed and committed. Both bookmarks load, presets load, stockpiles and
factory lines exist, `error.log` is acceptable. AI production is deferred to a single
final pass once the remaining designer content is in, at the owner's direction.

The batch added 10 generic carrier designs, 572 national carrier designs and 100 named
carrier OOB requests over the `faddc3dd5e` baseline. Bootstrap site count unchanged at
76: the carrier grants land inside the existing sites.

Two failures the first gate run reported, both resolved:

1. **Global design-name uniqueness was the wrong invariant.** It produced 382 false
   `duplicate tank recipe name` failures. A design name is only unique *per country*,
   and ten names legitimately span two chassis tiers because an incomplete national
   ladder shifts a vehicle relative to the common ladder. `_variant_recipes()` is now
   keyed by `(name, chassis)`; `_variant_recipes_by_name()` marks a name ambiguous
   rather than silently keeping the last recipe.
2. **Three medium-tank OOB requests contradicted the producer-resolution rule.** They
   named a generic design with SOV as creator, and SOV creates national names at every
   medium tier. Resolved by naming the Soviet design: `KPA_1949_nsb.txt:594` to
   `T-34-85` (historically correct), `BUL_1949_nsb.txt:183,193` to `T-44` (Bulgaria did
   not field T-44s; the request's chassis tier, not the name, is the ahistorical part).
   These were latent breakage, not a regression.

## Merge readiness inventory, 2026-09-24

Owner question: can the branch merge into `development-branch`? **Verdict: yes, mechanically,
with three pre-merge housekeeping items and a known-open list that is content work, not a
blocker.** Everything below was measured, not assumed.

### Merge mechanics

- Branch is 84 commits ahead of and 24 behind `origin/development-branch` (base `4a999ae3f3`,
  2026-09-03), and one local commit ahead of its own remote. Finding 53 is uncommitted.
- A trial merge of the branch **plus the uncommitted Finding 53 work** conflicts in exactly three
  files, all SOV focus trees: `SOV_Chinese_Civil_War_Branch.txt` and `SOV_Korean_War_Branch.txt`
  (deleted on `development-branch` by `d9f64b66e4`, which moved those branches into
  `common/decisions/SOV.txt`) and `SOV_Stalin.txt`. Our side of all three is Finding 1/53 armour
  branches plus one doctrine category line that no longer exists upstream. **Resolution: take
  `development-branch`'s side of all three.**
- On that resolved tree, `--tank-self-test` **passes**: 6639 stockpile grants and 1573 armour
  hand-overs. The six fewer hand-overs are the deleted SOV branches, and upstream's new SOV decisions
  add no ungated legacy armour. Static only; the merged tree was not launched.

### Pre-merge housekeeping

1. **Commit Finding 53** (170 tracked files plus `CWIC_armour_supply_effects.txt` and
   `data/Armour_Supply_Manifest.json`). Leave `.gitignore` unstaged; it is someone else's work.
2. **`interface/popupwindow.gui` is already committed on this branch** (`660f8984ae`, +16 lines, two
   hidden `iconType`s). README lists it as carrying other people's work. The owner must confirm
   it belongs in the merge.
3. **Non-English localisation was edited on this branch** (`ff036b399b`, `73c23beb19`): 72 lines deleted
   across `french/`, `japanese/` and `russian/` `designer_l_*` / `tank_modules_l_*`. Every deleted
   key names a removed vanilla chassis (modern, super-heavy, amphibious), so it is cleanup, but it breaks
   the English-only rule. Tell the translation owners, or revert those hunks before merging.

### Known-open, grouped as the owner asked

**3D models - the weakest area.**
- `zz_CWIC_armor_entity_aliases.asset` loads last, and the validator pins 140 aliases that shadow a
  national entity (`native_overrides = 140`). Measured on the merged tree, 63 of those names are
  `<TAG>_tank_destroyer_0..4_entity` for 13 Warsaw Pact tags, where `<TAG>_units_tanks.asset`
  authors real TD models (`SOV_tank_destroyer_1_mesh`, `b742529647`, 2026-07-12). The alias clones
  the tag's medium tank over them. The fresh log shows 141
  `Duplicate of ..._entity added to entity system` lines for these tags. Recommended fix before or
  right after merging: drop every alias whose name a national asset already declares, and lower the
  pin to 0. Authored models then win; it needs one in-game look at a Warsaw Pact TD battalion.
- Twelve hull-consuming sub-units still have zero aliases (Finding 28 "Coverage still owed"), so
  they render the default mesh. This is content authoring.
- Rendered battlefield models have never been confirmed in game for SP artillery, SPAAG, TD or ATGM
  battalions (Finding 28).

**GFX.**
- The per-type blueprint lookup (`<type>_<tag>`) is unconfirmed in game. Only USA `M47 Patton` has a
  custom blueprint, and 2,320 national designs fall back to the untagged root outline (Finding 52).
  That is a worklist, not a defect.
- The 16 zero-byte plane, ship and HQ `graphic_db` files are identical on `development-branch`, so
  this branch did not cause them. The 8 blank tank files are intentional and validator-pinned;
  `00_tank_icons.txt` replaces them.
- Fresh owner log, 2026-09-24 13:47: **0** `Couldnt find texticon` lines, so Finding 21's spam is
  gone in practice. The 8 `JAP_light_armor_*_entity` graphic-database misses come from vanilla
  `dlc025_axis_armor_pack`, not this mod; the mod's `00_tank_icons.txt` references 4,499 entities
  and all resolve.

**Edge cases not yet exercised.**
- A producer receiving a supplied design before researching its hull (Finding 53 risk 1).
- The French and West German 1949 starts, every non-USA tag at either bookmark, and long-run AI
  production and factory assignment for `land_apc` / `land_ifv` ("Not yet verified, any batch").
- Tranche 2 QA: `light_tank_ifv_chassis_6/7/8` research helpers and the 23 bookmark rows.
- Designer UI at 1920x1080 and 2560x1440, at 1.0x and 2.4x.

**Content still owed, none of it merge-blocking.** Owner ruling on the ATGM stockpile residue
(`DECISIONS.md`). OOB references for the four carrier battalions, and 16 awaiting OOB requests.
The mass non-NSB to NSB conversion. The `--tank-balance-report` command is red on clean `HEAD`
(module mirror missing 20 ids plus the retired `flamethrower` row). No balance acceptance exists
for any designer content.

## Open findings

### Finding 1: legacy armour focus awards were never migrated to NSB designer equipment - resolved 2026-09-08

Reported case: `BUL_Soviet_T55s` shows no completion award though it should grant 200
`mbt_equipment_3` from CUM.

Confirmed cause, and it is our own NSB designer change rather than a focus scripting
bug: every legacy armour equipment entry is reparented onto a designer archetype.
`tank_medium.txt` puts all 10 `mbt_equipment_*` on `archetype = medium_tank_chassis`,
and `tank_heavy.txt` (5), `tank_light.txt` (6) and `mechanized.txt` (18) do the same.
So `add_equipment_to_stockpile = { type = mbt_equipment_3 producer = CUM }` names
equipment that now belongs to a designer family with no design behind it for that
producer. Nothing is granted; the reward renders empty.

To be explicit, because an earlier draft got this wrong: **two `completion_reward`
blocks in one focus is not the cause here.** That pattern is a real and separate
issue - see `GOTCHAS.md` - but it is not what `BUL_Soviet_T55s` demonstrates.

Scope owed: **301 `add_equipment_to_stockpile` grants across the focus trees name a
legacy armour type, and all 301 specify a producer.** They span 22 distinct types, led
by `mbt_equipment_3` (57), `mbt_equipment_2` (44), `lt_equipment_2` (31),
`mbt_equipment_0` (30), `ht_equipment_3` (25) and `mbt_equipment_1` (24), plus 28
mechanized/heavy-mechanized grants. Heaviest files: `60s_Generic.txt` (41),
`60s_ITA.txt` (26), `60s_SOM.txt` (26), `60s_VIE.txt` (26).

Each grant needs a decision, not a mechanical rename: which designer chassis and which
named design the awarding producer hands over, on both the NSB and non-NSB profiles.
The carrier presets are the model - same producer-resolution rule, same named national
designs. This wants a validator contract pinning every focus armour grant to a design
some bootstrap creates, exactly like the OOB `force_equipment_variants` check.

Resolution: every active, in-scope legacy armour grant now keeps its original
non-NSB branch and gains an NSB branch that creates an obsolete producer-owned
export design before granting the matching chassis variant. The mapping uses the
largest designer chassis whose ratified introduction year is no later than the
legacy equipment year. This pass added 314 migrations; 9 existing export branches
were retained. The validator now checks all 323 in-scope grants, their chassis and
variant pairs, producer helper calls, and the 8 intentional equipment-type exceptions
(16 grants).

The 11 explicitly reference-only focus paths remain outside this contract:
`FOR HOTFIX/`, `Need Finished/`, `OUTDATED_PRC_60s.txt`, `Old/`, `Toberemoved/`,
and `Trees for 0.35/`. Static validation passed; no live QA or balance acceptance
is claimed for this migration.

~~Deferred follow-up: generic `CWIC Export ...` `variant_name` values instead of historical
preset variants.~~ **Resolved 2026-09-24 by Finding 53.** Every grant now hands over the
producer's historical design, and the export designs and the year-rule chassis mapping are gone.

### Finding 2: base gasoline engine outranked the CWIC petrol ladder - resolved

The script-owned `tank_gasoline_engine` was the `Petrol_0` parent and the default
engine slot, but its `maximum_speed` multiplier was 0.15, above every CWIC petrol
tier (`Petrol_0` 0.05, `Petrol_1` 0.07, `Petrol_2` 0.09, `Petrol_3` 0.11). It is
enabled by the base NSB armour tech (`NSB_armor.txt:63`); `Petrol_0` remains gated
at `NSB_armor.txt:1074`.

The ladder is corrected in place: `tank_gasoline_engine.maximum_speed` is 0.03,
below `Petrol_0` at 0.05. The module remains the pre-WW2 parent/base definition;
`Petrol_0` is the starting template. The English localisation now calls the former
"Gasoline Engine" **"Pre-WW2 Gasoline Engine"**.

Every tank-bootstrap country-history site grants `nsb_engines`, so `Petrol_0` is
available through the same starting-tech contract. The two scripted effects now route
all 576 national and 40 generic starting variants to `Petrol_0`; the four USA
manifest entries are synchronized. The three archetype default slots elsewhere remain
`tank_gasoline_engine` under the existing parent/default decision and were not changed
by this scoped preset migration.

The full static report passes with the inventory line unchanged. Relative to the
previous engine-only report, the 11 sampled tank envelope estimates changed as
follows (`speed`, `fuel_usage`):

| Recipe | Speed | Fuel |
| --- | ---: | ---: |
| Heavy Tank I | -3.13 -> -2.59 | -2.45 -> -2.02 |
| Heavy Tank II | -2.69 -> -2.14 | -2.45 -> -2.02 |
| Heavy Tank IV | -3.25 -> -2.69 | -2.45 -> -2.02 |
| Heavy Tank V | -3.81 -> -3.24 | -2.45 -> -2.02 |
| WWII Tank 1 | -4.07 -> -3.51 | -1.45 -> -1.02 |
| WWII Tank 2 | -4.63 -> -4.06 | -1.45 -> -1.02 |
| MBT II | -5.19 -> -4.61 | -1.45 -> -1.02 |
| MBT III | -5.75 -> -5.16 | -1.45 -> -1.02 |
| Light Tank I | -5.02 -> -4.43 | 0.35 -> 0.78 |
| Light Tank II | -5.58 -> -4.98 | 0.35 -> 0.78 |
| Light Tank IV | -7.70 -> -7.08 | 0.35 -> 0.78 |

These are diagnostic estimates only; no live balance acceptance is claimed.

### Finding 3: presets show the generic carrier icon - resolved 2026-09-08

`BTR-40` rendered with the generic APC picture. `apc_chassis_*` and `ifv_chassis_*`
declared no `picture` of their own, so every carrier design inherited
`archetype_motorized_equipment` from the `mechanized_equipment` archetype
(`mechanized.txt:11`) and `archetype_mechanized_heavy_equipment` from
`mechanized_heavy.txt:12`.

Stats are the good news: the owner confirms legacy and new NSB APC/IFV stats match
closely, so the module baselines are landing where they were aimed.

Per-design art was measured and rejected, not skipped. The designer icon compositor
is an explicit tank-family graphics contract, not a generic consequence of having
modules: vanilla `super_heavy_artillery_equipment_1` has `module_slots = inherit`
and still keeps its static archetype picture, and vanilla enumerates profile art as
`GFX_<tag-or-generic>_<size>_<profile>` in `interface/tank_profiles.gfx` with no
mechanized family. Vanilla NSB gives mechanized no generated icons either.

Resolution: one static picture per hull tier. Each of the sixteen hulls declares
`picture = cwic_apc_chassis_N` / `cwic_ifv_chassis_N`, and sixteen matching
`GFX_..._medium` sprites in `interface/cwic_tank_rework_icons.gfx` point at the
already-shipped neutral `gfx/interface/technologies/apc_N.dds` and `ifv_N.dds`
textures - the same art the corresponding hull technology icon uses, so the tech
tree and the production tab agree. Zero new, copied or renamed assets. The
validator pins the picture value, sprite registration and texture existence per
hull, with four negative fixtures.

This is a per-hull-tier icon, not per-vehicle: every APC tier-2 design still shares
one picture. That limit is now a recorded consequence of the engine's graphics
contract rather than an open question. Static verification only; the rendered icon
has not been confirmed in game.

### Finding 4: major-country Petrol_1 bootstrap - resolved 2026-09-09

`nsb_engines0` enables `Petrol_1`, starts in 1950 and costs 2 research. It is now
granted in the NSB starting-technology blocks for USA, SOV, ENG and WGR, immediately
after their existing `nsb_engines` grant. FRA's 1949 NSB bootstrap adds both
`nsb_engines` and `nsb_engines0` before its starting variants are created.

The only national tank preset rerouted is USA's 1950 `M47 Patton`
(`medium_tank_chassis_3`), from `Petrol_0` to `Petrol_1`. The 1950+ scripted-effect
blocks are generic fallbacks shared by every tag, not major-country content, so they
remain on `Petrol_0`; rerouting them would give minors an engine they cannot research.
SOV's 1950 `T-55` already uses `Diesel_1`, and FRA, ENG and WGR have no national tank
presets. Carrier presets remain on `Petrol_0`.

The validator self-test, balance-target report and envelope report pass with the
inventory line unchanged. The module-balance mirror remains incomplete; see the
slot-budget debt note below. French and West German 1949 start behaviour remains
unconfirmed in game. Static verification only; no balance acceptance is claimed.

### Finding 5: stockpile grants silently awarded nothing - resolved 2026-09-08

Found by triaging the four owner playtest logs, then re-confirmed against current
source. Three shapes, all of which parse as valid script and award nothing:

1. **`creator` on `add_equipment_to_stockpile`.** The effect accepts `type`,
   `amount`, `variant_name` and `producer` only. The engine logs
   `effect.cpp:358 Unexpected token: creator` and drops the grant. 246 grants
   carried it: 121 in `SOV_1980_nsb.txt`, 121 in `SOV_1980.txt`, 4 in
   `SWI_1980.txt`. The Soviet block is the entire 1980 armour and aircraft
   stockpile for both profiles, so both bookmarks started with none of it.
   `creator` stays legal and untouched on `force_equipment_variants` and
   `add_equipment_production`, which is why the token looked right.
2. **Transposed equipment ids.** `heavy_mechanized_equipment_1`/`_3` are not
   defined anywhere; the real ids are `mechanized_heavy_equipment_1`/`_3`. Seven
   grants across CUB, DDR, POL, CZE, ISR, TUR and HUN `_1980.txt`. The `_nsb`
   counterparts were already migrated to designer chassis in `eb708e3691`; only
   the non-NSB mirrors were left, and `DECISIONS.md` had recorded them as out of
   the *designer migration*, which is not the same as leaving a dead id in place.
3. **Misspelt and mistyped ids.** `infnatry_eqipment_1` in DOC, TOG and UGA
   `_1980.txt`. Each logs `invalid database object for effect/trigger`.

Also corrected in the same file, both engine-confirmed dead `add_tech_bonus`
categories: `BRA_50s.txt:3601` used `mechanized_equipment` where the declared
category is `cat_mechanized_equipment`, and `BRA_50s.txt:3564` used
`infantry_equipment` where four sibling mod focuses use `infantry_weapons`. Both
bonuses previously applied to nothing.

`validate_stockpile_grants()` now pins all **6220 stockpile grants mod-wide**, not
just the 2349 under `history/` - two thirds live in `common/national_focus/` and
`common/decisions/`, and a blind spot there is exactly where this defect class
would return. It requires no `creator` key, and every `type` must resolve to a
declared equipment id or to a tier its parent family actually declares behind a
`duplicate_archetypes` root, so `light_tank_aa_chassis_1` passes while
`light_tank_aa_chassis_99` does not. Six negative fixtures cover the rejected key,
a transposed id, a technology id used as equipment, the valid derived tier, a
deregistered carrier sprite and a carrier sprite pointing at a missing texture.

The wider scan surfaced nine pre-existing content bugs that are not
tank-designer-owned and that each need their content owner to say what was meant.
They are carried as a named, commented exception set rather than guessed at or
deleted:

| Id | Sites | What it actually is |
| --- | --- | --- |
| `mp_uav_1` | `ISR_1980{,_nsb}.txt:486` | technology in `helicopter.txt` |
| `apc_equipment_1` | `PHI_1950s.txt:586` | `derived_variant_name` only; see known inconsistency 12 |
| `manpads_3` | `USA_80s_CIA.txt:1850,1872` | undeclared |
| `cv_nav_bomber_equipment_6` | `JAP_1950s.txt:437` | undeclared |
| `armor_light`, `armor_medium`, `artillery_light`, `artillery_medium`, `support_artillery` | `PRC_50s_New.txt:2489-2509` | technology categories used as equipment |

Five further invalid `add_tech_bonus` categories appear in the logs outside
`BRA_50s.txt` and were left alone: `air_techs`, `electronic_mechanical_engineering`,
`excavation_tech`, `screen_hull_light`, and `radio` at `BRA_50s.txt:1041`. `radio`
is in a file this pass edited but its correct target is a content judgement - the
declared `radio_tech` category carries exactly one technology - so it was recorded
rather than guessed.

Static verification only.

### Finding 6: the designer module set and GUI are unfinished - 15 shipped against 21 designed

Recorded 2026-09-09 at the owner's direction, because nothing in this folder said it
out loud: the shipped designer is two thirds of the designed one, and the difference
was previously filed as a rejected sketch rather than as owed work.

**Shipped.** Five mandatory slots plus `tank_special_slot_1..10`, every special slot
specialized to a fixed category list, on all five archetypes: `tank_chassis.txt:16-152`
(light), `:271-411` (medium), `:522-660` (heavy), `mechanized.txt:37-164` (APC),
`mechanized_heavy.txt:28-42` (IFV). The GUI declares
`pos_custom_module_slot_window_0..14` at `interface/tank_designer_view.gui:129-215`, and
the validator pins exactly that set at `validate_military_reworks.py:3826-3829` while
printing the literal `15 designer slots` at `:4646-4647`.

**Designed.** 21 positions: drawio page 8 `[REFERENCE] Tank Designer Composition` lays
out Gun, Turret, AP Ammo, HE Ammo, Aiming, Optics, Suspension, Armour, Engine plus
`Slot 1..12`, with a candidate special-module row beneath it. The owner's screenshot is
that page over a designer capture, not a render of current code.

**The gap is two things, and only one of them is the slot count.**

1. Six missing positions and a semantic change: the sketch dedicates AP and HE
   ammunition, aiming and optics, and leaves the other twelve free. The architecture,
   GUI layout, exclusivity model, migration cost and its two unverified engine
   assumptions are ratified in `DECISIONS.md`.
2. Ten of the sketch's eighteen named specials have no module, no technology and no
   balance row: Blow-Out Panels, Anti-Mine Plow and rollers, External Additional Fuel
   Tanks, Unmanned Turret / RWS, Underwater Driving, Integrated Trench Plow, Modular
   Construction, amphibious drive, dozer plough, night vision I-III. Eight families
   from that row do exist (belt autoloaders, APS, ERA, add-on armour, APU, ATGM, smoke,
   thermal sights) - 145 special modules across 18 categories. Drawio page 11 already
   said "None exist in script"; the workbook's `Night & Thermal Vision Effects` tab is
   empty, so all ten families need invented numbers recorded as authored.

**Blast radius, measured.** The expansion is small in content and concentrated in the
validator, because unused optional slots may be omitted from a creation block
(vanilla `GER - Germany.txt:1097-1108`):

| Surface | Count | Needs rewriting? |
| --- | --- | --- |
| Archetype slot blocks | 5 | Yes - six new slots, four re-specialized, exclusivity groups |
| GUI positions | 15 -> 21 | Yes - six positions, one promoted row macro |
| Validator sites | 11 functions/constants | Yes - see the edit list in `DECISIONS.md` |
| National preset blocks | 586 (8,790 special assignments) | No - already-explicit 15 stay legal |
| Generic bookmark blocks | 40 (160 special assignments) | No |
| Focus export blocks | 16 (80 special assignments) | No |
| AI recipes in `generic_tank.txt` | 116 | No, unless a recipe wants a new special |
| Slot localisation keys | 15 -> 21 | Yes - twelve free-slot labels |

**The two gating engine assumptions are now answered.** Positions above 8 work: the
owner's 2026-09-09 designer capture renders the 7 / 7 / 7 layout with the middle row
over the blueprint exactly as ratified, and the top row reads turret, gun, suspension,
armour, engine, AP ammunition, HE ammunition - confirming both the 21-position layout
and the slot 1 / slot 2 ammunition split in game. The multi-category
`module_count_limit` shared budget was **not** authored: `DECISIONS.md` forbids it
before a positive engine test, and a log diff can only disprove such a block, never
confirm its enforcement. The ratified per-category `count < 2` fallback shipped
instead, so the envelope recalibration below is now owed rather than hypothetical.

**Implemented 2026-09-09.** Phases 1 and 2 are done and statically verified; the
self-test line moved from `15 designer slots checked` to `21 designer slots checked`
with every other count byte-identical.

- All five archetypes declare `tank_special_slot_1..16`. Slot 1 is AP ammunition
  (`tank_ammo_kinetic`, `tank_ammo_chemical`, `tank_ammo_missile`), slot 2 is
  `tank_ammo_he`, slots 3 and 4 are unchanged, and slots 5-16 share one 12-category
  free list. `tank_chassis.txt`, `mechanized.txt`, `mechanized_heavy.txt`.
- Each archetype now carries all 18 single-category `count < 2` limits. APC and IFV
  were missing seven (four ammunition, three loader). Those three loader limits are
  load-bearing: without them a twelve-free-slot carrier could mount three loading
  systems.
- `interface/tank_designer_view.gui` declares positions 0-20 at 7 / 7 / 7 with no
  geometry change - `equipment_modules` stays 515x350 and `equipment_preview` 508x248.
- Twelve free-slot labels added; slots 5-16 read `Slot 1`..`Slot 12`, slot 1 is
  "AP Ammunition" and slot 2 "HE Ammunition". The six retired specialized labels are
  gone.
- **A sixth surface the blast-radius table above missed:** the 106 per-hull blueprint
  files under `interface/equipmentdesigner/tanks/` enumerate the slot names by hand.
  All 106 declared only `tank_special_slot_1..10`, so the engine logged
  `containerwindow.cpp: Could not find "tank_special_slot_11" in window module_slots`
  plus a `Requested GUI element not found` assertion the moment a designer opened.
  All 106 now declare 1-16. This was found only by loading the game; nothing static
  pointed at it, which is why the validator now pins the file count and the exact
  ordered slot list per blueprint.
- Validator migrated off cardinality onto `variant_slot_errors()`
  (mandatory-complete plus specials-a-subset, per the vanilla precedent that optional
  slots may be omitted) and `tank_count_limit_errors()`. Eleven negative fixtures were
  added, including one asserting that a multi-category limit block is still rejected
  so the unverified form cannot be introduced by accident.

No preset, OOB, focus or AI-recipe content was edited, as predicted: the 8,790 + 160 +
80 already-explicit special assignments stay legal.

**Remaining plan.** Phases 1 and 2 are closed; these two are not.

3. *Module authoring*, in the order "Next scope" item 6 sets: amphibious (only with
   marine sub-unit supply), night/thermal vision, then the base/other specials. Each
   family needs a category decision, a per-hull eligibility decision, invented numbers
   recorded as authored, an unlock in `NSB_armor_modules.txt` and a `GFX_SMI_*` icon.
   The owner supplied the two source mockups on 2026-09-09 - see `DECISIONS.md` for the
   ladders they fix.
4. *Envelope recalibration.* Twelve free slots let a design mount more specials than
   the frozen envelopes assumed, and the shipped fallback does not cap the total. This
   is known inconsistency 2 in its full form now.

**The render is confirmed, 2026-09-09.** The owner re-checked in game after the
106-file blueprint fix and reports the 21 slots load correctly, on a T-54 /
`medium_tank_chassis_1` Late WW2 Medium Tank Hull. The live `error.log` corroborates
it: zero `Could not find "tank_special_slot_*"`, zero `Requested GUI element not
found`, zero `containerwindow.cpp` lines of any kind, with the designer open. The
pre-fix boot logged 85 slot-lookup failures plus the assertion, so this is a real
before/after and not an absence of evidence. Every one of the 21 positions resolves.

One cosmetic note, not a defect: in the captures the bottom row shows six `+`
affordances and a dark seventh cell. The engine resolves that element - it reports no
missing GUI element - and a `-debug` resolution overlay (`1600x900`, `x720`) is drawn
across exactly that area. Re-check without `-debug` if it ever matters visually.

**Owner direction, 2026-09-09: specialized slot restrictions must still be adjusted.**
21 slots on all five hulls is confirmed final, but slots are to be *locked per hull*
according to which specialized modules that hull may access - amphibious drive belongs
to APC and IFV and must not appear on the medium, MBT or heavy hulls. The shipped
state gives all five archetypes an identical free list, which is correct only while
every free-list category exists on every hull. The per-hull lock model must land in
the same pass as the first hull-restricted module, or that module silently becomes
mountable everywhere. See `DECISIONS.md`.

### Slot budget debt - accepted by owner decision

The owner accepts the per-category `count < 2` fallback and leaves the slot-budget debt
recorded. The envelope path has no tolerance or pass/fail threshold; it prints deltas
only. The estimator already consumes the modules a recipe actually installs, so
nothing in it encodes the old slot-count assumption and no code change follows.

Any future re-cut belongs in the frozen 40-row manifest. This remains a calibration
item, not balance acceptance.

The combined module-balance report remains blocked by pre-existing mirror coverage:
the living CSV reports 246 rows against 266 expected, and the CSV plus Minimal and
Master workbook tables omit 20 already-shipped IDs (`Blowout_Panels_0`, `Dozer_0`,
`Four_Track_0`, `Fuel_Tanks_0`, `Log_0`, `Mine_Plow_0..1`, `Mine_Roller_0..1`,
`Night_Vision_0..5`, `RWS_0`, `Trench_Plow_0` and `tank_aa_ammo_1..3`). The workbook
stays byte-identical and no balance acceptance follows.

### Finding 7: the carrier bookmark validator was dead code and had never run - resolved 2026-09-09

Found while migrating the slot-cardinality sites. `validate_carrier_bookmarks()` in
`validate_military_reworks.py` was defined and **never called from anywhere**, and it
contained a reference to an undefined `SPECIAL_SLOT_CATEGORIES` on its per-slot
legality path - a guaranteed `NameError` that proves the function had never executed
once. So the entire Step 2 carrier contract the `eb708e3691` acceptance notes describe
as checked - 572-preset source coverage, the `MBZ -> MZB` alias, producer tag
existence, per-slot module legality, the per-guard creation contract, dispatcher
interleave order and the manufacturer-bloc technology ordering - was never enforced.

Wiring it in produced 36 failures, and every one was a validator defect rather than a
content defect. The function had been written against a design that was never shipped:

1. Its mandatory-slot category sets named `tank_suspension_type`, `tank_armor_type` and
   `tank_engine_type`, none of which exist anywhere in the mod. The real categories are
   per-type - `Armor_0_W` is `tank_armor_welded`, `Bogie_0` is `tank_suspension_bogie`.
   Now derived from each family archetype's own `allowed_module_categories` so the check
   cannot drift from the archetype again.
2. It passed raw effect files to the bounded block parser, which needs one balanced
   root, so all ten per-hull helpers and the dispatcher read as absent. The helpers and
   the shipped `cwic_create_starting_tank_variants` dispatcher were there all along.
3. Quoted values (`name`, `variant_name`, `version_name`) were fed to a parser that
   deliberately only reads unquoted atoms, and five 1949 production requests wrap their
   payload in `equipment = { ... }`, which the OOB inventory never looked inside.
4. Its recipe expected `tank_gasoline_engine`; the accepted shipped effects use
   `Petrol_0` per Finding 2's engine reroute.

All seven repaired check shapes were re-proven with in-memory mutation probes through
the function's existing `*_override` parameters, so nothing was loosened to make it
pass. Static verification only; this changes no mod content.

### Finding 8: a validator self-test run corrupts a live `-debug` game

Recorded 2026-09-09 because it cost most of an investigation cycle and will do so
again. `run_apc_negative_fixtures()` and `run_ifv_negative_fixtures()` write their
mutated fixtures to the **real** `mechanized.txt` and `mechanized_heavy.txt` paths and
then restore them. A `-debug` game hot-reloads changed equipment files, and the reload
re-registers every `module_count_limit` on top of the existing registry.

Symptom: 2380 `A limit for category X already exists` errors, 1480 of them in
`CWIC_ship_hull_*.txt` files that no one had touched, appearing 90 seconds after load
finished in ten identical bursts - one per re-parse. It reads exactly like a global
engine limit being blown by the slot expansion, and it is not. A clean boot with the
expansion in place and no concurrent validator run reports zero.

**Never run the validator while a `-debug` game is loading or running.** The A/B that
settles any suspected engine regression must hold file writes still on both arms.
### Finding 9: the per-hull slot lock does not need a slot mechanism - the engine already has one

Recorded 2026-09-09 while planning the owner's per-hull lock direction, and it changes
the shape of that work. Restricting a module to certain hulls **cannot** be done through
the free-slot category lists, because a category is shared by all five archetypes - the
free list is per archetype, but a category is global, so putting amphibious drive in
`tank_mobility_auxiliary` makes it legal on any hull whose free slots accept that
category.

The engine's own primitive is module-side and already in use. Vanilla's
`amphibious_drive` at
`<steam>/Hearts of Iron IV/common/units/equipment/modules/00_tank_modules.txt:1372-1397`:

```
category = tank_special_module
allow_equipment_type = amphibious
forbid_equipment_type_exact_match = armor
forbid_equipment_type = { anti_air artillery anti_tank flame }
```

`allow_equipment_type` / `forbid_equipment_type` / `forbid_equipment_type_exact_match`
key off the archetype's own `type = { ... }` set, and the mod's module file already uses
those keys **49 times**. The designer role roots supply exactly the discriminators
needed: `x_tank_chassis.txt:8-15` declares `light_tank_aa_chassis` as
`type = { armor anti_air }`, `:18-25` gives `light_tank_artillery_chassis`
`type = { armor artillery }`, and the APC and IFV archetypes carry `mechanized`
alongside `armor`.

So the lock model is: author the hull-restricted module into an existing category, then
bound it with `allow_equipment_type` / `forbid_equipment_type`. No new slot, no GUI
change, no fifth copy of a category list, and no per-archetype divergence in the free
list. The one open question is what type token distinguishes an APC/IFV from a gun tank
for amphibious purposes - `mechanized` is the obvious candidate and must be confirmed
against the archetype `type` sets before authoring.

### Finding 10: `APU_6` is an orphan module with no unlock - false, closed 2026-09-09

**The claim does not hold against current source and should not be acted on.**
`NSB_armor.txt:1309-1313` declares `nsb_hybrid_engines` with
`enable_equipment_modules = { Diesel_6 APU_6 }`, `research_cost = 2`,
`start_year = 2020` - which is exactly the "2020 grant" the finding proposed as its own
fix. `APU_6` is reachable in play.

The reachability question the finding raised was answered properly rather than spot
checked. A full brace-structured audit parsed every module definition in
`00_tank_modules.txt` and every `enable_equipment_modules` block under
`common/technologies/`, `common/scripted_effects/` and `common/national_focus/`:
**289 modules defined across 47 categories, 0 with no technology unlock.** There are no
orphan tank modules at all, so the suggested validator orphan check would pin an
invariant that already holds. The reverse scan's 163 "undefined" ids are all naval and
submarine modules granted from ship technology files and defined in the ship module
files; they are outside `00_tank_modules.txt` by design, not dead grants.

No source change was made. The finding was stale documentation, not a defect.

### Finding 11: one missing `=` crashed every tank designer - resolved 2026-09-09

Owner-reported: the tank, APC and IFV designers all crashed on open. Cause found in the
log, not guessed:

```
Error: "Malformed token: positionType, near line: 143" in file: "interface/tank_designer_view.gui"
```

`interface/tank_designer_view.gui:140` read
`position = { x=@fixed_btn_mod_col_0 y@fixed_btn_mod_row_0 }` - the `=` after `y` was
missing. Introduced when the position block was rewritten for the 21-slot expansion.

The failure chain is worth writing down because every step is silent:

1. The malformed token aborts the parse of everything after it, so **125 children of
   `tank_designer_view` were dropped** - `module_selector_window`, `close_button`,
   `equipments`, `info` and the rest all logged
   `Could not find "X" in window tank_designer_view`.
2. Opening the designer then laid out against those missing containers and divided by a
   zero dimension: **`Caught signal 8 (SIGFPE)`**, per
   `crashes/hoi4_20260909_183945/exception.txt`. The crash is an integer division by
   zero, not a null dereference, which is why it presents as a hard crash rather than a
   missing panel.

**Why nothing caught it, and what now does.** Brace balance was 0 and every byte check
passed - a missing `=` changes neither. The validator's GUI check matches
`pos_custom_module_slot_window_(\d+)"` by regex, which matches the broken line perfectly,
so `21 designer slots checked` passed against a file the engine could not parse. The
validator now scans every `position` / `size` / `margin` block in
`tank_designer_view.gui` and all 106 blueprint files and fails on any token lacking an
`=`, with the failing file and line number. Mutation-probed: reintroducing the typo
produces
`tank_designer_view.gui:131 has a malformed assignment 'y@fixed_btn_mod_row_0'`.

**Verified by reproduction, not by inspection.** These errors fire at load time with
`no_game_date`, so a plain boot reproduces them without opening the designer. After the
fix a fresh boot reports **zero** `tank_designer_view.gui` errors and **zero**
`Could not find ... in window` lines, and the total `Could not find` count is back to 54
- byte-identical to the HEAD baseline, and all of it unrelated mesh/animation asset
noise. The 9 remaining `Malformed token` lines mod-wide are all in files untouched this
session (`USA_1980s_*` events, `HAI_1949.txt`, `PQC_1950s.txt`, `INO_Military_50s.txt`,
`KMT_dynamic_modifiers.txt`) and are pre-existing content bugs.

The designer opening successfully still needs an owner check; what is proven here is
that the parse error which caused the crash is gone.

**Lesson for this folder: brace balance is not a syntax check.** Any pass that rewrites
script or GUI assignment blocks must verify token shape, not just braces and bytes. A
boot is the cheap confirmation - load-time parse errors need no gameplay at all.

### Finding 12: the armour tech folders clip their right edge - resolved 2026-09-09

Owner-reported 2026-09-09 after the designer fix. The mechanism is now measured:
technology folder `x` is relative to its owning gridbox origin, and the rendered right
edge is `origin + 70 * tech_x + 127`. The `70` is the gridbox slot width; `127` is the
`techtree_nsb_armor_folder_item` offset and width (`x = -55`, `width = 182`).

The two dead-space origins moved, with no technology coordinate moved:

| Gridbox | Origin before -> after | Widest x | Right edge before -> after |
| --- | ---: | ---: | ---: |
| `nsb_tank_design_tree` | 3600 -> 1650 | 20 | 5127 -> 3177 |
| `nsb_armor_tree` | 2400 -> 950 | 30 | 4627 -> 3177 |

The validator parses each child gridbox's origin and slot width, assigns each
technology through an explicit folder-x partition, and rejects any computed edge over
the **3187px** ceiling. That ceiling is empirical: `industry_folder` is the widest
folder that does not clip. It is not a documented engine limit, so the underlying
engine cause remains unisolated. The owner's scrollbar check is still the only
measurement that can identify whether the remaining issue is scroll extent or input
handling.

Static verification only. The validator mutation fixture rejects the old module
origin with the measured 5127px edge; the tech-tree render is unconfirmed in game.
Do not treat this as render or balance acceptance.

### Finding 13: light / medium / heavy hull discrimination - resolved-as-infrastructure 2026-09-09

The light family now carries the discriminator `light_armor`. Exactly five declarations
changed: `tank_chassis.txt:11` sets `light_tank_chassis` to
`type = { armor light_armor }`, and `x_tank_chassis.txt:10,20,29,37` add
`light_armor` to the four light role roots. The medium and heavy archetypes remain
`type = armor`, and all eight medium/heavy role roots remain without the token.

The validator pins the archetype domains and the light-role membership rule. The token
is behaviour-neutral for the current module set: `tank_anti_air_cannon`,
`tank_anti_air_cannon_2` and `tank_anti_air_cannon_3` still carry
`allow_equipment_type = anti_air`, which independently excludes bare gun tanks from
those modules even though their now-redundant exact-match clause no longer matches the
light domain. No module consumes `light_armor` yet.

Static verification only. The type-set mutation fixture rejects a bare light
archetype and names the expected `{armor, light_armor}` domain. The eventual paradrop
consumer and its in-game filtering remain unconfirmed.

### Finding 14: the documented module-based amphibious design is engine-impossible - CLOSED 2026-09-12

Established 2026-09-09 from vanilla evidence, and it overrides `REFERENCE.md:129-131`,
which specifies an "amphibious mobility module on eligible mechanized designs". That
cannot work, and Finding 9's module-side approach - correct for ordinary stat modules -
is the wrong tool for this family.

**Sub-units consume equipment ids, never module-bearing variants.** Vanilla
`amphibious_mech.txt:44-59` has `transport = amphibious_mechanized_equipment` and
`need = { amphibious_mechanized_equipment = 50 infantry_equipment = 100 }`; vanilla
`amphibious_armor.txt:98-100` consumes `light_tank_amphibious_chassis`. Every value is
an equipment archetype id. A search of the whole vanilla `common/units/` tree found **no
land sub-unit key that references a tank module at all** - the only
`need_equipment_modules` sites are naval (`battlecruiser.txt:8-12`,
`battleship.txt:8-12`), and `can_be_parachuted` is a sub-unit key, not an equipment key.

**Vanilla amphibious capability follows the chassis role, not the fitted module.** The
chain is `light_tank_amphibious_chassis` with `type = { armor amphibious }`
(`x_tank_chassis.txt:38-40`) consumed by the sub-unit, which carries its own amphibious
terrain modifier (`amphibious_armor.txt:66-68`). `amphibious_drive` is only a module
eligibility-and-stats definition gated by `allow_equipment_type = amphibious`; it grants
no capability by itself.

**Consequence: amphibious must be a restored designer ROLE**, not a module - which is
exactly the "rebuilding it is new work, not a restore" that `DECISIONS.md` already warned
about, now with the engine reason attached. The alternative is pointing
`mechanized_marine`'s `need`/`transport` at `mechanized_equipment`, the APC designer
archetype - but that would make **every** APC a valid marine transport regardless of any
amphibious module, a balance consequence the owner must accept or reject explicitly.

Cost of the role route, all of it now measured: a new role chassis family typed
`{ armor mechanized amphibious }`, per-hull blueprint GUI files for it, and **six**
validator contracts to change consciously - the unsupported-id set (`:421-430`), the
generic unsupported scan (`:3957-3960`), the forbidden module id `amphibious_drive`
(`:2499-2502`), the rejected `tank_chassis_*_tank_amphibious*.gui` filenames
(`:2707-2708`), the 106-blueprint count and slot contract (`:4023-4044`), and the
`mechanized_marine` `active = no` assertion (`:4061-4062`). Note the validator currently
rejects precisely the blueprint filenames a restored role would need.

Nothing was implemented. Finding 15 records the owner's deferral before the amphibious
batch starts: a real sixth designer family, rejected carrier-member renaming, or
APC-wide marine transport. OPVT and Underwater Driving Capability inherit the same
blocker.

**Closed 2026-09-12 by owner ruling, not by a fix.** The role route this finding argues
for turned out to be unavailable: all five usable designer role tokens are spent, so
amphibious can never be a designer role. The owner took the option this finding flags as
needing explicit acceptance - every APC is a marine transport - and phase 6 shipped it.


### Finding 15: the ratified amphibious route cannot work - `need` cannot name a plain member - CLOSED 2026-09-12

Established 2026-09-09 from vanilla evidence, and it invalidates the previously
ratified route rather than refining it. The owner defers the whole amphibious batch;
the three priced options remain open: a real sixth designer family, rejected carrier
member renaming, or APC-wide marine transport.

`DECISIONS.md` settled, after the `duplicate_archetypes` attempt was reverted, on
declaring the amphibious carrier hulls **explicitly** - "sixteen equipment blocks in the
style of the existing `apc_chassis_0..7` and `ifv_chassis_0..7` members" with
`archetype = mechanized_equipment` and `type = { armor mechanized amphibious }`. That
fixes the id-concatenation defect. It does **not** deliver the selectivity the same
document promises when it says `mechanized_marine`'s `need`/`transport` should "point at
those role chassis".

**Measured rule: a land sub-unit's `need` and `transport` resolve an equipment
*family*, never an individual member.** Every value used in those fields across the
whole vanilla `common/units/` tree is either an archetype declared `is_archetype = yes`
or a `duplicate_archetypes` role root. There is **no** vanilla case of a sub-unit naming
a plain numbered member such as `mechanized_equipment_1`. Vanilla's own amphibious units
prove the intended shape: `amphibious_mech.txt:103-107` consumes
`amphibious_mechanized_equipment`, which is declared `is_archetype = yes` at
`equipment/amphibious_mechanized.txt:8` with its own members `_1.._5`; and
`amphibious_armor.txt:25` consumes `amphibious_tank_chassis`, itself
`is_archetype = yes`. Paradox's own equipment documentation states the same rule from
the other side - a need for an archetype is satisfied by any mix of that archetype's
variants, and different archetypes are never interchangeable.

Consequence, stated plainly: `apc_amphibious_chassis_N` declared as a member of
`mechanized_equipment` **cannot be named in `need`**. The only thing a sub-unit could
name is `mechanized_equipment` itself, which is the "APC-wide marine transport (cheap
but unselective)" option Finding 14 lists - every ordinary APC would become a marine
transport. The `type = { ... amphibious }` token still works for
`allow_equipment_type` module gating, so the *module* half of the plan survives; the
*supply* half does not, and the owner's Next-scope condition is "amphibious only
together with marine sub-unit supply".

**What is left, with the cost now honest:**

1. **A real sixth designer family** - amphibious carrier hulls under their own
   `is_archetype = yes` root, which is exactly vanilla's shape. This is the only route
   that is both selective and proven. Cost is a full family: archetype block with the
   21-slot layout, its own hull tiers, pictures, blueprint GUI, technology unlocks,
   presets, and the six validator contracts Finding 14 already enumerates - not the
   "nearly free" role `DECISIONS.md` assumed.
2. **Rename the carrier members** so `duplicate_archetypes` derivation works. Already
   rejected: the ids appear across 586 national presets, the generic bookmark variants
   and the OOB migration.
3. **Accept APC-wide marine transport.** Cheap, unselective, needs an explicit owner
   ruling.

**Owner decision: deferred.** Nothing was implemented and no amphibious content was
authored. The batch stays blocked on the three priced options above, rather than on an
assumption that would fail after the work was done.

**Closed 2026-09-12.** Option 2 was already rejected and option 1 is unbuildable as a
*role* - the token set is spent - so the owner chose option 3, APC-wide marine transport,
which the restructure made cheap: `light_tank_apc_chassis` is a `duplicate_archetypes`
root, and this finding's own measured rule says a root is exactly what `need` can name.
Option 1 survives only as a sixth standalone family, priced and declined. See phase 6.


### AA ammunition - IMPLEMENTED 2026-09-09

The owner's reversal of the self-supplying-AA-gun rule is shipped. Self-test delta:
`286 tank modules` -> **`289 tank modules`**, everything else unchanged.

Three modules `tank_aa_ammo_1..3`, one per existing AA cannon tier rather than a
six-tier ladder that would outrun the three guns able to use it. They sit in the
**existing** `tank_ammo_he` category - so no new category, no archetype edits, no new
count limit - and therefore mount in the dedicated HE slot `tank_special_slot_2`, which
is consistent with the slot contract. Each carries
`allow_equipment_type = anti_air`, so an AA shell cannot be fitted to a gun tank, and
each declares **no** `soft_attack`, `hard_attack` or `ap_attack`, so SPAA does not become
an anti-tank platform. Air attack is roughly 22% of the paired cannon: 4 / 7 / 10 against
18 / 32 / 46. All values authored. Unlocked from the existing
`nsb_aiming_devices0/2/4`, which already own the AA cannon tiers, so no new technology
and no `cwic_major_tank_research_1980` change was needed.

The three `Standard Light SPAA` starting variants (1942/1944/1950) now mount
`tank_aa_ammo_1`; every other field is byte-identical. The cannons' pinned air-attack
values 18/32/46 were not touched.

**The validator rule was inverted rather than deleted.** `needs_ammunition` now returns
true for AA armament, with a new `ammunition_requirement_error` distinguishing the AA
case, and the comment cites the 2026-09-09 decision instead of the retired rationale.
**Flame remains exempt** - verified in the final source. A negative fixture proves an AA
design without AA ammunition is now rejected.

Consequence to carry forward: known inconsistency 10's claim that "the three SPAA
variants deliberately carry no ammunition" is now **false and superseded**.

### Artillery/AA restructure - deferred by owner decision

The owner defers the artillery/AA batch entirely, including any provenance widening.
Preserved facts: the provenance filter is the literal path set
`{TECH_DIR / "NSB_armor.txt", TECH_DIR / "NSB_armor_modules.txt"}`, repeated at
`validate_military_reworks.py:1969` and `:3937`; `artillery.txt` is already parsed
into `technology_blocks` and excluded only by those two filters. No artillery family
currently carries `enable_equipment_modules`, and no artillery-ammunition category
exists. `Artillery_AA_Target_Manifest.md:117-119` requires fresh 1949/1980 NSB and
non-NSB runtime QA before implementation.

Static verification only. No artillery or AA restructure is authored in this batch.

## Module content plan, 2026-09-09

Written at the owner's request, from a four-lane evidence pass. **Nothing in this
section is implemented.**

### First, a correction: the special modules are not missing

The premise "AFAIK, all special modules are missing" is not what the source says.
`00_tank_modules.txt` holds **270 module definitions, 145 of them in the 18 special
categories** - verified by per-module category parse, not by counting `category` lines:

| Category | Modules | Category | Modules |
| --- | ---: | --- | ---: |
| `tank_ammo_kinetic` | 13 | `tank_loader_artillery` | 3 |
| `tank_ammo_chemical` | 14 | `tank_protection_passive` | 7 |
| `tank_ammo_missile` | 9 | `tank_protection_reactive` | 5 |
| `tank_ammo_he` | 5 | `tank_protection_active` | 6 |
| `tank_fcs_aiming` | 11 | `tank_survivability` | 3 |
| `tank_fcs_optics` | 16 | `tank_mobility_auxiliary` | 11 |
| `tank_fcs_computer` | 14 | `tank_smoke` | 6 |
| `tank_fcs_radar` | 7 | `tank_secondary_turret` | 4 |
| `tank_loader_manual_assist` | 2 | `tank_loader_autoloader` | 9 |

What is missing is narrower and it is worth stating precisely, because it decides how
much work this is: **one whole family (Special Capabilities, 11 boxes), the night-vision
ladder (6 technologies), and four previously recorded orphans** (Blow-Out Panels,
External Additional Fuel Tanks, Unmanned Turret / RWS, Modular Construction). Thermal
vision is *not* missing and suspension is *not* missing - see below. That is roughly
15-20 new modules against 145 existing, not a from-scratch build.

### On the proposed order: technologies first, then map to the designer

Agreed with one correction. Authoring the technologies and modules first is right,
because a module cannot be reached without an unlock and the tree geometry is the
scarce resource. But "then map it to the designer" is mostly already done: the 21-slot
contract exists, the free-slot list exists, and per Finding 9 the per-hull lock is a
module-side attribute rather than a designer change. The real sequencing constraint is
the opposite of what it looks like - **every new module must land in the free-slot
category list and the count limits in the same edit as its technology**, or it silently
stacks. There is no separate "map to designer" phase to defer to.

### Lane 1: night vision - IMPLEMENTED 2026-09-09

Shipped in this pass. Six technologies `nsb_night_vision0..5` in a new x=18 column of
`nsb_armor_modules_folder` at @1944 / @1960 / @1975 / @1990 / @2000 / @2020 - every
anchor already existed, none was added - chained
`nsb_optics0 -> nsb_night_vision0 -> .. -> nsb_night_vision5`, with `nsb_optics7` as the
second required input to Fusion so the thermal branch converges into it as the mockup
shows. Six modules `Night_Vision_0..5`, abbreviations `nvis0..5`, all in the existing
`tank_fcs_optics` category - so **no archetype, free-list or count-limit edit was
needed**, which is why that category was chosen. Localisation for all twelve keys from
the owner's descriptions 37-41 and 45, ASCII-only.

All stats are **authored/invented** - the workbook sheet is empty. They are monotonic
across the six tiers and bounded by `Optics_7`: the top tier matches `Optics_7` on fuel,
build IC, reliability, breakthrough, defence, dismantle and XP while staying below it on
hard/soft attack (0.15 against 0.25), so night vision reads as capability rather than a
raw attack upgrade.

**The tree was clipped and is now widened.** `nsb_tank_design_tree` hosts the FCS graph
and its gridbox width was the limiting value, at 2200 with 70px per x unit
(`countrytechtreeview.gui:4535-4541`). One number changed, 2200 -> 2500, which buys the
280px needed to reach x=20 plus 20px headroom. No tree origin, folder size, scrollbar or
year label moved. **This is a measured change, not a verified render** - the owner should
confirm the night-vision column is visible and scrollable in the module tree.

**One contract catch, worth recording because only the validator found it.** The six new
technologies broke `cwic_major_tank_research_1980`, which must grant every tank
technology with `start_year <= 1980`: the validator failed with
`1980 tank research coverage differs: ['nsb_night_vision0', 'nsb_night_vision1',
'nsb_night_vision2']`. Fixed by adding those three to
`CWIC_tank_bookmark_research.txt`. **Any future technology added to an NSB armour file
must be added there too if its `start_year` is 1980 or earlier.**

Self-test after: `1309 technologies, 275 tank modules ... 21 designer slots checked` -
plus six technologies and six modules, every other count unchanged.

### Lane 1 background: why night vision was absent and thermal was not

Before this pass no **night**-vision technology or module existed anywhere;
`night_vision` survived only as an orphan tag at
`common/technology_tags/00_technology.txt:42`, referenced by no technology, module,
localisation key or icon. Thermal vision was a different story - see below.

The existing FCS ladder in `NSB_armor_modules.txt` occupies columns x10 (aiming,
`nsb_aiming_devices0..5`), x12 (optics, `nsb_optics0..7`), x14 (ballistic computer,
`nsb_ballistic_calculator0..6`) and x16 (panoramic sight, `nsb_pano_sight0..2`), with
`nsb_awareness_system` converging at x8/@2020. **x18 is free**, which is exactly where
the owner's mockup puts the night-vision column - immediately right of the panoramic
sights. No existing technology has to move.

**The thermal half is already built, and that halves this lane.** `Optics_4..7` are
localised **"Thermal Sight I", "Thermal Sight II", "Thermal Sight III"** and
**"Advanced Thermal Sight"** (`tank_modules_l_english.yml:951-957`), category
`tank_fcs_optics`, unlocked by `nsb_optics4..7` at 1970 / 1980 / 1990 / 2005
(`NSB_armor_modules.txt:2895, 2922, 2949, 2976`). So the mockup's three-step thermal
branch is already four steps in script - it just lives in the optics column rather than
a column of its own, and its stat operations are ordinary optics operations rather than
anything thermal-specific.

That leaves a genuine decision, not an authoring task: either accept the existing
`Optics_4..7` as the thermal branch and only add night vision beside it, or split
thermal out into the new column to match the mockup - which means retargeting four
shipped modules and their four unlock technologies, and the shipped presets that
reference them. **The cheap and boring option is to keep `Optics_4..7` where they are**
and treat the mockup's thermal boxes as already satisfied, with a note that the mockup's
years (1975/1990/2000) disagree with the shipped 1970/1980/1990/2005.

Owner ladder and row status, with `@year` anchors resolved:

| Technology | Year | Status |
| --- | --- | --- |
| Zero Gen Night Vision | 1944 | new; row exists (`nsb_aiming_devices1`, `nsb_optics1`) |
| First Gen Night Vision | 1960 | new; **new row** |
| Second Gen Night Vision | 1975 | new; row exists (`nsb_ballistic_calculator2`) |
| Third Gen Night Vision | 1990 | new; row exists (`nsb_optics6`) |
| Third+ Gen Night Vision | 2000 | new; **new row** |
| First Gen Thermal Vision | 1975 | satisfied by `Optics_4` (shipped 1970) |
| Second Gen Thermal Vision | 1990 | satisfied by `Optics_5`/`Optics_6` (1980/1990) |
| Third Gen Thermal Vision | 2000 | satisfied by `Optics_7` (2005) |
| Fusion Night Vision | 2020 | new; row exists (`nsb_awareness_system`) |

So six new technologies, not nine, and two new tree rows. The owner supplied
description text for all nine boxes, numbered 37-45, which removes the localisation
blocker; entries 42-45 describe the thermal and fusion steps and can be attached to the
existing `Optics_4..7` if the cheap option is taken.

**Category decision for night vision.** If night vision goes in `tank_fcs_optics` it
competes with the day sights and the thermal tiers for the one dedicated optics slot,
which is probably right historically and costs nothing. If it gets its own category it
becomes a free-slot module that stacks with a sight, and that category must be added to
the free list and the count limits in the same edit.

**All numbers are invented.** The frozen workbook's `Night & Thermal Vision Effects`
sheet has dimension ref `A1` and **zero value cells** - confirmed by reading the sheet
XML out of the xlsx, without writing to it. The "recorded as authored" rule applies to
every stat in this lane.

### Lane 2: suspension - already implemented, do not rebuild it

This answers the owner's "needs further review if it should be implemented/already is"
directly: **it is implemented.** Fifteen suspension modules exist across all six
categories, with a full unlock chain:

| Mockup box | Status | Existing id |
| --- | --- | --- |
| Torsion Bar Suspension 1939 | exists | `Torsion_0`, granted by `nsb_iw_armored_vehicles` |
| Torsion Bar With Shock Absorbers 1944 | exists, year/name differ | `Torsion_1`, granted by `nsb_suspension0` (1940), localised "Modernized Torsion Bar Suspension" |
| Tracked Hydro-Pneumatic 1960 | exists, year agrees | `Hydro_pneumatic_1`, `nsb_suspension2` @1960 |
| Tracked Active Hydro-Pneumatic 1985 | exists, year agrees | `Hydro_pneumatic_2`, `nsb_suspension3` @1985 |
| Experimental 4-Track Suspension | **absent** | no module, technology or localisation key |

So the only genuinely new suspension item is Experimental 4-Track, whose mockup
annotation "Opened by 1955 H Tank" implies a prerequisite on a heavy hull rather than a
free-standing tech. Everything else is a naming and year reconciliation question, not
implementation. The mockup's "Modernised External Spring Suspension" annotation is
ambiguous: `Independent_external_1` exists and is localised "Modernized External
Independent Suspension", so decide whether that annotation labels `Torsion_1` or points
at the external-independent family before renaming anything.

There is **no transmission module family at all** - no `transmission` match anywhere in
the module file - so the mockup's "Transmission" heading currently describes nothing in
script. Decide whether it is a real surface or just a heading.

The engine column is likewise implemented (`Petrol_0..3`, `Diesel_0..6`, `GT_0..3`,
`APU_0..6`, `GT_APU_0..3`) but carries a systematic year disagreement worth one
decision rather than eleven: **the icon assets encode one year and the unlocking
technology another**, consistently for the gas turbines (icons 1960/1970/1980/2000 vs
techs 1965/1975/1985/2005) and the GT APUs (icons 1960/1970/1980/2000 vs techs
1965/1975/1985/2005). The mockup agrees with the icons. Pick one authority and record
it; do not fix these one at a time.

The mockup annotation "Early Auxiliary Power Unit - needed for SPAA with radar" is
**aspirational, not implemented**: no `allow`, prerequisite or trigger anywhere ties any
`APU_*` or `GT_APU_*` to `Radar_*` or to an AA chassis. If that coupling is wanted it is
new work, and Finding 9's `allow_equipment_type` is the mechanism for the AA half of it.

### Lane 3: Special Capabilities - absent, and two boxes have no engine mechanism

Every box is absent from the mod: no module, no technology, no icon, for Amphibious
Drive, OPVT, Underwater Driving Capability, Dozer Plow, Log, Anti-Mine Plow (1955 and
1970), Paradrop Capability, Anti-Mine Roller (KMT-5), Integrated Trench-Digging Plow,
or Anti-Mine Roller With Electro-Magnetic Coils (KMT-7 EMT).

Most of them are ordinary stat modules and have a home category already:

| Box | Available existing category |
| --- | --- |
| Log, Blow-Out Panels | `tank_survivability` (Blow-Out Panels also fits `tank_protection_passive`) |
| Dozer Plow, both Anti-Mine Plows, both Anti-Mine Rollers, Integrated Trench-Digging Plow, External Additional Fuel Tanks | `tank_mobility_auxiliary` |
| Unmanned Turret / RWS | `tank_secondary_turret` |
| Modular Construction | none clearly semantic |

**Two boxes are not stat modules and need a decision before they are designed.**

- *Amphibious Drive and Underwater Driving / OPVT.* Vanilla's mechanism is
  `allow_equipment_type = amphibious`, but this mod **deleted** the designer amphibious
  role (`DECISIONS.md`), so there is no `amphibious` type to allow. The legacy
  `amphibious1..5` technologies (`armor.txt:1765-1918`) only
  `enable_equipments = mechanized_marine_equipment_1..5`; they grant no module and no
  capability key. And `mechanized_marine` is still `active = no`
  (`CWIC-Special-Units.txt:62-70`) with the validator asserting it stays that way.
  Making an amphibious module actually supply marine sub-units therefore means
  rebuilding the role, flipping that sub-unit, and consciously changing that validator
  assertion - which is exactly the pre-condition `DECISIONS.md` already set for this
  family. This is the largest item in the whole plan and it is not a module.
- *Paradrop Capability.* There is **no engine field for it in the module system.** A
  search of the vanilla module directory finds no `can_be_parachuted`, `parachut*`,
  `special_forces` or `marines` key on any module - the only capability-bearing vanilla
  module is `amphibious_drive`, and it works through equipment types, not a paradrop
  flag. So a paradrop *module* cannot grant paradrop capability. It has to be a sub-unit
  or technology property, or the box has to be dropped. Do not author it as a module and
  discover this afterwards.

Authoring conventions for the rest, from three cited families: costs go inside
`add_stats` with a module-level `dismantle_cost_ic`, and `xp_cost = 1` universally -
`Addon_0_Comb` 1.5/0.1/1, `ERA_0` 1/0.05/1, `Smoke_0` 0.5/0.05/1. Each module also needs
a `GFX_SMI_<id>` sprite in `interface/cwic_tank_rework_icons.gfx` whose texture exists
on disk, or the engine logs a miss every load.

### Lane 4: armoured artillery and SPAA - the limbo is real and now measured

The owner's read is correct, and it is duplication of identity, not just of listing.

*The designer path.* Six role roots in `x_tank_chassis.txt` - light/medium/heavy
artillery and anti-air, e.g. `light_tank_aa_chassis` `type = { armor anti_air }` at
`:8-15` and `light_tank_artillery_chassis` `type = { armor artillery }` at `:18-25`.
`NSB_armor.txt` grants light and medium tiers 0-9 and heavy tiers 0-4 for both roles.

*The legacy path, still fully live.* `artillery.txt` is **85 technologies in 17
five-tier families**, confirming known inconsistency 8's count. It sits in an
**unconditional** `artillery_folder` - no `has_dlc`, no `allow`, no trigger anywhere in
the file - and it enables its own sub-units and its own equipment archetypes:
`sp_artillery_1` enables `sp_artillery` + `sp_artillery_equipment_1` (`:1271-1277`),
`light_sp_artillery_1` (`:1619-1625`), `heavy_sp_artillery_1` (`:1978-1984`), and
`spaag_1` enables `spaag` + `spaag_equipment_1` (`:252-259`). The consumers are real
sub-units in `CWIC-Artillery.txt` and `CWIC-Anti-Air.txt`, and the legacy archetypes
carry five tiers each at 1940/1955/1970/1985/2000 (`sp_art.txt:54-160`,
`sp_aa.txt:50-155`).

*What the tree grants the designer today: nothing.* The only
`enable_equipment_modules` in all of `artillery.txt` are `ship_AA_gun_1..5`. Eighty-five
technologies, zero tank designer modules.

**The gating decision already exists** - `DECISIONS.md` ratified that artillery and AA
gate legacy and designer paths by DLC, preserving technology-based sub-unit activation,
reusing the `OR = { has_tech = legacy has_tech = nsb_* }` shape. That shape is live in
`support.txt` at seven sites (`:82-86, 130-134, 184-188, 238-242, 290-294, 378-382,
430-434`). So the remaining work is implementation plus the mockup's restructure, not a
new decision about approach.

**Where the mockup and the existing module set disagree - resolve before authoring.**
The mockup wants each artillery/AA technology to unlock *gun modules only*, on six-tier
ladders. The modules it would unlock are only partly there:

| Mockup column | Existing designer modules | Gap |
| --- | --- | --- |
| Light/Medium/Heavy Artillery I-VI | `tank_low_p_cannon0..3`, category `tank_low_pressure_main_armament`, already `allow_equipment_type = artillery` | 4 tiers exist against 18 mockup boxes; there is no separate light/medium/heavy artillery gun family |
| AA Autocannon I-VI | `tank_anti_air_cannon`, `_2`, `_3` | 3 tiers against 6 |
| Artillery Ammunition I-VI | none - no artillery ammunition category exists | 6 new, and needs a category decision |
| AA Ammunition I-VI | none | **conflicts with a ratified decision** |
| Artillery / AA Modernisation I-VI | no module family; these are modifier technologies | decide whether they grant modules at all |

The AA ammunition column is the one to settle first, because it contradicts something
already ratified: AA guns deliberately supply their own attack, the three SPAA bookmark
variants deliberately carry no ammunition (known inconsistency 10), and the validator
pins that exemption. An AA ammunition ladder either overturns that or has to be modelled
as technology bonuses rather than modules.

Also note the frozen `Artillery_AA_Target_Manifest.md` already fixes 31 vehicle target
rows over SPAAG, SAM, SP Light/Medium/Heavy and AT, with six module budget rows, and
explicitly defines no towed-artillery or ammunition loadout. Any restructure has to land
inside that frozen contract or renegotiate it explicitly.

The validator would have to renegotiate its role-chassis grant formula
(`validate_tank_rework` expected grants), the `SUPPORTED_ROLES` constant, the exact AA
air-attack values 18/32/46, the `needs_ammunition` AA exemption, and the generated-enum
checks for artillery chassis.

### Amphibious: the documented specification and the five blockers

Researched 2026-09-09 under the owner's ruling that the design documents are the
authority.

**What the documents actually specify.** `REFERENCE.md:129-131` maps
`mechanized_marine_equipment` onto the same archetype with an **amphibious mobility
module**, marked NOT STARTED - so the documented design is a module on eligible
mechanized designs, not a restored tank role. `BALANCE.md:312-330` (drawio page 2) puts
`Amphibious Drive` at 1940 in the Special Capabilities column and records that it
**retires the legacy line**. Two things the documents do *not* provide: the xlsx `Roles`
tab contains no amphibious or marine row at all, and `Balance_Target_Manifest.md` rows
24-41 cover only WWII/Light/Heavy Mech - `BALANCE.md:259-261` states outright that no
source target defines amphibious equipment. Drawio page 7 "Trucks & Amphibious" is a
bare grid. **So every amphibious stat is authored, with no frozen envelope to match.**

**Current state.** The legacy half exists and works: `armor.txt:1765-1932` defines
`amphibious1..5` at 1944/1950/1965/1985/2005, each only
`enable_equipments = mechanized_marine_equipment_N`, and `mechanized_marine.txt:8-165`
defines the archetype plus five tiers. The consuming sub-unit is parked -
`CWIC-Special-Units.txt:62-108` has `special_forces = yes`, `marines = yes`,
`active = no`, `type = { mechanized }`, needing 50 `mechanized_marine_equipment` and 150
`infantry_equipment`. The designer half is gone: no `amphibious` type, no role chassis,
no module. Only cosmetics survive - MIO sprites at
`industrial_organization_department_icons.gfx:180,212,244`, a texticon at
`texticons.gfx:4597`, and vanilla-inherited loc keys at
`tank_modules_l_english.yml:241-242,280-284,303-307,336-340`.

**The hull-lock token is settled by measurement.** All three gun-tank archetypes are
bare `type = armor` (`tank_chassis.txt:2-15, 415-428, 825-838`); APC and IFV are
`type = { armor mechanized }` (`mechanized.txt:7-20`, `mechanized_heavy.txt:7-16`) and
every one of their sixteen hulls repeats it. The twelve designer role roots in
`x_tank_chassis.txt` add `anti_air` / `artillery` / `anti_tank` / `flame`. So
**`mechanized` is the discriminator** that locks amphibious to the carriers, and
`forbid_equipment_type_exact_match = armor` is the shape that excludes bare gun tanks -
exactly what vanilla's `amphibious_drive` does. Vanilla's own role root for comparison:
`x_tank_chassis.txt:39-45` is `light_tank_amphibious_chassis` with
`type = { armor amphibious }`.

**Five blockers, all of which must be crossed consciously.** The validator does not
merely lack support for this - it actively forbids it, in four places:

| # | Blocker | Site |
| --- | --- | --- |
| 1 | `amphibious_drive` is on the forbidden-module-id list | `validate_military_reworks.py:2499-2502` |
| 2 | `amphibious_tank_chassis`, `amphibious_mechanized_infantry`, `category_amphibious_tanks` are forbidden orphan ids | `:425-430` |
| 3 | any `tank_chassis_*_tank_amphibious*.gui` blueprint is rejected | `:2703-2705` |
| 4 | `mechanized_marine` must stay `active = no` | `:4039-4040`, exact assertion |
| 5 | `mechanized_marine_equipment_1..5` sit in `UNMIGRATED_LEGACY_ARMOUR` and are one of the eight ratified focus-grant exceptions | `:350-355`, `DECISIONS.md` |

Recommended shape, consistent with both the documents and Finding 9: author an
amphibious **mobility module** in `tank_mobility_auxiliary`, bounded by
`allow_equipment_type = mechanized` plus
`forbid_equipment_type_exact_match = armor`, rather than restoring a vanilla-style
amphibious role. That keeps the 21-slot contract and the free lists untouched. The hard
part is unchanged and is not a module problem: making an amphibious carrier design
actually supply the `mechanized_marine` sub-unit means flipping blocker 4 and rewriting
that assertion, and `DECISIONS.md` forbids retiring `amphibious1..5` until that supply
demonstrably works.

### Artillery and SPAA: restructure plan inputs

Researched 2026-09-09. Four things are now measured that the plan needs.

**1. The gate shape is `allow`, so gated legacy technologies stay visible.** All seven
`support.txt` sites (`:82-87, 130-135, 184-189, 238-243, 290-295, 378-383, 430-435`) put
`OR = { has_tech = legacy has_tech = nsb_* }` inside a per-technology `allow` block, not
`allow_branch` and not the folder block. A failing gate therefore leaves the technology
in the tree but unresearchable. That is the desired behaviour here and it is why folder
removal was rejected for mechanized.

**2. Gating is the right call, and the margin is now five times larger than the
precedent.** Legacy artillery/AA technologies are granted at **5653 `set_technology`
sites across 460 country-history files**. The mechanized precedent that made
`DECISIONS.md` choose DLC-gating over folder removal was 1144 sites. Removing these
families from the folder is not on the table.

**3. The AA ammunition reversal has three concrete consequences.** The validator's
`needs_ammunition` exemption at `:3619-3624` explicitly encodes "AA and flame supply
their own attack, no shell", and it is invoked on starting variants at `:3890-3893`. The
three affected designs are `Standard Light SPAA` 1942/1944/1950 at
`CWIC_tank_designer_effects.txt:159-173, 181-195, 203-217`, each mounting
`tank_anti_air_cannon` with no ammunition slot filled. And the only ammunition
categories that exist are `tank_ammo_kinetic` and `tank_ammo_he`, so an AA shell either
joins one of those - free - or gets a new category, which costs an edit to all five
archetypes' free lists **and** the count limits in the same edit. Prefer joining an
existing category unless the design genuinely needs AA-only exclusivity.

**4. The mockup's premise collides with the module-provenance contract.** The validator
only scans `NSB_armor.txt` and `NSB_armor_modules.txt` for module unlocks
(`:1795-1806`, `:3648-3655`). The mockup wants artillery technologies to unlock designer
gun modules, which would put unlocks in `artillery.txt` - outside that contract. Either
the new gun-module unlocks live in the NSB files while the artillery tree only gates
them, or the provenance contract is widened deliberately. **Decide this before authoring
a single technology.**

Existing module coverage against the mockup's six-tier ladders, all unlocks cited:

| Family | Have | Want | Unlocks |
| --- | ---: | ---: | --- |
| Low-pressure artillery guns `tank_low_p_cannon0..3` | 4 | 18 (light+medium+heavy) | `nsb_low_pressure_guns0..3` at `NSB_armor_modules.txt:385, 411, 445, 479` |
| AA cannon `tank_anti_air_cannon`/`_2`/`_3` | 3 | 6 | base at `NSB_armor.txt:59-69`, then `nsb_aiming_devices2/4` |
| AA aiming `Aim_AA_0..4` | 5 | - | base plus `nsb_aiming_devices2..5` |
| AA optics `AA_Optics_0..5` | 6 | - | base plus `nsb_optics4..7` |
| Artillery optics `Arty_Optics_0..1` | 2 | 6 | base plus `nsb_ballistic_calculator5` |
| Artillery computer `Computer_arty_0..3` | 4 | 6 | `nsb_ballistic_calculator3..6` |
| Artillery loader `Loader_5a/5b/5c` | 3 | 6 | `nsb_conveyer_autoloader0..2` |
| Artillery ammunition | 0 | 6 | none - new |
| AA ammunition | 0 | 6 | none - new, and see consequence 3 |

**Tree geometry: there is room, but the existing lattice already collides.** The 85
technologies occupy only **55 unique cells** in a lattice of x = -7,-4,-3,0,3,4,7 by
y = 0..28 even. At x=0 seven families overlap the same cells - `(0,0)` holds
`autocannon`, `artillery` and `direct_fire_gun`; `(0,2)` holds `spaag`, `sp_rocket` and
`tank_destroyer` - and `x=-3` doubles `cannon_ammo` with `at_ammo` while `x=3` doubles
`aa_upgrade` with `at_upgrade`. Roughly 50 cells are free. Per `README.md`'s guardrail,
do not resolve a collision by moving a technology to an arbitrary free cell; keep each
family in one column and move the minimum. Note the `artillery_folder` GUI declares only
one explicit gridbox (`countrytechtreeview.gui:5222-5229`, anti-air grid at
`:5252-5257`), so a widened tree may need the same clipping fix Lane 1 needed.

**Frozen-manifest boundary.** `Artillery_AA_Target_Manifest.md` freezes 31 vehicle rows
(SPAAG 5, SAM 6, SP Light/Medium/Heavy 5 each, AT 5) and six module budget rows, and
**explicitly leaves towed artillery, rocket artillery, amphibious, night vision and any
complete designer loadout undefined**. Omitted stats are unspecified, not zero. A
restructure lands inside that boundary or renegotiates it in writing.

**Migration checklist** - the DLC gate must cover all 17 five-tier families
(`artillery`, `light_artillery`, `heavy_artillery`, `art_ammo`, `art_upgrade`,
`sp_artillery`, `light_sp_artillery`, `heavy_sp_artillery`, `sp_rocket`, `autocannon`,
`spaag`, `aa_upgrade`, `cannon_ammo`, `direct_fire_gun`, `at_ammo`, `at_upgrade`,
`tank_destroyer`), their sub-units including the `_support` variants, and their eleven
five-tier equipment ladders.

### Order and status

1. ~~Four blocking decisions~~ - **answered by the owner 2026-09-09**, recorded in
   `DECISIONS.md` under "Owner decisions".
2. ~~Night vision~~ - **implemented 2026-09-09**, see Lane 1. Owner still owes a visual
   confirmation that the new x=18 column is visible after the tree widening.
3. ~~Special Capabilities minus amphibious and paradrop~~ - **implemented 2026-09-09**,
   see "Special Capabilities and 4-Track" below.
4. ~~Experimental 4-Track and the icon-year authority migration~~ - **implemented
   2026-09-09**, same section.
5. **Amphibious**, own batch - **blocked on an owner choice between three priced
   options, not on authoring.** Finding 15 withdrew the ratified route: a sub-unit
   `need`/`transport` cannot name a plain member, so explicitly declared carrier hulls
   can never supply marines selectively. Pick a real sixth archetype family, rename the
   carrier members (rejected), or accept APC-wide marine transport, then author.
6. **Artillery/AA restructure**, last and largest, against the frozen manifest, and
   gated on the module-provenance decision in that plan.

Items 3-4 were run as two concurrent agents split by **file ownership** rather than by
lane - one owning the module/archetype/icon files, the other the technology/effect files
- with the module-id-to-unlock map fixed in the batch contract so the halves met. Both
lanes editing `00_tank_modules.txt` is what makes a lane-shaped split impossible.

### Special Capabilities and 4-Track - IMPLEMENTED 2026-09-09

Self-test delta: `1309 technologies, 275 tank modules` -> **`1317 technologies, 286 tank
modules`**; every other count unchanged, still `21 designer slots checked`.

**Ten Special Capabilities modules, all into existing categories** - deliberately, since
an existing category needs no free-slot or count-limit edit. `tank_mobility_auxiliary`
11 -> 18 (`Dozer_0`, `Fuel_Tanks_0`, `Mine_Plow_0`, `Mine_Roller_0`, `Mine_Plow_1`,
`Trench_Plow_0`, `Mine_Roller_1`), `tank_survivability` 3 -> 5 (`Log_0`,
`Blowout_Panels_0`), `tank_secondary_turret` 4 -> 5 (`RWS_0`). Seven technologies
`nsb_special_capabilities0..6` at 1945/1950/1955/1965/1970/1980/1990 in a new x=20
column, chained off `nsb_tank_design`. A `@1945` anchor had to be added, resolving to 3
between `@1944 = 2` and `@1950 = 4`; no duplicate row value resulted.

All stats are **authored/invented** except `Log_0`, whose +2% reliability is the one
documented value in the drawio. Each module was priced against a named neighbour in its
own family. No new abbreviation collision was introduced.

**`Four_Track_0` needed a new category, and it is a mandatory-slot category rather than
a free-slot one.** `tank_suspension_multi_track` is now listed on `suspension_type_slot`
in all five archetypes (3 in `tank_chassis.txt`, 1 each in `mechanized.txt` and
`mechanized_heavy.txt`) and correctly has **no** `module_count_limit` - a mandatory slot
holds exactly one module, so the count-limit rule that governs free-slot categories does
not apply. Verified: the limit blocks stayed at 54 / 18 / 18. Its unlock
`nsb_suspension_multi_track` is gated on `nsb_heavy_tanks3`, the heavy ladder's 1955
technology, implementing the mockup's "Opened by 1955 H Tank" annotation as a
prerequisite rather than a free-standing tech.

**Icon-year authority applied to the gas turbines.** `nsb_gt_engines0..3` moved from
1965/1975/1985/2005 to **1960/1970/1980/2000**, with their tree rows moved to match and
no coordinate collision. This is the ratified rule that the icon asset year wins.

**The validator had to move with it, exactly as the guardrail predicts.** It hardcoded
those four years at `validate_military_reworks.py:2660-2665` and failed with
`nsb_gt_engines0..3 has the wrong start year or tree row`. Updated to the icon years
with the rationale in a comment. `README.md`'s warning that any balance change needs a
matching validator edit held true.

**Second hit of the 1980-coverage rule.** As in Lane 1, new technologies dated <= 1980
had to be added to `cwic_major_tank_research_1980`: `nsb_special_capabilities0..5`,
`nsb_suspension_multi_track`, and the gas-turbine technologies the migration newly
brought to 1980 or earlier. `nsb_special_capabilities6` (1990) is correctly excluded.
This rule has now bitten twice in one session - treat it as part of the definition of
adding an NSB armour technology.

**Deferred with reasons, not forgotten.** `OPVT` and `Underwater Driving Capability`
were pulled out of this batch: they are amphibious-adjacent and share the amphibious
missing-mechanism problem, so they belong to that batch rather than being approximated
with unrelated stats. `Modular Construction` remains deferred for want of a semantically
available category. Neither is implemented, and no stat was invented for them.

Static verification only. No live check of the new column, the new suspension option, or
any of the eleven modules in the designer.


## Owner QA notes, 2026-09-06 playtest

Both NSB and non-NSB loaded clean at 1949 and 1980. Verbatim notes are in
`TankQANotes.txt`; screenshots in `Screenshots_9-6-26/`.

**Items 2, 3, 4, 6 and 7 were human-verified in game and closed by the owner on
2026-09-08**, confirming the static dispositions below. Still open:

1. On non-NSB, FIN's focus "Acquire Soviet T-55's" needs a check that SOV has
   researched T-55 technology, or it grants nothing.
2. Tank research is not date-gated in either profile. A 1980 start still shows USA with
   1955+ tech locked.
3. NSB only: Light Turret Module has the same stats as Conventional Turret. (A revised
   conventional turret was authored - see `DECISIONS.md` - so confirm whether this
   observation predates that change.)
4. NSB only: Early MBT Heavy Gun, HEAT-MP Ammunition (1985) and HEAT-DU Ammunition
   (1985) are researchable in 1980 with no ahead-of-time penalty. May apply to other
   tank tech at other dates.
5. NSB only: ATGM modules have very high piercing. Gun-Launched ATGM III is 600
   piercing / 95 hard attack / 5.5 soft attack. This matches both script and workbook -
   see `DECISIONS.md` - so the question is whether the source itself is right.
6. NSB only: Vehicle Radar System stats look odd - supply use renders as `-0`,
   air attack +25%, reliability -5%, fuel usage 1.20. These match the workbook; the
   `-0` is a display rounding artifact, not a zero in the module definition.
7. NSB only: `CWIC_tank_focus_effects.txt` effects are verbose and fill the Armor
   Production tab with preset tanks for USA/SOV. Does not match non-NSB.
8. NSB only: preset tanks are not made for NSB - no T-54/T-55 for SOV, just a generic
   hull. (Superseded for carriers by the Step 2 commit; still true for other families.)

## Static QA disposition, 2026-09-08

Static review of owner QA items 2, 3, 4, 6 and 7 found no remaining source discrepancy:

- **QA 2:** `cwic_major_tank_research_1980` is called from the dated 1980 USA and
  SOV history blocks. Its NSB branch grants every tank technology with
  `start_year <= 1980`, and its legacy branch grants the corresponding legacy
  ladder. The validator checks both exact grant sets and the one-call-per-country
  history contract.
- **QA 3:** `light_turret` remains the inexpensive 1 IC / 0.15 reliability option.
  `conventional_turret` is the reviewed 1.5 IC / 0.15 reliability option with
  +0.05 breakthrough. The validator pins this deliberate difference.
- **QA 4:** `nsb_heavy_guns5`, `nsb_heat_mp_ammo0` and `nsb_heat_du_ammo0` each
  carry `start_year = 1985` and sit on the `@1985` row. The validator pins these
  dates; no missing `start_year` source defect was found.
- **QA 6:** `Radar_1` carries fuel 1.2, supply-use -0.075, air attack +0.25 and
  reliability -0.05, matching the living CSV and frozen workbook. The displayed
  `-0` supply value remains a tooltip-precision question, not a zero in script.
- **QA 7:** all 16 focus export helpers use `hidden_effect`, `obsolete = yes` and
  `allow_without_tech = yes`; all 586 national and 40 generic startup designs
  use `mark_older_equipment_obsolete = yes`. The shipped newest-only mechanism
  is present, with no design-name changes.

These were static verification. The owner then confirmed all five in game on
2026-09-08, along with newest-only production visibility and save/reload of an NSB
design, so those three items leave the unverified list below.

## Not yet verified, any batch

Closed by the owner's 2026-09-12 USA capture: non-NSB regression, the 1980 bookmark path
end to end, and equipment/OOB correctness on both profiles. Two entries are retired rather
than verified - the sixteen carrier hull icons and the moved tech-tree columns no longer
exist, phase 4 having deleted the sprites and the owner having reverted the column move
(Finding 18).

Still open: long-run AI production behaviour with mechanized now also in the `armor`
domain, light-family type filtering, the French and West German 1949 starts, every tag
other than USA at either date, and whether the AI ever assigns factories to `land_apc` or
`land_ifv` without a `role_ratio`.

Newest-only production visibility and save/reload of a saved NSB design were
confirmed by the owner on 2026-09-08 and are no longer open.

On that last point: `common/ai_equipment/generic_tank.txt` defines eight
`history = yes` recipes for each of `land_apc` and `land_ifv`, and no `role_ratio`
strategy in this repository names either role. The installed game's
`_documentation.md` does not specify default demand when an explicit ratio is absent.
Static recipe availability does not demonstrate factory assignment, but absence of a
ratio does not prove failure either. No AI strategy change is justified by this
evidence alone. Deferred to the final designer AI pass.

Also outstanding from Tier 3: a runtime render check of the legacy armour folder for
non-NSB players, and a designer UI pass at 1920x1080 and 2560x1440 at 1.0x and 2.4x.

## Playtest log corpus - read the dates before citing it

`error-1949NSB.log`, `error-1949NoNSB.log`, `error-1980NSB.log` and
`error-1980NoNSB.log` at the /LogDocs/Tank_Designer/archive directory are the owner's 2026-09-06 captures.
They are untracked and **predate `eb708e3691` by two days**, so their variant and
OOB evidence describes the pre-migration tree. That is provable rather than assumed:
they report `heavy_mechanized_equipment_3` at `CZE_1980_nsb.txt:289`, and that id
has not existed in any `_nsb` file since `eb708e3691`. New, unverified error logs arrive in
the /LogDocs/Tank_Designer/data directory. As seen by error_9-8-26-2119.log.

Findings 3 and 5 were taken from these logs and then **re-confirmed against current
source** before being acted on. Everything else in them - notably the 1980
`Trying to fill variant where none exist` counts - is stale and must not be used to
size work. A fresh four-profile capture is needed before the coverage sweep is
scoped from runtime demand.

What the stale corpus does establish, because it is a same-build comparison: the
designer bootstrap strictly improves 1980 armour coverage. `medium_tank_chassis`
empty-variant failures were 3 on NSB versus 53 on non-NSB, and `light_tank_chassis`
0 versus 12. The `mechanized_equipment` (79) and `mechanized_heavy_equipment` (93)
failures were **identical in both profiles**, so they are legacy 1980 content gaps
in those countries' histories, not a designer regression.

## Finding 16: the three-hull restructure - measured blast radius, 2026-09-10

Owner direction 2026-09-10. `DECISIONS.md` carries the ratified architecture; this
section carries only the counts, every one of them from a command run against current
source. **Nothing is implemented.**

### What changes shape

| Surface | Now | After | Kind of change |
| --- | --- | --- | --- |
| Designer archetypes | 5 | 3 | delete two families |
| `duplicate_archetypes` role roots | 12 | 17 (14 + 3 flame, pending) | +6 new, -1 heavy AA |
| Special slots | 4 dedicated + 12 free | 15 dedicated | full re-specialization; 21 positions was above the engine cap |
| Module categories | 45 | 49 | +5 new, -1 dissolved |
| Blueprint GUI files | 106 | ~136 | +30 for six roles x hulls, -2 carrier |
| `script_enum_equipment_bonus_type` | 872 entries | ~928 | +6 roots, +50 derived tiers |

### What has to be migrated, counted

| Item | Count | Derivation |
| --- | ---: | --- |
| `apc_chassis_*` / `ifv_chassis_*` references | **857 in 70 files** | regex `\b(apc\|ifv)_chassis_\d` over all `.txt/.yml/.gui/.gfx/.asset/.json` under `Cold War Iron Curtain/` |
| - `common/scripted_effects/` | 588 | 572 in `CWIC_national_tank_presets.txt`, 10 in `CWIC_tank_designer_effects.txt`, 6 in `CWIC_tank_focus_effects.txt` |
| - `history/units/` | 100 | NSB OOB forced variants and production requests |
| - `localisation/english/` | 48 | hull, derived-variant and technology keys |
| - `common/ai_equipment/generic_tank.txt` | 32 | 16 APC + 16 IFV recipes |
| - `common/units/equipment/` | 30 | the two family files themselves |
| - `common/national_focus/` | 27 | migrated legacy armour grants |
| - `common/script_enums.txt` | 16 | 8 APC + 8 IFV hull ids |
| - `common/technologies/NSB_armor.txt` | 16 | `nsb_apc_hulls0..7`, `nsb_ifv_hulls0..7` unlocks |
| Special-slot assignments to re-sort | 9,030 | 8,790 national + 160 generic + 80 export |
| Sub-units consuming a retired archetype | 7 | `mechanized_marine`, `mechanized_airborne`, `mechanized_infantry`, `armored_infantry`, `engineer_mechanized`, `recon_mechanized`, `field_hospital_mechanized` |
| `module_count_limit` blocks to re-derive | 90 | 54 `tank_chassis.txt` + 18 `mechanized.txt` + 18 `mechanized_heavy.txt` |
| Validator functions affected | 11 of 115 | family-identifier scan of `validate_military_reworks.py` |
| Validator contract sites to edit | 27 | contiguous-block grouping of those 11 functions plus the constants |
| Entity aliases affected | 0 | `gfx/entities/zz_CWIC_armor_entity_aliases.asset` contains zero apc/ifv/mechanized strings |

**The cheap-migration guarantee is gone.** The 15-to-21 expansion cost no content edits
because unused optional slots may be omitted and the already-explicit assignments stayed
legal. Full specialization breaks that: a preset that put `Smoke_0` in slot 9 is illegal
once slot 9 is ERA-only. All 9,030 assignments must be re-sorted into fixed positions.
This is mechanical and scriptable, but it is a mass migration and it must not be
described as a contract-only change.

### The tier and year problem, and it is the one real balance consequence

Carriers currently have their own eight-tier ladders. As hull roles they inherit the hull's
tiers, and the ladders do not line up:

| Family | Tiers | Years | Armour range |
| --- | ---: | --- | --- |
| `light_tank_chassis_0..9` | 10 | 1939-2010 | 5 - 27.5 |
| `apc_chassis_0..7` | 8 | 1947-2005 | 15 - 40 |
| `ifv_chassis_0..7` | 8 | 1947-2005 | 30 - 80 |
| `medium_tank_chassis_0..9` | 10 | 1939-2010 | 30 - 75 |
| `heavy_tank_chassis_0..4` | 5 | 1939-1955 | 45 - 65 |

An APC on the light hull inherits armour 5-27.5 against its frozen 15-40; an IFV on the
light hull inherits the same against its frozen 30-80. `for_each` can rewrite a stat per
role - vanilla and this mod both use `hardness = { set = }` - but only uniformly across
every tier, so a role-wide multiplier is the available shape, not a per-tier table.

Consequence, stated plainly: **the frozen 18-envelope carrier mapping and the 40-row
`Balance_Target_Manifest.md` are renegotiated by this restructure, not satisfied by it.**
Eighteen of the forty frozen rows are the mechanized rows keyed to
`mechanized_equipment_*` and `mechanized_heavy_equipment_*` armour values. Whether
carriers keep their armour targets through a role multiplier or adopt the hull's is an
owner balance decision that has to be taken before tier remapping, because the remap
decides which named preset lands on which tier.

Heavy hull ends at 1955, so Heavy Tank, Heavy Tank Destroyer and Heavy SP Artillery have
no post-1955 generation. That is consistent with the period and is not a gap to fill.

### Implementation order

Derived from the dependency graph, not from convenience. Phases 1-3 are additive and
leave the mod playable; phase 4 is the atomic cutover.

1. ~~**Gate A and Gate B first.**~~ **CLOSED 2026-09-10.** Gate A closed positively by the
   owner's live test: `light_armor`, a token this mod invented and vanilla does not
   define, builds on a light tank chassis with zero errors, and custom equipment types are
   documented as supported. Equipment `type` is an **open** enum; the `ifv` and `atgm`
   tokens are legal. Gate B is resolved by planning rather than by test - the six new role
   roots plus their 50 derived tier ids are authored into
   `script_enum_equipment_bonus_type` as part of phase 3.
2. ~~**Category re-cut.**~~ **IMPLEMENTED 2026-09-10**, see below.
3. ~~**Role roots.**~~ **IMPLEMENTED 2026-09-10**, see below. Fourteen roots, module bounds
   authored on the corrected engine model, blueprints at 87.
4. **Carrier cutover, atomic.** Tier remap decision, then all 857 references in one pass:
   presets, OOB requests, focus grants, AI recipes, enum, localisation, technology
   unlocks, sub-unit `need`/`transport`, and the validator's carrier layer. Partial
   landing leaves the mod unbuildable, so this phase does not split.
5. **Battalion taxonomy.** Line and support sub-units rewired onto role roots, the eleven
   `active = no` armour sub-units enabled, division and AI templates updated. This is
   where the designer output finally reaches the battlefield.
6. **Amphibious, unblocked.** Re-price off `DECISIONS.md`, not off Finding 15.
7. **Artillery/AA restructure** and **envelope recalibration**, both against the
   renegotiated manifest.

### Phase 2 - IMPLEMENTED 2026-09-10

Fifteen fully specialized special slots on all five archetypes, `tank_mobility_auxiliary`
dissolved, and the designer corrected from 21 positions to 20. Ratified map, the engine
cap and the merge rationale are in `DECISIONS.md`.

It shipped twice in one pass. The first cut was sixteen special slots / 21 positions; the
owner then established by live test that the engine renders at most twenty custom module
slot windows, so Mine Clearing and Engineering Blade were merged into one Engineering
Equipment slot and slot 16 was removed from every surface. Both categories survive with
their own count limits; no module changed category twice and none became unreachable.

| File | Change |
| --- | --- |
| `modules/00_tank_modules.txt` | 18 modules re-categorised; `tank_mobility_auxiliary` now appears 0 times. `tank_power_auxiliary` 11, `tank_external_fuel` 1, `tank_mine_clearing` 4, `tank_engineering_blade` 2. Line count unchanged at 7132, brace balance 0 before and after. |
| `tank_chassis.txt` | Three archetypes specialized to slots 1-15; limits 54 -> 63. 1905 -> 1548 lines, entirely from collapsed category lists. |
| `mechanized.txt` | APC archetype specialized; limits 18 -> 21. |
| `mechanized_heavy.txt` | IFV archetype specialized; limits 18 -> 21. |
| `interface/equipmentdesigner/tanks/*.gui` | All **106** blueprints lost their `tank_special_slot_16` block; every file now declares the identical ordered list `tank_special_slot_1..15`, verified as one distinct list across all 106. |
| `interface/tank_designer_view.gui` | `pos_custom_module_slot_window_20` removed; positions are 0-19, laid out 7 / 7 / 6 on the unchanged row and column macros. No geometry value changed. |
| `tank_modules_l_english.yml` | Slot labels rewritten; slot 15 is "Engineering Equipment" and slot 16's key is gone. The dissolved category's `EQ_MOD_CAT` key replaced by four new ones. BOM intact, non-ASCII byte count unchanged at 24 - the legal section-sign and pound-sign exceptions. |
| `equipmentdesignermoduleicons.gfx` | `GFX_EMI_tank_mobility_auxiliary` replaced by four category sprites reusing already-shipped textures. Zero new art. |
| `validate_military_reworks.py` | `TANK_FREE_SLOT_CATEGORIES` deleted; 15-entry specialized map; 21-category limit tuple; positions pinned to exactly 0-19; blueprint ordered list 1-15; five-archetype iteration; exact 18-module re-cut contract; every module category reachable from exactly one slot; three new negative fixtures. |

**Structural invariants proved unchanged** by diffing each archetype file against HEAD:
equipment definitions identical (28 / 19 / 10), mandatory slot blocks 15 / 5 / 5,
`module_slots = inherit` 25 / 9 / 8, `default_modules` 3 / 1 / 1, `type` declarations
3 / 9 / 1. Special-slot blocks are 45 / 15 / 15 after the merge. Brace balance 0 before
and after on all three, and on every one of the 106 blueprints and the designer view. No
BOM gained anywhere.

**Zero content migration, as predicted.** No preset, OOB, focus or AI-recipe file was
touched. All 567 non-empty special-slot assignments remain legal because the slot ids were
chosen to preserve their meaning, and none of them used slots 15 or 16.

**Verification.** Full validation passes with only the slot count moving:
`1317 technologies, 289 tank modules, 125 historical tank designs, 40 generic bookmark
variants, 586 national presets and 560 named OOB requests across 68 NSB OOBs, 76
country-history bootstrap sites, 6220 stockpile grants, 8 APC designer hulls, 8 IFV
designer hulls, and 20 designer slots checked.` Every other count is byte-identical to the
pre-change baseline. The in-memory tank negative fixtures were run too, including
`restored_twelve_category_free_list_fixture`, `deleted_mobility_category_module_fixture`
and `twenty_first_gui_position_fixture`; all three mutations were rejected, so the new
contract is not vacuous and the engine cap cannot be re-crossed silently.

**Not run, and owed:** the APC, IFV and stockpile negative fixtures. Those three write to
real mod files and the owner's `-debug` game was live for this whole session. Run
`--tank-self-test` once the game is closed. Static verification only; no balance
acceptance and no in-game check of the new slot labels is claimed.

### Phase 3 - IMPLEMENTED 2026-09-10

The fourteen designer role roots exist, and the module-side bounds that make each role's
equipment role-exclusive are authored. Additive as planned: the standalone APC and IFV
families are untouched and still shipping. Phase 4 retires them.

**A measured correction to the engine model came first, and it changes how every
restriction in this mod should be read.** `allow_equipment_type` **extends** eligibility;
it does not restrict. Proof from shipped, QA-accepted content rather than from
documentation: every tank gun carries `allow_equipment_type = anti_tank`, yet
`medium_tank_chassis` was `type = { armor }` with no `anti_tank` token, and the national
presets mount `tank_medium_cannon1` on `medium_tank_chassis_0` in live games. Only
`forbid_equipment_type` and `forbid_equipment_type_exact_match` exclude anything. Both
keys accept block form - vanilla ships `allow_equipment_type = { missile ballistic_missile }`
(`00_ship_modules.txt:2722`) and a block `forbid_equipment_type` (`00_tank_modules.txt:1378`).

**That exposed a live bug and dictated the token scheme.** `forbid_equipment_type_exact_match
= armor` was the only thing keeping AA cannons off plain gun tanks, and Finding 13 broke it
for the light family when `light_tank_chassis` became `{ armor light_armor }` - exact-match
stopped matching, so light gun tanks could mount AA cannons. Rather than patch it, the
scheme now makes "plain gun tank" a positive, checkable property:

| Archetype / role | `type` |
| --- | --- |
| `light_tank_chassis` | `{ armor light_armor }` |
| `medium_tank_chassis` | `{ armor medium_armor }` |
| `heavy_tank_chassis` | `{ armor heavy_armor }` |
| aa roles | `{ armor anti_air }` |
| artillery roles | `{ armor artillery }` |
| destroyer roles | `{ armor anti_tank }` |
| apc roles | `{ armor mechanized }` |
| ifv roles | `{ armor mechanized ifv }` |
| atgm roles | `{ armor atgm }` |

Size tokens live on base hulls only, so `forbid_equipment_type = { light_armor medium_armor
heavy_armor }` is the exact expression of "not on a plain gun tank". `light_armor` was
removed from the three light role roots; it was added by Finding 13 for a paradrop consumer
that does not exist and cannot exist as a module, so nothing regressed.
`forbid_equipment_type_exact_match` now appears **zero** times in the module file and the
validator rejects its return.

**Role roots: 9 -> 14.** Six new (`light`/`medium` x `apc`/`ifv`/`atgm`), one retired
(`heavy_tank_aa_chassis` - the ratified Anti-Air taxonomy is Light and Medium SPAAG only).
Authored hardness, recorded as authored: APC 0.3, IFV 0.5, ATGM 0.55.

| File | Change |
| --- | --- |
| `x_tank_chassis.txt` | 9 -> 14 roots, new type scheme applied throughout. 92 -> 138 lines. |
| `tank_chassis.txt` | medium and heavy gained their size tokens; light and medium turret and armament slots gained the four carrier categories. Heavy hull unchanged - it hosts no carrier role. |
| `00_tank_modules.txt` | 65 modules bounded. 23 carrier modules gained `allow` + size-token forbid; 38 conventional guns gained `forbid_equipment_type = { mechanized ifv atgm }`; the 3 AA cannons swapped the broken exact-match for a full forbid list; `tank_atgm_launcher_cannon` now allows `{ anti_tank atgm }`. `forbid_equipment_type` 3 -> 68, exact-match 3 -> 0. 7111 -> 7201 lines. |
| `script_enums.txt` | +6 roots +60 derived tiers, -1 root -5 tiers. 821 -> 881 entries. |
| `NSB_armor.txt` | +60 chassis grants across `nsb_iw_armored_vehicles`, `nsb_light_tanks0..8` and `nsb_main_battle_tanks0..8`; -5 heavy AA grants; `heavy_sp_anti_air_brigade` dropped from `enable_subunits`. |
| `generic_tank.txt` | 14 -> 19 AI recipe roots, 116 -> 171 histories: +60 for the new roles, -5 for heavy AA. |
| Blueprints | 6 created, 1 deleted. **82 -> 87**, all declaring `tank_special_slot_1..15`. |
| `need_for_tank_roles.txt` | `heavy_sp_anti_air_brigade` deleted; nothing else referenced it. |
| Localisation | 132 role keys added, 11 heavy-AA keys removed, 2 heavy SPAA battalion keys removed; `tank_designer_ifv` and `tank_designer_atgm` plus their disallowed companions added. |
| `validate_military_reworks.py` | `SUPPORTED_ROLES` replaced by an explicit `FAMILY_ROLES` map (light 6 / medium 6 / heavy 2) that both the grant formula and `expected_tank_types` now index; exact `type` domains pinned for all 14 roots and the 3 hulls; module bounds pinned per category; blueprint count 87; four new fixtures. |

**Four things the gate caught that the batch contract had wrong**, all fixed:

1. **The medium ATGM AI recipe named a category with no launcher in it.** The contract said
   `tank_medium_main_armament`; `tank_atgm_launcher_cannon` is in `tank_small_main_armament`,
   which the medium hull's armament slot already admits (`tank_chassis.txt:323-331`). Both
   ATGM recipes now request the small category, and selection is unambiguous because every
   conventional gun forbids `atgm`.
2. **The ammunition contract did not fit the new roles.** It demanded kinetic and HE of every
   recipe and failed all 20 ATGM recipes and the APC recipes. It is now role-aware: ATGM
   requires `tank_ammo_missile` in slot 7 and rejects shell slots, APC is exempt by family
   name the way the standalone APC family already was, and IFV keeps the full kinetic + HE
   requirement. The stale "exempt because APC modules use `add_stats` only" comment was
   corrected - the source shows they multiply, so the exemption has always been by family.
3. **A retired sub-unit was still consuming the retired role.** `heavy_sp_anti_air_brigade`
   needed `heavy_tank_aa_chassis = 40`. Removed, along with its technology unlock and
   localisation. Nothing else referenced it.
4. **Two new validator fixtures were pointed at the wrong file and one was structurally
   broken.** They read `TANK_ROLE_FILE` (`need_for_tank_roles.txt`, the sub-units) instead of
   `ROLE_CHASSIS_FILE` (`x_tank_chassis.txt`), and the size-token fixture indexed a parsed
   dict by a role name that parse never produces, raising `KeyError`. This is Finding 7
   repeating: a fixture that has never executed proves nothing. Both now mutate file text
   and both reject.

**Verification.** Full validation passes:
`1317 technologies, 288 tank modules, 155 historical tank designs, 40 generic bookmark
variants, 586 national presets and 560 named OOB requests across 68 NSB OOBs, 76
country-history bootstrap sites, 6220 stockpile grants, 8 APC designer hulls, 8 IFV
designer hulls, and 20 designer slots checked.` The in-memory tank negative fixtures pass,
including all four new ones.

Historical tank designs moved 100 -> 155, and the arithmetic closes exactly: +60 derived
types for the six new roles across the 10 / 10 tier ladders, -5 for retired heavy AA.

**Not verified:** nothing in phase 3 has been seen in game. The six new role blueprints, the
role dropdown gaining ATGM and IFV entries, and the module eligibility filtering all need an
owner check. The APC, IFV and stockpile negative fixtures remain unrun while a `-debug` game
is live.

### Finding 20: the two script enums are not interchangeable, and only one is extensible

Established 2026-09-10 from the owner's second QA log, which is the most informative
evidence this project has produced. It **corrects Finding 19's first fix**, which was
wrong.

**`script_enum_equipment_category` mirrors `EQUIPMENT_CATEGORY_META`, hardcoded in the
binary.** Adding a custom token there is not how you register an equipment type. The
engine says so directly, once per token:

```
equipment_category.cpp:357: ifv is in script enum script_enum_equipment_category
but is not an equipment stat (cf. EQUIPMENT_CATEGORY_META in code)
```

All five tokens Finding 19 added - `ifv`, `atgm`, `light_armor`, `medium_armor`,
`heavy_armor` - produced that line and fixed nothing. They are reverted. Custom `type`
tokens on an archetype remain legal and functional; they are simply not categories.

**`script_enum_equipment_bonus_type` is documentation the engine audits in both
directions, and it wants the DERIVED VARIANT ids of every role, not the chassis ids.**
This is the part no one had understood, and it explains the malformed-looking
`chassist` / `chassisbt` entries that three separate passes recorded as "pre-existing
typos, leave them alone". They are not typos. They are what the engine emits, and
`equipment_database.cpp:656` names every missing one:

```
light_tank_apc_chassist_equipment_1 is an equipment type or equipment category
but is not in script enum script_enum_equipment_bonus_type
```

The naming is irregular and was read out of the log rather than predicted, because no
rule derivable from `derived_variant_name` produces it:

| Family | Derived variant pattern | Indices | Hull tiers |
| --- | --- | --- | ---: |
| light | `<role>t_equipment_N` | 1-6 | 10 |
| medium | `<role>bt_equipment_N` | 0-9 | 10 |
| heavy | `<role>t_equipment_N` | 1-5 | 5 |

The index ranges do not match the tier counts and are not consistent between families.
**Do not "correct" them.** The log is the specification.

48 derived ids were added for the six new roles, the 5 stale
`heavy_tank_aa_chassist_equipment_*` entries were removed, and `flame` was restored to
the bonus-type enum - a declared category is itself a bonus type, and `flame` survives
as a category for the MIO policies, so removing it there while keeping the category
produced its own `:656` line.

**The validator now pins all three rules**, replacing Finding 19's incorrect check:
custom type tokens must be absent from `script_enum_equipment_category`; every role's
derived variant ids must be present in `script_enum_equipment_bonus_type` under the
per-family pattern above; every stale derived id must be gone; and every declared
category must also be a bonus type.

### Finding 22: the tank designer role list is a closed, hardcoded set - custom tokens cannot be roles

Established 2026-09-10 from the owner's third QA pass plus a full vanilla audit. **This is
the constraint that decides the carrier half of the restructure, and it invalidates the
phase 3 assumption that a custom `type` token can become a selectable designer role.**

**What the owner observed.** After the Finding 20 enum repair the `equipment_category.cpp`
and `equipment_database.cpp` errors are gone, but the role dropdown still lists exactly
four entries - Tank, Tank Destroyer, Artillery, Anti-Air - with no APC, IFV or ATGM. A
carrier module's tooltip does say it forbids the Tank role and unlocks a role, but that
role renders as "Unknown" and never appears in the dropdown.

**What vanilla says, measured across the whole install.** Every `allow_equipment_type` and
every `duplicate_archetypes` role token in the base game is drawn from one set of five:

| Token | Vanilla `allow_equipment_type` uses | Vanilla role root |
| --- | ---: | --- |
| `anti_tank` | 9 | yes |
| `artillery` | 6 | yes |
| `anti_air` | 3 | yes |
| `flame` | 2 | yes |
| `amphibious` | 1 | yes |

And `localisation/english/designer_l_english.yml` in the base game carries
`tank_designer_<token>` for exactly `amphibious`, `anti_air`, `artillery`, `anti_tank`,
`rocket` and `flame` - plus the AAT support-vehicle roles and the per-archetype chassis
names. There is no mechanism anywhere for declaring a new one.

**So the engine's designer role vocabulary is hardcoded.** A custom token is still
perfectly good for module eligibility - the owner confirmed `forbid_equipment_type` works,
and Gate A's "custom types are legal" stands - but it can never be a **named, selectable
role**. Being listed in `script_enum_equipment_category` does not help either: `mechanized`
is a vanilla category and still produces no dropdown entry, which is the cleanest possible
disproof of the Finding 19 theory.

**This also explains Finding 21's texticon spam, which is now closed.** The spam fires only
when hovering an APC or IFV module, which is precisely when the tooltip renders "unlocks the
"unlocks the <role>" for a role the engine has no icon for. A pound-sign prefix plus an
empty icon name is the
`GFX__texticon` lookup in `bitmapfont.cpp:1844`. Vanilla role-gated modules never spam
because their roles are all in the hardcoded set. The prediction is therefore exact: the
spam disappears the moment the carrier modules gate on a legal role token, and it is not a
separate defect to chase.

**Three usable tokens remain free** - `amphibious`, `flame` and `rocket` - against three
roles that need one: APC, IFV and ATGM. `rocket` is the only one of the three with no
vanilla role root, so its usability is inferred from its `tank_designer_rocket`
localisation key rather than observed, and must be tested before anything depends on it.

The dropdown label is localisation and is ours to write, so a remapped token can read
"Armored Personnel Carrier" regardless of its internal name. What is not cosmetic is
whether `amphibious` or `rocket` carry hardcoded engine behaviour beyond naming - vanilla's
amphibious role is consumed by amphibious sub-units, which is either a bonus or a trap
depending on the design, and that needs the same kind of in-game check.

No content was changed for this finding; it is a decision point, recorded for the owner.

### Finding 23: the carrier consolidation was tried and REVERTED 2026-09-11

Attempted, and it made things worse, so it is recorded as a dead end rather than as
architecture. **Do not retry it without new evidence.**

**The reasoning that led there.** APC on `amphibious` passed owner QA completely. IFV on
`rocket` failed on save with `equipmentdesignerview.cpp:3657: Failed to change role` -
`rocket` has a `tank_designer_rocket` key and a category entry but no vanilla role root,
which renders it without making it switchable. IFV was moved to `flame`, the last token
with a real role root, and then **both** carrier roles failed. The inference was that one
unusable role entry takes down the hull's whole role list, so APC and IFV were collapsed
into a single `amphibious` role with the loadout deciding the vehicle.

**That inference was wrong.** With the two roles consolidated onto the one token that had
been working, **both carriers were still broken in game.** So the failure is not "a second
carrier role poisons the list" - a single carrier role on `amphibious` also fails once the
hull has been through these edits. The real cause is still unidentified.

**Reverted to the last state with a confirmed-working APC**, at the owner's direction and
for the right reason: one working role plus one buggy role beats two broken ones. Restored
exactly:

| Surface | Restored to |
| --- | --- |
| `x_tank_chassis.txt` | 12 role roots; APC `{ armor amphibious }`, IFV `{ armor rocket }`, IFV hardness 0.5 |
| `00_tank_modules.txt` | APC 7 allow `amphibious` forbid size + `rocket`; IFV 16 allow `rocket` forbid size + `amphibious`; 38 guns forbid `{ amphibious rocket }`; 3 AA and the ATGM launcher forbid size + both |
| `script_enums.txt` | 38 IFV entries reinstated beside the APC ones |
| `NSB_armor.txt` | 20 IFV chassis grants reinstated |
| `generic_tank.txt` | 2 IFV recipe roots, 20 histories; 17 roots, 151 histories, 103 HE gates |
| Blueprints | 2 IFV role files regenerated from the APC templates; **85** |
| Localisation | 44 IFV role keys reinstated; `tank_designer_amphibious` "Armored Personnel Carrier", `tank_designer_rocket` "Infantry Fighting Vehicle" |
| `validate_military_reworks.py` | `FAMILY_ROLES` 5/5/2, IFV ids un-retired, blueprint 85, HE gate 103, two-role carrier bounds |

The IFV AI recipes and blueprints were **rebuilt from the surviving APC ones**, not
rewritten from scratch, so their structure is identical by construction. The IFV histories
gate on `nsb_ammo` and `nsb_he_ammo0` and carry kinetic plus HE ammunition, because IFV
armament multiplies attack and the validator's ammunition contract applies to it; that is
also why the HE-gate population returns to exactly 103.

**Flame stays deleted.** The `flame` token is unused again and `tank_designer_flame` is
gone; nothing from the flame family came back with this revert.

### Finding 24: the "Failed to change role" error is benign - RESOLVED 2026-09-11

**There was never a role bug.** Owner QA closes it: the APC and IFV roles work completely -
role header correct in the designer, correct chassis names, separate production lines,
separate equipment-tab entries, and both designs save and build. Confirmed by screenshots
of the light-hull APC and IFV designs, the production tab and the equipment tab.

**Why the error fires.** Carrier modules carry `allow_equipment_type`, which moves the
design into the role the moment the superstructure and armament are fitted. By the time the
player opens the dropdown and picks "Armored Personnel Carrier", the design is *already* in
that role, so `equipmentdesignerview.cpp:3657` logs a failed change for what is a no-op.

The tell was in the message text all along and was missed for three rounds: every failure
named a design whose name is the target role's own chassis localisation -
`Failed to change role to "Armored Personnel Carrier" on "Improved Light Armored Personnel
Carrier"`. That is `light_tank_apc_chassis_2` being asked to become an APC.

**Treat this line as ignorable engine noise**, alongside the other triaged families in
`README.md`. It fires only on a redundant role selection and has no gameplay effect. Do not
chase it, and do not "fix" it by removing `allow_equipment_type` from the carrier modules -
that key is what makes the role assignment work in the first place.

**Two wrong turns this cost, both recorded so they are not repeated.** The flame remap and
the one-role consolidation were both attempts to fix a defect that did not exist. The
consolidation was the more instructive failure: it disproved its own premise and still
reported "broken", because the observation driving it was this benign log line rather than
a real malfunction. The lesson is narrow and practical - **a log line is not a symptom until
the described behaviour is checked in the UI.** The owner's decision to save the design
despite the error is what settled it.

**Owner capture 2026-09-12 adds the workaround, and it corroborates the diagnosis.**
Selecting the role manually after the correct modules are fitted reports the failure;
renaming the design, or simply saving it, clears the state. That is exactly how a no-op
re-assignment onto an already-assigned role behaves - the design itself is unchanged
either way. Still ignorable, still not a defect to chase.

### Phase 3 status: COMPLETE

The three-hull restructure's role layer is done and owner-verified:

- 12 role roots on 3 hulls; APC/Heavy APC on `amphibious`, IFV/Heavy IFV on `rocket`,
  Tank Destroyer / SP Artillery / SPAA on their vanilla tokens, ATGM as a tank-destroyer
  loadout.
- 20 designer positions, 15 fully specialized special slots, 85 blueprints.
- Module bounds keep every role's equipment exclusive, and plain gun tanks excluded via the
  three size tokens.
- Flame removed; heavy SPAA retired.

Outstanding for later passes: amphibious supply, artillery/AA, envelope recalibration.
Phase 4 landed 2026-09-11 and phase 5 on 2026-09-12, both below.

### Phase 4 - IMPLEMENTED 2026-09-11

The carrier cutover landed as one atomic pass. `apc_chassis_0..7` and `ifv_chassis_0..7`
are gone; APC and IFV designs are roles on the light tank hull. The two mechanized
archetypes are plain equipment again - no `module_slots`, no `module_count_limit`, no
`default_modules`, and `type = mechanized` rather than `{ armor mechanized }` - so
non-NSB games keep `mechanized_equipment_1..10` and `mechanized_heavy_equipment_1..8`
exactly as before.

**Tier mapping, owner ruling: not-later-than-year.** Each retired tier lands on the
newest light hull tier whose year does not exceed it.

| Legacy | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| APC to light tier | 2 | 3 | 4 | 4 | 5 | 6 | 7 | 8 |
| IFV to light tier | 2 | 3 | 3 | 4 | 5 | 6 | 7 | 8 |

Two pairs collide, APC 2+3 on tier 4 and IFV 1+2 on tier 3. Measured before migrating:
zero duplicate `(tag, name, chassis)` triples across all 572 national presets, so no
national design was lost or merged.

**The delta instrument, owner ruling: armour, cost and speed carried by role-exclusive
modules.** The sixteen freed `nsb_apc_hulls0..7` / `nsb_ifv_hulls0..7` technologies no
longer enable equipment - the role tiers are already unlocked by the light hull ladder
from phase 3 - so each now unlocks one rung of an eight-step superstructure ladder. Five
APC and six IFV modules were authored to fill the ladders out from the shipped three and
two. Verified arithmetically on all sixteen rungs: light hull tier stat plus module
`add_stats` reproduces the retired chassis row exactly for armour, build cost and maximum
speed.

`defense`, `breakthrough`, `reliability` and `fuel_consumption` adopt the hull curve by
the same ruling. The deltas dropped are large and deliberate - APC breakthrough -17 to
-14, IFV defense +24 to +39 - because reproducing them would have meant a troop
compartment that adds 39 defense, which defeats putting carriers on the hull curve.
Phase 7 owns the recalibration.

**Corrections to Finding 16 that the migration produced:**

1. **There were never 18 frozen carrier rows.** `Balance_Target_Manifest.md:52` reads
   "The 18 mechanized rows remain explicitly out of scope for the tank designer pass",
   and the living balance CSV carries no carrier module rows at all. Finding 16's "the
   frozen 40-row manifest is renegotiated, not satisfied" is wrong: there was no frozen
   carrier contract to renegotiate. The only source of truth for carrier numbers was the
   equipment file, which is what the ladder reproduces.
2. **`for_each` cannot re-price a role.** Audited every `for_each` block in vanilla -
   `x_tank_chassis.txt` and `x_plane_airframes.txt`, 21 blocks. The entire observed
   vocabulary is `variant_name = { find_and_replace }`, `hardness = { set }` and
   `air_superiority = { set }`. No `multiply`, and no stat outside those two. Finding 16's
   "a role-wide multiplier is the shape available" rests on an operator nothing
   demonstrates, and the one proven operator would flatten a stat across all ten tiers.
3. **Sub-unit `need` needed no change.** Finding 16 counted seven sub-units consuming a
   retired archetype. The archetypes are not retired - only the designer hulls are - so
   `mechanized_infantry` and the six others still resolve `mechanized_equipment` and its
   legacy rows. Getting designer output to the battlefield remains phase 5's job.
4. **857 references was 809.** The measured count against current source, after the
   phase 1-3 work moved some of it.

**What the cutover touched.** 732 equipment-id rewrites across 66 files; 16 script enum
entries removed; 64 localisation keys removed and 22 added; 16 technologies rewired; two
dead designer windows deleted, 85 blueprints to 83; the two standalone carrier AI recipe
families deleted as exact duplicates of the phase 3 role recipes, HE-gated recipes 103 to
95; 16 orphaned hull picture sprites removed. Every national preset and the ten generic
bookmark designs now mount their tier's superstructure.

**Two generic designs were dropped, deliberately.** A bookmark chassis may hold exactly
one generic design, so `Standard APC 1965` and `Standard IFV 1955` - the non-owning half
of each merged pair - are gone. Both generations keep all their national presets, and the
manifest records this as `has_generic_design`. Generic bookmark variants 40 to 38.

**The IFV armour inversion is carried forward unchanged, and it is a defect.** A 2005 IFV
has 80 armour against the 2010 MBT's 75, and the 1947 IFV has 30 against the 1947 light
tank's 10. The cutover reproduces it exactly because a cutover preserves observable
behaviour; phase 7's envelope recalibration is where it should be priced. Do not read the
ladder's +20 to +55 rungs as authored intent.

**Hardness is the one carrier stat the cutover does not preserve.** Legacy APC 0.5 and IFV
0.6 against the role roots' 0.3 and 0.5, set by `for_each` in phase 3 and owner-verified in
game. Left alone rather than changed under a ruling that named three other stats.

Gate line after the pass: `1317 technologies, 299 tank modules, 135 historical tank
designs, 38 generic bookmark variants, 586 national presets and 560 named OOB requests
across 68 NSB OOBs, 76 country-history bootstrap sites, 6220 stockpile grants, 16 carrier
superstructure rungs, and 20 designer slots checked.`

### Phase 5 - IMPLEMENTED 2026-09-12

Designer carrier output now reaches the battlefield. Before this pass a player could
design, produce and stockpile an APC or IFV and no battalion in the game consumed it:
`mechanized_infantry` and `armored_infantry` still drew the retired
`mechanized_equipment` / `mechanized_heavy_equipment` families.

**Scope is narrower than Finding 16 implied, and the narrowing is measured.** Three
things were already true before this pass and needed no work:

1. **The armour line battalions already work.** `light_armor`, `medium_armor` and
   `heavy_armor` need the base hulls, and the legacy `lt_equipment_*`, `mbt_equipment_*`
   and `ht_equipment_*` rows were reparented into those same hull families in an earlier
   pass, so one battalion serves the NSB designer and the non-NSB legacy path together.
2. **The eight role brigades are neither inactive nor unreachable.** Tank destroyer, SP
   artillery and SPAA brigades on the role roots are `active = no` but each carries an
   `enable_subunits` grant in `NSB_armor.txt`, which is the ordinary
   technology-gated pattern, not a disabled unit. 59 of the mod's 91 land sub-units are
   `active = no` for the same reason, including `engineer` and `artillery`.
3. **Artillery and AA stay out.** Their legacy battalions still consume the standalone
   `sp_artillery_equipment`, `spaag_equipment` and `medium_tank_destroyer_equipment`
   families, and converging those is the artillery/AA restructure the owner deferred.

**What changed.** Six battalions move onto the carrier role families, on all three of
`need`, `essential` and `transport`: `mechanized_infantry`, `engineer_mechanized`,
`recon_mechanized` and `field_hospital_mechanized` to `light_tank_apc_chassis`;
`armored_infantry` and `mechanized_airborne` to `light_tank_ifv_chassis`. `essential`
matters as much as `need` - it is what a battalion must hold to read as combat-ready, and
leaving it stale would have made every rewired battalion silently register as unequipped.

Their ids are untouched, so the migration costs zero OOB edits: `mechanized_infantry`
alone appears 2,366 times across 294 order-of-battle files, `armored_infantry` 977 times
across 163, and renaming any of them would also have forced NSB and non-NSB division
templates apart, which the mod deliberately keeps identical.

**Non-NSB is preserved by relocation, not by a second battalion.** All 18 legacy carrier
rows - `mechanized_equipment_1..10` and `mechanized_heavy_equipment_1..8` - move into the
two role families and now carry `archetype = light_tank_apc_chassis` /
`light_tank_ifv_chassis`. They live in `x_tank_chassis.txt` rather than `mechanized.txt`
because of load order: the role archetypes do not exist until that file is evaluated.

Every stat the retired archetype used to supply is written out explicitly on each
relocated row, because the new archetype supplies the light tank hull's values instead.
Verified numerically across all 18 rows and 13 stats: effective armour, speed, defense,
breakthrough, hardness, attack, cost, fuel and lend-lease are identical to the values
those rows had before the move. A non-NSB game fields exactly the carriers it fielded
before.

**Two precedents carried the design, and both were checked rather than assumed.** Vanilla
declares plain, pre-NSB equipment inside a duplicated archetype - `light_tank_aa_equipment_1`
is a 1934 row with `archetype = light_tank_aa_chassis` - so a role family may hold members
that the designer did not generate. And this mod already ships an empty archetype:
`lt_equipment` has zero members, every `lt_equipment_N` having been reparented to
`light_tank_chassis`. `mechanized_equipment` and `mechanized_heavy_equipment` are now the
same kind of empty shell, which is why they are kept rather than deleted - roughly 180
military industrial organization, idea and decision entries name those archetype ids.

**A plan that was measured and abandoned.** The first design rewired the battalions and
left the legacy rows where they were, which would have cost non-NSB its carriers outright.
The second worried that relocating the rows would empty the archetypes and silently kill
those ~180 production bonuses. The `lt_equipment` precedent settles it: the bonuses key on
an archetype id that survives, and the mod has shipped exactly this shape through several
playtests.

**A validator bug this pass exposed.** `top_level_blocks` never stopped at its root's
closing brace, so once `x_tank_chassis.txt` gained an `equipments` section beside
`duplicate_archetypes`, all 18 relocated rows were reported as tank role roots. The parser
now breaks when the root closes.

New contracts: `validate_carrier_battalions` pins all three wiring keys per battalion and
rejects any land sub-unit file that still names a retired carrier family; the carrier role
contract now requires the legacy rows to sit in the role family with their stats stated
explicitly. Both proven to bite by mutating real source - a stale `transport`, a stale
`essential`, a stale `need`, a row left on the old archetype and a row that loses an
explicit stat are each reported, with every file restored afterwards.

Gate line is unchanged by this pass.

### Playtest acceptance, 2026-09-12

Owner capture: USA at 1949 and 1980 on NSB and non-NSB. **All four profiles pass.**
Equipment is redefined as intended and the OOBs read correctly, so the phase 4 carrier
cutover and the phase 5 battalion rewire are accepted in game rather than only statically
verified. This closes the fresh-capture item owed since 2026-09-06 and supersedes the
stale 2026-09-06 and 2026-09-08 log corpora for everything it covers.

The only issue observed was Finding 24's benign role line, with the workaround now known -
see that finding. No new defect was reported.

The acceptance is USA-scoped. It is not evidence about other tags, the French and West
German 1949 starts, or long-run AI production, all of which remain open above.

### Phase 6 - IMPLEMENTED 2026-09-12

Marines ride the APC role family. `mechanized_marine` had been consuming
`mechanized_marine_equipment` since before the restructure, so a player could field an
entire designer carrier fleet and still not supply a marine battalion with any of it.

**One option died before the ruling, and it is worth stating plainly: a selective
amphibious designer role is not buildable.** Finding 22 established the usable role token
vocabulary as exactly five, and all five are spent - `anti_air`, `anti_tank`, `artillery`,
`amphibious` on APC, `flame` on IFV. No sixth token exists and none can be registered. So
Finding 15's option list reduced to two: APC-wide marine transport, or a sixth standalone
designer family. The owner ruled for APC-wide. Findings 14 and 15 are closed by that
ruling rather than by a fix; `DECISIONS.md` carries the reasoning.

**What changed.** `mechanized_marine` names `light_tank_apc_chassis` on all three of
`need`, `essential` and `transport` - the same three-key rule phase 5 established, for the
same reason. The five `mechanized_marine_equipment_1..5` rows moved into
`x_tank_chassis.txt` under `archetype = light_tank_apc_chassis`, each stating every stat
the retired archetype used to supply, and `mechanized_marine.txt` is now an archetype-only
empty shell. The ids never change, so the `amphibious1..5` grants, 18 OOB references, six
`script_enums.txt` entries and the MIO, idea, focus and country-leader references all keep
resolving with no edit.

Marine armour comes down under phase 7's cap in the same pass: 24 / 31 / 35 / 42 / 49
against the old 24 / 36 / 48 / 64 / 80. Hardness aligns to the APC family's 0.5 from 0.55.

`mechanized_marine` stays `active = no`; the technology gate was not in scope and the
validator still asserts it.

New contract: `validate_marine_carrier` pins the empty shell, the five relocated rows,
their archetype, seven explicitly stated stats each, their exact armour and the cap.
`mechanized_marine` joins `CARRIER_BATTALIONS`, and the retired-family scan over
`common/units/*.txt` now rejects `mechanized_marine_equipment` alongside the other two.

### Phase 7 - carrier envelope recalibration, IMPLEMENTED 2026-09-12

The three defects phase 4 knowingly preserved are priced and closed. `DECISIONS.md`
carries the two rulings; this is what shipped.

**1. The armour inversion, both profiles.** Owner ruling: no carrier exceeds 70% of the
same-year medium tank hull. IFV armour goes 30 / 36 / 44 / 48 / 56 / 64 / 72 / 80 to
**22 / 25 / 28 / 31 / 35 / 39 / 44 / 49** on the designer rungs and on the eight relocated
legacy rows alike, against caps of 28 / 31.5 / 31.5 / 35 / 38.5 / 42 / 45.5 / 49. The old
ladder put a 2005 IFV at 80 against the 2010 MBT's 75 and the 2000 MBT's 70. APC armour is
untouched at 15 to 40 - it was never near the cap - and neither is carrier cost or speed.

**2. The defensive profile, restored rather than recalibrated.** This reverses phase 4's
"they adopt the hull curve", and the reason is that the curve was the wrong shape, not
merely the wrong magnitude. Every light hull tier is `defense = 6`, `breakthrough = 20`; a
carrier is `defense = 11..45`, `breakthrough = 3..18`. The 16 rungs now carry both stats
and reproduce the retired chassis rows exactly:

| Generation | APC defense / breakthrough | IFV defense / breakthrough |
| --- | --- | --- |
| 0-7 | 11/3, 14/4, 14/4, 16/5, 16/5, 16/5, 19/6, 19/6 | 30/12, 35/14, 36/14, 40/16, 40/16, 41/16, 45/18, 45/18 |

The breakthrough deltas are negative, between -17 and -2. Phase 4's objection - that
reproducing IFV defense meant a module adding 39 - is what shipped, because a troop
compartment that makes the vehicle defensible is the module doing its job.

**3. Hardness.** `light_tank_apc_chassis` sets 0.5 and `light_tank_ifv_chassis` 0.6, the
legacy values, replacing 0.3 / 0.5. The 15 per-rung hardness adds are deleted: with
`for_each ... hardness = { set }` deciding the family value, a module add is a second
authority over one stat.

**A fourth thing the pass found.** Three rungs carried an undocumented `multiply_stats` 5%
bump - `apc_open_troop_bay` on speed, both `*_frontal_engine_layout` on armour - which
silently broke the hull-tier-plus-module arithmetic every envelope claim is written in.
Phase 4's "verified arithmetically on all sixteen rungs" was true of the `add_stats` and
wrong about the shipped total on those three. Removed. Empty `multiply_stats` blocks are
shipped style on eleven rungs and stay; the ban is on a multiplied value.

`reliability` and `fuel_consumption` stay on the hull curve. Neither inverts anything and
changing them would mean inventing numbers.

New contracts: the two ladders carry `defense` and `breakthrough`, so `carrier_module_errors`
pins five stats per rung instead of three and rejects any hardness add or multiplied stat;
`carrier_armour_cap_errors` applies the 70% rule to all 16 designer generations, the 18
relocated legacy rows and the 5 marine rows; the role roots' `for_each` hardness value is
pinned per family. Five new negative fixtures cover a lost defense delta, a retained hull
breakthrough, a stacked hardness add, a multiplied stat and an over-cap 2005 IFV, plus
positive fixtures for the repriced IFV, a carrier sitting exactly on the cap and the empty
multiply block.

Gate line: `... 6220 stockpile grants, 16 carrier superstructure rungs, 5 relocated marine
rows, and 20 designer slots checked.` The marine-row counter is the only movement.

**Static verification only.** No live testing is claimed for either phase. What wants
in-game eyes: that a marine division equips off APC production on both profiles, and that
the repriced IFV still reads as worth its cost now that its armour is roughly two thirds of
what it was.


### Role-token probe - PASSED, and the remap is IMPLEMENTED 2026-09-10

The two-line probe answered Finding 22's open question. Owner result:

- **Both `amphibious` and `rocket` appeared as designer roles** on the light and medium
  hulls. The hardcoded token set is usable and the remap is authorable.
- **The texticon spam stopped for the IFV modules and persisted for the APC modules.** That
  asymmetry is the diagnosis, not a loose end: at probe time the APC modules still carried
  `forbid_equipment_type = { ... ifv }`, and `ifv` is a non-hardcoded token the tooltip
  cannot draw an icon for. The IFV modules forbade only size tokens, which are never
  rendered as roles. After the remap no module references `ifv`, `atgm` or `mechanized`, so
  the spam is expected to be gone entirely - **owner re-check owed.**
- **A design given the probe role produced base-hull equipment and reverted to the base
  role.** Expected: no role root carried those tokens during the probe, so there was nothing
  to switch to. The owner's own control observation - assigning the artillery role does
  produce distinct equipment - confirms the mechanism is sound.

**The remap as shipped.** `DECISIONS.md` carries the ratified mapping and the reasoning.
Role roots go **14 -> 12**; the two `*_tank_atgm_chassis` roots are deleted and ATGM becomes
a loadout on the tank destroyer role.

| File | Change |
| --- | --- |
| `x_tank_chassis.txt` | APC roots to `{ armor amphibious }`, IFV roots to `{ armor rocket }`, both ATGM roots deleted. 12 roots. 138 -> 122 lines. |
| `00_tank_modules.txt` | 65 modules retargeted. APC allows `amphibious` and forbids `{size rocket}`; IFV allows `rocket` and forbids `{size amphibious}`; 38 conventional guns forbid `{amphibious rocket}`; AA cannons and `tank_atgm_launcher_cannon` likewise. Key counts unchanged at 68/68/0 - this was a retarget, not an expansion. |
| `script_enums.txt` | 38 ATGM entries removed (2 roots, 20 tiers, 16 derived variants); bonus entries 925 -> 887. The 13 legacy `atgm_equipment` / `atgm_carrier_equipment` ids are untouched - those are the pre-existing non-designer families. |
| `NSB_armor.txt` | 20 ATGM chassis grants removed across `nsb_iw_armored_vehicles`, `nsb_light_tanks0..8` and `nsb_main_battle_tanks0..8`. |
| `generic_tank.txt` | 2 ATGM recipe roots and 20 histories removed; roots 19 -> 17. Both destroyer recipes already request `tank_small_main_armament`, so they can select `tank_atgm_launcher_cannon` with no edit - verified, not assumed. |
| Blueprints | 2 ATGM files deleted, **87 -> 85**, all still `tank_special_slot_1..15`. |
| Localisation | 44 ATGM keys removed; `tank_designer_amphibious` now reads "Armored Personnel Carrier" and `tank_designer_rocket` reads "Infantry Fighting Vehicle", so the internal token name is invisible to players. |
| `validate_military_reworks.py` | `FAMILY_ROLES` to 5/5/2; ATGM ids retired; blueprint count 85; **a new legal-token contract** rejecting any eligibility value or hull/role type token outside the hardcoded set, with a failure message citing the probe. |

**Two parent corrections to subagent work**, both caught by the gate:

1. **The standalone APC and IFV families were wrongly remapped too.** They are phase 4 scope
   and keep `type = { armor mechanized }`; `REFERENCE.md` records that token as load bearing
   for land/transport classification and every `transport = mechanized_equipment` consumer.
   Restored.
2. **The legal-token contract initially banned `mechanized` outright.** It is a real vanilla
   equipment type - it is simply not a *designer role*. The check now distinguishes the two:
   `LEGAL_TANK_DESIGNER_TYPE_TOKENS` governs module eligibility and the three hulls plus
   their role roots, while `LEGAL_CARRIER_FAMILY_TYPE_TOKENS` adds `mechanized` for the two
   carrier families and their hulls only.

**Verification.** Gate passes: `1317 technologies, 288 tank modules, 135 historical tank
designs, ... 20 designer slots checked`. In-memory fixtures pass, including the new
`non_hardcoded_module_fixture`. Historical designs moved 155 -> 135, which is exactly the
two deleted roles across the 10 + 10 tier ladders. A grep of every `allow_equipment_type`
and `forbid_equipment_type` line in the module file returns zero `mechanized`, `ifv` or
`atgm`.

**Owner QA result.** APC passed completely: role assigns, APC production is separate, and
the `_texticon` spam is gone - Findings 21 and 22 are both closed by the remap exactly as
predicted. IFV failed on save with
`equipmentdesignerview.cpp:3657: Failed to change role to "Infantry Fighting Vehicle"`.

**Cause and fix, same day.** `rocket` is not a real designer role. It has a
`tank_designer_rocket` key and a category entry, which is enough to render it in the
dropdown, but **no vanilla `duplicate_archetypes` role root anywhere in the base game** -
unlike `amphibious`, `anti_air`, `anti_tank`, `artillery` and `flame`, which all have one.
The APC role worked because `amphibious` is in that group. IFV therefore moved to `flame`,
the last token in it, free because flame tanks were deleted earlier the same day. The
internal name is invisible: `tank_designer_flame` reads "Infantry Fighting Vehicle", and
`tank_designer_rocket` was restored to "Rocket Artillery".

Scope of the swap: 2 role roots, 65 module restriction lines, 4 localisation keys and the
validator's IFV expectations. No other surface moved, because the remap had already put
every carrier reference on a token boundary.

One validator contract had to change with it. The flame-removal pass banned the `flame`
*type token* outright; the IFV roles now legitimately carry it. The check is now on the
family **name** - no chassis or role may contain `flame` - which is what was actually
retired. The role roots themselves stay pinned by `removed_tank_role_errors` and
`UNSUPPORTED_IDS`.

**The usable designer role vocabulary is exactly five and all five are now spent:**
`anti_air`, `anti_tank`, `artillery`, `amphibious`, `flame`. No further designer role can be
added - any future vehicle class has to be a loadout on an existing role or its own
archetype family. This is why ATGM is a tank-destroyer loadout and not a role.

**Owner re-check owed:** that the IFV role now saves and produces distinct equipment.

### Finding 21: the texticon spam - CAUSE IDENTIFIED, see Finding 22

**Closed as a diagnosis, open as a fix.** The cause is a role with no icon, because the
role token is not in the engine's hardcoded set. It resolves with the role remap, not on
its own. The elimination work below is kept because it rules out four plausible-looking
causes that would otherwise be re-investigated.

Open. `bitmapfont.cpp:1844: Couldnt find texticon: _texticon` appears **1,682 times** in
the current log, continuously at roughly 142 per second while the designer is open. The
empty name means a pound-sign texticon prefix in a localisation string resolved to nothing.

**It is new work, not pre-existing noise.** All three archived playtest logs -
`error-1949NSB.log`, `error-1980NSB.log` and `error_9-8-26-2119.log` - contain **zero**
occurrences. That is the one hard fact available.

Four hypotheses were tested and eliminated:

1. *Missing category title or sprite.* Fixed in Finding 19; the owner re-tested with the
   icons loading correctly and the spam persisted.
2. *Modules without `xp_cost`, making the `$EXPERIENCE_TYPE$` texticon empty.* Known inconsistency 4
   claims turret modules lack `xp_cost`. Measured against current source: **all 288
   modules have it.** That inconsistency is stale and should be closed.
3. *A malformed texticon sequence in mod localisation.* A scan of every English `.yml` for a
   pound-sign followed by a non-name character found 89 hits, all of them legal - the terminated
   terminator form or literal pound-sterling prose in UK content.
4. *A mod override diverging from vanilla.* The designer strings that use
   `$EXPERIENCE_TYPE$` and `$XPICON$` texticon strings are byte-equivalent to vanilla's.

That leaves the variable resolving empty at runtime, which points at equipment whose
bonus-type resolution fails - exactly what Finding 20 repaired. **Re-test before
investigating further**, because the enum was broken for all 48 derived role variants
when that log was captured. If the spam survives the enum fix, the next step is an A/B
with the designer opened on a pre-phase-3 chassis versus a new role chassis, diffing the
log, rather than more static reading.

### Finding 19: phase 3 QA - three defects, all of them presentation contracts nothing checked

Owner in-game QA of phase 3, 2026-09-10. Three symptoms, three distinct causes, all static
and all now pinned by the validator. Nothing about the role architecture was wrong.

**Symptom 1: the role dropdown still showed only four roles** - Tank, Tank Destroyer,
Artillery, Anti-Air - and selecting a carrier module unlocked a role labelled "Unknown".

Cause: **an equipment `type` token only becomes a role the UI can offer once it is declared
in `script_enum_equipment_category`.** `ifv` and `atgm` were never added there, so the
archetypes loaded, the modules bound correctly, the forbid rules worked - and the dropdown
had nothing to list. This refines the mechanism `REFERENCE.md` describes: the dropdown lists
one entry per distinct `allow_equipment_type` value, but only for *declared* categories.

The same check caught a third undeclared token nobody had noticed: **`light_armor` has been
undeclared since Finding 13 shipped it.** That is why Finding 13 could describe it as
"behaviour-neutral" - an undeclared token participates in nothing. All five tokens are now
declared: `ifv`, `atgm`, `light_armor`, `medium_armor`, `heavy_armor`.

This also explains Gate A's outcome more precisely than "equipment `type` is an open enum".
The engine does accept an undeclared token without error - the owner's `light_armor` test
was real - but the token is inert for anything that enumerates categories. Custom tokens are
legal **and must be declared to do anything.**

**Symptom 2: selecting Turret or Gun opened a category with an undefined label and a broken
texture, and spammed the log.** 1,203 `bitmapfont.cpp:1844: Couldnt find texticon: _texticon`
lines, with the empty name being the missing category title.

Cause: a module category needs two presentation assets that nothing was checking - an
`EQ_MOD_CAT_<category>_TITLE` localisation key and a `GFX_EMI_<category>` sprite. An audit of
every category reachable from a `tank_chassis.txt` slot found **six** gaps, only four of them
introduced by phase 3:

| Category | Missing | Introduced by |
| --- | --- | --- |
| `tank_apc_superstructure`, `tank_apc_armament` | both | phase 3 put them on the tank hulls |
| `tank_ifv_superstructure`, `tank_ifv_armament` | both | phase 3 put them on the tank hulls |
| `tank_suspension_multi_track` | both | the 2026-09-09 4-Track batch |
| `tank_secondary_turret` | sprite only | pre-existing |

The four carrier categories had never carried either asset, including on the APC and IFV
designers where they have shipped since `660f8984ae` - the gap was invisible because those
slots hold exactly one category, so the selector never drew a category header. Putting them
on a multi-category slot exposed it. All six are now authored, reusing already-shipped module
textures; zero new art.

**Symptom 3: the new role tooltips used the wrong wording.** `tank_designer_ifv` and
`tank_designer_atgm` got "Remove the module that forbids..." - the phrasing for an
archetype-swap role. A role reached by *allowing* a type takes "Add a module that allows..."
like `tank_designer_anti_air`. Corrected, and the archetype-shaped keys were added alongside
the type-token ones per `REFERENCE.md`'s standing advice to keep both shapes until one is
observed resolving.

**Two new validator contracts**, because the whole class of defect was invisible statically:

1. Every category reachable from any archetype slot must have an `EQ_MOD_CAT` title key and a
   `GFX_EMI` sprite. This is in `tank_category_contract_errors`.
2. Every equipment `type` token used by any archetype or role root must be declared in
   `script_enum_equipment_category`. This is in `validate_tank_type_domains`, and it failed on
   first run against the three size tokens - which is how `light_armor` was found.

**Verification.** The gate passes with the inventory line unchanged from phase 3. The fixes
are static; whether the dropdown now lists Armored Personnel Carrier, Infantry Fighting
Vehicle and ATGM Carrier needs an owner re-check, and so does the texticon spam. The log
evidence for symptom 2 was read from the live `error.log` rather than inferred.

### Flame removal - IMPLEMENTED 2026-09-10

Owner ruling: flame tanks are axed completely. Ratified in `DECISIONS.md`, including the
four surfaces deliberately left alone and why.

**It was safe to take in full because nothing consumes it.** `history/`,
`common/ai_templates/` and every OOB contain zero references to any flame sub-unit or
flame chassis, so no division template, starting order of battle or AI template lost a
battalion. The complete footprint was 33 files.

| Surface | Change |
| --- | --- |
| `x_tank_chassis.txt` | 3 role roots removed; 9 remain, in order light/medium/heavy x aa/artillery/destroyer. 113 -> 92 lines. |
| `need_for_tank_roles.txt` | `light_flame_tank`, `medium_flame_tank`, `heavy_flame_tank` deleted in full. 1106 -> 847 lines. The three armour battalions are untouched. |
| `00_tank_modules.txt` | `flamethrower` deleted; confirmed by scoped grep to be the sole member of `tank_flamethrower` before deletion. 7132 -> 7111 lines. |
| `tank_chassis.txt` | `tank_flamethrower` removed from all three `main_armament_slot` lists; nothing else touched. |
| `NSB_armor.txt` | 29 grant lines removed across `nsb_iw_armored_vehicles` (7), `nsb_light_tanks0..8`, `nsb_main_battle_tanks0..8` and `nsb_heavy_tanks0..3` (1 each). No technology deleted, no block emptied. |
| `generic_tank.txt` | 3 AI recipe blocks removed, 17 -> 14; surviving recipes byte-identical. |
| `script_enums.txt` | 49 derived flame entries plus the bare `flame` bonus type removed from `script_enum_equipment_bonus_type`, 871 -> 821. |
| Blueprint GUIs | 24 flame files deleted; **106 -> 82**, and all 82 still declare `tank_special_slot_1..15`. |
| `.gfx` | `GFX_SMI_flamethrower`, `GFX_EMI_tank_flamethrower` and three flame MIO department sprites removed. |
| English localisation | 67 keys from `tank_modules_l_english.yml` and `tank_designer_flame` / `tank_designer_flame_role_disallowed` from `designer_l_english.yml`. |
| `zz_CWIC_armor_entity_aliases.asset` | 670 dead flame aliases removed, 3019 -> 2349 entries, 15246 -> 11897 lines. Load-order-critical `zz_` name untouched. |
| Living balance CSV | the `flamethrower` row removed, 354 -> 353 lines. The frozen workbook is untouched and still hashes `dc2c9800b69b0f2f00568cdfe0f4bcac55c8bdd61476409b4a88b6d8e566b532`. |
| `validate_military_reworks.py` | `SUPPORTED_ROLES` is now `("aa", "artillery", "destroyer")`; `FLAME_TECH_GRANTS` and `flame_grant_errors` deleted; the 25 derived flame chassis ids, 3 sub-units, the module and the category added to `UNSUPPORTED_IDS`; blueprint count pinned at 82 with `tank_chassis_*_tank_flame*.gui` rejected the way amphibious already was; the dead flamethrower ammunition exemption removed; one new fixture `reintroduced_flame_role_fixture`. |

**Two corrections the parent made to subagent work, both caught by the gate:**

1. **`script_enum_equipment_category` must keep `flame`.** An agent removed it along with
   the bonus-type entries. Six `has_mio_equipment_type = flame` policy conditions under
   `common/military_industrial_organization/` still name that token and are explicitly out
   of scope, so deleting the enum value would have left them referencing an undeclared
   entry. Restored. The bonus-type removals stand - those are designer ids, not the
   equipment-domain vocabulary.
2. **The unsupported-id scan was reading prose.** It globbed `.info` alongside `.txt`,
   `.gui` and `.gfx`, so `common/unit_leader/_invalid_sub_unit_modifiers.info` failed for
   naming the very ids it documents as absent. `.info` files are notes and the engine
   never loads them; the suffix is dropped from that scan.

**Verification.** Full validation passes:
`1317 technologies, 288 tank modules, 100 historical tank designs, 40 generic bookmark
variants, 586 national presets and 560 named OOB requests across 68 NSB OOBs, 76
country-history bootstrap sites, 6220 stockpile grants, 8 APC designer hulls, 8 IFV
designer hulls, and 20 designer slots checked.` The in-memory tank negative fixtures pass
too, including the new flame-role fixture.

Two counts moved and both are accounted for: tank modules 289 -> 288 is the deleted
`flamethrower`, and historical tank designs **125 -> 100** is family x tier x role losing
three roles across the 10 / 10 / 5 ladders - exactly 25 derived types. No design content
was lost.

**Consequence to expect in game:** the designer role dropdown drops from five entries to
four on every chassis. `REFERENCE.md` explains why - the list is one entry per distinct
`allow_equipment_type` value in the loaded module set, and `flamethrower` was the only
module carrying `flame`. That is the intended outcome.

Static verification only. The APC, IFV and stockpile negative fixtures remain unrun while
a `-debug` game is live.

### Finding 17: the 20-window cap, and what the 2026-09-09 verification actually proved

Recorded 2026-09-10 because the failure mode is subtle and will recur. On 2026-09-09 this
folder recorded "21 positions is now verified, not plausible - do not reopen it as an
engine risk", on the strength of an owner designer capture plus a live `error.log` with
zero `Could not find "tank_special_slot_*"`, zero `Requested GUI element not found` and
zero `containerwindow.cpp` lines.

**All of that was true and none of it was evidence of rendering.** The engine resolves and
logs the 21st slot happily; it just never draws it. The one contrary observation was
already written down and dismissed: Finding 6's "one cosmetic note, not a defect" describes
six `+` affordances and a dark seventh cell in the bottom row, attributed to a `-debug`
resolution overlay. That dark cell was the 21st position failing to render.

The lesson generalises past this slot: **a clean log proves the engine parsed a
declaration, not that it honoured it.** Where a count exceeds anything vanilla ships, the
acceptance evidence has to be a positive visual count of the rendered elements, not the
absence of errors.

### Finding 18: the tech-folder right-edge ceiling contract is retired

The gated-item decision to move `nsb_tank_design_tree` from x=3600 to x=1650 and
`nsb_armor_tree` from x=2400 to x=950 was applied in an earlier session and **reverted by
the owner on 2026-09-10**. The owner's finding: the clipping is not caused by the origins.
Shifting the technologies left still leaves the right-most ones cut off even with the
horizontal scrollbar present, so the cause is the folder's usable extent rather than where
the content sits. It is cosmetic - no gameplay effect - and the owner logged it as a note,
not a defect.

The validator was enforcing the reverted position and failed with 55 right-edge errors
against the owner's restored GUI. `TECH_FOLDER_RIGHT_EDGE_CEILING` and the 3187px
comparison are removed; `validate_tank_folder_right_edges` is renamed
`validate_tank_folder_gridboxes` and keeps every structural check that earned its place -
one container per folder, no repeated or unmapped gridboxes, no missing gridbox, every
technology's folder x mapped, and sane origin/slot-width values. Its negative fixture now
probes an unmapped gridbox name instead of the retired pixel ceiling.

Open, and genuinely unexplained: what actually bounds the drawable width of a technology
folder. The 3187px figure was empirical (`industry_folder` is the widest that does not
clip) and it is now known to be an incomplete model, because moving content inside it did
not help. Anyone picking this up should measure the folder container and its scroll extent
rather than the technology coordinates.


### Carried forward from the previous next scope

These remain owed and are not superseded by the restructure:

1. ~~**Fresh playtest capture.**~~ **Done 2026-09-12** - USA, 1949 and 1980, NSB and
   non-NSB, all four accepted. See "Playtest acceptance, 2026-09-12". The French and West
   German 1949 starts and non-USA coverage were not in the capture and stay open.
2. **Historical coverage sweep** - named designs for every armour family across all
   countries. Its scope is the role table. Phase 4 landed, so this is now unblocked.
3. **`mp_uav_1`** - the two ISR grants still need a content owner's decision.
4. ~~**The flame decision.**~~ **Answered and implemented 2026-09-10** - flame is removed.
   Phase 3 authors six role roots, not nine. No open decisions remain on the restructure.

### A tooling note from this session

The baseline self-test was run while the owner's `-debug` game was live (pid 50004).
Per Finding 8 that is exactly the condition that produces the 2380 spurious
`A limit for category X already exists` burst, because the APC and IFV negative fixtures
write to the real `mechanized.txt` and `mechanized_heavy.txt` and a `-debug` game
hot-reloads them. Any `error.log` line in that session's log after the run time is
suspect and must not be treated as evidence. The check is `pgrep hoi4` before the
validator, every time. Running the script **without** `--tank-self-test` performs every
real contract check and writes nothing, so it is the safe form while a game is up.


Estimator status: module parents no longer stack predecessor stats. Radar II fuel 1.2
and GL ATGM III hard attack 95 are tested regression anchors. Full-design ordering,
caps, role bonuses, inherited chassis defaults, technology/MIO effects and agreed
tolerances remain uncalibrated. The envelope report samples 11 of 21 tank generations.

## Next scope: 3D models, vehicle images, legacy NSB duplicates - context gathered 2026-09-13

Owner direction 2026-09-13 after a passing playtest. Nothing below is implemented; this
section is the measured starting position for those three items. Baseline self-test on an
untouched tree matches the 2026-09-12 line exactly - `1317 technologies, 299 tank modules,
135 historical tank designs, 38 generic bookmark variants, 586 national presets and 560
named OOB requests across 68 NSB OOBs, 76 country-history bootstrap sites, 6220 stockpile
grants, 16 carrier superstructure rungs, 5 relocated marine rows, and 20 designer slots
checked` - so the delta for this session is zero.

**Phases 6 and 7 are recorded as implemented but are not committed.** Working tree carries
`CWIC-Special-Units.txt`, `mechanized_marine.txt`, `00_tank_modules.txt`,
`x_tank_chassis.txt` and `validate_military_reworks.py` modified, +399/-230. Commit that
before starting new work, or a later pass cannot tell the two batches apart.

**The role root set is twelve, not fourteen, and there are no ATGM roots.**
`x_tank_chassis.txt:4-124`: light aa/artillery/destroyer/apc/ifv (`:8,18,27,35,44`), medium
aa/artillery/destroyer/apc/ifv (`:58,67,75,83,92`), heavy artillery/destroyer (`:107,116`).
ATGM is a loadout on the tank-destroyer role per `DECISIONS.md`; heavy AA and flame are
retired. Any scout report citing six new roots including ATGM is reading the phase-3 plan,
not the file.

### 3D models

`gfx/entities/zz_CWIC_armor_entity_aliases.asset` is 2349 entries over 11,896 lines and its
own header states the lookup it feeds: `<TAG>_<sub_unit>_<visual_level>_entity`. Each entry
clones a country mesh entity under a derived name, e.g. `clone = "AFG_heavy_armor_entity"` /
`name = "AFG_heavy_armor_0_entity"` (`:5-8`), and role variants use the sub-unit id, e.g.
`AFG_heavy_tank_destroyer_brigade_0_entity` (`:30-33`).

**The key is the sub-unit and visual level, not the equipment id or the design name.** Zero
aliases name any of the twelve role roots or any derived role tier. Vanilla
`gfx/entities/units_tanks.asset` uses the same plain `TAG_<class>_armor[_N]_entity` naming
and contains no `tank_chassis`, module, turret or gun strings, so there is **no evidence in
either tree that a fitted module swaps a sub-entity**, and none that a named design can
carry its own model. Per-design historical models are unproven, not merely unimplemented.
What the evidence does support is per-country, per-sub-unit, per-visual-level models - which
is exactly the granularity the alias file already ships.

The 2026-09-08 log holds zero entity or GFX database lines naming CWIC content: all
`equipment_graphic_database.cpp:49/:72/:106` lines are base-game and old country content, the
already-triaged noise. So nothing is currently broken here; this item is additive art work.

### Vehicle images

Three archetype `picture` values cover every tank family: `archetype_light_tank_equipment`
(`tank_chassis.txt:10`, `tank_light.txt:13`), `archetype_medium_tank_equipment`
(`tank_chassis.txt:305`, `tank_medium.txt:9`) and `archetype_heavy_tank_equipment`
(`tank_chassis.txt:597`, `tank_heavy.txt:9`), plus `archetype_motorized_equipment` on
`mechanized.txt:11`, `mechanized_heavy.txt:12` and `mechanized_marine.txt:11`.
The twelve role roots and all relocated legacy rows in `x_tank_chassis.txt` declare no
`picture` and inherit.

**Five picture values resolved to no sprite anywhere - RESOLVED 2026-09-13.** Registered
`GFX_archetype_*_medium` sprites across the mod (`interface/Technologies.gfx:975-991`) and the
base game are `archetype_light_tank_equipment`, `archetype_medium_tank_equipment`,
`archetype_heavy_tank_equipment`, `archetype_super_heavy_tank_equipment`,
`archetype_modern_tank_equipment`, `archetype_motorized_equipment` and
`archetype_motorized_rocket_equipment`. An audit of all 30 distinct `picture` values under
`common/units/` found five armour families naming something outside that set, not three: the
two originally measured plus `archetype_sht_equipment` and `archetype_mechanized_marine_equipment`.
The engine logs nothing for any of them - grep of the 2026-09-08 log returns zero lines - so the
wrong production icon was silently wrong.

**Owner ruling: rename the picture value onto an already-registered sprite, which implies no new
art.** Six declarations changed, one per line, nothing else touched:

| Family | Was | Now |
| --- | --- | --- |
| `medium_tank_chassis` (`tank_chassis.txt:305`), `mbt_equipment` (`tank_medium.txt:9`) | `archetype_mbt_equipment` | `archetype_medium_tank_equipment` |
| `heavy_tank_chassis` (`tank_chassis.txt:597`), `ht_equipment` (`tank_heavy.txt:9`) | `archetype_ht_equipment` | `archetype_heavy_tank_equipment` |
| `sht_equipment` (`tank_super_heavy.txt:12`) | `archetype_sht_equipment` | `archetype_super_heavy_tank_equipment` |
| `mechanized_heavy_equipment` (`mechanized_heavy.txt:12`) | `archetype_mechanized_heavy_equipment` | `archetype_motorized_equipment` |
| `mechanized_marine_equipment` (`mechanized_marine.txt:11`) | `archetype_mechanized_marine_equipment` | `archetype_motorized_equipment` |

The two mechanized families go to the motorized picture because **no `archetype_mechanized_*`
sprite is registered anywhere and vanilla's own `mechanized.txt:7` uses
`archetype_motorized_equipment`** - following vanilla rather than inventing a name. Both
mechanized families therefore share one icon, which is exactly what vanilla does.

**New validator contract, because this class of defect is invisible at runtime.**
`validate_armour_archetype_pictures()` pins all ten armour families to an expected picture value
and additionally fails if that value has no registered `GFX_<picture>_medium` sprite in the mod
or in the literal vanilla set. The vanilla set is a literal because the validator must not depend
on a Steam install path existing. Proven to bite: reverting `tank_heavy.txt` to
`archetype_ht_equipment` produces both failures, the mismatch and the missing sprite.

**Still unverified in game.** Static verification only - the rendered icons have not been seen.
The rename can only improve matters, since the previous values resolved to nothing.

**Out of scope and deliberately untouched:** the same audit found eight aircraft and helicopter
picture values with no registered sprite - `archetype_jet_multirole_equipment`,
`archetype_cv_jet_multirole_equipment` (3 sites), `archetype_jet_CAS_equipment`,
`archetype_jet_interceptor_equipment` (2), `archetype_mach2stratbomber_equipment` (3),
`archetype_rocket_interceptor_equipment`, `attack_helicopter_equipment` (2) and
`scout_helicopter_equipment`. Same silent failure, different content owner. Reported, not fixed.

Per-design art stays closed for tanks on the same evidence that closed it for carriers.
Vanilla `interface/tank_profiles.gfx` is 6188 lines of enumerated
`GFX_<tag-or-generic>_<hull>_<profile>` sprites keyed on hull, module combination and
graphical culture, with texture paths `designer/<tag>/<TAG>_<hull>_<profile>.dds`; the mod
neither overrides nor extends it, and its eight
`gfx/interface/equipmentdesigner/tanks/designer/0N_tank_icons.txt` files are 0 bytes. National
presets are `create_equipment_variant` blocks with no art key
(`CWIC_national_tank_presets.txt:13-25`, BTR-40 at `:544-552`). So the realistic image work is
**profile-sprite coverage per hull and graphical culture**, not one picture per historical name.

Art already shipped and currently reachable only as technology icons:
`interface/cwic_tank_rework_icons.gfx:2620-2680` (8 APC hulls) and `:2707-2724` (8 IFV hulls),
plus national pieces such as `WGR_apc_2/3`, `WGR_ifv_2/3`, `SOV_apc_10`, `SOV_ifv_2..8`,
`USA_ifv_3/4` and generic `mbt_0..9` under `gfx/interface/technologies/`.

### Duplicate legacy vehicles on NSB - IMPLEMENTED 2026-09-13, narrowed mid-pass

**Shipped: 37 of the 64 legacy rows are now DLC-gated.** Read the scope correction below before
extending this - the artillery/SPAA/TD/ATGM half was gated, measured to break NSB division
templates, and reverted inside the same pass.

Sixty-four numbered legacy rows are declared - the earlier count of 54 in this section was
wrong - and before this pass **none carried `can_be_produced` or any DLC predicate**, so on an
NSB profile every one sat in the production tab beside its designer replacement:

| Family | Rows | Declared at |
| --- | --- | --- |
| `lt_equipment_1..6` | 6 | `tank_light.txt:55,96,127,158,190,223` |
| `mbt_equipment_0..9` | 10 | `tank_medium.txt:57,67,98,129,161,193,225,257,289,321` |
| `ht_equipment_1..5` | 5 | `tank_heavy.txt:55,101,132,164,197` |
| `mechanized_equipment_1..10` | 10 | `x_tank_chassis.txt:137,167,202,237,272,307,344,382,419,457` |
| `mechanized_heavy_equipment_1..8` | 8 | `x_tank_chassis.txt:494,524,561,598,636,674,712,750` |
| `mechanized_marine_equipment_1..5` | 5 | `x_tank_chassis.txt:788,816,845,874,903` |
| `spaag_equipment_1..5` | 5 | `sp_aa.txt:50,61,90,121,151` |
| `sp_artillery_equipment_1..5` | 5 | `sp_art.txt:54,66,96,126,156` |
| `medium_tank_destroyer_equipment_1..5` | 5 | `tank_destroyer.txt:52,93,124,155,187` |
| `atgm_carrier_equipment_0..4` | 5 | `atgm_carrier.txt:54,62,93,124,157` |

Enabling technologies carry no DLC predicate either: `armor.txt` MBT `:47..393`, heavy
`:429..599`, mechanized `:959..1354`, heavy mechanized `:1400..1724`, amphibious 1-5 at
`:1767,1795,1830,1866,1901`; `artillery.txt` SPAAG `:258..388`, SP artillery `:1273..1403`,
medium TD `:3402..3531`; `rocket.txt` ATGM `:1516..1667`.

**Correction to `DECISIONS.md`'s gating note: the claimed `OR = { has_tech = legacy has_tech = nsb_* }`
precedent does not exist in `common/units/`.** Measured: zero matches. The closest real sites are
dual-tech blocks in `common/technologies/support.txt:84,132,186,240,292,380,432`, and
`common/ai_equipment/generic_tank.txt` has NSB-only enables (`:14,41,68`). Do not cite a
`common/units/` precedent that is not there; pick the mechanism deliberately.

Live consumers that break if a row is deleted rather than gated: sub-unit `need` at
`CWIC-Anti-Air.txt:111,115`, `Support-Units.txt:1764,1768` (`spaag_equipment`),
`CWIC-Anti-Tank.txt:118,122` (`medium_tank_destroyer_equipment`) and `:269,273`
(`atgm_carrier_equipment`), `CWIC-Artillery.txt:120,124` (`sp_artillery_equipment`); the generic
AI template's `lt_equipment` at `:20`; and weapon-purchase decisions granting SPAAG and SP
artillery rows (eastern block `:765,792,818,842,869,895,918,944,969`, SP artillery `:1898`, WGR
`:344-372`). **Gating, not deletion, is the only option that keeps these alive**, which matches
the ratified position that the archetypes survive for non-NSB play.

### What shipped

Thirty-seven rows gained `can_be_produced = { NOT = { has_dlc = "No Step Back" } }`, inserted
immediately after the row's `year` line - or after its `archetype` line for `lt_equipment_1`,
which declares no row-local year and inherits 1942 from its archetype:

| File | Rows gated |
| --- | ---: |
| `tank_light.txt` | 6 (`lt_equipment_1..6`) |
| `tank_medium.txt` | 10 (`mbt_equipment_0..9`) |
| `tank_heavy.txt` | 5 (`ht_equipment_1..5`) |
| `x_tank_chassis.txt` | 16 (`mechanized_equipment_3..10`, `mechanized_heavy_equipment_1..8`) |

**Seven rows stay ungated, the ratified exception set:** `mechanized_equipment_1..2`, the
pre-designer WWII rows with no designer replacement, and `mechanized_marine_equipment_1..5`,
which stay legacy because marines ride any carrier under the 2026-09-13 ruling. Verified
independently of the subagents that made the edits: none of the seven carries `has_dlc`, and the
`duplicate_archetypes` block is untouched.

These four families are safe to gate because their battalions consume a family that still holds
designer members. The tank rows carry `archetype = light/medium/heavy_tank_chassis` and the three
armour battalions `need` those hulls; the carrier rows were relocated into
`light_tank_apc_chassis` / `light_tank_ifv_chassis`, which the carrier battalions name directly
(`CWIC-Infantry.txt:158-165,235-242`, `CWIC-Special-Units.txt:99-106,278-285`,
`CWIC-Support-Units.txt:122-127,457-462,937-941`). Nothing is stranded.

### Scope correction: the artillery/SPAA/TD/ATGM half was gated and reverted

All 20 rows in `sp_aa.txt`, `sp_art.txt`, `tank_destroyer.txt` and `atgm_carrier.txt` were gated
in this pass and then **reverted to byte-identical**, because the premise that justified gating
them was wrong.

The premise was that their legacy battalions are all `active = no` and therefore unreachable. The
first half is true - `CWIC-Anti-Air.txt` `spaag`, `CWIC-Artillery.txt` `sp_artillery` /
`light_sp_artillery` / `heavy_sp_artillery`, `CWIC-Anti-Tank.txt` `tank_destroyer` /
`atgm_carrier` and `CWIC-Support-Units.txt` `spaag_support` are every one `active = no`. The
second half does not follow: **`active = no` means "enabled by technology", not "unreachable"**,
and ordinary non-DLC technologies enable them on both profiles - `artillery.txt:254` (spaag),
`:1276` (sp_artillery), `:1621` (light), `:1980` (heavy), `:3405` (tank_destroyer) and
`rocket.txt:1513` (atgm_carrier).

Then the measurement that settles it: **NSB division templates across `history/` still field
those battalions** - 43 `_nsb` files name `sp_artillery`, 20 `light_sp_artillery`, 20
`tank_destroyer`, 9 `spaag`, 9 `heavy_sp_artillery`, 3 `atgm_carrier`. Gating their equipment
leaves every one of those templates unproducible on NSB. That is a regression, not a cleanup.

The same scan turned up families the original inventory missed entirely:
`light_sp_artillery_equipment_*`, `heavy_sp_artillery_equipment_*` and `rocket_sp_artillery`.
The artillery side is wider than this section previously claimed, which is further reason not to
gate it piecemeal.

**So gating the support-armour half requires rewiring those battalions onto the role families
first.** That rewire is the artillery/AA convergence, and it **landed 2026-09-13** - see
Finding 26. All 20 rows plus the ten this section did not know about are now gated.

## Finding 26: the artillery/AA convergence - IMPLEMENTED 2026-09-13

**Every armoured ground vehicle is now a role on the light, medium or heavy hull, with no
standalone family left.** This is the last restructure the three-hull architecture owed, and it
turned out far cheaper than the carrier cutover because phase 3 had already built the
destination: the twelve role roots, all NSB chassis grants, the 53 role blueprint GUI files, the
eight role AI recipes and every derived enum tier already existed. Nothing was created. Content
moved into place.

### What shipped

| Surface | Change |
| --- | --- |
| `x_tank_chassis.txt` | All **30** legacy rows relocated into their role families, every inherited stat written out explicitly. Groups at `:981-1178` SPAAG, `:1182-1383` light SP artillery, `:1387-1589` ATGM carrier, `:1593-1796` SP artillery, `:1800-2004` medium TD, `:2008-2212` heavy SP artillery. |
| `sp_aa.txt`, `sp_art.txt`, `light_sp_art.txt`, `heavy_sp_art.txt`, `tank_destroyer.txt`, `atgm_carrier.txt` | Six archetype roots survive as **empty shells**, zero members each - the shape `lt_equipment` has had since the legacy tank rows were reparented. They stay because MIO, idea and country-leader entries name five of the six. |
| `CWIC-Anti-Air.txt`, `CWIC-Artillery.txt`, `CWIC-Anti-Tank.txt`, `CWIC-Support-Units.txt` | Seven battalions rewired onto role families, amounts unchanged: `spaag` and `spaag_support` to `light_tank_aa_chassis` (36/18), `sp_artillery` to `medium_tank_artillery_chassis` (18), `light_sp_artillery` to `light_tank_artillery_chassis` (18), `heavy_sp_artillery` to `heavy_tank_artillery_chassis` (18), `tank_destroyer` to `medium_tank_destroyer_chassis` (36), `atgm_carrier` to `light_tank_destroyer_chassis` (36). All stay `active = no`; sprites and categories untouched. |
| `need_for_tank_roles.txt` | The **eight duplicate role brigades deleted** - light/medium/heavy tank destroyer, light/medium/heavy SP artillery, light/medium SP AA. The three armour battalions (`light_armor`, `medium_armor`, `heavy_armor`) are byte-identical. |
| `NSB_armor.txt:82-89` | The eight `enable_subunits` entries for those brigades removed - they were dangling the moment the brigades went. The surviving battalions are enabled by their own legacy technologies on both profiles, so nothing replaces them. |
| `script_enums.txt` | 30 legacy tier entries removed, 871 -> 841. The six root ids stay; every role derived tier was already enumerated. Nothing added. |
| `x_tank_chassis.txt` (second pass) | All 30 relocated rows **DLC-gated**, which is what the convergence unlocked. |
| `validate_military_reworks.py` | New relocation contract plus the extended gate map; see below. |

### Which battalion survived, and why that choice

Two complete sets existed: the legacy battalions (`active = no`, consuming legacy families) and
the eight role brigades (`active = yes`, consuming role roots). They were functional duplicates.
**The legacy ids survived because `history/` uses them and names the role brigades nowhere** - 43
`_nsb` files name `sp_artillery` alone. Keeping the brigades instead would have meant rewriting
division templates across a hundred-plus files for a rename. This is the same ruling phase 5 made
for the carriers: one battalion serves both profiles, and it is the one the content already names.

The deleted brigades' metadata is preserved here in case a later pass wants it: each carried
`need = <its role chassis> = 40`, sprites `light_armor` / `medium_armor` / `heavy_armor`, and
categories `category_tank_destroyers`, `category_self_propelled_artillery` or
`category_self_propelled_anti_air` alongside `category_all_armor` and `category_army`.

### `rocket_sp_artillery` is not an armour family and was excluded

Measured, and it corrects the earlier assumption that it was a seventh family to converge: the
sub-unit at `CWIC-Artillery.txt:621` consumes `motorized_rocket_equipment` from
`rocket_artillery.txt:5`, **no `rocket_sp_artillery` equipment id exists anywhere**, and no
technology declares `enable_equipments` for one. It is a motorized family wearing an artillery
name. It, `rocket_sp_artillery_support` and `motorized_rocket_equipment` were left untouched and
are out of scope for the three-hull architecture entirely.

### Validator

`validate_legacy_armour_roles()` pins the converged shape: each of the 30 rows must live only in
`x_tank_chassis.txt`, must declare its mapped role archetype, must **not** be parented to a
legacy archetype, and must state every stat explicitly - a literal key set, not a union derived
from siblings, because a derived union weakens itself the moment a sibling loses a key. The six
shells must keep zero members. The seven battalions must consume their mapped family and stay
`active = no`; the three armour battalions must stay `active = yes`. The eight deleted brigade
ids joined `UNSUPPORTED_IDS`, so reintroducing one fails.

Both new contracts were proven to bite, not assumed: deleting `air_attack` from
`spaag_equipment_1` produces `spaag_equipment_1 must state air_attack explicitly after the
relocation`, and re-parenting it to `spaag_equipment` produces `must not be parented to legacy
archetype spaag_equipment` plus the archetype mismatch. Both restored.

### Three validator bugs the first gate run caught, all in new code

Worth recording because each was a plausible-looking wrong assumption about ids:

1. The relocation map keyed SPAAG as `sp_aa_equipment`, derived from the filename. The archetype
   is `spaag_equipment`.
2. The armour battalion check expected `light_tank` / `medium_tank` / `heavy_tank`. The ids are
   `light_armor` / `medium_armor` / `heavy_armor`.
3. It required `transport = <role family>` on all seven battalions. **These battalions ARE the
   armour and carry no `transport`** - that key belongs to the infantry carriers. The check now
   fails if one ever gains a `transport`.

The eighth failure was real content: `NSB_armor.txt` still enabled the eight deleted brigades.
The contract found it, which is the contract working.

### Verification

Self-test passes with the inventory line **unchanged** from baseline - a relocation moves no
count, and the 135 historical designs, 299 modules and 20 slots all held. Independently
re-verified rather than taken from the subagents: all 30 ids present in `x_tank_chassis.txt`,
zero numbered members left in the six source files, all six roots present, and
`spaag_equipment_1` - the highest-risk row, which previously inherited *everything* - now
declares `air_attack`, `ap_attack`, `armor_value`, `breakthrough`, `build_cost_ic`, `defense`,
`fuel_consumption`, `hard_attack`, `hardness`, `maximum_speed`, `reliability`, `resources`,
`soft_attack` and `upgrades` explicitly. No BOM on any edited file.

**Static verification only.** Owner QA owed, and it is a bigger surface than the last pass: on
NSB confirm the production tab now shows no legacy artillery, SPAAG, TD or ATGM duplicates and
that SPAAG/artillery/TD battalions still build from designer equipment; on non-NSB confirm those
same battalions and the legacy rows behave exactly as before. Division templates in existing
saves are not migrated - use fresh campaigns.

## Finding 27: the brigade deletion orphaned two role families - FIXED 2026-09-13

**A regression introduced by Finding 26's own cutover, found the same day by the contract
written to prevent exactly this.** Deleting all eight duplicate role brigades went two too far:
six were genuine duplicates of a surviving legacy battalion, but **`heavy_tank_destroyer_chassis`
and `medium_tank_aa_chassis` had no other consumer**. Measured: after the deletion, a grep of
`common/units/` for either id returned nothing. Designer output for those two families could be
designed, researched and produced, and no battalion in the game would take it - which also
silently dropped Heavy Tank Destroyer and Medium SPAAG from the ratified battalion taxonomy.

The mapping that makes the asymmetry obvious, and which should have been checked before deleting:

| Deleted brigade | Surviving consumer of the same family |
| --- | --- |
| `light_tank_destroyer_brigade` | `atgm_carrier` |
| `medium_tank_destroyer_brigade` | `tank_destroyer` |
| `heavy_tank_destroyer_brigade` | **none** |
| `light_sp_artillery_brigade` | `light_sp_artillery` |
| `medium_sp_artillery_brigade` | `sp_artillery` |
| `heavy_sp_artillery_brigade` | `heavy_sp_artillery` |
| `light_sp_anti_air_brigade` | `spaag` |
| `medium_sp_anti_air_brigade` | **none** |

**Fix:** `heavy_tank_destroyer_brigade` and `medium_sp_anti_air_brigade` are restored to
`need_for_tank_roles.txt` byte-for-byte from `HEAD~1`, re-added to `NSB_armor.txt:82-83`
`enable_subunits`, and removed from `UNSUPPORTED_IDS` with a comment naming why they are not
retired. The other six stay retired and stay pinned.

**New contract, and it is the real deliverable here:** `validate_tank_rework()` now fails when
any declared role family has no sub-unit naming it anywhere under `common/units/` -
`role family <root> has no sub-unit consuming it`. Designer output that cannot reach the
battlefield is the failure class this whole restructure has hit repeatedly (phase 5 existed
because of it), and nothing checked for it until now.

### It immediately found two more, and they predate this session

`medium_tank_apc_chassis` and `medium_tank_ifv_chassis` - the **Heavy APC and Heavy IFV** roles -
have had no consuming battalion since phase 3 authored them. Every carrier battalion names the
light roles (`CWIC-Infantry.txt:158-165,235-242`, `CWIC-Special-Units.txt:99-106,278-285`,
`CWIC-Support-Units.txt:122-127,457-462,937-941`). So two of the twelve role families are
designable and unusable, and have been for three sessions.

The ratified battalion taxonomy lists Heavy APC and Heavy IFV under Infantry Carrier, so this is
a real gap rather than an intentional omission. **Closed 2026-09-17 by Finding 31**: both roles
now have a battalion, the `unconsumed_by_decision` exception is deleted, and all twelve role
families are guarded by the contract.

## Finding 31: the Heavy APC and Heavy IFV battalions - IMPLEMENTED 2026-09-17

Owner ruling, recorded in full in `DECISIONS.md` "Heavy carrier battalions". APCs are
mechanized and IFVs are armored: `mechanized_infantry` (APC) and the new
`heavy_mechanized_infantry` (Heavy APC) stay in `group = mobile`, while `armored_infantry`
(IFV) moves to `group = armor` and the new `heavy_armored_infantry` (Heavy IFV) joins it
there. The two existing ids are untouched, so the 2,366 `mechanized_infantry` and 977
`armored_infantry` OOB references cost nothing.

What changed, six files:

| File | Change |
| --- | --- |
| `common/units/CWIC-Infantry.txt` | `heavy_mechanized_infantry` and `heavy_armored_infantry` authored; `armored_infantry` regrouped to `armor` |
| `common/technologies/NSB_armor.txt` | both battalions added to `nsb_iw_armored_vehicles`' `enable_subunits`, beside `light_armor`/`medium_armor`/`heavy_armor` |
| `localisation/english/unit_l_english.yml` | `armored_infantry` relabelled "Armored Infantry"; its old "Heavy Mechanized Infantry" label transferred to the new Heavy APC battalion; two name and two desc keys added |
| `gfx/entities/zz_CWIC_armor_entity_aliases.asset` | 800 aliases: 40 TAGs x 10 visual levels x 2 sub-units, cloning `<TAG>_mechanized_entity` for the 22 TAGs that declare one and `mechanized_entity` for the rest |
| `CWIC Backup/tools/validate_military_reworks.py` | both battalions added to `CARRIER_BATTALIONS`; `unconsumed_by_decision` deleted; two new per-battalion contracts |

**The alias file was not optional, and the contract said so before the battalions shipped.**
Adding the two sub-units failed the self-test immediately with
`no entity of any kind covers heavy_armored_infantry` - Finding 28's coverage rule fires for
any sub-unit whose `need` names an armour hull, and a sub-unit with no entity renders a
default mesh with no log line. Ten levels because both roles sit on the ten-tier medium hull;
40 TAGs because a sub-unit the alias file owns outright must cover every TAG the file names.
No alias shadows a national entity, so the pinned `native_overrides = 140` is unchanged.

**Two new contracts, both for silent-failure classes this pass could have shipped into.** A
carrier battalion declared `active = no` must be named by some live `enable_subunits` block,
and must have an English name key. Either omission produces a battalion that is invisible or
renders as its raw id, and the engine logs neither. New helper `enabled_subunits()` reads
every `common/technologies/*.txt`, skipping the parked doctrine directory for the same reason
the doctrine contracts do. No negative fixture: both checks read the real tree rather than a
mutated string, and giving them a text seam means restructuring `validate_carrier_battalions()`.

**Heavy APC and Heavy IFV were ruled NSB-only, and that ruling is now void.** It rested on the
two medium carrier families having no non-NSB-producible member, which turned out to be the
very thing that made the battalions unreachable on *either* profile. The legacy ladders
authored below serve both profiles, so "one battalion serves both profiles" holds for all four
carrier battalions after all, and the owner's 2026-09-17 acceptance of the asymmetry is moot
rather than overridden.

**Owner QA 2026-09-17: Mechanized Infantry and Armored Infantry appeared in their proper
groups; the two heavy battalions were not selectable. The cause was the era gate, and the gate
is now moved.** Neither enabling tech was DLC-gated and both `enable_subunits` blocks were
live, so the only cause was that `mechanized_infantry8` starts 1985 (needs `hardware_V`) and
`mechanized_heavy_infantry8` starts 2005 (needs `hardware_XII`), against 1944 and 1947 for the
two light battalions' techs. **An `active = no` sub-unit whose technology is unresearched is
absent from the division designer, not greyed out**, which is why it read as a missing unlock.

**First attempt: `nsb_iw_armored_vehicles`. It did not work, and the reason it looked safe is
worth keeping.** Both entries were moved onto the NSB armour root beside `light_armor`,
`medium_armor` and `heavy_armor`, which 463 country-history files grant. Owner QA with every
hull researched still showed neither battalion, and `error.log` named neither id.

**The evidence that broke the tie, and it is a reasoning trap this folder should not repeat.**
`light_armor`, `medium_armor` and `heavy_armor` are **also** enabled by legacy `armor.txt`
technologies (`:720`, `:49`, `:431`), so their presence in game proves nothing about whether
the NSB root's `enable_subunits` fires. The only two sub-units that technology enables
exclusively - `heavy_tank_destroyer_brigade` and `medium_sp_anti_air_brigade` - are
`group = armor_combat_support` and never appear in the line-battalion lists, so the screenshots
could not confirm them either. **There was no positive evidence for that block at all; it was
picked because it looked architecturally right.**

**Resolved by using the only enablers with direct in-game proof.** `heavy_mechanized_infantry`
now sits in `mechanized_infantry`'s `enable_subunits` (`armor.txt:955-958`, 1944) and
`heavy_armored_infantry` in `mechanized_heavy_infantry`'s (`:1397-1400`, 1947) - the exact two
blocks that enable `mechanized_infantry` and `armored_infantry`, both of which the owner's QA
screenshots show live in their proper groups. The NSB-root entries are removed, so each
battalion has one enabler. This still satisfies the ruling that a battalion unlocks with its
hull rather than its generation year: 1944 and 1947 are earlier than every medium carrier tier
a player can field.

**Both gate moves were wrong. The owner's `active = yes` probe settled it 2026-09-17: the
battalions did not appear even with the technology taken out of the question, so enablement was
never the cause.**

## Finding 33: a role family whose only members are derived tiers cannot satisfy a `need`

**This is the real defect, it predates the battalions, and it invalidates a ratified claim.**
`DECISIONS.md` Finding 15 established that "a role root **is** a family" nameable by a sub-unit's
`need`. That is false on its own. A `duplicate_archetypes` role root needs **at least one plain
member** - an equipment row declaring `archetype = <root>` - before a sub-unit can draw from it.
Tiers derived by `for_each` are not enough, and the engine logs nothing at all.

The measurement that proves it, across the twelve role families:

| Role family | Plain member rows | Battalion in game |
| --- | ---: | --- |
| `light_tank_apc_chassis` | 15 | present |
| `light_tank_ifv_chassis` | 8 | present |
| `light_tank_aa_chassis`, `light_tank_artillery_chassis`, `light_tank_destroyer_chassis` | 5 each | present |
| `medium_tank_artillery_chassis`, `medium_tank_destroyer_chassis` | 5 each | present |
| `heavy_tank_artillery_chassis` | 5 | present |
| **`medium_tank_apc_chassis`** | **0** | absent |
| **`medium_tank_ifv_chassis`** | **0** | absent |
| **`medium_tank_aa_chassis`** | **0** | absent, unobservable |
| **`heavy_tank_destroyer_chassis`** | **0** | absent, unobservable |

The split is exact: every family with a plain member works, every family without one does not.
Vanilla agrees and is the reason the shape was never in doubt for the eight that work - it
declares `medium_tank_aa_equipment_1..3` under `medium_tank_aa_chassis` and a plain ladder under
every other role family a sub-unit consumes, while its childless roots (`*_amphibious_chassis`,
`*_flame_chassis`) have no consuming sub-unit at all. The eight working mod families only have
plain members by accident of history: they received relocated legacy rows in the 2026-09-12
carrier cutover and the 2026-09-13 artillery convergence. The four that never had legacy content
never got any.

**Two of the four were already broken before this session.** `medium_sp_anti_air_brigade` and
`heavy_tank_destroyer_brigade`, restored on 2026-09-13 by Finding 27 precisely so their designer
output could reach the battlefield, have been unequippable since - and invisibly so, because both
are `group = armor_combat_support` and never render in the line-battalion lists the owner's QA
screenshots show. Finding 27 fixed the symptom it could see and left the same defect in place.

**Fix: six plain members, one ladder per orphaned family.** In `x_tank_chassis.txt`, all gated
`NOT = { has_dlc = "No Step Back" }` on the legacy pattern, each researchable from the sibling's
own technology, each with name, short and description localisation:

| Family | Rows | Years | Enabled by |
| --- | --- | --- | --- |
| `medium_tank_apc_chassis` | `heavy_apc_equipment_1..3` | 1985 / 1995 / 2005 | `mechanized_infantry8/9/10` |
| `medium_tank_ifv_chassis` | `heavy_ifv_equipment_1` | 2005 | `mechanized_heavy_infantry8` |
| `medium_tank_aa_chassis` | `medium_spaag_equipment_1` | 2000 | `spaag_5` |
| `heavy_tank_destroyer_chassis` | `heavy_tank_destroyer_equipment_1` | 1950 | `tank_destroyer_1` |

Stats are priced off the surviving sibling rung moved onto the heavier hull, not invented from
nothing: the Heavy APC ladder off `mechanized_equipment_8/9/10`, Heavy IFV off
`mechanized_heavy_equipment_8`, medium SPAAG off `spaag_equipment_5`, heavy TD off
`medium_tank_destroyer_equipment_5`. Carrier armour stays inside the ratified 70% same-year
medium hull cap - 42 against 60 in 1985, 45 against 65 in 1995, 49 against 70 in 2005. This is
authored balance; no live test backs the numbers.

**New contract, and it is the durable deliverable.** `validate_tank_rework()` now fails with
`role family <root> is consumed by a sub-unit but declares no plain member` whenever a family
some sub-unit names holds only derived tiers. It found the SPAAG and tank-destroyer cases
immediately, which is how they were fixed in the same pass rather than discovered three sessions
later. **Guarding consumption alone was not enough: a family can be consumed and still be
unusable.**

**Owner QA 2026-09-17: ACCEPTED.** All four carrier battalions are selectable and draw the right
family, confirmed from the division designer tooltips: Mechanized Infantry pulls
`Light Armored Personnel Carrier` x50, Heavy Mechanized Infantry `Heavy Armored Personnel
Carrier` x50, Armored Infantry `Light Infantry Fighting Vehicle` x50 and Heavy Armored Infantry
`Heavy Infantry Fighting Vehicle` x50, each with `infantry_equipment` x200. The stat ladder
lands in the intended order - defence 60.7 / 68.8 / 94.5 / 101.2 and production cost 800 / 1050
/ 1500 / 1700 across Mechanized, Heavy Mechanized, Armored and Heavy Armored - so the
sibling-plus-medium-hull pricing reads correctly in game. Heavy Tank Destroyer and Medium SPAAG
are equippable again. The heavy pair becomes available late because their plain members start
1985 and 2005; that is the authored ladder, not a defect.

**Icon and sprite mismatches on the new battalions and equipment rows are explicitly out of
scope by owner direction 2026-09-17** - Heavy Mechanized Infantry showing a heavy-tank
silhouette and the shared carrier art are accepted. This project is on functional behaviour;
do not open art work for them.

Still owed: the four battalions have no OOB references, so no scripted order of battle fields
them; art and per-country names for the heavy carriers and the six new equipment rows are ruled
out of scope. AI templates were closed the same day - see Finding 34.

## Finding 34: the deferred AI pass - templates were the whole gap, 2026-09-17

Owner direction after Finding 33's acceptance, taking the AI pass that had been deferred
"until the remaining designer content is in". It is in: no standalone armour family remains and
all twelve role families are both consumed and equippable.

**Measured first, and the deferral turned out to be half unnecessary.** `common/ai_equipment/generic_tank.txt`
is **already complete** - 135 `target_variant` blocks covering all twelve role families across
their full tier ladders, `medium_tank_apc_chassis_0..9` and `medium_tank_ifv_chassis_0..9`
included, each with its `_history` counterpart. The AI has always known how to *design* the
reworked content. The gap was entirely in `common/ai_templates/`, where nothing named the two
new battalions, so the AI would never field them.

**A live defect found by the same audit, and it predates the battalions.** The generic light
armour template gated `can_upgrade_in_field` on `has_equipment = { lt_equipment < 500 }`.
`lt_equipment` is one of the archetypes the legacy reparenting left with **zero members**, so
the trigger could never be satisfied and the AI could never upgrade a light armour division in
the field. Repointed at `light_tank_chassis`, the family `light_armor` actually draws.

**Three tech-gated variants added, not date-gated.** A date gate would have the AI adopt a
template it cannot fill; these only outrank their predecessors once the equipment exists:

| File | Variant | Composition |
| --- | --- | --- |
| `generic.txt` | `heavy_mech_armor_default` | 6 medium armour, 2 Heavy Armored, 1 Heavy Mechanized |
| `templates_stellar.txt` | `armor_medium_contemporary` ("MBT Division 00") | the 1980 variant with both carriers swapped heavy |
| `templates_stellar.txt` | `infantry_mech_contemporary` ("Mechanized Division 00") | the 1980 mech division with both carriers swapped heavy |
| `templates_USA.txt` | `usa_heavy_mech` | 3 Heavy Mechanized, 2 Heavy Armored, 5 medium armour, 3 SP artillery |

All four gate on `has_tech = mechanized_infantry8` **and** `mechanized_heavy_infantry8`, the
technologies that unlock the plain members Finding 33 authored, and both exist on either DLC
profile.

**`heavy_tank_destroyer_brigade` and `medium_sp_anti_air_brigade` were deliberately left out of
the AI templates.** Both are enabled only by `nsb_iw_armored_vehicles`, so a template naming
them would be unfillable for a non-NSB AI - the inverse of the bug just fixed. Giving them AI
usage needs a both-profiles enabler first, which is a separate decision.

**New contract: `validate_ai_templates()`.** Every `regiments`/`support` entry must name a
declared sub-unit, every `has_tech` gate must name a declared technology, and every
`has_equipment` gate must name a family with at least one equipment member. That last rule is
what the `lt_equipment` defect needed, and the class is the same silent one as Findings 31 and
33: the file parses, the division never appears. Fourteen of the sixteen `ai_templates` files are
0 bytes and only `generic.txt`, `templates_USA.txt` and `templates_stellar.txt` carry content -
worth knowing before planning per-country AI work.

Static verification only; no AI behaviour has been observed in game. What would confirm it is a
post-2005 campaign where an AI major fields a division containing Heavy Mechanized or Heavy
Armored Infantry.

## Finding 32: the baseline was red before this session touched anything

**A validator edit shipped a fixture whose premise a later content commit invalidated, and it
failed on a clean tree.** `run_tank_negative_fixtures()` asserted that FIN resolves the generic
bookmark name on `medium_tank_chassis_3`, proving a USA/SOV national preset cannot leak to
another producer. Commit `bb4e0e6df2` then added 1,410 naming presets, one of which gives FIN
a `T-54B` on exactly that chassis, so `bookmark_variant_name` correctly returned a national
name and the fixture raised `national preset leaked into another producer` with no content
defect behind it. The main validation body passed throughout; only the fixture failed.

The fixture now measures its own unmapped producer - every preset producer minus those with a
preset on that chassis - instead of hardcoding a tag, so the invariant survives the naming
manifest growing. **A hardcoded tag inside a negative fixture is a latent baseline failure
whenever the content it asserts absence from is still being authored.**

## Finding 28: the entity alias remap - IMPLEMENTED 2026-09-13

**85% of the armour entity aliases named sub-units that no longer exist, and nothing detected
it** - a missing entity alias produces no log line at all, the unit just renders a default mesh.
The file is `gfx/entities/zz_CWIC_armor_entity_aliases.asset`; the engine looks up
`<TAG>_<sub_unit>_<visual_level>_entity`, so the sub-unit token is the whole contract.

### The remap

Six tokens renamed onto the surviving battalion that consumes the same role family, one deleted,
three untouched. **Two of the eight deleted brigades kept their aliases because Finding 27
restored those brigades** - getting that wrong would have destroyed 470 working aliases.

| Token | Aliases | Disposition |
| --- | ---: | --- |
| `medium_sp_artillery_brigade` | 390 | -> `sp_artillery` |
| `medium_tank_destroyer_brigade` | 388 | -> `tank_destroyer` |
| `light_tank_destroyer_brigade` | 200 | -> `atgm_carrier` |
| `light_sp_artillery_brigade` | 200 | -> `light_sp_artillery` |
| `light_sp_anti_air_brigade` | 200 | -> `spaag` |
| `heavy_sp_artillery_brigade` | 80 | -> `heavy_sp_artillery` |
| `heavy_sp_anti_air_brigade` | 80 | **deleted** - retired with heavy AA, no consumer exists |
| `medium_sp_anti_air_brigade` | 390 | kept - brigade restored 2026-09-13 |
| `heavy_tank_destroyer_brigade` | 80 | kept - brigade restored 2026-09-13 |
| `light_armor` / `medium_armor` / `heavy_armor` | 179 / 84 / 78 | kept |

1,458 renamed, 80 deleted, 811 untouched. **2,349 -> 2,269 aliases**, eleven distinct tokens,
11,496 lines. `clone` values were not touched by the rename - they name the mesh, and changing
one would change the model. Verified by diffing sorted clone multisets before and after: 80
removed, zero added.

### A second defect found underneath it: 15 dangling clone targets

The clone-integrity check turned up 15 targets that no entity declares, across **AFG, IRQ, PER,
RAJ and SPR**: the unnumbered base forms `<TAG>_light_armor_entity`,
`<TAG>_medium_armor_entity`, `<TAG>_heavy_armor_entity` plus two `_0` forms. 418 clone lines
pointed at them.

**The trap that hid this, and it is worth remembering: the alias file was resolving against
itself.** A first scan found numbered siblings like `IRQ_light_armor_0_entity` and concluded the
targets were nearly valid - but those numbered entities are the alias file's **own outputs**, not
meshes. Excluding the alias file from the declared set shows these five TAGs declare **no armour
mesh entity at all**, and none of the 15 exists in the base game either.

Resolved by repointing all 418 clone lines onto the generic `light_armor_entity` /
`medium_armor_entity` / `heavy_armor_entity` from `gfx/entities/units_tanks.asset`. Generic art
makes no aesthetic claim and is strictly better than a dangling clone. If someone later decides
Afghanistan should field Soviet models, that is a content choice on top of a working baseline
rather than a repair.

### Validator

`validate_entity_alias_contract()` pins four things: every alias token is in the expected
eleven-token set; every token resolves to a sub-unit actually declared in `common/units/*.txt`;
every `clone` target is declared in some `gfx/entities/*.asset` **excluding the alias file
itself**, which is the self-reference trap above; and the file keeps its load-order-critical
`zz_` name and gains no BOM. The alias count is deliberately not pinned as a magic number - it
would fight every future country addition.

Both new checks proven to bite against a real validator run, then reverted: renaming one alias
back to `light_sp_anti_air_brigade` produces `entity alias AFG_light_sp_anti_air_brigade_0_entity
uses unexpected sub-unit token: light_sp_anti_air_brigade`, and breaking one clone produces
`entity alias AFG_light_armor_1_entity clones undeclared entity: NOPE_light_armor_entity`.
Check 1 is the one that would have caught all 2,008 dead aliases.

### Coverage still owed, deliberately out of this pass

The remap fixes aliases that pointed at nothing. It does not add coverage, and **twelve
hull-consuming sub-units still have zero aliases**: `spaag_support`, `super_heavy_armor`,
`mechanized_infantry`, `armored_infantry`, `mechanized_marine`, `mechanized_airborne`,
`engineer_mechanized`, `engineer_armored`, `recon_mechanized`, `recon_armored`,
`field_hospital_mechanized`, plus the two restored brigades' partial ladders. 40 TAGs are
covered of the mod's full roster. Closing that is authoring, not remapping - it needs a clone
source chosen per country per sub-unit, which is a content decision.

**Static verification only.** Self-test inventory unchanged; no BOM; `git diff --check` clean.
The rendered models have not been confirmed in game, and that is the one thing owner QA should
check: a division with SP artillery, SPAAG, tank destroyer and ATGM battalions should show
country-appropriate armour models rather than the default mesh.

## Finding 29: the carrier designers logged missing blueprint sprites - FIXED 2026-09-13

Owner-reported: opening a carrier designer writes errors to the live `error.log`. Confirmed from
the log rather than reasoned about - 42 lines, all `graphics.cpp:1351: Failed to create gui
object. Could not find sprite type`, six distinct sprites repeated seven times as the designer
was opened and closed:

```
GFX_TC_light_tank_apc_chassis
GFX_TM_light_tank_apc_chassis_main_armament_slot
GFX_TM_light_tank_apc_chassis_turret_type_slot
GFX_TM_light_tank_apc_chassis_suspension_type_slot
GFX_TM_light_tank_apc_chassis_armor_type_slot
GFX_TM_light_tank_apc_chassis_engine_type_slot
```

**Cause: vanilla declares the designer blueprint overlay sprites only for its own role chassis.**
`vanilla interface/tank_modules_blueprint_overlay.gfx` declares `GFX_TC_<chassis>` plus five
`GFX_TM_<chassis>_<slot>` sprites for every aa, artillery and destroyer role - which is why those
designers are silent - and the mod's four **invented** carrier roles have blueprint `.gui` files
referencing the same sprite shape with nothing declaring them. Measured: the mod declared **zero**
`GFX_T[CM]_*` sprites of its own before this pass.

Only the APC appears in the log because that is the designer the owner opened; light IFV, medium
APC and medium IFV had the identical 6-sprite hole.

**Fix:** 24 sprites declared in `interface/cwic_tank_rework_icons.gfx` - one `GFX_TC_` plus five
`GFX_TM_` per carrier family - pointing at the vanilla generic blueprint art of the hull each role
sits on: `generic_light_tank_{blueprint,armor,engine,gun,suspension,turret}.dds` for the light
roles and `generic_medium_tank_*` for the medium ones. All twelve textures verified present in the
base game. Zero new assets.

**Why three owner QA passes missed it:** the engine renders the designer window anyway. The
missing sprite is cosmetic overlay art, so the only symptom is log noise - exactly the silent
class `GOTCHAS.md` warns about, and the reason the log must be read even when the UI looks right.

`validate_carrier_blueprint_sprites()` now fails when any of the 24 is undeclared, naming the
sprite and the log line it would produce. Proven to bite by renaming one declaration, then
restored.

## The missing names and photos are two known gaps, not a new defect

The same owner capture shows six role-family rows reading `Light SP Anti-Air`, `Light SP
Artillery`, `Light Armored Per...`, `Medium SP Artillery`, `Medium Tank Dest...`, `Heavy SP
Artillery` with generic icons. Both halves are already-measured items rather than regressions,
and the NSB OOB pass will **not** fix either - worth stating plainly because that was the open
question.

**Names.** Those strings are the *chassis* localisation, which is what an equipment row displays
when no design is bound to it. The designs themselves do exist and are correctly named in script:
`USA_1949_nsb.txt:1590,1599,1608,1617,1626` request `Standard Main Battle Tank Destroyer 1942`,
`Standard Light SPG 1942`, `Standard Main Battle SPG 1942`, `Standard Heavy SPG 1942` and
`Standard Light SPAA 1942`, the generic effects create exactly those names
(`CWIC_tank_designer_effects.txt:154-173` for the SPAA block), and USA's bootstrap grants the
gating technologies before `set_oob`, in the right order and with a comment saying why
(`USA - United States.txt:51-66`). So the wiring is sound and the naming gap is the measured one:
**979 historical names have no designer design carrying them, and ten of twelve role families
have zero national presets.** A country with none displays the literal `Standard <role> <year>`.

**Photos.** Now fully explained by the resolved icon mechanism. The production icon is a
code-resolved `GFX_technology_medium` keyed on the technology that enables the equipment, with the
per-country override `GFX_<TAG>_<technology>_medium`. Designer equipment is enabled by the `nsb_*`
chassis technologies, and **202 generic `GFX_nsb_*_medium` sprites exist against zero
`GFX_<TAG>_nsb_*_medium`**. Every country therefore shows the same generic designer icon,
including USA. Closing it means authoring per-country sprites against the existing 9,965-file art
library - the art half of the conversion, and the one item still wanting a one-texture in-game
probe to confirm engine precedence between the country sprite and the generic one.

## Finding 30: the per-country designer art probe - ANSWERED 2026-09-14

One sprite is declared and it tests two questions at once, because measuring the technology map
first turned the second question into the important one.

### The ceiling, measured before the probe was written

`NSB_armor.txt` holds **23 technologies that enable armour chassis**, and **not one of them
enables a single role tier**. Measured per block, cited at the technology's opening line:
`nsb_iw_armored_vehicles` at `:22` enables 15 ids (`:26-40`, every family's tier 0);
`nsb_light_tanks0..8` at `:129,158,198,238,278,318,358,398,438` enable 6 each (light tank plus
the destroyer, artillery, AA, APC and IFV roles on that tier); `nsb_main_battle_tanks0..8` at
`:507,536,576,618,658,698,738,778,818` enable 6 each; and `nsb_heavy_tanks0..3` at
`:887,924,961,1002` enable 3 each - heavy has no AA, APC or IFV role, so three is complete rather
than short. Distribution: **zero** technologies enable one role tier, four enable 3, nineteen
enable 6 or more. 111 distinct equipment ids sit behind 23 technologies.

**So the icon key is strictly coarser than the vehicle.** Because the production icon resolves
through the enabling technology, one per-country sprite necessarily serves every role sharing that
technology - a country's tier-1 light tank, tank destroyer, SP artillery, SPAA, APC and IFV would
all show the same picture. Per-role per-country designer art is **impossible on this key**, and no
amount of art fixes it; it would need one technology per role tier, which is a tech-tree
restructure and 111 technologies where there are 23.

This is the third time this project has measured an art ceiling and found a different mechanism
than the previous one assumed. Recording the chain so it is not re-litigated: per-design art is
impossible (the designer compositor is an enumerated hull/profile contract), per-equipment-row art
is impossible (the row has no icon key of its own), and per-role art is impossible (the technology
is shared). **What IS available is per-country, per-hull-class, per-tier** - which is 23 sprites
per country.

### The probe

`interface/cwic_tank_rework_icons.gfx` declares one sprite, commented as a probe and marked for
removal:

```
spriteType = { name = "GFX_USA_nsb_light_tanks0_medium" texturefile = "gfx/interface/technologies/USA_spaag_1.dds" }
```

Deliberately unmistakable art - the M16 halftrack photograph on a tank hull - so the result cannot
be misread as a coincidence. The texture already ships; nothing was created.

**What to look at, as USA on an NSB profile:** the production tab and the equipment tab for the
**tier-1 light hull** rows. Three outcomes, each conclusive:

1. **All six tier-1 light rows show the halftrack photo.** The override works and the ceiling is
   confirmed as per-technology. Bulk work is then authorable and the granularity is settled.
2. **Only some rows change.** There is a finer key than the technology after all, and it must be
   identified before any bulk pass - this would be the best possible outcome and the least
   expected.
3. **Nothing changes.** Either the engine prefers the generic sprite, or `nsb_*` technologies do
   not participate in the override the way legacy ones do. Either way the art half is blocked and
   the 2,116-sprite plan below is void.

Control: `nsb_light_tanks1` has no country sprite, so the **tier-2** light rows must keep the
generic icon in every outcome. If tier 2 also changes, the resolution is not per-technology at all
and the diagnosis is wrong.

### Bulk cost, if outcome 1

23 armour technologies x **92 country TAGs** that already own an `interface/<TAG>_techs.gfx` file =
**2,116 sprite declarations**. There are 94 `*_techs.gfx` files; two are the non-TAG
`ArmtraderEAST`/`ArmtraderWEST` namespaces and are not countries, so 92 is the figure to plan
against.
All 23 generic `GFX_nsb_*_medium` forms exist, so every declaration
is an override of a known name rather than a new key. The art can be drawn from the shipped
library - 9,965 files in `gfx/interface/technologies/` - so the pass is mapping and declaration,
not asset creation, and the reverse map already resolves per-country art paths for the legacy
tiers those sprites would reuse.

### Probe result, owner-run 2026-09-13: OUTCOME 2 - a finer key exists and it already works

**The least expected outcome, and it makes the 2,116-declaration plan unnecessary.** Owner
capture: USA light APC and medium tank production lines show correct US photographs - an M3
half-track for `M3A1 Half-Track Mk0` and a Patton for `M46 Patton Mk0` - while the other role
families still show generic art.

**Those photos are not from the probe and not from any `nsb_*` sprite.** Traced to the exact
file: the half-track image is `gfx/interface/technologies/USA_apc_1.dds`, registered as
`GFX_USA_mechanized_infantry_medium` at `interface/USA_techs.gfx:177-179`. That is the
**legacy** `mechanized_infantry` technology, not a designer technology. Confirmed by identifying
the textures rather than by inference: `USA_apc_1.dds` is an olive-drab M3-type half-track with
US star and period infantry, matching the capture exactly, while the generic
`GFX_nsb_light_tanks1_medium` points at `lt_2.dds`, a light tank in snow - which is what the
*generic* rows in the same capture show.

**So the resolution key is the equipment's FAMILY, not the single technology that enables its own
tier.** `light_tank_apc_chassis_2` is enabled only by `nsb_light_tanks1` (`NSB_armor.txt:164`),
yet it renders the legacy mechanized technology's country icon - and the reason it can is the
convergence: the relocated legacy `mechanized_equipment_*` rows now live inside
`light_tank_apc_chassis`, so the family is reachable from the legacy `mechanized_infantry*`
technologies, which carry 16,283 per-country sprites. **The restructure accidentally wired the
existing per-country art library into the designer families.**

Measured USA sprite coverage per legacy technology chain in `interface/USA_techs.gfx`:
`mechanized_infantry` 10, `main_battle_tanks` 10, `light_tanks` 6, `sp_artillery` 5, `spaag` 5,
`tank_destroyer` 5. So artillery, SPAA and tank destroyers **do** have USA art on the same
pattern, and their relocated legacy rows landed in the role families in the same pass - yet those
lines still render generic. That asymmetry is the next thing to measure and it is the whole
remaining question: something distinguishes the carrier and base-hull families from the
artillery/AA/TD ones. Candidates worth checking in order: the `parent` chain of the relocated
rows, `visual_level`, whether the legacy tier the player actually holds differs, and whether the
icon follows the design's `can_convert_from` lineage.

**Two things NOT to do on this result.** Do not start the 2,116-sprite bulk pass - the art may
already resolve for free once the asymmetry is understood, and authoring overrides would mask the
real mechanism. And do not remove the probe sprite yet: whether
`GFX_USA_nsb_light_tanks0_medium` fires for the **tier-1** light rows is still unanswered, and
that is the one datum that separates "the designer technology key works too" from "only the
legacy family key works". The M16 quad-gun half-track photograph is the tell; nothing else in the
mod uses it on a tank hull.

### Probe 1 CONFIRMED and one earlier attribution corrected, 2026-09-13

Owner capture with the debug tooltip visible: the `Mid-WW2 Light Tank (United States of America)`
row in the designer template list shows the M16 quad-gun half-track photograph and the tooltip
reads `GFX_USA_nsb_light_tanks0_medium`. **The per-country override fires for an `nsb_*` designer
technology.** That is probe 1 answered affirmatively, and it means outcome 1 and outcome 2 are
both true on different surfaces.

**Correction to the previous entry:** the half-track in the first capture was this probe sprite,
not evidence of family inheritance in the template list. The tooltip in that capture was
positioned over the row beneath the one it described, and I read it as naming the row it covered.
The family-inheritance evidence stands on the *production line* only, where the `M3A1 Half-Track
Mk0` row shows `USA_apc_1.dds` - a dozer-bladed M3 with no quad mount, a different photograph
from the probe's.

### The artillery/AA/TD asymmetry: three candidates eliminated, one standing

Measured, and the obvious explanations are all dead:

- **Not missing art.** `interface/USA_techs.gfx` declares `GFX_USA_sp_artillery_1..5_medium`,
  `GFX_USA_light_sp_artillery_1..5`, `GFX_USA_heavy_sp_artillery_1..5`, `GFX_USA_spaag_1..5` and
  `GFX_USA_tank_destroyer_1..5` - 25 sprites across exactly the chains in question.
- **Not missing technologies.** USA's own history grants `sp_artillery_1`, `sp_artillery_2`,
  `spaag_1`, `spaag_2`, `tank_destroyer_1`, `tank_destroyer_2`, `light_sp_artillery_1` and
  `heavy_sp_artillery_1`, so the player holds the technologies whose sprites exist.
- **Not a name mismatch.** The sprite names match the technology ids exactly, the same way
  `GFX_USA_mechanized_infantry_medium` matches `mechanized_infantry`.

So the APC and artillery cases differ in something narrower. **The one candidate still standing:
which technology the engine picks when several enable members of one family.** The APC family's
legacy rows come from `mechanized_infantry*`, a 1942 chain; the artillery families' legacy rows
come from `sp_artillery_*` and friends, but those families ALSO contain designer tiers enabled by
`nsb_iw_armored_vehicles` and the `nsb_*` ladders, which have no country sprite. If the engine
resolves the lowest-tier or first-declared enabling technology, artillery would land on an
`nsb_*` key and fall back to generic while APC lands on the legacy one.

That is a rule about engine selection order, and static files cannot settle it - the same limit
the first icon investigation hit. **Probe 2 discriminates it with one sprite**, now staged beside
probe 1:

```
spriteType = { name = "GFX_USA_nsb_light_tanks1_medium" texturefile = "gfx/interface/technologies/USA_mbt_1.dds" }
```

`light_tank_apc_chassis_2` is enabled only by `nsb_light_tanks1`, yet its production line
currently renders the legacy half-track. Art is a Patton, unmistakable against both the half-track
and the generic snow tank.

- **The M3A1 line becomes a Patton** -> the production icon follows the designer technology, the
  legacy half-track was arriving by some other route, and per-country designer sprites are the
  lever for every family. The bulk plan returns, at 23 sprites per country.
- **The M3A1 line stays a half-track** -> the family's legacy technology outranks the designer
  one. Then the fix for artillery is not new art but making the artillery role families resolve
  their legacy chain the way the carriers already do, which is far cheaper than 2,116 sprites.

Either answer decides the whole art half. Do not author bulk sprites before it.

### Finding 30: probe 2 answered - the legacy chain outranks the designer technology

Owner ruling 2026-09-14: the `M3A1 Half-Track Mk0` line **stays a half-track**, which is both the
observed behaviour and the wanted one. Both probe sprites are removed from
`interface/cwic_tank_rework_icons.gfx`.

The decisive shape of this result: `light_tank_apc_chassis_2` is enabled by exactly one
technology, `nsb_light_tanks1` (measured - `enable_equipments` across all tech files yields a
single producer per tier), `GFX_USA_nsb_light_tanks1_medium` was declared pointing at a Patton,
and the line still rendered `USA_apc_1.dds`. **The production icon is therefore not keyed on the
technology that enables the equipment id.** It follows the family's legacy art. Probe 1 remains
true and is a different surface: the designer *template list* does honour
`GFX_<TAG>_<nsb technology>_medium`.

**So the bulk 2,116-sprite pass is cancelled, not deferred.** Per-country production art already
arrives through the legacy `*_techs.gfx` declarations the mod has shipped all along, because the
convergence relocated the legacy rows into the role families.

Structural symmetry was verified before concluding, and it is exact - so the artillery families
are wired the same as the working APC one:

| family | legacy tech -> row | relocated row archetype | USA sprites |
|---|---|---|---|
| APC | `mechanized_infantry`..`10` -> `mechanized_equipment_1..10` | `light_tank_apc_chassis` | 10 |
| medium artillery | `sp_artillery_1..5` -> `sp_artillery_equipment_1..5` | `medium_tank_artillery_chassis` | 5 |
| light artillery | `light_sp_artillery_1..5` -> same | `light_tank_artillery_chassis` | 5 |
| heavy artillery | `heavy_sp_artillery_1..5` -> same | `heavy_tank_artillery_chassis` | 5 |
| SPAA | `spaag_1..5` -> `spaag_equipment_1..5` | `light_tank_aa_chassis` | 5 |
| TD | `tank_destroyer_1..5` -> `medium_tank_destroyer_equipment_1..5` | `medium_tank_destroyer_chassis` | 5 |

One technology enables exactly one legacy row in every family, every relocated row names its role
archetype, and the role roots carry no `picture` of their own. Nothing structural separates
artillery from APC. Given that, **the "artillery renders generic" claim is now unsupported** and
must not be acted on: it rests on reading row labels in a designer-list capture, and the
`(Generic)` / `(United States of America)` suffixes there are preset *design template* labels,
not icon fallbacks. That is the same misreading that produced the correction above. Re-check it on
a production line before spending anything on it.

### NSB OOB residue: re-measured, and the headline item was wrong

The cited MON residue is **not residue**. `light_artillery_equipment_*` lives in
`common/units/equipment/light_artillery.txt` under archetype `light_artillery_equipment` - towed
artillery, never DLC-gated, never touched by the convergence. All 16 cited MON lines are
out of scope.

Re-measured properly, against the 68 rows that actually carry
`can_be_produced = { NOT = { has_dlc = "No Step Back" } }`, scanning every `*_nsb.txt` for
uncommented references: **2 files, 5 references, all ATGM.**

- `SOV_1980_nsb.txt:1321-1323` - `atgm_carrier_equipment_1/2/3` stockpile grants
- `NOR_1980_nsb.txt:364,369` - `atgm_carrier_equipment_0/1` stockpile grants

These award stock an NSB profile cannot build. The year-to-tier map is unambiguous
(`atgm_carrier_equipment_0/1/2/3` = 1960/1970/1980/1990; `light_tank_chassis_4/5/6/7` = the same
four years), so the rewrite to `light_tank_destroyer_chassis_4..7` is mechanical.

**Attempted and reverted.** The rewrite fires an existing contract:
`starting tank variant set differs from NSB OOB references: missing=[light_tank_destroyer_chassis_4..7]`.
An OOB may only name a tier some starting-variant preset creates, and
`CWIC_national_tank_presets.txt` contains **zero** `light_tank_destroyer_chassis` presets. The
ratified export inventory (`DECISIONS.md:1080-1087`) lists MBT, Light, Heavy, APC and IFV - **no
ATGM or TD entry**. So there is no ratified target to map these five grants onto, and inventing
ATGM loadouts and names is balance content, not a mechanical pass. Left as gated legacy grants;
this needs the same kind of owner ruling the export inventory itself got.

**Bulk pass cancelled by Finding 30, not merely deferred.** Per-country production art already
resolves through the shipped legacy `*_techs.gfx` declarations.

## Finding 35: conversion tranche 1 - the naming debt was mostly unreachable, 2026-09-17

**The 2026-09-13 conversion measurement below is superseded. Re-measured against the current
tree because three commits and this session landed after it, and the headline number was wrong
in both directions.** Every figure here was computed directly, not read out of a document - a
scout that sourced its answer from `DECISIONS.md` reported 289 and missed a family, which is
why these are the main agent's own numbers.

| Quantity | 2026-09-13 | Now |
| --- | --- | --- |
| Reverse-map rows with a historical name | 1,593 | 1,593 |
| ... linked to a preset design | not measured | 921 |
| ... unlinked (the "naming debt") | 979 | **672** |
| Preset rows across the three manifests | not measured | 1,410 naming + 14 national + 572 carrier |
| Distinct `(producer, type)` pairs | not measured | 1,889 |
| Chassis families with zero preset coverage | "ten of twelve" | **five** |

**The debt is overwhelmingly not addressable by the naming system, and that is the finding.**
All 672 rows classified by what would have to exist for the name to be deliverable:

| Class | Rows |
| --- | ---: |
| Belongs to the carrier preset pipeline, not the naming pipeline | 350 |
| Target tier has no generic bookmark block, so there is no design to rename | 277 |
| Producer already holds a different name on that generation | 38 |
| **Addable under today's contract** | **4** |
| Tier unresolvable - reverse-map row carries no year | 3 |

**Why 277 are structurally unreachable.** The naming system can only rename a design the
generic dispatcher already creates at a bookmark, and the dispatcher only creates tiers a
bookmark date can reach - the ladders stop at light tier 5 (1970) and medium tier 6 (1980). A
1990 or 2000 legacy vehicle has no starting design to carry its name, and no mechanism exists
to name a design a country builds mid-campaign. **Delivering those names needs a new
mechanism, not more preset rows.** Owner decision; nothing here assumes it.

### The five uncovered families, and what this tranche did about them

The five families with zero naming coverage were exactly the five with **no generic bookmark
block at any tier**: `light_tank_destroyer_chassis`, `medium_tank_aa_chassis`,
`heavy_tank_destroyer_chassis`, `medium_tank_apc_chassis`, `medium_tank_ifv_chassis`. The
consequence is worse than missing names: on an NSB profile these families had **no starting
design**, so `atgm_carrier`, `medium_sp_anti_air_brigade`, `heavy_tank_destroyer_brigade`,
`heavy_mechanized_infantry` and `heavy_armored_infantry` began every campaign with nothing to
build. The naming debt was a symptom of that.

**Sixteen generic starting designs authored**, recipes proposed in parallel by three subagents
and integrated by the main agent into the single dispatcher file:

| Family | Tiers | Armament story |
| --- | --- | --- |
| `light_tank_destroyer_chassis` | 0-5 | `tank_light_cannon0` to tier 4; tier 5 (1970) mounts `tank_atgm_launcher_cannon` with `gl_atgm_0p` in slot 7, per the ratified "ATGM is a loadout" rule |
| `medium_tank_aa_chassis` | 1-6 | `tank_anti_air_cannon` with `tank_aa_ammo_1` in slot 2, mirroring `light_tank_aa_chassis_1..3` |
| `heavy_tank_destroyer_chassis` | 1-4 | `tank_heavy_cannon0` in `heavy_fixed_superstructure`, mirroring `medium_tank_destroyer_chassis_1..3` |

Tier 0 is skipped for medium SPAAG and heavy TD because the era's ammunition and heavy-cannon
modules do not exist that early. All 16 are registered in `BOOKMARK_VARIANT_NAMES` and
`BOOKMARK_VARIANT_TECHS`; the created-variant set is now 47, while the inventory line's "38
generic bookmark variants" counts OOB *references*, which is why that number does not move.

**One instruction the main agent gave the subagents was wrong, and the validator caught it.**
`create_equipment_variant` carries `allow_without_tech = yes`, which covers the mounted modules
and not merely the chassis - so a starting design may legally mount an unresearched module, and
the contract requires **exactly one** chassis technology per guard (`:5332`). The extra
`has_tech = nsb_gun_launcher0` added to the light TD tier 5 guard was reverted. Do not "fix" a
single-tech guard again.

**The OOB-reference check is now split by direction.** It asserted set equality between created
variants and NSB OOB requests, which made authoring a starting design ahead of its OOB request
a failure. An OOB requesting a design nothing creates is a silent break and stays hard; a
created design nobody requests yet is legitimate and is named in `AWAITING_OOB_REQUESTS`, so a
misspelt generation still fails. Those 16 OOB requests are conversion work still owed.

### The two medium carrier families - blocked on a ratified contradiction, then RESOLVED

`medium_tank_apc_chassis` and `medium_tank_ifv_chassis` initially got **no** starting designs:
the subagent stopped rather than author non-compliant blocks, correctly. The ratified carrier
armour envelope capped a carrier at **70% of the same-year medium tank hull**, and these two
families *are* medium-hull roles, so they inherit 30/35/40/45/50/55/60 against caps of
21/24.5/28/31.5/35/38.5/42. Even the lightest role-admitted armour module plus the lightest
superstructure breached every tier - APC by 9.5 to 14, IFV by 16.5 to 21. **The rule was
unsatisfiable by construction, not merely tight**, because it was written when both carrier
families lived on the light hull.

**Owner ruled the cap light-hull-only, 2026-09-17**, so a medium-hull carrier is capped by its
own hull. The fourteen blocks were then integrated, taking this tranche to **30 new starting
designs** and giving all five previously uncovered role families a bookmark design. Two
corrections were applied to the proposal during integration: the multi-technology guards were
reduced to the single chassis technology (`allow_without_tech` covers modules), and
`engine_type_slot = tank_gasoline_engine` was changed to `Petrol_0`, since Finding 2 established
that the bare gasoline engine is the pre-WW2 parent and every starting design routes to
`Petrol_0`.

**One tension recorded rather than resolved:** the ratified generation years put Heavy APC at
1985 and Heavy IFV at 2005, but the full tier ladder 0-6 now carries starting designs, so a 1949
bookmark can seed a "Standard Heavy APC 1939". That follows from the owner's earlier ruling that
these battalions unlock with their hull at 1944/1947 rather than at their generation year - both
bookmarks need something to build. The alternative, authoring only tiers 5-6, would leave the
1949 bookmark's Heavy Mechanized battalion empty.

### Finding 36: research-time naming - the 277 unreachable names are now deliverable

**Owner approved building the mechanism, 2026-09-17.** The bookmark dispatcher can only rename
a design it creates, and it only creates tiers a bookmark date reaches, so every historical name
for a later tier was undeliverable by any preset. This is the mechanism that fixes the class,
not just the 277 rows that motivated it.

**How it works.** One scripted effect per chassis generation in the new
`common/scripted_effects/CWIC_research_armour_naming.txt`, called from that tier's own enabling
technology through `on_research_complete` in `NSB_armor.txt`. Each per-country guard requires
`has_dlc = "No Step Back"`, the country tag, and the absence of a
`cwic_named_<generation>_created` flag, then creates the named variant and sets the flag - the
same guard-then-flag ordering the bookmark naming presets use, so a reload cannot duplicate the
design.

**What shipped:** 22 generations, 386 named designs, 48 country tags, 22 `on_research_complete`
hooks across 11 technologies.

| Step | Count |
| --- | ---: |
| Reverse-map rows carrying a historical name | 1,593 |
| Dropped: the `(tag, name)` pair is already delivered by a live preset | 921 |
| In scope for research-time naming | 427 |
| Dropped: `(producer, generation)` collision, newest legacy tier wins | 35 |
| **Named designs authored** | **386** |

The 22 recipes were proposed in parallel by two subagents - 13 light-hull, 9 medium and heavy -
and every module was re-verified by the main agent against the live module definitions: all 22
recipes legal, zero undeclared module ids, zero illegal special-slot placements.

**New contract `validate_research_armour_naming()`, and it was proven to fire rather than
assumed.** It pins one helper per generation, that some technology actually calls each helper,
the recipe's module ids and special-slot categories, per-country guard count against the
manifest, the `has_dlc` and flag guards, flag-after-creation ordering, the variant fields, and
that every name still equals its live localisation string with its recorded file and line.
Negative check run: renaming Cuba's `heavy_tank_artillery_chassis_4` design to a non-historical
string produced `research naming CUB/heavy_tank_artillery_chassis_4 wrong name`, then reverted.

**Provenance is machine-checked, which is what makes the names trustworthy.** Every row carries
`legacy_name_key`, `source_path`, `source_line` and the raw `source_name`; `name` is that string
NFKD-normalised to ASCII. A 40-row independent sample was re-read from the live `.yml` files by
the main agent: zero mismatches. If a translator moves a line, the validator fails rather than
the name silently drifting.

**Two subagent corrections worth keeping.** The manifest agent's first run produced 474
candidates against my 427 because I had not stated the duplicate-name filter - a name already
delivered by a live preset must not be re-created at research time, or the country gets two
designs with one name. The light-recipe agent revised its artifact after I had already
integrated it, advancing the AA fire-control radar to `Radar_2` (1980) and `Radar_4` (2000); the
effects file and manifest were regenerated from the revised recipes rather than left stale.

**Owner playtest 2026-09-17: ACCEPTED.** Historical names appear correctly in game and the
newly covered families behave as intended, so Findings 35 and 36 are confirmed live rather than
statically. That closes the research-time mechanism: the guard-then-flag ordering, the
`on_research_complete` hooks and the provenance-checked names all work against a real campaign.
Balance of the 22 authored recipes is still unexercised - acceptance covers behaviour, not stats.

## Finding 53: armour hand-overs name the producer's real vehicle, and what the sweep found, 2026-09-24

Owner scope: sweep every focus, event and other piece of content that hands out armour, and make
the NSB reward accurate - a Soviet T-55 focus should give T-55s, not a generic hull. Finding 1's
deferred follow-up is closed by this. `DECISIONS.md` "Legacy armour hand-overs" carries the rules.

### What the sweep measured

| Surface | Sites | State before | Now |
| --- | ---: | --- | --- |
| Focus grants and licences on `CWIC Export ...` designs | 323 + 9 | worked on NSB, generic name, year-rule hull | producer's historical design |
| Event grants of DLC-gated legacy tiers, 16 files | 72 | **empty on NSB** | NSB branch added |
| Decision grants, 6 files: 360 in the four weapon-purchasing markets, 4 WGR, 1 Ethiopia | 365 | **empty on NSB** - the player paid and received nothing | NSB branch added |
| Focus legacy grants and licences with no NSB branch | 5 + 17 | empty on NSB | NSB branch added |
| `equipment_bonus` keyed on `mbt_equipment`, `lt_equipment` and 9 other legacy archetypes, 35 files | 175 | **inert on both profiles** | keyed on the designer family |
| `add_tech_bonus` on `cat_*_armor` / `cat_mechanized_equipment` | 11 | inert on NSB / on both | `armor_*` / `infantry_vehicles_apc` |
| Legacy tank technology rewards | 14 grants, 10 research bonuses, 2 option triggers | empty on NSB | NSB counterpart added |

The equipment-bonus row is the surprise. Every legacy armour archetype lost all of its members when
the rows were reparented onto designer families (`dbf084d049`, July, already on
`development-branch`), so an idea such as `lt_equipment = { build_cost_ic = -0.1 }` has applied to
nothing on either profile since then. `cat_medium_armor`, `cat_light_armor` and `cat_heavy_armor`
are carried only by legacy `armor.txt` technologies, and **no technology carries
`cat_mechanized_equipment`** - so Finding 5's `BRA_50s.txt:3601` repair to that category still
applied to nothing. On the legacy tree the `armor_*` categories cover the same technologies as the
`cat_*` ones, except that `cat_heavy_armor` also reached the two super-heavy technologies; the one
`cat_heavy_armor` bonus (`60sgeneric.txt`) loses them.

### The mechanism

`common/scripted_effects/CWIC_armour_supply_effects.txt` replaces `CWIC_tank_focus_effects.txt`:
44 helpers `cwic_supply_<legacy tier>`, 188 per-producer guards, pinned by
`data/Armour_Supply_Manifest.json`. An NSB hand-over reads:

```
CUM = { cwic_supply_mbt_equipment_3 = yes }
add_equipment_to_stockpile = { type = medium_tank_chassis_3 amount = 200 producer = CUM variant_name = "T-55" }
```

Each (producer, legacy tier) resolves once:

- **110 canonical rows.** The producer already has a national preset for that tier - bookmark,
  research-time, USA/SOV medium or carrier. The guard is that preset's block verbatim, minus
  `mark_older_equipment_obsolete`, behind the preset's own flag. If the bookmark already made the
  design it is reused; if not, it is created once and the bookmark or research hook can never make
  a second copy.
- **78 supplied rows.** No preset exists, mostly for the four manufacturer blocs' post-1980 stock.
  The name is the live localisation the non-NSB game shows for that producer's tier (`CUM` T-80U,
  `CAP` M1A1, `MAO` ZTZ96), or the generic tier name where the bloc has none (`IND` and `MAO`
  SP artillery, SPAA and ATGM carriers). The recipe is the producer's own preset on that hull,
  else the hull's first preset, and the flag is `cwic_supplied_<tier>_created`.

The hull is the one the national preset ladder uses, not Finding 1's year rule. They disagreed on
125 of the 332 existing hand-overs - for example the year rule put M4 Sherman grants on
`medium_tank_chassis_1` while every M4 Sherman preset is on `_0`. `generation_map` in the
manifest pins the ladder for supplied rows.

### Content defects fixed on the way

- `FRA_1950s.txt:5569` granted the archetype `mbt_equipment` ("Receive M47 Patton from the US"),
  which is not buildable on either profile. Now `mbt_equipment_3`, USA's M47.
- `INO_Utilize_M3_Stuart` granted `light_tank_chassis_1` with no design name and no DLC branch.
  Now the standard pair: legacy `lt_equipment_1`, NSB USA `M5 Stuart` and ENG `M3 Honey (Stuart)`.
- `GRE_heavy_weapons_tanks_arty` gated its NSB branch on `nsb_light_tanks1` while granting the M41
  from the 1950 hull; the gate is now `nsb_light_tanks2`, the counterpart of legacy `light_tanks_3`.

### Validator

`validate_focus_armour_grants()` and the `EXPORT_VARIANTS` contract are replaced by three:

- `validate_armour_grants()` scans focuses, **events and decisions** - the old contract covered
  focuses only, which is how 437 empty grants went unseen. A gated legacy tier must sit in the legacy
  branch of an NSB split. A designer hand-over must name a manifest design, sit in the NSB branch,
  and follow a supply call scoped on its producer or licensor.
- `validate_armour_supply()` pins helpers and guards to the manifest. Canonical guards must equal
  their preset; supplied names must equal live localisation at the recorded file and line; no guard
  may archive its design; every row must be handed over somewhere.
- `validate_armour_bonus_targets()` fails on an equipment bonus keyed on a retired legacy archetype,
  an armour technology-bonus category no technology carries, a research bonus on a legacy tank
  technology without its NSB counterpart, and a legacy tank-technology grant outside a DLC split.

The Equipment Match icon contract now covers the supply file. Six new negative fixtures: missing
NSB gate, a name the producer is never given, a supply call for the wrong tier, supplied-name
drift, a canonical guard diverging from its preset, and an unused row.

**The old export-name check had never run.** It read `variant_name` with `top_level_values()`,
which skips quoted strings by design, so `startswith("CWIC Export ")` never matched. The new
contract reads quoted values with `quoted_values()`.

```
before: ... 6219 stockpile grants, ... 2488 Equipment Match design icons, and 20 designer slots checked
after:  ... 6661 stockpile grants, ... 2676 Equipment Match design icons, 1579 armour hand-overs, and 20 designer slots checked
```

Every other count is unchanged. Localisation audit clean; workbook SHA unchanged. The
`--tank-balance-report --tank-module-balance-report --tank-envelope-report` run fails with the
same five module-mirror errors on a clean `HEAD` worktree (`flamethrower` row 330 and 20 module
ids missing from both CSV mirrors), so this pass did not cause them. They are open.

### Owner QA 2026-09-24: ACCEPTED

Owner tested focus, event and decision hand-overs in game and all came back correct; the finding is
resolved. Behaviour is accepted, not balance. The early-production question and the non-NSB effect
of the revived bonuses below were not called out in that test and stay open as edge cases.

### Risks recorded at implementation

Static verification only at the time. No balance is claimed.

- **Early designs on real producers.** A supplied or canonical design is created on the producer
  when the hand-over fires, without `obsolete = yes`. SOV handing over T-55s in a 1949 campaign
  therefore owns a T-55 design before it researches that hull. [INFERENCE] The engine should refuse
  production until the hull technology is researched; that has not been observed. If it does not,
  the fix is to gate the guard on the hull technology and fall back to an archived copy.
- **Stats moved.** Every old export mounted the same baseline (`tank_*_cannon0`, `Bogie_0`,
  `Armor_0_W`, pre-WW2 gasoline engine) whatever its year. Hand-overs now carry the national
  preset's recipe, so a focus T-55 is the preset T-55. [INFERENCE] Most rewards got stronger; not
  measured.
- **Revived bonuses change the non-NSB game too.** The 175 equipment bonuses were inert on both
  profiles; they now apply on both.
- **What to check in game:** complete `BUL_Soviet_T55s` and `FIN_Acquire_Soviet_T55s` on NSB
  (T-55s arrive, the FIN licence resolves); buy `WP_CUM_mbt_equipment_4` (T-62s arrive, CUM gets no
  duplicate); fire `ENG_event.24` on both profiles; check `error.log` for `create_equipment_variant`
  or `variant_name` lines.

Out of scope and unchanged: the ratified ungated legacy exceptions (`mechanized_equipment_1/2`,
`mechanized_marine_equipment_1..5`), which still produce on NSB, and the 11 reference-only focus
paths.

## Finding 52: blueprint vehicle map, the worklist for per-vehicle outlines, 2026-09-23

Owner scope: list every historical vehicle each designer blueprint has to depict, like the 1950 USA
medium outline in Finding 50, and leave room for stylized blueprint-style production icons later.
Those icons are recorded, not authored: drawing ~2,400 of them is beyond what this workflow can
produce.

`data/Blueprint_Vehicle_Map.csv` has 2,623 rows, ASCII with LF line endings. Query it; do not read it.

- **135 `generic` rows,** one per designer chassis type: light 6 roles x 10, medium 6 x 10, heavy
  3 x 5. These are the untagged fallback outlines. 70 types have no national design:
  `medium_tank_apc`, `medium_tank_ifv`, `medium_tank_aa`, `heavy_tank_destroyer`, and tiers no
  bookmark or research name reaches.
- **2,488 `national` rows,** one per `create_equipment_variant` in
  `CWIC_national_armour_naming_presets.txt` (1,434), `CWIC_national_tank_presets.txt` (601) and
  `CWIC_research_armour_naming.txt` (453). The 16 `CWIC Export` focus designs are excluded. Each
  row is joined on (producer, type, name) to its manifest for `legacy_row` and `name_source`, and
  all 2,488 join. The 14 USA/SOV medium presets record a localisation key rather than file:line.
- **Blueprint key** = `chassis_type` + `tag`: 2,380 distinct keys across 87 tags.
  `designs_on_blueprint_key` > 1 means several names share one outline, for example SOV
  `BTR-60P` and `BTR-60PB` on `light_tank_apc_chassis_4`.
- `blueprint_now_*` is the window the engine resolves today. Lookup order assumed: `<type>_<tag>`,
  `<type>`, `<root>_<tag>`, `<root>`. **The per-type step is still unconfirmed in game** (Finding 50
  QA). 168 national rows resolve to a vanilla major's outline; 2,320 resolve to the untagged root.
- `blueprint_target_*` follows the `DECISIONS.md` naming: window, GUI file, `GFX_TC_` sprite and
  `cwic/cwic_<tag>_<type>_blueprint.dds`. The only `custom_shipped` row is USA `M47 Patton`, and its
  derived texture path matches the shipped sprite exactly.
- `equipment_match_icon` and `icon_source_texture` are the current production picture and its DDS,
  resolved through mod-over-vanilla `.gfx`. This is the art to trace for either outline.
- `stylized_icon_sprite` / `_texture` are blank and `stylized_icon_status` is `not_started`
  everywhere. No naming convention has been ratified for these icons.

It is a snapshot generated from the three scripted-effects files, so a rename or a new preset makes
it stale. The validator does not read it.

Static only: no game file changed. The pre-edit baseline passed on the README pass line, unchanged.
That run happened while an owner `-debug` session (started from the launcher) was live, which the
README forbids: its fixtures rewrite `mechanized.txt` / `mechanized_heavy.txt`, so that session's
`error.log` may hold the spurious `A limit for category X already exists` lines from Finding 8. Both
files were left clean. The post-edit run was skipped for the same reason; this change touches no
file the validator reads.

## Finding 51: two Soviet prototypes replaced, and ASU-57 reclassified, 2026-09-23

Soviet dev report: `Su-100P` and `Su-152G` are prototypes, not service designs. **Neither the
design docs nor this project chose those names.** They are the tier-2 strings from the 2019
non-NSB localisation (`32c5031311`, "Equipment Descriptions/Naming Work"). The Finding 35 naming
pass copies a legacy tier's live localisation string verbatim and checks that it exists, not
that it is historically right.

Owner rulings: fix at the source localisation, for every country using the names; ASU-57 is an
airborne assault gun and moves to light SP artillery, freeing the medium tank destroyer slot for
SU-100. All three are hull tier 2 (1944), so recipes, hulls, research gates and creation flags
are unchanged.

| Legacy key (tier 2) | Before | After | Countries |
| --- | --- | --- | --- |
| `<TAG>_light_sp_artillery_equipment_2` | Su-100P | ASU-57 | ADR AFG CUM EGY IRQ MON PRC SOV SYR UKR |
| `<TAG>_medium_tank_destroyer_equipment_2` | ASU-57 | SU-100 | AFG CUM MON SOV UKR |
| `<TAG>_sp_artillery_equipment_2` | Su-152G | SU-152 | ADR AFG CUM CZE IRQ MON PRC SOV UKR |

Changed together: 48 localisation lines across 10 English files (name and `_short`),
`Tank_Naming_Preset_Manifest.json` (24 presets, `name` / `source_name` / `raw_source_name`), the 24
preset blocks, `Historical_Vehicle_Reverse_Map.json`, and the one scripted grant naming a renamed
design: `SOV_1980_nsb.txt` stockpile `medium_tank_destroyer_chassis_2` "ASU-57" -> "SU-100" (amount
1000 unchanged). The non-NSB game shows the new names too. Commented-out lines were left alone.

Pictures, repointed in the country `_techs.gfx` sprites so NSB and non-NSB agree:
`GFX_<TAG>_light_sp_artillery_2_medium` (10 tags, ADR twice) -> `SOV_tank_destroyer_2.dds`, the
ASU-57 photo; `GFX_<TAG>_tank_destroyer_2_medium` (5 tags) -> `ROM_tank_destroyer_1.dds`, the
SU-100 photo (Soviet dev confirmed). **SU-152 has no photo in the library**, so every
`sp_artillery_2` sprite still shows the Su-152G prototype (IRQ: the Egyptian T-34 SPG). This needs
art. `EGY_sp_lt_art_2.dds` (an Egyptian SU-100) is now unreferenced and kept. Sprite names are
unchanged, so the graphic database and preset icons do not move.

Heavy SP artillery tier 2 `2B1 Oka` is also a prototype and stays by owner ruling: the Soviet
Union fielded no 1950s heavy SP artillery, and the name is a deliberate placeholder in place of
a generic one. No preset uses it. Owner considers the armour name mapping complete.

Validation: `--tank-self-test` passes with the pass line unchanged (601 national presets, 2488
Equipment Match design icons), so the naming provenance contract accepts the new localisation;
`loc_audit_1.py --check` clean; BOM, line endings and ASCII unchanged in every touched file.
Static only; nothing seen in game.

## Finding 50: armour tab condensed, and the first custom blueprint art, 2026-09-23

Owner QA of Finding 49: icons accepted as satisfactory. Owner's own same-day edits, verified by
them in game and left as they made them: suspension unlock rows, four-track reparented off the
heavy hull onto `nsb_suspension1`, an invisible `placeholder` container widening both armour
tabs, and the designer's design-team button moved.

### APC/IFV columns sat 340 px from the hulls

The carriers, hulls and `nsb_iw_armored_vehicles` share one gridbox (every one fits 40 screen
px per slot at 0.572 scale from the same origin), so the gap was nine empty slots between APC
x -6 and the light tank x 6. Condensed by moving everything right of the carriers 8 slots
(560 GUI px) left and keeping every relative position:

| Element | Before | After |
| --- | --- | --- |
| Light / medium / heavy hull technologies, `nsb_iw_armored_vehicles` (23 techs) | x 6 / 8 / 10 / 12 / 14 / 16 | x -2 / 0 / 2 / 4 / 6 / 8 |
| `nsb_engines_tree`, `nsb_armor_tree` gridboxes | 1200, 2400 | 640, 1840 |
| Year columns `mid_left`, `mid`, `right` | 1020, 2480, 3820 | 460, 1920, 3260 |
| Owner's armour-tab `placeholder` | 5700 | 5140 |

APC (-6), IFV (-9) and the left year column stay put. The year column between the carriers and
the hulls should now start about 20 screen px after the APC labels (estimated from the capture). The validator's folder-x map gained -2, 0,
2 and 4. The modules tab is unchanged. **Static only**: this relies on Finding 48's measurement
that a gridbox's contents move one-for-one with its declared x; nothing was seen in game after
the change.

Open, not requested: moving four-track to the engines tree left roughly seven empty slots between
the early cold war heavy tank and the `mid` year column.

### Custom blueprint background and the 1950 USA medium hull outline

- **Background:** `GFX_cwic_tank_blueprint_background`, now set as the `equipment_preview` background in
  `tank_designer_view.gui`, which replaces vanilla's `GFX_generic_tank_blueprint_background` for
  every design.
- **Hull:** `equipment_designer_medium_tank_chassis_3_usa` in the new
  `interface/equipmentdesigner/tanks/tank_chassis_medium_tank_chassis_3_usa.gui` draws
  `GFX_TC_medium_tank_chassis_3_usa`. The window is resolved `equipment_designer_<type>[_TAG]`
  before `<archetype>[_TAG]`, the same per-type key vanilla uses for plane airframes
  (`equipment_designer_small_plane_airframe_0_eng`); **whether the tank designer honours the
  per-type key is the thing this test settles.** It only replaces USA `medium_tank_chassis_3`
  (`M47 Patton`, `nsb_main_battle_tanks2`). Every other medium generation and role keeps the
  vanilla USA outline.
- The slot `@highlight` windows are kept but empty, because there is no module overlay art. Hovering a slot shows
  nothing rather than the vanilla USA medium tank's gun.
- Textures: `gfx/interface/equipmentdesigner/tanks/cwic/`, 508x248 uncompressed BGRA DDS, no
  mips, the same header and channel masks as vanilla's blueprints. The owner's art is 508x206,
  which matches the band above the middle module row (preview y 50 to 250). It is placed
  unscaled at the top. The background's last 42 rows are filled with a mirror of the art's
  bottom rows; the hull's are transparent.
- The validator's blueprint file count is 83 -> 84.

Owner QA owed: the new background on every designer; USA 1950 medium hull (open `M47 Patton`
or a new design on it) shows the new outline aligned in the preview; USA 1942 and 1960 medium
hulls still show vanilla's; `error.log` has no `Could not find sprite type` for the two new
sprites.

## Finding 49: design pictures follow their names, and the `Mk0` suffix is gone, 2026-09-23

Owner report, SOV, verified in game against photographs: `BTR-40` (light APC hull 2) showed
`SOV_apc_2` instead of `_3`, `ASU-57` (medium TD hull 2) `SOV_tank_destroyer_1` instead of `_2`,
`2S7 Pion` (heavy SPG hull 3) `SOV_sp_hv_art_1` instead of `_3`, `ZSU-57-2` (light SPAA hull 2)
`SOV_spaag_1` instead of `_2`. Every preset name also carried a `Mk0` suffix.

**Cause: the Equipment Match was chosen by year, the names by legacy row.** Finding 47 matched
each hull to the legacy tier nearest its year; the naming manifests put each legacy row's name
on a hull by a different ladder. Wherever the two ladders are offset they disagree. Measured
against every manifest `legacy_name_key`: 1,036 of the 2,488 national designs carried art from a
different legacy row than their name, on every role except light/heavy tanks and light TD. On
SOV alone that was 17 designs, including `T-44` and `T-54` one medium row behind; on USA the same
pattern, including `M26 Pershing` on the Sherman row's art.

**Fix, in `DECISIONS.md` "Designer graphic database":**

- `build_designer_graphic_db.py`: `ROLES` now carries an explicit per-generation ladder taken
  from the national names; `HULL_YEARS` is removed. Shared `art()` picks a country's picture for
  a tier; `LEGACY_ART` maps legacy equipment ids to art tiers. Database rebuilt.
- All 2,488 blocks: `icon` is the design's own legacy row (1,036 changed), and
  `show_position = no` follows `parent_version = 0` (2,487 added, 1 was the owner's ZSU-37 test).
- `validate_design_equipment_match_icons()` now derives the icon from the manifest
  `legacy_name_key`, requires the designer pool for that type to offer it, and requires exactly
  one `show_position = no`.

All 40 SOV designs now carry the art number of their own legacy row. Changed on SOV: `T-44`,
`T-54`, `BTR-40`, `BTR-60PB`, `BTR-70`, `BTR-50PK`, `BMP-1`, `BMP-1P`, `2S7 Pion`, `ZSU-57-2`,
`ZSU-23-4 Shilka`, `Su-100P`, `2S1 Gvozdika`, `Su-152G`, `2S3M Akatsia-M`, `ASU-57`, `ASU-85`;
USA has the 17 counterparts. **This moves icons on the USA armour the owner accepted on
2026-09-22** (`M26 Pershing`, `M46 Patton`, `M3A1 Half-Track` and the role designs); they are
now the art of their own legacy row.

### Validator delta

```
before: ... 17449 designer graphic pools, 2488 Equipment Match design icons, and 20 designer slots checked
after:  ... 17548 designer graphic pools, 2488 Equipment Match design icons, and 20 designer slots checked
```

Every other count unchanged. Pools rose by 99: the new ladder, and a country tolerance now measured
from the target tier rather than the hull year, change which countries get a pool of their own.
Negative run: SOV `BTR-40` with its icon reverted to `mechanized_infantry2` and AFG `BTR-40`
without `show_position = no` failed on exactly those two messages; file restored byte-exact.
**Static verification only**; nothing was seen in game after the change.

Owner QA owed:

1. SOV and USA 1949 and 1980: every design's production and designer picture is its own vehicle;
   no name carries `Mk0`.
2. `BTR-60P` and `BTR-60PB` (both APC hull 4) show different pictures.
3. A new player design on each role hull opens on the ladder's picture.

## Finding 48: Equipment Match icons on national designs, and the armour tab layout, 2026-09-22

Owner QA of Finding 47: USA/SOV 1949 OOBs are complete, but scripted designs did not take the
Equipment Match icon the designer lists for them; the fire-support tab is fine; the armour hull
and armour gun/module tabs overlap. IFV routing was queried and is as ratified: light hull ->
`light_tank_ifv_chassis` -> Armored Infantry, medium hull -> `medium_tank_ifv_chassis` (Heavy
IFV) -> Heavy Armored Infantry, drawing `mechanized_heavy_infantryN` art.

### Icons

Cause: none of the 2,488 country-guarded `create_equipment_variant` blocks set `icon`. Vanilla
history sets it on every scripted tank design; without it the database pool is offered in the
designer but never applied. Each block in `CWIC_national_tank_presets.txt` (601),
`CWIC_national_armour_naming_presets.txt` (1,434) and `CWIC_research_armour_naming.txt` (453)
now ends with `icon = "<Equipment Match>"`: the first icon of the tag's weight-1 pool for the
exact type, else the `default` pool's (2,388 country, 100 default). The 16 tag-agnostic
`CWIC Export` designs in `CWIC_tank_focus_effects.txt` are obsolete, producer-agnostic and left
without. `USA` M3A1 resolves to `GFX_USA_mechanized_infantry2_medium` (`USA_apc_2.dds`), also a
half-track, so the 2026-09-14 half-track ruling holds.

`validate_design_equipment_match_icons()` recomputes the match from `00_tank_icons.txt` and
fails on a missing, extra or stale icon, so rebuilding the database with different art fails
until the presets follow. Negative run: the USA M4 Sherman icon swapped to
`GFX_USA_light_tanks_1_medium` failed with the Equipment Match message; file restored byte-exact.

### Tech tree layout

Measured from the owner's 2026-09-22 captures (0.572 screen px per GUI px, +-20 px): gridbox
contents do not sit at their declared origins. The effective x of slot 0 is declared + ~305 for
the first gridbox of each folder, + ~765 for the second, + ~1165-1210 for the third, regardless
of declared x or content extent. Year-label containers do sit at their declared x. So labels
and techs in different gridboxes cannot be aligned from the declared numbers; only relative moves
are predictable. This is the unexplained part of Finding 18, now quantified, not solved.

| Defect | Change |
| --- | --- |
| APC/IFV hulls 0 (1947) and 1 (1950) one row apart; pictures overlapped | `nsb_apc_hulls0`, `nsb_ifv_hulls0` start 1947 -> 1944, row `@1944` (owner ruling below) |
| Special Capabilities 0 (1945) over 1 (1950) | `nsb_special_capabilities0` start 1945 -> 1944, row `@1944` |
| Four-track cramped against the early cold war heavy tank | `nsb_suspension_multi_track` x 18 -> 20 |
| Super-heavy gun stranded at x 16 beside the ammunition group | `nsb_superheavy_guns1` x 16 -> 10, beside its parent `nsb_heavy_guns4` |
| Armour mid year column drawn over the heavy tank / four-track | `nsb_armor_small_year_mid` x 1950 -> 2480, left of the engines |
| Armour right year column drawn over the ERA column | `nsb_armor_small_year_right` x 4000 -> 3820 |
| Gun-tab mid year column crowded by the super-heavy move | `nsb_armor_modules_small_year_mid` x 1450 -> 2010, left of the AP ammunition |
| Loader year column drawn over HEAT ammunition | `nsb_armor_modules_small_year_mid_left` x 3100 -> 4240, left of the loaders |

`@1947` (`NSB_armor.txt`) and `@1945` (`NSB_armor_modules.txt`) lost their last user and are
removed. The validator's folder-x partition gained `20` for the armour folder. Both 1980
bookmark `set_technology` lists already grant all three moved technologies. `nsb_ifv_hulls0` is
still gated on `mechanized_heavy_infantry` and `nsb_apc_hulls0` on `mechanized_infantry`, so the
earlier start year only lowers the ahead-of-time penalty once those are held.

### Validator delta

```
before: ... 17449 designer graphic pools, and 20 designer slots checked
after:  ... 17449 designer graphic pools, 2488 Equipment Match design icons, and 20 designer slots checked
```

Every other count unchanged. **Static verification only.** Nothing was seen in game. Owner QA owed:

1. USA and SOV 1949: production lines and the designer show the Equipment Match picture for every
   OOB design, including role designs (SPAA, SP artillery, TD, APC, IFV).
2. Armour tab: no year column over a technology; APC/IFV first hulls on the 1944 row, clear of the
   1950 hulls; four-track clear of the heavy tank.
3. Gun/module tab: super-heavy gun beside the heavy gun at 1955; the two moved year columns sit in
   empty space left of AP ammunition and of the loaders; Special Capabilities 0 on the 1944 row.
4. If a moved label lands wrong, move it by the observed error: label x and technology x in the
   same folder shift one-for-one.

### Owner QA of the above, same day

USA armour accepted: naming, icons and designs are correct and accurate. Two new defects:

**Every module technology enabled Mechanized Infantry.** 51 technologies in
`NSB_armor_modules.txt` (50 under `nsb_tank_design`, `nsb_low_pressure_guns`) carried
`enable_subunits = { mechanized_infantry }`, a 2023 pattern copied forward into night vision and
special capabilities. The battalion's NSB enabler is `nsb_iw_armored_vehicles`, which also
enables the other three carrier battalions and the three tank battalions. All 464 history,
effect, focus and decision files that grant a module technology also grant
`nsb_iw_armored_vehicles`, so nothing loses the battalion. All 51 blocks removed; the validator
now fails on any `enable_subunits` in that file.

**The APC/IFV module technologies read as extra hulls.** `nsb_apc_hulls0..7` and
`nsb_ifv_hulls0..7` only enable superstructure and armament modules for the APC/IFV roles on the
light and medium hulls. They were named "... APC Hull" / "... IFV Hull", and their icons were
180x65 vehicle photographs (`apc_N.dds`, `ifv_N.dds`) drawn in a 72px small-item box. Now:

- Names are the superstructure each unlocks (`APC Open Troop Bay` ... `APC Modular Troop Capsule`,
  `IFV Fighting Compartment` ... `IFV Modular Fighting Capsule`); descriptions list every module
  enabled, generated from `enable_equipment_modules` and module localisation.
- Four new 64x64 icons in `gfx/interface/technologies/cwic_tank_rework/`
  (`nsb_carrier_open_bay`, `_apc_compartment`, `_ifv_compartment`, `_frontal_powerpack`), each the
  designer's own module icon for that superstructure centred on the tech-icon canvas. Each tier
  takes the icon of the superstructure it unlocks, so tiers sharing a module picture share an icon.
- Technology ids, positions and gates are unchanged, so no reference moves. They stay in their
  own two columns at the left of the armour tab rather than moving to the module tab: they descend
  from `nsb_iw_armored_vehicles`, and a cross-folder move would change gridbox ownership in a way
  Finding 48's measurements cannot predict.

Static verification only; the validator was run in its non-writing form because a game was live.

## Finding 47: designer art rebuilt from the non-NSB library, generic presets removed, 2026-09-22

Owner scope: icons were hard-limited by generation, hulls showed pictures that did not line up,
light TDs and Heavy APC/IFV had no art, APC/IFV showed light tank hulls in the designer
(`M3A1 Half-Track Mk0` -> `GFX_USA_light_tanks_3_medium`), and generic presets cluttered the
production menu. Decisions are in `DECISIONS.md` under the revised graphic database entry and
the new "No generic starting designs" entry.

### Designer art

**Root causes.** (1) Generations were mapped to art by index with a clamp, not by year: USA
`light_tank_chassis_3` (1950) showed `light_tanks_4` (1960), `medium_tank_chassis_3` (1950)
showed `main_battle_tanks_4`. (2) APC and IFV keys had models only, so the designer fell
through to the light hull family's icon - the capture above. The archetype `picture` never
reaches the designer; the 2026-09-21 claim that it did was wrong. (3) Countries without role art
had no pool at all and fell to hull art, and there was no `default` block.

**What shipped.** `00_tank_icons.txt` is now generated by
`CWIC Backup/tools/build_designer_graphic_db.py`: one `default` block plus 97 TAG blocks, 17,449
pools (was 8,890). Match by nearest legacy equipment year; country art only within 10 years,
else generic; weight-0.5 alternates pool per key; APC/IFV/Heavy APC/Heavy IFV on the mechanized
families; light TD on `tank_destroyer_1` then `atgm_carrier`. All 5,815 model entries carried
over unchanged. USA now reads, per light hull generation 0-9: `light_tanks_1 1 2 3 4 5 5 6 6 6`;
light APC: `mechanized_infantry 1 1 2 4 5 6 7 8 9 10`.

**Validator.** `validate_designer_graphic_db()` additionally requires a complete `default`
block, rejects any icon outside its role's art family, and fails if the file is stale against
the builder. Negative fixture run: `GFX_USA_light_tanks_3_medium` injected under
`light_tank_apc_chassis_2` failed with the art-family message and the staleness message; file
restored byte-exact.

### Generic presets

All 68 bookmark placeholders and all 25 fire-support research designs removed (the latter
reverses Finding 43's ruling). The carrier national helper calls sat between the generic blocks
and were briefly lost with them; the carrier dispatcher contract caught it and they are restored
- worth knowing if that file is ever cut by region again. Consumers repointed: NOR
(12 forced ATGM brigades -> new naming preset `M113F1 w/ BGM-71 TOW`; 150 generic SPAA folded into
the Duster stockpile), CHI (500 generic 1950 MBTs -> its M48A1; bootstrap tech 2 -> 3). The
envelope report now samples the naming manifest's recipes by generation, the same modules the
placeholders carried.

### Validator delta

```
before: 39 generic bookmark variants, 580 named OOB requests, 6220 stockpile grants, 8890 designer graphic pools
after:  39 bookmarked chassis types,  579 named OOB requests, 6219 stockpile grants, 17449 designer graphic pools
```

The report pass (`--tank-balance-report --tank-module-balance-report --tank-envelope-report`)
fails, but identically on an untouched HEAD worktree: the balance CSV and workbook lack 20 module
rows (`Blowout_Panels_0`, `Dozer_0`, `Night_Vision_*` ...) and row 330 names the retired
`flamethrower`. Pre-existing and out of this scope; it also means the repointed envelope sampler
has not produced a report yet.

Everything else unchanged. The pass-line label changed because there are no generic variants;
the count is the chassis types NSB OOBs request. 579/6219 are the merged NOR SPAA grant.

**Static verification only.** Nothing here was seen in game. Owner QA owed:

1. Designer, USA NSB: every role x generation shows the matching-era picture as Equipment
   Match, alternates are listed below it, and `M3A1 Half-Track` shows the half-track.
2. A country with sparse art (e.g. ALB) shows generic role art rather than a tank hull.
3. Production menu at 1949 and 1980: no `Standard ...` design anywhere.
4. NOR 1980: the twelve ATGM brigades spawn equipped with `M113F1 w/ BGM-71 TOW`; CHI 1980
   holds 500 M48A1.
5. Researching a fire-support technology on NSB unlocks modules and creates no design.
6. `error.log` diff against a pre-change baseline for new `graphic database` lines.

## Finding 46: three defects in the first graphic database pass, 2026-09-21

Owner playtest of Finding 45 returned three defects. All three are now fixed; two were my errors
of inference and one was a misunderstanding of the engine's sort order.

**1. APC and IFV showed aircraft carriers.** `carrier_hull`, `carrier_hull_light` and
`carrier_hull_super` are NAVAL families for the ship designer. I mapped APC and IFV onto them on
the strength of the family name alone, without checking a single member - `GFX_ENG_carrier_hull_0`
is a Royal Navy aircraft carrier. Worse, the icon pools overrode the mechanized production art
those families already had from `archetype_mechanized_equipment` under the 2026-09-14 ruling,
which is why the old mechanized and heavy mechanized pictures disappeared. **APC and IFV now
carry models only and no icons at all**, restoring that art. The contract fails on any
`carrier_hull` reference.

**2. The proper role icons were reachable but never the default.** Archetype keying was the
defect. For a derived type such as `light_tank_destroyer_chassis_3`, the engine treats
`light_tank_chassis` as the archetype, and per the documented sort order **an archetype pool
outranks a family-type pool** - so the plain tank hull won every time and the tank destroyer art
sat one rank below, visible in the selector but never chosen.

**3. Generation mismatch** had the same root: an archetype pool holds every tier's art in one
ordered list, so the engine picked from that list rather than matching the design's generation.

**Both are fixed by keying the exact per-generation equipment type with exactly one icon and one
model per pool.** A type key outranks the hull archetype, and a single-entry pool removes the
choice entirely. File goes 1,370 pools -> 8,890, one per country per role per generation.
Generations map by index into each family's available levels and clamp at the top, so a country
whose sprite family stops at level 4 repeats that art for tiers above it rather than going blank.

The contract now also rejects any archetype-shaped key, so this specific regression cannot
return silently.

Static verification only: self-test green at 8,890 pools, every sprite and entity name resolving.
Whether each generation's art now looks right is the owner's call.

## Finding 45: the designer had no art because we deleted it, 2026-09-21

**Root cause: all 25 files under `gfx/interface/equipmentdesigner/graphic_db/` are zero bytes.**
A mod file at the same path as a base game file REPLACES it. A zero-byte override therefore
deletes every icon, 3D model and blueprint pool the base game would supply, for tanks, planes,
ships and HQs alike. The files were created empty in `62c7d85bad` and extended in `15a6ef9c72`,
commit message "error log clean up": the trade was made deliberately, to silence "unknown
equipment type" warnings.

**The folder's own `_equipment_type_warnings.info` contained the misdiagnosis**, asserting that
"the mod's graphic database files are empty, so the base game's graphic database is used". That
is false, and it is why the defect read as safe to ignore for three months. Corrected in place,
along with the matching line in root `GOTCHAS.md`.

**This is NOT the entity alias system repaired on 2026-09-14.** That fixed
`<TAG>_<sub_unit>_<level>_entity` names for the division model selector. The graphic database is
the designer-side pool, a separate system keyed on equipment type.

### How vanilla repaints a design automatically

Per `gfx/interface/equipmentdesigner/graphic_db/_documentation.info`: root keys are `default`, a
continent, or a TAG; below them, keys are equipment types or archetypes; each holds `pool` blocks
with `limit`, `weight`, `icons` and `models`, filterable by `sub_units`, `ideologies` and
`cultures`. Resolution runs country, then continent, then generic, type before archetype.

**Switching role changes the equipment type, so the pool changes and the art follows. There is no
script hook and none is needed.** This is the mechanism the owner observed in vanilla.

### What was authored

`00_tank_icons.txt`, 455,600 bytes: 95 country blocks, 1,370 pools, 3,691 icons and 6,997 model
entries, all drawn from sprite and entity families this mod already ships. **Keyed on the role
chassis archetype, not per-tier types**, because this mod's generations are created dynamically
by the designer, so one archetype pool covers every tier.

| Role chassis | TAGs covered of 95 |
| --- | --- |
| light / medium hull | 82 |
| heavy hull | 49 |
| light / medium SPAA | 65 |
| light SP artillery | 70 |
| medium SP artillery | 73 |
| heavy SP artillery | 58 |
| light / medium / heavy tank destroyer | 70 / 69 / 65 |
| light / medium APC | 53 / 63 |
| light / medium IFV | 66 / 65 |

26 TAGs have all 15 roles. **APC and IFV have no dedicated designer art anywhere in the mod**, so
per the owner ruling they borrow the nearest family: APC from the carrier hull sprites and the
`mechanized` entities, IFV from `atgm_carrier` sprites and the armoured infantry entities.

**Coverage is deliberately uneven and pinned rather than papered over.** 19 TAGs have fewer than
five roles covered; those countries fall back to whatever the engine picks, exactly as before.

`validate_designer_graphic_db()` fails if the file is emptied again, gains a BOM, keys a chassis
this mod does not declare, or names an unregistered sprite or entity. Negative fixture run: the
file was truncated, the contract failed with the empty-override message, and the file was
restored byte-exact.

### The APC/IFV role switch is mostly correct already

Role permission is `allow_equipment_type` / `forbid_equipment_type` on modules. All 34 APC and
IFV modules already carry the allow side and the loc keys are already overridden. The friction is
structural: APC is typed `flame` and IFV `rocket`, and every tank gun carries
`forbid_equipment_type = { flame rocket }`, so a gun-armed tank cannot switch until the gun comes
off. **That is identical to vanilla's tank destroyer behaviour and is not a defect.** Whether the
residual "refresh and rename" friction the owner reported disappears now that the art resolves is
an in-game question, unproven here.

Static verification only. Nothing about icon choice or visual quality is claimed.

## Finding 44: fire-support coverage completed, and an indentation defect worth naming

**All 25 in-scope fire-support technologies now grant modules AND a design.** The eight
generations left without a design in Finding 43 were authored by mirroring the nearest sibling
tier that had a recipe - `light_tank_aa_chassis_0` from `_1`, `_5` from `_3`,
`light_tank_artillery_chassis_5` from `_4`, `medium_tank_artillery_chassis_0` from `_1`, `_5`
from `_3`, `medium_tank_aa_chassis_8` from `_6`, `heavy_tank_artillery_chassis_2` from `_1`,
and `heavy_tank_destroyer_chassis_3` from `_2`. Each helper records the sibling it mirrors.
Helpers go 16 -> 24 and technology calls 19 -> 27.

**The defect that surfaced while doing it: 10 of the 68 generic blocks sat one tab shallower
than the rest of the dispatcher.** The medium SPAAG and heavy tank destroyer blocks integrated
on 2026-09-17 came in at two tabs where every sibling uses three. The engine does not care -
but the main agent's own parser silently skipped all ten, which is why those two families
looked recipe-less when they were not. Normalised to three tabs; the dispatcher is now
uniform at 68 blocks.

**Whitespace inconsistency in a generated file is not cosmetic when tooling parses that file.**
Both this session's parsers and the validator's block readers key on indentation depth.

### The pacing divergence, measured

Research date against vehicle year across all 25 in-scope technologies: **17 align exactly**,
and the 8 that do not split into two unrelated shapes.

| Shape | Technologies | Gap |
| --- | --- | --- |
| Systematic: the whole medium SP artillery branch researches five years AFTER its vehicle | `sp_artillery_1..5` | -5 at every tier |
| Ragged: no consistent offset | `tank_destroyer_1` +10, `_2` +5, `_3`/`_4` 0, `_5` -5 | drift |

The first looks deliberate - a uniform branch-wide offset. The second does not: `tank_destroyer_1`
becomes researchable in 1940 and unlocks a 1950 vehicle. **Neither is changed here**; the
mapping used the vehicle year per the ratified rule, so the designs are correct either way, and
moving research dates is a pacing decision for the owner.

Static verification only: self-test passes, inventory line unchanged.

## Finding 43: the fire-support tree converged onto the designer hulls, 2026-09-17

**Owner ruling: a fire-support technology must unlock the era's modules AND leave the player a
design.** On NSB the branch researched into nothing visible, because its legacy vehicle is
unbuildable there and the designer counterpart is built by hand.

**Scope, derived independently by the main agent and matched exactly by the subagent survey:**
25 of the 85 technologies in `artillery.txt` are in scope - the SPAA, SP artillery and
tank-destroyer tiers. The other 60 are towed artillery, infantry anti-tank, missiles or naval
and are deliberately untouched. `rocket.txt` holds no fire-support vehicles at all.

**Mapping uses the legacy equipment row's year, not the technology's `start_year`** - the
ratified not-later-than rule, applied to the vehicle rather than to the research date. The two
diverge in places: `tank_destroyer_1` starts 1940 but enables a 1950 vehicle. That is a pacing
oddity, recorded and not silently corrected.

**What each technology now does:**

| Half | Coverage |
| --- | --- |
| `enable_equipment_modules` | all **25**, granting the era's main armament plus the ammunition its gun needs - AA ammunition for SPAA, HE for artillery, kinetic and HE for tank destroyers |
| research-time design | **19 technologies** calling **16 helpers** in the new `CWIC_firesupport_designs.txt` |

**The helpers reuse the bookmark flag `cwic_starting_<generation>_created` deliberately.** A
country that already received that design at a bookmark start never receives a duplicate; the
helper only fires for a country researching into a generation it did not start with. Recipes
are copied from the generic bookmark block where one exists and otherwise from the
research-naming recipe authored earlier the same day - which is what made 12 of the 16 possible.

**Eight generations get modules but no design, and the reason is that nothing describes them
yet:** `light_tank_aa_chassis_0` and `_5`, `light_tank_artillery_chassis_5`,
`medium_tank_artillery_chassis_0` and `_5`, `medium_tank_aa_chassis_8`,
`heavy_tank_artillery_chassis_2`, `heavy_tank_destroyer_chassis_3`. None has a bookmark block or
a research-naming recipe, so authoring one is a balance decision rather than a cutover. The
module grant still makes those technologies meaningful on NSB.

**Two subagents disagreed on tier numbering** - one used hull-technology shorthand, the other
actual chassis ids - so the mapping used here is the main agent's own, computed from live
equipment years against the ratified ladders, with the artifacts used only as input. The module
grants were verified against `00_tank_modules.txt`: 25 technologies, zero undeclared ids.

Static verification only: self-test passes, inventory line unchanged.

### Marine chain, closed 2026-09-17

Owner reversed the 2026-09-12 both-folders ruling. Marines consume `light_tank_apc_chassis`, so
on NSB their transport is designer-supplied and the legacy chain was redundant duplicate
content. `amphibious1..5` leave `nsb_armor_folder`, and the validator contract now pins the
opposite direction: the chain must stay in the legacy folder and must NOT appear in the designer
folder. **The NSB armour tab is now purely designer content.**

## Finding 41: polish pass 1 - the NSB tree cleanup and a real error-log defect

Owner playtest 2026-09-17 compared the two profiles side by side. Non-NSB is clean; NSB still
showed legacy vehicle technologies beside the designer hulls, and the error counter read 2952
against 2484.

**The duplicate tech cards were a folder problem, not a gating problem.** No technology in
`armor.txt`, `artillery.txt`, `rocket.txt` or `NSB_armor.txt` uses `allow`, `allow_branch` or
`has_dlc` at all. The legacy APC and IFV chains simply declared **both** `armour_folder` and
`nsb_armor_folder`, so they rendered in the designer tab. Eighteen technologies -
`mechanized_infantry` and `mechanized_infantry2..10`, `mechanized_heavy_infantry` and
`mechanized_heavy_infantry2..8` - lost their `nsb_armor_folder` block. They remain fully
researchable on non-NSB, where they are the only armour.

**Re-homing had to come first, and this is the trap.** `mechanized_infantry` and
`mechanized_heavy_infantry` are what `enable_subunits` the four carrier battalions. Hiding them
on NSB would have removed Mechanized, Heavy Mechanized, Armored and Heavy Armored Infantry from
every NSB campaign. All four are now also enabled by `nsb_iw_armored_vehicles`: deliberate dual
enablement, one enabler per profile, whichever completes first.

**The marine chain stays in both folders, because a ratified contract says so.**
`amphibious1..5` were stripped with the rest and the validator failed with
`amphibious<N> is not exposed in both armor folder configurations` (`:5594-5599`). That check
exists so marine transport can be researched on either profile. The removal was reverted rather
than the contract overridden - so the `LVT-4`, `LVTP-5` and `LVTP-7` cards the owner saw in the
NSB tab are still there, by prior ruling. Closing that needs an owner decision, not a cutover.

### Finding 42: 36 equipment ids were missing from the bonus-type enum

**A real defect of ours, found by measuring the error log rather than assuming it was noise.**
The live `error.log` is the owner's NSB session - 2,952 parsed records, matching the counter
exactly. Normalising the messages surfaced 36 instances of
`equipment_database.cpp:656: <id> is an equipment type or equipment category but is not in
script enum script_enum_equipment_bonus_type`.

Six are the plain members authored 2026-09-17 - `heavy_apc_equipment_1..3`,
`heavy_ifv_equipment_1`, `medium_spaag_equipment_1`, `heavy_tank_destroyer_equipment_1` - so
this pass introduced them and `DECISIONS.md` Gate B had already stated the rule. The other 30
predate the session: the relocated legacy `spaag_equipment_*`, `sp_artillery_equipment_*`,
`light_sp_artillery_equipment_*`, `atgm_carrier_equipment_*` and `medium_tank_destroyer_equipment_*`
rows have never been enumerated. All 36 are now declared in `script_enums.txt`.

The rest of the 2,952 is the already-triaged graphics noise: 168 records name our ids and every
one is the base game's `equipment_graphic_database` complaining about vanilla role chassis this
mod removed, or per-country entities for `light_armor` / `heavy_armor` that were never authored.
No record names a battalion, a designer chassis family or a scripted effect of ours.

Static verification only: self-test passes, inventory line unchanged.

## Finding 40: the carrier source inventory widened - and the near-miss that mattered

**Owner rulings 2026-09-17 closed the last naming gap, and the item was smaller and stranger
than it looked.** The "12 blocked carrier rows" re-measured to 14, which split three ways:

- **Six were a measurement artifact.** The carrier manifest carries a ratified source-tag alias
  `MBZ -> MZB`: `MBZ_*` is the localisation prefix, `MZB` the declared country tag. Five of
  those names were already live under `MZB` and only looked missing because the comparison used
  the loc prefix. The sixth, `BMP-1P`, collides with MZB's existing `BMP-1` on the same
  generation and is closed by design like the other 203.
- **Four were marine equipment.** `carrier_source_inventory()` matched only
  `mechanized(_heavy)_equipment`, so the marine family never entered the pipeline even though
  the 2026-09-12 cutover had relocated it into `light_tank_apc_chassis`.
- **Four were below the window.** The inventory mapped `apc tier = level - 3`, so legacy levels
  1 and 2 produced negative tiers and were silently discarded.

**All three are fixed.** Marine equipment joins the inventory on a year-derived table -
`MARINE_LEVEL_TIERS = {1: 0, 2: 1, 3: 3, 4: 5, 5: 7}`, because its 1944/1950/1965/1985/2005
ladder is not evenly spaced - levels 1 and 2 clamp onto tier 0 instead of being dropped, and
the tag alias now lives in one constant, `CARRIER_SOURCE_TAG_ALIASES`, used by both the
inventory and the manifest pin so the same misreading cannot recur.

Coverage moves from **572 to 587 source-derived pairs**, adding 15 national carrier designs
across ARG, AUS, CHI, IND, INS, JOR, LEB, MAO, PAK, SIA, SPR (two), SWI, VEN and WGR. The
pinned count moves with it, so a silent coverage change still fails.

### The near-miss, and it is the part worth remembering

**Widening the inventory silently renamed 70 existing designs and downgraded 45 of them.** The
selection rule that decides which source names a pair sorted only by file precedence, so once
older legacy levels joined a pair, the OLDEST vehicle won: `CUM`'s 1947 `BTR-40` became a 1942
`ZiS-42` truck, and `CAP`'s `M3A1 Half-Track` became an `M2 Half-Track`, across 45 live OOB
requests. Nothing about that is a naming improvement - it is a content regression, and it
surfaced only because the OOB contract failed loudly on names its producers no longer created.

The fix is a better rule, not an accepted loss: **the newest legacy level names the generation**,
with file precedence as the tie-break. That is the same newest-wins rule already ratified for
collisions elsewhere. Verified before adopting it: the new rule reproduces **every one of the
572 pre-existing names exactly, zero differences against HEAD**, while still admitting the 15
new pairs. The manifest diff adds rows and provenance and renames nothing.

**A widening that changes a selection input can rewrite existing content.** Check the delta
against HEAD before adopting one, not just whether the validator passes.

Static verification only: self-test passes, national presets 586 -> 601, everything else on the
inventory line unchanged.

## Finding 39: the unfielded battalions reach scripted history, 2026-09-17

**The NSB-only enabler that blocked two of them is gone.** `heavy_tank_destroyer_brigade` and
`medium_sp_anti_air_brigade` were enabled only by `nsb_iw_armored_vehicles`, which made them
unusable on a non-NSB profile and is why Finding 34 kept them out of the AI templates. They now
sit in the same `enable_subunits` blocks as their surviving siblings - `tank_destroyer_1` and
`spaag_1` in `artillery.txt`, both present on either profile - and the NSB-root entries are
removed so each has one enabler. This closes suggested-order item 14.

**Two of the four are now fielded in scripted history, on historical grounds rather than to
satisfy a counter:**

| Battalion | Where | Basis |
| --- | --- | --- |
| `medium_sp_anti_air_brigade` | WGR `Panzer-Division`, 1980 both profiles | the Gepard, standard divisional SPAAG of the 1980 Bundeswehr |
| `heavy_tank_destroyer_brigade` | SOV `Gvardeyskaya Tankovaya Diviziya`, 1949 both profiles | the ISU-152, still the Guards tank division's heavy tank destroyer |

Each occupies a free grid slot in an existing template rather than displacing a battalion, and
each was applied to the `_nsb` and non-NSB files together, because the mod deliberately keeps
the two profiles' division templates identical.

**Heavy Mechanized and Heavy Armored Infantry are deliberately NOT fielded, and this is the
honest answer rather than a gap.** Their ratified generation years are 1985 and 2005; both
bookmarks are 1949 and 1980. There is no 1980 formation that historically carried a heavy APC -
the IDF's Nagmashot arrives 1983 and Achzarit later still - so putting one into a 1980 order of
battle would be inventing history to make a number move. They remain player-designable,
equippable on both profiles and AI-buildable from the tech-gated templates, which is the
correct state for a capability that postdates every bookmark.

**The AI now fields both restored brigades.** `armor_medium_contemporary` and
`infantry_mech_contemporary` in `templates_stellar.txt` gain one each, which was only safe once
the both-profiles enabler landed - under the old NSB-only enabler this would have handed a
non-NSB AI an unfillable division.

Static verification only: self-test passes, inventory line unchanged from the OOB pass at 39
generic bookmark variants and 580 named OOB requests.

## Finding 38: the OOB requests - only one family could receive them, 2026-09-17

**The "30 OOB requests" item was priced against designs, not against divisions, and that was
the error.** A `force_equipment_variants` request only does anything in an order of battle
whose divisions field the battalion that draws the family. Measured across every OOB, NSB and
non-NSB:

| Battalion | Family | OOBs fielding it |
| --- | --- | ---: |
| `atgm_carrier` | `light_tank_destroyer_chassis` | 9 total, 3 NSB |
| `medium_sp_anti_air_brigade` | `medium_tank_aa_chassis` | **0** |
| `heavy_tank_destroyer_brigade` | `heavy_tank_destroyer_chassis` | **0** |
| `heavy_mechanized_infantry` | `medium_tank_apc_chassis` | **0** |
| `heavy_armored_infantry` | `medium_tank_ifv_chassis` | **0** |

Four of the five battalions appear in no order of battle at all, so 24 of the 30 requests
cannot be written without first putting those battalions into historical divisions - content
and balance authoring per formation, not conversion. That is an owner decision and is recorded
as owed rather than guessed at.

**What was authored: 20 requests across two countries.** NOR and RAJ field `atgm_carrier` in
twelve and eight division instances respectively, and each now requests
`light_tank_destroyer_chassis_5` by name - RAJ its historical `Landrover w/ MILAN`, NOR the
generic `Standard Light Tank Destroyer 1970`, resolved through the ratified producer rule.
SOV was excluded on evidence: it declares two ATGM templates and **instantiates neither**, so
it has no division to carry a request.

**A second contract fired and was satisfied, not worked around.** Adding RAJ's request failed
`RAJ - British Raj.txt does not bootstrap the required chassis technologies and starting
variants immediately before set_oob`, because a country requesting a variant must research its
chassis before the OOB loads. `nsb_light_tanks4` was added to RAJ's bootstrap in sorted
position. NOR needed no change - it already carried the technology.

Inventory line moves for the first time this session: **38 -> 39 generic bookmark variants**
and **560 -> 580 named OOB requests**. `AWAITING_OOB_REQUESTS` drops
`light_tank_destroyer_chassis_5` and now carries the per-family reason each remaining entry
cannot be requested, so the set documents a measurement rather than a backlog.

## Finding 37: conversion tranche 2 - the naming surface is closed, 2026-09-17

**A null-year data gap was hiding 67 deliverable names, and finding it changed the shape of the
tranche.** Six reverse-map tiers carried `"year": null`, so nothing could map them to a designer
generation and every historical name under them was invisible to all three pipelines. Cause:
the 2026-09-13 generator missed `mechanized_heavy_equipment_4..8` because those rows declare
`<id>\t= {` with a **tab before the equals sign**, and missed `lt_equipment_1` because it lives
in `tank_light.txt` rather than `x_tank_chassis.txt` and declares no `year` at all - its 1942
comes from its technology `light_tanks_1`. Six values repaired in place; the diff is exactly six
lines, the file was not reformatted.

**The remaining debt, fully classified.** After the year fix, every reverse-map row carrying a
historical name falls into exactly one bucket:

| Bucket | Rows | Disposition |
| --- | ---: | --- |
| Already delivered by a live preset | 1,282 | done |
| Added to the research mechanism this pass | 67 | **shipped** |
| Added to the bookmark naming pipeline this pass | 23 | **shipped** |
| The country already has a named design on that generation | 203 | closed by design |
| Carrier generations, blocked by the legacy-flag contract | 12 | recorded below |

**The 203 are not owed.** They are cases where one country's several legacy vehicles map to a
single designer tier - the country already receives a historical name there, just not every one
of them. Delivering the rest would need more than one design per producer per generation, which
both naming contracts prohibit by unique `(producer, generation)`.

**Twelve carrier rows are blocked, and the reason is structural.** `light_tank_apc_chassis_2/3/4`
and `light_tank_ifv_chassis_2/4` cannot join the tank naming pipeline: their generic blocks
still set the **legacy** flag `cwic_starting_apc_chassis_N_created`, per the 2026-09-11 ruling
that a carrier generation is a bookmark index while `type` names the migrated role chassis. The
naming contract derives its flag from the generation, so the strings do not meet. They cannot
join the carrier pipeline either: `validate_carrier_bookmarks` pins the preset set to exactly
the 572 pairs derived from live localisation by `carrier_source_inventory()`, and these rows sit
outside its tier window - the inventory maps legacy level to tier with `apc = level - 3`, so
`mechanized_equipment_1` and `_2` produce negative tiers and are dropped. Closing them means
changing one of those two contracts, which is an owner decision, not a cutover.

**What shipped.** Research-time naming grew from 386 to **453** designs over 25 generations:
three new helpers for `light_tank_ifv_chassis_6/7/8`, whose recipes mirror the APC siblings of
the same tier with IFV-admitted armament and superstructure (`ifv_autocannon_4/5/6`,
`ifv_rear_ramp_compartment` / `ifv_spall_lined_compartment` / `ifv_modular_fighting_capsule`)
plus a missile in slot 7, wired into `nsb_light_tanks5/6/7`. The bookmark naming pipeline grew
by 23 rows over five generations, with two new recipes copied verbatim from the generic blocks
they shadow, as that contract requires.

**One self-inflicted incident, recorded because the recovery is the lesson.** A `git checkout`
used to undo an experiment reverted `CWIC_tank_designer_effects.txt` to HEAD and silently
destroyed the 30 uncommitted starting designs from Finding 35. They were rebuilt from the
subagent artifacts under `local://` with the same normalisations, and the validator confirmed
the restoration by failing on exactly the two missing helper calls and nothing else. **Do not
`git checkout` a file in this tree while the session's work is uncommitted** - much of it has
never been committed and the artifacts are the only other copy.

Static verification only: self-test passes, inventory line unchanged, `git diff --check` clean,
zero non-ASCII added, no BOM on any edited script or manifest.

### The MON "OOB residue" was miscategorised, and there is nothing to migrate

The 16 `force_equipment_variants` sites in `MON_1949_nsb.txt` and `MON_1980_nsb.txt` request
`light_artillery_equipment_1`/`_3`, which is **towed infantry artillery** - not one of the
fifteen designer chassis families, and with no `archetype` pointing at any role family. Its
consumer `light_artillery_support` (`CWIC-Support-Units.txt:1043,1078`) legitimately draws it.
The 2026-09-13 note filed these as NSB residue by pattern-matching the `_equipment_N` suffix.
All 16 left unchanged; `history/units/` verified byte-identical to HEAD.

Static verification only: self-test passes, inventory line unchanged. No bookmark has been
started, so none of the 16 new designs has been seen in a production tab.

## Conversion surface, measured 2026-09-13 - SUPERSEDED by Finding 35, 2026-09-17

The mass non-NSB-to-NSB conversion splits into four surfaces with very different readiness.

**Naming - 979 rows owed, and the fallback is not broken, just generic.** National presets cover
only three families: `light_tank_apc_chassis` (373), `light_tank_ifv_chassis` (199) and
`medium_tank_chassis` (14, the USA/SOV mediums). **Ten of the twelve role families have zero
national presets.** Cross-referencing the reverse map: of 1,593 country rows carrying a historical
name, **979 have no designer design carrying that name**. Heaviest by family: `mbt_equipment` 301,
`lt_equipment` 205, `sp_artillery_equipment` 93, `light_sp_artillery_equipment` 87,
`spaag_equipment` 85, `medium_tank_destroyer_equipment` 58, `atgm_carrier_equipment` 51,
`heavy_sp_artillery_equipment` 50, `ht_equipment` 28. Heaviest by TAG: MON 51, UKR 50, KOR 41,
ITA 40, EGY 36, NLF 36, AFG 35, SAF 34, SWE 33, RAJ 32. Countries without a preset display the
literal generic `Standard <role> <year>` (`CWIC_tank_designer_effects.txt:159-162,228-230,493-500,667-669,744-746,886-888`),
so nothing is missing - it is unhistorical, which is the whole point of the item.

**Entities - 2,008 of 2,349 aliases are now dead, and no surviving battalion has coverage.** The
alias file keys on `<TAG>_<sub_unit>_<visual_level>_entity`, and its sub-unit tokens are the
**eight deleted brigades** (1,928 aliases) plus `heavy_sp_anti_air_brigade` (80, a token retired
with heavy AA) plus `light_armor` 179, `medium_armor` 84, `heavy_armor` 78. So 85% of the file
now names sub-units that do not exist, and the seven surviving battalions plus the twelve carrier
and support sub-units have **zero** aliases. 40 TAGs are covered. This is the most mechanical
remaining work: remap the dead tokens onto the surviving consumers rather than authoring anything.

**NSB OOB residue - 41 files, mostly unpaired.** 41 `_nsb` OOB files field a surviving battalion;
only ENG_1949 and SOV_1949 clearly request the matching role variant, and designer stockpile
grants appear in just ENG, HOL, NOR, SOV and USA. Direct `force_equipment_variants` residue is
concentrated in MON_1949_nsb (`:56,66,76,86,96,106,116,125,134,144,155,168`) and MON_1980_nsb
(`:59,72,85,98`), all legacy `light_artillery_equipment_*`. Disposition, and it matters: a gated
legacy id is still a **declared** id, so the grant resolves and awards stock the profile cannot
build - it is not the silent-drop shape of an undeclared token (`DECISIONS.md:1107-1118`).

**2D art - the icon mechanism is now RESOLVED, and it changes the ceiling.** The production tab
binds `spriteType = "GFX_technology_medium"` (`interface/countryproductionlineview.gui:1565-1570`,
vanilla `:1564-1569`) - a code-resolved key, not an equipment-id literal. The engine resolves it
through the **technology that enables the equipment**, and a country overrides it by declaring
`GFX_<TAG>_<technology>_medium`. Vanilla proves the pattern with
`GFX_JAP_motorized_equipment_1_medium` beside the generic form (vanilla
`Technologies.gfx:158-165`), on a row that declares no `picture` of its own.

**So per-country art for designer equipment is possible, and it is keyed on the NSB chassis
technology, not on the design.** Per-design art remains impossible - confirming the earlier
ruling for a different reason than the one recorded. Measured gap: **202 generic `GFX_nsb_*_medium`
sprites exist and zero `GFX_<TAG>_nsb_*_medium` sprites exist**, so every country currently shows
the same generic designer icon. Engine precedence between a country sprite and the generic one is
the only part static evidence cannot settle; the probe is one texture, one country, one look at
the production line.


### Validator contract

`validate_legacy_armour_dlc_gates()` pins the 37 gated ids and the 7 exceptions by name. It
fails when a gated row loses its gate, when an exception gains one, when any row carries **two**
`can_be_produced` blocks - the engine keeps the last and silently drops the first - and when an
archetype root gates production by DLC. That last check is on a DLC predicate specifically, not
on the presence of `can_be_produced`, because the three designer hulls carry a deliberately empty
`can_be_produced = { }` at `tank_chassis.txt:7`. The first draft flagged those three as failures;
that was the check being wrong, not the content.

The excluded artillery families carry a comment at the map's end naming the technologies and the
template exposure, so the next reader does not re-derive the revert.

Proven to bite: deleting `ht_equipment_1`'s gate produces
`legacy armour row tank_heavy.txt:ht_equipment_1 must declare can_be_produced`, then restored.

**Verification: static only.** Self-test inventory line unchanged from baseline. No BOM on any
edited file. The NSB bookmark start has a buildable carrier because the presets create the
starting designs - but **that has not been confirmed in game**, and it is the one thing owner QA
should check first: start an NSB bookmark and confirm the production tab offers designer armour
and no legacy duplicates, and that a non-NSB start still offers the legacy rows.

### Finding 25: `flame` is free, and that reopens amphibious as a real designer role - 2026-09-13

Owner challenge 2026-09-13, and it is correct. **The flame blacklist rested on an observation
that Finding 24 already disproved**, and nothing in this folder had propagated the correction.
`DECISIONS.md` is corrected in place.

The chain: IFV moved to `flame` on 2026-09-10, "both carrier roles failed", so flame was
recorded as the token that breaks a working role. Finding 24 then established that **neither
role was ever broken** - the only symptom was the benign `equipmentdesignerview.cpp:3657`
no-op line - and it names the flame remap explicitly as one of "two wrong turns ... both
attempts to fix a defect that did not exist". So there is no evidence against flame at all.
Structurally it is in the safer group: vanilla declares `light_tank_flame_chassis`,
`medium_tank_flame_chassis` and `heavy_tank_flame_chassis` (`x_tank_chassis.txt:47,92,137`),
which is the exact property the `rocket` diagnosis used as its discriminator - and `rocket`
works anyway.

**Token ledger, corrected.** Six usable: `anti_air`, `anti_tank`, `artillery`, `amphibious`,
`rocket`, `flame`. Five spent: AA, TD, artillery, APC (`amphibious`), IFV (`rocket`). One free:
`flame`.

### The proposed reshuffle, and vanilla already ships its exact shape

Move APC from `amphibious` to `flame`; leave IFV on `rocket`; spend the freed `amphibious`
token on a dedicated amphibious mechanized role. One role migrates, not two.

**This is not a novel design - it is what vanilla does.** Vanilla's amphibious role roots are
`light_tank_amphibious_chassis` and `medium_tank_amphibious_chassis` (`x_tank_chassis.txt:38,83`),
and its sub-units `amphibious_light_armor` / `amphibious_medium_armor`
(`amphibious_armor.txt:71,139`) consume them by name with `light_tank_amphibious_chassis = 50`
in `need`. The amphibious combat bonus is a **sub-unit** block - `amphibious = { attack = 0.6 }`
alongside `river` and `marsh` at `amphibious_armor.txt:60-68` - not a property of the equipment
`type`, so it is granted by the battalion this mod authors, not inherited from the token.

That last point cuts both ways and is worth stating plainly: there is **no measured evidence
that today's APC-on-`amphibious` arrangement grants any unintended amphibious modifier**, since
the modifier lives on the sub-unit. The argument for the reshuffle is taxonomic, and the owner's
framing is the right one - it stops "every APC is amphibious" from being the mod's position,
without keeping legacy content and without a broad unrealistic category.

**It looked like it closed the amphibious batch on its own terms - and the owner has since ruled
that batch out entirely. See the ruling at the end of this finding before acting on anything in
this subsection.** The reasoning preserved here is only why the reshuffle was worth doing at the
time: Finding 15 priced three options and the owner took option 3, APC-wide marine transport,
because a dedicated role needed a token and the token set was believed spent. It was not spent.

### Cost, measured against the last swap of the same shape

The `rocket` -> `flame` IFV swap is the precedent and it was measured: 2 role roots, 65 module
restriction lines, 4 localisation keys, validator expectations. The APC swap is the same scope,
because every carrier reference already sits on a token boundary and **no chassis id changes** -
so presets, OOB requests, focus grants, blueprints, `script_enums.txt` and the AI recipes are all
untouched. Loc becomes `tank_designer_flame` = "Armored Personnel Carrier" and
`tank_designer_amphibious` = whatever the amphibious vehicle is called.

**Superseded by the ruling below - no new role is being authored.** The cost is recorded because
it is the standing price of any *future* role, not because this one is queued: one or two
`duplicate_archetypes` roots, their derived tiers in `script_enums.txt`, module `allow`/`forbid`
bounds, `NSB_armor.txt` chassis grants, blueprint GUI files, AI recipes, the marine sub-unit
rewire, and the validator's `FAMILY_ROLES` plus the historical-design count.

### The probe is SHIPPED and OWNER-ACCEPTED 2026-09-13

The probe was written as inference from Finding 24 plus vanilla structure, and the owner then
settled it in game. Flame carries a working CWIC designer role; the one earlier attempt failed
only because its result was misread.

What shipped, and it is exactly the token retarget and nothing else:

| Surface | Change |
| --- | --- |
| `x_tank_chassis.txt:37,85` | both APC role roots `{ armor amphibious }` -> `{ armor flame }`. IFV roots untouched at `{ armor rocket }`. |
| `00_tank_modules.txt` | all 76 `amphibious` tokens -> `flame`, in four shapes: 12 `allow_equipment_type = flame` (APC modules), 38 `forbid_equipment_type = { flame rocket }` (conventional guns), 22 `{ light_armor medium_armor heavy_armor flame }` (IFV modules), 4 `{ light_armor medium_armor heavy_armor flame rocket }` (AA and the ATGM launcher). Zero `amphibious` tokens remain mod-wide in `common/`. |
| `designer_l_english.yml:225-226` | `tank_designer_amphibious` -> `tank_designer_flame`, still reading "Armored Personnel Carrier". The `amphibious` override is gone, so that dropdown entry renders vanilla's "Amphibious". Nothing claims it, by the 2026-09-13 ruling below. |
| `validate_military_reworks.py` | `CARRIER_ARCHETYPES` APC binding to `flame`; module bound map, type-domain check, conventional/AA forbid sets and `carrier_module_errors` retargeted; the two checks that rejected `flame` in eligibility keys and type domains **deleted**, since the APC modules legitimately carry it now. The separate rule that no chassis or role *name* may contain `flame` survives, as do `UNSUPPORTED_IDS` and the blueprint-filename regex - that is what flame removal actually retired. Two negative fixtures re-pointed from `amphibious` to `flame`. |

**No chassis id changed**, so the 586 national presets, 560 OOB requests, focus grants, blueprints,
`script_enums.txt`, `NSB_armor.txt` grants and the AI recipes were not touched and did not need to
be. That was the prediction and it held.

**Verification: static only.** Gate passes with the inventory line byte-identical to the
2026-09-12 baseline - `1317 technologies, 299 tank modules, 135 historical tank designs, 38
generic bookmark variants, 586 national presets and 560 named OOB requests across 68 NSB OOBs,
76 country-history bootstrap sites, 6220 stockpile grants, 16 carrier superstructure rungs, 5
relocated marine rows, and 20 designer slots checked`. A retarget should move no count, and it
moved none. `loc_audit_1.py --check` clean on 22 SEA files; no BOM gained by the two script files,
`designer_l_english.yml` keeps its BOM, and its only non-ASCII bytes are the legal section-sign
and pound-sign prefixes. `french/` and `russian/` were not touched.

**What the owner has to check, and it is the whole point of the pass:** open a light-hull design,
fit the APC superstructure and armament, and confirm the role header reads "Armored Personnel
Carrier", the design saves, it produces its own equipment on its own production line, and the
equipment tab lists it separately from the IFV. Confirm the IFV role still does all of the same on
`rocket`. `equipmentdesignerview.cpp:3657` on a redundant role selection is expected and benign -
Finding 24 - so judge the UI, not the log.

**Owner playtest passed and the batch is committed as `2636424db7`.** The APC role assigns, saves
and produces on `flame`; the tree is clean. Phases 6 and 7 went in with it, because their edits
share `00_tank_modules.txt` and `x_tank_chassis.txt` and could not be split by file. So
`flame` is now positively confirmed as a working CWIC designer role, not an inference - that fact
outlives the plan it was gathered for.

### Owner ruling 2026-09-13: there is no amphibious vehicle class, and `amphibious` stays unspent

**Confirmed by the owner after the probe landed: mechanized marines and mechanized paratroopers
will not have custom vehicles.** Every APC and IFV is usable by them, and no APC or IFV differs
from another by usage. This is the final word on the question Findings 14, 15 and 25 kept
reopening, and it closes them as a class rather than deferring them again.

**What it settles.** No dedicated amphibious mechanized role is authored. No amphibious role root,
no derived tiers, no marine sub-unit rewire, no second carrier family. Phase 6's APC-wide marine
transport is not a compromise that was accepted under token scarcity - it is the correct and final
design, and it is already shipped. The five relocated marine rows stay where phase 6 put them.
Do not re-price the amphibious batch; there is no batch.

**Status of the `amphibious` token: free, and deliberately unspent.** Nothing consumes it. Leave
it that way unless a genuinely new vehicle class appears, and note that the English
`tank_designer_amphibious` override is gone, so it renders with vanilla's "Amphibious" label if
anything ever claims it.

**Was the flame swap wasted?** Partly, and it is worth being straight about which part. The
taxonomic goal - stop "every APC is amphibious" being the mod's position - is still achieved and
still correct under this ruling, arguably more so: the APC family now carries a token with no
semantic claim at all instead of one that implies a capability the owner has just said does not
exist. What is wasted is the freed token, which now has no consumer. The swap cost four files, no
chassis ids and zero content edits, and it bought a confirmed answer to "is flame usable" that
three earlier sessions got wrong. That is a cheap price for retiring a false constraint.

**Do not** use this ruling to reopen the flame blacklist, the role-token vocabulary, or the
question of whether `need` can name a role root. Those are settled and unaffected.

### Owner QA 2026-09-13: the gating works, and the remaining rows are the deferred half

Owner capture of a non-NSB production tab still lists M16 Multiple Gun Motor Carriage, T66
launcher, M36 Jackson, LVT-4 Water Buffalo, M40 Gun Motor Carriage, 105mm Howitzer Motor
Carriage M7 and 155mm Howitzer Motor Carriage M41. **No new errors.**

**Every one of those is a row this pass deliberately left ungated** - SPAA, rocket SP artillery,
medium TD, heavy/light/medium SP artillery and a marine row. So the capture corroborates the
scope correction rather than contradicting it: the tank and carrier halves are gated, the
artillery/SPAA/TD/ATGM half waits on the artillery/AA restructure, and the marine rows are a
ratified exception. Nothing here is a defect.

### The mod already ships a per-country equipment art and naming library - 2026-09-13

Found while checking that capture, and it materially changes the vehicle-image and naming scope
recorded above. Both surfaces are larger and further along than this folder believed.

**Naming.** Legacy equipment carries per-country historical names through `<TAG>_<equipment_id>`
localisation keys, with `_short` variants: `ARG_spaag_equipment_1` is "M16 Multiple Gun Motor
Carriage", `ARG_mechanized_marine_equipment_1` is "LVT-4 Water Buffalo" / "LVT-4", and the same
ids recur across AUS, BRA, COL, CUB, GRE, INO and more in `localisation/english/*_equipment_l_english.yml`.
This is a real, populated system. Designer equipment does not use it - designer names come from
`create_equipment_variant`. Any "historical naming conversion" should be measured against these
files first rather than designed from scratch.

**Art.** `gfx/interface/technologies/` holds **9,965** files, including per-country per-tier
carrier art such as `ADR_APC_9.png` and `ADR_ifv_7.png`, and `interface/*_techs.gfx` registers
**16,283** `GFX_<TAG>_<id>_medium` sprites. The per-hull-tier icon limit recorded under "Vehicle
images" was measured against the designer `picture` path only; it says nothing about this
library, which is where any historical-image work should start.

**Four archetype textures were shipped and never registered**, which is the real reason the
picture values existed: `archetype_mechanized_equipment.dds`,
`archetype_mechanized_heavy_equipment.dds`, `archetype_car_transport_equipment.dds` and
`archetype_mechanized_airborne_equipment.dds` sit in `gfx/interface/` with no `spriteType`
anywhere.

**So the earlier mechanized fix was corrected, 2026-09-13.** Pointing the two mechanized families
at the motorized picture was the right call on the evidence available at the time - no
`archetype_mechanized_*` sprite existed - but the textures did. Both sprites are now registered
in `interface/cwic_tank_rework_icons.gfx:2724-2725` and `mechanized.txt:11` and
`mechanized_heavy.txt:12` carry their own art again. This restores intended art instead of
sharing the motorized icon, and it is no less safe: the texture files are already in the repo.
`mechanized_marine_equipment` has no texture of its own and stays on the motorized picture.
`archetype_car_transport_equipment` and `archetype_mechanized_airborne_equipment` belong to
non-armour families and were left alone.

### The reverse map is BUILT 2026-09-13 - `data/Historical_Vehicle_Reverse_Map.json`

The owner's idea works and is now a machine-readable manifest, 402 KB, 77 equipment tiers.
**The join is `enable_equipments`**: a technology names the equipment it unlocks, the per-country
art is `GFX_<TAG>_<technology>_medium`, and the historical name is `<TAG>_<equipment_id>` in
`localisation/english/*_equipment_l_english.yml`. Technology is the hinge - art keys on the
technology name, names key on the equipment id, and nothing joined them before.

Measured supply: 16,526 `GFX_<TAG>_<tech>_medium` sprites, 6,897 per-country equipment names, and
**1,468 country rows that resolve BOTH art and a historical name** for a legacy armour tier. Each
manifest row carries the technology and its file, the equipment id and its file, the year, the
family, the designer target family, and the per-country art path and name.

| Family | Country rows with art + name |
| --- | ---: |
| `mechanized_equipment` | 364 |
| `mbt_equipment` | 297 |
| `lt_equipment` | 185 |
| `mechanized_heavy_equipment` | 152 |
| `sp_artillery_equipment` | 91 |
| `mechanized_marine_equipment` | 84 |
| `light_sp_artillery_equipment` | 83 |
| `spaag_equipment` | 81 |
| `medium_tank_destroyer_equipment` | 57 |
| `heavy_sp_artillery_equipment` | 49 |
| `ht_equipment` | 25 |
| `atgm_carrier_equipment` | 0 |
| `sht_equipment` | 0 |

Two gaps, both known rather than guessed: the five `atgm_carrier_equipment_*` tiers have **no
per-country art at all** - no `atgm_carrier_*` tech sprite exists - and the three
`sht_equipment_*` tiers have **no per-country names**. `rocket_sp_artillery` does not appear
because no technology declares `enable_equipments` for it; that family needs checking separately.

**Every family maps onto a light, medium or heavy hull role**, which is what makes the conversion
tractable - the manifest's `designer_target` column is filled for all 13 families with no
remainder.

The manifest is a data artefact for the conversion pass, not a decision. What still needs an
owner ruling per row: whether a designer design inherits the legacy historical name, and whether
per-country art can attach to designer equipment at all - see the icon-resolution question below.

### Suggested order

1. ~~Commit the phase 6/7 and flame-probe work.~~ **Done 2026-09-13, `2636424db7`.**
2. ~~The flame probe.~~ **Shipped and owner-accepted 2026-09-13.** The amphibious role it was
   gating is ruled out; see the ruling above. Nothing downstream is blocked on it.
3. ~~The unregistered archetype pictures.~~ **Fixed 2026-09-13** by renaming five picture values
   onto registered sprites, with a new validator contract. Static only; icons unseen in game.
4. ~~Legacy NSB gating.~~ **Complete 2026-09-13.** 37 tank and carrier rows first, then the
   remaining 30 artillery/SPAAG/TD/ATGM rows once the convergence made them safe. **67 legacy
   rows are now DLC-gated**; the only ungated rows are the seven ratified exceptions.
5. ~~The artillery/AA restructure.~~ **Shipped 2026-09-13, Finding 26.** No standalone armour
   family remains.
6. **The mass non-NSB to NSB conversion - next.** Historical OOBs, naming, 2D art and entities
   onto the designer systems. Start from `data/Historical_Vehicle_Reverse_Map.json` and the
   measured per-country library (9,965 technology art files, 16,283 `GFX_<TAG>_<id>_medium`
   sprites, `<TAG>_<equipment_id>` loc keys), not the designer `picture` path, whose
   per-hull-tier limit does not apply to it. The convergence just removed six families from this
   surface, so re-measure the reverse map's 1,468 rows before planning against it.
7. The icon-resolution probe still owed: no `GFX_<TAG>_<equipment_id>_medium` sprite exists for
   the rows that nonetheless render per-country photographs, so the resolution rule is unproven
   and gates any per-country designer art.
8. ~~Heavy APC / Heavy IFV battalions.~~ **Shipped 2026-09-17, Finding 31**, with the plain-member
   defect behind their invisibility fixed the same day in Finding 33. Owner QA confirmed the
   group split and both light battalions in game; two gate moves and an `active = yes` probe
   proved enablement was never the cause.
9. ~~Legacy implementation for the heavy carrier battalions.~~ **Done 2026-09-17 as part of
   Finding 33**, because it was the fix rather than deferrable content: `heavy_apc_equipment_1..3`
   and `heavy_ifv_equipment_1` serve both DLC profiles, so the NSB-only ruling is void.
10. ~~QA for Finding 33.~~ **Owner-accepted 2026-09-17.** All four carrier battalions plus Heavy
   Tank Destroyer and Medium SPAAG confirmed selectable, drawing the right family, with the
   intended stat and cost ordering. Icons and sprites for the new content are ruled out of
   scope: functional behaviour only.
11. ~~Per-country art for the six new equipment rows.~~ **Out of scope, owner ruling
   2026-09-17.** Their generic names and shared sprites are accepted; only the historical-name
   half of this remains, and it belongs to the mass conversion at item 6.
12. ~~AI production and division templates.~~ **Done 2026-09-17, Finding 34.** `ai_equipment`
   needed nothing - it was already complete at 135 variants. Four tech-gated templates now
   field the heavy carriers, a dead `lt_equipment` upgrade trigger is fixed, and
   `validate_ai_templates()` guards the class. Static only; AI behaviour unobserved.
13. **Next: the mass non-NSB to NSB conversion, item 6.** It is now the only large functional
   item left. One smaller one remains beside it: OOB references for the four carrier battalions,
   which no scripted order of battle fields yet. ~~The focus-grant historical variant mapping~~ is
   **done 2026-09-24, Finding 53**, widened to events and decisions.
14. ~~A both-profiles enabler for `heavy_tank_destroyer_brigade` and
   `medium_sp_anti_air_brigade`.~~ **Done 2026-09-17, Finding 39.** Both moved onto
   `tank_destroyer_1` and `spaag_1`, so they work on either profile and the AI can field them.
15. ~~Conversion tranche 1.~~ **Done 2026-09-17, Finding 35.** Thirty bookmark starting designs
   gave all five previously uncovered role families one; the naming debt re-measured to 672 rows
   of which only 4 were addable under the bookmark contract.
16. ~~The carrier armour cap.~~ **Ruled light-hull-only 2026-09-17.** It was unsatisfiable for
   medium-hull carriers by construction; they are now capped by their own hull, which unblocked
   the fourteen Heavy APC / Heavy IFV starting designs.
17. ~~Mid-campaign naming.~~ **Built 2026-09-17, Finding 36.** 386 named designs across 22
   generations and 48 TAGs, delivered through `on_research_complete`, with
   `validate_research_armour_naming()` pinning provenance against live localisation.
18. ~~Tranche 2 naming.~~ **Done 2026-09-17, Finding 37.** The reverse-map null-year gap is
   closed, research-time naming is 453 designs over 25 generations, and the bookmark pipeline
   gained 23 rows. Every remaining reverse-map name is classified: 203 closed by design, 12
   blocked by the carrier legacy-flag contract.
19. ~~QA for Findings 35 and 36.~~ **Owner playtest accepted 2026-09-17** - names appear
   correctly and the newly covered families behave. QA is still owed for the tranche 2 additions
   specifically: the three `light_tank_ifv_chassis_6/7/8` helpers and the 23 bookmark rows.
20. ~~The OOB requests.~~ **Done as far as it can go, 2026-09-17, Finding 38.** 20 requests
   authored across NOR and RAJ for `light_tank_destroyer_chassis_5`, plus RAJ's missing
   bootstrap technology. The other 24 are not writable: four of the five consuming battalions
   appear in zero orders of battle.
21. ~~Put the unfielded battalions into historical divisions.~~ **Done 2026-09-17, Finding 39.**
   Medium SPAAG goes to the WGR Panzer-Division as the Gepard, Heavy Tank Destroyer to the SOV
   Guards Tank Division as the ISU-152, both profiles. Heavy Mechanized and Heavy Armored
   Infantry are deliberately left unfielded: their 1985 and 2005 generations postdate both
   bookmarks, so a scripted 1980 formation carrying one would be invented history.
22. ~~The blocked carrier rows.~~ **Done 2026-09-17, Finding 40.** The inventory was widened
   rather than the flag contract touched: marine equipment joins the pipeline, legacy levels
   1-2 clamp onto tier 0, and the `MBZ -> MZB` alias is a shared constant. 572 -> 587 pairs,
   15 new national carrier designs, and the selection rule now takes the newest legacy level so
   the widening renames nothing.
23. **The final playtest.** Everything planned is implemented. Note the profile limit: the
   designer, all 30 starting designs and both naming mechanisms are behind
   `has_dlc = "No Step Back"`, so a non-NSB session can only exercise the legacy path - the six
   new legacy equipment rows, the four carrier battalions and their group split, and the two
   newly fielded brigades.
