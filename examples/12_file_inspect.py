#!/usr/bin/env python3
"""Inspect a freshly created SQLite database file using only its documented file format."""
from __future__ import annotations
import sqlite3
import struct
import tempfile
from pathlib import Path

with tempfile.TemporaryDirectory() as d:
    path = Path(d) / "page-demo.sqlite"
    con = sqlite3.connect(path)
    assert con.execute("PRAGMA journal_mode=DELETE").fetchone()[0].lower() == "delete"
    con.execute("PRAGMA page_size=1024")
    con.execute("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, body BLOB)")
    con.execute("CREATE INDEX users_name ON users(name)")
    con.executemany("INSERT INTO users(name,body) VALUES(?,?)",
                    [(f"name-{i:04}", b"x" * 100) for i in range(280)])
    con.commit()
    objects = con.execute("SELECT name, rootpage FROM sqlite_schema WHERE name IN ('users','users_name')").fetchall()
    assert {name for name, _ in objects} == {"users", "users_name"}
    assert con.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
    sql_page_size = con.execute("PRAGMA page_size").fetchone()[0]
    page_count = con.execute("PRAGMA page_count").fetchone()[0]
    con.close()
    data = path.read_bytes()
    assert data[:16] == b"SQLite format 3\x00"
    page_field = struct.unpack_from(">H", data, 16)[0]
    page_size = 65536 if page_field == 1 else page_field
    assert page_size == sql_page_size == 1024
    assert len(data) == page_count * page_size
    def root_flag(rootpage: int) -> int:
        off = (rootpage - 1) * page_size + (100 if rootpage == 1 else 0)
        return data[off]
    for name, rootpage in objects:
        flag = root_flag(rootpage)
        valid = {0x05, 0x0D} if name == "users" else {0x02, 0x0A}
        assert flag in valid, (name, hex(flag))
        print(f"{name}: rootpage={rootpage}, type=0x{flag:02x}")
    print(f"PASS: page_size={page_size}, page_count={page_count}, integrity_check=ok, sqlite_version={sqlite3.sqlite_version}")
