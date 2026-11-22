#!/usr/bin/env python3
"""Exercise SQL syntax and deterministic examples with the stdlib SQLite binding."""
from __future__ import annotations
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    for chapter in ("01_sql_path.sql", "03_explain.sql", "08_lexical.sql", "09_parser_semantics.sql", "10_expressions.sql", "11_vdbe.sql", "15_rollback.sql", "18_planner.sql", "19_windows.sql"):
        conn = sqlite3.connect(":memory:")
        try:
            conn.executescript((ROOT / "examples" / chapter).read_text(encoding="utf-8"))
            count = conn.execute("SELECT COUNT(*) FROM sqlite_master").fetchone()[0]
            if chapter in ("01_sql_path.sql", "03_explain.sql", "10_expressions.sql", "11_vdbe.sql", "15_rollback.sql", "18_planner.sql", "19_windows.sql"):
                assert count > 0, (chapter, "schema missing")
            else:
                assert count == 0, (chapter, "expression-only script unexpectedly created schema")
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
        assert conn.execute("SELECT 5 IN (1, NULL), 5 NOT IN (1, NULL)").fetchone() == (None, None)
        assert conn.execute("SELECT 5 IN (), 5 NOT IN ()").fetchone() == (0, 1)
        assert conn.execute("SELECT 42 = '42'").fetchone() == (0,)
        assert conn.execute("SELECT CAST('123e+5' AS INTEGER)").fetchone() == (123,)
        assert conn.execute("SELECT 1 + 2 * 3, (1 + 2) * 3").fetchone() == (7, 9)
        print("PASS: 9 SQL scripts and deterministic query results; sqlite3", sqlite3.sqlite_version)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
