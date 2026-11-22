#!/usr/bin/env python3
"""Chapter 25 lab: read key PRAGMAs and confirm a query uses an index."""
from __future__ import annotations
import sqlite3
import sys

VALID_PAGE = (512, 1024, 2048, 4096, 8192, 16384, 32768, 65536)


def main() -> int:
    db = sqlite3.connect(":memory:")
    cache = db.execute("PRAGMA cache_size").fetchone()[0]
    assert cache != 0, cache
    ps = db.execute("PRAGMA page_size").fetchone()[0]
    assert ps in VALID_PAGE, ps
    sync = db.execute("PRAGMA synchronous").fetchone()[0]
    assert sync in (0, 1, 2, 3), sync
    db.executescript("CREATE TABLE t(a INTEGER, b TEXT); CREATE INDEX i_t_a ON t(a);")
    plan = " ".join(str(row[3]) for row in db.execute("EXPLAIN QUERY PLAN SELECT b FROM t WHERE a=1"))
    assert "i_t_a" in plan, plan
    objs = db.execute("SELECT count(*) FROM sqlite_master").fetchone()[0]
    assert objs == 2, objs
    print("PASS: page_size=%d synchronous=%d cache_size=%d index_used=yes; sqlite3 %s"
          % (ps, sync, cache, sqlite3.sqlite_version))
    return 0


if __name__ == "__main__":
    sys.exit(main())
