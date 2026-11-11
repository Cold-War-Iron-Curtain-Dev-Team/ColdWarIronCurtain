WMD control regression checks

From the repository root:
  python "Cold War Iron Curtain/_tools/wmd/check_wmd_controls.py"

The checks parse the actual GUI/effect/localisation definitions and evaluate the
affected trigger/effect blocks in small stockpile fixtures. They cover missile
charging before reset, exact-stock launch boundaries, two-click nuclear/chemical
discard, live stock refresh, confirmation labels, cancellation and switching
between discard actions. They also check Clausewitz syntax and localisation BOM.
These are offline checks; they do not replace an in-game UI smoke test.

Discard confirmation uses one country variable: 0 = none, 1 = nuclear,
2 = chemical. The first click arms that action and changes its caption to
"Are you sure?". The second click performs it. Closing/reopening the WMD panel,
resetting the plan or switching discard actions cancels the previous action.
The existing four chemical stockpile types handled by this screen are retained.

The missile-cost fix changes deduction order only: payment happens before strike
events or the menu reset can clear missile_cost. The existing ICBM/IRBM/SRBM
selection by researched technology is retained. Choosing a stocked missile model,
binding range and payment to that model, and handling SLBM launch platforms are
separate range/inventory work; this patch does not redesign those mechanics.
