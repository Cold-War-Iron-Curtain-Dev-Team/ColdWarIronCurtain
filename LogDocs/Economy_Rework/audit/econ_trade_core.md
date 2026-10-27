# Trade core audit: IC_Trade_Scripted_Effects.txt (read-only)

Scope: `Cold War Iron Curtain/common/scripted_effects/IC_Trade_Scripted_Effects.txt` (12,667 lines), plus callers and the money-side consumers in `IncomeGenerator.txt`. Unverified items are marked `[INFERENCE]`.

## 1. Entry points

| Trigger | Site | Frequency | Actor |
|---|---|---|---|
| Monthly `export_script_for_pool` + `credit_calculation_work` | `common/on_actions/00_on_actions.txt:43-45` (inside `on_monthly`, `limit = { tag = UNS }`) | once/month | UNS only (global pool) |
| Monthly `trade.1` event → `trade_check` | `00_on_actions.txt:56` (`country_event = trade.1`), `IC_Influence_events.txt:3-11` (`trade.1` immediate calls `trade_check`) | per the on_monthly condition at 44-55 `[INFERENCE]` (condition not fully read) | AI and players with `trade_automation`, see §4 |
| Startup pool call | `on_startup_defines.txt:3537` | once | UNS |
| UNS-only credit check at startup | `on_startup_defines.txt` (credit_calculation_work per country, ~3691) `[INFERENCE]` | once | all listed countries |
| Backup credit check | `IC_Econ_2024.txt:1411` (`#Backup Check`) | unknown `[INFERENCE]` | — |
| Player buy/sort/reset buttons | `common/scripted_guis/Trade_Tab.txt` (buy 325–515; sort/clear/generate 1929–2250; reset 1164) | on click | players |
| CG monthly stock totals | `IC_Consumer_Goods.txt:2776` (`cwic_calculate_consumer_goods_export_stock_totals`) | monthly | all |
| CG AI flow | `consumer_goods_ai_automated_trade_effects.txt` (`clear_consumer_goods_sort_cache_arrays` :34; `generate_available_cg_*` 356–4118) | monthly `[INFERENCE]` | AI with `is_ai = yes` |
| Retired | `10_Yearly_On_Action.txt:15,18,30` (commented out); `decisions/_generic_decisions.txt:1503-1505` comment says export/credit/trade.1 moved to on_monthly | — | — |

Player vs AI: AI purchases go through `trade_check` (4656) → six `*_import_ai` effects. Players use Trade_Tab buttons. Both share `generate_available_*` / `buy_*` / `sort_*` helpers.

## 2. Map of effects (start line – purpose – callers)

| Effect | Lines | Purpose | Callers |
|---|---|---|---|
| `export_script_for_pool` | 3–214 | Per-country export pool: reads `resource@*` for each good, subtracts consumption, computes `currentAvailable*Export`, fires shortfall events | 00_on_actions:44, :3537; test_script (dead) |
| `startup_price_setting` | 215–251 | Sets `global.*BasePrice` | test_script only (dead chain) |
| `test_script` | 252–258 | Debug harness | none (dead) |
| `generate_available_chromium_import_array` | 259–447 | Chromium/nuclear exporter list + price | chromium_import_ai:808 |
| `buy_nuclear_material` | 449–564 | Chromium purchase for ROOT | Trade_Tab:325; test_script |
| `sort_price_number_aluminium` | 565–651 | UI sort | Trade_Tab:2235 |
| `sort_price_number_chromium` | 652–733 | UI sort | Trade_Tab:2174 |
| `sort_resource_number_chromium` | 734–793 | UI sort by qty | Trade_Tab:1930 |
| `chromium_import_ai` | 794–1047 | AI chromium purchase | trade_check:4663 chain |
| `generate_available_food_import_array` | 1048–1242 | Food exporters | food_import_ai:1521 |
| `buy_food` | 1243–1360 | Food purchase | Trade_Tab:331 |
| `sort_price_number_food` | 1361–1446 | UI sort | Trade_Tab:2221 |
| `sort_resource_number_food` | 1447–1506 | UI sort | Trade_Tab:1935 |
| `food_import_ai` | 1507–1760 | AI food purchase | trade_check:4657 |
| `generate_available_oil_import_array` | 1761–1949 | Oil exporters | oil_import_ai:2233 |
| `buy_oil` | 1950–2077 | Oil purchase | Trade_Tab:337 |
| `sort_resource_number_oil` | 2078–2135 | UI | Trade_Tab:1933 |
| `sort_price_number_oil` | 2136–2218 | UI | Trade_Tab:2249 |
| `oil_import_ai` | 2219–2469 | AI oil purchase | trade_check:4658 |
| `steel_import_ai` | 2470–2722 | AI steel purchase | trade_check:4659 |
| `generate_available_steel_import_array` | 2723–2920 | Steel exporters | steel_import_ai:2484 |
| `buy_steel` | 2921–3038 | Steel purchase | Trade_Tab:343 |
| `sort_price_number_steel` | 3039–3120 | UI | Trade_Tab:2189 |
| `sort_resource_number_steel` | 3121–3181 | UI | Trade_Tab:1931 |
| `generate_available_aluminium_import_array` | 3183–3370 | Aluminium exporters | aluminium_import_ai:4269 |
| `buy_aluminium` | 3371–3490 | Purchase | Trade_Tab:349 |
| `generate_available_rareEarth_import_array` | 3491–3678 | Rare earth exporters | rareEarth_import_ai:3955 |
| `buy_rareEarth` | 3679–3798 | Purchase | Trade_Tab:355 |
| `sort_price_number_rareEarth` | 3799–3880 | UI | Trade_Tab:2204 |
| `sort_resource_number_rareEarth` | 3881–3940 | UI | Trade_Tab:1932 |
| `rareEarth_import_ai` | 3941–4193 | AI rare-earth purchase | trade_check:4661 |
| `sort_resource_number_aluminium` | 4194–4254 | UI | Trade_Tab:1934 |
| `aluminium_import_ai` | 4255–4505 | AI aluminium purchase | trade_check:4660 |
| `sort_price_number_chromium_ai` | 4506–4530 | AI sort | chromium_import_ai:809 |
| `sort_price_number_food_ai` | 4531–4555 | AI sort | food_import_ai:1522 |
| `sort_price_number_oil_ai` | 4556–4580 | AI sort | oil_import_ai:2234 |
| `sort_price_number_steel_ai` | 4581–4605 | AI sort | steel_import_ai:2485 |
| `sort_price_number_rareEarth_ai` | 4606–4630 | AI sort | rareEarth_import_ai:3956 |
| `sort_price_number_aluminium_ai` | 4631–4655 | AI sort | aluminium_import_ai:4270 |
| `trade_check` | 4656–4666 | Calls all six `*_import_ai` | IC_Influence_events.txt:3-11 (trade.1); 10_Yearly:30 (commented) |
| `test_for_Trade_modifiers` | 4667–4673 | Test stub | none found `[INFERENCE]` dead |
| `reset_all_orders` | 4674–5193 | Clears all orders, returns infrastructure | Trade_Tab:1164; 10_Yearly:15 (commented) |
| `generate_available_cg_{basic,durable,vehicles}_t0..t5` and `cg_consumer_electronics_t1..t5` | 5194–7621 | Per-tier CG exporter lists | Trade_Tab:1958–2139; consumer_goods_ai_automated_trade_effects.txt 356–4118 |
| `buy_cg_{basic,durable,vehicles}_t0..t5`, `buy_cg_electronics_t1..t5` | 7622–10451 | CG purchase | Trade_Tab:365–515 |
| `clear_all_exporter_arrays` | 10452–10513 | Clears exporter arrays | Trade_Tab:1953, 2004 |
| `clear_consumer_goods_sort_cache_arrays` | 10514–10608 | Clears CG caches | consumer_goods_ai_automated_trade_effects.txt:34 |
| `set_all_import_list_variables_to_zero` | 10609–10623 | Zeroes import lists | Trade_Tab:1949, 2000, 2224 |
| `sort_price_number_cg_{...}` (basic/durable/vehicles t0–5, electronics t1–5) | 10624–12624 | CG price sort | Trade_Tab:1959–2140 |
| `cwic_calculate_consumer_goods_export_stock_totals` | 12625–12667 | Sums CG export stock | IC_Consumer_Goods.txt:2776 |

Dead or no-caller: `test_script`, `startup_price_setting` (only via test_script), `test_for_Trade_modifiers` `[INFERENCE]`.

## 3. Data model

- **Per-country resource stock/exports (on country scope):** `oilExport`, `foodExport`, `steelExport`, `chromiumExport`, `aluminiumExport`, `rareEarthExport`. Set by `export_script_for_pool` (`add_to_variable = { PREV.oilExport = resource@oil }` etc., lines ~33–50). Note the mapping: `foodExport = resource@rubber`, `rareEarthExport = resource@tungsten`, `chromiumExport = resource@chromium`.
- **Available export:** `currentAvailable<Good>Export` = `<good>Export` − `currentExported<Good>`; written at 150–211 and rounded. Negative values fire shortfall events.
- **Exported / imported totals (country):** `currentExported<good>`, `<good>Imports`, `<good>ExportTarget/Monthly`, `<good>ImportTarget/Monthly`, `<good>ExportTargetAmount`, `<good>ImportTargetAmount`. Written by `buy_*` (e.g., `currentExportedoil = ROOT.purchase_amount` at 1996, 2286, 2383; `ROOT.oilImports` +purchase_amount at 1999, 2289, 2386) and reset in `reset_all_orders` (4683–4687).
- **Indexed arrays / per-pair:** `<good>ExportTarget^THIS`, `<good>ExportTargetMonthly^THIS`, `chromiumExporterPrice^ROOT` (set at 442). Indexed by counterpart scope.
- **Exporter lists:** `ROOT.chromiumExporters`, `ROOT.chromiumExporterInfo`, and the equivalent lists for food, oil, steel, aluminium, rareEarth, CG tiers; filled by `generate_available_*`, cleared by `clear_all_exporter_arrays` / `clear_consumer_goods_sort_cache_arrays`.
- **Global base prices:** `global.<good>BasePrice`. Written by `on_startup_defines.txt:2634–2659`, and separately (conflicting) by dead `startup_price_setting:215–251`.
- **Infrastructure:** `trade_infrastructure_total` / `_available` / `_used`. Written at `IncomeGenerator.txt:289–292` (reset in income_effect), `:427–432` (available = total − used), IC_Trade_Scripted_Effects_Cuts.txt (many ±1 blocks), Trade_Tab.txt:221–1798, consumer_goods_ai_automated_trade_effects.txt:452–3704.
- **Trade-income accumulators (on UNS/ROOT scope):** `oil_exports`, `rubber_exports`, `steel_exports`, `chromium_exports`, `aluminium_exports`, `tungsten_exports` (zeroed `IncomeGenerator.txt:466–483`; summed 553–638 from `*ExportTargetMonthly^THIS` over `*_Export_List`).
- **Scratch:** `Export_List` (`IncomeGenerator.txt:553–615`, dedupe via add/clear). `purchase_amount`, `price_Adjuster`, `price_Adjuster_Special`, `shipping_cost`, `true_price`, `chromiumExportCash` (temps).

## 4. Formulas (file:line)

**Export pool** (per exporter, `export_script_for_pool`):
- `currentAvailableX = XExport − currentExportedX`, rounded (`round_variable`), e.g. steel 169–177, chromium 180–189.
- Pass structure: `every_other_country` (outer, ~N countries) → `every_controlled_state` (inner, sums `resource@<good>` per state, lines 33–50). Total visits ≈ N_countries + N_states per month `[INFERENCE]`.

**Chromium price** (`generate_available_chromium_import_array`, 259–447):
1. `chromiumExportCash = global.chromiumBasePrice`
2. If subject of ROOT: × `modifier@extra_trade_to_overlord_factor` (≈323–326)
3. × `price_adjust_generic^THIS` (with `price_Adjuster_Special`) (≈359–363)
4. × `price_adjustment_ideas` = 1 + `modifier@global_trade_penalty_adjustment` (+ Arab-League `modifier@arab_league_trade_penalty_adjustment`) (387–401)
5. × `price_adjustment_ideas2` = 1 − `modifier@global_trade_bonus_adjustment` (404–410)
6. Shipping: `shipping_cost = distance_to@ROOT.capital / global.base_shipping_cost_divisor`, rounded to 2dp, × `(1 + shipping_cost_effect)`, + 1 (411–435)
7. `true_price = chromiumExportCash × shipping_cost`; `chromiumExportCash += true_price` (≈437–440)
8. `chromiumExporterPrice^ROOT = chromiumExportCash` (442)

Same structure is assumed for other goods `[INFERENCE]`; only chromium was read in full.

**Money side:** `IncomeGenerator.txt:1171–1217` builds `resource_income` from `*_exports` accumulators, multiplied by `trade_credit_factor` (line 1215). `IC_Econ_2024.txt:2349–2357` uses `resource@X + X_exports − X_imports`, clamped to [0,1e6], times weights (oil 0.2, alu 0.1, tungsten 0.25, steel 0.1, chromium 0.5).

## 5. Money pulse interactions

- `ic_financial_monthly_pulse` is called from `00_on_actions.txt:37–40` (`is_ai = no`), not in the trade file.
- `income_effect` is defined at `IncomeGenerator.txt:287`. It begins `cwic_process_war_reparations`, then resets trade infrastructure (289–292). The accumulator reset is at 466–483, the summation at 553–638, and the `resource_income` use at 1171–1217.
- `income_effect = yes` is also called from `IC_scripted_effects.txt:57`, which adds `modifier@war_reperations` to `currentMoney`, and `_generic_decisions.txt:1534` (`every_country`).
- Trade purchases therefore do not touch treasury directly; they accumulate `*_exports` / `*Imports`, which `income_effect` consumes once per month `[INFERENCE]` (the pulse ordering was not verified).

## 6. Problems

Severity: H = high, M = medium, L = low.

1. **[L, corrected] Shortfall events carry two `immediate` blocks.** `trade.2`-`trade.7` (`IC_Influence_events.txt:12-66`) each have an empty `immediate = { }` followed by a live `immediate` that calls the matching `*DeliveryCuts` effect. They are not no-ops. `export_script_for_pool` fires them at 156, 166, 177, 188, 199, 210 and from the `buy_*` paths (e.g., 932, 1645, 2037, 2357, 2607, 4079, 4393).
2. **[H] Event labels and firing mismatch.** `trade.6` labelled "Nuclear Check" but fires chromium (188, 932); `trade.7` labelled "Nuclear Check" but fires food (166, 1645). Confusing, and any future event edits will go to the wrong good.
3. **[M] Mismatched resource mapping.** Food uses `resource@rubber` (`export_script_for_pool:33–50`, `food_import_ai:1509`); rare earth uses `resource@tungsten` (`rareEarth_import_ai:3943`). The naming is consistent but suspicious; `[INFERENCE]` whether intended (tungsten is a plausible rare-earth proxy, rubber for food is not obvious).
4. **[M] Variable name inconsistency.** `currentAvailableoilExport` (lines 154–155) uses lowercase `oil` while every other good uses `Oil`/capitalized. Works in Paradox unless there is a case-mismatched read elsewhere; `[INFERENCE]` potential silent mismatch with `currentAvailableOilExport` readers (none checked).
5. **[M] Dead code:** `test_script` (252), `startup_price_setting` (215–251), `test_for_Trade_modifiers` (4667) `[INFERENCE]`. Also `test_script` is the sole caller path for `startup_price_setting`.
6. **[M] Conflicting base prices.** `startup_price_setting` oil 0.2 / steel 0.1 / chromium 2 vs `on_startup_defines.txt:2634–2640` oil 0.0015 / steel 0.001 / chromium 0.025 and CG at 2643–2659. Only the on_startup values are live `[INFERENCE]`; dead code should be deleted.
7. **[M] Naming: "nuclear" = chromium.** `buy_nuclear_material` (449) and `nuclear_total = resource@chromium` (796) use nuclear for chromium. Confusing; the `Nuclear_Export_List` loop feeds `chromium_exports` (`IncomeGenerator.txt:553–572`).
8. **[M] Trade_Tab sort/clear ordering.** Every UI sort calls `set_all_import_list_variables_to_zero` and `clear_all_exporter_arrays` before regenerating. Any bug that leaves a list populated without a clear will double-count. `[INFERENCE]`, not tested.
9. **[L] Commented-out calls** `10_Yearly_On_Action.txt:15, 18, 30` (retired yearly pulse). Delete or keep consistent with the on_monthly cutover (per the retired comments in `_generic_decisions.txt:1503–1505`).
10. **[L] Typos/comments:** `IncomeGenerator.txt:618` "FIX 2026-07-05" comment is inside a loop; no action needed.
11. **[H, perf] O(E²) sort/selection.** Each `sort_price_number_*` and `sort_resource_number_*` uses nested `find_highest_in_array` loops over exporter lists, run from every UI sort click and from each `*_import_ai` monthly `[INFERENCE]` for count `E` exporters. Each AI import effect repeats `generate_available_*` (full scan of `every_other_country` + controlled states) once per good, so the monthly AI cost is roughly 6 × (N_countries + N_states) × per-exporter work `[INFERENCE]`.
12. **[M, perf] Per-month pool.** `export_script_for_pool` runs `every_other_country` → `every_controlled_state` once per month under the UNS tag, which is cheap, but `credit_calculation_work` (`IC_Loans_and_Interest_Rate_Effects.txt:272`) is also called inside an `every_country` block at `on_startup_defines.txt:~3691` (per-country), and from `IC_Econ_2024.txt:1411`. Full body not audited `[INFERENCE]`.
13. **[M] AI gaps.** AI purchases run only via `trade_check` from `trade.1`, and the on_monthly condition for `trade.1` (00_on_actions:44–56) was not fully read. CG AI is separate and uses `clear_consumer_goods_sort_cache_arrays` only. Player-only effects (`buy_*`, `sort_*`) are not reachable by AI.
14. **[L] Balance:** `trade_credit_factor` (IncomeGenerator:1215) and the IC_Econ_2024 weights (0.2/0.1/0.25/0.1/0.5) are hardcoded; not reviewed for balance.

## 7. Open questions

- Exact `trade.1` firing condition (00_on_actions:44–56) and whether AI always reaches `trade_check`.
- Whether `income_effect` runs before or after `export_script_for_pool` in the monthly order.
- Whether `price_adjust_generic`, `price_adjustment_ideas`, and `global_trade_*` modifiers apply identically to all six goods (only chromium was read end-to-end).
- Whether `credit_calculation_work` is per-country each month or only at startup (`on_startup_defines.txt:~3691`, `IC_Econ_2024.txt:1411`).
- Whether `test_for_Trade_modifiers` and `startup_price_setting` have callers outside the scanned tree.
- Whether `IC_Trade_Scripted_Effects_Cuts.txt` (not audited) still runs anywhere; it has live `trade.*` event calls at 156-equivalent lines and ±1 infrastructure edits.
- Whether `CWIC_trade_exporter_lists.txt` (rebuilt monthly via `cwic_rebuild_trade_exporter_lists`) supersedes the in-file list builders.
