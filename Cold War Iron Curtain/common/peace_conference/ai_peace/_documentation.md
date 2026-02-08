# Scripted AI desire for peace actions.
This affects AI behavior but not the cost.

## How to access data from the peace action
- `ROOT` - Negotiator country (who is doing the negotiation)
- `FROM` - Taker country (who will be the owner after the conference)
- `FROM.FROM` - Giver country (who was the owner before the conference)
- `FROM.FROM.FROM` - State (iff peace action refers to a state)

You might have to use e.g. `ROOT.FROM` to access the variable from inside another scope

## Possible peace action types
- `take_states`
- `puppet`
- `force_government`
- `liberate`

```
peace_ai_desires = {
	# All AI desires that are active for a peace action are summed. A desire that ends up at 0 or lower means the AI won't take the action.

	arbitrary_name_for_the_desire = {

		peace_action_type = force_government  # For which action types should the AI desire be active. Can take a single type or an array of types, e.g. { puppet liberate }

		enable = {  # Determines when this desire should be active for a peace action. Can contain any trigger, including the peace conference-specific ones.
			# Note that some things (e.g. diplomatic relations, state ownership, etc) are not updated during a peace conference but instead before or after. Use the peace conference-specific triggers (trigger names starting with pc_xxx, e.g. pc_is_puppeted_by) to check for things that happen during a conference.

			ROOT = { has_government = democratic }  # checks if negotiator is democratic

			ROOT.FROM = { tag = AUS }  # Checks if the taker is Austria

			ROOT.FROM.FROM.FROM = { is_core_of = AUS }  # Checks if the state targeted by the peace action is a core of Austria

		}

		ai_desire = 100  # Increase the AI desire by 100 %. 0 means no change, -50 means reduce AI desire by 50 %, and so on.

	}
}
```
