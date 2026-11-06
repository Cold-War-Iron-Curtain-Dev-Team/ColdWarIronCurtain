import os, re
sprites = set()
for f in os.listdir('interface'):
    if f.endswith('.gfx'):
        with open(os.path.join('interface', f), 'r', encoding='utf-8', errors='ignore') as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                sprites.add(m.group(1))

candidates = [
    'GFX_generic_focus_politics_red_banner',
    'GFX_generic_focus_politics_cabinet_meeting',
    'GFX_generic_focus_politics_armed_communism',
    'GFX_generic_focus_politics_hammer_and_sickle',
    'GFX_generic_focus_politics_hammer_and_sickle_wreath',
    'GFX_generic_focus_politics_backroom_deal',
    'GFX_generic_focus_diplomacy_anti_mao',
    'GFX_Army_Purge',
    'GFX_Generic_Indonesia',
    'GFX_Generic_Indonesia1',
    'GFX_Generic_Indonesia2',
    'GFX_INO_Establish_the_Basic_Foundation_of_Indonesian_Democracy',
    'GFX_generic_focus_military_field_manual'
]

for c in candidates:
    print(f'{c:60} -> {c in sprites}')
