import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import {
  agentPseudocode,
  agentInstructions,
  bookExample,
  bookTree,
  bookInteraction,
  bookEvaluation,
} from './src/lib/agent-pseudocode.mjs';
import { bookMarkdown, bookFootnotes } from './src/lib/book-markdown.mjs';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
  markdown: {
    processor: unified({
      remarkPlugins: [remarkMath, bookMarkdown],
      rehypePlugins: [bookFootnotes, [rehypeKatex, { strict: false }]],
    }),
    shikiConfig: {
      theme: 'github-dark',
      langs: [
        agentPseudocode,
        agentInstructions,
        bookExample,
        bookTree,
        bookInteraction,
        bookEvaluation,
      ],
      transformers: [
        {
          // Keep teaching annotations readable on the dark code surface.
          name: 'readable-comments',
          span(node) {
            if (typeof node.properties.style === 'string')
              node.properties.style = node.properties.style.replace(
                /#6a737d/gi,
                '#9DA7B3',
              );
          },
        },
      ],
    },
  },
});
