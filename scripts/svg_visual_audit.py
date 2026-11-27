#!/usr/bin/env python3
"""Inspect text extents of every original SVG in a real Chromium rendering engine.

Only flags text genuinely outside viewBox, with an 8 SVG-unit tolerance.
This does not prove semantic correctness or detect all overlaps.
"""
from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SVG_DIR = ROOT / "assets" / "svg"
OUTPUT = ROOT / "qa-local" / "svg-label-bounds.json"

JS = """
() => {
  const svg = document.querySelector('svg');
  if (!svg) return {error: 'no root svg'};
  const vb = svg.viewBox.baseVal;
  if (!vb || !vb.width || !vb.height) return {error: 'missing viewBox'};
  const clipped = [];
  const tiny = [];
  for (const node of svg.querySelectorAll('text')) {
    const css = getComputedStyle(node);
    if (css.display === 'none' || css.visibility === 'hidden') continue;
    let box;
    try { box = node.getBBox(); } catch(e) { continue; }
    if (!box.width && !box.height) continue;
    const t = (node.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 100);
    const tol = 8;
    if (box.x < vb.x - tol || box.y < vb.y - tol
      || box.x + box.width > vb.x + vb.width + tol
      || box.y + box.height > vb.y + vb.height + tol) {
      clipped.push({
        text: t,
        x: Math.round(box.x),
        y: Math.round(box.y),
        width: Math.round(box.width),
        height: Math.round(box.height),
        viewBox: [vb.x, vb.y, vb.width, vb.height]
      });
    }
    const size = Number.parseFloat(css.fontSize);
    if (size < 12 && size > 0) tiny.push({text: t, fontSize: size});
  }
  return {clipped, tiny};
}
"""


def main() -> None:
    failures: list[dict] = []
    warnings: list[dict] = []
    files = sorted(SVG_DIR.glob("*.svg"))
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for file in files:
            response = page.goto(file.as_uri(), wait_until="load")
            result = page.evaluate(JS)
            if result.get("error"):
                failures.append({"file": file.name, "error": result["error"]})
                continue
            if result["clipped"]:
                failures.append({"file": file.name, "clipped": result["clipped"]})
            if result["tiny"]:
                warnings.append({"file": file.name, "tiny_labels": result["tiny"][:6]})
        browser.close()
    output = {"files": len(files), "errors": failures, "warnings": warnings}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    print(json.dumps({
        "checked_svg": len(files), "out_of_bounds": len(failures),
        "small_type_warnings": len(warnings)
    }, ensure_ascii=False))
    if failures:
        for issue in failures:
            print(json.dumps(issue, ensure_ascii=False))
        raise SystemExit(1)


if __name__ == "__main__":
    main()
