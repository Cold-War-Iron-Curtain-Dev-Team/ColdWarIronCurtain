import os, re

for root, dirs, files in os.walk('Cold War Iron Curtain/localisation'):
    for f in files:
        if f.endswith('.yml'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'usa.19801' in c or 'usa.19802' in c or 'usa.19803' in c:
                    print(f"Loc in: {f}")
                    for line in c.splitlines():
                        if any(k in line for k in ['usa.19801', 'usa.19802', 'usa.19803']):
                            print(f"  {line.strip()[:80]}")
