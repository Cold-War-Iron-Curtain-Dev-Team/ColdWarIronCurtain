import os

for f in ['USA_Dole_1984.txt', 'USA_Haig_1984_First_Term.txt']:
    in_80 = os.path.exists('Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/' + f)
    in_84 = os.path.exists('Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1984/' + f)
    print(f"{f}: in 1980={in_80}, in 1984={in_84}")
