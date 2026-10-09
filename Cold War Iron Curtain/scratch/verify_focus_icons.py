import os, re

base = r"."
all_sprites = set()
for f in os.listdir("interface"):
    if f.endswith(".gfx"):
        with open(os.path.join("interface", f), "r", encoding="utf-8", errors="ignore") as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

focus_30 = [
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

replacements = {
    'GFX_Generic_National_Focus_Diplomacy_34': 'GFX_generic_focus_diplomacy_microphone',
    'GFX_Generic_National_Focus_Politics_49': 'GFX_generic_focus_politics_press_statement',
    'GFX_Generic_National_Focus_Diplomacy_41': 'GFX_generic_focus_diplomacy_chinese_hotline',
    'GFX_MLA_Marx-Sun_Yat-Sen-Chin_Peng': 'GFX_Generic_Communism',
    'GFX_Generic_National_Focus_Diplomacy_3': 'GFX_generic_focus_diplomacy_kuomintang_salute'
}

all_valid = True
for fid in focus_30:
    m = re.search(r'id\s*=\s*' + fid + r'\b[\s\S]*?(?=\n\tfocus\s*=\s*\{|\Z)', rew)
    icon = re.search(r'icon\s*=\s*(\S+)', m.group(0)).group(1)
    if icon in replacements:
        icon = replacements[icon]
    exists = icon in all_sprites
    if not exists:
        all_valid = False
    print(f"{fid:40} -> {icon:45} (exists: {exists})")

print(f"\nALL 30 FOCUS ICONS VALID: {all_valid}")
