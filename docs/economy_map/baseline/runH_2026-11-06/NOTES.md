# runH (2026-11-06): AI run 1949-1961, build ea1acbfe82

- Monthly tick 3011 ms average (profiler, 140 ticks), down from 3466 ms in runG. ic_pulse 481 ms, daily 180 ms, hourly 40 ms.
- Debug toggle `cwic_debug_skip_econ`: economy costs about 500 ms of the monthly tick (3077 ms -> about 2500 ms with the flag on).
- Economy: majors unchanged by the 3-month AI rotation; LAO and COG fixed; MAL keeps about half its debt after MLA wins (transfer base fix d7e3b07262, untested; accepted as an alt-history edge case).
- Runs finished. Econ-fix is not merged yet; the next work is general performance (non-economy monthly ~2.5 s, ic_pulse tag chains, trigger-heavy decisions).
