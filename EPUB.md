# Build the EPUB editions

The repository can build EPUB 3 editions for Simplified Chinese, Traditional Chinese (Taiwan), English, Tamil, Vietnamese, and Japanese from the same Markdown sources used by the PDF editions. Each table of contents includes the title page and table of contents itself. It then displays the introduction and chapter names as centered headings, followed by one flat list of fully qualified section numbers for that group.

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
./build_epub.sh ta
./build_epub.sh vi
./build_epub.sh ja
```

Note: `./build_epub.sh` (no argument, i.e. `all`) does **not** yet include Japanese —
its PDF/EPUB build is still unvalidated, so build it explicitly with `./build_epub.sh ja`
once the Japanese fonts and `book-ja/build_pdf.sh` output are confirmed to work.

The builder writes each `.epub` beside its language's PDF. Generated EPUB files are ignored by Git.
