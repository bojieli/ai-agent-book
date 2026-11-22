import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutCodingCore } from './coding-core-layout.mjs';
const source = (dir, n) =>
  readFileSync(
    new URL(`../../${dir}/images/fig5-${n}.svg`, import.meta.url),
    'utf8',
  );
test('Coding core layouts retain labels and bounds in every edition', () => {
  for (const { directory, dir } of Object.values(editions))
    for (const n of [1, 2]) {
      const s = source(directory, n),
        result = layoutCodingCore(s, n, { rtl: dir === 'rtl' });
      const labels = extractLabels(
        s,
        `5-${n}`,
        n === 1 ? [41] : [48, 53, 59, 60],
      );
      const rendered = [
        ...result.matchAll(/data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
      ].sort((a, b) => Number(a[1]) - Number(b[1]));
      assert.deepEqual(
        rendered.map((m) => [Number(m[1]), m[2]]),
        labels.map((s, i) => [i, s]),
        `${directory} 5-${n}`,
      );
      const height = Number(result.match(/viewBox="0 0 1000 ([\d.]+)"/)[1]);
      for (const m of result.matchAll(
        /<foreignObject x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(Number(m[1]) + Number(m[3]) <= 1000);
        assert.ok(Number(m[2]) + Number(m[4]) <= height);
      }
      assert.doesNotMatch(result, /NaN|undefined|font-size:(?:[0-9]|1[0-3])px/);
    }
});
test('Architecture retains its four directed connections and seven runtime tools', () => {
  const result = layoutCodingCore(source('book-en', 1), 1);
  for (const edge of [
    'gateway-runtime',
    'web-runtime',
    'runtime-browser',
    'runtime-filesystem',
  ])
    assert.ok(result.includes(`data-edge="${edge}"`));
  assert.equal((result.match(/marker-end=/g) || []).length, 4);
  assert.equal((result.match(/data-runtime-tool=/g) || []).length, 7);
  assert.equal((result.match(/data-memory-file=/g) || []).length, 5);
  const path = result.match(
    /data-edge="web-runtime"><path d="M200 ([\d.]+) L200 ([\d.]+)"/,
  );
  assert.ok(Number(path[1]) > Number(path[2]));
});
test('Workflow preserves five stages and their tool groups despite translated source positions', () => {
  for (const dir of ['book-en', 'book-vi', 'book-ja']) {
    const result = layoutCodingCore(source(dir, 2), 2);
    assert.equal((result.match(/data-stage=/g) || []).length, 5);
    assert.equal((result.match(/marker-end=/g) || []).length, 4);
    const stages = [
      ...result.matchAll(/<g data-stage="(\d+)">([\s\S]*?)<\/g>/g),
    ];
    assert.match(stages[0][2], /read_file/);
    assert.match(stages[0][2], /glob/);
    assert.match(stages[0][2], /write_file/);
    assert.match(stages[1][2], /ask_user/);
    assert.match(stages[1][2], /grep/);
    assert.match(stages[1][2], /read_file/);
    assert.match(stages[3][2], /pytest/);
  }
});
test('Coding core layouts fail on unknown source shapes', () => {
  assert.throws(
    () => layoutCodingCore(source('book-en', 1).replace(/<rect[^>]+>/, ''), 1),
    /structure changed/,
  );
  assert.throws(() => layoutCodingCore(source('book-en', 1), 3), /Unsupported/);
});
