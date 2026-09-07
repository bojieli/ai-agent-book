import editions from '../src/lib/editions.json' with { type: 'json' };
import { layoutAgentLoop } from './agent-loop-figure.mjs';
import { readFile, mkdir, copyFile, writeFile } from 'node:fs/promises';
const root = new URL('../../', import.meta.url);
let count = 0;
for (const { directory, suffix } of Object.values(editions)) {
  const markdown = await readFile(
    new URL(`${directory}/chapter1${suffix}.md`, root),
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
    if (image === 'images/fig1-1.svg') {
      await writeFile(
        destination,
        layoutAgentLoop(await readFile(original, 'utf8')),
      );
    } else {
      await copyFile(original, destination);
    }
    count++;
  }
}
console.log(`Prepared ${count} chapter figures from the original sources.`);
