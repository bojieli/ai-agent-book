import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutComputerUse } from './computer-use-layout.mjs';
const source = (dir, n) =>
  readFileSync(
    new URL(`../../${dir}/images/fig6-${n}.svg`, import.meta.url),
    'utf8',
  );
test('Computer-use layouts preserve every label and canvas bounds in 15 editions', () => {
  for (const { directory, dir } of Object.values(editions))
    for (const n of [11, 12, 13, 14]) {
      const s = source(directory, n),
        out = layoutComputerUse(s, n, { rtl: dir === 'rtl' });
      const labels = extractLabels(s, `6-${n}`, [
        { 11: 22, 12: 40, 13: 31, 14: 19 }[n],
      ]);
      const spans = [
        ...out.matchAll(/data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
      ].sort((a, b) => +a[1] - b[1]);
      assert.deepEqual(
        spans.map((m) => [+m[1], m[2]]),
        labels.map((v, i) => [i, v]),
        `${directory} 6-${n}`,
      );
      const height = +out.match(/viewBox="0 0 1000 ([\d.]+)"/)[1];
      for (const m of out.matchAll(
        /<foreignObject x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(+m[1] + +m[3] <= 1000);
        assert.ok(+m[2] + +m[4] <= height);
      }
      assert.doesNotMatch(out, /NaN|undefined|font-size:(?:[0-9]|1[0-3])px/);
      assert.equal(
        (out.match(/<g\b/g) || []).length,
        (out.match(/<\/g>/g) || []).length,
      );
    }
});
test('Perception retains the screenshot-inference-action loop with an external return route', () => {
  const out = layoutComputerUse(source('book-en', 11), 11);
  assert.equal((out.match(/marker-end=/g) || []).length, 3);
  for (const name of [
    'screenshot-inference',
    'inference-action',
    'action-next-screenshot',
  ])
    assert.ok(out.includes(`data-edge="${name}"`));
  assert.match(out, /M888 [\d.]+ H948 V[\d.]+ H888/);
});
test('Action-space and element-index diagrams keep five-stage workflows and four annotation IDs', () => {
  for (const n of [12, 13]) {
    const out = layoutComputerUse(source('book-en', n), n);
    assert.equal((out.match(/marker-end=/g) || []).length, 4);
  }
  const out = layoutComputerUse(source('book-en', 13), 13);
  assert.equal((out.match(/data-annotated-element=/g) || []).length, 4);
  for (const text of [
    'www.example.com',
    'submit-btn',
    'aria-label',
    'DOM/A11y',
  ])
    assert.ok(out.includes(text));
});
test('Coordinate scaling retains source values and both model-coordinate directions', () => {
  const out = layoutComputerUse(source('book-en', 14), 14);
  for (const name of ['screen-downscale', 'training-output', 'output-training'])
    assert.ok(out.includes(`data-edge="${name}"`));
  for (const text of [
    '2560',
    '1440',
    '1366',
    '768',
    '683',
    '384',
    '1280',
    '720',
    '1.87',
  ])
    assert.ok(out.includes(text));
  assert.equal((out.match(/marker-end=/g) || []).length, 3);
  assert.throws(
    () =>
      layoutComputerUse(
        source('book-en', 14).replace(/<text[\s\S]*?<\/text>/, ''),
        14,
      ),
    /source labels changed/,
  );
  assert.throws(() => layoutComputerUse('', 15), /Unsupported/);
});
