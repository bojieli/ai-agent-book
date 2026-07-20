"""
pptx Skill 捆绑的可执行脚本：使用 python-pptx 从结构化大纲生成真实的 .pptx 文件。

这是 Agent Skills「渐进式披露」中第三层（细则 / 捆绑工具）的一部分：
Agent 在读取 SKILL.md 后，得知需要通过 run_skill_script 工具调用本脚本，
并按约定的 JSON schema 传入幻灯片大纲。本脚本负责把大纲落地为 PowerPoint。

payload JSON schema（由 SKILL.md 向 Agent 说明）：
{
  "title":     "演示文稿主标题（字符串）",
  "subtitle":  "副标题，通常是作者/来源（字符串，可选）",
  "slides": [
    {"title": "页标题", "bullets": ["要点1", "要点2", ...]},
    ...
  ]
}

既可作为库被 import（build_presentation），也可作为 CLI 直接运行：
    python generate_pptx.py outline.json output/deck.pptx
"""

import json
import sys
from pathlib import Path

from pptx import Presentation
from pptx.util import Pt, Inches
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN


# 一套简单的品牌配色，作为设计起点（对应 SKILL.md 提到的「模板 / 设计起点」）
ACCENT = RGBColor(0x1F, 0x4E, 0x79)   # 深蓝
DARK = RGBColor(0x22, 0x22, 0x22)     # 近黑正文
LIGHT = RGBColor(0xF2, 0xF5, 0xFA)    # 浅色背景条


def _set_slide_bg(slide, rgb):
    """给整页填充一个纯色背景。"""
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = rgb


def _add_title_slide(prs, title, subtitle):
    slide = prs.slides.add_slide(prs.slide_layouts[6])  # 6 = 纯空白版式
    _set_slide_bg(slide, ACCENT)

    # 主标题
    box = slide.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(8.4), Inches(2.0))
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    run.font.size = Pt(40)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # 副标题
    if subtitle:
        sbox = slide.shapes.add_textbox(Inches(0.8), Inches(4.3), Inches(8.4), Inches(1.0))
        stf = sbox.text_frame
        stf.word_wrap = True
        sp = stf.paragraphs[0]
        sp.alignment = PP_ALIGN.CENTER
        srun = sp.add_run()
        srun.text = subtitle
        srun.font.size = Pt(20)
        srun.font.color.rgb = RGBColor(0xD5, 0xDE, 0xEB)


def _add_content_slide(prs, title, bullets):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    _set_slide_bg(slide, RGBColor(0xFF, 0xFF, 0xFF))

    # 顶部标题色条
    bar = slide.shapes.add_shape(
        1,  # MSO_SHAPE.RECTANGLE
        Inches(0), Inches(0), Inches(10), Inches(1.1),
    )
    bar.fill.solid()
    bar.fill.fore_color.rgb = ACCENT
    bar.line.fill.background()

    tf = bar.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.5)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.LEFT
    run = p.add_run()
    run.text = title
    run.font.size = Pt(26)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

    # 正文要点
    body = slide.shapes.add_textbox(Inches(0.7), Inches(1.5), Inches(8.6), Inches(5.2))
    btf = body.text_frame
    btf.word_wrap = True
    for i, bullet in enumerate(bullets):
        para = btf.paragraphs[0] if i == 0 else btf.add_paragraph()
        para.space_after = Pt(10)
        r = para.add_run()
        r.text = "•  " + str(bullet)
        r.font.size = Pt(18)
        r.font.color.rgb = DARK


def build_presentation(payload: dict, out_path: str) -> dict:
    """从大纲 payload 构建 pptx，返回 {path, num_slides, titles} 供校验。"""
    title = payload.get("title", "Untitled Presentation")
    subtitle = payload.get("subtitle", "")
    slides = payload.get("slides", [])
    if not slides:
        raise ValueError("payload.slides 为空，至少需要一页内容")

    prs = Presentation()
    prs.slide_width = Inches(10)
    prs.slide_height = Inches(7.5)

    titles = []

    # 标题页
    _add_title_slide(prs, title, subtitle)
    titles.append(title)

    # 内容页
    for s in slides:
        s_title = s.get("title", "")
        bullets = s.get("bullets")
        if bullets is None:
            bullets = []
        _add_content_slide(prs, s_title, bullets)
        titles.append(s_title)

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(out))

    return {"path": str(out), "num_slides": len(list(prs.slides)), "titles": titles}


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python generate_pptx.py <outline.json> <output.pptx>", file=sys.stderr)
        sys.exit(1)
    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    result = build_presentation(payload, sys.argv[2])
    print(json.dumps(result, ensure_ascii=False, indent=2))
