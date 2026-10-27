import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

candidates_1980 = [
    ("Reagan", "Ronald Reagan", "USA_Reagan_1980"),
    ("Bush Sr", "George H. W. Bush", "USA_Bush_1980"),
    ("Ford", "Gerald Ford", "USA_Ford1980_Second_Term"),
    ("Connally", "John Connally", "USA_Connally_1980"),
    ("Baker", "Howard Baker", "USA_Baker_1980_First_Term"),
    ("Dole", "Bob Dole", "USA_Dole_1980"),
    ("Anderson", "John Anderson", "USA_Anderson_1980"),
    ("Anderson GOP", "John Anderson", "USA_Anderson_GOP_1980"),
    ("Agnew", "Spiro Agnew", "USA_Agnew_1980"),
    ("Landgrebe", "Earl Landgrebe", "USA_Landgrebe_1980_First_Term"),
    ("Rockefeller", "Nelson Rockefeller", "USA_Rockefeller_1980"),
    ("Carter", "Jimmy Carter", "USA_Carter_1980"),
    ("Brown", "Jerry Brown", "USA_Brown_1980_First_Term"),
    ("Mondale", "Walter Mondale", "USA_Mondale_1980_First_Term"),
    ("Ted Kennedy", "Edward Kennedy", "USA_Kennedy_1980_First_Term"),
    ("Muskie", "Edmund Muskie", "USA_Muskie_1980_First_Term"),
    ("Shriver", "Sargent Shriver", "USA_Shriver_1980_First_Term"),
    ("Wallace", "George Wallace", "USA_Wallace_1980")
]

print("--- CHECKING 1980 CANDIDATE TREES & PORTRAITS ---")
for code, name, tree in candidates_1980:
    tree_path = None
    for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "national_focus", "USA 1980s")):
        for f in files:
            if f.replace(".txt", "").lower() == tree.lower():
                tree_path = os.path.relpath(os.path.join(root, f), mod_dir)
                break
    print(f"{code:15}: Tree={tree_path is not None} ({tree_path})")
