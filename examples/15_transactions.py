#!/usr/bin/env python3
"""Exercise SQLite transaction visibility and writer conflicts without simulating power loss."""
from __future__ import annotations
import sqlite3
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder) / "atomic.sqlite"
    conn1 = sqlite3.connect(path, timeout=0.1, isolation_level=None)
    conn2 = sqlite3.connect(path, timeout=0.1, isolation_level=None)
    try:
        mode = conn1.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower()
        assert mode == "delete", mode
        conn1.execute("PRAGMA synchronous=FULL")
        conn2.execute("PRAGMA synchronous=FULL")
        conn1.execute("CREATE TABLE t(n INTEGER)")
        conn1.execute("BEGIN IMMEDIATE")
        conn1.execute("INSERT INTO t VALUES(7)")
        assert conn2.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
        blocked = False
        try:
            conn2.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as err:
            blocked = "locked" in str(err).lower()
        assert blocked, "second writer was not rejected"
        print("PASS: BEGIN IMMEDIATE blocks second writer")
        conn1.execute("ROLLBACK")
        assert conn2.execute("SELECT COUNT(*) FROM t").fetchone()[0] == 0
        print("PASS: rollback leaves no committed row")
        conn2.execute("BEGIN IMMEDIATE")
        conn2.execute("INSERT INTO t VALUES(42)")
        conn2.execute("COMMIT")
    finally:
        conn2.close()
        conn1.close()
    with sqlite3.connect(path) as check:
        assert check.execute("SELECT n FROM t").fetchall() == [(42,)]
        assert check.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    print("PASS: committed row is visible after reconnect")
