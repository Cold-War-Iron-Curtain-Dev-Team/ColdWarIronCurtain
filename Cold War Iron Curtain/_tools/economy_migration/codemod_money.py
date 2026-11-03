#!/usr/bin/env python3
"""
C1 money codemod (economy rework Pass 2b, docs/economy_map/PLAN.md section 4.4).

Rewrites raw treasury writes in content into the content API (docs/economy_map/API.md):
  add_to_variable/subtract_from_variable = { [SCOPE.]currentMoney = N }  ->  cwic_change_money, same amount

  python _tools/economy_migration/codemod_money.py            dry run, writes the report only
  python _tools/economy_migration/codemod_money.py --apply    rewrites the files
"""
import csv, glob, os, re, sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
REPORT = os.path.join(MOD, '..', 'docs', 'economy_map', 'codemod_money_report.csv')

CONTENT_DIRS = ['common/national_focus', 'events', 'common/decisions', 'common/scripted_effects',
                'common/on_actions', 'common/scripted_guis', 'common/ideas',
                'common/scripted_diplomatic_actions']

CORE = {os.path.normpath(p) for p in [
    'common/scripted_effects/' + f for f in (
        'IC_Econ_2024.txt IC_Economic_Scripted_Effects.txt IC_Economy_Effects.txt '
        'IC_Financial_Scripted_Effects_for_Content.txt IC_Industrial_Pulse.txt IC_Inflation_Effect.txt '
        'IC_Loans_and_Interest_Rate_Effects.txt IC_Consumer_Goods.txt consumer_goods_ai_automated_trade_effects.txt '
        'IC_Trade_Scripted_Effects.txt IC_Trade_Scripted_Effects_Cuts.txt CWIC_trade_exporter_lists.txt '
        'CWIC_Goods_Generated_Effects.txt IC_literacy_calculations.txt IC_tax_avoidance_line.txt '
        'IncomeGenerator.txt IncomeGenerator_federations.txt IncomeGenerator_ideas_and_flags.txt '
        'PolicyCostCalculator.txt StartupMoney.txt policy_focus_effects.txt CWIC_GDP_Growth_Effects.txt '
        'CWIC_Employment_Init.txt IC_State_Decisions_Effect.txt CWIC_state_category_cache.txt '
        'IC_scripted_effects.txt War_Reparation_Effects.txt').split()
] + ['common/decisions/IC_Financial_Decisions.txt', 'common/decisions/IC_Economic_Investments.txt',
     'events/Economic_Penalties.txt', 'events/IMF.txt']}

SCOPE = r'((?:[A-Za-z_][\w:]*\.)?)'
TT = r'(?:tooltip\s*=\s*\w+\s*)?'
WRITE = re.compile(r'(add_to_variable|subtract_from_variable)\s*=\s*\{\s*' + TT + r'(?:var\s*=\s*)?' + SCOPE +
                   r'currentMoney\s*=\s*(?!tooltip\b)(-?\d+(?:\.\d+)?|[A-Za-z_][\w.@^:]*)\s*' + TT + r'\}')


def main(apply):
    rows, changed = [], 0
    for d in CONTENT_DIRS:
        for path in sorted(glob.glob(os.path.join(MOD, d, '**', '*.txt'), recursive=True)):
            rel = os.path.normpath(os.path.relpath(path, MOD))
            if rel in CORE:
                continue
            raw = open(path, 'rb').read()
            bom = raw.startswith(b'\xef\xbb\xbf')
            text = raw.decode('utf-8-sig', errors='surrogateescape')
            out, last, edits = [], 0, 0
            for m in WRITE.finditer(text):
                if text.rfind('#', text.rfind('\n', 0, m.start()) + 1, m.start()) != -1:
                    continue
                op, scope, amount = m.group(1), m.group(2), m.group(3)
                negate = op == 'subtract_from_variable'
                if re.fullmatch(r'-?\d+(?:\.\d+)?', amount):
                    body = 'set_temp_variable = { money_change_temp = %s }' % ('%.6g' % (float(amount) * (-1 if negate else 1)))
                else:
                    body = 'set_temp_variable = { money_change_temp = %s }' % amount
                    if negate:
                        body += ' multiply_temp_variable = { money_change_temp = -1 }'
                body += ' cwic_change_money = yes'
                if scope:
                    body = '%s = { %s }' % (scope[:-1], body)
                rows.append([rel, text.count('\n', 0, m.start()) + 1, m.group(0), body])
                out += [text[last:m.start()], body]
                last = m.end()
                edits += 1
            if edits and apply:
                out.append(text[last:])
                open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') +
                                       ''.join(out).encode('utf-8', errors='surrogateescape'))
                changed += 1
    if rows:
        with open(REPORT, 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['file', 'line', 'original', 'replacement'])
            w.writerows(rows)
    print('%d writes in %d files%s' % (len(rows), len({r[0] for r in rows}), (', rewrote %d files' % changed) if apply else ' (dry run)'))


if __name__ == '__main__':
    main('--apply' in sys.argv)
