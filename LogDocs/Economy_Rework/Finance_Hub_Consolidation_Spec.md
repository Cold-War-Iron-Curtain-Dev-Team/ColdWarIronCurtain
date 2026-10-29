# Finance Hub Consolidation — Design Spec

Status: implemented on `Econ-fix`, not yet tested in game. Open questions below were
resolved as: PP costs rebalanced (recurring 15-25, switches 40-60, crisis tools 90-120);
concession authorization designed in `cwic_action_authorize_concessions`; 67 founding
gates and 201 banded signature modifiers (`CWIC_MNC_Signature_Modifiers.txt`); VIN aid
decision kept, renamed "Channel Foreign Aid into Development". Economic-system
conversions live in the Monetary tab, not Fiscal Policy (no room under the sliders).

Goal: move every player-facing economic decision into the International Finance
scripted GUI (`countryfinanceview`), with explicit effect tooltips, so economic
crisis management is a visible, deliberate loop instead of a hidden decision list.

## Decisions taken

| # | Question | Decision |
|---|---|---|
| 1 | Insurgency gate | Window opens during insurgency (reduced view). A tag leaving insurgency must end with the full, normal economy and full view. |
| 2 | Foreign capital | Sector-level invitation, then a corporation picker inside it. Each corporation may carry a signature bonus. |
| 3 | Planned economies | Opt-in. A working "Authorize Foreign Concessions" action sets `cwic_allows_foreign_concessions`. |
| 4 | AI | AI keeps using decisions, made AI-only (`visible = { is_ai = yes }`). No new monthly AI script. |

## Current-state facts this spec relies on

- Window gate: `Finance_Tab.txt:154-157` and opener `:3047-3049` require `NOT has_country_flag = active_insurgency`.
- Startup seeding is skipped for insurgents: `events/tutorial.txt:115-141`. Insurgents get
  `cwic_setup_insurgency_economy`; everyone else gets `cwic_seed_starting_inflation`,
  `cwic_seed_starting_money`, `cwic_seed_starting_fx_balance`, `cwic_seed_starting_debt`,
  stockpiles, GDP record, crisis evaluation.
- Insurgency exits only call `startup_economics` and policy refreshes, never the CWIC seeds:
  `lao_convert_to_normal_economy` (`Indochina_Theater_Effects.txt:3455`),
  `MLA_transition_to_postwar_government` (`MLA_scripted_effects.txt:341-362`), the other MLA
  `clr_country_flag = active_insurgency` sites (`:398`, `:484`, `:614`), and VIE
  (`VIE_Effects.txt:1143`). Consequence: `CWIC_inflation_mom`, `CWIC_black_market_pressure`,
  `CWIC_fx_regime` can be missing after the exit, so every monetary category whose
  visibility is `has_variable` stays hidden, and the debt-GDP graph never initialises.
- Concession flag `cwic_allows_foreign_concessions` is read in every concession block of
  `MNC_Decisions.txt` and `cwic_mnc_triggers.txt:12`, and set nowhere.
- MNC invite visibility is axis-only (`MNC_Decisions.txt:16-23`; market-socialist band
  passes). No ideology, alignment, or date check.
- MNC acceptance only raises presence tier; host effects come from sector rollups
  (`CWIC_MNC_Sector_Presence_Effects_v1.txt:170-512`, tiers at >0/5/12/20/30) and elite
  capture ideas (`:143-168`). Direct host hook is a stub (`CWIC_MNC_Effects.txt:5740`).
- Existing GUI patterns to reuse: slider buttons with `*_click_enabled` triggers and a
  15 PP cost (`Finance_Tab.txt:1917-2276`); tab switching by `show_current_*` flags
  (`:2504-2603`); dynamic lists for debts (`:2604-2700`); loan confirmation sub-window
  (`:3-147`).

## Phase 0 — Prerequisite bug fixes

1. **Shared insurgency-exit effect.** One effect, `cwic_exit_insurgency_to_normal_economy`,
   in `IC_Economy_Effects.txt`, doing: clear `active_insurgency`; run the same seeding block
   as `tutorial.txt:120-140` (factor that block into `cwic_seed_conventional_economy` and call
   it from both places); reset debt arrays; `show_finance = 0`. Every existing exit
   (LAO, MLA x4, VIE) calls it, keeping only its tag-specific axis and slider values.
2. **Concession authorization.** See Phase 3.
3. Verify VIN starting-debt seed and the June 1949 empty ledger in-game before changing
   `cwic_seed_starting_debt`.

Acceptance: an exited insurgent has `CWIC_inflation_mom`, `CWIC_black_market_pressure`,
`CWIC_fx_regime`, `Credit_Rating`, a populated GDP and debt graph after one month, and sees
every tab.

## Phase 1 — Window structure

Tabs (existing in plain, new in bold):

| Tab | Contents |
|---|---|
| Fiscal Overview | unchanged |
| Workforce Data | unchanged |
| Fiscal Policy | sliders; economic-system conversions (Rentier, etc. from `IC_Financial_Decisions.txt`) |
| Crisis View | unchanged, plus a "recommended levers" hint line per active crisis |
| **Monetary** | monetary financing on/off, seigniorage x3, tightening on/off, currency reform |
| **Markets & FX** | capital controls light/heavy, price controls, dual rate, lift; peg/float/internationalize; raids, enforcement, amnesty |
| Borrowing | unchanged; domestic bond pool shown with its office-park source |
| Current Debts | unchanged |
| **Foreign Capital** | concession authorization; 5 sector rows; corporation picker |

Insurgent (reduced) view: the window opens; only Fiscal Overview, Fiscal Policy (military
and policing sliders) and Crisis View are visible. The other tab buttons are hidden with
`NOT has_country_flag = active_insurgency`. Graph updates in `00_on_actions.txt:71-75` stay
gated until the exit effect has run.

## Phase 2 — Converting decisions to GUI buttons

Every button follows one pattern:

- `<name>_click_enabled` = the old decision `available` block + `has_political_power > cost`.
- `<name>_click` = `add_political_power = -cost`, then the old `complete_effect`.
- Tooltip loc key `<name>_tt`: current state, exact one-shot effect, ongoing monthly effect,
  unlock condition when disabled. Numbers come from the decision bodies in
  `CWIC_Capital_Controls.txt` (see table in the session breakdown).
- Timers and cooldowns that decisions provided for free (`days_remove`, 30-day raid flag,
  365-day amnesty flag) become `set_country_flag = { flag = X days = N }` checks.

The effect bodies move into shared scripted effects (`cwic_action_<name>`), called by both
the GUI button and the AI-only decision, so the two paths cannot drift.

The player-facing decision categories (`CWIC_black_market`, `CWIC_capital_controls`,
`CWIC_currency_policy`, `CWIC_fx_policy`, `economy_decisions`, `cwic_mnc_invitations`) get
`visible = { is_ai = yes }` at category level. `CWIC_global_monetary_order` (SOV only) stays
a decision.

## Phase 3 — Foreign Capital

### Concession authorization (planned economies)

- Button "Authorize Foreign Concessions": cost TBD PP; sets `cwic_allows_foreign_concessions`;
  stability and ideology-drift cost to be designed. Revocable ("Revoke Concessions"), which
  feeds the existing nationalization pressure.
- Planned economies (non-free-market axis) see only this button until authorized.

### Eligibility (replaces axis-only check)

A corporation is eligible for a host when all hold:

- host is open for investment (`cwic_mnc_country_open_for_investment`) or has authorized
  concessions;
- host passes `cwic_mnc_country_risk_ok`;
- corporation home country and host are not in opposing blocs, unless the host authorized
  concessions (design: Western MNCs need concessions in socialist hosts);
- corporation exists by the current date (per-corp `founding_year`; e.g. Nissan exporting
  abroad is not 1949).

### Sector rows and picker

- Five rows: Hydrocarbons, Mining, Agriculture, Manufacturing, Electronics. Each row shows
  current sector presence tier and tier effect, and an "Invite" button.
- "Invite" opens a picker sub-window (same pattern as the loan confirmation window) with a
  dynamic list over the eligible corporations of that sector. Each entry shows its
  signature bonus. Picking sets the existing `cwic_invite_<corp>_<sector>` variable, so the
  existing pulse (`cwic_mnc_process_invites_global`) and events `CWIC_MNC.10xx` are reused
  unchanged.
- "Any" option: weighted random eligible corporation, lower cost.

### Corporation signature bonuses

Applied while that corporation's presence in the host is ≥ 1, scaled by presence tier,
via one dynamic modifier per corporation. Examples to settle before writing data:

| Corporation | Bonus idea |
|---|---|
| Nissan, Toyota, Ford, GM, VW, Fiat, Renault | motorized/truck production efficiency, consumer goods relief |
| Shell, BP, Exxon, ... | oil extraction, fuel capacity |
| Rio Tinto, Anglo American, ... | steel/tungsten/chromium extraction |
| United Fruit, Cargill, Nestle, ... | agricultural output, food crisis relief, higher nationalization pressure |
| IBM, Siemens, Philips, ... | research speed in electronics, office productivity |

Data lives in one table per corporation (founding year, home bloc, sector, bonus modifier),
in `CWIC_MNC_Effects.txt` next to the existing per-corp definitions.

## Phase 4 — AI path

Existing decisions stay, with categories made AI-only (Phase 2) and each `complete_effect`
replaced by a call to the shared `cwic_action_<name>`. No new on_action work.

## Open questions

1. PP costs: keep decision costs as-is, or rebalance once everything is in one place?
2. Concession authorization costs and revocation consequences.
3. Final per-corporation bonus values and founding years.
4. Whether the Foreign Capital tab replaces `VIN_Accept_Foreign_Investments` or coexists.

## Verification plan

- Console: start as VIN, open each tab, click each button, confirm tooltip numbers equal the
  variable deltas.
- LAO and MLA exit paths: trigger the exit, wait one month, confirm full view and seeded
  variables.
- AI: observer run, confirm AI still takes capital-control and loan decisions.
- `error.log` clean of scripted GUI and localisation errors.
