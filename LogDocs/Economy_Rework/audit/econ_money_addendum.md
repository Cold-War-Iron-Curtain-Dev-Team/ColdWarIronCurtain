# Addendum to local://econ_money.md (requested by Main)

Note: the write tool cannot append, so this addendum is a separate file. It supersedes the matching parts of econ_money.md where they conflict.

## A1. What AI gets instead of ic_financial_monthly_pulse (decisive)

- AI is excluded from the monthly pulse: `common/on_actions/00_on_actions.txt:38-41` (`is_ai = no`).
- AI runs a mission-style decision instead: `common/decisions/_generic_decisions.txt:1447-1485` (`ic_pulse_one`).
  - `activation`, `available`, `visible` all require `has_country_flag = ic_pulse_one_flag`; `available`/`visible` also require `is_ai = yes`.
  - `complete_effect` (about 1475-1484): `every_country = { ic_pulse = yes }` then `mercenary_calc_global = yes`.
  - `timeout_effect` (1466-1473): clears the flag, then sets it on tag `VTC` and runs `ROOT = { ic_pulse = yes }`. This re-arms the mission.
  - The flag is first set on VTC at `on_startup_defines.txt:3698`.
  - `ai_will_do` factor 1000. Frequency: [INFERENCE] set by AI selection plus the 1-day timeout re-arm, not a monthly schedule.
- `ic_pulse` (`IC_scripted_effects.txt:84-…`) contains **no** treasury, income or debt writes. A file-wide grep for `currentMoney|income_effect|IncomeTotal|cwic_change_money` in that file returns only lines 57-58 (inside `ic_financial_monthly_pulse`). `ic_pulse` covers religion/LGBT drift, oil and other systems, and some resource logic.
- Result: **AI countries never run `income_effect`, military cost, GDP-based tax, debt repayment, default checks, or the lender cascade.** AI treasury only moves through decisions/events that call `cwic_change_money` or edit `currentMoney` directly. [INFERENCE: the AI treasury is therefore largely static, which needs a sim check.]
- AI-side `credit_calculation_work` and the `trade.1` pulse still run from the UNS block of on_monthly (`00_on_actions.txt`, see econ_money.md §1).

## A2. P1 settled: `income_effect` double-run is NOT live

- The `ic_Financial` mission (`_generic_decisions.txt:1508-1541`) has `allowed`, `visible`, `available`, `activation` all `always = no`. It can never become active, so its `complete_effect` (`every_country { income_effect = yes }`, about 1530-1537) never runs. The `timeout_effect` is a comment-only stub ("Retired: ic_financial_monthly_pulse now runs from on_monthly").
- Downgrade P1 from **H** to **L (dead code)**. The block should be deleted, not just left.
- Also stale: `events/IC_Food_Pulse.txt:3` says "runs 1 day after ic_Financial". `ic_Financial_Start` (`_generic_decisions.txt:1543-1563`) is `visible/available = always = no`, `fire_only_once = yes`, and its timeout calls `industrial_pulse` and `monthly_power_projection_gain`. It has no income path.

## A3. Credit rating, interest, default, lender cascade

**`interest_rate_calc`** (`IC_Loans_and_Interest_Rate_Effects.txt:1-55`): calls `process_credit_rating`, `set_interest_rates`, `set_international_commercial_rates` (lines 2-4). Lines 30-53 set `austerityCheck` and `defaultCheck` as `grossdomesticproduct × austerity_multiplier` / `× default_multiplier`. This answers the open question on `defaultCheck`.

**`process_credit_rating`** (`IC_Loans…:329-915`):
- Lines 330-341: hard-coded `Credit_Rating = 10` for USA, UNS, VTC, SOV, ENG.
- Else branch: `Credit_Progress` accumulator. −1 if `CWIC_money_printing_active` (line ~345). +1 if `industrial_base_tier = 6` and not `Credit_Rating_Locked`. Remainder (about 363-915) not read.

**`set_starting_credit_ratings`** (`IC_Loans…:946-1080`): from `National_HDI` tiers, `Credit_Rating` 3-9 (lines 968-1010). Reserve-currency bonus +1 when `CWIC_reserve_currency > 0` and rating < 10 (1017-1020). Penalties −1 when rating > 3 (1036-1058). Floor 3 (1077-1079). The rating scale is therefore **1-10** (answers open question 4 on the scale).

**`set_interest_rates`** (`IC_Loans…:1082-1322`): tiers on `Credit_Rating`. Rating 10 → `Interest_Rate = 1.01`, `max_borrowable_modifier = 0.25` (1087-1094). Rating 9 → `Interest_Rate = 1.015`, `default_multiplier = 15`, `austerity_multiplier = 8` (1097-…). Lower tiers not read.

**`set_international_commercial_rates`** (1323-1436) copies `Interest_Rate` into `ParisCurrentInterestRate` (1325) and the rest of the lender rates. **`set_reserve_rate`** (1437-1454) copies it into `ReserveCurrentInterestRate` (1439).

**Default/austerity, live path** `IncomeGenerator.txt:2208-2268`: as in econ_money.md §3.5. Gates: `pulse_deficit > currentMoney`; default if `defaultCheck < currentDebt` and `Credit_Rating < 10` and not NLF and not `Recent_Default`; austerity via `austerityCheck` otherwise. Penalties: rating −2 (floor 1), `CWIC_inflation_mom += 0.010`, `CWIC_black_market_pressure += 0.10`, events `CWIC_ECON_PENALTIES.2` / `.1`.

**Dead second default block:** `cwic_default_monthly_check` (`IC_Loans…:2312-2342`) has its own default logic (rating −2, inflation +0.010) and sets `Credit_Rating = 7` when missing (2317). It is **never called**: its only caller is commented out at `IC_scripted_effects.txt:72`. Treat as dead (L), but the `CWIC_reserve_candidate` logic at 2396-2400 is also unreachable.

**Lender cascade** `IncomeGenerator.txt:2271-2560`, in order, each gated on `XMaxBorrowable > pulse_deficit`:
- Reserve (2271), World (2361), Morgan (2424), Paris (2451), Barclays (2478), Mitsubishi (2505), Deutsche (2532), Suisse (2559).
- Each block sets `bank_name_prompt = 1`, `purchase_length` = [5, 7, 10], `currentInterestRateCalc` = that lender's rate ×3, `max_index = 2`, `current_index = 0` (block at 2270-2303 shows this for Reserve). This settles the `current_index` open question: it is initialised to 0 here. [INFERENCE: the other blocks follow the same pattern; only Reserve was read in full.]
- Then loan drawdown via `automatic_loan_setting` (`IC_Loans…:1488-1554`) and bookkeeping in `loan_set_assigning_borrowable` (1555-1657). Only the Reserve block was read; the other seven bodies are [INFERENCE] identical apart from the array name and rate source.

## A4. `income_effect` structure (`IncomeGenerator.txt:287-2729`)

Section headers found by grep (line numbers are the header lines):

| Lines | Section |
|---|---|
| 287-325 | Entry: war reparations (288), trade_infrastructure reset (290), GDP influence limit (310-311), DEBUG (316, 325) |
| 326-336 | Calls: `military_expenditure`, `flag_building_macro`, `interest_rate_calc`, domestic bonds, mercenaries, social indices |
| 338-383 | Resets: upgrade estimates (339-378), strategic_forces_expend (380) |
| 384-431 | Social expenses: `get_average_development`, education, public services, welfare, healthcare, policing (385-390), public_expenditure_total, `totalexp` build (397-419), custom_expenses reset (402) |
| 433-457 | Tourism income ×GlobalCredit, into IncomeTotal |
| 459-678 | Overall multipliers and resource income (460-461), other income lines before the CG loop |
| 680-1189 | Consumer goods export income `for_each_scope_loop` over `CgBasicT0_Export_List` (680-683); end of trade income calc (1190) |
| 1192-1237 | Custom income and CG-export credit: `consumer_goods_export_income × trade_credit_factor` (1222-1223, the 2026-07-05 FIX at 1218-1221), `IncomeTotal += custom_income` (1226-1227) |
| 1240-1254 | Expenses: CorruptLoss (1242-1254), added to `totalexp` (1254) |
| 1256-1457 | Resource cost build (`resource_cost` reset 1257) |
| 1458-1920 | CG import costs `for_each_scope_loop` over `CgBasicT0_Import_List` (1459-1461); end of resource_cost (1920) |
| 1922-1943 | Insurgency costs: `total_insurgency_funding = paigc_funding` (1924) |
| 1944-1954 | Policy costs: `total_expenses` = CorruptLoss + military_total_exp (+ others, 1945-1952), subtracted from IncomeTotal (1954) |
| 1955-2135 | Display-only domestic cost (1956-1957); domestic debt bookkeeping; debt repayment loop (2033-2127) |
| 2136-2260 | `TotalDebtk`, `gdpDomesticDebtLimit = 0.4` (2137-2142), default/austerity (2208-2268) |
| 2271-2560 | Lender cascade (see A3) |
| 2630-2729 | AI building priorities (2630), separatism rollup (2698-2700), MNC effects (2712-2721, two calls commented as undefined), military calls (2734-2737), subsidy/corruption (2742-2895), monthly divisors (2897-2900), totals (2918-2920) |

Note: `military_expenditure` (2730) also contains the dead `IncomeCheck` add (2731-2733) from P9 in econ_money.md.

## A5. Other notes from the grep

- `IncomeGenerator.txt:2712-2718`: two `cwic_mnc_*` calls are commented out because the effects are undefined (noted as TODO(MNC) in source). Live calls are at 2719-2721.
- `IncomeGenerator.txt:3085-3119` `GDP_Extra_Calcs`: `checkdone` monthly counter and `initrun` first-run flag. These gate startup behaviour.
- `IC_Loans…:2316-2317`: init defaults (`currentMoney = 0`, `Credit_Rating = 7`) apply only inside the dead `cwic_default_monthly_check`.
