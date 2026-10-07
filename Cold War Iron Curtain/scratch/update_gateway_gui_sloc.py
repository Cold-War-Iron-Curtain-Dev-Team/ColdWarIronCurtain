import os

path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_localisation\USA_MKUltra_gui_scripted_localisation.txt'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

# 1. Card Title
old_title = """defined_text = {
	name = GetUSA_MKUltraDossierCardTitle
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 1 } }
		localization_key = USA_mkultra_gui_missing_baseline_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_unavailable_title }
}"""

new_title = """defined_text = {
	name = GetUSA_MKUltraDossierCardTitle
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 1 } }
		localization_key = USA_mkultra_gui_missing_baseline_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 } }
		localization_key = USA_mkultra_gui_countermeasure_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_title
	}
	text = {
		trigger = { check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 } }
		localization_key = USA_mkultra_gui_gateway_assessment_title
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_unavailable_title }
}"""
assert old_title in text, "old_title not found"
text = text.replace(old_title, new_title)

# 2. Card Stage
old_stage_end = """		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			OR = {
				check_variable = { USA_mkultra_countermeasure_stage = 6 }
				check_variable = { USA_mkultra_countermeasure_stage = 7 }
			}
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_state_malformed }
}"""

new_stage_end = """		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			OR = {
				check_variable = { USA_mkultra_countermeasure_stage = 6 }
				check_variable = { USA_mkultra_countermeasure_stage = 7 }
			}
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
			check_variable = { USA_mkultra_midnight_climax_stage = 2 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 3 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 4 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_renewal_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 5 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_renewal_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 6 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_replication
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 7 }
		}
		localization_key = USA_mkultra_gui_stage_midnight_final_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 8 }
		}
		localization_key = USA_mkultra_gui_stage_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 1 }
		}
		localization_key = USA_mkultra_gui_stage_available
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 2 }
		}
		localization_key = USA_mkultra_gui_stage_gateway_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
		}
		localization_key = USA_mkultra_gui_stage_gateway_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 4 }
		}
		localization_key = USA_mkultra_gui_stage_gateway_replication
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
		}
		localization_key = USA_mkultra_gui_stage_gateway_final_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 6 }
		}
		localization_key = USA_mkultra_gui_stage_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 7 }
		}
		localization_key = USA_mkultra_gui_stage_cancelled
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_state_malformed }
}"""
assert old_stage_end in text, "old_stage_end not found"
text = text.replace(old_stage_end, new_stage_end)

# 3. Card Disposition
old_disp_end = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			check_variable = { USA_mkultra_countermeasure_stage = 7 }
		}
		localization_key = USA_mkultra_gui_disposition_foreclosed
	}"""

new_disp_end = """	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			check_variable = { USA_mkultra_countermeasure_stage = 7 }
		}
		localization_key = USA_mkultra_gui_disposition_foreclosed
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			has_country_flag = USA_mkultra_midnight_climax_archived
		}
		localization_key = USA_mkultra_gui_disposition_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_disposition_cancelled
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_archived
		}
		localization_key = USA_mkultra_gui_disposition_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 7 }
		}
		localization_key = USA_mkultra_gui_disposition_cancelled
	}"""
assert old_disp_end in text, "old_disp_end not found"
text = text.replace(old_disp_end, new_disp_end)

# 4. Card Commitment
old_com_end = """		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 2 }
			has_country_flag = USA_mkultra_countermeasure_paid
		}
		localization_key = USA_mkultra_gui_commitment_countermeasure_paid
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_commitment_none }
}"""

new_com_end = """		trigger = {
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
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_replication_paid
		}
		localization_key = USA_mkultra_gui_commitment_gateway_replicated
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_dossier_index_array^USA_mkultra_dossier_index = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_paid
		}
		localization_key = USA_mkultra_gui_commitment_gateway_initial
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_commitment_none }
}"""
assert old_com_end in text, "old_com_end not found"
text = text.replace(old_com_end, new_com_end)

# 5. File Heading
old_head = """defined_text = {
	name = GetUSA_MKUltraSelectedFileHeading
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 1 } } localization_key = USA_mkultra_gui_missing_baseline_title }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_countermeasure_title }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_midnight_climax_title }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_unavailable_title }
}"""

new_head = """defined_text = {
	name = GetUSA_MKUltraSelectedFileHeading
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 1 } } localization_key = USA_mkultra_gui_missing_baseline_title }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_countermeasure_title }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_midnight_climax_title }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 4 } } localization_key = USA_mkultra_gui_gateway_assessment_title }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_unavailable_title }
}"""
assert old_head in text, "old_head not found"
text = text.replace(old_head, new_head)

# 6. Selected Stage
old_sel_stage_end = """		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			OR = {
				check_variable = { USA_mkultra_countermeasure_stage = 6 }
				check_variable = { USA_mkultra_countermeasure_stage = 7 }
			}
		}
		localization_key = USA_mkultra_gui_selected_stage_cancelled
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_state_malformed }
}"""

new_sel_stage_end = """		trigger = {
			check_variable = { USA_mkultra_selected_record = 2 }
			OR = {
				check_variable = { USA_mkultra_countermeasure_stage = 6 }
				check_variable = { USA_mkultra_countermeasure_stage = 7 }
			}
		}
		localization_key = USA_mkultra_gui_selected_stage_cancelled
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 1 }
		}
		localization_key = USA_mkultra_gui_selected_stage_available
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 2 }
		}
		localization_key = USA_mkultra_gui_selected_stage_gateway_research
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
		}
		localization_key = USA_mkultra_gui_selected_stage_gateway_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 4 }
		}
		localization_key = USA_mkultra_gui_selected_stage_gateway_replication
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
		}
		localization_key = USA_mkultra_gui_selected_stage_gateway_final_report
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 6 }
		}
		localization_key = USA_mkultra_gui_selected_stage_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 7 }
		}
		localization_key = USA_mkultra_gui_selected_stage_cancelled
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_state_malformed }
}"""
assert old_sel_stage_end in text, "old_sel_stage_end not found"
text = text.replace(old_sel_stage_end, new_sel_stage_end)

# 7. Owner
old_owner = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_owner_cia
		}
		localization_key = USA_mkultra_gui_owner_cia_midnight
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_owner_unassigned }
}"""

new_owner = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_owner_cia
		}
		localization_key = USA_mkultra_gui_owner_cia_midnight
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 4 } }
		localization_key = USA_mkultra_gui_owner_army_inscom
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_owner_unassigned }
}"""
assert old_owner in text, "old_owner not found"
text = text.replace(old_owner, new_owner)

# 8. Claim
old_claim = """	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_claim_midnight_climax }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""

new_claim = """	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_claim_midnight_climax }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 4 } } localization_key = USA_mkultra_gui_claim_gateway_assessment }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""
assert old_claim in text, "old_claim not found"
text = text.replace(old_claim, new_claim)

# 9. Appraisal
old_appr = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_appraisal
	}
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_countermeasure_appraisal_pending }"""

new_appr = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_midnight_climax_appraisal
	}
	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 4 } }
		localization_key = USA_mkultra_gui_gateway_assessment_appraisal
	}
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 2 } } localization_key = USA_mkultra_gui_countermeasure_appraisal_pending }"""
assert old_appr in text, "old_appr not found"
text = text.replace(old_appr, new_appr)

# 10. Harm
old_harm = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_harm_midnight_initial
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""

new_harm = """	text = {
		trigger = { check_variable = { USA_mkultra_selected_record = 3 } }
		localization_key = USA_mkultra_gui_harm_midnight_initial
	}
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 4 } } localization_key = USA_mkultra_gui_harm_gateway }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""
assert old_harm in text, "old_harm not found"
text = text.replace(old_harm, new_harm)

# 11. Awards
old_awards = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_initial
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_awards_none }
}"""

new_awards = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			has_country_flag = USA_mkultra_midnight_climax_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_midnight_initial
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_replication_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_gateway_replicated
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_record_awarded
		}
		localization_key = USA_mkultra_gui_awards_gateway_initial
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_awards_none }
}"""
assert old_awards in text, "old_awards not found"
text = text.replace(old_awards, new_awards)

# 12. Dimensions
old_dim = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_vouchers
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_dimension_unavailable }
}"""

new_dim = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_dimension_midnight_vouchers
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 1 }
		}
		localization_key = USA_mkultra_gui_dimension_gateway_sound
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 2 }
		}
		localization_key = USA_mkultra_gui_dimension_gateway_coherence
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 3 }
		}
		localization_key = USA_mkultra_gui_dimension_gateway_nonlocal
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_dimension_gateway_utility
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_dimension_unavailable }
}"""
assert old_dim in text, "old_dim not found"
text = text.replace(old_dim, new_dim)

# 13. State
old_state = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_vouchers
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_evidence_locked }
}"""

new_state = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_evidence_midnight_vouchers
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 1 }
		}
		localization_key = USA_mkultra_gui_evidence_gateway_sound
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 2 }
		}
		localization_key = USA_mkultra_gui_evidence_gateway_coherence
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 3 }
		}
		localization_key = USA_mkultra_gui_evidence_gateway_nonlocal
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_evidence_dimension_array^USA_mkultra_evidence_dimension = 4 }
		}
		localization_key = USA_mkultra_gui_evidence_gateway_utility
	}
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_evidence_locked }
}"""
assert old_state in text, "old_state not found"
text = text.replace(old_state, new_state)

# 14. Application Counter
old_app_c = """	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_application_midnight }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""

new_app_c = """	text = { trigger = { check_variable = { USA_mkultra_selected_record = 3 } } localization_key = USA_mkultra_gui_application_midnight }
	text = { trigger = { check_variable = { USA_mkultra_selected_record = 4 } } localization_key = USA_mkultra_gui_application_gateway }
	text = { trigger = { always = yes } localization_key = USA_mkultra_gui_text_unavailable }
}"""
assert old_app_c in text, "old_app_c not found"
text = text.replace(old_app_c, new_app_c)

# 15. Stamp
old_stamp = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_stamp_cancelled
	}
	text = {
		trigger = { has_country_flag = USA_mkultra_charter_terminated }
		localization_key = USA_mkultra_gui_stamp_closed
	}"""

new_stamp = """	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 3 }
			check_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		localization_key = USA_mkultra_gui_stamp_cancelled
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_archived
		}
		localization_key = USA_mkultra_gui_stamp_archived
	}
	text = {
		trigger = {
			check_variable = { USA_mkultra_selected_record = 4 }
			check_variable = { USA_mkultra_gateway_assessment_stage = 7 }
		}
		localization_key = USA_mkultra_gui_stamp_cancelled
	}
	text = {
		trigger = { has_country_flag = USA_mkultra_charter_terminated }
		localization_key = USA_mkultra_gui_stamp_closed
	}"""
assert old_stamp in text, "old_stamp not found"
text = text.replace(old_stamp, new_stamp)

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_gui_scripted_localisation.txt successfully updated for Dossier 4!")
