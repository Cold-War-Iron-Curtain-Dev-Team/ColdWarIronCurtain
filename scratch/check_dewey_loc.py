import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

print("--- DEWEY LOC SEARCH ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "localisation", "english")):
    for f in files:
        if f.endswith(".yml"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                if "Dewey.10" in content or "Dewey.11" in content or "Dewey_Mafia" in content:
                    for idx, line in enumerate(content.splitlines(), 1):
                        if any(k in line for k in ["Dewey.10", "Dewey.11", "Dewey_Mafia"]):
                            print(f"{f}:{idx}: {line.strip()}")
