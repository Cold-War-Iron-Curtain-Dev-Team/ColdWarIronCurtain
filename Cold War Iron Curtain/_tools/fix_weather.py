#!/usr/bin/env python3
"""Patch strategic-region weather blocks in Cold War Iron Curtain.

Only regions listed in SPEC (or caught by the snow/mud sweep) are touched.
Everything else is left byte-identical.
"""
import re, math, glob, os, shutil, sys

SRC = "/mnt/user-data/uploads/Cold War Iron Curtain/map/strategicregions"
DST = "/home/claude/fixed/strategicregions"

BETWEEN = ["0.0 30.0", "0.1 27.1", "0.2 30.2", "0.3 29.3", "0.4 30.4", "0.5 29.5",
           "0.6 30.6", "0.7 30.7", "0.8 29.8", "0.9 30.9", "0.10 29.10", "0.11 30.11"]


def phen(mean, wet, heavy, sand):
    """Phenomenon probabilities for one month. Sums to ~1.0."""
    precip = wet
    if mean <= -2:   sf = 1.0
    elif mean >= 4:  sf = 0.0
    else:            sf = (4 - mean) / 6.0
    snow = precip * sf
    rain = precip - snow
    bliz = 0.0
    if mean < -10:
        bliz = snow * 0.25
        snow -= bliz
    rh = rain * heavy
    rl = rain - rh
    sandv = sand if (sand and mean > 15) else 0.0
    none = 1.0 - precip - sandv
    msl = 0.1 if mean < -12 else 0
    return [round(x, 2) for x in (none, rl, rh, snow, bliz)] + [sandv, msl]


def block(w, s, d, south=False, wet=0.35, heavy=0.30, mud=1.0, sand=0.0, lag=0):
    """12 monthly periods from a winter/summer mean, diurnal spread and hemisphere."""
    mid, amp = (s + w) / 2.0, (s - w) / 2.0
    peak = (0 if south else 6) + lag
    out = ["\tweather = {"]
    for m in range(12):
        mean = mid + amp * math.cos(2 * math.pi * (m - peak) / 12.0)
        lo, hi = round(mean - d / 2.0), round(mean + d / 2.0)
        none, rl, rh, snow, bliz, sandv, msl = phen(mean, wet, heavy, sand)
        out += ["\t\tperiod = {",
                f"\t\t\tbetween = {{ {BETWEEN[m]} }}",
                f"\t\t\ttemperature = {{ {lo:g} {hi:g} }}",
                f"\t\t\tno_phenomenon = {none:g}",
                f"\t\t\train_light = {rl:g}",
                f"\t\t\train_heavy = {rh:g}",
                f"\t\t\tsnow = {snow:g}",
                f"\t\t\tblizzard = {bliz:g}",
                "\t\t\tarctic_water = 0",
                f"\t\t\tmud = {mud:g}",
                f"\t\t\tsandstorm = {sandv:g}",
                f"\t\t\tmin_snow_level = {msl:g}",
                "\t\t}"]
    out.append("\t}")
    return "\n".join(out)


SEA = dict(lag=1)   # thermal lag: ocean peaks a month after the solstice

# ---------------------------------------------------------------- §1 missing
SPEC = {
    250: dict(w=-7,  s=20, d=13, wet=.40, mud=1.6),                    # Central Chernozem
    301: dict(w=19,  s=20, d=13, wet=.45, heavy=.40, mud=1.0),         # Lake Victoria basin
    325: dict(w=3,   s=10, d=7,  south=True, wet=.50, mud=1.0),        # Straits of Magellan
    234: dict(w=18,  s=33, d=9,  wet=.08, heavy=.20, **SEA),           # Persian Gulf
    267: dict(w=25,  s=30, d=6,  wet=.10, heavy=.30, **SEA),           # Gulf of Aden
    237: dict(w=-10, s=16, d=10, wet=.40, mud=1.5),                    # Lake Onega
    268: dict(w=-9,  s=17, d=10, wet=.40, mud=1.5),                    # Lake Ladoga
    238: dict(w=10,  s=17, d=8,  wet=.25, heavy=.20, **SEA),           # San Francisco Bay
    269: dict(w=-6,  s=26, d=14, wet=.15, mud=0.8, sand=.05),          # Aral Sea
    315: dict(w=17,  s=29, d=8,  wet=.50, heavy=.45, mud=1.4),         # Tonkin
    266: dict(w=20,  s=29, d=5,  wet=.50, heavy=.45, **SEA),           # Gulf of Tonkin

    # ------------------------------------------------ §2 the 18-region Atlantic block
    44:  dict(w=-1, s=7,  d=5, wet=.50, **SEA),   # Denmark Strait
    45:  dict(w=3,  s=11, d=5, wet=.50, **SEA),   # Norwegian Sea
    46:  dict(w=-4, s=6,  d=5, wet=.45, heavy=.25, **SEA),  # Barents Sea
    50:  dict(w=-2, s=8,  d=5, wet=.50, **SEA),   # Labrador Sea
    55:  dict(w=1,  s=13, d=6, wet=.50, **SEA),   # Newfoundland Sea
    16:  dict(w=5,  s=15, d=6, wet=.50, **SEA),   # North Sea
    173: dict(w=4,  s=16, d=7, wet=.45, **SEA),   # Eastern North Sea
    174: dict(w=2,  s=12, d=6, wet=.50, **SEA),   # Norwegian Coast
    43:  dict(w=9,  s=16, d=6, wet=.50, **SEA),   # Western Approaches
    49:  dict(w=12, s=19, d=6, wet=.40, **SEA),   # Mid Atlantic 1
    51:  dict(w=14, s=21, d=6, wet=.35, **SEA),   # Mid Atlantic 2
    56:  dict(w=16, s=23, d=6, wet=.35, **SEA),   # Mid Atlantic 3
    57:  dict(w=18, s=25, d=6, wet=.30, heavy=.35, **SEA),  # Mid Atlantic 4
    58:  dict(w=19, s=26, d=6, wet=.30, heavy=.35, **SEA),  # Mid Atlantic 5
    59:  dict(w=20, s=27, d=6, wet=.30, heavy=.35, **SEA),  # Mid Atlantic 6
    47:  dict(w=13, s=21, d=7, wet=.35, **SEA),   # Spanish Coast
    48:  dict(w=18, s=24, d=7, wet=.20, **SEA),   # African Coast
    54:  dict(w=7,  s=24, d=8, wet=.40, heavy=.35, **SEA),  # Eastern Seaboard
    170: dict(w=21, s=29, d=7, wet=.40, heavy=.50, **SEA),  # Florida Coast

    # ------------------------------------------------ §3 wrong-climate pastes
    302: dict(w=8,  s=24, d=15, south=True, wet=.15, mud=0.8),          # Cuyo
    194: dict(w=13, s=26, d=11, south=True, wet=.35, heavy=.35),        # Eastern Australia
    278: dict(w=19, s=20, d=12, wet=.50, heavy=.40, mud=1.2),           # Kivu
    298: dict(w=24, s=26, d=10, wet=.55, heavy=.45, mud=1.3),           # Cameroon

    # ------------------------------------------------ §4 seasonless land regions
    30:  dict(w=6,  s=23, d=7,  wet=.40, **SEA),                        # Black Sea
    53:  dict(w=24, s=28, d=7,  wet=.40, heavy=.45, **SEA),             # Caribbean
    76:  dict(w=11, s=27, d=7,  wet=.45, heavy=.40, **SEA),             # East China Sea
    93:  dict(w=26, s=28, d=5,  wet=.50, heavy=.45, **SEA),             # Banda Sea
    169: dict(w=13, s=25, d=7,  wet=.35, **SEA),                        # Tyrrhenian Sea
    195: dict(w=13, s=31, d=16, south=True, wet=.08, mud=0.5, sand=.08),# Central Australia
    254: dict(w=3,  s=15, d=12, south=True, wet=.25, mud=1.0),          # Patagonia

    # ------------------------------------------------ §6 seasonless naval regions
    29:  dict(w=14, s=25, d=7, wet=.30, **SEA),
    32:  dict(w=1,  s=6,  d=4, south=True, wet=.60, heavy=.35, lag=1),
    52:  dict(w=21, s=29, d=6, wet=.35, heavy=.45, **SEA),
    60:  dict(w=25, s=27, d=5, south=True, wet=.35, heavy=.40, lag=1),
    61:  dict(w=23, s=27, d=5, wet=.30, heavy=.35, **SEA),
    62:  dict(w=14, s=20, d=6, south=True, wet=.45, lag=1),
    63:  dict(w=7,  s=17, d=7, south=True, wet=.40, lag=1),
    64:  dict(w=2,  s=8,  d=4, south=True, wet=.55, heavy=.35, lag=1),
    65:  dict(w=13, s=19, d=6, south=True, wet=.50, lag=1),
    66:  dict(w=18, s=24, d=5, south=True, wet=.35, lag=1),
    67:  dict(w=1,  s=7,  d=4, south=True, wet=.55, heavy=.35, lag=1),
    68:  dict(w=13, s=24, d=7, wet=.35, **SEA),
    69:  dict(w=16, s=27, d=7, wet=.30, **SEA),
    70:  dict(w=2,  s=26, d=9, wet=.25, heavy=.25, **SEA),
    71:  dict(w=25, s=28, d=5, south=True, wet=.40, heavy=.40, lag=1),
    72:  dict(w=27, s=29, d=4, wet=.50, heavy=.45, **SEA),
    73:  dict(w=26, s=29, d=5, wet=.50, heavy=.45, **SEA),
    74:  dict(w=18, s=24, d=5, south=True, wet=.40, heavy=.35, lag=1),
    75:  dict(w=24, s=29, d=5, wet=.45, heavy=.45, **SEA),
    77:  dict(w=3,  s=24, d=7, wet=.40, heavy=.35, **SEA),
    78:  dict(w=24, s=29, d=5, wet=.45, heavy=.45, **SEA),
    79:  dict(w=4,  s=23, d=7, wet=.45, heavy=.35, **SEA),
    80:  dict(w=27, s=29, d=4, wet=.50, heavy=.45, **SEA),
    81:  dict(w=22, s=27, d=5, south=True, wet=.40, heavy=.40, lag=1),
    82:  dict(w=25, s=29, d=5, south=True, wet=.45, heavy=.45, lag=1),
    83:  dict(w=26, s=28, d=4, south=True, wet=.50, heavy=.45, lag=1),
    84:  dict(w=26, s=28, d=4, south=True, wet=.50, heavy=.45, lag=1),
    85:  dict(w=20, s=26, d=5, south=True, wet=.40, heavy=.35, lag=1),
    86:  dict(w=12, s=19, d=6, south=True, wet=.45, lag=1),
    87:  dict(w=-6, s=12, d=6, wet=.45, **SEA),
    88:  dict(w=-3, s=8,  d=5, wet=.45, **SEA),
    89:  dict(w=11, s=17, d=6, wet=.40, **SEA),
    90:  dict(w=8,  s=24, d=7, wet=.45, heavy=.35, **SEA),
    91:  dict(w=26, s=29, d=4, south=True, wet=.45, heavy=.45, lag=1),
    92:  dict(w=25, s=29, d=5, south=True, wet=.40, heavy=.45, lag=1),
    94:  dict(w=22, s=28, d=5, wet=.40, heavy=.40, **SEA),
    95:  dict(w=24, s=28, d=5, wet=.40, heavy=.40, **SEA),
    96:  dict(w=2,  s=14, d=6, wet=.45, **SEA),
    97:  dict(w=23, s=27, d=5, south=True, wet=.45, heavy=.40, lag=1),
    98:  dict(w=14, s=19, d=6, south=True, wet=.40, lag=1),
    99:  dict(w=22, s=27, d=5, south=True, wet=.40, heavy=.35, lag=1),
    100: dict(w=24, s=31, d=6, wet=.05, heavy=.20, **SEA),
    101: dict(w=25, s=29, d=5, wet=.50, heavy=.50, **SEA),
    102: dict(w=25, s=28, d=5, south=True, wet=.35, heavy=.40, lag=1),
    103: dict(w=23, s=27, d=5, south=True, wet=.40, heavy=.40, lag=1),
    104: dict(w=24, s=29, d=5, wet=.25, heavy=.35, **SEA),
    105: dict(w=22, s=27, d=5, wet=.30, heavy=.35, **SEA),
    106: dict(w=23, s=29, d=6, wet=.30, heavy=.40, **SEA),
    107: dict(w=26, s=28, d=4, wet=.50, heavy=.45, **SEA),
    108: dict(w=9,  s=18, d=6, south=True, wet=.40, lag=1),
    109: dict(w=18, s=23, d=5, south=True, wet=.15, heavy=.20, lag=1),
    110: dict(w=21, s=26, d=5, wet=.30, heavy=.35, **SEA),
    111: dict(w=20, s=26, d=5, wet=.30, heavy=.35, **SEA),
    112: dict(w=6,  s=13, d=5, south=True, wet=.50, lag=1),
    113: dict(w=18, s=24, d=5, south=True, wet=.35, heavy=.35, lag=1),
    114: dict(w=2,  s=12, d=5, wet=.50, **SEA),
    115: dict(w=5,  s=14, d=6, wet=.50, **SEA),
    166: dict(w=-14,s=9,  d=7, wet=.40, heavy=.25, **SEA),
    168: dict(w=11, s=24, d=7, wet=.35, **SEA),
    171: dict(w=7,  s=15, d=6, wet=.55, heavy=.35, **SEA),
    172: dict(w=20, s=26, d=5, south=True, wet=.35, heavy=.35, lag=1),
    175: dict(w=18, s=24, d=5, south=True, wet=.30, lag=1),
    176: dict(w=11, s=20, d=5, wet=.35, **SEA),
    177: dict(w=12, s=22, d=6, wet=.40, heavy=.35, **SEA),
    178: dict(w=25, s=28, d=4, south=True, wet=.45, heavy=.45, lag=1),
    179: dict(w=24, s=27, d=4, south=True, wet=.40, heavy=.40, lag=1),
    180: dict(w=26, s=29, d=4, wet=.45, heavy=.45, **SEA),

    # ------------------------------------------------ §7 two-state stub curves
    18:  dict(w=7,  s=17, d=6,  wet=.50, **SEA),                        # Channel
    42:  dict(w=11, s=20, d=6,  wet=.45, **SEA),                        # Bay of Biscay
    9:   dict(w=0,  s=17, d=7,  wet=.45, **SEA),                        # Baltic Sea
    127: dict(w=12, s=34, d=18, wet=.03, heavy=.4, mud=0.3, sand=.12),  # Sahara desert
}

# regions whose land has no reason to be mud-proof (mud = 0 year round)
MUD_FIX = {121, 138, 205, 320, 21, 212, 214, 146, 232, 256, 36}
SNOW_MIN = -2.0     # below this monthly mean, some snow must be possible


def sweep(text):
    """Snow/mud repairs applied to regions we are not regenerating."""
    changed = False

    def fix_period(m):
        nonlocal changed
        body = m.group(0)
        t = re.search(r'temperature\s*=\s*\{\s*(-?[\d.]+)\s+(-?[\d.]+)\s*\}', body)
        if not t:
            return body
        lo, hi = float(t.group(1)), float(t.group(2))
        mean = (lo + hi) / 2

        def get(k):
            g = re.search(rf'\b{k}\s*=\s*(-?[\d.]+)', body)
            return float(g.group(1)) if g else 0.0

        def setv(b, k, v):
            return re.sub(rf'(\b{k}\s*=\s*)(-?[\d.]+)', lambda x: f"{x.group(1)}{v:g}", b, count=1)

        snow, bliz, none_, rl = get('snow'), get('blizzard'), get('no_phenomenon'), get('rain_light')
        mud = get('mud')

        # cold month with no frozen precipitation at all
        if mean < SNOW_MIN and snow + bliz == 0:
            take = min(0.35, max(0.1, none_ * 0.5 + rl))
            new_snow = round(take * (0.75 if mean > -12 else 0.7), 2)
            new_bliz = round(take - new_snow, 2) if mean < -12 else 0.0
            body = setv(body, 'snow', new_snow)
            if new_bliz:
                body = setv(body, 'blizzard', new_bliz)
            body = setv(body, 'rain_light', round(max(0.0, rl - take * 0.4), 2))
            body = setv(body, 'no_phenomenon', round(max(0.05, none_ - take * 0.6), 2))
            changed = True

        # snow where the month never gets near freezing
        if lo > 8 and snow + bliz > 0:
            body = setv(body, 'rain_light', round(rl + snow + bliz, 2))
            body = setv(body, 'snow', 0)
            body = setv(body, 'blizzard', 0)
            changed = True

        # sentinel / disabled mud
        if mud > 10 or (mud == 0 and RID in MUD_FIX):
            body = setv(body, 'mud', 1)
            changed = True
        return body

    text = re.sub(r'period\s*=\s*\{.*?\n\t\t\}', fix_period, text, flags=re.S)
    return text, changed


if __name__ == "__main__":
    os.makedirs(DST, exist_ok=True)
    rewritten, swept, untouched = [], [], 0
    for f in sorted(glob.glob(os.path.join(SRC, "*.txt"))):
        s = open(f, encoding='utf-8-sig', errors='replace').read()
        RID = int(re.search(r'\bid\s*=\s*(\d+)', s).group(1))
        name = os.path.basename(f)
        if RID in SPEC:
            new_block = block(**SPEC[RID])
            if re.search(r'\n\tweather\s*=\s*\{', s):
                out = re.sub(r'\n\tweather\s*=\s*\{.*?\n\t\}', "\n" + new_block, s, flags=re.S)
            else:  # 301 uses no-tab, no-space style
                out = re.sub(r'\n\s*weather\s*=\s*\{.*?\n\s*\}', "\n" + new_block, s, flags=re.S)
            assert out != s and 'period' in out, name
            rewritten.append(name)
        else:
            out, ch = sweep(s)
            if ch:
                swept.append(name)
            else:
                untouched += 1
        if out != s:
            open(os.path.join(DST, name), 'w', encoding='utf-8', newline='\n').write(out)
    print(f"regenerated : {len(rewritten)}")
    print(f"swept       : {len(swept)}")
    print(f"untouched   : {untouched}")
    print("swept regions:", ", ".join(swept))
