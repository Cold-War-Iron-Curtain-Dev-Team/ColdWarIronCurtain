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

- campaign IDs and Campaign Supply;
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

**Current implementation warning (2026-08-13):** this is still live, broken production content for `FRE_Operation_Hirondelle`, `FRE_Operation_Mouette`, and `FRE_Operation_Brochet`, not merely a historical description of code that has already been superseded. Each focus still opens a narrative event and selectable mission, then calls generic operation ID `2`, `3`, or `4`; `fre_operation_launch` attempts the obsolete one-province `start_border_war`, including its arbitrary adjacent-VIN fallback. These operations are not functional/accepted parts of the rework and must not be credited by campaign playtests. Their generic active, timer, result, cooldown, and cleanup state all remain in scope for the eventual conversion.

The neighboring `FRE_Prepare_for_the_Battle_of_Na_San`, `FRE_Prepare_for_the_Battle_of_Vinh_Yen`, and `FRE_Prepare_for_the_Battle_of_Mao_Khe` chains are a separate legacy problem: they do not launch that border war, but they still resolve selectable preparation missions from inventory/commander arithmetic and schedule disconnected battle events rather than reading live map outcomes. They, and any similar preparation focuses found during the audit, remain unconverted and unvalidated. This entry documents the debt only; it does not authorize treating focus completion as success or adding a quick border-war workaround.

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

### Committed response checkpoint

- Patch set: Northwest/Operation Lorraine response content, the post-Dien Bien Phu southern-war response, the accepted campaign-front containment/local-supply follow-up, and the two-stage Hoa Binh/Operation Amarante response.
- Status: recorded by this checkpoint; targeted static verification passed. Campaign-front containment, repaired southern supply, MEO self-defense, Northwest balance, the Hoa Binh lifecycle, and Lorraine's historical response path have engine acceptance. The Amarante payoff/clarity follow-up still awaits its two choice-specific human CEFEO checks. The ordinary post-Dien Bien Phu route through NLF destruction and the existing peace gate now has engine acceptance.
- Base checkpoint: the checked-in VIN lifecycle, THO/Cao-Bac, adjacency, overextension, state-policy, theatre-AI, and local-supply patch described below and in `HANDOFF.md`.

### Working Dien Bien Phu response patch

- Status: code-complete on 2026-08-11; targeted static verification passed. A full historical-path engine run completed successfully on 2026-08-12. Alternate posture and forced-terminal coverage remains available through the supplied diagnostics.
- Scope: one defensive-response package attached to live VIN campaign ID `3`, with standard hold, maximum reinforcement, Operation Condor, and Operation Vulture postures. The parent campaign still exclusively owns the exact camp objective, permanent battlefield/Geneva recorder, transfer, peace, and common cleanup.
- The production fire site for the old delayed `FRE_DBP.1-.8` arithmetic result chain is retired. The legacy definitions remain gated for old saves and console compatibility; `FRE_DBP.10` is retained as the limited American-response event and now feeds the live package.

### Working exact-province Operation Castor patch

- Status: code-complete on 2026-08-11; targeted static verification passed. The combined historical-path engine run completed successfully on 2026-08-12; alternate commitment, broken-streak, deadline, and supersession terminals were not individually reported.
- Scope: the Castor focus now opens an immediate full/limited airborne commitment and a visible thirty-day establishment clock. Success requires French-aligned control of province `4529` for fourteen consecutive daily checks; broken control resets the streak. The focus and launch effects recheck the live theatre, Tai Federation, Viet Minh, and landing-ground gates before committing resources.
- Castor is preparatory. It establishes and fortifies the camp, deploys a commitment-scaled GONO garrison, and records one of success, failure, or theatre-superseded. It does not transfer territory, make peace, resolve VIN campaign ID `3`, or write the Dien Bien Phu/Geneva battlefield recorder.
- Generic operation ID `5`, the arbitrary adjacent-state fallback, the generic border war, arithmetic threshold result, generic outcome dispatch, and 150-day watchdog consumer are retired for Castor. IDs `1`-`4` remain for the still-unconverted operation wrapper.

### Working Operation Pollux patch

- Status: code-complete on 2026-08-12; targeted static verification passed. Engine acceptance is pending. Pollux is a preparatory evacuation attached to an established Dien Bien Phu camp, not a primary campaign or a restored generic border war.
- Scope: evacuate Lai Chau toward the camp before VIN campaign ID `3` begins. The exact overland corridor is Lai Chau province `13765`, the Route Pavie approach at province `13762`, and the Dien Bien Phu camp at province `4529`.
- The commitment choice distinguishes the historical split evacuation (regular battalions by air and exposed Tai partisan columns overland), an escorted Route Pavie withdrawal, and an expanded airlift. Historical AI accepts the split evacuation and its column-loss result; an informed player may spend more to preserve the formation.
- The escorted withdrawal must keep all three exact corridor provinces under French-aligned control for seven consecutive daily checks inside a twenty-one-day window. The expanded airlift needs seven consecutive days of French-aligned camp control and ignores the land corridor. Broken control resets the relevant streak.
- Permanent results are force preserved, column lost, or theatre-superseded. A preserved force adds one Pollux survivor group to the existing GONO camp formation and supplies it; the historical column-loss result preserves only the regular stores flown out under Operation Leda. Pollux owns no state or province transfer, peace, VIN campaign result, Dien Bien Phu/Geneva recorder, or primary-campaign cleanup.
- If campaign ID `3` begins before Pollux resolves, Pollux records the result earned by its current posture and map state only where its seven-day requirement has already been met; otherwise it closes as superseded without delaying or altering the primary campaign. Theatre ending, CEFEO dissolution, mission timeout, weekly orphan handling, and console diagnostics use the same dedicated finish/cleanup path.
- Static verification: `git diff --check`, raw Clausewitz brace balance across all changed/new gameplay `.txt`, and `python3 tools/loc_audit.py --check` pass. New Pollux effects, triggers, events, AI strategies, focus, mission, and English localization keys are unique. Pixel-map adjacency confirms the exact `13765 -> 13762 -> 4529` corridor. Targeted source checks confirm three commitment choices, objective-first seventh-day handling, exclusive permanent results, parent-campaign handoff, complete orphan/dissolution/theatre cleanup, and no territory, peace, generic-operation, primary-campaign, or Geneva mutation.

### Working Operation Atlante patch

- Status: code-complete on 2026-08-12 and merged into the Pollux external-playtest batch at the user's direction. Targeted static verification passes; engine acceptance is pending.
- Scope: a ten-day focus after Pollux opens a central-Vietnam strategic choice. The full CEFEO plan, a Vietnamese-led limited plan, and cancellation in favor of a northern reserve are mutually exclusive. Atlante is a named operational package, not a Pollux extension or a restored generic border war.
- The map abstraction is the existing NLF-owned state `1287`, representing the Interzone V base. Its adjacent exact objectives are provinces `4255` and `1300`. A full commitment must keep both under French-aligned control for fourteen consecutive daily checks inside a ninety-day window; the Vietnamese-led plan must keep province `4255` under State of Vietnam control for the same streak. Broken control resets the count.
- A full commitment spends 100 War Credits, 4,500 manpower, and 7 Metropole Patience, supplies the Vietnamese National Army, and directs both allied AIs toward state `1287`. It permanently records that the expeditionary reserve went south. When VIN campaign ID `3` opens, that choice removes maximum reinforcement and Operation Condor from the CEFEO response menu while retaining the scheduled defense and Operation Vulture.
- The Vietnamese-led plan spends 40 War Credits and 2 Patience, supplies Saigon, directs the Vietnamese National Army toward the coastal objective, and preserves the complete Dien Bien Phu response menu. Canceling Atlante spends 40 War Credits, 2,500 manpower, and 3 Patience to bank a northern reserve. At campaign ID `3` launch, that reserve supplies the existing camp garrison and delays scripted fort degradation by ten active-siege days without moving the fixed day-`150` or day-`260` deadlines.
- Permanent results are full central success, Vietnamese foothold, stalled offensive, northern priority, or theatre-superseded. Atlante transfers no state or province, declares or ends no war, writes no primary campaign/Geneva record, and cannot resolve Dien Bien Phu. Daily and timer-backstop resolution, weekly orphan handling, theatre/dissolution cleanup, exact objective AI, centralized localization, and console diagnostics are wired.
- Static verification: `git diff --check`, raw Clausewitz brace balance across all changed/new gameplay `.txt`, and `python3 tools/loc_audit.py --check` pass. New Atlante effects, triggers, events, focus/mission entries, AI strategies, diagnostics, and English localization keys are unique. Pixel-map verification confirms provinces `4255` and `1300` share a land boundary inside state `1287`. Targeted checks confirm three funded commitments plus the unfunded fallback, objective-first fourteenth-day handling, exclusive results, the pre-response northern handoff, complete orphan/dissolution/theatre cleanup, and ownership/peace/campaign/Geneva neutrality.

### Completed behavior

- `FRE_Operation_Lorraine` is no longer a selectable mission or standalone generic border war. It prepares a response package attached to VIN's live Northwest/Tay Bac primary campaign; the date fallback lets the FRE tree progress if Hanoi never launches that campaign, and a prepared plan is offered automatically if it launches later.
- Lorraine offers three live choices: the historical deep Clear River thrust, a shorter raid-and-withdraw option, or withholding the mobile groups for Na San. The deep thrust spends War Credits and Metropole Patience, disrupts VIN Campaign Supply and campaign time, applies bounded supply penalties, and uses a named Dong Bac Bo rear-area objective rather than an unrelated-border fallback. The shorter raid causes a smaller immediate disruption without opening a second front. The Na San choice supplies TAI and grants a campaign-only defensive spirit.
- The response records exactly one permanent result: strategic success, limited tactical raid, failure, forces withheld, or theatre-superseded. Its result combines the deep thrust's own seven-day rear-area hold with the parent Northwest result. It cannot transfer territory, make peace, or terminate the primary campaign.
- The VIN resolver commits Lorraine's response result before common Northwest cleanup. Normal resolution, direct cleanup, CEFEO dissolution, and theatre supersession remove all Lorraine/VIN/TAI response spirits and active posture flags. The legacy Lorraine operation watchdog and credit-reserve reader no longer consume the response package.
- FRE and VIN receive cross-tree Lorraine conclusion events. The AI receives narrowly scoped Dong Bac Bo raid/counter-raid orders only for the deep posture; the existing Northwest objective and reserve orders remain in force.
- Hoa Binh is now explicitly two-stage inside the existing map abstraction. TAM's control of state `1766` is the completed French seizure/established salient; VIN campaign ID `2` begins Giap's counteroffensive and immediately attaches the CEFEO phase-two response to that same parent campaign.
- The old `FRE_Battles.5` no longer free-fires 200-245 days after Mao Khe for flat ledger changes. It is raised once by the live Hoa Binh campaign and offers the historical Operation Amarante plan or a funded hold-the-salient alternative. Historical-focus AI is forced onto Amarante; nonhistorical AI uses an 80/20 withdrawal/hold split when the hold is affordable.
- Amarante spends 30 War Credits and commits 1,500 manpower to schedule the fighting withdrawal for campaign day `105`. If it executes while Hoa Binh remains French-held, the result returns that manpower, 2,000 infantry equipment, 250 support equipment, and 100 artillery equipment; grants 75 War Credits; adds 25 de-escalation points; preserves a `+10` Na San preparation callback; and directly waives the parent clean-result `-12` Metropole Patience shock. It never changes the clean Viet Minh battlefield/Struggle result, transfers Hoa Binh, or makes peace itself: the parent resolver remains the sole owner of transfer, TAM annexation, rewards, peace, and cleanup.
- Holding Hoa Binh requires 80 War Credits and commits 4,000 manpower up front, supplies TAM, and replaces the phase-one salient modifier with a bounded defender-only state-`1766` holdout modifier plus state-focused AI demand. A true hold is now only parent outcome `4`, meaning the salient survived the final day-`210` deadline; an absent-war abort is inconclusive and cannot collect the victory package. A successful hold adds 100 War Credits, 10 Patience, 3% War Support, and a 25-point two-sided Struggle swing in addition to the normal parent failure reward. A committed hold that loses adds a further 3,000 manpower, 1,500 infantry equipment, 150 support equipment, 75 artillery equipment, 75 War Credits, 8 Patience, and 4% War Support loss, plus 50 escalation and a 25-point two-sided Struggle swing toward the communists.
- Hoa Binh records one response result before common cleanup: orderly withdrawal, held, lost, inconclusive, or superseded. CEFEO dissolution, orphan checks, and every parent-campaign exit clear its temporary state modifiers, posture flags, and withdrawal request without granting the response ownership of the war.
- Mixed player/AI engine runs confirm consistent Hoa Binh passes and clean response/resolution behavior. The follow-up now presents the asymmetric contract explicitly: Amarante concedes Hoa Binh on day `105`, preserves the field force, offsets the French Patience loss, and continues the wider war; holding retains the objective, risks the force to day `210`, pays a larger success reward, and suffers an additional result-dependent loss package if broken. Neither route changes primary-campaign ownership.
- The scoped player-facing English audit replaced raw country-tag prose and exposed implementation language in the reworked campaign, Lorraine, southern-war, and legacy named-operation tooltips. Internal keys/scopes and variable expressions remain unchanged.
- A recorded communist capture of Dien Bien Phu now raises one VIN briefing even when the NLF is already defeated or absent. The visible strategy is a focus fork after `VIN_Prepare_Dien`, gated by the recorded fall, an idle VIN campaign system, and the absence of an announced, active, or concluded Geneva conference.
- The 14-day historical focus `VIN_Push_for_Negotiations` grants 25 Communist leverage, adds 150 de-escalation points, starts `Indochina_Geneva_Pursuit`, and owns a renamed queue latch. Its immediate and daily checks retain `geneva_conference_vietnam_at_peace_trigger`; only a divisionless NLF paper war may be repaired, and only after VIN is at peace. The existing delegation and `VIN_The_Geneva_Peace_Conference` systems remain authoritative.
- The mutually exclusive 34-day `VIN_Carry_the_Revolution_South` costs no political power or Campaign Supply. It reuses the old funded-NLF posture and exact support package when NLF exists, adds 25 Communist Struggle score and 50 escalation points, clears VIN-owned pursuit/queue state, and suppresses the panic-collapse Geneva route without disabling deliberate French, American, or other conference entry points.
- The escalation continuation consists of a 56-day mobilization and a 14-day general offensive. Mobilization grants a 180-day +10% planning speed, +5% organization, -5% supply consumption, and +2% reinforce-rate spirit plus VIE-front AI and northern reserve buffers. The terminal directly declares one `annex_everything` war on VIE if no war already exists; it never sets the 1960s `Vietnam_War` flag, explicitly calls FRE/FRA, or changes NLF independence/ownership.
- Save compatibility maps the old talks posture into the focus-owned queue, maps funded-NLF into the escalation posture, and clears a legacy autonomous queue without touching an externally owned Geneva pursuit. Diagnostics and AFK telemetry report strategy exclusivity, queue ownership, the peace gate, panic suppression, NLF independence, preparation cleanup, and the guarded invasion.
- Castor now spends its manpower, transports, War Credits, and Patience at the airborne commitment event rather than at a later generic-operation prompt. Full and limited drops create different garrison tiers; a successful fourteen-day establishment returns a bounded part of the commitment, while a failed thirty-day effort applies posture-scaled losses. A lost landing ground before the drop and an unfunded plan receive distinct non-deployment conclusions.
- The camp fortification helper now sets the intended bunker and anti-air levels instead of repeatedly stacking construction. The siege state modifier is added only when VIN campaign ID `3` is actually live, so Castor can establish the pre-siege position without starting the siege months early.
- Castor's daily pulse, visible timer backstop, weekly orphan check, CEFEO dissolution, Struggle ending, and fallback dispatcher all share the dedicated result/cleanup state. If VIN campaign ID `3` begins before establishment completes, a handoff closes Castor as superseded while preserving its already-deployed garrison for the parent siege. Console helpers start, advance, fail, inspect, and reset the airhead lifecycle without routing through the generic operation wrapper.
- Live Dien Bien Phu campaign ID `3` now raises one CEFEO defensive choice. Standard hold commits manpower and accepts the scheduled airlift; maximum reinforcement spends War Credits, manpower, and Metropole Patience to strengthen the camp and delay siege degradation by fourteen active-siege days without changing the fixed campaign deadlines.
- Operation Condor becomes a map result rather than an advance bonus. It arms only after the Viet Minh satisfy the existing approach-plus-ring investment prerequisite, then requires French-aligned control of the camp, one northern/eastern approach, and one ring position for seven consecutive daily ticks. Opening the corridor relieves fourteen siege days and records force preservation, but the best response payoff still requires the camp to survive the parent day-`260` deadline.
- The Vulture posture spends War Credits and Patience to ask Washington for limited air support through the retained `FRE_DBP.10` event. Approval supplies the defenders, adds a bounded state modifier, and relieves ten siege days; refusal grants no battlefield aid. Completing `USA_50s_Operation_Vulture` during the campaign feeds the same support hook and retains its existing direct-intervention wars and diplomatic costs.
- Every posture pays its best reward only from parent outcome `4`, records a fall only from the parent's clean/costly camp capture, and treats an absent-war abort as inconclusive. Maximum commitment, failed Condor, and the Vulture route have distinct loss packages and conclusion prose; supersession is rewardless.
- The response resolves before `vin_dbp_record_outcome`, owns no state transfer, annexation, province-control mutation, white peace, campaign resolver call, or Geneva announcement, and is removed by parent cleanup, weekly orphan handling, CEFEO dissolution, or theatre supersession. State-scoped posture modifiers and CEFEO/TAI AI plans are limited to Tay Bac Bo.
- New `test_fre_dbp_response_status`, `test_fre_dbp_response_daily_check`, and `test_fre_dbp_response_reset` effects report and reset the response without changing the parent campaign, map, or Geneva recorder.
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
- Shared geography triggers now distinguish each VIN operational envelope, previously captured VIN home territory, starting bridgeheads, the Northwest outlier, and French-aligned penetration into VIN rear areas. A daily one-tier overextension penalty applies and clears from VIN or the entire FRE/VIE/crown-domain side as control changes; Nghe-Tinh is now correctly included as VIN rear ground.
- Campaign cleanup removes overextension and campaign-command spirits before any target annexation, during normal finish, during Struggle ending cleanup, and from FRE during CEFEO dissolution.
- The Dien Bien siege now requires an eastern/northern approach plus a separate valley-ring province before siege days accrue. AI assistance can finish an established siege but cannot invent the investment.
- The first balance pass removes the blanket French combat penalty, reduces VIN campaign mobilization to a moderate logistics benefit, reduces the objective-state defense penalty from 80% to 25%, removes the generic VIN AI push into the FRE delta, and adds targeted CEFEO defense for Tay Bac, Hoa Binh, and Dien Bien Phu.
- Campaign state policy is now explicit and self-healing. Cao-Bac opens only `1280`/`1768`; Northwest opens `1761`; Hoa Binh opens `1761`/`1766`; Dien Bien opens `1761`/`671`. The nine northern states damaged by the old broad cleanup are rebuilt before the operation is applied each day, while the full Indochina `unplanned_offensive` baseline is rebuilt at launch and resolution.
- Temporary planned offensives no longer clear `VIN_unplanned_offensive_flag`. Cleanup restores the baseline after clean, costly, aborted, failed, or superseded resolution; theatre-ending cleanup still removes it normally.
- Hoa Binh now treats Hoang Lien Son as a contested approach as well as Hoa Binh itself. Tay Bac Bo remains protected during Hoa Binh and becomes planned only for Dien Bien Phu.
- VIN-controlled Thanh Hoa, Nghe-Tinh, and Quang Binh receive a campaign-only local-supply modifier representing dispersed caches and porter relays. The first implementation failed to attach in engine; the repaired helper evaluates control from state scope, applies an explicit indefinite modifier, forces its refresh, and raises its bounded local supply from `0.25` to `0.50`.
- VIN's broad tag-front wartime strategy now aborts while a named campaign is active. Campaign strategies retain reserves across Dong Bac Bo and all three southern-base states, apply strong negative requests to VIE/NUN and non-objective FRE/crown-domain fronts, and reduce the stacked global `ignore_army_incompetence` value from `300` to `50`.
- FRE, VIE, THO, TAI, TAM, and NUN now suppress requests into VIN's rear areas and receive state-scoped rather than tag-wide campaign plans. Those plans may counterattack within their assigned state; they do not authorize general pursuit. Deep Lorraine remains the only scripted Dong Bac Bo offensive exception.
- MEO has a self-defense-only Ha Giang plan with no corresponding VIN deployment request. Its own divisions are ordered to remain in state `1767`, avoid allied-border diversion, and satisfy local front demand. TAI still begins with a fourth battalion at Dien Bien Phu.
- VIE's historical NUN event may still update NUN's nationalist identity, politics, and leadership, but its autonomy transfer has been removed. NUN therefore remains under CEFEO custody and in the northern war instead of silently becoming a VIE subject.
- New diagnostics report current planned/protected states, missing rear-area supply, and post-campaign restoration failures.

### Deferred work

- Human CEFEO engine acceptance of the revised Hoa Binh contract: one Amarante execution and one day-210 hold/lost-salient wager test.
- A severe/deep overextension tier; the first replacement patch intentionally ships one tier on geography helpers that can support a second.
- Alternate-terminal and balance coverage for the new Dien Bien Phu response package plus exact-province Castor; their full historical path has engine acceptance. Remaining FRE operations and supporting narrative content remain deferred.
- A post-failure recovery route from an unsuccessful Northwest campaign into Dien Bien Phu. The present focus still requires ownership of `1761`; this patch repairs the false failures caused by lost modifiers/supply but does not turn a genuine Northwest defeat into a free valley campaign.
- Extended engine coverage of the implemented northern/southern French Indochina command interface, especially old-save migration, intentional defection exits, and CEFEO dissolution ordering. Core faction membership and separate-war behavior passed the initial playtest on 2026-08-13.
- Deletion of the now-unassigned legacy northern adjacency-rule definitions after the unrestricted connections pass an engine map test. Their CSV assignments are already retired, so they no longer affect movement.
- Named colonial THO leadership research; the restoration patch uses a generic territorial council.

### French Indochina command implementation

- French Indochina is implemented as a fixed CEFEO-led faction rather than the old VIE-led State of Vietnam faction. Its members are CEFEO, State of Vietnam, Cochinchina, the Montagnard crown domain, Tai Federation, Nung territory, Muong Federation, and Tho territory. France remains outside both the faction and the CEFEO subject chain.
- The faction owns a hidden no-call rule and a hidden no-leadership-change rule. This makes it a coordination/access wrapper instead of a war-merger: CEFEO enters attacks on its northern crown-domain subjects, VIE and its southern subjects fight the southern Viet Minh, and neither command can summon the other through ordinary faction diplomacy.
- Hanoi's Viet Minh faction contains NLF at startup, restoring the original diplomatic relationship after engine feedback rejected the temporary separation model. `VIN_NLF_Coordination_Channel` and `NLF_Hanoi_Coordination` remain the scripted political/logistical interface. Membership must not make VIE and VIN direct belligerents.
- The four northern crown domains remain CEFEO subjects with `autonomy_crown_domain`; Cochinchina and FUL remain VIE subjects. Crown domains may join their CEFEO overlord's closed faction, while the faction call rule prevents their membership from broadening a war.
- VIE's Pau and Matignon focuses no longer touch Nung custody or display fictitious autonomy changes. Live pro-French VIE coup routes retain their political-status spirits without becoming direct French subjects. The French communist-collapse event likewise keeps CEFEO independent and preserves VIE's southern custody chain.
- The VIE Nung settlement decision cannot run while CEFEO custody/the war remains live. The historical `NUN_Unification.2.a` political/leadership result still owns no autonomy transfer. Nung communist and independence routes, FUL independence, CCC rupture, and the existing FUL-to-France branch now leave/remove the appropriate command identity explicitly.
- CEFEO dissolution dismantles French Indochina before crown-domain handback and before FRE annexation, preventing unintended faction succession. General Struggle cleanup also removes the new command identity as a final leak guard.
- The French-command initializer remains one-shot so save reloads do not undo intentional local defections. It retires the old Saigon faction; a narrow startup sync outside that one-shot block restores NLF to VIN only during the live Indochina theatre when both coordination flags still exist, repairing saves made by the temporary separation model. Intentional later generic VIE factions remain untouched.
- The French Indochina and Viet Minh faction templates both use the hidden no-call rule. `French_Indochina_Faction`, `State_of_Vietnam_Faction`, and `Viet_Minh_Faction` give AI `-1000` ally-get/call/join desire and allow call refusal, matching the existing State of Vietnam protectorate safeguard. The 1953 Laos raid applies the same isolation policy to the Kingdom of Laos before its declarations rather than after them.
- `test_indochina_command_status` checks faction leadership/membership, northern and southern custody, VIE-VIN non-belligerence, VIN-NLF membership, the VIE-NLF base war, and NLF-CEFEO leakage. `test_indochina_command_repair` rebuilds only an early setup damaged for testing or loaded from a legacy save.

### Dien Bien Phu defensive-response implementation

- The first implementation is complete. It preserves the existing siege investment, exact camp objective, day-`150` clean boundary, day-`260` final boundary, and Geneva recorder while replacing the production use of the delayed arithmetic-only final-assault chain.
- The same working patch now includes exact-province Castor so one external save can test airhead establishment and the later defense in sequence.
- Historical-path engine acceptance is complete. Remaining branch coverage should use the diagnostics for Castor's alternate commitment, broken-streak reset, deadline failure, and supersession; the alternate defensive postures; parent failure/hold and clean/costly camp fall; absent-war abort and supersession; Condor's investment-and-seven-day corridor gate; and limited/direct Vulture outcomes.
- Do not tune the accepted VIN objective or primary lifecycle from a response-package result alone. Tune posture costs, state modifiers, relief days, and AI demand first.

### Changed systems

- French Indochina faction template/rules, faction-status UI, CEFEO startup/dissolution, VIE/VIN/NLF histories, VIE diplomacy/events/decisions, Nung and FUL exit paths, centralized faction/VIE localization, and command diagnostics.
- FRE Northwest focus behavior, Lorraine response effects/triggers/events, response ideas, targeted AI, legacy-operation mission/watchdog isolation, and CEFEO cleanup.
- Exact-province Castor focus/event/effect/mission behavior, its state modifier and GONO tiers, generic-operation ID-`5` retirement, fallback integration, cleanup, localization, and diagnostics.
- FRE Hoa Binh response effects/events, the repurposed Meat Grinder choice, Operation Amarante's parent-resolver request, defender-only state modifiers/AI, conclusion events, localization, cleanup, and diagnostics.
- VIN Northwest launch/resolution callbacks, post-Dien Bien Phu southern-war triggers/effects/events/decisions, NLF support spirit, Geneva-pursuit integration, and diagnostics.
- Canonical design documentation and implementation ledger.
- VIN campaign scripted triggers, effects, clock/backstop decisions, result events, scripted localization, result localization, and failsafe coverage.
- VIN northern focus behavior, early economic state targeting, and Hanoi asset relocation.
- THO/VIN country history, Cao Bang/Lang Son ownership, THO and VIN starting OOBs, and colonial/communist THO lifecycle helpers.
- Indochina Struggle ending cleanup and VIN/FRE theatre AI strategies.
- FRE, Viet Bac, and VIN campaign test effects.
- Indochina adjacency assignments, VIN/FRE campaign and overextension ideas, contested-objective balance, CEFEO dissolution cleanup, and route/overextension test diagnostics.
- Campaign state-modifier lifecycle, Thanh Hoa/Nghe-Tinh/Quang Binh local supply, VIN/FRE/VIE/crown-domain/MEO theatre AI, the TAI starting OOB, and the NUN unification event's custody-preserving behavior.

### Verification

- 2026-08-13 faction-isolation follow-up: `git diff --check`, Clausewitz structure checks for the touched gameplay files, and `python3 tools/loc_audit.py --check` pass. Targeted source checks confirm NLF is added by VIN history and restored for live-theatre saves initialized by the separation model; both local faction templates own the hidden no-call rule; all three faction identities carry `-1000` AI ally-get/call/join desire and call-refusal permission; and the Kingdom of Laos receives its matching safeguard before the event's declarations. The user's initial engine playtest confirmed that the faction rework functions correctly; longer-run migration, defection, dissolution, and Laos edge branches remain useful coverage.
- 2026-08-12 initial French Indochina command static verification (partly superseded): the original checks passed, including the now-rejected NLF-separation invariant. The CEFEO leadership/custody/dissolution findings remain valid, but the 2026-08-13 faction-isolation follow-up replaces its NLF membership and call-policy conclusions.
- 2026-08-12 combined engine acceptance: a full player/AI run completed without a reported lifecycle regression. Player-controlled Operation Lorraine reached its proper terminal, defended the intended state, and produced the proper response outcome. Historical AI followed the historical campaign outcome through Dien Bien Phu. After the NLF was destroyed, the ordinary Hanoi/Saigon peace gate passed and the Geneva Conference convened in the historical post-Dien Bien Phu sequence. This accepts Lorraine's historical response path, the combined patch's historical campaign path, and the dead-NLF automatic-Geneva terminal; unreported alternate posture/forced-terminal branches remain diagnostic coverage rather than blockers to the checkpoint.
- 2026-08-11 exact-province Castor static verification: `git diff --check`, raw Clausewitz brace balance across every changed/new gameplay `.txt`, and `python3 tools/loc_audit.py --check` pass. The new Castor effects and state modifier are unique; no generic operation ID `5` or current-operation-`5` consumer remains; the dedicated effect contains no ownership transfer, province-controller mutation, peace, annexation, primary-campaign resolution, or Geneva-result mutation. Targeted checks confirm exact province `4529`, fourteen consecutive hold days, the thirty-day visible timer/backstop, full/limited/up-front costs, objective-first daily resolution, one-of-three permanent results, generic watchdog isolation, weekly/dissolution/theatre cleanup, and a fallback wait only while Castor is unresolved. The combined historical-path run was accepted on 2026-08-12.
- 2026-08-11 Dien Bien Phu response static verification: `git diff --check`, raw Clausewitz brace balance, and `python3 tools/loc_audit.py --check` pass. New response effects, triggers, events, modifiers, AI strategies, and English localization keys are unique in their namespaces. Targeted source checks confirm four live postures, Condor's prior-investment plus seven-day exact-province requirement, both limited and direct Vulture hooks, parent-before-recorder result ordering, fixed day-`150`/`260` deadlines, result-gated payouts, and response ownership neutrality. Parent finish, weekly orphan handling, CEFEO dissolution, and theatre supersession all reach response cleanup. The combined historical-path run was accepted on 2026-08-12.

- Historical baseline, superseded by the focus fork: the 2026-08-11 autonomous post-DBP closure repair passed static verification and its ordinary destroyed-NLF route received engine acceptance on 2026-08-12. Preserve that result only as regression evidence for the shared Vietnamese peace gate and conference backend; the new focus-owned queue and escalation branch require their own checkpoint coverage.
- 2026-08-10 Hoa Binh response static verification: `git diff --check` passed; all edited/new gameplay files have balanced raw braces; new effects, events, AI strategies, state modifiers, and English localization keys are unique; the two legacy delayed `FRE_Battles.5` calls are absent; the sole remaining call is owned by the live response; Amarante contains no transfer, peace, annexation, or direct resolver call; objective capture and theatre supersession precede its request in the primary classifier; and normal finish plus CEFEO dissolution clear the package.
- 2026-08-10 Hoa Binh payoff/clarity follow-up static verification: `git diff --check` and targeted raw-brace checks pass; the three new result-payoff effects and four new/changed response localization keys are unique; a successful hold requires parent outcome `4`; the committed-hold loss package is gated by the hold posture; Amarante still owns no transfer, annexation, peace, or campaign resolution; its permanent withdrawal result alone suppresses the Hoa Binh clean-result Patience loss; the Na San callback appears once in the preparation mission; and the scoped localization audit finds no raw `VIN`/`FRE`/`VIE`/`NUN`/`TAI`/`TAM`/`THO`/`MEO`/`NLF` prose, province/state IDs, border-war language, or primary-resolver language in the audited values. Engine acceptance is pending.
- 2026-08-10 Hoa Binh engine acceptance: repeated mixed player/AI runs produced more consistent passes for both CEFEO and the Viet Minh, with no reported response, campaign-resolution, or cleanup failure. Acceptance exposed one UX/balance failure: a player who held Hoa Binh through day `105` received too little benefit from Amarante and could reasonably interpret the scripted withdrawal as losing a war they had been winning.
- 2026-08-10 external campaign-front acceptance: repeated Northwest runs confirmed the repaired southern supply modifier appears and works, MEO defends or recovers Ha Giang, historical AI can follow the intended campaign result, and a capable player-led side can still dominate. The containment/local-supply follow-up is accepted for continuing content work.

- 2026-08-10 campaign-containment/supply follow-up: `git diff --check` passed; raw Clausewitz braces balance across every modified/new gameplay `.txt`; all new AI/helper definitions are unique; VIN has one reduced campaign-wide `ignore_army_incompetence` strategy and no Ha Giang unit request; FRE has no remaining tag-wide VIN campaign front; the supply helper covers `1762`/`1763`/`838`; VIE participates in rear-area overextension application/cleanup; and no adjacency file changed. Engine acceptance remains pending.
- 2026-08-09 Northwest/Lorraine and post-DBP southern follow-up static verification: `git diff --check` passed; raw Clausewitz braces balance in every modified/new gameplay `.txt` file; all new English localization keys are unique; Lorraine has no selectable-mission or focus call into legacy operation ID 1; response result/cleanup hooks, southern response exclusivity, and Geneva peace-gate preservation passed targeted source invariants. Engine acceptance remains pending.
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

### 2026-08-10 playtest findings

- Historical AI completed the entire campaign sequence and reached the historical Geneva outcome, confirming the objective/resolver spine is robust without restored northern adjacency gates.
- That success concealed excessive general-war movement. During Cao-Bac VIN overran THO but fought deeply through TAI/FRE before recovering two CEFEO-held objective provinces; during Hoa Binh CEFEO penetrated VIN rear areas while the southern base collapsed; during Northwest TAI and MEO were overrun and Hoa Binh changed hands. The next correction must shape front assignment rather than strengthen the already severe `unplanned_offensive` penalty.
- Dispersed Base-Area Supply did not appear beside `unplanned_offensive` in its intended states and provided no observed benefit. Nghe-Tinh, which contains two significant starting VIN formations, was also absent from the original two-state implementation.
- MEO repeatedly left its one-state territory insufficiently defended and capitulated. The chosen fix is MEO self-defense only; VIN is not asked to station forces in Ha Giang.
- A human FRE player defeated the Northwest campaign on its clock while penetrating VIN's interior and taking its northern capital, although encircled Hoa Binh resisted. This establishes that a French campaign victory is achievable and that complete VIN capitulation is not the correct balance target.
- Two AI games have produced VIN Northwest success. Dien Bien Phu remains unchanged pending a larger sample; no adjacency restoration or new combat-stat wall is justified by the current evidence.
- After the containment repair, multiple additional Northwest runs confirmed working southern supply, MEO self-defense/recovery, intended historical-AI results, and player freedom to outperform the script. This closes the containment/local-supply acceptance item.

### 2026-08-10 Hoa Binh response playtest findings

- Mixed player/AI control now produces consistent Hoa Binh passes for both CEFEO and the Viet Minh. The two-stage response, state modifiers, campaign result, and cleanup are mechanically accepted.
- Operation Amarante is not yet a worthwhile player choice. A CEFEO player can control and successfully defend Hoa Binh for the full 105-day withdrawal period, then automatically concede it while receiving too little force-preservation or future-operation value in return.
- A player unfamiliar with the First Indochina War can interpret that outcome as an unexplained loss of the wider war rather than a deliberate withdrawal from one costly salient. The selection tooltip must state the concession, timing, preserved force, continued wider war, and downstream benefit before selection.
- Holding must be framed as the opposite wager: retain Hoa Binh and gain a meaningful result if the Viet Minh offensive expires, but suffer materially worse result-dependent consequences if the position falls. Move appropriate rewards and penalties from selection time to response resolution.
- Player-facing prose should never show raw tags such as VIN, FRE, VIE, NUN, TAI, TAM, THO, or MEO when an in-world name is available. This does not prohibit tag-based localization keys, scope syntax, or variable expressions which the engine resolves before display.
- All localization `.yml` files are required to use UTF-8 with BOM (`EF BB BF`). Plain UTF-8 localization may not appear in game even when its YAML and keys pass the localization audit. Preserve the BOM on edits, add it to every newly created localization file, and verify the first three bytes as part of static handoff checks. The user repaired the files affected by the recent non-BOM edits.

### Known issues

- **2026-08-13 resolved faction-propagation finding:** the first CEFEO-faction run pulled the State of Vietnam and other uninvolved French Indochina/Viet Minh faction members into VIN's scripted campaigns and the 1953 Pathet Lao invasion. VIE later left through campaign white peace, but its temporary participation was still incorrect. The follow-up restored NLF to VIN's faction and added hidden no-call rules, call-refusal permission, `-1000` AI get/call/join desire, and pre-declaration Laos isolation. The user's initial replay confirmed the corrected faction rework functions properly; retain the diagnostics for longer-run and alternate-branch coverage.
- **Resolved in the 2026-08-17 renovation batch:** Hirondelle, Mouette, Brochet, and the Na San/Vinh Yen/Mao Khe preparation paths no longer use the broken generic launcher or legacy delayed arithmetic. See the implementation checkpoint below. The first full VIN run found three follow-up integration defects; their armistice, THO deployment, and objective-clarity repairs are code-complete but await focused engine acceptance.
- The Lorraine rear-depot objective uses the six provinces of state `881` (Dong Bac Bo) as the map's abstraction of the Clear River/Phu Doan rear area. The 2026-08-12 player run confirmed that the intended state can be defended, Lorraine terminates properly, and its response outcome records correctly. Alternate controller/focus-order branches remain useful diagnostic coverage.
- The retired post-DBP decisions and autonomous Geneva bridge have been superseded by the focus-owned strategy fork. Negotiations retain the existing Vietnamese peace predicate and the narrow divisionless-NLF armistice; escalation proceeds through mobilization to a direct VIN-VIE war while leaving the NLF independent.
- This repository environment still cannot run HOI4 directly; all engine findings come from the user's external playtests.
- Hoa Binh's mechanics are accepted and the payoff/contract follow-up is code-complete, but its new result values still need one human CEFEO run per choice. Do not reopen the accepted campaign lifecycle unless those runs demonstrate an engine failure.
- The scoped rework-localization audit is complete. Continue to keep raw tags and implementation terms out of player-facing values while leaving internal keys, scopes, and hidden variable syntax untouched.
- The first overextension release has one tier. Values and province bands are intentionally exposed in shared triggers/ideas for tuning after the next human and AI tests.
- Legacy `SWF_Indochina_War` border-war result events remain for debug/backward compatibility, but the production campaign watchdog no longer calls them. Consolidating or retiring those inert narrative paths belongs with the later unified campaign-ownership work.
- The legacy `FRE_DBP.1-.8` arithmetic siege definitions also remain for old saves and console compatibility, but their Castor-success production fire site is retired and each is gated out once the live response is active or resolved. Engine testing should confirm no delayed pre-patch event copy survives those guards.
- Castor's visible mission is a thirty-day timer while the scripted counter owns the exact fourteen-day streak. Engine testing must confirm that the mission removes cleanly on scripted success and that its final-day backstop credits a valid thirteenth-recorded-day-plus-current-control edge before failing the operation.

### Exact next resume point

- Re-run Cao-Bac and one restored limited battle first. Confirm THO keeps one battalion in each home state through declaration; confirm the exact province highlight, temporary VP label, and 0/5 hold count; and confirm finish removes both the temporary marker and every French-aligned campaign war without affecting Laos. Use `test_vin_campaign_armistice_cleanup` if a participant remains.
- Continue that save through the remaining limited battles and Geneva if the focused replay passes. No vanilla peace conference may appear from a completed set-piece campaign.
- Confirm Brochet/Na San alter both Castor's displayed threshold and debit, Final Push reads actual Mouette/Atlante results, and theatre closure bypasses the consolidation node. Exercise one abort on each side, one supersession, and `test_fre_limited_operation_status`; use `test_fre_limited_operation_supersede` for deterministic cleanup coverage.
- Fold the pending Pollux/Atlante acceptance into that natural run. Keep their existing alternate-route diagnostics and `test_indochina_command_status` available for opportunistic branch coverage. Use `test_indochina_command_repair` only for a deliberately damaged or legacy setup.
- If available, load one pre-renovation save with a launched old operation or preparation mission to verify the one-time migration. After acceptance, the next unimplemented named operation remains Dak Doa.
## 2026-08-17 FRE operations/preparation implementation checkpoint

The previously documented legacy warning is now addressed in the working tree. Hirondelle, Brochet, and Mouette use an exact-objective limited-operation lifecycle with daily control checks, bounded deadlines, terminal result flags, owned-war cleanup, and no territorial transfer. Their historical map contracts are Lang Son/Loc Binh (`9948`, `13761`), Hung Yen (`13755`), and Phu Nho Quan (`11909`).

The old Na San, Vinh Yen, and Mao Khe preparation arithmetic is no longer on the production path. VIN now owns limited primary campaigns for Vinh Yen (`12075`), Mao Khe (`13772`), the multi-objective Day River line (`1185`, `13753`, `13755`), and Na San (`13757`); FRE owns preparation posture and result callbacks. Each offensive requires five consecutive days on its objective and terminates through the common result enum without transferring state ownership.

The implementation also corrects initial control of Vinh Yen province `12075`, makes early results feed the following battle, carries Amarante and Lorraine into Na San, carries Na San/Brochet into Castor, activates Hirondelle's paratrooper-raid unlock, and replaces Final Push's unconditional struggle award with Mouette/Atlante result consolidation. Brochet/Na San change both Castor eligibility and the charged price. Scoped AI orders terminate with their owning package, crossing VIN campaigns supersede limited operations, Final Push has a theatre-closure bypass, and France carries the operation clock so VIN's disappearance cannot strand cleanup. A migration retires active legacy missions and prevents queued legacy outcomes from double-paying.

Static acceptance on 2026-08-17: `git diff --check`, raw Clausewitz brace balance over the 25 changed/new gameplay `.txt` files, the 22-file SEA localization audit, all edited localization BOM checks, targeted event/symbol/localization uniqueness and reference checks, both edited focus-tree cycle checks, exact-objective/owned-peace assertions, the single-carrier assertion, and legacy-result guard checks pass. A fresh 1949-1956 engine playtest remains required before this checkpoint is engine-accepted.

## 2026-08-17 VIN playtest integration repairs

A player-led VIN run reached 1956 and established that the expanded content order and operational pacing flow well. It also exposed three concrete defects in the restored content: THO's two battalions left Cao Bang/Lang Son when Cao-Bac opened; the Vinh Yen-era limited battles did not explain their exact province contracts; and a campaign armistice could white-peace the nominal target while leaving VIN at war with FRE. Continuing that orphaned war allowed an ordinary capitulation and vanilla peace conference, bypassing the intended campaign/Geneva lifecycle.

The armistice contract is now war-wide rather than nominal-target-only. Every primary campaign finish arms `VIN_Limited_Campaign_Armistice_Pending`, directly attempts white peace with FRE, France, TAI, TAM, THO, VIE, and NUN, and retries the same sweep from `on_daily_VIN` until no listed participant remains at war with VIN. Laos tags are not included, preserving unrelated Laos raid/invasion ownership. Limited-campaign declaration also records ownership even when subject/faction propagation made the target technically at war before the declaration branch evaluated. `test_vin_campaign_armistice_cleanup` exercises the production repair and reports whether another daily retry is required.

The first replay of the renovated 1953 CEFEO operations exposed a lifecycle collision in that retry: Hirondelle/Mouette/Brochet could create their fresh limited war while the prior VIN armistice flag still survived, after which the VIN daily tick immediately white-peaced the new operation. The ownership boundary is now explicit. `fre_operation_launch` clears a stale VIN campaign retry before declaring; the retry effect yields whenever `FRE_Limited_Operation_Active` is set; and `FRE_limited_operation_window_trigger` requires FRE and VIN to be at peace so an operation cannot piggyback a residual campaign war. Operation finish remains the sole owner of its deliberate white peace.

THO's two historical starting units remain at Cao Bang and Lang Son, but their defensive strategy now activates before war. It gives both home states maximum front request and theatre demand, suppresses allied/rear fronts and garrison diversion, and uses `dont_defend_ally_borders = 1000`. A separate startup inconsistency was corrected by moving VIN's second militia from TAI-controlled Vinh Yen to the VIN-controlled Hoang Lien Son approach.

Each restored limited battle now states its exact contract in the focus completion tooltip and in a persistent decision card: Vinh Yen and Mao Khe each require one named province; Day River requires Ninh Binh, Phat Diem, and the central line simultaneously; Na San requires the named camp rather than Dien Bien Phu or Son La. The card highlights the exact objective province or provinces, the map provinces have English names, and both the card and campaign clock show the live consecutive-hold count. The shared clock hides the hold line for older campaigns which do not use it.

The follow-up uses the decision system's exact `highlight_provinces` list inside each card instead of highlighting the containing state. Because all six objective provinces begin with zero victory-point value, localization alone cannot render their map labels. `vin_limited_campaign_add_objective_vps` therefore adds a reversible one-point marker only to the current objective set; one flag per campaign makes the effect idempotent, and the guaranteed daily tick repairs active saves made before this visibility layer. Common campaign finish calls `vin_limited_campaign_remove_objective_vps`, subtracting only markers whose ownership flag proves this lifecycle added them. The affected provinces are Vinh Yen `12075`, Mao Khe `13772`, Day River `1185`/`13753`/`13755`, and Na San `13757`.

Static acceptance for this follow-up: `git diff --check`, changed/new gameplay Clausewitz brace balance, the 22-file SEA localization audit, edited localization BOM checks, and 26 exact-objective visibility invariants pass. Focused engine acceptance remains required for THO's declaration-day deployment, exact province highlighting, temporary VP-label appearance/removal, five-day counter display, full French-aligned campaign teardown, survival and ordinary cleanup of the 1953 CEFEO limited-operation wars, and preservation of unrelated Laos wars.

## 2026-08-19 unattended acceptance telemetry

The remaining engine pass can now run unattended under `human_ai`. A passive,
always-on observer writes structured `IC_AFK|` records to `game.log`; it never
selects an option, changes an outcome, transfers territory, makes peace, or
repairs a failed invariant. A declaration-end call captures THO's Cao Bang and
Lang Son battalions before AI movement, while merged startup, daily-France, and
pre-peace-conference hooks observe the rest of the production lifecycle.

The record covers every VIN campaign launch/result, restored objective-marker
activation and cleanup, the retrying French-aligned armistice, the three exact
CEFEO limited operations and their owned-war cleanup, Castor's Brochet/Na San
price callbacks, Pollux and Atlante posture/results, an overlapping Atlante and
Dien Bien Phu launch, Final Push consolidation/bypass, Geneva/theatre closure,
and any premature vanilla peace conference involving an Indochina theatre tag.
It emits a heartbeat every 180 days. Exact province-highlight rendering remains
the one GUI-only observation; the underlying temporary VP-marker lifecycle is
logged automatically.

Static verification on 2026-08-19: scoped `git diff --check`, raw Clausewitz
brace balance for the two new gameplay files and the VIN callsite, effect/call
reference checks, and `python3 tools/loc_audit.py --check` pass. The repository-
wide diff check still reports a pre-existing indentation warning in the separate
dirty VIE/Diem worktree. Engine acceptance remains pending the unattended run
and post-run review of `game.log` plus `error.log`. Run instructions and filters
are in `CWIC Backup/documentation/Indochina_AFK_Playtest.md`.

### 2026-08-19 unattended engine result

The first `human_ai` run reached the end of VIE's 1956 content and produced the
historical scripted Geneva outcome naturally on 1954-05-30. No premature
Indochina peace conference was logged. Every completed VIN campaign armistice
reported zero remaining French-aligned wars; all four restored objective-marker
lifecycles activated and removed their markers; Hirondelle, Mouette, and Brochet
launched isolated wars and reported complete cleanup; Castor established the
airhead; and historical Pollux selected the split withdrawal and recorded its
column-loss result. The Brochet-clean and Na-San-failure callbacks correctly
netted Castor back to its base 100/60 prices.

Two integration items remain open. Both THO battalions were absent from their
home states at the exact Cao-Bac declaration snapshot, so the deployment repair
does not have engine acceptance. Atlante and Final Push never entered the logged
sequence before the historical Geneva closure, so this run supplies no engine
coverage for either package.

The run is a balance failure despite reaching the correct historical ending.
VIN won Cao-Bac on day 11, Vinh Yen on day 8, Hoa Binh on day 3, Northwest on
day 38, Na San on day 10, and Dien Bien Phu on day 10; only Mao Khe became costly
and Day River failed. Hirondelle and Mouette never held an objective for one day
and failed on their deadlines. During the repeated scripted wars, the other
CEFEO crown domains lost their armies and collapsed, leaving FRE effectively
confined to Saigon by the post-1952 sequence.

The next balance design pass should therefore audit and likely remove or sharply
reduce the stacked `VIN_Indochina_AI_Support`, `VIN_Campaign_AI_Support`, and
per-campaign AI resource injections before strengthening CEFEO globally. The
preferred containment direction is a two-tier operational-envelope contract:
AI must remain strictly inside each named operation/campaign envelope, while a
player may exceed it knowingly and receive a severe national/state overextension
package. A launch briefing for both sides should state the exact objectives and
the penalty contract. This is a recorded design direction only; it was not
implemented in this checkpoint.

The telemetry itself had one startup-only invalid-scope error because
`on_startup` has no country ROOT. The daily France carrier recovered and logged
the complete run. The startup hook now explicitly scopes initialization to FRA;
no production campaign logic changed as part of that correction.

### 2026-08-19 VIN/CEFEO balance and containment implementation

The first unattended run's balance correction is now implemented. VIN's two
hidden AI combat packages are no longer granted and are actively removed from
old saves. `vin_ai_prepare_campaign` no longer tops Campaign Supply to maximum
or grants 25,000 manpower, 3,000 rifles, 400 artillery, and 50 command power at
every launch. The retained idea definitions exist only so stale save state can
be cleaned safely.

Campaign participation is now objective-owned. CEFEO joins VIN's war alongside
only the crown domain which owns that campaign target: TAI for Northwest, Dien
Bien Phu, Vinh Yen, and Na San; TAM for Hoa Binh; THO for Cao-Bac; and no crown
domain for Mao Khe or Day River. Hirondelle, Mouette, and Brochet are FRE-VIN
operations and do not call TAI, TAM, NUN, or THO. Their finish path likewise no
longer white-peaces independent crown-domain wars it did not create.

All eight VIN campaigns now enforce exact operational envelopes. Vinh Yen, Mao
Khe, Day River, and Na San exempt only their named objective provinces within
the containing state. FRE's three limited operations apply the same rule to
CEFEO, while VIN is confined to its own territory during Hirondelle/Mouette and
to Brochet's single objective when attacking. Leaving the envelope applies a
single severe national penalty: -60% attack, -35% defense, -45% organization,
-35% speed, -50% planning speed, +90% supply consumption, +75% out-of-supply
penalty, -15% reinforce rate, and +35% attrition. It clears automatically on
withdrawal or operation cleanup. French-aligned campaign overextension is now
evaluated per command, preventing one CEFEO advance from debuffing unrelated
crown domains.

The AI retains positive requests only for the active objective state and gains
strong negative requests for unrelated fronts plus allied-border suppression.
The commitment events tell players that the named objectives are the contract,
that the AI follows it, and that a player may deliberately exceed it at severe
cost. AFK telemetry now records removed-buff checks, exact participant checks,
penalty application/clear transitions, and 180-day division health for CEFEO,
VIN, TAI, TAM, NUN, and THO.

Engine acceptance is pending a fresh 1949-to-Geneva `human_ai` run. Compare
campaign completion days and CEFEO operation hold days against the prior sample,
and use the `FORCE_HEALTH` series to determine whether the crown domains retain
armies through 1952-54. Any `VIN_hidden_AI_buffs_removed` or participant-envelope
`FAIL` is a code regression rather than a balance result.

## 2026-08-19 second unattended-run corrections

The follow-up run exposed three systemic defects despite again reaching the
historical outcome. The Pathet Lao clocks were declared with an impossible
`allowed` condition, AI raids reserved nearly CEFEO's entire field army, and VIN
received 500 duplicate Communist points from focus completion on top of live
campaign results.

Both Laos timers are now FRA-owned and activatable. Cleanup removes every hidden
and visible mission, a 90-day initial and 45-day last-chance daily backstop makes
the lifecycle self-terminating, and CEFEO limited operations cannot launch while
the raid is active. The shared raid AI predicate now suppresses new ambient raids
for VIN and FRE while preserving human access to all raid controls.

The five duplicate VIN focus awards are removed. VIN campaign outcomes are now
roughly quarter-strength, CEFEO limited-operation and response outcomes are
scaled into the same range, and Laos results move the score by 25-50 rather than
three-digit amounts. Escalation-phase arithmetic is intentionally unchanged.
VIN's Geneva seed now converts battlefield score at 1/50 and Communist leverage
at one quarter; PRC/SOV use one fifth. VIN's major focus and post-DBP leverage
awards are also reduced. The target for a complete VIN victory is a Communist
lead of roughly 100-200 points and a Hanoi delegate weight comparable in scale
to Saigon and France rather than the observed ~700.

AFK telemetry now logs six-month Struggle scores, all Geneva leverage pools,
VIN/VIE/FRA weights, Pathet Lao launch/result/duration, stuck-clock failures, and
any illegal CEFEO-operation overlap. Engine acceptance requires another fresh
1949-to-Geneva `human_ai` run.

## 2026-08-21 AFK defect-repair checkpoint

The follow-up log audit queue is code-complete and statically accepted. The
undefined `vin_ai_prepare_campaign` launch call is gone. An active Laos raid is
now rechecked inside `fre_operation_commit`, before any resource debit or
operation activation, and resolves the pending package as superseded. This is
the authoritative guard that focus availability alone could not provide.

THO placement telemetry established the real failure mode: both battalions load
in their historical states, but the Lang Son battalion leaves during peacetime
by June 1949. Because a front strategy cannot guarantee peacetime stationing,
Cao-Bac declaration now re-forms the two AI-only territorial battalions at Cao
Bang and Lang Son if either post is empty. This happens before war declaration
and validation, preserves exactly two battalions, and does not alter objectives,
deadlines, ownership, or campaign rewards. NUN has separate immediate-postwar
and later terminal existence/capitulation/state-ownership records to trace its
previously unexplained post-Geneva disappearance.

Balance values remain frozen pending evidence. The passive FRA daily carrier now
records every Struggle component delta, while the suspected one-time `+350`
Communist victory-preparation award emits a source-specific record. The next log
can therefore confirm or eliminate that award as the late-war overshoot source
without guessing from six-month snapshots.

The scoped runtime cleanup moves Tran Quoc Buu's retirement into NLF scope,
uses the valid generic VIN cleanup ideas, promotes Lo Van Hac through character
roles that already exist, seeds Pathet Lao's required truck variant before its
field-force OOB loads, and replaces the missing Laos demobilization icon with an
existing Laos-war asset. The Lo Van Hac role expiry and `war_industrialist`
trait remain declared on all three relevant ideology roles.

Static verification: repository and scoped `git diff --check`, raw Clausewitz
brace balance across all 17 changed gameplay `.txt` files, targeted lifecycle
and symbol assertions, and the 22-file SEA localization audit pass. External
engine acceptance remains the next step; no deferred operation, including Dak
Doa, should be started until the new baseline logs confirm these repairs.
## 2026-08-22 implementation checkpoint: Dak Doa and Northwest recovery

Implementation has begun. The contract is frozen as follows: Dak Doa is an
NLF-scoped, ownership-neutral seven-day province campaign whose cleanup can
white-peace only an NLF-FUL war it created; its CEFEO response is parent-resolved
before common cleanup. Northwest recovery is VIN campaign ID `9`, permanently
attempted at launch, always costly on success, and leaves campaign ID `1`'s
permanent result untouched. `VIN_Prepare_Dien` continues to require ownership of
state `1761`.

The historical AI defaults to the isolated-post defense represented by the
February 1954 siege; GM 100 remains the expensive counterfactual commitment.
Operational context: https://mcoecbamcoepwprd01.blob.core.usgovcloudapi.net/library/ABOLC_BA_2018/Research_Modules_B/Groupemont_Mobile_100/LaBatailled%27Ankh%C3%A9_ENG_translation.pdf

Code-complete checkpoint: Dak Doa, its CEFEO response, Northwest recovery ID
`9`, shared response validation/logging, scoped console diagnostics, English
localization, AI priorities, and the unified checkpoint playtest are present.
Static acceptance covers diff whitespace, raw braces, localization audit/BOM,
new symbol uniqueness/references, VIN focus acyclicity, permanent-result
exclusivity, ownership/peace mutation guards, and pixel-map adjacency
`1328 <-> 10180/16442/4363`. Unified engine acceptance remains pending.

Engine follow-up: the first alternate run exposed that TAI could receive the
campaign-owned white peace while FRE, pulled into that same recovery war, did
not. Campaign `9` now records a pre-launch war snapshot for the relevant
French-aligned tags. Resolution settles only opponents absent from that
snapshot, retries while a generated opponent remains, and records cleanup
complete only after all such participants are at peace. This preserves an
unrelated pre-existing VIN war while preventing the observed perpetual FRE war.
The Northwest recovery checkpoint must be rerun before engine acceptance.

## 2026-08-23 historical-AI playtest review

The 23 August logs supersede the prior baseline for current runtime behavior.
They do not accept the current battlefield AI or balance. Lifecycle telemetry
recorded no `IC_AFK|FAIL`: both THO declaration posts, participant isolation,
temporary objective markers, campaign armistices, CEFEO operation cleanup, and
Final Push consolidation behaved correctly. The result sequence was Cao-Bac
clean day `51`, Vinh Yen clean day `8`, Mao Khe failure day `36`, Day River
costly day `38`, Hoa Binh clean day `66`, Northwest clean day `102`, Na San
clean day `11`, and Dien Bien Phu clean day `30`. Hirondelle and Mouette failed,
Brochet succeeded, Castor established, Pollux was superseded by campaign `3`,
and Atlante was later superseded.

Two engine errors outrank balance interpretation. The recovery focus uses the
unsupported trigger `political_power > 49`, and the engine rejects
`defender_modifier` in all rework-local state dynamic modifiers. Until the
second issue is replaced by a supported defender-only application contract,
the intended contested-objective, holdout, Castor, Dak Doa, and Dien Bien Phu
packages cannot be treated as functioning balance inputs. The recovery console
inspection also needs to expose its cleanup-complete flag.

The same scoped error review found that `SWF_VIN.17` is deliberately fired in
both VIN and NLF scope but currently gives both options a VIN-only trigger. NLF
therefore receives no valid option. Restore a non-conflicting NLF
acknowledgement or stop sending that player-choice event to NLF. Missing Siam
focus completions in `Indochina_Flavor_Events.txt` are real adjacent regional
errors, but they are not a cause of the northern battlefield behavior and are a
lower priority than the rework-local failures.

The user's map observations establish a systemic objective-allocation problem:
Vinh Yen and Na San were not defended; VIN would not press favorable attacks at
Mao Khe and Day River; raid outposts drew CEFEO/TAI toward Lai Chau/`12319`
during Northwest; MEO did not visibly remain in Ha Giang; VIN entered Dien Bien
Phu before its named campaign; and the Laos AI left Luang Prabang open while
stacking province `13738`. Repair this through exact objective demand, local
minimum presence, raid-versus-campaign priority, and bounded reserve behavior
before applying global combat bonuses.

Operation-specific conclusions are now frozen for the next pass. Brochet's
observed behavior is acceptable. Hirondelle should become an ownership-neutral
airborne cache-destruction/interdiction raid rather than a conventional limited
war. Mouette needs exact southern-Tonkin/Red-River-Delta sweep objectives and
must keep both sides from abandoning the live operation for unrelated fronts.
Lorraine needs visible posture/result reporting. Castor and Pollux must occur
early enough to create a real preparation window; after the rejected defensive
modifier contract is repaired, the DBP garrison/output and siege duration may
be strengthened. Campaign `3` also needs a bounded Hanoi/Tonkin reserve so the
camp objective does not coexist with unopposed CEFEO penetration elsewhere.

The post-DBP focus fork is not yet authoritative. Dien Bien Phu fell on 16 March
1954, the VIN briefing appeared on 17 March, and scripted Geneva concluded on
31 May without evidence that `VIN_Push_for_Negotiations` completed. Shared
French or other pursuit owners can still bypass the visible Hanoi choice. Add
source-specific pursuit/announcement telemetry and a narrow post-communist-DBP
choice/grace latch while preserving the existing Vietnamese peace gate and
legitimate conference routes outside that causal path.

The outcome GUI must now display the full campaign ledger. "The Wars Behind the
Table" currently covers only the southern Viet Minh, Pathet Lao, Dien Bien Phu,
sects, highlands, and the Laos raid. Add the permanent result and actual
Struggle/leverage contribution for every VIN campaign, CEFEO operation, and
attached response package so raw outcomes are visible without observing each
battle live.

The score telemetry rules out the suspected single `+350` award in this run.
The Communist margin reached the desired band at `+184` in May 1953, then rose
through repeated ambient `+25`/`+50` awards to `+364` in October and `+429` in
April 1954. Trace those recurring sources before retuning outcome values. The
southern force comparison is independently unacceptable: VIE grew from `34` to
`38` divisions while NLF remained at `5` and disappeared by late April 1954.
Reduce VIE's effective wartime build/limit advantage and/or provide bounded NLF
sustainment without merging the southern and northern wars.

Revised implementation order: fix engine-rejected syntax, the NLF event with no
valid option, and recovery telemetry; make the post-DBP choice authoritative and log Geneva ownership;
expand the outcome GUI; repair objective allocation and raid interaction;
rework Hirondelle/Mouette; accelerate and then rebalance Castor/Pollux/DBP;
rebalance NLF/VIE and recurring score awards; then perform targeted checkpoint
coverage followed by a unified run. Dak Doa and Northwest recovery remain
code-complete but unaccepted because this natural run reached Geneva before Dak
Doa and did not exercise campaign `9`.

## 2026-08-23 corrective-pass implementation ledger

The corrective pass following the 23 August historical-AI review is implemented
but not yet engine-accepted. It repairs the rejected script contracts, makes
VIN's post-Dien Bien Phu strategy choice authoritative over shared Geneva entry,
adds observer-only CEFEO intelligence and a full campaign/operation outcome
journal, tightens objective AI allocation, converts Hirondelle into a
non-territorial cache raid, bounds Mouette to southern Tonkin, accelerates
Castor/Pollux, strengthens the supported Dien Bien Phu holdout modifiers, and
adds bounded NLF reconstitution. Brochet is intentionally retained unchanged.

This pass also establishes the presentation contract for future polish: VIN is
briefed only on visible French action and uncertain intent; commitment tiers and
resolver arithmetic stay concealed. A later dedicated prose pass may update the
remaining legacy raw keys and omniscient/future-tense writing, but new operation
briefings already use present-tense, fog-of-war language.

The score trace did not identify a repeated `+350` or duplicate campaign result.
The observed `+25`/`+50` deltas correspond to ordinary focus-ledger awards, so
the implementation does not apply a global score nerf without a comparative
run. The expanded GUI exposes exact standings and leverage for that test.

Engine acceptance is intentionally pending. The next sequence is a targeted
smoke pass for parser/event/mission/Geneva and operation contracts, followed by
the unified historical-AI run already requested in this specification.

## 2026-08-29 combined engine-acceptance protocol

Limited tester availability combines the targeted smoke pass and historical-AI
run into one fresh 1949-to-Geneva game. The authoritative procedure and
checkoff are in `CWIC Backup/documentation/Indochina_AFK_Playtest.md`. Parser,
telemetry, stuck-lifecycle, premature peace-conference, and post-Dien Bien Phu
choice-bypass defects are early-stop regressions. AI allocation, pacing,
force-health, and score problems are recorded and carried through the complete
run so the next fix pass has comparable evidence. Engine acceptance remains
pending review of both preserved logs and the completed checkoff.

## 2026-09-28 review of the 2026-09-02 combined run

The 2 September AFK `human_ai` run (`_local/logs/game.log`/`error.log`,
1949-05-23 to 1956-09-14) is the combined acceptance run defined above. Its
checkoff is recorded in `Indochina_AFK_Playtest.md`. Review used telemetry
only; no visual observation was available.

### Engine-accepted by this run

- Primary-campaign and CEFEO-operation lifecycle: 15 launches, 15 results, no
  `IC_AFK|FAIL`, all armistice and limited-operation cleanups at zero remaining
  wars, all four objective-marker lifecycles added and removed, hidden VIN AI
  buffs absent and participant envelopes exact at every launch.
- THO declaration-day deployment in both Cao Bang and Lang Son.
- Hirondelle as an ownership-neutral airborne raid (clean, no war).
- Castor/Pollux timing: airhead 1953-12-28, Pollux resolved 1954-01-09,
  campaign `3` launched 1954-02-15. Castor callbacks from Brochet (clean,
  discount 15) and Na San (failure, surcharge 15) applied.
- Atlante full posture to a stalled result, and Final Push consumption of the
  Mouette/Atlante terminals.
- Authoritative post-Dien Bien Phu choice: briefing 1954-03-11, negotiations
  selected 03-22, peace gate and a single `GENEVA_SOURCE|INVITE` 04-11,
  scripted Geneva concluded 06-25. No premature peace conference.
- Struggle calibration: final Communist margin `+135` (target `+100`-`+200`),
  Communist leverage 300, delegate weights VIN 54 / VIE 43.
- The 21 August runtime repairs did not recur; no rework-local parser errors.

Results: Cao-Bac clean day 36; Vinh Yen clean 12; Mao Khe failure 36; Day River
failure 51; Hoa Binh clean 105; Northwest clean 71; Na San clean 11; Dien Bien
Phu clean 24. Brochet clean, Hirondelle clean, Mouette failure, Pollux column
lost, Atlante stalled, Pathet Lao raid stalemate at day 90.

### Balance queue (open)

1. Metropole Patience sits at 0 from early 1952 to Geneva (brief 10 at
   campaign `3` launch) while CEFEO AI holds 700-1,200 unspent War Credits. At
   0, subsidies are Cut and the wind-down decision is available. Probable
   upstream cause of item 2, because GONO tiers above the minimum require
   Patience above 65 or full Castor [inference, not logged].
2. Dien Bien Phu fell on day 24. The scripted fort floor cannot finish before
   day 55, so ordinary combat took the camp. Standard hold AI demand is only
   ratio 0.8 / priority 750 (`FRA.txt`). The chosen posture is not logged.
3. Vinh Yen and Na San fell in 12 and 11 days. AI strategies are correct, but
   no scripted launch-time garrison exists (only Dien Bien Phu spawns GONO).
4. NLF held 12-13 divisions through 1953, then collapsed by 1954-04-27, while
   VIE reached 44 divisions with wartime army cap 9999. Dak Doa never
   launched; the log does not show which gate failed (NLF was alive after the
   1954-02-10 date gate), so add gate telemetry in the next pass.

### Minor defects (open)

- `events/Indochina_Flavor_Events.txt:343` completes missing focus
  `SIA_Coup_Succeeds`.
- LAO unit `Kong Pathom` needs unavailable motorized equipment.
- `vin_campaign_finish` calls `fre_lorraine_response_cleanup` unconditionally,
  logging Lorraine cleanup and clearing its state after every campaign.
- Unlocked-template warning at `VIN_50s.txt:4944`.
- The Dien Bien Phu response telemetry does not record the chosen posture.

### Not covered

Outcome-journal rendering, Mouette map behavior, Northwest corridor/MEO
behavior, the campaign-`3` Tonkin reserve, supersession payouts, Dak Doa,
Northwest recovery (campaign `9`), alternate Castor/Dien Bien Phu/Lorraine/
Hoa Binh terminals, and southern escalation after Dien Bien Phu.

### Testing constraint

As of 2026-09-28 no tester time is available for AFK or player-led runs. Work
continues without engine runs: balance, defect, and content patches are
statically verified and each records what its test must cover. One
consolidated playtest will later cover the accumulated batch plus the
not-covered list above.

### Unbuilt design content

First Nghia Lo; Bretagne; Adolphe; Camargue; Lower Laos / northeast Cambodia;
Mang Yang and Chu Dreh passes; VIN move on Lai Chau; FRE reject-Dien-Bien-Phu
hedgehog network; Royal Lao and Cambodian army branch; Charles Chanson/Sa Dec;
VIN Luang Prabang all-in; Soviet-versus-Chinese patronage as a campaign input;
Section 9.1 conversion of VIN army focuses into campaign inputs; the second
overextension tier; deletion of unassigned legacy adjacency rules.

## 2026-09-28 review of the 2026-09-28 AFK run

Logs preserved at `_local/logs/2026-09-28/` (run 1949-05-23 to 1962). Tag
reminder: `LAO` is the Pathet Lao, `LOS` is the Royal Lao starting tag.

### Confirmed again

- Lifecycle: 43 `PASS`, no `FAIL`; every campaign/operation recorded one
  result; THO declaration posts passed.
- Castor established 1953-12-26; campaign `3` launched 1954-03-03 (67-day
  preparation window). Pollux column loss.
- Atlante reached `central_success` (first engine coverage of that terminal).
- Post-DBP authority: `GENEVA_SOURCE|DEFERRED ... reason=VIN_post_DBP_choice_unresolved`
  on 1954-04-01, negotiations chosen 04-07.
- Map outcome as observed by the user: Diem in power in VIE, historical
  partition shape, apart from Laos.

### New findings

1. **Pathet Lao conquered the Kingdom of Laos.** The raid resolved as
   `attacker_victory` on day 83 (1953-06-19) after a royal capital (`670` or
   `1198`) fell. `ic_laos_raid_attacker_victory` in `IC_Laos_Raid_Effects.txt`
   sets the result, awards +50 Communist / -25 pro-France score and 100 phase-A
   points, and runs cleanup, but, unlike stalemate and total failure, it
   neither calls `ic_laos_raid_ceasefire` nor defines a settlement. The LAO-LOS
   war therefore continued: LOS had collapsed by 1953-10-29 and LAO reached 17
   divisions. Geneva then adds +100 Communist leverage for the same flag.
   Open design question: whether attacker victory should be a bounded
   capital-fall settlement or an intended conquest branch.
2. **Struggle overshoot returned:** final margin `+498` (target `+100`-`+200`),
   Communist leverage 550 (previous run 300), delegate weights VIN 135 / VIE 25.
   The margin moved from `+103` (1953-05) to `+353` (1953-10) across the Laos
   victory, and the leverage reached 250 by 1953-10. The Laos award is one
   confirmed contributor; the remainder is unattributed.
3. **Geneva closed through `GENEVA_SOURCE|AUTO_RESOLVE` (source 2) on
   1954-08-07**, not the focus-owned invite: NLF was still alive, so the
   negotiations queue never passed the peace gate. The date is historically
   plausible and the post-choice fallback is legitimate, but the
   negotiations route itself did not close the war.
4. Pacing worsened: Northwest clean day 24, Vinh Yen 15, Na San 11, Dien Bien
   Phu 18. Cao-Bac clean 23, Hoa Binh clean 105, Mao Khe and Day River failed.
5. Metropole Patience again hovered at 0-2 from early 1952 through Geneva
   while War Credits sat at 1,070-1,340.
6. NLF fell from 10 to 5 divisions by 1954-04 and collapsed after Geneva;
   VIE reached 46.
7. New adjacent errors: `ic_pulse` (`IC_scripted_effects.txt:7529-7541`) fails
   to spawn three FRA `Division d'Infanterie` divisions on 1952-10-22 (FRA
   template not found); missing Siam focuses at
   `Indochina_Flavor_Events.txt:562-563` (in addition to `:343`); LAO
   `Kong Pathom` motorized equipment persists.

### Pathet Lao raid hardening (code-complete 2026-09-28, untested)

User decision: conquest after attacker victory is intended, but it must be
hard to reach. Changes:

- `laos_raid_attacker_holds_capital` is replaced by
  `laos_raid_attacker_holds_both_capitals`: VIN, LAO, or NLF must control both
  capital provinces, Vientiane `1464` and Luang Prabang `4613`. This gates
  the daily victory check and the deadline resolution. LOS capitulation or
  disappearance still counts as victory.
- Raid launch fortifies both capital provinces to bunker level 2 (not removed
  afterward) and adds the state modifier `laos_raid_capital_defense` (+20%
  defence, +15% max dig-in, +30% local supplies, +10% local org regain) to
  states `670` and `1198`. Raid cleanup removes the modifier.
- `LOS_hold_the_capitals`: both capitals now get priority-1100 front control
  and unit requests of 1000; Phongsaly, Sam Neua, and state `1750` get -500.
  The border-wide LAO/VIN unit requests (400/350) and the `garrison 500`
  strategy are removed; border front control no longer makes manual attacks.
- Mission, event, and news localisation now says both capitals are needed.

Consolidated-playtest checks: the raid ends in stalemate or failure unless
both capitals fall; LOS divisions stand in `1464`/`4613` rather than on the
border (for example province `13738`); the modifier disappears at cleanup.
Static checks: brace balance, `git diff --check`, localisation BOM and ASCII.
`tools/loc_audit.py` no longer exists in the repo.

## 2026-09-29 tracing, negotiations gate, balance and defect pass

Code-complete, statically verified only (brace balance, `git diff --check`,
script files without BOM, localisation BOM and ASCII, one definition per new
name). No engine run.

### Struggle writer tracing

Evidence from the 2026-09-28 run: 136 `SCORE_DELTA` lines, dominated by
Communist `+25` steps roughly monthly. `indochina_struggle_vin_focus_standard`
(+25) has 226 call sites (VIN_50s 166, VIN_FORPOL 85 across all tiers), while
pro-France focus grants have 12. The VIN focus tree is the leading
structural suspect; the new tracing will confirm or reject it.

- `IC_AFK|SCORE_WRITE|track|amount|writer|root` is logged by every
  `indochina_struggle_award_*` / `grant_*` primitive, the raid award/penalty
  wrappers, the communist-victory preparation award, VIN campaign results,
  Laos raid results, USA levers, VIN post-DBP southern funding, and Dak Doa.
  Helpers: `ic_afk_trace_score_<track>` and `ic_afk_trace_score_pair`
  (`IC_Indochina_AFK_Validation_Effects.txt`).
- Writer codes: 1 phase-point award, 2 generic grant, 3/4/5/6 VIN focus
  standard/major/breakthrough/capstone, 7 raid actor, 8 raid victim, 9 raid
  penalty, 10 communist-victory preparation, 11 VIN campaign result, 12 Laos
  raid result, 13 USA lever, 14 VIN post-DBP southern funding, 15 Dak Doa.
- The daily observer subtracts traced writes and logs the remainder as
  `IC_AFK|SCORE_UNTRACED` (legacy event options, FRE response packages, the
  `FRA_1950s` -200 focus, clamp-to-zero corrections).
- `IC_AFK|LEVERAGE_WRITE` is logged by every `geneva_add_*_leverage` effect.
- `SCORE_AWARD` is retired in favour of `SCORE_WRITE` (writer 10).
- Fixed: `indochina_raid_award_actor` tested `FRA.ic_award` instead of the
  pro-independence array, so pro-independence raid actors never scored. This
  slightly raises pro-independence score.

### Negotiations gate (user decision: NLF must be dealt with first)

Root cause: `vin_post_dbp_focus_geneva_queue_tick` waits for
`geneva_conference_vietnam_at_peace_trigger` (VIN and VIE both at peace). The
only repair released a zero-division NLF, so an NLF with about 5 divisions kept
VIE at war, and the AI-only wrap-up timer fired `AUTO_RESOLVE`. VIN funding of
NLF was not involved: `vin_post_dbp_fund_southern_war` belongs to the
Carry the Revolution South branch, which was not chosen.

Change (user chose "defeat or VIN stand-down"): the first queue tick sets
`VIN_Post_DBP_NLF_Stand_Down_Ordered` and a 90-day
`VIN_Post_DBP_NLF_Stand_Down_Pending`. Once VIN is at peace, a disarmed NLF is
released at once; otherwise VIE and NLF white-peace when the delay expires
(`VIN_Post_DBP_NLF_Stood_Down`). The Geneva peace gate itself is unchanged.
`indochina_war_still_being_fought_trigger` holds the wrap-up timer while the
stand-down is pending. `stage=gate_blocked` records whether VIN or VIE still
blocks the gate afterwards. The `VIN_Push_for_Negotiations` description
now explains the stand-down.

### Balance

- Patience: nine Metropole request decisions get AI factor 0 through
  `FRE_ai_patience_request_hold_trigger` (AI, Patience below 45).
  Administrative Support is exempt because mission political power depends on
  it. New `FRE_Fund_Metropole_Information_Service`: 150 War Credits for +8
  Patience, 60-day cooldown. The AI takes it only above a 450-credit reserve,
  when credits are not short for an operation, and while Patience is 70 or
  below. It logs `FRE_PATIENCE_SINK`. The heartbeat logs `METROPOLE`.
- Dien Bien Phu: the GONO floor is three groupements at every tier. Tier 1
  adds the BMEE, and tier 2 adds a 3e Groupement plus the stocks. Every
  deployment logs `DBP_GARRISON`. New
  `FRE_dien_bien_standard_hold` (ratio 1.0, priority 900, request 650,
  theatre demand 25) and `TAI_dien_bien_standard_hold` (0.9/950/550). Each
  posture logs `DBP_POSTURE`.
- Vinh Yen / Na San: `fre_preparation_deploy_garrison` spawns
  `Groupe de Defense Locale` divisions for the controller (FRE, TAI or VIE) of
  `1761`/`671` at launch: 2 plus the preparation tier (up to 4), placed at
  `12075`/`13757`. `fre_preparation_disband_garrison` in
  `vin_campaign_finish` and CEFEO dissolution deletes them, and they never
  touch ownership. Deployments log `LAUNCH_GARRISON`.
- VIE: `CWIC_indochina_wartime_cap_active` (AI VIE, at war, Indochina War not
  over) sets `CWIC_max_divisions = 30` and lets the weekly demobilisation loop
  run in wartime at the 3% disband rate. The Korean War exemption does not
  apply to it.

### Defects

- Lorraine cleanup in `vin_campaign_finish` now runs only when a Lorraine
  flag or idea is present.
- The Siam flavour events no longer complete 13 focuses that do not exist
  (`SIA_Coup_Succeeds` and others). They had no other readers.
- `Kong Pathom` (both LAO OOBs): artillery, which needs `motorized_equipment`
  in this mod, is replaced with a third militia.
- Phase 2 (`IC_scripted_effects.txt`): FRA now spawns its three Tonkin
  divisions from a scripted `Division de Marche du Tonkin` template, not the
  history template `Division d'Infanterie` that could not be resolved.
- `VIN_Formalize_Tieu`: the empty duplicate `completion_reward` is removed.
  The `add_units_to_division_template` "unlocked template" warning remains:
  fixing it means locking `Trung doan Bo binh Infantry`, which is a design
  decision.

### Consolidated-playtest checks added

1. `SCORE_WRITE` totals per writer between 1953-05 and 1953-10 account for the
   margin rise, and `SCORE_UNTRACED` stays small. Report the writer-3 share.
2. After negotiations: `stage=nlf_stand_down_ordered`, then `nlf_released`
   within 90 days (if VIN is at peace), then
   `focus_queue=consumed|peace_gate=passed` and `GENEVA_SOURCE|INVITE`, with no
   `AUTO_RESOLVE`.
3. `METROPOLE` Patience stays above 0 through 1952-1954, `FRE_PATIENCE_SINK`
   fires, and War Credits no longer sit above 1,000.
4. `DBP_GARRISON` tier and at least 3 groupements, `DBP_POSTURE` logged, and
   Dien Bien Phu holds past day 24.
5. `LAUNCH_GARRISON` for campaigns 5 and 8, the garrisons are gone after
   `RESULT`, and Vinh Yen/Na San last past days 12/11.
6. VIE `ARMY_CAP` shows cap 30 in wartime with divisions converging to 30,
   and NLF is still alive at the post-DBP choice.
7. No Lorraine cleanup log after non-Northwest campaigns; no `Kong Pathom`
   locked-equipment error; no Siam missing-focus errors; no Phase 2
   malformed-token error.
8. `IC_AFK|DAK_DOA_GATE` (every 30 days after 1954-02-10 until Dak Doa
   launches) names the failing input: prerequisite focus, NLF/FUL/FRE
   existence, NLF wider southern war, or NLF control of province `10180`.

## 2026-09-29 content pass: first Nghia Lo and the hedgehog network

Code-complete, statically verified only. User decisions: Nghia Lo is a VIN
limited campaign with a CEFEO response. The hedgehog network is a focus that
excludes Castor and leaves Geneva's Dien Bien Phu outcome unrecorded. Values are
first-pass and are not tuned from one run.

### First Nghia Lo (VIN campaign `10`)

- Nghia Lo is province `13773` in Hoang Lien Son (`1761`), which is inside the
  Northwest envelope but not one of its five objectives. The province was
  chosen from map centroids, not from an in-game check (see check 9).
  `VICTORY_POINTS_13773` names it.
- Focus `VIN_Strike_Nghia_Lo`, below the Day River at tree position (47,9).
  It needs the Day River focus, a date after 1951-09-25, a French-aligned
  `1761` that VIN does not own, and the campaign window, idle and cooldown
  gates. It is optional: `VIN_Liberate_Duyen` does not require it. After the
  theatre closes, completion sets `VIN_Nghia_Lo_Focus_Superseded` and launches
  nothing.
- The campaign follows the Vinh Yen/Na San pattern and goes through the shared
  resolver and cleanup. It opens its own TAI war. VIN must hold `13773` for 5
  days: clean by day 25, final deadline day 40. The objective VP is temporary,
  the battle clock is the `VIN_Nghia_Lo_Objective` mission, and the cooldown is
  30 days. No territory changes hands, and the general payout by outcome is
  used. Overextension lets VIN hold every Northwest corridor province except
  Nghia Lo itself.
- CEFEO response: `FRE_Preparation.5`. Tier 1 if de Lattre is in command.
  Tu Le airborne relief (2 transports, 30 War Credits) raises the tier to 2 and
  adds a relief group. The launch garrison is 1 plus the tier, owned by the
  controller, at `13773`. `fre_preparation_disband_garrison` removes all of it.
  Results: `FRE_Nghia_Lo_Result_*` and `FRE_Nghia_Lo_Defensive_Success`.
- Optional follow-on effects:
  - A held Nghia Lo adds 1 to the Na San preparation tier (still capped at 2).
  - A VIN clean or costly result gives the Northwest campaign +25 Campaign
    Supply at launch.
- AI: `VIN_campaign_nghia_lo_push` and `FRE_TAI_defend_nghia_lo`; the focus
  is in the VIN historical AI list after the Day River. France is called into
  the war as for Na San. The campaign journal has a new Nghia Lo line.
- Telemetry: `LAUNCH`/`RESULT` for campaign `10`, the marker PASS/FAIL,
  the participant-envelope check, `LAUNCH_GARRISON|campaign=10`, and
  `NGHIA_LO_RELIEF`.

### Hedgehog network (FRE, excludes Castor)

- Focus `FRE_Hedgehog_Network` at (15,4), with the same prerequisites as
  Castor. The two are mutually exclusive. It becomes available from 1953-11-01
  under the same live and idle gates, with `671` French-held and at least 120
  War Credits. The historical AI never picks it.
- Cost: 120 War Credits, 4 Patience and 3,000 manpower. It sets bunker level 3
  at Na San `13757`, Lai Chau `13765` and Luang Prabang `4613`, and adds
  `FRE_Hedgehog_Base` (defence +10%, dig-in +10%, local supplies +25%) to
  states `671` and `1198`. Each base gets `Groupement de Herisson` garrisons
  owned by the controller (FRE or TAI; LOS or FRE at Luang Prabang): 2 each if
  Patience is above 65, otherwise 1, and Na San gets one more after
  `FRE_Na_San_Success`. The garrisons stay for the rest of the war and are
  removed at CEFEO dissolution (`fre_hedgehog_network_cleanup`).
- Dien Bien Phu: `fre_dbp_fortify_camp` builds nothing when
  `FRE_Hedgehog_Network_Chosen` is set. There is no bunker, no GONO and no
  siege floor, and the same applies to the legacy `SWF_Indochina_War.17`
  launch. The Dien Bien Phu response package is skipped, and
  `vin_dbp_record_outcome` is skipped for campaign `3`. Geneva therefore sees
  no Dien Bien Phu outcome, and the post-DBP choice latch
  (`geneva_outcome_dbp = 2`) never opens. VIN's Dien Bien Phu campaign still
  exists, and still takes state `671` on a win. VIN AI weight for
  `VIN_Prepare_Dien` is ×0.3 once hedgehogs are chosen.
- Pollux and Atlante now take either Castor or the hedgehog focus as their
  prerequisite. Pollux is skipped (bypassed) when hedgehogs are chosen, so
  Final Push stays reachable.
- Telemetry: `IC_AFK|HEDGEHOG|stage=established|superseded_at_completion|dbp_camp_not_built|cleanup`.

### Not changed

Geneva outcome values, Castor, the GONO logic, and the Dien Bien Phu response
package when Castor is chosen.

### Consolidated-playtest checks added

9. Nghia Lo: province `13773` shows as "Nghia Lo" near the historical site
   between the Red and Black Rivers. If not, correct the province before
   balancing.
10. Campaign `10`: one `LAUNCH` and one `RESULT`, full armistice, the marker
    removed, `LAUNCH_GARRISON|campaign=10` and, if chosen, `NGHIA_LO_RELIEF`.
    The garrison is gone after the result, and the 30-day cooldown then lets
    `VIN_Liberate_Duyen` launch.
11. Callbacks: the Na San preparation tier includes the Nghia Lo bonus, and the
    Northwest launch shows +25 Campaign Supply after a VIN Nghia Lo success.
12. Hedgehogs (player FRE or a forced non-historical AI):
    `HEDGEHOG|stage=established`, bunkers at the three bases, Castor locked,
    and Pollux bypassed. If VIN attacks the valley:
    `HEDGEHOG|stage=dbp_camp_not_built`, no `DBP_GARRISON`, no
    `DBP_POSTURE`, no `GENEVA_SOURCE|DEFERRED` for the post-DBP choice, and
    Geneva shows the Dien Bien Phu battle as undecided.
13. The campaign journal still fits its window with the extra Nghia Lo line.

## 2026-09-29 review of the 2026-09-29 AFK run: NLF survives the war

Logs preserved at `_local/logs/2026-09-29/`. User observation: NLF still
exists at peace with VIE, and VIE cannot complete its independence focus.

Telemetry: Dien Bien Phu clean on day 45 (1954-08-27). Negotiations were
chosen 1954-09-18 (`stage=nlf_stand_down_ordered`). The stand-down white peace
fired on schedule, 1954-12-17 (`nlf_released|reason=stand_down`, NLF 13
divisions). In the same tick the Indochina failsafe routed
("decisive evidence found"), found no ending, and forced the
never-ending-conflict terminator (`END|result=Indochina_War_Over|phase=100`).
No `GENEVA_SOURCE|INVITE` followed. Only the Geneva ending annexes NLF, so NLF
was left standing.

Root cause: the white peace ended the last theatre war. After 1954-07-21,
`ic_failsafe_theatre_unfinished_trigger` did not count the queued
negotiations as pending content, so the peace hook let the failsafe mutate
before the queue tick reached its Geneva launch block.

Fix: `ic_failsafe_theatre_unfinished_trigger` treats
`VIN_Post_DBP_Focus_Geneva_Queued` as unfinished until 1957-01-01. The
failsafe now skips, and the queue tick launches Geneva in the same tick.

Other results: Nghia Lo clean on day 22 (first engine coverage of campaign
`10`), Northwest failure then Recovery costly, Na San costly on day 41,
Castor success. error.log has no new rework errors; the `VIN_50s.txt`
unlocked-template warning remains.

Consolidated-playtest check 14: after `nlf_released`, the same day shows
`GENEVA_SOURCE|INVITE` and then the Geneva ending, and NLF is annexed. There is
no "forcing the terminator" line. Saves that already have `Indochina_War_Over`
are not repaired.

## 2026-09-30 scoring of the 2026-09-29 run against checks 1-13

The 2026-09-29 run (`_local/logs/2026-09-29/`) carried the whole 2026-09-29
batch (first engine coverage of campaign `10`), so it is scored here against
checks 1-13. Evidence is telemetry from that run only. One run is not enough
to tune from.

| Check | Evidence | Verdict |
|---|---|---|
| 1 Struggle writers | 157 `SCORE_WRITE`. 1953-05..10 Communist net `+215`: writer 3 `+150` (70%), writer 4 `+50`, writer 12 `+25`, writer 11 `-10`. Whole run, writer 3 = `+1450` of `+2097` traced Communist. `SCORE_UNTRACED` totals: Communist 33, Pro-France 427, Pro-Independence 215, Pro-Ethnic 100; in the window only Pro-France 45. Margin `+298` (1954-04), `+238` (1954-10). | Attributed. Writer 3 (`indochina_struggle_vin_focus_standard`) dominates. Untraced Pro-France/Pro-Independence writes are not small over the whole run. |
| 2 Negotiations | `nlf_stand_down_ordered` 1954-09-18, `nlf_released` 1954-12-17, no `INVITE`. | Failed; root cause and fix already recorded above (check 14). |
| 3 Patience | `METROPOLE` 13-47 from 1950 to 1954-04, 8 on 1954-10-24; War Credits 260-435; `FRE_PATIENCE_SINK` x10. | Pass. |
| 4 Dien Bien Phu | `DBP_GARRISON tier=0` on both camp builds = the limited Castor drop, which still spawns the three-groupement floor. `DBP_POSTURE=standard`. Campaign `3` clean on day 45. | Pass. |
| 5 Launch garrisons | `LAUNCH_GARRISON` campaign 5 (3 divisions), 8 (4 divisions, tier 2). Vinh Yen costly day 28, Na San costly day 41. | Pass. Garrison removal after `RESULT` is not logged separately. |
| 6 VIE cap | VIE `cap=30` at war; divisions 27 (1951), 29-30 (1952-53); 18 against cap 20 at peace (1955). NLF alive with 13 divisions at the stand-down. | Pass. |
| 7 Defects | error.log: no `Kong Pathom`, no `Indochina_Flavor_Events` lines, no malformed Phase 2 template; no Lorraine cleanup log lines. Remaining `SIA_` errors are in `SIA_operations.txt`/`SIA_50s.txt` (unrelated noise). | Pass. |
| 8 Dak Doa gate | 10 `DAK_DOA_GATE` lines, 1954-03-11 to 1954-12-06: `prereq_focus=1 nlf=1 ful=1 fre=1 nlf_wider_war=1 nlf_holds_10180=0`, `available=0`. | **Open.** Dak Doa never launched because NLF never controls staging province `10180`; every other input of `VIN_dak_doa_available_trigger` passed. |
| 9 Nghia Lo province | Not observable in telemetry. | Needs a visual check. |
| 10 Campaign `10` | One `LAUNCH` (1952-01-18), one `RESULT` (clean, day 22), `LAUNCH_GARRISON campaign=10` (2 divisions), `NGHIA_LO_RELIEF`. `VIN_Liberate_Duyen` (Hoa Binh) launched 1952-04-22, after the cooldown. | Pass. |
| 11 Callbacks | VIN clean at Nghia Lo, so the FRE Na San bonus correctly did not apply. The Northwest `+25` Campaign Supply is not logged on the campaign `1` `LAUNCH` line. | Not covered; needs a supply field on the campaign `1` launch log. |
| 12 Hedgehogs | 0 `HEDGEHOG` lines; the historical AI took Castor. | Not covered (player-only path). |
| 13 Journal fit | Not observable in telemetry. | Needs a visual check. |

Lifecycle: 17 `RESULT`, 0 `IC_AFK|FAIL`.

### `VIN_50s.txt` unlocked-template warning (closed by user decision)

User decision 2026-09-30: `Trung doan Bo binh Infantry` is locked from now
on. `history/units/VIN_1949.txt` gains `is_locked = yes` on that template, so
`VIN_Formalize_Tieu`'s `add_units_to_division_template` (VIN_50s.txt:4950)
now targets a locked template. Players can no longer edit it; VIN gets the
template change only through the focus. Statically verified only:
`git diff --check`, and the file's existing BOM is unchanged (it predates this
change).

### Consolidated-playtest checks added

15. error.log has no `unlocked template (Trung doan Bo binh Infantry)` warning
    after `VIN_Formalize_Tieu`, and the template shows as locked in the VIN
    division designer.
16. Dak Doa: if `nlf_holds_10180=0` persists in another run, the staging
    requirement in `VIN_dak_doa_available_trigger` is the blocker to fix (AI
    allocation toward `10180` or a different staging contract); do not change
    it from this single run.

## 2026-09-30 content pass: Lai Chau, Bretagne/Adolphe/Camargue, Lower Laos, highlands ambushes, AFK coverage

Code-complete and statically verified only; no engine run. These are
first-pass values and are not tuned. User decisions on shape (2026-09-30):
Lai Chau is VIN limited campaign `11`; Bretagne/Adolphe/Camargue are numbered
FRE operations `5`/`6`/`7`; Lower Laos is an Atlante-linked diversion with no
war; Mang Yang and Chu Dreh are FRE ambush packages with no war. None of
these transfers territory, makes peace outside the existing owned-war
cleanup, or writes the Geneva recorder or the post-DBP latch. None declares
war on `LOS` or `CAM`.

### VIN campaign `11`: the move on Lai Chau

- Focus `VIN_Strike_Lai_Chau` (VIN_50s (47,11), after `VIN_Assault_Na_San`).
  Available after 1953-11-20 with Castor success or the hedgehog network,
  13765 French-aligned held, Tai Federation alive, Dien Bien Phu (campaign
  `3`) not started, the live window, no campaign running, and the cooldown
  ready.
- VIN must hold province `13765` for 5 days; deadlines 30/45 on both routes.
  Cooldown is 14 days. VIN declares on and owns the TAI war; the shared
  armistice cleans it up. The Struggle payout uses the shared writer `11`.
- CEFEO response is `FRE_Preparation.6` with a launch garrison at `13765` and
  an optional airborne relief. A VIN clean or costly result gives Dien Bien
  Phu +15 Campaign Supply at launch.
- Pollux coupling is `fre_pollux_lai_chau_offer`. On Lai Chau launch, an
  unlaunched Pollux whose prerequisites are met is offered at once through
  the existing `fre_pollux_focus_complete`. If VIN has already taken Lai
  Chau, the existing origin-lost result applies. The Pollux focus is bypassed
  once Pollux is launched. The Pollux lifecycle is otherwise unchanged.

### FRE operations `5`/`6`/`7`

All three use the shared resolver in `FRE_Operation_Effects.txt`. Focuses
are relative to `FRE_The_Situation_in_Route_Coloniale_4`.

| Op | Focus slot | Available | Objective (French-aligned hold) | Deadlines | Clean reward |
|---|---|---|---|---|---|
| 5 Bretagne | (-1,3) | 1952-11-15; Lorraine result or Na San prepared | `13753` and `1185`, 7 days | 30/45 | VIN -15 Campaign Supply |
| 6 Adolphe | (-4,3) | 1953-03-15; Na San terminal, `13757` held | `13754`, 5 days | 20/30 | VIN -10 Campaign Supply; `FRE_Adolphe_Sortie_Success` adds +1 preparation tier (cap unchanged) |
| 7 Camargue | (5,3) | 1953-07-01; Brochet or Hirondelle terminal | `4379` and `16445`, 7 days | 25/40 | State of Vietnam +0.03 stability and war support; Pro-Independence +10 (writer `17`) |

Camargue spawns 2 State of Vietnam divisions at `4379` on launch and removes
them at finish. The generic ledger is routed through writer `16`.

### Lower Laos diversion

- Focus `VIN_Lower_Laos_Offensive` (VIN_50s (18,10), no prerequisite).
  Available from 1953-12-15 once Atlante has launched, or from 1954-02-15 as
  a fallback.
- It is a 45-day VIN package that costs 20 Campaign Supply. While Atlante is
  active, it adds +4 to Atlante's hold gate and applies
  `FRE_Lower_Laos_Reserves_Diverted` (org -4%, supply consumption +6%,
  reinforce -4%).
- Result `contained` (VIN +10 supply) if any CEFEO division entered state
  `1796` or `1187` during the package. Otherwise `pressure`, which gives
  Communist +15 (writer `18`).

### Mang Yang and Chu Dreh

- New files: `FRE_Highlands_Effects.txt`, `FRE_Highlands_Triggers.txt` and
  `events/FRE_Highlands_Events.txt`. The tick runs from the existing FRE
  block of `on_daily_VIN`.
- **Mang Yang** opens after Dien Bien Phu is terminal, with 1954-07-01 as a
  fallback. CEFEO chooses a road column, an airlift (60 credits, -3 Patience)
  or holding An Khe, with `GM 100` at `16443`. A risk roll after 5 days is
  weighted by enemy control of `1328`/`16442` and the Dak Doa result.
  Outcomes: destroyed (Communist +20), mauled (+10), escaped (Pro-France +5),
  airlifted, or held. All use writer `19`.
- **Chu Dreh** opens on 1954-07-10, or 14 days after Mang Yang resolves.
  `GM 42` runs from Pleiku `16442` toward Ban Me Thuot `1605`. Outcomes:
  mauled, escaped or held, using writer `20`.
- Both packages are superseded, with no reward, when the window closes.

### AFK coverage added

- The campaign `1` LAUNCH line now carries `supply=` and `nghia_lo_bonus=`.
  The bonus also logs as `CALLBACK|campaign=1|source=Nghia_Lo`.
- New records:
  - `PREP_TIER` with every input flag.
  - `LAUNCH_GARRISON_REMOVED` with a PASS/FAIL check one tick later (template-presence test).
  - `POLLUX_STAGE` and `ATLANTE_STAGE` every 7 days, plus the terminal `reason=`.
  - `POLLUX_OFFER`.
- Writer routing keeps the same amounts:
  - `16` FRE limited-operation ledger
  - `22` Pollux
  - `23` Atlante
  - `24` Dien Bien Phu response
  - `25` Northwest/Lorraine response
  - `26` Geneva-preparations decision
  - `21` is reserved. The next free code is `27`.
- Opt-in hedgehog forcing. Run `effect ic_afk_force_hedgehog_enable = yes`
  in the console before about 1953-11. Castor then becomes unavailable to the
  AI, and the hedgehog `ai_will_do` rises to x1000. Default runs are
  unchanged.

### Static verification

- `git diff --check` is clean, braces balance in every changed `.txt`, no
  script file gained a BOM, and the four new `.yml` files have a BOM and only
  `§` beyond ASCII.
- Every new effect, trigger, idea, mission, event and loc key has one
  definition, and every new `= yes` call resolves. The two hedgehog console
  effects have no caller by design.
- An existing duplicate of `FRE_Ops.1.t/.d` in `FRE_events_l_english.yml`
  and `French_Indochina_l_english.yml` predates this pass and is unchanged.

### Open risks to watch

- Camargue and Bretagne objectives are already French-aligned at start, so a
  clean result may accrue without fighting (the Brochet precedent). Add a
  clearing condition if the run shows free clean results.
- AI CEFEO may ignore `front_control` on fronts without VIN units, which
  makes Lower Laos `contained` unreachable for the AI.
- `FRE_Preparation.6` and `FRE_Pollux.1` reach CEFEO within about a day of
  each other.
- The campaign and operation journal rows each gained a line; check that they
  still fit.
- Engine-unproven syntax: `delete_units` by template, `random` as a 0-1
  variable, `has_template` absence, and `create_unit` into another country's
  state.
- Every province id here comes from centroid computation; confirm names
  in-game.

### Consolidated-playtest checks added

17. Lai Chau: `LAUNCH|..|campaign=11|name=Lai_Chau|hold=0/5|deadline_clean=30|deadline_final=45`,
    `LAUNCH_GARRISON|..|campaign=11`, `POLLUX_OFFER|source=Lai_Chau|stage=..`,
    one `RESULT|..|campaign=11`, marker and armistice PASS lines, and
    `CALLBACK|campaign=3|source=Lai_Chau` after a VIN clean or costly result.
    Dien Bien Phu still launches when Lai Chau never runs.
18. FRE ops `5`/`6`/`7`: one `LAUNCH|owner=FRE|operation=N|name=<Name>` and
    one `RESULT` each; owned war cleaned; Camargue
    `LAUNCH_GARRISON|operation=7|owner=VIE|divisions=2`, removed at finish.
    Record the day of each clean result to test the free-result risk.
19. Lower Laos: `LAUNCH|owner=VIN|package=Lower_Laos|..|atlante_active=..`.
    If Atlante is active, `PASS|check=Lower_Laos_atlante_pressure_applied|hold_extension=4`.
    Then `RESULT|package=Lower_Laos|outcome=pressure|contained` and
    `PASS|check=Lower_Laos_idea_removed`.
20. Highlands: `LAUNCH|owner=FRE|package=Mang_Yang|choice=road`,
    `HIGHLANDS_ROLL`, `RESULT|package=Mang_Yang|outcome=..`, and the
    `Mang_Yang_active_cleanup`/`unit_cleanup` PASS lines. Chu Dreh follows
    the same pattern. No war, no Geneva write, and writers `19`/`20` only.
21. AFK coverage: campaign `1` LAUNCH `supply=`/`nghia_lo_bonus=` (closes
    check 11 when Nghia Lo succeeds), `PREP_TIER` per preparation,
    `LAUNCH_GARRISON_REMOVED` with no `campaign=0 removed=0`, and
    `POLLUX_STAGE`/`ATLANTE_STAGE` every 7 days. `SCORE_UNTRACED` drops
    sharply for Pro-France.
22. Forced hedgehog run (console opt-in): check 12 lines appear, Castor is
    never taken, and Lai Chau stays available as the fortified-base assault.

## 2026-10-01 review of the 2026-10-01 AFK run: negotiations end in regroupment

Logs preserved at `_local/logs/2026-10-01/`. Everything after 1958 is ignored
(the run was left going too long; NLF returns in later, unrelated content).

Telemetry: Dien Bien Phu clean on day 32 (1954-04-10). Negotiations were
chosen 1954-04-24 (`nlf_stand_down_ordered`). The stand-down released NLF on
1954-07-23, and the same day logged `focus_queue=consumed|peace_gate=passed`
and `GENEVA_SOURCE|INVITE`. Geneva concluded on 1954-10-06
(`END|result=scripted_Geneva_concluded`) and annexed NLF into VIE; NLF has no
`ARMY_CAP` line from 1954-10 to 1958. Check 14 passes: there is no
"forcing the terminator" line.

User finding: the negotiations focus seemed to do nothing, and NLF
white-peaced with VIE oddly. Cause: `VIN_Push_for_Negotiations` showed no
effect tooltip, and the stand-down ended in a bare `white_peace`. That left a
live NLF at peace, holding the south, for 2.5 months until Geneva annexed it.

User decision: the stand-down ends in regroupment. In
`vin_post_dbp_focus_geneva_queue_tick`, the white peace is replaced by the
new `vin_post_dbp_nlf_regroupment`:

- VIE white-peaces NLF, then annexes it with `transfer_troops = no`.
- VIN gains 20,000 manpower, plus 2 "Southern Regroupment Regiment" divisions
  (`Trung doan Bo binh Infantry`) at its capital if NLF still had divisions.
- It sets `VIN_Post_DBP_NLF_Regrouped` and `geneva_nlf_outcome_applied`, so
  Geneva does not score regroupment as a southern defeat.
- Events `VIN_South.10` (VIN) and `VIN_South.11` (VIE) report it.
- The focus gains the tooltip `VIN_Push_for_Negotiations_Regroupment_tt`.
  Loc is in `IC_Post_DBP_l_english.yml`.

The 90-day delay, the Geneva gate and the post-DBP latch are unchanged.
Statically verified only.

### Consolidated-playtest checks added

23. After negotiations: `nlf_released`, then
    `stage=nlf_regrouped|nlf_had_divisions=..|nlf_exists_after=0` the same
    day, then `INVITE`. NLF has no `ARMY_CAP` line afterwards, VIN gains 2
    regiments, both events show, and the Geneva NLF line is not "defeated".

## 2026-10-01 fix-up pass: contested sweeps, Bolovens response, regroupment fallback

Statically verified only; no engine run.

- **Bretagne (5) and Camargue (7) must be contested.** `fre_operation_update_contest`
  sets `FRE_Operation_Contested` the first day the enemy shows up:
  - Bretagne: Viet Minh divisions in state `786`, or Viet Minh control of `13753`/`1185`.
  - Camargue: Viet Minh or southern Viet Minh divisions in `1759`/`1758`, or their control of `4379`/`16445`.

  The hold counter resets on that day, and a clean or costly result needs the
  flag. A sweep that is never contested resolves `aborted` at the final
  deadline (`FRE_OP_UNCONTESTED`). New AI strategies
  `VIN_operation_bretagne_push` and `NLF_operation_camargue_contest` send the
  defenders in. Camargue counts the southern Viet Minh because the Viet Minh
  are not at war with the State of Vietnam.
- **Lower Laos response.** At launch CEFEO gets `FRE_Lower_Laos.1`:
  - Fly in an airborne group: 40 War Credits. It spawns "Groupement Aeroporte Bolovens" in state `1187` at `1563` and adds +3 days to Atlante's hold gate if Atlante is active. This makes the result `contained`.
  - Leave it to the Royal Lao Army.

  AI chance is 60/40. The unit is deleted when the package ends or CEFEO
  dissolves.
- **Regroupment fallback.** After the stand-down, regroupment now also runs
  when the southern Viet Minh are already at peace with the State of Vietnam
  (`reason=already_at_peace`). The white peace is only issued if they are at
  war.

### Consolidated-playtest checks added

24. Ops 5/7: `FRE_OP_CONTESTED` before any clean/costly `RESULT`, or
    `FRE_OP_UNCONTESTED` followed by `outcome=aborted`. No clean result
    within 7 days of launch without a contest line.
25. Lower Laos: `LOWER_LAOS_RESPONSE|choice=..`. With `reinforce`, the unit
    appears near Paksong, the result is `contained`, and the unit is gone
    after `RESULT`.
26. Regroupment: `nlf_regrouped` appears even if `reason=already_at_peace`.

## 2026-10-01 content pass: remaining unbuilt design list

Code-complete and statically verified only; no engine run. These are
first-pass values and are not tuned. The lead fixed one engine-invalid
equipment type (`anti_air_equipment_1` became `auto_cannon_equipment_1`).
Struggle writers 27 (Luang Prabang), 30 (Chanson) and 31 (associated armies)
are used; 28 and 29 are reserved and unused.

### Severe overextension tier and VIN Luang Prabang all-in

- `VIN_Campaign_Overextension_Severe` replaces the ordinary tier and never
  stacks with it. Values: -70% attack, -45% defense, -55% org, -45% speed,
  -60% planning, +110% supply consumption, +90% out-of-supply, -20%
  reinforce, +45% attrition.
  - It applies while a campaign runs and VIN holds Vientiane-state ground, or
    the delta core (4075, 4119) outside campaigns 5-7.
  - It clears on withdrawal and in common cleanup.
  - Approved deviation: the ordinary tier already equals the CEFEO severe
    package, so this tier is stronger than both.
- `VIN_All_In_Luang_Prabang` is an alternative to the historical Pathet Lao
  raid event.
  - It launches the same raid with 3 extra Pathet Lao divisions, extra
    equipment, a deadline 30 days longer, Luang Prabang-first AI and -40
    Campaign Supply.
  - Severe applies only when VIN itself holds ground beyond Luang Prabang. The
    raid's own overextension modifier is suspended while severe applies.
  - Success: Communist +40, and Lai Chau and Dien Bien Phu each get +10
    supply at launch.
  - Failure: VIN -50 Campaign Supply, and CEFEO gets Castor -15 on both
    prices.
  - Raid ownership and the two-capitals conquest rule are unchanged. The
    historical AI never takes the focus. The Laos raid missions disappear
    from the UI at day 90 of the longer raid; this is cosmetic.

### Section 9.1: VIN army focuses as campaign inputs

`vin_campaign_apply_command_inputs` runs once per launch, after deadline
initialisation in `vin_campaign_declare_war`. A per-launch flag guards it.
Seven army and command focuses set `VIN_Cmd_Input_*` flags with tooltips
instead of their duplicated flat bonuses. Totals are clamped to +30 supply
and +7 clean days, and campaign 9 is skipped. `VIN_improve_drv_army` lost its
out-of-supply, speed, max-planning and planning-speed bonuses. Empty leading
`completion_reward` blocks were removed. Log: `IC_AFK|CAMPAIGN_INPUTS`.

### Chinese versus Soviet patronage

`VIN_Chinese_Patronage` (historical) and `VIN_Soviet_Patronage` are mutually
exclusive and available from 1950.

| | Chinese | Soviet |
|---|---|---|
| Campaign supply per launch | +15 | +5 |
| Deliveries | Rifles and support equipment, monthly | Artillery and anti-air guns, monthly |
| Other | | Quality idea, PP, doctrine and artillery research bonuses |
| Geneva communist leverage (once) | +25 | +40 |

### Charles Chanson and Sa Dec

The existing `FRE_Charles_Chanson` is used. A dated roll on 1951-07-31 kills
him 85% of the time.
- Death: -3 Patience, and Dak Doa gets +10 supply.
- Survival: opens `FRE_Chanson_Pacification` and makes Camargue cheaper
  (30/60/100) with a 6-day hold.

`VIE_Historical.10` now reads the roll.

### Royal Lao and Cambodian armies

`FRE_Associated_State_Armies` is mutually exclusive with
`FRE_Arm_the_National_Army` and is player-only.
- It costs 60 War Credits. Royal Laos and Cambodia each get 2 divisions,
  manpower and equipment, and the State of Vietnam's wartime cap drops from
  30 to 25.
- Lower Laos resolves `contained`. The raid capitals get bunker level 4.
- Geneva gets +30 ethnic leverage, and Pro-France +10.
- There are no wars, transfers or faction changes involving Laos or
  Cambodia.

### Legacy adjacency deletion

The 12 unassigned northern rules and the base `INDOCHINESE_WAR` rule were
deleted from `map/adjacency_rules.txt`, together with 3 flag or rule loc
keys. Kept, because they are still assigned in the CSV: `LAOS_VINH`, `LAOS`,
`DIVIDE` and `DIVIDE_SWF`. No movement change is expected.

### Engine-unproven syntax to watch

- `create_unit` inside `random_owned_controlled_state`.
- `has_template`.
- `num_divisions` in `set_variable`.
- `set_building_level` at level 4.
- The `Kong Phan`/`Kong Pathom` templates for extra Pathet Lao divisions.

### Consolidated-playtest checks added

27. Severe tier: `OVEREXTENSION|tier=severe|state=apply|clear` only with a
    real cause. No `LP_all_in_severe_tier_has_cause` or
    `raid_modifier_suspended_under_severe` FAIL.
28. All-in (player or non-historical AI): `LAUNCH`, `STAGE` and `RESULT`
    lines, then `CALLBACK|package=Castor|source=Luang_Prabang` on failure or
    the campaign supply callbacks on success.
29. `CAMPAIGN_INPUTS` on every launch, with values within the clamps. No
    double application after a re-declare.
30. `PATRONAGE|choice=chinese` for the historical AI, monthly
    `PATRONAGE_DELIVERY` lines, and `PASS|check=Patronage_exclusive`.
31. `CHANSON|outcome=..|roll=..` near 1951-07-31. On survival, the
    pacification focus appears and Camargue prices are 30/60/100.
32. Associated armies (player FRE): `ASSOCIATED_ARMIES|choice=associated`,
    the divisions spawn, the VIE cap is 25, and Lower Laos is `contained`.
33. Map: no adjacency errors in error.log, and northern movement as before.

## 2026-10-02 AFK run review: Viet Minh capitulates during Cao-Bac

Logs in `_local/logs/2026-10-02/` (run ends 1950-11-08). Evidence is
telemetry and error.log only; the autosave is binary and was not decoded.

### What happened

1. 1949-05 to 1950-10 matched the 2026-10-01 run: VIN 26-28 divisions at
   peace, FRE 17, VIE growing to 24. Struggle at 1950-05: pro-France 215,
   pro-independence 215. FRE was richer than last run (Patience 71, War
   Credits 600, against 21/340).
2. 1950-10-18: Cao-Bac launched normally (`LAUNCH`, THO garrison PASSes,
   `CAMPAIGN_INPUTS` supply +8, clean days +2).
3. 1950-10-22, day 4: VIN took the ordinary `VIN_Campaign_Overextension`
   tier (-60% attack, -35% defence, -45% organisation, +35% attrition for
   the whole army). The AFK line reads `status=severe_penalty_applied`, but
   it is logged from the ordinary idea; the severe tier (`OVEREXTENSION|
   tier=severe`) never fired. None of the three earlier runs took any
   penalty during Cao-Bac. Which foreign ground tripped it was not logged.
4. 1950-11-08, day 21: VIN and MEO lost the war to FRE and THO. Three
   failsafe calls ran in one tick; the first two (the capitulation hooks)
   found nothing decisive, the third
   (`on_before_peace_conference_start`) did, and the vanilla conference
   logged `later_theatre_peace_conference_after_scripted_end` for
   FRE/THO over VIN/MEO. VIN had 28 divisions on 1950-10-14, so it was a
   capitulation, not destruction. No Cao-Bac `RESULT` was ever written.
5. The router took `indochina_struggle_southern_victory` (confirmed by its
   line-817 `unplanned_offensive` error and the resistance-target 124
   errors in every northern state). That ending transfers the northern
   states, annexes VIN, NLF, FRE and the crown domains into VIE, moves the
   capital to Saigon, and calls `drop_cosmetic_tag = yes`
   (`CWIC_Struggle_Effects.txt:722`). The unification and the lost
   cosmetic tag are that ending working as written, not a separate bug.

### Verdict

- The failsafe and ending behaved as designed once VIN capitulated.
- The defect is upstream: an AI Viet Minh capitulating 21 days into
  Cao-Bac. The leading cause is the army-wide overextension penalty landing
  on day 4 with a better-funded CEFEO counter-attacking; this is
  `[INFERENCE]`, because neither the cause bits nor surrender state were
  logged. Ruled out: the legacy adjacency deletion (the deleted rules were
  referenced by no `adjacencies.csv` row and error.log has no adjacency
  errors), the CAMPAIGN_INPUTS log string (properly terminated), VIE
  joining the war (it is not in the conference pairs).
- No behaviour change was made: whether a limited-campaign capitulation
  should end the war needs evidence first and is a design decision.

### Patch (statically verified only)

- `ic_afk_validation_vin_envelope_cause`: on the first ordinary-tier
  application, logs `ENVELOPE_CAUSE|bits=..` (1 Cao-Bac, 2 Nung, 4 Ha
  Giang, 8 Northwest corridor, 16 Northwest outlier, 32 Hoa Binh, 64 Dien
  Bien, 128 Delta, 256 CEFEO operation). Generic ground triggers, so read
  the bits against the campaign number.
- `ic_afk_validation_capitulation` on `on_capitulation_immediate`: logs
  `CAPITULATION|tag|winner|divisions|owned_controlled_states|capital_held|
  overextended|vin_campaign` for any theatre tag. Not gated on
  `Indochina_War_Over`, because merged on_action order is not guaranteed.
- `IC_VIN_Patronage.txt`: `anti_air_equipment` is not an equipment-bonus
  type (error.log, rework-local); now `anti_air`, as in `z_mechanics.txt`.

### error.log classification

- Rework-local: the Patronage enum error (fixed); line-817
  `remove_dynamic_modifier unplanned_offensive` in the southern-victory
  ending (pre-existing, harmless).
- Adjacent Indochina/SEA: `VIE_50s_Military.txt:49-65` `create_unit`
  parse failures (5 Nam-Viet Militia without a template),
  `VIE_Events.txt:7013` invalid `controller` target, resistance target
  124 added twice by the ending.
- Unrelated noise: entity/texture, NORDIC dynamic modifiers, SWE events,
  Indonesia, raid modifiers.

### Consolidated-playtest checks added

34. Every `ENVELOPE|..|status=severe_penalty_applied` is followed by one
    `ENVELOPE_CAUSE` line with non-zero bits. Bits 0 means the penalty came
    from a path the logger does not cover.
35. No `CAPITULATION|tag=VIN` before Geneva. If one appears, record
    `capital_held`, `overextended` and the preceding `ENVELOPE_CAUSE`.
36. No `script_enum_equipment_bonus_type` error for `IC_VIN_Patronage.txt`.

Partial scoring from this run: 29 passed for the single launch; 33 passed
(no adjacency errors); the rest were not reached before the run ended.

## 2026-10-02 second AFK run: full arc to Geneva

Logs in `_local/logs/2026-10-02b/` (1949-05 to 1955-07). One manual
intervention: the user helped the PRC win the Chinese Civil War early.
Telemetry and error.log only.

### Accepted

- Full VIN arc: Cao-Bac clean (day 23), Vinh Yen failure, Mao Khe costly,
  Day River failure, Nghia Lo costly, Hoa Binh clean (day 105), Northwest
  clean (day 45, Nghia Lo callback +25), Na San failure, Dien Bien Phu clean
  (day 37; was day 24 in 2026-09).
- FRE operations: Bretagne and Adolphe clean, Brochet clean, Hirondelle and
  Mouette failure, Castor failure, Atlante stalled, Camargue aborted, Mang
  Yang and Chu Dreh escaped, Pathet Lao raid stalemate.
- Post-DBP negotiations: gate blocked while VIN/VIE at war, NLF stand-down
  ordered 1954-04-27, regroupment 1954-08-17 (check 23 passes), gate
  passed, scripted Geneva concluded 1954-10-12. Final margin +252.
- Check 34: every `ENVELOPE` has an `ENVELOPE_CAUSE` with non-zero bits.
  Check 35: no VIN capitulation; the only `CAPITULATION` is CCC to VIE in
  1955, after the war. Check 36: no Patronage enum error. No `IC_AFK|FAIL`
  lines in the whole run. Check 30: `PATRONAGE|choice=chinese` 1951-10-17.
  Check 31: `CHANSON|outcome=killed`. Check 33: no adjacency errors.

### Defects found and fixed (statically verified only)

1. **The overextension penalty landed on almost every launch.** 8 of 10 VIN
   launches took the ordinary tier 2-3 days in, almost always for Delta
   ground (bit 128; Vinh Yen 136). On Hoa Binh, Northwest, Mao Khe and Day
   River it lasted the whole campaign. Border units walk into the delta on
   declaration despite the -600 unit requests. This is the same mechanism
   behind the 1950 capitulation. User decision: grace period.
   `vin_campaign_update_overextension` now counts
   `VIN_Overextension_Streak_Days` and applies the ordinary tier only after
   5 consecutive days of off-envelope ground; leaving it resets the count
   and clears the idea. The streak resets at launch. The severe tier and
   the CEFEO-operation path stay immediate. `ENVELOPE_CAUSE` now logs
   `streak_days`; the console test checks the grace both ways.
2. **The Bolovens airlift never spawned.** CEFEO paid 40 War Credits on
   1954-02-26 but `create_unit` failed (`VIN_Lower_Laos_Effects.txt:31`:
   FRE not at war with controller LOS), so `contained` stayed unreachable.
   User decision: the group is raised as a Royal Lao (`LOS`) division in
   Champasak (template flag `LOS_Bolovens_Template_Loaded`, cleaned up on
   `LOS`). If LOS does not control Champasak, nothing spawns and the 40
   credits are refunded. The tooltip says so. No war or access deal with
   Laos.
3. **Command-input clamps did nothing.** `clamp_variable` was used on temp
   variables, so supply reached +32 (cap 30) from 1951-11. Now
   `clamp_temp_variable`. Check 29 failed on this run.

### Not changed, watch next run

- Campaign supply reached 370 by 1954. Partly the unclamped inputs and the
  Chinese patronage, which the early PRC victory may have brought forward.
- Metropole Patience fell to 5 at one point (IC_RESPONSE) and ended near 29.
- error.log, adjacent: VIE `Batallion Vietnamien` malformed token and
  `VIE_50s_Bao_Dai.txt:204` create_unit, `add_compliance` on states without
  resistance (`VIE_50s_Bao_Dai.txt:5491`), `VIE_Events.txt:7013` invalid
  `controller`. Rework-local leftover: `VIN_Lower_Laos_Effects.txt:8`
  delete_units on a missing template, fixed by the LOS-flag guard.

### Consolidated-playtest checks added

37. No `ENVELOPE|..|status=severe_penalty_applied` with
    `ENVELOPE_CAUSE|..|streak_days` below 5. Expect far fewer penalties;
    any that apply should last more than a few days.
38. If CEFEO picks the Bolovens airlift: no create_unit error, a Royal Lao
    `Groupement Aeroporte Bolovens` in Champasak, and Lower Laos can resolve
    `contained`. Or a `spawn=skipped` line with a 40-credit refund.
39. Every `CAMPAIGN_INPUTS` line has `supply` at most +30 and
    `clean_days` at most +7.

## 2026-10-02 third AFK run: grace period live

Logs in `_local/logs/2026-10-02c/` (1949-05 to 1967; the Indochina War
ends 1954-06-17). The early PRC victory again came from the user's manual
help. Telemetry and error.log only.

### Accepted

- Cao-Bac launched 1949-12-20, ten months early. This is intended:
  `VIN_Operation_Cao-Bac` is available on `date > 1950.09.01` OR
  `PRC_Victory`. Clean on day 18.
- Campaign results: Vinh Yen costly, Mao Khe and Day River failure, Nghia
  Lo costly, Hoa Binh clean (day 105), Northwest costly (day 149; TAI
  capitulated to VIN the same day, which triggered the full armistice),
  Na San failure, Dien Bien Phu clean on day 22.
- CEFEO: Bretagne, Hirondelle and Brochet clean, Mouette failure, Castor
  success (Brochet and Na San discounts), Pollux superseded by the Dien
  Bien Phu launch.
- Post-DBP negotiations: gate passed the same day; scripted Geneva concluded
  1954-06-16. Final margin +135. No `IC_AFK|FAIL` lines.
- Check 37 passes: every `ENVELOPE_CAUSE` has `streak_days=5`. Check 39
  passes: supply at most +30 and clean days at most +2. Check 38 is
  partial: no create_unit error after the Royal Lao airlift, but there was
  no success log line, and Lower Laos was superseded on day 14.
- error.log: 725k lines of vanilla `Raid City` modifier spam (unrelated; the
  run went to 1967). No rework-local errors. The adjacent VIE errors are
  unchanged (`Batallion Vietnamien`, `VIE_50s_Military.txt:867`
  create_unit, resistance/compliance on states with no resistance).

### Findings

1. **The grace period stops short grabs, not sustained holds.** Penalty
   lengths: Cao-Bac 5 days, Vinh Yen 18, Nghia Lo 22, Mao Khe 31, Day River
   46, Hoa Binh 98, Northwest 127. Every cause is Delta ground except Vinh
   Yen (Northwest corridor) and Cao-Bac (Cao-Bac plus Delta). VIN holds
   delta provinces for whole campaigns. Not changed; the delta-province
   detail is now logged (see below) before choosing a fix.
2. **The severe tier ran through all of Na San** (1953-04-10 to 05-27). It
   applied on the launch day while the Pathet Lao raid was live. Cause not
   logged; Luang Prabang ground is the likely cause (`[INFERENCE]`).
   Design deviation: the Section 17 entry says severe applies for
   Vientiane-state ground during campaigns, but
   `vin_controls_foreign_upper_laos_deep_trigger` also counts Luang Prabang
   state `1198` whenever the all-in is not active. That includes the
   historical raid's own capital objective. Not changed: needs a decision.
3. **The southern Viet Minh capitulated to the State of Vietnam on
   1953-05-13** with 12 divisions and its capital held, 17 months before
   Geneva. This is the old southern-collapse balance item, now earlier.
   Not changed.
4. **The Bolovens group would not have counted toward `contained`.**
   `vin_lower_laos_fre_garrison_present_trigger` is evaluated in FRE scope,
   and `divisions_in_state` counts only the scope country's divisions
   (`[INFERENCE]` from engine semantics). So the Royal Lao group from the
   last patch could never contain the diversion.

### Patch (statically verified only)

- `vin_lower_laos_fre_garrison_present_trigger`: new branch. If FRE has
  `FRE_Lower_Laos_Reinforced`, Royal Lao divisions in Champasak (1187)
  count as the garrison.
- `fre_lower_laos_reinforce_bolovens` logs `LOWER_LAOS_RESPONSE|..|
  spawn=royal_lao|champasak_divisions_present=..` after the spawn.
- `ENVELOPE_CAUSE` adds `delta_provinces` bits: 1 Hanoi 4075, 2 1185,
  4 Haiphong 4119, 8 13753, 16 13755, 32 13756, 64 13770, 128 13772.
- New `ic_afk_validation_vin_severe_cause`, called from
  `vin_overextension_severe_apply`, logs `SEVERE_CAUSE|bits|raid`: 1 Luang
  Prabang state, 2 Vientiane state, 4 delta core, 8 all-in corridor.

### Consolidated-playtest checks added

40. Every `OVEREXTENSION|tier=severe|state=apply` is followed by a
    `SEVERE_CAUSE` line. If bit 1 is set with `raid=1`, finding 2 is
    confirmed.
41. `ENVELOPE_CAUSE|..|delta_provinces` names the same few provinces across
    campaigns. That points to a targeted envelope or AI fix rather than a
    global one.
42. After the Bolovens airlift, `champasak_divisions_present=1`, and Lower
    Laos can end `contained` if it is not superseded.

## 2026-10-02 fourth AFK run: evidence for the three open decisions

Logs in `_local/logs/2026-10-02d/` (war ends 1954-06-20). Run only to
gather evidence; no balance change was made. Telemetry and error.log only.

### Arc

- Campaign results: Cao-Bac clean (day 28), Vinh Yen clean (day 19), Mao
  Khe and Day River failure, Nghia Lo costly, Hoa Binh clean (day 105),
  Northwest clean (day 35; MEO capitulated to FRE on 1952-11-17), Na San
  costly, Dien Bien Phu clean on day 21.
- CEFEO: Bretagne aborted, Adolphe, Brochet and Hirondelle clean, Mouette
  failure, Castor failure. Camargue (tier 0) was superseded by the Dien Bien
  Phu launch. Lower Laos: CEFEO chose `ignore`; superseded on day 13.
- Geneva concluded 1954-06-19. Final margin +374, above the +135 seen in
  the two runs before.
- error.log: no rework-local errors.

### Decision 1: Delta holds

`delta_provinces` per launch: Cao-Bac 66, Vinh Yen 64, Mao Khe 66, Day
River 66, Nghia Lo 64, Hoa Binh 82, Northwest 64, Na San 0 (its cause was
Dien Bien ground). Province `13770` is held in 7 of 8 launches; `1185` in 4;
`13755` once. Both `13770` and `1185` are bunker-3 provinces at the delta
edge (`history/states/786`). `13770` is no campaign's objective; `1185` is
one of Day River's three. Penalty length against campaign length: 19/28,
10/19, 29/38, 29/53, 28/39, 98/105, 20/35, 32/42. So the ordinary tier is
on for most of every campaign, and nearly all of it comes from one
province.

### Decision 2: Severe tier during the Laos raid

No severe tier this run: the raid (1953-03-31 to 06-28) ran with no
campaign live. Still unconfirmed in play. The code path is certain:
`vin_controls_foreign_upper_laos_deep_trigger` counts Luang Prabang state
`1198` whenever a campaign runs and the all-in is not active.

### Decision 3: Southern Viet Minh collapse

NLF capitulated on 1953-01-02 with 6 divisions, its one state and its
capital. `ARMY_CAP` shows the cause: NLF divisions fall 14, 13, 12, 10, 9,
8, 7 from 1949-06 to 1952-12 and never recover, while its manpower climbs
from 210k to 353k unused. Meanwhile VIE grows from 7 to 31 divisions. NLF
has one state, no industry (`gdp=1`), and no equipment or division inflow
before the post-DBP `NLF_Northern_Supply_Line`. It cannot replace losses,
so it bleeds out against an army that keeps growing.

### Fixed (statically verified only)

- `IC_AFK|FAIL|check=FRE_limited_operation_full_cleanup|
  remaining_operation_wars=2` at 1954-02-19 was a false positive. Dien Bien
  Phu superseded Camargue and declared its own war in the same tick. Both
  copies of the check (`ic_afk_validation_fre_limited_tick` and
  `ic_afk_validation_fre_new_operations_tick`) now log PASS with
  `vin_campaign_wars=..` when FRE no longer owns the war and a VIN campaign
  is running.

### Consolidated-playtest checks added

43. A CEFEO operation superseded by a VIN campaign logs
    `PASS|check=FRE_limited_operation_full_cleanup|..|vin_campaign_wars=`,
    never the FAIL.

## 2026-10-02 patch: the three decisions

User decisions, taken on the fourth-run evidence. Statically verified only.

### 1. Delta edge provinces exempt

`vin_controls_foreign_delta_ground_trigger` no longer lists `1185` or
`13770`, the bunker-3 delta edge provinces. It is the generic delta rule
used by the VIN campaign envelope outside the delta campaigns, and by the
CEFEO operation 2/3 path. The Mao Khe, Day River and Brochet variants keep
their own lists, so those three still count both provinces. Hanoi `4075`
and the rest of the delta still count. The `ENVELOPE_CAUSE` bit 128 now
follows the narrowed rule; `delta_provinces` still reports raw control.

### 2. Severe tier follows the Section 17 text

`vin_controls_foreign_upper_laos_deep_trigger` is renamed
`vin_controls_foreign_vientiane_ground_trigger` and keeps only Vientiane
state `670`. Luang Prabang state `1198` no longer causes the severe tier,
so the historical raid's own objective is never penalised. The all-in
keeps its separate corridor rule. `SEVERE_CAUSE` bit 1 is now
informational.

### 3. Northern resupply for the southern Viet Minh

New `vin_nlf_northern_resupply_monthly`, run from
`vin_accrue_monthly_supply` (VIN scope, about monthly).

- Conditions: from 1950-01-01, the war and Geneva not over, no post-DBP
  stand-down ordered, NLF exists and is at war, NLF does not have
  `NLF_Northern_Supply_Line`, and VIN has at least 50 Campaign Supply.
- Effect: NLF gets 300 `infantry_equipment_1` for 5 Campaign Supply. Below
  10 divisions, and if NLF controls its capital, it also gets one `Trung
  Doan Bo Binh Infantry` regiment there (experience 0.3, equipment 0.8) for
  10 more.
- Log: `IC_AFK|NLF_RESUPPLY|rifles|regiment|nlf_divisions|vin_supply`.
- The values are first-pass and untuned. At most 15 Campaign Supply a month,
  against a monthly income of 30-40 with PRC victory.

### Consolidated-playtest checks added

44. `ENVELOPE_CAUSE` with bit 128 never has `delta_provinces` of only 2,
    64 or 66 (edge provinces alone). Penalty days per campaign drop well
    below the 2026-10-02d lengths.
45. A severe tier during the Laos raid shows `SEVERE_CAUSE` bit 2, 4 or 8,
    never bit 1 alone.
46. Monthly `NLF_RESUPPLY` from 1950. NLF divisions hold near 10 instead of
    falling to 6. No NLF capitulation before Geneva. VIN Campaign Supply
    still funds every launch (`supply` on Northwest and Dien Bien Phu
    launches comparable to 2026-10-02d).
47. Watch balance: Dien Bien Phu duration (21-22 days in the last two runs),
    the final margin, and whether a stronger south delays the negotiations
    gate.

## 2026-10-03 AFK run review: second Viet Minh capitulation during Cao-Bac

Logs in `_local/logs/2026-10-03/` (run ends 1950-11-11). Only the local mod
was enabled (`dlc_load.json`), so the uncommitted 2026-10-02 patches were
loaded. Evidence is telemetry and error.log only.

### What happened

1. Cao-Bac launched 1950-10-18 (no PRC victory yet), as in the 2026-10-02
   first run. THO garrison and command-input PASSes.
2. 1950-10-26, day 8: ordinary overextension tier after the 5-day streak.
   `ENVELOPE_CAUSE|bits=129|delta_provinces=128` (Cao-Bac ground plus
   province `13772`, not one of the excluded edge provinces). Cleared
   1950-10-31 after 5 days.
3. 1950-11-11, day 24: `CAPITULATION|tag=VIN|winner=FRE|divisions=28|
   owned_controlled_states=3|capital_held=1|overextended=0|vin_campaign=4`.
   No Cao-Bac `RESULT`. The failsafe took the decisive route; FRE and THO
   beat VIN and MEO; the struggle ending annexed the north into the State
   of Vietnam (same `CWIC_Struggle_Effects.txt:817` and resistance-124
   signature as 2026-10-02).
4. No `NLF_RESUPPLY` line in the whole run (1950-01 to 1950-11), although
   NLF was at war with 14 divisions. Check 46 fails; cause not traced.

### Verdict

- The overextension inference of 2026-10-02 is refuted. The 2026-10-02d run
  took the identical penalty (same day, bits 129) for 19 days and did not
  capitulate; this run cleared it 11 days before the surrender and still
  capitulated. The penalty is not the proximate cause.
- VIN capitulated by surrender progress with its army intact and its
  capital held. VIN has no `surrender_limit` protection during campaigns,
  while CEFEO has `FRE_Highland_Overextension` (`surrender_limit = 1.0`)
  and the Royal Lao have the raid idea. Which victory points VIN lost is
  not logged `[INFERENCE: few owned states make a small VP base]`.
- 2 of 5 recent AFK runs end this way, both with the 1950-10-18 launch.
- No behaviour change: protecting VIN from capitulation is a design
  decision.

### Consolidated-playtest checks added

48. Before any fix, log weekly during a VIN campaign: VIN surrender
    progress, and the controller of each VIN victory-point province.
49. `NLF_RESUPPLY` appears monthly from 1950-02; if not, log which gate of
    `vin_nlf_northern_resupply_monthly` fails.

## 2026-10-03 patch: surrender and resupply telemetry

Statically verified only (brace balance, single definitions, `git diff
--check`). No behaviour change. Working hypothesis (user): VIN loses too
many victory points from a small base and surrenders.

- `ic_afk_validation_vin_surrender_tick` (VIN, from the FRA daily tick):
  while VIN is at war with FRE, logs `IC_AFK|SURRENDER|reason|campaign|
  surrender_pct|vp_owned|vp_lost|capital_held|states|divisions` on the first
  war day, on any change of bucket or lost ground (reason 1), and weekly
  (reason 2). `ic_afk_validation_capitulation` adds a reason-3 line when VIN
  capitulates. `surrender_pct` is engine surrender progress floored to 5.
- VP bits (province, state, value): 1 7015 881 5, 2 11936 1762 3, 4 4397
  1763 5, 8 12297 838 1, 16 17194 1875 1, 32 17193 1875 1, 64 12065 1280 10,
  128 13767 1280 1, 256 13765 671 6, 512 4529 671 5, 1024 10129 1766 5,
  2048 7093 1281 5, 4096 4075 1760 20, 8192 4119 786 10. `vp_owned`: VIN
  owns the state; `vp_lost`: VIN owns the state but not the province.
  Values are history values; runtime objective VPs are not included.
- `vin_nlf_northern_resupply_monthly` now calls
  `ic_afk_validation_nlf_resupply_skip` when it does not run (from 1950,
  war not over): `NLF_RESUPPLY_SKIP|gates|vin_supply`, bits 1 Geneva
  concluded, 2 stand-down ordered, 4 NLF missing, 8 NLF not at war, 16 NLF
  has the post-DBP supply line, 32 Campaign Supply below 50.

Checks 48 and 49 now read:

48. Every VIN war with CEFEO produces `SURRENDER` lines; a VIN
    `CAPITULATION` is followed by a reason-3 `SURRENDER` line. Read which
    `vp_lost` bits rise with `surrender_pct` before the surrender.
49. Each month from 1950-02 has exactly one `NLF_RESUPPLY` or
    `NLF_RESUPPLY_SKIP` line. Neither line means the monthly accrual never
    reached the resupply.

## 2026-10-03 second AFK run: historical arc, surrender telemetry live

Logs in `_local/logs/2026-10-03b/`. No VIN capitulation; no `IC_AFK|FAIL`.
Cao-Bac clean (day 28), Vinh Yen, Mao Khe and Day River failure, Nghia Lo
clean, Hoa Binh clean (day 105), Northwest clean (day 85), Na San clean,
Pathet Lao raid stalemate, Dien Bien Phu clean on day 35, Geneva concluded
1954-07-08 with a final margin of +343.

### Check 48: surrender progress confirms the victory-point hypothesis

| Campaign | Lost (`vp_lost`) | Peak `surrender_pct` |
|---|---|---|
| Cao-Bac | 2 (Thanh Hoa 11936) | 40 |
| Vinh Yen | 2 | 20 |
| Na San | 2 | 25 |
| Northwest | 3 (Thanh Hoa and Dong Bac Bo 7015) | 75 |
| Dien Bien Phu | 3 | 75 |

Losing Thanh Hoa alone puts VIN at 20-40% in two days; adding Dong Bac Bo
puts it at 70-75%. VIN's surrender base is a handful of victory points, so
one or two CEFEO counter-thrusts decide capitulation. This fits both
2026-10-02/03 capitulations. The exact engine weighting is not derived;
the percentages exceed the history VP share, so other ground or runtime
VPs also count `[INFERENCE]`. Needs a design decision (campaign-window
`surrender_limit`, VP rebalancing, or Thanh Hoa/Viet Bac defence).

### Check 49: resupply mostly silent

One `NLF_RESUPPLY` (1951-08-10, regiment, NLF 7 divisions) and one
`NLF_RESUPPLY_SKIP` (1954-01-02, gates 4: NLF gone). Every other month had
neither line, so the monthly accrual rarely reached the resupply although
Campaign Supply kept rising (163 to 353). NLF capitulated to VIE on
1952-09-04 with 0 divisions. Check 46 fails again. Not traced.

### Geneva Laos clause (user note, not addressed)

The AI conference picks `GENEVA_CONF_C5_OPT_1` "Independent and Neutral
Laos and Cambodia", which removes the Pathet Lao even after a partial or
historical raid victory. `GENEVA_CONF_C5_OPT_2` "Communist Regroupment
Zones" covers that case but its wording reads as a Pathet Lao withdrawal,
which a Pathet Lao holding ground would not accept. Open design item: tie
the Laos outcome to the raid result and reword the regroupment option.

## 2026-10-03 patch: VIN surrender limit, surrender-core defence, accrual trace

Statically verified only (brace balance, BOM and ASCII on the changed
`.yml`, single strategy definition, `git diff --check`).

- `VIN_Resistance_War_Economy` gains `surrender_limit = 0.5`. The idea is
  in VIN's 1949 history and removed only by the war-end cleanup in
  `CWIC_Struggle_Effects.txt`, so it covers the whole war. Description
  updated. Value is first-pass.
- New AI strategy `VIN_hold_surrender_core` (`indochina_communist.txt`),
  enabled in any war with FRE: theatre demand +6 and front unit request
  60/80 for Dong Bac Bo (881) and Thanh Hoa (1762). It stacks with the
  campaign all-in requests.
- Resupply trace. In 2026-10-03b the resupply, the patronage delivery and
  the skip line all appeared only on 1951-08-10 and 1954-01-02 (both at
  18:00), 876 days apart, about 28 times 31 days. The accrual counter
  needs 28 increments and assumes `ic_pulse` is daily. If `ic_pulse` runs
  for VIN about monthly (the `ic_pulse_one` mission cycle), the monthly
  accrual, the patronage delivery and the resupply all run once every
  2-3 years `[INFERENCE]`. New lines: `IC_AFK|VIN_PULSE|counter|supply` on
  every VIN pulse (`IC_scripted_effects.txt`) and `IC_AFK|VIN_ACCRUAL|
  amount|supply` on every accrual. Not fixed: the accrual feeds Campaign
  Supply, so a real monthly cadence would change VIN's economy.

### Consolidated-playtest checks added

50. No VIN `CAPITULATION` before Geneva. `SURRENDER` peaks stay well below
    the 2026-10-03b values (40 in Cao-Bac, 75 in Northwest and Dien Bien
    Phu) for the same `vp_lost`.
51. `vp_lost` bits 1 and 2 appear less often and for shorter spells than in
    2026-10-03b. Campaigns still launch and finish on their usual days.
52. `VIN_PULSE` spacing: about 1 day means the pulse is daily and the cause
    lies elsewhere; about 30 days confirms the cadence cause. Each
    `VIN_ACCRUAL` should be followed by one `NLF_RESUPPLY` or
    `NLF_RESUPPLY_SKIP` line.

## 2026-10-03 third AFK run: surrender limit live, pulse cadence confirmed

Logs in `_local/logs/2026-10-03c/`. No `IC_AFK|FAIL`; error.log has no
rework-local errors (its bulk is unrelated `faction_goals_medium_term.txt`
and SOV strategy-plan noise). Geneva concluded 1954-09-09, final margin
+341.

- VIN: Cao-Bac clean (day 16), Vinh Yen clean (day 18), Mao Khe, Day
  River and Nghia Lo failure, Hoa Binh clean (day 26, against 105 in
  2026-10-03b), Northwest clean (day 49), Na San clean, Pathet Lao raid
  stalemate, Dien Bien Phu clean on day 29, Lower Laos `pressure`.
- CEFEO: Bretagne, Adolphe, Hirondelle, Brochet, Camargue clean; Mouette
  failure; Castor success, Pollux superseded, Atlante stalled.

### Check scoring

- 50 passed: no VIN capitulation. Peak `surrender_pct` 10 with Thanh Hoa
  lost (`vp_lost=2`), against 20-40 for the same loss in 2026-10-03b.
- 51 passed: `vp_lost` non-zero in 2 of 64 `SURRENDER` lines (Northwest
  and Dien Bien Phu), otherwise 0. Campaign launch dates unchanged; Hoa
  Binh much faster. One run; watch whether VIN is now too strong.
- 52 confirmed the cause: `VIN_PULSE` fires every 30-31 days (counter 1
  to 63 over the run), so the 28-step counter gives `VIN_ACCRUAL` only on
  1951-08-12 and 1954-01-04 (amount 40 each). Each was followed by the
  patronage delivery and `NLF_RESUPPLY`. Monthly Campaign Supply income,
  the Chinese patronage delivery and the southern resupply have each run
  about once every 28 months. Campaign Supply still rose from other
  sources (164 to 296).
- 46: NLF held 14 divisions to Geneva and survived to 1962, with only two
  resupplies. The southern collapse did not recur in this run.

### New finding (adjacent, not changed)

The Pathet Lao enter the war at the Lower Laos launch in every recent run
(6 to 8 divisions). Here they capitulated to CEFEO on 1954-03-12 with 8
divisions and their capital held, then sat at 0 divisions to Geneva. Same
small-VP mechanism as the VIN surrender; `LOS_French_Airlift` protects
only the Royal Lao. Related to the deferred Geneva Laos item.

## 2026-10-03 patch: VIN supply step on every pulse

User decision. Statically verified only. `ic_pulse` runs for VIN about
every 31 days, so the VIN block in `IC_scripted_effects.txt` now calls
`vin_accrue_monthly_supply` and the AI rifle grant on every pulse. The
28-step `VIN_Supply_Accrual_Counter` is deleted (it had no other readers).
`VIN_PULSE` drops its `counter` field. Monthly Campaign Supply income
(15, 30 with PRC victory, +10 with larger raids), the Chinese patronage
delivery, the southern resupply and the AI rifle grant (600/1200) now run
monthly instead of about every 28 months. The game-start pulse is followed
by the first mission pulse on the same day, so two accruals land on
1949-05-23. The campaign watchdog is date-based and unaffected.

### Consolidated-playtest checks added

53. One `VIN_ACCRUAL` per `VIN_PULSE`, and each is followed by one
    `NLF_RESUPPLY` or `NLF_RESUPPLY_SKIP` line; `PATRONAGE_DELIVERY`
    monthly after the patronage choice.
54. Balance after the income change: Campaign Supply at each launch
    against 2026-10-03c (Northwest 311, Lower Laos 296), Dien Bien Phu
    duration, VIN campaign results, NLF divisions, final margin. If VIN
    supply runs away, lower the per-month amounts before anything else.
