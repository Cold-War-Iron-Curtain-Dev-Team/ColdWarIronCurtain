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

**Indochina_Wrapup_Timer:**
- Fallback only: After 1957.1.1, all AI-controlled, no GUI ending selected
- Prevents indefinite conflict in AI-only games

## Time-Based Bonuses

Daily de-escalation bonuses for 1954 Geneva timing:
- 1953: +0.3 points/day (~9/month)
- 1954: +0.5 points/day (~15/month)
- 1955: +0.4 points/day (~12/month)

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
