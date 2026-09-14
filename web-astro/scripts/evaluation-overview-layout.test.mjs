import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import {
  layoutEvaluationOverview,
  layoutDualControl,
  layoutEmbodiedEvaluation,
} from './evaluation-overview-figures.mjs';

const layouts = {
  1: layoutEvaluationOverview,
  3: layoutDualControl,
  10: layoutEmbodiedEvaluation,
};
const labelCounts = { 1: 24, 3: 34, 10: 39 };

function readFigure(directory, figure) {
  return readFileSync(
    new URL(`../../${directory}/images/fig7-${figure}.svg`, import.meta.url),
    'utf8',
  );
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

function renderedLabels(svg) {
  return [
    ...svg.matchAll(/<span data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
  ].map((match) => [Number(match[1]), match[2]]);
}

function connections(svg) {
  return [
    ...svg.matchAll(
      /<path\b[^>]*data-edge="([^"]+)"[^>]*data-from="([^"]+)"[^>]*data-to="([^"]+)"[^>]*data-route="gutter"[^>]*data-gutter-size="([\d.]+)"[^>]*data-card-gap-start="8"[^>]*data-card-gap-end="8"[^>]*\sd="([^"]+)"/g,
    ),
  ].map((match) => ({
    name: match[1],
    from: match[2],
    to: match[3],
    gutter: Number(match[4]),
    d: match[5],
  }));
}

function segments(d) {
  let x;
  let y;
  const result = [];
  for (const match of d.matchAll(/([MLHV])([\d. ]+)/g)) {
    const values = match[2].trim().split(/\s+/).map(Number);
    if (match[1] === 'M') {
      [x, y] = values;
      continue;
    }
    const nextX = match[1] === 'V' ? x : values[0];
    const nextY =
      match[1] === 'H' ? y : match[1] === 'V' ? values[0] : values[1];
    result.push([x, y, nextX, nextY]);
    [x, y] = [nextX, nextY];
  }
  return result;
}

function crosses([x1, y1, x2, y2], box) {
  if (y1 === y2)
    return (
      y1 > box.y &&
      y1 < box.y + box.height &&
      Math.max(x1, x2) > box.x &&
      Math.min(x1, x2) < box.x + box.width
    );
  if (x1 === x2)
    return (
      x1 > box.x &&
      x1 < box.x + box.width &&
      Math.max(y1, y2) > box.y &&
      Math.min(y1, y2) < box.y + box.height
    );
  return false;
}

test('evaluation overview layouts preserve all labels, typography, and bounds in 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [1, 3, 10]) {
      const source = readFigure(directory, figure);
      const unchanged = source;
      const expected = extractLabels(
        source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>'),
        `7-${figure}`,
        [labelCounts[figure]],
      );
      const svg = layouts[figure](source, { rtl: dir === 'rtl' });
      assert.equal(source, unchanged, `${directory} Figure 7-${figure} source`);
      assert.match(svg, new RegExp(`data-figure="7-${figure}"`));
      assert.doesNotMatch(svg, /<text\b|<tspan\b|NaN|undefined/);
      assert.deepEqual(
        renderedLabels(svg).sort((a, b) => a[0] - b[0]),
        expected.map((value, index) => [index, value]),
        `${directory} Figure 7-${figure} labels`,
      );
      const fontSizes = [...svg.matchAll(/font-size:([\d.]+)px/g)].map(
        (match) => Number(match[1]),
      );
      assert.ok(fontSizes.every((size) => size >= 14));
      for (const tier of [20, 18, 16, 14])
        assert.ok(
          fontSizes.includes(tier),
          `${directory} Figure 7-${figure} ${tier}px tier`,
        );
      if (dir === 'rtl') assert.match(svg, /dir="rtl"/);

      const [, canvasWidth, canvasHeight] = svg.match(
        /viewBox="0 0 ([\d.]+) ([\d.]+)"/,
      );
      assert.equal(Number(canvasWidth), 1000);
      for (const box of [
        ...boxes(svg, 'rect'),
        ...boxes(svg, 'foreignObject'),
      ]) {
        assert.ok(box.x >= 0 && box.y >= 0);
        assert.ok(
          box.x + box.width <= Number(canvasWidth) &&
            box.y + box.height <= Number(canvasHeight),
          `${directory} Figure 7-${figure} box outside canvas`,
        );
      }
    }
});

const expectedConnections = {
  1: [
    ['success-to-task-bank', 'success-definition', 'task-bank'],
    ['task-bank-to-verification', 'task-bank', 'verification-spectrum'],
    ['deterministic-to-checklist', 'deterministic', 'checklist'],
    ['checklist-to-rubric-llm', 'checklist', 'rubric-llm'],
    ['rubric-llm-to-pairwise', 'rubric-llm', 'pairwise'],
    ['verification-to-results', 'verification-spectrum', 'results'],
    ['results-to-task-bank', 'results', 'task-bank'],
  ],
  3: [
    ['user-to-agent-dialogue', 'user-simulator', 'agent'],
    ['agent-to-user-dialogue', 'agent', 'user-simulator'],
    ['user-to-shared-environment', 'user-simulator', 'device-state'],
    ['agent-to-shared-environment', 'agent', 'carrier-state'],
  ],
  10: [
    ['vision-to-language', 'vision-encoder', 'language-model'],
    ['language-to-action', 'language-model', 'action-decoder'],
    ['instruction-to-action', 'instruction', 'action-decoder'],
    ['head-camera-to-vla', 'head-camera', 'vla-model'],
    ['joint-state-to-vla', 'joint-state', 'vla-model'],
    ['model-to-simulator', 'action-decoder', 'simulator'],
    ['simulator-to-model', 'simulator', 'vision-encoder'],
  ],
};

test('all editions retain evaluation relationships and route arrows through dedicated gutters', () => {
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [1, 3, 10]) {
      const svg = layouts[figure](readFigure(directory, figure), {
        rtl: dir === 'rtl',
      });
      const actual = connections(svg);
      assert.deepEqual(
        actual.map(({ name, from, to }) => [name, from, to]),
        expectedConnections[figure],
        `${directory} Figure 7-${figure} connections`,
      );
      assert.ok(
        actual.every(({ gutter }) => gutter >= 64),
        `${directory} Figure 7-${figure} arrow gutter`,
      );
      if (figure === 3) {
        assert.match(
          svg,
          /data-dialogue="bidirectional" data-caption-labels="8 9"/,
        );
        assert.equal(
          (svg.match(/data-dialogue-caption="shared"/g) || []).length,
          2,
        );
      }
      if (figure === 10) {
        const captions = [
          ...svg.matchAll(
            /<foreignObject data-arrow-caption="(?:model-to-simulator|simulator-to-model)"[^>]*\bwidth="([\d.]+)"/g,
          ),
        ];
        assert.equal(captions.length, 2);
        assert.ok(captions.every((match) => Number(match[1]) >= 110));
      }

      const nodeBoxes = [
        ...svg.matchAll(
          /<rect\b[^>]*data-node="[^"]+"[^>]*\bx="([\d.]+)"[^>]*\by="([\d.]+)"[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"/g,
        ),
      ].map(([, x, y, width, height]) => ({
        x: Number(x),
        y: Number(y),
        width: Number(width),
        height: Number(height),
      }));
      const labelBoxes = boxes(svg, 'foreignObject');
      for (const connection of actual)
        for (const segment of segments(connection.d)) {
          assert.ok(
            nodeBoxes.every((box) => !crosses(segment, box)),
            `${directory} Figure 7-${figure} ${connection.name} crosses a card`,
          );
          assert.ok(
            labelBoxes.every((box) => !crosses(segment, box)),
            `${directory} Figure 7-${figure} ${connection.name} crosses text`,
          );
        }
    }
});

test('source guards accept known variants and reject structural drift', () => {
  assert.doesNotThrow(() =>
    layoutEmbodiedEvaluation(readFigure('book-en', 10)),
  );
  assert.doesNotThrow(() => layoutEmbodiedEvaluation(readFigure('book', 10)));
  assert.doesNotThrow(() =>
    layoutEmbodiedEvaluation(readFigure('book-tr', 10)),
  );
  for (const figure of [1, 3, 10]) {
    const source = readFigure('book-en', figure);
    assert.throws(
      () => layouts[figure](source.replace(/<rect\b[^>]*\/>/, '')),
      new RegExp(`Figure 7-${figure} source structure changed`),
    );
    assert.throws(
      () =>
        layouts[figure](source.replace(/viewBox="[^"]+"/, 'viewBox="0 0 1 1"')),
      new RegExp(`Figure 7-${figure} source structure changed`),
    );
  }
});
