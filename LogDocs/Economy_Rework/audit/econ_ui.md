# CWIC economy audit: UI, AI and health

Repo: `/home/zom/Projects/ColdWarIronCurtain`, mod at `Cold War Iron Curtain/`. Read-only. Citations are `path:line` relative to the mod root unless stated. `[INFERENCE]` marks unverified claims.

## Summary

- **Finance UI** is a scripted GUI (`common/scripted_guis/Finance_Tab.txt`) with a loan window, a fiscal/crisis tab, a debts tab, and slider-style policy levers. Sliders call `policy_focus_effects.txt` effects. Loan math is in `IC_Loans_and_Interest_Rate_Effects.txt`.
- **Graphs** (GDP, Debt, Food, Income, Electricity, Laffer) are rebuilt from history arrays capped at 20. They are updated monthly only for human players (`00_on_actions.txt:63-70`).
- **AI economies**: the core monthly financial pulse (`ic_financial_monthly_pulse`) is gated to `is_ai = no` (`00_on_actions.txt:39-40`). Income and industry pulses are also called from `IC_scripted_effects.txt:57-71` and from decision/startup paths, so AI countries get some economic simulation through other routes. [INFERENCE] Whether AI countries get the full income/industry calculation depends on those other callers. This needs runtime confirmation.
- **Dead or unreachable code**: the `SAMPLE_*` graph effects have no live button (their `add_button` elements are commented out). `scripted_effects/Econ backup/literacy calculations deprecated.txt` and `.disabled` espionage files are not loaded. `zz_unimplemented_placeholder_effects.txt` exists.
- **Log health**: `error.log` has no direct errors from the economy scripts (`IC_Econ*`, `Income_*`, `Laffer`, `Finance`, `Loans`). It does have economy-adjacent issues: unknown modifiers in ideas, one event variable syntax error, and a dynamic-token OOS warning for `Revamped_Trade_Policy`. `game.log` contains IC_AFK debug instrumentation lines (not errors).
- **Duplicate token blocks** in `common/synchronized_dynamic_tokens/tokens.txt` (see Problems).

## 1. Finance tab and other economy GUIs

### 1.1 What the player sees

- Window `countryfinanceview`, visibility gated on `show_finance`, `show_current_employment`, `show_current_overview`, `show_current_fiscal`, `show_current_fiscal_crisis`, `show_current_loans`, `show_current_borrowing`, `show_loan_screen`, `active_insurgency` (`common/scripted_guis/Finance_Tab.txt:153-156`).
- Crisis and Fiscal buttons are shown only with `show_current_fiscal_crisis_button` (`Finance_Tab.txt:316-318`).
- Slider bindings use `*_slider_gui` variables (`Finance_Tab.txt:269-310`).
- Loan window `Loan_Confirmation` (`Finance_Tab.txt:3-148`).

### 1.2 Buttons and what they call

| UI element | Effect | Location |
|---|---|---|
| Fiscal_Button | `Finance_Tab.gui:5241` → window update | `Finance_Tab.gui:5241` |
| Crisis_Button | `Finance_Tab.gui:5249` → `Laffer_Graph_Financial_Tab_Update` (via `Finance_Tab.txt:2669`, `:2679`) | `Finance_Tab.gui:5249` |
| Borrowing_Button | `Borrowing_Button_click` (~`Finance_Tab.txt:2630`) | `Finance_Tab.gui:5257` |
| Debts_Button | `Debts_Button_click` (`Finance_Tab.txt:2681`) | `Finance_Tab.gui:5265` |
| pay_off_loan | `pay_off_loan_click` (`Finance_Tab.txt:2748`) | `Finance_Tab.gui:5542` |
| increase_loan_term | `increase_loan_term_click` (`Finance_Tab.txt:85`) | `Finance_Tab.gui:5704` |
| increase_loan_principal | `increase_loan_principal_click` (`Finance_Tab.txt:97`) | `Finance_Tab.gui:5735` |
| confirm_loan_purchase | `confirm_loan_purchase_click` (`Finance_Tab.txt:46-84`) | `Finance_Tab.gui:5759` |

Shift-click on principal adds 10 (`Finance_Tab.txt:112`).

### 1.3 Loan flow

- Each loan change calls `ROOT = { calculate_loan_details = yes }` (`Finance_Tab.txt` loan click blocks at 46–112).
- `calculate_loan_details` (`common/scripted_effects/IC_Loans_and_Interest_Rate_Effects.txt:1455-1500`): principal `purchase_amount` + interest (`currentInterestRateCalc^current_index / 100` × principal). Monthly length = `purchase_length^current_index × 12`, monthly cost = total / length.
- `loan_set_assigning_borrowable` at `IC_Loans_and_Interest_Rate_Effects.txt:1555` (not re-read in this pass).
- `confirm_loan_purchase_click` writes `currentMoney`, `currentDebt`, and the debt arrays (`Finance_Tab.txt:46-84`), then calls `loan_set_assigning_borrowable`.
- `pay_off_loan_click` (`Finance_Tab.txt:2748`) subtracts `currentDebtTotalsArray^i` from `currentMoney` and `currentDebt`, then removes the array entries.

### 1.4 Borrowing and debts refresh

- `Borrowing_Button_click` resets `Current*MaxBorrowable` from base `*MaxBorrowable` **only when all nine are 0** (`Finance_Tab.txt` ~2630). Other `Current*` values are never reset in this path. [INFERENCE: intended as a first-open initialiser; if a bank's cap is set to 0 legitimately, it is reset again. Check intent.]
- `on_startup`/`tutorial.2000` initialises `Current*MaxBorrowable` from base values (`events/tutorial.txt:36-62`, nine `set_variable` calls) and calls `set_international_commercial_rates`, `set_reserve_rate`, `interest_rate_calc` (`tutorial.txt:30-33`).
- `Debts_Button_click` (`Finance_Tab.txt:2681`) rebuilds `currentDebt*Array` from `debt*Array` where `debtTotalsArray^i > 0`.

### 1.5 Policy sliders

- Slider triggers (`Finance_Tab.txt:1916-2100`) are gated by `*_policy_free_change_enabled` and `*_level_value` bounds 1–20.
- Slider effects (`Finance_Tab.txt:2153-2330`):
  - Healthcare left → `lower_healthcare_rate` (`common/scripted_effects/policy_focus_effects.txt:2152`). This subtracts 8 from `healthcare_slider_gui` (when >63) and 1 from `healthcare_level_value`, then swaps the `policy_healthcare_temp_N` idea chain (`policy_focus_effects.txt:2152-2203`, pattern continues down to `temp_1`).
  - Healthcare right → `increase_healthcare_rate` (`:2303`).
  - Welfare → `reduce_welfare_rate` / `increase_welfare_rate`.
  - Public_Services → `decrease_service_policy` (`:2910`) / `increase_service_policy`.
  - Policing → `decrease_cpi_policy` / `increase_cpi_policy`.
  - Education → `decrease_education_rate` / `increase_education_rate`.
  - Army → `decrease_military_policy` / `increase_military_policy` (`:541`).
  - Navy, Air, Strategic_Forces, Space: similar pattern.
  - Each sets `Recent_*_Funding_Change` flags.
- Tax sliders `Taxes_Slider_Left/Right` (`Finance_Tab.txt:2322-2330`) set `Recent_Tax_Law_Change` (60 days) only. The tax math is in `policy_focus_effects.txt:3673` (`lower_tax_rate`), `:3820` (`increase_tax_rate`), `:4112` (`increase_corporate_tax_rate`). [INFERENCE: the slider effect is wired through the `*_level_value` triggers, not these effects directly. Not confirmed by reading `Finance_Tab.txt:2322-2330` in full.]
- Tax effects are also called from many national focus/decision files (e.g. `common/decisions/US_HOUSE.txt:10402-17556` and `common/national_focus/*.txt`).

### 1.6 Graph refresh and dirty flags

- Monthly updates: `common/on_actions/00_on_actions.txt:63-70` call `GDP_Graph`, `GDP_Debt_Graph`, `Food_Graph`, `Income_Graph`, `Electricity_Graph` updates. Gated on `is_ai = no` and `NOT has_country_flag active_insurgency` (`00_on_actions.txt:63-64`).
- Graph effects are in `common/scripted_effects/line_graph_scripted_effects.txt`:
  - `GDP_Debt_Graph_Financial_Tab_Update` (42–113), `GDP_Graph_Financial_Tab_Update` (153), `Food_Graph_Financial_Tab_Update` (258), `Electricity_Graph_Financial_Tab_Update` (367), `Income_Graph_Financial_Tab_Update` (473–579), `Laffer_Graph_Financial_Tab_Update` (580+).
  - Each Update rebuilds its display arrays from scratch. History arrays are pruned to 20 entries (`Income_Graph` via `while_loop_effect` at roughly line 473+).
  - `Laffer_add_random_point_to_line` has no prune step.
- Dirty flags: `sd_view_dirty` is set at `common/scripted_effects/CWIC_Enviroment.txt:348` and initialised at `on_startup.txt:1583-1584`. `NAT.NATO_gui_dirty` is set at `decisions/IC_Nato_Decisons.txt:25,56,80` and `on_startup_defines.txt:2147`. [INFERENCE: neither is an economy-specific dirty flag; no Finance-tab dirty flag was found.]

### 1.7 Dead sample GUI code

- `interface/line_graph_sample.gui` defines `line_graph_sample_gui`, `line_graph_debt_gui`, `line_graph_income_gui`, `active_crises_scripted_gui`, and `productivty_display_scripted_gui`. The sample GUI binds `GDP_graph_offsets` and `Debt_graph_offsets`, so the visible graphs are the real ones.
- `Finance_Tab.txt:2811-2825` (`line_graph_sample_scripted_gui`) and `:2917` (`line_graph_debt_scripted_gui`) have `add_button_click = { SAMPLE_add_random_point_to_line = yes }`.
- The `add_button` in `interface/line_graph_sample.gui` is commented out at lines 30–34, 94–98, 157–161, 397–401, 456–460. No live `add_button` exists in `Finance_Tab.gui`. The SAMPLE effects are therefore unreachable [INFERENCE: strong, not runtime-confirmed].
- `line_graph_scripted_effects.txt:1-40` (`SAMPLE_add_random_point_to_line`) generates random Y values for demos.
- Parliament sample files are similar demo code: `parliament_sample_scripted_effects.txt:845` (`SAMPLE_generate_random_party_seats`), `parliament_sample_scripted_gui.txt:92-93` (`refresh_button_click` → `SAMPLE_init_parliament`), `parliament_sample_scripted_loc.txt`, `parliament_sample_localisation_l_english.yml`. [INFERENCE: dead.]

### 1.8 Loc, icons and text

- `economy_gui_localisation.txt`: one `defined_text` `income_pie_tip`, USA-only trigger. Its `localisation_key` is a raw English string, not a loc key.
- `IC_Economy_scripted_localisation.txt` (1182 lines; 1–300 read): Productivity getters, `GetEconSystem*ClassName` branch on `economic_x_axis`, and `GetProductivityModifier` uses `"productivity_details_[?productivity_i]"`. `[?var]` syntax inside a quoted key is a risk (see GOTCHAS on `[TAG.?var]` being malformed). [INFERENCE: not confirmed as a bug.]
- `IC_Econ2_Loc.txt` and `CWIC_Econ_gfx_scripted_loc.txt`: `GetEconomy_icon`, `GetEconomyTypeDesc2`, keyed by `economic_x_axis`/`y`/`z`.
- `Financial_Tab_l_english.yml` was not read in this pass. [INFERENCE: loc coverage of `ECON_SYSTEM_*_TT`, `PAY_OFF_THIS_LOAN_TT`, `SHIFT_CLICK_ADD_TT` is unverified.]

## 2. AI economic behaviour

### 2.1 Monthly pulses

- `common/on_actions/00_on_actions.txt:37-40`: `ic_financial_monthly_pulse = yes` is gated on `is_ai = no`. This is the core financial pulse.
- `IC_scripted_effects.txt:1-74` (`ic_financial_monthly_pulse`): the `else` branch runs export-shortage cuts, consumer-goods cuts, class-pop resets, `income_effect` (line 57), `industrial_pulse` (line 69), `monthly_borrowing_and_interest_pulse` (line 71).
- `IC_scripted_effects.txt:76-` (`ic_pulse_monthly`): `federation_calculator`, `monthly_power_projection_gain`, `monthly_set_fpp`, `monthly_infamy_calc`, `add_nhan_van_minigame_to_ui`. No economic pulse here.
- `00_on_actions.txt` `on_monthly_VTC` (block at lines 1–23): `every_country` runs `ic_pulse_monthly`. So the non-economy monthly calcs run for all countries.

### 2.2 Other AI-reachable economy paths

- `common/decisions/_generic_decisions.txt:1470-1477`: `ROOT = { ic_pulse = yes }` and `every_country = { ic_pulse = yes }`.
- `_generic_decisions.txt:1533-1534`: `every_country = { income_effect = yes }`.
- `_generic_decisions.txt:1560-1561`: `industrial_pulse = yes` in a `hidden_effect`.
- `on_startup_defines.txt:3223-3257`: `every_country` runs `industrial_pulse`, then `ic_pulse_monthly` and `ic_pulse`. [INFERENCE: this is in a startup/defines block, not a monthly loop. Check the surrounding context.]
- The `_generic_decisions.txt` callers run on decisions. Whether they are `is_ai`-gated depends on the decision's `available`/`ai_will_do`. [INFERENCE: not checked.]
- Insurgency path: `CWIC_Insurgency_Economy_Effects.txt:40-41, 58-59` and `MLA_scripted_effects.txt:390-391` and `Indochina_Theater_Effects.txt:3491-3492` also run `industrial_pulse`.

### 2.3 Income and tax calc (every_owned_state)

- `common/scripted_effects/IC_Econ_2024.txt:1376-1380`: `CWIC_econ_drift_vars`, then `every_owned_state` → `income_effect_every_owned_scope` and `get_total_infrastructure`.
- `IC_Econ_2024.txt:1504-1507` (`give_everyone_base_tax`): `every_country` adds tax policy ideas.
- `IC_Econ_2024.txt:1521-1525`: `every_owned_state` accumulates average development, factory totals, nuclear reactors.
- `IC_Econ_2024.txt:2665-2669`: `every_owned_state` accumulates `total_personal_income_tax`. A code comment at line 2668 notes that a divide-by-10 inside the per-state loop was removed on 2026-07-05.
- `IC_Econ_2024.txt:2695-2699` (`calculate_national_take_taxes_from_people`): `every_owned_state` then copies totals into `ui_income_tax`, `ui_corporate_tax`, `ui_wage_mass`.
- `IC_Industrial_Pulse.txt:623-625`: `every_owned_state` pollution calc.

### 2.4 AI-specific bugs: `ai_will_do`

- `common/decisions/` `ai_will_do` on economic decisions is widespread. Examples:
  - `CWIC_Capital_Controls.txt:19-575`: uses `currentMoney`, `CWIC_inflation_mom`, `CWIC_fx_reserves`, `grossdomesticproduct` modifiers (`:311-575`).
  - `CWIC_MNC_Targeted_Nationalization.txt` (27–542): `factor = 0.01` with modifiers.
  - `CWIC_MNC_Invitations_Toggle.txt:29,51`: `factor = 0`.
  - `FIN_1990s.txt:17-299`: fixed `factor` values 2–20.
- GOTCHAS trap: `ai_national_focuses` ignores `ai_will_do`. AI-only limits belong in `available` behind `is_ai = no`. [INFERENCE: these `ai_will_do` decisions are not focuses, so the trap does not apply directly; a check was not run on each file.]
- `Ai_will_do` on `_generic_decisions` economic decisions was not audited in this pass.

### 2.5 Are AI economies simulated?

- **Partly**. The per-state income and tax loops (`IC_Econ_2024.txt:1378, 2696`) run `every_owned_state` in whatever scope calls them. The core financial pulse (`ic_financial_monthly_pulse`) is player-only (`00_on_actions.txt:39-40`). `industrial_pulse` and `income_effect` run for AI in some decision/startup paths (see 2.2).
- [INFERENCE] AI countries therefore receive state-level production and tax updates but do not run the monthly borrowing/interest pulse (`IC_scripted_effects.txt:71`) or the export-shortage cuts (`IC_scripted_effects.txt:8-54`). This is an inference from the gates and needs runtime confirmation.

## 3. Health

### 3.1 error.log (economy-related)

- `error.log:5565-5573`: `Unknown modifier: factory_output` and `electronics_tech_research` in `common/ideas/CWIC_1990s_expansion.txt` (lines 9, 18, 27, 77, 86, 132, 218, 233, 326). `factory_output` is an economy modifier, so this is economy-relevant.
- `error.log:5575-5576`: `Unknown modifier: subversion_defense_factor` in `common/ideas/Russia.txt` (57, 67).
- `error.log:5574`: duplicate idea `KOR_us_restrictions_on_republic_of_koreas_armed_forces`.
- `error.log:5736-5737`: focus `KOR_50s_build_docks_and_roads` (`KOR_50s_Economy.txt:321`) references nonexistent `KOR_50s_infrastructure_reorganisation_plan`.
- `error.log:5924-5925`: `Token Revamped_Trade_Policy is a dynamic token...` OOS warning (twice). See 3.3.
- `error.log:6095`: `invalid variable syntax: "HUN_KADAR_ECON.22.a"` (`events/` file, economy-themed event). [INFERENCE: the variable name uses a dot-separated event-ID form, not a scoped variable.]
- Not economy, but a large cluster: `error.log:5550-5553` `Invalid effect 'capture_ciphers'` in `common/operations/CWIC_cold_war_operations.txt:591, 1111`. `error.log:5556` unknown effect `SIA_plant_indochina_port_charges` (`common/operations/SIA_operations.txt:51`).
- No errors matching `IC_Econ`, `Income_`, `Laffer`, `Finance`, `Loans`, `divide`, or `GDP` were found in the grep. [INFERENCE: the grep returned only the 20 most recent matches per pattern set. The narrow grep returned matches only for the entries above.]

### 3.2 game.log

- `game.log:13-38`: IC_AFK debug entries (`passive_production_observer`, `VIN_PULSE`, `VIN_ACCRUAL`, `PLACEMENT`, `SCORE_WRITE/DELTA`, `LEVERAGE_WRITE`). These are instrumentation, not errors. [INFERENCE: debug logging left enabled in the shipped build. Check whether this is intended.]
- No economy-specific errors in the first matches.

### 3.3 synchronized_dynamic_tokens/tokens.txt

- File lists economy tokens (regex-matched lines, `tokens.txt:78-1299`): `tax_increase`, `tax_cuts`, `economic_growth`, `war_taxes`, `crackdown_on_tax_fraud`, `economic_liberalization`, `increased_tax_revenue`, `pension_tax`, `health_tax_credits`, `grow_economy`, `FRA_Reconstruction`, `tax_rate_lower_class`, `tax_rate_middle_class`, `tax_rate_upper_class`, `tax_rate_corporate`, `productivity_factor`, `*_income_bonus`, `modifier_tax_efficiacy`, `tax_avoidance_elasticity`, `dockyard_income_bonus`, `Revamped_Trade_Policy` (line 1299).
- **Duplicate blocks**: `productivity_factor` at 808 and 1155; `*_income_bonus` (industrial_park, military_factory, office_park, foundry_district, metallurgy_plant, food, other_resources) at 809–815 and 1139/1156–1161; `tax_rate_lower_class/middle/upper/corporate` at 816–819 and 1103–1106; `modifier_tax_efficiacy` at 938 and 1107. Duplicated tokens are a maintenance hazard [INFERENCE: harmless if the engine de-duplicates; unverified].
- **Relevance**: `error.log:5923-5925` reports that `Revamped_Trade_Policy` is a dynamic token and needs to be a synchronized token. It is listed at `tokens.txt:1299`, so the warning suggests the token is used in a form the sync list does not match. [INFERENCE: check how `Revamped_Trade_Policy` is referenced, e.g. `@token:` vs. literal.] `attack_wasteful_military_spending` also triggers the same warning at `error.log:5923`, and it is not listed in the regex hits, so it is missing from the sync list.

### 3.4 Dead and legacy files

- `common/scripted_effects/Econ backup/literacy calculations deprecated.txt`: exists (glob). [INFERENCE: not loaded, since the engine loads only the root of `scripted_effects/`; confirm that the engine does not scan subfolders for effects. Contents not read.]
- `common/scripted_effects/zz_unimplemented_placeholder_effects.txt`: placeholder effect file. Not read in this pass.
- `common/scripted_effects/IC_Espionage_*.txt.disabled` (4 files) and `Espionage_*.txt.disabled` (2 files): disabled, not loaded.
- `common/scripted_effects/IC_Econ_2024.txt`, `IC_Industrial_Pulse.txt`, `CWIC_Insurgency_Economy_Effects.txt`: active (referenced above).
- `OUTDATED_PRC_50s_Rework.txt` (national_focus): known outdated file from an earlier pass.
- `scratch/*.py`: many throwaway scripts at repo root `scratch/`. These are cleanup candidates, not economy code.
- `events/tutorial.txt:1-63`: `tutorial.2000` "Initialized Scripted GUI Optimization and Financial System Setup". Sets `ic_pulse_check`, runs `set_international_commercial_rates`, `set_reserve_rate`, `interest_rate_calc`, and copies base `*MaxBorrowable` into `Current*MaxBorrowable` for nine banks. The rest of the file (`tutorial.txt:64-725`) was not read in this pass.

## 4. Problems found

| # | Severity | Location | Problem |
|---|---|---|---|
| 1 | High (AI) | `00_on_actions.txt:39-40`; `IC_scripted_effects.txt:71` | Monthly borrowing and interest pulse runs only for human players. AI debt and interest do not update [INFERENCE: runtime impact unverified]. |
| 2 | Medium (dead code) | `Finance_Tab.txt:2811-2825, 2917`; `interface/line_graph_sample.gui:30-34, 94-98, 157-161, 397-401, 456-460` | SAMPLE graph effects are unreachable. Remove or gate. |
| 3 | Medium (dead code) | `scripted_effects/Econ backup/literacy calculations deprecated.txt`; `parliament_sample_*` | Deprecated and sample files. Remove. |
| 4 | Medium (math) | `line_graph_scripted_effects.txt` (Income/GDP/Food/Electricity normalisation) | Normalisation divides by `max - min`. A flat or one-point history gives divide-by-zero [INFERENCE: runtime effect unverified; no divide error seen in `error.log`]. |
| 5 | Medium (mislabel) | `line_graph_scripted_effects.txt:369` | The "Electricity" graph stores `resource@coal`, not electricity. |
| 6 | Low (logic) | `Finance_Tab.txt` ~2630 (`Borrowing_Button_click`) | Resets `Current*MaxBorrowable` only when all nine are 0. Other values are never reset here. Intent unclear. |
| 7 | Low (logic) | `Laffer_add_random_point_to_line` | No prune step; the others prune at 20. Unbounded growth if called. (Only reachable via SAMPLE, so dead in practice.) |
| 8 | Medium (errors) | `error.log:5565-5573` (`CWIC_1990s_expansion.txt`) | `factory_output` and `electronics_tech_research` are unknown modifiers. Economy modifiers silently do nothing. |
| 9 | Medium (errors) | `error.log:5575-5576` (`Russia.txt` 57, 67) | `subversion_defense_factor` unknown. |
| 10 | Low (errors) | `error.log:5736-5737` (`KOR_50s_Economy.txt:321`) | Focus references a nonexistent `KOR_50s_infrastructure_reorganisation_plan`. |
| 11 | Low (errors) | `error.log:6095` | Invalid variable syntax `HUN_KADAR_ECON.22.a`. |
| 12 | Medium (OOS) | `error.log:5923-5925`; `tokens.txt:1299` | `Revamped_Trade_Policy` and `attack_wasteful_military_spending` are dynamic tokens. OOS risk in multiplayer. |
| 13 | Low (maintenance) | `tokens.txt:808-819` vs `1103-1161`; `938` vs `1107` | Duplicate token blocks. |
| 14 | Low (debug) | `game.log:13-38` | IC_AFK debug logging appears enabled [INFERENCE: check whether it is gated]. |
| 15 | Low (balance) | `policy_focus_effects.txt:2152-2203` | Healthcare lever is an 8-point step on a 1–20 level with idea chain swapping. Not evaluated for balance [INFERENCE]. |
| 16 | Low (GOTCHAS) | `IC_Economy_scripted_localisation.txt` (`GetProductivityModifier`) | Quoted `"productivity_details_[?productivity_i]"` key. Check the loc syntax against the GOTCHAS `[?SCOPE.var|fmt]` rule. |
| 17 | Medium (perf) | `IC_Econ_2024.txt:1378, 1522, 2666, 2696` | Multiple `every_owned_state` loops per cycle (income, development, factory totals, personal income tax, take-taxes). Each runs per monthly pulse for each affected country. Consolidate into one state loop [INFERENCE: cost not measured]. |
| 18 | Low (state) | `IC_Econ_2024.txt:2666-2669` | A comment documents a removed divide-by-10 bug. Historical note, not a live bug. |

## 5. Architecture

- **Entry points**: monthly `on_actions` (`00_on_actions.txt:37-70`), `on_monthly_VTC` (`00_on_actions.txt` lines 1–23), `on_startup_defines.txt:3223-3257`, decisions (`_generic_decisions.txt:1470-1561`), and GUI buttons (`Finance_Tab.txt` and `Finance_Tab.gui`).
- **Flow**: GUI sliders → `policy_focus_effects.txt` effects → idea swaps and `*_level_value` changes → `IC_Econ_2024.txt` state loops → totals (`total_personal_income_tax`, `total_corporate_tax`, `total_employed_pay_national`) → UI copies (`ui_income_tax`, `ui_corporate_tax`, `ui_wage_mass`) (`IC_Econ_2024.txt:2695-2699`).
- **Loans**: GUI → `calculate_loan_details` / `loan_set_assigning_borrowable` (`IC_Loans_and_Interest_Rate_Effects.txt:1455, 1555`) → `currentMoney`/`currentDebt` → monthly `monthly_borrowing_and_interest_pulse` (player only).
- **Graphs**: monthly on_action (player only) → `*_Graph_Financial_Tab_Update` → arrays rebuilt, normalised, capped at 20.

## 6. Open questions

1. Does the `_generic_decisions.txt:1470-1561` ic_pulse/income_effect path run for AI, and is it `is_ai`-gated in the decision's `available`/`ai_will_do`?
2. Does AI debt, interest, and export-shortage logic run anywhere else? (Not confirmed.)
3. Does `Revamped_Trade_Policy` get referenced in a form that needs a synchronized-token entry, and why is `attack_wasteful_military_spending` missing from the sync list?
4. Is `Econ backup/` loaded by the engine? (Expected not.)
5. Is the IC_AFK debug logging in `game.log` gated or always on?
6. Does `Financial_Tab_l_english.yml` cover every `ECON_SYSTEM_*_TT`, `PAY_OFF_THIS_LOAN_TT`, `SHIFT_CLICK_ADD_TT` key? (Not read.)
7. Is the `Borrowing_Button_click` reset-on-all-zero behaviour intended? (`Finance_Tab.txt` ~2630.)
8. Are the normalisation divisions in `line_graph_scripted_effects.txt` ever reached with `max == min`?
9. Tax slider wiring: `Finance_Tab.txt:2322-2330` sets `Recent_Tax_Law_Change` only. Which effect actually moves `upper_tax_level_value`?
