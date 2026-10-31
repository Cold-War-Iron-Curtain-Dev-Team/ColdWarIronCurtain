"""Offline regression tests of the actual parsed WW3 scripts, not a second design.

The small interpreter covers only the native scopes/effects used by this repair.
It cannot validate engine mission scheduling, UI rendering or peace callbacks.
"""
import json
import re
import unittest
from collections import Counter
from ww3_script import ROOT, parse, pairs, one, named
from build_ww3_objectives import build

GROUPS = json.loads((ROOT/'_tools/ww3/objectives.json').read_text())['groups']
STATES = {}
for p in (ROOT/'history/states').glob('*.txt'):
    state = one(parse(p.read_text(encoding='utf-8-sig')), 'state')
    STATES[int(one(state, 'id'))] = [int(p) for p in one(state, 'provinces') if isinstance(p, str) and p.isdigit()]

TRIGGERS, EFFECTS = {}, {}
for kind, dest in [('scripted_triggers', TRIGGERS), ('scripted_effects', EFFECTS)]:
    for p in (ROOT/'common'/kind).glob('CWIC_WW3_*.txt'):
        dest.update((k, v) for k, _, v in pairs(parse(p.read_text(encoding='utf-8-sig'))))
DECISIONS = one(parse((ROOT/'common/decisions/SOV_WW3.txt').read_text(encoding='utf-8-sig')), 'SOV_WW3_decisions')
EVENTS = parse((ROOT/'events/_SOV_WW3.txt').read_text(encoding='utf-8-sig'))


class World:
    def __init__(self):
        tags = {'SOV','USA','ENG','DDR','POL','ADR','FLA','WAL','YUG','ALB','JAP','AND','ALE','XXX'}
        tags.update(a for g in GROUPS for a in g['aliases'])
        self.countries = {t: dict(flags=set(), variables={}, faction=t, subject=None, ideas=set(), exists=True, capitulated=False, stability=1., support=1.) for t in tags}
        self.countries['DDR']['faction'] = 'SOV'
        self.countries['POL']['faction'] = 'SOV'
        self.countries['ENG']['faction'] = 'USA'
        self.countries['ADR']['exists'] = False
        self.provinces = {p: 'USA' for ps in STATES.values() for p in ps}
        self.controllers = {s: 'USA' for s in STATES}
        self.global_flags = {'WW3_Started'}
        self.wars = {frozenset(('SOV','USA')), frozenset(('DDR','USA')), frozenset(('SOV','FRA'))}
        self.missions = {'SOV_WW3_Time_Limit': 37}
        self.events = []
        self.super_events = []

    def flags(self, tag='SOV'):
        return self.countries[tag]['flags']

    def occupy(self, tag, holder='SOV'):
        g = next(g for g in GROUPS if g['tag'] == tag)
        for sid in g['states']:
            self.controllers[sid] = holder
            for p in STATES[sid]:
                self.provinces[p] = holder

    def resolve(self, value, scopes, root):
        if value == 'PREV': return scopes[-2]
        if value == 'ROOT': return root
        if value == 'THIS': return scopes[-1]
        return int(value) if value.isdigit() else value

    def targets(self, key, scopes, root):
        this = scopes[-1]
        if key in self.countries or key.isdigit() or key in ('ROOT','PREV','THIS'):
            return [self.resolve(key, scopes, root)]
        if key == 'controller': return [self.controllers[this]]
        if key in ('any_country','every_country'): return [t for t,c in self.countries.items() if c['exists']]
        if key in ('any_enemy_country','every_enemy_country'):
            return [next(t for t in w if t != this) for w in list(self.wars) if this in w]
        return None

    def trigger(self, tree, scopes=('SOV',), root='SOV', mode='AND'):
        results, branch = [], False
        for k, op, v in pairs(tree):
            this = scopes[-1]
            c = self.countries.get(this)
            if k == 'tooltip': continue
            if k in ('if','else_if','else'):
                if k == 'if': branch = False
                if not branch and (k == 'else' or self.trigger(one(v,'limit'), scopes, root)):
                    branch = True
                    results.append(self.trigger([x for x in v if not isinstance(x, tuple) or x[0] != 'limit'], scopes, root))
                continue
            if k in TRIGGERS: result = self.trigger(TRIGGERS[k],scopes,root) == (v == 'yes')
            elif k in ('AND','OR','NOT'):
                result = self.trigger(v,scopes,root,'OR' if k in ('OR','NOT') else 'AND')
                if k == 'NOT': result = not result
            elif k == 'custom_trigger_tooltip': result = self.trigger(v,scopes,root)
            elif k == 'always': result = v == 'yes'
            elif k == 'original_tag': result = this == v
            elif k == 'is_in_faction_with': result = c['faction'] == self.countries[v]['faction']
            elif k == 'is_subject_of': result = c['subject'] == v
            elif k == 'has_idea': result = v in c['ideas']
            elif k == 'has_country_flag': result = v in c['flags']
            elif k == 'has_global_flag': result = v in self.global_flags
            elif k == 'country_exists': result = self.countries[v]['exists']
            elif k == 'exists': result = c['exists'] == (v == 'yes')
            elif k == 'has_capitulated': result = c['capitulated'] == (v == 'yes')
            elif k == 'has_active_mission': result = v in self.missions
            elif k == 'controls_province': result = self.provinces.get(int(v)) == this
            elif k == 'is_fully_controlled_by': result = all(self.provinces[p] == self.resolve(v,scopes,root) for p in STATES[this])
            elif k == 'check_variable':
                key, operator, value = next(x for x in pairs(v) if x[0] != 'tooltip')
                left = c['variables'].get(key,0)
                right = value if value.endswith('.id') else float(value)
                result = left == right if operator == '=' else left > right if operator == '>' else left < right
            else:
                targets = self.targets(k,scopes,root)
                if targets is None: raise AssertionError(('Unsupported trigger',k))
                result = any(self.trigger(v,scopes+(t,),root) for t in targets)
            results.append(result)
        return any(results) if mode == 'OR' else all(results)

    def effect(self, tree, scopes=('SOV',), root='SOV'):
        if isinstance(tree,str): tree = EFFECTS[tree]
        branch = False
        for k, _, v in pairs(tree):
            this = scopes[-1]
            c = self.countries.get(this)
            if k == 'limit' or k == 'custom_effect_tooltip': continue
            if k in ('if','else_if','else'):
                if k == 'if': branch = False
                if not branch and (k == 'else' or self.trigger(one(v,'limit'),scopes,root)):
                    branch = True
                    self.effect(v,scopes,root)
            elif k in EFFECTS: self.effect(EFFECTS[k],scopes,root)
            elif k == 'hidden_effect': self.effect(v,scopes,root)
            elif k == 'set_country_flag': c['flags'].add(v)
            elif k == 'clr_country_flag': c['flags'].discard(v)
            elif k == 'set_global_flag': self.global_flags.add(v)
            elif k == 'clr_global_flag': self.global_flags.discard(v)
            elif k in ('set_variable','add_to_variable'):
                key, _, value = pairs(v)[0]
                c['variables'][key] = (c['variables'].get(key,0) if k == 'add_to_variable' else 0) + float(value)
            elif k == 'activate_mission':
                if v not in self.missions: self.missions[v] = int(one(one(DECISIONS,v),'days_mission_timeout'))
            elif k == 'remove_mission': self.missions.pop(v,None)
            elif k == 'add_days_mission_timeout': self.missions[one(v,'mission')] += int(one(v,'days'))
            elif k == 'country_event': self.events.append(v if isinstance(v,str) else one(v,'id'))
            elif k == 'white_peace': self.wars.discard(frozenset((this,self.resolve(v,scopes,root))))
            elif k == 'add_stability': c['stability'] += float(v)
            elif k == 'add_war_support': c['support'] += float(v)
            elif k == 'Super_Event_Partial_SOV_Victory_Play': self.super_events.append(k)
            else:
                targets = self.targets(k,scopes,root)
                if targets is None: raise AssertionError(('Unsupported effect',k))
                for target in targets:
                    child = scopes+(target,)
                    limit = one(v,'limit')
                    if limit is None or self.trigger(limit,child,root): self.effect(v,child,root)


class CampaignTests(unittest.TestCase):
    def test_neutrals_and_participant_latching(self):
        w = World(); w.effect('cwic_ww3_refresh_objectives')
        self.assertIn('cwic_ww3_required_FRA',w.flags())
        self.assertNotIn('cwic_ww3_required_SWE',w.flags())
        w.wars.discard(frozenset(('SOV','FRA')))
        w.effect('cwic_ww3_refresh_objectives')
        self.assertIn('cwic_ww3_required_FRA',w.flags())

    def test_all_state_and_coalition_occupation(self):
        # Every single theatre and every province, including non-VP enemy pockets.
        w = World()
        for g in GROUPS:
            tag = g['tag']; w.occupy(tag,'DDR')
            self.assertTrue(w.trigger(TRIGGERS[f'cwic_ww3_{tag}_secured']))
            for sid in g['states']:
                for p in STATES[sid]:
                    w.provinces[p] = 'USA'
                    self.assertFalse(w.trigger(TRIGGERS[f'cwic_ww3_state_{sid}_secured'],(sid,)))
                    w.provinces[p] = 'SOV' # Split Soviet/allied control counts.
                    self.assertTrue(w.trigger(TRIGGERS[f'cwic_ww3_state_{sid}_secured'],(sid,)))

    def test_successor_subject_and_sphere(self):
        for holder, setup in [('ADR', 'subject'),('FLA','sphere'),('POL','faction')]:
            w = World(); c = w.countries[holder]; c['exists'] = True
            if setup == 'subject': c['subject'] = 'SOV'
            if setup == 'sphere': c['ideas'].add('Warsaw_Treaty_Organization_member'); c['variables']['Sphere_Leader'] = 'SOV.id'
            if holder == 'ADR': w.occupy('AUS',holder)
            w.occupy('FRA',holder); w.effect('cwic_ww3_campaign_tick')
            self.assertEqual(w.events,['SOVw_Third_World_War.17'])
            self.assertIn('European_is_Soviet',w.global_flags)
            self.assertNotIn('SOV_WW3_Time_Limit',w.missions)
            w.effect('cwic_ww3_campaign_tick')
            self.assertEqual(len(w.events),1)

    def test_split_control_does_not_trust_stale_state_controller(self):
        w = World(); sid = GROUPS[0]['states'][0]
        for i,p in enumerate(STATES[sid]): w.provinces[p] = 'SOV' if i%2 else 'DDR'
        self.assertEqual(w.controllers[sid],'USA')
        self.assertTrue(w.trigger(TRIGGERS[f'cwic_ww3_state_{sid}_secured'],(sid,)))

    def test_belgian_successors_reconstruct_original_theatre(self):
        w = World(); w.countries['BEL']['exists'] = False
        w.countries['FLA']['faction'] = 'USA'
        w.wars.add(frozenset(('SOV','FLA')))
        w.effect('cwic_ww3_refresh_objectives')
        self.assertIn('cwic_ww3_required_BEL',w.flags())

    def test_empty_theatre_list_is_not_victory(self):
        w = World(); self.assertFalse(w.trigger(TRIGGERS['cwic_ww3_europe_secured']))

    def test_existing_timer_preserved_and_expired_timer_recovered(self):
        w = World(); w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.missions['SOV_WW3_Time_Limit'],37)
        w.missions.clear(); w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.events,['SOVw_Third_World_War.1010'])
        self.assertFalse(w.wars)
        self.assertIn('WW3_Ended',w.global_flags)
        self.assertNotIn('WW3_Started',w.global_flags)
        w.effect('cwic_ww3_campaign_tick'); self.assertEqual(len(w.events),1)

    def test_new_campaign_gets_one_year(self):
        w = World(); w.missions.clear(); w.effect('cwic_ww3_begin_campaign')
        self.assertEqual(w.missions,{'SOV_WW3_Time_Limit':365})

    def test_conference_wins_even_if_last_enemy_already_made_peace(self):
        w = World(); w.effect('cwic_ww3_refresh_objectives'); w.occupy('FRA')
        w.wars.clear(); w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.events,['SOVw_Third_World_War.17'])

    def test_settlement_and_unrelated_wars(self):
        w = World(); w.wars.add(frozenset(('DDR','XXX')))
        w.effect('cwic_ww3_accept_european_settlement')
        self.assertEqual(w.wars,{frozenset(('DDR','XXX'))})
        self.assertNotIn('CWIC_Achievement_SOV_Won_WW3',w.global_flags)
        self.assertNotIn('European_is_Soviet',w.global_flags)
        w = World(); w.occupy('FRA'); w.effect('cwic_ww3_campaign_tick')
        w.effect('cwic_ww3_accept_european_settlement')
        self.assertIn('CWIC_Achievement_SOV_Won_WW3',w.global_flags)
        self.assertEqual(len(w.super_events),1)
        self.assertFalse(w.missions); self.assertFalse(w.wars)
        w.effect('cwic_ww3_accept_european_settlement')
        self.assertEqual(len(w.super_events),1)

    def test_red_dusk_both_requirements_and_completion(self):
        w = World(); w.effect('cwic_ww3_start_red_dusk')
        self.assertEqual(w.missions,{'SOV_Operation_Red_Dusk':765})
        w.provinces[13344] = 'DDR'
        self.assertFalse(w.trigger(TRIGGERS['cwic_ww3_north_america_secured']))
        w.flags().add('cwic_ww3_us_defeated')
        self.assertTrue(w.trigger(TRIGGERS['cwic_ww3_north_america_secured']))
        w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.events,['SOVw_Third_World_War.1000'])
        self.assertIn('Full_Soviet_Domination',w.global_flags)
        self.assertFalse(w.wars); self.assertFalse(w.missions)
        self.assertEqual(w.countries['SOV']['stability'],1.)

    def test_red_dusk_legacy_flags_and_expiry(self):
        for global_legacy in (False,True):
            w = World(); w.missions = {'SOV_Operation_Red_Dusk':123}
            (w.global_flags if global_legacy else w.flags()).add('SOV_Operation_Red_Dusk_Activated')
            w.effect('cwic_ww3_campaign_tick')
            self.assertEqual(w.missions['SOV_Operation_Red_Dusk'],123)
            self.assertIn('SOV_Operation_Red_Dusk_Activated',w.flags())
            w.missions.clear(); w.effect('cwic_ww3_campaign_tick')
            self.assertEqual(w.events,['SOVw_Third_World_War.1011'])
            self.assertEqual(w.countries['SOV']['stability'],.5)
            self.assertEqual(w.countries['SOV']['support'],.5)
            self.assertFalse(w.wars)
            w.effect('cwic_ww3_campaign_tick')
            self.assertEqual(w.countries['SOV']['stability'],.5)

    def test_actual_mission_and_conference_wiring(self):
        conference = next(v for k,_,v in pairs(EVENTS) if isinstance(v,list) and one(v,'id') == 'SOVw_Third_World_War.17')
        options = named(conference,'option')
        for name in ('SOV_WW3_Time_Limit','SOV_Operation_Red_Dusk'):
            mission = one(DECISIONS,name)
            w = World()
            if name == 'SOV_WW3_Time_Limit':
                w.occupy('FRA'); w.effect('cwic_ww3_refresh_objectives')
            else:
                w.effect('cwic_ww3_start_red_dusk')
                w.provinces[13344] = 'POL'; w.countries['USA']['capitulated'] = True
            self.assertTrue(w.trigger(one(mission,'available')))
            w.effect(one(mission,'complete_effect'))
            self.assertEqual(w.events,['SOVw_Third_World_War.17' if name == 'SOV_WW3_Time_Limit' else 'SOVw_Third_World_War.1000'])
            if name == 'SOV_WW3_Time_Limit':
                w.effect(one(options[0],'hidden_effect'))
                self.assertEqual(w.missions,{'SOV_Operation_Red_Dusk':765})
                self.assertTrue(w.wars)
            w = World(); w.effect(one(mission,'timeout_effect'))
            self.assertIn('WW3_Ended',w.global_flags)
            self.assertFalse(w.wars)
        w = World(); w.occupy('FRA'); w.effect('cwic_ww3_campaign_tick')
        w.effect(one(options[1],'hidden_effect'))
        self.assertFalse(w.wars); self.assertFalse(w.missions)

    def test_red_dusk_achieved_after_last_war_ends_still_wins(self):
        w = World(); w.effect('cwic_ww3_start_red_dusk')
        w.wars.clear(); w.provinces[13344] = 'DDR'
        w.flags().add('cwic_ww3_us_defeated')
        w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.events,['SOVw_Third_World_War.1000'])

    def test_legacy_incomplete_settlement_repairs_allied_peace(self):
        w = World(); w.global_flags.add('WW3_Ended')
        w.wars = {frozenset(('DDR','USA')),frozenset(('POL','ENG')),frozenset(('DDR','XXX'))}
        w.effect('cwic_ww3_campaign_tick')
        self.assertEqual(w.wars,{frozenset(('DDR','XXX'))})
        self.assertNotIn('WW3_Started',w.global_flags)

    def test_rome_fixed_capital_and_no_cached_arrays(self):
        w = World(); w.provinces[11846] = 'SOV' # Anzio is not Rome.
        tree = TRIGGERS['cwic_ww3_capital_ITA_secured']
        self.assertFalse(w.trigger(tree))
        w.provinces[9904] = 'POL'; self.assertTrue(w.trigger(tree))
        for g in GROUPS:
            for s in g['states']: self.assertNotIn(s,json.loads((ROOT/'_tools/ww3/objectives.json').read_text())['excluded_remote_states'])

    def test_deadline_adjustments_once_and_only_in_europe_phase(self):
        tree = parse((ROOT/'common/on_actions/WW3_on_actions.txt').read_text(encoding='utf-8-sig'))
        wrappers = []
        def visit(block):
            for k,_,v in pairs(block):
                if isinstance(v,list):
                    if k == 'if' and named(v,'add_days_mission_timeout'): wrappers.append(v)
                    visit(v)
        visit(tree)
        self.assertEqual(len(wrappers),20)
        self.assertEqual(Counter(int(one(one(v,'add_days_mission_timeout'),'days')) for v in wrappers),Counter({25:14,-15:4,40:1,5:1}))
        for block in wrappers:
            w = World(); root = 'FRA'
            delta = int(one(one(block,'add_days_mission_timeout'),'days'))
            w.effect([('if','=',block)],root=root)
            self.assertEqual(w.missions['SOV_WW3_Time_Limit'],37+delta)
            w.effect([('if','=',block)],root=root)
            self.assertEqual(w.missions['SOV_WW3_Time_Limit'],37+delta)
            w = World(); w.missions = {'SOV_Operation_Red_Dusk':321}
            w.effect([('if','=',block)],root=root)
            self.assertEqual(w.missions,{'SOV_Operation_Red_Dusk':321})


class StaticTests(unittest.TestCase):
    def test_generated_files_current_and_utf8(self):
        outputs,_ = build()
        for name,text in outputs.items():
            self.assertEqual((ROOT/name).read_text(encoding='utf-8-sig'),text,name)
            self.assertNotIn('\u00c2\u00a7',text)
            if name.endswith('.yml'): self.assertTrue((ROOT/name).read_bytes().startswith(b'\xef\xbb\xbf'))

    def test_new_trigger_effect_and_event_references(self):
        paths = [ROOT/'common/decisions/SOV_WW3.txt', ROOT/'events/_SOV_WW3.txt']
        for kind in ('scripted_effects','scripted_triggers','on_actions','scripted_localisation'):
            paths += list((ROOT/'common'/kind).glob('CWIC_WW3_*.txt'))
        definitions = set(TRIGGERS)|set(EFFECTS)
        events = parse((ROOT/'events/_SOV_WW3.txt').read_text(encoding='utf-8-sig'))
        ids = [one(v,'id') for k,_,v in pairs(events) if isinstance(v,list)]
        self.assertEqual(len(ids),len(set(ids)))
        loc_keys = set()
        for path in (ROOT/'localisation/english').glob('*.yml'):
            loc_keys.update(re.findall(r'^\s*([^\s:#]+):',path.read_text(encoding='utf-8-sig',errors='replace'),re.M))
        def visit(block):
            for k,_,v in pairs(block):
                if k.startswith('cwic_ww3_') and k not in definitions:
                    # Variables/flags are scalar values, never invoked as keys.
                    self.assertNotEqual(v,'yes',k)
                if k in ('tooltip','custom_effect_tooltip','localization_key','title','desc','name') and isinstance(v,str):
                    if v.startswith(('CWIC_WW3_','SOVw_')): self.assertTrue(v in loc_keys,v)
                if k == 'country_event' and isinstance(v,str): self.assertIn(v,ids,v)
                if isinstance(v,list): visit(v)
        for path in paths: visit(parse(path.read_text(encoding='utf-8-sig')))
        for name in ('SOV_WW3_Time_Limit','SOV_Operation_Red_Dusk','SOV_Force_Peace'):
            self.assertIn(name,loc_keys); self.assertIn(name+'_desc',loc_keys)
        for g in GROUPS:
            for sid in g['states']: self.assertTrue(f'STATE_{sid}' in loc_keys,f'STATE_{sid}')
        for k,_,v in pairs(EVENTS):
            if isinstance(v,list):
                for option in named(v,'option'): self.assertEqual(len(named(option,'name')),1,one(v,'id'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
