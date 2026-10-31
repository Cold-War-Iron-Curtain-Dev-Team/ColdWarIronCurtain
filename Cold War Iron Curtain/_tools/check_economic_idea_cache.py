"""Regression fixtures for economic idea-cache initialization and tier changes."""
import json
import re
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]

LEX = re.compile(r'#[^\r\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|==|[{}=<>!]|[^\s{}=<>!#"]+')


def parse(source):
    tokens = [m[0] for m in LEX.finditer(source) if not m[0].startswith('#')]
    i = 0

    def block(nested=False):
        nonlocal i
        out = []
        while i < len(tokens):
            key = tokens[i]
            i += 1
            if key == '}':
                assert nested
                return out
            op = tokens[i]
            i += 1
            assert op in ('=', '>', '<', '>=', '<=', '!=', '=='), (key, op)
            value = tokens[i]
            i += 1
            if value == '{':
                value = block(True)
            out.append((key, op, value))
        assert not nested
        return out
    return block()


def number(value, env):
    try:
        return float(value)
    except ValueError:
        return env['temp'].get(value, env['vars'].get(value, 0))


def condition(nodes, env):
    values = []
    for key, op, value in nodes:
        if key == 'OR':
            values.append(any(condition([n], env) for n in value))
        elif key == 'NOT':
            values.append(not condition(value, env))
        elif key == 'AND':
            values.append(condition(value, env))
        elif key == 'has_variable':
            values.append(value in env['vars'])
        elif key == 'check_variable':
            assert len(value) == 1, value
            left, compare, right = value[0]
            a, b = number(left, env), number(right, env)
            values.append({'=': a == b, '>': a > b, '<': a < b}[compare])
        else:
            raise AssertionError(('unhandled condition', key))
    return all(values)


def run(nodes, env):
    taken = False
    for key, op, value in nodes:
        if key in ('if', 'else_if', 'else'):
            if key == 'if': taken = False
            limits = [v for k, o, v in value if k == 'limit']
            eligible = not limits or condition(limits[0], env)
            if not taken and eligible:
                taken = True
                run([n for n in value if n[0] != 'limit'], env)
        elif key in ('set_variable', 'set_temp_variable'):
            taken = False
            assert len(value) == 1
            name, _, rhs = value[0]
            env['temp' if key == 'set_temp_variable' else 'vars'][name] = number(rhs, env)
        elif key == 'remove_ideas':
            taken = False
            env['ideas'].discard(value)
        elif key == 'add_ideas':
            taken = False
            env['ideas'].add(value)
        else:
            raise AssertionError(('unhandled effect', key))


def main():
    count = 0
    for kind, filename, function, variable, cache, mapping in [
        ('governance', 'CWIC_MNC_Effects.txt', 'cwic_apply_governance_stress_modifiers_country',
         'CWIC_governance_stress_tier', 'CWIC_governance_stress_tier_applied',
         {0: None, **{i: 'cwic_governance_stress_t' + str(i) for i in range(1,6)}}),
        ('inflation', 'IC_Inflation_Effect.txt', 'cwic_inflation_tier_monthly_assign',
         'CWIC_infl_tier_id', 'CWIC_infl_tier_applied',
         dict(zip([1,2,3,11,12,13,14,15,16,17,18,19,20],
             ['CWIC_infl_env_' + suffix for suffix in ['deflation_1','deflation_2','deflation_3',
              'very_stable_1','stable_2','mild_4','noticeable_8','moderate_10','high_15',
              'serious_25','crisis_50','hyper_light_100','hyper_hard_200']]))),
    ]:
        text = (MOD / 'common/scripted_effects' / filename).read_text(encoding='utf-8-sig')
        body = next(v for k,o,v in parse(text) if k == function)
        if kind == 'inflation': body = [body[-1]]
        for target, idea in mapping.items():
            for previous, old_idea in mapping.items():
                for first_run in [True, False]:
                    for scratch in [0,3,12]:
                        variables = {variable: target}
                        if not first_run: variables[cache] = previous
                        env = {'vars': variables, 'temp': {'cwic_prev_tier_tmp': scratch},
                               'ideas': {old_idea} if old_idea else set()}
                        run(body, env)
                        assert env['ideas'] == ({idea} if idea else set()), (kind,target,previous,first_run,scratch,env)
                        run(body, env)
                        assert env['ideas'] == ({idea} if idea else set())
                        count += 1
    pensions = (MOD / 'common/scripted_effects/Pensions.txt').read_text(encoding='utf-8-sig')
    assert any(k == 'increase_pensions' for k,o,v in parse(pensions))
    print(f'PASS: {count} first-run, tier-transition and repeat-call fixtures; pension effect compatibility.')


if __name__ == '__main__':
    main()
