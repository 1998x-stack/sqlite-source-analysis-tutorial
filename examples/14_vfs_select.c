#include <stdio.h>
#include <sqlite3.h>
int main(int argc, char **argv) {
  if (argc!=2) { fprintf(stderr,"usage: %s /path/to/temporary.sqlite\n",argv[0]); return 1; }
  sqlite3_vfs *vfs=sqlite3_vfs_find(NULL);
  if (!vfs || !vfs->zName) return 2;
  sqlite3 *db=NULL;
  int rc=sqlite3_open_v2(argv[1],&db,SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE,vfs->zName);
  if (rc!=SQLITE_OK) { if(db) sqlite3_close(db); return 3; }
  rc=sqlite3_exec(db,
      "CREATE TABLE IF NOT EXISTS t(n INTEGER);"
      "INSERT INTO t VALUES(42);",NULL,NULL,NULL);
  int count=0;
  sqlite3_stmt *stmt=NULL;
  if (rc==SQLITE_OK) rc=sqlite3_prepare_v2(db,"SELECT COUNT(*) FROM t",-1,&stmt,NULL);
  if (rc==SQLITE_OK && sqlite3_step(stmt)==SQLITE_ROW) count=sqlite3_column_int(stmt,0);
  sqlite3_finalize(stmt);
  sqlite3_close(db);
  printf("VFS: %s, rows: %d\n",vfs->zName,count);
  remove(argv[1]);
  return count==1?0:4;
}
