---
name: pptx
description: 从论文、大纲或结构化文本生成 PowerPoint (.pptx) 演示文稿。Use when 用户需要把一篇论文/文章/大纲做成幻灯片、slides、演示文稿、PPT、deck。Don't use when 只需纯文本总结、生成 Word/PDF、或修改已有 pptx 的单个像素级样式。
---

# pptx Skill —— 从论文生成演示文稿

## 核心流程（第二层）

把一份来源文本（论文 / 大纲）转成 8-12 页的演示文稿，按以下步骤：

1. **通读来源**：理解论文的标题、作者、问题背景、方法、关键结果、结论。
2. **规划页序**：一份合格的演示文稿总页数应为 8-12 页，至少覆盖——
   - 标题页（论文标题 + 作者/来源作为副标题）
   - 目录 / 大纲页
   - 研究背景 / 问题动机
   - 方法概述（**必须拆成 2 页**，例如「总体思路」与「关键机制」）
   - 关键结果 / 实验发现（**必须拆成 2 页**，例如「效率指标」与「效果对比」）
   - 局限性 / 讨论
   - 小结 / 结论页（要点式总结全篇）
3. **提炼要点**：每页 3-5 条 bullet，每条一句话，避免整段照搬原文。
4. **生成文件**：调用本 Skill 捆绑的脚本 `scripts/generate_pptx.py`
   （通过 `run_skill_script` 工具），传入下面约定的 JSON payload。

## 捆绑脚本调用约定

工具：`run_skill_script(name="pptx", script="generate_pptx.py", payload=<JSON字符串>)`

payload 的 JSON schema：

```json
{
  "title": "演示文稿主标题（通常等于论文标题）",
  "subtitle": "副标题，通常是作者或来源，可留空",
  "slides": [
    {"title": "页标题", "bullets": ["要点1", "要点2", "要点3"]}
  ]
}
```

约束：
- `slides` **至少 8 项**（加上自动生成的标题页，总页数落在 8-12 页区间）。
- 第一项通常是「目录 / 大纲」，最后一项应为「小结 / 结论」。
- 每页 `bullets` 建议 3-5 条。

## 更详细的样式与实现细则（第三层）

如需了解版式、配色、python-pptx 的实现细节，或排查生成问题，
再用 `read_skill_file` 读取本 Skill 内的：
- `reference.md` —— 版式、配色与 python-pptx 技术细节
- `scripts/generate_pptx.py` —— 生成器源码本身
