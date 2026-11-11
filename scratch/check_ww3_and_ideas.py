import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- 1. CHECKING USAw and USAww EVENTS ---")
all_events = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as ef:
                text = ef.read()
            for m in re.findall(r"(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)", text):
                all_events.add(m)

ww3_events = ['USAww.5', 'USAww.2', 'USAw.4', 'USAww.4', 'USAww.6', 'USAww.17', 'USAww.18', 'USAww.10', 'USAw.1', 'USAww.1', 'USAw.5', 'USAww.7', 'USAww.8', 'USAww.13', 'USAww.15', 'USAw.6', 'USAw.2', 'USAww.16', 'USAw.3', 'USAww.12', 'USAww.11', 'USAww.3', 'USAw.7', 'USAww.19', 'USAww.14', 'USAw.0', 'USAw.8', 'USAww.9', 'USAw.9']

missing_ww3_events = [e for e in ww3_events if e not in all_events]
print(f"Missing WW3 events ({len(missing_ww3_events)}/{len(ww3_events)}):", missing_ww3_events)

print("\n--- 2. UNHOOKED 70s TREES ---")
unhooked_70s = ["USA_Rockefeller_1975", "USA_Rockefeller_1976"]
for t in unhooked_70s:
    print(t)

print("\n--- 3. CHECKING ALL IDEAS REFERENCED IN USA 1980s TREES ---")
existing_ideas = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "ideas")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as idf:
                text = idf.read()
            # match idea names
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("#"): continue
                m = re.match(r"^([a-zA-Z0-9_]+)\s*=\s*\{", line)
                if m:
                    existing_ideas.add(m.group(1))

# Also law ideas, etc.
print(f"Total defined ideas found: {len(existing_ideas)}")

# Scan 1980s trees for add_ideas
referenced_ideas = {}
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus", "USA 1980s", "Coded")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as tf:
                text = tf.read()
            for m in re.findall(r"add_ideas\s*=\s*([a-zA-Z0-9_]+)", text):
                if m not in referenced_ideas:
                    referenced_ideas[m] = []
                referenced_ideas[m].append(f)

missing_ideas = {k: v for k, v in referenced_ideas.items() if k not in existing_ideas}
print(f"Total ideas added in 1980s trees: {len(referenced_ideas)}")
print(f"Missing ideas in 1980s trees: {len(missing_ideas)}")
for k, v in sorted(missing_ideas.items(), key=lambda x: -len(x[1])):
    print(f"  {k} (in {len(v)} trees: {v[:3]}...)")
