#!/usr/bin/env python3
"""Small application-level contract tests; not SQLite's own TCL/TH3 harness."""
import sqlite3
import unittest


class SqliteContracts(unittest.TestCase):
    def setUp(self):
        self.db = sqlite3.connect(":memory:")
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.executescript("""
          CREATE TABLE account(
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE
          );
          CREATE TABLE payment(
            id INTEGER PRIMARY KEY,
            account_id INTEGER NOT NULL REFERENCES account(id),
            amount_cents INTEGER NOT NULL CHECK(amount_cents >= 0)
          );
          INSERT INTO account VALUES(1,'ada@example.test');
        """)

    def tearDown(self):
        self.db.close()

    def test_foreign_key_and_check_contracts(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO payment(account_id,amount_cents) VALUES(999,100)"
            )
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO payment(account_id,amount_cents) VALUES(1,-1)"
            )

    def test_unique_contract(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO account(id,email) VALUES(2,'ada@example.test')"
            )

    def test_rollback_is_atomic(self):
        self.db.execute("BEGIN")
        self.db.execute(
            "INSERT INTO payment(account_id,amount_cents) VALUES(1,250)"
        )
        self.db.rollback()
        self.assertEqual(
            self.db.execute("SELECT count(*) FROM payment").fetchone()[0], 0
        )

    def test_expected_result(self):
        row = self.db.execute(
            "SELECT email FROM account WHERE id=?", (1,)
        ).fetchone()
        self.assertEqual(row, ("ada@example.test",))


if __name__ == "__main__":
    unittest.main(verbosity=2)
