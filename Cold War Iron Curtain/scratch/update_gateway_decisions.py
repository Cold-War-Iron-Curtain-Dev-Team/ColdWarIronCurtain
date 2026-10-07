import os

path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\decisions\USA_MKUltra_decisions.txt'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

target = """	USA_mkultra_terminate_charter = {"""

decisions_addition = """	# Dossier 4: 1983 Army INSCOM Gateway Assessment
	USA_mkultra_commission_gateway_assessment = {
		icon = generic_intelligence_agency
		cost = 25
		fire_only_once = yes
		visible = {
			USA_mkultra_enabled_trigger = yes
			check_variable = { USA_mkultra_gateway_assessment_stage = 1 }
			has_country_flag = USA_mkultra_gateway_assessment_unlocked
		}
		available = {
			USA_mkultra_can_start_gateway_assessment_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_commission_gateway_assessment_tt
			USA_mkultra_start_gateway_assessment = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 70
				USA_mkultra_ai_can_afford_gateway_assessment_trigger = yes
			}
		}
	}

	USA_mkultra_gateway_assessment_research = {
		icon = generic_research
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 90
		is_good = yes

		timeout_effect = {
			USA_mkultra_complete_gateway_assessment = yes
		}
		cancel_trigger = {
			OR = {
				has_country_flag = USA_mkultra_charter_terminated
				NOT = { check_variable = { USA_mkultra_gateway_assessment_stage = 2 } }
			}
		}
		cancel_effect = {
			USA_mkultra_cancel_gateway_assessment = yes
		}
	}

	USA_mkultra_gateway_assessment_review = {
		icon = generic_prepare_civil_war
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 30
		is_good = no

		timeout_effect = {
			USA_mkultra_archive_gateway_assessment = yes
		}
		cancel_trigger = {
			OR = {
				has_country_flag = USA_mkultra_charter_terminated
				NOT = { check_variable = { USA_mkultra_gateway_assessment_stage = 3 } }
			}
		}
		cancel_effect = {
			USA_mkultra_archive_gateway_assessment = yes
		}
	}

	USA_mkultra_replicate_gateway_assessment = {
		icon = generic_intelligence_agency
		cost = 25
		fire_only_once = yes
		visible = {
			USA_mkultra_enabled_trigger = yes
			check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
			has_country_flag = USA_mkultra_gateway_assessment_report_opened
			NOT = { has_country_flag = USA_mkultra_gateway_assessment_replication_paid }
		}
		available = {
			USA_mkultra_can_replicate_gateway_assessment_trigger = yes
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_replicate_gateway_assessment_tt
			USA_mkultra_start_gateway_replication = yes
		}
		ai_will_do = {
			factor = 0
			modifier = {
				add = 40
				has_political_power > 120
			}
		}
	}

	USA_mkultra_gateway_assessment_replication_research = {
		icon = generic_research
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 60
		is_good = yes

		timeout_effect = {
			USA_mkultra_complete_gateway_replication = yes
		}
		cancel_trigger = {
			OR = {
				has_country_flag = USA_mkultra_charter_terminated
				NOT = { check_variable = { USA_mkultra_gateway_assessment_stage = 4 } }
			}
		}
		cancel_effect = {
			USA_mkultra_cancel_gateway_assessment = yes
		}
	}

	USA_mkultra_gateway_assessment_final_review = {
		icon = generic_prepare_civil_war
		activation = { always = no }
		available = { always = no }
		days_mission_timeout = 30
		is_good = no

		timeout_effect = {
			USA_mkultra_archive_gateway_assessment = yes
		}
		cancel_trigger = {
			OR = {
				has_country_flag = USA_mkultra_charter_terminated
				NOT = { check_variable = { USA_mkultra_gateway_assessment_stage = 5 } }
			}
		}
		cancel_effect = {
			USA_mkultra_archive_gateway_assessment = yes
		}
	}

	USA_mkultra_archive_gateway_assessment = {
		icon = generic_intelligence_agency
		cost = 0
		visible = {
			USA_mkultra_enabled_trigger = yes
			OR = {
				check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
				check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
			}
		}
		available = {
			OR = {
				check_variable = { USA_mkultra_gateway_assessment_stage = 3 }
				check_variable = { USA_mkultra_gateway_assessment_stage = 5 }
			}
		}
		complete_effect = {
			custom_effect_tooltip = USA_mkultra_archive_gateway_assessment_tt
			USA_mkultra_archive_gateway_assessment = yes
		}
		ai_will_do = { factor = 100 }
	}

	USA_mkultra_terminate_charter = {"""

assert target in text, "target not found"
text = text.replace(target, decisions_addition)

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_decisions.txt updated successfully!")
