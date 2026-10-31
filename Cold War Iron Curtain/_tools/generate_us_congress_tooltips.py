"""Generate state-scoped Congress map tooltips; no selected-state target is used.

Motto spellings and translations cross-checked against:
https://en.wikipedia.org/wiki/List_of_U.S._state_and_territory_mottos
https://alaska.gov/kids/student.htm
Oregon's 1957-1987 motto is selected by the in-game date.
Formatting follows JAP_country_localisation_l_english.yml faction tooltips and
CWIC_Culture_l_english.yml: coloured headings, dividers and spaced information.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALISATION = ROOT / "localisation/english/US_Congress_Map_l_english.yml"
SCRIPTED_LOC = ROOT / "common/scripted_localisation/USA_congress_map_localisation.txt"

# Abbreviation | representative state ID | name | motto | English translation.
# These are political-state representatives; a US state may span several map states.
STATE_DATA = """AL|367|Alabama|Audemus jura nostra defendere|We dare defend our rights.
AK|463|Alaska|North to the Future|Adopted in 1967.
AZ|377|Arizona|Ditat Deus|God enriches.
AR|372|Arkansas|Regnat populus|The people rule.
CA|378|California|Eureka|I have found it.
CO|382|Colorado|Nil sine numine|Nothing without providence.
CT|863|Connecticut|Qui transtulit sustinet|He who transplanted still sustains.
DE|860|Delaware|Liberty and Independence|
DC|1200|District of Columbia|Justitia omnibus|Justice for all.
FL|366|Florida|In God We Trust|
GA|365|Georgia|Wisdom, Justice, Moderation|
HI|629|Hawaii|Ua mau ke ea o ka aina i ka pono|The life of the land is perpetuated in righteousness.
ID|387|Idaho|Esto perpetua|Let it be perpetual.
IL|395|Illinois|State Sovereignty, National Union|
IN|396|Indiana|The Crossroads of America|
IA|392|Iowa|Our liberties we prize and our rights we will maintain|
KS|383|Kansas|Ad astra per aspera|To the stars through difficulties.
KY|369|Kentucky|United we stand, divided we fall|
LA|371|Louisiana|Union, Justice, Confidence|
ME|861|Maine|Dirigo|I lead.
MD|361|Maryland|Fatti maschi, parole femine|Strong deeds, gentle words.
MA|357|Massachusetts|Ense petit placidam sub libertate quietem|By the sword we seek peace, but peace only under liberty.
MI|393|Michigan|Si quaeris peninsulam amoenam circumspice|If you seek a pleasant peninsula, look about you.
MN|391|Minnesota|L'Etoile du Nord|The star of the North.
MS|370|Mississippi|Virtute et armis|By valor and arms.
MO|373|Missouri|Salus populi suprema lex esto|Let the welfare of the people be the supreme law.
MT|388|Montana|Oro y plata|Gold and silver.
NE|384|Nebraska|Equality Before the Law|
NV|379|Nevada|All for Our Country|
NH|862|New Hampshire|Live Free or Die|
NJ|359|New Jersey|Liberty and Prosperity|
NM|376|New Mexico|Crescit eundo|It grows as it goes.
NY|358|New York|Excelsior|Ever upward.
NC|363|North Carolina|Esse quam videri|To be, rather than to seem.
ND|389|North Dakota|Liberty and Union Now and Forever, One and Inseparable|
OH|261|Ohio|With God, all things are possible|Adopted in 1959.
OK|374|Oklahoma|Labor omnia vincit|Labor conquers all things.
OR|385|Oregon|Alis volat propriis|She flies with her own wings.
PA|360|Pennsylvania|Virtue, Liberty and Independence|
PR|686|Puerto Rico|Joannes est nomen ejus|John is his name.
RI|864|Rhode Island|Hope|
SC|364|South Carolina|Dum spiro spero; Animis opibusque parati|While I breathe, I hope; ready in soul and resource.
SD|390|South Dakota|Under God the People Rule|
TN|368|Tennessee|Agriculture and Commerce|
TX|375|Texas|Friendship|
UT|380|Utah|Industry|
VT|865|Vermont|Freedom and Unity|
VA|362|Virginia|Sic semper tyrannis|Thus always to tyrants.
WA|386|Washington|Alki|By and by. Traditional territorial motto.
WV|859|West Virginia|Montani semper liberi|Mountaineers are always free.
WI|394|Wisconsin|Forward|
WY|381|Wyoming|Equal Rights|"""
STATES = [dict(zip(("abbr", "id", "name", "motto", "translation"), line.split("|")))
          for line in STATE_DATA.splitlines()]


def text_function(name, entries):
    result = ["defined_text = {", f"\tname = {name}"]
    for trigger, key in entries:
        result += ["\ttext = {", f"\t\ttrigger = {{ {trigger} }}",
                   f"\t\tlocalization_key = {key}", "\t}"]
    return "\n".join(result + ["}", ""])


def generate():
    assert len(STATES) == 52 and len({s['id'] for s in STATES}) == 52
    loc = {}
    for state in STATES:
        abbr, sid, name = (state[key] for key in ("abbr", "id", "name"))
        motto = f'§Y"{state["motto"]}"§!'
        if state["translation"]:
            motto += f'\n§g{state["translation"]}§!'
        if abbr == "OR":
            loc["USA_CONGRESS_MOTTO_ORIGINAL_OR"] = motto
            motto = "[385.GetUSACongressOregonMotto]"
        loc[f"USA_CONGRESS_MAP_{abbr}_TT"] = (
            f"§C{name}§!\n{motto}\n-------------------------------------\n"
            f"§YSenate delegation§!\n[{sid}.GetUSACongressHoverDelegation]\n\n"
            f"[{sid}.GetUSACongressHoverElectionInfo]\n"
            "-------------------------------------\n"
            f"§gClick to view {name}'s political details.§!"
        )
    loc.update({
        "USA_CONGRESS_HOVER_DEM": "§CDemocratic delegation§!",
        "USA_CONGRESS_HOVER_GOP": "§RRepublican delegation§!",
        "USA_CONGRESS_HOVER_SPLIT": "§CDemocratic§! / §RRepublican§! split delegation",
        "USA_CONGRESS_HOVER_TERRITORY": "§gUS territory · no voting senators§!",
        "USA_CONGRESS_HOVER_DC": "§gFederal district · no voting senators§!",
        "USA_CONGRESS_HOVER_UNASSIGNED": "§gNo senators currently assigned§!",
        "USA_CONGRESS_HOVER_PVI_DEM": "§CDemocratic advantage: [?This.d_pvi|%0]§!",
        "USA_CONGRESS_HOVER_PVI_GOP": "§RRepublican advantage: [?This.r_pvi|%0]§!",
        "USA_CONGRESS_HOVER_PVI_EVEN": "§gEvenly balanced§!",
        "USA_CONGRESS_HOVER_PVI_NONE": "§gNo partisan-lean data available§!",
        "USA_CONGRESS_HOVER_LEAN": "§YPartisan lean§!\n[This.GetUSACongressHoverPVI]",
        "USA_CONGRESS_HOVER_PRIMARY": "§YPrimary campaign§!\n[This.GetStateCurrentIssueLongMap]\n§Y[This.GetStateCurrentIssuePositionMap]§!\n\n§YPartisan lean§!\n[This.GetUSACongressHoverPVI]",
        "USA_CONGRESS_MOTTO_UNION_OR": '§Y"The Union"§!',
    })
    scripted = "# Generated by _tools/generate_us_congress_tooltips.py.\n"
    scripted += text_function("GetUSACongressHoverDelegation", [
        ("USA_congress_state_is_territory = yes", "USA_CONGRESS_HOVER_TERRITORY"),
        ("check_variable = { id = 1200.id }", "USA_CONGRESS_HOVER_DC"),
        ("USA_congress_has_dem_senator = yes USA_congress_has_gop_senator = yes", "USA_CONGRESS_HOVER_SPLIT"),
        ("USA_congress_has_dem_senator = yes", "USA_CONGRESS_HOVER_DEM"),
        ("USA_congress_has_gop_senator = yes", "USA_CONGRESS_HOVER_GOP"),
        ("always = yes", "USA_CONGRESS_HOVER_UNASSIGNED"),
    ])
    scripted += text_function("GetUSACongressHoverPVI", [
        ("NOT = { has_variable = d_pvi } NOT = { has_variable = r_pvi }", "USA_CONGRESS_HOVER_PVI_NONE"),
        ("check_variable = { d_pvi > r_pvi }", "USA_CONGRESS_HOVER_PVI_DEM"),
        ("check_variable = { r_pvi > d_pvi }", "USA_CONGRESS_HOVER_PVI_GOP"),
        ("always = yes", "USA_CONGRESS_HOVER_PVI_EVEN"),
    ])
    scripted += text_function("GetUSACongressHoverElectionInfo", [
        ("USA = { check_variable = { show_usa_congress_alt = 2 } }", "USA_CONGRESS_HOVER_PRIMARY"),
        ("always = yes", "USA_CONGRESS_HOVER_LEAN"),
    ])
    scripted += text_function("GetUSACongressOregonMotto", [
        ("date > 1956.12.31 date < 1987.1.1", "USA_CONGRESS_MOTTO_UNION_OR"),
        ("always = yes", "USA_CONGRESS_MOTTO_ORIGINAL_OR"),
    ])
    # JSON string escaping also produces the quotes and literal newlines needed by HOI4 localisation.
    localisation = "l_english:\n" + "\n".join(
        f" {key}:0 {json.dumps(value, ensure_ascii=False)}" for key, value in loc.items()
    ) + "\n"
    return localisation, scripted


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    for path, content in zip((LOCALISATION, SCRIPTED_LOC), generate()):
        # Localisation YAML requires a BOM; Clausewitz script must start directly
        # with its comment/definition. A BOM here is parsed as an unknown token.
        encoding = "utf-8-sig" if path == LOCALISATION else "utf-8"
        if args.check:
            assert path.read_text(encoding=encoding) == content, f"Regenerate {path.name}"
        else:
            path.write_text(content, encoding=encoding, newline="\n")
    print("PASS: 52 state-scoped map tooltips are current.")


if __name__ == "__main__":
    main()
