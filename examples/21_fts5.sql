-- External-content FTS5 table with explicit synchronization triggers.
CREATE TABLE docs(
  id INTEGER PRIMARY KEY,
  title TEXT NOT NULL,
  body TEXT NOT NULL
);
INSERT INTO docs(title,body) VALUES
 ('Query planner','SQLite uses indexes and statistics to choose a query plan.'),
 ('WAL checkpoint','A checkpoint copies eligible WAL frames back into the database.'),
 ('Full text search','FTS5 stores tokens in an inverted index with segment B-trees.');

CREATE VIRTUAL TABLE docs_fts USING fts5(
  title, body,
  content='docs',
  content_rowid='id',
  tokenize='unicode61',
  prefix='2 3'
);
CREATE TRIGGER docs_ai AFTER INSERT ON docs BEGIN
  INSERT INTO docs_fts(rowid,title,body) VALUES(new.id,new.title,new.body);
END;
CREATE TRIGGER docs_ad AFTER DELETE ON docs BEGIN
  INSERT INTO docs_fts(docs_fts,rowid,title,body)
  VALUES('delete',old.id,old.title,old.body);
END;
CREATE TRIGGER docs_au AFTER UPDATE ON docs BEGIN
  INSERT INTO docs_fts(docs_fts,rowid,title,body)
  VALUES('delete',old.id,old.title,old.body);
  INSERT INTO docs_fts(rowid,title,body)
  VALUES(new.id,new.title,new.body);
END;

-- The base rows existed before the FTS table and triggers: build the index.
INSERT INTO docs_fts(docs_fts) VALUES('rebuild');

SELECT docs.id, docs.title, bm25(docs_fts) AS score
FROM docs_fts JOIN docs ON docs.id=docs_fts.rowid
WHERE docs_fts MATCH 'planner OR checkpoint'
ORDER BY rank;

SELECT snippet(docs_fts,1,'<b>','</b>','…',10)
FROM docs_fts WHERE docs_fts MATCH '"query planner"';

CREATE VIRTUAL TABLE docs_vocab USING fts5vocab(docs_fts,'instance');
SELECT term, doc, col, offset
FROM docs_vocab ORDER BY term, doc, offset;

-- Triggers keep future writes synchronized.
UPDATE docs SET body=body || ' Search ranking uses BM25.' WHERE id=1;
DELETE FROM docs WHERE id=2;
INSERT INTO docs(title,body) VALUES('Tokenization','unicode61 treats a run of token characters as one token.');

-- Optional maintenance operation; can be expensive on a large index.
INSERT INTO docs_fts(docs_fts) VALUES('optimize');
