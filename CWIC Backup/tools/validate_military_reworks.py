#!/usr/bin/env python3
"""Static integration checks for the doctrine and NSB tank reworks.

Pass ``--doctrine-self-test`` to exercise the bounded parser and its negative
fixtures without changing the working tree.
"""

from __future__ import annotations

import re
import sys
import csv
import tempfile
import json
import unicodedata
from collections import Counter
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree


if "--help" in sys.argv:
    print(
        "Usage: python3 tools/validate_military_reworks.py "
        "[--doctrine-self-test] [--tank-self-test] [--tank-balance-report] "
        "[--tank-module-balance-report] [--tank-envelope-report]\n"
        "Default validation reads the tracked mod files and exits 0 on success or 1 "
        "on contract failures.\n"
        "--doctrine-self-test and --tank-self-test add in-memory negative fixtures.\n"
        "--tank-balance-report additionally reads the untracked workbook at the repository "
        "root and prints the reviewed scope; the tracked manifest is "
        "LogDocs/Tank_Designer/data/Balance_Target_Manifest.md."
    )
    sys.exit(0)


ROOT = Path(__file__).resolve().parents[2]
MOD = ROOT / "Cold War Iron Curtain"
TECH_DIR = MOD / "common/technologies"
# The 3187px right-edge ceiling contract was retired 2026-09-10. It encoded the
# gated-item decision to move two gridbox origins left, and the owner reverted
# that move after finding the clipping is cosmetic and unaffected by it. The
# structural gridbox checks below are kept; the edge comparison is not.
TECH_FOLDER_X_GRIDBOX = {
    "nsb_armor_folder": {
        6: "nsb_iw_armored_vehicles_tree",
        8: "nsb_iw_armored_vehicles_tree",
        -9: "nsb_engines_tree",
        -6: "nsb_engines_tree",
        9: "nsb_engines_tree",
        10: "nsb_engines_tree",
        12: "nsb_engines_tree",
        14: "nsb_engines_tree",
        15: "nsb_engines_tree",
        16: "nsb_engines_tree",
        18: "nsb_engines_tree",
        22: "nsb_armor_tree",
        26: "nsb_armor_tree",
        30: "nsb_armor_tree",
    },
    "nsb_armor_modules_folder": {
        0: "nsb_light_guns_tree",
        2: "nsb_light_guns_tree",
        4: "nsb_light_guns_tree",
        6: "nsb_light_guns_tree",
        8: "nsb_light_guns_tree",
        -8: "nsb_ammo_tree",
        -6: "nsb_ammo_tree",
        -4: "nsb_ammo_tree",
        -2: "nsb_ammo_tree",
        -1: "nsb_ammo_tree",
        10: "nsb_tank_design_tree",
        12: "nsb_tank_design_tree",
        14: "nsb_tank_design_tree",
        16: "nsb_tank_design_tree",
        18: "nsb_tank_design_tree",
        20: "nsb_tank_design_tree",
    },
}
MODULE_FILE = MOD / "common/units/equipment/modules/00_tank_modules.txt"
CHASSIS_FILE = MOD / "common/units/equipment/tank_chassis.txt"
ROLE_CHASSIS_FILE = MOD / "common/units/equipment/x_tank_chassis.txt"
MECHANIZED_FILE = MOD / "common/units/equipment/mechanized.txt"
HEAVY_MECHANIZED_FILE = MOD / "common/units/equipment/mechanized_heavy.txt"
# Owner decision 2026-09-11: APC and IFV are roles on the light tank hull, not
# standalone designer families. The legacy mechanized archetypes keep only their
# plain equipment rows for non-NSB games. Each retired carrier tier maps onto the
# newest light hull tier whose year does not exceed it, and the role-exclusive
# superstructure module carries the envelope the old chassis row used to carry.
# Phase 7, 2026-09-12: the module also carries `defense` and `breakthrough`,
# because the light tank hull curve gave a troop carrier tank breakthrough and
# tank defense, inverting the one thing that distinguishes it from a tank. The
# deltas are negative on breakthrough for exactly that reason.
# tier -> (module, technology, light hull tier, armour, cost, speed, defense, breakthrough)
APC_LADDER = {
    0: ("apc_open_troop_bay", "nsb_apc_hulls0", 2, 5, 2.6, 4, 5, -17),
    1: ("apc_enclosed_troop_bay", "nsb_apc_hulls1", 3, 5.5, 3.45, 4, 8, -16),
    2: ("apc_troop_compartment", "nsb_apc_hulls2", 4, 7, 4.3, 4.5, 8, -16),
    3: ("apc_sloped_troop_compartment", "nsb_apc_hulls3", 4, 9, 5.6, 5.5, 10, -15),
    4: ("apc_frontal_engine_layout", "nsb_apc_hulls4", 5, 10.5, 7.5, 6.5, 10, -15),
    5: ("apc_rear_ramp_compartment", "nsb_apc_hulls5", 6, 12, 8.4, 7, 10, -15),
    6: ("apc_spall_lined_compartment", "nsb_apc_hulls6", 7, 13.5, 9.3, 7.5, 13, -14),
    7: ("apc_modular_troop_capsule", "nsb_apc_hulls7", 8, 15, 11.2, 8.5, 13, -14),
}
IFV_LADDER = {
    0: ("ifv_fighting_compartment", "nsb_ifv_hulls0", 2, 12, 10.4, 5, 24, -8),
    1: ("ifv_enclosed_fighting_compartment", "nsb_ifv_hulls1", 3, 12.5, 11.65, 5.5, 29, -6),
    2: ("ifv_sloped_fighting_compartment", "nsb_ifv_hulls2", 3, 15.5, 14.8, 6.5, 30, -6),
    3: ("ifv_reinforced_fighting_compartment", "nsb_ifv_hulls3", 4, 16, 16.55, 6, 34, -4),
    4: ("ifv_frontal_engine_layout", "nsb_ifv_hulls4", 5, 17.5, 18.3, 6.5, 34, -4),
    5: ("ifv_rear_ramp_compartment", "nsb_ifv_hulls5", 6, 19, 20.05, 8, 35, -4),
    6: ("ifv_spall_lined_compartment", "nsb_ifv_hulls6", 7, 21.5, 21.8, 8.5, 39, -2),
    7: ("ifv_modular_fighting_capsule", "nsb_ifv_hulls7", 8, 24, 24.55, 9, 39, -2),
}
# Phase 7 armour envelope, owner ruling 2026-09-12: no carrier may exceed 70% of
# the same-year medium tank hull's armour, on either DLC profile. Before it a
# 2005 IFV carried 80 armour against the 2010 MBT's 75, and the relocated legacy
# rows carried the same inversion.
CARRIER_ARMOUR_CAP_RATIO = 0.7
MEDIUM_HULL_ARMOUR = (
    (1939, 30), (1942, 35), (1944, 40), (1950, 45), (1960, 50),
    (1970, 55), (1980, 60), (1990, 65), (2000, 70), (2010, 75),
)
LIGHT_HULL_ARMOUR = {
    0: 5, 1: 7.5, 2: 10, 3: 12.5, 4: 15, 5: 17.5, 6: 20, 7: 22.5, 8: 25, 9: 27.5,
}
CARRIER_GENERATION_YEARS = {
    "apc": (1947, 1950, 1960, 1965, 1975, 1985, 1995, 2005),
    "ifv": (1947, 1950, 1955, 1965, 1975, 1985, 1995, 2005),
}
# Hardness is set once per role family and never added by a module, so a design
# cannot drift off the carrier value by mounting a superstructure.
CARRIER_ROLE_HARDNESS = {"apc": 0.5, "ifv": 0.6}
# Phase 6, 2026-09-12: `mechanized_marine` consumes the APC role family, so the
# marine rows moved into it exactly as the 18 legacy carrier rows did in phase 5.
MARINE_ARCHETYPE = "mechanized_marine_equipment"
MARINE_ROLE = "light_tank_apc_chassis"
MARINE_ROWS = {1: (1944, 24), 2: (1950, 31), 3: (1965, 35), 4: (1985, 42), 5: (2005, 49)}
CARRIER_LADDERS = {"apc": APC_LADDER, "ifv": IFV_LADDER}
CARRIER_ARCHETYPES = {
    "apc": ("mechanized_equipment", MECHANIZED_FILE, "light_tank_apc_chassis", "flame"),
    "ifv": ("mechanized_heavy_equipment", HEAVY_MECHANIZED_FILE, "light_tank_ifv_chassis", "rocket"),
}
# The 2023 balance workbook is frozen and predates the carrier modules, so its
# module sheets can never carry these rows. They are authored values kept in
# script only, and the module balance report reports them as an explicit
# exemption instead of silently widening workbook coverage.
APC_SUPERSTRUCTURE_MODULES = tuple(row[0] for row in APC_LADDER.values())
APC_ARMAMENT_MODULES = (
    "apc_firing_ports",
    "apc_pintle_mg",
    "apc_cupola_hmg",
    "apc_remote_weapon_station",
)
IFV_SUPERSTRUCTURE_MODULES = tuple(row[0] for row in IFV_LADDER.values())
IFV_ARMAMENT_MODULES = tuple(f"ifv_autocannon_{tier}" for tier in range(8)) + tuple(
    f"ifv_atgm_launcher_{tier}" for tier in range(6)
)
TANK_SPECIAL_SLOT_COUNT = 15
TANK_DESIGNER_POSITIONS = 20
# Engine cap verified 2026-09-10: custom module slot windows 0-19 render; index
# 20 is silently dropped. The tank designer therefore has fifteen optional slots.
# Owner decision 2026-09-10: the tank designer's fifteen optional slots are
# fully specialized, so each category has one declared slot owner.
TANK_SPECIAL_SLOT_CATEGORIES = {
    1: {"tank_ammo_kinetic"},
    2: {"tank_ammo_he", "tank_ammo_chemical"},
    3: {"tank_fcs_aiming"},
    4: {"tank_fcs_optics"},
    5: {"tank_fcs_computer", "tank_fcs_radar"},
    6: {"tank_loader_manual_assist", "tank_loader_autoloader", "tank_loader_artillery"},
    7: {"tank_ammo_missile"},
    8: {"tank_protection_passive", "tank_external_fuel"},
    9: {"tank_protection_reactive"},
    10: {"tank_secondary_turret"},
    11: {"tank_protection_active"},
    12: {"tank_smoke"},
    13: {"tank_survivability"},
    14: {"tank_power_auxiliary"},
    15: {"tank_mine_clearing", "tank_engineering_blade"},
}
# Owner decision 2026-09-10: dissolving tank_mobility_auxiliary changes the
# 45 live module categories to 45 - 1 + 4 = 48, with the four replacement
# categories below.
TANK_MODULE_CATEGORY_COUNT = 45 - 1 + 4
TANK_LIMITED_CATEGORIES = (
    "tank_ammo_kinetic", "tank_ammo_chemical", "tank_ammo_missile", "tank_ammo_he",
    "tank_fcs_aiming", "tank_fcs_optics", "tank_fcs_computer", "tank_fcs_radar",
    "tank_loader_manual_assist", "tank_loader_autoloader", "tank_loader_artillery",
    "tank_protection_passive", "tank_protection_reactive", "tank_protection_active",
    "tank_survivability", "tank_smoke", "tank_secondary_turret",
    "tank_power_auxiliary", "tank_external_fuel", "tank_mine_clearing",
    "tank_engineering_blade",
)
# Owner decision 2026-09-10: these are the only modules moved out of the
# dissolved category, with each module assigned to its replacement purpose.
TANK_RECUT_MODULE_CATEGORIES = {
    **{f"APU_{index}": "tank_power_auxiliary" for index in range(7)},
    **{f"GT_APU_{index}": "tank_power_auxiliary" for index in range(4)},
    "Fuel_Tanks_0": "tank_external_fuel",
    "Mine_Plow_0": "tank_mine_clearing",
    "Mine_Plow_1": "tank_mine_clearing",
    "Mine_Roller_0": "tank_mine_clearing",
    "Mine_Roller_1": "tank_mine_clearing",
    "Dozer_0": "tank_engineering_blade",
    "Trench_Plow_0": "tank_engineering_blade",
}
AI_FILE = MOD / "common/ai_equipment/generic_tank.txt"
ENUM_FILE = MOD / "common/script_enums.txt"
VARIANT_EFFECT_FILE = MOD / "common/scripted_effects/CWIC_tank_designer_effects.txt"
FOCUS_EFFECT_FILE = MOD / "common/scripted_effects/CWIC_tank_focus_effects.txt"
NATIONAL_EFFECT_FILE = MOD / "common/scripted_effects/CWIC_national_tank_presets.txt"
NATIONAL_MANIFEST_FILE = ROOT / "LogDocs/Tank_Designer/data/National_Tank_Preset_Manifest.json"
NATIONAL_PRESETS = json.loads(NATIONAL_MANIFEST_FILE.read_text(encoding="utf-8"))["presets"]
CARRIER_MANIFEST_FILE = ROOT / "LogDocs/Tank_Designer/data/APC_IFV_Preset_Manifest.json"
NAMING_MANIFEST_FILE = ROOT / "LogDocs/Tank_Designer/data/Tank_Naming_Preset_Manifest.json"
NAMING_EFFECT_FILE = MOD / "common/scripted_effects/CWIC_national_armour_naming_presets.txt"
NAMING_PRESETS = json.loads(NAMING_MANIFEST_FILE.read_text(encoding="utf-8"))["presets"]
RESEARCH_NAMING_MANIFEST_FILE = ROOT / "LogDocs/Tank_Designer/data/Research_Naming_Manifest.json"
RESEARCH_NAMING_EFFECT_FILE = MOD / "common/scripted_effects/CWIC_research_armour_naming.txt"
CARRIER_MANIFEST = json.loads(CARRIER_MANIFEST_FILE.read_text(encoding="utf-8"))
CARRIER_PRESETS = CARRIER_MANIFEST["presets"]
FOCUS_FILES = (
    MOD / "common/national_focus/60s_Generic.txt",
    MOD / "common/national_focus/GRE_military_shared_1950s.txt",
    MOD / "common/national_focus/50s_FIN.txt",
)
NATIONAL_FOCUS_DIR = MOD / "common/national_focus"
LEGACY_ARMOUR_GRANT_PATH_EXCEPTIONS = frozenset(
    {
        "Cold War Iron Curtain/common/national_focus/FOR HOTFIX/70s_Pak_Notes_for_Reference_Only_Do_Not_Delete.txt",
        "Cold War Iron Curtain/common/national_focus/Need Finished/50s_TUR_new.txt",
        "Cold War Iron Curtain/common/national_focus/Need Finished/EGY_1950s_RCC.txt",
        "Cold War Iron Curtain/common/national_focus/OUTDATED_PRC_60s.txt",
        "Cold War Iron Curtain/common/national_focus/Old/ISR_50s_old.txt",
        "Cold War Iron Curtain/common/national_focus/Old/YUG_1950s.txt",
        "Cold War Iron Curtain/common/national_focus/Toberemoved/50s_SYR.txt",
        "Cold War Iron Curtain/common/national_focus/Toberemoved/60s_SYR.txt",
        "Cold War Iron Curtain/common/national_focus/Toberemoved/IRQ_Mid_1960s.txt",
        "Cold War Iron Curtain/common/national_focus/Trees for 0.35/stalintreereworknew.txt",
        "Cold War Iron Curtain/common/national_focus/Trees for 0.35/Japan/JAP_1950s.txt",
    }
)
TANK_ROLE_FILE = MOD / "common/units/need_for_tank_roles.txt"
TANK_ICON_FILE = MOD / "interface/cwic_tank_rework_icons.gfx"
TANK_LOC_FILE = MOD / "localisation/english/tank_modules_l_english.yml"
BALANCE_MANIFEST_FILE = ROOT / "LogDocs/Tank_Designer/data/Balance_Target_Manifest.md"
BALANCE_WORKBOOK_FILE = ROOT / "LogDocs/Tank_Designer/data/2023 - CWIC Tank Rework Balance.xlsx"
BALANCE_CSV_FILE = ROOT / "LogDocs/Tank_Designer/data/2023 - CWIC Tank Rework Balance(Total Balance Sheet Minimal).csv"
BALANCE_METRICS = (
    ("reliability", "C", True),
    ("hardness", "D", True),
    ("hard_attack", "E", False),
    ("soft_attack", "F", False),
    ("breakthrough", "G", False),
    ("defense", "H", False),
    ("armor", "I", False),
    ("piercing", "J", False),
    ("speed", "K", False),
    ("supply", "L", False),
    ("fuel_usage", "M", False),
    ("production_cost", "N", False),
)
# The two module tables deliberately retain their original stat columns.  The
# operation column added by Tier 3 is a compact audit trail for fields such as
# reliability, whose old percentage column cannot distinguish add_stats from
# multiply_stats by itself.
MODULE_BALANCE_COLUMNS = {
    "reliability": ("I", 8, None, None),
    "hardness": ("J", 9, None, None),
    "hard_attack": ("K", 10, "L", 11),
    "soft_attack": ("M", 12, "N", 13),
    "breakthrough": ("O", 14, "P", 15),
    "defense": ("Q", 16, "R", 17),
    "armor_value": ("S", 18, "T", 19),
    "ap_attack": ("U", 20, "V", 21),
    "maximum_speed": ("W", 22, "X", 23),
    "reconnaissance": ("Y", 24, "Z", 25),
    "entrenchment": ("AA", 26, None, None),
    "supply_consumption": ("AB", 27, "AC", 28),
    "fuel_consumption": ("AD", 29, "AE", 30),
    "air_attack": ("AF", 31, "AG", 32),
    "build_cost_ic": ("AH", 33, "AI", 34),
}
MODULE_FIELD_ALIASES = {
    "recon": "reconnaissance",
    "armor": "armor_value",
}
MODULE_RESOURCE_COLUMNS = {
    "electricity": ("AK", 36),
    "steel": ("AL", 37),
    "aluminium": ("AM", 38),
    "tungsten": ("AN", 39),
    "nuclear_materials": ("AO", 40),
}
MODULE_OPERATION_COLUMN = ("AP", 41)
MODULE_DISMANTLE_COLUMN = ("AJ", 35)
MODULE_SCRIPT_FIELDS = set(MODULE_BALANCE_COLUMNS) | set(MODULE_RESOURCE_COLUMNS) | {
    "dismantle_cost_ic",
}
MODULE_EXPLICIT_EXCLUSIONS = {
    "parent": "inheritance is retained in script and reported separately",
    "category": "designer eligibility metadata, not a numeric balance column",
    "allow_equipment_type": "designer eligibility metadata",
    "forbid_equipment_type": "designer eligibility metadata",
    "forbid_equipment_type_exact_match": "designer eligibility metadata",
    "allowed_module_categories": "designer eligibility metadata",
    "can_convert_from": "conversion metadata; convert_cost_ic is not a balance stat",
    "xp_cost": "designer XP policy is frozen by the manual",
    "abbreviation": "display metadata, checked by the existing contract",
    "sfx": "display metadata, outside the balance workbook",
    "icon": "display metadata, outside the balance workbook",
}
# These two cells are prose notes inherited from the source workbook's radar
# draft.  They occupy a percentage column, but are not numeric balance data;
# keep them as explicit annotations rather than silently treating arbitrary
# text as valid.
MODULE_SOURCE_ANNOTATIONS = {
    "Нужно ли добавить топливо в запас?",
    "????? ?? ???????? ??????? ? ??????",
}
# Owner decision 2026-09-10: the removed flame module is no longer
# script-owned.
SCRIPT_OWNED_MODULES = {
    "conventional_turret",
    "cwic_coaxial_mg",
    "cwic_hull_mg",
    "cwic_secondary_autocannon",
    "cwic_secondary_hmg",
    "external_gun",
    "fixed_superstructure",
    "heavy_fixed_superstructure",
    "heavy_open_gun",
    "light_lp_turret",
    "light_turret",
    "lp_turret",
    "medium_fixed_superstructure",
    "medium_open_gun",
    "open_gun",
    "oscillating_turret",
    "pintle_turret",
    "tank_anti_air_cannon",
    "tank_anti_air_cannon_2",
    "tank_anti_air_cannon_3",
    "tank_gasoline_engine",
}
OOB_DIR = MOD / "history/units"
HISTORY_DIR = MOD / "history/countries"
EQUIPMENT_DIR = MOD / "common/units/equipment"
# The legacy artillery, AA and destroyer rows now live in their designer role
# families. Their archetype shells remain because other content names them.
LEGACY_ARMOUR_ROLE_RELOCATIONS = {
    "spaag_equipment": (
        EQUIPMENT_DIR / "sp_aa.txt",
        "light_tank_aa_chassis",
        tuple(f"spaag_equipment_{tier}" for tier in range(1, 6)),
    ),
    "sp_artillery_equipment": (
        EQUIPMENT_DIR / "sp_art.txt",
        "medium_tank_artillery_chassis",
        tuple(f"sp_artillery_equipment_{tier}" for tier in range(1, 6)),
    ),
    "light_sp_artillery_equipment": (
        EQUIPMENT_DIR / "light_sp_art.txt",
        "light_tank_artillery_chassis",
        tuple(f"light_sp_artillery_equipment_{tier}" for tier in range(1, 6)),
    ),
    "heavy_sp_artillery_equipment": (
        EQUIPMENT_DIR / "heavy_sp_art.txt",
        "heavy_tank_artillery_chassis",
        tuple(f"heavy_sp_artillery_equipment_{tier}" for tier in range(1, 6)),
    ),
    "medium_tank_destroyer_equipment": (
        EQUIPMENT_DIR / "tank_destroyer.txt",
        "medium_tank_destroyer_chassis",
        tuple(f"medium_tank_destroyer_equipment_{tier}" for tier in range(1, 6)),
    ),
    "atgm_carrier_equipment": (
        EQUIPMENT_DIR / "atgm_carrier.txt",
        "light_tank_destroyer_chassis",
        tuple(f"atgm_carrier_equipment_{tier}" for tier in range(5)),
    ),
}
# The owner measured these direct stats on the surviving role-family siblings.
# `resources` is a nested stat block; all other entries are scalar keys.
LEGACY_ARMOUR_STAT_KEYS = (
    "maximum_speed",
    "defense",
    "breakthrough",
    "armor_value",
    "soft_attack",
    "hard_attack",
    "ap_attack",
    "build_cost_ic",
    "resources",
)
LEGACY_SPAA_STAT_KEYS = LEGACY_ARMOUR_STAT_KEYS + ("air_attack",)
TANK_ROLE_ARMOUR_BATTALIONS = {
    "light_armor": "light_tank_chassis",
    "medium_armor": "medium_tank_chassis",
    "heavy_armor": "heavy_tank_chassis",
}
REWIRED_TANK_ROLE_BATTALIONS = {
    "spaag": ("CWIC-Anti-Air.txt", "light_tank_aa_chassis"),
    "spaag_support": ("CWIC-Support-Units.txt", "light_tank_aa_chassis"),
    "sp_artillery": ("CWIC-Artillery.txt", "medium_tank_artillery_chassis"),
    "light_sp_artillery": ("CWIC-Artillery.txt", "light_tank_artillery_chassis"),
    "heavy_sp_artillery": ("CWIC-Artillery.txt", "heavy_tank_artillery_chassis"),
    "tank_destroyer": ("CWIC-Anti-Tank.txt", "medium_tank_destroyer_chassis"),
    "atgm_carrier": ("CWIC-Anti-Tank.txt", "light_tank_destroyer_chassis"),
}
# `add_equipment_to_stockpile` accepts type, amount, variant_name and producer.
# `creator` is only valid on `force_equipment_variants` and
# `add_equipment_production`; here the engine logs `Unexpected token: creator`
# and the grant is dropped. 246 grants carried it before 2026-09-08.
STOCKPILE_REJECTED_KEYS = ("creator",)
# Grants naming something that is not an equipment id. Each awards nothing and
# each needs its content owner to say what was meant, so they are recorded here
# rather than guessed at or deleted. None is tank-designer owned.
#   mp_uav_1                    technology (helicopter.txt); ISR_1980{,_nsb}.txt:486
#   light_tank_apc_equipment_3  derived_variant_name only; PHI_1950s.txt:586
#                               (was apc_equipment_1 before the 2026-09-11 cutover)
#   manpads_3                   undeclared; USA_80s_CIA.txt:1850,1872
#   cv_nav_bomber_equipment_6   undeclared; JAP_1950s.txt:437
#   armor_light, armor_medium, artillery_light, artillery_medium,
#   support_artillery           technology categories; PRC_50s_New.txt:2489-2509
STOCKPILE_TYPE_EXCEPTIONS = {
    "mp_uav_1",
    "light_tank_apc_equipment_3",
    "manpads_3",
    "cv_nav_bomber_equipment_6",
    "armor_light",
    "armor_medium",
    "artillery_light",
    "artillery_medium",
    "support_artillery",
}

# Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
# remains deliberately unspent and reserved for a future dedicated amphibious
# mechanized role.
FAMILY_ROLES = {
    "light": ("aa", "artillery", "destroyer", "apc", "ifv"),
    "medium": ("aa", "artillery", "destroyer", "apc", "ifv"),
    "heavy": ("artillery", "destroyer"),
}
FAMILY_TIERS = {"light": 10, "medium": 10, "heavy": 5}
# Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
# remains deliberately unspent and reserved for a future dedicated amphibious
# mechanized role; flame, ATGM, and heavy SPAAG designer roots are retired.
REMOVED_TANK_ROLE_ROOTS = {
    "light_tank_flame_chassis",
    "medium_tank_flame_chassis",
    "heavy_tank_flame_chassis",
    "heavy_tank_aa_chassis",
    "light_tank_atgm_chassis",
    "medium_tank_atgm_chassis",
}
REMOVED_TANK_TYPE_IDS = (
    REMOVED_TANK_ROLE_ROOTS
    | {
        f"{family}_tank_flame_chassis_{tier}"
        for family, count in FAMILY_TIERS.items()
        for tier in range(count)
    }
    | {f"heavy_tank_aa_chassis_{tier}" for tier in range(FAMILY_TIERS["heavy"])}
    | {
        f"{family}_tank_atgm_chassis_{tier}"
        for family in ("light", "medium")
        for tier in range(FAMILY_TIERS[family])
    }
    | {
        f"{family}_tank_atgm_chassis{suffix}{index}"
        for family, suffix, indices in (
            ("light", "t_equipment_", range(1, 7)),
            ("medium", "bt_equipment_", range(0, 10)),
        )
        for index in indices
    }
)
# Owner decision 2026-09-11 carrier role consolidation removes IFV blueprints
# rather than retaining a role the engine cannot safely switch.
REMOVED_TANK_BLUEPRINT_PATTERN = re.compile(
    r"^(?:tank_chassis_.*_tank_(?:amphibious|flame|atgm)|tank_chassis_heavy_tank_aa)\.gui$"
)
# Owner decision 2026-09-11 carrier role consolidation bounds OOB references
# to ten surviving roots because the engine exposes only five designer tokens.
ROLE_CHASSIS_PATTERN = "|".join(
    f"{family}_tank_(?:{'|'.join(roles)})" for family, roles in FAMILY_ROLES.items()
)
OOB_TANK_PATTERN = re.compile(
    rf"\b(?:(?:light|medium|heavy)_tank|(?:{ROLE_CHASSIS_PATTERN})|apc|ifv)_chassis_[0-9]+\b"
)
STARTING_VARIANT_EFFECT = "cwic_create_starting_tank_variants = yes"
# Manufacturer bloc tags sell tanks but never load an OOB of their own.
MANUFACTURER_BLOC_TAGS = {"CAP", "CUM"}
# `producer` on a stockpile/production request and `creator` on a forced
# variant both name the tag whose designer built the tank.
FOREIGN_CREATOR_PATTERN = re.compile(r'\b(?:producer|creator)\s*=\s*"?([A-Z]{3})"?')
REQUIRED_VARIANT_SLOTS = {
    "main_armament_slot",
    "turret_type_slot",
    "suspension_type_slot",
    "armor_type_slot",
    "engine_type_slot",
}
SECONDARY_MODULES = {
    "cwic_coaxial_mg": "nsb_iw_armored_vehicles",
    "cwic_hull_mg": "nsb_iw_armored_vehicles",
    "cwic_secondary_hmg": "nsb_iw_armored_vehicles",
    "cwic_secondary_autocannon": "nsb_aiming_devices2",
}
SECONDARY_ICON_PATHS = {
    "cwic_coaxial_mg": "gfx/interface/equipmentdesigner/tanks/Modules/Other Modules/LMG.png",
    "cwic_hull_mg": "gfx/interface/equipmentdesigner/tanks/Modules/Other Modules/LMG.png",
    "cwic_secondary_hmg": "gfx/interface/equipmentdesigner/tanks/Modules/Other Modules/HMG.png",
    "cwic_secondary_autocannon": "gfx/interface/equipmentdesigner/tanks/Modules/SPAAG/AFV Autocannons/Light autocannon 1960.png",
}
EXPORT_VARIANTS = {
    "CWIC Export Main Battle Tank 1942": "medium_tank_chassis_1",
    "CWIC Export Main Battle Tank 1944": "medium_tank_chassis_2",
    "CWIC Export Main Battle Tank 1950": "medium_tank_chassis_3",
    "CWIC Export Main Battle Tank 1960": "medium_tank_chassis_4",
    "CWIC Export Main Battle Tank 1970": "medium_tank_chassis_5",
    "CWIC Export Main Battle Tank 1980": "medium_tank_chassis_6",
    "CWIC Export Light Tank 1942": "light_tank_chassis_1",
    "CWIC Export Light Tank 1944": "light_tank_chassis_2",
    "CWIC Export Heavy Tank 1942": "heavy_tank_chassis_1",
    "CWIC Export Heavy Tank 1944": "heavy_tank_chassis_2",
    # The 1960 and 1965 carrier exports share light hull tier 4 after the
    # 2026-09-11 cutover, and both remain distinct named export designs.
    "CWIC Export Armored Personnel Carrier 1947": "light_tank_apc_chassis_2",
    "CWIC Export Armored Personnel Carrier 1950": "light_tank_apc_chassis_3",
    "CWIC Export Armored Personnel Carrier 1960": "light_tank_apc_chassis_4",
    "CWIC Export Armored Personnel Carrier 1965": "light_tank_apc_chassis_4",
    "CWIC Export Infantry Fighting Vehicle 1950": "light_tank_ifv_chassis_3",
    "CWIC Export Infantry Fighting Vehicle 1965": "light_tank_ifv_chassis_4",
}
LEGACY_ARMOUR_GRANT = re.compile(
    r"^(?:lt_equipment|mbt_equipment|ht_equipment|mechanized_equipment"
    r"|mechanized_heavy_equipment|mechanized_marine_equipment)(?:_\d+)?$"
)
UNMIGRATED_LEGACY_ARMOUR = frozenset(
    {"mechanized_equipment", "mechanized_equipment_1", "mechanized_equipment_2"}
    | {f"mechanized_marine_equipment_{tier}" for tier in range(1, 6)}
)
BOOKMARK_VARIANT_NAMES = {
    "heavy_tank_artillery_chassis_1": "Standard Heavy SPG 1942",
    "heavy_tank_artillery_chassis_3": "Standard Heavy SPG 1950",
    "heavy_tank_chassis_1": "Standard Heavy Tank 1942",
    "heavy_tank_chassis_2": "Standard Heavy Tank 1944",
    "heavy_tank_chassis_3": "Standard Heavy Tank 1950",
    "heavy_tank_chassis_4": "Standard Heavy Tank 1955",
    "light_tank_aa_chassis_1": "Standard Light SPAA 1942",
    "light_tank_aa_chassis_2": "Standard Light SPAA 1944",
    "light_tank_aa_chassis_3": "Standard Light SPAA 1950",
    "light_tank_artillery_chassis_1": "Standard Light SPG 1942",
    "light_tank_artillery_chassis_2": "Standard Light SPG 1944",
    "light_tank_artillery_chassis_3": "Standard Light SPG 1950",
    "light_tank_chassis_1": "Standard Light Tank 1942",
    "light_tank_chassis_2": "Standard Light Tank 1944",
    "light_tank_chassis_3": "Standard Light Tank 1950",
    "light_tank_chassis_4": "Standard Light Tank 1960",
    "light_tank_chassis_5": "Standard Light Tank 1970",
    "medium_tank_artillery_chassis_1": "Standard Main Battle SPG 1942",
    "medium_tank_artillery_chassis_2": "Standard Main Battle SPG 1944",
    "medium_tank_artillery_chassis_3": "Standard Main Battle SPG 1950",
    "medium_tank_chassis_0": "Standard Main Battle Tank 1939",
    "medium_tank_chassis_1": "Standard Main Battle Tank 1942",
    "medium_tank_chassis_2": "Standard Main Battle Tank 1944",
    "medium_tank_chassis_3": "Standard Main Battle Tank 1950",
    "medium_tank_chassis_4": "Standard Main Battle Tank 1960",
    "medium_tank_chassis_5": "Standard Main Battle Tank 1970",
    "medium_tank_chassis_6": "Standard Main Battle Tank 1980",
    "medium_tank_destroyer_chassis_1": "Standard Main Battle Tank Destroyer 1942",
    "medium_tank_destroyer_chassis_2": "Standard Main Battle Tank Destroyer 1944",
    "medium_tank_destroyer_chassis_3": "Standard Main Battle Tank Destroyer 1950",
    # The five role families that had no bookmark starting design at all, 2026-09-17.
    # Light TD, medium SPAAG and heavy TD landed first; the two medium carrier families
    # followed once the owner ruled the carrier armour cap light-hull-only.
    "medium_tank_apc_chassis_0": "Standard Heavy APC 1939",
    "medium_tank_apc_chassis_1": "Standard Heavy APC 1942",
    "medium_tank_apc_chassis_2": "Standard Heavy APC 1944",
    "medium_tank_apc_chassis_3": "Standard Heavy APC 1950",
    "medium_tank_apc_chassis_4": "Standard Heavy APC 1960",
    "medium_tank_apc_chassis_5": "Standard Heavy APC 1970",
    "medium_tank_apc_chassis_6": "Standard Heavy APC 1980",
    "medium_tank_ifv_chassis_0": "Standard Heavy IFV 1939",
    "medium_tank_ifv_chassis_1": "Standard Heavy IFV 1942",
    "medium_tank_ifv_chassis_2": "Standard Heavy IFV 1944",
    "medium_tank_ifv_chassis_3": "Standard Heavy IFV 1950",
    "medium_tank_ifv_chassis_4": "Standard Heavy IFV 1960",
    "medium_tank_ifv_chassis_5": "Standard Heavy IFV 1970",
    "medium_tank_ifv_chassis_6": "Standard Heavy IFV 1980",
    "heavy_tank_destroyer_chassis_1": "Standard Heavy Tank Destroyer 1942",
    "heavy_tank_destroyer_chassis_2": "Standard Heavy Tank Destroyer 1944",
    "heavy_tank_destroyer_chassis_3": "Standard Heavy Tank Destroyer 1950",
    "heavy_tank_destroyer_chassis_4": "Standard Heavy Tank Destroyer 1955",
    "light_tank_destroyer_chassis_0": "Standard Light Tank Destroyer 1939",
    "light_tank_destroyer_chassis_1": "Standard Light Tank Destroyer 1942",
    "light_tank_destroyer_chassis_2": "Standard Light Tank Destroyer 1944",
    "light_tank_destroyer_chassis_3": "Standard Light Tank Destroyer 1950",
    "light_tank_destroyer_chassis_4": "Standard Light Tank Destroyer 1960",
    "light_tank_destroyer_chassis_5": "Standard Light Tank Destroyer 1970",
    "medium_tank_aa_chassis_1": "Standard Main Battle SPAA 1942",
    "medium_tank_aa_chassis_2": "Standard Main Battle SPAA 1944",
    "medium_tank_aa_chassis_3": "Standard Main Battle SPAA 1950",
    "medium_tank_aa_chassis_4": "Standard Main Battle SPAA 1960",
    "medium_tank_aa_chassis_5": "Standard Main Battle SPAA 1970",
    "medium_tank_aa_chassis_6": "Standard Main Battle SPAA 1980",
}
BOOKMARK_VARIANT_TECHS = {
    "heavy_tank_artillery_chassis_1": "nsb_heavy_tanks0",
    "heavy_tank_artillery_chassis_3": "nsb_heavy_tanks2",
    "heavy_tank_chassis_1": "nsb_heavy_tanks0",
    "heavy_tank_chassis_2": "nsb_heavy_tanks1",
    "heavy_tank_chassis_3": "nsb_heavy_tanks2",
    "heavy_tank_chassis_4": "nsb_heavy_tanks3",
    "light_tank_aa_chassis_1": "nsb_light_tanks0",
    "light_tank_aa_chassis_2": "nsb_light_tanks1",
    "light_tank_aa_chassis_3": "nsb_light_tanks2",
    "light_tank_artillery_chassis_1": "nsb_light_tanks0",
    "light_tank_artillery_chassis_2": "nsb_light_tanks1",
    "light_tank_artillery_chassis_3": "nsb_light_tanks2",
    "light_tank_chassis_1": "nsb_light_tanks0",
    "light_tank_chassis_2": "nsb_light_tanks1",
    "light_tank_chassis_3": "nsb_light_tanks2",
    "light_tank_chassis_4": "nsb_light_tanks3",
    "light_tank_chassis_5": "nsb_light_tanks4",
    "medium_tank_artillery_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_artillery_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_artillery_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_chassis_0": "nsb_iw_armored_vehicles",
    "medium_tank_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_chassis_4": "nsb_main_battle_tanks3",
    "medium_tank_chassis_5": "nsb_main_battle_tanks4",
    "medium_tank_chassis_6": "nsb_main_battle_tanks5",
    "medium_tank_destroyer_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_destroyer_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_destroyer_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_apc_chassis_0": "nsb_iw_armored_vehicles",
    "medium_tank_apc_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_apc_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_apc_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_apc_chassis_4": "nsb_main_battle_tanks3",
    "medium_tank_apc_chassis_5": "nsb_main_battle_tanks4",
    "medium_tank_apc_chassis_6": "nsb_main_battle_tanks5",
    "medium_tank_ifv_chassis_0": "nsb_iw_armored_vehicles",
    "medium_tank_ifv_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_ifv_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_ifv_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_ifv_chassis_4": "nsb_main_battle_tanks3",
    "medium_tank_ifv_chassis_5": "nsb_main_battle_tanks4",
    "medium_tank_ifv_chassis_6": "nsb_main_battle_tanks5",
    "heavy_tank_destroyer_chassis_1": "nsb_heavy_tanks0",
    "heavy_tank_destroyer_chassis_2": "nsb_heavy_tanks1",
    "heavy_tank_destroyer_chassis_3": "nsb_heavy_tanks2",
    "heavy_tank_destroyer_chassis_4": "nsb_heavy_tanks3",
    "light_tank_destroyer_chassis_0": "nsb_iw_armored_vehicles",
    "light_tank_destroyer_chassis_1": "nsb_light_tanks0",
    "light_tank_destroyer_chassis_2": "nsb_light_tanks1",
    "light_tank_destroyer_chassis_3": "nsb_light_tanks2",
    "light_tank_destroyer_chassis_4": "nsb_light_tanks3",
    "light_tank_destroyer_chassis_5": "nsb_light_tanks4",
    "medium_tank_aa_chassis_1": "nsb_main_battle_tanks0",
    "medium_tank_aa_chassis_2": "nsb_main_battle_tanks1",
    "medium_tank_aa_chassis_3": "nsb_main_battle_tanks2",
    "medium_tank_aa_chassis_4": "nsb_main_battle_tanks3",
    "medium_tank_aa_chassis_5": "nsb_main_battle_tanks4",
    "medium_tank_aa_chassis_6": "nsb_main_battle_tanks5",
}
# Shipped 2026-09-13: flame-family, IFV, and retired role/brigade ids stay
# unsupported; ATGM is a loadout on the destroyer role, while APC uses
# `flame`, IFV uses `rocket`, and `amphibious` remains deliberately unspent
# and reserved for a future dedicated amphibious mechanized role.
UNSUPPORTED_IDS = {
    "light_tank_rocket_chassis",
    "medium_tank_rocket_chassis",
    "heavy_tank_rocket_chassis",
    "medium_tank_heavy_artillery_chassis",
    "amphibious_tank_chassis",
    "modern_tank_chassis",
    "super_heavy_tank_chassis",
    "amphibious_mechanized_infantry",
    "category_amphibious_tanks",
    *REMOVED_TANK_TYPE_IDS,
    # Six of the eight duplicate role brigades are retired. `heavy_tank_destroyer_brigade`
    # and `medium_sp_anti_air_brigade` are NOT: no surviving legacy battalion consumes
    # `heavy_tank_destroyer_chassis` or `medium_tank_aa_chassis`, so deleting them
    # orphaned two role families and dropped Heavy Tank Destroyer and Medium SPAAG from
    # the ratified battalion taxonomy. They are restored and must stay.
    "light_tank_destroyer_brigade",
    "medium_tank_destroyer_brigade",
    "light_sp_artillery_brigade",
    "medium_sp_artillery_brigade",
    "heavy_sp_artillery_brigade",
    "light_sp_anti_air_brigade",
    "light_flame_tank",
    "medium_flame_tank",
    "heavy_flame_tank",
    "flamethrower",
    "tank_flamethrower",
}


# Two carrier generations share a light hull tier after the 2026-09-11 cutover,
# and only the generation that owns the tier carries a generic bookmark design,
# so the later one must not overwrite the map with a null name.
BOOKMARK_VARIANT_NAMES.update(
    {r["type"]: r["generic_name"] for r in CARRIER_MANIFEST["recipes"] if r["has_generic_design"]}
)
BOOKMARK_VARIANT_TECHS.update(
    {r["type"]: r["technology"] for r in CARRIER_MANIFEST["recipes"] if r["has_generic_design"]}
)


def bookmark_variant_names(equipment_type: str, producer: str) -> set[str]:
    """Every design a producer bootstraps on one chassis.

    Before the 2026-09-11 carrier cutover this was a single name, because each
    producer had at most one preset per chassis. Two carrier generations now
    share a light hull tier, so a producer legitimately bootstraps two designs
    on it - Canada's 1960 carrier and its M113A1 - and an OOB may request either.
    """
    names = {
        preset["name"]
        for preset in NATIONAL_PRESETS + CARRIER_PRESETS + NAMING_PRESETS
        if (preset["type"], preset["producer"]) == (equipment_type, producer)
    }
    return names or {BOOKMARK_VARIANT_NAMES[equipment_type]}


def bookmark_variant_name(equipment_type: str, producer: str) -> str:
    """The single design for a producer and chassis; fails loudly when ambiguous."""
    names = bookmark_variant_names(equipment_type, producer)
    if len(names) != 1:
        fail(f"{producer} bootstraps several designs on {equipment_type}: {sorted(names)}")
    return sorted(names)[0]


def oob_variant_producer(block: str, default_tag: str) -> str:
    for field in ("producer", "creator", "owner"):
        match = re.search(rf'\b{field}\s*=\s*"?([A-Z]{{3}})"?', code_only(block))
        if match:
            return match[1]
    return default_tag

errors: list[str] = []

LAND_MANIFEST_FILE = ROOT / "LogDocs/Doctrine_Rework/Doctrine_Cell_Manifest.md"
REVIEWED_LAND_MANIFEST_SHA256 = "d0adb7a947404256e43fe7a28a08b9d31a94a114a2252c76fafb11b61ccf201e"
DOCTRINE_CONTENT_SHA256 = {
    "land_doctrine.txt": "30f7b88844a779da077ddbea0cb2f5bf3ab6f47c5d21db9167b59dbe40941fea",
    "air_doctrine.txt": "60805d1cddae8deb5e2827501dfcb1186708f2b1045702c72dff4a6bab78f89c",
    "naval_doctrine.txt": "81b983873396a3dd108c85184163beaf2efdb02f2ff144904d7d4c1ed420d085",
}
EXPECTED_DOCTRINE_COUNTS = {"land_doctrine.txt": 528, "air_doctrine.txt": 73, "naval_doctrine.txt": 45}
LAND_ROOTS = (
    "cw_nato_1940s_integrated_arms_reorganization",
    "cw_france_1940s_doctrine_header",
    "cw_israel_1940s_doctrine_header",
    "cw_warsaw_1940s_doctrine_header",
    "cw_prc_1940s_doctrine_header",
    "cw_yugo_1940s_doctrine_header",
    "cw_himalayan_1960s_doctrine_header",
    "cw_non_aligned_1940s_doctrine_header",
    "cw_iran_1980s_doctrine_header",
    "cw_ins_1940s_doctrine_header",
    "cw_islamist_alt_ins_1990s_doctrine_header",
)
LAND_ROW_Y = {1940: 172, 1950: 790, 1960: 1420, 1970: 2050, 1980: 2680, 1990: 3310}
LEDGER_FOLDERS = {
    "old_land_doctrine_folder": "army",
    "old_naval_doctrine_folder": "navy",
    "old_air_doctrine_folder": "air",
}


class ScriptParseError(ValueError):
    """A bounded Clausewitz block could not be parsed safely."""


def strip_script_comments(value: str) -> str:
    """Remove comments while preserving quoted strings and line structure."""
    result: list[str] = []
    quoted = False
    escaped = False
    comment = False
    for character in value:
        if comment:
            if character == "\n":
                comment = False
                result.append(character)
            continue
        if quoted:
            result.append(character)
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
            result.append(character)
        elif character == "#":
            comment = True
        else:
            result.append(character)
    return "".join(result)


def balanced_end(value: str, opening: int, label: str) -> int:
    depth = 0
    quoted = False
    escaped = False
    for index in range(opening, len(value)):
        character = value[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            continue
        if character == '"':
            quoted = True
        elif character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                raise ScriptParseError(f"negative brace depth in {label}")
            if depth == 0:
                return index
    raise ScriptParseError(f"unbalanced block in {label}")


def top_level_ranges(block: str, label: str) -> list[tuple[str, int, int, str]]:
    """Return direct child blocks, including inline blocks, from a balanced block."""
    value = strip_script_comments(block)
    opening = value.find("{")
    if opening < 0:
        raise ScriptParseError(f"missing opening brace in {label}")
    ending = balanced_end(value, opening, label)
    result: list[tuple[str, int, int, str]] = []
    index = opening + 1
    depth = 0
    quoted = False
    escaped = False
    while index < ending:
        character = value[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            index += 1
            continue
        if character == '"':
            quoted = True
            index += 1
            continue
        if depth == 0:
            match = re.match(r"\s*([A-Za-z0-9_]+)\s*=\s*\{", value[index:ending])
            if match:
                name = match.group(1)
                start = index + match.start(1)
                child_opening = value.find("{", index + match.start(), index + match.end())
                child_ending = balanced_end(value, child_opening, f"{label}.{name}")
                result.append((name, start, child_ending, value[start : child_ending + 1]))
                index = child_ending + 1
                continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                raise ScriptParseError(f"negative child brace depth in {label}")
        index += 1
    if depth:
        raise ScriptParseError(f"unbalanced child block in {label}")
    return result


def top_level_named_blocks(block: str, key: str, label: str = "block") -> list[str]:
    return [child for name, _, _, child in top_level_ranges(block, label) if name == key]


def strict_top_level_blocks(value: str, root_name: str, label: str) -> list[tuple[str, str]]:
    code = strip_script_comments(value)
    matches = list(re.finditer(rf"(?m)^\s*{re.escape(root_name)}\s*=\s*\{{", code))
    if len(matches) != 1:
        raise ScriptParseError(f"expected one {root_name} block in {label}, found {len(matches)}")
    match = matches[0]
    opening = code.find("{", match.start(), match.end())
    ending = balanced_end(code, opening, label)
    root = code[match.start() : ending + 1]
    result = [(name, child) for name, _, _, child in top_level_ranges(root, label)]
    names = [name for name, _ in result]
    duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
    if duplicates:
        raise ScriptParseError(f"duplicate top-level IDs in {label}: {duplicates}")
    return result


def key_blocks(value: str, key: str, label: str) -> list[str]:
    code = strip_script_comments(value)
    result = []
    for match in re.finditer(rf"(?m)^\s*{re.escape(key)}\s*=\s*\{{", code):
        opening = code.find("{", match.start(), match.end())
        ending = balanced_end(code, opening, f"{label}.{key}")
        result.append(code[match.start() : ending + 1])
    return result


def top_level_values(block: str, key: str) -> list[str]:
    value = strip_script_comments(block)
    opening = value.find("{")
    if opening < 0:
        raise ScriptParseError(f"missing opening brace while reading {key}")
    ending = balanced_end(value, opening, key)
    pattern = re.compile(rf"(?<![A-Za-z0-9_]){re.escape(key)}\s*=\s*([A-Za-z0-9_.-]+)")
    result: list[str] = []
    index = opening + 1
    depth = 0
    quoted = False
    escaped = False
    while index < ending:
        character = value[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            index += 1
            continue
        if character == '"':
            quoted = True
            index += 1
            continue
        if depth == 0:
            match = pattern.match(value, index, ending)
            if match:
                result.append(match.group(1))
                index = match.end()
                continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
        index += 1
    return result


def top_level_quoted_values(block: str, key: str) -> list[str]:
    """Read quoted direct values from a balanced block."""
    value = strip_script_comments(block)
    opening = value.find("{")
    if opening < 0:
        raise ScriptParseError(f"missing opening brace while reading {key}")
    ending = balanced_end(value, opening, key)
    pattern = re.compile(
        rf'(?<![A-Za-z0-9_]){re.escape(key)}\s*=\s*"([^"]*)"'
    )
    result: list[str] = []
    index = opening + 1
    depth = 0
    quoted = False
    escaped = False
    while index < ending:
        character = value[index]
        if quoted:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                quoted = False
            index += 1
            continue
        if character == '"':
            quoted = True
            index += 1
            continue
        if depth == 0:
            match = pattern.match(value, index, ending)
            if match:
                result.append(match.group(1))
                index = match.end()
                continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
        index += 1
    return result


def doctrine_content_digest(blocks: list[tuple[str, str]]) -> str:
    canonical: list[str] = []
    for name, block in blocks:
        code = strip_script_comments(block)
        for child_name, start, ending, _ in reversed(top_level_ranges(code, name)):
            if child_name == "allow":
                code = code[:start] + code[ending + 1 :]
        canonical.append(name + "=" + re.sub(r"\s+", " ", code).strip())
    return sha256("\n".join(sorted(canonical)).encode("utf-8")).hexdigest()


def read_land_manifest() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    value = text(LAND_MANIFEST_FILE)
    for line in value.splitlines():
        if not line.startswith("| ") or line.startswith("| GUI") or line.startswith("| ---"):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) != 6:
            fail(f"malformed land cell manifest row: {line}")
            continue
        x, decade, header, nodes, terminal, parent = fields
        try:
            row = {
                "x": int(x),
                "decade": int(decade),
                "header": header.strip("`"),
                "nodes": int(nodes),
                "terminal": terminal.strip("`"),
                "parent": None if parent.startswith("**") else parent.strip("`"),
            }
        except ValueError:
            fail(f"malformed land cell manifest row: {line}")
            continue
        rows.append(row)
    canonical = "\n".join(
        "|".join(
            (
                str(row["x"]),
                str(row["decade"]),
                str(row["header"]),
                str(row["nodes"]),
                str(row["terminal"]),
                "ROOT" if row["parent"] is None else str(row["parent"]),
            )
        )
        for row in rows
    ) + "\n"
    if sha256(canonical.encode("utf-8")).hexdigest() != REVIEWED_LAND_MANIFEST_SHA256:
        fail("reviewed land cell manifest does not match its implementation contract")
    return rows


def named_gui_blocks(value: str, kind: str, wanted: str | None, label: str) -> list[str]:
    code = strip_script_comments(value)
    result: list[str] = []
    for match in re.finditer(rf"(?m)^\s*{re.escape(kind)}\s*=\s*\{{", code):
        opening = code.find("{", match.start(), match.end())
        ending = balanced_end(code, opening, f"{label}.{kind}")
        block = code[match.start() : ending + 1]
        name = re.search(r'\bname\s*=\s*"([^"]+)"', block)
        if name and (wanted is None or name.group(1) == wanted):
            result.append(block)
    return result

def validate_tank_folder_gridboxes(
    all_tank_techs: dict[str, str],
    variable_values: dict[str, str],
    research_ui: str,
) -> None:
    """Pin each NSB armor folder's gridbox set and every technology's folder x."""
    for folder_name, x_gridboxes in TECH_FOLDER_X_GRIDBOX.items():
        folders = named_gui_blocks(research_ui, "containerWindowType", folder_name, "countrytechtreeview")
        if len(folders) != 1:
            fail(f"{folder_name} must have one active GUI container, found {len(folders)}")
            continue
        gridboxes: dict[str, tuple[int, int]] = {}
        for gridbox in top_level_named_blocks(folders[0], "gridboxtype", folder_name):
            name = re.search(r'\bname\s*=\s*"([^"]+)"', gridbox)
            position = re.search(
                r"\bposition\s*=\s*\{\s*x\s*=\s*(-?[0-9]+)\s+y\s*=\s*(-?[0-9]+)",
                gridbox,
            )
            slotsize = re.search(
                r"\bslotsize\s*=\s*\{\s*width\s*=\s*([0-9]+)\s+height\s*=\s*([0-9]+)",
                gridbox,
            )
            if not name or not position or not slotsize:
                fail(f"{folder_name} has a malformed child gridbox")
                continue
            gridbox_name = name.group(1)
            if gridbox_name in gridboxes:
                fail(f"{folder_name} repeats GUI gridbox {gridbox_name}")
                continue
            gridboxes[gridbox_name] = (int(position.group(1)), int(slotsize.group(1)))
        expected_gridboxes = set(x_gridboxes.values())
        for gridbox_name in sorted(expected_gridboxes - set(gridboxes)):
            fail(f"{folder_name} is missing GUI gridbox {gridbox_name}")
        for gridbox_name in sorted(set(gridboxes) - expected_gridboxes):
            fail(f"{folder_name} has unmapped GUI gridbox {gridbox_name}")

        for technology, block in all_tank_techs.items():
            folders = top_level_named_blocks(block, "folder", technology)
            if len(folders) != 1:
                continue
            folder = folders[0]
            if direct_values(folder, "name") != [folder_name]:
                continue
            position = re.search(
                r"\bposition\s*=\s*\{\s*x\s*=\s*([^\s}]+)\s+y\s*=\s*([^\s}]+)",
                folder,
            )
            if not position:
                continue
            raw_x = variable_values.get(position.group(1), position.group(1))
            try:
                x = int(raw_x)
            except ValueError:
                fail(f"{folder_name} technology {technology} has a non-integer folder x {raw_x}")
                continue
            gridbox_name = x_gridboxes.get(x)
            if gridbox_name is None:
                fail(f"{folder_name} technology {technology} uses an unmapped folder x {x}")
                continue
            dimensions = gridboxes.get(gridbox_name)
            if dimensions is None:
                continue
            origin, slot_width = dimensions
            if origin < 0 or slot_width <= 0:
                fail(
                    f"{folder_name} gridbox {gridbox_name} has a nonsensical "
                    f"origin {origin} or slot width {slot_width}"
                )


def parse_allow_signature(allow: str, technology: str) -> tuple[list[str], list[tuple[str, str]]]:
    children = top_level_ranges(allow, f"{technology}.allow")
    if any(name in {"OR", "AND"} for name, _, _, _ in children):
        fail(f"{technology} allow prerequisite is hidden under OR/AND")
    direct_positive = top_level_values(allow, "has_tech")
    direct_researching = top_level_values(allow, "is_researching_technology")
    if direct_researching:
        fail(f"{technology} allow has a direct research-state clause")
    clauses: list[tuple[str, str]] = []
    for name, _, _, child in children:
        if name != "NOT":
            if name not in {"allow"}:
                fail(f"{technology} allow contains unsupported block {name}")
            continue
        child_has = top_level_values(child, "has_tech")
        child_researching = top_level_values(child, "is_researching_technology")
        dates = re.findall(r"\bdate\s*<\s*([0-9]+\.[0-9]+\.[0-9]+)", child)
        if child_has and not child_researching and not dates and len(child_has) == 1:
            clauses.append(("has", child_has[0]))
        elif child_researching and not child_has and not dates and len(child_researching) == 1:
            clauses.append(("researching", child_researching[0]))
        elif dates and not child_has and not child_researching and len(dates) == 1:
            clauses.append(("date", dates[0]))
        else:
            fail(f"{technology} allow contains malformed NOT clause")
    if re.search(r"\bdate\s*[<>]=?", allow) and not re.search(
        r"\bdate\s*<\s*[0-9]+\.[0-9]+\.[0-9]+", allow
    ):
        fail(f"{technology} allow has an unsupported date boundary")
    return direct_positive, clauses


def fixture_allow_signature(allow: str) -> tuple[list[str], list[tuple[str, str]]]:
    """Parse an allow fixture without adding failures to the real validation run."""
    children = top_level_ranges(allow, "fixture.allow")
    if any(name in {"OR", "AND"} for name, _, _, _ in children):
        raise ScriptParseError("allow contains OR/AND")
    positive = top_level_values(allow, "has_tech")
    clauses: list[tuple[str, str]] = []
    for name, _, _, child in children:
        if name != "NOT":
            raise ScriptParseError(f"unsupported allow block {name}")
        child_has = top_level_values(child, "has_tech")
        child_researching = top_level_values(child, "is_researching_technology")
        dates = re.findall(r"\bdate\s*<\s*([0-9]+\.[0-9]+\.[0-9]+)", child)
        if child_has and not child_researching and not dates and len(child_has) == 1:
            clauses.append(("has", child_has[0]))
        elif child_researching and not child_has and not dates and len(child_researching) == 1:
            clauses.append(("researching", child_researching[0]))
        elif dates and not child_has and not child_researching and len(dates) == 1:
            clauses.append(("date", dates[0]))
        else:
            raise ScriptParseError("malformed NOT clause")
    if re.search(r"\bdate\s*[<>]=?", allow) and not re.search(
        r"\bdate\s*<\s*[0-9]+\.[0-9]+\.[0-9]+", allow
    ):
        raise ScriptParseError("unsupported date boundary")
    return positive, clauses


def fixture_graph_check(
    edges: dict[str, list[str]], anchors: list[str], all_nodes: set[str]
) -> None:
    owners: dict[str, str] = {}
    state: dict[str, int] = {}

    def visit_graph(node: str) -> None:
        if state.get(node, 0) == 1:
            raise ScriptParseError(f"cycle at {node}")
        if state.get(node, 0) == 2:
            return
        state[node] = 1
        for target in edges.get(node, []):
            if target not in all_nodes:
                raise ScriptParseError(f"undefined target {target}")
            visit_graph(target)
        state[node] = 2

    for node in all_nodes:
        visit_graph(node)

    def visit_cell(cell: str, node: str, active: set[str]) -> None:
        if node in active:
            raise ScriptParseError(f"cycle at {node}")
        if node in owners:
            if owners[node] != cell:
                raise ScriptParseError(f"duplicate ownership of {node}")
            return
        owners[node] = cell
        active.add(node)
        for target in edges.get(node, []):
            visit_cell(cell, target, active)
        active.remove(node)

    for anchor in anchors:
        if anchor not in all_nodes:
            raise ScriptParseError(f"orphan anchor {anchor}")
        visit_cell(anchor, anchor, set())
    if set(owners) != all_nodes:
        raise ScriptParseError(f"orphan nodes: {sorted(all_nodes - set(owners))}")
    for source, targets in edges.items():
        for target in targets:
            if owners.get(source) != owners.get(target):
                raise ScriptParseError(f"cross-cell edge {source} -> {target}")


def run_doctrine_negative_fixtures() -> None:
    def require_rejection(label: str, function) -> None:
        try:
            function()
        except (AssertionError, ScriptParseError):
            return
        fail(f"doctrine negative fixture was accepted: {label}")

    def assert_one_allow_fixture() -> None:
        assert len(top_level_named_blocks("tech = { allow = { has_tech = root } allow = { has_tech = root } }", "allow")) == 1

    def assert_allow_signature(value: str, positive: list[str], clauses: list[tuple[str, str]]) -> None:
        assert fixture_allow_signature(value) == (positive, clauses)

    def assert_without_test_flag(value: str) -> None:
        assert "X_TESt" not in strip_script_comments(value)

    accepted = strict_top_level_blocks(
        "technologies = { root = { path = { leads_to_tech = child } } child = { allow  = { has_tech = root NOT = { date < 1950.1.1 } } } }",
        "technologies",
        "two-space fixture",
    )
    accepted_map = dict(accepted)
    assert top_level_values(top_level_named_blocks(accepted_map["root"], "path")[0], "leads_to_tech") == ["child"]
    assert fixture_allow_signature(top_level_named_blocks(accepted_map["child"], "allow")[0]) == (
        ["root"],
        [("date", "1950.1.1")],
    )
    inline = strict_top_level_blocks(
        "technologies = { root = { path = { leads_to_tech = child } } child = { allow = { has_tech = root } } }",
        "technologies",
        "inline fixture",
    )
    assert fixture_allow_signature(top_level_named_blocks(dict(inline)["child"], "allow")[0]) == (["root"], [])
    commented = strict_top_level_blocks(
        "technologies = { root = { # path = { leads_to_tech = ghost }\n } }",
        "technologies",
        "comment fixture",
    )
    assert not top_level_named_blocks(dict(commented)["root"], "path")

    require_rejection(
        "unbalanced block",
        lambda: strict_top_level_blocks("technologies = { root = {", "technologies", "unbalanced fixture"),
    )
    require_rejection(
        "missing prerequisite",
        lambda: assert_allow_signature("allow = { NOT = { date < 1950.1.1 } }", ["root"], [("date", "1950.1.1")]),
    )
    require_rejection(
        "wrong prerequisite",
        lambda: assert_allow_signature("allow = { has_tech = wrong }", ["root"], []),
    )
    require_rejection(
        "negated prerequisite",
        lambda: assert_allow_signature("allow = { NOT = { has_tech = root } }", ["root"], []),
    )
    require_rejection(
        "OR bypass",
        lambda: fixture_allow_signature("allow = { OR = { has_tech = root has_tech = sibling } }"),
    )
    require_rejection(
        "wrong date boundary",
        lambda: fixture_allow_signature("allow = { NOT = { date > 1950.1.1 } }"),
    )
    require_rejection(
        "duplicate allow",
        lambda: assert_one_allow_fixture(),
    )
    require_rejection(
        "missing reciprocal exclusion",
        lambda: assert_allow_signature(
            "allow = { NOT = { has_tech = rival } }",
            ["root"],
            [("has", "rival"), ("researching", "rival")],
        ),
    )
    require_rejection(
        "restored test flag",
        lambda: assert_without_test_flag("allow = { has_country_flag = X_TESt }"),
    )
    require_rejection(
        "cross-cell edge",
        lambda: fixture_graph_check({"a": ["b"], "b": []}, ["a", "b"], {"a", "b"}),
    )
    require_rejection(
        "cycle",
        lambda: fixture_graph_check({"a": ["b"], "b": ["a"]}, ["a"], {"a", "b"}),
    )
    require_rejection(
        "orphan",
        lambda: fixture_graph_check({"a": [], "b": []}, ["a"], {"a", "b"}),
    )
    require_rejection(
        "duplicate ownership",
        lambda: fixture_graph_check({"a": ["c"], "b": ["c"], "c": []}, ["a", "b"], {"a", "b", "c"}),
    )
    # Prefix changes do not change cell ownership; the anchor traversal is the contract.
    fixture_graph_check({"alt_header": ["cw_islamist_ins_1990s_global_operational_continuum"], "cw_islamist_ins_1990s_global_operational_continuum": []}, ["alt_header"], {"alt_header", "cw_islamist_ins_1990s_global_operational_continuum"})


def validate_doctrine_rework() -> None:
    parked = [path for path in doctrine_files if not path.is_file()]
    if len(parked) == len(doctrine_files):
        print(
            "Doctrine rework is parked under "
            "'common/technologies/doctrine rework/' and is not loaded by the game; "
            "skipping doctrine contracts."
        )
        return
    if parked:
        fail(
            "doctrine rework is half parked; these files are missing from the active "
            f"technologies directory: {sorted(path.name for path in parked)}"
        )
        return
    by_file: dict[str, dict[str, str]] = {}
    for path in doctrine_files:
        filename = path.name
        try:
            blocks = strict_top_level_blocks(text(path), "technologies", filename)
        except ScriptParseError as problem:
            fail(str(problem))
            continue
        by_file[filename] = dict(blocks)
        expected_count = EXPECTED_DOCTRINE_COUNTS[filename]
        if len(blocks) != expected_count:
            fail(f"{filename} must contain {expected_count} technologies, found {len(blocks)}")
        expected_type = {"land_doctrine.txt": "army", "air_doctrine.txt": "air", "naval_doctrine.txt": "navy"}[filename]
        for name, block in blocks:
            for field in ("xp_research_type", "xp_unlock_cost", "doctrine"):
                values = top_level_values(block, field)
                if len(values) != 1:
                    fail(f"{name} in {filename} must define exactly one {field}")
            if top_level_values(block, "xp_research_type") != [expected_type]:
                fail(f"{name} in {filename} has the wrong XP research type")
            if top_level_values(block, "xp_unlock_cost") != ["100"]:
                fail(f"{name} in {filename} must cost exactly 100 XP")
            if top_level_values(block, "doctrine") != ["yes"]:
                fail(f"{name} in {filename} must retain doctrine = yes")
            for path_block in top_level_named_blocks(block, "path", name):
                targets = top_level_values(path_block, "leads_to_tech")
                if not targets:
                    # Land capstones retain a documented, commented-out future path.
                    continue
                if len(targets) != 1:
                    fail(f"{name} has a malformed path block")
                elif targets[0] not in technology_set:
                    fail(f"undefined technology path {name} -> {targets[0]} in {filename}")
            for target in re.findall(
                r"\b(?:has_tech|is_researching_technology)\s*=\s*([A-Za-z0-9_]+)",
                strip_script_comments(block),
            ):
                if target not in technology_set:
                    fail(f"undefined doctrine prerequisite target {target} in {name}")
        expected_digest = DOCTRINE_CONTENT_SHA256.get(filename)
        if expected_digest and doctrine_content_digest(blocks) != expected_digest:
            fail(f"{filename} has an unexpected effect/path/content change outside allow blocks")

    land = by_file.get("land_doctrine.txt", {})
    air = by_file.get("air_doctrine.txt", {})
    naval = by_file.get("naval_doctrine.txt", {})
    manifest = read_land_manifest()
    if len(manifest) != 78:
        fail(f"land cell manifest must contain 78 rows, found {len(manifest)}")
    manifest_by_header = {row["header"]: row for row in manifest}
    if len(manifest_by_header) != len(manifest):
        fail("land cell manifest contains duplicate headers")
    if tuple(row["header"] for row in manifest if row["parent"] is None) != tuple(
        row["header"] for row in manifest if row["header"] in LAND_ROOTS
    ):
        fail("land cell manifest root set or order changed")
    if set(row["header"] for row in manifest if row["parent"] is None) != set(LAND_ROOTS):
        fail("land cell manifest has the wrong independent root set")

    if land:
        for name, block in land.items():
            allows = top_level_named_blocks(block, "allow", name)
            if top_level_named_blocks(block, "dependencies", name):
                fail(f"land technology {name} adds a cumulative dependencies block")
            if name not in manifest_by_header:
                if allows:
                    fail(f"non-header land technology {name} retains an allow block")
                continue
            if len(allows) != 1:
                fail(f"land header {name} must contain exactly one allow block")
                continue
            positive, clauses = parse_allow_signature(allows[0], name)
            row = manifest_by_header[name]
            expected_positive = [] if row["parent"] is None else [row["parent"]]
            if positive != expected_positive:
                fail(f"{name} has the wrong direct lineage prerequisite: {positive}")
            expected_clauses: set[tuple[str, str]] = set()
            if row["decade"] > 1940:
                expected_clauses.add(("date", f"{row['decade']}.1.1"))
            if name in LAND_ROOTS:
                for rival in LAND_ROOTS:
                    if rival != name:
                        expected_clauses.add(("has", rival))
                        expected_clauses.add(("researching", rival))
            if len(clauses) != len(set(clauses)) or set(clauses) != expected_clauses:
                fail(f"{name} has the wrong lineage/date/root exclusion clauses")
        header_names = set(manifest_by_header)
        actual_allow_names = {name for name, block in land.items() if top_level_named_blocks(block, "allow", name)}
        if actual_allow_names != header_names:
            fail("land allow blocks are not exactly the 78 reviewed header blocks")
        if re.search(r"\b(?:X_TESt|has_country_flag)\b", strip_script_comments(text(doctrine_files[0]))):
            fail("land doctrine retains the obsolete X_TESt/country-flag gate")

        outgoing: dict[str, list[str]] = {name: [] for name in land}
        incoming: dict[str, list[str]] = {name: [] for name in land}
        for name, block in land.items():
            for path_block in top_level_named_blocks(block, "path", name):
                targets = top_level_values(path_block, "leads_to_tech")
                if len(targets) != 1:
                    continue
                target = targets[0]
                outgoing[name].append(target)
                if target in incoming:
                    incoming[target].append(name)
            if len(outgoing[name]) != len(set(outgoing[name])):
                fail(f"land technology {name} contains a duplicate active path")

        graph_state: dict[str, int] = {}
        def visit_graph(node: str) -> None:
            state = graph_state.get(node, 0)
            if state == 1:
                fail(f"land doctrine path graph contains a cycle at {node}")
                return
            if state == 2:
                return
            graph_state[node] = 1
            for target in outgoing.get(node, []):
                if target in land:
                    visit_graph(target)
            graph_state[node] = 2
        for name in land:
            visit_graph(name)

        owners: dict[str, str] = {}
        def visit_cell(cell: str, node: str, active: set[str]) -> None:
            if node in active:
                fail(f"land cell {cell} contains a cycle at {node}")
                return
            previous = owners.get(node)
            if previous is not None:
                if previous != cell:
                    fail(f"land technology {node} is owned by both {previous} and {cell}")
                return
            owners[node] = cell
            active.add(node)
            for target in outgoing.get(node, []):
                if target in land:
                    visit_cell(cell, target, active)
            active.remove(node)

        for row in manifest:
            header = row["header"]
            if header in land:
                visit_cell(header, header, set())
        if set(owners) != set(land):
            fail(
                "land GUI anchors do not uniquely cover all technologies: "
                f"missing={sorted(set(land) - set(owners))}, extra={sorted(set(owners) - set(land))}"
            )
        for source, targets in outgoing.items():
            for target in targets:
                if target in owners and source in owners and owners[source] != owners[target]:
                    fail(f"cross-cell land path {source} -> {target}")
        for row in manifest:
            cell = row["header"]
            nodes = {name for name, owner in owners.items() if owner == cell}
            cell_roots = [name for name in nodes if not any(source in nodes for source in incoming[name])]
            cell_terminals = [name for name in nodes if not any(target in nodes for target in outgoing[name])]
            if len(nodes) != row["nodes"]:
                fail(f"land cell {cell} owns {len(nodes)} nodes, expected {row['nodes']}")
            if len(cell_roots) != 1 or cell_roots[0] != cell:
                fail(f"land cell {cell} must have exactly one root at its header")
            if len(cell_terminals) != 1 or cell_terminals[0] != row["terminal"]:
                fail(f"land cell {cell} has the wrong terminal: {cell_terminals}")

        gui_code = strip_script_comments(text(MOD / "interface/countrytechtreeview.gui"))
        land_folders = named_gui_blocks(gui_code, "containerWindowType", "old_land_doctrine_folder", "countrytechtreeview")
        if len(land_folders) != 1:
            fail(f"expected one active old_land_doctrine_folder GUI container, found {len(land_folders)}")
        else:
            anchors: dict[str, tuple[int, int]] = {}
            for grid in top_level_named_blocks(land_folders[0], "gridboxtype", "old_land_doctrine_folder"):
                name_match = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', grid)
                if not name_match:
                    fail("land GUI grid anchor has no name")
                    continue
                grid_name = name_match.group(1)
                if not grid_name.endswith("_tree"):
                    fail(f"unexpected non-cell grid in old_land_doctrine_folder: {grid_name}")
                    continue
                technology = grid_name[:-5]
                position = re.search(
                    r"\bposition\s*=\s*\{\s*x\s*=\s*(-?[0-9]+)\s*y\s*=\s*(-?[0-9]+)",
                    grid,
                )
                if not position:
                    fail(f"land GUI anchor {technology} has no position")
                    continue
                if technology in anchors:
                    fail(f"duplicate land GUI anchor: {technology}")
                anchors[technology] = (int(position.group(1)), int(position.group(2)))
            expected_anchors = {
                row["header"]: (row["x"], LAND_ROW_Y.get(row["decade"], -1)) for row in manifest
            }
            if anchors != expected_anchors:
                fail("land GUI anchors or coordinates differ from the reviewed manifest")

    expected_air = {
        "air_doctrine_versatile": {("has", "air_doctrine_integral"), ("researching", "air_doctrine_integral"), ("has", "air_doctrine_systemic"), ("researching", "air_doctrine_systemic")},
        "air_doctrine_systemic": {("has", "air_doctrine_integral"), ("researching", "air_doctrine_integral"), ("has", "air_doctrine_versatile"), ("researching", "air_doctrine_versatile")},
        "air_doctrine_integral": {("has", "air_doctrine_systemic"), ("researching", "air_doctrine_systemic"), ("has", "air_doctrine_versatile"), ("researching", "air_doctrine_versatile")},
        "air_doctrine_systemic_5a1": {("has", "air_doctrine_systemic_5a2"), ("researching", "air_doctrine_systemic_5a2")},
        "air_doctrine_systemic_5a2": {("has", "air_doctrine_systemic_5a1"), ("researching", "air_doctrine_systemic_5a1")},
        "air_doctrine_systemic_5b1": {("has", "air_doctrine_systemic_5b2"), ("researching", "air_doctrine_systemic_5b2")},
        "air_doctrine_systemic_5b2": {("has", "air_doctrine_systemic_5b1"), ("researching", "air_doctrine_systemic_5b1")},
        "air_doctrine_integral_2a1": {("has", "air_doctrine_integral_2a2"), ("researching", "air_doctrine_integral_2a2")},
        "air_doctrine_integral_2a2": {("has", "air_doctrine_integral_2a1"), ("researching", "air_doctrine_integral_2a1")},
        "air_doctrine_integral_2b1": {("has", "air_doctrine_integral_2b2"), ("researching", "air_doctrine_integral_2b2")},
        "air_doctrine_integral_2b2": {("has", "air_doctrine_integral_2b1"), ("researching", "air_doctrine_integral_2b1")},
        "air_doctrine_integral_6a": {("has", "air_doctrine_integral_6b"), ("researching", "air_doctrine_integral_6b")},
        "air_doctrine_integral_6b": {("has", "air_doctrine_integral_6a"), ("researching", "air_doctrine_integral_6a")},
    }
    if air:
        actual_air = {}
        for name, block in air.items():
            allows = top_level_named_blocks(block, "allow", name)
            if allows:
                if len(allows) != 1:
                    fail(f"{name} has duplicate air allow blocks")
                else:
                    positive, clauses = parse_allow_signature(allows[0], name)
                    if positive or len(clauses) != len(set(clauses)):
                        fail(f"{name} has a malformed air exclusion block")
                    actual_air[name] = set(clauses)
        if set(actual_air) != set(expected_air):
            fail(f"air exclusion block set changed: {sorted(set(actual_air) ^ set(expected_air))}")
        for name, expected in expected_air.items():
            if actual_air.get(name) != expected:
                fail(f"air exclusion semantics changed for {name}")

    expected_naval = {
        "fleet_in_being": {("has", "trade_interdiction"), ("researching", "trade_interdiction"), ("has", "base_strike"), ("researching", "base_strike")},
        "trade_interdiction": {("has", "fleet_in_being"), ("researching", "fleet_in_being"), ("has", "base_strike"), ("researching", "base_strike")},
        "base_strike": {("has", "fleet_in_being"), ("researching", "fleet_in_being"), ("has", "trade_interdiction"), ("researching", "trade_interdiction")},
    }
    if naval:
        actual_naval = {}
        for name, block in naval.items():
            allows = top_level_named_blocks(block, "allow", name)
            if allows:
                if len(allows) != 1:
                    fail(f"{name} has duplicate naval allow blocks")
                else:
                    positive, clauses = parse_allow_signature(allows[0], name)
                    if positive or len(clauses) != len(set(clauses)):
                        fail(f"{name} has a malformed naval exclusion block")
                    actual_naval[name] = set(clauses)
        if actual_naval != expected_naval:
            fail("naval root exclusion semantics changed")

    tags_code = strip_script_comments(text(MOD / "common/technology_tags/00_technology.txt"))
    gui_code = strip_script_comments(text(MOD / "interface/countrytechtreeview.gui"))
    for folder, ledger in LEDGER_FOLDERS.items():
        tag_blocks = key_blocks(tags_code, folder, "technology_tags")
        if len(tag_blocks) != 1:
            fail(f"expected one technology tag definition for {folder}")
        elif top_level_values(tag_blocks[0], "ledger") != [ledger] or top_level_values(tag_blocks[0], "doctrine") != ["no"]:
            fail(f"{folder} must remain an ordinary {ledger} ledger folder")
        if len(named_gui_blocks(gui_code, "containerWindowType", folder, "countrytechtreeview")) != 1:
            fail(f"missing active GUI container for {folder}")
        tabs = named_gui_blocks(gui_code, "containerWindowType", "folder_tabs", "countrytechtreeview")
        if len(tabs) != 1:
            fail("expected one active folder_tabs container")
        else:
            button_names = []
            for button in top_level_named_blocks(tabs[0], "buttonType", "folder_tabs"):
                name_match = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', button)
                if name_match:
                    button_names.append(name_match.group(1))
            if button_names.count(folder + "_tab") != 1:
                fail(f"missing or duplicate tab registration for {folder}")
        for suffix in ("_item", "_small_item"):
            template = "techtree_" + folder + suffix
            if len(named_gui_blocks(gui_code, "containerWindowType", template, "countrytechtreeview")) != 1:
                fail(f"missing or duplicate node template for {template}")

    gfx_code = strip_script_comments(text(MOD / "interface/CWIC_Doctrines.gfx"))
    doctrine_sprites = named_gui_blocks(gfx_code, "spriteType", None, "CWIC_Doctrines")
    doctrine_sprites += named_gui_blocks(gfx_code, "SpriteType", None, "CWIC_Doctrines")
    for sprite in doctrine_sprites:
        texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', sprite)
        vanilla_placeholder = "gfx/interface/doctrines/icons/doctrine_placeholder.dds"
        if texture and texture.group(1).startswith("gfx/") and texture.group(1) != vanilla_placeholder and not (MOD / texture.group(1)).is_file():
            name_match = re.search(r'\bname\s*=\s*"([^"]+)"', sprite)
            fail(f"missing doctrine icon texture for {name_match.group(1) if name_match else 'unnamed sprite'}")

    if manifest:
        expected_parent_count = sum(row["parent"] is not None for row in manifest)
        expected_date_count = sum(row["decade"] > 1940 for row in manifest)
        if expected_parent_count != 67 or expected_date_count != 70:
            fail("reviewed land manifest counts changed: expected 67 lineage and 70 date gates")
        # Static route model: the graph must expose a route to each terminal,
        # while header conjunctions enforce the reviewed date and lineage.
        for row in manifest:
            header = row["header"]
            terminal = row["terminal"]
            reachable = {header}
            frontier = [header]
            while frontier:
                node = frontier.pop()
                for target in outgoing.get(node, []):
                    if target not in reachable:
                        reachable.add(target)
                        frontier.append(target)
            if terminal not in reachable:
                fail(f"static route model cannot reach terminal {terminal} from {header}")

        def model_eligible(row: dict[str, object], year: int, owned: set[str], researching: set[str]) -> bool:
            if year < row["decade"]:
                return False
            parent = row["parent"]
            if parent is not None and parent not in owned:
                return False
            if row["header"] in LAND_ROOTS:
                rival_roots = set(LAND_ROOTS) - {row["header"]}
                if rival_roots & (owned | researching):
                    return False
            return True

        for year, expected_roots in (
            (1949, {row["header"] for row in manifest if row["decade"] == 1940}),
            (1980, {row["header"] for row in manifest if row["header"] in LAND_ROOTS and row["decade"] <= 1980}),
        ):
            eligible = {row["header"] for row in manifest if model_eligible(row, year, set(), set())}
            if eligible != expected_roots:
                fail(f"static date model has the wrong eligible headers at {year}")
        for row in manifest:
            if row["decade"] <= 1940:
                continue
            parent_owned = set() if row["parent"] is None else {row["parent"]}
            if model_eligible(row, row["decade"] - 1, parent_owned, set()):
                fail(f"static date model accepts {row['header']} before {row['decade']}.1.1")
            if not model_eligible(row, row["decade"], parent_owned, set()):
                fail(f"static date model rejects {row['header']} on {row['decade']}.1.1")
            if row["parent"] is not None and model_eligible(row, row["decade"], set(), set()):
                fail(f"static lineage model unlocks {row['header']} without its predecessor")
        for root in LAND_ROOTS:
            root_row = manifest_by_header.get(root)
            if root_row is None:
                continue
            for rival in set(LAND_ROOTS) - {root}:
                if model_eligible(root_row, root_row["decade"], {rival}, set()) or model_eligible(root_row, root_row["decade"], set(), {rival}):
                    fail(f"static root exclusion model permits {root} after {rival}")
        children_by_parent: dict[str, list[dict[str, object]]] = {}
        for row in manifest:
            if row["parent"] is not None:
                children_by_parent.setdefault(row["parent"], []).append(row)
        for parent, children in children_by_parent.items():
            if len(children) < 2:
                continue
            year = max(child["decade"] for child in children)
            if not all(model_eligible(child, year, {parent}, set()) for child in children):
                fail(f"static sibling model cannot unlock all children of {parent}")

        # Follow each independent root through its manifest descendants. This
        # permits multiple native branch routes inside a cell without inventing
        # an all-branches prerequisite for the terminal.
        for root in LAND_ROOTS:
            owned_terminals: set[str] = set()
            completed: set[str] = set()
            changed = True
            while changed:
                changed = False
                for row in manifest:
                    if row["header"] in completed:
                        continue
                    if row["parent"] is None:
                        available = row["header"] == root
                    else:
                        available = row["parent"] in owned_terminals
                    if available and model_eligible(row, max(1949, row["decade"]), owned_terminals, set()):
                        completed.add(row["header"])
                        owned_terminals.add(row["terminal"])
                        changed = True
            expected_family = {root}
            changed = True
            while changed:
                changed = False
                for row in manifest:
                    if row["parent"] in {manifest_by_header[name]["terminal"] for name in expected_family} and row["header"] not in expected_family:
                        expected_family.add(row["header"])
                        changed = True
            if completed != expected_family:
                fail(f"static family route model cannot complete descendants of {root}")


def fail(message: str) -> None:
    errors.append(message)


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig", errors="replace")
    except FileNotFoundError:
        fail(f"missing required file: {path.relative_to(ROOT)}")
        return ""


def code_only(value: str) -> str:
    return "\n".join(line.split("#", 1)[0] for line in value.splitlines())


def brace_balance(path: Path) -> None:
    value = code_only(text(path))
    depth = 0
    for number, line in enumerate(value.splitlines(), 1):
        depth += line.count("{") - line.count("}")
        if depth < 0:
            fail(f"negative brace depth: {path.relative_to(ROOT)}:{number}")
            return
    if depth:
        fail(f"unbalanced braces ({depth:+d}): {path.relative_to(ROOT)}")


def top_level_blocks(value: str, root_name: str) -> list[tuple[str, str]]:
    lines = value.splitlines(keepends=True)
    depth = 0
    inside = False
    start: int | None = None
    name: str | None = None
    result: list[tuple[str, str]] = []
    for index, line in enumerate(lines):
        code = line.split("#", 1)[0]
        if not inside and re.match(rf"^{re.escape(root_name)}\s*=\s*\{{", code):
            inside = True
            depth += code.count("{") - code.count("}")
            continue
        if not inside:
            continue
        if depth == 1:
            match = re.match(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{", code)
            if match:
                start = index
                name = match.group(1)
        depth += code.count("{") - code.count("}")
        if start is not None and depth == 1:
            result.append((name or "", "".join(lines[start : index + 1])))
            start = None
            name = None
        if depth <= 0:
            # The root closed. Anything after it is a sibling section, not a
            # child: `x_tank_chassis.txt` carries `duplicate_archetypes` and an
            # `equipments` block, and without this the second section's rows
            # were reported as role roots.
            break
    return result


def located_keyed_blocks(value: str, key: str) -> list[tuple[int, str]]:
    """Every balanced `key = { ... }` block with its start offset.

    The single lenient brace scanner in this file. `keyed_blocks` is the
    offset-free view of it; do not add a third scanner.
    """
    value = code_only(value)
    result: list[tuple[int, str]] = []
    pattern = re.compile(rf"\b{re.escape(key)}\s*=\s*\{{")
    for match in pattern.finditer(value):
        depth = 0
        for index in range(match.end() - 1, len(value)):
            if value[index] == "{":
                depth += 1
            elif value[index] == "}":
                depth -= 1
                if depth == 0:
                    result.append((match.start(), value[match.start() : index + 1]))
                    break
        else:
            fail(f"unbalanced {key} block")
    return result


def keyed_blocks(value: str, key: str) -> list[str]:
    """Return every balanced `key = { ... }` block from comment-free script."""
    return [block for _, block in located_keyed_blocks(value, key)]


def direct_values(block: str, key: str) -> list[str]:
    """Read simple direct values from a balanced block."""
    return top_level_values(block, key)

def equipment_type_domain(block: str) -> set[str]:
    if not block:
        return set()
    direct = direct_values(block, "type")
    if direct:
        return set(re.findall(r"\w+", " ".join(direct)))
    listed = re.findall(r"\btype\s*=\s*\{([^}]*)\}", block)
    return set(re.findall(r"\w+", " ".join(listed)))


def format_type_domain(domain: set[str]) -> str:
    return "{" + ", ".join(sorted(domain)) + "}"

def removed_tank_role_errors(role_blocks: dict[str, str]) -> list[str]:
    return sorted(REMOVED_TANK_ROLE_ROOTS & set(role_blocks))


def removed_tank_blueprint_errors(names: list[str]) -> list[str]:
    return sorted(name for name in names if REMOVED_TANK_BLUEPRINT_PATTERN.fullmatch(name))




# Owner decision 2026-09-10 phase 3 restructure reserves size tokens for plain
# gun hulls; all role roots must omit these tokens.
TANK_SIZE_TOKENS = {"light_armor", "medium_armor", "heavy_armor"}
# Owner decision 2026-09-10 role-token remap: this is the complete legal set
# for module eligibility values and for non-armor tokens on the three tank
# hulls and their role roots.
LEGAL_TANK_DESIGNER_TYPE_TOKENS = frozenset(
    {
        "anti_air",
        "anti_tank",
        "artillery",
        "amphibious",
        "rocket",
        "flame",
        "light_armor",
        "medium_armor",
        "heavy_armor",
    }
)
# `mechanized` is a vanilla equipment type but NOT a designer role - the
# 2026-09-10 probe showed it never reaches the dropdown. It stays legal on
# legacy mechanized family rows, where REFERENCE.md records it as load bearing
# for land/transport classification and every `transport = mechanized_equipment`
# consumer. Those rows are compatibility content, not designer role roots; APC
# uses `flame`, while `amphibious` remains reserved for a future dedicated role.
LEGAL_CARRIER_FAMILY_TYPE_TOKENS = LEGAL_TANK_DESIGNER_TYPE_TOKENS | {"mechanized"}


def unsupported_tank_designer_tokens(
    tokens: set[str], subject: str
) -> list[str]:
    unsupported = sorted(tokens - LEGAL_TANK_DESIGNER_TYPE_TOKENS)
    if not unsupported:
        return []
    return [
        f"{subject} uses unsupported designer type token(s): {unsupported}; "
        "custom tokens cannot be designer roles. The 2026-09-10 in-game probe "
        "showed amphibious, rocket, and flame as selectable roles, while ifv, "
        "atgm, and mechanized never appeared."
    ]


def tank_module_designer_token_errors(
    definitions: dict[str, str],
) -> list[str]:
    result: list[str] = []
    for module, definition in definitions.items():
        eligibility_tokens = (
            equipment_type_tokens(definition, "allow_equipment_type")
            | equipment_type_tokens(definition, "forbid_equipment_type")
        )
        result.extend(
            unsupported_tank_designer_tokens(
                eligibility_tokens,
                f"tank module {module} eligibility",
            )
        )
    return result


def tank_type_domain_token_errors(blocks: dict[str, str]) -> list[str]:
    result: list[str] = []
    carrier_families = {
        "mechanized_equipment",
        "mechanized_heavy_equipment",
    }
    for name, block in blocks.items():
    # Legacy carrier family rows keep `mechanized` for land/transport
    # classification; they are compatibility content, not designer role roots.
        legal = (
            LEGAL_CARRIER_FAMILY_TYPE_TOKENS
            if name in carrier_families or re.fullmatch(r"light_tank_(apc|ifv)_chassis_\d+", name)
            else LEGAL_TANK_DESIGNER_TYPE_TOKENS
        )
        unsupported = sorted((equipment_type_domain(block) - {"armor"}) - legal)
        if unsupported:
            result.extend(
                unsupported_tank_designer_tokens(
                    set(unsupported), f"tank archetype/role {name} type domain"
                )
            )
    return result


def equipment_type_tokens(block: str, key: str) -> set[str]:
    """Read a scalar or block-form equipment eligibility key."""
    values = set(direct_values(block, key))
    values.update(
        token
        for listed in keyed_blocks(block, key)
        for token in re.findall(r"\w+", listed[listed.find("{") + 1 : -1])
    )
    return values


def tank_module_type_bound_errors(definitions: dict[str, str]) -> list[str]:
    """Return role-exclusivity and hardcoded-token violations."""
    result = tank_module_designer_token_errors(definitions)
    # Owner decision 2026-09-11 carrier role consolidation keeps exact-match
    # eligibility retired; the engine's hardcoded role implementation accepts
    # the allow-plus-forbid bounds below instead.
    exact_match = sorted(
        module
        for module, definition in definitions.items()
        if re.search(r"\bforbid_equipment_type_exact_match\s*=", definition)
    )
    if exact_match:
        result.append(
            "tank modules must not use forbid_equipment_type_exact_match: "
            f"{exact_match}"
        )
    # Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
    # remains deliberately unspent and reserved for a future dedicated amphibious
    # mechanized role.
    carrier_categories = {
        "tank_apc_superstructure": ({"flame"}, TANK_SIZE_TOKENS | {"rocket"}),
        "tank_apc_armament": ({"flame"}, TANK_SIZE_TOKENS | {"rocket"}),
        "tank_ifv_superstructure": ({"rocket"}, TANK_SIZE_TOKENS | {"flame"}),
        "tank_ifv_armament": ({"rocket"}, TANK_SIZE_TOKENS | {"flame"}),
    }
    # Owner decision 2026-09-11 carrier role consolidation keeps carrier
    # modules role-exclusive despite allow_equipment_type extending eligibility.
    for module, definition in definitions.items():
        category = (direct_values(definition, "category") or [""])[0]
        if category not in carrier_categories:
            continue
        expected_allow, expected_forbid = carrier_categories[category]
        actual_allow = equipment_type_tokens(definition, "allow_equipment_type")
        actual_forbid = equipment_type_tokens(definition, "forbid_equipment_type")
        if actual_allow != expected_allow:
            result.append(
                f"{module} must allow {format_type_domain(expected_allow)}, "
                f"found {format_type_domain(actual_allow)}"
            )
        if actual_forbid != expected_forbid:
            result.append(
                f"{module} must forbid {format_type_domain(expected_forbid)}, "
                f"found {format_type_domain(actual_forbid)}"
            )
    # Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and
    # `amphibious` remains deliberately unspent and reserved for a future dedicated
    # amphibious mechanized role.
    conventional_categories = {
        "tank_small_main_armament",
        "tank_low_pressure_main_armament",
        "tank_medium_main_armament",
        "tank_heavy_main_armament",
    }
    conventional_forbid = {"flame", "rocket"}
    aa_forbid = TANK_SIZE_TOKENS | {"flame", "rocket"}
    for module, definition in definitions.items():
        category = (direct_values(definition, "category") or [""])[0]
        actual_forbid = equipment_type_tokens(definition, "forbid_equipment_type")
        if (
            category in conventional_categories
            and module not in AA_ARMAMENT_MODULES
            and module != "tank_atgm_launcher_cannon"
            and actual_forbid != conventional_forbid
        ):
            result.append(
                f"{module} must forbid {format_type_domain(conventional_forbid)}"
            )
        if (
            module in AA_ARMAMENT_MODULES or module == "tank_atgm_launcher_cannon"
        ) and actual_forbid != aa_forbid:
            result.append(
                f"{module} must forbid {format_type_domain(aa_forbid)}"
            )
    return result


def validate_tank_type_domains(chassis_text: str, role_text: str) -> None:
    # Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
    # remains deliberately unspent and reserved for a future dedicated amphibious
    # mechanized role.
    expected_archetypes = {
        "light_tank_chassis": {"armor", "light_armor"},
        "medium_tank_chassis": {"armor", "medium_armor"},
        "heavy_tank_chassis": {"armor", "heavy_armor"},
    }
    # Owner decision 2026-09-11 carrier role consolidation defines the ten
    # surviving role roots with only armor plus their hardcoded role token(s),
    # never a size token; IFV has no separate role root.
    expected_role_domains = {
        "light_tank_aa_chassis": {"armor", "anti_air"},
        "medium_tank_aa_chassis": {"armor", "anti_air"},
        "light_tank_artillery_chassis": {"armor", "artillery"},
        "medium_tank_artillery_chassis": {"armor", "artillery"},
        "heavy_tank_artillery_chassis": {"armor", "artillery"},
        "light_tank_destroyer_chassis": {"armor", "anti_tank"},
        "medium_tank_destroyer_chassis": {"armor", "anti_tank"},
        "heavy_tank_destroyer_chassis": {"armor", "anti_tank"},
        "light_tank_apc_chassis": {"armor", "flame"},
        "medium_tank_apc_chassis": {"armor", "flame"},
        "light_tank_ifv_chassis": {"armor", "rocket"},
        "medium_tank_ifv_chassis": {"armor", "rocket"},
    }
    chassis_blocks = dict(top_level_blocks(chassis_text, "equipments"))
    for archetype, expected in expected_archetypes.items():
        actual = equipment_type_domain(chassis_blocks.get(archetype, ""))
        if actual != expected:
            fail(
                f"{archetype} type domain must be {format_type_domain(expected)}, "
                f"found {format_type_domain(actual)}"
            )

    role_blocks = dict(top_level_blocks(role_text, "duplicate_archetypes"))
    for role in removed_tank_role_errors(role_blocks):
        fail(f"removed tank role root remains: {role}")
    # Owner decision 2026-09-11 carrier role consolidation pins the role-root
    # set to exactly ten; an unexpected IFV/custom root could revive the broken
    # multi-role hull list despite the five-token engine constraint.
    unexpected_role_roots = sorted(set(role_blocks) - set(expected_role_domains))
    if unexpected_role_roots:
        fail(f"unexpected tank role roots remain: {unexpected_role_roots}")
    # The flame-family name check remains: token use does not restore retired
    # flame chassis roots.
    flame_family_holders = sorted(
        name for name in {**chassis_blocks, **role_blocks} if "flame" in name
    )
    if flame_family_holders:
        fail(f"removed flame chassis family remains: {flame_family_holders}")
    # Owner decision 2026-09-11 carrier role consolidation rejects custom type
    # tokens in every chassis archetype and role domain, not only known roots.
    for message in tank_type_domain_token_errors({**chassis_blocks, **role_blocks}):
        fail(message)
    # Owner decision 2026-09-11 carrier role consolidation retains the
    # no-size-token rule on all ten surviving role roots.
    for role, expected in expected_role_domains.items():
        actual = equipment_type_domain(role_blocks.get(role, ""))
        if actual != expected:
            fail(
                f"{role} type domain must be {format_type_domain(expected)}, "
                f"found {format_type_domain(actual)}"
            )
        size_tokens = actual & TANK_SIZE_TOKENS
        if size_tokens:
            fail(
                f"{role} type domain must not contain plain-gun size tokens "
                f"{format_type_domain(size_tokens)}"
            )
    # Owner QA 2026-09-10, from the live log. The two script enums are NOT
    # interchangeable and only one of them is extensible.
    #
    # `script_enum_equipment_category` mirrors EQUIPMENT_CATEGORY_META, which is
    # hardcoded in the binary. Adding a custom token there logs
    # `equipment_category.cpp:357: <token> is in script enum
    # script_enum_equipment_category but is not an equipment stat`. Custom
    # equipment `type` tokens are legal on an archetype and must NOT be declared
    # here - the attempt to fix the role dropdown that way produced five such
    # lines and fixed nothing.
    # Owner decision 2026-09-10 role-token remap rejects custom names in the
    # hardcoded enum as well; size tokens belong only to equipment domains.
    custom_type_tokens = {"ifv", "atgm"} | TANK_SIZE_TOKENS
    enum_block = re.search(
        r"script_enum_equipment_category\s*=\s*\{(.*?)\n\}",
        strip_script_comments(text(ENUM_FILE)),
        re.DOTALL,
    )
    if enum_block is None:
        fail("script_enum_equipment_category is missing from common/script_enums.txt")
        return
    declared_categories = set(enum_block.group(1).split())
    intruders = sorted(custom_type_tokens & declared_categories)
    if intruders:
        fail(
            "custom equipment type tokens must not be declared in the hardcoded "
            f"script_enum_equipment_category: {intruders}"
        )
    #
    # Owner decision 2026-09-11 carrier role consolidation keeps the engine's
    # irregular derived-variant shapes while FAMILY_ROLES supplies ten role
    # names; the hardcoded five-token role list cannot safely carry IFV roots.
    bonus_block = re.search(
        r"script_enum_equipment_bonus_type\s*=\s*\{(.*?)\n\}",
        strip_script_comments(text(ENUM_FILE)),
        re.DOTALL,
    )
    if bonus_block is None:
        fail("script_enum_equipment_bonus_type is missing from common/script_enums.txt")
        return
    declared_bonus = set(bonus_block.group(1).split())
    derived_shape = {"light": ("t_equipment_", range(1, 7)), "medium": ("bt_equipment_", range(0, 10)), "heavy": ("t_equipment_", range(1, 6))}
    expected_derived = {
        f"{family}_tank_{role}_chassis{suffix}{index}"
        for family, (suffix, indices) in derived_shape.items()
        for role in FAMILY_ROLES[family]
        for index in indices
    }
    missing_derived = sorted(expected_derived - declared_bonus)
    if missing_derived:
        fail(
            "script_enum_equipment_bonus_type omits derived role variant ids the "
            f"engine emits: {missing_derived[:6]} ({len(missing_derived)} total)"
        )
    stale_derived = sorted(
        entry
        for entry in declared_bonus
        if re.fullmatch(r"(light|medium|heavy)_tank_\w+_chassis(b?)t_equipment_\d+", entry)
        and entry not in expected_derived
    )
    if stale_derived:
        fail(
            "script_enum_equipment_bonus_type keeps derived variant ids for roles "
            f"that no longer exist: {stale_derived}"
        )
    # A declared equipment category is itself a bonus type; `flame` survives as a
    # category for the MIO policies, so it must stay listed here too.
    missing_categories = sorted(declared_categories - declared_bonus)
    if missing_categories:
        fail(
            "script_enum_equipment_bonus_type omits declared equipment categories: "
            f"{missing_categories}"
        )




def listed_values(block: str) -> list[str]:
    """Read bare values from a list block such as enable_equipments."""
    value = strip_script_comments(block)
    opening = value.find("{")
    if opening < 0:
        raise ScriptParseError("missing opening brace while reading list block")
    ending = balanced_end(value, opening, "list block")
    return re.findall(r"(?m)^\s*([A-Za-z0-9_]+)\s*$", value[opening + 1 : ending])






def module_parent_errors(definitions: dict[str, str]) -> list[str]:
    errors_found: list[str] = []
    parents: dict[str, str] = {}
    for name, block in definitions.items():
        values = direct_values(block, "parent")
        if len(values) > 1:
            errors_found.append(f"tank module {name} has multiple parents")
        if not values:
            continue
        parent = values[0]
        if parent not in definitions:
            errors_found.append(f"tank module {name} has undefined parent {parent}")
        else:
            parents[name] = parent
    for name in definitions:
        trail: set[str] = set()
        node = name
        while node in parents:
            if node in trail:
                errors_found.append(f"tank module parent graph contains a cycle at {node}")
                break
            trail.add(node)
            node = parents[node]
    return errors_found


def abbreviation_errors(definitions: dict[str, str]) -> list[str]:
    errors_found: list[str] = []
    abbreviations: dict[str, str] = {}
    for name, block in definitions.items():
        values = re.findall(r"(?m)^\s*abbreviation\s*=\s*\"([^\"]+)\"", block)
        if len(values) != 1:
            errors_found.append(f"tank module {name} must have one abbreviation")
            continue
        previous = abbreviations.get(values[0])
        if previous and previous != name:
            errors_found.append(f"tank module abbreviation collision: {previous} and {name} use {values[0]}")
        abbreviations[values[0]] = name
    return errors_found


def secondary_unlock_errors(unlocked: set[str]) -> list[str]:
    return [
        f"secondary turret module is not unlocked: {module}"
        for module in SECONDARY_MODULES
        if module not in unlocked
    ]


def tank_self_loop_ids(technologies: dict[str, str]) -> set[str]:
    return {
        owner
        for owner, block in technologies.items()
        for path in top_level_named_blocks(block, "path", owner)
        if owner in direct_values(path, "leads_to_tech")
    }


def export_variant_map(value: str) -> dict[str, str]:
    variants: dict[str, str] = {}
    for block in keyed_blocks(value, "create_equipment_variant"):
        name_match = re.search(r"(?m)^\s*name\s*=\s*\"([^\"]+)\"", block)
        type_match = re.search(r"(?m)^\s*type\s*=\s*([A-Za-z0-9_]+)", block)
        if name_match and type_match:
            variants[name_match.group(1)] = type_match.group(1)
    return variants


def missing_ammunition_categories(installed_categories: set[str]) -> set[str]:
    return ammo_categories - installed_categories


def named_focus_blocks(value: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for kind in ("focus", "shared_focus"):
        for block in keyed_blocks(value, kind):
            match = re.search(r"(?m)^\s*id\s*=\s*([A-Za-z0-9_]+)", block)
            if match:
                result[match.group(1)] = block
    return result


def balance_manifest_rows() -> list[tuple[int, str, str, int, str]]:
    rows: list[tuple[int, str, str, int, str]] = []
    for line in text(BALANCE_MANIFEST_FILE).splitlines():
        if not line.startswith("|") or not re.match(r"\|\s*\d+\s*\|", line):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) < 5:
            fail(f"malformed tank balance manifest row: {line}")
            continue
        try:
            rows.append((int(fields[0]), fields[1], fields[2], int(fields[3]), fields[4]))
        except ValueError:
            fail(f"malformed tank balance manifest row: {line}")
    return rows


def balance_manifest_values() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in text(BALANCE_MANIFEST_FILE).splitlines():
        if not line.startswith("|") or not re.match(r"\|\s*\d+\s*\|", line):
            continue
        fields = [field.strip() for field in line.strip("|").split("|")]
        if len(fields) < 17:
            fail(f"tank balance manifest row lacks normalized target values: {line}")
            continue
        try:
            row: dict[str, object] = {
                "row": int(fields[0]),
                "name": fields[1],
                "kind": fields[2],
                "year": int(fields[3]),
                "role": fields[4],
            }
            for index, (metric, _, _) in enumerate(BALANCE_METRICS, start=5):
                raw = fields[index].replace(",", ".").strip()
                if raw in {"", "—", "-"}:
                    row[metric] = None
                    continue
                row[metric] = float(raw.rstrip("%"))
            rows.append(row)
        except (ValueError, IndexError) as error:
            fail(f"malformed normalized tank balance values: {line}")
    return rows


def read_balance_workbook(path: Path) -> list[dict[str, object]]:
    """Read the review rows with the standard library only."""
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    relationships_namespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    with ZipFile(path) as archive:
        strings_root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
        shared_strings = [
            "".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
            for item in strings_root.findall("main:si", namespace)
        ]
        workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
        relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        relationship_targets = {
            node.attrib["Id"]: node.attrib["Target"] for node in relationships
        }
        sheet_target = None
        for sheet in workbook.findall("main:sheets/main:sheet", namespace):
            if sheet.attrib.get("name") == "Total Balance Sheet":
                sheet_target = relationship_targets[
                    sheet.attrib[f"{{{relationships_namespace}}}id"]
                ]
                break
        if sheet_target is None:
            raise ValueError("Total Balance Sheet worksheet is missing")
        archive_path = "xl/" + sheet_target.lstrip("/")
        if archive_path.startswith("xl/xl/"):
            archive_path = archive_path[3:]
        worksheet = ElementTree.fromstring(archive.read(archive_path))
        rows: list[dict[str, object]] = []
        for row in worksheet.findall(".//main:sheetData/main:row", namespace):
            row_number = int(row.attrib["r"])
            cells: dict[str, str] = {}
            for cell in row.findall("main:c", namespace):
                reference = cell.attrib.get("r", "")
                value = cell.find("main:v", namespace)
                cell_value = "" if value is None else value.text or ""
                if cell.attrib.get("t") == "s" and cell_value:
                    cell_value = shared_strings[int(cell_value)]
                cells[reference.rstrip("0123456789")] = cell_value
            if row_number < 2 or not cells.get("A") or not cells.get("B"):
                continue
            try:
                year = int(float(cells["B"].replace(",", ".")))
            except ValueError as error:
                raise ValueError(f"invalid balance year in workbook row {row_number}") from error
            row: dict[str, object] = {
                "row": row_number,
                "name": cells["A"],
                "year": year,
            }
            for metric, column, percentage in BALANCE_METRICS:
                raw = cells.get(column, "").strip()
                if not raw:
                    row[metric] = None
                    continue
                try:
                    value = float(raw.replace(",", ".").rstrip("%"))
                except ValueError as error:
                    raise ValueError(
                        f"invalid balance value in workbook row {row_number}, column {column}"
                    ) from error
                row[metric] = value / 100 if percentage else value
            rows.append(row)
        return rows


def _xlsx_sheet_target(archive: ZipFile, sheet_name: str) -> str:
    """Resolve a worksheet through workbook relationships without openpyxl."""
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    relationships_namespace = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    relationships = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    targets = {node.attrib["Id"]: node.attrib["Target"] for node in relationships}
    for sheet in workbook.findall("main:sheets/main:sheet", namespace):
        if sheet.attrib.get("name") == sheet_name:
            target = targets[sheet.attrib[f"{{{relationships_namespace}}}id"]]
            path = "xl/" + target.lstrip("/")
            return path[3:] if path.startswith("xl/xl/") else path
    raise ValueError(f"worksheet is missing: {sheet_name}")


def _xlsx_shared_strings(archive: ZipFile) -> list[str]:
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t"))
        for item in root.findall("main:si", namespace)
    ]


def _xlsx_cell_value(cell: ElementTree.Element, shared_strings: list[str]) -> str:
    namespace = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    inline = cell.find(namespace + "is")
    if inline is not None:
        return "".join(node.text or "" for node in inline.iter(namespace + "t"))
    value = cell.find(namespace + "v")
    if value is None or value.text is None:
        return ""
    raw = value.text
    if cell.attrib.get("t") == "s" and raw:
        return shared_strings[int(raw)]
    return raw


def read_module_workbook(path: Path, sheet_name: str, id_column: str) -> dict[str, dict[str, object]]:
    """Read module rows while retaining cell presence for absent-versus-zero checks."""
    namespace = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(path) as archive:
        shared_strings = _xlsx_shared_strings(archive)
        worksheet = ElementTree.fromstring(archive.read(_xlsx_sheet_target(archive, sheet_name)))
        rows: dict[str, dict[str, object]] = {}
        for row in worksheet.findall(".//main:sheetData/main:row", namespace):
            row_number = int(row.attrib["r"])
            cells: dict[str, str] = {}
            present: set[str] = set()
            for cell in row.findall("main:c", namespace):
                reference = cell.attrib.get("r", "")
                column = reference.rstrip("0123456789")
                value = _xlsx_cell_value(cell, shared_strings)
                cells[column] = value
                if value.strip():
                    present.add(column)
            module = cells.get(id_column, "").strip()
            if not module or module == "Module Loc Name":
                continue
            if module not in module_ids:
                if row_number > 33 and not module.startswith(("Light_Hull_", "MBT_Hull_", "Heavy_Hull_")):
                    fail(f"unknown tank module ID in {sheet_name} row {row_number}: {module}")
                continue
            if module in rows:
                fail(f"duplicate {sheet_name} module row for {module}")
                continue
            rows[module] = {"row": row_number, "cells": cells, "present": present}
        return rows


def _decimal(value: str, *, percentage: bool = False, context: str = "value") -> float:
    raw = value.strip().replace(",", ".")
    if not raw:
        raise ValueError(f"empty numeric {context}")
    has_percent = raw.endswith("%")
    if has_percent:
        raw = raw[:-1].strip()
    try:
        result = float(raw)
    except ValueError as error:
        raise ValueError(f"malformed numeric {context}: {value!r}") from error
    if has_percent or percentage:
        return result / 100
    return result


def _numeric_block(block: str, label: str) -> dict[str, float]:
    """Read direct numeric assignments from one already-bounded child block."""
    value = strip_script_comments(block)
    opening = value.find("{")
    ending = balanced_end(value, opening, label)
    body = value[opening + 1 : ending]
    result: dict[str, float] = {}
    for match in re.finditer(
        r"(?m)^\s*([A-Za-z0-9_]+)\s*=\s*([-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?)\s*$",
        body,
    ):
        key, raw = match.groups()
        key = MODULE_FIELD_ALIASES.get(key, key)
        if key in result:
            fail(f"duplicate numeric field {key} in {label}")
        result[key] = float(raw)
    return result


def module_balance_record(module: str) -> dict[str, object]:
    """Extract direct module operations; parent effects remain explicit metadata."""
    definition = module_definitions.get(module, "")
    record: dict[str, object] = {"add": {}, "multiply": {}, "resources": {}}
    for operation in ("add_stats", "multiply_stats"):
        children = top_level_named_blocks(definition, operation, module)
        if len(children) > 1:
            fail(f"tank module {module} has multiple {operation} blocks")
        if children:
            record["add" if operation == "add_stats" else "multiply"] = _numeric_block(
                children[0], f"{module}.{operation}"
            )
    resources = top_level_named_blocks(definition, "build_cost_resources", module)
    if len(resources) > 1:
        fail(f"tank module {module} has multiple build_cost_resources blocks")
    if resources:
        record["resources"] = _numeric_block(resources[0], f"{module}.build_cost_resources")
    for field in ("hardness", "reliability", "breakthrough", "defense", "armor_value", "maximum_speed", "build_cost_ic", "fuel_consumption", "supply_consumption"):
        values = direct_values(definition, field)
        if values:
            record.setdefault("add", {})[MODULE_FIELD_ALIASES.get(field, field)] = float(values[0])
    dismantle = direct_values(definition, "dismantle_cost_ic")
    record["dismantle"] = float(dismantle[0]) if dismantle else None
    record["parent"] = (direct_values(definition, "parent") or ["none"])[0]
    record["category"] = (direct_values(definition, "category") or [""])[0]
    record["xp_present"] = bool(direct_values(definition, "xp_cost"))
    conversions = top_level_named_blocks(definition, "can_convert_from", module)
    conversion = []
    for child in conversions:
        category = (direct_values(child, "module_category") or [""])[0]
        cost = (direct_values(child, "convert_cost_ic") or [""])[0]
        conversion.append(f"module_category={category},convert_cost_ic={cost}")
    record["conversion"] = conversion
    numeric_fields = set(record["add"]) | set(record["multiply"])
    for field in sorted(numeric_fields):
        if field not in MODULE_BALANCE_COLUMNS:
            fail(f"unmapped numeric module stat {module}.{field}")
    for resource in record["resources"]:
        if resource not in MODULE_RESOURCE_COLUMNS:
            fail(f"unmapped module resource {module}.{resource}")
    return record


def module_unlock_provenance() -> dict[str, list[tuple[str, str | None]]]:
    result: dict[str, list[tuple[str, str | None]]] = {module: [] for module in module_ids}
    for technology, block, path in technology_blocks:
        if path not in {TECH_DIR / "NSB_armor.txt", TECH_DIR / "NSB_armor_modules.txt"}:
            continue
        year_values = direct_values(block, "start_year")
        year = year_values[0] if year_values else None
        for unlock in top_level_named_blocks(block, "enable_equipment_modules", technology):
            for module in listed_values(unlock):
                if module in result:
                    result[module].append((technology, year))
    return result


def _module_metadata(module: str, record: dict[str, object], unlocks: dict[str, list[tuple[str, str | None]]]) -> str:
    operations = []
    for operation in ("add", "multiply"):
        values = record[operation]
        if values:
            operations.append(
                f"{operation}=" + ",".join(f"{field}:{values[field]:g}" for field in sorted(values))
            )
    resources = record["resources"]
    if resources:
        operations.append("resources=" + ",".join(f"{key}:{resources[key]:g}" for key in sorted(resources)))
    provenance = unlocks.get(module, [])
    unlock_text = "|".join(
        f"{technology}@{year if year is not None else 'default/inherited'}"
        for technology, year in provenance
    ) or "default/inherited"
    conversion = "|".join(record["conversion"]) or "none"
    operation_text = "; ".join(operations) if operations else "none"
    return (
        f"parent={record['parent']}; unlock={unlock_text}; "
        f"xp_cost={'present' if record['xp_present'] else 'absent'}; "
        f"dismantle_cost_ic={record['dismantle'] if record['dismantle'] is not None else 'absent'}; "
        f"conversion={conversion}; operations={operation_text}; "
        "exclusions=category,eligibility,abbreviation,display"
    )


def _module_csv_rows(path: Path) -> dict[str, list[str]]:
    if not path.is_file():
        fail(f"tank module balance CSV is missing: {path.relative_to(ROOT)}")
        return {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.reader(handle))
    headers = [index for index, row in enumerate(rows) if len(row) > 7 and row[7] == "Module Loc Name"]
    if len(headers) < 2 or headers[0] != 0:
        fail("tank module balance CSV must contain two module-table headers with Module Loc Name at column 7")
    if not rows or len(rows[0]) <= 7 or rows[0][7] != "Module Loc Name":
        fail("tank module balance CSV header moved Module Loc Name from column 7")
    result: dict[str, list[str]] = {}
    hull_prefixes = ("Light_Hull_", "MBT_Hull_", "Heavy_Hull_")
    for line_number, row in enumerate(rows, 1):
        if len(row) <= 7:
            continue
        module = row[7].strip()
        if not module or module == "Module Loc Name":
            continue
        if row[0].strip().startswith("Coverage") or row[3].strip().endswith(" rows"):
            continue
        if module.startswith(hull_prefixes) or row[0].strip() == "Hulls":
            continue
        if module not in module_ids:
            fail(f"unknown tank module ID in balance CSV row {line_number}: {module}")
            continue
        if module in result:
            fail(f"duplicate tank module ID in balance CSV: {module}")
            continue
        if len(row) < 41:
            fail(f"tank module balance CSV row {line_number} is shorter than the stat/resource schema")
        result[module] = row
    return result


def _module_cell_value(cells: dict[str, str], column: str) -> str:
    return cells.get(column, "").strip()


def _is_module_annotation(value: str) -> bool:
    return value.strip() in MODULE_SOURCE_ANNOTATIONS


def _normalize_master_module_rows(rows: dict[str, dict[str, object]]) -> dict[str, dict[str, object]]:
    """Project the master table's S:BG layout onto the minimal table's A:AO layout."""
    def column_letter(number: int) -> str:
        result = ""
        while number:
            number, remainder = divmod(number - 1, 26)
            result = chr(ord("A") + remainder) + result
        return result

    master_columns = [column_letter(number) for number in range(_csv_column_index("S") + 1, _csv_column_index("BH") + 2)]
    minimal_columns = [column_letter(number) for number in range(1, len(master_columns) + 1)]
    result: dict[str, dict[str, object]] = {}
    for module, row in rows.items():
        cells = row["cells"]
        present = row["present"]
        result[module] = {
            **row,
            "cells": {minimal: cells.get(master, "") for master, minimal in zip(master_columns, minimal_columns)},
            "present": {minimal for master, minimal in zip(master_columns, minimal_columns) if master in present},
        }
    return result


def _compare_module_row(module: str, row: dict[str, object] | list[str], record: dict[str, object], source: str) -> tuple[int, int]:
    if isinstance(row, dict):
        cells = row["cells"]
        present = row["present"]
        get = lambda column: _module_cell_value(cells, column)
        is_present = lambda column: column in present
    else:
        cells = row
        get = lambda column: cells[ord(column) - ord("A")] if len(column) == 1 and ord(column) <= ord("Z") else cells[_csv_column_index(column)] if _csv_column_index(column) < len(cells) else ""
        is_present = lambda column: bool(get(column).strip())

    checked = 0
    populated = set()
    for metric, (flat_column, _, multiply_column, _) in MODULE_BALANCE_COLUMNS.items():
        add_value = record["add"].get(metric)
        multiply_value = record["multiply"].get(metric)
        expected_by_column = {
            flat_column: (add_value if multiply_column is not None or add_value is not None else multiply_value)
        }
        if multiply_column:
            expected_by_column[multiply_column] = multiply_value
        for column, expected in expected_by_column.items():
            if expected is not None:
                checked += 1
                if not is_present(column):
                    fail(f"{source} module {module} is missing {column} for {metric}")
                else:
                    try:
                        actual = _decimal(get(column), context=f"{source} {module}.{metric}")
                    except ValueError as error:
                        fail(str(error))
                        actual = None
                    if actual is not None and abs(actual - expected) > 1e-9:
                        fail(f"{source} module {module}.{metric}: {actual:g} != {expected:g}")
                populated.add(column)
        for column in expected_by_column:
            if column and is_present(column):
                if _is_module_annotation(get(column)):
                    continue
                if column not in populated:
                    fail(f"{source} module {module} has unmapped populated stat column {column}")
    if record["dismantle"] is not None:
        checked += 1
        if not is_present(MODULE_DISMANTLE_COLUMN[0]):
            fail(f"{source} module {module} is missing dismantle_cost_ic")
        else:
            try:
                actual = _decimal(get(MODULE_DISMANTLE_COLUMN[0]), context=f"{source} {module}.dismantle_cost_ic")
            except ValueError as error:
                fail(str(error))
                actual = None
            if actual is not None and abs(actual - record["dismantle"]) > 1e-9:
                fail(f"{source} module {module}.dismantle_cost_ic: {actual:g} != {record['dismantle']:g}")
    for resource, (column, _) in MODULE_RESOURCE_COLUMNS.items():
        expected = record["resources"].get(resource)
        if expected is not None:
            checked += 1
            if not is_present(column):
                fail(f"{source} module {module} is missing resource {resource}")
            else:
                try:
                    actual = _decimal(get(column), context=f"{source} {module}.{resource}")
                except ValueError as error:
                    fail(str(error))
                    actual = None
                if actual is not None and abs(actual - expected) > 1e-9:
                    fail(f"{source} module {module}.{resource}: {actual:g} != {expected:g}")
        elif is_present(column):
            fail(f"{source} module {module} has unmapped populated resource column {column}")
    metadata_column = MODULE_OPERATION_COLUMN[0]
    if module in SCRIPT_OWNED_MODULES:
        if not is_present(metadata_column):
            fail(f"{source} module {module} is missing operation/provenance metadata")
        else:
            metadata = get(metadata_column)
            for token in ("parent=", "unlock=", "xp_cost=", "dismantle_cost_ic=", "conversion=", "operations=", "exclusions="):
                if token not in metadata:
                    fail(f"{source} module {module} metadata lacks {token}")
    return checked, len(populated)


def _csv_column_index(column: str) -> int:
    result = 0
    for character in column:
        result = result * 26 + ord(character) - ord("A") + 1
    return result - 1


def tank_module_balance_report() -> str:
    if not BALANCE_WORKBOOK_FILE.is_file():
        fail("tank balance workbook is missing for --tank-module-balance-report")
        return ""
    csv_rows = _module_csv_rows(BALANCE_CSV_FILE)
    minimal = read_module_workbook(BALANCE_WORKBOOK_FILE, "Total Balance Sheet Minimal", "H")
    master = _normalize_master_module_rows(
        read_module_workbook(BALANCE_WORKBOOK_FILE, "Total Balance Sheet", "Z")
    )
    exempt = (
        set(APC_SUPERSTRUCTURE_MODULES) | set(APC_ARMAMENT_MODULES)
        | set(IFV_SUPERSTRUCTURE_MODULES) | set(IFV_ARMAMENT_MODULES)
    )
    sourced_modules = module_ids - exempt
    if exempt - module_ids:
        fail(f"workbook-exempt modules that no longer exist: {sorted(exempt - module_ids)}")
    if len(csv_rows) != len(sourced_modules):
        fail(f"tank balance CSV has {len(csv_rows)} module rows; expected {len(sourced_modules)}")
    for source, rows in (("CSV", csv_rows), ("Minimal", minimal), ("Master", master)):
        missing = sourced_modules - set(rows)
        extra = set(rows) - sourced_modules
        if missing:
            fail(f"{source} tank balance is missing module IDs: {sorted(missing)}")
        if extra:
            fail(f"{source} tank balance has unknown module IDs: {sorted(extra)}")
    unlocks = module_unlock_provenance()
    checked = 0
    populated = 0
    for module in sorted(sourced_modules):
        record = module_balance_record(module)
        for source, rows in (("CSV", csv_rows), ("Minimal", minimal), ("Master", master)):
            if module not in rows:
                continue
            source_record = record
            # The workbook is immutable. Reviewed source-to-live overrides live in
            # the CSV and script; still verify the old source cells explicitly.
            # See DECISIONS.md for the conventional turret balance and base
            # gasoline engine speed ordering.
            if module == "conventional_turret" and source != "CSV":
                source_record = record | {
                    "add": {"build_cost_ic": 1.0, "reliability": 0.15},
                    "multiply": {},
                    "dismantle": 0.5,
                }
            if module == "tank_gasoline_engine" and source != "CSV":
                source_record = record | {"multiply": {"maximum_speed": 0.15}}
            row_checked, row_populated = _compare_module_row(module, rows[module], source_record, source)
            checked += row_checked
            populated += row_populated
            if source in {"Minimal", "Master"}:
                cells = rows[module]["cells"]
                other = csv_rows.get(module)
                if other:
                    for metric, (column, csv_index, multiply_column, multiply_index) in MODULE_BALANCE_COLUMNS.items():
                        if module == "conventional_turret" and metric in {"build_cost_ic", "breakthrough"}:
                            continue  # Explicit source-to-live deviation, checked above and by turret_contract.
                        if module == "tank_gasoline_engine" and metric == "maximum_speed":
                            continue  # Frozen workbook retains the pre-rebalance source value.
                        for workbook_column, csv_column in ((column, csv_index), (multiply_column, multiply_index)):
                            if workbook_column is None:
                                continue
                            workbook_value = _module_cell_value(cells, workbook_column)
                            csv_value = other[csv_column].strip() if csv_column < len(other) else ""
                            if not workbook_value or not csv_value:
                                continue
                            if _is_module_annotation(workbook_value) or _is_module_annotation(csv_value):
                                continue
                            try:
                                workbook_number = _decimal(workbook_value, context=f"{source} {module}.{metric}")
                                csv_number = _decimal(csv_value, context=f"CSV {module}.{metric}")
                            except ValueError as error:
                                fail(str(error))
                                continue
                            if abs(workbook_number - csv_number) > 1e-9:
                                fail(f"{source}/CSV mismatch for {module}.{metric}")
    missing_script_owned = SCRIPT_OWNED_MODULES - module_ids
    if missing_script_owned:
        fail(f"script-owned module list contains undefined IDs: {sorted(missing_script_owned)}")
    metadata_count = sum(
        1 for module in SCRIPT_OWNED_MODULES if module in minimal and MODULE_OPERATION_COLUMN[0] in minimal[module]["present"]
    )
    if metadata_count != len(SCRIPT_OWNED_MODULES):
        fail(f"operation/provenance metadata covers {metadata_count}/{len(SCRIPT_OWNED_MODULES)} script-owned modules")
    return (
        f"Tank module balance report: {len(sourced_modules)} IDs reconciled across CSV, "
        f"Total Balance Sheet Minimal, and Total Balance Sheet; {checked} populated "
        f"stat/resource cells checked; operation/provenance metadata {metadata_count}/{len(SCRIPT_OWNED_MODULES)}; "
        f"21 script-owned IDs reconciled; 2 reviewed source-to-live overrides; "
        f"explicit exclusions cover eligibility, display, conversion, and XP fields "
        f"(the manual's 23 count has no additional module ID); "
        f"{len(APC_SUPERSTRUCTURE_MODULES) + len(APC_ARMAMENT_MODULES)} APC and "
        f"{len(IFV_SUPERSTRUCTURE_MODULES) + len(IFV_ARMAMENT_MODULES)} IFV designer modules "
        f"are authored in script only and are "
        f"exempt from the frozen workbook: {sorted(exempt)}."
    )


ENVELOPE_METRICS = (
    "reliability",
    "hardness",
    "hard_attack",
    "soft_attack",
    "breakthrough",
    "defense",
    "armor_value",
    "ap_attack",
    "maximum_speed",
    "fuel_consumption",
    "build_cost_ic",
)
ENVELOPE_RECIPE_MAP = {
    "Heavy Tank I": "Standard Heavy Tank 1942",
    "Heavy Tank II": "Standard Heavy Tank 1944",
    "Heavy Tank IV": "Standard Heavy Tank 1950",
    "Heavy Tank V": "Standard Heavy Tank 1955",
    "WWII Tank 1": "Standard Main Battle Tank 1942",
    "WWII Tank 2": "Standard Main Battle Tank 1944",
    "MBT II": "Standard Main Battle Tank 1950",
    "MBT III": "Standard Main Battle Tank 1960",
    "Light Tank I": "Standard Light Tank 1942",
    "Light Tank II": "Standard Light Tank 1944",
    "Light Tank IV": "Standard Light Tank 1960",
}


def _variant_recipes() -> dict[tuple[str, str], dict[str, object]]:
    """Recipes keyed by (name, chassis).

    A design name is only unique per country: the carrier presets give many tags
    the same exported vehicle, and an incomplete national ladder can place that
    vehicle on a different hull tier. Identical repeats are expected.

    Since the 2026-09-11 carrier cutover a name can also repeat on one chassis
    with a different loadout, because two bookmark generations share a light hull
    tier: Albania's 1950 BTR-50PK mounts `ifv_autocannon_1` and East Germany's
    1955 one mounts `ifv_autocannon_2`, both on `light_tank_ifv_chassis_3`. That
    is legal content, so the entry is marked ambiguous rather than failed - the
    envelope report already refuses to sample an ambiguous name, and OOB requests
    resolve per producer through `bookmark_variant_names`.
    """
    recipes: dict[tuple[str, str], dict[str, object]] = {}
    for path in (VARIANT_EFFECT_FILE, FOCUS_EFFECT_FILE, NATIONAL_EFFECT_FILE, NAMING_EFFECT_FILE):
        for block in keyed_blocks(text(path), "create_equipment_variant"):
            name_match = re.search(r'(?m)^\s*name\s*=\s*"([^"]+)"', block)
            type_match = re.search(r"(?m)^\s*type\s*=\s*([A-Za-z0-9_]+)", block)
            if not name_match or not type_match:
                fail(f"tank recipe lacks name or chassis type in {path.name}")
                continue
            modules = top_level_named_blocks(block, "modules", name_match.group(1))
            if len(modules) != 1:
                fail(f"tank recipe {name_match.group(1)} must have one modules block")
                continue
            slots: list[tuple[str, str]] = []
            module_body = modules[0]
            opening = module_body.find("{")
            ending = balanced_end(module_body, opening, f"{name_match.group(1)}.modules")
            for match in re.finditer(
                r"(?m)^\s*([A-Za-z0-9_]+)\s*=\s*([A-Za-z0-9_]+)\s*$",
                module_body[opening + 1 : ending],
            ):
                if match.group(2) != "empty":
                    slots.append((match.group(1), match.group(2)))
            name = name_match.group(1)
            key = (name, type_match.group(1))
            record = {
                "name": name,
                "type": type_match.group(1),
                "slots": slots,
                "loadouts": [slots],
                "source": path.name,
            }
            if key in recipes and recipes[key]["slots"] != slots:
                # Legal since the carrier cutover: one chassis, one design name,
                # two national loadouts. Keep every loadout so slot legality is
                # still checked, and mark the entry unusable for name lookups.
                recipes[key]["ambiguous"] = True
                if slots not in recipes[key]["loadouts"]:
                    recipes[key]["loadouts"].append(slots)
                continue
            recipes.setdefault(key, record)
    return recipes


def _variant_recipes_by_name() -> dict[str, dict[str, object]]:
    """Name-only view for the envelope map, which samples unique tank designs."""
    by_name: dict[str, dict[str, object]] = {}
    for (name, _chassis), record in _variant_recipes().items():
        if record.get("ambiguous"):
            by_name[name] = {"name": name, "ambiguous": True}
            continue
        if name in by_name and by_name[name].get("slots") != record["slots"]:
            by_name[name] = {"name": name, "ambiguous": True}
            continue
        by_name.setdefault(name, record)
    return by_name


def _effective_module_operations(module: str, trail: tuple[str, ...] = ()) -> tuple[dict[str, float], dict[str, float], set[str]]:
    if module not in module_definitions:
        return {}, {}, {f"unknown module {module}"}
    if module in trail:
        return {}, {}, {f"module parent cycle at {module}"}
    record = module_balance_record(module)
    # A module parent identifies the preceding upgrade, not another installed
    # module. Summing it made Radar II consume 2.2 fuel instead of the observed
    # 1.2 and GL ATGM III supply 255 hard attack instead of the observed 95.
    # Parent validity/cycles remain checked separately by module_parent_errors.
    return dict(record["add"]), dict(record["multiply"]), set()


def _direct_chassis_numbers(block: str) -> dict[str, float]:
    aliases = {"armor_value": "armor_value"}
    numbers: dict[str, float] = {}
    for field in ENVELOPE_METRICS:
        values = direct_values(block, field)
        if not values:
            continue
        try:
            numbers[aliases.get(field, field)] = float(values[0])
        except ValueError as error:
            raise ValueError(f"malformed chassis numeric field {field}: {values[0]}") from error
    return numbers


def _static_recipe_estimate(recipe: dict[str, object]) -> tuple[dict[str, float], set[str], list[str]]:
    chassis_blocks = dict(top_level_blocks(text(CHASSIS_FILE), "equipments"))
    chassis_type = recipe["type"]
    unknown: set[str] = set()
    reasons = ["engine modifier order, caps, and role bonuses are not modeled"]
    if chassis_type not in chassis_blocks:
        return {}, {f"unknown chassis {chassis_type}"}, reasons
    try:
        base = _direct_chassis_numbers(chassis_blocks[chassis_type])
    except ValueError as error:
        fail(str(error))
        return {}, {"malformed chassis value"}, reasons
    adds: dict[str, float] = {}
    multipliers: dict[str, float] = {}
    slots = recipe["slots"]
    slot_names = {slot for slot, _ in slots}
    missing_slots = REQUIRED_VARIANT_SLOTS - slot_names
    if missing_slots:
        unknown.add("missing required slots: " + ",".join(sorted(missing_slots)))
    for slot, module in slots:
        if module not in module_ids:
            unknown.add(f"unknown module {module} in {slot}")
            continue
        module_adds, module_multipliers, module_unknown = _effective_module_operations(module)
        unknown.update(module_unknown)
        for field, value in module_adds.items():
            adds[field] = adds.get(field, 0.0) + value
        for field, value in module_multipliers.items():
            multipliers[field] = multipliers.get(field, 0.0) + value
    values: dict[str, float] = {}
    for metric in ENVELOPE_METRICS:
        value = base.get(metric, 0.0) + adds.get(metric, 0.0)
        values[metric] = value * (1.0 + multipliers.get(metric, 0.0))
    return values, unknown, reasons


def _format_estimate(value: float, metric: str) -> str:
    if metric in {"reliability", "hardness"}:
        return f"{value * 100:.1f}%"
    return f"{value:.2f}".rstrip("0").rstrip(".")


def tank_envelope_report() -> str:
    recipes = _variant_recipes_by_name()
    if not recipes:
        fail("tank envelope report found no selected tank recipes")
        return ""
    manifest = [row for row in balance_manifest_values() if row.get("kind") == "tank" and row.get("role") == "target"]
    if len(manifest) != 21:
        fail(f"tank envelope report has {len(manifest)} tank targets; expected 21")
    selected: dict[str, dict[str, object]] = {}
    for target, recipe_name in ENVELOPE_RECIPE_MAP.items():
        if target not in {row["name"] for row in manifest}:
            fail(f"tank envelope map names unknown target: {target}")
        if recipe_name not in recipes:
            fail(f"tank envelope map recipe is missing: {recipe_name}")
        elif recipes[recipe_name].get("ambiguous"):
            fail(f"tank envelope map recipe is not unique: {recipe_name}")
        else:
            selected[target] = recipes[recipe_name]
    if not selected:
        fail("tank envelope report selected sample set is empty")
        return ""
    lines = [
        f"Tank envelope report: {len(manifest)} tank targets; {len(selected)} explicitly mapped recipes; "
        f"{len(recipes)} shipped recipes parsed.",
        "Static estimates are diagnostic only: module upgrade parents are not stacked, repeated slots are counted, "
        "and unknown engine order/caps/role bonuses remain annotated rather than treated as zero.",
    ]
    role_counts = Counter()
    for recipe in recipes.values():
        name = recipe["name"]
        role_counts["SPAA" if "SPAA" in name else "SPG" if "SPG" in name else "tank"] += 1
    lines.append(
        "Recipe role separation: "
        + ", ".join(f"{role}={role_counts[role]}" for role in ("tank", "SPAA", "SPG"))
        + "."
    )
    manifest_by_name = {row["name"]: row for row in manifest}
    for target in ENVELOPE_RECIPE_MAP:
        target_row = manifest_by_name[target]
        recipe = selected[target]
        values, unknown, reasons = _static_recipe_estimate(recipe)
        deltas = []
        target_metric_map = {
            "reliability": "reliability",
            "hardness": "hardness",
            "hard_attack": "hard_attack",
            "soft_attack": "soft_attack",
            "breakthrough": "breakthrough",
            "defense": "defense",
            "armor": "armor_value",
            "piercing": "ap_attack",
            "speed": "maximum_speed",
            "fuel_usage": "fuel_consumption",
            "production_cost": "build_cost_ic",
        }
        for metric, source_metric in target_metric_map.items():
            expected = target_row.get(metric)
            if expected is None:
                continue
            deltas.append(f"{metric}={_format_estimate(values[source_metric] - expected, metric)}")
        status = "UNKNOWN: " + "; ".join(sorted(unknown)) if unknown else "estimate"
        lines.append(f"- {target} <- {recipe['name']}: {status}; deltas " + ", ".join(deltas))
    unsampled = [row["name"] for row in manifest if row["name"] not in selected]
    lines.append(
        "Unsampled exact target generations: "
        + (", ".join(unsampled) if unsampled else "none")
        + ". No nearest-year recipe was silently substituted."
    )
    return "\n".join(lines)


def tank_balance_report() -> str:
    manifest = balance_manifest_rows()
    if not BALANCE_WORKBOOK_FILE.is_file():
        fail("tank balance workbook is missing for --tank-balance-report")
        return ""
    workbook_rows = read_balance_workbook(BALANCE_WORKBOOK_FILE)
    if len(manifest) != 40:
        fail(f"tank balance manifest has {len(manifest)} rows; expected 40")
    if len(workbook_rows) < 40:
        fail(f"tank balance workbook has {len(workbook_rows)} review rows; expected at least 40")
        return ""
    workbook_review = workbook_rows[:40]
    manifest_review = [(row, name, year) for row, name, _, year, _ in manifest]
    workbook_identity = [(row["row"], row["name"], row["year"]) for row in workbook_review]
    if manifest_review != workbook_identity:
        fail("tank balance manifest no longer matches workbook rows 2-41")
    manifest_values = balance_manifest_values()
    if len(manifest_values) != 40:
        fail(f"tank balance manifest has {len(manifest_values)} normalized value rows; expected 40")
    for manifest_row, workbook_row in zip(manifest_values, workbook_review):
        for metric, _, _ in BALANCE_METRICS:
            if manifest_row.get(metric) != workbook_row.get(metric):
                fail(
                    f"tank balance value mismatch at workbook row {workbook_row['row']}, "
                    f"field {metric}: {manifest_row.get(metric)!r} != {workbook_row.get(metric)!r}"
                )
    target_rows = [row for row in manifest if row[4] == "target"]
    reference_rows = [row for row in manifest if row[4] == "reference"]
    if len(target_rows) != 39 or len(reference_rows) != 1:
        fail("tank balance manifest must contain 39 targets and one reference row")
    if Counter(row[2] for row in target_rows) != Counter({"tank": 21, "mech": 18}):
        fail("tank balance manifest must contain 21 tank and 18 mechanized targets")
    years = Counter(row["year"] for row in workbook_review)
    return (
        f"Tank balance report: {len(workbook_review)} workbook rows parsed "
        f"(39 targets, 1 Abrams reference), {sum(years.values())} year entries; "
        f"scope manifest: {BALANCE_MANIFEST_FILE.relative_to(ROOT)}"
    )


def named_block_spans(value: str, label: str) -> list[tuple[str, int, int, str]]:
    code = strip_script_comments(value)
    spans: list[tuple[str, int, int, str]] = []
    for match in re.finditer(r"\b([A-Za-z0-9_]+)\s*=\s*\{", code):
        opening = code.find("{", match.start(), match.end())
        ending = balanced_end(code, opening, f"{label}.{match[1]}")
        spans.append((match[1], match.start(), ending, code[match.start() : ending + 1]))
    return spans


def nearest_containing_span(
    spans: list[tuple[str, int, int, str]],
    start: int,
    end: int,
    name: str | None = None,
) -> tuple[str, int, int, str] | None:
    containing = [
        span for span in spans
        if (name is None or span[0] == name)
        and span[1] <= start
        and end <= span[2]
        and not (span[1] == start and span[2] == end)
    ]
    return min(containing, key=lambda span: span[2] - span[1], default=None)


def validate_focus_armour_grants(
    overrides: dict[str, str] | None = None,
) -> int:
    checked = 0
    overrides = overrides or {}
    for path in sorted(NATIONAL_FOCUS_DIR.rglob("*.txt")):
        relative = str(path.relative_to(ROOT))
        if relative in LEGACY_ARMOUR_GRANT_PATH_EXCEPTIONS:
            continue
        value = strip_script_comments(overrides.get(relative, text(path)))
        if not re.search(r"\badd_equipment_to_stockpile\s*=\s*\{", value):
            continue
        spans = named_block_spans(value, relative)
        for grant in (span for span in spans if span[0] == "add_equipment_to_stockpile"):
            type_values = top_level_values(grant[3], "type")
            if len(type_values) != 1 or not LEGACY_ARMOUR_GRANT.fullmatch(type_values[0]):
                continue
            equipment_type = type_values[0]
            if equipment_type in UNMIGRATED_LEGACY_ARMOUR:
                continue
            legacy_else = (
                nearest_containing_span(spans, grant[1], grant[2], "else")
                or nearest_containing_span(spans, grant[1], grant[2], "else_if")
            )
            if legacy_else is None:
                fail(f"{relative}:{value[:grant[1]].count(chr(10)) + 1} legacy {equipment_type} grant lacks an NSB fallback branch")
                continue
            parent = nearest_containing_span(spans, legacy_else[1], legacy_else[2])
            if parent is None:
                fail(f"{relative} legacy {equipment_type} grant has no conditional parent")
                continue
            parent_text = value[parent[1] : parent[2] + 1]
            children = top_level_ranges(parent_text, f"{relative} conditional parent")
            else_children = [
                (start, end, child) for name, start, end, child in children
                if name in {"else", "else_if"}
                and parent[1] + start <= grant[1] <= parent[1] + end
            ]
            preceding_if = [
                child for name, start, end, child in children
                if name == "if"
                and else_children
                and parent[1] + end < parent[1] + else_children[0][0]
                and 'has_dlc = "No Step Back"' in child
            ]
            if not else_children or not preceding_if:
                fail(f"{relative}:{value[:grant[1]].count(chr(10)) + 1} legacy {equipment_type} grant lacks a sibling NSB designer branch")

        for grant in (span for span in spans if span[0] == "add_equipment_to_stockpile"):
            variant_values = top_level_values(grant[3], "variant_name")
            type_values = top_level_values(grant[3], "type")
            if len(variant_values) != 1 or not variant_values[0].startswith("CWIC Export "):
                continue
            variant, equipment_type = variant_values[0], type_values[0] if len(type_values) == 1 else ""
            expected_type = EXPORT_VARIANTS.get(variant)
            if expected_type != equipment_type:
                fail(f"{relative}:{value[:grant[1]].count(chr(10)) + 1} export grant has wrong type for {variant}")
                continue
            designer_if = nearest_containing_span(spans, grant[1], grant[2], "if")
            if designer_if is None or 'has_dlc = "No Step Back"' not in designer_if[3]:
                fail(f"{relative}:{value[:grant[1]].count(chr(10)) + 1} export grant lacks its NSB branch")
                continue
            producer_values = top_level_values(grant[3], "producer")
            helper = "cwic_create_" + re.sub(r"[^A-Za-z0-9]+", "_", variant).lower().strip("_")[len("cwic_"):]
            producer_blocks = (
                top_level_named_blocks(designer_if[3], producer_values[0], relative)
                if len(producer_values) == 1
                else []
            )
            if not any(top_level_values(block, helper) == ["yes"] for block in producer_blocks):
                fail(f"{relative}:{value[:grant[1]].count(chr(10)) + 1} export grant lacks producer helper {helper}")
    return checked


def validate_legacy_armour_roles() -> None:
    """Keep the six retired armour families as empty compatibility shells."""
    role_rows = top_level_blocks(text(ROLE_CHASSIS_FILE), "equipments")
    role_row_map = dict(role_rows)
    legacy_roots = set(LEGACY_ARMOUR_ROLE_RELOCATIONS)
    expected_rows = {
        name: (root, target)
        for root, (_source, target, names) in LEGACY_ARMOUR_ROLE_RELOCATIONS.items()
        for name in names
    }

    locations: dict[str, list[tuple[Path, str]]] = {}
    for path in sorted(EQUIPMENT_DIR.rglob("*.txt")):
        for name, block in top_level_blocks(text(path), "equipments"):
            if name in expected_rows:
                locations.setdefault(name, []).append((path, block))
            parent = direct_values(block, "archetype")
            if parent and parent[0] in legacy_roots:
                fail(f"{name} must not be parented to legacy archetype {parent[0]}")

    for root, (source, target, names) in LEGACY_ARMOUR_ROLE_RELOCATIONS.items():
        source_rows = top_level_blocks(text(source), "equipments")
        source_map = dict(source_rows)
        root_block = source_map.get(root)
        if root_block is None:
            fail(f"{root} archetype is missing")
        elif direct_values(root_block, "is_archetype") != ["yes"]:
            fail(f"{root} must remain an archetype shell")
        members = [name for name, _ in source_rows if name != root]
        if members:
            fail(f"{root} archetype must have zero members; found {members}")
        for name in names:
            found = locations.get(name, [])
            role_found = [
                body for path, body in found if path == ROLE_CHASSIS_FILE
            ]
            if len(found) != 1 or len(role_found) != 1:
                paths = [str(path.relative_to(ROOT)) for path, _ in found]
                fail(
                    f"{name} must live only in {ROLE_CHASSIS_FILE.name}; "
                    f"found {paths or ['nowhere']}"
                )
            body = role_row_map.get(name)
            if body is None:
                continue
            if direct_values(body, "archetype") != [target]:
                fail(f"{name} must declare archetype = {target}")
            stat_keys = (
                LEGACY_SPAA_STAT_KEYS
                if root == "spaag_equipment"
                else LEGACY_ARMOUR_STAT_KEYS
            )
            for stat in stat_keys:
                present = (
                    bool(keyed_blocks(body, stat))
                    if stat == "resources"
                    else bool(direct_values(body, stat))
                )
                if not present:
                    fail(f"{name} must state {stat} explicitly after the relocation")


def validate_tank_rework() -> None:
    armor_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor.txt"), "technologies"))
    module_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor_modules.txt"), "technologies"))
    all_tank_techs = {**armor_techs, **module_techs}

    # Owner decision 2026-09-11 carrier role consolidation grants only each
    # family's explicit ten-role set under the engine's five-token constraint.
    expected_chassis_techs: dict[str, set[str]] = {}
    for family, tier_count in FAMILY_TIERS.items():
        for tier in range(tier_count):
            technology = (
                "nsb_iw_armored_vehicles"
                if tier == 0
                else f"nsb_{'main_battle_tanks' if family == 'medium' else family + '_tanks'}{tier - 1}"
            )
            expected_chassis_techs.setdefault(technology, set()).add(
                f"{family}_tank_chassis_{tier}"
            )
            expected_chassis_techs[technology].update(
                f"{family}_tank_{role}_chassis_{tier}"
                for role in FAMILY_ROLES[family]
            )
    for technology, expected in expected_chassis_techs.items():
        actual = {
            equipment
            for enable in top_level_named_blocks(all_tank_techs.get(technology, ""), "enable_equipments", technology)
            for equipment in listed_values(enable)
        }
        missing = expected - actual
        if missing:
            fail(f"{technology} is missing supported chassis grants: {sorted(missing)}")
    # A role family with no consuming sub-unit is designer output that cannot reach
    # the battlefield - the exact defect the 2026-09-13 brigade deletion introduced
    # for `heavy_tank_destroyer_chassis` and `medium_tank_aa_chassis` before it was
    # caught. Every declared role root must be named by some land sub-unit.
    consumers = ""
    for path in sorted((MOD / "common/units").glob("*.txt")):
        consumers += code_only(text(path))
    # The Heavy APC and Heavy IFV roles gained their battalions 2026-09-17
    # (`heavy_mechanized_infantry`, `heavy_armored_infantry`), so the exception this
    # check carried for `medium_tank_apc_chassis` and `medium_tank_ifv_chassis` is
    # gone and all twelve role families are guarded. See `STATUS.md` Finding 31.
    for family, roles in FAMILY_ROLES.items():
        for role in roles:
            root = f"{family}_tank_{role}_chassis"
            if not re.search(rf"(?<![A-Za-z0-9_]){root}(?![A-Za-z0-9_])", consumers):
                fail(f"role family {root} has no sub-unit consuming it")
    # A consumed role family also needs at least one plain member. Established
    # 2026-09-17 the hard way: `medium_tank_apc_chassis` and `medium_tank_ifv_chassis`
    # held only tiers derived by `duplicate_archetypes`, and their battalions never
    # appeared in the division designer even with `active = yes` and a researched
    # enabling technology. The engine logs nothing. Vanilla declares plain members for
    # every role family a sub-unit consumes - `medium_tank_aa_equipment_1..3` under
    # `medium_tank_aa_chassis` - and so does every mod role family that works. This
    # supersedes Finding 15's claim that a role root is nameable by `need` on its own.
    plain_members: dict[str, int] = {}
    for path in sorted((MOD / "common/units/equipment").glob("*.txt")):
        for _, block in top_level_blocks(code_only(text(path)), "equipments"):
            for parent in direct_values(block, "archetype"):
                plain_members[parent] = plain_members.get(parent, 0) + 1
    for family, roles in FAMILY_ROLES.items():
        for role in roles:
            root = f"{family}_tank_{role}_chassis"
            if not re.search(rf"(?<![A-Za-z0-9_]){root}(?![A-Za-z0-9_])", consumers):
                continue
            if not plain_members.get(root):
                fail(
                    f"role family {root} is consumed by a sub-unit but declares no plain "
                    f"member; only derived tiers cannot satisfy a `need`"
                )
    roles = text(TANK_ROLE_FILE)
    validate_legacy_armour_roles()
    role_blocks = dict(top_level_blocks(roles, "sub_units"))
    for battalion, role in TANK_ROLE_ARMOUR_BATTALIONS.items():
        block = role_blocks.get(battalion)
        if block is None:
            fail(f"tank role battalion is missing: {battalion}")
            continue
        if direct_values(block, "active") != ["yes"]:
            fail(f"{battalion} must remain active = yes")
    for battalion, (filename, role) in REWIRED_TANK_ROLE_BATTALIONS.items():
        blocks = dict(
            top_level_blocks(text(MOD / "common/units" / filename), "sub_units")
        )
        block = blocks.get(battalion)
        if block is None:
            fail(f"tank role battalion is missing: {battalion}")
            continue
        if direct_values(block, "active") != ["no"]:
            fail(f"{battalion} must remain active = no")
        # These battalions ARE the armour; they carry no `transport`, unlike the
        # infantry carriers. Only `need` and `essential` resolve their family.
        if direct_values(block, "transport"):
            fail(f"{battalion} must not declare transport")
        for key in ("need", "essential"):
            bodies = keyed_blocks(block, key)
            if not bodies and key == "essential":
                continue
            if len(bodies) != 1:
                fail(f"{battalion} must declare exactly one {key} block")
                continue
            if not re.search(
                rf"(?<![A-Za-z0-9_]){role}(?![A-Za-z0-9_])", bodies[0]
            ):
                fail(f"{battalion} {key} must name {role}")
    retired = re.compile(
        r"(?<![A-Za-z0-9_])(?:"
        + "|".join(re.escape(root) for root in LEGACY_ARMOUR_ROLE_RELOCATIONS)
        + r")(?![A-Za-z0-9_])"
    )
    for path in sorted((MOD / "common/units").glob("*.txt")):
        if retired.search(code_only(text(path))):
            fail(f"{path.name} still wires a land sub-unit to a retired armour family")

    definitions = {name: block for name, block in module_blocks if name != "limit"}
    for message in module_parent_errors(definitions):
        fail(message)

    chassis_text = text(CHASSIS_FILE)
    # The retired vanilla amphibious count-limit id stays rejected.
    for invalid in (
        "sloped_armor", "amphibious_drive", "wet_ammo_storage", "squeezebore_adaptor",
        "armor_skirts", "dozer_blade", "easy_maintenance", "auto_loader", "stabilizer",
        "tank_radio_module", "tank_mobility_fuel",
    ):
        if re.search(rf"module_count_limit\s*=\s*\{{[^}}]*\b(?:module|category)\s*=\s*{re.escape(invalid)}\b", chassis_text, re.DOTALL):
            fail(f"tank chassis retains removed count limit {invalid}")

    for message in abbreviation_errors(definitions):
        fail(message)

    for module, technology in SECONDARY_MODULES.items():
        if module not in definitions:
            fail(f"secondary turret module is missing: {module}")
        if module not in unlocked_modules:
            fail(f"secondary turret module is not unlocked: {module}")
        if technology not in all_tank_techs:
            fail(f"secondary turret unlock technology is missing: {technology}")
        if module not in english_loc_keys or f"{module}_desc" not in english_loc_keys:
            fail(f"secondary turret localization is incomplete: {module}")
        icon_match = re.search(
            rf'name\s*=\s*"GFX_SMI_{re.escape(module)}"[\s\S]*?textureFile\s*=\s*"([^"]+)"',
            text(TANK_ICON_FILE),
        )
        if not icon_match:
            fail(f"secondary turret icon declaration is missing: {module}")
        elif icon_match.group(1) != SECONDARY_ICON_PATHS[module] or not (MOD / icon_match.group(1)).is_file():
            fail(f"secondary turret icon path is invalid: {module}")
        category = module_category(module)
        if category != "tank_secondary_turret":
            fail(f"secondary module {module} has category {category}, expected tank_secondary_turret")
    for message in secondary_unlock_errors(unlocked_modules):
        fail(message)

    tank_archetypes = tank_archetype_blocks()
    validate_tank_type_domains(chassis_text, text(ROLE_CHASSIS_FILE))
    # Owner decision 2026-09-10 role-token remap covers carrier archetype type
    # sets as well as the chassis and duplicate-archetype role roots.
    for message in tank_type_domain_token_errors(tank_archetypes):
        fail(message)
    for archetype, block in tank_archetypes.items():
        slots = [
            slot
            for index in range(1, TANK_SPECIAL_SLOT_COUNT + 1)
            for slot in keyed_blocks(block, f"tank_special_slot_{index}")
        ]
        if len(slots) != TANK_SPECIAL_SLOT_COUNT:
            fail(f"{archetype} must declare all {TANK_SPECIAL_SLOT_COUNT} special slots")
        for message in tank_slot_layout_errors(block):
            fail(f"{archetype}: {message}")
        for message in tank_count_limit_errors(block):
            fail(f"{archetype}: {message}")
    for message in tank_category_contract_errors(definitions, tank_archetypes):
        fail(message)
    if re.search(r"\btank_mobility_auxiliary\b", text(MODULE_FILE)):
        fail("module file retains dissolved category tank_mobility_auxiliary")

    anti_air_expected = {
        "tank_anti_air_cannon": "18",
        "tank_anti_air_cannon_2": "32",
        "tank_anti_air_cannon_3": "46",
    }
    for module, expected in anti_air_expected.items():
        if not re.search(rf"{re.escape(module)}\s*=\s*\{{[\s\S]*?air_attack\s*=\s*{expected}\b", text(MODULE_FILE)):
            fail(f"{module} does not use the expected air attack value {expected}")
    turret_contract = {
        "pintle_turret": (0.5, 0.05, -0.1, 0.0),
        "light_lp_turret": (1.25, 0.10, 0.0, 0.05),
        "light_turret": (1.0, 0.15, 0.0, 0.0),
        "lp_turret": (1.5, 0.10, 0.0, 0.10),
        "conventional_turret": (1.5, 0.15, 0.05, 0.0),
        "oscillating_turret": (1.75, 0.05, 0.10, 0.0),
        "open_gun": (0.5, 0.10, -0.20, -0.10),
        "medium_open_gun": (0.75, 0.10, -0.20, -0.10),
        "heavy_open_gun": (1.0, 0.10, -0.20, -0.10),
        "external_gun": (1.25, 0.05, -0.05, 0.10),
        "fixed_superstructure": (0.75, 0.20, -0.15, 0.05),
        "medium_fixed_superstructure": (1.0, 0.20, -0.15, 0.05),
        "heavy_fixed_superstructure": (1.25, 0.20, -0.15, 0.05),
    }
    def stat_value(block: str, key: str) -> float:
        match = re.search(rf"(?m)^\s*{re.escape(key)}\s*=\s*(-?\d+(?:\.\d+)?)\b", block)
        return 0.0 if match is None else float(match.group(1))
    for module, expected in turret_contract.items():
        block = definitions.get(module, "")
        add_stats = next(iter(keyed_blocks(block, "add_stats")), "")
        multiply_stats = next(iter(keyed_blocks(block, "multiply_stats")), "")
        actual = (
            stat_value(add_stats, "build_cost_ic"),
            stat_value(add_stats, "reliability"),
            stat_value(multiply_stats, "breakthrough"),
            stat_value(multiply_stats, "defense"),
        )
        if actual != expected:
            fail(f"{module} turret stats differ from the reviewed contract: {actual} != {expected}")
    superheavy = definitions.get("tank_super_heavy_cannon", "")
    if module_category("tank_super_heavy_cannon") != "tank_heavy_main_armament":
        fail("tank_super_heavy_cannon must use the heavy main armament category")

    for owner in sorted(tank_self_loop_ids(all_tank_techs)):
        fail(f"tank technology {owner} retains an active self-loop")
    tank_edges = {
        owner: [target for path in top_level_named_blocks(block, "path", owner)
                for target in direct_values(path, "leads_to_tech")]
        for owner, block in all_tank_techs.items()
    }
    visit_state: dict[str, int] = {}
    def visit(node: str) -> None:
        if visit_state.get(node, 0) == 1:
            fail(f"tank technology path graph contains a cycle at {node}")
            return
        if visit_state.get(node, 0) == 2:
            return
        visit_state[node] = 1
        for target in tank_edges.get(node, []):
            if target in all_tank_techs:
                visit(target)
            elif target not in technology_set:
                fail(f"tank technology {node} points to undefined technology {target}")
        visit_state[node] = 2
    for owner in all_tank_techs:
        visit(owner)

    variable_values: dict[str, str] = {}
    for path in (TECH_DIR / "NSB_armor.txt", TECH_DIR / "NSB_armor_modules.txt"):
        variable_values.update(dict(re.findall(r"(?m)^\s*(@[0-9]+)\s*=\s*([^\s#]+)", text(path))))
    gridbox_roots = {
        "nsb_armor_folder": ("nsb_iw_armored_vehicles", "nsb_engines", "nsb_armor"),
        "nsb_armor_modules_folder": ("nsb_light_guns", "nsb_ammo", "nsb_tank_design"),
    }
    tree_owner: dict[str, str] = {}
    for folder_name, roots in gridbox_roots.items():
        for root in roots:
            if root not in all_tank_techs:
                fail(f"{folder_name} gridbox root {root} is not a tank technology")
                continue
            seen = {root}
            stack = [root]
            while stack:
                node = stack.pop()
                for target in tank_edges.get(node, []):
                    if target in all_tank_techs and target not in seen:
                        seen.add(target)
                        stack.append(target)
            for member in seen:
                tree_owner.setdefault(member, root)
    positions: dict[str, dict[tuple[str, str, str], str]] = {
        "nsb_armor_folder": {},
        "nsb_armor_modules_folder": {},
    }
    for owner, block in all_tank_techs.items():
        folders = top_level_named_blocks(block, "folder", owner)
        if len(folders) != 1:
            fail(f"tank technology {owner} must have one folder placement")
            continue
        folder = folders[0]
        folder_name = direct_values(folder, "name")
        position = re.search(r"position\s*=\s*\{\s*x\s*=\s*([^\s}]+)\s*y\s*=\s*([^\s}]+)", folder)
        if not folder_name or not position or folder_name[0] not in positions:
            continue
        cell = tuple(variable_values.get(value, value) for value in position.groups())
        coordinate = (tree_owner.get(owner, owner), *cell)
        previous = positions[folder_name[0]].get(coordinate)
        if previous:
            fail(
                f"duplicate tank technology coordinate {cell} in {folder_name[0]} "
                f"gridbox {coordinate[0]}_tree: {previous} and {owner}"
            )
        positions[folder_name[0]][coordinate] = owner
    expected_years = {
        # QA 2026-09-06: raw GUI rows had hidden 1940/1942 research dates.
        # Icon-year authority ratified 2026-09-09: where an icon year and its
        # technology's start_year disagreed, the icon year won and the technology
        # moved. The gas turbines were 1965/1975/1985/2005.
        "nsb_gt_engines0": ("1960", "@1960"),
        "nsb_gt_engines1": ("1970", "@1970"),
        "nsb_gt_engines2": ("1980", "@1980"),
        "nsb_gt_engines3": ("2000", "@2000"),
        "nsb_heavy_guns5": ("1985", "@1985"),
        "nsb_heavy_guns6": ("1995", "@1995"),
        "nsb_heavy_guns7": ("2010", "@2010"),
        "nsb_superheavy_guns1": ("1955", "@1955"),
        "nsb_heat_mp_ammo0": ("1985", "@1985"),
        "nsb_heat_mp_ammo1": ("1995", "@1995"),
        "nsb_heat_mp_ammo2": ("2005", "@2005"),
        "nsb_heat_du_ammo0": ("1985", "@1985"),
        "nsb_heat_du_ammo1": ("1995", "@1995"),
        "nsb_heat_du_ammo2": ("2005", "@2005"),
        "nsb_al_armor0": ("1955", "@1955"),
        "nsb_al_armor1": ("1965", "@1965"),
        "nsb_addon_armor0": ("1995", "@1995"),
        "nsb_addon_armor1": ("2005", "@2005"),
    }
    for owner, (year, y_position) in expected_years.items():
        block = all_tank_techs.get(owner, "")
        if direct_values(block, "start_year") != [year] or y_position not in block:
            fail(f"{owner} has the wrong start year or tree row")
    validate_tank_qa_contracts(all_tank_techs)

    role_ui = text(MOD / "interface/tank_designer_view.gui")
    if not re.search(r"name\s*=\s*\"dropdown_tank_roles\"[\s\S]*?size\s*=\s*\{\s*width\s*=\s*285\s+height\s*=\s*40", role_ui):
        fail("tank role selector dimensions changed")
    role_dropdowns = named_gui_blocks(role_ui, "dropDownBoxType", "dropdown_tank_roles", "tank_designer_view")
    role_windows = top_level_named_blocks(role_dropdowns[0], "expandedWindow", "dropdown_tank_roles") if role_dropdowns else []
    role_window = role_windows[0] if role_windows else ""
    if not role_window or "height=308" not in role_window or "verticalScrollbar = \"right_vertical_slider\"" not in role_window:
        fail("tank role selector lacks the bounded scrollable viewport")
    role_entry = next(iter(named_gui_blocks(role_ui, "containerWindowType", "tank_designer_role_entry", "tank_designer_view")), "")
    if "height = 50" not in role_entry:
        fail("tank role entries must remain 50 pixels high")
    research_ui = text(MOD / "interface/countrytechtreeview.gui")
    validate_tank_folder_gridboxes(all_tank_techs, variable_values, research_ui)
    if 'name = "techtree_armour_folder_small_item"' not in research_ui:
        fail("legacy armor tree is missing its small-node template")
    modules_tab = re.search(r'name\s*=\s*"nsb_armor_modules_folder_tab"[\s\S]*?quadTextureSprite\s*=\s*"([^"]+)"', research_ui)
    if not modules_tab or modules_tab.group(1) != "GFX_artillery_folder_tab":
        fail("NSB armor modules tab does not use the artillery folder sprite")
    # The 2026-09-09 amphibious-role ratification and 2026-09-10 owner ruling
    # remove these tank-role blueprints rather than retaining dormant files.
    removed_blueprints = removed_tank_blueprint_errors(
        [
            path.name
            for path in (MOD / "interface/equipmentdesigner/tanks").glob("*.gui")
        ]
    )
    if removed_blueprints:
        fail(f"removed tank designer GUI files remain: {removed_blueprints}")

    variant_text = text(FOCUS_EFFECT_FILE)
    variants = export_variant_map(variant_text)
    for block in keyed_blocks(variant_text, "create_equipment_variant"):
        name_match = re.search(r"(?m)^\s*name\s*=\s*\"([^\"]+)\"", block)
        if name_match and ("allow_without_tech = yes" not in block or "parent_version = 0" not in block):
            fail(f"export variant {name_match.group(1)} lacks the stable no-tech contract")
        if name_match and "obsolete = yes" not in block:
            fail(f"export variant {name_match.group(1)} must be archived in its producer's production list")
    if variants != EXPORT_VARIANTS:
        fail(f"export variant map differs from contract: {variants}")
    for helper in EXPORT_VARIANTS:
        flag = re.sub(r"[^A-Za-z0-9]+", "_", helper).lower().strip("_") + "_created"
        if "set_country_flag = " + flag not in variant_text:
            fail(f"export variant {helper} lacks its producer flag guard")
    validate_focus_armour_grants()
    focus_contracts = {
        "BRA_american_tanks": ("nsb_main_battle_tanks2", "medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
        "BRA_soviet_tanks": ("nsb_main_battle_tanks2", "medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
        "GRE_heavy_weapons_tanks_arty": ("nsb_main_battle_tanks1", "medium_tank_chassis_2", "CWIC Export Main Battle Tank 1944"),
        "FIN_Acquire_Soviet_T55s": ("nsb_main_battle_tanks2", "medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
    }
    focus_stockpiles = {
        "BRA_american_tanks": (
            ("medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
            ("light_tank_chassis_1", "CWIC Export Light Tank 1942"),
            ("heavy_tank_chassis_2", "CWIC Export Heavy Tank 1944"),
        ),
        "BRA_soviet_tanks": (
            ("medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
            ("light_tank_chassis_1", "CWIC Export Light Tank 1942"),
            ("heavy_tank_chassis_2", "CWIC Export Heavy Tank 1944"),
        ),
        "GRE_heavy_weapons_tanks_arty": (
            ("light_tank_chassis_2", "CWIC Export Light Tank 1944"),
            ("medium_tank_chassis_2", "CWIC Export Main Battle Tank 1944"),
        ),
        "FIN_Acquire_Soviet_T55s": (
            ("medium_tank_chassis_3", "CWIC Export Main Battle Tank 1950"),
        ),
    }
    for path in FOCUS_FILES:
        focus_blocks = named_focus_blocks(text(path))
        for focus, (technology, chassis, variant) in focus_contracts.items():
            if focus not in focus_blocks:
                continue
            block = focus_blocks[focus]
            reward = next((reward for reward in keyed_blocks(block, "completion_reward") if "add_equipment_to_stockpile" in reward), "")
            nsb_branches = top_level_named_blocks(reward, "if", focus)
            legacy_branches = top_level_named_blocks(reward, "else_if", focus)
            if len(nsb_branches) != 1 or len(legacy_branches) != 1:
                fail(f"{focus} must have sibling designer and legacy reward branches")
            else:
                nsb_limit = top_level_named_blocks(nsb_branches[0], "limit", focus)[0]
                legacy_limit = top_level_named_blocks(legacy_branches[0], "limit", focus)[0]
                if 'has_dlc = "No Step Back"' not in nsb_limit or 'NOT = { has_dlc = "No Step Back" }' not in legacy_limit:
                    fail(f"{focus} rewards lack mutually exclusive DLC conditions")
            if technology not in block or chassis not in block or variant not in block:
                fail(f"{focus} lacks its NSB technology, chassis, or export variant branch")
            stockpile_blocks = keyed_blocks(block, "add_equipment_to_stockpile")
            for equipment_type, variant_name in focus_stockpiles[focus]:
                selected = any(
                    re.search(rf"\btype\s*=\s*{re.escape(equipment_type)}\b", stockpile)
                    and re.search(rf'\bvariant_name\s*=\s*"{re.escape(variant_name)}"', stockpile)
                    for stockpile in stockpile_blocks
                )
                if not selected:
                    fail(f"{focus} NSB stockpile does not select {variant_name}")
            legacy_tech = {
                "BRA_american_tanks": "main_battle_tanks_3",
                "BRA_soviet_tanks": "main_battle_tanks_3",
                "GRE_heavy_weapons_tanks_arty": "main_battle_tanks_2",
                "FIN_Acquire_Soviet_T55s": "main_battle_tanks_3",
            }[focus]
            if legacy_tech not in block:
                fail(f"{focus} no longer retains its legacy branch")


def validate_tank_qa_contracts(tank_techs: dict[str, str]) -> None:
    validate_national_tank_presets()
    validate_national_armour_naming_presets()
    path = MOD / "common/scripted_effects/CWIC_tank_bookmark_research.txt"
    brace_balance(path)
    effect = text(path)
    grants = keyed_blocks(effect, "set_technology")
    expected_nsb = {
        name for name, block in tank_techs.items()
        if name != "nsb_superheavy_guns1"
        and direct_values(block, "start_year")
        and int(direct_values(block, "start_year")[0]) <= 1980
    }
    legacy = dict(top_level_blocks(text(TECH_DIR / "armor.txt"), "technologies"))
    expected_legacy = {
        name for name, block in legacy.items()
        if re.fullmatch(r"iw_armored_vehicles|main_battle_tanks(?:_\d+)?|light_tanks_\d+|heavy_tanks_\d+", name)
        and direct_values(block, "start_year")
        and int(direct_values(block, "start_year")[0]) <= 1980
    }
    if len(grants) != 2 or 'limit = { has_dlc = "No Step Back" }' not in effect:
        fail("1980 major tank research must have two DLC-separated grant blocks")
    else:
        for grant, expected in zip(grants, (expected_nsb, expected_legacy)):
            actual = set(re.findall(r"(?m)^\s*(\w+)\s*=\s*1\s*$", grant))
            if actual != expected:
                fail(f"1980 tank research coverage differs: {sorted(actual ^ expected)}")
    for filename in ("USA - United States.txt", "SOV - Soviet union.txt"):
        history = text(HISTORY_DIR / filename)
        calls = "cwic_major_tank_research_1980 = yes"
        if history.count(calls) != 1 or not any(calls in block for block in keyed_blocks(history, "1980.1.1")):
            fail(f"{filename} must apply its tank research once in 1980 history")

    focus = named_focus_blocks(text(MOD / "common/national_focus/50s_FIN.txt"))["FIN_Acquire_Soviet_T55s"]
    available = keyed_blocks(focus, "available")[0]
    for pattern in (
        r'AND\s*=\s*\{\s*NOT\s*=\s*\{\s*has_dlc\s*=\s*"No Step Back"\s*\}\s*SOV\s*=\s*\{\s*has_tech\s*=\s*main_battle_tanks_3',
        r'AND\s*=\s*\{\s*has_dlc\s*=\s*"No Step Back"\s*SOV\s*=\s*\{\s*has_tech\s*=\s*nsb_main_battle_tanks2',
    ):
        if not re.search(pattern, available):
            fail("Finnish tank focus availability must pair producer research with the DLC profile")
    limits = keyed_blocks(focus, "limit")
    if len(limits) != 2 or 'has_dlc = "No Step Back"' not in limits[0] or 'NOT = { has_dlc = "No Step Back" }' not in limits[1]:
        fail("Finnish tank focus rewards must select mutually exclusive DLC branches")
    for helper in top_level_blocks("effects = {\n" + text(FOCUS_EFFECT_FILE) + "\n}", "effects"):
        if not top_level_named_blocks(helper[1], "hidden_effect", helper[0]):
            fail(f"export setup helper {helper[0]} must hide internal variant creation")
    for (name, _chassis), recipe in _variant_recipes().items():
        for loadout in recipe["loadouts"]:
            for slot, module in loadout:
                match = re.fullmatch(r"tank_special_slot_(\d+)", slot)
                if match and module_category(module) not in TANK_SPECIAL_SLOT_CATEGORIES.get(int(match[1]), set()):
                    fail(f"{name} places {module} in incompatible {slot}")
    for recipe in keyed_blocks(text(AI_FILE), "target_variant"):
        for slot, value in re.findall(r"(?m)^\s*(tank_special_slot_\d+)\s*=\s*(\w+)\s*$", recipe):
            if value == "empty":
                continue
            index = int(slot.rsplit("_", 1)[1])
            category = value if value in module_categories else module_category(value)
            if category not in TANK_SPECIAL_SLOT_CATEGORIES.get(index, set()):
                fail(f"AI recipe places {value} in incompatible {slot}")


def naming_localisation_entry(key: str) -> tuple[str | None, str | None, int | None]:
    """First live English localisation entry for a legacy equipment name key.

    Deterministic order so provenance cannot drift with directory listing order.
    """
    for path in sorted((MOD / "localisation/english").glob("*.yml")):
        content = path.read_text(encoding="utf-8-sig", errors="replace")
        for number, line in enumerate(content.splitlines(), 1):
            match = re.match(r'\s*([A-Za-z0-9_]+):\d*\s*"([^"]*)"', line)
            if match and match.group(1) == key:
                return match.group(2), str(path.relative_to(ROOT)), number
    return None, None, None


def validate_national_armour_naming_presets() -> None:
    """Pin the historical-name guards for the bookmark tank/SPAA/SPG/TD designs.

    These exist to replace player-visible placeholders like "Standard Main Battle
    Tank 1950". Every name must still be the live country localisation string for
    the matching legacy tier, and every recipe must still equal the generic block
    it suppresses - that equality is what makes the rename balance-neutral.
    """
    manifest = json.loads(NAMING_MANIFEST_FILE.read_text(encoding="utf-8"))
    presets, recipes = manifest["presets"], {r["generation"]: r for r in manifest["recipes"]}
    national = code_only(text(NAMING_EFFECT_FILE))
    generic = code_only(text(VARIANT_EFFECT_FILE))
    national_effects = top_level_ranges("effects = {\n" + national + "\n}", "armour naming effects")
    pairs = {(p["producer"], p["generation"]) for p in presets}
    if len(pairs) != len(presets):
        fail("armour naming presets must not repeat a producer/generation pair")
    if {p["generation"] for p in presets} != set(recipes):
        fail("armour naming recipes and presets must cover the same generations")
        return
    dispatcher = top_level_named_blocks("effects = {\n" + generic + "\n}", "cwic_create_starting_tank_variants", "dispatcher")
    if len(dispatcher) != 1:
        fail("armour naming dispatcher must occur exactly once")
        return
    generic_blocks = {}
    for block in top_level_named_blocks(dispatcher[0], "if", "generic armour blocks"):
        variants = top_level_named_blocks(block, "create_equipment_variant", "generic variant")
        if len(variants) != 1:
            continue
        kinds = top_level_values(variants[0], "type")
        if len(kinds) == 1:
            generic_blocks.setdefault(kinds[0], []).append((block, variants[0]))
    for generation, recipe in sorted(recipes.items()):
        sources = generic_blocks.get(generation, [])
        if len(sources) != 1:
            fail(f"armour naming {generation} must shadow exactly one generic design")
            continue
        gblock, gvariant = sources[0]
        gmods = dict(re.findall(r"(\w+)\s*=\s*(\w+)", top_level_named_blocks(gvariant, "modules", "generic modules")[0]))
        if gmods != recipe["modules"]:
            fail(f"armour naming {generation} recipe differs from the generic design it replaces")
        glimits = top_level_named_blocks(gblock, "limit", "generic guard limit")
        if len(glimits) != 1 or top_level_values(glimits[0], "has_tech") != [recipe["technology"]]:
            fail(f"armour naming {generation} technology differs from the generic guard")
        helper = f"cwic_create_national_{generation}_variants"
        bodies = [body for name, _, _, body in national_effects if name == helper]
        if len(bodies) != 1:
            fail(f"armour naming helper {helper} must occur exactly once")
            continue
        guards = top_level_named_blocks(bodies[0], "if", helper)
        expected = [p for p in presets if p["generation"] == generation]
        if len(guards) != len(expected):
            fail(f"armour naming helper {helper} guard count differs from manifest")
        for preset in expected:
            raw, path, line = naming_localisation_entry(preset["legacy_name_key"])
            if (raw, path, line) != (preset["source_name"], preset["source_path"], preset["source_line"]):
                fail(f"armour naming {preset['producer']}/{generation} provenance differs from live localisation")
            elif unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode().strip() != preset["name"]:
                fail(f"armour naming {preset['producer']}/{generation} name differs from its localisation source")
            matches = [g for g in guards if top_level_values(top_level_named_blocks(g, "limit", "guard limit")[0], "tag") == [preset["producer"]]]
            if len(matches) != 1:
                fail(f"armour naming {preset['producer']}/{generation} must have exactly one guard")
                continue
            guard = matches[0]
            flag = f"cwic_starting_{generation}_created"
            variant = top_level_named_blocks(guard, "create_equipment_variant", "naming variant")[0]
            for required in ('has_dlc = "No Step Back"', f"has_tech = {recipe['technology']}",
                             f"NOT = {{ has_country_flag = {flag} }}"):
                if required not in guard:
                    fail(f"armour naming {preset['producer']}/{generation} missing guard: {required}")
            if top_level_values(guard, "set_country_flag") != [flag]:
                fail(f"armour naming {preset['producer']}/{generation} must set the generic block's flag")
            if guard.find("set_country_flag") < guard.find("create_equipment_variant"):
                fail(f"armour naming {preset['producer']}/{generation} sets its flag before creation")
            if re.findall(r'name\s*=\s*"([^"\n]*)"', variant) != [preset["name"]]:
                fail(f"armour naming {preset['producer']}/{generation} wrong name")
            for field, value in (("type", generation), ("allow_without_tech", "yes"),
                                 ("parent_version", "0"), ("mark_older_equipment_obsolete", "yes")):
                if top_level_values(variant, field) != [value]:
                    fail(f"armour naming {preset['producer']}/{generation} wrong {field}")
            mods = dict(re.findall(r"(\w+)\s*=\s*(\w+)", top_level_named_blocks(variant, "modules", "naming modules")[0]))
            if mods != recipe["modules"]:
                fail(f"armour naming {preset['producer']}/{generation} differs from the generic recipe")
    for generation in sorted(recipes):
        helper = f"cwic_create_national_{generation}_variants"
        if top_level_values(dispatcher[0], helper) != ["yes"]:
            fail(f"armour naming helper {helper} is not called by the bookmark dispatcher")
        elif dispatcher[0].find(helper) > dispatcher[0].find(f"cwic_starting_{generation}_created"):
            fail(f"armour naming helper {helper} runs after its own generic block")


def validate_national_tank_presets(national_override: str | None = None, generic_override: str | None = None) -> None:
    """Keep the named producer designs, bootstrap guards and manifest in sync."""
    brace_balance(NATIONAL_EFFECT_FILE)
    national = text(NATIONAL_EFFECT_FILE) if national_override is None else national_override
    generic = text(VARIANT_EFFECT_FILE) if generic_override is None else generic_override
    expected_pairs = {(tag, f"medium_tank_chassis_{tier}") for tag in ("USA", "SOV") for tier in range(7)}
    pairs = {(p["producer"], p["type"]) for p in NATIONAL_PRESETS}
    if len(NATIONAL_PRESETS) != 14 or pairs != expected_pairs:
        fail("national presets must cover exactly USA/SOV medium tiers 0-6")
    guards = keyed_blocks(keyed_blocks(national, "cwic_create_national_tank_variants")[0], "if")
    if len(guards) != len(NATIONAL_PRESETS):
        fail("national preset guard count differs from manifest")
    legacy_loc = text(MOD / "localisation/english/equipment_country_l_english.yml")
    for preset in NATIONAL_PRESETS:
        name, kind, tag = preset["name"], preset["type"], preset["producer"]
        matches = [g for g in guards if f'name = "{name}"' in g]
        if len(matches) != 1:
            fail(f"national preset {name} must occur exactly once")
            continue
        guard = matches[0]
        flag = f"cwic_starting_{kind}_created"
        for required in (f"tag = {tag}", f"has_tech = {preset['technology']}",
                         'has_dlc = "No Step Back"', f"NOT = {{ has_country_flag = {flag} }}",
                         f"set_country_flag = {flag}", f"type = {kind}",
                         "allow_without_tech = yes", "parent_version = 0",
                         "tank_engine_upgrade = 0", "tank_armor_upgrade = 0"):
            if required not in guard:
                fail(f"national preset {name} missing contract: {required}")
        blocks = keyed_blocks(guard, "modules")
        actual = re.findall(r"(?m)^\s*(\w+)\s*=\s*(\w+)\s*$", blocks[0]) if len(blocks) == 1 else []
        for message in variant_slot_errors(actual, preset["modules"]):
            fail(f"national preset {name} {message}")
        if not re.search(rf'(?m)^\s*{re.escape(preset["legacy_name_key"])}:\d*\s*"{re.escape(name)}"', legacy_loc):
            fail(f"national preset {name} differs from existing country equipment name")
    for guard in keyed_blocks(generic, "if"):
        types = re.findall(r"\btype\s*=\s*(\w+)", guard)
        if len(types) != 1:
            continue
        kind = types[0]
        # Carrier guards key their flag on the bookmark generation, not on the
        # equipment id, because two generations share a light hull tier after the
        # 2026-09-11 cutover. `validate_carrier_bookmarks.check_guard` pins those
        # flags, their idempotence and their ordering.
        if re.match(r"light_tank_(?:apc|ifv)_chassis_\d", kind):
            continue
        flag = f"cwic_starting_{kind}_created"
        if f"NOT = {{ has_country_flag = {flag} }}" not in guard or f"set_country_flag = {flag}" not in guard:
            fail(f"generic preset {kind} is not idempotent")
        if ("USA", kind) in pairs and "NOT = { OR = { tag = USA tag = SOV } }" not in guard:
            fail(f"generic preset {kind} must exclude national preset producers")
    if generic.find("cwic_create_national_tank_variants = yes") < 0 or generic.find("cwic_create_national_tank_variants = yes") > generic.find("create_equipment_variant ="):
        fail("national presets must bootstrap before generic presets")


# The reverse map and the legacy localisation key on the loc prefix `MBZ`, while the
# declared country tag is `MZB`. Comparing the two spaces without this mapping reports
# five delivered Mozambican carrier names as missing - an error made twice while
# measuring the conversion debt, so the alias lives in one place and is pinned.
CARRIER_SOURCE_TAG_ALIASES = {"MBZ": "MZB"}


# Legacy carrier level -> carrier generation, 2026-09-17. Two owner rulings widened
# this beyond the original arithmetic, and both are recorded as tables rather than
# offsets because the marine ladder is not evenly spaced.
#
# Levels 1 and 2 are CLAMPED onto tier 0 rather than dropped. The old rule was
# `apc tier = level - 3`, which sent the 1942 and 1944 half-tracks to negative tiers
# and silently discarded four countries' historical names. Clamping means levels 1,
# 2 and 3 share tier 0, so a country with names at several of them resolves by the
# ratified newest-wins rule.
#
# Marine equipment joins the pipeline. `mechanized_marine_equipment_*` was relocated
# into `light_tank_apc_chassis` by the 2026-09-12 carrier cutover and every APC is a
# marine transport, so by our own architecture these are carriers; only this regex
# disagreed. Its levels are not evenly spaced - 1944, 1950, 1965, 1985, 2005 - so the
# map is derived from those years against the APC generation ladder rather than from
# an offset.
MARINE_LEVEL_TIERS = {1: 0, 2: 1, 3: 3, 4: 5, 5: 7}


def carrier_source_inventory() -> dict[tuple[str, str], list[tuple[str, str, int, str]]]:
    """Inventory live legacy localisation independently of the authored manifest."""
    inventory: dict[tuple[str, str], list[tuple[str, str, int, str]]] = {}
    pattern = re.compile(
        r'^\s*(([A-Z]{3})_(mechanized(?:_heavy|_marine)?_equipment)_(\d+)):\d*\s*"([^"]*)"'
    )
    for path in sorted((MOD / "localisation/english").glob("*.yml")):
        for line_number, line in enumerate(text(path).splitlines(), 1):
            match = pattern.match(line)
            if not match:
                continue
            key, tag, legacy, level, name = match.groups()
            if "marine" in legacy:
                tier = MARINE_LEVEL_TIERS.get(int(level))
                if tier is None:
                    continue
                family = "apc"
            else:
                family = "ifv" if "heavy" in legacy else "apc"
                offset = 1 if family == "ifv" else 3
                tier = max(int(level) - offset, 0)
            if not 0 <= tier <= 7:
                continue
            tag = CARRIER_SOURCE_TAG_ALIASES.get(tag, tag)
            inventory.setdefault((tag, f"{family}_chassis_{tier}"), []).append(
                (key, str(path.relative_to(ROOT)), line_number, name)
            )
    return inventory


def validate_carrier_bookmarks(national_override: str | None = None,
                              generic_override: str | None = None,
                              manifest_override: dict | None = None,
                              oob_overrides: dict[str, str] | None = None,
                              history_overrides: dict[str, str] | None = None) -> None:
    """Pin source coverage, executable initialization order and migrated requests."""
    manifest = CARRIER_MANIFEST if manifest_override is None else manifest_override
    national = code_only(text(NATIONAL_EFFECT_FILE) if national_override is None else national_override)
    generic = code_only(text(VARIANT_EFFECT_FILE) if generic_override is None else generic_override)
    national_effects = top_level_ranges(
        "effects = {\n" + national + "\n}", "national carrier effects"
    )
    generic_effects = top_level_ranges(
        "effects = {\n" + generic + "\n}", "generic carrier effects"
    )
    recipes = manifest["recipes"]
    # Owner decision 2026-09-11: a carrier generation is a bookmark index, not an
    # equipment id. The scripted effect names, creation flags and hull
    # technologies still carry the legacy generation, while `type` names the
    # migrated role chassis. Two generations collapse onto one light hull tier -
    # APC 2 and 3 onto tier 4, IFV 1 and 2 onto tier 3 - and a bookmark chassis
    # may hold exactly one generic design, so the later generation of each pair
    # keeps its national presets and has no generic design of its own.
    wanted = {f"{family}_chassis_{tier}" for family in ("apc", "ifv") for tier in range(5)}
    generic_generations = wanted - {"apc_chassis_3", "ifv_chassis_2"}
    recipe_map = {r["generation"]: r for r in recipes}
    if len(recipes) != 10 or set(recipe_map) != wanted:
        fail("carrier recipes must cover exactly APC/IFV bookmark generations 0-4")
        return
    if {r["generation"] for r in recipes if r["has_generic_design"]} != generic_generations:
        fail("exactly the eight generations that own a light hull tier may carry a generic design")
        return
    presets = manifest["presets"]
    pairs = {(p["producer"], p["generation"]) for p in presets}
    inventory = carrier_source_inventory()
    expected_pairs = {pair for pair in inventory if pair[1] in wanted}
    # 572 -> 587 on 2026-09-17: the owner widened the source inventory to admit the
    # marine carrier family and to clamp legacy levels 1-2 onto tier 0 instead of
    # discarding them. The count stays pinned so a silent coverage change still fails.
    if len(presets) != 587 or len(pairs) != len(presets) or pairs != expected_pairs:
        fail("carrier national preset coverage must equal the 587 source-derived bookmark pairs without duplicates")
    if manifest.get("source_tag_aliases") != CARRIER_SOURCE_TAG_ALIASES:
        fail("carrier source tag alias must remain MBZ -> MZB")
    country_tags = set()
    for path in (MOD / "common/country_tags").glob("*.txt"):
        country_tags.update(re.findall(r'^\s*([A-Z]{3})\s*=', code_only(text(path)), re.MULTILINE))
    if {tag for tag, _ in pairs} - country_tags:
        fail("carrier national presets include an undefined producer tag")
    mandatory = set(REQUIRED_VARIANT_SLOTS)
    light_hull = dict(top_level_blocks(text(CHASSIS_FILE), "equipments")).get("light_tank_chassis", "")
    archetypes = {"apc": light_hull, "ifv": light_hull}
    mandatory_categories: dict[str, dict[str, set[str]]] = {}
    for family, archetype in archetypes.items():
        module_slots = top_level_named_blocks(archetype, "module_slots", f"{family} archetype")
        slot_categories: dict[str, set[str]] = {}
        if len(module_slots) == 1:
            for slot in mandatory:
                definitions = top_level_named_blocks(module_slots[0], slot, f"{family} module slots")
                allowed_blocks = (
                    top_level_named_blocks(definitions[0], "allowed_module_categories", f"{family} {slot}")
                    if len(definitions) == 1 else []
                )
                if len(allowed_blocks) == 1:
                    slot_categories[slot] = set(re.findall(r"\btank_[a-z_]+\b", allowed_blocks[0]))
        mandatory_categories[family] = slot_categories
    for kind, recipe in recipe_map.items():
        family, _, tier = kind.split("_")
        if recipe["technology"] != f"nsb_{family}_hulls{tier}":
            fail(f"carrier recipe {kind} has the wrong hull technology")
        slots = recipe["modules"]
        for message in variant_slot_errors(list(slots.items()), slots):
            fail(f"carrier recipe {kind} {message}")
        for slot, module in slots.items():
            if module == "empty" and slot not in mandatory:
                continue
            category = module_category(module)
            allowed = (mandatory_categories[family].get(slot, set()) if slot in mandatory else
                       TANK_SPECIAL_SLOT_CATEGORIES.get(int(slot.rsplit("_", 1)[1]), set()))
            if module not in module_ids or category not in allowed:
                fail(f"carrier recipe {kind} has illegal module {module} in {slot}")
        categories = {module_category(module) for module in slots.values()}
        if family == "ifv" and missing_ammunition_categories(categories):
            fail(f"carrier recipe {kind} lacks attack-producing AP/HE ammunition")
        if family == "apc" and slots.get("main_armament_slot") != "apc_firing_ports":
            fail(f"carrier recipe {kind} must retain the unarmed APC baseline")
    def quoted_top_level_values(block: str, key: str, label: str) -> list[str]:
        code = strip_script_comments(block)
        for _, start, ending, _ in reversed(top_level_ranges(code, label)):
            code = code[:start] + code[ending + 1:]
        opening = code.find("{")
        ending = balanced_end(code, opening, label)
        return re.findall(
            rf'(?<![A-Za-z0-9_]){re.escape(key)}\s*=\s*"([^"\n]*)"',
            code[opening + 1:ending],
        )


    def check_guard(guard: str, recipe: dict, name: str, producer: str | None) -> None:
        kind = recipe["generation"]
        flag = f"cwic_starting_{kind}_created"
        limits = top_level_named_blocks(guard, "limit")
        variants = top_level_named_blocks(guard, "create_equipment_variant")
        if len(limits) != 1 or len(variants) != 1:
            fail(f"carrier {producer}/{kind} needs one direct limit and variant")
            return
        limit, variant = limits[0], variants[0]
        for required in ('has_dlc = "No Step Back"', f"has_tech = {recipe['technology']}",
                         f"NOT = {{ has_country_flag = {flag} }}"):
            if required not in limit:
                fail(f"carrier {producer}/{kind} missing limit: {required}")
        if top_level_values(limit, "has_tech") != [recipe["technology"]]:
            fail(f"carrier {producer}/{kind} must use only its hull technology guard")
        if top_level_values(limit, "tag") != ([producer] if producer else []):
            fail(f"carrier {producer}/{kind} has wrong producer guard")
        if top_level_values(guard, "set_country_flag") != [flag]:
            fail(f"carrier {producer}/{kind} missing creation flag")
        if quoted_top_level_values(variant, "name", f"carrier {producer}/{kind} variant") != [name]:
            fail(f"carrier {producer}/{kind} wrong name")
        for field, expected in (("type", recipe["type"]), ("allow_without_tech", "yes"),
                                ("parent_version", "0"), ("mark_older_equipment_obsolete", "yes")):
            if top_level_values(variant, field) != [expected]:
                fail(f"carrier {producer}/{kind} wrong {field}")
        upgrades = top_level_named_blocks(variant, "upgrades")
        if len(upgrades) != 1 or dict(re.findall(r'(\w+)\s*=\s*(\w+)', upgrades[0])) != {"tank_engine_upgrade": "0", "tank_armor_upgrade": "0"}:
            fail(f"carrier {producer}/{kind} upgrades must be zero")
        modules = top_level_named_blocks(variant, "modules")
        values = re.findall(r'(\w+)\s*=\s*(\w+)', modules[0]) if len(modules) == 1 else []
        # Starting effects use the first petrol template; the manifest retains
        # the archetype's pre-WWII parent as its design-time default.
        for message in variant_slot_errors(values, recipe["modules"] | {"engine_type_slot": "Petrol_0"}):
            fail(f"carrier {producer}/{kind} {message}")
        if guard.find("set_country_flag") < guard.find("create_equipment_variant"):
            fail(f"carrier {producer}/{kind} sets its flag before creation")

    for kind in sorted(wanted):
        helper = f"cwic_create_national_{kind}_variants"
        bodies = [body for name, _, _, body in national_effects if name == helper]
        if len(bodies) != 1:
            fail(f"carrier helper {helper} must occur exactly once")
            continue
        guards = top_level_named_blocks(bodies[0], "if")
        expected = [p for p in presets if p["generation"] == kind]
        if len(guards) != len(expected):
            fail(f"carrier helper {helper} guard count differs from manifest")
        by_tag: dict[str, list[str]] = {}
        for guard in guards:
            limits = top_level_named_blocks(guard, "limit")
            tags = top_level_values(limits[0], "tag") if len(limits) == 1 else []
            by_tag.setdefault(tags[0] if len(tags) == 1 else "", []).append(guard)
        for preset in expected:
            pair = preset["producer"], kind
            sources = inventory.get(pair, [])
            # Detailed country files precede the consolidated fallback; duplicate
            # ALB/MBZ keys retain their first occurrence. No legacy loc is rewritten.
            # Newest legacy level names the generation, then detailed country files
            # ahead of the consolidated fallback. The level term was added 2026-09-17
            # with the clamp that folds legacy levels 1-2 onto tier 0: without it the
            # oldest vehicle in a pair wins, which downgraded 45 in-game designs - the
            # 1947 BTR-40 became a 1942 ZiS-42 truck. Verified to reproduce every
            # pre-existing name exactly while admitting the widened sources.
            selected = sorted(sources, key=lambda row: (-int(row[0].rsplit("_", 1)[1]), Path(row[1]).name == "equipment_country_l_english.yml", row[1], row[2]))
            if not selected:
                fail(f"carrier {pair} lacks live source provenance")
                continue
            source = selected[0]
            normalized = unicodedata.normalize("NFKD", source[3]).encode("ascii", "ignore").decode().strip()
            if (preset["legacy_name_key"], preset["source_path"], preset["source_line"], preset["source_name"]) != source or preset["name"] != normalized:
                fail(f"carrier {pair} name/provenance differs from selected live localisation")
            provenance = {(p["source_key"], p["source_path"], p["line"], p["raw_source_name"]) for p in preset["provenance"]}
            if provenance != set(sources):
                fail(f"carrier {pair} provenance omits or invents source entries")
            if preset["modules"] != recipe_map[kind]["modules"] or preset["technology"] != recipe_map[kind]["technology"]:
                fail(f"carrier {pair} preset differs from baseline recipe")
            matches = by_tag.get(pair[0], [])
            if len(matches) != 1:
                fail(f"carrier {pair} must have exactly one national guard")
            else:
                check_guard(matches[0], recipe_map[kind], preset["name"], pair[0])

    dispatchers = [body for name, _, _, body in generic_effects if name == "cwic_create_starting_tank_variants"]
    if len(dispatchers) != 1:
        fail("carrier bookmark dispatcher must occur exactly once")
        return
    dispatcher = dispatchers[0]
    children = top_level_ranges(dispatcher, "bookmark dispatcher")
    ordered_events = []
    for family in ("apc", "ifv"):
        for tier in range(8):
            kind = f"{family}_chassis_{tier}"
            helper = f"cwic_create_national_{kind}_variants"
            values = top_level_values(dispatcher, helper)
            positions = [
                match.start()
                for match in re.finditer(rf"\b{re.escape(helper)}\s*=", dispatcher)
                if not any(start <= match.start() <= ending for _, start, ending, _ in children)
            ]
            if values and (values != ["yes"] or len(positions) != 1):
                fail(f"carrier dispatcher must call {helper} with yes")
            ordered_events.extend((position, "national", kind) for position in positions)
    for key, start, _, body in children:
        if key == "if":
            variants = top_level_named_blocks(body, "create_equipment_variant")
            types = top_level_values(variants[0], "type") if len(variants) == 1 else []
            generic_for_type = {
                r["type"]: r["generation"] for r in recipes if r["has_generic_design"]
            }
            if types and types[0] in generic_for_type:
                kind = generic_for_type[types[0]]
                ordered_events.append((start, "generic", kind))
                check_guard(body, recipe_map[kind], recipe_map[kind]["generic_name"], None)
    events = [(mode, kind) for _, mode, kind in sorted(ordered_events)]
    expected_events = [
        event
        for family in ("apc", "ifv")
        for tier in range(5)
        for event in (("national", f"{family}_chassis_{tier}"), ("generic", f"{family}_chassis_{tier}"))
        if event[0] == "national" or event[1] in generic_generations
    ]
    if events != expected_events:
        fail("carrier dispatcher must interleave national then fallback per ascending tier, with each family contiguous")
    # Execute the validated event model for actual and synthetic partial national
    # coverage. Flags persist across calls; obsolescence affects only that family.
    # Coverage is asserted per chassis tier, not per generation: after the
    # 2026-09-11 cutover two generations share a tier, and the generation that
    # does not own the tier has no generic fallback of its own. A country with no
    # national preset for it still fields a design on that tier through the
    # owning generation, which is the property that actually matters in game.
    chassis_of = {generation: recipe["type"] for generation, recipe in recipe_map.items()}
    for coverage in [{kind for tag, kind in pairs if tag == producer} for producer in {tag for tag, _ in pairs}] + [set(), wanted, {"apc_chassis_4", "ifv_chassis_3"}]:
        flags: set[str] = set()
        created: list[str] = []
        active: dict[str, str] = {}
        def simulate(unlocked: set[str]) -> None:
            for mode, kind in events:
                if kind not in unlocked or kind in flags or (mode == "national" and kind not in coverage):
                    continue
                flags.add(kind)
                created.append(kind)
                active[kind.split("_")[0]] = chassis_of[kind]
        first = {kind for kind in wanted if int(kind[-1]) < 4}
        simulate(first)
        before = list(created)
        simulate(first)
        if before != created:
            fail("carrier initialization must be idempotent under partial national coverage")
        if {chassis_of[kind] for kind in created} != {chassis_of[kind] for kind in first}:
            fail("carrier initialization must cover every unlocked carrier chassis tier")
        simulate(wanted)
        if active != {family: chassis_of[f"{family}_chassis_4"] for family in ("apc", "ifv")}:
            fail("carrier initialization must preserve newest-only visibility after new hull unlocks")

    actual_requests = Counter()
    for path in sorted(OOB_DIR.glob("*_nsb.txt")):
        relative = str(path.relative_to(ROOT))
        value = code_only((oob_overrides or {}).get(relative, text(path)))
        if re.search(r'\b(?:mechanized_equipment_(?:[3-9]|10)|mechanized_heavy_equipment_\d+|heavy_mechanized_equipment_\d+)\b', value):
            fail(f"{path.name} retains postwar legacy or misspelled carrier equipment")
        # Early production queues wrap the selected design in equipment = { };
        # later bookmarks use direct stockpile/production effects.
        for key in ("add_equipment_to_stockpile", "add_equipment_production", "equipment"):
            for block in keyed_blocks(value, key):
                kinds = top_level_values(block, "type")
                if kinds and re.fullmatch(r'light_tank_(?:apc|ifv)_chassis_\d+', kinds[0]):
                    name = quoted_top_level_values(
                        block, "variant_name" if key.endswith("stockpile") else "version_name",
                        f"{relative} {key}",
                    )
                    actual_requests[(relative, kinds[0], oob_variant_producer(block, path.stem[:3]), name[0] if len(name) == 1 else "")] += 1
        for block in keyed_blocks(value, "force_equipment_variants"):
            for kind, _, _, request in top_level_ranges(block, "carrier forced requests"):
                if re.fullmatch(r'light_tank_(?:apc|ifv)_chassis_\d+', kind):
                    names = quoted_top_level_values(request, "version_name", f"{relative} {kind}")
                    actual_requests[(relative, kind, oob_variant_producer(request, path.stem[:3]), names[0] if len(names) == 1 else "")] += 1
    expected_requests = Counter((r["file"], r["chassis"], r["resolved_producer"], r["resolved_variant_name"]) for r in manifest["oob_migration"])
    if sum(expected_requests.values()) != 100 or actual_requests != expected_requests:
        fail("carrier OOB migration must preserve the manifest's 100 producer/chassis/name requests")
    for row in manifest["oob_migration"]:
        if row["resolved_variant_name"] not in bookmark_variant_names(row["chassis"], row["resolved_producer"]):
            fail("carrier OOB manifest requests a name the resolved producer does not create")
    for path in sorted(HISTORY_DIR.glob("*.txt")):
        tag = path.name[:3]
        if tag not in MANUFACTURER_BLOC_TAGS:
            continue
        value = code_only((history_overrides or {}).get(str(path.relative_to(ROOT)), text(path)))
        required = set().union(*(techs for (producer, _), techs in foreign_producer_techs.items() if producer == tag))
        candidates = [body for body in keyed_blocks(value, "if") if STARTING_VARIANT_EFFECT in body and 'has_dlc = "No Step Back"' in body]
        if not any(required <= set(re.findall(r'\b(nsb_\w+)\s*=\s*1\b', body[:body.find(STARTING_VARIANT_EFFECT)])) for body in candidates):
            fail(f"{tag} manufacturer must grant every requested foreign chassis technology before NSB variant creation")


def tank_archetype_blocks() -> dict[str, str]:
    """The three designer archetypes.

    Owner decision 2026-09-11 retired the carrier designer families, so
    mechanized_equipment and mechanized_heavy_equipment are plain equipment and
    carry no designer slots. `validate_carrier_roles` owns their contract now.
    """
    chassis_blocks = dict(top_level_blocks(text(CHASSIS_FILE), "equipments"))
    return {
        archetype: chassis_blocks.get(archetype, "")
        for archetype in ("light_tank_chassis", "medium_tank_chassis", "heavy_tank_chassis")
    }


def tank_slot_layout_errors(block: str) -> list[str]:
    errors = []
    for index, expected in TANK_SPECIAL_SLOT_CATEGORIES.items():
        slots = keyed_blocks(block, f"tank_special_slot_{index}")
        if len(slots) != 1:
            errors.append(f"slot {index} must occur exactly once")
            continue
        if not re.search(r"\brequired\s*=\s*no\b", slots[0]):
            errors.append(f"slot {index} must stay optional")
        categories = keyed_blocks(slots[0], "allowed_module_categories")
        actual = set(re.findall(r"\btank_[a-z_]+\b", " ".join(categories)))
        if actual != expected:
            errors.append(f"slot {index} category mismatch: {sorted(actual ^ expected)}")
    declared = {int(value) for value in re.findall(r"\btank_special_slot_(\d+)\s*=", block)}
    for index in sorted(declared - set(TANK_SPECIAL_SLOT_CATEGORIES)):
        errors.append(f"slot {index} is outside the declared 1-{TANK_SPECIAL_SLOT_COUNT} set")
    return errors


def tank_category_contract_errors(
    definitions: dict[str, str], archetypes: dict[str, str]
) -> list[str]:
    errors = []
    for module, expected in TANK_RECUT_MODULE_CATEGORIES.items():
        definition = definitions.get(module, "")
        match = re.search(r"^\s*category\s*=\s*([A-Za-z0-9_]+)", definition, re.MULTILINE)
        actual = match.group(1) if match else ""
        if actual != expected:
            errors.append(f"{module} must use category {expected}, found {actual or 'none'}")
    module_categories = {
        match.group(1)
        for definition in definitions.values()
        if (match := re.search(r"^\s*category\s*=\s*([A-Za-z0-9_]+)", definition, re.MULTILINE))
    }
    slot_owners: dict[str, set[str]] = {}
    archetype_categories: dict[str, set[str]] = {}
    declared_slots = REQUIRED_VARIANT_SLOTS | {
        f"tank_special_slot_{index}" for index in range(1, TANK_SPECIAL_SLOT_COUNT + 1)
    }
    for archetype, block in archetypes.items():
        archetype_categories[archetype] = set()
        if re.search(r"\btank_mobility_auxiliary\b", block):
            errors.append(f"{archetype} retains dissolved category tank_mobility_auxiliary")
        for slot in declared_slots:
            for slot_block in keyed_blocks(block, slot):
                categories = set(
                    re.findall(
                        r"\btank_[a-z_]+\b",
                        " ".join(keyed_blocks(slot_block, "allowed_module_categories")),
                    )
                )
                archetype_categories[archetype].update(categories)
                for category in categories:
                    slot_owners.setdefault(category, set()).add(slot)
    # Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
    # remains deliberately unspent and reserved for a future dedicated amphibious
    # mechanized role.
    carrier_categories = {
        "tank_apc_superstructure",
        "tank_apc_armament",
        "tank_ifv_superstructure",
        "tank_ifv_armament",
    }
    for archetype in ("light_tank_chassis", "medium_tank_chassis"):
        missing = sorted(carrier_categories - archetype_categories.get(archetype, set()))
        if missing:
            errors.append(
                f"{archetype} must retain all carrier loadout categories, missing {missing}"
            )
    for category in sorted(module_categories):
        owners = slot_owners.get(category, set())
        if len(owners) != 1:
            errors.append(
                f"module category {category} must be reachable from exactly one "
                f"special or mandatory slot, found {sorted(owners)}"
            )
    # Owner QA 2026-09-10: a slot category with no title key rendered an
    # undefined label and spammed `bitmapfont.cpp: Couldnt find texticon:
    # _texticon`, and one with no GFX_EMI sprite rendered a broken texture.
    # Four carrier categories and tank_suspension_multi_track shipped without
    # either, and nothing static caught it because both are presentation.
    category_loc = text(MOD / "localisation/english/tank_modules_l_english.yml")
    category_gfx = text(MOD / "interface/equipmentdesignermoduleicons.gfx") + text(
        MOD / "interface/cwic_tank_rework_icons.gfx"
    )
    for category in sorted(slot_owners):
        if f"EQ_MOD_CAT_{category}_TITLE" not in category_loc:
            errors.append(f"slot category {category} has no EQ_MOD_CAT title key")
        sprite = f'name = "GFX_EMI_{category}"'
        if sprite not in category_gfx:
            errors.append(f"slot category {category} has no GFX_EMI sprite")
    return errors


def tank_count_limit_errors(block: str) -> list[str]:
    """Every limited special category retains one `count < 2` budget.

    The 2026-09-10 fully specialized slot map prevents cross-purpose mounting;
    these limits retain the category-level one-module invariant.
    """
    errors = []
    limits = re.findall(r"module_count_limit\s*=\s*\{([^{}]*)\}", block, re.DOTALL)
    seen: dict[str, int] = {}
    for limit in limits:
        categories = re.findall(r"\bcategory\s*=\s*(\w+)", limit)
        if len(categories) != 1:
            errors.append(f"count limit must name exactly one category, found {categories}")
            continue
        if not re.search(r"\bcount\s*<\s*2\b", limit):
            errors.append(f"count limit for {categories[0]} is not `count < 2`")
        seen[categories[0]] = seen.get(categories[0], 0) + 1
    for category in TANK_LIMITED_CATEGORIES:
        if seen.get(category) != 1:
            errors.append(f"needs exactly one `count < 2` limit for {category}, found {seen.get(category, 0)}")
    for category in sorted(set(seen) - set(TANK_LIMITED_CATEGORIES)):
        errors.append(f"has an unexpected count limit for {category}")
    return errors


def variant_slot_errors(assignments: list[tuple[str, str]], expected: dict[str, str]) -> list[str]:
    """Mandatory slots complete, optional specials a declared subset.

    Cardinality is deliberately not a contract: vanilla
    `history/countries/GER - Germany.txt` omits unused optional slots from a
    creation block, so an omitted optional special is identical to an empty one.
    """
    errors = []
    actual = dict(assignments)
    if len(actual) != len(assignments):
        errors.append("repeats a slot assignment")
    missing = REQUIRED_VARIANT_SLOTS - set(actual)
    if missing:
        errors.append(f"omits mandatory slots {sorted(missing)}")
    for slot in sorted(set(actual) - REQUIRED_VARIANT_SLOTS):
        match = re.fullmatch(r"tank_special_slot_(\d+)", slot)
        if not match or not 1 <= int(match[1]) <= TANK_SPECIAL_SLOT_COUNT:
            errors.append(f"assigns undeclared slot {slot}")
    for slot, module in sorted(expected.items()):
        current = actual.get(slot, None if slot in REQUIRED_VARIANT_SLOTS else "empty")
        if current != module:
            errors.append(f"has {current} in {slot} where the manifest wants {module}")
    for slot, module in sorted(actual.items()):
        if slot not in expected and slot not in REQUIRED_VARIANT_SLOTS and module != "empty":
            errors.append(f"mounts unmanifested {module} in {slot}")
    return errors


def tank_designer_position_errors(gui_text: str) -> list[str]:
    positions = {
        int(value)
        for value in re.findall(r'pos_custom_module_slot_window_(\d+)"', gui_text)
    }
    if positions == set(range(TANK_DESIGNER_POSITIONS)):
        return []
    return [
        f"tank designer slot positions must be exactly 0-{TANK_DESIGNER_POSITIONS - 1}, "
        f"found {sorted(positions)}"
    ]


def run_tank_negative_fixtures() -> None:
    """Exercise the tank contract's failure shapes without touching files."""
    armor_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor.txt"), "technologies"))
    module_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor_modules.txt"), "technologies"))
    all_tank_techs = {**armor_techs, **module_techs}
    variable_values: dict[str, str] = {}
    for path in (TECH_DIR / "NSB_armor.txt", TECH_DIR / "NSB_armor_modules.txt"):
        variable_values.update(dict(re.findall(r"(?m)^\s*(@[0-9]+)\s*=\s*([^\s#]+)", text(path))))
    research_ui = text(MOD / "interface/countrytechtreeview.gui")
    mutated_ui = research_ui.replace("nsb_tank_design_tree", "nsb_tank_design_tree_renamed", 1)
    if mutated_ui == research_ui:
        raise AssertionError("GUI gridbox fixture did not mutate the tank design gridbox")
    previous_errors = len(errors)
    try:
        validate_tank_folder_gridboxes(all_tank_techs, variable_values, mutated_ui)
        probe_messages = errors[previous_errors:]
    finally:
        del errors[previous_errors:]
    if not any("gridbox" in message for message in probe_messages):
        raise AssertionError("GUI gridbox contract accepted an unmapped tank design gridbox")
    # Engine cap verified 2026-09-10: custom module slot window index 20 is silently dropped.
    twenty_first_gui_position_fixture = (
        text(MOD / "interface/tank_designer_view.gui")
        + '\nname = "pos_custom_module_slot_window_20"\n'
    )
    previous_errors = len(errors)
    try:
        for message in tank_designer_position_errors(twenty_first_gui_position_fixture):
            fail(message)
        rejected_twenty_first_position = len(errors) > previous_errors
    finally:
        del errors[previous_errors:]
    if not rejected_twenty_first_position:
        raise AssertionError("tank designer GUI accepted a twenty-first slot position")
    chassis_text = text(CHASSIS_FILE)
    mutated_chassis = chassis_text.replace(
        "\t\ttype = { armor light_armor }\n",
        "\t\ttype = armor\n",
        1,
    )
    if mutated_chassis == chassis_text:
        raise AssertionError("light armor type-domain fixture did not mutate the archetype")
    previous_errors = len(errors)
    try:
        validate_tank_type_domains(mutated_chassis, text(ROLE_CHASSIS_FILE))
        probe_messages = errors[previous_errors:]
    finally:
        del errors[previous_errors:]
    if not any(
        "light_tank_chassis" in message
        and "{armor, light_armor}" in message
        for message in probe_messages
    ):
        raise AssertionError("light armor type-domain contract accepted a bare light archetype")
    for module, metric, expected in (("Radar_1", "fuel_consumption", 1.2), ("gl_atgm_2p", "hard_attack", 95)):
        adds, _, unknown = _effective_module_operations(module)
        if unknown or adds.get(metric) != expected:
            raise AssertionError(f"upgrade parent stats stacked for {module}")
    if bookmark_variant_name("medium_tank_chassis_3", "SOV") != "T-55":
        raise AssertionError("Soviet named preset lookup failed")
    # A producer with no preset on the chassis must fall back to the generic bookmark
    # name. The tag is measured rather than hardcoded: the 2026-09-14 naming presets gave
    # FIN a T-54B on this chassis, which silently turned a hardcoded FIN here into a
    # baseline failure with no content defect behind it.
    every_preset = NATIONAL_PRESETS + CARRIER_PRESETS + NAMING_PRESETS
    mapped = {p["producer"] for p in every_preset if p["type"] == "medium_tank_chassis_3"}
    unmapped = sorted({p["producer"] for p in every_preset} - mapped)
    if not unmapped:
        raise AssertionError("every producer now presets medium_tank_chassis_3")
    if bookmark_variant_name("medium_tank_chassis_3", unmapped[0]) != BOOKMARK_VARIANT_NAMES["medium_tank_chassis_3"]:
        raise AssertionError("national preset leaked into another producer")

    national = text(NATIONAL_EFFECT_FILE)
    generic = text(VARIANT_EFFECT_FILE)
    for label, mutated_national, mutated_generic in (
        ("wrong producer", national.replace("tag = USA", "tag = FIN", 1), generic),
        ("stale slot", national.replace("tank_special_slot_1 =", "special_type_slot_1 =", 1), generic),
        ("missing guard", national.replace("NOT = { has_country_flag", "NOT = { wrong_flag", 1), generic),
        ("duplicate generic", national, generic.replace("NOT = { OR = { tag = USA tag = SOV } }", "", 1)),
    ):
        previous_errors = len(errors)
        validate_national_tank_presets(mutated_national, mutated_generic)
        rejected_mutation = len(errors) > previous_errors
        del errors[previous_errors:]
        if not rejected_mutation:
            raise AssertionError(f"national preset mutation accepted: {label}")
    slots = "\n".join(
        f"tank_special_slot_{i} = {{ required = no allowed_module_categories = {{ {' '.join(sorted(categories))} }} }}"
        for i, categories in TANK_SPECIAL_SLOT_CATEGORIES.items()
    )
    if tank_slot_layout_errors(slots):
        raise AssertionError("valid specialized slot layout rejected")
    if not tank_slot_layout_errors(slots.replace("tank_fcs_aiming", "tank_fcs_radar")):
        raise AssertionError("radar accepted in aiming slot")
    if not tank_slot_layout_errors(slots.replace("tank_protection_active", "")):
        raise AssertionError("unreachable active protection was accepted")
    if not tank_slot_layout_errors(slots.replace(f"tank_special_slot_{TANK_SPECIAL_SLOT_COUNT} =", "unused =", 1)):
        raise AssertionError("a layout missing the last special slot was accepted")
    if not tank_slot_layout_errors(
        slots + f"\ntank_special_slot_{TANK_SPECIAL_SLOT_COUNT + 1} = "
        "{ allowed_module_categories = { tank_smoke } }"
    ):
        raise AssertionError("a slot beyond the declared set was accepted")
    restored_twelve_category_free_list_fixture = slots.replace(
        "tank_fcs_computer tank_fcs_radar",
        (
            "tank_fcs_computer tank_fcs_radar tank_loader_artillery "
            "tank_loader_autoloader tank_loader_manual_assist tank_mobility_auxiliary "
            "tank_protection_active tank_protection_passive tank_protection_reactive "
            "tank_secondary_turret tank_smoke tank_survivability"
        ),
        1,
    )
    if not tank_slot_layout_errors(restored_twelve_category_free_list_fixture):
        raise AssertionError("restored twelve-category free special slot was accepted")
    limits = "\n".join(
        f"module_count_limit = {{ category = {category} count < 2 }}"
        for category in TANK_LIMITED_CATEGORIES
    )
    if tank_count_limit_errors(limits):
        raise AssertionError("the per-category count limit fallback was rejected")
    if not tank_count_limit_errors(
        limits.replace("module_count_limit = { category = tank_loader_autoloader count < 2 }\n", "", 1)
    ):
        raise AssertionError("a missing loading-system limit was accepted")
    if not tank_count_limit_errors(
        limits.replace(
            "module_count_limit = { category = tank_fcs_radar count < 2 }",
            "module_count_limit = { category = tank_fcs_computer category = tank_fcs_radar count < 2 }",
            1,
        )
    ):
        raise AssertionError("a multi-category count limit was accepted")
    deleted_mobility_category_module_fixture = dict(module_definitions)
    deleted_mobility_category_module_fixture["APU_0"] = deleted_mobility_category_module_fixture["APU_0"].replace(
        "category = tank_power_auxiliary",
        "category = tank_mobility_auxiliary",
        1,
    )
    previous_errors = len(errors)
    try:
        for message in tank_category_contract_errors(
            deleted_mobility_category_module_fixture, tank_archetype_blocks()
        ):
            fail(message)
        rejected_mobility_category = len(errors) > previous_errors
    finally:
        del errors[previous_errors:]
    if not rejected_mobility_category:
        raise AssertionError("module left in tank_mobility_auxiliary was accepted")
    mandatory_pairs = [(slot, "baseline") for slot in sorted(REQUIRED_VARIANT_SLOTS)]
    manifest_modules = dict(mandatory_pairs)
    if variant_slot_errors(mandatory_pairs, manifest_modules):
        raise AssertionError("a creation block that omits every optional special slot was rejected")
    if variant_slot_errors(mandatory_pairs + [(f"tank_special_slot_{TANK_SPECIAL_SLOT_COUNT}", "empty")], manifest_modules):
        raise AssertionError("an explicitly empty optional special slot was rejected")
    if not variant_slot_errors(mandatory_pairs[1:], manifest_modules):
        raise AssertionError("a creation block missing a mandatory slot was accepted")
    if not variant_slot_errors(
        mandatory_pairs + [(f"tank_special_slot_{TANK_SPECIAL_SLOT_COUNT + 1}", "Smoke_1")],
        manifest_modules,
    ):
        raise AssertionError("a creation block assigning an undeclared slot was accepted")
    if not variant_slot_errors(mandatory_pairs + [("tank_special_slot_6", "Smoke_1")], manifest_modules):
        raise AssertionError("a creation block mounting an unmanifested module was accepted")
    parser_fixture = 'root = { child = { label = "quoted { brace }" } # ignored { }\n }'
    parsed = top_level_named_blocks(parser_fixture, "child", "fixture")
    if len(parsed) != 1 or 'label = "quoted { brace }"' not in parsed[0]:
        raise AssertionError("bounded parser failed quoted-brace/comment fixture")

    def rejected(condition: bool, label: str) -> None:
        if not condition:
            raise AssertionError(f"tank negative fixture was accepted: {label}")
    focus_path = NATIONAL_FOCUS_DIR / "1950s_Afghanistan.txt"
    focus_source = text(focus_path)
    helper_position = focus_source.find("cwic_create_export_main_battle_tank_1950")
    limit_position = focus_source.rfind('has_dlc = "No Step Back"', 0, helper_position)
    malformed_focus = (
        focus_source[:limit_position]
        + focus_source[limit_position:].replace('has_dlc = "No Step Back"', 'has_dlc = "Other DLC"', 1)
    )
    previous_errors = len(errors)
    validate_focus_armour_grants({str(focus_path.relative_to(ROOT)): malformed_focus})
    rejected_malformed_focus = len(errors) > previous_errors
    del errors[previous_errors:]
    if not rejected_malformed_focus:
        raise AssertionError("focus armour grant contract accepted a missing NSB gate")

    armor_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor.txt"), "technologies"))
    module_techs = dict(top_level_blocks(text(TECH_DIR / "NSB_armor_modules.txt"), "technologies"))
    all_tank_techs = {**armor_techs, **module_techs}

    reintroduced_flame_role_fixture = dict(
        top_level_blocks(text(ROLE_CHASSIS_FILE), "duplicate_archetypes")
    )
    reintroduced_flame_role_fixture["light_tank_flame_chassis"] = (
        "light_tank_flame_chassis = { archetype = light_tank_chassis }"
    )
    # The IFV role is restored 2026-09-11 on `rocket`, so there is no IFV
    # retirement fixture. What still holds is that an unexpected role root is
    # rejected - covered by the `unexpected tank role roots remain` contract.
    rejected(
        bool(removed_tank_role_errors(reintroduced_flame_role_fixture)),
        "reintroduced flame role root",
    )
    reintroduced_heavy_aa_role_fixture = dict(
        top_level_blocks(text(ROLE_CHASSIS_FILE), "duplicate_archetypes")
    )
    reintroduced_heavy_aa_role_fixture["heavy_tank_aa_chassis"] = (
        "heavy_tank_aa_chassis = { archetype = heavy_tank_chassis }"
    )
    # Owner decision 2026-09-10 phase 3 restructure retires heavy SPAAG.
    rejected(
        bool(removed_tank_role_errors(reintroduced_heavy_aa_role_fixture)),
        "reintroduced heavy tank AA role root",
    )
    # Owner decision 2026-09-11 carrier role consolidation preserves the
    # no-size-token rule on each surviving role root under the five-token engine.
    role_size_token_text = text(ROLE_CHASSIS_FILE).replace(
        "type = { armor anti_air }",
        "type = { armor anti_air light_armor }",
        1,
    )
    if role_size_token_text == text(ROLE_CHASSIS_FILE):
        raise AssertionError("role size-token fixture did not mutate the role root")
    previous_errors = len(errors)
    try:
        validate_tank_type_domains(text(CHASSIS_FILE), role_size_token_text)
        rejected_role_size_token = len(errors) > previous_errors
    finally:
        del errors[previous_errors:]
    rejected(rejected_role_size_token, "role root with a size token")

    # Shipped 2026-09-13: APC uses `flame`, IFV uses `rocket`, and `amphibious`
    # remains deliberately unspent and reserved for a future dedicated amphibious
    # mechanized role.
    carrier_armament_fixture = dict(module_definitions)
    carrier_armament_fixture[APC_ARMAMENT_MODULES[0]] = carrier_armament_fixture[
        APC_ARMAMENT_MODULES[0]
    ].replace("heavy_armor", "", 1)
    if carrier_armament_fixture[APC_ARMAMENT_MODULES[0]] == module_definitions[
        APC_ARMAMENT_MODULES[0]
    ]:
        raise AssertionError("carrier armament forbid fixture did not mutate the module")
    rejected(
        bool(tank_module_type_bound_errors(carrier_armament_fixture)),
        "carrier armament missing a size-token forbid",
    )

    # This in-memory negative fixture retargets the surviving APC `flame` bound.
    carrier_role_module_fixture = dict(module_definitions)
    fixture_module = APC_ARMAMENT_MODULES[0]
    carrier_role_module_fixture[fixture_module] = carrier_role_module_fixture[
        fixture_module
    ].replace("allow_equipment_type = flame", "allow_equipment_type = anti_air", 1)
    if carrier_role_module_fixture[fixture_module] == module_definitions[fixture_module]:
        raise AssertionError("carrier role eligibility fixture did not mutate the module")
    rejected(
        bool(tank_module_type_bound_errors(carrier_role_module_fixture)),
        "carrier module gated on the wrong surviving role",
    )

    # Owner decision 2026-09-10 phase 3 restructure permanently rejects the
    # engine's obsolete exact-match eligibility key.
    exact_match_module_fixture = dict(module_definitions)
    exact_match_module_fixture["tank_light_cannon0"] = (
        exact_match_module_fixture["tank_light_cannon0"].rsplit("}", 1)[0]
        + "\tforbid_equipment_type_exact_match = armor\n}"
    )
    rejected(
        bool(tank_module_type_bound_errors(exact_match_module_fixture)),
        "module using forbid_equipment_type_exact_match",
    )



    invalid_parent = {name: block for name, block in module_definitions.items() if name != "limit"}
    invalid_parent["fixture_invalid_parent"] = "fixture_invalid_parent = { parent = missing_parent }"
    rejected(bool(module_parent_errors(invalid_parent)), "invalid module parent")

    missing_secondary = unlocked_modules - {"cwic_secondary_autocannon"}
    rejected(bool(secondary_unlock_errors(missing_secondary)), "missing secondary unlock")

    abbreviation_fixture = {name: block for name, block in module_definitions.items() if name != "limit"}
    abbreviation_fixture["fixture_duplicate_abbreviation"] = (
        'fixture_duplicate_abbreviation = { abbreviation = "diesel0" }'
    )
    rejected(bool(abbreviation_errors(abbreviation_fixture)), "abbreviation collision")

    self_loop_fixture = dict(all_tank_techs)
    self_loop_fixture["fixture_self_loop"] = (
        "fixture_self_loop = { path = { leads_to_tech = fixture_self_loop } }"
    )
    rejected("fixture_self_loop" in tank_self_loop_ids(self_loop_fixture), "tank technology self-loop")

    variant_fixture = export_variant_map(text(FOCUS_EFFECT_FILE))
    variant_fixture["Undefined Export"] = "medium_tank_chassis_3"
    rejected(variant_fixture != EXPORT_VARIANTS, "undefined export variant")

    rejected(bool(missing_ammunition_categories({"tank_ammo_kinetic"})), "missing ammunition category")
    rejected(
        bool(
            ammunition_requirement_error(
                "tank_anti_air_cannon",
                {"tank_anti_air_cannon", "light_turret"},
            )
        ),
        "AA design without ammunition",
    )
    if ammunition_requirement_error(
        "tank_anti_air_cannon",
        {"tank_anti_air_cannon", "light_turret", "tank_aa_ammo_1"},
    ):
        raise AssertionError("an AA design with dedicated ammunition was rejected")

    module_rows = _module_csv_rows(BALANCE_CSV_FILE)

    def fixture_must_fail(callback, label: str) -> None:
        before = len(errors)
        callback()
        if len(errors) == before:
            raise AssertionError(f"tank negative fixture was accepted: {label}")
        del errors[before:]

    def duplicate_module_fixture() -> None:
        if "tank_anti_air_cannon" in module_rows:
            fail("duplicate tank module ID in fixture CSV")

    fixture_must_fail(duplicate_module_fixture, "duplicate module ID")

    changed_numeric = list(module_rows["tank_anti_air_cannon"])
    changed_numeric[_csv_column_index("K")] = "2.25"
    fixture_must_fail(
        lambda: _compare_module_row(
            "tank_anti_air_cannon", changed_numeric,
            module_balance_record("tank_anti_air_cannon"), "fixture changed numeric"
        ),
        "changed numeric value",
    )

    confused_operation = list(module_rows["tank_gasoline_engine"])
    confused_operation[_csv_column_index("W")] = ""
    confused_operation[_csv_column_index("X")] = "0.5"
    fixture_must_fail(
        lambda: _compare_module_row(
            "tank_gasoline_engine", confused_operation,
            module_balance_record("tank_gasoline_engine"), "fixture operation"
        ),
        "operation confusion",
    )
    missing_value = list(module_rows["tank_anti_air_cannon"])
    missing_value[_csv_column_index("AJ")] = ""
    fixture_must_fail(
        lambda: _compare_module_row(
            "tank_anti_air_cannon", missing_value,
            module_balance_record("tank_anti_air_cannon"), "fixture missing value"
        ),
        "missing value",
    )


    malformed_numeric = list(module_rows["tank_anti_air_cannon"])
    malformed_numeric[_csv_column_index("AH")] = "not-a-number"
    fixture_must_fail(
        lambda: _compare_module_row(
            "tank_anti_air_cannon", malformed_numeric,
            module_balance_record("tank_anti_air_cannon"), "fixture malformed numeric"
        ),
        "malformed numeric value",
    )


def expected_tank_types() -> set[str]:
    result = set()
    for family, count in FAMILY_TIERS.items():
        for tier in range(count):
            result.add(f"{family}_tank_chassis_{tier}")
            result.update(
                f"{family}_tank_{role}_chassis_{tier}"
                for role in FAMILY_ROLES[family]
            )
    return result


doctrine_files = [
    TECH_DIR / "land_doctrine.txt",
    TECH_DIR / "air_doctrine.txt",
    TECH_DIR / "naval_doctrine.txt",
]
key_files = doctrine_files + [
    TECH_DIR / "NSB_armor.txt",
    TECH_DIR / "NSB_armor_modules.txt",
    TECH_DIR / "armor.txt",
    TECH_DIR / "support.txt",
    MODULE_FILE,
    CHASSIS_FILE,
    MOD / "common/units/equipment/x_tank_chassis.txt",
    MOD / "common/units/CWIC-Special-Units.txt",
    AI_FILE,
    ENUM_FILE,
    VARIANT_EFFECT_FILE,
    FOCUS_EFFECT_FILE,
    TANK_ROLE_FILE,
    TANK_ICON_FILE,
    TANK_LOC_FILE,
    MOD / "interface/tank_designer_view.gui",
    MOD / "interface/countrytechtreeview.gui",
    *FOCUS_FILES,
]
for candidate in key_files:
    if candidate in doctrine_files and not candidate.is_file():
        continue
    brace_balance(candidate)

# Doctrine loader contract. The rework is either active in
# common/technologies/ or parked in common/technologies/doctrine rework/,
# which HOI4 does not load. Both are valid; a mix of the two is not.
parked_dir = TECH_DIR / "doctrine rework"
active_doctrine = [path for path in doctrine_files if path.is_file() and path.stat().st_size]
parked_doctrine = sorted(parked_dir.glob("*.txt")) if parked_dir.is_dir() else []
if active_doctrine and parked_doctrine:
    fail(
        "doctrine technologies exist both in common/technologies and in "
        "common/technologies/doctrine rework; the game would load only the active copy"
    )
elif active_doctrine and len(active_doctrine) != len(doctrine_files):
    missing = sorted(path.name for path in doctrine_files if path not in active_doctrine)
    fail(f"doctrine rework is active but incomplete; missing: {missing}")
elif not active_doctrine and not parked_doctrine:
    fail("doctrine technologies are neither active nor parked")

doctrine_root = MOD / "common/doctrines"
intentional_empty = {
    "grand_doctrines/air_grand_doctrines.txt",
    "grand_doctrines/land_grand_doctrines.txt",
    "grand_doctrines/sea_grand_doctrines.txt",
    "grand_doctrines/special_forces_grand_doctrines.txt",
    "tracks/air_doctrine_track.txt",
    "tracks/land_doctrine_tracks.txt",
    "tracks/sea_doctrine_tracks.txt",
    "tracks/special_forces_tracks.txt",
    "subdoctrines/air/air_fighter_aircraft_subdoctrines.txt",
    "subdoctrines/air/air_heavy_aircraft_subdoctrines.txt",
    "subdoctrines/air/air_medium_aircraft_subdoctrines.txt",
    "subdoctrines/air/air_strike_aircraft_subdoctrines.txt",
    "subdoctrines/land/armor_subdoctrines.txt",
    "subdoctrines/land/combat_support_subdoctrines.txt",
    "subdoctrines/land/infantry_subdoctrines.txt",
    "subdoctrines/land/operations_subdoctrines.txt",
    "subdoctrines/sea/navy_capital_subdoctrines.txt",
    "subdoctrines/sea/navy_carrier_doctrines.txt",
    "subdoctrines/sea/navy_screen_doctrines.txt",
    "subdoctrines/sea/navy_submarine_doctrines.txt",
    "subdoctrines/special_forces/special_forces_subdoctrines.txt",
}
actual_empty = {
    str(path.relative_to(doctrine_root))
    for path in doctrine_root.rglob("*.txt")
    if path.stat().st_size == 0
}
if actual_empty != intentional_empty:
    fail(
        "zero-byte doctrine override set changed: "
        f"missing={sorted(intentional_empty - actual_empty)}, "
        f"unexpected={sorted(actual_empty - intentional_empty)}"
    )

# Technology IDs, links, folders, and duplicate definitions.
technology_blocks: list[tuple[str, str, Path]] = []
for path in sorted(TECH_DIR.glob("*.txt")):
    technology_blocks.extend(
        (name, block, path) for name, block in top_level_blocks(text(path), "technologies")
    )
technology_ids = [name for name, _, _ in technology_blocks]
for name, count in Counter(technology_ids).items():
    if count > 1:
        fail(f"duplicate technology id: {name} ({count} definitions)")
technology_set = set(technology_ids)
for name, block, path in technology_blocks:
    for target in re.findall(r"\bleads_to_tech\s*=\s*([A-Za-z0-9_]+)", code_only(block)):
        checked_path_files = set(doctrine_files) | {
            TECH_DIR / "NSB_armor.txt",
            TECH_DIR / "NSB_armor_modules.txt",
        }
        if path in checked_path_files and target not in technology_set:
            fail(f"undefined technology path {name} -> {target} in {path.name}")

# A cross-decade path plus an allow prerequisite assigns the target to two grid
# boxes. The engine reports this as "multiple potential grid boxes" at startup.
land_blocks = {
    name: block
    for name, block, path in technology_blocks
    if path == TECH_DIR / "land_doctrine.txt"
}
for source, block in land_blocks.items():
    source_decade = re.search(r"_(\d{4})s_", source)
    if not source_decade:
        continue
    for target in re.findall(r"\bleads_to_tech\s*=\s*([A-Za-z0-9_]+)", code_only(block)):
        target_decade = re.search(r"_(\d{4})s_", target)
        target_block = code_only(land_blocks.get(target, ""))
        if (
            target_decade
            and source_decade.group(1) != target_decade.group(1)
            and re.search(rf"\bhas_tech\s*=\s*{re.escape(source)}\b", target_block)
        ):
            fail(
                "cross-decade doctrine path duplicates its allow prerequisite: "
                f"{source} -> {target}"
            )

doctrine_blocks = [
    (name, block, path)
    for name, block, path in technology_blocks
    if path in set(doctrine_files)
]
english_loc_keys = set()
for path in (MOD / "localisation/english").glob("*.yml"):
    english_loc_keys.update(
        re.findall(r"^\s*([A-Za-z0-9_.-]+):\d*\s", text(path), re.MULTILINE)
    )
for name, _, path in doctrine_blocks:
    if name not in english_loc_keys:
        fail(f"missing English doctrine name for {name} ({path.name})")
    if f"{name}_desc" not in english_loc_keys:
        fail(f"missing English doctrine description for {name} ({path.name})")

land_effect_patterns = (
    r"\bcategory_all_armor\s*=\s*\{",
    r"\bcategory_all_infantry\s*=\s*\{",
    r"\bartillery\s*=\s*\{",
    r"\brecon\s*=\s*\{",
    r"\bplanning_speed\s*=",
    r"\bsupply_consumption_factor\s*=",
)
for name, block, path in doctrine_blocks:
    if path == TECH_DIR / "land_doctrine.txt" and not any(
        re.search(pattern, code_only(block)) for pattern in land_effect_patterns
    ):
        fail(f"land doctrine has no gameplay effect: {name}")
if active_doctrine and re.search(
    r"\bdefence\s*=", code_only(text(TECH_DIR / "land_doctrine.txt"))
):
    fail("land doctrine uses rejected equipment stat spelling 'defence'; use 'defense'")

tag_text = code_only(text(MOD / "common/technology_tags/00_technology.txt"))
folder_ids = set(re.findall(r"^\s*([A-Za-z0-9_]+)\s*=\s*\{", tag_text, re.MULTILINE))
for name, block, path in technology_blocks:
    for folder in re.findall(r"\bfolder\s*=\s*\{[\s\S]*?\bname\s*=\s*([A-Za-z0-9_]+)", code_only(block)):
        if folder not in folder_ids:
            fail(f"undefined technology folder {folder} used by {name} in {path.name}")

# Tank module definition/unlock/category contract.
module_blocks = top_level_blocks(text(MODULE_FILE), "equipment_modules")
module_ids = {name for name, _ in module_blocks if name != "limit"}
module_definitions = dict(module_blocks)
ammo_categories = {"tank_ammo_kinetic", "tank_ammo_he"}
AA_ARMAMENT_MODULES = {
    "tank_anti_air_cannon",
    "tank_anti_air_cannon_2",
    "tank_anti_air_cannon_3",
}
AA_AMMUNITION_CONTRACT = {
    "tank_aa_ammo_1": {
        "parent": "none",
        "technology": "nsb_aiming_devices0",
        "year": "1942",
        "air_attack": 4.0,
        "build_cost_ic": 0.25,
        "dismantle_cost_ic": 0.05,
        "texture": "gfx/interface/equipmentdesigner/tanks/Modules/SPAAG/Autocannon Ammo/HE auto base.png",
    },
    "tank_aa_ammo_2": {
        "parent": "tank_aa_ammo_1",
        "technology": "nsb_aiming_devices2",
        "year": "1955",
        "air_attack": 7.0,
        "build_cost_ic": 0.5,
        "dismantle_cost_ic": 0.1,
        "texture": "gfx/interface/equipmentdesigner/tanks/Modules/SPAAG/Autocannon Ammo/HEVT auto 1980.png",
    },
    "tank_aa_ammo_3": {
        "parent": "tank_aa_ammo_2",
        "technology": "nsb_aiming_devices4",
        "year": "1985",
        "air_attack": 10.0,
        "build_cost_ic": 0.75,
        "dismantle_cost_ic": 0.15,
        "texture": "gfx/interface/equipmentdesigner/tanks/Modules/SPAAG/Autocannon Ammo/HEAB auto 2000.png",
    },
}
AA_AMMUNITION_MODULES = set(AA_AMMUNITION_CONTRACT)


def module_category(module: str) -> str:
    match = re.search(r"\bcategory\s*=\s*(\w+)", module_definitions.get(module, ""))
    return match.group(1) if match else ""


def needs_ammunition(module: str) -> bool:
    # The 2026-09-09 owner decision requires AA guns to carry dedicated
    # ammunition.
    return module in AA_ARMAMENT_MODULES or any(
        re.search(r"\b(?:soft_attack|hard_attack|ap_attack)\s*=", block)
        for block in keyed_blocks(module_definitions.get(module, ""), "multiply_stats")
    )


def ammunition_requirement_error(
    main_armament: str, installed_modules: set[str]
) -> str:
    if main_armament in AA_ARMAMENT_MODULES:
        if not (installed_modules & AA_AMMUNITION_MODULES):
            return "lacks dedicated AA ammunition"
        return ""
    if not needs_ammunition(main_armament):
        return ""
    installed_categories = {module_category(module) for module in installed_modules}
    if missing_ammunition_categories(installed_categories):
        return "lacks attack-producing AP/HE ammunition"
    return ""


def positive_attack_multiplier(
    module: str, definitions: dict[str, str] | None = None
) -> bool:
    """Whether a module multiplies at least one attack statistic above zero."""
    definitions = module_definitions if definitions is None else definitions
    for block in keyed_blocks(definitions.get(module, ""), "multiply_stats"):
        for value in re.findall(r"\b(?:soft_attack|hard_attack|ap_attack)\s*=\s*(-?[0-9.]+)", block):
            try:
                if float(value) > 0:
                    return True
            except ValueError:
                continue
    return False

module_categories = {
    match.group(1)
    for _, block in module_blocks
    if (match := re.search(r"^\s*category\s*=\s*([A-Za-z0-9_]+)", block, re.MULTILINE))
}
unlocked_modules = set()
for _, block, path in technology_blocks:
    if path not in {TECH_DIR / "NSB_armor.txt", TECH_DIR / "NSB_armor_modules.txt"}:
        continue
    for match in re.finditer(r"enable_equipment_modules\s*=\s*\{([^}]*)\}", code_only(block), re.DOTALL):
        for module in re.findall(r"\b[A-Za-z][A-Za-z0-9_]*\b", match.group(1)):
            unlocked_modules.add(module)
            if module not in module_ids:
                fail(f"undefined equipment module unlocked in {path.name}: {module}")
dead_modules = module_ids - unlocked_modules
if dead_modules:
    fail(f"unreachable tank modules remain: {sorted(dead_modules)}")

aa_unlocks = module_unlock_provenance()
aa_icon_text = text(TANK_ICON_FILE)
for module, expected in AA_AMMUNITION_CONTRACT.items():
    definition = module_definitions.get(module, "")
    if not definition:
        fail(f"AA ammunition module is missing: {module}")
        continue
    record = module_balance_record(module)
    expected_add = {
        "air_attack": expected["air_attack"],
        "build_cost_ic": expected["build_cost_ic"],
    }
    if record["add"] != expected_add or record["multiply"]:
        fail(f"{module} AA ammunition stats differ from the authored contract")
    if record["category"] != "tank_ammo_he":
        fail(f"{module} must use the existing tank_ammo_he category")
    if direct_values(definition, "allow_equipment_type") != ["anti_air"]:
        fail(f"{module} must be restricted to the anti_air role")
    if record["parent"] != expected["parent"]:
        fail(f"{module} has the wrong AA ammunition parent")
    if record["dismantle"] != expected["dismantle_cost_ic"]:
        fail(f"{module} has the wrong AA ammunition dismantle cost")
    if direct_values(definition, "xp_cost") != ["1"]:
        fail(f"{module} must cost 1 XP")
    expected_unlock = [(expected["technology"], expected["year"])]
    if aa_unlocks.get(module) != expected_unlock:
        fail(f"{module} has the wrong unlock provenance: {aa_unlocks.get(module)}")
    if module not in english_loc_keys or f"{module}_desc" not in english_loc_keys:
        fail(f"{module} AA ammunition localisation is incomplete")
    icon_match = re.search(
        rf'name\s*=\s*"GFX_SMI_{re.escape(module)}"[\s\S]*?textureFile\s*=\s*"([^"]+)"',
        aa_icon_text,
    )
    if not icon_match:
        fail(f"{module} AA ammunition icon declaration is missing")
    elif icon_match.group(1) != expected["texture"] or not (MOD / icon_match.group(1)).is_file():
        fail(f"{module} AA ammunition icon path is invalid")

allowed_categories = set()
for match in re.finditer(
    r"allowed_module_categories\s*=\s*\{([^}]*)\}",
    code_only(text(CHASSIS_FILE)),
    re.DOTALL,
):
    allowed_categories.update(re.findall(r"\b[A-Za-z][A-Za-z0-9_]*\b", match.group(1)))
missing_categories = allowed_categories - module_categories
if missing_categories:
    fail(f"chassis allow module categories with no live module: {sorted(missing_categories)}")

# Owner decision 2026-09-10: the flame armament module and category are removed.
for required in {
    "tank_anti_air_cannon",
    "tank_anti_air_cannon_2",
    "tank_anti_air_cannon_3",
}:
    if required not in module_ids:
        fail(f"required retained-role module is missing: {required}")
# Owner decision 2026-09-10 role-token remap pins role-exclusive module
# eligibility and scans every module-file allow/forbid token.
for message in tank_module_type_bound_errors(dict(module_blocks)):
    fail(message)
# Owner decision 2026-09-10 phase 3 restructure requires zero exact-match
# forbids anywhere in the tank module file.
if re.search(
    r"\bforbid_equipment_type_exact_match\s*=",
    code_only(text(MODULE_FILE)),
):
    fail("tank module file must contain zero forbid_equipment_type_exact_match keys")
# Supported types, OOB references, AI historical designs, and removed roles.
expected_types = expected_tank_types()
chassis_text = text(CHASSIS_FILE)
base_types = set(
    re.findall(r"^\s*((?:light|medium|heavy)_tank_chassis_[0-9]+)\s*=\s*\{", chassis_text, re.MULTILINE)
)
expected_base = {name for name in expected_types if re.match(r"^(light|medium|heavy)_tank_chassis_", name)}
if base_types != expected_base:
    fail(f"base tank chassis set differs from contract: {sorted(base_types ^ expected_base)}")

oob_refs: set[str] = set()
oob_required_techs: dict[str, set[str]] = {}
foreign_producer_techs: dict[tuple[str, str], set[str]] = {}
oob_files_with_tanks: list[Path] = []
versioned_oob_requests = 0
for path in sorted(OOB_DIR.glob("*_nsb.txt")):
    value = code_only(text(path))
    refs = set(OOB_TANK_PATTERN.findall(value))
    if not refs:
        continue
    oob_files_with_tanks.append(path)
    oob_refs.update(refs)
    brace_balance(path)
    if STARTING_VARIANT_EFFECT in value:
        fail(
            f"{path.name} bootstraps variants inside the OOB; the bootstrap must run "
            "in country history before set_oob"
        )
    # A tank chassis maps one-to-one onto its unlock, so seed those by type. The
    # carrier tiers do not: two bookmark generations share a light hull tier
    # after the 2026-09-11 cutover, so their technology is resolved from the
    # requested design name by `record_request` below.
    oob_required_techs[path.stem] = {
        BOOKMARK_VARIANT_TECHS[ref]
        for ref in refs
        if ref in BOOKMARK_VARIANT_TECHS
        and not re.match(r"light_tank_(?:apc|ifv)_chassis_\d", ref)
    }
    # A tank bought from or designed by another tag is created by that tag, so
    # its chassis technology belongs to that tag's bookmark bootstrap rather
    # than this OOB's.
    era = path.stem.split("_")[1]

    def request_tech(equipment_type: str, producer: str, name: str | None) -> str | None:
        """The technology whose generation bootstraps this exact design.

        Resolving by equipment type alone stopped working with the 2026-09-11
        carrier cutover: two generations share a light hull tier, so Canada's
        M113A1 and its 1960 carrier are both `light_tank_apc_chassis_4` but are
        unlocked by different technologies. The requested design name is what
        distinguishes them.
        """
        if name is not None:
            for preset in NATIONAL_PRESETS + CARRIER_PRESETS:
                if (preset["type"], preset["producer"], preset["name"]) == (equipment_type, producer, name):
                    return preset["technology"]
        return BOOKMARK_VARIANT_TECHS.get(equipment_type)

    def record_request(block: str, equipment_type: str, name: str | None) -> None:
        creator = oob_variant_producer(block, path.stem[:3])
        technology = request_tech(equipment_type, creator, name)
        if technology is None:
            return
        oob_required_techs[path.stem].add(technology)
        # A tank bought from or designed by another tag is created by that tag,
        # so its chassis technology also belongs to that tag's bookmark bootstrap.
        if creator != path.stem[:3]:
            foreign_producer_techs.setdefault((creator, era), set()).add(technology)


    for effect, field in (
        ("add_equipment_production", "version_name"),
        ("add_equipment_to_stockpile", "variant_name"),
    ):
        for block in keyed_blocks(value, effect):
            type_match = re.search(
                r"\btype\s*=\s*([A-Za-z0-9_]+)", code_only(block)
            )
            if not type_match or type_match.group(1) not in BOOKMARK_VARIANT_NAMES:
                continue
            tank_type = type_match.group(1)
            name_match = re.search(
                rf'\b{field}\s*=\s*"([^"]+)"', code_only(block)
            )
            if not name_match:
                fail(
                    f"{path.name} {effect} request for {tank_type} does not select "
                    f"an explicit variant with {field}"
                )
            elif name_match.group(1) not in bookmark_variant_names(tank_type, oob_variant_producer(block, path.stem[:3])):
                fail(
                    f"{path.name} {effect} request asks for {tank_type} variant "
                    f"{name_match.group(1)!r}, which no bootstrap creates"
                )
            record_request(block, tank_type, name_match.group(1) if name_match else None)
            versioned_oob_requests += 1

    for block in keyed_blocks(value, "force_equipment_variants"):
        for tank_type in BOOKMARK_VARIANT_NAMES:
            for variant_request in keyed_blocks(block, tank_type):
                name_match = re.search(
                    r'\bversion_name\s*=\s*"([^"]+)"',
                    code_only(variant_request),
                )
                if not name_match:
                    fail(
                        f"{path.name} forced variant request for {tank_type} does not "
                        "select an explicit version_name"
                    )
                elif name_match.group(1) not in bookmark_variant_names(tank_type, oob_variant_producer(variant_request, path.stem[:3])):
                    fail(
                        f"{path.name} forced variant request asks for {tank_type} "
                        f"variant {name_match.group(1)!r}, which no bootstrap creates"
                    )
                record_request(variant_request, tank_type, name_match.group(1) if name_match else None)
                versioned_oob_requests += 1
invalid_oob = oob_refs - expected_types
if invalid_oob:
    fail(f"NSB OOBs reference invalid tank types: {sorted(invalid_oob)}")

# The bootstrap must run in country history immediately before the matching
# set_oob, because an OOB-local instant_effect resolves after that OOB's
# version-sensitive requests.
history_bootstrap_sites = 0
set_oob_pattern = re.compile(r'^([ \t]*)set_oob = "([A-Za-z0-9_]+_nsb)"[ \t]*$', re.MULTILINE)
bootstrapped_oobs: set[str] = set()
bootstrapped_files: set[Path] = set()
for path in sorted(HISTORY_DIR.glob("*.txt")):
    value = text(path)
    tag_match = re.match(r"([A-Z]{3}) - ", path.name)
    tag = tag_match.group(1) if tag_match else ""
    if tag in MANUFACTURER_BLOC_TAGS and STARTING_VARIANT_EFFECT not in value:
        fail(
            f"{path.name} sells tanks to 1980 OOBs but never creates its variants"
        )
    for match in set_oob_pattern.finditer(value):
        indent, oob = match.group(1), match.group(2)
        if oob not in oob_required_techs:
            continue
        bootstrapped_oobs.add(oob)
        bootstrapped_files.add(path)
        history_bootstrap_sites += 1
        required = oob_required_techs[oob] | foreign_producer_techs.get(
            (tag, oob.split("_")[1]), set()
        )
        expected_techs = sorted(required)
        # FRA's 1949 bootstrap also seeds the engine ladder before its
        # starting variants are created.
        if tag == "FRA" and oob == "FRA_1949_nsb":
            expected_techs += ["nsb_engines", "nsb_engines0"]
        expected = "\n".join(
            [
                f"{indent}# Starting tank variants must exist before the OOB is loaded.",
                f"{indent}set_technology = {{",
                *(f"{indent}\t{tech} = 1" for tech in expected_techs),
                f"{indent}\tpopup = no",
                f"{indent}}}",
                f"{indent}{STARTING_VARIANT_EFFECT}",
                "",
            ]
        )
        if not value[: match.start()].endswith(expected):
            fail(
                f"{path.name} does not bootstrap the required chassis technologies and "
                f"starting variants immediately before set_oob = \"{oob}\""
            )
missing_bootstrap = set(oob_required_techs) - bootstrapped_oobs
if missing_bootstrap:
    fail(f"NSB OOBs are never loaded from country history: {sorted(missing_bootstrap)}")
unbootstrapped_producers = {
    producer
    for producer, _ in foreign_producer_techs
    if producer not in MANUFACTURER_BLOC_TAGS
    and not any(path.name.startswith(f"{producer} - ") for path in bootstrapped_files)
}
if unbootstrapped_producers:
    fail(
        "OOBs buy tanks from tags that never create variants: "
        f"{sorted(unbootstrapped_producers)}"
    )

variant_effect_text = text(VARIANT_EFFECT_FILE)
variant_blocks = keyed_blocks(variant_effect_text, "create_equipment_variant")
variant_guard_techs: dict[str, list[str]] = {}
for guarded_block in keyed_blocks(variant_effect_text, "if"):
    guarded_variants = keyed_blocks(guarded_block, "create_equipment_variant")
    if len(guarded_variants) != 1:
        fail("each starting tank variant guard must contain exactly one variant")
        continue
    guarded_type = re.search(
        r"^\s*type\s*=\s*([A-Za-z0-9_]+)",
        guarded_variants[0],
        re.MULTILINE,
    )
    if guarded_type:
        variant_guard_techs[guarded_type.group(1)] = re.findall(
            r"\bhas_tech\s*=\s*([A-Za-z0-9_]+)", guarded_block
        )
variant_types: list[str] = []
for block in variant_blocks:
    type_match = re.search(r"^\s*type\s*=\s*([A-Za-z0-9_]+)", block, re.MULTILINE)
    if not type_match:
        fail("starting tank create_equipment_variant block has no type")
        continue
    variant_type = type_match.group(1)
    variant_types.append(variant_type)
    name_match = re.search(r'^\s*name\s*=\s*"([^"]+)"', block, re.MULTILINE)
    if not name_match or name_match.group(1) != BOOKMARK_VARIANT_NAMES.get(variant_type):
        fail(
            f"starting variant {variant_type} does not use its stable bookmark name"
        )
    if not re.search(r"^\s*allow_without_tech\s*=\s*yes\b", block, re.MULTILINE):
        fail(
            f"starting variant {variant_type} can be skipped before OOB tech state settles"
        )
    slots = set(
        re.findall(
            r"^\s*([A-Za-z0-9_]+_slot(?:_[0-9]+)?)\s*=\s*([A-Za-z0-9_]+)",
            block,
            re.MULTILINE,
        )
    )
    slot_names = {slot for slot, _ in slots}
    if not REQUIRED_VARIANT_SLOTS <= slot_names:
        fail(
            f"starting variant {variant_type} has wrong required slots: "
            f"{sorted(slot_names)}"
        )
    for slot, module in slots:
        if module == "empty" and slot.startswith("tank_special_slot_"):
            continue
        if module not in module_ids:
            fail(f"starting variant {variant_type} uses undefined module {module}")
    ammunition_error = ammunition_requirement_error(
        dict(slots).get("main_armament_slot", ""),
        {module for _, module in slots},
    )
    if ammunition_error:
        fail(f"starting variant {variant_type} {ammunition_error}")
    variant_techs = variant_guard_techs.get(variant_type, [])
    if variant_techs != [BOOKMARK_VARIANT_TECHS.get(variant_type)]:
        fail(f"starting variant {variant_type} has the wrong chassis technology guard")
    for tech in variant_techs:
        if tech not in technology_set:
            fail(f"starting variant {variant_type} is gated by undefined tech {tech}")
if len(variant_types) != len(set(variant_types)):
    duplicates = sorted(
        name for name, count in Counter(variant_types).items() if count > 1
    )
    fail(f"duplicate starting tank variant types: {duplicates}")
# The two directions are not the same defect. An OOB requesting a design nothing
# creates is a silent break, so that direction stays hard. A created design no OOB
# requests is legitimate, but only for a measured reason - each entry below is a
# design no order of battle CAN request today, not merely one nobody has got to.
#
# Measured 2026-09-17: of the five battalions consuming these families, only
# `atgm_carrier` is fielded by any OOB at all. `medium_sp_anti_air_brigade`,
# `heavy_tank_destroyer_brigade`, `heavy_mechanized_infantry` and
# `heavy_armored_infantry` appear in zero OOBs, NSB or not, so a request for their
# equipment would name a design no division in the game draws. Putting those
# battalions into historical divisions is content and balance authoring, not
# conversion, and it needs an owner ruling per formation.
#
# `light_tank_destroyer_chassis_5` left this set the same day: NOR and RAJ field
# `atgm_carrier` in twenty divisions between them and now request it by name. SOV
# declares two ATGM templates and instantiates neither, so it has nothing to carry
# a request. The remaining light TD tiers are pre-ATGM eras no 1980 OOB wants.
AWAITING_OOB_REQUESTS = frozenset(
    {f"light_tank_destroyer_chassis_{tier}" for tier in range(5)}
    | {f"medium_tank_aa_chassis_{tier}" for tier in range(1, 7)}
    | {f"heavy_tank_destroyer_chassis_{tier}" for tier in range(1, 5)}
    | {f"medium_tank_apc_chassis_{tier}" for tier in range(7)}
    | {f"medium_tank_ifv_chassis_{tier}" for tier in range(7)}
)
if oob_refs - set(variant_types):
    fail(
        "NSB OOBs request starting tank variants nothing creates: "
        f"{sorted(oob_refs - set(variant_types))}"
    )
unrequested = set(variant_types) - oob_refs - AWAITING_OOB_REQUESTS
if unrequested:
    fail(
        "starting tank variants no NSB OOB requests and not named as awaiting "
        f"conversion: {sorted(unrequested)}"
    )
if set(variant_types) != set(BOOKMARK_VARIANT_NAMES):
    fail(
        "starting tank variant name map differs from created variants: "
        f"missing={sorted(set(variant_types) - set(BOOKMARK_VARIANT_NAMES))}, "
        f"unused={sorted(set(BOOKMARK_VARIANT_NAMES) - set(variant_types))}"
    )
if set(BOOKMARK_VARIANT_TECHS) != set(BOOKMARK_VARIANT_NAMES):
    fail("starting tank variant technology map differs from its name map")

ai_text = code_only(text(AI_FILE))
ai_types = set(re.findall(r"^\s*type\s*=\s*([A-Za-z0-9_]+)", ai_text, re.MULTILINE))
missing_ai = expected_types - ai_types
if missing_ai:
    fail(f"tank types without a generic historical AI design: {sorted(missing_ai)}")
# Owner decision 2026-09-11 carrier cutover: APC and IFV are roles on the light
# tank hull, so generic history coverage is exactly the FAMILY_ROLES set. The two
# standalone carrier recipe families were deleted as duplicates of the role
# recipes phase 3 authored.
if len(re.findall(r"^\s*history\s*=\s*yes\b", ai_text, re.MULTILINE)) != len(expected_types):
    fail("generic tank AI file must contain one historical recipe per supported tank type")
for recipe in keyed_blocks(ai_text, "target_variant"):
    type_match = re.search(r"\btype\s*=\s*(\w+)", recipe)
    if not type_match:
        continue
    equipment_type = type_match.group(1)
    # Owner decision 2026-09-10: flame recipes are removed with the vehicle
    # taxonomy, so only retained AA recipes bypass the ammunition slots.
    if re.search(r"_aa_chassis_", equipment_type):
        continue
    # Owner decision 2026-09-10 phase 3 restructure exempts the APC family by
    # family name: APC armament modules may multiply stats, but APC histories
    # intentionally carry no shell ammunition.
    if "_tank_apc_chassis_" in equipment_type:
        continue
    for category in ammo_categories:
        if not re.search(rf"\btank_special_slot_\d+\s*=\s*{category}\b", recipe):
            fail(f"AI recipe {equipment_type} lacks attack-producing {category}")
for enable in keyed_blocks(ai_text, "enable"):
    # Every cannon recipe must wait for the two ammunition research unlocks.
    if "nsb_ammo" in enable and "nsb_he_ammo0" not in enable:
        fail("AI ammunition prerequisite omits HE research")
# This count tracks the current conventional-gun recipe population and must move
# whenever recipes are added or removed. 103 -> 95 on 2026-09-11 when the carrier
# cutover deleted the eight standalone IFV histories, which duplicated the light
# hull IFV role recipes phase 3 authored.
if len(re.findall(r"\bhas_tech\s*=\s*nsb_he_ammo0\b", ai_text)) != 95:
    fail("generic tank AI HE-gated recipe population must contain 95 entries")

active_roots = [MOD / "common", MOD / "interface"]
# The 2026-09-09 amphibious-role ids are distinct from UNSUPPORTED_IDS, so this
# exact-id scan keeps every retired vanilla amphibious id forbidden.
for path_root in active_roots:
    for path in path_root.rglob("*"):
        # `.info` files are prose notes, never loaded by the engine. Scanning them
        # made `_invalid_sub_unit_modifiers.info` fail for naming the very ids it
        # documents as absent (2026-09-10 flame removal).
        if not path.is_file() or path.suffix not in {".txt", ".gui", ".gfx"}:
            continue
        value = code_only(text(path))
        for identifier in UNSUPPORTED_IDS:
            if re.search(rf"(?<![A-Za-z0-9_]){re.escape(identifier)}(?![A-Za-z0-9_])", value):
                fail(f"unsupported id {identifier} remains in {path.relative_to(MOD)}")

enum_text = code_only(text(ENUM_FILE))
stale_generated_enums = (
    r"light_tank_artillery_chassisbt_equipment_[0-9]+",
    r"light_tank_rocket_chassist_equipment_[0-9]+",
    r"medium_tank_heavy_artillery_chassisbt_equipment_[0-9]+",
    r"medium_tank_rocket_chassisbt_equipment_[0-9]+",
    r"heavy_tank_rocket_chassist_equipment_[0-9]+",
)
# The retired carrier ids must be gone from the enum: they name equipment the
# engine no longer derives, and equipment_database.cpp:656 audits this enum in
# both directions.
if re.search(r"(?m)^\s*(?:apc|ifv)_chassis_\d\s*$", enum_text):
    fail("script_enum_equipment_bonus_type still lists a retired carrier hull")

for pattern in stale_generated_enums:
    if re.search(rf"^\s*{pattern}\s*$", enum_text, re.MULTILINE):
        fail(f"stale generated tank enum remains: {pattern}")
for tier in range(1, 7):
    expected_enum = f"light_tank_artillery_chassist_equipment_{tier}"
    if not re.search(rf"^\s*{expected_enum}\s*$", enum_text, re.MULTILINE):
        fail(f"generated tank enum is missing: {expected_enum}")

# UI and corrected shared progression checks.
for message in tank_designer_position_errors(text(MOD / "interface/tank_designer_view.gui")):
    fail(message)
# A missing `=` inside a `position`/`size`/`margin` block is a hard parse error that
# kills the rest of the file: `y@fixed_btn_mod_row_0` instead of
# `y=@fixed_btn_mod_row_0` produced `Malformed token: positionType` and dropped every
# remaining child of tank_designer_view, which then crashed the designer with SIGFPE.
# Brace balance cannot see it and the slot-name regex above matches the broken file, so
# this is checked explicitly.
designer_gui_files = [MOD / "interface/tank_designer_view.gui"]
designer_gui_files += sorted((MOD / "interface/equipmentdesigner/tanks").glob("*.gui"))
for gui_path in designer_gui_files:
    for number, raw_line in enumerate(text(gui_path).splitlines(), 1):
        stripped = re.sub(r"#.*", "", raw_line)
        normalised = re.sub(r"\s*=\s*", "=", stripped)
        for block in re.finditer(r"\b(?:position|size|margin)=\{([^{}]*)\}", normalised):
            for token in block.group(1).split():
                if "=" not in token:
                    fail(
                        f"{gui_path.name}:{number} has a malformed assignment "
                        f"{token!r}; a missing '=' breaks the whole file's parse"
                    )
slot_loc = text(TANK_LOC_FILE)
for designer_slot in sorted(REQUIRED_VARIANT_SLOTS) + [
    f"tank_special_slot_{index}" for index in range(1, TANK_SPECIAL_SLOT_COUNT + 1)
]:
    if not re.search(rf'(?m)^\s*EQ_MOD_SLOT_{designer_slot}_TITLE:\d*\s+"', slot_loc):
        fail(f"designer slot localisation is missing: EQ_MOD_SLOT_{designer_slot}_TITLE")
blueprint_dir = MOD / "interface/equipmentdesigner/tanks"
blueprint_files = sorted(blueprint_dir.glob("*.gui"))
# Owner decision 2026-09-11 carrier cutover deletes the two standalone carrier
# designer windows, `equipment_designer_mechanized_equipment` and its heavy
# twin, because those archetypes no longer carry module slots; 83 survive.
if len(blueprint_files) != 83:
    fail(f"tank blueprint file count changed: {len(blueprint_files)}")
expected_blueprint_slots = [
    f"tank_special_slot_{index}" for index in range(1, TANK_SPECIAL_SLOT_COUNT + 1)
]
for path in blueprint_files:
    blueprint = text(path)
    declared = re.findall(r'name = "(tank_special_slot_\d+)"', blueprint)
    if declared != expected_blueprint_slots:
        fail(
            f"{path.name} must declare {expected_blueprint_slots[0]}-"
            f"{expected_blueprint_slots[-1]} in order, found {declared}"
        )
    if "module_slots" not in blueprint:
        fail(f"{path.name} has no module_slots window to hold the slot entries")

support_text = code_only(text(TECH_DIR / "support.txt"))
for tier in range(1, 8):
    name = "tech_armor_engineers" if tier == 1 else f"tech_armor_engineers{tier}"
    block = next((value for tech, value, _ in technology_blocks if tech == name), "")
    if "allow =" not in block or "nsb_main_battle_tanks" not in block:
        fail(f"{name} does not allow an NSB MBT prerequisite")
    if re.search(r"dependencies\s*=\s*\{[^}]*\bmain_battle_tanks", block, re.DOTALL):
        fail(f"{name} still has a cumulative legacy-only MBT dependency")

armor_text = code_only(text(TECH_DIR / "armor.txt"))
for tier in range(1, 6):
    name = f"amphibious{tier}"
    block = next((value for tech, value, _ in technology_blocks if tech == name), "")
    if "name = armour_folder" not in block or "name = nsb_armor_folder" not in block:
        fail(f"{name} is not exposed in both armor folder configurations")
# The 2026-09-09 amphibious-role ratification does not override the technology
# gate; the legacy mechanized_marine remains inactive by default.
if not re.search(r"mechanized_marine\s*=\s*\{[\s\S]*?\bactive\s*=\s*no", code_only(text(MOD / "common/units/CWIC-Special-Units.txt"))):
    fail("mechanized_marine must be technology-gated (active = no)")

validate_doctrine_rework()
if "--doctrine-self-test" in sys.argv:
    run_doctrine_negative_fixtures()
validate_tank_rework()
if "--tank-self-test" in sys.argv:
    run_tank_negative_fixtures()


def designer_window_names() -> set[str]:
    names: set[str] = set()
    for path in sorted((MOD / "interface/equipmentdesigner/tanks").glob("*.gui")):
        names.update(re.findall(r'name\s*=\s*"(equipment_designer_[A-Za-z0-9_]+)"', code_only(text(path))))
    return names


def validate_designer_window_coverage(window_override: set[str] | None = None) -> None:
    """Every designable hull must resolve an equipment designer window.

    QA 2026-09-06: apc_chassis_* shipped with module slots but no designer window,
    and the production view silently fell back to the legacy Create Variant upgrade
    popup instead of the module designer. Per
    interface/equipmentdesigner/_documentation.info the window is resolved as
    equipment_designer_<EQUIPMENT>[_TAG] then equipment_designer_<ARCHETYPE>[_TAG].
    A sibling role window is not a fallback for the parent family; the 2026-09-09
    amphibious-role ratification made that distinction load-bearing. This check makes
    a missing window's silent, non-erroring downgrade loud for every designer family.
    """
    windows = designer_window_names() if window_override is None else window_override
    designable: dict[str, str] = {}
    for source in (CHASSIS_FILE, MECHANIZED_FILE, HEAVY_MECHANIZED_FILE):
        for name, block in top_level_blocks(text(source), "equipments"):
            if direct_values(block, "module_slots") != ["inherit"]:
                continue
            parents = direct_values(block, "archetype")
            designable[name] = parents[0] if parents else name
    duplicates = {
        name: direct_values(block, "archetype")[0]
        for name, block in top_level_blocks(
            text(MOD / "common/units/equipment/x_tank_chassis.txt"), "duplicate_archetypes"
        )
        if direct_values(block, "archetype")
    }
    if not designable:
        fail("no designable hulls were found for designer window coverage")
    for equipment, archetype in sorted(designable.items()):
        wanted = {f"equipment_designer_{equipment}", f"equipment_designer_{archetype}"}
        if not (wanted & windows):
            fail(
                f"{equipment} has designer module slots but no designer window; "
                f"the production view would fall back to the legacy upgrade popup"
            )
    for duplicate, archetype in sorted(duplicates.items()):
        if f"equipment_designer_{duplicate}" not in windows:
            fail(f"duplicate role archetype {duplicate} has no designer window")


def tank_icon_sprites() -> dict[str, str]:
    """Sprite name to texture path from the mod's tank icon registry."""
    sprites: dict[str, str] = {}
    for block in keyed_blocks(text(TANK_ICON_FILE), "spriteType"):
        name = re.search(r'\bname\s*=\s*"([^"]+)"', block)
        texture = re.search(r'(?i)\btexturefile\s*=\s*"([^"]+)"', block)
        if name and texture:
            sprites[name.group(1)] = texture.group(1)
    return sprites


CARRIER_STALE_ID = re.compile(
    r"(?<![A-Za-z0-9_])(?:apc|ifv)_(?:chassis|equipment)_\d(?![A-Za-z0-9_])"
)


def carrier_archetype_errors(archetype: str, block: str) -> list[str]:
    """A retired carrier family must be plain equipment again.

    Any surviving designer surface re-opens a second carrier designer that no
    technology unlocks, and `armor` in the type set keeps legacy mechanized in
    the armour production domain it only ever entered to route the NSB hulls.
    """
    errors: list[str] = []
    for key in ("module_slots", "module_count_limit", "default_modules"):
        if re.search(rf"\b{key}\s*=", block):
            errors.append(f"{archetype} still declares {key}; the carrier designer family is retired")
    found = direct_values(block, "type")
    if found != ["mechanized"]:
        errors.append(
            f"{archetype} must be plain mechanized equipment after the cutover, "
            f"found type = {found or 'none'}"
        )
    return errors


def carrier_module_errors(
    family: str,
    tier: int,
    row: tuple,
    definition: str | None,
    tech_block: str | None,
    parent: str | None,
) -> list[str]:
    """One rung of a carrier superstructure ladder.

    The ladder is the only instrument the restructure leaves for carrier
    identity: the hull supplies the light tank curve, and this module supplies
    the envelope the retired chassis row used to carry. A missing delta is
    silent - the design still builds, it is simply a light tank hull.

    Phase 7 added `defense` and `breakthrough` to that envelope. They are what
    separates a troop carrier from a tank, and the hull curve had them backwards:
    breakthrough 20 and defense 6, against a carrier's 3-18 and 11-45. Hardness
    and stat multipliers are banned here rather than merely unused - hardness is
    set once on the role root, and a multiplier applied on top of the rung breaks
    the hull-plus-module arithmetic the whole envelope is checked with.
    """
    module, technology, _hull_tier, armour, cost, speed, defense, breakthrough = row
    token = "flame" if family == "apc" else "rocket"
    if definition is None:
        return [f"carrier superstructure module is missing: {module}"]
    errors: list[str] = []
    if module_category(module) != f"tank_{family}_superstructure":
        errors.append(f"{module} must sit in tank_{family}_superstructure")
    if direct_values(definition, "allow_equipment_type") != [token]:
        errors.append(f"{module} must be gated on the {token} role token")
    add = keyed_blocks(definition, "add_stats")
    stats = dict(re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", add[0])) if add else {}
    for key, expected in (
        ("armor_value", armour),
        ("build_cost_ic", cost),
        ("maximum_speed", speed),
        ("defense", defense),
        ("breakthrough", breakthrough),
    ):
        raw = stats.get(key)
        if raw is None or abs(float(raw) - expected) >= 1e-6:
            errors.append(
                f"{module} must add {key} = {expected} so a tier {tier} carrier reproduces "
                f"the retired chassis row, found {raw or 'none'}"
            )
    if "hardness" in stats:
        errors.append(
            f"{module} must not add hardness; the role root sets it once for the family"
        )
    multiplied = [
        key
        for block in keyed_blocks(definition, "multiply_stats")
        for key, _value in re.findall(r"(\w+)\s*=\s*(-?[\d.]+)", block)
    ]
    if multiplied:
        errors.append(
            f"{module} must not multiply {sorted(multiplied)}; the envelope is checked as "
            "light hull tier plus this module"
        )
    if parent is not None and direct_values(definition, "parent") != [parent]:
        errors.append(f"{module} must descend from {parent} so the ladder researches in order")
    if tech_block is None:
        errors.append(f"carrier technology is missing: {technology}")
    else:
        if module not in tech_block:
            errors.append(f"{technology} must unlock {module}")
        if "enable_equipments" in tech_block:
            errors.append(f"{technology} still enables retired carrier equipment")
    return errors


def carrier_stale_id_errors(label: str, body: str) -> list[str]:
    """The cutover is atomic; one surviving id means a half-migrated mod."""
    stale = CARRIER_STALE_ID.search(body)
    return [f"{label} still references retired carrier equipment {stale.group(0)}"] if stale else []


def medium_hull_armour(year: int) -> float:
    """Armour of the newest medium tank hull whose year does not exceed `year`."""
    armour = MEDIUM_HULL_ARMOUR[0][1]
    for hull_year, value in MEDIUM_HULL_ARMOUR:
        if hull_year <= year:
            armour = value
    return armour


def carrier_armour_cap_errors(label: str, year: int, armour: float) -> list[str]:
    """Phase 7 envelope: a carrier never out-armours a same-year medium tank.

    Owner ruling 2026-09-12, and it binds both DLC profiles. The cutover
    reproduced a legacy ladder that put a 2005 IFV at 80 armour against the 2010
    MBT's 75, so the inversion was inherited rather than introduced - which is
    exactly why nothing caught it.
    """
    cap = medium_hull_armour(year) * CARRIER_ARMOUR_CAP_RATIO
    if armour <= cap + 1e-6:
        return []
    percent = int(CARRIER_ARMOUR_CAP_RATIO * 100)
    return [
        f"{label} carries {armour:g} armour against a {cap:g} cap; a {year} carrier may not "
        f"exceed {percent}% of the same-year medium tank hull ({medium_hull_armour(year):g})"
    ]



CARRIER_BATTALIONS = {
    "mechanized_infantry": ("CWIC-Infantry.txt", "light_tank_apc_chassis"),
    "heavy_mechanized_infantry": ("CWIC-Infantry.txt", "medium_tank_apc_chassis"),
    "armored_infantry": ("CWIC-Infantry.txt", "light_tank_ifv_chassis"),
    "heavy_armored_infantry": ("CWIC-Infantry.txt", "medium_tank_ifv_chassis"),
    "mechanized_airborne": ("CWIC-Special-Units.txt", "light_tank_ifv_chassis"),
    "engineer_mechanized": ("CWIC-Support-Units.txt", "light_tank_apc_chassis"),
    "recon_mechanized": ("CWIC-Support-Units.txt", "light_tank_apc_chassis"),
    "field_hospital_mechanized": ("CWIC-Support-Units.txt", "light_tank_apc_chassis"),
    "mechanized_marine": ("CWIC-Special-Units.txt", "light_tank_apc_chassis"),
}


def enabled_subunits() -> set[str]:
    """Every sub-unit some live technology enables.

    The parked doctrine rework directory is skipped for the same reason the
    doctrine contracts skip it: the game does not load it.
    """
    names: set[str] = set()
    for path in sorted(TECH_DIR.glob("*.txt")):
        for body in keyed_blocks(code_only(text(path)), "enable_subunits"):
            names.update(body.split())
    return names


def equipment_family_has_member(family: str) -> bool:
    """True when some equipment row declares `archetype = family`."""
    for path in sorted((MOD / "common/units/equipment").glob("*.txt")):
        for _, block in top_level_blocks(code_only(text(path)), "equipments"):
            if family in direct_values(block, "archetype"):
                return True
    return False


def validate_ai_templates() -> None:
    """Every AI division template must name live sub-units and live technologies.

    Added 2026-09-17 with the AI production pass. An `ai_templates` entry naming a
    battalion the rework removed, or gating on a technology that no longer exists,
    parses cleanly and simply never produces the division - the same silent class as
    the battalion and role-family defects. It also caught a live one: the generic
    light armour template gated `can_upgrade_in_field` on `lt_equipment`, an archetype
    the reparenting left with zero members, so the AI could never upgrade it.
    """
    sub_units: set[str] = set()
    for path in sorted((MOD / "common/units").glob("*.txt")):
        content = code_only(text(path))
        for name, _ in top_level_blocks(content, "sub_units"):
            sub_units.add(name)
    technologies: set[str] = set()
    for path in sorted(TECH_DIR.glob("*.txt")):
        for name, _ in top_level_blocks(code_only(text(path)), "technologies"):
            technologies.add(name)
    for path in sorted((MOD / "common/ai_templates").glob("*.txt")):
        content = code_only(text(path))
        brace_balance(path)
        for key in ("regiments", "support"):
            for body in keyed_blocks(content, key):
                for unit in re.findall(r"(\w+)\s*=\s*\d+", body):
                    if unit not in sub_units:
                        fail(f"{path.name} {key} names an undeclared sub-unit: {unit}")
        for technology in re.findall(r"has_tech\s*=\s*(\w+)", content):
            if technology not in technologies:
                fail(f"{path.name} gates on an undeclared technology: {technology}")
        for archetype in re.findall(r"has_equipment\s*=\s*\{\s*(\w+)", content):
            if not equipment_family_has_member(archetype):
                fail(
                    f"{path.name} gates has_equipment on {archetype}, which has no "
                    f"equipment member and can never be satisfied"
                )


def validate_research_armour_naming() -> None:
    """Historical names delivered on research completion rather than at a bookmark.

    Authored 2026-09-17. The bookmark dispatcher can only rename a design it creates,
    and it only creates tiers a bookmark date reaches, so 386 historical names for
    later tiers were undeliverable by any preset. This mechanism names the design when
    the country finishes researching that chassis tier.

    The failure modes are all silent, which is why each is pinned: a helper no
    technology calls never fires, a guard without the creation flag re-creates the
    design on every reload, a name whose localisation moved is no longer historical,
    and a recipe naming a module the slot does not admit is rejected by the engine
    with the design half-built.
    """
    manifest = json.loads(RESEARCH_NAMING_MANIFEST_FILE.read_text(encoding="utf-8"))
    presets = manifest["presets"]
    recipes = {recipe["generation"]: recipe for recipe in manifest["recipes"]}
    effects = code_only(text(RESEARCH_NAMING_EFFECT_FILE))
    technologies = code_only(text(TECH_DIR / "NSB_armor.txt"))

    pairs = {(preset["producer"], preset["generation"]) for preset in presets}
    if len(pairs) != len(presets):
        fail("research naming presets must not repeat a producer/generation pair")
    generations = {preset["generation"] for preset in presets}
    if generations != set(recipes):
        fail("research naming recipes and presets must cover the same generations")
        return

    for generation in sorted(generations):
        recipe = recipes[generation]
        helper = f"cwic_name_{generation}_variants"
        bodies = top_level_named_blocks(
            "effects = {\n" + effects + "\n}", helper, "research naming helper"
        )
        if len(bodies) != 1:
            fail(f"research naming helper {helper} must occur exactly once")
            continue
        # A helper nothing calls is dead content the engine never reports.
        if not re.search(rf"(?<![A-Za-z0-9_]){helper}\s*=\s*yes", technologies):
            fail(f"research naming helper {helper} is never called by a technology")
        if recipe["technology"] not in technology_ids:
            fail(f"research naming {generation} names an undeclared technology")
        for slot, module in recipe["modules"].items():
            if module not in module_ids:
                fail(f"research naming {generation} recipe uses undefined module {module}")
                continue
            if not slot.startswith("tank_special_slot_"):
                continue
            index = int(slot.rsplit("_", 1)[1])
            category = module_category(module)
            if category not in TANK_SPECIAL_SLOT_CATEGORIES.get(index, set()):
                fail(
                    f"research naming {generation} puts {module} ({category}) in "
                    f"{slot}, which does not admit it"
                )
        guards = top_level_named_blocks(bodies[0], "if", helper)
        expected = [preset for preset in presets if preset["generation"] == generation]
        if len(guards) != len(expected):
            fail(f"research naming helper {helper} guard count differs from manifest")
        flag = f"cwic_named_{generation}_created"
        for preset in expected:
            raw, path, line = naming_localisation_entry(preset["legacy_name_key"])
            if (raw, path, line) != (preset["source_name"], preset["source_path"], preset["source_line"]):
                fail(
                    f"research naming {preset['producer']}/{generation} provenance "
                    f"differs from live localisation"
                )
            elif unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode().strip() != preset["name"]:
                fail(
                    f"research naming {preset['producer']}/{generation} name differs "
                    f"from its localisation source"
                )
            matches = [
                guard for guard in guards
                if top_level_values(
                    top_level_named_blocks(guard, "limit", "guard limit")[0], "tag"
                ) == [preset["producer"]]
            ]
            if len(matches) != 1:
                fail(f"research naming {preset['producer']}/{generation} must have exactly one guard")
                continue
            guard = matches[0]
            for required in ('has_dlc = "No Step Back"', f"NOT = {{ has_country_flag = {flag} }}"):
                if required not in guard:
                    fail(f"research naming {preset['producer']}/{generation} missing guard: {required}")
            if top_level_values(guard, "set_country_flag") != [flag]:
                fail(f"research naming {preset['producer']}/{generation} must set its creation flag")
            elif guard.find("set_country_flag") < guard.find("create_equipment_variant"):
                fail(f"research naming {preset['producer']}/{generation} sets its flag before creation")
            variant = top_level_named_blocks(guard, "create_equipment_variant", "naming variant")[0]
            if re.findall(r'name\s*=\s*"([^"\n]*)"', variant) != [preset["name"]]:
                fail(f"research naming {preset['producer']}/{generation} wrong name")
            for field, value in (("type", generation), ("allow_without_tech", "yes"),
                                 ("parent_version", "0"), ("mark_older_equipment_obsolete", "yes")):
                if top_level_values(variant, field) != [value]:
                    fail(f"research naming {preset['producer']}/{generation} wrong {field}")
            mounted = dict(re.findall(r"(\w+)\s*=\s*(\w+)", top_level_named_blocks(variant, "modules", "naming modules")[0]))
            if mounted != recipe["modules"]:
                fail(f"research naming {preset['producer']}/{generation} differs from its recipe")


def validate_carrier_battalions() -> None:
    """Designer carrier output has to reach a battalion.

    Phase 5, 2026-09-12. `need` is what a battalion draws, `essential` is what it
    must hold to count as combat-ready and `transport` is its carrier; all three
    name an equipment family, and leaving any one of them on the retired carrier
    family makes the battalion silently read as unequipped. Before this pass every
    carrier design a player produced fed nothing at all.
    """
    units_dir = MOD / "common/units"
    for battalion, (filename, role) in sorted(CARRIER_BATTALIONS.items()):
        blocks = dict(top_level_blocks(text(units_dir / filename), "sub_units"))
        block = blocks.get(battalion)
        if block is None:
            fail(f"carrier battalion is missing: {battalion}")
            continue
        if direct_values(block, "transport") != [role]:
            fail(f"{battalion} must have transport = {role}")
        for key in ("need", "essential"):
            bodies = keyed_blocks(block, key)
            # Support companies carry no `essential` block at all; only the line
            # battalions do. An absent block is fine, a stale one is not.
            if not bodies and key == "essential":
                continue
            if len(bodies) != 1:
                fail(f"{battalion} must declare exactly one {key} block")
                continue
            if not re.search(rf"(?<![A-Za-z0-9_]){role}(?![A-Za-z0-9_])", bodies[0]):
                fail(f"{battalion} {key} must name {role}")
        # An `active = no` battalion that no technology enables is dead content and
        # the engine logs nothing for it; so is one with no name key, which renders
        # as the raw id. Both are how `heavy_mechanized_infantry` and
        # `heavy_armored_infantry` could have shipped invisible on 2026-09-17.
        if direct_values(block, "active") == ["no"] and battalion not in enabled_subunits():
            fail(f"{battalion} is active = no and no technology enables it")
        if naming_localisation_entry(battalion)[0] is None:
            fail(f"{battalion} has no English localisation name")
    retired = re.compile(
        r"(?<![A-Za-z0-9_])mechanized(?:_heavy|_marine)?_equipment(?![A-Za-z0-9_])"
    )
    for path in sorted(units_dir.glob("*.txt")):
        if retired.search(code_only(text(path))):
            fail(f"{path.name} still wires a land sub-unit to a retired carrier family")


def validate_carrier_roles() -> None:
    """Contract for APC and IFV as roles on the light tank hull.

    Owner decision 2026-09-11 retired the standalone carrier designer families.
    Every retired tier maps onto the newest light hull tier whose year does not
    exceed it, and the role-exclusive superstructure ladder carries the armour,
    cost and speed the old chassis row used to carry.
    """
    role_text = text(ROLE_CHASSIS_FILE)
    tech_text = text(TECH_DIR / "NSB_armor.txt")
    gfx = text(TANK_ICON_FILE)
    hull_loc = text(MOD / "localisation/english/tank_modules_l_english.yml")
    definitions = module_definitions
    sprites = tank_icon_sprites()

    for family, (archetype, source, role, _token) in sorted(CARRIER_ARCHETYPES.items()):
        brace_balance(source)
        blocks = dict(top_level_blocks(text(source), "equipments"))
        block = blocks.get(archetype)
        if block is None:
            fail(f"{archetype} archetype is missing")
            continue
        for message in carrier_archetype_errors(archetype, block):
            fail(message)
        # Phase 5, 2026-09-12: the legacy carrier rows moved into the role
        # family so one battalion serves both the NSB designer path and the
        # non-NSB legacy path, exactly as `lt_equipment_1..6` already sit in
        # `light_tank_chassis`. The retired archetype is left as an empty shell
        # because roughly 180 MIO, idea and decision entries name it.
        role_members = dict(top_level_blocks(text(ROLE_CHASSIS_FILE), "equipments"))
        legacy = [name for name in role_members if re.fullmatch(rf"{archetype}_\d+", name)]
        if not legacy:
            fail(f"{archetype} rows are missing from the {role} family; non-NSB loses its carriers")
        for name in legacy:
            body = role_members[name]
            if direct_values(body, "archetype") != [role]:
                fail(f"{name} must declare archetype = {role}")
            if direct_values(body, "module_slots"):
                fail(f"legacy row {name} must not declare module slots")
            # Relocation moved these rows off an archetype that supplied their
            # base stats. Each must state its own, or it silently inherits the
            # light tank hull's.
            for stat in ("maximum_speed", "armor_value", "build_cost_ic", "defense", "reliability"):
                if not direct_values(body, stat):
                    fail(f"{name} must state {stat} explicitly after the relocation")
            years = direct_values(body, "year")
            armour = direct_values(body, "armor_value")
            if years and armour:
                for message in carrier_armour_cap_errors(name, int(years[0]), float(armour[0])):
                    fail(message)

        if not re.search(rf"(?m)^\s*{role}\s*=\s*{{", role_text):
            fail(f"carrier role root is missing: {role}")
        roots = dict(top_level_blocks(role_text, "duplicate_archetypes"))
        root = roots.get(role)
        if root is None:
            fail(f"{role} is not declared as a duplicate_archetypes root")
        else:
            # Phase 7: hardness is the one carrier stat the cutover did not
            # preserve, and it cannot come from a module - `for_each` sets it
            # once for every derived tier, so a design cannot drift off it.
            expected = CARRIER_ROLE_HARDNESS[family]
            found = re.search(r"hardness\s*=\s*{\s*set\s*=\s*([\d.]+)", root)
            if not found or abs(float(found.group(1)) - expected) >= 1e-6:
                fail(
                    f"{role} must set hardness = {expected} for the whole family, "
                    f"found {found.group(1) if found else 'none'}"
                )
        for tier in sorted({row[2] for row in CARRIER_LADDERS[family].values()}):
            if not re.search(rf"\b{role}_{tier}\b", tech_text):
                fail(f"{role}_{tier} is not enabled by any technology")

        ladder = sorted(CARRIER_LADDERS[family].items())
        for index, (tier, row) in enumerate(ladder):
            module, technology = row[0], row[1]
            techs = re.findall(rf"(?ms)^\t{technology}\s*=\s*{{.*?^\t}}", tech_text)
            parent = ladder[index - 1][1][0] if index else None
            for message in carrier_module_errors(
                family, tier, row, definitions.get(module), techs[0] if techs else None, parent
            ):
                fail(message)
            hull_armour = LIGHT_HULL_ARMOUR[row[2]]
            year = CARRIER_GENERATION_YEARS[family][tier]
            for message in carrier_armour_cap_errors(
                f"{family} generation {tier}", year, hull_armour + row[3]
            ):
                fail(message)
            if f"GFX_SMI_{module}" not in gfx:
                fail(f"carrier module sprite is missing: GFX_SMI_{module}")
            else:
                texture = sprites.get(f"GFX_SMI_{module}")
                if texture and not (MOD / texture).is_file():
                    fail(f"GFX_SMI_{module} points at a missing texture: {texture}")
            for key in (module, f"{module}_desc"):
                if not re.search(rf'(?m)^\s*{key}:\d*\s+"', hull_loc):
                    fail(f"carrier localisation key is missing: {key}")

    for path in sorted(MOD.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in (".txt", ".yml", ".gui", ".gfx", ".asset", ".json"):
            continue
        for message in carrier_stale_id_errors(
            str(path.relative_to(MOD)), path.read_text(encoding="utf-8", errors="replace")
        ):
            fail(message)

    # Two generations share a light hull tier, and a design name is unique per
    # producer and chassis, so both generations must mount the same
    # superstructure or the same named design would exist twice with different
    # loadouts. The generation that owns the tier supplies the module.
    preset_text = text(MOD / "common/scripted_effects/CWIC_national_tank_presets.txt")
    for family, ladder in sorted(CARRIER_LADDERS.items()):
        owner = {}
        for tier, row in sorted(ladder.items()):
            owner.setdefault(row[2], tier)
        for tier, row in sorted(ladder.items()):
            expected = ladder[owner[row[2]]][0]
            effect = f"cwic_create_national_{family}_chassis_{tier}_variants"
            found = re.findall(rf"(?ms)^{effect}\s*=\s*{{.*?^}}", preset_text)
            if not found:
                continue
            wrong = {name for name in re.findall(r"turret_type_slot = (\w+)", found[0]) if name != expected}
            if wrong:
                fail(f"{effect} mounts {sorted(wrong)}; tier {tier} must mount {expected}")


def validate_marine_carrier() -> None:
    """Phase 6, 2026-09-12: marines ride the APC role family.

    APC uses `flame`; IFV uses `rocket`; `amphibious` remains unspent for a
    future dedicated amphibious mechanized role. The owner ruled for APC-wide
    marine transport instead, which works because a `duplicate_archetypes` root
    is a family a sub-unit's `need` can name, unlike the plain members Finding 15
    ruled out. The five legacy marine rows follow the same relocation phase 5
    used for the 18 legacy carrier rows: they move into the role family stating
    every stat, and the retired archetype stays as an empty shell because MIO,
    idea, focus and country-leader entries name it.
    """
    shell = dict(top_level_blocks(text(EQUIPMENT_DIR / "mechanized_marine.txt"), "equipments"))
    if MARINE_ARCHETYPE not in shell:
        fail(f"{MARINE_ARCHETYPE} archetype is missing")
    stranded = sorted(name for name in shell if name != MARINE_ARCHETYPE)
    if stranded:
        fail(
            f"{MARINE_ARCHETYPE} still declares {stranded}; those rows belong to "
            f"{MARINE_ROLE} or the ids are declared twice"
        )
    rows = dict(top_level_blocks(text(ROLE_CHASSIS_FILE), "equipments"))
    for tier, (year, armour) in sorted(MARINE_ROWS.items()):
        name = f"{MARINE_ARCHETYPE}_{tier}"
        body = rows.get(name)
        if body is None:
            fail(f"{name} is missing from the {MARINE_ROLE} family; marines lose their transport")
            continue
        if direct_values(body, "archetype") != [MARINE_ROLE]:
            fail(f"{name} must declare archetype = {MARINE_ROLE}")
        for stat in (
            "maximum_speed", "armor_value", "build_cost_ic", "defense",
            "breakthrough", "hardness", "reliability",
        ):
            if not direct_values(body, stat):
                fail(f"{name} must state {stat} explicitly after the relocation")
        found = direct_values(body, "armor_value")
        if found and abs(float(found[0]) - armour) >= 1e-6:
            fail(f"{name} must carry armor_value = {armour}, found {found[0]}")
        for message in carrier_armour_cap_errors(name, year, armour):
            fail(message)


def run_carrier_negative_fixtures() -> None:
    """Every half-applied cutover shape must be rejected.

    In memory throughout. The retired APC and IFV fixtures rewrote the real
    equipment files, which corrupted any live `-debug` game and manufactured
    2380 unrelated errors - STATUS.md Finding 8.
    """
    plain = '\tmechanized_equipment = {\n\t\tis_archetype = yes\n\t\ttype = mechanized\n\t}'
    for label, block in (
        ("archetype keeps its designer slots", plain.replace("type = mechanized", "module_slots = { turret_type_slot = { } }\n\t\ttype = mechanized")),
        ("archetype keeps a count limit", plain.replace("type = mechanized", "module_count_limit = { category = tank_smoke count < 2 }\n\t\ttype = mechanized")),
        ("archetype keeps default modules", plain.replace("type = mechanized", "default_modules = { turret_type_slot = apc_open_troop_bay }\n\t\ttype = mechanized")),
        ("archetype stays in the armor domain", plain.replace("type = mechanized", "type = { armor mechanized }")),
    ):
        parsed = dict(top_level_blocks("equipments = {\n" + block + "\n}", "equipments"))
        if not carrier_archetype_errors("mechanized_equipment", parsed["mechanized_equipment"]):
            raise AssertionError(f"carrier archetype contract accepted: {label}")
    if carrier_archetype_errors(
        "mechanized_equipment",
        dict(top_level_blocks("equipments = {\n" + plain + "\n}", "equipments"))["mechanized_equipment"],
    ):
        raise AssertionError("carrier archetype contract rejected the shipped plain archetype")

    row = APC_LADDER[0]
    good = (
        '\t\tcategory = tank_apc_superstructure\n'
        '\t\tallow_equipment_type = flame\n'
        '\t\tadd_stats = {\n\t\t\tbuild_cost_ic = 2.6\n\t\t\tarmor_value = 5\n'
        '\t\t\tmaximum_speed = 4\n\t\t\tdefense = 5\n\t\t\tbreakthrough = -17\n\t\t}\n'
    )
    tech = "enable_equipment_modules = { apc_open_troop_bay }"
    for label, definition, tech_block in (
        ("module loses its armour delta", good.replace("armor_value = 5", "armor_value = 0"), tech),
        ("module loses its cost delta", good.replace("build_cost_ic = 2.6", "build_cost_ic = 0.3"), tech),
        ("module loses its speed delta", good.replace("maximum_speed = 4", "maximum_speed = 0"), tech),
        ("module loses its defense delta", good.replace("defense = 5", "defense = 1"), tech),
        ("module keeps the hull's breakthrough", good.replace("breakthrough = -17", "breakthrough = 0.5"), tech),
        ("module stacks hardness on the role root", good.replace("defense = 5", "defense = 5\n\t\t\thardness = 0.025"), tech),
        ("module multiplies a stat the envelope adds", good + '\t\tmultiply_stats = {\n\t\t\tarmor_value = 0.05\n\t\t}\n', tech),
        ("module drops its role gate", good.replace("allow_equipment_type = flame", "allow_equipment_type = armor"), tech),
        ("technology still enables a retired hull", good, tech + "\n\t\tenable_equipments = { apc_chassis_0 }"),
        ("technology stops unlocking the module", good, "enable_equipment_modules = { apc_firing_ports }"),
    ):
        if not carrier_module_errors("apc", 0, row, definition, tech_block, None):
            raise AssertionError(f"carrier module contract accepted: {label}")
    if not carrier_module_errors("apc", 0, row, None, tech, None):
        raise AssertionError("carrier module contract accepted a missing module")
    # An empty `multiply_stats` block is shipped style on eleven of the sixteen
    # rungs, so the ban is on multiplied values, not on the block.
    empty = carrier_module_errors("apc", 0, row, good + '\t\tmultiply_stats = {\n\t\t}\n', tech, None)
    if empty != carrier_module_errors("apc", 0, row, good, tech, None):
        raise AssertionError("carrier module contract reacted to an empty multiply_stats block")

    # The inversion this cap exists for: the shipped 2005 IFV carried 80 armour
    # against a 2000 medium hull's 70, and nothing reported it.
    if not carrier_armour_cap_errors("fixture", 2005, 80):
        raise AssertionError("carrier armour cap accepted an IFV that out-armours a same-year MBT")
    if carrier_armour_cap_errors("fixture", 2005, 49):
        raise AssertionError("carrier armour cap rejected the repriced 2005 IFV")
    if carrier_armour_cap_errors("fixture", 1947, 28):
        raise AssertionError("carrier armour cap rejected a carrier sitting exactly on the cap")

    for label, body in (
        ("a retired chassis id", "type = apc_chassis_3"),
        ("a retired derived variant", 'variant_name = "ifv_equipment_5"'),
    ):
        if not carrier_stale_id_errors("fixture", body):
            raise AssertionError(f"carrier stale-id contract accepted: {label}")
    for label, body in (
        ("the migrated role id", "type = light_tank_apc_chassis_4"),
        ("the preset effect name", "cwic_create_national_apc_chassis_2_variants = {"),
        ("the starting flag", "set_country_flag = cwic_starting_ifv_chassis_1_created"),
    ):
        if carrier_stale_id_errors("fixture", body):
            raise AssertionError(f"carrier stale-id contract rejected: {label}")


def defined_equipment_ids() -> tuple[set[str], dict[str, str]]:
    """Declared equipment ids, and the role archetypes whose tiers are derived.

    `duplicate_archetypes` roots such as `light_tank_aa_chassis` never appear as
    a declared equipment id, yet the engine derives numbered tiers from the
    archetype they duplicate and accepts `light_tank_aa_chassis_1` in a grant.
    The mapping is root to duplicated archetype, so a derived id can be bounded
    to the tiers its parent family actually declares instead of accepting any
    number.
    """
    declared: set[str] = set()
    derived_roots: dict[str, str] = {}
    for path in sorted(EQUIPMENT_DIR.rglob("*.txt")):
        value = text(path)
        declared.update(name for name, _ in top_level_blocks(value, "equipments"))
        for name, block in top_level_blocks(value, "duplicate_archetypes"):
            parent = direct_values(block, "archetype")
            if parent:
                derived_roots[name] = parent[0]
    return declared, derived_roots


def stockpile_grants(value: str) -> list[tuple[int, str]]:
    """Balanced `add_equipment_to_stockpile` blocks with their 1-based line."""
    return [
        (value.count("\n", 0, offset) + 1, block)
        for offset, block in located_keyed_blocks(value, "add_equipment_to_stockpile")
    ]


def validate_stockpile_grants(scan_root: Path = MOD) -> None:
    """Every stockpile grant the game loads must actually award its equipment.

    Two silent-failure shapes are pinned. A `creator` key is rejected by the
    effect parser, so the whole grant is dropped. A type that resolves to no
    equipment id logs `invalid database object` and awards nothing; a transposed
    id such as `heavy_mechanized_equipment_3` and a technology id used as
    equipment such as `mp_uav_1` both land here.

    The scan covers the whole mod, not just `history/`: two thirds of the grants
    live in `common/national_focus/` and `common/decisions/`, and a blind spot
    there is where this defect class would silently return.
    """
    declared, derived_roots = defined_equipment_ids()
    if not declared:
        fail("no equipment ids were parsed; the stockpile contract cannot run")
        return
    for path in sorted(scan_root.rglob("*.txt")):
        value = code_only(text(path))
        if "add_equipment_to_stockpile" not in value:
            continue
        location = path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name
        for line, block in stockpile_grants(value):
            for key in STOCKPILE_REJECTED_KEYS:
                if re.search(rf"\b{key}\s*=", block):
                    fail(
                        f"{location}:{line}: add_equipment_to_stockpile does not accept "
                        f"`{key}`; use `producer`"
                    )
            for granted in re.findall(r"\btype\s*=\s*([A-Za-z_][A-Za-z0-9_]*)", block):
                if granted in declared or granted in STOCKPILE_TYPE_EXCEPTIONS:
                    continue
                root, _, tier = granted.rpartition("_")
                parent = derived_roots.get(root) if tier.isdigit() else None
                if parent and f"{parent}_{tier}" in declared:
                    continue
                fail(f"{location}:{line}: stockpile grant names undefined equipment {granted}")


def run_stockpile_negative_fixtures() -> None:
    """The stockpile contract must reject both silent-failure shapes."""
    fixtures = (
        (
            "creator key on a stockpile grant",
            "add_equipment_to_stockpile = { type = infantry_equipment_1 amount = 1 creator = SOV }",
        ),
        (
            "transposed equipment id",
            "add_equipment_to_stockpile = { type = heavy_mechanized_equipment_3 amount = 1 producer = SOV }",
        ),
        (
            "technology id used as equipment",
            "add_equipment_to_stockpile = { type = nsb_apc_hulls0 amount = 1 producer = SOV }",
        ),
    )
    with tempfile.TemporaryDirectory() as directory:
        for label, grant in fixtures:
            probe = Path(directory) / "fixture.txt"
            probe.write_text(f"instant_effect = {{\n\t{grant}\n}}\n", encoding="utf-8", newline="")
            previous = len(errors)
            try:
                validate_stockpile_grants(Path(directory))
                rejected = len(errors) > previous
            finally:
                del errors[previous:]
                probe.unlink()
            if not rejected:
                raise AssertionError(f"stockpile contract accepted a broken grant: {label}")
        probe = Path(directory) / "fixture.txt"
        probe.write_text(
            "instant_effect = {\n"
            "\tadd_equipment_to_stockpile = { type = light_tank_aa_chassis_1 amount = 1 producer = SOV }\n"
            "}\n",
            encoding="utf-8",
            newline="",
        )
        previous = len(errors)
        try:
            validate_stockpile_grants(Path(directory))
            rejected = len(errors) > previous
        finally:
            del errors[previous:]
        if rejected:
            raise AssertionError("stockpile contract rejected a valid derived role tier")


# As of 2026-09-13, 2,008 of 2,349 armour entity aliases named deleted
# sub-units and nothing detected it: a missing entity alias produces no log line
# and the game silently renders its default mesh instead.
# Clone targets are checked against mod-declared entities, excluding this alias
# file itself. Including the alias file creates a self-reference trap: its alias
# outputs are `name` declarations that can make dangling clones look valid.
ENTITY_ALIAS_DIR = MOD / "gfx/entities"
ENTITY_ALIAS_FILE = ENTITY_ALIAS_DIR / "zz_CWIC_armor_entity_aliases.asset"
ENTITY_ALIAS_NAME = re.compile(
    r"^(?P<tag>[A-Z]{3})_(?P<sub_unit>[a-z0-9_]+)_(?P<visual_level>[0-9]+)_entity$"
)


def validate_entity_alias_contract() -> None:
    """Require aliases to cover armour-hull sub-units consistently."""
    alias_relative = ENTITY_ALIAS_FILE.relative_to(ROOT)
    misplaced = sorted(
        path.name
        for path in ENTITY_ALIAS_DIR.glob("*armor_entity_aliases.asset")
        if path.is_file()
        and path.name.endswith("CWIC_armor_entity_aliases.asset")
        and path.name != ENTITY_ALIAS_FILE.name
    )
    for filename in misplaced:
        fail(f"entity alias file must retain the zz_ prefix: {filename}")
    if not ENTITY_ALIAS_FILE.is_file():
        fail(f"missing required file: {alias_relative}")
        return

    raw = ENTITY_ALIAS_FILE.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        fail("entity alias file must not contain a UTF-8 BOM")
    alias_code = raw.decode("utf-8", errors="replace")
    alias_blocks = keyed_blocks(alias_code, "entity")
    if not alias_blocks:
        fail(f"entity alias file declares no aliases: {alias_relative}")
        return

    # Derive valid alias tokens from live definitions; a static allowlist would
    # freeze the set as new hull-consuming sub-units gain aliases.
    declared_sub_units: set[str] = set()
    armour_hull_sub_units: set[str] = set()
    armour_hull_prefixes = (
        "light_tank_",
        "medium_tank_",
        "heavy_tank_",
        "mechanized_equipment",
        "mechanized_heavy_equipment",
        "mechanized_marine_equipment",
    )
    for path in sorted((MOD / "common/units").glob("*.txt")):
        for name, block in top_level_blocks(code_only(text(path)), "sub_units"):
            declared_sub_units.add(name)
            equipment_ids = {
                equipment
                for need in keyed_blocks(block, "need")
                for equipment in re.findall(r"\b([A-Za-z0-9_]+)\s*=", need)
            }
            if any(
                equipment.startswith(armour_hull_prefixes)
                for equipment in equipment_ids
            ):
                armour_hull_sub_units.add(name)
    if not declared_sub_units:
        fail("no sub-unit declarations found under common/units/*.txt")
    # Vanilla sub-units this mod inherits without shadowing. common/units/
    # sp_artillery_brigade.txt, tank_destroyer_brigade.txt and sp_anti-air_brigade.txt
    # are vanilla files the mod never replaces, so these brigades are live in the
    # loaded game even though the convergence removed the mod's own role brigades.
    # The engine builds its equipment graphic database from live sub-units, so each
    # needs <TAG>_<sub_unit>_<level>_entity or it logs equipment_model_util.cpp:76
    # "includes invalid entity" and the default model entry is broken - which is why
    # a correct model had to be chosen by hand. Declaring them here is the fix, so
    # they are legal alias tokens despite not being declared under the mod's
    # common/units. Their hulls are all mod-declared role chassis.
    vanilla_inherited_sub_units = {
        "airborne_light_armor",
        "heavy_sp_artillery_brigade",
        "light_sp_anti_air_brigade",
        "light_sp_anti_air_support",
        "light_sp_artillery_brigade",
        "light_tank_destroyer_brigade",
        "light_tank_destroyer_support",
        "light_tank_recon",
        "medium_sp_artillery_brigade",
        "medium_tank_destroyer_brigade",
        "medium_tank_destroyer_support",
    }
    declared_sub_units |= vanilla_inherited_sub_units
    armour_hull_sub_units |= vanilla_inherited_sub_units

    # Coverage levels that predate this rework, counted as alias-or-native across
    # every source. They are not uniform and never were: some sub-units are covered
    # for more TAGs than the alias file itself names, because per-country entities
    # exist for countries that need no alias. Pinning the exact counts means partial
    # coverage cannot erode further and any improvement forces a deliberate update.
    # Shrinking this map is content work with an owner.
    legacy_tag_counts = {
        "armored_infantry": 57,
        "atgm_carrier": 20,
        "heavy_armor": 29,
        "heavy_sp_artillery": 29,
        "heavy_tank_destroyer_brigade": 16,
        "light_armor": 32,
        "light_sp_artillery": 20,
        "mechanized_airborne": 57,
        "mechanized_infantry": 44,
        "mechanized_marine": 57,
        "medium_sp_anti_air_brigade": 39,
        "spaag": 32,
        "tank_destroyer": 39,
    }

    declared_entities: set[str] = set()
    for path in sorted(ENTITY_ALIAS_DIR.glob("*.asset")):
        if path == ENTITY_ALIAS_FILE:
            continue
        for block in keyed_blocks(text(path), "entity"):
            declared_entities.update(
                top_level_quoted_values(block, "name")
            )

    # Coverage is alias-or-native. Several sub-units - armored_infantry,
    # mechanized_airborne, mechanized_marine - already have per-country entities in
    # the <TAG>_unit.asset files, so they need no alias. This file carries the zz_
    # prefix and loads last, so aliasing one of those names would replace a national
    # model with a generic one; native_overrides pins the pre-existing overrides so
    # no new one can slip in.
    native_levels: dict[tuple[str, str], set[int]] = {}
    for entity_name in declared_entities:
        parsed = ENTITY_ALIAS_NAME.fullmatch(entity_name)
        if parsed and parsed["sub_unit"] in armour_hull_sub_units:
            native_levels.setdefault(
                (parsed["tag"], parsed["sub_unit"]), set()
            ).add(int(parsed["visual_level"]))
    # 140 aliases deliberately shadow a native entity; the zz_ prefix makes this
    # file win. That is pre-existing legacy behaviour, pinned so a new override -
    # which would silently replace a national model with a generic one - fails.
    native_overrides = 140

    alias_tags: set[str] = set()
    alias_levels: dict[tuple[str, str], list[int]] = {}

    for number, block in enumerate(alias_blocks, 1):
        names = top_level_quoted_values(block, "name")
        clones = top_level_quoted_values(block, "clone")
        if len(names) != 1:
            fail(f"entity alias block {number} must declare exactly one name")
            continue
        if len(clones) != 1:
            fail(f"entity alias block {number} must declare exactly one clone")
        elif clones[0] not in declared_entities:
            fail(f"entity alias {names[0]} clones undeclared entity: {clones[0]}")
        name = names[0]
        match = ENTITY_ALIAS_NAME.fullmatch(name)
        if not match:
            fail(f"entity alias name has invalid shape: {name}")
            continue
        token = match["sub_unit"]
        if token not in declared_sub_units:
            fail(f"entity alias {name} names undeclared sub-unit: {token}")
            continue
        if token not in armour_hull_sub_units:
            fail(
                f"entity alias {name} names non-armour-hull sub-unit: {token}"
            )
            continue
        tag = match["tag"]
        alias_tags.add(tag)
        alias_levels.setdefault((tag, token), []).append(
            int(match["visual_level"])
        )
    overrides = sum(
        len(set(levels) & native_levels.get(pair, set()))
        for pair, levels in alias_levels.items()
    )
    if overrides != native_overrides:
        fail(
            f"entity alias overrides of native entities changed: expected "
            f"{native_overrides}, found {overrides}"
        )
    covered = {pair for pair in alias_levels} | set(native_levels)
    covered_sub_units = {sub_unit for _, sub_unit in covered}
    for sub_unit in sorted(armour_hull_sub_units - covered_sub_units):
        fail(f"no entity of any kind covers {sub_unit}")
    for sub_unit in sorted(armour_hull_sub_units & covered_sub_units):
        tags = {tag for tag, token in covered if token == sub_unit}
        expected_tag_count = legacy_tag_counts.get(sub_unit)
        if expected_tag_count is not None:
            if len(tags) != expected_tag_count:
                fail(
                    f"entity alias legacy coverage for {sub_unit} changed: "
                    f"expected {expected_tag_count} TAGs, found {len(tags)}"
                )
            continue
        missing_tag_count = len(alias_tags - tags)
        if missing_tag_count:
            fail(
                f"entity alias table omits {missing_tag_count} TAG aliases for "
                f"{sub_unit}"
            )
    # Legacy native coverage is genuinely patchy - TUR_armored_infantry and many
    # others declare only some levels - so contiguity is not an invariant of
    # pre-existing content. It IS an invariant of the sub-units this alias file
    # owns outright, where every level is generated from the hull's ceiling.
    alias_owned = {
        sub_unit
        for _, sub_unit in alias_levels
        if not any(token == sub_unit for _, token in native_levels)
    }
    for pair in sorted(alias_levels):
        levels = sorted(alias_levels[pair])
        if len(levels) != len(set(levels)):
            fail(f"entity alias {pair[0]}_{pair[1]} declares a duplicate level")
        elif pair[1] in alias_owned and levels != list(range(len(levels))):
            fail(
                f"entity alias {pair[0]}_{pair[1]} has non-contiguous visual levels"
            )


# Measured 2026-09-13: five armour archetypes named a `picture` value that no
# `GFX_<value>_medium` sprite registers, in this mod or in the base game, and the
# engine logs nothing for it - the production icon is simply wrong. The tank rows
# were renamed onto sprites the base game already registers. The two mechanized
# rows are the other case: `gfx/interface/archetype_mechanized_equipment.dds` and
# `archetype_mechanized_heavy_equipment.dds` were shipped and never registered, so
# the sprites are registered in `cwic_tank_rework_icons.gfx` and the picture values
# keep their own art. `mechanized_marine_equipment` has no texture of its own and
# follows vanilla onto the motorized picture.
ARMOUR_ARCHETYPE_PICTURES = {
    "light_tank_chassis": "archetype_light_tank_equipment",
    "medium_tank_chassis": "archetype_medium_tank_equipment",
    "heavy_tank_chassis": "archetype_heavy_tank_equipment",
    "lt_equipment": "archetype_light_tank_equipment",
    "mbt_equipment": "archetype_medium_tank_equipment",
    "ht_equipment": "archetype_heavy_tank_equipment",
    "sht_equipment": "archetype_super_heavy_tank_equipment",
    "mechanized_equipment": "archetype_mechanized_equipment",
    "mechanized_heavy_equipment": "archetype_mechanized_heavy_equipment",
    "mechanized_marine_equipment": "archetype_motorized_equipment",
    # Owner ruling 2026-09-14: the production icon follows the equipment type category, and
    # APC/IFV are typed flame/rocket because no mechanized category token exists, so they
    # otherwise inherit the tank hull art. No flame or rocket sprite key exists to override,
    # so the archetype picture carries the carrier art.
    "light_tank_apc_chassis": "archetype_mechanized_equipment",
    "medium_tank_apc_chassis": "archetype_mechanized_equipment",
    "light_tank_ifv_chassis": "archetype_mechanized_heavy_equipment",
    "medium_tank_ifv_chassis": "archetype_mechanized_heavy_equipment",
}
# Registered by the base game in `interface/*.gfx`. Kept as a literal set because
# the validator must not depend on a Steam install path being present.
VANILLA_ARCHETYPE_SPRITES = {
    "archetype_light_tank_equipment",
    "archetype_medium_tank_equipment",
    "archetype_heavy_tank_equipment",
    "archetype_super_heavy_tank_equipment",
    "archetype_modern_tank_equipment",
    "archetype_motorized_equipment",
    "archetype_motorized_rocket_equipment",
}


# NSB's designer rows otherwise sit beside their legacy counterparts in the
# production tab, allowing both versions to be built on the same DLC profile.
LEGACY_ARMOUR_DLC_GATES = {
    EQUIPMENT_DIR / "tank_light.txt": tuple(f"lt_equipment_{tier}" for tier in range(1, 7)),
    EQUIPMENT_DIR / "tank_medium.txt": tuple(f"mbt_equipment_{tier}" for tier in range(10)),
    EQUIPMENT_DIR / "tank_heavy.txt": tuple(f"ht_equipment_{tier}" for tier in range(1, 6)),
    ROLE_CHASSIS_FILE: (
        *(f"mechanized_equipment_{tier}" for tier in range(3, 11)),
        *(f"mechanized_heavy_equipment_{tier}" for tier in range(1, 9)),
        # Gating these became safe only once the convergence landed: their
        # battalions now consume role families that hold designer members, so an
        # NSB template is no longer stranded when the legacy row is hidden.
        *(f"spaag_equipment_{tier}" for tier in range(1, 6)),
        *(f"sp_artillery_equipment_{tier}" for tier in range(1, 6)),
        *(f"light_sp_artillery_equipment_{tier}" for tier in range(1, 6)),
        *(f"heavy_sp_artillery_equipment_{tier}" for tier in range(1, 6)),
        *(f"medium_tank_destroyer_equipment_{tier}" for tier in range(1, 6)),
        *(f"atgm_carrier_equipment_{tier}" for tier in range(5)),
    ),
}
# Pre-designer WWII rows have no designer replacement; marine rows stay legacy
# because marines ride any carrier.
LEGACY_ARMOUR_UNGATED_EXCEPTIONS = frozenset(
    {
        "mechanized_equipment_1",
        "mechanized_equipment_2",
        *(f"mechanized_marine_equipment_{tier}" for tier in range(1, 6)),
    }
)

# Vanilla declares the designer blueprint overlay sprites - `GFX_TC_<chassis>` and
# `GFX_TM_<chassis>_<slot>` - only for its own role chassis: aa, artillery and
# destroyer. The carrier roles this mod invented have blueprint `.gui` files that
# reference the same sprite shape, and nothing declared them, so opening an APC or
# IFV designer logged six `Could not find sprite type` lines per open. The engine
# renders the window anyway, which is why owner QA passed three times before the
# log was read.
CARRIER_BLUEPRINT_FAMILIES = (
    "light_tank_apc_chassis",
    "light_tank_ifv_chassis",
    "medium_tank_apc_chassis",
    "medium_tank_ifv_chassis",
)
CARRIER_BLUEPRINT_SLOTS = (
    "armor_type_slot",
    "engine_type_slot",
    "main_armament_slot",
    "suspension_type_slot",
    "turret_type_slot",
)


def validate_carrier_blueprint_sprites() -> None:
    """Mod-invented role chassis must declare their own blueprint overlay sprites."""
    declared: set[str] = set()
    for path in sorted((MOD / "interface").rglob("*.gfx")):
        declared.update(re.findall(r'name\s*=\s*"(GFX_T[CM]_[A-Za-z0-9_]+)"', text(path)))
    for family in CARRIER_BLUEPRINT_FAMILIES:
        wanted = [f"GFX_TC_{family}"]
        wanted += [f"GFX_TM_{family}_{slot}" for slot in CARRIER_BLUEPRINT_SLOTS]
        for sprite in wanted:
            if sprite not in declared:
                fail(
                    f"designer blueprint sprite {sprite} is not declared; opening the "
                    "designer logs 'Could not find sprite type'"
                )


validate_carrier_blueprint_sprites()


def validate_legacy_armour_dlc_gates() -> None:
    """Keep legacy armour out of NSB production without orphaning non-NSB rows."""
    equipment_blocks = {
        path: dict(top_level_blocks(code_only(text(path)), "equipments"))
        for path in LEGACY_ARMOUR_DLC_GATES
    }
    for path in (
        CHASSIS_FILE,
        ROLE_CHASSIS_FILE,
        MECHANIZED_FILE,
        HEAVY_MECHANIZED_FILE,
        EQUIPMENT_DIR / "mechanized_marine.txt",
    ):
        equipment_blocks.setdefault(
            path, dict(top_level_blocks(code_only(text(path)), "equipments"))
        )

    gates: dict[tuple[Path, str], list[str]] = {}
    for path, blocks in equipment_blocks.items():
        for equipment, block in blocks.items():
            row_gates = top_level_named_blocks(
                block, "can_be_produced", f"{path.name}:{equipment}"
            )
            gates[path, equipment] = row_gates
            if len(row_gates) > 1:
                fail(
                    f"legacy armour row {path.name}:{equipment} has duplicate "
                    "can_be_produced blocks"
                )
            # The three designer hulls carry a deliberately empty
            # `can_be_produced = { }`, which is not a gate. Only a DLC predicate
            # on an archetype would hide a whole family from a profile.
            dlc_gates = [gate for gate in row_gates if "has_dlc" in gate]
            if re.search(r"\bis_archetype\s*=\s*yes\b", block) and dlc_gates:
                fail(
                    f"legacy armour archetype {path.name}:{equipment} must not "
                    "gate production by DLC"
                )
            if equipment in LEGACY_ARMOUR_UNGATED_EXCEPTIONS and dlc_gates:
                fail(
                    f"legacy armour exception {path.name}:{equipment} must not "
                    "gate production by DLC"
                )

    for path, expected_rows in LEGACY_ARMOUR_DLC_GATES.items():
        blocks = equipment_blocks[path]
        for equipment in expected_rows:
            block = blocks.get(equipment)
            if block is None:
                fail(f"legacy armour row {path.name}:{equipment} is missing")
                continue
            row_gates = gates[path, equipment]
            if not row_gates:
                fail(
                    f"legacy armour row {path.name}:{equipment} must declare "
                    "can_be_produced"
                )
                continue
            if len(row_gates) > 1:
                continue
            gate = row_gates[0]
            if (
                not re.search(r"\bNOT\s*=\s*\{", gate)
                or not re.search(r'\bhas_dlc\s*=\s*"No Step Back"', gate)
            ):
                fail(
                    f"legacy armour row {path.name}:{equipment} must exclude "
                    "No Step Back from production"
                )


def validate_armour_archetype_pictures() -> None:
    """Every armour archetype picture must resolve to a registered sprite.

    This failure mode is silent: an unregistered `picture` value produces no
    `error.log` line, so only a static check catches it.
    """
    files = [
        CHASSIS_FILE,
        # The role families (APC, IFV, and the artillery/AA/TD roots) live here, and
        # the APC/IFV pictures carry their carrier art, so this file must be scanned.
        MOD / "common/units/equipment/x_tank_chassis.txt",
        MOD / "common/units/equipment/tank_light.txt",
        MOD / "common/units/equipment/tank_medium.txt",
        MOD / "common/units/equipment/tank_heavy.txt",
        MOD / "common/units/equipment/tank_super_heavy.txt",
        MECHANIZED_FILE,
        HEAVY_MECHANIZED_FILE,
        MOD / "common/units/equipment/mechanized_marine.txt",
    ]
    mod_sprites = set()
    for path in sorted((MOD / "interface").rglob("*.gfx")):
        mod_sprites.update(
            re.findall(r'\bname\s*=\s*"GFX_([A-Za-z0-9_]+)"', text(path))
        )
    seen: dict[str, str] = {}
    for path in files:
        code = code_only(text(path))
        for family in ARMOUR_ARCHETYPE_PICTURES:
            if family in seen:
                continue
            # Indentation is inconsistent across these files - `mechanized_heavy.txt`
            # opens its archetype at column 0 - so the block is bounded by brace
            # depth rather than by indent.
            opener = re.search(
                rf"(?m)^[ \t]*{re.escape(family)}\s*=\s*\{{", code
            )
            if not opener:
                continue
            depth = 0
            for index in range(opener.end() - 1, len(code)):
                if code[index] == "{":
                    depth += 1
                elif code[index] == "}":
                    depth -= 1
                    if depth == 0:
                        break
            block = code[opener.end() : index]
            picture = re.search(r"\bpicture\s*=\s*([A-Za-z0-9_]+)", block)
            if picture:
                seen[family] = picture.group(1)
    for family, expected in sorted(ARMOUR_ARCHETYPE_PICTURES.items()):
        actual = seen.get(family)
        if actual is None:
            fail(f"armour family {family} declares no picture")
            continue
        if actual != expected:
            fail(
                f"armour family {family} picture is {actual}, expected {expected}"
            )
        if (
            f"{actual}_medium" not in mod_sprites
            and actual not in VANILLA_ARCHETYPE_SPRITES
        ):
            fail(
                f"armour family {family} picture {actual} has no registered "
                "GFX_<picture>_medium sprite - the production icon is silently wrong"
            )


validate_entity_alias_contract()
validate_legacy_armour_dlc_gates()
validate_armour_archetype_pictures()
validate_carrier_bookmarks()
validate_carrier_roles()
validate_carrier_battalions()
validate_research_armour_naming()
validate_ai_templates()
validate_marine_carrier()
validate_designer_window_coverage()
stockpile_grant_count = sum(
    len(stockpile_grants(code_only(text(path))))
    for path in sorted(MOD.rglob("*.txt"))
)
validate_stockpile_grants()
if "--tank-self-test" in sys.argv:
    run_carrier_negative_fixtures()
    run_stockpile_negative_fixtures()

balance_report = tank_balance_report() if "--tank-balance-report" in sys.argv else ""
module_balance_report = (
    tank_module_balance_report() if "--tank-module-balance-report" in sys.argv else ""
)
envelope_report = tank_envelope_report() if "--tank-envelope-report" in sys.argv else ""

if errors:
    print("Military rework validation failed:")
    for message in errors:
        print(f"- {message}")
    sys.exit(1)

print(
    "Military rework validation passed: "
    f"{len(technology_set)} technologies, {len(module_ids)} tank modules, "
    f"{len(expected_types)} historical tank designs, {len(oob_refs)} generic bookmark variants, "
    f"{len(NATIONAL_PRESETS) + len(CARRIER_PRESETS)} national presets "
    f"and {versioned_oob_requests} named OOB requests across "
    f"{len(oob_files_with_tanks)} NSB OOBs, {history_bootstrap_sites} country-history "
    f"bootstrap sites, {stockpile_grant_count} stockpile grants, "
    f"{len(APC_LADDER) + len(IFV_LADDER)} carrier superstructure rungs, "
    f"{len(MARINE_ROWS)} relocated marine rows, and "
    f"{TANK_DESIGNER_POSITIONS} designer slots checked."
)
if balance_report:
    print(balance_report)
if module_balance_report:
    print(module_balance_report)
if envelope_report:
    print(envelope_report)
