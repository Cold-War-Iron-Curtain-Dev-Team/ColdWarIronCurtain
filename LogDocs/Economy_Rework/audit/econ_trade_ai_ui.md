# CWIC Trade Automation, AI, and UI Audit (read-only)

Mod root: `Cold War Iron Curtain/`. Paths below are relative to it. `[INFERENCE]` = not verified by reading the code.

## Summary
- The monthly trade automation chain is gated on the **UNS tag**. `trade.1` only fires from the `tag = UNS` block in `on_monthly` (`common/on_actions/00_on_actions.txt:42-56`). The per-country trade logic for both AI and automated players depends on that single block.
- Export-shortage cuts (`IC_Trade_Scripted_Effects_Cuts.txt`, 1,949 lines) are **live**. They run from `ic_financial_monthly_pulse` (player-only) and from `trade.2-7`, `trade.20-42` events.
- Likely bugs: (a) the export price `global_trade_bonus_adjustment` is **subtracted**, so a positive bonus lowers export revenue (sign inversion, HIGH); (b) the register code reads `currentAvailablefoodExport` while the rest of the code writes `currentAvailableFoodExport` (case mismatch, HIGH `[INFERENCE]` that variables are case-sensitive); (c) import-AI effects use the wrong resource keys (chromium→`nuclear_total`, food→`resource@rubber`, rare earth→`resource@tungsten`).
- `trade_automation` has one writer (the GUI toggle) and no default initialisation. AI bypasses it with `is_ai = yes`.

## 1. Entry points
| Entry | Caller | Frequency | Players vs AI |
|---|---|---|---|
| `on_monthly` → `tag = UNS` block (`00_on_actions.txt:42-56`): `export_script_for_pool`, `credit_calculation_work`, then `every_country` → `country_event = trade.1` for `trade_automation = 2 OR is_ai = yes` | on_monthly | Monthly, but only when root is UNS | Both |
| `trade.1` (`events/IC_Influence_events.txt:1-11`, hidden, triggered-only, `immediate = { trade_check = yes }`) | UNS block | Per country, monthly | Both |
| `trade_check` (`IC_Trade_Scripted_Effects.txt:4656-4663`): calls `food/oil/steel/aluminium/rareEarth/chromium_import_ai = yes` | trade.1 only (other callers: none found) | Monthly | Both |
| `ic_financial_monthly_pulse` (`IC_scripted_effects.txt:2-33`): cuts list (oil, steel, rare earth, aluminium, chromium, food, CG basic/durable/vehicles/electronics T0-5) | `on_monthly` in `is_ai = no` block (`00_on_actions.txt` ~56-60) | Monthly | **Players only** |
| `cwic_ai_consumer_goods_trade_master` (`consumer_goods_ai_automated_trade_effects.txt:3-38`) | `IC_Consumer_Goods.txt:2761-2762` (monthly CG step 6) | Monthly | AI or `trade_automation = 2`, gated on `trade_infrastructure_total_available > 0.99` |
| `cwic_rebuild_trade_exporter_lists` (`CWIC_trade_exporter_lists.txt:5-41`) | `on_monthly`, global flag `cwic_trade_exporter_lists_built` (25-day expiry, `00_on_actions.txt:29-33`) | ~ every 25 days, first country to hit it | Both (per `every_country`) |
| `trade_automation_button_click` (`scripted_guis/Trade_Tab.txt:1149-1165`) | GUI button `Trade_Tab.gui:538-553` | On click | Player only |
| `resource_concession_evaluation` (`scripted_effects/resource_concession_evaluation.txt:1-401`) | commented out at `IC_scripted_effects.txt:93`; live at `events/tutorial.txt:129` | Tutorial only `[INFERENCE]` | — |
| `income_effect` (`scripted_effects/IncomeGenerator.txt:287-343`) | caller not verified `[INFERENCE]` | Per income tick `[INFERENCE]` | Both `[INFERENCE]` |

Trade.N events (`trade.2`-`trade.7`, `trade.20`-`trade.42`) are fired from the export-setting effects in `IC_Trade_Scripted_Effects.txt` (lines 156-210, 932-2037, 2357-4493) and `consumer_goods_ai_automated_trade_effects.txt` (lines 494-3746, one per tier). Each is an `immediate` call into the cuts. `national_focus/COG_60s.txt:2851` calls `cabinda_trade.1`, which is a separate event and not related.

## 2. Data model
| Name | Meaning | Writers | Readers |
|---|---|---|---|
| `trade_automation` (country var) | 2 = automated, 1 = manual (default unset = 0) | `Trade_Tab.txt:1149-1165` (button) | `00_on_actions.txt:51`; `consumer_goods_ai_automated_trade_effects.txt:18`; ~40 checks in `Trade_Tab.txt` (140-212, 748-844, 905-932); `Trade_Tab.gui:538+` |
| `trade_infrastructure_total_available` / `_used` / `_total` | Shared pool of trade capacity | `reset_all_orders` (`IC_Trade_Scripted_Effects.txt:4674`), cuts, `income_effect` (resets `trade_infrastructure_total` at `IncomeGenerator.txt:289-290`) | CG AI gating; cuts |
| `currentAvailable<X>Export`, `currentExported<X>` | Exportable stock per resource | `IC_Trade_Scripted_Effects.txt:155-210` (`currentAvailableFoodExport`, `currentAvailableSteelExport`, `currentAvailableChromiumExport`, `currentAvailableAluminiumExport`, `currentAvailableRareEarthExport`, `currentAvailableoilExport`); cuts | `CWIC_trade_exporter_lists.txt` register block (43+); cuts |
| `<X>ExportTargetAmount^<scope>`, `<X>ExportTargetMonthly^<scope>`, `<X>ImportTargetMonthly^<scope>` | Per-pair export/import targets | Cuts, AI import effects | Cuts |
| `global.cwic_ex_*` (30 arrays) | Exporter lists by resource and CG tier | `cwic_rebuild_trade_exporter_lists` (clears at `CWIC_trade_exporter_lists.txt:5-41`) and register | Cuts (`Oil_Export_List` etc.), AI effects |
| `price_adjustment_ideas`, `price_adjustment_ideas2` | Export price multipliers | `IC_Trade_Scripted_Effects.txt:391-411` and repeats (1193, 1907, 2878, 3328, 3636, 5266 ... 6639) | export cash computations |
| `purchase_amount`, `purchase_amount_prior` | AI purchase size | AI effects (set to 0 at `consumer_goods_ai_automated_trade_effects.txt:~20`) | AI effects |
| `cg_*_demand`, `cg_*_stock_t0..t5` | CG demand/stock | `IC_Consumer_Goods.txt` | AI effects, `cwic_calculate_consumer_goods_*` |
| `CG_Quality_Cat` | Selected CG quality | `Trade_Tab.txt:31+` | GUI |
| `chromium_prompt` | Chromium purchase prompt | `Trade_Tab.txt:317` | GUI |
| `global_trade_bonus_adjustment` (dynamic modifier) | Export bonus | Ideas (e.g., `INS.txt:14`, `Indonesia.txt:188-267`, `JAP_Ideas.txt:511-559` negative, `New_Ideologies_Ideas.txt:1701/1920`, `brazil.txt:216-372`) | `IC_Trade_Scripted_Effects.txt` 406-407 and 19 repeats |
| `global_trade_penalty_adjustment` | Export penalty | Not traced | `IC_Trade_Scripted_Effects.txt:~398` |
| `Revamped_Trade_Policy` (idea) | Trade opinion +10%, CG factor -2% | `common/ideas/usa.txt:1012-1019`, added by `national_focus/USA_Wallace_1980_Second_Term.txt:298-303` (1825 days) | Modifiers only |

## 3. Formulas (file:line)
**Export price pipeline** (`IC_Trade_Scripted_Effects.txt` ~379-411, chromium block):
1. `price_adjustment_ideas = modifier@global_trade_penalty_adjustment` (+ `ROOT.modifier@arab_league_trade_penalty_adjustment` if `arab_league_member`), then `+= 1` → multiplier `P = 1 + penalty`.
2. `chromiumExportCash *= P`.
3. `price_adjustment_ideas2 = 1`; `price_adjustment_ideas2 -= modifier@global_trade_bonus_adjustment` (`:406-407`); `chromiumExportCash *= price_adjustment_ideas2`.
   - `[INFERENCE]` With percentage modifiers (`lar_operation_modifiers_pre_definition.txt:95-98`), a bonus of +0.10 gives `B = 0.90`, so **the bonus reduces revenue**. The penalty is added and the bonus is subtracted, so the bonus has the inverted sign. Verify against the engine's modifier semantics before editing.

**Shipping** (`IC_Trade_Scripted_Effects.txt:~420`): `shipping_cost = distance_to@capital / global.base_shipping_cost_divisor * 100`, then `round_variable`.

**Cuts** (`IC_Trade_Scripted_Effects_Cuts.txt:1-60` for oil): while `currentAvailableoilExport < 0` and a `Oil_Export_List` member has `ExportTargetAmount > 0`, each pass: `currentExportedoil -= 1`, `currentAvailableoilExport += 1`, `trade_infrastructure_total_available += 1`, `trade_infrastructure_total_used -= 1`, `oilImports -= 1`, `ExportTargetAmount^THIS -= 1`, `oilImportTargetAmount^ROOT -= 1`, and the monthly targets are reduced by `priorExportTotal` (`priorExportTotal = ExportTargetMonthly / ExportTargetAmount`, `:31-35`). The `### NEED CALCS` comment (~line 47) marks this as unfinished `[INFERENCE]`.

**CG AI need** (`consumer_goods_ai_automated_trade_effects.txt:36+`): need = `cg_basic_demand − Σ cg_basic_stock_t0..t5`, clamped at 0, gated by `> 0.99` and `trade_infrastructure_total_available > 0.99`.

## 4. Interaction with the money pulse
- `ic_financial_monthly_pulse` (`IC_scripted_effects.txt:2-33`) runs the cuts when there is no active insurgency (`else` branch). It is called from the `is_ai = no` block of `on_monthly` (`00_on_actions.txt` ~56-60). AI countries therefore never see cuts, but they do see the AI import effects.
- `income_effect` (`IncomeGenerator.txt:287-343`): resets `trade_infrastructure_total = 0` (`:289-290`), then calls `gdp_calculation_effect`, `cwic_cg_monthly_master_tick`, `interest_rate_calc`, `domestic_bond_calc`, and others. Income and trade therefore share a monthly tick, but the order between `income_effect`, `trade.1`, and `ic_financial_monthly_pulse` is not verified `[INFERENCE]`. Resetting `trade_infrastructure_total` while the pool is `…_available` / `…_used` may be a different variable, so the reset may be a no-op `[INFERENCE]`.
- `ic_pulse_monthly` (`IC_scripted_effects.txt:76-79`): `federation_calculator`, `monthly_power_projection_gain`, `monthly_set_fpp`. Called from `on_monthly_VTC` `every_country` (`00_on_actions.txt` 3-20). Not trade-related.

## 5. Problems
| # | Severity | Location | Issue |
|---|---|---|---|
| 1 | HIGH (balance) | `IC_Trade_Scripted_Effects.txt:406-407` and 19 repeats | `subtract_from_variable = { price_adjustment_ideas2 = modifier@global_trade_bonus_adjustment }` applies the bonus with the wrong sign `[INFERENCE]`. Positive bonuses in ideas (`INS.txt:14`, `brazil.txt:216-372`) reduce export revenue. |
| 2 | HIGH (bug) | `CWIC_trade_exporter_lists.txt` register block (43+) | Key `currentAvailablefoodExport` (lowercase `f`) vs writer `currentAvailableFoodExport` (`IC_Trade_Scripted_Effects.txt:158`). If keys are case-sensitive `[INFERENCE]`, food is never registered as exportable. |
| 3 | MEDIUM (bug) | `IC_Trade_Scripted_Effects.txt:794-796` | `chromium_import_ai` writes `nuclear_total = resource@chromium`. Label/variable mismatch (nuclear = chromium). |
| 4 | MEDIUM (bug) | `IC_Trade_Scripted_Effects.txt:1509` | `food_import_ai` uses `resource@rubber` for `food_total`. |
| 5 | MEDIUM (bug) | `IC_Trade_Scripted_Effects.txt:3943` | `rareEarth_import_ai` uses `resource@tungsten`. Confirm that is intended. |
| 6 | MEDIUM | `Trade_Tab.txt:1338-1361` | Nuclear block resets `nuclearImports` and chromium targets. Likely mislabelled. |
| 7 | MEDIUM (AI gap) | `00_on_actions.txt:42-56` | Entire automated trade chain runs only inside `tag = UNS`. If UNS is not always present, AI and automated players get no monthly trade `[INFERENCE]`. |
| 8 | MEDIUM (perf) | `IC_scripted_effects.txt:8-33` plus 30+ cuts | Each cut is a `while_loop_effect` over `for_each_scope_loop` on the export lists, run once per month per player. Cost scales with list size `[INFERENCE]`. |
| 9 | LOW (dead code) | `resource_concession_evaluation.txt` (401 lines) | Commented call at `IC_scripted_effects.txt:93`; only live caller is `events/tutorial.txt:129`. |
| 10 | LOW | `IC_Trade_Scripted_Effects_Cuts.txt:~47` | `### NEED CALCS` placeholder in oil cuts; monthly target recalcs unfinished. |
| 11 | LOW (dead/unused) | `IC_Trade_Scripted_Effects.txt` (trade_check) | `trade_check` now calls all six import effects; earlier-noted "unreachable" concern is resolved. |
| 12 | LOW (naming) | `Trade_Tab.txt`, `IC_Comecon` | Comecon modifiers in `IC_Comecon_Modifiers.txt` are a template with `COMECON_*` tokens. Values not verified `[INFERENCE]`. |

## 6. Vanilla coexistence
- The mod ships its own `interface/Trade_Tab.gui`, `interface/countrytradeview.gui`, and `common/scripted_guis/Trade_Tab.txt`. These replace vanilla files of the same name (no merge), so any vanilla trade GUI content is lost.
- `resources/00_resources.txt` and vanilla trade law / market files are **not** in the mod's `common/` listing (glob of `common/`, 40 results shown, not exhaustive) `[INFERENCE]`. Vanilla resource trade therefore likely coexists with the scripted trade via the `resource@<name>` reads (`IC_Trade_Scripted_Effects.txt:796, 1509, 2221, 2472, 3943, 4257`).
- `Revamped_Trade_Policy` changes trade opinion only; it does not touch the export pipeline.

## 7. Open questions
1. Is `tag = UNS` always an active tag? If not, the monthly trade chain is dead.
2. Does `multiply_variable` with a positive percentage modifier multiply by `(1 + x)` or `x`? That determines problem 1.
3. Are variable names case-sensitive in this engine? Determines problem 2.
4. Which file calls `income_effect` and in what order relative to `trade.1`?
5. Do the `*_import_ai` resource keys (`nuclear_total`, `food_total`, `rareEarth_total`) feed any reader? Grep showed the totals only `[INFERENCE]`.
6. Does the `chromium_exporter_list` window tail (`Trade_Tab.txt` ~2800-2967) contain any AI-facing logic? Not read.
7. Are the `COMECON_*` tokens defined in `synchronized_dynamic_tokens/tokens.txt`? Not verified.

## Files
- `common/on_actions/00_on_actions.txt:1-78` (on_monthly, trade gate)
- `events/IC_Influence_events.txt:1-66` (trade.1 and per-resource checks)
- `common/scripted_effects/IC_Trade_Scripted_Effects.txt:155-212, 379-423, 794, 1507, 2219, 2470, 3941, 4255, 4656-4663, 4674` (export pipeline, import AI, trade_check, reset)
- `common/scripted_effects/IC_Trade_Scripted_Effects_Cuts.txt:1-1949` (cuts)
- `common/scripted_effects/IC_scripted_effects.txt:2-33, 76-79, 93` (pulse, ic_pulse_monthly, commented resource call)
- `common/scripted_effects/IncomeGenerator.txt:287-343` (income_effect)
- `common/scripted_effects/CWIC_trade_exporter_lists.txt:5-41` (rebuild; register block 43+ not fully read)
- `common/scripted_effects/consumer_goods_ai_automated_trade_effects.txt:3-38, 36+` (AI CG master)
- `common/scripted_effects/IC_Consumer_Goods.txt:2760-2777` (monthly CG hook)
- `common/scripted_effects/resource_concession_evaluation.txt:1-401` (dead except tutorial)
- `common/scripted_guis/Trade_Tab.txt:31, 317, 1149-1165, 1338-1361` (GUI effects)
- `interface/Trade_Tab.gui:538-553` (automation toggle)
- `common/modifier_definitions/lar_operation_modifiers_pre_definition.txt:95-98` (global_trade_bonus_adjustment definition)
- `common/ideas/usa.txt:1012-1019` (Revamped_Trade_Policy)
- `common/dynamic_modifiers/IC_Comecon_Modifiers.txt:1-60` (Comecon template)
- `scratch/check_trade_tab_gui.py`, `check_trade_tab_sguis.py`, `compare_trade_gui.py` are scratch (not shipped).

## Not verified
- `CWIC_trade_exporter_lists.txt:43-442` (register block, consumer electronics lists).
- `IC_Comecon.txt` (scripted_localisation) body.
- `Trade_Tab.txt` 2800-2967.
- `IncomeGenerator.txt` beyond line 343.
- Vanilla resource and trade law files.
