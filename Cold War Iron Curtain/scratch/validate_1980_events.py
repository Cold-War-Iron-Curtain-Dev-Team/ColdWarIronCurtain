import os, re

base = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980'

# Gather all event IDs across all event files
all_events = set()
for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fl:
                for line in fl:
                    m = re.search(r'id\s*=\s*([a-zA-Z0-9_\.]+)', line)
                    if m:
                        all_events.add(m.group(1))

# Check events called in 1980 trees
missing_events = {}
for f in sorted(os.listdir(base)):
    if f.endswith('.txt'):
        p = os.path.join(base, f)
        with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
            c = fl.read()
        event_calls = re.findall(r'(country_event|news_event)\s*=\s*([a-zA-Z0-9_\.]+)', c)
        for t, eid in event_calls:
            if eid not in all_events:
                missing_events.setdefault(eid, []).append(f)

print("Missing events in 1980 trees:")
for eid, flist in missing_events.items():
    print(f"  {eid}: in {flist}")
