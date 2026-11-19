"""Build 150x57 national spirit / dynamic modifier icons in the style of the VIE/VIN art.

Each icon is a crop of an event picture already in the mod, kept in the photo's
original colours (monochrome photos stay grayscale), with alternating scanline rows
and a dark vignette on every edge, like the existing gfx/interface/ideas/vie and vin
icons. Output is DXT1 DDS.

    python _tools/assets/idea_icons.py              # write the DDS files
    python _tools/assets/idea_icons.py --preview out.png
"""
import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageOps

MOD = Path(__file__).resolve().parents[2] / "Cold War Iron Curtain"
# Recoloured or newly sourced pictures, already cropped to the photo: idea_icon_sources/<icon>.png
SOURCES = Path(__file__).resolve().parent / "idea_icon_sources"
W, H = 150, 57
EDGE = 7

# output (relative to the mod) -> (source, vertical crop anchor or None for auto).
# A source is an event picture relative to the mod, or a bare filename in SOURCES.
ICONS = {
    'gfx/interface/ideas/fre/FRE_Campaign_Overextension.dds':
        ('gfx/event_pictures/Indochina_Border_War_2.png', None),
    'gfx/interface/ideas/fre/FRE_Chanson_Pacification_Program.dds':
        ('gfx/event_pictures/Indochina_Border_War_38.png', None),
    'gfx/interface/ideas/fre/FRE_Command_Carpentier.dds':
        ('gfx/event_pictures/VIE/French_Hinh.3.png', None),
    'gfx/interface/ideas/fre/FRE_Command_De_Lattre.dds':
        ('gfx/event_pictures/Delattre_death.dds', None),
    'gfx/interface/ideas/fre/FRE_Command_Navarre.dds':
        ('gfx/event_pictures/VIE/VIE_Huu.7.png', 0.02),
    'gfx/interface/ideas/fre/FRE_Command_Salan.dds':
        ('gfx/event_pictures/Indochina_Border_War_5.png', None),
    'gfx/interface/ideas/fre/FRE_ECO_CEFEO_Pay_Raise.dds':
        ('gfx/event_pictures/Indochina_Border_War_6.png', None),
    'gfx/interface/ideas/fre/FRE_ECO_Infant_Illness_Prevention.dds':
        ('gfx/event_pictures/VIE/VIE_Historical.8.png', None),
    'gfx/interface/ideas/fre/FRE_Expeditionary_Command.dds':
        ('gfx/event_pictures/VIE/Colonel_Massau.1.png', None),
    'gfx/interface/ideas/fre/FRE_Highland_Overextension.dds':
        ('FRE_Highland_Overextension.png', None),
    'gfx/interface/ideas/fre/FRE_Indochina_War_Credits.dds':
        ('FRE_Indochina_War_Credits.png', 0.0),
    'gfx/interface/ideas/fre/FRE_Limited_Operation_Light.dds':
        ('gfx/event_pictures/Indochina_Border_War_13.png', None),
    'gfx/interface/ideas/fre/FRE_Limited_Operation_Maximum.dds':
        ('gfx/event_pictures/Indochina_Border_War_30.png', None),
    'gfx/interface/ideas/fre/FRE_Limited_Operation_Standard.dds':
        ('FRE_Limited_Operation_Standard.png', None),
    'gfx/interface/ideas/fre/FRE_Lorraine_Deep_Columns.dds':
        ('gfx/event_pictures/Indochina_Border_War_7.png', None),
    'gfx/interface/ideas/fre/FRE_Lower_Laos_Reserves_Diverted.dds':
        ('gfx/event_pictures/Indochina_Border_War_3.png', None),
    'gfx/interface/ideas/fre/FRE_Metropole_Subsidies_Cut.dds':
        ('gfx/event_pictures/VIE/Geneva_Conference_Negotiations_USA_Intervention.dds', None),
    'gfx/interface/ideas/fre/FRE_Metropole_Subsidies_Full.dds':
        ('gfx/event_pictures/VIE/CuongDe.10.png', None),
    'gfx/interface/ideas/fre/FRE_Metropole_Subsidies_Reduced.dds':
        ('gfx/event_pictures/VIE/Etat_du_Vietnam.1.png', None),
    'gfx/interface/ideas/fre/FRE_Northwest_Concentrated_Defence.dds':
        ('gfx/event_pictures/Indochina_Border_War_39.png', None),
    'gfx/interface/ideas/fre/FRE_Operation_Overextension.dds':
        ('gfx/event_pictures/Indochina_Border_War_22.png', None),
    'gfx/interface/ideas/fre/FRE_Preparation_Maximum.dds':
        ('gfx/event_pictures/Indochina_Border_War_16.png', None),
    'gfx/interface/ideas/fre/FRE_Preparation_Ready.dds':
        ('gfx/event_pictures/Indochina_Border_War_8.png', None),
    'gfx/interface/ideas/fre/FRE_Preparation_Supported.dds':
        ('gfx/event_pictures/Indochina_Border_War_31.png', None),
    'gfx/interface/ideas/fre/FRE_Under_Metropole_Command.dds':
        ('gfx/event_pictures/Generic_Indochina_French.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Cao_Bac_Hold_Defense.dds':
        ('FRE_Cao_Bac_Hold_Defense.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Cao_Bac_Reinforce_Defense.dds':
        ('gfx/event_pictures/Coloniale_Route_4_VIN.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Castor_Airhead_Forming.dds':
        ('gfx/event_pictures/Indochina_Border_War_34.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_DBP_Condor_Staging.dds':
        ('gfx/event_pictures/Indochina_Border_War_23.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_DBP_Maximum_Holdout.dds':
        ('gfx/event_pictures/FRE/FRE_Dien_Bien.1.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_DBP_Standard_Holdout.dds':
        ('gfx/event_pictures/Battle_of_Dien_Bien_Phu_FRA.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_DBP_Vulture_Air_Support.dds':
        ('FRE_DBP_Vulture_Air_Support.png', 0.12),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Dak_Doa_GM100_Defense.dds':
        ('gfx/event_pictures/Indochina_Border_War_25.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Dak_Doa_Isolated_Post.dds':
        ('gfx/event_pictures/VIE/Du_So_21.1.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Dislocation.dds':
        ('gfx/event_pictures/VIE/Diem.79.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Exploitative_Economy.dds':
        ('gfx/event_pictures/DiemLR_3.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Growth.dds':
        ('gfx/event_pictures/Generic_1950s_Saigon.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Industrial_Infancy.dds':
        ('gfx/event_pictures/VIE/Central_Highland_Railway.1.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Metropolitan_Dependency.dds':
        ('gfx/event_pictures/VIE/Elysee_Accords.1.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_ECO_Piastre_Inflation_Crisis.dds':
        ('gfx/event_pictures/VIE/CuongDe.1.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Hedgehog_Base.dds':
        ('gfx/event_pictures/VIN/VIN_Dien_Bien_Phu.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Hoa_Binh_Holdout.dds':
        ('gfx/event_pictures/Hoa_Binh_Campaign_VIN.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/FRE_Hoa_Binh_Salient.dds':
        ('gfx/event_pictures/Hoa_Binh_Campaign_FRA.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/IC_dbp_camp_under_siege.dds':
        ('gfx/event_pictures/Battle_of_Dien_Bien_Phu_VIN.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/IC_indochina_contested_objective.dds':
        ('gfx/event_pictures/Generic_Indochina_Communist.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/IC_laos_raid_capital_defense.dds':
        ('gfx/event_pictures/CIA_Laos.dds', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/IC_laos_raid_overextension.dds':
        ('gfx/event_pictures/news_laos_raid_2.png', None),
    'gfx/interface/ideas/fre/dynamic_modifiers/IC_laos_raid_overextension_severe.dds':
        ('gfx/event_pictures/Vietminhlaos.dds', None),
    'gfx/interface/ideas/los/LOS_French_Airlift.dds':
        ('gfx/event_pictures/CAM/CAM_Military.4.dds', None),
    'gfx/interface/ideas/vie/VIE_Air_Academy.dds':
        ('VIE_Air_Academy.png', 0.85),
    'gfx/interface/ideas/vie/VIE_AnNinh_QuocGia.dds':
        ('gfx/event_pictures/VIE/Diem.72.png', None),
    'gfx/interface/ideas/vie/VIE_Cach_Mang_Quoc_Gia_Press.dds':
        ('gfx/event_pictures/VIE/BaoDai.12.png', None),
    'gfx/interface/ideas/vie/VIE_Can_Lao_Party.dds':
        ('VIE_Can_Lao_Party.png', 0.05),
    'gfx/interface/ideas/vie/VIE_Caretaker_Cabinet.dds':
        ('VIE_Caretaker_Cabinet.png', None),
    'gfx/interface/ideas/vie/VIE_Censor_French.dds':
        ('gfx/event_pictures/VIE/VIE_Sect_Intro.3.png', None),
    'gfx/interface/ideas/vie/VIE_Chastened_Frontier.dds':
        ('gfx/event_pictures/VIE/Etat_du_Vietnam.2.png', None),
    'gfx/interface/ideas/vie/VIE_Cochinchina_Devolution.dds':
        ('gfx/event_pictures/VIE/CCC_Unification.5.png', None),
    'gfx/interface/ideas/vie/VIE_Cochinchina_Industry_spawnrate.dds':
        ('gfx/event_pictures/VIE_Humanity_1.png', None),
    'gfx/interface/ideas/vie/VIE_Cochinchina_Residents_spawnrate.dds':
        ('gfx/event_pictures/VIE/CCC_Unification.8.png', None),
    'gfx/interface/ideas/vie/VIE_Dac_Phu_Cong_Dan_Vu.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.5.png', None),
    'gfx/interface/ideas/vie/VIE_Democratic_Centralism.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.2.png', None),
    'gfx/interface/ideas/vie/VIE_Diem_Loyalist_Officer_Corps.dds':
        ('gfx/event_pictures/VIE/Diem.1.png', None),
    'gfx/interface/ideas/vie/VIE_Diem_Pol_Commissar.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.3.png', 0.02),
    'gfx/interface/ideas/vie/VIE_Diem_Pol_Commissar2.dds':
        ('gfx/event_pictures/VIE/Diem.6.png', None),
    'gfx/interface/ideas/vie/VIE_Diem_Soldiers_Pay_Hike.dds':
        ('gfx/event_pictures/VIE/VNA.4.png', None),
    'gfx/interface/ideas/vie/VIE_Disjointed_Army.dds':
        ('gfx/event_pictures/VIE/VIE_Lien_Minh.3.png', None),
    'gfx/interface/ideas/vie/VIE_Dong_Currency.dds':
        ('gfx/event_pictures/VIE/Etat_du_Vietnam.4.png', None),
    'gfx/interface/ideas/vie/VIE_Emphasized_NamKy.dds':
        ('gfx/event_pictures/VIE/CCC_Unification.1.png', None),
    'gfx/interface/ideas/vie/VIE_Emphasized_NamKy_NLF.dds':
        ('gfx/event_pictures/VIE/French_Coup.1.png', None),
    'gfx/interface/ideas/vie/VIE_FRA_Advisors.dds':
        ('gfx/event_pictures/VIE/VIE_Leroy.1.png', None),
    'gfx/interface/ideas/vie/VIE_FRA_Hero.dds':
        ('gfx/event_pictures/VIE/CCC_Unification.2.png', None),
    'gfx/interface/ideas/vie/VIE_Field_Chaplain.dds':
        ('gfx/event_pictures/VIE/Diem.73.png', None),
    'gfx/interface/ideas/vie/VIE_Form_3_Ministries.dds':
        ('gfx/event_pictures/VIE/Diem.81.png', None),
    'gfx/interface/ideas/vie/VIE_French_Advisors.dds':
        ('gfx/event_pictures/Indochina_Border_War_11.png', None),
    'gfx/interface/ideas/vie/VIE_French_Province.dds':
        ('gfx/event_pictures/VIE/Diem.70.png', None),
    'gfx/interface/ideas/vie/VIE_Importing_IBM_Computers.dds':
        ('VIE_Importing_IBM_Computers.png', None),
    'gfx/interface/ideas/vie/VIE_Independent_Facade.dds':
        ('gfx/event_pictures/VIE/Etat_du_Vietnam.3.png', None),
    'gfx/interface/ideas/vie/VIE_Joint_Staffs.dds':
        ('gfx/event_pictures/VIE/VIE_PQC.4.png', None),
    'gfx/interface/ideas/vie/VIE_Light_Industry_Drive.dds':
        ('gfx/event_pictures/USA_VIE50s_2.dds', None),
    'gfx/interface/ideas/vie/VIE_Looming_Diem.dds':
        ('gfx/event_pictures/Diem_Exiled.dds', None),
    'gfx/interface/ideas/vie/VIE_National_Reconstruction.dds':
        ('gfx/event_pictures/VIE/DiemLR.1.png', None),
    'gfx/interface/ideas/vie/VIE_New_Currency_Adoption.dds':
        ('gfx/event_pictures/VIE/Etat_du_Vietnam.5.png', None),
    'gfx/interface/ideas/vie/VIE_Nhu_Political_Counsellor.dds':
        ('gfx/event_pictures/VIE/NgoDinh_Brothers.1.png', None),
    'gfx/interface/ideas/vie/VIE_Phong_Trao_Cach_Mang_Quoc_Gia.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.11.png', None),
    'gfx/interface/ideas/vie/VIE_Phu_Tong_Uy_Di_Cu.dds':
        ('gfx/event_pictures/Anti_Vietnam_Refferendum_1950s.dds', None),
    'gfx/interface/ideas/vie/VIE_Poor_Infrastructure.dds':
        ('gfx/event_pictures/VIE/Diem.77.png', None),
    'gfx/interface/ideas/vie/VIE_Poor_Worker_Rights.dds':
        ('gfx/event_pictures/VIE/FUL_Econ_Committee.1.png', None),
    'gfx/interface/ideas/vie/VIE_Quan_Luc_VNCH.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.6.png', None),
    'gfx/interface/ideas/vie/VIE_Quicker_Construct.dds':
        ('gfx/event_pictures/VIE/DiemLR.2.png', None),
    'gfx/interface/ideas/vie/VIE_ROC_Advisor.dds':
        ('gfx/event_pictures/VIE/VIE_Chinese_Cooperation.1.png', None),
    'gfx/interface/ideas/vie/VIE_Reconstruction_Progressing.dds':
        ('gfx/event_pictures/VIE/Diem.71.png', None),
    'gfx/interface/ideas/vie/VIE_Regional_Aggressor.dds':
        ('gfx/event_pictures/VIE_Insurgency_Options_3.dds', None),
    'gfx/interface/ideas/vie/VIE_Regional_Hegemon.dds':
        ('gfx/event_pictures/VIE_Insurgency_Options_4.dds', None),
    'gfx/interface/ideas/vie/VIE_Repress.dds':
        ('gfx/event_pictures/VIE/VIE_Sect_Intro.1.png', None),
    'gfx/interface/ideas/vie/VIE_Revolutionary_Youth_Movement_Diem.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.9.png', None),
    'gfx/interface/ideas/vie/VIE_TRP_commissariat_remittance.dds':
        ('gfx/event_pictures/VIE/CD_Nhiep.9.png', None),
    'gfx/interface/ideas/vie/VIE_Terror_Tactics.dds':
        ('gfx/event_pictures/VIE/VIE_Sect_Intro.2.png', None),
    'gfx/interface/ideas/vie/VIE_VoBi_Academies.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.7.png', None),
    'gfx/interface/ideas/vie/VIE_cach_mang_dan_toc.dds':
        ('gfx/event_pictures/VIE/VIE_Historical_2.png', None),
    'gfx/interface/ideas/vie/VIE_cold_coexistence.dds':
        ('gfx/event_pictures/VIE/Geneva_Conference_Outcome_Success.dds', None),
    'gfx/interface/ideas/vie/VIE_ethnic_conflict.dds':
        ('gfx/event_pictures/VIE/FUL_DanVuong_Model.1.png', None),
    'gfx/interface/ideas/vie/VIE_indo_associated_state.dds':
        ('gfx/event_pictures/VIE/Elysee_Accords.2.png', None),
    'gfx/interface/ideas/vie/VIE_jungle_movement.dds':
        ('gfx/event_pictures/Indochina_Border_War_20.png', None),
    'gfx/interface/ideas/vie/VIE_jungle_tactics.dds':
        ('gfx/event_pictures/Indochina_Border_War_21.png', None),
    'gfx/interface/ideas/vie/VIE_perfected_jungle_tactics.dds':
        ('gfx/event_pictures/Indochina_Border_War_36.png', None),
    'gfx/interface/ideas/vie/VIE_religoius_tensions.dds':
        ('gfx/event_pictures/VIE/VIE_Sect_Intro.4.png', None),
    'gfx/interface/ideas/vie/dynamic_modifiers/VIE_DanXa_Revolution_modifier.dds':
        ('gfx/event_pictures/VIE/VIE_Historical.4.png', None),
    'gfx/interface/ideas/vie/dynamic_modifiers/VIE_Mobilized_Civil_Action_Cadres.dds':
        ('gfx/event_pictures/VIE/Diem.76.png', None),
    'gfx/interface/ideas/vin/NLF_Chanson_Pacification_Pressure.dds':
        ('gfx/event_pictures/NLF_2.dds', None),
    'gfx/interface/ideas/vin/NLF_Northern_Supply_Line.dds':
        ('gfx/event_pictures/Indochina_Border_War_32.png', None),
    'gfx/interface/ideas/vin/NLF_wartime_reconstitution.dds':
        ('gfx/event_pictures/VIN_PCF_1.png', None),
    'gfx/interface/ideas/vin/VIN_Bamboo_Diplomacy_Idea.dds':
        ('gfx/event_pictures/sinosovietsplit_1.dds', None),
    'gfx/interface/ideas/vin/VIN_Broad_National_Front.dds':
        ('gfx/event_pictures/VIE/VIE_Historical_3.png', None),
    'gfx/interface/ideas/vin/VIN_Campaign_Mobilization.dds':
        ('gfx/event_pictures/Decolonization_VIE_1.dds', None),
    'gfx/interface/ideas/vin/VIN_Campaign_Overextension.dds':
        ('gfx/event_pictures/Indochina_Struggle_Ending_4.png', None),
    'gfx/interface/ideas/vin/VIN_Chinese_Advisory_Group.dds':
        ('gfx/event_pictures/ZhenbaoConflict_Soviet.dds', None),
    'gfx/interface/ideas/vin/VIN_Chinese_Trained_Cadres.dds':
        ('gfx/event_pictures/Indochina_Struggle_Ending_3.png', None),
    'gfx/interface/ideas/vin/VIN_Concentrated_Battalion_Doctrine.dds':
        ('gfx/event_pictures/Indochina_Border_War_35.png', None),
    'gfx/interface/ideas/vin/VIN_Congress_Commissar_Line.dds':
        ('gfx/event_pictures/VIN/VIN_Intro_1.dds', None),
    'gfx/interface/ideas/vin/VIN_Congress_Organization_Line.dds':
        ('gfx/event_pictures/VIE/NV_CuongDe_Unification.4.png', None),
    'gfx/interface/ideas/vin/VIN_Congress_Party_Line.dds':
        ('gfx/event_pictures/Binh_Cung_Leadership_9.png', None),
    'gfx/interface/ideas/vin/VIN_Congress_Peoples_General_Line.dds':
        ('gfx/event_pictures/Battle_of_the_Day_River_VIN.dds', None),
    'gfx/interface/ideas/vin/VIN_Congress_Southern_Line.dds':
        ('gfx/event_pictures/VIE/VIE_Lien_Minh.4.png', None),
    'gfx/interface/ideas/vin/VIN_Defense_Production_Directorate.dds':
        ('gfx/event_pictures/Indochina_Border_War_37.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_American_Aid.dds':
        ('gfx/event_pictures/VIE/USA_VIE_CuongDe_Installation.1.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Automotive_Industry.dds':
        ('gfx/event_pictures/BGS_Parade.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Cement_Supply.dds':
        ('gfx/event_pictures/Generic_1950s_Cambodia.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Civil_Aviation.dds':
        ('gfx/event_pictures/Indonesian_National_Revolution_49.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Cooperative_Movement.dds':
        ('gfx/event_pictures/VIN_Land_Reform2.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Dong_Currency.dds':
        ('gfx/event_pictures/VIN/VIN_Hanoi.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Electronic_Assembly.dds':
        ('gfx/event_pictures/Binh_Cung_Leadership_8.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Labour_Mobilization.dds':
        ('gfx/event_pictures/Indochina_Border_War_28.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Modernization_Ministry.dds':
        ('gfx/event_pictures/VIE/DaLat_Question.2.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_National_Bank_Credit.dds':
        ('gfx/event_pictures/VIE/CuongDe.13.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_New_Life.dds':
        ('gfx/event_pictures/VIN_Geneva_2.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Patriotic_Capital.dds':
        ('gfx/event_pictures/VIN_Geneva_1.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Reconstruction_Program.dds':
        ('gfx/event_pictures/VIN_Land_Reform_Aftermath.dds', None),
    'gfx/interface/ideas/vin/VIN_Econ_Soviet_Aid.dds':
        ('VIN_Econ_Soviet_Aid.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Textile_Output.dds':
        ('VIN_Econ_Textile_Output.png', None),
    'gfx/interface/ideas/vin/VIN_Econ_Three_Year_Plan.dds':
        ('gfx/event_pictures/VIE/MayDay_Parade.1.png', None),
    'gfx/interface/ideas/vin/VIN_Election_Campaign_Machinery.dds':
        ('gfx/event_pictures/VIE/VIE_Historical_9.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_beijing_line.dds':
        ('gfx/event_pictures/VIN/VIN_PRC.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_coexistence_breathing_space.dds':
        ('gfx/event_pictures/VIE/Geneva_Conference_Negotiations_Ceasefire.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_diplomatic_momentum.dds':
        ('gfx/event_pictures/VIE/Geneva_Conference_Invitation.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_french_channel.dds':
        ('gfx/event_pictures/Indochina_Struggle_Ending_5.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_french_wariness.dds':
        ('gfx/event_pictures/VIE/QuyChe_16.1.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_independent_line.dds':
        ('gfx/event_pictures/VIE/VIE_Northern_Question.1.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_indochina_doctrine.dds':
        ('gfx/event_pictures/Pathet_Lao.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_laos_peace.dds':
        ('gfx/event_pictures/LaosandCambodia.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_liberation_front_rear.dds':
        ('gfx/event_pictures/VIN/VIN_Secret_Army.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_moscow_line.dds':
        ('gfx/event_pictures/report_soviet_union.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_northern_vigilance.dds':
        ('gfx/event_pictures/Indochina_Border_War_4.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_own_voice.dds':
        ('gfx/event_pictures/VIE/Geneva_Conference_Outcome_Ceasefire.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_revolutionary_sanctuary.dds':
        ('gfx/event_pictures/VIN/Binh_Cung_Leadership.4.dds', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_secure_northern_border.dds':
        ('gfx/event_pictures/Indochina_Border_War_1.png', None),
    'gfx/interface/ideas/vin/VIN_FORPOL_thai_front_prep.dds':
        ('gfx/event_pictures/Indochina_Border_War_29.png', None),
    'gfx/interface/ideas/vin/VIN_General_Military_Commission.dds':
        ('gfx/event_pictures/VIN/Binh_Cung_Leadership.1.dds', None),
    'gfx/interface/ideas/vin/VIN_General_Political_Department.dds':
        ('gfx/event_pictures/Indochina_Struggle_Ending_10.png', None),
    'gfx/interface/ideas/vin/VIN_General_Staff_Directorate.dds':
        ('gfx/event_pictures/VIN/Binh_Cung_Leadership.3.dds', None),
    'gfx/interface/ideas/vin/VIN_Hundred_Flowers_Lessons.dds':
        ('gfx/event_pictures/VIE/Initial_CuongDe.9.png', None),
    'gfx/interface/ideas/vin/VIN_Independent_Course.dds':
        ('gfx/event_pictures/Indochina_Struggle_Ending_6.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Bountiful_Harvest.dds':
        ('gfx/event_pictures/VIE/CuongDe_NgoDinh.33.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Cautious_Pace.dds':
        ('gfx/event_pictures/VIE/FUL_Unification.6.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Cooperatives.dds':
        ('gfx/event_pictures/VIE/FUL_Unification.3.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Patriotic_Capitalists.dds':
        ('gfx/event_pictures/Indonesian_National_Revolution_31.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Quynh_Luu_Unrest.dds':
        ('gfx/event_pictures/Indochina_Border_War_10.png', None),
    'gfx/interface/ideas/vin/VIN_LR_Sua_Sai.dds':
        ('gfx/event_pictures/Indochina_Border_War_14.png', None),
    'gfx/interface/ideas/vin/VIN_Lien_Viet_Consolidation.dds':
        ('gfx/event_pictures/VIE/VIE_Lien_Minh.2.png', None),
    'gfx/interface/ideas/vin/VIN_Lorraine_Depots_Disrupted.dds':
        ('gfx/event_pictures/VIN/VIN_Battle.png', None),
    'gfx/interface/ideas/vin/VIN_Military_Intelligence_Bureau.dds':
        ('gfx/event_pictures/Indonesian_National_Revolution_23.png', None),
    'gfx/interface/ideas/vin/VIN_Military_Medical_Academy.dds':
        ('gfx/event_pictures/Indochina_Border_War_33.png', None),
    'gfx/interface/ideas/vin/VIN_Military_Regions_System.dds':
        ('gfx/event_pictures/Indochina_Border_War_9.png', None),
    'gfx/interface/ideas/vin/VIN_Mobilizing_The_Youth.dds':
        ('gfx/event_pictures/Indochina_Border_War_27.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Human_Face.dds':
        ('gfx/event_pictures/VIN/VIN_Tang_Tuyet_Minh_3.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Intellectual_Chill.dds':
        ('gfx/event_pictures/VIN/VIN_Tang_Tuyet_Minh_1.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Open_Debate.dds':
        ('gfx/event_pictures/VIN/VIN_Tang_Tuyet_Minh_2.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Petition_Offices.dds':
        ('gfx/event_pictures/VIE/NUN_Unification.3.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Poet_Soldiers.dds':
        ('gfx/event_pictures/VIN_soldiers.dds', None),
    'gfx/interface/ideas/vin/VIN_NV_Resolution.dds':
        ('gfx/event_pictures/VIN/VIN_Geneva_Conference_200.dds', 0.6),
    'gfx/interface/ideas/vin/VIN_NV_Second_Tho_Moi.dds':
        ('gfx/event_pictures/VIE/Initial_CuongDe.8.png', None),
    'gfx/interface/ideas/vin/VIN_NV_Uncle_Ho_Mandate.dds':
        ('gfx/event_pictures/VIN/VIN_INO.png', None),
    'gfx/interface/ideas/vin/VIN_National_Reunification_Preparation.dds':
        ('gfx/event_pictures/VIE/NV_CuongDe_Unification.8.png', None),
    'gfx/interface/ideas/vin/VIN_Open_Debate.dds':
        ('gfx/event_pictures/VIE/NH_DIEMa.8.png', None),
    'gfx/interface/ideas/vin/VIN_People_Rooted_Government.dds':
        ('gfx/event_pictures/VIE/BaoDai.10.png', None),
    'gfx/interface/ideas/vin/VIN_Peoples_War_Doctrine.dds':
        ('gfx/event_pictures/Batle_of_Vinh_Yen_VIN.dds', None),
    'gfx/interface/ideas/vin/VIN_Pluralist_Opening.dds':
        ('gfx/event_pictures/VIE/VIE_Historical.10.png', None),
    'gfx/interface/ideas/vin/VIN_Political_Commissar_System.dds':
        ('gfx/event_pictures/Batle_of_Mao_Khe_VIN.dds', None),
    'gfx/interface/ideas/vin/VIN_President_Ho_Chi_Minh.dds':
        ('gfx/event_pictures/VIE/NV_CuongDe_Unification.2.png', None),
    'gfx/interface/ideas/vin/VIN_Public_Security_Apparatus.dds':
        ('gfx/event_pictures/Binh_Cung_Leadership_5.png', None),
    'gfx/interface/ideas/vin/VIN_Resistance_War_Economy.dds':
        ('gfx/event_pictures/Indochina_Border_War_12.png', None),
    'gfx/interface/ideas/vin/VIN_STL_COMECON_Member.dds':
        ('gfx/event_pictures/CPSU_VIN_1.dds', None),
    'gfx/interface/ideas/vin/VIN_STL_Deep_Battle_Army.dds':
        ('gfx/event_pictures/VINLAO_1.dds', None),
    'gfx/interface/ideas/vin/VIN_STL_Defence_In_Depth_Army.dds':
        ('gfx/event_pictures/Batle_of_Dong_Khe_VIN.dds', None),
    'gfx/interface/ideas/vin/VIN_STL_Hong_Ve_Army.dds':
        ('gfx/event_pictures/Indochina_Border_War_26.png', None),
    'gfx/interface/ideas/vin/VIN_Southern_Struggle_Preparation.dds':
        ('gfx/event_pictures/Indochinese_Liberation_Generic.dds', None),
    'gfx/interface/ideas/vin/VIN_Soviet_Military_Mission.dds':
        ('gfx/event_pictures/SOV_VIN_20.dds', None),
    'gfx/interface/ideas/vin/VIN_Soviet_Model_Discipline.dds':
        ('gfx/event_pictures/VIN/VIN_Intro_2.dds', None),
    'gfx/interface/ideas/vin/VIN_Tang_gia_San_Xuat.dds':
        ('gfx/event_pictures/VIE/MayDay_Parade.2.png', None),
    'gfx/interface/ideas/vin/VIN_Thi_dua_San_Xuat.dds':
        ('gfx/event_pictures/VIN_Land_Reform.dds', None),
    'gfx/interface/ideas/vin/VIN_Total_Resistance.dds':
        ('gfx/event_pictures/Vietnam_IND_3.png', None),
    'gfx/interface/ideas/vin/VIN_highland_autonomy_compact.dds':
        ('gfx/event_pictures/VIE/FireWater_Kings.1.png', None),
    'gfx/interface/ideas/vin/VIN_highland_direct_rule.dds':
        ('gfx/event_pictures/VIE/FUL_Unification.5.png', None),
    'gfx/interface/ideas/vin/VIN_ongoing_industrialization.dds':
        ('gfx/event_pictures/VIN/VIN_SOV.png', None),
    'gfx/interface/ideas/vin/dynamic_modifiers/VIN_DRV_marine_corps.dds':
        ('gfx/event_pictures/Indochina_Border_War_15.png', None),
    'gfx/interface/ideas/vin/dynamic_modifiers/VIN_campaign_rear_supply_network.dds':
        ('gfx/event_pictures/Indochina_Border_War_24.png', None),
    'gfx/interface/ideas/vin/dynamic_modifiers/VIN_guerilla_network.dds':
        ('gfx/event_pictures/NLF_1.dds', None),
}


def interior(im):
    """Bounding box of the photo inside an event picture, minus its tilted frame."""
    g = np.asarray(im.convert("L")).astype(float)
    rows = np.where(g.mean(1) > 30)[0]
    cols = np.where(g.mean(0) > 30)[0]
    x0, x1, y0, y1 = cols[0], cols[-1], rows[0], rows[-1]
    w, h = x1 - x0, y1 - y0
    m = 0.09
    return int(x0 + w * m), int(y0 + h * m), int(x1 - w * m), int(y1 - h * m)


def icon(src, vy):
    if "/" in src:
        im = Image.open(MOD / src).convert("RGB")
        x0, y0, x1, y1 = interior(im)
    else:
        im = Image.open(SOURCES / src).convert("RGB")
        x0, y0, x1, y1 = 0, 0, im.width, im.height
    w, h = x1 - x0, y1 - y0
    if vy is None:
        vy = 0.18 if h > w * 0.9 else 0.4  # portraits: keep the head
    if w / h > W / H:
        nw = int(h * W / H)
        x0 += (w - nw) // 2
        w = nw
    else:
        nh = int(w * H / W)
        y0 += int((h - nh) * vy)
        h = nh
    im = ImageOps.autocontrast(im.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.LANCZOS), cutoff=1)
    a = np.asarray(im).astype(float)
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.minimum(np.minimum(xx, W - 1 - xx), np.minimum(yy, H - 1 - yy)).astype(float)
    t = np.clip(d / EDGE, 0, 1)
    shade = (0.25 + 0.75 * t * t * (3 - 2 * t)) * np.where(yy % 2 == 0, 0.9, 1.0)
    return Image.fromarray(np.clip(a * shade[..., None], 0, 255).astype("uint8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", help="write a contact sheet instead of the DDS files")
    args = ap.parse_args()
    if args.preview:
        cols = 5
        sheet = Image.new("RGB", (cols * 310, -(-len(ICONS) // cols) * 140), (50, 50, 50))
        draw = ImageDraw.Draw(sheet)
        for i, (out, (src, vy)) in enumerate(ICONS.items()):
            x, y = i % cols * 310, i // cols * 140
            sheet.paste(icon(src, vy).resize((300, 114)), (x + 5, y + 3))
            draw.text((x + 5, y + 120), Path(out).stem[:44], fill=(255, 255, 0))
        sheet.save(args.preview)
        return
    for out, (src, vy) in ICONS.items():
        path = MOD / out
        path.parent.mkdir(parents=True, exist_ok=True)
        icon(src, vy).save(path, pixel_format="DXT1")
        print(out)


if __name__ == "__main__":
    main()
