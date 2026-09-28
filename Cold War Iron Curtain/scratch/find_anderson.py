import os

for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'anderson_independent' in c or 'USA_Anderson_1980' in c:
                    print(f"Found Anderson in: {f}")
