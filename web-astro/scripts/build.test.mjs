import { availableChapters } from '../src/lib/available-chapters.mjs';
import { figurePaths } from '../src/lib/figure-paths.mjs';
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { join } from 'node:path';

const dist = fileURLToPath(new URL('../dist/', import.meta.url));
const source = readFileSync(
  new URL('../../book-en/chapter1.md', import.meta.url),
  'utf8',
);
const editionData = JSON.parse(
  readFileSync(new URL('../src/lib/editions.json', import.meta.url), 'utf8'),
);
const editions = Object.entries(editionData).map(([lang, edition]) => ({
  lang,
  ...edition,
}));
const pages = editions.flatMap((edition) =>
  [
    edition.home,
    ...availableChapters.map((number) =>
      edition.chapter.replace('chapter1', `chapter${number}`),
    ),
  ].map((route) => ({
    route,
    html: readFileSync(join(dist, route, 'index.html'), 'utf8'),
  })),
);
const chapter = pages[1].html;
const article = chapter.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)?.[1];
assert.ok(article, 'The complete chapter must be rendered in an article.');
const count = (html, tag) =>
  [...html.matchAll(new RegExp(`<${tag}\\b`, 'g'))].length;
const ids = (html) =>
  new Set([...html.matchAll(/\bid="([^"]+)"/g)].map((match) => match[1]));

test('Chapter 1 retains its sections, code, tables, figures, and footnotes', () => {
  assert.equal(count(chapter, 'h1'), 1);
  for (const level of [2, 3, 4]) {
    const headings = [...source.matchAll(new RegExp(`^#{${level}}\\s+`, 'gm'))]
      .length;
    // The renderer adds one h2 for the footnotes section.
    assert.equal(count(article, `h${level}`), headings + (level === 2 ? 1 : 0));
  }
  assert.equal(count(article, 'pre'), 4);
  assert.equal(count(article, 'table'), 5);
  assert.equal(count(article, 'figure'), 7);
  assert.equal(count(article, 'figcaption'), 7);
  const footnotes = [...source.matchAll(/^\s*(?:>\s*)?\[\^([^\]]+)\]:/gm)].map(
    (match) => match[1],
  );
  assert.equal(footnotes.length, 7);
  for (const note of footnotes)
    assert.ok(
      ids(article).has(`user-content-fn-${note}`),
      `Missing footnote ${note}`,
    );
  assert.match(article, /Thought Questions/);
  assert.match(article, /Contextual adaptation/);
});

test('All generated pages resolve local assets, links, and fragments', () => {
  for (const page of pages) {
    const pageIds = [...page.html.matchAll(/\bid="([^"]+)"/g)].map(
      (match) => match[1],
    );
    assert.equal(
      new Set(pageIds).size,
      pageIds.length,
      `Duplicate IDs on ${page.route}`,
    );
    for (const [, ref] of page.html.matchAll(/\b(?:href|src)="([^"]+)"/g)) {
      const url = new URL(ref, `https://preview.example${page.route}`);
      if (url.origin !== 'https://preview.example') continue;
      const path = join(
        dist,
        decodeURIComponent(url.pathname),
        url.pathname.endsWith('/') ? 'index.html' : '',
      );
      assert.ok(
        existsSync(path),
        `Missing local asset or route: ${ref} on ${page.route}`,
      );
      if (url.hash && path.endsWith('.html')) {
        assert.ok(
          ids(readFileSync(path, 'utf8')).has(
            decodeURIComponent(url.hash.slice(1)),
          ),
          `Missing fragment: ${ref}`,
        );
      }
    }
  }
});

function assertFigureContent(copied, original, image) {
  assert.deepEqual(copied, original, `Original figure changed: ${image}`);
}

test('Chapter figures retain their source content, with Figure 1-1 labels reflowed', () => {
  const images = [...source.matchAll(/!\[[^\]]*\]\((images\/[^)]+)\)/g)].map(
    (match) => match[1],
  );
  for (const image of images) {
    const original = readFileSync(
      new URL(`../../book-en/${image}`, import.meta.url),
    );
    const copied = readFileSync(join(dist, 'book-en', image));
    assertFigureContent(copied, original, image);
  }
});

test('Each edition renders its original content, figures, language links, and note scope', () => {
  for (const edition of editions) {
    const homepage = pages.find((page) => page.route === edition.home).html;
    const reader = pages.find((page) => page.route === edition.chapter).html;
    const source = readFileSync(
      new URL(
        `../../${edition.directory}/chapter1${edition.suffix}.md`,
        import.meta.url,
      ),
      'utf8',
    );
    const article = reader.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)?.[1];
    assert.ok(article);
    assert.equal(count(reader, 'h1'), 1);
    const title = source
      .match(/^#\s+(.+)$/m)[1]
      .replaceAll('&', '&amp;')
      .replaceAll("'", '&#39;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;');
    assert.ok(reader.includes(title), `Missing title for ${edition.lang}`);
    for (const level of [2, 3, 4]) {
      const headings = [
        ...source.matchAll(new RegExp(`^#{${level}}\\s+`, 'gm')),
      ].length;
      assert.equal(
        count(article, `h${level}`),
        headings + (level === 2 ? 1 : 0),
      );
    }
    assert.equal(count(article, 'figure'), 7);
    assert.equal(count(article, 'table'), 5);
    assert.equal(count(article, 'pre'), 4);
    assert.ok(
      reader.includes(
        `data-chapter-key="ai-agents-in-depth:${edition.lang}:chapter1"`,
      ),
    );
    assert.ok(reader.includes(`href="${edition.home}#contents"`));
    assert.ok(
      reader.includes(`/${edition.directory}/chapter2${edition.suffix}/`),
    );
    for (const [html, kind] of [
      [homepage, 'home'],
      [reader, 'chapter'],
    ]) {
      assert.ok(html.includes(`lang="${edition.lang}" dir="${edition.dir}"`));
      if (kind === 'chapter')
        assert.ok(
          html.includes(`AI-Agents-in-Depth-${edition.pdf}.pdf`),
          `Missing PDF for ${edition.lang}`,
        );
      const picker = html.match(
        /<details class="language-picker"[\s\S]*?<\/details>/,
      )?.[0];
      assert.ok(picker);
      for (const target of editions)
        assert.ok(picker.includes(`href="${target[kind]}"`));
      if (edition.lang !== 'en') {
        assert.ok(!html.includes('>My highlights<'));
        assert.ok(!html.includes('>Text size<'));
        assert.ok(!html.includes('>Start reading'));
      }
    }
    for (const [, image] of source.matchAll(
      /!\[[^\]]*\]\((images\/[^)]+)\)/g,
    )) {
      assert.ok(
        article.includes(
          `src="${figurePaths(edition.directory, image).light}"`,
        ),
      );
      assertFigureContent(
        readFileSync(join(dist, edition.directory, image)),
        readFileSync(
          new URL(`../../${edition.directory}/${image}`, import.meta.url),
        ),
        image,
      );
    }
  }
});

test('Chinese footnotes keep separate citation URLs and translated navigation', () => {
  for (const edition of editions.filter(({ lang }) => lang.startsWith('zh-'))) {
    const html = pages.find((page) => page.route === edition.chapter).html;
    assert.ok(!html.includes('>Footnotes<'));
    assert.ok(!html.includes('aria-label="Back to reference'));
    assert.ok(html.includes(edition.lang === 'zh-CN' ? '>注释<' : '>註釋<'));
    for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
      assert.ok(
        !decodeURI(href).match(/、https?:\/\/|。$/),
        `Merged or punctuated citation: ${href}`,
      );
    }
    for (const url of [
      'https://manus.im/blog/manus-sandbox',
      'https://manus.im/blog/manus-google-drive-connector',
      'https://manus.im/blog/manus-my-computer-desktop',
      'https://github.com/openclaw/openclaw',
      'https://docs.openclaw.ai/tools',
      'https://adk.dev/workflows/',
    ])
      assert.ok(html.includes(`href="${url}"`));
  }
});

test('All 15 maintained editions have complete UI catalogs and isolated browser messages', () => {
  assert.equal(editions.length, 15);
  assert.equal(pages.length, editions.length * (availableChapters.length + 1));
  const catalogs = Object.fromEntries(
    editions.map(({ lang }) => [
      lang,
      JSON.parse(
        readFileSync(
          new URL(`../src/lib/locales/${lang}.json`, import.meta.url),
          'utf8',
        ),
      ),
    ]),
  );
  const keys = Object.keys(catalogs.en).sort();
  for (const edition of editions) {
    const messages = catalogs[edition.lang];
    assert.deepEqual(Object.keys(messages).sort(), keys, edition.lang);
    assert.ok(
      Object.values(messages).every(
        (value) => typeof value === 'string' && value.trim(),
      ),
      edition.lang,
    );
    for (const route of [edition.home, edition.chapter]) {
      const html = pages.find((page) => page.route === route).html;
      const embedded = JSON.parse(
        html.match(
          /<script id="book-ui-messages" type="application\/json">([\s\S]*?)<\/script>/,
        )?.[1] ?? 'null',
      );
      assert.deepEqual(embedded, edition.lang === 'en' ? {} : messages, route);
    }
  }
});

test('Arabic citation punctuation stays outside links', () => {
  const html = pages.find((page) => page.route === editionData.ar.chapter).html;
  for (const [, href] of html.matchAll(/href="([^"]+)"/g)) {
    assert.ok(
      !decodeURI(href).endsWith('،'),
      `Punctuation absorbed into URL: ${href}`,
    );
  }
  for (const href of [
    'https://www.drjoshcsimmons.com/writing/we-are-entering-the-graph-engineering-phase',
    'https://x.com/steipete/status/2078277297791189132',
    'https://docs.langchain.com/oss/python/langgraph/overview',
    'https://learn.microsoft.com/en-us/agent-framework/workflows/',
  ]) {
    assert.ok(html.includes(`href="${href}"`));
  }
});

test('Chapter 1 language section links resolve and round-trip across editions', () => {
  const maps = Object.fromEntries(
    editions.map((edition) => {
      const html = pages.find((page) => page.route === edition.chapter).html;
      const json = html.match(
        /<script\b[^>]*id="section-language-links"[^>]*>([\s\S]*?)<\/script>/,
      )?.[1];
      assert.ok(json, edition.lang);
      return [edition.lang, JSON.parse(json)];
    }),
  );
  for (const edition of editions) {
    for (const [slug, translations] of Object.entries(maps[edition.lang])) {
      assert.equal(Object.keys(translations).length, editions.length);
      for (const target of editions) {
        const translatedSlug = translations[target.lang];
        const html = pages.find((page) => page.route === target.chapter).html;
        assert.ok(
          html.includes(`id="${translatedSlug}"`),
          `${target.lang}: ${translatedSlug}`,
        );
        assert.equal(maps[target.lang][translatedSlug][edition.lang], slug);
      }
    }
  }
});

test('Chinese homepage is the default and machine options are clearly separate', () => {
  assert.ok(
    readFileSync(join(dist, 'index.html'), 'utf8').includes('lang="zh-CN"'),
  );
  assert.ok(
    readFileSync(join(dist, 'en/index.html'), 'utf8').includes('lang="en"'),
  );
  for (const { html } of pages) {
    assert.equal([...html.matchAll(/data-machine-language=/g)].length, 21);
    assert.ok(html.includes('未经审核 / Not vetted'));
    assert.ok(!html.includes('<script src="https://cdn.staticfile.net'));
  }
});

test('Chapter 2 preserves all editions, figures, outlines, and chapter isolation', () => {
  for (const edition of editions) {
    const route = edition.chapter.replace('chapter1', 'chapter2');
    const html = readFileSync(join(dist, route, 'index.html'), 'utf8');
    const markdown = readFileSync(
      new URL(
        `../../${edition.directory}/chapter2${edition.suffix}.md`,
        import.meta.url,
      ),
      'utf8',
    );
    const content = html.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)[1];
    assert.equal(count(content, 'img'), 17, edition.lang);
    assert.equal(count(content, 'h3'), 31, edition.lang);
    assert.ok(
      html.includes(
        `data-chapter-key="ai-agents-in-depth:${edition.lang}:chapter2"`,
      ),
    );
    assert.ok(html.includes(`href="${edition.chapter}"`));
    assert.ok(html.includes(`/chapter3${edition.suffix}/`));
    assert.ok(!content.includes('{height='));
    assert.ok(!content.includes('katex-error'));
    assert.ok(content.includes('class="katex"'), edition.lang);
    for (const [, image] of markdown.matchAll(
      /!\[[^\]]*\]\((images\/[^)]+)\)/g,
    )) {
      assert.ok(
        content.includes(
          `src="${figurePaths(edition.directory, image).light}"`,
        ),
      );
      assertFigureContent(
        readFileSync(join(dist, edition.directory, image)),
        readFileSync(
          new URL(`../../${edition.directory}/${image}`, import.meta.url),
        ),
        image,
      );
    }
    const mappings = JSON.parse(
      html.match(
        /<script\b[^>]*id="section-language-links"[^>]*>([\s\S]*?)<\/script>/,
      )[1],
    );
    assert.ok(Object.keys(mappings).length >= 40);
    for (const translations of Object.values(mappings)) {
      assert.equal(Object.keys(translations).length, 15);
      for (const target of editions) {
        const targetHtml = readFileSync(
          join(
            dist,
            target.chapter.replace('chapter1', 'chapter2'),
            'index.html',
          ),
          'utf8',
        );
        assert.ok(ids(targetHtml).has(translations[target.lang]));
      }
    }
  }
});

test('Chapter 2 visual replacements preserve originals and highlight teaching examples', () => {
  const html = readFileSync(join(dist, 'book-en/chapter2/index.html'), 'utf8');
  assert.equal([...html.matchAll(/data-language="jsonc"/g)].length, 6);
  assert.equal(
    [...html.matchAll(/data-language="agent-pseudocode"/g)].length,
    4,
  );
  assert.equal(
    [...html.matchAll(/data-language="agent-instructions"/g)].length,
    2,
  );
  assert.ok(
    html.includes('color:#9DA7B3'),
    'Explanatory comments use readable contrast',
  );
  const heatmap = readFileSync(
    join(dist, 'figures/chapter2-en/fig2-7-web.svg'),
    'utf8',
  );
  const embedded = heatmap.match(/data:image\/png;base64,([^"\s]+)/)[1];
  assert.deepEqual(
    Buffer.from(embedded, 'base64'),
    readFileSync(new URL('../../book-en/images/fig2-7.png', import.meta.url)),
  );
});

test('Every chapter figure has two styled variants and an untouched original', () => {
  for (const edition of editions)
    for (const number of availableChapters) {
      const markdown = readFileSync(
        new URL(
          `../../${edition.directory}/chapter${number}${edition.suffix}.md`,
          import.meta.url,
        ),
        'utf8',
      );
      const html = readFileSync(
        join(
          dist,
          edition.chapter.replace('chapter1', `chapter${number}`),
          'index.html',
        ),
        'utf8',
      );
      for (const [, image] of markdown.matchAll(
        /!\[[^\]]*\]\((images\/[^)]+)\)/g,
      )) {
        const paths = figurePaths(edition.directory, image);
        assert.ok(
          html.includes(`href="${paths.original}"`),
          `No source link: ${paths.original}`,
        );
        for (const theme of ['light', 'dark']) {
          assert.ok(existsSync(join(dist, paths[theme])));
          assert.ok(html.includes(`data-figure-${theme}="${paths[theme]}"`));
          if (image === 'images/fig4-4.svg') {
            const original = readFileSync(
              new URL(`../../${edition.directory}/${image}`, import.meta.url),
              'utf8',
            );
            const variant = readFileSync(join(dist, paths[theme]), 'utf8');
            assert.equal(count(variant, 'foreignObject'), 2);
            for (const [, label] of original.matchAll(
              /<text\b[^>]*>([\s\S]*?)<\/text>/g,
            ))
              assert.ok(
                variant.includes(label),
                `Missing diagram label in ${edition.lang}`,
              );
            assert.equal(
              readFileSync(join(dist, paths.original), 'utf8'),
              original,
            );
          }
        }
      }
    }
});

for (const chapterNumber of [3, 4, 5])
  test(`Chapter ${chapterNumber} preserves code, figures, headings, and reader navigation in all editions`, async () => {
    const { fromMarkdown } = await import('mdast-util-from-markdown');
    const decode = (s) =>
      s
        .replace(/&#x([0-9a-f]+);/gi, (_, n) =>
          String.fromCodePoint(parseInt(n, 16)),
        )
        .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
        .replace(
          /&(lt|gt|quot|apos|amp);/g,
          (_, n) => ({ lt: '<', gt: '>', quot: '"', apos: "'", amp: '&' })[n],
        );
    for (const edition of editions) {
      const route = edition.chapter.replace(
        'chapter1',
        `chapter${chapterNumber}`,
      );
      const html = readFileSync(join(dist, route, 'index.html'), 'utf8');
      const markdown = readFileSync(
        new URL(
          `../../${edition.directory}/chapter${chapterNumber}${edition.suffix}.md`,
          import.meta.url,
        ),
        'utf8',
      );
      const article = html.match(/<article\b[^>]*>([\s\S]*?)<\/article>/)[1];
      const code = [],
        inlineCode = [],
        headings = [],
        images = [];
      function visit(node) {
        if (node.type === 'code') code.push(node.value);
        if (node.type === 'inlineCode') inlineCode.push(node.value);
        if (node.type === 'image') images.push(node.url);
        if (node.type === 'heading' && node.depth === 3) headings.push(node);
        node.children?.forEach(visit);
      }
      visit(fromMarkdown(markdown));
      const rendered = [
        ...article.matchAll(
          /<pre\b[^>]*>\s*<code\b[^>]*>([\s\S]*?)<\/code>\s*<\/pre>/g,
        ),
      ].map((m) => decode(m[1].replace(/<[^>]*>/g, '')).replace(/\n$/, ''));
      assert.deepEqual(rendered, code, `Code altered in ${edition.lang}`);
      if (chapterNumber === 4) {
        const renderedInline = [
          ...article.matchAll(/<code\b[^>]*>([\s\S]*?)<\/code>/g),
        ].map((match) => decode(match[1]));
        assert.deepEqual(
          renderedInline.sort(),
          inlineCode.sort(),
          `Inline code altered in ${edition.lang}`,
        );
        assert.equal(count(article, 'table'), 2, edition.lang);
        for (const level of [2, 4]) {
          const expected = [
            ...markdown.matchAll(new RegExp(`^#{${level}}\\s+`, 'gm')),
          ].length;
          assert.equal(
            count(article, `h${level}`),
            expected + (level === 2 ? 1 : 0),
            edition.lang,
          );
        }
        for (const [, id] of markdown.matchAll(/^\[\^([^\]]+)\]:/gm))
          assert.ok(
            ids(article).has(`user-content-fn-${id}`),
            `Missing footnote ${id}`,
          );
      }
      if (chapterNumber === 5) {
        assert.equal(
          (article.match(/data-language="book-example"/g) || []).length,
          1,
          edition.lang,
        );
        assert.equal(
          (article.match(/data-language="python"/g) || []).length,
          1,
          edition.lang,
        );
        assert.equal(count(article, 'table'), 1, edition.lang);
        for (const [, id] of markdown.matchAll(/^\[\^([^\]]+)\]:/gm))
          assert.ok(
            ids(article).has(`user-content-fn-${id}`),
            `Missing footnote ${id}`,
          );
      }
      if (edition.lang === 'en' && chapterNumber === 3) {
        assert.equal(
          (article.match(/data-language="book-example"/g) || []).length,
          3,
        );
        assert.equal(
          (article.match(/data-language="book-tree"/g) || []).length,
          1,
        );
        assert.equal(
          (article.match(/data-language="python"/g) || []).length,
          5,
        );
        assert.ok(article.includes('Python-style pseudocode'));
      }
      assert.equal(count(article, 'img'), images.length, edition.lang);
      assert.equal(count(article, 'h3'), headings.length, edition.lang);
      assert.ok(!article.includes('katex-error'), edition.lang);
      if (chapterNumber === 3)
        assert.ok(article.includes('class="katex"'), edition.lang);
      assert.equal(
        (article.match(/class="katex-display"/g) || []).length,
        (markdown.match(/^(?:> )?\$\$.+\$\$\s*$/gm) || []).length,
        edition.lang,
      );
      assert.ok(
        html.includes(
          `data-chapter-key="ai-agents-in-depth:${edition.lang}:chapter${chapterNumber}"`,
        ),
      );
      assert.ok(
        html.includes(
          `href="${edition.chapter.replace('chapter1', `chapter${chapterNumber - 1}`)}"`,
        ),
      );
      assert.ok(
        html.includes(
          `href="${availableChapters.includes(chapterNumber + 1) ? '' : 'https://bojieli.github.io/ai-agent-book'}/${edition.directory}/chapter${chapterNumber + 1}${edition.suffix}/"`,
        ),
      );
      for (const target of editions)
        assert.ok(
          html.includes(
            `href="${target.chapter.replace('chapter1', `chapter${chapterNumber}`)}"`,
          ),
        );
      const mappings = JSON.parse(
        html.match(
          /<script\b[^>]*id="section-language-links"[^>]*>([\s\S]*?)<\/script>/,
        )[1],
      );
      for (const translations of Object.values(mappings))
        for (const [locale, slug] of Object.entries(translations)) {
          const target = editions.find((e) => e.lang === locale);
          assert.ok(
            ids(
              readFileSync(
                join(
                  dist,
                  target.chapter.replace('chapter1', `chapter${chapterNumber}`),
                  'index.html',
                ),
                'utf8',
              ),
            ).has(slug),
          );
        }
    }
  });

test('Chapter 5 architecture banner fits its web canvas in every edition', () => {
  for (const edition of editions) {
    const paths = figurePaths(edition.directory, 'images/fig5-1.svg');
    for (const theme of ['light', 'dark']) {
      const svg = readFileSync(join(dist, paths[theme]), 'utf8');
      const [, top, height] = svg.match(/viewBox="0 (\d+) 980 (\d+)"/);
      const [, bottomY, bannerHeight] = svg.match(
        /<rect x="60" y="(566)" width="860" height="(38)"/,
      );
      assert.ok(
        Number(top) + Number(height) >
          Number(bottomY) + Number(bannerHeight) + 1,
        edition.lang,
      );
    }
  }
});
