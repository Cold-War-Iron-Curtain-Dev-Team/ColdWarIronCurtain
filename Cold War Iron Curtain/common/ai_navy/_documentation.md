# Goal-based Naval AI

## Introduction

This system replaces how the AI executes missions. The previous system relied on pre-defined priorities between missions, and rather obtuse logic for how task forces would be gathered and assigned to the missions. This new system aims to make the AI decision-making process more flexible, understandable and scriptable.

## Key concepts:

### Goals

A goal is a high-level operation that the AI could utilize its navy for.

Some examples:
* Supporting naval invasions
* Protecting trade routes
* Establishing naval dominance

A goal encompasses the action and the purpose, but a goal in itself does not have a specific target. That is where **Objectives** come in.

### Objectives

An objective is the application of a goal to a specific target.

Some examples:
* Supporting the naval invasion **on Iwo Jima** (i.e. a specific invasion)
* Protecting our trade route **with France** (i.e. a specific trade route)
* Establishing naval dominance **in the Mediterranean** (i.e. a specific region)

## Goal/Objective Scoring

All active objectives for a country are collected and scored. Objectives are then executed in a prioritized order according to the score - the AI will try to execute as many objectives as possible, starting with the highest scoring one.

Objectives are scored based on two factors:
* The **goal priority**: Each goal has a priority range, which signifies the importance of that goal to the country. This range determines the scoring range for objectives within that goal.
* The **objective importance**: This is a normalized value between **0-1**, which determines where in the goal's priority range the objective will be scored.

### An example:

* The **naval invasion support** goal has a priority range of **5-10**
  * There is an objective targeting **Iwo Jima** with an importance of **0.8**
  * There is an objective targeting **Okinawa** with an importance of **0.4**
* The **convoy protection** goal has a priority range of **3-8**
  * There is an objective targeting a trade route with **France** with an importance of **0.9**
  * There is an objective targeting a trade route with **Spain** with an importance of **0.4**

The AI will score the objectives as follows:
* Naval invasion support on Iwo Jima: **9.0** ( 5 + (10-5) * 0.8 )
* Convoy protection with France: **7.5** ( 3 + (8-3) * 0.9 )
* Naval invasion support on Okinawa: **7.0** ( 5 + (10-5) * 0.4 )
* Convoy protection with Spain: **5.0** ( 3 + (8-3) * 0.4 )

As illustrated, this results in a priority order where objectives from different goals are mixed. The idea is that the **goal priority** makes sure that the most relevant goals are always more favored, while the **objective importance** prioritizes objectives within goals. This system also allows high-value objectives from lower-prio goals to still have a chance to be prioritized over low-value objectives from higher-prio goals, as can be seen from the example above.

## Scripting

```
goal_name = {
    objective_type = [type] # See *Objective Types* below
    available_for = {
        ENG # If present, the goal will be disabled for all countries by default, and only available for the countries within this block
    }
    blocked_for = {
        GER # If present, the goal will be disabled for the countries within this block
    }
    
    min_priority = 5 # The minimum priority for this goal, see *Goal/Objective Scoring* above
    max_priority = 10 # The maximum priority for this goal, see *Goal/Objective Scoring* above
}
```

### Objective Types

These objective types are supported:
* naval_invasion_support
* naval_invasion_defense
* mines_sweeping
* coast_defense
* convoy_protection
* convoy_raiding

## Debugging

Use the command "*imgui show ai_navy*" to enable debugging of naval goals.
