import re

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    dev = f.read()

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

dev_focuses = set(re.findall(r'focus\s*=\s*\{[\s\S]*?id\s*=\s*([a-zA-Z0-9_\-]+)', dev))
rew_focuses = set(re.findall(r'focus\s*=\s*\{[\s\S]*?id\s*=\s*([a-zA-Z0-9_\-]+)', rew))

print(f"Dev count: {len(dev_focuses)}")
print(f"Rew count: {len(rew_focuses)}")
print(f"In Rew but not in Dev ({len(rew_focuses - dev_focuses)}):")
for fid in sorted(rew_focuses - dev_focuses):
    print("  ", fid)

print(f"In Dev but not in Rew ({len(dev_focuses - rew_focuses)}):")
for fid in sorted(dev_focuses - rew_focuses):
    print("  ", fid)
