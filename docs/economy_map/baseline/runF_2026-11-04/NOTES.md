# runF (2026-11-04): AI run 1949-1964, after runE fixes

Build: Econ-fix at 20d43f78fd (runE fixes, catch-up growth, AI surplus tax cut). The /10 revert (e50112af5a) came after this run.

## Results
- No economy script errors. No negative debt. HDI rank correlation 0.89-0.92.
- GDP/head 1950 -> 1964: JAP 15.2 -> 29.7, FRA 20.7 -> 39.9, WGR 13.5 -> 23.7, ITA 12.7 -> 21.5, USA 42.3 -> 47.4.
- Debt paid off too fast: USA 100% -> 22%, ENG 183% -> 4% of GDP by 1964.
- New tags inherit 10-1000x GDP in debt (SOM, TAF, ERI, ANG, BAD, FNL, MAL, JAM). This run is about 10x worse than runE because the /10 in cwic_transfer_state_debt had been removed; that is now restored.
- SAU debt 1 -> 135 (1963) -> 436 (1964), from an unknown large loan.

## Performance (profiler.log, not committed, 375 MB)
- Monthly 3.51 s per tick (139 ticks), ic_pulse 514 ms, daily 206 ms, hourly 42 ms. Stable over time.
- The profiler does not break down on_monthly script, so the economy share of the monthly tick is not measurable without an in-game toggle.

## Next (steps 1-4 done in 220d7c57c5, untested; step 5 open)

Measure monthly cost from the console: `set_global_flag cwic_debug_skip_econ` (and/or `cwic_debug_skip_education`), compare profiler monthly ms with and without, then `clr_global_flag`.
1. Cap inherited debt so the receiver's debt/GDP does not exceed the previous owner's (cwic_transfer_state_debt, IC_Loans_and_Interest_Rate_Effects.txt).
2. Find the 1963 SAU loan source.
3. Slow the debt payoff: faster AI tax response, or inflation eroding real debt.
4. Console flag that skips the monthly per-country economy loop, to measure its cost. Then ic_pulse tag-chain dispatch, quarterly state HDI, and moving the chemical/separatism checks out of the monthly loop.
5. Run AI to 1975, then merge Econ-fix into development-branch.
