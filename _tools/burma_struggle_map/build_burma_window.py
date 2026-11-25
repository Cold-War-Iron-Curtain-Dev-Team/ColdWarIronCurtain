"""Build the Burma struggle window: .gui, the Struggle_GUI_Burma scripted gui block,
and the window's scripted localisation.

  python _tools/burma_struggle_map/build_burma_map.py      (sprites, run first)
  python _tools/burma_struggle_map/build_burma_window.py

Outputs:
  interface/Burma_Struggle_Window.gui
  common/scripted_guis/Burma_Struggle_Window.txt
All layout constants live here; edit them, rerun, render.
"""

import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
MOD = HERE.parents[1] / "Cold War Iron Curtain"
REPORT = json.loads((HERE / "report.json").read_text(encoding="utf-8"))
HIT_REL = "gfx/Scripted_GUI_Special/Struggle/Burma_Window"

W, H = 1150, 1068
FONT_SMALL = "AceCombat14"
FONT_MED = "AceCombat16"
FONT_HEAD = "AceCombat16"

GROUP_KEYS = ["", "COMMUNISTS", "KAREN", "KARENNI", "MON", "SHAN", "ARAKANESE",
              "ROHINGYA", "KOKANG", "KACHIN", "CHIN", "KUOMINTANG", "PAO"]
STATE_GROUP = {"Communists": 1, "Karen": 2, "Karenni": 3, "Mon": 4, "Shan": 5,
               "Arakanese": 6, "Rohingya": 7, "Kokang": 8, "Kachin": 9, "Chin": 10,
               "Kuomintang": 11, "Pa-O": 12}
ENDING_ART = ["Government_Victory", "Rebel_Victory", "Federal_Ending",
              "Communist_Victory", "Kuomintang_Victory"]
ACTIONS = [("Dialogue", "dialogue"), ("Amnesty", "amnesty"), ("Burmanize", "burmanize"),
           ("Sweep", "sweep"), ("Frontier", "frontier")]

MAP_X, MAP_Y, MAP_W, MAP_H = 15, 160, 560, 560
COL_X, COL_W = 590, 545
HEADER_H = 35
SEL_Y, ACT_Y, GRP_Y, END_Y = 160, 354, 512, 724
ROW_H = 14

hits = set()


def hit(w, h):
    hits.add((w, h))
    return f"GFX_BUR_hit_{w}x{h}"


def write_hits():
    out = MOD / HIT_REL
    lines = ["spriteTypes = {"]
    for w, h in sorted(hits):
        name = f"BUR_hit_{w}x{h}.png"
        Image.new("RGBA", (w, h), (0, 0, 0, 0)).save(out / name)
        lines.append(f'\tspriteType = {{ name = "GFX_BUR_hit_{w}x{h}" textureFile = "{HIT_REL}/{name}" }}')
    lines.append("}")
    (MOD / "interface/Burma_Struggle_Hit.gfx").write_text("\n".join(lines) + "\n", encoding="utf-8")


def icon(name, sprite, x, y, extra=""):
    return (f'\t\ticonType = {{\n\t\t\tname = "{name}"\n\t\t\tspriteType = "{sprite}"\n'
            f'\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tOrientation = "UPPER_LEFT"\n{extra}\t\t}}\n')


def button(name, sprite, x, y, tooltip=None, text=None, font=None, extra=""):
    s = (f'\t\tbuttonType = {{\n\t\t\tname = "{name}"\n\t\t\tspriteType = "{sprite}"\n'
         f'\t\t\tposition = {{ x = {x} y = {y} }}\n\t\t\tOrientation = "UPPER_LEFT"\n')
    if text:
        s += f'\t\t\tbuttonText = "{text}"\n\t\t\tbuttonFont = "{font}"\n'
    if tooltip:
        s += f'\t\t\tpdx_tooltip = "{tooltip}"\n'
    return s + extra + "\t\t}\n"


def text(name, value, x, y, w, h=20, font=FONT_SMALL, fmt="left"):
    return (f'\t\tinstantTextboxType = {{\n\t\t\tname = "{name}"\n\t\t\tposition = {{ x = {x} y = {y} }}\n'
            f'\t\t\ttextureFile = ""\n\t\t\tfont = "{font}"\n\t\t\tborderSize = {{x = 0 y = 0}}\n'
            f'\t\t\ttext = "{value}"\n\t\t\tmaxWidth = {w}\n\t\t\tmaxHeight = {h}\n\t\t\tformat = {fmt}\n\t\t}}\n')


def header(name, key, x, y, wide=False):
    sprite = "GFX_BUR_header_wide" if wide else "GFX_BUR_header_col"
    return icon(f"{name}_bar", sprite, x, y) + text(f"{name}_text", key, x + 12, y + 9, 500, 20, FONT_HEAD)


def build_gui():
    g = []
    a = g.append
    a('guiTypes = {\n\tcontainerWindowType = {\n\t\tname = "CWIC_Struggle_Mechanic_Burma"\n'
      f'\t\tposition = {{ x = 384 y = 6 }}\n\t\tsize = {{ width = {W} height = {H} }}\n'
      '\t\tfade_time = 300\n\t\tfade_type = linear\n\t\tmoveable = yes\n\t\tclipping = no\n\n'
      '\t\tbackground = {\n\t\t\tname = "Background"\n\t\t\tspriteType = "GFX_BUR_window_bg"\n\t\t}\n')
    a('\t\tbuttonType = {\n\t\t\tname = "close_button"\n\t\t\tposition = { x = -45 y = 5 }\n'
      '\t\t\tquadTextureSprite = "GFX_closebutton"\n\t\t\tshortcut = "ESCAPE"\n'
      '\t\t\tOrientation = "UPPER_RIGHT"\n\t\t\tclicksound = click_close\n\t\t\tpdx_tooltip = "CLOSE"\n\t\t}\n')
    a(text("struggle_title", "BUR_WINDOW_TITLE", 22, 6, 700, 26, "hoi_36header"))

    a(button("burma_phase_icon", "GFX_Crisis_High_Intensity_Phase", 20, 60, "BUR_TT_CURRENT_PHASE"))
    a(text("current_phase_head", "BUR_CURRENT_PHASE_HEAD", 106, 58, 280))
    a(text("current_phase_title", "[BurmaStruggleCurrentPhaseName]", 106, 78, 280, 24, FONT_MED))
    a(button("Participants_Button", "GFX_button_261x34", 106, 106, "BUR_TT_INVOLVEMENT",
             "BUR_PARTICIPANTS_BTN", FONT_MED))

    for i, (key, yy, bar, line, meter, tt) in enumerate([
            ("down", 58, "GFX_BUR_phase_bar_green", "[BurmaStruggleDownLine]", "[BurmaStruggleDownMeter]", "BUR_TT_METER_DOWN"),
            ("up", 104, "GFX_BUR_phase_bar_red", "[BurmaStruggleUpLine]", "[BurmaStruggleUpMeter]", "BUR_TT_METER_UP")]):
        a(text(f"burma_{key}_line", line, 470, yy, 290))
        a(text(f"burma_{key}_value", meter, 760, yy, 90, fmt="right"))
        a(icon(f"burma_{key}_track", "GFX_BUR_phase_track", 470, yy + 22))
        a(icon(f"burma_{key}_bar", bar, 470, yy + 22))
        a(button(f"burma_{key}_hit", hit(380, 40), 470, yy - 4, tt))

    a(text("struggle_modifiers_title", "BUR_MODIFIERS_HEAD", 878, 58, 250))
    for i, (n, s) in enumerate([("ARMY", "Army"), ("ECONOMY", "Economy"),
                                ("GOVERNMENT", "Government"), ("DIPLOMACY", "Diplomacy")]):
        a(icon(f"Struggle_{s}_Icon", f"GFX_Crisis_{s}_Icon", 878 + i * 48, 84))
        a(button(f"burma_modifier_{s.lower()}_hit", hit(36, 36), 878 + i * 48, 84, f"BUR_MODIFIER_{n}_TT"))

    a(icon("burma_map_panel", "GFX_BUR_map_panel_bg", MAP_X, MAP_Y))
    ox = MAP_X + (MAP_W - REPORT["frame_width"]) // 2
    oy = MAP_Y + (MAP_H - REPORT["frame_height"]) // 2
    for sid, st in REPORT["states"].items():
        x, y = ox + st["offset"][0], oy + st["offset"][1]
        if st["group"] is None:
            a(icon(f"BUR_State_{sid}", f"GFX_BUR_state_{sid}", x, y))
        else:
            n = STATE_GROUP[st["group"]]
            a(button(f"BUR_State_{sid}", f"GFX_BUR_state_{sid}", x, y, f"BUR_GROUP_TT_{n}"))
    for i, key in enumerate(["ACTIVE", "INTEGRATED", "SUBJUGATED", "AUTONOMOUS", "JOINED_BCP", "UNKNOWN", "LOYAL"]):
        y = MAP_Y + MAP_H - 18 * 7 - 8 + i * 18
        a(icon(f"burma_legend_swatch_{i + 1}", "GFX_BUR_legend_swatch", MAP_X + 12, y + 1,
               f"\t\t\tframe = {i + 1}\n"))
        a(text(f"burma_legend_text_{i + 1}", f"BUR_LEG_{key}", MAP_X + 42, y, 300))

    a(header("burma_selected", "BUR_SELECTED_HEAD", COL_X, SEL_Y))
    cy = SEL_Y + HEADER_H + 8
    a(text("burma_card_name", "[BurmaSelName]", COL_X + 10, cy, 380, 22, FONT_MED))
    a(text("burma_card_status", "[BurmaSelectedGroupStatus]", COL_X + COL_W - 170, cy, 160, 22, FONT_MED, "right"))
    a(text("burma_card_members", "[BurmaStruggleGroupMembers]", COL_X + 10, cy + 26, COL_W - 20))
    rows = [("friend", "BUR_LBL_FRIEND", "GFX_BUR_bar_green", "[BurmaSelFriendText]", [60, 90], 100, "BUR_TT_CARD_FRIEND"),
            ("burma", "BUR_LBL_BURMAN", "GFX_BUR_bar_yellow", "[BurmaSelBurmanText]", [40, 80], 100, "BUR_TT_CARD_BURMAN"),
            ("strength", "BUR_LBL_STRENGTH", "GFX_BUR_strength_bar", "[BurmaSelStrengthText]", [200], 1000, "BUR_TT_CARD_STRENGTH"),
            ("front", "BUR_LBL_FRONT", "GFX_BUR_bar_red", "[BurmaSelFrontText]", [], 100, "BUR_TT_CARD_FRONT")]
    for i, (key, label, bar, value, ticks, mx, tt) in enumerate(rows):
        ry = cy + 54 + i * 24
        bx = COL_X + 140
        a(text(f"burma_card_{key}_label", label, COL_X + 10, ry, 125))
        a(icon(f"burma_card_{key}_track", "GFX_BUR_bar_track", bx, ry + 5))
        a(icon(f"burma_card_{key}_bar", bar, bx, ry + 5))
        for t in ticks:
            a(icon(f"burma_card_{key}_tick_{t}", "GFX_BUR_meter_tick", bx + round(230 * t / mx) - 1, ry + 2))
        a(text(f"burma_card_{key}_value", value, bx + 240, ry, 60, fmt="right"))
        a(button(f"burma_card_{key}_hit", hit(COL_W - 20, 22), COL_X + 10, ry - 2, tt))

    a(header("burma_action", "BUR_ACTION_HEAD", COL_X, ACT_Y))
    for i, (label, key) in enumerate(ACTIONS):
        x = COL_X + 8 + (i % 2) * 270
        y = ACT_Y + HEADER_H + 8 + (i // 2) * 38
        a(button(f"Burma_Action_{label}_Button", "GFX_button_261x34", x, y, f"BUR_TT_{key.upper()}",
                 f"BUR_ACTION_{key.upper()}", "hoi_18mbs"))

    a(header("burma_groups", "BUR_GROUPS_HEAD", COL_X, GRP_Y))
    a(text("burma_col_status", "BUR_COL_STATUS", COL_X + 260, GRP_Y + 11, 150))
    a(text("burma_col_strength", "BUR_COL_STRENGTH", COL_X + COL_W - 130, GRP_Y + 11, 120, fmt="right"))
    for n in range(1, 13):
        y = GRP_Y + HEADER_H + 6 + (n - 1) * ROW_H
        a(icon(f"burma_row_{n}_swatch", "GFX_BUR_group_swatch", COL_X + 12, y + 1))
        a(text(f"burma_row_{n}_name", f"[BurmaRowName{n}]", COL_X + 32, y - 2, 220, 16))
        a(text(f"burma_row_{n}_status", f"[BurmaRowStatus{n}]", COL_X + 260, y - 2, 160, 16))
        a(text(f"burma_row_{n}_strength", f"[BurmaRowStrength{n}]", COL_X + COL_W - 130, y - 2, 120, 16, fmt="right"))
        a(button(f"Burma_Row_{n}", hit(COL_W - 8, ROW_H), COL_X + 4, y - 1, f"BUR_GROUP_TT_{n}"))

    a(header("burma_endings", "BUR_ENDINGS_HEAD", 15, END_Y, wide=True))
    card_y = END_Y + HEADER_H + 2
    gap = (1120 - 5 * 217) // 4
    start = 15 + (1120 - (5 * 217 + 4 * gap)) // 2
    for k in range(1, 6):
        x = start + (k - 1) * (217 + gap)
        a(icon(f"Burma_Ending_Icon_{k}", f"GFX_Burmese_{ENDING_ART[k - 1]}_Inactive", x, card_y))
        a(icon(f"Burma_Ending_CRT_{k}", "GFX_Bottom_CRT_Overlay_Layer_2", x, card_y))
        a(icon(f"Burma_Ending_Overlay_Inactive_{k}", "GFX_Bottom_Top_Overlay_Inactive", x, card_y))
        a(icon(f"Burma_Ending_Overlay_Active_{k}", "GFX_Bottom_Top_Overlay_Active", x, card_y))
        a(text(f"Burma_Ending_Status_{k}", f"[BurmaEndingStatus{k}]", x + 8, card_y + 8, 201, 34, "AceCombat28", "center"))
        a(text(f"Burma_Ending_Title_{k}", f"BUR_ENDING_{k}_TITLE", x + 8, card_y + 250, 201, 40, FONT_MED, "center"))
        a(button(f"Burma_Ending_Card_{k}", hit(217, 300), x, card_y, f"BUR_END_TT_{k}"))
    a("\t}\n}\n")
    (MOD / "interface/Burma_Struggle_Window.gui").write_text("".join(g), encoding="utf-8")


def build_scripted_gui():
    s = []
    a = s.append
    a("\tStruggle_GUI_Burma = {\n\t\tcontext_type = player_context\n\t\twindow_name = \"CWIC_Struggle_Mechanic_Burma\"\n"
      "\t\tvisible = {\n\t\t\tcheck_variable = { View_Burma_Struggle = 1 }\n\t\t}\n"
      "\t\tai_enabled = {\n\t\t\talways = no\n\t\t}\n\t\tproperties = {\n")
    a('\t\t\tburma_phase_icon = {\n\t\t\t\timage = "[BurmaStrugglePhaseIconForPhase]"\n\t\t\t}\n')
    for sid, st in REPORT["states"].items():
        frame = "7" if st["group"] is None else f"global.BUR_frame_{STATE_GROUP[st['group']]}"
        a(f"\t\t\tBUR_State_{sid} = {{\n\t\t\t\tframe = {frame}\n\t\t\t}}\n")
    for n in range(1, 13):
        a(f"\t\t\tburma_row_{n}_swatch = {{\n\t\t\t\tframe = global.BUR_swatch_{n}\n\t\t\t}}\n")
    for name, var in [("burma_down_bar", "global.BUR_deescalation"), ("burma_up_bar", "global.BUR_escalation"),
                      ("burma_card_friend_bar", "global.BUR_sel_friend"), ("burma_card_burma_bar", "global.BUR_sel_burman"),
                      ("burma_card_strength_bar", "global.BUR_sel_strength"), ("burma_card_front_bar", "global.BUR_sel_front")]:
        a(f"\t\t\t{name} = {{\n\t\t\t\tframe = {var}\n\t\t\t}}\n")
    for k in range(1, 6):
        a(f'\t\t\tBurma_Ending_Icon_{k} = {{\n\t\t\t\timage = "[BurmaEndingImage{k}]"\n\t\t\t}}\n')
    a("\t\t}\n\t\ttriggers = {\n")
    for k in range(1, 6):
        a(f"\t\t\tBurma_Ending_Overlay_Inactive_{k}_visible = {{\n\t\t\t\tNOT = {{ check_variable = {{ global.BUR_ending_available = {k} }} }}\n\t\t\t}}\n")
        a(f"\t\t\tBurma_Ending_Overlay_Active_{k}_visible = {{\n\t\t\t\tcheck_variable = {{ global.BUR_ending_available = {k} }}\n\t\t\t}}\n")
    conds = {
        "Dialogue": ["has_political_power > 49", "check_variable = { global.BUR_selected_group < 11 }"],
        "Amnesty": ["has_political_power > 74", "check_variable = { global.BUR_sel_friend > 19 }"],
        "Burmanize": ["has_political_power > 49", "check_variable = { global.BUR_selected_group < 11 }"],
        "Sweep": ["command_power > 9", "has_manpower > 499"],
        "Frontier": ["has_political_power > 99", "check_variable = { global.BUR_selected_group > 1 }",
                     "check_variable = { global.BUR_selected_group < 11 }"],
    }
    for label, key in ACTIONS:
        body = "\n".join(f"\t\t\t\t{c}" for c in ["tag = BRM", "check_variable = { global.BUR_sel_status = 0 }",
                                                   f"check_variable = {{ global.num_days > global.BUR_sel_cd_{key} }}"] + conds[label])
        a(f"\t\t\tBurma_Action_{label}_Button_click_enabled = {{\n{body}\n\t\t\t}}\n")
    a("\t\t}\n\t\teffects = {\n\t\t\tclose_button_click = {\n\t\t\t\tset_variable = { View_Burma_Struggle = 0 }\n\t\t\t}\n")
    a("\t\t\tParticipants_Button_click = {\n\t\t\t}\n")
    for sid, st in REPORT["states"].items():
        if st["group"] is not None:
            a(f"\t\t\tBUR_State_{sid}_click = {{\n\t\t\t\tset_variable = {{ global.BUR_selected_group = {STATE_GROUP[st['group']]} }}\n"
              "\t\t\t\tBUR_sync_display = yes\n\t\t\t}\n")
    for n in range(1, 13):
        a(f"\t\t\tBurma_Row_{n}_click = {{\n\t\t\t\tset_variable = {{ global.BUR_selected_group = {n} }}\n"
          "\t\t\t\tBUR_sync_display = yes\n\t\t\t}\n")
    for k in range(1, 6):
        a(f"\t\t\tBurma_Ending_Card_{k}_click = {{\n\t\t\t\tset_variable = {{ struggle_ending_display_value = {k} }}\n"
          "\t\t\t\tset_variable = { show_burma_end_gui = 1 }\n\t\t\t}\n")
    for label, key in ACTIONS:
        a(f"\t\t\tBurma_Action_{label}_Button_click = {{\n\t\t\t\tBUR_action_{key} = yes\n\t\t\t}}\n")
    a("\t\t}\n\t}\n")
    (MOD / "common/scripted_guis/Burma_Struggle_Window.txt").write_text("scripted_gui = {\n" + "".join(s) + "}\n", encoding="utf-8")


def dt(name, texts):
    body = "".join(f"\ttext = {{ {('trigger = { ' + t + ' } ') if t else ''}localization_key = {k} }}\n" for t, k in texts)
    return f"defined_text = {{\n\tname = {name}\n{body}}}\n"


def build_scripted_loc():
    d = []
    for n in range(1, 13):
        unk = f"check_variable = {{ global.BUR_status^{n} = 5 }}"
        name = [(unk, "BUR_GROUP_UNKNOWN")]
        if n == 11:
            name.append(("has_global_flag = ROC_Victory", "BUR_GROUP_11_PRC"))
        name.append(("", f"BUR_GROUP_{n}"))
        d.append(dt(f"BurmaRowName{n}", name))
        d.append(dt(f"BurmaRowStatus{n}", [(f"check_variable = {{ global.BUR_status^{n} = {s} }}", f"BUR_GROUP_STATUS_{s}") for s in range(7)]))
        d.append(dt(f"BurmaRowStrength{n}", [(unk, "BUR_UNKNOWN_VALUE"), ("", f"BUR_ROW_STR_{n}")]))
        d.append(dt(f"BurmaGroupStatusText{n}", [(f"check_variable = {{ global.BUR_status^{n} = {s} }}", f"BUR_GROUP_STATUS_{s}") for s in range(7)]))
    sel_unk = "check_variable = { global.BUR_sel_status = 5 }"
    for key in ["Friend", "Burman", "Strength", "Front"]:
        d.append(dt(f"BurmaSel{key}Text", [(sel_unk, "BUR_UNKNOWN_VALUE"), ("", f"BUR_SEL_VAL_{key.upper()}")]))
    d.append(dt("BurmaSelName", [(sel_unk, "BUR_GROUP_UNKNOWN"),
                                 ("check_variable = { global.BUR_selected_group = 11 } has_global_flag = ROC_Victory", "BUR_GROUP_11_PRC")]
                + [(f"check_variable = {{ global.BUR_selected_group = {n} }}", f"BUR_GROUP_{n}") for n in range(1, 13)]))
    d.append(dt("BurmaSelectedGroupStatus", [(f"check_variable = {{ global.BUR_sel_status = {s} }}", f"BUR_GROUP_STATUS_{s}") for s in range(7)]))
    d.append(dt("BurmaKmtTTBody", [("check_variable = { global.BUR_status^11 = 5 }", "BUR_GROUP_TT_11_UNKNOWN"),
                                   ("", "BUR_GROUP_TT_11_STATS")]))
    for label, key in ACTIONS:
        d.append(dt(f"BurmaCd{label}", [(f"check_variable = {{ global.num_days > global.BUR_sel_cd_{key} }}", "BUR_CD_READY"),
                                        ("", f"BUR_CD_LEFT_{key.upper()}")]))
    for k in range(1, 6):
        d.append(dt(f"BurmaEndingStatus{k}", [(f"check_variable = {{ global.BUR_ending_available = {k} }}", "BUR_STATUS_AVAILABLE"),
                                             ("", "BUR_STATUS_LOCKED")]))
        art = ENDING_ART[k - 1]
        d.append(dt(f"BurmaEndingImage{k}", [(f"check_variable = {{ global.BUR_ending_available = {k} }}", f"GFX_Burmese_{art}_Active"),
                                            ("", f"GFX_Burmese_{art}_Inactive")]))
    (MOD / "common/scripted_localisation/Burma_Struggle_Window_Scripted_Loc.txt").write_text("".join(d), encoding="utf-8")


if __name__ == "__main__":
    build_gui()
    build_scripted_gui()
    build_scripted_loc()
    write_hits()
    print("gui, scripted gui block, scripted loc and", len(hits), "hit sprites written")
