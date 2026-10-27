# Audit: income_effect resource / export income and corruption (IncomeGenerator.txt 287-1265, import debit 1256-1919, money credit 2009-2010)

Target path (not writable with this tool): LogDocs/Economy_Rework/audit/econ_income_resources.md
Read-only audit. No other file edited.

## 1. Entry points
- `income_effect` defined at `common/scripted_effects/IncomeGenerator.txt:287`.
- Callers:
  - `IC_scripted_effects.txt:57` inside `ic_financial_monthly_pulse` (`IC_scripted_effects.txt:1-60`). Live monthly path. AI gating not re-read in this slice [INFERENCE].
  - `events/tutorial.txt:125` (one-off).
  - `decisions/_generic_decisions.txt:1533-1534`, inside `ic_Financial` `complete_effect` (`every_country { income_effect = yes }`). Mission has `activation = { always = no }` (`_generic_decisions.txt:1519-1543`): unreachable, dead.
- No other scripted_effects file calls `income_effect` (grep over common, events, history).

## 2. Data model
| Variable | Scope | Meaning | Writers | Readers |
|---|---|---|---|---|
| resource_income | ROOT | Exporter credit: oil, Al, rubber(food), tungsten(rare earth), steel, Cr, × trade_credit_factor | IncomeGenerator.txt:1207-1216 (reset 460-472) | :1230; CWIC_laws_l_english.yml:170 |
| consumer_goods_export_income | ROOT | Exporter credit for CG exports, × factor | sum 1141-1167; multiply 1222-1224 | :1233; display |
| trade_income | ROOT | Display total: CG + Al + rubber + W + steel + Cr + oil (+ reparations, 1185-1187), unfactored | 1168-1184 | CWIC_core_l_english.yml:55,169; pie_chart_scripted_effects.txt:7-9,35 |
| custom_income | ROOT | Permanent PRC accumulator | common/national_focus/Trees for 0.35/PRC_50s_New.txt:1364 (+0.9), :1380 (+2), :4871 (+1), written as PRC.custom_income | :1227. Never reset. |
| trade_credit_factor | ROOT | Multiplier on exporter income | IC_Loans_and_Interest_Rate_Effects.txt:98 (set 1); IncomeGenerator_ideas_and_flags.txt:116 (+0.1, EEC currency flag), :122 (+0.25, EFTA flag) | clamp 1192-1206; used 1214, 1222 |
| xExportTargetMonthly^partner | exporter | Export value to partner (price × purchase_amount) | IC_Trade_Scripted_Effects.txt 506-511, 1271-1278, 2007-2014 etc. | export loops 643-1140 |
| xImportTargetMonthly^partner | importer | Mirror value | IC_Trade_Scripted_Effects.txt 516, 882, 979, 1281, 2017 etc. | import loops 1349-1870 |
| Oil_Export_List | exporter | importer ids | IC_Trade_Scripted_Effects.txt:1968-1980 (add_to_array = { Oil_Export_List = ROOT.id } on THIS=exporter) | export loops |
| resource_cost | ROOT | Total import debit | 1901-1909 | 1911, 1913, 1963 |
| CorruptIncomeLoss | ROOT | Corruption rate = CorruptionLevel × 0.5 | 1243-1246 | CWIC_laws_l_english.yml:184 (shown as money) |
| CorruptLoss | ROOT | Corruption amount = IncomeTotal × rate | 1249-1252 | 1254, 1946, 1957; CWIC_laws_l_english.yml:159 |
| totalexp | ROOT | Expense accumulator | 419, 1254, 1911 | overview B6: never read [INFERENCE] |
| custom_expenses | ROOT | Reparations payer charge | reset 402; add 416 | 1916, 1966 |

## 3. Formulas, step by step
3.1 Reset and tourism: 460-472 reset resource/CG/export vars (custom_income not reset). 452-458 IncomeTotal += tourism_infrastructure_total; TI_Display.
3.2 Export loops 553-1140: nuclear->chromium 553-575 (temp chromium_export_check never read); food 576-595 -> rubber_exports += foodExportTargetMonthly^THIS; oil 597-614 (Oil_Export_List); steel 616-638; aluminium 641-658; rare earth ~660-675 -> tungsten_exports; CgBasicT0 696; CgBasicT1-5, CgDurableT0-5, CgVehiclesT0-5, CgElectronicsT1-5 700-1140. Each dedupes against ROOT.Export_List; cleared per loop. No CgElectronicsT0 anywhere in range.
3.3 1141-1167 consumer_goods_export_income = sum cgBasic0-5, cgDurable0-5, cgVehicles0-5, cgElectronics1-5 (unfactored). 1168-1184 trade_income = CG + Al + rubber + W + steel + Cr + oil (unfactored). 1185-1187 trade_income += reparations_exp if reparations > 0 (display only).
3.4 Factor 1192-1206: if factor = 0 or < 0, set to 1. 1207-1216 resource_income = (oil+Al+rubber+W+steel+Cr) × factor. 1222-1224 CG income × factor (FIX comment 1218-1221). 1226-1234 IncomeTotal += custom_income, += resource_income, += CG income. 1235-1236 display_income = IncomeTotal.
3.5 Corruption 1242-1254: CorruptIncomeLoss = CorruptionLevel × 0.5; CorruptLoss = IncomeTotal × CorruptIncomeLoss (IncomeTotal here excludes imports and expenses); totalexp += CorruptLoss. Later 1946 total_expenses += CorruptLoss; 1954 IncomeTotal -= total_expenses; 1957 domestic_cost = CorruptLoss.
3.6 Imports 1256-1919: reset 1256-1264; import loops 1349-1870 (Food 1350, Nuclear 1368, Oil 1386, Steel 1404, Al 1422, RareEarth 1440, CG 1459-1870); consumer_goods_import_cost 1873-1899; resource_cost 1900-1909 = CG imports + Al + rubber + W + steel + Cr + oil (NO factor); 1911 totalexp += resource_cost; 1912-1914 IncomeTotal -= resource_cost; 1915-1919 IncomeTotal -= custom_expenses, total_insurgency_funding.
3.7 1945-1954 total_expenses = CorruptLoss + military + welfare + policing + ...; IncomeTotal -= total_expenses. 1968-2008 SubsidiyCheck = IncomeTotal × 0.25; subsidy SOV.currentMoney -= subsidiy_base (2003), IncomeTotal += subsidiy_base (2006). 2009-2011 currentMoney += IncomeTotal (only treasury credit of IncomeTotal). 2027 IncomeCheck = IncomeTotal. 2662 IncomeTotal = 0 (second branch, not verified). 2731-2825 second military block.
IC_scripted_effects.txt:58 add_to_variable currentMoney += modifier@war_reperations (after income_effect in pulse). Modifier: 0_dynamic_modifiers.txt:440 war_reperations = economic_modifier_war_reparations.

## 4. Subsystem interactions
- Treasury: currentMoney += IncomeTotal (2010); currentMoney += modifier@war_reperations (IC_scripted_effects.txt:58).
- GDP: gdp_calculation_effect in IC_Econ_2024.txt: NOT read in this slice.
- Trade: values from IC_Trade_Scripted_Effects.txt (price = <good>ExporterPrice^ROOT × purchase_amount, 506-511, 1271-1276, 2007-2011). Shortfall cuts IC_Trade_Scripted_Effects_Cuts.txt:52,55 reduce both sides. Clears IC_Trade_Scripted_Effects.txt:4687-4793; Trade_Tab.txt:1185-1651.
- Reparations: cwic_process_war_reparations at 288; payer charge custom_expenses 402-419; receiver display only at 1185-1187.
- Factor: IncomeGenerator_ideas_and_flags.txt:99-123; tax_credit_factor reset at IC_Loans...:100-103 (unused in this range [INFERENCE]).
- UI: display_income (CWIC_core_l_english.yml:34; Finance_Tab.gui:3299; COMECON_Redux.gui:1138); trade_income/TI_Display (CWIC_core_l_english.yml:55,169); CorruptLoss (CWIC_laws_l_english.yml:159); CorruptIncomeLoss (:184); resource_income (:170).

## 5. Problems
5.1 H. Money not conserved on trade. Credit: resource_income and CG income × trade_credit_factor (1207-1224). Debit: resource_cost raw (1900-1909). With factor 1.1 or 1.25 each export creates 0.1-0.25 extra money.
5.2 H. Trade with AI one-sided. AI does not run income_effect on the monthly pulse [INFERENCE: gating from caller set, IC_scripted_effects.txt:57]. Player exports to AI create money; player imports from AI vanish.
5.3 H. Inverted clamp: 1192-1206 maps factor <= 0 to 1 (full credit instead of none). Money-creation path with 5.1.
5.4 H. Reparations receivers never credited to IncomeTotal (1185-1187 display only). Payers charged via custom_expenses (402-419, subtracted 1916), and also via IC_scripted_effects.txt:58 modifier on currentMoney. [INFERENCE] possible double charge; sign/magnitude of reparations_exp vs modifier not verified.
5.5 M. custom_income permanent, PRC-only, never reset (PRC_50s_New.txt:1364,1380,4871; read 1227). Focus completion_reward (1355-1388).
5.6 M/L. CgElectronicsT0 absent in loops (1041-1139), sum (1141-1166), import (1784+). Intent unknown [INFERENCE].
5.7 M. CorruptIncomeLoss is a rate shown as money (CWIC_laws_l_english.yml:184, format $...B). Use CorruptLoss as fiscal_gen_corruption does (:159).
5.8 M. Corruption base = gross IncomeTotal (1249), incl. export credit, excl. imports (1913). totalexp (1254) and total_expenses (1946) both get CorruptLoss; B6 risk.
5.9 M. CorruptionLevel not clamped in this range (1243). Writers add up to +0.25 (LIB_50s.txt:1969); rate >1 would exceed IncomeTotal. Clamp not found in slice.
5.10 L. Dead: chromium_export_check (553-575); unreachable ic_Financial mission (_generic_decisions.txt:1519-1534); totalexp write-only (B6).
5.11 L. Duplication: ~22 export loops (553-1140) and ~22 import loops (1349-1870); candidate for one parameterised loop.
5.12 L. Dedupe: first loop (553) has no pre-clear of ROOT.Export_List; safe only if no earlier caller leaves residue [INFERENCE].
5.13 L. trade_income (1168-1184) unfactored while resource/CG credit is factored; UI (core_debt, TAX_PIE) shows different number than paid.

## 6. Open questions
1. Is AI gated out of ic_financial_monthly_pulse? (5.2)
2. Is xExportTargetMonthly on exporter always equal to the importer's xImportTargetMonthly? Writers symmetric (2014, 2017); end-to-end price/shipping not traced.
3. Sign/magnitude of economic_modifier_war_reparations_exp vs modifier (5.4).
4. Can trade_credit_factor be left at 0 or below by flags or loans?
5. Where is CorruptionLevel clamped (5.9)?
6. Is CgElectronicsT0 intentionally absent (5.6)?
7. Are totalexp and total_expenses read anywhere (5.8)?
8. Does Trees for 0.35 load, and do PRC completion_rewards fire once (5.5)?
9. Not read: export loops 1785+ details; gdp_calculation_effect (IC_Econ_2024.txt).

## Summary
1. H: exporter credit × factor, importer debit raw (1207-1224 vs 1900-1909).
2. H: factor clamp inverts zero credit to full credit (1192-1206).
3. H: reparations receivers uncredited to IncomeTotal (1185-1187); payer possibly double-charged (402-419, 1916; IC_scripted_effects.txt:58) [INFERENCE].
4. H: AI trade one-sided if AI gated out [INFERENCE].
5. M: fiscal_cor_loss shows rate as money (CWIC_laws_l_english.yml:184).
6. M: custom_income permanent, PRC-only (PRC_50s_New.txt:1364,1380,4871).
7. M: corruption on gross credit (1249); CorruptionLevel unclamped (1243).
8. L: dead chromium_export_check, unreachable mission (_generic_decisions.txt:1519-1534), ~44 duplicate loops.
