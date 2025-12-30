# Indochina War Focus Tree Bypass Implementation

## Summary

Added bypass triggers to all Indochina War ending-related focuses in VIE and VIN focus trees. Focuses are automatically bypassed when their corresponding ending becomes available in the Struggle GUI, ensuring consistency with the GUI-centric system.

## Changes

### Bypass Triggers (`common/scripted_triggers/IC_struggle_triggers.txt`)

Created 5 new bypass triggers following the `geneva_conference_available_trigger` pattern:

- `indochina_struggle_ending_communist_victory_available_trigger` → Used by `VIN_Total_Victory`
- `indochina_struggle_ending_southern_victory_available_trigger` → Used by `VIE_BaoDai_Liberator_of_Vietnam`
- `indochina_struggle_ending_federal_vietnam_available_trigger` → Used by `VIN_Accept_French_Three_Vietnam_Federal_Scheme`
- `indochina_struggle_ending_failed_state_available_trigger` → Used by `VIN_A_Failed_State`
- `indochina_struggle_ending_never_ending_available_trigger` → Reserved for future use

### Focus Tree Updates

**VIN Focus Tree:**
- `VIN_Total_Victory` - Communist Victory bypass
- `VIN_Accept_French_Three_Vietnam_Federal_Scheme` - Federal Vietnam bypass
- `VIN_A_Failed_State` - Failed State bypass
- `VIN_Accept_Temporary_Partitions` - Geneva Conference bypass (confirmed existing)

**VIE Focus Tree:**
- `VIE_BaoDai_Liberator_of_Vietnam` - Southern Victory bypass

## Design Notes

- All ending focuses follow GUI-centric design: no direct state transfers/peace treaties in `completion_reward`
- Bypass triggers check if ending trigger is met OR war is over
- Geneva Conference focuses use `complete_effect` with `autocomplete_by_effect`
- Follow-up focuses (e.g., `VIN_Proclaim_the_Indochinese_Federation`) don't need bypass triggers

## Files Modified

1. `common/scripted_triggers/IC_struggle_triggers.txt` - Added 5 bypass triggers
2. `common/national_focus/VIN_50s.txt` - Added bypasses to 4 focuses
3. `common/national_focus/VIE_50s_Bao_Dai.txt` - Added bypass to 1 focus
4. `localisation/english/CWIC_Struggle_l_english.yml` - Added tooltip localizations
