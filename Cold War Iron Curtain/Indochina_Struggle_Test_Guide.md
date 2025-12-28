# Indochina Struggle Test Effects Guide

## Quick Start

Use these commands in the game console (press `~` to open console):

```
e <effect_name>
```

Example: `e test_indochina_reset`

## Test Effect Categories

### 🔄 Setup & Reset
- `test_indochina_reset` - Reset everything to initial state
- `test_indochina_setup_initial` - Setup with balanced initial scores

### 📊 Phase Manipulation
- `test_indochina_set_phase_high_intensity` - Set to Phase 3
- `test_indochina_set_phase_medium_intensity` - Set to Phase 4
- `test_indochina_set_phase_low_intensity` - Set to Phase 5 (starting)
- `test_indochina_set_phase_high_tension` - Set to Phase 6
- `test_indochina_set_phase_medium_tension` - Set to Phase 7
- `test_indochina_set_phase_low_tension` - Set to Phase 8 (Geneva trigger)
- `test_indochina_set_phase_never_ending` - Set to Phase 9
- `test_indochina_set_phase_failed_state` - Set to Phase 10
- `test_indochina_set_phase_geneva` - Set to Phase 11 (Geneva active)
- `test_indochina_force_escalation` - Add 500 escalation points (⚠️ triggers on daily tick)
- `test_indochina_force_deescalation` - Add 500 de-escalation points (⚠️ triggers on daily tick)
- `test_indochina_manual_escalate` - Manually escalate phase (no daily tick needed)
- `test_indochina_manual_deescalate` - Manually de-escalate phase (no daily tick needed)

### 🎯 Score Manipulation
- `test_indochina_set_communist_high` - Set Communist score to 2000
- `test_indochina_set_communist_low` - Set Communist score to 100
- `test_indochina_set_profrance_high` - Set Pro-France score to 2000
- `test_indochina_set_proindependence_high` - Set Pro-Independence score to 2000
- `test_indochina_set_proethnic_high` - Set Pro-Ethnic score to 2000
- `test_indochina_set_kuomintang_high` - Set Kuomintang score to 2000
- `test_indochina_add_communist_points` - Add 100 to Communist score
- `test_indochina_add_profrance_points` - Add 100 to Pro-France score
- `test_indochina_add_proindependence_points` - Add 100 to Pro-Independence score
- `test_indochina_add_proethnic_points` - Add 100 to Pro-Ethnic score
- `test_indochina_recalculate_anti_communist` - Recalculate total anti-communist score

### 🏁 Ending Tests
- `test_indochina_trigger_communist_victory` - Test Communist Victory ending
- `test_indochina_trigger_southern_victory` - Test Southern Victory ending
- `test_indochina_trigger_federal_vietnam` - Test Federal Vietnam ending
- `test_indochina_trigger_balkanized_vietnam` - Test Balkanized Vietnam ending
- `test_indochina_trigger_kuomintang_victory` - Test Kuomintang Victory ending
- `test_indochina_trigger_geneva` - Test Geneva Conference ending (checks conditions)
- `test_indochina_force_geneva` - Force trigger Geneva Conference (bypasses conditions)
- `test_indochina_trigger_never_ending` - Test Never Ending Conflict ending
- `test_indochina_trigger_failed_state` - Test Failed State ending

### 🖥️ GUI Tests
- `test_indochina_show_gui` - Show main struggle GUI
- `test_indochina_hide_gui` - Hide main struggle GUI
- `test_indochina_show_intro` - Show introduction popup
- `test_indochina_show_phase_prompt` - Show phase change prompt
- `test_indochina_show_ending_popup` - Show ending popup
- `test_indochina_show_phase_list` - Show phase list GUI

### 🎬 Comprehensive Scenarios
- `test_indochina_scenario_communist_win` - Full Communist victory scenario
- `test_indochina_scenario_geneva` - Geneva Conference scenario
- `test_indochina_scenario_escalation` - Escalation path scenario (manual, no loop)
- `test_indochina_scenario_deescalation` - De-escalation path scenario (manual, no loop)
- `test_indochina_scenario_escalation_with_points` - Escalation with points (triggers on daily tick)
- `test_indochina_scenario_deescalation_with_points` - De-escalation with points (triggers on daily tick)
- `test_indochina_scenario_all_endings` - All endings available (GUI testing)

### 🔍 Debug/Info
- `test_indochina_debug_state` - Display current struggle state in log
- `test_indochina_debug_all_triggers` - Test all ending triggers and log results

## Common Test Workflows

### Test Phase Transitions
```
# Manual transition (recommended - no loop)
e test_indochina_reset
e test_indochina_set_phase_low_intensity
e test_indochina_manual_escalate
e test_indochina_debug_state

# Or use points (will trigger on daily tick, may cause loops)
e test_indochina_reset
e test_indochina_set_phase_low_intensity
e test_indochina_force_escalation
# Wait for daily tick
e test_indochina_debug_state
```

### Test Ending Conditions
```
e test_indochina_reset
e test_indochina_set_phase_medium_intensity
e test_indochina_set_communist_high
e test_indochina_recalculate_anti_communist
e test_indochina_trigger_communist_victory
```

### Test Geneva Conference
```
# Unlock Geneva (makes focuses/decisions available)
e test_indochina_reset
e test_indochina_set_phase_low_tension
e test_indochina_unlock_geneva
e test_indochina_debug_state
# Then check GUI - Geneva ending should be available to click

# Or force unlock (bypasses conditions)
e test_indochina_reset
e test_indochina_force_unlock_geneva
e test_indochina_debug_state
# Then check GUI - Geneva ending should be available to click
```

### Test GUI Elements
```
e test_indochina_reset
e test_indochina_setup_initial
e test_indochina_show_gui
e test_indochina_show_intro
```

### Quick State Check
```
e test_indochina_debug_state
e test_indochina_debug_all_triggers
```

## Tips

1. **Always reset first**: Use `test_indochina_reset` before starting a new test scenario
2. **Check state frequently**: Use `test_indochina_debug_state` to see current values
3. **Test triggers**: Use `test_indochina_debug_all_triggers` to see which endings are available
4. **Combine effects**: You can chain multiple effects in one command: `e test_indochina_reset; e test_indochina_set_phase_low_tension`
5. **Check logs**: Open the game log to see detailed output from debug effects
6. **Avoid phase loops**: Use `test_indochina_manual_escalate`/`deescalate` instead of `force_escalation`/`deescalation` to avoid daily tick loops
7. **Geneva testing**: If `test_indochina_trigger_geneva` doesn't work, use `test_indochina_force_geneva` to bypass conditions

## Phase Reference

- **Phase 3**: High Intensity
- **Phase 4**: Medium Intensity  
- **Phase 5**: Low Intensity (Starting Phase)
- **Phase 6**: High Tension
- **Phase 7**: Medium Tension
- **Phase 8**: Low Tension (Geneva trigger)
- **Phase 9**: Never Ending Conflict
- **Phase 10**: Failed State
- **Phase 11**: Conference in Geneva

## Score Thresholds for Endings

- **Minimum score**: 1000 points required for most endings
- **Ratio requirement**: Most endings require 2x the score of competing factions
- **Total Anti-Communist**: Sum of ProFrance + ProIndependence + ProEthnic

## Notes

- All test effects are prefixed with `test_indochina_` for easy identification
- Effects that modify scores will also update related variables when appropriate
- Some effects include logging to help track what's happening
- GUI effects only show/hide elements - they don't test functionality
- Ending test effects will check conditions and trigger if met, or log if not

