# State Upgrade Notification Alert - Design Notes

Status: proposal only. Nothing in this note is implemented. All names below are suggestions.

## Goal
A minor, non-event topbar alert telling a human player that one or more automatic
state upgrades started this month (see `auto_start_state_upgrade_effect` in
`common/scripted_effects/IC_State_Decisions_Effect.txt`).

## Reference implementation to copy
- `common/scripted_guis/RCO_alert_gui.txt`: `player_context` scripted_gui with
  `parent_window_token = top_bar`, visible on a country flag, `_right_click` to dismiss.
- `interface/RCO_alert.gui`: 47x42 container at x=855 y=85.
- `common/scripted_effects/RCO_effects.txt`, `RCO_sync`: flag/array bookkeeping.

## Hook point (proposed)
Inside `auto_start_state_upgrade_effect`, right after `Start_State_Upgrade_effect = yes`:

```
ROOT = {
	if = {
		limit = { is_ai = no }
		add_to_array = { sd_auto_upgrade_started_states = PREV.id }
		set_country_flag = sd_upgrade_alert_open
	}
}
```

Scope of `PREV` must be checked; alternatively add `THIS.id` before entering ROOT.
On dismiss (`_right_click`), `clear_array = sd_auto_upgrade_started_states` and
`clr_country_flag = sd_upgrade_alert_open`.

## Tooltip (proposed)
List array entries with `GetName` (e.g. via a scripted loc or `for_each_loop` building
temp tokens). Remember the GOTCHAS rule: a variable holding a state stores
`state_id - 2^30`; never test it with `> 0`.

## Open items
- Topbar position must be checked in-game against the existing RCO / victory / food
  topbar elements.
- Icon art is needed (47x42 frame, plus hover frame if following RCO).
