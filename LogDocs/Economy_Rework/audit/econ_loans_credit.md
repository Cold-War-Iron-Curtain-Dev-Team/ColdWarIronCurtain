# CWIC Economy Audit: Loans, Credit Rating, Interest, Lender Cascade, Default/Austerity

Branch Econ-fix. Mod root: `Cold War Iron Curtain/`. Read-only audit. Unverified items are marked `[INFERENCE]`. Paths are relative to the mod root unless noted.

Scope note: the requested "8 lenders" are, in code, 9 external branches plus the domestic liquidity pool (see §2 and §3.4). The Reserve, World Bank, Morgan, Paris, Barclays, Mitsubishi, Deutsche, Suisse and GER branches are all present.

---

## Summary (top findings)

1. **H. Interest is not annualised.** `potential_loan_total = P × (1 + rate/100)` is a single-period charge. A 35-year World Bank loan at 3.37% costs 3.37% of principal in total, not per year (`common/scripted_effects/IC_Loans_and_Interest_Rate_Effects.txt:1488-1553`, `IncomeGenerator.txt:2609-2611` region; see §3.3).
2. **H. Lender caps are never depleted or refreshed in the gate.** The cascade compares `pulse_deficit` against the static `*MaxBorrowable` values, not `Current*MaxBorrowable` (`IncomeGenerator.txt:2270-2600`). Consumption is applied only to `Current*` by `loan_set_assigning_borrowable` (`IC_Loans_and_Interest_Rate_Effects.txt:1555-1656`).
3. **H. GDP-driven caps never move after seeding.** `set_international_commercial_rates` (`IC_Loans_and_Interest_Rate_Effects.txt:1323-1436`) computes deltas from Old/New snapshots. On the second call in a month, Old = New, so the delta is 0. `Current*` values are seeded once in `events/tutorial.txt:32-62` and then never follow GDP.
4. **H. Repayment routing is broken for four lenders.** `loan_payoff_change_to_liquidity` (`IC_Loans_and_Interest_Rate_Effects.txt:1762-1865`) tests status value `4` in the Barclays, Mitsubishi, Deutsche, Suisse and IMF branches. Only Barclays can match. Mitsubishi (5), Deutsche (7), Suisse (6) and GER/IMF (9) repayments never restore their caps.
5. **M. Domestic debt tracker is write-only, and it goes negative.** `domesticTotalDebt` is only ever decremented (`IC_Loans_and_Interest_Rate_Effects.txt:1780-1781`) and is read only in a copy (`IncomeGenerator.txt:2134`).
6. **M. Dead write in the reserve-currency dampener.** `infl_premium` is multiplied before assignment (`IC_Loans_and_Interest_Rate_Effects.txt:~1206-1245`), so the inflation multiplier is dead.
7. **M. Rating 10 has no default or austerity multiplier.** Rating 10 falls through the table in `set_interest_rates` (`IC_Loans_and_Interest_Rate_Effects.txt:1082-1322`). It is excluded from default checks by the `rating < 10` gate, so this is latent.
8. **M. Credit_Progress reset overwrites same-pass penalties.** In `process_credit_rating` (`IC_Loans_and_Interest_Rate_Effects.txt:~620-660`), `Credit_Progress = 0` runs after penalties in the same pass.
9. **M. Finance tab uses a different cap for Barclays.** `scripted_guis/Finance_Tab.txt:2473` uses `BarclaysMaxBorrowable` (static). Other lenders in the same file use `Current*` (2398, 2453, 2492).
10. **M. Interest not annualised in national focuses.** `GDR_1960s.txt:2385, 2635`, `SWE_50s.txt:1608-1633`, `YUG_70s.txt:2909-2932` multiply `pulse_deficit` by an interest value (`1.015`, `Interest_Rate`) as a multiplier. This looks like a unit confusion.
11. **M. Unbounded debt arrays.** Paid-off loan entries are zeroed, not removed (`IncomeGenerator.txt:2117-2121`). Arrays grow forever and are iterated monthly.

---

## 1. Entry points

| Entry point | Location | Frequency | Players / AI |
|---|---|---|---|
| `income_effect` → `interest_rate_calc` | `IncomeGenerator.txt:328`; `IC_scripted_effects.txt:55-75` | Monthly | Gated by `is_ai = no` in `IC_scripted_effects.txt` (per Overview §1). AI: no treasury pulse. |
| `monthly_borrowing_and_interest_pulse` | `IC_scripted_effects.txt:71`; `IC_Loans_and_Interest_Rate_Effects.txt:1658-1760` | Monthly | Same gate as above. |
| Lender cascade (deficit → loan) | `IncomeGenerator.txt:2270-2624` | Monthly, when `pulse_deficit > currentMoney` `[INFERENCE]` | Player path (`is_ai = no`). AI: not reached `[INFERENCE]`. |
| Austerity / default trigger | `IncomeGenerator.txt:2192-2262` | Monthly, inside the deficit branch | Same as cascade. |
| `interest_rate_calc` direct callers | `StartingPoliciesBogosort.txt:124`; `IRAN_1960s.txt:1162`; `KMT_Burma_50s.txt:2272`; `events/tutorial.txt:35` | Event/focus driven | Mixed. |
| `tutorial.2000` init | `events/tutorial.txt:~25-35` | Triggered once | Calls `set_international_commercial_rates`, `set_reserve_rate`, `interest_rate_calc`. Seeds `Current*` caps at `tutorial.txt:32-62`. Trigger for all players not confirmed `[INFERENCE]`. |
| `credit_calculation_work` | `on_actions/00_on_actions.txt:45`; `on_startup_defines.txt:3691`; backup at `IC_Econ_2024.txt:1411` | Startup, then per-country every-tick block `[INFERENCE]` | Players and AI. |
| `set_interest_rates` direct | `IC_Econ_2024.txt:1412` | Per GDP recalc `[INFERENCE]` | Players and AI. |
| `add_loans_effect` | `IC_Economic_Scripted_Effects.txt:613-975`; called from `StartupMoney.txt:694-863`, `SIA_50s.txt:4875` | Startup / focus | AI and players (seeds). |
| `generate_reserve_debt` | `IC_Financial_Scripted_Effects_for_Content.txt:1-46` (calls `automatic_loan_setting` at 45) | Callers not checked `[INFERENCE]` | — |
| Player loan UI | `scripted_guis/Finance_Tab.txt:30-124` (purchase), `:2394-2492` (lender select) | On click | Players only. |
| Player `calculate_loan_details` | `IC_Loans_and_Interest_Rate_Effects.txt:1455-1487` | On GUI refresh | Players only. |

Lender tags referenced by the cascade: `WBK`, `JPM`, `BNP`, `BRC`, `CHY`, `DBA`, `SKA` (defined as colour entries at `common/countries/colors.txt:1498-1522`). `GER` is vanilla (colors.txt:245). Full country definitions were not checked `[INFERENCE]`.

---

## 2. Data model

### 2.1 Credit and rating
- `Credit_Rating` (1-10). Set in `set_starting_credit_ratings` (`IC_Loans_and_Interest_Rate_Effects.txt:946-1081`), adjusted in `process_credit_rating` (329-914), `raise_credit_rating` (916-934), `lower_credit_rating` (936-945).
- `Credit_Progress` (0-99 band, can go negative). Raised past 99 by `raise_credit_rating` (sets back to 0 via `add -100` and clamp at 0). Lowered by `lower_credit_rating` (sets to 25).
- `Credit_Rating_Locked` flag, set for USA/UNS/VTC/SOV/ENG (`:946-1081`, around the first branch).
- `Startup_Credit_Rating_Assigned` flag (`:272-327`).
- `CWIC_reserve_currency` (variable, > 0 gives +1 rating in the HDI branch, `:946-1081`).
- `National_HDI` (read at `:946-1081`).
- `DebtRiskAversionBad` / `DebtRiskAversionGood`: GDP multipliers by rating (`process_credit_rating`).

### 2.2 Interest and multipliers (written by `set_interest_rates` at `:1082-1322`)
- `Interest_Rate` (percent units, e.g. 1.05 means 1.05%). Display divides by 100 (`interest_rate_calc`, `:1-55`).
- `default_multiplier`, `austerity_multiplier` (used as GDP × multiplier thresholds).
- `max_borrowable_modifier`.
- `CWIC_monetary_policy_mult` (default 1, `:1082-1084`).
- `CWIC_reserve_trust` (reserve discount `×(1 − 0.10×CWIC_reserve_trust)`, ~`:1206-1217`).
- `CWIC_inflation_mom` (`infl_premium = CWIC_inflation_mom × 2.0`, halved for reserve issuers, ~`:1219-1245`).
- Oil pricing ×0.95 for USA and SOV (~`:1247-1254`).

### 2.3 Lender rates and caps
- `ReserveCurrentInterestRate` = `Interest_Rate × 0.8` (`set_reserve_rate`, `:1437-1453`).
- `ParisInterestRate`, `BarclaysInterestRate`, `MitsubishiInterestRate` (×1.30), `MorganInterestRate`, `SuisseInterestRate` (×2.25), `DeutscheInterestRate` (×1.60) (`set_international_commercial_rates`, `:1323-1436`).
- `*MaxBorrowable` (static caps): `ReserveMaxBorrowable` (GDP×0.5), `WorldMaxBorrowable` (GDP×0.33), `ParisMaxBorrowable`, `BarclaysMaxBorrowable`, `MitsubishiMaxBorrowable`, `MorganMaxBorrowable`, `SuisseMaxBorrowable`, `DeutscheMaxBorrowable` (GDP×`max_borrowable_modifier`), `IMFMaxBorrowable` (GDP×`max_borrowable_modifier`×1.5), all in `:1323-1453`. `IMFMaxBorrowable` source is `:1323-1436` `[INFERENCE]`.
- `Current*MaxBorrowable` (live balances): Reserve, World, Morgan, Paris, Barclays, Mitsubishi, Deutsche, Suisse, IMF. Seeded in `events/tutorial.txt:32-62` (Reserve at 37, Paris 46, Barclays 49, IMF 61). Written by `loan_set_assigning_borrowable` (`:1555-1656`) and `loan_payoff_change_to_liquidity` (`:1762-1865`).
- `CurrentMaxBorrowable` (player UI cap; set at `Finance_Tab.txt:2398, 2419, 2453, 2473, 2492`).
- `available_liquidity` (domestic bond pool, floored at 1 in `domestic_bond_calc`, `:194-270`).
- `domesticTotalDebt` (`:1780-1781` subtract; `IncomeGenerator.txt:2134` read). No positive writer found.
- `bank_name_prompt` (lender id: 1 Reserve, 2 domestic, 3 Paris, 4 Barclays, 5 Mitsubishi, 6 Suisse, 7 Deutsche, 8 Morgan, 9 GER/IMF fallback, 10 World). Written at `IncomeGenerator.txt:2276,2313,2366,2429,2456,2483,2510,2537,2564,2589` and `IC_Economic_Scripted_Effects.txt:616-916, 1078-1339`.

### 2.4 Loan arrays (per borrower)
- `debtTotalsArray` (remaining principal+interest), `debtOwnerArray` (lender scope, `this_loan_country`), `debtOwnerDomesticStatusArray` (bank id), `debtInterestArray` (`potential_loan_interest`), `debtPaymentArray` (monthly cost).
- Pushed in `automatic_loan_setting` (`:1488-1553`) and `add_loans_effect` (`IC_Economic_Scripted_Effects.txt:936-974`).
- Zeroed when paid (`IncomeGenerator.txt:2117-2121`), never removed.
- Scalars: `currentDebt`, `currentDebtPayments`, `pulse_deficit`, `loan_amount`, `potential_loan_total`, `potential_loan_monthly_cost`, `purchase_amount`, `purchase_length`, `currentInterestRateCalc` (array), `current_index`, `max_index`.

### 2.5 Default / austerity
- `defaultCheck = GDP × default_multiplier`, `austerityCheck = GDP × austerity_multiplier` (`IncomeGenerator.txt:~2192-2262`).
- Flags/vars: `CWIC_DEFAULTED`, `CWIC_MARKET_LOCKOUT`, `CWIC_inflation_mom` (+0.010 on default), `CWIC_black_market_pressure` (+0.10 on default). Consumers not checked `[INFERENCE]`.
- Timed ideas: `Recent_Default` (1825 days), `Recent_Austerity_Measures` (1825 days). Defined in `generic_foci.txt:1904-1915` with `allowed = {always = no}`. Applied by `Economic_Penalties.txt:4-49` (austerity) and `:52-195` (default, removes 10% of buildings).

---

## 3. Formulas (step by step)

### 3.1 Credit rating
1. Start: `set_starting_credit_ratings` (`:946-1081`). Pinned countries get 10 and the lock flag. Others: HDI bands (>0.800→9, >0.700→8, >0.650→7, >0.560→6, >0.480→5, >0.360→4, else 3). Then +1 if `CWIC_reserve_currency > 0`, −1 for FRA/FRE/ITA/WGR/AUS/JAP/GRE/PDG when rating>3, −1 for DDR/POL/CZE/HUN/ROM/BUL/ALB/PRC/KPA/MON when rating>3, +1 for CAN/SWI/SWE when rating<10, clamp 1-10. INO forced 3. No-HDI fallback 3.
   - Note: the clamp is inside the HDI branch only. The no-HDI fallback (3) is not clamped, but it is already in range.
2. Monthly progress (`process_credit_rating`, `:329-914`):
   - USA/UNS/VTC/SOV/ENG pinned to 10 (`:332-340`).
   - Progress increments by industrial-base tier (tier 6 gives +1/+2 by rating band `:565-574`; tier 5/4/3 `:565-574`; tier 2 `:591-600`; tier 1 `:602-609`).
   - DebtRiskAversion: if `currentDebt > DebtRiskAversionBad` then −1 progress; if `< Good` then +1.
   - Penalties: UN_Sanctions −1 (`:526-531`), unrecognized_state −1 (`:537-542`), money printing −1 (`:346`), border war −1, insurgency −1, war −1, surrender_progress >0.25/0.5/0.75 → −1/−2/−3, capitulated −4 (`~690-720`).
   - Reset: `Credit_Progress = 0` at rating=1, rating=9, and rating>6 with tier<5 (`~620-660`).
3. Rating change: `raise_credit_rating` when `Credit_Progress > 99` (`:916-934`): rating +1, progress −100, clamp at 0 if negative. `lower_credit_rating` when progress <0 and rating ≥ 4 (`:936-945`): rating −1, progress = 25.

### 3.2 Interest rate table (`set_interest_rates`, `:1082-1322`)
| Rating | Interest_Rate % | default_mult | austerity_mult | max_borrowable_mod |
|---|---|---|---|---|
| 10 | 1.01 | unset | unset | 0.25 |
| 9 | 1.015 | 15 | 8 | 0.20 |
| 8 | 1.02 | 12 | 6 | 0.18 |
| 7 | 1.05 | 10 | 5 | 0.16 |
| 6 | 1.10 | 8 | 4 | 0.14 |
| 5 | 1.15 | 6 | 3 | 0.12 |
| 4 | 1.20 | 4 | 2 | 0.10 |
| 3 | 1.25 | 3 | 1 | 0.10 |
| 2 | 1.40 | 2 | 0.75 | 0.10 |
| 1 | 1.50 | 1 | 0.5 | 0.10 |

Then: ×`CWIC_monetary_policy_mult`; reserve discount ×(1 − 0.10×`CWIC_reserve_trust`) (~1206-1217); inflation premium (~1219-1245); oil ×0.95 for USA/SOV (~1247-1254).

### 3.3 Loan pricing (per loan)
1. Rate: `currentInterestRateCalc^current_index` (lender-specific: Reserve ×3 branches, domestic IR/IR/1.2·IR/1.44·IR, World hard-coded 1.35, 1.35, 1.62, 1.95, 2.34, 2.81, 3.37, GER hard-coded 7/9/12/15). Source: `IncomeGenerator.txt:2270-2624` and `IC_Economic_Scripted_Effects.txt:613-974`.
2. `calculate_loan_details` / `automatic_loan_setting`:
   - `potential_loan_interest = rate / 100`
   - `potential_loan_total = P × (1 + potential_loan_interest)`, P = `pulse_deficit` (`automatic_loan_setting`, `:1488-1553`).
   - `potential_loan_monthly_cost = potential_loan_total / (tenor_years × 12)`.
   - **Issue (H):** the interest is never multiplied by years, so the total charge is `rate%` of principal regardless of tenor. A 5-year loan at 1.35% costs 1.35%; a 35-year loan at 3.37% costs 3.37%. Annualised, the rate is `rate / tenor`. `[INFERENCE]` that the intent is annual; the code comment and display (`interest_rate_calc:1-55`) suggest annual.
3. `loan_amount = potential_loan_total`; `currentDebt += loan_amount`; arrays pushed; `currentDebtPayments += debtPayment`; `loan_set_assigning_borrowable` (`:1555-1656`).
4. `loan_set_assigning_borrowable` subtracts principal from the matching `Current*MaxBorrowable` (not the static caps).

### 3.4 Lender cascade (`IncomeGenerator.txt:2270-2624`)
Order and gates (`pulse_deficit` = deficit):
1. Reserve (bank 1), gate `ReserveMaxBorrowable > pulse_deficit` (`:2270-2274`); tenors 5/7/10 y; rate `ReserveCurrentInterestRate` ×3.
2. Domestic (bank 2), gate `available_liquidity > pulse_deficit` (`:2279-2283`); tenors 5/10/15/20 y; rates IR, IR, 1.2×IR, 1.44×IR.
3. World Bank (bank 10), gate `WorldMaxBorrowable > pulse_deficit` (`:2365`); tenors 5-35 y; rates 1.35-3.37 (hard-coded).
4. Morgan (bank 8), `JPM`, 5 y, gate `MorganMaxBorrowable` (`:2428-2431`).
5. Paris (bank 3), `BNP`, 5 y (`:2455`).
6. Barclays (bank 4), `BRC`, 5 y (`:2482`).
7. Mitsubishi (bank 5), `CHY`, 5 y (`:2509`).
8. Deutsche (bank 7), `DBA`, 5 y (`:2536`).
9. Suisse (bank 6), `SKA`, 5 y (`:2563`).
10. Fallback `else` (bank 9), `GER`, uncapped; tenors 1/2/3/4 y; rates 7/9/12/15; `current_index = 1` (`:2561-2623`).
11. `automatic_loan_setting = yes` (`:2624`).

Notes:
- Gates use the static caps, and `pulse_deficit` is compared to them, not to `Current*` (see §5 H2).
- The 5-year-only branches set `current_index = 0` `[INFERENCE]` (index mapping not checked).
- Bank 9 is labelled IMF in `loan_set_assigning_borrowable` (`:1648-1654`, `CurrentIMFMaxBorrowable`), but the cascade calls it GER.

### 3.5 Pulse deficit
- `pulse_deficit = 0`, then `pulse_deficit = currentMoney` and `×= -1` when `currentMoney` is negative (`IncomeGenerator.txt:2012-2024`). The exact conditions (2013-2019) were not read `[INFERENCE]`.
- The deficit branch is `if pulse_deficit > currentMoney` (~`:2191`).

### 3.6 Repayment (monthly, `IncomeGenerator.txt:2035-2125`)
1. For each `debtPaymentArray^i` with `debtTotalsArray^i > 0`: subtract the payment from `debtTotalsArray^i`, `currentMoney`, `currentDebt`; add to `currentDebtPayments` (`:2035-2070`).
2. Owner credit: if `debtOwnerArray^i` is not THIS and not GER, `var:debtOwnerArray^i.currentMoney += payment`. For GER, `influence_array_val` is reduced (`:2071-2104`). For domestic loans the owner is THIS, so no credit `[INFERENCE]`.
3. `loan_payoff_change_to_liquidity` (`:2105`) restores the lender cap (see §5 H4).
4. When the remaining total is ≤0, the entries are zeroed (`:2106-2125`).

### 3.7 Domestic bond pool (`domestic_bond_calc`, `:194-270`)
- Floor `available_liquidity` at 1.
- `outcrowding_limit = 10 × office_park_total × (1 + modifier@office_park_income_bonus)`.
- Replenish by `outcrowding_limit × rate` per month when liquidity is below the limit; rate 6.5% / 5% / 3.5% by limit band (100 / 500). No clamp to limit, so liquidity can exceed it `[INFERENCE]`.
- Called at `IncomeGenerator.txt:329`.

### 3.8 Austerity and default (`IncomeGenerator.txt:2126-2262`)
- Default: if `defaultCheck < currentDebt`, rating <10, `defaultCheck ≠ 0`, not NLF, and not `has_idea Recent_Default`. Sets `CWIC_DEFAULTED`, `CWIC_MARKET_LOCKOUT`, rating −2 (floor 1), `CWIC_inflation_mom += 0.010`, `CWIC_black_market_pressure += 0.10`, fires `CWIC_ECON_PENALTIES.2` (`Economic_Penalties.txt:52-195`).
- Austerity: if `austerityCheck < currentDebt` and not default, fires `CWIC_ECON_PENALTIES.1` (`Economic_Penalties.txt:4-49`).
- `gdpDomesticDebtLimit` (`:2141-2193`): 0.4 + 0.1 per GDP threshold (>1, >5, >10, >100, >1000). Consumers not checked `[INFERENCE]`.
- `Interest_Rate = 0` fallback to 1.04 (~`:2196-2202`) is effectively dead (see §5 L).

---

## 4. Interactions

- **Treasury (`income_effect`).** `interest_rate_calc` is invoked at `IncomeGenerator.txt:328` and the cascade and repayments run in the same pulse. Ordering (`IC_scripted_effects.txt:55-75`): `income_effect` → `monthly_borrowing_and_interest_pulse` (`:71`). The `is_ai = no` gate means AI treasuries are excluded from this pulse (Overview S1).
- **GDP (`gdp_calculation_effect` in `IC_Econ_2024.txt`).** `IC_Econ_2024.txt:1411-1412` runs `credit_calculation_work` (backup) and `set_interest_rates` directly. The GDP-based caps and multipliers read GDP at call time. The problem is that the `Current*` caps are not refreshed (§5 H3).
- **Trade.** Lender-held debt repayments credit lender tags' `currentMoney` (`:2071-2104`). Whether lender tags run any treasury logic is unknown `[INFERENCE]` (likely AI with no pulse, so repayments accumulate without effect).
- **Taxes / policies.** `StartingPoliciesBogosort.txt:124` calls `interest_rate_calc`. Policy effects on `CWIC_monetary_policy_mult`, `CWIC_reserve_trust`, `CWIC_inflation_mom` were not traced `[INFERENCE]`.
- **Focus-driven debt.** `GDR_1960s.txt:2377-2398, 2627-2652`, `SWE_50s.txt:1608-1633`, `YUG_70s.txt:2909-2932`, `FRA_scripted_effects.txt:501-515` set `pulse_deficit` and multiply by interest-like values (§5 M5).
- **Seed loans.** `StartupMoney.txt:694-863` and `SIA_50s.txt:4875` call `add_loans_effect`, which pushes arrays and calls `loan_set_assigning_borrowable` directly (no `automatic_loan_setting`), so it is a separate path with the same rate/total formula.
- **Insurgency.** `CWIC_Insurgency_Economy_Effects.txt:46-47` zeroes money and debt (Overview B2). This bypasses the arrays, so arrays and `currentDebt` can desync `[INFERENCE]`.
- **UI.** `Finance_Tab.txt:30-124` (purchase/repay), `:2394-2492` (lender select). Uses `CurrentMaxBorrowable` set from `Current*` for most lenders, but `Barclays` from the static cap (`:2473`).
- **Military subsidy.** `IncomeGenerator.txt:2003` hard-codes SOV.currentMoney (Overview B5).

---

## 5. Problems

Severity: H = wrong numbers or mechanics in normal play; M = incorrect but limited; L = dead or cosmetic.

**H1. Interest not annualised.** `IC_Loans_and_Interest_Rate_Effects.txt:1488-1553` (`automatic_loan_setting`), `:1455-1487` (`calculate_loan_details`), `IC_Economic_Scripted_Effects.txt:936-974` (add_loans). Total charge = P × rate/100 independent of tenor. All loans are effectively near-interest-free over their term. Fix: `potential_loan_interest = rate/100 × tenor_years` or equivalent `[INFERENCE]` for intended semantics.

**H2. Lender gates use static caps, not live balances.** `IncomeGenerator.txt:2270-2600` compare `pulse_deficit` against `*MaxBorrowable` (not `Current*`). `loan_set_assigning_borrowable` (`IC_Loans_and_Interest_Rate_Effects.txt:1555-1656`) decrements only `Current*`. Lender capacity is effectively unlimited while static caps exceed the deficit.

**H3. `Current*` caps never follow GDP.** `set_international_commercial_rates` (`IC_Loans_and_Interest_Rate_Effects.txt:1323-1436`) and `:1658-1760` apply deltas between Old and New snapshots. Called twice per month (`interest_rate_calc` at `:1-55` plus the `tutorial.2000` path and `IC_Econ_2024`; exact second call site `[INFERENCE]`), so the second call sees Old = New and applies 0. Seeds in `tutorial.txt:32-62` are the only write to the `Current*` values from the GDP side.

**H4. Repayment routing is broken for four lenders.** `IC_Loans_and_Interest_Rate_Effects.txt:1762-1865`:
- Mitsubishi (`:~1825-1830`, comment `#5`) checks status `4` (should be `5`).
- Deutsche (`#7`) checks `4` (should be `7`).
- Suisse (`#6`) checks `4` (should be `6`).
- IMF/GER (`#9`) checks `4` (should be `9`).
- Only the Barclays branch can match status 4. Repayments to those four lenders never restore their `Current*` caps.

**H5. Interest and debt-loan multiplier misuse in focus scripts.** `GDR_1960s.txt:2385, 2635` (pulse_deficit 250 × 1.015), `SWE_50s.txt:1608-1633`, `YUG_70s.txt:2909-2932` (Interest_Rate as multiplier), `FRA_scripted_effects.txt:501-515` (×1.042). These use interest-like values as multipliers on principal, which is inconsistent with `automatic_loan_setting`. Treat as M until intent is confirmed `[INFERENCE]`.

**M1. `domesticTotalDebt` write-only and negative.** Only decremented at `IC_Loans_and_Interest_Rate_Effects.txt:1780-1781`. Read at `IncomeGenerator.txt:2134`. Will go negative after any status-2 repayment. Either add a positive writer or remove.

**M2. Domestic repayment does not restore liquidity.** `loan_payoff_change_to_liquidity` status-2 branch (`:1775-1781`) decrements `domesticTotalDebt` only; `available_liquidity` is not restored, so domestic bonds are only replenished via `domestic_bond_calc` `[INFERENCE]`.

**M3. Reserve dampener writes before assignment (dead inflation logic).** `IC_Loans_and_Interest_Rate_Effects.txt:~1206-1245`: the dampener multiplies `infl_premium` before it is assigned, so the subsequent write is overwritten and the inflation multiplier does nothing `[INFERENCE]` (exact lines not reread).

**M4. Rating 10 lacks default and austerity multipliers.** `IC_Loans_and_Interest_Rate_Effects.txt:1082-1322` (rating 10 branch). Gated out by `rating < 10` in `IncomeGenerator.txt:2192-2262`, so latent. If the gate changes, values will be stale or unset.

**M5. Credit_Progress reset overwrites same-pass penalties.** `IC_Loans_and_Interest_Rate_Effects.txt:~620-660`: `Credit_Progress = 0` at rating=1, rating=9, and rating>6 with tier<5, applied after penalties in the same pass, so penalties are lost.

**M6. Finance tab uses a different cap for Barclays.** `scripted_guis/Finance_Tab.txt:2473` uses `BarclaysMaxBorrowable` while lines 2398, 2453, 2492 use `Current*`. Inconsistent.

**M7. Unbounded loan arrays.** `IncomeGenerator.txt:2117-2121` zeroes entries, never removes. Every monthly repayment loop and `for_each` iterates the full history `[INFERENCE]` on cost. Perf M/L.

**M8. Insurgency debt zeroing desyncs arrays.** `CWIC_Insurgency_Economy_Effects.txt:46-47` zeroes `currentDebt` without clearing arrays `[INFERENCE]`. Next repayment pass can drive `currentDebt` negative.

**M9. Lender-tag repayments credit AI tags.** `IncomeGenerator.txt:2071-2104` credits `currentMoney` to lender tags. Those tags have no treasury pulse (`is_ai=no`), so the money is stranded `[INFERENCE]`.

**L1. Dead duplicate block.** `IC_Loans_and_Interest_Rate_Effects.txt:27-53` duplicates the assignments at 36-53; the first set is overwritten.

**L2. Dead dual-condition block.** Rating-band check `OR(rating=2 or 3) AND rating>5` in `process_credit_rating` (~580-589) is unsatisfiable.

**L3. `Interest_Rate = 0` fallback is dead.** `IncomeGenerator.txt:~2196-2202`: `set_interest_rates` always sets a value.

**L4. Bank 9 naming.** `IncomeGenerator.txt:2589` (GER) vs `loan_set_assigning_borrowable` `:1648-1654` (IMF). Cosmetic but misleading; `CurrentIMFMaxBorrowable` is never checked.

**L5. Raise without ceiling.** `raise_credit_rating` (`:916-934`) has no clamp at 10. Whether `process_credit_rating` guards rating 10 before calling it was not verified `[INFERENCE]`.

**L6. Starting rating clamp.** `set_starting_credit_ratings` clamp (`:946-1081`) is only in the HDI branch. INO override (3) and fallback (3) are in range, so no current impact.

---

## 6. Open questions

1. Is the interest rate meant to be annual? If yes, H1 is a bug; confirm the intended formula with the designer.
2. Where exactly is `set_international_commercial_rates` called a second time per month? (Confirm for H3.)
3. Does `tutorial.2000` run for every player, or only for tutorial starts? If not, `Current*` caps are undefined in normal starts (`tutorial.txt:32-62`).
4. Do AI countries ever reach the cascade (`IncomeGenerator.txt:2270-2624`) or `pulse_deficit` (`:2012-2024`)? Overview S1 says no treasury pulse for AI.
5. What are the conditions at `IncomeGenerator.txt:2013-2019` for the `pulse_deficit` sign flip?
6. What consumes `CWIC_inflation_mom` and `CWIC_black_market_pressure`? Not checked.
7. What consumes `gdpDomesticDebtLimit` (`IncomeGenerator.txt:2141-2193`)? Not checked.
8. Are `generate_reserve_debt` and `add_loans_effect` callers complete? Only the listed callers were checked.
9. `IC_Loans_and_Interest_Rate_Effects.txt:1866` (`get_decade_industrial_base_capita`) and `:2090` were not read.
10. `cwic_default_monthly_check` (`:2312`) and `cwic_reserve_currency_update` (`:2347`) were not read. Overview B7 says `cwic_default_monthly_check` is dead (caller commented at `IC_scripted_effects.txt:72`).
11. Lender country definitions (`common/countries/` beyond colors) were not checked, so tag existence is confirmed only in colors.
