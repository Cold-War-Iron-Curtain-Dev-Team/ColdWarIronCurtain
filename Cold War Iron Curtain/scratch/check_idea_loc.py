import os

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

ideas = [
    "Center_Left_Fed_Reserve", "Center_Fed_Reserve", "Right_Wing_Fed_Reserve",
    "Reduced_Barriers_to_American_Market", "Nuclear_Energy_Freeze", "Nuclear_Energy_Push",
    "Affirmitive_Action_Ban", "Regulatory_Reform", "Revamped_Trade_Policy",
    "Purged_State_Department", "nuclear_weapon_buildup", "Made_in_America_Initiative",
    "Economic_Slowdown", "Humphrey_Hawkins_Enforced", "Japanese_Trade_Sanctions_USA",
    "Japanese_Trade_Sanctions_JAP", "Office_of_Economic_Planning", "Savings_and_Loan_Industry_Collapse",
    "Economic_Consensus_Commission", "Gay_Recruitment_Allowed", "attack_wasteful_military_spending",
    "Truce_with_Corporate_America", "Withdrawed_from_UN_Activity", "Bear_Spares",
    "Foreign_Militia_Support", "Economic_Security_Council", "American_Intelligence_Collaboration",
    "Banned_Foriegn_Car_Imports"
]

found = {}
for root, dirs, files in os.walk(os.path.join(mod_dir, "localisation", "english")):
    for f in files:
        if f.endswith(".yml"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                for idea in ideas:
                    if f"{idea}:" in content or f"{idea}_desc:" in content:
                        if idea not in found: found[idea] = []
                        found[idea].append(f)

for idea in ideas:
    print(f"{idea:40}: {found.get(idea, 'MISSING')}")
