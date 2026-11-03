"""MODEL.md monthly economy for many countries in lockstep (the USA GDP per head is the catch-up frontier).

Start 1949-06, monthly. Money in billions, GDP in billions/yr. See README.md for approximations.
"""
import json, math, os, re
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
REPO = os.path.dirname(MOD)
LOG_A2 = os.path.join(REPO, "docs", "economy_map", "baseline", "runA2_2026-11-02", "game.log")
LOG_D = os.path.join(REPO, "docs", "economy_map", "baseline", "runD_2026-11-02", "game.log")
STARTUP = os.path.join(MOD, "common", "scripted_effects", "StartupMoney.txt")
END_YEAR = 1989
clamp = lambda x, lo, hi: lo if x < lo else hi if x > hi else x


# ---------------------------------------------------------------- data
def load_start():
    return json.load(open(os.path.join(HERE, "start_1949.json")))


def load_today():
    """runA2 1949 rows: tag -> dict(gdp, pc, hdi, debt, infl, money)."""
    out = {}
    rx = re.compile(r"CWIC_ECON;1949;(\w+);([-\d.]+);([-\d.]+);([-\d.]+);([-\d.]+);([-\d.]+);([-\d.]+)")
    for line in open(LOG_A2, errors="replace"):
        m = rx.search(line)
        if m:
            v = [float(x) for x in m.groups()[1:]]
            out[m.group(1)] = dict(gdp=v[0], pc=v[1], hdi=v[2], debt=v[3], infl=v[4], money=v[5])
    return out


def load_budget():
    """runD 1950 CWIC_BUDGET rows."""
    out = {}
    rx = re.compile(r"CWIC_BUDGET;1950;(\w+);" + ";".join([r"([-\d.]+)"] * 17))
    for line in open(LOG_D, errors="replace"):
        m = rx.search(line)
        if m:
            v = [float(x) for x in m.groups()[1:]]
            out[m.group(1)] = dict(income=v[0], balance=v[1], debt_pay=v[2], land=v[3], welfare=v[4], edu=v[5], health=v[6],
                                   tax_lvl=v[7], edu_lvl=v[8], welfare_lvl=v[9], health_lvl=v[10])
    return out


def load_debt_ratios():
    """StartupMoney historical debt/GDP overrides (tag -> ratio) and generic HDI-based fallback."""
    txt = open(STARTUP, errors="replace").read()
    a = txt.index("cwic_apply_historical_debt_ratio_overrides = {")
    seg = txt[a:txt.index("cwic_apply_starting_debt_profile = {")]
    out = {}
    pat = r"limit = \{(.*?)\}\s*set_temp_variable = \{ cwic_seed_total_debt = grossdomesticproduct \}\s*multiply_temp_variable = \{ cwic_seed_total_debt = ([\d.]+) \}"
    for m in re.finditer(pat, seg, re.S):
        for t in re.findall(r"tag = (\w+)", m.group(1)):
            out[t] = float(m.group(2))
    return out


def generic_ratio(hdi):
    return 0.55 if hdi > .8 else 0.40 if hdi > .65 else 0.12 if hdi < .35 else 0.22 if hdi < .5 else 0.30


# ---------------------------------------------------------------- country
class Country:
    def __init__(s, tag, states, cdata, today, budget, ratios, P):
        s.tag, s.P = tag, P
        x = (cdata or {}).get("x")
        s.x = 10.0 if x is None or not 0 <= x <= 20 else x
        s.mciv = 1.25 if s.x < 7 else 1.5 if s.x < 14 else 1.75
        s.mofp = 1.35 if s.x < 7 else 1.65 if s.x < 14 else 1.9
        s.closed = s.x < 4
        s.st = []
        for r in states:
            b, rs = r["b"], r["r"]
            ru = rs["oil"] + rs["aluminium"] + rs["tungsten"] + rs["steel"] + rs["chromium"] + r["coal"]
            d = r["dev"]
            jobs = (27 * d * b["industrial_complex"] + 9.45 * d * (b["arms_factory"] + b["dockyard"]) + 56.7 * d * b["office_park"]
                    + 5.67 * d * b["steel_factory"] + 4.05 * d * b["tungsten_factory"] + 4.05 * d * ru
                    + 14.175 * (b["agri_industrial_complex"] + rs["rubber"]))
            e = r["edu"]
            s.st.append(dict(pop=r["manpower"] / 1000.0, d=d, infra=b["infrastructure"], ic=b["industrial_complex"],
                             oth=1.25 * b["arms_factory"] + 2.5 * b["dockyard"] + 1.75 * (b["steel_factory"] + b["tungsten_factory"]),
                             op=b["office_park"], farms=b["agri_industrial_complex"] + 0, rub=rs["rubber"], res=ru, jobs=jobs,
                             edu=[e["literate_educated"], e["primary_educated"], e["high_school_educated"], e["college_educated"]]))
        s.oil = sum(r["r"]["oil"] for r in states)
        s.oil_exporter = s.oil * 1000 / max(1, sum(q["pop"] for q in s.st)) >= 0.15
        t = today.get(tag, {})
        s.hdi0 = t.get("hdi", 0.4)
        bl = budget.get(tag)
        lv = round(4 + 8 * s.hdi0)
        s.lv = dict(tax=bl["tax_lvl"] if bl else lv, edu=bl["edu_lvl"] if bl else lv, welfare=bl["welfare_lvl"] if bl else lv,
                    health=bl["health_lvl"] if bl else lv)
        s.land0 = bl["land"] if bl else None
        s.ratio = ratios.get(tag, generic_ratio(s.hdi0))
        s.reserve = 0.7 if tag == "USA" else 1.0
        s.tech, s.hdi, s.g, s.gdp, s.infl_hist = 1.0, s.hdi0, 1.0, 1.0, [0.0] * 12
        s.A = s.Ares = s.Idle = 0.0
        s.pop_total = sum(q["pop"] for q in s.st)
        s.defaults, s.cool, s.svc_run, s.rows, s.acc = 0, 0, 0, {}, defaultdict(lambda: defaultdict(float))
        s.rate_flag = False
        s.loans, s.cur = [], None
        s.money, s.balance_prev, s.rating = 0.0, 0.0, 6
        s.gdp0 = None
        s.target = None   # start GDP target (billions) for the start-productivity calibration
        s.tech0 = 1.0

    # -- quarterly: education pulse + per-state output aggregates (MODEL 1, 7)
    def refresh(s, year, edu_pulse, hdi_pulse):
        P = s.P
        if edu_pulse:
            s.edu_step()
        A = Ares = Idle = 0.0
        wsum = hsum = 0.0
        for q in s.st:
            L, Pr, H, C = q["edu"]
            Y = (3 * L + 3 * Pr + 6 * H + 4 * C) / 100.0
            pi0 = P["base"][int(q["d"]) - 1] * 1.1 ** Y * (1 + 0.05 * q["infra"])
            wf = q["pop"] * (1 - P["conscription"]) * 0.75 * P["workforce_ratio"]
            jobs = q["jobs"]
            E = 1.0 if jobs <= 0 else min(1.0, wf / jobs)
            idle = max(0.0, wf - jobs)
            food = 0.5 * P["farm_output_norm"] * q["farms"] + 0.5 * q["rub"]
            non = pi0 * E * (2 * s.mciv * q["ic"] + q["oth"] + 7 * s.mofp * q["op"] + food + P["sigma"] * wf / 100.0)
            res = pi0 * E * 0.5 * q["res"]
            A += non; Ares += res; Idle += 0.2 * idle / 100.0
            if hdi_pulse:
                gs = 1000.0 * ((s.tech * (non + res) + 0.2 * idle / 100.0) / 10.0) / max(q["pop"], 1e-6)
                lei = clamp((s.life(gs, L, year) - 20) / 65.0, 0, 1)
                hii = clamp(math.log(max(10 * gs, 1.0001)) / 6.907, 0.001, 1)
                edu = (10 * C + 6 * H + 4 * Pr + 2 * L) / 2200.0
                wsum += q["pop"]; hsum += q["pop"] * (hii + lei + edu) / 3.0
        s.A, s.Ares, s.Idle = A, Ares, Idle
        if hdi_pulse and wsum:
            s.hdi = hsum / wsum

    def life(s, g, L, year):
        return -0.68 + 5.1 * math.log(max(g * 228, 1.0)) + 0.21 * L + 0.18 * (year - 1950) + 0.3 * (s.lv["health"] - 10)

    def edu_step(s):
        P = s.P
        u = clamp((math.log(max(s.g, 1e-3) * 228) - math.log(150)) / (math.log(12000) - math.log(150)), 0, 1)
        T = (12 + 87 * u ** .5, 4 + 91 * u ** .8, 1 + 70 * u ** 1.2, .2 + 28 * u ** 1.5)
        k = P["edu_rate"] * s.lv["edu"] / 10.0
        for q in s.st:
            e = q["edu"]
            for i in range(4):
                e[i] = clamp(e[i] + clamp(k * (T[i] - e[i]), -0.5, P["edu_cap"]) / 4.0, 0, 100)
                if i and e[i] > e[i - 1]:
                    e[i] = e[i - 1]

    # -- rate / rating (MODEL 4)
    def rate_now(s, year, debt_ratio):
        P = s.P
        pts = sorted((int(k), v) for k, v in P["safe_ratio"].items())
        r = s.rating
        safe = pts[-1][1] if r >= pts[-1][0] else pts[0][1] if r <= pts[0][0] else next(
            a[1] + (b[1] - a[1]) * (r - a[0]) / (b[0] - a[0]) for a, b in zip(pts, pts[1:]) if a[0] <= r <= b[0])
        rate = max(0.5, P["rate_a"] - P["rate_b"] * r) * s.reserve + P["infl_premium"] * sum(s.infl_hist) * 100 + P["debt_premium"] * max(0, debt_ratio - safe)
        return rate + (P["rate_shock_spread"] if s.rate_flag and s.in_rate_shock else 0.0)

    def debt(s):
        return sum(b[0] for b in s.loans)

    def borrow(s, amount, year):
        key = year
        rate = s.rate_now(year, s.debt() / max(s.gdp, 1e-9))
        term = s.P["loan_term_years"]
        if s.cur and s.cur[3] == key:
            b = s.cur
            tot = b[0] + amount
            b[2] = (b[2] * b[0] + rate * amount) / tot
            b[0] = tot; b[1] += amount / (12 * term)
        else:
            s.cur = [amount, amount / (12 * term), rate, key]
            s.loans.append(s.cur)

    def seed(s):
        P = s.P
        s.gdp0 = s.gdp
        d = s.ratio * s.gdp
        for share, term, rate in ((P["dom_share"], P["dom_term"], P["dom_rate"]), (1 - P["dom_share"], P["for_term"], P["for_rate"])):
            if d * share > 0:
                s.loans.append([d * share, d * share / (12 * term), rate, 0])
        s.money = 0.035 * s.gdp * (1.3 if s.hdi > .8 else 1.15 if s.hdi > .65 else .7 if s.hdi < .35 else .85 if s.hdi < .5 else 1.0) * (1.4 if s.reserve < 1 else 1.0)
        s.rating = int(clamp(round(1 + 9.5 * s.hdi - 2 * max(0, s.ratio - 0.8)), 2, 10))

    def rec_stock(s, year):
        d = s.debt()
        s.rows[year] = dict(gdp=s.gdp, gdp_pc=s.g, hdi=s.hdi, debt=d, debt_gdp=d / max(s.gdp, 1e-9), defaults=s.defaults, money=s.money)

    # -- one month
    def step(s, year, mon, ref_g, first):
        P = s.P
        if mon in (1, 4, 7, 10) or first:
            if mon == 1 and not first:
                for q in s.st:
                    q["pop"] *= 1 + P["pop_growth"]
                s.pop_total = sum(q["pop"] for q in s.st)
            s.refresh(year, edu_pulse=not first, hdi_pulse=(mon == 1 or first))
        t = (year - 1949) * 12 + mon - 6
        # 9 history shocks
        sh, kres, infl_add = 1.0, 1.0, 0.0
        if year == 1958 and not s.closed:
            sh *= 1 - P["recession"]
        for y0, m0, f in ((1973, 10, 1.0), (1979, 1, 0.5)):
            if 0 <= (year - y0) * 12 + mon - m0 < 24:
                if s.oil_exporter:
                    kres *= 1 + P["oil1_exp"] * f
                else:
                    sh *= 1 - P["oil1_imp"] * f
                    infl_add += P["oil1_infl"] * f / 24 / 100
        s.in_rate_shock = 1981 <= year < 1984
        if year == 1981 and mon == 1:
            s.rate_flag = s.debt() / max(s.gdp, 1e-9) > 0.6
        stag = P["stagnation"] if year >= 1965 and s.x < 7 and year < P.get("stag_end", {}).get(s.tag, 1990) else 0.0
        if not first:
            rate = clamp(P["tg_base"] + P["tg_catch"] * clamp(math.log(max(ref_g, 1e-6) / max(s.g, 1e-6)), 0, 4) - stag, 0, P["tg_max"])
            s.tech *= math.exp(rate / 12)
        k = s.tech * clamp(sh, 0.1, 1.1)
        s.gdp = (k * (s.A + kres * s.Ares) + s.Idle) / 10.0
        s.g = 1000.0 * s.gdp / s.pop_total
        if first:
            if s.target is not None:
                s.tech = s.tech0 = max(P["tech0_min"], (10 * s.target - s.Idle) / max(s.A + s.Ares, 1e-9))
                s.refresh(year, False, True)
                s.gdp = (s.tech * (s.A + s.Ares) + s.Idle) / 10.0
                s.g = 1000.0 * s.gdp / s.pop_total
            s.seed(); s.rec_stock(year)
            s.infl_hist = [0.0] * 12
            return
        if mon == 1:
            s.rec_stock(year)
            s.rating = int(clamp(round(1 + 9.5 * s.hdi - 2 * max(0, s.debt() / max(s.gdp, 1e-9) - 0.8)), 2, 10))
        gm = s.gdp / 12.0
        # 6 consumer goods
        demand = gm * (P["delta0"] + P["delta_hdi"] * s.hdi)
        supply = k * s.A / 10.0 / 12.0 * P["chi"]   # civilian output = all non-resource, non-subsistence output
        short = clamp(1 - supply / demand, 0, 1) if demand > 0 else 0.0
        cg_exp = max(0.0, supply - demand) * P["export_rate"]
        # 3 budget
        eta = (1 - 0.5 * P["corruption"]) * (1 + P["tax_eff"])
        rev = gm * P["tax_scale"] * sum(P["tax_shares"]) * 0.05 * s.lv["tax"] * eta + cg_exp
        m = lambda lv: 0.001 if lv <= 0 else 0.05 * lv
        K = P["kappa"]
        social = gm * (K["welfare"] * m(s.lv["welfare"]) + K["health"] * m(s.lv["health"]) + K["edu"] * m(s.lv["edu"])
                       + K["police"] * m(P["police_level"]) + K["public"] * m(P["public_level"]))
        mil = (s.land0 * P["mil_mult"] * s.gdp / s.gdp0) if s.land0 is not None else P["mil_default_share"] * gm
        interest = inst = 0.0
        for b in s.loans:
            interest += b[0] * b[2] / 1200.0
            pay = min(b[1], b[0]); b[0] -= pay; inst += pay
        if len(s.loans) > 40 or (s.loans and s.loans[0][0] < 1e-9):
            s.loans = [b for b in s.loans if b[0] > 1e-9]
        bal = rev - social - mil - interest - inst
        s.money += bal
        debt = s.debt()
        if s.money < 0:
            cap = P["lender_cap"] * s.gdp * (P["rate_shock_cap"] if s.rate_flag and s.in_rate_shock else 1.0)
            amt = min(-s.money, max(0.0, cap - debt))
            if amt > 0:
                s.borrow(amt, year); s.money += amt; debt += amt
        # default test (4)
        svc = interest + inst
        s.svc_run = s.svc_run + 1 if rev > 0 and svc / rev > P["svc_default"] else 0
        if s.cool > 0:
            s.cool -= 1
        elif s.svc_run >= P["svc_months"] or debt / max(s.gdp, 1e-9) > P["default_mult"]:
            s.defaults += 1; s.cool = 24; s.svc_run = 0
            for b in s.loans:
                b[0] *= 0.5; b[1] *= 0.5
            s.money = max(s.money, 0.0)
        # 5 inflation
        era = P["era_infl"][0 if year < 1971 else 1 if year < 1983 else 2]
        dp = P["k_dp"] * max(0.0, -bal / gm) / 12.0
        infl = era / 1200.0 + short ** 2 * P["k_sp"] + dp + infl_add
        s.infl_hist = s.infl_hist[1:] + [infl]
        a = s.acc[year]
        a["n"] += 1; a["infl"] += infl; a["bal"] += bal; a["social"] += social; a["gdpm"] += gm; a["rev"] += rev; a["mil"] += mil; a["svc"] += svc
        s.balance_prev = bal


def start_targets(today, ref, data):
    """Start GDP targets: today's runA2 1949 GDP; for tags in the Maddison reference and not in the 15 stress-test
    countries, the Maddison 1950 GDP per head relative to the USA (anchored at 42.04) times start population."""
    stress = set("USA SOV ENG FRA WGR JAP ITA CAN RAJ PRC BRA POL SPR EGY IRQ".split())
    tg = {t: v["gdp"] for t, v in today.items()}
    pop = defaultdict(float)
    for r in data["states"].values():
        pop[r["owner"]] += r["manpower"] / 1000.0
    us = ref.get("USA", {})
    us_r = us[min(us, key=lambda y: abs(y - 1950))]
    for t, series in ref.items():
        if t in stress or t == "tag" or t not in pop:
            continue
        r = series[min(series, key=lambda y: abs(y - 1950))]
        tg[t] = 42.04 * r / us_r * pop[t] / 1000.0
    return tg


def build(tags, P, data=None, today=None, budget=None, ratios=None, targets=None):
    data = data or load_start()
    today = today if today is not None else load_today()
    budget = budget if budget is not None else load_budget()
    ratios = ratios if ratios is not None else load_debt_ratios()
    by = defaultdict(list)
    for r in data["states"].values():
        by[r["owner"]].append(r)
    cs = {}
    for t in tags:
        if t in by:
            cs[t] = Country(t, [json.loads(json.dumps(r)) for r in by[t]], data["countries"].get(t), today, budget, ratios, P)
            if targets and P.get("calibrate_start"):
                cs[t].target = targets.get(t)
    return cs


def simulate(cs, end_year=END_YEAR):
    ref_g = 42.04
    first = True
    for year in range(1949, end_year + 1):
        for mon in range(6 if year == 1949 else 1, 13):
            for c in cs.values():
                c.step(year, mon, ref_g, first)
            if "USA" in cs:
                ref_g = cs["USA"].g
            else:
                ref_g = max([c.g for c in cs.values()] + [1e-6])
            first = False
    return cs
