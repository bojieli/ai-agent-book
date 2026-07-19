"""[DEPRECATED] Old Chapter 9 (multi-Agent) figure generator.

⚠️ DO NOT RUN: 2026-03-12 重构后，章节编号变化（原第 9 章 → 第 10 章）。
此文件生成的图实际是当前【第 10 章】内容（多 Agent 协作），但仍保存为 fig9-*.svg，
若运行会覆盖当前正确的【第 9 章】（多模态与实时交互）图，导致内容错位。

当前正确的第 9 章 SVG（多模态/语音/Computer Use/VLA/Sim2Real）由
2026-03-12 提交 a33c88f 从原 fig8-*.svg 重命名而来；当前正确的第 10 章 SVG
（多 Agent 协作）由本文件原本生成的内容**手工迁移**到 fig10-*.svg。

要重新生成本文件中的图，应改为生成 fig10-*.svg 并对照 chapter10.md 引用名。

Original (now Ch 10) figure list:
  fig10-1:  共享上下文 vs 独立上下文 (concrete context windows)
  fig10-2:  基于阶段的角色切换 (prompt/tool-set changes per phase)
  fig10-3:  Proposer-Reviewer 循环 (Slidev PPT iterative feedback)
  fig10-4:  Manager 顺序协调 (sequential sub-agent delegation)
  fig10-5:  书籍翻译 Agent 架构 (NEW — Exp 10.4)
  fig10-6:  Manager 并行协调 (concurrent agents + message bus)
  fig10-7:  Phone + Computer 双 Agent (NEW — Exp 10.5/10.6)
  fig10-8:  并行网页搜集 (NEW — Exp 10.7)
  fig10-9:  Handoff 链式模式 (peer control passing)
  fig10-10: MetaGPT SOP 流水线 (PM→Arch→Eng→QA with artifacts)
  fig10-11: AI 小镇架构 (memory stream + reflection + planning)
  fig10-12: 语音狼人杀 Agent 系统 (NEW — Exp 10.9)
"""

import sys
print(
    "ERROR: gen_ch9_figs.py is DEPRECATED. Running it would overwrite the\n"
    "correct Chapter 9 (multimodal) figures with old Chapter 10 (multi-agent) content.\n"
    "See module docstring at the top of this file for the rename history.",
    file=sys.stderr,
)
sys.exit(2)
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import (
    SVG, COLORS, FONT, MONO,
    FS_TITLE, FS_BODY, FS_SMALL, FS_TINY, FS_LABEL, STROKE_W, CORNER_R,
    _escape,
)

OUT = os.path.join(os.path.dirname(__file__), 'images')


# ════════════════════════════════════════════════════════════════════
#  fig9-1: 共享上下文 vs 独立上下文
# ════════════════════════════════════════════════════════════════════

def fig9_1():
    W, H = 780, 560
    s = SVG(W, H)

    s.text(W // 2, 30, '共享上下文 vs 独立上下文', size=FS_TITLE, bold=True)

    col_w = 350
    lx, rx = 20, W - col_w - 20

    # ── Left: shared context ──
    s.group_box(lx, 55, col_w, 480, '共享上下文（单 Agent 多阶段）')

    ctx_x, ctx_w = lx + 15, col_w - 30
    phases = [
        ('阶段 1：需求分析师', 'medium', [
            'sys: "你的职责是充分理解需求..."',
            'tools: [ask_question, save_req]',
            'user: "写一个 CSV 分析脚本"',
            'agent: "需要处理哪些文件类型？"',
        ]),
        ('阶段 2：软件工程师', 'light', [
            'sys: "根据已确认需求编写代码..."',
            'tools: [write_file, execute_code]',
            'agent: write_file("analyze.py", ...)',
            'agent: execute_code("python test.py")',
        ]),
        ('阶段 3：代码审查员', 'light', [
            'sys: "审查代码质量和安全性..."',
            'tools: [run_linter, run_tests]',
            'agent: run_linter → 2 warnings',
            'agent: approve_code()',
        ]),
    ]

    cy = 82
    for title, fill, lines in phases:
        ph = 18 + len(lines) * 18 + 10
        s.rect(ctx_x, cy, ctx_w, ph, fill=fill, rx=4)
        s.text(ctx_x + 8, cy + 14, title, size=FS_SMALL, bold=True, anchor='start')
        for i, ln in enumerate(lines):
            s.mono(ctx_x + 12, cy + 32 + i * 18, ln, size=12)
        cy += ph + 2

    s.rect(ctx_x, cy, ctx_w, 28, fill='code_bg', rx=3)
    s.text(ctx_x + ctx_w // 2, cy + 14, '↑ 所有阶段共享同一对话历史', size=FS_TINY, bold=True)
    cy += 36

    s.text(lx + col_w // 2, cy + 10, '✓ 完整执行轨迹', size=FS_SMALL, fill='text_light')
    s.text(lx + col_w // 2, cy + 32, '✗ 上下文快速膨胀', size=FS_SMALL, fill='text_light')

    # ── Right: independent context ──
    s.group_box(rx, 55, col_w, 480, '独立上下文（真正多 Agent）')

    agents_data = [
        ('Glossary Agent', [
            'sys: "识别术语并翻译..."',
            'tools: [search_dict, write_file]',
            '→ glossary.json',
        ]),
        ('Translation Agent', [
            'sys: "翻译本章内容..."',
            'tools: [read_file, write_file]',
            '→ chapter3_zh.md',
        ]),
        ('Proofreading Agent', [
            'sys: "检查术语一致性..."',
            'tools: [read_file, write_file]',
            '→ review_report.md',
        ]),
    ]

    ay = 82
    for name, lines in agents_data:
        ah = 18 + len(lines) * 18 + 8
        s.rect(rx + 15, ay, ctx_w, ah, fill='light', rx=4)
        s.text(rx + 23, ay + 14, name, size=FS_SMALL, bold=True, anchor='start')
        for i, ln in enumerate(lines):
            s.mono(rx + 27, ay + 32 + i * 18, ln, size=12)
        ay += ah + 8

    fs_y = ay + 5
    s.rect(rx + 15, fs_y, ctx_w, 65, fill='medium', rx=4)
    s.text(rx + 15 + ctx_w // 2, fs_y + 16, '共享文件系统', size=FS_SMALL, bold=True)
    files = ['glossary.json', 'chapter3_zh.md', 'review_report.md']
    s.mono(rx + 27, fs_y + 38, '  '.join(files), size=11)
    s.text(rx + 15 + ctx_w // 2, fs_y + 55, '+ 工具调用参数传递结构化数据', size=FS_TINY, fill='text_light')

    s.text(rx + col_w // 2, fs_y + 82, '✓ 模块化 · 可扩展 · 并行', size=FS_SMALL, fill='text_light')
    s.text(rx + col_w // 2, fs_y + 104, '✗ 信息同步复杂', size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-1.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-2: 基于阶段的角色切换
# ════════════════════════════════════════════════════════════════════

def fig9_2():
    W, H = 780, 520
    s = SVG(W, H)

    s.text(W // 2, 28, '基于阶段的角色切换：Coding Agent 三阶段', size=FS_TITLE, bold=True)

    phases = [
        ('需求分析师', 'medium',
         '"你的职责是充分理解需求。\n不要急于实现，在这个阶段\n你的任务是提问和确认。"',
         ['ask_clarifying_question(q)', 'save_requirement(k, v)', 'complete_requirements_analysis()'],
         'complete_requirements_analysis()'),
        ('软件工程师', 'light',
         '"根据已确认的需求编写\n高质量 Python 代码。遵循\n模块化、错误处理最佳实践。"',
         ['write_file(path, content)', 'read_file(path)', 'execute_code(code)'],
         'submit_for_review()'),
        ('代码审查员', '#e8e8e8',
         '"从多个维度评估代码质量：\n功能正确性、代码规范、\n安全性。采用批判性思维。"',
         ['run_linter(file)', 'run_tests(file)', 'analyze_complexity(file)'],
         None),
    ]

    s.rect(30, 55, W - 60, 28, fill='code_bg', rx=3)
    s.text(W // 2, 69, '▼ 同一上下文连续流动 — 对话历史在阶段间完整保留 ▼', size=FS_SMALL, bold=True)

    pw = 225
    gap = 18
    px_start = (W - 3 * pw - 2 * gap) // 2
    py = 100

    for i, (role, fill, prompt, tools, trigger) in enumerate(phases):
        x = px_start + i * (pw + gap)

        s.rect(x, py, pw, 380, fill=fill, rx=6)
        s.text(x + pw // 2, py + 22, f'阶段 {i + 1}', size=FS_TINY, fill='text_light')
        s.text(x + pw // 2, py + 42, role, size=FS_BODY, bold=True)

        s.rect(x + 8, py + 60, pw - 16, 88, fill='code_bg', rx=3)
        s.text(x + 14, py + 75, '系统提示词', size=FS_TINY, fill='text_light', anchor='start')
        for j, ln in enumerate(prompt.split('\n')):
            s.text(x + 14, py + 92 + j * 16, ln, size=12, anchor='start', fill='text_light')

        s.rect(x + 8, py + 158, pw - 16, 18 + len(tools) * 20, fill='white', rx=3)
        s.text(x + 14, py + 172, '工具集', size=FS_TINY, fill='text_light', anchor='start')
        for j, tool in enumerate(tools):
            s.mono(x + 14, py + 190 + j * 20, tool, size=11)

        if trigger:
            ty = py + 290
            s.rect(x + 8, ty, pw - 16, 48, fill='dark', rx=12)
            s.text(x + pw // 2, ty + 16, '触发转换', size=FS_TINY, fill='white')
            s.mono(x + pw // 2, ty + 34, trigger, size=10, anchor='middle', fill='white')

        if i < 2:
            ax1 = x + pw + 2
            ax2 = x + pw + gap - 2
            ay = py + 310
            s.arrow(ax1, ay, ax2, ay)

    s.text(W // 2, H - 10, '角色转换：更新系统提示词 + 工具集，对话历史和状态连续保留',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-2.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-3: Proposer-Reviewer 循环（Slidev PPT 生成）
# ════════════════════════════════════════════════════════════════════

def fig9_3():
    W, H = 780, 520
    s = SVG(W, H)

    s.text(W // 2, 28, 'Proposer-Reviewer 循环：Slidev PPT 生成', size=FS_TITLE, bold=True)

    # Editor (Proposer)
    ex, ey, ew, eh = 30, 65, 300, 200
    s.rect(ex, ey, ew, eh, fill='light')
    s.text(ex + ew // 2, ey + 22, 'Proposer Agent', size=FS_BODY, bold=True)
    s.text(ex + 12, ey + 48, '输入: 论文扩展摘要 (2000 字)', size=FS_TINY, anchor='start', fill='text_light')
    editor_lines = [
        '---',
        'theme: academic',
        '---',
        '# Transformer 注意力机制',
        '',
        '## 核心思想',
        '- 自注意力计算 Q·K^T/√d',
        '- 多头注意力并行处理',
    ]
    ch = s.code_block(ex + 10, ey + 62, ew - 20, editor_lines, font_size=11, line_h=14)
    s.text(ex + ew // 2, ey + eh - 10, '理解内容结构 → 分解为幻灯片页面', size=FS_TINY, fill='text_light')

    # Critic (Reviewer)
    cx, cy, cw, ch_h = 450, 65, 300, 200
    s.rect(cx, cy, cw, ch_h, fill='medium')
    s.text(cx + cw // 2, cy + 22, 'Reviewer Agent', size=FS_BODY, bold=True)

    s.rect(cx + 10, cy + 42, cw - 20, 38, fill='code_bg', rx=3)
    s.text(cx + 18, cy + 55, '① Slidev 渲染 → PDF/PNG', size=FS_TINY, anchor='start')
    s.text(cx + 18, cy + 70, '② Vision LLM 多维度评估', size=FS_TINY, anchor='start')

    feedback_items = [
        '页码  问题类型    严重度',
        'P3   内容过密    高',
        'P7   字体过小    中',
        'P11  配色不协调  低',
    ]
    s.rect(cx + 10, cy + 86, cw - 20, 75, fill='code_bg', rx=3)
    s.text(cx + 18, cy + 100, '结构化反馈:', size=FS_TINY, anchor='start', bold=True)
    for i, fb in enumerate(feedback_items):
        s.mono(cx + 18, cy + 118 + i * 15, fb, size=11)
    s.text(cx + cw // 2, cy + ch_h - 10, '渲染 + 视觉分析 → 可执行改进建议', size=FS_TINY, fill='text_light')

    # Arrows between Editor and Critic
    mid_y1 = ey + 70
    mid_y2 = ey + eh - 50
    s.arrow(ex + ew + 2, mid_y1, cx - 2, mid_y1)
    s.text((ex + ew + cx) / 2, mid_y1 - 12, 'Slidev 代码', size=FS_SMALL, bold=True)

    s.arrow(cx - 2, mid_y2, ex + ew + 2, mid_y2)
    s.text((ex + ew + cx) / 2, mid_y2 + 16, '结构化反馈', size=FS_SMALL, bold=True)

    # Iteration timeline
    iy = 290
    s.rect(30, iy, W - 60, 100, fill='code_bg', rx=4)
    s.text(W // 2, iy + 18, '迭代改进过程', size=FS_BODY, bold=True)

    rounds = [
        ('Round 1', '12 页初稿\n5 个问题', 'light'),
        ('Round 2', '14 页（拆分密集页）\n2 个问题', 'light'),
        ('Round 3', '14 页（字体修正）\n0 个问题 ✓', 'medium'),
    ]
    rw = 190
    rx_start = (W - 3 * rw - 2 * 30) // 2
    for i, (name, desc, fill) in enumerate(rounds):
        rx = rx_start + i * (rw + 30)
        ry = iy + 35
        s.rect(rx, ry, rw, 52, fill=fill, rx=3)
        s.text(rx + 10, ry + 16, name, size=FS_SMALL, bold=True, anchor='start')
        for j, ln in enumerate(desc.split('\n')):
            s.text(rx + 10, ry + 34 + j * 16, ln, size=FS_TINY, anchor='start', fill='text_light')
        if i < 2:
            s.arrow(rx + rw + 4, ry + 26, rx + rw + 26, ry + 26, color='dark')

    # Why not single agent
    wy = 405
    s.rect(30, wy, W - 60, 90, fill='light', rx=4)
    s.text(W // 2, wy + 20, '为何不用单 Agent？', size=FS_BODY, bold=True)

    single_x = 60
    dual_x = W // 2 + 20
    s.text(single_x, wy + 45, '单 Agent: 渲染图 ×N 轮 → 上下文爆炸', size=FS_TINY, anchor='start', fill='text_light')
    s.text(single_x, wy + 63, '(1080p 截图 = 数千 token × 14 页 × 5 轮)', size=FS_TINY, anchor='start', fill='text_light')
    s.text(dual_x, wy + 45, '双 Agent: Critic 仅看当前版本', size=FS_TINY, anchor='start')
    s.text(dual_x, wy + 63, 'Editor 仅累积文本反馈 → 上下文干净', size=FS_TINY, anchor='start')

    s.save(os.path.join(OUT, 'fig9-3.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-4: Manager 顺序协调
# ════════════════════════════════════════════════════════════════════

def fig9_4():
    W, H = 780, 480
    s = SVG(W, H)

    s.text(W // 2, 28, 'Manager 顺序协调：Sub-Agent 作为工具', size=FS_TITLE, bold=True)

    # Manager
    mx, my, mw, mh = 240, 60, 300, 100
    s.rect(mx, my, mw, mh, fill='medium')
    s.text(mx + mw // 2, my + 22, 'Manager Agent', size=FS_BODY, bold=True)
    s.text(mx + mw // 2, my + 46, '任务理解 → 分解 → 调度 → 综合', size=FS_TINY, fill='text_light')
    s.text(mx + mw // 2, my + 66, '工具集: [call_agent_A, call_agent_B,', size=FS_TINY, fill='text_light')
    s.text(mx + mw // 2, my + 82, 'call_agent_C, search, write_file]', size=FS_TINY, fill='text_light')

    # Sub-agents in sequence
    agents = [
        ('Sub-Agent A', '数据收集', '搜索技术文档\n提取关键信息', 'light'),
        ('Sub-Agent B', '分析处理', '对比分析数据\n生成统计报告', 'light'),
        ('Sub-Agent C', '报告生成', '撰写最终报告\n格式化输出', 'light'),
    ]
    aw = 210
    ax_start = (W - 3 * aw - 2 * 25) // 2
    ay = 240

    for i, (name, role, desc, fill) in enumerate(agents):
        x = ax_start + i * (aw + 25)
        s.rect(x, ay, aw, 120, fill=fill, rx=6)
        s.text(x + aw // 2, ay + 20, name, size=FS_SMALL, bold=True)
        s.text(x + aw // 2, ay + 40, f'角色: {role}', size=FS_TINY, fill='text_light')
        for j, ln in enumerate(desc.split('\n')):
            s.text(x + aw // 2, ay + 62 + j * 18, ln, size=FS_TINY, fill='text_light')

        badge_labels = [f'Step {i + 1}']
        s.badge(x + aw - 55, ay + 95, 50, 20, badge_labels[0], fill='dark', font_size=FS_TINY)

        # Arrow from Manager to sub-agent
        s.arrow(mx + mw // 2 - 100 + i * 100, my + mh + 2,
                x + aw // 2, ay - 2, color='dark')

        # Sequential arrow between sub-agents
        if i < 2:
            s.arrow(x + aw + 2, ay + 60, x + aw + 23, ay + 60)

    # Data flow
    dy = 380
    s.rect(30, dy, W - 60, 80, fill='code_bg', rx=4)
    s.text(W // 2, dy + 18, '顺序执行流', size=FS_BODY, bold=True)

    flow_items = [
        'Manager 调用 Agent A',
        '→ A 返回数据',
        '→ Manager 传递给 B',
        '→ B 返回分析',
        '→ Manager 传递给 C',
        '→ C 返回报告',
    ]
    fx_start = 55
    for i, item in enumerate(flow_items):
        s.text(fx_start + i * 118, dy + 42, item, size=FS_TINY, anchor='start',
               fill='text' if '调用' in item or '返回' in item else 'text_light')

    s.text(W // 2, dy + 65, 'Manager 视角：调用 Agent = 调用工具（发请求 → 获响应）',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-4.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-5: 书籍翻译 Agent 架构 (Exp 9.4)
# ════════════════════════════════════════════════════════════════════

def fig9_5():
    W, H = 780, 540
    s = SVG(W, H)

    s.text(W // 2, 28, '实验 9.4：书籍翻译 Agent — Manager 模式', size=FS_TITLE, bold=True)

    # Manager at top
    mx, my, mw, mh = 240, 55, 300, 70
    s.rect(mx, my, mw, mh, fill='medium')
    s.text(mx + mw // 2, my + 22, 'Manager Agent', size=FS_BODY, bold=True)
    s.text(mx + mw // 2, my + 48, '任务规划 · 进度监控 · 异常处理 · 结果综合', size=FS_TINY, fill='text_light')

    # Three sub-agents
    sub_agents = [
        (30, 'Glossary Agent', '术语对照表',
         ['接收全书 → 识别专业术语', '搜索专业词典 + 翻译规范', '输出: glossary.json'],
         ['{"attention": "注意力",', ' "transformer": "Transformer",', ' "backprop": "反向传播"}']),
        (270, 'Translation Agent ×N', '章节翻译',
         ['输入: 章节 + 术语表 + 指南', '术语严格按表翻译', '输出: chapter{n}_zh.md'],
         ['"...注意力机制通过计算', ' Query·Key^T 的相似度..."']),
        (520, 'Proofreading Agent', '全文审校',
         ['扫描验证术语一致性', '检查流畅性和可读性', '输出: review_report.md'],
         ['P3: "注意力"→"关注"不一致', 'P8: 长句建议拆分']),
    ]

    aw = 230
    ay = 170

    for x, name, role, desc, output in sub_agents:
        s.rect(x, ay, aw, 185, fill='light', rx=6)
        s.text(x + aw // 2, ay + 20, name, size=FS_SMALL, bold=True)
        s.text(x + aw // 2, ay + 38, role, size=FS_TINY, fill='text_light')

        for i, ln in enumerate(desc):
            s.text(x + 12, ay + 60 + i * 18, ln, size=FS_TINY, anchor='start', fill='text_light')

        s.rect(x + 8, ay + 115, aw - 16, 10 + len(output) * 15, fill='code_bg', rx=3)
        for i, ln in enumerate(output):
            s.mono(x + 14, ay + 128 + i * 15, ln, size=10)

        # Arrow from Manager
        s.arrow(mx + mw // 2, my + mh + 2, x + aw // 2, ay - 2, color='dark')

    # Sequential arrows between sub-agents
    s.arrow(30 + aw + 4, ay + 90, 270 - 4, ay + 90, label='术语表')
    s.arrow(270 + aw + 4, ay + 90, 520 - 4, ay + 90, label='译文')

    # Shared file system
    fy = 375
    s.rect(30, fy, W - 60, 70, fill='medium', rx=6)
    s.text(W // 2, fy + 18, '共享文件系统', size=FS_BODY, bold=True)
    files = [
        ('glossary.json', '术语对照表'),
        ('chapter{1..10}_zh.md', '章节译文'),
        ('review_report.md', '审校报告'),
        ('translation_guide.md', '翻译指南'),
    ]
    fw = (W - 80) // len(files)
    for i, (fname, desc) in enumerate(files):
        cx = 50 + i * fw + fw // 2
        s.mono(cx, fy + 40, fname, size=11, anchor='middle')
        s.text(cx, fy + 58, desc, size=FS_TINY, fill='text_light')

    # Key insight
    ky = 460
    s.rect(30, ky, W - 60, 60, fill='code_bg', rx=4)
    s.text(W // 2, ky + 18, '上下文隔离优势', size=FS_BODY, bold=True)
    s.text(W // 2, ky + 42,
           'Glossary: 仅看术语 | Translation: 仅看当前章节+术语表 | Manager: 仅维护文件索引',
           size=FS_TINY, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-5.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-6: Manager 并行协调
# ════════════════════════════════════════════════════════════════════

def fig9_6():
    W, H = 780, 500
    s = SVG(W, H)

    s.text(W // 2, 28, 'Manager 并行协调：消息总线架构', size=FS_TITLE, bold=True)

    # Orchestration Agent
    ox, oy, ow, oh = 240, 55, 300, 70
    s.rect(ox, oy, ow, oh, fill='medium')
    s.text(ox + ow // 2, oy + 22, 'Orchestration Agent', size=FS_BODY, bold=True)
    s.text(ox + ow // 2, oy + 48, '并行调度 · 实时监控 · 结果汇总', size=FS_TINY, fill='text_light')

    # Message bus
    bus_y = 155
    s.rect(50, bus_y, W - 100, 36, fill='dark', rx=4)
    s.text(W // 2, bus_y + 18, '消息总线（Message Bus）', size=FS_SMALL, fill='white', bold=True)

    s.arrow(ox + ow // 2, oy + oh + 2, ox + ow // 2, bus_y - 2)

    # Parallel agents
    agents = [
        ('Agent 1', '数据采集', '运行中 ◎', 'light'),
        ('Agent 2', '内容分析', '运行中 ◎', 'light'),
        ('Agent 3', '图表生成', '已完成 ✓', 'medium'),
        ('Agent 4', '格式校验', '等待中 ○', 'code_bg'),
    ]
    aw = 160
    gap = 14
    total = len(agents) * aw + (len(agents) - 1) * gap
    ax_start = (W - total) // 2
    ay = 225

    for i, (name, role, status, fill) in enumerate(agents):
        x = ax_start + i * (aw + gap)
        s.rect(x, ay, aw, 100, fill=fill, rx=6)
        s.text(x + aw // 2, ay + 20, name, size=FS_SMALL, bold=True)
        s.text(x + aw // 2, ay + 40, role, size=FS_TINY, fill='text_light')
        s.text(x + aw // 2, ay + 65, status, size=FS_TINY,
               fill='text_light' if '等待' in status else 'text')
        s.text(x + aw // 2, ay + 82, '独立上下文', size=FS_TINY, fill='text_light')

        s.arrow(x + aw // 2, bus_y + 38, x + aw // 2, ay - 2, color='dark')

    # Message examples
    my = 350
    s.rect(30, my, W - 60, 125, fill='code_bg', rx=4)
    s.text(W // 2, my + 18, '消息总线通信示例', size=FS_BODY, bold=True)

    messages = [
        ('Orch → Agent 1', '{"type":"start","task":"采集 arxiv 论文","params":{"query":"LLM agent"}}'),
        ('Agent 3 → Orch', '{"type":"completed","agent_id":"3","result":"charts/fig1.svg 已生成"}'),
        ('Agent 1 → Agent 2', '{"type":"data_ready","source":"agent_1","file":"raw_data.json"}'),
        ('Orch → Agent 4', '{"type":"start","depends_on":["agent_2","agent_3"]}'),
    ]
    for i, (sender, msg) in enumerate(messages):
        y = my + 40 + i * 22
        s.text(40, y, sender, size=FS_TINY, bold=True, anchor='start')
        s.mono(200, y, msg, size=10, anchor='start')

    s.save(os.path.join(OUT, 'fig9-6.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-7: Phone + Computer 双 Agent (Exp 9.5/9.6)
# ════════════════════════════════════════════════════════════════════

def fig9_7():
    W, H = 780, 560
    s = SVG(W, H)

    s.text(W // 2, 28, '实验 9.5/9.6：Phone + Computer 双 Agent', size=FS_TITLE, bold=True)

    # Phone Agent (left)
    px, py, pw, ph = 30, 65, 310, 240
    s.rect(px, py, pw, ph, fill='light', rx=6)
    s.text(px + pw // 2, py + 22, 'Phone Agent', size=FS_BODY, bold=True)
    s.text(px + pw // 2, py + 42, 'Node.js · 实时语音通话', size=FS_TINY, fill='text_light')

    phone_pipeline = [
        ('用户语音', '麦克风输入', 'medium'),
        ('VAD + ASR', 'Silero VAD → STT 转录', 'light'),
        ('LLM 推理', '理解意图 + 提取信息', 'light'),
        ('TTS 合成', '生成语音回复 → 播放', 'medium'),
    ]
    for i, (label, desc, fill) in enumerate(phone_pipeline):
        y = py + 60 + i * 42
        s.rect(px + 10, y, pw - 20, 36, fill=fill, rx=3)
        s.text(px + 20, y + 14, label, size=FS_TINY, bold=True, anchor='start')
        s.text(px + 20, y + 28, desc, size=11, anchor='start', fill='text_light')
        if i < len(phone_pipeline) - 1:
            s.arrow(px + pw // 2, y + 38, px + pw // 2, y + 42, color='dark')

    # Computer Agent (right)
    cx, cy, cw, ch_h = 440, 65, 310, 240
    s.rect(cx, cy, cw, ch_h, fill='light', rx=6)
    s.text(cx + cw // 2, cy + 22, 'Computer Agent', size=FS_BODY, bold=True)
    s.text(cx + cw // 2, cy + 42, 'Python · 浏览器自动化', size=FS_TINY, fill='text_light')

    comp_pipeline = [
        ('屏幕截图', '浏览器当前页面', 'medium'),
        ('Vision LLM', '理解页面结构 + 表单字段', 'light'),
        ('动作规划', '定位字段 → 规划输入序列', 'light'),
        ('执行操作', '点击 / 输入 / 提交', 'medium'),
    ]
    for i, (label, desc, fill) in enumerate(comp_pipeline):
        y = cy + 60 + i * 42
        s.rect(cx + 10, y, cw - 20, 36, fill=fill, rx=3)
        s.text(cx + 20, y + 14, label, size=FS_TINY, bold=True, anchor='start')
        s.text(cx + 20, y + 28, desc, size=11, anchor='start', fill='text_light')
        if i < len(comp_pipeline) - 1:
            s.arrow(cx + cw // 2, y + 38, cx + cw // 2, y + 42, color='dark')

    # WebSocket connection between agents
    ws_y = py + ph + 15
    s.rect(30, ws_y, W - 60, 36, fill='dark', rx=4)
    s.text(W // 2, ws_y + 18, 'WebSocket 双向通信 (ws://localhost:8849)', size=FS_SMALL, fill='white', bold=True)

    s.arrow(px + pw // 2, py + ph + 2, px + pw // 2, ws_y - 2, color='dark')
    s.arrow(cx + cw // 2, cy + ch_h + 2, cx + cw // 2, ws_y - 2, color='dark')

    # Message examples
    my = ws_y + 50
    s.rect(30, my, W - 60, 150, fill='code_bg', rx=4)
    s.text(W // 2, my + 18, '实时双向消息流（边打电话边用电脑）', size=FS_BODY, bold=True)

    msgs = [
        ('Phone → Computer', '[FROM_PHONE_AGENT] 用户说姓名是张三', '→'),
        ('Computer → Phone', '[FROM_COMPUTER_AGENT] 已填写姓名，需要证件号', '←'),
        ('Phone → Computer', '[FROM_PHONE_AGENT] 证件号 310101199001011234', '→'),
        ('Computer → Phone', '[FROM_COMPUTER_AGENT] 表单已提交，注册成功', '←'),
    ]
    for i, (sender, content, direction) in enumerate(msgs):
        y = my + 42 + i * 26
        s.text(42, y, sender, size=FS_TINY, bold=True, anchor='start',
               fill='text' if '→' == direction else 'text_light')
        s.mono(210, y, content, size=10, anchor='start')

    # Key point
    s.text(W // 2, my + 140,
           '关键：两个 Agent 独立 ReAct 循环并行运行，互不阻塞',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-7.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-8: 并行网页搜集 Agent (Exp 9.7)
# ════════════════════════════════════════════════════════════════════

def fig9_8():
    W, H = 780, 530
    s = SVG(W, H)

    s.text(W // 2, 28, '实验 9.7：并行 Web Scraping — 级联终止', size=FS_TITLE, bold=True)

    # Orchestration Agent
    ox, oy, ow, oh = 230, 55, 320, 65
    s.rect(ox, oy, ow, oh, fill='medium')
    s.text(ox + ow // 2, oy + 20, 'Orchestration Agent', size=FS_BODY, bold=True)
    s.text(ox + ow // 2, oy + 44, '动态创建 · 实时监控 · 级联终止', size=FS_TINY, fill='text_light')

    # Parallel Computer Use Agents
    agents = [
        ('Agent 1', 'cs.edu.cn', '搜索中... ◎', 'light'),
        ('Agent 2', 'math.edu.cn', '未找到 ✗', '#e8e8e8'),
        ('Agent 3', 'phys.edu.cn', '找到！ ✓', 'medium'),
        ('Agent 4', 'chem.edu.cn', '已终止 ⊘', 'code_bg'),
        ('Agent 5', 'bio.edu.cn', '已终止 ⊘', 'code_bg'),
    ]
    aw = 130
    gap = 12
    total_w = len(agents) * aw + (len(agents) - 1) * gap
    ax_start = (W - total_w) // 2
    ay = 160

    for i, (name, url, status, fill) in enumerate(agents):
        x = ax_start + i * (aw + gap)
        s.rect(x, ay, aw, 95, fill=fill, rx=4)
        s.text(x + aw // 2, ay + 16, name, size=FS_SMALL, bold=True)
        s.mono(x + aw // 2, ay + 35, url, size=10, anchor='middle')
        s.text(x + aw // 2, ay + 55, '教师名录搜索', size=FS_TINY, fill='text_light')
        s.text(x + aw // 2, ay + 75, status, size=FS_TINY,
               bold=('找到' in status), fill='text' if '找到' in status else 'text_light')

        s.arrow(ox + ow // 2, oy + oh + 2, x + aw // 2, ay - 2, color='dark')

    # Cascade termination flow
    ty = 280
    s.rect(30, ty, W - 60, 120, fill='code_bg', rx=4)
    s.text(W // 2, ty + 18, '级联终止时序', size=FS_BODY, bold=True)

    timeline = [
        ('t=0s', '启动 5 个 Agent\n并行搜索教师"张伟"'),
        ('t=12s', 'Agent 2 完成\n未找到 → 正常退出'),
        ('t=18s', 'Agent 3 找到目标!\n发送 target_found'),
        ('t=18.1s', 'Orch 广播 terminate\n给 Agent 1,4,5'),
        ('t=19s', '全部确认终止\n汇总结果返回'),
    ]
    tw = 130
    tx_start = (W - len(timeline) * tw) // 2
    for i, (time, desc) in enumerate(timeline):
        x = tx_start + i * tw
        s.text(x + tw // 2, ty + 42, time, size=FS_SMALL, bold=True)
        for j, ln in enumerate(desc.split('\n')):
            s.text(x + tw // 2, ty + 60 + j * 16, ln, size=FS_TINY, fill='text_light')
        if i < len(timeline) - 1:
            s.arrow(x + tw - 2, ty + 55, x + tw + 4, ty + 55, color='dark')

    # Result and comparison
    ry = 420
    s.rect(30, ry, 340, 85, fill='light', rx=4)
    s.text(200, ry + 18, '找到结果', size=FS_BODY, bold=True)
    result_lines = [
        '姓名: 张伟  学院: 物理学院',
        '职位: 教授  方向: 量子计算',
        '邮箱: zhangwei@phys.edu.cn',
    ]
    for i, ln in enumerate(result_lines):
        s.mono(50, ry + 40 + i * 16, ln, size=11)

    s.rect(400, ry, 350, 85, fill='medium', rx=4)
    s.text(575, ry + 18, '性能对比', size=FS_BODY, bold=True)
    s.text(420, ry + 42, '串行: 10 个网站 × 30s = ~5 分钟', size=FS_TINY, anchor='start', fill='text_light')
    s.text(420, ry + 60, '并行: 18 秒找到 + 1 秒终止 = 19 秒', size=FS_TINY, anchor='start', bold=True)
    s.text(420, ry + 78, '加速比: ~15×（含级联终止优化）', size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-8.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-9: Handoff 链式模式
# ════════════════════════════════════════════════════════════════════

def fig9_9():
    W, H = 780, 440
    s = SVG(W, H)

    s.text(W // 2, 28, 'Handoff 链式模式：对等移交 + 契约式协作', size=FS_TITLE, bold=True)

    nodes = [
        ('Agent A', '需求分析', '输出: 结构化需求文档\nspec.json', 'medium'),
        ('Agent B', '架构设计', '输出: 技术设计文档\ndesign.md', 'light'),
        ('Agent C', '代码实现', '输出: 源代码\nsrc/*.py', 'light'),
        ('Agent D', '测试验证', '输出: 测试报告\ntest_report.md', 'medium'),
    ]

    nw, nh = 160, 130
    gap = 22
    total_w = len(nodes) * nw + (len(nodes) - 1) * gap
    nx_start = (W - total_w) // 2
    ny = 60

    for i, (name, role, output, fill) in enumerate(nodes):
        x = nx_start + i * (nw + gap)
        s.rect(x, ny, nw, nh, fill=fill, rx=6)
        s.text(x + nw // 2, ny + 20, name, size=FS_SMALL, bold=True)
        s.text(x + nw // 2, ny + 40, role, size=FS_TINY, fill='text_light')

        s.rect(x + 8, ny + 55, nw - 16, 50, fill='code_bg', rx=3)
        for j, ln in enumerate(output.split('\n')):
            s.text(x + nw // 2, ny + 72 + j * 16, ln, size=FS_TINY, fill='text_light')

        s.text(x + nw // 2, ny + nh - 8, '完成后移交 →', size=FS_TINY, fill='text_light')

        if i < len(nodes) - 1:
            s.arrow(x + nw + 4, ny + nh // 2, x + nw + gap - 4, ny + nh // 2)

    # Handoff data detail
    hy = 215
    s.rect(30, hy, W - 60, 90, fill='code_bg', rx=4)
    s.text(W // 2, hy + 18, 'Handoff 传递内容（Agent A → Agent B 示例）', size=FS_BODY, bold=True)

    handoff_fields = [
        ('触发条件', 'A 完成需求文档 → is_complete=True'),
        ('目标 Agent', 'target="architect" (Agent B)'),
        ('传递内容', 'files=["spec.json"] + summary="电商系统: 3个微服务, REST API"'),
        ('移交后状态', 'status="退出" (释放资源, 不保持待命)'),
    ]
    for i, (field, value) in enumerate(handoff_fields):
        y = hy + 38 + i * 16
        s.text(42, y, field + ':', size=FS_TINY, bold=True, anchor='start')
        s.text(150, y, value, size=FS_TINY, anchor='start', fill='text_light')

    # Comparison with Manager mode
    cy = 320
    s.rect(30, cy, 340, 100, fill='light', rx=4)
    s.text(200, cy + 18, '去中心化优势', size=FS_SMALL, bold=True)
    advantages = [
        '✓ 无需中心 Manager 理解所有角色',
        '✓ 清晰职责边界，接口解耦',
        '✓ Engineer 可多实例并行',
    ]
    for i, adv in enumerate(advantages):
        s.text(48, cy + 42 + i * 20, adv, size=FS_TINY, anchor='start', fill='text_light')

    s.rect(400, cy, 350, 100, fill='light', rx=4)
    s.text(575, cy + 18, '去中心化局限', size=FS_SMALL, bold=True)
    limits = [
        '✗ 缺乏全局优化视野',
        '✗ 异常处理困难（无中心协调）',
        '✗ 流程固定，难以动态调整',
    ]
    for i, lim in enumerate(limits):
        s.text(418, cy + 42 + i * 20, lim, size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-9.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-10: MetaGPT SOP 流水线
# ════════════════════════════════════════════════════════════════════

def fig9_10():
    W, H = 780, 530
    s = SVG(W, H)

    s.text(W // 2, 28, 'MetaGPT SOP 流水线：标准化文档驱动', size=FS_TITLE, bold=True)

    roles = [
        ('Product Manager', 'medium',
         '输入: 用户需求描述',
         ['功能列表 + 优先级', '用户故事 (5 条)', '验收标准'],
         'docs/PRD.md'),
        ('Architect', 'light',
         '输入: PRD.md',
         ['技术栈: FastAPI+React', 'API 规范 (OpenAPI)', '数据库 Schema'],
         'docs/design.md'),
        ('Engineer ×3', 'light',
         '输入: design.md + 模块规约',
         ['模块 A: 用户服务', '模块 B: 订单服务', '模块 C: 支付服务'],
         'src/*.py'),
        ('QA Engineer', 'medium',
         '输入: src/ + PRD.md',
         ['单元测试 (pytest)', '集成测试 (API)', 'Bug 报告 → Engineer'],
         'docs/test_report.md'),
    ]

    rw = 170
    gap = 16
    total_w = len(roles) * rw + (len(roles) - 1) * gap
    rx_start = (W - total_w) // 2
    ry = 55

    for i, (name, fill, input_desc, outputs, artifact) in enumerate(roles):
        x = rx_start + i * (rw + gap)

        s.rect(x, ry, rw, 230, fill=fill, rx=6)
        s.text(x + rw // 2, ry + 20, name, size=FS_SMALL, bold=True)

        s.text(x + 8, ry + 42, input_desc, size=11, anchor='start', fill='text_light')

        s.rect(x + 8, ry + 58, rw - 16, 20 + len(outputs) * 16, fill='code_bg', rx=3)
        s.text(x + 14, ry + 72, '产出:', size=FS_TINY, bold=True, anchor='start')
        for j, out in enumerate(outputs):
            s.text(x + 14, ry + 88 + j * 16, out, size=11, anchor='start', fill='text_light')

        s.rect(x + 8, ry + 168, rw - 16, 30, fill='dark', rx=12)
        s.mono(x + rw // 2, ry + 183, artifact, size=11, anchor='middle', fill='white')

        if i < len(roles) - 1:
            ax1 = x + rw + 2
            ax2 = x + rw + gap - 2
            s.arrow(ax1, ry + 115, ax2, ry + 115)

    # QA → Engineer feedback loop
    qa_x = rx_start + 3 * (rw + gap) + rw // 2
    eng_x = rx_start + 2 * (rw + gap) + rw // 2
    s.arrow_curved(qa_x, ry + 230 + 5, eng_x, ry + 230 + 5, curve=-30, label='Bug 修复', dash=True)

    # Shared file system
    fy = 310
    s.rect(30, fy, W - 60, 50, fill='medium', rx=4)
    s.text(W // 2, fy + 16, '共享项目目录', size=FS_SMALL, bold=True)
    s.mono(W // 2, fy + 36, 'docs/PRD.md  docs/design.md  src/*.py  docs/test_report.md',
           size=11, anchor='middle')

    # Key insight
    ky = 375
    s.rect(30, ky, W - 60, 130, fill='code_bg', rx=4)
    s.text(W // 2, ky + 18, 'MetaGPT 核心设计', size=FS_BODY, bold=True)

    insights = [
        ('标准化文档', '每个角色输出明确格式 — 下游只需理解格式，不需理解上游思考过程'),
        ('接口解耦', '改进 PM（换更强模型）只要输出符合 PRD 格式，下游零修改'),
        ('无 Manager', '控制权沿 DAG 自然流动：PM→Arch→Eng→QA，无中心调度开销'),
        ('异常通道', 'QA 测试失败 → Bug 报告按模块路由回 Engineer → 迭代修复'),
    ]
    for i, (title, desc) in enumerate(insights):
        y = ky + 42 + i * 24
        s.text(42, y, '▸ ' + title, size=FS_SMALL, bold=True, anchor='start')
        s.text(180, y, desc, size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-10.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-11: VLA 架构（Vision-Language-Action）—— 三种技术路径对比
# ════════════════════════════════════════════════════════════════════

def fig9_11():
    W, H = 900, 620
    s = SVG(W, H)

    # 共同输入
    in_x, in_y, in_w, in_h = 230, 55, 440, 64
    s.rect(in_x, in_y, in_w, in_h, fill='medium', rx=6)
    s.text(in_x + in_w / 2, in_y + 22, '共同输入：摄像头画面 + 语言指令', size=FS_SMALL, bold=True)
    s.text(in_x + in_w / 2, in_y + 44, '"把红色积木放到蓝色盒子里"', size=FS_TINY, fill='text_light')

    # 向三个分支引出箭头
    s.arrow(in_x + 70, in_y + in_h + 2, 145, 165)   # → OpenVLA
    s.arrow(W / 2, in_y + in_h + 2, W / 2, 165)     # → π₀
    s.arrow(in_x + in_w - 70, in_y + in_h + 2, 755, 165)  # → RT-2

    # 三栏架构
    col_w, col_gap = 270, 30
    cols_total = 3 * col_w + 2 * col_gap
    sx0 = (W - cols_total) / 2  # = 30

    columns = [
        ('OpenVLA', '开源 · 离散动作 token', 'light', [
            ('视觉编码器', 'DINOv2 + SigLIP', '提取像素特征'),
            ('LLM 主干', 'Llama 2 (7B)', '理解指令与场景'),
            ('解码方式', '自回归 · 文本 token', '动作切分成离散选项'),
            ('动作输出', '"a=[3,−2,5,...]" tokens', '逐步生成 7-DOF 控制量'),
        ]),
        ('π₀（Pi-Zero）', '扩散策略 · 平滑轨迹', 'medium', [
            ('视觉编码器', 'ViT 多视角融合', '提取像素特征'),
            ('Mixture-of-Transformers', '快慢分离主干', '语言慢思考 + 控制快思考'),
            ('解码方式', '扩散去噪迭代', '先粗后精打磨整段轨迹'),
            ('动作输出', '连续动作序列（50 步/批）', '高频流畅控制信号'),
        ]),
        ('RT-2', '语言模型即动作模型', 'light', [
            ('视觉-语言主干', 'PaLI-X / PaLM-E', 'VLM 端到端理解'),
            ('动作表示', '动作 → 自然语言 token', '"move arm 5cm right"'),
            ('解码方式', '复用 VLM 自回归', '与文本生成共享权重'),
            ('动作输出', '文本描述 → 控制器解析', '继承 VLM 的语义泛化'),
        ]),
    ]

    top_y = 165
    title_h = 50
    row_h = 80
    for i, (name, tag, fill, rows) in enumerate(columns):
        cx = sx0 + i * (col_w + col_gap)
        # 列容器
        col_total_h = title_h + len(rows) * row_h + 14
        s.rect(cx, top_y, col_w, col_total_h, fill='white', stroke='border')
        # 标题条
        s.rect(cx, top_y, col_w, title_h, fill=fill)
        s.text(cx + col_w / 2, top_y + 18, name, size=FS_BODY, bold=True)
        s.text(cx + col_w / 2, top_y + 38, tag, size=FS_TINY, fill='text_light')

        # 各行
        for j, (label, value, hint) in enumerate(rows):
            ry = top_y + title_h + 8 + j * row_h
            s.rect(cx + 10, ry, col_w - 20, row_h - 8, fill='code_bg', rx=4)
            s.text(cx + col_w / 2, ry + 18, label, size=FS_TINY, bold=True)
            s.text(cx + col_w / 2, ry + 38, value, size=FS_TINY)
            s.text(cx + col_w / 2, ry + 56, hint, size=FS_TINY, fill='text_light')

    # 底部：统一输出层
    out_y = top_y + title_h + 4 * row_h + 14 + 24
    s.rect(30, out_y, W - 60, 50, fill='darker', rx=6)
    s.text(W / 2, out_y + 18,
           '机器人控制信号：7-DOF 关节角度 / 末端位姿',
           size=FS_SMALL, bold=True, fill='white')
    s.text(W / 2, out_y + 36,
           '差异在"如何告诉机器人下一步该怎么动"，最终都落到统一的控制接口',
           size=FS_TINY, fill='white')

    s.save(os.path.join(OUT, 'fig9-11.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-12: 语音狼人杀 Agent 系统 (Exp 9.9)
# ════════════════════════════════════════════════════════════════════

def fig9_12():
    W, H = 780, 550
    s = SVG(W, H)

    s.text(W // 2, 28, '实验 9.9：语音狼人杀 — 信息权限控制', size=FS_TITLE, bold=True)

    # Judge (code-driven)
    jx, jy, jw, jh = 260, 55, 260, 75
    s.rect(jx, jy, jw, jh, fill='dark', rx=6)
    s.text(jx + jw // 2, jy + 20, '法官（代码驱动）', size=FS_BODY, bold=True, fill='white')
    s.text(jx + jw // 2, jy + 42, '游戏状态 · 阶段控制 · 信息分发', size=FS_TINY, fill='white')
    s.text(jx + jw // 2, jy + 58, 'Night → Day → Vote → Settle', size=FS_TINY, fill='white')

    # Role agents
    roles = [
        (40, '狼人 1', '🐺', 'medium',
         ['可见: 同伴身份', '策略: 伪装村民', '夜晚: 选择目标']),
        (185, '狼人 2', '🐺', 'medium',
         ['可见: 同伴身份', '策略: 跟票保护', '夜晚: 协商目标']),
        (330, '预言家', '🔮', 'light',
         ['可见: 验人结果', '策略: 择机跳出', '夜晚: 查验 1 人']),
        (475, '女巫', '🧪', 'light',
         ['可见: 死亡/救治', '策略: 保药/解药', '夜晚: 救/毒 1 人']),
        (620, '村民 ×2', '👤', '#e8e8e8',
         ['可见: 仅公开信息', '策略: 逻辑推理', '白天: 分析发言']),
    ]

    aw, ay = 135, 180
    for x, name, icon, fill, info in roles:
        s.rect(x, ay, aw, 140, fill=fill, rx=6)
        s.text(x + aw // 2, ay + 18, f'{icon} {name}', size=FS_SMALL, bold=True)
        for i, ln in enumerate(info):
            s.text(x + aw // 2, ay + 42 + i * 20, ln, size=11, fill='text_light')

        # Arrow from Judge
        s.arrow(jx + jw // 2, jy + jh + 2, x + aw // 2, ay - 2, color='dark')

        # Permission badge
        if '狼人' in name:
            s.badge(x + aw - 45, ay + aw - 15, 40, 18, '互知', fill='darker', font_size=11)
        elif '预言' in name:
            s.badge(x + aw - 55, ay + aw - 15, 50, 18, '验人结果', fill='darker', font_size=10)

    # Info permission control
    iy = 340
    s.rect(30, iy, W - 60, 90, fill='code_bg', rx=4)
    s.text(W // 2, iy + 18, '信息权限控制：法官按角色过滤上下文', size=FS_BODY, bold=True)

    perms = [
        ('狼人', '所有狼人身份 + 夜晚商议 + 公开发言'),
        ('预言家', '验人结果(仅自己验的) + 公开发言'),
        ('女巫', '当晚死亡者 + 解药/毒药状态 + 公开发言'),
        ('村民', '仅公开发言 + 投票记录（零私有信息）'),
    ]
    pw = (W - 80) // 2
    for i, (role, perm) in enumerate(perms):
        row, col = i // 2, i % 2
        x = 50 + col * pw
        y = iy + 40 + row * 22
        s.text(x, y, role + ':', size=FS_TINY, bold=True, anchor='start')
        s.text(x + 55, y, perm, size=FS_TINY, anchor='start', fill='text_light')

    # Voice interaction
    vy = 445
    s.rect(30, vy, W - 60, 85, fill='light', rx=4)
    s.text(W // 2, vy + 18, '实时语音交互（ASR + LLM + TTS）', size=FS_BODY, bold=True)

    voice_flow = [
        ('白天讨论', '法官管理发言顺序\n按座位依次发言'),
        ('投票阶段', '收集所有玩家投票\n统计票数公布结果'),
        ('夜晚阶段', '法官依次唤醒角色\n私密语音通道'),
        ('真人玩家', '随机分配角色\n语音表达投票/发言'),
    ]
    vw = (W - 80) // len(voice_flow)
    for i, (title, desc) in enumerate(voice_flow):
        cx = 50 + i * vw + vw // 2
        s.text(cx, vy + 42, title, size=FS_SMALL, bold=True)
        for j, ln in enumerate(desc.split('\n')):
            s.text(cx, vy + 60 + j * 16, ln, size=FS_TINY, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-12.svg'))


# ════════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════════

def main():
    os.makedirs(OUT, exist_ok=True)

    figs = [
        ('fig9-1', fig9_1),
        ('fig9-2', fig9_2),
        ('fig9-3', fig9_3),
        ('fig9-4', fig9_4),
        ('fig9-5', fig9_5),
        ('fig9-6', fig9_6),
        ('fig9-7', fig9_7),
        ('fig9-8', fig9_8),
        ('fig9-9', fig9_9),
        ('fig9-10', fig9_10),
        ('fig9-11', fig9_11),
        ('fig9-12', fig9_12),
    ]

    for name, func in figs:
        func()
        print(f'  ✓ {name}')

    print(f'\nGenerated {len(figs)} figures in {OUT}/')


if __name__ == '__main__':
    main()
