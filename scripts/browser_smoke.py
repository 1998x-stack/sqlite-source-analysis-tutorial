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
                elif file.startswith("chapters/"):
                    details = page.locator("details").first
                    if details.count() == 0:
                        problems.append("no interactive detail/answer control")
                    else:
                        details.locator("summary").click()
                        if details.get_attribute("open") is None:
                            problems.append("summary control did not open")
                elif file == "evidence/index.html":
                    if page.locator(".chapter-card").count() != 28:
                        problems.append("public evidence index does not list all 28 chapters")
                    if page.locator('.chapter-card[href="01.json"]').count() != 1:
                        problems.append("public evidence JSON links missing")
                elif file == "examples/index.html":
                    details = page.locator(".example-groups details")
                    if details.count() < 20:
                        problems.append("experimental source index missing chapter groups")
                    else:
                        details.first.locator("summary").click()
                        if details.first.get_attribute("open") is None:
                            problems.append("experiment group did not open")
                        if details.first.locator("a").count() == 0:
                            problems.append("experiment group missing file links")
                if file.startswith("chapters/"):
                    zooms = page.locator("article figure a.svg-zoom")
                    figures = page.locator("article figure")
                    if zooms.count() != figures.count():
                        problems.append("every SVG figure must have a keyboard-focusable original-link")
                    related = page.locator("aside.related-reading a.related-item")
                    if related.count() != 2:
                        problems.append("two conceptual deep links should be present")
                    if width == 360 and zooms.count():
                        zooms.first.focus()
                        if not zooms.first.evaluate("(el) => document.activeElement === el"):
                            problems.append("SVG original link is not keyboard focusable")
                        first_figure = figures.first
                        scroll = first_figure.evaluate("(el) => ({content: el.scrollWidth, width: el.clientWidth})")
                        if scroll["content"] <= scroll["width"]:
                            problems.append("narrow-screen diagram lost its scrollable readable width")
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
        # Exercise real navigation, not only static href strings.
        for source, dest in [("01", "03"), ("14", "15"), ("26", "14")]:
            ppage = browser.new_page(viewport={"width": 1280, "height": 840})
            ppage.goto((ROOT / f"chapters/{source}.html").as_uri())
            hrefs = ppage.locator("aside.related-reading a.related-item")
            if hrefs.count() != 2:
                result["errors"].append(f"chapter {source}: navigation links not rendered")
            else:
                candidate = hrefs.filter(has=ppage.locator("span.related-kicker")).first
                if source == "01":
                    candidate = hrefs.nth(1)
                candidate.click()
                page_num = ppage.url.split("/")[-1].split("#", 1)[0][:2]
                if page_num != dest:
                    result["errors"].append(f"chapter {source}: expected link to {dest}, got {ppage.url}")
                if not ppage.evaluate("() => !!document.querySelector(location.hash)"):
                    result["errors"].append(f"chapter {source}: target anchor missing after navigation")
            ppage.close()
        browser.close()
    (out / "report.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"views": len(result["pages"]), "failures": result["errors"]}, ensure_ascii=False, indent=2))
    if result["errors"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
