import os, re

tree_dir = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980'
for f in sorted(os.listdir(tree_dir)):
    if f.endswith('.txt'):
        fp = os.path.join(tree_dir, f)
        with open(fp, 'r', encoding='utf-8', errors='ignore') as fl:
            text = fl.read()
            m_tree = re.search(r'id\s*=\s*([a-zA-Z0-9_]+)', text)
            tree_id = m_tree.group(1) if m_tree else '?'
            
            # Find any set_politics or ideology or admin focus
            admin_focus = re.search(r'id = (USA_[A-Z0-9]+_The_[A-Za-z0-9_]+)', text)
            admin_name = admin_focus.group(1) if admin_focus else 'none'
            print(f"{f:32} | {tree_id:28} | {admin_name}")
