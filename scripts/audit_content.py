#!/usr/bin/env python3
"""Deterministic full-site editorial audit for the 28-chapter SQLite course.

Checks local claims/anchors/SEO/figures/evidence, not external HTTP reachability
or the factual truth of an upstream claim. Python stdlib only.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = "https://1998x-stack.github.io/sqlite-source-analysis-tutorial"
SVG_NS = "{http://www.w3.org/2000/svg}"
STATUSES = {"verified", "derived", "illustrative", "unverified"}


class AuditError(Exception):
    pass


def require(ok: bool, message: str, errors: list[str]) -> None:
    if not ok:
        errors.append(message)


class Document(HTMLParser):
    """Collect attributes, anchors and tags without treating code as HTML."""

    def __init__(self, filename: Path):
        super().__init__(convert_charrefs=True)
        self.filename = filename
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str]] = []
        self.metas: dict[str, list[str]] = {}
        self.canonical: list[str] = []
        self.lang: str | None = None
        self.h1 = 0
        self.figures = 0
        self.captions = 0
        self.sections = 0
        self.article = 0
        self.main = 0
        self.details = 0
        self.zoom_links = 0
        self.related_items = 0
        self.title_count = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v or "" for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "a" and a.get("href"):
            self.hrefs.append(a["href"])
            classes = a.get("class", "").split()
            if "svg-zoom" in classes:
                self.zoom_links += 1
            if "related-item" in classes:
                self.related_items += 1
        if tag == "img":
            self.images.append(a)
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.metas.setdefault(key, []).append(a.get("content", ""))
        if tag == "link":
            if a.get("rel") == "canonical":
                self.canonical.append(a.get("href", ""))
            if a.get("href"):
                self.hrefs.append(a["href"])
        self.h1 += (tag == "h1")
        self.title_count += (tag == "title")
        self.figures += (tag == "figure")
        self.captions += (tag == "figcaption")
        self.sections += (tag == "section")
        self.article += (tag == "article")
        self.main += (tag == "main")
        self.details += (tag == "details")


def parse_html(path: Path) -> Document:
    doc = Document(path)
    doc.feed(path.read_text(encoding="utf-8"))
    return doc


def audit() -> tuple[list[str], dict]:
    errors: list[str] = []
    chapters = json.loads((ROOT / "courses.json").read_text(encoding="utf-8"))["chapters"]
    config = json.loads((ROOT / "data/reading_paths.json").read_text(encoding="utf-8"))
    links_by_num = config["paths"]
    expected_nums = [f"{i:02}" for i in range(1, 29)]
    require(len(chapters) == 28, "expected 28 chapters", errors)
    require([c["num"] for c in chapters] == expected_nums, "courses.json order mismatch", errors)
    require(set(links_by_num) == set(expected_nums), "reading-path map must have all 28 chapters", errors)

    html_files = [ROOT / "index.html"] + [ROOT / c["file"] for c in chapters]
    parsed = {p.resolve(): parse_html(p) for p in html_files}
    all_ids = {p: set(d.ids) for p, d in parsed.items()}
    svg_refs: Counter[str] = Counter()
    outgoing: Counter[str] = Counter()
    evidence_count = 0
    verified_count = 0
    concept_links = 0

    for page, doc in parsed.items():
        rel = page.relative_to(ROOT).as_posix()
        duplicates = [v for v, n in Counter(doc.ids).items() if n > 1]
        require(not duplicates, f"{rel}: duplicate IDs {duplicates}", errors)
        require(doc.lang == "zh-CN", f"{rel}: html lang should be zh-CN", errors)
        require(doc.h1 == 1, f"{rel}: expected exactly one h1", errors)
        require(doc.title_count == 1, f"{rel}: expected exactly one title", errors)
        require(doc.main == 1, f"{rel}: expected exactly one main", errors)
        expected_url = SITE + ("/" if rel == "index.html" else "/" + rel)
        require(doc.canonical == [expected_url],
                f"{rel}: expected canonical {expected_url}, got {doc.canonical}", errors)
        require(len(doc.metas.get("description", [])) == 1 and bool(doc.metas["description"][0].strip()),
                f"{rel}: missing/duplicate description", errors)
        require(doc.metas.get("og:url") == [expected_url], f"{rel}: missing/wrong og:url", errors)
        require(bool(doc.metas.get("og:title")), f"{rel}: missing og:title", errors)
        require(bool(doc.metas.get("og:description")), f"{rel}: missing og:description", errors)

        for href in doc.hrefs:
            u = urlsplit(href)
            if u.scheme or u.netloc or href.startswith("//"):
                continue
            dest = ((page.parent / unquote(u.path)).resolve() if u.path else page)
            require(dest.is_relative_to(ROOT), f"{rel}: path escapes repository: {href}", errors)
            if not dest.is_relative_to(ROOT):
                continue
            require(dest.exists(), f"{rel}: broken local URL {href}", errors)
            if u.fragment and dest.exists() and dest.suffix == ".html":
                target_ids = all_ids.get(dest)
                if target_ids is None:
                    target_ids = set(parse_html(dest).ids)
                    all_ids[dest] = target_ids
                require(unquote(u.fragment) in target_ids,
                        f"{rel}: broken cross-page anchor {href}", errors)

        if rel != "index.html":
            num = rel.removeprefix("chapters/").removesuffix(".html")
            require(doc.article == 1, f"{rel}: expected one article", errors)
            require(doc.sections >= 5, f"{rel}: expected five or more sections", errors)
            require(doc.figures >= 2 and doc.figures == doc.captions,
                    f"{rel}: figure/caption mismatch", errors)
            require(doc.figures == doc.zoom_links,
                    f"{rel}: every figure must link to its original SVG", errors)
            require(doc.details >= 1, f"{rel}: missing interactive knowledge check", errors)
            require(doc.related_items == 2, f"{rel}: expected two concept connections", errors)
            require("reading-path" in doc.ids, f"{rel}: missing concept navigation anchor", errors)
            require("#reading-path" in doc.hrefs, f"{rel}: TOC does not link to concept navigation", errors)
            expected_related = [f'{item["target"]}.html#{item["anchor"]}' for item in links_by_num[num]]
            require(all(h in doc.hrefs for h in expected_related),
                    f"{rel}: concept links do not match reading_paths.json", errors)
            require(all(item["target"] != num and len(item["reason"]) >= 12 for item in links_by_num[num]),
                    f"{rel}: self-linked or shallow knowledge connection", errors)
            require(len(set(expected_related)) == 2,
                    f"{rel}: concept connections must lead to two distinct sections", errors)
            require(bool(re.search(r'class="figure-hint"', page.read_text(encoding="utf-8"))),
                    f"{rel}: missing SVG usage hint", errors)
            for item in links_by_num[num]:
                outgoing[num] += 1
                concept_links += 1
            for img in doc.images:
                src = img.get("src", "")
                require(src.startswith("../assets/svg/"), f"{rel}: unexpected figure src {src}", errors)
                require(bool(img.get("alt")), f"{rel}: figure lacks descriptive alt text", errors)
                if src.endswith(".svg"):
                    svg_refs[Path(src).name] += 1
            for part in re.findall(r"<figure\b[^>]*>[\s\S]*?<\/figure>", page.read_text(encoding="utf-8")):
                match = re.search(r'<a class="svg-zoom" href="([^"]+)"[^>]*>\s*<img[^>]+src="([^"]+)"',part)
                require(match is not None and match.group(1) == match.group(2),
                        f"{rel}: figure must wrap the matching vector source in an accessible link", errors)

            evidence = ROOT / "evidence" / f"{num}.json"
            require(evidence.exists(), f"{rel}: evidence ledger missing", errors)
            if evidence.exists():
                data = json.loads(evidence.read_text(encoding="utf-8"))
                require(str(data.get("chapter")) in (num, str(int(num))),
                        f"{rel}: evidence chapter ID mismatch", errors)
                require(bool(data.get("scope")), f"{rel}: evidence has no scope", errors)
                try:
                    date.fromisoformat(data.get("reviewed_at", ""))
                except ValueError:
                    errors.append(f"{rel}: evidence reviewed_at is not ISO date")
                claims = data.get("claims", [])
                require(len(claims) >= 3, f"{rel}: evidence ledger is too small", errors)
                ids = [c.get("id", "") for c in claims]
                require(len(ids) == len(set(ids)), f"{rel}: duplicate evidence IDs", errors)
                for claim in claims:
                    evidence_count += 1
                    require(claim.get("id", "").startswith(num + "-"),
                            f"{rel}: evidence ID prefix mismatch: {claim.get('id')}", errors)
                    require(claim.get("status") in STATUSES,
                            f"{rel}: invalid evidence status: {claim.get('status')}", errors)
                    require(bool(claim.get("claim")) and bool(claim.get("locator")),
                            f"{rel}: incomplete evidence record {claim.get('id')}", errors)
                    u = urlsplit(claim.get("source_url", ""))
                    require(u.scheme == "https" and bool(u.netloc),
                            f"{rel}: evidence requires an HTTPS source URL", errors)
                    verified_count += (claim.get("status") == "verified")

            head = page.read_text(encoding="utf-8").split("</head>", 1)[0]
            if num != "01":
                require(f'<link rel="prev" href="{int(num)-1:02}.html">' in head,
                        f"{rel}: missing head prev relation", errors)
            if num != "28":
                require(f'<link rel="next" href="{int(num)+1:02}.html">' in head,
                        f"{rel}: missing head next relation", errors)

    home = (ROOT / "index.html").read_text(encoding="utf-8")
    cards = re.findall(r'<a class="chapter-card"[^>]*>[\s\S]*?<\/a>', home)
    require(len(cards) == 28, f"homepage: expected 28 cards, got {len(cards)}", errors)
    for c in chapters:
        matches = [card for card in cards if f'href="{c["file"]}"' in card]
        require(len(matches) == 1, f"homepage: missing/duplicate chapter card {c['num']}", errors)
        if len(matches) == 1:
            require(c["title"] in matches[0],
                    f"homepage: chapter title not synchronized: {c['num']}", errors)
            require('class="pill new"' in matches[0],
                    f"homepage: revised badge is missing: {c['num']}", errors)
        require(c["status"] == "revised", f"chapter {c['num']}: obsolete status", errors)
    require('28</strong> 章已深度重构' in home,
            "homepage: revised chapter count has drifted", errors)
    require('83</strong> 张专业 SVG' in home,
            "homepage: SVG figure count has drifted", errors)
    require('id="knowledge-map"' in home, "homepage: mechanism route missing", errors)
    require(not re.search(r'二十篇文章|旧版\s*06[–-]28\s*章尚未|26[–-]28.*尚待逐章',home),
            "homepage: stale project status prose", errors)
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    require(not re.search(r'26[–-]28.*尚待逐章技术审计',agents),
            "AGENTS.md: claims completed chapters are pending review", errors)

    manifest = json.loads((ROOT / "assets/svg/manifest.json").read_text(encoding="utf-8"))
    figures = manifest["figures"]
    files = [f["file"] for f in figures]
    require(len(files) == len(set(files)), "SVG manifest has duplicate filenames", errors)
    svg_disk = sorted(x.name for x in (ROOT / "assets/svg").glob("*.svg"))
    require(set(files) == set(svg_disk), "SVG manifest does not match actual files", errors)
    for figure in figures:
        filename = figure["file"]
        require(figure.get("chapter") in expected_nums,
                f"SVG {filename}: invalid chapter reference", errors)
        require(filename.startswith(figure.get("chapter", "") + "-"),
                f"SVG {filename}: filename and chapter mismatch", errors)
        require(bool(figure.get("source")),
                f"SVG {filename}: missing provenance", errors)
        require(svg_refs[filename] > 0, f"SVG {filename}: orphaned SVG not used by chapter", errors)

    for filename in svg_disk:
        path = ROOT / "assets/svg" / filename
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError as exc:
            errors.append(f"SVG {filename}: XML parse error: {exc}")
            continue
        require(root.tag == SVG_NS + "svg" and bool(root.get("viewBox")),
                f"SVG {filename}: missing namespace or viewBox", errors)
        for name in ("title", "desc"):
            el = root.find(SVG_NS + name)
            require(el is not None and bool("".join(el.itertext()).strip() if el is not None else ""),
                    f"SVG {filename}: missing descriptive {name}", errors)
        forbidden_tags = {"script", "foreignObject"}
        for el in root.iter():
            tag = el.tag.rsplit("}", 1)[-1]
            require(tag not in forbidden_tags,
                    f"SVG {filename}: unsafe or nonportable <{tag}>", errors)
            for k, v in el.attrib.items():
                local = k.rsplit("}", 1)[-1].lower()
                require(not local.startswith("on"),
                        f"SVG {filename}: inline event handler {local}", errors)
                if local in {"href", "src"}:
                    require(not v.startswith(("http:", "https:", "data:", "//")),
                            f"SVG {filename}: external/embedded resource {v[:60]}", errors)

    for i in range(1, 29):
        num = f"{i:02}"
        redirect = ROOT / f"{num}.html"
        require(redirect.exists(), f"legacy redirect {num}.html missing", errors)
        if redirect.exists():
            content = redirect.read_text(encoding="utf-8")
            require("<head>" in content and "<body>" in content and f'chapters/{num}.html' in content,
                    f"legacy redirect {num}.html has invalid structure", errors)
            require(f'<link rel="canonical" href="{SITE}/chapters/{num}.html">' in content,
                    f"legacy redirect {num}.html missing canonical", errors)

    metrics = {
        "chapters": len(chapters),
        "revised_chapters": sum(c["status"] == "revised" for c in chapters),
        "svg_files": len(svg_disk),
        "svg_used_in_chapters": len(svg_refs),
        "svg_placements": sum(svg_refs.values()),
        "evidence_claims": evidence_count,
        "verified_evidence_claims": verified_count,
        "concept_links": concept_links,
        "canonical_chapters": 28,
        "legacy_redirects": 28,
        "errors": len(errors),
    }
    return errors, metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        help="Optionally save JSON report, e.g. qa-local/editorial-audit.json")
    args = parser.parse_args()
    errors, metrics = audit()
    result = {"metrics": metrics, "errors": errors}
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                               encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
