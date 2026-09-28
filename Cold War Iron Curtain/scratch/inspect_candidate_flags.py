import os, re

candidates = [
    ('Connally', 'USA_Connally_1980.txt'),
    ('Baker', 'USA_Baker_1980_First_Term.txt'),
    ('Dole', 'USA_Dole_1980.txt'),
    ('Anderson_GOP', 'USA_Anderson_GOP_1980.txt'),
    ('Anderson_Ind', 'USA_Anderson_1980.txt'),
    ('Agnew', 'USA_Agnew_1980.txt'),
    ('Rockefeller', 'USA_Rockefeller_1980.txt'),
    ('Landgrebe', 'USA_Landgrebe_1980_First_Term.txt'),
    ('Muskie', 'USA_Muskie_1980_First_Term.txt'),
    ('Muskie_2', 'USA_Muskie_1980_Second_Term.txt'),
    ('Shriver', 'USA_Shriver_1980_First_Term.txt'),
    ('Wilson', 'USA_Wilson_1980_First_Term.txt'),
    ('Wallace', 'USA_Wallace_1980_Second_Term.txt'),
]

tree_dir = 'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980'

for label, filename in candidates:
    path = os.path.join(tree_dir, filename)
    if not os.path.exists(path):
        print(f"MISSING: {filename}")
        continue
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    tree_id = re.search(r'id\s*=\s*([a-zA-Z0-9_]+)', content).group(1)
    # search for any flags checked or set
    flags_checked = set(re.findall(r'has_global_flag\s*=\s*([a-zA-Z0-9_]+)', content))
    flags_set = set(re.findall(r'set_global_flag\s*=\s*([a-zA-Z0-9_]+)', content))
    print(f"=== {label} ({tree_id}) ===")
    print(f"  Flags checked: {flags_checked}")
    print(f"  Flags set: {flags_set}")
