import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

all_modifiers = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "ideas")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                in_mod = False
                for line in file:
                    line = line.strip()
                    if line.startswith("#"): continue
                    if "modifier = {" in line:
                        in_mod = True
                        continue
                    if in_mod:
                        if "}" in line:
                            in_mod = False
                            continue
                        m = re.match(r"^([a-zA-Z0-9_]+)\s*=", line)
                        if m:
                            all_modifiers.add(m.group(1))

test_mods = [
    "stability_factor", "consumer_goods_factor", "production_speed_buildings_factor",
    "production_speed_industrial_complex_factor", "trade_opinion_factor", "research_speed_factor",
    "production_speed_synthetic_refinery_factor", "political_power_gain", "industrial_capacity_factory",
    "diplomatic_action_cost", "production_speed_arms_factory_factor", "monthly_population",
    "conscription_factor", "army_org_factor", "generate_wargoal_tension", "decryption_factor",
    "air_detection_factor", "send_volunteer_divisions_required", "subversive_activites_upkeep",
    "intel_network_gain_factor", "war_support_factor"
]

print("--- TESTING PROPOSED MODIFIERS ---")
for tm in test_mods:
    print(f"{tm:45}: {'VALID' if tm in all_modifiers else 'NOT FOUND'}")
