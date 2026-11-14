# ============================================================================
#  Soviet Presidium inlay - MOLOTOV PANEL configuration
#  Companion to presidium_data.py, which holds the shared catalogue
#  (characters, ministries, factions, traits) and the Stalin panel setup.
#  Edit this file, then run:  python gen_molotov_presidium.py
#
#  UNLIKE the Stalin panel, this panel is STATIC: it never reads the shared
#  SOV_pres_* seat array, so no dead, dismissed or stale member can ever
#  appear in it. The generated SOV_pres_molotov_government effect still
#  mirrors this government into the shared state for other content to use.
#
#  The panel is also REVEAL-GATED: when the tree starts, only Molotov (the
#  big leader portrait) is drawn. Each seat appears once the focus that
#  appoints its holder completes (REVEALS below); seats without an owning
#  focus appear once DEFAULT_REVEAL completes. A hidden seat renders a fully
#  blank portrait with no name/post/faction and NO tooltip (hover shows
#  nothing); the appointing focus itself announces the member through its
#  custom_effect_tooltip loc key.
# ============================================================================

from presidium_data import UNKNOWN  # noqa: F401  (silhouette placeholder sprite)

# Block id in the focus_inlay_windows file and in the SOV_Molotov tree
PANEL_ID = "SOV_Molotov_presidium_inlay"
# This panel gets its own .gui window (a geometry clone of the Stalin one)
WINDOW_NAME = "SOV_mpresidium_inlay_window"
# Prefix for this panel's context_aware elements and scripted localisation
PREFIX = "SOV_mpres"

# Output paths (relative to the mod folder "Cold War Iron Curtain")
GUI_FILE = "interface/SOV_Molotov_presidium_inlay.gui"
DEF_FILE = "common/focus_inlay_windows/SOV_Molotov_presidium_inlay_window.txt"
SCRIPTED_LOC_FILE = "common/scripted_localisation/SOV_Molotov_presidium_scripted_loc.txt"
LOC_FILE = "localisation/english/SOV_Molotov_presidium_l_english.yml"
EFFECTS_FILE = "common/scripted_effects/SOV_Molotov_presidium_effects.txt"
ON_ACTIONS_FILE = "common/on_actions/SOV_Molotov_presidium_on_actions.txt"
TREE_FILE = "common/national_focus/SOV_Molotov.txt"

# Panel placement inside SOV_Molotov. CAUTION: inlay positions are in tree
# pixels (vanilla wiki: "same syntax and scale as continuous focus position"),
# BUT the focus view renders zoomed out for wide trees while inlay windows
# keep their full GUI scale - so a naive 150px-per-column collision scan
# overestimates how far right the panel can sit. The position below is
# CALIBRATED IN-GAME (user screenshot, Nov 2026): at x=3100 the panel sat
# roughly a full panel-width away from the KGB branch; x=2250 puts its left
# edge just right of the tree. The panel fits the tree's natural scroll
# bounds (rightmost focus column is 24), so no scroll-bounds spacer focus is
# needed. If the tree layout or panel size changes, expect to re-tune this
# number from a screenshot.
INLAY_POSITION = (2250, 20)

# One fixed seat grid: seats fill the rows in ROW_PROFILE top to bottom, and
# rows narrower than the widest row are centred.
ROW_PROFILE = [6, 6]            # 12 seats in two rows of six

# 1953-era portraits. Values are the mod's OWN sprite names as defined in
# interface/_leader_portraits.gfx - NOT dds basenames (most decade files have
# no sprite named after them; those names render as the grey silhouette).
# Every entry below was verified to point at the intended texture.
PORTRAITS = {
    "molotov":    "GFX_Vyacheslav_Molotov_60s",        # big leader portrait
    "malenkov":   "GFX_Georgy_Malenkov",               # -> Georgy_Malenkov_50s.dds
    "kaganovich": "GFX_Lazar_Kaganovich",              # -> Lazar_Kaganovich_60s.dds
    "suslov":     "GFX_SOV_Minister_Suslov_50s",       # -> Mikhail_Suslov_60s.dds (legacy name)
    "bulganin":   "GFX_Nikolai_Bulganin",              # -> Nikolai_Bulganin_50s.dds
    "kruglov":    "GFX_Sergei_Kruglov",                # -> Sergei_Kruglov_60s.dds
    "shelepin":   "GFX_Alexander_Shelepin",            # -> Alexander_Shelepin_70s.dds
    "konev":      "GFX_FIELD_MARSHALS_Ivan_Konev",     # -> FIELD_MARSHALS/Ivan_Konev.dds
    "voroshilov": "GFX_SOV_Minister_Voroshilov_50s",   # -> Ministers/Kliment_Voroshilov_50s.dds
    "kuznetsov":  "GFX_ADMIRALS_Nikolay_Kuznetsov",    # -> ADMIRALS/Nikolay_Kuznetsov.dds
    "gromyko":    "GFX_Andrei_Gromyko",                # -> Andrei_Gromyko_80s.dds
}
# Seats without art simply stay out of this dict and render as the grey
# silhouette placeholder: "shepilov" (only 80s art exists), "pervukhin"
# (nothing at all yet).

# Portrait art native size (read from the .dds headers) and the big leader
# portrait's scale. Seat scale is height-bound (~0.60); 1.10 keeps Molotov
# clearly the largest figure on the panel (~1.8x a seat portrait's width)
# without towering over the grid.
PORTRAIT_NATIVE = (156, 210)
LEADER_SCALE = 1.10

# Global scale applied to every coordinate and sprite scale in the generated
# .gui (the focus view renders zoomed out for wide trees while inlay windows
# keep full GUI size - 0.8 brings the panel's visual weight closer to the
# focuses). Fonts keep their native size - only geometry and portraits shrink.
UI_SCALE = 0.8

# ---- Molotov government (big portrait; mirrored into the shared state by
#      SOV_pres_molotov_government) ----
START_LEADER = ("molotov", "gensec")

# (ministry, holder), in display order. 12 seats -> 4 columns x 3 rows.
START_SEATS = [
    ("second_secretary", "kaganovich"),   # per the Molotov tree's appointments
    ("premier",          "malenkov"),     # Chairman of the Council of Ministers
    ("deputy_premier",   "shepilov"),
    ("dep_chem_power",   "pervukhin"),    # chemicals, power & nuclear industry
    ("ideology",         "suslov"),
    ("kgb",              "shelepin"),     # via shelepin_empower
    ("mvd",              "kruglov"),      # via kruglov_rehab
    ("defence",          "konev"),        # Zhukov is retired and is not seated
    ("navy",             "kuznetsov"),
    ("foreign",          "gromyko"),
    ("head_of_state",    "voroshilov"),   # Chairman of the Presidium of the Supreme Soviet
    ("gosplan",          "bulganin"),
]

# ---- reveal gating ---------------------------------------------------------
# The panel starts with only Molotov. A seat becomes visible once its holder's
# appointing focus completes; the focus ids MUST exist in SOV_Molotov.txt and
# have english loc titles (the generator asserts both). Each focus listed here
# also carries a hand-added `custom_effect_tooltip = SOV_mpres_reveal_<key>`
# line in its completion_reward in the tree, for which the generator emits the
# loc text ("<Name> joins the Presidium as <post>").
REVEALS = {
    "kaganovich": "SOV_kaganovich_second_secretary",
    "malenkov":   "SOV_Malenkov_Chairman",
    "shepilov":   "SOV_Shepilov_Deputy",
    "suslov":     "SOV_ensure_suslov_loyalty",
    "shelepin":   "SOV_reorganise_kgb",
    "kruglov":    "SOV_kruglov_rehab",
    "konev":      "SOV_encourage_zhukovs_retirement",
    "bulganin":   "SOV_Bulganin_Gosplan",
}
# pervukhin, kuznetsov, gromyko and voroshilov have no appointing focus; they
# arrive with the closing vision focus (its custom_effect_tooltip stays
# generic and names no members).
DEFAULT_REVEAL = "SOV_Molotov_Vision"

# Relations with the leader (flavour) applied by the rebuild into the shared
# state - the static panel's tooltips carry the same numbers baked in.
RELATIONS = {
    "molotov":    100,   # the leader
    "kaganovich": 70,
    "malenkov":   60,
    "shepilov":   40,
    "pervukhin":  50,
    "suslov":     35,
    "shelepin":   45,
    "kruglov":    55,
    "konev":      40,
    "kuznetsov":  30,
    "gromyko":    45,
    "voroshilov": 50,
    "bulganin":   45,
    # the excluded circle (shared-state flavour only, not on the panel)
    "khrushchev": -40,
    "mikoyan":    -20,
    "zhukov":     -30,   # retired
    "kosygin":    10,
    "shvernik":   20,
}

# Politburo standing applied by the rebuild (2 full, 1 candidate, 0 none);
# also drives the static panel's gold/white/grey name colours.
RANKS = {
    "molotov":    2, "malenkov": 2, "kaganovich": 2, "bulganin": 2,
    "voroshilov": 2, "suslov": 2,
    "shepilov":   1, "shelepin": 1, "konev": 1, "pervukhin": 1,
    "kruglov":    1, "kuznetsov": 1,
    "gromyko":    0,
    "khrushchev": 0, "mikoyan": 0, "zhukov": 0,
}

# Molotov-era tooltips. ONLY the panel's cast may be listed here: the leader
# plus every START_SEATS holder (the generator asserts this) - nobody else is
# written into the panel's files.
BIOS = {
    "molotov":    "General Secretary of the Central Committee. The last of the old Bolsheviks now holds the party in his hands.",
    "kaganovich": "Second Secretary of the Central Committee. The iron commissar now runs the party apparatus.",
    "malenkov":   "Chairman of the Council of Ministers. Runs the state machine and the economy from day to day.",
    "shepilov":   "Deputy Premier. Pravda's editor turned economic administrator.",
    "pervukhin":  "Deputy Premier for the chemical, power and nuclear industries; a veteran of the atomic project.",
    "suslov":     "CC Secretary for ideology. The party's grey cardinal keeps the doctrine pure.",
    "shelepin":   "Chairman of the KGB. The young Komsomol chief now commands the sword and shield of the party.",
    "kruglov":    "Minister of Internal Affairs. Master of the camps, the militsiya and the passports.",
    "konev":      "Marshal of the Soviet Union, Minister of Defence.",
    "kuznetsov":  "Minister of the Navy. Back from the 1948 disgrace at last.",
    "gromyko":    "Minister of Foreign Affairs. The man who says nyet.",
    "voroshilov": "Chairman of the Presidium of the Supreme Soviet - head of state, and the oldest comrade of them all.",
    "bulganin":   "Chairman of Gosplan. A political marshal turned economic administrator.",
}
