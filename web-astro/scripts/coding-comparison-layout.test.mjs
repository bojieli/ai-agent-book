import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutCodingComparison } from './coding-comparison-layout.mjs';

const labelCounts = {
  3: [33],
  4: [52, 61, 65, 67, 68],
};

const sourceLabels = (input) =>
  [...input.matchAll(/<text\b[^>]*?(?:\/>|>([\s\S]*?)<\/text>)/g)].map(
    (match) =>
      (match[1] ?? '')
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim(),
  );

const source = (directory, figure) =>
  readFileSync(
    new URL(`../../${directory}/images/fig5-${figure}.svg`, import.meta.url),
    'utf8',
  );

test('coding comparisons preserve all labels and readable type in 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [3, 4]) {
      const input = source(directory, figure);
      const result = layoutCodingComparison(input, figure, {
        rtl: dir === 'rtl',
      });
      const expected = sourceLabels(input);
      assert.ok(labelCounts[figure].includes(expected.length));
      const actual = [
        ...result.matchAll(
          /<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g,
        ),
      ].sort((left, right) => Number(left[1]) - Number(right[1]));
      assert.deepEqual(
        actual.map((match) => Number(match[1])),
        expected.map((_, index) => index),
        `${directory} Figure 5-${figure} label indices`,
      );
      assert.deepEqual(
        actual.map((match) => match[2]),
        expected,
        `${directory} Figure 5-${figure} label values`,
      );
      assert.equal(
        input,
        source(directory, figure),
        'source SVG stays untouched',
      );
      assert.match(result, /width="1000"/);
      assert.match(result, /viewBox="0 0 1000 [\d.]+"/);
      assert.doesNotMatch(
        result,
        /<text\b|<tspan\b|NaN|undefined|font-size:(?:[0-9]|1[0-3])px/,
      );
      for (const size of [14, 16, 18, 20])
        assert.match(result, new RegExp(`font-size:${size}px`));
      assert.doesNotMatch(result, /marker-end=|data-edge=/);
      assert.equal(
        (result.match(/<g\b/g) || []).length,
        (result.match(/<\/g>/g) || []).length,
        `${directory} Figure 5-${figure} closes its SVG groups`,
      );

      const [, width, height] = result.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
      for (const match of result.matchAll(
        /<(?:foreignObject|rect)\b[^>]*x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(
          Number(match[1]) >= 0 &&
            Number(match[1]) + Number(match[3]) <= Number(width),
          `${directory} Figure 5-${figure} horizontal bounds`,
        );
        assert.ok(
          Number(match[2]) >= 0 &&
            Number(match[2]) + Number(match[4]) <= Number(height),
          `${directory} Figure 5-${figure} vertical bounds`,
        );
      }
    }
});

test('search comparison keeps four independent methods and ordered code rows', () => {
  const result = layoutCodingComparison(source('book-en', 3), 3);
  assert.equal((result.match(/data-search-method=/g) || []).length, 4);
  assert.equal((result.match(/data-code-kind="query"/g) || []).length, 4);
  assert.equal((result.match(/data-code-kind="result"/g) || []).length, 4);
  assert.equal((result.match(/data-search-code-line=/g) || []).length, 13);
  assert.deepEqual(
    [...result.matchAll(/data-search-code-line="(\d+):(\d+)"/g)].map(
      (match) => `${match[1]}:${match[2]}`,
    ),
    [
      '0:0',
      '0:1',
      '0:2',
      '1:0',
      '1:1',
      '1:2',
      '2:0',
      '2:1',
      '2:2',
      '3:0',
      '3:1',
      '3:2',
      '3:3',
    ],
  );
});

test('editing comparison keeps five methods, blank code rows, and adoption ranking', () => {
  const result = layoutCodingComparison(source('book-en', 4), 4);
  assert.equal((result.match(/data-editing-method=/g) || []).length, 5);
  assert.equal((result.match(/data-method-code=/g) || []).length, 26);
  assert.match(
    result,
    /data-method-code="2:3">[\s\S]*?<span data-source-label="27"><\/span>/,
  );
  assert.deepEqual(
    [
      ...result.matchAll(/data-adoption-rank="(\d+)" data-bar-width="(\d+)"/g),
    ].map((match) => [Number(match[1]), Number(match[2])]),
    [
      [1, 600],
      [2, 470],
      [3, 390],
      [4, 320],
      [5, 250],
    ],
  );
});

test('coding comparisons reject unsupported figures and source drift', () => {
  assert.throws(
    () => layoutCodingComparison(source('book-en', 3), 2),
    /Unsupported coding comparison figure/,
  );
  assert.throws(
    () =>
      layoutCodingComparison(
        source('book-en', 3).replace(/<rect\b[^>]*\/>/, ''),
        3,
      ),
    /Figure 5-3 source structure changed/,
  );
  assert.throws(
    () =>
      layoutCodingComparison(
        source('book-en', 4).replace(
          '</svg>',
          '<text x="0" y="0">unexpected</text><text x="0" y="0">second unexpected</text></svg>',
        ),
        4,
      ),
    /Figure 5-4 source labels changed/,
  );
});
