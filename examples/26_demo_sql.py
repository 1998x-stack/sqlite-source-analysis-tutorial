#!/usr/bin/env python3
"""Chapter 26 lab: validate the SQL used by the browser WASM demo on native sqlite3.

The WASM/OPFS part itself runs in a browser and is NOT executed here; this script
only proves that the demo's SQL semantics are correct on a normal SQLite build.
"""
from __future__ import annotations
import sqlite3
import sys

DEMO = """
CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, age INTEGER);
INSERT INTO users(id, name, age) VALUES (1,'张三',20),(2,'李四',17),(3,'王五',25);
"""


def main() -> int:
    db = sqlite3.connect(":memory:")
    db.executescript(DEMO)
    rows = db.execute(
        "SELECT id, name FROM users WHERE age > ? ORDER BY id", (18,)
    ).fetchall()
    assert rows == [(1, "张三"), (3, "王五")], rows
    one = db.execute("SELECT 'Hello, SQLite WASM!' AS message").fetchone()
    assert one == ("Hello, SQLite WASM!",), one
    print("PASS: demo SQL semantics verified on native sqlite3 %s; "
          "browser WASM/OPFS not executed (see notes)" % sqlite3.sqlite_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
