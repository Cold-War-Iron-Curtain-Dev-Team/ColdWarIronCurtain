# Indochina Struggle Mechanic - Documentation & Finalization Checklist

## Overview

The Indochina Struggle is a scripted GUI mechanic that tracks scores for countries involved in the First Indochina War. It uses a phase system that can escalate or de-escalate based on player actions, with multiple possible endings determined by faction scores.

## Core Components

### 1. Faction Arrays (Stored on FRA)
- **Communist**: VIN, NLF, MEO
- **Pro-France**: FRA, CAM, LOS, RCG, SEN, TOG, CMR, TUN, MOR, FRE, AND, SAR
- **Pro-Independence**: VIE, CCC
- **Pro-Ethnic**: NUN, FUL, TAI, TAM, THO
- **Kuomintang**: PQC (can be added dynamically)
- **Interlopers**: USA, SOV, PRC, CHI, SIA, KOR, KPA, HUM

### 2. Score Variables (Stored on FRA)
- `StruggleInvolvedNationsIndochinaCommunistScore` - Communist faction score
- `StruggleInvolvedNationsIndochinaProFranceScore` - French loyalist score
- `StruggleInvolvedNationsIndochinaProIndependenceScore` - Pro-independence score
- `StruggleInvolvedNationsIndochinaProEthnicScore` - Ethnic secessionist score
- `StruggleInvolvedNationsIndochinaKuomintangScore` - Kuomintang score
- `StruggleInvolvedNationsIndochinaTotalAntiCommunistScore` - Aggregated anti-communist score (sum of ProFrance + ProIndependence + ProEthnic)

### 3. Phase System
**Active Phases:**
- Phase 3: High Intensity
- Phase 4: Medium Intensity
- Phase 5: Low Intensity (Starting Phase)
- Phase 6: High Tension
- Phase 7: Medium Tension
- Phase 8: Low Tension

**Ending Phases:**
- Phase 9: Never Ending Conflict
- Phase 10: Failed State
- Phase 11: Conference in Geneva

**Phase Transition Variables:**
- `global.Indochina_War_Active_Phase` - Current phase
- `global.Indochina_War_Next_Phase_A` - Escalation path (increases intensity)
- `global.Indochina_War_Next_Phase_B` - De-escalation path (increases tension)
- `global.Indochina_War_Next_Phase_A_Points` - Points toward escalation (threshold: 500)
- `global.Indochina_War_Next_Phase_B_Points` - Points toward de-escalation (threshold: 500)

### 4. Score Sources
Scores are updated through:
- **Raids** (`Indochina_Raids.txt`): Various raid types award points based on success level
- **Border Wars** (`Indochina_War_Rework.txt`): Border war outcomes award 50 points
- **Focus Trees**: Should award points (needs verification)
- **Events**: Should award points (needs verification)

## Current Implementation Status

### ✅ Fully Implemented

1. **GUI System** (`CWIC_Struggle.txt`)
   - Main struggle GUI (`Struggle_GUI_Indochina`)
   - Introduction popup (`Struggle_Intro_Indochina`)
   - Phase list GUI (`CWIC_Indochina_Struggle_Phase_List`)
   - Ending popup (`CWIC_Indochina_Struggle_Ending_Popup`)
   - Phase change prompt (`Indochina_Phase_Prompt`)
   - Border war prompt (`Indochina_Conflict_Prompt`)

2. **On Actions** (`CWIC_Struggle_on_actions.txt`)
   - Daily phase transition check (when points reach 500)
   - Startup initialization (arrays, variables, ideas)
   - Phase change notifications

3. **Scripted Effects** (`CWIC_Struggle_Effects.txt`)
   - Starting idea setup
   - Phase change idea updates
   - Ending cleanup
   - All 10 ending effects (call news events)

4. **Border War Events** (`Indochina_War_Rework.txt`)
   - Complete border war event chain
   - Score updates for all faction combinations
   - Variable cleanup

5. **Ending News Events** (`Indochina_War_Rework.txt`)
   - All 11 ending events defined (1-11)
   - Proper localization keys

6. **Raids System** (`Indochina_Raids.txt`)
   - Extensive raid types for all factions
   - Score updates integrated
   - Phase point updates integrated

7. **Scripted Localization** (`IC_Struggle_Scripted_Loc.txt`)
   - Comprehensive localization system
   - Dynamic text for phases, endings, scores

### ⚠️ Partially Implemented / Needs Work

1. **Ending Triggers** (`IC_struggle_triggers.txt`)
   - ✅ Communist Victory - **COMPLETE**
   - ✅ Southern Victory - **COMPLETE**
   - ✅ Federal Vietnam - **COMPLETE**
   - ✅ Balkanized Vietnam - **COMPLETE**
   - ⚠️ Dan Quoc Peace - **INCOMPLETE** (only checks for flag, needs proper conditions)
   - ⚠️ American-North Vietnam Diplomatic - **INCOMPLETE** (always = no, TODO comment)
   - ✅ Kuomintang Victory - **COMPLETE**
   - ❌ Geneva Conference - **NOT IMPLEMENTED** (always = no)
   - ❌ Never Ending Conflict - **NOT IMPLEMENTED** (always = no)
   - ❌ Failed State - **NOT IMPLEMENTED** (always = no)

2. **Phase Ending Conditions** (`CWIC_Struggle_on_actions.txt`)
   - Line 74: Comment "#Add Section for Phase Endings when Endings Coded"
   - **MISSING**: Logic to transition to phase endings (9, 10, 11) when conditions are met
   - **MISSING**: Conditions for when phase 8 (Low Tension) should trigger Geneva
   - **MISSING**: Conditions for when to trigger Never Ending Conflict (Phase 9)
   - **MISSING**: Conditions for when to trigger Failed State (Phase 10)

3. **Total Anti-Communist Score Calculation**
   - Variable exists and is updated in raids/border wars
   - **MISSING**: Automatic aggregation system (should sum ProFrance + ProIndependence + ProEthnic)
   - Currently only updated manually in specific events

4. **Trigger Name Error**
   - `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger` exists but has `always = no`
   - This causes errors in scripted localization and GUI files that reference it
   - **FIX**: Implement proper conditions or remove `always = no` once conditions are added

## Ending Details

### Ending 1: Communist Victory ("3 Lands, 3 People, 1 Red Banner")
- **Trigger**: `indochina_struggle_ending_communist_victory_trigger`
- **Condition**: VIN tag, Communist score > 2x Total Anti-Communist score, Communist score > 1000
- **Status**: ✅ Complete

### Ending 2: Southern Victory ("A Quoc-gia Vietnam")
- **Trigger**: `indochina_struggle_ending_southern_victory_trigger`
- **Condition**: VIE tag, ProIndependence score > 2x Communist score, > 2x ProEthnic score, > 1000, > ProFrance score
- **Status**: ✅ Complete

### Ending 3: Federal Vietnam
- **Trigger**: `indochina_struggle_ending_federal_vietnam_trigger`
- **Condition**: FRA tag, ProFrance score > 2x Communist score, > 2x ProEthnic score, > 1000, > ProIndependence score
- **Status**: ✅ Complete

### Ending 4: Balkanized Vietnam ("An Overgrown Garden")
- **Trigger**: `indochina_struggle_ending_balkanized_vietnam_trigger`
- **Condition**: FUL/FRA/CCC tag, (ProEthnic + ProFrance) > 1000, > 2x ProIndependence, > 2x Communist
- **Status**: ✅ Complete

### Ending 5: Dan Quoc Peace
- **Trigger**: `indochina_struggle_ending_dan_quoc_peace_trigger`
- **Condition**: VIN/VIE tag, has flag `dan_quoc_peace`
- **Status**: ⚠️ **INCOMPLETE** - Only checks flag, needs proper score conditions

### Ending 6: American-North Vietnam Diplomatic ("A Gift From Truman")
- **Trigger**: `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger`
- **Condition**: USA/VIN tag, TODO comment present
- **Status**: ❌ **NOT IMPLEMENTED** - Always returns false

### Ending 7: Kuomintang Victory ("White Star Over The Southern Brother")
- **Trigger**: `indochina_struggle_ending_kuomintang_victory_trigger`
- **Condition**: PQC tag, owns states 286 & 1760 OR (owns one + KMT score > all other factions)
- **Status**: ✅ Complete

### Ending 8: Geneva Conference (Historical)
- **Trigger**: `indochina_struggle_ending_geneva_trigger`
- **Condition**: Always = no
- **Status**: ❌ **NOT IMPLEMENTED**
- **Note**: Should trigger when phase reaches Low Tension (8) and certain conditions met, OR via decision timer

### Ending 9: Never Ending Conflict
- **Trigger**: `indochina_struggle_ending_never_ending_trigger`
- **Condition**: Always = no
- **Status**: ❌ **NOT IMPLEMENTED**
- **Note**: Should trigger when phase = 9 (Never Ending Conflict phase)

### Ending 10: Failed State
- **Trigger**: `indochina_struggle_ending_failed_state_trigger`
- **Condition**: Always = no
- **Status**: ❌ **NOT IMPLEMENTED**
- **Note**: Should trigger when phase = 10 (Failed State phase)

## What Needs to be Finalized

### Priority 1: Critical Missing Implementations

1. **Phase Ending Conditions** (`CWIC_Struggle_on_actions.txt`)
   - Add logic in `on_daily_FRA` to check for phase ending conditions
   - When `global.Indochina_War_Active_Phase = 8` (Low Tension) + conditions → trigger Geneva ending
   - When `global.Indochina_War_Active_Phase = 9` → trigger Never Ending Conflict ending
   - When `global.Indochina_War_Active_Phase = 10` → trigger Failed State ending
   - Need to define what conditions should trigger these phase transitions

2. **Ending Triggers** (`IC_struggle_triggers.txt`)
   - **Geneva Conference**: Implement conditions (e.g., phase = 8, certain date, diplomatic conditions)
   - **Never Ending Conflict**: Implement conditions (e.g., phase = 9, war duration > X years)
   - **Failed State**: Implement conditions (e.g., phase = 10, all factions below threshold)
   - **Dan Quoc Peace**: Add score conditions in addition to flag check
   - **American-North Vietnam**: Implement proper conditions (diplomatic relations, score thresholds)

3. **Total Anti-Communist Score Aggregation**
   - Add daily/periodic calculation: `StruggleInvolvedNationsIndochinaTotalAntiCommunistScore = ProFrance + ProIndependence + ProEthnic`
   - Or add to `on_daily_FRA` to recalculate automatically

### Priority 2: Integration & Verification

4. **Focus Tree Integration**
   - Verify focus trees award struggle scores
   - Check focus trees reference struggle variables
   - Ensure focus tree completions update scores appropriately

5. **Event Integration**
   - Verify events award struggle scores where appropriate
   - Check for events that should trigger ending conditions
   - Ensure events properly update phase points

6. **Decision Integration** (`Indochina_War.txt`)
   - Verify `Indochina_Wrapup_Timer` decision works correctly
   - Check timeout logic for phase endings
   - Ensure decision properly triggers endings

### Priority 3: Polish & Edge Cases

7. **Trigger Name Consistency**
   - Fix `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger` references
   - Verify all trigger names match between files

8. **Phase Transition Edge Cases**
   - What happens if phase reaches 3 (High Intensity) and tries to escalate further?
   - What happens if phase reaches 8 (Low Tension) and tries to de-escalate further?
   - Add safeguards to prevent invalid phase transitions

9. **Score Validation**
   - Ensure scores can't go negative (or handle negative scores appropriately)
   - Add maximum score caps if needed
   - Verify score calculations are balanced

10. **GUI State Management**
    - Verify GUI properly shows/hides based on struggle state
    - Check ending popup triggers correctly when conditions met
    - Ensure phase change notifications work

## File Locations Reference

- **Scripted GUI**: `common/scripted_guis/CWIC_Struggle.txt`
- **On Actions**: `common/on_actions/CWIC_Struggle_on_actions.txt`
- **Scripted Effects**: `common/scripted_effects/CWIC_Struggle_Effects.txt`
- **Scripted Triggers**: `common/scripted_triggers/IC_struggle_triggers.txt`
- **Decisions**: `common/decisions/Indochina_War.txt`
- **Events**: `events/Indochina_War_Rework.txt`
- **Raids**: `common/raids/Indochina_Raids.txt`
- **Scripted Localization**: `common/scripted_localisation/IC_Struggle_Scripted_Loc.txt`
- **Focus Trees**: Check `common/national_focus/` for VIE, VIN, FRA, PQC, etc.

## Testing Checklist

- [ ] Phase transitions work correctly (escalation/de-escalation)
- [ ] Scores update from raids
- [ ] Scores update from border wars
- [ ] Scores update from focus trees (if applicable)
- [ ] Scores update from events (if applicable)
- [ ] All 10 ending triggers fire when conditions met
- [ ] Ending popup appears when ending becomes available
- [ ] Ending effects execute correctly
- [ ] Phase ending conditions (9, 10, 11) trigger appropriately
- [ ] GUI displays correctly for all involved nations
- [ ] Total Anti-Communist score calculates correctly
- [ ] No errors in error log related to struggle mechanic

## Notes

- The struggle mechanic is stored on FRA (France) as the "host" country
- All involved nations get struggle ideas that change with phases
- The mechanic should be global and accessible to any involved country
- Phase transitions require 500 points in either direction
- Ending conditions should be checked regularly (daily or on specific triggers)

## Known Issues

1. **Error Log Errors**: The trigger `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger` causes errors because it has `always = no` but is referenced in GUI and localization files. This will cause game startup errors until the trigger is properly implemented.

2. **Missing Total Anti-Communist Score Aggregation**: The variable is updated manually in some places but should be automatically calculated as the sum of ProFrance + ProIndependence + ProEthnic scores.

3. **Phase Ending Logic**: The comment on line 74 of `CWIC_Struggle_on_actions.txt` indicates phase ending logic was planned but not implemented.

## Quick Reference: Ending IDs

- Ending 1: Communist Victory
- Ending 2: Southern Victory  
- Ending 3: Federal Vietnam
- Ending 4: Balkanized Vietnam
- Ending 5: Dan Quoc Peace
- Ending 6: American-North Vietnam Diplomatic
- Ending 7: Kuomintang Victory
- Ending 8: Geneva Conference (Historical)
- Ending 9: Never Ending Conflict
- Ending 10: Failed State
- Ending 11: Geneva Conference (Alternate) - Used when PQC exists

