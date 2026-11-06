import re

with open("scratch/preview_emergency.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Check all focus IDs
focuses = re.findall(r'id\s*=\s*([a-zA-Z0-9_\-]+)', text)
print(f"Total focuses: {len(focuses)}")
# Check for duplicate focus IDs
seen = set()
dups = []
for fid in focuses:
    if fid in seen:
        dups.append(fid)
    seen.add(fid)
print("Duplicates:", dups)

# Verify coordinates of our 16 focuses
for fid in [
    'MLA_Expand_Min_Yuen', 'MLA_Maintain_Marxist_Purity', 'MLA_Radical_China', 'MLA_Promote_Nanyang',
    'MLA_Maintain_Sinophilic_Views', 'MLA_Enforce_Revolutionary', 'MLA_Ditch_Non-Chinese',
    'MLA_A_Pragmatic_Future', 'MLA_Recruit_Naryanan', 'MLA_Tolerate_non_Marxist_Views',
    'MLA_Expand_Non-Chinese_Supporter_Bases', 'MLA_Resolve_Racial_Inequality', 'MLA_All_Together',
    'MLA_Show_Ethnic_Chinese_the_Rights_of_Humans', 'MLA_Show_the_Malay_a_Better_Future',
    'MLA_Show_the_British_a_Way_Out'
]:
    m = re.search(r'id\s*=\s*' + fid + r'\b[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', text)
    blk = m.group(0)
    x = re.search(r'x\s*=\s*(-?\d+)', blk).group(1)
    y = re.search(r'y\s*=\s*(-?\d+)', blk).group(1)
    rel = re.search(r'relative_position_id\s*=\s*(\w+)', blk)
    icon = re.search(r'icon\s*=\s*(\w+)', blk).group(1)
    print(f"{fid:44} | rel={str(rel.group(1) if rel else 'None'):30} x={x:2} y={y:2} | icon={icon}")
