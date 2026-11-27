import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';
import { figurePaths } from '../src/lib/figure-paths.mjs';
import { styleFigure } from './figure-style.mjs';

test('the Russian reader serves the revised agent loop intact in both themes', () => {
  const root = new URL('../../', import.meta.url);
  const chapter = readFileSync(new URL('book-ru/chapter1.md', root), 'utf8');
  const image = 'images/revised/fig1-1.svg';
  assert.ok(chapter.includes(`](${image})`));
  const paths = figurePaths('book-ru', image);
  const source = readFileSync(new URL(`book-ru/${image}`, root), 'utf8');
  for (const theme of ['light', 'dark']) {
    const variant = readFileSync(new URL(`web-astro/dist${paths[theme]}`, root), 'utf8');
    assert.equal(variant, styleFigure(source, theme));
  }
});
