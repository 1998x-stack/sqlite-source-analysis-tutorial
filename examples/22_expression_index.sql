-- Expression index matching is structural, not algebraic.
CREATE TABLE account_change(
  id INTEGER PRIMARY KEY,
  account_id INTEGER NOT NULL,
  amount INTEGER NOT NULL
);
INSERT INTO account_change(account_id,amount) VALUES
 (7,1200), (7,-900), (7,40), (9,-4000);
CREATE INDEX account_change_magnitude
ON account_change(account_id, abs(amount));

SELECT id, amount
FROM account_change
WHERE account_id=7 AND abs(amount)>=500
ORDER BY abs(amount) DESC;

CREATE TABLE t2(x INTEGER, y INTEGER);
INSERT INTO t2 VALUES(10,12), (5,17), (1,2);
CREATE INDEX t2xy ON t2(x+y);

-- The expression matches the index definition.
EXPLAIN QUERY PLAN SELECT * FROM t2 WHERE x+y=22;
SELECT count(*) FROM t2 WHERE x+y=22;

-- Algebraically equivalent, but not the same expression tree.
EXPLAIN QUERY PLAN SELECT * FROM t2 WHERE y+x=22;
SELECT count(*) FROM t2 WHERE y+x=22;

PRAGMA integrity_check;
