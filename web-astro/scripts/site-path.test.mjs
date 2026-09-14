import test from 'node:test';
import assert from 'node:assert/strict';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkRehype from 'remark-rehype';
import rehypeStringify from 'rehype-stringify';
import { withBase } from '../src/lib/site-path.mjs';
import { bookMarkdown } from '../src/lib/book-markdown.mjs';
import { machineLanguage } from '../src/lib/machine-language.ts';

const base = '/ai-agent-book/astro/';
test('site paths work at the domain root and below a Pages project path', () => {
  assert.equal(withBase('/book-en/chapter1/'), '/book-en/chapter1/');
  assert.equal(
    withBase('/book-en/chapter1/?resume=1#tools', base),
    `${base}book-en/chapter1/?resume=1#tools`,
  );
  assert.equal(withBase('/', base), base);
  for (const value of [
    '#contents',
    'https://example.com/book/',
    '//example.com/image.svg',
  ]) {
    assert.equal(withBase(value, base), value);
  }
});
test('Markdown applies the deployment base to chapters, figures, and source figures', async () => {
  const result = await unified()
    .use(remarkParse)
    .use(bookMarkdown, { base })
    .use(remarkRehype)
    .use(rehypeStringify)
    .process({
      path: '/book-en/chapter1.md',
      value:
        '# Chapter 1\n\n[Next](chapter2.md#context)\n\n![Agent](images/fig1-1.svg)\n\n[External](https://example.com/)\n',
    });
  const html = String(result);
  assert.ok(html.includes(`href="${base}book-en/chapter2/#context"`));
  assert.ok(
    html.includes(`src="${base}figures/book/book-en/fig1-1-light.svg"`),
  );
  assert.ok(
    html.includes(
      `data-figure-dark="${base}figures/book/book-en/fig1-1-dark.svg"`,
    ),
  );
  assert.ok(html.includes(`href="${base}book-en/images/fig1-1.svg"`));
  assert.ok(html.includes('href="https://example.com/"'));
});
test('machine translation recognizes only English routes within the deployment', () => {
  for (const path of ['en/', 'book-en/chapter2/']) {
    assert.equal(
      machineLanguage(
        new URL(`https://example.com${base}${path}?translate=fr`),
        base,
      )?.locale,
      'fr',
    );
  }
  for (const path of ['/en/', '/book-en/chapter1/', `${base}book/chapter1/`]) {
    assert.equal(
      machineLanguage(new URL(`https://example.com${path}?translate=fr`), base),
      undefined,
    );
  }
});
