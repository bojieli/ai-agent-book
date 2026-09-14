import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutToolCache } from './tool-cache-layout.mjs';

function readFigure(directory, figure) {
  return readFileSync(
    new URL(`../../${directory}/images/fig4-${figure}.svg`, import.meta.url),
    'utf8',
  );
}

function renderedLabels(svg) {
  return [
    ...svg.matchAll(
      /<span\b[^>]*data-source-label="(\d+)"[^>]*>([\s\S]*?)<\/span>/g,
    ),
  ].map((match) => [Number(match[1]), match[2]]);
}

function boxes(svg, element) {
  return [
    ...svg.matchAll(
      new RegExp(
        `<${element}\\b[^>]*\\bx="([\\d.]+)"[^>]*\\by="([\\d.]+)"[^>]*\\bwidth="([\\d.]+)"[^>]*\\bheight="([\\d.]+)"`,
        'g',
      ),
    ),
  ].map(([, x, y, width, height]) => ({
    x: Number(x),
    y: Number(y),
    width: Number(width),
    height: Number(height),
  }));
}

test('tool-cache layouts preserve every source label once in all 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const edition of Object.values(editions))
    for (const figure of [3, 4]) {
      const source = readFigure(edition.directory, figure);
      const unchanged = source;
      const labels = extractLabels(
        source,
        `4-${figure}`,
        {
          3: [38],
          4: [17, 19],
        }[figure],
      );
      const layout = layoutToolCache(source, figure, {
        rtl: edition.dir === 'rtl',
      });
      assert.equal(source, unchanged, `${edition.directory} source SVG`);
      assert.match(layout, new RegExp(`data-figure="4-${figure}"`));
      assert.doesNotMatch(layout, /<text\b|<tspan\b|NaN|undefined/);
      assert.deepEqual(
        renderedLabels(layout).sort((a, b) => a[0] - b[0]),
        labels.map((value, index) => [index, value]),
        `${edition.directory} Figure 4-${figure}`,
      );
      const fontSizes = [...layout.matchAll(/font-size:([\d.]+)px/g)].map(
        (match) => Number(match[1]),
      );
      assert.ok(fontSizes.every((size) => size >= 14));
      for (const expected of [20, 18, 16, 14])
        assert.ok(
          fontSizes.includes(expected),
          `${edition.directory} Figure 4-${figure} ${expected}px tier`,
        );
      if (edition.dir === 'rtl') assert.match(layout, /dir="rtl"/);

      const [, canvasWidth, canvasHeight] = layout.match(
        /viewBox="0 0 (\d+) (\d+)"/,
      );
      assert.equal(Number(canvasWidth), 1000);
      for (const box of [
        ...boxes(layout, 'rect'),
        ...boxes(layout, 'foreignObject'),
      ]) {
        assert.ok(box.x >= 0 && box.y >= 0);
        assert.ok(
          box.x + box.width <= Number(canvasWidth) &&
            box.y + box.height <= Number(canvasHeight),
          `${edition.directory} Figure 4-${figure} box outside canvas`,
        );
      }
    }
});

test('Figure 4-3 separates metrics and retains a comparison without flow arrows', () => {
  for (const edition of Object.values(editions)) {
    const layout = layoutToolCache(readFigure(edition.directory, 3), 3, {
      rtl: edition.dir === 'rtl',
    });
    assert.match(layout, /data-region="naive-context-stack"/);
    assert.match(layout, /data-region="optimized-context-stack"/);
    assert.match(layout, /data-region="comparison-table"/);
    assert.equal((layout.match(/data-metric="\d+"/g) || []).length, 5);
    assert.equal((layout.match(/data-table-cell=/g) || []).length, 9);
    assert.equal((layout.match(/marker-end=/g) || []).length, 0);
    assert.equal((layout.match(/data-edge=/g) || []).length, 0);
    for (const stack of ['naive', 'optimized']) {
      const [, panelY, panelHeight] = layout.match(
        new RegExp(
          `<rect\\b[^>]*data-region="${stack}-context-stack"[^>]*y="([\\d.]+)"[^>]*height="([\\d.]+)"`,
        ),
      );
      const cards = [
        ...layout.matchAll(
          new RegExp(
            `<rect\\b[^>]*data-stack="${stack}"[^>]*y="([\\d.]+)"[^>]*height="([\\d.]+)"`,
            'g',
          ),
        ),
      ];
      const last = cards.at(-1);
      assert.equal(
        Number(panelY) + Number(panelHeight),
        Number(last[1]) + Number(last[2]) + 20,
        `${edition.directory} ${stack} panel fits its stack`,
      );
    }
  }
});

test('Figure 4-4 keeps two schema callouts clear of cards and each other', () => {
  for (const edition of Object.values(editions)) {
    const layout = layoutToolCache(readFigure(edition.directory, 4), 4, {
      rtl: edition.dir === 'rtl',
    });
    assert.match(layout, /data-region="static-prefix"/);
    assert.match(layout, /data-region="append-only-trajectory"/);
    assert.equal((layout.match(/data-schema-injection=/g) || []).length, 2);
    assert.equal((layout.match(/data-edge="schema-callout-/g) || []).length, 2);
    assert.equal((layout.match(/marker-end=/g) || []).length, 2);
    for (const match of layout.matchAll(
      /<path\b[^>]*data-edge="schema-callout-[12]"[^>]*data-card-gap-start="8"[^>]*data-card-gap-end="8"[^>]*d="M628 ([\d.]+) H676 V([\d.]+) H712"/g,
    )) {
      assert.ok(Number.isFinite(Number(match[1])));
      assert.ok(Number.isFinite(Number(match[2])));
      assert.ok(712 - 628 >= 48);
    }
    const paths = layout.match(/data-edge="schema-callout-/g) || [];
    assert.equal(paths.length, 2, `${edition.directory} connector geometry`);
    const callouts = [
      ...layout.matchAll(
        /<rect\b[^>]*data-callout="([12])"[^>]*x="720" y="([\d.]+)" width="256" height="([\d.]+)"/g,
      ),
    ].map((match) => ({
      id: Number(match[1]),
      y: Number(match[2]),
      height: Number(match[3]),
    }));
    assert.equal(callouts.length, 2);
    callouts.sort((a, b) => a.id - b.id);
    assert.ok(
      callouts[0].y + callouts[0].height + 32 <= callouts[1].y,
      `${edition.directory} callout separation`,
    );
  }
});

test('tool-cache layouts reject source drift and unsupported figures', () => {
  for (const figure of [3, 4]) {
    const source = readFigure('book-en', figure);
    assert.throws(
      () => layoutToolCache(source.replace(/<rect\b[^>]*\/>/, ''), figure),
      new RegExp(`Figure 4-${figure} source structure changed`),
    );
    assert.throws(
      () =>
        layoutToolCache(
          source.replace('</svg>', '<text>unexpected</text></svg>'),
          figure,
        ),
      new RegExp(`Figure 4-${figure}`),
    );
  }
  assert.throws(
    () => layoutToolCache(readFigure('book-en', 3), 2),
    /Unsupported tool-cache figure/,
  );
});
