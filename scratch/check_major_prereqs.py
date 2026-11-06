import re

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8") as f:
    dev = f.read()

for fid in ['MLA_Recreate_Malaysia', 'MLA_Deal_with_the_Great_Famine', 'MLA_Literacy_Campaign', 'MLA_Jumpstart_Colonial_Industry', 'MLA_The_Malaysian_Peoples_Liberation_Army']:
    m = re.search(r'id\s*=\s*' + fid + r'[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', dev)
    if m:
        prereqs = re.findall(r'prerequisite\s*=\s*\{([^}]*)\}', m.group(0))
        print(f"=== {fid} ===")
        print("Prereqs:", [p.strip() for p in prereqs])
