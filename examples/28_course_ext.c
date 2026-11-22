#include <sqlite3ext.h>
SQLITE_EXTENSION_INIT1

static void course_build(sqlite3_context *ctx, int argc, sqlite3_value **argv){
  (void)argc;
  (void)argv;
  sqlite3_result_text(ctx, "sqlite-course-extension/1", -1, SQLITE_STATIC);
}

#ifdef _WIN32
__declspec(dllexport)
#endif
int sqlite3_course_init(sqlite3 *db, char **pzErrMsg,
                        const sqlite3_api_routines *pApi){
  (void)pzErrMsg;
  SQLITE_EXTENSION_INIT2(pApi);
  return sqlite3_create_function_v2(
      db, "course_build", 0,
      SQLITE_UTF8 | SQLITE_DETERMINISTIC | SQLITE_INNOCUOUS,
      0, course_build, 0, 0, 0);
}
