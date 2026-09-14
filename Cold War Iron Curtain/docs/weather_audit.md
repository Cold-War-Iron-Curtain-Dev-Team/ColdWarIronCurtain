# Strategic region weather audit — Cold War Iron Curtain

327 region files, 17,546 provinces. Everything below was derived from the files themselves, not sampled.

## What is structurally sound

- Province coverage is perfect: all 14,243 land, 3,147 sea and 156 lake provinces belong to exactly one strategic region. No orphans, no duplicates, no ghosts.
- No duplicate region IDs. No inverted min/max temperatures. Every 12-period region maps cleanly to months 0–11.
- `IC_Defines.lua` does not touch weather. The commented-out `climate = "climate.txt"` in `default.map` is vanilla and inert.

The problems are all in the *content* of the weather blocks.

---

## 1. Regions with no usable weather (11)

Nine have an empty `weather = { }`; the game has no temperature curve to read.

| ID | Region | Provinces |
|---|---|---|
| 250 | Central Chernozem | 79 land |
| 301 | Lake Victoria basin | 87 land + 4 lake |
| 325 | Straits of Magellan | 18 land + 22 sea |
| 234 | Persian Gulf | 4 land + 4 sea |
| 267 | Gulf of Aden | 1 land + 4 sea |
| 237 / 268 / 238 / 269 | Lake Onega, Lake Ladoga, San Francisco Bay, Aral Sea | 1–3 sea/lake each |

Two more have a single period covering the whole year instead of twelve:

- **315 Tonkin** (42 land) and **266 Gulf of Tonkin** — `between = { 0.0 30.11 }`, `temperature = { 16 36 }`, snow 0, mud 0.5.

## 2. Wrong climate pasted into the wrong place

These are the ones that make temperatures look actively broken rather than merely flat.

**18 Atlantic regions share one Arctic curve.** `16 North Sea, 43 Western Approaches, 44 Denmark Strait, 45 Norwegian Sea, 47 Spanish Coast, 48 African Coast, 49–51 + 56–59 Mid Atlantic, 50 Labrador Sea, 54 Eastern Seaboard, 55 Newfoundland Sea, 170 Florida Coast, 173 Eastern North Sea, 174 Norwegian Coast`

Curve: `-15/2 -15/2 4/10 4/10 5/15 5/15 5/15 0/8 0/8 0/8 -15/2 -15/2`

Florida, the Spanish coast and the African coast get −15 °C for four months of the year. It is also a 6-step curve each step written twice, so it is not really monthly.

**5 regions share an Alpine curve, including Cuyo (Mendoza, Argentina).** `21 Alpine Region, 212 Austria, 214 Northern Italy, 320 North Spain, 302 Cuyo` — Cuyo gets northern-hemisphere phasing (peak July, trough February) *and* Alpine cold (−18 °C) in a warm southern-hemisphere wine region.

**194 Eastern Australia** shares its curve with `227 Sudan, 231 Niger, 272 White Nile, 275 Lower Egypt, 281 Upper Volta, 289 Guinea` — Sahel weather, northern-hemisphere phasing (peak June, trough January) on Brisbane/Sydney.

**278 Kivu** (equatorial DRC) shares with `185 South East Africa, 270 Zambia, 277 Katanga` — a 10 °C annual swing in a region that has almost none.

**184 South West Africa** shares with **298 Cameroon** — Namib desert curve peaking at 40 °C applied to equatorial rainforest.

## 3. Seasonless regions

**68 of 90 naval regions** repeat one identical temperature range for all twelve months. Sea of Okhotsk is `{ -10 35 }` every month of the year; Bering Sea and North Pacific are `{ -20 0 }`; Caspian and Mediterranean are `{ 12 30 }`.

**7 land regions** are seasonless too — these matter more, because armies stand on them:

| ID | Region | All-year range | Land provinces |
|---|---|---|---|
| 53 | Caribbean | 10 / 30 | 116 |
| 254 | Patagonia | 2 / 8 | 56 |
| 195 | Central Australia | 20 / 35 | 49 |
| 76 | East China Sea | 11 / 28 | 33 |
| 93 | Banda Sea | 11 / 28 | 31 |
| 169 | Tyrrhenian Sea | 12 / 30 | 11 |
| 30 | Black Sea | 12 / 30 | 9 |

Patagonia in particular takes its curve straight from the Southern Ocean naval group.

## 4. Snow and mud inconsistencies

- **39 regions, 173 months** drop below −8 °C with `snow = 0` and `blizzard = 0`. Includes the Alps, Austria, Northern Italy, Himalayas, Tibet, Kashmir, Ural Region, Northern Norway, Qinghai, Caucasus, Taman, Hudson Bay, Afghanistan. Snow-free winters at −30 °C in the Urals.
- **13 regions set `mud = 0`** for every month, including Eastern Canada, Northern Canada, Ural Region, Alpine Region, Austria, Northern Italy, North Spain, Himalayas, Tibet, Kashmir, Cuyo. No rasputitsa where the thaw is strongest.
- **30 Black Sea has `mud = 100000`** in all twelve periods. Almost certainly a stray typo.
- **4 Indian regions** (153 Northern India, 209 Western India, 260 Central India, 316 Sind-Balochistan) have snow in Dec/Feb at a monthly minimum of +11/+12 °C. Cosmetic, but wrong.
- **`arctic_water = 0` in every single region.** No sea ice forms anywhere on the map, Barents and Bering included.
- **Diurnal spread of 45 °C** in 87 Sea of Okhotsk, 90 Coast of Japan and 166 Hudson Bay (`temperature = { -10 35 }`).

## 5. Copy-paste concentration

316 regions with full curves resolve to only **132 unique temperature curves**, in 56 shared groups. The largest single block covers **31 regions** (most of the tropical and Indian Ocean naval map). That is the mechanism behind every mismatch above: blocks were duplicated across regions faster than they were checked against geography.

---

## Suggested repair order

1. Fill the 11 missing/flat blocks (§1) — smallest fix, biggest visible effect, and Central Chernozem sits in the mod's main theatre.
2. Split the 18-region Atlantic group (§2) into at least arctic / temperate / subtropical bands. Florida and the African coast are the loudest offenders.
3. Fix the four wrong-hemisphere or wrong-climate pastes: 302 Cuyo, 194 Eastern Australia, 278 Kivu, 184/298.
4. Give the 7 seasonless land regions real curves (§3).
5. Sweep snow/mud: add snow to the sub-zero months, fix `mud = 100000` in Black Sea, decide whether `mud = 0` in the mountain and Canadian regions is deliberate.
6. Optional: give the naval regions seasonal curves and turn on `arctic_water` in the polar seas.

`weather_audit.csv` has the per-region table — periods, January and July ranges, annual min/max, amplitude, seasonless flag, diurnal spread, mud values, sandstorm flag and snow-month count — so you can sort and work through it.
