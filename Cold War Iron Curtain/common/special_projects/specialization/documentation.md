# What is a specialization ?
Specialization is the category a Special Project is part of.
By extension, It is also the category of Facilities where Special Project are researched.

# Specialization and buildings
Facility buildings in building DB (`game/common/buildings`) and Specializations here need to be perfectly aligned.
For each Specialization entry here, there should be a building with `specialization = specialization_token` in building DB.

# Specialization localization
For the displayed name of the specialization :
- if localization key TAG_my_speciliazation_token exists, use it
- else use loc key my_speciliazation_token

# Example
For now, we mainly need the list of possible specialization tokens
```
my_specialization_token = {
  # Optional
  # GFX key of the background texture of the projects when they are being researched
  icon = GFX_icon
  # if icon provided, use GFX_icon
  # if gfx key GFX_TAG_my_specialization_token exists, use it
  # if gfx key GFX_my_specialization_token exists, use it
  # else use GFX_PLACEHOLDER_sp_specialization_icon

  # Optional
  # GFX key of the background texture of the projects when they are being researched
  blueprint_image = GFX_blueprint
  # if icon provided, use GFX_blueprint
  # if gfx key GFX_TAG_my_specialization_token_blueprint exists, use it (!!NB: Note the _blueprint suffix)
  # if gfx key GFX_my_specialization_token_blueprint exists, use it
  # else use GFX_PLACEHOLDER_sp_blueprint
  
  # Optional
  # GFX key of the program item background texture for the program item. If multiple specializations are applicable use the primary (first) one
  program_background = GFX_blueprint
  # if icon provided, use GFX_blueprint
  # if gfx key GFX_TAG_my_specialization_token_program_item exists, use it (!!NB: Note the _program_item suffix)
  # if gfx key GFX_TAG_my_specialization_token_program_item exists, use it
  # else use GFX_tiled_plain_bg
  
  # Optional
  # Color code for specialization <b, r, g>
  color = { 24 43 23 }
  # If no color code is specified the default color will be grey
}
```
