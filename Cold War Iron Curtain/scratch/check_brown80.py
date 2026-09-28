import os, re

for root, dirs, files in os.walk('Cold War Iron Curtain/events'):
    for f in files:
        if f.endswith('.txt'):
            p = os.path.join(root, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
                if 'Brown80' in c:
                    eids = re.findall(r'id\s*=\s*(Brown80\.[0-9]+)', c)
                    if eids:
                        print(f"{f}: {eids}")
