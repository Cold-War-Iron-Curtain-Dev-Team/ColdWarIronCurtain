# Slot membership for the USSR spirit consolidation (non-Brezhnev trees).
POL = """
SOV_Delayed_Presidium_Countermeasures SOV_Pledged_Allegiance_to_the_Presidium SOV_Cautious_Destalinization
SOV_Malenkov_Allies SOV_Party_Privileges_Cut SOV_Condemnetion_of_Bureaucratism_and_Corruption
SOV_Khrushchev_Exclusion_From_Presidium SOV_Khrushchevites_in_Presidium SOV_Malenkov_Resignation
SOV_Khrushchev_Politiburo SOV_Anti_Party_Group_Coup
SOV_Measures_Against_Khrushchevites SOV_Khrushchevites_Purge SOV_Stabiilised_Politiburo
Fragile_Kaganovich_Rule Kaganovichism_successful Kaganovichism_cemented
SOV_New_Soviet_Man SOV_Decriminialized_Homosexuality SOV_Soviet_Cultural_Renaissance
SOV_Discipline_strengthening_initiative SOV_Campaign_on_Strengthening_Labour_Discipline
SOV_Campaign_on_Strengthening_Labour_Discipline_Improved SOV_Campaign_on_Strengthening_Labour_Discipline_Improved_again
""".split()
SEC = """
SOV_MGB SOV_MGBMVD SOV_Merkulov_in_Power SOV_Meshik_Allied SOV_Dekanozov_Allied SOV_MVD_IN_CONTROL
SOV_Beria_State_of_Emergency SOV_MGB_ongoing_Purge SOV_KGB SOV_KGB_Improved SOV_MGB_Army_Joint_IAC
SOV_Preparation_for_an_anti_corruption_campaign SOV_Anti_corruption_campaign_in_MVD SOV_Wide_anti_corruption_campaign
SOV_ANTI_MISINFORMATION SOV_ANTI_MISINFORMATION_1
""".split()
MIL = """
victor_of_the_great_patriotic_war Politicized_Army_1 Politicized_Army_2 Politicized_Army_3
experienced_nonc_combating_officers_ranks SOV_experienced_army SOV_experienced_army_2 SOV_experienced_army_3
SOV_experienced_army_4 SOV_experienced_army_5 great_liberation_war great_liberation_war_2 great_liberation_war_3 the_last_war
""".split()
# Folded into the "State of the Union" dynamic modifier.
FOLD = """
gossnab antiquated_infrastructure Suchyi_voyny SOV_Abortion_Criminalized
soviet_economic_boost idea_SOV_Pavlovian_Session SOV_State_Atheism SOV_Cancelled_Stalin_Projects SOV_Beria_National_Reforms
five_year_plan nuclear_powered_icebreakers Currency_Devaluation soviet_free_specialized_education invested_in_housing Ukrainian_Academy_of_sciences
soviet_planned_komsomol_reform soviet_planned_komsomol_reform_1 soviet_planned_komsomol_reform_2 soviet_planned_komsomol_reform_3
soviet_planned_komsomol_reform_4 soviet_planned_komsomol_reform_5 reformed_komsomol
soviet_expanded_consumer_goods soviet_expanded_consumer_goods_2 soviet_expanded_consumer_goods_3 soviet_expanded_consumer_goods_4 soviet_expanded_consumer_goods_5
better_consumer_goods_management better_consumer_goods_management_1 reformed_kolkhozes enlarged_collective_farms
Experimental_mobile_concrete_plants standardised_concrete_standards large_scale_mobile_concrete_plants overhauled_maintenance
self_management_doctrine self_management_doctrine_2 self_management_doctrine_3 self_management_doctrine_4 self_management_doctrine_5
investment_in_cybernetics investment_in_cybernetics_2 investment_in_cybernetics_3 studying_western_computers best_of_both_world_hardware
new_algorithms new_algorithms_2 upgraded_networking_algorithms EGSVT_Network_early soviet_refocused_planning
soviet_expanded_elementary_and_medium_schools soviet_expanded_numbers_of_students_1 soviet_expanded_numbers_of_students_2
soviet_expanded_numbers_of_students_3 Improved_police_training more_nuclear_production Improved_Ground_Based_Air_Defence_Network
Recently_Created_Water_Commissions redirected_engineers Soviet_Greatworks recently_reshuffled_foreign_ministry
SOV_Revamped_Political_Bureau SOV_Khrushchevite_Affair SOV_Chairman_Molotov SOV_Dep_Chairman_Kaganovich SOV_Stalinist_Cult
sov_revisionism_defeated sov_dekhrushchevization sov_stalinist_agriculture sov_stalinist_agriculture_inov_good sov_stalinist_agriculture_inov_fail
SOV_studying_western_academics SOV_Stalin_Institute SOV_Kaganovich_Institute SOV_Anti_alcohol_Campaign SOV_Studying_American_Prohibition_Era
SOV_Expanded_Anti_Alcohol_Campaigns SOV_Partial_Prohibition SOV_Updated_Curricula SOV_Cybernetic_Future SOV_Cybernetic_Constitution
SOV_Computerized_Logistics_Monitoring_idea SOV_computerized_crop_management EGSVT_Network_expanded EGSVT_Network_Akademset EGSVT_Network_Military
SOV_SOFE_Theory SOV_Early_Automation_of_the_Heavy_Industry SOV_Early_Automation_of_the_Civilian_Economy
SOV_Real_Time_Troops_Monitoring SOV_Experimental_Cybernetics_in_the_Red_Army
era_of_stagnation growing_alcoholism andropov_diplomacy SOV_Economic_Department_of_the_Central_Committee_of_the_CPSU
SOV_Special_Commission_for_the_Direction_of_the_Economic_Experiment SOV_Special_Commission_for_the_Direction_of_the_Economic_Experiment_Improved
SOV_Gorbachev_led_reforms_team SOV_Gorbachev_led_reforms_team_Decree SOV_Gorbachev_led_reforms_team_Private SOV_Gorbachev_led_reforms_team_Private_Decree
SOV_Romanov_led_reforms_team SOV_Romanov_led_reforms_team_Decree SOV_Romanov_led_reforms_team_Market SOV_Romanov_led_reforms_team_Decree_Market
SOV_law_on_labour_collectives SOV_Amendments_to_the_law_on_labour_collectives
SOV_Mass_reshuffles_and_dismissals_in_the_party_and_administrative_apparatus SOV_Ongoing_mass_dismissals_in_the_Ministry_of_Internal_Affairs
Union_of_Laborer Joint_Planning_Commission Joint_Planning_Commission_Empowered
SOV_goal_eastern_europe_secured SOV_goal_avoid_direct_conflict SOV_goal_eastern_communism SOV_goal_western_europe_divided SOV_goal_communist_unity
""".split()
# Equipment-cost spirits replaced by research bonuses: idea -> (category, name)
TECH = {
    'Increase_T54_Production': 'armor',
    'AK_47_Mass_Adoption': 'infantry_weapons',
    'MiG_15_Mass_Adoption': 'jet_technology',
    'Submarine_Expansion': 'submarine_tech',
}
IN_SCOPE = """
history/countries/SOV - Soviet union.txt
common/national_focus/SOV_Stalin.txt
common/national_focus/SOV_50s_Military.txt
common/national_focus/SOV_50s_Industry.txt
common/national_focus/SOV_Troika.txt
common/national_focus/SOV_Stalin_Lives.txt
common/national_focus/SOV_Khruschev.txt
common/national_focus/SOV_Kaganovich.txt
common/national_focus/SOV_Beria_Malenkov.txt
common/national_focus/SOV_Bulganin.txt
common/national_focus/SOV_Ustinov.txt
common/national_focus/SOV_Andropov.txt
common/national_focus/SOV_WW3_1950s.txt
events/SovietUnion_Historical_Events.txt
events/SOV_Kaganovich_Events.txt
events/SOV_Bulganin_events.txt
events/SOV_Ustinov_events.txt
events/SOV_Andropov_Events.txt
events/_SOV_WW3.txt
common/decisions/SOV.txt
common/scripted_effects/IC_scripted_effects.txt
""".strip().split('\n')
ALL = set(POL) | set(SEC) | set(MIL) | set(FOLD) | set(TECH)
assert len(ALL) == len(POL) + len(SEC) + len(MIL) + len(FOLD) + len(TECH), 'overlap between slots'

# Shared files: only these names may be rewritten there.
ONLY = {
    'common/scripted_effects/IC_scripted_effects.txt': {'SOV_Ongoing_mass_dismissals_in_the_Ministry_of_Internal_Affairs', 'SOV_Mass_reshuffles_and_dismissals_in_the_party_and_administrative_apparatus'},
}

# Folded tier chains: each entry is a list of ranks, a rank is a list of alternatives.
# Adding a tier removes every other tier of its chain, and is skipped if a higher tier is active.
CHAINS = [
    [['soviet_planned_komsomol_reform'], ['soviet_planned_komsomol_reform_1'], ['soviet_planned_komsomol_reform_2'],
     ['soviet_planned_komsomol_reform_3'], ['soviet_planned_komsomol_reform_4'], ['soviet_planned_komsomol_reform_5'], ['reformed_komsomol']],
    [['soviet_expanded_consumer_goods'], ['soviet_expanded_consumer_goods_2'], ['soviet_expanded_consumer_goods_3'],
     ['soviet_expanded_consumer_goods_4'], ['soviet_expanded_consumer_goods_5']],
    [['self_management_doctrine'], ['self_management_doctrine_2'], ['self_management_doctrine_3'], ['self_management_doctrine_4'], ['self_management_doctrine_5']],
    [['investment_in_cybernetics'], ['investment_in_cybernetics_2'], ['investment_in_cybernetics_3']],
    [['better_consumer_goods_management'], ['better_consumer_goods_management_1']],
    [['studying_western_computers'], ['best_of_both_world_hardware']],
    [['new_algorithms'], ['new_algorithms_2']],
    [['EGSVT_Network_early'], ['EGSVT_Network_expanded'], ['EGSVT_Network_Akademset', 'EGSVT_Network_Military']],
    [['SOV_Computerized_Logistics_Monitoring_idea'], ['SOV_SOFE_Theory'], ['SOV_Early_Automation_of_the_Heavy_Industry', 'SOV_Early_Automation_of_the_Civilian_Economy']],
    [['SOV_Anti_alcohol_Campaign'], ['SOV_Studying_American_Prohibition_Era'], ['SOV_Expanded_Anti_Alcohol_Campaigns'], ['SOV_Partial_Prohibition']],
    [['SOV_Cybernetic_Future'], ['SOV_Cybernetic_Constitution']],
    [['SOV_Real_Time_Troops_Monitoring'], ['SOV_Experimental_Cybernetics_in_the_Red_Army']],
    [['Joint_Planning_Commission'], ['Joint_Planning_Commission_Empowered']],
    [['Experimental_mobile_concrete_plants'], ['standardised_concrete_standards'], ['large_scale_mobile_concrete_plants']],
    [['SOV_Revamped_Political_Bureau'], ['SOV_Khrushchevite_Affair']],
    [['sov_stalinist_agriculture'], ['sov_stalinist_agriculture_inov_good', 'sov_stalinist_agriculture_inov_fail']],
    [['SOV_Gorbachev_led_reforms_team'], ['SOV_Gorbachev_led_reforms_team_Decree', 'SOV_Gorbachev_led_reforms_team_Private'], ['SOV_Gorbachev_led_reforms_team_Private_Decree']],
    [['SOV_Romanov_led_reforms_team'], ['SOV_Romanov_led_reforms_team_Decree', 'SOV_Romanov_led_reforms_team_Market'], ['SOV_Romanov_led_reforms_team_Decree_Market']],
    [['SOV_law_on_labour_collectives'], ['SOV_Amendments_to_the_law_on_labour_collectives']],
    [['SOV_Special_Commission_for_the_Direction_of_the_Economic_Experiment'], ['SOV_Special_Commission_for_the_Direction_of_the_Economic_Experiment_Improved']],
]
for _c in CHAINS:
    for _r in _c:
        for _n in _r:
            assert _n in FOLD, _n
