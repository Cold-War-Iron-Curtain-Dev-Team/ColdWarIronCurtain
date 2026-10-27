import re

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

with open("common/national_focus/MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
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

min_yuen_ids = [
    'MLA_Expand_Min_Yuen', 'MLA_Maintain_Marxist_Purity', 'MLA_Radical_China', 'MLA_Promote_Nanyang',
    'MLA_Maintain_Sinophilic_Views', 'MLA_Enforce_Revolutionary', 'MLA_Ditch_Non-Chinese',
    'MLA_A_Pragmatic_Future', 'MLA_Recruit_Naryanan', 'MLA_Tolerate_non_Marxist_Views',
    'MLA_Expand_Non-Chinese_Supporter_Bases', 'MLA_Resolve_Racial_Inequality', 'MLA_All_Together'
]

blocks = []
for fid in min_yuen_ids:
    blk = extract_focus(rew, fid)
    if fid == 'MLA_Expand_Min_Yuen':
        blk = blk.replace('GFX_Generic_National_Focus_Military_3', 'GFX_generic_focus_military_field_manual')
        # add mutual exclusivity with the legacy 2
        # insert mutually_exclusive before completion_reward
        insert_pos = blk.find("completion_reward")
        mut_block = "mutually_exclusive = {\n\t\t\tfocus = MLA_Show_the_Malay_a_Better_Future\n\t\t\tfocus = MLA_Show_Ethnic_Chinese_the_Rights_of_Humans\n\t\t}\n\t\t"
        blk = blk[:insert_pos] + mut_block + blk[insert_pos:]
    blocks.append(blk)

# Legacy 2 focuses
chinese_rights = extract_focus(dev, 'MLA_Show_Ethnic_Chinese_the_Rights_of_Humans')
# adjust x and mutually_exclusive
chinese_rights = re.sub(r'x\s*=\s*-2', 'x = -5', chinese_rights)
# add MLA_Expand_Min_Yuen to mutually_exclusive
chinese_rights = chinese_rights.replace('focus = MLA_Show_the_Malay_a_Better_Future', 'focus = MLA_Show_the_Malay_a_Better_Future\n\t\t\tfocus = MLA_Expand_Min_Yuen')
blocks.append(chinese_rights)

malay_future = extract_focus(dev, 'MLA_Show_the_Malay_a_Better_Future')
malay_future = re.sub(r'x\s*=\s*2', 'x = 5', malay_future)
malay_future = malay_future.replace('focus = MLA_Show_Ethnic_Chinese_the_Rights_of_Humans', 'focus = MLA_Show_Ethnic_Chinese_the_Rights_of_Humans\n\t\t\tfocus = MLA_Expand_Min_Yuen')
blocks.append(malay_future)

# MLA_Show_the_British_a_Way_Out
british_out = extract_focus(dev, 'MLA_Show_the_British_a_Way_Out')
# update relative_position_id, prerequisite, and y
british_out_new = """focus = {
		id = MLA_Show_the_British_a_Way_Out
		icon = GFX_Show_the_British_the_Way_Out
		search_filters = {
			IC_FILTER
		}
		cost = 10
		relative_position_id = MLA_Expand_Min_Yuen
		prerequisite = {
			focus = MLA_Maintain_Marxist_Purity
			focus = MLA_A_Pragmatic_Future
			focus = MLA_Show_the_Malay_a_Better_Future
			focus = MLA_Show_Ethnic_Chinese_the_Rights_of_Humans
		}
		x = 0
		y = 5
		completion_reward = {
			MAL = {
				add_manpower = -1000
				add_war_support = -0.05
				add_ideas = Government_Extremely_Unpopular
			}
		}
	}"""
blocks.append(british_out_new)

all_new_text = "\n\t".join(blocks)

# Target in dev is from start of MLA_Show_Ethnic_Chinese_the_Rights_of_Humans to end of MLA_Show_the_British_a_Way_Out
start_target = dev.find("id = MLA_Show_Ethnic_Chinese_the_Rights_of_Humans")
start_target = dev.rfind("focus = {", 0, start_target)

end_target = dev.find("id = MLA_Raid_Perak")
end_target = dev.rfind("focus = {", 0, end_target)

target_content = dev[start_target:end_target].rstrip()

new_content = dev[:start_target] + all_new_text + "\n\t" + dev[end_target:]

# Check brackets
open_b = new_content.count('{')
close_b = new_content.count('}')
print(f"Brackets: {open_b} open, {close_b} close. Diff: {open_b - close_b}")

with open("scratch/preview_emergency.txt", "w", encoding="utf-8") as out:
    out.write(new_content)
print("Saved scratch/preview_emergency.txt")
