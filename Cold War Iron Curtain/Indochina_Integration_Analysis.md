# Indochina Integration Analysis & Recommendations

## Current Issues

### 1. Old Decisions Bypassing GUI System

**Indochina_Wrapup_Timer** (`common/decisions/Indochina_War.txt`)
- **Problem:** Hidden decision that auto-triggers after 60 days, directly calling ending effects and bypassing GUI
- **Current Behavior:** Forces an ending based on phase state, doesn't respect player choice
- **Solution:** Remove or convert to a late-game fallback (only triggers after 1957+ if no ending selected)

**Proclaim_Victory_in_the_liberation_war** (`common/decisions/FRA.txt`, VIN decision)
- **Problem:** Directly transfers states, annexes countries, signs peace treaties - bypasses GUI entirely
- **Current Behavior:** Old-style decision that resolves conflict automatically
- **Solution:** Convert to GUI trigger - unlock Communist Victory ending instead of directly resolving

**Proclaim_Victory_in_Vietnam** (FRA, commented out)
- **Status:** Already commented out (good!)
- **Note:** Keep commented out or remove entirely

### 2. 1954 Geneva Conference Timing

**Current System Analysis:**
- Starting Phase: 5 (Low Intensity)
- Target Phase for Geneva: 8 (Low Tension)
- Phase Transitions Needed: 5→6→7→8 = 3 transitions
- Points Required: 3 × 500 = 1500 de-escalation points

**Point Sources:**
- **Raids:** 1-15 points per raid (average ~3-5)
  - 14 day preparation time
  - From 1949-1954: ~130 possible raids
  - Estimated contribution: ~390-650 points
- **Border Wars:** 50 points each
  - Limited by phase < 4 requirement
  - Estimated contribution: ~200-400 points
- **Focus Trees:** Variable (need to verify)
- **Events:** Variable (need to verify)
- **Decisions:** 150 points (Geneva preparation decision)

**Problem:** Current system may not reliably reach Phase 8 by 1954 without additional mechanisms.

**Solution:** Add time-based modifiers and events to encourage 1954 timing:
1. Add daily/monthly de-escalation point bonuses starting in 1953
2. Add events in 1953-1954 that award significant de-escalation points
3. Add modifier to Geneva Conference trigger that makes it more likely in 1954

## Recommendations

### Priority 1: Remove/Update Old Decisions

1. **Update Indochina_Wrapup_Timer:** ✅ COMPLETED
   - Changed to only trigger after 1957.1.1
   - Only triggers if no ending has been selected via GUI (checks for Indochina_War_Over flag)
   - Only triggers if all Indochina countries + France are AI controlled
   - Acts as a last-resort fallback for AI-only games, not primary mechanism

2. **Update Proclaim_Victory_in_the_liberation_war:** ✅ COMPLETED
   - **Converted to automatic, invisible trigger** (removed decision entirely)
   - New scripted effect: `indochina_struggle_auto_trigger_communist_victory_preparation`
   - Automatically fires daily in `on_daily_FRA` when conditions are met
   - Conditions: VIE capitulated/doesn't exist (and no Operation Vulture) OR VIN captures Saigon (286) during full war
   - Awards significant Communist score (1500) and escalation points (200) to unlock ending
   - Uses flag `VIN_Communist_Victory_Preparation_Triggered` to fire only once
   - Unlocks Communist Victory ending in GUI (player must still select ending)
   - GUI ending handles all state changes, peace treaties, and focus completions
   - Added bypass to Communist victory trigger: Full war + VIN owns Saigon (286) OR VIN annexes VIE
   - **Prepares for future alert system** - when ending becomes available, can show popup notification

### Priority 2: Ensure 1954 Geneva Timing

1. **Add Time-Based Bonuses:**
   - Starting 1953.1.1: Add monthly de-escalation points (e.g., +10-20 per month)
   - Starting 1954.1.1: Increase bonus (e.g., +20-30 per month)
   - This ensures gradual progress toward Phase 8

2. **Add Historical Events:**
   - Dien Bien Phu event (1954.3-5): Award significant de-escalation points
   - French War Weariness events: Award de-escalation points
   - These should push toward Geneva in 1954

3. **Modify Geneva Trigger:**
   - Add date-based modifier: If date > 1954.1.1, reduce de-escalation point requirement for Geneva
   - Or: Add bonus de-escalation points if date > 1954.1.1 and phase >= 6

### Priority 3: Verify Raid System Balance

**Current Raid Point Awards:**
- Failure: +1 de-escalation (anti-commie raids)
- Limited Success: +1 escalation
- Success: +2 escalation
- Critical Success: +5 escalation

**Assessment:** 
- Raids are balanced for gradual accumulation
- Small point values prevent rapid phase changes
- System is reasonable for long-term conflict
- May need additional sources for 1954 timing

## Implementation Plan

1. ✅ Remove/update Indochina_Wrapup_Timer
2. ✅ Update Proclaim_Victory_in_the_liberation_war
3. ✅ Add time-based de-escalation bonuses in on_daily_FRA
4. ✅ Add 1954-specific events/modifiers
5. ⚠️ Test and balance point accumulation

