# Ratified decisions

Accepted choices. **Check here before proposing a redesign - most of it is settled,
and several entries record a wrong answer that was already tried.** The owner has
authorized practical design judgment within this scope; no repeat approval is needed.

## Three-hull restructure, ratified 2026-09-10

**Owner direction, and it is the largest architectural change this project has taken.
It supersedes every earlier statement about how many designer families exist.** Read
this section before anything below it: several entries in "Architecture" describe the
five-family world and are marked superseded where they conflict.

**Every armoured ground vehicle is a role on one of three hulls: light, medium, heavy.**
The five shipped designer families (light tank, medium tank, heavy tank,
`mechanized_equipment`/`apc_chassis_0..7`, `mechanized_heavy_equipment`/`ifv_chassis_0..7`)
collapse to three. APC and IFV stop being standalone families and become light-hull
roles; Heavy APC and Heavy IFV become medium-hull roles. This directly supersedes
"APC and IFV are standalone designer families" below, and it keeps that entry's
Heavy-APC/Heavy-IFV-are-medium-generation conclusion while changing its mechanism from
hull tiers to a role root.

### The role table

Light hull `light_tank_chassis`, tiers 0-9, 1939/1942/1944/1950/1960/1970/1980/1990/2000/2010:

| Vehicle | Role root | `type` set | State |
| --- | --- | --- | --- |
| Light Tank | base archetype | `{ armor light_armor }` | exists |
| APC | `light_tank_apc_chassis` | `{ armor light_armor mechanized }` | new |
| IFV | `light_tank_ifv_chassis` | `{ armor light_armor mechanized ifv }` | new |
| Light Tank Destroyer | `light_tank_destroyer_chassis` | `{ armor light_armor anti_tank }` | exists |
| Light SP Artillery (LL/LM/LH) | `light_tank_artillery_chassis` | `{ armor light_armor artillery }` | exists |
| Light SPAA | `light_tank_aa_chassis` | `{ armor light_armor anti_air }` | exists |
| ATGM Carrier | `light_tank_atgm_chassis` | `{ armor light_armor atgm }` | new |

Medium hull `medium_tank_chassis`, tiers 0-9, same year ladder:

| Vehicle | Role root | `type` set | State |
| --- | --- | --- | --- |
| MBT / Medium Tank | base archetype | `{ armor }` | exists |
| Heavy APC | `medium_tank_apc_chassis` | `{ armor mechanized }` | new |
| Heavy IFV | `medium_tank_ifv_chassis` | `{ armor mechanized ifv }` | new |
| Medium Tank Destroyer | `medium_tank_destroyer_chassis` | `{ armor anti_tank }` | exists |
| Medium SP Artillery (ML/MM/MH) | `medium_tank_artillery_chassis` | `{ armor artillery }` | exists |
| Medium SPAA | `medium_tank_aa_chassis` | `{ armor anti_air }` | exists |
| ATGM Tank | `medium_tank_atgm_chassis` | `{ armor atgm }` | new |

Heavy hull `heavy_tank_chassis`, tiers 0-4, 1939/1942/1944/1950/1955:

| Vehicle | Role root | `type` set | State |
| --- | --- | --- | --- |
| Heavy Tank | base archetype | `{ armor }` | exists |
| Heavy Tank Destroyer | `heavy_tank_destroyer_chassis` | `{ armor anti_tank }` | exists |
| Heavy SP Artillery (HL/HM/HH) | `heavy_tank_artillery_chassis` | `{ armor artillery }` | exists |

Six new role roots, one retirement. `heavy_tank_aa_chassis` retires: the ratified
Anti-Air taxonomy is Light SPAAG and Medium SPAAG only, with no heavy entry. The three
flame roots are not in the taxonomy either - see open decision 2.

**LL/LM/LH is a gun choice, not a role.** The owner enumerates nine light-hull vehicles
including LL, LM and LH Self-Propelled Artillery, but the battalion taxonomy has exactly
three artillery types - Light, Medium and Heavy SP Artillery - which map one-to-one onto
the three hulls. So the three gun weights share one artillery role per hull, selected by
which artillery gun module is mounted. Nine artillery role roots would also be
unusable: a sub-unit's `need` names one family, so a "Light SP Artillery" battalion can
consume only one of them.

### This restructure repairs the defect that blocked amphibious, and it is why the design works

`duplicate_archetypes` derives a role's tier ids by substituting the parent archetype's
name inside each member id. That only produces a clean id when the member id **contains**
the archetype id. Measured, and already recorded below under the reverted carrier
attempt:

| Family | Archetype | Members | Derived role tier |
| --- | --- | --- | --- |
| tanks | `light_tank_chassis` | `light_tank_chassis_0..9` | `light_tank_apc_chassis_3` - clean |
| carriers | `mechanized_equipment` | `apc_chassis_0..7` | `apc_amphibious_chassisapc_chassis_0` - concatenated |

Moving carriers onto the tank hulls puts every future carrier role on the left-hand row.
The concatenation defect class disappears permanently rather than being worked around.

**Consequence: Findings 14 and 15 are resolved, not deferred.** Finding 15 established
that a land sub-unit's `need` and `transport` resolve an equipment *family* - an
`is_archetype = yes` root or a `duplicate_archetypes` role root - and never a plain
numbered member, which is why explicitly declared `apc_amphibious_chassis_N` hulls could
never supply marines selectively. A role root **is** a family. `mechanized_infantry` can
name `light_tank_apc_chassis`, `armored_infantry` can name `light_tank_ifv_chassis`, and
an amphibious role root is nameable the same way. The three priced amphibious options in
Finding 15 are obsolete: option 1's "full sixth family" cost collapses to one
`duplicate_archetypes` block. Do not re-price that batch off the old finding.

**Amended 2026-09-17, and this is a hard prerequisite rather than a nuance: a role root is a
family only once it declares at least one plain member.** An equipment row with
`archetype = <root>` must exist; tiers derived by `for_each` alone are not enough, and a
sub-unit whose `need` names a root with no plain member is silently dropped from the division
designer with nothing in `error.log`. The eight role families that worked had plain members only
because the carrier cutover and the artillery convergence relocated legacy rows into them; the
four that never received legacy content - both medium carriers, `medium_tank_aa_chassis` and
`heavy_tank_destroyer_chassis` - were unusable until plain ladders were authored. Vanilla
declares a plain ladder under every role family a sub-unit consumes and consumes none of its
childless roots. **Any new role family therefore costs a `duplicate_archetypes` block *and* at
least one equipment row.** See `STATUS.md` Finding 33; the validator now fails on it.

### Battalion taxonomy

Line battalions, which make up the division's line:

| Class | Members |
| --- | --- |
| Infantry Carrier | APC, Heavy APC, IFV, Heavy IFV |
| Armor | Light Tank, MBT, Heavy Tank |

Support companies:

| Class | Members |
| --- | --- |
| Recon | Light Tank Recon, IFV Recon, APC Recon, Motorised Recon, MBT Recon |
| Artillery | Light SP Artillery, Medium SP Artillery, Heavy SP Artillery |
| Anti-Air | Light SPAAG, Medium SPAAG |
| Fire Support | Tank Destroyer, ATGM Carrier, ATGM Tank |

Every one of these consumes a role root or a base hull from the table above. The current
sub-units consume legacy archetypes instead (`spaag_equipment`, `sp_artillery_equipment`,
`medium_tank_destroyer_equipment`, `atgm_carrier_equipment`, `mechanized_equipment`,
`mechanized_heavy_equipment`), and all of them except the three `need_for_tank_roles.txt`
armour battalions are `active = no`. Rewiring `need`/`transport` onto role roots is the
step that makes the designer output actually reach the battlefield.

### The 20 positions are fully specialized - there are no free slots

Supersedes the shipped "slots 5-16 share one twelve-category free list" map below, and
corrects the 21-position count downward - see the engine cap immediately after the table.
The layout is five mandatory positions plus fifteen dedicated special slots. Measured
against the module inventory, the fit is exact rather than approximate:

| Slot | Label | Categories | Modules | State |
| --- | --- | --- | ---: | --- |
| mandatory | Gun, Turret, Suspension, Armour, Engine | unchanged | - | exists |
| 1 | AP Ammunition | `tank_ammo_kinetic` | 13 | exists |
| 2 | HE / HEAT Ammunition | `tank_ammo_he`, `tank_ammo_chemical` | 22 | exists |
| 3 | Aiming | `tank_fcs_aiming` | 11 | exists |
| 4 | Optics | `tank_fcs_optics` | 22 | exists |
| 5 | Computing | `tank_fcs_computer`, `tank_fcs_radar` | 21 | exists |
| 6 | Loading System | `tank_loader_manual_assist`, `tank_loader_autoloader`, `tank_loader_artillery` | 14 | exists |
| 7 | ATGM | `tank_ammo_missile` | 9 | exists |
| 8 | External Armour / Fuel Tanks | `tank_protection_passive`, `tank_external_fuel` | 7 + 1 | new category |
| 9 | Explosive Reactive Armour | `tank_protection_reactive` | 5 | exists |
| 10 | Secondary Armament | `tank_secondary_turret` | 5 | exists |
| 11 | Active Protection | `tank_protection_active` | 6 | exists |
| 12 | Smoke | `tank_smoke` | 6 | exists |
| 13 | Fire Fighting Systems | `tank_survivability` | 5 | exists |
| 14 | Auxiliary Power Unit | `tank_power_auxiliary` | 11 | new category |
| 15 | Engineering Equipment | `tank_mine_clearing`, `tank_engineering_blade` | 6 | new categories |

**The engine renders at most 20 custom module slot windows, and this is now the binding
constraint on the whole designer.** Established 2026-09-10 by owner live test, and it
overturns "21 positions is now verified" recorded on 2026-09-09. That earlier
verification was of the *declaration*, not of the render: all 21
`tank_special_slot_*` names resolved and the log was clean, which is exactly why the
missing 21st cell read as `-debug` overlay noise at the time - see the "one cosmetic note"
paragraph in `STATUS.md` Finding 6, which described a dark seventh cell in the bottom row.
That cell was the defect.

The test that settles it: `pos_custom_module_slot_window_20` never renders; removing index
19 and renaming 20 into its place still yields only the first twenty. The cap is on the
**count of positions**, not on any particular index. So the ceiling is
`pos_custom_module_slot_window_0..19` - twenty positions, laid out 7 / 7 / 6 - and five
mandatory slots leave exactly fifteen special slots.

**Mine Clearing and Engineering Blade were merged to pay for it.** They are the cheapest
pair to merge and the merge is thematically right rather than expedient: both are hull-front
attachments, a vehicle mounts one of them, and slot exclusivity is exactly that statement.
Neither category is deleted - both survive with their own `count < 2` limit, all six modules
stay reachable, and no module changes category. The alternatives were worse: dropping the
ATGM slot would strand nine missile modules, and dropping Secondary Armament would strand
five modules with fourteen live preset references.

**Do not add a 21st position.** The validator now fails on
`pos_custom_module_slot_window_20`, and any future slot family has to displace an existing
one or share a slot the way slots 2, 5, 6, 8 and 15 do.

**Slot ids were chosen to make the migration free, and the ordering is deliberate.** The
owner's picture reads in a visual order; slot *ids* do not have to match it, and
`DECISIONS.md` already establishes that the GUI label number is allowed to differ from the
slot id. Measured: of 6,041 special-slot assignments across the three scripted-effect
files only **567 are non-empty**, and every one of them already sits in a slot whose
meaning this map preserves - slot 1 `ap_*` (257), slot 2 `tank_he_*` / `tank_aa_ammo_*`
(260), slot 3 `Aim_*` (14), slot 4 `Optics_*` (14), slot 5 `Computer_*` (6), slot 6
`Loader_3a_Carousel` (2), slot 10 `cwic_coaxial_mg` (14). Slots 7-9 and 11-16 are `empty`
or absent everywhere. So full specialization costs **zero** preset, OOB, focus or
AI-recipe edits. Any reordering to match the picture visually would break 567 live
assignments for presentation only. Do not renumber these slots.

**Secondary Armament takes the slot the owner's list gave to Underwater Driving.** One
swap against the owner's enumeration, and the reason is asymmetric evidence:
`tank_secondary_turret` has five live modules and fourteen live preset references, while
Underwater Driving has **zero** modules, no technology and no balance row, and is blocked
on the same missing engine mechanism as amphibious and OPVT. Authoring an empty dedicated
slot while evicting a live five-module family would be the wrong way round. Underwater
Driving takes a position when its modules are authored in the amphibious batch - either as
a 22nd position or by sharing slot 16. This closes open decision 1 below.

**`tank_mobility_auxiliary` dissolves exactly, with no remainder.** Its 18 modules split
four ways and nothing is orphaned: `APU_0..6` plus `GT_APU_0..3` (11) to
`tank_power_auxiliary`, `Fuel_Tanks_0` (1) to `tank_external_fuel`, `Mine_Plow_0/1` and
`Mine_Roller_0/1` (4) to `tank_mine_clearing`, `Dozer_0` and `Trench_Plow_0` (2) to
`tank_engineering_blade`. The category is then deleted, not left empty. That the arithmetic
lands on 18 with no leftovers is the strongest evidence available that the owner's
sixteen-slot list was drawn against this module set.

`tank_survivability` already holds `FFS_0..2` alongside `Log_0` and `Blowout_Panels_0`, so
the Fire Fighting Systems slot needs no new module; the picture's "Blow-Out Pannels" box is
that slot showing a different mounted module.

**Mutual exclusion is expressed by slot sharing, not by a module key.** The owner requires
External Additional Fuel Tanks to be mutually exclusive with External Additional Armour.
`DECISIONS.md` already establishes that this engine has no module-to-module compatibility
key for land equipment. One slot admitting both categories delivers exactly that
exclusion, because a slot holds one module. Do not look for a `conflicts_with` key.

**The `count < 2` limits are kept, and the limited-category list goes 18 -> 21.** With
every category owning a dedicated slot the limits are strictly redundant - a slot holds
one module, and the four two-category slots cannot stack either. They are retained
anyway, because deleting 90 blocks across five archetypes would also mean rewriting the
validator's limit contract and its multi-category rejection fixture for no behavioural
gain. The one required change is that `tank_mobility_auxiliary`'s limit is replaced by
four limits for the categories that replace it. A multi-category limit block stays
prohibited.

**The slot-budget debt is discharged.** "Owner decisions, 2026-09-09 (gated-item batch)"
item 5 accepted the per-category fallback and recorded the debt that twelve free slots let
a design mount all three protection categories and all three utility categories where the
frozen envelopes assumed two of each. Full specialization removes that: protection is now
three separate one-per-vehicle slots by design rather than by accident, and the
still-unverified multi-category shared budget is no longer needed for anything. Do not
reopen the shared-budget test.

### The two engine gates

**Gate A: novel `type` tokens - CLOSED 2026-09-10, equipment `type` is an open enum.**
The role table needs two tokens outside vanilla's vocabulary: `ifv`, to tell an IFV role
from an APC role on the same hull, and `atgm`, to tell an ATGM carrier from a tank
destroyer. Without them `allow_equipment_type` cannot separate `tank_ifv_armament` from
`tank_apc_armament`, because both roles would read `mechanized`. The owner closed this by
live test: `light_armor` - a token this mod invented, absent from vanilla's 43 equipment
`type` tokens - was built onto a light tank chassis with zero errors and no issues, and
custom equipment types are documented as supported. **Custom `type` tokens are legal. Do
not reopen this as an engine risk.** The vanilla token vocabulary, measured for reference,
is 43 tokens across `common/units/equipment/*.txt`, of which the land-relevant ones are
`armor`, `infantry`, `motorized`, `mechanized`, `artillery`, `anti_air`, `anti_tank`,
`amphibious`, `flame`, `rocket`, `support`, `railway_gun`.

**Gate B: enum coverage for derived tiers - resolved by planning, not by test.**
`script_enum_equipment_bonus_type` (`common/script_enums.txt:152-1046`, 872 entries)
enumerates role roots at `:773-784`, base hull tiers at `:785-809` **and** derived role
tiers at `:810-909`. A new role root therefore needs its root plus every derived tier
listed, or the game logs one `equipment_database.cpp:656` line per missing id. Six new
roots across the 10/10/5 tier ladders is 6 roots + 50 derived ids, all authored in phase 3.
Note the existing derived entries at `:962-1045` contain malformed `chassist` / `chassisbt`
forms - artefacts to check when the block is extended, not a pattern to copy.

## Role tokens are a closed set - ratified 2026-09-10

**The tank designer's role vocabulary is hardcoded in the binary.** A custom equipment
`type` token is legal and works for module eligibility, but it can never be a named,
selectable designer role. This is the constraint the carrier half of the restructure has
to live inside, and it was settled by in-game probe rather than by reading: pointing one
module at `amphibious` and another at `rocket` made both appear as roles, while
`mechanized`, `ifv` and `atgm` never did - and `mechanized` is a vanilla category, which
rules out "declare it as a category" as the answer.

The full vanilla vocabulary, measured across the whole install: `anti_tank` (9
`allow_equipment_type` uses), `artillery` (6), `anti_air` (3), `flame` (2), `amphibious`
(1), plus `rocket`, which has a `tank_designer_rocket` localisation key and no vanilla role
root - now confirmed usable by the same probe.

**Ratified mapping.** The label a player sees is our localisation, so the internal token
name does not have to match the vehicle:

| Vehicle role | Token | Dropdown label |
| --- | --- | --- |
| Tank Destroyer, ATGM Carrier, ATGM Tank | `anti_tank` | Tank Destroyer |
| SP Artillery | `artillery` | Artillery |
| SPAA | `anti_air` | Anti-Air |
| APC, Heavy APC | `amphibious` | Armored Personnel Carrier |
| IFV, Heavy IFV | `rocket` | Infantry Fighting Vehicle |

**ATGM is a loadout, not a role.** Folding ATGM into the tank destroyer role is better than
spending a token on it: `tank_atgm_launcher_cannon` already gates on `anti_tank` and sits in
`tank_small_main_armament`, which both the light and medium hulls admit, so an ATGM Carrier
is a tank-destroyer-role design that mounts the launcher instead of a gun. The ratified Fire
Support taxonomy still ships in full; the distinction is the weapon, not the chassis role.

**`rocket` does work as a role - the apparent failure was a benign log line.** Established
2026-09-11 by owner QA: both carrier roles assign, save, produce and appear correctly in the
production and equipment tabs. `equipmentdesignerview.cpp:3657` fires only because
`allow_equipment_type` has already moved the design into the role before the player selects
it, so the dropdown click is a no-op. See `STATUS.md` Finding 24.

**The one-role carrier consolidation was tried and reverted 2026-09-11.** It is recorded
in `STATUS.md` Finding 23 as a dead end. The theory was that a second carrier role poisons
the hull's role list, since moving IFV onto `flame` broke the previously working APC role.
Consolidating both carriers onto `amphibious` alone reported both still broken, which
disproved that theory; the truth is that neither was ever broken. The tree is reverted to
the last state with a confirmed-working APC: APC on `amphibious`, IFV on `rocket` and still
failing its role change. One working role beats two broken ones.

**`flame` is available - corrected 2026-09-13, and the earlier blacklist is withdrawn.** The
sentence that stood here said flame "is the one token observed to break a role that was
previously working". That observation is the benign `equipmentdesignerview.cpp:3657` line, and
`STATUS.md` Finding 24 names the flame remap explicitly as one of "two wrong turns ... both
attempts to fix a defect that did not exist". Nothing was ever broken, so nothing was ever
observed about flame. Structurally flame is in the **stronger** group, not the weaker one: it
has a vanilla `duplicate_archetypes` role root (`light_tank_flame_chassis`,
`medium_tank_flame_chassis`, `heavy_tank_flame_chassis` at vanilla `x_tank_chassis.txt:47,92,137`),
which is the exact property the `rocket` diagnosis below used as its discriminator. **Confirmed
in game 2026-09-13** by owner playtest of the APC-on-`flame` swap, committed as `2636424db7`:
the role assigns, saves and produces. Flame is a working designer role, not a theory.

**`rocket` renders but cannot be switched to - the usable set is five, not six.**
**SUPERSEDED 2026-09-11 by Finding 24 and by the shipped tree, which runs IFV on `rocket`
and passed owner QA.** Kept for the structural discriminator it records, which is still the
best predictor available; its conclusion is wrong. Original text follows. Corrected
2026-09-10 after the remap shipped on `rocket` and the owner hit
`equipmentdesignerview.cpp:3657: Failed to change role to "Infantry Fighting Vehicle"` on
save, while the `amphibious` APC role worked completely. The discriminator is structural:
`amphibious`, `anti_air`, `anti_tank`, `artillery` and `flame` each have a vanilla
`duplicate_archetypes` role root in `x_tank_chassis.txt`; `rocket` has a
`tank_designer_rocket` localisation key and a category entry but **no role root anywhere in
the base game**. That is enough to render it in the dropdown and not enough to make it a
real role.

So IFV took `flame` on 2026-09-10, then moved back to `rocket` with the 2026-09-11 revert, and
APC took `flame` on 2026-09-13. The names are internal; the dropdown label is our localisation.

**Superseded by the final map below.** This paragraph claimed the vocabulary is five tokens, all
spent, with `rocket` excluded. Both halves are wrong: `rocket` works, the vocabulary is six, and
one token is unspent. Its surviving conclusion is that ATGM is a loadout - that stands, on the
separate ground ratified above.

## Final role-token map, ratified 2026-09-13

| Token | Spent on |
| --- | --- |
| `anti_tank` | Tank Destroyer, and ATGM as a loadout on it |
| `artillery` | SP Artillery |
| `anti_air` | SPAA |
| `flame` | Armored Personnel Carrier |
| `rocket` | Infantry Fighting Vehicle |
| `amphibious` | **deliberately unspent** |

The internal token names are invisible to players; the dropdown label is our localisation. The
English `tank_designer_amphibious` override was removed with the swap, so that entry renders
vanilla's "Amphibious" if anything ever claims it.

**Owner ruling 2026-09-13: mechanized marines and mechanized paratroopers get no custom
vehicles.** Every APC and IFV is usable by them; no carrier differs from another by usage. So
there is no amphibious vehicle class, no dedicated amphibious role, and no marine sub-unit
rewire. **This closes Findings 14, 15 and 25's amphibious thread as a class, not as a
deferral** - phase 6's APC-wide marine transport is the final design rather than a concession
to token scarcity, and it is already shipped. Do not re-price the amphibious batch; there is
no batch. The `amphibious` token stays free unless a genuinely new vehicle class appears.

**Consequence for the flame-removal contract:** the validator no longer bans the `flame`
type token, because the APC roles legitimately carry it since 2026-09-13. What it bans is any
chassis or role whose *name* contains `flame`, which is the thing that was actually retired.

Role roots therefore settle at **12**, not 14.

**Do not reopen this by trying to register a new token.** There is no mechanism. The
validator rejects any `allow_equipment_type` or `forbid_equipment_type` value, and any
non-`armor` token on the three hulls or their role roots, outside
`{anti_air, anti_tank, artillery, amphibious, rocket, flame}` plus the three size tokens -
`rocket` stays in the legal set because it is a real equipment type, but nothing uses it.
The two standalone carrier families additionally keep `mechanized`, which is a vanilla
equipment type and not a designer role.

**Retired 2026-09-13.** This note tracked that APC carried the `amphibious` token and that the
amphibious supply problem was therefore solvable whenever the batch was picked up. APC moved to
`flame` on 2026-09-13 and the owner ruled that there is no amphibious vehicle class, so there is
nothing left to track and no batch to pick up. Marines ride any APC or IFV, as shipped in phase 6.

### Flame tanks are removed - ratified 2026-09-10

**Owner ruling: flame is axed completely.** Nothing in the mod uses flame tanks, and
everything flame-related is legacy or vanilla-inherited. This is a clean cutover, and it
closes the last open decision on the restructure.

The removal was safe to take in full because the consumers do not exist: **`history/`,
`common/ai_templates/` and every OOB contain zero references to any flame sub-unit or
flame chassis.** No division template, no starting order of battle and no AI template
fields a flame battalion, which is the same evidence known inconsistency 1 recorded from
the other side when it noted that no AI division template fields a flame battalion.

What goes: the three `duplicate_archetypes` role roots, the three `active = yes`
sub-units in `need_for_tank_roles.txt`, the `flamethrower` module and its
`tank_flamethrower` category, that category's place in all three `main_armament_slot`
lists, every flame grant in `NSB_armor.txt`, the flame AI recipes, all flame entries in
`script_enum_equipment_bonus_type`, 24 blueprint GUI files, the flame designer-module and
MIO department sprites, the English localisation, and the dead flame entity aliases.

**Four surfaces are deliberately left alone**, and each for a reason rather than by
omission:

- `interface/texticons.gfx`. It is a full vanilla override, and a comment at `:2920`
  records that dropping entries there previously produced 1002 error-log lines. Orphan
  sprites are harmless; editing that file is not.
- `localisation/french/` and `localisation/japanese/`. Another team owns translations.
  Dead keys there are acceptable.
- `sound/sound.asset` and `combat_tactics.txt`. The sound entries are animation effects
  with no equipment binding, and the tactics block is already commented out.
- `common/military_industrial_organization/`. Six policies test
  `has_mio_equipment_type = flame`; with no equipment carrying that type they simply stop
  matching. That content has another owner, and silently deleting policy conditions to
  tidy a type token would be the wrong trade.

**Consequence for the role dropdown.** `REFERENCE.md` explains that the dropdown lists one
entry per distinct `allow_equipment_type` value in the loaded module set. Removing
`flamethrower` - the only module carrying `allow_equipment_type = flame` - drops the mod
from four such values to three, so every chassis designer now shows four entries instead
of five. That is the intended outcome, not a regression to investigate.

The `tank_secondary_turret` question is closed - see the slot table above. No open
decisions remain on the restructure.

### What this restructure costs - see `STATUS.md` Finding 16 for the measured blast radius

The headline is that the carrier retirement is a **mass content migration**, not the
contract-only change the 15-to-21 slot expansion was. 857 `apc_chassis_*` / `ifv_chassis_*`
references live across 70 files, 572 of them in `CWIC_national_tank_presets.txt` alone, and
full slot specialization invalidates the "already-explicit assignments stay legal"
guarantee that made the last expansion cheap.

### Carrier cutover, ratified 2026-09-11

**Tier mapping: not-later-than-year.** Each retired carrier tier lands on the newest light
hull tier whose year does not exceed it. APC 0-7 to light 2, 3, 4, 4, 5, 6, 7, 8; IFV 0-7
to light 2, 3, 3, 4, 5, 6, 7, 8. Mapping by armour instead was rejected outright: the hull
tier is the research tier, so an armour-anchored mapping would let a 1939 technology
produce a 1985 BTR. Two pairs collide and that is accepted; the merge was measured first
and produces zero duplicate `(tag, name, chassis)` triples across all 572 national presets.

**Both carrier families go to the light hull.** `light_tank_ifv_chassis` is "Infantry
Fighting Vehicle" and `medium_tank_ifv_chassis` is "Heavy IFV", so the legacy IFVs are
IFVs. Their armour ladder was authored at medium-hull weight, which is a pricing defect
rather than a statement about which hull they belong on.

**The delta rides on role-exclusive modules, and covers armour, cost and speed only.**
Not `for_each`: every `for_each` block in vanilla was audited and the whole observed
vocabulary is `variant_name = { find_and_replace }`, `hardness = { set }` and
`air_superiority = { set }`. There is no evidence `multiply` is accepted there, and `set`
would flatten a stat across all ten tiers. `defense`, `breakthrough`, `reliability` and
`fuel_consumption` adopt the hull curve: reproducing them meant authoring a troop
compartment with `defense = +39` and `breakthrough = -8`, which would defeat the point of
putting carriers on the hull curve. Phase 7 owns the recalibration.

**The sixteen freed hull technologies become the carrier's generational ladder.** After
phase 3 the light hull technologies already unlock every `light_tank_<role>_chassis_N`, so
`nsb_apc_hulls0..7` and `nsb_ifv_hulls0..7` had nothing left to enable. Each now unlocks
one rung of an eight-step superstructure ladder, which is also the fix for a real content
gap: the carrier designer had three APC and two IFV superstructure choices across 1947 to
2005. Deleting the technologies instead was rejected - they carry the tech tree geometry,
the 1980 bookmark research list, 741 `has_tech` references and the preset era pacing.

**A bookmark chassis holds exactly one generic design.** Where two generations share a
tier, the earlier one owns it: it keeps the generic bookmark design and supplies the
superstructure module both generations mount. The later generation keeps every national
preset and has no generic design. Without the shared module the same named design would
exist twice on one chassis with different loadouts, which is what the engine cannot
represent. `Standard APC 1965` and `Standard IFV 1955` are therefore deleted.

**The archetypes survive the cutover.** Only the designer hulls retire.
`mechanized_equipment` and `mechanized_heavy_equipment` keep their legacy rows for non-NSB
games, lose every designer surface, and revert to `type = mechanized`; `armor` was only
ever there to route the NSB hulls to `tank_designer_view`. The seven mechanized sub-units
keep `need = { mechanized_equipment = N }` unchanged - connecting designer output to
battalions is phase 5.

**Carrier stat values are authored, not derived from a frozen contract.**
`Balance_Target_Manifest.md:52` puts all 18 mechanized rows explicitly out of scope and
the living balance CSV carries no carrier module rows, so the only source of truth was the
equipment file. The ladder reproduces it exactly. This retires the claim that the
restructure renegotiates 18 of 40 frozen rows.

### Carrier battalions, ratified 2026-09-12

**One battalion serves both profiles; the legacy equipment moves to it.** The six carrier
battalions keep their ids and move onto the carrier role families, and all 18 legacy
carrier rows move into those same families. This is the shape the mod already uses for
tanks, where `lt_equipment_1..6` carry `archetype = light_tank_chassis` and `light_armor`
therefore draws designer and legacy equipment alike. Splitting the battalions per DLC
profile is rejected: `mechanized_infantry` appears 2,366 times across 294 OOB files, and
the mod deliberately keeps NSB and non-NSB division templates identical.

**`need`, `essential` and `transport` are one decision, not three.** `essential` is what a
battalion must hold to read as combat-ready. Rewiring `need` and `transport` while leaving
`essential` on the retired family would leave every rewired battalion silently registering
as unequipped, which is invisible in the files and obvious only in game.

**Relocated rows state every stat explicitly.** A row moved between archetypes silently
inherits the new archetype's base values, so each relocated row writes out the thirteen
stats the retired archetype used to supply. The relocation is required to be stat-neutral
and is verified numerically, not by inspection.

**The retired archetypes stay as empty shells.** `mechanized_equipment` and
`mechanized_heavy_equipment` keep no members. They are not deleted because roughly 180
military industrial organization, idea and decision entries name those archetype ids, and
because the mod already ships exactly this shape: `lt_equipment` has had zero members
since the legacy tank rows were reparented.

**Legacy carrier rows live in `x_tank_chassis.txt`.** Load order, not preference: the role
archetypes do not exist until that file is evaluated, so `mechanized.txt` cannot name them.
Vanilla puts its own plain members of duplicated archetypes in the same place.

**Artillery, AA and tank destroyers are out of scope here.** Their legacy battalions still
consume standalone families, and converging them is the artillery/AA restructure the owner
deferred. The eight role brigades that already exist are technology-gated through
`enable_subunits`, which is the normal pattern - `active = no` on a sub-unit is not a
disabled unit, and 59 of the mod's 91 land sub-units carry it.

### Heavy carrier battalions, ratified 2026-09-17

**Owner ruling, and it closes the Heavy APC / Heavy IFV question `STATUS.md` Finding 27
left open.** The four Infantry Carrier battalions map one-to-one onto the four carrier
role families, and the naming follows the hull rather than the vehicle generation:

| Battalion | Id | Role family | Group | Enabled by |
| --- | --- | --- | --- | --- |
| Mechanized Infantry | `mechanized_infantry` | `light_tank_apc_chassis` | `mobile` | `mechanized_infantry` (1944) |
| Heavy Mechanized Infantry | `heavy_mechanized_infantry` | `medium_tank_apc_chassis` | `mobile` | `mechanized_infantry` (1944) |
| Armored Infantry | `armored_infantry` | `light_tank_ifv_chassis` | `armor` | `mechanized_heavy_infantry` (1947) |
| Heavy Armored Infantry | `heavy_armored_infantry` | `medium_tank_ifv_chassis` | `armor` | `mechanized_heavy_infantry` (1947) |

**APCs are mechanized, IFVs are armored.** The two existing ids are kept, so the ruling
costs zero OOB edits - `mechanized_infantry` appears 2,366 times across 294 OOB files and
`armored_infantry` 977 times across 163 - and the only change to them is that
`armored_infantry` moves from `group = mobile` to `group = armor` and is relabelled
"Armored Infantry". Its old label was "Heavy Mechanized Infantry", which the new Heavy APC
battalion now carries, so the localisation move is a transfer rather than an invention.

**The battalion unlocks with its hull, not with its historical debut year - corrected
2026-09-17 the same day.** The first ruling gated Heavy Mechanized on `mechanized_infantry8`
(1985) and Heavy Armored on `mechanized_heavy_infantry8` (2005), the two chains' own Heavy
APC and Heavy IFV years from the xlsx `Roles` tab. Owner QA showed why that is wrong in
practice rather than in principle: `medium_tank_apc_chassis_0` and `medium_tank_ifv_chassis_0`
unlock with `nsb_iw_armored_vehicles` in 1939 and every later tier tracks the MBT ladder, so
the gate left an NSB player producing Heavy APCs for up to 46 years with no battalion to field
them in - Finding 27's designable-but-unusable class, time-shifted.

**The enabler is the sibling's own technology, chosen by evidence rather than by architecture.**
An intermediate attempt put both entries on `nsb_iw_armored_vehicles`, which looked right - it
is the technology that enables the hull tiers, and 463 country-history files grant it - and
owner QA showed neither battalion. So each heavy battalion now sits in the same
`enable_subunits` block as its light sibling: `mechanized_infantry` (1944) for Heavy APC and
`mechanized_heavy_infantry` (1947) for Heavy IFV. **Those two blocks are the only enablers in
this mod with direct in-game proof**, because the battalions they enable are visible in the
owner's QA screenshots. Prefer a proven enabler over an architecturally tidy one; see
`STATUS.md` Finding 31 for why the NSB root's behaviour is unobservable from the unit lists.
**A battalion is gated by the hull that equips it, not by the vehicle generation its name
refers to**, and 1944/1947 is earlier than every medium carrier tier a player can field, so the
principle holds. No new technology is authored either way, and the designer hull tiers still
carry the generation years.

**The NSB-only ruling is void, and the legacy ladders it deferred were mandatory.** The
2026-09-17 ruling accepted Heavy APC and Heavy IFV being equippable on No Step Back only,
because all 23 relocated legacy carrier rows had landed in the two light roles and authoring
heavy-carrier ladders looked like optional new content. The missing rows turned out to be the
reason the two battalions never appeared on **either** profile - a role family with no plain
member cannot satisfy a `need` at all, see the amendment under the three-hull restructure. Four
plain rows now serve the two carrier families (`heavy_apc_equipment_1..3`,
`heavy_ifv_equipment_1`), gated `NOT = { has_dlc = "No Step Back" }` on the legacy pattern, so
**all four carrier battalions serve both profiles** and the 2026-09-12 symmetry rule holds
everywhere. The other rejected option - gating the battalions behind NSB hull technologies -
stays rejected; it would have hidden the defect rather than fixed it.

**Stats extend the light sibling, they do not restate it.** Each heavy battalion copies its
light sibling and pays for the medium hull with +0.02 supply consumption, +0.25 weight and
2 more strength: Heavy Mechanized 0.16 / 1.25 / 32 against Mechanized 0.14 / 1.0 / 30, and
Heavy Armored 0.18 / 1.5 / 37 against Armored 0.16 / 1.25 / 35. Terrain tables, manpower,
training time, organisation and combat width are the sibling's unchanged. This is authored
balance, not a measured envelope - no live test backs it.

### Carrier armour envelope, ratified 2026-09-12

**No carrier may exceed 70% of the same-year medium tank hull's armour, on either DLC
profile.** Owner ruling, and it reaches both the eight designer IFV rungs and the eight
relocated legacy rows rather than only the NSB path. The inversion being fixed was
inherited, not introduced: a 2005 IFV carried 80 armour against the 2010 MBT's 75, and
`mechanized_heavy_equipment_8` carried the same 80, so the cutover reproduced it faithfully
and nothing flagged it. Same-year means the newest medium tier whose year does not exceed
the carrier's, the same not-later-than-year rule the tier mapping uses.

**Scope corrected 2026-09-17: the cap is LIGHT-HULL-ONLY.** Owner ruling. As originally
written the rule was unsatisfiable for the two medium carrier families, not merely tight: the
cap was authored when both carriers lived on the **light** hull, where base armour is 5 to 27.5
and a 70%-of-medium ceiling bites. Heavy APC and Heavy IFV are medium-hull roles, so they
inherit the medium hull's own 30/35/40/45/50/55/60 - which is 100% of the number the cap takes
70% of. Measured across tiers 0-6 with the lightest role-admitted armour module and the
lightest superstructure, APC breached by 9.5 to 14 and IFV by 16.5 to 21 at **every** tier; no
legal module combination complied.

**A medium-hull carrier is therefore capped by its own hull, not by 70% of it.** That preserves
the rule's actual intent - the inversion it was written to kill was a carrier out-armouring the
tank it rides on - while letting the ratified Infantry Carrier taxonomy ship complete. The two
rejected readings: keeping the cap and abandoning the medium carriers' starting designs would
leave two of twelve role families permanently half-live, and restating it as 70% of the
same-hull tank still fails, because a role inherits its hull's armour before any module applies.

Consequence, applied the same day: the fourteen Heavy APC / Heavy IFV bookmark starting designs
are integrated, so all five previously uncovered role families now have one. See `STATUS.md`
Finding 35. The validator's `carrier_armour_cap_errors` continues to check the light-hull
carrier rungs and the relocated legacy rows, which is exactly the scope this correction defines.

IFV armour therefore becomes 22 / 25 / 28 / 31 / 35 / 39 / 44 / 49 across the eight
generations, against caps of 28 / 31.5 / 31.5 / 35 / 38.5 / 42 / 45.5 / 49. APC armour is
untouched - at 15 to 40 it was never near the cap - and so are carrier cost and speed. An
IFV keeps its cost while losing armour because phase 7 hands it back the defensive profile
below, which is where a troop carrier's value actually sits.

**The carrier defensive profile is restored, superseding "they adopt the hull curve".**
The phase 4 ruling deferred `defense` and `breakthrough` to phase 7 on the grounds that
reproducing them meant a module adding 39 defense. That is exactly what ships now, and the
reason is that the hull curve had the carrier backwards: every light hull tier is
`defense = 6`, `breakthrough = 20`, which is a tank's profile, while a carrier's is
`defense = 11..45`, `breakthrough = 3..18`. Putting a troop carrier on a breakthrough curve
is not a neutral simplification, it deletes the thing that distinguishes it. The rungs now
carry both stats, with negative breakthrough deltas, reproducing the retired chassis rows
exactly.

**Hardness is set once on the role root and never added by a module.** `light_tank_apc_chassis`
sets 0.5 and `light_tank_ifv_chassis` 0.6, the legacy values, replacing the 0.3 / 0.5 the
cutover left. The rungs' 0.025-to-0.125 hardness adds are deleted rather than rebalanced:
with `for_each ... hardness = { set }` already deciding the family value, a module add is an
undeclared second authority over the same stat.

**Stat multipliers are banned on the rungs.** Three rungs carried an undocumented
`multiply_stats` 5% bump on armour or speed, which silently broke the hull-tier-plus-module
arithmetic every envelope check is written in. Empty `multiply_stats` blocks are shipped
style on eleven rungs and stay; what is banned is a multiplied value.

`reliability` and `fuel_consumption` stay on the hull curve. Neither inverts anything - a
carrier with hull reliability and zero fuel draw is not stronger than a tank in any way the
player can exploit - and reopening them would mean authoring numbers no evidence supports.

### Marine transport, ratified 2026-09-12

**`mechanized_marine` consumes `light_tank_apc_chassis`; every APC is a marine transport.**
Owner ruling, taken against the three priced options in Finding 15 and with one of them now
dead. A selective amphibious designer role is not buildable at all: the usable role token
vocabulary is exactly five and all five are spent - `anti_air`, `anti_tank`, `artillery`,
`amphibious` on APC, `flame` on IFV. There is no sixth token and no mechanism to register
one, so "amphibious as a designer role" is closed by the engine, not deferred.

What made the cheap option work is the restructure: `light_tank_apc_chassis` is a
`duplicate_archetypes` root, and Finding 15's measured rule is that `need`, `essential` and
`transport` resolve a family. A role root is a family, so the sub-unit can name it. The
alternative still standing was a sixth standalone designer family - archetype, hull tiers,
pictures, blueprints, unlocks, presets - and the owner declined to spend that for
selectivity.

**The five marine rows relocate into the APC role family**, exactly as the 18 legacy
carrier rows did in phase 5: every stat stated explicitly, `mechanized_marine_equipment`
kept as an empty shell because MIO, idea, focus and country-leader entries name it, and the
rows placed in `x_tank_chassis.txt` for load order. Their ids do not change, so the
`amphibious1..5` technology grants, the 18 OOB references and the stockpile grants all keep
resolving. Their armour comes down under the same 70% rule: 24 / 31 / 35 / 42 / 49, from
24 / 36 / 48 / 64 / 80.

**`mechanized_marine` stays `active = no`.** The ruling changes what marines consume, not
how they are unlocked; the technology gate is untouched and the validator still asserts it.

## Architecture

**SUPERSEDED 2026-09-10 by the three-hull restructure above. Kept for provenance.**
~~**APC and IFV are standalone designer families**, not roles on the light and medium
tank hulls. Superseded 2026-09-07 on evidence: the drawio `[REFERENCE] Whole Tech Tree`
mechanized column specifies a dedicated ladder separate from every tank hull column.
Light Mech is the APC line (`mechanized_equipment` / `apc_chassis_*`); Heavy Mech is
the IFV line (`mechanized_heavy_equipment` / `ifv_chassis_*`).~~ The owner reversed this
on 2026-09-10: carriers are light-hull and medium-hull roles.

**Heavy APC and Heavy IFV are a medium hull generation**, not more tiers on the
light-hull families. Both the xlsx `Roles` tab and the drawio AFV Hulls page place them
there (Heavy APC 1985 off Second Gen MBT, Heavy IFV 2005 off Second+ Gen MBT). Still
true, and the restructure implements it as `medium_tank_apc_chassis` /
`medium_tank_ifv_chassis` rather than as hull tiers.

**Tier count and years come from the frozen manifest, not the diagram.** 8+8 at
1947/1950/1960/1965/1975/1985/1995/2005, from the 18 mechanized envelope rows. The
diagram's seven-tier decade cadence is a sketch. Do not "correct" the years to it.

**`mechanized_heavy_equipment_3` stays at 1955.** The workbook's 1960 is a deliberate
year exception and is not permission to alter the stats or the workbook. `nsb_ifv_hulls2`
carries `start_year = 1955` and the `@1955` tree row so tree, tooltip and hull agree.

**CORRECTED 2026-09-10 to 20 positions by the engine cap on custom module slot windows.
Everything below about the expansion still holds except the count and the trailing slot.**

**The designer expands from 15 to 21 positions.** Ratified 2026-09-09, superseding
"the 15-position designer is final". The target is drawio page 8
`[REFERENCE] Tank Designer Composition`, which lays out nine named slots - Gun, Turret,
AP Ammo, HE Ammo, Aiming, Optics, Suspension, Armour, Engine - plus `Slot 1..12`, i.e.
21 positions. `archive/Balance_Sources.md:148-151` had ruled that page "a sketch, not a
specification, and the shipped 15-slot layout in interface/tank_designer_view.gui is the
thing that exists"; the owner reversed that on 2026-09-09. The sketch is now the
contract and the shipped 15-slot layout is the **unfinished** state - see `STATUS.md`
Finding 6.

- Slot set: the five mandatory slots plus `tank_special_slot_1..16`. Names stay
  `tank_special_slot_N`; `special_type_slot_N` is still prohibited in tank content
  (the plane-airframe collision fixed by `368fa4815c`).
- Specialized: slot 1 anti-tank ammunition, slot 2 HE ammunition, slot 3 aiming,
  slot 4 optics. This splits today's "either ammunition in either slot" pair, and it
  costs no preset edits because the shipped presets already follow it: of 586 national
  blocks, slot 1 holds only `ap_*` (213 assignments, 373 `empty`) and slot 2 only
  `tank_he_*` (213 assignments, 373 `empty`).
- Free: slots 5-16 accept every remaining special category and every category authored
  later. Their GUI labels are `Slot 1`..`Slot 12` per the sketch, so the label number is
  deliberately offset from the slot id. Do not "fix" that by renumbering the slots.
- The same 21-position layout applies to all five archetypes. `mechanized.txt:37-164`
  and `mechanized_heavy.txt:28-42` already mirror the tank special-slot names and
  category map and diverge only in mandatory armament/turret categories, so this is one
  change applied five times, not two designs.

**The 21 positions render 7 / 7 / 7 with the middle row over the blueprint.** Ratified
2026-09-09. `equipment_modules` stays 515x350 and `equipment_preview` keeps its 508x248
blueprint, so no art is rescaled or cropped: positions 0-6 on `@fixed_btn_mod_row_0 = 1`,
7-13 on the existing `@fixed_btn_mod_row_middle = 180` promoted to a full row, and 14-20
on `@fixed_btn_mod_row_1 = 300`. Frames stay 76x47
(`interface/equipmentdesignerview.gui:1743-1751`) and the seven existing column macros at
pitch 73 end at exactly 515. Two alternatives were rejected: the sketch's literal 6x3 +
3 geometry, and a 3x7 grid above the blueprint. Both force the preview down to <=162px,
which buys an art pass and no capacity. Overlaying frames on the blueprint is already
this panel's layout language - slot 14 sits at (439,180) today, and
`tag_icon_bg`/`niche_button` overlay the same rectangle (see "Retracted after
measurement").

**Gate: 21 positions is beyond anything vanilla ships and must be confirmed in game
before any content depends on it.** The vanilla tank designer declares
`pos_custom_module_slot_window_0..8` for 5 mandatory + 4 `special_type_slot_N` slots, and
the highest index anywhere in the vanilla interface files is 8. No engine-side cap is
documented and none was found; the mod's own 15 positions prove the count is not fixed at
9. That makes 21 plausible, not verified.

**Free slots keep today's tradeoffs through shared-budget exclusivity groups, pending an
engine test.** Slot specialization is currently the only thing making computing compete
with radar, allowing one loading system, and making active protection compete with an
armour layer. Twelve free slots delete all of that unless one `module_count_limit` block
can hold several `category` entries as a shared budget. **That form is unverified:**
vanilla ships no multi-category limit block anywhere under
`common/units/equipment/`, and all 18 blocks on the mod's own archetypes are
single-category `count < 2`. Test it in the same pass as the 21-position render. If the
engine rejects a shared budget, the fallback is per-category `count < 2` only, and the
consequence - up to 12 specials mounted where the frozen envelopes assumed 10
specialized picks - is an explicit balance-recalibration item, not a silent change.

**Shipped 2026-09-09 with the per-category fallback, not the shared budgets.** The
multi-category test was not runnable to a positive answer: a log diff can prove the
engine *rejects* a multi-category `module_count_limit`, but engine silence cannot prove
a shared budget is enforced rather than parsed and ignored, and that distinction needs
a human in the designer. So the ratified fallback shipped - one single-category
`count < 2` per special category, on all five archetypes, 18 each. APC and IFV were
missing seven of those limits before this pass (four ammunition, three loader); the
three loader limits are load-bearing, because twelve free slots would otherwise let a
carrier mount three loading systems. The validator now rejects a multi-category limit
block outright, so the unverified form cannot be reintroduced by accident. Authoring
the shared budgets remains open and still requires a live enforcement test.

**Positions above 8 are confirmed in game.** Ratified gate cleared 2026-09-09 by the
owner's designer capture: the 7 / 7 / 7 layout renders with the middle row over the
blueprint, and the top row reads turret, gun, suspension, armour, engine, AP
ammunition, HE ammunition - so both the 21-position layout and the slot 1 / slot 2
ammunition split are live. The gate is fully closed: after the blueprint fix below the
owner re-checked in game and confirms all 21 slots load, and the live `error.log`
carries zero `Could not find "tank_special_slot_*"`, zero `Requested GUI element not
found` and zero `containerwindow.cpp` lines with the designer open, against 85
slot-lookup failures on the pre-fix boot. **21 positions is now verified, not
plausible** - do not reopen it as an engine risk.

**The 106 per-hull blueprint files are a sixth surface, and they are hand-enumerated.**
Discovered 2026-09-09. Every file under `interface/equipmentdesigner/tanks/` lists the
slot names itself inside its `module_slots` window. A slot the archetype declares but a
blueprint omits produces `containerwindow.cpp: Could not find "tank_special_slot_N" in
window module_slots` and a `Requested GUI element not found` assertion, but **only once
that specific hull's designer is opened** - so no static check and no ordinary load test
sees it. All 106 now declare `tank_special_slot_1..16`; the validator pins the file
count and the exact ordered slot list per file. The 147 unshadowed vanilla blueprint
files were left alone: they all belong to chassis families this mod removed
(`amphibious_tank`, `modern_tank`, `super_heavy_tank`, `land_cruiser`, and the deleted
`*_amphibious` roles). Any future slot change must touch all 106 again.

**Slots are to be locked per hull, not uniformly free.** Owner direction 2026-09-09,
refining the free-slot rule above rather than replacing it. 21 positions on all five
hulls is final; what is not final is that all five share one free-list. Specialized
modules that only some hulls may carry - amphibious drive on APC and IFV, not on
medium, MBT or heavy - need per-hull slot eligibility. The shipped identical free list
is correct only while every free-list category applies to every hull, so the lock model
must land in the same pass as the first hull-restricted module. Authoring such a module
against the current uniform list would silently make it mountable everywhere.

**The two owner mockups are the source for the unbuilt families.** Supplied 2026-09-09
and now the authority for their ladders, superseding "invent the whole tree":

- *Night and thermal vision* sits on the optics/aiming page as a four-step ladder off
  the base optic sights: First Gen Night Vision (off Telescopic/Periscopic Sight,
  alongside Sterioscopic Sight With Optical Rangefinder), Second Gen Night Vision,
  Third Gen Night Vision, then Thermal Vision. The stat values are still invented and
  still fall under the "recorded as authored" rule - the mockup fixes the shape and the
  prerequisites, not the numbers.
- *Special Capabilities* is its own dated column: Amphibious Drive 1940; OPVT,
  Underwater Driving Capability and Dozer Plow 1945; Log (+2% reliability) 1950;
  Anti-Mine Plow 1955 off Dozer Plow; Paradrop Capability 1960; Anti-Mine Roller 1965
  (KMT-5); Integrated Trench-Digging Plow and a second Anti-Mine Plow 1970; Anti-Mine
  Roller With Electro-Magnetic Coils 1980 (KMT-7 EMT). Amphibious Drive and Paradrop
  Capability are hull-restricted by nature and are the reason the per-hull lock model
  above is a prerequisite rather than a follow-up.

**The per-hull lock is a module attribute, not a slot attribute.** Established
2026-09-09 on engine evidence, and it supersedes any reading of the direction above
that implies per-archetype free-slot lists. A category is global while a free-slot list
is per archetype, so a category cannot restrict a module to some hulls: putting
amphibious drive in `tank_mobility_auxiliary` makes it legal on every hull whose free
slots take that category. The engine primitive is
`allow_equipment_type` / `forbid_equipment_type` / `forbid_equipment_type_exact_match`,
which key off the archetype's own `type = { ... }` set. Vanilla's `amphibious_drive`
uses exactly that shape, and the mod's own module file already uses these keys 49
times. The designer role roots supply the discriminators: `x_tank_chassis.txt:8-15`
makes `light_tank_aa_chassis` `type = { armor anti_air }` and `:18-25` makes
`light_tank_artillery_chassis` `type = { armor artillery }`, while the carrier
archetypes carry `mechanized` beside `armor`. Consequence: hull-restricted modules
need no GUI change, no new slot and no divergence between the five free lists. Do not
implement per-hull locking by forking the category lists.

**Thermal vision is already shipped; only night vision is missing.** Established
2026-09-09. `Optics_4..7` are localised "Thermal Sight I/II/III" and "Advanced Thermal
Sight" (`tank_modules_l_english.yml:951-957`) in category `tank_fcs_optics`, unlocked by
`nsb_optics4..7` at 1970/1980/1990/2005. The owner's mockup shows a three-step thermal
branch in a separate column; the shipped four steps in the optics column satisfy it. The
default is to leave them where they are and treat the mockup's thermal boxes as done -
splitting them into their own column would retarget four shipped modules, four
technologies and every preset that names them, for presentation only. Night vision is
the genuinely absent half: six technologies, column x18 free immediately right of the
panoramic sights at x16, two new tree rows (1960 and 2000).

**Paradrop capability cannot be a designer module.** Established 2026-09-09 by
searching the vanilla module directory: no module anywhere carries
`can_be_parachuted`, `parachut*`, `special_forces` or `marines`. The only
capability-bearing vanilla module is `amphibious_drive`, and it works through equipment
types. So the mockup's Paradrop Capability box has no module mechanism - it must be a
sub-unit or technology property, or be dropped. Do not author it as a module.

## Owner decisions, 2026-09-09 (module content)

All four blocking decisions from the module content plan are answered. These are
ratified; do not reopen them.

1. **`Optics_4..7` are accepted as the thermal branch in place.** No new thermal
   column, no retargeting of the four shipped modules or their `nsb_optics4..7`
   unlocks. The mockup's thermal boxes are satisfied; its 1975/1990/2000 years yield to
   the shipped 1970/1980/1990/2005. Descriptions 42-45 attach to the existing modules.
2. **Amphibious follows the design documents, not an improvised role.** The proper
   amphibious role is whatever the design documentation specifies; that specification is
   the authority over any reconstruction from current script.
3. **Paradrop is restricted to light hulls and light vehicles only.** It is therefore
   hull-restricted in the Finding 9 sense. Since no module can carry a paradrop
   capability key, the capability itself must come from a sub-unit or technology, and
   the light-hull restriction is expressed with
   `allow_equipment_type` / `forbid_equipment_type` on whatever module or role carries
   it.
4. **AA ammunition overturns the legacy self-supplying-AA-gun rule.** The ratified
   position that AA guns supply their own attack and that SPAA variants carry no
   ammunition is **superseded**. An AA ammunition ladder is authorized. Consequences to
   settle in that batch: known inconsistency 10's "three SPAA variants deliberately
   carry no ammunition" no longer holds, and the validator's `needs_ammunition` AA
   exemption must be inverted rather than worked around.

**Engine and suspension year authority: the icon assets win.** Ratified 2026-09-09.
Where an icon year and its unlocking technology's `start_year` disagree, the icon year
is correct and the technology moves. This is one systematic decision, not eleven: gas
turbines `GT_0..3` icons 1960/1970/1980/2000 against techs
`nsb_gt_engines0..3` 1965/1975/1985/2005, and `GT_APU_0..3` icons 1960/1970/1980/2000
against the same four technologies. Also covers the combustion 1939-versus-1940 case.

**Experimental 4-Track Suspension is authorized** as described in the mockup, including
its "Opened by 1955 H Tank" prerequisite - a heavy-hull-gated unlock rather than a
free-standing technology.

**The module technology folder is visually clipped at x=16 and must be widened before
any column is added there.** Established 2026-09-09: across all 102 technologies in
`nsb_armor_modules_folder` the distinct x columns are
-8, -6, -4, -2, -1, 0, 2, 4, 6, 8, 10, 12, 14, 16, so x=16 (`nsb_pano_sight0..2`) is the
rightmost that has ever rendered, and the owner reports the tree is cut off there. The
night-vision column at x=18 therefore depends on a GUI change in
`interface/countrytechtreeview.gui` first. Per `GOTCHAS.md` the layout must be measured
rather than inferred from element names before any value is changed.

## Owner decisions, 2026-09-09 (gated-item batch)

These six decisions close the gated-item batch. They are ratified and must not be
reopened as unresolved implementation questions.

1. **Amphibious carriers are deferred.** Defer the whole batch; the three priced
   options remain open: a real sixth designer family, rejected carrier-member renaming,
   or APC-wide marine transport.
2. **Paradrop and hull-size discrimination use `light_armor`.** The light family is
   now `{ armor light_armor }`; any new light-family role root must carry the token.
   No paradrop consumer is authored yet.
3. **Artillery/AA is deferred entirely.** This includes widening the module-unlock
   provenance boundary.
4. **The tech-tree clip is fixed by moving two gridbox origins.** Move
   `nsb_tank_design_tree` from `x = 3600` to `x = 1650` and `nsb_armor_tree` from
   `x = 2400` to `x = 950`; technology coordinates do not move. The 3187 ceiling is
   empirical, not an engine constant.
5. **Slot-budget debt is accepted.** Keep the per-category fallback and its recorded
   debt; do not replace it with the unverified shared budget. Any future re-cut edits
   the frozen 40-row manifest.
6. **Major-country `Petrol_1` bootstrap is implemented.** Grant `nsb_engines0` to
   USA, SOV, FRA, ENG and WGR. Keep generic fallback recipes on `Petrol_0`; reroute
   only the tag-exclusive USA `M47 Patton` preset to `Petrol_1`.

**Standing rule: a new NSB armour technology dated 1980 or earlier is incomplete until
it is added to `cwic_major_tank_research_1980`.** That effect must grant every tank
technology with `start_year <= 1980`, and the validator fails with "1980 tank research
coverage differs" otherwise. It caught this twice on 2026-09-09 - once for
`nsb_night_vision0..2` and once for `nsb_special_capabilities0..5`,
`nsb_suspension_multi_track` and the migrated gas turbines. The effect lives in
`common/scripted_effects/CWIC_tank_bookmark_research.txt`. Treat updating it as part of
the definition of adding the technology, not as a follow-up.

**A new category's cost depends on whether its slot is mandatory or free.** Established
2026-09-09 by `tank_suspension_multi_track`. A **free-slot** category must be added to
the free list of all five archetypes AND given a `module_count_limit { count < 2 }`, or
it silently stacks. A **mandatory-slot** category - suspension, armour, engine, turret,
main armament - is added only to that slot's `allowed_module_categories` on all five
archetypes and must NOT get a count limit, because a mandatory slot holds exactly one
module. Do not reflexively add a limit for every new category.

**Brace balance and byte checks are not a syntax check, and a passing validator is not
a passing parse.** Established 2026-09-09 the hard way: a single missing `=` in
`tank_designer_view.gui` (`y@fixed_btn_mod_row_0`) aborted the parse of 125 children of
`tank_designer_view` and crashed every tank, APC and IFV designer with SIGFPE, while
brace balance was 0, all bytes were clean, and the validator reported
`21 designer slots checked` - because its slot regex matched the broken line. Any pass
that rewrites script or GUI assignment blocks MUST verify token shape. The validator now
enforces this for `position`/`size`/`margin` blocks in the designer GUI and all 106
blueprint files. Load-time parse errors appear with `no_game_date`, so a plain boot
confirms them with no gameplay required - do that after any GUI edit.

## Amphibious as a designer role, ratified 2026-09-09 - CLOSED 2026-09-13

**Do not implement any of this.** The owner ruled 2026-09-13 that mechanized marines and
paratroopers get no custom vehicles and that every APC and IFV serves them equally, so there is
no amphibious vehicle class and no amphibious designer role. See "Final role-token map". The
section is kept because its mechanism analysis - modules are restricted to a role, roles do not
emerge from modules - is correct and load-bearing elsewhere.

**Owner ruling, superseding every earlier amphibious statement** including
`REFERENCE.md:129-131`'s "amphibious mobility module" and the "eligible mechanized
designs" wording: the replacement for the legacy mechanized amphibious vehicle is an
APC/IFV design that gains the **amphibious designer role**, in the same way a tank's main
armament determines whether it is a gun tank, SP artillery, SPAA, tank destroyer or flame
tank. Where earlier notes conflict, this wins.

**The mechanism is real and already in use here - with the causality the other way
round.** A module does not create a role; the role exists as an archetype and the module
is *restricted to* it, which produces the same player experience. Measured:
`tank_anti_air_cannon` carries `allow_equipment_type = anti_air` plus
`forbid_equipment_type_exact_match = armor`, and `tank_low_p_cannon0` carries
`allow_equipment_type = artillery`. The roles themselves are cheap `duplicate_archetypes`
entries - `x_tank_chassis.txt:8-15` is six lines declaring `light_tank_aa_chassis` as
`archetype = light_tank_chassis`, `type = { armor anti_air }` - and the engine derives
every tier from the parent family, which is why `light_tank_aa_chassis_1` is legal though
never declared.

So the amphibious implementation is two small pieces plus rewiring:

1. Carrier amphibious role roots in `x_tank_chassis.txt`, e.g. `apc_amphibious_chassis`
   with `archetype = mechanized_equipment` and `type = { armor mechanized amphibious }`,
   and the IFV equivalent.
2. An amphibious drive module gated `allow_equipment_type = amphibious`, so it is
   mountable only on those roles and nowhere else.
3. `mechanized_marine`'s `need` / `transport` point at those **role chassis**, not at
   `mechanized_equipment`. This is what makes the capability selective and it removes the
   objection recorded in Finding 14: an ordinary APC is not a marine transport, only an
   amphibious-role APC is.

Finding 14 stands as the reason a module alone cannot do it - sub-units consume equipment
ids and no land sub-unit can test for a fitted module - but its "expensive role rebuild"
framing is downgraded: `duplicate_archetypes` makes the role itself nearly free. The real
cost remains the six validator contracts and the `mechanized_marine` `active = no`
assertion, all of which must change consciously.

**Module-to-module compatibility does not exist in this engine, and the design must not
assume it.** The complete tank-module vocabulary for restricting a module is three keys,
confirmed by scanning the whole vanilla module directory: `allow_equipment_type` (23
uses), `forbid_equipment_type` (4) and `forbid_equipment_type_exact_match` (6). There is
**no** key expressing "this module requires that module" or "this module conflicts with
that module" for land equipment; `need_equipment_modules` exists only on ship hulls
(`battlecruiser.txt:8-12`). Consequences for any future module-limitation design:

Restriction by **hull or role** is expressible, via the archetype `type` set.
Restriction between **individual modules** is not. The only levers are which category a
module sits in, the per-category `count < 2` limits, and the still-unverified
multi-category shared budget.
Restriction by **hull size** is now expressible for light versus medium/heavy:
`light_tank_chassis` is `{ armor light_armor }`, while the medium and heavy archetypes
remain `{ armor }`. Any new light-family role root must include `light_armor`.

**Attempted 2026-09-09, reverted: `duplicate_archetypes` cannot give the carrier
families clean role tier ids.** The role-as-designer-role design above is right; this is
a naming constraint on the mechanism, discovered by boot testing and not visible
statically.

`duplicate_archetypes` derives a role's tier ids by substituting the parent archetype's
name inside each member's id:

| Family | Archetype | Members | Derived role tier |
| --- | --- | --- | --- |
| tanks | `light_tank_chassis` | `light_tank_chassis_0..9` | `light_tank_aa_chassis_3` - clean |
| carriers | `mechanized_equipment` | `apc_chassis_0..7` | `apc_amphibious_chassisapc_chassis_0` - concatenated |

The tank case works because the member id **contains** the archetype id. The carrier
members were deliberately renamed to `apc_chassis_N` / `ifv_chassis_N`, which do not
contain `mechanized_equipment`, so the engine falls back to concatenating the role id and
the member id. A live boot produced 24 error lines, eight of them
`apc_amphibious_chassisapc_chassis_N is an equipment type ... not in script enum`, plus
13 `Failed to change role to "Unknown"` before the `for_each variant_name
find_and_replace` was removed. Renaming the role does not help - the mismatch is between
the archetype id and the member ids, not in the role id.

The whole attempt was reverted rather than shipped: the validator passed at
`1318 technologies, 290 tank modules` with malformed equipment ids in play, which is
Finding 11's lesson repeating in a new place. Post-revert boot is clean - zero
`amphibious_chassis`, zero `Failed to change role`, zero `script_enum` complaints.

**The explicit-declaration route is withdrawn, 2026-09-09.** It read: declare the
amphibious carrier role chassis explicitly, sixteen equipment blocks in the style of the
existing `apc_chassis_0..7` and `ifv_chassis_0..7` members, each carrying
`type = { armor mechanized amphibious }`, instead of deriving them. It does fix the
id-concatenation defect above, and it is **still wrong**, because it cannot supply the
marine sub-unit - see `STATUS.md` Finding 15. A land sub-unit's `need` and `transport`
resolve an equipment *family*: every such value in the whole vanilla `common/units/`
tree is an `is_archetype = yes` archetype or a `duplicate_archetypes` role root, and no
vanilla sub-unit anywhere names a plain numbered member. Hulls declared as members of
`mechanized_equipment` are therefore unnameable in `need`; the only nameable id is
`mechanized_equipment` itself, which makes **every** APC a marine transport - the
unselective option Finding 14 rejects.

What survives from that route is only the module half: the `amphibious` token in an
archetype's `type` set still gates modules through `allow_equipment_type`.

**The three surviving options, priced.** No route is ratified; the owner picks one.

1. *A real sixth designer family* - amphibious carrier hulls under their own
   `is_archetype = yes` root, which is vanilla's own shape
   (`amphibious_mechanized_equipment`, `amphibious_tank_chassis`). The only route that
   is both selective and proven, and the honest cost is a full family - archetype block
   with the 21-slot layout, hull tiers, pictures, blueprint GUI, unlocks, presets, and
   the six validator contracts in Finding 14. This is **not** the "nearly free"
   `duplicate_archetypes` role assumed above.
2. *Rename the carrier members* to contain `mechanized_equipment` so derivation works -
   **rejected**, unchanged: those ids appear across 586 national presets, the generic
   bookmark variants and the OOB migration.
3. *Accept APC-wide marine transport* - cheap, unselective, needs an explicit ruling.

Also established while attempting this, and it is why the module half is not enough on
its own: a single sub-unit cannot accept either the legacy equipment or a designer role
chassis. `transport` is one scalar id and `need` entries are conjunctive, so listing both
`mechanized_marine_equipment` and an amphibious role chassis makes the sub-unit require
**both** at once. Supplying marines from a designer carrier therefore needs a **second**
sub-unit consuming the role chassis, leaving legacy `mechanized_marine` intact for
non-NSB players - which touches division and AI templates and is its own decision.
`CWIC-Special-Units.txt` was left byte-for-byte unchanged.

Both columns are now partly built. Night vision shipped 2026-09-09 as
`nsb_night_vision0..5` with six `tank_fcs_optics` modules; the thermal half was already
shipped as `Optics_4..7`. The Special Capabilities column shipped the same day as
`nsb_special_capabilities0..6` with ten modules, plus `nsb_suspension_multi_track` and
`Four_Track_0`. Still unbuilt from that column: Amphibious Drive, Paradrop Capability,
OPVT, Underwater Driving Capability and Modular Construction - the first four for want
of an engine mechanism, the last for want of a category. All authored stats in both
columns are invented and recorded as authored; `Log_0`'s +2% reliability is the sole
documented value.

**Free slots are not enumerated in presets.** Vanilla proves optional slots may be
omitted: `history/countries/GER - Germany.txt:1097-1108` creates `light_tank_chassis_0`
with the five mandatory slots and one special, nothing else. So the shipped 586 national,
40 generic and 16 export creation blocks stay valid as written - their 8,790 + 160 + 80
special-slot assignment lines need no rewrite - and the validator moves from "exactly 15
assignments" to "five mandatory present, specials a subset of the declared set". Adding
six slots is therefore a contract change in one archetype family plus the validator, not
a mass content migration.

**Legacy mechanized ladders retire by DLC-gating production, not by removing
technologies from `nsb_armor_folder`.** Dropping the folder placement from
`mechanized_infantry*` and `mechanized_heavy_infantry*` would take four things with it:
their `enable_subunits` for `mechanized_infantry` and `armored_infantry`; the
cross-links feeding `light_tanks_3/4/5/6` and `amphibious1`; the `allow` gates on
`nsb_apc_hulls0` and `nsb_ifv_hulls0`; and 1144 `set_technology` sites in
`history/countries/` plus focus references in `USA_70s_Military.txt` and
`60s_Generic.txt`. DLC-gating keeps the technologies researchable and their sub-unit
activation intact while `can_be_produced` removes the legacy models from the NSB
production tab. `mechanized_equipment_1..2` must stay ungated - they are the
pre-designer WWII rows with no designer replacement.
*Blocker:* gating leaves an NSB bookmark start with no buildable carrier until a design
exists, so this depends on the presets and OOB migration landing first.

**Amphibious capability belongs in a mobility module on eligible mechanized designs.**
Do not remove the NSB legacy amphibious unlocks until replacement vehicles actually
supply the marine sub-units correctly. Three separate things must not be conflated:
the live legacy `amphibious1..5` technologies granting
`mechanized_marine_equipment_1..5`; the designer amphibious role, which was **deleted**
(rebuilding it is new work, not a restore); and the `mechanized_marine` sub-unit, which
is `active = no` with the validator asserting it stays that way. Any amphibious work
must change that assertion consciously.

**Night and thermal vision values are invented and must be recorded as authored.** The
design exists on drawio page 4; the workbook reserved a `Night & Thermal Vision Effects`
tab and left it empty. The mod has one orphan `night_vision` string in
`common/technology_tags/00_technology.txt:42` and nothing else.

**Artillery and AA gate legacy and designer paths by DLC**, preserving technology-based
sub-unit activation. The `support.txt` pattern `OR = { has_tech = legacy has_tech = nsb_* }`
already exists in the repo for exactly this. Source targets are frozen in `BALANCE.md`.

**Workbook is frozen; the CSV is the living balance mirror** with explicit reviewed
overrides.

## Producer resolution

A design's producer resolves as **producer, then creator, then owner, then the OOB
tag**, independent of token order. Both naming and bootstrap attribution use this rule;
neither source field is removed.

The old validator selected the first owner/producer/creator token, which disagreed with
attributing technology to creator/producer - for example DRY's forced request has
`owner = DRY creator = "CUM"`. Installed vanilla evidence settles it: `YUG_1939_nsb`
requests France's `FT mod. 31` with owner YUG and creator FRA, and France creates that
design.

Consequences already established by runtime testing:

- A tank bought from or designed by another tag is looked up on *that* tag. The chassis
  technology belongs in that country's bootstrap, not the loading country's. This is
  what made FRA, ENG and the `CAP`/`CUM` manufacturer bloc tags fail.
- Tech sets are scoped per bookmark. A 1949 bootstrap must not preload the 1970s
  chassis its country only sells in 1980.
- `CAP` and `CUM` sell tanks but never load an OOB, so they call the creator directly
  from their own history.
- Never rename all requests according to the country whose OOB file is being loaded.

The bootstrap ordering rule this depends on: an OOB-local `instant_effect` runs *after*
that OOB's own production, stockpile and forced-variant requests resolve, so a variant
created there is always too late. The bootstrap runs in country history immediately
before `set_oob`:

```
country scope
  -> set_technology for exactly the chassis technologies this bookmark needs
  -> cwic_create_starting_tank_variants = yes
  -> set_oob = <bookmark NSB OOB>
```

## Designer graphic database, ratified 2026-09-21, revised 2026-09-22 and 2026-09-23

**The tank designer graphic database is authored by this mod and must never be blanked again.**
A zero-byte file at a base game path is a deletion, not a fall-through. `00_tank_icons.txt`
carries CWIC's own pools; `validate_designer_graphic_db()` enforces it.

**It is generated, not hand-edited.** `CWIC Backup/tools/build_designer_graphic_db.py` writes
it; the validator fails if the file differs from the builder's output. Models already in the file
are carried over by the builder, so the icon rules can change without losing them.

**Keyed on the exact per-generation equipment type.** Keying the role archetype is NOT
sufficient and was wrong in the first pass: for a derived type such as
`light_tank_destroyer_chassis_3` the engine treats the hull as the archetype, and an archetype
pool outranks a family-type pool, so every role design kept plain tank hull art. A
per-generation type key outranks both.

**The art is the non-NSB technology library, matched to the NAMES on each hull - revised
2026-09-23.** Each role maps to one legacy sprite family (`light_tanks_N`, `main_battle_tanks_N`,
`heavy_tanks_N`, `spaag_N`, `light_sp_artillery_N`, `sp_artillery_N`, `heavy_sp_artillery_N`,
`tank_destroyer_N`, `atgm_carrier_N`, `mechanized_infantryN`, `mechanized_heavy_infantryN`). A
generation's Equipment Match is the legacy row the national names on that hull come from - the
`legacy_name_key` in the naming, carrier and research manifests - so a hull's picture and its
historical names share one row. `ROLES` in the builder carries the ladder explicitly per role.

The 2026-09-22 rule, nearest legacy YEAR, is superseded because it disagreed with the naming
wherever the hull ladder (1939/1942/1944/1950...) is offset from the legacy ladder
(1942/1944/1947/1950...). The owner found four on SOV by in-game and photo comparison on
2026-09-23: `BTR-40` carried `SOV_apc_2` (should be `_3`), `ZSU-57-2` `SOV_spaag_1` (`_2`),
`ASU-57` `SOV_tank_destroyer_1` (`_2`), `2S7 Pion` `SOV_sp_hv_art_1` (`_3`). The same offset gave
`M26 Pershing` and `T-44` the `mbt_equipment_0` (Sherman / T-34-85) row's art. The 2026-09-21
index-and-clamp pass is still wrong for the reason recorded then; the names are the index that
was missing.

- A generation with no national names takes the nearest tier by year, clamped between its named
  neighbours. An unnamed role (medium SPAA, Heavy APC/IFV, heavy TD) mirrors its named sibling.
- Heavy SP artillery 4 is the one hull where two rows compete (`heavy_sp_artillery_4` 3 names,
  `_5` 10 names). It takes `_4`: with `_5`, CUB/EGY/PER own `_4` art but no `_5`, drop to the
  `default` pool, and their own design's picture would not be offered.
- **Light TD** is `tank_destroyer_1` before hull 4 and the `atgm_carrier` ladder after. Non-NSB
  had no pre-ATGM light tank destroyer art.

**A country uses its own art only within 10 years of the target tier** (was: of the generation
year). Otherwise it gets no pool for that key and the `default` block's generic art for the tier
wins, rather than a country photograph thirty years out of date.

**Every pool offers alternates.** The first pool is the Equipment Match; a weight-0.5 pool lists
the rest of that country's family for that role, so the player can still pick another picture.
Weight outranks scope, so the alternates never displace the match.

**The `default` root is mandatory.** It carries every role and generation with generic art, so a
country with no art for a role gets that role's picture instead of falling through to the plain
tank hull. The validator requires it complete.

**APC and IFV carry icons - this REVERSES the 2026-09-21 "models only" rule.** Owner playtest
2026-09-22: `M3A1 Half-Track Mk0` showed `GFX_USA_light_tanks_3_medium` in the designer. With no
icon on the type key the designer fell through to the light hull family; the archetype picture
never reached the designer. Their icons are now the mechanized families themselves, which is the
same art the production tab showed, so nothing is lost. The validator fails if any role key
names an icon outside its own art family - the exact regression in that capture.

**`carrier_hull`, `carrier_hull_light` and `carrier_hull_super` are NAVAL families.** They are
aircraft carrier hulls for the ship designer, not armoured personnel carriers. A first pass on
2026-09-21 mapped APC and IFV onto them on the strength of the name alone and put aircraft
carriers in the tank designer. The contract fails on any `carrier_hull` reference.

**Scope is tanks only.** The plane, ship and HQ files in that folder carry the identical defect
and are deliberately left blank; restoring them is separate content work with an owner.

**Coverage is still uneven by country, and that is now harmless.** 97 TAG blocks carry their own
art where it exists; everything else resolves to the `default` block at the right generation.

**Role switching is not scripted and must not be.** The engine repaints from equipment type, and
`allow_equipment_type` / `forbid_equipment_type` on modules decide which roles a design may
switch to. APC being typed `flame` and IFV `rocket` means gun-armed tanks are blocked from those
roles until the gun is removed - vanilla's own behaviour for tank destroyers, and not a bug.

**Every national design names its icon explicitly, ratified 2026-09-22, revised 2026-09-23.** A
scripted `create_equipment_variant` without `icon` is shown the pool in the designer but does not
take it (owner QA, USA/SOV 1949). Vanilla sets `icon` on every scripted tank design, and so do
all 2,488 country-guarded blocks in the three preset/naming effect files. The value is derived,
not chosen, and since 2026-09-23 it is **the design's own legacy row**, not the hull's: the
builder's `art()` applied to the design's `legacy_name_key` tier (country art for that tier, else
its nearest within 10 years, else the generic art). Two hulls carry two carrier generations -
APC hull 4 (`mechanized_equipment_5`/`_6`, 76 countries) and IFV hull 3 (`_2`/`_3`, 32) - so
`BTR-60P` and `BTR-60PB` on one hull now show different pictures; one icon per hull could not.
Names with no art in the role family (11 marine rows) keep the hull's Equipment Match.
`validate_design_equipment_match_icons()` pins the icon AND that the designer pool for that type
offers it. Models are not set; the designer's "Default Model" stays dynamic.

**Every national design sets `show_position = no`, ratified 2026-09-23.** The engine defaults it
on and appends the design's position, so every preset read `BTR-40 Mk0`. Owner live test on
`ZSU-37` (SOV): `show_position = no` removes the suffix. All 2,488 blocks carry it after
`parent_version = 0`; the same validator fails a block without exactly one `show_position = no`.
The 16 obsolete `CWIC Export` designs in `CWIC_tank_focus_effects.txt` are out of scope and
unchanged.

## Armour tech tree rows and label columns, ratified 2026-09-22

**Two first tiers moved to the 1944 row rather than breaking row == start year.** Owner ruling:
`nsb_apc_hulls0`, `nsb_ifv_hulls0` (1947) and `nsb_special_capabilities0` (1945) start 1944 on
the `@1944` row. One row above their 1950 successors their pictures overlapped, and a sideways
offset would split a family across columns. The APC/IFV hulls stay gated on their legacy
mechanized technologies. `CARRIER_GENERATION_YEARS` keeps 1947: it is the vehicle generation for
the armour cap, not the research date.

**Year columns are placed from observed positions, not declared gridbox x.** Gridbox contents render
~305 / ~765 / ~1165-1210 px right of their declared origin for the first / second / third gridbox
in a folder (Finding 48); label containers render where declared. Place a year column by
measuring a capture, and keep it in empty space left of its group.

**Carrier battalions are enabled by `nsb_iw_armored_vehicles` alone.** Module technologies unlock
modules and nothing else; the validator fails on `enable_subunits` in `NSB_armor_modules.txt`.

**`nsb_apc_hulls*` / `nsb_ifv_hulls*` are presented as module unlocks, not hulls.** Owner QA
2026-09-22: the hull naming and vehicle photographs implied a fourth and fifth hull the designer
does not have. They are named after the superstructure they unlock and use that module's designer
icon. The ids keep the historical `hulls` suffix because 778 references across the mod use them;
do not rename the ids for presentation.

**The carriers sit against the hulls, 2026-09-23 (owner direction).** Carriers, hulls and
`nsb_iw_armored_vehicles` share one gridbox. The condense moved everything right of the carriers
left as one block: hull technology x minus 8, and every gridbox, year column and placeholder minus
560 GUI px. Nothing was moved alone. Shift the whole block the same way for any future
condense; moving one column independently breaks row alignment across gridboxes.

## Designer blueprint art, started 2026-09-23

**Custom blueprints go per equipment TYPE and TAG:** `equipment_designer_<type>_<tag>`, in its
own `interface/equipmentdesigner/tanks/tank_chassis_<type>_<tag>.gui`, drawing a `GFX_TC_<type>_<tag>`
sprite. The lookup order is `<type>[_TAG]` then `<archetype>[_TAG]`, so a generation-specific
outline replaces only that generation and every other tier falls back to the archetype window.
The first one is USA `medium_tank_chassis_3`. The owner's QA confirms whether the tank designer
honours the per-type key, as vanilla's plane designer does.

**Art is authored at 508x206 and shipped at 508x248.** 206 is the visible band above the middle
module row. The DDS is padded at the bottom, never scaled, and is uncompressed 32-bit BGRA without
mips, matching vanilla. Until an outline has module overlay art its slot `@highlight` windows stay
empty rather than borrowing another vehicle's overlay.

**The designer background is `GFX_cwic_tank_blueprint_background`, set in
`tank_designer_view.gui`.** Vanilla's sprite name is not redeclared.

## Fire-support pacing stays as authored, ratified 2026-09-17

**Research dates are not realigned to vehicle years. Both divergences are accepted as existing
balance.** Measured across the 25 in-scope fire-support technologies: 17 align exactly, and the
8 that do not fall into two unrelated shapes.

**The medium SP artillery branch researches five years after its vehicle, at every tier.** A
uniform branch-wide offset is a design choice rather than drift, and the light and heavy
artillery branches being exactly aligned does not make medium wrong. Left alone.

**The tank destroyer branch drifts - `tank_destroyer_1` +10, `_2` +5, `_3`/`_4` 0, `_5` -5.**
This one is genuinely uneven, and `tank_destroyer_1` is researchable in 1940 while unlocking a
1950 vehicle. Still left alone, because the fix is worse than the oddity: `tank_destroyer_1`
enables both the `tank_destroyer` and `heavy_tank_destroyer_brigade` battalions, so moving it to
1950 would remove both from every 1949 campaign.

**This does not affect any design.** Generation mapping uses the legacy equipment row's year
under the ratified not-later-than rule, so the vehicle a technology creates is correct
regardless of when the technology becomes researchable. The divergence is a research-pacing
question only. Do not re-derive it as a designer defect.

## Research-time armour naming, ratified 2026-09-17

**A historical name is delivered either at a bookmark or on research completion, and the two
mechanisms are disjoint by generation.** Owner approval, and it closes the class rather than the
instance: the bookmark dispatcher can only rename a design it creates, and it only creates tiers
a bookmark date reaches, so every name for a later tier was undeliverable by any number of
preset rows. 386 named designs across 22 generations and 48 TAGs now arrive when the country
finishes researching the chassis tier.

**Where each name lives is decided by the generation, never by preference.** If the bookmark
dispatcher creates the generation, the name belongs to
`CWIC_national_armour_naming_presets.txt`. If it does not, the name belongs to
`CWIC_research_armour_naming.txt`. Authoring the same `(producer, generation)` in both would
give the country two designs with one name, which is why the research manifest is built with a
duplicate-name filter against all three live preset manifests.

**The guard shape is the bookmark shape, deliberately.** `has_dlc = "No Step Back"`, the tag,
`NOT = { has_country_flag = cwic_named_<generation>_created }`, then create, then set the flag.
Flag-after-creation is load-bearing: the reverse order means a reload finds the flag set and
never creates the design. One `has_tech` never appears in these guards, because the hook already
fires on that technology's completion.

**Exactly one technology per guard elsewhere, too.** `create_equipment_variant` carries
`allow_without_tech = yes`, which covers the mounted MODULES as well as the chassis. A second
`has_tech` for a module's own technology is a validator failure. This was tried and reverted
this session; do not reintroduce it.

**One recipe per generation, shared by every country on it.** Only the name differs. Authoring
per-country recipes would make 386 balance claims instead of 22 and would break the equality the
naming contract checks.

**Provenance is the reason these names are trustworthy.** Every row records
`legacy_name_key`, `source_path`, `source_line` and the raw `source_name`, and `name` is that
string NFKD-normalised to ASCII. `validate_research_armour_naming()` re-reads the live
localisation on every run, so a moved or edited line fails the build instead of silently
changing a vehicle's name.

A `(producer, generation)` collision - one country with several legacy names mapping to one
generation - resolves to the **newest legacy tier year**. 35 collisions were resolved that way.

## Legacy focus armour grants

**Ratified 2026-09-08.** On an NSB profile, a legacy armour focus grant maps to
the largest designer chassis whose introduction year is no later than the legacy
equipment year. The producer creates one obsolete, no-tech export variant for
that chassis, and the focus grants that producer-owned variant. The non-NSB
branch remains the original legacy equipment grant unchanged. Producer
resolution follows the established producer, creator, owner, OOB-tag order.

The export inventory required by the current grants is:

- Main Battle Tank: 1942, 1944, 1950, 1960, 1970 and 1980.
- Light Tank: 1942 and 1944.
- Heavy Tank: 1942 and 1944.
- APC: 1947, 1950, 1960 and 1965.
- IFV: 1950 and 1965.

All export variants use the established obsolete baseline loadouts. The eight
equipment-type exceptions remain legacy grants: `mechanized_equipment`,
`mechanized_equipment_1`, `mechanized_equipment_2`, and
`mechanized_marine_equipment_1..5`. The first three are pre-designer WWII rows
without replacements; the marine rows remain legacy until a designer vehicle
supplies the marine sub-unit. The 11 explicitly reference-only focus paths are
excluded from this migration and from its validator contract: `FOR HOTFIX/`,
`Need Finished/`, `OUTDATED_PRC_60s.txt`, `Old/`, `Toberemoved/`, and
`Trees for 0.35/`.

**Deferred follow-up.** The current focus effects use generic `CWIC Export ...`
`variant_name` values instead of historical preset variants. This is
immersion-breaking and does not track the legacy equipment identity. A future
session must research and map each focus effect/equipment grant to its
historical variant counterpart. The research cost is intentionally deferred;
no historical mapping is part of this migration.

## Stockpile grants

**Ratified 2026-09-08.** `add_equipment_to_stockpile` takes `type`, `amount`,
`variant_name` and `producer`. It does **not** take `creator`, even though
`creator` is correct on `force_equipment_variants` and `add_equipment_production`
and is what the producer-resolution rule above talks about. The engine rejects the
token and drops the whole grant with no in-game symptom. Do not "restore" `creator`
here for consistency with the resolution rule - the rule is about which tag owns a
design, not about this effect's parameter names.

Every stockpile `type` must resolve to a declared equipment id, or to a tier its
parent family actually declares behind a `duplicate_archetypes` root. The engine
derives those tiers at runtime, so `light_tank_aa_chassis_1` is legal despite never
being declared, while `light_tank_aa_chassis_99` is not - the allowance is bounded
rather than "any number after a known root".

`validate_stockpile_grants()` pins both halves across **all 6220 grants in the mod**,
not only the 2349 under `history/`. Two thirds live in `common/national_focus/` and
`common/decisions/`; scanning only `history/` would leave the blind spot where this
defect class returns. Six negative fixtures.

Nine ids are carried as a named, commented exception set because each names
something that is not equipment and each needs its content owner to say what was
meant. None is tank-designer owned: `mp_uav_1` (ISR), `apc_equipment_1` (PHI),
`manpads_3` (USA), `cv_nav_bomber_equipment_6` (JAP), and `armor_light`,
`armor_medium`, `artillery_light`, `artillery_medium`, `support_artillery` (PRC,
all technology categories used as equipment types). Recorded, not guessed at and
not deleted. Shrinking this set is a content task with an owner, not a validator
task.

## Carrier art

**Ratified 2026-09-08.** Carrier designs get **one static picture per hull tier**,
not per-design art. Per-design art was measured and is not available: the designer
icon compositor is an explicit tank-family graphics contract keyed on enumerated
profile sprites in `interface/tank_profiles.gfx`, not a generic consequence of an
equipment having module slots. Vanilla `super_heavy_artillery_equipment_1` inherits
`module_slots` and still keeps a static archetype picture, and vanilla NSB gives
mechanized no generated icons at all. Do not reopen this as "wire the carriers into
the tank icon generator".

Each hull declares `picture = cwic_apc_chassis_N` / `cwic_ifv_chassis_N`, resolved
by the engine through `GFX_<picture>_medium`. Only the `_medium` sprite form is
registered, matching vanilla. The sixteen sprites point at the already-shipped
neutral `gfx/interface/technologies/apc_{N+3}.dds` and `ifv_{N+1}.dds` textures, so
a hull's production icon is the same art as its technology icon. Neutral mod art was
chosen over the equally complete USA and Soviet tech icon sets so no country's
artwork is baked into a shared chassis definition. No new, copied or renamed assets.

Consequence, accepted: every design on one hull tier shares one icon. `BTR-60P` and
`BTR-60PB` are both `apc_chassis_2` art.

## Naming and localisation

- Country-specific localisation is the naming authority over the consolidated file
  where they disagree. This is a project naming policy, not a claim about engine
  localisation precedence. TUR's country-specific ladder wins.
- ALB and MZB duplicate IFV3 keys select the first `BMP-1`, consistent with the
  surrounding tier progression. The duplicate `BMP-1P` source entries stay in
  provenance; legacy localisation is not edited.
- New names trim surrounding whitespace and transliterate diacritics to ASCII (NFKD).
  Literal variant names need no new localisation keys. No translation files change.
- Mozambique's source localisation uses the undefined tag `MBZ`; the registered tag is
  `MZB` (`common/country_tags/00_countries.txt:119`). The six corresponding preset
  guards use MZB, with MBZ source keys retained in provenance. No OOB request uses MBZ.
- Seven NSB requests used undefined `heavy_mechanized_equipment_1/3`. These are treated
  as spelling errors for `mechanized_heavy_equipment_1/3` and migrate to IFV tiers 0/2.
  A documented inference; mirrored non-NSB typos are deliberately outside the migration.

## Preset authoring

- All APC loadouts use the existing unarmed baseline modules. IFVs use their tier's
  autocannon plus the baseline fighting compartment, suspension, armor, gasoline engine,
  AP and HE ammunition. All fifteen slots are explicit, with zero engine/armor upgrades.
  `allow_without_tech` follows existing bookmark setup.
- These are **functional authored baseline designs carrying historical names**, not
  exact historical configurations and not calibrated frozen-envelope matches.
- Scope is the two bookmarks' chassis union (APC and IFV tiers 0-4), not future tier
  authoring. The 354 selected tier 5-7 pairs are preserved as `future_inventory` in the
  manifest, deliberately absent from bookmark creation until the bookmark/OOB chassis
  contract can expand coherently.
- National creation is split into ten per-hull helpers, and the caller **interleaves**
  national and generic creation for each ascending hull with each family contiguous.
  Calling all national tiers before all generic fallbacks would create an older generic
  design after a newer national one for tags with gaps, violating newest-only
  obsolescence. Shared per-chassis flags also prevent generic duplicate creation.
- Each national design requires NSB, its producer tag, its hull technology and an unset
  per-chassis creation flag. The historical initialization effect deliberately permits
  modules without separate technology checks, matching the established bookmark pattern.
- Touched country-history scripts that had a BOM have it removed; localisation BOMs are
  untouched.

## Special slot map

All named `tank_special_slot_N`. Do not introduce the obsolete `special_type_slot_N`
names in tank content - that collision with plane airframes is what made Computer/Radar
and Loading System both render as "Optics".

**Retired 15-position map.** Superseded in script on 2026-09-09; kept because the
shipped presets were authored against it and its tradeoffs are what the count limits
now have to reproduce. The 21-position map below is what exists today.

| Slot | Allowed categories | Tradeoff |
| --- | --- | --- |
| 1, 2 | Kinetic, chemical, missile or HE ammunition | Two ammunition choices |
| 3 | Aiming devices | Dedicated aiming/stabilization |
| 4 | Optics | Dedicated sight capacity |
| 5 | Ballistic/artillery computer or radar | Computing and radar compete |
| 6 | Manual loader assist, autoloader or artillery loader | One loading system |
| 7 | Passive or reactive protection | Additional armor choice |
| 8 | Passive, reactive or active protection | APS competes with another layer |
| 9 | Survivability, auxiliary mobility or smoke | Utility capacity |
| 10 | Secondary weapon, survivability, auxiliary mobility or smoke | Secondary weapon competes with utility |

All 18 existing special-module categories remain reachable on all three hull
archetypes. Existing category count limits remain in force. Player designs from before
the slot specialization may use now-ineligible placements - use fresh campaigns.

**Shipped 21-position map, ratified and implemented 2026-09-09.** Five mandatory slots
plus `tank_special_slot_1..16`, on all five archetypes.

| Slot | GUI label | Allowed categories |
| --- | --- | --- |
| mandatory x5 | Gun, Turret, Suspension, Armour, Engine | unchanged |
| 1 | AP Ammunition | `tank_ammo_kinetic`, `tank_ammo_chemical`, `tank_ammo_missile` |
| 2 | HE Ammunition | `tank_ammo_he` |
| 3 | Aiming | `tank_fcs_aiming` |
| 4 | Optics | `tank_fcs_optics` |
| 5-16 | Slot 1 - Slot 12 | the twelve categories with no dedicated slot: `tank_fcs_computer`, `tank_fcs_radar`, `tank_loader_manual_assist`, `tank_loader_autoloader`, `tank_loader_artillery`, `tank_protection_passive`, `tank_protection_reactive`, `tank_protection_active`, `tank_survivability`, `tank_mobility_auxiliary`, `tank_smoke`, `tank_secondary_turret` |

Free slots deliberately exclude the four dedicated categories, so one AP round, one HE
round, one aiming device and one sight remain structurally enforced without a limit.
A category authored later must be added to this list **and** to the count limits in the
same edit, or it silently stacks - and, once the per-hull lock model exists, to the
eligibility map as well.

Exclusivity was to move from slot restriction to shared budgets, preserving the current
tradeoffs. Every budget below is what the retired specialized layout enforced, so this
would be a re-expression, not a rebalance:

| Group | Budget |
| --- | --- |
| `tank_fcs_computer` + `tank_fcs_radar` | 1 |
| `tank_loader_manual_assist` + `tank_loader_autoloader` + `tank_loader_artillery` | 1 |
| `tank_protection_passive` + `tank_protection_reactive` + `tank_protection_active` | 2 |
| `tank_survivability` + `tank_mobility_auxiliary` + `tank_smoke` | 2 |
| `tank_secondary_turret` | 1 (already `count < 2`) |

**Not shipped, and still contingent on the multi-category `module_count_limit` test.**
The per-category `count < 2` fallback shipped instead. The consequence is exact and
recorded: the four one-per-group tradeoffs above survive, because each of those groups'
members reduces to one pick anyway, but the two budget-2 groups do not - a design may
now mount all three protection categories and all three utility categories rather than
two of each. That is the balance debt the expansion created.

**The sketch's special-module list is 8 shipped families and 10 unbuilt ones.** Shipped
today, all in `common/units/equipment/modules/00_tank_modules.txt`: Belt Autoloader
(`Loader_4a/4b/4c_Belt`), Active Protection (`APS_0_H..3_H`, `APS_0_S..1_S`), ERA
(`ERA_0`, `ERA_1`, `ERA_L`, `ERA_2`, `ERA_3`), External Additional Armour (`Addon_0_Comb`,
`Addon_1..4_NERA`, `Addon_0/1_CE`), Auxiliary Power Unit (`APU_0..6`, `GT_APU_0..3`),
ATGM (`tank_atgm_launcher_cannon`, `gl_atgm_0p..3p`, `h_atgm_0..4`), smoke launchers
(`Smoke_0`, `Smoke_ESS`, `Smoke_1..4`) and thermal sights (`Optics_4..7`, category
`tank_fcs_optics`). 145 special modules exist across the 18 special categories.

Unbuilt - no module, no technology, no balance row: Blow-Out Panels, Anti-Mine Plow
(and rollers), External Additional Fuel Tanks, Unmanned Turret / RWS, Underwater
Driving, Integrated Trench Plow, Modular Construction, amphibious drive, dozer plough,
and night vision I-III. Drawio page 11 `[STATUS]` states it verbatim: "`[TODO] Base &
Other Tech Modules - RWS I-III, blow-out panels, unmanned turret, anti-mine ploughs and
rollers, dozer plough, external fuel. None exist in script.`" The workbook carries rows
only for the Belt/ERA/APS/APU/ATGM families, and its `Night & Thermal Vision Effects`
tab has zero non-empty rows, so every unbuilt family's numbers are invented and fall
under the existing "recorded as authored" rule. "Bulldozer" is the owner's word for the
sketch's `Dozer Plow`; there is no separate module. `night_vision` exists only as an
orphan tag at `common/technology_tags/00_technology.txt:42`.

Each unbuilt family needs a category decision as well as numbers: some fit existing
categories (external armour -> `tank_protection_passive`), others have none (external
fuel, mine/trench ploughs, unmanned turret, amphibious drive). A new category is cheap
in a free slot but must be added to an exclusivity group and to a count limit in the
same edit, or it silently stacks.

## Module balance, ratified 2026-09-05

| # | Question | Outcome |
| --- | --- | --- |
| 5.3.1 | Reliability expressed two ways | **Kept split.** Guns use a negative multiplier, turrets a positive flat add. Units genuinely differ; converting would touch 13 blocks for cosmetic consistency. |
| 5.3.2 | `cwic_hull_mg` flat `defense = 0.5` | **Reduced to 0.25.** Script, CSV and both workbook tables updated. |
| 5.3.3 | Secondaries lacked reliability cost | **All four now carry one:** coax -0.005, hull MG -0.005, HMG -0.01, autocannon -0.025 unchanged. |
| 5.3.4 | Turret cost ordering | **LP premium kept, 1.5 tie broken.** `oscillating_turret` 1.5 to 1.75, dismantling 0.75 to 0.875, preserving the file-wide 0.5 ratio. |
| 5.3.5 | 12 of 15 sub-units `active = yes` | **Normalised to `active = yes`, not `no`.** The manual's recommendation was wrong: legacy `armor.txt` enables only `light_armor`, `medium_armor`, `heavy_armor`, `super_heavy_armor`. The 9 role brigades and 3 flame tanks are enabled only by `nsb_iw_armored_vehicles`, so in a non-NSB profile `active = yes` is the sole thing making them buildable. Setting them to `no` would have deleted them from non-NSB play. The validator contract was inverted to match. |
| 5.3.6 | `tank_gasoline_engine` home, missing `xp_cost` | **Base engine, not a duplicate.** It is `Petrol_0`'s declared parent and the `engine_type_slot` default at `tank_chassis.txt:391, 795, 1200`. Gains `xp_cost = 1` and `dismantle_cost_ic = 0.5`. |
| 5.3.7 | Base gasoline engine speed ordering and preset baseline | **Rebalanced and rerouted.** `tank_gasoline_engine` remains the script-owned pre-WW2 base module and `Petrol_0` remains its child/starting template. Its `maximum_speed` multiplier is 0.03, below `Petrol_0` at 0.05. The living CSV and frozen-workbook validator override are updated. The 576 national and 40 generic preset references in the two scripted effects now use `Petrol_0`; the four USA manifest entries are synchronized. `tank_gasoline_engine` localisation is "Pre-WW2 Gasoline Engine". |
| 5.3.8 | Major-country `Petrol_1` bootstrap | **Implemented 2026-09-09.** `nsb_engines0` is granted to USA, SOV, FRA, ENG and WGR. Generic fallback recipes remain on `Petrol_0`; only USA's tag-exclusive 1950 `M47 Patton` reroutes to `Petrol_1`. |
| 6 | Research cost curve | **Ratified and applied.** R1-R7; 91 of 169 technologies repriced; 337 to 345.5 (+2.52%); USA/SOV 1970 -1.67%, 2020 +8.33%. |
| 6 | XP economy | **Flat at 1, deliberate.** No repricing. Closed. |

**Conventional turret balance.** Authored in response to QA: conventional turret gets
+5% breakthrough for an extra 0.5 IC. Light turret remains the inexpensive option.
Reliability unchanged. This is a limited cost-versus-breakthrough choice, not a
turret/weapon-size eligibility redesign.

| Field | Frozen workbook | Revised conventional | Light turret |
| --- | --- | --- | --- |
| Build cost IC | 1 | 1.5 | 1 |
| Additive reliability | 0.15 | 0.15 | 0.15 |
| Breakthrough multiplier | absent | +0.05 | absent |
| Dismantle cost IC | 0.5 | 0.75 | 0.5 |

The CSV carries the revised row. The validator checks that row against the script, the
workbook against the old values, and the revised turret against its numeric contract.
These are the only cross-source exceptions.

## Static QA dispositions, 2026-09-08

The bounded owner-QA review is resolved at source level without a balance redesign:

- USA and SOV 1980 dated history already call
  `cwic_major_tank_research_1980`. Its two DLC branches and exact technology set
  are validator contracts; no second country-history research convention is added.
- The reported 1985 ahead-of-time cases already use matching `start_year` and
  `@1985` rows. The source contains no missing-date defect, so no technology dates
  are changed.
- The Light/Conventional Turret difference is intentional: the former is the
  1 IC option and the latter buys +0.05 breakthrough for 1.5 IC.
- `Radar_1`'s script values match both balance sources. A displayed `-0` supply
  value is a runtime tooltip-precision issue, not a balance correction.
- Focus exports are internal obsolete designs: every helper is hidden and marked
  obsolete, while startup national and generic designs use the existing
  newest-only obsolescence marker. No focus effect names or creation order change.

These are static dispositions only. Live tooltip, production-tab, bookmark and
balance acceptance remain unverified.

## QA findings that are not transcription errors

- **Gun-Launched ATGM III (`gl_atgm_2p`)** has additive hard attack 95, soft attack 5.5
  and piercing 600 in **both script and workbook**. Heavy ATGM values are likewise
  covered by the module balance report. Matching the source does not establish that the
  finished vehicle is balanced; missile/gun interactions need live calibration before
  imposing a new scale.
- **Radar II (`Radar_1`)** has additive fuel use 1.2, supply-use multiplier -0.075,
  air-attack multiplier +0.25 and reliability multiplier -0.05. These match the
  workbook. The screenshot's supply use rounded to `-0.0` is display precision, not a
  zero in the module definition. Verify application and tooltip precision live before
  changing balance to address a display symptom.

## Production icon resolution

**Settled 2026-09-14 by two in-game probes, owner-run.** Two different surfaces use two
different keys, and conflating them cost this project a 2,116-declaration plan:

- **Designer template list** honours `GFX_<TAG>_<technology>_medium` for `nsb_*` chassis
  technologies. Probe 1: `GFX_USA_nsb_light_tanks0_medium` rendered on the USA row with the
  tooltip naming it.
- **Production line** does *not* key on the technology that enables the equipment id. Probe 2
  declared `GFX_USA_nsb_light_tanks1_medium` against `light_tank_apc_chassis_2`, whose sole
  enabling technology is `nsb_light_tanks1`, and the line kept rendering the legacy half-track
  (`USA_apc_1.dds` = `GFX_USA_mechanized_infantry_medium`). The family's legacy art wins.

**Consequence, ratified: author no per-country `nsb_*` sprites.** Because the convergence
relocated the legacy rows into the role families, the per-country art the mod already ships in
`interface/*_techs.gfx` reaches the designer families for free. The owner confirms the resulting
half-track on an early APC line is the wanted, historically consistent outcome. Both probe
sprites are removed; do not re-stage them.

## ATGM stockpile residue on NSB profiles

**Open, needs an owner ruling - do not "fix" mechanically.** Five grants in two NSB OOBs name
DLC-gated legacy ATGM rows: `SOV_1980_nsb.txt:1321-1323` and `NOR_1980_nsb.txt:364,369`. A gated
id is still a declared id, so these resolve and award stock the profile cannot build.

The obvious rewrite to `light_tank_destroyer_chassis_4..7` (the year map is exact: 1960/1970/1980/
1990 on both sides) was applied and **reverted**, because it breaks the contract that an NSB OOB
may only name a tier a starting-variant preset creates - and there are zero
`light_tank_destroyer_chassis` presets. The ratified export inventory above covers MBT, Light,
Heavy, APC and IFV only. Extending it to ATGM means authoring loadouts and historical names,
which is balance content with an owner, exactly like the inventory itself.

## No generic starting designs, ratified 2026-09-22

**Owner ruling: only historical national presets are created. Every generic "Standard ..."
design is gone.** They cluttered the production menu (`Standard Light Tank Destroyer 1939`
through `1970` beside the national designs) and named nothing real.

- **Bookmark placeholders:** all 68 blocks deleted from `cwic_create_starting_tank_variants`.
  The dispatcher now only calls national helpers. A country with no national preset on a
  chassis starts with no design on it and designs its own; the AI does so from
  `generic_tank.txt`.
- **Fire-support research designs:** `CWIC_firesupport_designs.txt` and its 25
  `on_research_complete` hooks are deleted. **This reverses the 2026-09-17 ruling** that a
  fire-support technology must leave the player a design. Research now unlocks modules; the
  research-time national names (Finding 36) still arrive where a country has one.
- **Consumers repointed, not dropped:** NOR's twelve ATGM brigades force the new NOR preset
  `M113F1 w/ BGM-71 TOW` (live source `NOR_atgm_carrier_equipment_1`); NOR's 150 generic 1950
  SPAA folded into its M42 Duster stockpile (250 -> 400); CHI's 500 generic 1950 MBTs are now
  its own M48A1, with its bootstrap moved from `nsb_main_battle_tanks2` to `3`.
- The naming and carrier manifests keep their recipes: they were copied from the placeholders,
  and every national preset must still equal them, which is what keeps the names
  balance-neutral. `has_generic_design` in the carrier manifest is now a legacy field name
  meaning "owns the light hull tier".
- The validator fails on any `create_equipment_variant` named `Standard ...` anywhere under
  `common/`, and on any design the dispatcher creates directly.

**The 2026-09-11 rule "a bookmark chassis holds exactly one generic design" above is void** -
there are none. Its tier-ownership half still decides which generation maps a shared tier to
its technology.

## Armour naming presets

**Ratified 2026-09-14, implemented.** Players saw placeholders like "Standard Main Battle
Tank 1950" on NSB starting divisions. 339 such references existed across 66 NSB OOBs.

**The name source is live country equipment localisation, not research.** The existing carrier
preset contract already derives every national design name from an
`equipment_country_l_english.yml` / `<TAG>_equipment_*.yml` entry and records file and line as
provenance. The key shape is `<TAG>_<legacy_family>_<index>`, and the index is the designer tier
index - `medium_tank_chassis_3` takes `<TAG>_mbt_equipment_3`. That resolves 89 of the 104
placeholder rows mechanically. Six parallel scouts independently converged on the same entries,
which is how the index rule was found; their service-history fallbacks were **not** used, because
a name without a localisation entry cannot satisfy the provenance contract.

**Loadouts are copied verbatim from the generic block each guard suppresses**, so a rename can
never move a stat. The validator pins that equality rather than trusting it.

**Architecture: a second system, not an extension of the first.**
`validate_national_tank_presets()` pins `cwic_create_national_tank_variants` to exactly 14
guards (USA/SOV medium 0-6) against a manifest, and the carrier validator hardcodes APC/IFV
tiers 0-4 with `len(recipes) != 10`. Widening either would have weakened a pinned contract, so
the naming system is separate and mirrors their shape:

- `common/scripted_effects/CWIC_national_armour_naming_presets.txt` - 30 per-tier helpers,
  89 guards.
- `LogDocs/Tank_Designer/data/Tank_Naming_Preset_Manifest.json` - 89 presets, 30 recipes,
  each with localisation provenance.
- `validate_national_armour_naming_presets()` - name-from-provenance, recipe equality with the
  shadowed generic block, one guard per producer, flag ordering, and dispatcher call ordering.
  Proven to fire by breaking a name, a module and a flag, then reverting.

Helpers are called at the top of `cwic_create_starting_tank_variants`; each sets the generic
block's own `cwic_starting_<tier>_created` flag, which is what suppresses the placeholder. No
exclusion lists were needed.

**A name belongs to its producer, not to the OOB's country.** `oob_variant_producer` resolves
`producer`, then `creator`, then `owner`, then the file tag. 100 references name a design owned by
an exporter (CAP, CUM, WGR, USA), and those must carry the exporter's design name or stay
placeholders - never the importing country's name. Renaming by file tag is wrong and the
bootstrap-coverage contract catches it.

**Result: 339 placeholder references to 2.** 212 were replaced in the first pass; the remaining
125 were exporter-owned rows and fell out of the same mechanical rule once the worklist was keyed
on the *resolved producer* rather than the OOB's file tag. CUM, CAP, WGR and FRA already had
localisation for those tiers - they were never missing names, only missing presets. 106 presets
now, 30 helpers.

**The last 2 references need an owner decision, not code:**

- `CHI_1980_nsb.txt:603` (`medium_tank_chassis_3`) - `CHI_mbt_equipment_3` exists but is
  **commented out** at `equipment_country_l_english.yml:246-247`, as
  `Tank, Combat, Full Tracked: 76-mm gun, M41A1` / `M41A1 Walker Bulldog`. Someone disabled it
  deliberately, and plausibly for cause: the M41 is a light tank sitting on an MBT tier. Do not
  uncomment it without asking.
- `NOR_1980_nsb.txt:349` (`light_tank_aa_chassis_3`) - `NOR_spaag_equipment_3` is simply absent
  while `_1` and `_2` exist. Needs a name authored.

**`owner = "USA"` in `SOV_1949_nsb.txt` is intentional - do not "fix" it.** Owner ruling
2026-09-14: those 45 forced variants represent Lend-Lease equipment the Soviets kept using after
WWII. The naming pass therefore displays the USA designs (`M5 Stuart`,
`M16 Multiple Gun Motor Carriage`) on those Soviet divisions, which is correct and is the point.
A future pass that "corrects" the owner tag to SOV would destroy deliberate historical content.

## Entity alias coverage

**Implemented 2026-09-14.** 13 hull-consuming sub-units had **zero** aliases, so every one of
them showed a default battlefield model. The alias key the engine derives is
`<TAG>_<sub_unit>_<visual_level>_entity`; a miss is silent, which is why this needed a contract
rather than a spot check. 4,640 aliases added across 40 TAGs, table 2,269 -> 6,932.

**Clone target follows what the sub-unit fields, not merely its hull family.** Troop carriers
take `mechanized_entity` (`units_vehicles.asset:50`) and the marine variant
`mechanized_marine_entity` (`:68`). The obvious shortcut - clone the TAG's light armour entity,
since APC hulls are light - would have put a **tank model under mechanized infantry**. Armour
based support (HQ, armoured recon, armoured engineers) clones the entity that TAG already uses
for the matching armour family, `spaag_support` clones that TAG's own `spaag` entity where it
has one, and the generic entities in `units_tanks.asset` are the fallback for TAGs with no
national model. Every clone target was checked to exist; all 64 are pre-existing.

**Level counts are the consumed hull's `visual_level` ceiling plus one, and they differ per
role:** APC and the light/medium tank hulls reach 9, **IFV only 7**, light AA and heavy only 4.
A flat 10 everywhere - the first thing I generated - declares aliases for visual levels no
equipment row can reach. `armored_infantry` and `mechanized_airborne` are IFV and take 8;
`spaag_support` and `hq_heavy_armor` take 5.

**Corrected 2026-09-14, same day: coverage is alias-or-native, and my first pass got this
wrong.** Per-country entities also live in `<TAG>_unit.asset` and `*_units_*.asset`, and I had
measured coverage from the alias file alone. Two consequences, both fixed:

- **538 of the 4,640 aliases were overriding national models.** `armored_infantry`,
  `mechanized_airborne`, `mechanized_marine` and five `mechanized_infantry` entries already had
  per-country entities (410, 311, 181 and 5 pairs). Because this file carries the `zz_` prefix it
  loads **last**, so those aliases replaced a national model with the generic one. Removed; 4,102
  aliases remain, and nothing is declared here for a name a native asset already declares.
- **The 23 "pre-existing level holes" were not holes.** `SOV_light_armor_0_entity` and friends are
  declared natively (`SOV_units_tanks.asset:7`). Worse, my fill cloned
  `SOV_light_armor_entity`, which itself clones `SOV_light_armor_0_entity` - a **circular clone**.
  All 23 reverted.

The contract now unions alias and native coverage. Three consequences worth knowing:
contiguity is **not** an invariant of legacy content (`TUR_armored_infantry` and many others
declare only some levels), so it is enforced only for the sub-units this file owns outright, where
every level is generated from the hull ceiling; `legacy_tag_counts` holds alias-or-native counts,
which is why several exceed the alias file's own 40 TAGs; and `native_overrides = 140` pins the
pre-existing deliberate shadowing so a new override fails loudly.

**The static `ENTITY_ALIAS_TOKENS` allowlist was deleted, not extended.** It was a snapshot of
which sub-units happened to have aliases (11) and would have rejected all 13 new ones. The
invariant it was really defending is now derived and stronger: every alias must name a declared
sub-unit that actually consumes an armour hull, so typos and stale tokens still fail.

**Legacy coverage is deliberately not uniform, and is pinned rather than papered over.** Eleven
pre-designer tokens cover only some TAGs (`heavy_armor` 16/40, `atgm_carrier` 20/40,
`medium_armor` 36/40, three at 39/40). Blanket uniformity would have failed on content that was
never uniform, so `legacy_tag_counts` records each exact count: partial coverage cannot erode
further, and any improvement forces a deliberate update. Shrinking that map is content work with
an owner.

Contract proven by four negative fixtures: all aliases for a sub-unit removed, one TAG removed,
a level hole, and a bumped legacy count.

## Default 3D model selection

**Root cause found 2026-09-14 in the live error log, not in the files.** The mod owner reported
that correct models existed but had to be picked by hand in the 3D model selector. The decisive
evidence is `equipment_model_util.cpp:76`:

```
Equipment graphic database model entries for type "Medium SP Artillery" includes
invalid entity "USA_medium_sp_artillery_brigade_0_entity"
```

98 such lines, plus `Entity referenced in equipment graphic database does not exist` for other
TAGs. **The engine builds its equipment graphic database from every live sub-unit and expects
`<TAG>_<sub_unit>_<visual_level>_entity` for each.** A missing entry does not fall back silently -
it makes the *default* model entry invalid, so the selector opens with nothing chosen.

**Why those tokens are still live after the convergence deleted the mod's role brigades:**
`common/units/sp_artillery_brigade.txt`, `tank_destroyer_brigade.txt`, `sp_anti-air_brigade.txt`,
`recon.txt` and 36 other vanilla `common/units` files are **not shadowed by this mod**, so their
sub-units load. 31 vanilla-only sub-units consume an armour hull; 11 have a hull the mod declares
and now carry aliases. The fix is 2,283 aliases, table 6,371 -> 8,654, and the contract carries
`vanilla_inherited_sub_units` so these are legal tokens despite not being declared under the mod's
own `common/units`.

**Level ceilings come from the union of mod and vanilla rows.** Vanilla declares a third visual
level for the light tank destroyer hull that the mod's `atgm_carrier` rows stop short of, and the
database iterates vanilla's levels too, so level 2 was logged invalid for five TAGs. Deriving
ceilings from mod equipment alone is not sufficient.

**Every armour entity name the logs called invalid now exists - 0 remaining.** 132 non-armour
names remain invalid (16 `fighter_equipment`, 8 `battleship`, 8 `heavy_cruiser`, 7 `CAS_equipment`,
plus `modern_armor` and `super_heavy_armor`, whose hulls this mod does not declare). Those are the
same defect class in the air and naval subsystems, pre-existing and out of tank-designer scope.

**What is still NOT proven.** No vanilla text file specifies the regular-division default
resolution algorithm. The only documented chain is for raid `unit_model`
(`common/raids/_documentation.md:39-45`: country-specific, then culture-specific, then basic, then
default). The selector UI is `interface/divisiondesignerview.gui:1167-1333`, whose
`best_match_button` (`:1300-1314`, tooltip `USE_DEFAULT_MODEL`) is C++-bound with no script hook.
A template can be forced with `override_model` (vanilla `common/national_focus/germany.txt:9437`).
So repairing the database entries is evidence-backed as *the* logged defect, but whether it is
sufficient to make the right model default is an in-game question.

## Legacy localisation linkage audit

**Owner hypothesis 2026-09-14, confirmed and acted on:** a lot of per-country vehicle names were
already authored in localisation but never linked into the NSB designer system.

Measured across every English localisation file, keys of the shape
`<TAG>_<legacy_family>_<index>` for the 12 armour families:

| | count |
|---|---|
| legacy armour loc entries carrying a real name | 3,456 |
| already linked to a designer preset before this pass | 678 |
| **defined but unlinked** | **2,778** |

86 TAGs, 12 families. Heaviest unlinked: `mbt_equipment` 586, `lt_equipment` 373,
`mechanized_equipment` 341, `mechanized_marine_equipment` 223, `sp_artillery_equipment` 211.

**1,304 of them are now linked**, taking the naming manifest from 106 presets to 1,410 across 30
helpers and 86 TAGs. Same mechanical rule as before, so no new judgement: name from the
localisation entry with file and line provenance, recipe copied verbatim from the generic block
the guard suppresses, one guard per producer and tier, flag suppresses the placeholder.

**What is deliberately left unlinked, and why:**

- **1,214 entries name a tier that has no generic bookmark design.** The helper architecture
  copies its recipe from the generic block it shadows; with no generic block there is no recipe to
  copy and no placeholder to suppress. Linking these means authoring loadouts, which is balance
  content with an owner - the same boundary the ATGM export inventory hit.
- **13 candidates on APC and IFV chassis were dropped outright.** Those tiers are owned by the
  carrier preset system (`cwic_create_national_apc_chassis_*_variants`), which has its own
  manifest and contract. A second helper creating variants on the same chassis for the same TAG
  would make `bookmark_variant_names` ambiguous and break the "bootstraps several designs" check.
  One owner per tier.

## Per-country technology icon sprites

**Implemented 2026-09-14** from the owner's screenshot: a US self-propelled gun showed a generic
towed-artillery icon, tooltip `GFX_USA_improved_heavy_art_medium`. That sprite is declared
nowhere; vanilla ships only the Soviet one (`interface/Technologies.gfx:3267-3270`, texture
`SOV_imp_heavy_spart.dds`). Per Finding 30 the engine asks for `GFX_<TAG>_<technology>_medium` and
falls back silently to the generic sprite, so this is a missing declaration, not missing art.

**46 sprites added across 26 `interface/<TAG>_techs.gfx` files**, every one pointing at a texture
already on disk. Two sources:

- **33 derived from the mod's own convention.** For each armour technology that any country
  already declares, the texture suffix was derived from the existing declarations
  (`heavy_sp_artillery_1` -> `<TAG>_sp_hv_art_1`, `atgm_carrier_0` -> `<TAG>_atcar1`, and so on -
  74 technologies have a derivable suffix), then every TAG missing that sprite was checked for the
  matching file. Matching **must be case-insensitive and extension-agnostic**: the library mixes
  `apc`/`APC`, `ifv`/`IFV`, `.dds`/`.png`/`.PNG`, and a strict match found only 29 of 33.
- **13 `improved_heavy_art` declarations**, one per TAG that owns a heavy SP artillery texture.

**An unresolved contradiction, recorded rather than papered over.** `improved_heavy_art` exists in
**no mod file** - the mod's `common/technologies/armor.txt` fully replaces vanilla's, and the two
technology sets are **disjoint** (48 mod ids, 50 vanilla ids, zero overlap). The engine
nevertheless requested the key, so something still resolves vanilla armour technology names. The
declaration is therefore empirical: it costs one line, fixes the photographed symptom, and is
inert if the key is never requested again. Do not treat the underlying resolution as understood.

**Scale check before anyone "finishes" this.** 5,039 per-country armour technology sprites are
absent across 92 TAGs and 97 technologies. Only these 46 had art on disk; the rest need textures
drawn, which is art work, not scripting. 3,885 already exist.

## Production icons follow the equipment type category

**Measured 2026-09-14 from the owner's production-tab capture, and it settles the artillery
asymmetry once and for all - the technology is not the key.**

Every row in that capture is a designer tier (localisation confirms: `light_tank_apc_chassis_2` =
"Improved Light Armored Personnel Carrier", `light_tank_artillery_chassis_2` = "Improved Light SP
Artillery"). Those two ids are enabled by **exactly the same technology**, `nsb_light_tanks1`, yet
the artillery row renders the M52 self-propelled howitzer while the APC row renders a generic
light tank photograph. Same technology, different art, so the icon cannot be technology-keyed.

What differs is the `type` block on the role root (`x_tank_chassis.txt`):

| role root | type | icon observed |
|---|---|---|
| `light_tank_chassis` | `armor light_armor` | light tank photo |
| `light_tank_artillery_chassis` | `armor artillery` | M52, correct |
| `light_tank_aa_chassis` | `armor anti_air` | M42, correct |
| `light_tank_destroyer_chassis` | `armor anti_tank` | M56 Scorpion, correct |
| `light_tank_apc_chassis` | `armor **flame**` | light tank hull photo, wrong |
| `light_tank_ifv_chassis` | `armor **rocket**` | light tank hull photo, wrong |

**The production icon follows the equipment type category.** Artillery, AA and tank destroyers
work because their category matches what the vehicle actually is. APC and IFV are typed `flame`
and `rocket` - tokens spent in phase 6/7 because no `mechanized` category token exists - so they
inherit the hull's own art and can never show carrier art while typed that way.

This also retires the old "artillery renders generic" thread completely: artillery was never
broken, and no per-country `nsb_*` sprite could have fixed APC, because one armour technology
enables six role tiers at once and cannot distinguish them.

**Owner ruling 2026-09-14: full send on option 3.** Implemented in two halves.

**Half 1 - the blank fire-support icons had a simpler cause than the category rule.** The
production and designer views ask for *vanilla* fire-support technology keys, and ten of them had
**no sprite at all in this mod, neither generic nor per-country**: `improved_light_art`,
`improved_medium_art`, `improved_heavy_art`, `super_heavy_art`, `super_heavy_spaa`,
`improved_medium_td`, `advanced_light_td`, `advanced_medium_td`, `modern_td`, `super_heavy_td`.
Nothing declared means nothing renders, which is the transparency the owner saw - not a category
problem and not missing art. 10 generic sprites now point at the legacy fire-support photographs
in `cwic_tank_rework_icons.gfx`, and 177 per-country overrides across 46 `<TAG>_techs.gfx` files
give each nation its own vehicle. Both the tech tree and the designer now draw from the same
legacy photo set.

**Half 2 - flame and rocket have no sprite key to declare.** Measured: the mod defines **no
`flame` technology at all**, and the only rocket keys are `sp_rocket1..5` and vanilla
`rocket_artillery*`, which belong to real rocket artillery - hijacking them would corrupt those
icons. So a per-country flame/rocket sprite is not possible. The lever that does exist is the
archetype `picture`, now set on all four carrier roots: `light_tank_apc_chassis` and
`medium_tank_apc_chassis` to `archetype_mechanized_equipment`, `light_tank_ifv_chassis` and
`medium_tank_ifv_chassis` to `archetype_mechanized_heavy_equipment`. All four sprites were already
registered. `validate_armour_archetype_pictures()` now scans `x_tank_chassis.txt`, which it never
did, and pins the four new entries.

Whether the archetype picture outranks the hull technology sprite for these tiers is an in-game
question - it is the only remaining lever, so if APC still shows a tank hull, the category rule
below is the binding constraint and option 2 (retyping to `amphibious`) is the only fix left.

**The three options as originally recorded:**

1. **Accept it.** APC and IFV show their hull. Cheapest, and the names are correct.
2. **Retype to `amphibious`.** It is the one unspent role token (`DECISIONS.md` final role-token
   map) and its art is amphibious carriers - the LVT-4 row in the same capture proves that art
   resolves. Closer to an APC than a flamethrower is, but it re-opens a token the owner
   deliberately left unspent and changes designer role grouping.
3. **Declare art for the `flame` and `rocket` categories per country**, if the engine exposes a
   category sprite key. Unverified; would need a probe.

## Retracted after measurement - do not reopen

- **The AA and flamethrower sprites are not broken.** `tank_module_aa_gun{,_2,_3}.dds`,
  `tank_module_flamethrower.dds`, `EMI_tank_flamethrower.dds` and `Niche_icon_strip.dds`
  all exist in the base game under
  `gfx/interface/equipmentdesigner/tanks/{modules,icons}/`, which the mod does not
  shadow. HOI4 resolves sprite paths mod-first then vanilla, and the live error.log
  shows zero texture misses. Checking only the mod directory produced the false positive.
- **`nsb_armor_modules_folder` is not missing a year column.** Labels sit at
  x=20/1450/3100 against trees at x=428/1950/3600 - one per tree. The `nsb_armor`
  folder's fourth label at x=4000 is the anomaly.
- **The designer role group does not wrongly overlay `equipment_preview`.**
  `design_company_icon` and `design_team_button` at (461,382) sit inside the same
  preview rectangle, so floating icons over the blueprint is the panel's existing layout
  language. `tag_icon_bg` 465 to 461 and `niche_button` 474 to 470 aligned the group to
  the x=461 rail; the defect premise did not survive measurement.
- **Duplicate production listing of a carrier is working as intended.** See
  `REFERENCE.md`.
- **Two `completion_reward` blocks did not cause the empty `BUL_Soviet_T55s` award.**
  See `STATUS.md` Finding 1.

## Known inconsistencies - recorded, not scheduled

1. Granting flame chassis does not make the AI build them; no AI division template
   fields a flame battalion. Needs `common/ai_templates/` work.
2. Secondary armament competes for the special slots, and the workbook envelopes were
   computed without it.
3. Two parser families live in the validator - the doctrine work added a bounded parser
   while the tank half uses older near-duplicates. Do not add a third; reuse and delete.
   Partially paid down 2026-09-08: the lenient brace scanner is now the single
   `located_keyed_blocks`, with `keyed_blocks` and `stockpile_grants` as thin views
   over it. The bounded/lenient split itself remains.
4. Turret modules have no `xp_cost` while every other module family does.
5. 14 abbreviation collisions across 60 modules, including all ten light gun tiers
   sharing `tanklightc`. Variant auto-naming cannot distinguish a 1939 gun from a 2015
   one. Cosmetic, but it touches every armor design ever produced.
6. `main_armament_slot = empty` in `default_modules` despite `required = yes` on all
   three archetypes, which is why a fresh design opens with no gun. Probably
   intentional, but it is the first thing a player sees.
7. Legacy orphan archetypes `lt_equipment`, `mbt_equipment`, `ht_equipment` are declared
   but nothing targets them. Harmless, confusing.
8. The artillery tree is entirely NSB-unaware: 85 techs in an unconditional
   `artillery_folder` granting zero designer modules, running in parallel with the
   designer every game. The largest structural inconsistency in the system, and
   deliberately out of scope - record it, do not start it.
9. `derived_variant_name` targets do not exist in script; `light_tank_equipment_0` and
   friends are generated at runtime. Correct NSB behaviour, but it means no script can
   reference them.
10. Bookmark variants use concrete module ids (`ap_0p`, `tank_he_0p`) while AI recipes
    use categories (`tank_ammo_kinetic`, `tank_ammo_he`). Both correct; the asymmetry
    misleads. The claim that "the three SPAA variants deliberately carry no ammunition
    because AA guns supply their own attack" is **superseded as of 2026-09-09**: the
    owner reversed that rule, `tank_aa_ammo_1..3` exist in `tank_ammo_he` restricted to
    `allow_equipment_type = anti_air`, all three SPAA variants now mount tier 1, and the
    validator requires it. Flamethrowers remain self-supplying and exempt.
11. `sp_tag_tank_speed_factor` is an invalid modifier in
    `common/dynamic_modifiers/wuw_dynamic_modifiers.txt` - one live log error,
    tank-adjacent, trivial, unowned.
12. `common/national_focus/PHI_1950s.txt:587` grants `apc_equipment_1`, which is not an
    equipment id anywhere in the repo, so the focus silently awards nothing.
    `apc_equipment_1` exists only as the `derived_variant_name` of `apc_chassis_1`,
    which is a localisation key rather than an equipment type. Predates the APC work.
    Most likely wants `mechanized_equipment_3`, or a designer APC. Flagged for whoever
    owns PHI.
    Now also carried in `STOCKPILE_TYPE_EXCEPTIONS`, alongside eight sibling grants
    the mod-wide stockpile contract found in ISR, USA, JAP and PRC content.
