#include <stdio.h>
#include <sqlite3.h>

static void show(sqlite3 *db, int op, const char *name) {
  int current = 0, highwater = 0;
  int rc = sqlite3_db_status(db, op, &current, &highwater, 0);
  if (rc == SQLITE_OK) printf("%s: %d\n", name, highwater);
  else fprintf(stderr, "%s unsupported: %d\n", name, rc);
}

int main(void) {
  sqlite3 *db = NULL;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) {
    fprintf(stderr, "cannot open database\n");
    if (db) sqlite3_close(db);
    return 1;
  }
  char *err = NULL;
  int rc = sqlite3_exec(db,
    "CREATE TABLE t(x TEXT);"
    "INSERT INTO t VALUES('hello'),('world');"
    "SELECT * FROM t;", NULL, NULL, &err);
  if (rc != SQLITE_OK) {
    fprintf(stderr, "%s\n", err ? err : "SQL error");
    sqlite3_free(err);
    sqlite3_close(db);
    return 1;
  }
  show(db, SQLITE_DBSTATUS_LOOKASIDE_HIT, "hit");
  show(db, SQLITE_DBSTATUS_LOOKASIDE_MISS_SIZE, "miss_size");
  show(db, SQLITE_DBSTATUS_LOOKASIDE_MISS_FULL, "miss_full");
  sqlite3_close(db);
  return 0;
}
