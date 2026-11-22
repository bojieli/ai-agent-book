import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutReTool,
  layoutTrainingSystem,
} from './training-systems-figures.mjs';

const figures = {
  17: { layout: layoutReTool, labels: 35 },
  18: { layout: layoutTrainingSystem, labels: 54 },
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

test('Chapter 8 training-system layouts retain every localized label in both themes', () => {
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

test('Figure 8-17 preserves the execution graph and reported training results', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-17.svg', import.meta.url),
    'utf8',
  );
  const expected = sourceLabels(source);
  const layout = layoutReTool(source);

  assert.match(layout, /viewBox="0 0 1240 900"/);
  assert.equal((layout.match(/data-step="\d+"/g) || []).length, 5);
  assert.equal((layout.match(/data-edge="[^"]+"/g) || []).length, 6);
  assert.match(layout, /data-edge="code-to-sandbox"/);
  assert.match(layout, /data-edge="result-to-feedback"/);
  for (const index of [26, 27, 28, 29, 30, 31, 32, 33, 34]) {
    const rendered = renderedLabels(layout).find(
      (item) => item.index === index,
    );
    assert.equal(rendered?.value, expected[index], `training result ${index}`);
  }
});

test('Figure 8-18 preserves pipeline, tool groups, and rollout configuration', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig8-18.svg', import.meta.url),
    'utf8',
  );
  const expected = sourceLabels(source);
  const layout = layoutTrainingSystem(source);

  assert.match(layout, /viewBox="0 0 1320 1120"/);
  assert.equal((layout.match(/data-stage="\d+"/g) || []).length, 4);
  assert.equal((layout.match(/data-tool-group="\d+"/g) || []).length, 6);
  assert.equal((layout.match(/data-rollout-metric="\d+"/g) || []).length, 4);
  assert.equal((layout.match(/data-edge="stage-\d+-\d+"/g) || []).length, 3);
  for (const index of [43, 44, 46, 47, 49, 50, 52, 53]) {
    const rendered = renderedLabels(layout).find(
      (item) => item.index === index,
    );
    assert.equal(rendered?.value, expected[index], `rollout datum ${index}`);
  }
});

test('Training-system layouts reserve readable wrapped text zones', () => {
  const sources = [17, 18].map((number) =>
    readFileSync(
      new URL(`../../book-en/images/fig8-${number}.svg`, import.meta.url),
      'utf8',
    ),
  );
  const layouts = [layoutReTool(sources[0]), layoutTrainingSystem(sources[1])];

  for (const layout of layouts) {
    const fontSizes = [...layout.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );
    assert.ok(fontSizes.length > 0);
    assert.ok(fontSizes.every((size) => size >= 17));
    assert.doesNotMatch(
      layout,
      /<foreignObject[^>]*(?:width|height)="(?:[0-9]|1[0-5])"/,
    );
    assert.equal(
      (layout.match(/marker-end="url\(#training-system-arrow\)"/g) || [])
        .length,
      (layout.match(/data-edge="[^"]+"/g) || []).length,
    );
  }
});

test('Training-system layouts reject source structure drift', () => {
  const reward = readFileSync(
    new URL('../../book-en/images/fig8-17.svg', import.meta.url),
    'utf8',
  );
  const system = readFileSync(
    new URL('../../book-en/images/fig8-18.svg', import.meta.url),
    'utf8',
  );
  assert.throws(
    () => layoutReTool(reward.replace(/<path\b[^>]*\/>/, '')),
    /Figure 8-17 source structure changed/,
  );
  assert.throws(
    () => layoutTrainingSystem(system.replace(/<text\b[\s\S]*?<\/text>/, '')),
    /Figure 8-18 source structure changed/,
  );
});
