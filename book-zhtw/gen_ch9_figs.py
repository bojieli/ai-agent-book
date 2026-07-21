"""[DEPRECATED] Old Chapter 9 (multi-Agent) figure generator.

⚠️ DO NOT RUN: 2026-03-12 重構後，章節編號變化（原第 9 章 → 第 10 章）。
此檔案生成的圖實際是當前【第 10 章】內容（多 Agent 協作），但仍儲存為 fig9-*.svg，
若執行會覆蓋當前正確的【第 9 章】（多模態與實時互動）圖，導致內容錯位。

當前正確的第 9 章 SVG（多模態/語音/Computer Use/VLA/Sim2Real）由
2026-03-12 提交 a33c88f 從原 fig8-*.svg 重新命名而來；當前正確的第 10 章 SVG
（多 Agent 協作）由本檔案原本生成的內容**手工遷移**到 fig10-*.svg。

要重新生成本檔案中的圖，應改為生成 fig10-*.svg 並對照 chapter10.md 引用名。

Original (now Ch 10) figure list:
  fig10-1:  共享上下文 vs 獨立上下文 (concrete context windows)
  fig10-2:  基於階段的角色切換 (prompt/tool-set changes per phase)
  fig10-3:  Proposer-Reviewer 迴圈 (Slidev PPT iterative feedback)
  fig10-4:  Manager 順序協調 (sequential sub-agent delegation)
  fig10-5:  書籍翻譯 Agent 架構 (NEW — Exp 10.4)
  fig10-6:  Manager 並行協調 (concurrent agents + message bus)
  fig10-7:  Phone + Computer 雙 Agent (NEW — Exp 10.5/10.6)
  fig10-8:  並行網頁蒐集 (NEW — Exp 10.7)
  fig10-9:  Handoff 鏈式模式 (peer control passing)
  fig10-10: MetaGPT SOP 流水線 (PM→Arch→Eng→QA with artifacts)
  fig10-11: AI 小鎮架構 (memory stream + reflection + planning)
  fig10-12: 語音狼人殺 Agent 系統 (NEW — Exp 10.9)
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
#  fig9-1: 共享上下文 vs 獨立上下文
# ════════════════════════════════════════════════════════════════════

def fig9_1():
    W, H = 780, 560
    s = SVG(W, H)

    s.text(W // 2, 30, '共享上下文 vs 獨立上下文', size=FS_TITLE, bold=True)

    col_w = 350
    lx, rx = 20, W - col_w - 20

    # ── Left: shared context ──
    s.group_box(lx, 55, col_w, 480, '共享上下文（單 Agent 多階段）')

    ctx_x, ctx_w = lx + 15, col_w - 30
    phases = [
        ('階段 1：需求分析師', 'medium', [
            'sys: "你的職責是充分理解需求..."',
            'tools: [ask_question, save_req]',
            'user: "寫一個 CSV 分析指令碼"',
            'agent: "需要處理哪些檔案型別？"',
        ]),
        ('階段 2：軟體工程師', 'light', [
            'sys: "根據已確認需求編寫程式碼..."',
            'tools: [write_file, execute_code]',
            'agent: write_file("analyze.py", ...)',
            'agent: execute_code("python test.py")',
        ]),
        ('階段 3：程式碼審查員', 'light', [
            'sys: "審查程式碼質量和安全性..."',
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
    s.text(ctx_x + ctx_w // 2, cy + 14, '↑ 所有階段共享同一對話歷史', size=FS_TINY, bold=True)
    cy += 36

    s.text(lx + col_w // 2, cy + 10, '✓ 完整執行軌跡', size=FS_SMALL, fill='text_light')
    s.text(lx + col_w // 2, cy + 32, '✗ 上下文快速膨脹', size=FS_SMALL, fill='text_light')

    # ── Right: independent context ──
    s.group_box(rx, 55, col_w, 480, '獨立上下文（真正多 Agent）')

    agents_data = [
        ('Glossary Agent', [
            'sys: "識別術語並翻譯..."',
            'tools: [search_dict, write_file]',
            '→ glossary.json',
        ]),
        ('Translation Agent', [
            'sys: "翻譯本章內容..."',
            'tools: [read_file, write_file]',
            '→ chapter3_zh.md',
        ]),
        ('Proofreading Agent', [
            'sys: "檢查術語一致性..."',
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
    s.text(rx + 15 + ctx_w // 2, fs_y + 16, '共享檔案系統', size=FS_SMALL, bold=True)
    files = ['glossary.json', 'chapter3_zh.md', 'review_report.md']
    s.mono(rx + 27, fs_y + 38, '  '.join(files), size=11)
    s.text(rx + 15 + ctx_w // 2, fs_y + 55, '+ 工具呼叫引數傳遞結構化資料', size=FS_TINY, fill='text_light')

    s.text(rx + col_w // 2, fs_y + 82, '✓ 模組化 · 可擴充套件 · 並行', size=FS_SMALL, fill='text_light')
    s.text(rx + col_w // 2, fs_y + 104, '✗ 資訊同步複雜', size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-1.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-2: 基於階段的角色切換
# ════════════════════════════════════════════════════════════════════

def fig9_2():
    W, H = 780, 520
    s = SVG(W, H)

    s.text(W // 2, 28, '基於階段的角色切換：Coding Agent 三階段', size=FS_TITLE, bold=True)

    phases = [
        ('需求分析師', 'medium',
         '"你的職責是充分理解需求。\n不要急於實現，在這個階段\n你的任務是提問和確認。"',
         ['ask_clarifying_question(q)', 'save_requirement(k, v)', 'complete_requirements_analysis()'],
         'complete_requirements_analysis()'),
        ('軟體工程師', 'light',
         '"根據已確認的需求編寫\n高質量 Python 程式碼。遵循\n模組化、錯誤處理最佳實踐。"',
         ['write_file(path, content)', 'read_file(path)', 'execute_code(code)'],
         'submit_for_review()'),
        ('程式碼審查員', '#e8e8e8',
         '"從多個維度評估程式碼質量：\n功能正確性、程式碼規範、\n安全性。採用批判性思維。"',
         ['run_linter(file)', 'run_tests(file)', 'analyze_complexity(file)'],
         None),
    ]

    s.rect(30, 55, W - 60, 28, fill='code_bg', rx=3)
    s.text(W // 2, 69, '▼ 同一上下文連續流動 — 對話歷史在階段間完整保留 ▼', size=FS_SMALL, bold=True)

    pw = 225
    gap = 18
    px_start = (W - 3 * pw - 2 * gap) // 2
    py = 100

    for i, (role, fill, prompt, tools, trigger) in enumerate(phases):
        x = px_start + i * (pw + gap)

        s.rect(x, py, pw, 380, fill=fill, rx=6)
        s.text(x + pw // 2, py + 22, f'階段 {i + 1}', size=FS_TINY, fill='text_light')
        s.text(x + pw // 2, py + 42, role, size=FS_BODY, bold=True)

        s.rect(x + 8, py + 60, pw - 16, 88, fill='code_bg', rx=3)
        s.text(x + 14, py + 75, '系統提示詞', size=FS_TINY, fill='text_light', anchor='start')
        for j, ln in enumerate(prompt.split('\n')):
            s.text(x + 14, py + 92 + j * 16, ln, size=12, anchor='start', fill='text_light')

        s.rect(x + 8, py + 158, pw - 16, 18 + len(tools) * 20, fill='white', rx=3)
        s.text(x + 14, py + 172, '工具集', size=FS_TINY, fill='text_light', anchor='start')
        for j, tool in enumerate(tools):
            s.mono(x + 14, py + 190 + j * 20, tool, size=11)

        if trigger:
            ty = py + 290
            s.rect(x + 8, ty, pw - 16, 48, fill='dark', rx=12)
            s.text(x + pw // 2, ty + 16, '觸發轉換', size=FS_TINY, fill='white')
            s.mono(x + pw // 2, ty + 34, trigger, size=10, anchor='middle', fill='white')

        if i < 2:
            ax1 = x + pw + 2
            ax2 = x + pw + gap - 2
            ay = py + 310
            s.arrow(ax1, ay, ax2, ay)

    s.text(W // 2, H - 10, '角色轉換：更新系統提示詞 + 工具集，對話歷史和狀態連續保留',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-2.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-3: Proposer-Reviewer 迴圈（Slidev PPT 生成）
# ════════════════════════════════════════════════════════════════════

def fig9_3():
    W, H = 780, 520
    s = SVG(W, H)

    s.text(W // 2, 28, 'Proposer-Reviewer 迴圈：Slidev PPT 生成', size=FS_TITLE, bold=True)

    # Editor (Proposer)
    ex, ey, ew, eh = 30, 65, 300, 200
    s.rect(ex, ey, ew, eh, fill='light')
    s.text(ex + ew // 2, ey + 22, 'Proposer Agent', size=FS_BODY, bold=True)
    s.text(ex + 12, ey + 48, '輸入: 論文擴充套件摘要 (2000 字)', size=FS_TINY, anchor='start', fill='text_light')
    editor_lines = [
        '---',
        'theme: academic',
        '---',
        '# Transformer 注意力機制',
        '',
        '## 核心思想',
        '- 自注意力計算 Q·K^T/√d',
        '- 多頭注意力並行處理',
    ]
    ch = s.code_block(ex + 10, ey + 62, ew - 20, editor_lines, font_size=11, line_h=14)
    s.text(ex + ew // 2, ey + eh - 10, '理解內容結構 → 分解為幻燈片頁面', size=FS_TINY, fill='text_light')

    # Critic (Reviewer)
    cx, cy, cw, ch_h = 450, 65, 300, 200
    s.rect(cx, cy, cw, ch_h, fill='medium')
    s.text(cx + cw // 2, cy + 22, 'Reviewer Agent', size=FS_BODY, bold=True)

    s.rect(cx + 10, cy + 42, cw - 20, 38, fill='code_bg', rx=3)
    s.text(cx + 18, cy + 55, '① Slidev 渲染 → PDF/PNG', size=FS_TINY, anchor='start')
    s.text(cx + 18, cy + 70, '② Vision LLM 多維度評估', size=FS_TINY, anchor='start')

    feedback_items = [
        '頁碼  問題型別    嚴重度',
        'P3   內容過密    高',
        'P7   字型過小    中',
        'P11  配色不協調  低',
    ]
    s.rect(cx + 10, cy + 86, cw - 20, 75, fill='code_bg', rx=3)
    s.text(cx + 18, cy + 100, '結構化反饋:', size=FS_TINY, anchor='start', bold=True)
    for i, fb in enumerate(feedback_items):
        s.mono(cx + 18, cy + 118 + i * 15, fb, size=11)
    s.text(cx + cw // 2, cy + ch_h - 10, '渲染 + 視覺分析 → 可執行改進建議', size=FS_TINY, fill='text_light')

    # Arrows between Editor and Critic
    mid_y1 = ey + 70
    mid_y2 = ey + eh - 50
    s.arrow(ex + ew + 2, mid_y1, cx - 2, mid_y1)
    s.text((ex + ew + cx) / 2, mid_y1 - 12, 'Slidev 程式碼', size=FS_SMALL, bold=True)

    s.arrow(cx - 2, mid_y2, ex + ew + 2, mid_y2)
    s.text((ex + ew + cx) / 2, mid_y2 + 16, '結構化反饋', size=FS_SMALL, bold=True)

    # Iteration timeline
    iy = 290
    s.rect(30, iy, W - 60, 100, fill='code_bg', rx=4)
    s.text(W // 2, iy + 18, '迭代改進過程', size=FS_BODY, bold=True)

    rounds = [
        ('Round 1', '12 頁初稿\n5 個問題', 'light'),
        ('Round 2', '14 頁（拆分密集頁）\n2 個問題', 'light'),
        ('Round 3', '14 頁（字型修正）\n0 個問題 ✓', 'medium'),
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
    s.text(W // 2, wy + 20, '為何不用單 Agent？', size=FS_BODY, bold=True)

    single_x = 60
    dual_x = W // 2 + 20
    s.text(single_x, wy + 45, '單 Agent: 渲染圖 ×N 輪 → 上下文爆炸', size=FS_TINY, anchor='start', fill='text_light')
    s.text(single_x, wy + 63, '(1080p 截圖 = 數千 token × 14 頁 × 5 輪)', size=FS_TINY, anchor='start', fill='text_light')
    s.text(dual_x, wy + 45, '雙 Agent: Critic 僅看當前版本', size=FS_TINY, anchor='start')
    s.text(dual_x, wy + 63, 'Editor 僅累積文字反饋 → 上下文乾淨', size=FS_TINY, anchor='start')

    s.save(os.path.join(OUT, 'fig9-3.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-4: Manager 順序協調
# ════════════════════════════════════════════════════════════════════

def fig9_4():
    W, H = 780, 480
    s = SVG(W, H)

    s.text(W // 2, 28, 'Manager 順序協調：Sub-Agent 作為工具', size=FS_TITLE, bold=True)

    # Manager
    mx, my, mw, mh = 240, 60, 300, 100
    s.rect(mx, my, mw, mh, fill='medium')
    s.text(mx + mw // 2, my + 22, 'Manager Agent', size=FS_BODY, bold=True)
    s.text(mx + mw // 2, my + 46, '任務理解 → 分解 → 排程 → 綜合', size=FS_TINY, fill='text_light')
    s.text(mx + mw // 2, my + 66, '工具集: [call_agent_A, call_agent_B,', size=FS_TINY, fill='text_light')
    s.text(mx + mw // 2, my + 82, 'call_agent_C, search, write_file]', size=FS_TINY, fill='text_light')

    # Sub-agents in sequence
    agents = [
        ('Sub-Agent A', '資料收集', '搜尋技術文件\n提取關鍵資訊', 'light'),
        ('Sub-Agent B', '分析處理', '對比分析資料\n生成統計報告', 'light'),
        ('Sub-Agent C', '報告生成', '撰寫最終報告\n格式化輸出', 'light'),
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
    s.text(W // 2, dy + 18, '順序執行流', size=FS_BODY, bold=True)

    flow_items = [
        'Manager 呼叫 Agent A',
        '→ A 返回資料',
        '→ Manager 傳遞給 B',
        '→ B 返回分析',
        '→ Manager 傳遞給 C',
        '→ C 返回報告',
    ]
    fx_start = 55
    for i, item in enumerate(flow_items):
        s.text(fx_start + i * 118, dy + 42, item, size=FS_TINY, anchor='start',
               fill='text' if '呼叫' in item or '返回' in item else 'text_light')

    s.text(W // 2, dy + 65, 'Manager 視角：呼叫 Agent = 呼叫工具（發請求 → 獲響應）',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-4.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-5: 書籍翻譯 Agent 架構 (Exp 9.4)
# ════════════════════════════════════════════════════════════════════

def fig9_5():
    W, H = 780, 540
    s = SVG(W, H)

    s.text(W // 2, 28, '實驗 9.4：書籍翻譯 Agent — Manager 模式', size=FS_TITLE, bold=True)

    # Manager at top
    mx, my, mw, mh = 240, 55, 300, 70
    s.rect(mx, my, mw, mh, fill='medium')
    s.text(mx + mw // 2, my + 22, 'Manager Agent', size=FS_BODY, bold=True)
    s.text(mx + mw // 2, my + 48, '任務規劃 · 進度監控 · 異常處理 · 結果綜合', size=FS_TINY, fill='text_light')

    # Three sub-agents
    sub_agents = [
        (30, 'Glossary Agent', '術語對照表',
         ['接收全書 → 識別專業術語', '搜尋專業詞典 + 翻譯規範', '輸出: glossary.json'],
         ['{"attention": "注意力",', ' "transformer": "Transformer",', ' "backprop": "反向傳播"}']),
        (270, 'Translation Agent ×N', '章節翻譯',
         ['輸入: 章節 + 術語表 + 指南', '術語嚴格按表翻譯', '輸出: chapter{n}_zh.md'],
         ['"...注意力機制透過計算', ' Query·Key^T 的相似度..."']),
        (520, 'Proofreading Agent', '全文審校',
         ['掃描驗證術語一致性', '檢查流暢性和可讀性', '輸出: review_report.md'],
         ['P3: "注意力"→"關注"不一致', 'P8: 長句建議拆分']),
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
    s.arrow(30 + aw + 4, ay + 90, 270 - 4, ay + 90, label='術語表')
    s.arrow(270 + aw + 4, ay + 90, 520 - 4, ay + 90, label='譯文')

    # Shared file system
    fy = 375
    s.rect(30, fy, W - 60, 70, fill='medium', rx=6)
    s.text(W // 2, fy + 18, '共享檔案系統', size=FS_BODY, bold=True)
    files = [
        ('glossary.json', '術語對照表'),
        ('chapter{1..10}_zh.md', '章節譯文'),
        ('review_report.md', '審校報告'),
        ('translation_guide.md', '翻譯指南'),
    ]
    fw = (W - 80) // len(files)
    for i, (fname, desc) in enumerate(files):
        cx = 50 + i * fw + fw // 2
        s.mono(cx, fy + 40, fname, size=11, anchor='middle')
        s.text(cx, fy + 58, desc, size=FS_TINY, fill='text_light')

    # Key insight
    ky = 460
    s.rect(30, ky, W - 60, 60, fill='code_bg', rx=4)
    s.text(W // 2, ky + 18, '上下文隔離優勢', size=FS_BODY, bold=True)
    s.text(W // 2, ky + 42,
           'Glossary: 僅看術語 | Translation: 僅看當前章節+術語表 | Manager: 僅維護檔案索引',
           size=FS_TINY, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-5.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-6: Manager 並行協調
# ════════════════════════════════════════════════════════════════════

def fig9_6():
    W, H = 780, 500
    s = SVG(W, H)

    s.text(W // 2, 28, 'Manager 並行協調：訊息匯流排架構', size=FS_TITLE, bold=True)

    # Orchestration Agent
    ox, oy, ow, oh = 240, 55, 300, 70
    s.rect(ox, oy, ow, oh, fill='medium')
    s.text(ox + ow // 2, oy + 22, 'Orchestration Agent', size=FS_BODY, bold=True)
    s.text(ox + ow // 2, oy + 48, '並行排程 · 實時監控 · 結果彙總', size=FS_TINY, fill='text_light')

    # Message bus
    bus_y = 155
    s.rect(50, bus_y, W - 100, 36, fill='dark', rx=4)
    s.text(W // 2, bus_y + 18, '訊息匯流排（Message Bus）', size=FS_SMALL, fill='white', bold=True)

    s.arrow(ox + ow // 2, oy + oh + 2, ox + ow // 2, bus_y - 2)

    # Parallel agents
    agents = [
        ('Agent 1', '資料採集', '執行中 ◎', 'light'),
        ('Agent 2', '內容分析', '執行中 ◎', 'light'),
        ('Agent 3', '圖表生成', '已完成 ✓', 'medium'),
        ('Agent 4', '格式校驗', '等待中 ○', 'code_bg'),
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
        s.text(x + aw // 2, ay + 82, '獨立上下文', size=FS_TINY, fill='text_light')

        s.arrow(x + aw // 2, bus_y + 38, x + aw // 2, ay - 2, color='dark')

    # Message examples
    my = 350
    s.rect(30, my, W - 60, 125, fill='code_bg', rx=4)
    s.text(W // 2, my + 18, '訊息匯流排通訊示例', size=FS_BODY, bold=True)

    messages = [
        ('Orch → Agent 1', '{"type":"start","task":"採集 arxiv 論文","params":{"query":"LLM agent"}}'),
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
#  fig9-7: Phone + Computer 雙 Agent (Exp 9.5/9.6)
# ════════════════════════════════════════════════════════════════════

def fig9_7():
    W, H = 780, 560
    s = SVG(W, H)

    s.text(W // 2, 28, '實驗 9.5/9.6：Phone + Computer 雙 Agent', size=FS_TITLE, bold=True)

    # Phone Agent (left)
    px, py, pw, ph = 30, 65, 310, 240
    s.rect(px, py, pw, ph, fill='light', rx=6)
    s.text(px + pw // 2, py + 22, 'Phone Agent', size=FS_BODY, bold=True)
    s.text(px + pw // 2, py + 42, 'Node.js · 實時語音通話', size=FS_TINY, fill='text_light')

    phone_pipeline = [
        ('使用者語音', '麥克風輸入', 'medium'),
        ('VAD + ASR', 'Silero VAD → STT 轉錄', 'light'),
        ('LLM 推理', '理解意圖 + 提取資訊', 'light'),
        ('TTS 合成', '生成語音回覆 → 播放', 'medium'),
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
    s.text(cx + cw // 2, cy + 42, 'Python · 瀏覽器自動化', size=FS_TINY, fill='text_light')

    comp_pipeline = [
        ('螢幕截圖', '瀏覽器當前頁面', 'medium'),
        ('Vision LLM', '理解頁面結構 + 表單欄位', 'light'),
        ('動作規劃', '定位欄位 → 規劃輸入序列', 'light'),
        ('執行操作', '點選 / 輸入 / 提交', 'medium'),
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
    s.text(W // 2, ws_y + 18, 'WebSocket 雙向通訊 (ws://localhost:8849)', size=FS_SMALL, fill='white', bold=True)

    s.arrow(px + pw // 2, py + ph + 2, px + pw // 2, ws_y - 2, color='dark')
    s.arrow(cx + cw // 2, cy + ch_h + 2, cx + cw // 2, ws_y - 2, color='dark')

    # Message examples
    my = ws_y + 50
    s.rect(30, my, W - 60, 150, fill='code_bg', rx=4)
    s.text(W // 2, my + 18, '實時雙向訊息流（邊打電話邊用電腦）', size=FS_BODY, bold=True)

    msgs = [
        ('Phone → Computer', '[FROM_PHONE_AGENT] 使用者說姓名是張三', '→'),
        ('Computer → Phone', '[FROM_COMPUTER_AGENT] 已填寫姓名，需要證件號', '←'),
        ('Phone → Computer', '[FROM_PHONE_AGENT] 證件號 310101199001011234', '→'),
        ('Computer → Phone', '[FROM_COMPUTER_AGENT] 表單已提交，註冊成功', '←'),
    ]
    for i, (sender, content, direction) in enumerate(msgs):
        y = my + 42 + i * 26
        s.text(42, y, sender, size=FS_TINY, bold=True, anchor='start',
               fill='text' if '→' == direction else 'text_light')
        s.mono(210, y, content, size=10, anchor='start')

    # Key point
    s.text(W // 2, my + 140,
           '關鍵：兩個 Agent 獨立 ReAct 迴圈並行執行，互不阻塞',
           size=FS_SMALL, fill='text_light')

    s.save(os.path.join(OUT, 'fig9-7.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-8: 並行網頁蒐集 Agent (Exp 9.7)
# ════════════════════════════════════════════════════════════════════

def fig9_8():
    W, H = 780, 530
    s = SVG(W, H)

    s.text(W // 2, 28, '實驗 9.7：並行 Web Scraping — 級聯終止', size=FS_TITLE, bold=True)

    # Orchestration Agent
    ox, oy, ow, oh = 230, 55, 320, 65
    s.rect(ox, oy, ow, oh, fill='medium')
    s.text(ox + ow // 2, oy + 20, 'Orchestration Agent', size=FS_BODY, bold=True)
    s.text(ox + ow // 2, oy + 44, '動態建立 · 實時監控 · 級聯終止', size=FS_TINY, fill='text_light')

    # Parallel Computer Use Agents
    agents = [
        ('Agent 1', 'cs.edu.cn', '搜尋中... ◎', 'light'),
        ('Agent 2', 'math.edu.cn', '未找到 ✗', '#e8e8e8'),
        ('Agent 3', 'phys.edu.cn', '找到！ ✓', 'medium'),
        ('Agent 4', 'chem.edu.cn', '已終止 ⊘', 'code_bg'),
        ('Agent 5', 'bio.edu.cn', '已終止 ⊘', 'code_bg'),
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
        s.text(x + aw // 2, ay + 55, '教師名錄搜尋', size=FS_TINY, fill='text_light')
        s.text(x + aw // 2, ay + 75, status, size=FS_TINY,
               bold=('找到' in status), fill='text' if '找到' in status else 'text_light')

        s.arrow(ox + ow // 2, oy + oh + 2, x + aw // 2, ay - 2, color='dark')

    # Cascade termination flow
    ty = 280
    s.rect(30, ty, W - 60, 120, fill='code_bg', rx=4)
    s.text(W // 2, ty + 18, '級聯終止時序', size=FS_BODY, bold=True)

    timeline = [
        ('t=0s', '啟動 5 個 Agent\n並行搜尋教師"張偉"'),
        ('t=12s', 'Agent 2 完成\n未找到 → 正常退出'),
        ('t=18s', 'Agent 3 找到目標!\n傳送 target_found'),
        ('t=18.1s', 'Orch 廣播 terminate\n給 Agent 1,4,5'),
        ('t=19s', '全部確認終止\n彙總結果返回'),
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
    s.text(200, ry + 18, '找到結果', size=FS_BODY, bold=True)
    result_lines = [
        '姓名: 張偉  學院: 物理學院',
        '職位: 教授  方向: 量子計算',
        '郵箱: zhangwei@phys.edu.cn',
    ]
    for i, ln in enumerate(result_lines):
        s.mono(50, ry + 40 + i * 16, ln, size=11)

    s.rect(400, ry, 350, 85, fill='medium', rx=4)
    s.text(575, ry + 18, '效能對比', size=FS_BODY, bold=True)
    s.text(420, ry + 42, '序列: 10 個網站 × 30s = ~5 分鐘', size=FS_TINY, anchor='start', fill='text_light')
    s.text(420, ry + 60, '並行: 18 秒找到 + 1 秒終止 = 19 秒', size=FS_TINY, anchor='start', bold=True)
    s.text(420, ry + 78, '加速比: ~15×（含級聯終止最佳化）', size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-8.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-9: Handoff 鏈式模式
# ════════════════════════════════════════════════════════════════════

def fig9_9():
    W, H = 780, 440
    s = SVG(W, H)

    s.text(W // 2, 28, 'Handoff 鏈式模式：對等移交 + 契約式協作', size=FS_TITLE, bold=True)

    nodes = [
        ('Agent A', '需求分析', '輸出: 結構化需求文件\nspec.json', 'medium'),
        ('Agent B', '架構設計', '輸出: 技術設計文件\ndesign.md', 'light'),
        ('Agent C', '程式碼實現', '輸出: 原始碼\nsrc/*.py', 'light'),
        ('Agent D', '測試驗證', '輸出: 測試報告\ntest_report.md', 'medium'),
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

        s.text(x + nw // 2, ny + nh - 8, '完成後移交 →', size=FS_TINY, fill='text_light')

        if i < len(nodes) - 1:
            s.arrow(x + nw + 4, ny + nh // 2, x + nw + gap - 4, ny + nh // 2)

    # Handoff data detail
    hy = 215
    s.rect(30, hy, W - 60, 90, fill='code_bg', rx=4)
    s.text(W // 2, hy + 18, 'Handoff 傳遞內容（Agent A → Agent B 示例）', size=FS_BODY, bold=True)

    handoff_fields = [
        ('觸發條件', 'A 完成需求文件 → is_complete=True'),
        ('目標 Agent', 'target="architect" (Agent B)'),
        ('傳遞內容', 'files=["spec.json"] + summary="電商系統: 3個微服務, REST API"'),
        ('移交後狀態', 'status="退出" (釋放資源, 不保持待命)'),
    ]
    for i, (field, value) in enumerate(handoff_fields):
        y = hy + 38 + i * 16
        s.text(42, y, field + ':', size=FS_TINY, bold=True, anchor='start')
        s.text(150, y, value, size=FS_TINY, anchor='start', fill='text_light')

    # Comparison with Manager mode
    cy = 320
    s.rect(30, cy, 340, 100, fill='light', rx=4)
    s.text(200, cy + 18, '去中心化優勢', size=FS_SMALL, bold=True)
    advantages = [
        '✓ 無需中心 Manager 理解所有角色',
        '✓ 清晰職責邊界，介面解耦',
        '✓ Engineer 可多例項並行',
    ]
    for i, adv in enumerate(advantages):
        s.text(48, cy + 42 + i * 20, adv, size=FS_TINY, anchor='start', fill='text_light')

    s.rect(400, cy, 350, 100, fill='light', rx=4)
    s.text(575, cy + 18, '去中心化侷限', size=FS_SMALL, bold=True)
    limits = [
        '✗ 缺乏全域性最佳化視野',
        '✗ 異常處理困難（無中心協調）',
        '✗ 流程固定，難以動態調整',
    ]
    for i, lim in enumerate(limits):
        s.text(418, cy + 42 + i * 20, lim, size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-9.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-10: MetaGPT SOP 流水線
# ════════════════════════════════════════════════════════════════════

def fig9_10():
    W, H = 780, 530
    s = SVG(W, H)

    s.text(W // 2, 28, 'MetaGPT SOP 流水線：標準化文件驅動', size=FS_TITLE, bold=True)

    roles = [
        ('Product Manager', 'medium',
         '輸入: 使用者需求描述',
         ['功能列表 + 優先順序', '使用者故事 (5 條)', '驗收標準'],
         'docs/PRD.md'),
        ('Architect', 'light',
         '輸入: PRD.md',
         ['技術棧: FastAPI+React', 'API 規範 (OpenAPI)', '資料庫 Schema'],
         'docs/design.md'),
        ('Engineer ×3', 'light',
         '輸入: design.md + 模組規約',
         ['模組 A: 使用者服務', '模組 B: 訂單服務', '模組 C: 支付服務'],
         'src/*.py'),
        ('QA Engineer', 'medium',
         '輸入: src/ + PRD.md',
         ['單元測試 (pytest)', '整合測試 (API)', 'Bug 報告 → Engineer'],
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
        s.text(x + 14, ry + 72, '產出:', size=FS_TINY, bold=True, anchor='start')
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
    s.arrow_curved(qa_x, ry + 230 + 5, eng_x, ry + 230 + 5, curve=-30, label='Bug 修復', dash=True)

    # Shared file system
    fy = 310
    s.rect(30, fy, W - 60, 50, fill='medium', rx=4)
    s.text(W // 2, fy + 16, '共享專案目錄', size=FS_SMALL, bold=True)
    s.mono(W // 2, fy + 36, 'docs/PRD.md  docs/design.md  src/*.py  docs/test_report.md',
           size=11, anchor='middle')

    # Key insight
    ky = 375
    s.rect(30, ky, W - 60, 130, fill='code_bg', rx=4)
    s.text(W // 2, ky + 18, 'MetaGPT 核心設計', size=FS_BODY, bold=True)

    insights = [
        ('標準化文件', '每個角色輸出明確格式 — 下游只需理解格式，不需理解上游思考過程'),
        ('介面解耦', '改進 PM（換更強模型）只要輸出符合 PRD 格式，下游零修改'),
        ('無 Manager', '控制權沿 DAG 自然流動：PM→Arch→Eng→QA，無中心排程開銷'),
        ('異常通道', 'QA 測試失敗 → Bug 報告按模組路由回 Engineer → 迭代修復'),
    ]
    for i, (title, desc) in enumerate(insights):
        y = ky + 42 + i * 24
        s.text(42, y, '▸ ' + title, size=FS_SMALL, bold=True, anchor='start')
        s.text(180, y, desc, size=FS_TINY, anchor='start', fill='text_light')

    s.save(os.path.join(OUT, 'fig9-10.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-11: VLA 架構（Vision-Language-Action）—— 三種技術路徑對比
# ════════════════════════════════════════════════════════════════════

def fig9_11():
    W, H = 900, 620
    s = SVG(W, H)

    # 共同輸入
    in_x, in_y, in_w, in_h = 230, 55, 440, 64
    s.rect(in_x, in_y, in_w, in_h, fill='medium', rx=6)
    s.text(in_x + in_w / 2, in_y + 22, '共同輸入：攝像頭畫面 + 語言指令', size=FS_SMALL, bold=True)
    s.text(in_x + in_w / 2, in_y + 44, '"把紅色積木放到藍色盒子裡"', size=FS_TINY, fill='text_light')

    # 向三個分支引出箭頭
    s.arrow(in_x + 70, in_y + in_h + 2, 145, 165)   # → OpenVLA
    s.arrow(W / 2, in_y + in_h + 2, W / 2, 165)     # → π₀
    s.arrow(in_x + in_w - 70, in_y + in_h + 2, 755, 165)  # → RT-2

    # 三欄架構
    col_w, col_gap = 270, 30
    cols_total = 3 * col_w + 2 * col_gap
    sx0 = (W - cols_total) / 2  # = 30

    columns = [
        ('OpenVLA', '開源 · 離散動作 token', 'light', [
            ('視覺編碼器', 'DINOv2 + SigLIP', '提取畫素特徵'),
            ('LLM 主幹', 'Llama 2 (7B)', '理解指令與場景'),
            ('解碼方式', '自迴歸 · 文字 token', '動作切分成離散選項'),
            ('動作輸出', '"a=[3,−2,5,...]" tokens', '逐步生成 7-DOF 控制量'),
        ]),
        ('π₀（Pi-Zero）', '擴散策略 · 平滑軌跡', 'medium', [
            ('視覺編碼器', 'ViT 多視角融合', '提取畫素特徵'),
            ('Mixture-of-Transformers', '快慢分離主幹', '語言慢思考 + 控制快思考'),
            ('解碼方式', '擴散去噪迭代', '先粗後精打磨整段軌跡'),
            ('動作輸出', '連續動作序列（50 步/批）', '高頻流暢控制訊號'),
        ]),
        ('RT-2', '語言模型即動作模型', 'light', [
            ('視覺-語言主幹', 'PaLI-X / PaLM-E', 'VLM 端到端理解'),
            ('動作表示', '動作 → 自然語言 token', '"move arm 5cm right"'),
            ('解碼方式', '複用 VLM 自迴歸', '與文字生成共享權重'),
            ('動作輸出', '文字描述 → 控制器解析', '繼承 VLM 的語義泛化'),
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
        # 標題條
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

    # 底部：統一輸出層
    out_y = top_y + title_h + 4 * row_h + 14 + 24
    s.rect(30, out_y, W - 60, 50, fill='darker', rx=6)
    s.text(W / 2, out_y + 18,
           '機器人控制訊號：7-DOF 關節角度 / 末端位姿',
           size=FS_SMALL, bold=True, fill='white')
    s.text(W / 2, out_y + 36,
           '差異在"如何告訴機器人下一步該怎麼動"，最終都落到統一的控制介面',
           size=FS_TINY, fill='white')

    s.save(os.path.join(OUT, 'fig9-11.svg'))


# ════════════════════════════════════════════════════════════════════
#  fig9-12: 語音狼人殺 Agent 系統 (Exp 9.9)
# ════════════════════════════════════════════════════════════════════

def fig9_12():
    W, H = 780, 550
    s = SVG(W, H)

    s.text(W // 2, 28, '實驗 9.9：語音狼人殺 — 資訊許可權控制', size=FS_TITLE, bold=True)

    # Judge (code-driven)
    jx, jy, jw, jh = 260, 55, 260, 75
    s.rect(jx, jy, jw, jh, fill='dark', rx=6)
    s.text(jx + jw // 2, jy + 20, '法官（程式碼驅動）', size=FS_BODY, bold=True, fill='white')
    s.text(jx + jw // 2, jy + 42, '遊戲狀態 · 階段控制 · 資訊分發', size=FS_TINY, fill='white')
    s.text(jx + jw // 2, jy + 58, 'Night → Day → Vote → Settle', size=FS_TINY, fill='white')

    # Role agents
    roles = [
        (40, '狼人 1', '🐺', 'medium',
         ['可見: 同伴身份', '策略: 偽裝村民', '夜晚: 選擇目標']),
        (185, '狼人 2', '🐺', 'medium',
         ['可見: 同伴身份', '策略: 跟票保護', '夜晚: 協商目標']),
        (330, '預言家', '🔮', 'light',
         ['可見: 驗人結果', '策略: 擇機跳出', '夜晚: 查驗 1 人']),
        (475, '女巫', '🧪', 'light',
         ['可見: 死亡/救治', '策略: 保藥/解藥', '夜晚: 救/毒 1 人']),
        (620, '村民 ×2', '👤', '#e8e8e8',
         ['可見: 僅公開資訊', '策略: 邏輯推理', '白天: 分析發言']),
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
        elif '預言' in name:
            s.badge(x + aw - 55, ay + aw - 15, 50, 18, '驗人結果', fill='darker', font_size=10)

    # Info permission control
    iy = 340
    s.rect(30, iy, W - 60, 90, fill='code_bg', rx=4)
    s.text(W // 2, iy + 18, '資訊許可權控制：法官按角色過濾上下文', size=FS_BODY, bold=True)

    perms = [
        ('狼人', '所有狼人身份 + 夜晚商議 + 公開發言'),
        ('預言家', '驗人結果(僅自己驗的) + 公開發言'),
        ('女巫', '當晚死亡者 + 解藥/毒藥狀態 + 公開發言'),
        ('村民', '僅公開發言 + 投票記錄（零私有資訊）'),
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
    s.text(W // 2, vy + 18, '實時語音互動（ASR + LLM + TTS）', size=FS_BODY, bold=True)

    voice_flow = [
        ('白天討論', '法官管理發言順序\n按座位依次發言'),
        ('投票階段', '收集所有玩家投票\n統計票數公佈結果'),
        ('夜晚階段', '法官依次喚醒角色\n私密語音通道'),
        ('真人玩家', '隨機分配角色\n語音表達投票/發言'),
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
