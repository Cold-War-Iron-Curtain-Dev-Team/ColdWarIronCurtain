# Intelligence merge implementation and acceptance

The source fixes are implemented. **Native acceptance remains incomplete; this
branch must not be described as ready to merge on the evidence below.**

## Implemented behavior

- Versioned MKNAOMI/MKOFTEN migration restores earlier archive and cancellation
  meanings before mission recovery, without replaying costs or rewards.
- One calculation path combines the selected squad's traits and synergy with
  the existing mission-family probability tables. Launch saves probabilities,
  prices, duration, strength, target, and squad into the single operation slot.
- Launch guards prevent double payment, busy/injured squad use, the unfinished
  coup, and unfinished Tibet operations. Mission timeout uses the saved duration.
- Closeout consumes the saved slot once; detection applies a decaying -20 opinion
  modifier. Casualties use independent member rolls and saved exposure/reduction
  values. Recovery iterates actual squad IDs.
- GUI selection, trait, synergy, replacement, and mission changes invalidate the
  shared preview. Benefit text omits statistics with no calculation consumer.
- Shared dossier labels, GRILL FLAME amounts, card comments, a malformed trait
  assignment, and the stray 100 PP trait reward are repaired.
- Supported outcome repairs correct country targets, the infrastructure token,
  literal leader/building IDs, and actor-side technology rewards. Two references
  to nonexistent terrorist-attack events are removed; their existing numeric
  consequences remain.

## Source regression checks

Run from the repository root:

```powershell
python 'Cold War Iron Curtain/_tools/intelligence/check_merge.py'
git diff --check origin/development-branch HEAD
```

The suite executes the effect AST for migration, calculation, launch, closeout,
casualties, and recovery. It includes all 156 mission-family/risk combinations,
probability bounds, cross-squad isolation, duplicate callback/payment protection,
and legacy in-flight recovery. **These tests are not an HOI4 engine simulation
or evidence that the corresponding native interactions passed.**

## Native evidence collected on November 5, 2026

- HOI4 1.19.4.2, isolated CWIC candidate plus a disposable fixture overlay.
- Revision `60dad913125bf05c4b4a5fcffd1911c8ec5f07e7` reached the main menu and
  a fresh, paused USA campaign on May 23, 1949. The country introduction and map
  rendered.
- The corrected main-menu load had no focused MKUltra/Psychotronics/espionage
  parser errors. Earlier native parsing rejected shorthand `<=`/`>=` comparisons
  and variable building damage; those forms were repaired and regression checked.
- Country initialization then exposed two scripted espionage rule checks running
  from global scope. Their callers now enter country scope. **That final repair
  has not been retested natively.**
- The fixture overlay contains 13 assertions, but none were executed. No native
  mission, migration, casualty, save/reload, dossier-choice, or monthly-pulse pass
  is claimed.
- Computer Use subsequently reported a physical-Escape stop. Game input stopped
  and the test process was closed. The normal playset and settings were restored
  byte-for-byte; existing autosaves were backed up and restored.
- Diagnostic files and the frozen source snapshot are retained under
  `G:\CWIC-Merge-Acceptance-20261105`. `manifest.json` records the tested revision;
  `native-run-2` contains the engine logs. The fixture overlay is test-only and is
  not part of the mod's committed gameplay content.

## Remaining merge gates

1. Repeat native loading and country initialization on the final published head,
   including any concurrently integrated content. Require zero new feature-owned
   parser/runtime errors.
2. Execute native fixtures and actual UI operations for success, failure,
   detection, casualties, WIA recovery, frozen in-flight values, and single payment
   and closeout. Save and reload an active mission and completed records.
3. Load earlier dossier-save fixtures and verify that archived/cancelled files
   remain settled while active work survives reconciliation and another reload.
4. Exercise USA focus entry and dossier research, replication, report choices,
   findings, timeout, and charter closure. Inspect records-room list/detail text
   and Army records after CIA closure.
5. Test the 1949/1980 bookmarks and opt-in 1960/1970 fixtures, default/off rules,
   fictional options, and independent MKUltra/Psychotronics behavior. Run several
   monthly pulses and inspect mission/event repetition and logs.

The actual merge into `development-branch` is a separate action.
