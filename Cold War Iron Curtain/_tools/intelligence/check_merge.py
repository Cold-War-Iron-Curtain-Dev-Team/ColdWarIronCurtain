"""Source and behavioral regression checks for the intelligence merge.

The small interpreter below executes the actual effect AST for state migration,
calculation and launch/closeout contracts. It is deliberately not an HOI4 engine
or a substitute for the native acceptance matrix in MERGE_ACCEPTANCE.md.
"""
from __future__ import annotations

import copy
import math
from pathlib import Path
import re
import subprocess
import unittest

MOD = Path(__file__).resolve().parents[2]
TOKEN = re.compile(r'#[^\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|[{}=<>]|[^\s{}=<>!#]+')


def parse(text):
    tokens = [m[0] for m in TOKEN.finditer(text) if not m[0].startswith('#')]
    pos = 0

    def block(nested=False):
        nonlocal pos
        result = []
        while pos < len(tokens) and tokens[pos] != '}':
            key = tokens[pos].strip('"')
            pos += 1
            if pos >= len(tokens) or tokens[pos] not in ('=', '>', '<', '>=', '<=', '!='):
                # Clausewitz also permits bare lists (traits, filters, mouse
                # buttons). Variable/effect blocks are checked separately.
                result.append(('__value__', '=', key))
                continue
            op = tokens[pos]
            pos += 1
            if tokens[pos] == '{':
                pos += 1
                value = block(True)
            else:
                value = tokens[pos].strip('"')
                pos += 1
            result.append((key, op, value))
        if nested:
            if pos >= len(tokens):
                raise ValueError('Unclosed block')
            pos += 1
        return result

    result = block()
    if pos != len(tokens):
        raise ValueError(f'Unexpected closing brace at token {pos}')
    return result


def definitions(*names):
    result = {}
    for name in names:
        result.update({k: v for k, _, v in parse((MOD / name).read_text(encoding='utf-8-sig'))})
    return result


class ScriptState:
    def __init__(self, defs, variables=None, flags=(), missions=()):
        self.defs = defs
        self.variables = dict(variables or {})
        self.flags = set(flags)
        self.missions = set(missions)
        self.arrays = {}
        self.calls = []
        self.stubs = set()
        self.random = 0.5

    def key(self, key):
        if '^' in key:
            stem, index = key.split('^', 1)
            return f'{stem}^{int(self.value(index))}'
        return key

    def value(self, value):
        try:
            return float(value)
        except ValueError:
            if '^' in value:
                stem, index = value.split('^', 1)
                if index == 'num':
                    return len(self.arrays.get(stem, []))
                if stem in self.arrays:
                    i = int(self.value(index))
                    return self.arrays[stem][i] if 0 <= i < len(self.arrays[stem]) else 0
            return self.variables.get(self.key(value), 0)

    def condition(self, entries):
        def one(key, op, value):
            if key in ('AND', 'limit'):
                return self.condition(value)
            if key == 'OR':
                return any(one(*item) for item in value)
            if key == 'NOT':
                return not self.condition(value)
            if key == 'check_variable':
                return all({'=': a == b, '>': a > b, '<': a < b,
                            '>=': a >= b, '<=': a <= b, '!=': a != b}[cmp]
                           for left, cmp, right in value
                           for a, b in [(self.value(left), self.value(right))])
            if key == 'has_variable':
                return self.key(value) in self.variables
            if key == 'has_country_flag':
                return value in self.flags
            if key == 'has_active_mission':
                return value in self.missions
            if key == 'always':
                return value == 'yes'
            if key in ('exists', 'CWIC_espionage_enabled_trigger'):
                return True
            if key.startswith('var:'):
                return self.condition(value)
            if key in self.defs:
                return self.condition(self.defs[key]) == (value == 'yes')
            raise NotImplementedError(('trigger', key))
        return all(one(*entry) for entry in entries)

    def run(self, name):
        self.calls.append(name)
        if name not in self.stubs:
            self.execute(self.defs[name])

    def execute(self, entries):
        previous_if = None
        for key, _, value in entries:
            if key in ('if', 'else_if', 'else'):
                cond = key == 'else' or self.condition([x for x in value if x[0] == 'limit'])
                run = cond and (key == 'if' or previous_if is False)
                if key == 'if':
                    previous_if = False
                if run:
                    self.execute([x for x in value if x[0] != 'limit'])
                    previous_if = True
                continue
            if key in ('set_variable', 'set_temp_variable', 'add_to_variable',
                       'subtract_from_variable', 'multiply_variable', 'divide_variable'):
                for target, _, source in value:
                    target = self.key(target)
                    a, b = self.variables.get(target, 0), self.value(source)
                    self.variables[target] = {'set_variable': lambda: b,
                        'set_temp_variable': lambda: b, 'add_to_variable': lambda: a+b,
                        'subtract_from_variable': lambda: a-b,
                        'multiply_variable': lambda: a*b,
                        'divide_variable': lambda: a/b}[key]()
            elif key == 'clamp_variable':
                data = {k: v for k, _, v in value}
                target = self.key(data['var'])
                self.variables[target] = min(self.value(data['max']), max(self.value(data['min']), self.value(data['var'])))
            elif key == 'round_variable':
                self.variables[self.key(value)] = math.floor(self.value(value) + 0.5)
            elif key == 'set_variable_to_random':
                target = value if isinstance(value, str) else dict((k, v) for k, _, v in value)['var']
                result = self.random
                if isinstance(value, list):
                    data = dict((k, v) for k, _, v in value)
                    low, high = float(data.get('min', 0)), float(data.get('max', 1))
                    result = low + result * (high-low)
                    if data.get('integer') == 'yes':
                        result = min(high-1, math.floor(result))
                self.variables[self.key(target)] = result
            elif key == 'set_country_flag':
                self.flags.add(value)
            elif key == 'activate_mission':
                self.missions.add(value)
            elif key == 'remove_mission':
                self.missions.discard(value)
            elif key in ('add_to_array', 'remove_from_array'):
                for array, _, source in value:
                    items = self.arrays.setdefault(array, [])
                    item = self.value(source)
                    if key == 'add_to_array':
                        items.append(item)
                    elif item in items:
                        items.remove(item)
            elif key == 'for_each_loop':
                data = dict((k, v) for k, _, v in value)
                for index in range(len(self.arrays.get(data['array'], []))):
                    self.variables[data.get('index', 'i')] = index
                    self.execute([x for x in value if x[0] not in ('array', 'index')])
            elif key.startswith('var:'):
                self.execute(value)
            elif key == 'add_opinion_modifier':
                self.calls.append('add_opinion_modifier')
            elif key in self.defs or key in self.stubs:
                self.run(key)
            else:
                raise NotImplementedError(('effect', key))


DEFS = definitions('common/scripted_effects/CWIC_Espionage_lifecycle_effects.txt',
    'common/scripted_effects/IC_Espionage_effects.txt',
    'common/scripted_effects/IC_Espionage_Trait_Effects.txt',
    'common/scripted_effects/Espionage_Scripting_Special_Effects.txt',
    'common/scripted_effects/USA_MKUltra_mknaomi_effects.txt',
    'common/scripted_effects/Espionage_WIA_Pulse.txt',
    'common/scripted_effects/CWIC_Espionage_completion_effects.txt',
    'common/scripted_triggers/CWIC_Espionage_lifecycle_triggers.txt',
    'common/scripted_triggers/CWIC_Espionage_completion_triggers.txt')


class MergeContracts(unittest.TestCase):
    def state(self, **values):
        defaults = dict(current_page=1, selected_squad_origin=1,
            num_espionage_paramilitary_squads=2, currentMoney=1000,
            selected_operation_index_id_token=7, selected_operation_index_mission_type=11,
            selected_operation_index_risk=3, selected_operation_base_cost=100,
            selected_operation_base_duration=60, selected_operation_index_target=2,
            **{'paramilitary_squad_id_status^0': 1})
        for member in range(1, 6):
            defaults[f'paramilitary_operative_squad_unit_{member}_casualty_exposure_rate^1'] = 4
        defaults.update(values)
        state = ScriptState(DEFS, defaults)
        # Use the shipped member defaults, including their legacy sentinels.
        count = state.value('num_espionage_paramilitary_squads')
        state.variables['num_espionage_paramilitary_squads'] = 1
        state.variables['CWIC_espionage_trait_page'] = 1  # defaults index by the trait page (stage 2)
        for member in range(1, 6):
            state.run(f'generate_skill_traits_default_member_{member}')
        state.variables['num_espionage_paramilitary_squads'] = count
        return state

    def test_archived_legacy_reports_never_reopen_or_reward(self):
        cases = [('mknaomi', 'assay_only', 4), ('mknaomi', 'stockpiled', 5),
                 ('mknaomi', 'reference_only', 4), ('mkoften', 'toxicology_only', 4),
                 ('mkoften', 'anomaly_canvass', 5)]
        for dossier, disposition, terminal in cases:
            with self.subTest(dossier=dossier, disposition=disposition):
                prefix = f'USA_mkultra_{dossier}'
                s = self.state(**{prefix+'_state': 3, 'USA_mkultra_progress': 43})
                s.flags.update([prefix+'_archived', prefix+'_'+disposition])
                s.missions.add(prefix+'_review')
                s.run('USA_mkultra_migrate_mknaomi_archives')
                self.assertEqual(s.value(prefix+'_state'), terminal)
                self.assertNotIn(prefix+'_review', s.missions)
                self.assertEqual(s.value('USA_mkultra_progress'), 43)
                before = copy.deepcopy((s.variables, s.flags, s.missions))
                s.run('USA_mkultra_migrate_mknaomi_archives')
                self.assertEqual(before, (s.variables, s.flags, s.missions))

    def test_cancelled_foreclosed_and_active_files_remain_distinct(self):
        for dossier, old in [('mknaomi', 5), ('mkoften', 4)]:
            prefix = f'USA_mkultra_{dossier}'
            for cancelled, expected in [(True, 9), (False, 10)]:
                s = self.state(**{prefix+'_state': old})
                if cancelled:
                    s.flags.add(prefix+'_cancelled')
                s.run('USA_mkultra_migrate_mknaomi_archives')
                self.assertEqual(s.value(prefix+'_state'), expected)
            for active in (2, 3, 6, 7):
                s = self.state(**{prefix+'_state': active})
                s.run('USA_mkultra_migrate_mknaomi_archives')
                self.assertEqual(s.value(prefix+'_state'), active)

    def test_correct_squad_and_applicable_bonuses(self):
        base = self.state()
        base.run('CWIC_espionage_calculate_selected_operation')
        improved = self.state()
        improved.variables.update({
            'paramilitary_operative_squad_unit_1_installation_demolition_success^1': .15,
            'paramilitary_operative_squad_synergy_sabotage_stealth_bonus^1': .2,
            'paramilitary_operative_squad_synergy_covert_logistics_bonus^1': .1,
            'paramilitary_operative_squad_synergy_operation_planning_speed^1': .25,
            'paramilitary_operative_squad_synergy_airfield_sabotage_efficiency^1': .2,
            'paramilitary_operative_squad_synergy_installation_demolition_success^2': .9})
        improved.run('CWIC_espionage_calculate_selected_operation')
        self.assertGreater(improved.value('selected_operation_success'), base.value('selected_operation_success'))
        self.assertLess(improved.value('selected_operation_detection'), base.value('selected_operation_detection'))
        self.assertEqual(improved.value('selected_operation_index_cost'), 90)
        self.assertEqual(improved.value('selected_operation_index_mission_duration'), 39)
        self.assertGreater(improved.value('selected_operation_strength'), base.value('selected_operation_strength'))

    def test_probability_bounds_and_repeatable_preview(self):
        s = self.state()
        s.variables['paramilitary_operative_squad_synergy_installation_demolition_success^1'] = 20
        s.variables['paramilitary_operative_squad_synergy_sabotage_stealth_bonus^1'] = 20
        s.variables['paramilitary_operative_squad_synergy_operation_planning_speed^1'] = 20
        s.run('CWIC_espionage_calculate_selected_operation')
        self.assertEqual(s.value('selected_operation_success'), 1)
        self.assertEqual(s.value('selected_operation_detection'), 0)
        self.assertEqual(s.value('selected_operation_index_mission_duration'), 1)
        before = copy.deepcopy(s.variables)
        s.run('CWIC_espionage_calculate_selected_operation')
        self.assertEqual(before, s.variables)

    def test_all_base_mission_tables_are_bounded(self):
        for family in range(1, 27):
            for risk in range(1, 7):
                with self.subTest(family=family, risk=risk):
                    s = self.state(selected_operation_index_mission_type=family,
                                   selected_operation_index_risk=risk)
                    s.run('CWIC_espionage_calculate_selected_operation')
                    for field in ('success', 'detection', 'casualty'):
                        self.assertGreaterEqual(s.value('selected_operation_'+field), 0)
                        self.assertLessEqual(s.value('selected_operation_'+field), 1)

    def test_launch_snapshots_survive_selection_changes_and_double_callbacks(self):
        s = self.state()
        s.run('launch_operation_effect')
        self.assertEqual(s.value('currentMoney'), 900)
        self.assertIn('Espionage_Operation_Slot_1', s.missions)
        snapshots = {k: v for k, v in s.variables.items() if k.startswith('slot_one_')}
        s.variables.update(current_page=2, selected_squad_origin=2,
            selected_operation_index_target=99, selected_operation_index_id_token=3,
            selected_operation_base_cost=10000, selected_operation_index_risk=6)
        s.run('launch_operation_effect')
        self.assertEqual(s.value('currentMoney'), 900)
        self.assertEqual(snapshots, {k: v for k, v in s.variables.items() if k.startswith('slot_one_')})
        s.stubs.update(('CWIC_espionage_dispatch_operation_outcome', 'CWIC_espionage_resolve_casualties'))
        s.run('operation_closeout_effect')
        s.run('operation_closeout_effect')
        self.assertEqual(s.calls.count('CWIC_espionage_dispatch_operation_outcome'), 1)
        self.assertEqual(s.calls.count('CWIC_espionage_resolve_casualties'), 1)
        self.assertEqual(s.value('history_target'), 2)
        self.assertEqual(s.value('currentMoney'), 900)
        self.assertEqual(s.value('current_operations'), 0)
        self.assertEqual(s.value('paramilitary_squad_id_status^0'), 1)

    def test_unready_operations_do_not_charge_or_launch(self):
        cases = [dict(selected_operation_index_id_token=token) for token in (3518, *range(20000, 20010))]
        cases += [dict(currentMoney=0), dict(selected_squad_origin=3),
                  {'operative_1_wia^1': 1}, {'paramilitary_squad_id_status^0': 2}]
        for values in cases:
            with self.subTest(values=values):
                s = self.state(**values)
                balance = s.value('currentMoney')
                s.run('launch_operation_effect')
                self.assertEqual(s.value('currentMoney'), balance)
                self.assertNotIn('Espionage_Operation_Slot_1', s.missions)

    def test_casualties_use_the_launched_squad_and_probability_endpoints(self):
        for chance, roll, fate in [(0, .8, 'safe'), (1, .8, 'wia'), (1, 0, 'kia')]:
            s = self.state()
            s.run('launch_operation_effect')
            s.variables['current_page'] = 2
            s.random = roll
            for member in range(1, 6):
                s.variables[f'slot_one_member_{member}_casualty'] = chance
                s.stubs.add(f'remove_current_operative_{member}')
            s.run('CWIC_espionage_resolve_casualties')
            for member in range(1, 6):
                self.assertEqual(s.value(f'operative_{member}_wia^2'), 0)
                self.assertEqual(s.value(f'operative_{member}_wia^1'), 3 if fate == 'wia' else 0)
                self.assertEqual(s.value(f'operative_{member}_kia^1'), int(fate == 'kia'))

    def test_recovery_uses_stored_squad_ids(self):
        s = self.state(**{'operative_1_wia^1': 3, 'operative_2_wia^4': 1})
        s.arrays['paramilitary_squad_id'] = [1, 4]
        s.run('wia_recovery_effect')
        self.assertEqual(s.value('operative_1_wia^1'), 2)
        self.assertEqual(s.value('operative_2_wia^4'), 0)
        self.assertEqual(s.value('operative_1_wia^0'), 0)

    def test_existing_inflight_save_migrates_without_another_payment(self):
        s = self.state(current_page=2, slot_one_mission_token=7,
            slot_one_risk=3, slot_one_time_duration=60,
            selected_squad_slot_1_Current_Page_Ref=1)
        s.missions.add('Espionage_Operation_Slot_1')
        s.arrays['local_possible_operations_id_token'] = [7]
        s.arrays['local_possible_operations_operation_type'] = [11]
        s.run('CWIC_espionage_reconcile_operation')
        self.assertEqual(s.value('slot_one_operation_active'), 1)
        self.assertEqual(s.value('slot_one_snapshot_version'), 1)
        self.assertEqual(s.value('currentMoney'), 1000)
        self.assertEqual(s.value('current_page'), 2)
        self.assertIn('Espionage_Operation_Slot_1', s.missions)
        before = copy.deepcopy(s.variables)
        s.run('CWIC_espionage_reconcile_operation')
        self.assertEqual(before, s.variables)

    def test_changed_source_structure_and_variable_assignments(self):
        repo = MOD.parent
        tracked = subprocess.check_output(['git', '-c', 'core.safecrlf=false', 'diff',
            '--name-only', 'origin/development-branch'], cwd=repo, text=True).splitlines()
        untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'],
            cwd=repo, text=True).splitlines()

        def walk(body):
            for key, _, value in body:
                if isinstance(value, list):
                    if key in ('set_variable', 'set_temp_variable', 'add_to_variable',
                               'subtract_from_variable', 'multiply_variable', 'divide_variable'):
                        self.assertNotIn('__value__', [x[0] for x in value], key)
                    walk(value)
        for name in set(tracked + untracked):
            path = repo / name
            if not path.is_file() or path.suffix not in ('.txt', '.gui', '.gfx', '.yml'):
                continue
            with self.subTest(path=name):
                data = path.read_bytes()
                self.assertNotIn(b'\0', data)
                if path.suffix == '.yml':
                    self.assertTrue(data.startswith(b'\xef\xbb\xbf'), name)
                else:
                    walk(parse(data.decode('utf-8-sig')))

    def test_engine_comparison_and_building_damage_syntax(self):
        # Engine-generated documentation allows only =, < and > in shorthand
        # check_variable blocks. damage_building's damage takes a literal.
        for name in ('common/scripted_effects/CWIC_Espionage_lifecycle_effects.txt',
                     'common/scripted_triggers/CWIC_Espionage_lifecycle_triggers.txt'):
            text = (MOD / name).read_text(encoding='utf-8-sig')
            self.assertNotRegex(text, r'check_variable\s*=\s*\{[^{}]*(?:<=|>=)')
        text = (MOD / 'common/scripted_effects/IC_Espionage_effects.txt').read_text(encoding='utf-8-sig')
        self.assertFalse('damage = ROOT.slot_one_damage' in text,
                         'damage_building requires a literal damage amount')


if __name__ == '__main__':
    unittest.main(verbosity=2)
