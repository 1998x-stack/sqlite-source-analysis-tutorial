#include <sqlite3.h>
#include <stdint.h>
#include <stdio.h>
#include <limits.h>

static void doubled(sqlite3_context *ctx, int argc, sqlite3_value **argv) {
  (void)argc;
  if (sqlite3_value_type(argv[0]) == SQLITE_NULL) {
    sqlite3_result_null(ctx); return;
  }
  if (sqlite3_value_type(argv[0]) != SQLITE_INTEGER) {
    sqlite3_result_error(ctx, "integer argument required", -1); return;
  }
  sqlite3_int64 x = sqlite3_value_int64(argv[0]);
  if (x > INT64_MAX/2 || x < INT64_MIN/2) {
    sqlite3_result_error(ctx, "integer overflow", -1); return;
  }
  sqlite3_result_int64(ctx, 2*x);
}

typedef struct { sqlite3_int64 sum; int failed; } Acc;
static void square_step(sqlite3_context *ctx, int argc, sqlite3_value **argv) {
  (void)argc;
  if (sqlite3_value_type(argv[0]) == SQLITE_NULL) return;
  Acc *a = sqlite3_aggregate_context(ctx, sizeof(*a));
  if (!a) { sqlite3_result_error_nomem(ctx); return; }
  if (sqlite3_value_type(argv[0]) != SQLITE_INTEGER) {
    a->failed = 1; sqlite3_result_error(ctx,"integer only",-1); return;
  }
  sqlite3_int64 x = sqlite3_value_int64(argv[0]);
  /* Demo intentionally restricts input so x*x and sum cannot overflow. */
  if (x > 10000 || x < -10000 || a->sum > INT64_MAX - x*x) {
    a->failed = 1; sqlite3_result_error(ctx,"input/range overflow",-1); return;
  }
  a->sum += x*x;
}
static void square_final(sqlite3_context *ctx) {
  Acc *a = sqlite3_aggregate_context(ctx, 0);
  if (a && a->failed) { sqlite3_result_error(ctx,"aggregate failure",-1); return; }
  sqlite3_result_int64(ctx, a ? a->sum : 0);
}
int main(void) {
  sqlite3 *db = NULL;
  sqlite3_stmt *s = NULL;
  if (sqlite3_open(":memory:", &db) != SQLITE_OK) return 1;
  int rc = sqlite3_create_function_v2(db, "double_checked", 1,
    SQLITE_UTF8 | SQLITE_DETERMINISTIC, NULL, doubled, NULL, NULL, NULL);
  if (rc == SQLITE_OK) rc = sqlite3_create_function_v2(db, "sum_squares", 1,
    SQLITE_UTF8, NULL, NULL, square_step, square_final, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 2; }
  rc=sqlite3_prepare_v2(db,
    "WITH vals(x) AS (SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3) "
    "SELECT double_checked(7), sum_squares(x), double_checked(NULL) FROM vals",
    -1, &s, NULL);
  if (rc != SQLITE_OK) { sqlite3_close(db); return 3; }
  rc=sqlite3_step(s);
  int ok=(rc==SQLITE_ROW && sqlite3_column_int(s,0)==14 &&
          sqlite3_column_int(s,1)==14 && sqlite3_column_type(s,2)==SQLITE_NULL);
  sqlite3_finalize(s);
  sqlite3_close(db);
  if (!ok) return 4;
  puts("PASS: scalar and aggregate functions (14, 14, NULL)");
  return 0;
}
