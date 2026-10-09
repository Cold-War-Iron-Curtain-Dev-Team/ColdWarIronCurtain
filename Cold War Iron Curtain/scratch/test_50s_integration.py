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

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    dev = f.read()

def extract_focus(text, fid):
    idx = text.find(f"id = {fid}")
    if idx == -1:
        return None
    start = text.rfind("focus = {", 0, idx)
    depth = 0
    end = start
    for i in range(start, len(text)):
        if text[i] == '{':
            depth += 1
        elif text[i] == '}':
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return text[start:end]

focus_30 = [
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
    'MLA_Tridemism_is_Chinese_Socialism', 'MLA_White_Sun_Over_Malaya'
]

icon_replacements = {
    'MLA_Seek_Alternative_Paths': 'GFX_generic_focus_diplomacy_microphone',
    'MLA_Support_Boestamamites': 'GFX_Generic_Indonesia',
    'MLA_Purge_Maoist_Hardliners_NPLA': 'GFX_generic_focus_diplomacy_anti_mao',
    'MLA_Malayanize_Ex_Communists': 'GFX_generic_focus_politics_hammer_and_sickle_wreath',
    'MLA_Embrace_Indo-Melayu_Raya_Ideas': 'GFX_generic_focus_politics_press_statement',
    'MLA_Emulate_Sukarno_Regime': 'GFX_PRC_50s_Make_Friends_with_Sukarno_Regime',
    'MLA_Enforce_Pansicalla_Ideals': 'GFX_Generic_Indonesia1',
    'MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades': 'GFX_Pardon_Japanese_Collaborators',
    'MLA_Adopt_Marhaenism': 'GFX_Legitimize_Rural_Secret_Cults',
    'MLA_Paving_The_Way_for_Greater_Indo-Malay': 'GFX_Generic_Indonesia2',
    'MLA_Support_Syndicalists': 'GFX_generic_focus_politics_hammer_and_sickle',
    'MLA_Syndies_Takeover': 'GFX_MLA_Syndies_Takeover',
    'MLA_Collaborating_Shamsiah_Fakeh': 'GFX_MLA_Collaborating_Shamsiah_Fakeh',
    'MLA_Diversify_NPLA': 'GFX_MLA_Diversify_NPLA',
    'MLA_Ditching_Sinophilic_Views': 'GFX_MLA_Ditching_Sinophilic_Views',
    'MLA_Formation_Syndicalist_System': 'GFX_MLA_Formation_Syndicalist_System',
    'MLA_Enforce_Syndicalization': 'GFX_MLA_Enforce_Syndicalization',
    'MLA_Purge_Chin_Goons': 'GFX_MLA_Purge_Chin_Goons',
    'MLA_Syndicalism_More_Marxism': 'GFX_MLA_Syndicalism_More_Marxism',
    'MLA_New_Managament': 'GFX_MLA_New_Managament',
    'MLA_Declare_Nanyang': 'GFX_generic_focus_diplomacy_chinese_hotline',
    'MLA_Under_the_White_Sun': 'GFX_Generic_ROC_1',
    'MLA_Demaoistization_of_NPLA': 'GFX_generic_focus_diplomacy_anti_mao',
    'MLA_Marx-Sun_Yat-Sen-Chin_Peng': 'GFX_Generic_Communism',
    'MLA_Mimicking_KMT_Policies': 'GFX_AcademyForStudyOnRevolution',
    'MLA_Infuse_Tridemism_with_Socialism': 'GFX_generic_espionage',
    'MLA_Enfore_New_Direction_NLA': 'TIB_KMT_50s_Encourage_TIP_Membership',
    'MLA_Rebrand_Party_Vision_and_Future': 'GFX_generic_focus_politics_backroom_deal',
    'MLA_Tridemism_is_Chinese_Socialism': 'GFX_generic_espionage',
    'MLA_White_Sun_Over_Malaya': 'GFX_generic_focus_diplomacy_kuomintang_salute'
}

# Check all 30 icons are valid
for fid, ic in icon_replacements.items():
    assert ic in all_sprites, f"Icon {ic} for {fid} not in sprites!"

# Extract and patch the 30 focuses from rew
processed_30 = {}
for fid in focus_30:
    blk = extract_focus(rew, fid)
    assert blk is not None, f"Could not extract {fid} from rew"
    # replace icon
    old_icon = re.search(r'icon\s*=\s*(\S+)', blk).group(1)
    new_icon = icon_replacements[fid]
    blk = re.sub(r'icon\s*=\s*' + re.escape(old_icon), f'icon = {new_icon}', blk, count=1)
    processed_30[fid] = blk

# Updated MLA_Chairman_Chin_Peng
updated_chin_peng = """focus = {
		id = MLA_Chairman_Chin_Peng
		icon = GFX_MLA_Chairman_Chin_Peng
		cost = 1
		search_filters = {
			IC_FILTER
		}
		relative_position_id = MLA_Found_the_Peoples_Republic_of_Malaysia
		allow_branch = { 
			OR = {
				has_country_flag = MLA_Marxist_Purity
				NOT = { has_country_flag = MLA_Pragmatic_Future }
			}
		}
		prerequisite = {
			focus = MLA_Found_the_Peoples_Republic_of_Malaysia
		}
		x = 0
		y = 1
		completion_reward = {
			add_political_power = 150
		}
	}"""

# In dev, replace MLA_Chairman_Chin_Peng with:
# MLA_Seek_Alternative_Paths
# updated_chin_peng
# Boestamam focuses (MLA_Support_Boestamamites ... MLA_Paving_The_Way_for_Greater_Indo-Malay)
# Syndicalist focuses (MLA_Support_Syndicalists ... MLA_New_Managament)
# KMT focuses (MLA_Declare_Nanyang ... MLA_White_Sun_Over_Malaya)

boestamam_order = [
    'MLA_Support_Boestamamites', 'MLA_Purge_Maoist_Hardliners_NPLA',
    'MLA_Malayanize_Ex_Communists', 'MLA_Embrace_Indo-Melayu_Raya_Ideas', 'MLA_Emulate_Sukarno_Regime',
    'MLA_Enforce_Pansicalla_Ideals', 'MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades',
    'MLA_Adopt_Marhaenism', 'MLA_Paving_The_Way_for_Greater_Indo-Malay'
]

syndies_order = [
    'MLA_Support_Syndicalists', 'MLA_Syndies_Takeover', 'MLA_Collaborating_Shamsiah_Fakeh',
    'MLA_Diversify_NPLA', 'MLA_Ditching_Sinophilic_Views', 'MLA_Formation_Syndicalist_System',
    'MLA_Enforce_Syndicalization', 'MLA_Purge_Chin_Goons', 'MLA_Syndicalism_More_Marxism', 'MLA_New_Managament'
]

kmt_order = [
    'MLA_Declare_Nanyang', 'MLA_Under_the_White_Sun', 'MLA_Demaoistization_of_NPLA',
    'MLA_Marx-Sun_Yat-Sen-Chin_Peng', 'MLA_Mimicking_KMT_Policies', 'MLA_Infuse_Tridemism_with_Socialism',
    'MLA_Enfore_New_Direction_NLA', 'MLA_Rebrand_Party_Vision_and_Future',
    'MLA_Tridemism_is_Chinese_Socialism', 'MLA_White_Sun_Over_Malaya'
]

all_to_insert = [
    processed_30['MLA_Seek_Alternative_Paths'],
    updated_chin_peng,
    *[processed_30[f] for f in boestamam_order],
    *[processed_30[f] for f in syndies_order],
    *[processed_30[f] for f in kmt_order]
]

assembled_block = "\n\t".join(all_to_insert)

# Find MLA_Chairman_Chin_Peng in dev
chin_peng_dev = extract_focus(dev, 'MLA_Chairman_Chin_Peng')
assert chin_peng_dev is not None

new_50s = dev.replace(chin_peng_dev, assembled_block, 1)

open_b = new_50s.count('{')
close_b = new_50s.count('}')
print(f"Brackets: {open_b} open, {close_b} close. Diff: {open_b - close_b}")

with open("scratch/preview_50s.txt", "w", encoding="utf-8") as out:
    out.write(new_50s)
print("Saved scratch/preview_50s.txt")
