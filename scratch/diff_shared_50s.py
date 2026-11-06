import re

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

diffs = []
for fid in dev_blocks:
    if fid in rew_blocks:
        d_clean = "".join(dev_blocks[fid].split())
        r_clean = "".join(rew_blocks[fid].split())
        if d_clean != r_clean:
            diffs.append(fid)

print("Focuses in both that differ:", diffs)
