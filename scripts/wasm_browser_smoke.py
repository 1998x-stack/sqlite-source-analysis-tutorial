#!/usr/bin/env python3
"""Browser integration test for the SQLite WASM Worker + OPFS demo."""
from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "26_wasm"
URL = "http://127.0.0.1:4173"


def wait_for_server(process: subprocess.Popen[str]) -> None:
    last_error: Exception | None = None
    for _ in range(60):
        if process.poll() is not None:
            raise RuntimeError("Vite exited before becoming ready")
        try:
            with urllib.request.urlopen(URL, timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = exc
        time.sleep(0.5)
    raise RuntimeError(f"Vite did not become ready: {last_error}")


def run_once(page) -> tuple[str, dict]:
    page.locator("#run").click()
    page.wait_for_function(
        "() => document.querySelector('#status').textContent.startsWith('完成')",
        timeout=60000,
    )
    status = page.locator("#status").inner_text()
    rows = json.loads(page.locator("#output").inner_text())
    if len(rows) != 1 or rows[0].get("id") != 1:
        raise AssertionError(f"unexpected WASM query result: {rows!r}")
    return status, rows[0]


def main() -> None:
    process = subprocess.Popen(
        ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", "4173", "--strictPort"],
        cwd=EXAMPLE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server(process)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1280, "height": 900})
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            response = page.goto(URL, wait_until="load")
            if response is None or response.status != 200:
                raise AssertionError("WASM demo did not return HTTP 200")
            headers = response.headers
            if headers.get("cross-origin-opener-policy") != "same-origin":
                raise AssertionError("COOP header is missing")
            if headers.get("cross-origin-embedder-policy") != "require-corp":
                raise AssertionError("COEP header is missing")

            first_status, first = run_once(page)
            page.reload(wait_until="load")
            second_status, second = run_once(page)
            if "opfs" in first_status.lower():
                if second["count"] != first["count"] + 1:
                    raise AssertionError(
                        f"OPFS data did not survive a connection/page reload: {first} -> {second}"
                    )
            else:
                if second["count"] != 1:
                    raise AssertionError(f"memory fallback should start fresh: {second}")
            if errors:
                raise AssertionError("browser errors: " + "; ".join(errors))

            out = ROOT / "qa-local"
            out.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(out / "wasm-worker-opfs.png"), full_page=True)
            print(json.dumps({
                "status": "PASS",
                "first": {"mode": first_status, "row": first},
                "after_reload": {"mode": second_status, "row": second},
                "coop": headers.get("cross-origin-opener-policy"),
                "coep": headers.get("cross-origin-embedder-policy"),
            }, ensure_ascii=False, indent=2))
            browser.close()
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


if __name__ == "__main__":
    main()
