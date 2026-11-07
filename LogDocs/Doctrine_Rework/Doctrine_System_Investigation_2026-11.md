# Doctrine System Investigation (2026-11-06)

Supersedes the architecture sections of `Doctrine_Rework_Investigation.md`,
`Doctrine_Rework_Plan.md`, `Doctrine_Cell_Manifest.md` and
`Land_Doctrine_Tree_Structure.md`. `New_Doctrine_System_Reference.md` stays valid as the
engine reference (sections 1-7); its section 8 "current state" is out of date, see below.

Game: HOI4 `Operation Postern v1.19.4.2`. Repo: `development-branch` at `49a45bdcba`.

## 1. HOI4 doctrine history, verified

| Era | Model | Evidence |
| --- | --- | --- |
| 1.0 - 1.16 | Doctrines are technologies (`doctrine = yes`) in `land/naval/air_doctrine_folder`, researched in the tech ledger. | Vanilla 1.19 still declares those four folders in `common/technology_tags/00_technology.txt` with zero technologies assigned. |
| 1.17 (2025-11-20, released with *No Compromise, No Surrender*) | Free base-game rework: Folder -> Grand Doctrine -> Track -> Subdoctrine -> 5 Rewards, unlocked by Mastery earned from units in action. XP buys the grand doctrine and each subdoctrine. | `common/doctrines/**` in the install; wiki "For the pre-1.17 doctrine system, see a previous version". |
| 1.17 - 1.19.4 | Same framework; vanilla keeps tuning content. | Install. |

Corrections to the AI summary in the request:

- The framework itself is **not DLC content.** Only individual subdoctrines are DLC-gated, via
  `visible = { has_dlc = ... }`: 28 NCNS, 9 La Resistance, 7 Arms Against Tyranny, 4 By Blood Alone,
  2 Gotterdammerung, 1 Thunder at Our Gates.
- The **special forces folder** is the one folder-level gate:
  `allowed = { OR = { has_dlc = "No Compromise, No Surrender" has_dlc = "Arms Against Tyranny" } }`.
- The "1.11 moved doctrines to XP" claim is unverified and irrelevant to the target engine; it was not
  used for any decision.

DLC compatibility rule that follows: everything core must be ungated; a DLC-gated object needs an
ungated equivalent on the same track so no-DLC players never face an empty slot.

## 2. Current CWIC state: no doctrines exist at all

| Piece | State |
| --- | --- |
| New framework | `.mod` has `replace_path` on `grand_doctrines`, `subdoctrines/{air,land,sea,special_forces}`, `tracks`. Those dirs hold only `_documentation.md`. Zero grand doctrines, tracks, subdoctrines load. (The zero-byte override set described in older docs is gone; `replace_path` replaced it.) |
| Folders | `common/doctrines/folders/doctrine_folders.txt` overrides vanilla: land/naval/air only, **special_forces dropped**. |
| Legacy trees | Parked in `common/technologies/doctrine rework/` (not loaded): land 15,048 lines / 528 nodes, air 2,826 / 73, naval 1,976 / 45, SF empty. Parked again by `66c37cf447` (2026-09-05). |
| Tech folders | `old_{land,naval,air}_doctrine_folder` + `special_forces_doctrine_folder`, `doctrine = yes`, no technologies. Dead. |
| Rework branch | `tank-designer-and-doctrine-rework-test` is fully merged (tip `e650599da8` is an ancestor of HEAD). Nothing left on it to pick up. |
| AI | `common/ai_strategy` is `replace_path`; no doctrine strategy file. |
| Country history | No `set_grand_doctrine` / `set_sub_doctrine`. |

### Live consequences

1. **14 vanilla combat tactics are unreachable.** `common/combat_tactics.txt` is vanilla; its doctrine
   tactics are unlocked only by `enable_tactic` in vanilla doctrines. Only `tactic_elastic_defense` and
   `tactic_unexpected_thrust` are enabled anywhere in the mod.
2. **217 `add_doctrine_cost_reduction` rewards** across 77 files feed a system with nothing to buy.
   Categories used: `land_doctrine` 116, `cat_air_doctrine` 67, `naval_doctrine` 31, plus
   `fleet_in_being_tree`, `cat_mass_assault`, `air_doctrine` once each. Vanilla uses `land_doctrine`,
   `air_doctrine`, `naval_doctrine`, `special_forces_doctrine`. The mod's tag file has no plain
   `air_doctrine` or `special_forces_doctrine`, so the 67 air rewards are likely inert
   **[INFERENCE: engine folder mapping; confirm at runtime]**.
3. Army/navy/air XP has no doctrine sink.

## 3. Why vanilla content cannot be reused

CWIC replaces `common/units`. Vanilla doctrines name **48 subunits CWIC does not define**
(`armored_car`, `mechanized`, `motorized`, `anti_tank_brigade`, `battleship`, `submarine`,
`carrier`, `helicopter_*`, ...). Unit *categories* all resolve. A CWIC doctrine set must be written
against CWIC's 136 subunits and 66 categories (`category_helicopters`, `category_drone`,
`category_jump_jet`, `category_light_infantry`, ...). Vanilla's 14 `enable_tactic` values are reusable.

## 4. What to keep from the legacy rework

| Keep | Drop |
| --- | --- |
| Bloc identity: 18 land columns (NATO, SADF, France, Israel, Warsaw, DPRK, Cuba, Foco, Maoist, Insurgency, Hybrid, Regional Islamist, Transnational Islamist, Himalayan, Iran, Non-Aligned, PRC, Yugoslav). | The 646-node tech-tree format, grid GUI and `old_*_doctrine_folder` registration. |
| Lineage idea (SADF from NATO, DPRK from Warsaw, Cuba from Foco, insurgent descendants). | Header/terminal `allow` gating, cell manifest, decade grid. |
| Decade progression as a design goal. | 448 placeholder icons; per-node art requests. |
| ~160 bloc/decade background images in `interface/CWIC_Doctrines.gfx` (map onto track backgrounds and grand-doctrine art). | `Land_Doctrine_l_english.yml` keys (legacy IDs); text may be mined. |
| Air 3 roots (versatile/systemic/integral) and naval 3 roots (fleet_in_being/trade_interdiction/base_strike) as concepts. | Effects as written: "conservative" placeholder bonuses added in bulk in `7b50137918`. |
| `tools/validate_military_reworks.py` as the validator home. | Its legacy doctrine assertions. |

## 5. Engine facts that constrain the design

- No decade axis. Era progression must come from subdoctrine `available` date triggers and reward
  `mastery` thresholds.
- Switching grand doctrine resets mastery. Lineage (NATO -> SADF) cannot be a grand-doctrine switch
  without that penalty; it must live in subdoctrine availability under one grand doctrine.
- No active `add_mastery` calls exist in the mod (the five faction-goal calls the older reference lists
  are gone; one commented `add_daily_mastery` remains). Track IDs are unconstrained.
- Bookmark seeding uses `set_grand_doctrine`, `set_sub_doctrine`, `add_mastery` in country history.
- `milestones` are positional against `tracks`.
- Reward loc key is `<subdoctrine>_<reward>`; no `_desc`.
