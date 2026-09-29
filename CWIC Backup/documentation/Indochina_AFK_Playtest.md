# Indochina Combined Smoke and Historical-AI Playtest

## Purpose

This is the engine-acceptance protocol for the VIN/FRE First Indochina War
rework after the 23 August corrective pass. Because tester availability is
limited, the former targeted smoke pass and the 1949-to-Geneva `human_ai` run
are combined into one game.

The run has three jobs:

1. Reject parser, event, mission, Geneva, or campaign-cleanup regressions as
   early as practical.
2. Continue through the complete historical sequence to collect comparable AI,
   balance, force-health, and Struggle evidence.
3. Produce one preserved `game.log`, one preserved `error.log`, and a short
   observation record from which the next fix pass can be scoped.

This is an observational acceptance run. Do not use console effects to force
campaign results, focus completion, control changes, wars, peace, resources, or
Geneva. Branches that historical AI does not naturally reach are marked **not
covered**, not failed, and may be checked later with the existing diagnostics.

## Build under test

Before launching, record:

- date and tester;
- current commit from `git rev-parse --short HEAD`;
- branch name;
- whether historical focuses are enabled;
- any non-rework local modifications active in the mod;
- game and mod version shown by the launcher.

The run must use a fresh 1949 start. Do not reuse a save created before the
current corrective pass.

Static preflight from the repository root:

```bash
git status --short --branch
git diff --check
python3 tools/loc_audit.py --check
```

Expected preflight result:

- no whitespace errors from `git diff --check`;
- `OK - 22 SEA loc file(s) clean.`;
- unrelated dirty files are recorded and preserved rather than reverted.

## Preserve the previous evidence

Launching HOI4 again replaces its live logs. Before launch, copy the existing
`game.log` and `error.log` to names that include the date and `pre-corrective`
or otherwise place them outside the live log location. Do not overwrite the 23
August baseline.

After this run, preserve the new files with names containing:

- the test date;
- the short commit;
- `combined-human-ai`;
- `game` or `error`.

Do this before launching HOI4 a second time.

## Game setup

1. Launch with debug logging enabled and the current local CWIC build.
2. Start the 1949 bookmark with historical AI focuses enabled.
3. Select metropolitan France (`FRA`) as the observer country.
4. Open the console and enter `human_ai` once so the selected country is AI
   controlled. Do not also use `observe`; the passive validation carrier is
   already attached to France's daily tick.
5. Run at the fastest stable speed. Pausing to inspect the map, decisions,
   diplomacy, or logs is allowed. Do not issue orders or select outcomes.

The observer in
`common/scripted_effects/IC_Indochina_AFK_Validation_Effects.txt` is passive. It
logs state but does not select options, repair invariants, transfer territory,
make peace, or determine results.

## Opening smoke gate

Within the first few in-game days, confirm `game.log` contains:

```text
IC_AFK|START|...|mode=passive_production_observer
```

Check the live `error.log` once after initialization. The following corrected
defects must not recur:

- rejected `political_power > 49` in the Northwest-recovery focus;
- rejected rework-local `defender_modifier` entries;
- `SWF_VIN.17` reporting no valid option in NLF scope;
- missing Siam focus completions from the Indochina flavor event;
- undefined `vin_ai_prepare_campaign`;
- invalid Geneva cleanup ideas;
- duplicate MEO Ho Chi Minh Thought role;
- missing Pathet Lao truck variant;
- missing `LAO_50s_Refuse_to_Demobilize` icon.

### Stop immediately

Stop the combined run and preserve both logs if any of these occurs:

- crash, failed scenario load, or repeated script exception that prevents play;
- no `IC_AFK|START` record after several game days;
- a parser error in a rework-local focus, event, mission, trigger, effect,
  modifier, GUI, or localization file that invalidates the feature being tested;
- `IC_AFK|FAIL` for a core lifecycle invariant;
- a vanilla peace conference involving an Indochina theatre tag before scripted
  Geneva/theatre closure;
- a campaign or operation becomes permanently stuck and blocks the historical
  sequence;
- Geneva convenes after a communist Dien Bien Phu victory without VIN receiving
  and resolving its explicit strategy choice.

Report and continue through Geneva when the problem is balance, AI allocation,
pacing, poor objective defense, excess force loss, or an undesirable but
terminating campaign result. Those are primary outputs of this run.

## Combined observation schedule

Exact dates vary. Use the operation/campaign launch, result, and briefing
records in `game.log` as the checkpoint markers.

### Startup and Cao-Bac

Confirm:

- THO exists when Cao-Bac launches;
- both `THO_Cao_Bang_garrison_present` and
  `THO_Lang_Son_garrison_present` report `PASS`;
- the campaign includes only the intended French-aligned participant;
- VIN's retired hidden AI combat packages remain absent;
- campaign armistice and marker cleanup complete after the result.

Record the result and completion day.

### Vinh Yen, Mao Khe, Day River, and Hoa Binh

At each launch, note whether defenders are visibly present on or immediately
covering the exact objectives. Record whether VIN assembles and attacks rather
than remaining idle beside a favorable objective.

Required lifecycle checks:

- the exact objective marker activates and later clears;
- each campaign records exactly one terminal result;
- the temporary war ends without a vanilla peace conference;
- no stale response, commitment, or campaign idea survives cleanup;
- Hoa Binh's Amarante/hold response is result-dependent and does not take
  ownership of the parent campaign's territory or peace.

Record outcome and elapsed days for all four campaigns.

### Northwest, Lorraine, MEO, Na San, and Laos

Observe and record:

- campaign forces prioritize the Northwest corridor rather than Lai Chau raid
  outposts or unrelated fronts;
- MEO visibly retains or recovers a Ha Giang defense;
- VIN does not enter state `671` before the named Dien Bien Phu campaign;
- Lorraine's visible intelligence mission/briefing appears, then records its
  posture-independent public result and clears;
- Na San is defended at launch and uses its exact objective;
- LOS/LAO allocate meaningful forces to Luang Prabang rather than abandoning
  the capital while stacking province `13738`;
- a Pathet Lao raid reaches a terminal result and does not strand either timer;
- no CEFEO limited operation commits while `Laos_Raid_Active` is set.

Northwest recovery campaign `9` is naturally conditional. If historical AI does
not enter it, mark it **not covered**. If it does enter, require a one-time
attempt, exactly one terminal result, and cleanup of every newly introduced FRE
or TAI war while preserving wars that predated recovery.

### Hirondelle

This is the most important mid-run smoke contract. Confirm that Operation
Hirondelle:

- presents as an airborne cache-destruction/interdiction raid;
- creates no FRE-VIN war;
- transfers no province or state;
- uses its visible mission and intelligence briefing;
- records one terminal result;
- clears its active flag, mission, AI allocation, and commitment package;
- applies equipment/Campaign Supply losses only on the appropriate success
  result.

If the focus is bypassed by theatre timing, mark the contract **not covered**.

### Mouette and Brochet

Confirm Mouette:

- creates only its isolated FRE-VIN operation war;
- concentrates on Phu Nho Quan and the southern Red River Delta sector;
- does not pull either side onto the VIE front or the Hoa Binh corridor;
- applies and clears the exact-envelope penalty correctly;
- transfers no territory and ends only the war it owns;
- records one terminal result and cleans all temporary state.

Brochet was accepted in the previous run. Treat it as a regression check only:
it must retain its exact objective, participant isolation, terminal result, and
owned-war cleanup. Do not reinterpret an unfavorable Brochet outcome as a code
failure when the lifecycle remains correct.

### Castor, Pollux, Atlante, and Dien Bien Phu

Record focus completion, package launch, and result dates so the preparation
windows are measurable.

Confirm:

- Castor and Pollux occur early enough to provide a usable preparation window;
- Castor establishes and fortifies the airhead without transferring territory,
  ending a war, or writing the parent Dien Bien Phu/Geneva outcome;
- Pollux resolves before campaign `3`, or is cleanly superseded without changing
  the parent campaign clock or result;
- Atlante remains ownership-, peace-, campaign-, and Geneva-neutral and cleans
  up if superseded;
- the supported camp/holdout modifiers appear without parser errors;
- VIN maintains a bounded Hanoi/Tonkin reserve instead of ignoring deep CEFEO
  penetration while concentrating on the camp;
- the Dien Bien Phu siege begins only after the approach-plus-ring investment;
- campaign `3` records its defensive response before the parent battlefield and
  Geneva result, then cleans all attached packages.

Balance target: Dien Bien Phu should last materially longer than the previous
30-day result. A short but correctly terminating siege is a balance failure to
record and continue, not an early-stop lifecycle failure.

### Post-Dien Bien Phu strategy and Geneva

After a communist capture of the camp, the required order is:

1. `IC_AFK|POST_DBP|...|stage=briefed`;
2. one explicit VIN strategy result—historically negotiations, alternatively
   southern escalation;
3. any shared pursuit path attempting to advance first logs
   `GENEVA_SOURCE|DEFERRED|...|reason=VIN_post_DBP_choice_unresolved`;
4. negotiations may queue Geneva but must still wait for the existing
   Hanoi/Saigon peace gate;
5. only after the choice and peace gate may invitation/conference records
   appear.

Failure conditions:

- Geneva invitation, auto-resolution, panic resolution, or conference start
  precedes the VIN strategy choice after a communist camp victory;
- the strategy latch accumulates leverage while it is supposed to defer;
- negotiations bypass the Vietnamese peace gate;
- escalation accidentally annexes NLF, creates the 1960s `Vietnam_War` state,
  or calls France/CEFEO into its direct VIN-VIE war.

Inspect “The Wars Behind the Table” at or before Geneva if practical. It should
show current Struggle standings, Geneva leverage, every recorded VIN campaign,
the named CEFEO operation journal, and response results using clean/costly/
failure/withdrawal/superseded language rather than raw tags or internal IDs.

### Southern-war and force-health balance

Use `FORCE_HEALTH`, `ARMY_CAP`, and placement records to compare VIE and NLF.
Record:

- VIE and NLF divisions at each 180-day heartbeat;
- whether NLF retains a useful field force through Dien Bien Phu/Geneva;
- whether the bounded reconstitution spirit/cache operates without creating an
  unlimited force or merging the northern and southern wars;
- whether VIE remains far above its intended division cap/build relationship;
- whether unrelated CEFEO crown-domain armies survive until their scripted
  territorial endings rather than being consumed on other commands' fronts.

NLF collapsing again while VIE grows into the prior 34-38 division range is a
balance failure. Continue the run so the settlement and final score remain
auditable.

### Struggle and leverage

Do not tune from one intermediate snapshot. Preserve:

- every `IC_AFK|SCORE_DELTA` line;
- six-month `STRUGGLE_SCORE`, `GENEVA_LEVERAGE`, and `GENEVA_WEIGHT` lines;
- `SCORE_AWARD` and `GENEVA_SOURCE` lines;
- the final balance and delegate weights.

The working balance target is a Communist margin of approximately `+100` to
`+200` at the historical settlement, with Hanoi's delegate weight comparable in
scale to Saigon and France. A result outside the band is evidence for the next
balance pass, not proof that the lifecycle failed.

## End point

The primary endpoint is:

```text
IC_AFK|END|...|result=scripted_Geneva_concluded
```

After this appears, continue for at least 30 in-game days so delayed campaign,
operation, faction, mission, NUN, and CEFEO cleanup can run. Stop sooner only if
the game crashes or becomes unplayable. If scripted Geneva never occurs,
continue until the historical route is clearly stalled, record the blocking
state, and preserve the logs.

## Post-run extraction

After closing the game and preserving the logs, run these from the repository
root against the copied files. Substitute their actual filenames.

```bash
rg -n "IC_AFK\|FAIL|No valid option|defender_modifier|political_power > 49|vin_ai_prepare_campaign" <game-log> <error-log>
rg -n "IC_AFK\|(START|LAUNCH|RESULT|PASS|END|FINAL_BALANCE|POST_DBP|NUN_POSTWAR)|GENEVA_SOURCE" <game-log>
rg -n "IC_AFK\|(STRUGGLE_SCORE|SCORE_DELTA|GENEVA_LEVERAGE|GENEVA_WEIGHT|FINAL_GENEVA_WEIGHT|FORCE_HEALTH|ARMY_CAP)" <game-log>
rg -n "error|invalid|unknown|unexpected token|No valid option" <error-log>
```

Do not report the whole `error.log` as a rework failure. Separate findings into:

1. rework-local regression;
2. adjacent Indochina/SEA regression;
3. known global entity, animation, generic AI-command, or unrelated mod noise.

## Checkoff sheet

Use `PASS`, `FAIL`, or `NOT COVERED` for each line.

Completed 2026-09-28 from the 2026-09-02 AFK run (`_local/logs/game.log` and
`error.log`, 1949-05-23 to 1956-09-14). Evidence was read from telemetry only;
no observer notes or screenshots exist, so visual-only items are `NOT COVERED`.

### Smoke and parsing

- [x] PASS: Passive observer initialized (`IC_AFK|START`, 1949-05-23).
- [x] PASS: Corrected parser/runtime defects did not recur. No rework-local
      parser error; `defender_modifier` and `political_power` rejections absent.
      Residual adjacent errors: `SIA_Coup_Succeeds` at
      `Indochina_Flavor_Events.txt:343`, LAO `Kong Pathom` motorized equipment.
- [x] PASS: New operation intelligence events and missions loaded and cleared
      (`CEFEO_INTEL|LAUNCH/CONCLUSION/CLEANUP` records).
- [ ] NOT COVERED: Outcome journal rendered with the expanded campaign ledger.

### Core lifecycle

- [x] PASS: No `IC_AFK|FAIL` records (44 `PASS`).
- [x] PASS: No premature vanilla Indochina peace conference.
- [x] PASS: Every launched VIN campaign recorded exactly one result.
- [x] PASS: Every launched CEFEO operation/response recorded exactly one result.
- [x] PASS: Markers and owned wars cleaned (all armistice/operation checks
      report zero remaining wars; marker-removal checks pass). Missions, ideas,
      and AI strategies are not individually logged.
- [ ] NOT COVERED: Superseded packages remained rewardless and ownership-neutral
      (no package was superseded in this run).

### Corrective-pass contracts

- [x] PASS: THO declaration-day deployment passed in both states.
- [ ] FAIL: Vinh Yen and Na San had meaningful launch-time defense (both clean
      for VIN on days 12 and 11).
- [ ] NOT COVERED: Northwest/MEO/raid priorities did not abandon the campaign
      corridor (no map observation; Northwest was clean on day 71).
- [x] PASS: Hirondelle created no war or territorial transfer.
- [ ] NOT COVERED: Mouette stayed inside its southern-Tonkin contract
      (participant envelope passed; map behavior unobserved; result failure).
- [x] PASS: Castor/Pollux had a useful preparation window (airhead 1953-12-28,
      Pollux resolved 1954-01-09, campaign `3` launched 1954-02-15).
- [ ] FAIL: Dien Bien Phu holdout modifiers worked and the siege exceeded the
      prior 30-day baseline materially (camp fell on day 24).
- [ ] NOT COVERED: Hanoi/Tonkin retained a bounded reserve during campaign `3`.
- [x] PASS: Geneva deferred until VIN's explicit post-DBP choice and preserved
      the peace gate (briefed 03-11, negotiations 03-22, gate and single
      `GENEVA_SOURCE|INVITE` 04-11, concluded 06-25).
- [ ] FAIL: NLF retained a useful force (12-13 divisions through 1953 versus
      VIE 38-44 with wartime cap 9999; NLF collapsed by 1954-04-27).

### Conditional/new content

- [ ] NOT COVERED: Dak Doa never launched. Its focus needs `date > 1954.02.10`
      and a living NLF at war holding province `10180`; NLF was alive on that
      date and collapsed by 04-27. The log does not show which gate failed.
- [ ] NOT COVERED: Northwest recovery (Northwest succeeded).
- [x] PASS: Atlante result/cleanup (full posture, stalled 1954-04-06).
- [x] PASS: Final Push consumed terminal Mouette/Atlante facts.

### Final balance evidence

- [x] PASS: All campaign/operation dates and elapsed days recorded.
- [x] PASS: VIE/NLF and crown-domain force-health series preserved.
- [x] PASS: Final Struggle margin and all leverage/delegate weights recorded
      (margin `+135`, Communist leverage 300, VIN 54 / VIE 43).
- [x] PASS: Logs preserved before any subsequent launch.
- [x] PASS: Failures divided into regression, balance, and unrelated-noise
      queues (see the 2026-09-28 ledger entry in
      `VIN_FRE_Tree_Expansion_Design.md`).

## Decision after the run

1. Fix demonstrated lifecycle/parser regressions first.
2. Fix demonstrated AI allocation and balance failures using the recorded map,
   timing, force-health, and score evidence.
3. Re-run only the smallest affected checkpoint when the repair is isolated;
   require another unified run only when campaign ordering, Geneva, shared
   cleanup, faction/war topology, or broad balance changed.
4. Mark the tested corrective-pass systems engine-accepted in
   `VIN_FRE_Tree_Expansion_Design.md` and `HANDOFF.md` only after reviewing both
   preserved logs and this checkoff.
5. Once accepted, continue the remaining rework content without reopening
   accepted Brochet or primary-campaign lifecycle code absent a concrete
   regression.
