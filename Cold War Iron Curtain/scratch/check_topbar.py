with open(r"interface\topbar.gui", "r") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    if any(k in l.lower() for k in ['trade', 'market']):
        print(f"{idx+1}: {l.strip()}")
