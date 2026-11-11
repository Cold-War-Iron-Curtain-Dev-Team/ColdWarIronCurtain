with open('Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/USA_Anderson_1980.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
print("set_politics in Anderson 1980:", re.findall(r'set_politics\s*=\s*\{[^}]+\}', text))
print("ruling_party:", re.findall(r'ruling_party\s*=\s*([a-zA-Z0-9_]+)', text))
print("ideology:", re.findall(r'ideology\s*=\s*([a-zA-Z0-9_]+)', text))
