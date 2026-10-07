# 1. Update USA_MKUltra_scripted_localisation.txt
sloc_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_localisation\USA_MKUltra_scripted_localisation.txt'
with open(sloc_path, 'r', encoding='utf-8') as f:
    stext = f.read().replace('\r\n', '\n')

old_charter = """defined_text = {
	name = GetUSA_MKUltraCharterStatus
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 2 } }
		localization_key = USA_mkultra_charter_status_closed
	}
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 1 } }
		localization_key = USA_mkultra_charter_status_restricted
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_charter_status_preparatory
	}
}"""

new_charter = """defined_text = {
	name = GetUSA_MKUltraCharterStatus
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 2 } }
		localization_key = USA_mkultra_charter_status_closed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_charter_state = 1 }
			check_variable = { USA_mkultra_capacity = 2 }
		}
		localization_key = USA_mkultra_charter_status_expanded
	}
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 1 } }
		localization_key = USA_mkultra_charter_status_restricted
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_charter_status_preparatory
	}
}"""

assert old_charter in stext, "old_charter not found"
stext = stext.replace(old_charter, new_charter)

old_slot = """defined_text = {
	name = GetUSA_MKUltraSlotStatus
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 2 } }
		localization_key = USA_mkultra_slot_status_closed
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 2 } }
		localization_key = USA_mkultra_slot_status_report
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 1 } }
		localization_key = USA_mkultra_slot_status_research
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_slot_status_available
	}
}"""

new_slot = """defined_text = {
	name = GetUSA_MKUltraSlotStatus
	text = {
		trigger = { check_variable = { USA_mkultra_charter_state = 2 } }
		localization_key = USA_mkultra_slot_status_closed
	}
	text = {
		trigger = { check_variable = { USA_mkultra_capacity = 2 } }
		localization_key = USA_mkultra_slot_status_dual
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 2 } }
		localization_key = USA_mkultra_slot_status_report
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 1 } }
		localization_key = USA_mkultra_slot_status_research
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_slot_status_available
	}
}

defined_text = {
	name = GetUSA_MKUltraSlot1Status
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 2 } }
		localization_key = USA_mkultra_slot_status_report
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_1_state = 1 } }
		localization_key = USA_mkultra_slot_status_research
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_slot_status_available
	}
}

defined_text = {
	name = GetUSA_MKUltraSlot2Status
	text = {
		trigger = { check_variable = { USA_mkultra_slot_2_state = 2 } }
		localization_key = USA_mkultra_slot_status_report
	}
	text = {
		trigger = { check_variable = { USA_mkultra_slot_2_state = 1 } }
		localization_key = USA_mkultra_slot_status_research
	}
	text = {
		trigger = { always = yes }
		localization_key = USA_mkultra_slot_status_available
	}
}"""

assert old_slot in stext, "old_slot not found"
stext = stext.replace(old_slot, new_slot)

with open(sloc_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(stext)

print("USA_MKUltra_scripted_localisation.txt updated!")

# 2. Update USA_MKUltra_gui_scripted_localisation.txt
gui_sloc_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_localisation\USA_MKUltra_gui_scripted_localisation.txt'
with open(gui_sloc_path, 'r', encoding='utf-8') as f:
    gtext = f.read().replace('\r\n', '\n')

# Add Dossier 3 to GetUSA_MKUltraDossierCardTitle
title_target = """	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}"""
title_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_title
	}"""
assert title_target in gtext, "title_target not found"
gtext = gtext.replace(title_target, title_addition)

# Add Dossier 3 to GetUSA_MKUltraDossierCardStage
stage_target = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			check_variable = { USA_mkultra_countermeasure_stage = 6 }
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}"""
stage_addition = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			check_variable = { USA_mkultra_countermeasure_stage = 6 }
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 1 }
		}
		localization_key = USA_mkultra_gui_stage_available
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 2 }
				check_variable = { USA_mkultra_midnight_climax_stage = 4 }
				check_variable = { USA_mkultra_midnight_climax_stage = 6 }
			}
		}
		localization_key = USA_mkultra_gui_stage_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 3 }
				check_variable = { USA_mkultra_midnight_climax_stage = 5 }
				check_variable = { USA_mkultra_midnight_climax_stage = 7 }
			}
		}
		localization_key = USA_mkultra_gui_stage_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 8 }
		}
		localization_key = USA_mkultra_gui_stage_closed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}"""
assert stage_target in gtext, "stage_target not found"
gtext = gtext.replace(stage_target, stage_addition)

# Add Dossier 3 to GetUSA_MKUltraDossierCardCommitment
commit_target = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			has_country_flag = USA_mkultra_countermeasure_paid
		}
		localization_key = USA_mkultra_gui_commitment_countermeasure_paid
	}"""
commit_addition = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			has_country_flag = USA_mkultra_countermeasure_paid
		}
		localization_key = USA_mkultra_gui_commitment_countermeasure_paid
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_paid
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_full
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_replicated
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_renewed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			has_country_flag = USA_mkultra_midnight_climax_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_initial
	}"""
assert commit_target in gtext, "commit_target not found"
gtext = gtext.replace(commit_target, commit_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedFileHeading
heading_target = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}"""
heading_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_title
	}"""
assert heading_target in gtext, "heading_target not found"
gtext = gtext.replace(heading_target, heading_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedOwner
owner_target = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_owner_cia_internal
	}"""
owner_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_owner_cia_internal
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_owner_cia_midnight
	}"""
assert owner_target in gtext, "owner_target not found"
gtext = gtext.replace(owner_target, owner_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedClaim
claim_target = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_claim_countermeasure
	}"""
claim_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_claim_countermeasure
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_claim_midnight_climax
	}"""
assert claim_target in gtext, "claim_target not found"
gtext = gtext.replace(claim_target, claim_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedAppraisal
appraisal_target = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_appraisal_complete
	}"""
appraisal_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_appraisal_complete
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_appraisal
	}"""
assert appraisal_target in gtext, "appraisal_target not found"
gtext = gtext.replace(appraisal_target, appraisal_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedHarm
harm_target = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_harm_countermeasure
	}"""
harm_addition = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 2 } }
		localization_key = USA_mkultra_gui_harm_countermeasure
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
		}
		localization_key = USA_mkultra_gui_harm_midnight_renewed
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_harm_midnight_initial
	}"""
assert harm_target in gtext, "harm_target not found"
gtext = gtext.replace(harm_target, harm_addition)

# Add Dossier 3 to GetUSA_MKUltraSelectedAwards
awards_target = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_countermeasure
	}"""
awards_addition = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_countermeasure
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_record_awarded
			has_country_flag = USA_mkultra_midnight_climax_renewal_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_full
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_replicated
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_renewal_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_renewed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_initial
	}"""
assert awards_target in gtext, "awards_target not found"
gtext = gtext.replace(awards_target, awards_addition)

with open(gui_sloc_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(gtext)

print("USA_MKUltra_gui_scripted_localisation.txt updated!")
