import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- MacArthur loc search ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "localisation", "english")):
    for f in files:
        if f.endswith(".yml"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "macarthur.6" in content.lower():
                    for idx, line in enumerate(content.splitlines(), 1):
                        if "macarthur.6" in line.lower():
                            print(f"{f}:{idx}: {line.strip()}")
