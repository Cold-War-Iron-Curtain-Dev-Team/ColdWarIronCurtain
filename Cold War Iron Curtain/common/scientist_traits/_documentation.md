# Scientist trait database

This database lists the traits that can be used in the scientist role of characters.

Scientist trait will only apply to Special Projects. Therefore only modifiers applicable to those should be used.

# Example of scientist trait

```
my_scientist_trait_token = {
	# Optional
	# Localization key used for the name of the trait
	name = name_loc_key
    # if name provided, use it.
    # else use loc key my_scientist_trait_token
	
	# Optional
	# GFX key of the icon used to illustrate the Trait
	icon = GFX_icon
    # if icon provided, use GFX_icon
    # else use key GFX_my_scientist_trait_token
	
	# Optional
	# Modifiers that will apply to the special project the scientist with that trait is attached to
	modifier = {
		special_project_prototype_speed_factor = 0.5
	}
	
	# Optional
	# Trait limited to scientist with that specialization only.
	# If not specified it will applicable to all scientist specializations
	specialization = {specialization_land}
}
```