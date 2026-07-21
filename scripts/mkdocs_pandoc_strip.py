"""MkDocs hook: strip Pandoc-specific attributes before rendering.

The book source uses Pandoc/LaTeX attributes that Python-Markdown does not
understand and would otherwise render as literal text:

    ## 标题 {.unnumbered}        ->  ## 标题
    ![图](x.svg){height=55%}     ->  ![图](x.svg)
    [文本](#sec:foo){.unnumbered}
"""
import re

_ID_ATTR = re.compile(r"\{#[^{}]*\}")
_CLASS_ATTR = re.compile(r"\{\.[^{}]*\}")
_TRAILING_ATTR = re.compile(r"\)\{[^{}]*\}")


def on_page_markdown(markdown, **kwargs):
    markdown = _ID_ATTR.sub("", markdown)
    markdown = _CLASS_ATTR.sub("", markdown)
    markdown = _TRAILING_ATTR.sub(")", markdown)
    return markdown
