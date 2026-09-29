import os, re

for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'usa.19801' in c or 'usa.19802' in c or 'usa.19803' in c:
                    print(f"Referenced in: {f}")
