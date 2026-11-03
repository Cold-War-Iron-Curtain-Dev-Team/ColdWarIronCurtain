#!/usr/bin/env python3
"""
C1 money codemod (economy rework Pass 2b, docs/economy_map/PLAN.md section 4.4).

Rewrites raw treasury writes in content into the content API (docs/economy_map/API.md):
  add_to_variable/subtract_from_variable = { [SCOPE.]currentMoney = N }
    -> cwic_change_money_gdp_share  when the owning country is known (share = N / its 1949 GDP)
    -> cwic_change_money            otherwise (same absolute amount)

  python _tools/economy_migration/codemod_money.py            dry run, writes the report only
  python _tools/economy_migration/codemod_money.py --apply    rewrites the files
"""
import csv, glob, os, re, sys

MOD = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
HERE = os.path.dirname(os.path.abspath(__file__))
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

LATER_ERA = re.compile(r'(?i)(?:19)?[6-9]0s|19[6-9]\d|_[6-9]\d(?:s|_|\.)|[6-9]0sgeneric|Five_Year_Plan_(?:Eight|Nine|Ten|Eleven|Twelve)')
MAX_SHARE = 0.5

# Minigames with their own fixed-price economies keep absolute prices.
ABSOLUTE_FILES = {os.path.normpath(p) for p in [
    'events/CWIC_Space.txt', 'common/scripted_effects/CWIC_GDR_Card_Game_Effects.txt',
    'common/scripted_effects/IC_Malaya_Effects.txt',
]}

SCOPE = r'((?:[A-Za-z_][\w:]*\.)?)'
TT = r'(?:tooltip\s*=\s*\w+\s*)?'
LITERAL = re.compile(r'(add_to_variable|subtract_from_variable)\s*=\s*\{\s*' + TT + r'(?:var\s*=\s*)?' + SCOPE +
                     r'currentMoney\s*=\s*(-?\d+(?:\.\d+)?)\s*' + TT + r'\}')
VARIABLE = re.compile(r'(add_to_variable|subtract_from_variable)\s*=\s*\{\s*' + TT + r'(?:var\s*=\s*)?' + SCOPE +
                      r'currentMoney\s*=\s*(?!tooltip\b)([A-Za-z_][\w.@^:]*)\s*' + TT + r'\}')


def load_tags():
    tags = set()
    for f in glob.glob(os.path.join(MOD, 'common/country_tags/*.txt')):
        for line in open(f, encoding='utf-8-sig', errors='ignore'):
            m = re.match(r'\s*([A-Z][A-Z0-9]{2})\s*=', line)
            if m:
                tags.add(m.group(1))
    return tags


def load_gdp():
    with open(os.path.join(HERE, 'gdp_1949.csv'), newline='') as f:
        return {r['tag']: float(r['gdp']) for r in csv.DictReader(f)}


def file_owner(path, text, tags):
    base = os.path.basename(path)
    m = re.match(r'([A-Za-z][A-Za-z0-9]{2})[ _\-.]', base)
    if m and m.group(1).upper() in tags:
        return m.group(1).upper()
    m = re.search(r'focus_tree\s*=\s*\{.*?country\s*=\s*\{.*?(?:tag|original_tag)\s*=\s*([A-Z][A-Z0-9]{2})', text, re.S)
    if m:
        return m.group(1)
    m = re.search(r'add_namespace\s*=\s*([A-Za-z][A-Za-z0-9]{2})\b', text)
    if m and m.group(1).upper() in tags:
        return m.group(1).upper()
    return None


def fmt(x):
    return ('%.6g' % x)


def main(apply):
    tags, gdp = load_tags(), load_gdp()
    rows, changed = [], 0
    for d in CONTENT_DIRS:
        for path in sorted(glob.glob(os.path.join(MOD, d, '**', '*.txt'), recursive=True)):
            rel = os.path.normpath(os.path.relpath(path, MOD))
            if rel in CORE:
                continue
            raw = open(path, 'rb').read()
            bom = raw.startswith(b'\xef\xbb\xbf')
            text = raw.decode('utf-8-sig', errors='surrogateescape')
            owner = file_owner(rel, text, tags)
            out, last, edits = [], 0, 0
            matches = sorted([(m, 'lit') for m in LITERAL.finditer(text)] +
                             [(m, 'var') for m in VARIABLE.finditer(text)], key=lambda x: x[0].start())
            for m, kind in matches:
                if text.rfind('#', text.rfind('\n', 0, m.start()) + 1, m.start()) != -1:
                    continue
                op, scope, amount = m.group(1), m.group(2), m.group(3)
                sign = -1 if op == 'subtract_from_variable' else 1
                scope_tag = scope[:-1] if scope else ''
                target = scope_tag if re.fullmatch(r'[A-Z][A-Z0-9]{2}', scope_tag or '') else (owner if not scope else None)
                mode, value, reason = 'absolute', None, ''
                if kind == 'var':
                    reason = 'variable amount'
                    body = 'set_temp_variable = { money_change_temp = %s }' % amount
                    if sign < 0:
                        body += ' multiply_temp_variable = { money_change_temp = -1 }'
                    body += ' cwic_change_money = yes'
                else:
                    n = float(amount) * sign
                    window = text[max(0, m.start() - 3000):m.start()]
                    guarded = re.search(r'currentMoney\s*[<>]\s*' + re.escape(amount.lstrip('-')) + r'\b', window)
                    if rel in ABSOLUTE_FILES:
                        reason = 'minigame with fixed prices'
                    elif guarded:
                        reason = 'trigger checks the same amount'
                    elif not target or target not in gdp or gdp[target] <= 0.5:
                        reason = 'owner unknown' if not target else 'no 1949 GDP for ' + target
                    elif LATER_ERA.search(rel):
                        reason = 'later-era content (1949 GDP is not its reference)'
                    elif abs(n / gdp[target]) > MAX_SHARE:
                        reason = 'share above %.1f of yearly GDP' % MAX_SHARE
                    else:
                        mode, value = 'gdp_share', n / gdp[target]
                    if mode == 'gdp_share':
                        body = 'set_temp_variable = { money_change_gdp_share = %s } cwic_change_money_gdp_share = yes' % fmt(value)
                    else:
                        body = 'set_temp_variable = { money_change_temp = %s } cwic_change_money = yes' % fmt(n)
                if scope:
                    body = '%s = { %s }' % (scope[:-1], body)
                line = text.count('\n', 0, m.start()) + 1
                rows.append([rel, line, m.group(0), mode, target or '', fmt(value) if value is not None else '', reason, body])
                out.append(text[last:m.start()])
                out.append(body)
                last = m.end()
                edits += 1
            if edits and apply:
                out.append(text[last:])
                new = ''.join(out).encode('utf-8', errors='surrogateescape')
                open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + new)
                changed += 1
    os.makedirs(os.path.dirname(REPORT), exist_ok=True)
    with open(REPORT, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file', 'line', 'original', 'mode', 'owner', 'gdp_share', 'reason', 'replacement'])
        w.writerows(rows)
    modes = {}
    for r in rows:
        modes[(r[3], r[6])] = modes.get((r[3], r[6]), 0) + 1
    print('%d writes in %d files%s' % (len(rows), len({r[0] for r in rows}), (', rewrote %d files' % changed) if apply else ' (dry run)'))
    for k, v in sorted(modes.items(), key=lambda x: -x[1]):
        print('  %5d  %s%s' % (v, k[0], (' - ' + k[1]) if k[1] else ''))


if __name__ == '__main__':
    main('--apply' in sys.argv)
