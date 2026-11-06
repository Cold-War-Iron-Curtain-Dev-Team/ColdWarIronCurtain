import os

for root, dirs, files in os.walk('Cold War Iron Curtain/common/on_actions'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if '19801' in c or '19802' in c or '19803' in c or '19761' in c or '19841' in c:
                    print(f"Found in on_actions: {f}")
