# Faction creation audit (read-only)

Scope: `Cold War Iron Curtain/` excluding `Toberemoved/` and backups. This pass found 97 live sites (about 60 generic, about 10 other templates, about 27 legacy `create_faction =`). Class assignments are my judgment from names and effects; the draft's §3 is the rule set. Scope and "already in a faction" status are only checked where the code shows it, and are marked `[INFERENCE]` otherwise. Nothing was edited or run.

## Summary

- Only 2 of the live sites carry an explicit `is_in_faction` guard before creating (`_generic_decisions.txt:1831` and the CMC block at `CMC_Expansion.txt:694–847`). `FRE_Indochina_Effects.txt:3078` guards with `NOT is_in_faction`, and `sov.2000` guards with `is_faction_leader`.
- Legacy `create_faction =` sites are all unguarded (about 27). The draft's "≈12" is an undercount.
- Unguarded `add_to_faction` into factions that may already exist is the main risk. Congo, Kenya, and Libya have the clearest cases.
- Duplicate creations of the same name or the same role (for example "NATO", "Islamic Legion", "Anti-Chinese Coalition", "People's Defense Coalition", "Anti-Turkish Alliance") exist in several files, and their trigger overlap is unverified.

## Files

Paths are under `Cold War Iron Curtain/`. "Guard" = visible `is_in_faction` / `is_faction_leader` / flag check before creation. "Dismantle" = `dismantle_faction` in the same effect block.

### Class 1: durable alliance (pact, treaty, NATO/Warsaw-type; dedicated template)

| # | File:line | Creating scope | Name / template | Era | Trigger | Members added | Guard | Dismantle | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 1 | history/countries/USA - United States.txt:22 | USA | `faction_template_nato` | 1949.3.1 | history | (template) | N | N | Canonical NATO |
| 2 | history/countries/SOV - Soviet union.txt:9 | SOV | `faction_template_cominform` | start | history | (template) | N | N | |
| 3 | history/countries/SOV - Soviet union.txt:3548 | SOV | `faction_template_Warsaw_Treaty_Organization` | `[INFERENCE]` | history | (template) | N | N | |
| 4 | history/countries/VIN - Vietnam.txt:372 | VIN | `faction_template_viet_minh` | start | history | (template) | N | N | |
| 5 | history/countries/CPB - Red Flag Communist Party.txt:174 | CPB | `faction_template_arakan_state_alliance` | 1948.1.1 | history | (template) | N | N | |
| 6 | history/countries/KAY - Karen National Liberation Army.txt:182 | KAY | `faction_template_karen_national_union` | 1949.1.1 | history | (template) | N | N | |
| 7 | events/_NATO.txt:242 | FRA (nato.12) | generic "European Defense Community" | post-NATO-dissolution | `nato.12` | every European NATO country invited | N | N | |
| 8 | events/_NATO.txt:581 | ROOT (nato.16) | generic "NATO" | `nato_disbanded` branch | `nato.16` | FRA added | N | FRA's faction dismantled (`:582`) | **Risky** |
| 9 | events/_NATO.txt:722 | ROOT (nato.18) | generic "NATO" | same | `nato.18` | ENG added | N | ENG's faction dismantled (`:723`) | **Risky** |
| 10 | events/_NATO_system.txt:58 | USA (NATO.2) | legacy `create_faction = NATO` | `[INFERENCE]` | `NATO.2` | ROOT added, then all others | N | N | **Risky** (legacy, unguarded) |
| 11 | events/ColdWarUprisings.txt:702 | `[INFERENCE]` (ULT_SOV.2) | legacy `create_faction = NATO` | `[INFERENCE]` | `ULT_SOV.2` | HUN added | N | N | **Risky**; scope not shown |
| 12 | events/CubanMissileCrisis.txt:788 | ROOT (cubamc.25) | legacy `create_faction = NATO` | `[INFERENCE]` | `cubamc.25` | every country with `SEATO/CENTO/nato_member` idea `[INFERENCE]` | N | N | **Risky** |
| 13 | decisions/MD4_NATO.txt:214 | `[INFERENCE]` | legacy NATO | — | `call_nato_to_arms` | — | N | N | **Dead**: `allowed` and `visible` are `always = no` |
| 14 | events/SovietUnion_Focus_Events.txt:2224 | SOV (sov.2000) | `faction_template_Warsaw_Treaty_Organization` | `[INFERENCE]` | `sov.2000` | converts cominform members | Y (`is_faction_leader`) | Y (`:2223`, own faction) | Guarded |
| 15 | events/KPA_Focus_Events.txt:16 | KPA (KPA.1000) | cominform "The United Front" | `[INFERENCE]` | `KPA.1000` | PRC | N | N | |
| 16 | focus/national_focus/KPA_50s_Korean_War.txt:26 | KPA | cominform "People's Defense Coalition" | 1950.6.20+ | focus `KPA_50s_the_fatherland_liberation_war` | `[INFERENCE]` | N | N | **Duplicate** of 17 |
| 17 | focus/national_focus/KPA_50s_Political_legacy.txt:143 | KPA | cominform "People's Defense Coalition" | 1950.6.20+ | focus `KPA_The_Fatherland_Liberation_War` | `[INFERENCE]` | N | N | **Duplicate** of 16 |
| 18 | events/Russia_1990s.txt:26 | RUS (CSTO.1) | generic "United Armed Forces of the CIS" | 1990s | `CSTO.1` | 11 CIS states | N | N | |
| 19 | events/Russia_1990s.txt:59 | RUS (CSTO.2) | generic "Collective Security Treaty" | 1990s | `CSTO.2` | 8 states | N | Y (own, from CSTO.1) | **Risky**: unguarded dismantle |
| 20 | events/Russia_1990s.txt:88 | RUS (CSTO.3) | generic "Collective Security Treaty Organization" | 1990s | `CSTO.3` | 8 states | N | Y (own, from CSTO.2) | **Risky** |
| 21 | events/aplwun.txt:306 | VIE | generic "Southeast Asian Anti-Communist Alliance" | `[INFERENCE]` | `[INFERENCE]` | PHI, LAO, CAM (via `leave_faction`) | Y (`leave_faction` on VIE/PHI/LAO/CAM) | N | |
| 22 | events/aplwun.txt:504 | PRC | generic "Beijing Pact" | `[INFERENCE]` | `[INFERENCE]` | VIN, KPA, LAO, CAM | N | Y (PRC's own, `:504`) | **Risky**: PRC's own faction (from `:211`) gets dismantled |
| 23 | events/aplwun.txt:599 | PRC | generic "Beijing Pact" | `[INFERENCE]` | `[INFERENCE]` | `[INFERENCE]` | N | `[INFERENCE]` | Second Beijing Pact creation |
| 24 | focus/national_focus/PRC_SOV_60s.txt:3592 | PRC | legacy "Beijing Pact" | `[INFERENCE]` | focus `PRC_SOV_Found_the_Bejing_Pact` (loaded from `IC_scripted_effects.txt:1507`) | — | N | N | |
| 25 | events/Korean_War.txt:248 | USA (korea.4) | `faction_template_nato`, name "The United Nations" | Korean War | `korean_war_usa_enters` | KOR added | N | N | **Risky**: USA already in NATO template; class 2 by name |
| 26 | focus/national_focus/Simba_60s.txt:2297 | SIM | generic "Brazzaville Pact" | `[INFERENCE]` | focus `SIM_Join_the_Warsaw_Pact` | — | N | N | |
| 27 | focus/national_focus/TIB_1950s.txt:3601 | RAJ | generic "Himalayan Accords" | `[INFERENCE]` | TIB tree | — | N | N | Could be class 3 |
| 28 | focus/national_focus/VIN_50s.txt:946–947 | VIN | `faction_template_viet_minh` "Indochinese Front" | `[INFERENCE]` | focus `VIN_Unity_for_Independence` | members flagged `Faction_with_VIN` first | N | Y (own, `:946`) | |
| 29 | scripted_effects/FRE_Indochina_Effects.txt:3078 | FRE | `faction_template_french_indochina` | `[INFERENCE]` | scripted effect | VIE | Y (`NOT is_in_faction` + leader/leave checks) | Y (migration, leader-only) | |
| 30 | focus/national_focus/60s_ITA.txt:5072 | ITA | legacy `create_faction = the_concordat` | 1960s | focus `ITA_60s_The_Concordat` | — | N | N | Legacy |
| 31 | focus/national_focus/60s_MOR.txt:3289 | MOR | generic "The Non-Aligned Movement" | 1960s | focus `MOR_60s_ALT_LEADER_OF_THE_THIRD_WORLD` | — | N | N | |
| 32 | focus/national_focus/BAN_East_Pakistan_Cofederation.txt:236 | PAK | generic "Pakistan-Bangladeh Defense Pact" | 1970s | focus `BAN_Approach_Pakistan_For_Final_Status` | BAN | N | N | |
| 33 | events/Pakistan_Alternate_1973_Coup.txt:279 | PAK | generic "Pakistan-Bangladeshi Defense Pact" | 1973 | `Pakistan_Alt_1973_Coup.14` | BAN | N | N | Near-duplicate of 32 |
| 34 | focus/national_focus/COG_70s_Communism.txt:2049 | COG (DRC) | generic "Kinshasa Treaty Organization" | 1970s | focus `DRC_70s_The_Bulwark...` | — | N | N | Focus id ends with "." `[INFERENCE]` |
| 35 | focus/national_focus/Cuba_60s.txt:3899 | CUB | generic "Sino-Cuban Pact" | 1960s | focus `CUB_sino_cuban_pact` | PRC block | N (`bypass` on PRC `is_in_faction = yes`) | N | |
| 36 | events/Cuba.txt:160 | SPR (cuba.8) | generic "Trans-Atlantic Spanish Alliance" | `[INFERENCE]` | `cuba.8` | CUB (`SPR add_to_faction`) | N | N | |
| 37 | events/Iraq.txt:117 | IRQ (Iranian_Iraq.2) | generic "CENTO" | `[INFERENCE]` | `Iranian_Iraq.2` | PER | N | N | |
| 38 | events/Kenya.txt:788 | KEN (kenya.32) | generic "South Africa-Rhodesia Defensive Pact" | `[INFERENCE]` | `kenya.32` | ZIM→SAF, ZIM→POR | N | N | **Risky**: `ZIM add_to_faction = SAF` requires SAF to lead a faction |
| 39 | events/Kenya.txt:972 | GHA (kenya.34) | generic "TTWO" | `[INFERENCE]` | `kenya.34` | MLI, TOG, NGR, VOL, IVO, KEN, CMR, CHA | N | N | **Risky**: many members may already be in factions |
| 40 | events/Kenya.txt:1420 | KEN (kenya.46) | generic "African Defensive Bloc" | `[INFERENCE]` | `kenya.46` | ZIM, SAF | N | N | |
| 41 | events/Uganda.txt:748 | `[INFERENCE]` | generic "East African Defense Community" | `[INFERENCE]` | `[INFERENCE]` | MZB | N | N | |
| 42 | events/Libya.txt:36 | LBA (swfs.14) | generic "The Mediterranean Alliance" | `[INFERENCE]` | `swfs.14` | `LBA add_to_faction = ROOT` runs first, then create | N | N | **Risky**: add before create |
| 43 | events/PRC_Tibet_Events.txt:203 | PRC `[INFERENCE]` (PRC_TIBETAN.10) | generic "Himalayan Defense Pact" | 1950s | `PRC_TIBETAN.10` | TIB | N | N | |
| 44 | events/Third_Balkan_War.txt:813 | PDG (THIRD_BALKAN_WAR.34) | generic "Anti-Turkish Alliance" | `[INFERENCE]` | `THIRD_BALKAN_WAR.34` | ALB | N | N | Duplicate name, see 45 |
| 45 | events/Third_Balkan_War.txt:930 | PDG (THIRD_BALKAN_WAR.38) | generic "Anti-Turkish Alliance" | `[INFERENCE]` | `THIRD_BALKAN_WAR.38` | YUG | N | N | **Risky**: PDG can create this twice |
| 46 | events/sierra leone.txt:303 | NPF (SIE_Civil_War.1) | generic "Taylor Aligned Militias" | 1991 | `SIE_Civil_War.1` | RUF | N | N | (Class 2 by name; listed here by intended role) |

Class 1 total: 46 rows. Several (14, 22, 25, 27, 35, 38, 39, 42, 44, 45) are in risky lists below.

### Class 2: campaign coalition (generic template + one defined objective)

| # | File:line | Creating scope | Name | Era | Trigger | Members added | Guard | Dismantle | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 47 | decisions/Indonesia.txt:603 | DAR | legacy `DAR_Faction_1` | `[INFERENCE]` | `darul_islam_0` (group `Indonesia_Rebellion_decisions`) | — | N | N | **Risky**; DAR declares war on INO |
| 48 | decisions/Indonesia.txt:607 | INO | legacy `INO_Faction_1` | same | same | — | N | N | **Risky** |
| 49 | decisions/KMT_China_decisions.txt:2437 | CHI | generic "Anti-Communist Resistance Front" | Korean War | `join_the_fray_alone_against_Korea` | KOR | N | N | **Risky** |
| 50 | decisions/_generic_decisions.txt:1832 | CHI | generic "Anti-Communist Salvation Front" | nuke decision | `[INFERENCE]` | KOR, USA (both if not in faction) | Y (`is_in_faction = no`, `:1831`) | N | |
| 51 | decisions/arab_league_decisions.txt:881 | `UNS.arab_league_nation_target` | legacy `ADL` | action set 11 | `ARAB_LEAGUE_RESOLUTION` | target becomes leader | N | N | **Risky** |
| 52 | decisions/arab_league_decisions.txt:931 | UNS | generic "The United Nations" | action set 13 | `ARAB_LEAGUE_RESOLUTION` | target | N | N | **Risky** |
| 53 | scripted_effects/UN_Scripted_Effects.txt:323 | UNS | generic "The United Nations" | `UN_RESOLUTION` action 12 | `UN_RESOLUTION` | `var:UNS.coalition_tag` | N | N | |
| 54 | scripted_effects/UN_Scripted_Effects.txt:333 | UNS | generic "The United Nations" | action 13 | same | same | N | N | Duplicate of 53 |
| 55 | focus/national_focus/BCP_50s.txt:2799 | BCP | generic "Burmese Liberation Front" | 1950s | focus `BCP_50s_Denounce_U_Nu_s_Socialist_Government` | MNL | N | N | |
| 56 | focus/national_focus/Cuba_60s.txt:533 | CUB | generic "Posadist Fifth International" | 1960s | focus `CUB_the_posadist_fifth_international` | — | N | N | Could be class 3 (ideological) |
| 57 | focus/national_focus/FRA_1960s_Communist.txt:1248 | FRA | generic "Fourth Internationale" | 1960s | focus `FRA_60s_The_Fourth_Internationale` | — | N | N | Ideological |
| 58 | focus/national_focus/GPLA_60s.txt:2895 | PDG | generic "Anti-Revisionist Bloc" | 1960s | focus `PDG_60s_The_Tirana_Summit` | — | N | N | |
| 59 | focus/national_focus/MOR_1950s.txt:1146 | MOR | generic "Morrocan Liberation Front" | 1950s | `Ifni_War.1` completion | — | N | N | |
| 60 | focus/national_focus/60s_VIE.txt:4753 | VIE | generic "Anti-Communist League" | 1960s | focus `VIE_60s_Anti_Communist_KMT_Alliance` | CHI | N | N | Sets `VIE_generic_faction_created` |
| 61 | focus/national_focus/SAF_1960s.txt:2531 | SAF | generic "Alcora Exercise" | 1960s | focus `SAF_60s_The_Alcora_Exercise` | — | N | N | Could be class 3; reachable only via `IC_scripted_effects.txt:1335` |
| 62 | focus/national_focus/SOV_WW3_1950s.txt:365 | SOV | legacy `KOR_FACTION_WW3` | WW3 | focus `SOVw_...` (`DPRK_Letter_Join_War`) | KPA sphere | N | N | **Risky** |
| 63 | focus/national_focus/SOV_WW3_1950s.txt:907 | PRC | legacy `PRC_FACTION_WW3` | WW3 | `SOVw_Operation_Fallen_Sun` | — | flag only (`PRC_JOIN_WAR`) | N | **Risky** |
| 64 | focus/national_focus/SOV_WW3_1950s.txt:951 | PRC | legacy `PRC_WW3_FACTION` | WW3 | `SOVw_Sign_the_Mutual_Non_Interference...` | — | flag only | N | **Risky**: two PRC factions (907, 951) |
| 65 | focus/national_focus/YAN_50s_Victory.txt:1209 | YAN | generic "Anti-Communist Salvation Front" | `[INFERENCE]` | focus `YAN_Propose_a_Deal...` | MNL, KAY via events | N | N | Duplicate name of 50 |
| 66 | focus/national_focus/Trees for 0.35/PRC_50s_New.txt:4960 | PRC | generic "Revolutionary International" | `[INFERENCE]` | `PRC_50s-Build_our_own_Faction` | — | N | N | **Dead**: `Trees for 0.35` |
| 67 | focus/national_focus/OUTDATED_PRC_50s_Rework.txt:5896 | PRC | legacy "Emerging_Forces_Pact" | `[INFERENCE]` | `PRC_50s_Emerging_Forces_Pact` | — | N | N | **Dead**: `OUTDATED_` file |
| 68 | events/Bangladesh_War.txt:474 | ROOT (Operation_Searchlight.21) | generic "Bangladesh Liberation Front" | 1971 | `Operation_Searchlight.21` | BAN | N | N | Duplicate of 69 |
| 69 | events/Bangladesh_War.txt:1275 | RAJ (Bangladesh_War.1) | generic "Bangladesh Liberation Front" | 1971 | `Bangladesh_War.1` | BAN | N | N | |
| 70 | events/CMC_Expansion.txt:567 | USA (CMC_Sino_India_War.26) | generic "Anti-Chinese Coalition" | 1962 | `CMC_Sino_India_War.26` | `every_country` with flag | N | N | |
| 71 | events/CMC_Expansion.txt:694 | USA | generic "Anti-Chinese Coalition" | 1962 | CMC block | RAJ (if not in faction) | Y (`is_in_faction = no`) | N | |
| 72 | events/CMC_Expansion.txt:736 | USA | generic | `[INFERENCE]` | CMC | — | Y (per summary) | N | Not re-read |
| 73 | events/CMC_Expansion.txt:805 | USA | generic | `[INFERENCE]` | CMC | — | Y (per summary) | N | Not re-read |
| 74 | events/CMC_Expansion.txt:847 | USA | generic | `[INFERENCE]` | CMC | — | Y (per summary) | N | Not re-read |
| 75 | events/Congo.txt:644 | COG (congo.7, via `IC_scripted_effects.txt:11438`) | generic "Simbas" | 1964–65 | `congo.7` | SKS | N | N | |
| 76 | events/Congo.txt:1083 | RWA (congo.14, via `IC_scripted_effects.txt:11337`) | generic "Alliance of Democratic Forces for the Liberation of Congo" | 1996 | `congo.14` | COG, UGA, BRD | N | N | **Risky**: COG may already lead "Simbas" (644) |
| 77 | events/Congo.txt:1494 | RWA (congo.16, via `IC_scripted_effects.txt:11358`) | generic "Rwanda & Allies" | 1998 | `congo.16` | COG, BRD | N | N | **Risky**: COG in two factions |
| 78 | events/Congo.txt:1548 | UGA (congo.16) | generic "Uganda & Allies" | 1998 | `congo.16` | SKS | N | N | **Risky**: SKS already in "Simbas" |
| 79 | events/Libya70s.txt:57 | LBA (lba70.2) | generic "Islamic Legion" | 1970s | `lba70.2` | FRO | N | N | Duplicate of 80 |
| 80 | history/countries/LBA - Libya.txt:485 | LBA | legacy "Islamic Legion" | 1978.1.1 | history date | CHA | N | N | **Risky**: legacy and duplicate |
| 81 | events/SovietUnion_Historical_Events.txt:932 | RUS | generic "White Movement" | `[INFERENCE]` | RUS_CW event | RNU, RFE, RLG | N | N | |
| 82 | events/SovietUnion_Historical_Events.txt:1019 | SOV | generic "Red Movement" | `[INFERENCE]` | SOV_RSFSR event | USO | N | N | |
| 83 | events/Sino_Indian_War.txt:1164 | RAJ (Sino_India_Pact.1) | generic "Anti-Chinese Coalition" | 1962 | `Sino_India_Pact.1` option b | PAK | N | N | Duplicate of 84 |
| 84 | events/Sino_Indian_War.txt:1191 | RAJ (Sino_India_Pact.2) | generic "Anti-Chinese Coalition" | 1962 | `Sino_India_Pact.2` | PAK | N | N | Duplicate |
| 85 | events/Tibet_Events.txt:429 | `[INFERENCE]` (GHW_TIB.1) | generic "Anti-Communist Salvation Army" | `[INFERENCE]` | `GHW_TIB.1` | XSM, YAN, PQC | N | N | |
| 86 | events/USA_1980s_CIA.txt:3806 | `[INFERENCE]` (CIA_SOM.3) | generic "Somalian Liberation Front" | 1977–80 | `CIA_SOM.3` | WSL, SAL | N | N | |
| 87 | events/USA_1980s_CIA.txt:6896 | random country with flag `Afghan_Coalition_Agree` | generic "Anti-Communist Coalition" | `[INFERENCE]` | hidden effect | flagged countries | flag-only | N | |
| 88 | events/aplwun.txt:164 | CHI | generic "Anti-Communist Bloc" | 1950 | `[INFERENCE]` | KOR | N | N | |
| 89 | events/aplwun.txt:211 | PRC | generic "Peoples Liberation Front of Asia" | 1950 | `[INFERENCE]` | MON | N | N | |
| 90 | events/Korean_War.txt:84 | `[INFERENCE]` (korea.1.o.a) | `faction_template_peoples_liberation_front` | 1950 | `korea.1` | `[INFERENCE]` | N | N | |
| 91 | events/Cuba.txt:103 | `[INFERENCE]` (cuba.5) | generic "Caribbean Alligence" | `[INFERENCE]` | `cuba.5` | — | N | N | |

Class 2 total: 45 rows.

### Class 3: diplomatic or assistance (no faction candidate)

Candidates that could be replaced by a non-faction effect. Not reclassified in the table above; decide during migration.

- `national_focus/SAF_1960s.txt:2531` ("Alcora Exercise"), exercise rather than an alliance.
- `national_focus/Cuba_60s.txt:533` ("Posadist Fifth International") and `national_focus/FRA_1960s_Communist.txt:1248` ("Fourth Internationale"), ideological networks.
- `national_focus/TIB_1950s.txt:3601` ("Himalayan Accords"), possibly a diplomatic accord.

### Class 4: existing-faction participant (add-only, no creation)

- `events/Cuba.txt:` cuba.6 (`USA add_to_faction = CUB`) and cuba.7 (`SOV add_to_faction = CUB`): both guarded only by the event firing once. Membership checks: none.
- `events/aplwun.txt:` PRC adds VIN, KPA, LAO, CAM (after 504) and VIE adds PHI, LOS, CAM (after 306).
- `events/Sino_Indian_War.txt` and `Sino_India_Pact.2`: RAJ creates, then adds PAK (see 83–84).

## Dead content and inactive sites

- `decisions/MD4_NATO.txt:179–228`: `call_nato_to_arms` has `allowed = always = no` and `visible = always = no`. Dead. Its NATO creation (214) is also dead.
- `common/national_focus/Trees for 0.35/`: contains `PRC_50s_New.txt:4960`, `SOV_test_tree.txt`, and `stalintreereworknew.txt`. No `load_focus_tree` reference found, and `Historical_AI_Rework_Documentation.md:148` and `SOV_alternate_strategy_plan.txt:26,231` mark it outdated.
- `common/national_focus/OUTDATED_PRC_50s_Rework.txt:5896` (plus `OUTDATED_PRC_50s.txt` and `OUTDATED_PRC_60s.txt` listed in `.cwic-log-strip/last-strip.json`): treated as outdated. `[INFERENCE]` that it is not loaded.
- `national_focus/SAF_1960s.txt` (site 61): loaded only from `IC_scripted_effects.txt:1335` (conditional) and `decisions/debug_decisions.txt:835`. Reachability depends on the conditional.
- Commented-out sites: `PRC_SOV_50s.txt:2868`, `events/Egypt.txt:702`, `events/_NATO_system.txt:285`, `FRA - France.txt:1020`.
- `common/national_focus/Toberemoved/50s_SYR.txt:1869` (generic "Arab Kingdom of Syria"): excluded from main table.
- Backups, listed separately (not in the live table):
  - `CWIC Backup/Backup/OTHER STUFF/Korea.txt:65` (legacy `north_korean_faction`).
  - `CWIC Backup/misc/ENG_1950s.txt:5324` (legacy "The Commonwealth").
  - `CWIC Backup/misc/egypt_60s_focus.txt:1849` (legacy "The Cairo Pact").
  - `misc/*.xh4prj` files are project files, not script.

## Risky sites

### Dismantle

- `events/_NATO.txt:582` and `:723`: `dismantle_faction` on FRA and ENG (their EDC/NATO memberships) right after `create_faction_from_template` NATO. Dismantles factions created by the script (EDC at `:242`), but the NATO creation at `:581`/`:722` is unguarded.
- `events/Russia_1990s.txt:58` and `:87`: `RUS dismantle_faction` before creating CSTO, unguarded. Dismantles faction created at `CSTO.1` (script-created).
- `events/SovietUnion_Focus_Events.txt:2223`: guarded by `is_faction_leader`, but dismantles SOV's own cominform faction.
- `focus/national_focus/VIN_50s.txt:946`: VIN dismantles its own VM faction, unguarded.
- `events/aplwun.txt:504`: PRC dismantles PRC's own faction (from `:211`), unguarded.
- `scripted_effects/FRE_Indochina_Effects.txt:3066–3070`: leader-only dismantle under migration, guarded by `is_in_faction` checks.

### Unguarded legacy `create_faction =` (all about 27; list)

`Indonesia.txt:603,607`; `KMT`: none; `arab_league_decisions.txt:881`; `60s_ITA.txt:5072`; `PRC_SOV_60s.txt:3592`; `SOV_WW3_1950s.txt:365,907,951`; `_NATO_system.txt:58`; `ColdWarUprisings.txt:702`; `CubanMissileCrisis.txt:788`; `_WW3.txt:193,196,217,220`; `LBA - Libya.txt:485`; `Libya70s.txt` (generic, not legacy); `KPA_Focus_Events` (generic); `Congo`: none; `OUTDATED_PRC_50s_Rework.txt:5896`.

### Adding members that may already be in a faction (no guard)

- `Congo.txt:1083`, `:1494`, `:1548`: COG is added to two factions (Simbas at 644, Rwanda & Allies at 1494); SKS is added to Simbas (644) and to Uganda & Allies (1548).
- `Kenya.txt:788`: `ZIM add_to_faction = SAF` assumes SAF leads a faction; KEN creates the faction.
- `Kenya.txt:972`: TTWO adds eight members without checks.
- `Libya.txt:36`: `LBA add_to_faction = ROOT` runs before LBA creates its faction.
- `Korean_War.txt:248`: USA (already a NATO leader) creates a second faction.
- `arab_league_decisions.txt:881,931`: unguarded creation and target add.
- `CubanMissileCrisis.txt:788`, `ColdWarUprisings.txt:702`: legacy NATO creation when NATO may already exist `[INFERENCE]`.

### Duplicate creations (same role, same name)

- "NATO": `_NATO.txt:581`, `:722`, `_NATO_system.txt:58`, `ColdWarUprisings.txt:702`, `CubanMissileCrisis.txt:788`.
- "Islamic Legion": `Libya70s.txt:57` and `LBA:485`.
- "Anti-Chinese Coalition": `CMC_Expansion.txt:567`, `:694`, `:736`, `:805`, `:847`, `Sino_Indian_War.txt:1164,1191`.
- "Anti-Turkish Alliance": `Third_Balkan_War.txt:813,930`.
- "Bangladesh Liberation Front": `Bangladesh_War.txt:474,1275`.
- "People's Defense Coalition": `KPA_50s_Korean_War.txt:26`, `KPA_50s_Political_legacy.txt:143`.
- "Anti-Communist Salvation Front": `_generic_decisions.txt:1832`, `YAN_50s_Victory.txt:1209`.
- "Beijing Pact": `aplwun.txt:504,599`, `PRC_SOV_60s.txt:3592`.
- WW3 PRC factions: `SOV_WW3_1950s.txt:907,951` (different names, same creator).
- WW3 Middle East: `_WW3.txt:193,196,217,220` (both events create JOR and ISR factions, unguarded).

Next steps for the main agent: verify the trigger chains for `Congo` (IC_scripted_effects 11337/11358/11438) and `_WW3` before migrating, and decide whether duplicated names are the same event fired twice or two valid events.