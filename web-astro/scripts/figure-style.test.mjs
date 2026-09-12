import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { styleFigure } from './figure-style.mjs';
import { layoutEvaluationEnvironments } from './evaluation-environments-figure.mjs';
import { layoutLlmJudge } from './llm-judge-figure.mjs';
import { layoutObservability } from './observability-figure.mjs';

test('The attention matrix keeps its data colors and numeric labels in both themes', () => {
  const source = readFileSync(
    new URL('../../book-en/images/fig2-6.svg', import.meta.url),
    'utf8',
  );
  const data = source.match(
    /<rect\b[^>]*width="64"[^>]*height="64"[^>]*\/>|<text\b[^>]*>\d\.\d{2}<\/text>/g,
  );
  assert.equal(data.length, 26);
  for (const theme of ['light', 'dark']) {
    const rendered = styleFigure(source, theme, { preserveHeatmap: true });
    for (const cell of data) assert.ok(rendered.includes(cell));
    assert.deepEqual(
      [...rendered.matchAll(/<text\b[^>]*>(.*?)<\/text>/g)].map((x) => x[1]),
      [...source.matchAll(/<text\b[^>]*>(.*?)<\/text>/g)].map((x) => x[1]),
    );
  }
});

test('Figure 7-2 separates translated headings and interaction arrows', () => {
  for (const directory of ['book-en', 'book-vi', 'book-ar']) {
    const source = readFileSync(
      new URL(`../../${directory}/images/fig7-2.svg`, import.meta.url),
      'utf8',
    );
    const rendered = layoutEvaluationEnvironments(source);
    assert.match(rendered, /viewBox="0 0 1120 690"/);
    assert.equal((rendered.match(/data-label=/g) || []).length, 23);
    assert.equal((rendered.match(/stroke-dasharray="8,6"/g) || []).length, 2);
    assert.match(rendered, /x1="815" y1="117" x2="855" y2="117"/);
    assert.match(rendered, /x1="855" y1="139" x2="815" y2="139"/);
    assert.ok(!rendered.includes('<tspan'));
  }
});

test('Figure 7-5 consolidates evidence flow and preserves every label', () => {
  for (const directory of ['book-en', 'book-vi', 'book-ar']) {
    const source = readFileSync(
      new URL(`../../${directory}/images/fig7-5.svg`, import.meta.url),
      'utf8',
    );
    const rendered = layoutLlmJudge(source);
    assert.match(rendered, /viewBox="0 0 1120 820"/);
    assert.equal((rendered.match(/data-label=/g) || []).length, 35);
    assert.equal((rendered.match(/stroke-dasharray="8,6"/g) || []).length, 1);
    assert.match(rendered, /x1="195" y1="280" x2="925" y2="280"/);
    assert.equal(
      (rendered.match(/marker-end="url\(#arrowhead\)"/g) || []).length,
      2,
    );
    assert.ok(!rendered.includes('<tspan'));
  }
});

test('Figure 7-7 gives the trace a nested timeline and the loop its own row', () => {
  for (const directory of ['book-en', 'book-vi', 'book-ar']) {
    const source = readFileSync(
      new URL(`../../${directory}/images/fig7-7.svg`, import.meta.url),
      'utf8',
    );
    const rendered = layoutObservability(source);
    assert.match(rendered, /viewBox="0 0 1120 820"/);
    assert.equal((rendered.match(/data-label=/g) || []).length, 26);
    assert.equal((rendered.match(/stroke-dasharray="8,6"/g) || []).length, 2);
    assert.match(rendered, /x1="85" y1="127" x2="85" y2="615"/);
    assert.match(rendered, /x="30" y="725" width="1060" height="75"/);
    assert.ok(!rendered.includes('<tspan'));
  }
});
