"""Validate CWIC MIO references and inherited trees against the current databases.

Run from any directory. Pass --game-dir for vanilla sprite/texture validation.
This checks source data; it does not replace an in-game UI/DLC check.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from pathlib import Path
import re

MOD = Path(__file__).resolve().parents[2]
LEX = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|==|[{}=<>!]|[^\s{}=<>!#"]+')


@dataclass
class Node:
    key: str | None
    value: str | list[Node]
    start: int
    end: int
    value_start: int
    path: Path

    def children(self, key=None):
        items = self.value if isinstance(self.value, list) else []
        return items if key is None else [n for n in items if n.key == key]

    def get(self, key, default=None):
        items = self.children(key)
        return items[-1].value if items else default

    def values(self, key):
        value = self.get(key, [])
        return [n.value for n in value if n.key is None] if isinstance(value, list) else [value]

    def location(self):
        line = self.path.read_bytes().decode('utf-8-sig').count('\n', 0, self.start) + 1
        return f'{self.path.relative_to(MOD).as_posix()}:{line}'


def parse(path):
    # Decode without newline conversion: offsets are also used by maintenance tools.
    source = path.read_bytes().decode('utf-8-sig')
    tokens = [(m[0], m.start(), m.end()) for m in LEX.finditer(source) if not m[0].startswith('#')]
    index = 0

    def block(nested=False):
        nonlocal index
        result = []
        while index < len(tokens):
            word, start, end = tokens[index]
            index += 1
            if word == '}':
                if not nested:
                    raise ValueError(f'{path}: unexpected closing brace at {start}')
                return result, end
            key, value_start = None, start
            if index < len(tokens) and tokens[index][0] in ('=', '>', '<', '>=', '<=', '!=', '=='):
                key = word.strip('"')
                index += 1
                word, value_start, end = tokens[index]
                index += 1
            if word == '{':
                value, end = block(True)
            else:
                value = word.strip('"')
            result.append(Node(key, value, start, end, value_start, path))
        if nested:
            raise ValueError(f'{path}: missing closing brace')
        return result, len(source)

    return Node(None, block()[0], 0, len(source), 0, path)


def walk(node):
    for child in node.children():
        yield child
        yield from walk(child)


def database(folder, wrapper=None):
    result = {}
    for path in sorted(folder.rglob('*.txt')):
        root = parse(path)
        containers = root.children(wrapper) if wrapper else [root]
        for container in containers:
            for node in container.children():
                if node.key and isinstance(node.value, list):
                    if node.key in result:
                        raise ValueError(f'Duplicate definition {node.key}: {path}')
                    result[node.key] = node
    return result


def merge_node(base, override):
    keys = {n.key for n in override.children()}
    deleted = set(override.values('delete_included_values'))
    return replace(base, value=[n for n in base.children() if n.key not in keys | deleted] + override.children())


def resolve_organizations(orgs):
    cache = {}

    def resolve(key, visiting=()):
        if key in visiting:
            raise ValueError(f'MIO include cycle: {visiting + (key,)}')
        if key in cache:
            return cache[key]
        node = orgs[key]
        fields, traits = {}, {}
        for include in node.values('include'):
            inherited_fields, inherited_traits = resolve(include, visiting + (key,))
            fields.update(inherited_fields)
            traits.update(inherited_traits)
        for deleted in node.values('delete_included_values'):
            fields.pop(deleted, None)
        for child in node.children():
            if child.key == 'remove_trait':
                for token in (n.value for n in child.children()):
                    traits.pop(token)
            elif child.key in ('trait', 'add_trait', 'override_trait'):
                token = child.get('token')
                if child.key == 'override_trait':
                    if token not in traits:
                        raise ValueError(f'{child.location()}: override of missing trait {token}')
                    traits[token] = merge_node(traits[token], child)
                else:
                    if token in traits:
                        raise ValueError(f'{child.location()}: duplicate trait {token}')
                    traits[token] = child
            elif child.key:
                fields[child.key] = child
        cache[key] = (fields, traits)
        return cache[key]

    for key in orgs:
        resolve(key)
    return cache


def validate(game_dir=None):
    errors = []
    def check(condition, node, message):
        if not condition:
            errors.append(f'{node.location()}: {message}')

    folder = MOD / 'common/military_industrial_organization'
    orgs = database(folder / 'organizations')
    orgs = {k: n for k, n in orgs.items() if n.path.name != 'mio.txt'}  # Disabled engine examples.
    policies = database(folder / 'policies')
    groups = database(MOD / 'common/equipment_groups')
    equipment = database(MOD / 'common/units/equipment', 'equipments')
    # NSB role archetypes are generated by the engine, not regular equipments.
    equipment.update(database(MOD / 'common/units/equipment', 'duplicate_archetypes'))
    modules = database(MOD / 'common/units/equipment/modules', 'equipment_modules')
    types = {t for n in equipment.values() for t in n.values('type')}
    module_types = {n.get('category') for n in modules.values() if isinstance(n.get('category'), str)}
    valid_types = set(equipment) | set(modules) | types | module_types | set(groups)
    techs = database(MOD / 'common/technologies', 'technologies')
    categories = {c for n in techs.values() for c in n.values('categories')}
    ideas = set()
    for path in (MOD / 'common/ideas').rglob('*.txt'):
        for root in parse(path).children('ideas'):
            ideas.update(n.key for category in root.children() for n in category.children() if n.key)

    sprites = {}
    roots = ([game_dir] if game_dir else []) + [MOD]
    for root in roots:
        for path in (root / 'interface').rglob('*.gfx'):
            source = path.read_text(encoding='utf-8-sig', errors='replace')
            # Only sprite headers: shader blocks may have nested braces.
            for header in re.split(r'\b(?:spriteType|textspriteType|corneredTileSpriteType)\s*=\s*\{', source, flags=re.I)[1:]:
                header = header.split('}', 1)[0]
                name = re.search(r'\bname\s*=\s*"([^"]+)"', header)
                texture = re.search(r'\btexturefile\s*=\s*"([^"]+)"', header, re.I)
                if name:
                    sprites[name[1]] = texture[1] if texture else None

    used_groups = set()
    for key, node in {**orgs, **policies}.items():
        for child in walk(node):
            if child.key in ('equipment_type', 'limit_to_equipment_type', 'has_mio_equipment_type'):
                refs = [n.value for n in child.children()] if isinstance(child.value, list) else [child.value]
                for ref in refs:
                    check(ref in valid_types, child, f'unknown equipment/group {ref}')
                    if ref in groups:
                        used_groups.add(ref)
            if child.key == 'research_categories':
                for ref in (n.value for n in child.children()):
                    check(ref in categories, child, f'research category has no technologies: {ref}')
            if child.key == 'icon':
                check(child.value in sprites, child, f'missing sprite {child.value}')
                texture = sprites.get(child.value)
                if texture:
                    check(any((r / texture).is_file() for r in roots), child, f'missing texture {texture}')
            if child.key == 'set_technology':
                for target in child.children():
                    if target.key not in ('popup', 'show_equipment'):
                        check(target.key in techs, target, f'missing reward technology {target.key}')
            if child.key == 'add_ideas':
                refs = [child.value] if isinstance(child.value, str) else [n.value for n in child.children()]
                for ref in refs:
                    check(ref in ideas, child, f'missing reward idea {ref}')
            if child.key in ('production_bonus', 'equipment_bonus'):
                allowed = {'production_cost_factor', 'production_efficiency_cap_factor', 'production_efficiency_gain_factor',
                           'production_capacity_factor', 'production_resource_need_factor', 'production_resource_penalty_factor',
                           'production_conversion_speed_factor'}
                for bonus in child.children():
                    # Policies nest modifiers under equipment/group selectors.
                    modifiers = bonus.children() if isinstance(bonus.value, list) else [bonus]
                    if isinstance(bonus.value, list):
                        check(bonus.key == 'same_as_mio' or bonus.key in valid_types, bonus, f'unknown bonus selector {bonus.key}')
                    for mod in modifiers:
                        if child.key == 'production_bonus':
                            check(mod.key in allowed, mod, f'non-production modifier {mod.key} in production_bonus')
                        else:
                            check(mod.key not in allowed, mod, f'production modifier {mod.key} in equipment_bonus')

    def expand_group(key, visiting=()):
        if key in visiting:
            raise ValueError(f'Equipment group cycle: {visiting + (key,)}')
        if key not in groups:
            return {key} if key in valid_types else set()
        return set().union(*(expand_group(t, visiting + (key,)) for t in groups[key].values('equipment_type')))

    for key, node in groups.items():
        for ref in node.values('equipment_type'):
            check(ref in valid_types, node, f'unknown member {ref} in {key}')
        check(bool(expand_group(key)), node, f'empty equipment group {key}')
    for group in used_groups:
        node = groups[group]
        check('GFX_' + group in sprites, node, f'missing equipment group sprite GFX_{group}')
        texture = sprites.get('GFX_' + group)
        if texture:
            check(any((r / texture).is_file() for r in roots), node, f'missing group texture {texture}')

    # Resolve real variant ancestry as well as generated role archetypes. This
    # catches selectors which exist but cannot affect any supported equipment.
    def ancestry(key, visiting=()):
        if key in visiting or key not in equipment:
            return {key}
        result = {key}
        parent = equipment[key].get('archetype')
        if isinstance(parent, str):
            result |= ancestry(parent, visiting + (key,))
        return result
    families = {key: ancestry(key) for key in equipment}
    def coverage(key, visiting=()):
        if key in visiting:
            return set()
        if key in groups:
            return set().union(*(coverage(t, visiting + (key,)) for t in groups[key].values('equipment_type')))
        if key in equipment:
            return {name for name, chain in families.items() if key in chain}
        if key in types:
            return {name for name, chain in families.items()
                    if any(key in equipment[ancestor].values('type') for ancestor in chain if ancestor in equipment)}
        if key in modules:
            return {key}
        return {name for name, node in modules.items() if node.get('category') == key}

    for key, node in orgs.items():
        if not key.startswith('generic_'):
            continue
        supported = set().union(*(coverage(t) for t in node.values('equipment_type')))
        for trait in node.children('trait'):
            limits = trait.values('limit_to_equipment_type')
            if limits and (trait.get('equipment_bonus') or trait.get('production_bonus')):
                targets = set().union(*(coverage(t) for t in limits))
                check(bool(targets & supported), trait, f'{key}/{trait.get("token")}: bonuses target unsupported equipment')

    # Hidden rewards must target current battalion categories and have no
    # research-tree entry. Their IDs must remain stable for saved games.
    unit_categories = set(parse(MOD / 'common/unit_tags/00_categories.txt').values('sub_unit_categories'))
    rewards = MOD / 'common/technologies/MIO_electronics_rewards.txt'
    for root in parse(rewards).children('technologies'):
        for tech in root.children():
            check(bool(tech.children('allow')) and tech.children('allow')[0].get('always') == 'no', tech, 'MIO reward must be unresearchable')
            check(not tech.children('folder'), tech, 'MIO reward must stay outside the research tree')
            for child in tech.children():
                if child.key and child.key.startswith('category_'):
                    check(child.key in unit_categories, child, f'unknown battalion category {child.key}')

    for path in (MOD / 'common/ideas').glob('MIO*.txt'):
        for node in walk(parse(path)):
            if node.key == 'research_bonus':
                for bonus in node.children():
                    check(bonus.key in categories, bonus, f'MIO reward category has no technologies: {bonus.key}')

    effective = resolve_organizations(orgs)
    for key, (fields, traits) in effective.items():
        occupied = {}
        for token, trait in traits.items():
            for requirement in walk(trait):
                if requirement.key == 'is_mio_trait_completed':
                    check(requirement.value in traits, requirement, f'{key}: unknown completed trait {requirement.value}')
            for relation in ('any_parent', 'all_parents', 'mutually_exclusive'):
                for target in trait.values(relation):
                    check(target in traits, trait, f'{key}/{token}: missing {relation} {target}')
            position = tuple(sorted((n.key, n.value) for n in trait.get('position', [])))
            if position:
                check(position not in occupied, trait, f'{key}: position collision {token} and {occupied.get(position)}')
                occupied[position] = token
        # Parent dependencies must be acyclic, even when they reference valid tokens.
        visited, visiting = set(), set()
        def visit(token):
            if token in visited or token not in traits:
                return
            if token in visiting:
                raise ValueError(f'{key}: parent cycle at {token}')
            visiting.add(token)
            tr = traits[token]
            for parent in tr.values('any_parent') + tr.values('all_parents'):
                visit(parent)
            visiting.remove(token)
            visited.add(token)
        for token in traits:
            visit(token)
    print(f'Checked {len(orgs)} MIO definitions, {len(policies)} policies, {len(groups)} groups, '
          f'{len(techs)} technologies and {sum(len(t) for _, t in effective.values())} inherited trait instances.')
    for error in sorted(set(errors)):
        print('ERROR:', error)
    if errors:
        raise SystemExit(1)
    print('PASS: references, sprites/textures, bonus blocks, inheritance, positions and parent graphs.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--game-dir', type=Path)
    args = parser.parse_args()
    validate(args.game_dir)
