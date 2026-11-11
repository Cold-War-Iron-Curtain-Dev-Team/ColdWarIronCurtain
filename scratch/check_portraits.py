import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

names = ["connally", "baker", "dole", "anderson", "agnew", "rockefeller", "landgrebe", "muskie", "shriver", "wallace"]

for root, dirs, files in os.walk(os.path.join(mod_dir, "gfx", "leaders", "USA")):
    for f in files:
        fl = f.lower()
        for n in names:
            if n in fl:
                print(f"{n:12}: {f}")
