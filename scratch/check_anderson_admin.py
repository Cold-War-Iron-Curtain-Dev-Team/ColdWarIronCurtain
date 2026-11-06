with open('Cold War Iron Curtain/events/USA_1980s_Admin_Specific_Events.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = re.findall(r'.{0,50}anderson.{0,50}', text, re.IGNORECASE)
for m in matches[:15]:
    print(m.strip())
