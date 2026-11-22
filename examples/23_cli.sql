-- 第23章实验：CLI 便捷命令背后的等价 SQL。
-- 这些查询可以在库接口里执行；而 .tables/.schema 等点命令只能由 CLI 程序解析。
CREATE TABLE tbl1(one VARCHAR(10), two SMALLINT);
CREATE INDEX idx_tbl1_one ON tbl1(one);
CREATE VIEW v_tbl1 AS SELECT one FROM tbl1;
INSERT INTO tbl1 VALUES ('a', 1), ('b', 2);

-- .tables 的等价查询
SELECT name FROM sqlite_schema
WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%'
ORDER BY 1;

-- .indexes 的等价查询（列出索引名）
SELECT name FROM sqlite_schema WHERE type = 'index' ORDER BY 1;

-- .schema 的等价查询（取回建表/建索引语句）
SELECT sql FROM sqlite_schema WHERE sql IS NOT NULL ORDER BY name;
