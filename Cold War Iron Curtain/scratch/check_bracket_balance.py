import subprocess, os

files_to_check = [
    'Cold War Iron Curtain/events/USA.txt',
    'Cold War Iron Curtain/events/USA_1980s_Admin_Specific_Events.txt',
    'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/USA_Agnew_1980.txt',
    'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/USA_Landgrebe_1980_First_Term.txt',
    'Cold War Iron Curtain/events/USA_1980s_General_Political.txt',
    'Cold War Iron Curtain/events/Korean_War.txt',
    'Cold War Iron Curtain/events/USA_1950s_Rework_Events.txt',
    'Cold War Iron Curtain/common/ideas/usa.txt',
    'Cold War Iron Curtain/common/national_focus/USA_CIA_50s.txt'
]

for f in files_to_check:
    with open(f, 'r', encoding='utf-8', errors='ignore') as fl:
        content = fl.read()
    
    # remove comments
    clean_lines = []
    for line in content.splitlines():
        idx = line.find('#')
        if idx != -1:
            line = line[:idx]
        clean_lines.append(line)
    clean_content = "\n".join(clean_lines)
    
    open_b = clean_content.count('{')
    close_b = clean_content.count('}')
    if open_b != close_b:
        print(f"ERROR: {f} unbalanced: {open_b} open vs {close_b} close (diff: {open_b - close_b})")
    else:
        print(f"OK: {os.path.basename(f)} ({open_b} braces matched)")
