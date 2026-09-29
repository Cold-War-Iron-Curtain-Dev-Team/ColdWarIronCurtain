import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- SCANNING 1950s, 1960s, 1970s USA FOCUS TREES FOR MISSING IDEAS & EVENTS ---")

# Gather all ideas
all_ideas = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "ideas")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as idf:
                for line in idf:
                    line = line.strip()
                    if line.startswith("#"): continue
                    m = re.match(r"^([a-zA-Z0-9_]+)\s*=\s*\{", line)
                    if m: all_ideas.add(m.group(1))

# Gather all events
all_events = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as ef:
                for m in re.findall(r"(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)", ef.read()):
                    all_events.add(m)

# Check all non-80s USA trees in common/national_focus
non_80s_files = []
for f in os.listdir(os.path.join(mod_dir, "common", "national_focus")):
    if f.endswith(".txt") and ("USA" in f.upper() or "AMERICA" in f.upper()):
        non_80s_files.append(f)

print(f"Found {len(non_80s_files)} non-80s USA focus files in root national_focus.")

missing_ideas_by_file = {}
missing_events_by_file = {}

for f in non_80s_files:
    p = os.path.join(mod_dir, "common", "national_focus", f)
    with open(p, "r", encoding="utf-8", errors="ignore") as tf:
        text = tf.read()
    
    # Check add_ideas
    ideas = re.findall(r"add_ideas\s*=\s*([a-zA-Z0-9_]+)", text)
    miss_i = [i for i in set(ideas) if i not in all_ideas]
    if miss_i:
        missing_ideas_by_file[f] = miss_i
        
    # Check events
    ev1 = re.findall(r"(?:country_event|news_event)\s*=\s*([a-zA-Z0-9_\.]+)", text)
    ev2 = re.findall(r"(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)", text)
    miss_e = [e for e in set(ev1 + ev2) if e not in all_events and not e.startswith("USAw")]
    if miss_e:
        missing_events_by_file[f] = miss_e

print("\n--- MISSING IDEAS IN 50s/60s/70s USA TREES ---")
for f, items in sorted(missing_ideas_by_file.items()):
    print(f"{f}: {items}")

print("\n--- MISSING EVENTS IN 50s/60s/70s USA TREES (excluding USAw) ---")
for f, items in sorted(missing_events_by_file.items()):
    print(f"{f}: {items}")
