#include <sqlite3.h>
#include <stdio.h>
#include <stdlib.h>

/*
** A deliberately small instrumentation VFS: it intercepts xOpen(), logs
** the operation, and delegates to the platform VFS. It does NOT encrypt data.
** All other VFS callbacks and sqlite3_file methods are inherited unchanged.
*/
static sqlite3_vfs g_parent_copy;
static sqlite3_vfs *g_parent = 0;
static unsigned g_open_count = 0;

static int trace_xOpen(sqlite3_vfs *pVfs, const char *zName,
                       sqlite3_file *pFile, int flags, int *pOutFlags){
  (void)pVfs;
  ++g_open_count;
  fprintf(stderr, "[course-trace-vfs] xOpen name=%s flags=0x%x\n",
          zName ? zName : "<temporary>", flags);
  return g_parent->xOpen(g_parent, zName, pFile, flags, pOutFlags);
}

static int register_trace_vfs(void){
  g_parent = sqlite3_vfs_find(0);
  if( !g_parent ) return SQLITE_ERROR;
  g_parent_copy = *g_parent;
  g_parent_copy.pNext = 0;
  g_parent_copy.zName = "course-trace-vfs";
  g_parent_copy.xOpen = trace_xOpen;
  return sqlite3_vfs_register(&g_parent_copy, 0);
}

int main(void){
  sqlite3 *db = 0;
  char *err = 0;
  int rc;
  const char *path = "course-vfs-demo.sqlite";
  remove(path);

  rc = sqlite3_initialize();
  if( rc!=SQLITE_OK ) return 1;
  rc = register_trace_vfs();
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "register VFS: %s\n", sqlite3_errstr(rc));
    return 2;
  }
  rc = sqlite3_open_v2(path, &db, SQLITE_OPEN_READWRITE|SQLITE_OPEN_CREATE,
                       "course-trace-vfs");
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "open: %s\n", db ? sqlite3_errmsg(db) : sqlite3_errstr(rc));
    if( db ) sqlite3_close(db);
    return 3;
  }
  rc = sqlite3_exec(db,
      "CREATE TABLE sample(id INTEGER PRIMARY KEY, value TEXT);"
      "INSERT INTO sample(value) VALUES('delegated VFS I/O');",
      0, 0, &err);
  if( rc!=SQLITE_OK ){
    fprintf(stderr, "SQL: %s\n", err ? err : sqlite3_errmsg(db));
    sqlite3_free(err);
    sqlite3_close(db);
    return 4;
  }
  sqlite3_stmt *stmt = 0;
  rc = sqlite3_prepare_v2(db, "SELECT value FROM sample WHERE id=1", -1,
                          &stmt, 0);
  if( rc==SQLITE_OK ) rc = sqlite3_step(stmt);
  if( rc!=SQLITE_ROW ){
    fprintf(stderr, "query: %s\n", sqlite3_errmsg(db));
    if( stmt ) sqlite3_finalize(stmt);
    sqlite3_close(db);
    return 5;
  }
  const unsigned char *value = sqlite3_column_text(stmt, 0);
  printf("query result: %s\n", value ? (const char*)value : "<NULL>");
  sqlite3_finalize(stmt);
  rc = sqlite3_close(db);
  if( rc!=SQLITE_OK ) return 6;
  printf("PASS: trace VFS observed %u xOpen call(s)\n", g_open_count);
  remove(path);
  return g_open_count ? 0 : 7;
}
