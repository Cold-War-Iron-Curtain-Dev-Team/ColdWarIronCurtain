# CWIC economy: production slice (buildings, state production, workforce, food/electricity, pollution, resource efficiency, *_income_bonus)

Scope note: read-only. Paths relative to `Cold War Iron Curtain/`. Items marked [INFERENCE] are not directly observed. Gaps are listed in section 6.

## 1. Purpose and entry points

Monthly pipeline (verified wiring):
- `common/on_actions/00_on_actions.txt:11-25` `on_monthly_VTC`: `every_country { ic_pulse_monthly = yes }` (all countries).
- `00_on_actions.txt:27+` `on_monthly`: `monthly_education_pulse` (skipped during insurgency), then `ic_financial_monthly_pulse` only when `is_ai = no` (`00_on_actions.txt:38-41`).
- `scripted_effects/IC_scripted_effects.txt:2-~60` `ic_financial_monthly_pulse`: if `active_insurgency` runs `cwic_insurgency_monthly_pulse` instead; otherwise: delivery cuts (oil, steel, rareEarth, aluminium, chromium, food, cg tiers), resets class pop/pay accumulators, then `income_effect = yes`, `currentMoney += modifier@war_reperations`, resets `*_resource_bonus`, `resource_bonus_script = yes`, `industrial_pulse = yes`, `monthly_borrowing_and_interest_pulse = yes`.
- `IC_scripted_effects.txt:76-82` `ic_pulse_monthly` (not production-specific).
- `IC_scripted_effects.txt:84+` `ic_pulse`: contains `industrial_pulse` for every country (body beyond line 135 not read).
- Other callers: `common/on_actions/on_startup_defines.txt:3223-3224` (`every_country { industrial_pulse = yes }`), `:3256-3257` (`ic_pulse_monthly`, `ic_pulse`); `common/decisions/_generic_decisions.txt:1476-1480` (`every_country { ic_pulse = yes }`), `:1533-1534` (`every_country { income_effect = yes }`), `:1560-1561` (`industrial_pulse`, `monthly_power_projection_gain`); `events/tutorial.txt:124-130` and `:141-144` (`CWIC_force_update_econ_drift_vars`, `gdp_calculation_effect`); insurgency and MLA/Indochina files call `resource_bonus_script` + `industrial_pulse`.
- `IncomeGenerator.txt:292` `income_effect` calls `gdp_calculation_effect`. `00_on_actions.txt` has `#gdp_calculation_effect = yes` commented out.

Player vs AI: the income path (`ic_financial_monthly_pulse`) is human-only via on_monthly. AI reaches `ic_pulse` and `industrial_pulse` through on_startup/decisions. Whether AI gets `income_effect` monthly is [INFERENCE] (depends on decision/event paths, not traced fully).

Key effect chain per monthly tick:
1. `income_effect` (IncomeGenerator.txt:287+) → `gdp_calculation_effect` (IC_Econ_2024.txt:~1300-1400).
2. `gdp_calculation_effect` country preamble: `CWIC_econ_drift_vars` (IC_Econ_2024.txt:1377), `cwic_begin_separatism_rollup`, `check_individual_factory_productivity` (931), `cwic_cache_market_income_multipliers` (965).
3. `every_owned_state` (IC_Econ_2024.txt:1378+) runs per state: `income_effect_every_owned_scope` → `get_total_infrastructure` → `reset_potential_problems` → `cwic_cache_state_category` (if missing) → `check_buildings` (~119) → `calculate_free_building_slots` (211) → `check_resources` (243) → `check_building_slots_size` (300) → `check_other_state_relevant_information` (437) → `calculate_employable_population` (482) → `calculate_theoretical_population` (513) → `calculate_unemployment_factor` (564) → `calculate_conversion_labourer_worker` (660) → `calculate_conversion_lwa_capitalist_and_bureaucrat` (669) → `list_worker_type` (813) → `calculate_national_productivity_factor_var` (866) → `calculate_gross_factory_earnings` (1030) → `calculate_net_poptype_earnings` (1227).
4. Back in `income_effect`: military, flag building, interest, social indices, education/public/welfare/healthcare/policing expenditure, `totalexp`.
5. `industrial_pulse` (IC_Industrial_Pulse.txt:172-620) computes resource consumption, food balance, electricity; `industrial_pulse_food_script` (621-~760) computes per-state farm output and pollution penalty.
6. `resource_bonus_script` (Resource_Efficiency_Bonus.txt) computes per-resource bonuses; `resource_modifier_set_startup` (Resource_Efficiency.txt:391-402) and `resource_idea_effect` (Resource_Efficiency.txt:1-~390) compute `resourceEfficiencyGain`.
7. Per-state pollution: `calc_pollution_country_factors` and `calc_state_pollution_effect` (`CWIC_Enviroment.txt:1, :42`), called from `industrial_pulse_food_script`.

Building upgrades: `IC_State_Decisions_Effect.txt:348` `Upgrade_State_effect`, `:513` `auto_start_state_upgrade_effect`; `IC_Flag_Building_Effects.txt:2` `flag_building_macro`, `:473` `full_upgrade_estimate`. Upgrade progress increments per state category in `IncomeGenerator.txt` (~275-300, `global.upgrade_per_month_fast/nominal/slow/marathon`).

Education: `IC_literacy_calculations.txt:210` `monthly_education_pulse` (deprecated copy at `Econ backup/literacy calculations deprecated.txt:247`).

Consumer goods: `IC_Consumer_Goods.txt:2744` `cwic_cg_monthly_master_tick` (called from `income_effect`).

Separatism: `separatism_effects.txt:1` `calculate_separatism` (called from `income_effect_every_owned_scope`), `:201` `cwic_begin_separatism_rollup`.

## 2. Data model

Per state (scope THIS):
- `buildings^0..^8` (IC_Econ_2024.txt:119-209): ^0 industrial_complex, ^1 arms_factory, ^2 dockyard, ^3 office_park, ^4 agri_industrial_complex, ^5 steel_factory, ^6 tungsten_factory, ^7 powerplants_sum (fossil + renewable + nuclear_powerplant + nuclear_reactor + `refinery`), ^8 total.
- `resources^0..^7` (IC_Econ_2024.txt:243-298): ^0 oil, ^1 aluminium, ^2 rubber (= "Food"), ^3 tungsten, ^4 steel, ^5 chromium, ^6 coal, ^7 sum.
- `state_development` 1..6 and `food_consumption_base` set by `cwic_cache_state_category` (CWIC_state_category_cache.txt:5-~70).
- `building_slots_var`, `slot_factor`, `building_slots_size_var`, `State_Employment^0..^6` (IC_Econ_2024.txt:211-241, 300-480).
- `employable_population` (= (pop - soldier) × `owner:workforce_ratio_drift` × 0.75, IC_Econ_2024.txt:482-511).
- `theoretical_*` sums; `theoretical_unemployed`, `unemployment_factor`, `overemployment_factor`.
- `productivity_factor_var`, `civ/mil/ofp/stl/tng/fod/rsc_productivity_factor_var` (IC_Econ_2024.txt:931-963).
- `gross_factory_earnings` and sector sums; `net_factory_earnings`; wage pots (`substinents`, `farmer`, `labourer`, `soldier`, `artisan`, `worker`, `bureaucrat`, `capitalist`, `rentier`).
- `electricity_debuff_factor` (IC_Econ_2024.txt:910-929).
- Pollution: `statelandpollution`, `statewaterpollution` (clamped 0-600), `pollution_tech_factor` (0.5-1.5), `pollution_agri_organic_factor`, `local_water_recovery_initiative`, `local_land_recovery_initiative` (CWIC_Enviroment.txt).
- Farm: `farm_output`, `farm_output_efficiency`, `farm_tech_local`, `agri_prod_modifier`, `cropBoost`, `food_bonus` (IC_Industrial_Pulse.txt:621-760).
- Quantities: `*_quantity` (reset at IC_Industrial_Pulse.txt:~172-230, incremented at ~621-700 from `non_damaged_building_level@...`).
- Consumption: `oil_consumption`, `steel_consumption`, `aluminium_consumption`, `rare_earth_consumption`, `nuclear_consumption`, `electricity_consumption`, `food_consumption`, `ConsumptionTotal`, `FoodProdTotal`, `FoodBalance(Total)`, `FoodImported`, `FoodExported`, `FoodFromPuppets`, `previousFoodBalance`.
- Resource efficiency: `resourceEfficiencyInfra` (= `building_level@state_infrastructure` + `resourceEfficiencyGain`), `resourceEfficiencyGain`, `oilEfficiencyGain` (country scope), `*_resource_bonus` (country scope).

Country / global:
- `total_factory_amount` (sum of `buildings^8`, set at IC_Econ_2024.txt:1519-1527).
- `average_development`, `Total_Nuclear_Reactors`.
- `outcrowding_limit`, `social_cost_base`, `strategic_forces_expend`, `industrial_complex_total`, `farm_total`, `dockyard_total`, `oil_refinery_total`, `steel_works_total`, `tungsten_factory_total`, `fossil_fuel_powerplant_total`, `renewable_powerplant_total`, `nuclear_powerplant_total`, `tourism_infrastructure_total`, `office_park_total`, `trade_infrastructure_total` (IncomeGenerator.txt ~lines 1-285).
- Drift variables (lagged toward modifier targets by 0.01/tick): `industrial_park_income_bonus_drift`, `military_factory_income_bonus_drift`, `office_park_income_bonus_drift`, `foundry_district_income_bonus_drift`, `metallurgy_plant_income_bonus_drift`, `other_resources_income_bonus_drift`, `dockyard_income_bonus_drift`, `productivity_factor_drift`, `workforce_ratio_drift` (IC_Econ_2024.txt:2552-2636; writers `CWIC_force_update_econ_drift_vars` 2552 and `CWIC_econ_drift_vars` 2563).
- Global: `global.eco_output_factor` (IC_scripted_effects.txt:637-641; from `eco_health`), `global.eco_output_rate` (reset to 0 in on_startup_defines.txt:2897, used at IC_Industrial_Pulse.txt:702), `global.GlobalCredit`, `global.CashCrop_*`, `global.upgrade_per_month_*`.
- Antiquated industry (DDR only): `antiquated_industry_elec`, `antiquated_industry_oil` (set at `history/countries/DDR - East Germany.txt:296-297`; adjusted in `national_focus/GDR_*.txt` and `GDR_50s_ECON.txt`; applied at IC_Industrial_Pulse.txt:360-362, 401-403).

## 3. Formulas (step by step)

### 3.1 Building counts and slots
- `check_buildings` (IC_Econ_2024.txt:119-209): building_level sums per category.
- `calculate_free_building_slots` (211-241):
  `building_slots_var = modifier@local_building_slots + owner:modifier@global_building_slots + extra_building_slots`;
  `slot_factor = 1 + modifier@local_building_slots_factor + owner:modifier@global_building_slots_factor`;
  `building_slots_var *= slot_factor`; then `-0.5` and round (free slots = slots − buildings^8).
  Note: the subtraction of `buildings^8` happens in the lines not fully displayed; read summary [INFERENCE] on exact order.
- `check_building_slots_size` (300-435): base size by category (pop1=75 … pop20=1500, default 15), divided by `slot_divisor = 0.5 × state_development`.

### 3.2 Employment coefficients
- `check_other_state_relevant_information` (437-480): `base = 0.5 × (0.9 × state_development) × 60`;
  `SE^0 = base`, `SE^1 = base × 0.35` (mils), `SE^2 = base × 6` (office), `SE^3 = base / 10` (steel), `SE^4 = base × 5/7` (tungsten/other), `SE^5 = base × 3.5 / state_development` (food), `SE^6 = building_slots_size_var`.

### 3.3 Employable population
- `soldier = conscription × (1 + owner:modifier@conscription_factor) × state_population_k` (IC_Econ_2024.txt:487-491).
- `employable_population = (state_population − soldier) × owner:workforce_ratio_drift × 0.75` (499-503).

### 3.4 Theoretical employment and unemployment
- `theoretical_pop_sum = b0·SE0 + b1·SE2 + b2·SE1 + b3·SE2 + b5·SE3 + b6·SE4 + res7·SE4` (IC_Econ_2024.txt:513-562). **Suspicious**: mils (b1) use SE^2 (office coefficient), dockyard (b2) use SE^1 (mil coefficient). Labels in the coefficient block are mil=SE^1, office=SE^2 → likely swapped. [INFERENCE: intent unverified.]
- Farmer: `theoretical_pop_sum_food = res2 + farm_output`, × `farmer_y_axis_shift = (economic_y_axis − 18) × (−0.1) + 0.5`, × SE^5, added to `theoretical_pop_sum`.
- `theoretical_unemployed_raw = employable_population − theoretical_pop_sum`; `overemployment_factor = 1` or `employable/theoretical` when raw<0; `theoretical_unemployed = max(raw, 0)` (564-~585).
- Artisan conversion (587-~660): `artisan_rate = (college×0.5 + high_school×0.25 + primary×0.25) × 0.01`; `artisan_conversion_base = clamp(SE^6 × building_slots_var, 0, theoretical_unemployed)`; `artisan = base × rate`; `substinents = base − artisan`; `unemployed −= base`; `unemployment_factor = unemployed / employable_population` if >0.
- Labourer→worker (660-667): `worker = labourer × overemployment × high_school × 0.01`.
- Capitalist/rentier/bureaucrat (669-811): capitalist rates 0.001/0.0015/0.0005 scaled by `max(economic_x_axis − 1, 0)` and `(1 + office_park × 0.33)`; rentier rates 0.0015/0.0025/0.0005 with office park 0.75, agri 0.33, tourism 0.33; bureaucrat factor `(economic_x_axis − 18) × (−0.1) + 1.75 + office_park×0.67 + industrial_complex×0.2 + arms_factory×0.3 + dockyard×0.3`; bureaucrat rates 0.05 (worker), 0.025 (artisan, labourer).
- `list_worker_type` (813-832) accumulates country `*_sum` vars.

### 3.5 Productivity
- `calculate_national_productivity_factor_var` (866-908; per state despite name):
  `productivity_factor_var = ((literate_educated + 1.25×primary + 1.75×high_school + 3.5×college)/100 × state_development + productivity_factor_drift) × overemployment_factor × (1 + infrastructure_level × 0.05) × PREV.electricity_debuff_factor`, then `× cwic_prod_final_mult`, where `cwic_prod_final_mult = clamp(1 + CWIC_productivity_mult − CWIC_bm_productivity_penalty, 0.10, 1.10)`.
- `get_electricity_debuff` (910-929): `electricity_debuff_factor = 1 − max(0, −coal)/total_factory_amount` when `coal<0`. `total_factory_amount` set at 1519-1527 (sum of `buildings^8`). **Division by zero when no buildings** [INFERENCE: engine behaviour unverified; possible `total_factory_amount = 0` for states with no buildings or empty countries].
- `check_individual_factory_productivity` (931-963): civ = 1 + industrial_park_income_bonus_drift; mil = 1 + military_factory_income_bonus_drift; ofp = office_park_income_bonus_drift × (office_park_penalty_rate if flag `office_park_penalty`) + 1; stl = 1 + foundry_district_income_bonus_drift; tng = 1 + metallurgy_plant_income_bonus_drift; fod = modifier@food_income_bonus; rsc = 1 + other_resources_income_bonus_drift. `doc` line commented out at 961-962.
- `cwic_cache_market_income_multipliers` (965-1028): civ multiplier 1.25 / 1.5 / 1.75 by economic_x_axis / economic_y_axis windows; ofp 1.35 / 1.65 / 1.9 with same windows.

### 3.6 Gross earnings (per state)
`calculate_gross_factory_earnings` (1030-1225):
- civ: `2 × civ_mkt × pf × civ_prod × buildings^0`
- mil: `1.25 × pf × mil_prod × buildings^1`
- dock: `2.5 × pf × PREV.doc_productivity_factor_var × buildings^2` (1057) — **undefined variable** (see 5.1)
- ofp: `7 × ofp_mkt × pf × ofp_prod × buildings^3`
- steel: `1.75 × pf × stl_prod × buildings^5`
- tungsten: `1.75 × pf × tng_prod × buildings^6`
- resources: `0.5 × pf × rsc_prod × resources^2`
- food: `(0.5 + cropBoost) × pf × fod_prod × pollution_mult_land × pollution_mult_water × resources^7`; land pollution multipliers disturbed 0.95 / degraded 0.9 / severe 0.8 / catastrophic 0.65 / deadzone 0.4; water 0.95 / 0.9 / 0.8 / 0.6 / 0.3. `cropBoost` from biome tables (IC_Econ_2024.txt ~1030-1225), scaled by `1 + (economic_x_axis==26)×0.5 + (==24)×0.5`.
- Sector sums accumulate into `gross_factory_earnings`, `civilian_sector`, `mic_sector`, `service_sector`, `mill_sector`, `rgo_sector`, `food_sector`, `corporate_gross_income`.

### 3.7 Net wages
`calculate_net_poptype_earnings` (1227-~1300): `net_factory_earnings = gross − lowerclass − middleclass`. Wage shares (per 100): substinents 0.2; farmer 0.7×pf; labourer 1.0×pf; soldier 1.6×pf; artisan 2.2×pf; worker 2.0×pf (middle class); bureaucrat 3.5×pf (middle class); capitalist (100 − 97.5 if econ_x<6)×pf; rentier (100 − 97 if econ_x<6)×pf; upperclass = capitalist + rentier.

### 3.8 Industrial pulse: resource consumption
- Base per building (IC_Industrial_Pulse.txt:172-300): oil/steel/aluminium/rare_earth/dockyard base 1; reactor electricity 2, chromium 2; nuclear_power 1; steel_factory electricity 2, oil 1; tungsten electricity 3; refinery electricity 2; electricity 1. Electricity modifier `modifier@electricity_consumption_need` multiplies reactors (×2), steel (×2), tungsten (×3), refinery (×2) and total.
- Tech multipliers on `*_consumption` (chemistry_II/IV/VI/VII, materials_II–VII, ecoenergy_I–VII, management_IX, plastics_III/VI, electriccars) [INFERENCE: details not re-read].
- DDR: `steel_factory_electricity_consumption += antiquated_industry_elec`, `steel_factory_oil_consumption += antiquated_industry_oil` (360-362); `electricity_consumption += antiquated_industry_elec`, `oil_consumption += antiquated_industry_oil` (401-403).
- Consumption = `quantity × base × (0.75 consumer-goods adj.)` for industrial_complex oil/steel/electricity (~420-470); office_park, dockyard, reactor, powerplant, steel, tungsten, refinery similarly.
- Totals (~480-520): `oil_consumption`, `steel_consumption`, `aluminium_consumption`, `rare_earth_consumption`, `nuclear_consumption`, `electricity_consumption`.

### 3.9 Food balance (IC_Industrial_Pulse.txt ~520-600)
- `FoodProdTotal += agri_industrial_complex_quantity` and `+= food_bonus`; `FoodBalance += food_bonus`.
- `food_consumption *= (1 + modifier@food_consumption_need)`; `FoodBalance −= food_consumption`.
- Imports `resource_imported@rubber` → FoodImported and FoodProdTotal; exports `foodExport` → FoodExported.
- `FoodBalanceTotal = FoodProdTotal − ConsumptionTotal`; `FoodFromPuppets` adjustments.
- `food_negative_in_capital` dynamic modifier added when missing.
- `food_penalty = −rubber / food_consumption` when rubber < 0.
- Flags: `food_famine_extreme` (>3), `food_famine` (>0.8), `food_shortages` (>0.2), `food_highprices` (>0).
- `food_penalty_political = clamp(−0.1 × food_penalty, −0.1, 0)`.
- `country_event = { id = food_pulse.1 days = 1 }`; `cwic_register_own_trade_offers`.
- Food is stored as state resource `rubber` (labelled "Food"). See 5.7.

### 3.10 Farm output (industrial_pulse_food_script, IC_Industrial_Pulse.txt:621-~760)
- Base `farm_output` from biome table (desert −0.5, desertlush +1.0, tundra −0.5, mountains −0.25, arid_mountains −0.75, boreal +1.5, temperate +2.5, tropical +3.0, savanna +2.0, subtropical_monsoon +2.5, delta +3.5, wetlands +2.5, mediterranean +2.0, steppe ×1.05); water tiers (basic ×0.75, lakes ×1.25, river ×1.5, riverlarge ×1.75, freshwatersea ×2.0); `farm_tech_local` adjusted by water_infrastructure.
- `farm_tech = 1 + 0.15 × agriculture_I..VIII` (IC_Industrial_Pulse.txt ~210-235).
- `farm_output *= farm_tech_local`; `*= PREV.farm_output_modif` (agricultural_dysfunction_0..4 = 0.5/0.4/0.3/0.2/0.1; cotton_emphasis 0.35; banned_wheat_cultivation 0.5; Modernized_Cotton_Crops 0.15; sov_* 0.95–1.1); `+= global.eco_output_rate`.
- `farm_output *= non_damaged_building_level@agri_industrial_complex`; `farm_output_efficiency = farm_output × resourceEfficiencyInfra`, `farm_output += farm_output_efficiency`.
- `farm_output *= (1 + modifier@agricultural_complex_production_bonus)`.
- Pollution: `land_pollution_penalty = statelandpollution / 600 × 0.4`; `water_pollution_penalty = statewaterpollution / 600 × 0.2`; `pollution_multiplier = 1 − (land + water)`; `farm_output *= pollution_multiplier`.
- Colonial adjustment: if economic_x_axis = 26 or 24, `cropBoost × 0.5` (temp) [note: uses `multiply_temp_variable` on `cropBoost`, applied later in gross earnings].
- `PREV.food_bonus += farm_output`.

### 3.11 Pollution (CWIC_Enviroment.txt)
- `calc_pollution_country_factors` (1-41): `pollution_tech_factor = 1 + Σ tech increases (ww_infra 0.10, ww_oil 0.10, gas_I 0.10, gas_II/III 0.05, grid_I/II 0.05, excavation_I/III 0.05, plastics_I 0.05, plastics_III 0.075) − Σ reductions (inframanagement_V −0.10, VI −0.15, VII −0.20; renewables_I −0.10, III −0.15, IV −0.20 (duplicated line: IV also −0.25), V −0.15, conversion −0.25, VI −0.10)`, clamped 0.5–1.5. `pollution_agri_organic_factor` = 0.10 per organic_I..VII.
- `calc_state_pollution_effect` (42+): population_factor (0.5 for pop_level_1 ... 5 for pop_level_20), development_factor (0.2 dev0 ... 1.8 dev5), agri_dev_factor (0.25 default ... 3).
- Land base: arms 1.5, industrial 1.2, dockyard 0.8, synthetic_refinery 2.0, steel 4, tungsten 1.5, fossil 2.0, reactor 0.8, office 0.5, agri `0.6 × (agri_dev_factor) − organic`, renewable −1.5. Multiplied by population × development × tech factors, then `+ resource_pollution_land` (oil 0.03, aluminium 0.02, tungsten 0.02, steel 0.02, chromium 0.05), `/ 10`; micro urban `/ 3`; `statelandpollution += land_base` clamped 0–600.
- Water base: industrial 0.5, arms 0.35, dockyard 1, agri `2 × ...`, water_infrastructure `0.4 × agri_dev`, refinery 2, steel 4, tungsten 1, fossil 1.2, reactor 3; × population × development × tech; `+ resource_pollution_water` (oil 0.05, chromium 0.1, steel 0.05, aluminium 0.05); `/10`; `statewaterpollution += water_base` clamped 0–600.
- Recovery (`apply_pollution_recovery_effect`, line ~ 255+): base land −1, water −2; campaigns (`local_*_recovery_initiative` decremented by 1 per tick); building/tech/policy factors. Remaining lines 300-783 not read.

### 3.12 Resource efficiency
- `resource_modifier_set_startup` (Resource_Efficiency.txt:391-402): `resourceEfficiencyInfra = building_level@state_infrastructure`; `resource_idea_effect`; `resourceEfficiencyInfra += resourceEfficiencyGain`.
- `resource_idea_effect` (1-~390): sums `oilEfficiencyGain` (Oil_Expansion, Oil_Deregulation, Turkish_Petroleum_Company +0.10 each) and `resourceEfficiencyGain` from ideas/flags (examples: US_Resource_Bonus +0.10; comecon_level_1 +0.25; comecon_resource_extraction +0.25; comecon_level_2 +0.125; comecon_level_3 +0.05; DDR_idea_second_five_year_plan +0.2; Privatisation_Level1 +0.2, Level2 +0.08, Level3 +0.12, Level5 +0.04, Level2 +0.16 again; gen_materialist_1/2 +0.20; OPEC +0.10; Petrobras +0.10; Iraq_Petroleum_Company +0.15; `economic_x_axis = 24` +0.15; etc.). Lines 300-404 not fully read.
- `resource_bonus_script` (Resource_Efficiency_Bonus.txt): zeroes steel/oil/aluminium/nuclear/rare_earth bonuses at country scope; per owned state:
  - `tungstenBonus = resource@tungsten × resourceEfficiencyInfra` → added to `PREV.rare_earth_bonus`;
  - `aluminiumBonus = resource@aluminium × eff` → aluminium bonus;
  - `nuclearBonus = resource@chromium × eff` → `nuclear_resource_bonus`;
  - `steelBonus = resource@steel × eff` → steel bonus;
  - `oilBonus = resource@oil × (oilEfficiencyGain + resourceEfficiencyInfra)` → `oil_resource_bonus`, with `add_to_variable = { oilEfficiencyGain = resourceEfficiencyInfra }` executed inside the per-state loop.

### 3.13 Income side (IncomeGenerator.txt)
- Tourism income: `tourism_infrastructure_total = global.GlobalCredit × commerce_credit_factor_difference × stability / 12`, added to `IncomeTotal` (~420-450).
- Export loops (~500-700): dedupe with `Export_List`/`is_in_array`; `ROOT.<res>_exports = ROOT.<res>ExportTargetMonthly^THIS`; steel dedupe fixed 2026-07-05.
- `totalexp = military_total_exp + public_expenditure_total + policing + education + custom_expenses`; `public_expenditure_total = public_services + welfare + healthcare`.
- Expenditure formulas: healthcare `max_manpower × 0.001` (IC_Econ_2024.txt:1590-1605); education `max_manpower × 0.01` (1623-1645); public services `max_manpower / 10000`, "gives out at 50%" (1646-~1660); welfare (1537-1589), policing (1606-1622) bodies not read in detail.
- `grossdomesticproduct_influence_limit = grossdomesticproduct × 5` (IncomeGenerator.txt ~ income_effect preamble).
- `CorruptPolicyExcess = CorruptionLevel × 0.2`.
- `get_total_infrastructure` (IC_Econ_2024.txt:1530-1536): `total_infrastructure = 1 + state_infrastructure + infrastructure`.

### 3.14 Modifier-to-variable plumbing
- Drift vars converge by 0.01/tick toward `modifier@<name>` targets (IC_Econ_2024.txt:2563-2636). Called once per `gdp_calculation_effect` (IC_Econ_2024.txt:1377) and twice in tutorial event (events/tutorial.txt:124, 142, 144).
- `productivity_array` built from drift vars (2627-2636).

## 4. Interactions with other subsystems

- Money: `income_effect` produces `IncomeTotal`, `totalexp`, sets `currentMoney` via `ic_financial_monthly_pulse` (`+= modifier@war_reperations`). War reparations also processed by `cwic_process_war_reparations` at the start of `income_effect` (IncomeGenerator.txt:288). Possible double count [INFERENCE].
- Workforce ↔ wages ↔ income: employment (SE coefficients, unemployment, conversions) feeds productivity and gross earnings; gross minus class wages gives `net_factory_earnings`, which feeds tax/revenue (tax modules not read).
- Electricity debuff: negative coal → `electricity_debuff_factor` → multiplies productivity (IC_Econ_2024.txt:878).
- Food: food balance → `food_penalty_political` and food flags → stability/ideas (`CWIC_crisis_ideas.txt` consumes `food_consumption_need` and `food_income_bonus` directly, e.g. lines 405-745; IC_Policies.txt:1477-1727 sets `food_consumption_need` ±; MNC_Effects.txt:118-158 sets `food_income_bonus`).
- Pollution → farm_output (pollution_multiplier) and food gross earnings (land/water tiers).
- Trade: exports (IncomeGenerator.txt ~500-700) depend on `*ExportTargetMonthly` and the `*_exports` variables; food/chromium/rare earth naming crossover (5.7).
- Upgrades: `Upgrade_State_effect` and `full_upgrade_estimate` (IC_State_Decisions_Effect.txt:348, IC_Flag_Building_Effects.txt:473) change building levels which feed every calc.
- Modifiers used by ideas/policies/national_focus (see section 5.4 and 5.5).

## 5. Problems

Severity: H = wrong results/likely bug; M = wrong scope or dead ref with visible impact; L = cleanup/balance.

### 5.1 Bugs
1. **[H] Dockyard earnings use undefined variable.** `doc_productivity_factor_var` is only set in commented lines `IC_Econ_2024.txt:961-962`, but is read at `IC_Econ_2024.txt:1057` (`multiply = PREV.doc_productivity_factor_var`). Engine treats uninitialised vars as 0 [INFERENCE per GOTCHAS], so dockyard gross earnings = 0. Fix: uncomment with the `dockyard_income_bonus_drift` source, or read it directly.
2. **[H] Agent Orange decay checks wrong variable.** `IncomeGenerator.txt` ~lines 25-40 (`income_effect_every_owned_scope`) checks `napalm_total < 1` in the agent_orange branch instead of `agent_orange_total` [from earlier read; line numbers approximate].
3. **[H] `oilEfficiencyGain` accumulates across states.** `Resource_Efficiency_Bonus.txt` (oilBonus branch) does `add_to_variable = { oilEfficiencyGain = resourceEfficiencyInfra }` inside `every_owned_state`, mutating a country-scope variable. Each state adds its own infra value into the country sum, so later states see inflated gains [INFERENCE on magnitude; the mutation itself is directly observed].
4. **[M] Privatisation_Level2 counted twice.** `Resource_Efficiency.txt:144-148` (+0.08) and `:160-164` (+0.16) both test `has_idea = Privatisation_Level2`. Level 2 active gives +0.24 total [verified by grep]. Likely typo; intent unverified.
5. **[M] Tungsten feeds rare-earth bonus; chromium feeds nuclear bonus.** `Resource_Efficiency_Bonus.txt`: `tungstenBonus → PREV.rare_earth_bonus`, `nuclearBonus = resource@chromium × eff → nuclear_resource_bonus`. Naming suggests a mapping error or mislabelled variables. Consumer side not verified.
6. **[M] Rare earth exported as tungsten.** `IncomeGenerator.txt` ~540-560: `rareEarthExportTargetMonthly` written to `tungsten_exports` (naming crossover; verify).
7. **[M] Food stored in `rubber` resource.** `resources^2` labelled "Food" (IC_Econ_2024.txt:243-298) and `resource@rubber`, `resource_imported@rubber`, `FoodImported` (IC_Industrial_Pulse.txt:~540-600). The rubber resource is the food stock. Mislabel invites future bugs; not a math bug by itself. Confirm whether `FoodBalanceTotal` double-counts stock (not verified; flagged for the next reviewer).
8. **[M] Theoretical employment coefficients possibly swapped.** `IC_Econ_2024.txt:513-562`: mils (`buildings^1`) multiplied by `SE^2` (office coefficient) and dockyard (`buildings^2`) by `SE^1` (mil coefficient). Labels in IC_Econ_2024.txt:437-480 define SE^1 = mils and SE^2 = office. [INFERENCE: swap unintended.]
9. **[M] Division by zero risk.** `get_electricity_debuff` divides by `total_factory_amount` (IC_Econ_2024.txt:922) which can be 0 (set at 1519-1527). [INFERENCE: engine result unverified; guard absent.]
10. **[M] `refinery` building name.** `check_buildings` powerplants_sum (IC_Econ_2024.txt:~179) uses `refinery`; `common/buildings/00_buildings.txt:273` defines `synthetic_refinery` and no `refinery` was found in the buildings grep. So `refinery` building level is always 0 in ^7 [INFERENCE that the name is undefined; grep shows no `refinery = {` definition].
11. **[M] Pollution tech duplicate.** `CWIC_Enviroment.txt` renewables_IV appears twice (−0.20 and −0.25) in pollution_tech_factor.
12. **[M] Possible war reparation double count.** `cwic_process_war_reparations` at start of `income_effect` (IncomeGenerator.txt:288) and `currentMoney += modifier@war_reperations` in `ic_financial_monthly_pulse` (IC_scripted_effects.txt:58). [INFERENCE.]

### 5.2 Dead / duplicate / legacy code
- **[M] `food_consumption_calculator` is dead.** Defined at `IC_Industrial_Pulse.txt:2-170`; no callers anywhere in `Cold War Iron Curtain/` (grep). Its table is duplicated in `CWIC_state_category_cache.txt:5-~70` (`food_consumption_base`), which is the live path (`industrial_pulse_food_script` at IC_Industrial_Pulse.txt:~621-700). Delete the calculator.
- **[L] Empty stubs.** `IncomeGenerator_ideas_and_flags.txt:136-139` `specific_corruption_efficiency_calc = {}` and `edict_ideas_calc_plus = {}`; section headers MILITARY, HEALTHCARE, EDUCATION, WELFARE, CPI, PUBLIC, TAX, OFFICE PARK, REFINERY, AGRICULTURE, INDUSTRY are empty (1-135).
- **[L] `doc` productivity commented block** (IC_Econ_2024.txt:961-962) plus live reference (1057) — see 5.1.1.
- **[L] Commented call** `#gdp_calculation_effect = yes` in `00_on_actions.txt` (~line 31).
- **[L] Deprecated literacy copy**: `Econ backup/literacy calculations deprecated.txt:247` (and the "Econ backup" folder itself) — not loaded by the mod? [INFERENCE: check that backup folder is not under `common/`].
- **[L] Duplicate pollution-tech `renewables_IV`** (see 5.1.11).
- **[L] `farm_output_efficiency` pattern** duplicates the building-level scaling (IC_Industrial_Pulse.txt:704-712).

### 5.3 Performance hot spots
- `gdp_calculation_effect` runs every monthly tick for each owned state through ~20 effects (IC_Econ_2024.txt:1378+). Per-state `every_owned_state` loops nest: `income_effect_every_owned_scope` contains `calculate_separatism` (which may loop) [INFERENCE].
- `industrial_pulse` runs once per country per tick and also for every state in `industrial_pulse_food_script` (IC_Industrial_Pulse.txt:621+); `resource_bonus_script` runs another per-state loop. Three to four full state loops per month per country.
- `cwic_cache_state_category` triggers a 60+ branch `else_if` chain (CWIC_state_category_cache.txt:5-~70) per state when missing [performance cost low; only on init].
- Pollution: two per-state calls (land + water) with ~50 `has_tech` checks per country each tick (CWIC_Enviroment.txt:1-41); fine per country but repeated for every country.
- `industrial_pulse` computes `*_quantity` by summing `non_damaged_building_level@...` per state (IC_Industrial_Pulse.txt:621-700), i.e., per-state building queries.
- Fix path: merge state loops, cache `total_factory_amount` once.

### 5.4 Modifier families: defined vs used
Defined in `common/modifier_definitions/influence_modifier_definitions.txt` (verified):
- `industrial_park_income_bonus` (71), `military_factory_income_bonus` (77), `office_park_income_bonus` (83), `metallurgy_plant_income_bonus` (89), `foundry_district_income_bonus` (95), `food_income_bonus` (101), `other_resources_income_bonus` (107), `dockyard_income_bonus` (113), `war_reperations` (191), `workforce_ratio` (32), `tax_rate_middle_class` (57), `productivity_factor` (120).
Defined in `lar_operation_modifiers_pre_definition.txt`: `agricultural_complex_production_bonus` (65), `food_consumption_need` (71), `electricity_consumption_need` (77).

Used but not found as a definition in the grep scope:
- `local_building_slots`, `global_building_slots`, `local_building_slots_factor`, `global_building_slots_factor`, `conscription_factor`, `conscription`: read via `modifier@` at IC_Econ_2024.txt:212-224, 487-488. Not found under `modifier_definitions` in the grep (only anchored pattern search, which found no definitions). [INFERENCE: may be engine-built-in; verify against vanilla HOI4 `modifier_definitions`.]
- `productivity_factor` and `workforce_ratio` are defined (lines 120 and 32). Good.
- `modifier@food_income_bonus` read at IC_Econ_2024.txt:955 — defined.
- `modifier@production_factor` etc. not in this slice.

Defined but no consumer found in the production slice (candidates for removal after verification):
- `dockyard_income_bonus` is read through `dockyard_income_bonus_drift` (2559), but the dock productivity variable it should feed is dead (5.1.1). Effectively the modifier has no working consumer.
- `other_resources_income_bonus`: consumed via `other_resources_income_bonus_drift` (2558) and `rsc_productivity_factor_var` (958). Live.
- `dockyard_income_bonus` and `foundry_district_income_bonus` are live through drift vars.

Used via `modifier@` but not defined in the mod (search for definitions): `antiquated_industry_elec`/`oil` are *variables*, not modifiers, and are defined by `set_variable` in DDR history (fine).

Used via `_drift` variables only (no direct modifier definition needed): `productivity_factor_drift` and `workforce_ratio_drift` read `modifier@productivity_factor` / `modifier@workforce_ratio`, both defined.

### 5.5 Modifier usage with wrong scope/family (balance and bugs)
- `food_income_bonus` is set by ideas/national focus at +0.02 to +0.15 (JAP_Ideas, Tibet, USA_Congress_Acts, soviet.txt:2410, 2425, 2441 and DDR/SOV spirits). Because `food_income_bonus` feeds `fod_productivity_factor_var` (IC_Econ_2024.txt:955), it scales food gross earnings but also `farm_output` is separately built from `farm_tech` etc. [INFERENCE: two parallel food-output paths, double-scaling possible.]
- `CWIC_crisis_ideas.txt` lines 405-745: `food_income_bonus` negative (−0.03 to −0.35) together with `food_consumption_need` +0.03 to +0.28 — crisis ideas hit both sides; check for stacking with `food_penalty_political`.
- `electricity_consumption_need` set to 0.3 and 0.25 in New_Ideologies_Ideas.txt:1075, 1088 — large cost increases; plus DDR antiquated industry adds flat `antiquated_industry_elec` (2.5 at DDR start) to consumption (DDR history:296) which is not a multiplier. Balance review needed.
- `office_park_income_bonus` in New_Ideologies_Ideas.txt:6289-6357 (0.1–0.3) while `production_speed_industrial_complex_factor` −0.1…−0.3 at the same time (trade-off block) — ok but check that each tier is intentional.
- `workforce_ratio_drift` is also set by `CWIC_DM_CG_WORKFORCE_RATIO` (IC_dynamic_modifiers.txt:955) and national spirits; `CWIC_econ_drift_vars` drifts it 0.01/tick toward target, so the effective ramp is slow (up to 1 month per 0.01 difference). Check Nepal `workforce_ratio = NEP_PAJANI_workforce_ratio_var` (CWIC_Nepal_Dynamic_Modifiers.txt:19).

### 5.6 AI non-participation
- `ic_financial_monthly_pulse` runs only for `is_ai = no` (`00_on_actions.txt:38-41`). AI never runs the full monthly `income_effect` through that path. Other paths (`ic_pulse`, `industrial_pulse`, decisions `every_country`) do cover AI [INFERENCE on coverage].
- Balance: AI receives production effects through `industrial_pulse` but not the finance pulse (currentMoney/war reparations/interest). AI money effects inconsistent with player.

### 5.7 Naming/mapping traps (GOTCHAS-related)
- `rubber` = food; `tungsten` → `rare_earth_bonus`; `chromium` → `nuclear_resource_bonus`; `rare earth` → `tungsten_exports`; `refinery` vs `synthetic_refinery`. Each is a naming crossover that will mislead future edits.
- `state_id − 2^30`-style negative state variables: not applicable here; coal shortage (`coal < 0`) used as negative state variable in `get_electricity_debuff` (IC_Econ_2024.txt:910-929) — check `max(0, −coal)`; `coal` is a country/state variable whose sign convention must be verified.
- Multiplication by undefined PREV variables: `PREV.doc_productivity_factor_var` (5.1.1). Per GOTCHAS, `multiply` with missing PREV yields 0 [INFERENCE from GOTCHAS].

### 5.8 error.log / game.log
- Grep for `IC_Econ_2024|IC_Industrial_Pulse|IncomeGenerator|Resource_Efficiency|food_consumption|building_slots|modifier.*(not defined|undefined)` in `error.log` and `game.log`: no matches. No production-slice entries logged in the recent run.

## 6. Open questions / not fully covered
- `IncomeGenerator.txt:703-3141` (export loop tail, tourism, military_expenditure 2730-2923, agency_calc 2924-3084, GDP_Extra_Calcs 3085-3141) not read in detail.
- `IC_Econ_2024.txt:1660-2551` (calc_* bodies beyond headers, separatism hook, tax helpers) not read; `calculate_sum_up_total` body not read.
- `IC_Industrial_Pulse.txt:172-620` read only in summary; tech multiplier details not re-verified.
- `CWIC_Enviroment.txt:300-783` (rest of recovery effects) not read.
- `Resource_Efficiency.txt:300-404` not read (Privatisation lines confirmed at 136-172).
- `common/buildings/*.txt` read only for building names; cost/effects not reviewed.
- `IC_literacy_calculations.txt` body not read.
- Whether `income_effect` is reached for AI and where (decisions/events) not fully traced.
- Engine semantics: division by zero result; uninitialised PREV vars (assumed 0 per GOTCHAS).
- Whether `conscription`, `local_building_slots`, `global_building_slots`, `*_factor` modifiers are vanilla HOI4 engine modifiers (not defined in mod) — verify against base game.
- Whether `Econ backup/` folder is loaded (it lies outside `common/`).
- Whether `food_consumption_base` table and the dead `food_consumption_calculator` table agree (they do on sampled rows: pop1=0.5, pop20dev5=50, pop1dev5=3 match).

## Files (key anchors)
- `common/on_actions/00_on_actions.txt:11-41`
- `common/on_actions/on_startup_defines.txt:2890-2897, 3223-3224, 3256-3257`
- `common/scripted_effects/IC_scripted_effects.txt:2-82, 84-135, 637-641`
- `common/scripted_effects/IC_Econ_2024.txt:119-209, 211-241, 243-298, 300-480, 482-562, 564-811, 813-963, 965-1028, 1030-1300, 1308-1403, 1518-1527, 1530-1660, 2552-2636`
- `common/scripted_effects/IC_Industrial_Pulse.txt:2-170 (dead calc), 172-620, 621-762`
- `common/scripted_effects/IncomeGenerator.txt:1-703, 287-292, 420-450, 500-700`
- `common/scripted_effects/IncomeGenerator_ideas_and_flags.txt:1-139`
- `common/scripted_effects/Resource_Efficiency.txt:1-404 (partial), 136-172, 391-402`
- `common/scripted_effects/Resource_Efficiency_Bonus.txt:1-40`
- `common/scripted_effects/CWIC_Enviroment.txt:1-300`
- `common/scripted_effects/CWIC_state_category_cache.txt:1-70`
- `common/buildings/00__societalbuildings.txt:9-145`, `common/buildings/00_buildings.txt:57-399`
- `common/modifier_definitions/influence_modifier_definitions.txt:32-191`, `lar_operation_modifiers_pre_definition.txt:65-80`
- `history/countries/DDR - East Germany.txt:296-297`
- `events/tutorial.txt:123-144`
- `common/decisions/_generic_decisions.txt:1476-1561`
