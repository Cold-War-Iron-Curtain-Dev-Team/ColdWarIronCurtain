import os

for root, dirs, files in os.walk('Cold War Iron Curtain/localisation'):
    for f in files:
        if f.endswith('.yml'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'Brown80.10' in c or 'Solar_Space_Energy_Program' in c:
                    print(f"Match in {f}:")
                    for line in c.splitlines():
                        if 'Brown80.10' in line or 'Solar_Space_Energy_Program' in line:
                            print(f"  {line.strip()[:80]}")
