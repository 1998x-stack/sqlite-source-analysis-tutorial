# Portfolio Engineering Improvements

### 2026-11-06 14:18 UTC — ChatGPT Portfolio Iteration
- Run ID: portfolio-20261106T141836-sqlite
- Repo / Base SHA: 1998x-stack/sqlite-source-analysis-tutorial / 87c91b5ff7b21923110adc935c27cf3d338ec10f
- Historical context: default branch docs/improvements.md confirmed 404; no existing PR found.
- Product problem & expected user value: README promises direct index.html opening, but fetch('courses.json') can fail on file://, hiding all 28 lessons.
- Engineering diagnosis & evidence: index.html unconditionally fetches courses.json; file-origin restrictions can block it. HTTP must retain error reporting.
- Options & decision: offline failure (15), error recovery (9), schema checks (7); choose narrow offline fallback with canonical JSON snapshot.
- Changes: index.html embeds exact catalog JSON and uses it only for file://; tests/offline-catalog.test.cjs checks parity, links and protocol branches. No schema/API/dependency changes.
- Validation: C: connector JS static checks verified embedded JSON parity, protocol branch and 28 entries; D: Node test written but not run in a complete repository checkout; browser E2E not run. A/B: none.
- Security & regression review: only local static HTML and tests changed; no credentials or production data. HTTP retains fetch and status-error behavior.
- Risk & rollback: duplicated snapshot may drift; parity test detects it when run. Close Draft PR or revert branch commit.
- Follow-up: run node --test tests/offline-catalog.test.cjs and real Chrome file:// and HTTP E2E before merge.
- Commit: bc3364500d6e1f664948cdb22cce584ca9581849
- PR: https://github.com/1998x-stack/sqlite-source-analysis-tutorial/pull/1
