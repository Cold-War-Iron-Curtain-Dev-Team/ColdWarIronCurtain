import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- DEWEY EVENTS in USA_1950s_Rework_Events.txt ---")
p = os.path.join(mod_dir, "events", "USA_1950s_Rework_Events.txt")
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if "dewey" in line.lower() or "halleck" in line.lower() or "macarthur" in line.lower():
        if "id = " in line or "namespace" in line or "title = " in line:
            print(f"{idx+1}: {line.strip()}")

print("\n--- SEARCHING FOR Korean_War events across events/ ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt") and "korea" in f.lower():
            p2 = os.path.join(root, f)
            with open(p2, "r", encoding="utf-8", errors="ignore") as kf:
                for idx, line in enumerate(kf):
                    if "namespace" in line or "id = " in line:
                        print(f"{f}:{idx+1}: {line.strip()}")
