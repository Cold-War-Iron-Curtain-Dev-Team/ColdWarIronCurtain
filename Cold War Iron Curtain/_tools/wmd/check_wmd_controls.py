"""Offline behavioural checks for missile charging, launch bounds and discard confirmation."""
from pathlib import Path
import re

MOD = Path(__file__).resolve().parents[2]
TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|#[^\n]*|[{}=<>]|[^\s{}=<>]+')


def parse(text):
    tokens = [t for t in TOKEN.findall(text) if not t.startswith('#')]
    index = 0
    def block(nested=False):
        nonlocal index
        result = []
        while index < len(tokens):
            key = tokens[index]
            index += 1
            if key == '}':
                assert nested
                return result
            if index < len(tokens) and tokens[index] in ('=', '<', '>'):
                op = tokens[index]
                index += 1
                assert index < len(tokens)
                value = tokens[index]
                index += 1
                assert value != '}'
                value = block(True) if value == '{' else value.strip('"')
                result.append((key.strip('"'), op, value))
            else:
                result.append((key.strip('"'), None, None))
        assert not nested, 'Unclosed block'
        return result
    return block()


def load(relative):
    return parse((MOD / relative).read_text(encoding='utf-8-sig'))


def get(block, key):
    matches = [value for name, _, value in block if name == key]
    assert len(matches) == 1, (key, len(matches))
    return matches[0]


fx = load('common/scripted_effects/WMD_scripted_effects.txt')
sgui = get(load('common/scripted_guis/WMD_Tab.txt'), 'scripted_gui')
menu = get(sgui, 'WMD_tab_menu')
effects = get(menu, 'effects')
bottom = get(sgui, 'wmd_bottom_portion') if any(k == 'wmd_bottom_portion' for k, _, _ in sgui) else next(
    value for _, _, value in sgui if isinstance(value, list)
    and any(k == 'window_name' and v == 'wmd_bottom_portion' for k, _, v in value))
triggers = get(bottom, 'triggers')
labels = load('common/scripted_localisation/WMD_discard_confirmation.txt')


class Game:
    """Small evaluator for the real effect/trigger blocks under test, with no world countries."""
    def __init__(self, nukes=8, equipment=None, techs=()):
        self.nukes = nukes
        self.equipment = dict(equipment or {})
        self.techs = set(techs)
        self.vars = {'show_wmd': 1}
        self.temp = {}
        self.bindings = {}

    def number(self, value):
        if value.startswith('var:'):
            value = value[4:]
        if value == 'num_of_nukes':
            return self.nukes
        if value.startswith('num_equipment@'):
            kind = value.split('@', 1)[1]
            if kind in self.equipment:
                return self.equipment[kind]
            return sum(v for k, v in self.equipment.items() if k.startswith(kind + '_'))
        if value in self.bindings:
            return self.bindings[value]
        if value.startswith('[') and value.endswith(']'):
            return self.bindings[value[1:-1]]
        try:
            return float(value)
        except ValueError:
            return self.temp.get(value, self.vars.get(value, 0))

    def trigger(self, nodes):
        checks = []
        for key, op, value in nodes:
            if key == 'tooltip':
                continue
            if key == 'NOT':
                checks.append(not self.trigger(value))
            elif key in ('AND', 'custom_trigger_tooltip'):
                checks.append(self.trigger(value))
            elif key == 'OR':
                checks.append(any(self.trigger([node]) for node in value))
            elif key == 'has_tech':
                checks.append(value in self.techs)
            elif key == 'has_idea':
                checks.append(value == 'defcon_system_1')
            elif key == 'check_variable':
                if any(k == 'var' for k, _, _ in value):
                    left, right = self.number(get(value, 'var')), self.number(get(value, 'value'))
                    compare = get(value, 'compare')
                    checks.append({'greater_than_or_equals': left >= right}[compare])
                else:
                    checks.append(self.trigger(value))
            else:
                left, right = self.number(key), self.number(value)
                checks.append({'=': left == right, '>': left > right, '<': left < right}[op])
        return all(checks)

    def run(self, nodes):
        branch_taken = None
        for key, _, value in nodes:
            if key == 'if':
                branch_taken = self.trigger(get(value, 'limit'))
                if branch_taken:
                    self.run([node for node in value if node[0] != 'limit'])
            elif key == 'else_if':
                if not branch_taken and self.trigger(get(value, 'limit')):
                    self.run([node for node in value if node[0] != 'limit'])
                    branch_taken = True
            elif key == 'else':
                if not branch_taken:
                    self.run(value)
                branch_taken = True
            else:
                branch_taken = None
                if key == 'ROOT':
                    self.run(value)
                elif key in ('set_variable', 'set_temp_variable', 'multiply_temp_variable',
                             'add_to_variable', 'subtract_from_temp_variable'):
                    target = self.temp if 'temp_variable' in key else self.vars
                    name, _, argument = value[0]
                    amount = self.number(argument)
                    if key.startswith('set_'):
                        target[name] = amount
                    elif key.startswith('multiply_'):
                        target[name] = target.get(name, 0) * amount
                    elif key.startswith('subtract_'):
                        target[name] = target.get(name, 0) - amount
                    else:
                        target[name] = target.get(name, 0) + amount
                elif key == 'add_nuclear_bombs':
                    self.nukes += self.number(value)
                    assert self.nukes >= 0
                elif key == 'add_equipment_to_stockpile':
                    kind = get(value, 'type')
                    self.equipment[kind] = self.equipment.get(kind, 0) + self.number(get(value, 'amount'))
                    assert self.equipment[kind] >= 0
                elif key == 'meta_effect':
                    previous = self.bindings.copy()
                    for name, _, argument in value:
                        if name != 'text':
                            match = re.fullmatch(r'\[\?(\w+)\|0\]', argument)
                            assert match, argument
                            self.bindings[name] = self.number(match[1])
                    self.run(get(value, 'text'))
                    self.bindings = previous
                elif key == 'clear_array':
                    self.vars[value + '^num'] = 0
                elif key in ('every_country', 'for_each_scope_loop'):
                    pass  # The fixture has no other countries/enemies.
                elif key == 'close_all_windows':
                    self.vars['show_wmd'] = 0
                elif value == 'yes' and any(k == key for k, _, _ in fx):
                    self.run(get(fx, key))
                else:
                    raise AssertionError(('Unsupported effect in test', key, value))


launch = get(fx, 'wmd_nuke_launch')
prefix = launch[:next(i for i, node in enumerate(launch) if node[0] == 'clr_country_flag')]
assert prefix, 'Missile payment must precede strike event dispatch/reset'
for techs, kind in [({'icbm1', 'irbm1'}, 'icbm_equipment'), ({'irbm1'}, 'irbm_equipment'), (set(), 'srbm_equipment')]:
    for count, cost in [(10, 4), (4, 4)]:
        game = Game(equipment={kind: count}, techs=techs)
        game.vars['missile_cost'] = cost
        game.run(prefix)
        game.run(get(fx, 'wmd_reset'))
        assert game.equipment[kind] == count - cost
        assert game.vars['missile_cost'] == 0
print('PASS: missile cost is paid before reset for all three existing delivery branches, including exact stock.')

visibility_cases = 0
for ready in (0, 0.5, 0.75, 1):
    for stock in (1, 2, 3):
        for missiles in (1, 2, 3):
            for selected in (0, 1):
                game = Game(nukes=stock)
                game.vars.update(wmd_ready_status=ready, missile_selected=selected,
                                 wmd_missiles_total=missiles, missile_cost=2, warhead_cost=2,
                                 wmd_authorize=1, strike_level_tier1_selected=0)
                game.vars['WMD_target_states_array^num'] = 1
                on = game.trigger(get(triggers, 'wmd_button_launch_visible'))
                off = game.trigger(get(triggers, 'wmd_button_launch_off_visible'))
                assert on != off, (ready, stock, missiles, selected)
                assert on == (ready == 1 and stock >= 2 and missiles >= 2 and selected == 1)
                if on:
                    assert game.trigger(get(triggers, 'wmd_button_launch_click_enabled'))
                visibility_cases += 1
print(f'PASS: {visibility_cases} launch visibility/resource cases, with sufficient exact warhead and missile stock accepted.')

def label(game, name):
    definition = next(value for _, _, value in labels if get(value, 'name') == name)
    for key, _, value in definition:
        if key != 'text':
            continue
        limits = [v for k, _, v in value if k == 'trigger']
        if not limits or game.trigger(limits[0]):
            return get(value, 'localization_key')
    raise AssertionError('No label')

game = Game(nukes=8)
game.vars['NukeTotal'] = 99  # Deliberately stale display cache.
game.run(get(effects, 'denuclearize_click'))
assert game.nukes == 8 and label(game, 'GetWMDDiscardNuclearLabel') == 'WMD_DISCARD_CONFIRM'
game.nukes = 9  # Production between clicks: confirming must use the live count.
game.run(get(effects, 'denuclearize_click'))
assert game.nukes == 0 and game.vars['NukeTotal'] == 0
assert label(game, 'GetWMDDiscardNuclearLabel') == 'WMD_DISCARD_NUCLEAR'

stock = {'chemical_weapons_1': 5, 'napalm_1': 6, 'sarin_1': 7, 'vx_1': 8}
game = Game(equipment=stock)
game.vars.update(MustardGasTotal=99, NapalmTotal=99, SarinTotal=99, VXTotal=99)
game.run(get(effects, 'denuclearize1_click'))
assert game.equipment == stock
assert label(game, 'GetWMDDiscardChemicalLabel') == 'WMD_DISCARD_CONFIRM'
game.run(get(effects, 'denuclearize1_click'))
assert all(v == 0 for v in game.equipment.values())
assert game.vars['wmd_discard_confirmation'] == 0 and game.vars['VXTotal'] == 0
print('PASS: both discard actions require two clicks, show confirmation, and refresh stockpile amounts.')

for cancel in (get(effects, 'exitbutton_wmd_click'),
               get(get(get(sgui, 'wmd_topbar_button'), 'effects'), 'nuke_count_click'), get(fx, 'wmd_reset')):
    game = Game()
    game.run(get(effects, 'denuclearize_click'))
    game.run(cancel)
    assert game.vars['wmd_discard_confirmation'] == 0
    game.run(get(effects, 'denuclearize_click'))
    assert game.nukes == 8 and game.vars['wmd_discard_confirmation'] == 1
game = Game(equipment=stock)
game.run(get(effects, 'denuclearize_click'))
game.run(get(effects, 'denuclearize1_click'))
assert game.nukes == 8 and game.equipment == stock and game.vars['wmd_discard_confirmation'] == 2
game.run(get(effects, 'denuclearize_click'))
assert game.nukes == 8 and game.equipment == stock and game.vars['wmd_discard_confirmation'] == 1
print('PASS: close/topbar/reset and switching discard actions cannot accidentally confirm another discard.')

gui = load('interface/WMD.gui')
text = (MOD / 'interface/WMD.gui').read_text(encoding='utf-8-sig')
for name in ('GetWMDDiscardNuclearLabel', 'GetWMDDiscardChemicalLabel'):
    assert f'buttonText = "[{name}]"' in text
loc = (MOD / 'localisation/english/WMD_controls_l_english.yml').read_bytes()
assert loc.startswith(b'\xef\xbb\xbf')
keys = re.findall(r'^ (\w+):0 "', loc.decode('utf-8-sig'), re.M)
assert len(keys) == len(set(keys)) == 5
assert 'Are you sure?' in loc.decode('utf-8-sig')
print('PASS: changed Clausewitz files parse and dynamic labels/tooltips have BOM-encoded localisation.')
