#include <stdio.h>
#include <sqlite3.h>
static int on_trace(unsigned type, void *ctx, void *p, void *x) {
  (void)x;
  int *rows = (int*)ctx;
  if (type == SQLITE_TRACE_STMT) {
    const char *sql = sqlite3_sql((sqlite3_stmt*)p);
    printf("STMT: %s\n", sql ? sql : "(internal)");
  } else if (type == SQLITE_TRACE_ROW) {
    ++*rows;
  }
  return 0;
}
int main(void) {
  sqlite3 *db = NULL;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 1;
  int rows = 0;
  sqlite3_trace_v2(db, SQLITE_TRACE_STMT | SQLITE_TRACE_ROW, on_trace, &rows);
  int rc = sqlite3_exec(db, "SELECT 1 UNION ALL SELECT 2;", NULL, NULL, NULL);
  printf("row events=%d\n", rows);
  sqlite3_close(db);
  return (rc == SQLITE_OK && rows == 2) ? 0 : 2;
}
