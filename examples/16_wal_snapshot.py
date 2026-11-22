#!/usr/bin/env python3
"""WAL snapshot-isolation demonstration using two real file connections."""
import sqlite3
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temp:
    db_path = Path(temp) / "snapshot.sqlite"
    a = sqlite3.connect(db_path, timeout=0.3, isolation_level=None)
    b = sqlite3.connect(db_path, timeout=0.3, isolation_level=None)
    try:
        assert a.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        a.execute("CREATE TABLE t(n INTEGER)")
        a.execute("INSERT INTO t VALUES(1)")
        a.execute("BEGIN")
        assert a.execute("SELECT n FROM t").fetchone() == (1,)
        b.execute("UPDATE t SET n=2")
        assert a.execute("SELECT n FROM t").fetchone() == (1,), "reader snapshot moved unexpectedly"
        a.execute("ROLLBACK")
        assert a.execute("SELECT n FROM t").fetchone() == (2,)
        print("PASS: WAL old/new reader snapshot semantics verified")
    finally:
        b.close()
        a.close()
