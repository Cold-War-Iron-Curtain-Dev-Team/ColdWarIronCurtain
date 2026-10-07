with open('Cold War Iron Curtain/common/scripted_effects/CWIC_Super_Event_Scripted_Effects.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re

for se in [
    'anderson_gop_elected_super_event',
    'anderson_independent_elected_super_event',
    'president_landgrebe_super_event',
    'president_rockefeller_super_event',
    'president_agnew_super_event',
    'president_muskie_super_event',
    'bush_sr_elected_super_event',
    'mondale_elected_super_event',
    'ted_kennedy_elected_super_event',
    'president_ford_super_event',
    'president_wallace_super_event'
]:
    m = re.search(r'(' + se + r'\s*=\s*\{[^}]+\})', text)
    if m:
        print(f"=== {se} ===")
        print(m.group(1))
