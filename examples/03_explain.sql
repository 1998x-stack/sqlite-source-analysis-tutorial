-- sqlite3 :memory: < examples/03_explain.sql
CREATE TABLE logs(id INTEGER PRIMARY KEY, category TEXT, message TEXT);
INSERT INTO logs VALUES(1,'ok','alpha'),(2,'bad','beta');
EXPLAIN QUERY PLAN SELECT * FROM logs WHERE id=1;
EXPLAIN QUERY PLAN SELECT * FROM logs WHERE category='bad';
CREATE INDEX logs_category ON logs(category);
EXPLAIN QUERY PLAN SELECT * FROM logs WHERE category='bad';
EXPLAIN SELECT * FROM logs WHERE category='bad';
