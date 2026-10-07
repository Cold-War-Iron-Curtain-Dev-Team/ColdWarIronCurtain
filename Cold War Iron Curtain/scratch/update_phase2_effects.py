import os

effects_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_effects\USA_MKUltra_phase_2_effects.txt'

with open(effects_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update USA_mkultra_phase_2_initialize
old_init = """USA_mkultra_phase_2_initialize = {
	if = {
		limit = { USA_mkultra_enabled_trigger = yes }
		if = {
			limit = { NOT = { has_variable = USA_mkultra_schema_version } }
			set_variable = { USA_mkultra_schema_version = 3 }
		}
		if = {
			limit = { check_variable = { USA_mkultra_schema_version < 3 } }
			set_variable = { USA_mkultra_schema_version = 3 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_countermeasure_stage } }
			set_variable = { USA_mkultra_countermeasure_stage = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_inquiry_state } }
			set_variable = { USA_mkultra_inquiry_state = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_security_scare_state } }
			set_variable = { USA_mkultra_security_scare_state = 0 }
		}
		set_country_flag = USA_mkultra_phase_2_migrated
		USA_mkultra_assign_missing_baseline_profile = yes
		USA_mkultra_gui_initialize = yes
	}
}"""

new_init = """USA_mkultra_phase_2_initialize = {
	if = {
		limit = { USA_mkultra_enabled_trigger = yes }
		if = {
			limit = { NOT = { has_variable = USA_mkultra_schema_version } }
			set_variable = { USA_mkultra_schema_version = 4 }
		}
		if = {
			limit = { check_variable = { USA_mkultra_schema_version < 4 } }
			set_variable = { USA_mkultra_schema_version = 4 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_capacity } }
			set_variable = { USA_mkultra_capacity = 1 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_slot_2_state } }
			set_variable = { USA_mkultra_slot_2_state = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_information_policy } }
			set_variable = { USA_mkultra_information_policy = 1 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_countermeasure_stage } }
			set_variable = { USA_mkultra_countermeasure_stage = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_midnight_climax_stage } }
			set_variable = { USA_mkultra_midnight_climax_stage = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_inquiry_state } }
			set_variable = { USA_mkultra_inquiry_state = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_security_scare_state } }
			set_variable = { USA_mkultra_security_scare_state = 0 }
		}
		set_country_flag = USA_mkultra_phase_2_migrated
		USA_mkultra_assign_missing_baseline_profile = yes
		USA_mkultra_gui_initialize = yes
	}
}"""

# 2. Update USA_mkultra_phase_2_settle_charter_closure
old_closure = """		if = {
			limit = { check_variable = { USA_mkultra_countermeasure_stage = 3 } }
			USA_mkultra_archive_countermeasure = yes
		}
		set_variable = { USA_mkultra_slot_1_state = 0 }
		if = {
			limit = { has_active_mission = USA_mkultra_missing_baseline_renewal_research }
			remove_mission = USA_mkultra_missing_baseline_renewal_research
		}"""

new_closure = """		if = {
			limit = { check_variable = { USA_mkultra_countermeasure_stage = 3 } }
			USA_mkultra_archive_countermeasure = yes
		}
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_stage = 1 } }
			set_variable = { USA_mkultra_midnight_climax_stage = 9 }
		}
		if = {
			limit = {
				OR = {
					check_variable = { USA_mkultra_midnight_climax_stage = 2 }
					check_variable = { USA_mkultra_midnight_climax_stage = 4 }
					check_variable = { USA_mkultra_midnight_climax_stage = 6 }
				}
			}
			USA_mkultra_cancel_midnight_climax = yes
		}
		if = {
			limit = {
				OR = {
					check_variable = { USA_mkultra_midnight_climax_stage = 3 }
					check_variable = { USA_mkultra_midnight_climax_stage = 5 }
					check_variable = { USA_mkultra_midnight_climax_stage = 7 }
				}
			}
			USA_mkultra_archive_midnight_climax = yes
		}
		set_variable = { USA_mkultra_slot_1_state = 0 }
		set_variable = { USA_mkultra_slot_2_state = 0 }
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_research }
			remove_mission = USA_mkultra_midnight_climax_research
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_review }
			remove_mission = USA_mkultra_midnight_climax_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_research }
			remove_mission = USA_mkultra_midnight_climax_renewal_research
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_review }
			remove_mission = USA_mkultra_midnight_climax_renewal_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_replication_research }
			remove_mission = USA_mkultra_midnight_climax_replication_research
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_final_review }
			remove_mission = USA_mkultra_midnight_climax_final_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_missing_baseline_renewal_research }
			remove_mission = USA_mkultra_missing_baseline_renewal_research
		}"""

# Normalize CRLF for replacement
content = content.replace('\r\n', '\n')
old_init_norm = old_init.replace('\r\n', '\n')
new_init_norm = new_init.replace('\r\n', '\n')
old_closure_norm = old_closure.replace('\r\n', '\n')
new_closure_norm = new_closure.replace('\r\n', '\n')

assert old_init_norm in content, "old_init not found"
content = content.replace(old_init_norm, new_init_norm)

assert old_closure_norm in content, "old_closure not found"
content = content.replace(old_closure_norm, new_closure_norm)

# Add Midnight Climax reconcile in USA_mkultra_phase_2_reconcile
reconcile_target = "		if = {\n			limit = { USA_mkultra_charter_active_trigger = yes }\n			USA_mkultra_phase_2_unlock_countermeasure = yes"
reconcile_addition = """		if = {
			limit = { has_country_flag = USA_mkultra_midnight_climax_archived }
			set_variable = { USA_mkultra_midnight_climax_stage = 8 }
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_research }
				remove_mission = USA_mkultra_midnight_climax_research
			}
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_review }
				remove_mission = USA_mkultra_midnight_climax_review
			}
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_research }
				remove_mission = USA_mkultra_midnight_climax_renewal_research
			}
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_review }
				remove_mission = USA_mkultra_midnight_climax_renewal_review
			}
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_replication_research }
				remove_mission = USA_mkultra_midnight_climax_replication_research
			}
			if = {
				limit = { has_active_mission = USA_mkultra_midnight_climax_final_review }
				remove_mission = USA_mkultra_midnight_climax_final_review
			}
		}

		if = {
			limit = { USA_mkultra_charter_active_trigger = yes }
			USA_mkultra_phase_2_unlock_countermeasure = yes
			if = {
				limit = {
					has_country_flag = USA_mkultra_midnight_climax_unlocked
					check_variable = { USA_mkultra_midnight_climax_stage = 0 }
				}
				set_variable = { USA_mkultra_midnight_climax_stage = 1 }
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 2 }
					has_country_flag = USA_mkultra_midnight_climax_record_awarded
				}
				set_variable = { USA_mkultra_midnight_climax_stage = 3 }
				if = {
					limit = { has_active_mission = USA_mkultra_midnight_climax_research }
					remove_mission = USA_mkultra_midnight_climax_research
				}
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 4 }
					has_country_flag = USA_mkultra_midnight_climax_renewal_record_awarded
				}
				set_variable = { USA_mkultra_midnight_climax_stage = 5 }
				if = {
					limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_research }
					remove_mission = USA_mkultra_midnight_climax_renewal_research
				}
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 6 }
					has_country_flag = USA_mkultra_midnight_climax_replication_record_awarded
				}
				set_variable = { USA_mkultra_midnight_climax_stage = 7 }
				if = {
					limit = { has_active_mission = USA_mkultra_midnight_climax_replication_research }
					remove_mission = USA_mkultra_midnight_climax_replication_research
				}
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 2 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_research }
				}
				activate_mission = USA_mkultra_midnight_climax_research
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 3 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_review }
				}
				activate_mission = USA_mkultra_midnight_climax_review
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 4 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_renewal_research }
				}
				activate_mission = USA_mkultra_midnight_climax_renewal_research
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 5 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_renewal_review }
				}
				activate_mission = USA_mkultra_midnight_climax_renewal_review
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 6 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_replication_research }
				}
				activate_mission = USA_mkultra_midnight_climax_replication_research
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 7 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_final_review }
				}
				activate_mission = USA_mkultra_midnight_climax_final_review
			}"""

assert reconcile_target in content, "reconcile_target not found"
content = content.replace(reconcile_target, reconcile_addition)

# Now append Phase 3 & Phase 4 new scripted effects
phase_3_4_append = """

# Phase 3 & 4: New Effects
USA_mkultra_review_precursor_brief = {
	if = {
		limit = { USA_mkultra_can_review_precursor_trigger = yes }
		set_country_flag = USA_mkultra_precursor_reviewed
		set_country_flag = USA_mkultra_preparatory_authority
		add_to_variable = { USA_mkultra_progress = 5 }
		add_to_variable = { USA_mkultra_exposure = 1 }
		USA_mkultra_clamp_variables = yes
		country_event = { id = cwic_mkultra.101 }
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_expand_charter_capacity = {
	if = {
		limit = { USA_mkultra_can_expand_capacity_trigger = yes }
		set_variable = { USA_mkultra_capacity = 2 }
		set_country_flag = USA_mkultra_expanded_authorization_granted
		country_event = { id = cwic_mkultra.310 }
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_apply_policy_compartmentalization = {
	if = {
		limit = { USA_mkultra_can_policy_compartmentalization_trigger = yes }
		set_variable = { USA_mkultra_information_policy = 2 }
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_apply_policy_shared_review = {
	if = {
		limit = { USA_mkultra_can_policy_shared_review_trigger = yes }
		set_variable = { USA_mkultra_information_policy = 1 }
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_unlock_midnight_climax = {
	if = {
		limit = {
			USA_mkultra_enabled_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 0 }
			NOT = { has_country_flag = USA_mkultra_midnight_climax_unlocked }
		}
		set_country_flag = USA_mkultra_midnight_climax_unlocked
		set_variable = { USA_mkultra_midnight_climax_stage = 1 }
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_start_midnight_climax = {
	if = {
		limit = { USA_mkultra_can_start_midnight_climax_trigger = yes }
		set_country_flag = USA_mkultra_midnight_climax_paid
		set_country_flag = USA_mkultra_midnight_climax_owner_cia
		set_variable = { USA_mkultra_midnight_climax_stage = 2 }
		
		if = {
			limit = { check_variable = { USA_mkultra_slot_1_state = 0 } }
			set_variable = { USA_mkultra_midnight_climax_slot = 1 }
			set_variable = { USA_mkultra_slot_1_state = 1 }
		}
		else = {
			set_variable = { USA_mkultra_midnight_climax_slot = 2 }
			set_variable = { USA_mkultra_slot_2_state = 1 }
		}

		if = {
			limit = { check_variable = { USA_mkultra_information_policy = 2 } }
			add_to_variable = { USA_mkultra_exposure = 6 }
		}
		else = {
			add_to_variable = { USA_mkultra_exposure = 8 }
		}
		add_to_variable = { USA_mkultra_harm = 8 }

		if = {
			limit = { check_variable = { USA_mkultra_capacity = 2 } }
			add_political_power = -5
			add_to_variable = { USA_mkultra_exposure = 1 }
		}

		USA_mkultra_clamp_variables = yes
		USA_mkultra_evaluate_basic_inquiry = yes
		activate_mission = USA_mkultra_midnight_climax_research
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_complete_midnight_climax = {
	if = {
		limit = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 2 }
			has_country_flag = USA_mkultra_midnight_climax_paid
			NOT = { has_country_flag = USA_mkultra_midnight_climax_record_awarded }
		}
		set_country_flag = USA_mkultra_midnight_climax_record_awarded
		add_to_variable = { USA_mkultra_progress = 16 }
		set_variable = { USA_mkultra_midnight_climax_stage = 3 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 2 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 2 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_research }
			remove_mission = USA_mkultra_midnight_climax_research
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_midnight_climax_review
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_cancel_midnight_climax = {
	if = {
		limit = {
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 2 }
				check_variable = { USA_mkultra_midnight_climax_stage = 4 }
				check_variable = { USA_mkultra_midnight_climax_stage = 6 }
			}
		}
		set_variable = { USA_mkultra_midnight_climax_stage = 9 }
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 0 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 0 }
		}
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_start_midnight_climax_renewal = {
	if = {
		limit = { USA_mkultra_can_renew_midnight_climax_trigger = yes }
		set_country_flag = USA_mkultra_midnight_climax_renewal_paid
		set_variable = { USA_mkultra_midnight_climax_stage = 4 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 1 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 1 }
		}

		if = {
			limit = { check_variable = { USA_mkultra_information_policy = 2 } }
			add_to_variable = { USA_mkultra_exposure = 6 }
		}
		else = {
			add_to_variable = { USA_mkultra_exposure = 8 }
		}
		add_to_variable = { USA_mkultra_harm = 8 }

		if = {
			limit = { check_variable = { USA_mkultra_capacity = 2 } }
			add_political_power = -5
			add_to_variable = { USA_mkultra_exposure = 1 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_review }
			remove_mission = USA_mkultra_midnight_climax_review
		}
		USA_mkultra_clamp_variables = yes
		USA_mkultra_evaluate_basic_inquiry = yes
		activate_mission = USA_mkultra_midnight_climax_renewal_research
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_complete_midnight_climax_renewal = {
	if = {
		limit = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 4 }
			has_country_flag = USA_mkultra_midnight_climax_renewal_paid
			NOT = { has_country_flag = USA_mkultra_midnight_climax_renewal_record_awarded }
		}
		set_country_flag = USA_mkultra_midnight_climax_renewal_record_awarded
		add_to_variable = { USA_mkultra_progress = 6 }
		set_variable = { USA_mkultra_midnight_climax_stage = 5 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 2 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 2 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_research }
			remove_mission = USA_mkultra_midnight_climax_renewal_research
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_midnight_climax_renewal_review
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_start_midnight_climax_replication = {
	if = {
		limit = { USA_mkultra_can_replicate_midnight_climax_trigger = yes }
		set_country_flag = USA_mkultra_midnight_climax_replication_paid
		set_variable = { USA_mkultra_midnight_climax_stage = 6 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 1 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 1 }
		}

		add_to_variable = { USA_mkultra_exposure = 1 }

		if = {
			limit = { check_variable = { USA_mkultra_information_policy = 2 } }
			add_political_power = -10
		}
		if = {
			limit = { check_variable = { USA_mkultra_capacity = 2 } }
			add_political_power = -5
			add_to_variable = { USA_mkultra_exposure = 1 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_review }
			remove_mission = USA_mkultra_midnight_climax_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_review }
			remove_mission = USA_mkultra_midnight_climax_renewal_review
		}
		USA_mkultra_clamp_variables = yes
		USA_mkultra_evaluate_basic_inquiry = yes
		activate_mission = USA_mkultra_midnight_climax_replication_research
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_complete_midnight_climax_replication = {
	if = {
		limit = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 6 }
			has_country_flag = USA_mkultra_midnight_climax_replication_paid
			NOT = { has_country_flag = USA_mkultra_midnight_climax_replication_record_awarded }
		}
		set_country_flag = USA_mkultra_midnight_climax_replication_record_awarded
		add_to_variable = { USA_mkultra_progress = 6 }
		set_variable = { USA_mkultra_midnight_climax_stage = 7 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 2 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 2 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_replication_research }
			remove_mission = USA_mkultra_midnight_climax_replication_research
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_midnight_climax_final_review
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_archive_midnight_climax = {
	if = {
		limit = {
			USA_mkultra_enabled_trigger = yes
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 3 }
				check_variable = { USA_mkultra_midnight_climax_stage = 5 }
				check_variable = { USA_mkultra_midnight_climax_stage = 7 }
			}
		}
		set_country_flag = USA_mkultra_midnight_climax_archived
		set_variable = { USA_mkultra_midnight_climax_stage = 8 }
		
		if = {
			limit = { check_variable = { USA_mkultra_midnight_climax_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 0 }
		}
		else = {
			set_variable = { USA_mkultra_slot_1_state = 0 }
		}

		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_review }
			remove_mission = USA_mkultra_midnight_climax_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_renewal_review }
			remove_mission = USA_mkultra_midnight_climax_renewal_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_midnight_climax_final_review }
			remove_mission = USA_mkultra_midnight_climax_final_review
		}
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_ig_review_mksearch = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_ig_review_resolved
		set_country_flag = USA_mkultra_mksearch_reorganization
		add_to_variable = { USA_mkultra_exposure = -15 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_ig_review_tighten = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_ig_review_resolved
		set_country_flag = USA_mkultra_ig_review_tightened
		add_political_power = -15
		add_to_variable = { USA_mkultra_exposure = -10 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_records_preserve = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_records_disposition_decided
		set_country_flag = USA_mkultra_records_preserved
		add_political_power = -10
		add_to_variable = { USA_mkultra_exposure = 5 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_records_seal = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_records_disposition_decided
		set_country_flag = USA_mkultra_records_sealed
		add_political_power = -15
		add_to_variable = { USA_mkultra_exposure = -5 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_records_destroy = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_records_disposition_decided
		set_country_flag = USA_mkultra_records_destroyed
		add_political_power = -5
		add_to_variable = { USA_mkultra_exposure = -10 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_records_retain = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_records_disposition_decided
		set_country_flag = USA_mkultra_records_retained_current
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_church_committee = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_church_committee_resolved
		if = {
			limit = { USA_mkultra_charter_active_trigger = yes }
			USA_mkultra_terminate_charter = yes
		}
		add_political_power = -50
		add_stability = -0.02
		add_to_variable = { USA_mkultra_exposure = -15 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_senate_hearing = {
	if = {
		limit = { tag = USA }
		set_country_flag = USA_mkultra_senate_hearing_resolved
		set_country_flag = USA_mkultra_invoices_survived
		add_political_power = -25
		add_stability = -0.01
		add_to_variable = { USA_mkultra_exposure = -10 }
		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_seed_1980_archive = {
	if = {
		limit = {
			tag = USA
			USA_mkultra_enabled_trigger = yes
			NOT = { has_country_flag = USA_mkultra_initialized }
		}
		set_country_flag = USA_mkultra_initialized
		set_country_flag = USA_mkultra_charter_terminated
		set_country_flag = USA_mkultra_expanded_authorization_granted
		set_country_flag = USA_mkultra_precursor_reviewed
		set_country_flag = USA_mkultra_missing_baseline_paid
		set_country_flag = USA_mkultra_missing_baseline_archived
		set_country_flag = USA_mkultra_countermeasure_paid
		set_country_flag = USA_mkultra_countermeasure_archived
		set_country_flag = USA_mkultra_midnight_climax_paid
		set_country_flag = USA_mkultra_midnight_climax_archived
		set_country_flag = USA_mkultra_ig_review_resolved
		set_country_flag = USA_mkultra_records_disposition_decided
		set_country_flag = USA_mkultra_records_destroyed
		set_country_flag = USA_mkultra_invoices_survived
		set_country_flag = USA_mkultra_church_committee_resolved
		set_country_flag = USA_mkultra_senate_hearing_resolved
		set_country_flag = USA_mkultra_historical_archive_seeded

		set_variable = { USA_mkultra_schema_version = 4 }
		set_variable = { USA_mkultra_charter_id = 1 }
		set_variable = { USA_mkultra_charter_state = 2 }
		set_variable = { USA_mkultra_capacity = 2 }
		set_variable = { USA_mkultra_slot_1_state = 0 }
		set_variable = { USA_mkultra_slot_2_state = 0 }
		set_variable = { USA_mkultra_information_policy = 1 }
		set_variable = { USA_mkultra_inquiry_state = 2 }
		set_variable = { USA_mkultra_progress = 52 }
		set_variable = { USA_mkultra_exposure = 15 }
		set_variable = { USA_mkultra_harm = 28 }
		set_variable = { USA_mkultra_missing_baseline_stage = 3 }
		set_variable = { USA_mkultra_countermeasure_stage = 4 }
		set_variable = { USA_mkultra_midnight_climax_stage = 8 }

		USA_mkultra_clamp_variables = yes
		USA_mkultra_gui_initialize = yes
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}
"""

content = content + phase_3_4_append

with open(effects_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

print("USA_MKUltra_phase_2_effects.txt updated successfully!")
