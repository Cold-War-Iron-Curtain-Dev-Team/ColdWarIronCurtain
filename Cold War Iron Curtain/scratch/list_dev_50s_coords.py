import re

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

coords = {}
for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', text):
    block = m.group(1)
    fid = re.search(r'id\s*=\s*([a-zA-Z0-9_\-]+)', block).group(1)
    x = int(re.search(r'x\s*=\s*(\d+)', block).group(1))
    y = int(re.search(r'y\s*=\s*(\d+)', block).group(1))
    rel = re.search(r'relative_position_id\s*=\s*([a-zA-Z0-9_\-]+)', block)
    coords[fid] = {'x': x, 'y': y, 'rel': rel.group(1) if rel else None}

for fid, c in sorted(coords.items(), key=lambda item: (item[1]['y'], item[1]['x'])):
    print(f"y={c['y']:2} x={c['x']:2} rel={c['rel']} : {fid}")
