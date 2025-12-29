# Indochina Struggle Mechanic

## Overview

Scripted GUI mechanic tracking scores for countries in the First Indochina War. Uses a phase system that escalates or de-escalates based on player actions, with multiple endings determined by faction scores.

## Core Components

### Faction Arrays (Stored on FRA)
- Communist: VIN, NLF, MEO
- Pro-France: FRA, CAM, LOS, RCG, SEN, TOG, CMR, TUN, MOR, FRE, AND, SAR
- Pro-Independence: VIE, CCC
- Pro-Ethnic: NUN, FUL, TAI, TAM, THO
- Kuomintang: PQC (added dynamically)
- Interlopers: USA, SOV, PRC, CHI, SIA, KOR, KPA, HUM

### Score Variables (Stored on FRA)
- `StruggleInvolvedNationsIndochinaCommunistScore` - Communist faction score
- `StruggleInvolvedNationsIndochinaProFranceScore` - French loyalist score
- `StruggleInvolvedNationsIndochinaProIndependenceScore` - Pro-independence score
- `StruggleInvolvedNationsIndochinaProEthnicScore` - Ethnic secessionist score
- `StruggleInvolvedNationsIndochinaKuomintangScore` - Kuomintang score
- `StruggleInvolvedNationsIndochinaTotalAntiCommunistScore` - Sum of ProFrance + ProIndependence + ProEthnic

### Phase System

Active Phases (3-8):
- Phase 3: High Intensity
- Phase 4: Medium Intensity
- Phase 5: Low Intensity (Starting Phase)
- Phase 6: High Tension
- Phase 7: Medium Tension
- Phase 8: Low Tension (Maximum De-escalation)

Ending Phases (9-11):
- Phase 9: Never Ending Conflict
- Phase 10: Failed State
- Phase 11: Geneva Conference

Phase Transition Rules:
- Normal phases (3-8) transition via points (500 threshold)
- Transitions only occur when `global.Indochina_War_Active_Phase < 8`
- Phase 8 cannot transition further via points
- Ending phases only set when endings are triggered via GUI
- Phase 100 = Struggle Over (cleanup sentinel)

Geneva Conference Logic:
- Phase 8 + de-escalation points > 500: Geneva becomes available
- Unlock effect sets `Geneva_Conference` flag
- Phase remains at 8 until ending is triggered
- Phase 11 set when ending is triggered via GUI

Phase Variables:
- `global.Indochina_War_Active_Phase` - Current phase
- `global.Indochina_War_Next_Phase_A` - Escalation path
- `global.Indochina_War_Next_Phase_B` - De-escalation path
- `global.Indochina_War_Next_Phase_A_Points` - Points toward escalation
- `global.Indochina_War_Next_Phase_B_Points` - Points toward de-escalation

## Ending Conditions

### Ending 1: Communist Victory
- Trigger: `indochina_struggle_ending_communist_victory_trigger`
- Condition: VIN tag, Communist > 2x Total Anti-Communist, Communist > 1000

### Ending 2: Southern Victory
- Trigger: `indochina_struggle_ending_southern_victory_trigger`
- Condition: VIE tag, anti-communist government, high tension with VIN, ProIndependence > 2x Communist, > ProFrance, > ProEthnic, > 1000

### Ending 3: Federal Vietnam
- Trigger: `indochina_struggle_ending_federal_vietnam_trigger`
- Condition: FRA tag, Total Anti-Communist > 2x Communist, ProFrance > ProIndependence, ProEthnic > ProIndependence, ProFrance > 1000, ProFrance > ProEthnic

### Ending 4: Balkanized Vietnam
- Trigger: `indochina_struggle_ending_balkanized_vietnam_trigger`
- Condition: FUL/FRA/CCC tag, (ProEthnic + ProFrance) > 1000, > 2x ProIndependence, > 2x Communist, ProEthnic >= ProFrance

### Ending 5: Dan Quoc Peace
- Trigger: `indochina_struggle_ending_dan_quoc_peace_trigger`
- Condition: VIN/VIE tag, dan_quoc_peace flag, Ngo Dinh Diem in VIE, Ho Chi Minh in VIN, ProIndependence > ProFrance, > 500

### Ending 6: American-North Vietnam Diplomatic
- Trigger: `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger`
- Condition: USA/VIN tag, Ho Chi Minh in VIN, not at war, positive opinions, VIN favors USA over SOV, USA focus completed, Communist > 2x Total Anti-Communist, > 500

### Ending 7: Kuomintang Victory
- Trigger: `indochina_struggle_ending_kuomintang_victory_trigger`
- Condition: PQC tag, PQC exists, owns Saigon (286) and Hanoi (1760) OR (owns one + KMT score > all other factions)

### Ending 8: Geneva Conference
- Trigger: `indochina_struggle_ending_geneva_trigger`
- Condition: Phase 8 + de-escalation points > 500 OR Geneva_Conference flag OR Phase 11

### Ending 9: Never Ending Conflict
- Trigger: `indochina_struggle_ending_never_ending_trigger`
- Condition: Phase 9 OR (date > 1957.1.1 AND phase >= 3 AND phase < 9)

### Ending 10: Failed State
- Trigger: `indochina_struggle_ending_failed_state_trigger`
- Condition: Phase 10 OR (all faction scores < 500 AND date > 1955.1.1 AND phase < 9)

## Implementation Status

All Priority 1 tasks complete:
- Phase ending conditions implemented
- All ending triggers implemented
- Total Anti-Communist score calculation implemented
- Geneva Conference centralized
- Test effects system complete
- GUI score display working

## File Locations

- Scripted GUI: `common/scripted_guis/CWIC_Struggle.txt`
- On Actions: `common/on_actions/CWIC_Struggle_on_actions.txt`
- Scripted Effects: `common/scripted_effects/CWIC_Struggle_Effects.txt`
- Scripted Triggers: `common/scripted_triggers/IC_struggle_triggers.txt`
- Test Effects: `common/scripted_effects/IC_Struggle_Test_Effects.txt`
- Test Guide: `Indochina_Struggle_Test_Guide.md`
- Decisions: `common/decisions/Indochina_War.txt`
- Events: `events/Indochina_War_Rework.txt`
- Raids: `common/raids/Indochina_Raids.txt`
- Scripted Localization: `common/scripted_localisation/IC_Struggle_Scripted_Loc.txt`

## Notes

- All score variables stored on FRA with `FRA.` prefix
- Phase transitions require 500 points threshold
- Ending conditions checked daily in `on_daily_FRA`
- Endings triggered via GUI, not automatically
- Total Anti-Communist score recalculated daily
