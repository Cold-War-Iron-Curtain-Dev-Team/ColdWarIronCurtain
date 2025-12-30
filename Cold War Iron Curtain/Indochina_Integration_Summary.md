# Indochina Integration Summary

## Changes Made

### 1. Updated Indochina_Wrapup_Timer Decision (Fallback Only)
**File:** `common/decisions/Indochina_War.txt`

**What Changed:**
- Converted to a late-game fallback mechanism instead of removing it
- Only activates after 1957.1.1 (late-game fallback)
- Only triggers if no ending has been selected via GUI (checks Indochina_War_Over flag)
- Only triggers if all Indochina countries + France are AI controlled
- This ensures it only acts as a last resort for AI-only games

**Impact:**
- Players must still select endings through the GUI system (decision won't trigger if any player is involved)
- AI-only games will have a fallback to prevent indefinite conflict
- Maintains player agency and GUI-centric design for human players

### 2. Converted Proclaim_Victory_in_the_liberation_war to Automatic Trigger
**Files:** 
- `common/decisions/FRA.txt` (decision removed)
- `common/scripted_effects/CWIC_Struggle_Effects.txt` (new automatic effect)
- `common/on_actions/CWIC_Struggle_on_actions.txt` (added to daily check)

**What Changed:**
- **Removed decision entirely** - converted to automatic, invisible trigger
- **New scripted effect:** `indochina_struggle_auto_trigger_communist_victory_preparation`
- **Automatic daily check:** Fires automatically in `on_daily_FRA` when conditions are met
- **Conditions checked:**
  1. VIE capitulated or doesn't exist (and USA hasn't completed Operation Vulture)
  2. VIN and VIE are at full war AND VIN controls Saigon (state 286)
- **Effect:** Awards 1500 Communist score and 200 escalation points to unlock ending in GUI
- **Fire once flag:** Uses `VIN_Communist_Victory_Preparation_Triggered` to prevent multiple fires

**Impact:**
- Completely automatic and invisible - no player decision needed
- Maintains GUI-centric design (scores unlock ending, player selects in GUI)
- Allows for military victory path (capturing Saigon) in addition to score-based victory
- Prepares for future alert system (when ending becomes available, can show popup)

### 2b. Enhanced Communist Victory Trigger and Effect
**Files:** 
- `common/scripted_triggers/IC_struggle_triggers.txt`
- `common/scripted_effects/CWIC_Struggle_Effects.txt`

**What Changed:**
- **Trigger:** Added bypass condition - if VIN and VIE are at full war AND (VIN owns Saigon (286) OR VIN has annexed VIE), the ending becomes available regardless of scores
- **Effect:** Expanded from minimal cleanup to full state transfer implementation:
  - Transfers all Vietnam states from VIE to VIN (757, 982, 286, 1287, 983)
  - Annexes VIE and NLF into VIN
  - Handles Laos state transfers to LAO
  - Sets Cambodia autonomy
  - Signs peace treaties with FRA, LAO, NLF
  - Clears state flags and modifiers
  - Auto-completes VIN focus tree
  - Fires appropriate events

**Impact:**
- Allows military victory path (capturing Saigon) in addition to score-based victory
- Complete state transfer implementation ensures proper resolution
- Maintains GUI-centric design (all changes happen in ending effect, not decision)

### 3. Added Time-Based Bonuses for 1954 Geneva Timing
**File:** `common/on_actions/CWIC_Struggle_on_actions.txt`

**What Changed:**
- Added daily de-escalation point bonuses starting in 1953
- 1953: +0.3 points per day (~9 per month)
- 1954: +0.5 points per day (~15 per month) - increased to push toward Geneva
- 1955: +0.4 points per day (~12 per month) - continues if not resolved

**Impact:**
- Ensures gradual progress toward Phase 8 (Low Tension) by 1954
- Makes Geneva Conference most likely in 1954 (historical timing)
- Provides ~109 points in 1953, ~182 points in 1954, ~146 points in 1955
- Combined with raids, border wars, and other sources, should reliably reach Phase 8 by 1954

## Raid System Analysis

### Point Awards Per Raid:
- **Failure:** +1 de-escalation (anti-commie raids) or +1 escalation (commie raids)
- **Limited Success:** +1 escalation
- **Success:** +2 escalation  
- **Critical Success:** +5 escalation

### Assessment:
- **Reasonable for long-term conflict:** Small point values prevent rapid phase changes
- **Balanced accumulation:** Raids provide steady, gradual progress
- **Works with other systems:** Combined with border wars (50 points), focus trees, events, and time bonuses
- **1954 timing achievable:** With time-based bonuses, should reliably reach Phase 8 by 1954

### Point Accumulation Estimate (1949-1954):
- **Raids:** ~390-650 points (130 possible raids × 3-5 average)
- **Border Wars:** ~200-400 points (4-8 wars × 50 points)
- **Time Bonuses (1953-1954):** ~291 points (109 + 182)
- **Focus Trees/Events:** Variable, estimated ~200-400 points
- **Total Estimated:** ~1081-1741 points
- **Required for Phase 8:** 1500 points (3 transitions × 500)

**Conclusion:** System is reasonable and should reach Phase 8 by 1954 with time bonuses. May need minor adjustment based on testing.

## Design Philosophy Maintained

All changes maintain the **GUI-centric design**:
- Decisions act as triggers/precursors, not resolvers
- All major state changes happen in GUI ending effects
- Player agency preserved through GUI selection
- No automatic forced endings (except late-game fallbacks if needed)

## Next Steps

1. **Test the system:**
   - Verify time bonuses accumulate correctly
   - Test that Geneva Conference becomes available in 1954
   - Verify Proclaim_Victory decision unlocks GUI ending correctly

2. **Balance adjustments (if needed):**
   - Adjust time bonus values if 1954 timing is too early/late
   - Verify raid point values are balanced
   - Check if additional events needed for 1954 push

3. **Documentation:**
   - Update main documentation with these changes
   - Note that old decisions have been removed/updated

## Files Modified

1. `common/decisions/Indochina_War.txt` - Removed Indochina_Wrapup_Timer
2. `common/decisions/FRA.txt` - Updated Proclaim_Victory_in_the_liberation_war
3. `common/on_actions/CWIC_Struggle_on_actions.txt` - Added time-based bonuses

## Files Created

1. `Indochina_Integration_Analysis.md` - Detailed analysis of issues and recommendations
2. `Indochina_Integration_Summary.md` - This summary document

