import re

with open("localisation/english/MLA_l_english.yml", "r", encoding="utf-8-sig") as f:
    text = f.read()

existing_keys = set(re.findall(r'^\s*([a-zA-Z0-9_\-]+):', text, re.MULTILINE))

loc_entries = {
    # Boestamam Focuses
    "MLA_Purge_Maoist_Hardliners_NPLA": "Purge Maoist Hardliners in the NPLA",
    "MLA_Purge_Maoist_Hardliners_NPLA_desc": "The revolutionary army must reflect the national will rather than foreign Maoist dogma. We must purge unyielding dogmatists from our command structure to secure a united socialist front.",
    "MLA_Malayanize_Ex_Communists": "Malayanize Former Communists",
    "MLA_Malayanize_Ex_Communists_desc": "Our struggle cannot remain an isolated ethnic movement. We must reorient our cadres toward Malayan nationhood, integrating former communist partisans into a broader popular socialist movement.",
    "MLA_Embrace_Indo-Melayu_Raya_Ideas": "Embrace the Melayu Raya Ideals",
    "MLA_Embrace_Indo-Melayu_Raya_Ideas_desc": "The artificial borders drawn by British and Dutch colonialists divide brothers of the archipelago. We look across the Malacca Strait to Indonesia and champion the sacred vision of Greater Indonesia: Indonesia Raya.",
    "MLA_Emulate_Sukarno_Regime": "Emulate the Sukarno Model",
    "MLA_Emulate_Sukarno_Regime_desc": "President Sukarno's fiery anti-imperialism and blend of nationalism, religion, and socialism provide the blueprint for our revolutionary governance. We shall align our institutions with Jakarta.",
    "MLA_Enforce_Pansicalla_Ideals": "Enforce Pancasila Principles",
    "MLA_Enforce_Pansicalla_Ideals_desc": "To harmonize our diverse society without descending into ethnic strife, we adopt the five philosophical pillars of Pancasila: belief in one God, just humanity, unity, consensus democracy, and social justice.",
    "MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades": "Promote Former KMM Comrades",
    "MLA_Promote_Ex_Kesatuan_Melayu_Muda_Comrades_desc": "Veterans of the Kesatuan Melayu Muda—fighters like Ibrahim Yaacob, Mustapha Hussain, and Mokhtaruddin Lasso—have long championed our independence. We welcome them into senior military command.",
    "MLA_Adopt_Marhaenism": "Adopt Marhaenism",
    "MLA_Adopt_Marhaenism_desc": "Marhaenism, born of the struggles of the impoverished peasants and proletarians, places the common farmer and rubber tapper at the heart of our socio-economic revolution.",
    "MLA_Paving_The_Way_for_Greater_Indo-Malay": "Pave the Way for Greater Indo-Malay Unity",
    "MLA_Paving_The_Way_for_Greater_Indo-Malay_desc": "With ideological unity forged and colonial legacies cast off, we prepare the diplomatic and political path toward total integration with our Indonesian brethren.",

    # Syndicalist Focuses
    "MLA_Syndies_Takeover": "Trade Unionists Seize Control",
    "MLA_Syndies_Takeover_desc": "The organized working class will no longer take orders from clandestine forest politburos. Led by the Malayan Trade Union Council, the workers have claimed leadership of the revolutionary state.",
    "MLA_Collaborating_Shamsiah_Fakeh": "Cooperate with Shamsiah Fakeh",
    "MLA_Collaborating_Shamsiah_Fakeh_desc": "Shamsiah Fakeh and the Angkatan Wanita Sedar (AWAS) bring vital progressive and feminist leadership to our cause. Together with union leaders, we form a truly broad left coalition.",
    "MLA_Diversify_NPLA": "Diversify the People's Liberation Army",
    "MLA_Diversify_NPLA_desc": "To transform the NPLA from a guerrilla force into a genuine people's militia, we recruit leaders across ethnic lines—including trade union organizers and veterans like John Thivy and Rasammah Bhupalan.",
    "MLA_Ditching_Sinophilic_Views": "Discard Sinocentric Dogma",
    "MLA_Ditching_Sinophilic_Views_desc": "Our revolution belongs to the workers of Malaya, not to Beijing. By repudiating rigid pro-China rhetoric, we build a multi-ethnic revolutionary movement that represents Malays, Chinese, and Indians alike.",
    "MLA_Formation_Syndicalist_System": "Establish the Syndicalist Republic",
    "MLA_Formation_Syndicalist_System_desc": "We proclaim the reorganization of the state into industrial syndicates and democratic workers' councils under the All-Malayan Confederation of Labour Party (AMCLP).",
    "MLA_Enforce_Syndicalization": "Enforce Industrial Syndicalization",
    "MLA_Enforce_Syndicalization_desc": "Factories, plantations, and docks are placed directly into the hands of worker committees. Syndicates now coordinate production, ending both colonial exploitation and state bureaucracy.",
    "MLA_Purge_Chin_Goons": "Expel Hardline Partisans",
    "MLA_Purge_Chin_Goons_desc": "Remnants of Chin Peng's personal faction who resist democratic trade union governance must be removed from command before they subvert the worker councils.",
    "MLA_Syndicalism_More_Marxism": "Syndicalism: Beyond Orthodox Dogma",
    "MLA_Syndicalism_More_Marxism_desc": "Rather than slavishly following Moscow or Beijing, our syndicalist democracy adapts Marxist theory to the unique colonial and trade union conditions of Southeast Asia.",
    "MLA_New_Managament": "Under New Management",
    "MLA_New_Managament_desc": "The transitional period is over. Malaya is now a worker-governed syndicalist democracy, free from colonial chains, imperialist puppets, and guerrilla terror alike.",

    # KMT Descs
    "MLA_Demaoistization_of_NPLA_desc": "With the Nationalists triumphant across the sea, dogmatic Maoist insurgency tactics are obsolete. We reorganize the Liberation Army under modern, disciplined principles inspired by the National Revolutionary Army.",
    "MLA_Marx-Sun_Yat-Sen-Chin_Peng_desc": "Drawing together the egalitarian spirit of Marx and the Three Principles of the People of Dr. Sun Yat-sen, Chin Peng synthesizes a distinct ideology: revolutionary Tridemism adapted for Malaya.",
    "MLA_Mimicking_KMT_Policies_desc": "We implement state-led industrialization, controlled land reform, and civic education programs mirroring the national reconstruction blueprints established in China.",
    "MLA_Infuse_Tridemism_with_Socialism_desc": "Nationalism, Democracy, and the Livelihood of the People are infused with socialist economics to create a progressive, welfare-oriented developmental republic.",
    "MLA_Enfore_New_Direction_NLA_desc": "The army adopts modern military policing and logistical discipline to maintain civic order across the peninsula.",
    "MLA_Rebrand_Party_Vision_and_Future_desc": "We formally rebrand the party into the Parti Rakyat Malaya - Tridemist (PRM), presenting a modernized democratic face to the Malayan populace.",
    "MLA_Tridemism_is_Chinese_Socialism_desc": "Tridemism provides a unique synthesis that reconciles Chinese diaspora cultural heritage with Malayan civic socialism, welcoming refugees and building a modern society.",
    "MLA_White_Sun_Over_Malaya_desc": "Under the banner of the White Sun and the socialist republic, Malaya enters a new era of stability, constitutional democracy, and shared prosperity.",

    # Ideas
    "MLA_Radical_China_Attack": "Radicalized Cadre Offensive",
    "MLA_Radical_China_Attack_desc": "Fervent ideological mobilization has pushed our cadres to launch bold, aggressive assaults against British colonial positions.",
    "MLA_Malayan_Boat_People": "Malayan Diaspora Resettlement",
    "MLA_Malayan_Boat_People_desc": "Thousands of diaspora refugees and families have arrived and integrated into Malayan cooperatives, expanding our technical and skilled labor pool.",

    # Political Minigame UI & Tooltips
    "MLA_Political_Minigame": "Central Committee Factional Struggle",
    "MLA_Political_Minigame_desc": "Manage the balance of influence between the party's dominant faction and internal rivals. Shifts in domestic influence and external factional backing determine the leadership and future ideological course of the Malayan revolution.",
    "MLA_Main_Influence_Effect_tt": "§YDominant Faction Influence§! changes by §G[?MLA_Main_Influence_temp|+=%]§!.",
    "MLA_Alt_Influence_Effect_tt": "§YAlternative Faction Influence§! changes by §G[?MLA_Alt_Influence_temp|+=%]§!.",
    "add_mla_dom_influence_tt": "§GIncreases Dominant Faction Influence.§!",
    "minus_mla_dom_influence_tt": "§RDecreases Dominant Faction Influence.§!",
    "add_mla_main_support_tt": "§GIncreases Popular Support for Dominant Faction.§!",
    "minus_mla_main_support_tt": "§RDecreases Popular Support for Dominant Faction.§!",
    "add_mla_alt_support_tt": "§GIncreases Popular Support for Opposition Faction.§!",
    "minus_mla_alt_support_tt": "§RDecreases Popular Support for Opposition Faction.§!",
    "MLA_MAIN_MINIGAME_TT": "Dominant Faction Influence: §Y[?MLA_Main_Support|0]%§!",
    "MLA_ALT_MINIGAME_TT": "Opposition Faction Influence: §Y[?MLA_Alt_Support|0]%§!",
    "MLA_CHIN_PENG_MINIGAME_TT": "§HChin Peng§!\nLeader of the Marxist-Leninist Party Hardliners.",
    "MLA_SHAMSIAH_FAKEH_MINIGAME_TT": "§HShamsiah Fakeh§!\nLeader of the Malay Revolutionary Left (AWAS).",
    "MLA_BOESTAMAM_MINIGAME_TT": "§HAhmad Boestamam§!\nChampion of Left-Nationalism and Melayu Raya.",
    "MLA_NARAYANAN_MINIGAME_TT": "§HP.P. Narayanan§!\nLeader of the Trade Union Councils and Democratic Syndicalists.",
    "MLA_NO_OPPOSITION_MINIGAME_TT": "No organized factional rival currently challenges the central leadership.",
    "MLA_MINIGAME_DOMESTIC_INDEPENDENCE_TT": "Domestic Independence: §Y[?MLA_Influence|0]%§!",
    "MLA_MINIGAME_EXTERNAL_INFLUENCE_TT": "Foreign Dependence: §Y[?MLA_Dom_Influence|0]%§!",
    "MLA_MINIGAME_FACTIONAL_INFIGHTING_TT": "Factional Infighting Level",
    "MLA_MINIGAME_POPULAR_SUPPORT_TT": "Popular Grassroots Support",
    "MLA_Syndies_Last_Focus_tt": "§GThe Syndicalist political and economic transition has been successfully consolidated.§!",

    # Cosmetic Tags & Decisions
    "MLA_Syndicalist": "Socialist Republic of Malaya",
    "MLA_Syndicalist_DEF": "The Socialist Republic of Malaya",
    "MLA_KMT": "Republic of Malaya",
    "MLA_KMT_DEF": "The Republic of Malaya",
    "ask_INO_annex_MLA": "Petition Indonesia for Unification",
    "ask_INO_annex_MLA_desc": "Formalize our historic and fraternal bonds by petitioning the Republic of Indonesia to incorporate Malaya into the greater federation of Melayu Raya."
}

to_add = {}
for k, v in loc_entries.items():
    if k not in existing_keys:
        to_add[k] = v

print(f"Total entries to add: {len(to_add)}")
for k, v in to_add.items():
    print(f"  {k}: \"{v[:50]}...\"")

# Generate new content
new_lines = []
for k, v in to_add.items():
    # HOI4 loc format: Key:0 "Text" or Key: "Text"
    new_lines.append(f' {k}:0 "{v}"')

new_section = "\n\n # --- Reworked MLA Political Factions & Alternative Paths Loc ---\n" + "\n".join(new_lines) + "\n"

full_text = text.rstrip() + new_section

# Write with UTF-8 BOM
with open("scratch/preview_MLA_loc.yml", "w", encoding="utf-8-sig") as f:
    f.write(full_text)

print("Saved scratch/preview_MLA_loc.yml")
