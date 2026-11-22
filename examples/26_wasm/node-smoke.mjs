import assert from 'node:assert/strict';
import sqlite3InitModule from '@sqlite.org/sqlite-wasm';

const sqlite3 = await sqlite3InitModule();
const db = new sqlite3.oo1.DB(':memory:');
try {
  db.exec('CREATE TABLE item(id INTEGER PRIMARY KEY, label TEXT NOT NULL)');
  db.exec({
    sql: 'INSERT INTO item(label) VALUES ($label)',
    bind: { $label: 'WASM memory smoke test' },
  });
  const rows = db.selectObjects('SELECT id, label FROM item ORDER BY id');
  assert.equal(rows.length, 1);
  assert.equal(rows[0].id, 1);
  assert.equal(rows[0].label, 'WASM memory smoke test');
  assert.equal(db.selectValue('SELECT count(*) FROM item'), 1);
  console.log(`PASS: SQLite WASM ${sqlite3.version.libVersion}; Node.js in-memory database`);
} finally {
  db.close();
}
