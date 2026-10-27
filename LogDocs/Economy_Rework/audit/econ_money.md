# CWIC economy: money slice (treasury, budget, debt, deficits)

Scope: `ic_financial_monthly_pulse` and its callees. Read-only investigation. Line numbers are from the files as they exist on branch `Econ-fix`. Items marked [INFERENCE] are not directly verified. Paths are relative to `Cold War Iron Curtain/` unless noted.

## 1. Purpose and entry points

**Monthly chain (human players only)**
- `common/on_actions/00_on_actions.txt:38-41`: `on_monthly` runs `if = { limit = { is_ai = no } ic_financial_monthly_pulse = yes }`. This is the only live caller of the pulse. AI countries are excluded here.
- `common/scripted_effects/IC_scripted_effects.txt:2-74` (`ic_financial_monthly_pulse`):
  - If `has_country_flag = active_insurgency`, it calls `cwic_insurgency_monthly_pulse` (lines 4-5) and skips the rest.
  - Otherwise it runs the `*DeliveryCuts = yes` effects (about lines 9-40: oil, steel, rare earth, aluminium, chromium, food, consumer goods classes T0-T5), zeroes national class pop/pay variables (about 42-55), then:
    - `income_effect = yes` (57)
    - `add_to_variable = { currentMoney = modifier@war_reperations }` (58)
    - resets resource bonuses (59-63)
    - `resource_bonus_script = yes`, `industrial_pulse = yes`
    - `monthly_borrowing_and_interest_pulse = yes` (71)
- `IC_scripted_effects.txt:76-82` (`ic_pulse_monthly`): `federation_calculator`, `monthly_power_projection_gain`, `monthly_set_fpp`, `monthly_infamy_calc`, `add_nhan_van_minigame_to_ui`. Not a money effect.
- `IC_scripted_effects.txt:84+` (`ic_pulse`): not read in full. It is called for every country from `common/decisions/_generic_decisions.txt:1470-1477` and `on_startup_defines.txt:3255-3257`. [INFERENCE] It is the AI-side substitute, but its money content is unverified.

**Income/expense engine**
- `common/scripted_effects/IncomeGenerator.txt:287` (`income_effect`) is the core. It runs inside the pulse (line 57 of IC_scripted_effects) and from `_generic_decisions.txt:1533-1534` (`every_country { income_effect = yes }` in a complete_effect block). See Problem P1.
- `IncomeGenerator.txt:1` (`income_effect_every_owned_scope`) calls `calculate_separatism` (line 2). It is not a money effect.

**Monthly UNS world tick**
- `00_on_actions.txt:42-~60` (UNS-only block): `export_script_for_pool`, `credit_calculation_work`, and `every_country` → `country_event = trade.1` when `trade_automation = 2` or `is_ai = yes`.
- `on_startup_defines.txt:3536-3537` (UNS `export_script_for_pool`) and `3690-3691` (`every_country { credit_calculation_work = yes ... }`) run the same at startup.
- `_generic_decisions.txt:1504` says these were retired from another location and now run from on_monthly.

**Decisions and focus effects (spending and income events)**
- About 30 decision/focus files call `cwic_change_money` with `money_change_temp` in billions (for example FIN_1990s, Indonesia, PHI_Decisions, Russian_FSB_decisions, SIA, SOV, USA_1990s_*, US_HOUSE, INO_*, JAP_national_focus, RUS_90s_Yeltsin_1991, SIA_50s, SOV_WW3_1950s, USA_Truman_1948). Values range from about -0.05 to -50.
- `IC_Economic_Scripted_Effects.txt:1033` (`cwic_change_money`) is the one-off treasury adjuster.
- `IC_Economic_Scripted_Effects.txt:613` (`add_loans_effect`) is the player loan UI; it sets `purchase_amount` and `bank_name_prompt`.

**Retired or commented hooks (dead references)**
- `_generic_decisions.txt:1504`: "Retired: export_script_for_pool, credit_calculation_work, and trade.1 now run from on_monthly."
- `_generic_decisions.txt:1528`: "Retired: ic_financial_monthly_pulse now runs from on_monthly."
- `00_on_actions.txt` around line 75: `#gdp_calculation_effect = yes` is commented out.

## 2. Data model

| Variable | Scope | Meaning and units | Writers | Readers |
|---|---|---|---|---|
| `currentMoney` | country | Treasury balance, presumably in billions (inferred from the `money_change_temp` comment at `IC_Economic_Scripted_Effects.txt:1035`) | `income_effect` (`IncomeGenerator.txt:2010`), loans (`IC_Loans_and_Interest_Rate_Effects.txt` automatic_loan_setting 1490), debt repayments (2048, 2072, 2084), `cwic_change_money`, insurgency pulse (`CWIC_Insurgency_Economy_Effects.txt:46`), setup (`:30`) | pulse deficit gate (2012-2025), debt checks |
| `currentDebt` | country | Total outstanding debt | `automatic_loan_setting` (1500ish), repayments (`IncomeGenerator.txt:2051`), insurgency pulse (`CWIC_Insurgency_Economy_Effects.txt:47`) | default/austerity checks (2219, 2250), `TotalDebtk` (2138) |
| `currentDebtPayments` | country | Monthly amortisation paid | reset at `IncomeGenerator.txt:2033`, incremented at 2054 and in `automatic_loan_setting` | display_balance (2129-2131) |
| `debtTotalsArray`, `debtPaymentArray`, `debtOwnerArray`, `debtOwnerDomesticStatusArray`, `debtInterestArray` | country arrays | Parallel loan ledger (balance, monthly payment, creditor id, bank/domestic flag, rate) | `automatic_loan_setting` (1505-1538 range) | income_effect repayment loop (2035-2127) |
| `IncomeTotal` | country | Running monthly net income in the pulse | reset at `IncomeGenerator.txt:2663`; `+=` at 453, 1227, 1230, 1233; `-=` at 1913, 1916, 1919, 1954, 2000s subsidy | `IncomeCheck`, `SubsidiyCheck`, currentMoney |
| `IncomeCheck` | country | Snapshot of IncomeTotal used in the deficit check | `IncomeGenerator.txt:2027` | display (2130) |
| `pulse_deficit` | country | Positive shortfall when currentMoney < 0 after adding income | `IncomeGenerator.txt:2012-2025` | default check (2208), `automatic_loan_setting` (1490) |
| `totalexp`, `total_expenses` | country | Two parallel expense aggregates. `totalexp` (397-419) is an accumulator with no reader found [INFERENCE]. `total_expenses` (1945-1952) is subtracted from IncomeTotal (1954). | income_effect | `totalexp` no reader found [INFERENCE] |
| `military_total_exp` | country | Monthly military spend, the sum of GUI totals | `IncomeGenerator.txt:2918-2922` | `totalexp` (398), `total_expenses` (1947) |
| `mil_gui_total`, `navy_gui_total`, `af_gui_total`, `sf_gui_total` | country | Monthly per-branch spend after divisors | `IncomeGenerator.txt:2898-2916` | military_total_exp |
| `land_army_expenditure`, `navy_army_expenditure`, `air_army_expenditure`, `nuke_army_expenditure`, `space_expenditure` | country | Pre-divisor annual-style cost, see Formulas | `IC_Econ_2024.txt` calc_* 1665-1991 | `IncomeGenerator.txt:2754-2915` |
| `welfare_expenditure`, `healthcare_expenditure`, `policing_expenditure`, `education_expenditure`, `public_services_expenditure`, `public_expenditure_total` | country | Social spend (see Formulas) | `IC_Econ_2024.txt` calc_* 1537-1664 | `IncomeGenerator.txt:392-401, 1948-1952` |
| `custom_expenses` | country | War reparations charge (reset fixed at `IncomeGenerator.txt:402`) | 403-418 | 419, 1916 |
| `resource_income`, `consumer_goods_export_income`, `custom_income`, `resource_cost`, `total_insurgency_funding` | country | Income and cost buckets | income_effect | IncomeTotal |
| `GlobalDebit` = 0.28 | global | Policy cost multiplier for military | `on_startup_defines.txt:2684` | `IncomeGenerator.txt:2755-2770` |
| `GlobalCredit` = 0.45 | global | Commerce/tourism income multiplier | `on_startup_defines.txt:2682` | `IncomeGenerator.txt:435` |
| `GlobalEdictDebit` = 0.44 | global | Edict costs (`IC_Loans_and_Interest_Rate_Effects.txt:57` edict_expenditure) | `on_startup_defines.txt:2685` | edict_expenditure [INFERENCE] |
| `GlobalTaxCredit` = 1.00, `PreindustrialTaxCredit` = 0.5 | global | Tax credit multipliers | `on_startup_defines.txt:2683, 2687` | [INFERENCE] tax effects |
| `ReserveMaxBorrowable`, `WorldMaxBorrowable`, `MorganMaxBorrowable`, `ParisMaxBorrowable`, `BarclaysMaxBorrowable`, `MitsubishiMaxBorrowable`, `DeutscheMaxBorrowable`, `SuisseMaxBorrowable`, `available_liquidity` | country | Lending capacities per lender | `IC_Loans_and_Interest_Rate_Effects.txt` (set_interest_rates 1082+ and similar) | default cascade `IncomeGenerator.txt:2271-2560` |
| `Credit_Rating` | country | Credit grade (scale unverified; the code compares `< 10` and `< 1`) | `process_credit_rating` (329), raise/lower (916, 936), set_starting (946) | default checks (2220, 2257) |
| `Interest_Rate`, `ParisCurrentInterestRate`, `ReserveCurrentInterestRate` | country | Rates (percent); fallback 1.04 at `IncomeGenerator.txt` ~2180 | set_interest_rates (1082), set_international_commercial_rates (1323), set_reserve_rate (1437) | loan pricing |
| `grossdomesticproduct` | country | GDP (monthly flow, after `/10`) | `IC_Econ_2024.txt:1390-1420` range (sum) and `divide_variable ... = 10` | many |
| `gni_total` | country | Gross national income accumulator | `calculate_sum_up_total` 1482-1502 | unverified |
| `CWIC_inflation_mom` | country | Monthly inflation, seeded 0.0025 | `IC_Economic_Scripted_Effects.txt:1936-1941` | default penalty adds 0.010 at `IncomeGenerator.txt:2242` |
| `CWIC_black_market_pressure` | country | Default penalty | `IncomeGenerator.txt:2243` | unverified |
| `CWIC_monetary_policy_mult` | country | Default 1 | `IC_Loans_and_Interest_Rate_Effects.txt:1084` | currency policy decisions |
| `CWIC_fx_regime`, `CWIC_fx_reserves` | country | FX regime and reserves | `IC_Economic_Scripted_Effects.txt:977-1032` | unverified |
| `CorruptLoss`, `CorruptPolicyExcess`, `CorruptionLevel`, `CorruptIncomeLoss` | country | Corruption leakage | `IncomeGenerator.txt:1248-1254`, 2847-2880 | total_expenses |
| `subsidiy_base`, `SubsidiyCheck` | country | Subsidy base, 25% of net income | `IncomeGenerator.txt:1969-2008` | `SOV.currentMoney` (2003) [INFERENCE: hard-coded SOV reference] |
| `WorldMaxBorrowable` etc. | country | see above | | |

## 3. Formulas (step by step)

### 3.1 Monthly pulse (`IC_scripted_effects.txt:2-74`)
1. If country has `active_insurgency`: run `cwic_insurgency_monthly_pulse` and stop. The insurgency pulse resets `currentMoney = 0` and `currentDebt = 0` every month (`CWIC_Insurgency_Economy_Effects.txt:46-47`). Rest of that effect not read.
2. Otherwise: delivery cut effects, class zeroing, then `income_effect`.
3. `currentMoney += modifier@war_reperations` (line 58).
4. Resource bonus reset and `resource_bonus_script`, `industrial_pulse`.
5. `monthly_borrowing_and_interest_pulse` (line 71), which calls `set_international_commercial_rates` and `set_reserve_rate` (`IC_Loans_and_Interest_Rate_Effects.txt:1658-1661`).

### 3.2 Income and expenses (`IncomeGenerator.txt:287-2729`)
Order inside `income_effect`:
1. `cwic_process_war_reparations` (288).
2. `gdp_calculation_effect` (~293). This computes GDP, taxes, and the state loops (see section 3.4).
3. `cwic_cg_monthly_master_tick`.
4. `military_expenditure` (326) → land/air/navy/nuke/space costs (section 3.3).
5. `interest_rate_calc` (328), `domestic_bond_calc` (329), `mercenary_calc` (330), `social_indices` (331).
6. Social expenses (385-395):
   - `get_average_development` (385) is the required base.
   - `calc_education_expenditure`, `calc_public_services_expenditure`, `calc_welfare_expenditure`, `calc_healthcare_expenditure`, `calc_policing_expenditure` (386-390).
   - `public_expenditure_total = public_services + welfare + healthcare` (392-395).
7. `totalexp = military_total_exp + public_expenditure_total + policing + education + custom_expenses` (397-419).
8. Tourism: `tourism_infrastructure_total *= GlobalCredit (0.45) * tech * stability / 12`, then `IncomeTotal += tourism` (435-453). Note `ROOT.trade_infrastructure_total *= 8` (`:~320`).
9. Resource income and export income accumulate into `resource_income` and `consumer_goods_export_income`. Only the sums are read: `IncomeTotal += custom_income, resource_income, consumer_goods_export_income` (1227-1233).
10. Corruption: `CorruptLoss = IncomeTotal × CorruptIncomeLoss` (1249-1252), added to `totalexp` (1254).
11. `IncomeTotal -= resource_cost (1913), custom_expenses (1916), total_insurgency_funding (1919)`.
12. Policy costs: `total_expenses = CorruptLoss + military_total_exp + welfare + policing + education + healthcare + public_services` (1945-1952). `IncomeTotal -= total_expenses` (1954).
13. Subsidy: `SubsidiyCheck = IncomeTotal × 0.25` (1969-1972). Subsidy base is land army plus welfare cost (1982-1985). If the condition holds, `SOV.currentMoney -= subsidiy_base` and `IncomeTotal += subsidiy_base` (2003-2006). See P7.
14. `currentMoney += IncomeTotal` (2010). Then `pulse_deficit` is set to `-currentMoney` if negative (2012-2025). `IncomeCheck = IncomeTotal` (2027), `IncomePlannerCheck = IncomeCheck` (2030).
15. Debt repayments (2033-2127): for each entry in `debtPaymentArray`, subtract from `debtTotalsArray`, `currentMoney`, and `currentDebt`, and add to `currentDebtPayments`. Creditor side: if `debtOwnerArray^i` is this country or not GER, the payment is credited to `var:debtOwnerArray^i.currentMoney`. For GER-owned debt, the payment is credited and then distributed through `influence_array` (2081-2100). Zero-balance entries are cleared (2108-2124).
16. Default and austerity (2208-2268, see 3.5).
17. Domestic/international loan capacity cascade (2271-2560): for each lender with `MaxBorrowable > pulse_deficit`, call `automatic_loan_setting` (section 3.6). The order is Reserve, available_liquidity, World, Morgan, Paris, Barclays, Mitsubishi, Deutsche, Suisse.
18. End-of-pulse reset `IncomeTotal = 0` (2663) and the GDP/indices calls (2706-2708): `cwic_calc_corporate_risk_index`, `cwic_calc_global_budget_risk_factor`, `cwic_calc_global_budget_shock_factor`, `cwic_country_add_all_corp_profits`.

**Note:** `IncomeTotal` is reset at line 2663, which lies in a block after the expense and debt steps. The reset is therefore not at the start of the pulse. Which block 2663 belongs to needs confirming [INFERENCE].

### 3.3 Military costs (`IncomeGenerator.txt:2730-2916`, calc bodies in `IC_Econ_2024.txt`)
Each `calc_*` yields an annual-style value that is then divided to monthly in the military block.

- **Land** (`IC_Econ_2024.txt:1665-1750`): `average_development × deployed_army_manpower_k` + queue term `average_development × amount_manpower_in_deployment_queue / 1000`, all divided by 10000. Then a weighted battalion sum: 0.005 (direct_fire_gun, militia), 0.01 (infantry…), 0.02 (spaag…military_police), 0.025 (sam_carrier…signal_company), 0.03 (heavy armor set). The total is `×0.5 × modifier@army_spending_modifier`. Clamped to ≥0.
- **Air** (`IC_Econ_2024.txt:1751-1878`): `average_development × deployed_airforce_manpower_k × 0.05`, plus tier sums: tier1 ×0.01, tier2 ×0.025, tier3 ×0.05, tier4 ×0.075. Then `×0.5 × modifier@air_spending_modifier`. Clamped.
- **Navy** (`IC_Econ_2024.txt:1879-1958`): `average_development × deployed_navy_manpower_k × 4 / 10000`, plus ship tiers ×0.05, 0.1, 0.15, 0.25. Then `×0.5 × modifier@navy_spending_modifier`. **Clamp targets the wrong variable (P4).**
- **Nuke** (`IC_Econ_2024.txt:1959-1991`): `(average_development + Total_Nuclear_Reactors) × 750`, plus missiles (srbm×5, irbm×30, icbm×75, slbm×20) and nukes, all divided by 10000 and `× modifier@strategic_forces_spending_modifier`. **The ×10 on nukes is dead (P3).**
- **Space** (`IC_Econ_2024.txt:1992-2010`): only if `Space_Program_Active`. `grossdomesticproduct / 5 × modifier@space_spending_modifier`, added to `space_budget`.
- **Global scaling** (`IncomeGenerator.txt:2754-2771`): land, navy and air are multiplied by `GlobalDebit` (0.28). Nuke and space are not.
- **Subsidy and corruption shares** (2773-2895): 25% of each branch is removed from branch costs and redistributed through the `influence_array` loop (2825-2841). Corruption penalties are added back as `× CorruptPolicyExcess` (2847-2880).
- **Monthly divisors** (2898-2901): land ÷1.5, navy ÷2.5, air ÷2.25, nuke ÷1. These ad hoc numbers have no comment explaining them.
- **Totals** (2918-2922): `military_total_exp = mil_gui_total + navy_gui_total + af_gui_total + sf_gui_total`. `sf_gui_total` includes nuke and space.

### 3.4 Social expenses (`IC_Econ_2024.txt:1537-1664`)
- **Welfare** (1537-1589): `((labourer_sum + substinents_sum + unemployed_sum) + 0.5×(farmer_sum+worker_sum)) / 2000 × average_development`. Then `× welfare_policy_mult` (≈ `modifier@welfare_spending_modifier`, with 1 if < 0.0005), then `× modifier@welfare_spending_modifier` again. **Modifier applied twice (P5).**
- **Healthcare** (1590-1605): `max_manpower × 0.001 / 30000 × average_development × modifier@healthcare_spending_modifier`.
- **Policing** (1606-1622): `(max_manpower × 0.001 / 25000 × average_development × modifier@policing_spending_modifier) + black_ops_expedntiture`.
- **Education** (1623-1645): `max_manpower × 0.01 / 10000 × average_development × modifier@education_spending_modifier × 0.05`.
- **Public services** (1646-1664): `(max_manpower / 10000 / 100 + total_infrastructure) × 0.01 × modifier@public_services_spending_modifier`. Infrastructure dominates population (P6).

### 3.5 Default and austerity (`IncomeGenerator.txt:2208-2268`)
- Trigger: `pulse_deficit > currentMoney` (2208-2209).
- Default: if `defaultCheck < currentDebt` AND `Credit_Rating < 10` AND `defaultCheck ≠ 0` AND not NLF, and no `Recent_Default` idea: set `CWIC_DEFAULTED` and `CWIC_MARKET_LOCKOUT`. Then `Credit_Rating -= 2` (floor 1), `CWIC_inflation_mom += 0.010`, `CWIC_black_market_pressure += 0.10`, and fire `CWIC_ECON_PENALTIES.2` (2218-2246).
- Austerity: else if `austerityCheck < currentDebt` and `Credit_Rating < 10` (and conditions), fire `CWIC_ECON_PENALTIES.1` unless `Recent_Austerity_Measures` is present (2249-2268).
- `defaultCheck` and `austerityCheck` are not defined in the read range [INFERENCE: set by `cwic_default_monthly_check`, `IC_Loans_and_Interest_Rate_Effects.txt:2312`].

### 3.6 Loans (`IC_Loans_and_Interest_Rate_Effects.txt:1488-1554`, `IncomeGenerator.txt:2271-2560`)
1. `currentMoney += pulse_deficit` (1490).
2. `potential_loan_total = pulse_deficit × (1 + currentInterestRateCalc[current_index] / 100)` (1456-1475 region, using 1493-1505). Interest is one-off, not compounded.
3. `monthly_cost = potential_loan_total / (purchase_length[current_index] × 12)`.
4. Record in parallel arrays and add to `currentDebt`, `currentDebtPayments`, and `loan_set_assigning_borrowable` (1555+).
- `current_index` is not defined in this file [INFERENCE: loop index set by the caller].

### 3.7 GDP and tax (`IC_Econ_2024.txt:1308-1443`, `2638-2707`)
- `gdp_calculation_effect` resets sums, runs `every_owned_state` (the per-state chain in section 4), then:
  - `divide_variable grossdomesticproduct = 10`.
  - `calculate_national_take_taxes_from_people`.
  - `calculate_gdp_per_capita`, `GDP_Extra_Calcs`.
  - `credit_calculation_work = yes` as a backup (1411), `set_interest_rates = yes` (1412).
- Per state (`calculate_take_taxes_from_people`, 2638-2694):
  - Personal tax per class = `gross × owner tax rate`, summed over lower+substinent, middle+artisan, upper. Then `÷100` (2655-2660).
  - Corporate tax = `max(net_factory_earnings, 0) × owner:pop_corporateclass_tax_rate / 100` (2677-2687).
- National (2695+): `ui_income_tax`, `ui_corporate_tax`, `IncomeTotal += total_personal_income_tax + total_corporate_tax`, `IncomeCheck += IncomeTotal`.
- Note: `calculate_national_take_taxes_from_people` (2695) runs during `gdp_calculation_effect`, which runs at the top of `income_effect`. Tax therefore enters IncomeTotal before the expense steps (P8).

## 4. Interactions

- **Money ↔ income**: `income_effect` is the sole writer of `currentMoney` from taxes, GDP-based income, tourism, resources, and exports, and the sole place where expenses are subtracted. The same variable is also written by decisions (`cwic_change_money`), loans, debt repayments, and the insurgency pulse.
- **Money ↔ GDP**: `gdp_calculation_effect` runs inside `income_effect` and feeds tax. GDP also feeds `space_expenditure` and `gni_total` and the loan side through `gdpDomesticDebtLimit` (`IncomeGenerator.txt:~2150-2185`, uses `grossdomesticproduct > 1 / 5 / 10 / 100 / 1000` tiers).
- **Money ↔ military**: `military_expenditure` supplies `military_total_exp`, which is charged in `totalexp` (398) and `total_expenses` (1947).
- **Money ↔ social policy**: welfare/healthcare/education/policing/public services scale with `modifier@*_spending_modifier` (policy ideas). Policy changes move both the cost and the economic axis (`IC_Economy_Effects.txt`, `economic_modifier_welfare_spending` ±0.01 per step).
- **Money ↔ trade**: `export_script_for_pool` (`IC_Trade_Scripted_Effects.txt:3`) resets `oil_export_prior` and related vars. Export income reaches the treasury through `consumer_goods_export_income` and `resource_income`.
- **Money ↔ AI**: AI is excluded from `ic_financial_monthly_pulse` (`00_on_actions.txt:38-41`). The UNS block runs `credit_calculation_work` for everyone. Whether AI runs `income_effect` at all depends on `_generic_decisions.txt:1533` and `ic_pulse` (not read) [INFERENCE].
- **Money ↔ insurgency**: `active_insurgency` replaces the entire pulse with a reset (`CWIC_Insurgency_Economy_Effects.txt:46-47`).
- **Money ↔ UI**: `calculate_employment_data_for_gui` (`IC_Econ_2024.txt:2012`), `generate_class_pie_chart_gui` (2113), and the `*_gui_total` and `*_display` variables (`IncomeGenerator.txt:2744-2770`, 2903-2915).

## 5. Problems

Severity: **H** = wrong numbers or state corruption in normal play; **M** = likely wrong or hard to maintain; **L** = dead or cosmetic.

**P1 (H) `income_effect` may run twice per month.** `IncomeGenerator.txt:287` adds income to `currentMoney` (2010) on every call. `ic_financial_monthly_pulse` calls it at `IC_scripted_effects.txt:57`. `_generic_decisions.txt:1533-1534` also calls `every_country { income_effect = yes }` inside a complete_effect block. If that block fires monthly, income and expense are applied twice. The block was not confirmed as monthly [INFERENCE: check its trigger].

**P2 (M) `IncomeTotal` reset position.** `IncomeGenerator.txt:2663` resets `IncomeTotal = 0` inside a block that is not clearly the start of the pulse. The pre-pulse ordering (taxes at 2695 run before `IncomeTotal` is zeroed in another block?) needs confirmation. [INFERENCE: if the reset runs after the tax add, tax is lost.]

**P3 (M, dead code) Nuke ×10 has no effect.** `IC_Econ_2024.txt:1959-1991`: `multiply_temp_variable = { num_of_nukes = 10 }` multiplies a temporary variable named `num_of_nukes`. Then `nuke_expenditure` (set from `num_of_nukes` before the multiply) is added unmultiplied. The intended 10× is lost. Either delete the line or apply it to `nuke_expenditure`.

**P4 (M, bug) Navy clamp targets the wrong variable.** `IC_Econ_2024.txt` `calc_navy_army_expenditure` (1879-1958): the final `clamp_variable` uses `var = air_army_expenditure`. `navy_army_expenditure` is never clamped to ≥0. Low impact, since inputs are non-negative.

**P5 (H, balance/bug) Welfare modifier applied twice.** `IC_Econ_2024.txt:1537-1589`: `welfare_policy_mult` is set to `modifier@welfare_spending_modifier` (or 1 if below 0.0005), used to multiply `welfare_expenditure`, then `welfare_expenditure` is multiplied by `modifier@welfare_spending_modifier` again. For a country with a welfare policy the modifier is squared. For a country without one, the modifier is applied once even though the comment says "keep the old full cost (x1)". [INFERENCE: depends on the base value of the modifier when no policy idea is present.]

**P6 (M, balance) Public services scale with infrastructure, not population.** `IC_Econ_2024.txt:1646-1664`: `max_manpower/10000/100` is added to `total_infrastructure` (levels, typically 10-100), so the infrastructure term dominates. The expense barely responds to population.

**P7 (M, bug) Hard-coded SOV reference in subsidy.** `IncomeGenerator.txt:2003`: `SOV.currentMoney -= subsidiy_base`. This makes the subsidy mechanic depend on the Soviet Union's treasury for every country, which is probably wrong for non-SOV scenarios. Check the surrounding gate (1975-2008).

**P8 (M) Tax added before IncomeTotal is zeroed?** See P2. Also `calculate_take_taxes_from_people` contains a comment claiming "the /100 on IncomeTotal after the state loop restores the old overall scale" (`IC_Econ_2024.txt:2638-2660`). The only post-loop scaling in `gdp_calculation_effect` is `grossdomesticproduct / 10` (1443 region). No `/100` on `total_personal_income_tax` or `IncomeTotal` was found in the read ranges [INFERENCE: may exist outside what I read]. The same comment block has a contradictory "REVERT FIX 2026-07-09" note on the corporate-tax `max = 0` line. Clean up or verify.

**P9 (L, dead) Military `IncomeCheck` add is overwritten.** `IncomeGenerator.txt:2731-2733` adds `land_army_expenditure` to `IncomeCheck`. `military_expenditure` runs at line 326, before `IncomeCheck = IncomeTotal` (2027). The earlier add is therefore lost, and the land army value it uses is last month's (the calc runs later in the same block).

**P10 (L, dead/duplicate) `totalexp` has no reader found.** `IncomeGenerator.txt:397-419` builds `totalexp`, and 1254 adds `CorruptLoss` to it. A grep across the mod for `totalexp` is needed to confirm no reader exists [INFERENCE]. `total_expenses` (1945) is the one actually subtracted.

**P11 (L, debug residue) Debug variables and comments.** `IC_Econ_2024.txt:1504-1515` `give_everyone_base_tax` (Tax Debug, adds temp ideas to every country). `calc_land_army_expenditure` sets `land_army_expenditure_actual_land` and `mil_test` (about 1715-1717). `IncomeGenerator.txt:458, 1238-1239, 1255, 1921` contain commented `#log` lines. Many commented-out blocks in `IC_Econ_2024.txt:1-100` and `calculate_take_taxes_from_people`.

**P12 (L, dead) `decrease_global_oil_insecurity` and `increase_global_oil_insecurity` are empty** (`IC_Econ_2024.txt:2188-2194`).

**P13 (M, perf) Hot spot.** `income_effect` runs for each non-AI country monthly and calls `gdp_calculation_effect` (which runs `every_owned_state` with about 20 nested effects) plus about 110 `num_battalions_with_type` and `num_deployed_planes_with_type` lookups in land/air calcs. The lender cascade (IncomeGenerator 2271-2560) also runs for each lender whenever there is a deficit. `calc_*` and the GDP loop are the main cost. The on_monthly UNS block adds `every_country` loops for `trade.1`.

**P14 (M, risk) Insurgency pulse wipes treasury and debt every month.** `CWIC_Insurgency_Economy_Effects.txt:46-47` sets `currentMoney = 0` and `currentDebt = 0` on every pulse. Intended, but the rest of the effect was not read and the debt arrays are not cleared here, so `debtTotalsArray` can diverge from `currentDebt`.

**P15 (M) Default triggers depend on undefined ranges.** `Credit_Rating < 10` and `< 1` suggest a 0-10 or 1-10 scale. The scale is not documented in the read ranges [INFERENCE].

**P16 (M, unit mismatch) `cwic_change_money` mixes billions and millions.** `IC_Economic_Scripted_Effects.txt:1036-1066`: `money_change_temp_mil = money_change_temp × 1000` for tooltip only, while the input is in billions. Tooltip-only, so low impact, but the units should be explicit.

**P17 (L, error.log) No money-file entries.** `error.log` contains localisation errors (`MLA_l_english.yml:1564`, `ideologies_l_english.yml:133, 588`), audio warnings, and a GL shader dump. A grep for the money-slice filenames returned nothing. `game.log` returned no matches either.

## 6. Open questions

1. What does `ic_pulse` (`IC_scripted_effects.txt:84+`) contain for AI, and does AI ever run `income_effect`, `military_expenditure`, or any debt logic? Read the rest of that effect and the `every_country` block at `_generic_decisions.txt:1528-1534`.
2. Does `_generic_decisions.txt:1533-1534` (`every_country { income_effect = yes }`) fire monthly? If so, P1 is confirmed.
3. What is the full body of `cwic_change_money` (`IC_Economic_Scripted_Effects.txt:1033-1874`)? The read covered only 1033-1103.
4. What defines `defaultCheck` and `austerityCheck`, and what range is `Credit_Rating` on?
5. Where is `current_index` set for `automatic_loan_setting`?
6. What is the base value of `modifier@welfare_spending_modifier` when no welfare policy exists (P5)?
7. Where is `black_ops_expedntiture` set (spelling)? `IC_Econ_2024.txt:1606-1622`.
8. Are `Econ backup/` files loaded? They were not checked for references. [INFERENCE: they are not loaded if no include or descriptor references them.]
9. `income_effect` is about 2400 lines (287-2729). This report read roughly 40%. The middle (470-1226, 1260-1910, 2270-2560 cascade bodies) was only grepped, not read. Resource and export income formulas, subsidy gating (1975-2008), and the lender cascade (2271-2560) need a full read before any money fix.
10. `process_credit_rating` (`IC_Loans_and_Interest_Rate_Effects.txt:329-915`) and `set_interest_rates` (1082-1322) were not read.
11. `IncomeGenerator_federations.txt`: `federation_calculator` (1) and `federation_calculator_global` (27-97) were only listed.
12. `GlobalDebit` is defined in `on_actions/on_startup_defines.txt`, which is the startup hook file. Confirm it is reapplied on load/save or only once.
13. Whether `income_effect` is the only place the GDP feeds `currentMoney` (other than `cwic_cg_monthly_master_tick`, 290).
