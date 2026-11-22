#include <sqlite3.h>
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv){
  sqlite3 *db = 0;
  sqlite3_stmt *stmt = 0;
  char *err = 0;
  int rc;
  if( argc!=2 ){
    fprintf(stderr, "usage: %s ./course_ext.so\n", argv[0]);
    return 2;
  }
  rc = sqlite3_open(":memory:", &db);
  if( rc!=SQLITE_OK ) goto fail;
  /* Enable the C loading API without enabling SQL load_extension(). */
  rc = sqlite3_db_config(db, SQLITE_DBCONFIG_ENABLE_LOAD_EXTENSION, 1, 0);
  if( rc!=SQLITE_OK ) goto fail;
  rc = sqlite3_load_extension(db, argv[1], "sqlite3_course_init", &err);
  if( rc!=SQLITE_OK ) goto fail;
  rc = sqlite3_prepare_v2(db, "SELECT course_build()", -1, &stmt, 0);
  if( rc!=SQLITE_OK ) goto fail;
  rc = sqlite3_step(stmt);
  if( rc!=SQLITE_ROW ) goto fail;
  const unsigned char *value = sqlite3_column_text(stmt, 0);
  if( !value || strcmp((const char*)value, "sqlite-course-extension/1")!=0 ){
    rc = SQLITE_MISMATCH;
    goto fail;
  }
  printf("PASS: loaded extension returned %s\n", value);
  sqlite3_finalize(stmt);
  sqlite3_close(db);
  return 0;
fail:
  fprintf(stderr, "extension host failed: %s\n",
          err ? err : (db ? sqlite3_errmsg(db) : sqlite3_errstr(rc)));
  sqlite3_free(err);
  if( stmt ) sqlite3_finalize(stmt);
  if( db ) sqlite3_close(db);
  return 1;
}
