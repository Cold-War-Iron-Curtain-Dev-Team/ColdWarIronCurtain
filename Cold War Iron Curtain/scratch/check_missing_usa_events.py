import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- SCANNING FOR MISSING EVENTS REFERENCED IN ALL USA FOCUS TREES ---")

# Gather all defined events in mod
all_defined_events = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as ef:
                text = ef.read()
            for m in re.findall(r"(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)", text):
                all_defined_events.add(m)

print(f"Total defined events in mod: {len(all_defined_events)}")

# Scan all USA trees
usa_referenced_events = {}
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus")):
    for f in files:
        if f.endswith(".txt") and ("USA" in f.upper() or "AMERICA" in f.upper()):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as tf:
                text = tf.read()
            # Match both country_event = X and country_event = { id = X }
            matches1 = re.findall(r"(?:country_event|news_event)\s*=\s*([a-zA-Z0-9_\.]+)", text)
            matches2 = re.findall(r"(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)", text)
            for m in set(matches1 + matches2):
                if m not in usa_referenced_events:
                    usa_referenced_events[m] = []
                usa_referenced_events[m].append(f)

missing_events = {k: v for k, v in usa_referenced_events.items() if k not in all_defined_events}
print(f"Total events referenced in USA trees: {len(usa_referenced_events)}")
print(f"Missing events referenced in USA trees: {len(missing_events)}")

# Group by event namespace/prefix
by_prefix = {}
for k, v in sorted(missing_events.items(), key=lambda x: -len(x[1])):
    prefix = k.split(".")[0] if "." in k else k
    if prefix not in by_prefix:
        by_prefix[prefix] = []
    by_prefix[prefix].append((k, len(v), v[:2]))

for prefix, items in sorted(by_prefix.items(), key=lambda x: -len(x[1])):
    print(f"\nPrefix '{prefix}' ({len(items)} missing events):")
    for eid, count, trees in items[:10]:
        print(f"  {eid} in {count} trees ({trees})")
