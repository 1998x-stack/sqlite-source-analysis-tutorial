-- Run with: sqlite3 :memory: < examples/23_cli_workflow.sql
.headers on
.mode box
CREATE TABLE task(
  id INTEGER PRIMARY KEY,
  owner TEXT NOT NULL,
  state TEXT NOT NULL
);
INSERT INTO task(owner,state) VALUES
  ('Ada','open'), ('Lin','done'), ('Mira','open');
CREATE INDEX task_state_owner ON task(state,owner);

.eqp on
SELECT owner FROM task WHERE state='open' ORDER BY owner;
.eqp off
.schema task
.mode json
SELECT id,owner,state FROM task ORDER BY id;
