import { availableChapters } from '../src/lib/available-chapters.mjs';
import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutToolDiscovery } from './tool-discovery-figure.mjs';
import { layoutContextWindow } from './context-window-figure.mjs';
import { layoutAgentLoop } from './agent-loop-figure.mjs';
import { styleFigure, frameRaster } from './figure-style.mjs';
import { figurePaths } from '../src/lib/figure-paths.mjs';
import { readFile, mkdir, copyFile, writeFile } from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
let count = 0;
for (const { directory, suffix } of Object.values(editions)) {
  for (const chapterNumber of availableChapters) {
    const markdown = await readFile(
      new URL(`${directory}/chapter${chapterNumber}${suffix}.md`, root),
      'utf8',
    );
    const images = new Set(
      [...markdown.matchAll(/!\[[^\]]*\]\((images\/[^)]+)\)/g)].map(
        (match) => match[1],
      ),
    );
    for (const image of images) {
      const destination = new URL(
        `../public/${directory}/${image}`,
        import.meta.url,
      );
      await mkdir(new URL('./', destination), { recursive: true });
      const original = new URL(`${directory}/${image}`, root);
      // The original URL always serves the untouched source file.
      await copyFile(original, destination);
      const bytes = await readFile(original);
      let vector;
      const englishReplacement =
        directory === 'book-en' &&
        /^images\/fig2-(7|9|10|12|13|14|15|16|17)\.(svg|png)$/.exec(image);
      if (englishReplacement) {
        vector = await readFile(
          new URL(
            `../public/figures/chapter2-en/fig2-${englishReplacement[1]}-web.svg`,
            import.meta.url,
          ),
          'utf8',
        );
      } else if (image === 'images/fig1-1.svg')
        vector = layoutAgentLoop(bytes.toString());
      else if (image === 'images/fig2-1.svg')
        vector = layoutContextWindow(bytes.toString());
      else if (image === 'images/fig4-4.svg')
        vector = layoutToolDiscovery(bytes.toString(), {
          rtl: ['book-ar', 'book-he'].includes(directory),
        });
      else if (image.endsWith('.svg')) vector = bytes.toString();
      // The source's bottom banner extends past y=600. Add breathing room
      // to the web canvas without changing labels, geometry, or the raw SVG.
      if (image === 'images/fig5-1.svg')
        vector = vector.replace(
          /viewBox="0 40 980 (560|568)" width="980" height="\1"/,
          'viewBox="0 40 980 580" width="980" height="580"',
        );
      const paths = figurePaths(directory, image);
      for (const theme of ['light', 'dark']) {
        const target = new URL(`../public${paths[theme]}`, import.meta.url);
        await mkdir(new URL('./', target), { recursive: true });
        // Chapter 1/2 raster figures are PNGs; read dimensions from their IHDR.
        if (
          !vector &&
          !bytes
            .subarray(0, 8)
            .equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
        )
          throw new Error(`Unsupported raster figure: ${image}`);
        await writeFile(
          target,
          vector
            ? styleFigure(vector, theme, {
                preserveHeatmap: image === 'images/fig2-6.svg',
              })
            : frameRaster(
                bytes,
                'image/png',
                bytes.readUInt32BE(16),
                bytes.readUInt32BE(20),
                theme,
              ),
        );
      }
      count++;
    }
  }
}
console.log(`Prepared ${count} chapter figures from the original sources.`);
