with open(r"interface\Trade_Tab.gui", "r") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if "containerWindowType" in l or "windowType" in l:
        print(f"{idx+1}: {l.strip()}")
        if idx+1 < len(lines):
            print(f"   {lines[idx+1].strip()}")
