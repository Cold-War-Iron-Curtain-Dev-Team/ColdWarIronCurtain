import os

for root, dirs, files in os.walk('Cold War Iron Curtain/common/scripted_effects'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'president_landgrebe_super_event' in c:
                    print(f"Found in: {f}")
