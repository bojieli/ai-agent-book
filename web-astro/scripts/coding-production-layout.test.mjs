import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutCodingProduction } from './coding-production-layout.mjs';

const expectedLabelCounts = { 5: [37], 6: [50], 7: [50, 51] };

function readFigure(directory, figure) {
  return readFileSync(
    new URL(`../../${directory}/images/fig5-${figure}.svg`, import.meta.url),
    'utf8',
  );
}

function renderedLabels(svg) {
  return [
    ...svg.matchAll(/<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
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

function edges(svg) {
  return [
    ...svg.matchAll(
      /<path\b[^>]*data-edge="([^"]+)"[^>]*data-from="([^"]+)"[^>]*data-to="([^"]+)"[^>]*data-route="gutter"[^>]*data-card-gap-start="8"[^>]*data-card-gap-end="8"[^>]*\sd="([^"]+)"/g,
    ),
  ].map((match) => ({
    name: match[1],
    from: match[2],
    to: match[3],
    d: match[4],
  }));
}

test('coding-production layouts preserve all source labels at readable sizes in all 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [5, 6, 7]) {
      const source = readFigure(directory, figure);
      const unchanged = source;
      const expected = extractLabels(
        source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>'),
        `5-${figure}`,
        expectedLabelCounts[figure],
      );
      const layout = layoutCodingProduction(source, figure, {
        rtl: dir === 'rtl',
      });
      assert.equal(source, unchanged, `${directory} Figure 5-${figure} source`);
      assert.match(layout, new RegExp(`data-figure="5-${figure}"`));
      assert.doesNotMatch(layout, /<text\b|<tspan\b|NaN|undefined/);
      assert.deepEqual(
        renderedLabels(layout).sort((a, b) => a[0] - b[0]),
        expected.map((value, index) => [index, value]),
        `${directory} Figure 5-${figure} labels`,
      );

      const sizes = [...layout.matchAll(/font-size:([\d.]+)px/g)].map((match) =>
        Number(match[1]),
      );
      assert.ok(sizes.every((size) => size >= 14));
      for (const expectedSize of [20, 18, 16, 14])
        assert.ok(
          sizes.includes(expectedSize),
          `${directory} Figure 5-${figure} ${expectedSize}px tier`,
        );
      if (dir === 'rtl') assert.match(layout, /dir="rtl"/);

      const [, canvasWidth, canvasHeight] = layout.match(
        /viewBox="0 0 ([\d.]+) ([\d.]+)"/,
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
          `${directory} Figure 5-${figure} box outside canvas`,
        );
      }
    }
});

test('Figure 5-5 retains the two-way proposer-reviewer loop and complete code snippets', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutCodingProduction(readFigure(directory, 5), 5, {
      rtl: dir === 'rtl',
    });
    assert.match(svg, /data-agent="proposer"/);
    assert.match(svg, /data-agent="reviewer"/);
    assert.equal((svg.match(/data-benefit="/g) || []).length, 3);
    assert.match(svg, /data-code-block="proposer-output" data-code-lines="9"/);
    assert.match(svg, /data-code-block="reviewer-render" data-code-lines="2"/);
    assert.match(
      svg,
      /data-code-block="reviewer-analysis" data-code-lines="6"/,
    );
    assert.equal(
      (svg.match(/data-arrow-caption="(?:24|25)"/g) || []).length,
      2,
    );
    assert.deepEqual(
      edges(svg).map(({ name, from, to, d }) => ({ name, from, to, d })),
      [
        {
          name: 'proposer-to-reviewer',
          from: 'proposer',
          to: 'reviewer',
          d: edges(svg)[0].d,
        },
        {
          name: 'reviewer-to-proposer',
          from: 'reviewer',
          to: 'proposer',
          d: edges(svg)[1].d,
        },
      ],
    );
    assert.match(edges(svg)[0].d, /^M436 [\d.]+ L564 [\d.]+$/);
    assert.match(edges(svg)[1].d, /^M564 [\d.]+ L436 [\d.]+$/);
    assert.match(
      svg,
      /<path[^>]*data-edge="reviewer-to-proposer"[^>]*stroke-dasharray="6 5"/,
    );
    assert.equal((svg.match(/data-gutter-size="144"/g) || []).length, 3);
  }
});

test('Figure 5-6 retains two sequential five-stage pipelines and their phase connector', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutCodingProduction(readFigure(directory, 6), 6, {
      rtl: dir === 'rtl',
    });
    assert.equal(
      (svg.match(/data-pipeline="1" data-stage="/g) || []).length,
      5,
    );
    assert.equal(
      (svg.match(/data-pipeline="2" data-stage="/g) || []).length,
      5,
    );
    assert.equal((svg.match(/data-phase-header="[12]"/g) || []).length, 2);
    assert.equal(
      (svg.match(/data-acceptance-criterion="[123]"/g) || []).length,
      3,
    );
    assert.match(svg, /data-phase-connector-caption="true"/);
    const flow = edges(svg);
    assert.equal(flow.length, 9);
    assert.equal(
      flow.filter((item) => item.name === 'ppt-complete-to-video-phase').length,
      1,
    );
    assert.equal(
      flow.filter((item) => item.name !== 'ppt-complete-to-video-phase').length,
      8,
    );
    assert.match(flow[0].d, /^M476 [\d.]+ H500 V[\d.]+ H524$/);
    assert.match(flow[2].d, /^M524 [\d.]+ H500 V[\d.]+ H476$/);
    assert.match(flow[4].d, /^M246 [\d.]+ V[\d.]+ H500 V[\d.]+$/);
    assert.match(flow[5].d, /^M476 [\d.]+ H500 V[\d.]+ H524$/);
    assert.match(flow[7].d, /^M524 [\d.]+ H500 V[\d.]+ H476$/);
    for (const match of svg.matchAll(
      /<path\b[^>]*data-edge="[^"]+"[^>]*data-gutter-size="([\d.]+)"/g,
    ))
      assert.ok(Number(match[1]) >= 64, `${directory} arrow gutter`);
  }
});

test('Figure 5-7 makes the log-to-issue production sequence explicit', () => {
  const expected = [
    ['log-collection-to-llm-analysis', 'log-collection', 'llm-analysis'],
    ['llm-analysis-to-structured-report', 'llm-analysis', 'structured-report'],
    [
      'structured-report-to-regression-test',
      'structured-report',
      'regression-test',
    ],
    ['regression-test-to-github-issue', 'regression-test', 'github-issue'],
  ];
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutCodingProduction(readFigure(directory, 7), 7, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-production-stage="[1-5]"/g) || []).length, 5);
    assert.match(svg, /data-automation-summary="true"/);
    assert.deepEqual(
      edges(svg).map(({ name, from, to }) => [name, from, to]),
      expected,
      `${directory} stage order`,
    );
    for (const item of edges(svg)) {
      const match = item.d.match(/^M500 ([\d.]+) L500 ([\d.]+)$/);
      assert.ok(match);
      assert.equal(Number(match[2]) - Number(match[1]), 48);
    }
  }
});

test('coding-production layouts reject source drift and unsupported figures', () => {
  for (const figure of [5, 6, 7]) {
    const source = readFigure('book-en', figure);
    assert.throws(
      () =>
        layoutCodingProduction(source.replace(/<rect\b[^>]*\/>/, ''), figure),
      new RegExp(`Figure 5-${figure} source structure changed`),
    );
    assert.throws(
      () =>
        layoutCodingProduction(
          source.replace('</svg>', '<text>unexpected</text></svg>'),
          figure,
        ),
      new RegExp(`Figure 5-${figure}`),
    );
  }
  assert.doesNotThrow(() =>
    layoutCodingProduction(readFigure('book-es', 7), 7),
  );
  assert.doesNotThrow(() =>
    layoutCodingProduction(readFigure('book-vi', 5), 5),
  );
  assert.doesNotThrow(() => layoutCodingProduction(readFigure('book', 6), 6));
  assert.throws(
    () => layoutCodingProduction(readFigure('book-en', 5), 4),
    /Unsupported coding-production figure/,
  );
});
