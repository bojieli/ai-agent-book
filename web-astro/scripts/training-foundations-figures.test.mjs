import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutMdp,
  layoutRlInteraction,
  layoutNextToken,
  layoutSftToRl,
  layoutQUpdate,
  layoutTrainingAgents,
  layoutVlmTraining,
} from './training-foundations-figures.mjs';

const figures = {
  1: { layout: layoutRlInteraction, labels: 27 },
  2: { layout: layoutMdp, labels: 13 },
  4: { layout: layoutQUpdate, labels: 22 },
  7: { layout: layoutTrainingAgents, labels: 31 },
  8: { layout: layoutNextToken, labels: 21 },
  9: { layout: layoutVlmTraining, labels: 27 },
  11: { layout: layoutSftToRl, labels: 17 },
};
const normalize = (value) =>
  value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
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
    ...source.matchAll(/<div\b[^>]*data-label="(\d+)"[^>]*>([\s\S]*?)<\/div>/g),
  ].map((match) => ({ index: Number(match[1]), value: normalize(match[2]) }));

test('Chapter 8 training-foundation layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, { layout, labels: expectedCount }] of Object.entries(
      figures,
    )) {
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
        expectedCount,
        `${directory} Figure 8-${number}`,
      );

      const layoutSvg = layout(source);
      assert.match(layoutSvg, /viewBox="0 0 (1120|1320) \d+"/);
      assert.equal(
        (layoutSvg.match(/<foreignObject\b/g) || []).length,
        expectedCount,
      );
      assert.equal(
        (layoutSvg.match(/dir="auto"/g) || []).length,
        expectedCount,
      );

      for (const theme of ['light', 'dark']) {
        const actual = renderedLabels(styleFigure(layoutSvg, theme));
        assert.deepEqual(
          actual.map(({ index }) => index).sort((a, b) => a - b),
          Array.from({ length: expectedCount }, (_, index) => index),
          `${directory} Figure 8-${number} ${theme} label slots`,
        );
        assert.deepEqual(
          actual.map(({ value }) => value).sort(),
          [...expected].sort(),
          `${directory} Figure 8-${number} ${theme} labels`,
        );
      }
    }
});

test('Chapter 8 training-foundation layouts reject source structure drift', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-4.svg', import.meta.url),
    'utf8',
  );
  assert.throws(
    () => layoutQUpdate(source.replace(/<text\b[\s\S]*?<\/text>/, '')),
    /Figure 8-4 source structure changed/,
  );
});

test('English next-token illustration keeps the Chinese example and its original probabilities', () => {
  const read = (directory) =>
    readFileSync(
      new URL(`../../${directory}/images/fig8-8.svg`, import.meta.url),
      'utf8',
    );
  const english = read('book-en');
  const chinese = read('book');
  const expected = sourceLabels(english);
  const original = sourceLabels(chinese);
  for (const index of [0, 1, 2, 3, 4, 5, 6, 7, 11, 13, 15, 17])
    expected[index] = original[index];
  for (const theme of ['light', 'dark']) {
    const svg = styleFigure(
      layoutNextToken(english, { chineseExampleSource: chinese }),
      theme,
    );
    const actual = renderedLabels(svg).sort((a, b) => a.index - b.index);
    assert.deepEqual(
      actual.slice(0, 21).map(({ value }) => value),
      expected,
    );
    assert.match(
      actual[21].value,
      /An agent needs to perform tasks in a real environment/,
    );
    assert.deepEqual(
      [...svg.matchAll(/data-probability="([^"]+)"/g)].map((match) => match[1]),
      ['42', '28', '15', '15'],
    );
  }
});

test('English SFT heading allows the chapter’s conditional use of SFT before RL', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-11.svg', import.meta.url),
    'utf8',
  );
  const expected = sourceLabels(source);
  expected[12] = 'When is SFT needed before RL?';
  for (const theme of ['light', 'dark']) {
    const svg = styleFigure(layoutSftToRl(source, { english: true }), theme);
    assert.deepEqual(
      renderedLabels(svg)
        .sort((a, b) => a.index - b.index)
        .map(({ value }) => value),
      expected,
    );
  }
});
