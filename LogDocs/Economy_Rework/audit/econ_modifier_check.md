# CWIC Economy Modifier Existence Check

Scope: modifier keys read via `modifier@` in the 7 required scripted_effects files, keys written in the 8 required idea and dynamic-modifier files, and modifier definitions in `common/modifier_definitions/`. Vanilla reference: `documentation/modifiers_documentation.md` in the HOI4 install.

Coverage gap: the idea-file key scan was not exhaustive. Keys were verified only where they are read by `modifier@`, or where they were targeted by a defined-but-unread check. A full undefined-key sweep of the idea files is still needed, using a per-file grep that excludes defined and vanilla keys.

## 1. Entry points

- `IC_Econ_2024.txt` (`CWIC_force_update_econ_drift_vars` at 2553–2624 and many `modifier@` reads) is the main modifier reader. It runs from the economy update path (`[INFERENCE]` for frequency).
- `IC_Trade_Scripted_Effects.txt` reads export rates, trade penalty and bonus keys, and `extra_trade_to_overlord_factor`. Its trade reads cover about 30 sites through line 7545.
- `policy_focus_effects.txt:370–389` reads tax-rate keys and `modifier_tax_efficiacy`.
- `IC_Loans_and_Interest_Rate_Effects.txt:214` reads `office_park_income_bonus`.
- `IC_tax_avoidance_line.txt:15` reads `tax_avoidance_elasticity`.
- `IC_Industrial_Pulse.txt:189, 478, 711` reads consumption-need and agricultural keys.
- `IncomeGenerator.txt` has **no** `modifier@` reads (grep on `modifier@[A-Za-z_0-9]+` returned no matches in that file). `[INFERENCE]` that the file reads its inputs through other variables.

## 2. Data model

- Modifier definitions live in `common/modifier_definitions/*.txt`. Each definition sets `color_type`, `value_type`, and `precision`. Files:
  - `influence_modifier_definitions.txt`: tax, income, spending, and productivity definitions. Key sites: `health_spending_modifier` at line 20, `healthcare_spending_modifier` at line 154, `war_reperations` at 191.
  - `lar_operation_modifiers_pre_definition.txt`: export rates, consumption needs, trade adjustments, `modifier_tax_efficiacy` at 109, `agricultural_industrial_complex_income_adjustment` at 115 (commented "NOT REAL ONLY FOR DISPLAY"), and `modifier_arms_factory_income` at 121.
  - `zzz_restored_modifier_definitions.txt`: lines 6–153. Includes `office_park_income_adjustment` at 118 and `trade_goods_cost` at 153.
  - `Intelligence_agency_modifiers.txt`: lines 3–270+. Includes `modifier_mass_media_spending` at 123, `modifier_trade_efficiency` at 171, and `monthly_population` at 179.
  - `modifier_definitions.txt`: lines 34–322. Space, unit-limit, and anti-ballistic keys.
  - `PRC_Generic_GUI_modifiers.txt` (1–13) and `INO_modifier_definition.txt` (1). Display-only PRC and INO keys.
  - `CWIC_espionage_modifiers.txt.disabled`: disabled, not loaded. Excluded.
- `modifier@<key>` reads the scalar value of a modifier on the current scope. Keys are read from the definition or from vanilla.
- Idea and dynamic modifier blocks write modifier keys directly. They do not use `modifier@` reads.

## 3. Formulas (existence and mapping)

Classes: L = locally defined (definition file:line), V = vanilla documented (`modifiers_documentation.md` line), U = undefined.

**Keys read by the 7 required files**

| Key | Read sites | Class |
|---|---|---|
| `local_building_slots` | IC_Econ_2024.txt:212 | V (doc:3157) |
| `global_building_slots` | IC_Econ_2024.txt:213 | V (doc:2852) |
| `local_building_slots_factor` | IC_Econ_2024.txt:221 | V (doc:3162) |
| `global_building_slots_factor` | IC_Econ_2024.txt:224 | V (doc:2857) |
| `conscription` | IC_Econ_2024.txt:485 | V (doc:2272) |
| `conscription_factor` | IC_Econ_2024.txt:488 | V (doc:2277) |
| `food_income_bonus` | IC_Econ_2024.txt:955 | L (influence:101) |
| `tax_rate_lower_class`, `tax_rate_middle_class`, `tax_rate_upper_class`, `tax_rate_corporate` | IC_Econ_2024.txt:1341, 1346, 1351, 1356; policy_focus_effects.txt:370–379 | L (influence:45–63) |
| `welfare_spending_modifier` | IC_Econ_2024.txt:1570, 1583 | L (influence:148) |
| `healthcare_spending_modifier` | IC_Econ_2024.txt:1600, 2209 | L (influence:154) |
| `policing_spending_modifier` | IC_Econ_2024.txt:1614 | L (influence:136) |
| `education_spending_modifier` | IC_Econ_2024.txt:1637 | L (influence:130) |
| `public_services_spending_modifier` | IC_Econ_2024.txt:1657 | L (influence:142) |
| `army_spending_modifier` | IC_Econ_2024.txt:1740 | L (influence:160) |
| `air_spending_modifier` | IC_Econ_2024.txt:1872 | L (influence:172) |
| `navy_spending_modifier` | IC_Econ_2024.txt:1952 | L (influence:166) |
| `strategic_forces_spending_modifier` | IC_Econ_2024.txt:1986 | L (influence:178) |
| `space_spending_modifier` | IC_Econ_2024.txt:2003 | L (influence:184) |
| `education_gain_rate` | IC_Econ_2024.txt:2278; IC_literacy_calculations.txt:35–243 | L (influence:26) |
| `industrial_park_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:71) |
| `military_factory_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:77) |
| `office_park_income_bonus` | IC_Econ_2024.txt:2553–2561 range; IC_Loans_and_Interest_Rate_Effects.txt:214 | L (influence:83) |
| `foundry_district_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:95) |
| `metallurgy_plant_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:89) |
| `other_resources_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:107) |
| `dockyard_income_bonus` | IC_Econ_2024.txt:2553–2561 range | L (influence:113) |
| `productivity_factor` | IC_Econ_2024.txt:2553–2561 range | L (influence:120) |
| `workforce_ratio` | IC_Econ_2024.txt:2553–2561 range | L (influence:32) |
| `electricity_consumption_need` | IC_Industrial_Pulse.txt:189 | L (lar:77) |
| `food_consumption_need` | IC_Industrial_Pulse.txt:478 | L (lar:71) |
| `agricultural_complex_production_bonus` | IC_Industrial_Pulse.txt:711 | L (lar:65) |
| `chromium_export_rate`, `oil_export_rate`, `food_export_rate`, `steel_export_rate`, `aluminum_export_rate`, `rare_earth_export_rate`, `consumer_goods_export_rate` | IC_Trade_Scripted_Effects.txt:18–24 | L (lar:23–59) |
| `extra_trade_to_overlord_factor` | IC_Trade_Scripted_Effects.txt:326 … 7545 (about 30 sites) | V (doc:2707) |
| `global_trade_penalty_adjustment` | IC_Trade_Scripted_Effects.txt:387 + more | L (lar:83) |
| `arab_league_trade_penalty_adjustment` | IC_Trade_Scripted_Effects.txt:394 + more | L (lar:89) |
| `global_trade_bonus_adjustment` | IC_Trade_Scripted_Effects.txt:407 + more | L (lar:95) |
| `modifier_tax_efficiacy` | policy_focus_effects.txt:389 | L (lar:109) |
| `tax_avoidance_elasticity` | IC_tax_avoidance_line.txt:15 | L (lar:103) |

Keys read by the non-required files, found during the scan: `war_reperations` (IC_scripted_effects.txt:58, L influence:191), `consumer_goods_factor` and `consumer_goods_expected_value` (IC_Consumer_Goods.txt:298–300; V docs 468/467), `drift_defence_factor` (separatism_effects.txt:55–62; V doc:2438), `unit_limit_bonus` and `unit_limit_factor` (CWIC_division_limit_effects.txt:39–44; L modifier_definitions:312–319), `foreign_influence_modifier` and `foreign_influence_defense_modifier` (00_influence_scripted_effects.txt:1963–1966; L influence:1 and 8).

**Keys in idea and dynamic-modifier files**

- Vanilla-documented: `stability_factor` (doc:4825), `political_power_gain` (doc:4418), `research_speed_factor` (doc:4600), `production_speed_buildings_factor` (doc:4492), `industrial_capacity_factory` (doc:2917), `industrial_capacity_dockyard` (doc:2907), `industry_free_repair_factor` (doc:2937), `production_factory_max_efficiency_factor` (doc:4464), `war_support_factor` (doc:5115), `army_org_factor` (doc:1952), `encryption_factor` (doc:2458), `enemy_justify_war_goal_time` (doc:2488), `generate_wargoal_tension` (doc:2842), `join_faction_tension` (doc:2992), `lend_lease_tension` (doc:3042), `send_volunteers_tension` (doc:4725), `send_volunteer_divisions_required` (doc:4710), `recruitable_population_factor` (doc:4552), `resistance_growth` (doc:4635), `army_defence_factor` (doc:1852), `local_factories` (doc:3167), `monthly_population` (doc:3723), `subversive_activites_upkeep` (doc:4956, exact spelling), `state_production_speed_buildings_factor` (doc:4869), and the `production_speed_<Building>_factor` template (doc:619).
- Defined locally: `workforce_ratio` (influence:32), `productivity_factor` (influence:120), `wage_factor` (influence:38), `office_park_income_bonus` (influence:83), `chromium_export_rate` (lar:23), `food_export_rate` (lar:29), `health_spending_modifier` (influence:20), `monthly_population` (Intelligence:179).
- Not in vanilla docs and not defined locally (template-dependent, see Section 5): `production_speed_industrial_complex_factor`, `production_speed_arms_factory_factor`, `production_speed_office_park_factor`, `production_speed_infrastructure_factor`, `production_speed_state_infrastructure_factor`, `production_speed_water_infrastructure_factor`, `repair_speed_infrastructure_factor`, `state_production_speed_infrastructure_factor`, `state_production_speed_agri_industrial_complex_factor`.
- Undefined: `MONTHLY_POPULATION` (uppercase; IC_Policies.txt:253, _economic.txt:416). No definition and no vanilla doc entry under that spelling. Lowercase `monthly_population` is documented in vanilla (doc:3723) and defined locally (Intelligence:179).

## 4. Interactions

- Treasury: `income_effect` in `IncomeGenerator.txt` does not read modifiers via `modifier@`. Income-bonus keys feed `IC_Econ_2024.txt` (2553–2561, 2567–2624), not `IncomeGenerator.txt`. `[INFERENCE]` that the treasury path reads these values through `IC_Econ_2024.txt` variables.
- GDP: `gdp_calculation_effect` in `IC_Econ_2024.txt` reads `productivity_factor` and `workforce_ratio` (2553–2623). Drift updates use the same keys.
- Trade: export-rate and trade-penalty keys are read in `IC_Trade_Scripted_Effects.txt`. Definitions are in `lar_operation_modifiers_pre_definition.txt:23–95`.
- Taxes and policies: tax-rate keys are set by ideas (`IC_Laws.txt:154–251`, `CWIC_crisis_ideas.txt`) and read in `policy_focus_effects.txt:370–379` and `IC_Econ_2024.txt:1341–1356`. Definitions are in `influence_modifier_definitions.txt:45–63`.
- UI: localisation keys are `ECON_MODIFIER_TOOLTIP_LINE_*` (Financial_Tab_l_english.yml:294–298). Their variables are `economic_modifier_*` (IC_Economy_scripted_localisation.txt:1177–1181), not modifier keys.

## 5. Problems

Severity H/M/L.

| # | Sev | Location | Problem |
|---|---|---|---|
| 1 | M | IC_Policies.txt:253; _economic.txt:416 | `MONTHLY_POPULATION` (uppercase) is not defined and not in vanilla docs. Lowercase `monthly_population` exists (doc:3723; Intelligence_agency_modifiers.txt:179). `[INFERENCE]` the uppercase key is silently ignored if keys are case-sensitive. |
| 2 | M | IC_Policies.txt (`production_speed_water_infrastructure_factor`, `production_speed_state_infrastructure_factor`, `repair_speed_infrastructure_factor`, `production_speed_infrastructure_factor`); IC_dynamic_modifiers.txt (`state_production_speed_infrastructure_factor`, `state_production_speed_agri_industrial_complex_factor`) | Not defined locally and not in vanilla docs. The vanilla templates `production_speed_<Building>_factor` (doc:619) and `state_production_speed_<Building>_factor` (doc:1021) cover only real building names. `[INFERENCE]` `water_infrastructure`, `state_infrastructure`, and `agri_industrial_complex` are not valid building names, so these keys are no-ops. |
| 3 | M | IC_dynamic_modifiers.txt:814 | `health_spending_modifier = POLLUTION_HEALTH_SPENDING_PENALTY` writes a key that no `modifier@` reads. `IC_Econ_2024.txt:1600, 2209` reads `healthcare_spending_modifier` instead (defined at influence:154). `[INFERENCE]` the pollution health penalty has no effect on the healthcare spending read. |
| 4 | L | lar_operation_modifiers_pre_definition.txt:115 | `agricultural_industrial_complex_income_adjustment` is commented "NOT REAL ONLY FOR DISPLAY". The only use is `Dom_Ideas_Demo.txt:168` (outside the required list). It is not read by `modifier@`. Dead display key. |
| 5 | L | lar_operation_modifiers_pre_definition.txt:121 | `modifier_arms_factory_income` is defined. The variable `economic_modifier_arms_factory_income` is used in IC_Economy_Effects.txt:144, 183, 305, 341. No `modifier@` reads it. Its only modifier use is `JAP_Ideas.txt:586–642` (outside the required list). |
| 6 | L | zzz_restored_modifier_definitions.txt:118 | `office_park_income_adjustment` is not read by `modifier@` (only `office_park_income_bonus` is). Used only by `JAP_Ideas.txt:2050` (outside the required list). Localisation key mismatch: `CWIC_modifiers_l_english.yml:167` uses `modifier_office_park_income_adjustment`. |
| 7 | L | zzz_restored_modifier_definitions.txt:153; Intelligence_agency_modifiers.txt:123, 171 | `trade_goods_cost`, `modifier_mass_media_spending`, and `modifier_trade_efficiency` are defined but unread by `modifier@`. Their only uses are in `DDR_Dynamic_Modifiers.txt:26, 38, 54, 152` (outside the required list), not CWIC idea files. |
| 8 | L | IncomeGenerator.txt | Zero `modifier@` reads. The treasury path `income_effect` does not use modifier keys. Confirm that this is intended. |
| 9 | L | IC_Econ_2024.txt:1335 | Commented-out `tax_rate_lower_class` read. Remove the dead line. |
| 10 | L | IC_Trade_Scripted_Effects.txt:4671 | `extra_trade_to_overlord_factor` is read inside a `test3` block on `NGA.`, which looks like debug code. Check whether it should be removed. |
| 11 | L | lar_operation_modifiers_pre_definition.txt:109; policy_focus_effects.txt:389 | `modifier_tax_efficiacy` has a typo. It is consistent across definition, read, and localisation, so it is not a bug. |
| 12 | L | IC_scripted_effects.txt:58; influence_modifier_definitions.txt:191 | `war_reperations` is defined and read consistently. The name is a typo for "reparations". Low impact. |
| 13 | L | common/modifier_definitions/CWIC_espionage_modifiers.txt.disabled | Disabled file. Not loaded. Dead weight. |

Not flagged:
- `wage_factor` is defined (influence:38) and used by `CWIC_crisis_ideas.txt` (per prior scan).
- `workforce_ratio`, `productivity_factor`, and `*_income_bonus` keys are read by `IC_Econ_2024.txt` and used by ideas.
- Consumption-need and tax-rate keys are read.
- Trade keys are read.

## 6. Open questions

1. Are modifier keys case-sensitive in HOI4? If yes, `MONTHLY_POPULATION` is a no-op. `[INFERENCE]`.
2. Does the engine accept `production_speed_<X>_factor` for building names not in the vanilla list (`water_infrastructure`, `state_infrastructure`, `agri_industrial_complex`)? `[INFERENCE]` no.
3. Does vanilla define `repair_speed_<Building>_factor` (country-level)? The doc grep found only `state_repair_speed_<Building>_factor` (doc:1024).
4. Are `IC_Econ_2024.txt:2553–2624` reads of `*_income_bonus` values written by ideas, or set to 0 by default? Not verified in this audit.
5. Are `Dom_Ideas_Demo.txt`, `JAP_Ideas.txt`, and `DDR_Dynamic_Modifiers.txt` in the active mod load order? If not, findings #4–#7 change.
6. The full idea-file undefined-key sweep is not done. Run a per-file grep with a lookahead that excludes all keys in Sections 3–5 and the vanilla doc headings.
