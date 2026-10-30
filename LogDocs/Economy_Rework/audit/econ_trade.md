# CWIC Economy: Trade Slice

Repo: `/home/zom/Projects/ColdWarIronCurtain`, mod root `Cold War Iron Curtain/`. Branch `Econ-fix`. Read-only analysis. Unverified items are marked `[INFERENCE]`.

## 1. Purpose and entry points

Trade is a fully scripted market. Vanilla resource trade is not used; `common/resources/00_resources.txt` only supplies `cic`/`convoys` values. Scripts read `resource@<x>` stockpile/state yields and run their own export pool, exporter registry, price formula, buy/sort pipeline, and monthly money flow.

### Monthly pipeline (on_monthly)
- `common/on_actions/00_on_actions.txt:30–32`: `cwic_rebuild_trade_exporter_lists`, gated by `global flag cwic_trade_exporter_lists_built days=25`. Rebuild is every 25 days, not monthly.
- `00_on_actions.txt:43–45`: UNS scope runs `export_script_for_pool` and `credit_calculation_work`.
- `00_on_actions.txt:46–59`: `every_country` fires `country_event = trade.1` when `trade_automation = 2` (L51) OR `is_ai = yes` (L53). Every AI and every automated player runs the full trade tick each month.
- `trade.1` (`events/IC_Influence_events.txt`, hidden, triggered-only) runs `trade_check = yes`.
- `trade_check` (`common/scripted_effects/IC_Trade_Scripted_Effects.txt:4656`) calls the six `*_import_ai` effects: chromium L794, food L1507, oil L2219, steel L2470, rareEarth L3941, aluminium L4255.
- Consumer goods chain: `common/scripted_effects/IC_Consumer_Goods.txt:2762` calls `cwic_ai_consumer_goods_trade_master`; L2775–2776 call the CG totals effects. `IC_Industrial_Pulse.txt:617` and `IC_Consumer_Goods.txt:3764` call `cwic_register_own_trade_offers`.
- `common/on_actions/10_Yearly_On_Action.txt:14–33`: `trade_check` is commented out (no yearly trade tick).
- `common/scripted_effects/_generic_decisions.txt:1503–1505`: retired calls (now monthly).
- `IC_Econ_2024.txt:1411`: backup `credit_calculation_work` call.
- `common/on_actions/on_startup_defines.txt:3537` (UNS `export_script_for_pool`), `:3691` (`credit_calculation_work` every_country).

### Player entry points (GUI)
- `interface/Trade_Tab.gui:549–552`: `trade_automation_button` (frame = 2, label L539 "Automate Trade:"). Scripted gui entry at `common/scripted_guis/Trade_Tab.txt:994` (`frame = trade_automation`).
- `Trade_Tab.txt:1149–1165` `trade_automation_button_click`: if `trade_automation = 2` set 1; else set 2 and call `reset_all_orders = yes`.
- Manual buy/sell buttons are gated by `ROOT.trade_automation = 2` NOT-gates: chromium L140–212 (incl. `increase_chromium_shift_click_enabled` ~L190, `decrease_chromium_click_enabled` ~L178), per-resource and CG totals L748–932.
- `cancel_oil_imports_click` (`Trade_Tab.txt:1169–1173`) returns oil imports to available.
- Per-resource return handlers L1168–1340 (oil, aluminium, food, rareEarth, steel, nuclear); CG totals L1366+, durable L1510+.
- `purchase_amount_prior = *ExportTargetAmount` at L2273+.
- List grids `oil_trade_listing_grid` (`oilExporters`) and `chromium_trade_listing_grid` (`chromiumExporters`).
- Default value of `trade_automation` is unset → manual by default `[INFERENCE]`.

### Events
- `events/IC_Influence_events.txt` namespace `trade`: `trade.1` (trade_check); `trade.2`–`trade.7` run the `*DeliveryCuts` effects (oil, steel, rareEarth, aluminium, chromium, food); `trade.20`+ CG basic tier cuts; `trade.40/41/42` cgBasicT0 / cgDurableT0 / cgVehiclesT0 cuts.

## 2. Data model

### Country variables (per exporter/importer)
| Variable | Meaning | Writers | Readers |
|---|---|---|---|
| `<res>ExportRate` (chromium, oil, food, steel, aluminium, rareEarth, consumerGoods) | Fraction of available surplus that may be exported | `export_script_for_pool` L7–13 from `modifier@<res>_export_rate` | export_script_for_pool, cuts |
| `<res>Export` | Export capacity for the month | `export_script_for_pool` L26–34, after multiplication L140–210 | `currentAvailable<res>Export`, IncomeGenerator |
| `currentAvailable<res>Export` | Remaining exportable amount | `export_script_for_pool` (`= Export − currentExported`), `buy_*` decrements, cuts reset | `generate_available_*_import_array`, registry |
| `currentExported<res>` | Amount already sold this month | `export_script_for_pool` (`*_produced_prior`/`*_export_prior` clears L4–15), `buy_*` increments | registry, `export_script_for_pool` |
| `<res>Imports` | Monthly import quantity | `buy_*`, cuts zero it | IncomeGenerator cost side |
| `<res>ImportTargetMonthly^THIS` | Import cost booked this month | `buy_*`, cuts (`= priorExportTotal`) | IncomeGenerator (chromium_imports includes nuclear, L1381) |
| `<res>ExportTargetMonthly^THIS` | Export income booked this month | `buy_*` (seller side, `^ROOT`) | IncomeGenerator L559–703+ |
| `<res>ExporterPrice^ROOT` (`oilExporterPrice` etc.) | Quoted price per exporter per buyer | `generate_*` | `sort_price_*`, `buy_*` |
| `trade_infrastructure_total`, `_used`, `_available` | Trade-capacity budget | IncomeGenerator L162–171 (+), L289–290 (reset), L424–428 (×8), L431 (available = total − used); `buy_*` (`used +=`, `available −=`); cuts/reset_all_orders return it | all buy/import paths, CG AI gate |
| `purchase_amount`, `purchase_amount_prior` | Scratch purchase quantities | CG AI L30–31, Trade_Tab | Trade_Tab, CG AI |
| `trade_embargo_check^<TAG>` | Embargo flag (1 = blocked) | diplomacy actions (`scripted_diplomatic_actions.txt:61,100`), history files (SOV_Ustinov L523–539, USA_FP_50s L6991, JAP_scripted_effects, YUG_50sR, on_startup L572–595) | all generate/buy paths (`ROOT.trade_embargo_check^THIS = 0`, e.g. IC_Trade L279, 540, 1067, 1335, 1781, 2049, 2742) |
| `price_adjust_generic^<TAG>` | Per-pair price adder | ECSC.txt L698–778 (+0.25), New_Ideologies_Ideas.txt L7090–7107 (−0.25 removal), 50s_NIC L1873, DOM_49 L1484, DOM_60s L1874, LIB_50s L149/154/1831/1836 | IC_Trade L352, 1140, 1854 |
| `price_adjust_food^<TAG>` | Food price adder | INDIA_60s.txt:1207 (`price_adjust_food^USA = 0.15`) | IC_Trade L1107 |
| `price_adjust_chromium/oil/steel^<TAG>` | Per-pair price adders | **none found** | IC_Trade L319, 1821, 2782 |
| `price_Adjuster`, `price_Adjuster_Special`, `price_Adj` | Temp scratch sums in formula | buy/generate paths | same |
| `price_Adj2` | Set/subtracted at IC_Trade L329–369, 1116–1160, 1830–1870 but never applied to final price | — | — (dead) |
| `shipping_cost` | Distance cost factor | `distance_to@ROOT.capital / global.base_shipping_cost_divisor` | exporter price |
| `shipping_cost_effect` | Multiplier on shipping | **no writer found** (reader IC_Trade L427, 1222, 1928) | same |
| `oilExporterPrice^ROOT` | Final price stored per buyer | oil generate path | sort/buy |
| `<res>Concession` | Concession output | `resource_concession_evaluation.txt` | Concession modifiers |
| `ic_pulse_check`, `Credit_Progress`, `Credit_Rating` | credit system (not trade) | IC_Loans_and_Interest_Rate_Effects.txt | — |

### Modifiers that feed trade
- Export rate modifiers `<res>_export_rate` (`common/ideas/_economic.txt`): tier 1 L312–319 (chromium 0.25, food 0.45, oil 0.7, steel 0.7, rare_earth 0.7, aluminum 0.7, consumer_goods 0.5); tier 2 L338–345 (0.2, 0.3, 0.6, 0.6, 0.6, 0.6, 0.4); tier 3 L365–372 (0.1, 0.15, 0.4, 0.4, 0.4, 0.8, 0.25); tier 4 L388–393 (food 0.05, oil 0.2, steel 0.2, rare 0.2, aluminum 0.2, cg 0.05). Country-specific: Tibet.txt:97–137 (food negatives), brazil.txt:50–51 (food +0.10), liberia_ideas.txt:325–327 (steel −0.1). Dynamic modifier `economic_modifier_market_resources` set in `common/dynamic_modifiers/0_dynamic_modifiers.txt:410–414`.
- `global_trade_bonus_adjustment` (reduces price by `(1 − x)`): INS.txt:14 (+0.05), Indonesia.txt:188/201/214/227/267 (+0.05…+0.25), JAP_Ideas.txt:511/523/535/547/559 (−0.07…−0.5), brazil.txt:216/253/292/372 (+0.05…+0.10), New_Ideologies_Ideas.txt:1701/1920.
- `global_trade_penalty_adjustment` (adds to price by `+1`): New_Ideologies_Ideas.txt:675, 1368 (+0.15), 1566 (+0.25), 2187, 3043 (+0.2), 3053, 3487, 3494, 3503, 3512, 3609, 3617, 3950, 3958, 6647 (+0.5 UN_Weapon_Trade_Ban).
- `extra_trade_to_overlord_factor` in `common/autonomous_states/`: integrated_puppet 1.0 (L17), lar_collaboration_government 1.0 (L24), nsb_personal_union 0.5 (L27), puppet 1.0 (L18), supervised_state 0.25 (L17), usa_major_non_nato_ally 0.1 (L13); plus China/Crown_Domain/etc. per summary. `overlord_trade_cost_factor` puppet −0.9, integrated/LAR −0.9, nsb −0.5, supervised −0.25, usa_major −0.1.
- `Revamped_Trade_Policy` (`common/ideas/usa.txt:1012–1030`): `allowed = always`, `modifier = { trade_opinion_factor = 0.10; consumer_goods_factor = -0.02 }`. No export or price effect. Added via timed idea in `common/national_focus/USA_Wallace_1980_Second_Term.txt:298–303`. Token at `common/synchronized_dynamic_tokens/tokens.txt:1299`.
- Dynamic modifier `resource_trade` (`0_dynamic_modifiers.txt:247–256`): country_resource_cost_oil = oilExport, rubber = foodExport, steel = steelExport, … (income-side display/cost link).
- `resource_consumption` (L217–224) and concession modifier block (L268–271: steelConcession, oilConcession…) — concession modifier is applied only via commented call (see §5).

### Global values
- `common/scripted_effects/IC_Trade_Scripted_Effects.txt:215–251` `startup_price_setting`: oil 0.2, steel 0.1, food 0.15, chromium 2, rareEarth 0.3, aluminium 0.1; CG basic T0 0.03…T5 0.25; durable T0 0.08…T5 0.80; vehicles T0 0.35…T5 2.50; electronics T1 0.20…T5 1.40.
- `on_startup_defines.txt:2629–2631`: `global.base_transport_cost_divisor = 200`, `global.base_shipping_cost_divisor = 1000`, `global.base_shipping_cost_divisor_cg = 10000`. Oil `oilBasePrice`, steel etc. via `global.<res>BasePrice`.
- `on_startup_defines.txt:2682–2685`: `GlobalCredit 0.45`, `GlobalTaxCredit 1.00`, `GlobalDebit 0.28`, `GlobalEdictDebit 0.44`.
- `common/resources/00_resources.txt`: oil cic 0.200 / convoys 0.05; aluminium 0.1 / 0.1; rubber 0.150 / 0.1; tungsten 0.250 / 0.05; steel 0.100 / 0.1; chromium 0.5 / 0.05; coal 0.125 / 0.1 (coal untraded).

### Exporter registry
- `CWIC_trade_exporter_lists.txt:5–38` `cwic_rebuild_trade_exporter_lists`: clears `global.cwic_ex_chromium/food/oil/steel/aluminium/rareEarth`, `cwic_ex_cg_basic_t0..t5`, `cg_durable_t0..t5`, `cg_vehicles_t0..t5`, `cg_consumer_electronics_t1..t5`; then `every_country = { cwic_register_own_trade_offers = yes }` (L36–37).
- `cwic_register_own_trade_offers` (L40+): removes THIS from each array; re-adds if `currentAvailable<Res>Export > 0.99` OR `currentExported<Res> > 0.99` (chromium L44–52, food L54–62, oil ~L64–75; L84–442 CG registration not re-read).

## 3. Formulas (step by step)

### 3a. Export capacity (`export_script_for_pool`, IC_Trade_Scripted_Effects.txt:3–213, UNS scope)
1. Clear prior-month arrays/vars (L4–15).
2. For each other country: `<res>ExportRate = modifier@<res>_export_rate` for chromium, oil, food, steel, aluminium, rareEarth, consumerGoods (L7–13). Note: `aluminum_export_rate` spelling matches `_economic.txt`, so consistent.
3. Zero current exports (L15–20).
4. For each controlled state: add `resource@oil` → oilExport; `resource@rubber` → foodExport; `resource@steel`, `resource@chromium`, `resource@aluminium`, `resource@tungsten` → respective exports (L26–34).
5. Subtract domestic consumption; clamp <2 to 0 (`[INFERENCE]` from summary); multiply by ExportRate; round.
6. `currentAvailable<Res>Export = <Res>Export − currentExported<Res>`; if negative fire `trade.2`–`trade.7` (cuts) (~L140–210).
7. Debug residue: `aluminium_test` (~L103).

Cost: `every_other_country × every_controlled_state` nested per owner per month (see §5 perf).

### 3b. Price (`generate_available_oil_import_array` L1761–1948; identical pattern for chromium L259, food L1048, steel L2723, aluminium L3183, rareEarth L3491, CG tiers L5194–7621)
Exporter eligible if (`currentAvailable<res>Export > 0.99` OR `currentExported<res> > 0.99`), not ROOT, `ROOT.trade_embargo_check^THIS = 0`, not at war (`has_war_with`).
1. `oilExportCash = global.oilBasePrice`.
2. `price_Adjuster = ROOT.price_adjust_oil^THIS` (L1821) — **no writer**, always 0 `[INFERENCE: effectively dead]`.
3. If ROOT is subject of THIS: multiply by `modifier@extra_trade_to_overlord_factor` (`[INFERENCE]` from branch structure).
4. `ROOT.price_adjust_generic^THIS` added (L1854); `price_Adjuster_Special` path (L1861–1865).
5. Multiply by `(modifier@global_trade_penalty_adjustment + 1)`; plus `ROOT.modifier@arab_league_trade_penalty_adjustment` if flag `arab_league_member`.
6. Multiply by `(1 − modifier@global_trade_bonus_adjustment)`.
7. `shipping_cost = distance_to@ROOT.capital / global.base_shipping_cost_divisor`, rounded 2dp; `× (1 + shipping_cost_effect)` (L1928–1931; `shipping_cost_effect` has no writer → factor 1); then `+ 1`.
8. `oilExportCash = cash × (1 + shipping_cost)`; stored `oilExporterPrice^ROOT`.

`price_Adj2` is set and subtracted (L1830–1870) but not applied to step 8 → dead.

### 3c. Sort and select (`sort_price_*`, `sort_price_number_*_ai`)
- Manual sort: aluminium L565/L4194, chromium L652/L734, food L1361/L1447, oil L2078/L2136, steel L3039/L3121, rareEarth L3799/L3881; CG tiers L10624–12537.
- AI sort: `sort_price_number_chromium_ai` L4506, food L4531, oil L4556, steel L4581, rareEarth L4606, aluminium L4631. Each truncates the exporter array to **one** cheapest entry (`break = cheapest_brk`).

### 3d. Import (`*_import_ai`, AI path) — e.g. oil L2219
- Need = monthly demand − current stock; ordered from the cheapest exporter in the truncated array; capped by `trade_infrastructure_total_available` and `currentAvailableoilExport`.
- `trade_check` (L4656) calls all six per AI per month.

### 3e. Purchase (`buy_*`; buy_oil L1950–2076; identical pattern for chromium L488–495, food L1253–1260, steel L2921, aluminium L3371, rareEarth L3679, nuclear L449, CG L7622–10328)
1. Reduce `currentAvailable<res>Export −= purchase_amount`.
2. Infra: `trade_infrastructure_total_used += amount`, `trade_infrastructure_total_available −= amount` (IC_Trade L1990–1993 pattern).
3. `currentExported<res> += amount`.
4. Buyer: `<res>Imports += amount`; `<res>ImportTargetMonthly^THIS += price × amount`.
5. Seller: `<res>ExportTargetMonthly^ROOT += price × amount` (`oilExportTargetMonthly^ROOT`, L~2070).
6. Update `Oil_Import_List` / `Oil_Export_List` arrays.

### 3f. Money flow (IncomeGenerator.txt)
- Infrastructure capacity: L162–171 adds `building_level@air_base`, `office_park_total`, `building_level@state_infrastructure` to `ROOT.trade_infrastructure_total`; L289–290 zero it monthly; L293 calls `cwic_cg_monthly_master_tick`; L424–428 `trade_infrastructure_total *= 8`; L431 `_available = total − used`.
- Export income: L559–703+ builds `chromium_exports`, `rubber_exports` (food), `oil_exports`, `steel_exports`, `aluminium_exports`, `tungsten_exports` (rareEarth), CG exports from `*ExportTargetMonthly^THIS`, deduplicated with `for_each_scope_loop` over `*_Export_List` and `add_to_array ROOT.Export_List` (cleared between). Steel loop fixed 2026-07-05 (comment ~L673).
- Import cost: ~L1262–1410: `chromium_imports` (includes nuclear, L1381), `oil_imports` (L1399), `rubber_imports`, steel/aluminium/tungsten imports; `consumer_goods_import_cost` = sum of CG `*_imports` (~L1879–1905); `resource_cost` (L1906–1911) = CG + aluminium + rubber + tungsten + steel + chromium + oil imports; `totalexp += resource_cost`; `IncomeTotal −= resource_cost` (~L1911–1913).
- `[INFERENCE]` The export side must be added into IncomeTotal in the same block (L559–703 region); not fully traced.

### 3g. Valuation (`IC_Econ_2024.txt:2349–2357`)
`oil_val/alu_val/tng_val/stl_val/chr_val` = resource@X + exports − imports, clamped ≥0, multiplied by 0.200/0.100/0.250/0.100/0.500 → `metal_val`/`total_val`. Purpose (indicator/score) not confirmed.

### 3h. Delivery cuts (`IC_Trade_Scripted_Effects_Cuts.txt`)
- Each cut resets `trade_infrastructure_total_available = 1` and `*_used = 1` (oil L36–42, steel L96–102, rareEarth L156–162, aluminium L216–222, nuclear L276–282, food L336–342, cgBasicT0 L405–412, cgBasicT1 L474–481, cgBasicT2 L543–550, cgBasicT3 L612–619).
- Subtract `oilImportTargetMonthly^ROOT = priorExportTotal` (L54–55), chromium at L294–295.
- `[INFERENCE]` Reclaim sets capacity to 1 regardless of purchase size; a fixed reset rather than a refund of the actual amount.

### 3i. Concession (`resource_concession_evaluation.txt`, 401 lines)
Per owned state: concession amount = `resource@X + XBonus` × 0.25/0.5/0.75/1 depending on `has_state_flag <res>_resource_concession_25/50/75/100` (tungsten ~L3–60, aluminium L94–164, chromium L171–241, oil L253–314, steel ~L320–400). Moves amounts from `var:<res>_concession_target.<res>ConcessionsGains` and adds to `concession_owner` (= THIS.owner) variable `<res>Concession`.

### 3j. Comecon
- `common/scripted_guis/COMECON.txt` L631–660, L742–753: `COMECON_TARGET.TRADE_COMECON_RATE` 0–6 gate rows; click handlers L1091–1092 (`SOV` scope `add_to_variable COMECON_TARGET.TRADE_COMECON_RATE = ±1`).
- `common/scripted_effects/COMECON_Effects.txt:309–312`: only `#TRADE_COMECON_RATE` comment and a table `5 10 20 40 80 160 / 2.5 5 10 20 40 80`. **No effect body** reads `TRADE_COMECON_RATE`; grep for `TRADE_COMECON_RATE` across the mod returns only GUI and this comment.
- `common/dynamic_modifiers/IC_Comecon_Modifiers.txt`: `comecon_member` modifier (production, construction, needs discount `COMECON_NEEDS_DISCOUNT`, etc.). Comments mention "Trade — Mutual Trade Adjustment Cost" and "Economic support gives a percentage of your monthly income", but no trade modifier is defined in the file.

## 4. Interactions

- **Money**: trade is an income/expense line in IncomeGenerator (§3f). Purchases always debit the buyer's IncomeTotal; sales credit the seller via `*ExportTargetMonthly`. Money cost of imports is not gated by treasury balance `[INFERENCE]`.
- **Production/infra**: trade capacity depends on air bases, office parks and state infrastructure (IncomeGenerator L162–171), multiplied ×8 (L425). Cap check in CG AI gate (`trade_infrastructure_total_available > 0.99`, CG AI L21).
- **Taxes/laws/policies**: export rates (`_economic.txt` tiers), price bonuses/penalties (New_Ideologies, JAP, Indonesia, brazil), trade_opinion_factor (Revamped_Trade_Policy, usa.txt), embargo (`trade_embargo_check`), ECSC price adder (ECSC.txt).
- **Diplomacy**: embargo flags set by scripted diplomatic actions (`scripted_diplomatic_actions.txt:61,100`) and history; `has_war_with` blocks trade.
- **Autonomy**: `extra_trade_to_overlord_factor` and `overlord_trade_cost_factor` (autonomous_states).
- **UI**: Trade_Tab buttons use the same arrays and variables; manual buttons disabled under `trade_automation = 2`.
- **AI**: AI runs `trade.1` monthly (`00_on_actions.txt:53`) and CG AI (`consumer_goods_ai_automated_trade_effects.txt:17–18` gate `is_ai = yes` OR automated, plus infra > 0.99).
- **Credit**: `credit_calculation_work` runs from UNS scope monthly; not directly trade-price-linked.

## 5. Problems

### High
1. **Concession chromium target bug** — `resource_concession_evaluation.txt:172–173, 190–192, 209–211, 228–230`: chromium gains are subtracted from `var:aluminium_concession_target` instead of `chromium_concession_target`. The aluminium target is corrupted, and chromium gains are never removed from their own target. The 100-tier block (L228–243) also uses the aluminium target. Also L176, 195, 214, 233 use `nuclearBonus` as the chromium bonus (naming, possibly intentional; [INFERENCE] unclear).
2. **Concession evaluation scheduling** — the only live call is `events/tutorial.txt:129` inside event `resource.1250` (L88–129) in an `else` branch of a startup-type block. `IC_scripted_effects.txt:93` is commented out. The concession effect appears to run once at setup, not monthly `[INFERENCE]`. Concession modifier block (`0_dynamic_modifiers.txt:268–271`) is commented out in `tutorial.txt` (L~112–115 `#add_dynamic_modifier = resource_concessions`). So concessions are effectively inert after setup `[INFERENCE]`.
3. **AI single-supplier truncation** — `sort_price_number_*_ai` (IC_Trade L4506–4655) keeps only the cheapest exporter per resource per tick. The AI never splits a purchase across suppliers, so AI under-buys whenever the cheapest supplier's `currentAvailable` is below demand, and it ignores the rest of the market. Severity high for AI participation.
4. **Shipping effect with no writer** — `shipping_cost_effect` is read at IC_Trade L427, 1222, 1928, but no writer exists. Any intended distance modifier is inert.

### Medium
5. **`price_adjust_oil`, `price_adjust_chromium`, `price_adjust_steel` have no writers** (readers IC_Trade L319, 1821, 2782). Only `price_adjust_food` (INDIA_60s.txt:1207) and `price_adjust_generic` (ECSC, DOM, LIB, 50s_NIC) are written. Per-resource adjusters are dead for three of six resources.
6. **Comecon trade rate is GUI-only** — `COMECON.txt:631–660, 742–753, 1091–1092` change `TRADE_COMECON_RATE`, but no effect reads it (`COMECON_Effects.txt:309–312` comment only). Player-facing lever with no effect `[INFERENCE: no read in whole mod per grep]`.
7. **Undefined token reference** — error.log L5857–5858: "Tried to get dynamic token that does not exist: stabilizing_oil_prices" (USA_80s_CIA.txt). error.log L6338: "add_timed_idea: Invalid idea: Stabilizing_Oil_Prices" (`common/national_focus/USA_Agnew_1980.txt:60`). Needs `var:` prefix or a missing idea definition. No such idea defined in the trade slice.
8. **Revamped_Trade_Policy OOS** — error.log L5924–5925: "Token Revamped_Trade_Policy is a dynamic token, this can cause OOS". Token defined at `synchronized_dynamic_tokens/tokens.txt:1299`; the warning means it is a dynamic token used in a synced context.
9. **Global trade bonus sign** — `global_trade_bonus_adjustment` reduces price by `(1 − x)`. JAP_Ideas.txt L511–559 has negative values (raises price) paired with `trade_opinion_factor`. Positive bonus lowers the export price for exporters `[INFERENCE: intended meaning]`.
10. **Per-cut reset** — delivery cuts reset available capacity to 1 and used to 1 regardless of size (`Cuts.txt` L36–42, etc.). Capacity can be lost or inflated `[INFERENCE]`.
11. **Stale registry** — `cwic_rebuild_trade_exporter_lists` runs every 25 days (`00_on_actions.txt:30–32`). Between rebuilds, exporters that gained or lost availability are not reflected in importers' arrays `[INFERENCE: array only reflects state at rebuild]`.

### Performance hot spots (per month)
12. `export_script_for_pool`: every_other_country × every_controlled_state per owner (UNS scope; `00_on_actions.txt:43`). Nested loops over all countries and states.
13. `trade.1` per AI and per automated player (`00_on_actions.txt:46–59`): each runs `trade_check` (6 `_import_ai`), each iterating exporter arrays with nested every_other_country and for_loop over `*ExportTarget^num`.
14. CG chain: ~36 tiers × (generate + sort + buy). `IC_Trade_Scripted_Effects.txt` CG tiers L5194–12537. Plus `cwic_ai_consumer_goods_trade_master` per AI per month.
15. Registry rebuild every 25 days: every_country × 36+ arrays (`CWIC_trade_exporter_lists.txt:36–37`).
16. `IncomeGenerator.txt` export/import dedupe loops (L559–703, L1262–1410) run per country per month.

### Dead / debug / duplicate code
- `price_Adj2` (set/subtract only; IC_Trade L329–369, 1116–1160, 1830–1870).
- `aluminium_test` (IC_Trade ~L103, temp residue in export_script_for_pool).
- `exp_test` (IC_Trade ~L345).
- `test_script` (IC_Trade L252–258; calls startup_price_setting, USA pool, buy_nuclear_material).
- `test_for_Trade_modifiers` (IC_Trade L4667–4673; sets `test3 = NGA.modifier@extra_trade_to_overlord_factor`).
- `cwic_ai_consumer_goods_trade_master_with_immediate_delivery` (CG AI L4282–4289) — not called from the monthly chain found so far `[INFERENCE]`.
- `10_Yearly_On_Action.txt:14–33` (commented trade_check), `_generic_decisions.txt:1503–1505` (retired calls), `IC_scripted_effects.txt:93` (commented concession call), `0_dynamic_modifiers.txt` `resource_concessions` (commented in tutorial).
- Duplicate `cwic_ai_import_*` / `sort_price_*` families for each resource: pattern duplicated ~6 times rather than generalized.
- Repo `scratch/` (check_trade_tab_gui.py, check_trade_tab_sguis.py, compare_trade_gui.py): throwaway, not in mod.

### Balance red flags
- Export rate tiers (`_economic.txt`): chromium tier 1 0.25 vs oil/steel 0.7 — chromium exports heavily restricted at tier 1 but chromium price 2 (startup_price_setting) — ratio unverified.
- CG price tiers grow ~25× from T0 to T5 (basic 0.03→0.25 is ~8×; vehicles 0.35→2.50 is ~7×; durable 0.08→0.80 is 10×). Check relative to chromium at 2.
- Shipping divisor 1000 vs CG divisor 10000 (`on_startup_defines.txt:2630–2631`) — CG shipping 10× cheaper; intentional? [INFERENCE].
- Penalty adjustments up to +0.5 (New_Ideologies L6647) vs bonus up to +0.25 (Indonesia) — asymmetric.

### AI not participating
- Single-supplier truncation (#3).
- CG AI requires `trade_infrastructure_total_available > 0.99` (CG AI L21); infra reset to 0 then rebuilt each month (IncomeGenerator L289–293, 424–431) — AI capacity starts from zero each month before ×8 scaling.
- Concessions inert after setup (#2) — AI gets no concession income `[INFERENCE]`.

### error.log entries (trade)
- L5857–5858: stabilizing_oil_prices token missing.
- L5924–5925: Revamped_Trade_Policy dynamic token OOS warning.
- L6338: Stabilizing_Oil_Prices invalid idea (USA_Agnew_1980.txt:60).
- No errors matched IC_Trade, Trade_Tab, COMECON or concession files in the grep (a broad grep was capped; re-check with a file-scoped grep if needed).

## 6. Open questions
1. Whether `resource_concession_evaluation` is scheduled anywhere beyond the one-time `resource.1250` call (grep across all `events/` and `common/on_actions/` not exhaustive; `tutorial.txt:129` only found).
2. Where export income is added to `IncomeTotal` (IncomeGenerator L559–703 region not fully read).
3. Whether `trade_automation` is initialized anywhere (default unset → manual).
4. Whether `cwic_ai_consumer_goods_trade_master_with_immediate_delivery` is called (not found in monthly chain).
5. Whether `price_adjust_chromium/oil/steel` intentionally unused, and whether `shipping_cost_effect` should be written by anything.
6. Whether `COMECON_TARGET.TRADE_COMECON_RATE` should drive trade prices or income; no consumer found.
7. Full CG registration body (`CWIC_trade_exporter_lists.txt:84–442`) and CG buy/sort bodies (IC_Trade L7622+, L10624+) not fully read.
8. Convoys (`common/units/equipment/convoys.txt`) treated as out of scope (vanilla naval/convoy, not trade economy).
9. Exact sign convention of `global_trade_bonus_adjustment` across JAP vs others.
