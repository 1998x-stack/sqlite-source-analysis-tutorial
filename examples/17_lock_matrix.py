#!/usr/bin/env python3
"""Exercise rollback writer exclusion and WAL stale-snapshot conflict."""
import sqlite3
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "locks.sqlite"
    a = sqlite3.connect(path, timeout=0.05, isolation_level=None)
    b = sqlite3.connect(path, timeout=0.05, isolation_level=None)
    try:
        assert a.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower() == "delete"
        a.execute("CREATE TABLE t(n INTEGER)")
        a.execute("INSERT INTO t VALUES(1)")
        a.execute("BEGIN IMMEDIATE")
        blocked = False
        try:
            b.execute("BEGIN IMMEDIATE")
        except sqlite3.OperationalError as exc:
            blocked = (getattr(exc, "sqlite_errorcode", sqlite3.SQLITE_BUSY) & 0xff) == sqlite3.SQLITE_BUSY
        assert blocked, "second writer unexpectedly acquired lock"
        a.execute("ROLLBACK")
        print("PASS: rollback second writer blocked")
        assert a.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        a.execute("BEGIN")
        assert a.execute("SELECT n FROM t").fetchone() == (1,)
        b.execute("UPDATE t SET n=2")
        code = None
        try:
            a.execute("UPDATE t SET n=3")
        except sqlite3.OperationalError as exc:
            code = getattr(exc, "sqlite_errorcode", None)
        assert code is not None and (code & 0xff) == sqlite3.SQLITE_BUSY, code
        if hasattr(sqlite3, "SQLITE_BUSY_SNAPSHOT"):
            assert code == sqlite3.SQLITE_BUSY_SNAPSHOT, (code, sqlite3.SQLITE_BUSY_SNAPSHOT)
        print("PASS: WAL stale read snapshot cannot be upgraded")
        a.execute("ROLLBACK")
        a.execute("BEGIN IMMEDIATE")
        a.execute("UPDATE t SET n=4")
        a.execute("COMMIT")
        assert b.execute("SELECT n FROM t").fetchone() == (4,)
        print("PASS: fresh transaction permits write")
    finally:
        b.close()
        a.close()
