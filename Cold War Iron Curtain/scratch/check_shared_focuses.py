import os, re

base = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980'
for f in sorted(os.listdir(base)):
    if f.endswith('.txt'):
        p = os.path.join(base, f)
        with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
            c = fl.read()
        shared = re.findall(r'shared_focus\s*=\s*([a-zA-Z0-9_]+)', c)
        print(f"{f:35} -> shared: {len(shared)} {shared}")
