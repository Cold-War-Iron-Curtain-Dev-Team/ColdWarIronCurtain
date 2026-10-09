# VIN/FRE Rework Session Handoff

## Checkpoint

- Repository: `/home/zom/Projects/ColdWarIronCurtain`
- Branch: `development-branch`
- Current checked-in base before this checkpoint: `d9c681eb98` (`Nerfed division limit buff for VIN`)
- Gameplay checkpoint commit after history rewrite: `7e32f0b919` (`Rework VIN campaigns and restore THO`)
- Canonical design and implementation ledger: `CWIC Backup/documentation/VIN_FRE_Tree_Expansion_Design.md`
- Status at handoff: the first unattended run reached historical Geneva naturally but established a balance failure: VIN won most campaigns extremely quickly while repeated broad participation destroyed the other crown-domain armies. The working tree now removes VIN's hidden AI combat/resource packages, isolates participation to the objective-owning crown, makes CEFEO operations FRE-VIN only, applies severe exact-envelope overextension per offending command, tightens AI state requests, and expands AFK telemetry. Static verification passes; a fresh full unattended run is next.

This is a deliberate stopping point after the VIN campaign lifecycle stabilization, game-start THO/Cao-Bac restoration, adjacency retirement, first overextension pass, and the first state-policy/supply/AI balance follow-up. Do not restart these patches from the original plan; continue from the checked-in implementation and the canonical ledger.

## User intent and latest conclusions

- Continue rebuilding the VIN/FRE Indochina campaigns around a common primary-campaign lifecycle and later French response packages.
- Preserve historical flavor, but favor playable operational flow over hard province fences.
- Artificial northern adjacency restrictions made THO and Dien Bien Phu impossible to enter. The relevant northern/campaign assignments have now been retired; Laos/theatre-divider restrictions remain.
- Human VIN was initially too powerful, while campaign state cleanup and broad AI orders caused severe front/supply failures. The current patch replaces those behaviors with targeted state policy, local base-area supply, narrower AI objectives, stronger CEFEO defense, and moderate rather than blanket combat modifiers.
- A full historical-AI run completed Cao-Bac, Hoa Binh, Northwest, Dien Bien Phu, and a historical Geneva settlement. Campaign outcomes worked, but both sides still fought too freely outside the named operations: VIN overran secondary crown-domain ground, CEFEO penetrated VIN rear areas, the southern base collapsed, and MEO repeatedly abandoned Ha Giang and capitulated.
- A human FRE Northwest test remained winnable: FRE drove VIN into its interior, took the northern capital for supply, and timed the campaign out as a French success despite failing to break encircled Hoa Binh. Do not weaken VIN or strengthen Dien Bien from this one result; the scenario objective is the campaign, not unconditional VIN capitulation.
- The original Geneva non-fire had two layers. A living NLF correctly kept VIE at war and failed `geneva_conference_vietnam_at_peace_trigger`, while the autonomous defeated-NLF bridge could later force Hanoi into Geneva without a visible choice. That bridge has now been replaced by the explicit focus fork documented below; only the negotiations focus owns Hanoi's peace-gated queue.
- The user removed the autonomy transfer from `NUN_Unification.2.a`. Keep this change. The event may update NUN politics/leadership, but NUN must remain under CEFEO rather than becoming a VIE puppet during the northern war.
- French Indochina is now a CEFEO-led coordination faction rather than a VIE-led faction. Its fixed no-call rule is essential: the northern CEFEO/VIN wars and southern VIE/NLF war share alignment and access but must not merge automatically. NLF remains in Hanoi's Viet Minh faction as before; faction identity spirits, the two no-call rules, and the existing protectorate restriction suppress ordinary AI calls so that membership does not make VIE and VIN direct belligerents.
- The repaired local-supply modifier now has engine acceptance: it appears and works in VIN's southern states. Repeated Northwest runs also confirmed MEO defends or recovers Ha Giang, historical AI can reach the intended outcome, and a capable player-led side retains room to dominate.
- Operation Lorraine is now a response attached to the Northwest primary campaign rather than a standalone border war. Its three postures are a deep Clear River thrust, a limited raid, or withholding the mobile groups for Na San.
- A recorded communist Dien Bien Phu capture now briefs VIN regardless of NLF viability and opens the focus fork after `VIN_Prepare_Dien`. Historical Hanoi retains the peace-gated Geneva pursuit; alternate Hanoi reinforces the southern resistance and can escalate through mobilization to direct VIN-VIE intervention.
- Repeated mixed player/AI Hoa Binh runs resolved consistently and established that the lifecycle is clean. The follow-up now makes Amarante a real force-preservation option and holding an explicit result-dependent wager without changing the accepted campaign ownership or timing. Its new values still need external engine confirmation.
- The scoped rework-localization audit is complete. Player-facing values now use Viet Minh, CEFEO/French Expeditionary Corps, State of Vietnam, Nung, Tai Federation, Muong Federation, Tho territory, named geography, and plain campaign language instead of raw tags or resolver/state IDs. Internal localization keys and scripted variable references such as `[?FRE.FRE_War_Credits]` remain untouched.
- Because external test time is limited, the user explicitly approved batching compatible content patches into one playtest. The present uncommitted batch combines Pollux and Atlante after the accepted Castor/Dien Bien foundation, with console terminals for branches that do not fit one natural run.
- 2026-08-12 engine result: player-controlled Lorraine terminated properly, defended the intended state, and recorded the proper outcome; historical AI produced the historical campaign result; after the NLF died, Geneva convened through the intended post-Dien Bien Phu peace-gated route. No lifecycle regression was reported in the full run.
- 2026-08-17 engine result: the expanded VIN path was playable through 1956 and its content order flowed well. The run is the baseline for the armistice, THO deployment, and objective-clarity repairs below; it is not engine acceptance of those three new fixes.

## Implemented systems

### Canonical campaign lifecycle

- Shared resolver in `Cold War Iron Curtain/common/scripted_effects/VIN_Campaign_Effects.txt`.
- Result vocabulary is fixed: clean `1`, costly `2`, aborted `3`, failure `4`, superseded `5`.
- Daily resolution order is objective, theatre closure, final deadline, then absent-war abort.
- Boundary days are inclusive; elapsed days survive cleanup for delayed result localization.
- Every campaign records one permanent result flag. Supersession gives no ownership transfer, Struggle score, phase movement, War Credits, Metropole Patience, or DBP/Geneva battlefield result.
- Campaign finish now arms a retrying armistice sweep. It removes VIN from wars with any French Indochina participant pulled into the set-piece battle, checks FRE and metropolitan France directly, and retries on the guaranteed VIN daily tick until the temporary war graph is empty. Laos belligerents are deliberately excluded so an unrelated Laos raid cannot be erased.
- All production exits use common cleanup. The obsolete border-war watchdog routes into the resolver.
- Reusable console diagnostics live in `Cold War Iron Curtain/common/scripted_effects/IC_VIN_Campaign_Test_Effects.txt`.

### THO and Cao-Bac

- THO starts alive in states `1280` (Cao Bang) and `1768` (Lang Son), using `THO_FRA` and a neutral French-aligned territorial council.
- VIN starts with capital state `881` (Dong Bac Bo).
- THO is a FRE crown domain with the existing non-Together-for-Victory puppet fallback, starts with two small defensive units, and is AI-only without a focus tree.
- THO's two territorial battalions now receive their Cao Bang/Lang Son state requests before war begins, maximum local theatre demand, negative requests for allied fronts, reduced garrison diversion, and `dont_defend_ally_borders = 1000`. Their historical starting locations remain Cao Bang and Lang Son.
- `VIN_Operation_Cao-Bac` is campaign ID `4`. It targets complete simultaneous control of `1280` and `1768` and annexes THO only after successful state transfer.
- Failure/abort leaves THO intact; supersession cleans up without ownership or battlefield rewards.
- Existing GCMA, Struggle, military-access, CEFEO dissolution, failsafe, and postwar communist THO restoration paths remain connected.
- The later communist autonomy-zone chain still re-creates THO under VIN with Chu Van Tan only if colonial THO no longer survives.

### Front policy, movement, supply, and balance

- Fifty-seven northern/campaign adjacency assignments are unrestricted. Thirty-five Laos/theatre-divider assignments remain gated. The two Dien Bien-to-Laos boundaries remain gated; four internal camp approaches are open.
- Do not restore the retired adjacency assignments merely to contain the AI. Use objectives, defense strategy, supply, and overextension.
- Campaign state policy is rebuilt and applied daily:
  - Cao-Bac: planned/contested `1280`, `1768`.
  - Northwest: `1761`.
  - Hoa Binh: `1761`, `1766`.
  - Dien Bien Phu: `1761`, `671`.
- Non-objective northern states retain/recover `unplanned_offensive`; cleanup restores the baseline rather than erasing it.
- VIN-controlled Thanh Hoa (`1762`), Nghe-Tinh (`1763`), and Quang Binh (`838`) receive campaign-only dispersed local supply. The repaired state-scoped effect grants `+0.50` local supply, follows control, and clears at campaign end.
- One-tier shared overextension applies to off-theatre penetration and clears from VIN or the CEFEO/crown-domain side as geography changes. A severe/deep second tier is deferred.
- The blanket French combat penalty and excessively broad VIN buffs were reduced/removed. The objective-state defense penalty is now moderate.
- VIN's broad wartime plan aborts while a named campaign is live. The campaign posture keeps reserves in Dong Bac Bo and all three southern-base states, suppresses VIE/NUN and non-objective CEFEO fronts, and reduces the country-wide poor-odds override from a stacked `300` to `50`.
- FRE, VIE, THO, TAI, TAM, and NUN suppress requests into VIN rear areas and use state-scoped campaign plans instead of tag-wide counteroffensives. Operation Lorraine's deep posture remains the sole scripted exception for Dong Bac Bo.
- MEO receives a self-contained Ha Giang defense plan, maximum local unit demand, reduced garrison diversion, and an instruction not to defend allied borders. VIN receives no Ha Giang unit request. TAI still starts with an extra Dien Bien battalion.
- Dien Bien siege progress now needs an approach plus a separate valley-ring province; AI aid can finish an established siege but cannot create one from nothing.

### Supporting content included in this checkpoint

- THO character/history/OOB and localization support.
- MEO/TAI-MEO leadership and event/focus support, including the `Lo_Van_Hac.png` portrait.
- Campaign result events/localization, focus compatibility, CEFEO dissolution cleanup, Struggle ending cleanup, and expanded test helpers.
- The four restored limited battles have pre-launch objective tooltips, a persistent objective card, exact province highlights, named objective provinces, and a live five-day hold counter. The accidental VIN militia deployment in TAI-controlled Vinh Yen was moved to the VIN-held Hoang Lien Son approach.
- User-owned NUN change in `Cold War Iron Curtain/events/VIE_Events.txt`: no `set_autonomy` in `NUN_Unification.2.a`.

### Northwest/Lorraine response

- `FRE_Operation_Lorraine` is a ten-day response focus. It can be prepared on the historical date fallback or during a live Northwest campaign, and an early plan is automatically offered when VIN launches later.
- The legacy selectable Lorraine mission is removed. No border war, generic target fallback, territorial transfer, or independent peace path remains in production.
- A deep thrust spends 100 War Credits/8 Patience, removes 40 VIN Campaign Supply, advances its clock by 14 days, and must hold any Dong Bac Bo province for seven daily ticks. A limited raid spends 60 Credits and imposes a smaller one-shot disruption. Withholding spends 30 Credits on a temporary FRE/TAI defensive package; an unfunded fallback grants no package.
- Permanent response results are strategic success, limited tactical raid, failure, withheld, or superseded. The VIN resolver records one before common cleanup. Targeted FRE/VIN AI orders cover only the named Dong Bac Bo rear objective.

### Post-Dien Bien Phu southern war

- A recorded communist capture of Dien Bien Phu raises one briefing whether the NLF is viable, defeated, or absent. After `VIN_Prepare_Dien`, it exposes two mutually exclusive focuses instead of temporary decisions: the 14-day historical `VIN_Push_for_Negotiations` and the 34-day alternate `VIN_Carry_the_Revolution_South`.
- Negotiations grant 25 Communist leverage and 150 de-escalation points, start `Indochina_Geneva_Pursuit`, and create the VIN-focus-owned `VIN_Post_DBP_Focus_Geneva_Queued` latch. The queue checks the existing Hanoi/Saigon peace gate immediately and daily. An unrelated VIN or VIE war leaves the route visibly queued while the ordinary pursuit tick continues de-escalation.
- The former autonomous DBP/defeated-NLF queue is retired. Old autonomous queue state is cleared on load unless the save records the old talks posture; that posture migrates to the focus-owned queue. Existing funded-NLF saves migrate to the escalation posture. France-, United States-, and other system-owned Geneva entry points remain intact.
- Escalation has no PP or Campaign Supply debit. It preserves the former NLF support package (15,000 manpower, 25 command power, 4,000 infantry equipment, 500 support equipment, 200 artillery, and the Northern Supply Line), adds 25 Communist Struggle score and 50 escalation points, and suppresses only the panic-collapse Geneva route.
- `VIN_Mobilize_for_National_Reunification` adds a 180-day preparation spirit (+10% planning speed, +5% army organization, -5% supply consumption, +2% reinforce rate) and focused AI pressure toward Saigon while retaining northern reserves. The 14-day `VIN_Launch_the_General_Offensive` directly declares one `annex_everything` VIN-VIE war. It does not set `Vietnam_War`, explicitly call FRE/FRA, or annex/control the independent NLF.
- Only the negotiations focus may use the narrow divisionless-NLF paper armistice, and only after VIN itself is at peace. The queue then waits for `geneva_conference_vietnam_at_peace_trigger` before inviting the existing delegations and continuing through `VIN_The_Geneva_Peace_Conference`.
- `test_vin_post_dbp_southern_war_status` reports strategic-choice count, queue ownership, peace-gate state, panic suppression, NLF independence, preparation cleanup, and the invasion/1960s-war guards. `test_vin_post_dbp_focus_geneva_check` advances the production checks once; the legacy-named helper remains only as a console alias.

### Two-stage Hoa Binh / Operation Amarante

- TAM's control of Hoa Binh represents the completed French seizure and established salient. VIN campaign ID `2` transitions the same primary campaign into the counteroffensive/CEFEO holdout phase and raises one live response choice.
- `FRE_Battles.5` no longer free-fires after Mao Khe. Historical-focus AI is forced to plan Operation Amarante for campaign day `105`; nonhistorical AI uses an 80/20 withdrawal/hold split when the hold is affordable. The alternate choice spends 80 War Credits and commits 4,000 manpower to replace the phase-one salient modifier with a defender-only state-`1766` holdout modifier, supply TAM, and raise focused AI demand.
- Amarante raises a withdrawal request only if French-aligned forces still control state `1766`. VIN's classifier checks an actual capture and theatre supersession first, then consumes the request as a clean success. Only the parent resolver transfers Hoa Binh, annexes an empty TAM, makes peace, pays rewards, and runs cleanup.
- Permanent response results are orderly withdrawal, held, lost, inconclusive, or superseded. Common finish, CEFEO dissolution, and the orphan check remove all temporary flags/state modifiers and clear any pending withdrawal request.
- Engine acceptance: mixed player/AI control produced more consistent passes for both sides, the response prompt and postures worked, and no lifecycle or cleanup regression was reported. Treat the mechanics as accepted.
- Successful Amarante now returns the 1,500 committed manpower plus 2,000 infantry equipment, 250 support equipment, and 100 artillery equipment; grants 75 War Credits; adds 25 de-escalation; preserves a `+10` Na San preparation callback; and directly waives the Hoa Binh clean-result `-12` Patience shock. The Viet Minh still receive the clean battlefield/Struggle result and Hoa Binh; the wider Indochina War continues.
- Holding now pays its best reward only when the salient survives the final day-`210` deadline: in addition to the parent campaign reward, CEFEO receives 100 War Credits, 10 Patience, 3% War Support, and a 25-point two-sided Struggle swing. If a committed hold loses Hoa Binh, it suffers an additional 3,000 manpower, 1,500 infantry equipment, 150 support equipment, 75 artillery equipment, 75 War Credits, 8 Patience, and 4% War Support loss, plus 50 escalation and a 25-point two-sided Struggle swing toward the communists. An absent-war abort is inconclusive and cannot collect the hold reward.
- Both tooltips and the choice event now state the outcome contract before selection: withdraw on day `105`, concede Hoa Binh, preserve the field force, and continue the wider war versus retain Hoa Binh through day `210`, risk the force, gain more if the offensive fails, and lose more if the salient breaks.

### Dien Bien Phu defensive response

- VIN campaign ID `3` remains the only owner of exact camp classification, territory, peace, battlefield/Geneva recording, and primary cleanup. Its launch now raises one CEFEO response choice: scheduled airlift, maximum reinforcement, Operation Condor, or an Operation Vulture request.
- Each posture pays visible up-front costs and receives result-dependent consequences only after the parent campaign classifies its outcome. The fixed day-`150` clean and day-`260` final boundaries are unchanged.
- Condor arms only after the Viet Minh establish the existing approach-plus-ring investment, then requires French-aligned control of the camp, an approach, and an outer-ring position for seven consecutive days. Vulture consumes both the retained limited-support event and the direct American-focus intervention hook.
- The legacy delayed `FRE_DBP.1-.8` chain remains gated for old saves and console compatibility, but its production fire site is retired. Parent finish, weekly orphan handling, CEFEO dissolution, and theatre ending all clear the new response package.

### Exact-province Operation Castor

- The Castor focus now requires a live theatre, surviving Viet Minh and Tai Federation, French-aligned control of the Dien Bien Phu landing ground, no live Dien Bien offensive, and no other CEFEO operation. Completion opens an immediate full, limited, or unfunded commitment event.
- A funded drop pays manpower, transport planes, War Credits, and Metropole Patience up front, fortifies the actual camp, and deploys a commitment-scaled GONO garrison. Success requires province `4529` to remain under French-aligned control for fourteen consecutive daily checks inside a thirty-day visible establishment window; broken control resets the streak.
- Castor records only establishment success, failure, or theatre supersession. It owns no territory transfer, peace, annexation, VIN campaign resolution, or Geneva result. Success establishes the camp for the later campaign rather than declaring the battle won.
- Castor is removed from generic operation ID `5`, target-state fallback, border war, arithmetic threshold, result dispatch, and 150-day watchdog. The generic operation implementation has since been retired for Hirondelle, Mouette, and Brochet as well; the numeric IDs survive only as inputs to their dedicated exact-objective lifecycle and migration shims.
- Daily, timer-backstop, weekly orphan, dissolution, theatre-ending, fallback-dispatcher, localization, and console diagnostic paths are wired. If campaign ID `3` begins before the establishment clock finishes, Castor closes as superseded but preserves its deployed garrison for the parent siege. A lost landing ground before commitment and an unfunded launch receive distinct conclusions without charging a deployment that never occurred.

### Operation Pollux

- Pollux is a ten-day focus after Castor and before the final operational node. It requires an established French-aligned Dien Bien Phu camp, a surviving Tai Federation, a live theatre, and no active Dien Bien Phu campaign or other CEFEO operation.
- The historical split evacuation spends 30 War Credits, three transport planes, and 2 Metropole Patience. Operation Leda preserves limited regular stores, while the Tai partisan column records its historical loss after ten days.
- The escorted alternative spends 80 War Credits, commits 2,000 manpower, and requires French-aligned control of Lai Chau province `13765`, Route Pavie province `13762`, and camp province `4529` for seven consecutive days inside a twenty-one-day window. Broken control resets the streak.
- The expanded airlift spends 120 War Credits, eight transport planes, and 7 Patience. It preserves the force after seven consecutive days of camp control without requiring the land corridor.
- Preservation deploys one additional Pollux survivor group into the existing GONO formation and supplies the camp. Permanent results are preserved, column lost, or theatre-superseded. Pollux owns no transfer, peace, VIN campaign result, Dien Bien Phu/Geneva recorder, or primary cleanup.
- Daily, timer-backstop, weekly orphan, CEFEO dissolution, theatre ending, parent-campaign handoff, targeted AI, centralized localization, and console diagnostics are wired. Campaign ID `3` closes an unfinished Pollux result before opening the defensive response.

### Renovated legacy FRE focuses

- The former broken Hirondelle, Mouette, and Brochet border-war paths are replaced by dedicated exact-objective lifecycles. Their old selectable mission definitions remain hidden and hard-disabled only so old saves can cancel those mission IDs safely.
- The former Na San, Vinh Yen, and Mao Khe arithmetic missions are likewise outside the production path. Their focuses now prepare live FRE responses to VIN-owned primary campaigns; Day River has been restored between Mao Khe and Hoa Binh.
- These conversions are code-complete and statically checked in the 2026-08-17 batch below. They are not engine-accepted until a new playtest covers their launch, terminal outcomes, callbacks, and cleanup.

### Operation Atlante

- Atlante is a ten-day focus after Pollux. It requires the State of Vietnam and the southern Viet Minh to remain at war in a live theatre and waits for any preceding CEFEO mission to finish.
- The operation uses the NLF-owned Interzone V map abstraction in state `1287`. A full commitment must hold adjacent provinces `4255` and `1300` for fourteen consecutive days inside a ninety-day mission; a Vietnamese-led plan must hold coastal province `4255` under State of Vietnam control. Broken control resets the streak.
- Historical AI selects the full CEFEO commitment: 100 War Credits, 4,500 manpower, and 7 Patience, plus equipment for Saigon and targeted allied AI pressure into state `1287`. This records that the expeditionary reserve is in central Vietnam and removes maximum reinforcement and Condor when the live Dien Bien Phu response opens. Scheduled defense and Vulture remain available.
- The limited plan costs 40 Credits and 2 Patience, arms the Vietnamese National Army, and preserves the full northern response menu. Canceling Atlante costs 40 Credits, 2,500 manpower, and 3 Patience to bank a northern reserve; campaign ID `3` consumes it for 1,000 infantry equipment, 100 support equipment, 50 artillery equipment, and a ten-active-siege-day degradation offset. The day-`150` and day-`260` campaign deadlines remain fixed.
- Permanent results are central success, Vietnamese foothold, stalled, northern priority, or superseded. Atlante owns no state/province transfer, war declaration or peace, primary campaign result, Dien Bien battlefield record, or Geneva record. It may continue concurrently after the northern campaign begins.
- Daily, ninety-day backstop, weekly orphan, theatre/dissolution cleanup, exact-objective AI, centralized localization, and `test_fre_atlante_*` diagnostics are wired.

### French Indochina command model

- `faction_template_french_indochina` replaces Saigon's 1949 faction. CEFEO is the fixed leader; State of Vietnam, Cochinchina, the Montagnard crown domain, Tai Federation, Nung territory, Muong Federation, and Tho territory are the intended members. France is deliberately outside the faction and CEFEO remains outside France's subject chain.
- A dedicated no-call faction rule prevents ordinary faction calls to war, and a dedicated leadership rule prevents command drift. CEFEO still enters northern crown-domain defensive wars through the subject relationship; Saigon and its southern subjects continue their separate war with the southern Viet Minh.
- VIN and NLF remain together in the Viet Minh faction at startup. Bilateral coordination flags still expose their political/logistical relationship to scripted content. The Viet Minh and French Indochina templates both use the hidden no-call rule, and all three Indochina faction-identity spirits give AI `-1000` get/call/join desire plus permission to decline calls.
- The northern domains remain CEFEO crown-domain subjects. Cochinchina and the Montagnard territory remain Saigon's southern subjects. The VIE Nung decision is unavailable until the war/CEFEO custody ends, and the removed `NUN_Unification.2.a` autonomy transfer remains removed.
- VIE's Pau/Matignon diplomacy no longer changes northern custody or pretends to move VIE through direct French autonomy levels. Pro-French coup routes use their political status spirits instead of making VIE a French subject and exposing the theatre to NATO. The Free French collapse event likewise preserves CEFEO independence and the southern custody chain.
- Nung communist/independence routes and Montagnard independence explicitly leave the correct command. CEFEO dissolution dismantles French Indochina before handback/annexation, preventing accidental faction-leader succession.
- `test_indochina_command_status` verifies leadership, membership, custody, Hanoi/NLF faction coordination, the continuing VIE-NLF war, and the absence of VIE-VIN or NLF-CEFEO war leakage. `test_indochina_command_repair` rebuilds the early setup for old saves or destructive branch testing; ordinary startup now also restores NLF membership for saves created by the brief separation model.

## Important files

- Design/ledger: `CWIC Backup/documentation/VIN_FRE_Tree_Expansion_Design.md`
- Campaign effects: `Cold War Iron Curtain/common/scripted_effects/VIN_Campaign_Effects.txt`
- Campaign geography/triggers: `Cold War Iron Curtain/common/scripted_triggers/VIN_indochina_campaign_triggers.txt`
- Campaign tests: `Cold War Iron Curtain/common/scripted_effects/IC_VIN_Campaign_Test_Effects.txt`
- Campaign UI: `Cold War Iron Curtain/common/decisions/Indochina_War.txt`, `Cold War Iron Curtain/common/scripted_localisation/VIN_Campaign_Scripted_Loc.txt`, and `Cold War Iron Curtain/localisation/english/VIN_events_l_english.yml`
- Starting deployments/map names: `Cold War Iron Curtain/history/units/THO_1949.txt`, `Cold War Iron Curtain/history/units/VIN_1949.txt`, and `Cold War Iron Curtain/localisation/english/victory_points_l_english.yml`
- VIN focuses/events/localization:
  - `Cold War Iron Curtain/common/national_focus/VIN_50s.txt`
  - `Cold War Iron Curtain/events/VIN_Campaign_Events.txt`
  - `Cold War Iron Curtain/common/scripted_localisation/VIN_Campaign_Scripted_Loc.txt`
  - `Cold War Iron Curtain/localisation/english/VIN_misc_l_english.yml`
- Balance/AI:
  - `Cold War Iron Curtain/common/ideas/VIN.txt`
  - `Cold War Iron Curtain/common/ideas/FRE_CEFEO.txt`
  - `Cold War Iron Curtain/common/dynamic_modifiers/0_dynamic_modifiers.txt`
  - `Cold War Iron Curtain/common/ai_strategy/FRA.txt`
  - `Cold War Iron Curtain/common/ai_strategy/indochina_communist.txt`
- THO lifecycle/history:
  - `Cold War Iron Curtain/common/characters/THO.txt`
  - `Cold War Iron Curtain/common/scripted_effects/THO_Viet_Bac_Effects.txt`
  - `Cold War Iron Curtain/history/countries/THO - Tay.txt`
  - `Cold War Iron Curtain/history/units/THO_1949.txt`
- Movement graph: `Cold War Iron Curtain/map/adjacencies.csv`
- NUN custody behavior: `Cold War Iron Curtain/events/VIE_Events.txt`
- Lorraine response: `Cold War Iron Curtain/common/scripted_effects/FRE_Northwest_Response_Effects.txt`, `Cold War Iron Curtain/events/FRE_Northwest_Response_Events.txt`
- Post-DBP strategy: `Cold War Iron Curtain/common/national_focus/VIN_50s.txt`, `Cold War Iron Curtain/common/scripted_effects/VIN_Post_DBP_South_Effects.txt`, `Cold War Iron Curtain/common/scripted_triggers/VIN_Post_DBP_South_Triggers.txt`, `Cold War Iron Curtain/events/VIN_Post_DBP_South_Events.txt`
- Hoa Binh response: `Cold War Iron Curtain/common/scripted_effects/FRE_Hoa_Binh_Response_Effects.txt`, `Cold War Iron Curtain/events/FRE_Hoa_Binh_Response_Events.txt`, `Cold War Iron Curtain/events/FRE_Events.txt`, `Cold War Iron Curtain/localisation/english/FRE_Hoa_Binh_Response_l_english.yml`
- Dien Bien Phu response: `Cold War Iron Curtain/common/scripted_effects/FRE_Dien_Bien_Response_Effects.txt`, `Cold War Iron Curtain/common/scripted_triggers/FRE_Dien_Bien_Response_Triggers.txt`, `Cold War Iron Curtain/events/FRE_Dien_Bien_Response_Events.txt`, `Cold War Iron Curtain/localisation/english/FRE_Dien_Bien_Response_l_english.yml`
- Castor: `Cold War Iron Curtain/common/scripted_effects/FRE_Castor_Effects.txt`, `Cold War Iron Curtain/common/national_focus/FRE_50s_Indochina.txt`, `Cold War Iron Curtain/common/decisions/FRE.txt`, `Cold War Iron Curtain/events/FRE_Events.txt`
- Pollux: `Cold War Iron Curtain/common/scripted_effects/FRE_Pollux_Effects.txt`, `Cold War Iron Curtain/common/scripted_triggers/FRE_Pollux_Triggers.txt`, `Cold War Iron Curtain/events/FRE_Pollux_Events.txt`
- Atlante: `Cold War Iron Curtain/common/scripted_effects/FRE_Atlante_Effects.txt`, `Cold War Iron Curtain/common/scripted_triggers/FRE_Atlante_Triggers.txt`, `Cold War Iron Curtain/events/FRE_Atlante_Events.txt`
- French Indochina command: `Cold War Iron Curtain/common/factions/templates/FRE_French_Indochina.txt`, `Cold War Iron Curtain/common/scripted_effects/FRE_Indochina_Command_Effects.txt`, `Cold War Iron Curtain/common/scripted_triggers/FRE_Indochina_Command_Triggers.txt`, `Cold War Iron Curtain/common/scripted_effects/IC_Indochina_Command_Test_Effects.txt`

## Verification completed

- 2026-08-13 faction-isolation follow-up: `git diff --check`, Clausewitz structure checks for all touched gameplay files, and `python3 tools/loc_audit.py --check` pass. Source checks confirm NLF startup/restored-save membership, the hidden no-call rule on both faction templates, `-1000` AI get/call/join desire plus call refusal on all three faction identities, and application of the Kingdom of Laos safeguard before its declaration tick. The user's initial playtest confirmed that the faction rework functions correctly. Longer-run defection/dissolution branches and isolated Laos edge cases remain useful coverage, not blockers to this checkpoint.
- 2026-08-12 French Indochina command static verification passed for the initial implementation, but its NLF-separation assumption was superseded by the 2026-08-13 engine finding. NLF membership is restored; both faction templates and the faction-identity spirits suppress calls. The corrected model received initial engine acceptance on 2026-08-13.
- `git diff --check` passed at the stopping point.
- Raw Clausewitz brace balance passed for the modified/new gameplay text files.
- Adjacency rows retain ten fields; 57 campaign routes are unrestricted and 35 Laos/divider routes remain assigned.
- Targeted invariants passed for THO ownership/OOB/custody, VIN capital, Cao-Bac lifecycle/result flags, campaign state policy, overextension cleanup, TAI OOB, focus wiring, and localization uniqueness.
- The environment cannot launch HOI4. Engine results come from the user's external full VIN playtests.
- Latest external runs confirmed practical campaign access, a complete historical-AI path through historical Geneva, and a viable human-FRE Northwest defense. They also supplied the off-front, MEO, and local-supply failures addressed by the newest follow-up.
- Checkpoint patch: `git diff --check`, raw brace balance, new event/effect/trigger uniqueness, English localization uniqueness, response ownership neutrality, legacy Lorraine entry-point retirement, and Geneva peace-gate preservation all pass targeted static checks.
- 2026-08-10 containment follow-up: `git diff --check` and raw braces pass across every modified/new gameplay file. Targeted invariants confirm unique VIN/FRE/VIE/NUN/MEO strategy definitions, one reduced campaign-wide poor-odds override, no tag-wide FRE-vs-VIN campaign front, no VIN request for Ha Giang, three-state supply coverage, VIE-inclusive rear-area overextension, and no adjacency edit.
- External acceptance after that follow-up: multiple Northwest runs confirmed working southern supply, MEO self-defense/recovery, historical AI outcomes, and continued player-led operational freedom.
- Hoa Binh response: `git diff --check`, raw braces, unique effect/event/AI/state-modifier/localization definitions, single live-parent event ownership, parent-only territory/peace resolution, supersession ordering, and cleanup invariants pass targeted static checks.
- External Hoa Binh acceptance: multiple mixed player/AI runs confirmed consistent outcomes and clean mechanics. Those runs exposed the former player-facing balance/clarity failure in which Amarante felt strictly worse than continuing to hold; the current follow-up addresses it and awaits retesting.
- 2026-08-10 Hoa Binh payoff/clarity follow-up: `git diff --check`, targeted raw-brace checks, new effect/localization uniqueness, result-gating, Amarante ownership neutrality, direct Patience protection, Na San callback uniqueness, and the scoped raw-tag/implementation-language localization audit all pass. Engine acceptance of the new payouts remains pending.
- Historical baseline, superseded by the focus fork: the 2026-08-11 autonomous post-DBP closure repair passed its static checks and its ordinary destroyed-NLF route ran successfully on 2026-08-12. That runtime result remains useful regression evidence for the shared peace gate and conference backend, but it is not acceptance of the new focus-owned queue.
- 2026-08-11 combined Dien Bien Phu/Castor patch: `git diff --check`, raw Clausewitz brace balance across all changed/new gameplay `.txt`, and `python3 tools/loc_audit.py --check` pass. New effects, triggers, events, modifiers, and English keys are unique. Targeted checks confirm four live defensive postures, exact Condor/Vulture hooks, parent-before-recorder ordering, exact province `4529`, fourteen consecutive Castor hold days, a thirty-day visible timer/backstop, no remaining generic operation ID `5`, complete orphan/dissolution/theatre cleanup, and no Castor ownership/peace/campaign/Geneva mutation.
- 2026-08-12 engine acceptance: a complete player/AI historical-path test passed. Lorraine's live response cleanup, state defense, and result were correct; historical AI reached the historical outcome; NLF destruction was followed by the historically timed post-Dien Bien Phu Geneva Conference through the preserved peace gate. Alternate Castor commitments, defensive postures, and forced failure/supersession terminals were not individually reported and remain optional diagnostic coverage.
- 2026-08-12 Operation Pollux patch: `git diff --check`, raw Clausewitz brace balance across all changed/new gameplay `.txt`, and `python3 tools/loc_audit.py --check` pass. New effects, triggers, events, focus/mission entries, AI strategies, diagnostics, and English localization keys are unique. Pixel-map verification confirms the exact `13765 -> 13762 -> 4529` route. Targeted checks confirm the three commitments, consecutive-day reset/backstop, exclusive results, early-campaign handoff, survivor-group cleanup, and complete ownership/peace/campaign/Geneva neutrality. Engine acceptance is pending.

## Accepted content patch: Castor into the Dien Bien Phu defense

The defensive-response and Castor slices are implemented and their full historical path passed the combined playtest. Do not recreate either package or restore Castor's generic operation ID `5` path.

The natural test sequence is now:

- Complete Operation Castor, choose full or limited commitment, deliberately break control once to confirm the consecutive-day reset, then establish the camp after fourteen uninterrupted days.
- Launch VIN campaign ID `3` and select one CEFEO posture. Confirm that Castor's establishment modifier is gone, the siege modifier starts only with the campaign, and exactly one defensive conclusion is recorded before the parent Dien Bien Phu/Geneva recorder.
- Use the Castor and campaign console effects to force deadline failure, theatre supersession, the alternate defensive postures, Condor corridor edges, and both Vulture answers without replaying the entire tree.

Treat alternate Castor/Dien Bien terminals, Amarante/day-`210`, Lorraine focus-order, and funded/negotiated southern routes as opportunistic branch coverage, not as reasons to reopen accepted lifecycle code without a concrete engine regression.

## Resume here

1. Run a fresh 1949-to-Geneva game in debug mode with `human_ai`, following `CWIC Backup/documentation/Indochina_AFK_Playtest.md`. Preserve `_local/logs/game.log` and `_local/logs/error.log` before launching the game again.
2. Treat any `VIN_hidden_AI_buffs_removed` or `participant_envelope` failure as a code regression. Compare campaign completion days and CEFEO objective-hold days with the recorded first run.
3. Read the 180-day `FORCE_HEALTH` series for FRE, TAI, TAM, NUN, and THO. The acceptance target is that unrelated crown domains retain armies through the 1952-54 operation sequence instead of being consumed by CEFEO's wars.
4. Review every `ENVELOPE` application/clear transition. AI spillover within an objective state may briefly trip the severe penalty, but it should withdraw/clear rather than expand onto unrelated fronts.
5. Retain the prior checks for THO's two declaration-day garrisons, exact objective markers, armistice cleanup, premature peace conferences, Castor callbacks, Pollux/Atlante, and Final Push.

## Latest 2026-08-19 balance/lifecycle pass

- Pathet Lao's FRA-owned mission clocks are activatable, cleanup removes all
  mission variants, and daily 90/45-day backstops prevent a stuck raid.
- Hirondelle/Mouette/Brochet cannot launch while `Laos_Raid_Active` is set.
- VIN and FRE AI no longer select ambient raids; human raid access is retained.
- Five duplicate VIN focus awards worth 500 Communist Struggle points are gone.
  Campaign, operation, response, and Laos-result score swings are sharply
  reduced; escalation pacing was not changed.
- VIN's Geneva seed uses score/50 and Communist leverage/4. Its major focus and
  post-DBP leverage awards were reduced, and PRC/SOV use leverage/5.
- AFK logs now include `STRUGGLE_SCORE`, `GENEVA_LEVERAGE`, `GENEVA_WEIGHT`, and
  the Pathet Lao raid launch/result/timeout contract. Re-run from 1949 through
  Geneva and compare the Communist lead to the requested 100-200-point band.

## Deferred work and known limits

- A second graduated overextension tier; the current contract intentionally uses one severe tier.
- Generalized response-package work beyond the implemented Northwest/Lorraine, Hoa Binh, Vinh Yen, Mao Khe, Day River, Na San, and Dien Bien Phu cases, plus the remaining historical operations beginning with Dak Doa.
- Genuine Northwest-failure recovery route into the Dien Bien focus; current ownership gate remains.
- Extended engine coverage of French Indochina startup migration, intentional defection exits, and dissolution ordering; the core faction membership and separate-war behavior have initial acceptance.
- Removal of now-unassigned legacy adjacency-rule definitions after more engine coverage; their CSV assignments are already retired.
- Named historical THO colonial leadership research.
- Alternate-terminal balance coverage for Castor/Dien Bien, Lorraine, the post-DBP southern choices, and the revised Hoa Binh payout values. Their historical path and Hoa Binh's underlying lifecycle are accepted.

## Guardrails for the next session

- Treat the canonical design ledger as authoritative and update its implementation ledger when a new patch starts, becomes code-complete, or receives engine results.
- Preserve user changes in a dirty worktree; specifically do not restore the removed NUN autonomy block.
- Keep the normal Geneva peace gate. The zero-division terminal should close only the residual VIE-NLF war through its guarded armistice, then pass through that gate rather than bypassing it.
- Keep all campaign exits on the shared resolver/cleanup path.
- Keep superseded campaigns rewardless and ownership-neutral.
- Keep Castor preparatory: it may establish/fortify the camp and deploy the garrison, but it must never transfer territory, end a war, resolve campaign ID `3`, or write the Dien Bien Phu/Geneva battlefield result.
- Keep Pollux preparatory: it may preserve or lose the Lai Chau force and reinforce the established camp, but it must never transfer territory, make peace, delay campaign ID `3`, or write the Dien Bien Phu/Geneva battlefield result.
- Keep Atlante ownership-neutral: it may pressure the two Interzone V objectives and alter which reserve reaches Dien Bien Phu, but it must never transfer state `1287`, declare or end the southern war, move the parent campaign deadlines, or write a Dien Bien Phu/Geneva result.
- Keep both Indochina no-call rules, the negative faction-spirit AI call weights, and fixed CEFEO leadership. Preserve NLF's startup membership in Hanoi's faction, but never allow that membership—or French Indochina membership—to broaden a scripted campaign, the Pathet Lao raid, or the base VIE-NLF war. Do not make VIE/FRE direct French subjects during the live theatre.
- Never expose raw country tags or implementation terms in player-facing prose when an immersive country, army, organization, or territorial name is available. Internal keys, scopes, and variable references are exempt.
- Every localization `.yml` file must remain encoded as UTF-8 with BOM (`EF BB BF`). Plain UTF-8 files may silently fail to load or display in HOI4. Preserve the BOM when editing an existing file and include it when creating a localization file; verify the first three bytes before handoff. The user already repaired the recent affected files—do not rewrite or normalize their encoding.
- Keep Laos/divider movement rules until their separate theatre redesign.
- The underlying checkpoint is committed locally; the Pollux/Atlante and French Indochina command batch is uncommitted. Pushing remains a separate user action.
## 2026-08-17 FRE limited-operation and preparation renovation

- The legacy Hirondelle, Mouette, and Brochet production path has been replaced. Focus completion now enters a War Credit commitment prompt and a daily exact-province resolver; it no longer launches an arbitrary one-province border war, spawns permanent colonial divisions, or decides the result with arithmetic.
- Exact objectives are Lang Son/Loc Binh (`9948`, `13761`) for Hirondelle, Phu Nho Quan (`11909`) for Mouette, and the Hung Yen sector (`13755`) for Brochet. Results use clean/costly/aborted/failure/superseded and every exit shares cleanup. Limited wars are made white only when the package created them; no operation transfers ownership.
- Vinh Yen, Mao Khe, Day River, and Na San are now VIN limited campaigns `5`-`8`. They use exact objectives (`12075`; `13772`; `1185`, `13753`, `13755`; and `13757`) and five consecutive days of control. Vinh Yen province `12075` now starts under TAI control; VIN retains adjacent `16526` as its approach.
- FRE preparation focuses now grant persistent readiness and live response choices instead of inventory arithmetic followed by delayed battle events. Vinh Yen feeds Mao Khe, Mao Khe feeds Day River, and Amarante/Lorraine feed Na San. Na San and Brochet results soften Castor cost without gating it.
- Hirondelle clean/costly results unlock a real paratrooper interdiction decision against the supply pool of a live VIN campaign. Castor waits for a terminal Brochet result, and Final Push now consolidates actual Mouette/Atlante results instead of granting an unconditional `+200` score and `+175` escalation.
- A one-time startup migration maps old results/readiness, removes legacy missions, and relaunches unresolved completed-operation focuses through the new commitment prompt when the theatre remains open. Old queued result/battle events are guarded against duplicate payouts.
- State-scoped AI orders concentrate both sides on the restored campaign and operation objectives and terminate with their owning active flag. A primary VIN campaign supersedes a crossing limited operation; France carries the daily operation heartbeat so VIN's disappearance cannot strand cleanup.
- Brochet and Na San outcomes now alter Castor's displayed eligibility price and its actual debit. Final Push bypasses cleanly after theatre closure instead of waiting forever for terminal flags from bypassed operations.
- Static acceptance on 2026-08-17: `git diff --check`, raw Clausewitz brace balance across all 25 changed/new gameplay `.txt` files, the 22-file SEA localization audit, UTF-8 BOM checks for all four edited localization files, new event/effect/trigger/localization uniqueness and reference checks, both focus-tree acyclicity checks, exact-objective/owned-peace invariants, one daily operation carrier, and legacy-result guards all pass. Engine acceptance remains pending; the earlier 1956 playtest is the regression baseline, not acceptance of these newly converted packages.

## 2026-08-17 VIN playtest integration repair

- Campaign teardown now owns the whole temporary battle, not only its nominal target. Finish attempts white peace with FRE, France, TAI, TAM, THO, VIE, and NUN, then the guaranteed VIN daily tick retries while `VIN_Limited_Campaign_Armistice_Pending` remains. Laos tags are deliberately outside the sweep.
- 2026-08-17 FRE-operation collision repair: the retry now yields and clears itself when `FRE_Limited_Operation_Active` owns a new operation. `fre_operation_launch` also clears a stale VIN retry before declaring, and the common operation window requires FRE and VIN to be at peace so Hirondelle, Mouette, and Brochet always own a fresh isolated war. This prevents the campaign safeguard from instantly white-peacing the 1953 operations.
- Limited-campaign declaration records ownership even if subject/faction propagation made the target technically at war before the branch evaluated. `test_vin_campaign_armistice_cleanup` invokes the production sweep and reports whether a retry remains necessary.
- THO's Cao Bang/Lang Son plan activates before war, raises both state requests/theatre demand, suppresses allied and rear fronts, reduces garrison diversion, and forbids allied-border defense. The two historical battalions still begin in their respective states.
- The misplaced VIN militia in TAI-controlled Vinh Yen now begins on the VIN-controlled Hoang Lien Son approach.
- Vinh Yen, Mao Khe, Day River, and Na San now display an exact pre-launch contract, a persistent objective card, exact target-province highlighting, named provinces, and the live consecutive-hold counter. Major campaigns do not display the irrelevant five-day counter.
- Province visibility follow-up: the four cards now use `highlight_provinces` rather than broad state targets. While each campaign is live, its zero-value objective provinces receive reversible `+1` victory-point markers so their localized names render on the map: Vinh Yen `12075`, Mao Khe `13772`, Day River `1185`/`13753`/`13755`, and Na San `13757`. Per-campaign flags prevent stacking, the daily tick repairs active old saves, and common finish subtracts the markers.
- Static verification passes. Focused engine acceptance remains required for declaration-day THO deployment, exact province-highlight visibility, temporary VP-name appearance/removal, the 0/5 counter, full campaign armistice teardown, survival of the 1953 FRE operation declarations, and non-interference with Laos wars.

## 2026-08-21 AFK log audit and next development queue

- The returned `_local/logs/game.log` and `_local/logs/error.log` cover a complete 1949-to-Geneva run followed through October 1955. The campaign lifecycle is broadly healthy: every VIN campaign/operation reached a terminal result, hidden VIN AI-buff checks passed, participant-envelope checks passed, armistice/operation cleanup passed, and Geneva concluded without a premature peace conference.
- This run is not balance acceptance. The Communist Struggle margin reached the requested `+100` band in May 1953, then rose to `+353` in October 1953, `+538` in April 1954, and ended Geneva at `+506`; the requested target remains approximately `+100` to `+200`. Add temporary source-specific score-delta telemetry before changing values. The one-time `+350` award in `indochina_struggle_auto_trigger_communist_victory_preparation` in `common/scripted_effects/CWIC_Struggle_Effects.txt` is a prime suspect, but the late-war jump must be confirmed from the log before tuning.
- Two AFK validation failures are actionable:
  - `_local/logs/game.log` records `THO_Lang_Son_garrison_present` failing at the Cao-Bac declaration while the Cao Bang check passes. Trace the THO OOB/AI movement between startup and the 20 December 1949 declaration; do not weaken the campaign until the expected historical deployment is either held or the validator is corrected.
  - Brochet (`operation=4`) launched on 5 June 1953 while `Laos_Raid_Active` was set, immediately followed by `FRE_operation_blocked_during_Laos_raid`. The trigger in `FRE_operation_triggers.txt` is correct, but `fre_operation_commit` in `FRE_Operation_Effects.txt` does not recheck the flag. Add an authoritative commit/launch guard before charging War Credits or activating the operation; focus availability alone is not sufficient.
- Remove the stale `vin_ai_prepare_campaign = yes` call from `VIN_Campaign_Effects.txt` or restore a valid replacement. `_local/logs/error.log` reports the undefined effect twice during static parsing. This is a code defect even though the run continued.
- Campaign pacing remains too easy in the middle sequence: Vinh Yen, Mao Khe, Day River, Hoa Binh, and Na San resolved cleanly in roughly 8-28 days; Dien Bien Phu resolved cleanly in 71 days. Northwest was the only costly VIN campaign, resolving after 201 days. Envelope penalties activated and cleared, but the result pattern still warrants objective-pressure/AI tuning after the lifecycle guards are repaired.
- Do not treat every crown-domain disappearance in the force-health series as an unexpected collapse. Clean Cao-Bac annexes THO, clean Hoa Binh annexes an empty TAM, and clean Dien Bien Phu annexes TAI through the intended campaign effects. LAO reaches zero divisions during the 1953 Laos sequence and is later marked collapsed by the post-Geneva health check, but the ownership result is the Geneva settlement path already documented above, not evidence that a Laos total-loss mechanic fired. NUN remains the one postwar force-health transition that should receive a separate ownership/capitulation trace.
- The following runtime errors should be cleaned before the next acceptance run: the NLF character `NLF_Tran_Quoc_Buu` is retired from VIN scope in `events/VIN_Events.txt`; Geneva cleanup references invalid ideas `VIN_paramilitarism_focus` and `VIN_cold_war_civil_war_ideological_idea`; MEO attempts to add an already-existing Ho Chi Minh Thought leader role; Pathet Lao units request unavailable motorized equipment; and the LAO focus `LAO_50s_Refuse_to_Demobilize` lacks its icon. The unlocked VIN division-template warning is lower priority. Global entity/animation and generic AI-command noise is not a VIN/FRE blocker.
- Natural branch coverage did not reach Atlante, Final Push/consolidation, or several alternate Castor/Pollux/Dien Bien/southern-response terminals. Keep these as deliberate console/branch tests after the baseline run is clean. Defer Dak Doa and additional Diem/content expansion until the score, operation race, THO deployment, and runtime-error baseline are resolved.

### Next session order

1. Remove `vin_ai_prepare_campaign` and fix the Brochet/Laos commit guard.
2. Trace and repair or redefine the THO Lang Son declaration-day contract; add a NUN postwar ownership/capitulation check.
3. Add temporary score-award/delta logging and identify the late-1953/early-1954 overshoot before retuning campaign or Geneva values.
4. Fix the focused runtime errors, then run a fresh 1949-to-Geneva `human_ai` playtest and preserve both logs.
5. Use console diagnostics for Atlante, Final Push, and alternate response terminals; only then resume deferred historical content.

## 2026-08-21 queued repair implementation

- The stale undefined `vin_ai_prepare_campaign` call is removed. `fre_operation_commit` now treats an active Laos raid as an authoritative supersession condition before commitment tier, War Credits, Patience, ideas, flags, or war declaration are touched. A guarded attempt records `FRE_operation_commit_guarded_during_Laos_raid`; it must not be followed by a limited-operation launch.
- Placement telemetry proves THO's Lang Son battalion starts correctly on 23 May 1949 but leaves by 21 June, long before Cao-Bac. Peacetime front strategy cannot enforce a fixed base. If either historical post is empty when campaign `4` declares, the AI-only territorial formation is now re-formed as exactly one battalion in Cao Bang and one in Lang Son before the war and launch validator run. The campaign objective and THO force scale are unchanged.
- NUN now emits an immediate postwar existence/capitulation/ownership snapshot and a second terminal snapshot if it later capitulates or disappears. This will identify whether the observed October 1954 transition is annexation, capitulation, or a settlement ownership change.
- Temporary Struggle telemetry now logs every daily component delta. The one-time `+350` Communist award in `indochina_struggle_auto_trigger_communist_victory_preparation` also emits an explicit `SCORE_AWARD` source record. No balance value was changed: match that record against the daily delta and the late-1953/early-1954 jump before tuning.
- Focused runtime repairs are implemented: Tran Quoc Buu retires in NLF scope; Geneva removes the valid generic `paramilitarism_focus` and `cold_war_civil_war_ideological_idea`; Lo Van Hac is promoted through his predeclared ideology roles instead of adding a duplicate role (with the prior expiry and trait preserved in the character definitions); Pathet Lao receives a valid truck variant before its field-force OOB loads; and `LAO_50s_Refuse_to_Demobilize` uses an existing Laos-war icon.
- Static verification passes: scoped and repository `git diff --check`, raw Clausewitz brace balance across all 17 changed gameplay `.txt` files, targeted lifecycle/reference assertions, and `python3 tools/loc_audit.py --check` over all 22 SEA localization files.
- Engine acceptance is still required. The next natural step is the fresh 1949-to-Geneva `human_ai` run from `CWIC Backup/documentation/Indochina_AFK_Playtest.md`, preserving both logs. Confirm both THO declaration checks pass, a Brochet/Laos overlap records the guard without a launch or debit, `SCORE_AWARD` explains (or rules out) the overshoot, the NUN terminal trace appears, and the five focused runtime errors do not recur. Only after that baseline is clean should console branch coverage and Dak Doa resume.
# 2026-08-22 Dak Doa / Northwest recovery implementation

Implementation has begun from the accepted 2026-08-21 Indochina baseline. The
new work is additive: NLF owns the isolated Dak Doa lifecycle and its optional
NLF-FUL war, while VIN campaign ID 9 owns the one-time Northwest recovery. No
accepted Castor, Lorraine, Hoa Binh, Dien Bien, post-DBP, Geneva, faction-call,
or NUN lifecycle is being migrated or reverted.

Code-complete checkpoint: the NLF-owned Dak Doa parent, all three CEFEO
responses, permanent results/callbacks, VIN campaign ID 9 recovery, historical
AI ordering, missions, localization, shared response-contract logging, console
diagnostics, and unified checkpoint playtest are implemented. Static checks pass;
the unified engine run is still pending and must be recorded here after it is
performed. Do not describe this batch as engine-accepted before that result.

First engine feedback found a campaign `9` settlement defect: a successful
recovery peaced its direct TAI target but left VIN at war with FRE after FRE
joined the same recovery conflict. The recovery now snapshots VIN's relevant
pre-launch wars, explicitly white-peaces every newly introduced French-aligned
participant, and retries that scoped cleanup daily until none remain. It does
not close a VIN war recorded before campaign `9`. AFK and console diagnostics
now expose FRE/TAI war state and require the scoped cleanup-complete flag. This
repair is statically verified but still needs the Northwest checkpoint retest.

## 2026-08-23 AI playtest audit and revised priority queue

The returned `_local/logs/game.log` and `_local/logs/error.log` are a new historical-AI run from 23
August and supersede the 21 August logs for current behavior. This was a useful
lifecycle pass but not battlefield-AI, balance, Geneva-sequencing, or UI
acceptance.

### What the run accepted

- No `IC_AFK|FAIL` record was emitted. Both Cao Bang and Lang Son declaration
  checks passed, all recorded VIN campaign armistices and CEFEO limited-operation
  wars cleaned up, hidden VIN AI packages remained absent, participant-envelope
  checks passed, and Final Push consumed the Mouette/Atlante terminal records.
- Recorded VIN results were Cao-Bac clean on day `51`, Vinh Yen clean on day
  `8`, Mao Khe failure on day `36`, Day River costly on day `38`, Hoa Binh clean
  on day `66`, Northwest clean on day `102`, Na San clean on day `11`, and Dien
  Bien Phu clean on day `30`.
- Hirondelle failed, Brochet succeeded cleanly, and Mouette failed. Castor began
  on 30 January 1954 and established the airhead on 12 February. Campaign `3`
  began on 15 February, superseded unfinished Pollux, and ended with the camp's
  fall on 16 March. Atlante opened during the siege and was then superseded.
- The five focused runtime errors repaired on 21 August did not recur. NUN's
  new terminal trace resolves the earlier ambiguity: at the 31 May settlement
  NUN no longer existed and state `1281` belonged to VIN.

### Hard defects found before balance work

- `_local/logs/error.log` rejects `political_power > 49` in the Northwest-recovery focus at
  `common/national_focus/VIN_50s.txt:5599`. Replace it with a supported political
  power check before attempting campaign `9` acceptance.
- `_local/logs/error.log` rejects `defender_modifier` in every rework-local dynamic modifier
  in `common/dynamic_modifiers/0_dynamic_modifiers.txt`. This affects the
  contested-objective, Hoa Binh, Dak Doa, Dien Bien Phu, Castor, Condor, Vulture,
  and other holdout packages. Do not tune their numbers until their supported
  scope/application model is repaired and confirmed in-engine; otherwise the
  intended defender-only contract is not trustworthy.
- `ic_northwest_recovery_test_inspect` still does not print the scoped
  `VIN_Campaign_Northwest_Recovery_Cleanup_Complete` flag even though the test
  protocol requires it. Add that field before the recovery checkpoint retest.
- `events/SWF_VIN_events.txt` fires `SWF_VIN.17` in NLF scope, but both current
  options require `tag = VIN`; the run therefore reports "No valid option" on
  17 February 1953. Restore the promised NLF acknowledgement option or stop
  firing the player-choice event in NLF scope.
- `Indochina_Flavor_Events.txt` also tries to complete missing Siam focuses
  (`SIA_Coup_Fails`, `SIA_The_1952_Elections`, and
  `SIA_Plaek_Phibunsongkhram_Re_Elected`). These are adjacent regional runtime
  errors, not evidence for the VIN/FRE battlefield behavior, and may follow the
  four rework-local blockers above.

### Battlefield and operation findings

- Vinh Yen and Na San were effectively undefended and fell as soon as VIN
  arrived. CEFEO/TAI require launch-time objective defense demand and a local
  minimum presence, not only broad state requests.
- Mao Khe and Day River exposed the opposite attacker problem: VIN assembled
  enough nearby formations but would not make favorable objective attacks.
  Review poor-odds suppression, `manual_attack`, objective-province pressure,
  and competing lower-Tonkin fronts before changing combat statistics.
- During Northwest, CEFEO/TAI concentrated around Lai Chau and province `12319`,
  apparently treating raid outposts as higher priorities than the campaign
  corridor. Tonkin and Na San were left open, MEO did not visibly hold Ha Giang,
  and VIN entered Dien Bien Phu before its named campaign. Audit raid/outpost
  unit demand against campaign demand, reinforce MEO's self-only stationing,
  and prevent campaign `1` AI from advancing into state `671` even when generic
  fronts or access override the existing negative request.
- The Pathet Lao invasion ended in the intended stalemate, but four LOS
  divisions sat in province `13738` while Luang Prabang was open. The Laos
  objective AI needs explicit capital defense/attack allocation rather than a
  general state/front order.
- Lorraine produced a terminal callback but remained opaque to the observer.
  Its live posture/result needs to appear in the outcome UI and telemetry at
  selection, not only after parent resolution.
- Hirondelle's present exact-objective limited war is mechanically clean but is
  a poor representation of the historical paratrooper raid that destroyed
  caches around Lang Son. Rework it as an ownership-neutral airborne
  interdiction/raid package with cache-destruction and withdrawal objectives,
  not a conventional front-clearing war.
- Brochet's observed behavior was acceptable. Do not reopen it without a
  concrete regression.
- Mouette currently directs CEFEO toward state `1762`, allowing the ordinary
  front to choose attacks such as the Hoa Binh corridor. Its historical role was
  a southern-Tonkin/Red-River-Delta sweep intended to engage and destroy Viet
  Minh formations. Give it exact sector objectives and prevent both sides from
  abandoning the package for the VIE border while it is live.
- Castor/Pollux scheduling was too late: the airhead established only three days
  before campaign `3`, and Pollux was immediately superseded. Shorten or remove
  the preparatory focus delays and gate the DBP launch on a usable preparation
  window. After the invalid defender-only modifiers are repaired, strengthen
  the camp's actual garrison/output and aim for a materially longer siege than
  the observed thirty days.
- During the DBP war VIN ignored CEFEO penetrations elsewhere in Tonkin while
  winning the camp and taking the scripted peace. Preserve the exact camp
  objective, but add a bounded home-front reserve/containment response so the
  rest of Hanoi's territory is not freely occupied during the siege.

### Geneva, Struggle UI, and southern-war findings

- Dien Bien Phu fell on 16 March, the VIN strategy briefing appeared on 17
  March, and scripted Geneva concluded on 31 May without telemetry showing that
  `VIN_Push_for_Negotiations` had been selected. The shared FRE/other pursuit
  routes can still convene the conference around the new VIN fork. Add
  source-owner telemetry for every Geneva pursuit/announcement and enforce a
  post-DBP choice/grace latch so a communist camp capture cannot bypass the
  visible VIN decision. Preserve the peace gate; do not solve this with an
  immediate forced conference or by disabling legitimate non-DBP conference
  routes globally.
- Expand "The Wars Behind the Table" from the six old summary lines to show the
  recorded VIN campaigns, CEFEO operations, response-package results, and their
  actual Struggle/leverage changes. A player should be able to distinguish
  clean, costly, failure, withdrawal, and supersession without watching every
  province or reading raw flags.
- The score correction improved the mid-war sample: the Communist margin was
  `+184` in May 1953, inside the requested `+100` to `+200` band. It then climbed
  to `+364` in October 1953 and `+429` in April 1954. No source-specific `+350`
  award fired; the log instead shows repeated ambient `+25` and `+50` Communist
  deltas. Audit those recurring sources before another score reduction.
- VIE fielded `34-38` divisions while NLF remained at `5`; NLF disappeared by
  27 April 1954. Rebalance the southern war by reducing the effective VIE
  wartime division-limit/build advantage and/or giving NLF a bounded force and
  equipment sustainment package. Do not merge the southern war into VIN's
  northern campaigns.

### Implementation order from this checkpoint

1. Repair the engine-rejected script contracts (`political_power` and all
   `defender_modifier` uses), the NLF `SWF_VIN.17` no-option path, and recovery
   inspection telemetry. Clean the missing Siam focus calls in the same scoped
   runtime pass if their replacement focus IDs are unambiguous.
2. Make the post-DBP VIN choice authoritative against automatic pursuit and add
   Geneva-source logging.
3. Expand the Struggle outcome GUI so later balance tests expose all campaign,
   operation, response, score, and leverage results.
4. Repair objective allocation in the early battles, Northwest/MEO/raid
   interaction, Na San, Laos, and the Tonkin reserve behavior.
5. Rework Hirondelle and Mouette's operational contracts; retain Brochet.
6. Accelerate Castor/Pollux sequencing and rebalance Dien Bien Phu only after
   the defender-only modifier repair is engine-valid.
7. Rebalance NLF versus VIE and trace the recurring Communist score awards.
8. Run targeted checkpoint tests first, then one unified historical-AI pass.
   Dak Doa and campaign `9` remain code-complete but unaccepted because natural
   Geneva closed before Dak Doa and the recovery branch was not exercised.

## 2026-08-23 implementation pass after playtest review

The ordered corrective pass is code-complete and deliberately has not received
another engine playtest yet. The user asked to hold the next run until this
batch and its review were complete.

- Rework-local parser blockers are repaired: `has_political_power` replaces the
  invalid trigger, unsupported `defender_modifier` entries are gone, NLF has a
  valid `SWF_VIN.17` acknowledgement, the recovery inspection exposes cleanup,
  and the three missing Siam focus-completion calls were removed.
- A communist Dien Bien Phu result now creates a narrow authoritative VIN
  strategy latch. Shared Geneva invitation, pursuit, wrap-up, panic, and
  headless-resolution paths defer without accumulating leverage until VIN has
  selected negotiations or southern escalation. Pursuit source IDs are logged.
- VIN receives observer-only CEFEO briefings, map-highlight missions, and
  conclusion reports for Lorraine, Hirondelle, Mouette, Brochet, Castor,
  Pollux, and Atlante. They reveal neither commitment tiers nor hidden result
  math and cannot change an operation's outcome.
- "The Wars Behind the Table" now includes exact Struggle standings, Geneva
  leverage, every VIN campaign result, and the named CEFEO operation journal.
- Objective allocation now reinforces Vinh Yen, Na San, Northwest/Ha Giang,
  the Tonkin reserve, and Luang Prabang while suppressing unrelated VIE and
  Laos fronts during VIN set-piece attacks.
- Hirondelle is now an ownership-neutral airborne cache raid. It uses airlift
  availability and commitment-scaled duration, creates no FRE-VIN war, takes
  no territory, and on success removes bounded VIN equipment/Campaign Supply.
  Mouette remains the temporary limited war but is constrained to Phu Nho Quan
  and the southern Red River Delta sector. Brochet is unchanged.
- Castor and Pollux take about ten and five days respectively and receive a
  strong historical-AI priority. Supported camp modifiers were retuned to make
  standard/maximum holdouts and the forming airhead materially tougher.
- NLF receives a bounded wartime reconstitution spirit and 4,000 cached rifles;
  it remains independent of VIN's northern campaign lifecycle.
- Review of `_local/logs/game.log` found the recurring `+25`/`+50` Communist deltas align
  with ordinary completed-focus ledger awards across many factions, not one
  duplicated campaign award or the suspected `+350` grant. No blind global
  score reduction was applied; the expanded GUI makes the next sample auditable.

Next engine work is one targeted smoke pass (new events/missions, Hirondelle
without war, Mouette envelope, Geneva deferral), then the held unified
historical-AI run. Balance targets remain objective defense at launch, DBP
materially longer than 30 days, a useful surviving NLF field force, and no
conference before VIN's explicit post-DBP choice.

## 2026-08-29 combined acceptance protocol

Tester availability requires the corrective-pass smoke test and full
historical-AI acceptance run to share one fresh 1949 game. The reconstructed
protocol is `CWIC Backup/documentation/Indochina_AFK_Playtest.md`. It front-loads
parser and core-lifecycle stop conditions, then continues balance, allocation,
force-health, Struggle, and Geneva observation through the scripted settlement.
Balance failures are recorded and carried through the run; parser, stuck
lifecycle, premature peace-conference, and post-Dien Bien Phu choice-bypass
regressions remain early-stop conditions. After evidence-backed repairs, use
the checkoff to close accepted systems before resuming remaining rework content.

## 2026-09-28 run review and resume point

The 2026-09-02 combined AFK run was reviewed from telemetry. The full record,
accepted systems, and queues are in the 2026-09-28 section of
`CWIC Backup/documentation/VIN_FRE_Tree_Expansion_Design.md`. The checkoff is
completed in `Indochina_AFK_Playtest.md`.

- Accepted: lifecycle/cleanup, THO deployment, Hirondelle raid, Castor/Pollux
  window, Atlante and Final Push, post-DBP choice authority over Geneva, and
  Struggle calibration (final margin `+135`).
- Failed (balance): Dien Bien Phu fell on day 24; Vinh Yen/Na San fell in
  11-12 days; NLF collapsed by April 1954 (VIE 44 divisions); Metropole
  Patience at 0 from 1952 to Geneva.
- Testing: no tester time is available. Batch statically verified patches and
  plan one consolidated playtest later; do not wait on engine runs.

### Next session order

Updated 2026-10-09. Remaining order:

0. Check 59 passed in `2026-10-09b`. Next AFK run: check 61 (resupply no
   longer blocked by the Nam Bo focus) and re-score 58. Then the deferred
   Trung Phan (VIE) issues the user raised on 2026-10-09, including
   `VIE_Events.txt:7555`, and the State of Vietnam army-cap overrun.
1. Next AFK run: score checks 53-58 first. 55 and 58 need a hover/glance
   in a player game; 56-57 come from `IC_AFK|NOTICE`. The VIN supply step now runs on
   every pulse (monthly), so Campaign Supply income, patronage and the
   southern resupply all rise. If VIN supply runs away, lower the
   per-month amounts. Keep `surrender_limit = 0.5`; watch whether VIN is
   now too strong (Hoa Binh day 26 in 2026-10-03c).
2. Deferred design items (user, 2026-10-03): the Geneva Laos clause, and
   now the Pathet Lao capitulating to CEFEO during Lower Laos (2026-10-03c).
   Not to be fixed until the user raises them.
3. Next consolidated AFK run: score ledger checks 1-58. Passed:
   23, 30, 31, 33, 34, 36, 37, 39, 48, 50, 51, 52. Partial: 38.
   Failed: 35 (before the surrender limit), 46 (twice; passed in 03c), 49.
   Still open:
   9 and 13 (visual), 11, 12, 15, 16, 17-22, 24-28, 32, 40, 42, 43, 44, 45,
   47, 53-58.
4. Read the `NLF_RESUPPLY` series, the penalty days, and the Dien Bien Phu
   duration first. Retune the resupply values only if the south is now too
   strong or VIN supply is starved. Also cover the Pathet
   Lao raid hardening and the older not-covered list. Player-only paths
   (hedgehogs, Luang Prabang all-in, associated-state armies, Soviet
   patronage) need one player game or console forcing; for hedgehogs use
   `effect ic_afk_force_hedgehog_enable = yes` before 1953-11.
5. Tune only with evidence from more than one run. Watch first: Bretagne and
   Camargue contest rates, Lower Laos outcomes, the campaign-input totals,
   the Struggle writer-3 share, and the Dak Doa `10180` staging.
6. The design's unbuilt list is empty. New content needs a new design
   decision from the user. Open loc items: about 1,190 internal flags
   without loc (user deferred), and `VIN_CEFEO.1`-`.13` options are still
   name-only.
7. Keep the consolidated-playtest list current: every patch adds its expected
   observations to that list.

## 2026-09-28 second run

A further AFK run (logs in `_local/logs/2026-09-28/`) is recorded in the
design ledger's "review of the 2026-09-28 AFK run". It reconfirms lifecycle,
THO, Castor timing, and post-DBP deferral, and covers Atlante `central_success`.
It adds three items to the next pass, ahead of the balance work above:

1. Pathet Lao (`LAO`) raid victory has no ceasefire/settlement, so LAO
   conquered the Royal Lao (`LOS`) kingdom. Decide the intended outcome, then
   fix `ic_laos_raid_attacker_victory`.
2. Struggle margin `+498` and VIN delegate weight 135 versus 25; attribute the
   remaining overshoot beyond the Laos award.
3. The negotiations queue never passed the peace gate while NLF lived; Geneva
   closed through `AUTO_RESOLVE` on 1954-08-07.

Also fix the `ic_pulse` FRA `Division d'Infanterie` spawn and the Siam focus
completions at `Indochina_Flavor_Events.txt:343,562-563`.

## 2026-09-29 tracing, negotiations gate, balance and defect pass

Full record in the design ledger's 2026-09-29 section. Statically verified
only; no engine run.

- Struggle tracing: `SCORE_WRITE` (with writer codes), `SCORE_UNTRACED`, and
  `LEVERAGE_WRITE`. `SCORE_AWARD` is retired. The pro-independence raid-award
  array bug is fixed.
- Negotiations gate: the cause was VIE's war with a surviving NLF, which kept
  the at-peace gate closed. VIN funding was not involved. User decision: NLF
  is dealt with by defeat or by a VIN-ordered stand-down, which is a VIE-NLF
  white peace 90 days after negotiations are chosen. The Geneva gate itself is
  unchanged, and the wrap-up timer waits during the stand-down.
- Balance: AI Metropole requests are held below 45 Patience, and a new
  War-Credits-to-Patience decision is added. The GONO floor is 3 groupements
  at every Patience level. There is new standard-hold AI demand for FRE and
  TAI. Vinh Yen and Na San get scripted, ownership-neutral launch garrisons.
  The AI State of Vietnam has a 30-division cap during the war, enforced by
  the demobilisation loop.
- Defects: Lorraine cleanup is now conditional, the dead Siam focus
  completions are removed, `Kong Pathom` no longer needs motorized equipment,
  the Phase 2 FRA spawn uses a scripted template, `VIN_Formalize_Tieu` has one
  reward block, and the Dien Bien Phu posture and Dak Doa gate
  (`DAK_DOA_GATE`) are logged.
- Left open: the `VIN_50s.txt` "unlocked template" warning. Fixing it means
  locking `Trung doan Bo binh Infantry`, which is a design decision.

## 2026-09-29 content pass: first Nghia Lo and the hedgehog network

Full record in the design ledger's "2026-09-29 content pass". Statically
verified only; the values are first-pass and not tuned.

- First Nghia Lo is VIN campaign `10` (`VIN_Strike_Nghia_Lo`). VIN must hold
  province `13773` for 5 days. It never changes ownership and uses the shared
  resolver and cleanup. CEFEO responds through `FRE_Preparation.5`, with an
  optional Tu Le airborne relief and a scripted launch garrison. A held Nghia
  Lo helps the Na San preparation; a VIN success gives the Northwest campaign
  +25 Campaign Supply.
- `FRE_Hedgehog_Network` excludes Castor. It fortifies and garrisons Na San,
  Lai Chau and Luang Prabang. With it, no Dien Bien Phu camp, GONO garrison or
  response package exists, and nothing is recorded to Geneva for Dien Bien
  Phu, so the post-DBP latch never opens. Pollux and Atlante accept either
  focus, and Pollux is skipped when hedgehogs are chosen.
- Province `13773` was identified from map centroids; confirm it in-game
  first (ledger check 9).

## 2026-09-29 AFK run review: NLF left standing

Logs in `_local/logs/2026-09-29/`; full record in the ledger's matching
section. The negotiations stand-down worked, but its white peace let the
Indochina failsafe force the never-ending-conflict terminator in the same
tick, before Geneva launched, so NLF was never annexed. Fixed in
`ic_failsafe_theatre_unfinished_trigger`: queued negotiations now count as
unfinished content. Verify with ledger check 14 in the next run; the affected
save is not repaired.

## 2026-09-30 commit, run scoring, and template lock

The whole 2026-09-29 batch is committed (`87801f6193`) after static checks.
The 2026-09-29 run is scored against ledger checks 1-13 in the ledger's
2026-09-30 section. Passes: Patience (3), Dien Bien Phu garrison and duration
(4), launch garrisons and Vinh Yen/Na San duration (5), VIE cap (6), defect
errors (7), and Nghia Lo lifecycle (10). Open: Dak Doa never launched because
NLF never held staging province `10180` (8, now check 16). Not covered: the
Northwest supply callback (11) is not logged, and hedgehogs (12).

User decision: `Trung doan Bo binh Infantry` is locked (`is_locked = yes` in
`history/units/VIN_1949.txt`), which closes the `VIN_50s.txt` unlocked-template
warning. Statically verified only; ledger check 15.

## 2026-09-30 content pass

Full record in the ledger's "2026-09-30 content pass". Statically verified
only; values are first-pass. User-chosen shapes:

- VIN limited campaign `11`, the move on Lai Chau. It holds `13765` for 5
  days and offers Pollux early.
- Numbered FRE operations `5` Bretagne, `6` Adolphe and `7` Camargue.
- An Atlante-linked Lower Laos diversion with no war against Royal Lao or
  Cambodia.
- Mang Yang and Chu Dreh as post-Dien Bien Phu CEFEO ambush packages with
  no war.

AFK coverage was widened in the same pass:

- Campaign `1` supply and the Nghia Lo bonus.
- `PREP_TIER`, garrison-removal checks, and Pollux/Atlante stage logs.
- More Struggle writers routed (codes 16-26).
- An opt-in console switch that makes the AI pick the hedgehog network.

New playtest checks are 17-22.

## 2026-10-01 run review: negotiations end in regroupment

Logs in `_local/logs/2026-10-01/`; ignore everything after 1958. Check 14
passed: Geneva launched on the stand-down day and annexed NLF on 1954-10-06.
The user-visible problem was that NLF stayed alive at peace for months after
a bare white peace, and the focus showed nothing. User decision: the
stand-down now ends in regroupment. VIE annexes NLF without its troops, VIN
gets manpower and 2 regiments, and both sides get an event. The focus now
has a tooltip. Full record in the ledger; new check 23.

## 2026-10-01 fix-up pass

Statically verified only. Bretagne and Camargue now need enemy contact
before they count a clean hold; an uncontested sweep is aborted. The Viet
Minh and southern Viet Minh AI get counter-strategies. Lower Laos gives
CEFEO a Bolovens airlift choice that makes `contained` reachable. Regroupment
also runs if the southern Viet Minh are already at peace with the State of
Vietnam. New ledger checks 24-26; the next run scores checks 1-26. Next:
remaining unbuilt design content, starting with VIN Luang Prabang all-in and
the second overextension tier.

## 2026-10-01 remaining unbuilt design content

The last unbuilt items are code-complete: the severe overextension tier and
the VIN Luang Prabang all-in, Section 9.1 campaign inputs, Chinese versus
Soviet patronage, Charles Chanson/Sa Dec, the Royal Lao and Cambodian army
branch, and deletion of the unassigned legacy adjacency rules. Statically
verified only. Full record and checks 27-33 are in the ledger. The design's
unbuilt list is now empty; the next step is the consolidated playtest of
checks 1-33.

## 2026-10-02 run review: Viet Minh capitulates during Cao-Bac

Logs in `_local/logs/2026-10-02/`; full record in the ledger's matching
section. Day 4 of Cao-Bac (1950-10-22) VIN took the ordinary army-wide
overextension penalty, which no earlier run had taken in Cao-Bac. On day 21
it capitulated to CEFEO and the Tho with 28 divisions. The failsafe then
routed to the southern-victory ending, which annexes the north into the
State of Vietnam and drops its cosmetic tag by design. The capitulation is
the defect. Its cause is inferred, not proven. Telemetry was added
(`ENVELOPE_CAUSE`, `CAPITULATION`), and the Patronage `anti_air` enum error
is fixed. Behaviour is unchanged. Statically verified only; checks 34-36.

## 2026-10-02 second run: full arc to Geneva

Logs in `_local/logs/2026-10-02b/`; full record in the ledger's matching
section. The arc ran end to end with no `IC_AFK|FAIL` lines. Dien Bien Phu
fell on day 37, negotiations ended in regroupment, and the scripted Geneva
concluded on 1954-10-12 with a final margin of +252. The only manual step
was helping the PRC win the Chinese Civil War.

Three fixes, statically verified only:

- VIN overextension now needs 5 consecutive days on off-envelope ground,
  which was the user's decision. Before this, 8 of 10 launches were
  penalised within 3 days for incidental Delta ground.
- The Bolovens airlift spawns as a Royal Lao division, which was the user's
  decision. If it cannot spawn, the credits are refunded. Before this,
  CEFEO paid 40 credits and got nothing.
- The command-input clamps now use `clamp_temp_variable`. Supply had
  reached +32 against the cap of 30.

## 2026-10-02 third run: grace period live

Logs in `_local/logs/2026-10-02c/`; full record in the ledger's matching
section. Clean arc with no `IC_AFK|FAIL` lines. The early Cao-Bac
(1949-12) is intended, because the PRC won early. Dien Bien Phu fell on
day 22. Geneva concluded 1954-06-16 with a final margin of +135.

The grace period works, but VIN still holds Delta ground for most of every
campaign (Hoa Binh 98 days, Northwest 127). The severe tier ran through all
of Na San while the Pathet Lao raid was live. The southern Viet Minh
capitulated in May 1953.

Patched, statically verified only:

- Royal Lao Bolovens divisions now count toward `contained`.
- New `SEVERE_CAUSE` line, `delta_provinces` field on `ENVELOPE_CAUSE`, and
  a Bolovens spawn log.

The three design questions are in "Next session order".

## 2026-10-02 fourth run: evidence for the three decisions

Logs in `_local/logs/2026-10-02d/`; full record in the ledger's matching
section. The arc is clean: Dien Bien Phu fell on day 21 and Geneva
concluded on 1954-06-19 with a final margin of +374. The only FAIL was a
false positive in the CEFEO cleanup check when Dien Bien Phu superseded
Camargue, and it is fixed. The evidence for the three open decisions is in
the ledger; the decisions themselves are in the next section.

## 2026-10-02 patch: the three decisions

Full record in the ledger's matching section. Statically verified only.
These are the user's decisions:

- The delta edge provinces `1185` and `13770` no longer trigger VIN
  overextension outside the delta campaigns.
- The severe tier counts only Vientiane ground (as in Section 17), never
  Luang Prabang.
- The north now resupplies the southern Viet Minh monthly: 300 rifles, and
  one regiment while it has fewer than 10 divisions. This is paid from
  Campaign Supply.

New checks 44-47.

## 2026-10-03 run review: second capitulation during Cao-Bac

Logs in `_local/logs/2026-10-03/`; full record in the ledger's matching
section. VIN capitulated to CEFEO on 1950-11-11, day 24 of Cao-Bac, with
28 divisions and its capital held; the struggle ending then annexed the
north into the State of Vietnam. The overextension penalty had cleared on
1950-10-31, and the 2026-10-02d run survived a longer one, so it is not
the cause. No `NLF_RESUPPLY` line ever fired. No code changed; checks
48-49.

## 2026-10-03 patch: surrender and resupply telemetry

Statically verified only; no behaviour change. New `IC_AFK|SURRENDER`
lines log VIN surrender progress (5% buckets) and which northern
victory-point provinces VIN owns and has lost, weekly and on change while
at war with CEFEO, and once more at a capitulation. New
`IC_AFK|NLF_RESUPPLY_SKIP|gates` names the failing resupply gate. Bit
tables are in the ledger's matching section.

## 2026-10-03 second run: historical arc

Logs in `_local/logs/2026-10-03b/`; full record in the ledger's matching
section. No capitulation, no FAIL lines; Dien Bien Phu fell on day 35 and
Geneva concluded 1954-07-08 (+343). `SURRENDER` shows VIN reaching 75%
surrender progress after losing only Thanh Hoa and Dong Bac Bo, which
confirms the victory-point cause. The resupply fired once in four years;
the southern Viet Minh capitulated 1952-09-04. User note, deferred: the
Geneva "Independent and Neutral Laos and Cambodia" outcome removes the
Pathet Lao even after a raid victory, and the "Communist Regroupment
Zones" option reads as a withdrawal the Pathet Lao would not accept.

## 2026-10-03 patch: surrender limit, core defence, accrual trace

Statically verified only; full record in the ledger. The Resistance War
Economy idea, which VIN holds for the whole war, now gives
`surrender_limit = 0.5`. New AI strategy `VIN_hold_surrender_core` adds
standing defence for Dong Bac Bo and Thanh Hoa in any war with CEFEO. The
resupply is probably silent because the VIN pulse is monthly, not daily:
the 28-step counter then fires about every 28 months, which fits the two
observed deliveries 876 days apart. New `VIN_PULSE` and `VIN_ACCRUAL` lines
will confirm it. Checks 50-52.

## 2026-10-03 third run: surrender limit live, cadence confirmed

Logs in `_local/logs/2026-10-03c/`; full record in the ledger. Clean arc,
no FAIL lines, no rework errors; Dien Bien Phu fell on day 29 and Geneva
concluded 1954-09-09 (+341). No VIN capitulation; peak surrender progress
10%. `VIN_PULSE` is every 30-31 days, so the monthly accrual, patronage
delivery and resupply ran only twice in five years. New: the Pathet Lao
capitulated to CEFEO during Lower Laos on 1954-03-12.

## 2026-10-03 patch: supply step on every pulse

User decision; statically verified only. The VIN pulse is monthly, so the
supply step (Campaign Supply income, patronage delivery, southern
resupply, AI rifles) now runs on every pulse and the 28-step counter is
gone. Checks 53-54.

## 2026-10-08 localisation cleanup and notice events

Statically verified only; full record in the ledger's matching section.
288 player-visible Indochina flags got loc (user scope: visible only). 37
scripted triggers are wrapped internally in `custom_trigger_tooltip`, and
the 57 missing `VIN_CEFEO.1`-`.13` keys are written. 96 new notice events
(`FRE_Intel`, `VIN_Notice`, `IC_Notice_VIN`, `IC_Notice_FRE`, `VIN_CEFEO.14`
onward, `IC_Aid`, `VIN_Aid`, `FRE_Aid`) tell opponents, third parties and
patrons about campaigns, operations and aid. Each event is bespoke, and
each option has a small effect. Checks 55-58.

## 2026-10-09 run review and error-log spam patch

Logs in `_local/logs/2026-10-09/`; full record in the ledger's matching
section. Clean arc, no FAIL lines: Dien Bien Phu fell on day 39 and Geneva
concluded 1954-06-27 (+844). The southern Viet Minh capitulated 1953-08-04.
The 95.9 million error lines were not Indochina code: 99.6% came from the
trade exporter list removing absent values, and about 234,000 from an
`is_ai` check in state scope in the religion drift. Both are fixed. The
rework's own regression was the 2026-10-08 notice loc: literal line breaks
stopped three loc files from loading past the first break. Fixed with `\n`
escapes. Statically verified only; checks 59-60.

## 2026-10-09 second run: error log clean, resupply gate fixed

Logs in `_local/logs/2026-10-09b/`; full record in the ledger. error.log is
8,647 lines (check 59 passed). Clean arc, no FAIL lines: Dien Bien Phu fell
on day 28, Geneva concluded 1954-06-09 (+770). The southern Viet Minh
capitulated 1952-09-23. Cause found in both 2026-10-09 runs: the Nam Bo
Resistance focus gives the southern Viet Minh the Northern Supply Line idea
for a year, and the monthly resupply treated that idea as the post-DBP
funding and stopped. The gate now uses the post-DBP funding flag.
Statically verified only; check 61.

## 2026-10-09 patch: raid warnings and State of Vietnam script errors

Statically verified only; ledger has the details, check 62. The Raid City
and Raid Supply Hub types no longer use unit organisation, strength or
recon in their success chance, which silences the hourly warning from a
raid left without a unit. The Saigon-lost event now tests province control
correctly, and Ngo Dinh Can is recruited at game start instead of by event.
