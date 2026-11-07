"""Format Congress passage effects for the current bill and last vote cards."""

from decimal import Decimal, InvalidOperation

from spirit_slots.parse_ideas import blocks, parse as parse_ideas, strip_comments
from ww3.ww3_script import pairs, parse


def label(key, loc):
    return f"${key}$" if key in loc else key.replace("_", " ").strip()


def number(value, *, percent=False, precision=None):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError, ValueError):
        return None
    if percent:
        amount *= 100
    result = f"{amount:+.{precision}f}" if precision is not None else f"{amount:+f}"
    if precision is None and "." in result:
        result = result.rstrip("0").rstrip(".")
    return result + ("%" if percent else "")


def read_idea_effects(root):
    ideas = {}
    for path in sorted((root / "common/ideas").rglob("*.txt")):
        for idea, category, body in parse_ideas(path):
            if category != "TOPLEVEL_BROKEN":
                effects = {}
                for section, content, _, _ in blocks(body):
                    if section in ("modifier", "research_bonus"):
                        effects[section] = pairs(parse(content))
                if effects:
                    ideas[idea] = effects
    return ideas


def read_modifier_types(root):
    types = {}
    for path in sorted((root / "common/modifier_definitions").rglob("*.txt")):
        text = strip_comments(path.read_text(encoding="utf-8-sig", errors="replace"))
        for key, body, _, _ in blocks(text):
            fields = {k: v for k, _, v in pairs(parse(body))}
            types[key] = fields.get("value_type")
    return types


def bill_effect_localisation(root, bills, loc):
    ideas = read_idea_effects(root)
    modifier_types = read_modifier_types(root)

    def idea_effect(key, days=None):
        duration = f" for {days} days" if days else ""
        lines = [f"Gain §Y{label(key, loc)}§!{duration}."]
        for modifier, _, value in ideas.get(key, {}).get("modifier", []):
            kind = modifier_types.get(modifier)
            percent = kind == "percentage" or (
                kind is None and modifier.endswith(("_factor", "_multiplier"))
            )
            precision = 1 if percent else 2 if modifier in ("encryption", "decryption") else None
            amount = number(value, percent=percent, precision=precision)
            if amount is not None:
                loc_key = "MODIFIER_" + modifier.upper()
                lines.append(f"  {label(loc_key if loc_key in loc else modifier, loc)}: {amount}")
        for category, _, value in ideas.get(key, {}).get("research_bonus", []):
            amount = number(value, percent=True)
            if amount is not None:
                lines.append(f"  {label(category, loc)} research: {amount}")
        return lines

    scalars = {
        "add_political_power": ("Political power", False),
        "add_stability": ("Stability", True),
        "add_war_support": ("War support", True),
        "add_research_slot": ("Research slots", False),
        "army_experience": ("Army experience", False),
        "air_experience": ("Air experience", False),
        "navy_experience": ("Navy experience", False),
        "add_extra_state_shared_building_slots": ("Building slots", False),
    }
    scopes = {
        "capital_scope": "Capital",
        "every_owned_state": "Each owned state",
        "random_owned_state": "An eligible owned state",
        "random_owned_controlled_state": "An eligible controlled state",
        "every_country": "Eligible countries",
    }
    policy = {
        "step_towards_planned": "Shift toward a planned economy.",
        "step_towards_market": "Shift toward a market economy.",
        "step_towards_public": "Shift toward public ownership.",
        "step_towards_private": "Shift toward private ownership.",
        "cwic_set_healthcare_level": "Change the healthcare policy tier.",
    }

    def describe(key, value):
        fields = {k: v for k, _, v in pairs(value)} if isinstance(value, list) else {}
        if key == "add_ideas":
            names = [value] if isinstance(value, str) else [v for v in value if isinstance(v, str)]
            return [line for name in names for line in idea_effect(name)]
        if key == "remove_ideas":
            names = [value] if isinstance(value, str) else [v for v in value if isinstance(v, str)]
            return [f"Remove §Y{label(name, loc)}§!." for name in names]
        if key == "add_timed_idea" and "idea" in fields:
            return idea_effect(fields["idea"], fields.get("days"))
        if key == "swap_ideas" and "add_idea" in fields:
            return describe("remove_ideas", fields["remove_idea"]) + idea_effect(fields["add_idea"])
        if key in scalars:
            name, percent = scalars[key]
            return [f"{name}: {number(value, percent=percent) or label(value, loc)}."]
        if key == "custom_effect_tooltip" and isinstance(value, str) and value in loc:
            return [label(value, loc)]
        if key in ("add_building_construction", "add_offsite_building") and "type" in fields:
            return [f"Build {fields.get('level', '1')} × {label(fields['type'], loc)}."]
        if key == "add_tech_bonus" and "bonus" in fields:
            category = fields.get("category", fields.get("technology", "research"))
            return [f"{label(category, loc)} research bonus: {number(fields['bonus'], percent=True)} "
                    f"({fields.get('uses', '1')} uses)."]
        if key == "add_core_of":
            return [f"Becomes a core of {label(value, loc)}."]
        if key == "complete_national_focus":
            return [f"Complete §Y{label(value, loc)}§!."]
        if key in ("country_event", "news_event"):
            event = fields.get("id", value)
            return [f"Event: §Y{label(event + '.t', loc)}§!."] if isinstance(event, str) and event + ".t" in loc else []
        if key == "set_temp_variable" and "money_change_temp" in fields:
            amount = number(fields["money_change_temp"])
            return [f"Treasury: {amount} billion."] if amount is not None else []
        if key == "cwic_change_money":
            return []
        if key in ("add_to_variable", "set_variable"):
            return [
                f"{label('Election environment' if variable == 'focus_adjustment_USA' else variable, loc)}: "
                f"{'set to ' if key == 'set_variable' else ''}{number(amount) or label(amount, loc)}."
                for variable, amount in fields.items()
                if isinstance(amount, str) and ".idea_" not in variable
            ]
        if key in ("if", "else_if", "else") and "cwic_set_welfare_level" in fields:
            return ["Reduce the welfare policy tier where possible."]
        if key.isdigit() or key in scopes or key in ("if", "else_if", "else"):
            lines = [line for effect, _, val in pairs(value) if effect != "limit" for line in describe(effect, val)]
            if not lines:
                return []
            heading = label("STATE_" + key, loc) if key.isdigit() else scopes.get(key, "Conditional effects")
            return [f"{heading}:", *("  " + line for line in lines)]
        if key in policy:
            return [policy[key]]
        if value == "yes":
            description = key.replace("_", " ")
            return [description[0].upper() + description[1:] + "."]
        return []

    result = {}
    for bill in bills:
        effects = pairs(parse(" ".join(bill["pass"] + bill.get("after_vote", []))))
        lines = [line for key, _, value in effects for line in describe(key, value)]
        # A conditional policy chain describes one change, irrespective of which branch runs.
        welfare = "Reduce the welfare policy tier where possible."
        if lines.count(welfare) > 1:
            first = lines.index(welfare)
            lines = [line for i, line in enumerate(lines) if line != welfare or i == first]
        result[f'USA_CONGRESS_EFFECTS_{bill["key"]}'] = "\n".join(lines or ["See the bill's focus for details."])
    return result
