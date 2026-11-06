import os, re

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew_text = f.read()

with open("common/national_focus/MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
    dev_text = f.read()

print(f"Reworked MLA focuses:")
for m in re.finditer(r'focus\s*=\s*\{[\s\S]*?id\s*=\s*([a-zA-Z0-9_\-]+)', rew_text):
    print(m.group(1))
