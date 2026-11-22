#include <stdio.h>
#include <string.h>
#include <sqlite3.h>
int main(void) {
  sqlite3 *db = 0;
  sqlite3_stmt *stmt = 0;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 1;
  const char *sql =
    "SELECT CASE WHEN ?1 IS NULL THEN 'missing' "
    "WHEN ?1 IN (1,2) THEN 'in' ELSE 'other' END;";
  if (sqlite3_prepare_v2(db, sql, -1, &stmt, 0) != SQLITE_OK) {
    sqlite3_close(db); return 2;
  }
  if (sqlite3_bind_int(stmt, 1, 2) != SQLITE_OK) {
    sqlite3_finalize(stmt); sqlite3_close(db); return 3;
  }
  int rc = sqlite3_step(stmt);
  const unsigned char *value = (rc == SQLITE_ROW)
    ? sqlite3_column_text(stmt, 0) : NULL;
  int ok = value && strcmp((const char*)value, "in") == 0;
  sqlite3_finalize(stmt);
  sqlite3_close(db);
  return ok ? 0 : 4;
}
