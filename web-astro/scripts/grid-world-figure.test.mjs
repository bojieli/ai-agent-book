import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutGridWorld } from './grid-world-figure.mjs';
import { styleFigure } from './figure-style.mjs';

test('Q-learning grid retains data shading, wall contrast, and every localized label', () => {
  for (const { directory } of Object.values(editions)) {
    const source = readFileSync(
      new URL(`../../${directory}/images/fig8-3.svg`, import.meta.url),
      'utf8',
    );
    const layout = layoutGridWorld(source);
    const grid = layout.match(
      /<g data-preserve-colors="true">([\s\S]*?)<\/g>/,
    )[1];
    assert.ok(source.includes(grid), directory);
    assert.equal((grid.match(/<rect\b/g) || []).length, 25);
    const normalize = (s) =>
      s
        .replace(/<[^>]+>/g, ' ')
        .replace(/\s+/g, ' ')
        .trim();
    const expected = [...source.matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)]
      .map((m) => normalize(m[1]))
      .sort();
    for (const theme of ['light', 'dark']) {
      const rendered = styleFigure(layout, theme);
      assert.ok(rendered.includes(grid), `${directory} ${theme} grid changed`);
      const actual = [
        ...rendered.matchAll(
          /<text\b[^>]*>([\s\S]*?)<\/text>|<foreignObject\b[^>]*>([\s\S]*?)<\/foreignObject>/g,
        ),
      ]
        .map((m) => normalize(m[1] ?? m[2]))
        .sort();
      assert.deepEqual(actual, expected, `${directory} ${theme}`);
    }
  }
});
