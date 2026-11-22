import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutCreditAssignment,
  layoutTurnComparison,
} from './training-sequences-figures.mjs';

const figures = {
  14: {
    layout: layoutTurnComparison,
    labels: 26,
    viewBox: '0 0 1240 784',
  },
  15: {
    layout: layoutCreditAssignment,
    labels: 28,
    viewBox: '0 0 1320 742',
  },
};
const normalize = (value) =>
  value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
const sourceLabels = (source) =>
  [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) => normalize(match[1]));
const renderedLabels = (source) =>
  [
    ...source.matchAll(
      /<foreignObject\b[^>]*data-label="(\d+)"[^>]*>([\s\S]*?)<\/foreignObject>/g,
    ),
  ].map((match) => ({
    index: Number(match[1]),
    value: normalize(match[2]),
  }));

test('Chapter 8 sequence layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);

  for (const { directory } of Object.values(editions))
    for (const [number, figure] of Object.entries(figures)) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig8-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = sourceLabels(source);
      assert.equal(
        expected.length,
        figure.labels,
        `${directory} Figure 8-${number}`,
      );

      const layout = figure.layout(source);
      assert.match(layout, new RegExp(`viewBox="${figure.viewBox}"`));
      assert.equal(
        (layout.match(/<foreignObject\b/g) || []).length,
        figure.labels,
      );
      assert.equal(
        (layout.match(/<div dir="auto"/g) || []).length,
        figure.labels,
      );
      assert.equal(
        (layout.match(/overflow-wrap:anywhere/g) || []).length,
        figure.labels,
      );

      for (const theme of ['light', 'dark']) {
        const rendered = renderedLabels(styleFigure(layout, theme));
        assert.deepEqual(
          rendered.map(({ index }) => index).sort((a, b) => a - b),
          Array.from({ length: figure.labels }, (_, index) => index),
          `${directory} Figure 8-${number} ${theme} label slots`,
        );
        assert.deepEqual(
          rendered.map(({ value }) => value).sort(),
          [...expected].sort(),
          `${directory} Figure 8-${number} ${theme} labels`,
        );
      }
    }
});

test('Sequence layouts keep wrapping regions in bounds at readable sizes', () => {
  for (const [number, figure] of Object.entries(figures)) {
    const source = readFileSync(
      new URL(`../../book-en/images/fig8-${number}.svg`, import.meta.url),
      'utf8',
    );
    const layout = figure.layout(source);
    const [, , canvasWidth, canvasHeight] = figure.viewBox
      .split(' ')
      .map(Number);
    const fontSizes = [...layout.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );
    assert.ok(fontSizes.length > 0);
    assert.ok(
      fontSizes.every((size) => size >= 17),
      `Figure 8-${number} has undersized text`,
    );

    for (const match of layout.matchAll(
      /<foreignObject\b[^>]*x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
    )) {
      const [x, y, width, height] = match.slice(1).map(Number);
      assert.ok(x >= 0 && y >= 0, `Figure 8-${number} negative label origin`);
      assert.ok(
        x + width <= canvasWidth && y + height <= canvasHeight,
        `Figure 8-${number} label exceeds its viewBox`,
      );
    }
  }
});

test('Turn comparison preserves both modes and all four comparison dimensions', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-14.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutTurnComparison(source);

  assert.match(layout, /data-turn="single" data-labels="0-6"/);
  assert.match(layout, /data-turn="multi" data-labels="7-13"/);
  assert.deepEqual(
    [
      ...layout.matchAll(/data-comparison="([^"]+)" data-labels="([^"]+)"/g),
    ].map((match) => [match[1], match[2]]),
    [
      ['credit-assignment', '14 15 16'],
      ['state-management', '17 18 19'],
      ['reward-design', '20 21 22'],
      ['exploration-cost', '23 24 25'],
    ],
  );
});

test('Credit assignment preserves step fields, reward approaches, and roomy transitions', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-15.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutCreditAssignment(source);

  assert.deepEqual(
    [...layout.matchAll(/data-step="(\d+)" data-labels="([^"]+)"/g)].map(
      (match) => [match[1], match[2]],
    ),
    [
      ['1', '0 1 2 3'],
      ['2', '4 5 6 7'],
      ['3', '8 9 10 11'],
      ['4', '12 13 14 15'],
      ['5', '16 17 18 19'],
    ],
  );
  assert.match(layout, /data-credit-question="true" data-labels="20 21"/);
  assert.match(layout, /data-reward-approach="process" data-labels="22 23 24"/);
  assert.match(layout, /data-reward-approach="outcome" data-labels="25 26 27"/);

  const transitions = [
    ...layout.matchAll(
      /<line data-transition="([^"]+)" x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"[^>]*marker-end=/g,
    ),
  ];
  assert.deepEqual(
    transitions.map((match) => match[1]),
    ['1-2', '2-3', '3-4', '4-5'],
  );
  for (const transition of transitions) {
    assert.equal(Number(transition[3]), Number(transition[5]));
    assert.ok(
      Number(transition[4]) - Number(transition[2]) >= 50,
      `transition ${transition[1]} needs a clear arrow gutter`,
    );
  }
});

test('Sequence layout guards reject source structure drift', () => {
  const turnSource = readFileSync(
    new URL('../../book-en/images/fig8-14.svg', import.meta.url),
    'utf8',
  );
  const creditSource = readFileSync(
    new URL('../../book-en/images/fig8-15.svg', import.meta.url),
    'utf8',
  );

  assert.throws(
    () =>
      layoutTurnComparison(turnSource.replace(/<text\b[\s\S]*?<\/text>/, '')),
    /Figure 8-14 source structure changed/,
  );
  assert.throws(
    () => layoutCreditAssignment(creditSource.replace(/<line\b[^>]*\/>/, '')),
    /Figure 8-15 source structure changed/,
  );
});
