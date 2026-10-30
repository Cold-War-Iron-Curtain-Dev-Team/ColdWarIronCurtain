# CWIC Economy: Taxes, Laws, Policies, Economic Systems (read-only audit)

Scope: taxes, Laffer/tax-avoidance curve, tax-rate modifiers, economic laws/policies (ideas), policy-tier machinery, economic systems, investments, and how choices reach the monthly money pulse. Paths are relative to `Cold War Iron Curtain/` unless noted. Unverified items are marked `[INFERENCE]`. Coverage note: `policy_focus_effects.txt` (8,302 lines), `IC_Laws.txt`, `IC_Policies.txt`, `zz_econ_laws.txt`, `_economic.txt`, `IC_Economic_Investments.txt`, `IC_Industrial_Pulse.txt`, `IC_Economy_Effects.txt`, and `CWIC_Econ_Change*` / `IC_Economic_System_Triggers*` were only partially read or not located. Those gaps are listed in §6.

---

## 1. Purpose and entry points

### 1.1 Monthly pulse chain (verified)

| Step | Where | Who | Notes |
|---|---|---|---|
| `on_monthly` → `ic_financial_monthly_pulse` | `common/on_actions/00_on_actions.txt:38-41` | `is_ai = no` only | Players only. Finance-side. Also `monthly_education_pulse` (:33-37) for all non-insurgent countries. |
| `on_monthly_VTC` → `every_country { ic_pulse_monthly }` | `00_on_actions.txt:19-23` | all countries | `ic_pulse_monthly` (`scripted_effects/IC_scripted_effects.txt:76-82`) runs `federation_calculator`, `monthly_power_projection_gain`, `monthly_set_fpp`, `monthly_infamy_calc`, UI. No tax code. |
| `ic_pulse` | `on_startup_defines.txt:3257`; `decisions/_generic_decisions.txt:1471, 1477` | all countries | Calls `income_effect` at `IC_scripted_effects.txt:57`. Frequency: [INFERENCE] tied to the decision/startup context, not `on_monthly`; not settled. |
| `income_effect` (IncomeGenerator) | `scripted_effects/IncomeGenerator.txt:287` | — | Calls `gdp_calculation_effect` at `:292`, then `cwic_cg_monthly_master_tick`. Also `income_effect = yes` at `events/tutorial.txt:125` and `decisions/_generic_decisions.txt:1534`. |
| `gdp_calculation_effect` | `scripted_effects/IC_Econ_2024.txt:1308-1480` | — | Main tax engine (see §3). Its own `every_owned_state` loop at `:1378-1379` calls `income_effect_every_owned_scope`. |
| `calculate_national_take_taxes_from_people` | `IC_Econ_2024.txt:2695-2706` (called `:1407`) | — | Sums state taxes into `IncomeTotal`. |

Note: `on_actions/00_on_actions.txt:60` has `#gdp_calculation_effect = yes` commented out (so the monthly tax calc is reached only via `income_effect`, not directly from on_monthly). [INFERENCE] which frequency `ic_pulse` runs at is the main unresolved question for the money pulse (see §6).

### 1.2 Startup and policy setup

- `on_startup_defines.txt:1893, 1902, 1911, 1920, 1927, 1953, 1973` — `startup_tax_loops` per tag (SOV/ENG/FRA/FRE and `every_country` generic). Sets `*_startup_rate`, `economic_freedom_tax_adjustment = economic_x_axis` (`:1956`) and adds `lower_startup_rate` adjustments (`:1972`).
- `startup_tax_loops` (`scripted_effects/policy_focus_effects.txt:297-367`) turns each class's startup rate into a tier idea (`policy_taxrate_corporate_temp_[N]`, `policy_taxrate_temp_[N]` (upper), `policy_taxrate_lower_middle_temp_[N]`, `policy_taxrate_lower_temp_[N]`) and a slider value (`*_tax_slider_gui = rate*8 + 387`).
- `Policy_Startup_Script_2025` (`policy_focus_effects.txt:7959`) calls `gdp_per_capita_categorization` (:8024), then sets army/navy/air/space/strategic/healthcare/welfare/education/services/policing tiers by level (not fully read).
- `give_everyone_base_tax` (`IC_Econ_2024.txt:1504-1515`, labelled "Tax Debug") adds `policy_taxrate_lower_temp_1` to every country. [INFERENCE] debug helper; check whether it is called.

### 1.3 Player-driven entry points

- Finance GUI buttons: `scripted_guis/Finance_Tab.txt:2669, 2679` call `Laffer_Graph_Financial_Tab_Update` (fiscal crisis / borrowing toggles). `Finance_Tab.txt:3068-3100` is `line_graph_laffer_scripted_gui` (plot).
- Policy tier steps: `increase_/decrease_*` effects in `policy_focus_effects.txt`: `lower_healthcare_rate` :2152, `increase_healthcare_rate` :2303, `increase_welfare_rate` :2455, `reduce_welfare_rate` :2607, `increase_service_policy` :2758, `decrease_service_policy` :2910, `increase_cpi_policy` :3062, `decrease_cpi_policy` :3214, `increase_education_rate` :3365, `decrease_education_rate` :3517, `lower_tax_rate` :3673, `increase_tax_rate` :3820, `decrease_corporate_tax_rate` :3965, `increase_corporate_tax_rate` :4112, `decrease_lower_middle_tax_rate` :4257, `increase_lower_middle_tax_rate` :4404, `decrease_lower_tax_rate` :4549, `increase_lower_tax_rate` :4696, `get_actual_tax_rate_effect` :4842 (comment "#Needs Changed?" at :4841). These are invoked from focuses/decisions (not enumerated here).
- Decisions: `decisions/IMF_Decisions.txt:764-815` steps `policy_taxrate_temp_5 → 1` down (IMF bailout rate cut path). National focuses (e.g. `national_focus/GPLA_60s.txt:2954-2961`, `IRAN_1960s.txt:1154-1161`, `TTM_70s.txt:140-147`, `60s_NGA.txt:3605-3627`, `FOR HOTFIX/AUS_50s.txt:1236-1353`) remove `policy_taxrate_temp_1..5` and add one tier. US presidential focuses (`USA_Nixon_1972.txt:357`, `USA_McGovern_1972.txt:459`, `USA_RFK_1972.txt:310`, `USA_Reagen_1972.txt:358`, `USA_Ford_1974.txt:93`, `USA_Agnew_1974.txt:96`, `USA_Albert_1974.txt:87`, `USA_Brown_1976.txt:138`) set tiers 1–3 as completion rewards.

### 1.4 AI participation

- `ic_financial_monthly_pulse` is player-only (`00_on_actions.txt:38-41`). AI countries still run `ic_pulse_monthly` and (via `income_effect`) the tax engine. AI policy changes come only from focus rewards and `StartingPoliciesBogosort.txt:5-8` (`is_ai = yes` and `IncomeCheck < 1` → `starting_policies`). AI strategies read `IncomeCheck` (`ai_strategy/CWIC_building_strategies.txt:70-107`), so AI building decisions track the same tax output.

---

## 2. Data model

### 2.1 Tax-rate modifiers (per country, per class)
- Defined `common/modifier_definitions/influence_modifier_definitions.txt:45-66`: `tax_rate_corporate`, `tax_rate_upper_class`, `tax_rate_middle_class`, `tax_rate_lower_class`. All `value_type = percentage` (`:51-66`).
- Read by: `generate_tax_info` (`policy_focus_effects.txt:370-382`), per-class rate in `IC_Econ_2024.txt:1341-1358`, and tax collection `IC_Econ_2024.txt:2649-2692`.
- Written by: ideas (see §2.3), national focus completion effects, bop files (`bop/DDR.txt:77,97`, `bop/INO.txt:30,55`, `bop/WGR.txt:28,48,73`), dynamic modifiers (`dynamic_modifiers/CWIC_Nepal_Dynamic_Modifiers.txt:14-15`), MNC effects (`ideas/MNC_Effects.txt:257-312`).

### 2.2 Per-country working variables (tax engine)
- `laffer_weighted_average_tax_rate` — unweighted mean of the four class modifiers (`policy_focus_effects.txt:370-382`).
- `effective_tax_rate_factor` — collection-loss factor (set in `:386-415`).
- `effective_tax_rate` — Laffer/collection efficiency output (computed in `IC_tax_avoidance_line.txt:21-28`).
- `actual_tax_rate_adjusted` = weighted × effective (`policy_focus_effects.txt:428-431`), used only by commented-out code in `IC_Econ_2024.txt:1330-1333` and `get_actual_tax_rate_effect` (:4842, untraced).
- `effective_tax_rate_display` = round(weighted × 100 × 2) + 90 (`policy_focus_effects.txt:435-445`) — the x-coordinate of the Laffer graph (see §3.4).
- `pop_{lowerclass,middleclass,upperclass,corporateclass}_tax_rate(_bonus)` (`IC_Econ_2024.txt:1341-1358`): class rate × effective rate, written back into `pop_*_tax_rate`.
- `CWIC_bm_tax_leak_mult` — black-market leak, clamped [0, 0.95] (`policy_focus_effects.txt:397-406`). Writer not traced.
- `modifier_tax_efficiacy` — dynamic modifier mapped to global `economic_modifier_tax_efficiacy` (`dynamic_modifiers/0_dynamic_modifiers.txt:427`); reset to 0 at `IC_Economy_Effects.txt:599`.
- `tax_avoidance_elasticity` — modifier (`common/modifier_definitions/lar_operation_modifiers_pre_definition.txt:103`), mapped from `economic_modifier_tax_avoidance_elasticity` (`0_dynamic_modifiers.txt:428`); ±0.01 steps at `IC_Economy_Effects.txt:54, 99, 135, 174, 221, 263, 296, 332`; reset `:600`.
- Pulse outputs: `total_personal_income_tax`, `total_corporate_tax`, `IncomeTotal`, `IncomeCheck`, `currentMoney`, `ui_income_tax`, `ui_corporate_tax` (`IC_Econ_2024.txt:2697-2703`; `IncomeGenerator.txt:1227-1233, 1913-1919, 1954, 2010, 2027`).

### 2.3 Policy and law idea tiers
- `common/ideas/IC_Laws.txt`: tax-rate tier ideas `policy_taxrate_temp_1..19` (:854-1073+; "Upper Tax Rate" comment at :853). Each tier has `allowed = { always = no # Added via focus }`, `removal_cost = -1`.
- `common/ideas/IC_Laws.txt:153-373`: `tax_rate_lower_class` ladder (law-side modifier, values 0.05→0.95 per earlier pass) with paired stability and agricultural-production entries. `:382-386` `tax_rate_middle_class` (`#5% Income`).
- `common/ideas/IC_Policies.txt`: spending tiers `policy_military_temp_0..19` (:289-520+ visible), and other `*_temp_N` families (not fully read).
- `common/ideas/_economic.txt`: `trade_laws` (:305), social tiers `policy_saga_temp_0..4a` (:412-458), `policy_union_temp_0..7` (:473-556), `policy_media_temp_0..3a` (:575-623). All `removal_cost = -1`.
- `common/ideas/zz_econ_laws.txt`: `war_tension_law_0..4` (:5-80), `lend_lease_law_0..5` (:202-296), `volunteers_law_0..5` (:318-414), `justification_speed_law_0..` (:438+). These are hidden-idea law ladders.

### 2.4 Economic system (economic_x/y/z_axis)
- `economic_x_axis` (per country, 0–28) is the economic-system index. Special types 20–28 map to named systems (`common/map_modes/cwic_map_mode.txt:6506-6599`; 20 Palace Economy, 21–23 Feudalism, 24 Rentier, 25 Petrostate, 26 Colonial, 27 Drug Cartel, 28 War Economy).
- Gates: `decisions/IC_Financial_Decisions.txt:11` (`< 18`), `:42` (`> 17`), `:71` (`= 24`); `decisions/MNC_Decisions.txt` (`economic_x_axis > 10` / `= 10` at :20-22, :55-57, :91-93, ... :339-341); `decisions/CWIC_MNC_Invitations_Toggle.txt:20` (`has_variable = economic_x_axis`); `decisions/categories/00_decision_categories.txt:1225` (`< 9`).
- Startup: `on_startup_defines.txt:1956` sets `economic_freedom_tax_adjustment = economic_x_axis` → `lower_startup_rate` (:1972).
- Economic-system dynamic modifiers: `dynamic_modifiers/0_dynamic_modifiers.txt:391` (`economic_system_modifier`); `dynamic_modifiers/IC_dynamic_modifiers.txt:80` (`bangladesh_economic_system_modifier`, `original_tag = BAN`) and `:100` (`indian_economic_system_modifier`, `original_tag = RAJ`). They map `var_economic_system_*` variables to modifiers (`production_speed_*`, research, agricultural production, food consumption, office-park income, electricity consumption).
- Focus-driven econ steps: `policy_focus_effects.txt:6884` `india_economic_towards_left`, `:6937` `_communism`, `:6989` `_mixed` (sets `var_economic_system_office_park_income_bonus`), `:7011` `_capitalism` (sets `var_economic_system_food_consumption` 0.025).
- `ideas/east_germany_ideas.txt:405` `ddr_idea_new_economic_system`, added as a timed idea by `national_focus/GPLA_60s.txt:2910-2915`.

---

## 3. Formulas (step by step)

### 3.1 Class weighting (`policy_focus_effects.txt:368-383`)
1. `W = modifier@tax_rate_lower_class`
2. `W += modifier@tax_rate_upper_class`; `W += modifier@tax_rate_corporate`; `W += modifier@tax_rate_middle_class`
3. `W = W / 4` — an unweighted mean of the four class rates (corporate counts as one class). [INFERENCE] intentional? No population/GDP weighting is applied.

### 3.2 Collection efficiency (`policy_focus_effects.txt:385-416`)
1. `F = 1 − modifier@modifier_tax_efficiacy` (:387-390).
2. Black-market leak: `CWIC_bm_tax_leak_mult` initialised to 0 if absent; clamped to [0, 0.95] (:397-406). `bm = 1 − leak` (:408-409 via temp var).
3. `F = F × bm` (:408).
4. `F = 1 − F` (:411-415). After steps 1–4, `F = 1 − (1 − m)(1 − leak)` = total loss fraction.
5. `tax_avoidance_function = yes` (:416) — computes `effective_tax_rate` from `W` and `F`.

### 3.3 Laffer/tax-avoidance curve (`common/scripted_effects/IC_tax_avoidance_line.txt`)
1. `laffer_tax_rate = W` (:3).
2. `E = { value = 1, add = F, max = 0 }` (:5-10) — "tax_efficiency_factor".
3. `S = { value = 0.5, add = tax_avoidance_elasticity, min = 1, max = 0 }` (:12-18) — slope.
4. `effective_tax_rate = { value = S, multiply = -1, multiply = W, add = E, max = 0.01, min = 1 }` (:21-28).

Intended form (inferred from the names and the GUI sampler): efficiency `E = 1 − loss`, slope clamped to [0, 1], effective rate `= E − S × W` clamped to [0, 1].

**Defects (see §5, B1–B3):** clamp bounds are inverted or conflicting in steps 2, 3, 4 (`max = 0` with a `min = 1`, and `max = 0.01` with `min = 1`). Whatever the engine's precedence rule, the result is pinned to a bound regardless of inputs [INFERENCE: needs in-game or log test]. The loss sign is also wrong: step 2 *adds* `F` (which already equals the loss) to 1, so leakage raises efficiency (pre-clamp) [INFERENCE: clamp precedence decides whether it is visible].

### 3.4 GUI sampler and graph
- `tax_avoidance_gui_function` (`IC_tax_avoidance_line.txt:31-58`) repeats steps 3.3 with `current_laffer_variable` as the rate, multiplies by 100, rounds, and appends to `laffer_gui_segments` and `effective_tax_rate_gui_info`.
- `gui_numbers_generate_laffer` (`laffer_curve_gui_effects.txt:1-31`) clears arrays, loops `current_laffer_variable` in steps of 0.05 calling `tax_avoidance_gui_function` (:26-28). `laffer_gui_count` is set (:8, :21) and never read in the visible code.
- `Laffer_Graph_Financial_Tab_Update` (`scripted_guis` … `line_graph_scripted_effects.txt:580-625`) calls the sampler (:581) and builds plotting arrays (`Laffer_graph_offsets`, `Laffer_graph_slopes`, `max_laffer`, `min_laffer`).
- It is called every pulse from `generate_tax_info` (`policy_focus_effects.txt:447`) and from two Finance buttons (`Finance_Tab.txt:2669, 2679`).
- Display mismatch: the label `Collection Efficiency: [?effective_tax_rate|0%]` (`Finance_Tab.gui:5047-5051`) shows efficiency, but the plotted marker x uses `effective_tax_rate_display` (`Finance_Tab.txt:3068-3100`), which is the nominal rate × 200 + 90 (`policy_focus_effects.txt:435-445`) — a different quantity with an ad hoc offset [INFERENCE on the graph's coordinate contract].

### 3.5 Per-class collection (`IC_Econ_2024.txt:1328-1358`)
For each class `c` in {lower, middle, upper, corporate}:
- `rate_c = modifier@tax_rate_c`
- `pop_c_tax_rate = rate_c × effective_tax_rate` (`:1341-1358`).

### 3.6 Monthly collection (`IC_Econ_2024.txt:2638-2706`)
Per owned state:
1. Personal taxes: `taken_lower = (lower_gross + substinents_gross) × pop_lowerclass_tax_rate`; `taken_middle = (middle_gross + artisan_gross) × pop_middleclass_tax_rate`; `taken_upper = upper_gross × pop_upperclass_tax_rate` (`:2649-2660`).
2. `state_personal_income_tax = (taken_lower + taken_middle + taken_upper) / 100` (`:2661-2667`).
3. `total_personal_income_tax += state_personal_income_tax` (:2670-2672 comment; actual add at `:2681-2684` region).
4. Corporate: `net_factory_taxed_earnings = max(net_factory_earnings, 0) × pop_corporateclass_tax_rate / 100` (`:2684-2691`) and `total_corporate_tax += ...`.

National (`:2695-2706`):
5. `ui_income_tax = total_personal_income_tax`; `ui_corporate_tax = total_corporate_tax`; `IncomeTotal += total_personal_income_tax + total_corporate_tax`; `IncomeCheck = IncomeTotal`.

Then `IncomeGenerator.txt` (same pulse):
6. `IncomeTotal += custom_income + resource_income + consumer_goods_export_income` (`:1227-1233`), subtract resource cost, custom expenses, insurgency funding, total expenses (`:1913-1954`), subsidy base (`:2006`).
7. `currentMoney += IncomeTotal` (`:2010`); `IncomeCheck = IncomeTotal` (`:2027`).

Scaling: the comments at `IC_Econ_2024.txt:2645-2647` and `:2670-2671` say the total "is scaled once after the loop in gdp_calculation_effect" by /100. The code at `:1406` divides `grossdomesticproduct` by 10, and no `/100` on `IncomeTotal` was found in the grep. [INFERENCE] the comment is stale and the scale is applied only via the per-state `/100` (`:2667`, `:2690`). Needs a check.

---

## 4. Interactions with other subsystems

- **Money**: `currentMoney += IncomeTotal` monthly (`IncomeGenerator.txt:2010`). Policy costs and `total_expenses` (`IncomeGenerator.txt:1954`) are deducted in the same pulse. Debt/loans/IMF: `IMF_Decisions.txt:764-815` edits tier ideas; loans are in `IC_Loans_and_Interest_Rate_Effects.txt` (not read).
- **Production/income**: `IC_Econ_2024.txt:1406-1407` (GDP feeds tax via `grossdomesticproduct`, `net_factory_earnings`); `IncomeGenerator.txt` tourism/resource/consumer income feed `IncomeTotal` (`:453`, `:1227-1233`).
- **Laws/policies**: tier ideas (`policy_taxrate_temp_N`, `policy_*_temp_N`) are the only mechanism that changes class rates at runtime (apart from MNC/bop/dynamic modifiers). Tier ideas also drive non-tax systems: e.g. `scripted_effects/Authoriatian_GUI.txt:999-2008` reads `policy_taxrate_temp_1..5` to adjust `ForiegnInterests`, `LandowningElite`, `CatholicChurch`, `Cartel` (cross-coupling; policy-driven side-effects are hidden in a GUI file).
- **Economic systems**: `economic_x_axis` gates decisions and map colours (§2.4). `economic_freedom_tax_adjustment` links the startup tax to the axis (`on_startup_defines.txt:1956, 1972`).
- **UI/AI**: `Finance_Tab` (Laffer graph, income graphs via `line_graph_scripted_effects.txt:474-478` which keeps 20 points). AI building strategy reads `IncomeCheck` (`CWIC_building_strategies.txt:70-107`). Map mode uses `FROM.IncomeCheck` thresholds (`cwic_map_mode.txt:5437-5571`).

---

## 5. Problems found

Severity: H = wrong results or broken gate; M = misleading/fragile/perf; L = dead or cosmetic.

### 5.1 Bugs

**B1 (H) — Tax avoidance clamps are inverted/conflicting.** `IC_tax_avoidance_line.txt:5-10` (`max = 0` on efficiency), `:12-18` (`min = 1, max = 0` on slope), `:21-28` (`max = 0.01, min = 1` on effective rate); GUI copy `:36-42`. Intended ranges are [0,1]. Result is a pinned constant for all inputs under any precedence rule [INFERENCE]. Verify with `log` of `effective_tax_rate` for a test country.

**B2 (H) — Loss sign inverted in efficiency.** `policy_focus_effects.txt:411-415` builds `F` as the total loss; `IC_tax_avoidance_line.txt:5-10` adds it to 1 (`add = effective_tax_rate_factor`). Intended is `1 − loss`. With `leak > 0` the pre-clamp efficiency rises above 1 [INFERENCE that the clamp then hides it].

**B3 (M) — Double inversion looks unintended.** `policy_focus_effects.txt:386-390` sets `F = 1 − m`; `:408` multiplies by `bm`; `:411-415` inverts again. The comment block at `:393-400` describes `effective_tax_rate *= (1 − leak)` — the implementation does not match that comment. [INFERENCE] fix path: drop the inversion at `:411-415` only if `IC_tax_avoidance_line.txt:5-10` is changed to `subtract`.

**B4 (M) — Tax avoidance computed before the weighted rate it reads.** `IC_Econ_2024.txt:1312` calls `tax_avoidance_function` before `:1313 generate_tax_info`, which is what sets `laffer_weighted_average_tax_rate` (`policy_focus_effects.txt:370-382`). `generate_tax_info` calls `tax_avoidance_function` again at `:416`, so the final value is correct before consumers at `IC_Econ_2024.txt:1341+`. The first call is therefore redundant and reads last month's `W`. Low functional impact; remove the first call.

**B5 (M) — Mis-named tier for upper class.** `startup_tax_loops` uses `policy_taxrate_temp_[N]` for the upper class (`policy_focus_effects.txt:~340-345` block "#Upper"), while lower-middle/lower/corporate use class-named families (`policy_taxrate_lower_middle_temp_`, `policy_taxrate_lower_temp_`, `policy_taxrate_corporate_temp_`). The upper family is also the one `IMF_Decisions.txt:764-815` and focuses and `Authoriatian_GUI.txt` use as a generic "tax rate" index. Confirm this is intended; if not, the class is ambiguous in every reader.

**B6 (M) — Unconditional +50 political power on the "else" tier.** `lower_healthcare_rate` (`policy_focus_effects.txt:2152-~2302`) ends with `else = { add_political_power = 50 }` after the tier chain. Any press at the bottom of the ladder grants PP silently. Check the design intent.

**B7 (M) — Possible scale comment/code mismatch.** See §3.6 scaling note. Stale comments at `IC_Econ_2024.txt:2645-2647, 2670-2671`.

**B8 (L) — `CWIC_bm_tax_leak_mult` default.** `policy_focus_effects.txt:397-398` sets default 0 but never checks it is written by a black-market effect (writer not located). [INFERENCE] dead input unless set elsewhere.

**B9 (L) — Strategic forces clear-all uses the wrong prefix.** `clear_all_strategic_forces_ideas` (`policy_focus_effects.txt:7663-7666`) removes `policy_special_temp_*`, while the family is strategic forces; [INFERENCE] mis-scoped clear (not verified against the strategic ideas file).

**B10 (L) — Typos and naming.** `maxiumum_tax_rate` (`laffer_curve_function.txt:689`), `laffer_skewnewss` (multiple), `laffer_gui_count` set but never read (`laffer_curve_gui_effects.txt:8, 21`).

### 5.2 Dead / duplicate / legacy

**D1 — Old Laffer curve cluster is unreachable.**
- `laffer_curve_function` (`laffer_curve_function.txt:3-589`) is called only from `laffer_curve_test` (`:714-731`, :721-729).
- `laffer_curve_function_mean` (`:590-712`) is called only from `laffer_curve_function` (`:588`).
- `laffer_curve_test` (`:714-731`) has no callers (grep for `laffer_curve_test`: only the definition).
- `laffer_curve_function_for_gui` (`laffer_curve_gui_effects.txt:32-352`) and `laffer_curve_function_mean_for_gui` (`:353-474`) have no callers; `:351` calls the mean.
- Net: ~1,100 dead lines. Replaced by `IC_tax_avoidance_line.txt`. Safe to delete after confirming the grep result (caution: `laffer_curve_test` is in a shipping file; GOTCHAS says verify before deleting).

**D2 — Duplicate tax-tier ideas in two places?** Tier ideas are defined in `IC_Laws.txt:854-1073+` (upper). Other families (`policy_taxrate_lower_temp_`, `policy_taxrate_lower_middle_temp_`, `policy_taxrate_corporate_temp_`) were not located — [INFERENCE] defined elsewhere or missing. Must be checked: `startup_tax_loops` adds them unconditionally (`policy_focus_effects.txt:297-367`), and if undefined the add is a silent no-op.

**D3 — Duplicate effect name.** `decrease_DOM_Dominican_Nationalist_Fervor` appears at `policy_focus_effects.txt:6073` and `:6167`; `Military_Unease`/`decrease_Military_Unease` at `:5474` and `:6269`. Second definition wins in HOI4 [INFERENCE]; delete the duplicate.

**D4 — Test effect in shipping file.** `victory_screen_test_input` (`policy_focus_effects.txt:7493`) sets global flags; test-only.

**D5 — Debug tax helper.** `give_everyone_base_tax` (`IC_Econ_2024.txt:1504-1515`, "Tax Debug") — check callers; likely dead.

**D6 — Commented-out tax code.** `IC_Econ_2024.txt:1330-1333, 1392-1399 (approx), 1439-1475` (pre-2024 net-wage and per-class subtractions). Clean up.

**D7 — Policy-tier ideas with `always = no`.** All tiers in `IC_Laws.txt`, `IC_Policies.txt` use `allowed = { always = no # Added via focus }`. Not a bug; they are applied by effects only. `zzz_generic.txt` `tax_rate_0..7` hidden placeholders (`ideas/zzz_generic.txt:4-130+`) are dead by `always = no` [INFERENCE: unused].

### 5.3 Performance hot spots

**P1 (M) — Laffer GUI sampled for every country every pulse.** `generate_tax_info` (`policy_focus_effects.txt:447`) calls `Laffer_Graph_Financial_Tab_Update`, which runs `gui_numbers_generate_laffer` (~20 sample iterations, each calling the curve with 3–4 modifier lookups; `laffer_curve_gui_effects.txt:1-31`). `gdp_calculation_effect` runs for every country via `income_effect`. [INFERENCE] the sampling and array building run for AI countries that never see the Finance tab. Guard with `is_ai = no` or lazy compute.

**P2 (M) — Per-state loops in the tax path.** `calculate_national_take_taxes_from_people` runs `every_owned_state = { calculate_take_taxes_from_people }` (`IC_Econ_2024.txt:2696`), and `gdp_calculation_effect` runs its own `every_owned_state` (`:1378-1379`). Two state loops per country per pulse. Consolidate if the pulse is per-month.

**P3 (L) — Per-state `calculate_state_hdi`** is called inside `calculate_take_taxes_from_people` (`:2676`), i.e. HDI recomputed per state per pulse, separate from `calculate_national` HDI.

### 5.4 Balance red flags

- **BF1** — Class rates are multiplied by the efficiency (`IC_Econ_2024.txt:1341-1358`), while `effective_tax_rate` depends on the same class rates through `W` (`policy_focus_effects.txt:370-382`). Raising a class rate lowers efficiency and raises the base; the net effect is non-monotone once B1/B2 are fixed. Verify with the graph after the clamp fix.
- **BF2** — `W` weights corporate and each class equally (`policy_focus_effects.txt:370-382`). A 0.05 corporate cut is worth as much as a 0.05 lower-class cut regardless of revenue base.
- **BF3** — `tax_rate_lower_class` ladder runs to 0.95 (`IC_Laws.txt:153-373`) with stability offsets down to −0.13 per step; no cap on combined stacking [INFERENCE: confirm].

### 5.5 AI not participating
- Player-only `ic_financial_monthly_pulse` (`00_on_actions.txt:38-41`); AI does not run the Finance-side logic. AI's tax policy changes only from focus rewards and `StartingPoliciesBogosort.txt:5-8`. AI tier decisions (IMF path) are decisions, not AI-weighted.

### 5.6 error.log
- `error.log` (repo root): grep for `IC_tax_avoidance|laffer|policy_focus_effects|IC_Laws|IC_Policies|IC_Econ_2024|zz_econ_laws|tax_rate|tax_avoidance` returned **no matches**. No recorded errors for this slice in that log.

---

## 6. Open questions / not settled

1. **Frequency of `ic_pulse` / `income_effect`.** Callers are `on_startup_defines.txt:3257`, `_generic_decisions.txt:1471, 1477, 1534`, `tutorial.txt:125`. Need to confirm which is the monthly driver; `on_monthly` does not call `ic_pulse` directly (`00_on_actions.txt:60` commented). [INFERENCE] `_generic_decisions.txt:1476-1477` is a monthly-tick decision.
2. **Engine clamp precedence** for `min`/`max` combined in one value block (B1). Needs a test or log.
3. **Scale of `IncomeTotal`** (§3.6, B7): is there a /100 on IncomeTotal anywhere?
4. **`policy_taxrate_lower_temp_`, `_lower_middle_temp_`, `_corporate_temp_` definitions** — not located in `IC_Laws.txt` / `IC_Policies.txt` (D2).
5. **Class-rate modifier values per tier** (`IC_Laws.txt:854-1073+`) — tier-to-rate mapping not read.
6. **Not read / not located**: `CWIC_Econ_Change_scripted_effects.txt`, `IC_Economic_System_Triggers.txt` (not found by glob under `common/`); `common/decisions/IC_Economic_Investments.txt`; `IC_Industrial_Pulse.txt`; `IC_Economy_Effects.txt` (writers only partly read); `IC_Consumer_Goods.txt`; `IC_Financial_Scripted_Effects_for_Content.txt`; `IC_Economic_Scripted_Effects.txt`; `common/ideas/_economic.txt` beyond :623; `IC_Policies.txt` beyond `military_temp_19`; `policy_focus_effects.txt` :3673–4842 (tax-rate effects), :7507–8302 (2025 refresh/startup/`Remove_ALL_Spendings`), and the swap helpers :1–296.
7. **Ordering check**: whether `IC_Econ_2024.txt:1312` (B4) can ever read a meaningful `W` on the first month.
8. **Black-market leak writer** (`CWIC_bm_tax_leak_mult`) — not found (B8).
9. **Economic-axis writers** (what sets `economic_x_axis` over time) — not traced; the `economic_x_axis` tick is likely in `CWIC_Econ_Change_scripted_effects.txt`, which was not located.
10. **Graph coordinate contract** (§3.4): whether `effective_tax_rate_display` (×200+90) is consumed as intended by `line_graph_laffer_scripted_gui`.

---

## Files (key)
- `common/scripted_effects/IC_tax_avoidance_line.txt:1-58` — live curve + GUI sampler (B1, B2).
- `common/scripted_effects/policy_focus_effects.txt:297-448` — startup tiers, `generate_tax_info` (B3, B5); :2152-2302 `lower_healthcare_rate` (B6); :3673-4842 tax-rate effects (unread detail); :7507-8302 2025 policy machinery (partial).
- `common/scripted_effects/IC_Econ_2024.txt:1308-1480` `gdp_calculation_effect` (B4, §3.5); :1504-1515 `give_everyone_base_tax` (D5); :2638-2706 tax collection (§3.6, B7).
- `common/scripted_effects/IncomeGenerator.txt:287-292, 1227-1233, 1913-1954, 2006-2027` — pulse wiring.
- `common/scripted_effects/IC_scripted_effects.txt:57, 76-82` — `income_effect` and `ic_pulse_monthly`.
- `common/scripted_effects/laffer_curve_function.txt:3-731`, `laffer_curve_gui_effects.txt:1-474` — live GUI sampler (:1-31) and dead cluster (D1).
- `common/scripted_effects/line_graph_scripted_effects.txt:580-625` — graph arrays, called per pulse (P1).
- `common/on_actions/00_on_actions.txt:19-41, 60` — monthly entry points.
- `common/ideas/IC_Laws.txt:153-373, 382-386, 853-1073+` — law ladders and upper-tier ideas.
- `common/ideas/_economic.txt:305-623` — trade law, saga/union/media tiers.
- `common/ideas/zz_econ_laws.txt:5-438+` — war-tension, lend-lease, volunteers, justification laws.
- `common/modifier_definitions/influence_modifier_definitions.txt:45-66` — class tax modifiers.
- `common/dynamic_modifiers/0_dynamic_modifiers.txt:391, 427-428` — economic system and efficiency/elasticity mappings.
- `common/dynamic_modifiers/IC_dynamic_modifiers.txt:80, 100` — BAN/RAJ economic-system modifiers.
- `common/decisions/IMF_Decisions.txt:764-815` — tier stepping.
- `common/decisions/IC_Financial_Decisions.txt:11, 42, 71` — `economic_x_axis` gates.
- `common/decisions/MNC_Decisions.txt:20-341` — `economic_x_axis` gates.
- `common/scripted_guis/Finance_Tab.txt:2669, 2679, 3068-3100`; `Finance_Tab.gui:5047-5051` — UI.
- `on_startup_defines.txt:1893-1973` — startup tiers per tag.
- `common/map_modes/cwic_map_mode.txt:5437-5571, 6506-6599` — map colouring.
- `error.log` (repo root) — no matches for this slice.

## Summary for Main
- The live tax engine is `generate_tax_info` + `IC_tax_avoidance_line.txt` + `IC_Econ_2024.txt` (monthly via `income_effect`); the old Laffer-curve cluster (~1,100 lines) is dead (only test-caller `laffer_curve_test`, which has no caller).
- The live curve appears broken: inverted/conflicting clamps (B1) and a loss-sign error (B2) mean the output is likely pinned, unverified in-game.
- Monthly flow: `income_effect` → `gdp_calculation_effect` → `calculate_national_take_taxes_from_people` → `IncomeTotal` → `currentMoney`. Player-only Finance pulse is separate.
- Biggest unknowns: `ic_pulse` frequency, missing `policy_taxrate_*_temp_` families, and several unread files (§6).
- Verification to run later: log `effective_tax_rate`, `effective_tax_rate_factor` and `IncomeTotal` for one player and one AI country before and after a clamp fix; confirm `ic_pulse` frequency; grep for definitions of `policy_taxrate_lower_temp_`.
