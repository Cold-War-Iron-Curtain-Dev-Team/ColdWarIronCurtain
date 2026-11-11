#!/usr/bin/env python3
"""News relevance tiers: who receives each broadcast (major = yes) event.

news_tiers.csv (id,tier,note) says how widely an event matters:
world / regional / local. This script writes a show_major under every
`major = yes` in events/*.txt, choosing the variant from the event script so
gameplay never changes:

  no effects            show_major = { CWIC_news_<tier> = yes }        humans only
  effects gated by tag  show_major = { OR = { CWIC_news_<tier>_fx = yes tag = X } }
  other safe effects    show_major = { CWIC_news_<tier>_fx = yes }     all AI still receive
  effects that land on  show_major = { CWIC_news_world_fx = yes }      forced world
  whoever receives it

"Safe" = the effect does the same thing no matter which country runs the
option (named scopes, global flags/variables, super events), so it still
runs via the AI receivers. Rules: common/scripted_triggers/CWIC_News_Relevance_Triggers.txt

    python _tools/news_tiers/build_news_tiers.py              apply
    python _tools/news_tiers/build_news_tiers.py --check      no writes; exit 1 if out of date
    python _tools/news_tiers/build_news_tiers.py --add-missing  label new events 'regional'
    python _tools/news_tiers/build_news_tiers.py --report     list forced-world events and why

Exits non-zero if a major event has no CSV row.
"""
import csv, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'Cold War Iron Curtain')
EVENTS = os.path.join(MOD, 'events')
CSV_PATH = os.path.join(HERE, 'news_tiers.csv')
SE_EFFECTS = os.path.join(MOD, 'common', 'scripted_effects', 'CWIC_Super_Event_Generated_Effects.txt')
TIERS = ('world', 'regional', 'local')
EVENT_KEYS = ('news_event', 'country_event', 'state_event', 'unit_leader_event', 'operative_leader_event')

# ---------------------------------------------------------------- parsing
TOKEN = re.compile(r'#[^\n]*|"(?:[^"\\]|\\.)*"|[{}=<>]|[^\s{}=<>#"]+')


def tokens(text):
    return [(m.group(0), m.start(), m.end()) for m in TOKEN.finditer(text) if not m.group(0).startswith('#')]


def parse(toks):
    """Token list -> nested [(key, op, value)], value is str or list."""
    pos = 0

    def block():
        nonlocal pos
        items = []
        while pos < len(toks):
            t = toks[pos][0]
            if t == '}':
                pos += 1; return items
            if t == '{':
                pos += 1; items.append((None, None, block())); continue
            pos += 1
            if pos < len(toks) and toks[pos][0] in '=<>':
                op = toks[pos][0]; pos += 1
                if pos < len(toks) and toks[pos][0] == '{':
                    pos += 1; items.append((t, op, block()))
                elif pos < len(toks):
                    items.append((t, op, toks[pos][0])); pos += 1
            else:
                items.append((t, None, None))
        return items
    return block()


def get(b, k):
    for kk, _, v in b:
        if kk == k: return v
    return None


def flat(b):
    out = []
    for k, op, v in b:
        if isinstance(v, list): out += ['%s%s{' % (k, op or ''), flat(v), '}']
        else: out.append('%s%s%s' % (k, op or '', '' if v is None else v))
    return ' '.join(out)


def scan(text):
    """Top-level event blocks with id, major span, show_major span, parsed body."""
    toks = tokens(text)
    depth, cur, n = 0, None, len(toks)
    for i, (t, s, e) in enumerate(toks):
        if t == '{':
            depth += 1
        elif t == '}':
            depth -= 1
            if depth == 0 and cur:
                cur['body'] = parse(toks[cur['open'] + 1:i + 1])
                yield cur
                cur = None
        elif depth == 0 and t in EVENT_KEYS and i + 2 < n and toks[i + 1][0] == '=' and toks[i + 2][0] == '{':
            cur = dict(type=t, id=None, major=None, show=None, open=i + 2)
        elif depth == 1 and cur and i + 2 < n and toks[i + 1][0] == '=':
            v = toks[i + 2]
            if t == 'id' and not cur['id']:
                cur['id'] = v[0]
            elif t == 'major' and v[0] == 'yes':
                cur['major'] = (s, v[2])
            elif t == 'show_major' and v[0] == '{':
                d, j = 0, i + 2
                while j < n:
                    if toks[j][0] == '{': d += 1
                    elif toks[j][0] == '}':
                        d -= 1
                        if d == 0: break
                    j += 1
                cur['show'] = (s, toks[j][2])

# ---------------------------------------------------------------- effect analysis
TAG = re.compile(r'^[A-Z][A-Z0-9]{2}$')
RECEIVER_REF = re.compile(r'\b(ROOT|PREV|THIS)\b')
OPTION_META = {'name', 'ai_chance', 'trigger', 'original_recipient_only', 'highlight_states', 'log'}
COSMETIC = {'play_song', 'play_sound', 'custom_effect_tooltip', 'effect_tooltip', 'mark_focus_tree_layout_dirty', 'log'}
GLOBAL_EFFECTS = {'set_global_flag', 'clr_global_flag', 'modify_global_flag'}
VAR_EFFECTS = {'set_variable', 'add_to_variable', 'subtract_from_variable', 'multiply_variable',
               'divide_variable', 'clear_variable', 'set_temp_variable', 'clamp_variable', 'round_variable'}
INDEPENDENT_TRIGGERS = {'has_global_flag', 'country_exists', 'date', 'always', 'has_dlc', 'has_game_rule',
                        'is_historical_focus_on', 'difficulty', 'threat'}
VAR_INDEPENDENT = re.compile(r'^(global\.|[A-Z][A-Z0-9]{2}\.)')
SCOPE_LOOPS = {'every_country', 'random_country', 'every_state', 'random_state'}


class ReceiverEffect(Exception):
    pass


FLAG_READS = {}   # flag -> set of reasons a read is unsafe-free: {'firer'|'own:<event id>'|'other'}
CURRENT = {'id': None}


def index_flag_reads():
    """Where is each country flag read? A read is harmless to filtering when it sits
    beside a tag/original_tag check (only that country's flag matters) or in the
    receiving event's own trigger (a receipt guard)."""
    def flags_in(b):
        out = []
        for k, _, v in b:
            if k == 'has_country_flag':
                f = v if isinstance(v, str) else (get(v, 'flag') if isinstance(v, list) else None)
                if f: out.append(f)
            elif k in ('NOT', 'AND', 'OR') and isinstance(v, list):
                out += flags_in(v)
        return out

    def walk(b, gated, own):
        here_gated = gated or any(k in ('tag', 'original_tag') and isinstance(v, str) and TAG.match(v) for k, _, v in b)
        for f in flags_in(b):
            FLAG_READS.setdefault(f, set()).add('own:' + own if own else ('firer' if here_gated else 'other'))
        for k, _, v in b:
            if isinstance(v, list) and k not in ('NOT', 'AND', 'OR'):
                # entering a new scope resets the gate; plain if/limit/trigger keep it
                keep = k in ('if', 'else_if', 'limit', 'trigger', 'available', 'allowed', 'hidden_effect', 'option', 'immediate', None)
                walk(v, here_gated and keep, own)

    for top in ('common', 'events', 'history'):
        for dp, _, fs in os.walk(os.path.join(MOD, top)):
            for f in fs:
                if not f.endswith('.txt'): continue
                tree = parse(tokens(open(os.path.join(dp, f), encoding='utf-8-sig', errors='replace').read()))
                for k, _, v in tree:
                    if not isinstance(v, list): continue
                    if k in EVENT_KEYS:
                        eid = get(v, 'id')
                        trig = get(v, 'trigger')
                        if isinstance(trig, list): walk(trig, False, eid)
                        walk([x for x in v if x[0] != 'trigger'], False, None)
                    else:
                        walk(v, False, None)


def startup_fired():
    """Event ids fired from on_startup. It runs on no country, so those events have no FROM
    and must stay world (a FROM-based filter would hide them from every player)."""
    out = set()
    def walk(b):
        for k, _, v in b:
            if k in ('news_event', 'country_event'):
                i = v if isinstance(v, str) else (get(v, 'id') if isinstance(v, list) else None)
                if i: out.add(i)
            if isinstance(v, list): walk(v)
    d = os.path.join(MOD, 'common', 'on_actions')
    for f in os.listdir(d):
        if not f.endswith('.txt'): continue
        for k, _, v in parse(tokens(open(os.path.join(d, f), encoding='utf-8-sig', errors='replace').read())):
            if isinstance(v, list):
                for k2, _, v2 in v:
                    if k2 == 'on_startup' and isinstance(v2, list): walk(v2)
    return out


def flag_safe(f):
    reads = FLAG_READS.get(f, set())
    return all(r == 'firer' or r == 'own:' + str(CURRENT['id']) for r in reads)


def tag_gate(trig):
    """[(kind, TAG)] if the trigger can only pass for those tags, else None."""
    if not isinstance(trig, list): return None
    tags = []
    for k, _, v in trig:
        if k in ('tag', 'original_tag') and isinstance(v, str) and TAG.match(v):
            tags.append((k, v))
        elif k == 'OR' and isinstance(v, list) and v and all(
                kk in ('tag', 'original_tag') and isinstance(vv, str) and TAG.match(vv) for kk, _, vv in v):
            tags += [(kk, vv) for kk, _, vv in v]
    return tags or None   # extra AND conditions only narrow further


def independent_trigger(trig):
    """True if the trigger's result does not depend on which country evaluates it."""
    for k, _, v in trig:
        if k in ('NOT', 'OR', 'AND'):
            if not (isinstance(v, list) and independent_trigger(v)): return False
        elif k in INDEPENDENT_TRIGGERS:
            continue
        elif k == 'check_variable' and isinstance(v, list) and 'global.' in flat(v):
            continue
        elif (TAG.match(k or '') or (k or '').isdigit() or k == 'FROM') and isinstance(v, list):
            if RECEIVER_REF.search(flat(v)): return False
        else:
            return False
    return True


def effects(body, tags, se_names):
    """Walk an effect block run by the receiver. Adds tag gates to `tags`;
    returns True if it has any effect; raises ReceiverEffect if an effect
    depends on which country runs it."""
    any_fx = False
    i = 0
    while i < len(body):
        k, _, v = body[i]
        i += 1
        if k in COSMETIC:
            continue
        if k == 'hidden_effect' and isinstance(v, list):
            any_fx |= effects(v, tags, se_names); continue
        if k == 'if' and isinstance(v, list):
            chain = [('if', v)]
            while i < len(body) and body[i][0] in ('else_if', 'else'):
                chain.append((body[i][0], body[i][2])); i += 1
            for kind, b in chain:
                if not isinstance(b, list): raise ReceiverEffect(kind)
                lim = get(b, 'limit') if kind != 'else' else None
                inner = [x for x in b if x[0] != 'limit']
                gate = tag_gate(lim) if lim is not None else None
                if gate and not any(x[0] == 'else' for x in chain):
                    if has_effect(inner, se_names):      # only these tags run it
                        any_fx = True; tags.update(gate)
                    continue
                sub = set()
                if not effects(inner, sub, se_names): continue
                any_fx = True
                if kind != 'else' and isinstance(lim, list) and independent_trigger(lim):
                    tags.update(sub)
                else:
                    raise ReceiverEffect(kind + ' ' + flat(lim or [])[:60])
            continue
        if k in GLOBAL_EFFECTS:
            any_fx = True; continue
        if k == 'set_country_flag':
            f = v if isinstance(v, str) else (get(v, 'flag') if isinstance(v, list) else None)
            if f and flag_safe(f):
                any_fx = True; continue
            raise ReceiverEffect('set_country_flag ' + str(f))
        if k in VAR_EFFECTS:
            if k == 'set_temp_variable': continue
            name = v if isinstance(v, str) else ((v[0][0] or '') if v else '')
            if VAR_INDEPENDENT.match(name):
                any_fx = True; continue
            raise ReceiverEffect(k + ' ' + name)
        if k in se_names and v == 'yes':
            any_fx = True; continue          # super events loop over every player themselves
        if isinstance(v, list) and (TAG.match(k or '') or (k or '').isdigit() or k == 'FROM' or k in SCOPE_LOOPS):
            if RECEIVER_REF.search(flat(v)): raise ReceiverEffect(k + ' {ROOT/PREV}')
            any_fx = True; continue          # named scope: same result whoever runs it
        raise ReceiverEffect(k)
    return any_fx


def has_effect(body, se_names):
    try:
        return effects(body, set(), se_names)
    except ReceiverEffect:
        return True


def classify(ev, se_names):
    """-> ('none', []) | ('fx', tags) | ('world', reason)"""
    gate = tag_gate(get(ev, 'trigger'))
    if gate:                                             # only these tags can receive it at all
        bodies = [get(ev, 'immediate'), get(ev, 'after')] + [[x for x in o if x[0] not in OPTION_META] for k, _, o in ev if k == 'option' and isinstance(o, list)]
        return ('fx', sorted(gate)) if any(isinstance(b, list) and has_effect(b, se_names) for b in bodies) else ('none', [])
    tags, fx = set(), False
    try:
        for key in ('immediate', 'after'):
            b = get(ev, key)
            if isinstance(b, list) and effects(b, tags, se_names): fx = True
        for k, _, opt in ev:
            if k != 'option' or not isinstance(opt, list): continue
            body = [x for x in opt if x[0] not in OPTION_META]
            gate = tag_gate(get(opt, 'trigger'))
            if gate:                                     # only these tags can pick it
                if has_effect(body, se_names): fx = True; tags.update(gate)
                continue
            sub = set()
            if not effects(body, sub, se_names): continue
            fx = True
            if get(opt, 'original_recipient_only') == 'yes':
                raise ReceiverEffect('original_recipient_only option')
            tags.update(sub)
    except ReceiverEffect as e:
        return 'world', str(e)
    return ('fx', sorted(tags)) if fx else ('none', [])


def show_major(tier, cls):
    kind, data = cls
    if kind == 'none':
        return 'show_major = { CWIC_news_%s = yes }' % tier
    if kind == 'world' or tier == 'world':
        return 'show_major = { CWIC_news_world_fx = yes }'
    if not data:
        return 'show_major = { CWIC_news_%s_fx = yes }' % tier
    gates = ' '.join('%s = %s' % kv for kv in data)
    return 'show_major = { OR = { CWIC_news_%s_fx = yes %s } }' % (tier, gates)

# ---------------------------------------------------------------- main


def read_csv():
    rows = {}
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f): rows[r['id']] = r
    return rows


def write_csv(rows):
    with open(CSV_PATH, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['id', 'tier', 'note'], lineterminator='\n')
        w.writeheader()
        for k in sorted(rows, key=lambda k: (TIERS.index(rows[k]['tier']), k.lower())):
            w.writerow({'id': k, 'tier': rows[k]['tier'], 'note': rows[k].get('note', '')})


def super_event_names():
    if not os.path.exists(SE_EFFECTS): return set()
    return set(re.findall(r'^([A-Za-z0-9_]+)\s*=\s*\{', open(SE_EFFECTS, encoding='utf-8-sig').read(), re.M))


def main():
    args = set(sys.argv[1:])
    check, add_missing, report = '--check' in args, '--add-missing' in args, '--report' in args
    rows = read_csv()
    bad = [k for k, r in rows.items() if r['tier'] not in TIERS]
    if bad:
        print('ERROR: unknown tier for', bad[:20]); return 1
    se_names = super_event_names()
    index_flag_reads()
    startup = startup_fired()

    missing, custom, changed, seen, forced = [], [], [], set(), []
    stats = {'none': 0, 'fx': 0, 'world': 0}
    for fn in sorted(os.listdir(EVENTS)):
        if not fn.endswith('.txt'): continue
        path = os.path.join(EVENTS, fn)
        raw = open(path, 'rb').read()
        bom = raw.startswith(b'\xef\xbb\xbf')
        text = raw.decode('utf-8-sig', errors='surrogateescape')
        nl = '\r\n' if '\r\n' in text else '\n'
        edits = []
        for ev in scan(text):
            if not ev['major'] or not ev['id']: continue
            eid = ev['id']; seen.add(eid)
            if eid not in rows:
                if add_missing: rows[eid] = {'id': eid, 'tier': 'regional', 'note': 'auto'}
                else: missing.append(f'{eid} ({fn})'); continue
            CURRENT['id'] = eid
            cls = ('world', 'fired from on_startup (no FROM)') if eid in startup else classify(ev['body'], se_names)
            stats[cls[0]] += 1
            if cls[0] == 'world' and rows[eid]['tier'] != 'world': forced.append((eid, fn, cls[1]))
            want = show_major(rows[eid]['tier'], cls)
            if ev['show']:
                s, e = ev['show']
                if 'CWIC_news_' not in text[s:e]:
                    custom.append(f'{eid} ({fn})'); continue
                if text[s:e] != want: edits.append((s, e, want))
            else:
                ms, me = ev['major']
                ls = text.rfind('\n', 0, ms) + 1
                indent = re.match(r'[ \t]*', text[ls:ms]).group(0) or '\t'
                edits.append((me, me, nl + indent + want))
        if edits:
            changed.append(fn)
            if not check:
                for s, e, rep in sorted(edits, reverse=True): text = text[:s] + rep + text[e:]
                open(path, 'wb').write((b'\xef\xbb\xbf' if bom else b'') + text.encode('utf-8', errors='surrogateescape'))

    if add_missing and not check: write_csv(rows)
    if report:
        print('Forced world (effects depend on the receiving country):')
        for eid, fn, why in forced: print(f'   {eid:40} {fn:40} {why}')
    stale = sorted(set(rows) - seen)
    if custom: print('NOTE: hand-written show_major kept for', len(custom), 'events:', ', '.join(custom[:10]))
    if stale: print('NOTE:', len(stale), 'CSV ids are no longer major events:', ', '.join(stale[:10]))
    if missing:
        print('ERROR:', len(missing), 'major events have no tier in news_tiers.csv (or run with --add-missing):')
        for m in missing[:40]: print('   ', m)
        return 1
    if check and changed:
        print('ERROR: show_major out of date in', len(changed), 'files; run build_news_tiers.py'); return 1
    tiers = {t: sum(1 for k in seen if rows[k]['tier'] == t) for t in TIERS}
    print('OK' if check else 'Wrote %d files.' % len(changed), 'Tiers:', tiers,
          '| no effects (humans only): %d, effects kept for AI: %d, forced world: %d' % (stats['none'], stats['fx'], len(forced)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
