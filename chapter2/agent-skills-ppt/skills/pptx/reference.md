# pptx Skill —— 技术细则（第三层 / 渐进式披露最深一层）

本文件对应本书「渐进式披露」的第三层：只有当 Agent 需要控制版式、配色，
或排查生成问题时才会读取，平时不占用上下文。

## 版式约定

生成器使用 python-pptx 的空白版式（`slide_layouts[6]`），并手动摆放文本框，
从而完全掌控排版，不依赖模板占位符：

- 画布尺寸：10 x 7.5 英寸（4:3）。
- **标题页**：深蓝底（RGB 1F4E79），白色居中大标题（40pt）+ 浅蓝副标题（20pt）。
- **内容页**：白底，顶部深蓝色条内放页标题（26pt 白字），下方为要点列表（18pt）。

## 配色

| 名称   | RGB      | 用途           |
|--------|----------|----------------|
| ACCENT | #1F4E79  | 标题页底 / 色条 |
| DARK   | #222222  | 正文文字        |
| LIGHT  | #F2F5FA  | 备用浅背景      |

## python-pptx 关键点

- `Presentation()` 新建演示文稿；`prs.slides.add_slide(layout)` 增页。
- 文本必须放进 `text_frame`，逐段 `add_paragraph()`、逐段 `add_run()` 设置字体。
- 纯色页背景：`slide.background.fill.solid()` 后设 `fore_color.rgb`。
- 形状类型 `1` 对应矩形（MSO_SHAPE.RECTANGLE），用于顶部色条。
- 保存：`prs.save(path)`，扩展名必须是 `.pptx`。

## 校验建议

生成后重新打开文件即可验证有效性：

```python
from pptx import Presentation
prs = Presentation("output/deck.pptx")
print(len(list(prs.slides)))               # 页数
for s in prs.slides:                        # 每页第一个文本
    for shp in s.shapes:
        if shp.has_text_frame and shp.text_frame.text.strip():
            print(shp.text_frame.text.strip().splitlines()[0]); break
```
