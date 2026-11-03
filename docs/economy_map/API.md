# CWIC economy content API

These effects are the only supported way for focuses, events, decisions and other content to
change economy state. They live in `common/scripted_effects/IC_Financial_Scripted_Effects_for_Content.txt`
(except `cwic_change_money`, in `IC_Economic_Scripted_Effects.txt`), and they keep working when the
core is replaced in Pass 2.

All inputs are temp variables set right before the call. Temp variables live for the whole effect
block, so **set every input on every call**. Leftovers from an earlier call in the same block are read.

## Money

| Effect | Inputs | Behaviour |
|---|---|---|
| `cwic_change_money` | `money_change_temp` (billions; negative = spend) | Adds money. Spending more than the treasury holds borrows the rest through the normal lender cascade, with tooltips. Use it for **absolute** prices (weapon purchases, fixed contracts). |
| `cwic_change_money_gdp_share` | `money_change_gdp_share` (fraction of yearly GDP; negative = spend) | `money_change_temp = share × grossdomesticproduct`, then `cwic_change_money`. Use it for grants, costs and windfalls that should mean the same to every country (D3, D7). |

```
set_temp_variable = { money_change_gdp_share = -0.02 }   # 2% of yearly GDP
cwic_change_money_gdp_share = yes
```

## Debt

| Effect | Inputs | Behaviour |
|---|---|---|
| `cwic_take_loan` | `purchase_amount_temp` (billions) **or** `loan_gdp_share_temp`; `lender_temp` (1 Domestic Reserve, 2 Domestic Commercial, 3 BNP, 4 Barclays, 5 Chiyoda-Mitsubishi, 6 Credit Suisse, 7 Deutsche, 8 JPM, 9 IMF, 10 World Bank, **11 a country**); `current_index_temp` (term index for banks); for 11: `loan_interest_temp` (percent per year), `loan_years_temp`, and the global event target `cwic_loan_lender`; optional `loan_no_payout_temp = 1` | Records the loan in all five debt arrays and `currentDebt`/`currentDebtPayments`, then pays the principal into the treasury (unless no-payout). A country lender pays the principal from its own money and receives the repayments. Lenders 1–10 go through `add_loans_effect`. |
| `cwic_forgive_debt` | `debt_forgive_share_temp` (0–1); optional `debt_forgive_lender_temp` (country id: only that lender's loans); optional `debt_forgive_payer_temp = 1` with the global event target `cwic_debt_payer` | Scales the matching loans down by the share. With a payer, the payer's money pays for the forgiven amount (the "pay off a country's debt" diplomatic action). |

```
set_temp_variable = { loan_gdp_share_temp = 0.05 }
set_temp_variable = { purchase_amount_temp = 0 }
set_temp_variable = { lender_temp = 11 }
set_temp_variable = { loan_interest_temp = 2 }
set_temp_variable = { loan_years_temp = 10 }
SOV = { save_global_event_target_as = cwic_loan_lender }
cwic_take_loan = yes
```

## Policies

Step one level with the existing setters (`increase_welfare_rate`, `lower_tax_rate`, ...). Jump to a level with:

| Effect | Level variable | Range |
|---|---|---|
| `cwic_set_army_level` | `army_level_value` | 0–20 |
| `cwic_set_navy_level` | `navy_level_value` | 0–20 |
| `cwic_set_air_level` | `air_level_value` | 0–20 |
| `cwic_set_strategic_forces_level` | `strategic_forces_level_value` | 0–20 |
| `cwic_set_space_level` | `space_level_value` | 0–20 |
| `cwic_set_healthcare_level` | `healthcare_level_value` | 0–20 |
| `cwic_set_welfare_level` | `welfare_level_value` | 0–20 |
| `cwic_set_education_level` | `education_level_value` | 0–20 |
| `cwic_set_services_level` | `public_services_level_value` | 0–20 |
| `cwic_set_policing_level` | `policing_level_value` (the "cpi" policy) | 0–20 |
| `cwic_set_tax_level` | `upper_tax_level_value` | 1–19 |

Input: `policy_level_target_temp`. Each effect sets the level, the slider and exactly one idea of the
family. Never `add_ideas`/`remove_ideas` an economic `policy_*_temp_N` idea directly. To check a level,
read the variable: `check_variable = { welfare_level_value > 5 }`, not `has_idea`.

The media, religion, union, women, minorities and saga sliders are not economic. They stay on
their idea ladders and setters.

## Economic system, corruption, education

| Effect | Inputs |
|---|---|
| `step_towards_market` / `_planned` / `_public` / `_private`, `convert_to_*` | none (grid-bounded) |
| `cwic_change_corruption` | `corruption_change_temp` (CorruptionLevel is 0–1) |
| `nep_ed_increase/decrease_literate`, `_primary`, `_secondary`, `_college` (state scope) | `literate_change`, `primary_change`, `secondary_change`, `college_change` |

## Read-only outputs

See `PLAN.md` §2.1 for the published variables (GDP, GDP per head, growth, HDI, money, debt,
balance, credit rating, interest rate, inflation, ...). Read them; never write them.
