#!/usr/bin/env python3
"""Chapter 24 lab: exercise an error branch and run a logic-test style comparison."""
from __future__ import annotations
import sqlite3
import sys

CASES = [
    ("SELECT 1+2*3", (7,)),
    ("SELECT 'a'||'b'", ("ab",)),
    ("SELECT 5 IN (1, NULL)", (None,)),
]


def main() -> int:
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, v TEXT NOT NULL)")
    db.execute("INSERT INTO t VALUES (1, 'x')")
    try:
        db.execute("INSERT INTO t VALUES (2, NULL)")
        raise AssertionError("expected a NOT NULL constraint failure")
    except sqlite3.IntegrityError as exc:
        assert "NOT NULL" in str(exc).upper(), exc
    for sql, want in CASES:
        got = db.execute(sql).fetchone()
        assert got == want, (sql, got, want)
    print("PASS: error branch exercised (NOT NULL) and %d logic cases matched; sqlite3 %s"
          % (len(CASES), sqlite3.sqlite_version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
