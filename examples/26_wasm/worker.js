import sqlite3InitModule from '@sqlite.org/sqlite-wasm';

self.addEventListener('message', async (event) => {
  if (event.data?.type !== 'run') return;
  let db;
  try {
    const sqlite3 = await sqlite3InitModule();
    const useOpfs = typeof sqlite3.oo1.OpfsDb === 'function'
      && typeof navigator !== 'undefined'
      && typeof navigator.storage?.getDirectory === 'function'
      && self.crossOriginIsolated === true;
    db = useOpfs
      ? new sqlite3.oo1.OpfsDb('/sqlite-course-worker-demo.sqlite3', 'c')
      : new sqlite3.oo1.DB(':memory:');

    db.exec(`
      CREATE TABLE IF NOT EXISTS note(
        id INTEGER PRIMARY KEY,
        body TEXT NOT NULL
      );
      INSERT INTO note(id, body)
      VALUES(1, 'A transaction completed inside one Worker message')
      ON CONFLICT(id) DO UPDATE SET body=excluded.body;
    `);
    const rows = db.selectObjects('SELECT id, body FROM note ORDER BY id');
    self.postMessage({
      type: 'success',
      mode: useOpfs ? 'opfs' : 'memory fallback',
      version: sqlite3.version.libVersion,
      rows,
    });
  } catch (error) {
    self.postMessage({ type: 'error', error: String(error?.stack || error) });
  } finally {
    if (db) db.close();
  }
});
