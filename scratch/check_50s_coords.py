import re

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    dev = f.read()

for name in ['MLA_Our_Place_in_the_Socialist_World', 'MLA_Consolidate_Our_Power', 'MLA_Strengthen_Chinese_Relations', 'MLA_Deal_with_the_Great_Famine', 'MLA_Literacy_Campaign']:
    m_dev = re.search(r'id\s*=\s*' + name + r'[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', dev)
    m_rew = re.search(r'id\s*=\s*' + name + r'[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', rew)
    print(f"=== {name} ===")
    if m_dev:
        x_d = re.search(r'x\s*=\s*(\d+)', m_dev.group(0))
        y_d = re.search(r'y\s*=\s*(\d+)', m_dev.group(0))
        rel_d = re.search(r'relative_position_id\s*=\s*(\w+)', m_dev.group(0))
        print(f"Dev: rel={rel_d.group(1) if rel_d else 'NONE'} x={x_d.group(1) if x_d else '?'} y={y_d.group(1) if y_d else '?'}")
    if m_rew:
        x_r = re.search(r'x\s*=\s*(\d+)', m_rew.group(0))
        y_r = re.search(r'y\s*=\s*(\d+)', m_rew.group(0))
        rel_r = re.search(r'relative_position_id\s*=\s*(\w+)', m_rew.group(0))
        print(f"Rew: rel={rel_r.group(1) if rel_r else 'NONE'} x={x_r.group(1) if x_r else '?'} y={y_r.group(1) if y_r else '?'}")
