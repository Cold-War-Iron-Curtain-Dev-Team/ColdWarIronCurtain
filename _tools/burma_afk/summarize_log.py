"""Summarize BUR_AFK lines from a HOI4 game.log after an unmanned Burma run.

  python _tools/burma_afk/summarize_log.py [path/to/game.log]

Needs the game rule "Burmese Struggle Test Logging" set to On. Prints the timeline of
wars, resolutions, capitulations, phase changes, AI actions per type, the ending, and the
last monthly snapshot, then a PASS/FAIL verdict: an ending fired and no group stayed
"Unknown" after the KMT spawned.
"""

import re
import sys
from collections import Counter
from pathlib import Path

DEFAULT_LOG = Path.home() / ".local/share/Paradox Interactive/Hearts of Iron IV/logs/game.log"
ACTIONS = {"1": "dialogue", "2": "amnesty", "3": "burmanize", "4": "sweep", "5": "frontier"}
ENDINGS = {"1": "Bamar Supremacy", "2": "Blood of the Tyrants", "3": "A Federal Burma",
           "4": "Land to the Tillers", "5": "Orphaned No More", "6": "Never-Ending Conflict"}
GROUPS = ["", "Communists", "Karen", "Karenni", "Mon", "Shan", "Arakanese", "Rohingya",
          "Kokang", "Kachin", "Chin", "Kuomintang", "Pa-O"]


def fields(line):
    return dict(p.split("=", 1) for p in line.split("|") if "=" in p)


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_LOG
    lines = [l.split("BUR_AFK|", 1)[1].strip() for l in path.read_text(errors="replace").splitlines()
             if "BUR_AFK|" in l]
    if not lines:
        print(f"no BUR_AFK lines in {path}; is the logging rule on?")
        sys.exit(1)
    actions, events, months = Counter(), [], []
    ending = None
    groups = {}
    for l in lines:
        kind = l.split("|", 1)[0]
        f = fields(l)
        if kind == "AI_ACTION":
            actions[(ACTIONS.get(f.get("action", "").split(".")[0], "?"), GROUPS[int(float(f["group"]))])] += 1
        elif kind in ("WAR", "RESOLVE", "CAPITULATION", "PHASE", "KMT_SPAWN"):
            events.append(l)
        elif kind == "ENDING":
            ending = f.get("ending", "").split(".")[0]
            events.append(l)
        elif kind == "MONTH":
            months.append(f)
        elif kind == "GROUPS":
            for k, v in f.items():
                if re.fullmatch(r"g\d+", k):
                    groups[int(k[1:])] = v
    print(f"{len(lines)} lines, {len(months)} monthly snapshots")
    print("\nTimeline:")
    for e in events:
        print("  " + e)
    print("\nAI actions:")
    for (a, g), n in sorted(actions.items()):
        print(f"  {a:10} {g:12} {n}")
    print("\nLast snapshot (status/strength/friendliness/burmanization):")
    for n in sorted(groups):
        print(f"  {GROUPS[n]:12} {groups[n]}")
    unknown = [GROUPS[n] for n, v in groups.items() if v.split("/")[0].split(".")[0] == "5"]
    print(f"\nEnding: {ENDINGS.get(ending, 'none')}")
    ok = ending is not None and not ("Kuomintang" in unknown and any("KMT_SPAWN" in e for e in events))
    print("PASS" if ok else "FAIL")
    sys.exit(0 if ok else 2)


if __name__ == "__main__":
    main()
