# CWIC economy laws/policies audit (PARTIAL, read-only)

Status: this is a partial audit. Sections marked **NOT DONE** were not reached within this run and need a follow-up pass. Everything below is either read directly (file:line given) or marked [INFERENCE].

Mod root: `Cold War Iron Curtain/` (repo root `/home/zom/Projects/ColdWarIronCurtain`).

## 1. Entry points

| Entry | Callers | Frequency | Player vs AI |
|---|---|---|---|
| `ic_financial_monthly_pulse` (`common/scripted_effects/IC_scripted_effects.txt:2`) | `common/on_actions/00_on_actions.txt:39-40` | monthly | **Player only** (`limit = { is_ai = no }`, 00_on_actions.txt:39). AI path is unclear, see §6. |
| `income_effect` (`IncomeGenerator.txt:287`) | `IC_scripted_effects.txt:57` (pulse); `_generic_decisions.txt:1531-1534` (`every_country = { income_effect = yes }` inside a decision `complete_effect`; the adjacent comment says the pulse was "Retired … now runs from on_monthly") | monthly / per decision | Both via the decision path [INFERENCE: need the surrounding decision's `is_ai` gate] |
| `income_effect_every_owned_scope` (`IncomeGenerator.txt:1`) | `IC_Econ_2024.txt:1378-1379` (every_owned_state) | monthly | Both |
| `tax_avoidance_function` / `generate_tax_info` | `IC_Econ_2024.txt:1312-1313`; `IC_tax_avoidance_line.txt:1` | per economy recalc | Both |
| `policy_focus_effects` family (`increase_/decrease_/lower_/…_tax_rate`, `*_policy`, `swap_*_ideas`, `refresh_*_policy_rate`) | ~148 focus/decision files (e.g. `national_focus/50s_TUR.txt:2562`, `60s_FIN.txt:18`, `_generic_decisions.txt:4274-4275`, `US_HOUSE.txt:10402`, `US_HOUSE.txt:11104-11106`) | on focus completion, event, or decision | Mostly AI and player alike via focus completion_reward |
| Startup tax/policy setup (`startup_tax_loops` l.297, `Policy_Startup_Script_2025` l.7959, `IC_Econ_2024.txt:1506-1510`) | IC_Econ_2024 l.1506-1510 (adds tier 1 for all four tax families); `StartingPoliciesBogosort.txt` l.41-69 (AI-only start-tier logic) | game start / reset | Both |

Not measured: the exact count per callsite. Grep caps results, so per-effect frequency is [INFERENCE] from file count.

## 2. Data model

### 2.1 Tax tier ideas (`common/ideas/IC_Laws.txt`)
Four families, each with tiers 1..19, and each tier declared `allowed = { always = no # Added via focus }` (checked on the lower and corporate families, l.147-374 and l.624-852). Tier selection is therefore never player-selected via law UI. It happens only via `add_ideas`/`remove_ideas` in effects.

| Family | Lines | Modifier driving the tax rate |
|---|---|---|
| `policy_taxrate_lower_temp_N` | l.147-374 | `tax_rate_lower_class` = 0.05·N |
| `policy_taxrate_lower_middle_temp_N` | l.376-622 | `tax_rate_middle_class` = 0.05·N |
| `policy_taxrate_corporate_temp_N` | l.624-852 | `tax_rate_corporate` = 0.05·N |
| `policy_taxrate_temp_N` | l.854-1081 | `tax_rate_upper_class` = 0.05·N |

(The "lower middle" family drives `tax_rate_middle_class`. Naming is inverted relative to the tier name. [INFERENCE] intentional, but worth noting.)

Side-effect modifiers per tier (sample values read):

| Family | Key | Tier 1 | Tier 2 | Tier 19 | Lines |
|---|---|---|---|---|---|
| lower | `stability_factor` | 0.05 | 0.04 | -0.13 (tier 19 per summary) | l.147-373 |
| lower | `agricultural_complex_production_bonus` | 0.1 | 0.075 | -0.35 | l.147-373 |
| lower_middle | `war_stability_factor` | 0.15 | 0.10 | -0.75 | l.376-622 |
| lower_middle | `cic_construction_boost_factor` | 0.10 | 0.08 | -0.26 | l.376-622 |
| corporate | `war_support_factor` | 0.10 | 0.08 | not read | l.624-852 |
| corporate | `political_power_gain` | 0.10 | 0.08 | not read | l.624-852 |
| upper | `office_park_income_bonus` | 0.4 | 0.35 | -0.5 | l.854-1081 |
| upper | `production_speed_office_park_factor` | -0.25 | -0.2 | 0.65 | l.854-1081 |

Tiers 4–18 of the corporate and upper families were not fully read. The lower and lower-middle values above come from grep output and summary notes, so treat intermediate tiers as [INFERENCE] until verified.

Tier-step effects `lower_tax_rate` (`policy_focus_effects.txt:3673`) and `increase_*` / `decrease_*` (l.3820, 3965, 4112, 4257, 4404, 4549, 4696) step the tier by `add_ideas` of tier N-1 and `remove_ideas` of tier N. `startup_tax_loops` (l.297-366) sets the start tier from `*_startup_rate × 8`, then uses `meta_effect` text to pick the idea name.

### 2.2 Variables
- `laffer_weighted_average_tax_rate` (policy_focus_effects.txt:370-382): average of the four `modifier@tax_rate_*` values, then /4.
- `effective_tax_rate_factor`, `effective_tax_rate` (l.384-419).
- `CWIC_bm_tax_leak_mult` (black market leakage, clamped 0..0.95, l.393-399).
- `actual_tax_rate_adjusted` = laffer × effective_tax_rate (l.404-407); `effective_tax_rate_display` (l.409-415).
- Per-class: `pop_lowerclass_tax_rate`, `pop_middleclass_tax_rate`, `pop_upperclass_tax_rate`, `pop_corporateclass_tax_rate` and `*_bonus` (IC_Econ_2024.txt:1341-1358).
- GUI/state: `lower_tax_level_value`, `lower_tax_slider_gui`, `upper_tax_level_value`, `upper_tax_slider_gui`, `upper_class_tax_rate`, `corporate_tax_slider_gui`, `lower_middle_tax_slider_gui` (l.299-365; decrement at l.3673-3690).

### 2.3 Writers and readers
- Writers: `startup_tax_loops` (l.297); `lower_tax_rate` and the other step effects; `generate_tax_info` (l.368) writes `laffer_weighted_average_tax_rate` and `effective_tax_rate_factor`; IMF effects (`IMF_effects.txt:475-500`) and `IMF_Decisions.txt:790-815` also step the upper tier directly.
- Readers: `IC_Econ_2024.txt:1341-1358` (pop tax rates), `IC_tax_avoidance_line.txt`, `Laffer_Graph_Financial_Tab_Update`.

## 3. Formulas (file:line)

1. Laffer average (policy_focus_effects.txt:370-382): `laffer_avg = (modifier@tax_rate_lower_class + modifier@tax_rate_upper_class + modifier@tax_rate_corporate + modifier@tax_rate_middle_class) / 4`.
2. Efficiency (l.384-386): `effective_tax_rate_factor = 1 - modifier@modifier_tax_efficiacy`. Note the key is spelled `modifier_tax_efficiacy` (typo). It must match the definition exactly. Not yet verified against `modifier_definitions`.
3. Black-market leak (l.391-404): `bm_collect = 1 - CWIC_bm_tax_leak_mult`; `factor = 1 - (factor × bm_collect)`. The leak compounds with efficiency: `final = 1 - (1 - eff)(1 - leak)` [INFERENCE from the sequence].
4. Actual rate (l.404-407): `actual_tax_rate_adjusted = laffer × effective_tax_rate`.
5. Per-class pop rate (IC_Econ_2024.txt:1341-1358): `pop_X_tax_rate = modifier@tax_rate_X × effective_tax_rate`.

## 4. Money pulse interactions

Chain (verified):
1. Monthly, player only: `00_on_actions.txt:39-40` → `ic_financial_monthly_pulse` (`IC_scripted_effects.txt:2`).
2. If `active_insurgency` flag set: `cwic_insurgency_monthly_pulse`; else the delivery-cut checks and then `income_effect = yes` (`IC_scripted_effects.txt:57`).
3. `income_effect` (`IncomeGenerator.txt:287`) → `cwic_process_war_reparations`, resets `trade_infrastructure_total`, then the per-state work.
4. Income accumulated in `IncomeTotal` and added to `currentMoney` (`IncomeGenerator.txt:2009-2010`).
5. Deficit handling (`IncomeGenerator.txt:2012-2020`): if `currentMoney < 0`, `pulse_deficit = -currentMoney`; debt repayment via `debtPaymentArray^i` (l.2047-2085); austerity/default check at l.2208-2209.
6. Tax contribution: `pop_*_tax_rate` (IC_Econ_2024.txt:1341-1358) drives per-class income. Whether `income_effect` reads these `pop_*` values was **not verified** (grep for `pop_.*tax_rate` in `IncomeGenerator.txt` returned nothing directly; see open question Q2).

Player choice to money flow, as traced:
- Tax tier (player via focus/decision) → `add_ideas` tier idea → `modifier@tax_rate_*` → `laffer_weighted_average_tax_rate` and per-class `pop_*_tax_rate` → `income_effect` (partially verified) → `IncomeTotal` → `currentMoney`.
- Spending policies (`*_policy_temp_N`, `*_spending_modifier` in IC_Policies) affect the spend side. The spend-side pathway was **not traced** (NOT DONE).

## 5. Problems

| Sev | Location | Issue |
|---|---|---|
| Medium (bug candidate) | `policy_focus_effects.txt:3960`-ish `decrease_DOM_Dominican_Nationalist_Fervor` at **l.6073 and l.6167** | Two effects share the same name. The second (l.6167) checks `has_idea = DOM_Dominican_Nationalist_Fervor0` in its limit, which looks like a copy-paste of the increase effect. The duplicate-name behaviour in HOI4 is [INFERENCE]: the later definition may override the earlier one. |
| Low | `policy_focus_effects.txt:5224` `decrease_minority_rigts` | Typo in name. Callers not verified. Possibly `decrease_minorities_policy` (l.6571) is the intended one. |
| Medium (desync risk) | `policy_focus_effects.txt:3673-3690` `lower_tax_rate` | On first step (NOT has `policy_taxrate_temp_1`) it writes `upper_tax_slider_gui`, `upper_tax_level_value`, and `upper_class_tax_rate` (-0.05) in addition to the idea swap. Two representations of the same tier (tier idea and `upper_class_tax_rate`) can disagree. |
| Low | `IC_Econ_2024.txt:1330-1340` | Commented-out lines and a duplicate `# after generate_tax_info` comment. Cosmetic. |
| Low | `IC_Laws.txt` `policy_taxrate_lower_middle_temp_*` | Commented `#weekly_casualties_war_support` dead lines. Cosmetic. |
| Low | `IC_Laws.txt` `policy_taxrate_lower_middle_temp_*` | Name/modifier mismatch: "lower_middle" tier drives `tax_rate_middle_class`. Documentation issue. |
| Low | `generate_tax_info` `modifier_tax_efficiacy` | Misspelled key. Verify against definition. |
| Low | `policy_focus_effects.txt:297-365` `startup_tax_loops` | Magic constants (`* 8`, `+ 387`) for slider GUI with no explanation. |
| Low | `policy_focus_effects.txt:6167-6170` | See duplicate above. |
| Balance (unverified) | corporate/upper tiers 4–18 | Not verified. Possible imbalance between `office_park_income_bonus` sign flip at tier 15/16 and `production_speed_office_park_factor`. |
| AI gap (likely) | `00_on_actions.txt:39` `is_ai = no` | The monthly pulse is player-only. AI reaches `income_effect` only through the decision in `_generic_decisions.txt:1527-1537`. Need to confirm that decision is AI-reachable; otherwise AI income is not pulsed. [INFERENCE] |
| Perf (unverified) | `IncomeGenerator.txt` `every_country`/`every_owned_state` | `income_effect` runs per-country and per-state inside a loop; not measured. |

## 6. Open questions / NOT DONE

- **Q1 (NOT DONE)**: Full enumeration of modifier keys in `IC_Laws.txt` l.624–1081 (corporate tail, upper block), `IC_Policies.txt` (cooldown ideas, `policy_military/navy/air/special_temp_N`), `_economic.txt`, `zz_econ_laws.txt`, and `zzz_generic.txt`.
- **Q2 (NOT DONE)**: Where `income_effect` reads `pop_*_tax_rate`. Check `IncomeGenerator.txt` around the per-class section (before l.2002) for `pop_`.
- **Q3 (NOT DONE)**: Read `common/scripted_effects/policy_focus_effects.txt` effect bodies for `increase_/decrease_` (l.541–6837) and the `*_policy` families in detail.
- **Q4 (NOT DONE)**: `CWIC_Econ_Change_scripted_effects.txt` (path not confirmed by glob; locate with grep).
- **Q5 (NOT DONE)**: `scripted_triggers/IC_Economic_System_Triggers.txt` (path not confirmed).
- **Q6 (NOT DONE)**: `common/dynamic_modifiers/IC_dynamic_modifiers.txt` (glob only listed `0_dynamic_modifiers.txt`; the economic_x_axis entries may live elsewhere).
- **Q7 (NOT DONE)**: `decisions/IC_Economic_Investments.txt` (~1.6k lines): categories, costs, effects, `ai_will_do`.
- **Q8 (NOT DONE)**: Verify every modifier key (`tax_rate_*`, `modifier_tax_efficiacy`, `stability_factor`, `war_stability_factor`, `office_park_income_bonus`, `production_speed_office_park_factor`, `agricultural_complex_production_bonus`, `cic_construction_boost_factor`, `war_support_factor`, `political_power_gain`, `production_factory_max_efficiency_factor`, `industrial_capacity_factory`, `industrial_capacity_dockyard`, `production_speed_buildings_factor`, `*_spending_modifier`, `conscription`) against `common/modifier_definitions/` and vanilla HOI4. Not yet done.
- **Q9**: Confirm whether the AI reaches the monthly pulse through `_generic_decisions.txt:1527-1537`.
- **Q10**: Verify `clear_all_*_ideas` removal lists (`policy_space_temp_*`, `policy_healthcare_temp_*`, etc.) match ideas that actually exist. Those families were not found in IC_Policies (military/navy/air/special are the only ones confirmed).

## 7. Summary of what was verified vs. not

Verified by direct read: `GOTCHAS.md`; the IC_Laws tax family structure and the lower/lower-middle/upper sample values; `policy_focus_effects.txt` effect map (lines in §1 and below); the tax-computation chain in policy_focus_effects.txt l.297–453 and IC_Econ_2024.txt l.1312–1358; the money-pulse chain in IC_scripted_effects.txt l.2–57 and IncomeGenerator.txt l.287–2010.

Not verified: modifier-key existence (Q8), the corporate/upper intermediate tiers, IC_Policies / _economic / zz_econ_laws modifier values, the four files listed in Q4–Q7, and the AI-pulse path (Q9).
