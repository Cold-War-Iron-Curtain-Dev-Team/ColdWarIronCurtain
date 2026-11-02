# Run C: Pass 1, AFK as USA via human_ai, 1949.5.23 → 1960.1.1

Econ-fix at the Pass 1 commit. Files:
- `game.log`, `error.log`: copies of the run's logs.
- `check_economy.txt`: full `check_economy.py` output.

## Errors
- 877 × `IC_Loans_and_Interest_Rate_Effects.txt:2238 invalid event target: event_target:cwic_dt_receiver`,
  plus 2 × `Unknown effect-type: save_temporary_event_target_as` (line 2199). HOI4 has no
  `save_temporary_event_target_as`, so every peaceful state transfer subtracted the debt from
  the old owner and gave nothing to the new one. **Fixed after the run** with `save_event_target_as`
  (used elsewhere in the mod, e.g. `Algerian_war_Scripted_Effects.txt:62`).
- No other economy errors.

## Exit criteria (36 countries with 1949 GDP ≥ 50)
| Criterion | Run B | Run C | Target | Met? |
|---|---|---|---|---|
| Debt/GDP > 150% in 1960 | 16 | **2** (CHI 11.4×, PRC 4.5×) | ≤ 3 | yes |
| Defaults (debt halved in a year) | none effective; the spiral was unbounded | 4 small ones in 1959 (CZE, POL, DDR, WPA) | ≈ 0 | close |
| Median inflation, %/yr | 9.6 | 7.2 | plausible (1950s ≈ 2–4) | **no** |
| Countries with negative inflation | 0 | 0 | – | – |
| Median GDP-per-head growth | 3.7%/yr | 3.75%/yr | – | – |
| HDI rank correlation 1960 | 0.88 | 0.89 | ≥ 0.85 | yes |
| Seconds per game year (1950–59 avg) | 411 | 418 | ≤ 418 (Run A 398 + 5%) | at the limit; the 877 error lines may account for part of it |

## Per country, 1960 (Run B → Run C)
- **Debt cured:**

  | Country | Debt/GDP, Run B | Debt/GDP, Run C |
  |---|---|---|
  | RAJ | 343× | 1.19× |
  | POL | 22× | 0.01× |
  | ROM | 19× | 0.01× |
  | TUR | 13× | 0.04× |
  | CZE | 10× | 0.02× |
  | YUG | 6.7× | 0.05× |
  | MEX | 5.2× | 0.05× |
  | BRA | 3.6× | 0.07× |
  | ITA | 2.6× | 0.40× |
  | WGR | 2.4× | 0.19× |

  RAJ also grows faster: 3.8%/yr → 5.6%/yr.
- **Still spiralling:**
  - PRC: debt 31 → 1,923 (GDP 429), money −157.
  - CHI: debt 63 → 1,030 (GDP 90), territory loss in 1952–53.

  Both are at war or in civil war for most of the decade; check military cost against their GDP.
- **Nordic drift:** DEN 0.75×, FIN 0.73×, SWE 1.36× debt by 1960, with low growth (DEN 1.7%, FIN 1.1%, SWE 1.0%).
  They were in surplus until about 1955, then turned to deficit. Candidate causes: F3's lower market multiplier
  (DEN, FIN and SWE are market economies), or the F15 surplus branch raising education and welfare and then never coming back down.
- **The F3 impact on rich countries is mild:** USA 3.2 → 3.4%, CAN 1.8 → 2.0%, WGR 1.4 → 1.3%.
