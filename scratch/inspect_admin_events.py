with open('Cold War Iron Curtain/events/USA_1980s_Admin_Specific_Events.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
events = re.findall(r'(country_event|news_event)\s*=\s*\{\s*id\s*=\s*([a-zA-Z0-9_\.]+)', text)
print(f"Total events in USA_1980s_Admin_Specific_Events.txt: {len(events)}")
for t, eid in events[:30]:
    print(f"  {t:15} {eid}")
