"""Stage 9a checks: Cuban Regime Change (tokens 100-116) and Pacifying Western
Ukraine (500-506).

Run from the repository root:
    python -I "Cold War Iron Curtain/_tools/intelligence/check_projects.py"

The interpreter here is deliberately small. It executes the project effects and
the real current_entry_visible_trigger, so a prerequisite that can never be met
(the kind of dead end that stopped these chains before) fails a test.
"""
import math
import pathlib
import re
import sys
import unittest

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from check_merge import MOD, parse  # noqa: E402

PROJECTS = 'common/scripted_effects/CWIC_Espionage_projects_effects.txt'
DOCS = pathlib.Path('G:/steamlbirary/steamapps/common/Hearts of Iron IV/documentation')


def load(*names):
    out = {}
    for name in names:
        out.update({k: v for k, _, v in parse((MOD / name).read_text(encoding='utf-8-sig'))})
    return out


DEFS = load(PROJECTS,
            'common/scripted_triggers/IC_Espionage.txt',
            'common/scripted_triggers/CWIC_Espionage_projects_triggers.txt',
            'common/scripted_triggers/CWIC_Espionage_lifecycle_triggers.txt')

SCOPE = re.compile(r'^(?:[A-Z]{3}|ROOT|THIS|PREV|FROM|var:.+|every_owned_state)$')
VAR_OPS = ('set_variable', 'set_temp_variable', 'add_to_variable', 'subtract_from_variable',
           'multiply_variable', 'divide_variable')


class Game:
    """One country's variables, arrays and flags."""

    def __init__(self, tag):
        self.tag = tag
        self.vars = {}
        self.arrays = {}
        self.flags = set()
        self.global_flags = set()
        self.engine_effects = []      # (scope chain, effect name)
        self.calls = []
        self.random = 0.5
        self.cuba_communist = True

    # --- values -----------------------------------------------------------
    @staticmethod
    def strip(name):
        for prefix in ('ROOT.', 'USA.', 'SOV.', 'THIS.'):
            if name.startswith(prefix):
                return name[len(prefix):]
        return name

    def value(self, raw):
        try:
            return float(raw)
        except (TypeError, ValueError):
            pass
        raw = self.strip(raw)
        if raw.endswith('.id'):
            return hash(raw) % 1000 + 5000          # an opaque, stable scope id
        if '^' in raw:
            stem, index = raw.split('^', 1)
            items = self.arrays.get(stem, [])
            if index == 'num':
                return len(items)
            i = int(self.value(index))
            return items[i] if 0 <= i < len(items) else 0
        return self.vars.get(raw, 0)

    def assign(self, raw, value):
        raw = self.strip(raw)
        if '^' in raw:
            stem, index = raw.split('^', 1)
            items = self.arrays.setdefault(stem, [])
            i = int(self.value(index))
            if not 0 <= i < len(items):
                raise IndexError(f'{stem}^{i} written outside 0..{len(items) - 1}')
            items[i] = value
        else:
            self.vars[raw] = value

    # --- triggers ---------------------------------------------------------
    def test(self, entries):
        return all(self.test_one(k, v) for k, _, v in entries)

    def test_one(self, key, value):
        if key in ('AND', 'limit'):
            return self.test(value)
        if key == 'OR':
            return any(self.test_one(k, v) for k, _, v in value)
        if key == 'NOT':
            return not self.test(value)
        if key == 'check_variable':
            return all({'=': a == b, '>': a > b, '<': a < b}[op]
                       for left, op, right in value
                       for a, b in [(self.value(left), self.value(right))])
        if key == 'has_country_flag':
            return value in self.flags
        if key == 'has_global_flag':
            return value in self.global_flags
        if key == 'tag':
            return value == self.tag
        if key == 'is_in_array':
            data = {k: v for k, _, v in value}
            if set(data) == {'array', 'value'}:
                array, item = data['array'], data['value']
            else:
                (array, item), = data.items()
            return self.value(item) in self.arrays.get(self.strip(array), [])
        if key == 'has_government':
            return self.cuba_communist
        if key in ('exists', 'has_resistance', 'has_active_resistance', 'has_state_flag', 'state',
                   'is_core_of', 'always'):
            return True
        if SCOPE.match(key):
            return self.test(value)
        if key in DEFS:
            return self.test(DEFS[key]) == (value == 'yes')
        raise NotImplementedError(('trigger', key))

    # --- effects ----------------------------------------------------------
    def run(self, name):
        self.calls.append(name)
        self.execute(DEFS[name], ())

    def execute(self, entries, scope):
        took = None
        for key, _, value in entries:
            if key in ('if', 'else_if', 'else'):
                cond = key == 'else' or self.test([x for x in value if x[0] == 'limit'])
                run = cond and (key == 'if' or took is False)
                if key == 'if':
                    took = False
                if run:
                    self.execute([x for x in value if x[0] != 'limit'], scope)
                    took = True
                continue
            if key == 'limit':
                continue
            if key in VAR_OPS:
                for target, _, source in value:
                    a, b = self.value(target), self.value(source)
                    self.assign(target, {'set_variable': b, 'set_temp_variable': b,
                                         'add_to_variable': a + b, 'subtract_from_variable': a - b,
                                         'multiply_variable': a * b,
                                         'divide_variable': a / b if b else 0}[key])
            elif key == 'clamp_variable':
                data = {k: v for k, _, v in value}
                self.assign(data['var'], min(self.value(data['max']),
                                             max(self.value(data['min']), self.value(data['var']))))
            elif key == 'round_variable':
                self.assign(value, math.floor(self.value(value) + 0.5))
            elif key == 'set_variable_to_random':
                self.assign(value, self.random)
            elif key == 'clear_array':
                self.arrays[self.strip(value)] = []
            elif key == 'resize_array':
                data = {k: v for k, _, v in value}
                self.arrays[self.strip(data['array'])] = [0] * int(self.value(data['size']))
            elif key == 'add_to_array':
                for array, _, source in value:
                    self.arrays.setdefault(self.strip(array), []).append(self.value(source))
            elif key == 'for_each_loop':
                data = {k: v for k, _, v in value}
                body = [x for x in value if x[0] not in ('array', 'index')]
                for index in range(len(self.arrays.get(self.strip(data['array']), []))):
                    self.vars[data.get('index', 'i')] = index
                    self.execute(body, scope)
            elif key == 'set_country_flag':
                if scope:
                    self.engine_effects.append((scope, key))
                else:
                    self.flags.add(value if isinstance(value, str)
                                   else {k: v for k, _, v in value}['flag'])
            elif key == 'clr_country_flag':
                self.flags.discard(value)
            elif key == 'set_global_flag':
                self.global_flags.add(value)
            elif SCOPE.match(key):
                self.execute(value, scope + (key,))
            elif key in DEFS:
                self.run(key)
            elif key in ('slot_1_operation_success_shared_effect', 'slot_1_operation_failure_effect'):
                self.calls.append(key)
            else:
                self.engine_effects.append((scope, key))

    # --- helpers ----------------------------------------------------------
    def resolve(self, token, success=True, detected=False):
        self.vars.update(current_token=token, slot_one_successful=int(success),
                         slot_one_detected=int(detected))
        if token == 100:        # handled in IC_Espionage_effects.txt
            if success:
                self.flags.add('Cuban_Emigre_Contacts_Token')
            return
        self.run('CWIC_espionage_dispatch_project_outcome')

    def open_project(self, builder, prefix, view):
        self.run(builder)
        self.vars[view] = 1
        for column, source in (('', ''), ('_id_token', '_id_tokens'),
                               ('_operation_type', '_type'),
                               ('_repeatable_condition', '_repeatable_condition')):
            self.arrays['local_possible_operations' + column] = list(
                self.arrays[prefix + 'operation' + source])

    def visible_tokens(self):
        out = []
        for i, token in enumerate(self.arrays['local_possible_operations_id_token']):
            self.vars['i'] = i
            if self.test(DEFS['current_entry_visible_trigger']):
                out.append(int(token))
        return out


def names_in(body, effects, triggers, in_trigger=False):
    for key, _, value in body:
        here = in_trigger or key == 'limit'
        if key in ('if', 'else_if', 'else', 'limit', 'AND', 'OR', 'NOT') or SCOPE.match(key):
            pass
        elif key not in DEFS:
            (triggers if here else effects).add(key)
        if isinstance(value, list) and key not in VAR_OPS + ('check_variable', 'clamp_variable',
                'add_to_array', 'resize_array', 'add_opinion_modifier', 'add_dynamic_modifier',
                'add_equipment_to_stockpile', 'set_politics', 'start_civil_war', 'set_country_flag',
                'is_in_array', 'for_each_loop'):
            names_in(value, effects, triggers, here)


class ProjectContracts(unittest.TestCase):
    def test_every_engine_name_is_documented(self):
        if not DOCS.is_dir():
            self.skipTest('engine documentation not found')
        effects, triggers = set(), set()
        names_in(parse((MOD / PROJECTS).read_text(encoding='utf-8-sig')), effects, triggers)
        effects -= {'slot_1_operation_success_shared_effect', 'slot_1_operation_failure_effect',
                    'CWIC_espionage_dispatch_project_outcome'}
        known_effects = set(re.findall(r'^## (\w+)$', (DOCS / 'effects_documentation.md').read_text(
            encoding='utf-8', errors='replace'), re.M))
        known_triggers = set(re.findall(r'^## (\w+)$', (DOCS / 'triggers_documentation.md').read_text(
            encoding='utf-8', errors='replace'), re.M))
        self.assertFalse(sorted(effects - known_effects), 'undocumented effects')
        self.assertFalse(sorted(triggers - known_triggers - {'tag'}), 'undocumented triggers')

    def test_every_offered_token_can_launch_and_has_an_outcome(self):
        text = (MOD / PROJECTS).read_text(encoding='utf-8-sig')
        offered = {int(x) for x in re.findall(r'_id_tokens = (\d+)', text)}
        self.assertEqual(offered, set(range(100, 117)) | set(range(500, 507)))
        for token in sorted(offered):
            with self.subTest(token=token):
                g = Game('USA')
                g.vars.update(selected_operation_index_id_token=token,
                              selected_operation_index_mission_type=8, selected_operation_index_risk=3)
                self.assertTrue(g.test(DEFS['CWIC_espionage_selected_operation_supported_trigger']))
                if token != 100:
                    for success in (True, False):
                        g = Game('USA' if token < 500 else 'SOV')
                        g.random = 0.0 if success else 0.99     # 116 rolls its own odds
                        g.resolve(token, success)
                        self.assertIn('slot_1_operation_success_shared_effect' if success
                                      else 'slot_1_operation_failure_effect', g.calls)

    def test_builders_repair_a_doubled_table(self):
        g = Game('USA')
        # The state found in a live 1950 save: the old setup appended risk twice.
        g.arrays['bay_of_pigs_operation_risk_level'] = [1] * 34
        g.arrays['bay_of_pigs_operation'] = list(range(1, 18))
        for _ in range(2):
            g.run('CWIC_espionage_build_bay_of_pigs_operations')
            for column in ('', '_target', '_id_tokens', '_risk_level', '_type',
                           '_repeatable_condition', '_cost'):
                self.assertEqual(len(g.arrays['bay_of_pigs_operation' + column]), 17, column)
            self.assertEqual(len(g.arrays['bay_of_pigs_operation_list_verification']), 8)
        self.assertEqual(g.arrays['bay_of_pigs_operation_id_tokens'], list(range(100, 117)))

    def test_cuban_chain_reaches_the_landing(self):
        g = Game('USA')
        g.open_project('CWIC_espionage_build_bay_of_pigs_operations', 'bay_of_pigs_', 'show_bay_of_pigs')
        launched, steps = [], 0
        self.assertEqual(g.visible_tokens(), [100])
        while 'Bay_of_Pigs_Start_Token' not in g.flags:
            steps += 1
            self.assertLess(steps, 80, f'chain stalled; launched {launched}, visible {g.visible_tokens()}')
            visible = g.visible_tokens()
            self.assertTrue(visible, f'nothing to launch after {launched}')
            fresh = [t for t in visible if t not in launched]
            # New operations first; otherwise work on whichever material is short.
            if fresh:
                token = fresh[0]
            else:
                need = [(103, g.vars.get('Bay_of_Pigs_Aircraft', 0) < 25),
                        (102, g.vars.get('Bay_of_Pigs_Pilots', 0) < 100),
                        (110, g.vars.get('Bay_of_Pigs_Ships', 0) < 10),
                        (108, g.vars.get('Bay_of_Pigs_Infantry_Equipment', 0) < 5000),
                        (109, g.vars.get('Bay_of_Pigs_Trained_Recruits', 0) < 1500
                         and g.vars.get('Bay_of_Pigs_Recruits', 0) > 100),
                        (107, g.vars.get('Bay_of_Pigs_Trained_Recruits', 0) < 1500)]
                token = next((t for t, short in need if short and t in visible), None)
                self.assertIsNotNone(token, f'materials short but no way to add them; visible {visible}')
            g.random = 0.0      # the landing rolls its own odds
            g.resolve(token)
            launched.append(token)
        self.assertEqual(set(launched), set(range(100, 117)))
        self.assertEqual(g.vars['CWIC_esp_bop_outcome'], 2)
        self.assertEqual(g.arrays['bay_of_pigs_operation_list_verification'], [1] * 8)
        self.assertIn('bay_of_pigs_successful', g.global_flags)
        self.assertNotIn(116, g.visible_tokens())

    def test_failures_never_leave_negative_materials(self):
        g = Game('USA')
        for token in list(range(101, 117)) * 2:
            g.resolve(token, success=False, detected=True)
        for name, value in g.vars.items():
            if name.startswith('Bay_of_Pigs_'):
                self.assertGreaterEqual(value, 0, name)
        self.assertEqual(g.vars['CWIC_esp_bop_outcome'], 1)
        self.assertIn('bay_of_pigs_disaster', g.global_flags)

    def test_landing_odds_follow_preparation(self):
        g = Game('USA')
        g.run('CWIC_espionage_bop_roll_liberation')
        self.assertAlmostEqual(g.vars['CWIC_esp_bop_chance'], 0.10)
        g.vars['Bay_of_Pigs_Experience'] = 100
        g.flags |= {'Operation_Puma_Token', 'Diversionary_Strikes_Cuba_Project_Token',
                    'Contacted_Insurgents_Cuba_Project_Token'}
        g.run('CWIC_espionage_bop_roll_liberation')
        self.assertAlmostEqual(g.vars['CWIC_esp_bop_chance'], 0.75)
        g.random = 0.74
        g.run('CWIC_espionage_bop_roll_liberation')
        self.assertEqual(g.vars['slot_one_successful'], 1)
        g.random = 0.76
        g.run('CWIC_espionage_bop_roll_liberation')
        self.assertEqual(g.vars['slot_one_successful'], 0)

    def test_row_markers_show_progress_and_completion(self):
        g = Game('USA')
        g.open_project('CWIC_espionage_build_bay_of_pigs_operations', 'bay_of_pigs_', 'show_bay_of_pigs')
        g.arrays['current_operation_list'] = [101]
        g.flags.add('Cuban_Emigre_Contacts_Token')      # a save from before this stage
        g.run('CWIC_espionage_refresh_operation_status')
        status = g.arrays['local_possible_operations_completed_status']
        self.assertEqual(len(status), 17)
        self.assertEqual(status[:3], [2, 1, 0])
        g.arrays['current_operation_list'] = []
        g.resolve(101)
        g.resolve(102)                                  # repeatable: never ticked
        self.assertEqual(g.arrays['local_possible_operations_completed_status'][:3], [2, 2, 0])
        # Another project's list must not inherit these rows.
        g.vars['show_bay_of_pigs'] = 0
        g.run('CWIC_espionage_refresh_operation_status')
        self.assertEqual(g.arrays['local_possible_operations_completed_status'], [])

    def test_ukraine_chain_ends_the_project(self):
        g = Game('SOV')
        g.flags.add('ukranian_seccessionism')
        g.open_project('CWIC_espionage_build_uia_operations', 'uia_', 'show_uia')
        self.assertEqual(sorted(set(g.arrays['uia_operation_id_tokens'])), list(range(500, 507)))
        # Every row targets the USSR: the UIA is not a country, and the launch
        # gate needs a target that exists.
        self.assertEqual(set(g.arrays['uia_operation_target']), {g.value('ROOT.id')})
        visible = g.visible_tokens()
        self.assertIn(503, visible)
        self.assertNotIn(504, visible)
        g.resolve(503)
        self.assertTrue({504, 505} <= set(g.visible_tokens()))
        for token in (500, 504, 505):
            self.assertIn('ukranian_seccessionism', g.flags)
            g.resolve(token)
        self.assertNotIn('ukranian_seccessionism', g.flags)
        self.assertIn('CWIC_esp_uia_pacified', g.flags)
        g.resolve(501)
        self.assertNotIn(501, g.visible_tokens())      # raids pause after one


if __name__ == '__main__':
    unittest.main(verbosity=2)
