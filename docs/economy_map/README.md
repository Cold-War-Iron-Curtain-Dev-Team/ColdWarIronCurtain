# CWIC economy dependency map (2026-11-02)

This is a static map of everything outside the economy core that touches it. It is
input for planning the simplification and the fixes; it makes no design decisions.

Files in this folder:

- `README.md`: this summary.
- `external_references.csv`: one row per (file, symbol), with call, write, read
  and idea-reference counts and the core file that defines the symbol (14,064 rows).
- `external_files_summary.csv`: every non-history file that uses an economy
  symbol, ranked by how many distinct symbols it uses (503 files), with symbol families.
- `unreferenced_core_definitions.csv`: core effects and triggers with no reference
  anywhere in the mod (144).

## Method

1. **Core**, meaning what the simplification would replace:
   - `scripted_effects`: `IC_Econ_2024`, `IC_Economic_Scripted_Effects`, `IC_Economy_Effects`,
     `IC_Financial_Scripted_Effects_for_Content`, `IC_Industrial_Pulse`, `IC_Inflation_Effect`,
     `IC_Loans_and_Interest_Rate_Effects`, `IC_Consumer_Goods`, `consumer_goods_ai_automated_trade_effects`,
     `IC_Trade_Scripted_Effects(_Cuts)`, `CWIC_trade_exporter_lists`, `IC_literacy_calculations`,
     `IC_tax_avoidance_line`, `IncomeGenerator*` (3), `PolicyCostCalculator`, `StartupMoney`,
     `policy_focus_effects`, `CWIC_GDP_Growth_Effects`, `CWIC_Employment_Init`,
     `CWIC_employment_scratch_cleanup`, `CWIC_Econ_Change_scripted_effects`, `IC_State_Decisions_Effect`,
     `CWIC_Goods_Generated_Effects`, `CWIC_state_category_cache`, `IC_scripted_effects`.
   - `scripted_triggers`: `IC_Economic_System_Triggers`, `IC_spending_level_triggers`,
     `IC_state_decision_triggers`, `cwic_cg_unlocks_scripted_triggers`, `IC_Pops_Triggers`.
   - `ideas`: `IC_Policies`, `z_policy_ideas`, `zz_econ_laws`, `IC_Laws`, `IC_Laws_Country`, `_economic`, `IC_Edicts`.
   - Events: `Economic_Penalties`, `IMF`, `IC_Food_Pulse`, `CWIC_Economy_Guide`.
   - UI: `scripted_guis/Finance_Tab`, `Trade_Tab`, and the scripted localisation files `IC_Economy_scripted_localisation`,
     `IC_Econ2_Loc`, `economy_gui_localisation`, `CWIC_Econ_gfx_scripted_loc`.
   - Decisions: `IC_Financial_Decisions`, `IC_Economic_Investments`.
2. **Vocabulary**, the 2,600+ symbols scanned for:
   - top-level effect and trigger names defined in core;
   - idea names defined in the core idea files;
   - every variable that core effects write, excluding temp variables.
3. **Scan.** Every other `.txt`/`.gui` file was tokenised with comments stripped. Each
   use was classified as `call` (`x = yes`), `write` (target of `set_`/`add_to_`/`subtract_from_`/…`_variable`),
   `idea` or `read`.

Limits:

- The scan is static, so names built with `@token`, `^index` or `[?…]` concatenation are missed.
- Some generic engine keys were dropped (`modifier`, `allowed`, `buildings`, `resources`…).
- A few variables that core happens to write are not economy (`badboy`, `kurd_agit_*`,
  `INO_Approval_*`, `radiation`). They show up in the CSV; ignore them.
- `history/` (2,600 files) is reported separately because it is starting data, not logic.

## 1. Entry points and who runs them

| Effect | Called from | Runs for |
|---|---|---|
| `ic_financial_monthly_pulse` | `00_on_actions.txt:44` | players only (`is_ai = no`) |
| ↳ `income_effect` (IncomeGenerator) | `IC_scripted_effects.txt:57`, `IC_Economy_Effects.txt:736` | players |
| ↳ `industrial_pulse` | `IC_scripted_effects.txt:65`, `IC_Economy_Effects.txt:738`, plus `_generic_decisions:1526`, `on_startup_defines:3238`, `CWIC_Insurgency_Economy_Effects:41,57`, `Indochina_Theater_Effects:3698`, `MLA_scripted_effects:386` | players, plus those content hooks |
| ↳ `gdp_calculation_effect` | `IC_scripted_effects.txt:81`, `IncomeGenerator.txt:292`, `IC_Economy_Effects.txt:750` | players; AI only through the territory refresh |
| ↳ `cwic_cg_monthly_master_tick` | `IncomeGenerator.txt:293`, `IC_Economy_Effects.txt:745` | players |
| ↳ `cwic_inflation_monthly_pulse` | `IncomeGenerator.txt:1268` | players |
| `monthly_education_pulse` | `00_on_actions.txt:40` | **everyone** not in an insurgency |
| `cwic_ai_money_stipend`, `cwic_ai_refresh_gdp_on_territory_change` | `00_on_actions.txt:51-52` | AI |
| `export_script_for_pool` | `00_on_actions.txt:57`, `on_startup_defines.txt:3569` | everyone |
| `Policy_Startup_Script_2025` | `IC_Econ_2024.txt:2176` | startup |
| `cwic_inflation_tier_monthly_assign`, `state_population_category_check` | none | never runs |

The only monthly logic that reaches the AI is education, export pools and a flat money stipend.

## 2. Footprint outside core, by symbol family (history excluded)

| Family | Files | Main surface |
|---|---|---|
| Treasury (`currentMoney`, `cwic_change_money`) | 178 | 129 files write `currentMoney` directly; only 28 use `cwic_change_money` |
| Non-economic policy sliders (media, religion, union, women, minorities, saga) | 202 | the same `policy_*_temp_N` idea framework as the economy policies |
| Social spending (`increase_education_rate`, `_welfare_`, `_healthcare_`, `_service_`, `_military_policy`) | 109 | mostly focuses (188 refs) |
| Tax (`increase_tax_rate`, `lower_tax_rate`, `policy_taxrate_temp_1..5`, class tax effects) | 70 | focuses (126 refs) |
| Economic system axes (`economic_x/y_axis`, `step_towards_*`, `india_economic_towards_*`, `convert_to_*`) | 62 | focuses; 11 files write the axes raw |
| Trade, exports, consumer goods | 50 | `Trade_Tab.gui` (184 refs), dynamic modifiers, trade laws in focuses |
| Inflation / CPI | 47 | `increase/decrease_cpi_policy` in 38 focus files; `CWIC_inflation_mom` in 5 |
| GDP, HDI, pops, education shares | 39 | read-mostly: MNC, separatism, environment, logging, crisis triggers |
| Corruption (`CorruptionLevel`) | 35 | written raw in focuses |
| Debt, loans, credit, interest | 32 | small, but the most fragile (§4) |

Localisation: 243 `[?var]` reads of economy variables across 19 English files. The
biggest are `CWIC_core` (68), `decisions` (57), `CWIC_MNC` (28), `CWIC_Culture` (24) and `CWIC_laws` (20).

## 3. Most-used content API

Effects called from outside core, by number of files:

| Effect | Files | | Effect | Files |
|---|---|---|---|---|
| `increase_union_policy` | 53 | | `cwic_change_money` | 28 |
| `increase_education_rate` | 47 | | `increase_service_policy` | 28 |
| `increase_welfare_rate` | 45 | | `increase_tax_rate` | 27 |
| `increase_military_policy` | 38 | | `decrease_union_policy` | 24 |
| `increase_healthcare_rate` | 31 | | `lower_tax_rate` | 18 |
| `increase_cpi_policy` | 28 | | `increase_Free_Market_Economy` | 13 |

Policy ideas are also handled directly, which bypasses those effects. Examples by number of files:

| Ideas | add_ideas | remove_ideas |
|---|---|---|
| `policy_media_*` | 56 | 53 |
| `policy_religion_*` | 44 | 37 |
| `policy_union_*` | 38 | 35 |
| `policy_cpi_*` | 20 | 20 |
| `policy_taxrate_*` | 17 | – |
| `policy_education_*` | 18 | 16 |
| `policy_welfare_*` | 17 | 17 |
| `policy_healthcare_*` | – | 17 |

The raw idea edits cannot be routed through one setter until each of those files is migrated.

## 4. Raw writes into economy state

These are the places most likely to break under a redesign.

**Money amounts are hard-coded absolutes.**
- 1,280 `add_to_variable currentMoney = <literal>` and 118 literal subtractions, ranging from −4000 to +300.
- They are concentrated in a few files: `CWIC_Space` events (396), `CWIC_GDR_Card_Game_Effects` (242),
  `VIE_Effects` (72), `SOV_Beria_Malenkov` (62), `SWK_RAJ_50s`, `Saudi_60s`, `Sov_Five_Year_Plan_Nine`,
  `JAP_decisions`, and 99 more files.
- Weapon purchasing deducts priced variables: 1,036 variable subtractions across `weapon_purchasing_*`,
  `rgo_development_northamerica` and `scenario_tests/international_market`.
- Any change to the money unit or scale must re-price every one of these. Grants that
  scale with GDP would need a converter effect.

**Debt is handled by hand in content.** These files copy the loan-creation internals:
- `currentDebt` / `currentDebtPayments` are written by `PRC_50s` (decision), the focus files `GDR_1960s`,
  `SOV_Kaganovich`, `SWE_50s` and `YUG_70s`, `influence_scripted_diplomatic_actions`,
  `CWIC_Insurgency_Economy_Effects`, `FRA_scripted_effects` and `VIE_Effects`.
- `debtTotalsArray`, `debtOwnerArray` and `debtPaymentArray` are built by `influence_scripted_diplomatic_actions`
  and edited in `GDR_1960s`, `SWE_50s`, `YUG_70s` and `FRA_scripted_effects`.
- `pulse_deficit` × `Interest_Rate` loan maths is copied in `YUG_70s`, `GDR_1960s`, `SWE_50s`,
  `FRA_1950s`, `FRA_scripted_effects` and `events/Indonesia.txt`.

**Credit, inflation and GDP are read by other systems:**
- `Credit_Rating`: written by `IMF_effects`; read by `IMF_Decisions`, `IC_localisation` and the macro-crisis triggers.
- `Interest_Rate`: read by `YUG_70s`, `CWIC_macro_crisis_scripted_triggers_v2` and `Finance_Tab.gui`.
- `CWIC_inflation_mom`: written by `CWIC_Capital_Controls`; read by IMF decisions, decision categories,
  `CWIC_Economy_Log_on_actions` and the macro-crisis triggers.
- `grossdomesticproduct`: read by 17 files, including division limits, the NATO ranking scorer, Crisis Manager,
  line graphs, Capital Controls and French effects.

**Economic axes are written raw** in 11 files: Albania AC, `INO_50s`, `NEP_1950s`, `TIB_1950s`,
`Indochina_Theater`, `MLA`, `VIE`, `VIN`, `WW3_Europe` effects, and the `Indonesia` and `SOV_Stalin`
events. They are read by MNC (decisions, triggers, generated ideas, 1949 seed) and `Resource_Efficiency`.

**Education shares are written raw** in the INO Hatta, Natsir and Wilopo focuses, `50s_TUR_new`,
`YUG_scripted_effects` and `events/Indonesia.txt`.

## 5. Economy-adjacent subsystems that depend on core

These are not core, but each would need an adapter or a rewrite:

| Subsystem | Files | Depends on |
|---|---|---|
| Macro crisis | `CWIC_macro_crisis_scripted_triggers_v2`, `CWIC_Crisis_Manager_Effects_with_Ideas` | GDP, debt, debt payments, `pulse_deficit`, inflation, credit, interest (30 symbols) |
| IMF / World Bank | `IMF_effects`, `IMF_Decisions`, `events/IMF` | credit rating, loans, exports |
| Capital controls | `CWIC_Capital_Controls` | inflation, GDP, money (30 symbols) |
| MNC | `MNC_Decisions`, `cwic_mnc_triggers`, `CWIC_MNC_*` | axes, National/State HDI; money via 67 variable payouts |
| Influence / foreign loans | `influence_scripted_diplomatic_actions`, `IC_Influence_events`, `MD_influence.gui` | builds debt arrays |
| Insurgency economy | `CWIC_Insurgency_Economy_Effects` | money, debt, `industrial_pulse` (34 symbols) |
| Weapon purchasing | `weapon_purchasing_*` (6 files) | money |
| Employment / pops | `Employment_Effects`, `pop_effects`, `IC_Flag_Building_Effects` | wages, education shares, HDI |
| Environment, separatism, religion GUI | `CWIC_Enviroment`, `separatism_effects`, `CWIC_Religion_GUI` | State HDI, money |
| Logging / graphs | `CWIC_Economy_Log_on_actions`, `line_graph_scripted_effects` | GDP, debt, inflation, HDI |
| Division limits, NATO scorer | `CWIC_division_limit_*`, `NATO_ranking_scorer` | GDP |
| Dynamic modifiers / tokens | `0_dynamic_modifiers` (54), `IC_dynamic_modifiers` (29), `synchronized_dynamic_tokens/tokens` (54) | economy variables as modifier inputs |
| UI | `Finance_Tab.gui`, `Trade_Tab.gui`, `US_HOUSE` decisions (56), `events/tutorial` (28) | broad reads |

## 6. Starting data in `history/`

| Data | State or country files |
|---|---|
| `literate_` / `primary_` / `high_school_` / `college_educated` | ~2,090 state files each |
| `economic_x_axis`, `startup_economics` | ~489 |
| `economic_y_axis` | 221 |
| `currentMoney` | 75 |
| Trade laws (`closed_economy`, `export_focus`, `limited_exports`) | ~57 |
| Policy ideas set in history | small (≤10 each) |
| `CorruptionLevel` | 7 |

Corruption is unset for almost every country, so it reads as 0.
A simplification that keeps the education shares and the x/y axes keeps the bulk of
the history data valid. Dropping either one invalidates about 2,000 files.

## 7. Dead or unreachable core

There are 144 definitions with no reference anywhere (`unreferenced_core_definitions.csv`):

| Count | Where | What |
|---|---|---|
| 70 | `IC_spending_level_triggers` | e.g. `air_has_atleast_*_percent` |
| 27 | `IC_Inflation_Effect` | the `cwic_inflation_env_remove_*` set |
| 11 | `IC_Economic_System_Triggers` | `has_*_economy` triggers for feudal, palace, cartel, keynesian… |
| 11 | `IC_Economy_Effects` | `convert_to_feudal_1..3`, `_palace`, `_drug_cartel`, `_war_economy`, `_colonial`… |
| 4 | `IC_Loans_and_Interest_Rate_Effects` | including `cwic_clear_default_status` and `cwic_oil_pricing_monthly` |
| 1 | `PolicyCostCalculator` | `policy_cost_pulse` |

Separately, `state_population_category_check` and `cwic_inflation_tier_monthly_assign` are defined but never called.

## 8. What this means for planning

- **The public API is small and well used.** The `increase_*`/`decrease_*` policy effects and
  `cwic_change_money` cover about 150 files. Keep those names with new bodies and those
  files need no changes.
- **Most of the work is in raw writes:**
  - 129 files write money directly with absolute literals;
  - about 10 files hand-roll debt;
  - about 60 files add or remove policy ideas directly;
  - 11 files write the axes.
  These need a mechanical codemod to new setter effects before or during the cutover.
- **Seven subsystems read core internals** (macro crisis, IMF, capital controls, MNC, influence loans,
  logging, division limits). Whatever replaces GDP, debt, inflation and credit needs a
  small, stable set of output variables they can read.
- **The non-economic policy sliders share the economy's policy framework.** That puts 202
  files in scope unless the redesign keeps the `policy_*_temp_N` framework and changes only
  the economic lines.
