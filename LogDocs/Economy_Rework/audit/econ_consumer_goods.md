# Consumer Goods (CG) Economy Audit (Econ-fix)

Scope: `common/scripted_effects/IC_Consumer_Goods.txt` (CG engine), `CWIC_trade_exporter_lists.txt:1-442` (CG export registry), `consumer_goods_ai_automated_trade_effects.txt` (AI purchases), trade events `trade.20-42` and `trade.40` in `events/IC_Influence_events.txt`. Read-only. Unverified items marked [INFERENCE].

## 1. Entry points

| Entry | Caller | Frequency | Scope |
|---|---|---|---|
| `cwic_cg_monthly_master_tick` | `IncomeGenerator.txt:292-293` (after `gdp_calculation_effect = yes`) | Monthly | Every country (player and AI) |
| `cwic_cg_monthly_master_tick` | `events/tutorial.txt:135-137` | Once, at start (with `cwic_seed_starting_debt`, `cwic_cg_seed_starting_stockpiles`) | Start |
| `cwic_calculate_consumer_goods_trade_totals` | `scripted_guis/Trade_Tab.txt:528`, master tick | UI + monthly | Player GUI + all |
| `cwic_register_own_trade_offers` | master tick (3764); `CWIC_trade_exporter_lists.txt:36-40`; `IC_Industrial_Pulse.txt:617`; `on_actions/00_on_actions.txt:31-32` (rebuild 25 days after flag `cwic_trade_exporter_lists_built`) | Monthly + events | Every country |
| `cwic_ai_consumer_goods_trade_master` | master tick (2762) only | Monthly | AI purchases |
| `cwic_ai_consumer_goods_trade_master_with_immediate_delivery` | none found | Never | Dead (`consumer_goods_ai_automated_trade_effects.txt:4282-4283`) |

Player vs AI: the monthly engine (demand, production, stock, coverage, pressure) has no player/AI branch in the master tick (`IC_Consumer_Goods.txt:2744-2786`). AI purchasing is in `consumer_goods_ai_automated_trade_effects.txt`. Player purchasing uses the trade GUI path (`IC_Trade_Scripted_Effects.txt:7672-7673`, which increments `cgBasicT0Imports`).

## 2. Data model

- **Demand:** `cg_basic_demand`, `cg_durable_demand`, `cg_vehicles_demand`, `cg_electronics_demand`. Written in `cwic_calculate_consumer_goods_monthly_demand` (`IC_Consumer_Goods.txt:322-547`). Inputs: `ROOT.employable_population_sum` (342), HDI, decade tier from `current_year` (~345-375).
- **Stock tiers:** `cg_<cat>_stock_t0..t5`. Adds at 1233-1354; seeded at 3266-3292; imports at 3294-3320.
- **Export stock:** `cg_<cat>_export_stock_t0..t5`, `currentExportedCg<Cat>T<n>`. Used in `IC_Trade_Scripted_Effects.txt` and `cwic_cg_trade_stock_hygiene` (2787-2851).
- **Imports:** `cgBasicT0Imports` etc. Written at `IC_Trade_Scripted_Effects.txt:7672-7673` (`+= purchase_amount`) and `consumer_goods_ai_automated_trade_effects.txt:457-458` (basic T0 only shown; other tiers [INFERENCE] same pattern). Reset at `IC_Trade_Scripted_Effects.txt:4778-4788` and `scripted_guis/Trade_Tab.txt:1373-1374`. Subtracted at `IC_Trade_Scripted_Effects_Cuts.txt:411-412`.
- **Resource pools:** `cwic_res_steel_pool`, `cwic_res_coal_pool`, `cwic_res_oil_pool`, `cwic_res_aluminium_pool`, `cwic_res_tungsten_pool`. Added by `cwic_cg_sync_resource_pools_from_vanilla` (`IC_Consumer_Goods.txt:3142-3157`, adds `resource@X` every monthly tick). Decremented by spends (921, 930, 994, 1001, 1008, 1082, 1089, 1096, 1103, 1169, 1176, 1183, 1190). Read at 666-674 (tungsten gate) and 894-1068 (caps). Referenced only in `IC_Consumer_Goods.txt`.
- **Coverage/need:** `cg_<cat>_need`. Consumed by coverage weights at 2295-2702. Tier weights 5,4,3,2,1 for T5..T1 (basic 2295-2351; durable 2414-2470; vehicles 2530-2586; electronics 2646-2702).
- **Dynamic modifiers:** `CWIC_DM_CG_*`. Reset at `IC_Consumer_Goods.txt:7-24`, set at 189-216, declared in `common/dynamic_modifiers/IC_dynamic_modifiers.txt:950-972`.
- **Shared scalars:** `master_scalar` (164-182), `sev_basic/durable/vehicles/electronics`, `CWIC_bm_stability_penalty` (200-204, clamped 0..0.20).
- **Export rate:** `economic_modifier_market_resources`, written by `IC_Economy_Effects.txt` (39, 84, 206, 248, 543, 557, 572, 624, 644; cleared 582, 592) and `national_focus/TIB_1950s.txt:1218-1220,1274`. Shared by 7 export rates (`0_dynamic_modifiers.txt:408-415`). `economic_modifier_consumer_goods_need` (written at `IC_Economy_Effects.txt` 35-36, 80-81, 202-203, 244-245; TIB_1950s.txt) maps to `consumer_goods_factor` (`0_dynamic_modifiers.txt:395`).

## 3. Formulas

Master tick order (`IC_Consumer_Goods.txt:2744-2786`): demand (322) -> production_and_allotment (548; calls sync at 550) -> apply imports (3294) -> export stock (3560) -> apply existing exports (3322) -> AI trade (2762) -> trade stock hygiene (2787) -> consume and coverage (1411) -> update modifiers (1999) -> pressure master (3) -> trade totals (3451) -> export stock totals (`IC_Trade_Scripted_Effects.txt:12625`, called 2776) -> monthly balance (3522) -> stockpile hygiene (2853).

1. **Demand** (322-547):
   - HDI clamp 337-339. `hdi_scale = 0.60 + 0.80*HDI`; `elec_hdi_scale = 0.30 + 1.20*HDI`.
   - HDI tier adjust: HDI < 0.35 gives -1; HDI > 0.80 gives +1. Electronics clamped to 1..5.
   - Basic: `pop_k * 0.12 * hdi_scale * mult[tier] * 0.01`, mult 0.80/1.00/1.05/1.10/1.15/1.20 (~430-440); floor 1 (~458-460).
   - Durable: base 0.05, mult 0.50/0.80/1.00/1.15/1.30/1.45, times 0.01.
   - Vehicles: base 0.02, mult 0.40/0.70/0.90/1.05/1.20/1.35, times 0.01.
   - Electronics: base 0.015, mult 0.60/0.90/1.15/1.40/1.70 (tiers 1..5), times 0.01.
   - `round_variable` on all four demands (~510-513).
2. **Production** (548-1410): civilian factory calc `calculate_civilian_factory_production_total_factories` (282-321) with `cg_locked` driven by `modifier@consumer_goods_factor`. Electronics tungsten gate (659-674): `gate = clamp((cwic_res_tungsten_pool - 1)/15, 0, 1)`. Spend order: basic steel/coal (893-1008); durable steel/aluminium/coal (956-1008); vehicles steel/aluminium/oil/coal (1034-1103); electronics aluminium/tungsten/coal/oil (1130-1190). Each spend caps by pool (`pool / units - 0.49`, rounded), then subtracts from pool. Tier adds 1233-1354. Points allocation 3165-3265: `cg_points_per_factory = 25` hard-set at 3166; fallback 10 at 3174-3176.
3. **Consume and coverage** (1411-1998): weighted coverage sums (weights above) and need reduction. `CG_construction = -0.12*sev_vehicles - 0.02*sev_basic` (2163-2166); consumer [INFERENCE: not traced].
4. **Master scalar** (164-182): `0.35*sev_basic + 0.20*sev_durable + 0.25*sev_vehicles + 0.20*sev_electronics`, capped at 1.
5. **Pressure** (189-216):
   - `CWIC_DM_CG_STABILITY_FACTOR = master_scalar * -0.18`, then minus `CWIC_bm_stability_penalty` (207).
   - `CWIC_DM_CG_POLITICAL_POWER_GAIN = master_scalar * -0.20` (209-210).
   - `CWIC_DM_CG_WORKFORCE_RATIO = sev_basic * -0.15` (213-214).
   - `CWIC_DM_CG_WELFARE_SPENDING_MOD = sev_basic` (216).
6. **Inflation back-derivation** (`IC_Inflation_Effect.txt:86-98`): `cg_pressure = CWIC_DM_CG_STABILITY_FACTOR / -0.18`, clamped 0..1, squared, times `k_sp`.
7. **Export rate** (`0_dynamic_modifiers.txt:408-415`; `IC_Trade_Scripted_Effects.txt:24`): `consumerGoodsExportRate` = `economic_modifier_market_resources`.
8. **Monthly balance** (3522-3555): per category `produced + imports - demand - exports`.

## 4. Interactions

- **Treasury (`income_effect`, `IncomeGenerator.txt`):** CG runs inside the income path (IncomeGenerator.txt:292-293). No direct money transfer found in CG files [INFERENCE: not exhaustively grepped]. Income effects via `CWIC_DM_CG_OTHER_RESOURCES_INCOME_BONUS` (dyn mod 965), `..._INDUSTRIAL_PARK_INCOME_BONUS` (968), `..._OFFICE_PARK_INCOME_BONUS` (969). Writers not located [INFERENCE: likely in 1999-2259, not fully read].
- **GDP (`gdp_calculation_effect`, `IC_Econ_2024.txt`):** called just before the master tick (IncomeGenerator.txt:292). No CG variable found read by the GDP block in scope. Indirect via `cg_locked` and `productivity_factor` (dyn mod 956) [INFERENCE].
- **Stability/political power/workforce/welfare/policing/public services/education:** dyn mods at `IC_dynamic_modifiers.txt:951-972`.
- **Trade:** registry `CWIC_trade_exporter_lists.txt:150-440` checks `cg_<cat>_export_stock_tN > 0.99` AND `currentExportedCg<Cat>TN > 0.99`, then adds to `global.cwic_ex_cg_<cat>_tN`. No electronics T0. Delivery cuts triggered by events: trade.40 (basic T0) calls `cgBasicT0DeliveryCuts` (confirmed at `IC_Influence_events.txt:67-76`); trade.41 durable T0; trade.42 vehicles T0 (78-97); trade.20-24 basic T1-T5; trade.25-29 durable T1-T5; trade.30-34 vehicles T1-T5; trade.35-39 electronics T1-T5 (100-313). Bodies beyond trade.40-42 and trade.20 not read [INFERENCE].
- **Taxes/policies:** no writers of CG variables found in scope [INFERENCE].
- **UI:** `Trade_Tab.txt:528` (totals), `Trade_Tab.txt:1373-1374` (reset). `Financial_Tab_l_english.yml:282-287` tooltip labels for the 7 shared export rates do not match them [INFERENCE: consumer_goods_export_rate label absent].
- **Factories:** `consumer_goods_factor` feeds `cg_locked` (`IC_Consumer_Goods.txt:298-302`), tying civilian factory count to CG need.
- **AI purchases** (`consumer_goods_ai_automated_trade_effects.txt`):
  - Master 3-37: calls four category effects (23-27), sets `purchase_amount = 0` (30), need = monthly demand minus domestic stock (44-45).
  - Category wrappers: basic 38-117, durable 118-197, vehicles 198-277, electronics 278-348.
  - Tier effects: basic t0-t5 at 349, 520, 691, 862, 1033, 1204; durable t0-t5 at 1375, 1546, 1717, 1888, 2059, 2230; vehicles t0-t5 at 2401, 2572, 2743, 2914, 3085, 3256; electronics t1-t5 at 3427, 3598, 3769, 3940, 4111.
  - Each ~171 lines, gated `cg_<cat>_ai_need > 0.99`. 23 tier effects total.

## 5. Problems

| # | Sev | Location | Problem |
|---|---|---|---|
| 1 | H | `IC_Consumer_Goods.txt:3145-3149` | Sync adds full vanilla `resource@X` to `cwic_res_*_pool` every monthly tick, with no reset; spends only subtract. Mod never writes `resource@X` (only commented lines 2894-2898). Pools accumulate, so the caps (894-1068) and tungsten gate (666-674) are effectively unbounded. [INFERENCE on engine semantics: flow vs stock.] |
| 2 | H | `IC_Inflation_Effect.txt:90-91` with `IC_Consumer_Goods.txt:207` | Shortage pressure reconstructed by dividing `CWIC_DM_CG_STABILITY_FACTOR` by -0.18. That modifier includes `- CWIC_bm_stability_penalty`, so black-market penalty is counted as shortage pressure. Clamp at 93-94 hides it. |
| 3 | M | `IC_Consumer_Goods.txt:2260-2739` | Dead legacy `cwic_calculate_consumer_goods_coverage_and_consume` (~480 lines); not called; comments at 2741-2742 warn against it. |
| 4 | M | `consumer_goods_ai_automated_trade_effects.txt:4282-4283` | Dead wrapper `..._with_immediate_delivery`. |
| 5 | M | `consumer_goods_ai_automated_trade_effects.txt:349-4111` | 23 near-identical ~171-line tier blocks. Electronics has no t0 (starts 3427); intent [INFERENCE: unconfirmed]. |
| 6 | M | `IC_Consumer_Goods.txt:3166` vs 818-819 | `cg_points_per_factory = 25` hard-set, overriding config; comment says 10; fallback 3174-3176 unreachable. |
| 7 | M | `IC_Consumer_Goods.txt:322-547` | Comments say base 0.12; effective 0.0012 per thousand workers (extra *0.01). |
| 8 | M | `IC_Consumer_Goods.txt:~510-513` | `round_variable` zeroes durable/vehicles/electronics demand below 0.5; small nations never fire those tiers. |
| 9 | M | `IC_Consumer_Goods.txt:923, 932, 934-935` | Debug leftovers `units_basic_test6`, `cg_tmp_test`, `units_basic_test8`, `cwic_res_coal_pool_test`. |
| 10 | M | `IC_Consumer_Goods.txt:2163-2166` | `CG_construction` consumer not located [INFERENCE]. |
| 11 | L | `Financial_Tab_l_english.yml:282-287` | Export-rate tooltips mismatch the rates they feed. |
| 12 | L | `consumer_goods_ai_automated_trade_effects.txt:457-458` | Only basic T0 import write confirmed; other tiers [INFERENCE]. |
| 13 | L | `IC_Influence_events.txt:67-313` | 30 one-line trigger events calling `*DeliveryCuts`; verbose but fine. |

Performance: master tick runs monthly for every country (`IncomeGenerator.txt:293`). AI path runs up to 23 tier blocks per AI country per month when gated. Not measured [INFERENCE].

## 6. Open questions

1. Is `resource@<resource>` a per-month flow or a stock? Decides severity of #1.
2. Writers of `CWIC_DM_CG_OTHER_RESOURCES_INCOME_BONUS`, `..._INDUSTRIAL_PARK_INCOME_BONUS`, `..._OFFICE_PARK_INCOME_BONUS`, `..._CONSTRUCTION_SPEED_FACTOR`, `..._PRODUCTIVITY_FACTOR` (in unread `IC_Consumer_Goods.txt:1999-2259`).
3. Do any treasury or GDP effects read CG variables? Not exhaustively checked.
4. Electronics t0 absence: intentional?
5. Bodies of trade.20-39 and 41-42 unread.
6. Are `*DeliveryCuts` effects (`IC_Trade_Scripted_Effects_Cuts.txt`) the only consumer of the export registry?

Top findings: (1) monthly pool accumulation from vanilla `resource@X` (H); (2) black-market penalty leaking into shortage pressure (H); (3) ~500 lines dead legacy code plus dead wrapper (M); (4) hard-set `cg_points_per_factory = 25` (M); (5) demand docs/code mismatch and small-country zeroing (M).
