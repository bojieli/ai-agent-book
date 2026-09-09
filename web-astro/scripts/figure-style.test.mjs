import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { styleFigure } from './figure-style.mjs';

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
