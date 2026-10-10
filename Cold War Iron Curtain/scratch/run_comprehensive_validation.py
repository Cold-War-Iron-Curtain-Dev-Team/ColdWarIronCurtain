import os, re

base = r"."

print("=" * 60)
print("COMPREHENSIVE VALIDATION SUITE - MLA CONTENT")
print("=" * 60)

# 1. Bracket Check
files_to_bracket_check = [
    "common/national_focus/MLA_Initial_Emergency.txt",
    "common/national_focus/MLA_50s.txt",
    "events/MLA.txt",
    "common/ideas/MLA_ideas.txt",
    "common/scripted_effects/MLA_scripted_effects.txt",
    "common/scripted_effects/IC_Malaya_Effects.txt",
    "common/scripted_triggers/MLA_scripted_triggers.txt",
    "common/scripted_guis/MLA_gui.txt",
    "common/scripted_localisation/MLA_scripted_localisation.txt",
    "common/decisions/MLA.txt",
    "common/decisions/categories/MLA_decision_categories.txt",
    "interface/MLA_GUI.gfx",
    "interface/MLA_GUI.gui",
    "interface/IC_goals.gfx",
    "history/countries/MLA - Malaya.txt"
]

bracket_errors = 0
for fpath in files_to_bracket_check:
    if not os.path.exists(fpath):
        print(f"[FAIL] Missing file: {fpath}")
        bracket_errors += 1
        continue
    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
        txt = fp.read()
    # strip comments
    clean_txt = re.sub(r'#.*$', '', txt, flags=re.MULTILINE)
    o = clean_txt.count('{')
    c = clean_txt.count('}')
    if o != c:
        print(f"[FAIL] Bracket mismatch in {fpath}: {o} open vs {c} close (diff: {o - c})")
        bracket_errors += 1
    else:
        print(f"[OK] Brackets balanced in {fpath} ({o} pairs)")

# 2. UTF-8 BOM Check
bom_files = [
    "localisation/english/MLA_l_english.yml",
    "localisation/english/MAL_l_english.yml"
]
bom_errors = 0
for fpath in bom_files:
    with open(fpath, "rb") as fp:
        raw = fp.read(3)
        if raw != b'\xef\xbb\xbf':
            print(f"[FAIL] BOM missing in {fpath}")
            bom_errors += 1
        else:
            print(f"[OK] UTF-8 BOM verified in {fpath}")

# 3. Sprite Definition Check
all_sprites = set()
for f in os.listdir("interface"):
    if f.endswith(".gfx"):
        with open(os.path.join("interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

sprite_errors = 0
for fpath in ["common/national_focus/MLA_Initial_Emergency.txt", "common/national_focus/MLA_50s.txt"]:
    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
        txt = fp.read()
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', txt):
        blk = m.group(1)
        fid_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', blk)
        icon_m = re.search(r'\bicon\s*=\s*([a-zA-Z0-9_\-]+)', blk)
        if fid_m and icon_m:
            fid = fid_m.group(1)
            icon = icon_m.group(1)
            if icon not in all_sprites:
                print(f"[FAIL] Missing sprite '{icon}' in focus '{fid}' ({fpath})")
                sprite_errors += 1

if sprite_errors == 0:
    print(f"[OK] All focus sprites exist in interface/*.gfx")

# 4. Focus Tree Internal Consistency Check (prerequisites and mutual exclusives)
tree_errors = 0
for fpath in ["common/national_focus/MLA_Initial_Emergency.txt", "common/national_focus/MLA_50s.txt"]:
    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
        txt = fp.read()
    focuses = set()
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', txt):
        fid_m = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', m.group(1))
        if fid_m:
            focuses.add(fid_m.group(1))
    
    # Now check prereqs
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', txt):
        blk = m.group(1)
        fid = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', blk).group(1)
        # Check prerequisites
        for p in re.finditer(r'focus\s*=\s*([a-zA-Z0-9_\-]+)', blk):
            # Exclude self
            prereq_id = p.group(1)
            # Find if this occurrence is inside prerequisite = { } or mutually_exclusive = { }
            start_p = p.start()
            # check enclosing block
            sub = blk[:start_p]
            last_prereq = sub.rfind("prerequisite =")
            last_mut = sub.rfind("mutually_exclusive =")
            if last_prereq > last_mut and prereq_id not in focuses:
                print(f"[FAIL] In {fid}: prerequisite focus '{prereq_id}' does not exist in {fpath}!")
                tree_errors += 1
            elif last_mut > last_prereq and prereq_id not in focuses:
                print(f"[FAIL] In {fid}: mutually exclusive focus '{prereq_id}' does not exist in {fpath}!")
                tree_errors += 1

if tree_errors == 0:
    print(f"[OK] Focus prerequisites and mutual exclusivity internally consistent")

# 5. Localization Coverage Check
all_loc_keys = set()
for f in os.listdir("localisation/english"):
    if f.endswith(".yml"):
        with open(os.path.join("localisation/english", f), "r", encoding="utf-8", errors="ignore") as fp:
            for k in re.findall(r'^\s*([a-zA-Z0-9_\-]+):', fp.read(), re.MULTILINE):
                all_loc_keys.add(k)

loc_errors = 0
for fpath in ["common/national_focus/MLA_Initial_Emergency.txt", "common/national_focus/MLA_50s.txt"]:
    with open(fpath, "r", encoding="utf-8", errors="ignore") as fp:
        txt = fp.read()
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', txt):
        fid = re.search(r'\bid\s*=\s*([a-zA-Z0-9_\-]+)', m.group(1)).group(1)
        if fid not in all_loc_keys:
            print(f"[FAIL] Missing loc title for focus '{fid}' ({fpath})")
            loc_errors += 1

if loc_errors == 0:
    print(f"[OK] All focuses have localization titles")

print("=" * 60)
print(f"SUMMARY: Bracket Errors: {bracket_errors} | BOM Errors: {bom_errors} | Sprite Errors: {sprite_errors} | Tree Errors: {tree_errors} | Loc Errors: {loc_errors}")
print("=" * 60)
