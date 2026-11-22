import sqlite3InitModule from '@sqlite.org/sqlite-wasm';

self.addEventListener('message', async (event) => {
  if (event.data?.type !== 'run') return;
  let db;
  let inTransaction = false;
  try {
    const sqlite3 = await sqlite3InitModule();
    const useOpfs = typeof sqlite3.oo1.OpfsDb === 'function'
      && typeof navigator !== 'undefined'
      && typeof navigator.storage?.getDirectory === 'function'
      && self.crossOriginIsolated === true;
    db = useOpfs
      ? new sqlite3.oo1.OpfsDb('/sqlite-course-worker-demo.sqlite3', 'c')
      : new sqlite3.oo1.DB(':memory:');

    db.exec('BEGIN IMMEDIATE');
    inTransaction = true;
    db.exec(`
      CREATE TABLE IF NOT EXISTS run_counter(
        id INTEGER PRIMARY KEY CHECK(id=1),
        count INTEGER NOT NULL
      );
      INSERT INTO run_counter(id, count) VALUES(1, 1)
      ON CONFLICT(id) DO UPDATE SET count=run_counter.count+1;
    `);
    db.exec('COMMIT');
    inTransaction = false;
    const rows = db.selectObjects('SELECT id, count FROM run_counter');
    self.postMessage({
      type: 'success',
      mode: useOpfs ? 'opfs' : 'memory fallback',
      version: sqlite3.version.libVersion,
      rows,
    });
  } catch (error) {
    if (db && inTransaction) {
      try { db.exec('ROLLBACK'); } catch {}
    }
    self.postMessage({ type: 'error', error: String(error?.stack || error) });
  } finally {
    if (db) db.close();
  }
});
