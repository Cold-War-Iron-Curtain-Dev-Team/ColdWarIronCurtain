# Land Doctrine Tree Structure

Derived from `common/technologies/land_doctrine.txt` and the
`old_land_doctrine_folder` container in `interface/countrytechtreeview.gui`.
528 technologies, 78 cells, 17 columns. The completion correction at the end of this
document records the implemented progression rules; the earlier gap analysis remains
as historical provenance.

## The grid is the design

Every cell is one bloc in one decade. **Columns are blocs** (`x = 80 + 480n`) and
**rows are decades** (`y = 172, 790, 1420, 2050, 2680, 3310` for the 1940s through
1990s). A column that starts partway down does so because that doctrine arrives
later in Cold War history; the vertical offset is meaningful, not cosmetic.

Each cell is a self-contained DAG with exactly one **root** and exactly one
**terminal**, which acts as the cell's capstone. All 78 cells have this shape. The
alternative Islamist header owns seven nodes reached through its existing
`cw_islamist_ins_1990s_*` path IDs; prefix grouping does not define ownership.

## Column lineage

Columns are **not** 17 independent choices. Continuation columns descend through a
lineage `allow` on their first cell's header, while the 11 independent root headers
exclude each other.

| Column x | Bloc | Span | Cells | Descends from |
| --- | --- | --- | --- | --- |
| 80 | `nato` | 1940s-1990s | 6 | **independent root** |
| 560 | `sadf` | 1960s-1990s | 4 | `nato` |
| 1040 | `france` | 1940s-1990s | 6 | **independent root** |
| 1520 | `israel` | 1940s-1990s | 6 | **independent root** |
| 2000 | `warsaw` | 1940s-1990s | 6 | **independent root** |
| 2480 | `dprk` | 1960s-1990s | 4 | `warsaw` |
| 2960 | `cuba` | 1970s-1990s | 3 | `foco` |
| 3440 | `prc` | 1940s-1990s | 6 | **independent root** |
| 3920 | `yugo` | 1940s-1990s | 6 | **independent root** |
| 4400 | `himalayan` | 1960s-1990s | 4 | **independent root** |
| 4880 | `non_aligned` | 1940s-1990s | 6 | **independent root** |
| 5360 | `iran` | 1980s-1990s | 2 | **independent root** |
| 5840 | `maoist` | 1960s-1990s | 4 | `ins` |
| 6320 | `foco` | 1960s-1990s | 4 | `ins` |
| 6800 | `ins` | 1940s-1990s | 6 | **independent root** |
| 7280 | `islamist_ins` | 1960s-1990s | 4 | `ins` |
| 7760 | `islamist_alt_ins` | 1990s-1990s | 1 | **independent root** |

The insurgency family is the clearest case: the `ins` column (1940s-1950s) is the
common ancestor, and `maoist`, `foco`, `hybrid_ins` and `islamist_ins` all branch
off its 1950s capstone `cw_ins_1950s_protracted_war_planning_doctrine` in the 1960s.
`cuba` then branches off `foco`. `sadf` continues `nato`, and `dprk` continues
`warsaw`. `hybrid_ins` shares the `ins` column because it is that column's own
post-1960s continuation.

## Pre-completion findings

Decade chaining exists and uses `allow = { has_tech = ... }`, **not** `path`. Note
the file writes `allow  = {` with two spaces, which defeats a naive `grep 'allow = '`.

- 53 of 61 decade transitions carry a gate.
- All 60 gates sit on the **capstone** of the later cell and require the **capstone**
  of the earlier one. None sit on a cell header.
- 7 of those gates are the cross-bloc lineage links in the table above.

## Pre-completion gaps

### 1. Eight 1940s-to-1950s gates were never written

Every column that starts in the 1940s is missing its first transition:

- `cw_nato_1950s` capstone should require `cw_nato_1940s_early_atomic_support_integration`
- `cw_france_1950s` capstone should require `cw_france_1940s_tactical_decentralization`
- `cw_israel_1950s` capstone should require `cw_israel_1940s_fragmented_command_coordination`
- `cw_warsaw_1950s` capstone should require `cw_warsaw_1940s_mechanized_exploitation_forces`
- `cw_prc_1950s` capstone should require `cw_prc_1940s_political_military_integration`
- `cw_yugo_1950s` capstone should require `cw_yugo_1940s_postwar_territorial_defense_blueprint`
- `cw_non_aligned_1950s` capstone should require `cw_non_aligned_1940s_integrated_defense_concept`
- `cw_ins_1950s` capstone should require `cw_ins_1940s_integrated_liberation_movement_framework`

### 2. Gating the capstone does not gate the cell

This is the reported bug. A gate on the capstone leaves the header and every other
node in that cell freely purchasable, so a country with no 1940s progress can still
buy most of the 1960s cell. The fix is to gate the **header** on the previous cell's
capstone; because the header is the cell's only root, that locks the whole cell.
61 headers need this (all cells except the 17 column roots).

### 3. Nothing stops taking several columns at once

There is no exclusivity between the independent roots, which is why one country can
research Integrated Arms Reorganization (NATO) and Deep Operations School (Warsaw)
side by side. The 11 independent roots are the natural exclusivity set:

- `cw_nato_1940s_integrated_arms_reorganization` (1940s)
- `cw_france_1940s_doctrine_header` (1940s)
- `cw_israel_1940s_doctrine_header` (1940s)
- `cw_warsaw_1940s_doctrine_header` (1940s)
- `cw_prc_1940s_doctrine_header` (1940s)
- `cw_yugo_1940s_doctrine_header` (1940s)
- `cw_himalayan_1960s_doctrine_header` (1960s)
- `cw_non_aligned_1940s_doctrine_header` (1940s)
- `cw_iran_1980s_doctrine_header` (1980s)
- `cw_ins_1940s_doctrine_header` (1940s)
- `cw_islamist_alt_ins_1990s_doctrine_header` (1990s)

Continuation columns do not need their own exclusivity rule; they inherit it through
their parent's lineage gate.

### 4. No date gating

There is not a single date condition in the file, so nothing but the capstone chain
stops a 1949 campaign from buying 1990s content. Each cell header wants a
`date > <decade>.1.1` alongside its lineage gate.

### 5. Two columns start mid-war with no parent

`himalayan` (1960s) and `iran` (1980s) begin partway down the grid but have no
lineage gate, so they are reachable from turn one. Either they are genuinely
independent and need only a date gate, or they are missing a parent. This is a
design decision, not a mechanical fix.

## Completion correction (2026-09-05)

The reviewed manifest in `LogDocs/Doctrine_Rework/Doctrine_Cell_Manifest.md` is now
implemented. The land tree has 78 header allow blocks: 67 direct predecessor-terminal
requirements and 70 inclusive January 1 decade gates. The eight 1940s roots have no
date gate. Himalayan, Iran, and the transnational Islamist tree remain independent
roots beginning in 1960, 1980, and 1990 respectively.

The 60 old terminal allow blocks were removed. The header gates use the graph terminal
for every predecessor, including Foco for Cuba 1970, and the alternative Islamist
terminal no longer requires the regional Islamist technology or `X_TESt`. The 11
independent roots exclude the other ten roots while descendants remain available
together within a selected family.

The path graph still covers all 528 technologies exactly once, with one root and one
terminal in every cell. `tools/validate_military_reworks.py` checks the manifest hash,
balanced active paths, GUI anchors and coordinates, allow polarity, date boundaries,
root exclusions, ledger registrations, localization, and unchanged non-allow
technology content. These are static checks; fresh-game, UI, AI, save/load, and
multiplayer acceptance remain runtime work.

## Economy note

All 528 nodes cost exactly 100 army XP, so buying the whole tree costs 52,800 XP.
Scarcity is currently the only thing discouraging cross-bloc mixing, and it is not
a rule.
