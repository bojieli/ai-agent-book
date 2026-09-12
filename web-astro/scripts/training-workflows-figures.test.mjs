import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import {
  layoutSftPipeline,
  layoutToolRl,
} from './training-workflows-figures.mjs';
import { styleFigure } from './figure-style.mjs';

const layouts = {
  10: layoutSftPipeline,
  16: layoutToolRl,
};
const normalize = (value) =>
  value
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

function textLabels(svg) {
  return [
    ...svg
      .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
      .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
  ]
    .map((match) => normalize(match[1]))
    .filter(Boolean);
}

function renderedLabels(svg) {
  return [
    ...svg.matchAll(
      /<foreignObject\b[^>]*data-label="\d+"[^>]*>([\s\S]*?)<\/foreignObject>/g,
    ),
  ]
    .map((match) => normalize(match[1].replace(/<[^>]+>/g, '')))
    .filter(Boolean);
}

function labelHeight(svg, index) {
  const tag = svg.match(
    new RegExp(`<foreignObject\\b[^>]*data-label="${index}"[^>]*>`),
  )?.[0];
  assert.ok(tag, `missing label ${index}`);
  return Number(tag.match(/\bheight="([^"]+)"/)?.[1]);
}

test('Chapter 8 training workflow layouts retain every localized label in both themes', () => {
  assert.equal(Object.keys(editions).length, 15);
  for (const { directory } of Object.values(editions))
    for (const [number, layout] of Object.entries(layouts)) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig8-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = textLabels(source).sort();
      for (const theme of ['light', 'dark']) {
        const rendered = styleFigure(layout(source), theme);
        assert.deepEqual(
          renderedLabels(rendered).sort(),
          expected,
          `${directory} Figure 8-${number} ${theme}`,
        );
      }
    }
});

test('Training workflow layouts provide roomy wrapped cards and explicit connectors', () => {
  const sftSource = readFileSync(
    new URL('../../book-en/images/fig8-10.svg', import.meta.url),
    'utf8',
  );
  const toolSource = readFileSync(
    new URL('../../book-en/images/fig8-16.svg', import.meta.url),
    'utf8',
  );
  const sft = layoutSftPipeline(sftSource);
  const tool = layoutToolRl(toolSource);

  for (const rendered of [sft, tool]) {
    assert.match(rendered, /viewBox="0 0 1120 \d+"/);
    assert.equal(
      [...rendered.matchAll(/<foreignObject\b/g)].length,
      [...rendered.matchAll(/<div dir="auto"/g)].length,
    );
    const fontSizes = [...rendered.matchAll(/font-size:(\d+)px/g)].map(
      (match) => Number(match[1]),
    );
    assert.ok(fontSizes.every((size) => size >= 16));
  }
  assert.equal(
    [...sft.matchAll(/marker-end="url\(#training-arrow\)"/g)].length,
    2,
  );
  assert.equal(
    [...tool.matchAll(/marker-end="url\(#training-arrow\)"/g)].length,
    5,
  );
  for (const index of [0, 5, 10]) assert.ok(labelHeight(sft, index) >= 80);
  for (const index of [0, 3, 5, 7]) assert.ok(labelHeight(tool, index) >= 80);
});

test('Layout guards reject changed source label counts', () => {
  const sftSource = readFileSync(
    new URL('../../book-en/images/fig8-10.svg', import.meta.url),
    'utf8',
  );
  const toolSource = readFileSync(
    new URL('../../book-en/images/fig8-16.svg', import.meta.url),
    'utf8',
  );
  assert.throws(
    () =>
      layoutSftPipeline(sftSource.replace('</svg>', '<text>x</text></svg>')),
    /source structure changed/,
  );
  assert.throws(
    () =>
      layoutToolRl(
        toolSource.replace('</svg>', '<text>x</text><text>y</text></svg>'),
      ),
    /source structure changed/,
  );
});
