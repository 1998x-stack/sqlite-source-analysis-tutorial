#include <sqlite3.h>
#include <stdio.h>

static int exec_sql(sqlite3 *db, const char *sql){
  char *err = 0;
  int rc = sqlite3_exec(db, sql, 0, 0, &err);
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL error: %s\n", err ? err : sqlite3_errmsg(db));
    sqlite3_free(err);
  }
  return rc;
}

static int measure(sqlite3 *db, const char *label){
  sqlite3_stmt *stmt = 0;
  sqlite3_int64 count = -1;
  int rc = sqlite3_prepare_v2(db,
    "SELECT count(*) FROM event "
    "WHERE device_id=42 AND ts>=100000 AND ts<300000",
    -1, &stmt, 0);
  if( rc!=SQLITE_OK ) return rc;
  rc = sqlite3_step(stmt);
  if( rc==SQLITE_ROW ){
    count = sqlite3_column_int64(stmt, 0);
    rc = SQLITE_OK;
  }
  int fullscan = sqlite3_stmt_status(stmt, SQLITE_STMTSTATUS_FULLSCAN_STEP, 0);
  int vmstep = sqlite3_stmt_status(stmt, SQLITE_STMTSTATUS_VM_STEP, 0);
  int sort = sqlite3_stmt_status(stmt, SQLITE_STMTSTATUS_SORT, 0);
  printf("%s: rows=%lld fullscan_steps=%d vm_steps=%d sorts=%d\n",
         label, (long long)count, fullscan, vmstep, sort);
  sqlite3_finalize(stmt);
  if( rc!=SQLITE_OK ) return rc;
  return fullscan;
}

int main(void){
  sqlite3 *db = 0;
  if( sqlite3_open(":memory:", &db)!=SQLITE_OK ) return 1;
  printf("SQLite %s\nSource %s\n",
         sqlite3_libversion(), sqlite3_sourceid());
  if( exec_sql(db,
      "CREATE TABLE event(id INTEGER PRIMARY KEY,device_id INTEGER,ts INTEGER,payload TEXT);"
      "BEGIN;")!=SQLITE_OK ) return 2;

  sqlite3_stmt *ins = 0;
  int rc = sqlite3_prepare_v2(db,
    "INSERT INTO event(device_id,ts,payload) VALUES(?1,?2,'x')",
    -1, &ins, 0);
  if( rc!=SQLITE_OK ) return 3;
  for(int i=0; i<50000; i++){
    sqlite3_bind_int(ins,1,i%100);
    sqlite3_bind_int(ins,2,i*10);
    rc=sqlite3_step(ins);
    if( rc!=SQLITE_DONE ) return 4;
    sqlite3_reset(ins);
    sqlite3_clear_bindings(ins);
  }
  sqlite3_finalize(ins);
  if( exec_sql(db,"COMMIT;")!=SQLITE_OK ) return 5;

  int before = measure(db,"before index");
  if( before<=0 ){
    fprintf(stderr,"expected a full scan before index\n");
    return 6;
  }
  if( exec_sql(db,
      "CREATE INDEX event_device_ts ON event(device_id,ts);"
      "PRAGMA optimize;")!=SQLITE_OK ) return 7;
  int after = measure(db,"after index");
  if( after!=0 ){
    fprintf(stderr,"expected no full scan after covering range index\n");
    return 8;
  }
  sqlite3_close(db);
  puts("PASS: statement counters observed full-scan reduction");
  return 0;
}
