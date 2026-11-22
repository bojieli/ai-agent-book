import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import {
  layoutVerificationSpectrum,
  layoutSimulationFidelity,
} from './evaluation-spectrum-figures.mjs';
import { layoutPairwise } from './pairwise-figure.mjs';

const figures = {
  4: layoutVerificationSpectrum,
  6: layoutPairwise,
  9: layoutSimulationFidelity,
};

const source = (directory, figure) =>
  readFileSync(
    new URL(`../../${directory}/images/fig7-${figure}.svg`, import.meta.url),
    'utf8',
  );

const sourceLabels = (input) =>
  [
    ...input
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) =>
    match[1]
      .replace(/<tspan\b[^>]*>/g, '')
      .replace(/<\/tspan>/g, ' ')
      .replace(/\s+/g, ' ')
      .trim(),
  );

const renderedLabels = (result) =>
  [
    ...result.matchAll(/<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
  ].sort((left, right) => Number(left[1]) - Number(right[1]));

function assertBounds(result, context) {
  const [, width, height] = result.match(/viewBox="0 0 ([\d.]+) ([\d.]+)"/);
  assert.equal(Number(width), 1000, `${context} canvas width`);
  for (const match of result.matchAll(
    /<(?:foreignObject|rect)\b[^>]*x="(-?[\d.]+)" y="(-?[\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
  )) {
    const [, x, y, itemWidth, itemHeight] = match.map(Number);
    assert.ok(x >= 0 && x + itemWidth <= Number(width), `${context} x bounds`);
    assert.ok(
      y >= 0 && y + itemHeight <= Number(height),
      `${context} y bounds`,
    );
  }
}

test('comparison layouts preserve all labels, readable type, and bounds in 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const [figure, layout] of Object.entries(figures)) {
      const input = source(directory, figure);
      const expected = sourceLabels(input);
      const result = layout(input, { rtl: dir === 'rtl' });
      const actual = renderedLabels(result);
      assert.deepEqual(
        actual.map((match) => Number(match[1])),
        expected.map((_, index) => index),
        `${directory} Figure 7-${figure} label indices`,
      );
      assert.deepEqual(
        actual.map((match) => match[2]),
        expected,
        `${directory} Figure 7-${figure} label values`,
      );
      assert.equal(
        input,
        source(directory, figure),
        'source SVG stays untouched',
      );
      assert.match(result, /width="1000"/);
      assert.doesNotMatch(
        result,
        /<text\b|<tspan\b|NaN|undefined|font-size:(?:[0-9]|1[0-3])px/,
      );
      const fontSizes = [...result.matchAll(/font-size:(\d+)px/g)].map(
        (match) => Number(match[1]),
      );
      assert.ok(fontSizes.length > 0);
      assert.ok(
        fontSizes.every((size) => [14, 16, 18, 20].includes(size)),
        `${directory} Figure 7-${figure} typography scale`,
      );
      if (dir === 'rtl') assert.match(result, /dir="rtl"/);
      assert.doesNotMatch(
        result,
        /data-[a-z-]+>/,
        'SVG attributes require explicit values',
      );
      assertBounds(result, `${directory} Figure 7-${figure}`);
    }
});

test('verification spectrum preserves stage order and eight-pixel arrow gutters', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const result = layoutVerificationSpectrum(source(directory, 4), {
      rtl: dir === 'rtl',
    });
    const cards = [
      ...result.matchAll(
        /data-spectrum-stage="(\d+)"><rect x="([\d.]+)"[^>]*?width="([\d.]+)"/g,
      ),
    ].map((match) => ({
      stage: Number(match[1]),
      x: Number(match[2]),
      width: Number(match[3]),
    }));
    assert.deepEqual(
      cards.map(({ stage }) => stage),
      [0, 1, 2, 3],
      `${directory} stages`,
    );
    const edges = [
      ...result.matchAll(
        /data-spectrum-edge="(\d)-(\d)" data-start-x="([\d.]+)" data-end-x="([\d.]+)"/g,
      ),
    ];
    assert.equal(edges.length, 3, `${directory} spectrum edges`);
    edges.forEach((edge, index) => {
      assert.equal(Number(edge[1]), index);
      assert.equal(Number(edge[2]), index + 1);
      assert.equal(Number(edge[3]), cards[index].x + cards[index].width + 8);
      assert.equal(Number(edge[4]), cards[index + 1].x - 8);
    });
  }
});

test('pairwise layout preserves the formula, ratings, row order, and edges', () => {
  const expectedEdges = [
    'model-a-to-decision',
    'model-b-to-decision',
    'comparison-to-decision',
    'decision-to-elo',
    'elo-to-leaderboard',
  ];
  for (const { directory, dir } of Object.values(editions)) {
    const input = source(directory, 6);
    const labels = sourceLabels(input);
    const result = layoutPairwise(input, { rtl: dir === 'rtl' });
    const rendered = new Map(
      renderedLabels(result).map((match) => [Number(match[1]), match[2]]),
    );
    assert.equal(rendered.get(10), labels[10], `${directory} Elo formula`);
    assert.deepEqual(
      [18, 22, 26, 30, 34, 38].map((id) => rendered.get(id)),
      [18, 22, 26, 30, 34, 38].map((id) => labels[id]),
      `${directory} Elo ratings`,
    );
    assert.deepEqual(
      [...result.matchAll(/data-leaderboard-row="(\d+)"/g)].map((match) =>
        Number(match[1]),
      ),
      [1, 2, 3, 4, 5, 6],
      `${directory} leaderboard order`,
    );
    assert.deepEqual(
      [...result.matchAll(/data-pairwise-edge="([^"]+)"/g)].map(
        (match) => match[1],
      ),
      expectedEdges,
      `${directory} comparison relationships`,
    );
  }
});

test('simulation chart keeps all six source positions and the exact trend line', () => {
  const points = (input) =>
    [...input.matchAll(/<circle\b[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"/g)].map(
      (match) => [Number(match[1]), Number(match[2])],
    );
  for (const { directory, dir } of Object.values(editions)) {
    const input = source(directory, 9);
    const result = layoutSimulationFidelity(input, { rtl: dir === 'rtl' });
    assert.deepEqual(
      points(result),
      points(input),
      `${directory} chart points`,
    );
    const trend = input.match(
      /<line\b[^>]*stroke-dasharray="8,4"[^>]*\/\s*>/,
    )[0];
    assert.ok(result.includes(trend), `${directory} trend geometry`);
    assert.deepEqual(
      [...result.matchAll(/data-fidelity-key="(\d+)"/g)].map((match) =>
        Number(match[1]),
      ),
      [1, 2, 3, 4, 5, 6],
      `${directory} chart key order`,
    );
  }
});

test('comparison layouts reject unreviewed source variants', () => {
  assert.throws(
    () =>
      layoutVerificationSpectrum(
        source('book-en', 4).replace(/<rect\b[^>]*\/>/, ''),
      ),
    /Figure 7-4 source structure changed/,
  );
  assert.throws(
    () => layoutPairwise(source('book-en', 6).replace(/<line\b[^>]*\/>/, '')),
    /Figure 7-6 source structure changed/,
  );
  assert.throws(
    () =>
      layoutSimulationFidelity(
        source('book-en', 9).replace(/<circle\b[^>]*\/>/, ''),
      ),
    /Figure 7-9 source structure changed/,
  );
});
