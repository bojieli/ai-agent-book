import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutAsyncArchitecture } from './async-architecture-layout.mjs';

const expectedLabelCounts = { 1: [39], 2: [28], 3: [43], 4: [18], 5: [22] };

function readFigure(directory, figure) {
  return readFileSync(
    new URL(`../../${directory}/images/fig6-${figure}.svg`, import.meta.url),
    'utf8',
  );
}

function normalizedSource(source) {
  return source.replace(/<text\b([^>]*)\/>/g, '<text$1></text>');
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
      /<path\b[^>]*data-edge="([^"]+)"[^>]*data-from="([^"]+)"[^>]*data-to="([^"]+)"[^>]*data-route="gutter"[^>]*data-card-gap-start="8"[^>]*data-card-gap-end="8"[^>]*data-gutter-size="([\d.]+)"[^>]*\sd="([^"]+)"/g,
    ),
  ].map((match) => ({
    name: match[1],
    from: match[2],
    to: match[3],
    gutter: Number(match[4]),
    d: match[5],
  }));
}

function timelineCard(svg, id) {
  const match = svg.match(
    new RegExp(
      `<g data-timeline-event="${id}"><rect x="([\\d.]+)" y="([\\d.]+)" width="([\\d.]+)" height="([\\d.]+)"`,
    ),
  );
  assert.ok(match, `missing timeline event ${id}`);
  return {
    x: Number(match[1]),
    y: Number(match[2]),
    width: Number(match[3]),
    height: Number(match[4]),
  };
}

test('async-architecture layouts preserve every source label and remain in bounds in all 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [1, 2, 3, 4, 5]) {
      const source = readFigure(directory, figure);
      const unchanged = source;
      const expected = extractLabels(
        normalizedSource(source),
        `6-${figure}`,
        expectedLabelCounts[figure],
      );
      const layout = layoutAsyncArchitecture(source, figure, {
        rtl: dir === 'rtl',
      });
      assert.equal(source, unchanged, `${directory} Figure 6-${figure} source`);
      assert.match(layout, new RegExp(`data-figure="6-${figure}"`));
      assert.doesNotMatch(layout, /<text\b|<tspan\b|NaN|undefined/);
      assert.deepEqual(
        renderedLabels(layout).sort((a, b) => a[0] - b[0]),
        expected.map((value, index) => [index, value]),
        `${directory} Figure 6-${figure} labels`,
      );

      const sizes = [...layout.matchAll(/font-size:([\d.]+)px/g)].map((match) =>
        Number(match[1]),
      );
      assert.ok(sizes.every((size) => size >= 14));
      assert.ok(
        sizes.includes(16),
        `${directory} Figure 6-${figure} body tier`,
      );
      if ([1, 2, 3, 5].includes(figure))
        assert.ok(
          sizes.includes(20),
          `${directory} Figure 6-${figure} heading tier`,
        );
      if ([1, 3, 5].includes(figure))
        assert.ok(
          sizes.includes(18),
          `${directory} Figure 6-${figure} title tier`,
        );
      if ([1, 3, 4].includes(figure))
        assert.ok(
          sizes.includes(14),
          `${directory} Figure 6-${figure} code tier`,
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
          `${directory} Figure 6-${figure} box outside canvas`,
        );
      }
    }
});

test('Figure 6-1 keeps event sources, the priority queue, and the five-stage processing loop', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutAsyncArchitecture(readFigure(directory, 1), 1, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-event-source="[1-4]"/g) || []).length, 4);
    assert.equal((svg.match(/data-queue-event="[1-4]"/g) || []).length, 4);
    assert.equal((svg.match(/data-processing-stage="[1-5]"/g) || []).length, 5);
    assert.deepEqual(
      edges(svg).map(({ name, from, to }) => [name, from, to]),
      [
        ['sources-to-queue', 'event-sources', 'event-queue'],
        ['queue-to-processing', 'event-queue', 'agent-processing'],
        ['processing-1-to-2', 'processing-1', 'processing-2'],
        ['processing-2-to-3', 'processing-2', 'processing-3'],
        ['processing-3-to-4', 'processing-3', 'processing-4'],
        ['processing-4-to-5', 'processing-4', 'processing-5'],
        ['result-to-router-loop', 'result-handling', 'router'],
      ],
    );
    assert.match(
      svg,
      /data-edge="result-to-router-loop"[^>]*stroke-dasharray="6 5"/,
    );
  }
});

test('Figure 6-2 distinguishes cancellation, queued updates, and independent parallel work', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutAsyncArchitecture(readFigure(directory, 2), 2, {
      rtl: dir === 'rtl',
    });
    for (const pattern of ['cancellation', 'queue', 'parallel'])
      assert.match(svg, new RegExp(`data-scheduling-pattern="${pattern}"`));
    assert.equal((svg.match(/data-cancelled-work="[12]"/g) || []).length, 2);
    assert.equal((svg.match(/data-queue-stage="[1-3]"/g) || []).length, 3);
    assert.equal((svg.match(/data-parallel-stage="[1-3]"/g) || []).length, 3);
    const flow = edges(svg);
    assert.ok(flow.some((item) => item.name === 'interrupt-to-new-reasoning'));
    assert.ok(flow.some((item) => item.name === 'waiting-to-batch-append'));
    assert.ok(flow.some((item) => item.name === 'weather-to-reply'));
    assert.ok(flow.every((item) => item.gutter >= 20));
  }
});

test('Figure 6-3 retains external inputs, runtime order, bidirectional tools, and persistence', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutAsyncArchitecture(readFigure(directory, 3), 3, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-external-source="[1-6]"/g) || []).length, 6);
    assert.equal((svg.match(/data-runtime-stage="[1-5]"/g) || []).length, 5);
    assert.equal((svg.match(/data-tool-group="[1-4]"/g) || []).length, 4);
    assert.equal((svg.match(/data-persistence-item="[1-5]"/g) || []).length, 5);
    const flow = edges(svg);
    assert.deepEqual(
      flow
        .filter(
          (item) =>
            item.name.includes('runtime-to-tools') ||
            item.name.includes('tools-to-runtime'),
        )
        .map(({ name, from, to }) => [name, from, to]),
      [
        ['runtime-to-tools', 'agent-loop', 'mcp-tools'],
        ['tools-to-runtime', 'mcp-tools', 'agent-loop'],
      ],
    );
    assert.match(
      svg,
      /data-edge="tools-to-runtime"[^>]*stroke-dasharray="6 5"/,
    );
  }
});

test('Figure 6-4 preserves all five lanes, three milestones, and the three-tool launch', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutAsyncArchitecture(readFigure(directory, 4), 4, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-lane="[1-5]"/g) || []).length, 5);
    assert.equal((svg.match(/data-milestone="[1-3]"/g) || []).length, 3);
    assert.equal((svg.match(/data-milestone-line="[1-3]"/g) || []).length, 3);
    assert.equal((svg.match(/data-milestone-leader="[1-3]"/g) || []).length, 3);
    const milestoneXs = [...svg.matchAll(/data-time-x="([\d.]+)"/g)].map(
      (match) => Number(match[1]),
    );
    const toolA = timelineCard(svg, '2-1');
    const toolB = timelineCard(svg, '3-1');
    const cancellation = timelineCard(svg, '4-2');
    const report = timelineCard(svg, '1-3');
    assert.deepEqual(milestoneXs, [
      toolA.x + toolA.width,
      cancellation.x + cancellation.width / 2,
      toolB.x + toolB.width,
    ]);
    assert.ok(
      report.x > toolB.x + toolB.width,
      `${directory} report must begin after Tool B completes`,
    );
    assert.deepEqual(
      edges(svg).map(({ name, from, to }) => [name, from, to]),
      [
        ['launch-tool-1', 'launch-tools', 'tool-1'],
        ['launch-tool-2', 'launch-tools', 'tool-2'],
        ['launch-tool-3', 'launch-tools', 'tool-3'],
      ],
    );
  }
});

test('Figure 6-5 retains the compatibility flow and both native asynchronous flows', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutAsyncArchitecture(readFigure(directory, 5), 5, {
      rtl: dir === 'rtl',
    });
    for (const flow of [
      'compatibility',
      'work-while-waiting',
      'mid-task-update',
    ])
      assert.equal(
        (
          svg.match(
            new RegExp(`data-flow="${flow}" data-stage="[1-3]"`, 'g'),
          ) || []
        ).length,
        3,
      );
    assert.deepEqual(
      edges(svg).map(({ name }) => name),
      [
        'compatibility-1-to-2',
        'compatibility-2-to-3',
        'work-while-waiting-1-to-2',
        'work-while-waiting-2-to-3',
        'mid-task-update-1-to-2',
        'mid-task-update-2-to-3',
      ],
    );
    assert.ok(edges(svg).every((item) => item.gutter === 44));
  }
});

test('async-architecture layouts reject unsupported figures and changed source structure', () => {
  assert.throws(
    () => layoutAsyncArchitecture(readFigure('book-en', 1), 6),
    /Unsupported async-architecture figure/,
  );
  assert.throws(
    () =>
      layoutAsyncArchitecture(
        readFigure('book-en', 1).replace('<rect ', '<circle '),
        1,
      ),
    /source structure changed/,
  );
  assert.throws(
    () =>
      layoutAsyncArchitecture(
        readFigure('book-en', 5).replace(
          'viewBox="0 0 880 540"',
          'viewBox="0 0 900 540"',
        ),
        5,
      ),
    /source structure changed/,
  );
});
