import os, re
sprites = set()
for f in os.listdir('interface'):
    if f.endswith('.gfx'):
        with open(os.path.join('interface', f), 'r', encoding='utf-8', errors='ignore') as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                sprites.add(m.group(1))

def find_matches(pattern):
    return [s for s in sorted(sprites) if re.search(pattern, s, re.IGNORECASE) and not s.endswith('_shine')]

print('generic_focus_politics:')
print(find_matches(r'generic_focus_politics_')[:20])

print('\ngeneric_focus_diplomacy:')
print(find_matches(r'generic_focus_diplomacy_')[:20])

print('\ngeneric_focus_military:')
print(find_matches(r'generic_focus_military_')[:20])

print('\ngeneric_focus_industry:')
print(find_matches(r'generic_focus_industry_')[:20])

print('\nMarx / Lenin / Mao / Socialism:')
print(find_matches(r'marx|socialis|purge|red_star|hammer')[:25])
