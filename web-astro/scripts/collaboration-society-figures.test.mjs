import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { styleFigure } from './figure-style.mjs';
import {
  layoutAITownArchitecture,
  layoutMetaGPTCollaboration,
  layoutVoiceWerewolfSystem,
} from './collaboration-society-figures.mjs';

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
  ].map((match) => ({
    index: Number(match[1]),
    value: normalize(match[2]),
  }));
const attributeNumbers = (source, selector, attribute) =>
  [
    ...source.matchAll(
      new RegExp(
        `<rect\\b[^>]*${selector}="[^"]+"[^>]*\\s${attribute}="(\\d+)"`,
        'g',
      ),
    ),
  ].map((match) => Number(match[1]));

const figures = {
  9: { layout: layoutMetaGPTCollaboration, labels: 47, canvas: '1480 2080' },
  10: { layout: layoutAITownArchitecture, labels: 43, canvas: '1320 2440' },
  11: { layout: layoutVoiceWerewolfSystem, labels: 48, canvas: '1320 2520' },
};

test('Chapter 10 collaboration and society layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [
      number,
      { layout, labels: expectedCount, canvas },
    ] of Object.entries(figures)) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig10-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = sourceLabels(source);
      assert.equal(
        expected.length,
        expectedCount,
        `${directory} Figure 10-${number}`,
      );

      const layoutSvg = layout(source);
      assert.match(layoutSvg, new RegExp(`viewBox="0 0 ${canvas}"`));
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

test('Figure 10-9 preserves the SOP pipeline, artifacts, and QA feedback relationship', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig10-9.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutMetaGPTCollaboration(source);

  assert.equal((layout.match(/data-role="[^"]+"/g) || []).length, 5);
  assert.deepEqual(
    [...layout.matchAll(/data-flow-position="(\d+)"/g)].map((match) =>
      Number(match[1]),
    ),
    [1, 2, 3, 4, 5],
  );
  assert.deepEqual(
    attributeNumbers(layout, 'data-role-card', 'y'),
    [30, 310, 590, 870, 1150],
  );
  assert.equal((layout.match(/data-artifact-for="[^"]+"/g) || []).length, 5);
  assert.equal((layout.match(/data-edge="[^"]+"/g) || []).length, 5);
  assert.match(layout, /data-edge="qa-to-engineer"[^>]*stroke-dasharray="9 6"/);
  assert.match(layout, /data-shared-directory-card="true"[^>]*y="1430"/);
  assert.equal(
    (layout.match(/data-design-principle="[^"]+"/g) || []).length,
    4,
  );
});

test('Figure 10-10 keeps memory, reflection, and planning in causal order before emergence', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig10-10.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutAITownArchitecture(source);

  assert.deepEqual(
    attributeNumbers(layout, 'data-component-card', 'y'),
    [220, 790, 1300],
  );
  assert.equal((layout.match(/data-memory-entry="\d+"/g) || []).length, 5);
  assert.equal((layout.match(/data-reflection-entry="\d+"/g) || []).length, 4);
  assert.equal((layout.match(/data-plan-step="\d+"/g) || []).length, 6);
  assert.match(layout, /data-edge="memory-to-reflection" d="M 660 710 V 780"/);
  assert.match(
    layout,
    /data-edge="reflection-to-planning" d="M 660 1220 V 1290"/,
  );
  assert.ok(
    layout.indexOf('data-component-card="planning"') <
      layout.indexOf('data-emergent-behavior="true"'),
  );
  assert.equal((layout.match(/data-behavior="[^"]+"/g) || []).length, 4);
});

test('Figure 10-11 preserves judge fan-out, role-filtered context, and voice phases', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig10-11.svg', import.meta.url),
    'utf8',
  );
  const layout = layoutVoiceWerewolfSystem(source);

  assert.match(layout, /data-controller-card="judge"[^>]*y="30"/);
  assert.deepEqual(
    attributeNumbers(layout, 'data-role-card', 'x'),
    [180, 180, 180, 180, 180],
  );
  assert.deepEqual(
    attributeNumbers(layout, 'data-role-card', 'y'),
    [280, 530, 780, 1030, 1280],
  );
  assert.equal((layout.match(/data-edge="judge-to-[^"]+"/g) || []).length, 5);
  assert.equal(
    (layout.match(/data-private-knowledge-for="[^"]+"/g) || []).length,
    3,
  );
  for (const index of [7, 12, 17])
    assert.match(
      layout,
      new RegExp(
        `<foreignObject\\b[^>]*data-label="${index}"[^>]*width="232" height="66"`,
      ),
    );
  assert.equal((layout.match(/data-access-row="\d+"/g) || []).length, 4);
  assert.equal((layout.match(/data-voice-phase="[^"]+"/g) || []).length, 4);
  assert.ok(
    layout.indexOf('data-role-card="villager"') <
      layout.indexOf('data-information-access="role-filtered"'),
  );
  assert.ok(
    layout.indexOf('data-information-access="role-filtered"') <
      layout.indexOf('data-voice-loop="true"'),
  );
});

test('Chapter 10 layouts reserve readable wrapping areas and keep arrows in gutters', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const source = readFileSync(
      new URL(`../../book-en/images/fig10-${number}.svg`, import.meta.url),
      'utf8',
    );
    const result = layout(source);
    const sizes = [...result.matchAll(/font-size:(\d+)px/g)].map((match) =>
      Number(match[1]),
    );
    const boxes = [
      ...result.matchAll(
        /<foreignObject\b[^>]*width="(\d+)"[^>]*height="(\d+)"/g,
      ),
    ].map((match) => ({ width: Number(match[1]), height: Number(match[2]) }));
    assert.ok(sizes.length > 0);
    assert.ok(sizes.every((size) => size >= 17));
    assert.ok(boxes.every(({ width, height }) => width >= 150 && height >= 34));
    assert.doesNotMatch(result, /<text\b/);
    assert.equal(
      (result.match(/marker-end="url\(#collaboration-society-arrow\)"/g) || [])
        .length,
      (result.match(/data-edge="[^"]+"/g) || []).length,
    );
    assert.equal(
      (result.match(/overflow-wrap:anywhere/g) || []).length,
      (result.match(/<foreignObject\b/g) || []).length,
    );
  }
});

test('Chapter 10 layouts reject source structure drift', () => {
  for (const [number, { layout }] of Object.entries(figures)) {
    const source = readFileSync(
      new URL(`../../book-en/images/fig10-${number}.svg`, import.meta.url),
      'utf8',
    );
    assert.throws(
      () => layout(source.replace(/<text\b[\s\S]*?<\/text>/, '')),
      new RegExp(`Figure 10-${number} source structure changed`),
    );
    assert.throws(
      () => layout(source.replace(/<rect\b[^>]*\/>/, '')),
      new RegExp(`Figure 10-${number} source structure changed`),
    );
  }
});
