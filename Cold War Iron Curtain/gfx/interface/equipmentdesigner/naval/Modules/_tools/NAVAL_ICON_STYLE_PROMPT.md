Make a naval equipment-designer module icon for CWIC in the NSB armour-module aesthetic.

MODULE: <module key, e.g. ship_SAM_mid_range_1> — <tech + start_year, e.g. light_sam_1, 1985>
REAL SYSTEM: <named system for that era, e.g. RIM-7M Sea Sparrow> (if blank, pick the most iconic real system in service at that tech year and tell me which and why)

## What the icon is
- A side-view SCHEMATIC of the actual weapon/system itself, drawn like the NSB tank-gun and SAM icons.
  - Guns: barrel + rings + cradle + breech block only. No turret house, no ship, no hull.
  - Missiles (AShM, SAM rounds, torpedoes): the munition only, nose pointing LEFT. Add a launcher only if the module IS the launcher.
  - Self-contained systems (e.g. CIWS): draw the recognisable whole mount (e.g. Phalanx = rounded dome, gatling under it, ammo drum, base).
- It must be identifiable as that specific real system from silhouette alone at 1x. Exaggerate its signature features (Harpoon booster, Exocet aft deltas, Oniks nose cone, 76/62 loading drum).
- No waves or sea motif (the schematic carries it).

## Pixel rules (exact, matches existing files)
- Canvas 76x42 RGBA, transparent background (ship-module size; tank icons are 56x42).
- Art lives in rows ~1-26, nothing below row 28. Label baseline: glyph rows 31-39.
- Draw only 1-px "bright" lines in these five colours:
  - G green  (140,255,197)  barrels, structure, label text
  - W white  (255,255,255)  missile/torpedo airframes, ammunition
  - B blue   (140,182,255)  fins, wings, rings, clamps, intakes, breech/receiver housings, section joints
  - Y yellow (197,162, 33)  muzzles, seekers, motors, boosters, nozzles
  - R red    (254,136,136)  add-on hardware: radomes/sensors, launch canisters, loading drums, hoists
- Shadow: every bright pixel gets an opaque copy at (+1,+1) in its dark colour, unless that pixel is bright:
  G (80,161,129)  W (177,177,177)  B (87,114,161)  Y (124,103,19)  R (161,79,79)
- Glow: every empty pixel touching a bright/shadow pixel gets that pixel's colour at alpha 51 (orthogonal) or 30 (diagonal only).
- Hollow shapes: draw tubes/bodies as two parallel outlines with the shadow filling between, never solid fills. Small fins/wings may be filled with blue.
- Prefer horizontal, vertical, 45-degree and 1:2 lines; shallow diagonals (1:3, 1:4) on parallel lines turn into dashed noise. Keep barrels level.
- Leave ~2 px margin; nothing touches the canvas edge except glow.

## Label
- 5x9 pixel font, 1-px letter spacing, green, from the tank icons (glyphs in draw.py FONT; add new ones in the same 5x9 style).
- Left: role code, with a count where relevant: `1x 76MM`, `1x CIWS`, `ASHM`, `TORP`, `SR-SAM`, `LR-SAM`.
  2-px gap after the count.
- Right-aligned 2 px from the edge: apostrophe + 2-digit tech year, e.g. `'85`.

## Workflow
1. Add the design to _tools/naval_icons.py: an art function drawing in a LOCAL 60x26 box (x 0..59, y 0..25), plus a registry
   row (key, folder, file name, label, year, art, module keys, tech keys). Reuse the helpers there (barrel/ring/slide/house/
   drum/hoist for guns, torp_body/tail_cone/props/duct/wire for torpedoes, fin() for missiles). draw.py holds Canvas, font,
   shadow/glow rendering.
2. Each design renders twice: module icon 76x42 (art at 8,1; label rows 31-39) and tech icon 64x64 (art at 2,12; label rows
   42-50 - the same layout as the NSB armour tech icons). Keep art inside the 60x26 box or it clips on the tech icon.
3. Review: render a sheet of the new icons at 1x, 2x and 6-8x beside a reference (tanks/Modules/SPAAG/AA Guns/1 naval AA gun
   1990.png, SPAAG/AA Missiles/SAM 1980.png). Iterate until it reads at 1x.
4. From the mod root run:  python "gfx/interface/equipmentdesigner/naval/Modules/_tools/naval_icons.py"
   It writes module PNGs to naval/Modules/<Category>/, tech PNGs to gfx/interface/technologies/cwic_naval_rework/<tech>.png
   and regenerates interface/cwic_naval_rework_icons.gfx (GFX_SMI_<module>, GFX_<tech>, GFX_<tech>_medium).
   Never hand-edit that .gfx. If a sprite name is newly taken over, delete its old definition elsewhere in interface/
   (equipmentdesignermoduleicons.gfx, Technologies.gfx) so names stay unique. A module with `gfx = X` uses GFX_SMI_X.
5. A module that borrows another module's sprite via `gfx = <sprite>` changes with it. Before redrawing a sprite, grep
   00_ship_modules.txt for `gfx = <sprite>`; give borrowers their own name and keep their old art via the LEGACY list in
   naval_icons.py.
