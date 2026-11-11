with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_Initial_Emergency.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

def extract_focus(text, fid):
    idx = text.find(f"id = {fid}")
    if idx == -1:
        return None
    # backtrack to "focus = {"
    start = text.rfind("focus = {", 0, idx)
    # forward match braces
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

for fid in min_yuen_ids:
    blk = extract_focus(rew, fid)
    print(f"=== {fid} ===")
    if blk:
        print(blk[:250] + "...\n")
    else:
        print("NOT FOUND!\n")
