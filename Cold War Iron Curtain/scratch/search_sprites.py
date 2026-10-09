import os, re

base = r"."
all_sprites = set()
for f in os.listdir("interface"):
    if f.endswith(".gfx"):
        with open(os.path.join("interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

for query in ['infrastructure', 'communism', 'Recognition', 'APRI', 'political_pressure', 'pressure', 'Indonesia']:
    matches = [s for s in all_sprites if query.lower() in s.lower()]
    print(f"=== {query} ({len(matches)}) ===")
    for m in matches[:8]:
        print(" ", m)
