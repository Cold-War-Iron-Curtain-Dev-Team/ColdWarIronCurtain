import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- 1. GOLDWATER SEARCH ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "goldwater" in content.lower():
                    for idx, line in enumerate(content.splitlines(), 1):
                        if "id = " in line or "namespace" in line:
                            print(f"{f}:{idx}: {line.strip()}")

print("\n--- 2. DEWEY.10 in USA_1950s_Rework_Events.txt ---")
p = os.path.join(mod_dir, "events", "USA_1950s_Rework_Events.txt")
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if "Dewey.10" in line or "Dewey.11" in line:
        start = max(0, idx - 5)
        end = min(len(lines), idx + 25)
        print("".join(lines[start:end]))

print("\n--- 3. Syria_CIA in events/ ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "Syria_CIA" in content:
                    for idx, line in enumerate(content.splitlines(), 1):
                        if "id = " in line or "namespace" in line:
                            print(f"{f}:{idx}: {line.strip()}")
