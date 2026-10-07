decisions_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\decisions\USA_MKUltra_decisions.txt'

with open(decisions_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

target = "\tUSA_mkultra_terminate_charter = {"

new_decisions = """\tUSA_mkultra_precursor_brief = {
		icon = generic_intelligence_agency
		cost = 10
		fire_only_once = yes
		visible = {
			USA_mkultra_enabled_trigger = yes
			date < 1953.4.13
			NOT = { has_country_flag = USA_mkultra_precursor_reviewed }
		}
		available = {
			USA_mkultra_can_review_precursor_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_precursor_brief_tt
			USA_mkultra_review_precursor_brief = yes
		}
		ai_will_do = { factor = 100 }
	}

	USA_mkultra_expand_charter_capacity = {
		icon = generic_intelligence_agency
		cost = 60
		fire_only_once = yes
		visible = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_capacity = 1 }
			NOT = { has_country_flag = USA_mkultra_expanded_authorization_granted }
		}
		available = {
			USA_mkultra_can_expand_capacity_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_expand_charter_capacity_tt
			USA_mkultra_expand_charter_capacity = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 100
				USA_mkultra_ai_can_afford_expansion_trigger = yes
			}
		}
	}

	USA_mkultra_policy_compartmentalization = {
		icon = generic_intelligence_agency
		cost = 20
		visible = {
			USA_mkultra_charter_active_trigger = yes
			NOT = { check_variable = { USA_mkultra_information_policy = 2 } }
		}
		available = {
			USA_mkultra_can_policy_compartmentalization_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_policy_compartmentalization_tt
			USA_mkultra_apply_policy_compartmentalization = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 50
				check_variable = { USA_mkultra_exposure > 40 }
				has_political_power > 150
			}
		}
	}

	USA_mkultra_policy_shared_review = {
		icon = generic_intelligence_agency
		cost = 10
		visible = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_information_policy = 2 }
		}
		available = {
			USA_mkultra_can_policy_shared_review_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_policy_shared_review_tt
			USA_mkultra_apply_policy_shared_review = yes
		}
		ai_will_do = { factor = 0 }
	}

	# Historical Dossier 3: Operation Midnight Climax
	USA_mkultra_commission_midnight_climax = {
		icon = generic_intelligence_agency
		cost = 25
		fire_only_once = yes
		visible = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 1 }
			has_country_flag = USA_mkultra_midnight_climax_unlocked
		}
		available = {
			USA_mkultra_can_start_midnight_climax_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_commission_midnight_climax_tt
			USA_mkultra_start_midnight_climax = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 60
				USA_mkultra_ai_can_afford_midnight_climax_trigger = yes
			}
		}
	}

	USA_mkultra_midnight_climax_research = {
		icon = generic_research
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 90
		is_good = yes

		timeout_effect = { USA_mkultra_complete_midnight_climax = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 2 } }
			}
		}
		cancel_effect = { USA_mkultra_cancel_midnight_climax = yes }
	}

	USA_mkultra_midnight_climax_review = {
		icon = generic_intelligence_agency
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 30
		is_good = yes

		timeout_effect = { USA_mkultra_archive_midnight_climax = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 3 } }
			}
		}
		cancel_effect = { USA_mkultra_archive_midnight_climax = yes }
	}

	USA_mkultra_renew_midnight_climax = {
		icon = generic_research
		cost = 25
		fire_only_once = yes
		visible = {
			USA_mkultra_charter_active_trigger = yes
			check_variable = { USA_mkultra_midnight_climax_stage = 3 }
			NOT = { has_country_flag = USA_mkultra_midnight_climax_renewal_paid }
		}
		available = {
			USA_mkultra_can_renew_midnight_climax_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_renew_midnight_climax_tt
			USA_mkultra_start_midnight_climax_renewal = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 40
				USA_mkultra_ai_can_afford_midnight_climax_trigger = yes
			}
		}
	}

	USA_mkultra_midnight_climax_renewal_research = {
		icon = generic_research
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 90
		is_good = yes

		timeout_effect = { USA_mkultra_complete_midnight_climax_renewal = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 4 } }
			}
		}
		cancel_effect = { USA_mkultra_cancel_midnight_climax = yes }
	}

	USA_mkultra_midnight_climax_renewal_review = {
		icon = generic_intelligence_agency
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 30
		is_good = yes

		timeout_effect = { USA_mkultra_archive_midnight_climax = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 5 } }
			}
		}
		cancel_effect = { USA_mkultra_archive_midnight_climax = yes }
	}

	USA_mkultra_replicate_midnight_climax = {
		icon = generic_research
		cost = 30
		fire_only_once = yes
		visible = {
			USA_mkultra_charter_active_trigger = yes
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 3 }
				check_variable = { USA_mkultra_midnight_climax_stage = 5 }
			}
			NOT = { has_country_flag = USA_mkultra_midnight_climax_replication_paid }
		}
		available = {
			USA_mkultra_can_replicate_midnight_climax_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_replicate_midnight_climax_tt
			USA_mkultra_start_midnight_climax_replication = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 70
				USA_mkultra_ai_can_afford_midnight_climax_trigger = yes
			}
		}
	}

	USA_mkultra_midnight_climax_replication_research = {
		icon = generic_research
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 90
		is_good = yes

		timeout_effect = { USA_mkultra_complete_midnight_climax_replication = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 6 } }
			}
		}
		cancel_effect = { USA_mkultra_cancel_midnight_climax = yes }
	}

	USA_mkultra_midnight_climax_final_review = {
		icon = generic_intelligence_agency
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 30
		is_good = yes

		timeout_effect = { USA_mkultra_archive_midnight_climax = yes }
		cancel_trigger = {
			OR = {
				NOT = { USA_mkultra_charter_active_trigger = yes }
				NOT = { check_variable = { USA_mkultra_midnight_climax_stage = 7 } }
			}
		}
		cancel_effect = { USA_mkultra_archive_midnight_climax = yes }
	}

	USA_mkultra_archive_midnight_climax = {
		icon = generic_intelligence_agency
		cost = 0
		visible = {
			USA_mkultra_enabled_trigger = yes
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 3 }
				check_variable = { USA_mkultra_midnight_climax_stage = 5 }
				check_variable = { USA_mkultra_midnight_climax_stage = 7 }
			}
		}
		available = {
			OR = {
				check_variable = { USA_mkultra_midnight_climax_stage = 3 }
				check_variable = { USA_mkultra_midnight_climax_stage = 5 }
				check_variable = { USA_mkultra_midnight_climax_stage = 7 }
			}
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_archive_midnight_climax_tt
			USA_mkultra_archive_midnight_climax = yes
		}
		ai_will_do = { factor = 100 }
	}

"""

assert target in text, "target not found"
text = text.replace(target, new_decisions + target)

with open(decisions_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_decisions.txt updated successfully!")
