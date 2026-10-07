path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_localisation\USA_MKUltra_gui_scripted_localisation.txt'

with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

# 1. Heading
target1 = "	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_countermeasure_title }"
replace1 = target1 + "\n\ttext = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_midnight_climax_title }"
assert target1 in text, "target1 not found"
text = text.replace(target1, replace1)

# 2. Stage in SelectedStage
target2 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			check_variable = { USA_mkultra_countermeasure_stage = 3 }
		}
		localization_key = USA_mkultra_gui_selected_stage_counter_report
	}"""
addition2 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 1 }
		}
		localization_key = USA_mkultra_gui_selected_stage_available
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 2 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 3 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 4 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_renewal_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 5 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_renewal_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 6 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_replication
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 7 }
		}
		localization_key = USA_mkultra_gui_selected_stage_midnight_final_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 8 }
		}
		localization_key = USA_mkultra_gui_selected_stage_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_selected_stage_cancelled
	}"""
assert target2 in text, "target2 not found"
text = text.replace(target2, target2 + addition2)

# 3. Owner
target3 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_owner_cia
		}
		localization_key = USA_mkultra_gui_owner_cia_internal
	}"""
addition3 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_owner_cia
		}
		localization_key = USA_mkultra_gui_owner_cia_midnight
	}"""
assert target3 in text, "target3 not found"
text = text.replace(target3, target3 + addition3)

# 4. Claim
target4 = "	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_claim_countermeasure }"
replace4 = target4 + "\n\ttext = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_claim_midnight_climax }"
assert target4 in text, "target4 not found"
text = text.replace(target4, replace4)

# 5. Appraisal
target5 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_record_awarded
		}
		localization_key = USA_mkultra_gui_countermeasure_appraisal_complete
	}"""
addition5 = """
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_appraisal
	}"""
assert target5 in text, "target5 not found"
text = text.replace(target5, target5 + addition5)

# 6. Commitment
target6 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_paid
		}
		localization_key = USA_mkultra_gui_commitment_countermeasure_paid
	}"""
addition6 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_paid
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_full
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_replication_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_replicated
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_renewed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_paid
		}
		localization_key = USA_mkultra_gui_commitment_midnight_initial
	}"""
assert target6 in text, "target6 not found"
text = text.replace(target6, target6 + addition6)

# 7. Harm
target7 = "	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_harm_countermeasure }"
addition7 = """
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
assert target7 in text, "target7 not found"
text = text.replace(target7, target7 + addition7)

# 8. Awards
target8 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			has_country_flag = USA_mkultra_countermeasure_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_countermeasure
	}"""
addition8 = """
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
assert target8 in text, "target8 not found"
text = text.replace(target8, target8 + addition8)

# 9. Evidence dimension label
target9 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_dimension_counter_finding
	}"""
addition9 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 1 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_infra
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 2 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_subjects
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 3 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_chemicals
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_vouchers
	}"""
assert target9 in text, "target9 not found"
text = text.replace(target9, target9 + addition9)

# 10. Evidence dimension state
target10 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
			has_country_flag = USA_mkultra_countermeasure_archived
		}
		localization_key = USA_mkultra_gui_evidence_archived
	}"""
addition10 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 1 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_infra
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 2 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_subjects
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 3 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_chemicals
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_vouchers
	}"""
assert target10 in text, "target10 not found"
text = text.replace(target10, target10 + addition10)

# 11. Selected application
target11 = "	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_application_counter_none }"
replace11 = target11 + "\n\ttext = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_application_midnight }"
assert target11 in text, "target11 not found"
text = text.replace(target11, replace11)

# 12. Disposition stamp
target12 = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			OR = {
				check_variable = { USA_mkultra_countermeasure_stage = 6 }
				check_variable = { USA_mkultra_countermeasure_stage = 7 }
			}
		}
		localization_key = USA_mkultra_gui_stamp_cancelled
	}"""
addition12 = """
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_archived
		}
		localization_key = USA_mkultra_gui_stamp_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_stamp_cancelled
	}"""
assert target12 in text, "target12 not found"
text = text.replace(target12, target12 + addition12)

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_gui_scripted_localisation.txt fully updated!")
