# Indochina Struggle Mechanic

## Overview

**The Indochina Struggle GUI minigame is the CENTER of all reworked Indochina content.** It represents the entire buildup and conclusion to the First Indochina War, tracking the conflict from its origins through to its resolution.

The Struggle GUI uses a phase system that escalates or de-escalates based on player actions, with multiple endings determined by faction scores. All major decisions, focus trees, and events related to the First Indochina War should feed into and interact with this GUI system, rather than bypassing it.

## Design Philosophy

### Central Role of the Struggle GUI

The Struggle GUI minigame is the primary interface where the First Indochina War plays out. It is not a supplementary system—it is the core mechanic that tracks and resolves the conflict.

### Integration with Decisions and Focus Trees

**Decisions and focus trees should act as triggers and prerequisites, not automatic resolvers.**

- **Decisions** (e.g., "Commence Preparations for the Geneva Conference") should:
  - Unlock or prepare for endings/actions within the GUI
  - Set flags or modify conditions that make GUI endings available
  - NOT automatically trigger state transfers, peace treaties, or other major changes
  - Instead, they should enable the player to take those actions through the GUI

- **Focus Trees** should:
  - Award struggle scores that influence the GUI
  - Unlock GUI options or modify ending availability
  - NOT directly trigger endings or force state changes
  - Instead, they should prepare conditions that allow endings to be selected in the GUI

- **Events** should:
  - Award struggle scores
  - Modify phase points
  - Provide narrative context
  - NOT automatically resolve the conflict

### Example: Geneva Conference

**OLD (Incorrect) Approach:**
- Decision "The Geneva Accords" automatically fires when conditions are met
- Decision directly transfers states, signs peace treaties, and ends the war
- GUI is bypassed entirely

**NEW (Correct) Approach:**
- Decision "Commence Preparations for the Geneva Conference" becomes available when conditions are met
- Decision sets a flag (e.g., `Geneva_Conference_Preparations`) and unlocks the Geneva Conference ending in the GUI
- Player must then select the Geneva Conference ending through the GUI
- The GUI ending effect handles all state transfers, peace treaties, and war resolution
- Decision is a precursor/trigger, not the resolver

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

## How Decisions and Focus Trees Should Interact with GUI

### Decision Pattern: "Commence Preparations for X"

When a decision should lead to an ending, it should follow this pattern:

```
Commence_Preparations_for_Geneva_Conference = {
    available = {
        # Conditions that make Geneva Conference possible
        geneva_conference_should_be_available_trigger = yes
        NOT = { has_global_flag = Geneva_Conference_Preparations }
    }
    complete_effect = {
        # Set flag that unlocks the ending in GUI
        set_global_flag = Geneva_Conference_Preparations
        
        # Optionally award points toward the ending
        add_to_variable = { global.Indochina_War_Next_Phase_B_Points = 100 }
        
        # Fire flavor event if desired
        # news_event = Geneva_Preparations_Begin.1
        
        # DO NOT directly trigger the ending
        # DO NOT transfer states
        # DO NOT sign peace treaties
        # DO NOT call indochina_struggle_trigger_geneva_conference
    }
}
```

### Focus Tree Pattern: "Prepare for X Ending"

When a focus should lead to an ending, it should follow this pattern:

```
FRA_Geneva_Peace_Conference = {
    available = {
        # Conditions that make Geneva Conference possible
        geneva_conference_should_be_available_trigger = yes
        NOT = { has_global_flag = Geneva_Conference_Preparations }
    }
    completion_reward = {
        # Set flag that unlocks the ending in GUI
        set_global_flag = Geneva_Conference_Preparations
        
        # Award struggle scores
        FRA = {
            add_to_variable = { FRA.StruggleInvolvedNationsIndochinaProFranceScore = 200 }
        }
        
        # Optionally award points toward the ending
        add_to_variable = { global.Indochina_War_Next_Phase_B_Points = 150 }
        
        # DO NOT directly trigger the ending
        # DO NOT call indochina_struggle_trigger_geneva_conference
    }
}
```

### GUI Ending Availability

The GUI should check for these preparation flags when determining which endings are available:

```
# In GUI ending availability checks
if = {
    limit = {
        has_global_flag = Geneva_Conference_Preparations
        indochina_struggle_ending_geneva_trigger = yes
    }
    # Show Geneva Conference ending option in GUI
}
```

### GUI Ending Completion Effects

All state transfers, peace treaties, and major changes should happen in the GUI ending completion effects:

```
# In GUI ending effect (e.g., indochina_struggle_geneva_ending_effect)
indochina_struggle_geneva_ending_effect = {
    # Set phase
    set_variable = { global.Indochina_War_Active_Phase = 11 }
    set_global_flag = Geneva_Conference
    
    # Handle all state transfers
    VIN = {
        transfer_state = 838
        transfer_state = 786
    }
    
    # Handle peace treaties
    white_peace = VIN
    white_peace = NLF
    
    # Handle autonomy changes
    set_autonomy = { target = CAM autonomy_state = autonomy_free }
    
    # Fire events
    news_event = Geneva_conference.1
    
    # Auto-complete relevant focus trees
    # (if they haven't been completed already)
}
```

## Rework Required: Making GUI the Center

### Current Issues

The current implementation has decisions and focus trees that automatically trigger endings and force state changes, bypassing the GUI. This needs to be reworked so that:

1. **Decisions become triggers/precursors:**
   - `The_Geneva_Accords` decision should become "Commence Preparations for the Geneva Conference"
   - It should unlock the Geneva ending in the GUI, not directly trigger it
   - All state transfers and peace treaties should happen in the GUI ending effect

2. **Focus trees become enablers:**
   - Focus trees should award scores and unlock GUI options
   - They should NOT directly call ending effects
   - They should set flags that make endings available in the GUI

3. **All major changes happen in GUI:**
   - State transfers
   - Peace treaties
   - Country annexations
   - Autonomy changes
   - All should be handled by GUI ending completion effects

### Decisions to Rework

**France (`common/decisions/FRA.txt`):**
- `The_Geneva_Accords` - Should unlock Geneva ending in GUI, not directly trigger it
- `Proclaim_Victory_in_Vietnam` - Should unlock a victory ending in GUI, not directly annex/transfer states

**Other countries:**
- Any decision that automatically triggers endings or forces state changes should be converted to GUI triggers

### Focus Trees to Rework

**France (`common/national_focus/FRA_1950s.txt`):**
- `FRA_Geneva_Peace_Conference` - Should unlock Geneva ending in GUI, not directly trigger it

**Vietnam (`common/national_focus/VIN_50s.txt`):**
- `VIN_The_Geneva_Peace_Conference` - Should unlock Geneva ending in GUI, not directly trigger it

**USA (`common/national_focus/USA_FP_50s.txt`):**
- `USA_50s_The_Geneva_Conferece` - Should unlock Geneva ending in GUI, not directly trigger it

**Other focus trees:**
- Any focus that directly calls `indochina_struggle_trigger_geneva_conference` or similar ending effects should instead set flags that unlock GUI options

## Implementation Status

All Priority 1 tasks complete:
- Phase ending conditions implemented
- All ending triggers implemented
- Total Anti-Communist score calculation implemented
- Geneva Conference centralized (but needs rework to follow GUI-centric design)
- Test effects system complete
- GUI score display working

Priority 2: Integration & Verification
4. **Focus Tree Integration**
   - Rework focus trees to unlock GUI options instead of directly triggering endings
   - Verify focus trees award struggle scores
   - Check focus trees reference struggle variables
   - Ensure focus tree completions update scores appropriately

5. **Event Integration**
   - Verify events award struggle scores where appropriate
   - Check for events that should trigger ending conditions
   - Ensure events properly update phase points

6. **Decision Integration** (`Indochina_War.txt` and `FRA.txt`)
   - Rework decisions to be triggers/precursors for GUI actions
   - Verify `Indochina_Wrapup_Timer` decision works correctly
   - Check timeout logic for phase endings
   - Ensure decisions unlock GUI options rather than directly triggering endings

Priority 3: Polish & Edge Cases
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
