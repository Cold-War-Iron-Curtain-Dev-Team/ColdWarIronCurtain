# Weather fix — changelog

131 of 327 strategic region files changed. The other 196 are byte-identical.

## Regenerated (112 regions)
Temperature curves rebuilt from a winter mean, summer mean, diurnal spread and
hemisphere, using a cosine annual cycle. Oceans get a one-month thermal lag.
Precipitation is derived from the monthly mean: snow below about +4 C, blizzard
below -10 C, rain above, sandstorm only in arid regions above +15 C.

- 11 regions that had no usable weather: 234, 237, 238, 250, 266, 267, 268, 269, 301, 315, 325
- 19 Atlantic regions split out of the single Arctic curve: 16, 43, 44, 45, 46, 47, 48, 49, 50, 51, 54, 55, 56, 57, 58, 59, 170, 173, 174
- 4 wrong-climate pastes: 194 Eastern Australia, 278 Kivu, 298 Cameroon, 302 Cuyo
- 7 seasonless land regions: 30, 53, 76, 93, 169, 195, 254
- 67 seasonless naval regions
- 4 two-state stub curves: 9 Baltic Sea, 18 Channel, 42 Bay of Biscay, 127 Sahara desert

## Swept in place (19 regions)
Existing curves kept; only snow and mud values corrected.
120, 121, 138, 143, 146, 153, 190, 191, 205, 209, 21, 212, 214, 232, 256, 260, 316, 320, 36

- snow and blizzard added to months averaging below -2 C that had none
- snow removed from months whose minimum never drops below +8 C
- `mud = 0` replaced with `mud = 1` where a region has a real thaw
- `mud = 100000` in 30 Black Sea replaced with `mud = 1`

## Deliberately left alone
- `arctic_water = 0` in the weather blocks. The mod handles sea ice with the
  `water_modifier_arctic_waters` static modifier on 10 regions, so this field is
  unused by design.
- Monsoon regions peaking in March/April (India, Burma, Thailand, Mekong, Sahel,
  West Africa). That is correct climatology, not a phase error.
- 137 Western Steppe's 31 C diurnal spread. Continental Kazakhstan really is that extreme.

## Verification after the change
- 327 regions, all with 12 monthly periods
- 0 seasonless regions (was 75)
- 0 inverted min/max, 0 months below -2 C without snow, 0 snow above +8 C
- mud range 0.2 - 2.0 (was 0.0 - 100000)
- 223 unique curves for 327 regions, largest shared group 8 (was 132 unique, largest group 31)
- province coverage unchanged: every land, sea and lake province in exactly one region

`fix_weather.py` in `_tools/` regenerates everything. Edit the `SPEC` table to
retune a region and re-run; it only rewrites the weather block and leaves
provinces, naval_terrain and static_modifiers untouched.
