#!/usr/bin/env python3
"""Warm-cache microbenchmark with result assertions and no timing threshold."""
import platform
import sqlite3
import statistics
import time

ROWS = 40000
REPEATS = 31

db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE event(id INTEGER PRIMARY KEY, device_id INTEGER, ts INTEGER, payload TEXT)")
db.execute("BEGIN")
db.executemany(
    "INSERT INTO event(device_id,ts,payload) VALUES(?,?,?)",
    ((i % 200, i * 10, f"payload-{i % 13}") for i in range(ROWS)),
)
db.commit()

query = "SELECT count(*) FROM event WHERE device_id=? AND ts>=? AND ts<?"
params = (42, 100000, 300000)

def sample():
    start = time.perf_counter()
    result = db.execute(query, params).fetchone()[0]
    return time.perf_counter() - start, result

for _ in range(5):
    sample()
baseline = [sample() for _ in range(REPEATS)]
expected = baseline[0][1]
assert all(row[1] == expected for row in baseline)

db.execute("CREATE INDEX event_device_ts ON event(device_id,ts)")
db.execute("PRAGMA optimize")
for _ in range(5):
    sample()
indexed = [sample() for _ in range(REPEATS)]
assert all(row[1] == expected for row in indexed)

def report(name, rows):
    values = sorted(x[0] for x in rows)
    p95 = values[min(len(values)-1, int(0.95 * len(values)))]
    print(f"{name}: median_ms={statistics.median(values)*1000:.4f} "
          f"p95_ms={p95*1000:.4f} result={rows[0][1]}")

print("SQLite:", sqlite3.sqlite_version)
print("Source id:", db.execute("SELECT sqlite_source_id()").fetchone()[0])
print("Platform:", platform.platform())
print("Rows:", ROWS, "repeats:", REPEATS, "cache: warm in-memory")
report("scan", baseline)
report("indexed", indexed)
print("PASS: result equality; timing is environment-specific, no threshold asserted")
