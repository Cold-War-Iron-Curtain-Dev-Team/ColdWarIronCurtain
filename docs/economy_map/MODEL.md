# CWIC economy model, Pass 2 (approved 2026-11-02)

Status: approved 2026-11-02 (decisions in §12). This file defines the formulas the new core implements. The simulator
(`_tools/economy_check/sim/`) ports exactly these formulas and is used to tune the coefficients marked
**[tune]**. Everything is monthly, and runs for every country (D2).

Notation:
- `s` = state, `c` = country, `d` = `state_development` (1–6).
- `L`, `P`, `H`, `C` = literate, primary, high-school and college shares (0–100), nested so that L ≥ P ≥ H ≥ C.
- Money in billions; GDP in billions per year.

The current formulas this replaces were extracted on 2026-11-02 from `IC_Econ_2024`, `IncomeGenerator`,
`IC_Loans_and_Interest_Rate_Effects`, `IC_Inflation_Effect`, `IC_literacy_calculations` and `IC_Consumer_Goods`.
Line references are in the extraction reports (agent transcripts `GdpChainFormulas`, `BudgetFormulas`,
`DebtInflationFormulas`, `SocialAndGoodsFormulas`).

## 0. Hard constraints

1. **Hybrid GDP anchor at the 1949 start** (decision 2026-11-02, §12.4). Countries whose 1949 GDP per head is
   already within 2× of Maddison 1950 keep today's GDP within ±10%, so fixed content amounts (D3) keep their
   meaning (USA 6,547, SOV 1,086, ENG 960, FRA 1,089, JAP 1,032, WGR 636, ...; full list in
   `baseline/runA2_2026-11-02/game.log`). Countries further off move to Maddison levels (within 1.5×).
   The gap between the formulas and the target is closed by one start factor per country,
   `cwic_start_productivity`, generated from the simulator into a startup table. GDP keeps the `Σ state output / 10` scale.
2. **Same published outputs** as PLAN §2.1, with the same names and units.
3. **Same content API** (`API.md`). Policy levels, ladders and setters are unchanged.
4. **Performance:** at most ~6 ms per country per month, i.e. today's AI-economy cost. One `every_owned_state`
   loop per country per month with ≤ 20 variable operations per state, no nested country or state loops,
   and loan loops linear in the number of loans.

## 1. State output (replaces employment, class conversion, wages)

### 1.1 Buildings and output weights

Kept from today, per building per month before productivity:

| Sector | Building | Weight `w` | Jobs per building `j` (thousand) |
|---|---|---|---|
| Civilian | industrial_complex | 2 × `M_civ` | 27d |
| Military | arms_factory | 1.25 | 9.45d |
| Naval | dockyard | 2.5 | 9.45d |
| Services | office_park | 7 × `M_ofp` | 56.7d |
| Metals | steel_factory, tungsten_factory | 1.75 each | 5.67d, 4.05d |
| Resources | resource units `R` (oil, aluminium, tungsten, steel, chromium, coal) | 0.5 per unit | 4.05d |
| Food | agri_industrial_complex, plus rubber deposits (**rubber is food in this mod**) | `0.5 × crop × farm_output_norm` per farm; 0.5 per rubber unit | 14.175 |

- `M_civ` and `M_ofp` are the market multipliers by x band (F3): 1.25/1.5/1.75 and 1.35/1.65/1.9.
- Today the "resources" line pays only for rubber (`R2`), which is food in this mod, and the food line multiplies
  by the **total resource count** (`R7`) instead of farms. Fixed (decision 2026-11-02): real resources pay per unit,
  and food output comes from farms plus rubber deposits. This shifts income towards resource and farm states;
  the simulator measures the shift.
- Building income bonuses (`*_income_bonus_drift`) multiply their sector as today.

### 1.2 Productivity

    π_s = base(d) × 1.10^Y_s × tech_c × sys_c × (1 + 0.05·infra_s) × elec_c × clamp(1 + CWIC_productivity_mult − CWIC_bm_productivity_penalty, 0.10, 1.10)

- **Years of schooling** `Y_s = (3·L + 3·P + 6·H + 4·C) / 100`. That is 3 years for literate-only, 6 for primary,
  12 for secondary and 16 for college, using the nested shares. Range 0–16.
  This replaces today's linear `(L + 1.25P + 1.75H + 3.5C)/100 × d`, which makes 20% → 60% literacy triple output
  (about 10× what wage data supports, per the stress test).
- `base(d)`: development tier as the capital/technology level, table **[tune]**. Start from `base(d) = 0.55·d`,
  chosen so that a typical 1949 state reproduces today's π.
- `tech_c = 1 + Σ` the relevant tech income bonuses (today's `industrial_park_income_bonus` etc. stay where they are).
- `sys_c`: economic-system productivity, `1 + economic_modifier_production_eff_growth` (today's grid values, §8).
- `elec_c = max(0, 1 + coal_balance / total_factories)` when coal < 0, else 1 (today's rule).

### 1.3 Labour constraint

    workforce_s = state_population_k × (1 − conscription_c) × 0.75 × workforce_ratio_drift_c
    jobs_s      = Σ_k j_k × B_k,s
    E_s         = min(1, workforce_s / jobs_s)                    (1 when jobs_s = 0)
    idle_s      = max(0, workforce_s − jobs_s)

### 1.4 State GDP contribution

    G_s = π_s × E_s × Σ_k w_k × B_k,s  +  0.2 × idle_s / 100  +  services_s

- The idle term keeps today's subsistence income (0.2 per thousand, no productivity).
- `services_s = σ × π_s × workforce_s × E_s / 100` **[tune σ]**. It stands in for today's artisan, bureaucrat,
  capitalist and rentier wages, which are added on top of factory output and make up a large share of today's GDP.
  σ is set so that constraint 0.1 holds.
- `grossdomesticproduct = Σ_s G_s / 10`, as today.
- `grossdomesticproductcapita = 1000 × GDP / max_manpower_k`, as today. The reference value 42.04 (USA 1949) stays valid.
- The state's GDP share (`cwic_gdp_state_last_month`) is still written for growth tracking and F14 debt transfers.

## 2. HDI

- **Income:** `HDI_II = clamp(ln(10·g) / 6.907, 0.001, 1)` with `g` = GDP per head. Today's formula,
  but fed the real GDP per head instead of the class-wage sum, whose denominator has no writer.
- **Education:** `HDI_EDU = (10C + 6H + 4P + 2L) / 2200`. Today's divisor is 1200, which lets the index exceed 1;
  the education-gain term is dropped.
- **Health:** life expectancy follows a Preston-style fit, calibrated on 45 country-decades in the stress test
  (mean error 2.7 years):

      LE = −0.68 + 5.1·ln(g × 228) + 0.21·L + 0.18·(year − 1950) + 0.3·(healthcare_level − 10) + biome + pollution

  `g × 228` converts game GDP per head to 1990 dollars (USA 1949: 42.04 ↔ about 9,600). The biome and pollution
  adjustments are today's tables. `HDI_LEI = (LE − 20) / 65`.
- `State_HDI = (HDI_II + HDI_LEI + HDI_EDU) / 3`. `National_HDI` is population-weighted, as today.
- Two fixes along the way: the life-expectancy "secondary" term no longer reads `college_educated`, and the dead
  `state_gni_ln_lookup_table` is deleted.

## 3. Budget (per country, monthly)

### 3.1 Revenue

    tax_c = GDP/12 × Σ_k share_k × rate_k × η_c

- The four tax ladders stay: lower, middle, corporate and upper, each with `rate = 0.05 × level`.
- `share_k` is each class's slice of GDP as a tax base **[tune]**. Start: lower 0.35, middle 0.30, corporate 0.20, upper 0.15.
- **Revenue bands** (decision 2026-11-02, §12.6). At start policy levels, total tax revenue must fall in a plausible
  tax-to-GDP band: 20–30% for countries with HDI > 0.6 that are not planned economies, 10–15% for HDI < 0.4,
  35–50% for planned economies (x < 7, state revenue), linear in between. The tuner may not leave these bands.
- `η_c = (1 − 0.5·CorruptionLevel) × (1 − CWIC_bm_tax_leak_mult) × (1 + modifier@modifier_tax_efficiacy) × cap_c × sysrev_c`.
  It replaces the Laffer/tax-avoidance curve (D5) and today's separate corruption loss line.
- **Fiscal capacity** `cap_c = clamp(cap_lo + (1 − cap_lo) × (National_HDI − h_lo) / (h_hi − h_lo), cap_lo, 1)`
  **[tune: cap_lo, h_lo, h_hi]**. Poor states collect less of what they levy (start: cap_lo 0.45, h_lo 0.30, h_hi 0.70).
  It rises as HDI rises, so fiscal capacity grows with development.
- **State revenue** `sysrev_c = 1 + ρ × max(0, 7 − economic_x_axis) / 7` **[tune ρ, start 0.8]**. In planned
  economies, state-enterprise profits flow into the budget; this separates them from market economies at the same
  ladder levels. It moves with the axis, so reforms change it.
- Pass-through, unchanged: tourism, resource exports, consumer-goods exports (§6), custom income, reparations,
  the Soviet subsidy and military subsidies.

### 3.2 Social spending

    line = GDP/12 × m_line × κ_line × (1 + m_extra)

- `m_line` = the policy's spending modifier from its ladder (0.001 at level 0, then 0.05 × level, up to 1.0 at level 20), as today.
- `κ_line` = the share of GDP the line costs at level 20 **[tune]**. Start: welfare 0.10, healthcare 0.06,
  education 0.06, policing 0.02, public services 0.04.
  A level-10 rich country then spends about 14% of GDP on these lines, close to 1950s OECD levels.
- Costs scale with GDP, not head count, so the F6 wage-price factor and the welfare fallback hack go away.
  A poor country pays poor-country prices automatically.
- `m_extra`: today's other `*_spending_modifier` sources (crisis ideas, MNC, pollution, consumer goods) keep working.

### 3.3 Military

Decision 2026-11-02 (§12.5): GDP share by policy level, plus units.

    military = GDP/12 × (m_army·κ_army + m_navy·κ_navy + m_air·κ_air + m_strat·κ_strat) + unit_upkeep

- `m_*` are the army/navy/air/strategic-forces spending modifiers from their ladders (0.05 × level).
- `κ` **[tune]**, start: army 0.04, navy 0.02, air 0.02, strategic 0.01. A level-10 peacetime country spends
  about 4–5% of GDP; mobilised countries far more. Historical anchor: USA about 5% of GDP in 1950, 14% in 1953.
- `unit_upkeep` = today's per-battalion, per-plane and per-ship pricing × `GlobalDebit` 0.28, with the F8 additions
  and F17's `(0.3 + 0.7·P)` land personnel factor (`P = clamp(g/42.04, 0.05, 1)`). It stays on top, so a large
  standing army still costs more than a small one at the same level.

### 3.4 Balance

    balance = revenue + pass-through − social − military − imports − custom_expenses − insurgency_funding − interest − principal

- `cwic_monthly_balance = balance` is the new published output (replaces `pulse_deficit` for readers).
- `currentMoney += balance`. A negative treasury borrows through the lender cascade, as today.

## 4. Debt

- **Principal-only stock.** `debtTotalsArray^i` = outstanding principal; `currentDebt = Σ principal`.
  Today the stock includes all future interest (France's 900B shows as 1,173B).
- **Payments:**
  - principal installment = `P0_i / (12 × years_i)`, stored in `debtPaymentArray^i`;
  - interest this month = `principal_i × rate_i / 12`, from `debtInterestArray^i`;
  - `currentDebtPayments` = Σ (installment + interest), as today's meaning.
  Repayments go to the lender (`debtOwnerArray`) as today. The arrays and the API stay the same, so `cwic_take_loan`
  and the F14 transfer need no content changes; their bodies switch to principal semantics.
- **Interest rate:** `Interest_Rate = table(rating) × monetary_mult × reserve_factor + inflation_premium + debt_premium`.
  The first three terms are today's.

      debt_premium = 2 × max(0, debt/GDP − safe_ratio(rating))        (percentage points)

  `safe_ratio`: 10 → 1.5, 8 → 1.0, 6 → 0.7, 4 → 0.4, 2 → 0.2 (linear between) **[tune]**.
- **Credit rating:** today's progress system stays. Its debt risk thresholds compare principal to GDP.
- **Default:** fires when debt service exceeds 35% of revenue **[tune]** for 3 consecutive months, or when
  debt/GDP exceeds today's `default_multiplier`. Restructuring is as in F5: half the principal written off,
  no demolition. Austerity uses the same test at 25%.
- **Starting debt:** today's ratios and lender profiles, recorded as principal.

## 5. Inflation

Today's pulse stays (it is afushin's capital-control and FX system), with three changes:

1. `base_infl` = the era baseline instead of a flat 0.1% a month **[tune]**:
   - 1949–1970 (Bretton Woods): 2%/yr;
   - 1971–1982: 7%/yr;
   - 1983 on: 4%/yr.
   Each is divided by 1,200 to give a monthly rate.
2. Shortage pressure reads the new `cg_shortage` (§6) directly: `sp = cg_shortage² × k_sp`.
3. `CWIC_cpi_index` is removed (D5). `CWIC_inflation_yoy_display` stays.

## 6. Consumer goods (replaces the tier matrix)

    cg_demand  = GDP/12 × δ(era, HDI)                       [tune δ: 0.15 + 0.10·National_HDI]
    cg_supply  = civilian_sector_output × χ + cg_imports     [tune χ]
    cg_shortage = clamp(1 − cg_supply / cg_demand, 0, 1)
    stability modifier = −0.18 × cg_shortage                 (today's maximum)
    cg_exports = max(0, cg_supply − cg_demand) × export_rate, sold to AI importers in deficit (trade.1)

- One stock per country instead of 4 categories × 6 tiers. The tier unlock triggers (`cwic_can_produce_cg_*`)
  become a quality factor on χ.
- AI countries both import and export, which fixes the stress test's "consumer goods never find a buyer".

## 7. Education and population

- **Education:** today's cohort pipeline and F7 penalty stay. Two changes:
  1. Each share may rise at most 2.5 points a year **[tune]**. The adult stock moves slowly; this is the cause of
     the stress test's rich-country overshoot.
  2. The pulse runs **quarterly** instead of monthly, with the yearly gain unchanged (×3 per pulse). It is the
     largest per-state script in the monthly tick.
- **Population tiers:** `state_population_category_check` runs yearly per state, from the yearly tick, so growing
  states gain tiers and slots. Today it is never called.
- Population growth: vanilla base 0.008 plus `monthly_population` modifiers, unchanged.

## 8. Economic system

Today's grid stays: x/y axes, `step_towards_*`, `convert_to_*`, `economic_modifier_*` mapped through the dynamic
modifiers, and the market multipliers (§1.1). Removed: class conversion coefficients and the capitalist/rentier wages.

## 9. History layer (D9)

Built as events and flags in the rework's own files. Values **[tune]** in the simulator:

| Shock | Date / trigger | Who | Effect |
|---|---|---|---|
| World recession | 1958 | open economies (not closed_economy) | productivity −3% for 12 months |
| Oil shock 1 | 1973.10 | oil importers / exporters | importers −5% productivity for 24 months, inflation +4 pts; exporters +resource income |
| Oil shock 2 | 1979 | same | half of shock 1 |
| Rate shock | 1981 | debt/GDP > 0.6 | lender caps ×0.25 for 36 months, spreads +4 pts |
| Planned stagnation | 1965 until a reform flag | x < 7 | productivity growth −1%/yr |
| Path events | existing focus/event flags (Great Leap, Cultural Revolution, 1978 reform, Gierek loans, II PND, Iran–Iraq war, Suez closure, Korean War procurement, MITI, Iraq literacy campaign) | the tag on that path | per event; designed with the content owners |

## 10. Calibration

The simulator reads the 1949 start (states, buildings, resources, education shares, policies, debt profiles)
and runs 1949–1989 monthly. Targets, from PLAN §6:

| Target | Today | Goal |
|---|---|---|
| 1949 GDP, hybrid anchor (§0.1) | — | near-history majors within ±10% of today; far-off countries within 1.5× of Maddison |
| Defaults among the 15, 40 years | 38 (stress test) | 0 |
| GDP-per-head growth error vs Maddison | 1.57× | ≤ 1.3× |
| 1949 GDP per head within 1.5× of Maddison | 18/53 | ≥ 35/53 |
| Rich-country social spending at level 10 | — | 10–18% of GDP |
| Tax revenue at start levels | — | inside the §3.1 bands |
| Military % of GDP, USA 1950 at start levels | ~0.25% (Run D) | 4–6% |
| Median inflation 1950s | 3.6%/yr (Run D) | 2–4%/yr |

## 11. What is removed

- Class pops, wages, conversions, `national_total_*`, `class_pop_total_*`, `theoretical_*_sum`, artisan/substinent pools.
- `tax_avoidance_function`, `generate_tax_info` averaging, the per-class tax collection loops.
- The wage-price factor for social lines and the welfare 0.0005 fallback.
- The consumer-goods T0–T5 matrix, `*DeliveryCuts`, and the per-tier export/import variables.
- `CWIC_cpi_index`, `state_gni_ln_lookup_table`, `PolicyCostCalculator`.
- `pulse_deficit` as a published output (kept as an internal name only if a reader is left).

## 12. Decisions (2026-11-02)

1. **Four tax ladders stay** (lower, middle, corporate, upper), applied to GDP shares (§3.1).
2. **Food and resource income bugs are fixed** (§1.1). Rubber is food.
3. **Quarterly education pulse accepted** (§7).
4. **Hybrid GDP anchor** (§0.1): today's GDP for countries already near history, Maddison for the rest, via a per-country start factor.
5. **Military: GDP share by policy level, plus units** (§3.3).
6. **Tax revenue anchored to plausible tax-to-GDP bands** (§3.1).
7. **Growth is validated in game, not in the simulator.** Construction, research and AI building are engine-side; the
   simulator's growth term is a stand-in, and the growth target is judged in AFK runs.
