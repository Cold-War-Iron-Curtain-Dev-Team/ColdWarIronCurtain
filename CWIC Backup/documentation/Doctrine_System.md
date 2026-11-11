# Doctrines - Developer Guide

How CWIC's doctrines are built and how to change them. All game paths are under
`Cold War Iron Curtain/`. Tools live in `CWIC Backup/tools/`.

CWIC uses HOI4's grand doctrine framework (`common/doctrines/`, game 1.17+). The old technology-tree
doctrines are gone. The framework is base-game, so everything works without DLC; only the special
forces folder needs a DLC (Arms Against Tyranny or No Compromise, No Surrender), exactly like vanilla.

## How the framework works

| Object | What it is | Where |
| --- | --- | --- |
| Folder | Land, naval, air, special forces tab | `common/doctrines/folders/doctrine_folders.txt` |
| Grand doctrine | One per folder, bought with XP. Lists its tracks and one milestone per track | `common/doctrines/grand_doctrines/` |
| Track | A slot that holds one subdoctrine. Owns the mastery source and background art | `common/doctrines/tracks/` |
| Subdoctrine | Bought with XP into a track. Has 5 named rewards unlocked by mastery | `common/doctrines/subdoctrines/<folder>/` |

- Mastery comes from units fighting or training. 100 mastery per reward by default, 500 completes a
  subdoctrine (special forces rewards cost 60).
- **Swapping the subdoctrine in a track resets that track's mastery to 0.** Tested in game. This is
  why CWIC uses era rows instead of era replacements.
- Switching grand doctrine resets all mastery in that folder.
- `milestones` in a grand doctrine are **positional**: the Nth milestone belongs to the Nth track in
  `tracks`. Reordering one list without the other silently reassigns every milestone.
- Reward loc key is `<subdoctrine>_<reward>` (title only). Grand doctrines and subdoctrines use
  their `name` and `description` keys.

Engine reference: vanilla `common/doctrines/**` and `common/doctrines/_documentation.md` files.
Shipped vanilla script beats the bundled docs when they disagree.

## CWIC structure

### Land: seven schools, three era rows

Each land grand doctrine is a Cold War school. Bloc lineages that would otherwise be separate
grand doctrines (SADF, DPRK, Cuba, hybrid/Islamist insurgency) are school-exclusive subdoctrines, so
following a lineage never costs a mastery wipe.

| Grand doctrine | School | Typical users |
| --- | --- | --- |
| `cw_forward_defense` | NATO forward defense to AirLand Battle | USA, UK, West Germany, NATO, South Africa, South Korea |
| `cw_deep_battle` | Soviet deep battle | USSR, Warsaw Pact, North Korea, Soviet clients |
| `cw_peoples_war` | Maoist people's war | PRC, North Vietnam, Maoist movements |
| `cw_intervention_pacification` | French intervention and guerre revolutionnaire | France, Portugal, Belgium |
| `cw_preemptive_maneuver` | Israeli preemptive armoured maneuver | Israel |
| `cw_total_national_defense` | Territorial and total defense | Yugoslavia, Sweden, Switzerland, Finland, Austria, India, Iran |
| `cw_revolutionary_insurgency` | Foco, insurgency, irregular war | Cuba, liberation movements |

Every land grand doctrine has **12 tracks in three rows of four** (`max_track_columns = 4`):

| Row | Track ids | Unlocks |
| --- | --- | --- |
| 1945-1959 | `cw_<school>_infantry`, `_combat_support`, `_armor`, `_operations` | start |
| 1960s | the same with `_e2` | `active = { NOT = { date < 1960.1.1 } }` |
| 1980s | the same with `_e3` | `active = { NOT = { date < 1980.1.1 } }` |

Tracks are per school, so each school has its own track art. Shared subdoctrines list the
matching track of all seven schools in `track = { ... }`; school subdoctrines list only their own.

### Naval and air: shared tracks, three era rows

Three grand doctrines each, all using the same 12 tracks (`<base>`, `<base>_e2`, `<base>_e3`):

- Naval: `cw_sea_control`, `cw_sea_denial`, `cw_power_projection`; bases `capital_ships`,
  `carriers`, `screens`, `submarines`.
- Air: `cw_air_superiority`, `cw_strategic_deterrence`, `cw_integrated_air_land`; bases
  `fighter_aircraft`, `strike_aircraft`, `medium_aircraft`, `heavy_aircraft`.

Base track ids are vanilla's, so vanilla `DOCTRINE_TRACK_*` loc and any `add_mastery = { track = ... }`
written against vanilla names keep working.

### Special forces

Four grand doctrines (`cw_sf_mass_airborne`, `cw_sf_elite_commandos`,
`cw_sf_unconventional_warfare`, `cw_sf_deep_reconnaissance`), 2 x 2 tracks:
`special_forces_first`, `special_forces_second`, plus `_e2` versions unlocking in 1970.
The second column needs `sf_trees > 1`, set by the `diversify_special_forces` decision
(`common/decisions/_generic_decisions.txt`, operations category) through
`add_potential_special_forces_tree`. Subdoctrines come in `xor` pairs per unit family and each has
its own `mastery` block sourced from its unit.

### Era gating rule

A subdoctrine's era is its `available` date gate, and it must sit in the matching row:
no gate = base track, `1960.1.1` = `_e2`, `1980.1.1` = `_e3` (special forces: `1970.1.1` = `_e2`).
School gating is `visible` and `available` both checking `has_doctrine = <grand doctrine>`.

## Files

| What | Path |
| --- | --- |
| Folders (SF DLC gate) | `common/doctrines/folders/doctrine_folders.txt` |
| Tracks | `common/doctrines/tracks/CWIC_{land,naval,air,special_forces}_tracks.txt` |
| Grand doctrines | `common/doctrines/grand_doctrines/CWIC_{land,naval,air,special_forces}_grand_doctrines.txt` |
| Land subdoctrines, shared | `subdoctrines/land/CWIC_land_{infantry,combat_support,armor,operations}_subdoctrines.txt` |
| Land subdoctrines, per school | `subdoctrines/land/CWIC_land_<school>_subdoctrines.txt` |
| Naval / air / SF subdoctrines | `subdoctrines/sea/CWIC_naval_subdoctrines.txt`, `air/CWIC_air_subdoctrines.txt`, `special_forces/CWIC_special_forces_subdoctrines.txt` |
| Localisation | `localisation/english/CWIC_doctrines_{land,naval,air,special_forces}_l_english.yml` |
| AI army composition per doctrine | `common/ai_strategy/CWIC_doctrines.txt` |
| Bookmark seeding | `history/countries/*.txt`, dated `1949.1.1` and `1980.1.1` blocks |
| Sprites | `interface/CWIC_Doctrines.gfx` (track, medallion, icon), `interface/doctrines/doctrines.gfx` (frames, folder icons) |
| Art | `gfx/interface/doctrines/cwic/{tracks,grand,icons,ui}/`, credits in `gfx/interface/doctrines/cwic/CREDITS.md` |
| Doctrine view layout | `interface/doctrines/doctrines_view.gui`, officer corps buttons in `interface/countryofficercorpview.gui` |

`.mod` has `replace_path` on the vanilla grand doctrine, subdoctrine and track folders, so no
vanilla doctrine leaks in.

## Recipes

### Add a subdoctrine

1. Pick the folder, base track and era. Write it in the matching file, copying an existing entry's
   shape: `track`, `name`, `description`, `icon`, `xp_cost = 100`, `xp_type`, `available`,
   optional `visible`, `ai_will_do`, base effects, exactly **5 named rewards**.
2. Land: `track` lists the era's track for every school that should see it.
   School-only: one track plus `visible`/`available` with `has_doctrine`.
3. Add loc: name, description and one key per reward (`<subdoctrine>_<reward>`), ASCII, file keeps
   its BOM.
4. Icon: `icon = GFX_cw_sd_<subdoctrine>`. Add the photo through the art pipeline (below), which
   writes the PNG; declare the sprite in `interface/CWIC_Doctrines.gfx`.
5. Add the id to the appendix of this file (the validator compares them).
6. Run the validator.

### Add a grand doctrine

Copy an existing one in the same folder. Keep the same `tracks` list (land: create the 12
`cw_<school>_*` tracks in `CWIC_land_tracks.txt` too, with art) and write one milestone per track in
the same order. Medallion `GFX_cw_gd_<id>`. Add to the appendix.

### Add an era row

Add the tracks with an `active` date gate, append them to every grand doctrine's `tracks` in that
folder, append one milestone per new track, move the era's subdoctrines onto them, add track loc
(`DOCTRINE_TRACK_CW_<BASE>_E<n>`) and art, and update `DOCTRINE_*_ERAS` in the validator.

### Seed a country at a bookmark

In the country's history file:

```text
1949.1.1 = {
    set_grand_doctrine = cw_forward_defense
    set_sub_doctrine = cw_covering_force_screen
}
1980.1.1 = {
    set_sub_doctrine = cw_panzergrenadier_defense
    add_mastery = { amount = 500 sub_doctrine = cw_covering_force_screen }
    add_mastery = { amount = 500 sub_doctrine = cw_panzergrenadier_defense }
}
```

- Both blocks run at the 1980 bookmark (1949 first). Don't repeat the 1949 `set_sub_doctrine`.
- Rule for 1980: if a country holds a doctrine in a folder, **every** 1945 and 1960s track of its
  grand doctrine in that folder has a subdoctrine at 500 mastery. 1980s tracks get 100.
- One subdoctrine per track. Special forces seeding must sit inside a DLC check.

### Reference doctrines from other content

| Need | Use |
| --- | --- |
| Has a doctrine | `has_doctrine = <grand doctrine or subdoctrine>` |
| Completed a subdoctrine (even if swapped out) | `has_completed_subdoctrine = <id>` |
| Completed a track | `has_completed_track = <track>`. Land tracks are per school: OR over the schools/eras you mean |
| Grant mastery | `add_mastery = { amount = N sub_doctrine = X }` or `track = <track>` |
| Cheaper doctrines | `add_doctrine_cost_reduction = { name = X cost_reduction = 0.25 uses = 1 category = land_doctrine }` with category `land_doctrine`, `naval_doctrine`, `air_doctrine` or `special_forces_doctrine` |

`add_tech_bonus` does nothing for doctrines; they are not technologies.

## Rules that have cost a debugging cycle

- Unit stats go inside a unit or category block: `category_army = { defense = 0.05 }`. Bare
  `attack`, `defense` or `initiative` in a doctrine is a parse error. `attack`/`movement` are only
  valid inside terrain blocks (`mountain = { attack = 0.1 movement = 0.1 }`).
- Air stats (`air_attack`, `air_agility`, `air_range`, `air_bombing`, `air_ground_attack`,
  `air_defence`) only inside `category_fighter`, `category_cas`, `category_tac_bomber`,
  `category_strat_bomber`, etc.
- Naval coordination modifiers (`convoy_raiding_coordination`, `patrol_coordination`) only inside a
  hull block (`sub_hull_large_double = { ... }`).
- Mastery `sub_units` takes subunit names; categories go in `categories`.
- Reference only CWIC subunits. Vanilla doctrine content names dozens of units CWIC replaces
  (`mechanized`, `armored_car`, `battleship`...).
- No `has_dlc` outside special forces content.
- Keep `effect = { }` for one-shot grants; anything there is not undone when the doctrine changes.
- A failed track or sprite usually logs nothing useful. Look at the screen, not only at `error.log`.

## AI

- Engine purchase drive: vanilla defines `DESIRE_USE_XP_TO_UNLOCK_{LAND,NAVAL,AIR}_DOCTRINE`
  (CWIC does not override them).
- Choice: `ai_will_do` on each grand doctrine carries historical `original_tag` weights and
  faction/ideology fallbacks; subdoctrines carry tag weights and a boost for their own school.
- Composition after the choice: `common/ai_strategy/CWIC_doctrines.txt` (role ratios keyed on
  `has_doctrine` / `has_completed_track`).

## Art pipeline

`CWIC Backup/tools/doctrine_art/build.py` regenerates every doctrine image:

- `picks.json`: sprite -> chosen photo (`picked/*.jpg`), source, licence, crop focus, optional
  `mode = fit` for wide images (whole image over a blurred fill).
- `banners/`: the original bloc/decade banners (source only, not loaded by the game).
- `legacy/`: icons from the old doctrine trees still used by some land subdoctrines.
- Every image gets the CRT treatment; track backgrounds also get the soften pass
  (`soften_track`) so overlaid UI reads cleanly; icons get the circle mask.

To change an image: add or replace the photo in `picked/`, update its `picks.json` entry, run
`python3 build.py` (about 2 minutes), add the credit line in `CREDITS.md`.

## Validation

```bash
python3 "CWIC Backup/tools/validate_military_reworks.py"
```

Doctrine checks: track existence and era gates, tracks vs milestones count, `max_track_columns`,
subdoctrine era vs track suffix, 5 rewards, loc keys, sprites, units and categories, no `has_dlc`
outside SF, and that every grand doctrine and subdoctrine id appears in the appendix below.

## Appendix: doctrine ids

Generated from `common/doctrines`. Era: 1 = start, 2 = 1960 (SF 1970), 3 = 1980. Gate = grand doctrines that can see it.

### Land

Grand doctrines: `cw_forward_defense`, `cw_deep_battle`, `cw_peoples_war`, `cw_intervention_pacification`, `cw_preemptive_maneuver`, `cw_total_national_defense`, `cw_revolutionary_insurgency`

| Subdoctrine | Track | Era | Gate |
| --- | --- | --- | --- |
| `cw_ambush_tank_destroyers` | armor | 1 | cw_total_national_defense |
| `cw_colonial_light_armor` | armor | 1 | cw_intervention_pacification |
| `cw_hull_down_ambush` | armor | 1 | cw_forward_defense |
| `cw_improvised_armored_brigades` | armor | 1 | cw_preemptive_maneuver |
| `cw_infantry_accompanying_tanks` | armor | 1 | cw_peoples_war |
| `cw_infantry_support_armor` | armor | 1 | all |
| `cw_tank_army_breakthrough` | armor | 1 | cw_deep_battle |
| `cw_tank_heavy_formations` | armor | 1 | all |
| `cw_technicals_and_captured_armor` | armor | 1 | cw_revolutionary_insurgency |
| `cw_all_tank_doctrine` | armor | 2 | cw_preemptive_maneuver |
| `cw_antitank_defense_in_depth` | armor | 2 | all |
| `cw_cavalry_reconnaissance_armor` | armor | 2 | cw_intervention_pacification |
| `cw_combined_arms_battalions` | armor | 2 | all |
| `cw_cross_attached_task_forces` | armor | 2 | cw_forward_defense |
| `cw_hull_down_armor` | armor | 2 | cw_total_national_defense |
| `cw_nuclear_battlefield_armor` | armor | 2 | cw_deep_battle |
| `cw_rpg_ambush_teams` | armor | 2 | cw_revolutionary_insurgency |
| `cw_tank_hunter_teams` | armor | 2 | cw_peoples_war |
| `cw_armored_cavalry_screen` | armor | 3 | all |
| `cw_combined_arms_restoration` | armor | 3 | cw_preemptive_maneuver |
| `cw_group_army_armor` | armor | 3 | cw_peoples_war |
| `cw_heavy_corps_gunnery` | armor | 3 | cw_forward_defense |
| `cw_manpads_and_advanced_antiarmor` | armor | 3 | cw_revolutionary_insurgency |
| `cw_mbt_maneuver_groups` | armor | 3 | all |
| `cw_operational_maneuver_groups` | armor | 3 | cw_deep_battle |
| `cw_territorial_armor_reserve` | armor | 3 | cw_total_national_defense |
| `cw_wheeled_gun_armor` | armor | 3 | cw_intervention_pacification |
| `cw_artillery_breakthrough_divisions` | combat_support | 1 | cw_deep_battle |
| `cw_combat_engineering` | combat_support | 1 | all |
| `cw_groupes_mobiles` | combat_support | 1 | cw_intervention_pacification |
| `cw_heavy_mortar_improvisation` | combat_support | 1 | cw_preemptive_maneuver |
| `cw_improvised_explosive_devices` | combat_support | 1 | cw_revolutionary_insurgency |
| `cw_infantry_heavy_weapons` | combat_support | 1 | cw_peoples_war |
| `cw_massed_artillery_fires` | combat_support | 1 | all |
| `cw_obstacle_engineering` | combat_support | 1 | cw_total_national_defense |
| `cw_tactical_air_control` | combat_support | 1 | cw_forward_defense |
| `cw_air_defense_umbrella` | combat_support | 2 | cw_deep_battle |
| `cw_army_aviation` | combat_support | 2 | all |
| `cw_atgm_screening_belts` | combat_support | 2 | cw_forward_defense |
| `cw_helicopter_fire_support` | combat_support | 2 | cw_intervention_pacification |
| `cw_mountain_warfare_corps` | combat_support | 2 | cw_total_national_defense |
| `cw_rocket_and_mortar_harassment` | combat_support | 2 | cw_revolutionary_insurgency |
| `cw_sapper_demolition_units` | combat_support | 2 | cw_peoples_war |
| `cw_self_propelled_armored_fire` | combat_support | 2 | cw_preemptive_maneuver |
| `cw_tactical_nuclear_fires` | combat_support | 2 | all |
| `cw_antitank_missile_belts` | combat_support | 3 | cw_total_national_defense |
| `cw_drone_suppression_of_defenses` | combat_support | 3 | cw_preemptive_maneuver |
| `cw_electronic_warfare_support` | combat_support | 3 | all |
| `cw_follow_on_forces_attack` | combat_support | 3 | cw_forward_defense |
| `cw_hybrid_irregular_warfare` | combat_support | 3 | cw_revolutionary_insurgency |
| `cw_massed_air_defense` | combat_support | 3 | cw_peoples_war |
| `cw_overseas_pre_positioning` | combat_support | 3 | cw_intervention_pacification |
| `cw_reconnaissance_fire_complex` | combat_support | 3 | cw_deep_battle |
| `cw_reconnaissance_strike_complex` | combat_support | 3 | all |
| `cw_sanctuary_logistics` | combat_support | 3 | cw_revolutionary_insurgency |
| `cw_covering_force_screen` | infantry | 1 | cw_forward_defense |
| `cw_echeloned_rifle_assault` | infantry | 1 | cw_deep_battle |
| `cw_foco_vanguard` | infantry | 1 | cw_revolutionary_insurgency |
| `cw_human_wave_tactics` | infantry | 1 | cw_peoples_war |
| `cw_legion_parachute_regiments` | infantry | 1 | cw_intervention_pacification |
| `cw_mass_infantry_assault` | infantry | 1 | all |
| `cw_nahal_citizen_army` | infantry | 1 | cw_preemptive_maneuver |
| `cw_rifle_company_firepower` | infantry | 1 | all |
| `cw_territorial_defense_forces` | infantry | 1 | cw_total_national_defense |
| `cw_airmobile_infantry` | infantry | 2 | all |
| `cw_bush_war_mobility` | infantry | 2 | cw_forward_defense |
| `cw_fortress_belt_defense` | infantry | 2 | cw_total_national_defense |
| `cw_juche_infiltration_warfare` | infantry | 2 | cw_deep_battle |
| `cw_main_force_local_force` | infantry | 2 | cw_peoples_war |
| `cw_mechanized_infantry_integration` | infantry | 2 | all |
| `cw_motor_rifle_divisions` | infantry | 2 | cw_deep_battle |
| `cw_panzergrenadier_defense` | infantry | 2 | cw_forward_defense |
| `cw_protracted_peoples_war` | infantry | 2 | cw_revolutionary_insurgency |
| `cw_sayeret_deep_raids` | infantry | 2 | cw_preemptive_maneuver |
| `cw_zone_commandos` | infantry | 2 | cw_intervention_pacification |
| `cw_airmobile_assault_brigades` | infantry | 3 | cw_deep_battle |
| `cw_citizen_army_mobilization` | infantry | 3 | cw_total_national_defense |
| `cw_dismounted_atgm_teams` | infantry | 3 | all |
| `cw_fist_units` | infantry | 3 | cw_peoples_war |
| `cw_heavy_apc_infantry` | infantry | 3 | cw_preemptive_maneuver |
| `cw_light_infantry_divisions` | infantry | 3 | all |
| `cw_mujahideen_cell_networks` | infantry | 3 | cw_revolutionary_insurgency |
| `cw_rapid_action_force` | infantry | 3 | cw_intervention_pacification |
| `cw_urban_terrain_defense` | infantry | 3 | cw_forward_defense |
| `cw_cross_border_sanctuaries` | operations | 1 | cw_revolutionary_insurgency |
| `cw_delaying_defense` | operations | 1 | cw_total_national_defense |
| `cw_forward_strategy` | operations | 1 | cw_forward_defense |
| `cw_guerre_revolutionnaire` | operations | 1 | cw_intervention_pacification |
| `cw_mobile_counterattack` | operations | 1 | all |
| `cw_operational_echelonment` | operations | 1 | cw_deep_battle |
| `cw_positional_defense` | operations | 1 | all |
| `cw_preemptive_first_strike` | operations | 1 | cw_preemptive_maneuver |
| `cw_protracted_war` | operations | 1 | cw_peoples_war |
| `cw_active_defense` | operations | 2 | cw_forward_defense |
| `cw_counterinsurgency_operations` | operations | 2 | all |
| `cw_flexible_response_operations` | operations | 2 | all |
| `cw_forward_detachments` | operations | 2 | cw_deep_battle |
| `cw_francafrique_defense_accords` | operations | 2 | cw_intervention_pacification |
| `cw_general_peoples_defense` | operations | 2 | cw_total_national_defense |
| `cw_general_uprising_offensive` | operations | 2 | cw_revolutionary_insurgency |
| `cw_internationalist_expeditions` | operations | 2 | cw_revolutionary_insurgency |
| `cw_luring_deep` | operations | 2 | cw_peoples_war |
| `cw_reserve_mobilization_surge` | operations | 2 | cw_preemptive_maneuver |
| `cw_air_ground_deep_penetration` | operations | 3 | cw_preemptive_maneuver |
| `cw_airland_battle` | operations | 3 | cw_forward_defense |
| `cw_armed_neutrality_posture` | operations | 3 | cw_total_national_defense |
| `cw_deep_strike_operations` | operations | 3 | all |
| `cw_low_intensity_conflict` | operations | 3 | all |
| `cw_networked_insurgency_campaign` | operations | 3 | cw_revolutionary_insurgency |
| `cw_overseas_operations_command` | operations | 3 | cw_intervention_pacification |
| `cw_peoples_war_modern_conditions` | operations | 3 | cw_peoples_war |
| `cw_theater_strategic_operations` | operations | 3 | cw_deep_battle |

### Naval

Grand doctrines: `cw_sea_control`, `cw_sea_denial`, `cw_power_projection`

| Subdoctrine | Track | Era | Gate |
| --- | --- | --- | --- |
| `cw_cruiser_task_groups` | capital_ships | 1 | all |
| `cw_gunboat_diplomacy` | capital_ships | 1 | cw_power_projection |
| `cw_shore_bombardment_gunline` | capital_ships | 1 | all |
| `cw_guided_missile_cruisers` | capital_ships | 2 | all |
| `cw_nuclear_surface_escorts` | capital_ships | 2 | all |
| `cw_standing_naval_force` | capital_ships | 2 | cw_sea_control |
| `cw_aegis_area_defense` | capital_ships | 3 | all |
| `cw_ssm_cruiser_salvos` | capital_ships | 3 | cw_sea_denial |
| `cw_surface_action_groups` | capital_ships | 3 | all |
| `cw_escort_carrier_asw` | carriers | 1 | all |
| `cw_fleet_carrier_strike` | carriers | 1 | all |
| `cw_hunter_killer_carrier_groups` | carriers | 1 | cw_sea_control |
| `cw_helicopter_assault_carriers` | carriers | 2 | all |
| `cw_nuclear_strike_carriers` | carriers | 2 | cw_power_projection |
| `cw_supercarrier_strike` | carriers | 2 | all |
| `cw_aviation_cruiser_squadrons` | carriers | 3 | cw_sea_denial |
| `cw_carrier_battle_groups` | carriers | 3 | all |
| `cw_vstol_light_carriers` | carriers | 3 | all |
| `cw_asw_hunter_killer` | screens | 1 | all |
| `cw_atlantic_lifeline_convoys` | screens | 1 | cw_sea_control |
| `cw_convoy_escort_groups` | screens | 1 | all |
| `cw_area_air_defense_escorts` | screens | 2 | all |
| `cw_missile_boat_swarms` | screens | 2 | all |
| `cw_mosquito_fleet` | screens | 2 | cw_sea_denial |
| `cw_expeditionary_escort_squadrons` | screens | 3 | cw_power_projection |
| `cw_littoral_combatants` | screens | 3 | all |
| `cw_towed_array_asw` | screens | 3 | all |
| `cw_fleet_submarine_scouting` | submarines | 1 | all |
| `cw_mass_produced_patrol_submarines` | submarines | 1 | cw_sea_denial |
| `cw_snorkel_wolfpacks` | submarines | 1 | all |
| `cw_giuk_gap_barrier` | submarines | 2 | cw_sea_control |
| `cw_nuclear_attack_submarines` | submarines | 2 | all |
| `cw_ssbn_deterrent_patrols` | submarines | 2 | all |
| `cw_bastion_defense` | submarines | 3 | all |
| `cw_cruise_missile_submarines` | submarines | 3 | all |
| `cw_forward_deployed_hunter_killers` | submarines | 3 | cw_power_projection |

### Air

Grand doctrines: `cw_air_superiority`, `cw_strategic_deterrence`, `cw_integrated_air_land`

| Subdoctrine | Track | Era | Gate |
| --- | --- | --- | --- |
| `cw_continental_air_defense` | fighter_aircraft | 1 | cw_strategic_deterrence |
| `cw_fighter_sweeps` | fighter_aircraft | 1 | all |
| `cw_ground_controlled_interception` | fighter_aircraft | 1 | all |
| `cw_counter_air_dominance` | fighter_aircraft | 2 | cw_air_superiority |
| `cw_dissimilar_air_combat` | fighter_aircraft | 2 | all |
| `cw_frontal_aviation_air_cover` | fighter_aircraft | 2 | cw_integrated_air_land |
| `cw_missile_interceptors` | fighter_aircraft | 2 | all |
| `cw_beyond_visual_range_combat` | fighter_aircraft | 3 | all |
| `cw_energy_maneuverability` | fighter_aircraft | 3 | all |
| `cw_area_bombing` | heavy_aircraft | 1 | all |
| `cw_dispersed_alert_basing` | heavy_aircraft | 1 | cw_strategic_deterrence |
| `cw_strategic_air_command` | heavy_aircraft | 1 | all |
| `cw_aerial_refueling_network` | heavy_aircraft | 2 | cw_air_superiority |
| `cw_airborne_alert` | heavy_aircraft | 2 | all |
| `cw_battlefield_heavy_bombardment` | heavy_aircraft | 2 | cw_integrated_air_land |
| `cw_maritime_patrol_asw` | heavy_aircraft | 2 | all |
| `cw_conventional_heavy_bombing` | heavy_aircraft | 3 | all |
| `cw_standoff_cruise_missiles` | heavy_aircraft | 3 | all |
| `cw_light_bomber_interdiction` | medium_aircraft | 1 | all |
| `cw_tactical_nuclear_bombers` | medium_aircraft | 1 | cw_strategic_deterrence |
| `cw_tactical_reconnaissance` | medium_aircraft | 1 | all |
| `cw_electronic_countermeasures` | medium_aircraft | 2 | all |
| `cw_frontal_bomber_aviation` | medium_aircraft | 2 | cw_integrated_air_land |
| `cw_low_level_penetration` | medium_aircraft | 2 | all |
| `cw_airborne_early_warning` | medium_aircraft | 3 | all |
| `cw_stealth_penetration` | medium_aircraft | 3 | all |
| `cw_swing_role_multirole` | medium_aircraft | 3 | cw_air_superiority |
| `cw_cab_rank_close_support` | strike_aircraft | 1 | all |
| `cw_maritime_strike` | strike_aircraft | 1 | all |
| `cw_nuclear_strike_fighter_bombers` | strike_aircraft | 1 | cw_strategic_deterrence |
| `cw_airfield_suppression_strikes` | strike_aircraft | 2 | cw_air_superiority |
| `cw_interdiction_strike` | strike_aircraft | 2 | all |
| `cw_wild_weasel_sead` | strike_aircraft | 2 | all |
| `cw_airland_close_support` | strike_aircraft | 3 | cw_integrated_air_land |
| `cw_precision_guided_strike` | strike_aircraft | 3 | all |
| `cw_tank_busting` | strike_aircraft | 3 | all |

### Special forces

Grand doctrines: `cw_sf_mass_airborne`, `cw_sf_elite_commandos`, `cw_sf_unconventional_warfare`, `cw_sf_deep_reconnaissance`

| Subdoctrine | Track | Era | Gate |
| --- | --- | --- | --- |
| `cw_sf_air_commandos` | special_forces_first | 1 | all |
| `cw_sf_airborne_assault` | special_forces_first | 1 | all |
| `cw_sf_arctic_winter_warfare` | special_forces_first | 1 | all |
| `cw_sf_army_commandos` | special_forces_first | 1 | all |
| `cw_sf_expeditionary_rapid_reaction` | special_forces_first | 1 | all |
| `cw_sf_foreign_internal_defense` | special_forces_first | 1 | all |
| `cw_sf_jungle_warfare_scouts` | special_forces_first | 1 | all |
| `cw_sf_legion_pacification_garrisons` | special_forces_first | 1 | all |
| `cw_sf_legion_shock_troops` | special_forces_first | 1 | all |
| `cw_sf_marine_amphibious` | special_forces_first | 1 | all |
| `cw_sf_mountain_troops` | special_forces_first | 1 | all |
| `cw_sf_mounted_raiders` | special_forces_first | 1 | all |
| `cw_sf_naval_commandos` | special_forces_first | 1 | all |
| `cw_sf_ranger_raids` | special_forces_first | 1 | all |
| `cw_sf_stay_behind_networks` | special_forces_first | 1 | cw_forward_defense, cw_total_national_defense |
| `cw_sf_strategic_reserve_brigades` | special_forces_first | 1 | all |
| `cw_sf_underwater_demolition` | special_forces_first | 1 | all |
| `cw_sf_air_assault` | special_forces_first | 2 | all |
| `cw_sf_combat_search_rescue` | special_forces_first | 2 | all |
| `cw_sf_counter_terror_assault` | special_forces_first | 2 | all |
| `cw_sf_forward_air_controllers` | special_forces_first | 2 | all |
| `cw_sf_gunship_cavalry` | special_forces_first | 2 | all |
| `cw_sf_high_altitude_warfare` | special_forces_first | 2 | all |
| `cw_sf_long_range_air_insertion` | special_forces_first | 2 | all |
| `cw_sf_long_range_patrols` | special_forces_first | 2 | all |
| `cw_sf_maritime_counter_terror` | special_forces_first | 2 | all |
| `cw_sf_mechanized_airborne` | special_forces_first | 2 | all |
| `cw_sf_mountain_strike_raiders` | special_forces_first | 2 | all |
| `cw_sf_naval_infantry_armored` | special_forces_first | 2 | all |
| `cw_sf_pathfinder_infiltration` | special_forces_first | 2 | all |
| `cw_sf_pseudo_operations` | special_forces_first | 2 | cw_intervention_pacification, cw_revolutionary_insurgency |
| `cw_sf_ranger_airfield_seizure` | special_forces_first | 2 | all |
| `cw_sf_regional_sf_groups` | special_forces_first | 2 | all |
| `cw_sf_riverine_littoral` | special_forces_first | 2 | all |
| `cw_sf_sapper_infiltration` | special_forces_first | 2 | cw_peoples_war, cw_revolutionary_insurgency, cw_deep_battle |
| `cw_sf_special_operations_command` | special_forces_first | 2 | all |
| `cw_sf_spetsnaz_deep_sabotage` | special_forces_first | 2 | cw_sf_deep_reconnaissance, cw_deep_battle |
| `cw_sf_swimmer_delivery_vehicles` | special_forces_first | 2 | all |
