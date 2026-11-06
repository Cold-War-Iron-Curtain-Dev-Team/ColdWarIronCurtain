import os, re

base = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"
rew = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA"

focus_list = [
    'MLA_Seek_Alternative_Paths', 'MLA_Support_Boestamamites', 'MLA_Purge_Maoist_Hardliners_NPLA',
    'MLA_Malayanize_Ex_Communists', 'MLA_Embrace_Indo', 'MLA_Emulate_Sukarno_Regime',
    'MLA_Enforce_Pansicalla_Ideals', 'MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades',
    'MLA_Adopt_Marhaenism', 'MLA_Paving_The_Way_for_Greater_Indo', 'MLA_Support_Syndicalists',
    'MLA_Syndies_Takeover', 'MLA_Collaborating_Shamsiah_Fakeh', 'MLA_Diversify_NPLA',
    'MLA_Ditching_Sinophilic_Views', 'MLA_Formation_Syndicalist_System', 'MLA_Enforce_Syndicalization',
    'MLA_Purge_Chin_Goons', 'MLA_Syndicalism_More_Marxism', 'MLA_New_Managament',
    'MLA_Declare_Nanyang', 'MLA_Under_the_White_Sun', 'MLA_Demaoistization_of_NPLA',
    'MLA_Marx', 'MLA_Mimicking_KMT_Policies', 'MLA_Infuse_Tridemism_with_Socialism',
    'MLA_Enfore_New_Direction_NLA', 'MLA_Rebrand_Party_Vision_and_Future',
    'MLA_Tridemism_is_Chinese_Socialism', 'MLA_White_Sun_Over_Malaya'
]

with open(os.path.join(rew, "common/national_focus/MLA_50s.txt"), "r", encoding="utf-8", errors="ignore") as fp:
    rew_50s = fp.read()

# Load all gfx
all_gfx = ""
for f in os.listdir(os.path.join(base, "interface")):
    if f.endswith(".gfx"):
        with open(os.path.join(base, "interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            all_gfx += fp.read()

# Load all loc
all_loc = ""
loc_dir = os.path.join(base, "localisation/english")
for f in os.listdir(loc_dir):
    if f.endswith(".yml"):
        with open(os.path.join(loc_dir, f), "r", encoding="utf-8", errors="ignore") as fp:
            all_loc += fp.read()

print("AUDITING 30 FOCUSES IN MLA_50s:")
for fid in focus_list:
    m = re.search(r'id\s*=\s*' + fid + r'[\s\S]*?(?=focus\s*=\s*\{|\Z)', rew_50s)
    if not m:
        print(f"ERROR: {fid} not found in rew_50s")
        continue
    block = m.group(0)
    icon_m = re.search(r'icon\s*=\s*([a-zA-Z0-9_\-]+)', block)
    icon = icon_m.group(1) if icon_m else "NO_ICON"
    icon_exists = icon in all_gfx
    loc_title = fid + ":" in all_loc or fid + "_desc:" in all_loc
    print(f"{fid:40} | icon: {icon:35} (exists: {icon_exists}) | loc: {loc_title}")
