import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import editions from '../src/lib/editions.json' with { type: 'json' };

const base = process.env.ASTRO_BASE;
assert.ok(
  base?.startsWith('/') && base.endsWith('/'),
  'Set ASTRO_BASE to the deployed path, including its trailing slash.',
);
const dist = fileURLToPath(new URL('../dist/', import.meta.url));
const root = fileURLToPath(new URL('../../', import.meta.url));
const origin = 'https://astro-deployment.test';
const walk = (directory) =>
  readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const path = join(directory, entry.name);
    return entry.isDirectory() ? walk(path) : [path];
  });
const files = walk(dist);
const decode = (value) =>
  value
    .replaceAll('&amp;', '&')
    .replaceAll('&quot;', '"')
    .replaceAll('&#39;', "'");
const pages = new Map(
  files
    .filter((file) => file.endsWith('.html'))
    .map((file) => [file, readFileSync(file, 'utf8')]),
);
let checked = 0;
function checkLink(value, from) {
  if (!value || /^(data:|mailto:|tel:|javascript:)/i.test(value)) return;
  const pagePath = relative(dist, from).replace(/index\.html$/, '');
  const url = new URL(decode(value), `${origin}${base}${pagePath}`);
  if (url.origin !== origin) return;
  assert.ok(
    url.pathname.startsWith(base),
    `${relative(dist, from)} escapes ASTRO_BASE: ${value}`,
  );
  let target = join(dist, decodeURIComponent(url.pathname.slice(base.length)));
  assert.ok(
    existsSync(target),
    `${relative(dist, from)} links to missing file: ${value}`,
  );
  if (statSync(target).isDirectory()) target = join(target, 'index.html');
  assert.ok(existsSync(target), `Missing page: ${value}`);
  if (url.hash && pages.has(target)) {
    const ids = [...pages.get(target).matchAll(/\bid="([^"]+)"/g)].map(
      (match) => decode(match[1]),
    );
    assert.ok(
      ids.includes(decodeURIComponent(url.hash.slice(1))),
      `Missing fragment: ${value}`,
    );
  }
  checked++;
}
for (const [file, html] of pages) {
  // Inspect tags only: teaching code blocks also contain literal href="..." text.
  for (const [tag] of html.matchAll(/<[a-z][a-z\d-]*\b[^<>]*>/gi)) {
    for (const [, value] of tag.matchAll(
      /\b(?:href|src|data-figure-light|data-figure-dark)="([^"]+)"/g,
    ))
      checkLink(value, file);
  }
}
for (const file of files.filter((file) => file.endsWith('.css'))) {
  for (const [, value] of readFileSync(file, 'utf8').matchAll(
    /url\(["']?([^\s"')]+)["']?\)/g,
  ))
    checkLink(value, file);
}
for (const [locale, edition] of Object.entries(editions)) {
  assert.ok(
    pages.has(join(dist, edition.home, 'index.html')),
    `Missing ${locale} homepage`,
  );
  for (let chapter = 1; chapter <= 10; chapter++) {
    assert.ok(
      pages.has(
        join(
          dist,
          edition.chapter.replace('chapter1', `chapter${chapter}`),
          'index.html',
        ),
      ),
      `Missing ${locale} chapter ${chapter}`,
    );
  }
  const readme =
    locale === 'he'
      ? 'README.he.md'
      : locale === 'pt-BR'
        ? 'README.ptbr.md'
        : `docs/${locale}/README.md`;
  // README links always point to the canonical deployment, including on forks.
  const url = `https://bojieli.github.io/ai-agent-book/astro${edition.home}`;
  assert.ok(
    readFileSync(join(root, readme), 'utf8').includes(`](${url})`),
    `${readme} must link to its Astro edition`,
  );
}
assert.ok(
  pages.get(join(dist, 'zh-CN/index.html')).includes(`${base}"`),
  'Chinese homepage redirect must stay under ASTRO_BASE',
);
console.log(
  `Verified ${pages.size} pages, ${checked} local URLs, and all 15 README edition links under ${base}.`,
);
