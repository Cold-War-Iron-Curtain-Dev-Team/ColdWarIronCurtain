# USSR foreign policy goals: every way to achieve or lose them

These are working notes for writing player hints in the five goal focuses of `SOV_Stalin.txt`.

**How the goals are judged.** Each goal completes itself as soon as its condition holds after **14 May 1955**.
Any goal not yet completed gets one last check when the **20th Party Congress** focus completes (available from
1 January 1956). The conditions live in `common/scripted_triggers/SOV_foreign_policy_goals_triggers.txt`.

**Read this first: World War III starts automatically.** `common/on_actions/WW3_on_actions.txt` turns *any* war
declared between a Soviet-faction member and a NATO member before 1970 into WW3. It then calls
`Start_Total_War_Between_Factions` and loads the WW3 tree. That tree is loaded without `keep_completed`, so any goal
not yet achieved is lost. Every "careful, this starts a war" hint below comes back to this rule.

---

## 1. Eastern Europe Secured

**Check:** Poland, Romania, Hungary, Czechoslovakia, Albania and Bulgaria are all in our faction. So are Communist
Turkey (SRT), the Austrian Democratic Republic (ADR) and the Greek communists (PDG), **if they exist**.
East Germany is *not* required.

**Start state:** at the 1949 start every one of them is already in the Cominform faction. Poland, Romania, Bulgaria,
Albania and Czechoslovakia are Eastern-bloc puppets, and Hungary is added in history. This is a "don't lose anyone"
goal.

| Source | When | Effect on the goal | Soviet lever |
|---|---|---|---|
| **Albanian subversion** `albania.5` (`IC_scripted_effects` ~9087) | Aug–Nov 1951 | If the Western operation succeeds, Free Albania (KOA) is created and **Albania is removed from the faction** → fail | None directly. The chance comes from `USA.Albanian_Subversion_Chance` (US CIA tree and a game rule). |
| **Albanian counter-revolution** (`WAR_on_actions_scripted_effects`, Greek Civil War peace) | During the Greek Civil War | Can remove Albania | Keep Albania out of the Greek war, or win it |
| **Hungarian Revolution** `HUNGARIAN_REV.1` (`IC_scripted_effects` ~5819) | **Mar–May 1956** | `HUNGARIAN_REV.20` "End to one-party rule" → **Hungary leaves the faction** | Hold the 20th Congress before March 1956, or crush it: `HUNGARIAN_REV.22` "Launch the Invasion" re-adds Hungary |
| **Greek communists (PDG) exist at start** | 1949– | Must be in the faction, or be destroyed | **Percentage-agreement opportunity** (diplomatic button `RCO_sov_greece`, when PDG is more than 40% capitulated): option **b** brings PDG into the faction and declares war on Greece. Option **a** leaves them out. |
| `PDG.35` "Titoism Rises in Greece" | PDG event | Option b2 "Who Needs Them" → **PDG leaves** | Option a2 (compromise) or c2 (tanks) keeps them |
| `PDG.51` "A Letter From Greece" | PDG event | Option a2 → PDG joins | Accept |
| Third Balkan War `THIRD_BALKAN_WAR.93` option c | Later | NATO expels PDG | |
| **Communist Turkey (SRT)** created by `TUR_SOV.1` option a2 (Turkey accepts regime change) | Turkey-in-NATO chain | Once it exists it **must stay in the faction**. Its focuses `SRT_Assert_Turkish_Independence` and `SRT_Reject_Comecon_Planning` make it leave. | Only take this road if you can hold SRT |
| ADR (Austria) | Only created in WW3 (`WW3_Europe_Scripted_Effects`) | Irrelevant outside WW3 | |
| `ddr.9` "Soviet Betrayal" option o2 | East German chain | Removes **Poland** from the faction | |
| `SOV_Establish_the_Warsaw_Pact` decision (from 1955) | | Only renames the faction (news `swf.9`). **No effect on the condition**, but it's the natural thematic hint. | |

**Hint direction:** keep every people's democracy in the bloc through 1955. Guard Albania against Western
subversion (1951). Bring the Greek communists into the faction, or don't let them survive outside it. Settle Hungary
before spring 1956. Don't create a Communist Turkey you can't keep.

---

## 2. Western Europe Divided

**Check:** NOT (the USA is in a faction with France, Britain, West Germany *and* Italy). One of the four missing is
enough.

**Start state:** France, Britain and Italy are in NATO from history. West Germany is **not**. It only joins through
`nato_expansion.9` "Joining NATO?" (option a2), which is fired by the US focus `USA_50s_Invite_West_Germany` (from
1 May 1955) or by the West German focus `WGR_Adenauer_53_Join_NATO`. (The `1956.1.1` history block that adds West
Germany only applies to the 1980 bookmark.) **The real goal is keeping West Germany out of NATO.**

| Route | How | Notes |
|---|---|---|
| **Stalin Note** (diplomatic button `RCO_sov_stalin_note`, 1952+, Stalin ruling) → `StalinNotes.1` "Send the Note to Washington" | Leads through the `Stalin_Notes.txt` chain to a **neutral reunified Germany** (`Germany_Unified_Neutral`, `annex_country` in `StalinNotes.11/.18/.33/.35`) | Strongest Soviet lever. West Germany is either annexed or neutral → never joins NATO. |
| **1949 West German election** (button `RCO_sov_wgr49`, before 1951) → `SOV_WGR.1` "Interfere" | Raises KPD support. If the KPD wins (`WGRElection.1` option c) → `sov_german_question.2` "A Red Bonn" | The election win is a long shot. `SOV_WGR.2` can expose the network. Game rule `SOV_1949_german_election` controls the AI. |
| **East German unification** `ddr.12` / `ddr.17` "Unification?" option Accept | The USA removes West Germany from NATO | East German chain, mostly later |
| West German `nato_expansion.9` option b2 "Decline the Offer" | West Germany never joins | AI/West German choice |
| France / Italy / Britain leaving NATO | No reachable 1949–56 content. The Italian civil war chain `itacw.*` (Italy joins the Soviet faction) is **never fired**. French Communism `French_Communism.11` re-adds France. | |
| `soviet_international_detente_category` (European tour, state visits) | Opinion and influence only | No direct effect |

**Hint direction:** stop the West German army joining NATO. Push the German question: the Stalin Note for a neutral,
united Germany, or meddle in the 1949 Bundestag election.

---

## 3. Establish Eastern Communism

**Check (corrected reading):**
- Mongolia owns **Ulaanbaatar** (1184).
- The PRC owns **Chongqing** (601).
- **North Korea owns Seoul (750)**.
- **North Vietnam owns Hanoi (1760)**.
- Malaya (MLA) owns **Kuala Lumpur** (784) if it exists.
- The Philippines rebels (HUK) own **Manila** (327) if they exist.

These are **not** "hold your capitals": it means **winning** the Chinese Civil War, the Korean War and the First
Indochina War.

| Front | Soviet levers | Ways to fail |
|---|---|---|
| **China (Chongqing)** | `SOV_Treaty_of_Friendship_with_China` (after 14 Feb 1950, needs `PRC_Victory`); `SOV_156_projects` | **Manchurian intervention** (button `RCO_sov_china`, when the PRC is more than 79% capitulated) runs `PRC_Lose_CCW` = **Nationalist victory**. The PRC survives in Manchuria but never holds Chongqing → fail. The PRC must win outright. |
| **Korea (Seoul)** | `SOV_Arms_the_Korean_Army` (1950+), `SOV_consolidate_Korea` (1955+) | A UN ceasefire on the old line (`Korean_War_Ceasefire_show`, 1095-day mission) leaves Seoul with South Korea → fail. Direct Soviet entry `korea.33` is **commented out** (`_generic_decisions.txt:1985`). Win: `annexation_of_south_korea`, when South Korea's backers answer `korea.24` with "No, let it rest" (→ `korea.26`). |
| **Vietnam (Hanoi)** | `SOV_Arrange_Meeting_with_Ho` (`SOV_VIN.1`), `SOV_Recognize_Vietnam` (after 30 Jan 1950: equipment, money, recognition) | Driven by the **Indochina Struggle** system (`CWIC_Struggle_Effects.txt`). Hanoi goes to North Vietnam in the communist-victory, Geneva and failed-state endings. Southern, Federal, Kuomintang and Đạn Quốc endings give it away. |
| **Mongolia** | Nothing to do | **Annexing Mongolia** would fail it (it no longer "owns" its capital) |
| **Malaya / Philippines** | No Soviet decisions | Both exist at the start (Malaya 1 state, HUK 5). If they **survive without their capital** → fail. Quirk: if they are **destroyed**, the clause passes. |

**Hint direction:** see the revolution through everywhere in the East. Arm Kim and help him take Seoul. Recognise
and arm Ho Chi Minh. Make sure Mao wins outright, because a rescue in Manchuria is not a victory.

---

## 4. Prevent Communist Deviations

**Check:** Yugoslavia is in our faction, **and** Yugoslavia is not `trotskyism` ("Revisionist Marxism", Tito's
ideology), **and** the PRC is not `trotskyism`.

**Start state:** Yugoslavia is ruled by `trotskyism` and is outside the faction.

| Route | Result for the goal |
|---|---|
| **Yugoslav ultimatum** (button `RCO_sov_yug`, before 1953, needs PDG to own state 47) → `TUR_SOV.11` option a2 "Accept Soviet Troops" | Yugoslavia **joins the faction but is deliberately kept `trotskyism`**: "Tito gets to stay in power". → **Never satisfies the goal.** |
| Same ultimatum, option b2 "Reject" → Soviet–Yugoslav war → peace in `wars_on_actions` (~245) | Yugoslavia becomes an Eastern-bloc puppet (in the faction) but is **again forced to `trotskyism`** → **never satisfies the goal**. |
| **Cominformist plot** in Yugoslavia's own tree (`YUG_50sR.txt`: `YUG_scale_back_udba_operations` → `YUG_brand_rankovic_a_traitor` → `YUG_assasinate_tito`) → `cominplot.2` → **`cominplot.5`** | Yugoslavia becomes a **Soviet puppet ruled by `communism`** → **satisfies the goal.** This is Yugoslavia's choice; the USSR has no lever. |
| `yug.30` "Transformation To Communism" | `communism`, but not fired by Soviet content |
| SOV_Troika `SOV_secret_talks_with_tito` | Opinion only |
| PRC clause | **Always true.** No content ever makes the PRC `trotskyism`. |

**Hint direction:** bring Belgrade back into the camp *and* end Titoism. As coded, the USSR can achieve the first
half but never the second.

---

## 5. Avoid Direct Conflict

**Check:** not at war with the USA, Britain, France or West Germany.

| Risk | Detail |
|---|---|
| **Any bloc war → automatic WW3** | `WW3_on_actions.txt`: *any* declaration between a Soviet-faction member and a NATO member before 1970 starts WW3 and pulls everyone in. The danger includes **allies**: PDG, Albania, Communist Turkey. |
| Turkey | NATO expansion → `sov_turkey_in_nato.1-3` → `TUR_SOV.1` option b2 "Reject": **the USSR declares war on Turkey**. If Turkey is already in NATO → WW3. |
| Greece | Percentage agreement option b declares war on Greece. Safe before Greece joins NATO (`nato_expansion`, around 1952), WW3 after. |
| Czechoslovak ultimatum `cwu.100` option b "Reject their Ultimatum" | The USA joins the war against the USSR |
| WW3 decisions / `SOVw_Third_World_War.1` | Starting WW3 obviously fails it |
| Korea | No direct Soviet entry (`korea.33` disabled). Arming North Korea is safe. |
| Berlin crisis (`berlincrisis.4` "A military option") | Only from the 1957 West German trees, so outside the window |

**Hint direction:** fight the imperialists by proxy only, and remember that any ally's war with a NATO member drags
the whole bloc into world war.

---

## Design issues found along the way

1. **Prevent Communist Deviations can't be achieved through Soviet content.** Both Soviet routes force Yugoslavia
   back to `trotskyism`, and that's intentional (comment: "dont change this at all!!"). Options:
   - (a) Drop the `trotskyism` clause and require only "Yugoslavia in the faction".
   - (b) Keep it as a Cominformist-plot-only goal and say so in the hint.
   - (c) Swap the clause for "Yugoslavia is our subject".
   The PRC clause is dead and could become "no Sino-Soviet split" if a flag for that exists.
2. **Malaya / Philippines vacuous pass.** Destroying them satisfies Eastern Communism. A clause like
   "`NOT = { country_exists = MLA }` OR MLA owns 784" is the same thing, so if the intent is "the insurgency won", it
   needs a flag or a "communist-held" check instead.
3. **Eastern Communism is much harder than its name.** It requires Seoul and Chongqing, not capitals. It's fine as a
   stretch goal, but the description has to say "win in Korea".
4. **Dead references to the old side branches** (removed in `268697f0a2` and `d9f64b66e4`):
   - `complete_national_focus = SOV_wge_a_red_bonn` in `sov_german_question.2`
   - `SOV_ccw_the_twentieth_congress_in_peking` and `SOV_krushchev_visit_china` in the 20th Congress focus
     (`SOV_Stalin.txt`)
   - `SOV_historical_strategy_plan.txt`
5. **Unreachable content:** the Italian civil war chain `itacw.1-3` is never fired, and `korea.33` is commented out.
6. **The WW3 tree drops completed goals.** It loads without `keep_completed`, which is fine because WW3 means failure
   anyway.
