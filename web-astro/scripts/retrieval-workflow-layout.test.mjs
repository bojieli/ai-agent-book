import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { extractLabels } from './chapter3-figure-kit.mjs';
import { layoutRetrievalWorkflow } from './retrieval-workflow-layout.mjs';
const editions = JSON.parse(
  readFileSync(new URL('../src/lib/editions.json', import.meta.url)),
);

test('Workflow typography preserves translated content and readable text across all editions', () => {
  for (const { directory } of Object.values(editions))
    for (const figure of [13, 14, 15]) {
      const source = readFileSync(
        new URL(
          `../../${directory}/images/fig3-${figure}.svg`,
          import.meta.url,
        ),
        'utf8',
      );
      const svg = layoutRetrievalWorkflow(source, figure, {
        rtl: ['book-ar', 'book-he'].includes(directory),
      });
      const labels = extractLabels(source, figure, [18, 19, 20, 21, 23]);
      const rendered = [
        ...svg.matchAll(/data-source-label="(\d+)">([\s\S]*?)<\/span>/g),
      ].sort((a, b) => Number(a[1]) - Number(b[1]));
      const expected = labels
        .map((text, id) => [id, text])
        .filter(([id]) => figure !== 14 || id !== 10);
      assert.deepEqual(
        rendered.map((m) => [Number(m[1]), m[2]]),
        expected,
        `${directory} 3-${figure}`,
      );
      assert.equal(
        (svg.match(/marker-end=/g) || []).length,
        { 13: 9, 14: 4, 15: 5 }[figure],
      );
      assert.ok(
        [...svg.matchAll(/font-size:([\d.]+)px/g)].every(
          (m) => Number(m[1]) >= 14,
        ),
      );
      assert.doesNotMatch(svg, /NaN|undefined/);
      const cards = [
        ...svg.matchAll(
          /<rect x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
        ),
      ]
        .map(([, x, y, width, height]) => ({
          x: +x,
          y: +y,
          width: +width,
          height: +height,
        }))
        .filter((r) => r.width < 400);
      for (const [, d] of svg.matchAll(/<path d="([^"]+)"[^>]*marker-end=/g)) {
        let x, y;
        for (const [, command, values] of d.matchAll(/([MLHV])([\d. ]+)/g)) {
          const coords = values.trim().split(/\s+/).map(Number);
          if (command === 'M') {
            [x, y] = coords;
            continue;
          }
          const nx = command === 'V' ? x : coords[0],
            ny = command === 'H' ? y : command === 'V' ? coords[0] : coords[1];
          for (const r of cards) {
            const crosses =
              y === ny
                ? y > r.y &&
                  y < r.y + r.height &&
                  Math.max(x, nx) > r.x &&
                  Math.min(x, nx) < r.x + r.width
                : x === nx &&
                  x > r.x &&
                  x < r.x + r.width &&
                  Math.max(y, ny) > r.y &&
                  Math.min(y, ny) < r.y + r.height;
            assert.ok(
              !crosses,
              `${directory} 3-${figure}: connector crosses a card`,
            );
          }
          [x, y] = [nx, ny];
        }
      }
      const [, w, h] = svg.match(/viewBox="0 0 (\d+) (\d+)"/);
      for (const [, x, y, width, height] of svg.matchAll(
        /<foreignObject x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)"/g,
      )) {
        assert.ok(
          +x + +width <= +w && +y + +height <= +h,
          `${directory} 3-${figure}: label outside canvas`,
        );
      }
    }
});
