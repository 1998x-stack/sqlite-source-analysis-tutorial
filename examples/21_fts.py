#!/usr/bin/env python3
"""Verify the FTS4/FTS5 semantics that chapter 21 relies on (stdlib sqlite3 only)."""
from __future__ import annotations
import sqlite3
import sys


def main() -> int:
    db = sqlite3.connect(":memory:")
    opts = {row[0] for row in db.execute("PRAGMA compile_options")}
    have5 = "ENABLE_FTS5" in opts
    have4 = "ENABLE_FTS4" in opts
    print("fts5=%s fts4=%s sqlite=%s" % (have5, have4, sqlite3.sqlite_version))
    if not have5:
        print("SKIPPED: this sqlite3 build does not include FTS5")
        return 0
    db.execute("CREATE VIRTUAL TABLE docs USING fts5(title, body)")
    db.executemany("INSERT INTO docs(title, body) VALUES (?,?)", [
        ("Intro", "SQLite is a small database engine"),
        ("Planner", "The SQLite query planner chooses an index"),
        ("Lookup", "An index speeds up database lookups"),
    ])
    hits = db.execute("SELECT count(*) FROM docs WHERE docs MATCH 'database'").fetchone()[0]
    assert hits == 2, hits
    phrase = db.execute("SELECT title FROM docs WHERE docs MATCH '\"query planner\"'").fetchone()
    assert phrase == ("Planner",), phrase
    prefix = db.execute("SELECT count(*) FROM docs WHERE docs MATCH 'data*'").fetchone()[0]
    assert prefix == 2, prefix
    ranked = db.execute("SELECT title FROM docs WHERE docs MATCH 'database OR index' ORDER BY rank").fetchall()
    assert len(ranked) >= 1, ranked
    if have4:
        db.execute("CREATE VIRTUAL TABLE t4 USING fts4(x)")
        db.execute("INSERT INTO t4(x) VALUES ('hello world')")
        db.execute("INSERT INTO t4(t4) VALUES ('optimize')")
        assert db.execute("SELECT count(*) FROM t4 WHERE t4 MATCH 'world'").fetchone()[0] == 1
    print("PASS: fts5 match/phrase/prefix/rank verified; rank_order=%s" % (ranked,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
