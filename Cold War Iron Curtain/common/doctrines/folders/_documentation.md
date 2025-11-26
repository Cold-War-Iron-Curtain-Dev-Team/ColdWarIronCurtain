# Doctrine Folders

Folders are the top-level categorization of doctrines, e.g. *land*, *air* and *naval*, but you can also create a custom folder with any name. Each *Grand Doctrine* belongs to one folder.
 
## Script Example
```
land = { 
    allowed = { # If this trigger evaluates to False, the folder won't be available
        always = yes    
    }
    name = LOC_KEY
    tab_gfx = GFX # This tab button icon to be displayed at the top of the doctrine UI
    color_frame = 1 # This is used as frame index for various UI elements where e.g. background colors depend on the folder
    ledger = army # In which intel ledger should this folder be shown? Supported values: army, navy, air, all, hidden
    ledger_gfx = GFX # The button icon to be shown in the intel ledger
    sound = ui_doctrine_tab_air # The sound to be played when switching to this folder
}
```