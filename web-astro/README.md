# Astro reading prototype

A local design exploration for **AI Agents in Depth**, built with plain Astro.
The homepage and complete Chapters 1–3 are implemented in all 15 maintained editions:
English, Simplified Chinese, Traditional Chinese, Spanish, Indonesian, Russian,
Tamil, Vietnamese, Japanese, Korean, Arabic, Turkish, Hungarian, Hebrew, and
Brazilian Portuguese. Other chapters link to the existing online edition.

## Run locally

From the repository root, with Node.js 22.12 or newer:

```sh
cd web-astro
npm ci
npm run dev
```

Open the URL printed by Astro (normally `http://127.0.0.1:4321`). The chapter is
at `/book-en/chapter1/`, matching its existing online path. Use the header language
switcher to choose an edition. Chinese is the default homepage at `/`; English is at `/en/`. Other homepages use locale paths such as `/ja/`, `/ar/`,
and `/pt-BR/`; Chapter 1 keeps each edition’s existing book path. Astro 7 runs the
server in the background; stop it with `npx astro dev stop` from this directory.

```sh
npm run check
npm run build
npm test
```

`npm test` checks the generated production pages, so run the build first.
`npm run format` formats the prototype's source.

## Design and reading features

- Language switching preserves the current chapter section when the translated outline matches; otherwise it opens the chapter start.
- Editorial homepage with an animated agent loop and all 10 chapters.
- The loop supports pause/play, manual steps, reduced motion, and off-screen suspension.
- Chapter reader with book navigation and an active section outline.
- A persistent reading bar on phones and tablets keeps sections, highlights, text sizing,
  and focus mode available while scrolling.
- Light/dark themes, adjustable text size, focus mode, and chapter progress.
- Figures support zoom, Fit, scrolling/dragging, and opening the image.
- Text sizing scales prose, code blocks, and tables.
- Captions, code copying, optional line wrapping, tables, and linked footnotes.
- Select a passage to highlight it; revisit or remove it in My highlights.
- Undo restores removed highlights with their saved notes and drafts, newest removal first.
  Undo history stays in the current page until you navigate away or reload.
- Highlights and plain-text notes save in IndexedDB on this browser, with JSON backup export/import.
- Choose Add note on a selection or click a highlight to edit it. Save note commits
  the note; unfinished drafts are stored separately and restored after closing or reloading.
- Backups include notes and drafts for the current edition only. Import into the same language edition. Older highlight-only backups still import;
  conflicting notes are kept as separate entries rather than overwritten.
- Fonts are self-hosted. No accounts or external font requests.

Theme, text size, and reading position stay in browser local storage. Reading
position uses a section and relative offset for each language edition. The homepage
offers Continue reading; the most recently read enabled chapter is resumed; normal chapter links start normally and section links
take precedence. A reminder on the chapter page can resume your previous position. Highlights are scoped to this book, language,
and chapter; clearing site data removes them, and private browsing may discard
them on exit. They do not sync across devices or site origins. Export a backup
before switching browsers or moving from localhost to a hosted preview.

Highlight anchoring stores the selected quote and surrounding text. Ambiguous
or changed passages remain in My highlights as unmatched quotes. This first
version supports chapter prose (including inline emphasis and links), excluding
code blocks, figures, equations, and footnotes. Essential content and links work without
JavaScript; enhanced controls are shown when their scripts initialize.

## Source boundaries

Each chapter route imports its tracked Markdown directly from the corresponding
`book/` or `book-*/` directory. Shared `Home.astro` and `Reader.astro` components
render the editions. `src/lib/editions.json` defines routes, source directories,
PDF suffixes, and text direction; `src/lib/locales/<locale>.json` contains interface
text. The browser receives only the current edition’s interface dictionary. `src/lib/book.ts` reads chapter titles through Vite's raw imports.
There is no second editable copy of the book text.

`src/lib/book-markdown.mjs` adapts the web rendering: it removes the duplicated
chapter heading, adds figure captions from existing alt text, and resolves image
and relative page links. Astro's unified Markdown processor preserves GFM tables,
footnotes, and highlighted code. Chapters 1–3 render code, footnotes, and math with KaTeX; print-only figure sizing is omitted. Mermaid and additional syntax in later chapters still need migration work.

`npm run dev` and `npm run build` copy Chapters 1–3’s 39 referenced images
per edition (585 total) into ignored generated public directories. Rerun the
command when source images change. Figure 1-1 is generated with a taller web layout
and wrapping labels, preserving all 18 labels from each source SVG. Its XHTML
labels target modern browsers; the tracked SVG remains the portable PDF/MkDocs
source. Figure 2-1 also uses a web-only layout with wrapping labels and a separate context brace to prevent overlaps. All 19 source labels are retained. All originals are copied unchanged; presentation variants are generated separately. This rendering pipeline preserves the original Markdown and assets; MkDocs
configuration, the PDF pipeline, and root dependencies are unchanged.

The existing repository license applies. The book is by Bojie Li; translation
credits and source history remain available in `docs/en/README.md` and Git.

## Prototype limits

- All 15 maintained source editions cover the homepage and Chapters 1–3; other chapters
  open the matching existing edition. Search is not prototyped yet.
- The same 21 optional machine-translation languages as MkDocs are available from English.
  They are clearly marked as unvetted. The pinned third-party script and service load
  only after selection; failures leave the source readable. Code and figures remain
  English, and annotations are disabled in machine-translated views. New interface
  translations still need native-speaker editorial review.
- Explicit language URLs are authoritative; no automatic language redirects.
- Arabic and Hebrew use right-to-left layouts; code and diagram coordinates remain
  left-to-right. Non-Latin typography uses system font fallbacks and can vary by OS.
- No deployment configuration or publishing workflow; this preview is local only.
- Root hosting paths are assumed. A GitHub Pages subpath needs an explicit base
  URL migration before deployment.
- Preview pages use `noindex, nofollow` until a publishing decision is made.

## Figure review

The homepage diagram connects context, the model, tools, and the environment.
Its arrows show observations entering context, context informing the model, tool
selection, and actions returning to the environment. Animation follows those
arrows; there are no decorative orbits or unrelated activity indicators.

The original Chapter 1 figures are retained for specific teaching purposes:

| Figure | Purpose                                                                   |
| ------ | ------------------------------------------------------------------------- |
| 1-1    | Distinguish agent/environment and model/harness boundaries.               |
| 1-2    | Compare contextual adaptation, external artifacts, and parameter updates. |
| 1-3    | Explain the context ablation experiment.                                  |
| 1-4    | Follow a multi-step tool-calling trajectory.                              |
| 1-5    | Explain native tool calling and the surrounding architecture.             |
| 1-6    | Explain the execution loop of an autonomous agent.                        |
| 1-7    | Show an actual workflow editor connecting model, memory, and tools.       |

A source-content review found issues to reconcile separately before presenting
this as a revised edition. These are in the existing SVGs, which this prototype
copies unchanged:

- `book-en/images/fig1-3.svg` describes the reasoning-history ablation as
  “Inconsistent decisions.” The adjacent prose says dropping reconstructible
  reasoning history costs almost nothing.
- `book-en/images/fig1-4.svg` labels trajectory as the complete LLM input, while
  the prose defines context as static prefix plus trajectory. Its three-quarter
  example is also labeled annual revenue, and its displayed rounded arithmetic
  does not produce the precise reported total.

### Chapter 2 English visual replacements

Nine new assets in `public/figures/chapter2-en/` replace figures 2-7, 2-9, 2-10, and 2-12 through 2-17 in the English Astro reader only. The Markdown image references and original `book-en/images` files remain unchanged. Each replacement caption links to the original copied asset. Other editions continue to use their original localized figures.

The new SVGs use wrapping XHTML text for browser layout. Figure 2-7 embeds the original PNG bytes and adds magnified viewports without regenerating experimental data. Cache diagrams distinguish reuse from free or permanent storage. Figure 2-16 keeps the recorded results and explains that the experiment’s logged character ratio includes formatting and excludes later windowed history compression (see `chapter2/context-compression/run_all_strategies.py` and `agent.py`). These SVGs are web assets; the existing PDF pipeline continues to use the originals.

### Shared diagram style across Chapters 1–3

`figure-style.mjs` defines the common slate/blue palette, surfaces, rounded boxes, and connectors for both themes. `prepare-assets.mjs` generates light/dark presentation variants for all 39 chapter figures across all 15 editions under ignored `public/figures/book/`. Source labels and geometry are preserved, using the existing reflowed layouts for figures 1-1 and 2-1 and the authored English Chapter 2 replacements where available. Experimental heatmap cell colors and embedded raster data are protected.

Original source URLs now always serve byte-for-byte originals, including figures 1-1 and 2-1. Each rendered caption has a localized original-figure link. The reader switches image variants with its theme, including the expanded viewer. Raster figures retain their pixels inside a matching frame. To change the design, edit the shared palette rather than editing the original artwork.
