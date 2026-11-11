with open('Cold War Iron Curtain/events/USA_1980s_Admin_Specific_Events.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = re.findall(r'(country_event|news_event)\s*=\s*\{\s*id\s*=\s*(?:Anderson|GOP_Anderson)[a-zA-Z0-9_\.]+', text)
print(matches)
