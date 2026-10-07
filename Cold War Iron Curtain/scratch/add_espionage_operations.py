import os

repo_dir = r"c:\Users\New\Documents\Paradox Interactive\Hearts of Iron IV\mod\CWIC Dev\Cold War Iron Curtain"
ops_file = os.path.join(repo_dir, "common", "operations", "CWIC_cold_war_operations.txt")
loc_file = os.path.join(repo_dir, "localisation", "english", "CWIC_operations_l_english.yml")

new_operations = """
# 5. Targeted Assassination: Military Commander
operation_assassinate_commander = {
	icon = GFX_operations_infiltrate_armed_forces_army
	map_icon = GFX_operations_infiltrate_armed_forces_army_map
	name = operation_assassinate_commander
	desc = operation_assassinate_commander_desc
	priority = 23

	cost_multiplier = 0.5
	days = 90
	network_strength = 50
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	requirements = {
		FROM = {
			NOT = { is_in_faction_with = ROOT }
			NOT = { is_subject_of = ROOT }
		}
	}

	equipment = {
		infantry_equipment = 200
		support_equipment = 50
	}

	required_tokens = {
		token_army
	}

	risk_chance = 0.25
	experience = 2.5
	outcome_extra_chance = 0.35
	outcome_modifiers = { operation_outcome }
	risk_modifiers = { operation_risk }
	cost_modifiers = { operation_cost }

	outcome_execute = {
		FROM = {
			add_stability = -0.05
			add_command_power = -25
			if = {
				limit = {
					any_army_leader = {
						is_field_marshal = no
					}
				}
				random_army_leader = {
					limit = {
						is_field_marshal = no
					}
					retire = yes
				}
			}
			else_if = {
				limit = {
					any_army_leader = {
						always = yes
					}
				}
				random_army_leader = {
					retire = yes
				}
			}
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 15
			}
			remove_operation_token = {
				tag = FROM
				token = token_army
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Critical success - High Command in disarray
				FROM = {
					add_stability = -0.08
					add_command_power = -45
					if = {
						limit = {
							any_army_leader = {
								is_field_marshal = yes
							}
						}
						random_army_leader = {
							limit = {
								is_field_marshal = yes
							}
							retire = yes
						}
					}
					else_if = {
						limit = {
							any_army_leader = {
								always = yes
							}
						}
						random_army_leader = {
							retire = yes
						}
					}
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 25
					}
				}
			}
			60 = {
				FROM = {
					add_stability = -0.05
					add_command_power = -25
					if = {
						limit = {
							any_army_leader = {
								is_field_marshal = no
							}
						}
						random_army_leader = {
							limit = {
								is_field_marshal = no
							}
							retire = yes
						}
					}
					else_if = {
						limit = {
							any_army_leader = {
								always = yes
							}
						}
						random_army_leader = {
							retire = yes
						}
					}
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 15
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM = {
			add_stability = -0.05
			add_command_power = -25
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 15
			}
		}
	}

	target_weight = {
		base = 50
	}

	phases = { # Infiltration
		infiltration_diplomatic = {
			base = 35
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_border = { base = 35 }
		infiltration_paradrop = {
			base = 30
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
	phases = { # Reconnaissance & Ambush
		coordinated_strike_scout_target = { base = 40 }
		collaboration_government_contact_military_officers = { base = 30 }
		infiltrate_military_bribe = { base = 30 }
	}
	phases = { # Exfiltration
		exfiltration_border = { base = 35 }
		exfiltration_go_to_ground = { base = 35 }
		exfiltration_air_pickup = {
			base = 20
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
		exfiltration_submarine_pickup = { base = 10 }
	}
}

# 6. Targeted Assassination: Naval Commander
operation_assassinate_admiral = {
	icon = GFX_operations_infiltrate_armed_forces_navy
	map_icon = GFX_operations_infiltrate_armed_forces_navy_map
	name = operation_assassinate_admiral
	desc = operation_assassinate_admiral_desc
	priority = 24

	cost_multiplier = 0.5
	days = 90
	network_strength = 50
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	requirements = {
		FROM = {
			NOT = { is_in_faction_with = ROOT }
			NOT = { is_subject_of = ROOT }
			has_navy_size = { size > 0 }
		}
	}

	equipment = {
		support_equipment = 50
	}

	required_tokens = {
		token_navy
	}

	risk_chance = 0.25
	experience = 2.5
	outcome_extra_chance = 0.35
	outcome_modifiers = { operation_outcome }
	risk_modifiers = { operation_risk }
	cost_modifiers = { operation_cost }

	outcome_execute = {
		FROM = {
			add_stability = -0.04
			add_command_power = -25
			if = {
				limit = {
					any_navy_leader = {
						always = yes
					}
				}
				random_navy_leader = {
					retire = yes
				}
			}
		}
		ROOT = {
			add_intel = {
				target = FROM
				navy_intel = 20
			}
			remove_operation_token = {
				tag = FROM
				token = token_navy
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Critical success - Naval staff crippled
				FROM = {
					add_stability = -0.06
					add_command_power = -40
					if = {
						limit = {
							any_navy_leader = {
								always = yes
							}
						}
						random_navy_leader = {
							retire = yes
						}
					}
				}
				ROOT = {
					add_intel = {
						target = FROM
						navy_intel = 30
					}
				}
			}
			60 = {
				FROM = {
					add_stability = -0.04
					add_command_power = -25
					if = {
						limit = {
							any_navy_leader = {
								always = yes
							}
						}
						random_navy_leader = {
							retire = yes
						}
					}
				}
				ROOT = {
					add_intel = {
						target = FROM
						navy_intel = 20
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM = {
			add_stability = -0.04
			add_command_power = -25
		}
		ROOT = {
			add_intel = {
				target = FROM
				navy_intel = 20
			}
		}
	}

	target_weight = {
		base = 45
	}

	phases = { # Infiltration
		infiltration_diplomatic = {
			base = 35
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_submarine = { base = 35 }
		infiltration_border = { base = 30 }
	}
	phases = { # Port Surveillance & Sabotage
		steal_blueprints_infiltrate_naval_design_office = { base = 40 }
		coordinated_strike_scout_target = { base = 35 }
		infiltrate_military_bribe = { base = 25 }
	}
	phases = { # Exfiltration
		exfiltration_submarine_pickup = { base = 35 }
		exfiltration_border = { base = 35 }
		exfiltration_go_to_ground = { base = 30 }
	}
}

# 7. Establish Clandestine Black Site
operation_establish_black_site = {
	icon = GFX_operations_fake_intel
	map_icon = GFX_operations_fake_intel_map
	name = operation_establish_black_site
	desc = operation_establish_black_site_desc
	priority = 25

	cost_multiplier = 0.5
	days = 120
	network_strength = 40
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	requirements = {
		FROM = {
			NOT = { is_in_faction_with = ROOT }
			NOT = { is_subject_of = ROOT }
		}
	}

	equipment = {
		support_equipment = 100
	}

	required_tokens = {
		token_civilian
	}

	risk_chance = 0.20
	experience = 3.0
	outcome_extra_chance = 0.35
	outcome_modifiers = { operation_outcome }
	risk_modifiers = { operation_risk }
	cost_modifiers = { operation_cost }

	outcome_execute = {
		ROOT = {
			add_intel = {
				target = FROM
				civilian_intel = 25
				army_intel = 20
				airforce_intel = 20
				navy_intel = 20
			}
			remove_operation_token = {
				tag = FROM
				token = token_civilian
			}
		}
		FROM = {
			add_stability = -0.04
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			50 = { # Critical success - Deep black site with cipher access
				ROOT = {
					add_intel = {
						target = FROM
						civilian_intel = 40
						army_intel = 35
						airforce_intel = 30
						navy_intel = 30
					}
					capture_ciphers = {
						target = FROM
					}
				}
				FROM = {
					add_stability = -0.08
				}
			}
			50 = {
				ROOT = {
					add_intel = {
						target = FROM
						civilian_intel = 25
						army_intel = 20
						airforce_intel = 20
						navy_intel = 20
					}
				}
				FROM = {
					add_stability = -0.04
				}
			}
		}
	}

	outcome_potential = {
		ROOT = {
			add_intel = {
				target = FROM
				civilian_intel = 25
				army_intel = 20
				airforce_intel = 20
				navy_intel = 20
			}
		}
		FROM = {
			add_stability = -0.04
		}
	}

	target_weight = {
		base = 55
	}

	phases = { # Infiltration
		infiltration_diplomatic = {
			base = 40
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_border = { base = 35 }
		infiltration_submarine = { base = 25 }
	}
	phases = { # Facility Construction & Commercial Cover
		collaboration_government_set_up_planning_committees = { base = 40 }
		steal_blueprints_middle_manager = { base = 35 }
		fake_intel_plant_evidence = { base = 25 }
	}
	phases = { # Network Securement
		exfiltration_go_to_ground = { base = 40 }
		exfiltration_border = { base = 35 }
		exfiltration_air_pickup = {
			base = 25
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
}

# 8. Sabotage Military Production Complex
operation_sabotage_military_production = {
	icon = GFX_operations_targeted_sabotage
	map_icon = GFX_operations_targeted_sabotage_map
	name = operation_sabotage_military_production
	desc = operation_sabotage_military_production_desc
	priority = 26

	cost_multiplier = 0.35
	days = 80
	network_strength = 45
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		arms_factory > 0
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				arms_factory > 0
			}
		}
	}

	equipment = {
		infantry_equipment = 100
		support_equipment = 75
	}

	required_tokens = {
		token_civilian
	}

	risk_chance = 0.20
	experience = 2.0
	outcome_extra_chance = 0.30
	outcome_modifiers = { target_sabotage_factor operation_outcome }
	risk_modifiers = { target_sabotage_risk operation_risk }
	cost_modifiers = { target_sabotage_cost operation_cost }

	outcome_execute = {
		FROM.FROM = {
			damage_building = {
				type = arms_factory
				damage = 2
			}
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 10
			}
			remove_operation_token = {
				tag = FROM
				token = token_civilian
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Critical industrial devastation
				FROM.FROM = {
					damage_building = {
						type = arms_factory
						damage = 4
					}
				}
				FROM = {
					add_stability = -0.06
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 20
					}
				}
			}
			60 = {
				FROM.FROM = {
					damage_building = {
						type = arms_factory
						damage = 2
					}
				}
				FROM = {
					add_stability = -0.03
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 10
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			damage_building = {
				type = arms_factory
				damage = 2
			}
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 10
			}
		}
	}

	target_weight = {
		base = 50
	}

	phases = { # Infiltration
		infiltration_border = { base = 35 }
		infiltration_diplomatic = {
			base = 35
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_submarine = { base = 30 }
	}
	phases = { # Industrial Plant Sabotage
		targeted_sabotage_plant_explosives = { base = 40 }
		steal_blueprints_middle_manager = { base = 30 }
		targeted_sabotage_burn_storage = { base = 30 }
	}
	phases = { # Exfiltration
		exfiltration_border = { base = 35 }
		exfiltration_go_to_ground = { base = 35 }
		exfiltration_air_pickup = {
			base = 20
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
		exfiltration_submarine_pickup = { base = 10 }
	}
}

# 9. Sabotage Military Airfield
operation_sabotage_airfields = {
	icon = GFX_operations_infiltrate_armed_forces_airforce
	map_icon = GFX_operations_infiltrate_armed_forces_airforce_map
	name = operation_sabotage_airfields
	desc = operation_sabotage_airfields_desc
	priority = 27

	cost_multiplier = 0.35
	days = 75
	network_strength = 40
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		air_base > 0
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				air_base > 0
			}
		}
	}

	equipment = {
		support_equipment = 75
	}

	required_tokens = {
		token_airforce
	}

	risk_chance = 0.20
	experience = 2.0
	outcome_extra_chance = 0.30
	outcome_modifiers = { target_sabotage_factor operation_outcome }
	risk_modifiers = { target_sabotage_risk operation_risk }
	cost_modifiers = { target_sabotage_cost operation_cost }

	outcome_execute = {
		FROM.FROM = {
			damage_building = {
				type = air_base
				damage = 3
			}
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				airforce_intel = 15
			}
			remove_operation_token = {
				tag = FROM
				token = token_airforce
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Runway and hangar firestorm
				FROM.FROM = {
					damage_building = {
						type = air_base
						damage = 6
					}
				}
				FROM = {
					add_stability = -0.05
				}
				ROOT = {
					add_intel = {
						target = FROM
						airforce_intel = 30
					}
				}
			}
			60 = {
				FROM.FROM = {
					damage_building = {
						type = air_base
						damage = 3
					}
				}
				FROM = {
					add_stability = -0.03
				}
				ROOT = {
					add_intel = {
						target = FROM
						airforce_intel = 15
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			damage_building = {
				type = air_base
				damage = 3
			}
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				airforce_intel = 15
			}
		}
	}

	target_weight = {
		base = 45
	}

	phases = { # Infiltration
		infiltration_border = { base = 35 }
		infiltration_diplomatic = {
			base = 35
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_paradrop = {
			base = 30
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
	phases = { # Airfield Infiltration & Demolition
		targeted_sabotage_plant_explosives = { base = 40 }
		targeted_sabotage_burn_storage = { base = 35 }
		coordinate_strike_mark_targets = { base = 25 }
	}
	phases = { # Exfiltration
		exfiltration_border = { base = 35 }
		exfiltration_go_to_ground = { base = 35 }
		exfiltration_air_pickup = {
			base = 20
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
		exfiltration_submarine_pickup = { base = 10 }
	}
}

# 10. Sabotage Naval Facilities & Dockyards
operation_sabotage_naval_facilities = {
	icon = GFX_operations_infiltrate_armed_forces_navy
	map_icon = GFX_operations_infiltrate_armed_forces_navy_map
	name = operation_sabotage_naval_facilities
	desc = operation_sabotage_naval_facilities_desc
	priority = 28

	cost_multiplier = 0.35
	days = 80
	network_strength = 45
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		OR = {
			naval_base > 0
			dockyard > 0
		}
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				OR = {
					naval_base > 0
					dockyard > 0
				}
			}
		}
	}

	equipment = {
		support_equipment = 75
	}

	required_tokens = {
		token_navy
	}

	risk_chance = 0.20
	experience = 2.0
	outcome_extra_chance = 0.30
	outcome_modifiers = { target_sabotage_factor operation_outcome }
	risk_modifiers = { target_sabotage_risk operation_risk }
	cost_modifiers = { target_sabotage_cost operation_cost }

	outcome_execute = {
		FROM.FROM = {
			if = {
				limit = { naval_base > 0 }
				damage_building = {
					type = naval_base
					damage = 2
				}
			}
			if = {
				limit = { dockyard > 0 }
				damage_building = {
					type = dockyard
					damage = 2
				}
			}
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				navy_intel = 15
			}
			remove_operation_token = {
				tag = FROM
				token = token_navy
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Harbor installations destroyed
				FROM.FROM = {
					if = {
						limit = { naval_base > 0 }
						damage_building = {
							type = naval_base
							damage = 4
						}
					}
					if = {
						limit = { dockyard > 0 }
						damage_building = {
							type = dockyard
							damage = 4
						}
					}
				}
				FROM = {
					add_stability = -0.06
				}
				ROOT = {
					add_intel = {
						target = FROM
						navy_intel = 25
					}
				}
			}
			60 = {
				FROM.FROM = {
					if = {
						limit = { naval_base > 0 }
						damage_building = {
							type = naval_base
							damage = 2
						}
					}
					if = {
						limit = { dockyard > 0 }
						damage_building = {
							type = dockyard
							damage = 2
						}
					}
				}
				FROM = {
					add_stability = -0.03
				}
				ROOT = {
					add_intel = {
						target = FROM
						navy_intel = 15
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			custom_effect_tooltip = operation_sabotage_naval_facilities_potential_tt
		}
		FROM = {
			add_stability = -0.03
		}
		ROOT = {
			add_intel = {
				target = FROM
				navy_intel = 15
			}
		}
	}

	target_weight = {
		base = 45
	}

	phases = { # Infiltration
		infiltration_submarine = { base = 40 }
		infiltration_diplomatic = {
			base = 30
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_border = { base = 30 }
	}
	phases = { # Dockyard Infiltration & Limpet Charges
		steal_blueprints_infiltrate_naval_design_office = { base = 40 }
		targeted_sabotage_plant_explosives = { base = 35 }
		targeted_sabotage_burn_storage = { base = 25 }
	}
	phases = { # Exfiltration
		exfiltration_submarine_pickup = { base = 40 }
		exfiltration_border = { base = 30 }
		exfiltration_go_to_ground = { base = 30 }
	}
}

# 11. Sabotage Rail & Logistics Network
operation_sabotage_logistics_rail = {
	icon = GFX_operations_targeted_sabotage
	map_icon = GFX_operations_targeted_sabotage_map
	name = operation_sabotage_logistics_rail
	desc = operation_sabotage_logistics_rail_desc
	priority = 29

	cost_multiplier = 0.25
	days = 60
	network_strength = 35
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		NOT = { FROM = { tag = ROOT } }
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		OR = {
			infrastructure > 0
			supply_node > 0
		}
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				OR = {
					infrastructure > 0
					supply_node > 0
				}
			}
		}
	}

	equipment = {
		infantry_equipment = 50
		support_equipment = 50
	}

	required_tokens = {
		token_army
	}

	risk_chance = 0.20
	experience = 1.5
	outcome_extra_chance = 0.30
	outcome_modifiers = { target_sabotage_factor operation_outcome }
	risk_modifiers = { target_sabotage_risk operation_risk }
	cost_modifiers = { target_sabotage_cost operation_cost }

	outcome_execute = {
		FROM.FROM = {
			damage_building = {
				type = infrastructure
				damage = 2
			}
			if = {
				limit = { supply_node > 0 }
				damage_building = {
					type = supply_node
					damage = 1
				}
			}
		}
		FROM = {
			add_stability = -0.02
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 10
			}
			remove_operation_token = {
				tag = FROM
				token = token_army
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Critical rail bottleneck collapse
				FROM.FROM = {
					damage_building = {
						type = infrastructure
						damage = 4
					}
					if = {
						limit = { supply_node > 0 }
						damage_building = {
							type = supply_node
							damage = 2
						}
					}
				}
				FROM = {
					add_stability = -0.04
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 20
					}
				}
			}
			60 = {
				FROM.FROM = {
					damage_building = {
						type = infrastructure
						damage = 2
					}
					if = {
						limit = { supply_node > 0 }
						damage_building = {
							type = supply_node
							damage = 1
						}
					}
				}
				FROM = {
					add_stability = -0.02
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 10
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			damage_building = {
				type = infrastructure
				damage = 2
			}
		}
		FROM = {
			add_stability = -0.02
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 10
			}
		}
	}

	target_weight = {
		base = 45
	}

	phases = { # Infiltration
		infiltration_border = { base = 40 }
		infiltration_diplomatic = {
			base = 30
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_paradrop = {
			base = 30
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
	phases = { # Railway Demolition
		targeted_sabotage_destroy_bridge = { base = 40 }
		targeted_sabotage_plant_explosives = { base = 35 }
		targeted_sabotage_immobilize_rolling_stock = { base = 25 }
	}
	phases = { # Exfiltration
		exfiltration_border = { base = 40 }
		exfiltration_go_to_ground = { base = 40 }
		exfiltration_air_pickup = {
			base = 20
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
}

# 12. Embed Guerrilla Warfare Advisors
operation_embed_advisors = {
	icon = GFX_operations_boost_resistance
	map_icon = GFX_operations_boost_resistance_map
	name = operation_embed_advisors
	desc = operation_embed_advisors_desc
	priority = 30

	cost_multiplier = 0.35
	days = 90
	network_strength = 45
	operatives = 2

	visible = {
		num_of_operatives > 1
		network_national_coverage = {
			target = FROM
			value > 0
		}
		has_operation_token = {
			tag = FROM
			token = token_resistance_contacts
		}
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		has_resistance = yes
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				has_resistance = yes
			}
		}
	}

	equipment = {
		infantry_equipment = 800
		support_equipment = 100
	}

	required_tokens = {
		token_resistance_contacts
	}

	risk_chance = 0.20
	experience = 2.5
	outcome_extra_chance = 0.35
	outcome_modifiers = { boost_resistance_factor operation_outcome }
	risk_modifiers = { operation_risk }
	cost_modifiers = { operation_cost }

	outcome_execute = {
		FROM.FROM = {
			add_resistance_target = {
				amount = 25
				tooltip = intelligency_agency_resistance_boost_tt
			}
			add_compliance = -15
		}
		FROM = {
			add_stability = -0.05
		}
		ROOT = {
			add_intel = {
				target = FROM
				army_intel = 15
			}
			remove_operation_token = {
				tag = FROM
				token = token_resistance_contacts
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Guerrilla Stronghold entrenched
				FROM.FROM = {
					add_resistance_target = {
						amount = 40
						tooltip = intelligency_agency_resistance_boost_tt
					}
					add_compliance = -25
				}
				FROM = {
					add_stability = -0.08
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 25
					}
				}
			}
			60 = {
				FROM.FROM = {
					add_resistance_target = {
						amount = 25
						tooltip = intelligency_agency_resistance_boost_tt
					}
					add_compliance = -15
				}
				FROM = {
					add_stability = -0.05
				}
				ROOT = {
					add_intel = {
						target = FROM
						army_intel = 15
					}
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			add_resistance_target = {
				amount = 25
				tooltip = intelligency_agency_resistance_boost_tt
			}
			add_compliance = -15
		}
		FROM = {
			add_stability = -0.05
		}
	}

	target_weight = {
		base = 50
	}

	phases = { # Infiltration
		infiltration_border = { base = 35 }
		infiltration_paradrop = {
			base = 35
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
		infiltration_diplomatic = {
			base = 30
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
	}
	phases = { # Guerilla Training & Organization
		resistance_contacts_briefings = { base = 40 }
		collaboration_government_train_paramilitary_forces = { base = 35 }
		resistance_contacts_radio_circuits = { base = 25 }
	}
	phases = { # Exfiltration
		exfiltration_go_to_ground = { base = 40 }
		exfiltration_border = { base = 35 }
		exfiltration_air_pickup = {
			base = 25
			modifier = {
				ROOT = { has_equipment = { transport_plane_equipment < 1 } }
				factor = 0.1
			}
		}
	}
}

# 13. Counter-Insurgency Security Sweep
operation_counter_insurgency_sweep = {
	icon = GFX_operations_make_resistance_contacts
	map_icon = GFX_operations_make_resistance_contacts_map
	name = operation_counter_insurgency_sweep
	desc = operation_counter_insurgency_sweep_desc
	priority = 31

	cost_multiplier = 0.25
	days = 60
	network_strength = 30
	operatives = 1

	visible = {
		num_of_operatives > 0
		network_national_coverage = {
			target = FROM
			value > 0
		}
	}

	selection_target = {
		targets = { FROM }
	}

	selection_target_state = {
		has_resistance = yes
	}

	requirements = {
		FROM = {
			any_controlled_state = {
				has_resistance = yes
			}
		}
	}

	equipment = {
		infantry_equipment = 400
		support_equipment = 50
	}

	required_tokens = {
		token_civilian
	}

	risk_chance = 0.15
	experience = 2.0
	outcome_extra_chance = 0.35
	outcome_modifiers = { operation_outcome }
	risk_modifiers = { operation_risk }
	cost_modifiers = { operation_cost }

	outcome_execute = {
		FROM.FROM = {
			add_resistance_target = {
				amount = -25
				tooltip = intelligency_agency_resistance_reduction_tt
			}
			add_compliance = 15
		}
		ROOT = {
			remove_operation_token = {
				tag = FROM
				token = token_civilian
			}
		}
	}

	outcome_extra_execute = { # SCOPE_OPERATION
		random_list = {
			40 = { # Decisive liquidation of partisan cells
				FROM.FROM = {
					add_resistance_target = {
						amount = -40
						tooltip = intelligency_agency_resistance_reduction_tt
					}
					add_compliance = 25
				}
			}
			60 = {
				FROM.FROM = {
					add_resistance_target = {
						amount = -25
						tooltip = intelligency_agency_resistance_reduction_tt
					}
					add_compliance = 15
				}
			}
		}
	}

	outcome_potential = {
		FROM.FROM = {
			add_resistance_target = {
				amount = -25
				tooltip = intelligency_agency_resistance_reduction_tt
			}
			add_compliance = 15
		}
	}

	target_weight = {
		base = 60
	}

	phases = { # Security Mobilization
		collaboration_government_set_up_planning_committees = { base = 40 }
		infiltration_diplomatic = {
			base = 35
			modifier = {
				factor = 10
				ROOT = { has_war = no }
				FROM = { has_war = no }
			}
		}
		infiltration_border = { base = 25 }
	}
	phases = { # Intelligence Sweep & Raids
		free_operative_liberate_camp = { base = 40 }
		coordinated_strike_scout_target = { base = 35 }
		fake_intel_utilize_double_agents = { base = 25 }
	}
	phases = { # Consolidation
		exfiltration_go_to_ground = { base = 50 }
		exfiltration_border = { base = 50 }
	}
}
"""

new_loc = """ operation_assassinate_commander:0 "Assassinate Military Commander"
 operation_assassinate_commander_desc:0 "Direct our clandestine field operatives and sniper teams to stalk, ambush, and eliminate a senior military officer in [FROM.GetName], sowing disarray throughout the enemy's chain of command."
 operation_assassinate_admiral:0 "Assassinate Naval Commander"
 operation_assassinate_admiral_desc:0 "Infiltrate naval headquarters and port command facilities in [FROM.GetName] to assassinate a high-ranking fleet admiral, severely disrupting enemy naval operations."
 operation_establish_black_site:0 "Establish Clandestine Black Site"
 operation_establish_black_site_desc:0 "Construct a heavily fortified, off-the-books intelligence outpost and interrogation center within [FROM.GetName] under diplomatic or commercial front cover, granting continuous operational reach."
 operation_sabotage_military_production:0 "Sabotage Military Production Complex"
 operation_sabotage_military_production_desc:0 "Deploy elite demolition operatives to infiltrate defense manufacturing plants in [FROM.GetName], detonating critical machine tooling and assembly lines."
 operation_sabotage_airfields:0 "Sabotage Military Airfield"
 operation_sabotage_airfields_desc:0 "Infiltrate enemy frontline air bases and runways in [FROM.GetName] under cover of darkness to detonate hangars, fuel depots, and parked combat aircraft."
 operation_sabotage_naval_facilities:0 "Sabotage Naval Facilities & Dockyards"
 operation_sabotage_naval_facilities_desc:0 "Deploy combat swimmers and covert sabotage teams into [FROM.GetName]'s naval bases to attach limpet mines to dock facilities and drydock installations."
 operation_sabotage_naval_facilities_potential_tt:0 "Damages naval bases and dockyards in the target state."
 operation_sabotage_logistics_rail:0 "Sabotage Rail & Logistics Network"
 operation_sabotage_logistics_rail_desc:0 "Clandestine saboteurs plant high-yield plastic explosives along vital railway bottlenecks, switching yards, and bridges in [FROM.GetName] to throttle enemy military supply lines."
 operation_embed_advisors:0 "Embed Guerrilla Warfare Advisors"
 operation_embed_advisors_desc:0 "Clandestinely insert veteran special forces and intelligence advisors into [FROM.GetName] to train, organize, and lead anti-government insurgent factions in asymmetric combat."
 operation_counter_insurgency_sweep:0 "Counter-Insurgency Security Sweep"
 operation_counter_insurgency_sweep_desc:0 "Mobilize intelligence agents and internal security paramilitaries to conduct sweeping raids against underground partisan cells, arresting subversive agitators and crushing local resistance."
 intelligency_agency_resistance_reduction_tt:0 "Counter-Insurgency Operations: $VALUE|=-%0$"
"""

# Append to operations file
with open(ops_file, "r", encoding="utf-8") as f:
    content = f.read()

if "operation_assassinate_commander" not in content:
    content = content.rstrip() + "\n" + new_operations
    with open(ops_file, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print("Appended new operations to", ops_file)
else:
    print("Operations already present in", ops_file)

# Append to localization file (keeping UTF-8 BOM)
with open(loc_file, "rb") as f:
    raw_loc = f.read()

has_bom = raw_loc.startswith(b"\xef\xbb\xbf")
loc_text = raw_loc.decode("utf-8-sig")

if "operation_assassinate_commander" not in loc_text:
    loc_text = loc_text.rstrip() + "\n" + new_loc
    out_bytes = (b"\xef\xbb\xbf" if has_bom else b"") + loc_text.encode("utf-8")
    with open(loc_file, "wb") as f:
        f.write(out_bytes)
    print("Appended new localization to", loc_file)
else:
    print("Localization already present in", loc_file)
