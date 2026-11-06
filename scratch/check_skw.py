import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- Searching for Second_Korean_War ---")
for root, dirs, files in os.walk(mod_dir):
    for f in files:
        if f.endswith((".txt", ".yml")):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                for idx, line in enumerate(file, 1):
                    if "Second_Korean_War" in line:
                        print(f"{os.path.relpath(p, mod_dir)}:{idx}: {line.strip()}")
