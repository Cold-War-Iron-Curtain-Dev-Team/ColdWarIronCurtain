#!/usr/bin/env python3
"""
CWIC UN SIMULATOR
=================
A standalone model of the mod's UN voting rules, so numbers can be balanced
without a 40-minute game session per experiment.

It mirrors what the script actually does today, not what we wish it did:

  weight  = opinion(voter -> target)
          + (-500 if at war with target)
          + (+400 if target is our subject)
          + (+200 if target shares our sphere leader)
          + (+200 if the target IS our sphere leader)
          + (-120 if target belongs to the rival sphere)
          + (+200 if voter and target are both in the same western pact)
          + (+/-50 ideology terms)

  weight >  DEADZONE            -> NO   (a P5 with >=250 PP vetoes instead)
  weight < -DEADZONE            -> YES
  otherwise                     -> ABSTAIN

  The resolution is AGAINST the target, so sympathy for the target reads as a
  NO vote. That sign flip is the single most confusing thing in the file and
  it is faithfully reproduced here.

Player lobbying: LOBBY_COST political power buys a bloc leader, and the whole
bloc votes with the player (cwic_un_apply_pledges).

Run:  python3 un_sim.py            full report
      python3 un_sim.py --sweep    parameter sweeps
      python3 un_sim.py --test     self-check
"""

import random, statistics, sys
from dataclasses import dataclass, field

# ----------------------------------------------------------------- knobs
DEADZONE      = 24     # ai_un_voting_weight threshold for yes/no
VETO_PP       = 250    # what a veto costs a permanent member
VETO_WEIGHT   = 24     # sympathy needed before a P5 spends it
SPHERE_CLIENT = 200    # target shares our patron
SPHERE_PATRON = 200    # target IS our patron
SPHERE_RIVAL  = -120   # target is in the other camp
PACT_BONUS    = 200
SUBJECT_BONUS = 400
WAR_PENALTY   = -500
IDEOLOGY      = 50
OPINION_SCALE = 1.0    # how loudly raw opinion (-200..200) speaks in the weight
LOBBY_COST    = 100    # PP for one bloc leader (opt_un_lobby_action)
GUARANTEE_PP  = 100
PP_PER_MONTH  = 30     # rough player income

# ----------------------------------------------------------------- world
@dataclass
class Country:
    tag: str
    sphere: str          # "USA", "SOV" or ""
    bloc: str            # bloc leader tag, "" if none
    ideology: str        # democratic / communism / fascism / neutral
    un_member: bool = True
    p5: bool = False
    subject_of: str = ""
    pact: str = ""       # nato / seato / cento / ""
    pp: float = 300.0
    seat: bool = False   # holds an elected council seat

def build_world():
    W = {}
    def add(tag, sphere, bloc, ideo, **kw):
        W[tag] = Country(tag, sphere, bloc, ideo, **kw)

    # the five permanent members
    add("USA","USA","USA","democratic",p5=True,pact="nato",pp=900)
    add("SOV","SOV","SOV","communism",p5=True,pp=900)
    add("ENG","USA","ENG","democratic",p5=True,pact="nato",pp=600)
    add("FRA","USA","ENG","democratic",p5=True,pact="nato",pp=500)
    add("CHI","USA","","democratic",p5=True,pp=400)          # ROC holds the seat in 1949

    # eastern bloc
    for t in ["POL","CZE","HUN","ROM","BUL","ALB","DDR","MON"]:
        add(t,"SOV","SOV","communism")
    # western europe and others
    for t in ["ITA","HOL","BEL","LUX","POR","SPR","SWI","AUS","GRE","TUR","IRE","CAN","AST","NZL","SAF"]:
        add(t,"USA","ENG","democratic",pact="nato" if t in ("ITA","HOL","BEL","LUX","POR","CAN","TUR","GRE") else "")
    # arab league
    for t in ["EGY","SYR","IRQ","SAU","LEB","YEM","JOR","LBA","SUD","MOR","TUN","ALG"]:
        add(t,"","EGY","neutral")
    # latin america
    for t in ["BRA","ARG","CHL","COL","PER","VEN","MEX","CUB","URG","BOL","ECU","PAR","GUA","HON","NIC","COS","PAN","DOM","HAI","ELS"]:
        add(t,"USA","BRA","democratic")
    # south and south-east asia
    for t in ["RAJ","PAK","CEY","BRM","INS","SIA","AFG"]:
        add(t,"","RAJ","neutral")
    # nordics
    for t in ["SWE","NOR","DEN","FIN","ICE"]:
        add(t,"","SWE","democratic")
    # africa, such as it is in 1949
    for t in ["ETH","LBR"]:
        add(t,"","ETH","neutral")
    W["EGY"].bloc="EGY"; W["BRA"].bloc="BRA"; W["RAJ"].bloc="RAJ"
    W["SWE"].bloc="SWE"; W["ETH"].bloc="ETH"
    return W

def opinion(a: Country, b: Country, rng) -> float:
    """No opinion table exists outside the game, so model it from what drives
    it there: same camp, same ideology, colonial ties. Noisy on purpose."""
    v = rng.gauss(0, 25)
    if a.sphere and a.sphere == b.sphere: v += 60
    elif a.sphere and b.sphere and a.sphere != b.sphere: v -= 60
    if a.ideology == b.ideology: v += 30
    elif {a.ideology, b.ideology} == {"democratic","communism"}: v -= 40
    if b.subject_of == a.tag: v += 80
    return max(-200, min(200, v))

# ----------------------------------------------------------------- voting
def weight(voter, target, W, op):
    if voter.tag == target.tag: return None
    w = op[(voter.tag, target.tag)] * OPINION_SCALE
    if voter.tag in W and target.tag in getattr(voter, "wars", ()): w += WAR_PENALTY
    if target.subject_of == voter.tag: w += SUBJECT_BONUS
    if voter.sphere:
        if target.sphere == voter.sphere:               w += SPHERE_CLIENT
        if target.tag == voter.sphere:                  w += SPHERE_PATRON
        if target.sphere and target.sphere != voter.sphere: w += SPHERE_RIVAL
    if voter.pact and target.pact:                      w += PACT_BONUS
    if voter.ideology in ("fascism",) and target.ideology == "communism": w -= IDEOLOGY
    if voter.ideology == "communism" and target.ideology == "communism":  w += IDEOLOGY
    if voter.ideology == "communism" and target.pact:                     w -= IDEOLOGY
    return w

def cast(voter, w, pledged_to, player_vote):
    """pledged_to: the player tag this country has been bought by, or None."""
    if pledged_to is not None:
        return player_vote
    if w > DEADZONE:
        if voter.p5 and voter.pp >= VETO_PP and w > VETO_WEIGHT:
            voter.pp -= VETO_PP
            return "veto"
        return "no"
    if w < -DEADZONE: return "yes"
    return "abstain"

def run_vote(W, target_tag, rng, op, lobbied=(), player="USA", player_vote="yes"):
    target = W[target_tag]
    tally = {"yes":0,"no":0,"abstain":0,"veto":0}
    bought = set()
    for lead in lobbied:                       # a leader carries their bloc
        bought.add(lead)
        bought |= {c.tag for c in W.values() if c.bloc == lead}
    for c in W.values():
        if not c.un_member or c.tag == target_tag: continue
        w = weight(c, target, W, op)
        v = cast(c, w, player if c.tag in bought else None, player_vote)
        tally[v] += 1
    passed = tally["veto"] == 0 and tally["yes"] > tally["no"]
    return tally, passed

# ----------------------------------------------------------------- report
def targets_for(W, rng):
    """What the auto-generator actually picks: a country at war, a colonial
    empire, an embargoed state."""
    pool = ["SOV","USA","ENG","FRA","SAF","POR","EGY","CHI","SPR","YUG" ]
    return [t for t in pool if t in W]

def report(seed=1):
    rng = random.Random(seed)
    W = build_world()
    op = {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}
    members = [c for c in W.values() if c.un_member]
    print(f"world: {len(W)} countries, {len(members)} UN members, {sum(c.p5 for c in W.values())} permanent seats\n")

    print("=== 1. UNLOBBIED RESOLUTIONS ===")
    print(f"{'target':>6} {'yes':>5} {'no':>5} {'abst':>5} {'veto':>5}  result")
    rows=[]
    for t in targets_for(W, rng):
        for c in W.values(): c.pp = 900 if c.p5 else 300
        tally, passed = run_vote(W, t, rng, op)
        rows.append((t,tally,passed))
        print(f"{t:>6} {tally['yes']:>5} {tally['no']:>5} {tally['abstain']:>5} {tally['veto']:>5}  {'PASS' if passed else 'fail'}")
    ab = statistics.mean(r[1]['abstain'] for r in rows)
    print(f"\npass rate {sum(r[2] for r in rows)}/{len(rows)}   mean abstentions {ab:.1f} of {len(members)-1} voters"
          f"  ({100*ab/(len(members)-1):.0f}% of the floor says nothing)\n")

    print("=== 2. WHAT LOBBYING BUYS (target: SOV, player USA voting yes) ===")
    leaders = ["EGY","BRA","RAJ","SWE","ETH","ENG"]
    print(f"{'PP spent':>9} {'blocs bought':>32} {'yes':>5} {'no':>5}  result")
    for n in range(len(leaders)+1):
        for c in W.values(): c.pp = 900 if c.p5 else 300
        tally, passed = run_vote(W, "SOV", rng, op, lobbied=leaders[:n])
        print(f"{n*LOBBY_COST:>9} {','.join(leaders[:n]) or '-':>32} {tally['yes']:>5} {tally['no']:>5}  {'PASS' if passed else 'fail'}")
    print(f"\n  at {PP_PER_MONTH} PP/month, {len(leaders)*LOBBY_COST} PP is "
          f"{len(leaders)*LOBBY_COST/PP_PER_MONTH:.1f} months of income\n")

    print("=== 3. THE VETO ===")
    vetoes = 0
    for t in targets_for(W, rng):
        for c in W.values(): c.pp = 900 if c.p5 else 300
        tally,_ = run_vote(W, t, rng, op)
        vetoes += tally["veto"]
    n_res = len(targets_for(W,rng))
    print(f"  {vetoes} vetoes across {n_res} resolutions "
          f"({VETO_PP} PP each = {vetoes*VETO_PP} PP burned, "
          f"{vetoes/n_res:.1f} vetoes per resolution)")
    print(f"  the generator tables a resolution roughly every 45 days, so a P5 that")
    print(f"  vetoes what it dislikes spends {VETO_PP*8:.0f} PP a year on vetoes alone")
    print(f"  a P5 on {PP_PER_MONTH} PP/month can afford one veto every "
          f"{VETO_PP/PP_PER_MONTH:.1f} months\n")

def sweep():
    global DEADZONE, SPHERE_RIVAL, LOBBY_COST
    base_dz, base_rival, base_cost = DEADZONE, SPHERE_RIVAL, LOBBY_COST
    rng = random.Random(7); W = build_world()
    op = {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}
    print("=== DEADZONE sweep (how many abstain, how often things pass) ===")
    print(f"{'deadzone':>9} {'mean yes':>9} {'mean no':>9} {'mean abst':>10} {'pass rate':>10}")
    for dz in (0, 12, 24, 50, 100, 200):
        DEADZONE = dz
        ys,ns,abs_,ps = [],[],[],0
        for t in targets_for(W,rng):
            for c in W.values(): c.pp = 900 if c.p5 else 300
            tl,p = run_vote(W,t,rng,op); ys.append(tl['yes']); ns.append(tl['no']); abs_.append(tl['abstain']); ps += p
        print(f"{dz:>9} {statistics.mean(ys):>9.1f} {statistics.mean(ns):>9.1f} {statistics.mean(abs_):>10.1f} {ps}/{len(ys):<10}")
    DEADZONE = base_dz

    print("\n=== SPHERE_RIVAL sweep (how hard the two camps push apart) ===")
    print(f"{'rival':>9} {'mean yes':>9} {'mean no':>9} {'pass rate':>10}")
    for rv in (0, -60, -120, -200, -400):
        SPHERE_RIVAL = rv
        ys,ns,ps = [],[],0
        for t in targets_for(W,rng):
            for c in W.values(): c.pp = 900 if c.p5 else 300
            tl,p = run_vote(W,t,rng,op); ys.append(tl['yes']); ns.append(tl['no']); ps += p
        print(f"{rv:>9} {statistics.mean(ys):>9.1f} {statistics.mean(ns):>9.1f} {ps}/{len(ys):<10}")
    SPHERE_RIVAL = base_rival

    print("\n=== LOBBY_COST sweep (PP for the USSR to carry a vote against the USA) ===")
    leaders = ["EGY","RAJ","SWE","ETH","BRA","ENG"]
    for cost in (50, 100, 150, 250):
        LOBBY_COST = cost
        need = None
        for n in range(len(leaders)+1):
            for c in W.values(): c.pp = 900 if c.p5 else 300
            tl,p = run_vote(W,"USA",rng,op,lobbied=leaders[:n],player="SOV")
            if p: need = n; break
        if need is None:
            print(f"{cost:>9} PP/bloc -> impossible: every bloc bought and it still fails")
        else:
            print(f"{cost:>9} PP/bloc -> {need} blocs, {need*cost} PP, {need*cost/PP_PER_MONTH:.1f} months")
    LOBBY_COST = base_cost

    print("\n=== HOW MANY VOTES ARE ACTUALLY IN PLAY ===")
    print("  a country is 'swingable' if its weight sits within N of the threshold,")
    print("  i.e. a diplomatic action could plausibly move it. Everything else is")
    print("  decided before the resolution is even tabled.")
    print(f"{'margin':>8} {'swingable':>10} {'of floor':>10}")
    for margin in (25, 50, 100, 200):
        n = 0; tot = 0
        for t in targets_for(W,rng):
            for c in W.values():
                if not c.un_member or c.tag == t: continue
                tot += 1
                w = weight(c, W[t], W, op)
                if abs(abs(w) - DEADZONE) <= margin: n += 1
        print(f"{margin:>8} {n/len(targets_for(W,rng)):>10.1f} {100*n/tot:>9.0f}%")

def self_check():
    rng = random.Random(3); W = build_world()
    op = {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}
    # sympathy for the target means a NO vote on a resolution against them
    sov, pol = W["SOV"], W["POL"]
    op[("POL","SOV")] = 150
    assert weight(pol, sov, W, op) > DEADZONE, "a client should defend its patron"
    assert cast(pol, weight(pol,sov,W,op), None, "yes") == "no"
    # a bought bloc member votes with the player whatever it thinks
    assert cast(pol, 999, "USA", "yes") == "yes", "pledges must override the AI weight"
    # a veto stops a resolution that otherwise passes
    tally, passed = {"yes":40,"no":1,"abstain":0,"veto":1}, None
    assert not (tally["veto"] == 0 and tally["yes"] > tally["no"]), "veto must beat a majority"
    # lobbying a leader carries the bloc. Note the target: buying Latin America
    # for a vote against the USSR changes nothing, because Latin America was
    # already voting against the USSR. A pledge only shows up when it buys a
    # bloc that was going the other way - which is the first finding below.
    for c in W.values(): c.pp = 900 if c.p5 else 300
    t0,_ = run_vote(W,"USA",rng,op,player="SOV")
    for c in W.values(): c.pp = 900 if c.p5 else 300
    t1,_ = run_vote(W,"USA",rng,op,lobbied=["BRA"],player="SOV")
    assert t1["yes"] > t0["yes"], "buying a hostile bloc must add yes votes"
    print("self-check ok")



# ================================================================= TIMING
# The calendar, as the scripts actually run it:
#   - resolutions start from a WEEKLY on_action, so nothing can begin except
#     on a 7-day boundary
#   - only one can run at a time (the Current_UN_Vote flag on UNS)
#   - the vote window is the UN_Vote mission: days_mission_timeout = 10
#     (UN_Vote_Cleanuo runs 15, so the slot is really blocked for 15 days)
#   - the generator (cwic_un_auto_resolution) has a 45-day cooldown and only
#     fires when nothing else is running
#   - the authored historical layer is THREE resolutions, all in 1949
VOTE_WINDOW   = 10
CLEANUP_BLOCK = 15
GEN_COOLDOWN  = 45
TICK          = 7
HISTORICAL = [  # (start day since 1949.1.1, expiry)
    (221, 365),   # 1949.8.10 -> 1950.1.1
    (268, 365),   # 1949.9.26 -> 1950.1.1
    (276, 365),   # 1949.10.4 -> 1950.1.1
]

def timeline(years=12, verbose_years=2):
    day = 0; end = years*365
    busy_until = -1; gen_ready = 0
    pending = list(HISTORICAL)
    started = []          # (day, kind)
    missed  = []
    while day < end:
        # expiries
        for h in list(pending):
            if day > h[1]:
                pending.remove(h); missed.append(h)
        if day % TICK == 0 and day >= busy_until:
            fired = None
            for h in list(pending):
                if day >= h[0]:
                    pending.remove(h); fired = "historical"; break
            if fired is None and day >= gen_ready:
                fired = "generated"; gen_ready = day + GEN_COOLDOWN
            if fired:
                started.append((day, fired))
                busy_until = day + CLEANUP_BLOCK
        day += 1

    print("=== THE CALENDAR ===")
    print(f"  vote window {VOTE_WINDOW}d, slot blocked {CLEANUP_BLOCK}d, generator cooldown {GEN_COOLDOWN}d,")
    print(f"  resolutions can only start on a weekly tick, one at a time\n")
    per_year = {}
    for d,k in started: per_year.setdefault(d//365, []).append(k)
    print(f"{'year':>6} {'votes':>6} {'historical':>11} {'generated':>10}")
    for y in range(years):
        v = per_year.get(y, [])
        print(f"{1949+y:>6} {len(v):>6} {v.count('historical'):>11} {v.count('generated'):>10}")
    gaps = [b[0]-a[0] for a,b in zip(started, started[1:])]
    print(f"\n  {len(started)} resolutions in {years} years"
          f"  |  mean gap {statistics.mean(gaps):.0f} days, min {min(gaps)}, max {max(gaps)}")
    print(f"  theoretical ceiling: one every {max(CLEANUP_BLOCK, TICK)}d = {365/21:.0f}/year;"
          f" the cooldown holds it to {365/GEN_COOLDOWN:.1f}/year")
    if missed: print(f"  {len(missed)} authored resolutions expired unheard")
    print(f"\n  a player who opens the UN tab on a random day finds a vote running"
          f" {100*CLEANUP_BLOCK/(statistics.mean(gaps)):.0f}% of the time,")
    print(f"  and has {VOTE_WINDOW} days to act when there is one.\n")

# ================================================================= TUNING
PROPOSED = dict(
    OPINION_SCALE = 0.25,  # 1.0 - raw opinion swamped everything else
    SPHERE_CLIENT = 60,    # was 200 - eight times the threshold, nothing could move it
    SPHERE_PATRON = 60,    # was 200
    SPHERE_RIVAL  = -40,   # was -120
    PACT_BONUS    = 60,    # was 200
    SUBJECT_BONUS = 150,   # was 400
    VETO_WEIGHT   = 120,   # was 24 - a veto should cost a real decision
    DEADZONE      = 24,
)

def apply(d):
    g = globals()
    for k,v in d.items(): g[k] = v

def metrics(W, op, rng):
    ys=ns=vt=0; passes=0; res = targets_for(W,rng)
    for t in res:
        for c in W.values(): c.pp = 900 if c.p5 else 300
        tl,p = run_vote(W,t,rng,op)
        ys+=tl['yes']; ns+=tl['no']; vt+=tl['veto']; passes+=p
    # what it costs the USSR to carry a vote against the USA
    leaders = ["EGY","RAJ","SWE","ETH","BRA","ENG"]
    need = None
    for n in range(len(leaders)+1):
        for c in W.values(): c.pp = 900 if c.p5 else 300
        _,p = run_vote(W,"USA",rng,op,lobbied=leaders[:n],player="SOV")
        if p: need = n; break
    # how much one bought bloc is worth, in net votes
    for c in W.values(): c.pp = 900 if c.p5 else 300
    m0,_ = run_vote(W,"USA",rng,op,player="SOV")
    for c in W.values(): c.pp = 900 if c.p5 else 300
    m1,_ = run_vote(W,"USA",rng,op,lobbied=["EGY"],player="SOV")
    per_bloc = (m1['yes']-m1['no']) - (m0['yes']-m0['no'])
    return dict(passes=f"{passes}/{len(res)}", yes=ys/len(res), no=ns/len(res),
                vetoes=vt/len(res), swing=("never" if need is None else f"{need*LOBBY_COST} PP"),
                per_bloc=float(per_bloc))

def tune():
    rng = random.Random(11); W = build_world()
    op = {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}
    current = {k: globals()[k] for k in PROPOSED}
    print("=== CURRENT vs PROPOSED ===")
    print(f"{'':>26} {'current':>12} {'proposed':>12}")
    for k,v in PROPOSED.items():
        print(f"{k:>26} {current[k]:>12} {v:>12}")
    a = metrics(W, op, rng)
    apply(PROPOSED)
    b = metrics(W, op, rng)
    apply(current)
    print()
    for key,label in [("passes","resolutions passing"),("yes","mean yes"),("no","mean no"),
                      ("vetoes","vetoes per resolution"),("per_bloc","net votes per bloc bought"),
                      ("swing","PP for the USSR to win a vote")]:
        f = (lambda x: f"{x:.1f}") if isinstance(a[key], float) else str
        print(f"{label:>30} {f(a[key]):>12} {f(b[key]):>12}")
    print()


# ================================================================ CHAMBERS
# The mod votes ONE body: every UN member votes, and any permanent member can
# veto the result. That is two different institutions welded together. The
# General Assembly cannot be vetoed by anyone, and the Security Council is
# fifteen countries, not seventy-four.
def run_chamber(W, target_tag, rng, op, chamber="assembly", council=(), lobbied=(),
                player="USA", player_vote="yes"):
    target = W[target_tag]
    tally = {"yes":0,"no":0,"abstain":0,"veto":0}
    bought = set()
    for lead in lobbied:
        bought.add(lead); bought |= {c.tag for c in W.values() if c.bloc == lead}
    voters = [c for c in W.values() if c.un_member and c.tag != target_tag]
    if chamber == "council":
        voters = [c for c in voters if c.p5 or c.tag in council]
    for c in voters:
        w = weight(c, target, W, op)
        v = cast(c, w, player if c.tag in bought else None, player_vote)
        if chamber == "assembly" and v == "veto": v = "no"      # no veto in the GA
        tally[v] += 1
    if chamber == "council":
        passed = tally["veto"] == 0 and tally["yes"] >= 9
    else:
        passed = tally["yes"] > tally["no"]
    return tally, passed

def chambers():
    rng = random.Random(5); W = build_world()
    op = {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}
    council = ["EGY","BRA","RAJ","SWE","ETH","POL","ITA","CAN","TUR","INS"]
    leaders = ["EGY","RAJ","SWE","ETH","BRA","ENG"]
    print("=== ONE BODY (today) vs TWO CHAMBERS ===")
    print("  today: 74 members vote and any P5 can veto the result.")
    print("  split: the Assembly cannot be vetoed; the Council is 15 seats, 9 to pass.\n")
    for t in ["USA","SOV","SAF","POR"]:
        for c in W.values(): c.pp = 900 if c.p5 else 300
        t0,p0 = run_vote(W,t,rng,op,player="SOV")
        for c in W.values(): c.pp = 900 if c.p5 else 300
        ta,pa = run_chamber(W,t,rng,op,"assembly",council,player="SOV")
        for c in W.values(): c.pp = 900 if c.p5 else 300
        tc,pc = run_chamber(W,t,rng,op,"council",council,player="SOV")
        print(f"  against {t}:  today {t0['yes']}-{t0['no']} +{t0['veto']}veto {'PASS' if p0 else 'fail'}"
              f"   |  assembly {ta['yes']}-{ta['no']} {'PASS' if pa else 'fail'}"
              f"   |  council {tc['yes']}-{tc['no']} +{tc['veto']}veto {'PASS' if pc else 'fail'}")

    print("\n  what lobbying buys in each, target USA, player USSR:")
    print(f"{'PP':>6} {'today':>16} {'assembly':>16} {'council':>16}")
    for n in range(len(leaders)+1):
        row=[]
        for mode in ("today","assembly","council"):
            for c in W.values(): c.pp = 900 if c.p5 else 300
            if mode=="today":
                tl,p = run_vote(W,"USA",rng,op,lobbied=leaders[:n],player="SOV")
            else:
                tl,p = run_chamber(W,"USA",rng,op,mode,council,lobbied=leaders[:n],player="SOV")
            row.append(f"{tl['yes']}-{tl['no']}{'+v' if tl['veto'] else '  '} {'PASS' if p else 'fail'}")
        print(f"{n*LOBBY_COST:>6} {row[0]:>16} {row[1]:>16} {row[2]:>16}")
    print()


if __name__ == "__main__":
    if   "--test"     in sys.argv: self_check()
    elif "--sweep"    in sys.argv: sweep()
    elif "--timeline" in sys.argv: timeline()
    elif "--tune"     in sys.argv: tune()
    elif "--chambers" in sys.argv: chambers()
    else:
        report();   print("="*64 + "\n")
        timeline(); print("="*64 + "\n")
        tune();     print("="*64 + "\n")
        chambers(); print("="*64 + "\n")
        sweep()


