import os, re

base = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1988'
for f in sorted(os.listdir(base)):
    if f.endswith('.txt'):
        p = os.path.join(base, f)
        with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
            c = fl.read()
        m = re.search(r'id\s*=\s*([a-zA-Z0-9_]+)', c)
        tid = m.group(1) if m else '?'
        print(f"{f:42} -> {tid}")
