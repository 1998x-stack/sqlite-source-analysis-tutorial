#include <stdio.h>
#include <string.h>
#include <sqlite3.h>

int main(void) {
  sqlite3 *db = NULL;
  sqlite3_stmt *s = NULL;
  int rc = sqlite3_open(":memory:", &db);
  if (rc != SQLITE_OK) return 1;
  rc = sqlite3_exec(db, "CREATE TABLE t(id INTEGER PRIMARY KEY,name TEXT);"
                        "INSERT INTO t VALUES(1,'Ada'),(2,'Lin'),(3,'Grace');",
                    NULL, NULL, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 2; }
  rc = sqlite3_prepare_v2(db, "SELECT name FROM t WHERE id>?1 ORDER BY id", -1, &s, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 3; }
  sqlite3_bind_int(s, 1, 1);
  const char *names[] = {"Lin", "Grace"};
  int n = 0;
  while ((rc = sqlite3_step(s)) == SQLITE_ROW) {
    const unsigned char *v = sqlite3_column_text(s, 0);
    if (n >= 2 || !v || strcmp((const char *)v, names[n])) { sqlite3_finalize(s); sqlite3_close(db); return 4; }
    n++;
  }
  if (n != 2 || rc != SQLITE_DONE) { sqlite3_finalize(s); sqlite3_close(db); return 5; }
  if (sqlite3_reset(s) != SQLITE_OK) { sqlite3_finalize(s); sqlite3_close(db); return 6; }
  n = 0;
  while ((rc = sqlite3_step(s)) == SQLITE_ROW) n++;
  sqlite3_finalize(s);
  sqlite3_close(db);
  if (rc != SQLITE_DONE || n != 2) return 7;
  printf("PASS VDBE step/reset semantics: 2 rows on each execution\n");
  return 0;
}
