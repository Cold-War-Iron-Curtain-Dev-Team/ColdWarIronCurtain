with open(r"common\scripted_guis\Trade_Tab.txt", "r") as f:
    lines = f.readlines()

for idx, l in enumerate(lines):
    # look for root-level entries in scripted_gui
    if l.startswith("\t") and not l.startswith("\t\t") and "=" in l:
        print(f"{idx+1}: {l.strip()}")
