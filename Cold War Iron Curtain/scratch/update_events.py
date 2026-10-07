events_path = r'c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain\events\USA_MKUltra_events.txt'

with open(events_path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('\r\n', '\n')

new_events = """
# Historical Precursor Brief: Project BLUEBIRD and ARTICHOKE (1950-1951)
country_event = {
	id = cwic_mkultra.101
	title = cwic_mkultra.101.t
	desc = cwic_mkultra.101.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.101.a
	}
}

# 1963-1964 Inspector General Audit: John Earman Report
country_event = {
	id = cwic_mkultra.300
	title = cwic_mkultra.300.t
	desc = cwic_mkultra.300.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.300.a
		custom_effect_tooltip = USA_mkultra_ig_review_mksearch_tt
		USA_mkultra_resolve_ig_review_mksearch = yes
		ai_chance = { factor = 100 }
	}
	option = {
		name = cwic_mkultra.300.b
		trigger = { has_political_power > 14 }
		custom_effect_tooltip = USA_mkultra_ig_review_tighten_tt
		USA_mkultra_resolve_ig_review_tighten = yes
		ai_chance = { factor = 50 }
	}
}

# Expanded Authorization: A Larger Remit (Section 12.3)
country_event = {
	id = cwic_mkultra.310
	title = cwic_mkultra.310.t
	desc = cwic_mkultra.310.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.310.a
	}
}

# January 1973: The Records Disposition Order (Section 10.3)
country_event = {
	id = cwic_mkultra.320
	title = cwic_mkultra.320.t
	desc = cwic_mkultra.320.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.320.a
		trigger = { has_political_power > 9 }
		custom_effect_tooltip = USA_mkultra_records_preserve_tt
		USA_mkultra_resolve_records_preserve = yes
		ai_chance = { factor = 10 }
	}
	option = {
		name = cwic_mkultra.320.b
		trigger = { has_political_power > 14 }
		custom_effect_tooltip = USA_mkultra_records_seal_tt
		USA_mkultra_resolve_records_seal = yes
		ai_chance = { factor = 30 }
	}
	option = {
		name = cwic_mkultra.320.c
		trigger = { has_political_power > 4 }
		custom_effect_tooltip = USA_mkultra_records_destroy_tt
		USA_mkultra_resolve_records_destroy = yes
		ai_chance = { factor = 100 }
	}
	option = {
		name = cwic_mkultra.320.d
		custom_effect_tooltip = USA_mkultra_records_retain_tt
		USA_mkultra_resolve_records_retain = yes
		ai_chance = { factor = 5 }
	}
}

# 1975: Church Committee & Rockefeller Commission
country_event = {
	id = cwic_mkultra.325
	title = cwic_mkultra.325.t
	desc = cwic_mkultra.325.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.325.a
		custom_effect_tooltip = USA_mkultra_church_committee_tt
		USA_mkultra_resolve_church_committee = yes
		ai_chance = { factor = 100 }
	}
}

# August 1977: Senate Hearings — Somebody Kept the Invoice (Section 12.4)
country_event = {
	id = cwic_mkultra.330
	title = cwic_mkultra.330.t
	desc = cwic_mkultra.330.d
	picture = GFX_MKUltra
	is_triggered_only = yes
	fire_only_once = yes

	option = {
		name = cwic_mkultra.330.a
		custom_effect_tooltip = USA_mkultra_senate_hearing_tt
		USA_mkultra_resolve_senate_hearing = yes
		ai_chance = { factor = 100 }
	}
}
"""

text = text + new_events

with open(events_path, 'w', encoding='utf-8', newline='\n') as f:
    f.write(text)

print("USA_MKUltra_events.txt updated successfully!")
