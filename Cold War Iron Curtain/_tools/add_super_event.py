#!/usr/bin/env python3
# =====================================================================
#  add_super_event.py  -  Add new CWIC super events without hand-editing
#  every file.  Fill in NEW_EVENTS below, then run:  python add_super_event.py
#
#  It patches (append-only, never touches existing entries):
#    common/scripted_localisation/CWIC_Super_Event_Scripted_Loc.txt
#        get_superevent_texture / _title / _quote / _option
#    common/scripted_effects/CWIC_Super_Event_System.txt
#        CWIC_Resolve_Current_SE / CWIC_Clear_All_SE_Flags / CWIC_Reopen_SE_By_Id
#    common/scripted_localisation/CWIC_Super_Event_News_Loc.txt
#        get_se_list_texture / get_se_list_title
#    common/scripted_effects/CWIC_Super_Event_Scripted_Effects.txt
#        appends a <name>_Play fire effect
#
#  To FIRE the event from an event/focus/decision, call:  <name>_Play = yes
# =====================================================================

# ----------------------- FILL THIS IN --------------------------------
NEW_EVENTS = [
    {
        "name":   "Super_Event_Example",                 # fire effect becomes Super_Event_Example_Play
        "flag":   "Super_Event_Example_visible",         # unique country flag identifying this event
        "sprite": "GFX_Big_Example",                     # 600px picture sprite (must exist in a .gfx)
        "title":  "Example Event",                       # popup title (loc key or literal text)
        "quote":  "A memorable quote here. -Someone",    # popup quote text
        "option": "Continue",                            # popup button text
        "song":   "",                                    # play_song name, or "" for no song
    },
]
# ---------------------------------------------------------------------

import os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the "Cold War Iron Curtain" folder
LOC   = os.path.join(BASE, "common/scripted_localisation/CWIC_Super_Event_Scripted_Loc.txt")
SYS   = os.path.join(BASE, "common/scripted_effects/CWIC_Super_Event_System.txt")
NEWS  = os.path.join(BASE, "common/scripted_localisation/CWIC_Super_Event_News_Loc.txt")
FIRE  = os.path.join(BASE, "common/scripted_effects/CWIC_Super_Event_Scripted_Effects.txt")

def read(p):  return open(p, encoding="utf-8-sig").read()
def write(p, s): open(p, "w", encoding="utf-8", newline="\n").write(s)

def block_bounds(s, header):
    """Return (open_index, close_index) of the enclosing block for `header`.
       'name = X' headers live inside a defined_text -> return the defined_text block;
       'NAME = {' headers are their own block."""
    i = s.index(header)
    if header.rstrip().endswith("{"):
        ob = s.index("{", i)          # the header's own brace
    else:
        ob = s.rindex("{", 0, i)      # the enclosing defined_text brace (before "name =")
    d = 0
    for j in range(ob, len(s)):
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return ob, j
    raise ValueError("unbalanced block: " + header)

def insert_before_close(s, header, text):
    ob, cb = block_bounds(s, header)
    return s[:cb] + text + s[cb:]

def insert_before_marker(s, header, marker, text):
    """Insert text right before the first `marker` line inside the block of `header`."""
    ob, cb = block_bounds(s, header)
    m = s.index(marker, ob, cb)
    line_start = s.rindex("\n", ob, m) + 1
    return s[:line_start] + text + s[line_start:]

def next_id(sys_txt):
    ids = [int(n) for n in re.findall(r"CWIC_se_current = (\d+)", sys_txt)]
    return (max(ids) + 1) if ids else 1

def esc(t):  # keep quotes safe inside a "..." localization_key
    return t.replace('"', "'")

def main():
    loc, syst, news, fire = read(LOC), read(SYS), read(NEWS), read(FIRE)
    added, skipped = [], []
    for ev in NEW_EVENTS:
        name, flag, sprite = ev["name"], ev["flag"], ev["sprite"]
        title, quote, option, song = ev.get("title",""), ev.get("quote",""), ev.get("option",""), ev.get("song","")
        if re.search(r"has_country_flag = %s\b" % re.escape(flag), syst):
            skipped.append(flag); continue
        eid = next_id(syst)

        # 1) display loc
        loc = insert_before_close(loc, "name = get_superevent_texture",
              '\ttext = { trigger = { has_country_flag = %s } localization_key = "%s" }\n' % (flag, sprite))
        loc = insert_before_close(loc, "name = get_superevent_title",
              '    text = { trigger = { has_country_flag = %s } localization_key = "%s" }\n' % (flag, esc(title)))
        loc = insert_before_close(loc, "name = get_superevent_quote",
              '    text = { trigger = { has_country_flag = %s } localization_key = "%s" }\n' % (flag, esc(quote)))
        loc = insert_before_close(loc, "name = get_superevent_option",
              '    text = { trigger = { has_country_flag = %s } localization_key = "%s" }\n' % (flag, esc(option)))

        # 2) helper effects
        syst = insert_before_close(syst, "CWIC_Resolve_Current_SE = {",
              '\telse_if = { limit = { has_country_flag = %s } set_variable = { CWIC_se_current = %d } }\n' % (flag, eid))
        syst = insert_before_marker(syst, "CWIC_Clear_All_SE_Flags = {",
              "clr_country_flag = CWIC_Super_Event_Visible",
              '\tclr_country_flag = %s\n' % flag)
        syst = insert_before_marker(syst, "CWIC_Reopen_SE_By_Id = {",
              "set_variable = { CWIC_se_current = CWIC_se_reopen }",
              '\telse_if = { limit = { check_variable = { CWIC_se_reopen = %d } } set_country_flag = %s }\n' % (eid, flag))

        # 3) news list loc
        news = insert_before_close(news, "name = get_se_list_texture",
              '\ttext = { trigger = { check_variable = { CWIC_se_view = %d } } localization_key = "%s" }\n' % (eid, sprite))
        news = insert_before_close(news, "name = get_se_list_title",
              '\ttext = { trigger = { check_variable = { CWIC_se_view = %d } } localization_key = "%s" }\n' % (eid, esc(title)))

        # 4) fire effect
        song_line = ('\t\t\tplay_song = "%s"\n' % song) if song else ""
        fire = fire.rstrip() + "\n\n%s_Play = {\n\thidden_effect = {\n\t\tevery_country = {\n\t\t\tlimit = { is_ai = no }\n%s\t\t\tset_country_flag = %s\n\t\t\tCWIC_Show_Super_Event = yes\n\t\t}\n\t}\n}\n" % (name, song_line, flag)

        added.append((name, flag, eid))

    write(LOC, loc); write(SYS, syst); write(NEWS, news); write(FIRE, fire)
    print("Added %d event(s):" % len(added))
    for n, f, i in added: print("   id %-3d  %s  (call %s_Play = yes)" % (i, f, n))
    if skipped: print("Skipped (flag already present): " + ", ".join(skipped))

if __name__ == "__main__":
    main()
