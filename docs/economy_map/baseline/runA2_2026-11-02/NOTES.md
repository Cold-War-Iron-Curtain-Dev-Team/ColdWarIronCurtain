# Run A (valid): AFK as USA via human_ai, 1949.5.23 → 1966.1.1

Econ-fix at c93c0cea1a plus the F12 yearly-tick fix. Files:
- `game.log`, `error.log`: copies of the run's logs.
- `check_economy.txt`: full output of `_tools/economy_check/check_economy.py`.

## Harness
- F12 works: 2,998 `CWIC_ECON` lines, one per country per year (186 countries in 1949, 159 by 1966).
- No economy errors in error.log. The single core-file hit is an unrelated retired-portrait warning
  (`IC_scripted_effects.txt:19356`, SIA_sarit_thanarat).
- Speed: about 370–435 s per game year (about 33 s per game month), flat from 1950 to 1965.
- `human_ai` makes `is_ai = yes`. USA GDP stays at exactly 6547.479 for 17 years, so the
  player pulse did not run for the spectated country. Run A therefore measures the
  pure AI economy, and Run B needs the console flag.

## What the AI economy does today (evidence for F9 and Pass 2)
| Finding | Evidence |
|---|---|
| GDP changes only when the state count changes, in steps | ENG 960 → 1046 (1951) → 1112 (1952) → 1364 (1955)…; JAP flat at 1032.041 for all 17 years; USA flat |
| The checker's growth test: 0.0%/yr for most countries | USA, JAP, ITA, SWE, DEN, NOR, BEL, HOL, BRA, MEX, VEN, POL, HUN, ROM, TUR, KOR, SIA… |
| Money fills to the stipend cap (24 × base), then stops | JAP ~1,100–1,180; SOV ~1,770–1,800; ENG 1,181 from 1958 on |
| An AI with negative money never recovers: the stipend pays only when money ≥ 0 | PRC: 26 → −27 (1955) → −166.8 (1958 onward, flat) |
| Debt is frozen at its starting value: no service, no repayment | USA 7,922 → 8,578 (content in 1952), then flat; ENG 2,229.5 flat (232% of GDP) |
| Losing territory recomputes GDP but leaves the debt | CHI: GDP 203 → 0.184 in 1952, debt 63.4 kept → 34,476% of GDP. MAL: GDP 42.8 → 0.002 in 1956 → 437,400% |
| GDP ≤ 0 for stateless or micro tags | UNS (all years), the Trucial states AJM/FUJ/UMM/RAS/SAG, HUM, MUS… |
| One-year jumps come from territory changes, not growth | DRY +1254%, THO +515%, VIN +267%, VIE +231% |

## 1949 snapshot (AI values = startup values)
- HDI rank correlation with history: 0.92 in 1950, falling to 0.87 by 1965 (frozen HDI while history moved).
- Far too poor in 1949, against Maddison: SAU 64×, AFG 50×, RAJ 21×, PAK 18×, ETH 15×, PER 11×, IRQ 10×, COL 9×,
  MOR 7×, PRC 7×, POR 7×, NGA 5.5×, EGY 3.5×, NZL 3.2×, ARG 2.8×.
- Too rich: CUB 2.6×, JAP 1.8× (1950), ISR 1.7×, GRE 1.7×, IRE 1.6×.
