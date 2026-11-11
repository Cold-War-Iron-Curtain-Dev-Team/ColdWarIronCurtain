import os, re

missing_19 = [
    'MLA_Purge_Maoist_Hardliners_NPLA',
    'MLA_Malayanize_Ex_Communists',
    'MLA_Embrace_Indo-Melayu_Raya_Ideas',
    'MLA_Emulate_Sukarno_Regime',
    'MLA_Enforce_Pansicalla_Ideals',
    'MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades',
    'MLA_Adopt_Marhaenism',
    'MLA_Paving_The_Way_for_Greater_Indo-Malay',
    'MLA_Syndies_Takeover',
    'MLA_Collaborating_Shamsiah_Fakeh',
    'MLA_Diversify_NPLA',
    'MLA_Ditching_Sinophilic_Views',
    'MLA_Formation_Syndicalist_System',
    'MLA_Enforce_Syndicalization',
    'MLA_Purge_Chin_Goons',
    'MLA_Syndicalism_More_Marxism',
    'MLA_New_Managament',
    'MLA_Radical_China_Attack',
    'MLA_Malayan_Boat_People'
]

# Check all files in localisation/ across all subdirectories
for root, dirs, files in os.walk("localisation"):
    for f in files:
        if f.endswith(".yml"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as fp:
                txt = fp.read()
                for k in missing_19:
                    if k in txt:
                        print(f"Found {k} in {p}")
