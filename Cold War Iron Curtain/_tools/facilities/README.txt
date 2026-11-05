Historical starting experimental facilities

The catalogue in starting_facilities.csv is the maintained source of truth.
It selects representative existing research/test institutions, not every laboratory
in every country. Each entry is one level of infrastructure. It does not grant
scientists, breakthroughs, completed projects, nuclear weapons, or space modules.

Run from any directory:
  python build_starting_facilities.py
  python build_starting_facilities.py --check
  python check_starting_facilities.py

Generation uses only the Python standard library. The check script also uses
Pillow to verify map spawn coordinates against provinces.bmp.

The generator writes marked blocks inside native state history. Existing state
history, ownership, resources, victory points, and ordinary buildings are preserved.
It uses province membership and actual state IDs, not filename numbers; several
CWIC filenames are misleading. Regeneration is deterministic and can be checked
without writing.

Every facility uses the standard conditional building-history format:
  nuclear_facility = { level = 1 allowed = { has_dlc = "Gotterdammerung" } }
The enclosing dated history entry determines which bookmarks include the site.
These are starting-history changes, not scheduled construction during gameplay.
Existing saves do not receive free buildings from these history changes.

Availability dates are conservative cutoffs for a site's established capability,
not claims that the precise day is its ceremonial opening date. Some older dates
use year-end because the evidence establishes a year rather than an exact day.
Sites predating 1949 are included in both current bookmarks; later ones only
appear in the 1980 start. Countries must own their corresponding map provinces.

Current inventory with Gotterdammerung:
                   1949    1980
  United States       5       6
  Soviet Union        5       6
  United Kingdom      4       4
  France              5       5
  Canada              1       1
  Italy               1       1
  Australia           1       2
  China               0       3
  India               0       4
  Japan               0       3
  West Germany        0       4
  Israel              0       1
  South Africa        0       1
  Pakistan            0       1
  Brazil              0       1
  South Korea         0       1
  Total              22      44
Without the DLC these historical grants are absent.

The five types share a single facility slot per state in CWIC. The catalogue
therefore represents national capabilities with selected institutions rather
than stacking facilities. For example Harwell and Farnborough compete for the
same state, so Malvern represents British air/radar research. INPE represents
Brazil's research capability in the capped Sao Paulo state; IPEN is not stacked
on top. A civil nuclear research site does not imply a weapons program.

Province-scale geography is necessarily approximate. The catalogue notes these
abstractions, including NRL/DC at coastal Annapolis because the DC province is
inland, and Porton Down in the South West England research region. Locations were
cross-checked against the mod's province data and regional unit/map coordinates.
The Jiuquan launch facility is in Alshaa/Ejin northeast of Jiuquan city.

The old Soviet nuclear/air/land grants are retained with DLC conditions. The
generic Murmansk naval facility is relocated to Leningrad's established Krylov
ship-research institution; Murmansk's naval base and other buildings are retained.

Validation evaluates generated history in all four combinations of bookmark and
DLC ownership, checks the actual owning tag, rejects duplicate facilities in one
state, and checks land/coastal province requirements. It also verifies generation
is current. These are offline checks; an in-game new-campaign smoke test is still
needed to confirm engine initialization and presentation.
