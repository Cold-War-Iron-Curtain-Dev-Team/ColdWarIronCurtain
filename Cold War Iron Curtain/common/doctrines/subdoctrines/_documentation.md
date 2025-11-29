# Subdoctrines

**Subdoctrines** are at the root of each doctrine *Track*. The player can choose any available subdoctrine for that track and activate it by paying an XP cost. Activating a subdoctrine gives immediate effects, like unit stat bonuses or unlocking tactics. Also, activating a subdoctrine starts the automatic activation of a sequence of *Rewards*.

### TODO - how unlocking of rewards works
###reward keys are sub_doctrine_key_reward_key(_desc) - this is because they're not really database objects and this will help us avoid collisions.

## Script Examples

```
bicycle_heroes = {
    track = infantry   # Refers to the script name of a track
    name = SUBDOCTRINE_BICYCLE_HEROES   # Loc key
    description = SUBDOCTRINE_BICYCLE_HEROES_DESC   # Bindable loc
    icon = GFX_subdoctrine_bicycle_heroes   # Refers to the script name of an icon
    available = yes # Trigger that determines whether the doctrine can be selected
    visible = yes # Trigger that determines whether the doctrine is shown in the list at all
    reward_gfx = [GFX_NAME] # Optional - if set, will override the default reward icon strip. Frame 1 to X correspond to reward 1 to X, and X+1 to 2X should be the same but grayed out

    xp_cost = 100
    xp_type = army   # army, navy or air

    ai_will_do = { }

    # ACTIVATION EFFECTS - SEE GRAND DOCTRINES DOCUMENTATION

    rewards = {
        {
            mastery = 150 # Optional - if set, will overide NDefines::NDoctrines::DEFAULT_REWARD_MASTERY
            # ACTIVATION EFFECTS - SEE GRAND DOCTRINES DOCUMENTATION
        }
        {
            # ACTIVATION EFFECTS - SEE GRAND DOCTRINES DOCUMENTATION
        }
        {
            # ACTIVATION EFFECTS - SEE GRAND DOCTRINES DOCUMENTATION
        }
        {
            # ACTIVATION EFFECTS - SEE GRAND DOCTRINES DOCUMENTATION
        }
    }
    
    mastery = { # This will override the default mastery conditions for the track
        multiplier = 5.0 # Multiplies manpower contribution to mastery gain (in this case, 5 times less manpower is needed to gain the same amount of mastery)
        sub_units = { # Which subunits contribute to mastery gain?
            bicycle_battalion
        }
        categories = { # Which subunit categories constribute to mastery gain?
        }
        equipment = { # Subunits with this equipment category will contribute to mastery gain
        }
    }
}
```