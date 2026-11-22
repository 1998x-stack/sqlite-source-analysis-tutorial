CREATE TABLE events(id INTEGER PRIMARY KEY, category TEXT, created_at INTEGER);
INSERT INTO events VALUES(1,'A',100),(2,'A',101),(3,'B',99),(4,'B',102);
CREATE INDEX idx_events_cat_time ON events(category,created_at);
ANALYZE;
EXPLAIN QUERY PLAN SELECT id FROM events WHERE category='A' AND created_at>=100 ORDER BY created_at;
SELECT id FROM events WHERE category='A' AND created_at>=100 ORDER BY created_at;
