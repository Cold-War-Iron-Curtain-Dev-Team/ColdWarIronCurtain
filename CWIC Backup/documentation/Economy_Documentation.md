# CWIC Economy Documentation

Reference for the Cold War: Iron Curtain economy: treasury, GDP, taxes, spending, debt, inflation,
resources, consumer goods, trade, economic systems, crises, foreign capital and the Finance Hub GUI.
- Status: NOT verified against a specific build. The commit hash and check date in the earlier draft were invented and are removed.
- Paths are relative to `Cold War Iron Curtain/` unless stated. `effects/` means `common/scripted_effects/`.
- Line numbers are approximate where marked "~" and otherwise as read during the audit and scout passes. Prefer the effect name: line numbers drift.
- `[unverified]` means the claim was not confirmed in source. `[inference]` means it was read from source but
  not observed in game.

This file replaces `LogDocs/Economy_Rework/Economy_System_Overview.md`, the 17 slice audits in
`LogDocs/Economy_Rework/audit/` and `CWIC Backup/documentation/Finance_Hub_Documentation.md`. Those notes
describe the economy as of 2026-10-27. Most of what they audited was rewritten in November:

| Date | Change | Key commits |
|---|---|---|
| 2026-11-02 | Pass 1 fixes; every country (AI included) runs the same monthly pulse; yearly tick added | `39d4bfc399`, `3bb5bd07f3` |
| 2026-11-02 | Content API (`cwic_take_loan`, `cwic_set_*_level`, ...) and codemods of content onto it | `45943a3e3c` |
| 2026-11-03 | Pass 2: new state-output, HDI and budget core; principal-only loans with monthly interest | `b40c4abdc7`, `342fcdc548`, `daf737bd7f` |
| 2026-11-04 | AI state pass every 3rd month; debt follows GDP on territory change; import bill cap | `ea1acbfe82`, `d7e3b07262` |
| 2026-11-10..13 | Raw resources trade through native HOI4 deals, settled in money at a world price | `7417efe7d5`, `a0f73a2ced`, `20ac54b474` |
| 2026-11-15..17 | Consumer goods become four native trade resources | `81e7c39e7e`, `ca0ec443be`, `19eebf578e` |
| 2026-11-24 | `cwic_action_convert_normal_axis` picks axes by ruling ideology | `7df7eb7118` |

Design intent for the rework is in `docs/economy_map/` (`PLAN.md`, `MODEL.md`, `API.md`). Where those
files and the code disagree, this document follows the code; section 11 lists the gaps.

---

## Contents

1. Architecture and cadence
2. Key variables and units
3. GDP, state output and HDI
4. Revenue
5. Spending
6. Treasury and the monthly balance
7. Debt, loans, credit and default
8. Inflation, FX, capital controls, black market
9. Resources, industrial pulse, food, electricity, pollution
10. Consumer goods
11. Trade
12. Tax and policy ladders, sliders, AI fiscal rule
13. Economic systems (axis grid)
14. Economic investments
15. Economic crises
16. Foreign capital (MNC)
17. Comecon (economy hooks only)
18. Finance Hub GUI
19. Content API
20. Modifier reference
21. Known issues and status of every audit finding
22. Testing status

---

## 1. Architecture and cadence

The economy is scripted: per-country variables recomputed by scripted effects. Vanilla buildings,
resources, trade deals and population are inputs. Money, GDP, taxes, debt, inflation and crises are
variables.

### 1.1 Monthly

`common/on_actions/00_on_actions.txt`, `on_monthly`, for every country:

1. If VTC is gone, the global tick runs once (flag `cwic_global_monthly_tick_done`, 27 days). Normally
   `on_monthly_VTC` runs `cwic_global_monthly_tick` (`effects/IC_scripted_effects.txt:19816`): MNC
   rollover, auto-invest and invite processing, `ic_pulse_monthly` for every country, federations,
   cold-war counters, and `cwic_trade_manual_default` for human players.
2. SOV only: `COMECON_monthly_tick`.
3. `monthly_education_pulse` (skipped with global flag `cwic_debug_skip_education`).
4. `ic_financial_monthly_pulse` (skipped with global flag `cwic_debug_skip_econ`). **No `is_ai` gate**: AI
   and players run the same pulse. Insurgents run it too.
5. UNS only: `treaty_lifecycle_monthly`, `credit_calculation_work`, `cwic_sync_trade_embargoes`,
   `cwic_update_world_resource_market`, `cwic_update_world_cg_market`.
6. Players only: month counter, year-over-year snapshots (`last_year_gdp`, `yoy_change_*`), finance graph
   samples (section 18.6).

`ic_financial_monthly_pulse` (`effects/IC_scripted_effects.txt:2`):

```
income_effect                       # GDP, tax, consumer goods, spending, trade, balance, debt service, cascade
if cwic_econ_skip = 0:              # AI skip months skip this block (1.3)
    reset *_resource_bonus; resource_bonus_script; industrial_pulse
monthly_borrowing_and_interest_pulse   # refresh lender rates and caps
```

`income_effect` (`effects/IncomeGenerator.txt:278`), in order:

1. `cwic_process_war_reparations` (`effects/War_Reparation_Effects.txt:101`).
2. `gdp_calculation_effect` (`effects/IC_Econ_2024.txt:531`): resets `IncomeTotal`, computes GDP and HDI
   (section 3), runs `credit_calculation_work` and `set_interest_rates`.
3. `cwic_budget_tax_revenue` (`IncomeGenerator.txt:1873`): tax into `IncomeTotal` (section 4).
4. `cwic_cg_monthly_master_tick` (`effects/IC_Consumer_Goods.txt:1621`, section 10).
5. Capital-control and FX display flags; `default_social_policies` once per country.
6. `military_expenditure`, `flag_building_macro`, `interest_rate_calc`, `domestic_bond_calc`,
   `mercenary_calc`, `social_indices`; social `calc_*_expenditure` effects.
7. Tourism, `ic_calc_trade_exports`, `custom_income`, `resource_income`,
   `consumer_goods_export_income` into `IncomeTotal`.
8. `ic_calc_trade_imports`; subtract `resource_cost`, `custom_expenses`, insurgency funding,
   `total_expenses`; add `modifier@war_reperations`; Soviet subsidy.
9. `currentMoney += IncomeTotal`; AI in deficit gets `cwic_ai_trade_austerity`.
10. `pulse_deficit = -currentMoney` if negative; `IncomeCheck = IncomeTotal`.
11. Debt loop: installments and interest (section 7.4).
12. Default/austerity checks and the automatic borrowing cascade when `pulse_deficit > currentMoney`.
13. Tail (`IncomeGenerator.txt:~1240-1305`): building totals, `cwic_capital_controls_monthly_effects`,
    `cwic_black_market_monthly_update`, `cwic_inflation_monthly_pulse`, corporate and budget risk indices,
    MNC sector/elite/backlash effects, and `CWIC_evaluate_national_crises` once the global flag
    `Crisis_Check_Evaluation_1` is set.

`food_pulse.1` (`events/IC_Food_Pulse.txt`) is fired one day after `industrial_pulse` to settle the food
balance and take the food and electricity graph samples.

### 1.2 Daily

`on_daily`: `cwic_update_trade_civ_neutrality` for countries holding the `cwic_trade_civ_neutrality`
dynamic modifier (section 11.6).

### 1.3 AI state-pass rotation

`gdp_calculation_effect` (`IC_Econ_2024.txt:557-575`), only for AI and only after 1949.7.1:

- `cwic_econ_tick` starts at `id mod 3` and counts to 3. On 2 months in 3 `cwic_econ_skip = 1`: each owned
  state adds its cached `cwic_state_output` and `State_HDI_1000` instead of recomputing, and
  `resource_bonus_script`, `industrial_pulse` and the separatism rollup are skipped.
- On the third month the full state pass runs with `cwic_econ_steps = 3`, so step-based drifts
  (separatism) move three months at once.
- The cache is summed only when the state's `cwic_gdp_owner_month` matches the country, so a state that
  changed owner on a skip month contributes nothing until the next full pass.
- Tax, spending, trade settlement and debt still run every month on the cached GDP.

### 1.4 Yearly

HOI4 has no `on_yearly`. `common/on_actions/CWIC_Economy_Log_on_actions.txt` runs once per country per
game year from `on_monthly`, guarded by `cwic_last_yearly_tick = global.year`:

- `cwic_update_yearly_gdp_growth` (`effects/CWIC_GDP_Growth_Effects.txt:93`).
- `cwic_apply_catch_up_growth` (`IC_Econ_2024.txt:1569`), section 3.4.
- `cwic_ai_fiscal_rule` for AI countries (section 12.5).
- USA SDI spending check.
- Log lines `CWIC_ECON`, `CWIC_BUDGET`, `CWIC_REV` in `game.log`, read by `_tools/economy_check/check_economy.py`.

### 1.5 Startup

- `on_startup_defines.txt` sets globals (`GlobalCredit 0.45`, `GlobalDebit 0.28`, `GlobalEdictDebit 0.44`,
  `GlobalTaxCredit 1.0`, `UPC_pop*` upgrade costs, world prices), runs `industrial_pulse` and
  `starting_policies` for every country (`cwic_clear_insurgent_conventional_policies` for insurgents),
  and fires `tutorial.2000` one hour later.
- `tutorial.2000` (`events/tutorial.txt:22`) adds the `resource_consumption`, `cwic_market_refunds` and
  `cwic_trade_civ_neutrality` dynamic modifiers, runs `cwic_seed_conventional_economy`, and then
  `convert_to_war_economy` for countries with `active_insurgency`, otherwise
  `cwic_setup_postwar_soviet_reparations`.
- `cwic_seed_conventional_economy` (`effects/IC_Economy_Effects.txt:779`): starting inflation, drift vars,
  `cwic_set_start_productivity` (generated table, `effects/CWIC_Start_Productivity_Generated.txt:191`),
  `income_effect`, resource and industrial pulses, starting money, FX balance, starting debt (only before
  1949.7.1), a consumer-goods tick, GDP record clean-up, a crisis evaluation and a final GDP pass.

### 1.6 Insurgents

- At start they get conventional seeding, then War Economy (`economic_x_axis = 28`), and every policy level
  set to 0 by `cwic_clear_insurgent_conventional_policies` (`effects/CWIC_Insurgency_Economy_Effects.txt:1`).
- They run the normal monthly pulse. Nothing zeroes their money or debt.
- `cwic_exit_insurgency_to_normal_economy` (`IC_Economy_Effects.txt:800`) only clears `active_insurgency`.
  Callers: `Indochina_Theater_Effects.txt:4112`, `MLA_scripted_effects.txt:552, 568, 836`. The exit leaves
  the War Economy axis and level-0 policies in place; the caller must set its own axes
  (`cwic_set_economic_axes`) and policy levels (`cwic_set_*_level`).
- `VIE_Effects.txt:1168` calls `cwic_seed_conventional_economy` directly for the VIE takeover.
- The Finance Hub no longer has an insurgent view: `Finance_Tab.txt` has no `active_insurgency` check.

---

## 2. Key variables and units

Units confirmed by the team on 2026-11-02 (`docs/economy_map/PLAN.md` §2.4).

| Variable | Scope | Unit / meaning | Written by |
|---|---|---|---|
| `currentMoney` | country | Treasury, billions | `income_effect`, debt loop, cascade, `cwic_change_money` |
| `grossdomesticproduct` | country | GDP, billions per year (Σ state output / 10) | `gdp_calculation_effect` |
| `cwic_gdp_monthly` | country | GDP / 12; base of every GDP-share line | `gdp_calculation_effect` |
| `grossdomesticproductcapita` | country | GDP per head; USA 1949 ≈ 42.04 | `calculate_gdp_per_capita` |
| `National_HDI` / `State_HDI_1000` | country / state | 0-1 / per mille | `gdp_calculation_effect`, `calculate_state_hdi` |
| `IncomeTotal` | country | Net cash flow this month before debt service | `income_effect` (reset in `gdp_calculation_effect`) |
| `IncomeCheck`, `IncomePlannerCheck` | country | Copy of `IncomeTotal`; read by AI building strategies and map mode | `income_effect` |
| `display_balance`, `cwic_monthly_balance` | country | `IncomeCheck − currentDebtPayments` | `income_effect` |
| `pulse_deficit` | country | `-currentMoney` when negative, else 0 | `income_effect` |
| `currentDebt` | country | Σ outstanding principal | debt loop |
| `currentDebtPayments` | country | This month's installments + interest | debt loop |
| `cwic_interest_payments` | country | This month's interest only | debt loop |
| `Credit_Rating` | country | 1-10 | `process_credit_rating` |
| `Interest_Rate` | country | Percent per year (1.01-1.5 from the rating table, plus premiums) | `set_interest_rates` |
| `CWIC_inflation_mom` | country | Inflation, fraction per month | `cwic_inflation_monthly_pulse` |
| `CorruptionLevel` | country | 0-1 | `cwic_change_corruption` (clamped) and content |
| `economic_x_axis`, `economic_y_axis`, `economic_z_axis` | country | System grid (section 13) | `step_towards_*`, `convert_to_*`, `cwic_set_economic_axes` |
| `*_level_value` | country | Policy level, source of truth for each ladder | policy setters |
| `trade_automation` | country | 1 manual, 2 automated (players only) | `cwic_trade_manual_default`, Trade tab |

Prices: world prices are in money per 1000 units (`ic_calc_trade_exports` divides by 1000).

---

## 3. GDP, state output and HDI

### 3.1 `gdp_calculation_effect` (`IC_Econ_2024.txt:531`)

1. `cwic_set_year_offset`, reset `National_HDI`, GDP, sectors, `IncomeTotal`, `IncomeCheck`.
2. Market multipliers by `economic_x_axis`: `cwic_mciv`/`cwic_mofp` = 1.75/1.9, or 1.5/1.65 if x < 14,
   or 1.25/1.35 if x < 7. Exclusive bands (the October "stacking" bug is gone).
3. AI rotation (1.3).
4. Per owned state: `income_effect_every_owned_scope` (separatism, napalm/agent-orange decay, building
   totals), `cwic_calc_state_output`, `calculate_state_hdi` (`IC_Econ_2024.txt:1114`); or the cached sums on
   skip months.
5. `grossdomesticproduct /= 10`, `National_HDI /= 1000`, `cwic_gdp_monthly = GDP / 12`.
6. `CWIC_econ_drift_vars`, `cwic_begin_gdp_growth_pass`, `credit_calculation_work`, `set_interest_rates`.

### 3.2 State output (`cwic_calc_state_output`, `IC_Econ_2024.txt:482`)

```
R       = resource@oil + aluminium + tungsten + steel + chromium + coal
wf      = state_population_k × 0.7275
jobs    = (27·ind + 9.45·arms + 9.45·dock + 56.7·office + 5.67·steel_f + 4.05·tungsten_f + 4.05·R) × state_development
          + 14.175·agri + 14.175·resource@rubber
E       = min(1, wf / jobs)              (1 when jobs = 0)
idle    = max(0, wf − jobs)
base    = 1.2524744 (dev < 3) | 3.1739341 (dev < 5) | 4.2 (dev < 6) | 5.5
Y       = (3·literate + 3·primary + 6·high_school + 4·college) / 100      (years of schooling)
pi      = 1.1^Y × base × (1 + 0.05 × (state_infrastructure + infrastructure + water_infrastructure))
bld     = 2·ind·mciv + 7·office·mofp + 1.25·arms + 2.5·dock + 1.75·steel_f + 1.75·tungsten_f
          + 3·agri + 3·resource@rubber + 0.02005722·wf + 0.03·R
output  = pi × E × bld × cwic_start_productivity + 0.002 × idle
```

- **Rubber is food** in this mod: farms and rubber deposits make the food sector.
- Sectors (`cwic_add_state_sectors`): civilian, service, mic (arms + dockyards), mill (steel and tungsten
  factories), rgo (resources), food. They feed the Finance sector pie.
- `cwic_start_productivity` is a per-country start factor generated from a simulator so 1949 GDP matches
  the hybrid anchor (`MODEL.md` §0). It is raised yearly by catch-up growth.
- Not in the formula: technology income bonuses, `productivity_factor`, `workforce_ratio`,
  `CWIC_productivity_mult`, `CWIC_bm_productivity_penalty`, electricity shortage. See section 21.2.

### 3.3 HDI

`calculate_state_hdi` (`IC_Econ_2024.txt:1114`) per state; `National_HDI` is the mean of state values.
Formula intent: income from log GDP per head, education from the four shares, health from a life-expectancy
fit (`MODEL.md` §2). [unverified: body not re-read for this document.]

### 3.4 Growth

- Monthly: `cwic_track_state_gdp_for_growth` (`CWIC_GDP_Growth_Effects.txt:30`) compares each state with its
  remembered owner and output. Growth is measured only on states held in both periods; gaining or losing
  territory is not counted as growth. `cwic_store_gdp_and_monthly_growth` annualises it
  (`(now − last) / last × 120000`, percent × 100). Skipped when last month's kept GDP ≤ 0.1.
- When a state's owner changes, the same effect calls `cwic_transfer_state_debt` (section 7.7) and, if the
  state count dropped, sets `CWIC_CRISIS_GRACE` for 180 days (`CWIC_GDP_Growth_Effects.txt:89`).
- Yearly: `cwic_update_yearly_gdp_growth` rolls the baseline on retained states.
- Catch-up (`cwic_apply_catch_up_growth`): USA sets `global.cwic_ref_gdp_pc`. A country with HDI > 0.45
  below that reference multiplies `cwic_start_productivity` by
  `1 + clamp(0.04 × min(ln(ref/gdp_pc), 4) × min((HDI − 0.45)/0.15, 1) × (0.5 if x < 7), 0, 0.10)`.

---

## 4. Revenue

### 4.1 Tax (`cwic_budget_tax_revenue`, `IncomeGenerator.txt:1873`)

```
cap    = clamp(0.45 + 0.55 × (National_HDI − 0.30) / 0.40, 0.45, 1)     fiscal capacity
sysrev = 1 + 0.8 × max(0, 7 − economic_x_axis) / 7                      state-enterprise revenue
eta    = (1 − 0.5·CorruptionLevel) × (1 − CWIC_bm_tax_leak_mult) × (1 + modifier@modifier_tax_efficiacy) × cap × sysrev
base   = cwic_gdp_monthly × 0.05 × eta
corp   = corporate_tax_level_value × 0.20 × base
pers   = (0.2625·lower_tax_level_value + 0.15·lower_middle_tax_level_value + 0.15·upper_tax_level_value) × base
IncomeTotal += corp + pers
```

- Each ladder level is 5 points of rate (`0.05 × level`); the constants weight each class's slice of GDP.
- Outputs: `cwic_tax_*`, `ui_income_tax`, `total_personal_income_tax`, `total_corporate_tax`,
  `effective_tax_rate = eta` (shown as "Collection Efficiency"), `actual_tax_rate_adjusted`.
- `eta` has no clamp.
- Corruption costs revenue only through `eta`. The old separate corruption expense line (`CorruptLoss`) is gone.
  `CorruptPolicyExcess = 0.2 × CorruptionLevel` still adds a corruption markup to military costs.
- The Laffer / tax-avoidance curve (`IC_tax_avoidance_line.txt`, `laffer_curve_*.txt`) is deleted.

### 4.2 Other income

| Line | Formula / source |
|---|---|
| Tourism | `tourism_infrastructure_total × GlobalCredit (0.45) × (1 + commerce_credit_factor_difference) × stability / 12` |
| Raw-resource exports | `resource_income`, section 11.4 |
| Consumer-goods exports | `consumer_goods_export_income`, section 11.4 |
| `custom_income` | Standing monthly income from content. Never reset. Only writer: `Trees for 0.35/PRC_50s_New.txt` (PRC). |
| War reparations | `modifier@war_reperations` (`0_dynamic_modifiers.txt:443` maps it to `economic_modifier_war_reparations`): negative for payers, positive for SOV. One channel only. |
| Soviet subsidy | Received by countries with flag `Soviet_Subsidies` (section 5.4). |

---

## 5. Spending

### 5.1 Social lines (`IC_Econ_2024.txt:694-731`)

`line = cwic_gdp_monthly × max(modifier@<line>_spending_modifier, 0.001) × κ`

| Line | Effect | κ |
|---|---|---|
| Welfare | `calc_welfare_expenditure` | 0.0495 |
| Healthcare | `calc_healthcare_expenditure` | 0.033 |
| Policing ("CPI" = Civil Protection and Intelligence) | `calc_policing_expenditure` | 0.011, plus `black_ops_expedntiture` |
| Education | `calc_education_expenditure` | 0.033 |
| Public services | `calc_public_services_expenditure` | 0.022 |

The spending modifier comes from the policy ladder idea (0.001 at level 0, 0.05 × level up to 1.0 at
level 20) plus other sources (crisis ideas, consumer-goods pressure, pollution, MNC). Each modifier is
read once.

### 5.2 Military (`military_expenditure`, `IncomeGenerator.txt:1307`)

1. Unit upkeep (`IC_Econ_2024.txt:734-1060`):
   - Land: weighted battalion counts (0.005/0.01/0.02/0.025/0.03 by type bucket) × 0.5 ×
     `army_spending_modifier` × `cwic_land_price_factor` (= 0.3 + 0.7 × wage factor, where wage factor =
     clamp(GDP per head / 42.04, 0.05, 1), `cwic_calc_wage_price_factor`).
   - Air: `average_development × deployed airforce manpower (k) × 0.05` + tier sums (0.01/0.025/0.05/0.075),
     × 0.5 × `air_spending_modifier`.
   - Navy: `average_development × deployed navy manpower (k) × 4 / 10000` + ship tiers
     (0.05/0.1/0.15/0.25), × 0.5 × `navy_spending_modifier`. Clamped ≥ 0.
   - Strategic: `(average_development + Total_Nuclear_Reactors) × 750` + missiles (SRBM 5, IRBM 30,
     ICBM 75, SLBM 20) + `num_of_nukes × 10`, / 10000 × `strategic_forces_spending_modifier`.
   - Space (if `Space_Program_Active`): `GDP / 5 × space_spending_modifier`, also added to `space_budget`.
2. Land, navy and air upkeep × `GlobalDebit` (0.28).
3. GDP-share lines: land += `cwic_gdp_monthly × (0.02 × army_mod + 0.01 × strategic_mod)`;
   navy += `cwic_gdp_monthly × 0.01 × navy_mod`; air += `cwic_gdp_monthly × 0.01 × air_mod`.
4. Military subsidies: 25% of each branch is moved to the countries in `military_subsidies` and their
   influence. Corruption markup: each branch × `(1 + CorruptPolicyExcess)`.
5. Monthly divisors: land / 1.5, navy / 2.5, air / 2.25, strategic / 1. They also divide the GDP-share part.
6. `military_total_exp = mil_gui_total + navy_gui_total + af_gui_total + sf_gui_total` (sf includes space).

### 5.3 Expense totals

- `total_expenses = military_total_exp + welfare + policing + education + healthcare + public_services`,
  subtracted from `IncomeTotal`.
- `totalexp` is a display aggregate (military + public + policing + education + custom expenses + imports);
  read by the Finance sector pie (`pie_chart_scripted_effects.txt`).
- `custom_expenses`: standing monthly charge from content (SOV_Ustinov, SOV_Kaganovich, 50s_SRT,
  stalintreereworknew, SovietUnion_Focus_Events). Never reset; charged every month.
- Insurgency funding: `paigc + los + vie + vin + mpla + unita + fnla _funding`, computed and charged in the
  same month.

### 5.4 Soviet subsidy

If the receiver has `Soviet_Subsidies` (set by `VIN_50s.txt`):
`subsidiy_base = 0.25 × (land_army + welfare + policing + education + healthcare + public_services expenditure)`.
`var:subsidy_payer.currentMoney −= base`, receiver `IncomeTotal += base`. `subsidy_payer` defaults to
`SOV.id`; content may set it.

---

## 6. Treasury and the monthly balance

- `currentMoney += IncomeTotal` once a month, then debt service is paid from `currentMoney`.
- A negative treasury always borrows through the automatic cascade (section 7.5); the IMF stand-in (GER) is
  the uncapped last resort, so money does not stay negative.
- `cwic_change_money` (`effects/IC_Economic_Scripted_Effects.txt:1037`) is the only supported way for
  content to add or spend money. Input `money_change_temp` in billions (negative = spend). A spend beyond the
  treasury borrows the rest through a spending cascade (section 7.5) with tooltips. Amounts are fixed, not
  GDP-scaled (decision D3, 2026-11-02).
- `cwic_ai_trade_austerity` (`0_dynamic_modifiers.txt:262`): added to an AI with `IncomeTotal < 0`, removed
  when `IncomeTotal > 0`. `min_export = 0.15`, `trade_opinion_factor = −0.5`: the AI sells more raw
  resources and gets less credit from partners.

---

## 7. Debt, loans, credit and default

File: `effects/IC_Loans_and_Interest_Rate_Effects.txt` unless stated.

### 7.1 Ledger

Five parallel arrays per borrower, one entry per loan:

| Array | Meaning |
|---|---|
| `debtTotalsArray` | Outstanding principal |
| `debtPaymentArray` | Monthly principal installment |
| `debtInterestArray` | Annual rate as a fraction (`rate% / 100`) |
| `debtOwnerArray` | Lender country (THIS for domestic, GER for the IMF stand-in) |
| `debtOwnerDomesticStatusArray` | Lender id (7.2) |

`currentDebt = Σ positive debtTotalsArray`. `domesticTotalDebt` tracks lender-2 principal.
Paid-off entries are zeroed, not removed.

### 7.2 Lenders

| Id | Lender | Tag | Cap (`*MaxBorrowable`) | Rate |
|---|---|---|---|---|
| 1 | Domestic Reserve | own | GDP × 0.5 | `Interest_Rate × 0.8` (`set_reserve_rate`) |
| 2 | Domestic Commercial (bond pool) | own | `available_liquidity` | `Interest_Rate`, × 1.2, × 1.44 by term |
| 3 | BNP Paris | BNP | GDP × `max_borrowable_modifier` | `Interest_Rate × 1.25` |
| 4 | Barclays | BRC | same | × 1.25 |
| 5 | Chiyoda-Mitsubishi | CHY | same | × 1.3 |
| 6 | Credit Suisse | SKA | same | × 2.25 |
| 7 | Deutsche | DBA | same | × 1.6 |
| 8 | JP Morgan | JPM | same | × 1.25 |
| 9 | IMF (stand-in tag GER) | GER | GDP × 1.5, uncapped as last resort | 7/9/12/15 by term |
| 10 | World Bank | WBK | GDP × 0.33 | 1.35-3.37 by term (5-35 years) |
| 11 | A country (`cwic_take_loan` only) | any | lender's money | given by content |

- `set_international_commercial_rates` and `set_reserve_rate` recompute rates and static caps from GDP
  every time they run (from `interest_rate_calc` in `income_effect` and from
  `monthly_borrowing_and_interest_pulse`). Each run adds the change in the static cap to the live
  `Current*MaxBorrowable`, so live caps follow GDP growth and shrink when GDP falls. The second run in a
  month adds 0.
- Drawing a loan lowers the live cap (`loan_set_assigning_borrowable`). Each repayment restores it
  (`loan_payoff_change_to_liquidity`, `:1781`), branch per lender id 1-10.
- Live caps are seeded in `tutorial.2000`. `Borrowing_Button_click` copies static into live caps only when
  every live cap is 0 (a first-open initialiser).
- Domestic bond pool (`domestic_bond_calc`, `:185`): `outcrowding_limit = 10 × office_park_total ×
  (1 + office_park_income_bonus)`. Below the limit, liquidity regrows by 6.5% / 5% / 3.5% of the limit a
  month (limit < 100 / < 500 / larger). Floor 1.

### 7.3 Loan pricing

`automatic_loan_setting` (`:1577`) and `calculate_loan_details` (`:1542`):

```
principal   = pulse_deficit (automatic) or purchase_amount (player)
rate        = currentInterestRateCalc^current_index / 100          stored in debtInterestArray
years       = purchase_length^current_index (automatic loans: at least 10)
installment = principal / (years × 12)                              stored in debtPaymentArray
first month cost shown = installment + principal × rate / 12
```

`cwic_take_loan` with lender 11 uses simple interest to size the installment:
`total = P × (1 + rate/100 × years)`, `installment = total / (years × 12)` (`IC_Financial_Scripted_Effects_for_Content.txt:110`).
The monthly loop then also charges interest on the outstanding principal [inference: country loans pay
interest twice; see 21.2].

### 7.4 Monthly debt service (`income_effect`, `IncomeGenerator.txt:~575-660`)

For each loan with principal > 0:
1. installment = min(installment, principal); principal −= installment; `currentMoney −= installment`.
2. interest = principal (after the installment) × rate / 12; `currentMoney −= interest`.
3. `currentDebtPayments += installment + interest`; `cwic_interest_payments += interest`.
4. The installment is credited to the lender's `currentMoney`, except own-country and GER loans; GER
   repayments also reduce `influence_array_val` for the borrower.
5. `loan_payoff_change_to_liquidity` restores the lender's live cap.

### 7.5 Borrowing cascades

**Automatic (monthly, `IncomeGenerator.txt:~819-1150`)**, when `pulse_deficit > currentMoney`, first match:
Reserve → domestic bond pool → World Bank → JPM → BNP → Barclays → Chiyoda-Mitsubishi → Deutsche →
Credit Suisse → IMF/GER (else). Each gate is `Current<Lender>MaxBorrowable > pulse_deficit`.

**Spending (`cwic_change_money`, `IC_Economic_Scripted_Effects.txt:1037-1880`)**: same order, but gated on
the static `*MaxBorrowable` caps, and the result goes through `automatic_loan_setting_spending`.

**Player (Finance Hub Borrowing page)**: pick a lender and term; `confirm_loan_purchase_click` records the
loan and calls `loan_set_assigning_borrowable`; `pay_off_loan_click` repays a loan from money.

### 7.6 Credit rating and interest rate

- `credit_calculation_work` (`:255`) → `process_credit_rating` (`:312`). USA, UNS, VTC, SOV and ENG are locked
  at 10. Others accumulate `Credit_Progress` from industrial-base tier and debt risk, lose it for money
  printing, sanctions, non-recognition, war, border war, insurgency, surrender progress and capitulation.
  `Credit_Progress > 99` raises the rating (`raise_credit_rating`, progress −100);
  `< 0` with rating ≥ 4 lowers it (`lower_credit_rating`, progress set to 25). Progress is reset to 0 at
  rating 1, rating 9, and rating > 6 with industrial tier < 5.
- Starting ratings (`set_starting_credit_ratings`, `:942`): from National HDI (>0.8 → 9 ... else 3), +1 reserve
  currency, −1 for listed war-damaged and Eastern-bloc tags when > 3, +1 CAN/SWI/SWE, INO 3, VIN 5.
- `set_interest_rates` (`:1086`):

| Rating | 10 | 9 | 8 | 7 | 6 | 5 | 4 | 3 | 2 | 1 |
|---|---|---|---|---|---|---|---|---|---|---|
| `Interest_Rate` (%/yr) | 1.01 | 1.015 | 1.02 | 1.05 | 1.10 | 1.15 | 1.20 | 1.25 | 1.40 | 1.50 |
| `default_multiplier` | unset | 15 | 12 | 10 | 8 | 6 | 4 | 3 | 2 | 1 |
| `austerity_multiplier` | unset | 8 | 6 | 5 | 4 | 3 | 2 | 1 | 0.75 | 0.5 |
| `max_borrowable_modifier` | 0.25 | 0.20 | 0.18 | 0.16 | 0.14 | 0.12 | 0.10 | 0.10 | 0.10 | 0.10 |

  Then × `CWIC_monetary_policy_mult`; × `(1 − 0.10 × CWIC_reserve_trust)` for reserve-currency issuers;
  + inflation premium `2 × CWIC_inflation_mom` (halved and further reduced by trust for reserve issuers);
  × 0.95 for USA or SOV under the oil-pricing global flags. Fallback 1.04 if 0.
  [unverified: multipliers for ratings 5-1 come from the audits; the rate column was re-read.]

### 7.7 Debt follows GDP (`cwic_transfer_state_debt`, `:2195`)

Called from `cwic_track_state_gdp_for_growth` when a state's remembered owner changes. The state's share of
the old owner's pre-loss GDP is moved, loan by loan (same lender, status and rate), to the new owner. The
share is written off when the new owner is at war with the old owner or the old owner has capitulated
(repudiation, decision D10). Uses `save_event_target_as`.

### 7.8 Default and austerity (`IncomeGenerator.txt:~760-820`, `events/Economic_Penalties.txt`)

Only when `pulse_deficit > currentMoney`:

- `defaultCheck = GDP × default_multiplier`, `austerityCheck = GDP × austerity_multiplier`.
- Default if `defaultCheck < currentDebt`, rating < 10, not NLF, no `Recent_Default`: flags `CWIC_DEFAULTED`
  and `CWIC_MARKET_LOCKOUT`, rating −2 (floor 1), inflation +0.010/month, black market +0.10, event
  `CWIC_ECON_PENALTIES.2`.
- `CWIC_ECON_PENALTIES.2` is a restructuring: every loan, `currentDebt`, `currentDebtPayments` and
  `domesticTotalDebt` are halved; welfare, healthcare and services −2, education −1, union −2 through the
  setters; taxes untouched; no building demolition.
- Austerity if `austerityCheck < currentDebt` and no `Recent_Austerity_Measures`: `CWIC_ECON_PENALTIES.1`.
- `Recent_Default` and `Recent_Austerity_Measures` last 1825 days.

---

## 8. Inflation, FX, capital controls, black market

File: `effects/IC_Inflation_Effect.txt` unless stated. Called from the tail of `income_effect`.

### 8.1 Monthly inflation (`cwic_inflation_monthly_pulse`, `:21`)

```
SP  = clamp(cwic_cg_shortage_stability / −0.18, 0, 1)² × 0.006     consumer-goods shortage
FP  = min(pulse_deficit / GDP, 0.20) × 0.030                        deficit
DP  = min(currentDebtPayments / GDP, 0.20) × 0.020                  debt service
TD  = clamp(Interest_Rate − 1, 0, 10) × 0.000833                    tightening (1 point ≈ 1%/yr)
expect = 1 + 0.75 × (1 − clamp(Credit_Rating/10, 0.1, 1))
raw = (SP + FP + DP) × expect + 0.001 − TD + CWIC_inflation_bias_mom,   clamped [−0.02, 0.20]
CWIC_inflation_mom = 0.75 × previous + 0.25 × raw
```

`CWIC_cpi_index *= 1 + CWIC_inflation_mom`. Components are stored as `cwic_infl_sp/fp/dp/td/expect`.

### 8.2 Monetary levers (Finance Hub, section 18.3)

- Money printing: flag `CWIC_money_printing_active` (−1 credit progress a month while on). Bursts
  `cwic_money_print_small/medium/large` (`:528/538/548`): +2/+6/+15 money, inflation +0.0010/+0.0025/+0.0050,
  black market +0.03/+0.06/+0.10, cooldown 2/3/4 months; medium needs inflation < 0.02, large needs
  `currentMoney < 1`; reserve-currency issuers pay 70%.
- Monetary tightening: inflation −0.003, `CWIC_productivity_mult` −0.010, black market +0.02.
- Currency reform: CPI × 0.5, inflation −0.010, bias −0.001, black market −0.20, productivity −0.020,
  24-month cooldown.
- Internationalize currency: needs `CWIC_reserve_candidate`; sets `CWIC_reserve_currency = 1`,
  `CWIC_reserve_trust = 0.5`.

### 8.3 FX regime (`cwic_fx_regime_monthly`, `IC_Economic_Scripted_Effects.txt:981`)

Peg (`CWIC_fx_regime = 1`): inflation −0.0010 a month; reserves drain by
`40 × max(inflation, 0) + 8 × black_market`. If reserves < 1 and inflation > 0.008 the peg breaks: regime 0,
flag `CWIC_fx_pegged_currency_break`, inflation +0.010, black market +0.10, bias +0.001.

### 8.4 Capital and price controls (`cwic_capital_controls_monthly_effects`, `:233`)

Per month while active:

| Control | Inflation | Black market | `CWIC_productivity_mult` |
|---|---|---|---|
| Light capital controls | −0.0005 | +0.01 | −0.002 |
| Heavy capital controls | −0.0015 | +0.03 | −0.006 |
| Basic price controls | −0.0007 | +0.02 | −0.003 |
| Dual FX controls | −0.0010 | +0.03 | −0.008 |

`CWIC_productivity_mult` is clamped to [−0.25, 0]. It is not read by GDP (section 21.2).

### 8.5 Black market (`cwic_black_market_monthly_update`)

`CWIC_black_market_pressure` (0-1) sets tiered penalties (`:444-472`):
`CWIC_bm_tax_leak_mult` 0 / 0.03 / 0.08 / 0.18 / 0.35 (cuts tax `eta`, raises policing and public-services
spending modifiers), `CWIC_bm_stability_penalty` 0 / 0.005 / 0.015 / 0.03 / ..., and
`CWIC_bm_productivity_penalty` 0 / 0.01 / 0.03 / 0.07 / 0.12 (not read by GDP).

---

## 9. Resources, industrial pulse, food, electricity, pollution

### 9.1 Name mapping

| Game resource | Mod meaning | Script names |
|---|---|---|
| `rubber` | Food | `food*`, `rubber_exports`, `FoodBalance*` |
| `tungsten` | Rare earth | `rareEarth*`, `rare_earth_bonus`, `tungsten_exports` |
| `chromium` | Nuclear material | `nuclear_consumption`, `nuclear_resource_bonus` |
| `coal` | Electricity | `electricity_consumption`; coal cannot be traded (`cic = 1000`) |
| `cg_basic`, `cg_durable`, `cg_vehicles`, `cg_electronics` | Consumer goods (section 10) | `cg_*` |

`common/resources/00_resources.txt`: raw resources `cic = 0.125` (8 units per civilian factory), convoys
0.05-0.1; consumer goods `cic` 0.2 (basic) / 0.25, convoys 0.01.

### 9.2 `industrial_pulse` (`effects/IC_Industrial_Pulse.txt:172`)

Per country, skipped on AI skip months:
- Per-building consumption constants (reactor, steel, tungsten, refinery, base) scaled by
  `modifier@electricity_consumption_need` and by technology; DDR `antiquated_industry_*` adds flat
  consumption.
- Outputs `oil_ / steel_ / aluminium_ / rare_earth_ / nuclear_ / electricity_consumption`, applied through
  the `resource_consumption` dynamic modifier (`0_dynamic_modifiers.txt:~236`) as
  `country_resource_cost_*`, together with the `*_resource_bonus` values as `country_resource_*`.
- `industrial_pulse_food_script` (`:620`), per state: farm output from biome and water tables,
  `farm_tech` (+0.15 per agriculture tech), the `agricultural_dysfunction_*` and crop ideas,
  `resourceEfficiencyInfra`, `agricultural_complex_production_bonus` and a pollution multiplier
  `1 − (land/600 × 0.4 + water/600 × 0.2)`.
- Food: `food_consumption × (1 + food_consumption_need)`; `food_penalty = −rubber / food_consumption` when
  rubber < 0; flags `food_famine_extreme` (> 3), `food_famine` (> 0.8), `food_shortages` (> 0.2),
  `food_highprices` (> 0); `food_penalty_political = clamp(−0.1 × penalty, −0.1, 0)` into stability and war
  support. Fires `food_pulse.1` the next day.
- `food_pulse.1` (`events/IC_Food_Pulse.txt`) recomputes `FoodProdTotal`, `ConsumptionTotal` and sets
  `FoodBalanceTotal = resource@rubber`; samples the food and electricity (`resource@coal`) graphs.

### 9.3 Resource efficiency

- `resource_modifier_set_startup` / `resource_idea_effect` (`effects/Resource_Efficiency.txt`): sum
  `resourceEfficiencyGain` from ideas, flags, techs (`excavation_I-VI`), `economic_x_axis = 24` (+0.15) and
  privatisation levels; `resourceEfficiencyInfra = state infrastructure + gain`. Runs at startup.
- `resource_bonus_script` (`effects/Resource_Efficiency_Bonus.txt:1`), monthly per owned state:
  `<res>Bonus = resource@<res> × resourceEfficiencyInfra` into `rare_earth_bonus` (tungsten),
  `aluminium_resource_bonus`, `nuclear_resource_bonus` (chromium), `steel_resource_bonus`; oil uses
  `oilEfficiencyGain + resourceEfficiencyInfra` (see P3 in section 21).

### 9.4 Pollution (`effects/CWIC_Enviroment.txt`)

`calc_pollution_country_factors` (tech factor clamped 0.5-1.5, organic-farming factor) and
`calc_state_pollution_effect` (land and water pollution per state, 0-600, from buildings × population ×
development × tech, plus resource extraction), recovery effects and flags. The pollution health penalty
writes `healthcare_spending_modifier` (`IC_dynamic_modifiers.txt:800`), which is the key spending reads.

---

## 10. Consumer goods

File: `effects/IC_Consumer_Goods.txt`. Four goods (basic, durable, vehicles, electronics) are native trade
resources. Quality tiers 0-5 (electronics 1-5) are unlocked by `cwic_can_produce_*` triggers.

### 10.1 Monthly tick (`cwic_cg_monthly_master_tick`, `:1621`)

1. Heavy-industry priority idea for SOV/Comecon (removed by reform focuses).
2. Strategy reset when `cg_strategy_cd` has expired.
3. `cwic_cg_read_native_supply` (`:1428`): coverage and supplied tier per good from production and imports.
4. `cwic_cg_auto_import` (AI, or players with `trade_automation = 2`), section 11.5.
5. `cwic_calculate_consumer_goods_monthly_demand` (`:424`): demand from core population, HDI and year,
   × the per-country anchor and `global.cg_<good>_demand_scale`.
6. `cwic_cg_monthly_production_and_allotment` (`:694`).
7. `cwic_cg_calibrate_demand` (`:1906`) once per country, when the anchor is unset: anchors demand to
   produced output × 0.92 (0.80 if HDI > 0.499) × home share `clamp(1 − consumer_goods_export_rate, 0.1, 1)`.
8. `cwic_cg_push_native_resources` (`:1554`): writes produced goods into the native resources.
9. `cwic_apply_consumer_goods_pressure_master` (`:3`), 10.3.
10. Black-market pressure +0.01 at severity 3, +0.02 at 4.
11. Random `cwic_cg_crisis.1-4` events (weight lower with basic price controls).

### 10.2 Production

- Civilian factories available: `calculate_civilian_factory_production_total_factories` (`:382`).
- Points = civilian factories × `cg_points_per_factory` (25, hard-set at `:1806`).
- Allotment weights (normalised): basic `0.50 + shortage + (1 − HDI)`, durable `0.20 + shortage + 0.25·HDI`,
  vehicles `0.20 + shortage + 0.35·HDI` × office-park gate, electronics `0.10 + shortage + 0.80·HDI` × office
  gate × rare-earth gate, each × the strategy multiplier: Balanced/Basic (1.6, 1.2, 0.5, 0.5),
  Durables (0.9, 1.6, 1.1, 0.8), Export (0.8, 0.85, 1.8, 1.8).
- Unit cost in points: basic `1.125 + 0.10·tier`, durable `2.00 + 0.20·tier`, vehicles `4.00 + 0.30·tier`,
  electronics `3.00 + 0.35·tier`, × `1 + clamp(cg_*_output_factor, −0.5, 0.5)`.
- Inputs per unit come from monthly pools set from `resource_produced@X + resource_imported@X`
  (`cwic_cg_sync_resource_pools_from_vanilla`, `:1778`): steel, aluminium, oil, coal, tungsten. Output is
  capped by pools, but coal can never cut output below 50%, and `cg_input_floor` sets a floor of 50-100% of
  units over every cap.

### 10.3 Shortage pressure

- Severity per good from coverage, blended into `master_scalar`
  (0.35 basic, 0.20 durable, 0.25 vehicles, 0.20 electronics, cap 1).
- `cwic_cg_shortage_stability = −0.18 × master_scalar` is the inflation input (section 8.1). It is taken
  before the black-market penalty.
- Shortage levels 0-5 per good (thresholds 0.05/0.2/0.4/0.6/0.8; goods with demand < 3 are ignored) give
  `cg_crisis_severity` 0-4. The `cwic_dm_consumer_goods_pressure_master` modifier then uses fixed values per
  severity (stability, political power, productivity, workforce, welfare/policing/public-services spending,
  construction speed, office-park income), minus `CWIC_bm_stability_penalty`, plus the black-market tax leak
  on policing and public services.

### 10.4 Other effects

`cwic_cg_set_strategy` (180-day cooldown), `cwic_cg_grant_aid_shipment` (timed idea), `cwic_add_consumer_industry`
(content adds `cwic_ci_*` to the `cwic_consumer_industry` modifier), `cwic_import_consumer_vehicles`,
`cwic_cg_ensure_office_parks`. Engine AI never evaluates consumer-goods imports
(`common/defines/IC_Defines.lua:192`, `MIN_FACTORIES_TO_WANT_TO_IMPORT`); script does.

---

## 11. Trade

Files: `effects/IC_Trade_Scripted_Effects.txt` (1,399 lines), `effects/IncomeGenerator.txt`
(`ic_calc_trade_exports` `:1737`, `ic_calc_trade_imports`), `common/scripted_guis/Trade_Tab.txt`,
`interface/Trade_Tab.gui`.

### 11.1 Model

- Trade uses native HOI4 deals (`create_import`, the vanilla trade window). The scripted per-partner ledger,
  exporter registry, delivery cuts and `trade.*` events are deleted.
- Importers pay money at the world price. Exporters earn money only for what sells.
- Native civilian-factory costs of trade are neutralised (11.6).
- Trade laws act through `min_export` (free trade 0.7, export focus 0.6, limited exports 0.4, closed 0.2).
  The old per-resource export-rate modifiers are retired.

### 11.2 World prices (`cwic_update_world_resource_market`, `:438`, UNS monthly)

Per raw good:
```
O = Σ resource_exported@X (offers)      S = Σ resource_imported@X (sales)
SoldRatio = clamp(S / max(O, 1), 0, 1)  RefRatio = first non-zero SoldRatio (latched)
MarketPrice = 0.7 × MarketPrice + 0.3 × StartPrice × SoldRatio / RefRatio
clamped [0.3, 5] × StartPrice;  BasePrice = MarketPrice × ShockMult while ShockMonths > 0
```

`cwic_update_world_cg_market` (`:992`) does the same for consumer goods with
`target = StartPrice × clamp(2 × SoldRatio, 0.5, 2)` (electronics start price falls by decade), and steers
`global.cg_<good>_demand_scale` (0.4-1.5) so world demand tracks 92% of world production.

Price shocks `cwic_price_shock_*` (oil crisis ×3 for 12 months, minor ×1.5, glut ×0.6, steel, light metal,
rare earth, nuclear rush, food crisis and glut, plus `_end_*`) exist but have no callers.

### 11.3 Who buys

- AI, and players with `trade_automation = 2`: `cwic_auto_import_native` (`:284`) for each raw good with
  `resource@X < 0`. Sellers: every other country not at war with the buyer and not embargoed, with
  `avail = resource_produced@X × modifier@min_export − resource_exported@X > 0`. It buys from the seller with
  the most available, amount `−resource@X` capped at that seller's availability, one deal per good per month.
- Players with `trade_automation = 1` (the default) buy through the vanilla trade window.
- `cwic_trade_manual_default` sets `trade_automation = 1` for players without the variable (startup and
  global tick).

### 11.4 Settlement (`ic_calc_trade_exports` / `ic_calc_trade_imports`)

```
X_exports      = resource_exported@X × X_SoldRatio × X_BasePrice / 1000
X_imports      = resource_imported@X × X_BasePrice / 1000
resource_income              = Σ raw exports           (into IncomeTotal)
consumer_goods_export_income = Σ CG exports           (into IncomeTotal)
trade_income                 = both (display)
resource_cost = Σ raw imports + Σ CG imports, capped at 0.3 × cwic_gdp_monthly   (subtracted)
```

- `resource_exported@X` is what a country offers, not what it sold. Scaling by `SoldRatio` makes total
  exporter income equal total importer cost for each good.
- The 30% import cap breaks that equality for an importer at the cap: it pays less than its exporters earn.
  `cwic_import_bill_raw` keeps the uncapped bill; `cwic_tb_*` hold the trade-balance display values.
- Market refunds (`cwic_update_market_refunds`, `:72`, and the `cwic_market_refunds` modifier): refund shares
  by trade law (free trade 0.7/0.45/0.25, export focus 0.6/0.3/0.2, limited 0.4/0.15/0.1, closed
  0.2/0.05/0) keep electricity off the market and food and nuclear material near their old export rates.

### 11.5 Consumer-goods imports (`cwic_cg_auto_import`, `:1193`)

AI or `trade_automation = 2`. A good is imported when its monthly balance is below −2 (basic) or −1.5
(others; vehicles and electronics also need readiness). Sellers need `offer_applied × 0.8 − promised` above
4.99 (basic) / 3.99. Largest seller, amount `−balance / 5` (basic) or `/ 4`, booked into `cg_*_promised`;
45-day cooldown per good (`cg_import_cd_<good>`).

### 11.6 Civilian-factory neutrality (`cwic_update_trade_civ_neutrality`, `:839`, daily)

Native imports cost civilian factories. The effect counts traded units
(`0.125 × raw imports + 0.25 × CG durable/vehicles/electronics + 0.2 × CG basic`) and adds or removes
offsite `industrial_complex` buildings so imports cost money only; exporters' trade civs are offset through
`consumer_goods_expected_value`, and resource demand from settlement civs is refunded
(`cwic_tn_res_*`). `industrial_complex` max level was raised for this. `cwic_update_true_factory_display`
drives the true-factory panel for players.

### 11.7 Embargoes

`cwic_sync_trade_embargoes` (`:1`, UNS monthly) walks every pair: `cwic_sync_native_embargo` mirrors the
scripted `trade_embargo_check^TAG` (set by diplomatic actions and history) into native `send_embargo` /
`break_embargo` when allowed, and applies or lifts the `cwic_trade_embargo_block` relation modifier
(events `trade.51` / `trade.52` for players). Embargoed sellers are excluded from auto-import.

### 11.8 Dead or orphaned trade code

- `cwic_trade_tier_calc` (`:695`, subject / EEC / EFTA / Comecon / faction tiers): no callers. Bloc and
  subject trade discounts were removed in `20ac54b474`; `EEC_Currency` and
  `european_free_trade_association` have no trade effect.
- `cwic_price_shock_*`: no callers.
- `global_trade_bonus_adjustment` is still set by ideas (INS, Indonesia, JAP, brazil, New_Ideologies) and its
  loc says it improves exporter ranking, but no script reads it.
- `global.base_shipping_cost_divisor*` (`on_startup_defines.txt`) has no reader. Shipping is not modelled.

---

## 12. Tax and policy ladders, sliders, AI fiscal rule

### 12.1 Ladders

The policy level variable is the source of truth; one idea per family is derived from it.

| Family | Level variable | Ideas | Range | Modifier |
|---|---|---|---|---|
| Lower-class tax | `lower_tax_level_value` | `policy_taxrate_lower_temp_N` (`IC_Laws.txt`) | 1-19 | `tax_rate_lower_class = 0.05·N` |
| Middle-class tax | `lower_middle_tax_level_value` | `policy_taxrate_lower_middle_temp_N` | 1-19 | `tax_rate_middle_class` |
| Corporate tax | `corporate_tax_level_value` | `policy_taxrate_corporate_temp_N` | 1-19 | `tax_rate_corporate` |
| Upper-class tax | `upper_tax_level_value` | `policy_taxrate_temp_N` | 1-19 | `tax_rate_upper_class` |
| Army, navy, air, strategic forces, space | `army_ / navy_ / air_ / strategic_forces_ / space_level_value` | `policy_military/navy/air/special/space_temp_N` (`IC_Policies.txt`) | 0-20 | `*_spending_modifier` |
| Healthcare, welfare, education, public services, policing | `healthcare_ / welfare_ / education_ / public_services_ / policing_level_value` | `policy_healthcare/welfare/education/service/cpi_temp_N` | 0-20 | `*_spending_modifier` |

Tax ideas also carry side modifiers (stability and farm output on lower; war stability and construction on
middle; war support and political power on corporate; office-park income and speed on upper).

The tax modifiers are no longer read by revenue; revenue uses the level variables (section 4.1).

### 12.2 Setters

- Step: `increase_/decrease_<policy>` effects in `effects/policy_focus_effects.txt` (for example
  `lower_tax_rate` `:3556`, `increase_tax_rate` `:3700`, `lower_healthcare_rate` `:2038`). Each moves the level,
  the slider (±8) and the idea.
- Jump: `cwic_set_<policy>_level` with `policy_level_target_temp` (`IC_Financial_Scripted_Effects_for_Content.txt:199+`,
  `cwic_set_tax_level` for the upper ladder).
- Never `add_ideas`/`remove_ideas` an economic `policy_*_temp_N` idea directly; check levels with
  `check_variable`, not `has_idea`.
- Media, religion, union, women, minorities and saga sliders share the idea-ladder framework but are not economic.

### 12.3 Startup

`starting_policies` (`StartingPoliciesBogosort.txt`) and `startup_tax_loops` (`policy_focus_effects.txt:253`,
from `on_startup_defines.txt:1897-1977`) set start levels and slider positions (`rate × 8 + 387`).
`Policy_Startup_Script_2025` sets spending levels by GDP per head; startup education is at least 6.

### 12.4 Player cost

Each slider step costs 15 political power (`Finance_Tab.txt:~2301-2441`, `add_political_power = -15`), enabled by
`tax_ / civilian_ / military_ / space_policy_free_change_enabled` = `has_political_power > 14.99`
(`common/scripted_triggers/IC_spending_level_triggers.txt:458-469`). There is no time lock.

### 12.5 AI fiscal rule (`cwic_ai_fiscal_rule`, `IC_Economic_Scripted_Effects.txt:2185`, yearly)

- Tax cap by system: 16 (x < 7), 14 (x < 13), 12, 8 (x > 19).
- Deficit (`display_balance < 0`): raise upper tax one step if under the cap. At the cap, or debt/GDP > 0.6,
  cut public services, welfare and healthcare (floor 3) and army (floor 2, not at war).
- Surplus above `GDP × 0.0004` and debt/GDP < 0.6: cut upper tax (floor 4); if debt/GDP < 0.3, raise
  education to 10, else welfare to 8, else healthcare to 8.

---

## 13. Economic systems (axis grid)

Files: `effects/IC_Economy_Effects.txt`, `common/scripted_triggers/IC_Economic_System_Triggers.txt`,
`0_dynamic_modifiers.txt` (`economic_system_modifier`, `:~400-436`).

### 13.1 Grid

- `economic_x_axis`: 0 public ... 18 private. `economic_y_axis`: 0 planned ... 18 market.
- Systems on the grid (x band × y band):

| | y < 7 | y < 13 | y < 19 |
|---|---|---|---|
| x < 7 | Central State Planning | Consumer Socialist | Market Socialist |
| x 7-12 | State Capitalist | Keynesian | Social Corporatist |
| x 13-18 | Dirigisme | Orderliberal | Fordist |

- Special systems by exact x: 20 Palace, 21-23 Feudal I-III, 24 Rentier, 25 Petrostate, 26 Colonial,
  27 Drug Cartel, 28 War Economy.
- `economic_z_axis = 1` selects a variant name, description and icon in the map mode and localisation.
  `cwic_set_economic_variant` / `cwic_clear_economic_variant` (`:765`) set it but have no callers.

### 13.2 Steps and modifiers

- `step_towards_planned/market/public/private` (`:34/82/130/172`) move one step, bounded to 0-18, and are
  skipped for special systems (x ≥ 19 for the x steps). Each adds fixed deltas to `economic_modifier_*`
  variables (consumer goods need ±0.01, tax efficiency, tax-avoidance elasticity, welfare, building speeds,
  office-park and agricultural income, research, electricity, ...).
- `economic_system_modifier` maps the `economic_modifier_*` variables onto real modifiers
  (`consumer_goods_factor`, `production_speed_*`, `modifier_tax_efficiacy`, `military_factory_income_bonus`,
  `war_reperations`, ...).
- `startup_economics` (`:360`): adds the dynamic modifier; for x < 19 replays `x − 9` / `y − 9` startup steps;
  for x 20-28 applies that system's fixed set. `clear_current_economic_modifiers` (`:627`) zeroes every
  `economic_modifier_*` and removes the War Economy inflation bias.

### 13.3 Setters

All go through `clear_current_economic_modifiers` → set axes → `startup_economics`:

| Setter | Result | Callers |
|---|---|---|
| `convert_to_normal_axis` (`:668`) | x 12, y 12 (Keynesian) | INO focuses (`INO_LIB_50s.txt:785`, `INO_Natsir_50s.txt:869`, `INO_Soekiman_50s.txt:307`) |
| `cwic_action_convert_normal_axis` (`:685`) | by ruling party: communism/maoism/trotskyism 3/3; socialist 3/15; Christian Democratic 15/10; conservative, Liberal Conservatism, liberal, centrist 15/15; fascism, nationalist, monarchism 10/15; islamism, radical Shiaism, Salafism 10/4; neutrality 15/4; otherwise 10/10 | Finance button and AI decision |
| `convert_to_planned` (`:662`) | x 2, y 1 | `cwic_action_convert_planned` (`on_actions/wars_on_actions.txt:275`) |
| `convert_to_rentier` (`:657`) | x 24 (slow-industry values) | Finance button, `_Decolonization` events, `Malaysia.txt` |
| `convert_to_petrostate` (`:674`) | x 25 | Finance button (visible at x 24) |
| `convert_to_palace`, `convert_to_feudal_1/2/3`, `convert_to_colonial`, `convert_to_drug_cartel` | x 20, 21-23, 26, 27 | content |
| `convert_to_war_economy` (`:758`) | x 28; consumer goods need −0.2; inflation bias +0.001/month | insurgents at start, content |
| `cwic_set_economic_axes` (`IC_Financial_Scripted_Effects_for_Content.txt:185`) | any x/y from `economic_x_target_temp` / `economic_y_target_temp` | MLA, VIE, VIN, WW3, SOV_Stalin, Albania content |

Drug Cartel and War Economy modifier sets are drafts pending dev review.

---

## 14. Economic investments

`common/decisions/IC_Economic_Investments.txt`; spending in `effects/IC_flagbuildings_category.txt`,
`IC_Flag_Building_Effects.txt`, `IC_State_Decisions_Effect.txt`.

- Four budgets: `industrialization_budget`, `development_budget`, `modernization_budget`, `automation_budget`.
  Decisions add 25/100/250/500 to a budget and subtract the same from `currentMoney`
  (`currentMoney >= N` required). Modernize needs a tech list and developed states.
- Each decision flags states whose upgrade cost (`global.UPC_pop*` / `UPC_pop*devK`) is below its own budget;
  the flagged states are upgraded monthly and paid from the budget. Leftover budget carries over.
- `category_upgrade_25/100/250/500` cycle the UI tier. `*_locked` decisions are placeholders.
- AI: `ai_will_do` 0, +50 when `currentMoney > 500`.
- Religious decisions add to budgets directly.

---

## 15. Economic crises

Files: `common/scripted_triggers/CWIC_macro_crisis_scripted_triggers_v2.txt`,
`effects/CWIC_Crisis_Manager_Effects_with_Ideas.txt`, `effects/CWIC_Crisis_GUI_Array_Effects.txt`.

- Evaluated monthly at the end of `income_effect` (`CWIC_evaluate_national_crises`) once
  `Crisis_Check_Evaluation_1` is set (at startup for non-insurgents).
- Types, each with low/medium/high/extreme triggers: fiscal, economic contraction, inflationary,
  deflationary, energy (includes electricity deficit), trade/external shock, financial/credit,
  governance/institutional, crop failure, food security/famine, capital flight, resource curse; plus the
  consumer-goods shortage crisis (`cg_crisis_severity`, section 10.3).
- Fiscal crisis low: defaulted or locked out, or deficit/GDP > 4% with an austerity check, or
  `CWIC_debt_service_gdp_ratio` > 5%. That ratio is annual interest only (`cwic_interest_payments × 12 / GDP`);
  principal installments do not count.
- Buffer (`cwic_crisis_buffer_step`, `:530`): fiscal and contraction crises change level only after 3
  consecutive months on the other side of a threshold; they rise straight to the new level and fall one level
  at a time. With `CWIC_CRISIS_GRACE` (180 days after losing a state; 45 days for VIN during the Indochina
  war) they cannot rise.
- Player help: the active-crisis tooltip ends with `[CWIC_ACTIVE_CRISIS_LEVERS]`
  (`Crisis_GUI_scripted_loc.txt`), one `CWIC_ACTIVE_CRISIS_<crisis>_LEVERS` key per crisis; "Prerequisites for
  Next Severity" keys restate the triggers. Change the triggers and both loc sets together.
- Topbar alert: `interface/CWIC_crisis_alert.gui` (x 807, y 85, left of the RCO alert),
  `common/scripted_guis/CWIC_crisis_alert_gui.txt`. Visible when `CWIC_active_crisis_count > 0` and not
  dismissed. Click opens the Finance Hub on the Economy page; right-click sets `CWIC_crisis_alert_dismissed`.
  `CWIC_crisis_alert_refresh` clears the dismissal when a new crisis starts or summed severity rises.

---

## 16. Foreign capital (MNC)

Files: `effects/CWIC_MNC_Effects.txt`, `effects/CWIC_MNC_Generated_Effects.txt`,
`common/scripted_triggers/cwic_mnc_triggers.txt`, `common/dynamic_modifiers/CWIC_MNC_Signature_Modifiers.txt`,
`events/MNC_Events.txt`, `common/decisions/MNC_Decisions.txt`.

- Global monthly: `cwic_mnc_monthly_rollover`, `cwic_mnc_auto_invest_global`,
  `cwic_mnc_process_invites_global` (from `cwic_global_monthly_tick`). Per country monthly (tail of
  `income_effect`): sector presence, elite capture and state backlash effects.
- Concessions: `cwic_action_authorize_concessions` (`CWIC_MNC_Effects.txt:1238`, 40 PP, flag
  `cwic_allows_foreign_concessions`, −5% stability [unverified: stability value]) and
  `cwic_action_revoke_concessions` (free; +0.5 nationalization pressure, cap 5).
- Five sectors: hydrocarbons, mining, agri, manufacturing, electronics. Each row has a five-segment presence
  track (`CWIC_mnc_presence_tier_<sector>`), a Browse button (picker) and an Any button
  (`Foreign_Capital_Any_<sector>`, 15 PP, weighted random eligible invite or concession).
- Picker: 67 company cards across the five sectors, hidden until the company's founding year. Card click:
  invite (25 PP, `cwic_action_invite_<corp>_<sector>`, sets the invite value to 60) if eligible, else
  concession (50 PP, value 84).
- `cwic_mnc_process_invites_global` (`CWIC_MNC_Generated_Effects.txt:15057`) fires at most one invite event
  (`CWIC_MNC.1000`-`1066`) per country per month (25-day flag `cwic_mnc_invite_evt_global_cd`).
  - Accept: presence +1 → `CWIC_MNC.1100`. If the company lacks capital, the invite loses 12 and stays open
    (`CWIC_MNC.1101`); at 0 it lapses.
  - Decline: 180-day cooldown flag `cwic_invite_cd_<corp>`, company shock timer +2.
  - Outcome events read `cwic_mnc_last_corp/_sector/_presence/_tier/_lapsed`; names come from
    `CWIC_MNC_invite_outcome_loc.txt` (a new company needs a line there).
- Eligibility: invite needs `economic_x_axis >= 10` (or a free-market bonus), nationalization pressure ≤ 4.5,
  presence below the company cap; concession needs `cwic_allows_foreign_concessions`. Communist, maoist and
  trotskyist hosts are ineligible until they authorize. Companies are gated on their foreign-operations year.
- Signature bonuses: `cwic_sig_<corp>_<sector>_b1/b2/b3` for presence 1-2, 3-4, 5+;
  `cwic_mnc_apply_signature_bonuses_country` swaps bands. 22 consumer-facing companies also add native
  consumer-goods output.
- Two monthly MNC calls are commented out in `income_effect` because the effects were never written:
  `cwic_country_mnc_presence_growth`, `cwic_mnc_set_auto_invest_pool_flags_country`.

---

## 17. Comecon (economy hooks only)

`COMECON_monthly_tick` (`effects/COMECON_Effects.txt:1007`, SOV): joins, member upkeep, drift, member
modifiers, crises and AI management. `TRADE_COMECON_RATE` (0-6, Comecon GUI `scripted_guis/COMECON.txt`)
feeds member satisfaction (`COMECON_Effects.txt:183`); it has no trade-price effect. Comecon partners get no
trade discount.

---

## 18. Finance Hub GUI

### 18.1 Files

| Purpose | File |
|---|---|
| Window layout | `interface/Finance_Tab.gui` (window `countryfinanceview`) |
| Sprites | `interface/CWIC_Economy_icon.gfx`, art in `gfx/interface/finance_policy/` |
| Buttons, triggers, sliders, pages | `common/scripted_guis/Finance_Tab.txt` |
| Action effects | `effects/IC_Inflation_Effect.txt` (monetary, FX, controls, black market), `effects/IC_Economy_Effects.txt` (systems), `effects/CWIC_MNC_Effects.txt` (foreign capital), `effects/IC_Consumer_Goods.txt` (strategy) |
| Slider triggers | `common/scripted_triggers/IC_spending_level_triggers.txt` |
| Status lines | `common/scripted_localisation/IC_Economy_scripted_localisation.txt`, `Crisis_GUI_scripted_loc.txt` |
| Labels and tooltips | `localisation/english/CWIC_core_l_english.yml`, `CWIC_MNC_l_english.yml`, `Financial_Tab_l_english.yml`, `CWIC_laws_l_english.yml` |
| Graphs | `effects/line_graph_scripted_effects.txt` |
| Guide | `events/CWIC_Economy_Guide.txt`, `localisation/english/CWIC_econ_guide_l_english.yml` |
| AI decisions | `common/decisions/IC_Financial_Decisions.txt`, `CWIC_Capital_Controls.txt`, `MNC_Decisions.txt` |

### 18.2 Pages

Tabs (`Finance_Tab.gui:~5353-5390`) and their page variables (`Finance_Tab.txt:~2684-2745`):

| Tab button | Sets | Page |
|---|---|---|
| `Overview_Button` | `show_current_overview = 1` | Fiscal Overview: KPIs, ledger, sector pie, graphs; workforce data is merged here |
| `Fiscal_Button` | `show_current_fiscal = 1`, `fiscal_crisis = 0`, `policy = 0` | Fiscal Policy: tax and spending sliders, Collection Efficiency (`effective_tax_rate`) |
| `Economy_Button` | `show_current_fiscal = 1`, `fiscal_crisis = 1`, `policy = 1` | Crisis view plus the Economic Policy panels (`policy_tab`) |
| `Borrowing_Button` | `show_current_borrowing = 1` | Lender list and loan window (`Loan_Confirmation`) |
| `Debts_Button` | `show_current_loans = 1` | Current debts (copies debt arrays to `current*` arrays); pay-off buttons |

`Finance_Guide_Button` (`?`, left of close) fires `cwic_econ_guide.1`: a contents page with six topics
(Reading the Fiscal Overview; Taxes and spending; Inflation and the black market; Economic crises; Borrowing
and debt; Economic Policy and foreign capital). Update the guide when a mechanic it names changes.

### 18.3 Economic Policy buttons

All click effects are `add_political_power = -<cost>` then the action effect; the AI decision for the same
action calls the same effect, so player and AI paths cannot drift. Change the effect, never the button or the
decision alone.

| Panel | Button | PP | Effect | Enabled when |
|---|---|---|---|---|
| Monetary | `enable_money_printing` / `disable_money_printing` | 15 / 15 | `cwic_action_enable_/disable_money_printing` | flag off / on |
| | `print_money_small/medium/large` | 20 / 40 / 90 | `cwic_money_print_small/medium/large` | cooldown 0 (8.2) |
| | `enable_monetary_tightening` / `disable_` | 50 / 15 | `cwic_action_enable_/disable_monetary_tightening` | inflation > 0.006 / < 0.008 |
| | `currency_reform` | 120 | `cwic_action_currency_reform` | cooldown 0, inflation < 0.06, black market < 0.8 |
| | `internationalize_currency` | 120 | `cwic_action_internationalize_currency` | reserve candidate, not yet reserve |
| Markets and FX | `capital_controls_light` / `_heavy` / `_lift` | 40 / 90 / 50 | `cwic_action_capital_controls_*` | inflation > 0.006 / light on and > 0.01 / any control on |
| | `price_controls_basic` | 40 | `cwic_action_price_controls_basic` | inflation > 0.004 |
| | `fx_controls_dual` | 75 | `cwic_action_fx_controls_dual` | inflation > 0.008 |
| | `black_market_raids` / `_enforcement_campaign` / `_amnesty` | 20 / 60 / 50 | `cwic_action_black_market_*` | pressure > 0.2 / 0.45 / 0.3 |
| | `adopt_currency_peg` / `float_currency` | 60 / 25 | `cwic_action_adopt_currency_peg` / `_float_currency` | floating with reserves > 5 / pegged |
| Economic System (`[GetEconomyTypeTitle]`) | `convert_to_rentier` | 50 | `cwic_action_convert_rentier` | x < 18, development ≥ 1, `Rentier_Economic_Check ≥ 0.7` |
| | `convert_to_normal_economic_axis_system` | 50 | `cwic_action_convert_normal_axis` | x > 17, development ≥ 1, `Rentier_Economic_Check < 0.6` |
| | `convert_to_petrostate` | 60 | `cwic_action_convert_petrostate` | x = 24, development ≥ 3, oil exported > 75 |
| Foreign Capital | Authorize / Revoke concessions | 40 / 0 | `cwic_action_authorize_/revoke_concessions` | (16) |
| | Any (per sector) | 15 | weighted random invite or concession | |
| | Picker card | 25 / 50 | invite / concession | (16) |
| Consumer industry | `cg_strat_balanced/basic/durables/export` | [unverified] | `cwic_cg_set_strategy` | 180-day cooldown; durables and export need unlock triggers (Export-Led is player-only) |

Panels are `iconType` siblings drawn before the buttons (see GOTCHAS on containers catching clicks). Buttons
are 188x26 sprites coloured by action type: Expand (blue), Restrict (orange), Structural (yellow), Drastic
(red), Revert (grey). On/off pairs share a slot. Labels `cwic_pol_<button>_lbl` (about 18 characters max),
tooltips `<button>_tt` (Cost / Gains / Drawbacks / Every month / Requires).

### 18.4 Company picker

One window per sector, docked right of the Finance window; two columns of cards ordered by founding year.
Badge, first match: Invite pending, On cooldown, Fully established (presence 5), Invite 25 PP / Concession
50 PP, Not eligible. A pending invite blocks both pick triggers. Hit area: card background, flag and texts, then
a transparent `GFX_cwic_fc_card_hit` button on top (text over a button swallows clicks). Home flags are a fixed
table (Shell and Unilever HOL, Bunge ARG, Gecamines DOC).

### 18.5 Adding a button

1. Write `cwic_action_<name>` in the owning effect file (grep `common/` first).
2. Add the element to `policy_tab` in `Finance_Tab.gui` with the sprite for its action type.
3. Add `_click_enabled`, `_click` and, for paired buttons, `_visible` in `Finance_Tab.txt`.
4. Add `<button>_tt` and `cwic_pol_<button>_lbl` (ASCII only).
5. If AI should use it, add a decision in an AI-only category (`visible = { is_ai = yes }`) calling the same effect.

### 18.6 Graphs

Monthly for players (`00_on_actions.txt`): GDP, GDP-to-debt, Treasury, Inflation, FX reserves; Food and
Electricity are sampled by `food_pulse.1` the next day. 20 samples per history; the first two months are
re-seeded flat (`finance_graph_warmup`); `finance_graph_build_segments` pads new histories and guards a flat
range. The electricity graph samples `resource@coal`, which is the electricity balance.

### 18.7 AI decisions

`IC_Financial_Decisions.txt`: the three conversions are `visible = { is_ai = yes ... }`;
`convert_to_rentier` has `ai_will_do = 0`, normal axis `1`. Capital-control, currency, FX and black-market
categories are AI-only. `CWIC_global_monetary_order` (SOV) stays a player decision. `SOV_Reperation_Payments`
and the `PAEU.*` decisions live in the player-visible `economy_decisions` category.

---

## 19. Content API

From `docs/economy_map/API.md`; verified to exist. Inputs are temp variables set right before the call (they
live for the whole effect block, so set every input on every call).

| Effect | Inputs | Notes |
|---|---|---|
| `cwic_change_money` | `money_change_temp` (billions) | Borrows through the spending cascade if the treasury is short |
| `cwic_take_loan` | `purchase_amount_temp`, `lender_temp` 1-11, `current_index_temp`; for 11: `loan_interest_temp` (%/yr), `loan_years_temp`, global target `cwic_loan_lender`; optional `loan_no_payout_temp = 1` | Lenders 1-10 go through `add_loans_effect` |
| `cwic_forgive_debt` | `debt_forgive_share_temp` (0-1), optional `debt_forgive_lender_temp`, `debt_forgive_payer_temp = 1` with target `cwic_debt_payer` | Does not reduce `domesticTotalDebt` |
| `cwic_set_<policy>_level` | `policy_level_target_temp` | 11 effects (10 spending + `cwic_set_tax_level`) |
| `step_towards_*`, `convert_to_*`, `cwic_set_economic_axes` | axes in `economic_x_target_temp`, `economic_y_target_temp` | |
| `cwic_change_corruption` | `corruption_change_temp` | `CorruptionLevel` clamped 0-1 |
| `nep_ed_increase/decrease_*` (state scope) | `literate_change` etc. | Education shares |

Read-only published outputs: section 2. Remaining raw writes are documented exceptions: insurgent policy reset,
VIE integration, Finance loan UI internals, startup `clear_all_policies`.

---

## 20. Modifier reference

| Modifier | Defined | Read by |
|---|---|---|
| `tax_rate_lower_class`, `tax_rate_middle_class`, `tax_rate_upper_class`, `tax_rate_corporate` | `influence_modifier_definitions.txt:45-66` | tax ideas only; revenue reads the level variables |
| `welfare_ / healthcare_ / education_ / policing_ / public_services_spending_modifier` | `influence_modifier_definitions.txt` | `calc_*_expenditure` |
| `army_ / navy_ / air_ / strategic_forces_ / space_spending_modifier` | same | `military_expenditure`, `calc_*_army_expenditure` |
| `modifier_tax_efficiacy` (spelling is consistent everywhere) | `lar_operation_modifiers_pre_definition.txt:73` | tax `eta` |
| `tax_avoidance_elasticity` | `lar_operation_modifiers_pre_definition.txt:67` | written by axis steps; no reader since the Laffer curve was cut |
| `war_reperations` (spelling) | `influence_modifier_definitions.txt:191` | `income_effect` |
| `consumer_goods_factor`, `consumer_goods_expected_value` | vanilla | civilian factories for CG, trade neutrality |
| `cg_*_output_factor`, `cg_input_floor`, `cg_rare_earth_relief`, `consumer_goods_export_rate`, `cap_*` | custom, synchronized tokens | consumer goods |
| `min_export` | vanilla | seller availability, market refunds |
| `electricity_consumption_need`, `food_consumption_need`, `agricultural_complex_production_bonus` | `lar_operation_modifiers_pre_definition.txt:65-80` | industrial pulse |
| `food_income_bonus`, `*_income_bonus` (industrial park, military factory, office park, foundry, metallurgy, other resources, dockyard), `productivity_factor`, `workforce_ratio` | `influence_modifier_definitions.txt` | only drift variables and the domestic bond pool (`office_park_income_bonus`); not GDP |
| `global_trade_bonus_adjustment`, `global_trade_penalty_adjustment`, `arab_league_trade_penalty_adjustment` | `lar_operation_modifiers_pre_definition.txt:83-98` | no reader since the trade rewrite |
| `monthly_population` | `Intelligence_agency_modifiers.txt:179` | engine; also written as `MONTHLY_POPULATION` in about 270 places [unverified that the engine accepts the uppercase key; no error.log entry] |

Dynamic modifiers that carry the economy into the engine: `resource_consumption`, `food_negative_in_capital`,
`cwic_market_refunds`, `cwic_trade_civ_neutrality`, `cwic_ai_trade_austerity`, `economic_system_modifier`
(`0_dynamic_modifiers.txt`), `cwic_dm_consumer_goods_pressure_master`, `cwic_consumer_industry`
(`IC_dynamic_modifiers.txt`).

---

## 21. Known issues and status of every audit finding

Verified against the code on 2026-11-27, row by row. Rows still tagged `[unverified]` could not be
confirmed from source alone: U2, F1, D1, C4 (electronics tier), R13 (level tables), X3 (line range),
the D4 progress reset, the market-multiplier note, and the N4, N6 and N10 impact claims.

### 21.1 Old finding IDs

Status: **fixed**, **removed** (code deleted or rewritten, finding no longer applies), **open**, **not real**,
**decided** (design choice, no change).

**Structural**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| S1 | AI has no treasury simulation | fixed | `ic_financial_monthly_pulse` has no `is_ai` gate (`00_on_actions.txt`). The AI stipend and GDP refresh were deleted (PLAN F9). AI state pass is every 3rd month (1.3). |
| S2 / T1 | Tax-avoidance clamps; black-market leak sign | removed | `IC_tax_avoidance_line.txt` deleted; revenue is the `eta` formula (4.1), leak subtracted correctly. `eta` is unclamped (21.2). |
| S3 | World trade tick hangs on UNS | open (low) | UNS still hosts the world market, embargo sync and `credit_calculation_work`; per-country buying no longer depends on UNS. No fallback if UNS stops existing. |
| S4 | 3-4 state passes per country per month | open (perf) | One output pass, but `resource_bonus_script`, `industrial_pulse_food_script`, separatism and education still loop states. AI runs them 1 month in 3. Economy ≈ 500 ms of the monthly tick (runH). |

**Money and budget**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| B1 | Welfare modifier applied twice | removed | `calc_welfare_expenditure` (`IC_Econ_2024.txt:694`) reads it once |
| B2 | Insurgency pulse zeroes money and debt | fixed | `CWIC_Insurgency_Economy_Effects.txt` only resets policies |
| B3 | Navy clamp targets air | fixed | clamp on `navy_army_expenditure` |
| B4 | Nuke ×10 on unused temp | fixed | `num_of_nukes × 10` added to strategic cost |
| B5 | Subsidy hard-codes SOV | fixed | `var:subsidy_payer`, default `SOV.id` (`IncomeGenerator.txt:~535`) |
| B6 | `totalexp` never read; `IncomeCheck` set twice | not real / open (low) | `totalexp` read by the sector pie. `military_expenditure` still adds `land_army_expenditure` to `IncomeCheck`, overwritten later in the month (dead write). |
| B7 | `cwic_default_monthly_check` and `ic_Financial` dead | fixed | both deleted |

**Production**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| P1 | Dockyards earn nothing | fixed | dockyard × 2.5 in `cwic_calc_state_output` |
| P2 | Employment coefficients swapped | removed | new jobs table: arms and dockyards both 9.45 × development |
| P3 | `oilEfficiencyGain` accumulates per state | not real | `Resource_Efficiency_Bonus.txt:10` calls `resource_modifier_set_startup` inside `every_owned_state`, which reaches `resource_idea_effect` (`Resource_Efficiency.txt:376`) and resets `oilEfficiencyGain = 0` (`:2`) before `:32` adds to it, so the value does not accumulate across states [inference: scope of the reset] |
| P4 | `Privatisation_Level2` counted twice | fixed | one check (`Resource_Efficiency.txt:137`) |
| P5 | Divide by zero; dead `food_consumption_calculator`; agent-orange decay checks napalm | partly open | No division by factory count (output guards `jobs > 0`). `food_consumption_calculator` (`IC_Industrial_Pulse.txt:2`) still has no callers. Agent-orange reset still tests `napalm_total < 1` (`IncomeGenerator.txt:~32`). |

**Taxes, laws, policies**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| T2 | `tax_avoidance_function` runs before its input | removed | function deleted |
| T3 | `lower_tax_rate` writes upper-class drift var | open (cosmetic) | `upper_class_tax_rate −0.05` still written (`policy_focus_effects.txt:3569`), never read, never added back |
| T4 | `decrease_DOM_Dominican_Nationalist_Fervor` defined twice | fixed | one definition (`policy_focus_effects.txt:5785`) |
| T5 | `lower_healthcare_rate` bottom tier +50 PP | fixed | the call at `IC_Economic_Scripted_Effects.txt:2229-2231` is an `if` on `healthcare_level_value > 3` with no `else` |
| T6 | Dead Laffer cluster; Laffer sampler every pulse | partly open | the Laffer function is gone, but the UI and modifier remain: `Laffer_Label` (`Finance_Tab.gui:5068`, visibility `Finance_Tab.txt:1403`), the Laffer graph in `line_graph_sample.gui:362-416`, its sprite (`New_Technology.gfx:1411`), loc (`CWIC_laws_l_english.yml:695`), and `IC_Economy_Effects.txt` still writes `economic_modifier_tax_avoidance_elasticity` (`:56`, `:596`, `:651`), which nothing reads |

**Trade**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| R1 | AI buys only from the cheapest exporter | removed / changed | AI now buys from the seller with the most available, one deal per good per month (`cwic_auto_import_native`) |
| R2, R11 | `chromium_import_ai` writes `nuclear_total` | removed | effect deleted |
| R3 | Resource concessions dead | fixed (cut) | `resource_concession_evaluation.txt` deleted; stale `resource_concessions` keys remain in non-English loc |
| R4 | No writers for shipping and `price_adjust_*` | partly open | shipping not modelled; `base_shipping_cost_divisor` is set at `on_startup_defines.txt:2652-2653` and never read. `price_adjust_generic^` does have writers (`decisions/ECSC.txt:701-735`, `50s_NIC.txt:1868-1873`, `DOM_49.txt:1482-1487`, `DOM_60s_Democratic.txt:1872-1877`, `LIB_50s.txt`, `New_Ideologies_Ideas.txt:7102-7117`); whether trade settlement reads it is unverified |
| R5 | Trade bonus lowers exporter price | open (dead modifier) | price no longer cut; `global_trade_bonus_adjustment` is defined (`lar_operation_modifiers_pre_definition.txt:59`) and set by ideas (Indonesia, JAP, Brazil, INS, New Ideologies) but no script reads it; its loc promises exporter ranking [unverified: engine-side use] |
| R6 | Comecon trade rate has no effect | changed | trade discounts removed; `TRADE_COMECON_RATE` feeds Comecon satisfaction (`COMECON_Effects.txt:183`), is bounded and clamped 0-6 (`:918-924`, `:1165-1166`) and drives GUI visibility (`scripted_guis/COMECON.txt:671-807`) |
| R7 | `trade_automation` never initialised | fixed | `cwic_trade_manual_default` |
| R8 | `trade.2-7` double immediates; food var case | removed | events and variables deleted |
| R9 | Trade debug effects | removed | none remain |
| R10 | `stabilizing_oil_prices` / `Revamped_Trade_Policy` errors | partly open | no script reference to `stabilizing_oil_prices` remains; `Revamped_Trade_Policy` is an idea at `ideas/usa.txt:1012`. Both warnings appear in older error logs (`_local/logs/2026-09-28`, `2026-10-02`, `2026-10-19`); not seen in `2026-11-24d`. Recheck after the next run |
| R12 | Shared buy prompt; steel/chromium skip target add | removed | `buy_*_click` effects deleted |
| R13 | Comecon level tables disagree; `comecon_gross_ratio_calc` uncalled | removed | effect deleted |
| Registry | Exporter registry rebuilt every 25 days | removed | registry deleted; sellers are listed at purchase time |

**UI**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| U1 | Graph normalisation divides by zero | fixed | range guard in `finance_graph_build_segments` |
| U2 | Electricity graph stores `resource@coal` | not real | coal is electricity in this mod (9.1) |
| U3 | `SAMPLE_*` unreachable; duplicate tokens; `tax_efficiacy` spelling | open (cleanup) / fixed / not real | `Finance_Tab.txt:2912, 3005` still call `SAMPLE_add_random_point_to_line` from sample windows whose `add_button` is commented out in `interface/line_graph_sample.gui`. Duplicate tokens removed 2026-10-27 [unverified now]. Spelling consistent. |

**Treasury flows**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| F1 | Import costs count only the first supplier | removed | settlement reads engine import totals |
| F2 | Trade money not conserved (`trade_credit_factor`) | changed / partly open | factor and bloc pricing removed. Settlement conserves money per good, except the 30% import cap (11.4). |
| F3 | Insurgency funding one month stale | fixed | computed before it is subtracted |
| F4 | `custom_expenses` reset before charge | fixed | never reset; standing monthly charge |
| F5 | Reparations double channel | fixed | single `modifier@war_reperations` line |
| F6 | `custom_income` PRC-only; subsidy inputs have no writers | decided / fixed / open (low) | `custom_income` kept as standing income. Subsidy reads live expenditures. `welfare_cost` still read by `COMECON_Effects.txt:42`, `pie_chart_scripted_effects.txt:165`, `COMECON.txt:1236, 1288` with no writer. |
| F7 | `fiscal_cor_loss` shows a rate as money; factor reset | open / removed | `CWIC_laws_l_english.yml:184` still shows `CorruptIncomeLoss`, which no longer has a writer; factor gone |

**Debt and credit**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| D1 | Interest charged once, not per year | fixed | annual rate charged monthly on principal (7.3, 7.4) |
| D2 | Repayments never restore Mitsubishi, Deutsche, Suisse, IMF caps | fixed | `loan_payoff_change_to_liquidity` branches 1-10 (`:1781`) |
| D3 | Cascade gates on static caps; caps never follow GDP | fixed / open | monthly cascade gates on live caps, which follow GDP (7.2). `cwic_change_money` gates on the same GDP-based caps, not each lender's remaining capacity (N10). |
| D4 | `domesticTotalDebt` only decremented; progress reset wipes penalties; reserve dampener order; arrays never shrink | fixed / unverified / fixed / open | written at `IC_Economic_Scripted_Effects.txt:976, 1922`, `IC_Loans_and_Interest_Rate_Effects.txt:1630, 1800-1803, 2257-2259` and `events/Economic_Penalties.txt:75`, clamped ≥ 0 on repayment; `cwic_forgive_debt` does not reduce it. The progress-reset block the audit cited could not be located [unverified]. Dampener applies to the assigned premium. Zeroed entries still stay in the arrays. |
| D5 | Finance tab static Barclays cap; focus loan maths | fixed | `Finance_Tab.txt:2534-2553` (`Open_Barclays_click`) uses the live cap; `cwic_take_loan` callers: `decisions/PRC_50s.txt:4025`, `FRA_1950s.txt` (8 sites), `GDR_1960s.txt:2281, 2496`, `SOV_Kaganovich.txt:31`, `SWE_50s.txt:1462`, `YUG_70s.txt:2876, 2968`, `events/Indonesia.txt:1592` |

**Consumer goods**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| C1 | Resource pools accumulate | fixed | pools set each month (`:1778`) |
| C2 | Black-market penalty read as shortage | fixed | inflation reads `cwic_cg_shortage_stability`, stored before the penalty (`:194` vs `:210`) |
| C3 | `cg_points_per_factory = 25` over config; demand scale; rounding | open (cosmetic) / removed | 25 still hard-set (`:1806`) against a comment saying 10; demand rewritten and not rounded |
| C4 | Legacy coverage code; 23 AI tier blocks; no electronics T0 | removed / decided | old code and `consumer_goods_ai_automated_trade_effects.txt` deleted; electronics tiers start at 1 by design |

**Taxes, systems, investments**

| ID | Old finding | Status | Evidence |
|---|---|---|---|
| X1 | Tax step `else` grants 50 PP | fixed for tax / open for spending | the eight tax step effects have no `else`. 17 spending step effects (military, navy, air, space, strategic, increase healthcare, both welfare, services, CPI, education) still end `else = { add_political_power = 50 }`, reached when no idea of the family matches (stepping past the ladder end). Sliders are bounds-checked; content callers are not. |
| X2 | `startup_tax_loops` multiplies the start rate in place | fixed | uses `startup_slider_base` temp |
| X3 | Modernize/automate gate on the industrialization budget | fixed | each checks its own budget (`common/decisions/IC_Economic_Investments.txt`) [unverified: exact line range] |
| X4 | Budget refund; no 27/28 startup; CG-need asymmetry; dev-cost accumulator; no z writer | fixed ×4 / open | budgets carry over; 27/28 branches exist; steps ±0.01; dev-cost writes removed. `economic_z_axis` setter exists but is never called. |
| X5 | Duplicate `US_HOUSE` steps; dead tax effects; write-only class vars; French loc keys | decided / fixed / open / not checked | consecutive corporate-tax calls kept (owner's call, e.g. `US_HOUSE.txt:14532-14533`); dead effects deleted; T3; French loc is owned by the translation team |

**Other old notes**

| Item | Status |
|---|---|
| Pollution health penalty used `health_spending_modifier` | fixed (`healthcare_spending_modifier`, `IC_dynamic_modifiers.txt:800`) |
| Market multiplier `if` blocks stacked | fixed (exclusive bands) |
| Food export variable name | removed |
| `MONTHLY_POPULATION` uppercase | open [unverified: engine case handling; no error.log entry] |
| `office_park_income_adjustment` undefined on the old branch | fixed on 2026-10-27 [unverified now] |
| Owner follow-ups: sample graph call, `USA_Electoral_Scripted_Effects_WIP.txt:22` placeholder idea, Russian `resource_concessions` loc | sample call open (U3); others [unverified] |
| AI stipend `cwic_ai_money_stipend`, AI GDP refresh, AI trade-capacity refresh | removed (AI runs the full pulse) |
| Tax and spending changes cost 15 PP instead of a 60-day lock | current (12.4). The `*_cooldown` ideas in `IC_Policies.txt` [unverified: still present, unused] |
| Crisis buffer (retained-territory growth, 180-day grace, 3-month buffer) | current (15) |
| Fiscal crisis judges interest only | current (15) |
| Decision D-items of 2026-10-27 (F2 conserved bloc pricing, R4 shipping by geography, R5 bonus as rank lever, R7 manual trade) | superseded by the November trade rewrite: no bloc pricing, no shipping, no rank lever; manual trade means the vanilla trade window |

### 21.2 Open issues found in the current code

| # | Issue | Evidence | Impact |
|---|---|---|---|
| N1 | GDP ignores productivity levers. `cwic_calc_state_output` does not read `CWIC_productivity_mult`, `CWIC_bm_productivity_penalty`, `productivity_factor`, `workforce_ratio`, the `*_income_bonus` modifiers or their drift variables, or an electricity shortage. | `IC_Econ_2024.txt:482-530`; drift vars written at `:1484-1560` with no reader | Productivity costs of capital controls, tightening, currency reform and the black market, the CG crisis productivity/workforce penalties, and every income-bonus idea and tech do nothing to GDP. `MODEL.md` §1.2 promised them. |
| N2 | `eta` is unclamped | `cwic_budget_tax_revenue` | large negative tax efficiency or extreme leak could make tax negative |
| N3 | Military subsidy copy-paste | `IncomeGenerator.txt:~1395-1420`: navy and air subsidy totals add `mil_expend_subsidy` (land) | wrong subsidy amounts for navy and air |
| N4 | Military GDP-share lines may be lower than intended | `military_expenditure` (`IncomeGenerator.txt:1307-1360`) | monthly land = (`army_spending_modifier` × 0.02 + `strategic_forces_spending_modifier` × 0.01) × GDP/12; navy = `navy_spending_modifier` × 0.01 × GDP/12; air = `air_spending_modifier` × 0.01 × GDP/12. `MODEL.md` §3.3 intended 4/2/2% at full modifier; whether any further divisor applies is unverified |
| N5 | Country loans may pay interest twice | `cwic_take_loan` lender 11 builds interest into the installment; the monthly loop also charges interest on principal | [inference] overpriced country loans |
| N6 | 30% import cap may break trade conservation | `ic_calc_trade_imports` (`IncomeGenerator.txt:1852-1859`) | the importer's `resource_cost` is clamped to 30% of monthly GDP while the trade balance uses the raw bill; whether exporters are paid the uncapped amount is unverified |
| N7 | Dead trade code | `cwic_trade_tier_calc` (`IC_Trade_Scripted_Effects.txt:695`) and `cwic_price_shock_*` (`:739-784`) have no callers; `global_trade_bonus_adjustment` is set by ideas but never read (R5) | cleanup; misleading loc |
| N8 | Insurgency exit keeps War Economy and level-0 policies | `cwic_exit_insurgency_to_normal_economy` clears a flag only | callers must set axes and levels themselves |
| N9 | `economic_z_axis` variants unreachable | `cwic_set_economic_variant` has no callers | variant names and icons never show |
| N10 | `cwic_change_money` gates on lender caps | `IC_Economic_Scripted_Effects.txt:1037+` checks `ReserveMaxBorrowable`, `WorldMaxBorrowable`, `MorganMaxBorrowable`; `IC_Loans_and_Interest_Rate_Effects.txt:1452` recomputes the reserve cap from GDP | caps follow GDP, not each lender's remaining capacity [unverified: whether that lets spending exceed it] |
| N11 | `cwic_forgive_debt` leaves `domesticTotalDebt` | `IC_Financial_Scripted_Effects_for_Content.txt:151` | domestic debt display drifts high |
| N12 | Rating 10 has no default/austerity multipliers | `set_interest_rates` | latent; guarded by `Credit_Rating < 10` |
| N13 | `cropBoost` multiplied but never set in `industrial_pulse_food_script` | `IC_Industrial_Pulse.txt` | no-op |
| N14 | Empty first `immediate` blocks | `tutorial.2000`, `food_pulse.1` | cosmetic |
| N15 | `CWIC_CRISIS_GRACE` set for VIN every month during the Indochina war | `IncomeGenerator.txt:1290-1297` | intended override, labelled VIN-only |
| N16 | Two MNC monthly effects never written | `IncomeGenerator.txt:1280-1286` | commented calls |
| N17 | `MODEL.md` promises not built | no `debt_premium` anywhere; default still compares debt against `default_multiplier` (`IC_Loans_and_Interest_Rate_Effects.txt:40, 52`, values set by credit rating at `:1112-1207`) instead of debt service > 35% of revenue for 3 months; `base_infl` is a flat 0.001/month (`IC_Inflation_Effect.txt:71`) instead of era baselines; no single `cg_shortage` variable (computed separately in `IC_Consumer_Goods.txt:48-51` and `:77-80`); history-layer shocks not wired (`cwic_price_shock_*` uncalled) | design gap |

---

## 22. Testing status

**Verified in game (AFK observer runs, `docs/economy_map/baseline/`, logs and NOTES committed):**

| Run | Date | Build | What it showed |
|---|---|---|---|
| A, A2 | 11-02 | pre-Pass 1 | yearly tick works; AI GDP flat between territory changes, debt frozen (the problems F9 fixed) |
| B | 11-02 | player pulse forced on AI | full pulse for every country costs about 3% of tick time; no economy errors |
| C, D | 11-02 | Pass 1 | debt transfer, F16-F18 tuning; Run D: 0 economy errors, 1 country > 150% debt/GDP, median inflation 3.6%/yr |
| E, F | 11-03/04 | Pass 2 core | HDI rank correlation 0.89-0.92; new tags inherited too much debt (fixed) |
| G | 11-05 | 220d7c57c5 | to 1969; majors at 7-40% debt/GDP; LAO/COG fixed deficits found |
| H | 11-06 | ea1acbfe82 | AI 3-month rotation; economy ≈ 500 ms of a 3.0 s monthly tick |
| I | 11-04 | perf pass | monthly tick ≈ 1.25-1.3 s |
| Lead-dev playtest | 10-27 | pre-rework | signed off the Oct 27 fixes (code since rewritten) |

Observer mode makes every country AI, including the one watched (GOTCHAS); these runs test the AI path.

**Not verified in game (no run notes in the repo):**

- The native trade rewrite (11-10..13) and consumer goods as native resources (11-15..17). Commit messages
  report tuning (world CG demand balance, daily tick back to about 53 ms after `f0a87f4516`), but no
  run notes are committed.
- `cwic_action_convert_normal_axis` by ideology (11-24).
- The Finance Hub checklist from the old reference: open every page as VIN and compare tooltips with variable
  changes; LAO and MLA exits; communist versus free-market MNC eligibility; AI still taking capital-control,
  MNC and loan decisions in an observer run; scripted GUI and localisation errors.
- The `cwic_transfer_state_debt` base fix for MAL (`d7e3b07262`).

**Latest error.log** (`~/.local/share/Paradox Interactive/Hearts of Iron IV/logs/error.log`, 2026-11-26,
game date 1956-01): no entries from the core economy scripted-effect files. It does contain a dynamic-token OOS
warning for `Provide_Farmers_Affordable_Loans`.

**Tools:** `_tools/economy_check/check_economy.py` (reads `CWIC_ECON`/`CWIC_BUDGET`/`CWIC_REV` log lines),
`_tools/check_native_trade_gui.py`, `_tools/check_economic_idea_cache.py`. Debug flags:
`cwic_debug_skip_econ`, `cwic_debug_skip_education`.
