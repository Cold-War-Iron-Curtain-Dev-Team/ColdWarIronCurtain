# Focus inlay windows
Focus inlay windows are generic inlay components that can be added
to the focus tree. Currently, they only support showing information
and no interaction.

## Define inlay window syntax
An inlay window is defined using the following syntax
```
inlay_window_id = {
    window_name = gui_component_name
    internal = yes/no # If true, then the inlay window is only visible to the country itself (defaults no) 
    visible = visibility_trigger # when not visible, no evaluations will be done
    scripted_images = { # list of images that should have dynamic sprites
        icon_name = { # Name of the icon (must be a subcomponent of "gui_component_name")
            # List of possible gfx:es for the icon, first that
            # evaluates to true is selected (each update)

            # Each entry consists of a gfx_name (the gfx that will be used if the trigger is true); and a trigger or "yes"
            # If a trigger is provided, then it will be evaluated with the country scope of the focus tree.
            # If "yes" is set, then it will always be used.
            # Note: "yes" is commonly the last entry in the list
            # that acts as a default case.
            gfx_name = selection_trigger_or_yes
        }
    }
}
```

## Include inlay window in focus tree
An inlay window can be included in a focus tree using the following syntax. Note that any number of inlay windows can be defined for every focus tree.

```
inlay_window = {
    id = inlay_window_id
    position = { x = XXX y = YYY } # same syntax and scale as continuous focus position
}
```