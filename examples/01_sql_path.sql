-- sqlite3 :memory: < examples/01_sql_path.sql
CREATE TABLE users(id INTEGER PRIMARY KEY,name TEXT);
INSERT INTO users VALUES(7,'Ada'),(9,'Lin');
SELECT name FROM users WHERE id=7;
EXPLAIN QUERY PLAN SELECT name FROM users WHERE id=7;
EXPLAIN SELECT name FROM users WHERE id=7;
SELECT sqlite_version();
