import os
import re

mod_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"

# Load defined ideas
existing_ideas = set()
for root, dirs, files in os.walk(os.path.join(mod_dir, "common", "ideas")):
    for f in files:
        if f.endswith(".txt"):
            p = os.path.join(root, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as idf:
                text = idf.read()
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("#"): continue
                m = re.match(r"^([a-zA-Z0-9_]+)\s*=\s*\{", line)
                if m:
                    existing_ideas.add(m.group(1))

doc_ideas = [
    "Reduced_Barriers_to_American_Market", "Affirmitive_Action_Ban", "Regulatory_Reform",
    "Mass_Deportation_Campaign", "House_Committee_on_Internal_Security", "Revamped_Trade_Policy",
    "War_on_Wall_Street", "Purged_State_Department", "nuclear_weapon_buildup",
    "Made_in_America_Initiative", "Economic_Slowdown", "Humphrey_Hawkins_Enforced",
    "Japanese_Trade_Sanctions_USA", "Japanese_Trade_Sanctions_JAP", "Office_of_Economic_Planning",
    "Reduced_Nato_Committment", "Savings_and_Loan_Bailout", "Savings_and_Loan_Industry_Collapse",
    "Executive_Order_12333", "Executive_Order_12334", "Executive_Order_12334_2",
    "Nuclear_Energy_Push", "Nuclear_Energy_Freeze", "Economic_Consensus_Commission",
    "Center_Left_Fed_Reserve", "Center_Fed_Reserve", "Right_Wing_Fed_Reserve",
    "Department_of_Veterans_Affairs", "Gay_Recruitment_Allowed", "Working_Group_on_Financial_Markets",
    "attack_wasteful_military_spending", "Truce_with_Corporate_America", "Slash_Military_Spending",
    "Withdrawed_from_UN_Activity", "Bear_Spares", "Foreign_Militia_Support",
    "Economic_Security_Council", "American_Intelligence_Collaboration", "Banned_Foriegn_Car_Imports"
]

print("--- CHECKING DOCUMENTED 1980s IDEAS ---")
for idea in doc_ideas:
    status = "EXISTS" if idea in existing_ideas else "MISSING"
    print(f"{idea:40}: {status}")
