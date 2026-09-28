with open('Cold War Iron Curtain/events/USA.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'usa.19801' in l or 'usa.19802' in l or 'usa.19803' in l:
        print(f"Line {i+1}: {l.strip()}")
