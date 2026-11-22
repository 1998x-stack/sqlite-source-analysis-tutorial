#include <stdio.h>
#include <sqlite3.h>
int main(void) {
  sqlite3 *db = NULL;
  sqlite3_stmt *stmt = NULL;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 1;
  int rc = sqlite3_exec(db,
    "CREATE TABLE users(email TEXT UNIQUE);"
    "INSERT INTO users VALUES('x@example.com');", NULL, NULL, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 2; }
  rc = sqlite3_prepare_v2(db, "INSERT INTO users VALUES(?1)", -1, &stmt, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 3; }
  sqlite3_bind_text(stmt, 1, "x@example.com", -1, SQLITE_STATIC);
  rc = sqlite3_step(stmt);
  int extended = sqlite3_extended_errcode(db);
  printf("step=%d, primary=%d, extended=%d, message=%s\n",
         rc, extended & 0xff, extended, sqlite3_errmsg(db));
  sqlite3_finalize(stmt);
  sqlite3_close(db);
  return (extended & 0xff) == SQLITE_CONSTRAINT ? 0 : 4;
}
