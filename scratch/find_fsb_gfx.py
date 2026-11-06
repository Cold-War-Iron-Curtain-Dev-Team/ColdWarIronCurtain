import os
import re

interface_dir = 'Cold War Iron Curtain/interface'
results = []
for fname in os.listdir(interface_dir):
    if not fname.endswith('.gfx'): continue
    path = os.path.join(interface_dir, fname)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    for m in re.finditer(r'name\s*=\s*"([^"]+)"', content):
        name = m.group(1)
        if 'report_event' in name.lower() and any(k in name.lower() for k in ['sov', 'rus', 'kremlin', 'moscow', 'secret', 'spy', 'soldier', 'tank']):
            results.append(name)

for r in sorted(set(results))[:50]:
    print(r)
