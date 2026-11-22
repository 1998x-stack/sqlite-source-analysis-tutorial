#!/usr/bin/env python3
"""Playwright browser QA for desktop and small mobile devices."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PAGES = ["index.html"] + [f"chapters/{i:02}.html" for i in range(1, 29)]
VIEWPORTS = [(1440, 900), (390, 844), (360, 800)]

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "qa-local")
    args = parser.parse_args()
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    result = {"pages": [], "errors": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for file in PAGES:
            for width, height in VIEWPORTS:
                page = browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
                problems: list[str] = []
                page.on("pageerror", lambda err, dst=problems: dst.append(str(err)))
                page.on("console", lambda msg, dst=problems: dst.append(msg.text) if msg.type == "error" else None)
                page.goto((ROOT / file).as_uri(), wait_until="load")
                dims = page.evaluate("({width: document.documentElement.scrollWidth, viewport: innerWidth})")
                if dims["width"] > dims["viewport"] + 1:
                    overflow = page.evaluate("""() => Array.from(document.querySelectorAll('html,body,body *'))
                        .map(el => {
                          const r = el.getBoundingClientRect();
                          return { tag: el.tagName, id: el.id, cls: String(el.className).slice(0,80),
                                   sw: el.scrollWidth, cw: el.clientWidth,
                                   left: Math.round(r.left), right: Math.round(r.right),
                                   overflow: getComputedStyle(el).overflowX };
                        })
                        .filter(x => x.sw > x.cw + 4 || x.right > innerWidth + 4)
                        .sort((a,b) => (b.sw-b.cw)-(a.sw-a.cw))
                        .slice(0, 24)""")
                    problems.append(f"horizontal overflow: {dims}; outside elements: {overflow}")
                images = page.locator("img")
                for index in range(images.count()):
                    image = images.nth(index)
                    image.scroll_into_view_if_needed()
                    decoded = image.evaluate("(img) => img.decode().then(() => img.naturalWidth > 0).catch(() => false)")
                    if not decoded:
                        problems.append(f"image {index} did not load or decode")
                if file == "index.html":
                    q = page.locator("#filter")
                    q.fill("Pager")
                    if page.locator(".chapter-card:visible").count() == 0:
                        problems.append("search failed to display result")
                    q.fill("")
                    if page.locator(".chapter-card:visible").count() != 28:
                        problems.append("search reset failed")
                else:
                    details = page.locator("details").first
                    if details.count() == 0:
                        problems.append("no interactive detail/answer control")
                    else:
                        details.locator("summary").click()
                        if details.get_attribute("open") is None:
                            problems.append("summary control did not open")
                page.screenshot(path=str(out / f"{file.replace('/', '-')}-{width}.png"), full_page=True)
                result["pages"].append({"file": file, "viewport": width, "pass": not problems, "errors": problems})
                result["errors"].extend([f"{file} {width}: {x}" for x in problems])
                page.close()
        ppage = browser.new_page()
        ppage.goto((ROOT / "chapters/05.html").as_uri())
        ppage.emulate_media(media="print")
        ppage.screenshot(path=str(out / "chapter05-print.png"), full_page=True)
        ppage.close()
        ppage = browser.new_page()
        ppage.goto((ROOT / "chapters/10.html").as_uri())
        ppage.emulate_media(media="print")
        ppage.screenshot(path=str(out / "chapter10-print.png"), full_page=True)
        ppage.close()
        printpage = browser.new_page()
        printpage.goto((ROOT / "chapters/15.html").as_uri())
        printpage.emulate_media(media="print")
        printpage.screenshot(path=str(out / "chapter15-print.png"), full_page=True)
        printpage.close()
        printpage = browser.new_page()
        printpage.goto((ROOT / "chapters/20.html").as_uri())
        printpage.emulate_media(media="print")
        printpage.screenshot(path=str(out / "chapter20-print.png"), full_page=True)
        printpage.close()
        printpage = browser.new_page()
        printpage.goto((ROOT / "chapters/21.html").as_uri())
        printpage.emulate_media(media="print")
        printpage.screenshot(path=str(out / "chapter21-print.png"), full_page=True)
        printpage.close()
        printpage = browser.new_page()
        printpage.goto((ROOT / "chapters/25.html").as_uri())
        printpage.emulate_media(media="print")
        printpage.screenshot(path=str(out / "chapter25-print.png"), full_page=True)
        printpage.close()
        for chapter in (26, 27, 28):
            printpage = browser.new_page()
            printpage.goto((ROOT / f"chapters/{chapter:02}.html").as_uri())
            printpage.emulate_media(media="print")
            printpage.screenshot(path=str(out / f"chapter{chapter:02}-print.png"), full_page=True)
            printpage.close()
        browser.close()
    (out / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"views": len(result["pages"]), "failures": result["errors"]}, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
