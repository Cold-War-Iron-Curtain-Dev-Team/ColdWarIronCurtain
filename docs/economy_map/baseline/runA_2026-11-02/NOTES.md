# Run A: AFK as USA (human_ai), 1949.5.23 → 1959.12.18, Econ-fix at c93c0cea1a

The logs in this folder are copied from `~/.local/share/Paradox Interactive/Hearts of Iron IV/logs/`.

## Results
- **Economy data: none.** There are 0 `CWIC_ECON` lines because the logger hung off `on_yearly`,
  which HOI4 does not have. The engine fires only `on_daily`, `on_weekly` and `on_monthly`:
  the `hoi4` binary contains only those strings, and no vanilla on_action file uses `on_yearly`.
  The same dead hook meant `cwic_update_yearly_gdp_growth` never ran, so
  `CWIC_gdp_growth_yoy` / `CWIC_real_gdp_growth_yoy` (read by the macro-crisis triggers)
  stayed 0. The SDI yearly spending check never ran either.
  Fixed after this run: `CWIC_Economy_Log_on_actions.txt` now runs a per-country yearly
  tick from `on_monthly`, guarded by `cwic_last_yearly_tick = global.year`, and the SDI
  `on_yearly` block was removed from `SDI_on_actions.txt`.
- **Economy errors in error.log: none.** One unrelated warning:
  `IC_scripted_effects.txt:708 clamp_variable Unknow variable 'foreignpowerprojection'`.
  The other 3,700 lines are AI commands, music, animations and content.
- **Speed (at the game speed used for this run):** 1950–1956 averaged about 33 s per game month
  (30–37 s), from `game.log` timestamps. After mid-1957 the timestamps are too sparse to
  measure, because the IC_AFK harness retired. Use the same game speed for Run B.

## Run A must be redone
Re-run Run A with the yearly-tick fix for usable economy data. It doubles as the
first in-game test of that fix.
