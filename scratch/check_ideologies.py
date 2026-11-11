with open('Cold War Iron Curtain/common/ideologies/00_ideologies.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
parties = re.findall(r'([a-zA-Z0-9_]+)\s*=\s*\{\s*types\s*=', text)
print("Parties defined:", parties)
print("Has centrism:", "centrism" in text)
print("Has liberal:", "liberal" in text)
