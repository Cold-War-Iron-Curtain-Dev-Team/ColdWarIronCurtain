import json, os, subprocess, hashlib, glob
import numpy as np
from PIL import Image, ImageDraw

ROOT = "/home/zom/Projects/ColdWarIronCurtain/Cold War Iron Curtain"
OUT = ROOT + "/gfx/interface/doctrines/cwic"
W = os.path.dirname(os.path.abspath(__file__))
BANNERS = ROOT + "/gfx/interface/doctrines"
inv = json.load(open(W + "/inv.json"))
srcs = json.load(open(W + "/srcfiles.json"))

SCHOOLS = ["forward_defense", "deep_battle", "peoples_war", "intervention_pacification",
           "preemptive_maneuver", "total_national_defense", "revolutionary_insurgency"]
LAND_TRACKS = ["infantry", "combat_support", "armor", "operations"]
POOLS = {
    "forward_defense": ["NATO_1940s", "NATO_1950s", "NATO_1960s", "NATO_1970s", "NATO_1980s", "NATO_1990s",
                        "SADF_1960s", "SADF_1970s", "SADF_1980s", "SADF_1990s"],
    "deep_battle": ["Warsaw_1940s", "Warsaw_1950s", "Warsaw_1960s", "Warsaw_1970s", "Warsaw_1980s", "Warsaw_1990s",
                    "dprk_1960s", "dprk_1970s", "dprk_1980s", "dprk_1990s"],
    "peoples_war": ["prc_1940s", "prc_1950s", "prc_1960s", "prc_1970s", "prc_1980s", "prc_1990s",
                    "Maoist_1960s", "Maoist_1970s", "Maoist_1980s", "Maoist_1990s"],
    "intervention_pacification": ["france_1940s", "france_1950s", "france_1960s", "france_1970s", "france_1980s", "france_1990s"],
    "preemptive_maneuver": ["israel_1940s", "israel_1950s", "israel_1960s", "israel_1970s", "israel_1980s", "israel_1990s"],
    "total_national_defense": ["Yugoslav_1940s", "Yugoslav_1950s", "Yugoslav_1960s", "Yugoslav_1970s", "Yugoslav_1980s", "Yugoslav_1990s",
                               "non_aligned_1940s", "non_aligned_1950s", "non_aligned_1960s", "non_aligned_1970s", "non_aligned_1980s", "non_aligned_1990s",
                               "himalayan_1960s", "himalayan_1970s", "himalayan_1980s", "himalayan_1990s", "iran_1980s", "iran_1990s"],
    "revolutionary_insurgency": ["Foco_1960s", "Foco_1970s", "Foco_1980s", "Foco_1990s", "Insurgent_1940s", "Insurgent_1950s",
                                 "Hybrid_1960s", "Hybrid_1970s", "Hybrid_1980s", "Hybrid_1990s", "Islamist_1960s", "Islamist_1970s",
                                 "Islamist_1980s", "Islamist_1990s", "Islamist_Transnational_1990s", "cuba_1970s", "cuba_1980s", "cuba_1990s"],
}
# track background banner choice per land track (pool-unique within each school)
TRACK_BANNER = {
    "forward_defense": {"infantry": "NATO_1940s", "combat_support": "NATO_1960s", "armor": "NATO_1990s", "operations": "SADF_1970s"},
    "deep_battle": {"infantry": "dprk_1990s", "combat_support": "dprk_1970s", "armor": "Warsaw_1960s", "operations": "Warsaw_1990s"},
    "peoples_war": {"infantry": "prc_1940s", "combat_support": "Maoist_1970s", "armor": "prc_1970s", "operations": "prc_1940s"},
    "intervention_pacification": {"infantry": "france_1960s", "combat_support": "france_1950s", "armor": "france_1970s", "operations": "france_1940s"},
    "preemptive_maneuver": {"infantry": "israel_1940s", "combat_support": "israel_1960s", "armor": "israel_1970s", "operations": "israel_1950s"},
    "total_national_defense": {"infantry": "Yugoslav_1940s", "combat_support": "himalayan_1970s", "armor": "non_aligned_1970s", "operations": "iran_1990s"},
    "revolutionary_insurgency": {"infantry": "Hybrid_1960s", "combat_support": "Islamist_1980s", "armor": "cuba_1980s", "operations": "Insurgent_1950s"},
}
L, R = 0.15, 0.85
TRACK_BANNER_ERA = {
    2: {
        "forward_defense": {"infantry": ("SADF_1960s",), "combat_support": ("NATO_1970s",), "armor": ("NATO_1960s", R, 1.35), "operations": ("NATO_1950s",)},
        "deep_battle": {"infantry": ("dprk_1960s",), "combat_support": ("Warsaw_1970s",), "armor": ("Warsaw_1950s",), "operations": ("Warsaw_1960s", R, 1.35)},
        "peoples_war": {"infantry": ("Maoist_1960s",), "combat_support": ("prc_1970s", R, 1.35), "armor": ("prc_1970s", R, 1.35), "operations": ("prc_1950s",)},
        "intervention_pacification": {"infantry": ("france_1960s", L, 1.5), "combat_support": ("france_1950s", R, 1.5), "armor": ("france_1970s", R, 1.5), "operations": ("france_1940s", L, 1.5)},
        "preemptive_maneuver": {"infantry": ("israel_1960s", L, 1.5), "combat_support": ("israel_1970s", R, 1.5), "armor": ("israel_1950s", R, 1.5), "operations": ("israel_1940s", L, 1.5)},
        "total_national_defense": {"infantry": ("Yugoslav_1960s",), "combat_support": ("himalayan_1960s",), "armor": ("non_aligned_1960s",), "operations": ("Yugoslav_1970s",)},
        "revolutionary_insurgency": {"infantry": ("Foco_1960s",), "combat_support": ("Islamist_1970s",), "armor": ("cuba_1970s",), "operations": ("Hybrid_1970s",)},
    },
    3: {
        "forward_defense": {"infantry": ("NATO_1980s",), "combat_support": ("SADF_1980s",), "armor": ("NATO_1990s", L, 1.35), "operations": ("SADF_1990s",)},
        "deep_battle": {"infantry": ("dprk_1980s",), "combat_support": ("Warsaw_1980s",), "armor": ("Warsaw_1990s", L, 1.35), "operations": ("Warsaw_1940s",)},
        "peoples_war": {"infantry": ("Maoist_1990s",), "combat_support": ("prc_1980s",), "armor": ("prc_1990s",), "operations": ("Maoist_1980s", L, 1.35)},
        "intervention_pacification": {"infantry": ("france_1980s",), "combat_support": ("france_1990s",), "armor": ("france_1980s", L, 1.5, 0.0), "operations": ("france_1990s", R, 1.35)},
        "preemptive_maneuver": {"infantry": ("israel_1980s",), "combat_support": ("israel_1990s",), "armor": ("israel_1980s", L, 1.5, 0.0), "operations": ("israel_1990s", R, 1.35)},
        "total_national_defense": {"infantry": ("Yugoslav_1980s",), "combat_support": ("himalayan_1980s",), "armor": ("non_aligned_1980s",), "operations": ("iran_1980s",)},
        "revolutionary_insurgency": {"infantry": ("Foco_1980s",), "combat_support": ("Islamist_1990s",), "armor": ("cuba_1990s",), "operations": ("Hybrid_1990s",)},
    },
}
GRAND_BANNER = {
    "forward_defense": "NATO_1960s", "deep_battle": "Warsaw_1960s", "peoples_war": "prc_1960s",
    "intervention_pacification": "france_1960s", "preemptive_maneuver": "israel_1970s",
    "total_national_defense": "Yugoslav_1960s", "revolutionary_insurgency": "Foco_1960s",
}
NAVAL_AIR_SF_TRACKS = {
    "capital_ships": "GFX_fleet_in_being_bg", "carriers": "GFX_base_strike_bg", "screens": "GFX_screens_bg",
    "submarines": "GFX_trade_interdiction_bg", "fighter_aircraft": "GFX_air_superiority_bg",
    "strike_aircraft": "GFX_battlefield_destruction_bg", "medium_aircraft": "GFX_operational_destruction_bg",
    "heavy_aircraft": "GFX_strategic_destruction_bg", "special_forces_first": "GFX_paratroopers_bg",
    "special_forces_second": "GFX_marine_bg",
}
NAVAL_AIR_SF_GRAND = {}
LEGACY_MAP = {
    "cw_covering_force_screen": "nato_1940s_forward_deterrence_planning",
    "cw_panzergrenadier_defense": "nato_1940s_armored_infantry_coordination",
    "cw_urban_terrain_defense": "nato_1960s_counterinsurgency_adaptation_framework",
    "cw_tactical_air_control": "nato_1970s_air_land_coordination_framework",
    "cw_atgm_screening_belts": "nato_1980s_precision_and_maneuver_synergy",
    "cw_follow_on_forces_attack": "nato_1980s_deep_attack_integration",
    "cw_hull_down_ambush": "nato_1950s_dispersed_maneuver_formations",
    "cw_cross_attached_task_forces": "nato_1990s_cjtf_joint_task_force_command",
    "cw_heavy_corps_gunnery": "nato_1950s_pentomic_battle_group_structure",
    "cw_forward_strategy": "nato_1940s_joint_operational_planning_staffs",
    "cw_active_defense": "nato_1970s_active_defense_posture",
    "cw_mechanized_infantry_integration": "nato_1970s_maneuver_warfare_emphasis",
    "cw_airmobile_infantry": "nato_1960s_helicopter_air_mobility_integration",
    "cw_rapid_action_force": "nato_1980s_rapid_maneuver_brigades",
    "cw_light_infantry_divisions": "nato_1960s_road_division_structure",
    "cw_dismounted_atgm_teams": "nato_1990s_joint_precision_campaigning",
    "cw_combined_arms_restoration": "nato_1960s_transitional_combined_arms_cohesion",
    "cw_combined_arms_battalions": "nato_1940s_integrated_arms_reorganization",
    "cw_mbt_maneuver_groups": "nato_1970s_unified_operational_logistics_backbone",
    "cw_tactical_nuclear_fires": "nato_1950s_tactical_nuclear_fire_planning",
    "cw_reconnaissance_strike_complex": "nato_1980s_reconnaissance_strike_coordination",
    "cw_electronic_warfare_support": "nato_1970s_integrated_air_defense_support",
    "cw_army_aviation": "nato_1990s_air_mobile_expeditionary_brigades",
    "cw_airland_battle": "nato_1970s_airland_battle_preparations",
    "cw_flexible_response_operations": "nato_1960s_flexible_response_doctrine",
    "cw_deep_strike_operations": "nato_1980s_joint_operational_synchronization",
    "cw_mobile_counterattack": "nato_1990s_networked_warfare_continuum",
    "cw_massed_artillery_fires": "nato_1950s_atomic_battlefield_readiness",
    "cw_fortress_belt_defense": "iran_1980s_forward_defense_in_depth",
    "cw_citizen_army_mobilization": "iran_1980s_basij_mass_mobilization_system",
    "cw_ambush_tank_destroyers": "iran_1990s_mobile_hybrid_battlegroups",
    "cw_hull_down_armor": "himalayan_1970s_desert_mechanized_task_forces",
    "cw_territorial_armor_reserve": "iran_1980s_dual_military_command_structure",
    "cw_obstacle_engineering": "himalayan_1980s_extreme_terrain_hardening",
    "cw_antitank_missile_belts": "himalayan_1990s_mountain_warfare_digitization",
    "cw_delaying_defense": "himalayan_1960s_forward_defense_in_rugged_terrain",
    "cw_general_peoples_defense": "iran_1980s_religious_political_cohesion_framework",
    "cw_armed_neutrality_posture": "himalayan_1990s_frontline_modernization_cohesion",
    "cw_protracted_peoples_war": "iran_1990s_revolutionary_hybrid_force_consolidation",
    "cw_mujahideen_cell_networks": "iran_1990s_proxy_and_partner_force_integration",
    "cw_technicals_and_captured_armor": "himalayan_1960s_desert_armored_warfare_foundations",
    "cw_rpg_ambush_teams": "himalayan_1960s_rapid_reinforcement_over_difficult_terrain",
    "cw_manpads_and_advanced_antiarmor": "iran_1990s_missile_and_rocket_strike_doctrine",
    "cw_improvised_explosive_devices": "iran_1990s_urban_defense_layering",
    "cw_rocket_and_mortar_harassment": "iran_1990s_revolutionary_guard_operational_dominance",
    "cw_sanctuary_logistics": "himalayan_1980s_sector_command_system",
    "cw_cross_border_sanctuaries": "himalayan_1990s_counter_infiltration_grid_systems",
    "cw_general_uprising_offensive": "iran_1980s_human_wave_and_infiltration_tactics",
    "cw_networked_insurgency_campaign": "himalayan_1990s_rapid_reaction_mountain_brigades",
    "cw_sf_mountain_troops": "himalayan_1960s_high_altitude_infantry_training_programs",
    "cw_sf_arctic_winter_warfare": "himalayan_1980s_high_altitude_permanent_garrisoning",
    "cw_sf_high_altitude_warfare": "himalayan_1970s_battalion_level_mountain_combat_groups",
    "cw_sf_mountain_strike_raiders": "himalayan_1990s_helicopter_gunship_valley_support",
    "cw_sf_riverine_littoral": "himalayan_1970s_river_crossing_and_bridgehead_operations",
    "cw_sf_air_assault": "himalayan_1980s_thin_air_helicopter_operations",
    "cw_operational_maneuver_groups": "himalayan_1970s_operational_bifurcation_mastery",
    "cw_massed_air_defense": "himalayan_1980s_integrated_mountain_air_defense",
    "cw_tank_army_breakthrough": "himalayan_1990s_desert_strike_corps_evolution",
}
# school-exclusive subdoctrines with no legacy match get banner crops
CROP_SUBS_ORDER = None


def load(p):
    return Image.open(p).convert("RGBA")


def crt(im, variant=0):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    rgb = a[..., :3].copy()
    alpha = a[..., 3:4]
    g = (rgb * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
    rgb = rgb * 0.8 + g * 0.2
    rgb = rgb * np.array([0.96, 1.0, 1.03], np.float32)
    rgb[..., 0] = np.roll(rgb[..., 0], 1, axis=1)
    rgb[..., 2] = np.roll(rgb[..., 2], -1, axis=1)
    rgb[1::2] *= 0.92
    h, w = rgb.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    v = 1 - 0.22 * np.clip((d - 0.55) / 0.85, 0, 1)
    rgb = rgb * v[..., None]
    if variant:
        pal = [(1.0, 1.0, 1.0), (1.08, 0.98, 0.9), (0.9, 1.0, 1.1), (1.05, 1.05, 0.9), (0.92, 0.96, 1.08),
               (1.1, 0.92, 0.98), (0.95, 1.08, 0.95), (1.0, 0.93, 1.07)]
        rgb = rgb * np.array(pal[variant % len(pal)], np.float32)
        s = (variant // len(pal)) % 3
        if s:
            rgb = np.roll(rgb, s, axis=1)
    out = np.concatenate([np.clip(rgb, 0, 255), alpha], -1).astype(np.uint8)
    return Image.fromarray(out, "RGBA")


def normalize(im, target=75.0):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    m = a[..., 3] > 128
    if not m.any():
        return im
    rgb = a[..., :3]
    w = np.array([0.299, 0.587, 0.114], np.float32)
    L = (rgb * w).sum(-1)
    lo, hi = np.percentile(L[m], [1, 99])
    if hi - lo < 1:
        return im
    s = np.clip((rgb - lo) / (hi - lo) * 255, 0, 255)
    cur = ((s * w).sum(-1))[m].mean() / 255
    g = min(max(np.log(target / 255) / np.log(max(cur, 1e-3)), 0.6), 1.6)
    out = (np.power(s / 255, g) * 255).astype(np.uint8)
    return Image.fromarray(np.concatenate([out, a[..., 3:4].astype(np.uint8)], -1), "RGBA")


def circle(im64):
    im = im64.convert("RGBA").resize((64, 64), Image.LANCZOS)
    big = Image.new("L", (256, 256), 0)
    ImageDraw.Draw(big).ellipse((2, 2, 253, 253), fill=255)
    m = big.resize((64, 64), Image.LANCZOS)
    a = np.asarray(im).copy()
    a[..., 3] = (a[..., 3].astype(np.float32) * np.asarray(m).astype(np.float32) / 255).astype(np.uint8)
    return Image.fromarray(a, "RGBA")


def banner(name):
    im = load(f"{BANNERS}/{name}.png")
    bg = Image.new("RGBA", im.size, (0, 0, 0, 255))
    bg.alpha_composite(Image.merge("RGBA", (*im.split()[:3], Image.new("L", im.size, 255))))
    return bg


def cover_track(im, ax=0.5, zoom=1.0, ay=0.5):
    w, h = im.size
    tw, th = 360, 660
    s = th * zoom / h
    nw = round(w * s)
    nh = round(h * s)
    r = im.resize((nw, nh), Image.LANCZOS)
    x0 = max(0, int((nw - tw) * ax))
    y0 = max(0, int((nh - th) * ay))
    return r.crop((x0, y0, x0 + tw, y0 + th))


def square_crop(im, zoom, anchor):
    w, h = im.size
    side = int(min(w, h) * zoom)
    ax, ay = anchor
    cx = int(w * ax)
    cy = int(h * ay)
    x0 = min(max(0, cx - side // 2), w - side)
    y0 = min(max(0, cy - side // 2), h - side)
    return im.crop((x0, y0, x0 + side, y0 + side)).resize((64, 64), Image.LANCZOS)


def vanilla_src(sprite):
    return load(srcs_path(sprite))


def srcs_path(sprite):
    return f"{W}/src/{sprite}.png"


def save(im, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    im.save(path, "PNG", optimize=True)
    return path


def sub_file_school(sub):
    return sub


MIN_STD = 25.0


def contrast(im):
    a = np.asarray(im.convert("RGBA")).astype(np.float32)
    m = a[..., 3] > 128
    if not m.any():
        return 0.0
    L = (a[..., :3] * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1)
    return float(L[m].std())


def crop_icon(banner_name, zoom, anchor, variant):
    school = next(s for s, v in POOLS.items() if banner_name in v)
    pool = POOLS[school]
    start = pool.index(banner_name)
    anchors = [tuple(anchor), (0.5, 0.85), (0.5, 0.4), (0.35, 0.4), (0.65, 0.4), (0.5, 0.2), (0.5, 0.6)]
    zooms = [zoom, 0.8, 1.0, 0.62]
    for k in range(len(pool)):
        b = banner(pool[(start + k) % len(pool)])
        for z in zooms:
            for an in anchors:
                im = normalize(circle(crt(square_crop(b, z, an), variant)))
                if contrast(im) >= MIN_STD:
                    return im
    raise RuntimeError(f"no contrasting crop in pool {school} for {banner_name}")



def cover_focus(im, tw, th, fx, fy, zoom=1.0):
    w, h = im.size
    s = max(tw / w, th / h) * zoom
    r = im.resize((max(tw, round(w * s)), max(th, round(h * s))), Image.LANCZOS)
    x0 = min(max(0, round(r.width * fx - tw / 2)), r.width - tw)
    y0 = min(max(0, round(r.height * fy - th / 2)), r.height - th)
    return r.crop((x0, y0, x0 + tw, y0 + th))


def fit_track(im, fy=0.5, scale=1.0, tw=360, th=660):
    from PIL import ImageFilter
    w, h = im.size
    s = tw / w * scale
    fg = im.resize((max(1, round(w * s)), max(1, round(h * s))), Image.LANCZOS)
    bg = cover_focus(im, tw, th, 0.5, 0.5).filter(ImageFilter.GaussianBlur(18))
    bg = Image.blend(bg, Image.new("RGBA", bg.size, (0, 0, 0, 255)), 0.55)
    x = (tw - fg.width) // 2
    y = round((th - fg.height) * fy)
    bg.alpha_composite(fg, (x, y))
    return bg


def apply_picks(made):
    picks = json.load(open(W + "/picks.json"))
    for sprite, pk in picks.items():
        src = load(W + "/" + pk["src"])
        fx, fy = pk.get("focus") or (0.5, 0.5)
        stem = sprite[4:]
        if sprite.startswith("GFX_cw_track_"):
            if pk.get("mode") == "fit":
                im = crt(fit_track(src, pk.get("fit_y", 0.45), pk.get("fit_scale", 1.0)))
            else:
                im = crt(cover_focus(src, 360, 660, fx, fy, pk.get("zoom", 1.0)))
            path = f"{OUT}/tracks/{stem}.png"
        else:
            sq = cover_focus(src, 256, 256, fx, fy, 1.15).resize((64, 64), Image.LANCZOS)
            im = normalize(circle(crt(sq)))
            path = f"{OUT}/{'grand' if sprite.startswith('GFX_cw_gd_') else 'icons'}/{stem}.png"
        save(im, path)
    made["picked"] = list(picks)


def main():
    made = {"track": [], "grand": [], "sub": []}
    # ---- tracks ----
    for s in SCHOOLS:
        for t in LAND_TRACKS:
            tid = f"cw_{s}_{t}"
            im = cover_track(crt(banner(TRACK_BANNER[s][t])))
            p = save(im, f"{OUT}/tracks/cw_track_{tid}.png")
            made["track"].append((f"GFX_cw_track_{tid}", p))
    for era, plan in TRACK_BANNER_ERA.items():
        for s in SCHOOLS:
            for t in LAND_TRACKS:
                name, ax, zoom, ay = (plan[s][t] + (0.5, 1.0, 0.5))[:4] if len(plan[s][t]) == 1 else (plan[s][t] + (0.5,))[:4]
                tid = f"cw_{s}_{t}_e{era}"
                im = cover_track(crt(banner(name)), ax, zoom, ay)
                p = save(im, f"{OUT}/tracks/cw_track_{tid}.png")
                made["track"].append((f"GFX_cw_track_{tid}", p))
    for tid, sprite in NAVAL_AIR_SF_TRACKS.items():
        im = cover_track(crt(vanilla_src(sprite)))
        p = save(im, f"{OUT}/tracks/cw_track_{tid}.png")
        made["track"].append((f"GFX_cw_track_{tid}", p))
    # ---- grand ----
    for s in SCHOOLS:
        b = banner(GRAND_BANNER[s])
        im = square_crop(b, 1.0, (0.5, 0.42))
        im = normalize(circle(crt(im)))
        p = save(im, f"{OUT}/grand/cw_gd_cw_{s}.png")
        made["grand"].append((f"GFX_cw_gd_cw_{s}", p))
    for gid, gfx in json.load(open(W + "/grand_vanilla.json")).items():
        im = crt(vanilla_src(gfx))
        p = save(im, f"{OUT}/grand/cw_gd_{gid}.png")
        made["grand"].append((f"GFX_cw_gd_{gid}", p))
    # ---- subdoctrines ----
    subs = json.load(open(W + "/sub_plan.json"))
    for sid, plan in subs.items():
        kind = plan["kind"]
        if kind == "legacy":
            im = normalize(circle(load(f"{W}/legacy/cw_{plan['src']}.png")))
            if contrast(im) < MIN_STD:
                raise RuntimeError(f"legacy icon below contrast floor: {sid}")
        elif kind == "crop":
            im = crop_icon(plan["banner"], plan["zoom"], plan["anchor"], plan.get("variant", 0))
        elif kind == "vanilla":
            im = crt(vanilla_src(plan["src"]), plan.get("variant", 0))
            im = im.resize((64, 64), Image.LANCZOS)
        p = save(im, f"{OUT}/icons/cw_sd_{sid}.png")
        made["sub"].append((f"GFX_cw_sd_{sid}", p))
    json.dump(made, open(W + "/made.json", "w"), indent=1)
    apply_picks(made)
    print({k: len(v) for k, v in made.items()})


if __name__ == "__main__":
    main()
