#!/usr/bin/env python3
"""Version-gated smoke test for SQL syntax introduced in SQLite 3.53.0."""
from __future__ import annotations

import sqlite3


def main() -> None:
    version = sqlite3.sqlite_version_info
    print("SQLite runtime:", sqlite3.sqlite_version)
    if version < (3, 53, 0):
        print("SKIP: REINDEX EXPRESSIONS requires SQLite 3.53.0 or later")
        return

    db = sqlite3.connect(":memory:")
    try:
        db.executescript("""
          CREATE TABLE measurements(
            id INTEGER PRIMARY KEY,
            raw_value TEXT NOT NULL
          );
          INSERT INTO measurements(raw_value) VALUES('1.25'),('2.5');
          CREATE INDEX measurements_numeric
            ON measurements(CAST(raw_value AS REAL));
        """)
        db.execute("REINDEX EXPRESSIONS")
        result = db.execute("PRAGMA integrity_check").fetchone()[0]
        assert result == "ok", result
        print("PASS: REINDEX EXPRESSIONS rebuilt expression indexes")
    finally:
        db.close()


if __name__ == "__main__":
    main()
