import re

with open(r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Reworked MLA\common\national_focus\MLA_50s.txt", "r", encoding="utf-8", errors="ignore") as f:
    rew = f.read()

m_start = rew.find("id = MLA_Seek_Alternative_Paths")
m_end = rew.find("id = MLA_Our_Place_in_the_Socialist_World")

print("Length between Seek_Alternative_Paths and Our_Place_in_the_Socialist_World:", m_end - m_start)

# Let's count how many focuses are in that section:
section = rew[m_start:m_end]
focus_ids = re.findall(r'id\s*=\s*([a-zA-Z0-9_\-]+)', section)
print(f"Total focus IDs in section: {len(focus_ids)}")
print(focus_ids)
