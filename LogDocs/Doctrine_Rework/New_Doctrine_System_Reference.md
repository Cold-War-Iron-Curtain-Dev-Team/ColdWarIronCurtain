# The New (DLC-era) Doctrine System - Reference

Date: 2026-09-05. Written against local Hearts of Iron IV **1.19.2** (`Operation Postern`), all DLC.

This is a study of `common/doctrines/` - the framework the game itself uses since Graveyard of
Empires / Operation Postern. It is **not** the legacy `common/technologies/*_doctrine.txt` model that
`Doctrine_Rework_Plan.md`, `Land_Doctrine_Tree_Structure.md` and `Doctrine_Cell_Manifest.md` describe.
Those documents own the currently-shipping CWIC architecture. This one exists so a future conversion
pass has an accurate picture of the target before anyone starts moving files again.

Primary evidence is the installed vanilla game, not the wiki. Where the in-repo
`_documentation.md` files disagree with shipped vanilla script, **the shipped script wins** - see
"Where the bundled documentation is stale" below.

---

## 1. The object model

Five object types, nested:

```
Folder            land / naval / air / special_forces        common/doctrines/folders/
  Grand Doctrine  one active per folder, mutually exclusive  common/doctrines/grand_doctrines/
    Track         fixed slots the grand doctrine exposes     common/doctrines/tracks/
      Subdoctrine one chosen per track, mutually exclusive   common/doctrines/subdoctrines/<folder>/
        Reward    5 per subdoctrine, unlocked by Mastery     (inline, inside the subdoctrine)
      Milestone   1 per track, defined on the grand doctrine (inline, inside the grand doctrine)
```

The mental model, in one paragraph: a country picks **one Grand Doctrine per folder** by paying XP.
That grand doctrine declares a list of **Tracks** (land has four: infantry, combat_support, armor,
operations). Each track is an empty slot. The player pays XP again to slot **one Subdoctrine** into
each track - subdoctrines declare which track they belong to, so the pool available for a slot is
"every subdoctrine whose `track` is this one". Once slotted, the subdoctrine's **five Rewards**
unlock automatically as the country accumulates **Mastery** in that track, which is earned passively
by having relevant units in action. When all five rewards are unlocked, the track is complete and the
grand doctrine's **Milestone** for that track fires as a bonus capstone.

Key structural consequences:

- **Tracks are slots, not trees.** There is no `path`, no XY grid, no `leads_to_tech`. Layout is
  engine-driven from the four-track list. This is the single biggest difference from the legacy model
  and the reason a 1:1 port of the 78-cell / 528-node land tree is impossible without redesign.
- **Progression is per-track and horizontal.** Each of the four land tracks advances independently
  and each holds exactly one subdoctrine at a time.
- **The player buys twice, then stops.** XP buys the grand doctrine and the subdoctrines. Everything
  after that is Mastery, which is not purchased.
- **Switching Grand Doctrine resets all Mastery** (`SWITCH_GRAND_DOCTRINE_MASTERY_RESET` loc).

### Vanilla's scale, as a sizing reference

| Folder | Grand doctrines | Tracks | Subdoctrines |
| --- | ---: | ---: | ---: |
| land | 4 (`new_mobile_warfare`, `superior_firepower`, `grand_battleplan`, `mass_assault`) | 4 | 36 |
| air | 3 (`new_strategic_destruction`, `new_battlefield_support`, `new_operational_integrity`) | 4 | 25 |
| naval | 3 (`new_fleet_in_being`, `new_convoy_raiding`, `new_base_strike`) | 4 | 26 |
| special_forces | 2 (`special_forces_quantity`, `special_forces_quality`) | 2 | 8 |

Total 12 grand doctrines, 14 tracks, 95 subdoctrines, 5 rewards each (one infantry subdoctrine has 4).
About 9,000 lines of script. For comparison the parked CWIC legacy trees are ~19,850 lines / 646 nodes.

---

## 2. File-by-file syntax

### 2.1 Folder - `common/doctrines/folders/doctrine_folders.txt`

```
land = {
    allowed = { always = yes }      # false = folder not available at all
    name = "land_doctrine_folder"   # loc key
    ledger = army                   # army | navy | air | all | hidden
    ledger_gfx = GFX_land_doctrine_folder_icon
    tab_gfx = GFX_landdoctrine_tab_large
    color_frame = 1                 # frame index for folder-tinted UI elements
    sound = ui_doctrine_tab_land
}
```

Vanilla defines exactly four: `land` (1), `naval` (2), `air` (3), `special_forces` (4).
`special_forces` is DLC-gated via `allowed = { OR = { has_dlc = "No Compromise, No Surrender"
has_dlc = "Arms Against Tyranny" } }`. Custom folder names are permitted.

> **CWIC drift:** the mod's copy of this file is a November 2025 vanilla snapshot and **omits the
> `special_forces` folder entirely.** Since the file is a full-path override, that folder currently
> does not exist for the mod. Any conversion must decide whether to restore it.

### 2.2 Track - `common/doctrines/tracks/*.txt`

Tracks are the smallest objects. They carry presentation and the default Mastery source.

```
infantry = {
    name = DOCTRINE_TRACK_INFANTRY
    background = "GFX_grand_battleplan_bg"
    background_offset = 10                       # optional horizontal nudge
    frame = GFX_NAME                             # optional
    icon = "GFX_doctrine_milestone_infantry_land"    # the milestone icon
    icon_frame = "GFX_doctrine_decor_land"

    active = { <trigger> }                       # optional; track hidden/locked when false

    mastery = {
        multiplier = 1.0
        categories = { category_all_infantry }   # subunit categories that generate mastery
        sub_units  = { armored_car }             # specific subunits
        equipment  = { fighter interceptor }     # equipment archetype categories (air/naval)
    }
}
```

`multiplier` scales the manpower contribution, i.e. **higher multiplier = less manpower needed for
the same mastery**. Vanilla values show the intent clearly: `operations` 0.7 (huge manpower pool, all
of infantry + artillery + armor feeds it), `infantry` 1.0, `combat_support` 8.0, `armor` 10.0,
all air tracks 8.0, special forces 6.0. Tune this per track against how many divisions realistically
feed it, not as a difficulty knob.

`active` is used by vanilla's `special_forces_second` track, which calls the scripted trigger
`can_unlock_second_track_of_sf_doctrine`. It is **not** in the bundled `_documentation.md`.

### 2.3 Grand doctrine - `common/doctrines/grand_doctrines/*.txt`

```
new_mobile_warfare = {
    folder = land
    name = GRAND_DOCTRINE_MOBILE_WARFARE
    description = GRAND_DOCTRINE_MOBILE_WARFARE_DESC
    icon = GFX_doctrine_mobile_warfare_medium

    available = { always = yes }   # can it be selected
    visible  = { <trigger> }       # is it listed at all (optional)

    xp_cost = 100
    xp_type = army                 # army | navy | air

    ai_will_do = { base = 1  modifier = { factor = 0 is_major = no } }

    tracks = { infantry combat_support armor operations }

    # activation effects, applied while this grand doctrine is active
    planning_speed = 0.20
    army_speed_factor = 0.10
    enable_tactic = tactic_unexpected_thrust

    milestones = {                 # ORDER-MATCHED to `tracks`, positional, unnamed
        { org_loss_when_moving = -0.15  land_reinforce_rate = 0.02  enable_tactic = tactic_delay
          effect = { ... } }
        { ... }   # combat_support
        { ... }   # armor
        { ... }   # operations
    }
}
```

**`milestones` is positional.** The Nth block belongs to the Nth entry in `tracks`. There is no name
key and no loc key - the UI composes the title from `DOCTRINE_MILESTONE_TITLE` and the grand
doctrine's name. Reordering `tracks` silently reassigns every milestone; this is the easiest way to
break a converted file.

Vanilla milestones additionally bump a country variable (`infantry_milestone_var`,
`support_milestone_var`, `armor_milestone_var`, `operations_milestone_var`) inside `effect = { }`.
Other vanilla content reads those variables, so keep the pattern if CWIC ever relies on it.

### 2.4 Subdoctrine - `common/doctrines/subdoctrines/<folder>/*.txt`

```
mobile_infantry = {
    track = infantry                                   # or: track = { special_forces_first special_forces_second }
    name = SUBDOCTRINE_MOBILE_INFANTRY
    description = SUBDOCTRINE_MOBILE_INFANTRY_DESC
    icon = GFX_doctrine_mobile_infantry_medium
    reward_gfx = GFX_NAME                              # optional custom reward icon strip

    xp_cost = 100
    xp_type = army

    available = { always = yes }
    visible   = { has_dlc = "Arms Against Tyranny" }   # optional
    xor       = { mountaineers_2 }                     # optional mutual exclusion

    ai_will_do = { base = 1  modifier = { factor = 95 original_tag = GER } }

    mastery = { ... }        # optional; REPLACES the track's mastery block for this subdoctrine

    # base activation effects, applied the moment the subdoctrine is slotted
    enable_tactic = tactic_overwhelming_fire
    category_all_infantry = { breakthrough = 0.1 }
    effect = { add_tech_bonus = { bonus = 0.5 uses = 1 category = motorized_equipment name = SUBDOCTRINE_MOBILE_INFANTRY } }

    rewards = {
        cavalry_charge          = { category_cavalry = { breakthrough = 0.20 } }
        combined_arms_planning  = { category_all_infantry = { max_organisation = 10 maximum_speed = 0.05 } }
        decisive_operations     = { ... }
        delegated_authority     = { ... }
        maneuver_warfare        = { ... }
    }
}
```

Points that matter for conversion:

- **Rewards are named keys, not anonymous blocks.** The name is the loc key stem (see section 4).
  The bundled `_documentation.md` shows anonymous `{ }` blocks; that is out of date.
- **Five rewards is the vanilla standard** across all 95 subdoctrines. The engine does not require
  five, but the reward icon strip and the milestone pacing are built around it.
- Each reward may set `mastery = <n>` to override `NDoctrines.DEFAULT_REWARD_MASTERY` (100). Vanilla
  special forces uses 60 per reward; land/air/naval leave it at the default. Note the **absolute**
  values are thresholds, not increments - vanilla SF sets `mastery = 60` on every one of its five,
  which is the per-reward requirement, so tune with the track multiplier in mind.
- `xor` is real and undocumented in the bundled files. Vanilla uses it for the paired special-forces
  subdoctrines (`mountaineers_1` xor `mountaineers_2`, etc.).
- `track` accepts a single value or a list. A subdoctrine listed for two tracks can be slotted into
  either.
- The per-subdoctrine `mastery` block **replaces**, not merges with, the track's. Vanilla special
  forces uses this so each SF subdoctrine only levels from its own unit type.

### 2.5 Activation effects (shared by grand doctrines, milestones, subdoctrines and rewards)

All four object kinds accept the same payload grammar:

| Form | Example |
| --- | --- |
| Bare country modifier | `planning_speed = 0.4` |
| Explicit block | `modifiers = { planning_speed = 0.4 }` |
| Unit-category stat bonus | `category_tanks = { max_organisation = 1 }` |
| Single subunit stat bonus | `armored_car = { max_organisation = 2 }` |
| Terrain sub-block inside a subunit | `rangers_support = { snow = { attack = 0.15 } }` |
| Equipment bonus | `equipment_bonus = { capital_ship = { naval_range = 0.10 instant = yes } }` |
| Tactic unlock | `enable_tactic = tactic_blitz` |
| Arbitrary effect | `effect = { add_tech_bonus = { ... } }` / `effect = { unlock_subunit = rangers_support }` |

Use `equipment_bonus` rather than the `add_equipment_bonus` effect: the effect is fire-and-forget and
will **not** be removed if the doctrine changes, whereas the declarative block is tied to the
doctrine's active state. The same reasoning applies generally - anything inside `effect = { }` is a
one-shot that will not be undone on a grand-doctrine switch. Put permanent-feeling bonuses in the
declarative forms and reserve `effect` for genuine one-time grants.

---

## 3. Mastery - how progression actually works

Mastery is per-track, accrued monthly, driven by units.

Defines live in `common/defines/00_defines.lua` under `NDoctrines`:

| Define | Value | Meaning |
| --- | ---: | --- |
| `DEFAULT_REWARD_MASTERY` | 100.0 | Mastery per reward when not overridden |
| `BASE_MASTERY_GAIN_TARGET_MANPOWER` | 100000.0 | Diminishing returns begin past this contributing manpower |
| `TRAINING_MASTERY_GAIN_FACTOR` | 0.1 | Training counts at 10% of combat/mission rate |
| `MAX_MONTHLY_MASTERY_GAIN` | 40.0 | Hard monthly cap |
| `MIN_MASTERY_GAIN_PER_DAY` | 0.0 | Floor once any gain exists |
| `MASTERY_BANK_CONVERSION_RATE` | 0.25 | Rate at which gain is "reserved" when a track is full or empty |
| `MASTERY_BANK_MAX` | 200.0 | Reserve ceiling |
| `MILITARY_ATTACHE_MASTERY_TRANSFER_FACTOR` | 0.1 | Attache leech from the host country's unit gain |
| `THEATER_COMMANDER_UNITS_MASTERY_GAIN_FACTOR_PER_SKILL` | 0.01 | Per attack+defense skill point |
| `NAVAL_MISSION_MASTERY_GAIN_FACTORS` | table | Per naval mission: hold 0.0, patrol 0.2, strike force 0.05, convoy raiding 0.3, convoy escort 0.2, mines 0.2 |

Other relevant defines: `FACTION_DOCTRINE_SHARING_UNLOCK_COST`,
`DOCTRINE_SHARING_BASE_MASTERY_GAIN_MONTHLY` (10), `DOCTRINE_SHARING_MONTHLY_MASTERY_GAIN_PER_COMMANDER` (2),
`INTEL_TO_SHOW_GRAND_DOCTRINE` / `INTEL_TO_SHOW_SUBDOCTRINES` (doctrine intel gating),
and the AI-side `DESIRE_USE_XP_TO_UNLOCK_{LAND,NAVAL,AIR}_DOCTRINE` (0.5 each) plus
`DAYS_BETWEEN_CHECK_BEST_DOCTRINE` (30).

**Reserved / banked mastery:** while a track has no subdoctrine slotted, or is fully complete, 25% of
what would have been gained is banked up to 200. When you then slot a subdoctrine, the bank seeds it.
This is why a country that fights for years before choosing does not start from zero. It also means an
empty track is not a dead track - relevant when designing a folder where players may deliberately wait.

**Design implication for CWIC:** a full track is 5 x 100 = 500 mastery at default, and the monthly cap
is 40, so a track cannot complete faster than ~13 months of maximum-rate warfare. Four land tracks in
parallel means a realistic full-land-doctrine buildout is multi-year. Whatever decade-pacing CWIC
wants has to be expressed through `mastery` thresholds and track `multiplier`, not through dates.

### Mastery-related modifiers

Documented in `common/doctrines/_documentation.md` and auto-localized (no loc key needed):

- `<folder>_doctrine_cost_factor` - e.g. `land_doctrine_cost_factor = -0.15`, cuts XP cost of grand
  doctrines and subdoctrines in that folder.
- `<grand_doctrine>_mastery_gain_factor` - e.g. `new_mobile_warfare_mastery_gain_factor = 0.15`.
- `<subdoctrine>_mastery_gain_factor` - e.g. `guerilla_war_mastery_gain_factor = 0.15`.
- `<track>_track_mastery_gain_factor` - e.g. `infantry_track_mastery_gain_factor = 0.15`.

These generate from the script names, so every doctrine object CWIC defines gets its own modifier for
free - a very cheap hook for focuses, ideas and advisors.

---

## 4. Localisation contract

| Object | Key | Source |
| --- | --- | --- |
| Folder | whatever `name` says, e.g. `land_doctrine_folder` | explicit |
| Grand doctrine | `name` + `description`, e.g. `GRAND_DOCTRINE_MOBILE_WARFARE` / `_DESC` | explicit |
| Track | `name`, e.g. `DOCTRINE_TRACK_INFANTRY` | explicit |
| Subdoctrine | `name` + `description`, e.g. `SUBDOCTRINE_MOBILE_INFANTRY` / `_DESC` | explicit |
| **Reward** | **`<subdoctrine_key>_<reward_key>`** | derived, lowercase |
| Milestone | none - composed from `DOCTRINE_MILESTONE_TITLE` + grand doctrine name | automatic |

Reward example, from `localisation/english/doctrines_l_english.yml`:

```
  mobile_infantry_cavalry_charge: "Modernized Cavalry"
  mobile_infantry_combined_arms_planning: "Infiltration"
  defensive_postures_improvised_fighting_position: "Improvised Fighting Positions"
  line_of_battle_flagships: "Flagship Coordination"
```

Rewards have a **title only** - vanilla ships no `_desc` for them; the tooltip is generated from the
modifiers. The prefixing exists specifically so generic reward keys cannot collide, which is what
lets vanilla special forces reuse `reward_1` ... `reward_5` across eight subdoctrines.

Descriptions are "bindable loc", so `[...]` scopes and promotes work in them.

CWIC's ASCII-only localisation rule applies here as everywhere: no diacritics, no em dashes, no smart
quotes in the yml files.

---

## 5. Script API - effects and triggers

### Effects

```
set_grand_doctrine = new_mobile_warfare      # also valid at country-history top level
set_sub_doctrine   = mobile_infantry         # slots it into its declared track, free

add_mastery = { amount = 100  track = submarines }
add_mastery = { amount = 200  sub_doctrine = mobile_infantry }

add_daily_mastery = { amount = 0.1  days = 180  name = CZE_trust_in_old_guard  folder = air }

add_mastery_bonus = { name = JUNO_invite_japanese_army_advisors  bonus = 0.15  days = 240  track = infantry }
```

`add_mastery` targets either a `track` or a `sub_doctrine`. `add_daily_mastery` grants a flat amount
per day for a duration and can target a whole `folder`. `add_mastery_bonus` is a percentage modifier
for a duration; `name` is the loc key shown in the mastery-gain breakdown tooltip.

Country history usage (vanilla GER) is the canonical bookmark-seeding pattern, and is exactly what
CWIC would need for its 1949/1980 bookmarks:

```
set_grand_doctrine = new_mobile_warfare
set_grand_doctrine = new_convoy_raiding
set_grand_doctrine = new_battlefield_support
set_sub_doctrine = mobile_infantry
add_mastery = { amount = 200  sub_doctrine = mobile_infantry }
set_sub_doctrine = mission_type_tactics
add_mastery = { amount = 100  sub_doctrine = mission_type_tactics }
```

Note that grand doctrines are set one per folder, and each subdoctrine grant is normally paired with
an `add_mastery` so the starting country is partway through the track rather than at zero.

### Triggers

```
has_doctrine = new_mobile_warfare            # grand doctrine OR subdoctrine id
has_completed_subdoctrine = fire_concentration
has_completed_track = armor
has_subdoctrine_in_track = <subdoctrine>
has_mastery = { ... }
has_mastery_level = { amount = 5  sub_doctrine = marines_1 }
```

`has_mastery_level` takes a **reward index** (`amount = 3` means "at least three rewards unlocked"),
not a raw mastery number - see `common/on_actions/00_on_actions.txt` and `common/ideas/_event.txt`.
This is the trigger to use for "the country has progressed far enough in X", and vanilla uses it to
gate real gameplay effects that are only *displayed* as a reward via `custom_effect_tooltip`. That
display-only pattern is worth copying whenever a reward needs a scripted effect rather than a modifier.

### AI

Two separate mechanisms, both needed:

1. **`ai_will_do` inside the doctrine object** decides which grand doctrine / subdoctrine the AI buys.
   Vanilla shape is `base = 1` with tag-specific `factor = 95` spikes and `factor = 0.5 is_major = no`
   dampening. This is a weight, not a gate; use `available` for hard gating.
2. **`common/ai_strategy/doctrines.txt`** adapts AI army composition and behaviour to whatever it
   picked, keyed on `has_doctrine` / `has_completed_track` / `has_completed_subdoctrine`. Vanilla uses
   `role_ratio` and `force_concentration_factor` there, escalating as tracks complete.

> **CWIC drift:** `common/ai_strategy/doctrines.txt` in the mod is a **zero-byte override**, so
> vanilla's entire doctrine-driven AI composition layer is suppressed. Any conversion has to rewrite
> this file, not just the doctrine definitions.

---

## 6. Art and UI

- Icons are declared in `interface/doctrines/doctrines.gfx` as plain `SpriteType`s:
  `name = "GFX_doctrine_mobile_infantry_medium"`, `texturefile = "gfx/interface/doctrines/icons/doctrine_mobile_infantry.dds"`,
  `alwaystransparent = yes`. The `_medium` suffix is a naming convention, not an engine requirement.
- Track backgrounds (`GFX_grand_battleplan_bg`, `GFX_mob_warfare_bg`, ...), milestone icons
  (`GFX_doctrine_milestone_*`) and per-folder decor frames (`GFX_doctrine_decor_land`) are all
  referenced by the track definitions.
- `reward_gfx` on a subdoctrine overrides the default reward icon strip. It is a framed sprite:
  frames 1..X are rewards 1..X lit, frames X+1..2X are the same icons greyed out. For the standard
  five rewards that is a 10-frame strip.
- The view itself is `interface/doctrines/doctrines_view.gui` plus `interface/countrydoctrinetreeview.gui`.

CWIC already ships overrides of all three UI files (`interface/doctrines/doctrines.gfx` 748 vs vanilla
769 lines, `doctrines_view.gui` 719 vs 720, `countrydoctrinetreeview.gui` 3990 vs 456 - the last is a
heavily reworked custom view). It also has ~160 custom doctrine background images registered in
`interface/CWIC_Doctrines.gfx` as `GFX_<bloc>_<decade>_Doctrine_BG` (NATO, Warsaw, Cuba, DPRK, and the
rest). Those backgrounds map naturally onto track `background` slots, but the per-node icons drawn for
the legacy 646-node trees do not map onto a 95-subdoctrine framework without curation.

Remember the standing repo caveat: a `texturefile` missing from the mod may still resolve against the
vanilla install, so check both before "fixing" a sprite, and never infer layout from element names.

---

## 7. Where the bundled `_documentation.md` files are stale

The mod's `common/doctrines/_documentation.md`, `grand_doctrines/_documentation.md`,
`tracks/_documentation.md` and `subdoctrines/_documentation.md` are the November 2025 import and now
differ from the shipped 1.19.2 versions (`folders/_documentation.md` is still identical). Even the
current vanilla docs are incomplete. Confirmed gaps:

| Claim in bundled docs | Reality in 1.19.2 script |
| --- | --- |
| `rewards = { { ... } { ... } }` anonymous blocks | Named keys: `rewards = { cavalry_charge = { ... } }` |
| Reward loc "TODO - how unlocking works" | Loc key is `<subdoctrine>_<reward>`, title only, no `_desc` |
| No mention of `xor` | `xor = { other_subdoctrine }` is used by special forces |
| No mention of track `active` | `special_forces_second` uses `active = { can_unlock_second_track_of_sf_doctrine = yes }` |
| `track = infantry` only | `track = { special_forces_first special_forces_second }` list form is valid |
| `visible` mentioned only in passing | Used in 47 vanilla doctrine objects, mostly for DLC gating |
| No mention of milestone ordering hazard | `milestones` is strictly positional against `tracks` |
| No `has_mastery_level` signature | `{ amount = <reward index>  sub_doctrine = <id> }` |

When in doubt, grep the installed game rather than trusting either doc set.

---

## 8. Current CWIC state and the concrete conversion gaps

As of this branch, the mod suppresses the framework completely: every one of the 21 vanilla gameplay
files under `common/doctrines/` is overridden with a **zero-byte** file, and `folders/doctrine_folders.txt`
is a 35-line snapshot that defines land/naval/air only. That override set is now complete - no vanilla
doctrine file leaks through, which is what fixed the old `can_unlock_second_track_of_sf_doctrine` error.

Loose ends a conversion pass would have to close, beyond writing the doctrine definitions themselves:

1. **Dangling `add_mastery` calls.** `common/factions/goals/faction_goals_medium_term.txt` and
   `faction_goals_long_term.txt` contain five inherited `add_mastery = { track = ... }` calls naming
   `capital_ships`, `heavy_aircraft`, `submarines`, `screens` and `fighter_aircraft` - vanilla track
   names that do not exist in the mod because the track files are empty. Either the converted tracks
   reuse those names or these calls need retargeting.
2. **`common/ai_strategy/doctrines.txt` is empty.** The whole doctrine-to-AI-composition layer is gone.
3. **The `special_forces` folder is missing** from the mod's folders file.
4. **No country history grants.** Nothing in the mod calls `set_grand_doctrine` / `set_sub_doctrine`,
   so every bookmark would start doctrine-blank under the new system.
5. **Loc.** `localisation/english/doctrine_l_english.yml` (142 lines) and `Land_Doctrine_l_english.yml`
   (1749 lines) are written for legacy technology IDs. Reward keys under the new system have a
   different, derived shape entirely.
6. **Art curation.** ~160 bloc/decade backgrounds fit tracks; the legacy per-node icon set does not
   transfer one-for-one.

### The design problem, stated plainly

The legacy CWIC land tree is **17 bloc columns x 6 decades = 78 cells / 528 nodes**, with lineage
gating so a country commits to a doctrinal family and walks it forward through the Cold War. The new
framework offers **4 grand doctrines x 4 tracks x N subdoctrines**, with no decade axis and no
lineage - only "pick one of each, then grind mastery".

These are not the same shape, and no mechanical translation exists. A conversion has to answer:

- Does a **bloc** (NATO, Warsaw Pact, Maoist, Foco, ...) become a **grand doctrine**? That gives ~11-17
  grand doctrines in the land folder against vanilla's 4 - allowed, but it makes the folder a bloc
  picker and leaves the four tracks to carry all the internal variety.
- Or does a bloc become a **subdoctrine family**, with grand doctrines being broad postures? That
  preserves vanilla's shape but flattens the bloc identity CWIC's art and loc are built around.
- Where does the **decade progression** go? There is no date axis in the framework. Options are
  `available` triggers on subdoctrines (date-gated slotting), reward `mastery` thresholds tuned so
  progression is slow, or accepting that decades stop being a mechanic.
- What happens on a **bloc realignment** mid-campaign? Switching grand doctrine wipes all mastery,
  which is a much harsher penalty than the legacy tree's "you cannot switch at all".

Answer those four before writing any script. The first three sections of this document are stable
reference; that list is the actual open work.

---

## 9. If someone does start the conversion

Order that avoids the previous false start:

1. **Decide the mapping first** (the four questions above), in writing, in this directory.
2. Build a **vertical slice**: the `land` folder, one grand doctrine, all four of its tracks, one
   subdoctrine per track with five rewards, full loc, real icons. Do not convert breadth-first.
3. Delete the zero-byte overrides **only for the files the slice populates**. Leave the rest empty so
   vanilla content cannot leak in half-converted.
4. Re-park the legacy trees back under `common/technologies/doctrine rework/` **after** the slice
   loads, not before - the two systems must never both be live.
5. Add doctrine checks to `tools/validate_military_reworks.py`: track/subdoctrine name resolution,
   `tracks` vs `milestones` count parity per grand doctrine, reward loc key existence, GFX resolution.
6. Only then go wide.

Cross-references: `Doctrine_Rework_Investigation.md` (why both systems were parked, and the July 2026
decision trail), `Doctrine_Rework_Plan.md` + `Doctrine_Cell_Manifest.md` + `Land_Doctrine_Tree_Structure.md`
(the legacy architecture that currently ships), `Doctrine_Icon_Art_Requests.md` (existing art backlog).
