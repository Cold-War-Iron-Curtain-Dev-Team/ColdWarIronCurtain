# Finish the CWIC Doctrine Trees

Status: **finalized for GPT-5.6-luna implementation**, reviewed 2026-09-05 against branch `tank-designer-and-doctrine-rework-test`, HEAD `034c4d0b70` and its working tree. This review changes planning documents only. Runtime acceptance remains outstanding; static inspection cannot certify engine behavior.

This document supersedes conflicting structural claims in `LogDocs/Doctrine_Rework/Land_Doctrine_Tree_Structure.md` and `LogDocs/Tank_Designer/Doctrine_Rework_Handoff.md`. Use the handoff for completed tank work, runtime instructions, and protected user files. Do not resume its unrelated tank UI backlog as part of this task.

## Outcome and scope

Finish the retained XP-unlocked technology trees: enforce land lineage and decade availability, prevent mixing independent doctrine families, preserve air's internal choices, and add regression coverage. Keep existing technology IDs, effects, costs, icons, layout, and the zero-byte modern doctrine overrides. Do not port the system, rebalance XP, assign historical country doctrines, generate art, or implement patron realignment in this pass.

A family choice is permanent during normal play. Descendant columns remain available together: NATO permits both later NATO and SADF, Warsaw permits DPRK, and the insurgency family permits its several descendants including Cuba. This is exclusivity between **11 independent families**, not between all 17 columns. No country, ideology, faction, or DLC restrictions are added.

Late independent roots remain independent: Himalayan begins in 1960, Iran in 1980, and transnational Islamist in 1990. Choosing an earlier independent family prevents switching to them later; waiting for a late root means foregoing land doctrine purchases until its date. This restrictive consequence is accepted for this completion pass, with historical realignment deferred.

## Review findings that change the draft

1. **67 lineage headers, not 61.** There are 61 same-column transitions plus six first-cell cross-column transitions. Hybrid insurgency is a change of ID prefix within the existing insurgency column, already counted among the 61. Thus 78 cells minus 11 independent roots equals 67 gated headers.
2. **All 78 cells have one root and one terminal.** Traversal of uncommented `path` edges covers all 528 land technologies exactly once: 18 six-node cells and 60 seven-node cells. The apparent 13-node Islamist cell and singleton alternative are prefix-grouping artifacts. The alternative header points to six nodes named `cw_islamist_ins_1990s_*`; those IDs must remain unchanged.
3. **The existing 60 terminal gates are not a reliable prerequisite specification.** Many name an earlier branch endpoint rather than the graph terminal. Cuba 1970 uses an OR of an earlier Foco node and its own branch endpoint. Copying that OR to the header would not express the intended lineage. Derive the new predecessor from the reviewed cell graph.
4. **The alternative Islamist terminal is currently blocked.** `cw_islamist_ins_1990s_global_operational_continuum` requires the regional Islamist 1980 node and `has_country_flag = X_TESt`. An active-content search found no setter for that flag. Under independent-root exclusivity, the regional prerequisite would also be incompatible with this root. Remove this obsolete terminal gate as specified below.
5. **Convergence does not establish full-cell completion.** Air's mutually exclusive `air_doctrine_integral_6a` and `_6b` both lead to `_7b`; the existing design relies on alternative incoming paths. Require the prior land cell's actual terminal, while preserving native within-cell path behavior. Do not add AND requirements for all branches or claim the whole prior cell must be purchased. Verify this interpretation in-game.
6. **Air already has root exclusion.** Its 13 allow blocks comprise three root exclusions and ten blocks implementing five reciprocal internal pairs. Preserve all 13. Naval has no allow blocks.
7. **XP type is domain-specific:** land uses army, air uses air, naval uses navy. All 646 nodes currently cost 100 XP each. Preserve both type and cost; 52,800 army XP is the sum of all land nodes, not a price a single mutually exclusive family can pay.
8. The two existing analysis documents contain stale conclusions. Their corrections are part of implementation documentation, not independent evidence supporting the old plan.

Local primary evidence: the three doctrine technology files, the active research GUI, installed vanilla `common/technologies/industry.txt` (native XOR examples), and `common/technologies/support.txt` (separate `dependencies` examples). No engine source was available. The official technology-modding wiki could not be retrieved during review; runtime semantics below are acceptance items, not claims of completed testing.

## Starting state and change ownership

The restored research-ledger tabs and icons are already staged, along with the two doctrine analysis documents. The tank/doctrine handoff has both staged and unstaged edits. The plan itself was untracked when this review began. Inspect `git status --short`, staged and unstaged diffs before editing; preserve unrelated changes and the existing index. HEAD in the older handoff is stale.

The restoration provides all four required pieces per folder: `doctrine = no` in `common/technology_tags/00_technology.txt`, the folder container, tab button, and normal/small node templates in `interface/countrytechtreeview.gui`. Keep technology-level `doctrine = yes` and XP fields. Handoff reports the ledger tabs and slot-free purchases have been seen working.

Delivery grouping: keep the existing restoration/art declarations as one reviewable checkpoint; deliver progression/exclusivity, validator, and corrected documentation together as a second checkpoint. Do not commit, push, reset the index, or use `git add .`. Stage only implementation-owned paths when delivering the programming work; stage mixed files by reviewed hunks. The user handles pushing. If commits are later requested, no `Co-Authored-By` or `Claude-Session` trailers.

Review baseline: military validator passes; localisation audit passes **22 SEA files**, not all doctrine localisation; unstaged `git diff --check` passes. Staged diff checking already reports trailing whitespace in the restored GUI and a blank EOF line in the icon document. These are baseline defects to clean only within restoration-owned added lines, not grounds for a repository-wide reformat.

## Implementation order and instructions for GPT-5.6-luna

### 1. Establish the cell manifest before editing script

Read `LogDocs/Doctrine_Rework/Doctrine_Cell_Manifest.md`, generated and checked during finalization. It specifies every header, graph terminal, date and intended predecessor. It is the reviewable contract, not an output that the validator may silently regenerate to agree with broken script.

Parse balanced technology and GUI blocks; ignore comments before extracting edges. `allow  = {` uses two spaces, and paths may be inline. Comments contain inactive paths: including them gives false roots and overlapping cells. Do not use prefix splitting or a regex that stops at the first closing brace.

Find the **active** `old_land_doctrine_folder` container in `countrytechtreeview.gui`, then its 78 grid anchors named `<technology>_tree`. Strip only the `_tree` suffix. Follow active outgoing paths from each anchor; require disjoint ownership, complete coverage, no cycles, one terminal per cell, and no edge crossing cells. Do not derive ownership from technology ID prefixes. The first NATO root is `cw_nato_1940s_integrated_arms_reorganization`, not a `_doctrine_header` ID.

Rows map as follows: y=172/790/1420/2050/2680/3310 correspond to 1940/1950/1960/1970/1980/1990. Columns begin x=80 and increase by 480. Same-column predecessor is the immediately preceding occupied row. The six extra first-cell parents are:

| First cell | Parent cell |
| --- | --- |
| SADF 1960 | NATO 1950 |
| DPRK 1960 | Warsaw 1950 |
| Cuba 1970 | Foco 1960 |
| Maoist 1960 | Insurgency 1950 |
| Foco 1960 | Insurgency 1950 |
| Regional Islamist 1960 | Insurgency 1950 |

Hybrid 1960 follows Insurgency 1950 in column x=6800. Follow the parent cell's **terminal**, including for Cuba, not the existing gate's target. If the checkout differs from the manifest, investigate and report the difference before regenerating edits; do not weaken expected counts to get a pass.

### 2. Replace terminal gating with header gating

Remove the 60 current land terminal `allow` blocks, then add the 67 lineage requirements on headers. This is replacement, not duplication. Removing the old blocks eliminates contradictory branch-specific prerequisites, Cuba's OR bypass, and the alternative Islamist test gate. Preserve every other field in those technologies.

Every non-independent header gets exactly one positive `has_tech = <parent terminal>` in its allow conjunction. There must be no same-cell or future-cell lineage prerequisite. Independent headers get none. Keep paths within cells; do not restore cross-decade paths, which risk assigning technologies to multiple grid boxes.

Progression policy is **terminal completion**, with the current internal branches retained. Both branches may still be purchased where no existing exclusion forbids it, but neither a new full-tree AND policy nor an early-header shortcut is introduced. This is a deliberate strengthening relative to old branch-endpoint gates. Preserve costs and effects so pacing can be assessed separately.

### 3. Add inclusive land date gates

Exactly 70 headers, every row after 1940, require the first day of their decade or later. Merge with lineage and root-exclusion checks into **one** allow block per header. Use the existing date-trigger syntax with an explicit inclusive boundary:

```text
allow = {
    has_tech = cw_nato_1940s_early_atomic_support_integration
    NOT = { date < 1950.1.1 }
}
```

This example is NATO 1950. Do not use `date > 1950.1.1`, which describes a strict boundary, or assume ahead-of-time research penalties enforce a hard date. Test the previous day and January 1. No date gates on 1940 headers. No air/naval date gates in this pass: their numeric tiers are not this decade grid.

Calendar eligibility and lineage eligibility are independent. Completing NATO 1940 in 1949 must **not** unlock NATO 1950 until 1950. At the 1980 bookmark, 1980 headers satisfy their date condition but still require their predecessors. Do not auto-grant older doctrine technologies for the later bookmark.

### 4. Enforce independent-family exclusion using the existing air pattern

Use explicit root `allow` checks as the production mechanism. Do not introduce untested 11-root XOR rendering into this wide, separate-grid layout. Native XOR exists in installed vanilla, but verifying its large-set and cross-grid behavior is unnecessary for this fix. A later UI enhancement can evaluate it separately.

For each rival root, add both checks as separate NOT clauses, conjunctively:

```text
NOT = { has_tech = <rival_root> }
NOT = { is_researching_technology = <rival_root> }
```

The 11 land roots are the manifest rows with no predecessor. Each must exclude the other ten (20 clauses), never itself or its descendants. Merge with its date gate when applicable. Do not put multiple rival tests into a single NOT whose semantics differ from the conjunction above.

Air roots are `air_doctrine_versatile`, `air_doctrine_systemic`, `air_doctrine_integral`; their existing symmetric exclusion blocks already do this. Keep them unchanged. Add the equivalent four clauses per naval root: `fleet_in_being`, `trade_interdiction`, `base_strike`.

Preserve air's internal reciprocal exclusions: systemic `5a1/5a2`, systemic `5b1/5b2`, integral `2a1/2a2`, integral `2b1/2b2`, integral `6a/6b`. Preserve all effects, tooltips, paths and AI weights. Check both purchase orders for each pair and that their downstream convergence stays reachable.

The explicit mechanism guarantees intended purchase eligibility, not XOR connecting artwork. Manual acceptance requires unavailable rival purchases and intelligible tooltips; do not promise a particular line or grey-out rendering before observing it.

### 5. Audit bypasses, compatibility and AI

Review found no exact references granting these 646 IDs in active `common`, `history`, or `events` outside their definitions. The USA focus reference to `air_doctrine_systemic` is a declared research-bonus **category**, not a technology grant; preserve it. Repeat this scan against the implementation checkout and distinguish grants from category uses, comments, localisation, and sprites. Inspect generic scripted technology grants as well, since token searches do not prove their absence.

`set_technology`, console grants, old saves, and external mods can bypass purchase prerequisites. Do not create an automatic save migration or remove owned technologies. The branch already requires fresh campaigns because of earlier tank changes. Supported progression testing uses fresh 1949 and 1980 starts, followed by saves created with this implementation. Report incompatible old ownership without claiming the new gates repair it.

Preserve AI weights in this pass and test AI advancement separately. Equal root weights may produce historically implausible choices; that is deferred historical AI design, not permission to assign countries to families by guesswork. However, failure to purchase any affordable, eligible doctrine is a runtime blocker to investigate before release. The new restrictions must apply to AI as well as the player.

### 6. Extend validation with structural and negative checks

Extend `tools/validate_military_reworks.py`; preserve all existing tank checks and the exact zero-byte override-set assertion. Its simple helpers are not a full Clausewitz parser: reuse only where nesting, comments, quoting and duplicate keys are correctly handled. Report malformed or unsupported syntax explicitly instead of silently passing it. Avoid introducing a third-party parser dependency for this bounded syntax.

Required assertions:

- Unique IDs, all path/positive prerequisite/exclusion targets defined, 528/73/45 domain counts, XP types army/air/navy and cost 100 preserved, no unintended effect or path changes against the edit baseline.
- 78 GUI land anchors, correct coordinates, 528 uniquely owned nodes, acyclic paths, exactly one root and terminal per cell, and no cross-cell path. There are **no exception cells**.
- Exactly 67 intended lineage prerequisites and 70 inclusive decade gates, each on the correct header with the correct Boolean polarity. Reject a prerequisite hidden under OR or NOT, duplicate allow blocks, extra contradictory gates, and an absent root exclusion. Compare the independently reviewed manifest, not just counts.
- No terminal allow gates remain, no active `X_TESt` requirement, and the alternative Islamist cell owns its actual seven nodes. No added dependencies that force both branches.
- Exact symmetric root exclusions for land and naval; air's three root blocks and five internal reciprocal pairs preserved semantically. Distinguish `has_tech` inside NOT from positive lineage ownership.
- Both new-game dates have a satisfiable route through each eligible family; future cells remain unavailable, descendants require their parent, siblings remain compatible. Model incoming path alternatives and allow conjunctions explicitly; label this a static model, not proof of the engine.
- All four research-ledger registration pieces remain for each folder. Scope GUI searches to the intended container so a parked legacy GUI cannot satisfy the check. Preserve icon declarations and ensure every doctrine name/description resolves in English. Existing loc_audit alone does not cover this.

Add focused negative fixtures or temporary mutation tests for the risky parser/graph checks: two-space and inline allow syntax; commented-out paths; missing/wrong/negated prerequisite; OR bypass; duplicate allow; wrong date boundary; missing reciprocal exclusion; cross-cell edge, cycle, orphan or duplicate ownership; alternative-prefix cell; restored test flag. Every malformed case must fail with the responsible ID and useful message. Do not run fixtures by modifying the user's real working tree, and do not import the current validator blindly: it executes checks at module scope.

Generation must be deterministic and idempotent, preserve original line endings and encoding, and introduce no BOM into script. A second application must produce no diff. Use structural block ranges, not global string replacement. Print the intended header/predecessor/date changes for review before writing them. Avoid committing a one-off generator unless it has a concrete maintenance purpose.

### 7. Verify and deliver

Run these after the final script/validator changes, investigating new failures rather than accepting all baseline noise:

```bash
python3 tools/validate_military_reworks.py
python3 tools/loc_audit.py --check
git diff --check
git diff --cached --check
```

Run the focused negative tests as well. Review the complete scoped diff, including staged changes. Preserve script IDs, effects, path edges, costs, and encoding; only allow blocks should change in the doctrine scripts. Clean restoration-owned whitespace separately, without rewriting unrelated lines. Localisation edits, if actually needed, are English-only ASCII text with the existing file encoding retained; no French/Japanese edits.

Update the structural analysis and append a short correction to the handoff describing the verified counts, real alternative-cell membership, actual air exclusion, and replacement of terminal gates. Do not overwrite unrelated handoff edits. Report exact checks run and clearly separate static success from runtime checks still pending.

Manual acceptance matrix (user-run unless separately instructed; do not start a slow game session automatically):

| Scenario | Expected result |
| --- | --- |
| Fresh 1949 and 1980, research ledger | All three tabs and nodes render; tooltips and XP purchase work without research slots |
| No technology, 1949 | Only eight 1940 land roots can be purchased; their children need paths; all later headers locked |
| Prior terminal owned, day before / January 1 | Next header locked before the boundary and eligible exactly on it |
| Eligible date, only prior header or incomplete route owned | Next decade remains locked until prior terminal is owned |
| One branch to a convergence purchased | Check native path behavior; terminal route remains possible without inventing all-branch AND gates |
| Each of 11 land roots, separate fresh state | Other ten roots cannot be bought; own descendants remain possible; test late roots at their valid dates |
| NATO 1950 terminal and date 1960 | Both NATO 1960 and SADF 1960 can be bought; Warsaw family cannot |
| Insurgency 1950 terminal | Maoist/Foco/Hybrid/Regional Islamist 1960 eligible by date; Cuba still needs Foco 1960 terminal and 1970 |
| Transnational alternative in 1990, no earlier family | All seven nodes reachable through internal paths, terminal requires neither regional doctrine nor test flag |
| Air/naval roots and air internal pairs | Exclusion works in both purchase orders; alternate-path downstream nodes remain reachable |
| Insufficient/exactly 100 appropriate XP | No free purchase, correct XP pool deducted, other pools untouched |
| Save/reload a newly created campaign | Ownership, gates and family exclusion persist |
| AI with enough matching XP and an eligible route | Purchases and advances without mixed independent roots or forbidden dates |
| Multiplayer, when available | Same eligibility and purchase outcome on host/client; no synchronization regression |

Do not use grant-all-research cheats to test purchase gates. If limited setup grants are needed, grant only prerequisites and then perform the tested purchase through the UI. A clean `_local/logs/error.log` cannot establish that a folder rendered or a gate worked. If runtime evidence contradicts the static path model, report a concrete reproducer and amend the validator/model before claiming completion.

## Deferred work

The 448 placeholder icons remain non-blocking; 80 land nodes have art declarations (53 original plus 27 restored). Promote art only when the texture exists. The empty special-forces box, XP balance, historical AI and patron switching remain separate work. Do not treat the artist queue as a gate for completing this implementation.

A grand-doctrine port is a future redesign requiring its own approved scope. The old numerical estimates for tracks, rewards, XP decisions and Mastery pacing are hypotheses, not implementation requirements. A NATO prototype would need isolation from production saves, consideration of double-applied effects and XP/mastery sources, small-country viability and AI, and an explicit alternative to the current validator's zero-byte override contract. Do not enable both systems in this branch as an incidental final step.
