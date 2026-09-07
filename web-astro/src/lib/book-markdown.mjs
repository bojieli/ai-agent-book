import { sourceEdition } from './edition-source.mjs';
import { readFileSync } from 'node:fs';
const originalSite = 'https://bojieli.github.io/ai-agent-book';

// Adapt the web view only. The tracked book remains the shared PDF/website source.
export function bookMarkdown() {
  return (tree, file) => {
    const { directory, suffix } = sourceEdition(file.path);
    if (tree.children[0]?.type === 'heading' && tree.children[0].depth === 1) {
      tree.children.shift();
    }
    const walk = (node) => {
      if (
        node.type === 'code' &&
        node.lang === 'text' &&
        ((node.value.includes('get_weather') &&
          node.value.includes('tool_call_id')) ||
          (node.value.includes('role:') && node.value.includes('tool_calls:')))
      ) {
        node.lang = 'agent-pseudocode';
      }
      if (
        node.type === 'paragraph' &&
        node.children?.length === 1 &&
        node.children[0].type === 'image'
      ) {
        node.data = { ...node.data, hName: 'figure' };
        node.children.push({
          type: 'paragraph',
          data: { hName: 'figcaption' },
          children: [{ type: 'text', value: node.children[0].alt ?? '' }],
        });
      }
      if (node.type === 'image' && node.url.startsWith('images/')) {
        node.url = `/${directory}/${node.url}`;
      }
      if (
        node.type === 'link' &&
        !/^(?:[a-z][a-z\d+.-]*:|#|\/)/i.test(node.url)
      ) {
        if (/^chapter1(?:\.[a-z]+)?\.md(?:#|$)/.test(node.url)) {
          node.url = node.url.replace(
            /^chapter1(?:\.[a-z]+)?\.md/,
            `/${directory}/chapter1${suffix}/`,
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
