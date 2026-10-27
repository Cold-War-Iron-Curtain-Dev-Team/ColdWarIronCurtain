import re

for fn in ['USA_Anderson_1980.txt', 'USA_Anderson_GOP_1980.txt']:
    p = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/' + fn
    with open(p, 'r', encoding='utf-8', errors='ignore') as f:
        t = f.read()
    print(f"=== {fn} ===")
    focuses = re.findall(r'id\s*=\s*(USA_[A-Z0-9_]+)', t)
    for fc in focuses[:8]:
        print(f"  {fc}")
