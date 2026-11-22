"""Tests for the MkDocs hook that turns book figures into <figure> + <figcaption>.

Three things are locked down here:

1. the HTML transform itself (standalone images, inline images, images
   without alt text, attributes Python-Markdown may add);
2. end to end through Python-Markdown with the site's extensions: a quoted
   experiment figure must stay inside its <blockquote>, and image syntax in
   a code fence must stay code (skipped when `markdown` is not installed —
   the site build installs it via requirements-docs.txt); and
3. the book sources the transform depends on — every figure in every edition
   must carry its "图X-Y …" / "Figure X-Y: …" label in the image alt text,
   because that alt text is exactly what the site prints as the caption.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from mkdocs_figure_captions import (
    _IMAGE_LINE,
    _transform,
    iter_figure_files,
    on_page_content,
)
from mkdocs_pandoc_strip import on_page_markdown as strip_pandoc_attrs

# Every edition labels its figures in its own script, e.g. 图1-1, 圖 1-1,
# 図1-1, 그림 1-1, Figure 1-1:, Figura 1-1:, Рис. 1-1., Şekil 1-1:, 1-1. ábra:,
# איור 1‑1: (note the non-breaking hyphen), படம் 1-1, Hình 1-1:, Gambar 1-1:.
FIGURE_LABEL = re.compile(r"\d+\s*[-‐‑‒–]\s*\d+")

# The extensions from mkdocs.yml that shape how an image line is rendered.
SITE_EXTENSIONS = ["admonition", "attr_list", "footnotes", "md_in_html"]


def render(markdown_text: str) -> str:
    """Python-Markdown -> figure hook, the way MkDocs chains them."""
    markdown = pytest.importorskip("markdown")
    html = markdown.markdown(strip_pandoc_attrs(markdown_text), extensions=SITE_EXTENSIONS)
    return on_page_content(html)


def test_standalone_image_paragraph_becomes_a_captioned_figure():
    html = (
        "<p>段落。</p>\n"
        '<p><img alt="图0-2 全书结构：构建 Agent 与提升 Agent 能力" src="images/fig0-2.svg" /></p>\n'
        "<p>后续段落。</p>"
    )

    result = _transform(html)

    assert result == (
        "<p>段落。</p>\n"
        '<figure class="md-typeset-figure">\n'
        '<img alt="图0-2 全书结构：构建 Agent 与提升 Agent 能力" src="images/fig0-2.svg" />\n'
        "<figcaption>图0-2 全书结构：构建 Agent 与提升 Agent 能力</figcaption>\n"
        "</figure>\n"
        "<p>后续段落。</p>"
    )


def test_image_tag_is_kept_verbatim_including_extra_attributes():
    # Whatever Python-Markdown (attr_list, a title) put on the tag survives;
    # the hook only wraps, it never rebuilds the <img>.
    html = '<p><img alt="图2-12 结构" src="images/fig2-12.svg" title="t" width="50%"></p>'

    result = _transform(html)

    assert result.startswith('<figure class="md-typeset-figure">\n')
    assert '<img alt="图2-12 结构" src="images/fig2-12.svg" title="t" width="50%">' in result
    assert "<figcaption>图2-12 结构</figcaption>" in result


def test_caption_reuses_python_markdowns_escaped_alt_text():
    # Python-Markdown already escaped the attribute; the same entities are
    # valid as element text, so the caption is the attribute value verbatim.
    html = '<p><img alt="图5-1 A &amp; B &lt;tag&gt; &quot;quoted&quot;" src="images/fig5-1.svg" /></p>'

    result = _transform(html)

    assert "<figcaption>图5-1 A &amp; B &lt;tag&gt; &quot;quoted&quot;</figcaption>" in result


def test_inline_images_and_images_without_alt_are_left_alone():
    html = (
        '<p><img alt="Hình 2-4 Thành phần ngữ cảnh " src="images/fig2-4.svg" /> mỗi lần gọi</p>\n'
        '<p>行内图片 <img alt="图1-1 示例" src="images/fig1-1.svg" /> 后面还有正文。</p>\n'
        '<p><img alt="" src="images/decoration.svg" /></p>\n'
        '<p><img src="images/decoration.svg" /></p>'
    )

    assert _transform(html) == html


def test_empty_content_is_returned_unchanged():
    assert on_page_content("") == ""
    assert on_page_content(None) is None


def test_quoted_experiment_figure_stays_inside_its_blockquote():
    # All 23 experiment figures per edition sit inside the experiment box:
    #   > **实验 8-2 ★★：…**
    #   >
    #   > ![图8-7 …](images/fig8-7.svg)
    #   >
    #   > 正文 …
    # The earlier Markdown-level hook had to drop the `>` marker, which split
    # the box into two blockquotes with a bare figure in between.
    markdown_text = (
        "> **实验 8-2 ★★：传统 RL 与 LLM Agent 的对比研究**\n"
        ">\n"
        ">\n"
        "> ![图8-7 Q-learning 与 LLM Agent 在寻宝游戏中的架构对比](images/fig8-7.svg)\n"
        ">\n"
        ">\n"
        "> 在同一个寻宝游戏中对比 Q-learning 与 LLM Agent。\n"
    )

    result = render(markdown_text)

    assert result.count("<blockquote>") == 1
    assert result.count("</blockquote>") == 1
    assert result.count("<figure") == 1
    # The figure is a direct child of the blockquote, not wrapped in a <p>.
    assert "<p><figure" not in result
    assert '<figure class="md-typeset-figure">\n<img' in result
    assert "<figcaption>图8-7 Q-learning 与 LLM Agent 在寻宝游戏中的架构对比</figcaption>" in result
    assert result.index("<blockquote>") < result.index("<figure") < result.index("</blockquote>")
    assert "markdown=" not in result


def test_end_to_end_pandoc_attribute_never_reaches_the_caption():
    markdown_text = (
        "![图2-12 启用 Skills 后 Agent Trajectory 的完整结构](images/fig2-12.svg){height=55%}\n"
    )

    result = render(markdown_text)

    assert "<figcaption>图2-12 启用 Skills 后 Agent Trajectory 的完整结构</figcaption>" in result
    assert "height" not in result
    assert "fig2-12.svg}" not in result


def test_end_to_end_code_fences_and_inline_images_are_left_alone():
    markdown_text = (
        "```markdown\n"
        "![图9-9 代码示例里的图片](images/fig9-9.svg)\n"
        "```\n"
        "\n"
        "![Hình 2-4 Thành phần ngữ cảnh ](images/fig2-4.svg) mỗi lần Tác nhân gọi mô hình\n"
    )

    result = render(markdown_text)

    assert "<figure" not in result
    assert "<figcaption" not in result
    assert "![图9-9 代码示例里的图片](images/fig9-9.svg)" in result  # still code


def test_mkdocs_yml_registers_the_hook():
    config = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "scripts/mkdocs_figure_captions.py" in config
    assert "scripts/mkdocs_pandoc_strip.py" in config


def test_every_figure_in_every_edition_carries_its_number_in_the_alt_text():
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
