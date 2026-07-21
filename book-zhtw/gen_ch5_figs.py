#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 5 (程式碼生成).

Figures (11 total):
  fig5-1:  OpenClaw architecture — Coding Agent as core of general Agent
  fig5-2:  Coding Agent multi-phase workflow (concrete file ops & tool calls)
  fig5-3:  Search tool comparison (4 types with real query examples)
  fig5-4:  File editing approach comparison (5 methods with code diffs)
  fig5-5:  PPT generation pipeline (Proposer-Reviewer with Slidev code)
  fig5-6:  Exp 5.6+5.7 — Paper-to-PPT/Video pipeline
  fig5-7:  Exp 5.10 — Production log diagnosis pipeline
  fig5-8:  Dynamic form generation (LLM → HTML form → JSON → continue)
  fig5-9:  SQL query agent (artifact mode, data bypasses LLM)
  fig5-10: Agent bootstrap cycle (self-replication concept)
  fig5-11: Exp 5.14 — Agent that creates agents (meta-agent)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import (
    SVG, COLORS, FONT, MONO, STROKE_W, CORNER_R, _escape,
    FS_TITLE, FS_BODY, FS_SMALL, FS_TINY, FS_LABEL,
)

OUT = os.path.join(os.path.dirname(__file__), 'images')


def _pill(svg, x, y, w, h, label, fill='light', font_size=FS_SMALL, bold=False):
    svg.rect(x, y, w, h, fill=fill, rx=h // 2)
    c = 'white' if fill in ('dark', 'darker') else 'text'
    svg.text(x + w / 2, y + h / 2, label, size=font_size, fill=c, bold=bold)


# ──────────────────────── fig5-1 (NEW: OpenClaw arch) ──────

def fig5_1():
    """OpenClaw 架構：以 Coding Agent 為核心的通用 Agent"""
    w, h = 980, 600
    svg = SVG(w, h)
    svg.text(w / 2, 30, "OpenClaw 架構：以 Coding Agent 為核心的通用 Agent", size=FS_TITLE, bold=True)

    # Top: multi-platform messaging gateway
    gw_y, gw_h = 58, 66
    svg.group_box(60, gw_y, w - 120, gw_h, "多平臺訊息閘道器（使用者互動層）")
    channels = ["WhatsApp", "Telegram", "iMessage", "Slack", "CLI"]
    pill_w, pill_h = 130, 32
    total_pw = len(channels) * pill_w + (len(channels) - 1) * 18
    px_start = (w - total_pw) / 2
    for i, ch in enumerate(channels):
        px = px_start + i * (pill_w + 18)
        svg.rect(px, gw_y + 26, pill_w, pill_h, fill='medium', rx=pill_h // 2)
        svg.text(px + pill_w / 2, gw_y + 26 + pill_h / 2, ch, size=FS_SMALL)

    svg.arrow(w / 2, gw_y + gw_h + 2, w / 2, 158)
    svg.text(w / 2 + 12, 134, "自然語言請求", size=FS_LABEL, fill='text_light', anchor='start')

    # Center: Coding Agent runtime — widened to fit 4 tools comfortably
    ca_x, ca_y, ca_w, ca_h = 200, 160, 580, 210
    svg.rect(ca_x, ca_y, ca_w, ca_h, fill='light')
    svg.rect(ca_x, ca_y, ca_w, 40, fill='darker', rx=6)
    svg.text(ca_x + ca_w / 2, ca_y + 20,
             "Coding Agent 執行時（推理 + 執行核心）", size=FS_BODY, bold=True, fill='white')

    tools = [
        ("Code Interpreter", "程式碼執行"), ("Bash Shell", "系統命令"),
        ("Read File", "讀取檔案"), ("Write File", "寫入檔案"),
        ("Edit File", "編輯檔案"), ("Glob", "檔案搜尋"), ("Grep", "內容搜尋"),
    ]
    tw, th, tgap = 132, 60, 12
    for ri, row in enumerate([tools[:4], tools[4:]]):
        row_total_w = len(row) * tw + (len(row) - 1) * tgap
        rx_start = ca_x + (ca_w - row_total_w) / 2
        ry = ca_y + 56 + ri * (th + tgap)
        for ci, (name, desc) in enumerate(row):
            tx = rx_start + ci * (tw + tgap)
            svg.rect(tx, ry, tw, th, fill='white')
            svg.text(tx + tw / 2, ry + 22, name, size=FS_TINY, bold=True)
            svg.text(tx + tw / 2, ry + 42, desc, size=FS_TINY, fill='text_light')

    # Left: Deep Research
    dr_x, dr_y, dr_w, dr_h = 22, 198, 158, 86
    svg.rect(dr_x, dr_y, dr_w, dr_h, fill='medium')
    svg.text(dr_x + dr_w / 2, dr_y + 22, "網路搜尋模組", size=FS_SMALL, bold=True)
    svg.text(dr_x + dr_w / 2, dr_y + 44, "Deep Research", size=FS_TINY, fill='text_light')
    svg.text(dr_x + dr_w / 2, dr_y + 66, "Web 請求 · 解析", size=FS_TINY, fill='text_light')
    svg.arrow(dr_x + dr_w + 2, dr_y + dr_h / 2, ca_x - 2, ca_y + ca_h / 2)

    # Right: Computer Use
    cu_x, cu_y, cu_w, cu_h = 800, 198, 158, 86
    svg.rect(cu_x, cu_y, cu_w, cu_h, fill='medium')
    svg.text(cu_x + cu_w / 2, cu_y + 22, "瀏覽器自動化", size=FS_SMALL, bold=True)
    svg.text(cu_x + cu_w / 2, cu_y + 44, "Computer Use", size=FS_TINY, fill='text_light')
    svg.text(cu_x + cu_w / 2, cu_y + 66, "Playwright DOM", size=FS_TINY, fill='text_light')
    svg.arrow(ca_x + ca_w + 2, ca_y + ca_h / 2, cu_x - 2, cu_y + cu_h / 2)

    # Bottom: file system layer
    fs_y, fs_h = 410, 140
    svg.arrow(w / 2, ca_y + ca_h + 2, w / 2, fs_y - 2)
    svg.text(w / 2 + 12, 390, "讀 / 寫檔案", size=FS_LABEL, fill='text_light', anchor='start')
    svg.group_box(60, fs_y, w - 120, fs_h, "檔案系統（記憶 · 知識 · 能力中樞）")

    mem_items = [
        ("MEMORY.md", "高層級事實 / 使用者偏好"),
        ("daily/YYYY-MM-DD.md", "按日歸檔 / 互動日誌"),
        ("SOUL.md", "Agent 身份與行為規則"),
        ("知識庫檔案", "任務經驗 / 自我進化"),
        ("Git 版本控制", "記憶回滾 / 歷史審計"),
    ]
    item_w, item_h, item_gap = 162, 76, 16
    total_iw = len(mem_items) * item_w + (len(mem_items) - 1) * item_gap
    ix_start = (w - total_iw) / 2
    for i, (title, desc) in enumerate(mem_items):
        ix = ix_start + i * (item_w + item_gap)
        iy = fs_y + 34
        svg.rect(ix, iy, item_w, item_h, fill='white')
        svg.text(ix + item_w / 2, iy + 26, title, size=FS_TINY, bold=True)
        svg.text(ix + item_w / 2, iy + 52, desc, size=FS_TINY, fill='text_light')

    # Very bottom: LLM as OS
    os_y = fs_y + fs_h + 16
    svg.rect(60, os_y, w - 120, 38, fill='darker', rx=6)
    svg.text(w / 2, os_y + 19,
             "大模型 = 新作業系統：遮蔽智慧複雜性，提供統一抽象", size=FS_SMALL, bold=True, fill='white')

    svg.save(os.path.join(OUT, 'fig5-1.svg'))


# ──────────────────────── fig5-2 (was fig5-1) ────────────────────────

def fig5_2():
    """Coding Agent 多階段工作流程（具體工具呼叫）"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "Coding Agent 分層工作流程", size=FS_TITLE, bold=True)

    phases = [
        ("① 專案文件化", 'medium', [
            ("read_file", "README.md, ARCHITECTURE.md"),
            ("glob", "**/*.py, **/*.ts"),
            ("write_file", "→ 生成 CLAUDE.md 專案指南"),
        ]),
        ("② 需求理解", 'light', [
            ("ask_user", "\"最佳化目標是延遲還是吞吐？\""),
            ("grep", "\"latency|throughput\" src/"),
            ("read_file", "src/config.py (當前引數)"),
        ]),
        ("③ 設計文件", 'light', [
            ("write_file", "design.md (方案對比)"),
            ("ask_user", "提交設計 → 等待審批"),
            ("—", "人類審查後 → 繼續"),
        ]),
        ("④ 編碼與測試", 'medium', [
            ("edit_file", "old_str→new_str 修改程式碼"),
            ("bash", "pytest tests/ -v"),
            ("edit_file", "修復失敗測試 → 重跑"),
        ]),
        ("⑤ 審查與交付", 'light', [
            ("bash", "ruff check src/ (lint)"),
            ("read_file", "自審: 可讀性/安全/效能"),
            ("edit_file", "更新 ARCHITECTURE.md"),
        ]),
    ]

    phase_w = 155
    phase_gap = 12
    total_w = len(phases) * phase_w + (len(phases) - 1) * phase_gap
    sx = (w - total_w) / 2

    for i, (title, fill, steps) in enumerate(phases):
        x = sx + i * (phase_w + phase_gap)
        ph = 240
        svg.rect(x, 55, phase_w, ph, fill=fill)
        svg.text(x + phase_w / 2, 78, title, size=FS_SMALL, bold=True)
        svg.line(x + 8, 92, x + phase_w - 8, 92, color='dark')

        for j, (tool, desc) in enumerate(steps):
            ty = 110 + j * 70
            _pill(svg, x + 8, ty, phase_w - 16, 22, tool, fill='dark', font_size=11, bold=True)
            lines = desc.split('\n') if '\n' in desc else [desc]
            for k, line in enumerate(lines):
                svg.mono(x + 10, ty + 34 + k * 16, line, size=10)

        if i < len(phases) - 1:
            ax = x + phase_w + 2
            svg.arrow(ax, 55 + ph / 2, ax + phase_gap - 4, 55 + ph / 2)

    # Bottom: feedback loops
    svg.line(30, 320, w - 30, 320, color='dark', dash=True)
    svg.text(w / 2, 340, "閉環反饋機制", size=FS_BODY, bold=True)

    loops = [
        ("測試失敗 → 修改程式碼 → 重新測試", "④內迴圈: 平均 2-3 輪收斂"),
        ("Lint 錯誤 → 即時修復 → 再檢查", "⑤內迴圈: 編輯後自動觸發"),
        ("審查發現問題 → 回到④修改", "⑤→④回退: 保證交付質量"),
    ]
    ly = 365
    for label, note in loops:
        svg.rect(80, ly, 500, 46, fill='light')
        svg.text(330, ly + 15, label, size=FS_SMALL, bold=True)
        svg.text(330, ly + 34, note, size=FS_TINY, fill='text_light')
        ly += 50

    # Annotations on the right
    annots = [
        "Agent 狀態列: cwd, git branch",
        "Agent 狀態列: 未暫存變更",
        "工具輸出: 頭尾截斷",
        "持久化終端會話",
    ]
    for i, ann in enumerate(annots):
        svg.rect(610, 365 + i * 50, 250, 38, fill='code_bg', stroke='dark', rx=4)
        svg.text(735, 384 + i * 50, ann, size=FS_TINY, fill='text_light')

    svg.text(w / 2, 565, "計劃先於行動 · 驗證貫穿始終 · 文件與程式碼共同演化", size=FS_BODY, bold=True, fill='darker')

    svg.save(os.path.join(OUT, 'fig5-2.svg'))


# ──────────────────────── fig5-3 ────────────────────────

def fig5_3():
    """搜尋工具對比（四種工具 + 實際查詢示例）"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "四種搜尋工具對比", size=FS_TITLE, bold=True)

    tools = [
        ("正則內容匹配 (grep)", 'medium',
         "rg \"def handle_.*\" --type py",
         ["src/api.py:42:  def handle_request(..)",
          "src/api.py:89:  def handle_timeout(..)",
          "src/ws.py:15:   def handle_connect(..)"],
         "精確文字 → 所有出現位置"),
        ("檔名匹配 (glob)", 'light',
         "glob: **/test_*.py",
         ["tests/test_api.py",
          "tests/test_auth.py",
          "tests/unit/test_parser.py"],
         "路徑模式 → 不讀取檔案內容"),
        ("語義程式碼搜尋", 'light',
         "\"處理使用者輸入驗證\"",
         ["[0.91] src/validators.py:validate_input()",
          "[0.87] src/forms.py:sanitize_fields()",
          "[0.82] src/api.py:check_params()"],
         "自然語言 → 向量+BM25混合"),
        ("符號定義/引用", 'medium',
         "find_references: UserService",
         ["定義: src/services/user.py:12",
          "引用: src/api/routes.py:34 (import)",
          "引用: src/api/routes.py:56 (呼叫)",
          "引用: tests/test_user.py:8 (測試)"],
         "AST級 → 消除同名歧義"),
    ]

    col_w = (w - 60) // 2
    col_gap = 20

    for i, (title, fill, query, results, note) in enumerate(tools):
        col = i % 2
        row = i // 2
        x = 20 + col * (col_w + col_gap)
        y = 55 + row * 260

        svg.rect(x, y, col_w, 240, fill='white', stroke='border')
        svg.rect(x, y, col_w, 36, fill=fill, rx=CORNER_R)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + col_w / 2, y + 18, title, size=FS_SMALL, bold=True, fill=tc)

        svg.text(x + 12, y + 54, "查詢:", size=FS_TINY, bold=True, anchor='start', fill='text_light')
        svg.rect(x + 8, y + 64, col_w - 16, 24, fill='code_bg', stroke='dark', rx=3)
        svg.mono(x + 14, y + 76, query, size=11)

        svg.text(x + 12, y + 102, "結果:", size=FS_TINY, bold=True, anchor='start', fill='text_light')
        rh = len(results) * 20 + 12
        svg.rect(x + 8, y + 112, col_w - 16, rh, fill='code_bg', stroke='dark', rx=3)
        for j, r in enumerate(results):
            svg.mono(x + 14, y + 128 + j * 20, r, size=10)

        svg.text(x + col_w / 2, y + 226, note, size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig5-3.svg'))


# ──────────────────────── fig5-3 ────────────────────────

def fig5_4():
    """檔案編輯方案對比（五種方式 + 程式碼示例）"""
    w, h = 900, 700
    svg = SVG(w, h)
    svg.text(w / 2, 28, "五種檔案編輯方案對比", size=FS_TITLE, bold=True)

    approaches = [
        ("Diff + Apply Model", "dark",
         ["LLM 輸出 diff 描述:",
          "- def foo(x):",
          "    return x",
          "+ def foo(x, y=0):",
          "+   return x + y",
          "→ 小模型定位並應用"],
         "優勢: 關注點分離",
         "劣勢: 微小偏差致錯位"),
        ("Old String → New String", "medium",
         ['old: "def foo(x):\\n',
          '       return x"',
          'new: "def foo(x, y=0):\\n',
          '       return x + y"',
          "→ 字串精確匹配替換"],
         "優勢: 可預測、無歧義",
         "劣勢: 大段刪除需全輸出"),
        ("行號定位", "light",
         ["刪除行 42-43，插入:",
          "  def foo(x, y=0):",
          "    return x + y",
          "",
          "→ 行號精確指定範圍"],
         "優勢: 大段操作高效",
         "劣勢: 長檔案行號易錯"),
        ("類 Vim 命令", "light",
         ["42G  (跳轉42行)",
          "cw   (替換單詞)",
          "dd   (刪除行)",
          "yy/p (複製/貼上)",
          "→ 豐富的編輯語義"],
         "優勢: 移動/重組高效",
         "劣勢: 弱模型出錯多"),
        ("首尾匹配", "medium",
         ['start: "def foo(x):"',
          'end:   "    return x"',
          'new: "def foo(x, y=0):',
          '       return x + y"',
          "→ 只需邊界即可定位"],
         "優勢: 大段刪除免全輸出",
         "劣勢: 需邊界組合唯一"),
    ]

    col_w = 168
    col_gap = 10
    total_cw = len(approaches) * col_w + (len(approaches) - 1) * col_gap
    sx = (w - total_cw) / 2

    for i, (title, fill, code_lines, pro, con) in enumerate(approaches):
        x = sx + i * (col_w + col_gap)

        svg.rect(x, 55, col_w, 38, fill=fill, rx=CORNER_R)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + col_w / 2, 74, title, size=FS_TINY, bold=True, fill=tc)

        code_h = len(code_lines) * 17 + 14
        svg.rect(x, 101, col_w, code_h, fill='code_bg', stroke='dark', rx=3)
        for j, line in enumerate(code_lines):
            svg.mono(x + 6, 117 + j * 17, line, size=11)

        py = 101 + code_h + 12
        svg.rect(x + 4, py, col_w - 8, 56, fill='white', stroke='dark', rx=3)
        svg.text(x + col_w / 2, py + 19, pro, size=FS_TINY, fill='text')
        svg.text(x + col_w / 2, py + 41, con, size=FS_TINY, fill='text_light')

    # Adoption bar chart at bottom
    chart_y = 320
    svg.line(30, chart_y, w - 30, chart_y, color='dark', dash=True)
    svg.text(w / 2, chart_y + 24, "實際採用情況", size=FS_BODY, bold=True)

    adoptions = [
        ("Old→New", "Claude Code", 0.85, 'dark'),
        ("行號定位", "IDE 深度整合場景", 0.50, 'medium'),
        ("Diff + Apply", "Cursor", 0.40, 'light'),
        ("首尾匹配", "部分定製方案", 0.30, 'light'),
        ("Vim 命令", "實驗性方案", 0.15, 'code_bg'),
    ]
    bar_x, bar_w_max = 250, 480
    by = chart_y + 48
    for label, products, ratio, fill in adoptions:
        svg.text(bar_x - 10, by + 14, label, size=FS_TINY, anchor='end', bold=True)
        bw = bar_w_max * ratio
        svg.rect(bar_x, by, bw, 28, fill=fill, rx=3)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(bar_x + bw / 2, by + 14, products, size=FS_TINY, fill=tc)
        by += 38

    svg.save(os.path.join(OUT, 'fig5-4.svg'))


# ──────────────────────── fig5-4 ────────────────────────

def fig5_5():
    """PPT 生成流水線（Proposer-Reviewer 協作 + Slidev 程式碼）"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "PPT 生成：Proposer-Reviewer 協作機制", size=FS_TITLE, bold=True)

    # Proposer Agent (left)
    svg.rect(20, 60, 350, 280, fill='white', stroke='border', dash=True)
    svg.text(195, 82, "Proposer Agent", size=FS_BODY, bold=True)

    svg.text(40, 110, "輸入: 論文/資料內容", size=FS_SMALL, anchor='start', bold=True)
    svg.rect(30, 125, 330, 24, fill='code_bg', stroke='dark', rx=3)
    svg.mono(38, 137, "paper.pdf → 提取章節/論點/圖表", size=11)

    svg.text(40, 168, "輸出: Slidev Markdown", size=FS_SMALL, anchor='start', bold=True)
    code_lines = [
        "---",
        "layout: two-cols",
        "---",
        "# Transformer 架構",
        "::left::",
        "- 自注意力機制",
        "- 多頭注意力",
        "::right::",
        "<img src=\"fig3.png\" />",
    ]
    ch = svg.code_block(30, 182, 330, code_lines, font_size=10, line_h=14)

    # Reviewer Agent (right)
    svg.rect(510, 60, 350, 280, fill='white', stroke='border', dash=True)
    svg.text(685, 82, "Reviewer Agent", size=FS_BODY, bold=True)

    svg.text(520, 110, "步驟1: 渲染截圖", size=FS_SMALL, anchor='start', bold=True)
    svg.rect(520, 125, 330, 50, fill='light')
    svg.text(685, 142, "slidev export --per-slide", size=FS_TINY, fill='text_light')
    svg.text(685, 160, "→ slide-01.png, slide-02.png ...", size=FS_TINY, fill='text_light')

    svg.text(520, 192, "步驟2: Vision LLM 審查", size=FS_SMALL, anchor='start', bold=True)
    critique_lines = [
        "審查維度:",
        "  ✓ 文字是否溢位邊界",
        "  ✓ 佈局是否擁擠",
        "  ✓ 圖片尺寸是否合適",
        "  ✗ Slide 3: 文字溢位右欄",
        "  ✗ Slide 7: 內容過於密集",
    ]
    svg.rect(520, 208, 330, len(critique_lines) * 16 + 12, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(critique_lines):
        svg.mono(528, 222 + j * 16, line, size=10)

    # Arrows: Proposer → Reviewer → Proposer (loop)
    svg.arrow(370, 200, 508, 150, label="Slidev 程式碼")
    svg.arrow(508, 300, 370, 260, label="修改建議", dash=True)

    # Iteration badge
    _pill(svg, 395, 220, 100, 24, "迭代 2-3 輪", fill='dark', font_size=11, bold=True)

    # Bottom: why separate agents
    svg.line(30, 365, w - 30, 365, color='dark', dash=True)
    svg.text(w / 2, 388, "為什麼分離 Proposer 和 Reviewer？", size=FS_BODY, bold=True)

    reasons = [
        ("單 Agent 問題", [
            "數十頁渲染截圖 → 上下文膨脹",
            "程式碼 + 截圖混合 → 注意力分散",
        ]),
        ("分離的優勢", [
            "Reviewer 獨立上下文 → 只看截圖+程式碼",
            "Proposer 專注程式碼 → 只收修改建議",
        ]),
        ("實際效果", [
            "顯著減少上下文佔用",
            "修復準確率提升顯著",
        ]),
    ]
    rx = 30
    for title, items in reasons:
        svg.rect(rx, 405, 270, 130, fill='light')
        svg.text(rx + 135, 425, title, size=FS_SMALL, bold=True)
        for j, item in enumerate(items):
            svg.text(rx + 135, 450 + j * 24, item, size=FS_TINY, fill='text_light')
        rx += 290

    svg.save(os.path.join(OUT, 'fig5-5.svg'))


# ──────────────────────── fig5-5 ────────────────────────

def fig5_6():
    """實驗 5.6+5.7：論文→PPT→影片 端到端流水線"""
    w, h = 880, 520
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 5.6+5.7：論文 → PPT → 講解影片", size=FS_TITLE, bold=True)

    # Top pipeline: paper → PPT
    stages_top = [
        ("PDF 輸入", 'medium', [
            "paper.pdf",
            "解析章節結構",
            "提取圖表引用",
        ]),
        ("內容規劃", 'light', [
            "10-20 頁結構",
            "核心論點提取",
            "圖表分配到頁",
        ]),
        ("Slidev 生成", 'light', [
            "逐頁生成程式碼",
            "layout: two-cols",
            "程式碼+圖片混排",
        ]),
        ("渲染檢查", 'medium', [
            "export --per-slide",
            "Vision LLM 審查",
            "溢位/擁擠檢測",
        ]),
        ("迭代修復", 'light', [
            "Reviewer→Proposer",
            "修改 Slidev 程式碼",
            "重新渲染驗證",
        ]),
    ]

    sw = 155
    sgap = 10
    total = len(stages_top) * sw + (len(stages_top) - 1) * sgap
    sx = (w - total) / 2

    svg.text(w / 2, 60, "階段一：PPT 生成 (Proposer-Reviewer)", size=FS_SMALL, bold=True, fill='text_light')
    for i, (title, fill, details) in enumerate(stages_top):
        x = sx + i * (sw + sgap)
        svg.rect(x, 72, sw, 130, fill=fill)
        svg.text(x + sw / 2, 92, title, size=FS_SMALL, bold=True)
        svg.line(x + 8, 104, x + sw - 8, 104, color='dark')
        for j, line in enumerate(details):
            svg.mono(x + 8, 120 + j * 20, line, size=10)
        if i < len(stages_top) - 1:
            svg.arrow(x + sw + 2, 72 + 65, x + sw + sgap - 2, 72 + 65)

    # Arrow down
    svg.arrow(w / 2, 202, w / 2, 240)
    svg.text(w / 2 + 60, 222, "PPT 完成", size=FS_SMALL, fill='text_light')

    # Bottom pipeline: PPT → Video
    svg.text(w / 2, 255, "階段二：影片合成", size=FS_SMALL, bold=True, fill='text_light')

    stages_bot = [
        ("逐頁截圖", 'medium', [
            "slide-01.png",
            "slide-02.png",
            "...",
        ]),
        ("講解稿生成", 'light', [
            "LLM 生成口語化",
            "講解文字(每頁)",
            "引導性敘述",
        ]),
        ("TTS 合成", 'light', [
            "文字 → 語音",
            "speech-01.mp3",
            "speech-02.mp3",
        ]),
        ("音畫同步", 'medium', [
            "ffmpeg 合成",
            "截圖時長=音訊時長",
            "轉場效果",
        ]),
        ("最終影片", 'dark', [
            "output.mp4",
            "5-15 分鐘",
            "視覺+聽覺雙通道",
        ]),
    ]

    for i, (title, fill, details) in enumerate(stages_bot):
        x = sx + i * (sw + sgap)
        svg.rect(x, 268, sw, 130, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(x + sw / 2, 288, title, size=FS_SMALL, bold=True, fill=tc)
        svg.line(x + 8, 300, x + sw - 8, 300, color='dark')
        for j, line in enumerate(details):
            fc = 'white' if fill in ('dark', 'darker') else 'text'
            svg.mono(x + 8, 316 + j * 20, line, size=10, fill=fc)
        if i < len(stages_bot) - 1:
            svg.arrow(x + sw + 2, 268 + 65, x + sw + sgap - 2, 268 + 65)

    # Bottom: key metrics
    svg.line(30, 420, w - 30, 420, color='dark', dash=True)
    svg.text(w / 2, 440, "驗收標準", size=FS_BODY, bold=True)

    criteria = [
        ("PPT", "10-20 頁 · 覆蓋主要貢獻 · ≥3 原圖表"),
        ("渲染", "零文字溢位 · 佈局合理 · 圖文匹配"),
        ("影片", "5-15 分鐘 · 音畫同步 · 敘述連貫"),
    ]
    cx = 60
    for label, desc in criteria:
        _pill(svg, cx, 458, 60, 26, label, fill='dark', font_size=12, bold=True)
        svg.text(cx + 70, 471, desc, size=FS_TINY, fill='text_light', anchor='start')
        cx += 265

    svg.save(os.path.join(OUT, 'fig5-6.svg'))


# ──────────────────────── fig5-7 ────────────────────────

def fig5_8():
    """動態表單生成流程（LLM→HTML→JSON→繼續）"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "動態表單生成：結構化意圖澄清", size=FS_TITLE, bold=True)

    # Step 1: User input
    svg.rect(20, 60, 200, 60, fill='medium')
    svg.text(120, 82, "使用者輸入", size=FS_SMALL, bold=True)
    svg.text(120, 100, "\"我想訂去北京的機票\"", size=FS_TINY, fill='text_light')

    svg.arrow(220, 90, 260, 90)

    # Step 2: LLM analyzes and generates form
    svg.rect(260, 55, 260, 140, fill='white', stroke='border', dash=True)
    svg.text(390, 75, "LLM 分析 → 生成表單程式碼", size=FS_SMALL, bold=True)
    form_code = [
        '<form id="clarify">',
        ' <input type="text"',
        '  name="from" label="出發城市"/>',
        ' <input type="date"',
        '  name="depart" label="出發日"/>',
        ' <select name="type">',
        '  <option>單程</option>',
        '  <option>往返</option>',
        ' </select>',
        '</form>',
    ]
    svg.rect(270, 90, 240, len(form_code) * 13 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(form_code):
        svg.mono(276, 103 + j * 13, line, size=9)

    svg.arrow(520, 130, 560, 130)

    # Step 3: Rendered form (visual representation)
    svg.rect(560, 55, 300, 200, fill='white', stroke='border')
    svg.text(710, 75, "渲染後的表單介面", size=FS_SMALL, bold=True)

    fields = [
        ("出發城市", "上海", 95),
        ("出發日期", "2025-08-15", 135),
        ("旅行型別", "往返 ▾", 175),
        ("返程日期", "2025-08-22", 215),
    ]
    for label, value, fy in fields:
        svg.text(580, fy, label, size=FS_TINY, anchor='start', bold=True)
        svg.rect(660, fy - 12, 180, 24, fill='code_bg', stroke='dark', rx=3)
        svg.mono(668, fy, value, size=11)

    _pill(svg, 660, 238, 80, 26, "提交", fill='dark', font_size=FS_SMALL, bold=True)

    # Step 4: JSON result
    svg.arrow(710, 268, 710, 300)
    svg.rect(560, 300, 300, 110, fill='white', stroke='border', dash=True)
    svg.text(710, 318, "結構化 JSON 返回", size=FS_SMALL, bold=True)
    json_lines = [
        '{"from": "上海",',
        ' "depart": "2025-08-15",',
        ' "type": "往返",',
        ' "return": "2025-08-22"}',
    ]
    svg.rect(570, 330, 280, len(json_lines) * 16 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(json_lines):
        svg.mono(578, 344 + j * 16, line, size=11)

    # Step 5: Agent continues with structured data
    svg.arrow(560, 390, 400, 440)

    svg.rect(100, 430, 500, 50, fill='medium')
    svg.text(350, 448, "Agent 攜帶完整引數繼續執行任務", size=FS_BODY, bold=True)
    svg.text(350, 468, "search_flights(from='上海', to='北京', depart='2025-08-15', ...)", size=FS_TINY, fill='text_light')

    # Comparison: text vs form
    svg.rect(20, 280, 250, 140, fill='light')
    svg.text(145, 300, "對比: 純文字 vs 表單", size=FS_SMALL, bold=True)
    comp = [
        "文字問答: 10 輪對話",
        "  Q1: 從哪出發? A: 上海",
        "  Q2: 幾號? A: 8月15",
        "  Q3: 單程還是往返? ...",
        "",
        "動態表單: 1 次提交",
        "  所有資訊一次收集完成",
        "  級聯邏輯自動處理",
    ]
    for j, line in enumerate(comp):
        svg.mono(30, 318 + j * 13, line, size=10)

    # Bottom annotation
    svg.text(w / 2, 510, "表單程式碼由 LLM 動態生成 → 級聯邏輯: 選\"往返\"時自動顯示返程日期", size=FS_SMALL, fill='darker')

    svg.save(os.path.join(OUT, 'fig5-8.svg'))


# ──────────────────────── fig5-8 ────────────────────────

def fig5_9():
    """SQL 查詢 Agent（artifact 模式 — 資料繞過 LLM）"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "SQL 查詢 Agent：Artifact 模式 vs 傳統模式", size=FS_TITLE, bold=True)

    # Top: Traditional mode (data through LLM)
    svg.rect(20, 55, w - 40, 200, fill='white', stroke='border', dash=True)
    svg.text(60, 78, "傳統模式: 資料經過 LLM（低效）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 110, 65, 80, 24, "✗ 低效", fill='dark', font_size=12, bold=True)

    trad_steps = [
        ("使用者", 'medium', "\"每部門\\n人數？\""),
        ("LLM", 'light', "生成\\nSQL"),
        ("DB", 'medium', "執行\\n查詢"),
        ("LLM", 'light', "閱讀\\n5000行"),
        ("使用者", 'medium', "文字\\n描述"),
    ]
    tsx = 60
    for i, (name, fill, desc) in enumerate(trad_steps):
        svg.rect(tsx, 100, 130, 60, fill=fill)
        svg.text(tsx + 65, 118, name, size=FS_SMALL, bold=True)
        for j, line in enumerate(desc.split('\\n')):
            svg.text(tsx + 65, 138 + j * 16, line, size=FS_TINY, fill='text_light')
        if i < len(trad_steps) - 1:
            svg.arrow(tsx + 130, 130, tsx + 150, 130)
        tsx += 155

    svg.rect(60, 175, w - 120, 30, fill='code_bg', stroke='dark', rx=3)
    svg.mono(70, 190, "問題: LLM 抄寫資料易出錯 · 消耗大量 token · 延遲高", size=12)

    # Separator
    svg.line(30, 265, w - 30, 265, color='dark', dash=True)

    # Bottom: Artifact mode (data bypasses LLM)
    svg.rect(20, 275, w - 40, 280, fill='white', stroke='border', dash=True)
    svg.text(60, 298, "Artifact 模式: 資料直達前端（高效）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 110, 285, 80, 24, "✓ 高效", fill='medium', font_size=12, bold=True)

    # LLM generates code, not data
    svg.rect(40, 315, 250, 120, fill='light')
    svg.text(165, 335, "LLM 只生成程式碼", size=FS_SMALL, bold=True)
    sql_code = [
        "build_artifact(",
        '  type="sql",',
        '  code="SELECT dept,',
        '    COUNT(*) as cnt',
        '    FROM employees',
        '    GROUP BY dept")',
    ]
    svg.rect(50, 345, 230, len(sql_code) * 14 + 8, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(sql_code):
        svg.mono(58, 358 + j * 14, line, size=10)

    svg.arrow(290, 380, 340, 380)

    # Frontend executes directly
    svg.rect(340, 315, 250, 120, fill='medium')
    svg.text(465, 335, "前端直接執行", size=FS_SMALL, bold=True)
    svg.rect(350, 348, 230, 75, fill='code_bg', stroke='dark', rx=3)
    table = [
        "┌────────┬──────┐",
        "│ dept   │ cnt  │",
        "├────────┼──────┤",
        "│ 研發部 │  42  │",
        "│ 市場部 │  28  │",
        "└────────┴──────┘",
    ]
    for j, line in enumerate(table):
        svg.mono(358, 360 + j * 12, line, size=9)

    svg.arrow(590, 380, 640, 380)

    # Visualization artifact
    svg.rect(640, 315, 210, 120, fill='light')
    svg.text(745, 335, "視覺化 Artifact", size=FS_SMALL, bold=True)
    svg.text(745, 355, "第二個 artifact:", size=FS_TINY, fill='text_light')
    svg.rect(650, 365, 190, 60, fill='code_bg', stroke='dark', rx=3)
    svg.mono(658, 380, "build_artifact(", size=10)
    svg.mono(658, 394, '  type="chart",', size=10)
    svg.mono(658, 408, '  code="bar(data)")', size=10)

    # Data flow annotation
    svg.rect(180, 450, 520, 45, fill='dark')
    svg.text(440, 465, "資料流: DB → 前端 → 視覺化 （完全繞過 LLM）", size=FS_BODY, fill='white', bold=True)
    svg.text(440, 483, "LLM 只負責生成程式碼，不參與資料傳遞", size=FS_TINY, fill='white')

    # Data flow arrow (bypass)
    svg.arrow_curved(465, 435, 745, 435, curve=25, label="SQL結果直傳", dash=True, color='dark')

    svg.save(os.path.join(OUT, 'fig5-9.svg'))


# ──────────────────────── fig5-6 ────────────────────────

def fig5_7():
    """實驗 5.10：生產日誌智慧診斷流水線"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 5.10：生產日誌智慧診斷", size=FS_TITLE, bold=True)

    # Pipeline: left to right, then down
    # Row 1: ingestion → analysis
    svg.rect(20, 60, 250, 160, fill='white', stroke='border', dash=True)
    svg.text(145, 82, "① 日誌採集", size=FS_BODY, bold=True)
    log_lines = [
        "trajectory_001.json:",
        '  {"role":"user","content":',
        '   "取消訂單 #12345"}',
        '  {"role":"assistant",',
        '   "tool_call":"cancel_order"}',
        '  {"role":"tool","result":',
        '   "ERROR: no insurance"}',
        '  → Agent 未告知使用者原因',
    ]
    svg.rect(30, 98, 230, len(log_lines) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(log_lines):
        svg.mono(38, 112 + j * 14, line, size=9)

    svg.arrow(270, 140, 310, 140)

    svg.rect(310, 60, 260, 160, fill='white', stroke='border', dash=True)
    svg.text(440, 82, "② LLM 分析", size=FS_BODY, bold=True)
    analysis = [
        "輸入: 軌跡 + 架構文件 + PRD",
        "",
        "分析維度:",
        "  - 執行流程是否符合預期",
        "  - 工具呼叫是否正確",
        "  - 錯誤處理是否得當",
        "  - 使用者體驗是否滿意",
        "",
        "→ 定位偏差環節和模組",
    ]
    for j, line in enumerate(analysis):
        svg.mono(320, 100 + j * 14, line, size=10)

    svg.arrow(570, 140, 610, 140)

    svg.rect(610, 60, 250, 160, fill='white', stroke='border', dash=True)
    svg.text(735, 82, "③ 結構化報告", size=FS_BODY, bold=True)
    report = [
        "問題報告:",
        "  優先順序: P1 (使用者流失風險)",
        "  模組: cancellation_handler",
        "  描述: 取消失敗後未向",
        "    使用者解釋原因和替代方案",
        "  建議: 新增失敗原因說明",
        "    和購買保險的引導",
    ]
    svg.rect(620, 98, 230, len(report) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(report):
        svg.mono(628, 112 + j * 14, line, size=9)

    # Row 2: test case generation → issue creation
    svg.arrow(w / 2, 220, w / 2, 260)

    svg.rect(60, 260, 370, 160, fill='white', stroke='border', dash=True)
    svg.text(245, 282, "④ 迴歸測試用例生成", size=FS_BODY, bold=True)
    test_code = [
        "def test_cancel_no_insurance():",
        '  """軌跡 #001, 輪次 3-5"""',
        "  # 重放: 使用者請求取消經濟艙",
        "  resp = agent.run(",
        '    "取消訂單 #12345")',
        "  # 驗證: 應解釋原因",
        '  assert "保險" in resp.text',
        '  assert "替代方案" in resp.text',
        "  # 驗證: 不應直接報錯",
        '  assert "ERROR" not in resp.text',
    ]
    svg.rect(70, 298, 350, len(test_code) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(test_code):
        svg.mono(78, 312 + j * 14, line, size=10)

    svg.arrow(430, 340, 470, 340)

    svg.rect(470, 260, 380, 160, fill='white', stroke='border', dash=True)
    svg.text(660, 282, "⑤ GitHub Issue 自動建立", size=FS_BODY, bold=True)
    issue = [
        "gh issue create \\",
        '  --title "P1: 取消失敗缺少',
        '    使用者引導" \\',
        '  --body "**問題**: Agent 在',
        '    cancel_order 失敗後直接',
        '    返回錯誤，未解釋原因...',
        '    **軌跡**: #001 輪次 3-5',
        '    **測試**: test_cancel_..." \\',
        '  --assignee @backend-team',
    ]
    svg.rect(480, 298, 360, len(issue) * 14 + 10, fill='code_bg', stroke='dark', rx=3)
    for j, line in enumerate(issue):
        svg.mono(488, 312 + j * 14, line, size=10)

    # Bottom: full pipeline summary
    svg.rect(100, 445, w - 200, 44, fill='dark')
    svg.text(w / 2, 460, "端到端自動化：日誌 → 分析 → 報告 → 測試 → Issue", size=FS_BODY, fill='white', bold=True)
    svg.text(w / 2, 480, "透過 MCP 對接 GitHub · 測試框架自動重放驗證", size=FS_TINY, fill='white')

    svg.text(w / 2, 530, "將人工診斷成本從小時級降低到分鐘級", size=FS_SMALL, fill='darker', bold=True)

    svg.save(os.path.join(OUT, 'fig5-7.svg'))


# ──────────────────────── fig5-9 ────────────────────────

def fig5_10():
    """Agent 自舉迴圈（自我複製與進化）"""
    w, h = 880, 555
    svg = SVG(w, h)
    svg.text(w / 2, 30, "Agent 自舉：從程式碼到自我複製", size=FS_TITLE, bold=True)

    # Evolution timeline at top
    stages = [
        ("塵埃→恆星", "物理定律"),
        ("恆星→行星", "引力聚合"),
        ("行星→生命", "DNA 自複製"),
        ("生命→智慧體", "程式碼自舉"),
    ]
    sx = 60
    for i, (stage, mechanism) in enumerate(stages):
        fill = 'dark' if i == 3 else ('medium' if i == 2 else 'light')
        svg.rect(sx, 55, 180, 50, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(sx + 90, 72, stage, size=FS_SMALL, bold=True, fill=tc)
        svg.text(sx + 90, 92, mechanism, size=FS_TINY, fill='white' if fill == 'dark' else 'text_light')
        if i < len(stages) - 1:
            svg.arrow(sx + 180, 80, sx + 195, 80)
        sx += 200

    # Key distinction
    svg.line(30, 120, w - 30, 120, color='dark', dash=True)

    svg.rect(30, 135, 400, 70, fill='light')
    svg.text(230, 155, "DNA 自複製: 隨機變異 + 自然選擇", size=FS_SMALL, bold=True)
    svg.text(230, 177, "不理解自身 · 不能定向修改 · 37億年盲目試錯", size=FS_TINY, fill='text_light')

    svg.rect(450, 135, 400, 70, fill='dark')
    svg.text(650, 155, "Agent 自舉: 理解程式碼 + 定向設計", size=FS_SMALL, bold=True, fill='white')
    svg.text(650, 177, "理解自身機制 · 有目的地創造 · 繼承最佳實踐", size=FS_TINY, fill='white')

    # Bootstrap cycle (main diagram)
    svg.rect(20, 225, 390, 295, fill='white', stroke='border', dash=True)
    svg.text(215, 248, "原始 Agent (自身程式碼)", size=FS_BODY, bold=True)

    svg.rect(30, 265, 175, 124, fill='light')
    svg.text(118, 285, "系統提示詞", size=FS_SMALL, bold=True)
    svg.text(40, 308, "你是一個航空客服", size=12, anchor='start')
    svg.text(40, 326, "取消規則: ...", size=12, anchor='start')
    svg.text(40, 344, "轉接規則: ...", size=12, anchor='start')
    svg.text(40, 362, "工具: cancel_order", size=12, anchor='start')

    svg.rect(215, 265, 185, 124, fill='light')
    svg.text(308, 285, "Agent 框架程式碼", size=FS_SMALL, bold=True)
    svg.mono(225, 308, "loop:", size=12)
    svg.mono(225, 326, "  msg = llm(ctx)", size=12)
    svg.mono(225, 344, "  if tool_call:", size=12)
    svg.mono(225, 362, "    exec(tool)", size=12)

    svg.rect(30, 400, 370, 54, fill='code_bg', stroke='dark', rx=4)
    svg.text(215, 419, "工具定義 + MCP 整合 + 訊息格式", size=FS_SMALL)
    svg.text(215, 438, "經過驗證的高質量實現", size=FS_TINY, fill='text_light')

    # Arrow: self-replication — label placed above dashed box headers
    svg.text(440, 215, "複製 + 修改", size=FS_TINY, fill='text_light', bold=True)
    svg.arrow(410, 375, 470, 375)

    # New Agent
    svg.rect(470, 225, 390, 295, fill='white', stroke='border', dash=True)
    svg.text(665, 248, "新 Agent（定向修改後）", size=FS_BODY, bold=True)

    svg.rect(480, 265, 180, 124, fill='medium')
    svg.text(570, 285, "新系統提示詞", size=FS_SMALL, bold=True)
    svg.text(490, 308, "你是一個電商客服", size=12, anchor='start')
    svg.text(490, 326, "退款規則: ...", size=12, anchor='start')
    svg.text(490, 344, "物流查詢: ...", size=12, anchor='start')
    svg.text(490, 362, "工具: refund_order", size=12, anchor='start')

    svg.rect(670, 265, 180, 124, fill='light')
    svg.text(760, 285, "繼承框架程式碼", size=FS_SMALL, bold=True)
    svg.mono(680, 308, "loop:", size=12)
    svg.mono(680, 326, "  msg = llm(ctx)", size=12)
    svg.mono(680, 344, "  if tool_call:", size=12)
    svg.mono(680, 362, "    exec(tool)", size=12)

    svg.rect(480, 400, 370, 54, fill='code_bg', stroke='dark', rx=4)
    svg.text(665, 419, "新工具 + 新業務邏輯", size=FS_SMALL)
    svg.text(665, 438, "架構框架完全繼承 → 質量有保障", size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig5-10.svg'))


# ──────────────────────── fig5-10 ────────────────────────

def fig5_11():
    """實驗 5.14：Meta-Agent 建立新 Agent 的流水線"""
    w, h = 880, 610
    svg = SVG(w, h)
    svg.text(w / 2, 30, "實驗 5.14：能創造 Agent 的 Agent", size=FS_TITLE, bold=True)

    # Input: user request
    svg.rect(30, 60, 280, 55, fill='medium')
    svg.text(170, 80, "使用者需求", size=FS_SMALL, bold=True)
    svg.text(170, 98, "\"建立一個電商退款客服 Agent\"", size=FS_TINY, fill='text_light')

    svg.arrow(170, 115, 170, 145)

    # Meta-Agent: the creator
    svg.rect(20, 145, 840, 230, fill='white', stroke='border', dash=True)
    svg.text(440, 168, "Meta-Agent (Coding Agent)", size=FS_BODY, bold=True)

    # Step 1: Read reference
    svg.rect(35, 185, 190, 170, fill='light')
    svg.text(130, 205, "① 閱讀參考程式碼", size=FS_SMALL, bold=True)
    svg.mono(45, 228, "read_file:", size=12)
    svg.mono(45, 248, "  agent.py", size=12)
    svg.mono(45, 268, "  tools/*.py", size=12)
    svg.mono(45, 288, "  system_prompt.md", size=12)
    svg.mono(45, 308, "  config.yaml", size=12)
    svg.text(45, 332, "→ 理解架構模式", size=12, anchor='start', fill='text_light')

    svg.arrow(225, 270, 248, 270)

    # Step 2: Copy scaffold
    svg.rect(248, 185, 190, 170, fill='light')
    svg.text(343, 205, "② 複製腳手架", size=FS_SMALL, bold=True)
    svg.mono(258, 228, "cp -r reference/", size=12)
    svg.mono(258, 248, "  → new_agent/", size=12)
    svg.text(258, 278, "保留：", size=12, anchor='start', fill='text_light')
    svg.text(258, 298, "  Agent 迴圈框架", size=12, anchor='start', fill='text_light')
    svg.text(258, 318, "  訊息格式 / KV 最佳化", size=12, anchor='start', fill='text_light')

    svg.arrow(438, 270, 461, 270)

    # Step 3: Targeted modification
    svg.rect(461, 185, 190, 170, fill='medium')
    svg.text(556, 205, "③ 定向修改", size=FS_SMALL, bold=True)
    svg.mono(471, 228, "edit_file:", size=12)
    svg.mono(471, 248, "  system_prompt.md", size=12)
    svg.text(471, 268, "  → 電商退款規則", size=12, anchor='start', fill='text_light')
    svg.mono(471, 290, "  tools/refund.py", size=12)
    svg.text(471, 310, "  → 新增退款工具", size=12, anchor='start', fill='text_light')
    svg.mono(471, 332, "  config.yaml", size=12)

    svg.arrow(651, 270, 674, 270)

    # Step 4: Validate
    svg.rect(674, 185, 175, 170, fill='light')
    svg.text(761, 205, "④ 驗證測試", size=FS_SMALL, bold=True)
    svg.mono(684, 228, "bash:", size=12)
    svg.mono(684, 248, "  python agent.py", size=12)
    svg.text(684, 270, "  → 啟動新 Agent", size=12, anchor='start', fill='text_light')
    svg.text(684, 290, "  → 傳送測試訊息", size=12, anchor='start', fill='text_light')
    svg.text(684, 310, "  → 檢查工具呼叫", size=12, anchor='start', fill='text_light')
    svg.text(684, 330, "  → 驗證對話流程", size=12, anchor='start', fill='text_light')

    # Output: new agent
    svg.arrow(w / 2, 375, w / 2, 410)

    svg.rect(115, 410, 700, 90, fill='white', stroke='border', dash=True)
    svg.text(465, 432, "生成的新 Agent", size=FS_BODY, bold=True)

    outputs = [
        ("system_prompt.md", "電商退款規則"),
        ("tools/refund.py", "退款 / 查詢工具"),
        ("agent.py", "繼承框架程式碼"),
        ("config.yaml", "模型 / 引數配置"),
    ]
    ox = 135
    for fname, desc in outputs:
        svg.rect(ox, 448, 170, 42, fill='light')
        svg.mono(ox + 85, 462, fname, size=10, anchor='middle')
        svg.text(ox + 85, 480, desc, size=FS_TINY, fill='text_light')
        ox += 178

    # Bottom: comparison
    svg.line(30, 515, w - 30, 515, color='dark', dash=True)
    svg.rect(60, 530, 350, 54, fill='light')
    svg.text(235, 549, "從零生成：缺乏最佳實踐", size=FS_SMALL, bold=True)
    svg.text(235, 571, "上下文管理隨意 · 工具設計不規範 · API 過時", size=FS_TINY, fill='text_light')

    svg.rect(470, 530, 350, 54, fill='dark')
    svg.text(645, 549, "基於範例修改：繼承最佳實踐", size=FS_SMALL, bold=True, fill='white')
    svg.text(645, 571, "標準訊息格式 · 規範工具設計 · 現代 API", size=FS_TINY, fill='white')

    svg.save(os.path.join(OUT, 'fig5-11.svg'))


# ──────────────────────── main ────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    figs = [
        fig5_1, fig5_2, fig5_3, fig5_4, fig5_5, fig5_6,
        fig5_7, fig5_8, fig5_9, fig5_10, fig5_11,
    ]
    for fn in figs:
        fn()
        print(f"  ✓ {fn.__name__}: {fn.__doc__}")
    print(f"\nGenerated {len(figs)} figures in {OUT}/")


if __name__ == '__main__':
    main()
