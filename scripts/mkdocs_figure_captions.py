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

This hook rewrites such lines *before* Python-Markdown runs (MkDocs runs every
`on_page_markdown` hook before parsing):

    ![图0-2 全书结构](images/fig0-2.svg)
      ->  <figure class="md-typeset-figure">
          <img src="images/fig0-2.svg" alt="图0-2 全书结构">
          <figcaption>图0-2 全书结构</figcaption>
          </figure>

The `<figure>` is emitted as finished HTML rather than with `markdown="1"`, for
two reasons:

* inside a blockquote, `md_in_html` never processes the nested figure, so the
  attribute survived into the page and the `<figcaption>` came out wrapped in a
  `<p>` (both verified in a real build);
* it keeps the caption verbatim — the book's captions are plain single-line text
  (no emphasis or links), so nothing is lost, and no stray Pandoc attribute can
  end up printed inside the caption.

The caption is never invented: it is the label the author already wrote in the
alt text, so numbering stays identical to the PDF/EPUB and to every translated
edition.

Run this hook AFTER `mkdocs_pandoc_strip.py` (see mkdocs.yml): the image line
must already be free of Pandoc attributes (`{height=55%}`), because the `src`
written here is final and any leftover attribute would be printed verbatim.

Images inside a blockquote (`> ![图8-7 …](…)`, the 23 experiment figures of
each edition) lose their quote marker and render as plain centered figures like
every other figure. Python-Markdown offers no shape that avoids this: a figure
quoted line comes out as `<p><figure>` with its `<figcaption>` wrapped in a
`<p>` (inside a blockquote every block is parsed as a paragraph), and with
`markdown="1"` the attribute and the extra `<p>` both reached the served HTML.
Every such line is a standalone blockquote, so no prose is disturbed; the only
visible effect is that the surrounding quote bar breaks where the figure sits.
Images that are inline inside a sentence (Vietnamese chapter 2) are left alone,
since splitting their paragraph would reflow prose.
"""

import re

# A whole line that is nothing but one Markdown image, optionally in a
# blockquote, optionally indented, and optionally carrying Pandoc attributes
# that `mkdocs_pandoc_strip` has not removed yet. Inline images
# (`… text ![img](x.svg) more text`) never match.
_IMAGE_LINE = re.compile(
    r"^[ \t]*(?P<quote>>[ \t]?)?[ \t]*"
    r"(?P<image>!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\))"
    r"[ \t]*(?P<attrs>\{[^}]*\})?[ \t\r]*$"
)


_IMAGE_HTML = re.compile(r"!\[(?P<alt>[^\]]*)\]\((?P<src>[^)]+)\)")


def _escape(text: str) -> str:
    """Escape the few characters that could break out of an HTML attribute."""
    return (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
    )


def _figure_block(alt: str, src: str) -> list[str]:
    """The `<figure>` lines as they go into the page (indentation is applied by
    the caller when the image was an indented list item)."""
    return [
        '<figure class="md-typeset-figure">',
        f'<img src="{_escape(src)}" alt="{_escape(alt)}">',
        f"<figcaption>{_escape(alt)}</figcaption>",
        "</figure>",
    ]


def _indent(lines: list[str]) -> list[str]:
    """Indent a block so it nests in the list item or admonition it belongs to."""
    return ["  " + line if line else "" for line in lines]


def _transform(markdown: str) -> str:
    lines = markdown.split("\n")
    out: list[str] = []
    in_fence = False

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            # Fenced code: image syntax in it is an example, not a figure.
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue

        match = _IMAGE_LINE.match(line)
        if not match:
            out.append(line)
            continue

        # `mkdocs_pandoc_strip` runs first (see mkdocs.yml), so there must be no
        # Pandoc attribute left on the line. If the order ever flips, leave the
        # line alone instead of emitting a broken `src`.
        image = _IMAGE_HTML.fullmatch(match.group("image"))
        if image is None or match.group("attrs"):
            out.append(line)
            continue

        block = _figure_block(image.group("alt"), image.group("src"))

        if line.startswith((" ", "\t")):
            out.extend(_indent(block))
        else:
            out.extend(block)

    return "\n".join(out)


def on_page_markdown(markdown, **kwargs):
    """MkDocs hook entry point (see module docstring)."""
    if not markdown:
        return markdown
    return _transform(markdown)


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
