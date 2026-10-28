# Audit: tax-tier ideas, `*_temp_X` policy families, zz_econ_laws, _economic, policy_focus_effects (tax and policy sections)

Scope: CWIC mod under `Cold War Iron Curtain/`, branch `Econ-fix`. Read-only. Overlaps with `Economy_System_Overview.md` and `audit/econ_policy*.md` are cross-referenced (S2, T3, T4, T5, T6, P8, P11) rather than repeated.

Verification note: findings marked [INFERENCE] rest on grep results with limited scope or on code shape, not on a full trace. Settled facts (`rubber`→Food, `tungsten`→Rare Earth) are not flagged.

## 1. Entry points

| Entry | Where | Caller frequency | Player vs AI |
|---|---|---|---|
| Tier-step effects `lower_tax_rate` / `increase_tax_rate` (upper family) | `policy_focus_effects.txt:3673`, `3820` | Many national_focus and decision calls | Both |
| `decrease_/increase_corporate_tax_rate` | `policy_focus_effects.txt:3965`, `4112` | National focus (`60s_FIN.txt:18,420`, `FRA_1950s.txt:2187,2228,3511,3999`, `INDIA_60s.txt:2679,2847-2848,2926,4344`, etc.), decisions (`US_HOUSE.txt` ~10402-27051), `_generic_decisions.txt:4274-4275` (with lower-middle) | Both |
| `decrease_/increase_lower_middle_tax_rate` | `policy_focus_effects.txt:4257`, `4404` | `_generic_decisions.txt:4274-4275`, `US_HOUSE.txt` [INFERENCE: increase callers not found in grep, possibly truncated] | Both |
| `decrease_/increase_lower_tax_rate` | `policy_focus_effects.txt:4549`, `4696` | `US_HOUSE.txt` decisions | Both |
| `startup_tax_loops` | `policy_focus_effects.txt:297-366`; callers `on_startup_defines.txt:1888-1928` (test-tag blocks for SOV/ENG/FRA/FRE, labelled "#Policy test") | Once per tag at startup [INFERENCE: debug-scoped; confirm] | Mostly players (tags listed) |
| `give_everyone_base_tax` | `IC_Econ_2024.txt:1504-1515` (labelled "Tax Debug") | No caller found in searched paths | n/a |
| `generate_tax_info` | `policy_focus_effects.txt:368-449`; called from `IC_Econ_2024.txt:1313` inside `gdp_calculation_effect` | Every GDP recalculation | Both (every country) |
| `Policy_Startup_Script_2025` | `policy_focus_effects.txt:7959`; called `IC_Econ_2024.txt:2184` inside a block gated by `set_country_flag = Expense_Policy_Setup_Check` | Once per flag [INFERENCE] | Both |
| `refresh_*_policy_rate` (10 effects) | `policy_focus_effects.txt:7507-7913`; callers `Indochina_Theater_Effects.txt:3480-3490`, `MLA_scripted_effects.txt:374-384` | Event-driven | Both |
| `get_actual_tax_rate_effect` | `policy_focus_effects.txt:4842-5000` ("#Needs Changed?" at 4841) | **No callers found** in common/events/interface/gfx | n/a (dead) |
| IMF path | `IMF_Decisions.txt:764-815` (steps upper tier, 790-815), `IMF_effects.txt:475-500` | Decision | AI and player |
| Slider GUI | `Finance_Tab.txt:299-308` (sliders), click handlers `Finance_Tab.txt:2135-2142`, right-click `Finance_Tab.txt:2344-2353` (corporate decrease at 2345, increase at 2353) | Player only | Player |

## 2. Data model

### 2.1 Tier ideas (the `*_temp_N` families)

Defined in `common/ideas/IC_Laws.txt`. Each family has tiers 1-19 only; no tier 0 exists in any family. Every tier block has `removal_cost = -1` and `allowed = { always = no # Added via focus }`.

| Family | Idea key pattern | Ideas range | Header comment | Modifier written | Other modifiers |
|---|---|---|---|---|---|
| Lower | `policy_taxrate_lower_temp_N` | 147-374 | (tier comments) | `tax_rate_lower_class` = 0.05×N | `stability_factor` 0.05→-0.13; `agricultural_complex_production_bonus` 0.1→-0.35 |
| Lower-middle | `policy_taxrate_lower_middle_temp_N` | 376-622 (header 375 `#Lower Middle Tax Rate`) | | `tax_rate_middle_class` = 0.05×N | `war_stability_factor` 0.15→-0.75; `cic_construction_boost_factor` 0.10→-0.26; commented `#weekly_casualties_war_support` lines |
| Corporate | `policy_taxrate_corporate_temp_N` | 624-852 (header 623 mislabelled `#Upper Middle Tax Rate`) | | `tax_rate_corporate` = 0.05×N | `war_support_factor` and `political_power_gain` 0.10→-0.26 |
| Upper | `policy_taxrate_temp_N` | 854-1072 (header 853 `#Upper Tax Rate`) | | `tax_rate_upper_class` = 0.05×N | `office_park_income_bonus` 0.4→-0.5; `production_speed_office_park_factor` -0.25→0.65 |

- The `corruption_idea0` block follows at about 1075 (comment-only modifier) [`IC_Laws.txt`].
- Modifier definitions: `common/modifier_definitions/influence_modifier_definitions.txt:45-66` (`tax_rate_corporate`, `tax_rate_upper_class`, `tax_rate_middle_class`, `tax_rate_lower_class`, all percentage).
- Labels for the four `tax_rate_*` modifiers: `localisation/english/CWIC_laws_l_english.yml:685-688`.

### 2.2 Country variables

| Variable | Meaning | Writers | Readers |
|---|---|---|---|
| `*_tax_level_value` (upper, corporate, lower_middle, lower) | Integer tier, -1..19 | `policy_focus_effects.txt` step effects (3681-3687 upper decrement; 3827-3831 upper increment; 3972-3979 corporate; 4264-4271 lower_middle; 4556-4563 lower) and `startup_tax_loops` (300-365) | Slider GUI via `Finance_Tab.txt:299-308` [INFERENCE: GUI reads level/slider] |
| `*_tax_slider_gui` | Display slider value, startup = rate×8+387, steps ±8 | Same as above | `Finance_Tab.txt:299-308` |
| `*_startup_rate` | Startup tier input | `on_startup_defines.txt:1888-1928` (values corporate 10/15/15/8/7, upper 8/15/15/12/10, lower_middle 5/12/9/6/5, lower 4/12/7/3/3); **mutated** by `multiply_variable` ×8 at `policy_focus_effects.txt:306,323,340,357` | `startup_tax_loops` |
| `upper_class_tax_rate`, `corporate_tax_rate`, `middle_class_tax_rate`, `lower_class_tax_rate` | Drift accumulator ±0.05 per step | Decrement effects only: `3687` (upper, lower_tax_rate), `3979` (corporate), `4271` (lower_middle), `4563` (lower). Increment of upper does not write (3827-3831) | **No readers found** in common/events/interface/gfx grep [INFERENCE] |
| `laffer_weighted_average_tax_rate` | Mean of the four modifier values | `generate_tax_info` 368-449; divides by 4 at 381-382 | Laffer UI, `Laffer_Graph_Financial_Tab_Update` [INFERENCE] |
| `effective_tax_rate` | Post-avoidance rate | `generate_tax_info` 386-415 (includes `CWIC_bm_tax_leak_mult`) | `IC_tax_avoidance_line.txt`, `IC_Econ_2024.txt:1341-1358` |
| `pop_*class_tax_rate`, `*_bonus` | Per-class tax burden for pops | `IC_Econ_2024.txt:1341-1358` (reads `modifier@tax_rate_{lower,middle,upper,corporate}_class` × `effective_tax_rate`) | Pop economy; collection at `IC_Econ_2024.txt:2649-2699` and `ui_*` copies |

### 2.3 Other `*_temp_X` families (policy-level, not tax)

- `military_temp_0..20` `IC_Policies.txt:289-529`; `navy_temp_0..20` 542-802; `air_temp_0..6` 816-897+ (tail not read).
- `food`: `IC_Policies.txt:1477-1727` (`food_consumption_need`).
- `_economic.txt`: `saga_temp_0..4a` 412-457; `union_temp_0..7` 473-556; `media_temp_0..3a` 575-620; `women_temp_0` begins 636 (rest unread). Modifier bodies not read.
- Clear/refresh: `refresh_{army,navy,air,strategic_forces,space,healthcare,welfare,education,services,policing}_policy_rate` at `policy_focus_effects.txt:7507-7913`, each calling `clear_all_*_ideas` (7527 onward, removing `_temp_20` down to `_temp_0`). `clear_all_cpi_ideas` (7933) uses `policy_cpi_temp_*`; `refresh_policing_policy_rate` (7913) maps to it.
- Swap effects `swap_*_ideas` at `policy_focus_effects.txt:1, 45, 89, 149, 193, 245` (`swap_lgbt_ideas` uses `policy_saga_temp`, 193).

### 2.4 Localisation

- Corporate: `CWIC_laws_l_english.yml:219-238` (`_0`..`_19`, all present).
- Upper-middle loc keys: `CWIC_laws_l_french.yml:193-212` define `policy_taxrate_upper_middle_temp_0..19`. No idea uses this key; the actual upper family is `policy_taxrate_temp_N` (French `policy_taxrate_temp_19` at 192).
- Lower-middle loc keys: `CWIC_laws_l_japanese.yml:193-212` (`_0`..`_19`).
- English loc for lower and lower-middle families and for upper (`policy_taxrate_temp_N`): not confirmed. The English grep reported ">20 matches" and capped output, so absence is [INFERENCE] until grepped on that file alone.

## 3. Formulas, step by step

### 3.1 Startup (`startup_tax_loops`, `policy_focus_effects.txt:297-366`)
1. For each class, set `*_tax_level_value = *_startup_rate` (corporate 300-314, upper 317-331, lower_middle 334-348, lower 351-365).
2. Set `*_tax_slider_gui = 0`.
3. `multiply_variable` `*_startup_rate` by 8 (306, 323, 340, 357). This mutates the startup input.
4. Set slider to `*_startup_rate` and add 387.
5. `meta_effect` text-substitutes the family name (`policy_taxrate_{corporate|temp_|lower_middle|lower}_temp_[IDEA_TOKEN]`) and adds the idea with the token equal to the rate.

Net effect: a rate of 0 adds the undefined `_temp_0` for the upper or lower family. Reachability is [INFERENCE], since listed startup values are all ≥3. Re-invoking the effect multiplies the startup rate again and re-adds ideas without removing old ones.

### 3.2 Step effects (upper family example, `lower_tax_rate` 3673-3819)
1. Guard `NOT = { has_idea = policy_taxrate_temp_1 }` (3675-3687 region): if true, decrement `upper_tax_slider_gui` by 8, `upper_tax_level_value` by 1, `upper_class_tax_rate` by 0.05.
2. Chain: for each N, if has tier N+1 (or N), add tier N-1 and remove tier N (the same pattern repeats for the other three families).
3. Final `else` at 3816-3817: `add_political_power = 50`.

`increase_tax_rate` (3820-3963) mirrors this: guard `NOT has temp_19` (3822 region), slider +8, level +1 (3827-3831), no `upper_class_tax_rate` write, `else` at 3960-3961 gives `add_political_power = 50`.

The same `else` → `add_political_power = 50` pattern appears in all eight step effects: 4109, 4253, 4401, 4545, 4693, 4837 (plus 3817, 3961). Verified by grep.

### 3.3 Generate tax info (`policy_focus_effects.txt:368-449`)
1. Read four modifiers (`tax_rate_upper_class`, `tax_rate_middle_class`, `tax_rate_corporate`, `tax_rate_lower_class`) and sum.
2. Divide by 4 (381-382) → `laffer_weighted_average_tax_rate`.
3. Lines 386-415 compute `effective_tax_rate` with tax avoidance and `CWIC_bm_tax_leak_mult`. Full formula not reproduced here; overlaps with S2 (overview).
4. `IC_Econ_2024.txt:1341-1358` multiplies each class modifier by `effective_tax_rate` into `pop_*class_tax_rate` and `*_bonus`.

## 4. Interactions

- **Treasury (`income_effect`, IncomeGenerator.txt)**: consumes pop tax collections from `IC_Econ_2024.txt:2649-2699`. Tax rates depend on `generate_tax_info` through `effective_tax_rate` (see 3.3). Not re-verified here.
- **GDP (`gdp_calculation_effect`, IC_Econ_2024.txt ~1308)**: calls `generate_tax_info` at 1313; comment at 1339-1340; pop tax at 1341-1358. The `actual_tax_rate_adjusted` block is commented out at 1330-1333 (per overview).
- **Trade**: no direct tie found in this slice [INFERENCE].
- **Policies/laws**: the tier ideas are the only writers of tax modifiers besides the per-country writers listed below. Tax-rate modifier writers: `bop/DDR.txt:77,97`, `bop/INO.txt:30,55`, `bop/WGR.txt:28,48,73`, `dynamic_modifiers/CWIC_Nepal_Dynamic_Modifiers.txt:14-15`, `ideas/MNC_Effects.txt:257-312`, `ideas/JAP_Ideas.txt` (upper and middle stacks 9-240), `ideas/USA_Congress_Acts.txt:152-153`, `ideas/New_Ideologies_Ideas.txt:12627`, `ideas/british_focus.txt:53`, `ideas/brazil.txt:262-264` (comment: `modifier_corporate_tax_bonus` undefined).
- **Decisions and events**: national_focus about 48 files (listed in §1); `US_HOUSE.txt` heaviest user; `Malaysia.txt:277`; `IMF_Decisions.txt`. Commented-out callers: `StartingPoliciesBogosort.txt:99-106`, `brazil.txt:142`.
- **UI**: slider GUI `Finance_Tab.txt:299-310`; click and right-click at 2135-2142 and 2344-2353. The left-click `Taxes_Slider_Left/Right` at 2322-2330 only sets `Recent_Tax_Law_Change` [INFERENCE: not fully read].

## 5. Problems

| # | Sev | Location | Problem |
|---|---|---|---|
| 1 | **H** | `policy_focus_effects.txt:3816-3817`, `3960-3961`, `4108-4109`, `4252-4253`, `4400-4401`, `4544-4545`, `4692-4693`, `4836-4837` | Floor/ceiling `else` grants `add_political_power = 50` with no state change. When the player is already at the floor (tier 1 for decrement) or the ceiling (tier 19 for increment), each call grants 50 PP. Reachability from UI and any guard in the calling focus or decision are [INFERENCE]. Rate H if reachable, M otherwise. |
| 2 | **H** | `policy_focus_effects.txt:300-314, 317-331, 334-348, 351-365` | `startup_tax_loops` can add undefined `policy_taxrate_*_temp_0` when `*_startup_rate` is 0. Also multiplies `*_startup_rate` in place (306, 323, 340, 357), so a second call compounds ×8 and re-adds ideas without removing old ones. Reachability [INFERENCE]: current callers pass nonzero values, and re-entry was not traced. |
| 3 | **M** | `policy_focus_effects.txt:3687`, `3979`, `4271`, `4563` | Drift accumulators `upper_class_tax_rate`, `corporate_tax_rate`, `middle_class_tax_rate`, `lower_class_tax_rate` are written only on decrement and never read in the grep scope. Dead writes or a missed reader [INFERENCE]. The upper increment (3827-3831) does not write `upper_class_tax_rate`, so the pair is asymmetric. (Overlaps T3 in the overview; this slice adds the other three.) |
| 4 | **M** | `policy_focus_effects.txt:4842-5000` | `get_actual_tax_rate_effect` has no callers in the searched paths; labelled "#Needs Changed?" at 4841. Dead code [INFERENCE: grep scope]. Its body still references `policy_taxrate_temp_1`. |
| 5 | **M** | `US_HOUSE.txt:21942-21943`, `21961-21962`, `27029-27030`, `27047-27048` | Same `decrease_/increase_corporate_tax_rate` effect called twice in one block: double step per event. Intent unverified. |
| 6 | **M** | `localisation/french/CWIC_laws_l_french.yml:193-212` | Loc keys `policy_taxrate_upper_middle_temp_0..19` have no idea matching them. The upper family is `policy_taxrate_temp_N`. Orphaned keys, or a mislabelled family. |
| 7 | **M** | `localisation/english/CWIC_laws_l_english.yml` | English loc for lower, lower-middle, and upper tiers not confirmed (grep cap reached). If absent, tooltips show raw keys [INFERENCE]. |
| 8 | **M** | `IC_Laws.txt:854-1072` (upper family) | Balance flag: at the top tier, `office_park_income_bonus` is -0.5 and `production_speed_office_park_factor` is +0.65, so high upper-class tax raises a production speed. Sign direction should be checked [INFERENCE]. |
| 9 | **M** | `IC_Laws.txt` (corporate 624-852, lower-middle 376-622) | `war_stability_factor` (-0.75 at 95%) and `political_power_gain` (-0.26 at 95%) penalise high taxes sharply. Trade-off looks intentional; magnitude is a balance question [INFERENCE]. |
| 10 | **L** | `IC_Laws.txt` lower family, tier 9 (comment near the tier-9 block, value 0.45) | Comment "#40% Income" on a 45% tier. Mislabel. |
| 11 | **L** | `IC_Laws.txt:623` | Corporate block header `#Upper Middle Tax Rate` is wrong. |
| 12 | **L** | `IC_Laws.txt` lower-middle block | Commented `#weekly_casualties_war_support` lines (dead comments). |
| 13 | **L** | `policy_focus_effects.txt:5224` | `decrease_minority_rigts` misspelling. |
| 14 | **L** | `policy_focus_effects.txt:6073`, `6167` | Duplicate `decrease_DOM_Dominican_Nationalist_Fervor` (existing T4). |
| 15 | **L** | `IC_Econ_2024.txt:1504-1515` | `give_everyone_base_tax` labelled "Tax Debug" adds `policy_taxrate_lower_temp_1` to every country; no caller found. Debug residue (overlaps P11). |
| 16 | **L** | `brazil.txt:262-264` | Comment says `modifier_corporate_tax_bonus` is undefined. |
| 17 | **L** | `synchronized_dynamic_tokens/tokens.txt:815-819`, `1102-1106` | Duplicate tax tokens (existing overview finding). |
| 18 | **L** | `on_startup_defines.txt:1888-1928` | Startup values use tiers 3-15 in test blocks; likely debug scope, not a bug on its own. |

Items from the existing overview that this slice confirms and does not repeat in detail: S2 (tax avoidance no-op), T3 (lower_tax_rate drift), T4 (duplicate DOM effect), T5 (healthcare +50 PP), T6 (dead Laffer cluster), P8/P2 (tax ordering), P11 (debug residue).

### AI gap notes
- `startup_tax_loops` covers SOV, ENG, FRA, FRE and the `every_country` path (`on_startup_defines.txt:1929+`, not read). AI tier movement happens only through focus and decision effects [INFERENCE].
- `StartingPoliciesBogosort.txt:99-106` tax calls are commented out, so the bogosort start path sets no tax tiers.

## 6. Open questions

1. Is `get_actual_tax_rate_effect` called from any file outside the searched paths (GUI `.gui`, `.csv`, `history/`)?
2. Does the floor/ceiling PP `else` in the eight step effects have a guard in its calling focus or decision that prevents repeat clicks (Finding 1)?
3. Is `startup_tax_loops` ever called with `*_startup_rate` = 0, or twice for the same country (Finding 2)?
4. Who reads `upper_class_tax_rate`, `corporate_tax_rate`, `middle_class_tax_rate`, `lower_class_tax_rate` (Finding 3)? Check GUI `.gui` files and `Laffer_Graph_Financial_Tab_Update`.
5. Full English loc coverage for lower, lower-middle, and upper tiers (Finding 7): grep the English file alone, with a higher match cap.
6. Unread: `zz_econ_laws.txt`; `_economic.txt` modifier bodies (saga/union/media/women); `IC_Policies.txt` air tail beyond 897 and healthcare/welfare/cpi/women/religion/minorities families; `policy_focus_effects.txt` 5000-7506 in full; enclosing effect names for `IC_Econ_2024.txt:1313` and `:2184`.
7. Whether the `US_HOUSE.txt` double calls (Finding 5) are intentional two-step decisions.
8. Whether `increase_lower_middle_tax_rate` has callers (grep for callers was capped).
