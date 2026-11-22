#!/usr/bin/env python3
"""Observe query-plan changes without asserting unstable EXPLAIN prose."""
import sqlite3
db = sqlite3.connect(":memory:")
try:
    db.execute("CREATE TABLE events(id INTEGER PRIMARY KEY, category TEXT, created_at INTEGER, payload TEXT)")
    records = [(i, "A" if i % 4 == 0 else "B", i % 1000, "text") for i in range(3000)]
    db.executemany("INSERT INTO events VALUES (?,?,?,?)", records)
    sql = "SELECT COUNT(*), MIN(created_at) FROM events WHERE category='A' AND created_at>=100"
    baseline = db.execute(sql).fetchone()
    explain = "EXPLAIN QUERY PLAN " + sql
    before = [row[3] for row in db.execute(explain)]
    db.execute("CREATE INDEX idx_events_cat_time ON events(category,created_at)")
    db.execute("ANALYZE")
    after = [row[3] for row in db.execute(explain)]
    assert db.execute(sql).fetchone() == baseline
    assert baseline == (675, 100), baseline
    assert db.execute("SELECT COUNT(*) FROM sqlite_stat1 WHERE idx='idx_events_cat_time'").fetchone()[0] == 1
    assert db.execute("PRAGMA index_list(events)").fetchall()
    print("PLAN before:", before)
    print("PLAN after:", after)
    print("PASS: result unchanged; composite index/statistics created; sqlite3=", sqlite3.sqlite_version)
finally:
    db.close()
