# What is a Prototype Reward?
A prototype reward is a reward that can be acquired when doing prototypes in
a special project. The prototype reward database defines generic rewards
that can be used from the Projects definition (a project can also have inline
prototype rewards).

# Example of prototype reward

```python
token = { # Dynamic token for the reward (i.e. identifier for the reward)

		# Optional
		narrative = {
			# Optional
			# Localization key used for the name of the Project
			# The localization key is localized with the following localization scope objects:
			#    * Country: The country that owns the project.
			name = name_loc_key
			# if name provided, use TAG_name_loc_key if it exists. if not use name_loc_key (where TAG is the tag of the project owner)
			# if localization key TAG_my_reward_token exists, use it
			# else use loc key my_reward_token

			# Optional
			# Localization key used for the long description of the Project
			# The localization key is localized with the following localization scope objects:
			#    * SpecialProjet: The project.
			#    * Character: The scientist assigned to the project.
			#    * State: The state that the facility belongs to.
			#    * Country: The country that owns the project
			desc = desc_loc_key
			# if desc provided, use TAG_desc_loc_key if it exists. if not use desc_loc_key (where TAG is the tag of the project owner)
			# if localization key TAG_my_reward_token_desc exists, use it (!! Note the _desc suffix)
			# else use loc key my_reward_token_desc
		}

		# Optional
		# GFX key of the icon used to illustrate the Project
		icon = GFX_icon
		# if icon provided, use GFX_icon
		# if gfx key GFX_TAG_my_reward_token exists, use it
		# if gfx key GFX_my_reward_token exists, use it
		# else use GFX_PLACEHOLDER_sp_project_picture

		# Optional
		# Determine if the reward can only be obtained once - or several times
		# Default is no
		fire_only_once = yes
		
		# Optional
		# (Min, Max]. Meaning Min value is considered inside the threshold but max is not.
		# In the example below this reward would be triggered when the prototype progress is a value from 0 to and not including 60
		# default is "always eligible"
		threshold = {
			min = 0
			max = 60
		}
		
		# Optional
		# The weight for the probability of the reward being choosen
		# default is set by define NProject::ITERATION_REWARD_DEFAULT_WEIGHT
		# scriptable weight similar to ai_will_do
		# ROOT is the project
		# FROM is the Country
		# var:facility_state is the State where the facility is (ensured to be set in this case)
		# var:facility_province_id is the province ID where the facility is (ensured to be set in this case)
		# var:scientist is the Scientist (ensured to be set in this case)
		weight = {
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
		# Set an allowed trigger for the reward - Defaults to true
		allowed = { original_tag = GER }
		
		# Repeatable - at least 1 mandatory
		option = {
			# Mandatory - must be unique within the same Reward
			token = my_option_token

			# Optional
			# Whether or not this option is the default one when timing out
			# Only 1 option should have default = yes
			# If none has it, the first one is the default one
			default = yes

			# Optional
			narrative = {
				# Optional
				# Localization key used for the name of the Project
				# The localization key is localized with the following localization scope objects:
				#    * Country: The country that owns the project.
				#    * (Nullable) Character: The scientist working on the project, if one exist (effects may miss character).
				#    * (Nullable) State: The state that the scientist is in, if one exist (effects may miss state).
				#    * (Nullable) Project: The project that the option was completed from (effects may miss project).
				name = name_loc_key
				# if name provided, use TAG_name_loc_key if it exists. if not use name_loc_key (where TAG is the tag of the project owner)
				# if localization key TAG_my_option_token exists, use it
				# else use loc key my_option_token
			}

			# Optional
			# Bonus given when a prototype phase ends up with this reward and this option is chosen
			iteration_output = {
				# output content, detailed in special project documentation
				[...]
			}
		}
}

prototype_reward = {
	token = reward2
	
	# Reward can only be received once. Defaults to 'no'
	fire_only_once = yes
	
	threshold = {
		min = 60
		max = 100
	}
	
	iteration_output = {
		# output content, detailed in special project documentation
		[...]
	}
}
```