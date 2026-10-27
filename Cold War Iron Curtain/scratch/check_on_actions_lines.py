with open('Cold War Iron Curtain/common/on_actions/00_on_actions.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if any(k in l for k in ['19801', '19802', '19803', '19841', '19881', '19761']):
        print(f"Line {i+1}: {l.strip()}")
        for j in range(max(0, i-5), min(len(lines), i+6)):
            print(f"  {j+1}: {lines[j].strip()}")
        print("-" * 40)
