# CWIC Doctrine Design (new framework)

Decided 2026-11-06. Engine reference: `New_Doctrine_System_Reference.md` sections 1-7.
State and rationale: `Doctrine_System_Investigation_2026-11.md`.

## Decisions

1. Land grand doctrines are seven Cold War **schools**. Descendant blocs (SADF, DPRK, Cuba,
   hybrid/Islamist insurgency) are school-exclusive subdoctrines, not grand doctrines, so lineage
   never costs a mastery wipe.
2. Decades are **date-gated subdoctrine generations**: era 1 always available, era 2 from
   `1960.1.1`, era 3 from `1980.1.1`. Syntax, inclusive:
   `available = { NOT = { date < 1960.1.1 } }`.
3. Special forces folder restored with CWIC content behind vanilla's exact DLC gate (AAT or NCNS).
4. 1949 (`the_gathering_storm`) and 1980 bookmarks seed doctrines historically.
5. The legacy technology trees are deleted after this port.

## Compatibility rules

- Land, naval and air content carries **no** `has_dlc` anywhere. Nothing may depend on a DLC-only
  mechanic, modifier, unit or effect. Stat bonuses go through unit categories / CWIC subunits.
- Only the special forces folder `allowed` block is DLC-gated.
- Reference only CWIC subunits and categories (list: `/tmp/cwic_units.txt`; regenerate from
  `common/units/*.txt` + `common/unit_tags/` if missing). Vanilla-only subunits (`mechanized`,
  `armored_car`, `battleship`, ...) do not exist in CWIC.
- Equipment archetype categories for air/naval mastery must exist as `type` values in
  `common/units/equipment/*.txt`.
- Tactics: vanilla `common/combat_tactics.txt` loads unmodified. Every one of vanilla's 14 doctrine
  tactics must be enabled by some CWIC grand doctrine, milestone, subdoctrine or reward.
- Persistent bonuses use declarative forms (modifiers, category blocks, `equipment_bonus`,
  `enable_tactic`). `effect = { }` only for genuine one-shot grants.
- Loc: English only, ASCII only, UTF-8 **with BOM**, `l_english:` header. Script files: no BOM.
  Reward keys are `<subdoctrine>_<reward>` (title only). Grand doctrine and subdoctrine use
  `name` + `description` keys. Track names reuse vanilla `DOCTRINE_TRACK_*` keys (base-game loc loads).
- Art: reference only sprites that already resolve (mod `interface/**/*.gfx` or vanilla
  `interface/doctrines/doctrines.gfx`). Do not declare new sprites. Choose thematically.
- No comments in script (repo rule). No new files beyond the ones assigned below.
- XP: grand doctrine 100, subdoctrine 100 (vanilla parity). Era-3 subdoctrines 100 as well.
  Reward mastery default (100); SF rewards 60 (vanilla parity).
- Magnitudes: stay within vanilla doctrine ranges for the same modifier. A school is a playstyle, not
  a power tier.
- `ai_will_do`: base 1; school's historical tags factor 50-100; era preference: an older-era
  subdoctrine gets `factor = 0.2` once its successor era is available.

## Files and owners

| Path (under `Cold War Iron Curtain/`) | Content |
| --- | --- |
| `common/doctrines/folders/doctrine_folders.txt` | land, naval, air, special_forces (vanilla copy incl. DLC gate) |
| `common/doctrines/tracks/CWIC_land_tracks.txt` | land tracks |
| `common/doctrines/tracks/CWIC_naval_tracks.txt` | naval tracks |
| `common/doctrines/tracks/CWIC_air_tracks.txt` | air tracks |
| `common/doctrines/tracks/CWIC_special_forces_tracks.txt` | SF tracks |
| `common/doctrines/grand_doctrines/CWIC_{land,naval,air,special_forces}_grand_doctrines.txt` | grand doctrines |
| `common/doctrines/subdoctrines/land/CWIC_land_{infantry,combat_support,armor,operations}_subdoctrines.txt` | land |
| `common/doctrines/subdoctrines/sea/CWIC_naval_subdoctrines.txt` | naval |
| `common/doctrines/subdoctrines/air/CWIC_air_subdoctrines.txt` | air |
| `common/doctrines/subdoctrines/special_forces/CWIC_special_forces_subdoctrines.txt` | SF |
| `localisation/english/CWIC_doctrines_{land,naval,air,special_forces}_l_english.yml` | loc |
| `common/ai_strategy/CWIC_doctrines.txt` | AI composition by doctrine |

## Track IDs (94 tracks; land tracks reuse vanilla base-track names and loc)

| Folder | Tracks, in this order everywhere (`milestones` are positional) |
| --- | --- |
| land | per school `cw_<school>_<base>[_e2|_e3]`, base = `infantry`, `combat_support`, `armor`, `operations` (7 schools x 4 x 3 eras = 84) |
| naval | `capital_ships`, `carriers`, `screens`, `submarines` |
| air | `fighter_aircraft`, `strike_aircraft`, `medium_aircraft`, `heavy_aircraft` |
| special_forces | `special_forces_first`, `special_forces_second` |

Land tracks are **era rows** (decision 2026-11-06). Each school grand doctrine has 12 tracks and 12
positional milestones, `max_track_columns = 4`, listed row by row:

| Row | Era | Track ids | Active |
| --- | --- | --- | --- |
| 1 | 1940s-50s | `cw_<school>_<base>` | always |
| 2 | 1960s | `cw_<school>_<base>_e2` | `active = { NOT = { date < 1960.1.1 } }` |
| 3 | 1980s | `cw_<school>_<base>_e3` | `active = { NOT = { date < 1980.1.1 } }` |

84 land tracks in total (7 schools x 4 bases x 3 eras). A subdoctrine's era is its track suffix and
must match its `available` date gate (none = always, `_e2` = from 1960.1.1, `_e3` = from 1980.1.1);
the validator enforces this. Era-2/3 subdoctrines sit on their era tracks; older subdoctrines stay
slotted and keep their bonuses.

Why rows: a swap test showed that replacing a subdoctrine inside one track resets that slot's
mastery to 0. Putting each era on its own track means earlier eras stay active and keep mastery, so
there is no swapping. Each track copies its base track's `name`, `icon`, `icon_frame` and `mastery`
block. A generic land subdoctrine (no school gate) lists all 7 school variants of its base track in
the same era in `track = { ... }`; a school-exclusive or lineage subdoctrine lists the single track of
its school and era. Triggers that ask "has this kind of track completed" (`has_completed_track`) are
an `OR` over the 7 schools x 3 eras = 21 variants.

Naval and air era rows (decision 2026-11-06, extended): the naval folder (`capital_ships`, `carriers`,
`screens`, `submarines`) and the air folder (`fighter_aircraft`, `strike_aircraft`, `medium_aircraft`,
`heavy_aircraft`) share era tracks. Each grand doctrine lists its 4 base tracks, then the 4 `_e2`
tracks, then the 4 `_e3` tracks, with `max_track_columns = 4` and 12 positional milestones (the
original 4 plus 8 era milestones). Era gates match land: `_e2` = `active = { NOT = { date < 1960.1.1 } }`,
`_e3` = `active = { NOT = { date < 1980.1.1 } }`. 1980 bookmark seeding: era-1 subdoctrines get
`add_mastery` 500 and era-2 subdoctrines 300. Naval/air subdoctrines follow the land rule: `track`
suffix equals the `available` date gate (none, 1960.1.1 = `_e2`, 1980.1.1 = `_e3`).

Special forces era row: a single extra row, `special_forces_first_e2` and `special_forces_second_e2`,
gated by `active = { NOT = { date < 1970.1.1 } }`; `special_forces_second_e2` also ANDs the existing
`can_unlock_second_track_of_sf_doctrine = yes`. Each SF grand doctrine lists 2 base tracks then the 2
era tracks, `max_track_columns = 2`, and 4 milestones. SF subdoctrines gated at 1960 move to the
`_e2` row with their gate changed to 1970.1.1; those gated at 1980 stay at 1980 on the `_e2` row.
Era-track backgrounds reuse the base track texture until art lands (`GFX_cw_track_<track_id>`).


Sprite naming: track background `GFX_cw_track_<track_id>` (all 94), grand doctrine icon
`GFX_cw_gd_<grand_doctrine_id>` (17), subdoctrine icon `GFX_cw_sd_<subdoctrine_id>` (all subdoctrines).
All are declared in `interface/CWIC_Doctrines.gfx`; images live under `gfx/interface/doctrines/cwic/{tracks,grand,icons}/`
with the sprite name minus `GFX_` as the file stem.

## Land grand doctrines

| ID | School | Historical users (resolve tags in `common/country_tags`) |
| --- | --- | --- |
| `cw_forward_defense` | NATO forward defense -> active defense -> AirLand | USA, ENG, WGR, CAN, ITA, TUR, NATO members, SAF, ROK |
| `cw_deep_battle` | Soviet deep battle, echeloned offensive | SOV, Warsaw Pact, DPRK, Syria/Iraq/Egypt client armies |
| `cw_peoples_war` | Maoist people's war | PRC, VIN, Khmer Rouge, Maoist movements |
| `cw_intervention_pacification` | French intervention / guerre revolutionnaire | FRA, POR, BEL, colonial powers |
| `cw_preemptive_maneuver` | Israeli preemptive armored maneuver | ISR |
| `cw_total_national_defense` | Territorial and total defense | YUG, SWE, SWI, FIN, AUS, IND (Himalayan), PER, non-aligned |
| `cw_revolutionary_insurgency` | Foco, insurgency, irregular war | CUB, insurgent and liberation tags |

## Land subdoctrines

Era column: 1 = always, 2 = from 1960.1.1, 3 = from 1980.1.1. "School" = `visible` and `available`
also require `has_doctrine = <grand doctrine>`.

| Track | Era | ID | School |
| --- | --- | --- | --- |
| infantry | 1 | `cw_rifle_company_firepower` | |
| infantry | 1 | `cw_mass_infantry_assault` | |
| infantry | 1 | `cw_human_wave_tactics` | peoples_war |
| infantry | 1 | `cw_territorial_defense_forces` | total_national_defense |
| infantry | 1 | `cw_foco_vanguard` | revolutionary_insurgency |
| infantry | 2 | `cw_mechanized_infantry_integration` | |
| infantry | 2 | `cw_airmobile_infantry` | |
| infantry | 2 | `cw_bush_war_mobility` | forward_defense (SADF lineage) |
| infantry | 2 | `cw_juche_infiltration_warfare` | deep_battle (DPRK lineage) |
| infantry | 3 | `cw_light_infantry_divisions` | |
| infantry | 3 | `cw_dismounted_atgm_teams` | |
| infantry | 3 | `cw_rapid_action_force` | intervention_pacification |
| combat_support | 1 | `cw_massed_artillery_fires` | |
| combat_support | 1 | `cw_combat_engineering` | |
| combat_support | 2 | `cw_tactical_nuclear_fires` | |
| combat_support | 2 | `cw_army_aviation` | |
| combat_support | 2 | `cw_mountain_warfare_corps` | total_national_defense |
| combat_support | 3 | `cw_reconnaissance_strike_complex` | |
| combat_support | 3 | `cw_electronic_warfare_support` | |
| combat_support | 3 | `cw_hybrid_irregular_warfare` | revolutionary_insurgency (hybrid/Islamist lineage) |
| armor | 1 | `cw_tank_heavy_formations` | |
| armor | 1 | `cw_infantry_support_armor` | |
| armor | 2 | `cw_combined_arms_battalions` | |
| armor | 2 | `cw_antitank_defense_in_depth` | |
| armor | 2 | `cw_all_tank_doctrine` | preemptive_maneuver |
| armor | 3 | `cw_mbt_maneuver_groups` | |
| armor | 3 | `cw_armored_cavalry_screen` | |
| armor | 3 | `cw_operational_maneuver_groups` | deep_battle |
| armor | 3 | `cw_combined_arms_restoration` | preemptive_maneuver |
| operations | 1 | `cw_positional_defense` | |
| operations | 1 | `cw_mobile_counterattack` | |
| operations | 1 | `cw_guerre_revolutionnaire` | intervention_pacification |
| operations | 2 | `cw_flexible_response_operations` | |
| operations | 2 | `cw_counterinsurgency_operations` | |
| operations | 2 | `cw_internationalist_expeditions` | revolutionary_insurgency (Cuba lineage) |
| operations | 3 | `cw_deep_strike_operations` | |
| operations | 3 | `cw_low_intensity_conflict` | |
| operations | 3 | `cw_airland_battle` | forward_defense |
| operations | 3 | `cw_peoples_war_modern_conditions` | peoples_war |

## Naval

Grand doctrines: `cw_sea_control` (legacy fleet_in_being), `cw_sea_denial` (legacy
trade_interdiction), `cw_power_projection` (legacy base_strike).

| Track | Era 1 | Era 2 | Era 3 |
| --- | --- | --- | --- |
| capital_ships | `cw_shore_bombardment_gunline`, `cw_cruiser_task_groups` | `cw_guided_missile_cruisers`, `cw_nuclear_surface_escorts` | `cw_aegis_area_defense`, `cw_surface_action_groups` |
| carriers | `cw_fleet_carrier_strike`, `cw_escort_carrier_asw` | `cw_supercarrier_strike`, `cw_helicopter_assault_carriers` | `cw_carrier_battle_groups`, `cw_vstol_light_carriers` |
| screens | `cw_asw_hunter_killer`, `cw_convoy_escort_groups` | `cw_missile_boat_swarms`, `cw_area_air_defense_escorts` | `cw_towed_array_asw`, `cw_littoral_combatants` |
| submarines | `cw_snorkel_wolfpacks`, `cw_fleet_submarine_scouting` | `cw_nuclear_attack_submarines`, `cw_ssbn_deterrent_patrols` | `cw_bastion_defense`, `cw_cruise_missile_submarines` |

Historical users: sea_control USA/ENG/NATO navies; sea_denial SOV/Warsaw/PRC; power_projection
USA (alternative), FRA, ENG (alternative).

## Air

Grand doctrines: `cw_air_superiority` (legacy versatile), `cw_strategic_deterrence` (legacy
systemic), `cw_integrated_air_land` (legacy integral).

| Track | Era 1 | Era 2 | Era 3 |
| --- | --- | --- | --- |
| fighter_aircraft | `cw_ground_controlled_interception`, `cw_fighter_sweeps` | `cw_missile_interceptors`, `cw_dissimilar_air_combat` | `cw_beyond_visual_range_combat`, `cw_energy_maneuverability` |
| strike_aircraft | `cw_cab_rank_close_support`, `cw_maritime_strike` | `cw_interdiction_strike`, `cw_wild_weasel_sead` | `cw_precision_guided_strike`, `cw_tank_busting` |
| medium_aircraft | `cw_tactical_reconnaissance`, `cw_light_bomber_interdiction` | `cw_low_level_penetration`, `cw_electronic_countermeasures` | `cw_airborne_early_warning`, `cw_stealth_penetration` |
| heavy_aircraft | `cw_strategic_air_command`, `cw_area_bombing` | `cw_airborne_alert`, `cw_maritime_patrol_asw` | `cw_standoff_cruise_missiles`, `cw_conventional_heavy_bombing` |

Historical users: air_superiority ISR/ENG/FRA; strategic_deterrence USA/SOV/ENG(1949);
integrated_air_land SOV(1980)/Warsaw/PRC/WGR.

## Special forces

Folder `special_forces`, gate copied from vanilla (AAT or NCNS); the only DLC-gated content. Tracks
`special_forces_first` and `special_forces_second`; the second is active when `sf_trees > 1`, set by the
`diversify_special_forces` decision. One subdoctrine per track, so every `xor` pair is a real choice.

Grand doctrines (two positional milestones each):
- `cw_sf_mass_airborne`: quantity (VDV, US airborne corps).
- `cw_sf_elite_commandos`: quality (SAS, Sayeret Matkal).
- `cw_sf_unconventional_warfare`: by, with and through partner forces (US Special Forces, Portuguese
  Comandos, Rhodesian pseudo-operations).
- `cw_sf_deep_reconnaissance`: strategic recon and sabotage (Spetsnaz, Recces, LRRP).

Subdoctrines: per-subdoctrine mastery from their own units, reward mastery 60, `xor` pairs inside each
unit family. Era 2 from 1960.1.1, era 3 from 1980.1.1. Gate column = `visible`/`available` doctrine.

| ID | Era | Gate | xor |
| --- | --- | --- | --- |
| `cw_sf_airborne_assault` | 1 |  | cw_sf_pathfinder_infiltration |
| `cw_sf_pathfinder_infiltration` | 2 |  | cw_sf_airborne_assault |
| `cw_sf_strategic_reserve_brigades` | 1 |  | cw_sf_mechanized_airborne |
| `cw_sf_mechanized_airborne` | 2 |  | cw_sf_strategic_reserve_brigades |
| `cw_sf_air_assault` | 2 |  | cw_sf_gunship_cavalry |
| `cw_sf_gunship_cavalry` | 2 |  | cw_sf_air_assault |
| `cw_sf_mounted_raiders` | 1 |  | cw_sf_pseudo_operations |
| `cw_sf_pseudo_operations` | 2 | cw_intervention_pacification / cw_revolutionary_insurgency | cw_sf_mounted_raiders |
| `cw_sf_marine_amphibious` | 1 |  | cw_sf_expeditionary_rapid_reaction |
| `cw_sf_expeditionary_rapid_reaction` | 1 |  | cw_sf_marine_amphibious |
| `cw_sf_naval_infantry_armored` | 2 |  | cw_sf_riverine_littoral |
| `cw_sf_riverine_littoral` | 2 |  | cw_sf_naval_infantry_armored |
| `cw_sf_mountain_troops` | 1 |  | cw_sf_arctic_winter_warfare |
| `cw_sf_arctic_winter_warfare` | 1 |  | cw_sf_mountain_troops |
| `cw_sf_high_altitude_warfare` | 2 |  | cw_sf_mountain_strike_raiders |
| `cw_sf_mountain_strike_raiders` | 2 |  | cw_sf_high_altitude_warfare |
| `cw_sf_ranger_raids` | 1 |  | cw_sf_long_range_patrols |
| `cw_sf_long_range_patrols` | 2 |  | cw_sf_ranger_raids |
| `cw_sf_jungle_warfare_scouts` | 1 |  | cw_sf_ranger_airfield_seizure |
| `cw_sf_ranger_airfield_seizure` | 2 |  | cw_sf_jungle_warfare_scouts |
| `cw_sf_army_commandos` | 1 |  | cw_sf_counter_terror_assault |
| `cw_sf_counter_terror_assault` | 3 |  | cw_sf_army_commandos |
| `cw_sf_foreign_internal_defense` | 1 |  | cw_sf_sapper_infiltration |
| `cw_sf_sapper_infiltration` | 2 | cw_peoples_war / cw_revolutionary_insurgency / cw_deep_battle | cw_sf_foreign_internal_defense |
| `cw_sf_spetsnaz_deep_sabotage` | 2 | cw_sf_deep_reconnaissance / cw_deep_battle | cw_sf_stay_behind_networks |
| `cw_sf_stay_behind_networks` | 1 | cw_forward_defense / cw_total_national_defense | cw_sf_spetsnaz_deep_sabotage |
| `cw_sf_naval_commandos` | 1 |  | cw_sf_maritime_counter_terror |
| `cw_sf_maritime_counter_terror` | 3 |  | cw_sf_naval_commandos |
| `cw_sf_underwater_demolition` | 1 |  | cw_sf_swimmer_delivery_vehicles |
| `cw_sf_swimmer_delivery_vehicles` | 2 |  | cw_sf_underwater_demolition |
| `cw_sf_air_commandos` | 1 |  | cw_sf_combat_search_rescue |
| `cw_sf_combat_search_rescue` | 2 |  | cw_sf_air_commandos |
| `cw_sf_forward_air_controllers` | 2 |  | cw_sf_long_range_air_insertion |
| `cw_sf_long_range_air_insertion` | 2 |  | cw_sf_forward_air_controllers |
| `cw_sf_legion_shock_troops` | 1 |  | cw_sf_legion_pacification_garrisons |
| `cw_sf_legion_pacification_garrisons` | 1 |  | cw_sf_legion_shock_troops |
| `cw_sf_regional_sf_groups` | 2 |  | cw_sf_special_operations_command |
| `cw_sf_special_operations_command` | 3 |  | cw_sf_regional_sf_groups |

## Bookmark seeding

`set_grand_doctrine` for land/naval/air (SF only where the history is unambiguous and inside
`if = { limit = { OR = { has_dlc = "No Compromise, No Surrender" has_dlc = "Arms Against Tyranny" } } }`),
`set_sub_doctrine` for era-appropriate subdoctrines, `add_mastery = { amount = N sub_doctrine = X }`
for veteran armies. 1949: era 1 only. 1980: era 1-3 as historical. Countries without a clear
doctrine start blank.

Era-row seeding: in each 1980.1.1 block, every era-1 land subdoctrine the country received in its
1949 block gets `add_mastery = { amount = 500 sub_doctrine = <id> }` (the veteran era-1 row is
complete by 1980), and every era-2 land subdoctrine set in the 1980 block gets
`add_mastery = { amount = 300 sub_doctrine = <id> }`. Empty tracks stay empty unless history is obvious.

## Cost reductions

`add_doctrine_cost_reduction` categories map to folders by technology category name:
`land_doctrine`, `naval_doctrine`, `air_doctrine`, `special_forces_doctrine`. CWIC's
`cat_air_doctrine` and the stray `fleet_in_being_tree`, `cat_mass_assault` targets are retargeted;
`add_tech_bonus` grants into legacy doctrine categories become `add_doctrine_cost_reduction`.

## Expansion 1: school identity (2026-11-06)

Playtest feedback: the seven land schools see mostly the same subdoctrines. Rule from here on:

**Land.** Every school owns exactly one exclusive subdoctrine per track per era (7 x 4 x 3 = 84
slots). Slots already filled: forward_defense ops/3 `cw_airland_battle`; deep_battle armor/3
`cw_operational_maneuver_groups`; peoples_war inf/1 `cw_human_wave_tactics`, ops/3
`cw_peoples_war_modern_conditions`; intervention_pacification inf/3 `cw_rapid_action_force`, ops/1
`cw_guerre_revolutionnaire`; preemptive_maneuver armor/2 `cw_all_tank_doctrine`, armor/3
`cw_combined_arms_restoration`; total_national_defense inf/1 `cw_territorial_defense_forces`, cs/2
`cw_mountain_warfare_corps`; revolutionary_insurgency inf/1 `cw_foco_vanguard`. The four lineage
subdoctrines (`cw_bush_war_mobility`, `cw_juche_infiltration_warfare`, `cw_internationalist_expeditions`,
`cw_hybrid_irregular_warfare`) are extras on top of the grid. The 24 generic subdoctrines stay as the
shared baseline. 73 new land subdoctrines.

New school content lives in `common/doctrines/subdoctrines/land/CWIC_land_<school>_subdoctrines.txt`
(school = grand doctrine ID without `cw_`), loc merged into `CWIC_doctrines_land_l_english.yml`.

**Naval and air.** Each grand doctrine owns one exclusive subdoctrine per track (12 naval, 12 air),
era chosen to fit history.

**Special forces.** Redesigned from research into Cold War special operations models; see the SF
section once rewritten.

### Land school subdoctrines (73)

| School | Track | Era | ID |
| --- | --- | --- | --- |
| forward_defense | infantry | 1 | `cw_covering_force_screen` |
| forward_defense | infantry | 2 | `cw_panzergrenadier_defense` |
| forward_defense | infantry | 3 | `cw_urban_terrain_defense` |
| forward_defense | combat_support | 1 | `cw_tactical_air_control` |
| forward_defense | combat_support | 2 | `cw_atgm_screening_belts` |
| forward_defense | combat_support | 3 | `cw_follow_on_forces_attack` |
| forward_defense | armor | 1 | `cw_hull_down_ambush` |
| forward_defense | armor | 2 | `cw_cross_attached_task_forces` |
| forward_defense | armor | 3 | `cw_heavy_corps_gunnery` |
| forward_defense | operations | 1 | `cw_forward_strategy` |
| forward_defense | operations | 2 | `cw_active_defense` |
| deep_battle | infantry | 1 | `cw_echeloned_rifle_assault` |
| deep_battle | infantry | 2 | `cw_motor_rifle_divisions` |
| deep_battle | infantry | 3 | `cw_airmobile_assault_brigades` |
| deep_battle | combat_support | 1 | `cw_artillery_breakthrough_divisions` |
| deep_battle | combat_support | 2 | `cw_air_defense_umbrella` |
| deep_battle | combat_support | 3 | `cw_reconnaissance_fire_complex` |
| deep_battle | armor | 1 | `cw_tank_army_breakthrough` |
| deep_battle | armor | 2 | `cw_nuclear_battlefield_armor` |
| deep_battle | operations | 1 | `cw_operational_echelonment` |
| deep_battle | operations | 2 | `cw_forward_detachments` |
| deep_battle | operations | 3 | `cw_theater_strategic_operations` |
| peoples_war | infantry | 2 | `cw_main_force_local_force` |
| peoples_war | infantry | 3 | `cw_fist_units` |
| peoples_war | combat_support | 1 | `cw_infantry_heavy_weapons` |
| peoples_war | combat_support | 2 | `cw_sapper_demolition_units` |
| peoples_war | combat_support | 3 | `cw_massed_air_defense` |
| peoples_war | armor | 1 | `cw_infantry_accompanying_tanks` |
| peoples_war | armor | 2 | `cw_tank_hunter_teams` |
| peoples_war | armor | 3 | `cw_group_army_armor` |
| peoples_war | operations | 1 | `cw_protracted_war` |
| peoples_war | operations | 2 | `cw_luring_deep` |
| intervention_pacification | infantry | 1 | `cw_legion_parachute_regiments` |
| intervention_pacification | infantry | 2 | `cw_zone_commandos` |
| intervention_pacification | combat_support | 1 | `cw_groupes_mobiles` |
| intervention_pacification | combat_support | 2 | `cw_helicopter_fire_support` |
| intervention_pacification | combat_support | 3 | `cw_overseas_pre_positioning` |
| intervention_pacification | armor | 1 | `cw_colonial_light_armor` |
| intervention_pacification | armor | 2 | `cw_cavalry_reconnaissance_armor` |
| intervention_pacification | armor | 3 | `cw_wheeled_gun_armor` |
| intervention_pacification | operations | 2 | `cw_francafrique_defense_accords` |
| intervention_pacification | operations | 3 | `cw_overseas_operations_command` |
| preemptive_maneuver | infantry | 1 | `cw_nahal_citizen_army` |
| preemptive_maneuver | infantry | 2 | `cw_sayeret_deep_raids` |
| preemptive_maneuver | infantry | 3 | `cw_heavy_apc_infantry` |
| preemptive_maneuver | combat_support | 1 | `cw_heavy_mortar_improvisation` |
| preemptive_maneuver | combat_support | 2 | `cw_self_propelled_armored_fire` |
| preemptive_maneuver | combat_support | 3 | `cw_drone_suppression_of_defenses` |
| preemptive_maneuver | armor | 1 | `cw_improvised_armored_brigades` |
| preemptive_maneuver | operations | 1 | `cw_preemptive_first_strike` |
| preemptive_maneuver | operations | 2 | `cw_reserve_mobilization_surge` |
| preemptive_maneuver | operations | 3 | `cw_air_ground_deep_penetration` |
| total_national_defense | infantry | 2 | `cw_fortress_belt_defense` |
| total_national_defense | infantry | 3 | `cw_citizen_army_mobilization` |
| total_national_defense | armor | 1 | `cw_ambush_tank_destroyers` |
| total_national_defense | armor | 2 | `cw_hull_down_armor` |
| total_national_defense | armor | 3 | `cw_territorial_armor_reserve` |
| total_national_defense | combat_support | 1 | `cw_obstacle_engineering` |
| total_national_defense | combat_support | 3 | `cw_antitank_missile_belts` |
| total_national_defense | operations | 1 | `cw_delaying_defense` |
| total_national_defense | operations | 2 | `cw_general_peoples_defense` |
| total_national_defense | operations | 3 | `cw_armed_neutrality_posture` |
| revolutionary_insurgency | infantry | 2 | `cw_protracted_peoples_war` |
| revolutionary_insurgency | infantry | 3 | `cw_mujahideen_cell_networks` |
| revolutionary_insurgency | armor | 1 | `cw_technicals_and_captured_armor` |
| revolutionary_insurgency | armor | 2 | `cw_rpg_ambush_teams` |
| revolutionary_insurgency | armor | 3 | `cw_manpads_and_advanced_antiarmor` |
| revolutionary_insurgency | combat_support | 1 | `cw_improvised_explosive_devices` |
| revolutionary_insurgency | combat_support | 2 | `cw_rocket_and_mortar_harassment` |
| revolutionary_insurgency | combat_support | 3 | `cw_sanctuary_logistics` |
| revolutionary_insurgency | operations | 1 | `cw_cross_border_sanctuaries` |
| revolutionary_insurgency | operations | 2 | `cw_general_uprising_offensive` |
| revolutionary_insurgency | operations | 3 | `cw_networked_insurgency_campaign` |

### Naval and air grand-doctrine subdoctrines (24)

| Folder | Grand doctrine | Track | Era | ID |
| --- | --- | --- | --- | --- |
| naval | cw_sea_control | capital_ships | 2 | `cw_standing_naval_force` |
| naval | cw_sea_denial | capital_ships | 3 | `cw_ssm_cruiser_salvos` |
| naval | cw_power_projection | capital_ships | 1 | `cw_gunboat_diplomacy` |
| naval | cw_sea_control | carriers | 1 | `cw_hunter_killer_carrier_groups` |
| naval | cw_power_projection | carriers | 2 | `cw_nuclear_strike_carriers` |
| naval | cw_sea_denial | carriers | 3 | `cw_aviation_cruiser_squadrons` |
| naval | cw_sea_control | screens | 1 | `cw_atlantic_lifeline_convoys` |
| naval | cw_sea_denial | screens | 2 | `cw_mosquito_fleet` |
| naval | cw_power_projection | screens | 3 | `cw_expeditionary_escort_squadrons` |
| naval | cw_sea_denial | submarines | 1 | `cw_mass_produced_patrol_submarines` |
| naval | cw_sea_control | submarines | 2 | `cw_giuk_gap_barrier` |
| naval | cw_power_projection | submarines | 3 | `cw_forward_deployed_hunter_killers` |
| air | cw_air_superiority | fighter_aircraft | 2 | `cw_counter_air_dominance` |
| air | cw_strategic_deterrence | fighter_aircraft | 1 | `cw_continental_air_defense` |
| air | cw_integrated_air_land | fighter_aircraft | 2 | `cw_frontal_aviation_air_cover` |
| air | cw_air_superiority | strike_aircraft | 2 | `cw_airfield_suppression_strikes` |
| air | cw_strategic_deterrence | strike_aircraft | 1 | `cw_nuclear_strike_fighter_bombers` |
| air | cw_integrated_air_land | strike_aircraft | 3 | `cw_airland_close_support` |
| air | cw_air_superiority | medium_aircraft | 3 | `cw_swing_role_multirole` |
| air | cw_strategic_deterrence | medium_aircraft | 1 | `cw_tactical_nuclear_bombers` |
| air | cw_integrated_air_land | medium_aircraft | 2 | `cw_frontal_bomber_aviation` |
| air | cw_air_superiority | heavy_aircraft | 2 | `cw_aerial_refueling_network` |
| air | cw_strategic_deterrence | heavy_aircraft | 1 | `cw_dispersed_alert_basing` |
| air | cw_integrated_air_land | heavy_aircraft | 2 | `cw_battlefield_heavy_bombardment` |

## Status (2026-11-06)

Implemented on `development-branch` (uncommitted). Legacy trees, `old_*_doctrine_folder` registrations,
`Land_Doctrine_l_english.yml` and the 80 per-node PNGs in `gfx/interface/doctrines/Technology/` are
deleted. Obsolete planning docs in this directory: `Doctrine_Rework_Plan.md`,
`Doctrine_Cell_Manifest.md`, `Land_Doctrine_Tree_Structure.md`, `Doctrine_Icon_Art_Requests.md`,
`Doctrine_Rework_Handoff.md` (doctrine sections).

Also changed outside the doctrine files:

- `interface/doctrines/doctrines.gfx` resynced to vanilla 1.19.4 plus CWIC's folder icons and the
  vanilla SF / background sprites whose home files CWIC overrides.
- `interface/countryofficercorpview.gui`: the land/naval/air doctrine buttons were parked off-screen
  (`x=-10000`); restored to the vanilla layout. SF button replaced with vanilla's.
- `interface/countrydoctrinetreeview.gui` replaced with the vanilla 1.19.4 copy.
- `common/decisions/_generic_decisions.txt`: `diversify_special_forces` (operations category) is the
  only source of `add_potential_special_forces_tree`, which unlocks the second SF track.
- `common/technology_tags/00_technology.txt`: `air_doctrine`, `special_forces_doctrine` categories.
- 41 legacy doctrine `add_tech_bonus` grants became `add_doctrine_cost_reduction`.

### Runtime evidence

Headless runs: `gamescope --backend headless -W 1920 -H 1080 -- ./run_hoi4 -mod=mod/Cold_War_Iron_Curtain.mod -debug -ai_testing`.
With the monitors in DPMS-off the normal window never gets a frame and the game stalls after
`defines loaded`; headless gamescope avoids that. Time stays paused at the start date.

A throwaway `on_startup` probe (removed) slotted all 15 grand doctrines and 95 subdoctrines on one
country, added 600 mastery and checked `has_mastery_level = 5`: 15/15, 95/95, 95/95, with all DLC and
with every DLC disabled through `dlc_load.json`. Seeding was read back with `has_doctrine` at 1949
(28 tags) and 1980 (bookmark date temporarily set to 1980 because `-ai_testing` always loads the
default bookmark). `error.log` has zero doctrine, officer-corps or doctrine-loc lines.

### Not yet exercised

- Land doctrine view confirmed rendering by the user (Intervention and Pacification, four tracks).
  Naval, air and SF views, and the borrowed air/naval icons on land school subdoctrines, still unseen.
- AI purchasing over time, and the `ai_will_do` era preference (needs time to run).
- `available` era/school gating in the purchase UI (`set_sub_doctrine` bypasses it).
- Whether `add_doctrine_cost_reduction` with `air_doctrine` / `special_forces_doctrine` discounts the
  matching folder.
- Balance: magnitudes follow vanilla ranges, untuned.

### Expansion 1 verification (2026-11-06)

Totals: land 112 subdoctrines (24 generic, 84 school slots, 4 lineage), naval 36, air 36, SF 4 grand
doctrines / 38 subdoctrines. Startup probe (removed): 17/17 grand doctrines and 222/222 subdoctrines
slot and reach 5 mastery levels; zero doctrine lines in `error.log` after fixing bare `defense`,
bare naval coordination modifiers and an SF `sub_units = { category_* }` block. Seeds now use each
school's exclusive subdoctrine where one exists for that track and era; other intervention countries
(BEL, POR) keep the generic picks because the French slots are Legion- and Francafrique-specific.
