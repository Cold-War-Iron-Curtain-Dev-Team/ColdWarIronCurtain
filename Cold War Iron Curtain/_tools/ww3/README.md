# WW3 campaign repair

The Soviet European mission uses live occupation predicates, not the
`European_is_Soviet` outcome flag. The daily Soviet on-action opens the
conference once the objectives are secured, and repairs campaigns loaded from
older saves without resetting an active countdown. Missing expired missions
produce their actual ending instead of granting another year.

`objectives.json` defines 17 European theatres using fixed 1949 home territory.
A theatre becomes required when its country (or listed successor) participates
against SOV. Requirements remain after capitulation and exile. Already secured
theatres reconstruct older campaigns. Austria includes all nine occupation-zone
states. Overseas territories and the listed remote islands are excluded; Denmark
retains its capital islands. This is the pre-1970 WW3 chain, not a dynamic border
system for arbitrary later scenarios.

Every province in a required state must be held by SOV, its native faction,
direct subjects, or a Warsaw Pact government whose sphere leader is SOV.
Mixed allied occupation counts, and a single enemy pocket prevents completion.
The generator reads province membership from native state history. No cached
controller arrays, moving capitals or external data are used at runtime.

The conference offers a European settlement or Operation Red Dusk. Red Dusk
requires Washington plus American defeat within 765 days. Settlements close both
missions and end Soviet bloc wars against recorded WW3 opponents. White peace
returns unfinished occupations; scripted successor governments and completed
state transfers remain. The early negotiated-ceasefire decision now has effects;
the empty paid Red Dawn placeholder is hidden. Existing deadline bonuses and
penalties retain their values and only apply once per loser during the European
mission.

Maintain generated files with:

```powershell
python "Cold War Iron Curtain/_tools/ww3/build_ww3_objectives.py"
python "Cold War Iron Curtain/_tools/ww3/build_ww3_objectives.py" --check
python "Cold War Iron Curtain/_tools/ww3/test_ww3.py"
```

The regression suite interprets the actual parsed repair scripts against
synthetic country, state, province, war and mission data. It covers every
objective province, split allied occupation, successor tags, neutral countries,
conference selection, expiry, legacy saves, global versus country flags,
settlement scope, Red Dusk outcomes, deadline adjustments, and localisation/event
references. It does not run HOI4 or prove native event scheduling, UI layout or
peace callbacks. A live-game smoke test should check these paths with an active
WW3 save: occupied Europe -> conference -> settle; conference -> continue ->
Washington and American capitulation; and each mission's expiry. Reopen the game
to load the modified scripts, then allow a daily tick for existing-save recovery.
