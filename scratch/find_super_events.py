import os, re

for root, dirs, files in os.walk('Cold War Iron Curtain/common/scripted_effects'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                for line in fl:
                    if 'super_event' in line and '=' in line and '{' in line:
                        print(line.strip())
