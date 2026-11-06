import os, re

base = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

# Check goal image files on disk
mla_goal_dir = os.path.join(base, "gfx/interface/goals/MLA/50s")
if os.path.exists(mla_goal_dir):
    print("Files in gfx/interface/goals/MLA/50s:")
    for f in os.listdir(mla_goal_dir):
        print(" ", f)

# Check all spriteType in interface/*.gfx
all_sprites = set()
for f in os.listdir(os.path.join(base, "interface")):
    if f.endswith(".gfx"):
        with open(os.path.join(base, "interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

print("\nChecking specific sprites:")
targets = [
    "GFX_Generic_National_Focus_Diplomacy_34",
    "GFX_Generic_National_Focus_Politics_49",
    "GFX_Generic_National_Focus_Diplomacy_41",
    "GFX_MLA_Marx-Sun_Yat-Sen-Chin_Peng",
    "GFX_Generic_National_Focus_Diplomacy_3",
    "GFX_Generic_National_Focus_Military_3",
    "GFX_Chinese_rightsMLA",
    "GFX_Malay_a_better_future",
    "GFX_MLA_Maintain_Marxist_Purity",
    "GFX_MLA_A_Pragmatic_Future"
]

for t in targets:
    print(f"{t}: exists={t in all_sprites}")

# Check generic diplomacy sprites that exist
print("\nSome Generic_National_Focus_Diplomacy sprites:")
dip = [s for s in all_sprites if "diplomacy" in s.lower()]
print(dip[:15])

print("\nSome Generic_National_Focus_Politics sprites:")
pol = [s for s in all_sprites if "politics" in s.lower()]
print(pol[:15])
