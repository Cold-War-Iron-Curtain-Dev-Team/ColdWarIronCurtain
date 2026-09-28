with open('Cold War Iron Curtain/common/national_focus/USA 1980s/Coded/1980/USA_Anderson_1980.txt', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        if 'id = USA_ANDERSON80_' in line:
            print(line.strip())
