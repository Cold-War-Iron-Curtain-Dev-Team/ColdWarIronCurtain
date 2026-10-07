import os, re

for year in ['1984', '1988']:
    base = f'Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/{year}'
    for f in sorted(os.listdir(base)):
        if f.endswith('.txt'):
            p = os.path.join(base, f)
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                c = fl.read()
            shared = re.findall(r'shared_focus\s*=\s*([a-zA-Z0-9_]+)', c)
            fp = [s for s in shared if 'FP' in s]
            expected_fp = f'USA_FP{year[-2:]}_The_State_Department'
            if fp and fp[0] != expected_fp:
                print(f"MISMATCH in {year}/{f}: {fp[0]} vs expected {expected_fp}")
