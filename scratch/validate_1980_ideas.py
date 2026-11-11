import os, re

base = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980'

# Gather all ideas defined in common/ideas/
all_ideas = set()
for root, dirs, files in os.walk('Cold War Iron Curtain/common/ideas'):
    for f in files:
        if f.endswith('.txt'):
            with open(os.path.join(root, f), 'r', encoding='utf-8', errors='ignore') as fl:
                for line in fl:
                    m = re.match(r'\s*([a-zA-Z0-9_]+)\s*=\s*\{', line)
                    if m:
                        all_ideas.add(m.group(1))

missing_ideas = {}
for f in sorted(os.listdir(base)):
    if f.endswith('.txt'):
        p = os.path.join(base, f)
        with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
            c = fl.read()
        idea_calls = re.findall(r'(?:add_ideas|swap_ideas|remove_ideas|has_idea)\s*=\s*([a-zA-Z0-9_]+)', c)
        for iid in idea_calls:
            if iid not in all_ideas:
                missing_ideas.setdefault(iid, []).append(f)

print(f"Missing ideas in 1980 trees: {len(missing_ideas)}")
for iid, flist in missing_ideas.items():
    print(f"  {iid}: in {flist}")
