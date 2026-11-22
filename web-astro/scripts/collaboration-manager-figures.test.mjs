import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutBookTranslationManager,
  layoutCascadingTermination,
  layoutManagerParallelCoordination,
  layoutPhoneComputerCollaboration,
} from './collaboration-manager-figures.mjs';

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

function source(number, directory = 'book-en') {
  return readFileSync(
    new URL(`../../${directory}/images/fig10-${number}.svg`, import.meta.url),
    'utf8',
  );
}

function rectangles(svg, attribute) {
  return [
    ...svg.matchAll(new RegExp(`<rect\\b[^>]*${attribute}="[^"]+"[^>]*>`, 'g')),
  ].map(({ 0: tag }) => ({
    x: Number(tag.match(/\bx="([\d.]+)"/)?.[1]),
    y: Number(tag.match(/\by="([\d.]+)"/)?.[1]),
    width: Number(tag.match(/\bwidth="([\d.]+)"/)?.[1]),
    height: Number(tag.match(/\bheight="([\d.]+)"/)?.[1]),
  }));
}

function labelRectangles(svg) {
  return [...svg.matchAll(/<foreignObject\b[^>]*>/g)].map(({ 0: tag }) => ({
    x: Number(tag.match(/\bx="([\d.]+)"/)?.[1]),
    y: Number(tag.match(/\by="([\d.]+)"/)?.[1]),
    width: Number(tag.match(/\bwidth="([\d.]+)"/)?.[1]),
    height: Number(tag.match(/\bheight="([\d.]+)"/)?.[1]),
  }));
}

function connectorSegments(svg) {
  const segments = [];
  for (const { 0: tag } of svg.matchAll(
    /<path\b[^>]*data-edge="[^"]+"[^>]*>/g,
  )) {
    const edge = tag.match(/data-edge="([^"]+)"/)?.[1];
    const path = tag.match(/\sd="([^"]+)"/)?.[1];
    assert.ok(edge && path);
    const tokens = path.match(/[MHV]|-?[\d.]+/g) || [];
    let command = '';
    let x = 0;
    let y = 0;
    for (let index = 0; index < tokens.length;) {
      if (/[MHV]/.test(tokens[index])) command = tokens[index++];
      const from = { x, y };
      if (command === 'M') {
        x = Number(tokens[index++]);
        y = Number(tokens[index++]);
        command = 'L';
        continue;
      }
      if (command === 'H') x = Number(tokens[index++]);
      else if (command === 'V') y = Number(tokens[index++]);
      else {
        x = Number(tokens[index++]);
        y = Number(tokens[index++]);
      }
      segments.push({ edge, from, to: { x, y } });
    }
  }
  return segments;
}

function overlaps(first, second) {
  return (
    first.x < second.x + second.width &&
    first.x + first.width > second.x &&
    first.y < second.y + second.height &&
    first.y + first.height > second.y
  );
}

function crossesInterior(segment, box) {
  const { from, to } = segment;
  if (from.x === to.x)
    return (
      from.x > box.x &&
      from.x < box.x + box.width &&
      Math.max(from.y, to.y) > box.y &&
      Math.min(from.y, to.y) < box.y + box.height
    );
  if (from.y === to.y)
    return (
      from.y > box.y &&
      from.y < box.y + box.height &&
      Math.max(from.x, to.x) > box.x &&
      Math.min(from.x, to.x) < box.x + box.width
    );
  throw new Error(`Non-orthogonal connector in ${segment.edge}`);
}

const figures = {
  5: { layout: layoutBookTranslationManager, labels: 37 },
  6: { layout: layoutManagerParallelCoordination, labels: 28 },
  7: { layout: layoutPhoneComputerCollaboration, labels: 31 },
  8: { layout: layoutCascadingTermination, labels: 46 },
};

test('Chapter 10 manager layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, { layout, labels: expectedCount }] of Object.entries(
      figures,
    )) {
      const original = source(number, directory);
      const expected = sourceLabels(original);
      assert.equal(
        expected.length,
        expectedCount,
        `${directory} Figure 10-${number}`,
      );

      const layoutSvg = layout(original);
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

test('Figure 10-5 keeps manager fan-out, artifact handoffs, and isolated file views explicit', () => {
  const layout = layoutBookTranslationManager(source(5));

  assert.match(layout, /viewBox="0 0 1320 1120"/);
  for (const kind of ['glossary', 'translation', 'proofreading'])
    assert.match(layout, new RegExp(`data-agent="${kind}"`));
  for (const edge of [
    'manager-to-glossary',
    'manager-to-translation',
    'manager-to-proofreading',
    'glossary-to-translation',
    'translation-to-proofreading',
  ])
    assert.match(layout, new RegExp(`data-edge="${edge}"`));
  assert.match(layout, /data-target-port="translation-input"/);
  assert.match(layout, /data-source-port="translation-output"/);
  assert.equal((layout.match(/data-artifact-card="[^"]+"/g) || []).length, 4);
  assert.match(layout, /data-shared-filesystem="true"/);
  assert.match(layout, /data-context-isolation="true"/);
});

test('Figure 10-6 routes manager work through one message bus and preserves the message envelope examples', () => {
  const layout = layoutManagerParallelCoordination(source(6));

  assert.match(layout, /data-edge="manager-to-message-bus"/);
  for (const number of [1, 2, 3, 4])
    assert.match(
      layout,
      new RegExp(`data-edge="message-bus-to-agent-${number}"`),
    );
  for (const route of [
    'manager-to-agent-1',
    'agent-3-to-manager',
    'agent-1-to-agent-2',
    'manager-to-agent-4',
  ])
    assert.match(layout, new RegExp(`data-message-route="${route}"`));
  assert.equal((layout.match(/data-message-card="[^"]+"/g) || []).length, 4);
});

test('Figure 10-7 presents two independent ReAct flows joined by a bidirectional channel', () => {
  const layout = layoutPhoneComputerCollaboration(source(7));

  assert.equal((layout.match(/data-agent-flow="phone"/g) || []).length, 3);
  assert.equal((layout.match(/data-agent-flow="computer"/g) || []).length, 3);
  for (const edge of [
    'phone-agent-to-websocket',
    'websocket-to-phone-agent',
    'computer-agent-to-websocket',
    'websocket-to-computer-agent',
  ])
    assert.match(layout, new RegExp(`data-edge="${edge}"`));
  assert.match(
    layout,
    /data-channel="websocket" data-direction="bidirectional"/,
  );
  assert.equal(
    (layout.match(/data-message-direction="phone-to-computer"/g) || []).length,
    2,
  );
  assert.equal(
    (layout.match(/data-message-direction="computer-to-phone"/g) || []).length,
    2,
  );
});

test('Figure 10-8 ties the successful search to an ordered cascading termination sequence', () => {
  const layout = layoutCascadingTermination(source(8));

  for (const number of [1, 2, 3, 4, '5-10'])
    assert.match(layout, new RegExp(`data-edge="manager-to-agent-${number}"`));
  assert.match(layout, /data-agent="3" data-state="found"/);
  assert.match(
    layout,
    /data-edge="agent-3-success-to-cascade" data-trigger="target-found"/,
  );
  assert.equal(
    (layout.match(/data-termination-event="[^"]+"/g) || []).length,
    5,
  );
  assert.equal((layout.match(/data-timeline-edge="true"/g) || []).length, 4);
  assert.match(layout, /data-result="found"/);
  assert.match(layout, /data-performance-comparison="true"/);
});

test('Chapter 10 manager layouts reserve wrapped text regions and connector gutters', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const svg = layout(source(number));
    const labels = [...svg.matchAll(/<foreignObject\b[^>]*>/g)];
    const fontSizes = [...svg.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );

    assert.ok(fontSizes.length > 0);
    assert.ok(fontSizes.every((size) => size >= 15));
    assert.doesNotMatch(svg, /<text\b/);
    assert.equal(
      (svg.match(/overflow-wrap:anywhere/g) || []).length,
      labels.length,
    );
    assert.ok(
      labels.every((match) => {
        const width = Number(match[0].match(/\bwidth="([\d.]+)"/)?.[1]);
        const height = Number(match[0].match(/\bheight="([\d.]+)"/)?.[1]);
        return width >= 188 && height >= 24;
      }),
      `Figure 10-${number} label wrapping regions`,
    );
    assert.ok((svg.match(/data-connector-gutter=/g) || []).length > 0);
  }
});

test('Chapter 10 manager connectors stay out of label regions and peer cards do not overlap', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const svg = layout(source(number));
    const labels = labelRectangles(svg);
    for (const segment of connectorSegments(svg))
      for (const box of labels)
        assert.equal(
          crossesInterior(segment, box),
          false,
          `Figure 10-${number} ${segment.edge} crosses a label`,
        );

    for (const attribute of [
      'data-node-card',
      'data-agent-card',
      'data-stage-card',
      'data-artifact-card',
      'data-event-card',
      'data-message-card',
    ]) {
      const peers = rectangles(svg, attribute);
      for (let first = 0; first < peers.length; first += 1)
        for (let second = first + 1; second < peers.length; second += 1)
          assert.equal(
            overlaps(peers[first], peers[second]),
            false,
            `Figure 10-${number} overlapping ${attribute} rectangles`,
          );
    }
  }
});

test('Chapter 10 manager layouts reject source structure drift', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const original = source(number);
    assert.throws(
      () => layout(original.replace(/<rect\b[^>]*\/>/, '')),
      new RegExp(`Figure 10-${number} source structure changed`),
    );
  }
});
