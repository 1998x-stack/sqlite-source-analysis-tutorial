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
    for name in ["chapters", "assets", "evidence", "data", "audits"]:
        shutil.copytree(ROOT / name, DIST / name)
    shutil.copytree(
        ROOT / "examples", DIST / "examples",
        ignore=shutil.ignore_patterns("node_modules", "__pycache__", ".vite", "dist", "*.pyc", "*.sqlite", "*.sqlite3"),
    )
    for c in json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))["chapters"]:
        shutil.copy2(ROOT / f"{c['num']}.html", DIST / f"{c['num']}.html")
    print("Prepared", DIST, "with 28 chapters, 28 redirects, evidence, examples, audit and knowledge graph")

if __name__ == "__main__":
    main()
