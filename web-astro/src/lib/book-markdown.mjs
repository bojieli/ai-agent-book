import { availableChapters } from './available-chapters.mjs';
import { figurePaths, originalFigureLabels } from './figure-paths.mjs';
import { sourceEdition } from './edition-source.mjs';
import { readFileSync } from 'node:fs';
const originalSite = 'https://bojieli.github.io/ai-agent-book';

// Adapt the web view only. The tracked book remains the shared PDF/website source.
export function bookMarkdown() {
  return (tree, file) => {
    const { directory, suffix, locale } = sourceEdition(file.path);
    if (tree.children[0]?.type === 'heading' && tree.children[0].depth === 1) {
      tree.children.shift();
    }
    const walk = (node) => {
      // Pandoc permits display equations with both $$ delimiters on one line.
      // remark-math parses those as inline math; restore display layout when
      // the expression occupies its own paragraph, preserving source Markdown.
      if (node.type === 'paragraph' && node.children?.length === 1) {
        const expression = node.children[0];
        const start = expression.position?.start.offset;
        const end = expression.position?.end.offset;
        if (
          expression.type === 'inlineMath' &&
          start != null &&
          end != null &&
          String(file.value).slice(start, end).startsWith('$$')
        ) {
          node.type = 'math';
          node.value = expression.value;
          node.data = {
            hName: 'pre',
            hChildren: [
              {
                type: 'element',
                tagName: 'code',
                properties: { className: ['language-math', 'math-display'] },
                children: [{ type: 'text', value: expression.value }],
              },
            ],
          };
          delete node.children;
        }
      }
      // A few editions place prose after an image on the same Markdown line.
      // Split those paragraphs so every displayed replacement has a caption/source link.
      if (node.children)
        node.children = node.children.flatMap((child) => {
          if (
            child.type !== 'paragraph' ||
            child.data?.hName === 'figure' ||
            child.children.length < 2 ||
            !child.children.some((item) => item.type === 'image')
          )
            return [child];
          const parts = [];
          let text = [];
          const flush = () => {
            if (text.length) parts.push({ type: 'paragraph', children: text });
            text = [];
          };
          for (const item of child.children) {
            if (item.type === 'image') {
              flush();
              parts.push({ type: 'paragraph', children: [item] });
            } else if (!(
              item.type === 'text' &&
              /^\{height=[\d.]+%\}$/.test(item.value.trim()) &&
              child.children[child.children.indexOf(item) - 1]?.type === 'image'
            ))
              text.push(item);
          }
          flush();
          return parts;
        });

      // Style the Chapter 3 teaching transcripts without rewriting source text.
      if (
        node.type === 'code' &&
        directory === 'book-en' &&
        /chapter3\.md$/.test(file.path)
      ) {
        if (/^(User:|Extracted memories:|Query tokens:)/.test(node.value))
          node.lang = 'book-example';
        if (node.value.startsWith('viking://')) node.lang = 'book-tree';
      }
      // The localized Chapter 5 tool trace mixes narration with tool calls.
      if (
        node.type === 'code' &&
        node.lang === 'text' &&
        /chapter5(?:\.[a-z]+)?\.md$/.test(file.path) &&
        node.value.includes('Grep(') &&
        node.value.includes('Write(')
      )
        node.lang = 'book-example';
      // Chapter 6 mixes event traces, HTML element listings, and action flows.
      // Highlight their structure without changing the localized source text.
      if (
        node.type === 'code' &&
        /chapter6(?:\.[a-z]+)?\.md$/.test(file.path)
      ) {
        if (node.lang === 'text') node.lang = 'book-interaction';
        // Japanese and Turkish label the JSON event envelope as JavaScript.
        if (
          node.lang === 'javascript' &&
          node.value.includes('"gmail_webhook"')
        )
          node.lang = 'json';
      }
      // Dollar amounts are prose, not TeX. Keep money examples literal.
      if (node.type === 'inlineMath' && /^\d/.test(node.value)) {
        node.type = 'text';
        node.value = `$${node.value}$`;
        delete node.data;
      }
      // Pandoc figure sizing is a print hint, not visible book content.
      if (node.children)
        node.children = node.children.filter(
          (child, index, siblings) =>
            !(
              child.type === 'text' &&
              /^\{height=[\d.]+%\}$/.test(child.value.trim()) &&
              siblings[index - 1]?.type === 'image'
            ),
        );
      if (
        node.type === 'code' &&
        node.lang === 'text' &&
        ((node.value.includes('get_weather') &&
          node.value.includes('tool_call_id')) ||
          (node.value.includes('role:') && /messages\s*[:=]/.test(node.value)))
      ) {
        node.lang = 'agent-pseudocode';
      }
      if (
        node.type === 'code' &&
        node.lang === 'javascript' &&
        /^\s*\/\//.test(node.value) &&
        node.value.includes('\"messages\"')
      )
        node.lang = 'jsonc';
      if (
        node.type === 'code' &&
        node.lang === 'javascript' &&
        node.value.includes('\"choices\"')
      )
        node.lang = 'jsonc';
      if (
        node.type === 'code' &&
        node.lang === 'text' &&
        (node.value.includes('<file_operation>') ||
          node.value.includes('Standard Operating Procedure:'))
      )
        node.lang = 'agent-instructions';
      if (
        node.type === 'paragraph' &&
        node.children?.length === 1 &&
        node.children[0].type === 'image'
      ) {
        node.data = { ...node.data, hName: 'figure' };
        node.children.push({
          type: 'paragraph',
          data: { hName: 'figcaption' },
          children: [
            { type: 'text', value: node.children[0].alt ?? '' },
            ...(node.children[0].url.startsWith('images/')
              ? [
                  { type: 'text', value: ' · ' },
                  {
                    type: 'link',
                    url: figurePaths(directory, node.children[0].url).original,
                    children: [
                      {
                        type: 'text',
                        value:
                          originalFigureLabels[locale] ??
                          originalFigureLabels.en,
                      },
                    ],
                    data: { hProperties: { title: node.children[0].alt } },
                  },
                ]
              : []),
          ],
        });
      }
      if (node.type === 'image' && node.url.startsWith('images/')) {
        const paths = figurePaths(directory, node.url);
        node.data = {
          ...node.data,
          hProperties: {
            ...node.data?.hProperties,
            'data-figure-light': paths.light,
            'data-figure-dark': paths.dark,
          },
        };
        node.url = paths.light;
      }
      if (
        node.type === 'link' &&
        !/^(?:[a-z][a-z\d+.-]*:|#|\/)/i.test(node.url)
      ) {
        const chapterLink = node.url.match(
          /^chapter(\d+)(?:\.[a-z]+)?\.md(?=#|$)/,
        );
        if (chapterLink && availableChapters.includes(Number(chapterLink[1]))) {
          node.url = node.url.replace(
            chapterLink[0],
            `/${directory}/chapter${chapterLink[1]}${suffix}/`,
          );
        } else {
          const resolved = new URL(node.url, `${originalSite}/${directory}/`);
          resolved.pathname = resolved.pathname.replace(/\.md$/, '/');
          node.url = resolved.href;
        }
      }
      // GFM can absorb Chinese or Arabic punctuation into bare URLs. Split autolinks only;
      // explicit Markdown links and their labels retain the author's intent.
      if (node.children)
        node.children = node.children.flatMap((child) => {
          const start = child.position?.start.offset;
          if (
            child.type !== 'link' ||
            child.children?.length !== 1 ||
            child.children[0].type !== 'text' ||
            child.children[0].value !== child.url ||
            !/、https?:\/\/|[。\u060c]+$/.test(child.url) ||
            !String(file.value)
              .slice(start, start + 8)
              .match(/^https?:\/\//)
          )
            return [child];
          return child.url
            .split(/(、(?=https?:\/\/)|[。\u060c]+$)/)
            .filter(Boolean)
            .map((part) =>
              /^https?:\/\//.test(part)
                ? {
                    ...child,
                    url: part,
                    children: [{ type: 'text', value: part }],
                  }
                : { type: 'text', value: part },
            );
        });
      node.children?.forEach(walk);
    };
    walk(tree);
  };
}

// Footnote UI is generated after Markdown parsing, so translate it in the HTML tree.
export function bookFootnotes() {
  return (tree, file) => {
    const { locale } = sourceEdition(file.path);
    if (locale === 'en') return;
    const messages = JSON.parse(
      readFileSync(
        new URL(`./locales/${locale}.json`, import.meta.url),
        'utf8',
      ),
    );
    const walk = (node) => {
      // Pandoc permits display equations with both $$ delimiters on one line.
      // remark-math parses those as inline math; restore display layout when
      // the expression occupies its own paragraph, preserving source Markdown.
      if (node.type === 'paragraph' && node.children?.length === 1) {
        const expression = node.children[0];
        const start = expression.position?.start.offset;
        const end = expression.position?.end.offset;
        if (
          expression.type === 'inlineMath' &&
          start != null &&
          end != null &&
          String(file.value).slice(start, end).startsWith('$$')
        ) {
          node.type = 'math';
          node.value = expression.value;
          node.data = {
            hName: 'pre',
            hChildren: [
              {
                type: 'element',
                tagName: 'code',
                properties: { className: ['language-math', 'math-display'] },
                children: [{ type: 'text', value: expression.value }],
              },
            ],
          };
          delete node.children;
        }
      }
      if (node.type === 'element') {
        if (node.properties?.id === 'footnote-label') {
          node.children = [
            { type: 'text', value: messages.Footnotes ?? 'Footnotes' },
          ];
        }
        const label = node.properties?.ariaLabel;
        if (typeof label === 'string' && /^Back to reference /.test(label)) {
          node.properties.ariaLabel = label.replace(
            'Back to reference ',
            `${messages['Back to reference'] ?? 'Back to reference'} `,
          );
        }
      }
      node.children?.forEach(walk);
    };
    walk(tree);
  };
}
