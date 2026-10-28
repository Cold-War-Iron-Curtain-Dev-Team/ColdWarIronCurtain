# CWIC Economy: Remaining Trade Audit (Trade_Tab, Comecon, chromium_import_ai, resource coexistence, UNS assumptions)

Scope: read-only audit. Paths are relative to `Cold War Iron Curtain/` unless stated. Line numbers come from grep and range reads; items marked `[INFERENCE]` were not fully verified. Not reviewed in this slice: `IncomeGenerator.txt` (`income_effect`), the body of `gdp_calculation_effect` in `IC_Econ_2024.txt`, `Economy_System_Overview.md` sections 1-2, and the prior audit files in `LogDocs/Economy_Rework/audit/`. Overlap with those is not checked.

## Summary (top findings)

1. **H** `chromium_import_ai` writes its result into `nuclear_total`, which no modifier reads. The engine import modifier reads `nuclearImports` (`0_dynamic_modifiers.txt`, `resource_trade`). Chromium buys therefore never reach the resource modifier, and the variable is overwritten from the stock on every call.
2. **H** Every `buy_*_click` in Trade_Tab writes the same prompt variable `ROOT.currentAvailableChromiumExportPrompt` and `ROOT.chromium_prompt = 1`, regardless of resource. The prompt is shared across all resources.
3. **M** `buy_steel_click` and `buy_chromium_click` omit the `ExportTargetAmount` add that the other `buy_*` effects perform, so their available-amount calculation is inconsistent.
4. **M** `TRADE_COMECON_RATE` has no economic consumer. It is a GUI slider variable. The `comecon_gross_ratio_calc` effect has no trade block, only a comment at line 309.
5. **M** The Comecon tier tables disagree: CON and PRO map level 6 to 160 and level 1 to 5, while RES, ECO and MIL map level 6 to 80 and level 1 to 2.5.
6. **M** `on_startup_defines.txt:3536` runs `UNS = { export_script_for_pool }` with no existence guard. `UNS` is defined in `history/countries/UNS -UN.txt`, so the tag exists at normal bookmark starts `[INFERENCE]`.
7. **L** Several localisation and label defects in `IC_Comecon.txt`, including Imre Nagy mapped to the Rakosi portrait and a key typo `Rufolf`.

---

## 1. Entry points

### 1a. Trade_Tab GUI (`common/scripted_guis/Trade_Tab.txt`)
- Player-only UI. Windows and their effects:
  - `Quality_Prompt` L29-89: `confirm_quality_click`, `cancel_button_click`, `quality_level_select_click` (sets `ROOT.CG_Quality_Cat = global.consumer_good_tier_list^i`).
  - `Chroium_Buy_Prompt` L90-545 (misspelled ID): quantity buttons `increase_chromium_click` L228, `increase_chromium_shift_click` L246, `decrease_chromium_shift_click` L263, `decrease_chromium_click` L280, `decrease_chromium_control_click` L297, `confirm_chromium_purchase_click` L317-529, `cancel_button_click` L530.
  - `chromium_exporter_list` L546-1147: exporter list windows bound to arrays `cgBasicT0Exporters`…`cgElectronicsT5Exporters`, `foodExporters`, `steelExporters`, `aluminiumExporters`, `rareEarthExporters`, `oilExporters`, `chromiumExporters` (L998-1146).
  - Effects L1148-2967 contain the trade-automation toggle (`trade_automation_button_click` L1149), the cancel-import effects (L1167-1917), sort/switch effects (L1923-2247), and the buy effects (L2252-2967).
- Buttons enabled only when `NOT ROOT.trade_automation = 2` (L138-227 and in the exporter list). This is the only player-facing gate for automation.

### 1b. Buy chain
- Per-resource GUI click effects (`buy_cg_basic_t0..t5` L2252 onward, `buy_cg_durable_*`, `buy_cg_vehicles_*`, `buy_cg_electronics_t1..t5` L~2700-2825, then `buy_food_click` L2826, `buy_rare_earth_click`, `buy_aluminum_click`, `buy_oil_click`, `buy_steel_click`, `buy_chromium_click` L2944) set the prompt variables and do not purchase.
- `confirm_chromium_purchase_click` (Trade_Tab.txt:317-~529) sets `chromium_prompt = 0` (L318-320) and dispatches to scripted effects: `buy_nuclear_material` (if `nuclear_trade = 1`), `buy_food`, `buy_oil`, `buy_steel`, `buy_aluminium`, `buy_rareEarth`, and the basic CG tier chain (`basic_trade`, `CG_Quality_Cat`). Each dispatch is gated by a `*_trade = 1` flag.

### 1c. AI entry
- `chromium_import_ai` is a scripted effect (`common/scripted_effects/IC_Trade_Scripted_Effects.txt:794`), called from `IC_Trade_Scripted_Effects.txt:4662` (`chromium_import_ai = yes`), inside an effect that also calls `rareEarth_import_ai` at ~L4661. Caller frequency is `[INFERENCE]` because the enclosing effect was not traced here.
- Player vs AI: GUI effects are player-only; `*_import_ai` effects are AI-only `[INFERENCE]`.

### 1d. Startup and periodic runners for export/credit
- `export_script_for_pool` (`IC_Trade_Scripted_Effects.txt:3`) is called from:
  - `common/on_actions/00_on_actions.txt:43-45`, under `limit = { tag = UNS }`.
  - `common/on_actions/on_startup_defines.txt:3536-3537`, as `UNS = { export_script_for_pool = yes ... }`, no guard.
  - `IC_Trade_Scripted_Effects.txt:254-256` (`USA = { export_script_for_pool = yes buy_nuclear_material = yes }`).
- `credit_calculation_work` is called from:
  - `00_on_actions.txt:43-45` (under UNS limit).
  - `on_startup_defines.txt:3690-3691`, as `every_country = { credit_calculation_work = yes country_event = focus_check.1 }`.
  - `common/scripted_effects/IC_Econ_2024.txt:1411`, as `credit_calculation_work = yes #Backup Check`.
  - `common/decisions/_generic_decisions.txt:1504` comment: "Retired: export_script_for_pool, credit_calculation_work, and trade.1 now run from on_monthly." `[INFERENCE]` the on_monthly runner was not located in this slice.
- `10_Yearly_On_Action.txt:17-18` UNS block is commented out.

---

## 2. Data model (variables touched in this slice)

| Variable | Scope | Written by | Read by | Meaning |
|---|---|---|---|---|
| `currentAvailableChromiumExportPrompt` | ROOT (buyer) | every `buy_*_click` (Trade_Tab.txt L2826-2944, and per-CG blocks L2252-2825) | prompt loc `custom_trade_stuff_l_english.yml:3` | Amount shown and bought in the chromium prompt for **any** resource |
| `chromium_prompt` | ROOT | `buy_*_click`, `cancel_button_click`, `confirm_chromium_purchase_click` (Trade_Tab.txt L318) | prompt visibility | Prompt open flag |
| `purchase_amount`, `purchase_amount_prior` | ROOT | `buy_*_click`, `chromium_import_ai` (IC_Trade_Scripted_Effects.txt:829-848) | purchase logic | Amount requested, and prior amount |
| `nuclear_total` | ROOT | `chromium_import_ai` L796 (`= resource@chromium`), L845 and L943 (`+= ROOT.purchase_amount`) | `chromium_import_ai` L802, L825, L829, L1037 | Chromium balance used as a need counter (see finding 1) |
| `chromium_need` | temp | `chromium_import_ai` L829, then `*= -1` | L844+ | Amount still needed |
| `nuclearImports`, `oilImports`, `steelImports`, `aluminiumImports`, `rareEarthImports`, `foodImports` | country | scripted buy/cancel flows (not traced here) | `0_dynamic_modifiers.txt` `resource_trade` block | Import quantity fed to the vanilla resource modifier |
| `oilExport`, `foodExport`, `steelExport`, `chromiumExport`, `aluminiumExport`, `rareEarthExport` | country | zeroed by `export_script_for_pool` (IC_Trade_Scripted_Effects.txt:~24-30, `every_other_country`) | `resource_trade` block (`country_resource_cost_* = *Export`) | Export quantity fed to the modifier |
| `*ExportRate` (`chromiumExportRate`, `oilExportRate`, `foodExportRate`, `steelExportRate`, `aluminiumExportRate`, `rareEarthExportRate`, `consumerGoodsExportRate`) | other countries | `export_script_for_pool` from `modifier@*_export_rate` (IC_Trade_Scripted_Effects.txt:~12-18) | export logic | Export rate from engine modifiers |
| `TRADE_COMECON_RATE` | `COMECON_TARGET` (SOV) | `COMECON.txt:1091-1092` (`±1`) | `COMECON.txt:631-637, 659-660, 742-753` (GUI only) | Trade cooperation slider (0-6). No economic reader found |
| `current_spending_comecon`, `comecon_spending_total`, `soviet_gdp`, `gdp_ratio` | SOV / temp | `COMECON_Effects.txt:31-307` | none found (see section 5) | Comecon spending calculation |

Vanilla resource-trade mutation sites (not scripted trade): `add_resource` appears in `common/decisions/*` and `common/ideas/*` (e.g., `rgo_development_universal.txt:31`, `ideas/ALB.txt:78`, `BUL_ideas.txt:66`, `ideas/BRU.txt:329`). No `add_resource` or `country_resource_*` write was found in `IC_Trade_Scripted_Effects.txt` or `Trade_Tab.txt` (grep returned none).

---

## 3. Formulas, step by step

### 3a. chromium_import_ai (IC_Trade_Scripted_Effects.txt:794-~1040)
1. L796: `nuclear_total = resource@chromium` (the **stock**, not a deficit).
2. L801-805: enter only if `nuclear_total < 0` and `trade_infrastructure_total_available > 0`. A positive chromium stock therefore never triggers buying.
3. L817-848: for each `ROOT.chromiumExporters` in price order (`break = cheapest_brk`), if `currentAvailableChromiumExport > 0` and (infrastructure available or `nuclear_total <= -1`):
   - L829: `chromium_need = ROOT.nuclear_total`, L831: `*= -1` (need = -stock).
   - If exporter supply > need: L840-845 set `purchase_amount = need` and `nuclear_total += purchase_amount`; L848 subtracts `purchase_amount_prior`; then subtracts from `currentAvailableChromiumExport`.
4. Second branch at L942-943 repeats the `nuclear_total += purchase_amount` add. L1036-1037 repeats the `nuclear_total > -1` check.
5. **Nothing adds the purchased quantity to `resource@chromium` or to `nuclearImports`.** The import is visible only in `nuclear_total`. The next call overwrites `nuclear_total` from the stock again (L796).

### 3b. Buy prompt (Trade_Tab.txt, per-resource blocks)
- Typical `buy_*_click` (e.g., `buy_food_click` L2826): `ROOT.currentAvailableChromiumExportPrompt = currentAvailablefoodExport + THIS.foodExportTargetAmount^ROOT` (`add_to_variable`), `pricePerUnit = foodExporterPrice^ROOT`, `purchase_amount = foodExportTargetAmount^ROOT`, `chromium_prompt = 1`.
- `buy_steel_click` (~L2880-2900) and `buy_chromium_click` (L2944-2967) set `currentAvailable*Export` without the target-amount add `[INFERENCE: read at summary level; exact lines should be confirmed]`.

### 3c. Comecon ratio (COMECON_Effects.txt:31-307)
For each member in `COMECON_MEMBERSHIP`:
1. L41-47: `SOV.gdp_ratio = member.grossdomesticproduct / SOV.soviet_gdp + 0.5`.
2. L49-99: `current_spending_comecon = CON_COMECON_RATE` mapped via tiers (6→160, 5→80, 4→40, 3→20, 2→10, 1→5, 0→0), then `× gdp_ratio`, added to `SOV.comecon_spending_total` (L98-99).
3. L101-151: PRO block (same 6→160 table).
4. L153-203: RES block (6→80, 5→40, 4→20, 3→10, 2→5, 1→2.5).
5. L205-255: ECO block (same as RES).
6. L256-306: MIL block (same as RES/ECO).
7. L309: `#TRADE_COMECON_RATE` (comment only). The trade rate is not processed.
8. L311-312: comment tables `#5 10 20 40 80 160` and `#2.5 5 10 20 40 80`.

### 3d. Engine resource modifiers (common/dynamic_modifiers/0_dynamic_modifiers.txt, range ~199-265)
- `food_negative_in_capital`: `country_resource_cost_rubber = var:food_consumption`, `country_resource_rubber = var:FoodProdTotalBonus`.
- `resource_consumption` (after L221): `country_resource_cost_{steel,oil,chromium,aluminium,tungsten,coal}` = `{steel,oil,nuclear,aluminium,rare_earth,electricity}_consumption`; `country_resource_{steel,oil,aluminium,chromium,tungsten}` = `{steel,oil,aluminium,nuclear,rare_earth}_resource_bonus`; `stability_factor`/`war_support_factor` = `food_penalty_political`; `production_factory_max_efficiency_factor` = `food_penalty_production`; `production_speed_buildings_factor` = `food_penalty_construction`; `min_export = -0.2`.
- `resource_trade` (after the comment near L250): `country_resource_cost_{oil,rubber,steel,chromium,aluminium,tungsten}` = `{oilExport,foodExport,steelExport,chromiumExport,aluminiumExport,rareEarthExport}`; `country_resource_{steel,oil,aluminium,chromium,tungsten,rubber}` = `{steelImports,oilImports,aluminiumImports,nuclearImports,rareEarthImports,foodImports}`.

Interpretation `[INFERENCE]`: the `*Export` and `*Imports` variables are the only scripted-trade link to the engine resource stock. The engine applies them as a country-level modifier. Sign and stock effect depend on the engine and were not verified.

---

## 4. Subsystem interactions

- **Treasury** (`income_effect` in `IncomeGenerator.txt`): not reviewed. No link from trade variables to treasury was found in the files read.
- **GDP** (`gdp_calculation_effect` in `IC_Econ_2024.txt`): `IC_Econ_2024.txt:1411` calls `credit_calculation_work` as a backup check. The body of `gdp_calculation_effect` was not reviewed.
- **Trade (vanilla resources)**: scripted trade writes variables only. Engine stock changes come from `add_resource` in decisions/ideas, not from trade. The two paths connect only through the `resource_trade` dynamic modifier (section 3d). A purchase increments a variable, the modifier applies it, and stock is never directly credited. See finding 1.
- **Taxes/policies**: trade laws are slot-based (`idea_tags/00_idea.txt:28`, `trade_laws` slot). `trade_laws_cost_factor` appears only in `country_leader/cold_war_traits.txt` (not traced). `resource_export_multiplier_modifier` was not found in the mod `[INFERENCE]`. `export_script_for_pool` reads `modifier@*_export_rate` (IC_Trade_Scripted_Effects.txt:~12-18), so trade-law modifiers, if they exist, flow through there.
- **UI**: Trade_Tab and COMECON.txt windows as in section 1. Prompt loc `custom_trade_stuff_l_english.yml:3` reads `[?.currentAvailableChromiumExportPrompt|Y0]` for every resource.
- **AI**: `chromium_import_ai` and `rareEarth_import_ai` are the only AI purchase effects found in this slice. No AI counterpart for steel, oil, aluminium, or food was found here `[INFERENCE]`.

---

## 5. Problems

### H
1. **`chromium_import_ai` credits the wrong variable.** `IC_Trade_Scripted_Effects.txt:796` sets `nuclear_total = resource@chromium`, and purchases add to `nuclear_total` (L845, L943). No modifier reads `nuclear_total` (grep of `common/` returns only the scripted effect). The import modifier reads `nuclearImports` (`0_dynamic_modifiers.txt`, `resource_trade`). Result: AI chromium buys never reach the resource modifier, and the next call discards the running total by overwriting it from the stock (L796). The entry guard `nuclear_total < 0` (L802) means buying happens only when stock is already negative. Fix direction: use a dedicated deficit variable and write `nuclearImports` (or a chromium import variable); do not reuse the stock. [INFERENCE on the exact fix]
2. **Shared prompt variable.** Every `buy_*_click` writes `ROOT.currentAvailableChromiumExportPrompt` and `ROOT.chromium_prompt = 1` (Trade_Tab.txt L2826-2944 and L2252-2825). The prompt is one dialog for all resources; the name suggests chromium-only. Consequence: the prompt amount is the last clicked resource's amount, and confirm (L317-529) then dispatches on `*_trade` flags set separately. The user-visible symptom `[INFERENCE]` was not reproduced.

### M
3. **Inconsistent availability calc.** `buy_steel_click` and `buy_chromium_click` (Trade_Tab.txt ~L2880-2967) do not add `*ExportTargetAmount^ROOT`, unlike the other `buy_*_click` effects (L2826 onward). The prompt therefore shows a smaller amount for steel and chromium `[INFERENCE: confirm exact lines]`.
4. **TRADE_COMECON_RATE has no economic effect.** `COMECON_Effects.txt:309` is a comment, and comecon_gross_ratio_calc (L31-307) has no trade block. Readers: `COMECON.txt:631-637, 659-660, 742-753` (display and enable checks). Writers: `COMECON.txt:1091-1092` (slider). The slider changes nothing in the economy. Either the trade block was removed or never added; the GUI is misleading either way.
5. **Tier tables disagree.** CON (`COMECON_Effects.txt:56`) and PRO (`:108`) map level 6 to 160; RES (`:160`), ECO (`:212`) and MIL (`:263`) map level 6 to 80. Level 1 is 5 in CON and PRO (`:96`, `:148`) and 2.5 in RES, ECO and MIL (`:200`, `:252`, `:303`). The comment (L311-312) lists two different tables. Balance red flag M.
6. **Possibly unused effect.** No caller of `comecon_gross_ratio_calc` was found in `common/` or `events/` (grep: only the definition). It may be called from an unsearched directory `[INFERENCE]`. If unused, it is dead code.
7. **gdp_ratio floor.** `COMECON_Effects.txt:46-47` adds 0.5 to every member's `gdp_ratio`, so small members still get weight ≥0.5 of Soviet GDP share. Balance question M.
8. **UNS-scope assumption in on_startup.** `on_startup_defines.txt:3536-3537` runs `UNS = { export_script_for_pool = yes ... }` with no existence check. `00_on_actions.txt:43-45` guards the same call with `limit = { tag = UNS }`. `UNS` is defined in `history/countries/UNS -UN.txt` (dated entries from L120; country definition undated), so the tag should exist at bookmark start `[INFERENCE]`. Severity M if a bookmark omits the UNS history file; otherwise L.
9. **credit_calculation_work scope.** `on_startup_defines.txt:3690-3691` runs it on `every_country` with no UNS dependency. `IC_Loans_and_Interest_Rate_Effects.txt:272-275` guards the UNS reference with `if = { limit = { UNS = {...} } }`. The body of `credit_calculation_work` was not read, so UNS reads inside it are unverified `[INFERENCE]`.
10. **Export clearing per call.** `export_script_for_pool` (IC_Trade_Scripted_Effects.txt:3-30) clears export arrays and zeroes `*Export` for `every_other_country`, then reads `modifier@*_export_rate`. Import/export totals are rebuilt from scratch each call. Consistency with the buy flow (section 3a) was not verified.
11. **Resource naming collision.** `chromium` is mapped to `nuclear_consumption`, `nuclear_resource_bonus`, `nuclearImports`, and `nuclear_total` (`0_dynamic_modifiers.txt` resource blocks; `IC_Trade_Scripted_Effects.txt:796`). `nuclear_total` holds chromium. This naming hazard produced finding 1.

### L
12. **IC_Comecon.txt (scripted_localisation).** `GetPortrait` HUN section maps `Imre Nagy` to `GFX_Comecon_Matyas_Rakosi` (copy-paste). `Erno_Gero` uses an underscore while others use spaces. The `Rudolf Slansky` key is `GFX_Comecon_Rufolf_Slansky` (typo in key name). `subideology_id` lists `maoist` twice (for "Maoist" and "Anti-Revisionist"). `Political_Status` returns `NO_COMECON_STABILITY_TITLE` for stability > 0.25 and `YES_` for < 0.26; the naming looks inverted `[INFERENCE]`. The `Economic_Status` comment about food shortages is stale. Line numbers were not captured for these entries.
13. **Overlapping food keys.** `food_negative_in_capital` (`country_resource_cost_rubber = var:food_consumption`) and `resource_trade` (`country_resource_cost_rubber = foodExport`) both write rubber cost in different dynamic modifiers. Summing behavior was not verified `[INFERENCE]`.
14. **Misspelled identifiers.** `Chroium_Buy_Prompt` (Trade_Tab.txt:90) and mixed casing `buy_rareEarth` vs `buy_rare_earth_click`. Harmless but a grep hazard.

---

## 6. Open questions

1. Does any engine path read `nuclear_total`? Grep found none in `common/`. Check `interface/`, `events/`, `localisation/`.
2. Where is `comecon_gross_ratio_calc` called? Search `events/`, `history/`, and `common/national_focus/` (not found there).
3. Is the `buy_steel_click` / `buy_chromium_click` target-amount omission intentional? Confirm exact lines in Trade_Tab.txt ~L2880-2967.
4. Which on_monthly effect runs `export_script_for_pool` and `trade.1` (per the comment at `_generic_decisions.txt:1504`)?
5. How does the engine treat `resource_trade` (`*Export`, `*Imports`) against stock? Does a negative `nuclear_total` have a stock effect?
6. Do `*_trade` flags stay set after a cancel? `cancel_*_imports_click` clears import variables; not all `*_trade` flags were traced.
7. Are `trade_laws` ideas present? Only the slot (`idea_tags/00_idea.txt:28`) was found; no idea file using `trade_laws` was located.
8. Do `IncomeGenerator.txt income_effect` and `IC_Econ_2024.txt gdp_calculation_effect` read any trade variable? Not checked in this slice.
9. Are `rareEarth_import_ai` and other AI purchase paths symmetric with `chromium_import_ai`? Not checked.
