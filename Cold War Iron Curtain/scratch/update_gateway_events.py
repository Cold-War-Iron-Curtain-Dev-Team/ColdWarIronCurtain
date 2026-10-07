import os

path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\events\USA_MKUltra_events.txt'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read().replace('\r\n', '\n')

new_events = """
# 1983 Gateway Assessment (Army INSCOM)
country_event = {
	id = cwic_mkultra.400
	title = cwic_mkultra.400.t
	desc = cwic_mkultra.400.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.400.a
		custom_effect_tooltip = USA_mkultra_gateway_authorize_tt
		USA_mkultra_resolve_gateway_authorize = yes
		ai_chance = { factor = 70 }
	}
	option = {
		name = cwic_mkultra.400.b
		custom_effect_tooltip = USA_mkultra_gateway_archive_transfer_tt
		USA_mkultra_resolve_gateway_archive_transfer = yes
		ai_chance = { factor = 20 }
	}
	option = {
		name = cwic_mkultra.400.c
		custom_effect_tooltip = USA_mkultra_gateway_decline_tt
		USA_mkultra_resolve_gateway_decline = yes
		ai_chance = { factor = 10 }
	}
}

# 1983 Gateway Field Report Review
country_event = {
	id = cwic_mkultra.405
	title = cwic_mkultra.405.t
	desc = cwic_mkultra.405.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.405.a
		custom_effect_tooltip = USA_mkultra_gateway_replicate_opt_tt
		ai_chance = { factor = 70 }
	}
	option = {
		name = cwic_mkultra.405.b
		custom_effect_tooltip = USA_mkultra_gateway_archive_opt_tt
		USA_mkultra_archive_gateway_assessment = yes
		ai_chance = { factor = 30 }
	}
}

# Gateway Expanded Episode: The Assessment Arrived Early (Part I)
country_event = {
	id = cwic_mkultra.420
	title = cwic_mkultra.420.t
	desc = cwic_mkultra.420.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.420.a
		custom_effect_tooltip = USA_mkultra_early_assessment_preparedness_tt
		USA_mkultra_resolve_early_assessment_preparedness = yes
		hidden_effect = {
			country_event = { id = cwic_mkultra.421 days = 120 }
		}
		ai_chance = { factor = 50 }
	}
	option = {
		name = cwic_mkultra.420.b
		custom_effect_tooltip = USA_mkultra_early_assessment_appraisal_tt
		USA_mkultra_resolve_early_assessment_appraisal = yes
		hidden_effect = {
			country_event = { id = cwic_mkultra.421 days = 120 }
		}
		ai_chance = { factor = 40 }
	}
	option = {
		name = cwic_mkultra.420.c
		custom_effect_tooltip = USA_mkultra_early_assessment_archive_tt
		USA_mkultra_resolve_early_assessment_archive = yes
		ai_chance = { factor = 10 }
	}
}

# Gateway Expanded Episode: The Matching Event (Part II)
country_event = {
	id = cwic_mkultra.421
	title = cwic_mkultra.421.t
	desc = cwic_mkultra.421.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.421.a
		if = {
			limit = { has_country_flag = USA_mkultra_early_preparedness }
			add_stability = -0.01
		}
		else_if = {
			limit = { has_country_flag = USA_mkultra_early_appraisal_active }
			add_stability = -0.02
		}
		else = {
			add_stability = -0.03
		}
		hidden_effect = {
			country_event = { id = cwic_mkultra.422 days = 30 }
		}
		ai_chance = { factor = 100 }
	}
}

# Gateway Expanded Episode: The Final Comparison (Part III)
country_event = {
	id = cwic_mkultra.422
	title = cwic_mkultra.422.t
	desc = cwic_mkultra.422.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.422.a
		custom_effect_tooltip = USA_mkultra_early_assessment_comparison_tt
		USA_mkultra_resolve_early_assessment_comparison = yes
		ai_chance = { factor = 100 }
	}
}

# 1995 AIR Utility Review
country_event = {
	id = cwic_mkultra.440
	title = cwic_mkultra.440.t
	desc = cwic_mkultra.440.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.440.a
		custom_effect_tooltip = USA_mkultra_air_decommission_tt
		USA_mkultra_resolve_air_review_decommission = yes
		ai_chance = { factor = 80 }
	}
	option = {
		name = cwic_mkultra.440.b
		custom_effect_tooltip = USA_mkultra_air_seal_tt
		USA_mkultra_resolve_air_review_seal = yes
		ai_chance = { factor = 20 }
	}
}

# Cultural Afterlife: A File Outside Its Setting
country_event = {
	id = cwic_mkultra.460
	title = cwic_mkultra.460.t
	desc = cwic_mkultra.460.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.460.a
		custom_effect_tooltip = USA_mkultra_cultural_deny_tt
		USA_mkultra_resolve_cultural_afterlife_deny = yes
		ai_chance = { factor = 50 }
	}
	option = {
		name = cwic_mkultra.460.b
		custom_effect_tooltip = USA_mkultra_cultural_foia_tt
		USA_mkultra_resolve_cultural_afterlife_foia = yes
		ai_chance = { factor = 50 }
	}
}

# 1999 Y2K Epilogue: The Last Machine in the Records Room
country_event = {
	id = cwic_mkultra.500
	title = cwic_mkultra.500.t
	desc = cwic_mkultra.500.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.500.a
		custom_effect_tooltip = USA_mkultra_y2k_epilogue_tt
		USA_mkultra_resolve_y2k_epilogue = yes
		ai_chance = { factor = 100 }
	}
}
"""

with open(path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text + new_events)

print("USA_MKUltra_events.txt updated successfully!")
