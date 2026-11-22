import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutRetrievalStructure } from './retrieval-structure-layout.mjs';

const normalize = (value) =>
  value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

const sourceLabels = (source) =>
  [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map((match) =>
    normalize(match[1]),
  );

const renderedLabels = (source) =>
  [...source.matchAll(/<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g)]
    .map((match) => ({ index: Number(match[1]), value: normalize(match[2]) }))
    .sort((a, b) => a.index - b.index);

const readFigure = (directory, figure) =>
  readFileSync(
    new URL(`../../${directory}/images/fig3-${figure}.svg`, import.meta.url),
    'utf8',
  );

test('retrieval structure layouts preserve every localized source label once', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const edition of Object.values(editions))
    for (const figure of [9, 10, 11, 12]) {
      const source = readFigure(edition.directory, figure);
      const result = layoutRetrievalStructure(source, figure, {
        rtl: edition.dir === 'rtl',
      });
      const labels = sourceLabels(source);
      const rendered = renderedLabels(result);
      assert.deepEqual(
        rendered.map(({ index }) => index),
        labels.map((_, index) => index),
        `${edition.directory} figure 3-${figure} label indices`,
      );
      assert.deepEqual(
        rendered.map(({ value }) => value),
        labels,
        `${edition.directory} figure 3-${figure} label values`,
      );
      assert.match(result, /width="1000"/);
      assert.match(result, /viewBox="0 0 1000 /);
      assert.doesNotMatch(result, /<text\b|NaN|font-size:(?:[0-9]|1[0-3])px/);
    }
});

test('hybrid retrieval supports compact and extended source variants', () => {
  const compact = layoutRetrievalStructure(readFigure('book-ja', 9), 9);
  const extended = layoutRetrievalStructure(readFigure('book-en', 9), 9);
  const arabic = layoutRetrievalStructure(readFigure('book-ar', 9), 9, {
    rtl: true,
  });
  assert.match(compact, /data-variant="compact"/);
  assert.doesNotMatch(compact, /data-retrieval-stage="reranker"/);
  assert.match(extended, /data-variant="extended"/);
  assert.match(extended, /data-retrieval-stage="reranker"/);
  assert.match(extended, /data-retrieval-stage="final-ranking"/);
  assert.equal((compact.match(/data-source-label=/g) || []).length, 21);
  assert.equal((extended.match(/data-source-label=/g) || []).length, 25);
  assert.match(extended, /d="M200 [\d.]+ L232 [\d.]+"/);
  assert.match(extended, /d="M696 [\d.]+ L728 [\d.]+"/);
  for (const index of [1, 4, 6, 8, 13, 15, 17])
    assert.match(
      arabic,
      new RegExp(`dir="rtl"[^>]*><span data-source-label="${index}"`),
    );
  for (const index of [5, 7, 9, 14, 16, 18, 21])
    assert.match(
      arabic,
      new RegExp(`dir="ltr"[^>]*><span data-source-label="${index}"`),
    );
});

test('recursive abstraction keeps all ten tree connectors directionless', () => {
  for (const directory of ['book-en', 'book-es']) {
    const result = layoutRetrievalStructure(readFigure(directory, 10), 10);
    assert.match(result, /data-tree-connectors="directionless"/);
    assert.equal(
      (result.match(/<path d="M(?:575|340|625|853)/g) || []).length,
      10,
    );
    assert.equal((result.match(/marker-end=/g) || []).length, 0);
    assert.match(result, /data-cluster-index="0" data-chunk-columns="0 1 2"/);
    assert.match(result, /data-cluster-index="1" data-chunk-columns="3 4"/);
    assert.match(result, /data-cluster-index="2" data-chunk-columns="5 6"/);
    for (const [cluster, expectedCenters] of [
      [0, [226, 340, 454]],
      [1, [568, 682]],
      [2, [796, 910]],
    ]) {
      const group = result.match(
        new RegExp(
          `<g data-cluster-index="${cluster}"[^>]*>([\\s\\S]*?)<\\/g>`,
        ),
      );
      assert.ok(group);
      assert.deepEqual(
        [...group[1].matchAll(/L(\d+) [\d.]+" fill/g)].map((match) =>
          Number(match[1]),
        ),
        expectedCenters,
      );
    }
    assert.equal((result.match(/<foreignObject x="24"/g) || []).length, 2);
  }
});

test('agentic comparison leaves a readable loop gutter', () => {
  const result = layoutRetrievalStructure(readFigure('book-en', 12), 12);
  assert.match(result, /M896 [\d.]+ L968 [\d.]+ L968 [\d.]+ L896 [\d.]+/);
  assert.match(result, /x="898" y="[\d.]+" width="62" height="[\d.]+"/);
  assert.match(result, /font-size:14px/);
  assert.match(result, /font-size:16px/);
  assert.match(result, /font-size:18px/);
  assert.match(result, /font-size:20px/);
});

test('retrieval structure layouts reject unsupported figures and source drift', () => {
  assert.throws(
    () => layoutRetrievalStructure(readFigure('book-en', 9), 8),
    /Unsupported retrieval structure figure/,
  );
  assert.throws(
    () =>
      layoutRetrievalStructure(
        readFigure('book-en', 11).replace(/<line\b[^>]*\/>/, ''),
        11,
      ),
    /Figure 3-11 source structure changed/,
  );
});
