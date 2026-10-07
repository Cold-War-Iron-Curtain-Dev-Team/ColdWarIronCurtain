# ============================================================================
#  Soviet Presidium inlay - DATA FILE
#  Edit this file, then run:  python gen_presidium.py
#
#  IDs: factions, domains, ministries and characters are numbered by their
#  position in their list (1, 2, 3...). Only ADD new entries at the END of a
#  list, so existing saves keep the same ids.
#
#  Everything below except MAX_SEATS / LAYOUT_BREAKS is only the STARTING
#  state or the catalogue. Seats, ministries, holders, factions, relations and
#  the leader can all be changed in game with the effects listed in
#  common/scripted_effects/SOV_presidium_effects.txt.
# ============================================================================

# Panel placement inside SOV_Stalin (pixels, same scale as focus positions)
INLAY_POSITION = (1180, 20)

# The GUI has fixed slots; this is the most seats the panel can ever show.
MAX_SEATS = 24
# Seat counts where the panel switches to smaller portraits:
# <=8 seats large, <=15 medium, <=MAX_SEATS small.
LAYOUT_BREAKS = [8, 15, MAX_SEATS]

# Internal factions. In game: set_variable = { SOV_pres_<char>_faction = <number> }
FACTIONS = [
    ("old_guard",   "§iStalinist Old Guard§!"),   # 1  crimson
    ("technocrats", "§4Technocrats§!"),           # 2  light blue
    ("organs",      "§0Security Organs§!"),       # 3  violet
    ("moderates",   "§6Party Moderates§!"),       # 4  turquoise
    ("military",    "§uThe Army§!"),              # 5  olive
]

# Every ministry/post that can exist. (key, title)
MINISTRIES = [
    ("gensec",         "General Secretary"),
    ("first_secretary","First Secretary"),
    ("premier",        "Chairman, Council of Ministers"),
    ("head_of_state",  "Head of State"),
    ("cadres",         "CC Secretary"),
    ("moscow",         "Moscow Party Chief"),
    ("ideology",       "CC Secretary, Ideology"),
    ("dep_security",   "Deputy Premier, Security"),
    # NOTE: ids are positions - new posts go at the END
    ("dep_defence",    "Deputy Premier, Defence"),
    ("dep_industry",   "Deputy Premier, Industry"),
    ("dep_foreign",    "Deputy Premier, Foreign"),
    ("dep_trade",      "Deputy Premier, Trade"),
    ("dep_culture",    "Deputy Premier, Culture"),
    ("foreign",        "Foreign Minister"),
    ("war",            "Minister of War"),
    ("defence",        "Minister of Defence"),
    ("navy",           "Minister of the Navy"),
    ("mvd",            "Minister, MVD"),
    ("mgb",            "Minister, MGB"),
    ("kgb",            "Chairman, KGB"),
    ("gosplan",        "Chairman of Gosplan"),
    ("light_industry", "Light Industry"),
    ("agriculture",    "Minister of Agriculture"),
    ("first_deputy",   "First Deputy Premier"),
    ("armed_forces",   "Min. of the Armed Forces"),
    ("ukraine",        "First Secretary, Ukraine"),
    ("kolkhoz",        "Council for Kolkhoz Affairs"),
    ("dep_atomic",     "Deputy Premier, Atomic Project"),
]

# Traits are flavour only (shown in tooltips, no gameplay effect). key: (name, description)
TRAITS = {
    "apparatchik":   ("Apparatchik",   "A creature of the party machine who knows every file and every favour."),
    "chekist":       ("Chekist",       "Formed in the security organs. Sees plots everywhere, and is sometimes right."),
    "brutal":        ("Brutal",        "Signs lists without reading them."),
    "planner":       ("Planner",       "Thinks in tonnes, quotas and five-year horizons."),
    "industrialist": ("Industrialist", "Built factories from nothing, whatever the cost."),
    "trader":        ("Trader",        "Knows what things cost, abroad and at home."),
    "agrarian":      ("Agrarian",      "Has opinions about maize, kolkhozes and the harvest."),
    "soldier":       ("Soldier",       "Wore the uniform through the war and still thinks like a front commander."),
    "sailor":        ("Sailor",        "A navy man in a land power's government."),
    "diplomat":      ("Diplomat",      "Has sat across the table from Churchill and Truman."),
    "ideologue":     ("Ideologue",     "Guardian of doctrinal purity."),
    "populist":      ("Populist",      "Talks to workers in their own language."),
    "scholar":       ("Scholar",       "Reads more than is safe."),
}

UNKNOWN = "GFX_leader_unknown"

# relation = starting relationship with the current leader (-100..100)
# politburo = starting Politburo rank: 2 full member, 1 candidate, 0 not a member
CHARACTERS = [
    dict(key="stalin", politburo=2,     name="Joseph Stalin",       portrait="GFX_Joseph_Stalin_50sLate", faction="old_guard",   relation=100, traits=[],
         bio="The Vozhd. Every seat around this table exists at his pleasure."),
    dict(key="malenkov", politburo=2,   name="Georgy Malenkov",     portrait="GFX_Georgy_Malenkov",       faction="technocrats", relation=60,  traits=["apparatchik", "planner"],
         bio="Back in the Secretariat since 1948, he is busy destroying the Leningrad group."),
    dict(key="beria", politburo=2,      name="Lavrentiy Beria",     portrait="GFX_Lavrentiy_Beria",       faction="organs",      relation=40,  traits=["chekist", "industrialist"],
         bio="Runs the atomic bomb project. He lost the security ministries in 1946, and Abakumov's MGB is hunting his people."),
    dict(key="khrushchev", politburo=2, name="Nikita Khrushchev",   portrait="GFX_Nikita_Khrushchev_50s", faction="moderates",   relation=50,  traits=["populist", "agrarian"],
         bio="First Secretary of Ukraine. Stalin will call him to Moscow before the year is out."),
    dict(key="bulganin", politburo=2,   name="Nikolai Bulganin",    portrait="GFX_Nikolai_Bulganin",      faction="moderates",   relation=55,  traits=["apparatchik", "soldier"],
         bio="A political marshal overseeing the armed forces and defence industry."),
    dict(key="kaganovich", politburo=2, name="Lazar Kaganovich",    portrait="GFX_Lazar_Kaganovich",      faction="old_guard",   relation=45,  traits=["industrialist", "brutal"],
         bio="The iron commissar of heavy industry and the railways."),
    dict(key="molotov", politburo=2,    name="Vyacheslav Molotov",  portrait="GFX_Vyacheslav_Molotov_50s", faction="old_guard",  relation=-40, traits=["diplomat", "ideologue"],
         bio="Removed from the Foreign Ministry in March 1949; his wife Polina was arrested in January."),
    dict(key="mikoyan", politburo=2,    name="Anastas Mikoyan",     portrait="GFX_Anastas_Mikoyan",       faction="technocrats", relation=-20, traits=["trader", "planner"],
         bio="Removed from the Ministry of Foreign Trade in March 1949. The great survivor."),
    dict(key="voroshilov", politburo=2, name="Kliment Voroshilov",  portrait="GFX_FIELD_MARSHALS_Kliment_Voroshilov", faction="old_guard", relation=-20, traits=["soldier", "ideologue"],
         bio="Stalin's old comrade from Tsaritsyn, lately suspected of being a British spy."),
    dict(key="shvernik", politburo=1,   name="Nikolay Shvernik",    portrait="GFX_Nikolay_Shvernik",      faction="old_guard",   relation=20,  traits=["apparatchik", "populist"],
         bio="Chairman of the Presidium of the Supreme Soviet."),
    dict(key="vyshinsky", politburo=0,  name="Andrey Vyshinsky",    portrait=UNKNOWN,                     faction="old_guard",   relation=50,  traits=["diplomat", "brutal"],
         bio="Prosecutor of the Moscow Trials, Foreign Minister since March 1949."),
    dict(key="vasilevsky", politburo=0, name="Aleksandr Vasilevsky", portrait="GFX_FIELD_MARSHALS_Aleksandr_Vasilevsky", faction="military", relation=40, traits=["soldier", "planner"],
         bio="Minister of the Armed Forces since March 1949, planner of the great wartime offensives."),
    dict(key="kuznetsov", politburo=0,  name="Nikolay Kuznetsov",   portrait="GFX_ADMIRALS_Nikolay_Kuznetsov", faction="military", relation=-40,  traits=["sailor", "scholar"],
         bio="Demoted by the 1948 naval court of honour. He will be recalled."),
    dict(key="kruglov", politburo=0,    name="Sergei Kruglov",      portrait="GFX_Sergei_Kruglov",        faction="organs",      relation=10,  traits=["chekist", "industrialist"],
         bio="Minister of Internal Affairs, master of the camp economy."),
    dict(key="ignatiev", politburo=0,   name="Semyon Ignatiev",     portrait=UNKNOWN,                     faction="old_guard",   relation=50,  traits=["apparatchik", "chekist"],
         bio="A Central Committee organiser, still a minor figure in 1949."),
    dict(key="saburov", politburo=0,    name="Maksim Saburov",      portrait=UNKNOWN,                     faction="technocrats", relation=30,  traits=["planner", "scholar"],
         bio="Replaced the disgraced Voznesensky at Gosplan in March 1949."),
    dict(key="kosygin", politburo=2,    name="Alexei Kosygin",      portrait="GFX_Alexei_Kosygin",        faction="technocrats", relation=-10, traits=["planner", "trader"],
         bio="Minister of Light Industry. The Leningrad Affair is closing in on him."),
    dict(key="zhukov", politburo=0,     name="Georgy Zhukov",       portrait="GFX_FIELD_MARSHALS_Georgy_Zhukov", faction="military", relation=-60, traits=["soldier", "populist"],
         bio="The Marshal of Victory, exiled to the Urals Military District."),
    dict(key="suslov", politburo=0,     name="Mikhail Suslov",      portrait=UNKNOWN,                     faction="old_guard",   relation=50,  traits=["ideologue", "apparatchik"],
         bio="CC Secretary for ideology and editor of Pravda, the party's grey cardinal."),
    dict(key="gromyko", politburo=0,    name="Andrei Gromyko",      portrait="GFX_Andrei_Gromyko",        faction="technocrats", relation=20,  traits=["diplomat", "scholar"],
         bio="First Deputy Foreign Minister."),
    dict(key="shepilov", politburo=0,   name="Dmitri Shepilov",     portrait="GFX_Dmitry_Shepilov",       faction="moderates",   relation=30,  traits=["ideologue", "scholar"],
         bio="Editor at Pravda and rising ideological voice."),
    dict(key="abakumov", politburo=0,   name="Viktor Abakumov",     portrait=UNKNOWN,                     faction="old_guard",   relation=60,  traits=["chekist", "brutal"],
         bio="Minister of State Security, SMERSH veteran and Beria's rival. He is building the Leningrad case."),
    dict(key="popov", politburo=0,      name="Georgy Popov",        portrait=UNKNOWN,                     faction="technocrats", relation=20,  traits=["apparatchik", "industrialist"],
         bio="First Secretary of Moscow, with too many enemies in the Politburo."),
    dict(key="andreyev", politburo=2,   name="Andrei Andreyev",     portrait=UNKNOWN,                     faction="old_guard",   relation=0,   traits=["agrarian", "apparatchik"],
         bio="Chairman of the Council for Kolkhoz Affairs; his link-system farming is out of favour."),
    dict(key="voznesensky", politburo=0, name="Nikolai Voznesensky", portrait=UNKNOWN,                    faction="technocrats", relation=-80, traits=["planner", "scholar"],
         bio="The brilliant planner of the war economy, dismissed in March 1949 and awaiting his fate."),
]

# ---- Starting state (applied once by SOV_pres_init) ----
START_LEADER = ("stalin", "premier")         # (character, leader title ministry)
START_SEATS = [                              # (ministry, holder or None), in display order
    # --- Politburo, May 1949 (full members after Voznesensky's removal on 7 Mar 1949) ---
    ("cadres",         "malenkov"),      # CC Secretary
    ("dep_atomic",     "beria"),         # Special Committee (atomic bomb); lost the security organs in 1946
    ("dep_foreign",    "molotov"),       # lost the Foreign Ministry 4 Mar 1949
    ("dep_trade",      "mikoyan"),       # lost Foreign Trade 4 Mar 1949
    ("dep_industry",   "kaganovich"),
    ("dep_defence",    "bulganin"),      # left the Armed Forces Ministry 24 Mar 1949
    ("dep_culture",    "voroshilov"),
    ("ukraine",        "khrushchev"),    # to Moscow in Dec 1949
    ("kolkhoz",        "andreyev"),
    ("light_industry", "kosygin"),
    # --- Politburo candidate ---
    ("head_of_state",  "shvernik"),
    # --- Government / apparatus, not Politburo members ---
    ("ideology",       "suslov"),        # CC Secretary
    ("moscow",         "popov"),         # Moscow party chief until Dec 1949
    ("foreign",        "vyshinsky"),     # since 4 Mar 1949
    ("armed_forces",   "vasilevsky"),    # since 24 Mar 1949
    ("mvd",            "kruglov"),
    ("mgb",            "abakumov"),      # until Jul 1951
    ("gosplan",        "saburov"),       # since Mar 1949
]
