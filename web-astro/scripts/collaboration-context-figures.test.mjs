import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutManagerSequentialCoordination,
  layoutProposerReviewerLoop,
  layoutSharedContextComparison,
  layoutVirtualFilesystemMounts,
} from './collaboration-context-figures.mjs';

function normalize(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sourceLabels(source) {
  return [
    ...source
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ].map((match) => normalize(match[1]));
}

function renderedLabels(source) {
  return [
    ...source.matchAll(
      /<foreignObject\b[^>]*data-source-label="(\d+)"[^>]*>([\s\S]*?)<\/foreignObject>/g,
    ),
  ].map((match) => ({
    index: Number(match[1]),
    value: normalize(match[2]),
  }));
}

function readFigure(directory, number) {
  return readFileSync(
    new URL(`../../${directory}/images/fig10-${number}.svg`, import.meta.url),
    'utf8',
  );
}

function edges(source) {
  return [
    ...source.matchAll(
      /<path data-edge="([^"]+)" data-from="([^"]+)" data-to="([^"]+)" data-route="gutter" d="([^"]+)"[^>]*marker-end="url\(#collaboration-context-arrow\)"\/>/g,
    ),
  ].map((match) => ({
    name: match[1],
    from: match[2],
    to: match[3],
    d: match[4],
  }));
}

const figures = {
  1: { layout: layoutSharedContextComparison, labels: 37 },
  2: { layout: layoutVirtualFilesystemMounts, labels: 35 },
  3: { layout: layoutProposerReviewerLoop, labels: 37 },
  4: { layout: layoutManagerSequentialCoordination, labels: 27 },
};

test('Chapter 10 context layouts retain every localized source label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, { layout, labels: expectedCount }] of Object.entries(
      figures,
    )) {
      const source = readFigure(directory, number);
      const expected = sourceLabels(source);
      assert.equal(
        expected.length,
        expectedCount,
        `${directory} Figure 10-${number}`,
      );

      const layoutSvg = layout(source);
      assert.equal(
        (layoutSvg.match(/<foreignObject\b/g) || []).length,
        expectedCount,
        `${directory} Figure 10-${number} source slots`,
      );
      assert.equal(
        (layoutSvg.match(/dir="auto"/g) || []).length,
        expectedCount,
        `${directory} Figure 10-${number} bidi labels`,
      );

      for (const theme of ['light', 'dark']) {
        const actual = renderedLabels(styleFigure(layoutSvg, theme));
        assert.deepEqual(
          actual.map(({ index }) => index).sort((a, b) => a - b),
          Array.from({ length: expectedCount }, (_, index) => index),
          `${directory} Figure 10-${number} ${theme} label slots`,
        );
        assert.deepEqual(
          actual.map(({ value }) => value).sort(),
          [...expected].sort(),
          `${directory} Figure 10-${number} ${theme} labels`,
        );
      }
    }
});

test('Figure 10-1 preserves the shared and isolated collaboration comparison', () => {
  const layout = layoutSharedContextComparison(readFigure('book-en', 1));

  assert.match(layout, /viewBox="0 0 1320 1260"/);
  assert.match(layout, /data-collaboration-model="shared-context"/);
  assert.match(layout, /data-collaboration-model="isolated-context"/);
  assert.equal((layout.match(/data-phase="[^"]+"/g) || []).length, 3);
  assert.equal((layout.match(/data-isolated-agent="[^"]+"/g) || []).length, 3);
  assert.match(layout, /data-shared-history="true"/);
  assert.match(layout, /data-shared-file-system="true"/);
  assert.equal(edges(layout).length, 0, 'the source comparison has no arrows');
});

test('Figure 10-2 keeps filesystem access, mount, upload, and external-source relationships', () => {
  const layout = layoutVirtualFilesystemMounts(readFigure('book-en', 2));

  assert.match(layout, /viewBox="0 0 1320 1010"/);
  assert.equal((layout.match(/data-region="[^"]+"/g) || []).length, 4);
  for (const region of ['private', 'shared', 'external', 'system'])
    assert.match(layout, new RegExp(`data-region="${region}"`));
  assert.deepEqual(edges(layout), [
    {
      name: 'agent-a-to-root',
      from: 'agent-a',
      to: 'virtual-filesystem',
      d: 'M 250 70 H 460',
    },
    {
      name: 'agent-b-to-root',
      from: 'agent-b',
      to: 'virtual-filesystem',
      d: 'M 250 160 H 360 V 140 H 460',
    },
    {
      name: 'root-to-private',
      from: 'virtual-filesystem',
      to: 'private',
      d: 'M 660 215 V 290 H 170 V 370',
    },
    {
      name: 'root-to-shared',
      from: 'virtual-filesystem',
      to: 'shared',
      d: 'M 660 215 V 290 H 490 V 370',
    },
    {
      name: 'root-to-external',
      from: 'virtual-filesystem',
      to: 'external',
      d: 'M 660 215 V 290 H 810 V 370',
    },
    {
      name: 'root-to-system',
      from: 'virtual-filesystem',
      to: 'system',
      d: 'M 660 215 V 290 H 1130 V 370',
    },
    {
      name: 'user-to-shared',
      from: 'user',
      to: 'shared',
      d: 'M 1180 190 H 1290 V 830 H 490 V 780',
    },
    {
      name: 'external-source-to-external',
      from: 'external-source',
      to: 'external',
      d: 'M 810 855 V 780',
    },
  ]);
  assert.match(layout, /data-edge="user-to-shared"[^>]*stroke-dasharray="7 6"/);
});

test('Figure 10-3 retains the review loop and ordered improvement rounds', () => {
  const layout = layoutProposerReviewerLoop(readFigure('book-en', 3));

  assert.match(layout, /viewBox="0 0 1320 1090"/);
  assert.match(layout, /data-agent="proposer"/);
  assert.match(layout, /data-agent="reviewer"/);
  assert.equal((layout.match(/data-round="[^"]+"/g) || []).length, 3);
  assert.match(layout, /data-comparison="single-vs-dual-agent"/);
  assert.deepEqual(edges(layout), [
    {
      name: 'proposer-to-reviewer',
      from: 'proposer',
      to: 'reviewer',
      d: 'M 520 175 H 800',
    },
    {
      name: 'reviewer-to-proposer',
      from: 'reviewer',
      to: 'proposer',
      d: 'M 800 345 H 520',
    },
    {
      name: 'round-1-to-round-2',
      from: 'round-1',
      to: 'round-2',
      d: 'M 420 718 H 470',
    },
    {
      name: 'round-2-to-round-3',
      from: 'round-2',
      to: 'round-3',
      d: 'M 850 718 H 900',
    },
  ]);
});

test('Figure 10-4 retains manager dispatch and the A-to-B-to-C sequence', () => {
  const layout = layoutManagerSequentialCoordination(readFigure('book-en', 4));

  assert.match(layout, /viewBox="0 0 1320 920"/);
  assert.match(layout, /data-manager="true"/);
  assert.equal((layout.match(/data-sub-agent="[^"]+"/g) || []).length, 3);
  assert.equal((layout.match(/data-sequence-index="\d+"/g) || []).length, 6);
  assert.deepEqual(edges(layout), [
    {
      name: 'manager-to-agent-a',
      from: 'manager',
      to: 'agent-a',
      d: 'M 420 250 V 310 H 220 V 390',
    },
    {
      name: 'manager-to-agent-b',
      from: 'manager',
      to: 'agent-b',
      d: 'M 660 250 V 390',
    },
    {
      name: 'manager-to-agent-c',
      from: 'manager',
      to: 'agent-c',
      d: 'M 900 250 V 310 H 1100 V 390',
    },
    {
      name: 'agent-a-to-agent-b',
      from: 'agent-a',
      to: 'agent-b',
      d: 'M 420 530 H 460',
    },
    {
      name: 'agent-b-to-agent-c',
      from: 'agent-b',
      to: 'agent-c',
      d: 'M 860 530 H 900',
    },
  ]);
});

test('Chapter 10 context layouts use readable wrapped HTML labels', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const svg = layout(readFigure('book-en', number));
    const labelCount = (svg.match(/<foreignObject\b/g) || []).length;
    const fontSizes = [...svg.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );

    assert.doesNotMatch(svg, /<text\b/);
    assert.ok(fontSizes.every((size) => size >= 16));
    assert.equal(
      (svg.match(/overflow-wrap:anywhere/g) || []).length,
      labelCount,
    );
    assert.equal(
      (svg.match(/unicode-bidi:plaintext/g) || []).length,
      labelCount,
    );
    assert.equal(
      (svg.match(/data-route="gutter"/g) || []).length,
      edges(svg).length,
    );
  }
});

test('Chapter 10 context layouts reject source structure drift', () => {
  const mutations = [
    [1, (source) => source.replace(/<g\b/, '<section')],
    [2, (source) => source.replace(/<line\b[^>]*\/>/, '')],
    [3, (source) => source.replace(/<rect\b/, '<circle')],
    [4, (source) => source.replace(/<marker\b[\s\S]*?<\/marker>/, '')],
  ];

  for (const [number, mutate] of mutations)
    assert.throws(
      () => figures[number].layout(mutate(readFigure('book-en', number))),
      new RegExp(`Figure 10-${number} source structure changed`),
    );
});
