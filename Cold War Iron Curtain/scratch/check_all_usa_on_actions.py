with open('Cold War Iron Curtain/common/on_actions/00_on_actions.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = re.findall(r'usa\.[0-9]+', text)
print("All USA events in 00_on_actions.txt:", sorted(set(matches)))
