"""Tests for the MkDocs hook that turns book figures into <figure> + <figcaption>.

Two things are locked down here:

1. the line transform itself (standalone images, blockquoted images, Pandoc
   attributes, code fences, inline images); and
2. the book sources the transform depends on — every figure in every edition
   must carry its "图X-Y …" / "Figure X-Y: …" label in the image alt text,
   because that alt text is exactly what the site now prints as the caption.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mkdocs_figure_captions import (
    _IMAGE_LINE,
    _transform,
    iter_figure_files,
    on_page_markdown,
)
from mkdocs_pandoc_strip import on_page_markdown as strip_pandoc_attrs

# Every edition labels its figures in its own script, e.g. 图1-1, 圖 1-1,
# 図1-1, 그림 1-1, Figure 1-1:, Figura 1-1:, Рис. 1-1., Şekil 1-1:, 1-1. ábra:,
# איור 1‑1: (note the non-breaking hyphen), படம் 1-1, Hình 1-1:, Gambar 1-1:.
FIGURE_LABEL = re.compile(r"\d+\s*[-\u2010\u2011\u2012\u2013]\s*\d+")


def test_standalone_image_becomes_a_captioned_figure():
    markdown = (
        "段落。\n"
        "\n"
        "![图0-2 全书结构：构建 Agent 与提升 Agent 能力](images/fig0-2.svg)\n"
        "\n"
        "后续段落。\n"
    )

    result = _transform(markdown)

    assert (
        '<figure class="md-typeset-figure">\n'
        '<img src="images/fig0-2.svg" alt="图0-2 全书结构：构建 Agent 与提升 Agent 能力">\n'
        "<figcaption>图0-2 全书结构：构建 Agent 与提升 Agent 能力</figcaption>\n"
        "</figure>"
    ) in result
    assert result.startswith("段落。\n\n")
    assert result.endswith("\n\n后续段落。\n")
    # No `markdown="1"`: inside a blockquote md_in_html never processes the
    # nested figure, and the attribute leaked into the served HTML.
    assert "markdown=" not in result


def test_blockquoted_figure_becomes_a_plain_centered_figure():
    # All 23 experiment figures per edition are written as `> ![图8-7 …](…)`.
    # Inside a blockquote Python-Markdown cannot make the figure a direct child
    # of the <blockquote> (`<p><figure>` came out of the real build), so the
    # markers are dropped and the figure renders like every other figure.
    markdown = "> ![图8-7 Q-learning 与 LLM Agent 在寻宝游戏中的架构对比](images/fig8-7.svg)\n"

    result = _transform(markdown)

    assert result == (
        '<figure class="md-typeset-figure">\n'
        '<img src="images/fig8-7.svg" alt="图8-7 Q-learning 与 LLM Agent 在寻宝游戏中的架构对比">\n'
        "<figcaption>图8-7 Q-learning 与 LLM Agent 在寻宝游戏中的架构对比</figcaption>\n"
        "</figure>\n"
    )


def test_pandoc_attributes_never_reach_the_figure_html():
    # mkdocs_pandoc_strip runs first (see mkdocs.yml), so the attribute is gone
    # before this hook turns the line into HTML. If the order ever flips, the
    # hook refuses to rewrite the line instead of emitting a broken `src`.
    image = "![图2-12 启用 Skills 后 Agent Trajectory 的完整结构](images/fig2-12.svg)"
    caption = "图2-12 启用 Skills 后 Agent Trajectory 的完整结构"

    stripped = _transform(strip_pandoc_attrs(f"{image}{{height=55%}}\n"))

    assert '<img src="images/fig2-12.svg" ' in stripped
    assert f"<figcaption>{caption}</figcaption>" in stripped
    assert "{height=55%}" not in stripped
    assert "fig2-12.svg}" not in stripped

    # Attribute still on the line (the ordering mistake): leave it untouched
    # rather than guess.
    assert _transform(f"{image}{{height=55%}}\n") == f"{image}{{height=55%}}\n"


def test_code_fences_and_inline_images_are_left_alone():
    markdown = (
        "```markdown\n"
        "![图9-9 代码示例里的图片](images/fig9-9.svg)\n"
        "```\n"
        "\n"
        "![Hình 2-4 Thành phần ngữ cảnh ](images/fig2-4.svg) mỗi lần Tác nhân gọi mô hình\n"
        "\n"
        "行内图片 ![图1-1 示例](images/fig1-1.svg) 后面还有正文。\n"
    )

    result = _transform(markdown)

    assert result == markdown
    assert "<figure" not in result


def test_indented_image_keeps_its_indentation():
    markdown = "  ![图6-3 实验 6-1 事件驱动 Agent 架构](images/fig6-3.svg)\n"

    result = _transform(markdown)

    assert result.split("\n")[:2] == [
        '  <figure class="md-typeset-figure">',
        '  <img src="images/fig6-3.svg" alt="图6-3 实验 6-1 事件驱动 Agent 架构">',
    ]


def test_caption_text_is_escaped_for_html():
    markdown = '![图5-1 A & B <tag> "quoted"](images/fig5-1.svg)\n'

    result = _transform(markdown)

    assert (
        '<img src="images/fig5-1.svg" alt="图5-1 A &amp; B &lt;tag&gt; &quot;quoted&quot;">'
        in result
    )
    assert "<figcaption>图5-1 A &amp; B &lt;tag&gt; &quot;quoted&quot;</figcaption>" in result


def test_empty_markdown_is_returned_unchanged():
    assert on_page_markdown("") == ""
    assert on_page_markdown(None) is None


def test_mkdocs_yml_registers_the_hook_after_the_pandoc_strip_hook():
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    strip_at = config.index("scripts/mkdocs_pandoc_strip.py")
    figures_at = config.index("scripts/mkdocs_figure_captions.py")

    assert strip_at < figures_at, "figure captions must run after the Pandoc strip"


def test_every_book_figure_has_a_numbered_caption_in_its_alt_text():
    unlabelled = []
    total = 0

    for path in iter_figure_files(ROOT):
        for line in path.read_text(encoding="utf-8").splitlines():
            match = _IMAGE_LINE.match(line)
            if not match:
                continue
            total += 1
            # The caption shown on the site is this alt text verbatim, so an
            # alt without "图X-Y" would render an unnumbered figure.
            if not FIGURE_LABEL.search(match.group("alt")):
                unlabelled.append(f"{path.relative_to(ROOT)}: {match.group('alt')}")

    assert total > 1000, f"expected every edition's figures, found only {total}"
    assert not unlabelled, "figures without a number in their alt text:\n" + "\n".join(
        unlabelled[:20]
    )
