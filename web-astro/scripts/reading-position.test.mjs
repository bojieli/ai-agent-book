import test from 'node:test';
import assert from 'node:assert/strict';
import { parsePosition, positionKey } from '../src/lib/reading-position.ts';
const chapter = 'ai-agents-in-depth:en:chapter1';
const position = {
  version: 1,
  chapter,
  section: 'tools',
  sectionTitle: 'Tools',
  offset: 0.35,
  progress: 0.2,
};
test('reading positions are isolated by edition and validate stored data before navigation', () => {
  assert.deepEqual(parsePosition(JSON.stringify(position), chapter), position);
  const chinese = 'ai-agents-in-depth:zh-CN:chapter1';
  assert.notEqual(positionKey(chapter), positionKey(chinese));
  assert.equal(parsePosition(JSON.stringify(position), chinese), null);
  for (const raw of [null, '', 'broken', '{}', 'null'])
    assert.equal(parsePosition(raw, chapter), null);
  for (const patch of [
    { version: 2 },
    { offset: -1 },
    { offset: 1.1 },
    { progress: null },
    { progress: 1.01 },
    { section: 123 },
    { sectionTitle: [] },
  ]) {
    assert.equal(
      parsePosition(JSON.stringify({ ...position, ...patch }), chapter),
      null,
    );
  }
});
