# runI (2026-11-04): monthly tick performance pass, AI run 1949-1950

- Monthly tick about 1.25-1.3 s average, down from 2.5-3.0 s (runF to runH). ic_pulse spike (mission completes around day 22-24) about 200 ms, down from 300-600 ms.
- Profiler, one in-game year with profiling on: monthly 25.3 s over 13 ticks (about 1.95 s each with profiler overhead), daily 117 ms, hourly 39 ms, ic_pulse 112 ms.
- error.log: 2190 lines, no entries from the files changed in this pass.

## Changes

- `CWIC_trade_exporter_lists.txt`: the monthly rebuild after `clear_array` only adds sellers (`cwic_add_own_trade_offers`). It used to run `is_in_array` and `remove_from_array` per country and list right after the clear, about 2 s of the monthly tick. Per-country membership is tracked with `in_cwic_ex_<list>` country flags instead of `is_in_array`; non-qualifying countries clear the flag. Lists have the same members in the same order.
- `NATO_scripted_effects.txt`: `NATO_apply_*_effects` only add or remove an idea when the member does not already have it or does. Removed about 15 idea changes per member per month (200-400 ms). Same ideas.
- `IC_scripted_effects.txt`: in `ic_pulse`, 1610 of 1783 blocks whose limit requires a single `tag` or `original_tag` are grouped per contiguous run under one `original_tag = X` check per tag (42 runs, 360 checks instead of 1610 full limits). Inner limits are unchanged and blocks keep their order, so the same blocks run in the same order. Blocks with an `else` branch or without a single tag key were not moved.

## Measurement notes

- Global array writes cost about 40 us each in script (5,300 `add_to_array` calls on dummy global arrays added about 200 ms). Avoid scanning or rewriting global arrays per country per month.
- The profiler does not break down `gamestate.monthly`. Monthly costs were attributed by toggling temporary `cwic_debug_skip_*` global flags; these were removed after the pass. `cwic_debug_skip_econ` and `cwic_debug_skip_education` remain.
- game.log timestamps were misleading for per-country attribution inside one monthly tick.
- Script triggers are no longer a large cost: unattributed `and`/`or`/`is_in_array` total about 2.9 s per profiled year (Indochina raid `visible` blocks about 0.6 s). One-off option spikes are engine work: `indonesia.1` 3.5 s (transfer_state, set_autonomy), `india.1` 0.4 s (set_autonomy). Left as is.
- Remaining cost is the hourly tick (about 0.9 s per game day), mostly engine AI and supply.
