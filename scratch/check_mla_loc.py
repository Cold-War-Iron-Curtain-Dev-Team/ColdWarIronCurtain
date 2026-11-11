import re

with open("localisation/english/MLA_l_english.yml", "r", encoding="utf-8-sig", errors="ignore") as f:
    text = f.read()

keys = re.findall(r'^\s*([a-zA-Z0-9_\-]+):', text, re.MULTILINE)
print(f"Total keys in MLA_l_english.yml: {len(keys)}")

# Check our 45 keys
to_check = [
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

present = []
missing = []
for k in to_check:
    has_title = k in keys
    has_desc = (k + "_desc") in keys
    if has_title:
        present.append((k, has_desc))
    else:
        missing.append(k)

print(f"\nPresent ({len(present)}):")
for k, d in present:
    print(f"  {k:45} (has desc: {d})")

print(f"\nMissing ({len(missing)}):")
for k in missing:
    print(f"  {k}")
