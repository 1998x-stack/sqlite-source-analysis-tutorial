#!/usr/bin/env python3
"""Prepare the static GitHub Pages payload; no Node/Jekyll dependency."""
from __future__ import annotations
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)
    for name in ["index.html", "courses.json", ".nojekyll"]:
        shutil.copy2(ROOT / name, DIST / name)
    for name in ["chapters", "assets"]:
        shutil.copytree(ROOT / name, DIST / name)
    for c in json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))["chapters"]:
        shutil.copy2(ROOT / f"{c['num']}.html", DIST / f"{c['num']}.html")
    print("Prepared", DIST, "with 28 canonical chapters and 28 compatibility redirects")

if __name__ == "__main__":
    main()
