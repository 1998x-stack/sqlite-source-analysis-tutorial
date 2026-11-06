const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(root, 'index.html'), 'utf8');
const json = JSON.parse(fs.readFileSync(path.join(root, 'courses.json'), 'utf8'));
const match = html.match(/<script id="offline-course-data" type="application\\/json">([\\s\\S]*?)<\\/script>/);
test('offline catalog matches canonical JSON', () => {
  assert.ok(match, 'offline snapshot must exist');
  assert.deepEqual(JSON.parse(match[1]), json);
});
test('all course links target existing local HTML files', () => {
  assert.equal(json.chapterCount, json.chapters.length);
  for (const chapter of json.chapters) {
    assert.match(chapter.file, /^\\d{2}\\.html$/);
    assert.ok(fs.existsSync(path.join(root, chapter.file)), chapter.file);
  }
});
test('file protocol bypasses fetch, HTTP keeps fetch and errors', () => {
  assert.match(html, /window\\.location\\.protocol === 'file:'/);
  assert.match(html, /Promise\\.resolve\\(JSON\\.parse/);
  assert.match(html, /fetch\\('courses\\.json'\\)/);
  assert.match(html, /if \\(!res\\.ok\\) throw new Error/);
});
