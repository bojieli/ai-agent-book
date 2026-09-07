import { defineConfig } from 'astro/config';
import { unified } from '@astrojs/markdown-remark';
import { agentPseudocode } from './src/lib/agent-pseudocode.mjs';
import { bookMarkdown, bookFootnotes } from './src/lib/book-markdown.mjs';

export default defineConfig({
  output: 'static',
  trailingSlash: 'always',
  devToolbar: { enabled: false },
  markdown: {
    processor: unified({
      remarkPlugins: [bookMarkdown],
      rehypePlugins: [bookFootnotes],
    }),
    shikiConfig: { theme: 'github-dark', langs: [agentPseudocode] },
  },
});
