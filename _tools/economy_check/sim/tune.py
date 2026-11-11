"""Coordinate search over the [tune] params (stdlib only).

Usage (from mod root): python ../_tools/economy_check/sim/tune.py [seconds_budget]
Priority order: (1) 1949 GDP within +-10% for the 15, (2) 0 defaults, (3) minimise growth error, (4) maximise 1949 level matches.
Phase 1 fits base(d)/sigma on month-0 output only (fast). Phase 2 fits growth/tax/education/CG params on full runs.
Writes params_tuned.json and out/report.txt.
"""
import json, math, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import model, params, run

PHASE1 = ["base0", "base1", "base2", "base3", "base4", "base5", "sigma"]
PHASE2 = ["tax_shares0", "tax_shares1", "tax_shares2", "tax_shares3", "tg_base", "tg_catch", "chi", "k_sp",
          "k_army", "k_navy", "k_air", "k_strat", "cap_lo", "h_lo", "h_hi", "rho"]


def mono(ov):
    for i in range(1, 6):
        ov["base%d" % i] = max(ov["base%d" % i], ov["base%d" % (i - 1)])
    return ov


def search(ov, keys, score, deadline, steps):
    best = score(ov)
    for st in steps:
        improved = True
        while improved and time.time() < deadline:
            improved = False
            for k in keys:
                lo, hi = params.TUNABLE[k][2], params.TUNABLE[k][3]
                for f in (st, 1 / st):
                    c = dict(ov)
                    c[k] = min(hi, max(lo, ov[k] * f))
                    if k.startswith("base"):
                        c = mono(c)
                    if c == ov:
                        continue
                    sc = score(c)
                    if sc < best - 1e-12:
                        ov, best, improved = c, sc, True
                if time.time() > deadline:
                    break
    return ov, best


def main():
    budget = float(sys.argv[1]) if len(sys.argv) > 1 else 90.0
    t0 = time.time()
    data, today, ref = model.load_start(), model.load_today(), run.load_ref()
    budg, ratios = model.load_budget(), model.load_debt_ratios()
    P0 = params.get()
    ov = {}
    for k, (key, idx, _, _) in params.TUNABLE.items():
        ov[k] = P0[key] if idx is None else P0[key][idx]
    tags1 = sorted(set(run.STRESS) | {t for t in ref if t in today})
    tg = model.start_targets(today, ref, data)

    def month0(o):
        P = params.get(o)
        cs = model.build(tags1, P, data, today, budg, ratios, tg)
        for c in cs.values():
            c.step(1949, 6, 42.04, True)
        return cs, P

    def score1(o):
        cs, P = month0(o)
        m = run.evaluate(cs, today, ref, P)
        l = [math.log(cs[t].cwic_start_productivity) for t in run.STRESS if t in cs]
        return sum(x * x for x in l) / len(l) + 10 * m["gdp_err"] ** 2 - 0.0005 * m["levels"]

    ov, s1 = search(ov, PHASE1, score1, t0 + 0.3 * budget, (3, 2, 1.5, 1.25, 1.1, 1.05, 1.02, 1.01))
    print("phase 1: score %.4f in %.0fs" % (s1, time.time() - t0))

    def score2(o):
        P = params.get(o)
        cs = model.simulate(model.build(tags1, P, data, today, budg, ratios, tg))
        m = run.evaluate(cs, today, ref, P)
        g = m["growth"] if m["growth"] == m["growth"] else 9.0
        # MODEL 3.1 revenue bands are hard: every country's start tax-to-GDP must sit inside its band
        pen = 1e6 * sum(model.band_violation(P, c.tax_lv, c.hdi0, c.x) for c in cs.values())
        mu = m["mil_usa"]
        pen += 100 * max(0.0, 0.04 - mu, mu - 0.06)     # MODEL 3.3 USA military 4-6% GDP
        return (pen + 1000 * m["defaults15"] + 5 * m["defaults_all"] + 100 * max(0.0, math.log(g)) - m["levels"]
                + 20 * abs(m["infl50"] - 3.0) + 0.05 * abs(m["social_rich"] - 14.0) + (0 if m["gdp_out"] == 0 else 1e5))

    ov, s2 = search(ov, PHASE2, score2, t0 + budget, (2, 1.5, 1.25, 1.1, 1.05))
    print("phase 2: score %.3f in %.0fs" % (s2, time.time() - t0))
    json.dump({"overrides": ov, "score": s2}, open(os.path.join(HERE, "params_tuned.json"), "w"), indent=1)
    P = params.get(ov)
    cs = model.simulate(model.build(sorted({r["owner"] for r in data["states"].values()}), P, data, today, budg, ratios, tg))
    m = run.evaluate(cs, today, ref, P)
    run.write_csv(cs, os.path.join(HERE, "out", "yearly.csv"))
    run.write_start_csv(cs, tg, os.path.join(HERE, "out", "start_productivity.csv"))
    txt = run.report(m, today) + "\n\ntuned overrides:\n" + json.dumps(ov, indent=1)
    open(os.path.join(HERE, "out", "report.txt"), "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
