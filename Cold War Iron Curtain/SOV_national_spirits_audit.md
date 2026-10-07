# USSR National Spirit Audit

Goal: the USSR should show **3–4 national spirits at any point in the game**.

Method: every `add_ideas` / `add_timed_idea` / `swap_ideas` / `remove_ideas` in the Soviet focus trees, events,
decisions, scripted effects and history was traced. Grants that target another country (`CZE = { add_ideas = … }`,
`every_subject_country`, etc.) were excluded. Only `country`-category ideas count, because those are the ones in the
spirits bar. Laws, `hidden_ideas` and the policy sliders don't count.

---

## 1. Cleanup already done

`common/ideas/soviet.txt`: **71 spirits deleted** (958 lines). Nothing in `common/`, `events/`, `history/` or
`interface/` referenced any of them. Brace balance was checked after the edit, and the file is still CRLF.

```
antiquated_infrastructure_2 test_idea_1 test_idea_3 SOV_Increased_Computer_Production sov_suspended_5
sov_suspended_5_plus temporary_soviet_discipline KGB_idea small_package important_package huge_package
Beria_shadow Malenkov_figurehead Politicized_Army_4 sov_demilitarize_1..5 sov_labor_short sov_labor_short_1
severe_repression traditional_farms kainiji_dam industry_rearrangement traditional_healthcare
SOV_fortification_focus Autocrat_Shah Return_to_the_Farms_and_Fields one_form_of_government
soviet_research_collaboration SOV_military_production_initiatiive_idea SOV_great_soviet_engineering
khrushchev_standards cuban_missles higher_political_payments farmers_first increase_the_population
helsinki_treaty comumnist_world revise_the_economy reduce_soviet_army end_of_the_soviet_era
make_the_russian_federation restore_the_glory keep_the_union revise_the_system kgb_coup immortal_nation
kgb_leading_union rule_with_iron_fist stabilize_the_union undo_the_damage reorganize_farms internal_economy
fix_the_inefficiencies black_sea_canal constructing_black_Sea_canal SOV_Korenizatsiya SOV_Aviation_Corps
ground_froces_expenditure improved_training idea_mobile_warfare mixed_warfare armoured_superiority big_seven
fulda_gap_tactics mass_armor armored_invasion yyyyyyyyyyyyyyy destalinization
```

**Kept on purpose:**
- **Designer ideas** (Uralvagonzavod, MiG/Ilyushin/Tupolev bureaus, GAZ, Tula, Grabin, Nevskoye, Stalingrad Tractor,
  Leningrad Polytechnic). Nothing scripts them, but the player picks them from the designer slots.
- **Orphans: removed but never granted.** `sov_policy_target`, `sov_eco_infla` and `sov_ex_meat_production` are
  removed by the 8th Five-Year Plan and checked by `IC_Industrial_Pulse`, but nothing ever adds them. They look like
  missing starting "plan problems", not dead content, so they need a design decision (see §5).
- `legacy_of_the_occupation_kor` is only removed by KOR history. It isn't Soviet; it's harmless and left alone.
- Their localisation and GFX entries were not touched. Stale loc keys are harmless.

---

## 2. Who rules when (succession graph as coded)

```
1949 START ── Stalin (SOV_Stalin + 50s Military/Industry shared trees)
   │  branch: Troika (SOV_Troika)              OR   Advisory body (SOV_Stalin_Lives)
   │
   └─ 20th Congress focus (1956)
        ├─ Pospelov commission done ──► Khrushchev (SOV_Khruschev)
        │     ├─ +490 days soviet_leader_change.5 ──► Bulganin (Anti-Party Group wins)
        │     └─ soviet_leader_change.2 (1964) ──► Brezhnev (SOV_Brezhnevite + FP + 5YP 8–11 + Mil)
        │                                       └─► or Khrushchev Extended ──► Mikoyan (1971)
        ├─ Advisory body done ──► Kaganovich (SOV_Kaganovich)
        │     └─ soviet_leader_change.9 ──► Ustinov  |  Shelepin (tree SOV_Shelepin DOES NOT EXIST)
        └─ else ──► Beria–Malenkov (SOV_Beria_Malenkov)
Brezhnev ── 1982.3 soviet_leader_change.3/.4 ──► Andropov ── 1984 Chernenko ── 1985 Gorbachev/Romanov (event only, no tree)
Alt: SOV_WW3_1950s (war path)

1980 START ── Brezhnev, SOV_Brezhnevite tree
```

Dead or unreachable:
- `soviet_leader_change.8` (Molotov) is never fired.
- `SOV_Ogarkov`, `SOV_Beria` (Beria_New) and `SOV_Brezhev_live_more` (except via `brezhnev_last_year.1`) are only
  reachable from debug decisions.
- Molotov, Mikoyan, Khrushchev-Extended, Beria_New and Brezhnev_live grant **no** spirits at all.

---

## 3. Spirits per leader: start → end of rule

"End" assumes every focus is taken, so it's an upper bound for exclusive branches. **Timed** spirits come on top while
they last. Transient tier steps (`_1 → _2 → _3`) are counted once.

| Leader | Start | Permanent adds | Timed adds | **End** |
|---|---:|---:|---:|---:|
| Stalin (Troika branch) | 7 | 5 | 8 | **7** |
| Stalin (Advisory branch) | 7 | 0 | 6 | **4** |
| Khrushchev | 7 | 4 | 3 | **10** |
| Beria–Malenkov | 7 | 2 | 4 | **9** |
| Kaganovich | 4 | 8 | 15 | **12** |
| Bulganin | 10 | 9 | 0 | **18** |
| Ustinov | 12 | 11 | 2 | **19** |
| Brezhnev (1964) | 10 | 10 | **62** | **20** |
| Andropov | 20 | 12 | 2 | **32** |
| WW3 1950s | 7 | 4 | 1 | **10** |
| **Brezhnev (1980 bookmark)** | **7** ← all the 1949 spirits | | | |

### Stalin (1949 start, 7)
`Suchyi_voyny`, `gossnab`, `antiquated_infrastructure`, `victor_of_the_great_patriotic_war`, `SOV_MGB`,
`SOV_Abortion_Criminalized`, `defcon_system_5`

- **Troika branch.** Removes gossnab, MGB and Abortion. Runs a long chain
  `SOV_MGB → MGB_ongoing_Purge → MGBMVD → MVD_IN_CONTROL → KGB → KGB_Improved` plus about 10 one-step faction spirits
  (Malenkov_Allies, Meshik_Allied, Dekanozov_Allied, Merkulov_in_Power…).
  End: `Beria_State_of_Emergency, Cautious_Destalinization, KGB_Improved, Khrushchev_Exclusion_From_Presidium,
  Khrushchev_Politiburo, victor_of_GPW, defcon`.
- **Advisory branch.** Only removes `Suchyi_voyny`.
  End: `MGB, Abortion_Criminalized, victor_of_GPW, defcon`.
- Timed: AK-47 / T-54 / MiG-15 / Submarine production-cost spirits, `soviet_economic_boost`, `Pavlovian_Session`,
  `State_Atheism`, `Cancelled_Stalin_Projects`.

### Khrushchev (7 → 10)
Adds `Anti_Party_Group_Coup`, `Ukrainian_Academy_of_sciences`, `nuclear_powered_icebreakers`,
`soviet_free_specialized_education`. Timed: `five_year_plan`, `invested_in_housing`, `Currency_Devaluation`.
**Never removes anything**, so all five Troika political spirits are still there in 1964.

### Beria–Malenkov (7 → 9)
Adds `Politicized_Army_1→2→3` and `pacific_naval_treaty_adherent`.
The `*_Champion_*`, `Joint_Planning_Commission`, `military_spending_limitation` and `softened_soviet_loans` spirits
go to the satellites, not the USSR.

### Kaganovich (4 → 12)
Has six five-tier chains, all permanent: `self_management_doctrine_1–5`, `soviet_expanded_consumer_goods_1–5`,
`soviet_planned_komsomol_reform_1–5`, `SOV_experienced_army_1–3`, `investment_in_cybernetics_1–3`, `new_algorithms`.
Also `Kaganovichism_successful/cemented`, `Fragile_Kaganovich_Rule`, `EGSVT_Network_early`,
`enlarged_collective_farms`, `reformed_komsomol`, plus 15 timed.
Bug: `soviet_planned_komsomol_reform_1` stays alongside `reformed_komsomol`.

### Bulganin (10 → 18)
Adds `Chairman_Molotov`, `Dep_Chairman_Kaganovich`, `Stabiilised_Politiburo`, `Stalinist_Cult`,
`dekhrushchevization`, `revisionism_defeated`, and all three of `sov_stalinist_agriculture`, `_inov_good` and
`_inov_fail`. The last three are meant to be exclusive outcomes but can stack.

### Ustinov (12 → 19)
Removes MGB, Abortion and the Kaganovichism spirits. Adds the EGSVT chain, but **Akademset and Military both stay**.
Both `Early_Automation_*` spirits stay too, and they're near-identical. Also adds `Experimental_Cybernetics_in_the_Red_Army`,
`Cybernetic_Constitution`, `Partial_Prohibition`, `Cultural_Renaissance`, `computerized_crop_management`,
`experienced_army_5` and `KGB_Improved`.

### Brezhnev (10 → 20, with up to 62 timed on top)
- **Main tree:** `Nomenklatura1→5`, `black_market1–5` (cycled), `ideological_fanaticism_focus`, `marxist_escuelas`,
  `socialist_realism`, `public_media` **and** `state_media` (contradictory, both permanent), plus 14 timed
  (purges, repression, propaganda, gulag, hygiene, capitalism, centralization…).
- **Military shared tree:** `VDV_Expansion`, `Vozdushno_desantnye_voyska_1/_2` stay permanently, plus 8 timed equipment
  spirits.
- **Five-Year Plans 8–11:** about 45 timed spirits (`sov_*`, `economic_growth`, `high_quotas`…). **This is the main
  source of bloat.** Eleven of them have no modifier: `sov_agr_*` and `sov_crop_rotation` are just flags that
  `IC_Industrial_Pulse` reads.

### Andropov (20 → 32)
Adds `era_of_stagnation`, `growing_alcoholism`, `andropov_diplomacy`, the discipline chain (the last tier stays), the
anti-corruption chain, the Economic Department, the Special Commission, and **both tiers** of the Gorbachev team and
the Romanov team (`_Market` + `_Decree_Market`, `_Private` + `_Private_Decree`), because the lower tier is never
removed.

---

## 4. Duplicates, overlaps and useless spirits

### 4a. Identical effects (same modifier block, different name)
| Group | Effect |
|---|---|
| `SOV_MGBMVD` = `SOV_MGB_Army_Joint_IAC` | +5% stab, +5% PP, … |
| `SOV_Stalin_Institute` = `SOV_Kaganovich_Institute` = `SOV_studying_western_academics` = `best_of_both_world_hardware` | +0.5% research |
| `SOV_Discipline_strengthening_initiative` = `SOV_Campaign_on_Strengthening_Labour_Discipline` = `SOV_Cybernetic_Constitution` | −5% stability |
| `SOV_Anti_corruption_campaign_in_MVD` = `SOV_Mass_reshuffles_and_dismissals…` | −10% PP |
| `Soviet_Greatworks` = `SOV_computerized_crop_management` | +5% consumer goods |
| `private_plots` = `sov_long_term_agri` = `sov_rular_attr` | +10% agri complex speed |
| `education_invest` = `sov_tech_comp` = `sov_compete_int_market` = `sov_reward_private_dis` | +1% research |
| `high_skill_engineers` = `workers_culture` | +10% construction |
| `sov_enc_priv_busn` = `sov_tran_power_to_loc` | +10% civ-complex speed |
| `sov_subs_based_production` = `sov_more_women_prod` | +5% eff gain / +5% max eff |
| `sov_eff_labor_use` = `sov_computers_to_companies` | +10% eff gain / +5% max eff |
| `better_consumer_goods_management` = `overhauled_maintenance` | −1% consumer goods |

### 4b. The same spirit granted by several trees (the second grant does nothing)
- `five_year_plan`: Khrushchev, Kaganovich, Ustinov, Ogarkov
- `invested_in_housing`, `soviet_free_specialized_education`: Khrushchev and Kaganovich
- `economic_growth`: 5YP 8, 9 and 11
- `medical_increase`: 5YP 8 and 11
- `sov_agr_bur_reduce`: 5YP 9 and 11
- `sov_agr_subs`, `sov_agr_mach_mod`: decision and 5YP
- `SOV_KGB_Improved`: Troika and Ustinov

### 4c. Tier chains that leave the lower tier behind (bugs)
- `soviet_planned_komsomol_reform_1` + `reformed_komsomol` (Kaganovich)
- `EGSVT_Network_Akademset` + `EGSVT_Network_Military` (Ustinov). These should be an exclusive choice.
- `SOV_Early_Automation_of_the_Civilian_Economy` + `…_Heavy_Industry` (Ustinov, about 95% identical)
- `sov_stalinist_agriculture` + `_inov_good` + `_inov_fail` (Bulganin)
- `SOV_Gorbachev_led_reforms_team_Private` + `_Private_Decree`; `SOV_Romanov_…_Market` + `_Decree_Market` (Andropov)
- `public_media` + `state_media` (Brezhnev, opposite policies)
- `Vozdushno_desantnye_voyska_1` + `_2` + `VDV_Expansion` + `SF_Cap_Bonus` (Brezhnev Mil)

### 4d. Useless
- **No modifier at all:** `investment_in_cybernetics`, `soviet_planned_komsomol_reform` (tier-0 stubs),
  `Vozdushno_desantnye_voyska`, `VDV_BMP`, and the `sov_agr_*` / `sov_crop_rotation` / `sov_sensible_meat` farm flags.
  Turn the flags into country flags, or move them to `hidden_ideas`.
- **Effects too small to matter (≤1%):** `Experimental_mobile_concrete_plants` (+0.5% construction),
  `invested_in_housing` (+0.1% monthly pop), `studying_western_computers` (+0.25% research), `new_algorithms`,
  `standardised_concrete_standards`, `SOV_New_Soviet_Man`, the four +0.5% institutes, `overhauled_maintenance`.
- **Equipment-cost spirits:** AK-47, T-54, MiG-15, Submarines, AK-74, BMP ×3, ZSU, ATGM, Recon helo, Weapon_Exports.
  These are a one-off "make X cheaper" reward, so they'd be better as `add_tech_bonus` or MIO effects than as a spirit
  slot.
- **Stale in the 1980 bookmark:** the 1949 history block applies to every bookmark. A 1980 USSR therefore starts with
  `Suchyi_voyny` (post-war dry law), `SOV_MGB` (abolished 1954), `SOV_Abortion_Criminalized` (repealed 1955), `gossnab`
  and `antiquated_infrastructure`.
- **Kept forever with no exit:** `victor_of_the_great_patriotic_war` (no tree removes it except WW3) and
  `SOV_Beria_State_of_Emergency`, `SOV_Cautious_Destalinization` and `SOV_Khrushchev_Exclusion_From_Presidium`
  (carried from 1953 to Andropov).

---

## 5. Target: 4 fixed slots

Each slot is **one** idea at a time. Focuses upgrade it with `swap_ideas`. A new leader swaps it to that leader's
version. Nothing is ever added without either replacing a slot or being timed and short.

| Slot | Purpose | How it evolves |
|---|---|---|
| **1. Political line** | The leader's regime | One spirit per leader. Its tiers replace the leader's own political spirits. |
| **2. Economy / Five-Year Plan** | gossnab → FYP 5…11 | One "Nth Five-Year Plan" idea. Plan focuses tier it up, or set variables a dynamic modifier reads (the 5YP code already uses `sov_8th_5yp_progress` / `farm_output_modif`). |
| **3. Security & society** | MGB → MVD → KGB, media, repression, anti-corruption | Uses the existing MGB→KGB chain as the backbone. |
| **4. Armed forces** | victor_of_GPW → doctrine | Uses the existing `SOV_experienced_army_1–5` / `Politicized_Army_1–3` chains. Equipment spirits become one-shot rewards. |

`defcon_system_5` is a global mechanic shown for every country. Either hide it (the DEFCON GUI already shows the level)
or accept it as a fifth, shared spirit.

### Per-leader mapping (what each slot holds at the start → end of rule)

| Leader | 1. Political | 2. Economy | 3. Security | 4. Military |
|---|---|---|---|---|
| **Stalin** start | `Suchyi_voyny` → rename "Late Stalinism" (merge Abortion_Criminalized into it) | `gossnab` (+ merge antiquated_infrastructure) | `SOV_MGB` | `victor_of_the_great_patriotic_war` |
| Stalin end, Troika | Beria_State_of_Emergency / Cautious_Destalinization / Khrushchev_* collapsed into **one** "Collective Leadership" tier | `soviet_economic_boost` (5th FYP) | `SOV_KGB_Improved` (end of the MGB chain) | victor_of_GPW (AK/T-54/MiG become one-shots) |
| Stalin end, Advisory | "Late Stalinism" | gossnab | SOV_MGB | victor_of_GPW |
| **Khrushchev** | "Thaw": `Anti_Party_Group_Coup` becomes a tier of it, not a separate spirit | 6th/7th FYP (`five_year_plan`; Academy/icebreakers/education folded in) | KGB | victor_of_GPW → reformed army |
| **Beria–Malenkov** | Beria_State_of_Emergency line | FYP (Water Commissions folded in) | KGB | `Politicized_Army_1–3` |
| **Kaganovich** | `Fragile_Kaganovich_Rule → Kaganovichism_successful → _cemented` | One chain: `self_management_doctrine` OR `expanded_consumer_goods` (pick one; merge the other) | MGB → `reformed_komsomol` chain | `SOV_experienced_army_1–3` |
| **Bulganin** | `SOV_Stalinist_Cult` with tiers: Khrushchevites purge → revisionism_defeated → dekhrushchevization (Molotov/Kaganovich deputies folded in) | `sov_stalinist_agriculture` (good/fail as exclusive swap) | KGB | inherited |
| **Ustinov** | `SOV_Cybernetic_Constitution` / Cultural Renaissance | EGSVT chain, ending in **either** Akademset **or** Military; the Automation spirits fold in | KGB_Improved / Partial_Prohibition | `experienced_army_4–5` + Cybernetics_in_Red_Army |
| **Brezhnev** | `Nomenklatura1–5` | 8th→11th FYP: **one** idea instead of about 45 timed `sov_*` | `state_media` **or** `public_media` + black_market tiers | VDV chain (collapse VDV ×4 into one) |
| **Brezhnev 1980 start** | Nomenklatura4 | 11th FYP | KGB_Improved + state_media | VDV / victor removed |
| **Andropov** | `era_of_stagnation` → discipline chain (lower tiers removed) | Special Commission → Gorbachev **or** Romanov team (top tier only) | Anti-corruption chain | inherited |
| **WW3** | `great_liberation_war_1–3` | `Union_of_Laborer` | `ANTI_MISINFORMATION_1` | `the_last_war` |

### Decisions (approved) and what was implemented

Brezhnev-era files are **out of scope** (pending rework): `SOV_Brezhnev`, `SOV_Brezhnev_Mil`, `SOV_Mid_Foriegn_Policy`,
`Sov_Five_Year_Plan_Eight..Eleven`, `SOV_5_year_plans`. Also left alone: the debug-only trees (Ogarkov, Beria_New).

1. **DEFCON hidden.** `common/ideas/Defcon.txt` was moved to `hidden_ideas`. Its modifiers still apply, and the WMD tab still
   shows the level.
2. **Economy slot = one dynamic modifier.** `SOV_state_of_the_union` ("State of the Union",
   `common/dynamic_modifiers/SOV_state_of_the_union.txt`). 112 former spirits are folded into it with their exact
   modifiers, held in `SOV_sotu_*` variables.
   - Focus tooltips show the original spirit via `show_ideas_tooltip`. The idea definitions stay as tooltip data.
   - Timed spirits keep their original duration through hidden events `SOV_sotu.1–29`
     (`events/SOV_state_of_the_union.txt`). Refreshing a timed spirit moves its end date.
   - Tier chains (komsomol, consumer goods, self-management, cybernetics, EGSVT, automation, anti-alcohol, reform teams…)
     keep only their highest tier. Adding a tier removes the others, and the add is skipped if a higher tier is already
     active. This fixes the stacked-tier bugs from §4c.
   - `research_bonus` parts (Andropov reform teams, labour-collective law, Special Commission) become a one-off
     `add_tech_bonus` (0.5, 1 use) per category.
3. **Political / security / military slots.** Every grant goes through `SOV_clear_<slot>_spirit`, defined in
   `common/scripted_effects/SOV_spirit_slots.txt` along with all generated add/remove effects. A slot can therefore never
   hold two spirits. `victor_of_the_great_patriotic_war` is now replaced by the first army reform (NCO / Politicized Army
   / experienced army).
4. **Equipment-cost spirits become research bonuses.** AK-47, T-54, MiG-15 and Submarines now give `add_tech_bonus`
   (0.5, 2 uses) in infantry_weapons, armor, jet_technology and submarine_tech.
5. **1980 bookmark.** The `1980.1.1` history block removes the 1949 folds (gossnab, antiquated infrastructure, Suchyi
   voyny, abortion ban) and replaces MGB with `SOV_KGB_Improved`.

Orphans `sov_policy_target`, `sov_eco_infla` and `sov_ex_meat_production` were left for the Brezhnev rework.

**Result:** at most 4 entries (State of the Union + political + security + military) for Stalin, Khrushchev,
Kaganovich, Beria–Malenkov, Bulganin, Ustinov and WW3. Known exceptions:
- `pacific_naval_treaty_adherent` (Beria–Malenkov). It belongs to the multi-country naval-treaty system in
  `IC_Influence.txt`.
- `rhine_in_seven_days` (WW3, 7 days, targeted modifier).
- Andropov still inherits whatever the Brezhnev trees leave behind until those are reworked.

**Regenerating:** edit `_tools/spirit_slots/slots.py`, then run `python _tools/spirit_slots/gen.py .`. This rebuilds
the dynamic modifier, slot effects, expiry events and loc. Call sites in focus and event files are edited by hand.

---

## Appendix: every spirit granted to the USSR

"perm" means added with `add_ideas`; "timed" means `add_timed_idea`. The leader is blank when the grant sits in a
shared or unreachable file.

| Spirit | Leader(s) | Type | Effects | Granted in |
|---|---|---|---|---|
| `SOV_Amendments_to_the_law_on_labour_collectives` | Andropov | perm | production_speed_buildings_factor 0.02, industrial_capacity_factory 0.02, industrial_capacity_dockyard 0.02, production_factory_max_efficiency_factor 0.02, production_factory_efficiency_gain_factor 0.05, line_change_production_efficiency_factor 0.05, research_bonus:manufacturing 0.02, research_bonus:computing_tech 0.02 | SOV_Andropov_Events |
| `SOV_Anti_corruption_campaign_in_MVD` | Andropov | perm | political_power_factor -0.1 | SOV_Andropov |
| `SOV_Campaign_on_Strengthening_Labour_Discipline` | Andropov | perm | stability_factor -0.05 | SOV_Andropov |
| `SOV_Campaign_on_Strengthening_Labour_Discipline_Improved` | Andropov | perm | stability_factor -0.1 | SOV_Andropov |
| `SOV_Campaign_on_Strengthening_Labour_Discipline_Improved_again` | Andropov | perm | stability_factor -0.1, political_power_gain -0.05 | SOV_Andropov |
| `SOV_Discipline_strengthening_initiative` | Andropov | perm | stability_factor -0.05 | SOV_Andropov |
| `SOV_Economic_Department_of_the_Central_Committee_of_the_CPSU` | Andropov | perm | political_power_factor 0.05, consumer_goods_factor -0.01, industrial_concern_cost_factor -0.2 | SOV_Andropov |
| `SOV_Gorbachev_led_reforms_team` | Andropov | perm | production_speed_office_park_factor 0.02, production_speed_agri_industrial_complex_factor 0.02 | SOV_Andropov_Events |
| `SOV_Gorbachev_led_reforms_team_Private` | Andropov | perm | production_speed_office_park_factor 0.02, production_speed_agri_industrial_complex_factor 0.02, research_bonus:management 0.04, research_bonus:manufacturing 0.02 | SOV_Andropov |
| `SOV_Gorbachev_led_reforms_team_Private_Decree` | Andropov | perm | production_speed_office_park_factor 0.02, production_speed_agri_industrial_complex_factor 0.02, production_factory_efficiency_gain_factor 0.02, production_factory_max_efficiency_factor 0.02, research_bonus:management 0.04, research_bonus:manufacturing 0.02 | SOV_Andropov |
| `SOV_Mass_reshuffles_and_dismissals_in_the_party_and_administrative_apparatus` | Andropov | timed | political_power_factor -0.1 | SOV_Andropov |
| `SOV_Ongoing_mass_dismissals_in_the_Ministry_of_Internal_Affairs` | Andropov | timed | weekly_manpower -500, political_power_factor -0.05, army_core_defence_factor 0.1, stability_factor -0.03 | SOV_Andropov |
| `SOV_Preparation_for_an_anti_corruption_campaign` | Andropov | perm | political_power_factor -0.05 | SOV_Andropov |
| `SOV_Romanov_led_reforms_team` | Andropov | perm | production_speed_industrial_complex_factor 0.02, production_speed_office_park_factor 0.02 | SOV_Andropov_Events |
| `SOV_Romanov_led_reforms_team_Decree_Market` | Andropov | perm | production_speed_industrial_complex_factor 0.02, production_speed_office_park_factor 0.02, production_factory_efficiency_gain_factor 0.02, production_factory_max_efficiency_factor 0.02, research_bonus:manufacturing 0.02, research_bonus:computing_tech 0.02 | SOV_Andropov |
| `SOV_Romanov_led_reforms_team_Market` | Andropov | perm | production_speed_industrial_complex_factor 0.02, production_speed_office_park_factor 0.02, research_bonus:manufacturing 0.02, research_bonus:computing_tech 0.02 | SOV_Andropov |
| `SOV_Special_Commission_for_the_Direction_of_the_Economic_Experiment` | Andropov | perm | production_speed_office_park_factor 0.01, production_speed_agri_industrial_complex_factor 0.01 | SOV_Andropov |
| `SOV_Wide_anti_corruption_campaign` | Andropov | perm | political_power_factor 0.05, stability_factor 0.01, drift_defence_factor -0.05 | SOV_Andropov |
| `SOV_law_on_labour_collectives` | Andropov | perm | production_speed_buildings_factor 0.01, industrial_capacity_factory 0.01, industrial_capacity_dockyard 0.01, production_factory_max_efficiency_factor 0.01, production_factory_efficiency_gain_factor 0.025, line_change_production_efficiency_factor 0.025, research_bonus:manufacturing 0.02, research_bonus:computing_tech 0.02 | SOV_Andropov_Events |
| `andropov_diplomacy` | Andropov | perm | guarantee_cost -0.3, opinion_gain_monthly 5 | SOV_Andropov |
| `era_of_stagnation` | Andropov | perm | stability_factor -0.06, drift_defence_factor -0.1, consumer_goods_factor 0.07, production_factory_max_efficiency_factor -0.05 | SOV_Andropov |
| `growing_alcoholism` | Andropov | perm | production_factory_max_efficiency_factor -0.05, decryption_factor -0.075, war_support_factor -0.025 | SOV_Andropov |
| `Joint_Planning_Commission` | Beria-Malenkov | timed | production_factory_max_efficiency_factor 0.05 | SOV_Beria_Malenkov |
| `Joint_Planning_Commission_Empowered` | Beria-Malenkov | timed | production_factory_max_efficiency_factor 0.05, production_speed_buildings_factor 0.1, political_power_gain -0.25 | SOV_Beria_Malenkov |
| `Politicized_Army_1` | Beria-Malenkov | perm | experience_gain_army_factor -0.1, political_power_gain 0.02 | SOV_Beria_Malenkov |
| `Politicized_Army_2` | Beria-Malenkov | perm | experience_gain_army_factor -0.15, political_power_gain 0.04 | SOV_Beria_Malenkov |
| `Politicized_Army_3` | Beria-Malenkov | perm | experience_gain_army_factor -0.2, political_power_gain 0.06 | SOV_Beria_Malenkov |
| `Recently_Created_Water_Commissions` | Beria-Malenkov | timed | production_speed_water_infrastructure_factor 0.2 | SOV_Beria_Malenkov |
| `Soviet_Greatworks` | Beria-Malenkov | perm | consumer_goods_factor 0.05 | SOV_Beria_Malenkov |
| `pacific_naval_treaty_adherent` | Beria-Malenkov | perm | production_cost_max_screen_hull_medium 2000, production_cost_max_screen_hull_heavy 4000, production_cost_max_carrier_hull_light 1000, production_cost_max_carrier_hull 2200, production_cost_max_carrier_hull_super 4000, production_cost_max_battle_hull_light 1500, production_cost_max_battle_hull_medium 2000, production_cost_max_battle_hull_heavy 4000, production_cost_max_sub_hull_small_single 1800, production_cost_max_sub_hull_large_single 3500, production_cost_max_sub_hull_large_double 7000 | SOV_Beria_Malenkov |
| `recently_reshuffled_foreign_ministry` | Beria-Malenkov | timed | trade_opinion_factor 0.3 | SOV_Beria_Malenkov |
| `redirected_engineers` | Beria-Malenkov | timed | production_speed_arms_factory_factor -0.25 | SOV_Beria_Malenkov |
| `AK_74_Service_Rifle_Adoption` | Brezhnev | timed | equipment_bonus:infantry_equipment.build_cost_ic -0.15, equipment_bonus:infantry_equipment.instant yes | SOV_Brezhnev_Mil |
| `Academic_Competition` | Brezhnev | timed | research_speed_factor 0.02 | SOV_Mid_Foriegn_Policy |
| `BMP_Bonus` | Brezhnev | timed | equipment_bonus:light_tank_ifv_chassis.build_cost_ic -0.35, equipment_bonus:light_tank_ifv_chassis.soft_attack 0.10, equipment_bonus:light_tank_ifv_chassis.hard_attack 0.25, equipment_bonus:light_tank_ifv_chassis.instant yes | SOV_Brezhnev_Mil |
| `BMP_Cost_Reduction` | Brezhnev | perm | equipment_bonus:light_tank_ifv_chassis.build_cost_ic -0.35, equipment_bonus:light_tank_ifv_chassis.instant yes | SOV_Brezhnev_Mil |
| `Fight_Crime` | Brezhnev | timed | stability_factor 0.05, resistance_growth -0.25 | SOV_Brezhnev |
| `Inflation_Crisis` | Brezhnev | timed | consumer_goods_factor 0.05, production_factory_max_efficiency_factor -0.075, stability_factor -0.05 | SOV_Brezhnev |
| `Inflation_Crisis2` | Brezhnev | timed | consumer_goods_factor 0.025, production_factory_max_efficiency_factor -0.05, stability_factor -0.025 | SOV_Brezhnev |
| `Nomenklatura` | Brezhnev | perm | stability_factor 0.05, drift_defence_factor 0.25, political_power_gain 0.1 | SOV_Brezhnev |
| `Nomenklatura2` | Brezhnev | perm | stability_factor 0.1, drift_defence_factor 0.5, political_power_gain 0.2 | SOV_Brezhnev |
| `Nomenklatura3` | Brezhnev | perm | stability_factor 0.125, drift_defence_factor 0.65, political_power_gain 0.25, production_factory_efficiency_gain_factor 0.01 | SOV_Brezhnev |
| `Nomenklatura4` | Brezhnev | perm | stability_factor 0.15, drift_defence_factor 0.75, political_power_gain 0.3, production_factory_efficiency_gain_factor 0.025 | SOV_Brezhnev |
| `Nomenklatura5` | Brezhnev | perm | stability_factor 0.2, drift_defence_factor 0.85, political_power_gain 0.35, production_factory_efficiency_gain_factor 0.05 | SOV_Brezhnev |
| `SF_Cap_Bonus` | Brezhnev | timed | special_forces_cap 0.10 | SOV_Brezhnev_Mil |
| `SOV_Recon_Helicoptor_Bonus` | Brezhnev | timed | equipment_bonus:scout_helicopter_equipment.build_cost_ic -0.25, equipment_bonus:scout_helicopter_equipment.instant yes | SOV_Brezhnev_Mil |
| `SOV_Thermobaric_ATGM_Warheads` | Brezhnev | timed | equipment_bonus:atgm_equipment.soft_attack 0.25, equipment_bonus:light_tank_destroyer_chassis.soft_attack 0.25 | SOV_Brezhnev_Mil |
| `SOV_ZSU_23_4_Afghanski` | Brezhnev | timed | equipment_bonus:light_tank_aa_chassis.hard_attack 0.25, equipment_bonus:light_tank_aa_chassis.soft_attack 0.25 | SOV_Brezhnev_Mil |
| `Secret_Courts` | Brezhnev | timed | war_support_factor 0.03, drift_defence_factor 0.2 | SOV_Brezhnev |
| `VDV_BMP` | Brezhnev | timed | **none** | SOV_Brezhnev_Mil |
| `VDV_Expansion` | Brezhnev | perm | special_forces_cap 0.25 | SOV_Brezhnev_Mil |
| `Vozdushno_desantnye_voyska` | Brezhnev | perm | **none** | SOV_Brezhnev_Mil |
| `Vozdushno_desantnye_voyska_1` | Brezhnev | perm | equipment_bonus:transport_plane_equipment.build_cost_ic -0.25, equipment_bonus:transport_plane_equipment.instant yes | SOV_Brezhnev_Mil |
| `Vozdushno_desantnye_voyska_2` | Brezhnev | perm | equipment_bonus:utility_helicopter_equipment.build_cost_ic -0.25, equipment_bonus:utility_helicopter_equipment.instant yes | SOV_Brezhnev_Mil |
| `black_market1` | Brezhnev | perm | production_speed_industrial_complex_factor -0.025, production_speed_infrastructure_factor -0.025, production_speed_synthetic_refinery_factor -0.025, production_factory_max_efficiency_factor -0.025 | SOV_Brezhnev |
| `black_market2` | Brezhnev | perm | production_speed_industrial_complex_factor -0.05, production_speed_infrastructure_factor -0.05, production_speed_synthetic_refinery_factor -0.05, production_factory_max_efficiency_factor -0.05 | SOV_Brezhnev |
| `black_market3` | Brezhnev | perm | production_speed_industrial_complex_factor -0.075, production_speed_infrastructure_factor -0.075, production_speed_synthetic_refinery_factor -0.075, production_factory_max_efficiency_factor -0.075, stability_factor 0.025 | SOV_Brezhnev |
| `black_market4` | Brezhnev | perm | production_speed_industrial_complex_factor -0.1, production_speed_infrastructure_factor -0.1, production_speed_synthetic_refinery_factor -0.1, production_factory_max_efficiency_factor -0.1, stability_factor 0.05 | SOV_Brezhnev |
| `black_market5` | Brezhnev | perm | production_speed_industrial_complex_factor -0.125, production_speed_infrastructure_factor -0.125, production_speed_synthetic_refinery_factor -0.125, production_factory_max_efficiency_factor -0.125, stability_factor 0.075, political_power_gain 0.15 | SOV_Brezhnev |
| `capitalism` | Brezhnev | timed | production_factory_max_efficiency_factor 0.2, research_speed_factor 0.01, political_power_factor 0.25 | SOV_Brezhnev |
| `centralization` | Brezhnev | timed | industrial_capacity_factory 0.05, production_speed_buildings_factor 0.05, stability_factor 0.05 | SOV_Brezhnev |
| `economic_growth` | Brezhnev | timed | consumer_goods_factor -0.02, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05 | Sov_Five_Year_Plan_Eight, Sov_Five_Year_Plan_Eleven, Sov_Five_Year_Plan_Nine |
| `education_invest` | Brezhnev | timed | research_speed_factor 0.01 | Sov_Five_Year_Plan_Eight |
| `gulag_politic` | Brezhnev | timed | production_speed_buildings_factor 0.05, stability_factor -0.1 | SOV_Brezhnev |
| `high_quotas` | Brezhnev | timed | consumer_goods_factor -0.02, stability_factor -0.1, production_speed_buildings_factor 0.1, production_factory_max_efficiency_factor 0.05 | Sov_Five_Year_Plan_Eight |
| `high_skill_engineers` | Brezhnev | timed | production_speed_buildings_factor 0.1 | Sov_Five_Year_Plan_Eight |
| `hygene_campaign` | Brezhnev | timed | stability_factor 0.05, MONTHLY_POPULATION 0.05 | SOV_Brezhnev |
| `hyperinflation1` | Brezhnev | timed | consumer_goods_factor 0.1, production_factory_max_efficiency_factor -0.15, stability_factor -0.1 | SOV_Brezhnev |
| `ideological_fanaticism_focus` | Brezhnev | perm | war_support_factor 0.05, army_core_attack_factor 0.05, army_core_defence_factor 0.05, rule:can_create_factions yes, rule:can_send_volunteers yes | SOV_Brezhnev |
| `increased_encryption` | Brezhnev | timed | encryption 0.25, decryption 0.25 | SOV_Brezhnev |
| `infilitrate_pro_democratic_groups` | Brezhnev | timed | drift_defence_factor 0.25, Social_Democratic_drift -0.01, democratic_drift -0.01, conservative_drift -0.01, centrist_drift -0.01, Christian_Democratic_drift -0.01, Liberal_Conservatism_drift -0.01 | SOV_Brezhnev |
| `marxist_escuelas` | Brezhnev | perm | research_speed_factor 0.025, consumer_goods_factor 0.02, drift_defence_factor 0.5, conscription_factor 0.05 | SOV_Brezhnev |
| `mass_propaganda` | Brezhnev | timed | communism_drift 0.05 | SOV_Brezhnev |
| `medical_increase` | Brezhnev | timed | MONTHLY_POPULATION 0.01 | Sov_Five_Year_Plan_Eight, Sov_Five_Year_Plan_Eleven |
| `military_expansion` | Brezhnev | timed | conscription_factor 0.05, land_doctrine_cost_factor -0.05 | SOV_Mid_Foriegn_Policy |
| `private_plots` | Brezhnev | timed | production_speed_agri_industrial_complex_factor 0.1 | Sov_Five_Year_Plan_Eight |
| `public_media` | Brezhnev | perm | stability_factor 0.05, research_speed_factor 0.02, political_power_gain -0.01, drift_defence_factor 0.35 | SOV_Brezhnev |
| `purge_reformists` | Brezhnev | timed | democratic_drift -0.04, democratic_acceptance -5 | SOV_Brezhnev |
| `purge_the_inteligenista` | Brezhnev | timed | drift_defence_factor 0.15, research_speed_factor -0.025 | SOV_Brezhnev |
| `reduce_bureacracy` | Brezhnev | timed | production_speed_industrial_complex_factor 0.05, production_speed_arms_factory_factor 0.05, industrial_capacity_factory 0.05, research_speed_factor -0.01 | SOV_Brezhnev |
| `repression` | Brezhnev | timed | resistance_growth -0.2, stability_factor -0.05, conscription_factor -0.01, political_power_factor 0.1 | SOV_Brezhnev |
| `revolutionary_fervor` | Brezhnev | timed | war_support_factor 0.05, drift_defence_factor 0.5 | SOV_Brezhnev |
| `socialist_realism` | Brezhnev | perm | research_speed_factor 0.01, conscription_factor 0.05 | SOV_Brezhnev |
| `sov_agr_bur_reduce` | Brezhnev | timed | **none** | Sov_Five_Year_Plan_Eleven, Sov_Five_Year_Plan_Nine |
| `sov_agr_ca_pop` | Brezhnev | timed | **none** | Sov_Five_Year_Plan_Eleven |
| `sov_agr_mach_mod` | Brezhnev | timed | **none** | SOV_5_year_plans, Sov_Five_Year_Plan_Nine |
| `sov_agr_proc_mod` | Brezhnev | timed | **none** | Sov_Five_Year_Plan_Ten |
| `sov_agr_prod_choose` | Brezhnev | timed | **none** | Sov_Five_Year_Plan_Eleven |
| `sov_agr_subs` | Brezhnev | timed | **none** | SOV_5_year_plans, Sov_Five_Year_Plan_Eleven |
| `sov_compete_int_market` | Brezhnev | timed | research_speed_factor 0.01 | Sov_Five_Year_Plan_Nine |
| `sov_computers_to_companies` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.1 | Sov_Five_Year_Plan_Ten |
| `sov_crop_rotation` | Brezhnev | perm | **none** | Sov_Five_Year_Plan_Eight |
| `sov_divide_budget_bur` | Brezhnev | timed | production_speed_industrial_complex_factor 0.05, production_speed_arms_factory_factor 0.05, production_speed_agri_industrial_complex_factor 0.05 | Sov_Five_Year_Plan_Eight |
| `sov_eco_decentr` | Brezhnev | timed | political_power_factor -0.05, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.1, production_factory_efficiency_gain_factor 0.1, base_fuel_gain_factor 0.05 | Sov_Five_Year_Plan_Eight |
| `sov_eco_export` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05, trade_opinion_factor 0.25 | Sov_Five_Year_Plan_Eight |
| `sov_eco_mil_cuts` | Brezhnev | timed | political_power_factor -0.05, stability_factor -0.025, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05, research_speed_factor 0.01, army_morale_factor -0.1 | Sov_Five_Year_Plan_Eight |
| `sov_eff_labor_use` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.1 | Sov_Five_Year_Plan_Eleven |
| `sov_enc_priv_busn` | Brezhnev | timed | production_speed_industrial_complex_factor 0.1 | Sov_Five_Year_Plan_Eight |
| `sov_eq_towards_mic` | Brezhnev | timed | research_speed_factor -0.01, production_speed_industrial_complex_factor -0.1, production_speed_agri_industrial_complex_factor -0.1, production_factory_efficiency_gain_factor 0.1, production_speed_arms_factory_factor 0.1 | Sov_Five_Year_Plan_Nine |
| `sov_forecast_comp` | Brezhnev | timed | production_factory_max_efficiency_factor 0.025, production_factory_efficiency_gain_factor 0.025 | Sov_Five_Year_Plan_Eight |
| `sov_ind_modernity` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05, research_speed_factor 0.01 | Sov_Five_Year_Plan_Eight |
| `sov_long_term_agri` | Brezhnev | timed | production_speed_agri_industrial_complex_factor 0.1 | Sov_Five_Year_Plan_Eight |
| `sov_modernise_mac` | Brezhnev | timed | production_factory_efficiency_gain_factor 0.1 | Sov_Five_Year_Plan_Eleven |
| `sov_more_women_prod` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05 | Sov_Five_Year_Plan_Ten |
| `sov_new_companies_ass` | Brezhnev | timed | production_speed_industrial_complex_factor 0.05, production_speed_arms_factory_factor 0.05 | Sov_Five_Year_Plan_Nine |
| `sov_prevent_mic` | Brezhnev | timed | research_speed_factor 0.01, production_speed_industrial_complex_factor 0.1, production_speed_agri_industrial_complex_factor 0.1, production_factory_efficiency_gain_factor -0.1, production_speed_arms_factory_factor -0.1 | Sov_Five_Year_Plan_Nine |
| `sov_prod_to_workers` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05, stability_weekly 0.001, political_power_gain 0.1 | Sov_Five_Year_Plan_Ten |
| `sov_restrain_mil_skilled` | Brezhnev | timed | research_speed_factor 0.02 | Sov_Five_Year_Plan_Nine |
| `sov_reward_private_dis` | Brezhnev | timed | research_speed_factor 0.01 | Sov_Five_Year_Plan_Ten |
| `sov_rular_attr` | Brezhnev | timed | production_speed_agri_industrial_complex_factor 0.1 | Sov_Five_Year_Plan_Ten |
| `sov_rural_ins` | Brezhnev | timed | production_speed_agri_industrial_complex_factor 0.05 | Sov_Five_Year_Plan_Eight |
| `sov_sensible_meat` | Brezhnev | perm | **none** | Sov_Five_Year_Plan_Eight, Sov_Five_Year_Plan_Nine |
| `sov_subs_based_production` | Brezhnev | timed | production_factory_max_efficiency_factor 0.05, production_factory_efficiency_gain_factor 0.05 | Sov_Five_Year_Plan_Eight |
| `sov_tran_power_to_loc` | Brezhnev | timed | production_speed_industrial_complex_factor 0.1 | Sov_Five_Year_Plan_Nine |
| `soviet_natalism` | Brezhnev | timed | MONTHLY_POPULATION 0.05 | Sov_Five_Year_Plan_Nine |
| `state_media` | Brezhnev | perm | stability_factor -0.05, resistance_growth -0.25, drift_defence_factor 1 | SOV_Brezhnev |
| `workers_culture` | Brezhnev | timed | production_speed_buildings_factor 0.1 | Sov_Five_Year_Plan_Ten |
| `youth_positive` | Brezhnev | timed | mobilization_speed 0.25, stability_factor 0.05 | SOV_Brezhnev |
| `SOV_Chairman_Molotov` | Bulganin | perm | opinion_gain_monthly_same_ideology_factor 0.05, send_volunteer_size 3, drift_defence_factor 0.04 | SOV_Bulganin |
| `SOV_Dep_Chairman_Kaganovich` | Bulganin | perm | production_factory_efficiency_gain_factor 0.02, production_factory_max_efficiency_factor 0.02, political_power_gain 0.04 | SOV_Bulganin |
| `SOV_Khrushchevite_Affair` | Bulganin | perm | political_power_gain 0.1 | SOV_Bulganin |
| `SOV_Khrushchevites_Purge` | Bulganin | perm | political_power_gain -0.15 | SOV_Bulganin |
| `SOV_Measures_Against_Khrushchevites` | Bulganin | perm | stability_factor -0.05, political_power_gain -0.15 | SOV_Bulganin |
| `SOV_Revamped_Political_Bureau` | Bulganin | perm | political_power_gain 0.05 | SOV_Bulganin |
| `SOV_Stabiilised_Politiburo` | Bulganin | perm | stability_factor 0.05, political_power_gain 0.05 | SOV_Bulganin |
| `SOV_Stalinist_Cult` | Bulganin | perm | war_stability_factor 0.1, opinion_gain_monthly_factor -0.05 | SOV_Bulganin |
| `sov_dekhrushchevization` | Bulganin | perm | stability_weekly 0.0005, political_power_gain 0.10, resistance_decay 0.10, resistance_target -0.10 | SOV_Bulganin |
| `sov_revisionism_defeated` | Bulganin | perm | stability_weekly 0.0015, arms_factory_throughput 0.05 | SOV_Bulganin |
| `sov_stalinist_agriculture` | Bulganin | perm | production_speed_agri_industrial_complex_factor 0.1, food_income_bonus 0.1 | SOV_Bulganin_events |
| `sov_stalinist_agriculture_inov_fail` | Bulganin | perm | production_speed_agri_industrial_complex_factor -0.025, food_income_bonus -0.01 | SOV_Bulganin_events |
| `sov_stalinist_agriculture_inov_good` | Bulganin | perm | production_speed_agri_industrial_complex_factor 0.2, modifier_agriculture_output 0.1, food_income_bonus 0.03, consumer_goods_factor 0.02, stability_factor 0.03 | SOV_Bulganin_events |
| `EGSVT_Network_early` | Kaganovich | perm | consumer_goods_factor 0.14, research_speed_factor 0.04, production_speed_industrial_complex_factor 0.01, static_anti_air_hit_chance_factor 0.01 | SOV_Kaganovich |
| `Experimental_mobile_concrete_plants` | Kaganovich | timed | production_speed_buildings_factor 0.005 | SOV_Kaganovich |
| `Fragile_Kaganovich_Rule` | Kaganovich | perm | political_power_factor -0.01, stability_factor -0.025 | SOV_Kaganovich |
| `Improved_Ground_Based_Air_Defence_Network` | Kaganovich | timed | static_anti_air_hit_chance_factor 0.05 | SOV_Kaganovich |
| `Improved_police_training` | Kaganovich | timed | mobilization_speed 0.15 | SOV_Kaganovich |
| `Kaganovichism_cemented` | Kaganovich | perm | political_power_factor 0.02, stability_factor 0.01 | SOV_Kaganovich |
| `Kaganovichism_successful` | Kaganovich | perm | political_power_factor 0.03, stability_factor 0.025, research_speed_factor 0.01, production_speed_buildings_factor 0.01 | SOV_Kaganovich |
| `SOV_experienced_army` | Kaganovich | perm | army_leader_start_level 1, motorized_defence_factor 0.025 | SOV_Kaganovich |
| `SOV_experienced_army_2` | Kaganovich | perm | army_leader_start_level 1, motorized_defence_factor 0.025, army_artillery_defence_factor 0.025 | SOV_Kaganovich |
| `SOV_experienced_army_3` | Kaganovich | perm | army_leader_start_level 1, motorized_defence_factor 0.025, army_artillery_defence_factor 0.025, air_intercept_efficiency 0.1 | SOV_Kaganovich |
| `best_of_both_world_hardware` | Kaganovich | perm | research_speed_factor 0.005 | SOV_Kaganovich |
| `better_consumer_goods_management` | Kaganovich | perm | consumer_goods_factor -0.01 | SOV_Kaganovich |
| `better_consumer_goods_management_1` | Kaganovich | perm | consumer_goods_factor -0.02 | SOV_Kaganovich |
| `enlarged_collective_farms` | Kaganovich | perm | consumer_goods_factor -0.03, production_lack_of_resource_penalty_factor -0.02 | SOV_Kaganovich |
| `experienced_nonc_combating_officers_ranks` | Kaganovich | perm | army_leader_start_level 1 | SOV_Kaganovich |
| `five_year_plan` | Kaganovich, Khrushchev, Ustinov | timed | production_factory_efficiency_gain_factor 0.025, production_speed_buildings_factor 0.1 | SOV_Kaganovich, SOV_Khruschev, SOV_Ogarkov, SOV_Ustinov |
| `invested_in_housing` | Kaganovich, Khrushchev | timed | monthly_population 0.001 | SOV_Kaganovich, SOV_Khruschev |
| `investment_in_cybernetics` | Kaganovich | perm | **none** | SOV_Kaganovich |
| `investment_in_cybernetics_2` | Kaganovich | perm | consumer_goods_factor 0.05, research_speed_factor 0.01 | SOV_Kaganovich |
| `investment_in_cybernetics_3` | Kaganovich | perm | consumer_goods_factor 0.09, research_speed_factor 0.02 | SOV_Kaganovich |
| `large_scale_mobile_concrete_plants` | Kaganovich | timed | production_speed_buildings_factor 0.02 | SOV_Kaganovich |
| `more_nuclear_production` | Kaganovich | timed | nuclear_production_factor 0.05 | SOV_Kaganovich |
| `new_algorithms` | Kaganovich | perm | production_speed_industrial_complex_factor 0.005 | SOV_Kaganovich |
| `new_algorithms_2` | Kaganovich | perm | production_speed_industrial_complex_factor 0.005, static_anti_air_hit_chance_factor 0.005 | SOV_Kaganovich |
| `overhauled_maintenance` | Kaganovich | timed | consumer_goods_factor -0.01 | SOV_Kaganovich |
| `reformed_kolkhozes` | Kaganovich | perm | production_lack_of_resource_penalty_factor -0.01 | SOV_Kaganovich |
| `reformed_komsomol` | Kaganovich | perm | drift_defence_factor 0.1, research_speed_factor 0.05, production_speed_buildings_factor 0.1, political_power_factor 0.15, stability_factor 0.05 | SOV_Kaganovich |
| `self_management_doctrine` | Kaganovich | perm | consumer_goods_factor -0.01, production_speed_industrial_complex_factor -0.01 | SOV_Kaganovich |
| `self_management_doctrine_2` | Kaganovich | perm | consumer_goods_factor -0.02, production_speed_industrial_complex_factor -0.03 | SOV_Kaganovich |
| `self_management_doctrine_3` | Kaganovich | perm | consumer_goods_factor -0.03, production_speed_industrial_complex_factor -0.05 | SOV_Kaganovich |
| `self_management_doctrine_4` | Kaganovich | perm | consumer_goods_factor -0.05, production_speed_industrial_complex_factor -0.07 | SOV_Kaganovich |
| `self_management_doctrine_5` | Kaganovich | perm | consumer_goods_factor -0.08, production_speed_industrial_complex_factor -0.1 | SOV_Kaganovich |
| `soviet_expanded_consumer_goods` | Kaganovich | perm | consumer_goods_factor 0.01, stability_factor 0.02 | SOV_Kaganovich |
| `soviet_expanded_consumer_goods_2` | Kaganovich | perm | consumer_goods_factor 0.02, stability_factor 0.04 | SOV_Kaganovich |
| `soviet_expanded_consumer_goods_3` | Kaganovich | perm | consumer_goods_factor 0.03, stability_factor 0.06 | SOV_Kaganovich |
| `soviet_expanded_consumer_goods_4` | Kaganovich | perm | consumer_goods_factor 0.04, stability_factor 0.08 | SOV_Kaganovich |
| `soviet_expanded_consumer_goods_5` | Kaganovich | perm | consumer_goods_factor 0.05, stability_factor 0.1 | SOV_Kaganovich |
| `soviet_expanded_elementary_and_medium_schools` | Kaganovich | timed | production_factory_efficiency_gain_factor 0.02, stability_factor 0.01 | SOV_Kaganovich |
| `soviet_expanded_numbers_of_students_1` | Kaganovich | timed | research_speed_factor 0.02 | SOV_Kaganovich |
| `soviet_expanded_numbers_of_students_2` | Kaganovich | timed | monthly_population 0.1 | SOV_Kaganovich |
| `soviet_expanded_numbers_of_students_3` | Kaganovich | timed | research_speed_factor 0.01, production_factory_max_efficiency_factor 0.01 | SOV_Kaganovich |
| `soviet_free_specialized_education` | Kaganovich, Khrushchev | perm/timed | research_speed_factor 0.015 | SOV_Kaganovich, SOV_Khruschev |
| `soviet_planned_komsomol_reform` | Kaganovich | perm | **none** | SOV_Kaganovich |
| `soviet_planned_komsomol_reform_1` | Kaganovich | perm | drift_defence_factor 0.1 | SOV_Kaganovich |
| `soviet_planned_komsomol_reform_2` | Kaganovich | perm | drift_defence_factor 0.1, stability_factor 0.01 | SOV_Kaganovich |
| `soviet_planned_komsomol_reform_3` | Kaganovich | perm | drift_defence_factor 0.1, production_speed_buildings_factor 0.1, stability_factor 0.01 | SOV_Kaganovich |
| `soviet_planned_komsomol_reform_4` | Kaganovich | perm | drift_defence_factor 0.1, research_speed_factor 0.01, production_speed_buildings_factor 0.1, political_power_factor 0.1 | SOV_Kaganovich |
| `soviet_planned_komsomol_reform_5` | Kaganovich | perm | drift_defence_factor 0.1, research_speed_factor 0.01, production_speed_buildings_factor 0.1, political_power_factor 0.1, stability_factor 0.01 | SOV_Kaganovich |
| `soviet_refocused_planning` | Kaganovich | timed | consumer_goods_factor 0.05, stability_factor 0.05 | SOV_Kaganovich |
| `standardised_concrete_standards` | Kaganovich | timed | production_speed_buildings_factor 0.01 | SOV_Kaganovich |
| `studying_western_computers` | Kaganovich | perm | research_speed_factor 0.0025 | SOV_Kaganovich |
| `upgraded_networking_algorithms` | Kaganovich | perm | production_speed_industrial_complex_factor 0.0075, static_anti_air_hit_chance_factor 0.0075, research_speed_factor 0.0075 | SOV_Kaganovich |
| `Currency_Devaluation` | Khrushchev | timed | consumer_goods_factor -0.04, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor -0.05 | SOV_Khruschev |
| `SOV_Anti_Party_Group_Coup` | Khrushchev | perm | stability_factor -0.1, political_power_gain -0.15 | SovietUnion_Historical_Events |
| `Ukrainian_Academy_of_sciences` | Khrushchev | perm | production_factory_max_efficiency_factor 0.1, research_speed_factor 0.01 | SOV_Khruschev |
| `nuclear_powered_icebreakers` | Khrushchev | perm | research_speed_factor 0.02, consumer_goods_factor -0.01 | SOV_Khruschev |
| `AK_47_Mass_Adoption` | Stalin | timed | equipment_bonus:infantry_equipment.build_cost_ic -0.25, equipment_bonus:infantry_equipment.instant yes | SOV_50s_Military |
| `Increase_T54_Production` | Stalin | timed | equipment_bonus:medium_tank_chassis.build_cost_ic -0.20, equipment_bonus:medium_tank_chassis.instant yes | SOV_50s_Military |
| `MiG_15_Mass_Adoption` | Stalin | timed | equipment_bonus:fighter_equipment.build_cost_ic -0.05, equipment_bonus:fighter_equipment.instant yes | SOV_50s_Military |
| `SOV_Beria_National_Reforms` | Stalin | perm | political_power_gain 0.01, stability_weekly -0.01 | SOV_Troika |
| `SOV_Beria_State_of_Emergency` | Stalin | perm | stability_weekly 0.01, command_power_gain -0.02, political_power_gain -1 | SOV_Troika |
| `SOV_Cancelled_Stalin_Projects` | Stalin | timed | consumer_goods_factor -0.07 | SOV_Troika |
| `SOV_Cautious_Destalinization` | Stalin | perm | political_power_cost 0.2 | SOV_Troika |
| `SOV_Condemnetion_of_Bureaucratism_and_Corruption` | Stalin | perm | party_popularity_stability_factor 0.08, political_power_gain 0.07 | SOV_Troika |
| `SOV_Dekanozov_Allied` | Stalin | perm | stability_factor 0.09, drift_defence_factor 0.08 | SOV_Troika |
| `SOV_Delayed_Presidium_Countermeasures` | Stalin | perm | political_power_gain -0.05, political_power_cost 0.1 | SOV_Troika |
| `SOV_KGB` | Stalin | perm | stability_factor 0.025, research_speed_factor 0.015, party_popularity_stability_factor 0.015, drift_defence_factor 0.01, intelligence_agency_defense 1, intel_network_gain_factor 0.15, intel_from_operatives_factor 0.2 | SOV_Troika |
| `SOV_KGB_Improved` | Stalin, Ustinov | perm | stability_factor 0.05, research_speed_factor 0.015, party_popularity_stability_factor 0.02, drift_defence_factor 0.02, intelligence_agency_defense 1.5, intel_network_gain_factor 0.2, intel_from_operatives_factor 0.3 | SOV_Troika, SOV_Ustinov |
| `SOV_Khrushchev_Exclusion_From_Presidium` | Stalin | perm | party_popularity_stability_factor 0.1, political_power_gain 0.1 | SOV_Troika |
| `SOV_Khrushchev_Politiburo` | Stalin | perm | research_speed_factor 0.02, party_popularity_stability_factor 0.0225 | SOV_Troika |
| `SOV_Khrushchevites_in_Presidium` | Stalin | perm | research_speed_factor 0.0175, party_popularity_stability_factor 0.0175 | SOV_Troika |
| `SOV_MGBMVD` | Stalin | perm | stability_factor 0.05, research_speed_factor 0.01, party_popularity_stability_factor 0.02, political_power_gain 0.05, drift_defence_factor 0.02 | SOV_Troika |
| `SOV_MGB_ongoing_Purge` | Stalin | perm | stability_factor 0.025, research_speed_factor 0.015, party_popularity_stability_factor 0.015, drift_defence_factor 0.01 | SOV_Troika |
| `SOV_MVD_IN_CONTROL` | Stalin | perm | stability_factor 0.1, drift_defence_factor 0.1 | SOV_Troika |
| `SOV_Malenkov_Allies` | Stalin | perm | party_popularity_stability_factor 0.02 | SOV_Troika |
| `SOV_Malenkov_Resignation` | Stalin | perm | research_speed_factor 0.0175, party_popularity_stability_factor 0.02 | SOV_Troika |
| `SOV_Merkulov_in_Power` | Stalin | perm | stability_factor 0.06, party_popularity_stability_factor 0.01, political_power_gain 0.04, drift_defence_factor 0.04 | SOV_Troika |
| `SOV_Meshik_Allied` | Stalin | perm | stability_factor 0.08, political_power_gain 0.02, drift_defence_factor 0.05 | SOV_Troika |
| `SOV_Party_Privileges_Cut` | Stalin | perm | party_popularity_stability_factor 0.06, political_power_gain 0.05 | SOV_Troika |
| `SOV_Pledged_Allegiance_to_the_Presidium` | Stalin | perm | political_power_cost 0.15 | SOV_Troika |
| `SOV_State_Atheism` | Stalin | timed | monthly_population -0.01, drift_defence_factor 0.05, war_support_factor 0.05 | SOV_Troika |
| `Submarine_Expansion` | Stalin | timed | equipment_bonus:sub_hull_large_single.build_cost_ic -0.1, equipment_bonus:sub_hull_large_single.instant yes, equipment_bonus:sub_hull_small_single.build_cost_ic -0.1, equipment_bonus:sub_hull_small_single.instant yes, equipment_bonus:sub_hull_large_double.build_cost_ic -0.1, equipment_bonus:sub_hull_large_double.instant yes | SOV_50s_Military |
| `idea_SOV_Pavlovian_Session` | Stalin | timed | research_speed_factor 0.025, political_power_gain -0.1 | SOV_Stalin |
| `soviet_economic_boost` | Stalin | timed | office_park_income_bonus 0.1, industrial_park_income_bonus 0.1, monthly_population 0.05 | SOV_50s_Industry |
| `EGSVT_Network_Akademset` | Ustinov | perm | consumer_goods_factor 0.14, research_speed_factor 0.08, production_speed_industrial_complex_factor 0.02, production_speed_office_park_factor 0.02, production_speed_buildings_factor 0.02, static_anti_air_hit_chance_factor 0.05 | SOV_Ustinov |
| `EGSVT_Network_Military` | Ustinov | perm | consumer_goods_factor 0.14, research_speed_factor 0.08, production_speed_industrial_complex_factor 0.02, production_speed_arms_factory_factor 0.03, production_speed_buildings_factor 0.02, static_anti_air_hit_chance_factor 0.07 | SOV_Ustinov |
| `EGSVT_Network_expanded` | Ustinov | perm | consumer_goods_factor 0.14, research_speed_factor 0.06, production_speed_industrial_complex_factor 0.01, production_speed_buildings_factor 0.02, static_anti_air_hit_chance_factor 0.05 | SOV_Ustinov |
| `SOV_Anti_alcohol_Campaign` | Ustinov | perm | monthly_population 0.005, stability_factor -0.02 | SOV_Ustinov |
| `SOV_Computerized_Logistics_Monitoring_idea` | Ustinov | perm/timed | production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05 | SOV_Ustinov |
| `SOV_Cybernetic_Constitution` | Ustinov | perm | stability_factor -0.05 | SOV_Ustinov |
| `SOV_Cybernetic_Future` | Ustinov | perm | stability_factor -0.01 | SOV_Ustinov |
| `SOV_Decriminialized_Homosexuality` | Ustinov | perm | war_support_factor 0.02, monthly_population -0.01, stability_factor -0.02 | SOV_Ustinov |
| `SOV_Early_Automation_of_the_Civilian_Economy` | Ustinov | perm | production_factory_efficiency_gain_factor 0.05, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05, production_speed_office_park_factor 0.05, production_speed_industrial_complex_factor 0.015, research_speed_factor 0.05, consumer_goods_factor -0.05 | SOV_Ustinov |
| `SOV_Early_Automation_of_the_Heavy_Industry` | Ustinov | perm | production_factory_efficiency_gain_factor 0.05, production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05, production_speed_office_park_factor 0.05, production_speed_industrial_complex_factor 0.01, production_speed_arms_factory_factor 0.05, research_speed_factor 0.05, consumer_goods_factor 0.05 | SOV_Ustinov |
| `SOV_Expanded_Anti_Alcohol_Campaigns` | Ustinov | perm | monthly_population 0.0075, stability_factor -0.06, production_factory_max_efficiency_factor 0.005 | SOV_Ustinov |
| `SOV_Experimental_Cybernetics_in_the_Red_Army` | Ustinov | perm | army_org_regain 0.05, army_org 0.5, experience_gain_army_unit 0.5, land_reinforce_rate 0.05, no_supply_grace 12, production_speed_supply_node_factor 0.1 | SOV_Ustinov |
| `SOV_Kaganovich_Institute` | Ustinov | perm | research_speed_factor 0.005 | SOV_Ustinov |
| `SOV_MGB_Army_Joint_IAC` | Ustinov | perm | stability_factor 0.05, research_speed_factor 0.01, party_popularity_stability_factor 0.02, political_power_gain 0.05, drift_defence_factor 0.02 | SOV_Ustinov |
| `SOV_New_Soviet_Man` | Ustinov | perm | war_support_factor 0.01 | SOV_Ustinov |
| `SOV_Partial_Prohibition` | Ustinov | perm | monthly_population 0.005, stability_factor -0.1, production_factory_max_efficiency_factor 0.0075 | SOV_Ustinov |
| `SOV_Real_Time_Troops_Monitoring` | Ustinov | perm | army_org_regain 0.05, army_org 0.5, experience_gain_army_unit 0.5 | SOV_Ustinov |
| `SOV_SOFE_Theory` | Ustinov | perm | production_speed_buildings_factor 0.05, production_factory_max_efficiency_factor 0.05, production_speed_office_park_factor 0.05, production_speed_industrial_complex_factor 0.01, research_speed_factor 0.05 | SOV_Ustinov |
| `SOV_Soviet_Cultural_Renaissance` | Ustinov | perm | research_speed_factor 0.065, stability_factor 0.01, political_power_gain 0.05, war_support_factor 0.02, monthly_population -0.01, drift_defence_factor 0.1, production_speed_buildings_factor 0.1, political_power_factor 0.15 | SOV_Ustinov |
| `SOV_Stalin_Institute` | Ustinov | perm | research_speed_factor 0.005 | SOV_Ustinov |
| `SOV_Studying_American_Prohibition_Era` | Ustinov | perm | monthly_population 0.005, stability_factor -0.04, production_factory_max_efficiency_factor 0.001 | SOV_Ustinov |
| `SOV_Updated_Curricula` | Ustinov | timed | production_factory_efficiency_gain_factor 0.01, research_speed_factor 0.01 | SOV_Ustinov |
| `SOV_computerized_crop_management` | Ustinov | perm | consumer_goods_factor 0.05 | SOV_Ustinov |
| `SOV_experienced_army_4` | Ustinov | perm | army_leader_start_level 1, army_org_factor 0.01, motorized_defence_factor 0.025, army_artillery_defence_factor 0.025, air_intercept_efficiency 0.1 | SOV_Ustinov |
| `SOV_experienced_army_5` | Ustinov | perm | army_leader_start_level 1, army_org_factor 0.03, motorized_defence_factor 0.025, army_artillery_defence_factor 0.025, air_intercept_efficiency 0.2 | SOV_Ustinov |
| `SOV_studying_western_academics` | Ustinov | perm | research_speed_factor 0.005 | SOV_Ustinov |
| `SOV_ANTI_MISINFORMATION` | WW3 1950s | perm | war_stability_factor -0.1, civilian_fear_modifier 0.25, city_infiltration_speed 0.05, border_security_strength 0.15, assassination_success_rate 0.1, targeted_modifier:tag USA, targeted_modifier:civilian_intel_factor -0.1, targeted_modifier:army_intel_factor -0.1 | SOV_WW3_1950s |
| `SOV_ANTI_MISINFORMATION_1` | WW3 1950s | perm | political_power_gain 0.1, war_stability_factor 0.05, civilian_fear_modifier 0.3, city_infiltration_speed 0.15, border_security_strength 0.15, assassination_success_rate 0.15, targeted_modifier:tag USA, targeted_modifier:civilian_intel_factor -0.15, targeted_modifier:army_intel_factor -0.15 | SOV_WW3_1950s |
| `Union_of_Laborer` | WW3 1950s | perm | surrender_limit 0.1, office_park_income_bonus 0.05, production_speed_industrial_complex_factor 0.1, industrial_capacity_factory 0.2, industrial_capacity_dockyard 0.2, workforce_ratio 0.15, wage_factor 0.1 | _SOV_WW3 |
| `great_liberation_war` | WW3 1950s | timed | planning_speed 0.2, army_speed_factor 0.1, production_speed_buildings_factor 0.2, political_power_factor -0.5, consumer_goods_factor 0.3, production_speed_infrastructure_factor 0.2, justify_war_goal_time -0.5, weekly_manpower 200, conscription 0.01, attrition -0.1, war_support_weekly 0.01, winter_attrition -0.15, army_core_attack_factor 0.2, army_core_defence_factor 0.2, recruitable_population 0.02, experience_gain_army 0.2, mobilization_speed 0.03, surrender_limit 0.5 | SOV_WW3_1950s |
| `great_liberation_war_2` | WW3 1950s | perm | planning_speed 0.4, army_speed_factor 0.2, production_speed_buildings_factor 0.4, political_power_factor -0.6, consumer_goods_factor 0.4, production_speed_infrastructure_factor 0.4, justify_war_goal_time -0.5, weekly_manpower 250, conscription 0.02, attrition -0.2, war_support_weekly 0.02, winter_attrition -0.2, army_core_attack_factor 0.1, army_core_defence_factor 0.1, recruitable_population 0.02, experience_gain_army 0.2, mobilization_speed 0.05, surrender_limit 0.3 | SOV_WW3_1950s |
| `great_liberation_war_3` | WW3 1950s | perm | planning_speed 0.5, army_speed_factor 0.3, production_speed_buildings_factor 0.6, political_power_factor -0.1, consumer_goods_factor 0.5, production_speed_infrastructure_factor 0.6, justify_war_goal_time -0.7, weekly_manpower 300, conscription 0.02, attrition -0.25, war_support_weekly 0.02, winter_attrition -0.2, army_attack_factor 0.2, army_defence_factor 0.2, recruitable_population 0.02, experience_gain_army 0.2, mobilization_speed 0.05, surrender_limit 0.3 | SOV_WW3_1950s |
| `rhine_in_seven_days` | WW3 1950s | timed | equipment_capture 0.1, air_attack_factor 0.15, army_speed_factor 0.5, targeted_modifier:tag WGR, targeted_modifier:attack_bonus_against 0.5, targeted_modifier:max_surrender_limit_offset -0.4 | SOV_WW3_1950s |
| `the_last_war` | WW3 1950s | perm | conscription 0.5, non_core_manpower 0.35, army_core_attack_factor 0.95, army_core_defence_factor 0.95, mobilization_speed 0.5, attrition -0.5, repair_speed_arms_factory_factor -0.5, ground_attack 0.8, no_supply_grace 0.9, max_dig_in 0.8, army_org 0.7, sickness_chance 0.3, wounded_chance_factor 0.5, ai_call_ally_desire_factor 0.5, surrender_limit 0.99, political_power_gain -0.5 | _SOV_WW3 |
| `SOV_Abortion_Criminalized` | — | perm | stability_factor -0.02, political_power_gain -0.05, monthly_population 0.005 | SOV - Soviet union |
| `SOV_MGB` | — | perm | stability_factor 0.025, research_speed_factor 0.01, party_popularity_stability_factor 0.01, drift_defence_factor 0.01 | SOV - Soviet union |
| `Suchyi_voyny` | — | perm | stability_factor -0.01, war_support_factor -0.02 | SOV - Soviet union |
| `antiquated_infrastructure` | — | perm | planning_speed -0.1, army_speed_factor -0.1, production_speed_buildings_factor -0.2 | SOV - Soviet union |
| `comecon_agri` | — | perm | research_speed_factor -0.10, MONTHLY_POPULATION 0.15, production_speed_buildings_factor -0.10, production_speed_infrastructure_factor 0.10 | SovietUnion_Focus_Events |
| `comecon_heavy_industrial` | — | perm | research_speed_factor -0.10, production_speed_industrial_complex_factor -0.10, production_speed_arms_factory_factor 0.10 | SovietUnion_Focus_Events |
| `comecon_industrial` | — | perm | research_speed_factor -0.01, production_speed_industrial_complex_factor 0.10, production_speed_arms_factory_factor -0.10 | SovietUnion_Focus_Events |
| `comecon_military` | — | perm | production_speed_industrial_complex_factor -0.15, production_speed_arms_factory_factor 0.10, conscription_factor 0.10 | SovietUnion_Focus_Events |
| `comecon_resource_extraction` | — | perm | production_speed_industrial_complex_factor 0.05, production_speed_arms_factory_factor -0.10, conscription_factor -0.10 | SovietUnion_Focus_Events |
| `comecon_technology_focus` | — | perm | research_speed_factor 0.1, production_speed_buildings_factor 0.1, conscription_factor -0.01 | SovietUnion_Focus_Events |
| `defcon_system_5` | — | perm | generate_wargoal_tension 1, stability_factor 0.02 | SOV - Soviet union |
| `gossnab` | — | perm | political_power_factor 0.05, supply_consumption_factor 0.05, stability_factor 0.03, production_speed_buildings_factor -0.05, production_factory_max_efficiency_factor -0.05, production_factory_efficiency_gain_factor -0.05, base_fuel_gain_factor -0.05 | SOV - Soviet union |
| `victor_of_the_great_patriotic_war` | — | perm | party_popularity_stability_factor 0.2, recruitable_population -0.02, justify_war_goal_time 0.5, experience_gain_army 0.05, defensive_war_stability_factor 0.2, conscription -0.01, mobilization_speed 0.03 | SOV - Soviet union |
