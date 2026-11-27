# Faction System Documentation

Checked against the code on 2026-11-26. Paths are relative to `Cold War Iron Curtain/` unless stated otherwise. This file replaces `LogDocs/Faction_Rework/Faction_Rework_Phase2_Draft.md` and `LogDocs/Faction_Rework/Translation_Handoff.md`.

Relevant history:

| Commit | Date | Change |
|---|---|---|
| `c348e75304` | 2026-10-31 | Pruned the vanilla goal pool; added Cominform/Warsaw Pact and Indochina goals and faction initiative. |
| `aa044f728f` | 2026-10-31 | Added the wartime coalition template and the guarded coalition API; migrated faction creation call sites. |
| `5df61ff9c1` | 2026-11-01 | Loose ends: Cominform lock, Non-Aligned Movement idea, translation handoff. |
| `3f8e1e6958` | 2026-11-01 | Treaty packages: UN Command (Korea), Rio Pact, GCC Peninsula Shield faction. |
| `bb7538a9ca` | 2026-11-01 | Merged `faction-bloc-hybrid` into `development-branch`. |
| `49a45bdcba` | 2026-11-06 | **Removed the Rio Pact.** |
| `9203dfd514` | later | NATO: keep members' puppets out of the faction and off the member list. |
| `e00110c91b` | later | Guard NATO idea churn. |

## 1. Overview

The mod uses the HOI4 faction system for two purposes:

1. **Engine factions** created with `create_faction_from_template`. They have a template, a manifest, goals and rules under `common/factions/`.
2. **Treaty packages** for overlapping commitments that cannot be engine factions (SEATO, Baghdad Pact/CENTO, UN Command in Korea). These use a membership idea, decisions and global flags, not faction membership.

The rule that decides between the two: a country can be in only one engine faction (see section 3). NATO and the Warsaw Pact keep the engine faction. Treaties that overlap with them are modelled as treaty packages.

Comecon is **not** a faction. It is an economic system with its own GUI (`interface/COMECON_Redux.gui`, `common/scripted_effects/COMECON_Effects.txt`). It is listed here only because its loc changed in the same rework.

### Directory layout (`common/factions/`)

| Path | Contents |
|---|---|
| `templates/` | 10 files, one template each except `SOV_Cominform_Warsaw_Pact.txt` (2) and `generic_factions.txt` (2). |
| `goals/faction_goals_{short,medium,long}_term.txt` | 18 / 19 / 8 goals after the vanilla pool was pruned in `c348e75304`. |
| `goals/CWIC_cold_war_faction_goals.txt` | `faction_goal_cwic_contain_communism`, `_spread_the_revolution`, `_arsenal_of_the_bloc`, `_non_aligned_unity`. |
| `goals/faction_manifests.txt` | Manifests: vanilla-derived ones plus CWIC ones (`faction_manifest_common_undertaking`, `faction_manifest_gcc_defence`, `faction_manifest_VIE_Dan_viqui`, etc.). |
| `rules/` | Joining, call-to-war, change-leader, dismissal, war-declaration, peace, manpower and exile rules; `rules/groups/rule_groups.txt`. |
| `member_upgrades/`, `icons/pool.txt` | Small; mostly vanilla shape. |
| `_documentation.md` | Paradox's format reference (vanilla file, not CWIC-specific). |

Supporting files:

- `common/ideas/faction.txt` (`hidden_ideas`): identity ideas shown in the UI. Examples are `Leader_of_the_Free_World`, `Close_NATO_Ally`, `Warsaw_Treaty_Organization_member`, `Cominform_Press_Discipline`, `Cominform_Reconstruction_Works`, `French_Indochina_Faction`, `Viet_Minh_Faction`, `Pathet_Lao_Faction`, `State_of_Vietnam_Faction`, `Karen_National_Union_Faction`, `Arakan_State_Alliance_Faction` and `Axis_of_Resistance`.
- `common/ideas/New_Ideologies_Ideas.txt:10552` `SEATO_member`, `:10565` `CENTO_member`, `:10619` `nato_member`.
- `common/ideas/zzz_generic.txt:1552` `non_aligned_movement_member_idea`. It is granted by focuses in `1950s_Albania_Anti_Communist`, `50s_PER`, `50s_SRT`, `60s_BUL` and others. It is not a faction.
- `common/scripted_guis/CWIC_faction_icon_gui.txt`: `CWIC_faction_icons` drives the `CWIC_factions_status_mapicons` window. `common/scripted_localisation/IC_faction_icons.txt` supplies its icon names.

## 2. Current implementation

### 2.1 Template summary

"Leader join" is `can_leader_join_other_factions`. A dash means the template does not set it, so the engine default applies (unverified).

| Template | File | Name key | Manifest | Leader join | Rules | Goals | Created by |
|---|---|---|---|---|---|---|---|
| `faction_template_nato` | `USA_North_Atlantic_Treaty_Organization.txt` | `nato_faction` | `faction_manifest_animus_in_consulendo_liber` | no | `joining_rule_puppets_only`, `war_declaration_generated_tension_25`, `war_declaration_threat_75`, `change_leader_rule_nato_usa_only` | none in template | `history/countries/USA - United States.txt:22`; `NATO_found_faction` |
| `faction_template_cominform` | `SOV_Cominform_Warsaw_Pact.txt` | `Cominform_name` | `faction_manifest_workers_of_the_world` | – | `joining_rule_communist_only`, `faction_peace_rule_puppeting_focus`, `change_leader_rule_warsaw_sov_only`, `war_declaration_rule_major_only` | aid Greek DSE, arm Korean army, consolidate GDR, conclude Warsaw treaty, coordinate party press, reconstruction agreements | `history/countries/SOV - Soviet union.txt:9` |
| `faction_template_Warsaw_Treaty_Organization` | same | `Warsaw_Treaty_Organization_name` | `faction_manifest_spread_of_communism` | – | `joining_rule_communist_only`, `change_leader_rule_warsaw_sov_only`, `dismissal_rule_ideology_not_communism`, `war_declaration_rule_major_only` | keep Hungary, Poland's commitments, Prague, Kabul, deterrence, unified command, Berlin frontier, forward groups, renew treaty | `SOV - Soviet union.txt:3548` (later bookmark); SOV events |
| `faction_template_french_indochina` | `FRE_French_Indochina.txt` | `french_indochina_faction` | `faction_manifest_VIE_Dan_viqui` | no | `joining_rule_puppets_only`, war-declaration pair, `call_to_war_rule_indochina_separate_commands`, `change_leader_rule_indochina_cefeo_only` | equip VNA, raise associated armies, hold Na San, keep Delta supplied, bring expedition home | `fre_indochina_command_initialize` (`common/scripted_effects/FRE_Indochina_Effects.txt:3050`) via `common/on_actions/FRE_CEFEO_on_actions.txt:8` |
| `faction_template_viet_minh` | `VIN_Viet_Minh.txt` | `viet_minh_faction` | `faction_manifest_VIN_Nothing_is_more_precious_than_independence_and_freedom` | yes | puppets only, war-declaration pair, `call_to_war_rule_indochina_separate_commands`, `change_leader_rule_industry`/`_manpower`/`_manifest_below_35` | reopen NW corridor, take Dien Bien Phu, end French expedition, equip main force, Chinese supply route, coordinate resistance fronts | `history/countries/VIN - Vietnam.txt:372` (also adds NLF) |
| `faction_template_state_of_vietnam` | `VIE_State_of_Vietnam.txt` | `state_of_vietnam_faction` | `faction_manifest_VIE_Dan_viqui` | yes | puppets only, war-declaration pair, change-leader industry/manpower/manifest | `faction_goal_secure_independent_state_of_vietnam` | **No caller.** `fre_indochina_command_initialize` retires any old VIE faction. |
| `faction_template_peninsula_shield` | `SAU_Peninsula_Shield_Force.txt` | `peninsula_shield_faction` | `faction_manifest_gcc_defence` | no | `joining_rule_gcc_members_only`, war-declaration pair, `change_leader_rule_sau_only` | five `faction_goal_gcc_*` goals | `events/Saudi_Arabia.txt:659` (`GCC_Peninsula_Shield.1`) |
| `faction_template_peoples_liberation_front` | `KPA_Peoples_Liberation_Front.txt` | `peoples_liberation_front_faction` | `faction_manifest_workers_of_the_world` | yes | puppets only, war-declaration pair, change-leader trio | destroy Kingdom of Greece, prep North Korea, win the Cold War 1950s | KPA focus/events |
| `faction_template_karen_national_union` | `KAY_Karen_National_Union.txt` | `karen_national_union_faction` | `faction_manifest_KAY_give_me_liberty_or_give_me_death` | yes | puppets only, war-declaration pair, change-leader trio | none | `history/countries/KAY ...:182` |
| `faction_template_arakan_state_alliance` | `CPB_Arakan_State_Alliance.txt` | `arakan_state_alliance_faction` | `faction_manifest_ARA_liberty_equality_fraternity` | yes | same as Karen | none | `history/countries/CPB ...:173` |
| `faction_template_generic` | `generic_factions.txt` | set by caller | `faction_manifest_common_undertaking` | yes | `joining_rule_neighbors_only`, `joining_rule_has_no_offensive_war`, `dismissal_rule_offensive_war`, `change_leader_rule_manpower` | `faction_goal_establish_joint_liaison` | 33 call sites |
| `faction_template_wartime_coalition` | `generic_factions.txt` | set by caller | `faction_manifest_common_undertaking` | yes | `change_leader_rule_manpower` only | `faction_goal_establish_joint_liaison` | 39 call sites |

All templates set `visible = { always = no }`, so players cannot pick them from the faction creation UI. Two exceptions: Cominform and Warsaw Pact have no `visible` block.

**Lock rules.** These are invisible rules with `trigger = { always = no }` and `can_remove = { always = no }`:

- `change_leader_rule_nato_usa_only`, `change_leader_rule_warsaw_sov_only`, `change_leader_rule_sau_only` and `change_leader_rule_indochina_cefeo_only` in `rules/change_leader_rules.txt:62-136`. They stop leadership from moving.
- `call_to_war_rule_indochina_separate_commands` in `rules/call_to_war_rules.txt:34`. It suppresses ordinary calls to war, so each Indochina operation brings in only its named belligerents.

**Joining rules.**

- `joining_rule_gcc_members_only` (`rules/joining_rules.txt:106`) admits only SAU, KUW, BHR, QAT, UAE and OMA.
- `joining_rule_communist_only` (`:128`) requires the same government as the leader unless the `can_join_opposite_factions` rule is set.

### 2.2 NATO

- **Identity.** The faction comes from `faction_template_nato`. The `NAT` tag alias (`common/country_tag_aliases/NATO_tag_aliases.txt:47`) resolves to USA while it has `nato_member` and falls back to USA. NATO arrays and variables live on `NAT` (`NAT.NATO_member_countries`, `NAT.NATO_military_cooperation`, and so on).
- **Membership.** Membership is the `nato_member` idea plus the `NAT.NATO_member_countries` array. Both are kept in sync with engine faction membership. The old `NATO_Member` idea was merged into `nato_member`; no `NATO_Member` reference remains in `common/` or `events/`.
- **Effects** (`common/scripted_effects/NATO_scripted_effects.txt`):

  | Effect | Line | What it does |
  |---|---|---|
  | `NATO_join` | 131 | Adds the array entry, the idea and politics list entry 200, and joins the NATO leader's faction if the country has none. Then applies the member effects. |
  | `NATO_found_faction` | 167 | Creates the faction only if the country has no faction and no NATO leader exists. |
  | `NATO_leave` | 182 | Removes the array entry, the idea, major status and the panel, then leaves the faction. |
  | `NATO_sync_membership` | 211 | Adds `nato_member` holders who have no faction. Removes subjects that lack `nato_member` (the engine pulls subjects in with their overlord). Reconciles the array against the faction in both directions. |
  | Issue/voting machinery | 9-1039 | `NATO_initialize_voting`, `NATO_whip_*`, `NATO_issue_N_effect/_fail` for issues 3-14, Marshall aid, `NATO_gre_return_command` and others. |

- **Triggers.** `common/scripted_triggers/NATO_scripted_triggers.txt` holds the issue `_can_start`, `_can_raise`, `_opposes` and `_stake` triggers, the government-group helpers and `NATO_greek_civil_war_ongoing`.
- **On actions.**
  - `common/on_actions/NATO_on_actions.txt` (`on_monthly_USA`): sync membership, grow the three integration bars, clamp them, recalculate member effects, let AI start issues, apply aid goodwill decay.
  - `common/on_actions/on_startup_defines.txt:2138`: initial sync and major status for ENG and FRA.
- **Decisions and GUI.** `common/decisions/IC_Nato_Decisons.txt`, `common/decisions/MD4_NATO.txt`; the NATO panel opens through the `show_nato_panel` variable.
- **Game rule.** `NATO_GREEK_INTERVENTION_RULE` (`common/game_rules/00_game_rules.txt:804`) has options `ALWAYS` and `NEVER` plus the default.

### 2.3 Cominform and Warsaw Pact

- **Creation.** The Cominform is created at game start (`SOV - Soviet union.txt:9`). The Warsaw Pact template is used by the later bookmark block (`:3548`) and by Soviet events.
- **Leadership.** Both are locked to SOV by `change_leader_rule_warsaw_sov_only`. This is the "Cominform lock" from `5df61ff9c1`.
- **Dismissal.** The Warsaw Pact also uses `dismissal_rule_ideology_not_communism`.
- **Ideas.** `Leader_of_the_Socialist_Nations`, `Warsaw_Treaty_Organization_member`, `Socialist_oriented_countries`, `Close_non_WTO_ally` and the two Cominform goal-reward ideas.
- **Decisions.** Soviet decisions for the goals are in `common/decisions/SOV.txt` (added in `c348e75304`).

### 2.4 Indochina factions

- **French Indochina (CEFEO).** `fre_indochina_command_initialize` (FRE scope) creates the faction once, unless `Indochina_War_Over`, `FRE_CEFEO_Dissolved` or `VIE_generic_faction_created` is set. It first dismantles any older VIE- or FRE-led faction, then adds VIE, CCC, FUL, TAI, NUN, TAM and THO where they exist. It also adds the UI-only identity ideas: `French_Indochina_Faction` for FRE, TAI, NUN, TAM and THO, and `State_of_Vietnam_Faction` for VIE, CCC and FUL.
- **Teardown.** `fre_indochina_command_dismantle` (`:3143`) dismantles the faction and removes the ideas. It is called from `fre_dissolution_cleanup` (`:1868`).
- **Viet Minh.** VIN creates the faction in history and adds NLF. On every init call, the second half of `fre_indochina_command_initialize` re-adds NLF if both coordination flags are set and NLF has no faction.
- **Pathet Lao.** There is **no Pathet Lao faction or template**. The `Pathet_Lao_Faction` idea (`common/ideas/faction.txt:172`) and its loc exist. The loc describes the Pathet Lao as a fraternal movement, "not a member of" the Viet Minh faction. No script adds the idea. The Laotian civil war is tracked through `geneva_pathet_lao_*` flags in `common/scripted_effects/CWIC_Geneva_Conference_Effects.txt:130-170`.
- **State of Vietnam.** The template exists but nothing creates it. The 60s VIE focus that sets `VIE_generic_faction_created` (`common/national_focus/60s_VIE.txt:4495`) creates a generic-template faction ("the League").

### 2.5 Peninsula Shield (GCC)

This is the one Phase 2 bloc implemented as an engine faction.

- **Lifecycle.** `GCC_lifecycle_monthly` (`common/scripted_effects/00_scripted_effects.txt:765`) runs inside `treaty_lifecycle_monthly`. It sets `GCC_1980_campaign` on the 1980 bookmark.
- **Founding.** After 1981-05-24, if all six states exist, are not subjects and are not in a faction, SAU fires `GCC_Peninsula_Shield.1`. That event creates the faction and sets `GCC_members_total = 6`.
- **Monthly upkeep.** `GCC_recount_members` counts members. Contributors who leave the faction lose `GCC_force_contributor`, which resets `global.GCC_force_months`.
- **Decisions.** `common/decisions/GCC_decisions.txt`: fund liaison, prepare the exercise, host the exercise, provide a contingent, approve the joint force, host facilities, provide a joint contingent, follow-up exercise, end participation.
- **Loc.** `localisation/english/GCC_Peninsula_Shield_l_english.yml`.

### 2.6 Treaty packages (idea-based, not factions)

All are driven monthly by `treaty_lifecycle_monthly` (`common/scripted_effects/USA_scripted_effects.txt:93`). It is called from `common/on_actions/00_on_actions.txt:68` in the UNS (United Nations dummy tag) branch of the monthly on_action.

| Package | Membership | Decisions | Lifecycle |
|---|---|---|---|
| SEATO | `SEATO_member` idea | `common/decisions/SEATO_decisions.txt` (liaison, exercises, assistance to Thailand and the Philippines, Indochina consultation and pledge, sustain, `SEATO_Renew_Treaty`) | Dissolves after 1977-06-30 (`SEATO_Dissolved`, idea removed) unless `SEATO_Continued`. |
| Baghdad Pact / CENTO | `CENTO_member` idea | `common/decisions/CENTO_decisions.txt` (pact council, staff link, Northern Tier exercise, successor cooperation, secretariat to Ankara, joint programme, `CENTO_Renew_Treaty`) | `Baghdad_Pact_Founded` is set once any country holds the idea. Renamed (`CENTO_Renamed`) on Iraqi withdrawal or after 1959-08-21; Iraq loses the idea on withdrawal. Dissolves after 1979-03-05 unless `CENTO_Survives`. |
| UN Command (Korea) | `UNCOM_participant` country flag | `common/decisions/UNCOM_decisions.txt` (liaison, ground/naval/air/transport contingents, resupply, sustain, armistice, withdraw) | `UNCOM_lifecycle_monthly` (`:169`) activates after 1950-07-06 once the Korean war and US entry flags are set. Closes on the UN ceasefire or when KOR is gone. Triggers `UNCOM_contributor`, `UNCOM_in_command`, `UNCOM_has_service_contribution` (`common/scripted_triggers/USA_scripted_triggers.txt`). |

`SEATO_member` is also read by `common/decisions/Beijing_pact_decisions.txt:114` and by UN voting content.

### 2.7 Generic and wartime coalitions

**Templates.** `faction_template_generic` and `faction_template_wartime_coalition` both use `faction_manifest_common_undertaking`. That manifest is the Phase 2 replacement for "Strength in Unity" (`faction_manifest_strength_in_unity` is still defined at `goals/faction_manifests.txt:251` but no template uses it). Both templates start with the single goal `faction_goal_establish_joint_liaison`.

**Coalition API** (`common/scripted_effects/00_scripted_effects.txt:662-763`):

| Effect | What it does |
|---|---|
| `coalition_init` | Run by the leader after creation. Reads the temp-style variables `coalition_new_objective`, `coalition_new_target` and `coalition_new_protected`. Sets the `coalition_leader` and `coalition_founder` flags and adds one objective goal: 1 `faction_goal_coalition_repel_invasion`, 2 `_preserve_government`, 3 `_secure_withdrawal`, 4 `_defeat_target`. |
| `coalition_add_member` | Adds `var:coalition_new_member` only if it is in no faction. This is the guard that stops a coalition from pulling a country out of NATO or the Warsaw Pact. Marks the member as a founder. |
| `coalition_recount_founders` | Recounts non-capitulated founders and records `coalition_war_seen`. |
| `coalition_campaign_reward` | Adds 2 faction initiative and 25 PP to every member. |
| `coalition_dissolve` | Clears flags and variables, then `dismantle_faction`. Only works on a `coalition_leader`. |

Triggers: `coalition_target_holds_member_owned_land` and `coalition_target_holds_member_cored_land` (`common/scripted_triggers/00_scripted_triggers.txt:106,120`).

**Callers.** 33 `faction_template_generic` and 39 `faction_template_wartime_coalition` creations across events and focuses. Examples: `events/Congo.txt`, `events/Korean_War.txt`, `events/aplwun.txt`, `events/Kenya.txt`, `history/countries/LBA - Libya.txt:484` ("Islamic Legion").

**Legacy `create_faction`.** One call remains: `create_faction = Emerging_Forces_Pact` at `common/national_focus/PRC_50s_Shared_Focuses.txt:5891`.

## 3. Engine constraints

- **No dual membership.** A country is in at most one faction. The Phase 2 draft cites the vanilla documentation: `can_leader_join_other_factions = yes` lets a faction leader join another faction, which **merges or destroys** the leader's old faction. It does not allow dual membership. [Not re-verified against the installed docs in this pass.] This is why the USA cannot lead NATO, SEATO, ANZUS and Rio as separate factions, and why those treaties are idea-based.
- **Leader can join elsewhere.** Templates with leader join `yes`: Viet Minh, State of Vietnam, KPA front, Karen, Arakan, generic, wartime coalition. Their leaders can therefore be absorbed into another faction. NATO, French Indochina and Peninsula Shield set `no`.
- **Subjects follow their overlord.** The engine pulls a member's subjects into the faction. NATO strips them back out in `NATO_sync_membership` unless they hold `nato_member`.
- **`create_faction` is obsolete.** Vanilla marks it obsolete (per the draft). Templates are the supported path. One legacy call remains (section 2.7).
- **Scripted adds bypass joining rules.** `add_to_faction` ignores the joining rules [INFERENCE, as stated in the draft]. Guards must therefore live in script, as in `coalition_add_member` and `NATO_join`.

## 4. Phase 2 design proposal (from the 2026-11-01 draft)

**Status: proposal.** The implementation status column reflects the code on 2026-11-26.

**Principle.** Model military commitments, not every organisation. Overlapping treaties are idea, decision and event packages. Standalone templates are only for compatible regional commands or explicit alternate-history alliances. Never dismantle NATO or the Warsaw Pact to populate a new bloc.

| Bloc | Proposed representation | Status now |
|---|---|---|
| SEATO (P1) | Treaty package. Manifest "Consultation Before Commitment"; goals: Bangkok liaison, combined exercise, regional assistance, Indochina response, sustained cooperation; dissolves 1977. | **Implemented** as a decision package (2.6). No faction. |
| Baghdad Pact / CENTO (P1) | Treaty package. Manifest "A Northern Tier of Security"; council, staffs, exercise, secretariat to Ankara, commitments; dissolves 1979. | **Implemented** as a decision package (2.6). |
| Rio Pact / TIAR (P1) | Treaty package with date-sensitive ratification roster (1949 ratifiers; ARG/BOL/ECU/PER 1950, GUA 1955, TRI 1967, BAH 1982); Article 20 consent. | **Implemented then removed** in `49a45bdcba` (perf). Only the USA 1980 focus `USA_FP80_Honor_the_Rio_Pact` remains; it does influence changes and references no Rio system. |
| GCC / Peninsula Shield (P1) | Regional command template; SAU as coordinating leader; from 1981. | **Implemented** as an engine faction (2.5). |
| Korean War UN Command (P2) | Theatre-command package, not a faction. | **Implemented** as a package (2.6). |
| Arab League defence, ANZUS, FPDA, Alcora, RSS, Sino-Soviet treaty (P2) | Treaty packages or conditional theatre templates. | Not implemented. No RSS or Rio template files remain in `common/factions/templates/` (the draft said empty owner files existed). |
| Balkan Pact, DPRK treaties, Frontline States, WEU (P3) | Treaty or cooperation packages only. | Not implemented. |
| NAM, OAU, ASEAN, Contadora, UAR | No faction. | NAM is represented by the `non_aligned_movement_member_idea` idea and the `faction_goal_cwic_non_aligned_unity` goal. Others are not implemented. |

**Generic template policy.**

| Proposal item | Status |
|---|---|
| Replace "Strength in Unity" (target 20 members) with "The Coalition's Common Undertaking" | Implemented (`faction_manifest_common_undertaking`). |
| Default short-term goal "Establish Joint Liaison" | Implemented (`faction_goal_establish_joint_liaison`). |
| Creation script picks one campaign objective | Implemented in `coalition_init`. |
| Optional "Conclude the Settlement" | Uses the `coalition_settlement_enabled` flag [INFERENCE that it gates the goal; the flag is cleared in `coalition_dissolve`]. |
| Migrate about 12 legacy `create_faction` calls | Done except `Emerging_Forces_Pact`. |
| Audit about 60 generic callers | Done in `aa044f728f`; they are now split between generic and wartime coalition. |

**Cross-bloc rules policy.**

| Proposal | Status |
|---|---|
| Lock NATO leadership to the USA | Implemented. |
| Separate Soviet lock for the Warsaw Pact | Implemented (also covers Cominform). |
| Theatre commanders preserved | Implemented for CEFEO via `change_leader_rule_indochina_cefeo_only`. |
| Consultation is not automatic war entry; no expulsion for starting a war; subjects and beneficiaries are not auto-members; same safeguards for scripted adds; small one-shot rewards; bookmark-correct initialisation | Partly reflected. The generic template still uses `dismissal_rule_offensive_war`, which contradicts "no automatic expulsion". |

## 5. Localisation and translation notes

**Baseline.** The handoff compared English loc against commit `5e16abf868`. `french/`, `japanese/` and `russian/` were not touched on the faction branch.

**English key changes vs `5e16abf868` (from the handoff, 2026-11-01).**

| File | Added | Removed | Text changed |
|---|---|---|---|
| `COMECON_l_english.yml` | 44 (`COMECON.400/500/501/510.*` events, `COMECON_CRISIS_*`, slider tooltips, `COMECON_MEMBER_SAT_LINE`, `COMECON_SOV_COST_LINE`) | 2 (`COMCECON_CRISIS_DESC_1` typo key, `COMECON_STEAL_FARM_TT`) | 0 |
| `IC_NATO_l_english.yml` | about 128 | 19 (Foretop exercise, issues 1-2, Norwegian mission, `twrTAnew.1/2.*`, `TA_*`) | 12 (`NATO_INTERVENTION.10/12-15/22.d`, voting lines, issue 10, Greek intervention desc) |
| `NATO_l_english.yml` | 2 (`non_aligned_movement_member_idea[_desc]`) | 2 (`call_nato_to_arms[_desc]`) | 0 |
| `SEATO_CENTO_treaty_l_english.yml` | 54 (new file) | 0 | 0 |
| `extracted_misc_l_english.yml` | 6 (`NATO_Aegean_Shield_Watch_tt`, `NATO_INTERVENTION.13.*`/`.32.a.tt` tooltips) | 0 | 6 (`NATO_INTERVENTION.10.a/b`, `.13.a/b`, `.14.t`, `.15.t`) |
| `factions_l_english.yml` | 5 (`coalition_founder`, `coalition_fund_liaison[_desc]`, `take_dien_bien_phu[_desc]`) | 2 (`NATO_Member`, `NATO_Member_desc`) | 0 |
| `factions_names_l_english.yml` | about 115 (faction, goal and manifest names) | about 2 | 0 |
| `focus_PER_50s_l_english.yml` | 0 | 0 | 1 (`CENTO_member`) |
| `focus_PRC_50s_l_english.yml` | 0 | 2 (`PRC_Become_COMECON_Observer[_desc]`) | 0 |
| `game_rules_l_english.yml` | 5 (`NATO_GREEK_INTERVENTION_RULE`, `RULE_OPTION_NATO_GRE_ALWAYS/NEVER[_DESC]`) | 0 | 0 |

**Renames and merges translators must mirror.**

- `NATO_Member` / `NATO_Member_desc` were folded into `nato_member`. `localisation/russian/factions_names_l_russian.yml:19` still has `NATO_Member`, which is now dead.
- `COMCECON_CRISIS_DESC_1` became `COMECON_CRISIS_DESC_1`.
- `call_nato_to_arms` was removed.

**Files added after the handoff, not in its tables.**

| File | Status | Keys |
|---|---|---|
| `GCC_Peninsula_Shield_l_english.yml` | Current | 52 |
| `UNCOM_treaty_l_english.yml` | Current | 45 |
| `RIO_treaty_l_english.yml` | Added, then **deleted** in `49a45bdcba` | 0; nothing to translate |

**Regenerating full key lists.** Run from the repo root:

```sh
git diff 5e16abf868 HEAD -- "Cold War Iron Curtain/localisation/english/" \
  | grep -E '^[+-]\s+[A-Za-z0-9_.]+:[0-9]? ' | sort
```

Keys that appear on both the `+` and `-` sides are text changes. Keys on only one side are additions or removals. A key that appears in different files across the two sides was moved.

## 6. Open items

1. `faction_template_state_of_vietnam` has no caller. Either use it or delete it (its goal `faction_goal_secure_independent_state_of_vietnam` goes with it).
2. The `Pathet_Lao_Faction` idea is never added. Either wire it to LAO as the UI identity the loc describes, or remove it.
3. `create_faction = Emerging_Forces_Pact` (`PRC_50s_Shared_Focuses.txt:5891`) still uses the obsolete effect.
4. `generic_factions.txt` keeps commented-out vanilla goals (`faction_goal_growing_the_faction`, `faction_goal_the_atomic_race` and others) that no longer exist after the pool prune. They are harmless, but uncommenting them would break.
5. `faction_template_generic` uses `dismissal_rule_offensive_war`, which contradicts the Phase 2 rule against automatic expulsion.
6. Russian `NATO_Member` loc is dead; the translation of `nato_member` needs checking in french/japanese/russian.
7. Remaining Phase 2 blocs (Arab League, ANZUS, FPDA, Alcora, RSS, Sino-Soviet, Balkan) are not started. The Rio Pact was cut for performance and would need a cheaper lifecycle before it returns.
8. The engine claims in section 3 come from the draft and were not re-checked against the installed game docs in this pass.
