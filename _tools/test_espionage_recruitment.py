"""Exercise the parsed recruitment scripts; native UI verification is separate.

Run: python _tools/test_espionage_recruitment.py
The small interpreter deliberately rejects script constructs outside this fixture.
"""
from pathlib import Path
import operator
import re
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent / 'mio'))
from validate_mios import parse, walk

MOD = Path(__file__).resolve().parents[1] / 'Cold War Iron Curtain'
ARRAYS = (
    'temp_build_espionage_paramilitary_operative_type',
    'temp_build_espionage_paramilitary_operative_name_type',
    'temp_build_first_name', 'temp_build_surname', 'temp_build_portrait',
)


class ScriptFixture:
    def __init__(self):
        self.vars = {'has_political_power': 25, 'currentMoney': 0.05}
        self.arrays = {'espionage_paramilitary_operative_type': list(range(8))}
        self.defs = {}
        for name in ('CWIC_Espionage_recruitment_effects.txt', 'rename_keypress_effects.txt'):
            self.defs.update({n.key: n for n in parse(MOD / 'common/scripted_effects' / name).children()})
        self.defs.update({n.key: n for n in parse(MOD / 'common/scripted_triggers/CWIC_Espionage_completion_triggers.txt').children()})
        gui = parse(MOD / 'common/scripted_guis/IC_Espionage_Expansion.txt').children('scripted_gui')[0]
        self.gui = gui
        self.builder = gui.children('country_special_operations_recruitment_list')[0]
        self.gates = {n.key: n for n in self.builder.children('triggers')[0].children()}
        self.clicks = {n.key: n for n in self.builder.children('effects')[0].children()}
        self.sources = {}

    def ref(self, name):
        name = name.removeprefix('ROOT.')
        if '^' in name:
            array, index = name.split('^', 1)
            return array, index if index == 'num' else int(self.value(index))
        return name, None

    def value(self, text):
        try:
            return float(text)
        except ValueError:
            name, index = self.ref(text)
            if index is None:
                return self.vars.get(name, 0)
            data = self.arrays.get(name, [])
            if index == 'num':
                return len(data)
            return data[index] if 0 <= index < len(data) else 0

    def put(self, name, value):
        name, index = self.ref(name)
        if index is None:
            self.vars[name] = value
        else:
            assert index >= 0, f'Negative array write: {name}^{index}'
            data = self.arrays.setdefault(name, [])
            data.extend([0] * max(0, index + 1 - len(data)))
            data[index] = value

    def condition(self, block):
        results = []
        for n in block.children():
            if n.key in ('OR', 'AND', 'NOT'):
                value = self.condition(n) if n.key != 'OR' else any(self.condition_one(c) for c in n.children())
                results.append(not value if n.key == 'NOT' else value)
            else:
                results.append(self.condition_one(n))
        return all(results)

    def condition_one(self, n):
        if n.key == 'AND':
            return self.condition(n)
        if n.key == 'OR':
            return any(self.condition_one(c) for c in n.children())
        if n.key == 'NOT':
            return not self.condition(n)
        if n.key == 'check_variable':
            return self.condition(n)
        if n.key == 'has_variable':
            return n.value in self.vars
        if n.key in self.defs:
            return self.condition(self.defs[n.key]) == (n.value == 'yes')
        if n.key == 'always':
            return n.value == 'yes'
        source = self.sources.setdefault(n.path, n.path.read_bytes().decode('utf-8-sig'))
        comparison = re.search(r'(>=|<=|!=|==|=|>|<)', source[n.start:n.value_start]).group()
        compare = {'=': operator.eq, '==': operator.eq, '!=': operator.ne,
                   '>': operator.gt, '<': operator.lt, '>=': operator.ge, '<=': operator.le}[comparison]
        return compare(self.value(n.key), self.value(n.value))

    def execute(self, block):
        for n in block.children():
            if n.key == 'if':
                if self.condition(n.children('limit')[0]):
                    self.execute_body(n, 'limit')
            elif n.key in ('set_variable', 'add_to_variable', 'subtract_from_variable',
                           'set_temp_variable', 'add_to_temp_variable', 'subtract_from_temp_variable'):
                assignment = n.children()[0]
                value = self.value(assignment.value)
                if not n.key.startswith('set_'):
                    value = self.value(assignment.key) + (value if n.key.startswith('add_') else -value)
                self.put(assignment.key, value)
            elif n.key == 'clamp_variable':
                name = n.get('var')
                self.put(name, max(self.value(n.get('min')), min(self.value(n.get('max')), self.value(name))))
            elif n.key == 'clear_array':
                self.arrays[n.value.removeprefix('ROOT.')] = []
            elif n.key == 'resize_array':
                data = self.arrays.setdefault(n.get('array'), [])
                size = int(self.value(n.get('size')))
                data[:] = (data + [0] * size)[:size]
            elif n.key == 'add_to_array':
                assignment = n.children()[0]
                self.arrays.setdefault(assignment.key, []).append(self.value(assignment.value))
            elif n.key == 'while_loop_effect':
                for _ in range(1000):  # the engine's default cap
                    if not self.condition(n.children('limit')[0]):
                        break
                    self.execute_body(n, 'limit')
                else:
                    raise AssertionError('while_loop_effect did not terminate')
            elif n.key == 'for_each_loop':
                for i, value in enumerate(self.arrays[n.get('array')]):
                    self.vars.update(i=i, v=value)
                    self.execute_body(n, 'array')
            elif n.key == 'CWIC_espionage_refresh_preview':
                pass  # GUI refresh is not part of the recruitment state machine.
            elif n.key in self.defs:
                self.execute(self.defs[n.key])
            else:
                raise AssertionError(f'Unhandled effect {n.key}')

    def execute_body(self, node, excluded):
        for child in node.children():
            if child.key != excluded:
                self.execute(type(node)(None, [child], 0, 0, 0, node.path))

    def ready(self):
        return self.condition(self.defs['CWIC_espionage_can_create_group_trigger'])

    def recruit_five(self):
        self.execute(self.defs['CWIC_espionage_reset_group_builder'])
        for row in range(5):
            self.vars['i'] = row
            for name, values in (
                ('espionage_paramilitary_operative_type', range(8)),
                ('espionage_paramilitary_operative_name_type', range(10, 18)),
                ('first_name', range(20, 28)), ('surname', range(30, 38)), ('portrait', range(40, 48)),
            ):
                self.arrays[name] = list(values)
            assert self.condition(self.gates['special_operations_recruitment_target_entry_button_click_enabled'])
            self.execute(self.clicks['special_operations_recruitment_target_entry_button_click'])
            assert self.condition(self.gates['next_button_click_enabled'])
            self.execute(self.clicks['next_button_click'])


class RecruitmentTests(unittest.TestCase):
    def setUp(self):
        self.s = ScriptFixture()

    def test_five_distinct_confirmations_enable_unnamed_squad(self):
        self.s.recruit_five()
        self.assertEqual(self.s.arrays[ARRAYS[0]], [0, 1, 2, 3, 4])
        self.assertTrue(self.s.ready())
        self.assertFalse(self.s.condition(self.s.gates['next_button_click_enabled']))
        self.s.vars['i'] = 0
        self.assertFalse(self.s.condition(self.s.gates['special_operations_recruitment_target_entry_button_click_enabled']))

    def test_no_stale_or_missing_member_can_enable_creation(self):
        self.s.execute(self.s.defs['CWIC_espionage_reset_group_builder'])
        self.assertFalse(self.s.condition(self.s.gates['next_button_click_enabled']))
        self.s.recruit_five()
        for name in ARRAYS:
            with self.subTest(array=name):
                value = self.s.arrays[name].pop()
                self.assertFalse(self.s.ready())
                self.s.arrays[name].append(value)

    def test_cost_and_squad_caps_still_apply(self):
        self.s.recruit_five()
        for pp, money, squads, upgrades, allowed in (
            (24, .05, 0, 0, False), (25, .049, 0, 0, False),
            (25, .05, 0, 0, True), (25, .05, 2, 2, False),
            (25, .05, 2, 3, True), (25, .05, 3, 5, False),
            (25, .05, 3, 6, True), (25, .05, 4, 8, False),
            (25, .05, 4, 9, True), (25, .05, 5, 20, False),
        ):
            with self.subTest(pp=pp, money=money, squads=squads, upgrades=upgrades):
                self.s.vars.update(has_political_power=pp, currentMoney=money,
                                   num_espionage_paramilitary_squads=squads, agency_upgrade_number=upgrades)
                self.assertEqual(self.s.ready(), allowed)

    def test_default_and_custom_names(self):
        for squads in range(5):
            self.s.vars['num_espionage_paramilitary_squads'] = squads
            self.s.arrays['chars'] = []
            self.s.execute(self.s.defs['CWIC_espionage_ensure_group_name'])
            self.assertEqual(''.join(chr(int(v)) for v in self.s.arrays['chars'] if v), f'Squad {squads + 1}')
        self.s.arrays['chars'] = list(map(ord, 'Alpha')) + [0] * 27
        self.s.execute(self.s.defs['CWIC_espionage_ensure_group_name'])
        self.assertEqual(self.s.arrays['chars'][:5], list(map(ord, 'Alpha')))

    def test_reopening_resets_cursor_and_roster(self):
        self.s.recruit_five()
        self.s.vars['current_char'] = 29
        self.s.execute(self.s.defs['CWIC_espionage_reset_group_builder'])
        self.assertEqual(self.s.value('current_char'), -1)
        self.assertEqual(self.s.value('operative_number_step'), 0)
        self.assertTrue(all(not self.s.arrays[name] for name in ARRAYS))
        self.assertFalse(self.s.ready())

    def test_backspace_and_name_length_boundaries(self):
        self.s.vars['current_char'] = -1
        self.s.arrays['chars'] = [0] * 32
        self.s.execute(self.s.defs['get_keypress_backspace'])
        for _ in range(40):
            self.s.execute(self.s.defs['get_keypress_0'])
        self.assertEqual(len(self.s.arrays['chars']), 32)
        for _ in range(40):
            self.s.execute(self.s.defs['get_keypress_backspace'])
        self.s.execute(self.s.defs['get_keypress_1'])
        self.assertEqual(self.s.arrays['chars'][0], ord('1'))
        self.assertEqual(self.s.value('current_char'), 0)

    def test_staged_row_is_highlighted_before_confirmation(self):
        highlighted = self.s.gates['special_operations_recruitment_target_entry_button_active_visible']
        self.s.execute(self.s.defs['CWIC_espionage_reset_group_builder'])
        for name, values in (
            ('espionage_paramilitary_operative_name_type', range(10, 18)),
            ('first_name', range(20, 28)), ('surname', range(30, 38)), ('portrait', range(40, 48)),
        ):
            self.s.arrays[name] = list(values)
        for row in range(8):
            self.s.vars['i'] = row
            self.assertFalse(self.s.condition(highlighted), row)
        self.s.vars['i'] = 3
        self.s.execute(self.s.clicks['special_operations_recruitment_target_entry_button_click'])
        for row in range(8):
            self.s.vars['i'] = row
            self.assertEqual(self.s.condition(highlighted), row == 3, row)
        self.s.execute(self.s.clicks['next_button_click'])
        for row in range(8):  # confirmed row stays lit; row 0 must not light up from the cleared pick
            self.s.vars['i'] = row
            self.assertEqual(self.s.condition(highlighted), row == 3, row)

    def test_five_confirmed_members_without_political_power_stay_blocked(self):
        self.s.vars['has_political_power'] = 0
        self.s.recruit_five()
        self.assertFalse(self.s.ready())

    def test_unit_builder_fills_the_pool_before_sizing_the_selection_list(self):
        start = self.s.gui.children('Paramilitary_Intel_Button_Placeholder')[0].children('effects')[0]
        order = [n.key for n in start.children('create_special_operations_team_start_click')[0].children()]
        self.assertLess(order.index('espionage_recruitment_generation'),
                        order.index('CWIC_espionage_reset_group_builder'))

    def test_new_squad_state_is_initialised_without_touching_older_squads(self):
        init = self.s.defs['CWIC_espionage_init_new_squad_state']
        self.s.vars['num_espionage_paramilitary_squads'] = 1
        self.s.execute(init)
        self.s.put('operative_3_wia^1', 1)  # squad 1 takes a casualty before squad 2 exists
        self.s.vars['num_espionage_paramilitary_squads'] = 2
        self.s.execute(init)
        for member in range(1, 6):
            for kind in ('wia', 'mia'):
                data = self.s.arrays[f'operative_{member}_{kind}']
                self.assertEqual(len(data), 3)
                self.assertEqual(data[2], 0)
        self.assertEqual(self.s.arrays['operative_3_wia'][1], 1)
        self.assertEqual(self.s.arrays['paramilitary_operative_squad_leader_on_mission'], [0, 0])

    def test_create_click_pays_then_initialises_the_squad(self):
        order = [n.key for n in self.s.clicks['create_group_click'].children()]
        self.assertLess(order.index('CWIC_espionage_pay_group_creation'),
                        order.index('CWIC_espionage_init_new_squad_state'))

    def test_create_tooltip_names_every_gate_condition(self):
        text = (MOD / 'common/scripted_localisation/CWIC_Espionage_recruitment_scripted_localisation.txt').read_text('utf-8-sig')
        loc = (MOD / 'localisation/english/CWIC_Espionage_recruitment_l_english.yml').read_text('utf-8-sig')
        gui = (MOD / 'interface/CWIC_Espionage.gui').read_text('utf-8-sig')
        self.assertIn('pdx_tooltip = CWIC_ESP_CREATE_GROUP_TT', gui)
        for name in ('Members', 'PP', 'Money', 'Cap'):
            self.assertIn(f'name = GetCWICEspCreate{name}Line', text)
            self.assertIn(f'[GetCWICEspCreate{name}Line]', loc)
        for key in re.findall(r'localization_key = (CWIC_ESP_CREATE_\w+)', text):
            self.assertIn(f' {key}:0 ', loc)

    def test_ai_random_choices_have_no_invalid_trigger_effects(self):
        root = parse(MOD / 'common/scripted_effects/CWIC_Espionage_completion_effects.txt')
        ai = root.children('CWIC_espionage_ai_resolve')[0]
        choices = ai.children('random_list')[0]
        self.assertFalse([n for n in walk(choices) if n.key == 'trigger'])
        self.assertEqual(sum(bool(n.children('modifier')) for n in choices.children()), 4)


if __name__ == '__main__':
    unittest.main(verbosity=2)
