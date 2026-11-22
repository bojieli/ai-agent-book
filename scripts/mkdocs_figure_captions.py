"""MkDocs hook: render every standalone book figure as `<figure>` + `<figcaption>`.

The book is authored for Pandoc/LaTeX first: a figure is a lone image whose
alt text carries the label, e.g.

    ![图0-2 全书结构：构建 Agent 与提升 Agent 能力](images/fig0-2.svg)

GitHub renders that alt text as a tooltip; the PDF and EPUB print it as the
figure caption. Material renders the image alone, so on the reading site the
label ("图0-2") is invisible and the caption is lost (issue reported from the
online edition). Waiting for the browser to fix that up is not enough: the
caption has to be in the served HTML for search engines, screen readers,
"view source", and the no-JavaScript case.

This hook rewrites the *rendered* HTML (`on_page_content`, i.e. after
Python-Markdown has run). A lone image line always comes out of
Python-Markdown as a paragraph holding nothing but the `<img>`:

    <p><img alt="图0-2 全书结构" src="images/fig0-2.svg" /></p>
      ->  <figure class="md-typeset-figure">
          <img alt="图0-2 全书结构" src="images/fig0-2.svg" />
          <figcaption>图0-2 全书结构</figcaption>
          </figure>

Working on the HTML rather than the Markdown is what keeps the 23 experiment
figures of each edition inside their experiment box. Those are written as

    > **实验 8-2 ★★：…**
    >
    > ![图8-7 …](images/fig8-7.svg)
    >
    > 正文 …

and Python-Markdown offers no Markdown-level shape that puts a `<figure>`
directly inside a `<blockquote>`: raw HTML on a quoted line is treated as
inline HTML (`<p><figure>`, caption wrapped in a `<p>`), and `md_in_html`'s
`markdown="1"` is never processed inside a quote, so the earlier
Markdown-level version of this hook had to drop the `>` marker and the quote
bar broke around every experiment figure. Once the page is HTML the quoted
image is just `<blockquote>…<p><img …></p>…</blockquote>` and can be wrapped
in place, so the experiment box stays one unbroken blockquote.

The `<img>` tag is kept exactly as Python-Markdown emitted it, and the
caption is the alt text verbatim: it is the label the author already wrote,
so numbering stays identical to the PDF/EPUB and to every translated edition.
Python-Markdown has already HTML-escaped the alt attribute (`&amp;`, `&lt;`,
`&quot;`), and every such entity is equally valid as element text, so the
caption is safe to copy as-is.

Images that sit inside a sentence (Vietnamese chapter 2) produce a `<p>` with
other content around the `<img>`, so they never match and their prose is not
reflowed. Image syntax inside a code block is rendered as `<code>` text, not
an `<img>`, so it is never touched either.

`mkdocs_pandoc_strip.py` still has to run as a Markdown hook (it removes the
`{height=55%}` Pandoc attributes before Python-Markdown sees them); this hook
runs at a later stage regardless of its position in `hooks:`.
"""

import re

# The shape of a figure line in the book sources: a whole line that is nothing
# but one Markdown image, optionally in a blockquote, optionally indented, and
# optionally carrying Pandoc attributes. Not used by the hook itself (which
# works on HTML) but by the tests, to audit that every figure of every edition
# carries its label in the alt text that becomes the caption.
_IMAGE_LINE = re.compile(
    r"^[ \t]*(?P<quote>>[ \t]?)?[ \t]*"
    r"(?P<image>!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\))"
    r"[ \t]*(?P<attrs>\{[^}]*\})?[ \t\r]*$"
)

# A rendered paragraph that holds exactly one image and nothing else. This is
# what Python-Markdown emits for a standalone image line, inside or outside a
# blockquote / admonition. Attributes stay in whatever order and form
# Python-Markdown produced them (`src`, `alt`, and anything `attr_list` added).
_IMAGE_PARAGRAPH = re.compile(
    r"<p>[ \t]*(?P<img><img\b(?P<attrs>[^<>]*?)\s*/?>)[ \t]*</p>",
)

_ALT_ATTR = re.compile(r'\balt="(?P<alt>[^"]*)"')


def _figure_html(img: str, alt: str) -> str:
    return f'<figure class="md-typeset-figure">\n{img}\n<figcaption>{alt}</figcaption>\n</figure>'


def _wrap(match: re.Match) -> str:
    alt = _ALT_ATTR.search(match.group("attrs"))
    if alt is None or not alt.group("alt").strip():
        # No caption to show: leave the bare image as it was.
        return match.group(0)
    return _figure_html(match.group("img"), alt.group("alt"))


def _transform(html: str) -> str:
    return _IMAGE_PARAGRAPH.sub(_wrap, html)


def on_page_content(html, **kwargs):
    """MkDocs hook entry point (see module docstring)."""
    if not html:
        return html
    return _transform(html)


def iter_figure_files(root):
    """Yield every chapter/front-matter Markdown file of every book edition.

    Mirrors `scripts/build_site.sh` (every `book*/` edition, chapters and
    introduction). The tests use it to keep the figure numbering honest.
    """
    for edition in sorted(root.glob("book*")):
        if not edition.is_dir():
            continue
        for path in sorted(edition.glob("*.md")):
            name = path.name
            if name.startswith(("chapter", "introduction")):
                yield path
