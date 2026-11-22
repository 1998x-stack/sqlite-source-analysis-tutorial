#!/usr/bin/env python3
"""Chapter 27 lab: check 3.53+ features that are observable on the local build."""
from __future__ import annotations
import sqlite3
import sys


def version() -> tuple[int, ...]:
    return tuple(int(part) for part in sqlite3.sqlite_version.split("."))


def main() -> int:
    v = version()
    if v < (3, 53, 0):
        print("SKIPPED: needs SQLite 3.53.0+ (found %s)" % sqlite3.sqlite_version)
        return 0
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, e TEXT, n INTEGER)")
    db.execute("CREATE INDEX ie ON t(lower(e))")  # expression index
    db.execute("INSERT INTO t(id,e,n) VALUES(1,'A',10)")
    db.execute("REINDEX EXPRESSIONS")             # 3.53.0
    db.execute("UPDATE t SET n=11 WHERE id=1")    # indexed value unchanged
    hit = db.execute("SELECT id FROM t WHERE lower(e)='a'").fetchone()
    assert hit == (1,), hit
    one = db.execute("SELECT (SELECT 1 UNION SELECT 2 LIMIT 1)").fetchone()
    assert one == (1,), one
    print("PASS: REINDEX EXPRESSIONS, expression-index consistency and UNION LIMIT ok; sqlite3 %s"
          % sqlite3.sqlite_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
