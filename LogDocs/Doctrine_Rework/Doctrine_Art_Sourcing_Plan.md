# Doctrine Art Sourcing Plan

Goal: every land, naval, air and SF track background, grand doctrine medallion and subdoctrine icon
is a period photo that matches its subject. Land first, then naval, air, SF.

## Problems reported (2026-11-06 playtest)

- Track backgrounds that miss their track: Revolutionary Insurgency armor (a group of fighters),
  Intervention and Pacification (no armor in armor), People's War (generic), Deep Battle combat support
  (a tunnel), Forward Defense combat support and armor (a cut-off figure; troops on a truck).
- Grand doctrine medallions read as random photos: Forward Defense (same photo as a track), People's
  War, Intervention and Pacification, Revolutionary Insurgency.
- Subdoctrine icons are a mix of vanilla silhouettes, banner crops, legacy icons and near-blank grey
  discs. Style and subject are inconsistent.

## Rules for every image

1. **Licence.** Public domain or a licence that allows redistribution in a mod: US DoD / DVIDS /
   NARA / Library of Congress (PD), Wikimedia Commons (PD or CC BY / CC BY-SA with attribution),
   Bundesarchiv (CC BY-SA 3.0 DE), IDF / GPO Israel (released, attribution), Imperial War Museums
   (non-commercial licence; check per image), Australian War Memorial (PD for pre-1955 or marked
   items). No stock agencies, no Getty/AP/Alamy, no unattributed Pinterest copies.
2. **Provenance recorded** per file in `gfx/interface/doctrines/cwic/CREDITS.md`: target sprite,
   source URL, author, licence, date.
3. **Period and side.** Photo must be from the school's bloc (or a close user) and from 1945-1991.
   Era 2 and 3 subdoctrines prefer photos from their decade.
4. **Subject.** Track: the track's arm (infantry, artillery/engineers/aviation, tanks/AFVs, command and
   movement). Medallion: the school's single most recognisable image (formation, leader at map,
   signature vehicle). Subdoctrine: the exact concept (helicopter landing for airmobile, ATGM team,
   BM-21 salvo, OMG tank column...).
5. **Composition.** Track art must survive a 360x660 portrait cover-crop with the subject in the
   middle 60 percent. Icons must read at 48 px inside a circle: one clear subject, high contrast.
6. Same CRT treatment, circle mask and luminance band as now (pipeline in the art agent's build
   script). Silhouette icons are retired; everything becomes a photo.

## Phases

### 1. Inventory and briefs (no downloads)

Generate `Doctrine_Art_Manifest.csv` from the doctrine files: one row per sprite (277), columns
sprite, object, school, track, era, concept (from loc description), current source, status
(keep / replace / missing), search terms, preferred archives. Mark the user's list above as
`replace`, every silhouette or grey disc as `missing`. Output also a short brief per land school
(bloc, countries, signature equipment, iconic operations) to steer searches.

### 2. Land sourcing (one agent per school pair, parallel)

For every land row not `keep`: search archives (Commons category trees such as
"Military of the Soviet Union in the 1970s", "M60 Patton in service", "Yugoslav People's Army",
DVIDS / NARA catalogue, Bundesarchiv, IDF Flickr), pick 2-3 candidates, download originals to
`_local/doctrine_art_candidates/<sprite>/`, record licence and URL. No processing yet.

### 3. Review gate (user)

Build a contact sheet per school: current image vs candidates, labelled with sprite and concept.
User picks or rejects; rejected rows go back to phase 2 with notes. Taste call stays with the user.

### 4. Processing and integration

Run the existing pipeline on chosen originals (cover-crop with manual focal point from the manifest,
CRT, circle mask, luminance normalisation). Overwrite files in `cwic/{tracks,grand,icons}`; sprite
names and doctrine scripts do not change. Update CREDITS.md. Headless load check for texture errors.

### 5. In-game check (user)

Screenshot pass of all 7 land schools; nitpicks feed one more phase 2-4 loop.

### 6-8. Naval, air, special forces

Same phases. Naval: US Navy NHHC, Royal Navy, Soviet Navy (Commons), French Marine Nationale.
Air: USAF NMUSAF, Bundesarchiv, Soviet VVS, IAF. SF: unit-specific (SAS, Green Berets, Spetsnaz,
Selous Scouts, Legion, Recces) with extra licence care; many SF photos are restricted.

## Risks

- Legible PD photos of Warsaw Pact, PRC, Iranian and insurgent forces are scarcer than NATO ones;
  expect more Commons CC BY-SA and some substitutions (e.g. East German or Czech exercises for
  generic Soviet subjects).
- CC BY-SA requires attribution and share-alike of the edited image; CREDITS.md and keeping the
  edited PNGs under the same licence covers it. Confirm the mod team is fine with that.
- 222 icons is a large search. Prioritise: track backgrounds and medallions, then school-exclusive
  subdoctrines, then generics.

## Step 1 status (2026-11-06)

- `Doctrine_Art_Manifest.csv`: 277 rows (sprite, kind, folder, school, track, era, name, concept,
  current source, status, search seed, archives, note). Status: replace = flagged or washed out,
  review = photo with unverified subject, missing = still a vanilla silhouette.
- `Doctrine_Art_School_Briefs.md`: per-school kit, events, track subjects, sources.
- Triage sheets: `_local/doctrine_art_review/<school>.png` (red replace, yellow review, blue missing).
- Pipeline moved to `CWIC Backup/tools/doctrine_art/` (build.py, plans, vanilla source cache, legacy
  icons). Fixed there: the bloc banners are ~45% transparent PNGs, so every banner-based track,
  medallion and icon rendered ghosted over the frame (the blank grey discs). Banners are now
  flattened to opaque before processing and all art was rebuilt.
