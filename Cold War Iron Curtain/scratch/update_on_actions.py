path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\common\on_actions\USA_MKUltra_on_actions.txt'

new_content = """on_actions = {
	on_startup = {
		effect = {
			if = {
				limit = { country_exists = USA }
				USA = {
					if = {
						limit = {
							date > 1979.12.30
							NOT = { has_country_flag = USA_mkultra_initialized }
						}
						USA_mkultra_seed_1980_archive = yes
					}
					else_if = {
						limit = {
							OR = {
								has_variable = USA_mkultra_schema_version
								USA_mkultra_has_entry_authority_trigger = yes
							}
						}
						USA_mkultra_initialize = yes
					}
				}
			}
		}
	}

	# The monthly hook handles date gates, historical lifecycle milestones,
	# and lightweight recovery pass.
	on_monthly_USA = {
		effect = {
			if = {
				limit = {
					OR = {
						has_variable = USA_mkultra_schema_version
						USA_mkultra_has_entry_authority_trigger = yes
					}
				}
				USA_mkultra_initialize = yes

				# 1963-1964 Inspector General Audit
				if = {
					limit = {
						date > 1963.6.1
						USA_mkultra_charter_active_trigger = yes
						NOT = { has_country_flag = USA_mkultra_ig_review_fired }
						OR = {
							check_variable = { USA_mkultra_harm > 7 }
							check_variable = { USA_mkultra_exposure > 24 }
							has_country_flag = USA_mkultra_midnight_climax_paid
						}
					}
					set_country_flag = USA_mkultra_ig_review_fired
					country_event = { id = cwic_mkultra.300 }
				}

				# 1973 Records Disposition
				if = {
					limit = {
						date > 1973.1.1
						has_country_flag = USA_mkultra_initialized
						NOT = { has_country_flag = USA_mkultra_records_disposition_decided }
					}
					country_event = { id = cwic_mkultra.320 }
				}

				# 1975 Church Committee
				if = {
					limit = {
						date > 1975.5.1
						has_country_flag = USA_mkultra_initialized
						NOT = { has_country_flag = USA_mkultra_church_committee_resolved }
						OR = {
							check_variable = { USA_mkultra_harm > 0 }
							check_variable = { USA_mkultra_exposure > 20 }
							has_country_flag = USA_mkultra_records_disposition_decided
						}
					}
					country_event = { id = cwic_mkultra.325 }
				}

				# 1977 Senate Hearings
				if = {
					limit = {
						date > 1977.8.1
						has_country_flag = USA_mkultra_initialized
						has_country_flag = USA_mkultra_church_committee_resolved
						NOT = { has_country_flag = USA_mkultra_senate_hearing_resolved }
					}
					country_event = { id = cwic_mkultra.330 }
				}
			}
		}
	}

	on_annex = {
		effect = {
			if = {
				limit = {
					ROOT = {
						tag = USA
						USA_mkultra_charter_active_trigger = yes
					}
				}
				ROOT = {
					USA_mkultra_terminate_charter = yes
				}
			}
		}
	}

	on_capitulation = {
		effect = {
			if = {
				limit = {
					ROOT = {
						tag = USA
						USA_mkultra_charter_active_trigger = yes
					}
				}
				ROOT = {
					USA_mkultra_terminate_charter = yes
				}
			}
		}
	}
}
"""

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(new_content)

print("USA_MKUltra_on_actions.txt updated successfully!")
