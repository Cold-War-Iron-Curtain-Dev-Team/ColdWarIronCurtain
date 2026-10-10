import os, re
sprites = set()
for f in os.listdir('interface'):
    if f.endswith('.gfx'):
        with open(os.path.join('interface', f), 'r', encoding='utf-8', errors='ignore') as fp:
            for m in re.finditer(r'name\s*=\s*"([^"]+)"', fp.read()):
                sprites.add(m.group(1))

def find_matches(pattern):
    return [s for s in sorted(sprites) if re.search(pattern, s, re.IGNORECASE)]

print('Pancasila / Indo:')
print(find_matches(r'pancasila|sukarno|indonesia')[:10])

print('\nSyndicalist:')
print(find_matches(r'syndic')[:10])

print('\nCommunism:')
print(find_matches(r'communism|communist')[:15])

print('\nPolitical Pressure / Rebrand:')
print(find_matches(r'political_pressure|press_statement|backroom_deal')[:10])

print('\nInfrastructure / Build:')
print(find_matches(r'infrastructure')[:10])

print('\nINO:')
print(find_matches(r'GFX_INO_')[:15])
