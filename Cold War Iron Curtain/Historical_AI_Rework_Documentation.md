# Historical AI Rework — USSR & USA (1949–1960s)

Pass 1 of the historical-path rework: make USSR and USA AI actually follow history on historical mode, and give players game rules to force election/event outcomes per country.

## What was broken

1. **`common/ai_focuses/USA.txt` was dead code.** It held a 212-line curated historical focus list (`ai_historical_focus_list_USA`) that nothing in the game ever referenced — `ai_focuses` files only support research-weight `ai_focus_*` blocks. USA had *no* working strategy plan at all, so its focus picks were effectively random.
2. **`USA_historical_strategy_plan.txt` and `USA_alternate_strategy_plan.txt` were empty files.**
3. **Two broken focus IDs in `SOV_historical_strategy_plan.txt`** (wrong casing, silently skipped by the AI):
   - `SOV_establish_diplomatic_relations_with_west_germany` → `SOV_Establish_Diplomatic_Relations_with_West_Germany`
   - `SOV_send_back_german_pows` → `SOV_Send_Back_German_PoWs`
4. **SOV plans stopped dead at 1957.** Nothing steered the AI through the Khrushchev tree (1956–1964).
5. **1968 Democratic nomination (`usa.19681`) had no historical weighting.** Humphrey had no `ai_chance` (weight 1) vs RFK at 30 — the AI nominated RFK in the vast majority of historical runs.
6. **Khrushchev's 1964 removal (`soviet_leader_change.2`) was a coin flip.** When the Seven-Year Plan partially succeeded, both the Brezhnev option and the Khrushchev-stays option were valid with no `ai_chance` at all.
7. **Election events generally:** ahistorical options kept their base weights on historical mode (e.g. MacArthur 70 vs forced-Ike in 1952 general), so "historical" runs still diverged with low but real probability every election.

## What was added

### Strategy plans
- **`USA_historical_strategy_plan.txt`** (new, 7 plans):
  - `usa_historical_50s` — Truman agenda + shared 50s trees (Korea/Suez/Hungary reactive focuses at top of list), 1949–1961.
  - `usa_historical_eisenhower_1952` / `usa_historical_eisenhower_1956` — Ike term agendas, keyed to `president_eisenhower` flag (so they also run when a game rule forces Ike in ahistorical games).
  - `usa_historical_jfk` (flag `jfk_60`), `usa_historical_lbj` (flag `lbj_64`), `usa_historical_nixon_1968` (flag `nixon_68`).
  - `usa_historical_60s` — shared 60s military + foreign policy trees with every mutually-exclusive fork resolved historically (Gulf of Tonkin → Vietnam War, DMZ crisis restrained, Reject Containment → Vietnamization → Beijing outreach → Shanghai Communiqué, Tar Baby limited, XB-70 cancelled).
- **`SOV_historical_strategy_plan.txt`** — added `soviet_historical_khrushchev_internal` (1956–1964, enabled by `gensec_khrushev` + the `SOV_internal_ai_behavior` rule): full Khrushchev-tree order following the real timeline (destalinization → anti-party group → Zhukov's removal → XXI Congress/Seven-Year Plan → anti-religious campaign → XXII Congress → 1962 reforms → `SOV_review_khrushchev_plans`). Mutually exclusive picks: traditional aircraft over flying submarine, Tu-114 campaign over MiG-15, high-speed interceptors over jet interceptors.
- `common/ai_focuses/USA.txt` cleaned to a pointer comment; `USA_alternate_strategy_plan.txt` documents that alternates are driven by the election rules.

### Game rules (`common/game_rules/00_game_rules.txt`)
| Rule | Options |
|---|---|
| `USA_1952_elections` | Default, Eisenhower (hist), Stevenson, Kefauver, Harriman, Russell, MacArthur (needs dismissal chain) |
| `USA_1956_elections` | Default, Eisenhower (hist), Stevenson, Kefauver, Harriman |
| `USA_1960_elections` | Default, Kennedy (hist), Nixon, Humphrey |
| `USA_1964_elections` | Default, Johnson (hist), Humphrey, Goldwater, Rockefeller, Nixon |
| `USA_1968_elections` | Default, Nixon (hist), Humphrey, RFK, Reagan, Wallace, Rockefeller |
| `SOV_1964_presidium` | Default, Brezhnev (hist), Khrushchev stays |

English localisation added in `localisation/english/game_rules_l_english.yml` (other languages fall back to English keys).

### Event wiring (70 `ai_chance` blocks rewritten)
- `events/USA.txt` — all nomination + general election events 1952–1968 (`usa.1000/1100/1200/1001/1002`, `usa.1956/19562/19563`, `usa.19601/19603`, `usa.19641/19642/19643`, `usa.19681/19682/19683`). Pattern per option:
  - existing `is_historical_focus_on` modifiers now gated on rule = `DEFAULT` (so a forced rule beats historical mode),
  - `factor = 1000` when the option's candidate is forced by the rule,
  - `factor = 0` when a different candidate is forced.
  - Fixed on the way: 1968 Dem nomination now historically weighted (Humphrey); Russell/Harriman keep their "can't win the general" behavior on Default but win when forced.
- `events/SovietUnion_Historical_Events.txt` — `soviet_leader_change.2` options now have `ai_chance` wired to `SOV_1964_presidium` + historical mode (Brezhnev on historical).

## How to test
1. Historical focuses ON, all rules Default, observe USA: Truman agenda → Ike '52/'56 → JFK '60 → LBJ '64 → Nixon '68; USSR: Stalin path → Khrushchev → Brezhnev in Oct 1964.
2. Set `USA_1952_elections = Stevenson` on a non-historical run: Stevenson must be nominated and win, and load `USA_Stevenson_1952`.
3. Set `SOV_1964_presidium = Khrushchev Stays`: requires the Seven-Year Plan check to pass (AI must have built enough refineries/factories/office parks — see `SOV_review_khrushchev_plans`); if the plan failed outright (`SOV_KHR_Loss`), only the Brezhnev option is valid regardless of rule.

## Pass 2 — alternates, precondition wiring, old-content cleanup

### Broken things found and fixed
1. **`usa.19684` (RFK at the California primary) was a dead event** — defined but never fired by anything, so `rfk_dead` was never set and RFK never died. Now fired from `ic_pulse` (June 4 – July 15, 1968) and its two options are wired: historical/Default → assassinated, `USA_1968_elections = RFK` → survives.
2. **`USA_ALBANIAN_SUBVERSION` rule was half-wired** — only the ZOG-advice option did anything (startup set subversion chance to 1). The British-advice ("Albania Unsubverted") option now sets the chance to −10 at startup so the `albania.5` check (needs > 0.30) can never pass.
3. **The Beria alternate plan didn't steer the Troika era at all** — it ended at the Troika focus, leaving the AI free to stumble into `SOV_arrest_beria`/`SOV_pospelov_commission` (the Khrushchev route) by `ai_will_do`. It now walks the full Beria conspiracy branch (`SOV_delay_presidiums_countermeasures` → Merkulov/Kobulov/SSR MVD chain → Malenkov as First Secretary → state of emergency → Merkulov commission → 20th Congress → `SOV_Beria_Malenkov` tree).

### Precondition events wired to rules
- **MacArthur '52**: `MacArthur_Dismissal.8` (fade away vs stay political, was a bare 80/20) and `MacArthur_Dismissal.18` (candidacy announcement, was 50/50) now obey `USA_1952_elections`: forced-MacArthur games take the political path and set `enable_macarthur`/`MacArthur_1952_Enabled`; historical/Default games deterministically fade him away.
- **RFK '68**: see `usa.19684` above.
- **JFK/LBJ '64**: no wiring needed — the Dallas events (`swf.1011`, and `swf.1000` for a Nixon 1960 presidency) fire unconditionally, so `lbj_63` always exists on a JFK path; the `HUMPHREY_1964` option is for non-JFK 1960 outcomes, as its description states.

### Alternate strategy plans (new)
- **`USA_alternate_strategy_plan.txt`** — 38 agenda plans, one per alternate presidential tree ('52 through '68: Stevenson, Kefauver, Harriman, Russell, MacArthur, Dewey, Warren, Stassen, Truman '52, Eisenhower-DEM, Nixon '56/'60/'64, Halleck, Martin, Humphrey '60/'64/'68, Goldwater '64/'68, Rockefeller '64/'68, RFK, Reagan, Wallace, Johnson '68). Each enables on `has_focus_tree = <tree>`, so it applies however that president won — game rule, random deviation, or player handover. Plus three shared-60s foreign-policy plans for ahistorical games:
  - `usa_ahistorical_60s_hawk` (Goldwater/Reagan/Wallace): Continue Containment → Double Down → Cambodia intervention → Veto PRC; DMZ retaliation with limited escalation; extensive southern-Africa approach.
  - `usa_ahistorical_60s_dove` (RFK): Restrict Involvement, Reject Containment → withdrawal, Outreach to Moscow, PRC admitted.
  - `usa_ahistorical_60s_moderate` (all other ahistorical presidents): mirrors the historical picks so non-historical runs are not rudderless.
- **`SOV_alternate_strategy_plan.txt`** — Beria plan extended through the Troika (see above), plus three continuation plans enabled by `has_focus_tree`:
  - `soviet_ahistorical_beria_gensec` — full `SOV_Beria_Malenkov` tree order (134 focuses), to 1965.
  - `soviet_ahistorical_kaganovich` — `SOV_Kaganovich` tree after Stalin's retirement (142 focuses; picks Kitov's Red Book over deeper self-management at the one fork), to 1965.
  - `soviet_ahistorical_khrushchev_stays` — `SOV_Khruschev_Extended` tree when Khrushchev survives October 1964 (59 focuses), to 1972.

### Old rules review (all USA/SOV rules audited)
Every defined USA/SOV rule is referenced and functional after this pass: `USA_Stance_on_Vietnam` (plans + veto flag set in America_1950s_Expansion), `USA_ALBANIAN_SUBVERSION` (fixed, see above), `SOV_internal_ai_behavior` (plans + Stalin-death event), `SOV_foreign_ai_behavior` (historical/aggressive plans; AGGRESSIVE has no post-1957 content by design — the mid-era FP tree is Brezhnev-era), `SOV_1964_presidium` + five `USA_19XX_elections` (new). No dead rules to remove.

## Pass 3 — The German Question / Stalin Notes

The Stalin-era German content was superseded by the shared side branch `SOV_Stalin_Notes_Branch.txt` (`SOV_sn_*`), revealed by `germanquestion.1` (flag `SOV_german_question_active`). Its core fork — `SOV_sn_manage_the_division` (historical) vs `SOV_sn_pursue_the_note` (→ the StalinNotes negotiation chain, possible `Germany_Unified_Neutral`) — had no plan steering and no game-rule control.

Added:
- **Game rule `SOV_german_question`** (AI Behavior — Europe): Default / **Manage the Division** (historical) / **The Note is Rejected** (note pursued, West refuses, Germany stays divided) / **A Neutral, Unified Germany** (negotiations succeed). Localised.
- **Event wiring in `events/Stalin_Notes.txt`** (15 options across StalinNotes.1–5 and .28): SOV's decision to send the note, all three Western responses (USA receives .2/.4), both SOV counter-offers, and the election-interference choice now obey the rule; existing `is_historical_focus_on` modifiers gated on rule = Default. On Unified, the AI also refrains from rigging the all-German elections (interference can collapse the deal).
- **Plans:** `sov_german_question_division` (historical file — takes the division fork, `focus_factors` zeroes the note; New Course → June uprising → Adenauer in Moscow → Treaty on Relations) and `sov_german_question_note` (alternate file — pursues the note and covers all three outcome sub-branches: rejected/fortify, reunified/neutral, socialist camp).

Note: the pre-branch German focuses in the base Stalin tree (`SOV_Stalin_The_German_Question`, Volkspolizei, 1949 election interference) still exist and remain valid in the old foreign plans — the sn branch supplements them for the 1952+ fate of Germany.

## Pass 4 — rule sections for the majors + Five Year Plan AI completion

**Game rules reorganized.** Two dedicated rule groups now exist: **AI Behavior — United States** (`RULE_GROUP_AI_BEHAVIOR_USA`: Vietnam stance, the five election rules, Albanian Subversion — the latter physically moved into the USA section) and **AI Behavior — Soviet Union** (`RULE_GROUP_AI_BEHAVIOR_SOV`: foreign policy, power struggle, 1964 Presidium, German Question). Banner sections in `00_game_rules.txt` mark where each major's rules live; future USA/SOV rules go there.

**4th/5th Five Year Plan missions (SOV_50s_Industry.txt).** These focuses are permanently unavailable and auto-complete via `bypass` when real economic objectives are met — so the AI needs building/research steering, not focus picks. Fixed/added in `common/ai_strategy/CWIC_building_strategies.txt`:
- `SOV_1950s_focus_build_helper`: fossil fuel powerplant target corrected from **8 → 115** (`SOV_Electrification_of_the_Economy` needs >114); added `nuclear_reactor` target 2 (`SOV_Early_Atomic_ReD`) and `synthetic_refinery` target 8 (`SOV_Boost_Petroleum_Refining`); window extended to 1958 (several required techs only unlock in 1955).
- New `SOV_1950s_ukraine_reconstruction`: per-state build targets for states 200/226/227/228/221/259 (steel, industry, arms, office parks, agri) mirroring the `SOV_Complete_Ukrainian_Reconstruction` bypass.
- Don-Volga and transport-infra helpers extended to 1958.
- Strategy plans now carry `research = { agriculture = 50 infrastructure = 50 }` (historical Stalin + Khrushchev plans, Beria + Stalin-lives alternates) for `organic_I`/`water_I`/`inframunicipal_I`/`infrastate_I`.
- The Beria and Stalin-lives alternate plans now include the `STALIN_*` military modernization chain, without which the `SOV_Rebuild_the_Armed_Forces_of_the_Union` mission (needs Supersonic Fighters, Air Defense, Submarine Production) could never bypass on those paths.

Still AI-dependent rather than guaranteed: the Shukhevych token and Don-Volga completion come from decisions, Baltic compliance from occupation policy, and the HDI 0.68 target from general development — the helpers push all the building-side requirements.

## Bugfix — "Brezhnev death" popup on Stalin's death

Not an event bug: no event chain fires the Brezhnev death event (`soviet_leader_change.4`) in 1953 — the Tashkent chain (`soviet_leader_change.3` → `.4`) is correctly gated to March 1982 with Brezhnev ruling. The culprit was the **super-event window** (`common/scripted_guis/CWIC_super_events.txt`), which stacks all its images at the same position and controls them with case-sensitive `<element>_visible` triggers:

1. The Death-of-Stalin image trigger checked `Super_Event_Death_**Of**_Stalin_visible` while `death_of_stalin_super_event` sets lowercase `of` → the Stalin image **never displayed**.
2. The GKCHP (1991 coup) image's trigger key was `Super_Event_gkchp_visible`, which matches no GUI element (the element is `Super_Event_GKCHP`) → with no trigger attached, the GKCHP image was **always visible**, normally hidden only because other super-event images drew on top of it.

Combined effect: when Stalin died, the popup opened, the Stalin image stayed hidden, and the late-Soviet GKCHP artwork showed instead — reading as a Brezhnev-era death popup. Fixed both case mismatches (plus the capital-Of leftover in the bulk flag-clear list).

Also noted during the hunt: `ic_pulse` calls `sov_death.1` (November 1982, Brezhnev natural death) but **no such event exists** — dead call, harmless, since the Tashkent chain handles Brezhnev's death; worth either deleting or implementing later. The scripted gui also carries a handful of orphaned trigger keys (`Super_Event_Zhukov_Coup_visible`, `Super_Event_APG_Coup_visible`, `Super_Event_Gorbachev_1996`, SMO/Zyuganov entries) that match no element — dead code, no visual impact.

## Pass 5 — more Soviet game rules (choice points that mattered)

Swept the SOV event files for AI-facing decisions with real consequences and put four new rules in the Soviet Union section:

| Rule | Event(s) wired | What was broken before |
|---|---|---|
| `SOV_1957_anti_party_group` — Khrushchev Prevails (hist) / The Old Guard Wins | `soviet_leader_change.5` | **Pure 50/50 with no ai_chance** — half of all games had Khrushchev ousted and killed in June 1957, with Bulganin loading the `SOV_Bulganin` tree, even on historical. Now deterministic on historical/rule. |
| `SOV_returned_exiles` — Return to the Caucasus (hist) / Settle in Kazakhstan | `SOV_KHR.4` | 50/50 coin flip on whether the deported peoples' republics are restored or a new Kazakh ASSR appears. |
| `SOV_cuban_missile_crisis` — Thirteen Days (hist) / A Defense Treaty Instead / Brinkmanship | `cubamc.3/.9/.10/.15/.16/.19` (14 options, SOV + USA sides) | Historical weighting existed but was uncontrollable; now the player can force the peaceful resolution, avert the crisis entirely (Castro's defense-treaty counteroffer), or let both sides refuse to blink. Nuclear-retaliation options stay at 0 even under Brinkmanship. |
| `SOV_kaganovich_succession` — Ustinov / Shelepin | `soviet_leader_change.9` (fired from the Kaganovich tree) | No ai_chance — 50/50 succession on the Stalin-lives→Kaganovich path. |

Not given rules (checked and deliberately skipped): `SOV_KHR.8/.9/.26/.27` (regional investment flavor, equal weights are fine), `sov_jvs.5` (Dalian status, already 99/1), COMECON events (sensible weights), the 1980s succession chain (out of era scope).

## Pass 6 — per-branch Soviet foreign policy rules (SOV_foreign_ai_behavior removed)

The blanket Historical/Aggressive foreign rule was removed, along with the `soviet_ahistorical_aggressive` plan. Every foreign-policy fork of the Stalin tree now has its own rule in the Soviet section:

| Rule | Fork | Historical option | Wiring |
|---|---|---|---|
| `SOV_greek_civil_war` | Follow the Percentage Agreements vs armed intervention for the KKE (declares war!) | Percentage | `ai_will_do` on both focuses |
| `SOV_1949_german_election` | Reinforce Communist Ideals in the East vs interfere in the West German election | Hands off | `ai_will_do` |
| `SOV_austria_question` | Neutral Austria (State Treaty) vs "delay independence" / socialist Austria | Neutral | `ai_will_do` |
| `SOV_french_communists` | Sponsor the dockers' strikes vs order a low profile | Dockers' strikes | `ai_will_do` |
| `SOV_yugoslavia_question` | Lift the blockade vs demand Tito's obedience | Lift (post-Stalin) | `ai_will_do` |
| `SOV_turkey_question` | Accept Turkey's NATO accession vs ultimatum chain | Relent | events `sov_turkey_in_nato.1/.3` + `ai_will_do` on the Bosphorus claims focus |

Notable fixes on the way:
- **Turkey/NATO was a hidden disaster** — the full war pipeline, now defused:
  1. `sov_turkey_in_nato.1` had no ai_chance → 50% of games the USSR pushed to expel Turkey. Now 15/85 on Default, deterministic on historical (back down) and under the rule.
  2. Turkey then folded and *left NATO* 99% of the time (`sov_turkey_in_nato.2`, mod-intended drama, left as is — only reachable when the USSR pushes).
  3. **The real war generator**: `SOV_Turkey_Fold` unlocks the focus `SOV_Demand_Turkish_Subordination`, which had **no ai_will_do** — the AI freely took it, firing `TUR_SOV.1` at Turkey, which *rejects regime change ~77% of the time* → `declare_war_on TUR (annex_everything)` + the Invasion of Turkey mission. The focus is now **AI-forbidden unless `SOV_turkey_question = Force Turkey Out`** — random Soviet–Turkish wars from this chain cannot happen anymore on Default or historical.
  4. Same class of problem on the Yugoslav side: `SOV_demand_tito_obediance` fires `TUR_SOV.11` at Belgrade (rejects ~37% → `declare_war_on YUG`); on Default the AI now leans 4:1 toward lifting the blockade, 0 on historical, and the war path is only likely under `SOV_yugoslavia_question = Demand Tito's Obedience`.
  (`SOV_Turkey_Fold`/`Defiance`/`NATO_Application` are inert markers — empty rewards, nothing reads them — so the contradictory double-completion in `sov_turkey_in_nato.3a` is harmless.)
- The Greek intervention focus is not mutually exclusive with the Percentage Agreements focus in script — only `ai_will_do` (now 0 on historical/percentage) prevents the AI from declaring war on Greece.
- `soviet_historical_peaceful` no longer references the deleted rule (enables on historical mode alone) and no longer lists fork focuses — the per-branch rules always win because forks are decided purely by `ai_will_do`.
- The old aggressive plan referenced `SOV_Stalin_Push_for_Socialist_Austria`, which only exists in the outdated "Trees for 0.35" folder — gone with the plan.

## Pass 7 — inline event text extracted to localisation

288 of 450 event files had text written directly in the script — 16,400+ inline strings (6,161 titles, 9,657 option names, 595 descs), which made translation impossible without editing event files.

**14,302 strings extracted** to generated keys following the mod's own convention (`<eventid>.t` / `.d` / `.a .b .c`) and written to **68 new per-country loc files** (`localisation/english/extracted_<TAG>_l_english.yml`, largest: USA 3,643, misc 1,357, India 607). English display is pixel-identical (quoted literals were already looked up as keys first); translators now work from yml files only.

Deliberately untouched: 1,064 `name =` entries inside `create_country_leader`/character blocks (not event options), 211 quoted strings that were already valid loc keys, and ~25 key-style references (`POLITICS_*_DESC` etc.) that are pre-existing references to keys defined elsewhere or missing from loc (pre-existing issue, unchanged behavior).

Validation performed against a pre-run snapshot: event id sets byte-identical per file, comment-aware brace balance unchanged in all 209 modified files, all 14,302 generated keys defined exactly once, zero collisions with the 230,185 pre-existing loc keys, zero unreferenced keys, and a comment-aware final sweep found (and fixed) exactly one straggler (`pru.17`).

## Known gaps / next passes
- **SOV Khrushchev-era foreign policy** has no dedicated tree (Mid_Foriegn_Policy is Brezhnev-era+); Hungary/Suez are event-driven.
- **`SOV_Beria_New.txt` (tree `SOV_Beria`)** is only reachable via debug decisions — appears to be WIP; no plan written for it.
- `usa.19602` (1960 GOP nomination) left untouched — Nixon is the only non-incumbent-gated option.
- If the AI overperforms the Seven-Year Plan (`SOV_KHR_Successful_Plan_even_better`), the Brezhnev option is unavailable by trigger even on historical — very unlikely with the historical plan list, but possible.
- Some alternate-candidate flags ('52 Dewey/Warren/Stassen, Eisenhower-DEM) have no election rule of their own; their agenda plans still work if they win by chance.
- 1970s+ (Watergate, both countries' 70s/80s trees, '72/'76 candidates like McGovern/Muskie/Agnew/Ford/Carter) untouched — next era pass.
