import os, re

all_sprites = set()
for f in os.listdir("interface"):
    if f.endswith(".gfx"):
        with open(os.path.join("interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

with open("scratch/preview_50s.txt", "r", encoding="utf-8") as f:
    text = f.read()

focus_defs = []
missing_sprites = []
for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', text):
    block = m.group(1)
    fid_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', block)
    if fid_m:
        fid = fid_m.group(1)
        focus_defs.append(fid)
        icon_m = re.search(r'\bicon\s*=\s*([a-zA-Z0-9_\-]+)', block)
        if icon_m:
            icon = icon_m.group(1)
            if icon not in all_sprites:
                missing_sprites.append((fid, icon))

print(f"Total focus definitions in 50s tree: {len(focus_defs)}")
seen = set()
dups = []
for fid in focus_defs:
    if fid in seen:
        dups.append(fid)
    seen.add(fid)

print("Duplicates:", dups)
print(f"Missing sprites ({len(missing_sprites)}):", missing_sprites)
