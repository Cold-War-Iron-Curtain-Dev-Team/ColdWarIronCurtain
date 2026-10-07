# Politburo / Presidium inlay: how to use it

This panel sits in the SOV_Stalin focus tree. It shows the leader and up to 24 seats (ministries). Each seat holder has a **faction**, a **Politburo rank** (full member, candidate or none), a **relationship with the leader** and **two traits**. These are **flavour only** for now: they show in the tooltips and have no gameplay effect.

There are two ways to change it:

| You want to... | Do it with |
|---|---|
| Change who sits where, add or remove seats, change the leader, factions or relationships **during the game** | **Effects** (section 2), from focuses, events and decisions |
| Add **new characters, ministries, traits or factions**, change portraits, bios or the panel position | **The data file**, then run the generator (section 3) |

---

## 1. Files

Everything except the data file and the generator is **generated**. Don't edit those files by hand, because the generator overwrites them.

| File | What it is |
|---|---|
| `_tools/presidium/presidium_data.py` | **The only file you edit.** Characters, ministries, traits, factions, the starting setup and the position. |
| `_tools/presidium/gen_presidium.py` | The generator. Run `python gen_presidium.py` from that folder. |
| `common/scripted_effects/SOV_Stalin_presidium_effects.txt` | The effects in section 2, plus init. |
| `common/scripted_localisation/SOV_Stalin_presidium_scripted_loc.txt` | All the dynamic text (names, titles, factions, tooltips). |
| `common/focus_inlay_windows/SOV_Stalin_presidium_inlay_window.txt` | The inlay definition and portrait switching. |
| `interface/SOV_Stalin_presidium_inlay.gui` | The layout: 3 pre-built grids (8, 15 and 24 seats). |
| `interface/SOV_Stalin_presidium.gfx`, `gfx/interface/SOV_pres_blank.tga` | The transparent sprite for hidden slots. |
| `common/on_actions/SOV_Stalin_presidium_on_actions.txt` | Runs init at game start. A monthly check also refreshes the ids if the data file changed. |
| `localisation/english/SOV_Stalin_presidium_l_english.yml` | Names, bios, titles and tooltip text. |

The panel is added to the tree in `SOV_Stalin.txt` with:

```
inlay_window = {
	id = SOV_Stalin_presidium_inlay
	position = { x = 3150 y = 20 }
}
```

To show the same panel in **another tree** (for example after Stalin's death), paste this block into that tree. The panel is visible whenever the flag `SOV_pres_initialized` is set, so its state carries over.

---

## 2. Changing the panel during the game

Everything runs in **SOV country scope** (focus, event or decision effects).

> **HOI4 scripted effects can't take arguments** (`SOV_pres_x = { CHAR = y }` is invalid and breaks the whole file). So you **put the arguments in temp variables first**, then call the effect:
>
> - `pres_char = SOV_pres_char_id_<character key>`
> - `pres_min = SOV_pres_min_id_<ministry key>`

### Seats

```
set_temp_variable = { pres_min = SOV_pres_min_id_gosplan }
SOV_pres_add_seat = yes          # adds an empty Gosplan seat at the end
SOV_pres_remove_seat = yes       # removes the Gosplan seat, later seats move up
SOV_pres_vacate = yes            # empties the Gosplan seat

SOV_pres_clear_seats = yes       # removes every seat
```

The panel picks its layout by seat count: 1–8 seats are large (4×2), 9–15 are medium (5×3), and 16–24 are small (6×4). Adding a seat beyond 24 does nothing.

### People

```
set_temp_variable = { pres_char = SOV_pres_char_id_malenkov }
set_temp_variable = { pres_min = SOV_pres_min_id_gosplan }
SOV_pres_appoint = yes           # he leaves his old seat automatically

set_temp_variable = { pres_char = SOV_pres_char_id_beria }
SOV_pres_dismiss = yes           # he leaves whatever seat he holds
```

- The ministry must already be a seat on the panel (`add_seat` first). Otherwise `appoint` only removes him from his old seat.
- Appointing someone to an occupied seat replaces the old holder, who ends up with no seat.

### Leader, faction, Politburo rank and relationship

These are plain variables. Set them directly:

```
set_variable = { SOV_pres_leader_char = SOV_pres_char_id_khrushchev }
set_variable = { SOV_pres_leader_title = SOV_pres_min_id_first_secretary }

set_variable = { SOV_pres_bulganin_faction = 2 }     # faction id, see section 5
set_variable = { SOV_pres_suslov_rank = 2 }          # Politburo: 2 full, 1 candidate, 0 none
add_to_variable = { SOV_pres_molotov_relation = -20 } # keep it within -100 … 100
```

- **Rank** only affects the display: full members' names are **gold**, candidates' are white and non-members' are grey. The tooltip also shows it.
- **Relationship** is with *the current leader*, so reset it after a change of leader (see recipe 4.6).

### Title: Politburo or Presidium

```
set_country_flag = SOV_pres_presidium_name    # "Presidium of the Central Committee and Government"
clr_country_flag = SOV_pres_presidium_name    # "Politburo of the Central Committee and Government"
```

The 19th Congress focus already sets this flag.

### Raw variables (for triggers)

Seats are stored as **two parallel arrays**. Index 0 is the first seat.

| Variable | Meaning |
|---|---|
| `SOV_pres_seat_min^<i>` | Ministry id of seat i |
| `SOV_pres_seat_char^<i>` | Character id of seat i (0 = vacant) |
| `SOV_pres_seat_min^num` | Number of seats |
| `SOV_pres_leader_char`, `SOV_pres_leader_title` | Leader's character id and title ministry id |
| `SOV_pres_<char>_faction` | Faction id |
| `SOV_pres_<char>_rank` | Politburo rank: 2 full, 1 candidate, 0 none |
| `SOV_pres_<char>_relation` | -100 … 100 |
| `SOV_pres_char_id_<char>`, `SOV_pres_min_id_<ministry>` | Id constants |

Examples of triggers:

```
check_variable = { SOV_pres_beria_relation < 0 }                  # Beria is out of favour
check_variable = { SOV_pres_malenkov_faction = 2 }                # Malenkov is a Technocrat
check_variable = { SOV_pres_suslov_rank = 2 }                     # Suslov is a full Politburo member
check_variable = { SOV_pres_leader_char = SOV_pres_char_id_khrushchev }
```

To check whether someone holds a specific post, loop over the seats:

```
for_each_loop = {
	array = SOV_pres_seat_min
	if = {
		limit = {
			check_variable = { v = SOV_pres_min_id_mgb }
			check_variable = { SOV_pres_seat_char^i = SOV_pres_char_id_abakumov }
		}
		# ... Abakumov is at the MGB
	}
}
```

---

## 3. The data file: adding content

Edit `_tools/presidium/presidium_data.py`, then run:

```
cd "_tools/presidium"
python gen_presidium.py
```

The generator checks your data (unknown traits, factions and so on) and tells you what's wrong before it writes anything.

> **Golden rule:** ids are **list positions**. Only add new characters, ministries and factions **at the end** of their list. Never reorder or delete entries, or saves will show the wrong people. To retire someone, just stop seating him.

### 3.1 Add a character

Add a line at the end of `CHARACTERS`:

```python
dict(key="ponomarenko", politburo=0, name="Panteleimon Ponomarenko", portrait="GFX_some_portrait",
     faction="old_guard", relation=40, traits=["apparatchik", "planner"],
     bio="Belarusian party boss and CC Secretary."),
```

- `portrait` is any existing sprite name. Use `UNKNOWN` if there isn't one yet.
- `relation` and `politburo` are only **starting** values.
- In the game, seat him with `SOV_pres_appoint` (section 2), or put him in `START_SEATS`.

### 3.2 Add a ministry or post

Add a line at the end of `MINISTRIES`: `("minfin", "Minister of Finance"),`

### 3.3 Add or change a trait

Traits are flavour: a name and a one-line description shown in the tooltip.

```python
"reformer": ("Reformer", "Wants to loosen the plan, quietly."),
```

### 3.4 Add a faction

Add a line at the end of `FACTIONS`. Faction display text can use colour codes (`§R … §!`).

### 3.5 Change the starting setup

`START_LEADER` and `START_SEATS` are only applied once, in `SOV_pres_init`. **Changing them needs a new game.**

### 3.6 Change the layout or position

- `INLAY_POSITION`: the generator also rewrites the position in `SOV_Stalin.txt`.
- `MAX_SEATS` and `LAYOUT_BREAKS`: control how many slots exist and when portraits shrink. The last break must equal `MAX_SEATS`.

---

## 4. Recipes (historical changes, 1949–53)

Put these in focus, event or decision effects.

### 4.1 Khrushchev comes to Moscow (December 1949)

```
set_temp_variable = { pres_min = SOV_pres_min_id_ukraine }
SOV_pres_vacate = yes
set_temp_variable = { pres_char = SOV_pres_char_id_popov }
SOV_pres_dismiss = yes
set_temp_variable = { pres_char = SOV_pres_char_id_khrushchev }
set_temp_variable = { pres_min = SOV_pres_min_id_moscow }
SOV_pres_appoint = yes
add_to_variable = { SOV_pres_khrushchev_relation = 10 }
```

### 4.2 The Leningrad Affair (Voznesensky arrested October 1949, Kosygin threatened)

```
set_variable = { SOV_pres_voznesensky_relation = -100 }
add_to_variable = { SOV_pres_kosygin_relation = -20 }
add_to_variable = { SOV_pres_malenkov_relation = 10 }
```

### 4.3 The Navy Ministry is created (February 1950), and Kuznetsov is recalled (July 1951)

```
set_temp_variable = { pres_min = SOV_pres_min_id_navy }
SOV_pres_add_seat = yes
set_temp_variable = { pres_char = SOV_pres_char_id_kuznetsov }
SOV_pres_appoint = yes
# the Armed Forces ministry becomes the War ministry:
set_temp_variable = { pres_min = SOV_pres_min_id_armed_forces }
SOV_pres_remove_seat = yes
set_temp_variable = { pres_min = SOV_pres_min_id_war }
SOV_pres_add_seat = yes
set_temp_variable = { pres_char = SOV_pres_char_id_vasilevsky }
SOV_pres_appoint = yes
```

### 4.4 Abakumov's fall (July 1951)

```
set_temp_variable = { pres_char = SOV_pres_char_id_ignatiev }
set_temp_variable = { pres_min = SOV_pres_min_id_mgb }
SOV_pres_appoint = yes                       # replaces Abakumov in the seat
add_to_variable = { SOV_pres_beria_relation = -15 }
```

### 4.5 19th Congress (October 1952)

This one is already hooked into the focus:

```
set_country_flag = SOV_pres_presidium_name
add_to_variable = { SOV_pres_molotov_relation = -30 }
add_to_variable = { SOV_pres_mikoyan_relation = -30 }
```

### 4.6 After Stalin's death (March 1953): rebuild the whole panel

```
SOV_pres_clear_seats = yes
set_variable = { SOV_pres_leader_char = SOV_pres_char_id_malenkov }
set_variable = { SOV_pres_leader_title = SOV_pres_min_id_premier }
set_temp_variable = { pres_min = SOV_pres_min_id_first_secretary }
SOV_pres_add_seat = yes
set_temp_variable = { pres_char = SOV_pres_char_id_khrushchev }
SOV_pres_appoint = yes
set_temp_variable = { pres_min = SOV_pres_min_id_dep_security }
SOV_pres_add_seat = yes
set_temp_variable = { pres_char = SOV_pres_char_id_beria }
SOV_pres_appoint = yes
set_temp_variable = { pres_min = SOV_pres_min_id_defence }
SOV_pres_add_seat = yes
set_temp_variable = { pres_char = SOV_pres_char_id_bulganin }
SOV_pres_appoint = yes
# relationships are now towards Malenkov:
add_to_variable = { SOV_pres_molotov_relation = 60 }
```

With a handful of seats, the panel switches to the large layout by itself.

---

## 5. Id reference (current data)

### Characters
| id | key | name | Politburo (May 1949) | faction | relation | traits | seat in May 1949 |
|---|---|---|---|---|---|---|---|
| 1 | `stalin` | Joseph Stalin | full | old_guard | 100 | - | leader |
| 2 | `malenkov` | Georgy Malenkov | full | technocrats | 60 | apparatchik, planner | `cadres` |
| 3 | `beria` | Lavrentiy Beria | full | organs | 40 | chekist, industrialist | `dep_atomic` |
| 4 | `khrushchev` | Nikita Khrushchev | full | moderates | 50 | populist, agrarian | `ukraine` |
| 5 | `bulganin` | Nikolai Bulganin | full | moderates | 55 | apparatchik, soldier | `dep_defence` |
| 6 | `kaganovich` | Lazar Kaganovich | full | old_guard | 45 | industrialist, brutal | `dep_industry` |
| 7 | `molotov` | Vyacheslav Molotov | full | old_guard | -40 | diplomat, ideologue | `dep_foreign` |
| 8 | `mikoyan` | Anastas Mikoyan | full | technocrats | -20 | trader, planner | `dep_trade` |
| 9 | `voroshilov` | Kliment Voroshilov | full | old_guard | -20 | soldier, ideologue | `dep_culture` |
| 10 | `shvernik` | Nikolay Shvernik | candidate | old_guard | 20 | apparatchik, populist | `head_of_state` |
| 11 | `vyshinsky` | Andrey Vyshinsky | - | old_guard | 50 | diplomat, brutal | `foreign` |
| 12 | `vasilevsky` | Aleksandr Vasilevsky | - | military | 40 | soldier, planner | `armed_forces` |
| 13 | `kuznetsov` | Nikolay Kuznetsov | - | military | -40 | sailor, scholar | - |
| 14 | `kruglov` | Sergei Kruglov | - | organs | 10 | chekist, industrialist | `mvd` |
| 15 | `ignatiev` | Semyon Ignatiev | - | old_guard | 50 | apparatchik, chekist | - |
| 16 | `saburov` | Maksim Saburov | - | technocrats | 30 | planner, scholar | `gosplan` |
| 17 | `kosygin` | Alexei Kosygin | full | technocrats | -10 | planner, trader | `light_industry` |
| 18 | `zhukov` | Georgy Zhukov | - | military | -60 | soldier, populist | - |
| 19 | `suslov` | Mikhail Suslov | - | old_guard | 50 | ideologue, apparatchik | `ideology` |
| 20 | `gromyko` | Andrei Gromyko | - | technocrats | 20 | diplomat, scholar | - |
| 21 | `shepilov` | Dmitri Shepilov | - | moderates | 30 | ideologue, scholar | - |
| 22 | `abakumov` | Viktor Abakumov | - | old_guard | 60 | chekist, brutal | `mgb` |
| 23 | `popov` | Georgy Popov | - | technocrats | 20 | apparatchik, industrialist | `moscow` |
| 24 | `andreyev` | Andrei Andreyev | full | old_guard | 0 | agrarian, apparatchik | `kolkhoz` |
| 25 | `voznesensky` | Nikolai Voznesensky | - | technocrats | -80 | planner, scholar | - |

### Ministries / posts
| id | key | title |
|---|---|---|
| 1 | `gensec` | General Secretary |
| 2 | `first_secretary` | First Secretary |
| 3 | `premier` | Chairman, Council of Ministers |
| 4 | `head_of_state` | Head of State |
| 5 | `cadres` | CC Secretary |
| 6 | `moscow` | Moscow Party Chief |
| 7 | `ideology` | CC Secretary, Ideology |
| 8 | `dep_security` | Deputy Premier, Security |
| 9 | `dep_defence` | Deputy Premier, Defence |
| 10 | `dep_industry` | Deputy Premier, Industry |
| 11 | `dep_foreign` | Deputy Premier, Foreign |
| 12 | `dep_trade` | Deputy Premier, Trade |
| 13 | `dep_culture` | Deputy Premier, Culture |
| 14 | `foreign` | Foreign Minister |
| 15 | `war` | Minister of War |
| 16 | `defence` | Minister of Defence |
| 17 | `navy` | Minister of the Navy |
| 18 | `mvd` | Minister, MVD |
| 19 | `mgb` | Minister, MGB |
| 20 | `kgb` | Chairman, KGB |
| 21 | `gosplan` | Chairman of Gosplan |
| 22 | `light_industry` | Light Industry |
| 23 | `agriculture` | Minister of Agriculture |
| 24 | `first_deputy` | First Deputy Premier |
| 25 | `armed_forces` | Min. of the Armed Forces |
| 26 | `ukraine` | First Secretary, Ukraine |
| 27 | `kolkhoz` | Council for Kolkhoz Affairs |
| 28 | `dep_atomic` | Deputy Premier, Atomic Project |

### Factions
| id | key | display |
|---|---|---|
| 1 | `old_guard` | Stalinist Old Guard |
| 2 | `technocrats` | Technocrats |
| 3 | `organs` | Security Organs |
| 4 | `moderates` | Party Moderates |
| 5 | `military` | The Army |

### Traits (flavour)
| key | name | description |
|---|---|---|
| `apparatchik` | Apparatchik | A creature of the party machine who knows every file and every favour. |
| `chekist` | Chekist | Formed in the security organs. Sees plots everywhere, and is sometimes right. |
| `brutal` | Brutal | Signs lists without reading them. |
| `planner` | Planner | Thinks in tonnes, quotas and five-year horizons. |
| `industrialist` | Industrialist | Built factories from nothing, whatever the cost. |
| `trader` | Trader | Knows what things cost, abroad and at home. |
| `agrarian` | Agrarian | Has opinions about maize, kolkhozes and the harvest. |
| `soldier` | Soldier | Wore the uniform through the war and still thinks like a front commander. |
| `sailor` | Sailor | A navy man in a land power's government. |
| `diplomat` | Diplomat | Has sat across the table from Churchill and Truman. |
| `ideologue` | Ideologue | Guardian of doctrinal purity. |
| `populist` | Populist | Talks to workers in their own language. |
| `scholar` | Scholar | Reads more than is safe. |


---

## 6. Troubleshooting and engine notes

- **Text shows as `[SOV_pres_...]`:** inlay GUIs only resolve scripted localisation through `context_aware_text` and `context_aware_tooltip`. Plain `text` and `pdx_tooltip` show the raw key. The generator already uses the right ones. Keep them if you hand-edit.
- **The panel is empty, or shows old data after an update:** start a **new game**. `SOV_pres_init` only runs once per save, so a save from an older version keeps its old variables.
- **A portrait is the grey silhouette:** that character's `portrait` is `UNKNOWN`, or the sprite name is wrong.
- **In triggers, `NOT = { A B }` means "neither A nor B"**, not "not both". To negate both together, write `NOT = { AND = { A B } }`.
- **Scripted effects take no arguments** in HOI4. Anything like `SOV_pres_x = { CHAR = y }` fails to load, and can break parsing of the whole file it's in (including a focus tree). Always pass values through temp variables.
- **Buttons:** inlays also support `scripted_buttons` (with `available` and `click_effect`) and `scripted_progressbars`. See `common/focus_inlay_windows/documentation.md` in the vanilla game folder. They aren't used yet.
- **Why the display files are long even though the effects are short:** inlays can only pick a portrait (`scripted_images`) or a text (scripted localisation) through triggers, so each seat needs one branch per character. That code is generated, so you never edit it.

---
