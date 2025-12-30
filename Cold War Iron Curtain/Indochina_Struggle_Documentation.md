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

## Complete Implementation Details

### Initialization (on_startup)

**Location:** `common/on_actions/CWIC_Struggle_on_actions.txt`

On game start:
- Sets initial phase to 5 (Low Intensity - Starting Phase)
- Initializes phase point variables to 0
- Populates phase arrays (3-11) and ending arrays (1-10)
- Initializes all score variables to 0 on FRA
- Sets up faction arrays:
  - Communist: VIN, NLF, MEO
  - Pro-France: FRA, CAM, LOS, RCG, SEN, TOG, CMR, TUN, MOR, FRE, AND, SAR
  - Pro-Independence: VIE, CCC
  - Pro-Ethnic: NUN, FUL, TAI, TAM, THO
  - Interlopers: USA, SOV, PRC, CHI, SIA, KOR, KPA, HUM
- Adds struggle ideas to all involved nations
- Sets up Indochina core states array
- Sets up victory point array (47 VPs total)
- Sets `View_Indochina_Struggle_Startup = 1` to show intro GUI

### Daily Processing (on_daily_FRA)

**Location:** `common/on_actions/CWIC_Struggle_on_actions.txt`

Daily checks:
1. **Phase Transitions:**
   - If escalation points > 499 AND phase < 8: Transition to escalation phase
   - If de-escalation points > 499 AND phase < 8: Transition to de-escalation phase
   - Resets phase points after transition
   - Updates phase transition variables
   - Updates struggle ideas for all involved nations
   - Sets `global.indochina_phase_check = 1` to show phase change notification

2. **Ending Availability:**
   - Checks for Never Ending Conflict conditions, sets `Never_Ending_Conflict_Available` flag
   - Checks for Failed State conditions, sets `Failed_State_Available` flag

3. **Score Recalculation:**
   - Recalculates Total Anti-Communist score daily
   - Updates phase transition paths

### GUI System

**Location:** `common/scripted_guis/CWIC_Struggle.txt`

**Main GUI Windows:**
1. **Struggle_Intro_Indochina** - Introduction screen shown on startup
   - Visible when `View_Indochina_Struggle_Startup = 1`
   - Shows faction-specific introduction image
   - Clickable icons for Army, Economy, Government, Diplomacy (show tooltips)

2. **Struggle_GUI_Indochina** - Main struggle interface
   - Visible when `View_Indochina_Struggle = 1`
   - Displays current phase, next phases, and available endings
   - Dynamic list of endings from `global.Indochina_War_Endings` array
   - Ending buttons show active/inactive based on trigger conditions
   - Clicking ending opens popup

3. **CWIC_Indochina_Struggle_Ending_Popup** - Ending confirmation popup
   - Visible when `show_indochina_end_gui = 1`
   - Shows ending image and description
   - Confirmation button enabled when `show_indochina_end_gui_active = 1`
   - Executes corresponding ending effect on confirmation

4. **CWIC_Indochina_Struggle_Phase_List** - Phase list viewer
   - Visible when `show_indochina_phase_gui = 1`
   - Shows all phases in dynamic list

5. **Indochina_Phase_Prompt** - Phase change notification
   - Visible when `global.indochina_phase_check != 0`

6. **Indochina_Conflict_Prompt** - Border war notification
   - Visible when `global.indochina_border_war_check != 0`

### Border War System

**Location:** `common/decisions/Indochina_War.txt`

Three border war decisions:
1. **Indochina_Struggle_Border_Conflict_Anti_Commie** - For anti-communist factions
2. **Indochina_Struggle_Border_Conflict_Commie** - For communist factions
3. **Indochina_Struggle_Border_Conflict_Kuomintang** - For KMT faction

**Mechanics:**
- Only available when phase < 4
- State-targeted decisions on Indochina core states
- Requires border with enemy faction
- Costs 5 PP
- Starts border war with 4 provinces per side
- Different events based on attacker/defender faction combinations
- Awards phase points and struggle scores based on outcome

**Border War Events:**
- Location: `events/Indochina_War_Rework.txt`
- Events 1-39: Various win/lose outcomes for different faction matchups
- Events 3, 4, 9, 10, 22, 23, 34, 35: Defense outcomes
- Event 100: Cancel event (cleanup)

**Score Awards (per border war):**
- Win: +50 to faction score, +50 phase points
- Loss: +50 to enemy faction score, +50 phase points (opposite direction)
- Some outcomes can reduce enemy scores (e.g., -50)

### Geneva Conference System

**Decision:** `Commence_Preparations_for_Geneva_Conference`
- Location: `common/decisions/FRA.txt`
- Available when: Phase 8 + de-escalation points > 500
- Effects:
  - Sets `Geneva_Conference_Preparations` flag
  - Adds 150 de-escalation points
  - Adds 100 Pro-France score
  - Invites countries to Geneva (FRA, VIN, USA, VIE)

**Invitation Events:**
- Location: `events/Geneva_Conference_Invitations.txt`
- Events 1-4: Invitations to FRA, VIN, USA, VIE
- Each country can accept/decline attendance

**Negotiation Events:**
- Events 5-8: Negotiation events for each country
- Countries choose ceasefire acceptance/rejection
- Countries choose reunification acceptance/rejection
- USA has special option to tamper with VIE negotiations

**Completion Check:**
- Scripted effect: `indochina_struggle_check_geneva_negotiations_complete`
- Checks if all 4 countries have completed negotiations (or don't exist)
- Sets `Geneva_Conference_Negotiations_Complete` flag when all done
- This flag is required for Geneva ending trigger

**Geneva Ending:**
- Two variants:
  - `indochina_struggle_run_geneva_ending_effect` - Standard (no PQC)
  - `indochina_struggle_run_geneva_ending_alternate_effect` - With PQC present
- Handles all state transfers, peace treaties, autonomy changes
- Unlocks focus trees for FRA, VIN, USA
- Clears state flags and modifiers

### Scripted Effects

**Location:** `common/scripted_effects/CWIC_Struggle_Effects.txt`

**Key Effects:**
1. `indochina_struggle_starting_idea_setup` - Initial idea setup
2. `indochina_struggle_invite_countries_to_geneva` - Sends Geneva invitations
3. `indochina_struggle_check_geneva_negotiations_complete` - Checks negotiation completion
4. `indochina_struggle_recalculate_total_anti_communist_score` - Recalculates total
5. `indochina_struggle_update_phase_transitions` - Updates phase transition paths
6. `indochina_struggle_starting_idea_phase_change` - Updates ideas on phase change
7. `indochina_border_war_start_gui_prompt_display` - Shows border war GUI
8. `indochina_struggle_ending_cleanup` - Cleanup when struggle ends
9. `indochina_struggle_communist_victory` - Communist victory ending
10. `indochina_struggle_southern_victory` - Southern victory ending
11. `indochina_struggle_federal_vietnam` - Federal Vietnam ending (includes state transfers)
12. `indochina_struggle_balkanized_vietnam` - Balkanized Vietnam ending
13. `indochina_struggle_dan_quoc_peace` - Dan Quoc peace ending
14. `indochina_struggle_american_north_vietnam` - American-North Vietnam diplomatic ending
15. `indochina_struggle_kuomintang_victory` - KMT victory ending
16. `indochina_struggle_unlock_geneva_conference` - Sets Geneva Conference flag
17. `indochina_struggle_run_geneva_ending_effect` - Geneva ending (standard)
18. `indochina_struggle_run_geneva_ending_alternate_effect` - Geneva ending (with PQC)
19. `indochina_struggle_run_never_ending_conflict_ending_effect` - Never ending conflict
20. `indochina_struggle_run_failed_state_ending_effect` - Failed state ending

### Scripted Triggers

**Location:** `common/scripted_triggers/IC_struggle_triggers.txt`

**Ending Triggers:**
1. `indochina_struggle_ending_communist_victory_trigger`
2. `indochina_struggle_ending_southern_victory_trigger`
3. `indochina_struggle_ending_federal_vietnam_trigger`
4. `indochina_struggle_ending_balkanized_vietnam_trigger`
5. `indochina_struggle_ending_dan_quoc_peace_trigger`
6. `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger`
7. `indochina_struggle_ending_kuomintang_victory_trigger`
8. `indochina_struggle_ending_geneva_trigger`
9. `indochina_struggle_ending_never_ending_trigger`
10. `indochina_struggle_ending_failed_state_trigger`

**Helper Triggers:**
- `geneva_conference_available_trigger` - Checks if Geneva already happened
- `geneva_conference_preparations_trigger` - Checks if preparations started
- `geneva_conference_should_be_available_trigger` - Checks if Geneva should be available

**Component Triggers:**
- Multiple helper triggers for individual condition checks (e.g., `indochina_comm_victory_cond_is_vietnam`, `indochina_comm_victory_cond_ratio`, etc.)

### Ending Effects Details

**Federal Vietnam Ending:**
- Transfers states 838, 786, 671, 881, 1280, 1281 from VIN to VIE
- Annexes VIN and NLF into VIE
- Handles Laos (LOS annexes LAO if both exist)
- Auto-completes USA focus `USA_50s_The_Fall_of_the_Viet_Minh`
- Fires VIN events
- Clears state flags and modifiers

**Geneva Ending:**
- Transfers Laos states to LAO
- White peace with VIN, NLF, LAO
- Sets autonomy for CAM, VIE, LOS
- VIE annexes NLF, CCC, FUL
- VIE transfers states 757, 982, 286, 1287, 983
- VIE leaves faction
- VIN transfers states 838, 786, 671, 881, 1280, 1281, 1760, 1761, 1766
- VIN sets capital to 1760 (Hanoi)
- VIN dismantles faction, drops cosmetic tag
- NLF drops cosmetic tag
- Unlocks focus trees for FRA, VIN, USA
- Clears state flags and modifiers

### Struggle Ideas System

**Location:** `common/ideas/Indochina.txt` (file exists but appears empty - ideas may be defined elsewhere)

**Idea Categories:**
- `STRUGGLE_INDO_ARMY_LEVEL_[3-8]` - Army ideas per phase
- `STRUGGLE_INDO_ECON_LEVEL_[3-8]` - Economic ideas per phase
- `STRUGGLE_INDO_GOVT_LEVEL_[3-8]` - Government ideas per phase
- `STRUGGLE_INDO_DIPL_LEVEL_[3-8]` - Diplomacy ideas per phase

**Phase-Based Ideas:**
- Phase 3: High Intensity ideas
- Phase 4: Medium Intensity ideas
- Phase 5: Low Intensity ideas (starting)
- Phase 6: High Tension ideas
- Phase 7: Medium Tension ideas
- Phase 8: Low Tension ideas

### Scripted Localization

**Location:** `common/scripted_localisation/IC_Struggle_Scripted_Loc.txt`

**Key Localization Functions:**
- `GetIndochinaStruggleIntroductionPicture` - Faction-specific intro images
- `GetIndochinaStruggleIntroductionDesc` - Faction-specific descriptions
- `IndochinaStruggleEndImage` - Ending images
- `IndochinaStruggleEndImageInactive` - Inactive ending images
- `IndochinaStruggleCurrentPhase` - Current phase display
- `IndochinaStruggleNextPhaseA` - Next escalation phase
- `IndochinaStruggleNextPhaseB` - Next de-escalation phase
- `IndochinaStruggleEndPicturePrompt` - Ending popup image
- `GetIndochinaPhaseIcon` - Phase list icons
- Ending title and description functions for all 10 endings

### Events

**Location:** `events/Indochina_War_Rework.txt`

**Border War Events:**
- 39 border war outcome events (win/lose for various faction combinations)
- Event 100: Border war cancellation cleanup

**Ending News Events:**
- `Indochina_Struggle_Ending.1` through `.11` - Major news events for each ending
- All marked as `major = yes` and `fire_only_once = yes`

### Decisions

**Location:** `common/decisions/Indochina_War.txt`

1. **Indochina_Wrapup_Timer** - Hidden decision for timeout logic
   - Not selectable by player
   - 60 day timeout
   - Triggers appropriate ending based on phase state

2. **Debug_Test_Indochina** - Debug decision (empty implementation)

3. **Border War Decisions** - Three decisions for different factions

**Location:** `common/decisions/FRA.txt`

1. **Commence_Preparations_for_Geneva_Conference** - Geneva preparation decision
   - Follows GUI-centric design pattern correctly

### Focus Tree Integration

**Focuses that reference Geneva Conference:**
- `VIE_Accept_Geneva_Conference` (VIE_50s_Bao_Dai.txt)
- `VIN_The_Geneva_Peace_Conference` (VIN_50s.txt)
- `UK50_Participate_Geneva_Conference` (UK_50.txt)
- `PRC_Participate_in_the_Geneva_Conference` (OUTDATED_PRC_50s.txt)
- `CAM_The_Geneva_Conference` (CAM_50s.txt)
- `USA_50s_The_Geneva_Conferece` (USA_FP_50s.txt)
- `FRA_Geneva_Peace_Conference` (likely in FRA_1950s.txt)

**Note:** These focuses may need review to ensure they follow GUI-centric design (unlock GUI options rather than directly triggering endings).

### Test System

**Location:** `common/scripted_effects/IC_Struggle_Test_Effects.txt`

Test effects for debugging and development (not for production use).

## Implementation Status

### ✅ Completed

1. **Core System:**
   - Phase system fully implemented (3-8 active, 9-11 ending phases)
   - Phase transition logic working
   - Score system implemented (5 faction scores + total anti-communist)
   - Daily processing system active

2. **GUI System:**
   - Main struggle GUI implemented
   - Ending popup system working
   - Phase list viewer implemented
   - Introduction screen implemented
   - Phase change notifications working
   - Border war notifications working

3. **Ending System:**
   - All 10 ending triggers implemented
   - All ending effects implemented
   - Ending cleanup system working
   - Ending news events created

4. **Border War System:**
   - Three border war decisions implemented
   - 39 border war events created
   - Score and phase point awards working
   - GUI notifications working

5. **Geneva Conference System:**
   - Preparation decision implemented (follows GUI-centric design)
   - Invitation events created (4 countries)
   - Negotiation events created
   - Completion check system working
   - Two ending variants implemented (with/without PQC)

6. **Scripted Effects:**
   - All major effects implemented
   - Phase transition updates working
   - Score recalculation working
   - Idea system working

7. **Scripted Triggers:**
   - All ending triggers implemented
   - Helper triggers implemented
   - Component triggers for detailed checks

8. **Localization:**
   - Scripted localization functions implemented
   - Ending descriptions and titles set up

### ⚠️ Needs Review/Verification

1. **Focus Tree Integration:**
   - Verify all Geneva-related focuses follow GUI-centric design
   - Check if focuses award struggle scores appropriately
   - Ensure focuses unlock GUI options rather than directly triggering endings
   - Files to check:
     - `common/national_focus/FRA_1950s.txt`
     - `common/national_focus/VIN_50s.txt`
     - `common/national_focus/USA_FP_50s.txt`
     - `common/national_focus/VIE_50s_Bao_Dai.txt`
     - `common/national_focus/CAM_50s.txt`

2. **Event Integration:**
   - Verify other Indochina events award struggle scores where appropriate
   - Check events in:
     - `events/Indochina_War.txt`
     - `events/Indochina_Flavor_Events.txt`
     - `events/American_Indochina.txt`

3. **Decision Integration:**
   - `Indochina_Wrapup_Timer` decision logic needs verification
   - Check if any other decisions need to interact with struggle system

4. **Score Awards:**
   - Verify score awards from focuses and events are balanced
   - Check for any missing score awards

5. **Phase Transition Edge Cases:**
   - Phase 3 escalation: Currently transitions to phase 9 (Never Ending Conflict) - verified
   - Phase 8 de-escalation: Currently transitions to phase 11 (Geneva) - verified
   - These are correct as designed

6. **Geneva Conference Flow:**
   - Verify invitation → negotiation → completion flow works correctly
   - Check if all countries properly complete negotiations
   - Verify ending triggers correctly after negotiations complete

### 🔧 Known Issues/Todos

1. **Trigger Name Consistency:**
   - `indochina_struggle_ending_american_north_vietnam_diplomatic_trigger` - name is correct, verify all references use this exact name

2. **Score Validation:**
   - Border war events can reduce scores (negative values possible)
   - Consider adding minimum score checks or handling negative scores

3. **GUI State Management:**
   - Verify GUI shows/hides correctly based on struggle state
   - Check ending popup triggers when conditions met
   - Verify phase change notifications work

4. **Federal Vietnam Ending:**
   - Currently implements state transfers directly in ending effect
   - This is correct per GUI-centric design (endings handle state changes)
   - Verify all state IDs are correct

5. **Geneva Ending State Transfers:**
   - Complex state transfer logic - verify all state IDs
   - Verify autonomy changes work correctly
   - Check focus tree unlocks

6. **PQC (Kuomintang) Integration:**
   - PQC added dynamically to Kuomintang array
   - Verify PQC creation/joining works correctly
   - Check KMT victory ending handles PQC correctly

7. **Idea System:**
   - Ideas file appears empty - verify ideas are defined elsewhere
   - Check idea effects are properly applied
   - Verify phase-based idea changes work

8. **Test System:**
   - Test effects file exists - ensure it's not used in production
   - Create test guide if needed

## Notes

- All score variables stored on FRA with `FRA.` prefix
- Phase transitions require 500 points threshold
- Ending conditions checked daily in `on_daily_FRA`
- Endings triggered via GUI, not automatically
- Total Anti-Communist score recalculated daily
- Border wars only available when phase < 4
- Geneva Conference requires Phase 8 + de-escalation points > 500
- All major state transfers happen in ending effects (GUI-centric design)
- Struggle ideas applied to all involved nations on startup
- Phase change notifications shown to all involved nations
