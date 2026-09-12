import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutEvolutionDeployment,
  layoutEvolutionLoop,
  layoutExperienceKnowledge,
} from './evolution-flow-figures.mjs';

const figures = {
  1: { layout: layoutEvolutionLoop, canvas: '1320 700' },
  4: { layout: layoutExperienceKnowledge, canvas: '1320 840' },
  5: { layout: layoutEvolutionDeployment, canvas: '1320 808' },
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
    ...source.matchAll(
      /<span\b[^>]*data-source-label="(\d+)"[^>]*>([\s\S]*?)<\/span>/g,
    ),
  ].map((match) => ({
    index: Number(match[1]),
    value: normalize(match[2]),
  }));

test('Chapter 9 evolution-flow layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, { layout, canvas }] of Object.entries(figures)) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig9-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = sourceLabels(source);
      const layoutSvg = layout(source);

      assert.match(
        layoutSvg,
        new RegExp(`viewBox="0 0 ${canvas}"`),
        `${directory} Figure 9-${number} canvas`,
      );
      assert.equal(
        (layoutSvg.match(/data-(?:source-)?label="\d+"/g) || []).length,
        expected.length,
        `${directory} Figure 9-${number} label count`,
      );
      assert.equal(
        (layoutSvg.match(/dir="auto"/g) || []).length,
        (layoutSvg.match(/<foreignObject\b/g) || []).length,
        `${directory} Figure 9-${number} text direction`,
      );

      for (const theme of ['light', 'dark']) {
        const actual = renderedLabels(styleFigure(layoutSvg, theme));
        assert.deepEqual(
          actual.map(({ index }) => index).sort((a, b) => a - b),
          Array.from({ length: expected.length }, (_, index) => index),
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

test('Chapter 9 evolution-flow layouts reject source structure drift', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const source = readFileSync(
      new URL(`../../book-en/images/fig9-${number}.svg`, import.meta.url),
      'utf8',
    );
    assert.throws(
      () => layout(source.replace(/<rect\b[^>]*\/>/, '')),
      new RegExp(`Figure 9-${number} source structure changed`),
    );
    assert.throws(
      () => layout(source.replace(/<text\b[\s\S]*?<\/text>/, '')),
      new RegExp(`Figure 9-${number} source structure changed`),
    );
  }
});

test('Figure 9-1 preserves five stages and the verified-release feedback edge', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig9-1.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutEvolutionLoop(source);
  assert.equal((layout.match(/data-stage="\d+"/g) || []).length, 5);
  assert.equal((layout.match(/data-edge="stage-\d-to-\d"/g) || []).length, 4);
  assert.match(layout, /data-edge="release-to-execute"/);
});

test('Figure 9-4 preserves the evidence pipeline and knowledge-revision loop', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig9-4.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutExperienceKnowledge(source);
  assert.equal((layout.match(/data-stage="\d+"/g) || []).length, 5);
  assert.equal((layout.match(/data-edge="stage-\d-to-\d"/g) || []).length, 4);
  assert.match(layout, /data-edge="retrieval-to-comparison"/);
});

test('Figure 9-5 keeps online execution and offline deployment as separate loops', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig9-5.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutEvolutionDeployment(source);
  assert.equal((layout.match(/data-online-stage="\d+"/g) || []).length, 3);
  assert.equal((layout.match(/data-offline-stage="\d+"/g) || []).length, 4);
  assert.match(layout, /data-edge="experience-to-diagnosis"/);
  assert.match(layout, /data-edge="release-to-stable"/);
  assert.match(layout, /data-edge="online-1-to-2"/);
  assert.match(layout, /data-edge="offline-3-to-4"/);
});

test('Evolution-flow layouts reserve wrapping text zones and arrow gutters', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const source = readFileSync(
      new URL(`../../book-en/images/fig9-${number}.svg`, import.meta.url),
      'utf8',
    );
    const result = layout(source);
    const sizes = [...result.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );
    assert.ok(sizes.length > 0);
    assert.ok(sizes.every((size) => size >= 17));
    assert.match(result, /overflow-wrap:anywhere/);
    assert.equal(
      (result.match(/marker-end="url\(#evolution-arrow\)"/g) || []).length,
      (result.match(/data-edge="[^"]+"/g) || []).length,
    );
  }
});
