# Audit: income_effect cost section and IncomeTotal lifecycle

Scope: `Cold War Iron Curtain/common/scripted_effects/IncomeGenerator.txt` 1256-1960 (cost section) and 2560-2740 (lender cascade boundary, `IncomeTotal` reset at 2663, end-of-pulse calls). Paths below are relative to `Cold War Iron Curtain/` unless noted. Unverified claims are marked `[INFERENCE]`.

## Summary

- **Insurgency lag (H).** `total_insurgency_funding` is subtracted from `IncomeTotal` at IncomeGenerator.txt:1919 before it is recomputed at 1924-1942. The charge therefore uses the previous pulse's value. Nothing resets it earlier in the pulse.
- **Import dedupe (H).** Each import-list loop sets a temp flag on the first element and never clears it. Only the first supplier per resource is counted. Lines 1349-1869, per list.
- **Monthly import accumulators are never reset on the monthly path (H, `[INFERENCE]`).** `*ImportTargetMonthly^THIS` is only ever added to (`IC_Trade_Scripted_Effects.txt:1281` and siblings). The only `= 0` resets are in `scripted_guis/Trade_Tab.txt:1188-1459`, which is GUI-driven.
- **focus `custom_expenses` deltas are wiped before they are charged (H, `[INFERENCE]` on intent).** `custom_expenses` is cleared at IncomeGenerator.txt:402, and the focus files add to it between pulses. Only reparations are re-added before the charge at 1916.
- **`IncomeTotal` carry-over.** Within `income_effect` there is no loss: every read of `IncomeTotal` (1236, 1249, 1913-1954, 1969, 2006, 2010, 2027) occurs before the reset at 2663. The pulse starts with no initialisation, so it relies on the previous pulse's reset. Writes outside the pulse (`IC_Econ_2024.txt:1328`, `2701-2703`) need a caller check (open question Q1).
- **AI gap (H, `[INFERENCE]`).** `income_effect` is invoked monthly only for `is_ai = no` (`common/on_actions/00_on_actions.txt:39-40`). The only other caller found is the `ic_Financial` mission, which has `always = no` gates and therefore cannot fire (`decisions/_generic_decisions.txt:1520-1537`).
- **Subsidy block uses undefined variables (M).** `welfare_cost`, `cpi_cost`, `edu_cost`, `health_cost`, `pub_cost` have no writer in `common/` (grep, see Q4). `SubsidiyCheck` has no reader.

## 1. Entry points

| Caller | File:line | Frequency | Who |
|---|---|---|---|
| `ic_financial_monthly_pulse` → `income_effect = yes` | `scripted_effects/IC_scripted_effects.txt:2, 57` | Monthly via on_monthly | Human players only (`on_actions/00_on_actions.txt:39-40`, `is_ai = no`) |
| `income_effect = yes` in tutorial | `events/tutorial.txt:125` | One-off | Tutorial |
| `every_country { income_effect = yes }` in mission `ic_Financial` | `decisions/_generic_decisions.txt:1520-1537` | Would be on completion | AI path, but gated `allowed/available/activation = always = no` (`_generic_decisions.txt` block `ic_Financial`), so [INFERENCE] never fires |
| `ic_pulse` / `ic_pulse_monthly` | `on_actions/00_on_actions.txt:22`, `on_startup_defines.txt:3256-3257`, `decisions/_generic_decisions.txt:1471, 1477` | Monthly | Do not call `income_effect` (grep: no `income_effect = yes` there) |

`income_effect` begins at IncomeGenerator.txt:287. It calls `military_expenditure = yes` at line 326 (the effect is defined at 2730). Because of that call, the military totals are fresh before the charge at 1947.

## 2. Data model

| Variable | Meaning | Written | Read |
|---|---|---|---|
| `IncomeTotal` | Running net treasury delta for the pulse | 453 (tourism add), 1227/1230/1233 (custom, resource, CG export), 1328 (reset, in `IC_Econ_2024.txt`), 1913, 1916, 1919, 1954, 2006 (subsidy), 2663 (reset, in `IncomeGenerator.txt`), `IC_Econ_2024.txt:2701-2702` (tax add) | 1236, 1249, 1969, 2010, 2027 |
| `IncomeCheck` | Copy for UI/planning | 2027, `2703` (IC_Econ), 1329 | `2030`, `2732` |
| `resource_cost` | Sum of import costs | Reset 1257; `+=` in 1274-1909 region via sums | 1911-1913, 1963 |
| `custom_expenses` | Reparations plus focus charges | Reset 402; `+=` 416 (reparations); focus files (`national_focus/SOV_Ustinov.txt`, `SOV_Kaganovich.txt`, `50s_SRT.txt:1150`, `Trees for 0.35/stalintreereworknew.txt:1410, 1500, 1505`) | 419, 1916, 1966 |
| `total_insurgency_funding` | Insurgency charge | Never reset in 1256-1347; set at 1924 from `paigc_funding`, then `+=` los/vie/vin/mpla/unita/fnla at 1925-1942 | 1919, 1960 |
| `paigc_funding`, `mpla_funding`, `unita_funding`, `fnla_funding`, `los_funding`, `vie_funding`, `vin_funding` | Per-country funding levels | `decisions/Angola_Decisions.txt:1751, 1777, 1881, 1910, 2011, 2307`; `decisions/Portugese_Colonial_Wars.txt:100, 125, 346, 365, 398, 429`; `national_focus/USA_CIA_Shared_60s.txt:1140`; `IC_scripted_effects.txt:7056` | 1924-1942 |
| `CorruptionLevel` | Corruption rate | Many `decisions/` and `national_focus/` files (not exhaustively checked) | 1243-1246 |
| `CorruptLoss`, `CorruptIncomeLoss` | Corruption charge | 1243-1252, 1946 (`total_expenses`), 1957 (`domestic_cost`) | 1254, 1946, 1957 |
| `totalexp` | Display total of all costs | 397-419, 1254, 1911 | UI: `interface/COMECON_Redux.gui:1148`, `interface/Finance_Tab.gui:3388`. Also written by `scripted_guis/COMECON.txt:1369-1377, 1421-1429` on `SOV.COMECON1` scope (collision, see 5.8) |
| `total_expenses` | Policy and public cost charge | 1945 (reset), 1946-1952 | 1954 |
| `public_expenditure_total` | Public services plus welfare plus healthcare | 392-395 | 399 |
| `military_total_exp` | Military total | `IC_Econ_2024.txt:2918-2921` (`mil_gui_total`+`navy_gui_total`+`af_gui_total`+`sf_gui_total`) | 398, 1947 |
| `welfare_expenditure`, `healthcare_expenditure`, `policing_expenditure`, `education_expenditure`, `public_services_expenditure` | Policy costs | `IC_Econ_2024.txt:1537-1589` (welfare), `1590-1605` (healthcare), `1606-1622` (policing), `1623-` (education), public services (not read) | 385-390, 1948-1952 |
| `domestic_cost` | Display only | 1957-1966 | No reader found in `common/`, `interface/`, `scripted_guis/` (grep). Only a commented reference in `COMECON.txt:1374, 1426` [INFERENCE] dead |
| `SubsidiyCheck` | Subsidy base (25% of IncomeTotal) | 1969-1972 | No reader found [INFERENCE] dead |
| `subsidiy_base` | Soviet subsidy payment | 1978-2006 | Used at 2006 |
| `pulse_deficit` | Deficit flag | 2012-2024 | Lender cascade |
| `ImportTargetMonthly^`, `ImportTarget^`, `ImportTargetAmount^` | Per-trade bookkeeping keyed by partner | Writers `IC_Trade_Scripted_Effects.txt:516, 882, 979` (chromium), `1281, 1595, 1692` (food), plus the same pattern for other goods; resets only in `scripted_guis/Trade_Tab.txt:1188-1459` | `IncomeGenerator.txt:1363, 1381, 1399, 1417, 1435, 1453, 1472-1869` |
| `*_Import_List` | Partner list (deduped) | `IC_Trade_Scripted_Effects.txt:1282-1295` (pattern `for_loop_effect` + `add_to_array`, flag `found`) and equivalent sites `464, 908, 1005, 1621, 1718, 1965, 2333, 2430, 2583, 2680, 2936, 3386, 4369, 4466, 3694, 4055, 4152, 7637, 7760`. No `clear_array` found (grep) | IncomeGenerator loops |

## 3. Formulas (step by step)

Within `income_effect` (line numbers are IncomeGenerator.txt unless noted):

1. Pre-pass (385-419):
   - `calc_public_services/welfare/healthcare/policing/education` run (385-390).
   - `public_expenditure_total = public_services + welfare + healthcare` (392-395).
   - `totalexp = military_total_exp + public_expenditure_total + policing + education` (397-401).
   - `custom_expenses = 0` (402). Reparations: `custom_expenses += -economic_modifier_war_reparations` if negative (410-416).
   - `totalexp += custom_expenses` (419).
2. Income (452-1233): `IncomeTotal` accumulates tourism (453), `custom_income` (1227), `resource_income` (1230), `consumer_goods_export_income` (1233). `display_income = IncomeTotal` (1236).
3. Corruption (1242-1254): `CorruptIncomeLoss = CorruptionLevel * 0.5` (1243-1246). `CorruptLoss = IncomeTotal * CorruptIncomeLoss` (1249-1252). `totalexp += CorruptLoss` (1254). No clamp on `CorruptionLevel` is visible in this block [INFERENCE: upper bound unverified].
4. Import resets (1256-1347): `resource_cost`, `consumer_goods_import_cost`, the seven commodity imports, and all `cg*_imports` are zeroed. `total_insurgency_funding` is not.
5. Import accumulation (1349-1869): for each list, for each element `i`, if `X_import_check` is 0 it sets the flag to 1 and adds `ROOT.<x>ImportTargetMonthly^THIS` to `<x>_imports`. Commodity-specific mapping:
   - Food list → `rubber_imports` (1363)
   - Nuclear list → `chromium_imports` (1381)
   - Oil list → `oil_imports` (1399)
   - Steel list → `steel_imports` (1417)
   - Aluminium list → `aluminium_imports` (1435)
   - RareEarth list → `tungsten_imports` (1453)
   - CgBasic/Durable/Vehicles T0-5 and Electronics T1-5 → matching `cg*_imports` (1472-1869)
   - Only the first element of each list is counted (see 5.2).
6. Consumer goods import sum (1873-1899): `consumer_goods_import_cost` = sum of all `cg*_imports`.
7. `resource_cost = consumer_goods_import_cost + aluminium + rubber + tungsten + steel + chromium + oil` (1901-1909). `totalexp += resource_cost` (1911).
8. Subtractions from `IncomeTotal`:
   - `-= resource_cost` (1913)
   - `-= custom_expenses` (1916)
   - `-= total_insurgency_funding` (1919) — **old value** (see 5.1)
9. Insurgency recompute (1923-1942): `total_insurgency_funding = paigc_funding` (1924), then `+= los, vie, vin, mpla, unita, fnla` funding.
10. Policy charge (1945-1954): `total_expenses = 0` (1945). Adds `CorruptLoss` (1946), `military_total_exp` (1947), `welfare` (1948), `policing` (1949), `education` (1950), `healthcare` (1951), `public_services` (1952). `IncomeTotal -= total_expenses` (1954). `total_expenses` is disjoint from `resource_cost`, `custom_expenses`, and `total_insurgency_funding` (no double count).
11. Display (1956-1966): `domestic_cost = CorruptLoss + total_insurgency_funding + resource_cost + custom_expenses` (`domestic_cost` is display-only, [INFERENCE]).
12. Soviet subsidy (1968-2008): `SubsidiyCheck = 0.25 * IncomeTotal` (1968-1973, unused). If `Soviet_Subsidies` is set (1976), `subsidiy_base = land_army_expenditure + welfare_cost + cpi_cost + edu_cost + health_cost + pub_cost`, times 0.25 (per grep, the undefined terms contribute 0). `SOV.currentMoney -= subsidiy_base` and `IncomeTotal += subsidiy_base` (2006).
13. Credit (2009-2011): `currentMoney += IncomeTotal` (2010).
14. Pulse end (2012-2030): `pulse_deficit` set (2012-2024), `IncomeCheck = IncomeTotal` (2027), `IncomePlannerCheck = IncomeCheck` (2030).
15. Lender cascade (2034-2560, not read in detail). `currentDebtPayments += debtPayment` also appears in `national_focus/GDR_1960s.txt:2409, 2659`.
16. Reset (2663): `IncomeTotal = 0`, after `ai_economic_planning = yes`, followed by building-total resets (2663-2700). `IncomeTotal` has no reads after this point inside the effect.
17. End-of-pulse index calls (2663-2728): `cwic_*` calls for capital controls, black market, FX, inflation, reserve currency, stability, nationalisation, governance, corporate risk, global budget, `cwic_country_add_all_corp_profits`, MNC effects, and conditional `CWIC_evaluate_national_crises`. Two commented `cwic_*` MNC TODO lines reference undefined effects (see 5.9).
18. `military_expenditure` (2730-2921) is a separate effect that ends the `income_effect` block. Its `calc_*_army_expenditure` calls (2735-2738) and monthly division (2898-2901) feed `land_army_expenditure`, which the subsidy block reads.

**Answer to the lifecycle question.** Nothing added to `IncomeTotal` is lost within the pulse. The 2663 reset comes after the last reads (2006, 2010, 2027). Between pulses, `IncomeTotal` is carried only if written outside `income_effect`: `IC_Econ_2024.txt:1328` (`= 0`) and `2701-2703` (adds tax totals). Whether those run inside the pulse is Q1. There is no initialisation at the start of the pulse; the first write (453) is an `add`, so the pulse depends on the 2663 reset from the previous pulse.

## 4. Subsystem interactions

- **Treasury (`income_effect`):** This section feeds `IncomeTotal`, which is credited to `currentMoney` at 2010. Costs in 1913-1954 reduce it.
- **GDP (`gdp_calculation_effect`, `IC_Econ_2024.txt`):** The policy cost inputs come from `calc_*_expenditure` in `IC_Econ_2024.txt:1537-1622`, which scale with `average_development` and population (e.g. 1566-1567, 1590-1605 using `max_manpower/30000`). I did not read the GDP effect in this slice [INFERENCE: not verified].
- **Trade:** Import costs (`*ImportTargetMonthly^THIS`) are written by `IC_Trade_Scripted_Effects.txt` (`buy_food` at 1243-1303 and siblings). Matching income (`resource_income`) is on the exporter side; this slice did not verify the exporter's counterpart.
- **Taxes and policies:** `IC_Econ_2024.txt:2701-2703` adds `total_personal_income_tax` and `total_corporate_tax` into `IncomeTotal`. Caller not verified (Q1).
- **UI:** `interface/Finance_Tab.gui:3299, 3388` and `interface/COMECON_Redux.gui:1138, 1148` read `display_income` and `totalexp`.
- **Military:** `military_expenditure` (2730) produces `land_army_expenditure` used in the Soviet subsidy (2006) and in `military_total_exp` (2918-2921).

## 5. Problems

**5.1 H — Insurgency charge uses last pulse's value.** `IncomeGenerator.txt:1919` subtracts `total_insurgency_funding`, which is recomputed at 1924-1942. The reset block (1256-1347) does not zero it. Result: charge is one month stale, and zero on the first pulse. Also `IncomeGenerator.txt:1960` displays the current value, so display and charge disagree. Fix: move the recompute above 1919, or subtract the recomputed value.

**5.2 H — Import loops count only the first supplier.** Loops at `IncomeGenerator.txt:1349-1869` set `X_import_check = 1` with `set_temp_variable` on the first element and never clear it. Each later element hits `NOT check_variable X_import_check=1` and skips. Confirm the scope semantics: [INFERENCE] temp variables persist across loop iterations in one effect execution. Impact: import cost for each commodity is one partner's price, not the sum. The same bug exists in all 18 loop blocks (Food, Nuclear, Oil, Steel, Aluminium, RareEarth, CgBasicT0-5, CgDurableT0-5, CgVehiclesT0-5, CgElectronicsT1-5).

**5.3 H — Monthly import accumulators never reset on the monthly path (`[INFERENCE]`).** `IC_Trade_Scripted_Effects.txt:1281` (`ROOT.foodImportTargetMonthly^THIS += price_of_goods`) and the same pattern at 516, 882, 979, 1595, 1692 accumulate. Grep for `ImportTargetMonthly^... = 0` in `common/`, `events/`, `interface/` finds resets only in `scripted_guis/Trade_Tab.txt:1188-1459`, which is GUI-driven. If the monthly flow does not clear them, the charge grows without bound. Verify the trade-pulse path (Q2).

**5.4 H — Focus-driven `custom_expenses` are wiped before being charged (`[INFERENCE]` on intent).** `IncomeGenerator.txt:402` clears `custom_expenses` at pulse start (the FIX note says the old behaviour accumulated forever, `IncomeGenerator.txt:402`). Focus files add to `custom_expenses` between pulses (e.g. `national_focus/SOV_Ustinov.txt`, `SOV_Kaganovich.txt`, `50s_SRT.txt:1150`, `Trees for 0.35/stalintreereworknew.txt:1410, 1500, 1505`). Only reparations are re-added at 410-416 before the charge at 1916. So focus-driven amounts are never charged. Either the design is "one-shot charge" (then the reset should not clear it) or "standing charge" (then the reset should not be used). Decide which, then fix the reset.

**5.5 H — AI monthly treasury path appears absent (`[INFERENCE]`).** `on_actions/00_on_actions.txt:39-40` calls `ic_financial_monthly_pulse` only for `is_ai = no`. `income_effect` is also called only by `tutorial.txt:125` and `decisions/_generic_decisions.txt:1534` in the `ic_Financial` mission, which is gated `always = no` (lines ~1520-1537). Consequence: AI countries may never charge or credit income, and `currentMoney` for AI never changes here. Verify (Q3).

**5.6 M — Undefined subsidy inputs.** `IncomeGenerator.txt:1978-2005` (subsidy base) reads `welfare_cost`, `cpi_cost`, `edu_cost`, `health_cost`, `pub_cost`. Grep for `name =` writes across `common/`, `events/`, `interface/` finds none. Readers only in `scripted_guis/COMECON.txt:1372-1377, 1424-1429`. Result: only `land_army_expenditure` contributes. Either the terms are dead or writers are missing. Also `SubsidiyCheck` (1968-1972) has no reader.

**5.7 M — Stale comment on welfare.** `national_focus/SOV_Brezhnev.txt:562` says "welfare_expenditure itself isn't used anymore", but `IncomeGenerator.txt:1948` charges it and `392-395` includes it in `public_expenditure_total`. Remove the stale comment or the usage.

**5.8 M — `totalexp` collision.** `scripted_guis/COMECON.txt:1369-1377, 1421-1429` writes `totalexp` on `SOV.COMECON1`. `income_effect` writes `totalexp` at 397-419 and 1254, 1911 on the owning country. Whether these scopes overlap is [INFERENCE]; if the COMECON write runs on a country that also runs the pulse, the display is overwritten.

**5.9 L — Dead MNC references.** Two commented TODO(MNC) lines reference `cwic_country_mnc_presence_growth` and `cwic_mnc_set_auto_invest_pool_flags_country`, which are not defined in the scanned files (`IncomeGenerator.txt`, 2663-2728 region). Remove or define.

**5.10 L — `domestic_cost` and `SubsidiyCheck` are write-only** (1957-1966, 1968-1972). No readers found.

**5.11 L — Reset fragility.** `IncomeTotal` has no initialisation at pulse start. The reset at 2663 is the only one, and it happens after `income_effect` reaches its tail. Adding a `set_variable IncomeTotal = 0` at line 288 region would remove the dependency.

**5.12 L — Unclamped `CorruptionLevel`.** `IncomeGenerator.txt:1243-1246` multiplies by 0.5 with no clamp. If `CorruptionLevel > 2`, `CorruptIncomeLoss > 1` [INFERENCE: writers unverified].

## 6. Open questions

- **Q1.** Who calls the `IncomeTotal = 0` at `IC_Econ_2024.txt:1328` and the tax adds at `2701-2703`? Are they inside `income_effect`? If not, they feed the pulse from outside.
- **Q2.** Is there a monthly reset of `*ImportTargetMonthly^*` in the trade pulse (not found in `common/` grep)? If not, 5.3 is confirmed.
- **Q3.** Do AI countries run any monthly `income_effect` path? (5.5)
- **Q4.** Do `welfare_cost`, `cpi_cost`, `edu_cost`, `health_cost`, `pub_cost` have writers in files not grepped (e.g. `national_focus/`, `decisions/`)? The grep covered `common/`, `events/`, `interface/` only for the `name =` pattern.
- **Q5.** Intent of `custom_expenses`: one-shot or standing? (5.4)
- **Q6.** Does the `military_total_exp` effect (`IC_Econ_2024.txt:2918`) always run before 1947? It runs inside `military_expenditure` (called at 326), but the enclosing effect boundary was not confirmed.
- **Q7.** Exporter-side income counterpart for the import costs (not in this slice).
