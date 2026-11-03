# Run D: Pass 1 + post-Run C fixes, AFK as USA via human_ai, 1949.5.23 → 1960.1.1

Econ-fix at d17eafee3b. Files:
- `game.log`: 2,117 `CWIC_ECON` and 2,117 `CWIC_BUDGET` lines.
- `error.log`.
- `check_economy.txt`.

## Exit criteria (36 countries with 1949 GDP ≥ 50)
| Criterion | Run B | Run C | Run D | Met? |
|---|---|---|---|---|
| Economy errors | 0 | 879 (event target) | **0** | yes |
| Debt/GDP > 150% in 1960 | 16 | 2 | **1** (PRC 5.3×) | yes (≤ 3) |
| Median inflation, %/yr | 9.6 | 7.2 | **3.6** | yes |
| Median GDP-per-head growth | 3.7%/yr | 3.75%/yr | 3.75%/yr | – |
| HDI rank correlation 1960 | 0.88 | 0.89 | 0.88 | yes |
| Seconds per game year | 411 | 418 | **471** (440–524) | **no**; see below |

## Fixes confirmed
- **F14:** CHI (ROC) debt drops from 56 to 0 in 1952 when the mainland goes to the PRC at war, so it is repudiated.
  CHI ends at 1.13× instead of 11.4×.
- **F17 / F16:**
  - RAJ: debt/GDP 1.19× → 0.02×, growth 5.6% → 7.7%, money +576.
  - Inflation components are small everywhere. `sp` is ≤ 0.0025/month; USA's is 0.
- **F18:** DEN 0.75× → 0.12×, FIN 0.73× → 0.09× (growth 1.1% → 3.6%), SWE 1.36× → 0.60×.
  SWE's 1950 debt service of 4.6/month comes from the SWE_50s hand-built loans.

## Found in the budget log
- **Welfare fallback bug (fixed after the run).** `calc_welfare_expenditure` charged full cost (× 1) whenever the
  welfare modifier was below 0.0005, intended for countries without a welfare policy. PRC at welfare level 0, with
  other negative modifiers, crossed it: welfare cost went 0.53 → 9.2 per month. Now the fallback applies only
  without `welfare_level_value`, and the multiplier is clamped at ≥ 0.
- **PRC runs a −13/month operating deficit from 1950** (GDP 104/yr), with land 0.48, welfare 0.53, education 0.22
  and healthcare 0.14. The missing cost is not in the logged lines (candidates: navy/air, policing black ops,
  public services, subsidies, war reparations). Its 1-to-4-year IMF loans then compound: debt service is 191/month by 1960.
  This needs a full expense breakdown; Pass 2 or a follow-up.

## Speed
- 471 s per game year against 398 (Run A), 411 (B) and 418 (C).
- The economy code changed little between C and D: one extra yearly log line, a few multiplications per country
  per month, and working debt transfers (a handful of events).
- D's slowest years are 1952–53 (517–524 s), when the AI's war schedule differs from run to run.
- Run B, which ran the whole player pulse on every country, cost +3% over A. The D increase is
  more likely run-to-run war variance than the economy, but that is **not proven**. A repeat run on the same
  commit would settle it.
