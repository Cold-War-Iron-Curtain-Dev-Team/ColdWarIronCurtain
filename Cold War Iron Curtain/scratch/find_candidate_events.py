import os, re

keywords = ['connally', 'baker', 'landgrebe', 'dole', 'rockefeller', 'shriver', 'muskie']
found = {}

for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read().lower()
                for kw in keywords:
                    if kw in c:
                        found.setdefault(kw, []).append(f)

for kw, flist in found.items():
    print(f"{kw}: {set(flist)}")
