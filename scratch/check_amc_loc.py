import os

for root, dirs, files in os.walk('Cold War Iron Curtain/localisation'):
    for f in files:
        if f.endswith('.yml'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'AgnewMcCarthy' in c:
                    print(f"Loc in {f}:")
                    for line in c.splitlines():
                        if 'AgnewMcCarthy' in line:
                            print(f"  {line.strip()[:80]}")
