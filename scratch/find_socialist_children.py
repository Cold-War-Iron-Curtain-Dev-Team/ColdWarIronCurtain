import re

with open("common/national_focus/MLA_50s.txt", "r", encoding="utf-8") as f:
    dev = f.read()

def find_descendants(root_id):
    descendants = []
    for m in re.finditer(r'focus\s*=\s*\{([\s\S]*?)(?=\n\tfocus\s*=\s*\{|\n\}\s*$)', dev):
        block = m.group(1)
        fid = re.search(r'id\s*=\s*([a-zA-Z0-9_\-]+)', block).group(1)
        prereqs = re.findall(r'prerequisite\s*=\s*\{[^}]*?focus\s*=\s*([a-zA-Z0-9_\-]+)', block)
        if root_id in prereqs:
            descendants.append(fid)
    return descendants

print("Direct children of MLA_Our_Place_in_the_Socialist_World:")
for ch in find_descendants('MLA_Our_Place_in_the_Socialist_World'):
    print("  ", ch)
