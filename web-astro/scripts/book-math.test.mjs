import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { unified } from 'unified';
import remarkParse from 'remark-parse';
import remarkMath from 'remark-math';
import remarkRehype from 'remark-rehype';
import rehypeKatex from 'rehype-katex';
import rehypeStringify from 'rehype-stringify';
import { bookMarkdown } from '../src/lib/book-markdown.mjs';

const editions = Object.values(
  JSON.parse(
    readFileSync(new URL('../src/lib/editions.json', import.meta.url), 'utf8'),
  ),
);

const astProcessor = unified()
  .use(remarkParse)
  .use(remarkMath)
  .use(bookMarkdown);

const htmlProcessor = unified()
  .use(remarkParse)
  .use(remarkMath)
  .use(bookMarkdown)
  .use(remarkRehype)
  .use(rehypeKatex, { strict: false })
  .use(rehypeStringify);

const chapter = (edition, number) => {
  const url = new URL(
    `../../${edition.directory}/chapter${number}${edition.suffix}.md`,
    import.meta.url,
  );
  return {
    path: fileURLToPath(url),
    source: readFileSync(url, 'utf8'),
  };
};

const nodes = (tree, predicate) => {
  const matches = [];
  const visit = (node) => {
    if (predicate(node)) matches.push(node);
    node.children?.forEach(visit);
  };
  visit(tree);
  return matches;
};

const parse = async ({ path, source }) => {
  const tree = astProcessor.parse(source);
  return astProcessor.run(tree, { path, value: source });
};

test('Chapter 8 digit-start expressions remain inline math in every edition', async () => {
  const expected = ['1/p', '2{,}000+600=2{,}600', '10^{-3}'];

  for (const edition of editions) {
    const file = chapter(edition, 8);
    const tree = await parse(file);
    const values = nodes(tree, (node) => node.type === 'inlineMath').map(
      (node) => node.value,
    );

    for (const expression of expected)
      assert.ok(
        values.includes(expression),
        `${file.path} lost numeric inline math ${expression}`,
      );
  }
});

test('paired prose prices stay literal across the source editions', async () => {
  let priceSpans = 0;

  for (const edition of editions) {
    for (const number of [2, 7]) {
      const file = chapter(edition, number);
      const parsed = astProcessor.parse(file.source);
      const accidentalPriceSpans = nodes(
        parsed,
        (node) =>
          node.type === 'inlineMath' &&
          /^\d/.test(node.value) &&
          /\s/.test(node.value) &&
          node.position?.end.offset != null &&
          /^\d/.test(file.source.slice(node.position.end.offset)),
      ).map((node) => ({
        start: node.position.start.offset,
        source: file.source.slice(
          node.position.start.offset,
          node.position.end.offset,
        ),
      }));

      const tree = await astProcessor.run(parsed, {
        path: file.path,
        value: file.source,
      });
      const transformedByStart = new Map(
        nodes(tree, (node) => node.position?.start.offset != null).map(
          (node) => [node.position.start.offset, node],
        ),
      );

      for (const span of accidentalPriceSpans) {
        priceSpans++;
        const transformed = transformedByStart.get(span.start);
        assert.equal(transformed?.type, 'text', span.source);
        assert.equal(transformed.value, span.source);
      }
    }
  }

  assert.ok(
    priceSpans > 20,
    'Expected real paired-price examples in the books',
  );
});

test('the rendered English chapters use KaTeX for formulas and text for prices', async () => {
  const chapter8 = chapter(
    editions.find(({ directory }) => directory === 'book-en'),
    8,
  );
  const chapter2 = chapter(
    editions.find(({ directory }) => directory === 'book-en'),
    2,
  );
  const [mathHtml, moneyHtml] = await Promise.all([
    htmlProcessor.process({
      path: chapter8.path,
      value: chapter8.source,
    }),
    htmlProcessor.process({
      path: chapter2.path,
      value: chapter2.source,
    }),
  ]);

  for (const expression of ['1/p', '2{,}000+600=2{,}600', '10^{-3}'])
    assert.ok(
      String(mathHtml).includes(
        `<annotation encoding="application/x-tex">${expression}</annotation>`,
      ),
      `Missing rendered formula ${expression}`,
    );

  assert.match(String(moneyHtml), /billed at \$0\.05 per minute/);
  assert.match(String(moneyHtml), /rises to \$180 next year/);
  assert.doesNotMatch(
    String(moneyHtml),
    /<annotation encoding="application\/x-tex">0\.05 per minute/,
  );
});
