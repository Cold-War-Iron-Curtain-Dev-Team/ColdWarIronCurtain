#!/usr/bin/env python3
"""
CWIC economy check: compares a game run against history.

  1. Play/observe a game for some years (the mod logs one CWIC_ECON line per country per year in game.log).
  2. Run:  python _tools/economy_check/check_economy.py  [path/to/game.log]
     (default: Documents/Paradox Interactive/Hearts of Iron IV/logs/game.log)

It compares RELATIVE numbers, so the mod's internal money units don't matter:
  - GDP per capita as a share of the USA's, against the Maddison Project Database 2023
  - average yearly GDP-per-capita growth over the run, against Maddison
  - HDI ranking of countries, against Prados de la Escosura's historical HDI (different scale, so ranks only)
  - sanity: zero/negative GDP, debt > 150% of GDP, extreme monthly inflation, big one-year jumps

Reference data (CC BY 4.0): Bolt & van Zanden (2024), Maddison Project Database 2023;
Prados de la Escosura, historical HDI; both via Our World in Data. See reference_*.csv.
Tolerances are at the top of this file.
"""
import csv, os, re, sys, collections

LEVEL_TOLERANCE = 1.5      # flag if (game share of US GDPpc) / (historical share) is above this or below 1/this
GROWTH_TOLERANCE = 2.0     # flag if average yearly growth differs from history by more than this many points
HDI_RANK_TOLERANCE = 15    # flag if a country's HDI rank differs from its historical rank by more than this
DEBT_LIMIT = 1.5           # debt / GDP
INFLATION_MOM_LIMIT = 10   # % per month
JUMP_LIMIT = 0.35          # GDP per capita change in a single year (35%)

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_LOG = os.path.join(os.path.expanduser("~"), "Documents", "Paradox Interactive", "Hearts of Iron IV", "logs", "game.log")


def num(x):
    try:
        return float(x.replace(",", ""))
    except ValueError:
        return None


def load_reference(name, col):
    ref = collections.defaultdict(dict)
    with open(os.path.join(HERE, name), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            ref[r["tag"]][int(r["year"])] = float(r[col])
    return ref


def load_game(path):
    game = collections.defaultdict(dict)
    rx = re.compile(r"CWIC_ECON;(\d{4});(\w+);([^;]*);([^;]*);([^;]*);([^;]*);([^;]*);([^;\s]*)")
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            m = rx.search(line)
            if m:
                y, tag = int(m.group(1)), m.group(2)
                gdp, pc, hdi, debt, infl, money = (num(v) for v in m.groups()[2:])
                game[tag][y] = dict(gdp=gdp, pc=pc, hdi=hdi, debt=debt, infl=infl, money=money)
    return game


def nearest(series, year, max_gap=3):
    best = min(series, key=lambda y: abs(y - year), default=None)
    return series[best] if best is not None and abs(best - year) <= max_gap else None


def spearman(a, b):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0] * len(v)
        for k, i in enumerate(order):
            r[i] = k
        return r
    ra, rb = ranks(a), ranks(b)
    n = len(a)
    d2 = sum((x - y) ** 2 for x, y in zip(ra, rb))
    return 1 - 6 * d2 / (n * (n * n - 1)) if n > 2 else None


def main():
    log = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG
    if not os.path.exists(log):
        sys.exit("game.log not found: %s" % log)
    game = load_game(log)
    if not game:
        sys.exit("No CWIC_ECON lines in %s - play at least one in-game year with the mod loaded." % log)
    gdp_ref = load_reference("reference_gdp_per_capita.csv", "gdp_per_capita")
    hdi_ref = load_reference("reference_hdi.csv", "ahdi")
    years = sorted({y for t in game.values() for y in t})
    issues = []  # (severity, text)

    # 1) relative level vs USA
    for y in years:
        us_g = (game.get("USA", {}).get(y) or {}).get("pc")
        us_r = nearest(gdp_ref["USA"], y)
        if not us_g or not us_r:
            continue
        for tag, rows in sorted(game.items()):
            g = rows.get(y)
            r = nearest(gdp_ref.get(tag, {}), y)
            if not g or not g["pc"] or not r or tag == "USA":
                continue
            ratio = (g["pc"] / us_g) / (r / us_r)
            if ratio > LEVEL_TOLERANCE or ratio < 1 / LEVEL_TOLERANCE:
                issues.append((tag, "GDP per capita level", abs(ratio if ratio > 1 else 1 / ratio), "%d %s: GDP per capita is %.0f%% of the USA's (history: %.0f%%), %.1fx %s"
                               % (y, tag, 100 * g["pc"] / us_g, 100 * r / us_r, ratio if ratio > 1 else 1 / ratio, "too rich" if ratio > 1 else "too poor")))

    # 2) growth over the whole run
    if len(years) > 1:
        y0, y1 = years[0], years[-1]
        for tag, rows in sorted(game.items()):
            if y0 in rows and y1 in rows and rows[y0]["pc"] and rows[y1]["pc"] and rows[y0]["pc"] > 0:
                r0, r1 = nearest(gdp_ref.get(tag, {}), y0), nearest(gdp_ref.get(tag, {}), y1)
                if not r0 or not r1:
                    continue
                n = y1 - y0
                g_cagr = 100 * ((rows[y1]["pc"] / rows[y0]["pc"]) ** (1 / n) - 1)
                r_cagr = 100 * ((r1 / r0) ** (1 / n) - 1)
                if abs(g_cagr - r_cagr) > GROWTH_TOLERANCE:
                    issues.append((tag, "growth", abs(g_cagr - r_cagr) / GROWTH_TOLERANCE, "%d-%d %s: GDP per capita grows %.1f%%/yr (history: %.1f%%/yr)" % (y0, y1, tag, g_cagr, r_cagr)))

    # 3) HDI ordering
    hdi_lines = []
    for ref_year in sorted({y for t in hdi_ref.values() for y in t}):
        if not any(abs(ref_year - y) <= 2 for y in years):
            continue
        y = min(years, key=lambda v: abs(v - ref_year))
        tags = [t for t in hdi_ref if ref_year in hdi_ref[t] and (game.get(t, {}).get(y) or {}).get("hdi") is not None]
        if len(tags) < 5:
            continue
        g = [game[t][y]["hdi"] for t in tags]
        r = [hdi_ref[t][ref_year] for t in tags]
        rho = spearman(g, r)
        hdi_lines.append("%d: HDI rank correlation with history %.2f over %d countries" % (y, rho, len(tags)))
        g_rank = {t: i for i, t in enumerate(sorted(tags, key=lambda t: -game[t][y]["hdi"]))}
        r_rank = {t: i for i, t in enumerate(sorted(tags, key=lambda t: -hdi_ref[t][ref_year]))}
        for t in tags:
            if abs(g_rank[t] - r_rank[t]) > HDI_RANK_TOLERANCE:
                issues.append((t, "HDI rank", abs(g_rank[t] - r_rank[t]) / HDI_RANK_TOLERANCE, "%d %s: HDI rank %d (history: %d of %d)" % (y, t, g_rank[t] + 1, r_rank[t] + 1, len(tags))))

    # 4) sanity
    for tag, rows in sorted(game.items()):
        prev = None
        for y in sorted(rows):
            g = rows[y]
            if g["gdp"] is not None and g["gdp"] <= 0:
                issues.append((tag, "GDP <= 0", 3, "%d %s: GDP is %s" % (y, tag, g["gdp"])))
            if g["gdp"] and g["debt"] and g["debt"] / g["gdp"] > DEBT_LIMIT:
                issues.append((tag, "debt", g["debt"] / g["gdp"] / DEBT_LIMIT, "%d %s: debt is %.0f%% of GDP" % (y, tag, 100 * g["debt"] / g["gdp"])))
            if g["infl"] is not None and abs(g["infl"]) > INFLATION_MOM_LIMIT:
                issues.append((tag, "inflation", abs(g["infl"]) / INFLATION_MOM_LIMIT, "%d %s: inflation %.1f%% per month" % (y, tag, g["infl"])))
            if prev and prev["pc"] and g["pc"] and abs(g["pc"] / prev["pc"] - 1) > JUMP_LIMIT:
                issues.append((tag, "one-year jump", abs(g["pc"] / prev["pc"] - 1) / JUMP_LIMIT, "%d %s: GDP per capita changed %+.0f%% in one year" % (y, tag, 100 * (g["pc"] / prev["pc"] - 1))))
            prev = g

    print("CWIC economy check: %d countries, years %d-%d, log %s\n" % (len(game), years[0], years[-1], log))
    for l in hdi_lines:
        print(l)
    grouped = collections.defaultdict(list)
    for tag, kind, sev, text in issues:
        grouped[(tag, kind)].append((sev, text))
    print("\n%d problems in %d countries (worst first; severity 1.0 = exactly at the tolerance):" % (len(grouped), len({t for t, _ in grouped})))
    for (tag, kind), v in sorted(grouped.items(), key=lambda kv: -max(x[0] for x in kv[1])):
        sev, text = max(v)
        print("  [%4.1f] %-5s %-21s %3d year(s)  worst: %s" % (sev, tag, kind, len(v), text))


if __name__ == "__main__":
    main()
