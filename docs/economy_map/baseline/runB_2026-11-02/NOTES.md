# Run B: AFK as USA via human_ai with `cwic_econ_force_player_pulse`, 1949.5.23 → 1960.1.1

Econ-fix at c93c0cea1a plus F12 and the temporary Run B switch. Files:
- `game.log`, `error.log`: copies of the run's logs.
- `check_economy.txt`: full `check_economy.py` output.

## Harness
- The flag worked: USA GDP moves (6,566 → 10,268); in Run A it was flat. 2,108 `CWIC_ECON` lines for 1949–1960.
- **No economy errors.** The AI ran the player code for 10 years without a single new error-log line.
  The one core-file hit is the same unrelated retired-portrait warning seen in Run A.

## Speed: the player pulse on every country is cheap

Seconds per game year, at the same game speed as Run A:

| Year | Run A (AI path) | Run B (player path for all) |
|---|---|---|
| 1950 | 419 | 433 |
| 1951 | 423 | 443 |
| 1952 | 413 | 432 |
| 1953 | 435 | 433 |
| 1954 | 414 | 410 |
| 1955 | 386 | 396 |
| 1956 | 373 | 391 |
| 1957 | 370 | 382 |
| 1958 | 382 | 393 |
| 1959 | 370 | 398 |

On average Run B costs about **+3%** (Run A 398 s, Run B 411 s per year). The per-country economy
is not the bottleneck; AI and war are. This weakens the case for D2's "AI yearly, staggered"
(see PLAN §0).

## Results, 36 countries with 1949 GDP ≥ 50

- Median GDP-per-head growth over 1949–1960: **3.69%/yr** (Run A 0.00%).
- **The debt spiral reproduces in game.** 16 of 36 countries end above 150% debt/GDP:

  | Country | Debt / GDP 1960 |
  |---|---|
  | RAJ | 343× |
  | PRC | 173× |
  | CHI | 49× (territory) |
  | POL | 22× |
  | ROM | 19× |
  | TUR | 13× |
  | CZE | 10× |
  | YUG | 6.7× |
  | MEX | 5.2× |
  | SPR | 4.2× |
  | PHI | 4.2× |
  | BRA | 3.6× |
  | ITA | 2.6× |
  | WGR | 2.4× |
  | NOR | 1.9× |
  | BEL | 1.8× |

  The debt grows without limit. For example, RAJ 164 → 3,209 → 11,822 → 29,780 (1949/52/56/60), with money
  at −2,488. No restructuring caps it, so the default path is not stopping the spiral; check F5 and F10 here.
- **Rich countries with history debt pay it down.** USA 8,101 → 3,030; ENG 2,210 → 508; JAP 1,184 → 639; FRA 1,339 → 552.
- **Slow growers despite being solvent:** CAN 1.8%, SWE 1.7%, SAF 1.5%, CUB 1.2%. WGR grows only 1.4% (history 6.4%) while borrowing.
- **Inflation:** none negative in 1960; the median `CWIC_inflation_mom` is 0.008 (about 10%/yr), which is high.
  The stress test's "deflates forever" doesn't show here, because almost every country carries debt
  or a low rating. F1 is still a units bug.
- HDI rank correlation: 0.92 (1950), 0.86 (1955), 0.88 (1960).
- MAL / MLD territory artefacts are as in Run A (F14).
