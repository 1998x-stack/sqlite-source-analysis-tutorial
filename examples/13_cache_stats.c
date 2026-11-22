#include <stdio.h>
#include <sqlite3.h>
static int report(sqlite3 *db, int op, const char *name) {
  int current=0, highwater=0;
  int rc=sqlite3_db_status(db, op, &current, &highwater, 0);
  if (rc==SQLITE_OK) printf("%s: current=%d highwater=%d\n",name,current,highwater);
  return rc;
}
int main(void) {
  sqlite3 *db=NULL;
  if (sqlite3_open(":memory:",&db)!=SQLITE_OK) return 1;
  int rc=sqlite3_exec(db,
    "PRAGMA cache_size=64;"
    "CREATE TABLE t(id INTEGER PRIMARY KEY, body TEXT);"
    "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n WHERE x<250)"
    "INSERT INTO t SELECT x, printf('row-%04d',x) FROM n;"
    "SELECT sum(length(body)) FROM t;",NULL,NULL,NULL);
  if (rc!=SQLITE_OK) { sqlite3_close(db); return 2; }
  int ok=1;
  ok &= report(db,SQLITE_DBSTATUS_CACHE_USED,"cache_used")==SQLITE_OK;
  ok &= report(db,SQLITE_DBSTATUS_CACHE_HIT,"cache_hit")==SQLITE_OK;
  ok &= report(db,SQLITE_DBSTATUS_CACHE_MISS,"cache_miss")==SQLITE_OK;
  sqlite3_close(db);
  return ok?0:3;
}
