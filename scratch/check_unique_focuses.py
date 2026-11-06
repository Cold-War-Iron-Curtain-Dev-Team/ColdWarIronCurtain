import re

with open("scratch/preview_emergency.txt", "r", encoding="utf-8") as f:
    text = f.read()

focus_defs = []
for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', text):
    fid_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', m.group(1))
    if fid_m:
        focus_defs.append(fid_m.group(1))

print(f"Total focus definitions: {len(focus_defs)}")
seen = set()
dups = []
for fid in focus_defs:
    if fid in seen:
        dups.append(fid)
    seen.add(fid)

print("Duplicate focus IDs:", dups)
