import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import {
  layoutEvaluationOverview,
  layoutDualControl,
  layoutEmbodiedEvaluation,
} from './evaluation-overview-figures.mjs';
import {
  layoutVerificationSpectrum,
  layoutSimulationFidelity,
} from './evaluation-spectrum-figures.mjs';
import { layoutPairwise } from './pairwise-figure.mjs';
import { layoutImprovementCycle } from './improvement-cycle-figure.mjs';
import { styleFigure } from './figure-style.mjs';

const layouts = {
  1: layoutEvaluationOverview,
  3: layoutDualControl,
  4: layoutVerificationSpectrum,
  6: layoutPairwise,
  8: layoutImprovementCycle,
  9: layoutSimulationFidelity,
  10: layoutEmbodiedEvaluation,
};
const normalize = (s) =>
  s
    .replace(/<\/?tspan\b[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();

test('Remaining Chapter 7 web figures retain every localized label in both themes', () => {
  for (const { directory } of Object.values(editions))
    for (const [number, layout] of Object.entries(layouts)) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig7-${number}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const expected = [
        ...source
          .replace(/<text\b([^>]*)\/>/g, '<text$1></text>')
          .matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g),
      ]
        .map((m) => normalize(m[1]))
        .filter(Boolean)
        .sort();
      for (const theme of ['light', 'dark']) {
        const rendered = styleFigure(layout(source), theme);
        const actual = [
          ...rendered.matchAll(
            /<foreignObject\b([^>]*)>([\s\S]*?)<\/foreignObject>/g,
          ),
        ]
          .flatMap((m) =>
            m[1].includes('data-label=')
              ? [m[2].replace(/<[^>]+>/g, '')]
              : [
                  ...m[2].matchAll(
                    /<div\b[^>]*data-label="\d+"[^>]*>([\s\S]*?)<\/div>/g,
                  ),
                ].map((d) => d[1]),
          )
          .map(normalize)
          .filter(Boolean)
          .sort();
        assert.deepEqual(
          actual,
          expected,
          `${directory} Figure 7-${number} ${theme}`,
        );
      }
    }
});

test('The fidelity plot preserves source point positions and trend geometry', () => {
  for (const { directory } of Object.values(editions)) {
    const source = readFileSync(
      new URL(`../../${directory}/images/fig7-9.svg`, import.meta.url),
      'utf8',
    );
    const result = layoutSimulationFidelity(source);
    const points = (s) =>
      [...s.matchAll(/<circle\b[^>]*cx="([^"]+)"[^>]*cy="([^"]+)"/g)].map(
        (m) => [Number(m[1]), Number(m[2])],
      );
    assert.deepEqual(points(result).slice(0, 6), points(source));
    const trend = source.match(/<line\b[^>]*stroke-dasharray="8,4"[^>]*\/>/)[0];
    assert.ok(result.includes(trend));
  }
});
