"""All [tune] coefficients of the MODEL.md economy in one place. tune.py searches the keys in TUNABLE."""
import json, os

PARAMS = {
    # 1.2 base(d): capital/technology level per development tier d=1..6
    "base": [0.6, 1.2, 2.0, 3.0, 4.2, 5.5],
    "calibrate_start": True, "tech0_min": 0.02,   # per-country start productivity (tech_c) fitted to the start targets
    "sigma": 4.0,              # 1.4 services term
    "farm_output_norm": 1.0,   # 1.1 food multiplier (crop assumed 1)
    "conscription": 0.03,      # 1.3 average conscription share
    "workforce_ratio": 1.0,
    # tech growth stands in for investment/construction, which the sim does not model
    "tg_base": 0.015, "tg_catch": 0.012, "tg_max": 0.10,
    # 3.1 tax shares (lower, middle, corporate, upper) and global scale; corruption
    "tax_shares": [0.35, 0.30, 0.20, 0.15], "tax_scale": 0.35, "corruption": 0.2, "tax_eff": 0.0,
    # 3.2 kappa at level 20
    "kappa": {"welfare": 0.10, "health": 0.06, "edu": 0.06, "police": 0.02, "public": 0.04},
    "police_level": 10, "public_level": 10,
    "mil_mult": 1.0, "mil_default_share": 0.003,
    # 4 debt
    "safe_ratio": {"2": 0.2, "4": 0.4, "6": 0.7, "8": 1.0, "10": 1.5},
    "debt_premium": 2.0, "rate_a": 11.0, "rate_b": 0.9, "infl_premium": 0.5,
    "svc_default": 0.35, "svc_months": 3, "default_mult": 3.5,
    "loan_term_years": 10, "dom_share": 0.5, "dom_term": 25, "dom_rate": 3.0, "for_term": 15, "for_rate": 4.0,
    "lender_cap": 3.0,         # max new-borrowing ceiling as multiple of GDP
    # 5 inflation
    "era_infl": [2.0, 7.0, 4.0], "k_sp": 0.02, "k_dp": 0.05,
    # 6 consumer goods
    "delta0": 0.15, "delta_hdi": 0.10, "chi": 0.6, "export_rate": 0.2,
    # 7 education and population
    "edu_cap": 2.5, "edu_rate": 0.08, "pop_growth": 0.008,
    # 9 history layer
    "recession": 0.03, "oil1_imp": 0.05, "oil1_exp": 0.25, "oil1_infl": 4.0, "stagnation": 0.01,
    "rate_shock_cap": 0.25, "rate_shock_spread": 4.0,
}

TUNABLE = {  # key -> (index or None, lo, hi)
    "base0": ("base", 0, 0.01, 8), "base1": ("base", 1, 0.01, 8), "base2": ("base", 2, 0.01, 8),
    "base3": ("base", 3, 0.01, 8), "base4": ("base", 4, 0.01, 8), "base5": ("base", 5, 0.01, 8),
    "sigma": ("sigma", None, 0.0, 40), "tg_base": ("tg_base", None, 0.0, 0.05), "k_sp": ("k_sp", None, 0.0, 0.05),
    "tg_catch": ("tg_catch", None, 0.0, 0.04), "tax_scale": ("tax_scale", None, 0.05, 1.0),
    "edu_rate": ("edu_rate", None, 0.01, 0.3), "chi": ("chi", None, 0.05, 3.0),
}

HERE = os.path.dirname(os.path.abspath(__file__))


def get(overrides=None):
    p = json.loads(json.dumps(PARAMS))
    for k, v in (overrides or {}).items():
        key, idx, _, _ = TUNABLE[k] if k in TUNABLE else (k, None, 0, 0)
        if idx is None:
            p[key] = v
        else:
            p[key][idx] = v
    return p


def load_tuned():
    path = os.path.join(HERE, "params_tuned.json")
    if os.path.exists(path):
        return get(json.load(open(path))["overrides"])
    return get()
