with open('Cold War Iron Curtain/common/ideologies/00_ideologies.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'centrism' in l or 'rockefeller_republican' in l or 'new_federalism' in l:
        print(f"Line {i}: {l.strip()}")
        for j in range(max(0, i-10), i):
            if '=' in lines[j] and '{' in lines[j]:
                print(f"  Parent: {lines[j].strip()}")
