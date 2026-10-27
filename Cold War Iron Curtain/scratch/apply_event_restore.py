import subprocess, re

# Read old events from git f0db1e7810~1
old_events_txt = subprocess.check_output(
    ['git', 'show', 'f0db1e7810~1:Cold War Iron Curtain/events/MLA.txt'],
    text=True, errors='ignore'
)

with open('events/MLA.txt', 'r', encoding='utf-8', errors='ignore') as f:
    live_events_txt = f.read()

# Helper to extract an event block by ID from old_events_txt
def extract_event(eid, txt):
    m = re.search(r'(?:country_event|news_event)\s*=\s*\{\s*id\s*=\s*' + re.escape(eid) + r'\b', txt)
    if not m:
        raise ValueError(f"Event {eid} not found in old text")
    start = m.start()
    depth = 0
    end = start
    for i in range(start, len(txt)):
        if txt[i] == '{':
            depth += 1
        elif txt[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return txt[start:end].strip()

# Extract blocks
power_struggle_1 = extract_event('MLA_Power_Struggle.1', old_events_txt)
power_struggle_2 = extract_event('MLA_Power_Struggle.2', old_events_txt)
mla_6 = extract_event('MLA.6', old_events_txt)
mla_7 = extract_event('MLA.7', old_events_txt)
mla_17 = extract_event('MLA.17', old_events_txt)
mla_18 = extract_event('MLA.18', old_events_txt)
mla_57 = extract_event('MLA.57', old_events_txt).replace('picture = GFX_', 'picture = GFX_politics')
mla_64 = extract_event('MLA.64', old_events_txt)
mla_81 = extract_event('MLA.81', old_events_txt)
mla_82 = extract_event('MLA.82', old_events_txt)
mla_83 = extract_event('MLA.83', old_events_txt)

tail_events = [
    'MLA_KMT.1', 'MLA_KMT.2', 'MLA_KMT.3', 'MLA_KMT.4', 'MLA_KMT.5', 'MLA_KMT.100',
    'MLA_Boestamam.1', 'MLA_Boestamam.2', 'MLA_Boestamam.3', 'MLA_Boestamam.4', 'MLA_Boestamam.5',
    'MLA_Boestamam.6', 'MLA_Boestamam.7', 'MLA_Boestamam.100',
    'MLA_Syndies.1', 'MLA_Syndies.2', 'MLA_Syndies.3', 'MLA_Syndies.4', 'MLA_Syndies.5', 'MLA_Syndies.100'
]
tail_blocks = [extract_event(eid, old_events_txt) for eid in tail_events]

# Now assemble modified text
# 1. Namespaces at top
new_txt = live_events_txt
ns_target = "add_namespace = PRC_RAJ\n"
ns_replacement = (
    "add_namespace = PRC_RAJ\n"
    "add_namespace = MLA_KMT\n"
    "add_namespace = MLA_Power_Struggle\n"
    "add_namespace = MLA_Boestamam\n"
    "add_namespace = MLA_Syndies\n\n"
    f"{power_struggle_1}\n\n"
    f"{power_struggle_2}\n"
)
new_txt = new_txt.replace(ns_target, ns_replacement, 1)

# 2. MLA.6 and MLA.7 after MLA.5
m_mla5 = re.search(r'news_event\s*=\s*\{\s*id\s*=\s*MLA\.5\b[\s\S]*?\n\}', new_txt)
mla5_end = m_mla5.end()
new_txt = new_txt[:mla5_end] + f"\n\n{mla_6}\n\n{mla_7}" + new_txt[mla5_end:]

# 3. MLA.17 and MLA.18 after MLA.16
m_mla16 = re.search(r'country_event\s*=\s*\{\s*id\s*=\s*MLA\.16\b[\s\S]*?\n\}', new_txt)
mla16_end = m_mla16.end()
new_txt = new_txt[:mla16_end] + f"\n\n{mla_17}\n\n{mla_18}" + new_txt[mla16_end:]

# 4. MLA.57 after MLA.56
m_mla56 = re.search(r'country_event\s*=\s*\{\s*id\s*=\s*MLA\.56\b[\s\S]*?\n\}', new_txt)
mla56_end = m_mla56.end()
new_txt = new_txt[:mla56_end] + f"\n\n{mla_57}" + new_txt[mla56_end:]

# 5. MLA.64 after MLA.63
m_mla63 = re.search(r'news_event\s*=\s*\{\s*id\s*=\s*MLA\.63\b[\s\S]*?\n\}', new_txt)
mla63_end = m_mla63.end()
new_txt = new_txt[:mla63_end] + f"\n\n{mla_64}" + new_txt[mla63_end:]

# 6. MLA.81, 82, 83 after MLA.80
m_mla80 = re.search(r'country_event\s*=\s*\{\s*id\s*=\s*MLA\.80\b[\s\S]*?\n\}', new_txt)
mla80_end = m_mla80.end()
new_txt = new_txt[:mla80_end] + f"\n\n{mla_81}\n\n{mla_82}\n\n{mla_83}" + new_txt[mla80_end:]

# 7. Tail events at end
tail_text = "\n\n" + "\n\n".join(tail_blocks) + "\n"
new_txt = new_txt.rstrip() + tail_text

# Check bracket balance
depth = 0
for idx, ch in enumerate(new_txt):
    if ch == '{':
        depth += 1
    elif ch == '}':
        depth -= 1
        if depth < 0:
            print(f"Error: Negative bracket depth at char {idx}")
            break

print(f"Final bracket depth: {depth}")

# Count events
all_eids = re.findall(r'id\s*=\s*([a-zA-Z0-9_\.]+)', new_txt)
print(f"Total events in new_txt: {len(all_eids)}")
for eid in ['MLA_Power_Struggle.1', 'MLA_Power_Struggle.2', 'MLA.6', 'MLA.7', 'MLA.17', 'MLA.18', 'MLA.57', 'MLA.64', 'MLA.81', 'MLA.82', 'MLA.83'] + tail_events:
    if eid not in all_eids:
        print(f"MISSING: {eid}")

with open('events/MLA.txt', 'w', encoding='utf-8') as f:
    f.write(new_txt)
print("events/MLA.txt successfully updated!")
