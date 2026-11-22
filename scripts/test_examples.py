#!/usr/bin/env python3
"""Exercise SQL syntax and deterministic examples with the stdlib SQLite binding."""
from __future__ import annotations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    for chapter in ("01_sql_path.sql", "03_explain.sql"):
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript((ROOT / "examples" / chapter).read_text(encoding="utf-8"))
            count = conn.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0]
            assert count > 0, (chapter, "schema missing")
        finally:
            conn.close()
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript("""
        CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT);
        INSERT INTO users VALUES(7, 'Ada'), (9, 'Lin');
        """)
        assert conn.execute("SELECT name FROM users WHERE id=?", (7,)).fetchone() == ("Ada",)
        assert conn.execute("SELECT name FROM users WHERE id=?", (50,)).fetchone() is None
        assert conn.execute("SELECT 1+2").fetchone() == (3,)
        print("PASS: SQL scripts parse and deterministic query results are correct; sqlite3", sqlite3.sqlite_version)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
