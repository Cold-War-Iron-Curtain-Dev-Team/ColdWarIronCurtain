```


 ## ###  ###  ##  ###  ##  #       ###  ###   ##   ### ###  ##  ### 
#   #  # #   #  #  #  #  # #       #  # #  # #  #    # #   #  #  #  
 #  ###  ##  #     #  #### #       ###  ###  #  #    # ##  #     #  
  # #    #   #  #  #  #  # #       #    #  # #  # #  # #   #  #  #  
##  #    ###  ##  ### #  # ###     #    #  #  ##   ##  ###  ##   #  


#### SPECIAL PROJECT DEFINITION ####

special_project_id = {
	
	# OPTIONAL
	narrative = {
		# OPTIONAL - by default getting it from loc string matching project ID: "special_project_id"
		# Can have TAG_ to make it country-specific automatically (just like with MIOs)
		# The localization key is localized with the following localization scope objects:
		#    * Country: The country that owns the project.
		name = special_project_id


		# (IF APPROPRIATE)
		# OPTIONAL - by default getting it from loc string matching project ID: "special_project_id_desc"
		# Can have TAG_ to make it country-specific automatically (just like with MIOs)
		# The localization key is localized with the following localization scope objects:
		#    * SpecialProjet: The project.
		#    * Country: The country that owns the project
		desc = special_project_id_desc
	}


	# (IF APPROPRIATE)
	# OPTIONAL - By default getting it from GFX matching the project ID: "GFX_special_project_id"
	icon = GFX_special_project_id # Should it be a project icon or the end goal icon?

	# OPTIONAL (if non-existent the project has no other project requirements)
	# Could use a simple system (add parents and project needs ALL of them), or go for a more customizable system like focus tree or MIO traits (parent / any_parent / all_parents)
	special_project_parent = {
		special_project_1
		special_project_2
	}


	# MANDATORY - Type establishes things like in which kind of facility it can be developed, art assets etc.
	special_project_type = nuclear / aircraft (advanced / weapons) / electronics / tank / artillery / rocket / missiles / naval
	
	# OPTIONAL - overrides the one applied by default based on the project type
	blueprint_image = GFX_XXX

	# OPTIONAL - override the one applied by default based on the project type
	facility_model = facility_type_entity



	# OPTIONAL - default "always = yes"
	allowed = {
		# Mainly Country-specific & DLC locks
	}

	# OPTIONAL - default "always = yes"
	visible = {
		# Special Projects progression, unlocked by content, etc.
	}
	
	# OPTIONAL - default "always = yes"
	available = {
		# Extra requirements like resources, tech, focus/dec/event completed, etc.
	}


	# Optional
	prototype_cost = {
		# If resource requirement isn't met then a linear speed penalty will be applied
		resources = {
			steel = INT
			chromium = INT
			...
		}
	}


	# (IF APPROPRIATE)
	# OPTIONAL - Base value from a define/constant - This parameter multiplies the base value.
	# This value could be modified by
		# Country Modifier: game rule, national spirit, character trait...
		# Facility: Assigned scientist trait, supply availability
		# State Modifier: Resource availability, state modifiers
	prototype_time = FLOAT


	# (IF APPROPRIATE)
	# This could act as a modifier multiplying the value of the completion progress granted by each reward
	# This way we have
		# prototype_time: Affects the time it takes from start to finish of a prototype iteration -> How long it takes per iteration
		# complexity: Amount of progress received by each iteration -> Influences how many iterations a project need
	# Alternative: prototype_time affects both progress AND time
	complexity = FLOAT / predefined script enums (simple, medium, complex, very_complex, insane, etc.)
	#Each one has min & max values
	# INITIAL IMPLEMENTATION: MIN & MAX as parameters




	# MANDATORY - Reward granted when project reaches completion.
	project_output = {

		# OPTIONAL - Used to override default name (project ID) when bonuses from output show up in tooltips (equipment bonus, unit bonus, etc.). Can be overriden by "name" in equipment_bonus/unit_bonus
		name = special_project_id_output_<name>

		# Effects triggered when the project is completed.
		effects = {

		### SCOPES ###

		 # THIS = Facility (Could be project instead, if more appropriate) - UP TO DEBATE WHICH SCOPE MAKES MORE SENSE
		 # ROOT / owner = TAG owning the facility
		 # Info held within the facility:
				# State in which the facility is
				# Province in which the facility is (code needs to check this but should be doable)
				# Scientists array (position 0 always means main scientist)
				# Project - with all its data
		
		### COUNTRY EFFECTS
			ROOT = {
				# New equipment variant, maybe with new archetype (super heavy tank, submarine carrier, mega-monstruous artillery etc.)
				create_equipment_variant = {
					# special variant, or new hull
				}

				# New module for designer unlocked, will probably need a custom tooltip for that since it might be a common reward
				unlock_module_tooltip = module_id

				# New building unlocked, will probably need a custom tooltip for that since it might be a common reward
				unlock_building_tooltip = building_id

				add_stability = 0.06
			}


		### SCIENTIST EFFECTS
			# SCOPING TO THE MAIN SCIENTIST - Requires being able to retrieve the project's scientists array (Main scientist should always be in position 0)
			# Syntax just for reference
			main_scientist = {

				# Example of some new scientist-unique effects
				add_scientist_xp = INT

				add_scientist_level = INT

				add_scientist_trait = scientist_trait_id

			}

			# Loops through the scientists arrray in the project and applies effects - Works like other every_X
			# Syntax just for reference
			every_scientist_in_facility = { # Alternative every_scientist_in_project
				limit = {
					# Example of new scientist-unique trigger
					NOT = { has_scientist_level > 4 } # 4 = Expert
				}
				retire = yes
			}

			# Scopes to a random scientist in the project and applies effects
			random_scientist_in_facility = { # Alternative random_scientist_in_project
				limit = {
					# Example of new scientist-unique trigger
					is_main_scientist = no
				}
				add_advisor_role = { ... }
			}


		### STATE EFFECTS
			facility_state = { #Retrieve state from the facility scope
				add_building_construction = {
					type = dockyard
					level = 2
					instant_build = yes
				}
			}



			...
		}

		# Equipment bonuses applied to specified equipment. Works just like ideas.
		equipment_bonus = {
			limit = { ... } # Optional Enable equipment if DLC restricted trigger is true
			# OPTIONAL - will override any other name hooked-in by default (project output name or project ID)
			name = equipment_bonus_name # -> NEW PARAMETER

			equipment_type = {
				< bonuses >
				...
			}
		}

		# (IF APPROPRIATE)
		# To boost units instead of equipment (maybe not needed) - Similar to how we apply bonuses with hidden tech to boost infantry, militia, etc.
		unit_bonus = {

			# OPTIONAL - will override any other name hooked-in by default (project output name or project ID)
			name = unit_bonus_name # -> NEW PARAMETER

			# Using TECH as script reference
			unit_type = {
				< bonuses > 
				...
			}
		}

		# Enable equipment modules. Works just like technologies.
		# OPTIONAL - Will read a list of items inside curly bracers.
		enable_equipment_modules = {
			limit = { ... } # Optional Enable equipment if DLC restricted trigger is true
			tank_medium_howitzer_2
		}

		# For example:
		unit_bonus = {
			name = amazing_unit_bonus_name

			infantry = {
				hills = {
					attack = 0.05 
					movement = 0.1
				}
				mountain = {
					attack = 0.05 
					movement = 0.1
				}
			}
			irregular_infantry = {
				max_organisation = 10
			}
			category_support_battalions = {
				max_strength = 5
				max_organisation = 10
			}
		}
		
		# Enable equipment - Make an equipment available as project reward. Works just like with technology
		# Will read a list of items inside curly bracers.
		enable_equipments = {
			limit = { ... } # Optional Enable equipment if DLC restricted trigger is true
			anti_tank_equipment_3
		}

		# Equipment bonuses & Unit bonuses will use the project's name by default when they show up in tooltips. 
		# Additionally, a project_output can have a "name" parameter that will override default project name.
		# Additionally to the additional, a unit_bonus or equipment_trait can have a "name" parameter that will override everything else.

		### IMPORTANT: Equipment bonuses and Unit bonuses defined here can be tricky to implement in code, code will need to investigate.
		# POTENTIAL SOLUTION: These bonuses defined here could be processed by code and automatically generate the equivalent hidden ideas (equipment bonus) and hidden tech (unit bonus) to act as the actual containers of the bonuses.
		# This way we don't have to create yet another new way of applying bonuses to equipment or units, and CD doesn't have to implement hundreds of new ideas and techs for this purpose.
		# Additional benefit of keeping them here is that then everything will be defined in this file, instead of having to declare those ideas/techs in different files :)

	}


	# REWARDS
	unique_reward_id = {
		
		narrative = {
			# OPTIONAL - by default getting it from loc string matching reward ID: "unique_reward_id"
			# Can have TAG_ to make it country-specific automatically (just like with MIOs)
			# The localization key is localized with the following localization scope objects:
			#    * Country: The country that owns the project.
			name = unique_reward_id


			# (IF APPROPRIATE)
			# OPTIONAL - by default getting it from loc string matching reward ID: "unique_reward_id_desc"
			# Can have TAG_ to make it country-specific automatically (just like with MIOs)
			# The localization key is localized with the following localization scope objects:
			#    * SpecialProjet: The project.
			#    * Character: The scientist assigned to the project.
			#    * State: The state that the facility belongs to.
			#    * Country: The country that owns the project
			desc = unique_reward_id_desc
		}


		# (IF APPROPRIATE)
		# OPTIONAL - By default getting it from GFX matching the reward ID: "GFX_unique_reward_id"
		icon = GFX_unique_reward_id # Should it be related to reward? (hull, module, XP, building...)

		# OPTIONAL - Defaults to no. Allows reward to be triggered more than once.
		fire_only_once = yes/no
		
		# OPTIONAL - When this reward becomes available it will have priority. If several available rewards have this set to true, the reward will be randomly chosen based on weight.
		force_reward_if_available = yes/no

		threshold = {
			min = 35
			max = 75

			weight = {

			}
		}


		# MANDATORY - Percentage % (0-1) - Reward CAN/will be obtained after project completion progress is equals/above this value
		threshold_min = FLOAT #(0-1)

		# (IF APPROPRIATE)
		# This could help filtering out early low-value rewards at the latest stages of the project, to prevent them from taking over more important and useful stuff, if they were not triggered early due to RNG.
		threshold_max = FLOAT #(0-1)

		# Every clickable option the player can choose
		# Potentially every reward will have at least one -> This requires the player to interact with the feature every time they get a reward.
		option = {

			#MANDATORY - Not really an easy way to auto-hook this in
			name = unique_reward_option_a

			# OPTIONAL - AI weights - defaults to 1 and AI should probably fallback to first option if AI is off etc.
			ai_chance = {
				base = 10
			}

			# Effects triggered when the reward is granted.
			effects = {

			### SCOPES ###

			 # THIS = Facility (Could be project instead, if more appropriate) - UP TO DEBATE WHICH SCOPE MAKES MORE SENSE
			 # ROOT / owner = TAG owning the facility
			 # Info held within the facility:
					# State in which the facility is
					# Province in which the facility is (code needs to check this but should be doable)
					# Scientists array (position 0 always means main scientist)
					# Project - with all its data
			
			### COUNTRY EFFECTS
				ROOT = {
					# New equipment variant, maybe with new archetype (super heavy tank, submarine carrier, mega-monstruous artillery etc.)
					create_equipment_variant = {
						# special variant, or new hull
					}

					# New module for designer unlocked, will probably need a custom tooltip for that since it might be a common reward
					unlock_module_tooltip = module_id

					# New building unlocked, will probably need a custom tooltip for that since it might be a common reward
					unlock_building_tooltip = building_id

					add_stability = 0.06
				}


			### SCIENTIST EFFECTS
				# SCOPING TO THE MAIN SCIENTIST - Requires being able to retrieve the project's scientists array (Main scientist should always be in position 0)
				# Syntax just for reference
				main_scientist = {

					# Example of some new scientist-unique effects
					add_scientist_xp = INT

					add_scientist_level = INT

					add_scientist_trait = scientist_trait_id

				}

				# Loops through the scientists arrray in the project and applies effects - Works like other every_X
				# Syntax just for reference
				every_scientist_in_facility = { # Alternative every_scientist_in_project
					limit = {
						# Example of new scientist-unique trigger
						NOT = { has_scientist_level > 4 } # 4 = Expert
					}
					retire = yes
				}

				# Scopes to a random scientist in the project and applies effects
				random_scientist_in_facility = { # Alternative random_scientist_in_project
					limit = {
						# Example of new scientist-unique trigger
						is_main_scientist = no
					}
					add_advisor_role = { ... }
				}


			### STATE EFFECTS
				facility_state = { #Retrieve state from the facility scope
					add_building_construction = {
						type = dockyard
						level = 2
						instant_build = yes
					}
				}


			### PROJECT EFFECTS ###
				# Percentage % - can be negative (final value clamped between 0-1)
				add_project_completion_progress = FLOAT #(0-1) -> Requires FACILITY (maybe project if appropriate) scope, the default scope in here.


				...
			}


			# Equipment bonuses applied to specified equipment. Works just like ideas.
			equipment_bonus = {

				# OPTIONAL - will override any other name hooked-in by default (unique_reward name or project ID)
				name = equipment_bonus_name # -> NEW PARAMETER

				equipment_type = {
					instant = yes #Apply bonuses retroactively to existing variants # -> Might be complex to achieve in code and be discarded
					< bonuses >
					...
				}
			}

			# (IF APPROPRIATE)
			# To boost units instead of equipment (maybe not needed) - Similar to how we apply bonuses with hidden tech to boost infantry, militia, etc.
			unit_bonus = { # -> NEW THING, based on tech

				# OPTIONAL - will override any other name hooked-in by default (unique_reward name or project ID)
				name = unit_bonus_name 

				# Using TECH as script reference
				unit_type = {
					< bonuses > 
					...
				}
			}


			# For example:
			unit_bonus = {
				name = amazing_unit_bonus_name

				infantry = {
					hills = {
						attack = 0.05 
						movement = 0.1
					}
					mountain = {
						attack = 0.05 
						movement = 0.1
					}
				}
				irregular_infantry = {
					max_organisation = 10
				}
				category_support_battalions = {
					max_strength = 5
					max_organisation = 10
				}
			}
			
			# Enable sub units. Works just like technologies.
			# OPTIONAL - Will read a list of items inside curly bracers.
			enable_subunits = {
				limit = { ... } # Optional Enable equipment if DLC restricted trigger is true
				militia
			}

			# Equipment bonuses & Unit bonuses will use the project's name by default when they show up in tooltips. 
			# Additionally, a unique_reward can have a "name" parameter that will override default project name.
			# Additionally to the additional, a unit_bonus or equipment_trait can have a "name" parameter that will override everything else.


			### IMPORTANT: Equipment bonuses and Unit bonuses defined here can be tricky to implement in code, code will need to investigate.
			# POTENTIAL SOLUTION: These bonuses defined here could be processed by code and automatically generate the equivalent hidden ideas (equipment bonus) and hidden tech (unit bonus) to act as the actual containers of the bonuses.
			# This way we don't have to create yet another new way of applying bonuses to equipment or units, and CD doesn't have to implement hundreds of new ideas and techs for this purpose.
			# Additional benefit of keeping them here is that then everything will be defined in this file, instead of having to declare those ideas/techs in different files :)
		}


		option = {
			...
		}

	}

	unique_reward_2 = {

	}

	...


	
}





### PROJECT SPECIALIZATION DEFINITION ### 
# A Facility belongs to one of these specializations
# A Project belongs to one of these specializations or one of the sub_specializations defined in them.

# For projects only AND facilities
special_project_specialization_<name> = {
	
	# Any thematic art assets tied to the specialization

	# MANDATORY - Default blueprint image - (overriden if sub-specialization or the individual project has one defined)
	blueprint_image = GFX_special_project_specialization_<name>_blueprint

	# MANDATORY - Default facility render image - (overriden if sub-specialization or the individual project has one defined)
	facility_model = special_project_specialization_<name>_entity # maybe "_render" instead of "_entity"


	...

	# OPTIONAL
	# For projects only
	special_project_sub_specializations = {

		special_project_specialization_<name>_<sub_specialization 1> = {

			# Overrides to any thematic art assets defined on the special project specialization

			# MANDATORY - Default blueprint image - (overriden if sub-specialization or the individual project has one defined)
			blueprint_image = GFX_special_project_specialization_<name>_<sub_specialization 1>_blueprint

			# MANDATORY - Default facility render image - (overriden if sub-specialization or the individual project has one defined)
			facility_model = special_project_specialization_<name>_<sub_specialization 1>_entity # maybe "_render" instead of "_entity"

		}

		special_project_specialization_<name>_<sub_specialization 2> = {
			...
		}
	}

}

# Example:
special_project_specialization_naval_engineering = {

	# MANDATORY - Default blueprint image - (overriden if sub-specialization or the individual project has one defined)
	blueprint_image = GFX_special_project_specialization_naval_engineering_blueprint

	# MANDATORY - Default facility render image - (overriden if sub-specialization or the individual project has one defined)
	facility_model = special_project_specialization_naval_engineering_entity # maybe "_render" instead of "_entity"

	...

	sub_specializations = {

		naval_engineering_submarine = {

			# OPTIONAL - Overriding blueprint image - (overriden if the individual project has one defined)
			blueprint_image = GFX_special_project_specialization_naval_engineering_submarine_blueprint

			# MANDATORY - Default facility render image - (overriden if the individual project has one defined)
			facility_model = special_project_specialization_naval_engineering_submarine_entity # maybe "_render" instead of "_entity"

			...
		}

		naval_engineering_surface_ship = {
			...
		}
	}
}


### SCIENTIST DEFINITION ###

# Basically a character role - Requires LARGE portrait (civilian or we could add a new type "scientist" if we want to differentiate, only if very easy to implement in code)

scientist = {
	# I don't think we need a special token for this (like advisors have), but this is to be confirmed by code.

	allowed = {
		# Usually DLC and TAG checks
	}

	visible = {
		# triggers
	}

	available = {
		# triggers
	}

	skill_levels = { #If any specialization level is not defined here it will default to 1. This is compatible with creating new specializations in script.
		nuclear_physics_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		aircraft_engineering_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		advanced_electronic_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		land_warfare_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		rockets_and_missiles_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		naval_engineering_level = INT # (1-5 -> Inexperienced / Skilled / Experienced / Expert / Mastermind)
		... 
		<any_existing_spec_levels_not_explicitly_here> = 0 
	}
	# Use in content: Skill levels will boost the speed of a project of the same specialization.

	# New Scientist Traits
	traits = { trait_scientist_1 trait_scientist_2 }
	# Use in content: Traits will mainly boost XP gain for the Scientist in different fields. They can be earned while researching.

	# AI weights. The AI should also consider level and traits when assigning a scientist
	ai_will_do = {
		base = 1

		modifier = {
			factor = 10
			has_ideology = communism
		}
	}

}



### FACILITY BUILDING DEFINITION ###

# IMPORTANT: Facilities need a new province position on the map for all provinces. Need to work with nudger to generate appropriate map files or update existing ones

special_project_facility = {

	icon_frame = INT # New icon for UI required
	
	provincial = yes # Built within a province

	disabled_in_dmz = yes # TBD, probably should not be built in DMZ

	base_cost = INT # Maybe around 20k-30k? - Reference: Supply node = 20k / Nuclear Reactor = 30k
	
	#max_level = 1 # -> This parameter will change (see "building_level_cap" further down)
	
	value = INT # Probably around 30-50? - Mil is 8, civ is 5, nuclear reeactor is 10 (multiplied per level) - Influences the PP cost for state in PC. - Would also influence the damage taken by Strat. Bombing (if it was applicable)
	
	damage_factor = -1 # I believe this should maake the building invulnerable for Strat. Bombing and Land combat, if that is what we want. 

	allied_build = yes # We might need a new parameter here "subject_build = yes" to specify that the building can only be built in subject's territory.
	
	show_on_map = 1 # We want 1 model to show up
	
	has_destroyed_mesh = yes # Lets be honest, we all want this - Not sure if this is applied only for totally destroyed building or just damaged
	
	infrastructure_construction_effect = yes # I guess we want it to be affected by infra in the state

	
	### NEW PARAMETERS ###

	# New bloc to include both provincial and state max capacity, combining the old max_level parameter with a new state_max parameter.
	# Need to discuss with code how this will affect the old max_level, since level is applied in many places, and in terms of cap the cap is applied on the state/province level based on the parameter "provincial = yes/no"
	# Need to discuss with code how this will affect normal buildings
	# Default values being 0? Meaning no limit?
	building_level_cap = { 
		state_max = 1 # Old parameter "max_level" // Building Cap in the State
		province_max = 1 # New Parameter // Building Cap in the Province
	}

	supply_need = yes # BOOL. Default = no // When true, construction of the building can only be started in a province that is connected to the supply network. Building construction can be halted while there is no supply connection. Could be done with slowing down construction later on, but is more complex.

	special_project_specialization = special_project_specialization_<name> # A defined special project specialization. For example: special_project_specialization_naval_engineering

	# Requirements to build the facility in the province
	requirements = {
		#Need to define this a bit more. Example of requirements:
			# is_coastal / naval_base > 0
			# has_resources_in_country = { resource = steel  amount > 0 } # Country scope
			# facility_state = { has_resources_amount = { resource = steel  amount > 0  delivered = yes } } # State scope - Basically a way to scope to the state in which the facility is being built
			# ...
	}

	# Things that might affect building speed (syntax just for reference) - This is definitely TBD material
	construction_speed_modifier = {
		bonus = 0.2
		has_resources_amount = { resource = steel  amount > 0  delivered = yes }
	}

	construction_speed_modifier = {
		bonus = 0.7
		facility_state = { has_resources_in_country = { resource = steel  amount > 0 } # State scope - Basically a way to scope to the state in which the facility is being built
	}

	construction_speed_modifier = {
		bonus = -0.5
		ROOT = { has_country_leader_ideology = monarchism }  # ROOT/owner should allow us to scope to country building the facility
	}

}




###############################

	### OTHER BUILDINGS ###

###############################
```
