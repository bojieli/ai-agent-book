import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutVoiceArchitecture } from './voice-architecture-layout.mjs';

const expectedLabelCounts = { 6: [23], 7: [19], 8: [22], 9: [46], 10: [24] };

function readFigure(directory, figure) {
  return readFileSync(
    new URL(`../../${directory}/images/fig6-${figure}.svg`, import.meta.url),
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

test('voice architecture layouts retain all source labels and bounds in all 15 editions', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory, dir } of Object.values(editions))
    for (const figure of [6, 7, 8, 9, 10]) {
      const source = readFigure(directory, figure);
      const unchanged = source;
      const expected = extractLabels(
        source,
        `6-${figure}`,
        expectedLabelCounts[figure],
      );
      const layout = layoutVoiceArchitecture(source, figure, {
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

test('Figure 6-6 retains the ordered four-stage serial voice pipeline', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutVoiceArchitecture(readFigure(directory, 6), 6, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-pipeline-stage="[1-4]"/g) || []).length, 4);
    assert.deepEqual(
      [...svg.matchAll(/data-edge="([^"]+)"/g)].map((match) => match[1]),
      ['vad-to-asr', 'asr-to-llm', 'llm-to-tts'],
    );
    assert.equal((svg.match(/data-gutter-size="40"/g) || []).length, 3);
    assert.match(svg, /data-serial-summary="true"/);
  }
});

test('Figure 6-7 preserves timing ranges, starts, axis values, and response totals', () => {
  const expectedStages = [
    ['vad-wait', 0, 500, 800],
    ['asr', 500, 50, 200],
    ['llm-ttft', 550, 100, 500],
    ['llm-generation', 650, 100, 300],
    ['tts', 750, 200, 500],
  ];
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutVoiceArchitecture(readFigure(directory, 7), 7, {
      rtl: dir === 'rtl',
    });
    const actualStages = [
      ...svg.matchAll(
        /data-latency-stage="([^"]+)" data-start-ms="(\d+)" data-min-ms="(\d+)" data-max-ms="(\d+)"/g,
      ),
    ].map((match) => [
      match[1],
      Number(match[2]),
      Number(match[3]),
      Number(match[4]),
    ]);
    assert.deepEqual(actualStages, expectedStages, directory);
    assert.deepEqual(
      [...svg.matchAll(/data-time-tick="(\d+)"/g)].map((match) =>
        Number(match[1]),
      ),
      [0, 500, 1000, 1500, 2000],
    );
    assert.match(
      svg,
      /data-axis-min="0" data-axis-max="2300" data-best-total-ms="950" data-worst-total-ms="2300"/,
    );
    for (const kind of ['best', 'worst', 'context'])
      assert.match(svg, new RegExp(`data-response-summary="${kind}"`));
  }
});

test('Figure 6-8 preserves the queueing formula, axes, sampled trend, and milestones', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutVoiceArchitecture(readFigure(directory, 8), 8, {
      rtl: dir === 'rtl',
    });
    assert.match(
      svg,
      /data-chart="utilization-latency" data-formula="S\/\(1-rho\)" data-idle-latency-s="1" data-x-min="0" data-x-max="1" data-y-min="0" data-y-max="12"/,
    );
    assert.deepEqual(
      [...svg.matchAll(/data-x-tick="([\d.]+)"/g)].map((match) =>
        Number(match[1]),
      ),
      [0, 0.2, 0.4, 0.6, 0.8, 1],
    );
    assert.deepEqual(
      [...svg.matchAll(/data-y-grid="(\d+)"/g)].map((match) =>
        Number(match[1]),
      ),
      [0, 2, 4, 6, 8, 10, 12],
    );
    const series = svg.match(
      /data-series="queue-latency" data-samples="38" data-overflow-rho="([\d.]+)" d="([^"]+)"/,
    );
    assert.ok(series, directory);
    assert.equal(Number(series[1]), 11 / 12);
    const curvePoints = [...series[2].matchAll(/[ML]([\d.]+) ([\d.]+)/g)].map(
      (match) => [Number(match[1]), Number(match[2])],
    );
    assert.equal(curvePoints.length, 38);
    assert.deepEqual(curvePoints.at(-1), [698.33, 72]);
    assert.notEqual(curvePoints.at(-2)[1], curvePoints.at(-1)[1]);

    const milestones = [
      ...svg.matchAll(
        /data-curve-point="([^"]+)" data-rho="([\d.]+)" data-latency-s="([\d.]+)"([^>]*)/g,
      ),
    ].map((match) => [match[1], Number(match[2]), Number(match[3]), match[4]]);
    assert.deepEqual(
      milestones.map((item) => item.slice(0, 3)),
      [
        ['saturation', 11 / 12, 12],
        ['unacceptable', 0.8, 5],
        ['tolerance', 0.5, 2],
      ],
      directory,
    );
    assert.match(milestones[0][3], /data-overflow-boundary="y-max"/);
    assert.deepEqual(
      [
        ...svg.matchAll(
          /data-annotation-line="([^"]+)" data-route="right-elbow"/g,
        ),
      ].map((match) => match[1]),
      ['saturation', 'unacceptable', 'tolerance'],
    );
  }
});

test('Figure 6-9 keeps product evidence, limitation causes, and architecture rows grouped', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutVoiceArchitecture(readFigure(directory, 9), 9, {
      rtl: dir === 'rtl',
    });
    assert.deepEqual(
      [...svg.matchAll(/data-realtime-product="([^"]+)"/g)].map(
        (match) => match[1],
      ),
      ['openai-realtime', 'gemini-live', 'qwen3-omni', 'step-audio-2'],
    );
    assert.equal((svg.match(/data-common-limitation=/g) || []).length, 3);
    assert.equal((svg.match(/data-architecture-row="[1-5]"/g) || []).length, 5);
  }
});

test('Figure 6-10 keeps both parallel thought paths connected to the experience', () => {
  for (const { directory, dir } of Object.values(editions)) {
    const svg = layoutVoiceArchitecture(readFigure(directory, 10), 10, {
      rtl: dir === 'rtl',
    });
    assert.equal((svg.match(/data-thought-path=/g) || []).length, 2);
    assert.deepEqual(
      [...svg.matchAll(/data-edge="([^"]+)"/g)].map((match) => match[1]),
      [
        'input-to-parallel-thinking',
        'fast-thinking-to-experience',
        'slow-thinking-to-experience',
      ],
    );
    assert.equal((svg.match(/data-issue=/g) || []).length, 2);
    assert.equal((svg.match(/data-conclusion=/g) || []).length, 2);
    assert.equal((svg.match(/data-card-gap-start="8"/g) || []).length, 3);
    assert.equal((svg.match(/data-card-gap-end="8"/g) || []).length, 3);
  }
});

test('voice architecture layouts reject source drift and unsupported figures', () => {
  for (const figure of [6, 7, 8, 9, 10]) {
    const source = readFigure('book-en', figure);
    assert.throws(
      () =>
        layoutVoiceArchitecture(source.replace(/<rect\b[^>]*\/>/, ''), figure),
      new RegExp(`Figure 6-${figure} source structure changed`),
    );
    assert.throws(
      () =>
        layoutVoiceArchitecture(
          source.replace('</svg>', '<text>unexpected</text></svg>'),
          figure,
        ),
      new RegExp(`Figure 6-${figure}`),
    );
  }
  assert.throws(
    () => layoutVoiceArchitecture(readFigure('book-en', 6), 5),
    /Unsupported voice architecture figure/,
  );
});
