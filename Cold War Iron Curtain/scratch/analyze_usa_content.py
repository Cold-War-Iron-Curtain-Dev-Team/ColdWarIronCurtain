import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- ANALYZING USA CONTENT IMPROVEMENTS ---")

# 1. Collect all USA focus trees
usa_trees = {}
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as tf:
                content = tf.read()
            matches = re.findall(r"focus_tree\s*=\s*\{[^{}]*?id\s*=\s*([a-zA-Z0-9_]+)", content, re.DOTALL)
            for m in matches:
                if "USA" in m.upper() or "AMERICA" in m.upper():
                    usa_trees[m] = {
                        "path": os.path.relpath(p, mod_dir),
                        "file": f,
                        "content": content
                    }

print(f"Total USA focus trees: {len(usa_trees)}")

# 2. Check loaded status
all_loaded = {}
for root, dirs, files in os.walk(mod_dir):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as cf:
                text = cf.read()
            for m in re.findall(r"load_focus_tree\s*=\s*([a-zA-Z0-9_]+)", text):
                if m not in all_loaded:
                    all_loaded[m] = []
                all_loaded[m].append(os.path.relpath(p, mod_dir))

never_loaded = {k: v for k, v in usa_trees.items() if k not in all_loaded}
print(f"Never loaded USA trees: {len(never_loaded)}")

# Categorize never loaded trees by decade
by_decade = {"50s": [], "60s": [], "70s": [], "80s": [], "other": []}
for t, info in never_loaded.items():
    if "195" in t or "50s" in t:
        by_decade["50s"].append((t, info["path"]))
    elif "196" in t or "60s" in t:
        by_decade["60s"].append((t, info["path"]))
    elif "197" in t or "70s" in t:
        by_decade["70s"].append((t, info["path"]))
    elif "198" in t or "80s" in t:
        by_decade["80s"].append((t, info["path"]))
    else:
        by_decade["other"].append((t, info["path"]))

for dec, items in by_decade.items():
    print(f"\nDecade {dec} ({len(items)} unhooked trees):")
    for t, path in sorted(items):
        print(f"  {t} ({path})")

# 3. Check WW3 tree USA_1950s_WW3
ww3_info = usa_trees.get("USA_1950s_WW3")
if ww3_info:
    print("\n--- USA_1950s_WW3 Tree Analysis ---")
    content = ww3_info["content"]
    # Check what triggers or country = { factor = 0 modifier = ... } it has
    country_block = re.search(r"country\s*=\s*\{([^}]+)\}", content)
    if country_block:
        print("Country block:", country_block.group(1).strip())
    # Count focuses
    focus_ids = re.findall(r"focus\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_]+)", content)
    print(f"Number of focuses in WW3 tree: {len(focus_ids)}")
    # Find event calls in WW3 tree
    event_calls = re.findall(r"(?:country_event|news_event)\s*=\s*([a-zA-Z0-9_\.]+)", content)
    print(f"Event calls in WW3 tree: {set(event_calls)}")
