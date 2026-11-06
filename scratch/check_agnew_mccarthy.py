with open('Cold War Iron Curtain/events/USA_1980s_Admin_Specific_Events.txt', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if 'AgnewMcCarthy' in l:
        print(f"Line {i+1}: {l.strip()}")
        for j in range(max(0, i-5), min(len(lines), i+25)):
            print(f"  {j+1}: {lines[j].strip()}")
        print("="*40)
