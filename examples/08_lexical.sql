SELECT 'a''b' AS quoted_string;
SELECT 1 /* skipped inside SQL */ + 2 AS result;
SELECT "select" FROM (SELECT 7 AS "select");
SELECT typeof(3.14) AS numeric_type;
