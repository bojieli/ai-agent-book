import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutEvolutionMethods,
  layoutTrajectoryVerification,
} from './evolution-methods-figures.mjs';

function normalize(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sourceLabels(source) {
  const matches = [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ];
  const labels = [];
  for (let index = 0; index < matches.length; index += 1) {
    let value = normalize(matches[index][1]);
    while (
      index + 1 < matches.length &&
      source.slice(
        matches[index].index + matches[index][0].length,
        matches[index + 1].index,
      ) === ''
    ) {
      index += 1;
      value = normalize(`${value} ${matches[index][1]}`);
    }
    labels.push(value);
  }
  return labels;
}

function renderedLabels(source) {
  return [
    ...source.matchAll(
      /<foreignObject\b[^>]*data-label="(\d+)"[^>]*>([\s\S]*?)<\/foreignObject>/g,
    ),
  ].map((match) => ({
    index: Number(match[1]),
    value: normalize(match[2]),
  }));
}

const figures = {
  2: { layout: layoutTrajectoryVerification, labels: 21 },
  3: { layout: layoutEvolutionMethods, labels: 18 },
};

test('Chapter 9 evolution-method layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, { layout, labels: expectedCount }] of Object.entries(
      figures,
    )) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig9-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = sourceLabels(source);
      assert.equal(
        expected.length,
        expectedCount,
        `${directory} Figure 9-${number}`,
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
          `${directory} Figure 9-${number} ${theme} label slots`,
        );
        assert.deepEqual(
          actual.map(({ value }) => value).sort(),
          [...expected].sort(),
          `${directory} Figure 9-${number} ${theme} labels`,
        );
      }
    }
});

test('Figure 9-2 keeps the three verification layers and evaluation flow explicit', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig9-2.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutTrajectoryVerification(source);

  assert.match(layout, /viewBox="0 0 1320 820"/);
  assert.match(layout, /data-verifier="rubric" data-layer-position="top"/);
  assert.match(layout, /data-verifier="process" data-layer-position="middle"/);
  assert.match(layout, /data-verifier="outcome" data-layer-position="bottom"/);
  assert.equal(
    (layout.match(/data-evaluation-field="[^"]+"/g) || []).length,
    4,
  );
  for (const index of [8, 9, 10, 11, 12, 13, 14, 15])
    assert.match(
      layout,
      new RegExp(`<foreignObject\\b[^>]*data-label="${index}"[^>]*width="398"`),
    );
  assert.equal((layout.match(/data-edge="[^"]+"/g) || []).length, 4);
  assert.match(layout, /data-edge="evaluation-to-diagnostic-signal"/);
  assert.ok(
    layout.indexOf('data-stage="structured-evaluation"') <
      layout.indexOf('data-stage="diagnostic-signal"'),
  );
});

test('Figure 9-3 presents four complementary update carriers without progression cues', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig9-3.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutEvolutionMethods(source);

  assert.match(layout, /viewBox="0 0 1320 900"/);
  assert.equal((layout.match(/data-carrier="[^"]+"/g) || []).length, 4);
  assert.equal(
    (layout.match(/data-relationship="complementary"/g) || []).length,
    4,
  );
  assert.match(layout, /data-relationship-note="complementary"/);
  assert.match(
    layout,
    /data-carrier-attribute="13" data-attached-to="knowledge"/,
  );
  assert.match(
    layout,
    /data-carrier-attribute="14" data-attached-to="parameters"/,
  );
  assert.doesNotMatch(layout, /data-step=|data-edge=|marker-end=/);
});

test('Chapter 9 evolution-method layouts reserve readable wrapping zones', () => {
  const verificationSource = readFileSync(
    new URL('../../book-en/images/fig9-2.svg', import.meta.url),
    'utf8',
  );
  const methodsSource = readFileSync(
    new URL('../../book-en/images/fig9-3.svg', import.meta.url),
    'utf8',
  );

  for (const layout of [
    layoutTrajectoryVerification(verificationSource),
    layoutEvolutionMethods(methodsSource),
  ]) {
    const fontSizes = [...layout.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );
    assert.ok(fontSizes.length > 0);
    assert.ok(fontSizes.every((size) => size >= 17));
    assert.doesNotMatch(layout, /<text\b/);
    assert.equal(
      (layout.match(/overflow-wrap:anywhere/g) || []).length,
      (layout.match(/<foreignObject\b/g) || []).length,
    );
  }
});

test('Chapter 9 evolution-method layouts reject source structure drift', () => {
  const verificationSource = readFileSync(
    new URL('../../book-en/images/fig9-2.svg', import.meta.url),
    'utf8',
  );
  const methodsSource = readFileSync(
    new URL('../../book-en/images/fig9-3.svg', import.meta.url),
    'utf8',
  );
  assert.throws(
    () =>
      layoutTrajectoryVerification(
        verificationSource.replace(/<path\b[^>]*\/>/, ''),
      ),
    /Figure 9-2 source structure changed/,
  );
  assert.throws(
    () =>
      layoutEvolutionMethods(
        methodsSource.replace('</svg>', '<rect width="1" height="1"/></svg>'),
      ),
    /Figure 9-3 source structure changed/,
  );
});
