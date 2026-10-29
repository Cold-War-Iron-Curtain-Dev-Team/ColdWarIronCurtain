# Finance Hub Consolidation — Design Spec

Status: implemented on `Econ-fix` (commits `87bf5e76f1`, `e74578aba2`, `c3f6a4521c`,
`fa64a0158d`), not yet tested in game. This document describes the code as built.

Goal: every player-facing economic decision lives in the International Finance scripted
GUI (`countryfinanceview`) with explicit effect tooltips, so economic crisis management is
a visible, deliberate loop instead of a hidden decision list.

## Decisions taken

| # | Question | Decision |
|---|---|---|
| 1 | Insurgency gate | Window opens during insurgency (reduced view). A tag leaving insurgency ends with the full, normal economy and full view. |
| 2 | Foreign capital | Sector-level row, then a corporation picker inside it. Each corporation carries a banded signature bonus. |
| 3 | Planned economies | Opt-in. "Authorize Foreign Concessions" sets `cwic_allows_foreign_concessions`. |
| 4 | AI | AI keeps using decisions, made AI-only (`is_ai = yes` in category `visible`). No new monthly AI script. |
| 5 | Layout | One **Economic Policy** page with four sections, not separate Monetary / Markets & FX / Foreign Capital tabs. |
| 6 | PP costs | Rebalanced: recurring 15-25, switches 40-60, crisis tools 75-120. |
| 7 | VIN aid decision | Coexists with Foreign Capital; `VIN_Accept_Foreign_Investments` titled "Channel Foreign Aid into Development". |

## Phase 0 — Insurgency exit (`87bf5e76f1`)

- The start-of-game seeding block from `events/tutorial.txt` is now
  `cwic_seed_conventional_economy` (`IC_Economy_Effects.txt`): inflation, money, FX
  reserves, starting debt, stockpiles, GDP record, crisis evaluation. `tutorial.txt`
  calls it for non-insurgents; insurgents still get `cwic_setup_insurgency_economy`.
- `cwic_exit_insurgency_to_normal_economy` clears `active_insurgency`, runs
  `cwic_seed_conventional_economy`, resets debt arrays and `show_finance`.
- Callers: `lao_convert_to_normal_economy` (`Indochina_Theater_Effects.txt`), the MLA exits
  (`MLA_scripted_effects.txt`), VIE (`VIE_Effects.txt`). Each keeps only its tag-specific
  axis and slider values.

Acceptance: an exited insurgent has `CWIC_inflation_mom`, `CWIC_black_market_pressure`,
`CWIC_fx_regime`, `Credit_Rating`, a populated GDP and debt graph after one month, and sees
every tab.

Still open: verify the VIN starting-debt seed and the June 1949 empty ledger in game
before changing `cwic_seed_starting_debt`.

## Window structure

| Tab button | Page | Visible to insurgents |
|---|---|---|
| Overview | Fiscal Overview | yes |
| Employment | Workforce Data (button shown on Overview) | no |
| Fiscal / Crisis (toggle pair) | Fiscal Policy sliders / Crisis View | yes |
| Borrowing ↔ Policy (share one slot) | Borrowing / **Economic Policy** | no |
| Debts | Current Debts | no |

- Page switching uses the `show_current_*` variables; the Economic Policy page is
  `show_current_policy = 1`, container `policy_tab` in `interface/Finance_Tab.gui`
  (position `0,34`, size `624x966`).
- `Borrowing_Button` shows while not on Borrowing; `Policy_Button` replaces it while on
  Borrowing (`Finance_Tab.txt:322-324`). The Policy page is therefore reached through
  Borrowing.
- Insurgent gating: `NOT = { has_country_flag = active_insurgency }` on the Employment,
  Borrowing, Debts and Policy buttons.

## Economic Policy page (`fa64a0158d`)

Four sections, each with an `instantTextboxType` title and a set of buttons.
Every button follows one pattern in `common/scripted_guis/Finance_Tab.txt`:

- `<button>_click_enabled` = the old decision `available` block + `has_political_power`
  above cost.
- `<button>_click` = `add_political_power = -cost` then `cwic_action_<name> = yes`.
- Tooltip `<button>_tt` in `CWIC_core_l_english.yml`, format
  Cost / Gains / Drawbacks / Every month / Requires, coloured values.
- Decision timers (`days_remove`, raid 30-day, amnesty 365-day) are timed
  `set_country_flag = { flag = X days = N }` checks.

### Monetary

| Button | PP | Effect called |
|---|---|---|
| `enable_money_printing` | 15 | `cwic_action_enable_money_printing` |
| `disable_money_printing` | 15 | `cwic_action_disable_money_printing` |
| `print_money_small` | 20 | `cwic_money_print_small` |
| `print_money_medium` | 40 | `cwic_money_print_medium` |
| `print_money_large` | 90 | `cwic_money_print_large` |
| `enable_monetary_tightening` | 50 | `cwic_action_enable_monetary_tightening` |
| `disable_monetary_tightening` | 15 | `cwic_action_disable_monetary_tightening` |
| `currency_reform` | 120 | `cwic_action_currency_reform` |
| `internationalize_currency` | 120 | `cwic_action_internationalize_currency` |

### Markets & FX

| Button | PP | Effect called |
|---|---|---|
| `capital_controls_light` | 40 | `cwic_action_capital_controls_light` |
| `capital_controls_heavy` | 90 | `cwic_action_capital_controls_heavy` |
| `capital_controls_lift` | 50 | `cwic_action_capital_controls_lift` |
| `price_controls_basic` | 40 | `cwic_action_price_controls_basic` |
| `fx_controls_dual` | 75 | `cwic_action_fx_controls_dual` |
| `black_market_raids` | 20 | `cwic_action_black_market_raids` |
| `black_market_enforcement_campaign` | 60 | `cwic_action_black_market_enforcement_campaign` |
| `black_market_amnesty` | 50 | `cwic_action_black_market_amnesty` |
| `adopt_currency_peg` | 60 | `cwic_action_adopt_currency_peg` |
| `float_currency` | 25 | `cwic_action_float_currency` |

### Economic System

| Button | PP | Effect called |
|---|---|---|
| `convert_to_rentier` | 50 | `cwic_action_convert_rentier` |
| `convert_to_normal_economic_axis_system` | 50 | `cwic_action_convert_normal_axis` |
| `convert_to_petrostate` | 60 | `cwic_action_convert_petrostate` |

The `cwic_action_convert_*` wrappers (`IC_Economy_Effects.txt`) call the existing
`convert_to_*` setters. Source decisions: `IC_Financial_Decisions.txt`.

### Foreign Capital (`e74578aba2`)

- **Authorize Foreign Concessions** (40 PP): `cwic_action_authorize_concessions` sets
  `cwic_allows_foreign_concessions`, −5% stability.
- **Revoke Foreign Concessions** (free): `cwic_action_revoke_concessions` clears the flag,
  +0.5 `CWIC_nationalization_pressure_index` (capped at 5).
- **Sector rows**: hydrocarbons, mining, agri, manufacturing, electronics. Each row has
  `Foreign_Capital_Name_<sector>`, `Foreign_Capital_Tier_<sector>` (presence tier) and
  `Foreign_Capital_Browse_<sector>` (free; sets `show_fc_picker_<sector> = 1` and the
  other four to 0, so only one picker is open).
- **Picker**: `Foreign_Capital_Picker_<sector>` window, a fixed list of
  `Foreign_Capital_Pick_<corp>_<sector>` buttons (67 total). Clicking:
  - if `cwic_mnc_pick_invite_<corp>_<sector>_ok`: 25 PP, `cwic_action_invite_<corp>_<sector>`;
  - else if `cwic_mnc_pick_concession_<corp>_<sector>_ok`: 50 PP,
    `cwic_action_concession_<corp>_<sector>`;
  - then closes the picker.
  The invite path sets the existing `cwic_invite_<corp>_<sector>` variable, so
  `cwic_mnc_process_invites_global` and events `CWIC_MNC.10xx` are reused unchanged.
- **Any** (`Foreign_Capital_Any_<sector>`, 15 PP): weighted `random_list` over every
  eligible invite or concession in that sector.

#### Eligibility (`cwic_mnc_triggers.txt`)

- Invite path: host economic axis in the free-market or market-socialist band
  (`economic_x_axis >= 10` or a free-market bonus), nationalization pressure ≤ 4.5,
  corporation presence below its cap.
- Concession path: host has `cwic_allows_foreign_concessions`.
- Communist, maoist and trotskyist hosts need authorization before any corporation is
  eligible.
- Each corporation is gated on its historical foreign-operations year.

#### Signature bonuses

- `common/dynamic_modifiers/CWIC_MNC_Signature_Modifiers.txt`: three presence bands per
  corporation, `cwic_sig_<corp>_<sector>_b1/b2/b3` (presence 1-2, 3-4, 5+).
- `cwic_mnc_apply_signature_bonuses_country` (`CWIC_MNC_Effects.txt`) removes the bands
  present and adds the one matching current presence.
- Invitation cooldowns use timed `set_country_flag` (the old `clr_country_flag` with
  `days` never expired).

## AI path

Decision categories `CWIC_black_market`, `CWIC_capital_controls`, `CWIC_currency_policy`,
`CWIC_fx_policy`, `economy_decisions` and the MNC invitation categories have `is_ai = yes`
in `visible`. Each decision's `complete_effect` calls the same `cwic_action_<name>` as the
button, so the two paths cannot drift. The MNC hide/show toggle category
(`CWIC_MNC_Invitations_Toggle.txt`) was removed. `CWIC_global_monetary_order` (SOV only)
stays a player decision.

## Economic Policy page redesign

Status: implemented, not yet tested in game. The page used a bare 3-column grid of identical 148x34 buttons
with no state display. The redesign keeps every element name, click effect and
enable trigger; it changes only layout, art, labels and visibility.

### Layout (child coordinates of `policy_tab`, which sits at y=34; usable x 12-600, y 362-966)

| Panel | y range | Contents |
|---|---|---|
| Monetary Policy | 362-500 | centred title, live status line, 3x3 action grid |
| Markets & FX | 506-644 | centred title, live status line, 3x3 action grid |
| Economic System (left half) | 650-756 | title, "Current: [GetEconomyTypeTitle]", up to 2 conversion buttons |
| Policy Key (right half) | 650-756 | colour legend for the five action types |
| Foreign Capital | 762-962 | title, concession status line, Revoke at top right (when authorized) or Authorize centred under the status line (when closed), column header, five sector rows |

Panels and table cells are `iconType` siblings drawn before the buttons, each using a
pre-rendered PNG at its exact size (`panel_588x138`, `cell_166x24`, ...), so buttons stay
flat children of `policy_tab` and keep their scripted-GUI names. Do not use
`containerWindowType` backgrounds here: in game they captured clicks and ignored the
scripted-GUI `_visible` triggers, so they showed on every tab.

Help: the status lines, the Policy Key entries and the Foreign Capital
Presence/Tier/Investment headers carry plain-language `pdx_tooltip`s
(`cwic_pol_*_tt` in `CWIC_core_l_english.yml`). Per-panel info icons were tried and
dropped as visual clutter.

### Action buttons

- One 188x26 sprite per action type, each with a coloured chip on the left:
  Expand (blue), Restrict (orange), Structural (yellow), Drastic (red), Revert (grey).
  Disabled state comes from `buttonstate.lua`.
- Labels use new short keys `cwic_pol_<button>_lbl` (at most ~18 characters); the full
  name and numbers stay in the existing `_tt` tooltip.
- On/off pairs share one slot, with visibility driven by state:
  printing (`CWIC_money_printing_active`), tightening (`CWIC_monetary_tightening_active`),
  peg/float (`CWIC_fx_regime`), authorize/revoke (`cwic_allows_foreign_concessions`).

| Grid | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| Monetary | printing toggle, print small, print medium | print large, tightening toggle, currency reform | internationalize |
| Markets & FX | light controls, heavy controls, lift controls | price controls, dual rate, peg/float | raids, enforcement, amnesty |

Action type per button: Expand = start printing, print small/medium, amnesty;
Restrict = tightening on, light controls, price controls, raids, enforcement;
Structural = internationalize, dual rate, peg, float, conversions, authorize;
Drastic = print large, currency reform, heavy controls; Revert = stop printing,
tightening off, lift controls, revoke.

### Live status lines (scripted localisation in `IC_Economy_scripted_localisation.txt`)

- Monetary: printing ON/OFF, tightening ON/OFF, monthly inflation `CWIC_inflation_mom`.
- Markets & FX: controls None/Light/Heavy, FX Floating/Pegged/Reserve currency,
  black-market pressure `CWIC_black_market_pressure` (0-1, shown as %).
- Foreign Capital: concessions authorized or not, nationalization pressure
  `CWIC_nationalization_pressure_index` of 5. When `cwic_mnc_fc_rows_visible` is false
  the rows are replaced by a "closed to foreign capital" line.

### Sector rows

Sector name cell, presence track (five segments; segment k lit when
`CWIC_mnc_presence_tier_<sector> > k-1`), tier cell `N/5`, Browse button. Segments are
separate icons with visibility, not a frame-indexed sprite, to avoid frame-index
ambiguity at tier 0.

### Art

Generated PNGs under `gfx/interface/finance_policy/`, registered in
`interface/CWIC_Economy_icon.gfx`: panel and cell backgrounds, five action buttons, a
neutral button, five legend chips, presence track and lit segment.

### Company picker

- One window per sector, docked at x=622 y=78 against the Finance window, 620 wide,
  same panel style. Header: sector title, presence tier, concession status, hint.
- Two columns of 290x48 company cards (`GFX_cwic_fc_card`); the card is the existing
  `Foreign_Capital_Pick_<corp>_<sector>` button, so click effects are unchanged.
- Card: home-country flag (`[TAG.GetFlag]` set in the picker's `properties`), company
  name, cost badge (`Invite 25 PP` / `Concession 50 PP` / `Unavailable` by the two
  pick triggers), and a bonus summary at full presence (`cwic_fc_sum_<corp>_<sector>`).
- Companies are ordered by their founding gate (`date >` in the pick triggers) and
  hidden until founded, so the visible cards are always a gap-free prefix.
- Footer: Any eligible (15 PP), Close (Escape).
- Home tags are a fixed table (Shell and Unilever use HOL, Bunge ARG, Gecamines DOC).
- Hit area: each card is an `iconType` background (`cwic_fc_card_<corp>_<sector>`) under
  the flag and texts, with the pick button drawn last on top using a transparent
  290x48 sprite (`GFX_cwic_fc_card_hit`), the same pattern as the Borrowing `Open_*`
  rows. Text and icons on top of a button swallow its clicks and tooltip.
- A pending invitation (`cwic_invite_<corp>_<sector>` set) blocks both pick triggers, and
  the click falls through to the concession branch only via `else_if` on its trigger, so
  no political power is spent on a click that cannot act.
- Card state: the normal card background shows only when the pick button is enabled
  (eligible and enough PP); otherwise a grey `GFX_cwic_fc_card_dim` shows. One badge
  shows, first match wins: Invite pending (`cwic_invite_*` set), On cooldown
  (`cwic_invite_cd_*`), Fully established (presence 5), Invite 25 PP / Concession 50 PP
  (green, red when PP is short), Not eligible.

## Known gaps

- Crisis View has no "recommended levers" hint line yet.
- Borrowing does not show the domestic bond pool's office-park source.

## Verification plan

- Console: start as VIN, open each page, click each button, confirm tooltip numbers equal
  the variable deltas.
- LAO and MLA exit paths: trigger the exit, wait one month, confirm full view and seeded
  variables.
- Foreign Capital: as a communist host, confirm no corporation is eligible before
  authorization and the concession path works after it; as a free-market host, confirm
  invites respect founding years.
- AI: observer run, confirm AI still takes capital-control, MNC and loan decisions.
- `error.log` clean of scripted GUI and localisation errors.
