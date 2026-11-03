# CWIC economy simulator (MODEL.md, Pass 2c)

Offline monthly simulator of docs/economy_map/MODEL.md, 1949-06 to 1989-12, all countries that own states. Python 3 stdlib only. Run from the mod root:

    python _tools/economy_check/sim/load_start.py   # parse the mod, writes start_1949.json (already cached)
    python _tools/economy_check/sim/run.py          # simulate with params_tuned.json (or --default), writes out/yearly.csv, out/report.txt
    python _tools/economy_check/sim/tune.py [secs]  # coordinate search, writes params_tuned.json and the report (default 90 s)

Files: `params.py` (every [tune] value; `TUNABLE` lists the searched ones), `model.py` (formulas), `run.py` (CSV and section 10 report), `tune.py`.
`out/yearly.csv` columns: gdp, gdp_pc, hdi, debt, debt_gdp, defaults (cumulative), inflation_pct, balance (per year), social/revenue/military % of GDP, debt service % of revenue. Stocks are 1 January values (1949 = start); flows are annualised over the months simulated that year.

## Data read from the mod
- States (`history/states`): owner, manpower (thousands of people), category, buildings, resources, education shares, with dated blocks up to 1949.5.23 applied. `state_development = 1 + N` for `popXdevN`, 1 for plain `popX` (CWIC_state_category_cache).
- Countries (`history/countries`): economic_x_axis, set variables. 1949 GDP, HDI: runA2 log. Budget levels and land cost: runD 1950 CWIC_BUDGET. Debt ratios: StartupMoney overrides, else its generic HDI ladder.

## Approximations (known)
- Today's per-country start productivity (tech bonuses, grid sys_c) is not read from the mod. The sim fits a per-country start factor `tech0` so 1949 GDP equals the target: today's runA2 GDP for the 15 stress countries (and every country without Maddison data); for other countries in the Maddison file, Maddison 1950 GDP per head relative to the USA times start population. See the spec issue in the final report: the tier table alone cannot reach +-10%.
- Rubber counts as food; farms use crop = 1; coal units from the state `coal_amount`; conscription 3%; market multiplier bands x<7 / 7-13 / >=14; `closed_economy` = x<4; electricity factor 1; no biome or pollution terms in life expectancy.
- Education cohort pipeline is not available: each share moves toward a target set by GDP per head (log scale) at `edu_rate * level/10`, capped at 2.5 pts/yr, quarterly pulses.
- Credit rating = clamp(1 + 9.5 HDI - 2 max(0, debt/GDP - 0.8)), rate table `rate_a - rate_b*rating`, reserve factor 0.7 for the USA only. Lender profiles are reduced to 50% domestic (25 y, 3%) + 50% foreign (15 y, 4%). New loans are 10-year, one merged bucket per year.
- Military cost = runD 1950 `land` value scaled by sim GDP growth (default 0.3% of GDP monthly if a country has no row). Pass-through lines other than CG exports are zero. Policy levels stay at the runD 1950 levels (fallback `4 + 8*HDI`); policing and public services at level 10.
- Starting treasury: StartupMoney 3.5% of GDP with the HDI/reserve multipliers.
- Technology growth (`tg_base + tg_catch * ln(USA g / g)`) stands in for construction and tech; buildings and jobs are static. Shocks of section 9 are implemented, except the path events and the planned-stagnation reform flag (PRC reform 1978 is not set).
- Inflation: era baseline + shortage^2 * k_sp + deficit term + oil shock; no FX or capital-control pulse. Civilian output for CG = all non-resource output.
