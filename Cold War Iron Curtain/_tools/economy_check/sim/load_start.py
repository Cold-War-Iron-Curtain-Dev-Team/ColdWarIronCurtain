"""Parse the 1949.5.23 start from the mod into sim/start_1949.json.

Usage (from mod root): python _tools/economy_check/sim/load_start.py
"""
import glob, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
MOD = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
START = (1949, 5, 23)
BUILDINGS = ["industrial_complex", "arms_factory", "dockyard", "office_park", "agri_industrial_complex",
             "steel_factory", "tungsten_factory", "infrastructure"]
RESOURCES = ["oil", "aluminium", "rubber", "tungsten", "steel", "chromium"]
EDU = ["literate_educated", "primary_educated", "high_school_educated", "college_educated"]
TOK = re.compile(r'"[^"]*"|[{}=]|[^\s{}=]+')
DATE = re.compile(r"^(\d{4})\.(\d+)\.(\d+)$")


def parse(text):
    """Clausewitz text -> list of (key, value) pairs; value is a scalar string or a nested pair list."""
    text = re.sub(r"#[^\n]*", "", text)
    toks = TOK.findall(text)
    pos = 0

    def block():
        nonlocal pos
        out = []
        while pos < len(toks):
            t = toks[pos]
            if t == "}":
                pos += 1
                return out
            if pos + 1 < len(toks) and toks[pos + 1] == "=":
                pos += 2
                if toks[pos] == "{":
                    pos += 1
                    out.append((t, block()))
                else:
                    out.append((t, toks[pos]))
                    pos += 1
            else:
                pos += 1
        return out
    return block()


def pairs_of(blk, key):
    return [v for k, v in blk if k == key]


def active_blocks(blk):
    """The block itself, then dated sub-blocks on or before the start date, in order."""
    res = [blk]
    dated = []
    for k, v in blk:
        m = DATE.match(k)
        if m and isinstance(v, list):
            d = tuple(int(x) for x in m.groups())
            if d <= START:
                dated.append((d, v))
    return res + [v for _, v in sorted(dated, key=lambda x: x[0])]


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def setvars(blk, into):
    for v in pairs_of(blk, "set_variable"):
        if isinstance(v, list) and v and isinstance(v[0][1], str):
            into[v[0][0]] = num(v[0][1], v[0][1])


def derive_development(cat):
    """CWIC_state_category_cache: popN -> 1, popNdevM -> 1+M."""
    m = re.search(r"dev(\d+)$", cat or "")
    return 1 + int(m.group(1)) if m else 1


def load_states():
    states = {}
    for f in glob.glob(os.path.join(MOD, "history", "states", "*.txt")):
        top = parse(open(f, encoding="utf-8", errors="replace").read())
        st = pairs_of(top, "state")
        if not st:
            continue
        st = st[0]
        sid = int(pairs_of(st, "id")[0])
        rec = {"id": sid, "owner": None, "manpower": num(pairs_of(st, "manpower")[0]) if pairs_of(st, "manpower") else 0.0,
               "category": (pairs_of(st, "state_category") or [None])[0], "b": {k: 0.0 for k in BUILDINGS},
               "r": {k: 0.0 for k in RESOURCES}, "coal": 0.0, "edu": {k: 0.0 for k in EDU}, "flags": []}
        for res in pairs_of(st, "resources"):
            for k, v in res:
                if k in rec["r"]:
                    rec["r"][k] = num(v)
        hist = (pairs_of(st, "history") or [[]])[0]
        for blk in [st] + [hb for hb in active_blocks(hist)]:
            for o in pairs_of(blk, "owner"):
                rec["owner"] = o
            for c in pairs_of(blk, "set_state_category"):
                rec["category"] = c
            for a in pairs_of(blk, "add_manpower"):
                rec["manpower"] += num(a)
            for fl in pairs_of(blk, "set_state_flag"):
                rec["flags"].append(fl)
            for bb in pairs_of(blk, "buildings"):
                for k, v in bb:
                    if k in rec["b"] and isinstance(v, str):
                        rec["b"][k] = num(v)
            vv = {}
            setvars(blk, vv)
            for k in EDU:
                if k in vv:
                    rec["edu"][k] = vv[k]
            if "coal_amount" in vv:
                rec["coal"] = vv["coal_amount"]
        rec["dev"] = derive_development(rec["category"])
        if rec["owner"]:
            states[sid] = rec
    return states


def load_countries():
    out = {}
    for f in glob.glob(os.path.join(MOD, "history", "countries", "*.txt")):
        tag = os.path.basename(f)[:3]
        top = parse(open(f, encoding="utf-8", errors="replace").read())
        vv, ideas = {}, []
        for blk in active_blocks(top):
            setvars(blk, vv)
            for ai in pairs_of(blk, "add_ideas"):
                ideas += [ai] if isinstance(ai, str) else [k for k, _ in ai] + [v for _, v in ai if isinstance(v, str)]
        out[tag] = {"x": vv.get("economic_x_axis"), "y": vv.get("economic_y_axis"), "vars": vv, "ideas": ideas}
    return out


def main():
    states, countries = load_states(), load_countries()
    data = {"states": states, "countries": countries}
    path = os.path.join(HERE, "start_1949.json")
    json.dump(data, open(path, "w"))
    owners = {s["owner"] for s in states.values()}
    print(f"{len(states)} owned states, {len(owners)} owners, {len(countries)} country files -> {path}")


if __name__ == "__main__":
    main()
