import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import { layoutMemoryFoundation } from './memory-foundation-layout.mjs';

const figures = {
  1: { labels: [15, 16], edges: 2 },
  3: { labels: [23], edges: 8 },
  4: { labels: [16, 17], edges: 6 },
  5: { labels: [21, 22], edges: 3 },
  7: { labels: [7], edges: 17 },
};

function normalize(value) {
  return value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function sourceLabels(source) {
  return [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map((match) =>
    normalize(match[1]),
  );
}

function renderedLabels(source) {
  return [
    ...source.matchAll(
      /<span\b[^>]*data-source-label="(\d+)"[^>]*>([\s\S]*?)<\/span>/g,
    ),
  ].map((match) => ({ index: Number(match[1]), value: normalize(match[2]) }));
}

function readFigure(directory, number) {
  return readFileSync(
    new URL(`../../${directory}/images/fig3-${number}.svg`, import.meta.url),
    'utf8',
  );
}

test('memory-foundation layouts preserve every localized source label with readable type', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const edition of Object.values(editions))
    for (const [figure, specification] of Object.entries(figures)) {
      const source = readFigure(edition.directory, figure);
      const expectedLabels = sourceLabels(source);
      assert.ok(
        specification.labels.includes(expectedLabels.length),
        `${edition.directory} Figure 3-${figure} source label count`,
      );
      const layout = layoutMemoryFoundation(source, Number(figure), {
        rtl: edition.dir === 'rtl',
      });

      assert.match(layout, /viewBox="0 0 1000 \d+"/);
      assert.doesNotMatch(layout, /<text\b|<tspan\b/);
      assert.equal(
        (layout.match(/data-source-label="\d+"/g) || []).length,
        expectedLabels.length,
        `${edition.directory} Figure 3-${figure} label slots`,
      );
      for (const match of layout.matchAll(/font-size:(\d+)px/g))
        assert.ok(
          Number(match[1]) >= 14,
          `${edition.directory} Figure 3-${figure} ${match[0]}`,
        );
      if (edition.dir === 'rtl') {
        assert.match(layout, /dir="rtl"/);
        assert.doesNotMatch(layout, /dir="ltr"/);
      }

      for (const theme of ['light', 'dark']) {
        const actual = renderedLabels(styleFigure(layout, theme));
        assert.deepEqual(
          actual.map(({ index }) => index).sort((a, b) => a - b),
          Array.from({ length: expectedLabels.length }, (_, index) => index),
          `${edition.directory} Figure 3-${figure} ${theme} source indices`,
        );
        assert.deepEqual(
          actual.map(({ value }) => value).sort(),
          [...expectedLabels].sort(),
          `${edition.directory} Figure 3-${figure} ${theme} source text`,
        );
      }
    }
});

test('memory-foundation layouts retain source relationships and content regions', () => {
  for (const [figure, specification] of Object.entries(figures)) {
    const layout = layoutMemoryFoundation(
      readFigure('book-en', figure),
      Number(figure),
    );
    assert.equal(
      (layout.match(/data-edge="[^"]+"/g) || []).length,
      specification.edges,
      `Figure 3-${figure} relationship count`,
    );
  }

  const overview = layoutMemoryFoundation(readFigure('book-en', 1), 1);
  assert.match(overview, /data-region="user-memory"/);
  assert.match(overview, /data-region="knowledge-base"/);
  assert.match(overview, /data-region="shared-foundation"/);

  const comparison = layoutMemoryFoundation(readFigure('book-en', 3), 3);
  assert.equal((comparison.match(/data-stage="v2-[^"]+"/g) || []).length, 5);
  assert.equal((comparison.match(/data-stage="v3-[^"]+"/g) || []).length, 5);

  const memoryTypes = layoutMemoryFoundation(readFigure('book-en', 4), 4);
  assert.equal(
    (memoryTypes.match(/data-memory-subtype="[^"]+"/g) || []).length,
    3,
  );
  assert.equal(
    (memoryTypes.match(/data-memory-description="[^"]+"/g) || []).length,
    3,
  );
  assert.equal(
    (memoryTypes.match(/data-connector-caption="[^"]+"/g) || []).length,
    2,
  );
  assert.match(memoryTypes, /M162 \d+ H370 V\d+/);
  assert.match(memoryTypes, /M838 \d+ H630 V\d+/);

  const rag = layoutMemoryFoundation(readFigure('book-en', 5), 5);
  assert.equal((rag.match(/data-stage="[^"]+"/g) || []).length, 4);
  assert.equal((rag.match(/data-example="[^"]+"/g) || []).length, 3);

  const layered = layoutMemoryFoundation(readFigure('book-en', 7), 7);
  assert.equal((layered.match(/data-layer="layer-\d"/g) || []).length, 3);
  assert.equal((layered.match(/<circle\b/g) || []).length, 19);
});

test('memory-foundation layouts reject source structure drift', () => {
  for (const figure of Object.keys(figures).map(Number)) {
    const source = readFigure('book-en', figure);
    assert.throws(
      () =>
        layoutMemoryFoundation(
          source.replace(
            '</svg>',
            '<text>unexpected label</text><text>second unexpected label</text></svg>',
          ),
          figure,
        ),
      new RegExp(`Figure 3-${figure}`),
    );
    assert.throws(
      () =>
        layoutMemoryFoundation(source.replace(/<rect\b[^>]*\/>/, ''), figure),
      new RegExp(`Figure 3-${figure} source structure changed`),
    );
  }
  assert.throws(
    () => layoutMemoryFoundation(readFigure('book-en', 1), 2),
    /Unsupported memory-foundation figure/,
  );
});
