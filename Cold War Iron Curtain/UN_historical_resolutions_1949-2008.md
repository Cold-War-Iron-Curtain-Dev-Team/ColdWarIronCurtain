# Historical UN resolutions mappable to CWIC resolution types (1949–2008)

Candidates for `UN_QUEUE_SCRIPTED_RESOLUTION`. Compiled from memory: **verify numbers/dates before scripting.**

**Implemented:** the scheduled set lives in `_tools/un_resolutions/generate.py` (repo root). Edit the table there and rerun it to regenerate `common/scripted_effects/UN_historical_schedule.txt` and the titles in `IC_localisation.txt`. The generator's docstring lists the exclusions. New types: 18 = unfreeze assets, 19 = lift sanctions on officials; all four sanctions now last until lifted.
★ = strong fit / high-impact. SC = Security Council, GA = General Assembly. Tags are best guesses from `history/countries`.

## Type key (`un_q_action`)
| # | Type | # | Type |
|---|---|---|---|
| 0 | Condemn human rights violations | 9 | Status of a state (`un_q_state`) |
| 1 | Condemn colonialism | 10 | Peacekeepers |
| 2 | Influence containment | 11 | Mediation / ceasefire (hits target's enemies) |
| 3 | Freeze national assets | 12 | Intervention (generic UN force) |
| 4 | Sanction officials (travel bans etc.) | 13 | Coalition war against target |
| 5 | Trade sanctions | 14 | Remove trade sanctions |
| 6 | Arms embargo | 15 | Remove arms embargo |
| 7 | Halt nuclearisation | 16 | Freedom for target's people (release cores) |
| 8 | WMD disbandment | 17 | Membership |

## Already implemented
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1949 | (Dutch police action) | 5 | HOL | id 1949001, from Indonesia event |
| 1949 | SC 73 | 10 | ISR | Palestine armistice |
| 1949 | (Kashmir commission) | 10 | RAJ | id 1949075 |
| 1949 | (Indonesia observers) | 10 | INO | id 1949076 |

## 1949–1959
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1949 | GA 288 | 2 | ALB / BUL / YUG | Support to Greek guerrillas |
| 1949 | ★ GA 289 | 16 | LBA | Libyan independence by 1952 (also Somali trusteeship → 9) |
| 1950 | ★ SC 82–84 | 13 | KPA | Korea; USSR boycotting, so no veto |
| 1950 | GA 390 | 9 | ETH (Eritrea state) | Eritrea federation (ETH focus already narrates it) |
| 1951 | GA 498 | 2 | PRC | PRC named aggressor in Korea |
| 1951 | ★ GA 500 | 6 | PRC, KPA | Strategic embargo |
| 1951 | SC 91 | 9 | Kashmir state | Plebiscite (repeat: SC 122, 1957) |
| 1953 | GA 707 | 2 | CHI | KMT troops in Burma |
| 1955 | GA 995 | 17 | 16 states | "Package deal" admissions |
| 1956 | ★ GA 997 | 11 | ISR / ENG / FRA | Suez ceasefire |
| 1956 | ★ GA 1000 | 10 | EGY | UNEF I |
| 1956 | GA 1004 | 0 | SOV | Hungary |
| 1958 | SC 128 | 10 | LEB | UNOGIL |
| 1959 | GA 1353 | 0 | PRC | Tibet |

## 1960–1969
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1960 | SC 134 | 0 | SAF | Sharpeville |
| 1960 | ★ SC 143 | 10 | DOC | ONUC |
| 1960 | GA 1514 | 1 | POR / ENG / FRA etc. | Decolonisation declaration |
| 1960 | GA 1573 | 16 | ALG | Algerian self-determination |
| 1961 | ★ SC 161 / 169 | 13 | KAG | Force against Katanga |
| 1961 | SC 164 | 11 | FRA | Bizerte |
| 1961 | GA 1723 | 16 | TIB | Tibetan self-determination (repeat: GA 2079, 1965) |
| 1962 | GA 1752 | 10 | WPA | UNTEA, West New Guinea |
| 1962 | GA 1761 | 5 | SAF | Voluntary apartheid sanctions |
| 1963 | SC 179 | 10 | YEM | UNYOM |
| 1963 | SC 180 | 1 | POR | Portuguese territories (repeat: SC 290, 1970) |
| 1963 | SC 181 | 6 | SAF | Voluntary arms embargo |
| 1964 | ★ SC 186 | 10 | CYP | UNFICYP |
| 1965 | SC 203 | 11 | DOM | Dominican crisis |
| 1965 | ★ SC 211 | 11 | PAK / RAJ | Indo-Pak ceasefire |
| 1965 | SC 216 / 217 | 1 | ZIM (Rhodesia) | UDI condemned |
| 1965 | GA 2065 | 9 | Falklands | Negotiate sovereignty |
| 1966 | ★ SC 232 | 5 | ZIM | Selective mandatory sanctions |
| 1966 | GA 2145 | 1 | SAF | Namibia mandate ended (SC 264/276 follow) |
| 1967 | ★ SC 242 | 11 | ISR | Land for peace |
| 1967 | GA 2353 | 9 | Gibraltar | |
| 1968 | ★ SC 253 | 5 | ZIM | Comprehensive sanctions |

## 1970–1979
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1970 | SC 278 | 9 | Bahrain | Independence, Iran claim dropped |
| 1971 | ★ GA 2758 | 17 | PRC | China seat swaps from CHI |
| 1971 | SC 307 / GA 2793 | 11 | PAK / RAJ | Bangladesh war |
| 1973 | SC 335 | 17 | WGR, DDR | Both Germanys |
| 1973 | ★ SC 338 / 340 | 11 / 10 | ISR | Yom Kippur ceasefire, UNEF II |
| 1974 | SC 350 | 10 | SYR | UNDOF Golan |
| 1974 | SC 351 | 17 | BAN | |
| 1974 | ★ SC 353 | 11 | TUR | Cyprus invasion |
| 1974 | GA 3236 | 16 | PAL | Self-determination |
| 1975 | SC 380 | 11 | MOR | Green March |
| 1975 | ★ SC 384 | 16 | TIM | East Timor (repeat: SC 389) |
| 1976 | SC 392 | 0 | SAF | Soweto |
| 1977 | SC 413 | 17 | VIN | Vietnam |
| 1977 | ★ SC 418 | 6 | SAF | Mandatory arms embargo |
| 1978 | ★ SC 425 / 426 | 10 | LEB | UNIFIL |
| 1978 | ★ SC 435 | 16 | NMB | Namibian independence plan |
| 1979 | SC 457 / 461 | 0 | PER | Hostage crisis |
| 1979 | SC 460 | 14 | ZIM | Rhodesia sanctions end |
| 1979 | GA 34/22 | 2 | VIN | Cambodia occupation |

## 1980–1989
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1980 | ★ GA ES-6/2 | 2 | SOV | Afghanistan |
| 1980 | SC 478 | 9 | Jerusalem state | |
| 1980 | SC 479 | 11 | IRQ / PER | Iran–Iraq war |
| 1981 | SC 487 | 7 | ISR | Osirak, IAEA safeguards |
| 1981 | SC 497 | 9 | Golan state | Annexation null |
| 1982 | ★ SC 502 | 11 | ARG | Falklands withdrawal |
| 1983 | SC 541 | 9 | NCY | TRNC invalid |
| 1983 | GA 38/7 | 2 | USA | Grenada |
| 1986 | GA 41/38 | 2 | USA | Libya bombing |
| 1987 | ★ SC 598 | 11 | IRQ / PER | Ceasefire (UNIIMOG: SC 619, 1988) |
| 1988 | SC 612 | 0 / 8 | IRQ | Chemical weapons |
| 1988 | SC 622 | 10 | AFG | UNGOMAP |
| 1988 | SC 626 | 10 | ANG | UNAVEM |
| 1989 | SC 632 | 10 | NMB | UNTAG |
| 1989 | SC 644 | 10 | NIC / HON | ONUCA |
| 1989 | GA 44/240 | 2 | USA | Panama |

## 1990–1999
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 1990 | SC 660 | 11 | IRQ | Withdraw from Kuwait |
| 1990 | ★ SC 661 | 5 | IRQ | Sanctions |
| 1990 | SC 662 | 16 | KUW | Annexation null |
| 1990 | ★ SC 678 | 13 | IRQ | Gulf War |
| 1991 | ★ SC 687 | 8 | IRQ | Disarmament (follow-ups: SC 707, 715, 1284) |
| 1991 | SC 688 | 0 | IRQ | Kurds |
| 1991 | SC 690 | 10 / 9 | WES | MINURSO, referendum |
| 1991 | SC 693 | 10 | ELS | ONUSAL |
| 1991 | SC 702 / 709–711 | 17 | KOR, KPA / Baltics | Admissions |
| 1991 | ★ SC 713 | 6 | YUG | Arms embargo |
| 1992 | SC 733 / 751 | 6 / 10 | SOM | Arms embargo, UNOSOM |
| 1992 | SC 743 | 10 | CRO | UNPROFOR |
| 1992 | SC 745 | 10 | CAM | UNTAC |
| 1992 | ★ SC 748 | 6 | LBA | Lockerbie arms + air embargo |
| 1992 | ★ SC 757 | 5 | YUG | Sanctions |
| 1992 | SC 788 | 6 | LIB | Arms embargo |
| 1992 | ★ SC 794 | 12 | SOM | UNITAF |
| 1992 | SC 797 | 10 | MZB | ONUMOZ |
| 1993 | SC 816 / 836 | 12 | BOS | No-fly zone, safe areas |
| 1993 | SC 822 / 853 | 11 | ARM | Nagorno-Karabakh |
| 1993 | SC 825 | 7 | KPA | NPT withdrawal |
| 1993 | SC 827 | 0 | YUG | ICTY |
| 1993 | SC 841 | 5 / 6 | HAI | Oil and arms embargo |
| 1993 | SC 858 | 10 | GEO | UNOMIG |
| 1993 | SC 864 | 6 | UNT | UNITA embargo |
| 1993 | SC 866 | 10 | LIB | UNOMIL |
| 1993 | SC 872 | 10 | RWA | UNAMIR |
| 1993 | SC 883 | 3 | LBA | Asset freeze |
| 1993 | GA 48/1 | 14 | SAF | Economic sanctions lifted |
| 1994 | SC 918 | 6 | RWA | |
| 1994 | ★ SC 919 | 15 | SAF | Arms embargo ends |
| 1994 | SC 929 | 12 | RWA | Opération Turquoise |
| 1994 | ★ SC 940 | 13 | HAI | Restore Aristide (sanctions lifted: SC 944 → 14) |
| 1994 | SC 955 | 0 | RWA | ICTR |
| 1994 | SC 968 | 10 | TAJ | UNMOT |
| 1995 | SC 1031 | 12 | BOS | IFOR |
| 1996 | SC 1037 | 9 | CRO (E. Slavonia) | UNTAES |
| 1996 | SC 1054 | 4 | SUD | Mubarak assassination attempt |
| 1996 | SC 1074 | 14 | YUG | Sanctions end |
| 1997 | SC 1094 | 10 | GUA | MINUGUA |
| 1997 | SC 1101 | 12 | ALB | Operation Alba |
| 1997 | SC 1127 | 4 | UNT | Travel bans |
| 1997 | SC 1132 | 5 / 6 | SIE | Junta embargo |
| 1998 | SC 1160 | 6 | YUG | Kosovo |
| 1998 | ★ SC 1172 | 7 | RAJ, PAK | Nuclear tests |
| 1998 | SC 1173 | 3 | UNT | Asset freeze |
| 1998 | SC 1177 | 11 | ETH / ERI | |
| 1998 | SC 1199 | 0 | YUG | Kosovo |
| 1999 | ★ SC 1244 | 9 | KOS | UNMIK |
| 1999 | ★ SC 1264 | 12 | TIM | INTERFET (UNTAET: SC 1272 → 10) |
| 1999 | ★ SC 1267 | 3 | TAL | Taliban sanctions |
| 1999 | SC 1270 | 10 | SIE | UNAMSIL |
| 1999 | SC 1279 | 10 | DOC | MONUC |

## 2000–2008
| Year | Res. | Type | Target | Note |
|---|---|---|---|---|
| 2000 | SC 1298 | 6 | ETH, ERI | (UNMEE: SC 1320 → 10) |
| 2000 | SC 1306 | 5 | SIE | Diamonds |
| 2000 | SC 1333 | 6 | TAL | |
| 2001 | SC 1343 | 4 / 5 | LIB | Taylor regime |
| 2001 | SC 1367 | 15 | YUG | |
| 2001 | SC 1372 | 14 | SUD | |
| 2001 | ★ SC 1386 | 12 | AFG | ISAF |
| 2002 | ★ SC 1441 | 8 | IRQ | Final opportunity |
| 2002 | SC 1448 | 14 / 15 | UNT | UNITA sanctions end |
| 2003 | SC 1483 | 14 | IRQ | Sanctions end |
| 2003 | SC 1484 | 12 | DOC | Operation Artemis |
| 2003 | SC 1506 | 14 / 15 | LBA | Sanctions end |
| 2003 | SC 1509 | 10 | LIB | UNMIL |
| 2004 | SC 1528 / 1572 | 10 / 6 | IVO | UNOCI, arms embargo |
| 2004 | SC 1532 | 3 | LIB | Taylor assets |
| 2004 | SC 1542 | 10 | HAI | MINUSTAH |
| 2004 | SC 1545 | 10 | BRD | ONUB |
| 2004 | ★ SC 1556 | 6 | SUD | Darfur |
| 2004 | SC 1559 | 16 | LEB | Foreign forces out (aimed at SYR) |
| 2005 | SC 1591 | 4 | SUD | |
| 2005 | SC 1636 | 4 | SYR | Hariri suspects |
| 2006 | SC 1695 | 7 | KPA | Missiles |
| 2006 | ★ SC 1696 / 1737 | 7 / 3 | PER | Enrichment (repeat: SC 1747 2007, SC 1803 2008) |
| 2006 | ★ SC 1701 | 11 | ISR | Lebanon war, UNIFIL expanded |
| 2006 | ★ SC 1718 | 7 / 6 / 4 | KPA | Nuclear test |
| 2007 | SC 1740 | 10 | NEP | UNMIN |
| 2007 | ★ SC 1769 | 10 | SUD | UNAMID |
| 2007 | SC 1778 | 10 | CHA / CAR | MINURCAT |
| 2008 | SC 1816 | 12 | SOM | Piracy |

## Vetoed drafts (scripted votes that should fail)
1956 Suez (ENG / FRA veto), 1956 Hungary (SOV), 1961 Goa (SOV), 1968 Czechoslovakia (SOV), 1971 Bangladesh (SOV), 1980 Iran sanctions (SOV), 1980 Afghanistan (SOV), 1983 KAL 007 (SOV), 1983 Grenada (USA), 1986 Nicaragua (USA), 1989 Panama (USA / ENG / FRA), 2007 Myanmar (PRC / SOV-RUS), 2008 Zimbabwe (PRC / RUS).

## Notes
- **ID scheme breaks after 1995.** `YYYYNNN` assumes 3-digit SC numbers. Suggest SC id = SC number, and GA id = 100000 + resolution number (post-1976 GA: 100000 + session × 1000 + number). All of these stay under the HOI4 variable cap.
- **No type exists to lift asset freezes (3) or official sanctions (4).** These are 10-year timed ideas, so the lifting resolutions (1372, 1412, 1506) only map to 14 / 15.
- **Thematic resolutions have no target** (1373 counter-terrorism, 1540 non-proliferation, 1325) and don't fit.
- **Membership (17) applies to about 150 admissions.** Only the political ones are listed above.
