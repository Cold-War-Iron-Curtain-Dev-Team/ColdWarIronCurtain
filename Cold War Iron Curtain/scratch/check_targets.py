import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

targets = [
    "Second_Korean_War", "USA_BAN_PORN", "Dewey", "Halleck", 
    "MacArthur", "civil_rights_truman", "SS_Purge", "Fairness_Doctrine",
    "EnvironmentUSA", "ERA_Extension", "USALGB80s"
]

print("--- SEARCHING EVENTS FOR TARGETS ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as ef:
                content = ef.read()
            for t in targets:
                if t.lower() in content.lower():
                    # Find matching lines
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if t.lower() in line.lower() and ("id = " in line or "namespace" in line):
                            print(f"{f}:{idx+1}: {line.strip()}")
