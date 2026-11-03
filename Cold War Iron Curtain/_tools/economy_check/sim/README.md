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
- Today's per-country start productivity (tech bonuses, grid sys_c) is not read from the mod. The sim fits `cwic_start_productivity` per country so 1949 GDP equals the hybrid start anchor (MODEL 1): today's runA2 GDP when within a factor 2 of Maddison's 1950 GDP per head (relative to the USA, USA = 42.04), otherwise Maddison's value times start population; tags without Maddison data use today's GDP. Factors and anchors are written to `out/start_productivity.csv`.
- Rubber counts as food; farms use crop = 1; coal units from the state `coal_amount`; conscription 3%; market multiplier bands x<7 / 7-13 / >=14; `closed_economy` = x<4; electricity factor 1; no biome or pollution terms in life expectancy.
- Education: literacy, primary, secondary and college shares follow the monthly pulse of `IC_literacy_calculations.txt` (gain 0.01 per education level, class factors, penalty below 0.06), run as quarterly pulses (3 monthly steps), each share capped at 2.5 pts/yr. There is no GDP-target shortcut.
- Credit rating = clamp(1 + 9.5 HDI - 2 max(0, debt/GDP - 0.8)), rate table `rate_a - rate_b*rating`, reserve factor 0.7 for the USA only. Lender profiles are reduced to 50% domestic (25 y, 3%) + 50% foreign (15 y, 4%). New loans are 10-year, one merged bucket per year.
- Revenue: four tax ladders at start levels from the startup rules, times `tax_shares`, with corruption; the subject-colony discount is not applied. Hard bands (MODEL 3.1) are enforced by tune.py. Military: army, navy and air levels = `Startup_Policy_Base`, strategic = 5 ENG/SOV, Base USA, else 0; cost = 5% of GDP per level times `mil_kappa`, plus unit upkeep from runD 1950 `land` scaled by GDP growth (default 0.3% of GDP monthly if no row). Other policy levels stay at the runD 1950 levels (fallback `4 + 8*HDI`); policing and public services at level 10.
- `oil_exporter` flag: oil production x1000 / population (thousands) >= 0.15.
- Starting treasury: StartupMoney 3.5% of GDP with the HDI/reserve multipliers.
- Technology growth (`tg_base + tg_catch * ln(USA g / g)`) stands in for construction and tech; buildings and jobs are static. Shocks of section 9 are implemented, except the path events and the planned-stagnation reform flag (PRC reform 1978 is not set).
- Inflation: era baseline + shortage^2 * k_sp + deficit term + oil shock; no FX or capital-control pulse. Civilian output for CG = all non-resource output.
