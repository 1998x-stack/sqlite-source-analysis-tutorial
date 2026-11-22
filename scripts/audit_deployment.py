#!/usr/bin/env python3
"""Verify that the real GitHub Pages payload includes all promised resources."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


def main() -> None:
    errors: list[str] = []
    courses = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "assets/svg/manifest.json").read_text(encoding="utf-8"))
    knowledge = json.loads((ROOT / "data/reading_paths.json").read_text(encoding="utf-8"))

    required = ["index.html", "courses.json", ".nojekyll",
                "evidence/index.html", "examples/index.html",
                "data/reading_paths.json", "audits/2026-11-22.md"]
    required += [f"{i:02}.html" for i in range(1, 29)]
    required += [chapter["file"] for chapter in courses["chapters"]]
    required += [f"evidence/{i:02}.json" for i in range(1, 29)]
    required += ["assets/svg/" + figure["file"] for figure in manifest["figures"]]
    for file in sorted((ROOT / "examples").rglob("*")):
        if not file.is_file():
            continue
        if any(part in {"node_modules", "__pycache__", ".vite", "dist"} for part in file.parts):
            continue
        if file.suffix in {".pyc", ".sqlite", ".sqlite3"}:
            continue
        required.append(file.relative_to(ROOT).as_posix())

    for path in required:
        if not (DIST / path).is_file():
            errors.append(f"site build omitted {path}")

    for folder in ("node_modules", "__pycache__", ".vite", ".git"):
        if (DIST / folder).exists():
            errors.append(f"site build leaked transient directory {folder}")
        if list(DIST.rglob(folder)):
            errors.append(f"site build leaked nested directory {folder}")

    for chapter in courses["chapters"]:
        num = chapter["num"]
        html = (DIST / chapter["file"]).read_text(encoding="utf-8")
        if f'../evidence/{num}.json' not in html:
            errors.append(f"chapter {num}: evidence link missing in deployed HTML")
        if '../examples/index.html' not in html:
            errors.append(f"chapter {num}: examples index missing in deployed HTML")
        for target in knowledge["paths"][num]:
            href = f'{target["target"]}.html#{target["anchor"]}'
            if href not in html:
                errors.append(f"chapter {num}: concept link missing from deployed HTML: {href}")

    print(json.dumps({
        "canonical_chapters": len(courses["chapters"]),
        "redirects": 28,
        "evidence_ledgers": 28,
        "svg_files": len(manifest["figures"]),
        "required_site_files": len(set(required)),
        "errors": errors
    }, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
