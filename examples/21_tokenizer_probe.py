#!/usr/bin/env python3
"""Inspect the built-in FTS5 unicode61 token stream with fts5vocab."""
import sqlite3

db = sqlite3.connect(":memory:")
try:
    db.executescript("""
      CREATE VIRTUAL TABLE f USING fts5(body, tokenize='unicode61');
      INSERT INTO f(rowid, body) VALUES(1, 'SQLite 数据库引擎 中文分词');
      CREATE VIRTUAL TABLE vocab USING fts5vocab(f, 'instance');
    """)
except sqlite3.OperationalError as exc:
    raise SystemExit(f"FTS5 is unavailable in this SQLite build: {exc}")

tokens = [row[0] for row in db.execute(
    "SELECT term FROM vocab ORDER BY offset"
)]
print("SQLite:", sqlite3.sqlite_version)
print("unicode61 tokens:", tokens)
# unicode61 groups a contiguous run of token characters; it does not
# apply a Chinese dictionary segmenter such as jieba.
assert "sqlite" in tokens
assert "数据库引擎" in tokens
assert "中文分词" in tokens
assert "数" not in tokens and "据" not in tokens
print("PASS: unicode61 token boundaries inspected")
