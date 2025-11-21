
# AI Faction Theater
```
ai_faction_theater_id = {

	name = [...] # Name of the theater (Loc Environment = faction leader: COUNTRY)

	ai_will_do = {
		# How likely AI is to create this theater
		# SCOPE = actor : COUNTRY
	}

	cancel = {
		# Makes AI to abandon owned theater
		# SCOPE = actor : COUNTRY
	}

	regions = {
		# List of strategic region IDs in this theater
		# NOTE that the area of the theater must be connected!!!
	}

	# By default, the first region in the list of regions must be available in order for the theater
	# to be created. This flag allows to override that behavior and create the theater anyway, as long
	# as at least one region is available.
	can_skip_first_region = yes

	preferred_countries = {
		# Priority list for countries to be assigned to the theater, if those countries are
		# present in the faction. The AI will try to assign countries going from top to bottom
		# until theater's needs are fulfilled. Note, that AI will *not* try to assign every
		# country from this list - if the number of countries needed for the theater is less
		# than are in this list, the remaining countries will be left not assigned to the theater.
	}
}
```
