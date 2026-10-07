import os

path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\scripted_effects\USA_MKUltra_phase_2_effects.txt'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

# 1. Add variable init in USA_mkultra_phase_2_initialize
init_target = """		if = {
			limit = { NOT = { has_variable = USA_mkultra_midnight_climax_stage } }
			set_variable = { USA_mkultra_midnight_climax_stage = 0 }
		}"""

init_addition = """		if = {
			limit = { NOT = { has_variable = USA_mkultra_midnight_climax_stage } }
			set_variable = { USA_mkultra_midnight_climax_stage = 0 }
		}
		if = {
			limit = { NOT = { has_variable = USA_mkultra_gateway_assessment_stage } }
			set_variable = { USA_mkultra_gateway_assessment_stage = 0 }
		}"""

assert init_target in text, "init_target not found"
text = text.replace(init_target, init_addition)

# 2. Add stale mission recovery in USA_mkultra_recover_stale_records
recover_target = """			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 7 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_final_review }
				}
				activate_mission = USA_mkultra_midnight_climax_final_review
			}"""

recover_addition = """			if = {
				limit = {
					check_variable = { USA_mkultra_midnight_climax_stage = 7 }
					NOT = { has_active_mission = USA_mkultra_midnight_climax_final_review }
				}
				activate_mission = USA_mkultra_midnight_climax_final_review
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_gateway_assessment_stage = 2 }
					NOT = { has_active_mission = USA_mkultra_gateway_assessment_research }
				}
				activate_mission = USA_mkultra_gateway_assessment_research
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
					NOT = { has_active_mission = USA_mkultra_gateway_assessment_review }
				}
				activate_mission = USA_mkultra_gateway_assessment_review
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_gateway_assessment_stage = 4 }
					NOT = { has_active_mission = USA_mkultra_gateway_assessment_replication_research }
				}
				activate_mission = USA_mkultra_gateway_assessment_replication_research
			}
			if = {
				limit = {
					check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
					NOT = { has_active_mission = USA_mkultra_gateway_assessment_final_review }
				}
				activate_mission = USA_mkultra_gateway_assessment_final_review
			}"""

assert recover_target in text, "recover_target not found"
text = text.replace(recover_target, recover_addition)

# 3. Add Phase 5 Gateway Effects at the end
phase5_effects = """

# Phase 5: Gateway Extension & Historical Endings
USA_mkultra_unlock_gateway_assessment = {
	if = {
		limit = {
			USA_mkultra_enabled_trigger = yes
			check_variable = { USA_mkultra_gateway_assessment_stage = 0 }
			NOT = { has_country_flag = USA_mkultra_gateway_assessment_unlocked }
		}
		set_country_flag = USA_mkultra_gateway_assessment_unlocked
		set_variable = { USA_mkultra_gateway_assessment_stage = 1 }
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_start_gateway_assessment = {
	if = {
		limit = { USA_mkultra_can_start_gateway_assessment_trigger = yes }
		set_country_flag = USA_mkultra_gateway_assessment_paid
		set_country_flag = USA_mkultra_gateway_assessment_owner_inscom
		set_variable = { USA_mkultra_gateway_assessment_stage = 2 }

		if = {
			limit = { check_variable = { USA_mkultra_slot_1_state = 0 } }
			set_variable = { USA_mkultra_gateway_assessment_slot = 1 }
			set_variable = { USA_mkultra_slot_1_state = 1 }
		}
		else = {
			set_variable = { USA_mkultra_gateway_assessment_slot = 2 }
			set_variable = { USA_mkultra_slot_2_state = 1 }
		}

		if = {
			limit = { check_variable = { USA_mkultra_information_policy = 2 } }
			add_to_variable = { USA_mkultra_exposure = 1 }
		}
		else = {
			add_to_variable = { USA_mkultra_exposure = 2 }
		}

		if = {
			limit = { check_variable = { USA_mkultra_capacity = 2 } }
			add_political_power = -5
			add_to_variable = { USA_mkultra_exposure = 1 }
		}

		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_gateway_assessment_research
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_complete_gateway_assessment = {
	if = {
		limit = {
			check_variable = { USA_mkultra_gateway_assessment_stage = 2 }
			has_country_flag = USA_mkultra_gateway_assessment_paid
			NOT = { has_country_flag = USA_mkultra_gateway_assessment_record_awarded }
		}
		set_country_flag = USA_mkultra_gateway_assessment_record_awarded
		set_country_flag = USA_mkultra_gateway_assessment_report_opened
		add_to_variable = { USA_mkultra_progress = 14 }
		set_variable = { USA_mkultra_gateway_assessment_stage = 3 }
		if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 1 } }
			set_variable = { USA_mkultra_slot_1_state = 2 }
		}
		else_if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 2 }
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_research }
			remove_mission = USA_mkultra_gateway_assessment_research
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_gateway_assessment_review
		country_event = { id = cwic_mkultra.405 }
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_start_gateway_replication = {
	if = {
		limit = { USA_mkultra_can_replicate_gateway_assessment_trigger = yes }
		set_country_flag = USA_mkultra_gateway_assessment_replication_paid
		set_variable = { USA_mkultra_gateway_assessment_stage = 4 }
		if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 1 } }
			set_variable = { USA_mkultra_slot_1_state = 1 }
		}
		else_if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 1 }
		}
		add_to_variable = { USA_mkultra_exposure = 1 }
		if = {
			limit = { check_variable = { USA_mkultra_capacity = 2 } }
			add_political_power = -5
			add_to_variable = { USA_mkultra_exposure = 1 }
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_review }
			remove_mission = USA_mkultra_gateway_assessment_review
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_gateway_assessment_replication_research
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_complete_gateway_replication = {
	if = {
		limit = {
			check_variable = { USA_mkultra_gateway_assessment_stage = 4 }
			has_country_flag = USA_mkultra_gateway_assessment_replication_paid
			NOT = { has_country_flag = USA_mkultra_gateway_assessment_replication_record_awarded }
		}
		set_country_flag = USA_mkultra_gateway_assessment_replication_record_awarded
		add_to_variable = { USA_mkultra_progress = 6 }
		set_variable = { USA_mkultra_gateway_assessment_stage = 5 }
		if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 1 } }
			set_variable = { USA_mkultra_slot_1_state = 2 }
		}
		else_if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 2 }
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_replication_research }
			remove_mission = USA_mkultra_gateway_assessment_replication_research
		}
		USA_mkultra_clamp_variables = yes
		activate_mission = USA_mkultra_gateway_assessment_final_review
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_archive_gateway_assessment = {
	if = {
		limit = {
			OR = {
				check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
				check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
			}
		}
		set_country_flag = USA_mkultra_gateway_assessment_archived
		set_variable = { USA_mkultra_gateway_assessment_stage = 6 }
		if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 1 } }
			set_variable = { USA_mkultra_slot_1_state = 0 }
		}
		else_if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 0 }
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_review }
			remove_mission = USA_mkultra_gateway_assessment_review
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_final_review }
			remove_mission = USA_mkultra_gateway_assessment_final_review
		}
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_cancel_gateway_assessment = {
	if = {
		limit = {
			OR = {
				check_variable = { USA_mkultra_gateway_assessment_stage = 2 }
				check_variable = { USA_mkultra_gateway_assessment_stage = 4 }
			}
		}
		set_country_flag = USA_mkultra_gateway_assessment_cancelled
		set_variable = { USA_mkultra_gateway_assessment_stage = 7 }
		if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 1 } }
			set_variable = { USA_mkultra_slot_1_state = 0 }
		}
		else_if = {
			limit = { check_variable = { USA_mkultra_gateway_assessment_slot = 2 } }
			set_variable = { USA_mkultra_slot_2_state = 0 }
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_research }
			remove_mission = USA_mkultra_gateway_assessment_research
		}
		if = {
			limit = { has_active_mission = USA_mkultra_gateway_assessment_replication_research }
			remove_mission = USA_mkultra_gateway_assessment_replication_research
		}
		USA_mkultra_gui_reconcile = yes
		USA_mkultra_mark_gui_dirty = yes
	}
}

USA_mkultra_resolve_gateway_authorize = {
	set_country_flag = USA_mkultra_gateway_authorized
	set_country_flag = USA_mkultra_gateway_assessment_unlocked
	set_variable = { USA_mkultra_gateway_assessment_stage = 1 }
	set_variable = { USA_mkultra_charter_state = 3 }
	add_political_power = -25
	if = {
		limit = {
			OR = {
				check_variable = { USA_mkultra_records_state = 1 }
				check_variable = { USA_mkultra_records_state = 2 }
			}
		}
		add_to_variable = { USA_mkultra_progress = 15 }
	}
	else = {
		add_to_variable = { USA_mkultra_progress = 10 }
	}
	USA_mkultra_clamp_variables = yes
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_gateway_archive_transfer = {
	set_country_flag = USA_mkultra_gateway_archive_transferred
	add_political_power = -10
	add_to_variable = { USA_mkultra_progress = 5 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_gateway_decline = {
	set_country_flag = USA_mkultra_gateway_declined
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_early_assessment_preparedness = {
	set_country_flag = USA_mkultra_early_preparedness
	add_political_power = -20
	add_to_variable = { USA_mkultra_exposure = 5 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_early_assessment_appraisal = {
	set_country_flag = USA_mkultra_early_appraisal_active
	add_political_power = -30
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_early_assessment_archive = {
	set_country_flag = USA_mkultra_early_assessment_archived
	add_to_variable = { USA_mkultra_progress = 4 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_early_assessment_comparison = {
	set_country_flag = USA_mkultra_early_assessment_resolved
	add_to_variable = { USA_mkultra_progress = 8 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_air_review_decommission = {
	set_country_flag = USA_mkultra_air_decommissioned
	set_variable = { USA_mkultra_charter_state = 2 }
	set_variable = { USA_mkultra_slot_1_state = 0 }
	set_variable = { USA_mkultra_slot_2_state = 0 }
	add_political_power = 20
	if = {
		limit = { check_variable = { USA_mkultra_exposure > 19 } }
		subtract_from_variable = { USA_mkultra_exposure = 20 }
	}
	else = {
		set_variable = { USA_mkultra_exposure = 0 }
	}
	USA_mkultra_clamp_variables = yes
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_air_review_seal = {
	set_country_flag = USA_mkultra_air_sealed
	add_political_power = -15
	USA_mkultra_clamp_variables = yes
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_cultural_afterlife_deny = {
	set_country_flag = USA_mkultra_cultural_afterlife_resolved
	add_to_variable = { USA_mkultra_exposure = 2 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_cultural_afterlife_foia = {
	set_country_flag = USA_mkultra_cultural_afterlife_resolved
	add_political_power = -10
	if = {
		limit = { check_variable = { USA_mkultra_exposure > 4 } }
		subtract_from_variable = { USA_mkultra_exposure = 5 }
	}
	else = {
		set_variable = { USA_mkultra_exposure = 0 }
	}
	USA_mkultra_clamp_variables = yes
	USA_mkultra_mark_gui_dirty = yes
}

USA_mkultra_resolve_y2k_epilogue = {
	set_country_flag = USA_mkultra_y2k_epilogue_resolved
	add_to_variable = { USA_mkultra_progress = 5 }
	USA_mkultra_clamp_variables = yes
	USA_mkultra_gui_reconcile = yes
	USA_mkultra_mark_gui_dirty = yes
}
"""

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text + phase5_effects)

print("USA_MKUltra_phase_2_effects.txt updated successfully!")
