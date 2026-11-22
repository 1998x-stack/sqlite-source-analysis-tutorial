#!/usr/bin/env python3
"""Chapter 22 lab: expression indexes, the deterministic rule, and REINDEX EXPRESSIONS."""
from __future__ import annotations
import sqlite3
import sys


def plan(db: sqlite3.Connection, sql: str) -> str:
    return " ".join(str(row[3]) for row in db.execute("EXPLAIN QUERY PLAN " + sql))


def main() -> int:
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'Alice', 'Alice@Example.com')")
    before = plan(db, "SELECT id FROM users WHERE LOWER(email)='alice@example.com'")
    assert "idx_email_lower" not in before, before
    db.execute("CREATE INDEX idx_email_lower ON users(LOWER(email))")
    after = plan(db, "SELECT id FROM users WHERE LOWER(email)='alice@example.com'")
    assert "idx_email_lower" in after and "INDEX" in after, after
    assert db.execute("SELECT id FROM users WHERE LOWER(email)='alice@example.com'").fetchone() == (1,)
    try:
        db.execute("CREATE INDEX bad ON users(random())")
        raise AssertionError("non-deterministic index expression was accepted")
    except sqlite3.OperationalError as exc:
        assert "deterministic" in str(exc).lower(), exc
    db.execute("CREATE TABLE doc(doc JSON, mtime AS (doc->>'mtime') STORED)")
    db.execute("CREATE INDEX doc_mtime ON doc(mtime)")
    db.execute("INSERT INTO doc(doc) VALUES ('{\"mtime\":12.5}')")
    assert db.execute("SELECT count(*) FROM doc WHERE mtime=12.5").fetchone()[0] == 1
    if tuple(map(int, sqlite3.sqlite_version.split("."))) >= (3, 53, 0):
        db.execute("REINDEX EXPRESSIONS")
        print("PASS: expression index used, non-deterministic refused, STORED column indexed, REINDEX EXPRESSIONS ran")
    else:
        print("SKIPPED REINDEX EXPRESSIONS (needs 3.53.0); other assertions passed on", sqlite3.sqlite_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
