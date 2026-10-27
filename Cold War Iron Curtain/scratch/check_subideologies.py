with open('Cold War Iron Curtain/common/ideologies/00_ideologies.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
m = re.search(r'([a-zA-Z0-9_]+)\s*=\s*\{[^{}]*centrism', text)
if m:
    print("centrism belongs to party:", m.group(1))

m2 = re.search(r'([a-zA-Z0-9_]+)\s*=\s*\{[^{}]*rockefeller_republican', text)
if m2:
    print("rockefeller_republican belongs to party:", m2.group(1))
