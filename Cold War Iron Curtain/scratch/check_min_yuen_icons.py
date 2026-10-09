import os, re

all_sprites = set()
for f in os.listdir('interface'):
    if f.endswith('.gfx'):
        with open(os.path.join('interface', f), 'r', encoding='utf-8', errors='ignore') as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                all_sprites.add(m.group(1))

min_yuen_icons = [
    'GFX_Generic_National_Focus_Military_3',
    'GFX_Chinese_rightsMLA',
    'GFX_MLA_Radical_China',
    'GFX_MLA_Promote_Nanyang',
    'GFX_MLA_Maintain_Sinophilic_Views',
    'GFX_MLA_Enforce_Revolutionary',
    'GFX_MLA_Ditch_Non-Chinese',
    'GFX_Malay_a_better_future',
    'GFX_MLA_Recruit_Naryanan',
    'GFX_MLA_Tolerate_non_Marxist_Views',
    'GFX_MLA_Expand_Non-Chinese_Supporter_Bases',
    'GFX_MLA_Resolve_Racial_Inequality',
    'GFX_All_together',
    'GFX_MLA_Maintain_Marxist_Purity',
    'GFX_MLA_A_Pragmatic_Future'
]

for ic in min_yuen_icons:
    print(f'{ic:45} -> {ic in all_sprites}')
