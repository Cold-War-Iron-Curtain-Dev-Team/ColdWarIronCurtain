# VIN / FRE First Indochina War Focus Tree Expansion — Final Design Specification

Status: **FINAL TECHNICAL PASS v4, reviewed — implementation in progress.** Reviewed against the earlier planning drafts: the primary campaign / response package split, the FRE offensive-initiator vs defensive-holdout modes, and the reuse of the existing Struggle score instead of a new shared war-momentum resource all resolve open questions from the prior draft cleanly and are retained as-is. One design principle from the earlier draft (Section 1, principle 7) and two flags for afushin to sanity-check before implementation (Section 15) were added back in.

This document combines the historical/content plan with the current repository's technical constraints. It supersedes the earlier draft's secondhand assumptions about the VIN campaign and FRE operation systems. Exact Paradox script syntax, balance values outside the three existing VIN campaigns, and map province lists for new operations remain implementation-stage work.

**Game start date: late May 1949.** Events before that date are background and localization, not buildable operational focuses. Both trees begin in a war already in progress.

## 1. Scope and Design Goals

The rework covers:

- VIN's northern operational spine from the 1949-50 border fighting through Dien Bien Phu.
- FRE's command, defensive, offensive, pacification, and terminal branches for the same war.
- Outcome-driven cross-tree reactions.
- Replacement of Indochina's campaign-gated movement adjacencies with province-triggered overextension penalties.
- Repair and better integration of VIN's existing army-buildup and Southern Viet Minh branches.

It does **not** replace the existing Indochina Struggle score/phase system, Geneva Conference backend, VIN campaign-supply system, FRE War Credits/Metropole Patience systems, or the existing USA Operation Vulture focus. Those systems should be reused and extended.

The core principles are:

1. **Outcomes drive reactions.** A launched operation, a clean victory, a costly victory, and a failure are different facts and must not share one generic completion flag.
2. **Operations are real map commitments.** Named operations resolve from named geographic objectives and time limits, not arbitrary border-war results or mission-success arithmetic.
3. **One primary campaign owns peace.** Supporting operations and defensive reactions may run during it, but only the primary campaign resolver may transfer territory or white-peace the belligerents.
4. **Movement is discouraged, not prohibited.** Players may leave the historical operational area, but doing so produces escalating overextension penalties.
5. **The historical spine is the default, not an unavoidable rail.** Date failsafes and bypasses prevent a dead opponent or unusual AI path from locking either tree.
6. **Player knowledge should matter.** Historical mistakes remain the AI default, while informed players may choose a safer or more expensive alternative.
7. **Some of those "mistakes" should be live decisions, not just alt-history branches.** Carried over from the earlier draft: several currently-existing free-firing FRE events grant flat, disconnected bonuses/penalties instead of representing an actual historical decision point (dig in vs abandon a border post, commit reserves vs hold them, etc). Where one of these maps to a real historical call that turned out badly (Lorraine's overextended supply line, De Lattre overcommitting at Hoa Binh's tail end), rewrite it as a real choice inside the campaign/response-package framework rather than a standalone flat modifier. AI takes the historical option by default; a player who's run the tree before can knowingly pick differently. This doesn't need new mechanics, it needs the existing free-firing events threaded into the outcome-branch system in Section 7 instead of living outside it.

## 2. Current Backend Baseline

### 2.1 VIN campaigns

VIN already has a useful campaign wrapper in `VIN_Campaign_Effects.txt`. It is not a special engine-level limited war: it declares a normal `annex_everything` war, then imposes a scripted objective, clock, outcome, territorial settlement, and white peace.

The working pieces to retain are:

- campaign IDs, commitment tiers, Campaign Supply, and spawned formations;
- the guaranteed `on_daily_VIN` objective tick;
- clean, ground-out, abandoned, and failed outcome classes;
- control-based objectives rather than ownership checks;
- full-state transfer only after the scripted result;
- the 90-day inter-campaign cooldown;
- the FRA-hosted 300-day safety mission;
- campaign cleanup through one common finish effect.

The existing focuses in the root `common/national_focus/VIN_50s.txt` already call these effects for Northwest, Hoa Binh, and Dien Bien Phu. The 1949 Thap Van Dai Son and 1950 Cao-Bac focuses currently grant rewards and set cooldowns but do not run map campaigns; the rework may promote them into the same campaign framework.

### 2.2 FRE operations

FRE's present named-operation wrapper is scaffolding, not the target design. It:

- uses focus completion to activate a narrative event and selectable mission;
- selects preferred target **states**, but falls back to any adjacent VIN state;
- starts a one-province border war with `change_state_after_war = no`;
- treats winning that border war anywhere as success;
- resolves a stalled operation from commitment tier plus commander/GCMA/VNA values after 90 days.

The reusable parts are War Credits, commitment tiers, commander bonuses, GCMA, VNA coordination, Metropole Patience, spawned columns, cooldown gates, and the centralized finish concept. Generic target fallback and arithmetic-only outcomes must be replaced.

### 2.3 Existing shared systems

Do not create a second war-momentum resource. The Indochina Struggle already records Communist, Pro-France, Pro-Independence, Pro-Ethnic, and Kuomintang scores on FRA scope and tracks escalation/de-escalation through `global.Indochina_War_Active_Phase` plus phase-point variables. Campaign outcomes should pay into that ledger through shared tiered effects.

Geneva is a shared backend process, not a single shared focus. FRE, VIN, the great powers, and the conference GUI already enter it through common flags/triggers. The rework should feed military outcomes into the existing Geneva recorder and leverage systems rather than create a parallel ending.

## 3. Unified Campaign Architecture

### 3.1 One primary campaign, optional response packages

Only one **primary theatre campaign** may be active at once. It owns:

- the war declaration, if one is required;
- the campaign ID and initiator;
- objective and operational-envelope data;
- clean and final deadlines;
- territorial transfer;
- outcome scoring;
- final white peace and cleanup.

A response such as Lorraine during the Northwest Campaign, Condor during Dien Bien Phu, or an FRE defensive commitment is a **response package attached to the primary campaign**. It may have its own subobjective and timer, alter supply, deadlines, units, or scoring, and record its own result. It must not independently white-peace the same war or transfer the primary objective.

This prevents two concurrent resolvers from ending each other's operation and leaving flags, missions, or national spirits stranded.

### 3.2 Required campaign lifecycle

Every primary campaign follows:

`available -> launched -> commitment selected -> active -> resolving -> finished`

Use distinct flags/variables for:

- launch or preparation;
- active campaign state;
- clean success;
- costly success;
- failure;
- voluntary/peace abort;
- theatre-superseded result;
- cooldown.

Cross-tree focuses read result flags, not merely `has_completed_focus` or a generic launched flag. Result flags are permanent historical facts; active and cooldown flags are transient state.

### 3.3 Daily resolution priority

The daily tick must evaluate an active primary campaign in this order:

1. If the objective is met, resolve clean or costly success according to the inclusive time boundary.
2. If the theatre has ended (`Indochina_War_Over`, Geneva concluded, or the active phase has left the live-war window), resolve as theatre-superseded and clean up without adding a fresh campaign victory.
3. If the final deadline has passed, resolve failure.
4. If all relevant campaign wars have been absent for more than the declaration grace period, resolve aborted.

The existing 14-day grace period is retained so a declaration has time to register. If a target tag disappears, objective control decides the result: VIN/FRE receives victory if it actually holds the objective; otherwise the campaign aborts.

### 3.4 Cleanup invariant

Every exit—including watchdogs, scripted peace, tag disappearance, Geneva, and CEFEO dissolution—must call the primary campaign's common finish effect. No event may merely clear an active flag.

The finish effect must:

- clear all active/resolving/response flags;
- set the correct outcome and cooldown flags;
- end only the wars opened or adopted by the campaign;
- remove campaign, defensive, AI-support, and overextension spirits;
- remove campaign missions and timers from every host scope;
- clear objective and siege modifiers;
- remove or stand down temporary formations;
- reset campaign, siege, hold-duration, and overextension variables;
- recalculate the shared Struggle ledger where needed.

The current `vin_campaign_watchdog` violates this rule: it assumes a border war and directly fires an old stand-down event after 150 days. It must be replaced later with a safety call into the same resolver. The 300-day FRA-hosted timer may remain as the ultimate backstop, but it must also use the common resolver.

## 4. Fixed VIN Victory and Termination Conditions

The following are final design decisions for the three already implemented VIN campaigns.

| Campaign | Primary victory condition | Clean success | Costly success | Failure |
|---|---|---:|---:|---:|
| Northwest / Tay Bac | VIN simultaneously controls provinces `10075`, `12075`, `13775`, `16526`, and `16527` | Objective by day 120 inclusive | Days 121-210 inclusive | Objective absent after day 210 |
| Hoa Binh | VIN controls province `10129`, the sole province of state `1766` | Objective by day 120 inclusive | Days 121-210 inclusive | Objective absent after day 210 |
| Dien Bien Phu | VIN controls camp province `4529`; the rest of state `671` is not the objective | Objective by day 150 inclusive | Days 151-260 inclusive | Objective absent after day 260 |

Success transfers ownership only during resolution:

- Northwest transfers state `1761` (Hoang Lien Son).
- Hoa Binh transfers state `1766`.
- Dien Bien Phu transfers state `671` (Tay Bac Bo).

The current `< 120` / `< 150` checks make the exact deadline day a costly result despite localization saying “within.” Implementation must use the inclusive boundaries above.

### 4.1 Northwest operational area

Victory remains the five-province strategic corridor, not full control of state `1761`. The normal operational envelope may include reachable Hoang Lien Son provinces:

`10075`, `12075`, `13773`, `13774`, `13775`, `16526`, `16527`.

Province `12319` remains outside the envelope because it is approached through MEO-held Ha Giang and is intentionally unnecessary to the corridor objective.

### 4.2 Hoa Binh operational area

The enemy-ground objective/envelope is province `10129`, with VIN's own direct approach provinces treated as home/rear-area ground. Moving into Hoang Lien Son, Tay Bac Bo, or the Red River Delta during this campaign is off-plan and may trigger overextension.

Historically this should become a two-stage campaign:

1. FRE initiates the seizure of Hoa Binh.
2. If FRE establishes the salient, the same primary campaign transitions to VIN's counteroffensive/CEFEO holdout phase.

Salan's Operation Amarante choice is a voluntary withdrawal result within phase two, not a second independent peace-owning campaign. Holding the salient is the costly player alternative.

### 4.3 Dien Bien Phu operational area and siege

The normal VIN envelope includes the reachable Hoang Lien Son corridor and all provinces of state `671`. Only `4529` grants victory.

The existing siege begins if VIN controls **any one** non-camp province in state `671`, which will be too permissive after movement restrictions are removed. The rework should require a meaningful investment condition—at minimum an eastern/northern approach plus one valley/ring province—before siege days accrue.

Fort degradation may retain the present fourteen-day steps and AI assistance, but AI assistance cannot bypass the primary objective. It may advance the siege or force an AI-held camp to fall only after the investment and supply conditions have genuinely been met.

## 5. Province-Triggered Overextension

The new system replaces campaign-gated land adjacencies. It does not change victory conditions.

### 5.1 Trigger model

Each active campaign supplies two province sets:

- its objective set;
- its wider permitted operational envelope.

At a throttled daily or weekly pulse, each principal side checks whether it controls enemy ground outside its active envelope. Home territory, allied starting territory, and rear-area transit ground must never trigger the penalty merely because it is controlled normally.

Recommended tiers:

- **In envelope:** no overextension penalty.
- **One operational band beyond the envelope:** ordinary overextension.
- **Deep/off-theatre penetration:** severe overextension.

The first implementation may use one tier if province-band maintenance is too expensive, but the trigger/data model should not prevent adding the severe tier later.

### 5.2 Behavioral requirements

- Apply the penalty to VIN/FRE, not as a blanket state penalty affecting both sides.
- FRE's crown-domain troops must follow the FRE-side result through a shared alignment trigger.
- Re-evaluate promptly when control changes; remove the spirit as soon as no forbidden enemy province is controlled.
- A campaign result must remove all overextension spirits even if the checker has not run again.
- Straying does not auto-fail an operation. It makes the ahistorical offensive increasingly difficult while the original objective and clock continue to decide the result.
- Province lists must live in shared scripted triggers/effects or arrays, not be duplicated between focus availability, victory, localization, AI, and overextension code.

### 5.3 Adjacency retirement

Remove only the artificial campaign movement limiters after the replacement triggers have passed map tests. Straits, canals, Laos-war boundaries, and unrelated special adjacencies are outside this work. The implementation audit must map every retired `INDOCHINESE_WAR_*` rule to either a normal map connection or a retained geopolitical restriction before deleting it.

## 6. FRE Operation and Defensive-Holdout Design

### 6.1 Offensive-initiator mode

FRE operations such as the opening seizure of Hoa Binh, an independent Lorraine divergence, and Castor may create a primary campaign when none exists. Their focuses should call the operation setup effect directly on completion. A narrative/commitment event may still open immediately, but the extra selectable-mission layer should be removed.

Success must be defined by an exact province objective, a hold duration where appropriate, and a deadline. Commitment tier and existing CEFEO systems should influence forces, supply, deadline flexibility, and available decisions—not substitute for controlling the objective.

Castor specifically succeeds by establishing and holding the airhead at province `4529`, not by winning a border war elsewhere in state `671` or `1761`.

### 6.2 Defensive-holdout mode

When VIN owns the primary campaign, FRE does not launch a second limited war. The relevant FRE focus unlocks a response package that can:

- select withdrawal, standard defense, or maximum commitment;
- deploy relief/garrison formations;
- fortify the named objective;
- change the attacker's clean/final deadline within bounded limits;
- impose or mitigate supply/overextension effects;
- record a defensive result when the primary campaign resolves.

This mode is appropriate for Nghia Lo/Na San, the later Hoa Binh phase, and Dien Bien Phu.

### 6.3 Existing operation targets to preserve conceptually

The current target-state choices remain useful historical routing hints, but later map design must replace them with exact province envelopes:

| Operation | Existing target geography | Reworked role |
|---|---|---|
| Lorraine | Ha Giang / Cao Bang | Northwest response package historically; optional independent deep raid on divergence |
| Hirondelle | Lang Son | Short raid/interdiction operation with a raid objective, not territorial annexation |
| Mouette | Thanh Hoa | Spoiling/pacification operation with temporary control or disruption objective |
| Brochet | Thanh Hoa / Hoa Binh | Pacification/clearing operation; exact historical province set required |
| Castor | Tay Bac Bo / Hoang Lien Son | Primary campaign to establish the `4529` airhead |

Camargue, Pollux, Atlante, and the other operations in the master list require new operation records rather than being squeezed into one of these IDs.

## 7. Cross-Tree Reactivity Contract

Use four levels of coupling:

1. **Hard response:** an explicit causal reaction, such as Northwest launching Lorraine. Unlock on the relevant `active` or `launched` fact, with a date/war-state fallback so the tree cannot deadlock.
2. **Outcome branch:** different effects or follow-up focuses for clean success, costly success, failure, or withdrawal.
3. **Soft callback:** Na San's result modifies Castor/hedgehog choices but is not required for the tree to continue.
4. **Localization-only callback:** descriptions acknowledge earlier events without changing mechanics.

Focus completion must never masquerade as battlefield victory. Use a consistent namespace, for example conceptually:

- `VIN_Campaign_Northwest_Active`
- `VIN_Campaign_Northwest_Result_Clean`
- `VIN_Campaign_Northwest_Result_Costly`
- `VIN_Campaign_Northwest_Result_Failure`
- `VIN_Campaign_Northwest_Result_Aborted`

Exact final names should follow existing project casing and avoid unnecessary migration of flags already consumed elsewhere.

All operation focuses need the same live-war window used by VIN campaigns: not `Indochina_War_Over`, not Geneva-concluded, and active phase below 9. A focus already in progress may finish, but its completion effect must refuse to launch a new campaign after the theatre closes.

## 8. Historical Operational Spine

The historical order and intended mechanical relationship are:

| Period | Primary action | Required reaction or consequence |
|---|---|---|
| 1949-50 | PRC victory opens VIN's supply corridor; Thap Van Dai Son / Cao-Bac / RC4 | Rebuild both sides' border campaign using the primary campaign framework |
| Jan 1951 | VIN general counteroffensive at Vinh Yen | FRE defensive package under De Lattre |
| Mar 1951 | Dong Trieu / Mao Khe | Follow-up fight affected by Vinh Yen result |
| May-Jun 1951 | Day River battles | Multi-objective defensive sequence; do not flatten into Vinh Yen |
| Oct 1951 | First Nghia Lo | FRE raid/offensive distinct from the 1952 battle |
| Nov 1951-Feb 1952 | FRE takes Hoa Binh; VIN counterattacks | Two-stage campaign; Amarante withdrawal or costly hold |
| Oct-Dec 1952 | VIN takes the Northwest corridor / second Nghia Lo | Lorraine response package; withdrawal toward Na San |
| Nov-Dec 1952 | Na San | FRE holdout; its result becomes a soft doctrinal input to Castor |
| Apr 1953 | VIN Upper Laos offensive | Existing Laos raid/alt outcomes remain the base; add downstream wiring |
| Mid-1953 | Hirondelle, Camargue, Mouette, Brochet, Pollux | FRE pacification/interdiction sub-branch with distinct objectives |
| Nov 1953 | Castor establishes Dien Bien Phu | FRE primary airhead campaign; success schedules the siege setup |
| Late 1953 | VIN moves on Lai Chau | Confirms or accelerates FRE's valley commitment |
| Mar-May 1954 | VIN besieges Dien Bien Phu | FRE holdout plus optional Vulture and Condor response packages |
| 1954 | Atlante in central Vietnam | Genuine strategic branch: central buildup versus northern reinforcement |
| Jul 1954 | Geneva | Existing shared conference/settlement backend consumes accumulated outcomes |

Pre-1949 events remain background. Operation focuses should normally cost the equivalent of 5-14 days; political, command, logistical, and army-reform focuses retain longer pacing. Date gates are guardrails, while causal result flags do the real sequencing.

## 9. Supporting Tree Rework

### 9.1 VIN army and command branches

Retain the existing focus set from `VIN_Issue_Ao` through `VIN_Plan_Large`, including `VIN_Mimic_French` versus `VIN_Maintain_Domestic_Weapon_Programs` and the `VIN_Implement_Vo` command branch. Convert flat bonuses into campaign inputs where appropriate:

- Campaign Supply generation or commitment prices;
- available commitment tiers;
- artillery/logistics formations;
- siege speed or consolidation time;
- overextension mitigation;
- AI strategy and historical option weights.

No focus should grant an automatic campaign win.

### 9.2 Southern Viet Minh branch

Preserve the existing Nguyen Binh event/focus structure. `VIN_Nguyen_Binh_Ambush` is intentionally unavailable and is force-completed by the dated `ic_pulse` event chain; its death/survival result is likewise force-completed. The rework task is therefore an audit of date, state-control, leader, and terminal focus gates—not a blanket conversion to northern campaign flags.

`VIN_Bac_Tien` currently waits for the Geneva-available trigger, while `VIN_Victory_in_the_South` waits for the communist-victory ending trigger. Test those intended mutually exclusive endings after northern outcome wiring changes. Use explicit northern result callbacks only where they create an actual southern consequence.

### 9.3 Named figures

Nguyen Binh remains the pattern for character-driven forks. Add a Charles Chanson/Sa Dec chain only after confirming character IDs, event ownership, and downstream Cochinchina consumers. Other figures should use the same event-result-to-focus pattern rather than inventing a new subsystem.

## 10. Alt-History Branches Retained for Content Design

### VIN

- Full commitment to Luang Prabang, with severe corridor-overextension risk.
- “South before North,” strengthening the Southern Viet Minh/Cochinchina struggle at the expense of Tonkin campaign capacity.
- Soviet patronage over primary Chinese patronage, changing equipment, doctrine, and diplomatic leverage.
- Negotiation from strength before Dien Bien Phu, producing an earlier and weaker Geneva-equivalent position.

### FRE

- Hold Hoa Binh instead of Amarante.
- Convert Lorraine from diversion into a sustained rear-area offensive.
- Reject Dien Bien Phu and expand a network of smaller hedgehogs.
- Vulture follow-up content around the already implemented USA focus.
- Condor arriving in time as a response package, not an automatic French victory.
- Prioritize Atlante over northern reinforcement.
- Build the Royal Lao and Cambodian armies instead of concentrating on the Vietnamese National Army.
- Charles Chanson survives Sa Dec, altering later pacification options.

These branches must change later choices, resource allocation, or settlement leverage; they are not renamed versions of the historical operation.

## 11. Geneva and Theatre-End Integration

- Continue writing Dien Bien Phu results into the existing Geneva outcome recorder.
- Campaign rewards use the existing Struggle score and phase effects; no direct ad hoc setting of a final Geneva outcome except through the established recorder.
- `FRE_Proclaim_Victory_in_Indochina`, `FRE_The_Geneva_Accords`, and `FRE_The_Fall_of_Saigon` remain score-and-ground-gated finales.
- The final campaign result must be committed before a same-day Geneva route reads it.
- Once Geneva concludes or `Indochina_War_Over` is set, every live campaign/operation is superseded and cleaned up, all launch focuses are bypassed or unavailable, and CEFEO wind-down may proceed.

## 12. Implementation Order

1. Audit the Indochina province graph and classify every existing campaign adjacency as remove, retain, or unrelated.
2. Harden the VIN state machine: inclusive deadlines, theatre-superseded outcome, unified cleanup, and corrected watchdog.
3. Add shared campaign objective/envelope data and province-triggered overextension checks.
4. Convert the three existing VIN campaigns without changing their fixed objectives.
5. Build the unified primary-campaign/response-package interface.
6. Rebuild FRE's five current operations on that interface; remove generic border-war fallback and selectable-mission indirection.
7. Add the earlier VIN/FRE battles and later new operations in historical order.
8. Wire result-driven focus reactions and AI plans.
9. Audit Southern Viet Minh and character event gates.
10. Run Geneva, dissolution, save/load, tag-disappearance, and ahistorical-path regression tests.
11. Only after tests pass, retire the obsolete movement adjacency rules and legacy outcome events.

## 13. Acceptance Criteria

The rework is not complete until all of the following pass for both human and AI participants:

- Every primary campaign produces exactly one terminal result.
- Exact clean/final boundary days resolve as documented.
- Capturing non-objective ground never grants victory.
- Capturing an objective after taking a deep ahistorical route still grants the correct timed result while overextension applies.
- White peace, Geneva, target annexation, CEFEO dissolution, and the safety timer leave no active flags, missions, temporary units, siege variables, or national spirits.
- A response package cannot independently terminate its parent campaign.
- FRE operations cannot fall back to an unrelated VIN border.
- The other tree reacts to launch/result flags without deadlocking if the expected opponent or prerequisite battle no longer exists.
- Overextension never fires from a side's ordinary home/allied territory and clears after withdrawal.
- Dien Bien Phu cannot be won by controlling state `671` while province `4529` remains in enemy hands.
- Castor cannot succeed without establishing the `4529` airhead.
- Geneva and all three FRE finale regions remain mutually exhaustive after the new score awards.
- Save/load during every campaign phase produces the same eventual result as uninterrupted play.

## 14. Implementation Source Map

The later implementation should begin from these current files rather than recreating their responsibilities elsewhere:

- `common/national_focus/VIN_50s.txt` — VIN focus entry points and the Southern Viet Minh branch.
- `common/national_focus/FRE_50s_Indochina.txt` — FRE operational, support, and finale focus layout.
- `common/scripted_triggers/VIN_indochina_campaign_triggers.txt` — current VIN gates and geographic objectives.
- `common/scripted_effects/VIN_Campaign_Effects.txt` — VIN commitment, daily resolution, transfers, siege, and cleanup.
- `common/scripted_triggers/FRE_operation_triggers.txt` and `common/scripted_effects/FRE_Operation_Effects.txt` — reusable FRE gates/resources plus the border-war logic to replace.
- `common/decisions/Indochina_War.txt` and `common/decisions/FRE.txt` — campaign safety timers and the selectable-operation missions to retire.
- `common/on_actions/CWIC_Struggle_on_actions.txt` and `common/on_actions/FRE_CEFEO_on_actions.txt` — guaranteed VIN daily and FRE weekly pulses.
- `common/ideas/VIN.txt`, `common/ideas/FRE_CEFEO.txt`, and `common/dynamic_modifiers/0_dynamic_modifiers.txt` — present campaign, overextension, objective, siege, and guerrilla modifiers.
- `map/adjacency_rules.txt` and `map/adjacencies.csv` — movement limiters to audit only after the replacement is working.
- `common/scripted_triggers/IC_struggle_triggers.txt`, `common/scripted_effects/CWIC_Geneva_Conference_Effects.txt`, and `common/scripted_triggers/FRE_Indochina_ending_triggers.txt` — shared Struggle/Geneva/finale interfaces.
- `events/VIN_Campaign_Events.txt`, `events/FRE_Operation_Events.txt`, `events/FRE_Events.txt`, and `events/SWF_Indochina_War_events.txt` — current result presentation and legacy outcome paths requiring consolidation.

## 15. Remaining Content Decisions

These require designer/map-owner judgment rather than backend invention:

- Exact province objectives and operational envelopes for every new battle beyond Northwest, Hoa Binh, and Dien Bien Phu.
- Balance values for ordinary/severe overextension and whether the first release needs both tiers.
- Hold durations for FRE airheads, fortified positions, and clearing operations.
- Which named engagements deserve independent primary campaigns versus response packages or event phases.
- Final focus names/layout and which existing placeholder nodes should be renamed, moved, or retained.
- VIN internal political/command factions used to frame the alt-history branches.
- **Worth confirming before implementation starts:** Section 9.2's diagnosis of the Southern Viet Minh branch is a real correction to how this was described earlier in planning — it says `VIN_Nguyen_Binh_Ambush` is intentionally unavailable and force-completed by a dated `ic_pulse` chain, not a broken reactive trigger. That changes the task from "fix the trigger wiring" to "audit date/state/leader/terminal gates," which is a smaller and different job than originally scoped. Worth a quick sanity check against actual in-game behavior before treating it as settled, since it reverses an earlier assumption.
- **Province and state IDs throughout Section 4** (`10075`, `12075`, `13775`, `16526`, `16527`, `10129`, `4529`, states `671`/`1766`/`1761`, etc) read as pulled directly from the repo, but this review had no access to the actual map/state files to cross-check them. Worth a quick verification pass against the live province map before they get locked into acceptance criteria, since several of those criteria (Section 13) hard-depend on exact IDs being correct.

## 16. Reference Checklist

Master operational checklist: Route Coloniale 4, Vinh Yen, Mao Khe, Day River, first Nghia Lo, Hoa Binh, second Nghia Lo, Lorraine, Na San, Bretagne, Adolphe, Upper Laos/Muong Khoua, Lower Laos and northeast Cambodia, Hirondelle, Camargue, Brochet, Mouette, Castor, Pollux, Atlante, Dak Doa, Dien Bien Phu, Vulture, Condor, Mang Yang Pass, and Chu Dreh Pass.

Existing tree landmarks:

- FRE: RC4/Revers Report/De Lattre/Vinh Yen; Na San/Lorraine/Mao Khe; Hirondelle/American financing/Brochet; Mouette/Castor; Final Push; mutually exclusive Victory/Geneva/Defeat finales.
- VIN northern: `VIN_Plan_Large`; `VIN_Thap_Van_Dai` and `VIN_Operation_Cao-Bac`; `VIN_Northwest` and `VIN_Liberate_Duyen`; `VIN_Prepare_Dien`.
- VIN army/command: `VIN_Issue_Ao`, `VIN_Chin_Tranh`, `VIN_Mass_Defectors`, `VIN_Sign_Sac_17`, `VIN_Implement_Vo`, and `VIN_Plan_Large`.
- VIN southern: `VIN_Nam_Bo_Khang_Chien`, the Nguyen Binh ambush/result fork, ideological leadership branches, and `VIN_Bac_Tien` / `VIN_Victory_in_the_South`.

## 17. Implementation Ledger

### Current patch

- Patch set: VIN campaign lifecycle and THO/Cao-Bac restoration, followed by adjacency retirement, overextension, state-policy, theatre-AI, and disconnected-base-supply balancing.
- Status: code-complete on 2026-08-09; targeted static verification and follow-up human campaign-flow acceptance passed, dedicated AI/balance acceptance pending.
- Patch/commit reference: the phase checkpoint commit containing this ledger; its exact hash is recorded in the local, intentionally untracked `HANDOFF.md`.

### Completed behavior

- Design review completed and canonical document selected.
- Existing VIN campaign wrapper, CEFEO custody, THO autonomy-zone chain, map ownership, startup OOB, focus, failsafe, Struggle, GCMA, and dissolution integration audited before edits.
- The common resolver now classifies clean, costly, aborted, failure, and superseded outcomes in the contractual order; clean/final deadline days are inclusive, the 300-day backstop checks the live objective and theatre first, and elapsed days survive cleanup for delayed localization.
- Every resolved primary campaign records one permanent result flag. Supersession performs cleanup without territorial transfer, Struggle movement, War Credits, Metropole Patience, or Dien Bien Phu/Geneva battlefield recording.
- The legacy VIN campaign watchdog now calls the common resolver instead of treating the absence of a border war as failure. Ending cleanup supersedes any live campaign before the theatre is dismantled.
- THO now begins alive as a neutral, French-aligned territorial council in Cao Bang and Lang Son, under FRE crown-domain custody with the existing non-Together-for-Victory puppet fallback. It begins with two small territorial battalions; VIN begins in Dong Bac Bo.
- The three early VIN economic focuses and the Hanoi asset-relocation focus now select a VIN-owned Cao Bang or Dong Bac Bo scope and never construct in or strip THO-owned territory.
- `VIN_Operation_Cao-Bac` now launches campaign ID 4 against THO. Its objective is simultaneous control of every province in Cao Bang and Lang Son; successful resolution transfers both states, removes THO without transferring its units, and unlocks air-base raids. Abort, failure, and supersession leave or restore surviving THO to French command.
- Existing CEFEO access, GCMA, Struggle, ending failsafe, dissolution handback, and postwar communist THO restoration paths remain connected. A surviving colonial THO blocks the communist re-release; a previously annexed THO can still be restored under VIN with Chu Van Tan.
- VIN and FRE AI strategies now recognize the Cao-Bac front, including targeted CEFEO defense of the two THO states while the campaign is active.
- Reusable console effects cover startup, status, deadline boundaries, abort, supersession, cleanup, result invariants, and save/load checkpoints.
- Fifty-seven northern/campaign adjacency assignments are now unrestricted land connections. Thirty-five Laos-war and theatre-divider assignments remain gated, including the two Dien Bien-to-Laos crossings; the four internal Dien Bien camp approaches are unrestricted.
- Shared geography triggers now distinguish each VIN operational envelope, previously captured VIN home territory, starting bridgeheads, the Northwest outlier, and French-aligned penetration into VIN rear areas. A daily one-tier overextension penalty applies and clears from VIN or the entire CEFEO/crown-domain side as control changes.
- Campaign cleanup removes overextension and campaign-command spirits before any target annexation, during normal finish, during Struggle ending cleanup, and from FRE during CEFEO dissolution.
- The Dien Bien siege now requires an eastern/northern approach plus a separate valley-ring province before siege days accrue. AI assistance can finish an established siege but cannot invent the investment.
- The first balance pass removes the blanket French combat penalty, reduces VIN campaign mobilization to a moderate logistics benefit, reduces the objective-state defense penalty from 80% to 25%, removes the generic VIN AI push into the FRE delta, and adds targeted CEFEO defense for Tay Bac, Hoa Binh, and Dien Bien Phu.
- Campaign state policy is now explicit and self-healing. Cao-Bac opens only `1280`/`1768`; Northwest opens `1761`; Hoa Binh opens `1761`/`1766`; Dien Bien opens `1761`/`671`. The nine northern states damaged by the old broad cleanup are rebuilt before the operation is applied each day, while the full Indochina `unplanned_offensive` baseline is rebuilt at launch and resolution.
- Temporary planned offensives no longer clear `VIN_unplanned_offensive_flag`. Cleanup restores the baseline after clean, costly, aborted, failed, or superseded resolution; theatre-ending cleanup still removes it normally.
- Hoa Binh now treats Hoang Lien Son as a contested approach as well as Hoa Binh itself. Tay Bac Bo remains protected during Hoa Binh and becomes planned only for Dien Bien Phu.
- VIN-controlled Thanh Hoa and Quang Binh receive a campaign-only local-supply modifier representing dispersed caches and porter relays. It grants local supply only, cannot create a route through French Tonkin, follows control daily, and is removed at campaign end.
- VIN AI no longer receives tag-wide conquer orders against TAI. Its campaign strategies request only the named objective states, retain a base-area reserve, and suppress unit requests on secondary CEFEO fronts during Cao-Bac and Hoa Binh.
- FRE now assigns more formations to Hanoi/Tonkin and the current operation. THO, TAI, and TAM have their own careful defensive plans for territory they own, and TAI begins with a fourth battalion at Dien Bien Phu so the western state is not empty before campaign reinforcements arrive.
- VIE's historical NUN event may still update NUN's nationalist identity, politics, and leadership, but its autonomy transfer has been removed. NUN therefore remains under CEFEO custody and in the northern war instead of silently becoming a VIE subject.
- New diagnostics report current planned/protected states, missing rear-area supply, and post-campaign restoration failures.

### Deferred work

- A severe/deep overextension tier; the first replacement patch intentionally ships one tier on geography helpers that can support a second.
- Northwest/Lorraine response work, the two-stage Hoa Binh design, expanded Dien Bien Phu response packages, remaining FRE operations, and supporting narrative/AI content.
- A post-failure recovery route from an unsuccessful Northwest campaign into Dien Bien Phu. The present focus still requires ownership of `1761`; this patch repairs the false failures caused by lost modifiers/supply but does not turn a genuine Northwest defeat into a free valley campaign.
- The full northern/southern French Indochina command interface. The immediate NUN custody conflict is contained by suppressing the event's autonomy transfer, but VIE/FRE faction and crown-domain ownership remain separate systems pending that patch.
- Deletion of the now-unassigned legacy northern adjacency-rule definitions after the unrestricted connections pass an engine map test. Their CSV assignments are already retired, so they no longer affect movement.
- Named colonial THO leadership research; the restoration patch uses a generic territorial council.

### Changed systems

- Canonical design documentation and implementation ledger.
- VIN campaign scripted triggers, effects, clock/backstop decisions, result events, scripted localization, result localization, and failsafe coverage.
- VIN northern focus behavior, early economic state targeting, and Hanoi asset relocation.
- THO/VIN country history, Cao Bang/Lang Son ownership, THO and VIN starting OOBs, and colonial/communist THO lifecycle helpers.
- Indochina Struggle ending cleanup and VIN/FRE theatre AI strategies.
- FRE, Viet Bac, and VIN campaign test effects.
- Indochina adjacency assignments, VIN/FRE campaign and overextension ideas, contested-objective balance, CEFEO dissolution cleanup, and route/overextension test diagnostics.
- Campaign state-modifier lifecycle, Thanh Hoa/Quang Binh local supply, VIN/FRE/crown-domain theatre AI, the TAI starting OOB, and the NUN unification event's custody-preserving behavior.

### Verification

- `git diff --check`: passed.
- Raw Clausewitz brace balance: passed for all 21 changed/new `.txt` gameplay files.
- Targeted static invariants: passed for starting ownership/capitals, two-unit THO OOB, the single TAM declaration path, Cao-Bac active/cooldown/deadline wiring, five exclusive Cao-Bac result names, focus launch behavior, and localization key presence.
- The repository's broad style checker reports pre-existing space-indentation findings in these legacy files; inspection of added diff lines found no new four-space indentation.
- In-game verification for the lifecycle/THO patch: a full human VIN game completed on 2026-08-08. Campaign lifecycle and THO restoration otherwise behaved smoothly.
- Adjacency/overextension patch static verification: `git diff --check` passed; every modified/untracked gameplay `.txt` file has balanced raw Clausewitz braces; every operative adjacency row retains ten fields; exactly 57 campaign routes are unrestricted, 35 Laos/divider routes remain assigned, and no retired northern rule name remains assigned in the CSV.
- New overextension idea/localization uniqueness and update/cleanup call sites passed targeted checks. Engine route access and balance remain pending.
- 2026-08-09 follow-up static verification: `git diff --check` passed; every modified/untracked gameplay `.txt` file has balanced raw braces; the obsolete broad-clear effect and all tag-wide TAI conquer orders are absent; the new modifier/localization/test effects are unique; TAI has exactly four starting battalions; and NUN's historical event contains no autonomy transfer to VIE.

### 2026-08-08 playtest findings

- Artificial campaign adjacency rules blocked valid routes into THO and Dien Bien Phu objectives. Both campaigns became mechanically unwinnable without console intervention because divisions could not enter required provinces.
- Human VIN was too strong in direct fighting and could push CEFEO and its crown domains with little difficulty. The next balance pass must remove the always-on French combat penalty, reduce VIN's broad campaign buffs and the objective-state defense debuff, and replace hard movement fences with conditional overextension pressure.
- Adjacency access and combat balance are failures for the current acceptance run; campaign resolution, results, ownership transitions, and surrounding Patch 1-2 integration passed the reported full-game smoke test.

### 2026-08-09 playtest findings

- Campaign launch removed `unplanned_offensive` not only from the named operation but also from Dong Bac Bo, Thanh Hoa, Hanoi/Tonkin, Hoa Binh, and the Tai exterior. It also cleared `VIN_unplanned_offensive_flag`, so campaign cleanup had no persistent marker from which to rebuild the original front. Later campaigns therefore inherited the damage.
- Cao-Bac was mechanically correct but too easy for a human (roughly two weeks). The AI did the opposite of the intended operation: while the subject war exposed the wider CEFEO front, tag-wide concentration let it occupy most of TAI and penetrate Hanoi/Tonkin before completing the THO objective.
- Hoa Binh needs Hoang Lien Son (`1761`) inside the planned/contested approach, while Tay Bac Bo (`671`) remains an unplanned exterior position. The latter should be strongly defended but not permanently impossible once a later campaign explicitly selects it.
- VIN's Thanh Hoa and southern forces collapse when cut off from the Dong Bac capital by French-held Tonkin. The fix should model dispersed local supply rather than create a railway or supply path through hostile territory.
- Northwest exposed the same modifier and supply failures: VIN could wander through TAI yet lose Hoa Binh and the southern base, fail the Hoang Lien objective, and deadlock the Dien Bien focus gate.
- NUN's 1950 VIE puppet decision can override its CEFEO crown-domain custody and remove it from northern wars. This belongs to the northern/southern command-interface repair, but the immediate wartime override must be prevented.

### 2026-08-09 follow-up playtest findings

- The revised first three campaigns completed smoothly in a human VIN run. The adjacency retirement restored practical access to the objectives; no console movement was required.
- VIN had difficulty holding its positions during Dien Bien Phu, but still captured TAI and the valley within the campaign deadline. This is useful defensive pressure rather than the earlier hard movement failure; further tuning should wait for an AI sample and comparative loss/time data.
- Dien Bien Phu did not immediately produce Geneva because the NLF was still alive and VIE remained at war. This is the intended result of `geneva_conference_vietnam_at_peace_trigger`, not a campaign-result regression. Once both Vietnamese conference parties are at peace, the existing daily Geneva path can consume the recorded DBP outcome.
- NUN's autonomy transfer to VIE was removed from `NUN_Unification.2.a`. The event can still update its politics and leadership, but NUN remains under CEFEO custody as intended for the current command model.

### Known issues

- This repository environment still cannot run HOI4 directly; the 2026-08-08 and 2026-08-09 findings come from the user's external full-game tests.
- Route access and the restored human campaign flow passed the latest engine run. AI containment, local-supply behavior, and comparative human/AI balance still need dedicated observation before they can be marked resolved.
- The first overextension release has one tier. Values and province bands are intentionally exposed in shared triggers/ideas for tuning after the next human and AI tests.
- Legacy `SWF_Indochina_War` border-war result events remain for debug/backward compatibility, but the production campaign watchdog no longer calls them. Consolidating or retiring those inert narrative paths belongs with the later unified campaign-ownership work.

### Exact next resume point

- Start a fresh VIN route test and confirm divisions can enter every Cao Bang/Lang Son province and reach Dien Bien Phu through the four internal camp connections without console movement. Confirm the two Laos-facing camp connections still obey the Laos/Dien Bien permissions.
- At the start of each campaign run `test_vin_campaign_overextension_status`: the normal objective envelope, previously won VIN territory, and the starting `12075`/`16526` bridgeheads must not apply a penalty. Occupy one listed off-theatre foreign province, verify the VIN idea appears on the next daily tick, withdraw, and verify it clears.
- Let FRE or a crown domain enter Dong Bac Bo or Thanh Hoa. Verify every living CEFEO/crown-domain tag receives the shared French penalty, then withdraw and run `test_vin_campaign_overextension_cleanup_check` after resolution.
- For Dien Bien Phu, verify one approach province alone does not advance siege days, then add a separate ring province and confirm the fourteen-day fort degradation starts. Repeat the campaign route at days 150/260 without cheats.
- Run a human VIN balance sample and historical-AI smoke test. Compare time-to-objective and losses against the prior effortless push, then tune the new ideas/objective modifier rather than restoring hard movement fences.
- Immediately after each launch run `test_vin_campaign_state_policy_status`. Expected planned states are Cao-Bac `1280/1768`, Northwest `1761`, Hoa Binh `1761/1766`, and Dien Bien `1761/671`; every named non-objective state in the log must remain under `unplanned_offensive`.
- During Hoa Binh confirm `1761` and `1766` show Contested Objective when French-aligned, while `671`, `881`, `1762`, `1760`, and `786` remain unplanned. After resolution run `test_vin_campaign_front_restoration` and confirm no marked state is reported open.
- Confirm VIN-controlled `1762` and `838` show Dispersed Base-Area Supply during a campaign, that the modifier disappears immediately if FRE takes control, and that it is absent after cleanup.
- Run historical AI through Cao-Bac and record control when THO falls: VIN should not have occupied `671`, Hanoi, or the Tonkin delta first. Repeat Northwest and verify TAI/FRE keep forces in both `1761` and `671` while VIN retains a reserve in `881`/`1762`.
- On a fresh historical run after 1950-04-14, allow VIE's NUN event to complete and confirm its political/leader changes apply without changing NUN's CEFEO subject or war status.
- After Dien Bien Phu falls, verify the DBP result is visible in the Geneva outcomes panel while the NLF war continues, then end that war and confirm the conference becomes available/fires on the established daily path.
