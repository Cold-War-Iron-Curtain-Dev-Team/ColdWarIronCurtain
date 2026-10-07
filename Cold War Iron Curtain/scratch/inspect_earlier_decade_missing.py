import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

targets = [
    (r"common\national_focus\USA_60s_Diplomatic.txt", "Second_Korean_War.1"),
    (r"common\national_focus\USA_70s_CIA.txt", "USA_NIC_WAR"),
    (r"common\national_focus\USA_CIA_50s.txt", "Syria_CIA"),
    (r"common\national_focus\USA_CIA_50s.txt", "FF.10"),
    (r"common\national_focus\USA_Dewey_1952.txt", "Dewey.11"),
    (r"common\national_focus\USA_Halleck_1960.txt", "Halleck.2"),
    (r"common\national_focus\USA_Kefauver_1952.txt", "usa_flavor.3"),
    (r"common\national_focus\USA_Kefauver_1956.txt", "USA_BAN_PORN.1"),
    (r"common\national_focus\USA_MacArthur_1952.txt", "MacArthur.6"),
    (r"common\national_focus\USA_Reagen_1972.txt", "Goldwater_UN.1"),
    (r"common\national_focus\USA_Truman_1948.txt", "civil_rights_truman.1")
]

for relpath, term in targets:
    p = os.path.join(mod_dir, relpath)
    print(f"\n=== {relpath} ({term}) ===")
    with open(p, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    for idx, line in enumerate(lines):
        if term in line:
            start = max(0, idx - 10)
            end = min(len(lines), idx + 12)
            print("".join(lines[start:end]))
