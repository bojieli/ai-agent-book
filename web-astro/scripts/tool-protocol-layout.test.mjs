import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutToolProtocol } from './tool-protocol-layout.mjs';
const source = (directory, n) =>
  readFileSync(
    new URL(`../../${directory}/images/fig4-${n}.svg`, import.meta.url),
    'utf8',
  );
test('Tool protocol layouts retain all localized labels and readable typography', () => {
  for (const { directory, dir } of Object.values(editions))
    for (const n of [1, 2]) {
      const input = source(directory, n);
      const svg = layoutToolProtocol(input, n, { rtl: dir === 'rtl' });
      const actual = [
        ...svg.matchAll(/<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
      ].sort((a, b) => Number(a[1]) - Number(b[1]));
      const expected = extractLabels(input, `4-${n}`, [n === 1 ? 18 : 26]);
      assert.deepEqual(
        actual.map((a) => Number(a[1])),
        expected.map((_, i) => i),
      );
      assert.deepEqual(
        actual.map((a) => a[2]),
        expected,
      );
      assert.doesNotMatch(svg, /NaN|undefined|font-size:(?:[0-9]|1[0-3])px/);
      const [, width, height] = svg.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
      for (const match of svg.matchAll(
        /<foreignObject x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(
          Number(match[1]) + Number(match[3]) <= Number(width),
          `${directory} 4-${n} horizontal bounds`,
        );
        assert.ok(
          Number(match[2]) + Number(match[4]) <= Number(height),
          `${directory} 4-${n} vertical bounds`,
        );
      }
    }
});
test('MCP sequence preserves three requests, three dashed responses, and two lifelines', () => {
  const svg = layoutToolProtocol(source('book-en', 1), 1);
  assert.equal((svg.match(/data-direction="request"/g) || []).length, 3);
  assert.equal((svg.match(/data-direction="response"/g) || []).length, 3);
  assert.equal((svg.match(/marker-end=/g) || []).length, 6);
  for (const [, d] of svg.matchAll(
    /data-direction="response"><path d="([^"]+)"/g,
  ))
    assert.match(d, /M840 [\d.]+ L296 [\d.]+/);
  assert.equal((svg.match(/stroke-dasharray=/g) || []).length, 5);
});
test('Hierarchical search retains server selection, tool order, and three arrows', () => {
  const svg = layoutToolProtocol(source('book-en', 2), 2);
  assert.equal((svg.match(/data-server=/g) || []).length, 5);
  assert.equal((svg.match(/data-tool=/g) || []).length, 5);
  assert.equal((svg.match(/marker-end=/g) || []).length, 3);
  assert.match(svg, /data-selected-server="0"><path d="M130 /);
});
test('Tool protocol source guards reject changed relationships', () => {
  assert.throws(
    () =>
      layoutToolProtocol(
        source('book-en', 1).replace(/<line\b[^>]*\/>/, ''),
        1,
      ),
    /relationships changed/,
  );
  assert.throws(
    () => layoutToolProtocol(source('book-en', 2), 3),
    /Unsupported/,
  );
});
