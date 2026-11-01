# NATO and COMECON GUI rework: design and plan

## 1. Current state

### 1.1 NATO panel
Files: `common/scripted_guis/North_Atlanatic_Treaty_Organization.txt` (call it NGUI), `interface/TWR_TOR_ui.gui`, `common/scripted_effects/NATO_scripted_effects.txt` (NFX), `common/on_actions/NATO_on_actions.txt` (NOA), `common/decisions/IC_Nato_Decisons.txt` (NDEC), `events/NATO_Events.txt` (NEV).

| Element | Verdict | Evidence |
|---|---|---|
| Panel open via politics-list button 200 | Works | Toggle at `Parliament.txt:139-147`. `NATO_join` adds 200 to `country_politics_list` (NFX:149-154). `NATO_leave` removes it (NFX:200). |
| Visibility gate | Works | NGUI:7-11. `is_ai = no`, `has_idea = nato_member`, `show_nato_panel > 0`. |
| Member grid | Works | NGUI:196-201 reads `NAT.NATO_member_countries`. Sort via `NATO_sort_membership` (NFX:119-136). It removes subjects from the array, so subjects cannot be members. |
| Member type icon (leader/major/minor) | Cosmetic | The icon comes from `is_major` or `NATO_major_member` (`NATO_scripted_localisation.txt:420-470`). The flag is never set: `NATO_become_major` is defined (NFX:244) and has no callers in common/events/history. |
| Three bars (military, political, espionage) | Mostly broken | See below. |
| Military bar 1-5 effects | Works, but only one real bar | Ideas at `Various_Scripted_GUI_Hidden_Ideas.txt:250-290` carry real modifiers. They are applied by `NATO_apply_military_effects` (NFX:301-352). |
| Political bar 1-5 | Cosmetic | `NATO_political_1..5_idea` have empty `modifier = {}` (ideas file :292-321). |
| Espionage bar 2-5 | Cosmetic | Only `NATO_espionage_1_idea` has a modifier (:323-329). 2 to 5 are empty. |
| Clicking a tier icon | Cosmetic | NGUI:95-139 only shows an idea tooltip. |
| Bar growth | Broken | See below. |
| Voting UI (current issue, vote icons, whip buttons) | Works mechanically, but nothing feeds it | See below. |
| Vote tally counters | Works | `NATO_total_votes` (`NATO_scripted_triggers.txt:14-55`). Majority is `members/2`, rounded. Any single "no" vetoes (NDEC:119). |
| Whip cost | Works | Factory-power ratio times 25 political power, with a PP deduction (NFX:77-117). |
| AI behaviour | Mostly inert | See below. |
| Missing textures | Broken | `error.log:3481-3484` reports `gfx/interface/NATO_gui/NATO_military_progressbar_bg.dds` and `NATO_political_progressbar_bg.dds` missing. `find` shows neither file exists in the mod. |

**Bar growth is broken.** The monthly tick (NOA:3-28) only increments the bars when `NOT (NAT.NATO_political_integration < 20)`.
- Startup sets political integration to 0 (`on_startup_defines.txt:2136`), so the gate never opens.
- The only political raisers I found are a Portugal focus (`POR_1950s.txt:2069`) and the +75 espionage Truman focus (`USA_Truman_1948.txt:33`).
- So the passive +0.25 never runs at start. Military sits at 45 and espionage at 25, and both change only through exercises and focuses.
- The espionage cap (NOA:17-22) is also inside that gate.

**Issues pipeline is mostly dead.**
- Only issues 3, 10 and 11 can start.
  - Issue 3 (accept an applicant) starts from `NATO_motion_to_join`, which only the 1980s CIA event `USA_1980s_CIA.txt:3153` calls.
  - Issues 10 and 11 start from the Greek and Albanian civil-war decisions (NDEC:342-455).
- Issue 1 (Norway) and the generic debug mission are commented out (NDEC:269-340). `NATO_issue_1_effect` and `NATO_issue_2_effect` (NFX:478-580) have no starter.
- `NATO_issue_2_effect` and `_1_effect` fire `twrta.2000`, `twrta.2001` and `twrTAnew.1`. Only the namespaces exist in NEV:4-5; no such events exist in `events/`.
- Issue 11 grants `Volunteer_Allowance^KOA` and nothing else. Issue 10 fires GRE `NATO_INTERVENTION.10`.
- NATO "major" is never meaningfully distinguished from `is_major`.

**AI voting is inert.**
- AI vote intention is random uniform -10..10 for non-leaders (NDEC:386-392). `NATO_vote_neutral` has `add = 10` when intention is 0 (NDEC:83-90).
- The mission needs positives at or above half, and no vetoes (NDEC:97-123). A random member below 0 vetoes.
- Timeout costs -5 political integration (NDEC:167). That is the only downside of a failed vote.
- The AI whip (NDEC:185-231) only fires for intention above 9.999, and only the leader's `NATO_vote_intention = 10` triggers it.

**Other defects.**
- `twrta.1013` (NEV:1013-1027) uses `subtract_from_variable = { ... = -2 }` inside `effect_tooltip`. It is a double negative that executes nothing. The real -2 is in `twrta.1011` (NEV:810).
- `twrta.1005` (NEV:161-191) is the only periodic driver: a 182-day loop that offers the exercise menu at military ≥ 50. It is the only live gameplay loop (4 exercise types, participation counted, +0.5 or +1 or -2 military).
- Faction template `faction_template_nato` is `visible = no` and USA-only leader (`USA_North_Atlantic_Treaty_Organization.txt`). The faction goals file has no NATO entries (I found NATO only in `faction_manifests.txt`).
- Whip cost uses `NAT.NATO_member_countries` and `num_of_factories`. It was designed for peers, not for a USA-dominated alliance.

**Net:** one working loop (exercises, military bar, military ideas), a voting engine with no inputs, and two bars with no effects.

### 1.2 COMECON window
Files: `common/scripted_guis/COMECON.txt` (CGUI, 1515 lines), `interface/COMECON_Redux.gui` (3126 lines), `COMECON_Effects.txt` (CFX), `common/ideas/COMECON.txt`, `common/dynamic_modifiers/IC_Comecon_Modifiers.txt` (CMOD).

| Element | Verdict | Evidence |
|---|---|---|
| Opening the window | Works | Button 201 (`Parliament.txt:149-165`). It is gated by `SOV` having a non-empty `COMECON_MEMBERSHIP` (`on_startup_defines.txt:3365-3373`). `SOV_open_comecon_window` (CFX:35-41) selects the first member. |
| Member list, per-member selection | Works | CGUI:1382-1513. Duplicated refresh logic lives in the click effects and in `comecon_refresh_target` (CFX:43-65). |
| Stats pane (consumer goods factories, research speed, construction speed, efficiency cap, PP gain) | Works, read-only | Computed from the target's modifiers. |
| Expenditure pie | Cosmetic | 31 pie-slice widgets (`COMECON_Redux.gui:1249-1459`), `create_pie_chart`. Not used for decisions. |
| 6 sliders (Eco, Con, Pro, Res, Mil, Trade) | Cosmetic for five, partial for Trade | CGUI:1129-1140 only edit `COMECON_TARGET.*_COMECON_RATE`. Grep across `common/events/history/interface` finds no reader of `ECO/CON/PRO/RES/MIL_COMECON_RATE` outside CGUI. Only `TRADE_COMECON_RATE` is read: `IncomeGenerator.txt:1753-1769` sets a bilateral trade-cost factor of `1 - 0.025 × clamp(max(a,b), 0, 6)`. |
| Dynamic modifier `comecon_member` | Dead | CMOD:1-35 reads `COMECON_*_BONUS` variables. They are only ever written by the GDR card game (`CWIC_GDR_Card_Game_Effects.txt:1113, 3324, 4069`), never by the sliders. Nothing calls `add_dynamic_modifier = comecon_member`. The idea `comecon_member` in `zzz_generic.txt:1552` is empty. |
| `increase_comecon_value_effect`, `decrease_comecon_value_effect`, `comecon_influence_invest_effect`, `comecon_influence_steal_effect` | Dead stubs | CFX:25-30 are empty. `comecon_influence_invest_effect` is still called from every Build click (e.g. CGUI:874). |
| Build Farm/Arms/Factory/Dockyard | Works | Charges SOV `currentMoney` (-12, -18, ...) and starts a mission (CGUI:864-893, 908-938, 958-987, 1002-1031). Completion adds the building (`_generic_decisions.txt:3595-3630`, 3677+). SOV `COMECON_INVESTMENT_CONSUMER_GOODS` +5, paid back at mission end. Duration shrinks with `ECO_COMECON_RATE`, which is the only effect of that slider. |
| Seize Farm/Factory/Dockyard | Stub | `Seize_Farm_click`, `Seize_Factory_click`, `Seize_Dockyard_click` are empty (CGUI:894, 988, 1032). Seize Arms sets a prompt. Dockyard/Factory/Arms rental windows exist (CGUI:1-361) but have no live way in. |
| Emphasis (5-year timed idea) | Works | CGUI:897-907, 947-956, 991+. Ideas in `common/ideas/COMECON.txt:17-77`. |
| Promote Friendly Parties | Works | CGUI:1053-1066. Costs 100 PP and 2 money; gives `COMECON_Political_Support` for 365 days (`communism_drift 0.001`, `political_power_gain 0.1`). |
| Subsidize Expenses | Flag only | CGUI:1067-1078 sets `Soviet_Subsidies` and a prompt flag, with `#Add Influence Bit`. Nothing consumes `Soviet_Subsidies` outside CGUI (grep found none). |
| Demand Military Access | Works for AI (50% coin flip); human target gets a prompt flag (CGUI:1079-1114). |
| Kick from COMECON | Works (CGUI:1115-1123) | Removes the array entry and idea. |
| Membership data | Wrong at start | SOV history (`SOV - Soviet union.txt:1335-1348`) puts BUL, CZE, ALB, HUN, POL, ROM in the array. There is no date guard. DDR joins by focus (`GDR_Initial_Political.txt:1428-1436`). Nothing models Albania leaving (1961), or the later joins: Mongolia (1962), Cuba (1972), Vietnam (1978). `[INFERENCE]` the 1980.1.1 blocks at SOV:1610 and :3540 have no `COMECON_MEMBERSHIP` writes (grep of `history/` finds none outside SOV:1343-1348), so the 1980 start reuses the 1949 list. Verify in game. |
| Targeted idea ladder `comecon_level_N_<tag>` | Mostly dead | `common/ideas/COMECON.txt:100-896` are per-country `trade_cost_for_target_factor` ideas. Only `comecon_level_1/2/3` is read, by `Resource_Efficiency.txt:97-121`. |
| Per-member portrait triggers | Cosmetic | CGUI:379-400 matches hardcoded leader names, including non-ASCII ones such as "Mátyás Rákosi" and "Ernő Gerő". Several are for CZE/HUN/KRD/MEX leaders that may not be COMECON members. |
| Logging | Error noise | `error.log` shows `Unknown promotion "COMECON1"` repeatedly (loc text variable that is not a promotion). `PRC_Become_COMECON_Observer` is an invalid focus for an AI strategy. |

**Net:** a good-looking dashboard whose only live levers are four building-construction missions, an idea toggle, a PP-for-drift buy, and trade cost. The five main sliders do nothing. There are no crises, no member agency, and no 1980 state.

## 2. Design goals

### NATO
- **Who plays it:** USA (leader) sets the agenda and spends influence. Members (UK, FRA, GER, CAN, ITA, TUR, GRE and so on) vote, whip, veto, and make demands. Non-USA players need real actions, not only voting.
- **Decisions the player should face:**
  1. Which issue to put forward, and whether to spend PP/whip to pass it.
  2. Burden-sharing: how much to ask members to spend. This is the lever for the bars.
  3. How to handle internal disputes: Suez 1956, France leaving the integrated command 1966, Greece/Turkey and Cyprus 1974, the Euromissile deployment 1979, and the 1950s German rearmament debate.
- **AI behaviour:** AI members vote by a weighted score from ideology, relations, the issue's cost, and threat level, not a random number. The AI leader proposes the next historical issue on a date or condition.
- **Bars have to matter:** every tier should unlock something concrete for members (a decision, a focus, a modifier, an upper bound).

### COMECON
- **Who plays it:** SOV is the patron. Members (POL, HUN, CZE, DDR, ROM, BUL, ALB until 1961) are not passive. They have their own requests and crises.
- **Decisions:** how hard to push subsidies and integration (cost to SOV) against loyalty and unrest (risk to members).
- **Core loop:** the Soviet cost of subsidising is real, and the member's dependency and satisfaction move with each slider. Crises fire when satisfaction falls.
- **AI behaviour:** AI SOV runs a simple policy; AI members react to the same variables.

## 3. NATO rework

### 3.1 Fix the broken loop (precondition for everything else)
1. Remove the political gate on bar growth in NOA:8-23. Replace it with one condition: no more than three major NATO-hostile events this month (or simply none).
2. Move the cap of 100 to a clamp for all three bars (currently espionage only, NOA:17-22).
3. Fix `twrta.1013` to put the real `add_to_variable -2` effect in the option, not the tooltip.
4. Supply the missing `.dds` files or point the gfx entries at existing assets. First `find -iname "NATO_*progressbar*"` (case-sensitivity gotcha), then check `interface/*.gfx` for a vanilla fallback.

### 3.2 Redefine the three bars

| Bar | Raised by | Lowered by | Unlocks for members |
|---|---|---|---|
| Military integration | Exercises (existing `twrta.1005-1013`), joint operations (issue 10/11 style), members above a spending threshold, Korean War for USA/UK/FRA/CAN | Low participation (-2, existing), member leaving, a disputed issue | Existing military ideas 1 to 5 (keep), plus: tier 3 unlocks a "combined command" decision for the leader; tier 5 unlocks the "Rapid Response Force" |
| Political integration | Issues passed, joint statements, accession, EEC-like events | Failed votes (-5 existing), vetoes, member-state crises | Replace the empty ideas with real ones: tier 1 `stability_factor`; tier 2 relation/trade bonus among members; tier 3 `ai_get_ally_desire`; tier 4 lowers faction-leader dependency; tier 5 shared-research bonus |
| Espionage | Gladio, the CIA focus, joint ops | Leaks (a Soviet coup attempt), failed ops | Fill tier 2 to 5: intel from partners (`intel_network_gain`), operative slots, anti-coup defence; tier 5 reveals one Warsaw Pact member's capabilities |

Use the existing comment block (NGUI:205-224) as the names for tiers: SHAPE, Secretary General, Regular Exercises, STANAG, Rapid Response; Gladio, Allied Clandestine Committee, SACLANT, LRRP School, Fusion Centre; Science Programme, Atomic Development Community, Bank, Free Trade Area, Common Currency. Gate the last political tiers behind a historical-event or an alt-history condition so they remain hard.

### 3.3 Issues pipeline
Add to NFX a single dispatcher effect (`NATO_start_issue = yes` taking an `issue_id`) that sets `NAT.NATO_issue_id`, seeds each member's `NATO_vote_intention` from rules, and calls the existing `NATO_initialize_voting`. Reuse the existing `NATO_issue_<id>_effect` / `NATO_issue_<id>_desc` meta-effect naming (NDEC:134-139, NGUI:155-162). Seed intention with a formula, not `randomize_variable`: base 0, add for same ideology, add for relation above a threshold, subtract if the issue costs the member (their cost is the issue's own trigger), and use the leader as 10.

**Starter:** one pass of a monthly on_action checks each issue's trigger. Only one issue is active at a time (`NOT has_variable = NATO_issue_id`).

Historical issue list (each needs: trigger, vote rule, outcome). IDs 3, 10 and 11 are already used; 1, 2 exist as dead effects.

| ID | Issue | Window and trigger | Vote notes | Outcome effects |
|---|---|---|---|---|
| 3 | Accept an applicant | Applicant starts it (existing `NATO_motion_to_join`); historical GRE and TUR 1951-52, GER 1955, ESP 1982 | The applicant's neighbours can veto (GRE/TUR) | `NATO_join`, small bars delta (existing) |
| 1 | Norwegian intervention | Existing effect NFX:478-509. Fold in or drop; it targets an event that is not in the files | | |
| 2 | Operation Foretop exercise | Existing NFX:511-580. Needs `twrta.2000/2001`, or drop the events and keep only the idea | | |
| 4 | Korean War UN contribution | 1950.6 | Wide majority | Members send divisions/volunteers; military +3 |
| 5 | German rearmament and accession | 1950-1955 | FRA is the hard vote (EDC fails 1954); fallback WEU | GER joins; political +; Warsaw Pact trigger |
| 6 | Suez: back the invasion or condemn | 1956.10 | UK/FRA for, USA against | Passing = bars up for the aggressors only, but USA spends PP; failing = UK/FRA stability hit, political bar -5 |
| 7 | Nuclear sharing (Multilateral Force) | 1960-64 | FRA against | MLF fails = FRA flag for exit path |
| 8 | France leaves the integrated command | 1966.3 | Not a vote; an event on FRA's choice | Remove FRA from the military bar sum (or halve its contribution) while staying in the faction |
| 9 | Harmel Report: detente or defence | 1967 | Majority | Political bar +; lowers Warsaw Pact tension |
| 12 | Greece/Turkey Cyprus crisis | 1974.7 | Both parties lock each other out | GRE withdraws from the integrated command (1974-80); bars -; Soviet gain |
| 13 | Dual-track decision (Pershing II / GLCM + talks) | 1979.12 | Members with strong left parties are against | Passes = missiles + military bar +, domestic unrest events in NED/GER/ITA/BEL; fails = military -, SOV bonus |
| 14 | Spain accession | 1982 | | Only if the world reaches that state |
| 15 | Out-of-area (Lebanon, Gulf) | 1980s | Always fails or splits | Teaches the veto |

Existing 10 (Greek civil war) and 11 (Albania) stay as 1949-50 issues; they are the only ones the 1949.5.23 start can reach by default.

Failure outcomes need cost beyond -5 political: set `has_been_whipped` grievances, a "dispute" flag lasting 180 days that blocks new issues, and a loyalty drain for the member that was overruled.

### 3.4 Member roles
- **Roles:** leader (USA), major (the six by `is_major` or industry rank), minor (the rest). Set `NATO_major_member` explicitly through `NATO_become_major` for UK, FRA, GER (post-1955) and CAN. Right now it is never called.
- **Weighting:** keep one-member-one-veto for accession; make non-accession votes weighted (leader 3, major 2, minor 1) by replacing `NATO_total_votes` counts. This keeps the whip UI meaningful. `[INFERENCE]` UI counters (positive, negative, neutral) can show weighted totals without changing `.gui`.
- **Non-USA actions** (as targeted decisions, reusing the `NATO_vote_*` category):
  - Propose an issue (UK/FRA/GER only, major role), limited to issues whose trigger is true for them (Suez for UK/FRA).
  - Pledge forces (gives bars + for PP/manpower).
  - Refuse burden-sharing (saves cost; -military bar, flags a grievance).
  - Demand consultation (small political bar change; the leader must answer).
- **USA actions:** put an issue forward, whip (existing), grant aid (Marshall-style), and escalate. Each should cost PP; the whip already does.
- **AI:** score decisions with `ai_will_do` from the same formula as the vote seed.

### 3.5 Cut
- The dead debug mission and the duplicate commented blocks in NDEC (lines 233-340).
- `NATO_leader_icon` and `NATO_member_icon` empty properties (NGUI:188-193) unless art needs them.
- `control_my_states` at the top of NFX:1-7, which transfers states to the actor and is unrelated.
- The espionage-only clamp in NOA, replaced with the common clamp.
- Empty tier ideas: do not leave them empty; fill them or lower the tier count. Five tiers on three bars is 15 icons; if fewer than 15 real effects exist, shrink the UI.

## 4. COMECON rework

### 4.1 Core economic loop
Add two per-member variables and one global: `COMECON_dependency` (0-100, how reliant the member is on SOV), `COMECON_satisfaction` (0-100, how much it likes the arrangement), and SOV's `COMECON_cost` (monthly). Reuse `SOV.currentMoney` (already used by the Build clicks) for SOV cost, and `COMECON_TARGET`, `COMECON1`, `comecon_refresh_target` (CFX:35-65) for selection.

| Slider | Cost to SOV | Gives the member | Gives SOV | Effect on satisfaction / dependency |
|---|---|---|---|---|
| Economic (ECO) | Money/month × level | Consumer goods, food, `COMECON_NEEDS_DISCOUNT` | Faster investment missions (existing) | Satisfaction + , dependency + |
| Construction (CON) | Money + construction slots | `COMECON_CONSTRUCTION_BONUS` | Control over where factories go | Dependency + |
| Production (PRO) | Money | `COMECON_PROD_*_BONUS` | Standardisation (arms licences) | Dependency + |
| Research (RES) | Research speed/tech sharing | `COMECON_RESEARCH_BONUS` | Access to member research | Satisfaction ± by level |
| Military (MIL) | Equipment | `COMECON_COMMAND_POWER_BONUS`, `WAR_SUPPORT` | Joint command, basing | Dependency + , satisfaction - at high level |
| Trade (TRADE) | Trade income (existing factor) | Cheaper bilateral trade (existing `ic_bloc_pair_factor`) | Cheaper trade, loyalty | Satisfaction + |

**Wiring:** write one effect `COMECON_apply_member_modifiers` (in `COMECON_Effects.txt`, the owner file) that sets `COMECON_*_BONUS` from the six sliders and applies the existing dynamic modifier `comecon_member`. It runs on slider click and on the monthly tick. Per the GOTCHAS, no new script file: add it to CFX and a monthly on-action to the existing SOV monthly block. Calibrate bonuses from the numbers already in CMOD (for example `COMECON_NEEDS_DISCOUNT` is already shaped for 0 to 6 levels).

**Cost to SOV:** monthly `COMECON_cost = Σ level × weight × member GDP ratio`. Subtract it from `currentMoney`, and show it in the existing stats pane. If SOV cannot pay, sliders fall automatically (the economy decides, not the player).

**Satisfaction drift:** `satisfaction += f(ECO, TRADE, RES) - g(MIL, oversight)` monthly, plus event deltas, minus a nationalism term for HUN/POL/ROM/ALB.

### 4.2 Crisis system
A monthly check per member: if `COMECON_satisfaction < threshold` and a historical window is open, fire the crisis event chain. Use `fire_only_once` carefully: one event per country (GOTCHAS), so crisis events must be keyed per tag with distinct ids.

| Crisis | Window | Trigger | Player choice (SOV) | Outcomes |
|---|---|---|---|---|
| East Germany 1953 | June 1953 | DDR satisfaction < 40 and SOV leadership in transition | Send tanks / concede on norms | Crush: stability + for DDR regime, satisfaction -20, dependency +. Concede: satisfaction +, SOV prestige -. |
| Poland and Hungary 1956 | Jun to Nov 1956 | HUN and POL satisfaction < 35. Reuse `Hungarian_Revolution.txt` (HUNGARIAN_REV.1-24, existing 24-event chain) | Intervene / negotiate | Intervene: Hungary occupied, WP cohesion + , world opinion -. Negotiate: Gomulka-style concessions, ROM/BUL satisfaction + , SOV dependency - . |
| Czechoslovakia 1968 | Jan to Aug 1968 | CZE satisfaction < 35 and reform leader (Dubcek) | Invade (WP) / tolerate | Invade: reuse existing CZE events. Tolerate: CZE leaves the dependency ladder; a cascade check for POL/HUN. |
| Poland 1970 | Dec 1970 | POL satisfaction < 40 and ECO level low | Subsidise / repress | Subsidise: Gierek-style loans, dependency +. Repress: strikes spread. |
| Poland 1980 | Aug 1980 | POL satisfaction < 35 (Solidarity) | Pressure Warsaw to impose order / threaten invasion / accept | Martial law path: POL regime stays, WP cohesion -; accept: SOV sees cascade risk. The 1980 start must enter here with satisfaction already at about 30. |
| Albanian break | 1961 | ALB satisfaction < 30 | Concede / let go | ALB removed from the array (in step with the Sino-Soviet split). |
| Romania independent line | 1964 onwards | ROM satisfaction < 45 | | Reduced MIL level for ROM, loses WP military access. |

Crises add a `COMECON_crisis_active` flag on the member and a countdown; the player's sliders change the odds. Defaults: AI SOV resolves each crisis historically with a modest random deviation (decision weights from satisfaction, the leader's ideology and the current domestic situation).

### 4.3 Members and AI
- **Member actions** (new targeted decisions, owned by the member): request subsidy (raises ECO, costs satisfaction if refused), demand price relief on oil (TRADE), request troops withdrawn (MIL), seek observer-only status (reduces all levels), seek exit.
- **AI members:** `ai_will_do` weighted by satisfaction and dependency. A member under 25 satisfaction with no crisis open requests exit; the exit goes through the same Kick/Leave path as `COMECON_Kick_From_click` (CGUI:1115-1123), which removes the array entry and the idea.
- **Joins/leaves by date:** Albania out 1961, Mongolia in 1962, Cuba in 1972, Vietnam in 1978, and DDR already in by 1949 history (today only via focus). Add these with a dated on-action `add_to_array = { SOV.COMECON_MEMBERSHIP = X.id }` and the variable `COMECON_MEMBERSHIP_STATUS`. Observers (PRC, as the dead AI strategy implies; Yugoslavia, Finland) as a status value 2.
- **1980-start state:** SOV array must be written in the 1980 block: BUL, CZE, HUN, POL, ROM, DDR, MON, CUB, VIE (no ALB). Set per-member sliders and satisfaction by history: POL very low (about 25-30, the Gdansk strikes), HUN high (about 60, goulash communism), ROM medium-low (about 40), CZE about 45, DDR about 55, BUL about 65, CUB about 70 and heavily dependent. The 1949 start begins with satisfaction about 55 and dependency about 80 for the six members.

### 4.4 What COMECON members can do in the GUI
The window currently opens only for SOV (gate at `on_startup_defines.txt:3365-3373` is `tag = SOV`). Add a member view that reuses the same window with `comecon_sov_selected` pointing at the member itself (`COMECON_Large_Flag_click`, CGUI:857-863 already supports selecting a country): members see their own satisfaction/dependency, their slider levels as received, active crisis, and three actions (ask for subsidy, ask for exit, ask for trade deal). Members cannot change sliders; they file a request that SOV accepts or refuses (AI SOV decides by an `ai_will_do`).

### 4.5 Cut
- Seize Farm/Factory/Dockyard stubs (CGUI:894, 988, 1032) and the Dockyard/Factory/Arms rental windows (CGUI:1-361), unless they are to be wired to a real "seize assets" crisis outcome. Decide this first; the rental windows are 360 lines with no entry point.
- Empty effects in `COMECON_Effects.txt` (lines 25-30): implement or delete.
- The expenditure pie (31 widgets in `COMECON_Redux.gui:1249-1459`) and its `create_pie_chart` calls; replace it with the dependency/satisfaction block.
- `comecon_level_N_<tag>` idea ladder (`common/ideas/COMECON.txt:100-896`, about 800 lines): only levels 1 to 3 feed `Resource_Efficiency.txt`. Replace it with one dynamic modifier driven by TRADE.
- Hardcoded leader-portrait triggers for non-members (MEX, KRD) in CGUI:392-400.
- The `COMECON1` text variable producing `Unknown promotion` errors, and the dead `PRC_Become_COMECON_Observer` AI strategy reference.

## 5. Phased plan

| Phase | Work | Effort | In-game checkpoint |
|---|---|---|---|
| 0 | Restore the two missing NATO `.dds` assets or repoint the gfx. Fix `twrta.1013`. Remove the NATO political gate (NOA:8-23). | S | Start 1949.5.23 as USA. Run 12 months with `set_variable` debug on the NATO variables: all three bars move. `error.log` has no `NATO_gui` texture lines. |
| 1 | NATO bars: fill empty political and espionage ideas; make `NATO_become_major` called for UK, FRA, GER, CAN. | M | Open panel (button 200). Tier tooltips show real modifiers. Major icons show for the right members. |
| 2 | NATO issues dispatcher and formula seeding. Add issues 4, 5, 6, 8, 9, 12, 13 with the events needed. Replace dead `twrta.2000/2001` and `twrTAnew.1` references. | L | Use `event` console to start each issue. Vote, whip, pass, fail, check the veto path and the cleanup (`NATO_cleanup_voting`). Do an AI-only run: AI members cast sensible non-random votes. |
| 3 | NATO member actions and weighted votes. | M | As UK, propose Suez at 1956.10 and observe a vote with USA against. |
| 4 | COMECON wiring: `COMECON_apply_member_modifiers`; costs to SOV; satisfaction/dependency variables; fix the monthly drift. | M | Set ECO slider 0 to 6 on one member. The member's stats pane and `modifier@` values change. SOV `currentMoney` drops. Check the 1980 start for the same. |
| 5 | COMECON crisis chain. Reuse `Hungarian_Revolution.txt`, `Czechoslovakia_1950s.txt`, `GDR_1950s_Events.txt`, `Poland_1950s_Events.txt` as outcome events; new triggers and decisions only. | L | Force satisfaction low per member and check each crisis fires once per game for the right tag. |
| 6 | Membership by date (ALB out, MON, CUB, VIE in) and the 1980 start state. Member view of the window. | M | Start 1980.1.1 as POL and as SOV: window opens, member list is correct, POL crisis is imminent. |
| 7 | Cut list: stubs, rental windows, pie chart, ideas ladder, portrait triggers. | S | `error.log` has no new missing-element errors. The `.gui` still loads, window opens, nothing else broke. |
| 8 | AI behaviour pass: NATO leader proposals, member votes, COMECON AI decisions. | M | One-year AI-only run with `observe`, checking that issues start and that COMECON crises trigger without player input. |

**Order constraints:** 0 before everything; 4 before 5 (the crisis needs the satisfaction variable); 2 before 3; do not start 7 until 4 and 5 have chosen what to keep.

**Risks and gotchas:**
- No `>=` in `check_variable` (the existing NDEC:113 uses `compare = greater_than_or_equals` with `var/value`, which is the long form; do not copy it into a short form).
- One event id per country: do not use `fire_only_once = yes` on a crisis sent to several tags.
- Localisation in ASCII, English only, with BOM. Existing leader-name triggers use non-ASCII names; do not add more of those.
- No comments in code and no new script files: put NATO logic in the existing NFX/NDEC/NOA, COMECON logic in CFX and the existing COMECON GUI file.
- Grep before defining any new effect or variable name.
- `NAT` is used as a scope throughout. I did not find where it is defined, so do not change it; reuse as is.

**Open questions for Main:**
1. Whether the unused rental windows should be wired to a seize-assets crisis outcome or deleted.
2. Whether non-USA NATO members should be able to propose issues, or only vote and whip.
