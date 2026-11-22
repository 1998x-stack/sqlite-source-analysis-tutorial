#include <sqlite3.h>
#include <stdio.h>
#include <string.h>

/* Read-only instructional vtab. Schema is SQL, rows are a private C array. */
typedef struct { sqlite3_vtab base; } ToyTable;
typedef struct { sqlite3_vtab_cursor base; int pos, end; } ToyCursor;
static const char *labels[] = {"one", "two", "three"};

static int toy_connect(sqlite3 *db, void *aux, int argc, const char *const*argv,
                       sqlite3_vtab **out, char **error) {
  (void)aux; (void)argc; (void)argv; (void)error;
  int rc=sqlite3_declare_vtab(db,"CREATE TABLE x(id INTEGER,label TEXT)");
  if(rc!=SQLITE_OK) return rc;
  ToyTable *tab=sqlite3_malloc64(sizeof(*tab));
  if(!tab) return SQLITE_NOMEM;
  memset(tab,0,sizeof(*tab));
  *out=(sqlite3_vtab*)tab;
  return SQLITE_OK;
}
static int toy_disconnect(sqlite3_vtab *tab) {
  sqlite3_free(tab); return SQLITE_OK;
}
static int toy_best(sqlite3_vtab *tab, sqlite3_index_info *info) {
  (void)tab;
  info->idxNum=0;
  info->estimatedCost=100.0;
  for(int i=0; i<info->nConstraint; ++i) {
    if(info->aConstraint[i].usable &&
       info->aConstraint[i].iColumn==0 &&
       info->aConstraint[i].op==SQLITE_INDEX_CONSTRAINT_EQ) {
      info->idxNum=1;
      info->aConstraintUsage[i].argvIndex=1;
      /* Keep omit=0: SQL will recheck the equality, including types/NULL. */
      info->estimatedCost=3.0;
      break;
    }
  }
  return SQLITE_OK;
}
static int toy_open(sqlite3_vtab *tab, sqlite3_vtab_cursor **out) {
  (void)tab;
  ToyCursor *c=sqlite3_malloc64(sizeof(*c));
  if(!c) return SQLITE_NOMEM;
  memset(c,0,sizeof(*c));
  *out=(sqlite3_vtab_cursor*)c;
  return SQLITE_OK;
}
static int toy_close(sqlite3_vtab_cursor *c) {
  sqlite3_free(c); return SQLITE_OK;
}
static int toy_filter(sqlite3_vtab_cursor *cursor, int idxNum, const char *idxStr,
                      int argc, sqlite3_value **argv) {
  (void)idxStr;
  ToyCursor *c=(ToyCursor*)cursor;
  if(idxNum==1 && argc==1) {
    int id=sqlite3_value_int(argv[0]);
    if(id>=1 && id<=3) { c->pos=id; c->end=id+1; }
    else { c->pos=4; c->end=4; }
  } else { c->pos=1; c->end=4; }
  return SQLITE_OK;
}
static int toy_next(sqlite3_vtab_cursor *cursor) {
  ((ToyCursor*)cursor)->pos++; return SQLITE_OK;
}
static int toy_eof(sqlite3_vtab_cursor *cursor) {
  ToyCursor *c=(ToyCursor*)cursor;
  return c->pos >= c->end;
}
static int toy_column(sqlite3_vtab_cursor *cursor,sqlite3_context *ctx,int col) {
  ToyCursor *c=(ToyCursor*)cursor;
  if(col==0) sqlite3_result_int(ctx,c->pos);
  else if(col==1 && c->pos>=1 && c->pos<=3)
    sqlite3_result_text(ctx,labels[c->pos-1],-1,SQLITE_STATIC);
  else sqlite3_result_null(ctx);
  return SQLITE_OK;
}
static int toy_rowid(sqlite3_vtab_cursor *cursor, sqlite3_int64 *rowid) {
  *rowid=((ToyCursor*)cursor)->pos; return SQLITE_OK;
}
static sqlite3_module toy_module = {
  .iVersion=1, .xCreate=toy_connect, .xConnect=toy_connect,
  .xBestIndex=toy_best, .xDisconnect=toy_disconnect, .xDestroy=toy_disconnect,
  .xOpen=toy_open, .xClose=toy_close, .xFilter=toy_filter,
  .xNext=toy_next, .xEof=toy_eof, .xColumn=toy_column, .xRowid=toy_rowid
};

int main(void) {
  sqlite3 *db=NULL; sqlite3_stmt *s=NULL;
  if(sqlite3_open(":memory:",&db)!=SQLITE_OK) return 1;
  int rc=sqlite3_create_module(db,"toyrows",&toy_module,NULL);
  if(rc==SQLITE_OK)
    rc=sqlite3_exec(db,"CREATE VIRTUAL TABLE vt USING toyrows",NULL,NULL,NULL);
  if(rc!=SQLITE_OK) { sqlite3_close(db); return 2; }
  rc=sqlite3_prepare_v2(db,"SELECT label FROM vt WHERE id=2",-1,&s,NULL);
  if(rc!=SQLITE_OK) { sqlite3_close(db); return 3; }
  rc=sqlite3_step(s);
  const unsigned char *result=rc==SQLITE_ROW?sqlite3_column_text(s,0):NULL;
  int match=result && strcmp((const char*)result,"two")==0;
  sqlite3_finalize(s);
  if(!match) { sqlite3_close(db); return 4; }
  rc=sqlite3_prepare_v2(db,"SELECT count(*) FROM vt",-1,&s,NULL);
  if(rc!=SQLITE_OK) { sqlite3_close(db); return 5; }
  rc=sqlite3_step(s);
  int n=rc==SQLITE_ROW?sqlite3_column_int(s,0):-1;
  sqlite3_finalize(s);
  sqlite3_close(db);
  if(n!=3) return 6;
  puts("PASS: virtual table scan=3, id=2 returns two");
  return 0;
}
