#!/usr/bin/env python3
"""Read the documented WAL header/frame fields while writer connection is live."""
import sqlite3
import struct
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as temp:
    path = Path(temp) / "wal-format.sqlite"
    db = sqlite3.connect(path, isolation_level=None)
    try:
        assert db.execute("PRAGMA journal_mode=WAL").fetchone()[0].lower() == "wal"
        db.execute("PRAGMA wal_autocheckpoint=0")
        db.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, note TEXT)")
        db.execute("INSERT INTO t VALUES(1, 'alpha')")
        db.execute("INSERT INTO t VALUES(2, 'beta')")
        wal = Path(str(path) + "-wal")
        assert wal.exists(), "active WAL not present"
        data = wal.read_bytes()
        assert len(data) >= 32 + 24
        magic, fmt, page_size = struct.unpack(">III", data[:12])
        assert magic in (0x377f0682, 0x377f0683), hex(magic)
        size = page_size if page_size != 1 else 65536
        assert size == db.execute("PRAGMA page_size").fetchone()[0]
        assert (len(data) - 32) % (24 + size) == 0
        frames = (len(data) - 32) // (24 + size)
        assert frames >= 1
        print(f"PASS: WAL magic=0x{magic:08x}, format={fmt}, page_size={size}, frames={frames}")
    finally:
        db.close()
