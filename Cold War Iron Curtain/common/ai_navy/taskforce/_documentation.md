# Taskforce composition

## Introduction

Script the amount of ships for a specific taskforce and its possible available missions (Currently only limited to 1)

## Scripting

```
generic_taskforce_1 = {
	allowed = {
		original_tag = ENG
	}
	ai_will_do = {
		# AI weight modifier for this template
		# If <= 0, the AI will not use this template
		#
		# SCOPE = COUNTRY
		factor = 1
	}
	mission = { naval_patrol } # A list of applicable missions this taskforce can perform
	min_composition = { # The minimum composition needed (Need more clarification here. Is the minimum before the goal system can use the taskforce?)
		carrier = 1 # Ship types and the amount needed
		battleship = 1
		heavy_cruiser = 1
		light_cruiser = 1
		destroyer = 1
	}
	
	optimal_composition = { # The maximum composition this taskforce will have
		carrier = 2
		battleship = 2
		heavy_cruiser = 5
		light_cruiser = 3
		destroyer = 6
		submarine = 2
	}
}
```
