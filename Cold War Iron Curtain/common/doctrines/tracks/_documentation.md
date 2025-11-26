# Doctrine Tracks

Doctrine tracks are made available to the player after they have selected a *Grand Doctrine*. Each track represents the player with further customization of their doctrines, in the form of:
* A **Subdoctrine** at the root
* A series of **Rewards** derived from the subdoctrine that will gradually unlock automatically as you gain **Mastery**
* A **Milestone** derived from the grand doctrine activate once all of the rewards are unlocked

The track script itself is very small; it is the subdoctrine that defines which track it can be assigned to,
and the grand doctrine that defines which tracks it contains.
 
## Script Example
```
infantry = { 
    name = DOCTRINE_TRACK_INFANTRY   # Bindable loc
    background = GFX_NAME             # Background image for the track
    background_offset = 10            # Horizontal offset applied to the background image  
    frame = GFX_NAME                  # Frame image around the track
    icon = GFX_NAME                   # Milestone icon for the track
    icon_frame = GFX_NAME             # Frame around the milestone icon
    
    mastery = {
        multiplier = 2.0 # Multiplies manpower contribution to mastery gain (in this case, 2 times less manpower is needed to gain the same amount of mastery)
        sub_units = { # Which subunits contribute to mastery gain?
            # Any specific subunits could go here, but probably best left for subdoctrine overrides
        }
        categories = { # Which subunit categories constribute to mastery gain?
	        category_all_infantry
	        category_cavalry
        }
        equipment = { # Subunits with this equipment category will contribute to mastery gain
            screen
            capital
        }
    }
}
```