## What is a Collection

Collections are groups of scopable objects of the same type.

## Referencing Collections

To reference a collection, simply write its name in the form `prefix:name`,
like in the following example:

```
some_property = game:all_countries # All countries in the game!
```

## Creating Collections

To create a new collection, pick a unique name and put the following script in any
script file in "common/collections":

```
my_awesome_collection = {

	input = prefix:another_collection # A reference to another collection that will be used as input

	limit = {
		# Optional
		#
		# A trigger that can be used to make the new collection only contain elements of the input
		# that match certain criteria.
		#
		# SCOPE = element of the input collection
		# PREV = previous scope, defined by the context in which the collection is used
		# ROOT = PREV.ROOT
		# FROM = PREV.FROM
		#
		# NOTE : the scope structure above mimics the scope structure of other every_xxx effects
	}
}
```

To reference the newly created collection in script, use the *collection:* prefix:

```
some_property = collection:my_awesome_collection
```

## Anonymous Collections

Collections can be defined directly in the place where they are used. Such collections
are called *anonymous*, because they have no name and therefore cannot be referenced
elsewhere.

The syntax used to define an anonymous collection is the same that is used to define
a named collection, except for the fact that anonymous collections can occur anywhere
in script, where a collection reference is expected.

```
some_property = {
	# The scripting of the collection goes here (see above for the detailed info)
}
```

## Built-In Collections

There is a variety of collections that are already built into the game. These built-in
collections can be used directly in script, or serve as inputs when creating other collections.

### game:

Scope: ANY

- *game:empty* - an empty collection
- *game:all_countries* - all currently existing countries in the game
- *game:all_possible_countries* - all possible countries in the game
- *game:all_states* - all states in the game

### country:

Scope: COUNTRY

- *country:faction_members* - all members of the country's faction if any, otherwise - empty collection

## Triggers and Effects

### List of Collection-Related Triggers

- *collection_size* - compares size of a collection with a number or a variable

### List of Collection-Related Effects

- *every_collection_element* - iterates over elements of a collection and applies effects to every element

