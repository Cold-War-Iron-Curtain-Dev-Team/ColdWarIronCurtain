"""CWIC naval module + tech icon generator (NSB armour schematic style).

Every design draws its art ONCE in a local 60x26 box (x 0..59, y 0..25) and is
rendered twice:
  * module icon  76x42  -> art at (8,1),  label rows 31-39   (equipment designer)
  * tech icon    64x64  -> art at (2,12), label rows 42-50   (same layout as the
    NSB armour tech icons, which are the 56x42 module icon pasted at (4,11))

Run from the mod root:  python "gfx/interface/equipmentdesigner/naval/Modules/_tools/naval_icons.py"
  --sheet <png>   also writes a review contact sheet
It writes the PNGs and regenerates interface/cwic_naval_rework_icons.gfx.
See NAVAL_ICON_STYLE_PROMPT.md for the style rules.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from draw import Canvas, label

MOD_DIR = 'gfx/interface/equipmentdesigner/naval/Modules'
TECH_DIR = 'gfx/interface/technologies/cwic_naval_rework'
GFX_FILE = 'interface/cwic_naval_rework_icons.gfx'

# ======================================================================
# drawing helpers (local coordinates)
# ======================================================================
def shifted(c, dx, dy, fn, *a, **k):
    c.ox += dx; c.oy += dy
    try: fn(c, *a, **k)
    finally: c.ox -= dx; c.oy -= dy

def fin(c, xr, y_root, h, sweep, chord, up, col='B'):
    """filled swept fin: trailing edge at xr, root row y_root, grows away from body"""
    d = -1 if up else 1
    for i in range(h):
        xl = xr - chord + 1 + sweep * (i + 1)
        c.hl(min(xl, xr), xr, y_root + d * i, col)

# ---- guns -------------------------------------------------------------
def barrel(c, x0, x1, cy, h):           # hollow green tube, outlines at cy-h / cy+h
    c.hl(x0, x1, cy - h, 'G'); c.hl(x0, x1, cy + h, 'G')

def muzzle_plain(c, x, cy, h):
    c.vl(x, cy - h, cy + h, 'Y')

def muzzle_brake(c, x0, cy, h, baffles=1, w=5):
    c.p(x0 - 1, cy - h, 'Y'); c.p(x0 - 1, cy + h, 'Y')
    c.rect(x0, cy - h - 1, x0 + w - 1, cy + h + 1, 'B')
    for i in range(baffles):
        c.vl(x0 + 2 + 2 * i, cy - h - 1, cy + h + 1, 'B')

def ring(c, x0, x1, cy, hh, inner=False):   # bore evacuator / fume extractor
    c.rect(x0, cy - hh, x1, cy + hh, 'B')
    if inner: c.vl(x0 + 2, cy - hh, cy + hh, 'B')

def jacket(c, x0, x1, cy, h):               # perforated cooling jacket
    c.hl(x0, x1, cy - h - 1, 'B'); c.hl(x0, x1, cy + h + 1, 'B')
    for x in range(x0, x1 + 1, 3): c.vl(x, cy - h - 1, cy + h + 1, 'B')

def slide(c, x0, x1, cy, hh):               # recoil sleeve / cradle, stepped wider
    c.hl(x0, x1, cy - hh, 'G'); c.hl(x0, x1, cy + hh, 'G')
    c.vl(x0, cy - hh + 1, cy - 2, 'G'); c.vl(x0, cy + 2, cy + hh - 1, 'G')
    c.vl(x1, cy - hh + 1, cy + hh - 1, 'G')

def house(c, x0, x1, cy, hh, diamond=True, inner=True):   # breech / mount block
    y0, y1 = cy - hh, cy + hh
    c.hl(x0 + 1, x1 - 3, y0, 'B'); c.hl(x0 + 1, x1 - 4, y1, 'B'); c.vl(x0, y0 + 1, y1 - 1, 'B')
    c.p(x1 - 2, y0 + 1, 'B'); c.vl(x1 - 1, y0 + 2, y1 - 3, 'B'); c.p(x1 - 2, y1 - 2, 'B'); c.p(x1 - 3, y1 - 1, 'B')
    if inner: c.vl(x0 + 2, y0 + 2, y1 - 2, 'B')
    if diamond:
        dx = x0 + 6
        c.p(dx, cy - 1, 'B'); c.p(dx - 1, cy, 'B'); c.p(dx + 1, cy, 'B'); c.p(dx, cy + 1, 'B')

def drum(c, x0, x1, y0, y1, step=3, col='R'):   # ribbed loading drum / magazine
    c.rect(x0, y0, x1, y1, col)
    for x in range(x0 + step, x1, step): c.vl(x, y0 + 1, y1 - 1, col)

def hoist(c, x0, x1, y0, y1):
    c.rect(x0, y0, x1, y1, 'R'); c.vl((x0 + x1) // 2, y0 + 1, y1 - 1, 'R')
    for y in range(y0 + 2, y1, 2):
        c.hl(x0 + 1, (x0 + x1) // 2 - 1, y, 'R'); c.hl((x0 + x1) // 2 + 1, x1 - 1, y, 'R')

def shell(c, x0, x1, cy):                       # white round, yellow fuze, blue band
    c.p(x0, cy, 'Y'); c.line(x0 + 1, cy - 1, x0 + 3, cy - 2, 'Y'); c.line(x0 + 1, cy + 1, x0 + 3, cy + 2, 'Y')
    c.hl(x0 + 4, x1, cy - 2, 'W'); c.hl(x0 + 4, x1, cy + 2, 'W'); c.vl(x1, cy - 1, cy + 1, 'W')
    c.vl(x1 - 4, cy - 2, cy + 2, 'B')

def simple_gun(c, cy, h, bx0, bx1, sx1, hx1, hh, sh=None, muzzle='plain'):
    """barrel bx0..bx1, slide bx1+1..sx1, housing sx1+2..hx1"""
    if muzzle == 'plain': muzzle_plain(c, bx0 - 1, cy, h)
    barrel(c, bx0, bx1, cy, h)
    slide(c, bx1 + 1, sx1, cy, sh or h + 2)
    house(c, sx1 + 2, hx1, cy, hh)

# ---- light guns ---------------------------------------------------------
def L_ww(c):    # twin 4"/45 QF Mk XVI
    def one(c): simple_gun(c, 5, 1, 2, 31, 38, 54, 3)
    one(c); shifted(c, 4, 12, one)
def L_0(c):     # 3"/50 Mk 22
    simple_gun(c, 12, 1, 6, 34, 41, 56, 4)
def L_1(c):     # twin 76 mm AK-726
    def one(c):
        simple_gun(c, 5, 1, 2, 33, 39, 55, 3); ring(c, 12, 16, 5, 2)
    one(c); shifted(c, 3, 12, one)
def L_2(c):     # OTO Melara 76/62 Compact
    cy = 11
    muzzle_brake(c, 2, cy, 1)
    barrel(c, 7, 31, cy, 1); ring(c, 15, 21, cy, 3)
    slide(c, 32, 40, cy, 3); house(c, 42, 59, cy, 5)
    drum(c, 45, 57, cy + 7, cy + 10)
def L_3(c):     # OTO Melara 76/62 Super Rapid
    cy = 11
    muzzle_brake(c, 1, cy, 1, baffles=2, w=7)
    barrel(c, 8, 31, cy, 1); ring(c, 15, 21, cy, 3); c.vl(25, cy - 2, cy + 2, 'B'); c.vl(27, cy - 2, cy + 2, 'B')
    slide(c, 32, 40, cy, 3); house(c, 42, 59, cy, 5)
    drum(c, 43, 58, cy + 7, cy + 10, step=2)
def L_4(c):     # Bofors 57 mm Mk 3
    cy = 13
    muzzle_brake(c, 3, cy, 1, baffles=1)
    barrel(c, 8, 34, cy, 1); jacket(c, 10, 28, cy, 1)
    slide(c, 35, 41, cy, 3); house(c, 43, 59, cy, 5)
    drum(c, 45, 57, cy - 10, cy - 7, step=2)

# ---- medium guns --------------------------------------------------------
def M_ww(c):    # 5"/38 Mk 12
    simple_gun(c, 12, 2, 11, 35, 42, 58, 5)
def M_0(c):     # twin 5.25" QF Mk I
    def one(c): simple_gun(c, 5, 2, 3, 32, 38, 55, 4)
    one(c); shifted(c, 4, 13, one)
def M_1(c):     # 5"/54 Mk 42 (twin loading drums)
    cy = 10
    simple_gun(c, cy, 2, 4, 33, 41, 59, 6)
    drum(c, 43, 50, cy + 8, cy + 12); drum(c, 52, 59, cy + 8, cy + 12)
def M_2(c):     # 5"/54 Mk 45 Mod 0
    cy = 10
    muzzle_plain(c, 2, cy, 2); barrel(c, 3, 33, cy, 2); ring(c, 12, 20, cy, 4, inner=True)
    slide(c, 34, 41, cy, 4); house(c, 43, 59, cy, 6)
    hoist(c, 48, 56, cy + 8, cy + 14)
def M_3(c):     # twin 130 mm AK-130
    def one(c):
        muzzle_plain(c, 1, 5, 2); barrel(c, 2, 32, 5, 2); ring(c, 10, 16, 5, 3, inner=True)
        slide(c, 33, 39, 5, 4); house(c, 41, 56, 5, 4)
    one(c); shifted(c, 3, 14, one)
def M_4(c):     # OTO Melara 127/64 LW (four revolving drums)
    cy = 10
    muzzle_brake(c, 2, cy, 2)
    barrel(c, 7, 33, cy, 2)
    slide(c, 34, 41, cy, 4); house(c, 43, 59, cy, 6)
    for i in range(4): drum(c, 42 + i * 5, 45 + i * 5, cy + 8, cy + 12, step=9)

# ---- heavy guns ---------------------------------------------------------
def H_ww(c):    # 6"/47 Mk 16
    cy = 11
    muzzle_plain(c, 4, cy, 2); barrel(c, 5, 20, cy, 2); barrel(c, 21, 34, cy, 3); c.vl(21, cy - 3, cy - 2, 'G'); c.vl(21, cy + 2, cy + 3, 'G')
    slide(c, 35, 41, cy, 5); house(c, 43, 59, cy, 7)
def H_0(c):     # 6"/47 DP Mk 16 (automatic, Worcester)
    H_ww(c); hoist(c, 47, 56, 20, 25)
def H_1(c):     # 8"/55 Mk 16 (automatic, Salem)
    cy = 10
    muzzle_plain(c, 1, cy, 2); barrel(c, 2, 17, cy, 2); barrel(c, 18, 33, cy, 3); c.vl(18, cy - 3, cy - 2, 'G'); c.vl(18, cy + 2, cy + 3, 'G')
    slide(c, 34, 40, cy, 6); house(c, 42, 59, cy, 8)
    hoist(c, 46, 56, cy + 10, cy + 15)
def H_2(c):     # 8"/55 Mk 71 MCLWG
    cy = 10
    muzzle_plain(c, 1, cy, 2); barrel(c, 2, 33, cy, 2); ring(c, 9, 18, cy, 4, inner=True)
    slide(c, 34, 41, cy, 5); house(c, 43, 59, cy, 7)
    hoist(c, 47, 57, cy + 9, cy + 15)
def H_3(c):     # 155 mm Advanced Gun System
    cy = 9
    muzzle_plain(c, 1, cy, 2); barrel(c, 2, 33, cy, 2); jacket(c, 6, 30, cy, 2)
    slide(c, 34, 41, cy, 5); house(c, 43, 59, cy, 7)
    drum(c, 41, 59, cy + 10, cy + 15, step=3)

# ---- super-heavy guns -----------------------------------------------------
def S_0(c):     # 16"/50 Mk 7 (stepped chase, huge breech)
    cy = 12
    muzzle_plain(c, 1, cy, 2)
    barrel(c, 2, 13, cy, 2)
    barrel(c, 14, 25, cy, 3); c.vl(14, cy - 3, cy - 2, 'G'); c.vl(14, cy + 2, cy + 3, 'G')
    barrel(c, 26, 34, cy, 4); c.vl(26, cy - 4, cy - 3, 'G'); c.vl(26, cy + 3, cy + 4, 'G')
    slide(c, 35, 41, cy, 6); house(c, 43, 59, cy, 9)
    c.rect(52, cy - 3, 56, cy + 3, 'B')                  # breech block
def S_1(c):     # 16"/50 Mk 7, 1980s reactivation (+ improved shells)
    S_0(c); shell(c, 5, 24, 3)

# ---- torpedoes ----------------------------------------------------------
def torp_body(c, x0, x1, cy, r, nose='round', ncol='Y'):
    t, b = cy - r, cy + r
    if nose == 'round':
        c.vl(x0, t + 2, b - 2, ncol); c.p(x0 + 1, t + 1, ncol); c.p(x0 + 1, b - 1, ncol)
        c.hl(x0 + 2, x0 + 4, t, ncol); c.hl(x0 + 2, x0 + 4, b, ncol); c.vl(x0 + 5, t + 1, b - 1, ncol)
        hx = x0 + 6
    elif nose == 'flat':
        c.vl(x0, t + 1, b - 1, ncol); c.hl(x0 + 1, x0 + 3, t, ncol); c.hl(x0 + 1, x0 + 3, b, ncol); c.vl(x0 + 3, t + 1, b - 1, ncol)
        hx = x0 + 4
    else:  # 'pointed'
        c.p(x0, cy, ncol); c.line(x0 + 1, cy - 1, x0 + r, t, ncol); c.line(x0 + 1, cy + 1, x0 + r, b, ncol)
        c.vl(x0 + r + 1, t + 1, b - 1, ncol); hx = x0 + r + 1
    c.hl(hx, x1, t, 'W'); c.hl(hx, x1, b, 'W')
    return t, b

def tail_cone(c, x, cy, r, n=3):
    t, b = cy - r, cy + r
    c.line(x, t, x + n, t + n, 'W'); c.line(x, b, x + n, b - n, 'W'); c.vl(x + n + 1, t + n, b - n, 'W')
    return x + n + 1

def props(c, x, cy, r):
    c.hl(x, x + 4, cy, 'B'); c.vl(x + 1, cy - r, cy + r, 'B'); c.vl(x + 3, cy - r + 1, cy + r - 1, 'B')

def duct(c, x0, x1, cy, r):     # pump-jet shroud
    c.rect(x0, cy - r, x1, cy + r, 'B'); c.vl(x0 + 2, cy - r + 1, cy + r - 1, 'B')

def wire(c, x, cy):             # guidance wire + dispenser
    c.rect(x, cy - 1, x + 2, cy + 1, 'R'); c.hl(x + 3, 59, cy + 3, 'R'); c.vl(x + 3, cy + 1, cy + 3, 'R')

def T_ww(c):    # Mk 15 21-inch destroyer torpedo
    cy, r = 12, 3
    t, b = torp_body(c, 2, 46, cy, r, 'round', 'W')
    for x in (13, 30): c.vl(x, t, b, 'B')
    e = tail_cone(c, 47, cy, r, 2)
    c.rect(43, t - 3, 49, t - 1, 'B'); c.rect(43, b + 1, 49, b + 3, 'B')      # box fins
    props(c, e + 1, cy, 3)
def T_0(c):     # Mk 24 "Fido" acoustic homing
    cy, r = 12, 5
    t, b = torp_body(c, 8, 42, cy, r, 'round')
    c.vl(24, t, b, 'B')
    e = tail_cone(c, 43, cy, r, 2)
    c.rect(43, cy - 7, 52, cy + 7, 'B')                                       # ring tail
    props(c, e + 1, cy, 3)
def T_1(c):     # Mk 44
    cy, r = 12, 4
    t, b = torp_body(c, 6, 44, cy, r, 'flat')
    for x in (18, 30): c.vl(x, t, b, 'B')
    e = tail_cone(c, 45, cy, r)
    fin(c, 47, t - 1, 3, 1, 5, True); fin(c, 47, b + 1, 3, 1, 5, False)
    props(c, e + 1, cy, 3)
def T_2(c):     # Mk 46
    cy, r = 12, 4
    t, b = torp_body(c, 4, 45, cy, r, 'round')
    for x in (19, 21, 33): c.vl(x, t, b, 'B')
    e = tail_cone(c, 46, cy, r)
    fin(c, 48, t - 1, 3, 1, 5, True); fin(c, 48, b + 1, 3, 1, 5, False)
    props(c, e + 1, cy, 4)
def T_3(c):     # Sting Ray (pump-jet)
    cy, r = 12, 4
    t, b = torp_body(c, 4, 44, cy, r, 'round')
    for x in (17, 31): c.vl(x, t, b, 'B')
    e = tail_cone(c, 45, cy, r, 2)
    fin(c, 47, t - 1, 2, 1, 4, True); fin(c, 47, b + 1, 2, 1, 4, False)
    duct(c, e, e + 6, cy, 4)
def T_4(c):     # MU90 Impact (pump-jet, long seeker)
    cy, r = 12, 4
    t, b = torp_body(c, 2, 46, cy, r, 'flat')
    c.vl(9, t, b, 'Y'); c.hl(4, 9, t, 'Y'); c.hl(4, 9, b, 'Y')
    for x in (20, 34): c.vl(x, t, b, 'B')
    e = tail_cone(c, 47, cy, r, 2)
    fin(c, 49, t - 1, 2, 1, 4, True); fin(c, 49, b + 1, 2, 1, 4, False)
    duct(c, e, e + 6, cy, 4)
def TL_0(c):    # Mk 37 Mod 1 wire-guided
    cy, r = 10, 5
    t, b = torp_body(c, 2, 44, cy, r, 'round')
    for x in (16, 30): c.vl(x, t, b, 'B')
    e = tail_cone(c, 45, cy, r, 3)
    fin(c, 47, t - 1, 3, 1, 5, True); fin(c, 47, b + 1, 3, 1, 5, False)
    props(c, e + 1, cy, 5); wire(c, 44, cy + 9)
def TL_1(c):    # Mk 48 (pump-jet, wire)
    cy, r = 10, 5
    t, b = torp_body(c, 1, 47, cy, r, 'round')
    for x in (14, 27, 38): c.vl(x, t, b, 'B')
    e = tail_cone(c, 48, cy, r, 2)
    duct(c, e, e + 6, cy, 5); wire(c, 44, cy + 9)
def TL_2(c):    # Spearfish (pointed seeker, pump-jet, wire)
    cy, r = 10, 5
    t, b = torp_body(c, 1, 48, cy, r, 'pointed')
    for x in (12, 24, 36): c.vl(x, t, b, 'B')
    e = tail_cone(c, 49, cy, r, 2)
    duct(c, e, e + 6, cy, 5); wire(c, 45, cy + 9)

# ---- anti-ship missiles (light line) ------------------------------------
def A_0(c):     # SS-N-1 Scrubber
    t, b = 10, 14
    c.vl(2, t, b, 'B'); c.vl(3, t + 1, b - 1, 'B')
    c.hl(3, 48, t, 'W'); c.hl(3, 48, b, 'W'); c.line(49, t + 1, 51, t + 2, 'W'); c.line(49, b - 1, 51, b - 2, 'W'); c.vl(52, t + 2, b - 2, 'Y')
    fin(c, 28, t - 1, 4, 2, 10, True); fin(c, 28, b + 1, 4, 2, 10, False)
    c.line(40, t - 1, 46, t - 7, 'B'); c.hl(46, 49, t - 7, 'B'); c.line(49, t - 7, 50, t - 1, 'B')
    c.rect(18, b + 3, 46, b + 6, 'Y'); c.hl(47, 49, b + 4, 'Y')
    fin(c, 48, b + 7, 3, 1, 5, False)
def A_1(c):     # P-15 Termit
    t, b = 9, 17
    c.vl(2, t + 3, b - 3, 'W'); c.p(3, t + 2, 'W'); c.p(3, b - 2, 'W'); c.p(4, t + 1, 'W'); c.p(4, b - 1, 'W')
    c.hl(5, 47, t, 'W'); c.hl(5, 47, b, 'W'); c.line(48, t + 1, 50, t + 3, 'W'); c.line(48, b - 1, 50, b - 3, 'W'); c.vl(51, t + 3, b - 3, 'Y')
    c.vl(12, t, b, 'B')
    fin(c, 28, t - 1, 5, 3, 14, True)
    c.line(38, t - 1, 43, t - 7, 'B'); c.hl(43, 48, t - 7, 'B'); c.vl(48, t - 6, t - 1, 'B')
    c.hl(42, 47, b + 1, 'B'); c.hl(44, 47, b + 2, 'B')
    c.p(28, b + 4, 'Y'); c.hl(29, 43, b + 3, 'Y'); c.hl(29, 43, b + 7, 'Y'); c.vl(28, b + 5, b + 6, 'Y')
    c.line(44, b + 3, 47, b + 5, 'Y'); c.line(44, b + 7, 47, b + 6, 'Y')
def A_2(c):     # MM38 Exocet
    t, b = 11, 15
    c.p(1, 13, 'Y'); c.line(2, 12, 6, t, 'W'); c.line(2, 14, 6, b, 'W')
    c.hl(7, 42, t, 'W'); c.hl(7, 42, b, 'W'); c.vl(14, t, b, 'B')
    c.hl(43, 56, t, 'Y'); c.hl(43, 56, b, 'Y'); c.vl(43, t, b, 'Y'); c.vl(57, t + 1, b - 1, 'Y')
    fin(c, 41, t - 1, 5, 3, 15, True); fin(c, 41, b + 1, 5, 3, 15, False)
    fin(c, 56, t - 1, 4, 1, 6, True); fin(c, 56, b + 1, 4, 1, 6, False)
def A_3(c):     # RGM-84 Harpoon (+ booster)
    t, b = 11, 15
    c.vl(1, t + 1, b - 1, 'Y'); c.p(2, t, 'Y'); c.p(2, b, 'Y'); c.vl(6, t + 1, b - 1, 'Y'); c.hl(3, 5, t, 'Y'); c.hl(3, 5, b, 'Y')
    c.hl(7, 40, t, 'W'); c.hl(7, 40, b, 'W'); c.vl(18, t, b, 'B'); c.vl(40, t, b, 'W')
    fin(c, 27, t - 1, 4, 2, 8, True); fin(c, 27, b + 1, 4, 2, 8, False)
    c.line(30, b + 1, 31, b + 2, 'B'); c.hl(32, 36, b + 2, 'B')
    fin(c, 39, t - 1, 4, 1, 6, True); fin(c, 39, b + 1, 3, 1, 6, False)
    c.hl(42, 57, t - 1, 'Y'); c.hl(42, 57, b + 1, 'Y'); c.vl(42, t, b, 'Y'); c.vl(58, t, b, 'Y')
    fin(c, 57, t - 2, 4, 1, 5, True); fin(c, 57, b + 2, 4, 1, 5, False)
def A_4(c):     # P-800 Oniks
    t, b = 10, 16
    c.hl(1, 5, 13, 'Y'); c.vl(5, 12, 14, 'Y')
    c.vl(6, t, b, 'B'); c.vl(7, t, b, 'B')
    c.hl(8, 54, t, 'W'); c.hl(8, 54, b, 'W'); c.vl(24, t, b, 'B')
    c.hl(55, 58, t + 1, 'Y'); c.hl(55, 58, b - 1, 'Y'); c.vl(58, t + 1, b - 1, 'Y')
    fin(c, 39, t - 1, 3, 1, 7, True); fin(c, 39, b + 1, 3, 1, 7, False)
    fin(c, 53, t - 1, 4, 1, 6, True); fin(c, 53, b + 1, 4, 1, 6, False)

# ---- anti-ship missiles (heavy line) ------------------------------------
def AH_0(c):    # P-35 / SS-N-3 Shaddock
    t, b = 9, 15
    c.p(1, 12, 'W'); c.line(2, 11, 5, t, 'W'); c.line(2, 13, 5, b, 'W')
    c.hl(6, 50, t, 'W'); c.hl(6, 50, b, 'W'); c.line(51, t + 1, 52, t + 2, 'W'); c.line(51, b - 1, 52, b - 2, 'W'); c.vl(53, t + 2, b - 2, 'Y')
    c.vl(12, t, b, 'B')
    fin(c, 30, t - 1, 4, 2, 9, True)                                   # folding wing
    c.line(23, b + 1, 24, b + 2, 'B'); c.hl(25, 32, b + 2, 'B'); c.vl(32, b + 1, b + 1, 'B')   # ventral intake
    fin(c, 50, t - 1, 5, 1, 7, True)                                   # dorsal fin
    c.hl(38, 51, b + 4, 'Y'); c.hl(38, 51, b + 8, 'Y'); c.vl(37, b + 5, b + 7, 'Y'); c.line(52, b + 4, 54, b + 5, 'Y'); c.line(52, b + 8, 54, b + 7, 'Y'); c.vl(55, b + 5, b + 7, 'Y')
    fin(c, 50, b + 9, 2, 1, 4, False)
def AH_1(c):    # P-120 Malakhit / SS-N-9 Siren
    t, b = 10, 16
    c.vl(1, t + 2, b - 2, 'Y'); c.p(2, t + 1, 'Y'); c.p(2, b - 1, 'Y'); c.vl(5, t + 1, b - 1, 'Y'); c.hl(3, 4, t, 'Y'); c.hl(3, 4, b, 'Y')
    c.hl(6, 42, t, 'W'); c.hl(6, 42, b, 'W'); c.vl(16, t, b, 'B')
    c.hl(43, 56, t, 'Y'); c.hl(43, 56, b, 'Y'); c.vl(43, t, b, 'Y'); c.vl(57, t + 1, b - 1, 'Y')
    fin(c, 34, t - 1, 6, 2, 13, True); fin(c, 34, b + 1, 6, 2, 13, False)
    fin(c, 56, t - 1, 4, 1, 6, True); fin(c, 56, b + 1, 4, 1, 6, False)
def AH_2(c):    # P-500 Bazalt / SS-N-12 Sandbox (chin intake)
    t, b = 9, 16
    c.p(1, 12, 'W'); c.line(2, 11, 4, t, 'W'); c.line(2, 13, 5, b - 1, 'W')
    c.hl(5, 49, t, 'W'); c.hl(6, 49, b, 'W')
    c.rect(5, b + 1, 17, b + 4, 'B'); c.vl(7, b + 2, b + 3, 'B')                             # chin intake
    c.vl(18, t, b, 'B')
    fin(c, 33, t - 1, 4, 2, 10, True); fin(c, 33, b + 1, 3, 2, 10, False)
    fin(c, 48, t - 1, 5, 1, 7, True); fin(c, 48, b + 1, 4, 1, 7, False)
    c.hl(50, 57, t + 1, 'Y'); c.hl(50, 57, b - 1, 'Y'); c.vl(57, t + 1, b - 1, 'Y')
def AH_3(c):    # P-700 Granit / SS-N-19 Shipwreck (annular intake, booster ring)
    t, b = 8, 16
    c.hl(1, 4, 12, 'Y'); c.vl(4, 11, 13, 'Y')
    c.vl(5, t, b, 'B'); c.vl(6, t, b, 'B')
    c.hl(7, 44, t, 'W'); c.hl(7, 44, b, 'W'); c.vl(20, t, b, 'B')
    fin(c, 33, t - 1, 3, 1, 8, True); fin(c, 33, b + 1, 3, 1, 8, False)
    fin(c, 44, t - 1, 4, 1, 6, True); fin(c, 44, b + 1, 4, 1, 6, False)
    c.rect(46, t - 1, 57, b + 1, 'Y'); c.vl(49, t - 1, b + 1, 'Y'); c.vl(54, t - 1, b + 1, 'Y')   # booster ring
def AH_4(c):    # P-270 Moskit / SS-N-22 Sunburn (ramjet pods)
    t, b = 10, 15
    c.p(1, 12, 'Y'); c.line(2, 11, 4, t, 'W'); c.line(2, 13, 5, b - 1, 'W'); c.p(5, b, 'W')
    c.hl(5, 52, t, 'W'); c.hl(6, 52, b, 'W'); c.vl(53, t + 1, b - 1, 'Y')
    fin(c, 16, t - 1, 3, 1, 6, True); fin(c, 16, b + 1, 3, 1, 6, False)        # fore wings
    c.rect(24, t - 4, 44, t - 1, 'B'); c.vl(24, t - 4, t - 1, 'B'); c.vl(26, t - 3, t - 2, 'B')   # ramjet pods
    c.rect(24, b + 1, 44, b + 4, 'B'); c.vl(26, b + 2, b + 3, 'B')
    fin(c, 52, t - 1, 4, 1, 6, True); fin(c, 52, b + 1, 4, 1, 6, False)

# ---- radar ---------------------------------------------------------------
# reflectors/arrays blue, masts/pedestals/directors green, feeds yellow, radomes red
def ellipse(c, cx, cy, rx, ry, col, part=None):
    """1-px midpoint ellipse outline (integer radii); part='top'/'bottom' draws one half"""
    pts = set()
    x, y = 0, ry
    rx2, ry2 = rx * rx, ry * ry
    d1 = ry2 - rx2 * ry + rx2 / 4
    dx, dy = 2 * ry2 * x, 2 * rx2 * y
    while dx < dy:
        pts.add((x, y)); x += 1; dx += 2 * ry2
        if d1 < 0: d1 += dx + ry2
        else: y -= 1; dy -= 2 * rx2; d1 += dx - dy + ry2
    d2 = ry2 * (x + 0.5) ** 2 + rx2 * (y - 1) ** 2 - rx2 * ry2
    while y >= 0:
        pts.add((x, y)); y -= 1; dy -= 2 * rx2
        if d2 > 0: d2 += rx2 - dy
        else: x += 1; dx += 2 * ry2; d2 += dx - dy + rx2
    for x, y in pts:
        for sx in (1, -1):
            for sy in (1, -1):
                if part == 'top' and sy > 0 and y: continue
                if part == 'bottom' and sy < 0 and y: continue
                c.p(cx + sx * x, cy + sy * y, col)

def pedestal(c, cx, y0, y1=25, w=4):          # trainable mount on a base plate
    c.vl(cx - 1, y0, y1 - 2, 'G'); c.vl(cx + 1, y0, y1 - 2, 'G')
    c.line(cx - 1, y1 - 1, cx - w, y1, 'G'); c.line(cx + 1, y1 - 1, cx + w, y1, 'G')
    c.hl(cx - w - 2, cx + w + 2, y1, 'G')

def grid(c, x0, y0, x1, y1, step, col='B', dots=False):
    for x in range(x0 + step, x1, step):
        if dots:
            for y in range(y0 + step, y1, step): c.p(x, y, col)
        else: c.vl(x, y0 + 1, y1 - 1, col)
    if not dots:
        for y in range(y0 + step, y1, step): c.hl(x0 + 1, x1 - 1, y, col)

def dish(c, cx, cy, r, spokes=True):            # front-on parabolic dish + feed
    ellipse(c, cx, cy, r, r, 'B')
    if spokes:
        c.line(cx - r + 2, cy - r + 2, cx - 1, cy - 1, 'B'); c.line(cx + r - 2, cy - r + 2, cx + 1, cy - 1, 'B')
        c.line(cx - r + 2, cy + r - 2, cx - 1, cy + 1, 'B'); c.line(cx + r - 2, cy + r - 2, cx + 1, cy + 1, 'B')
    c.p(cx, cy, 'Y'); c.p(cx - 1, cy, 'Y'); c.p(cx + 1, cy, 'Y'); c.p(cx, cy - 1, 'Y'); c.p(cx, cy + 1, 'Y')

def director(c, x0, x1, y0, y1):                # gun director house with rangefinder ears
    c.hl(x0 + 2, x1 - 2, y0, 'G'); c.line(x0 + 2, y0, x0, y0 + 2, 'G'); c.line(x1 - 2, y0, x1, y0 + 2, 'G')
    c.vl(x0, y0 + 2, y1, 'G'); c.vl(x1, y0 + 2, y1, 'G'); c.hl(x0, x1, y1, 'G')
    c.rect(x0 + 3, y0 + 3, x0 + 6, y0 + 5, 'G')                          # sight port

# air search ("AW") ------------------------------------------------------
def AW_ww(c):   # SK "bedspring"
    c.rect(17, 2, 43, 18, 'B'); grid(c, 17, 2, 43, 18, 4)
    c.hl(22, 38, 0, 'Y'); c.vl(22, 0, 1, 'Y'); c.vl(30, 0, 1, 'Y'); c.vl(38, 0, 1, 'Y')     # IFF rods
    pedestal(c, 30, 19)
def AW_0(c):    # AN/SPS-6 orange peel
    ellipse(c, 30, 9, 22, 8, 'B')
    for x in (16, 23, 30, 37, 44): c.vl(x, 2, 16, 'B')
    c.hl(10, 50, 9, 'B')
    c.rect(28, 7, 32, 11, 'Y')
    pedestal(c, 30, 18)
def AW_1(c):    # AN/SPS-43 long bedspring
    c.rect(2, 4, 57, 15, 'B')
    for x in range(5, 57, 3): c.vl(x, 5, 14, 'B')
    c.hl(3, 56, 9, 'B')
    for x in range(4, 56, 8): c.line(x, 3, x + 4, 0, 'G'); c.line(x + 4, 0, x + 8, 3, 'G')   # truss
    c.hl(2, 57, 3, 'G')
    pedestal(c, 30, 16)
def AW_2(c):    # AN/SPS-49 mesh dish, offset feed below
    ellipse(c, 30, 8, 18, 8, 'B'); grid(c, 12, 0, 48, 16, 4, dots=True)
    c.line(30, 17, 30, 21, 'G'); c.rect(28, 17, 32, 19, 'Y')            # feed horn on boom
    c.line(22, 15, 28, 18, 'B'); c.line(38, 15, 32, 18, 'B')
    pedestal(c, 30, 20)
def AW_3(c):    # AN/SPY-1 octagonal fixed array on deckhouse
    pts = [(24, 1), (36, 1), (41, 6), (41, 17), (36, 22), (24, 22), (19, 17), (19, 6)]
    for i in range(8): c.line(*pts[i], *pts[(i + 1) % 8], 'B')
    grid(c, 19, 1, 41, 22, 3, dots=True)
    c.line(9, 25, 14, 5, 'G'); c.hl(14, 18, 5, 'G'); c.line(51, 25, 46, 5, 'G'); c.hl(42, 46, 5, 'G')   # deckhouse
    c.hl(5, 55, 25, 'G')
def AW_4(c):    # SAMPSON spherical radome
    ellipse(c, 30, 10, 10, 10, 'R')
    c.rect(26, 3, 28, 17, 'B'); c.rect(32, 3, 34, 17, 'B')            # back-to-back faces
    pedestal(c, 30, 21)

# fire control ("FC") -----------------------------------------------------
def FC_0(c):    # Mk 37 director with Mk 12 / Mk 22
    c.rect(18, 1, 34, 9, 'B'); grid(c, 18, 1, 34, 9, 4)                  # Mk 12 array
    ellipse(c, 40, 5, 3, 5, 'B'); c.p(40, 5, 'Y')                          # Mk 22 orange peel
    c.vl(26, 10, 12, 'G')
    director(c, 14, 46, 13, 23)
    c.hl(4, 13, 17, 'G'); c.hl(47, 56, 17, 'G'); c.rect(2, 15, 4, 19, 'G'); c.rect(56, 15, 58, 19, 'G')   # rangefinder
    c.hl(10, 50, 25, 'G')
def FC_1(c):    # Mk 25 dish on Mk 56 director
    dish(c, 30, 8, 8)
    c.vl(29, 17, 18, 'G'); c.vl(31, 17, 18, 'G')
    director(c, 20, 40, 19, 25)
def FC_2(c):    # AN/SPG-51 tracker + illuminator
    dish(c, 23, 10, 9); dish(c, 44, 12, 6)
    c.hl(23, 44, 20, 'G'); c.vl(23, 19, 20, 'G'); c.vl(44, 18, 20, 'G')
    pedestal(c, 33, 21)
def FC_3(c):    # AN/SPG-60 STIR, Cassegrain
    ellipse(c, 30, 10, 10, 10, 'B')
    c.line(22, 4, 28, 9, 'B'); c.line(38, 4, 32, 9, 'B'); c.line(30, 20, 30, 12, 'B')    # struts
    c.rect(28, 8, 32, 12, 'Y')                                              # subreflector
    ellipse(c, 30, 10, 6, 6, 'B')
    pedestal(c, 30, 21)
def FC_4(c):    # Mk 92 CAS "egg"
    ellipse(c, 30, 12, 8, 11, 'R', 'top'); ellipse(c, 30, 12, 8, 6, 'R', 'bottom')   # egg radome
    c.hl(25, 35, 19, 'R')                                                  # base ring
    pedestal(c, 30, 21)
def FC_5(c):    # AN/SPQ-9B slab radome
    c.hl(10, 50, 6, 'R'); c.hl(10, 50, 15, 'R'); c.vl(8, 8, 13, 'R'); c.vl(52, 8, 13, 'R')
    c.p(9, 7, 'R'); c.p(9, 14, 'R'); c.p(51, 7, 'R'); c.p(51, 14, 'R')
    for x in range(14, 48, 3): c.vl(x, 8, 13, 'B')                         # slotted array
    pedestal(c, 30, 16)
def FC_6(c):    # APAR four-face array tower
    c.rect(16, 2, 34, 20, 'B'); grid(c, 16, 2, 34, 20, 3, dots=True)        # front face
    c.line(34, 2, 46, 8, 'B'); c.line(34, 20, 46, 14, 'B'); c.vl(46, 8, 14, 'B')   # side face (1:2)
    for x, y0, y1 in ((38, 6, 16), (42, 8, 14)):
        for y in range(y0, y1 + 1, 3): c.p(x, y, 'B')
    c.vl(18, 21, 25, 'G'); c.vl(44, 16, 25, 'G'); c.hl(10, 50, 25, 'G')       # mast block

# ---- air defence ----------------------------------------------------------
def flash_hider(c, x, cy, h):                   # conical Bofors flash hider, muzzle left
    c.vl(x, cy - h - 2, cy + h + 2, 'Y'); c.line(x + 1, cy - h - 2, x + 3, cy - h, 'Y'); c.line(x + 1, cy + h + 2, x + 3, cy + h, 'Y')

def bofors(c, cy, bx0, bx1, hx1, hh, coil=(20, 28)):
    flash_hider(c, bx0 - 4, cy, 1)
    barrel(c, bx0, bx1, cy, 1)
    for x in range(coil[0], coil[1] + 1, 2): c.vl(x, cy - 2, cy + 2, 'B')   # recoil spring
    house(c, bx1 + 1, hx1, cy, hh)

def AG_0(c):    # 40 mm Bofors quad Mk 2 (two pairs shown)
    def one(c):
        bofors(c, 5, 6, 32, 50, 3)
        c.rect(36, 0, 42, 1, 'R')                                           # clip guide
    one(c); shifted(c, 6, 12, one)
def AG_1(c):    # 40 mm Bofors L/70
    cy = 13
    bofors(c, cy, 6, 34, 56, 5, coil=(22, 32))
    c.rect(38, cy - 11, 50, cy - 6, 'R'); c.vl(44, cy - 10, cy - 7, 'R')    # top-feed magazine

def gatling(c, x0, x1, cy, clamps):
    for y in (cy - 2, cy, cy + 2): c.hl(x0, x1, y, 'G'); c.p(x0 - 2, y, 'Y'); c.p(x0 - 1, y, 'Y')
    for x in clamps: c.rect(x, cy - 4, x + 2, cy + 4, 'B')

def phalanx_dome(c, L, R):
    c.vl(L, 8, 15, 'R'); c.vl(R, 8, 15, 'R')
    c.p(L + 1, 7, 'R'); c.p(L + 1, 6, 'R'); c.p(L + 2, 5, 'R'); c.p(L + 3, 4, 'R'); c.hl(L + 4, L + 5, 3, 'R'); c.hl(L + 6, L + 8, 2, 'R')
    c.p(R - 1, 7, 'R'); c.p(R - 1, 6, 'R'); c.p(R - 2, 5, 'R'); c.p(R - 3, 4, 'R'); c.hl(R - 5, R - 4, 3, 'R'); c.hl(R - 8, R - 6, 2, 'R')
    c.hl(L + 9, R - 9, 1, 'R')
    c.hl(L + 3, R - 3, 6, 'R')                                              # search antenna band
    c.rect(L - 3, 9, L, 13, 'R')                                            # track antenna

def CW_0(c):    # AK-630 (gatling in compact turret)
    cy = 12
    gatling(c, 4, 30, cy, (6, 18))
    c.hl(33, 50, 4, 'B'); c.line(31, 6, 33, 4, 'B'); c.line(51, 5, 54, 8, 'B'); c.vl(55, 9, 18, 'B')   # rounded turret
    c.vl(31, 7, 20, 'B'); c.hl(31, 55, 20, 'B'); c.vl(33, 8, 18, 'B')
    c.p(40, cy - 1, 'B'); c.p(39, cy, 'B'); c.p(41, cy, 'B'); c.p(40, cy + 1, 'B')
    c.rect(42, 21, 50, 25, 'R'); c.vl(46, 22, 24, 'R')                       # ammunition feed
def CW_1(c):    # Mk 15 Phalanx
    phalanx_dome(c, 29, 53)
    gatling(c, 3, 28, 19, (5, 17))
    c.rect(29, 16, 39, 22, 'B'); c.p(34, 18, 'B'); c.p(33, 19, 'B'); c.p(35, 19, 'B'); c.p(34, 20, 'B')
    c.rect(40, 16, 55, 22, 'W')
    for x in range(43, 55, 3): c.vl(x, 17, 21, 'W')
    c.vl(56, 17, 21, 'W')
    c.hl(31, 55, 23, 'G'); c.line(31, 23, 28, 25, 'G'); c.line(55, 23, 58, 25, 'G'); c.hl(28, 58, 25, 'G')
def CW_2(c):    # Thales RapidFire (40 mm CTA cannon, faceted turret, roof optronic director)
    cy = 15
    muzzle_brake(c, 3, cy, 1)
    barrel(c, 8, 33, cy, 1); ring(c, 24, 28, cy, 2)                         # 40 CTA barrel + sleeve
    # faceted turret - only 1:2 and 45-degree edges so the outline never breaks
    c.line(30, 21, 36, 9, 'B'); c.line(36, 9, 39, 6, 'B'); c.hl(39, 54, 6, 'B')
    c.line(54, 6, 57, 9, 'B'); c.vl(57, 9, 21, 'B'); c.hl(30, 57, 21, 'B')
    c.hl(33, 57, 18, 'B')                                                   # belt line
    c.p(46, 12, 'B'); c.p(45, 13, 'B'); c.p(47, 13, 'B'); c.p(46, 14, 'B')
    c.rect(44, 1, 52, 4, 'R'); c.vl(43, 2, 3, 'Y'); c.vl(48, 5, 5, 'R')     # optronic director on a stem
    c.hl(33, 55, 23, 'G'); c.line(33, 23, 30, 25, 'G'); c.line(55, 23, 58, 25, 'G'); c.hl(30, 58, 25, 'G')

# SAM rounds: white airframe, blue fins, yellow seeker/motor/booster; launcher red
def SR_0(c):    # Sea Cat GWS-22 on 4-rail launcher
    cy = 5
    c.vl(8, cy - 1, cy + 1, 'Y'); c.hl(9, 36, cy - 1, 'W'); c.hl(9, 36, cy + 1, 'W'); c.vl(37, cy - 1, cy + 1, 'Y')
    fin(c, 15, cy - 2, 2, 1, 3, True); fin(c, 15, cy + 2, 2, 1, 3, False)  # canards
    fin(c, 34, cy - 2, 4, 1, 10, True); fin(c, 34, cy + 2, 4, 1, 10, False) # big cruciform wings
    c.rect(6, 12, 46, 15, 'R'); c.vl(10, 13, 14, 'R'); c.vl(42, 13, 14, 'R') # quad-rail beam
    c.vl(24, 16, 17, 'R'); c.vl(36, 16, 17, 'R'); c.rect(22, 18, 38, 20, 'R') # cradle
    pedestal(c, 30, 21)
def SR_1(c):    # RIM-7M Sea Sparrow on Mk 29 8-cell launcher
    by = 4; nx = 6; tail = 54
    c.p(nx, by + 1, 'W'); c.p(nx + 1, by + 1, 'W')
    c.hl(nx + 2, tail - 12, by, 'W'); c.hl(nx + 1, tail - 12, by + 2, 'W')
    c.rect(tail - 11, by, tail, by + 2, 'Y'); c.vl(tail - 9, by, by + 2, 'Y')
    for i in range(3):
        c.hl(26 - i, 28, by - 1 - i, 'B'); c.hl(26 - i, 28, by + 3 + i, 'B')
        c.hl(tail - 3 - i, tail - 1, by - 1 - i, 'B'); c.hl(tail - 3 - i, tail - 1, by + 3 + i, 'B')
    lx0, lx1, ly0, ly1 = 6, 54, 12, 19; mid = (ly0 + ly1) // 2
    c.rect(lx0, ly0, lx1, ly1, 'R'); c.hl(lx0, lx1, mid, 'R')
    for rx in (lx0 + 4, lx0 + 6, 29, 31, lx1 - 4): c.vl(rx, ly0, ly1, 'R')
    c.vl(lx0 - 2, ly0 + 1, mid - 1, 'B'); c.vl(lx0 - 2, mid + 1, ly1 - 1, 'B')
    pedestal(c, 30, 20)
def SR_2(c):    # RIM-116 RAM on Mk 49 21-cell launcher
    cy = 4
    c.vl(6, cy - 1, cy + 1, 'Y'); c.hl(7, 48, cy - 1, 'W'); c.hl(7, 48, cy + 1, 'W'); c.vl(49, cy - 1, cy + 1, 'Y')
    fin(c, 13, cy - 2, 2, 0, 3, True); fin(c, 13, cy + 2, 2, 0, 3, False)  # canards
    fin(c, 48, cy - 2, 3, 1, 5, True); fin(c, 48, cy + 2, 3, 1, 5, False)  # tail fins
    c.rect(10, 11, 50, 21, 'R'); c.vl(8, 12, 20, 'R')                      # launcher, cells end-on
    for y in (13, 16, 19):
        for x in range(13, 49, 5): c.rect(x, y - 1, x + 2, y + 1, 'R')
    pedestal(c, 30, 22)
def LR_0(c):    # RIM-2 Terrier (+ booster) on Mk 10 rail
    cy = 5
    c.p(1, cy, 'W'); c.line(2, cy - 1, 4, cy - 2, 'W'); c.line(2, cy + 1, 4, cy + 2, 'W')
    c.hl(5, 32, cy - 2, 'W'); c.hl(5, 32, cy + 2, 'W'); c.vl(33, cy - 2, cy + 2, 'W')
    fin(c, 22, cy - 3, 3, 2, 7, True); fin(c, 22, cy + 3, 3, 2, 7, False)
    fin(c, 33, cy - 3, 2, 1, 4, True); fin(c, 33, cy + 3, 2, 1, 4, False)
    c.rect(35, cy - 3, 54, cy + 3, 'Y'); c.vl(37, cy - 3, cy + 3, 'Y')      # booster
    fin(c, 54, cy - 4, 4, 1, 7, True); fin(c, 54, cy + 4, 4, 1, 7, False)
    c.hl(4, 56, 14, 'R'); c.hl(4, 56, 16, 'R'); c.vl(4, 14, 16, 'R'); c.vl(56, 14, 16, 'R')   # launcher arm
    for x in (10, 30, 50): c.vl(x, 12, 13, 'R')
    c.rect(40, 17, 50, 20, 'R'); pedestal(c, 45, 21)
def LR_1(c):    # RIM-8 Talos ramjet (+ booster)
    cy = 5
    c.hl(1, 4, cy, 'Y'); c.vl(4, cy - 1, cy + 1, 'Y'); c.vl(5, cy - 3, cy + 3, 'B'); c.vl(6, cy - 3, cy + 3, 'B')
    c.hl(7, 34, cy - 3, 'W'); c.hl(7, 34, cy + 3, 'W'); c.vl(35, cy - 2, cy + 2, 'W')
    fin(c, 24, cy - 4, 2, 1, 8, True); fin(c, 24, cy + 4, 2, 1, 8, False)
    fin(c, 34, cy - 4, 2, 1, 5, True); fin(c, 34, cy + 4, 2, 1, 5, False)
    c.rect(37, cy - 3, 54, cy + 3, 'Y'); c.vl(39, cy - 3, cy + 3, 'Y')
    fin(c, 54, cy - 4, 4, 1, 7, True); fin(c, 54, cy + 4, 4, 1, 7, False)
    c.hl(4, 56, 14, 'R'); c.hl(4, 56, 16, 'R'); c.vl(4, 14, 16, 'R'); c.vl(56, 14, 16, 'R')
    for x in (10, 30, 50): c.vl(x, 12, 13, 'R')
    c.rect(40, 17, 50, 20, 'R'); pedestal(c, 45, 21)
def LR_2(c):    # RIM-66 SM-1MR on Mk 13 single-arm launcher
    cy = 5
    c.vl(3, cy - 1, cy + 1, 'Y'); c.p(4, cy - 2, 'Y'); c.p(4, cy + 2, 'Y')
    c.hl(5, 52, cy - 2, 'W'); c.hl(5, 52, cy + 2, 'W'); c.vl(52, cy - 2, cy + 2, 'Y')
    c.hl(18, 44, cy - 3, 'B'); c.hl(18, 44, cy + 3, 'B'); c.p(17, cy - 3, 'B'); c.p(17, cy + 3, 'B')   # long strakes
    fin(c, 52, cy - 3, 3, 1, 6, True); fin(c, 52, cy + 3, 3, 1, 6, False)
    c.hl(8, 54, 12, 'R'); c.hl(8, 54, 14, 'R'); c.vl(8, 12, 14, 'R'); c.vl(54, 12, 14, 'R')   # single arm
    c.vl(26, 10, 11, 'R'); c.vl(46, 10, 11, 'R')
    c.rect(36, 15, 52, 21, 'R'); c.vl(44, 16, 20, 'R')                        # launcher drum housing
    pedestal(c, 44, 22, w=6)
def vls(c, x0, x1, y0, y1, cells):              # side view of a VLS module, hatches on top
    c.rect(x0, y0, x1, y1, 'R')
    w = (x1 - x0) // cells
    for i in range(1, cells): c.vl(x0 + i * w, y0, y1, 'R')
    for i in range(cells): c.hl(x0 + i * w + 1, x0 + i * w + w - 2, y0 - 2, 'R'); c.p(x0 + i * w + 1, y0 - 1, 'R')
def LR_3(c):    # RIM-66 SM-2MR over Mk 41 VLS
    cy = 4
    c.vl(3, cy - 1, cy + 1, 'Y'); c.p(4, cy - 2, 'Y'); c.p(4, cy + 2, 'Y')
    c.hl(5, 52, cy - 2, 'W'); c.hl(5, 52, cy + 2, 'W'); c.vl(52, cy - 2, cy + 2, 'Y')
    c.hl(18, 44, cy - 3, 'B'); c.hl(18, 44, cy + 3, 'B'); c.p(17, cy - 3, 'B'); c.p(17, cy + 3, 'B')
    fin(c, 52, cy - 3, 3, 1, 6, True); fin(c, 52, cy + 3, 3, 1, 6, False)
    vls(c, 6, 54, 14, 25, 8)
def LR_4(c):    # Aster 30 (dart + booster) over Sylver VLS
    cy = 5
    c.p(1, cy, 'Y'); c.line(2, cy - 1, 3, cy - 1, 'W'); c.line(2, cy + 1, 3, cy + 1, 'W')
    c.hl(4, 30, cy - 1, 'W'); c.hl(4, 30, cy + 1, 'W')
    c.hl(12, 26, cy - 2, 'B'); c.hl(12, 26, cy + 2, 'B')                      # long wings
    fin(c, 30, cy - 2, 2, 1, 4, True); fin(c, 30, cy + 2, 2, 1, 4, False)
    c.rect(32, cy - 3, 54, cy + 3, 'Y'); c.vl(34, cy - 3, cy + 3, 'Y')      # booster
    fin(c, 54, cy - 4, 4, 1, 6, True); fin(c, 54, cy + 4, 4, 1, 6, False)
    vls(c, 10, 50, 15, 25, 5)

# ======================================================================
# registry:  key, folder, file name, label, year, art, module sprites, techs
# ======================================================================
TORP = [
 ('T_ww', 'Torpedoes', 'Torpedo 1935 (Mk 15)',          'TORP',   "'35", T_ww, ['torpedo_ww', 'sub_torpedo_ww'], ['torpedo_ww']),
 ('T_0',  'Torpedoes', 'Torpedo 1945 (Mk 24 Fido)',     'TORP',   "'45", T_0,  ['torpedo_small_0', 'sub_torpedo_small_0'], ['torpedo_small_0']),
 ('T_1',  'Torpedoes', 'Torpedo 1960 (Mk 44)',          'TORP',   "'60", T_1,  ['torpedo_small_1', 'sub_torpedo_small_1'], ['torpedo_small_1']),
 ('T_2',  'Torpedoes', 'Torpedo 1975 (Mk 46)',          'TORP',   "'75", T_2,  ['torpedo_small_2', 'sub_torpedo_small_2'], ['torpedo_small_2']),
 ('T_3',  'Torpedoes', 'Torpedo 1990 (Sting Ray)',      'TORP',   "'90", T_3,  ['torpedo_small_3', 'sub_torpedo_small_3'], ['torpedo_small_3']),
 ('T_4',  'Torpedoes', 'Torpedo 2005 (MU90)',           'TORP',   "'05", T_4,  ['torpedo_small_4', 'sub_torpedo_small_4'], ['torpedo_small_4']),
 ('TL_0', 'Torpedoes', 'Heavy torpedo 1960 (Mk 37)',    'TORP-H', "'60", TL_0, ['torpedo_large_0', 'sub_torpedo_large_0'], ['torpedo_large_0']),
 ('TL_1', 'Torpedoes', 'Heavy torpedo 1975 (Mk 48)',    'TORP-H', "'75", TL_1, ['torpedo_large_1', 'sub_torpedo_large_1'], ['torpedo_large_1']),
 ('TL_2', 'Torpedoes', 'Heavy torpedo 1990 (Spearfish)','TORP-H', "'90", TL_2, ['torpedo_large_2', 'sub_torpedo_large_2'], ['torpedo_large_2']),
]
GUNS = [
 ('L_ww', 'Naval Guns', 'Light gun 1935 (4in QF Mk XVI twin)', '2x 102MM', "'35", L_ww, ['ship_armament_light_ww'], []),
 ('L_0',  'Naval Guns', 'Light gun 1940 (3in-50 Mk 22)',       '1x 76MM',  "'40", L_0,  ['ship_armament_light_0'], ['ship_armament_light_0']),
 ('L_1',  'Naval Guns', 'Light gun 1960 (AK-726 twin)',        '2x 76MM',  "'60", L_1,  ['ship_armament_light_1'], ['ship_armament_light_1']),
 ('L_2',  'Naval Guns', 'Light gun 1975 (OTO 76-62 Compact)',  '1x 76MM',  "'75", L_2,  ['ship_armament_light_2'], ['ship_armament_light_2']),
 ('L_3',  'Naval Guns', 'Light gun 1990 (OTO 76-62 SR)',       '1x 76MM',  "'90", L_3,  ['ship_armament_light_3'], ['ship_armament_light_3']),
 ('L_4',  'Naval Guns', 'Light gun 2005 (Bofors 57 Mk3)',      '1x 57MM',  "'05", L_4,  ['ship_armament_light_4'], ['ship_armament_light_4']),
 ('M_ww', 'Naval Guns', 'Medium gun 1935 (5in-38 Mk 12)',      '1x 127MM', "'35", M_ww, ['ship_armament_medium_ww'], ['ww_armaments']),
 ('M_0',  'Naval Guns', 'Medium gun 1940 (5.25in QF twin)',    '2x 133MM', "'40", M_0,  ['ship_armament_medium_0'], ['ship_armament_medium_0']),
 ('M_1',  'Naval Guns', 'Medium gun 1955 (5in-54 Mk 42)',      '1x 127MM', "'55", M_1,  ['ship_armament_medium_1'], ['ship_armament_medium_1']),
 ('M_2',  'Naval Guns', 'Medium gun 1970 (5in-54 Mk 45)',      '1x 127MM', "'70", M_2,  ['ship_armament_medium_2'], ['ship_armament_medium_2']),
 ('M_3',  'Naval Guns', 'Medium gun 1990 (AK-130 twin)',       '2x 130MM', "'90", M_3,  ['ship_armament_medium_3'], ['ship_armament_medium_3']),
 ('M_4',  'Naval Guns', 'Medium gun 2005 (OTO 127-64 LW)',     '1x 127MM', "'05", M_4,  ['ship_armament_medium_4'], ['ship_armament_medium_4']),
 ('H_ww', 'Naval Guns', 'Heavy gun 1935 (6in-47 Mk 16)',       '1x 152MM', "'35", H_ww, ['ship_armament_heavy_ww'], []),
 ('H_0',  'Naval Guns', 'Heavy gun 1950 (6in-47 DP Mk 16)',    '1x 152MM', "'50", H_0,  ['ship_armament_heavy_0'], ['ship_armament_heavy_0']),
 ('H_1',  'Naval Guns', 'Heavy gun 1965 (8in-55 Mk 16 auto)',  '1x 203MM', "'65", H_1,  ['ship_armament_heavy_1'], ['ship_armament_heavy_1']),
 ('H_2',  'Naval Guns', 'Heavy gun 1980 (8in-55 Mk 71)',       '1x 203MM', "'80", H_2,  ['ship_armament_heavy_2'], ['ship_armament_heavy_2']),
 ('H_3',  'Naval Guns', 'Heavy gun 1995 (155mm AGS)',          '1x 155MM', "'95", H_3,  ['ship_armament_heavy_3'], ['ship_armament_heavy_3']),
 ('S_0',  'Naval Guns', 'Super-heavy gun 1965 (16in-50 Mk 7)', '1x 406MM', "'65", S_0,  ['ship_armament_super_heavy_0'], ['ship_armament_super_heavy_0']),
 ('S_1',  'Naval Guns', 'Super-heavy gun 1980 (16in-50 Mk 7 refit)', '1x 406MM', "'80", S_1, ['ship_armament_super_heavy_1'], ['ship_armament_super_heavy_1']),
]
ASHM = [
 ('A_0',  'Anti-Ship Missiles', 'AShM 1955 (SS-N-1)',          'ASHM',   "'55", A_0,  ['ship_armament_asm_0'], ['ashm_0']),
 ('A_1',  'Anti-Ship Missiles', 'AShM 1965 (P-15 Termit)',     'ASHM',   "'65", A_1,  ['ship_armament_asm_1'], ['ashm_1']),
 ('A_2',  'Anti-Ship Missiles', 'AShM 1975 (MM38 Exocet)',     'ASHM',   "'75", A_2,  ['ship_armament_asm_2'], ['ashm_2']),
 ('A_3',  'Anti-Ship Missiles', 'AShM 1985 (Harpoon)',         'ASHM',   "'85", A_3,  ['ship_armament_asm_3'], ['ashm_3']),
 ('A_4',  'Anti-Ship Missiles', 'AShM 1995 (P-800 Oniks)',     'ASHM',   "'95", A_4,  ['ship_armament_asm_4'], ['ashm_4']),
 ('AH_0', 'Anti-Ship Missiles', 'Heavy AShM 1955 (P-35 Shaddock)', 'ASHM-H', "'55", AH_0, ['ship_armament_heavyasm_0'], []),
 ('AH_1', 'Anti-Ship Missiles', 'Heavy AShM 1965 (P-120 Malakhit)','ASHM-H', "'65", AH_1, ['ship_armament_heavyasm_1'], []),
 ('AH_2', 'Anti-Ship Missiles', 'Heavy AShM 1975 (P-500 Bazalt)',  'ASHM-H', "'75", AH_2, ['ship_armament_heavyasm_2'], []),
 ('AH_3', 'Anti-Ship Missiles', 'Heavy AShM 1985 (P-700 Granit)',  'ASHM-H', "'85", AH_3, ['ship_armament_heavyasm_3'], []),
 ('AH_4', 'Anti-Ship Missiles', 'Heavy AShM 1995 (P-270 Moskit)',  'ASHM-H', "'95", AH_4, ['ship_armament_heavyasm_4'], []),
]
RADAR = [
 ('AW_ww', 'Radar', 'Air search radar 1935 (SK)',           'AW RADAR', "'35", AW_ww, ['A2A_navalradar'],   ['detection_ww']),
 ('AW_0',  'Radar', 'Air search radar 1945 (SPS-6)',        'AW RADAR', "'45", AW_0,  ['A2A_navalradar_0'], ['radar_aa_0']),
 ('AW_1',  'Radar', 'Air search radar 1955 (SPS-43)',       'AW RADAR', "'55", AW_1,  ['A2A_navalradar_1'], ['radar_aa_1']),
 ('AW_2',  'Radar', 'Air search radar 1970 (SPS-49)',       'AW RADAR', "'70", AW_2,  ['A2A_navalradar_2'], ['radar_aa_2']),
 ('AW_3',  'Radar', 'Air search radar 1985 (SPY-1)',        'AW RADAR', "'85", AW_3,  ['A2A_navalradar_3'], ['radar_aa_3']),
 ('AW_4',  'Radar', 'Air search radar 2000 (SAMPSON)',      'AW RADAR', "'00", AW_4,  ['A2A_navalradar_4'], ['radar_aa_4']),
 ('FC_0',  'Radar', 'Fire control radar 1935 (Mk 37 + Mk 12)', 'FC RADAR', "'35", FC_0, ['maritime_ta_fcs_0'], []),
 ('FC_1',  'Radar', 'Fire control radar 1950 (Mk 25)',      'FC RADAR', "'50", FC_1,  ['maritime_ta_fcs_1'], ['radar_naval_0']),
 ('FC_2',  'Radar', 'Fire control radar 1960 (SPG-51)',     'FC RADAR', "'60", FC_2,  ['maritime_ta_fcs_2'], ['radar_naval_1']),
 ('FC_3',  'Radar', 'Fire control radar 1970 (SPG-60)',     'FC RADAR', "'70", FC_3,  ['maritime_ta_fcs_3'], ['radar_naval_2']),
 ('FC_4',  'Radar', 'Fire control radar 1980 (Mk 92 CAS)',  'FC RADAR', "'80", FC_4,  ['maritime_ta_fcs_4'], ['radar_naval_3']),
 ('FC_5',  'Radar', 'Fire control radar 1990 (SPQ-9B)',     'FC RADAR', "'90", FC_5,  ['maritime_ta_fcs_5'], ['radar_naval_4']),
 ('FC_6',  'Radar', 'Fire control radar 2000 (APAR)',       'FC RADAR', "'00", FC_6,  ['maritime_ta_fcs_6'], ['radar_naval_5']),
]
AIRDEF = [
 ('AG_0', 'Air Defence', 'AA gun 1935 (40mm Bofors quad)',  '4x 40MM',  "'35", AG_0, ['ship_AA_gun_1'], []),
 ('AG_1', 'Air Defence', 'AA gun 1950 (40mm Bofors L70)',   '1x 40MM',  "'50", AG_1, ['ship_AA_gun_2'], []),
 ('CW_0', 'Air Defence', 'CIWS 1970 (AK-630)',              '1x CIWS',  "'70", CW_0, ['ciws_0'], ['ship_armament_aa_2']),
 ('CW_1', 'Air Defence', 'CIWS 1985 (Phalanx)',             '1x CIWS',  "'85", CW_1, ['ciws_1'], ['ship_armament_aa_3']),
 ('CW_2', 'Air Defence', 'CIWS 2000 (Thales RapidFire)',              '1x CIWS',  "'00", CW_2, ['ciws_2'], ['ship_armament_aa_4']),
 ('SR_0', 'Air Defence', 'SR-SAM 1970 (Sea Cat)',           'SR-SAM',   "'70", SR_0, ['ship_SAM_mid_range_0'], ['light_sam_0']),
 ('SR_1', 'Air Defence', 'SR-SAM 1985 (Sea Sparrow Mk 29)', 'SR-SAM',   "'85", SR_1, ['ship_SAM_mid_range_1'], ['light_sam_1']),
 ('SR_2', 'Air Defence', 'SR-SAM 2000 (RAM Mk 49)',         'SR-SAM',   "'00", SR_2, ['ship_SAM_mid_range_2'], ['light_sam_2']),
 ('LR_0', 'Air Defence', 'LR-SAM 1955 (Terrier)',           'LR-SAM',   "'55", LR_0, ['ship_SAM_long_range_0'], ['heavy_sam_0']),
 ('LR_1', 'Air Defence', 'LR-SAM 1965 (Talos)',             'LR-SAM',   "'65", LR_1, ['ship_SAM_long_range_1'], ['heavy_sam_1']),
 ('LR_2', 'Air Defence', 'LR-SAM 1975 (SM-1MR Mk 13)',      'LR-SAM',   "'75", LR_2, ['ship_SAM_long_range_2'], ['heavy_sam_2']),
 ('LR_3', 'Air Defence', 'LR-SAM 1985 (SM-2MR Mk 41)',      'LR-SAM',   "'85", LR_3, ['ship_SAM_long_range_3'], ['heavy_sam_3']),
 ('LR_4', 'Air Defence', 'LR-SAM 1995 (Aster 30 Sylver)',   'LR-SAM',   "'95", LR_4, ['ship_SAM_long_range_4'], ['heavy_sam_4']),
]
ICONS = TORP + GUNS + ASHM + RADAR + AIRDEF

# Modules that used to borrow a sprite we now redraw: keep their current art under their own name.
LEGACY = [
 ('GFX_SMI_dual_purpose_arm_module_0', 'gfx/interface/equipmentdesigner/modules/ship_SAM_mid_range_0.dds'),
 ('GFX_SMI_VLS_module_0',              'gfx/interface/equipmentdesigner/modules/ship_SAM_long_range_0.dds'),
 ('GFX_SMI_VLS_module_1',              'gfx/interface/equipmentdesigner/modules/ship_SAM_long_range_1.dds'),
]

# ======================================================================
def label_at(c, x0, x1, y, left, year):
    x = x0
    for part in left.split(' '):
        x = c.text(x, y, part) + 2
    c.text(x1 - c.width(year), y, year)

def render_module(art, left, year):
    c = Canvas(76, 42); c.ox, c.oy = 8, 1; art(c); c.ox = c.oy = 0
    label_at(c, 1, 74, 31, left, year); return c.render()

def render_tech(art, left, year):
    c = Canvas(64, 64); c.ox, c.oy = 2, 12; art(c); c.ox = c.oy = 0
    label_at(c, 2, 61, 42, left, year); return c.render()

def sprite(name, path):
    return '\tspriteType = {\n\t\tname = "%s"\n\t\ttextureFile = "%s"\n\t}\n' % (name, path)

def build(sheet=None):
    os.makedirs(TECH_DIR, exist_ok=True)
    mods, techs, out = [], [], []
    for key, folder, fname, left, year, art, modules, tlist in ICONS:
        os.makedirs(os.path.join(MOD_DIR, folder), exist_ok=True)
        mp = '%s/%s/%s.png' % (MOD_DIR, folder, fname)
        mi = render_module(art, left, year); mi.save(mp)
        ti = render_tech(art, left, year)
        out.append((key, mi, ti))
        for m in modules: mods.append(sprite('GFX_SMI_' + m, mp))
        for t in tlist:
            tp = '%s/%s.png' % (TECH_DIR, t); ti.save(tp)
            techs.append(sprite('GFX_' + t, tp)); techs.append(sprite('GFX_' + t + '_medium', tp))
    with open(GFX_FILE, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# GENERATED by gfx/interface/equipmentdesigner/naval/Modules/_tools/naval_icons.py - edit the script, not this file\n')
        f.write('spriteTypes = {\n\n### CWIC Naval Rework Module Icons\n\n')
        f.writelines(mods)
        f.write('\n### Legacy art for modules that used to borrow a redrawn sprite\n\n')
        f.writelines(sprite(n, p) for n, p in LEGACY)
        f.write('\n### CWIC Naval Rework Tech Icons\n\n')
        f.writelines(techs)
        f.write('}\n')
    if sheet: contact_sheet(out, sheet)
    print('icons:', len(ICONS), 'module sprites:', len(mods), 'tech sprites:', len(techs))

def contact_sheet(out, path, cols=4, sc=3):
    from PIL import Image
    cw, ch = 76 * sc + 64 * sc + 30, 64 * sc + 12
    rows = (len(out) + cols - 1) // cols
    sh = Image.new('RGBA', (cols * cw, rows * ch), (60, 60, 60, 255))
    for i, (key, mi, ti) in enumerate(out):
        x, y = (i % cols) * cw, (i // cols) * ch
        sh.alpha_composite(mi.resize((76 * sc, 42 * sc), Image.NEAREST), (x + 6, y + 6))
        sh.alpha_composite(ti.resize((64 * sc, 64 * sc), Image.NEAREST), (x + 76 * sc + 16, y + 6))
    sh.save(path)

if __name__ == '__main__':
    sheet = sys.argv[sys.argv.index('--sheet') + 1] if '--sheet' in sys.argv else None
    build(sheet)
