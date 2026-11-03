"""Simulate 1949-1989 and report against MODEL.md section 10.

Usage (from mod root): python _tools/economy_check/sim/run.py [--default] [--tags USA,SOV,...]
Uses params_tuned.json when present, unless --default.
"""
import csv, math, os, statistics, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model, params

STRESS = "USA SOV ENG FRA WGR JAP ITA CAN RAJ PRC BRA POL SPR EGY IRQ".split()
REF_CSV = os.path.join(model.MOD, "_tools", "economy_check", "reference_gdp_per_capita.csv")
TODAY = {"defaults": 38, "growth": 1.57, "levels": "18/53", "infl": 3.6}


def load_ref():
    ref = {}
    for r in csv.DictReader(open(REF_CSV, encoding="utf-8")):
        ref.setdefault(r["tag"], {})[int(r["year"])] = float(r["gdp_per_capita"])
    return ref


def near(series, year, gap=3):
    y = min(series, key=lambda v: abs(v - year), default=None)
    return series[y] if y is not None and abs(y - year) <= gap else None


def evaluate(cs, today, ref, P):
    m = {"gdp": {}, "gdp_ratio": {}}
    for t in STRESS:
        c = cs.get(t)
        if c and t in today:
            m["gdp"][t] = c.rows[1949]["gdp"]
            m["gdp_ratio"][t] = c.rows[1949]["gdp"] / today[t]["gdp"]
    m["gdp_err"] = max((abs(r - 1) for r in m["gdp_ratio"].values()), default=9.0)
    m["gdp_out"] = sum(1 for r in m["gdp_ratio"].values() if abs(r - 1) > 0.10)
    m["defaults15"] = sum(cs[t].defaults for t in STRESS if t in cs)
    m["defaults_all"] = sum(c.defaults for c in cs.values())
    # growth error: geometric mean of max(r, 1/r), r = game 1950-1989 growth factor / Maddison factor
    logs = []
    if 1989 in cs.get("USA", type("x", (), {"rows": {}})).rows or any(1989 in c.rows for c in cs.values()):
        for t, series in ref.items():
            c = cs.get(t)
            if not c or 1950 not in c.rows or 1989 not in c.rows:
                continue
            r0, r1 = near(series, 1950), near(series, 1989)
            if r0 and r1 and c.rows[1950]["gdp_pc"] > 0:
                r = (c.rows[1989]["gdp_pc"] / c.rows[1950]["gdp_pc"]) / (r1 / r0)
                logs.append(abs(math.log(r)))
    m["growth"] = math.exp(sum(logs) / len(logs)) if logs else float("nan")
    # 1949-50 level vs Maddison, relative to USA
    n, tot = 0, 0
    us = cs.get("USA")
    ly = 1950 if us and 1950 in us.rows else 1949
    if us and near(ref.get("USA", {}), 1950):
        us_g, us_r = us.rows[ly]["gdp_pc"], near(ref["USA"], 1950)
        for t, series in ref.items():
            c = cs.get(t)
            if t not in today:
                continue
            tot += 1
            if c and ly in c.rows and near(series, 1950):
                ratio = (c.rows[ly]["gdp_pc"] / us_g) / (near(series, 1950) / us_r)
                n += 1 if 1 / 1.5 <= ratio <= 1.5 else 0
    m["levels"], m["levels_total"] = n, tot
    # 1950s inflation and social share
    infl, soc = [], []
    for c in cs.values():
        v = [100 * c.acc[y]["infl"] * 12 / c.acc[y]["n"] for y in range(1950, 1960) if c.acc[y]["n"]]
        if v:
            infl.append(sum(v) / len(v))
        if c.rows.get(1950, {}).get("hdi", 0) > 0.6 and c.acc[1950]["gdpm"]:
            soc.append(100 * c.acc[1950]["social"] / c.acc[1950]["gdpm"])
    m["infl50"] = statistics.median(infl) if infl else float("nan")
    m["social_rich"] = statistics.median(soc) if soc else float("nan")
    K = P["kappa"]
    m["social10"] = 100 * (sum(K.values()) * 0.5)
    return m


def write_csv(cs, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tag", "year", "gdp", "gdp_pc", "hdi", "debt", "debt_gdp", "defaults", "inflation_pct", "balance", "social_pct_gdp", "revenue_pct_gdp", "military_pct_gdp", "service_pct_rev"])
        for t, c in sorted(cs.items()):
            for y, r in sorted(c.rows.items()):
                a = c.acc[y]
                n = a["n"] or 1
                gm = a["gdpm"] or 1e-9
                w.writerow([t, y, "%.3f" % r["gdp"], "%.4f" % r["gdp_pc"], "%.4f" % r["hdi"], "%.3f" % r["debt"], "%.4f" % r["debt_gdp"], r["defaults"],
                            "%.3f" % (100 * a["infl"] * 12 / n), "%.3f" % (a["bal"] * 12 / n), "%.2f" % (100 * a["social"] / gm),
                            "%.2f" % (100 * a["rev"] / gm), "%.2f" % (100 * a["mil"] / gm), "%.1f" % (100 * a["svc"] / a["rev"] if a["rev"] else 0)])


def report(m, today):
    L = ["MODEL.md section 10 targets (today = runA2/PLAN; sim = this run)", ""]
    L.append("1949 GDP vs today's (goal each within +-10%)")
    L.append("  %-5s %9s %9s %7s" % ("tag", "today", "sim", "ratio"))
    for t in STRESS:
        if t in m["gdp"]:
            L.append("  %-5s %9.1f %9.1f %7.2f %s" % (t, today[t]["gdp"], m["gdp"][t], m["gdp_ratio"][t], "" if abs(m["gdp_ratio"][t] - 1) <= .1 else "  OUT"))
    L += ["", "%-46s %-10s %-12s %s" % ("target", "today", "sim", "goal"),
          "%-46s %-10s %-12s %s" % ("1949 GDP within +-10% (of 15)", "-", "%d/15" % (len(m["gdp_ratio"]) - m["gdp_out"]), "15/15"),
          "%-46s %-10s %-12d %s" % ("defaults among the 15, 40 years", TODAY["defaults"], m["defaults15"], "0"),
          "%-46s %-10s %-12d %s" % ("defaults, all simulated countries", "-", m["defaults_all"], "-"),
          "%-46s %-10s %-12.2f %s" % ("GDP/head growth error vs Maddison (geo mean x)", TODAY["growth"], m["growth"], "<= 1.3"),
          "%-46s %-10s %-12s %s" % ("1950 GDP/head within 1.5x of Maddison", TODAY["levels"], "%d/%d" % (m["levels"], m["levels_total"]), ">= 35/53"),
          "%-46s %-10s %-12.1f %s" % ("social % GDP at level 10 (kappa formula)", "-", m["social10"], "10-18"),
          "%-46s %-10s %-12.1f %s" % ("social % GDP 1950, median of HDI>0.6 (own levels)", "-", m["social_rich"], "10-18"),
          "%-46s %-10s %-12.2f %s" % ("median inflation 1950s, %/yr", TODAY["infl"], m["infl50"], "2-4")]
    return "\n".join(L)


def main():
    P = params.get() if "--default" in sys.argv else params.load_tuned()
    tags = None
    for i, a in enumerate(sys.argv):
        if a == "--tags":
            tags = sys.argv[i + 1].split(",")
    data = model.load_start()
    today = model.load_today()
    t0 = time.time()
    tg = model.start_targets(today, load_ref(), data)
    cs = model.simulate(model.build(tags or sorted({r["owner"] for r in data["states"].values()}), P, data, today, targets=tg))
    m = evaluate(cs, today, load_ref(), P)
    write_csv(cs, os.path.join(HERE, "out", "yearly.csv"))
    txt = report(m, today) + "\n\n%d countries, %.0fs" % (len(cs), time.time() - t0)
    open(os.path.join(HERE, "out", "report.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
