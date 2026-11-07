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
ICONS = TORP + GUNS + ASHM

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
