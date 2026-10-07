import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- 1. SUPER EVENTS SEARCH ---")
for root, dirs, files in os.walk(mod_dir):
    for f in files:
        if "super_event" in f.lower() or "superevent" in f.lower():
            print(f"Super event file: {os.path.relpath(os.path.join(root, f), mod_dir)}")

print("\n--- 2. USALGB80s SEARCH ---")
for root, dirs, files in os.walk(mod_dir):
    for f in files:
        if f.endswith((".txt", ".yml")):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "USALGB" in content:
                    for idx, line in enumerate(content.splitlines(), 1):
                        if "USALGB" in line:
                            print(f"{os.path.relpath(p, mod_dir)}:{idx}: {line.strip()}")

print("\n--- 3. FEDERAL RESERVE IDEAS USAGE ---")
fed_ideas = ["Center_Left_Fed_Reserve", "Center_Fed_Reserve", "Right_Wing_Fed_Reserve"]
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus", "USA 1980s")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as tf:
                content = tf.read()
            for fi in fed_ideas:
                if fi in content:
                    print(f"{f} references {fi}")

print("\n--- 4. REDUCED BARRIERS TO AMERICAN MARKET USAGE ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus", "USA 1980s")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as tf:
                content = tf.read()
            if "Reduced_Barriers_to_American_Market" in content:
                print(f"{f} references Reduced_Barriers_to_American_Market")
