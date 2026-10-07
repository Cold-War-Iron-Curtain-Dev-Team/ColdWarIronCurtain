# Update USA_MKUltra_gui_effects.txt
gui_effects_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_effects\USA_MKUltra_gui_effects.txt'
with open(gui_effects_path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

old_dossier_setup = """		clear_array = USA_mkultra_dossier_index_array
		add_to_array = { USA_mkultra_dossier_index_array = 1 }
		if = {
			limit = {
				OR = {
					has_country_flag = USA_mkultra_countermeasure_introduced
					check_variable = { USA_mkultra_countermeasure_stage > 0 }
				}
			}
			add_to_array = { USA_mkultra_dossier_index_array = 2 }
		}"""

new_dossier_setup = """		clear_array = USA_mkultra_dossier_index_array
		add_to_array = { USA_mkultra_dossier_index_array = 1 }
		if = {
			limit = {
				OR = {
					has_country_flag = USA_mkultra_countermeasure_introduced
					check_variable = { USA_mkultra_countermeasure_stage > 0 }
				}
			}
			add_to_array = { USA_mkultra_dossier_index_array = 2 }
		}
		if = {
			limit = {
				OR = {
					has_country_flag = USA_mkultra_midnight_climax_unlocked
					check_variable = { USA_mkultra_midnight_climax_stage > 0 }
				}
			}
			add_to_array = { USA_mkultra_dossier_index_array = 3 }
		}"""

assert old_dossier_setup in text, "old_dossier_setup not found"
text = text.replace(old_dossier_setup, new_dossier_setup)

# Update clamp max from 2 to 3
text = text.replace("max = 2", "max = 3")

# Update discrete check
old_disc = """						check_variable = { USA_mkultra_selected_record = 0 }
						check_variable = { USA_mkultra_selected_record = 1 }
						check_variable = { USA_mkultra_selected_record = 2 }"""

new_disc = """						check_variable = { USA_mkultra_selected_record = 0 }
						check_variable = { USA_mkultra_selected_record = 1 }
						check_variable = { USA_mkultra_selected_record = 2 }
						check_variable = { USA_mkultra_selected_record = 3 }"""

assert old_disc in text, "old_disc not found"
text = text.replace(old_disc, new_disc)

# Add check for selected_record = 3 validity
old_cm_check = """		if = {
			limit = {
				check_variable = { USA_mkultra_selected_record = 2 }
				NOT = { has_country_flag = USA_mkultra_countermeasure_introduced }
				NOT = { check_variable = { USA_mkultra_countermeasure_stage > 0 } }
			}
			set_variable = { USA_mkultra_selected_record = 0 }
			set_variable = { USA_mkultra_record_file_open = 0 }
		}"""

new_cm_check = """		if = {
			limit = {
				check_variable = { USA_mkultra_selected_record = 2 }
				NOT = { has_country_flag = USA_mkultra_countermeasure_introduced }
				NOT = { check_variable = { USA_mkultra_countermeasure_stage > 0 } }
			}
			set_variable = { USA_mkultra_selected_record = 0 }
			set_variable = { USA_mkultra_record_file_open = 0 }
		}
		if = {
			limit = {
				check_variable = { USA_mkultra_selected_record = 3 }
				NOT = { has_country_flag = USA_mkultra_midnight_climax_unlocked }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage > 0 } }
			}
			set_variable = { USA_mkultra_selected_record = 0 }
			set_variable = { USA_mkultra_record_file_open = 0 }
		}"""

assert old_cm_check in text, "old_cm_check not found"
text = text.replace(old_cm_check, new_cm_check)

with open(gui_effects_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_gui_effects.txt updated!")

# Update USA_MKUltra_gui.txt
gui_txt_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_guis\USA_MKUltra_gui.txt'
with open(gui_txt_path, 'r', encoding='utf-8') as f:
    gtext = f.read().replace('\r\n', '\n')

old_gui_vis = """			OR = {
				check_variable = { USA_mkultra_selected_record = 1 }
				AND = {
					check_variable = { USA_mkultra_selected_record = 2 }
					OR = {
						has_country_flag = USA_mkultra_countermeasure_introduced
						check_variable = { USA_mkultra_countermeasure_stage > 0 }
					}
				}
			}"""

new_gui_vis = """			OR = {
				check_variable = { USA_mkultra_selected_record = 1 }
				AND = {
					check_variable = { USA_mkultra_selected_record = 2 }
					OR = {
						has_country_flag = USA_mkultra_countermeasure_introduced
						check_variable = { USA_mkultra_countermeasure_stage > 0 }
					}
				}
				AND = {
					check_variable = { USA_mkultra_selected_record = 3 }
					OR = {
						has_country_flag = USA_mkultra_midnight_climax_unlocked
						check_variable = { USA_mkultra_midnight_climax_stage > 0 }
					}
				}
			}"""

assert old_gui_vis in gtext, "old_gui_vis not found"
gtext = gtext.replace(old_gui_vis, new_gui_vis)

with open(gui_txt_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(gtext)

print("USA_MKUltra_gui.txt updated!")

# Update USA_MKUltra_GUI.gui
gui_layout_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\interface\USA_MKUltra_GUI.gui'
with open(gui_layout_path, 'r', encoding='utf-8') as f:
    ltext = f.read().replace('\r\n', '\n')

ltext = ltext.replace("size = { width = 500 height = 505 }", "size = { width = 500 height = 595 }")
ltext = ltext.replace("size = { width = 476 height = 174 }", "size = { width = 476 height = 265 }")

with open(gui_layout_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(ltext)

print("USA_MKUltra_GUI.gui updated!")
