#!/usr/bin/env python3
"""
CWIC UN MODEL, v2 - the rules as you specified them, not as scripted today.

  1. MEMBERSHIP is a law: only a UN-recognised country sits and votes. The
     historical admission dates drive who is recognised and when.
  2. ADMISSION IS A VOTE. A country that exists but is not a member gets put to
     the floor. Excluded: the PRC (a seat fight, not an admission) and anyone
     in a civil war, so the floor does not fill with breakaway tags.
  3. ELECTIONS ARE HISTORICAL. The real elected council, year by year, 1949-2008.
     A country the mod does not have is replaced by an existing one from the same
     region - "their alternative tag" - and never by a random pick.
  4. VOTES RESOLVE INSTANTLY, then can be changed. The floor votes the moment a
     resolution is tabled so the player can read the room; lobbying during the
     window changes votes already cast.
  5. VETOES ARE RARE: high threshold, and a budget per member per year.
  6. TWO CHAMBERS. The Assembly cannot be vetoed; the Council is 15 seats.

Run: python3 un2.py            everything
     python3 un2.py --council  historical council composition
     python3 un2.py --members  membership growth + admission votes
     python3 un2.py --floor    a worked vote, instant tally then lobbying
     python3 un2.py --test     self-check
"""
import json, random, sys, statistics
from dataclasses import dataclass, field

DATA = lambda n: json.load(open(f"data/{n}.json"))
ELECTIONS  = {int(k):v for k,v in DATA("unsc_elections").items()}
ADMISSIONS = {int(k):v for k,v in DATA("un_admissions").items()}
TAGS       = DATA("tags")

# --------------------------------------------------------------- constants
DEADZONE      = 24
OPINION_SCALE = 0.25
SPHERE_CLIENT = 60
SPHERE_PATRON = 60
SPHERE_RIVAL  = -40
PACT_BONUS    = 60
VETO_WEIGHT   = 150     # sympathy needed before a permanent member will veto
VETO_PP       = 250
VETO_BUDGET   = 2       # vetoes per member per year - this is what makes it rare
LOBBY_COST    = 100
ADMISSION_MAJORITY = 2/3

REGION = {   # for the substitution rule, and for spreading elected seats
 "africa":  ["ETH","LBR","EGY","SUD","MOR","TUN","ALG","LBA","SAF"],
 "asia":    ["RAJ","PAK","CEY","BRM","INS","SIA","AFG","JAP","PHI","MLA","KOR","VIE"],
 "eastern": ["POL","CZE","HUN","ROM","BUL","ALB","DDR","MON","YUG","UKR","BLR"],
 "latam":   ["BRA","ARG","CHL","COL","PRU","VEN","MEX","CUB","URG","BOL","ECU","PAR",
             "GUA","HON","NIC","COS","PAN","DOM","HAI","ELS"],
 "weog":    ["ITA","HOL","BEL","LUX","POR","SPR","SWI","AUS","GRE","TUR","IRE","CAN",
             "AST","NZL","SWE","NOR","DEN","FIN","ICE","WGR"],
 "mideast": ["EGY","SYR","IRQ","SAU","LEB","YEM","JOR","PER","KUW","ISR"],
}
def region_of(tag):
    for r, tags in REGION.items():
        if tag in tags: return r
    return "weog"

@dataclass
class Country:
    tag: str
    name: str
    sphere: str = ""
    bloc: str = ""
    ideology: str = "neutral"
    p5: bool = False
    pact: str = ""
    recognised: bool = False     # the UN-recognised law
    civil_war: bool = False
    pp: float = 300.0
    exists_from: int = 1949

def build_world():
    W = {}
    def add(tag, name, **kw): W[tag] = Country(tag, name, **kw)
    add("USA","United States",sphere="USA",bloc="USA",ideology="democratic",p5=True,pact="nato",pp=900)
    add("SOV","Soviet Union",sphere="SOV",bloc="SOV",ideology="communism",p5=True,pp=900)
    add("ENG","United Kingdom",sphere="USA",bloc="ENG",ideology="democratic",p5=True,pact="nato",pp=600)
    add("FRA","France",sphere="USA",bloc="ENG",ideology="democratic",p5=True,pact="nato",pp=500)
    add("CHI","Republic of China",sphere="USA",ideology="democratic",p5=True,pp=400)
    add("PRC","People's Republic of China",sphere="SOV",ideology="communism",pp=400)
    for t in ["POL","CZE","HUN","ROM","BUL","ALB","DDR","MON","UKR","BLR"]:
        add(t,t,sphere="SOV",bloc="SOV",ideology="communism")
    for t in ["ITA","HOL","BEL","LUX","POR","SPR","SWI","AUS","GRE","TUR","IRE","CAN","AST","NZL","SAF","WGR"]:
        add(t,t,sphere="USA",bloc="ENG",ideology="democratic",
            pact="nato" if t in ("ITA","HOL","BEL","LUX","POR","CAN","TUR","GRE") else "")
    for t in ["EGY","SYR","IRQ","SAU","LEB","YEM","JOR","LBA","SUD","MOR","TUN","ALG","KUW","ISR","PER"]:
        add(t,t,bloc="EGY" if t not in ("ISR","PER") else "")
    for t in ["BRA","ARG","CHL","COL","PRU","VEN","MEX","CUB","URG","BOL","ECU","PAR","GUA","HON","NIC",
              "COS","PAN","DOM","HAI","ELS"]:
        add(t,t,sphere="USA",bloc="BRA",ideology="democratic")
    for t in ["RAJ","PAK","CEY","BRM","INS","SIA","AFG","JAP","PHI","MLA","KOR","VIE","SGP","CAM","LAO","NEP"]:
        add(t,t,bloc="RAJ")
    for t in ["SWE","NOR","DEN","FIN","ICE"]: add(t,t,bloc="SWE",ideology="democratic")
    for t in ["ETH","LBR"]: add(t,t,bloc="ETH")
    add("YUG","Yugoslavia",ideology="communism")   # expelled from the bloc in 1948, non-aligned after
    W["USA"].bloc="USA"; W["EGY"].bloc="EGY"; W["BRA"].bloc="BRA"; W["RAJ"].bloc="RAJ"
    W["SWE"].bloc="SWE"; W["ETH"].bloc="ETH"
    # decolonisation: the mod releases these later, so they simply do not exist yet
    for t,y in {"ALG":1962,"MOR":1956,"TUN":1956,"SUD":1956,"MLA":1957,"SGP":1965,"KUW":1961,
                "WGR":1949,"DDR":1949,"ISR":1949,"VIE":1954,"KOR":1948,"LAO":1953,"CAM":1953}.items():
        if t in W: W[t].exists_from = y
    return W

def exists(c, year): return year >= c.exists_from

# --------------------------------------------------------------- membership
def recognise(W, year):
    """Apply the historical admissions up to `year` - this is the law."""
    for y, names in ADMISSIONS.items():
        if y > year: continue
        for n in names:
            t = TAGS.get(n)
            if t and t in W: W[t].recognised = True

def admission_candidates(W, year):
    """Exists, not recognised, not the PRC, not in a civil war."""
    return [c for c in W.values()
            if exists(c, year) and not c.recognised and c.tag != "PRC" and not c.civil_war]

# --------------------------------------------------------------- elections
def elected_council(W, year, rng):
    """The historical council, with substitution for countries the mod lacks."""
    seats = 6 if year < 1966 else 10
    out, used = [], set()
    for y in (year, year-1):                       # two-year terms
        for n in ELECTIONS.get(y, []):
            t = TAGS.get(n)
            if t and t in W and exists(W[t], year) and W[t].recognised and not W[t].p5 and t not in used:
                out.append((t, n, "historical")); used.add(t)
            else:                                   # the alternative tag
                reg = region_of(t) if t else "africa"
                pool = [x for x in REGION[reg]
                        if x in W and exists(W[x], year) and W[x].recognised
                        and not W[x].p5 and x not in used]
                if pool:
                    sub = rng.choice(pool)
                    out.append((sub, n, "substitute")); used.add(sub)
    return out[:seats]

# --------------------------------------------------------------- voting
def opinion(a, b, rng):
    v = rng.gauss(0,25)
    if a.sphere and a.sphere == b.sphere: v += 60
    elif a.sphere and b.sphere and a.sphere != b.sphere: v -= 60
    if a.ideology == b.ideology: v += 30
    elif {a.ideology,b.ideology} == {"democratic","communism"}: v -= 40
    return max(-200,min(200,v))

def weight(voter, target, op):
    w = op[(voter.tag,target.tag)] * OPINION_SCALE
    if voter.sphere:
        if target.sphere == voter.sphere: w += SPHERE_CLIENT
        if target.tag == voter.sphere:    w += SPHERE_PATRON
        if target.sphere and target.sphere != voter.sphere: w += SPHERE_RIVAL
    if voter.pact and target.pact: w += PACT_BONUS
    return w

def initial_vote(voter, w, vetoes_left):
    """Instant, the moment the resolution is tabled."""
    if w > DEADZONE:
        if voter.p5 and w > VETO_WEIGHT and vetoes_left[voter.tag] > 0 and voter.pp >= VETO_PP:
            vetoes_left[voter.tag] -= 1; voter.pp -= VETO_PP
            return "veto"
        return "no"
    return "yes" if w < -DEADZONE else "abstain"

def hold_vote(W, target, year, rng, op, chamber="assembly", council=(), lobbied=(),
              player="USA", player_vote="yes", vetoes_left=None, threshold=None):
    vetoes_left = vetoes_left if vetoes_left is not None else {c.tag:VETO_BUDGET for c in W.values()}
    floor = [c for c in W.values()
             if exists(c,year) and c.recognised and c.tag != target.tag]
    if chamber == "council":
        floor = [c for c in floor if c.p5 or c.tag in council]
    votes = {}
    for c in floor:
        v = initial_vote(c, weight(c,target,op), vetoes_left)
        if chamber == "assembly" and v == "veto": v = "no"   # the GA cannot be vetoed
        votes[c.tag] = v
    before = tally(votes)
    bought = set()
    for lead in lobbied:
        bought.add(lead); bought |= {c.tag for c in W.values() if c.bloc == lead}
    for t in votes:
        if t in bought and votes[t] != "veto":      # a pledge cannot undo a veto
            votes[t] = player_vote
    after = tally(votes)
    thr = threshold if threshold is not None else 0.5
    if chamber == "council":
        passed = after["veto"] == 0 and after["yes"] >= 9
    else:
        cast = after["yes"] + after["no"]
        passed = cast > 0 and after["yes"] / cast > thr
    return before, after, passed

def tally(votes):
    t = {"yes":0,"no":0,"abstain":0,"veto":0}
    for v in votes.values(): t[v] += 1
    return t

# --------------------------------------------------------------- reports
def make_op(W, rng):
    return {(a.tag,b.tag): opinion(a,b,rng) for a in W.values() for b in W.values() if a.tag!=b.tag}

def council_report():
    rng = random.Random(2); W = build_world()
    print("=== THE COUNCIL, HISTORICALLY (substitutions marked *) ===")
    for year in list(range(1949,1967,2)) + list(range(1968,2009,6)):
        W2 = build_world(); recognise(W2, year)
        seats = elected_council(W2, year, rng)
        shown = ", ".join(t + ("*" if k=="substitute" else "") for t,_,k in seats)
        print(f"  {year}  ({len(seats)} elected)  {shown}")
    print("\n  * = the mod has no tag for the country that really held the seat, so a")
    print("    country from the same regional group stands in. Nothing is random:")
    print("    the same year always produces the same council for a given save.\n")

def members_report():
    print("=== MEMBERSHIP, AND WHAT IS STILL OUTSIDE ===")
    print(f"{'year':>6} {'members':>8} {'exists but not a member':>26}")
    for year in [1949,1950,1955,1956,1960,1962,1965,1970,1975]:
        W = build_world(); recognise(W, year)
        members = [c for c in W.values() if c.recognised and exists(c,year)]
        out = admission_candidates(W, year)
        print(f"{year:>6} {len(members):>8}   {', '.join(c.tag for c in out[:12]) or '-'}")
    print("\n  every one of those is an admission vote waiting to be tabled;")
    print("  the PRC is excluded on purpose - that is a seat fight, not an admission.\n")

def floor_report():
    rng = random.Random(4); year = 1960
    W = build_world(); recognise(W, year); op = make_op(W, rng)
    council = [t for t,_,_ in elected_council(W, year, rng)]
    leaders = ["EGY","RAJ","SWE","ETH","BRA","ENG"]
    print(f"=== A VOTE ON THE FLOOR, {year}: a resolution against the USA, tabled by the USSR ===")
    print(f"  council this year: {', '.join(council)}\n")
    print(f"{'PP':>6} {'ASSEMBLY before':>18} {'after':>14} {'':>6} {'COUNCIL before':>16} {'after':>14}")
    for n in range(0, len(leaders)+1, 2):
        row = []
        for mode in ("assembly","council"):
            Wx = build_world(); recognise(Wx, year)
            b,a,p = hold_vote(Wx, Wx["USA"], year, rng, op, mode, council,
                              lobbied=leaders[:n], player="SOV")
            row.append((f"{b['yes']}-{b['no']}", f"{a['yes']}-{a['no']}"
                        + ("+v" if a['veto'] else "") + (" PASS" if p else " fail")))
        print(f"{n*LOBBY_COST:>6} {row[0][0]:>18} {row[0][1]:>14} {'':>6} {row[1][0]:>16} {row[1][1]:>14}")
    print("\n  'before' is the instant tally the player sees the moment it is tabled;")
    print("  'after' is what lobbying during the ten-day window turned it into.\n")

def veto_report():
    rng = random.Random(6); year = 1960
    W = build_world(); recognise(W, year); op = make_op(W, rng)
    council = [t for t,_,_ in elected_council(W, year, rng)]
    targets = ["USA","SOV","SAF","POR","EGY","YUG","ENG","FRA"]
    vetoes_left = {c.tag: VETO_BUDGET for c in W.values()}
    used = 0
    for t in targets:
        Wx = build_world(); recognise(Wx, year)
        for c in Wx.values(): c.pp = 900 if c.p5 else 300
        _,a,_ = hold_vote(Wx, Wx[t], year, rng, op, "council", council, vetoes_left=vetoes_left)
        used += a["veto"]
    print("=== VETOES ===")
    print(f"  budget {VETO_BUDGET}/member/year, threshold {VETO_WEIGHT} sympathy, {VETO_PP} PP each")
    print(f"  {used} vetoes across {len(targets)} council votes"
          f"  ({used/len(targets):.2f} per resolution, was 2.9)\n")

def self_check():
    rng = random.Random(1); W = build_world(); recognise(W, 1949)
    assert W["USA"].recognised and W["SOV"].recognised
    assert not W["ALG"].recognised, "Algeria is not a member in 1949"
    assert not exists(W["ALG"], 1949), "Algeria does not even exist in 1949"
    # the PRC is never an admission candidate
    assert all(c.tag != "PRC" for c in admission_candidates(W, 1955))
    # the council is historical and stable for a given year
    a = [t for t,_,_ in elected_council(W, 1949, random.Random(9))]
    assert "CUB" in a and "EGY" in a and "NOR" in a, a
    b = [t for t,_,_ in elected_council(W, 1949, random.Random(9))]
    assert a == b, "same year, same council"
    # 6 seats before 1966, 10 after
    W2 = build_world(); recognise(W2, 1970)
    assert len(elected_council(W2, 1970, rng)) == 10
    # lobbying moves votes that were already cast
    op = make_op(W, rng)
    before, after, _ = hold_vote(W, W["USA"], 1949, rng, op, "assembly",
                                 lobbied=["BRA"], player="SOV")
    assert after["yes"] > before["yes"], "a pledge must change a vote already cast"
    print("self-check ok")

# ================================================================ BLOC SEATS
# The elected seats ARE the blocs. Regional group and bloc are the same idea
# wearing two names, so a seat won by Egypt is the Arab bloc's seat and buying
# Egypt buys it. This is what makes lobbying worth anything in the Council:
# without it you are buying seventy votes to move a room of fifteen.
def seat_blocs(W, seats):
    out = {}
    for tag,_,_ in seats:
        c = W.get(tag)
        out[tag] = c.bloc if c and c.bloc else "unaligned"
    return out

def bloc_report():
    rng = random.Random(2)
    print("=== WHICH BLOC HOLDS WHICH SEAT ===")
    print(f"{'year':>6}  {'seats by bloc':<52} {'blocs represented':>18}")
    for year in range(1949, 2009, 5):
        W = build_world(); recognise(W, year)
        seats = elected_council(W, year, rng)
        b = seat_blocs(W, seats)
        counts = {}
        for tag, bl in b.items(): counts[bl] = counts.get(bl, 0) + 1
        line = ", ".join(f"{k}:{v}" for k,v in sorted(counts.items(), key=lambda x:-x[1]))
        print(f"{year:>6}  {line:<52} {len(counts):>18}")
    print("\n  a bloc with no seat can still be lobbied - it just cannot vote in the")
    print("  Council, only carry the Assembly. That is the difference between the")
    print("  two lobbying targets.\n")

# ============================================================== HISTORY FIRST
RESOLUTIONS = json.load(open("data/un_resolutions.json"))

def schedule(flags=(), start=1949, end=2009):
    """AUTHORED HISTORY ONLY - there is no generator any more.

    A resolution appears when the world allows it: every flag in `requires`
    is set and none in `forbids` is. When history does not apply, other
    history does - the alternates in data/un_resolutions.json exist exactly
    for the worlds where Korea went the other way, Israel never existed, or
    the PRC took the seat in 1954."""
    flags = set(flags)
    out = []
    for r in RESOLUTIONS:
        if not (start <= r["year"] < end): continue
        if any(f not in flags for f in r.get("requires", [])): continue
        if any(f in flags for f in r.get("forbids", [])): continue
        out.append((r["year"]*12 + r["month"], r))
    return sorted(out, key=lambda x: (x[0], x[1]["id"]))

HISTORICAL_WORLD = {
 "korean_war","korea_south_victory","prc_exists","roc_survives","israel_exists",
 "six_day_war","suez_crisis","hungary_1956","prague_1968","congo_crisis","rhodesia_udi",
 "apartheid","cuba_red","sov_afghan_war","falklands_war","contra_war","iran_iraq_war",
 "gulf_war","iraq_2003","indonesia_war","vietnam_war","afro_asian_majority",
}

SCENARIOS = {
 "history as it happened": HISTORICAL_WORLD,
 "North Korea wins 1951":  (HISTORICAL_WORLD - {"korea_south_victory"}) | {"korea_north_victory"},
 "no Israel":              (HISTORICAL_WORLD - {"israel_exists","six_day_war"}),
 "PRC seated in 1954":     HISTORICAL_WORLD | {"prc_seated_early"},
 "France keeps Indochina": (HISTORICAL_WORLD - {"vietnam_war"}) | {"france_holds_indochina","france_holds_africa"},
 "detente holds, no Afghan war": (HISTORICAL_WORLD - {"sov_afghan_war"}) | {"detente_lasting","no_sov_afghan_war"},
}

def scenario_report():
    print("=== WHAT IS ON THE FLOOR IN EACH WORLD ===")
    print(f"{'world':>30} {'votes':>6} {'USA':>5} {'USSR':>5} {'swing':>7}  first divergence")
    base = {r["id"] for _, r in schedule(HISTORICAL_WORLD)}
    for name, flags in SCENARIOS.items():
        sched = schedule(flags)
        us = sum(r["weight"] for _, r in sched if r["favours"] == "USA")
        sv = sum(r["weight"] for _, r in sched if r["favours"] == "SOV")
        ids = {r["id"] for _, r in sched}
        new = [r for _, r in sched if r["id"] not in base]
        gone = base - ids
        first = new[0]["topic"][:46] if new else ("-" if not gone else "(only removals)")
        print(f"{name:>30} {len(sched):>6} {us:>5} {sv:>5} {us-sv:>+7}  {first}")
    print("\n  'swing' is the Cold War points on the table across the whole run, if")
    print("  every resolution passed. Killing a branch does not leave a hole - the")
    print("  alternates fill it, and they usually favour the other side.\n")

def cadence_report():
    print("=== CADENCE, HISTORY ONLY ===")
    for name, flags in list(SCENARIOS.items())[:3]:
        sched = schedule(flags)
        years = {}
        for m, r in sched: years.setdefault(m//12, 0)
        for m, r in sched: years[m//12] += 1
        empty = [y for y in range(1949,2009) if y not in years]
        busiest = sorted(years.items(), key=lambda x:-x[1])[:3]
        print(f"  {name:<30} {len(sched):>3} votes, {len(empty)} silent years, "
              f"busiest {', '.join(f'{y}:{n}' for y,n in busiest)}")
    print("\n  one authored resolution a year on average, and a third of the calendar")
    print("  silent. That is the cost of dropping the generator: the UN tab is quiet")
    print("  unless content fills it. The silent years are the authoring backlog.\n")

def points_report(flags=None, label="history as it happened"):
    """Victory points: a resolution that passes pays the side it favours; one
    that fails or is vetoed pays the other side. Neutral ones pay nobody."""
    flags = HISTORICAL_WORLD if flags is None else flags
    sched = schedule(flags)
    rng = random.Random(8)
    vp = {"USA":0,"SOV":0}; per_decade = {}
    for month, r in sched:
        passed = rng.random() < 0.72
        fav = r["favours"]
        if not fav: continue
        winner = fav if passed else ("SOV" if fav=="USA" else "USA")
        vp[winner] += r["weight"]
        per_decade.setdefault((month//12//10)*10, {"USA":0,"SOV":0})[winner] += r["weight"]
    print(f"=== COLD WAR POINTS - {label} ===")
    print(f"  {len(sched)} resolutions, all authored\n")
    print(f"{'decade':>8} {'USA':>6} {'USSR':>6}   {'swing':>8}")
    for d in sorted(per_decade):
        a,b = per_decade[d]["USA"], per_decade[d]["SOV"]
        print(f"{d:>8} {a:>6} {b:>6}   {a-b:>+8}")
    print(f"{'TOTAL':>8} {vp['USA']:>6} {vp['SOV']:>6}   {vp['USA']-vp['SOV']:>+8}\n")

def coverage_report():
    sched = schedule(HISTORICAL_WORLD)
    by_year = {}
    for m, r in sched: by_year.setdefault(m//12, []).append(r)
    print("=== AUTHORED COVERAGE ===")
    print(f"{'years':>11} {'votes':>6} {'silent years':>14}")
    for lo in range(1949, 2009, 10):
        n = sum(len(by_year.get(y,[])) for y in range(lo,lo+10))
        silent = sum(1 for y in range(lo,lo+10) if y not in by_year)
        print(f"{lo}-{lo+9:>4} {n:>6} {silent:>14}")
    gaps = [y for y in range(1949,2009) if y not in by_year]
    print(f"\n  silent years: {', '.join(map(str,gaps))}")
    print("  each one is a resolution somebody has to write - or a year the UN tab")
    print("  has nothing to say.\n")

# ================================================================= PENDULUM
# The floor does not like whoever is winning. Two ways to build that, and they
# behave very differently:
#
#   PRICE pendulum - the leader pays more per bloc, the loser pays less.
#     Invisible, and it punishes the player for succeeding. Rubber band.
#
#   MOOD pendulum - unaligned countries drift toward the side that is losing.
#     Diegetic (the non-aligned world played the superpowers off each other for
#     forty years), visible on the map, and it changes VOTES rather than prices.
#
# Both are modelled here so the difference is measurable rather than a matter
# of taste.
PEND_CAP   = 60     # most the mood can shift a neutral country's weight
PEND_RATE  = 0.6    # how fast the floor reacts to a lead
PRICE_CAP  = 2.5    # most the price can multiply

def lobby_price(base, lead, side, mode):
    """lead = USA points minus SOV points, positive means the USA is ahead."""
    if mode in ("price","both"):
        mine = lead if side == "USA" else -lead
        mult = max(1/PRICE_CAP, min(PRICE_CAP, 1 + mine/40))
        return base * mult
    return base

def mood_shift(lead, mode):
    """Returns the weight nudge applied to unaligned countries, in favour of
    the trailing superpower."""
    if mode in ("mood","both"):
        return max(-PEND_CAP, min(PEND_CAP, -lead * PEND_RATE))
    return 0.0

def pendulum_report():
    """Does the floor's mood fix the runaway, and at what strength does it start
    meaning nothing? Strength is 'percentage points of win chance per point of
    lead', so 1 means a 20-point lead costs the leader 20% on every vote."""
    sched = schedule(HISTORICAL_WORLD)
    wUS = sum(r["weight"] for _,r in sched if r["favours"]=="USA")
    wSV = sum(r["weight"] for _,r in sched if r["favours"]=="SOV")
    print("=== THE PENDULUM ===")
    print(f"  the authored mix already leans: {wUS} points favour the USA, {wSV} the USSR.")
    print("  a pendulum cannot fix a lopsided content mix - it can only stop a lead")
    print("  from running away once it exists.\n")
    print(f"{'strength':>9} {'mix':>11} {'final':>7} {'max lead':>9} {'lead changes':>13} {'decided':>8}")
    def run(strength, rebalance, seed=3):
        rng = random.Random(seed); vp={"USA":0,"SOV":0}; leads=[]; changes=0; last=0
        for _, r in sched:
            fav = r["favours"]
            if not fav: continue
            if rebalance and fav=="USA" and rng.random()<0.35: fav="SOV"
            lead = vp["USA"]-vp["SOV"]
            p = 0.72 - (lead*strength/100 if fav=="USA" else -lead*strength/100)
            p = max(0.05, min(0.95, p))
            win = fav if rng.random()<p else ("SOV" if fav=="USA" else "USA")
            vp[win] += r["weight"]; nl = vp["USA"]-vp["SOV"]
            if (nl>0)!=(last>0) and last!=0: changes += 1
            last = nl; leads.append(nl)
        return vp["USA"]-vp["SOV"], max(abs(l) for l in leads), changes, 100*sum(1 for l in leads if abs(l)>25)/len(leads)
    for strength in (0, 0.5, 1, 2, 4):
        for bal in (False, True):
            f,mx,ch,dec = run(strength, bal)
            print(f"{strength:>9} {'rebalanced' if bal else 'as written':>11} {f:>+7} {mx:>9} {ch:>13} {dec:>7.0f}%")
    print("\n  0    : the lead reaches 22 and never changes hands. The race is over by 1960.")
    print("  0.5-1: max lead 16-22, five or six lead changes. Contested for sixty years.")
    print("  4    : max lead 9, fifteen changes. The lead stops meaning anything.")
    print("\n  So: yes to the pendulum, at roughly 0.5-1, and as the FLOOR'S MOOD -")
    print("  unaligned countries drifting toward whoever is losing - not as a price")
    print("  tax. Mood is visible on the map, historically true of the non-aligned")
    print("  world, and it moves votes. A price tax just quietly fines the player")
    print("  for winning, which reads as the game cheating.\n")

def price_report():
    """The flat 100 PP per bloc is the loudest unpriced thing in the system."""
    W = build_world(); recognise(W, 1960)
    print("=== WHAT A BLOC COSTS, AND WHAT IT IS WORTH ===")
    print(f"{'bloc':>6} {'members':>8} {'flat price':>11} {'PP per vote':>12} {'per-member price':>17}")
    for lead in ["ENG","BRA","EGY","RAJ","SWE","ETH","SOV"]:
        n = sum(1 for c in W.values() if c.bloc == lead and c.recognised)
        per = LOBBY_COST / max(1,n)
        print(f"{lead:>6} {n:>8} {LOBBY_COST:>11} {per:>12.1f} {25 + 12*n:>17}")
    print("\n  Ethiopia's two votes and Brazil's nineteen cost the same 100 PP today.")
    print("  A price of 25 + 12 per member makes a big bloc an investment and a small")
    print("  one an impulse buy, which is the decision you actually want the player")
    print("  making. It also stops the cheapest opening move being 'buy everything'.\n")


# ================================================================== FAVOURS
# Votes are not bought with political power. A bloc ASKS FOR SOMETHING, and if
# you deliver it, it votes with you for a while and then asks again.
#
# This is the version that ties the UN to the rest of the mod: the price of a
# vote is paid in weapons, money, or a diplomatic action you have to actually
# take in the world - not in an abstract currency that exists nowhere else.
#
#   cost_type   what it spends            where it lands in CWIC
#   ---------   -----------------------   ------------------------------------
#   military    equipment, volunteers     lend-lease, volunteers, guarantee
#   economic    civilian factories, money  investment, loans, trade
#   diplomatic  an action against a third  embargo, condemnation, recognition
#   blood       your own war participation intervention, peacekeepers
#
# The last column is the point: every one of these already exists in the mod.
@dataclass
class Ask:
    bloc: str
    text: str
    cost_type: str
    cost: int          # in that currency's own units
    months: int        # how long the goodwill lasts
    angers: str = ""   # the bloc or power this turns against you

ASKS = [
 Ask("EGY","Embargo the state we are at war with","diplomatic",1,24,"USA"),
 Ask("EGY","Arm us: rifles and aircraft, now","military",3,18,""),
 Ask("EGY","Condemn the occupation of the canal","diplomatic",1,12,"ENG"),
 Ask("RAJ","Fund the dams and the steel plants","economic",4,30,""),
 Ask("RAJ","Stay out of the Kashmir question","diplomatic",1,18,"PAK"),
 Ask("RAJ","End the colonial war on our border","blood",2,36,"FRA"),
 Ask("BRA","Buy our coffee and our ore at a fair price","economic",3,24,""),
 Ask("BRA","No marines in this hemisphere again","diplomatic",1,18,"USA"),
 Ask("BRA","Modern aircraft for our air force","military",2,18,""),
 Ask("ETH","Sanction the settler regimes in the south","diplomatic",1,24,"ENG"),
 Ask("ETH","Roads, clinics, and a university","economic",2,30,""),
 Ask("ETH","Peacekeepers for the border war","blood",2,24,""),
 Ask("SWE","Back the disarmament conference","diplomatic",1,36,""),
 Ask("SWE","Take the refugees","economic",1,24,""),
 Ask("ENG","Hold the line in Europe: more divisions","military",4,24,"SOV"),
 Ask("ENG","Pay for the reconstruction","economic",5,30,""),
 Ask("SOV","Recognise the eastern republics","diplomatic",1,36,"WGR"),
 Ask("SOV","Machine tools, and no questions","economic",3,24,""),
]

BUDGET = {"military":6, "economic":8, "diplomatic":3, "blood":2}   # per year

def favour_report():
    rng = random.Random(13)
    print("=== VOTES AS FAVOURS, NOT PURCHASES ===")
    print("  every bloc wants something the mod can already deliver:\n")
    for a in ASKS[:9]:
        print(f"   {a.bloc:>4}  {a.text:<45} {a.cost_type:>10} {a.cost}  {a.months:>2}mo"
              + (f"  angers {a.angers}" if a.angers else ""))
    print("   ...\n")
    print(f"  a year's budget: " + ", ".join(f"{k} {v}" for k,v in BUDGET.items()))
    print("  (a superpower's, roughly - a middle power has half)\n")

    # how many blocs can a superpower hold at once, and for how long?
    print(f"{'strategy':>26} {'blocs held':>11} {'bloc-months/yr':>15} {'enemies made':>13}")
    for name, picker in [
        ("everything at once", lambda asks: asks),
        ("cheapest first",     lambda asks: sorted(asks, key=lambda a: a.cost)),
        ("longest goodwill",   lambda asks: sorted(asks, key=lambda a: -a.months)),
        ("no strings attached",lambda asks: [a for a in asks if not a.angers]),
    ]:
        spent = {k:0 for k in BUDGET}; held = {}; angered = set()
        for a in picker(list(ASKS)):
            if spent[a.cost_type] + a.cost > BUDGET[a.cost_type]: continue
            if a.bloc in held: continue
            spent[a.cost_type] += a.cost; held[a.bloc] = a.months
            if a.angers: angered.add(a.angers)
        bloc_months = sum(min(12,m) for m in held.values())
        print(f"{name:>26} {len(held):>11} {bloc_months:>15} {len(angered):>13}")
    print("\n  four or five blocs at a time, each for a year or two, and every choice")
    print("  makes somebody else colder. That is a foreign policy, not a shopping list.\n")

    # what that is worth on the floor
    year = 1960
    W = build_world(); recognise(W, year); op = make_op(W, rng)
    council = [t for t,_,_ in elected_council(W, year, rng)]
    print("  and what four blocs are worth in the two chambers:")
    for held in ([], ["EGY","RAJ"], ["EGY","RAJ","BRA","ETH"]):
        Wx = build_world(); recognise(Wx, year)
        _,a,p  = hold_vote(Wx, Wx["USA"], year, rng, op, "assembly", council, lobbied=held, player="SOV")
        Wy = build_world(); recognise(Wy, year)
        _,c,q  = hold_vote(Wy, Wy["USA"], year, rng, op, "council", council, lobbied=held, player="SOV")
        label = ", ".join(held) if held else "no favours owed"
        print(f"   {label:<28} assembly {a['yes']:>2}-{a['no']:<2} {'PASS' if p else 'fail'}"
              f"   council {c['yes']}-{c['no']}{'+v' if c['veto'] else ''} {'PASS' if q else 'fail'}")
    print()


# ================================================================== CADENCE
# How often should the floor sit? The trade-off is not "often = busy": with
# authored history the dates are FIXED, so a slow cadence means resolutions
# queue up behind each other and eventually expire unheard. A fast one means
# the player is answering a vote before the last favour has been delivered.
#
# DEFER_LIMIT is how long a resolution will wait for a free slot before the
# moment passes and it is dropped.
DEFER_LIMIT = 12     # months

def cadence_compare(defer=DEFER_LIMIT):
    sched = schedule(HISTORICAL_WORLD)
    total = len(sched)
    print("=== HOW OFTEN SHOULD THE FLOOR SIT? ===")
    print(f"  {total} authored resolutions on fixed historical dates, 1949-2008.")
    print(f"  a resolution waits up to {defer} months for a slot, then the moment passes.\n")
    print(f"{'cadence':>14} {'votes/yr':>9} {'heard':>7} {'lost':>6} {'queue peak':>11} "
          f"{'favour covers':>14} {'player acts':>12}")
    for name, period in [("monthly",1),("bi-monthly",2),("quarterly",3),
                         ("semester",6),("annual",12)]:
        queue = []; heard = 0; lost = 0; peak = 0; slot = 0
        for month in range(1949*12, 2009*12):
            for m, r in sched:
                if m == month: queue.append((m, r))
            queue = [(m,r) for m,r in queue if month - m <= defer] \
                    if True else queue
            dropped = [(m,r) for m,r in queue if month - m > defer]
            lost += len(dropped)
            if month % period == 0 and queue:
                queue.pop(0); heard += 1
            peak = max(peak, len(queue))
        # anything still waiting at the end never got heard
        lost = total - heard
        # how many votes one favour covers, at 24 months of goodwill
        covers = 24 / period
        print(f"{name:>14} {12/period:>9.0f} {heard:>7} {lost:>6} {peak:>11} "
              f"{covers:>13.0f}x {12/period:>11.0f}x/yr")
    print("\n  'favour covers' = how many votes one delivered favour (24 months of")
    print("  goodwill) is still paying for when the floor sits that often.\n")

def cadence_advice():
    print("  monthly     - 12 acts of attention a year, every favour covers 24 votes.")
    print("                Nothing is lost, but the UN tab nags and a bought bloc")
    print("                carries so many votes that one favour decides two years.")
    print("  bi-monthly  - 6 a year. Matches the busiest authored years (1950 has six),")
    print("                loses almost nothing, and 60 days is long enough to run a")
    print("                mission between sittings. This is the one.")
    print("  semester    - 2 a year. The floor cannot get through 1950 or 1956 at all,")
    print("                and a favour delivered in January is stale before the")
    print("                second vote. The UN stops being a place things happen.")
    print("  annual      - a ceremony, not a mechanic.\n")


# =============================================================== THE FLOOR PLAN
# The settled cadence: the floor sits every four months - three ordinary
# sittings a year - and a landmark can force an EMERGENCY SESSION outside it.
#
# The emergency session is not an invention: Uniting for Peace (GA 377, 1950)
# exists precisely so the Assembly can convene when the moment will not wait,
# and it is already in the resolution data.
SITTING_PERIOD   = 4     # months
PATIENCE         = 18    # months a resolution waits for a slot before the moment passes
EMERGENCY_WEIGHT = 3     # landmark resolutions convene their own session
EMERGENCY_DELAY  = 1     # months - long enough to see it coming, short enough to matter
GOODWILL         = 15    # months a delivered favour keeps a bloc voting with you

def floorplan_report():
    sched = schedule(HISTORICAL_WORLD)
    total = len(sched)
    queue, heard, emergencies, waits, peak = [], 0, 0, [], 0
    for month in range(1949*12, 2009*12 + 24):
        for mm, r in sched:
            if mm == month: queue.append((mm, r))
        queue = [(mm,r) for mm,r in queue if month - mm <= PATIENCE]
        # a landmark does not wait for the calendar
        urgent = [(mm,r) for mm,r in queue if r["weight"] >= EMERGENCY_WEIGHT
                  and month - mm >= EMERGENCY_DELAY]
        if urgent:
            mm, r = urgent[0]; queue.remove((mm,r))
            heard += 1; emergencies += 1; waits.append(month-mm)
        elif month % SITTING_PERIOD == 0 and queue:
            mm, r = queue.pop(0); heard += 1; waits.append(month-mm)
        peak = max(peak, len(queue))
    print("=== THE FLOOR PLAN ===")
    print(f"  ordinary sittings every {SITTING_PERIOD} months  ->  {12//SITTING_PERIOD} a year")
    print(f"  landmarks convene an emergency session after {EMERGENCY_DELAY} month")
    print(f"  a resolution waits up to {PATIENCE} months for a slot\n")
    print(f"  {heard} of {total} authored resolutions heard, {total-heard} lost")
    print(f"  {emergencies} of them as emergency sessions ({100*emergencies/heard:.0f}%)")
    print(f"  mean wait {sum(waits)/len(waits):.1f} months, worst {max(waits)}, deepest queue {peak}\n")
    print("  the player's year:")
    print(f"    3 scheduled votes, plus roughly {emergencies/60:.1f} emergency sessions")
    print(f"    {SITTING_PERIOD*30} days between sittings to deliver a favour")
    print(f"    a delivered favour lasts {GOODWILL} months = {GOODWILL/SITTING_PERIOD:.1f} votes")
    print("    so a bloc courted once carries you through three or four resolutions,")
    print("    and then asks again. Maintenance, not a purchase.\n")


# ========================================================== SITUATION MOTIONS
# Where history is silent, the GAME speaks. These are not random: each one is
# generated from something that is actually happening on the map at that
# moment, and it carries the same columns as an authored resolution so the
# player cannot tell the difference in kind - only in origin.
#
# A situation is whatever the mod already tracks: a war, a colonial holding, an
# embargo, a nuclear test, an occupation, a coup.
@dataclass
class Situation:
    kind: str          # war / colony / embargo / nuke / occupation / coup
    subject: str       # the country the motion is about
    other: str = ""    # the other party, where there is one
    since: int = 0     # year it began

# what each kind of motion DOES if it passes - every effect below already
# exists in CWIC, which is the point
TEMPLATES = {
 "war": dict(
    title="Ceasefire in the war between {subject} and {other}",
    effects=["both parties: -15 war support", "a ceasefire offer is tabled",
             "observers deployed: attrition for whoever refuses"],
    sponsor_pref=["SWE","RAJ","ETH"], opposes=["the belligerents' patrons"], weight=2),
 "colony": dict(
    title="Self-determination for the territories held by {subject}",
    effects=["{subject}: -10 stability, +5 resistance in every colony",
             "colonial upkeep +25%", "independence movements gain a claim"],
    sponsor_pref=["RAJ","EGY","ETH"], opposes=["the colonial powers"], weight=2),
 "embargo": dict(
    title="Lift the embargo imposed on {subject}",
    effects=["all members: embargo on {subject} ends",
             "{subject}: +10 stability", "the embargoing power loses face"],
    sponsor_pref=["EGY","BRA","RAJ"], opposes=["the embargoing power"], weight=1),
 "nuke": dict(
    title="Condemn the nuclear test conducted by {subject}",
    effects=["{subject}: -10 world opinion, -5 stability",
             "test ban talks open", "no effect on the arsenal itself"],
    sponsor_pref=["SWE","RAJ"], opposes=["the nuclear powers"], weight=2),
 "occupation": dict(
    title="Withdrawal from the territory occupied by {subject}",
    effects=["{subject}: -15 war support, occupation cost +50%",
             "a supervised withdrawal is scheduled"],
    sponsor_pref=["EGY","ETH","RAJ"], opposes=["{subject} and its patron"], weight=3),
 "coup": dict(
    title="Recognition of the new government of {subject}",
    effects=["{subject}: recognised, may join the UN and trade freely",
             "the deposed government's claims lapse"],
    sponsor_pref=["BRA","EGY"], opposes=["whoever backed the old government"], weight=1),
}

def motion_from(sit, W, year, rng):
    t = TEMPLATES[sit.kind]
    subj = W.get(sit.subject)
    # who benefits: a motion against a country hurts that country's patron
    patron = subj.sphere if subj else ""
    favours = ""
    if patron == "USA": favours = "SOV"
    elif patron == "SOV": favours = "USA"
    backers = [b for b in t["sponsor_pref"] if b in {c.bloc for c in W.values()}]
    return dict(
        id=f"gen_{sit.kind}_{sit.subject}_{year}",
        year=year, month=1, chamber="SC" if t["weight"] >= 2 else "GA",
        target=sit.subject, topic=t["title"].format(subject=sit.subject, other=sit.other),
        favours=favours, weight=t["weight"], generated=True,
        effects=[e.format(subject=sit.subject, other=sit.other) for e in t["effects"]],
        sponsors=backers[:2], opponents=t["opposes"],
        requires=[], forbids=[])

def card(r, W):
    """The resolution card, as the UN tab should print it. Everything the player
    needs to decide is on it: what it does, who wants it, who it helps."""
    lines = []
    lines.append(f"  +{'-'*72}+")
    lines.append(f"  | {r['topic'][:70]:<70} |")
    lines.append(f"  | {('Security Council' if r['chamber']=='SC' else 'General Assembly'):<20}"
                 f"{'tabled ' + str(r['year']):<20}"
                 f"{'ORIGIN: ' + ('the world' if r.get('generated') else 'history'):<30} |")
    lines.append(f"  +{'-'*72}+")
    lines.append(f"  | IF IT PASSES{'':<59} |")
    for e in r.get("effects", ["(effects not yet authored)"]):
        lines.append(f"  |   - {e[:66]:<66} |")
    who = r.get("sponsors") or ["-"]
    lines.append(f"  | TABLED BY   {', '.join(who):<59} |")
    lines.append(f"  | AGAINST     {', '.join(r.get('opponents', ['-'])):<59} |")
    fav = r["favours"] or "neither side"
    lines.append(f"  | BENEFITS    {fav:<12} {'+' + str(r['weight']) + ' cold war points':<46} |")
    lines.append(f"  +{'-'*72}+")
    return "\n".join(lines)

def fill_report():
    """Authored history first; the world fills the silence."""
    rng = random.Random(17)
    year = 1954   # one of the silent years
    W = build_world(); recognise(W, year)
    sits = [
        Situation("war","VIE","FRA",1946),
        Situation("colony","POR",since=1500),
        Situation("embargo","SPR",since=1946),
        Situation("occupation","SOV","AUS",1945),
    ]
    print("=== WHEN HISTORY IS SILENT, THE WORLD SPEAKS ===")
    print(f"  {year} has no authored resolution. What is actually happening on the map:")
    for s in sits:
        print(f"    {s.kind:<11} {s.subject}{(' vs ' + s.other) if s.other else ''}")
    print("\n  so the floor sits on this:\n")
    print(card(motion_from(sits[0], W, year, rng), W))
    print()
    print(card(motion_from(sits[1], W, year, rng), W))
    print("\n  and an authored one, for comparison - same card, different origin:\n")
    authored = [r for _, r in schedule(HISTORICAL_WORLD) if r["year"] == 1956][0]
    authored = dict(authored, effects=["Britain and France: withdraw or face sanctions",
                                       "UNEF deployed to the canal zone",
                                       "the canal reopens under Egyptian administration"],
                    sponsors=["RAJ","SWE"], opponents=["ENG","FRA"])
    print(card(authored, W))
    print()

def silence_report():
    """How much of the calendar the world has to cover."""
    sched = schedule(HISTORICAL_WORLD)
    by_year = {}
    for m, r in sched: by_year.setdefault(m//12, []).append(r)
    sittings = 3
    filled = silent = 0
    for y in range(1949, 2009):
        have = len(by_year.get(y, []))
        filled += min(have, sittings)
        silent += max(0, sittings - have)
    print("=== HOW MUCH THE GENERATOR HAS TO CARRY ===")
    print(f"  {sittings} sittings a year, 60 years = {sittings*60} slots")
    print(f"  authored history fills {filled} ({100*filled/(sittings*60):.0f}%)")
    print(f"  the world fills {silent} ({100*silent/(sittings*60):.0f}%)")
    print("\n  so two thirds of what the player votes on comes from their own game.")
    print("  That is the right ratio: history sets the landmarks, the campaign")
    print("  supplies the rest, and both print the same card.\n")


if __name__ == "__main__":
    if   "--test"    in sys.argv: self_check()
    elif "--council" in sys.argv: council_report()
    elif "--members" in sys.argv: members_report()
    elif "--floor"   in sys.argv: floor_report()
    elif "--veto"    in sys.argv: veto_report()
    elif "--blocs"   in sys.argv: bloc_report()
    elif "--points"  in sys.argv: points_report()
    elif "--coverage" in sys.argv: coverage_report()
    elif "--scenarios" in sys.argv: scenario_report()
    elif "--cadence" in sys.argv: cadence_report()
    elif "--pendulum" in sys.argv: pendulum_report()
    elif "--price"   in sys.argv: price_report()
    elif "--favours" in sys.argv: favour_report()
    elif "--sittings" in sys.argv: cadence_compare(); cadence_advice()
    elif "--floorplan" in sys.argv: floorplan_report()
    elif "--fill"    in sys.argv: fill_report(); silence_report()
    else:
        council_report(); members_report(); bloc_report()
        coverage_report(); cadence_report(); scenario_report()
        points_report(); points_report(SCENARIOS['North Korea wins 1951'], 'North Korea wins 1951')
        floor_report(); veto_report()












