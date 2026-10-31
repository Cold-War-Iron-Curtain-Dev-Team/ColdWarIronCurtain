#!/usr/bin/env python3
"""Run every CWIC generator: python _tools/build_all.py  (exits non-zero if any build reports errors)."""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDS = [
    "super_events/build_super_events.py",
    "companies/build_companies.py",
    "religions/build_religions.py",
    "cultures/build_cultures.py",
    "goods/build_goods.py",
]

failed = []
for b in BUILDS:
    print("==", b)
    if subprocess.call([sys.executable, os.path.join(HERE, b)]) != 0:
        failed.append(b)
print("\nAll builds OK." if not failed else "\nFAILED: " + ", ".join(failed))
sys.exit(1 if failed else 0)
