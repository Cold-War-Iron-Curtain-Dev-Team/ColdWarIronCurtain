import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

def check_file(relpath, pattern):
    p = os.path.join(mod_dir, relpath)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            for idx, line in enumerate(f, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    print(f"{relpath}:{idx}: {line.strip()}")

print("--- 1. USA_Halleck_1960.txt around Halleck.2 ---")
check_file(r"common\national_focus\USA_Halleck_1960.txt", r"Halleck")

print("\n--- 2. USA_Dewey_1952.txt around Dewey.11 ---")
check_file(r"common\national_focus\USA_Dewey_1952.txt", r"Dewey")

print("\n--- 3. USA_Kefauver_1956.txt around USA_BAN_PORN ---")
check_file(r"common\national_focus\USA_Kefauver_1956.txt", r"PORN")

print("\n--- 4. Search whole events directory for PORN ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt"):
            check_file(os.path.join(os.path.relpath(root, mod_dir), f), r"PORN")

print("\n--- 5. USA_Reagan_1980.txt around SS_Purge ---")
check_file(r"common\national_focus\USA 1980s\Coded\1980\USA_Reagan_1980.txt", r"SS_Purge")

print("\n--- 6. Search events for Purge ---")
for root, dirs, files in os.walk(os.path.join(mod_dir, "events")):
    for f in files:
        if f.endswith(".txt") and "80" in f:
            check_file(os.path.join(os.path.relpath(root, mod_dir), f), r"Purge")

print("\n--- 7. USA_60s_Diplomatic.txt around Second_Korean_War ---")
check_file(r"common\national_focus\USA_60s_Diplomatic.txt", r"Second_Korean_War")
