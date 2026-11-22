#include <sqlite3.h>
int main(void) {
  sqlite3 *db = 0;
  if (sqlite3_complete("SELECT FROM t;") == 0) return 1;
  if (sqlite3_complete("SELECT 1") != 0) return 2;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 3;
  sqlite3_stmt *st = 0;
  int rc = sqlite3_prepare_v2(db, "SELECT FROM t;", -1, &st, 0);
  sqlite3_finalize(st);
  sqlite3_close(db);
  return (rc != SQLITE_OK) ? 0 : 4;
}
