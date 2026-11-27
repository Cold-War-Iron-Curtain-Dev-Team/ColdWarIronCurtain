# VIE - Diem Premiership Art Requests

Every asset below is currently pointed at an existing icon so nothing renders blank in game.
All 52 focus icons have landed (`GFX_VIE_PM_Diem` / `GFX_VIE_Diem_*` in
`interface/IC_goals.gfx` and `interface/IC_goals_shine.gfx`, PNGs in `gfx/interface/goals/VIE/`).

## Idea icons

| Idea | Wanted GFX name | Currently borrowing | Subject |
|---|---|---|---|
| `VIE_Can_Lao_Party` | `GFX_idea_Diem_Pol_Commissar` | `idea_generic_political_support` | A Can-Lao cell of five around a table, the Sac-lenh on the wall |
| `VIE_Diem_Loyalist_Officer_Corps` | `GFX_idea_Diem_Pol_Commissar2` | `idea_generic_army_problems` | Newly commissioned officers taking the oath, French insignia gone |

`GFX_idea_Diem_Pol_Commissar` and `GFX_idea_Diem_Pol_Commissar2` were referenced by eight
`VIE_ideas.txt` entries and registered nowhere; they are now declared in
`interface/CWIC_ideas.gfx` against vanilla placeholders. Replace the `texturefile` there when
real art lands - no idea needs editing.

## Event pictures
Done (Nov 2026). All of the event pictures below now have their own art in
`gfx/event_pictures/VIE/` with matching sprites in `interface/eventpictures.gfx`. The
pictures were built with EventPic Studio from period photographs, mostly Wikimedia
Commons and the Texas Tech Vietnam Archive. The manifest and sources are in
`agent_docs/eventpics/vie_diem/`, which is gitignored. Most of the photographs are
period stand-ins, not exact matches for the subjects listed in the original
request. `Diem.31` and `Diem.42` were not on the original list and also got
pictures. `Diem.1`, `Diem.6`, `Diem.61`, `VIE_PMs.9` and `Can_Lao.1` already had
their own art.

## Idea icon

`VIE_Diem_Loyalist_Officer_Corps` in `common/ideas/VIE_ideas.txt` uses
`picture = alcoholism #PLACEHOLDER`, the same placeholder the neighbouring VIE ideas use.
Wanted: an officer corps insignia over a personalist emblem.

`VIE_Can_Lao_Party` borrows `picture = Diem_Pol_Commissar`, which is real art but belongs to
a different idea. Wanted: `VIE_Can_Lao_Party`, the party emblem over a five-cell diagram.

`VIE_Caretaker_Cabinet` borrows `picture = generic_disjointed_gov`. Wanted:
`VIE_Caretaker_Cabinet`, an empty cabinet table with fifteen chairs pushed back.

## Character portraits

`VIE_Duong_Van_Minh` and `VIE_Do_Cao_Tri` were added to `common/characters/VIE.txt` and both
reuse portraits that already shipped (`gfx/leaders/VIE/GENERALS/Duong_Van_Minh.dds` and
`Do_Cao_Tri.dds`), so nothing is missing for them.

Three people named in the new events have **no character entry and no portrait**, and appear
in prose only: Tran-Van-Don (promoted 30 April 1955, signatory of the generals' telegram),
Nhi-Lang (the civilian who drew on General Vy) and Ha-Thuc-Ky (the Dai-Viet commander at
Ba-Long). If any of them is ever given a role, a portrait is needed first.
