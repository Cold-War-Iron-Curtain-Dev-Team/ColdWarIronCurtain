# Economic Systems (axes) and Economic Investments / Financial Decisions Audit

Scope: `Cold War Iron Curtain/common/...` (paths below are relative to `Cold War Iron Curtain/`). Read-only. Sections 1-2 of `LogDocs/Economy_Rework/Economy_System_Overview.md` and the existing audit slices were used to avoid repeats. Known findings not repeated here: S1 (AI has no treasury loop), S2 (tax avoidance no-op), B1 (double welfare), P1 (dockyards), B7 (dead `cwic_default_monthly_check`), U3 (`tax_efficiacy` spelling in UI).

`[INFERENCE]` = not directly observed in the files read.

---

## Summary (top findings)

1. **H – Wrong budget checked in `_modernize` and `_automate` upgrades.** Their `complete_effect` gates `FBU_category_2/3 = yes` on `industrialization_budget`, not `modernization_budget` / `automation_budget` (e.g. `common/decisions/IC_Economic_Investments.txt:792-832`, `884-920`, `972-1012`, `1064-1100`, `1153-1189`, `1238-1274`, `1323-1359`, `1408-1444`). Result: the upgrade trigger fires from the wrong pool. Starved modernization/automation budgets can be upgraded when industrialization budget is high, and vice versa.
2. **M – Leftover budget is refunded to treasury.** `common/scripted_effects/IC_flagbuildings_category.txt:133-135, 260-261, 387-389, 516-518` move remaining budget back into `currentMoney` and zero the budget. Every investment is therefore partially reversible; the net treasury cost depends on when the FBU effect runs `[INFERENCE]`.
3. **M – `economic_modifier_war_reparations_exp` read without a write in the positive branch.** `common/scripted_effects/IncomeGenerator.txt:1181-1186` adds `_exp` to `trade_income` when reparations > 0; `_exp` is written only in the negative branch (`:405-416`). A receiving country adds a stale or zero value `[INFERENCE]`.
4. **M – `economic_modifier_state_development_cost` is written but never read or cleared.** Written at `common/scripted_effects/IC_Economy_Effects.txt:156, 195, 317, 353`; the only modifier that reads it is commented out at `common/dynamic_modifiers/0_dynamic_modifiers.txt:432` ("On Hold"); `clear_current_economic_modifiers` (`IC_Economy_Effects.txt:581-604`) does not reset it, so it accumulates across axis steps.
5. **M – Startup axis-to-modifier mapping has coverage gaps.** `startup_economics` only maps axes when `economic_x_axis < 19` (`IC_Economy_Effects.txt:363-369`). x=19 and x≥29 get no axis modifiers. x=27 (drug cartel) and x=28 (war economy) have no branch (`:443-560`), though triggers and map colours exist for them.
6. **M – Inconsistent conversion paths.** `conversion_to_normal_axis` calls `startup_economics` (`IC_Economy_Effects.txt:626-631`), but `conversion_to_rentier` (`:606-625`) and `convert_to_petrostate` (`:632-`) do not, so their modifier sets are hand-written and diverge from the axis-derived set.
7. **M – `consumer_goods_need` step asymmetry.** Planned steps add +0.001 (`IC_Economy_Effects.txt:36`) and startup planned adds the same (`:203`); market steps subtract 0.01 (`:81`, `:245`). A 10x asymmetry in the same direction on either side is a probable typo `[INFERENCE]`.
8. **M – Stacked market income multipliers.** `cwic_cache_market_income_multipliers` (`common/scripted_effects/IC_Econ_2024.txt:965-1025`) uses non-exclusive `if` blocks for civ (1.75 / 1.5 / 1.25) and OFP (1.9 / 1.65 / 1.35), so mid-range states multiply (2.625 / 3.135) `[INFERENCE]`.
9. **M – Decision AI weight is unconditional on conversion decisions.** `convert_to_rentier`, `convert_to_normal_economic_axis_system`, `convert_to_petrostate` all use `ai_will_do = { factor = 1 }` with no gating (`common/decisions/IC_Financial_Decisions.txt:36, 65, 93`). Investments have `factor = 0` and `+50` only when `currentMoney > 500`.
10. **M – `economic_z_axis` has readers but no writer found in `common/`, `events/`, `history/`.** Read in `common/map_modes/cwic_map_mode.txt:6550, 6574, 6598, 6623, 6647, 6671, 6695, 6717, 6739` and `common/scripted_localisation/IC_Economy_scripted_localisation.txt` / `CWIC_Econ_gfx_scripted_loc.txt` (`economic_z_axis = 1`). `national_focus/` was not searched (path skipped). If unwritten, the nine z-gated system labels/colours never show `[INFERENCE]`.

---

## 1. Entry points

### 1a. Axis steps and startup (IC_Economy_Effects.txt)

| Effect | File:line | Callers (player vs AI) |
|---|---|---|
| `step_towards_planned` / `_market` / `_public` / `_private` | `IC_Economy_Effects.txt:34, 79, 124, 163` | Decisions and national focus: `common/decisions/US_HOUSE.txt` (many, e.g. `:5796-5797`, `:13088`, `:13152`, `:13213`, `:13337`, `:13399`, `:14574`, `:15930`); `common/scripted_effects/CWIC_GDR_Card_Game_Effects.txt:756, 1562, 3311, 4222`; events `events/USA_1980s_ForPol.txt:6746`, `events/USA_1980s_General_Events.txt:1513`. Mixed player and AI (events and US_HOUSE decisions apply to whoever owns them `[INFERENCE]`). |
| `step_towards_*_startup` | `IC_Economy_Effects.txt:201, 243, 285, 321` | Only `startup_economics` (`:385, :401, :419, :435`). |
| `startup_economics` | `IC_Economy_Effects.txt:357` | `scripted_effects/Indochina_Theater_Effects.txt:3468` (x=22); `scripted_effects/MLA_scripted_effects.txt:362` (x=6,y=9); `scripted_effects/VIE_Effects.txt:1143`; `conversion_to_normal_axis` (`IC_Economy_Effects.txt:630`); national focus `NEP To Fix/NEP_1950s.txt:1655-1657` (x=23) and others listed in section 4. Startup is scripted (history / focus / event), not a player-facing action. |
| `clear_current_economic_modifiers` | `IC_Economy_Effects.txt:581` | `Indochina_Theater_Effects.txt:3466`, `MLA_scripted_effects.txt:359`, `VIE_Effects.txt:1140`, and inside the three conversion effects (`:607, 627, 633`). |
| `conversion_to_rentier` | `IC_Economy_Effects.txt:606` | `common/decisions/IC_Financial_Decisions.txt:34` (player decision `convert_to_rentier`, visible x<18); `events/Malaysia.txt:909`; `events/_Decolonization.txt` (about 20 call sites, e.g. `:156, 231, 286, 350, 448, 520, 585, 683, 728, 859, 918`) and `_Decolonization_Debug.txt`. Decolonization = scripted, mostly AI-owned minors. |
| `conversion_to_normal_axis` | `IC_Economy_Effects.txt:626` | `IC_Financial_Decisions.txt:63` (`convert_to_normal_economic_axis_system`, visible x>17). Player only. |
| `convert_to_petrostate` | `IC_Economy_Effects.txt:632` | `IC_Financial_Decisions.txt:91` (`convert_to_petrostate`, visible x=24, available `oilExport > 75`). Player only. |

Frequency: axis steps fire from decisions and events on demand. Startup fires once per country at history/focus/event time. `_Decolonization` events fire for minors when independence is granted.

### 1b. Investment and financial decisions

- `common/decisions/IC_Economic_Investments.txt` (block `economic_investments`, line 1): 61 decision entries (category toggles, `*_industrialize`, `*_develop`, `*_modernize`, `*_automate`, `*_locked`). Player-facing; AI weight only via `ai_will_do` (section 3c).
- `common/decisions/IC_Financial_Decisions.txt`: `economy_decisions_reenable` (line 1), `economy_decisions` (line 8) with `convert_to_rentier`, `convert_to_normal_economic_axis_system`, `convert_to_petrostate`, `SOV_Reperation_Payments` (HUN only), `PAEU.1`-`PAEU.3` (EU federation, cost 150/150/300).
- Budget readers: `scripted_effects/IC_flagbuildings_category.txt` (FBU_category_0-3), `scripted_effects/IC_Flag_Building_Effects.txt:6-34`, `scripted_effects/IC_State_Decisions_Effect.txt:533-735` (state upgrade costs), `common/decisions/Religious_Decisions.txt:23-25, 190-192, 365-367, 485-507, 669-691` and `00_decision_categories.txt:133-135` (budget gating for religious and other decisions).

---

## 2. Data model

### 2a. Axis variables

| Variable | Meaning | Writers | Readers |
|---|---|---|---|
| `economic_x_axis` | public (low) ↔ private (high) | `step_towards_public/private` (`IC_Economy_Effects.txt:159, 198`), conversion effects (`:609, 628, 635`), focus/event writes (section 4) | modifiers via `startup_economics` (`:363`), `IC_Econ_2024.txt:669-764, 965-1025, 1164-1172, 1273-1294, 2391-2458`, `IC_Industrial_Pulse.txt:746-751`, `Resource_Efficiency.txt:208-212`, `policy_focus_effects.txt:7989`, `on_startup_defines.txt:1939, 1956-1973`, `CWIC_MNC_Seed_1949_Presence.txt:10-20`, `cwic_mnc_triggers.txt:2-10`, `IC_Economic_System_Triggers.txt`, `cwic_map_mode.txt:6506-6582`, `IC_Financial_Decisions.txt:9-30, 41-47, 70-75` |
| `economic_y_axis` | planned (low) ↔ market (high) | `step_towards_planned/market` (`:75, 120`), conversion (`:629, 629`), focus/event writes | `startup_economics` (`:364`), `IC_Econ_2024.txt:540-544` (farmer shift), `IC_Econ_2024.txt:965-1025` (y<19 gate), triggers, map mode and localisation |
| `public_private_ratio` | startup step count for x | `startup_economics` (`IC_Economy_Effects.txt:363-369`) | local to startup |
| `planned_market_ratio` | startup step count for y | `startup_economics` (`:363-369`) | local to startup |
| `economic_z_axis` | (unknown) | none found in `common/`, `events/`, `history/` | `common/map_modes/cwic_map_mode.txt:6550-6739`; localisation (`IC_Economy_scripted_localisation.txt:456-799`, `CWIC_Econ_gfx_scripted_loc.txt:181-317`) |

### 2b. Modifier variables (`economic_modifier_*`)

- Written by step effects (both directions, bulk of the list in `IC_Economy_Effects.txt:36-353`) and cleared by `clear_current_economic_modifiers` (`:581-604`, 23 variables).
- Read by `common/dynamic_modifiers/0_dynamic_modifiers.txt:391-~430` (`economic_system_modifier`, applied at `IC_Economy_Effects.txt:358-360`).
- Exceptions:
  - `economic_modifier_state_development_cost`: written (`:156, 195, 317, 353`), not cleared, not read (its modifier is `#` commented at `0_dynamic_modifiers.txt:432`).
  - `economic_modifier_education_gain_rate`: written by `national_focus/TIB_1950s.txt:1705, 1785` (+0.05 each); read at `0_dynamic_modifiers.txt:420`; not cleared by `clear_current_economic_modifiers` `[INFERENCE: it is intentionally focus-driven]`.
  - `economic_modifier_war_reparations`: written by `scripted_effects/War_Reparation_Effects.txt:15, 34, 46, 58, 70, 82, 91, 145, 183, 199, 214`; read by `IncomeGenerator.txt:406, 1182` and `0_dynamic_modifiers.txt:440` (`war_reperations`).
  - `economic_modifier_war_reparations_exp`: written only `IncomeGenerator.txt:410, 413`; read at `:416` and `:1186` (see problem 3).

### 2c. Investment budget variables

| Variable | Writers | Readers / spenders |
|---|---|---|
| `industrialization_budget` | `IC_Economic_Investments.txt:94, 177, 255, 337` (industrialize tiers); `common/decisions/Religious_Decisions.txt:486, 670, 502` (religious conversions +5/+10) | `IC_flagbuildings_category.txt:12-23, 46-133` (FBU_category_0); `IC_State_Decisions_Effect.txt:534-583` (spending by `UPC_pop*`); `IC_Economic_Investments.txt:103-143, 186-222, 264-304, 346-389` (per-state flag gates); `IC_Economic_Investments.txt:792-1444` (wrong-budget checks, problem 1) |
| `development_budget` | `IC_Economic_Investments.txt:431, 517, 599, 681` | `IC_flagbuildings_category.txt:141-261`; `IC_State_Decisions_Effect.txt:591-` (dev1 spend); `IC_Economic_Investments.txt:440-480, 526-562, 608-644, 700-736` |
| `modernization_budget` | `IC_Economic_Investments.txt:783, 875, 963, 1055` | `IC_flagbuildings_category.txt:267-389` (FBU_category_2); `IC_Flag_Building_Effects.txt:22-26`; `IC_State_Decisions_Effect.txt:641-683` (dev2 spend) |
| `automation_budget` | `IC_Economic_Investments.txt:1144, 1229, 1314, 1399` | `IC_flagbuildings_category.txt:394-521` (FBU_category_3); `IC_Flag_Building_Effects.txt:30-34`; `IC_State_Decisions_Effect.txt:692-733` (dev3 spend) |
| `currentMoney` (treasury) | subtract in each investment `complete_effect` (`IC_Economic_Investments.txt:93, 176, 254, 336, 430, 516, 598, 680, 782, 874, 962, 1054, 1143, 1228, 1313, 1398`); refunds at `IC_flagbuildings_category.txt:134, 261, 388, 517` | treasury `income_effect` (IncomeGenerator.txt:287) and availability checks (`IC_Economic_Investments.txt:89, 172, 250, ...`) |
| `category_upgrades.*` (flag) | `IC_Economic_Investments.txt:18-19` etc. (state machine) | visible gates in each category upgrade |

`global.UPC_pop*`, `global.UPC_pop*dev1..dev3` cost tables are set in `common/on_actions/on_startup_defines.txt:3062-3156` (e.g. `UPC_pop1 = dev0per`, `UPC_pop1dev2 = dev2per`, `UPC_pop15 *= 3.5` at `:3078`). Not all dev3 entries were verified `[INFERENCE]`.

---

## 3. Formulas (step by step)

### 3a. Axis step effects (`IC_Economy_Effects.txt`)

- `step_towards_planned` (34-77): applies additive changes to 13 variables (`consumer_goods_need +0.001`, `market_resources -0.01`, `office_park_construction_speed -0.02`, `office_park_income -0.02`, `production_eff_growth -0.01`, `tax_efficiacy +0.01`, `tax_avoidance_elasticity -0.01`, `welfare_spending -0.01`, `industrialization_complex_building_speed +0.02`, `infrastructure +0.02`, `railway +0.02`, `water_infra -0.02`, `state_infra -0.02`), plus `economic_modifier_state_development_cost +0.02` (`:156`), and `economic_y_axis -1` (`:75`).
- `step_towards_market` (79-122): mirror values; `consumer_goods_need -0.01` (`:81`); `economic_y_axis +1` (`:120`).
- `step_towards_public` (124-161): `welfare -0.01`, `education -0.02`, `tax_eff +0.01`, `tax_avoid -0.01`, `food_consumption -0.01`, `agricultural_income -0.02`, `arms_factory_income -0.02`, `office_park_income -0.02`, `electricity +0.01`, `research_speed -0.01`, `state_development_cost +0.02`, and `economic_x_axis -1` (`:159`).
- `step_towards_private` (163-200): mirror; `economic_x_axis +1` (`:198`), `state_development_cost -0.02` (`:195`).
- `*_startup` variants (201-355): same deltas without axis writes; `state_development_cost` writes at `:317, :353`.

### 3b. startup_economics (357-~580)

1. `:358-360` add dynamic modifier `economic_system_modifier` (`0_dynamic_modifiers.txt:391-~430`).
2. `:363-369` if `economic_x_axis < 19`: `public_private_ratio = x - 9`, `planned_market_ratio = y - 9`.
3. `:372-436` while-loops step the startup variants (direction determined by sign of ratio).
4. `:443-455` x=20 (palace): research -0.25, prod_eff -0.25, office_park_income -0.25, all building speeds -0.25, conscription/stability/war_support +0.12.
5. `:465-481` x=21 (feudal I): -0.15 values, factors +0.1.
6. `:486-502` x=22 (feudal II): -0.1, factors +0.075.
7. `:507-523` x=23 (feudal III): -0.05, factors +0.05.
8. `:528-543` x=24 (rentier): research -0.025, prod_eff -0.025, agri building -0.15, industrial +0.5, infra -0.15, state_infra -0.1, water -0.1, railway -0.15, office park construction +0.5, agricultural_income +0.1, office_park_income -0.1, market_resources +0.25.
9. `:548-~560` x=25 (petrostate): industrial -0.5, infra/state_infra/railway +0.25, office park construction +0.10, office_park_income +0.15, market_resources +0.4, food_consumption +0.1, welfare +0.1, stability +0.15.
10. `:565-~580` x=26 (colonial): research -0.05, prod_eff -0.05, agricultural_income +0.1, office_park_income -0.1, market_resources +0.4, conscription/stability/war_support -0.05.
11. x=27 and x=28: no branch; final `else = { }`.

### 3c. Investment costs and AI weight (IC_Economic_Investments.txt)

- Categories: 4 budgets (`industrialize`, `develop`, `modernize`, `automate`) × 4 tiers (25/100/250/500), plus 4 `*_locked` placeholders (1459-1623).
- Cost: every upgrade has `cost = 0` at the decision level (e.g. `category_upgrade_25` `:5`); actual money is taken in `complete_effect` by `subtract_from_variable = { currentMoney = N }`. Availability is `check_variable = { currentMoney >= N }` (`:89, 172, 250, 331`).
- `ai_will_do` for every tier: `factor = 0` plus `modifier add = 50 when currentMoney > 500` (e.g. `:149-155`, `:228-234`, `:310-316`, `:396-402`, `:486-492`, `:568-574`, `:650-656`, `:742-748`, `:838-844`, `:926-932`, `:1018-1024`, `:1106-1112`, `:1195-1201`, `:1280-1286`, `:1365-1371`, `:1450-1456`).
- Category toggles (`category_upgrade_25/100/250/500`, `:3-69`): cost 0, `complete_effect` flips `category_upgrades.*` flags in a cycle 25→100→250→500→25 (`:18-19, 34-35, 50-51, 66-67`). These are UI state switches.
- Spending flow: budget = `budget + N`, then per-state flag checks `budget > global.UPC_pop*` set `FBU_category_N = yes` and call `full_upgrade_estimate_regen` (`:103-146`, etc.). The per-state upgrade is then paid from the budget in `IC_State_Decisions_Effect.txt:533-735`.
- Locked placeholders (`:1459-1623`): visible when the category is not unlocked; complete subtracts `currentMoney = 1` (a 1-unit fee on a visibly locked button). Visibility not analysed in full `[INFERENCE: placeholder]`.

### 3d. Financial decisions (IC_Financial_Decisions.txt)

- `convert_to_rentier` (9-40): visible `economic_x_axis < 18`; available `average_development >= 1` (`:15-21`) and `Rentier_Economic_Check > 0.7` (`:25-29`); complete `conversion_to_rentier`; `ai_will_do factor = 1`.
- `convert_to_normal_economic_axis_system` (41-69): visible `economic_x_axis > 17`; available `average_development >= 1` and `Rentier_Economic_Check < 0.6`; complete `conversion_to_normal_axis` (sets x=12, y=12 then startup); `ai_will_do factor = 1`.
- `convert_to_petrostate` (70-95): visible `economic_x_axis = 24`; available `average_development > 3` or `= 3`, `oilExport > 75`; complete `convert_to_petrostate`; `ai_will_do factor = 1`.
- No `cost` field on the three conversions (free).
- `PAEU.1` (cost 150, `:~123`), `PAEU.2` (cost 150), `PAEU.3` (cost 300): EU federation, visibility by capital continent and SOV modifier.
- `SOV_Reperation_Payments` (HUN only): visible when `Loan_Repayment_Enabled` flag and reparation idea; `civilian_factory_use = 5` modifier; `days_remove = 180` remove effect cycles reparation ideas 1→2→3→4 (not economy-axis related).

---

## 4. Interactions

- **Treasury (`income_effect`, `IncomeGenerator.txt:287`)**: first line is `cwic_process_war_reparations` (`:288`). War reparations are treated as expense (`:405-419`, `custom_expenses`, `totalexp`) and income (`:1181-1186`, `trade_income`). Problem 3 applies. Investment budgets are not read by `income_effect`; they are only refunded to `currentMoney` in `IC_flagbuildings_category.txt`.
- **GDP (`gdp_calculation_effect`, `IC_Econ_2024.txt`)**: `cwic_cache_market_income_multipliers` (`:965-1025`) and `calculate_conversion_lwa_capitalist_and_bureaucrat` (`:669-764`) read x and y. `CWIC_nationalization_pressure_index` (`:2391-2458`) uses x steps and an exclusive else-if relief. `farmer_y_axis_shift` (`:540-544`). `IC_Econ_2024.txt` was only grepped for axis readers, not read in full `[INFERENCE: complete]`.
- **Trade**: `IC_Industrial_Pulse.txt:746-751` (crop boost x=24/26), `Resource_Efficiency.txt:208-212` (x=24 efficiency +0.15), `cwic_mnc_triggers.txt:2-10` and `CWIC_MNC_Seed_1949_Presence.txt:10-20` (MNC gating and seed on x/20).
- **Taxes/policies**: `policy_focus_effects.txt:7989-7991` (`Startup_Policy_Welfare_Base_Modifier = economic_x_axis / 3.5`, unbounded); `on_startup_defines.txt:1939, 1956-1973` (corporate_startup_rate and `economic_freedom_tax_adjustment = -(x-18)/2`). `modifier_tax_efficiacy` and `tax_avoidance_elasticity` come from step effects (`IC_Economy_Effects.txt:44, 47, 111, 130, 205, 290`).
- **Welfare**: `CWIC_Econ_Change_scripted_effects.txt:1-63` (`Econ_Welfare_UP_five`): ladders `policy_welfare_temp_0` → `_7` via `swap_ideas`. The file was read only to line 63 of 182 `[INFERENCE: rest is the same ladder]`.
- **UI/map/localisation**: `cwic_map_mode.txt:6506-6741` (colours by x/y and z); localisation keys `ECON_SYSTEM_*` in `IC_Economy_scripted_localisation.txt:455-799` and `CWIC_Econ_gfx_scripted_loc.txt:181-317`.
- **Investments and state upgrades**: `IC_State_Decisions_Effect.txt:533-735` uses the budgets as the spending pool; `IC_flagbuildings_category.txt` decides whether a state is upgraded this month.
- **Religious decisions**: `Religious_Decisions.txt:485-507` and similar add to the budgets (+10/+5) directly, bypassing `currentMoney`.
- **Decolonization and events**: `_Decolonization.txt` calls `conversion_to_rentier` ~20 times; these bypass decision `available` gates (no axis or development check).

---

## 5. Problems

| # | Sev | Location | Problem |
|---|---|---|---|
| 1 | H | `common/decisions/IC_Economic_Investments.txt:792, 806, 820, 832` (`_25_modernize`); `884, 898, 912, 920` (`_100_modernize`); `972, 986, 1000, 1012` (`_250_modernize`); `1064, 1078, 1092, 1100` (`_500_modernize`); `1153-1189`, `1238-1274`, `1323-1359`, `1408-1444` (automate) | Modernize and automate `complete_effect` checks use `industrialization_budget` instead of `modernization_budget` / `automation_budget`. The FBU flag set by these decisions is then wrong. |
| 2 | M | `common/scripted_effects/IC_flagbuildings_category.txt:133-135, 260-261, 387-389, 516-518` | Remaining budget refunded to `currentMoney` and zeroed. Investments are partially reversible; treasury cost is not fixed `[INFERENCE: timing]`. |
| 3 | M | `common/scripted_effects/IncomeGenerator.txt:1181-1186` vs `:405-416` | `economic_modifier_war_reparations_exp` is only written in the paying branch (`:410`) but read in the receiving branch (`:1186`). Receiving countries use a stale or zero value. |
| 4 | M | `common/scripted_effects/IC_Economy_Effects.txt:156, 195, 317, 353`; `common/dynamic_modifiers/0_dynamic_modifiers.txt:432`; `IC_Economy_Effects.txt:581-604` | `economic_modifier_state_development_cost` is accumulated (+0.02 / -0.02 per step) with no reader and no clear. Dead state that grows with every axis step. |
| 5 | M | `IC_Economy_Effects.txt:363-369` | Axis modifiers only applied when x<19. x=19 and x≥29 get none. |
| 6 | M | `IC_Economy_Effects.txt:443-560` | No startup branches for x=27 (drug cartel) and x=28 (war economy); systems exist only as triggers and map colours. |
| 7 | M | `IC_Economy_Effects.txt:606-625, 632-651` vs `:626-631` | Inconsistent conversion: rentier and petrostate skip `startup_economics`; normal-axis does not. |
| 8 | M | `IC_Economy_Effects.txt:36, 81, 203, 245` | `consumer_goods_need` +0.001 on planned vs -0.01 on market (asymmetric 10x). Probable typo `[INFERENCE]`. |
| 9 | M | `common/scripted_effects/IC_Econ_2024.txt:965-1025` | Non-exclusive `if` blocks: civ and OFP multipliers stack (x 13-18 gets 2.625 / 3.135) `[INFERENCE]`. Balance red flag. |
| 10 | M | `common/map_modes/cwic_map_mode.txt:6550-6739`; localisation (see section 2a) | `economic_z_axis` read, not written in searched paths. 9 system colours and labels may never show. |
| 11 | M | `common/decisions/IC_Financial_Decisions.txt:36, 65, 93` | `ai_will_do = factor 1` on all three conversions, no `is_ai`/treasury gate. AI could convert systems at will. Combined with S1 (no AI treasury loop). |
| 12 | M | `IC_Financial_Decisions.txt:9-40, 41-69, 70-95`; `_Decolonization.txt:156-1216` | Decision gates (`available`) are bypassed by direct `conversion_to_rentier` calls in events (no check on development or Rentier_Economic_Check). |
| 13 | M | `IC_Economic_Investments.txt:149-155` (and 16 others) | `ai_will_do` is `currentMoney > 500` → +50 across all 64 investment tiers; AI can buy every tier when rich. No cap on total spend per month. |
| 14 | M | `IC_Economic_Investments.txt:1-1624` | Duplication: 16 near-identical blocks differing only by numbers and budget name; `IC_State_Decisions_Effect.txt:533-735` repeats the same else-if ladder per pop category. Maintenance risk. |
| 15 | L | `IC_Economic_Investments.txt:1459-1623` | Four `*_locked` decisions subtract 1 currentMoney on click; looks like a UI placeholder `[INFERENCE]`. |
| 16 | L | `IC_Econ_2024.txt:2391-2458` vs `:965-1025` | Threshold inconsistency: market multipliers use 6/12/18; nationalization base_axis uses 13/17/21/25; market_relief uses 6/7/12. Not a bug, but hard to reason about. |
| 17 | L | `common/scripted_effects/IC_Economy_Effects.txt:159, 198` and `policy_focus_effects.txt:7989` | `economic_x_axis` unbounded; `x/3.5` gives unlimited welfare base for large x. |
| 18 | L | `common/scripted_effects/CWIC_GDR_Card_Game_Effects.txt:1564` | `add_to_variable = { currentMoney = -0.05 }` inside a step effect; tiny but unusual. |

---

## 6. Open questions

1. Who writes `economic_z_axis`? Check `national_focus/` (path not present in the search root I used) and `common/interface`.
2. Does `full_upgrade_estimate_regen` (called from every investment) run on a schedule that refunds leftovers each month (`IC_flagbuildings_category.txt:133`)? Determines the real treasury cost of investments.
3. Are `average_development`, `Rentier_Economic_Check`, and `oilExport` defined and set anywhere? Not verified.
4. Is the `economic_modifier_war_reparations_exp` stale-value behaviour intended? Check whether it is zeroed elsewhere.
5. Does the x=19 gap and x≥29 gap matter? Check whether any writer sets x=19 or x≥29 (`national_focus/` search not complete).
6. `CWIC_Econ_Change_scripted_effects.txt:63-182` was not read in full.
7. `IC_Econ_2024.txt` was grepped for axis readers only; its GDP formula was not traced end to end.
8. Is `category_upgrade_*_locked` intended as a placeholder? Its `visible` logic (1459-1623) was not read.
9. Do the `global.UPC_pop*dev3` values exist? `on_startup_defines.txt` shows dev1/dev2/dev4 setup; dev3 entries not checked.
