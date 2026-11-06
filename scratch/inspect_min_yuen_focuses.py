import re

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

min_yuen_ids = [
    'MLA_Expand_Min_Yuen', 'MLA_Maintain_Marxist_Purity', 'MLA_Radical_China', 'MLA_Promote_Nanyang',
    'MLA_Maintain_Sinophilic_Views', 'MLA_Enforce_Revolutionary', 'MLA_Ditch_Non-Chinese',
    'MLA_A_Pragmatic_Future', 'MLA_Recruit_Naryanan', 'MLA_Tolerate_non_Marxist_Views',
    'MLA_Expand_Non-Chinese_Supporter_Bases', 'MLA_Resolve_Racial_Inequality', 'MLA_All_Together'
]

for fid in min_yuen_ids:
    m = re.search(r'focus\s*=\s*\{[\s\S]*?id\s*=\s*' + fid + r'\b[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', rew)
    if not m:
        print(f"ERROR: {fid} not found")
    else:
        print(f"=== {fid} ===")
        print(m.group(0)[:250] + "...\n")
