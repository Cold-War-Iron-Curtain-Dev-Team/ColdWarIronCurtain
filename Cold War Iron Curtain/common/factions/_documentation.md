# Abbreviations

- *FI* - Faction Initiative

# Faction Goals
```
faction_goal_id = {

	name = [...] # Goal name (Loc Environment = faction + player country)
	description = [...] # Goal description (Loc Environment = faction + player country)
	category = [...] # Goal's category (short_term, medium_term or long_term)
	visible = {
		# Trigger - checks if goal will show up in selection list
		# SCOPE = ROOT = faction leader: COUNTRY / FROM = faction member: COUNTRY
	}
	available = {
		# Trigger - checks if goal will be selectable in selection list
		# SCOPE = ROOT = faction leader: COUNTRY / FROM = faction member: COUNTRY
	}
	completed = {
		# Trigger - checks if goal completion condition is fulfilled
		# NOTE if empty - the goal is never completed!
		#
		# SCOPE = faction leader: COUNTRY
	}

	group = # a categorization used by the UI to allow for filtering. UI asset will be GFX_group and the localization string will be group_FACTION_GOAL_FILTER
	
	auto_complete = yes # automatically complete goal if the progress reaches 100%
	
	ai_will_do = { #how likely the faction leader AI is to select this goal if there is a free slot
		factor = 200 
		# SCOPE = faction member: COUNTRY
	}

	complete_effect = {
		# Effect - runs once when the goal is completed
		#
		# SCOPE = faction leader: COUNTRY
	}
	
	cancel = {
		# Trigger - checks if goal should be removed from faction
		#
		# SCOPE = faction leader: COUNTRY
	}

	cancel_effect = {
		# Effect - runs once if the goal is canceled
		#
		# SCOPE = faction leader: COUNTRY
	}

	select_effect = {
		# Effect - runs once if the goal is selected, only runs if the goal is selected after game start
		#
		# SCOPE = faction leader: COUNTRY
	}
	remove_effect = {
		# Effect - runs once if the goal is removed, only runs if the goal is removed after game start
		#
		# SCOPE = faction leader: COUNTRY
	}

	# NOTE the following block is optional - for continuous goals only!
	progress = {
		# we can mark dfifferent sections of the progress give effects like modifiers to different areas of the progress
		# by doing: 
		#progress_sections = {
		#  this can hold as many sections as you want and works dynamically
		#  so you would create a new section by doing:
		#  	SectionNameLoc = {
		#  	Min = The start of the section ex 0.1 means that once 10% has been hit this section is active
		#  	Max = the end of the section ex. 0.5 means that once 50% has been passed we have leave this section 
		#  	So if Section1 has Max 0.5 and Section2 Min 0.5 both will be active
		#	
		#	Modifier = this holds a modifier that is applied when this section is in effect
		#	Rule = This holds a new rule that is applied when this section is in effect
		#	on_activate = is disabled for faction goals
		#   on_deactivate = is disabled for faction goals
		#	}
		# 
		#}
	}

	ratio_progress = {
		# Is an extended version of progress
		# The current progress value of a continuous goal is defined as the size of "completed_amount_collection"
		# divided by the size of "completed_amount_collection"
		#
		# NOTE scripted collections are defined in "common/collections"
		#
		# For example:
		#    total_amount_collection = game:all_countries # all countries in the game
		#    completed_amount_collection = democratic_countries # countries with democratic government
		#
		# In the example above, the progress is defined as a ratio between the number of democratic countries in the world
		# and the total number of countries in the world, the progress will be 100% if all countries become democratic and
		# it will be 0% if none of the countries is democratic.
		#
		# For both collections: SCOPE = faction leader: COUNTRY
		#
		total_amount_collection = collection_id
		completed_amount_collection = collection_id
		
		# Alternatively, both total amount and completed amount can be fixed values or variables:
		total_amount = MY_VALUE
		completed_amount = MY_OTHER_VALUE
		
		# NOTE
		#  - 'total_amount' and 'total_amount_collection' are mutially exclusive!
		#  - 'completed_amount' and 'completed_amount_collection' are mutially exclusive!

		Optional - defines how the ratio calculated above is mapped to the goal progress
		#
		# For example:
		#
		#    range = { max = 0.75 }
		#
		# Means that the goal progress is set to 100% when the ratio is equal to 0.75 or more
		#
		# Another example:
		#
		#    range = { min = 0.1 max = 0.8 }
		#
		# Means that:
		#  - the goal progress is set to 0% when the ratio is less or equal to 0.1
		#  - the goal progress is set to 100% when the ratio is more or equal to 0.8
		#
		# NOTES:
		#  - both min and max are optional, by default min = 0, max = 1
		#  - min can actually be greater than max, in which case the progress will increase as the ratio decreases and vice versa
		#
		# range = { min = X max = Y }
	}
}
```

# Faction Rules
```
faction_rule_id = {

	# Type of the rule
	#  - tells in which situation the rule is applicable
	#  - determines which scope will be used when the rule trigger is called
	#
	# Can be an arbitrary token. However, there are several tokens that have a special meaning:
	#
	#    joining_rule - checks whether a country can join the faction
	#        SCOPE = joining country: COUNTRY
	#        FROM = faction leader: COUNTRY
	#
	#    war_declaration_rule - checks who can declare wars
	#        SCOPE = country declaring the war: COUNTRY
	#        FROM = target country: COUNTRY
	#	
	#	 call_to_war_rule - checks who can call to war
	#         SCOPE = country calling to the war: COUNTRY
	#         FROM = target country: COUNTRY
	#
	#    member_rules - checks whether a member can become government in exile
	#        SCOPE = faction leader: COUNTRY
	#
	#	 change_leader_rules - checks which country can become the faction leader
	#	 	 SCOPE = country that becomes the faction leader: COUNTRY
	#
	#    peace_conference_rules - is supposed to contain a list of peace_action_modifiers to apply during a peace conferences
	#
	# Rule name is localized with Country and Faction environment
	#
	type = type_token
	

	visible = {
		# Whether the rule should show up in the list
		#
		# SCOPE = faction leader: COUNTRY
	}

	available = {
		# Whether the rule should be available for the faction
		# NOTE that this won't block the rule from being set with an effect!
		#
		# SCOPE = faction leader: COUNTRY
	}

	can_remove = {
		# Whether the rule can be removed, if currently active
		# NOTE that this won't block the rule from being removed with an effect!
		#
		# SCOPE = faction leader: COUNTRY
	}

	trigger = {
		# NOTE : Scope depends on the type of the faction, see above!
	}

	modifier = {
		# Any modifiers that come from having this rule active
	}

	# A reference to a peace action modifier to apply during peace conferences
	# Peace action modifiers can be found in "common/peace_conference/cost_modifiers"
	# NOTE #1 : only applies when type = peace_conference_rules
	# NOTE #2 : enable trigger will not run for the modifier - the modifier is enabled as long as the rule is active!
	peace_action_modifiers = {
		# List of modifiers in this group
	}

	
	ai_will_do = {
		# AI weight modifier for this rule
		# If <= 0, the AI will not use the rule
		#
		# SCOPE = faction leader: COUNTRY
	}
}
```

# Faction Rule Groups
```
group_id = {
	default_rule = rule_token # The default rule to be set
	rules = {
		# List of rules in this group
		# NOTE : Can be a DB reference or an inline definition
	}
}
```

# Faction Templates
```
faction_template_id = {

	name = [...] # Faction name
	
	visible = {
		# Checks if template shows up when a new faction is created by a country
		# If empty - the template won't show up (this allows, for example, to make faction templates that can only be created from script)
		# 
		# SCOPE = country creating a faction : COUNTRY
	}
	
	available = {
		# Checks if template should be available to choose when a new faction is created by a country
		# If empty - the template is always available (given that it is also visible)
		#
		# SCOPE = country creating a faction : COUNTRY
	}

    can_leader_join_other_factions = yes
	# a setting that allows this faction leader to join another faction
	# if the faction leader leaves it destroys the existing faction and invite
	# all the other faction members that are able to join to the new faction 

	manifest = faction_goal_id # Main goal (faction manifest)

	goals = {
		# List of initial goals of the faction
		# NOTE : Can be a DB reference or an inline definition
	}

	default_rules = {
		# List of rules to be set by default
		# This overrides default rules defined in rule groups
	}
}
```

# Triggers and Effects

### List of faction-related effects
- *create_faction* - creates a faction without a template (OBSOLETE)
- *create_faction_from_template* - the new fancy way of creating factions
- *dismantle_faction* - dismantles faction
- *set_faction_leader* - changes faction's leader
- *set_faction_spymaster* - changes faction's spymaster
- *set_faction_name* - changes faction's name
- *add_to_faction* - adds a country to a faction
- *remove_from_faction* - removes a country from a faction
- *leave_faction* - removes the current country from faction
- *set_faction_rule* - sets a rule on a faction
- *set_faction_manifest* - changes faction's manifest (main goal)
- *add_faction_goal* - adds a goal to a faction
- *remove_faction_goal* - removes a goal from a faction
- *add_faction_initiative* - adds FI to faction
- *add_faction_power_projection* - adds power to the faction
- *add_faction_influence_score* - adds influence to the country in the faction
- *add_faction_influence_ratio* - adds influence to the country based on the given ratio of the faction's total influence


### List of faction-related triggers
- *faction_manifest_fulfillment* - compares the current country faction's manifest fulfillmens to a value
- *has_faction_template* - checks if the current country is in a faction created from a template
- *faction_power_projection* - compares the current country faction's power to a value
- *faction_influence_score* - checks influence value of current country in the faction
- *faction_influence_ratio* - checks influence ratio of current country in the faction
- *faction_influence_rank* - checks influence rank in the faction of the current country
- *has_faction_goal* - checks if the current country's faction has an active or completed goal
- *has_completed_faction_goal* - checks if the current country's faction has completed a goal
- *faction_goal_fulfillment* - checks goal fulfillment for the current country's faction
- *has_manpower_to_become_leader* - checks if the current country exceeds the current faction leader and its subjects in deployed manpower
- *has_industry_to_become_leader* - checks if the current country exceeds the faction leader in number of factories

### List of faction-related modifiers
- *faction_influence_war_score_factor* - war score modifier for faction influence
- *faction_influence_industrial_capacity_factor* - industrial capacity modifier for faction influence
- *faction_influence_garrison_support_provider_factor* - garrison support provider modifier for faction influence
- *faction_influence_garrison_support_reciver_factor* - garrison support reciver modifier for faction influence
- *faction_influence_expeditionary_force_provider_factor* - expeditionary force provider modifier for faction influence
- *faction_influence_expeditionary_force_reciver_factor* -  expeditionary force reciver modifier for faction influence

# Defines

### NFactions
- *FACTION_INITIATIVE_CHANGE_RULE_COST* - cost of changing a faction rule in FI

# Console Commands

- *faction_initiative X* - adds X faction initiative (FI) points to current player's faction (shortcut: "fi X")

# Faction Member Upgrades
Faction_Member_Upgrade_Id = {
	name = the localization string key for the screen name while active. will override the group's name
	desc = the localization string key for the screen description while active. will override the group's desc
	icon = the icon that will be displayed while active. will override the group's icon
	upgrade_cost = the amount of faction initiative that it cost to replace this upgrade with another
	bonus = a numerical value to dictate the boost the country gets based on the type of upgrade
}

# Faction Member Upgrade Group
Faction_Upgrade_Group_Id = {
	name = the default localization string key for the screen name
	desc = the default localization string key for the screen description
	icon = the default icon that will be displayed 
	upgrades = {
		the faction upgrades within this group, this list will be sorted on their bonus
	}

   ### List of faction-member-upgrade-types, that have code support
	faction_member_upgrade_manpower = bonus will be the % that you take from your own countries manpower and put into the faction manpower pool
}

# AI Faction Initiative Spending

AI spending of faction initiative can be affected by AI strategies like such:
```
default_add_faction_facility = {
	enable = {
		always = yes
	}
	abort_when_not_enabled = yes
	ai_strategy = {
		type = spent_faction_initiative_priority
		id = program # <---- This specifies what to spend the Faction Initiative on
		value = 5
	}
}
```
Valid ids are:
```
program
unlock_doctrine_sharing
unlock_faction_commander
```

Intel Advisors work a bit differently, and use custom AI strategy types, e.g:
```
default_become_spymaster_minor = {
	allowed = {
		has_dlc = "La Resistance"
	}
	enable = {
		is_major = no
	}
	abort_when_not_enabled = yes
	ai_strategy = {
		type = become_spymaster
		value = 2
	}
}
```
Valid types are:
```
become_spymaster
become_head_of_crypto
become_head_of_counter_intel
become_head_of_operations
```
Faction Rules initiative spending priority are scripted in the faction rules themselves (ai_will_do)