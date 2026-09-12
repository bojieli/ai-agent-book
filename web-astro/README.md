# Astro reading prototype

A local design exploration for **AI Agents in Depth**, built with plain Astro.
The homepage and complete Chapters 1–10 are implemented in all 15 maintained editions:
English, Simplified Chinese, Traditional Chinese, Spanish, Indonesian, Russian,
Tamil, Vietnamese, Japanese, Korean, Arabic, Turkish, Hungarian, Hebrew, and
Brazilian Portuguese. All ten chapters are available in the local reader.

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
footnotes, and highlighted code. Chapters 1–10 render code, footnotes, and math with KaTeX; print-only figure sizing is omitted. Chapter 10 highlights its action-flow transcript, Python examples, and JavaScript workflow without rewriting the source snippets.

`npm run dev` and `npm run build` copy Chapters 1–10’s referenced images
(1,679 total: 112 per edition, except Spanish, whose source has 111) into ignored generated public directories. Rerun the
command when source images change. Figure 1-1 is generated with a taller web layout
and wrapping labels, preserving all 18 labels from each source SVG. Its XHTML
labels target modern browsers; the tracked SVG remains the portable PDF/MkDocs
source. Figure 2-1 also uses a web-only layout with wrapping labels and a separate context brace to prevent overlaps. All 19 source labels are retained. All originals are copied unchanged; presentation variants are generated separately. This rendering pipeline preserves the original Markdown and assets; MkDocs
configuration, the PDF pipeline, and root dependencies are unchanged.

The existing repository license applies. The book is by Bojie Li; translation
credits and source history remain available in `docs/en/README.md` and Git.

## Prototype limits

- All 15 maintained source editions cover the homepage and all ten chapters. Search is not implemented yet.
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

### Shared diagram style across Chapters 1–10

`figure-style.mjs` defines the common slate/blue palette, surfaces, rounded boxes, and connectors for both themes. `prepare-assets.mjs` generates light/dark presentation variants for all referenced chapter figures across all 15 editions under ignored `public/figures/book/`. Source labels and geometry are preserved, using the existing reflowed layouts for figures 1-1 and 2-1 and the authored English Chapter 2 replacements where available. Experimental heatmap cell colors and embedded raster data are protected.

Original source URLs now always serve byte-for-byte originals, including figures 1-1 and 2-1. Each rendered caption has a localized original-figure link. The reader switches image variants with its theme, including the expanded viewer. Raster figures retain their pixels inside a matching frame. To change the design, edit the shared palette rather than editing the original artwork.

Figure 4-4 wraps its four side annotations in the generated web variants to prevent clipping across languages. `scripts/tool-discovery-figure.mjs` retains every source label; the original SVG remains unchanged for MkDocs and PDF.

Figure 5-1’s web canvas includes extra bottom padding so the final banner is not clipped. Its source geometry and raw SVG remain unchanged. The Spanish Chapter 5 source omits Figure 5-11; the reader preserves that source difference. Chapter 5’s tool-call walkthrough uses the shared transcript highlighting, while its side-by-side reasoning comparison retains plain text to preserve column alignment.

Chapter 6 highlights JSON event envelopes and localized event traces, element listings, and action sequences. Teaching traces wrap by default and retain their original text for copying. All 14 figures per edition use shared light/dark styling with links to the unchanged originals.

Chapter 7 uses native JSONC, YAML, and Python highlighting for task definitions, rubrics, and statistical examples. Its two source-sensitive evaluation traces use a lightweight grammar that emphasizes labels, protected strings, comments, and data flow while preserving the original text. All 10 figures per edition use shared light/dark styling with links to the unchanged originals.

Figure 7-2 uses a wider web layout so translated comparison headings have room to wrap and the bidirectional user/agent arrows remain clear of both boxes. All 23 source labels are preserved; the tracked SVGs and original-figure links remain unchanged.

Figure 7-5 routes the rubric, candidate answer, and optional reference through a single evidence bus so arrowheads do not overlap at the judge. Its structured output gives scores, explanations, and aggregation rules dedicated space while preserving all 35 source labels and the original SVGs.

Figure 7-7 gives the denser execution trace more room than the summary dashboard. A timeline and indented child operations clarify the trace hierarchy, while the monitoring cards and closed-loop message have dedicated readable regions. All 26 source labels and original SVGs remain available.

The remaining Chapter 7 figures also use generated web layouts: 7-1 separates its four stages and regression loop; 7-3 separates dialogue, shared state, and verification; 7-4 wraps the verification spectrum; 7-6 separates the anonymous comparison, Elo formula, and example leaderboard; 7-8 keeps its iteration connector in an outer gutter; and 7-10 gives observations, model components, simulation, and metrics distinct regions. Figure 7-9 uses numbered points with a description key, preserving the original point coordinates and trend line. Every localized source label is retained and checked in both themes; all raw SVGs continue to serve the original-image links and MkDocs.

### Chapter 8: model post-training

Chapter 8 uses the maintained Markdown in all 15 editions, with native Python highlighting for its five teaching examples, KaTeX equations, source footnotes, and the existing reading, highlighting, and note controls. The original Markdown and SVGs remain the MkDocs/PDF sources.

Figure 8-2 separates its five state transitions from their action labels with right-angle connectors and wrapping text slots. All 13 localized labels, the terminal reward, and the original five-state graph are preserved in both themes; the raw SVGs remain unchanged.

Figure 8-1 gives the Agent and environment larger panels, separates the action and feedback labels from their arrows, and spaces out the five trajectory cards. All 27 localized labels and reward values are retained; only the generated web layout changes.

Figure 8-8 separates the token sequence, probability chart, loss formula, and takeaway into larger wrapping regions. Its bars use a common 0–100% scale derived from the original percentages. The English web version restores the Chinese source tokens and adds an English explanation: translating individual tokens had distorted the example. Other localized labels and all source SVGs are preserved.

Figure 8-11 gives the SFT and RL stages taller cards, places the format-stability labels above a connector with clear end spacing, and separates the prerequisite explanation from the objectives and takeaway. The English web heading asks when SFT is needed before RL, consistent with the chapter's discussion of models that can skip SFT. Other localized labels and all source SVGs remain unchanged.

Figures 8-14 through 8-18 use dedicated wrapping layouts: the turn comparison has separate metric columns; the credit-assignment sequence has wider step-arrow gaps; the tool-use RL feedback label sits outside its return path; ReTool separates its execution trace, sandbox, and training results; and the training-system diagram gives its tool catalog and rollout configuration their own cards. Localized labels, code, rewards, and recorded results are preserved, with links to the untouched original SVGs.

The generated web figures share the book's light/dark palette. Figures 8-4, 8-7, 8-9, 8-10, and 8-16 use wrapping layouts to separate equations, stage labels, and connectors while retaining every localized source label. Figure 8-3 keeps its original grid cells, numeric values, direction arrows, and grayscale encoding together; only its explanatory key is reflowed. Data-bearing SVG groups are protected from palette conversion.

Figure 8-13 is a content correction in the web presentation: the Simplified Chinese figure and chapter describe 16 isolated SWE-bench rollouts with four passing, but the other 14 editions still contain an older four-candidate arithmetic example. `scripts/grpo-rollouts-figure.mjs` supplies a localized, explicitly hypothetical 16-rollout diagram in all editions, following the current Chinese source and preserving its pass positions, reward values, and group mean. Every original remains available through its original-image link.

### Chapter 9: continual evolution of agents

Chapter 9 reads the maintained Markdown directly in all 15 editions, including its three comparison tables, 25 source footnotes, and existing highlighting and note controls. It contains no fenced code examples. Chapter 8 links forward to the local Chapter 9, which continues to the local Chapter 10.

All five figures use generated wrapping layouts in the shared light/dark style. The overall evolution and experience-to-knowledge flows reserve space for feedback connectors. The trajectory-verification diagram retains the outcome/process/quality hierarchy, while the four update methods remain complementary choices. The deployment diagram separates online execution from offline candidate generation and verification, with a distinct release path and trust boundary. Localized labels and original SVGs are preserved; original-figure links continue to serve unchanged source files.

### Chapter 10: multi-agent collaboration

The final chapter reads the maintained Markdown in all 15 editions, including four tables, five highlighted code/flow examples, and each edition’s source footnotes (14 in most editions; 15 in Hungarian). Chapter 9 links to the local Chapter 10, and the final reader navigation returns to the edition’s homepage contents instead of linking to a nonexistent next chapter.

All 11 diagrams use generated wrapping layouts in the shared light/dark palette, preserving the localized source labels and original SVG files. Context boundaries, private and shared workspaces, reviewer feedback, sequential and parallel delegation, and society/game information flows retain their distinct relationships. Figure 10-2 also adds the missing mount connector to the shared workspace, matching the four mounted areas described in the chapter. The original-image links continue to serve the untouched source assets.
