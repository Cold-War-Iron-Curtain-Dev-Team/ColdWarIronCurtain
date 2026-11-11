with open('Cold War Iron Curtain/common/scripted_effects/CWIC_Super_Event_Scripted_Effects.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
effects = re.findall(r'([a-zA-Z0-9_]+_super_event)\s*=\s*\{', text)
for e in sorted(effects):
    if any(k in e for k in ['elect', 'president', 'trump', 'anderson', 'baker', 'connally', 'dole', 'landgrebe', 'mcdonald', 'rockefeller', 'agnew', 'muskie', 'shriver', 'wilson', 'bush', 'mondale', 'kennedy', 'ford', 'reagan', 'hart', 'glenn', 'clinton', 'brooke', 'bradley', 'dukakis', 'jackson', 'robertson', 'rumsfeld', 'gingrich', 'inoyue']):
        print(e)
