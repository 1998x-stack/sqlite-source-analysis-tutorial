#!/usr/bin/env python3
"""Static checks for SQLite course pages. No dependencies beyond Python stdlib."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []


def check(condition: bool, message: str) -> None:
    if not condition:
        ERRORS.append(message)


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.h1 = 0
        self.sections = 0
        self.figures = 0
        self.figcaptions = 0
        self.images: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if a.get("id"):
            check(a["id"] not in self.ids, f"duplicate anchor id: {a['id']}")
            self.ids.add(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "section":
            self.sections += 1
        if tag == "figure":
            self.figures += 1
        if tag == "figcaption":
            self.figcaptions += 1
        if tag == "img":
            self.images.append(a.get("src", "") or "")
            check(bool(a.get("alt")), "image must have nonempty alt")
        for attr in ("href", "src"):
            if a.get(attr):
                self.links.append((attr, a[attr]))


def inspect_html(path: Path, *, strict: bool = False) -> Page:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    for attr, href in p.links:
        target = urlsplit(href)
        if target.scheme or target.netloc or href.startswith("//"):
            continue
        dest = (path.parent / unquote(target.path)).resolve() if target.path else path
        check(dest.is_relative_to(ROOT), f"{path.relative_to(ROOT)}: path outside repo: {href}")
        if dest.is_relative_to(ROOT):
            check(dest.exists(), f"{path.relative_to(ROOT)}: missing {attr} target: {href}")
            if strict and target.fragment and dest == path:
                check(unquote(target.fragment) in p.ids, f"{path.relative_to(ROOT)}: missing anchor #{target.fragment}")
    if strict:
        check(p.h1 == 1, f"{path.relative_to(ROOT)}: expected one H1, got {p.h1}")
        check(p.figures == p.figcaptions, f"{path.relative_to(ROOT)}: each figure needs caption")
    return p


def main() -> int:
    chapters = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))["chapters"]
    check(len(chapters) == 28, "courses.json: expected 28 chapters")
    check([c["num"] for c in chapters] == [f"{i:02}" for i in range(1, 29)], "courses.json: numbers/order must be 01..28")
    for required in ["index.html", "AGENTS.md", "README.md", "chapters/theme.css", "assets/css/site.css", ".nojekyll"]:
        check((ROOT / required).exists(), f"missing {required}")
    inspect_html(ROOT / "index.html", strict=True)
    for c in chapters:
        path = ROOT / c["file"]
        check(path.exists(), f"missing chapter {c['num']}: {c['file']}")
        check(c["status"] == ("revised" if int(c["num"]) <= 10 else "legacy"), f"chapter status mismatch: {c['num']}")
        if path.exists():
            p = inspect_html(path, strict=int(c["num"]) <= 10)
            if c["status"] == "revised":
                check(p.sections >= 5, f"{c['num']}: at least five major sections required")
                check(len(p.images) >= 2, f"{c['num']}: at least two diagrams required")
                check(all(src.startswith("../assets/svg/") for src in p.images), f"{c['num']}: diagrams must come from assets/svg")
                evidence_path = ROOT / "evidence" / f"{c['num']}.json"
                check(evidence_path.exists(), f"{c['num']}: missing evidence ledger")
                if evidence_path.exists():
                    ledger = json.loads(evidence_path.read_text(encoding="utf-8"))
                    check(len(ledger.get("claims", [])) >= 3, f"{c['num']}: evidence ledger too small")
                    for claim in ledger.get("claims", []):
                        check(all(claim.get(key) for key in ("id", "claim", "source_url", "locator", "status")), f"{c['num']}: incomplete evidence claim")
                        check(claim.get("status") in ("verified", "derived", "illustrative", "unverified"), f"{c['num']}: invalid evidence status")
        redirect = ROOT / f"{c['num']}.html"
        check(redirect.exists(), f"missing compatibility URL for {c['num']}")
        if redirect.exists():
            inspect_html(redirect)
            check(f"chapters/{c['num']}.html" in redirect.read_text(), f"incorrect old URL redirect: {c['num']}")
    check((ROOT / "chapters" / "index.html").exists(), "legacy chapters/index.html missing")
    manifest = json.loads((ROOT / "assets/svg/manifest.json").read_text(encoding="utf-8"))
    svg_paths = sorted((ROOT / "assets/svg").glob("*.svg"))
    check(len(svg_paths) >= 10, "at least ten tutorial figures expected")
    check({x["file"] for x in manifest.get("figures", [])} == {p.name for p in svg_paths}, "SVG manifest must match files")
    for file in svg_paths:
        try:
            root = ET.parse(file).getroot()
            ns = {"svg": "http://www.w3.org/2000/svg"}
            check(root.tag == "{http://www.w3.org/2000/svg}svg", f"{file.name}: missing SVG namespace")
            check(bool(root.get("viewBox")), f"{file.name}: missing viewBox")
            check(bool(root.find("svg:title", ns) is not None), f"{file.name}: missing SVG title")
            check(bool(root.find("svg:desc", ns) is not None), f"{file.name}: missing SVG description")
            check(len(root.findall(".//svg:text", ns)) >= 3, f"{file.name}: diagram labels missing")
        except ET.ParseError as exc:
            ERRORS.append(f"{file.name}: invalid SVG XML: {exc}")
    css = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")
    check(":focus-visible" in css and "prefers-reduced-motion" in css and "@media print" in css, "CSS lacks accessibility or print rules")
    check("overflow-x:hidden" not in css.replace(" ", ""), "CSS hides horizontal overflow globally")
    if ERRORS:
        print(f"FAILED: {len(ERRORS)} error(s)")
        for x in ERRORS:
            print(" -", x)
        return 1
    print(f"PASS: {len(chapters)} chapters, {len(svg_paths)} SVGs, {sum(c['status'] == 'revised' for c in chapters)} evidence ledgers, local references and a11y structure")
    return 0


if __name__ == "__main__":
    sys.exit(main())
