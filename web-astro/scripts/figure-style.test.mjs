import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutImprovementCycle } from './improvement-cycle-figure.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { styleFigure } from './figure-style.mjs';
import { layoutEvaluationEnvironments } from './evaluation-environments-figure.mjs';
import { layoutLlmJudge } from './llm-judge-figure.mjs';
import { layoutObservability } from './observability-figure.mjs';

const workflows = {
  2: layoutEvaluationEnvironments,
  5: layoutLlmJudge,
  7: layoutObservability,
  8: layoutImprovementCycle,
};

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

test('Chapter 7 workflow layouts preserve labels and canvas bounds across all editions', () => {
  for (const { directory, dir } of Object.values(editions))
    for (const [n, layout] of Object.entries(workflows)) {
      const source = readFileSync(
        new URL(`../../${directory}/images/fig7-${n}.svg`, import.meta.url),
        'utf8',
      );
      const rendered = layout(source, { rtl: dir === 'rtl' });
      const normalized = source.replace(
        /<text\b([^>]*)\/>/g,
        '<text$1></text>',
      );
      const expected = [
        ...normalized.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
      ].map((m) =>
        m[1]
          .replace(/<tspan\b[^>]*>/g, '')
          .replace(/<\/tspan>/g, ' ')
          .replace(/\s+/g, ' ')
          .trim(),
      );
      const actual = [
        ...rendered.matchAll(/data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
      ].sort((a, b) => +a[1] - b[1]);
      assert.deepEqual(
        actual.map((m) => [+m[1], m[2]]),
        expected.map((v, i) => [i, v]),
        `${directory} 7-${n}`,
      );
      const h = +rendered.match(/viewBox="0 0 1000 ([\d.]+)"/)[1];
      for (const m of rendered.matchAll(
        /<foreignObject x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(+m[1] + +m[3] <= 1000);
        assert.ok(+m[2] + +m[4] <= h);
      }
      assert.doesNotMatch(
        rendered,
        /NaN|undefined|font-size:(?:[0-9]|1[0-3])px/,
      );
      assert.equal(
        (rendered.match(/<g\b/g) || []).length,
        (rendered.match(/<\/g>/g) || []).length,
      );
      assert.throws(
        () => layout(normalized.replace(/<text\b[\s\S]*?<\/text>/, '')),
        /source labels changed/,
      );
    }
});
const en = (n) =>
  readFileSync(
    new URL(`../../book-en/images/fig7-${n}.svg`, import.meta.url),
    'utf8',
  );
test('Evaluation environments keep both interaction directions and independent reward pipelines', () => {
  const out = layoutEvaluationEnvironments(en(2));
  assert.equal((out.match(/marker-end=/g) || []).length, 8);
  for (const name of [
    'user-agent',
    'agent-user',
    'tool-reward',
    'interaction-reward',
    'double-verification',
  ])
    assert.ok(out.includes(`data-edge="${name}"`));
  const forward = out.match(
    /data-edge="user-agent"><path d="M([\d.]+) ([\d.]+) L([\d.]+) ([\d.]+)"/,
  );
  const reverse = out.match(
    /data-edge="agent-user"><path d="M([\d.]+) ([\d.]+) L([\d.]+) ([\d.]+)"/,
  );
  assert.ok(+forward[3] - +forward[1] >= 48);
  assert.ok(+reverse[1] - +reverse[3] >= 48);
  assert.notEqual(forward[2], reverse[2]);
});
test('LLM judging joins three evidence sources and preserves dimension-score associations', () => {
  const out = layoutLlmJudge(en(5));
  assert.equal((out.match(/data-panel="evidence-/g) || []).length, 3);
  assert.equal((out.match(/data-score-row=/g) || []).length, 4);
  assert.equal((out.match(/marker-end=/g) || []).length, 2);
  assert.match(out, /data-input-bus="true"/);
  for (const [i, score] of ['4/4', '3/4', 'PASS', '4/4'].entries()) {
    const block = out.match(
      new RegExp(`data-score-row="${i}">([\\s\\S]*?)<\\/g>`),
    )[1];
    assert.ok(block.includes(score));
  }
});
test('Observability retains two nested tool operations and a separate closed-loop footer', () => {
  const out = layoutObservability(en(7));
  assert.equal((out.match(/data-trace-depth="1"/g) || []).length, 2);
  assert.equal((out.match(/data-trace-depth="0"/g) || []).length, 5);
  assert.equal((out.match(/data-panel="dashboard-/g) || []).length, 3);
  assert.match(out, /data-panel="closed-loop"/);
});
test('Improvement cycle preserves four experiments and returns iteration to hypothesis', () => {
  const out = layoutImprovementCycle(en(8));
  assert.equal((out.match(/data-panel="experiment-/g) || []).length, 4);
  assert.equal((out.match(/marker-end=/g) || []).length, 5);
  assert.match(
    out,
    /data-edge="iteration-hypothesis"><path d="M944 [\d.]+ H976 V[\d.]+ H944"/,
  );
  for (const value of ['88%', '94%', '0%→75%', '0%→80%', '0%→70%', '17%→52%'])
    assert.ok(out.includes(value));
});
