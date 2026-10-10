import re, difflib

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    dev = f.read()

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

def get_focus_blocks(txt):
    blocks = {}
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', txt):
        fid_m = re.search(r'id\s*=\s*([a-zA-Z0-9_\-]+)', m.group(1))
        if fid_m:
            blocks[fid_m.group(1)] = m.group(0).strip()
    return blocks

dev_blocks = get_focus_blocks(dev)
rew_blocks = get_focus_blocks(rew)

for fid in ['MLA_Found_the_Peoples_Republic_of_Malaysia', 'MLA_Chairman_Chin_Peng', 'MLA_Our_Place_in_the_Socialist_World', 'MLA_Co-rule_With_Shamsiah_Fakeh', 'MLA_Consolidate_Our_Power']:
    print(f"=== DIFF FOR {fid} ===")
    d_lines = dev_blocks[fid].splitlines()
    r_lines = rew_blocks[fid].splitlines()
    diff = difflib.unified_diff(d_lines, r_lines, fromfile="dev", tofile="rew", lineterm="")
    for l in diff:
        print(l)
