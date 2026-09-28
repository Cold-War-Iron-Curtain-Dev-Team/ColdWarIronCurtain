import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

for root, dirs, files in os.walk(mod_dir):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "USA_Eisenhower_1952" in content:
                    for idx, line in enumerate(content.splitlines(), 1):
                        if "USA_Eisenhower_1952" in line:
                            print(f"{os.path.relpath(p, mod_dir)}:{idx}: {line.strip()}")
