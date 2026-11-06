import os

for root, dirs, files in os.walk('Cold War Iron Curtain'):
    for f in files:
        if f.endswith(('.txt', '.gui', '.lua')):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'usa.19801' in c or 'usa.19802' in c or 'usa.19761' in c or 'usa.19762' in c:
                    print(f"Match in: {os.path.relpath(p, 'Cold War Iron Curtain')}")
