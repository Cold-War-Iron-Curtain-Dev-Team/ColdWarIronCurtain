# Indochina Struggle GUI System

## Overview

The Indochina Struggle GUI is the core mechanic for the First Indochina War. It uses a phase system (3-8 active, 9-11 endings) and faction scores to determine outcomes. All major decisions, focus trees, and events feed into this GUI system.

## Design Philosophy

**GUI-Centric Design:**
- Decisions and focus trees act as triggers/precursors, not automatic resolvers
- All state transfers, peace treaties, and major changes happen in GUI ending effects
- Player selects endings through GUI, maintaining agency

**Integration Pattern:**
- Decisions: Unlock GUI options, set flags, award scores
- Focus Trees: Award scores, unlock GUI options, set flags
- Events: Award scores, modify phase points, provide narrative
- GUI Endings: Handle all state changes, peace treaties, annexations

## To Do
- Have SV mix of defending and doing raids instead of letting NLF walk over everything
- Include points in VIE Mil branch
- Have VIE do Diplo tree focuses when they unlock
- Maybe start off on medium intensity then have huge boost to high/medium tension when/if they annex NLF
- Have the Geneva Conference be triggered like we have it already/OR have it triggered when FRA and USA realize costs too high and dip
- This way other endings are triggered also depending on FRA/USA choices

## Core Components

### Faction Arrays (Stored on FRA)
- Communist: VIN, NLF, MEO
- Pro-France: FRA, CAM, LOS, RCG, SEN, TOG, CMR, TUN, MOR, FRE, AND, SAR
- Pro-Independence: VIE, CCC
- Pro-Ethnic: NUN, FUL, TAI, TAM, THO
- Kuomintang: PQC (added dynamically)
- Interlopers: USA, SOV, PRC, CHI, SIA, KOR, KPA, HUM

### Score Variables (Stored on FRA)
- `StruggleInvolvedNationsIndochinaCommunistScore`
- `StruggleInvolvedNationsIndochinaProFranceScore`
- `StruggleInvolvedNationsIndochinaProIndependenceScore`
- `StruggleInvolvedNationsIndochinaProEthnicScore`
- `StruggleInvolvedNationsIndochinaKuomintangScore`
- `StruggleInvolvedNationsIndochinaTotalAntiCommunistScore` (sum of ProFrance + ProIndependence + ProEthnic)

### Phase System

**Active Phases (3-8):**
- Phase 3: High Intensity
- Phase 4: Medium Intensity
- Phase 5: Low Intensity (Starting)
- Phase 6: High Tension
- Phase 7: Medium Tension
- Phase 8: Low Tension (Max De-escalation)

**Ending Phases (9-11):**
- Phase 9: Never Ending Conflict
- Phase 10: Failed State
- Phase 11: Geneva Conference

**Phase Variables:**
- `global.Indochina_War_Active_Phase` - Current phase
- `global.Indochina_War_Next_Phase_A_Points` - Escalation points
- `global.Indochina_War_Next_Phase_B_Points` - De-escalation points

**Transition Rules:**
- 500 points threshold for phase transitions
- Transitions only when phase < 8
- Phase 8 cannot transition further via points
- Ending phases set when endings triggered via GUI
- Phase 100 = Struggle Over (cleanup)

## Ending Conditions

### 1. Communist Victory
- Tag: VIN
- Conditions: Communist > 2x Total Anti-Communist, Communist > 1000
- Bypass: Full war + VIN owns Saigon (286) OR VIN annexes VIE
- Effect: VIN annexes VIE/NLF, transfers all Vietnam states, sets capital to Hanoi (1760)

### 2. Southern Victory
- Tag: VIE
- Conditions: Anti-communist government, high tension with VIN, ProIndependence > 2x Communist, > ProFrance, > ProEthnic, > 1000
- Effect: VIE annexes VIN/NLF, transfers all North Vietnam states, sets capital to Saigon (286), cores Hanoi (1760)
- Focus Chain: `VIE_BaoDai_Liberator_of_Vietnam` bypass → `BaoDai.13` (revolt in Hoang Lien Son) → `VIE_Why_Revolting` → `BaoDai.14` (crackdown)

### 3. Federal Vietnam
- Tag: FRA
- Conditions: Total Anti-Communist > 2x Communist, ProFrance > ProIndependence, ProEthnic > ProIndependence, ProFrance > 1000, ProFrance > ProEthnic
- Effect: VIE annexes VIN/NLF, transfers North Vietnam states to VIE

### 4. Balkanized Vietnam
- Tag: FUL/FRA/CCC
- Conditions: (ProEthnic + ProFrance) > 1000, > 2x ProIndependence, > 2x Communist, ProEthnic >= ProFrance
- Effect: Multiple independent states

### 5. Dan Quoc Peace
- Tag: VIN/VIE
- Conditions: `dan_quoc_peace` flag, Ngo Dinh Diem in VIE, Ho Chi Minh in VIN, ProIndependence > ProFrance, > 500
- Effect: Reunification under Diem-Ho agreement

### 6. American-North Vietnam Diplomatic
- Tag: USA/VIN
- Conditions: Ho Chi Minh in VIN, not at war, positive opinions, VIN favors USA over SOV, USA focus completed, Communist > 2x Total Anti-Communist, > 500
- Effect: VIN democratizes (Social Democratic), unifies Vietnam, improves USA relations

### 7. Kuomintang Victory
- Tag: PQC
- Conditions: PQC exists, owns Saigon (286) and Hanoi (1760) OR (owns one + KMT score > all other factions)
- Effect: PQC unifies Vietnam, sets capital to Saigon (286) or Hanoi (1760)

### 8. Geneva Conference
- Tag: Any
- Conditions: Phase 8 + de-escalation points > 500 OR `Geneva_Conference` flag OR Phase 11
- Effect: Partition at 17th parallel, VIN gets North, VIE gets South, Laos/Cambodia independent

### 9. Never Ending Conflict
- Tag: Any
- Conditions: Phase 9 OR (date > 1957.1.1 AND phase >= 3 AND phase < 9)
- Effect: Conflict continues indefinitely

### 10. Failed State
- Tag: Any
- Conditions: Phase 10 OR (all faction scores < 500 AND date > 1955.1.1 AND phase < 9)
- Effect: Complete collapse, no clear winner

## Focus Tree Bypass System

Focuses automatically bypass when their ending becomes available:
- `VIN_Total_Victory` - Communist Victory
- `VIE_BaoDai_Liberator_of_Vietnam` - Southern Victory
- `VIN_Accept_French_Three_Vietnam_Federal_Scheme` - Federal Vietnam
- `VIN_A_Failed_State` - Failed State
- `VIE_Accept_Geneva_Conference` - Geneva Conference

Bypass triggers check if ending trigger is met OR war is over.

## Automatic Triggers

**Communist Victory Preparation:**
- Fires daily in `on_daily_FRA` when VIE capitulates/doesn't exist OR (VIN at war with VIE AND VIN owns Saigon)
- Awards 1500 Communist score and 200 escalation points
- Unlocks ending in GUI

**Indochina_Wrapup_Timer (AI-only auto-resolution):**
- Activated from `ic_pulse` (IC_scripted_effects.txt) only when `indochina_struggle_all_participants_ai_trigger` passes: France AND every Indochina participant (VIN, VIE, NLF, MEO, CAM, LOS, LAO, CCC, PQC, FUL, TAI, TAM, THO, NUN, FRE) is AI controlled. A human playing any participant keeps full control of the minigame; interloper players (USA/SOV/etc.) still shape the outcome through scores.
- Historical window: activates 1954.5.20-1954.7.10, and the 60-day timeout lands ~21 July 1954 (OTL Geneva Accords). A post-1957.1.1 window catches AI-only stalemates that missed it. The 1954 window is skipped while a human USA is mid `USA_VIN_Reunification` chain.
- On timeout it runs the first *earned* decisive ending (USA-VIN reunification complete → Communist Victory → Southern Victory → Kuomintang Victory → Dan Quoc Peace → Federal Vietnam → Balkanized Vietnam), defaulting to the historical Geneva partition otherwise. Each ending effect fires its own `major = yes` news event from FRA scope, so all players see the outcome.
- Cancelled automatically if `Indochina_War_Over` gets set while the timer runs.

**Save-load guard:**
- The struggle `on_startup` block is guarded by `indochina_struggle_initialized`; without it every save reload reset the phase/scores and duplicated the phase/ending GUI arrays.

## Time-Based Bonuses

Monthly de-escalation bonuses for 1954 Geneva timing (on_monthly_FRA):
- 1953: +9/month
- 1954: +15/month
- 1955: +12/month

The drip runs in every active phase including Low Tension (gate `phase < 9`), so
progress toward the Geneva threshold (phase 8 + 500 B points) does not stall
once maximum de-escalation is reached.

## Struggle Diplomacy Decisions

Faction-gated decisions in `Indochina_War_Rework` (common/decisions/Indochina_War.txt),
visible only during the tension phases (6-8), added because raids progressively
disable as tension drops and previously left de-escalating players with no actions.
All point awards go through the shared helpers in CWIC_Struggle_Effects.txt
(`indochina_struggle_add_<faction>_diplomatic_points` = 75 B + 75 faction score;
`..._military_points` = 75 A + 75 faction score).

Per faction array (Pro-Independence, Communist, Pro-France):
- 3 de-escalation decisions (25 PP, 70-day re-enable, ~96 B/month if cycled)
- 1 escalation decision (50 PP, 90-day re-enable, `ai_will_do = 0` so only
  players can push tension back up; AI escalation stays raid/border-war driven)
- AI weight on the de-escalation decisions ramps x10 after 1953.1.1 to support
  the historical Geneva timeline.

**Pro-Independence path to Geneva:** `Indochina_Struggle_ProInd_Propose_Peace_Conference`
(phase 8, B > 300, Geneva preparations not yet set) fires
`Geneva_Conference_Invitation.5` at FRA. Accepting sets `Geneva_Conference_Preparations`,
adds 150 B + 100 ProIndependence score and runs the normal invitation chain;
declining costs 100 B (clamped at 0) and the proposal re-enables after 120 days.
Previously only an FRA decision or FRE focus could initiate Geneva.

**VIE Diplo tree hooks:** `VIE_Negotiate_Brevet_Lines`, `VIE_Beg_Pulo_Condore_Return`
and `VIE_Beg_Crown_Domain_French_Renouncement` now award pro-independence
diplomatic points (75 B + 75 score) on completion.

**Raid failure parity fix:** all five `steal_*_INDO_KMT_AGAINST_COM` raids were
missing the de-escalation award on failure that their `_COMMIE` and
`_KMT_AGAINST_CAP` siblings have; failure now adds B points (16 small
arms/armor, 8 artillery/motorized/mechanized) to match.

## File Locations

- Scripted GUI: `common/scripted_guis/CWIC_Struggle.txt`
- On Actions: `common/on_actions/CWIC_Struggle_on_actions.txt`
- Scripted Effects: `common/scripted_effects/CWIC_Struggle_Effects.txt`
- Scripted Triggers: `common/scripted_triggers/IC_struggle_triggers.txt`
- Test Effects: `common/scripted_effects/IC_Struggle_Test_Effects.txt`
- Test Guide: `Indochina_Struggle_Test_Guide.md`
- Decisions: `common/decisions/Indochina_War.txt`, `common/decisions/FRA.txt`
- Events: `events/VIE_Events.txt` (BaoDai.13, BaoDai.14)
- Focus Trees: `common/national_focus/VIN_50s.txt`, `common/national_focus/VIE_50s_Bao_Dai.txt`
