# What is a Project ?
Special projects are about researching projects in Facilities to get equipment and other bonuses.
Special projects are divided in several Specializations. Each Specialization has a tree of researchable projects. 
One entry in this DB is one node in those trees.

# Phases of a Project

Researching a Project is divided in several phases.

* Establishing phase : 
will need to go through that phase when start or re-starting a project
will start from beginning of the phase if cancelled in the middle
* Initial research phase : 
will need to go through that phase only once - if project cancelled after it's done, it won't go through it again
if cancelled in the middle, will remember where it was
* Prototyping phase :
will need to go through that phase in several iterations until project is completed - once completed the Project is fully researched
if cancelled in the middle, will remember where it was
	* Complexity :
	How much progress is gained each prototype iteration. Once reaching 100 the prototype phase is completed.

# Example of project

```python
my_project_token = {
	# Mandatory
	# Category of Special Projects containing this project
	specialization = my_specialization_token

	# Optional
	# Trigger evaluated at startup for every countries to fill the pool of potential projects
	# if triggers returns true, an instance of this Project is created for this country
	# scope: country. only tag, original_tag and has_dlc allowed.
	allowed = { ... }

	# Optional
	# Trigger evaluated when displaying the Project
	# if trigger returns false, the project is disabled and greyed-out
	# scope: project. FROM: country
	available = { ... }

	# Optional
	# Trigger evaluated when displaying the Project
	# if trigger returns false, the project is hidden
	# scope: project. FROM: country
	visible = { ... }
	
	# Optional
	# Cost of breakthrough points to start project.
	# Can consist of several breakthrough points from different specializations.
	# If omitted it will default to 0 for the project specialization.
	# Can also add script to modify the value (Country Scope).
	breakthrough_cost = {
		specialization_air = 2
		specialization_nuclear = 1
		specialization_land = {
			base = 1
			modifier = {
				add = -1
				has_tech = improved_medium_tank_chassis
			}
		}
	}

	# for AI and script, a Project is considered enabled if it is both visible and available

	# Optional
	narrative = {
		# Optional
		# Localization key used for the name of the Project
		# The localization key is localized with the following localization scope objects:
		#    * Country: The country that owns the project.
		name = name_loc_key
    	# if name provided, use TAG_name_loc_key if it exists. if not use name_loc_key (where TAG is the tag of the project owner)
    	# if localization key TAG_my_project_token exists, use it
    	# else use loc key my_project_token
	
		# Optional
		# Localization key used for the long description of the Project
		# The localization key is localized with the following localization scope objects:
		#    * SpecialProjet: The project.
		#    * Country: The country that owns the project
		desc = desc_loc_key
    	# if name provided, use TAG_desc_loc_key if it exists. if not use desc_loc_key (where TAG is the tag of the project owner)
    	# if localization key TAG_my_project_token_desc exists, use it (!! Note the _desc suffix)
    	# else use loc key my_project_token_desc
	}
	
	# Optional
	# GFX key of the icon used to illustrate the Project
	icon = GFX_icon
    # if icon provided, use GFX_icon
    # if gfx key GFX_TAG_my_project_token exists, use it
    # if gfx key GFX_my_project_token exists, use it
    # else use GFX_PLACEHOLDER_sp_project_icon
	
	# Optional
	# GFX key of the background texture of the project when it is being researched
	# overrides the one set at Specialization level
	blueprint_image = GFX_generic_tank_blueprint_background
	
	# At least 1 is Mandatory (and not 0)
	# Number of days needed to complete each phase
	# default is 0
	prototype_time = 3

	# Optional
	# Resources drained during basic research & prototyping phases
	# If not enough resources, research speed will be slowed down
	# special project cost is always evaluated AFTER production lines resource cost
	# Oil is not allowed here.
	resource_cost = {
		resources = { steel=5 rubber=12 ... }
	}
	
	# Optional: Defaults to defined default, if set to 0 a log error is produced and complexity is set to default.
	# Amount of progress gained each prototype iteration.
	complexity = 10
	
	# Optional
	# The weight for the probability of the reward being empty
	# default is set by define NProject::DEFAULT_EMPTY_REWARD_WEIGHT
	# scriptable weight similar to ai_will_do
	# ROOT is the project
	# FROM is the Country
	# var:facility_state is the State where the facility is (ensured to be set in this case)
	# var:facility_province_id is the province ID where the facility is (ensured to be set in this case)
	# var:scientist is the Scientist (ensured to be set in this case)
	empty_reward_weight = {
		base = 1.0
		modifier = {
			factor = 42.0
			[...triggers...]
		}
		modifier = {
			add = 12.0
			[...triggers...]
		}
	}

	# Optional
	# AI weight modifier for this project
	# Default value is 1
	# current Project scope - FROM = country
    # For documentation, see examples of ai_will_do throughout the content
	ai_will_do = {
		...
	}
	
	# Optional
	# Project will appear only if all parents are completed
	# use other Projects' token
	special_project_parent = {
		my_other_project_token
		another_project_token
	}
	
	# Optional
	# Bonus given when the Project is fully researched (i.e. at the end of the last Prototyping phase)
	project_output = {
		# output content, detailed below
		[...]
	}
	
	# Optional array
	# Rewards for when one iteration in the prototype phase is completed
	# "Unique rewards" are only reachable by the containing project.
	# Specification for content for a prototype reward can be found in documentation
	# for generic prototype rewards.
	unique_prototype_rewards = {
		# Optional - Repeatable
		# Dynamic token that identifies the reward
		# Same specification as for prototype rewards.
		dynamic_token1 = { ... }
		# Optional - Repeatable
		# Anonymous prototype reward (not accessible except from effects)
		# Same specification inside definition as for all other prototype rewards.
		{ ... }
	}

	# Optional array
	# "Generic rewards" are coming from the prototype reward DB and can be used in several projects
	# (cf. game/common/special_projects/prototype_rewards)
	generic_prototype_rewards = {
		# Repeatable - Any number of generic prototype reward tokens
		generic_prototype_reward_token
	}
}
```

# Example of output

This is the output for either : 
* the project output on completion
* or the prototype rewards when iterating

```python
project_output/iteration_output = {
	# Country effect block
	# scope: country. FROM: project
	country_effects = {
		add_stability = var:FROM.some_variable_at_projet_level
	}

	# Facility State effect block
	# !Warning: if the project is completed via script, there may be no facility and this will be skipped
	# scope: state. FROM: project
	# var:facility_province_id : temporary variable with the province ID of the facility
	facility_state_effects = {
		add_province_modifier  = {
			static_modifiers = { my_modifier }
			province = var:facility_province_id
		}

		# can also run country stuff needing a state input here
		FROM.owner = {
			delete_unit = { state = ROOT }
		}
	}

	# Scientist effect block
	# !Warning: if the project is completed via script, there may be no scientist and this will be skipped
	# scope: character. FROM: project
	scientist_effects = {
		retire = yes
	}

	# Optional array
	# Enable equipment variants - cf. game/common/units/equipment
	enable_equipments = {
		# Optional trigger - only accepts has_dlc
		# Only enabled if limit is empty or returns true
		limit = { ... }
		equipment_variant_token
	}

	# Optional array 
	# Enable equipment modules - cf. game/common/units/equipment/modules
	enable_equipment_modules = {
		# Only enabled if limit is empty or returns true
		limit = { ... }
		module_token ...
	}

	# Optional array
	# Enable sub units (aka battalion) - cf. game/common/units
	enable_subunits = {
		# Only enabled if limit is empty or returns true
		limit = { ... }
		subunit_token ...
	}

	# Optional
	# Sub-unit stat bonus
	sub_unit_bonus = {
		# same format as in technology
		cavalry = {
			soft_attack = 0.05
			hard_attack = 0.05
		}
		motorized = {
			soft_attack = 0.05
		}
	}

	# Optional
	# Equipment bonus
	equipment_bonus = {
		# same format as equipment_bonus in ideas
		armor = {
			armor_value = 3
			soft_attack = 3
		}
		ship_hull_light = {
			build_cost_ic = -0.05
		}
		# Optional to apply to already existing variants
		# default is no - i.e. bonus will apply only to variants created after getting the bonus
		instant = yes
	}
}
```
