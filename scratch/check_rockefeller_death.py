import os

for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'death_of_rockefeller' in c or 'rockefeller_dies' in c or 'rockefeller_dead' in c or 'nelson_rockefeller_dies' in c:
                    print(f"Found in: {f}")
