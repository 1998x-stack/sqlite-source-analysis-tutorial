.echo on
.eqp full
CREATE TABLE logs(id INTEGER PRIMARY KEY, category TEXT);
INSERT INTO logs VALUES(1,'warning'),(2,'info'),(3,'warning');
SELECT * FROM logs WHERE category='warning';
CREATE INDEX logs_category ON logs(category);
SELECT * FROM logs WHERE category='warning';
.eqp off
EXPLAIN QUERY PLAN SELECT * FROM logs WHERE category='warning';
