#!/usr/bin/env python3
"""Chapter 28 lab: register a user-defined SQL function, extension-API style.

Python's sqlite3.create_function() mirrors what an extension does with
sqlite3_create_function(): it adds an application-defined function that SQL
statements can then call alongside the built-ins.
"""
from __future__ import annotations
import sqlite3
import sys


def rot13(text: str) -> str:
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr((ord(ch) - 97 + 13) % 26 + 97))
        elif "A" <= ch <= "Z":
            out.append(chr((ord(ch) - 65 + 13) % 26 + 65))
        else:
            out.append(ch)
    return "".join(out)


def main() -> int:
    db = sqlite3.connect(":memory:")
    db.create_function("rot13", 1, rot13, deterministic=True)
    got = db.execute("SELECT rot13('Hello')").fetchone()[0]
    assert got == "Uryyb", got
    mixed = db.execute("SELECT rot13('abc') || upper('d')").fetchone()[0]
    assert mixed == "nopD", mixed
    print("PASS: user-defined function registered and callable from SQL; sqlite3 %s"
          % sqlite3.sqlite_version)
    return 0


if __name__ == "__main__":
    sys.exit(main())
