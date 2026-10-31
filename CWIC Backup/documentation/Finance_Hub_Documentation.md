# Finance Hub (International Finance window)

Reference for the Finance Hub: the scripted GUI `countryfinanceview` that holds every
player-facing economic decision. Built on `Econ-fix` (commits `87bf5e76f1` to `94ecf5a83a`).
In-game verification is still outstanding (see the end of this document).

For the underlying economy model (GDP, inflation, debt, credit, crisis) see
`LogDocs/Economy_Rework/Economy_System_Overview.md`.

## Files

| Purpose | File |
|---|---|
| Window layout | `interface/Finance_Tab.gui` |
| Sprites | `interface/CWIC_Economy_icon.gfx`, art in `gfx/interface/finance_policy/` |
| Buttons (click, enable, visibility) | `common/scripted_guis/Finance_Tab.txt` |
| Action effects, seeding, insurgency exit | `common/scripted_effects/IC_Economy_Effects.txt` |
| Foreign capital effects, signature bonuses | `common/scripted_effects/CWIC_MNC_Effects.txt` |
| Foreign capital eligibility | `common/scripted_triggers/cwic_mnc_triggers.txt` |
| Signature modifiers | `common/dynamic_modifiers/CWIC_MNC_Signature_Modifiers.txt` |
| Status lines | `common/scripted_localisation/IC_Economy_scripted_localisation.txt` |
| Labels and tooltips | `localisation/english/CWIC_core_l_english.yml`, `CWIC_MNC_l_english.yml` |
| AI decisions | `IC_Financial_Decisions.txt`, `CWIC_Capital_Controls.txt`, `MNC_Decisions.txt` |

## Pages

| Tab button | Page | Insurgents |
|---|---|---|
| Overview | Fiscal Overview | yes |
| Employment (on Overview) | Workforce Data | no |
| Fiscal / Crisis | Fiscal Policy sliders / Crisis View | yes |
| Borrowing / Policy (one slot) | Borrowing / Economic Policy | no |
| Debts | Current Debts | no |

- Pages switch on `show_current_*` variables. Economic Policy is `show_current_policy = 1`,
  container `policy_tab`.
- `Policy_Button` replaces `Borrowing_Button` while on Borrowing, so Policy is reached
  through Borrowing.
- Insurgents (`active_insurgency` flag) get the reduced view.

## Insurgency exit

- `cwic_seed_conventional_economy` seeds inflation, money, FX reserves, starting debt,
  stockpiles, GDP record and crisis state. `events/tutorial.txt` runs it at game start for
  non-insurgents; insurgents get `cwic_setup_insurgency_economy`.
- `cwic_exit_insurgency_to_normal_economy` clears `active_insurgency`, runs the seed,
  resets debt arrays and `show_finance`. Callers: `lao_convert_to_normal_economy`
  (`Indochina_Theater_Effects.txt`) and the MLA exits (`MLA_scripted_effects.txt`). The
  VIE-created TRP commissariat calls `cwic_seed_conventional_economy` directly
  (`VIE_create_trung_phan_commissariat`).
- New exit paths must call `cwic_exit_insurgency_to_normal_economy`, then set only their
  own axis and slider values.

## The button pattern

Every Economic Policy button follows one shape in `Finance_Tab.txt`:

```
<button>_click_enabled = { <old decision available block>  has_political_power > <cost> }
<button>_click = { add_political_power = -<cost>  cwic_action_<name> = yes }
```

- Tooltip `<button>_tt` (Cost / Gains / Drawbacks / Every month / Requires).
- Short label `cwic_pol_<button>_lbl`, at most about 18 characters.
- Old decision timers are timed flags: `set_country_flag = { flag = X days = N }`.
- The matching AI decision's `complete_effect` calls the same `cwic_action_<name>`, so
  player and AI paths cannot drift. Change the effect, never the button or decision alone.

## Economic Policy page

Panels are `iconType` siblings drawn before the buttons (see GOTCHAS: a
`containerWindowType` background catches clicks and ignores `_visible`). Buttons are
188x26 sprites colour-coded by action type: Expand (blue), Restrict (orange),
Structural (yellow), Drastic (red), Revert (grey). On/off pairs share one slot.

### Monetary (status: printing, tightening, `CWIC_inflation_mom`)

| Button | PP | Effect |
|---|---|---|
| `enable_money_printing` / `disable_money_printing` | 15 / 15 | `cwic_action_enable_money_printing` / `_disable_` |
| `print_money_small` / `_medium` / `_large` | 20 / 40 / 90 | `cwic_money_print_small` / `_medium` / `_large` |
| `enable_monetary_tightening` / `disable_` | 50 / 15 | `cwic_action_enable_monetary_tightening` / `_disable_` |
| `currency_reform` | 120 | `cwic_action_currency_reform` |
| `internationalize_currency` | 120 | `cwic_action_internationalize_currency` |

### Markets & FX (status: controls level, `CWIC_fx_regime`, `CWIC_black_market_pressure`)

| Button | PP | Effect |
|---|---|---|
| `capital_controls_light` / `_heavy` / `_lift` | 40 / 90 / 50 | `cwic_action_capital_controls_*` |
| `price_controls_basic` | 40 | `cwic_action_price_controls_basic` |
| `fx_controls_dual` | 75 | `cwic_action_fx_controls_dual` |
| `black_market_raids` / `_enforcement_campaign` / `_amnesty` | 20 / 60 / 50 | `cwic_action_black_market_*` |
| `adopt_currency_peg` / `float_currency` | 60 / 25 | `cwic_action_adopt_currency_peg` / `cwic_action_float_currency` |

### Economic System (shows `[GetEconomyTypeTitle]`)

| Button | PP | Effect |
|---|---|---|
| `convert_to_rentier` | 50 | `cwic_action_convert_rentier` |
| `convert_to_normal_economic_axis_system` | 50 | `cwic_action_convert_normal_axis` |
| `convert_to_petrostate` | 60 | `cwic_action_convert_petrostate` |

The wrappers call the existing `convert_to_*` setters.

### Foreign Capital (status: concessions, `CWIC_nationalization_pressure_index` of 5)

- **Authorize Foreign Concessions** (40 PP): sets `cwic_allows_foreign_concessions`, -5%
  stability. **Revoke** (free): clears it, +0.5 nationalization pressure (cap 5).
- **Sector rows** (hydrocarbons, mining, agri, manufacturing, electronics): name, five-segment
  presence track (`CWIC_mnc_presence_tier_<sector>`), tier `N/5`, Browse. Browse sets
  `show_fc_picker_<sector> = 1` and closes the other four.
- **Any** (`Foreign_Capital_Any_<sector>`, 15 PP): weighted random eligible invite or
  concession in that sector.
- If `cwic_mnc_fc_rows_visible` is false the rows become a "closed to foreign capital" line.

## Company picker

- One window per sector, docked right of the Finance window. Two columns of company cards,
  67 cards in total, ordered by founding year and hidden until founded.
- Card click (`Foreign_Capital_Pick_<corp>_<sector>`):
  - `cwic_mnc_pick_invite_<corp>_<sector>_ok`: 25 PP, `cwic_action_invite_<corp>_<sector>`;
  - else `cwic_mnc_pick_concession_<corp>_<sector>_ok`: 50 PP,
    `cwic_action_concession_<corp>_<sector>`;
  - then the picker closes.
- The invite path sets `cwic_invite_<corp>_<sector>` (60 for invites, 84 for concessions) and
  `cwic_has_pending_mnc_invite`. Monthly, `cwic_mnc_process_invites_global` fires at most one
  invite event (`CWIC_MNC.1000`-`1066`) per country. It keeps the pending flag while
  `cwic_mnc_has_any_invite` is true, so invites queued behind another still fire later.
- Accepting runs `cwic_corp_<corp>_invest_presence_<sector>`:
  - presence rose: the invite is cleared, sector tiers and bonuses are recomputed at once
    (`cwic_mnc_apply_sector_presence_effects_country`), and `CWIC_MNC.1100` confirms it
    with the company presence and sector tier;
  - the company lacked capital: the invite loses 12 and stays open, and `CWIC_MNC.1101`
    says so. At 0 it lapses and `1101` reports that instead.
- Declining clears the invite and sets a 180-day cooldown. One invite buys one presence
  level; re-invite after the cooldown to expand.
- The outcome events read `cwic_mnc_last_corp` (event id minus 1000), `_sector` (1-5 in row
  order), `_presence`, `_tier` and `_lapsed`. Names come from
  `CWIC_MNC_invite_outcome_loc.txt`. A new company needs a line there too.
- Badge, first match wins: Invite pending, On cooldown (`cwic_invite_cd_*`), Fully
  established (presence 5), Invite 25 PP / Concession 50 PP, Not eligible. A pending invite
  blocks both pick triggers, so no PP is spent on a dead click.
- Hit area: card background icon, flag and texts underneath, a transparent
  `GFX_cwic_fc_card_hit` button drawn last on top. Text over a button swallows its clicks.
- Home flags are a fixed table (Shell and Unilever HOL, Bunge ARG, Gecamines DOC).

### Eligibility

- Invite: host `economic_x_axis >= 10` or a free-market bonus, nationalization pressure at
  most 4.5, presence below the corporation's cap.
- Concession: host has `cwic_allows_foreign_concessions`.
- Communist, maoist and trotskyist hosts are ineligible for everything until they authorize.
- Every corporation is gated on its historical foreign-operations year.

### Signature bonuses

Three presence bands per corporation and sector, `cwic_sig_<corp>_<sector>_b1/b2/b3`
(presence 1-2, 3-4, 5+). `cwic_mnc_apply_signature_bonuses_country` removes the current band
and adds the matching one. Invitation cooldowns are timed flags.

## Crisis alert

- Topbar alert `CWIC_crisis_alert_gui` (`interface/CWIC_crisis_alert.gui`, one slot left of
  the RCO alert at `807,85`). Shown while `CWIC_active_crisis_count > 0`.
- Tooltip lists every active crisis with severity (`CWIC_crisis_alert_list`). Click opens the
  Finance window on the Crisis view. Right-click sets `CWIC_crisis_alert_dismissed`.
- `CWIC_crisis_alert_refresh` (end of `CWIC_update_active_crisis_arrays`) clears the
  dismissal when a crisis starts that was not active last month or the summed severity
  rises.

## AI

- Categories `CWIC_black_market`, `CWIC_capital_controls`, `CWIC_currency_policy`,
  `CWIC_fx_policy` and the MNC invitation categories have `is_ai = yes` in `visible`.
- `economy_decisions` stays player-visible because it also holds `SOV_Reperation_Payments`;
  its three conversion decisions are AI-only per decision. `convert_to_rentier` has
  `ai_will_do = 0` (AI never converts to rentier).
- No monthly AI script. `CWIC_global_monetary_order` (SOV) stays a player decision. The MNC
  show/hide toggle category is gone.

## Adding a button

1. Write `cwic_action_<name>` in `IC_Economy_Effects.txt` (grep `common/` first).
2. Add the element to `policy_tab` in `Finance_Tab.gui` with the sprite for its action type.
3. Add `_click_enabled`, `_click` and, for paired buttons, `_visible` in `Finance_Tab.txt`.
4. Add `<button>_tt` and `cwic_pol_<button>_lbl` (ASCII only).
5. If AI should use it, add a decision in an AI-only category calling the same effect.

## Known gaps

- Crisis View has no "recommended levers" line.
- Borrowing does not show the domestic bond pool's office-park source.

## In-game verification (outstanding)

- Start as VIN, open every page, click every button, compare tooltip numbers to variable
  changes.
- Trigger the LAO and MLA exits, wait a month: full view, seeded variables, GDP and debt
  graphs populated. Check the VIN starting-debt seed and the June 1949 empty ledger before
  touching `cwic_seed_starting_debt`.
- Communist host: nothing eligible before authorization, concessions work after. Free-market
  host: invites respect founding years.
- Observer run: AI still takes capital-control, MNC and loan decisions.
- `error.log` free of scripted GUI and localisation errors.
