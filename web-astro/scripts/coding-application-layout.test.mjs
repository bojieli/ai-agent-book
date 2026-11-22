import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutCodingApplication } from './coding-application-layout.mjs';

const counts = { 8: [40], 9: [39, 40, 42], 10: [39], 11: [43] };

const source = (directory, figure) =>
  readFileSync(
    new URL(`../../${directory}/images/fig5-${figure}.svg`, import.meta.url),
    'utf8',
  );

const sourceLabels = (input) =>
  [...input.matchAll(/<text\b([^>]*?)(?:\/>|>([\s\S]*?)<\/text>)/g)].map(
    (match) => {
      const text = (match[2] ?? '')
        .replace(/<tspan\b[^>]*>/g, '')
        .replace(/<\/tspan>/g, ' ');
      return /Courier/.test(match[1])
        ? text.replace(/[\r\n]/g, '').replace(/\s+$/, '')
        : text.replace(/\s+/g, ' ').trim();
    },
  );

function assertBalancedXml(svg, label) {
  for (const tag of ['svg', 'g', 'foreignObject', 'div', 'span'])
    assert.equal(
      (svg.match(new RegExp(`<${tag}\\b`, 'g')) || []).length,
      (svg.match(new RegExp(`</${tag}>`, 'g')) || []).length,
      `${label} balanced ${tag}`,
    );
}

test('coding application layouts preserve labels, bounds, and typography in 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [8, 9, 10, 11]) {
      const input = source(directory, figure);
      const result = layoutCodingApplication(input, figure, {
        rtl: dir === 'rtl',
      });
      const expected = sourceLabels(input);
      assert.ok(
        counts[figure].includes(expected.length),
        `${directory} Figure 5-${figure} source label count`,
      );
      const actual = [
        ...result.matchAll(
          /<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g,
        ),
      ].sort((left, right) => Number(left[1]) - Number(right[1]));
      assert.deepEqual(
        actual.map((match) => Number(match[1])),
        expected.map((_, index) => index),
        `${directory} Figure 5-${figure} source label indices`,
      );
      assert.deepEqual(
        actual.map((match) => match[2]),
        expected,
        `${directory} Figure 5-${figure} source label values`,
      );
      assert.equal(
        input,
        source(directory, figure),
        'source remains unchanged',
      );
      assert.match(result, /width="1000"/);
      assert.match(result, /viewBox="0 0 1000 [\d.]+"/);
      assert.doesNotMatch(
        result,
        /<text\b|<tspan\b|NaN|undefined|font-size:(?:[0-9]|1[0-3])px/,
      );
      for (const size of [14, 16, 18, 20])
        assert.match(result, new RegExp(`font-size:${size}px`));
      assertBalancedXml(result, `${directory} Figure 5-${figure}`);

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

test('dynamic form keeps five stages, form fields, and four forward edges', () => {
  const result = layoutCodingApplication(source('book-en', 8), 8);
  assert.equal((result.match(/data-form-stage=/g) || []).length, 5);
  assert.equal((result.match(/data-form-field=/g) || []).length, 4);
  assert.equal((result.match(/data-edge=/g) || []).length, 4);
  assert.equal((result.match(/data-code-line="form-html:/g) || []).length, 10);
  assert.equal((result.match(/data-code-line="json:/g) || []).length, 4);
  assert.match(
    result,
    /data-body-line="comparison:4">[\s\S]*?<span data-source-label="35"><\/span>/,
  );
});

test('artifact comparison keeps five traditional and three artifact stages', () => {
  for (const directory of ['book-en', 'book', 'book-vi']) {
    const result = layoutCodingApplication(source(directory, 9), 9);
    assert.equal((result.match(/data-traditional-stage=/g) || []).length, 5);
    assert.equal((result.match(/data-artifact-stage=/g) || []).length, 3);
    assert.equal((result.match(/data-edge=/g) || []).length, 7);
    assert.match(
      result,
      /data-edge="frontend-to-visualization-data"[^>]*data-kind="data">[\s\S]*?stroke-dasharray=/,
    );
    assert.match(result, /white-space:pre-wrap/);
  }
});

test('bootstrapping keeps evolution and directed copy relationships without feedback', () => {
  const result = layoutCodingApplication(source('book-en', 10), 10);
  assert.equal((result.match(/data-evolution-stage=/g) || []).length, 4);
  assert.equal((result.match(/data-agent-version=/g) || []).length, 2);
  assert.equal((result.match(/data-edge=/g) || []).length, 4);
  assert.match(
    result,
    /data-edge="original-to-new-agent" data-from="original-agent" data-to="new-agent"/,
  );
  assert.doesNotMatch(result, /new-agent-to-original|feedback/);
});

test('meta-agent keeps requirement, four stages, generated artifacts, and comparison', () => {
  for (const directory of ['book-en', 'book-es']) {
    const result = layoutCodingApplication(source(directory, 11), 11);
    assert.equal((result.match(/data-meta-stage=/g) || []).length, 4);
    assert.equal((result.match(/data-generated-item=/g) || []).length, 4);
    assert.equal((result.match(/data-meta-comparison=/g) || []).length, 2);
    assert.equal((result.match(/data-edge=/g) || []).length, 5);
  }
});

test('coding application layouts reject unsupported figures and source drift', () => {
  assert.throws(
    () => layoutCodingApplication(source('book-en', 8), 7),
    /Unsupported coding application figure/,
  );
  for (const figure of [8, 9, 10, 11])
    assert.throws(
      () =>
        layoutCodingApplication(
          source('book-en', figure).replace(/<rect\b[^>]*\/>/, ''),
          figure,
        ),
      new RegExp(`Figure 5-${figure} source structure changed`),
    );
  assert.throws(
    () =>
      layoutCodingApplication(
        source('book-en', 11).replace(
          '</svg>',
          '<text x="0" y="0">unexpected</text></svg>',
        ),
        11,
      ),
    /Figure 5-11 source labels changed/,
  );
});
