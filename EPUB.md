# Build the EPUB editions

The repository can build EPUB 3 editions for Simplified Chinese, Traditional Chinese (Taiwan), English, Spanish, Indonesian, Arabic, Russian, Tamil, Vietnamese, Japanese, Turkish, Korean, and Hungarian from the same Markdown sources used by the PDF editions. Arabic EPUBs use RTL page progression while preserving LTR layout for code and mathematics.

Install [Pandoc](https://pandoc.org/), Poppler (`pdftoppm`), and optionally [EPUBCheck](https://www.w3.org/publishing/epubcheck/). The builder uses each PDF's first page as the corresponding EPUB cover. When EPUBCheck is available, the builder validates every generated book.

Build every language from the repository root:

```bash
./build_epub.sh
```

Build one language by passing its language code:

```bash
./build_epub.sh zh-CN
./build_epub.sh zh-TW
./build_epub.sh en
./build_epub.sh es
./build_epub.sh id
./build_epub.sh ar
./build_epub.sh ru
./build_epub.sh ta
./build_epub.sh vi
./build_epub.sh tr
./build_epub.sh ja
./build_epub.sh ko
./build_epub.sh hu
```

Note: `./build_epub.sh` (no argument, i.e. `all`) does **not** yet include Japanese
or Arabic while their PDF pipelines are being validated. Build them explicitly
with `./build_epub.sh ja` or `./build_epub.sh ar`.

The builder writes each `.epub` beside its language's PDF. Generated EPUB files are ignored by Git.

## Kindle reflowable edition

For a Kindle copy, convert a book produced by the builder or downloaded from the release. The converter renders mathematical expressions and SVG diagrams locally using Chromium. It saves a separate `-kindle.epub` beside the source and retains the formula text as image descriptions.

```bash
python -m pip install lxml playwright
python -m playwright install chromium
python scripts/kindle_epub_patcher.py "book/深入理解-AI-Agent-李博杰-v2.0.epub"
```

Run `epubcheck` on the generated copy before distributing it. Font selection and layout can vary between reading devices.
