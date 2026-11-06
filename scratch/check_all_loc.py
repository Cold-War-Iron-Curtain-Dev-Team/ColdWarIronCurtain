import os, re

base = r"."
rew = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA"

def search_text_for_keys(text, keys):
    found = {}
    for k in keys:
        m = re.search(r'^\s*' + re.escape(k) + r'[:\s].*$', text, re.MULTILINE)
        if m:
            found[k] = m.group(0).strip()
    return found

# All keys we need
keys_to_find = [
    'MLA_Expand_Min_Yuen', 'MLA_Maintain_Marxist_Purity', 'MLA_Radical_China', 'MLA_Promote_Nanyang',
    'MLA_Maintain_Sinophilic_Views', 'MLA_Enforce_Revolutionary', 'MLA_Ditch_Non-Chinese',
    'MLA_A_Pragmatic_Future', 'MLA_Recruit_Naryanan', 'MLA_Tolerate_non_Marxist_Views',
    'MLA_Expand_Non-Chinese_Supporter_Bases', 'MLA_Resolve_Racial_Inequality', 'MLA_All_Together',
    'MLA_Seek_Alternative_Paths', 'MLA_Support_Boestamamites', 'MLA_Purge_Maoist_Hardliners_NPLA',
    'MLA_Malayanize_Ex_Communists', 'MLA_Embrace_Indo-Melayu_Raya_Ideas', 'MLA_Emulate_Sukarno_Regime',
    'MLA_Enforce_Pansicalla_Ideals', 'MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades',
    'MLA_Adopt_Marhaenism', 'MLA_Paving_The_Way_for_Greater_Indo-Malay', 'MLA_Support_Syndicalists',
    'MLA_Syndies_Takeover', 'MLA_Collaborating_Shamsiah_Fakeh', 'MLA_Diversify_NPLA',
    'MLA_Ditching_Sinophilic_Views', 'MLA_Formation_Syndicalist_System', 'MLA_Enforce_Syndicalization',
    'MLA_Purge_Chin_Goons', 'MLA_Syndicalism_More_Marxism', 'MLA_New_Managament',
    'MLA_Declare_Nanyang', 'MLA_Under_the_White_Sun', 'MLA_Demaoistization_of_NPLA',
    'MLA_Marx-Sun_Yat-Sen-Chin_Peng', 'MLA_Mimicking_KMT_Policies', 'MLA_Infuse_Tridemism_with_Socialism',
    'MLA_Enfore_New_Direction_NLA', 'MLA_Rebrand_Party_Vision_and_Future',
    'MLA_Tridemism_is_Chinese_Socialism', 'MLA_White_Sun_Over_Malaya',
    'MLA_Radical_China_Attack', 'MLA_Malayan_Boat_People'
]

# Check existing english
all_eng = ""
for f in os.listdir("localisation/english"):
    if f.endswith(".yml"):
        with open(os.path.join("localisation/english", f), "r", encoding="utf-8", errors="ignore") as fp:
            all_eng += fp.read() + "\n"

# Check french
all_fre = ""
if os.path.exists("localisation/french"):
    for f in os.listdir("localisation/french"):
        if f.endswith(".yml"):
            with open(os.path.join("localisation/french", f), "r", encoding="utf-8", errors="ignore") as fp:
                all_fre += fp.read() + "\n"

# Check reworked MLA
all_rew = ""
if os.path.exists(rew):
    for root, dirs, files in os.walk(rew):
        for f in files:
            if f.endswith(".yml"):
                with open(os.path.join(root, f), "r", encoding="utf-8", errors="ignore") as fp:
                    all_rew += fp.read() + "\n"

print("--- FOUND IN ENGLISH ---")
eng_found = search_text_for_keys(all_eng, keys_to_find)
print(f"Found {len(eng_found)} / {len(keys_to_find)}")
for k, v in eng_found.items():
    print(" ", v[:80])

print("\n--- FOUND IN REWORKED MLA ---")
rew_found = search_text_for_keys(all_rew, keys_to_find)
print(f"Found {len(rew_found)} / {len(keys_to_find)}")
for k, v in rew_found.items():
    print(" ", v[:80])

print("\n--- FOUND IN FRENCH ---")
fre_found = search_text_for_keys(all_fre, keys_to_find)
print(f"Found {len(fre_found)} / {len(keys_to_find)}")
for k, v in fre_found.items():
    print(" ", v[:80])

missing = set(keys_to_find) - set(eng_found.keys()) - set(rew_found.keys())
print("\nMISSING FROM ALL ENGLISH/REW:", missing)
