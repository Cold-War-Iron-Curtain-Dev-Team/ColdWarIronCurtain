"""Generate the historical UN resolution schedule for CWIC.

Run from anywhere:  python _tools/un_resolutions/generate.py

Writes
  Cold War Iron Curtain/common/scripted_effects/UN_historical_schedule.txt
  the GENERATED UN HISTORICAL TITLES blocks in
  Cold War Iron Curtain/common/scripted_localisation/IC_localisation.txt

Each entry queues one vote through UN_QUEUE_SCRIPTED_RESOLUTION during an
8-day window starting on its historical date. The weekly UNS tick lands in that
window once (twice at most, which the queue de-duplicates), so no per-resolution
flags are stored in the save. The queue itself skips votes that would do nothing
(target gone, sanction already applied, nothing to lift).

IDs: SC n -> n; GA n (to 1975) -> 100000+n; GA s/n -> 200000+s*1000+n;
GA ES-s/n -> 300000+s*1000+n. Extra targets of one resolution add 1,000,000
per target (HOI4 variables top out near 2,147,483). Legacy 1949 ids are kept.

Excluded on purpose: resolutions whose wars already have scripted event chains
(Korea 82-84, Suez 997, 242, 338, Falklands 502, Gulf 660/662/678, Iran-Iraq
479/598, Cyprus 353, Katanga 161/169, Karabakh, India-Pakistan 211/307,
Kashmir 91/122), Eritrea 390 and Spain 386 (focus-driven), PRC seat 2758
(Japan focus), memberships, and 1244 (no fitting type).
"""
from __future__ import annotations

import datetime as dt
import re
from pathlib import Path

MOD = Path(__file__).resolve().parents[2] / 'Cold War Iron Curtain'
SCHEDULE = MOD / 'common/scripted_effects/UN_historical_schedule.txt'
SCRIPTED_LOC = MOD / 'common/scripted_localisation/IC_localisation.txt'

APARTHEID = 'SAF = { check_variable = { apartheidValue > 0 } }'
NO_APARTHEID = 'SAF = { NOT = { check_variable = { apartheidValue > 0 } } }'


def war(t):
    return f'{t} = {{ OR = {{ has_war = yes has_civil_war = yes }} }}'


def war_with(a, b):
    return f'{a} = {{ has_war_with = {b} }}'


def owns(t, state):
    return f'{state} = {{ is_owned_by = {t} }}'


def passed(rid):
    return f'is_in_array = {{ array = UNS.un_historical_resolution_id_historical value = {rid} }}'


def not_dem(t):
    return f'{t} = {{ NOT = {{ has_government = democratic }} }}'


def sc(n):
    return n


def ga(n):
    return 100000 + n


def ga_s(session, n):
    return 200000 + session * 1000 + n


def ga_es(session, n):
    return 300000 + session * 1000 + n


# (date, id, title, [(action, target, state, cond)...], proposer)
# Extra (action, target) pairs on one resolution get id + k*1,000,000.
R = []


def res(date, rid, title, *parts, proposer='UNS'):
    R.append((date, rid, title, parts, proposer))


def p(action, target='0', state=0, cond=''):
    return (action, target, state, cond)


# ---- 1949-1959 -------------------------------------------------------------
res('1949.8.11', 1949073, 'UN Resolution on the Palestine Armistice Agreements', p(10, 'ISR'))
res('1949.9.27', 1949075, 'UN Resolution on UN Commission Expenses for India-Pakistan',
    p(10, 'RAJ', cond='country_exists = PAK RAJ = { NOT = { has_war_with = PAK } } '
                      'NOT = { UNS = { has_country_flag = UN_Kashmir_Refferendum_Active } }'))
res('1949.10.5', 1949076, 'UN Resolution on UN Observers in Indonesia', p(10, 'INO'))
res('1949.11.18', ga(288), 'UNGA Resolution 288: Threats to the Independence of Greece',
    p(2, 'ALB'), p(2, 'BUL'))
res('1949.11.21', ga(289), 'UNGA Resolution 289: Independence of Libya', p(16, 'LBA'))
res('1951.2.1', ga(498), 'UNGA Resolution 498: Chinese Intervention in Korea',
    p(2, 'PRC', cond=war_with('PRC', 'KOR')))
res('1951.5.18', ga(500), 'UNGA Resolution 500: Strategic Embargo on China and North Korea',
    p(6, 'PRC', cond=war_with('PRC', 'KOR')), p(6, 'KPA', cond=war_with('KPA', 'KOR')))
res('1953.4.23', ga(707), 'UNGA Resolution 707: Foreign Forces in Burma', p(2, 'CHI'))
res('1956.11.4', ga(1004), 'UNGA Resolution 1004: The Situation in Hungary', p(0, 'SOV', cond=war('HUN')))
res('1956.11.5', ga(1000), 'UNGA Resolution 1000: UN Emergency Force', p(10, 'EGY', cond='EGY = { has_war = yes }'))
res('1958.6.11', sc(128), 'UNSC Resolution 128: UN Observation Group in Lebanon', p(10, 'LEB'))
res('1959.10.21', ga(1353), 'UNGA Resolution 1353: The Question of Tibet',
    p(0, 'PRC', cond='any_state = { is_core_of = TIB is_owned_by = PRC }'))

# ---- 1960-1969 -------------------------------------------------------------
res('1960.4.1', sc(134), 'UNSC Resolution 134: The Sharpeville Massacre', p(0, 'SAF', cond=APARTHEID))
res('1960.7.14', sc(143), 'UNSC Resolution 143: UN Operation in the Congo', p(10, 'DOC'))
res('1960.12.19', ga(1573), 'UNGA Resolution 1573: Algerian Self-Determination', p(16, 'ALG'))
res('1961.7.22', sc(164), 'UNSC Resolution 164: The Bizerte Crisis', p(11, 'TUN', cond=war_with('TUN', 'FRA')))
res('1961.12.20', ga(1723), 'UNGA Resolution 1723: Tibetan Self-Determination', p(16, 'TIB'))
res('1962.9.21', ga(1752), 'UNGA Resolution 1752: UN Temporary Executive Authority', p(10, 'WPA'))
res('1962.11.6', ga(1761), 'UNGA Resolution 1761: Sanctions against Apartheid', p(5, 'SAF', cond=APARTHEID))
res('1963.6.11', sc(179), 'UNSC Resolution 179: UN Yemen Observation Mission', p(10, 'YEM'))
res('1963.7.31', sc(180), 'UNSC Resolution 180: Portuguese Territories in Africa',
    p(1, 'POR', cond='POR = { any_owned_state = { is_on_continent = africa } }'))
res('1963.8.7', sc(181), 'UNSC Resolution 181: Arms Embargo on South Africa', p(6, 'SAF', cond=APARTHEID))
res('1964.3.4', sc(186), 'UNSC Resolution 186: UN Peacekeeping Force in Cyprus', p(10, 'CYP'))
res('1965.5.14', sc(203), 'UNSC Resolution 203: The Dominican Crisis', p(11, 'DOM', cond=war('DOM')))
res('1965.11.12', sc(216), 'UNSC Resolution 216: Rhodesian Declaration of Independence', p(1, 'ZIM'))
res('1965.12.16', ga(2065), 'UNGA Resolution 2065: Question of the Falkland Islands',
    p(9, 'ARG', 299, cond=owns('ENG', 299)))
res('1966.10.27', ga(2145), 'UNGA Resolution 2145: The South West Africa Mandate',
    p(1, 'SAF', cond='any_state = { is_core_of = NMB is_owned_by = SAF }'))
res('1966.12.16', sc(232), 'UNSC Resolution 232: Sanctions on Rhodesia', p(5, 'ZIM'))
res('1967.12.19', ga(2353), 'UNGA Resolution 2353: Question of Gibraltar', p(9, 'SPR', 118, cond=owns('ENG', 118)))
res('1968.5.29', sc(253), 'UNSC Resolution 253: Comprehensive Sanctions on Rhodesia', p(3, 'ZIM'))

# ---- 1970-1979 -------------------------------------------------------------
res('1970.11.23', sc(290), 'UNSC Resolution 290: Portuguese Aggression against Guinea',
    p(1, 'POR', cond='POR = { any_owned_state = { is_on_continent = africa } }'))
res('1973.10.25', sc(340), 'UNSC Resolution 340: UN Emergency Force II', p(10, 'EGY'))
res('1974.5.31', sc(350), 'UNSC Resolution 350: UN Disengagement Observer Force', p(10, 'SYR'))
res('1974.11.22', ga(3236), 'UNGA Resolution 3236: Question of Palestine', p(16, 'PAL'))
res('1975.11.6', sc(380), 'UNSC Resolution 380: The Green March', p(11, 'MOR'))
res('1975.12.22', sc(384), 'UNSC Resolution 384: East Timor', p(16, 'TIM'))
res('1976.6.19', sc(392), 'UNSC Resolution 392: The Soweto Uprising', p(0, 'SAF', cond=APARTHEID))
res('1977.11.4', sc(418), 'UNSC Resolution 418: Mandatory Arms Embargo on South Africa', p(6, 'SAF', cond=APARTHEID))
res('1978.3.19', sc(425), 'UNSC Resolution 425: UN Interim Force in Lebanon', p(10, 'LEB'))
res('1978.9.29', sc(435), 'UNSC Resolution 435: Namibian Independence', p(16, 'NMB'))
res('1979.12.4', sc(457), 'UNSC Resolution 457: The Tehran Hostage Crisis',
    p(0, 'PER', cond='PER = { OR = { has_government = islamism has_government = radical_shiaism } }'))
res('1979.12.21', sc(460), 'UNSC Resolution 460: Ending Sanctions on Rhodesia', p(14, 'ZIM'), p(18, 'ZIM'))

# ---- 1980-1989 -------------------------------------------------------------
res('1980.1.14', ga_es(6, 2), 'UNGA Resolution ES-6/2: The Situation in Afghanistan',
    p(2, 'SOV', cond='OR = { SOV = { has_war_with = AFG } AFG = { is_subject_of = SOV } }'))
res('1981.6.19', sc(487), 'UNSC Resolution 487: The Osirak Strike', p(7, 'ISR'))
res('1981.12.17', sc(497), 'UNSC Resolution 497: The Golan Heights', p(9, 'SYR', 759, cond=owns('ISR', 759)))
res('1983.11.2', ga_s(38, 7), 'UNGA Resolution 38/7: The Situation in Grenada', p(2, 'USA', cond=war_with('USA', 'GND')))
res('1983.11.18', sc(541), 'UNSC Resolution 541: Northern Cyprus', p(9, 'CYP', 912, cond=owns('NCY', 912)))
res('1988.4.25', sc(622), 'UNSC Resolution 622: UN Good Offices Mission in Afghanistan', p(10, 'AFG'))
res('1988.5.9', sc(612), 'UNSC Resolution 612: Chemical Weapons in the Iran-Iraq War',
    p(0, 'IRQ', cond=war_with('IRQ', 'PER')))
res('1988.8.9', sc(619), 'UNSC Resolution 619: UN Iran-Iraq Military Observer Group',
    p(10, 'IRQ', cond='IRQ = { NOT = { has_war_with = PER } }'))
res('1988.12.20', sc(626), 'UNSC Resolution 626: UN Angola Verification Mission', p(10, 'ANG'))
res('1989.2.16', sc(632), 'UNSC Resolution 632: UN Transition Assistance Group', p(10, 'NMB'))
res('1989.11.7', sc(644), 'UNSC Resolution 644: UN Observer Group in Central America', p(10, 'NIC'))
res('1989.12.29', ga_s(44, 240), 'UNGA Resolution 44/240: Intervention in Panama', p(2, 'USA', cond=war_with('USA', 'PAN')))

# ---- 1990-1999 -------------------------------------------------------------
KUWAIT = 'OR = { IRQ = { has_war_with = KUW } 656 = { is_owned_by = IRQ } }'
res('1990.8.6', sc(661), 'UNSC Resolution 661: Sanctions on Iraq', p(5, 'IRQ', cond=KUWAIT), p(3, 'IRQ', cond=KUWAIT))
res('1991.4.3', sc(687), 'UNSC Resolution 687: Disarmament of Iraq', p(8, 'IRQ', cond=passed(661)))
res('1991.4.5', sc(688), 'UNSC Resolution 688: Repression of the Iraqi Kurds', p(0, 'IRQ', cond=passed(661)))
res('1991.4.29', sc(690), 'UNSC Resolution 690: Referendum in Western Sahara', p(16, 'WES'))
res('1991.5.20', sc(693), 'UNSC Resolution 693: UN Observer Mission in El Salvador', p(10, 'ELS'))
res('1991.9.25', sc(713), 'UNSC Resolution 713: Arms Embargo on Yugoslavia', p(6, 'YUG', cond=war('YUG')))
res('1992.1.23', sc(733), 'UNSC Resolution 733: Arms Embargo on Somalia', p(6, 'SOM', cond=war('SOM')))
res('1992.2.21', sc(743), 'UNSC Resolution 743: UN Protection Force', p(10, 'CRO'))
res('1992.2.28', sc(745), 'UNSC Resolution 745: UN Transitional Authority in Cambodia', p(10, 'CAM'))
res('1992.3.31', sc(748), 'UNSC Resolution 748: Sanctions on Libya', p(6, 'LBA'))
res('1992.4.24', sc(751), 'UNSC Resolution 751: UN Operation in Somalia', p(10, 'SOM'))
res('1992.5.30', sc(757), 'UNSC Resolution 757: Sanctions on Yugoslavia', p(5, 'YUG', cond=war('YUG')))
res('1992.11.19', sc(788), 'UNSC Resolution 788: Arms Embargo on Liberia', p(6, 'LIB', cond=war('LIB')))
res('1992.12.3', sc(794), 'UNSC Resolution 794: Unified Task Force in Somalia', p(12, 'SOM', cond=war('SOM')))
res('1992.12.16', sc(797), 'UNSC Resolution 797: UN Operation in Mozambique', p(10, 'MZB'))
res('1993.3.31', sc(816), 'UNSC Resolution 816: No-Fly Zone over Bosnia', p(12, 'BOS', cond='BOS = { has_war = yes }'))
res('1993.5.11', sc(825), 'UNSC Resolution 825: North Korea and the NPT', p(7, 'KPA'))
res('1993.5.25', sc(827), 'UNSC Resolution 827: Tribunal for the Former Yugoslavia', p(0, 'YUG', cond=war('YUG')))
res('1993.6.16', sc(841), 'UNSC Resolution 841: Sanctions on Haiti',
    p(5, 'HAI', cond=not_dem('HAI')), p(6, 'HAI', cond=not_dem('HAI')))
res('1993.8.24', sc(858), 'UNSC Resolution 858: UN Observer Mission in Georgia', p(10, 'GEO'))
res('1993.9.15', sc(864), 'UNSC Resolution 864: Sanctions on UNITA', p(6, 'UNT'))
res('1993.9.22', sc(866), 'UNSC Resolution 866: UN Observer Mission in Liberia', p(10, 'LIB'))
res('1993.10.5', sc(872), 'UNSC Resolution 872: UN Assistance Mission for Rwanda', p(10, 'RWA'))
res('1993.10.8', ga_s(48, 1), 'UNGA Resolution 48/1: Lifting Sanctions on South Africa', p(14, 'SAF', cond=NO_APARTHEID))
res('1993.11.11', sc(883), 'UNSC Resolution 883: Libyan Asset Freeze', p(3, 'LBA', cond=passed(748)))
res('1994.5.17', sc(918), 'UNSC Resolution 918: Arms Embargo on Rwanda', p(6, 'RWA', cond=war('RWA')))
res('1994.5.25', sc(919), 'UNSC Resolution 919: Ending the Arms Embargo on South Africa', p(15, 'SAF', cond=NO_APARTHEID))
res('1994.6.22', sc(929), 'UNSC Resolution 929: Operation Turquoise', p(12, 'RWA', cond=war('RWA')))
res('1994.7.31', sc(940), 'UNSC Resolution 940: Restoring Democracy in Haiti', p(13, 'HAI', cond=not_dem('HAI')), proposer='USA')
res('1994.9.29', sc(944), 'UNSC Resolution 944: Ending Sanctions on Haiti',
    p(14, 'HAI', cond='HAI = { has_government = democratic }'), p(15, 'HAI', cond='HAI = { has_government = democratic }'))
res('1994.11.8', sc(955), 'UNSC Resolution 955: Tribunal for Rwanda', p(0, 'RWA', cond=war('RWA')))
res('1994.12.16', sc(968), 'UNSC Resolution 968: UN Mission of Observers in Tajikistan', p(10, 'TAJ'))
res('1995.12.15', sc(1031), 'UNSC Resolution 1031: Implementation Force in Bosnia', p(12, 'BOS'))
res('1996.1.15', sc(1037), 'UNSC Resolution 1037: Eastern Slavonia',
    p(9, 'CRO', 163, cond='163 = { NOT = { is_owned_by = CRO } }'))
res('1996.4.26', sc(1054), 'UNSC Resolution 1054: Sanctions on Sudan', p(4, 'SUD'))
res('1996.10.1', sc(1074), 'UNSC Resolution 1074: Ending Sanctions on Yugoslavia', p(14, 'YUG', cond='YUG = { has_war = no }'))
res('1997.1.20', sc(1094), 'UNSC Resolution 1094: UN Verification Mission in Guatemala', p(10, 'GUA'))
res('1997.3.28', sc(1101), 'UNSC Resolution 1101: Multinational Protection Force for Albania', p(12, 'ALB', cond=war('ALB')))
res('1997.8.28', sc(1127), 'UNSC Resolution 1127: Travel Ban on UNITA', p(4, 'UNT'))
res('1997.10.8', sc(1132), 'UNSC Resolution 1132: Sanctions on the Sierra Leone Junta',
    p(6, 'SIE', cond=war('SIE')), p(5, 'SIE', cond=war('SIE')))
res('1998.3.31', sc(1160), 'UNSC Resolution 1160: Kosovo Arms Embargo', p(6, 'YUG'))
res('1998.6.6', sc(1172), 'UNSC Resolution 1172: Indian and Pakistani Nuclear Tests',
    p(7, 'RAJ', cond='RAJ = { has_tech = atomic_weapons }'), p(7, 'PAK', cond='PAK = { has_tech = atomic_weapons }'))
res('1998.6.12', sc(1173), 'UNSC Resolution 1173: UNITA Asset Freeze', p(3, 'UNT'))
res('1998.6.26', sc(1177), 'UNSC Resolution 1177: The Ethiopia-Eritrea War', p(11, 'ETH', cond=war_with('ETH', 'ERI')))
res('1998.9.23', sc(1199), 'UNSC Resolution 1199: The Situation in Kosovo', p(0, 'YUG'))
res('1999.9.15', sc(1264), 'UNSC Resolution 1264: International Force for East Timor', p(12, 'TIM'))
res('1999.10.15', sc(1267), 'UNSC Resolution 1267: Sanctions on the Taliban', p(3, 'TAL'), p(4, 'TAL'))
res('1999.10.22', sc(1270), 'UNSC Resolution 1270: UN Mission in Sierra Leone', p(10, 'SIE'))
res('1999.10.25', sc(1272), 'UNSC Resolution 1272: UN Transitional Administration in East Timor', p(10, 'TIM'))
res('1999.11.30', sc(1279), 'UNSC Resolution 1279: UN Mission in the Congo', p(10, 'DOC'))
res('1999.12.17', sc(1284), 'UNSC Resolution 1284: UN Monitoring Commission for Iraq', p(8, 'IRQ', cond=passed(687)))

# ---- 2000-2008 -------------------------------------------------------------
res('2000.5.17', sc(1298), 'UNSC Resolution 1298: Arms Embargo on Ethiopia and Eritrea',
    p(6, 'ETH', cond=war_with('ETH', 'ERI')), p(6, 'ERI', cond=war_with('ERI', 'ETH')))
res('2000.9.15', sc(1320), 'UNSC Resolution 1320: UN Mission in Ethiopia and Eritrea', p(10, 'ERI'))
res('2000.12.19', sc(1333), 'UNSC Resolution 1333: Arms Embargo on the Taliban', p(6, 'TAL'))
res('2001.3.7', sc(1343), 'UNSC Resolution 1343: Sanctions on Liberia', p(4, 'LIB'), p(5, 'LIB'))
res('2001.9.10', sc(1367), 'UNSC Resolution 1367: Ending the Arms Embargo on Yugoslavia', p(15, 'YUG'))
res('2001.9.28', sc(1372), 'UNSC Resolution 1372: Lifting Sanctions on Sudan', p(19, 'SUD'))
res('2001.12.20', sc(1386), 'UNSC Resolution 1386: International Security Assistance Force', p(12, 'AFG'))
res('2002.5.17', sc(1412), 'UNSC Resolution 1412: Suspending the UNITA Travel Ban', p(19, 'UNT'))
res('2002.11.8', sc(1441), 'UNSC Resolution 1441: Iraqi Disarmament', p(8, 'IRQ'))
res('2002.12.9', sc(1448), 'UNSC Resolution 1448: Ending Sanctions on UNITA', p(14, 'UNT'), p(15, 'UNT'), p(18, 'UNT'))
res('2003.5.22', sc(1483), 'UNSC Resolution 1483: Ending Sanctions on Iraq', p(14, 'IRQ'), p(18, 'IRQ'))
res('2003.5.30', sc(1484), 'UNSC Resolution 1484: Operation Artemis', p(12, 'DOC'))
res('2003.9.12', sc(1506), 'UNSC Resolution 1506: Ending Sanctions on Libya', p(14, 'LBA'), p(15, 'LBA'), p(18, 'LBA'))
res('2003.9.19', sc(1509), 'UNSC Resolution 1509: UN Mission in Liberia', p(10, 'LIB'))
res('2004.2.27', sc(1528), 'UNSC Resolution 1528: UN Operation in Cote d\'Ivoire', p(10, 'IVO'))
res('2004.3.12', sc(1532), 'UNSC Resolution 1532: Freezing the Assets of Charles Taylor', p(3, 'LIB'))
res('2004.4.30', sc(1542), 'UNSC Resolution 1542: UN Stabilisation Mission in Haiti', p(10, 'HAI'))
res('2004.5.21', sc(1545), 'UNSC Resolution 1545: UN Operation in Burundi', p(10, 'BRD'))
res('2004.7.30', sc(1556), 'UNSC Resolution 1556: Darfur Arms Embargo', p(6, 'SUD', cond=war('SUD')))
res('2004.9.2', sc(1559), 'UNSC Resolution 1559: Foreign Forces in Lebanon', p(2, 'SYR'))
res('2004.11.15', sc(1572), 'UNSC Resolution 1572: Arms Embargo on Cote d\'Ivoire', p(6, 'IVO'), p(4, 'IVO'))
res('2005.3.29', sc(1591), 'UNSC Resolution 1591: Sanctions over Darfur', p(4, 'SUD'), p(3, 'SUD'))
res('2005.10.31', sc(1636), 'UNSC Resolution 1636: The Hariri Assassination', p(4, 'SYR'))
res('2006.7.15', sc(1695), 'UNSC Resolution 1695: North Korean Missile Tests', p(7, 'KPA'))
res('2006.7.31', sc(1696), 'UNSC Resolution 1696: Iranian Uranium Enrichment', p(7, 'PER'))
res('2006.8.11', sc(1701), 'UNSC Resolution 1701: The Lebanon War', p(11, 'ISR', cond=war_with('ISR', 'LEB')))
res('2006.10.14', sc(1718), 'UNSC Resolution 1718: North Korean Nuclear Test', p(6, 'KPA'), p(4, 'KPA'), p(3, 'KPA'))
res('2006.12.23', sc(1737), 'UNSC Resolution 1737: Sanctions on Iran', p(3, 'PER'))
res('2007.1.23', sc(1740), 'UNSC Resolution 1740: UN Mission in Nepal', p(10, 'NEP'))
res('2007.3.24', sc(1747), 'UNSC Resolution 1747: Iranian Arms Export Ban', p(6, 'PER'))
res('2007.7.31', sc(1769), 'UNSC Resolution 1769: UN-AU Mission in Darfur', p(10, 'SUD'))
res('2007.9.25', sc(1778), 'UNSC Resolution 1778: UN Mission in Chad and the CAR', p(10, 'CHA'))
res('2008.3.3', sc(1803), 'UNSC Resolution 1803: Iranian Travel Bans', p(4, 'PER'))
res('2008.6.2', sc(1816), 'UNSC Resolution 1816: Piracy off Somalia', p(12, 'SOM', cond=war('SOM')))

# Historical ids queued from events or focuses rather than the schedule; they
# only need titles. (Ids that are also scheduled, e.g. 143 and 101353, are
# titled from the schedule.)
TITLES_ONLY = {
    1949001: 'UN Resolution on Dutch Military Action in Indonesia',  # Indonesian_Independence_War event
}

ID_CAP = 2_147_483
WINDOW_DAYS = 8


def parse(d):
    y, m, dd = (int(x) for x in d.split('.'))
    return dt.date(y, m, dd)


def fmt(d):
    return f'{d.year}.{d.month}.{d.day}'


def entries():
    out = []
    seen = set()
    for date, rid, title, parts, proposer in R:
        for k, (action, target, state, cond) in enumerate(parts):
            vid = rid + k * 1_000_000
            if vid in seen:
                raise SystemExit(f'duplicate id {vid}')
            if vid >= ID_CAP:
                raise SystemExit(f'id {vid} over the variable cap')
            if not 0 <= action <= 19:
                raise SystemExit(f'bad action {action} on {vid}')
            seen.add(vid)
            out.append((parse(date), vid, title, action, target, state, cond, proposer))
    out.sort(key=lambda e: (e[0], e[1]))
    return out


def schedule(es):
    L = ['# GENERATED by _tools/un_resolutions/generate.py - do not edit by hand.',
         '# Historical UN resolutions, queued in an 8-day window on their date.',
         '# Runs weekly in UNS scope (UN_HISTORICAL_RESOLUTION_WEEKLY_CHECK).',
         '',
         'UN_HISTORICAL_RESOLUTION_SCHEDULE = {']
    decades = sorted({e[0].year // 10 * 10 for e in es})
    for i, dec in enumerate(decades):
        kw = 'if' if i == 0 else 'else_if'
        L.append(f'    {kw} = {{')
        L.append(f'        limit = {{ date < {dec + 10}.1.1 }}')
        for d, vid, title, action, target, state, cond, proposer in es:
            if d.year // 10 * 10 != dec:
                continue
            lo, hi = d - dt.timedelta(days=1), d + dt.timedelta(days=WINDOW_DAYS)
            L.append(f'        # {title}')
            L.append('        if = {')
            L.append(f'            limit = {{ date > {fmt(lo)} date < {fmt(hi)}' + (f' {cond}' if cond else '') + ' }')
            tgt = f'{target}.id' if target != '0' else '0'
            body = [f'set_temp_variable = {{ un_q_target = {tgt} }}',
                    f'set_temp_variable = {{ un_q_action = {action} }}',
                    f'set_temp_variable = {{ un_q_state = {state} }}',
                    f'set_temp_variable = {{ un_q_id = {vid} }}']
            L += [f'            {b}' for b in body]
            if proposer == 'UNS':
                L.append('            UN_QUEUE_SCRIPTED_RESOLUTION = yes')
            else:
                L.append(f'            if = {{ limit = {{ country_exists = {proposer} }} {proposer} = {{ UN_QUEUE_SCRIPTED_RESOLUTION = yes }} }}')
            L.append('        }')
        L.append('    }')
    L.append('}')
    return '\n'.join(L) + '\n'


def loc_block(es, tag, var):
    lines = []
    done = set()
    titled = [(vid, title) for _d, vid, title, *_ in es] + list(TITLES_ONLY.items())
    for vid, title in sorted(titled):
        if vid in done:
            continue
        done.add(vid)
        lines.append('\ttext = {')
        lines.append(f'\t   trigger = {{ check_variable = {{ {var} = {vid} }} }}')
        lines.append(f'\t   localization_key = "{title}"')
        lines.append('\t}')
    head = f'\t# BEGIN GENERATED UN HISTORICAL TITLES ({tag}) - _tools/un_resolutions/generate.py'
    tail = f'\t# END GENERATED UN HISTORICAL TITLES ({tag})'
    return head, lines, tail


def write_loc(es):
    raw = SCRIPTED_LOC.read_bytes().decode('utf-8')
    nl = '\r\n' if '\r\n' in raw else '\n'
    s = raw.replace('\r\n', '\n')
    blocks = [('current', 'UNS.un_historical_resolution_id'),
              ('current-short', 'UNS.un_historical_resolution_id'),
              ('past', 'UNS.un_historical_resolution_id_historical^i')]
    for tag, var in blocks:
        head, lines, tail = loc_block(es, tag, var)
        rx = re.compile(r'\t# BEGIN GENERATED UN HISTORICAL TITLES \(' + re.escape(tag) + r'\)[^\n]*\n.*?\t# END GENERATED UN HISTORICAL TITLES \(' + re.escape(tag) + r'\)\n', re.S)
        if len(rx.findall(s)) != 1:
            raise SystemExit(f'marker block {tag} not found exactly once')
        s = rx.sub(lambda _m: '\n'.join([head, *lines, tail]) + '\n', s)
    SCRIPTED_LOC.write_bytes(s.replace('\n', nl).encode('utf-8'))


def main():
    es = entries()
    SCHEDULE.write_bytes(schedule(es).replace('\n', '\r\n').encode('utf-8'))
    write_loc(es)
    print(f'{len(R)} resolutions, {len(es)} queued votes')


if __name__ == '__main__':
    main()
