"""Generate all Chapter 2 figures.

9 figures total (fig2-1 through fig2-9):
  fig2-1:  Context window composition (reworked — with actual content snippets)
  fig2-2:  Local LLM tool calling architecture (NEW — Exp 2.1)
  fig2-3:  Chat Template token structure (reworked — larger fonts)
  fig2-4:  KV Cache prefix reuse (reworked — concrete token sequences)
  fig2-5:  System hint injection (reworked — actual hint text)
  fig2-6:  Context compression strategy comparison (reworked — data viz)
  fig2-7:  Context compression pipeline variants (NEW — Exp 2.7)
  fig2-8:  Skills progressive disclosure (reworked — concrete PPTX example)
  fig2-9:  Memory strategy comparison (NEW — Exp 2.10)

Deleted (no longer generated):
  old fig2-4: Prompt結構化 (text code examples already show this)
  old fig2-8: 工作記憶→長期記憶 (text explains clearly)
"""
import sys, os

sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import (
    SVG, COLORS, FONT, MONO,
    FS_TITLE, FS_BODY, FS_SMALL, FS_TINY, FS_LABEL, STROKE_W, CORNER_R,
    _escape,
)

OUT = os.path.join(os.path.dirname(__file__), 'images')


# ════════════════════════════════════════════════════════════════════
#  fig2-1: Context Window Composition (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_1():
    """Context window with actual content snippets in each layer."""
    W, H = 820, 620
    s = SVG(W, H)

    s.text(410, 30, '上下文視窗的構成概覽', size=FS_TITLE, bold=True)

    lx, lw = 40, 700
    layers = [
        ('系統提示詞（System Prompt）', 'medium', [
            '"You are a helpful assistant. You MUST answer concisely."',
            '"Use tools when the user asks for real-time information."',
        ]),
        ('工具定義（Tool Definitions）', 'light', [
            '{"name": "web_search", "description": "Search the web",',
            ' "parameters": {"query": {"type": "string"}}}',
        ]),
        ('對話歷史（Conversation History）', 'light', [
            'user: "北京今天天氣怎麼樣？"',
            'assistant: [tool_call] → get_weather("北京")',
            'tool: {"temp": "23°C", "conditions": "晴"}',
        ]),
        ('推理軌跡（Reasoning Trace）', '#e8e8e8', [
            '<think>使用者問天氣，我已經獲得了工具結果，',
            '可以直接彙總回答，無需再呼叫工具。</think>',
        ]),
        ('當前生成位置 →', 'white', [
            'assistant: "北京今天晴，氣溫 23°C..."  ← LLM 正在生成',
        ]),
    ]

    y = 60
    for title, fill, snippets in layers:
        block_h = 30 + len(snippets) * 22 + 10
        s.rect(lx, y, lw, block_h, fill=fill)
        s.text(lx + 15, y + 20, title, size=FS_BODY, bold=True, anchor='start')
        for i, line in enumerate(snippets):
            s.mono(lx + 25, y + 42 + i * 22, line, size=FS_TINY)
        y += block_h + 8

    # Right side brace
    brace_top = 60
    brace_bot = y - 8
    s.brace_right(lx + lw + 8, brace_top, brace_bot)
    s.text(lx + lw + 15, (brace_top + brace_bot) / 2 - 12, '上下文', size=FS_BODY, bold=True, anchor='start')
    s.text(lx + lw + 15, (brace_top + brace_bot) / 2 + 12, '視窗', size=FS_BODY, bold=True, anchor='start')

    # Bottom annotation
    s.rect(100, y + 15, 620, 50, fill='code_bg', stroke='dark', rx=4)
    s.text(410, y + 32, '視窗大小：Qwen3 = 32K tokens | Claude = 200K | Gemini = 2M', size=FS_SMALL)
    s.text(410, y + 52, '所有內容序列化為 token 流 → Transformer 注意力機制處理', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-1.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-2: Local LLM Tool Calling Architecture (NEW — Exp 2.1)
# ════════════════════════════════════════════════════════════════════

def fig2_2():
    """Qwen3-0.6B on local hardware + tool registry + ReAct loop."""
    W, H = 820, 540
    s = SVG(W, H)

    s.text(410, 30, '實驗 2.1：本地 LLM 工具呼叫架構', size=FS_TITLE, bold=True)

    # Hardware box (left)
    s.group_box(30, 65, 220, 130, '本地硬體')
    s.box(50, 100, 180, 35, 'Apple M2 / 16GB', fill='light', font_size=FS_SMALL)
    s.box(50, 145, 180, 35, 'MLX 推理後端', fill='light', font_size=FS_SMALL)

    # Model box (center)
    s.rect(290, 65, 240, 130, fill='medium')
    s.text(410, 95, 'Qwen3-0.6B', size=FS_BODY, bold=True)
    s.text(410, 120, '0.6B 引數 · Q4 量化', size=FS_SMALL, fill='text_light')
    s.text(410, 145, '> 100 tokens/s', size=FS_SMALL, fill='text_light')
    s.text(410, 170, 'ReAct + 工具呼叫能力', size=FS_SMALL)

    # Tool registry (right)
    s.group_box(570, 65, 220, 130, '工具登錄檔')
    s.box(590, 100, 180, 35, 'get_current_time', fill='code_bg', font_size=FS_SMALL)
    s.box(590, 145, 180, 35, 'get_temperature', fill='code_bg', font_size=FS_SMALL)

    # Arrows hardware → model, model ↔ tools
    s.arrow(252, 130, 288, 130)
    s.arrow(532, 122, 568, 122)
    s.arrow(568, 138, 532, 138)

    # ReAct loop (below)
    s.group_box(50, 220, 720, 290, 'ReAct 迴圈')

    # Step 1: User query
    s.rect(80, 260, 300, 40, fill='light')
    s.text(90, 280, 'user: "What\'s the time and weather in Vancouver?"', size=FS_TINY, anchor='start')

    # Step 2: Think
    s.rect(80, 310, 300, 55, fill='#e8e8e8')
    s.text(90, 328, '<think>', size=FS_TINY, anchor='start', bold=True)
    s.text(90, 348, '需要呼叫 get_current_time', size=FS_TINY, anchor='start')
    s.text(90, 363, '和 get_temperature 兩個工具', size=FS_TINY, anchor='start')
    s.arrow(230, 302, 230, 308)

    # Step 3: Tool calls
    s.rect(80, 375, 300, 50, fill='code_bg', stroke='dark', rx=4)
    s.mono(90, 393, '<tool_call>', size=FS_TINY)
    s.mono(90, 411, '{"name":"get_current_time",...}', size=FS_TINY)
    s.arrow(230, 367, 230, 373)

    # Step 4: Tool results
    s.rect(80, 435, 300, 40, fill='light')
    s.text(90, 455, '<tool_response> {"time":"05:18","temp":"13.2°C"}', size=FS_TINY, anchor='start')
    s.arrow(230, 427, 230, 433)

    # Right side: loop arrow + final output
    # 迴圈箭頭改走左側外緣，避免遮擋左列內的文字
    s.arrow_curved(80, 455, 80, 280, curve=-40, color='dark')
    s.text(30, 367, '繼續迴圈', size=FS_TINY, fill='text_light', bold=True)

    # Final output box
    s.rect(430, 280, 320, 55, fill='medium')
    s.text(440, 298, '最終輸出:', size=FS_SMALL, bold=True, anchor='start')
    s.text(440, 318, '"Vancouver: 05:18 AM, 13.2°C,', size=FS_TINY, anchor='start')
    s.text(440, 335, '  clear sky, humidity 93%"', size=FS_TINY, anchor='start')

    # Streaming annotation
    s.rect(430, 360, 320, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(590, 378, '流式處理關鍵時序', size=FS_SMALL, bold=True)
    s.text(440, 400, '<think>...  → 隱藏，不顯示給使用者', size=FS_TINY, anchor='start')
    s.text(440, 418, '普通文字    → 實時流式展示', size=FS_TINY, anchor='start')
    s.text(440, 436, '<tool_call> → 解析並執行工具', size=FS_TINY, anchor='start')

    s.save(f'{OUT}/fig2-2.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-3: Chat Template Token Structure (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_3():
    """Chat template token structure with actual token content and larger fonts."""
    W, H = 920, 580
    s = SVG(W, H)

    s.text(W / 2, 30, 'Chat Template 的 Token 結構', size=FS_TITLE, bold=True)

    lx = 40
    rw = 800

    y = 65
    segments = [
        ('<|im_start|>system', 'darker', 'white', [
            '# Tools',
            'You may call one or more functions...',
            '<tools>{"name":"get_weather",...}</tools>',
            '<tool_call>{"name":..., "arguments":...}</tool_call>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>user', 'darker', 'white', [
            '"北京今天天氣怎麼樣？"',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '<think>需要查詢天氣，呼叫 get_weather 工具</think>',
            '<tool_call>{"name":"get_weather","args":{"city":"北京"}}</tool_call>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>user', 'darker', 'white', [
            '<tool_response>{"temp":"23°C","sky":"晴"}</tool_response>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '← LLM 從這裡開始生成新 token',
        ]),
    ]

    for tag, tag_fill, _, content_lines in segments:
        if not content_lines:
            # End token — small badge
            s.badge(lx, y, 140, 24, tag, fill=tag_fill, font_size=FS_TINY)
            y += 32
        else:
            total_h = 26 + len(content_lines) * 20 + 8
            s.rect(lx, y, rw, total_h, fill='light')
            s.badge(lx + 5, y + 4, 200, 22, tag, fill=tag_fill, font_size=FS_TINY)
            for i, line in enumerate(content_lines):
                s.mono(lx + 220, y + 8 + i * 20 + 12, line, size=FS_TINY)
            y += total_h + 4

    # Right annotation
    s.text(lx + rw + 5, 80, '特殊', size=FS_SMALL, anchor='start', bold=True)
    s.text(lx + rw + 5, 100, '標記', size=FS_SMALL, anchor='start', bold=True)

    s.save(f'{OUT}/fig2-3.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-4: KV Cache Prefix Reuse (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_4():
    """KV Cache with concrete token sequences showing prefix reuse."""
    W, H = 820, 480
    s = SVG(W, H)

    s.text(410, 30, 'KV Cache 字首複用機制', size=FS_TITLE, bold=True)

    lx = 40
    bw = 740

    # Request 1
    s.text(lx, 70, '請求 1', size=FS_BODY, bold=True, anchor='start')
    # System prompt portion (cached)
    s.rect(lx, 85, 380, 40, fill='medium')
    s.text(lx + 190, 105, 'System Prompt + Tools (1200 tokens)', size=FS_SMALL)
    # User message
    s.rect(lx + 385, 85, 180, 40, fill='light')
    s.text(lx + 475, 105, 'user: "天氣如何？"', size=FS_SMALL)
    # KV computed
    s.rect(lx + 570, 85, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 105, '→ 生成回答', size=FS_SMALL)

    # Request 2 (cache hit)
    s.text(lx, 155, '請求 2', size=FS_BODY, bold=True, anchor='start')
    # Same prefix — cached
    s.rect(lx, 170, 380, 40, fill='medium')
    s.text(lx + 190, 190, 'System Prompt + Tools（快取命中 ✓）', size=FS_SMALL)
    # Different user msg
    s.rect(lx + 385, 170, 180, 40, fill='light')
    s.text(lx + 475, 190, 'user: "時間幾點？"', size=FS_SMALL)
    s.rect(lx + 570, 170, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 190, '→ 生成回答', size=FS_SMALL)

    # Cache reuse arrow
    s.arrow(lx + 190, 127, lx + 190, 168, label='KV 複用', color='dark')

    # Request 3 (cache miss)
    s.text(lx, 245, '請求 3', size=FS_BODY, bold=True, anchor='start')
    s.text(lx + 85, 245, '（系統提示變了）', size=FS_SMALL, anchor='start', fill='text_light')
    s.rect(lx, 260, 400, 40, fill='white', dash=True)
    s.text(lx + 200, 280, 'System + Tools + "Time: 10:30:45"', size=FS_SMALL)
    s.rect(lx + 405, 260, 160, 40, fill='light')
    s.text(lx + 485, 280, 'user: "天氣如何？"', size=FS_SMALL)
    s.rect(lx + 570, 260, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 280, '→ 全部重算 ✗', size=FS_SMALL)

    # Performance comparison
    s.rect(80, 330, 660, 130, fill='code_bg', stroke='dark', rx=4)
    s.text(410, 355, '效能對比（3000 token 上下文）', size=FS_BODY, bold=True)

    # Table header
    s.line(100, 370, 720, 370, color='dark')
    s.text(230, 390, '快取命中', size=FS_SMALL, bold=True)
    s.text(490, 390, '快取失效', size=FS_SMALL, bold=True)
    s.line(100, 405, 720, 405, color='dark')

    # Rows
    s.text(130, 425, 'TTFT', size=FS_SMALL, anchor='start')
    s.text(230, 425, '~0.5 秒', size=FS_SMALL)
    s.text(490, 425, '3 - 5 秒', size=FS_SMALL)

    s.text(130, 450, '成本', size=FS_SMALL, anchor='start')
    s.text(230, 450, '僅新 token 計費', size=FS_SMALL)
    s.text(490, 450, '全部 token 重新計費', size=FS_SMALL)

    s.save(f'{OUT}/fig2-4.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-5: Agent 狀態列 Injection Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_5():
    """Show WHERE hints are inserted with actual hint text."""
    W, H = 820, 580
    s = SVG(W, H)

    s.text(410, 30, '系統提示注入架構', size=FS_TITLE, bold=True)

    # Left: WITHOUT hints
    col_w = 350
    col_gap = 70
    lx1 = 30
    lx2 = lx1 + col_w + col_gap

    s.text(lx1 + col_w / 2, 65, '無系統提示', size=FS_BODY, bold=True)
    s.text(lx2 + col_w / 2, 65, '有系統提示', size=FS_BODY, bold=True)

    # Left column: raw trajectory
    y = 90
    left_items = [
        ('system', 'System Prompt + Tools', 'medium', 35),
        ('user', '"幫我聯絡 Xfinity 砍價"', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 1 次', '#e8e8e8', 35),
        ('tool', '結果: 等待 45 分鐘, 未接通', 'light', 35),
        ('assistant', 'web_search("Xfinity deals")', '#e8e8e8', 35),
        ('tool', '結果: [大量搜尋內容...]', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 2 次', '#e8e8e8', 35),
        ('tool', '結果: 接通，報價 $65/月', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 3 次', '#e8e8e8', 35),
        ('tool', '結果: 確認降價到 $59/月', 'light', 35),
        ('user', '"能不能再打一次催一下？"', 'light', 35),
    ]

    for role, content, fill, h in left_items:
        s.rect(lx1, y, col_w, h, fill=fill, rx=4)
        s.text(lx1 + 8, y + h / 2, f'{role}:', size=FS_TINY, anchor='start', bold=True)
        s.mono(lx1 + 65, y + h / 2, content, size=FS_TINY - 2)
        y += h + 3

    s.text(lx1 + col_w / 2, y + 15, '→ 模型需掃描全部上下文來"數"', size=FS_SMALL, fill='text_light')
    s.text(lx1 + col_w / 2, y + 35, '撥打了幾次電話，容易數錯', size=FS_SMALL, fill='text_light')

    # Right column: with system hints
    y = 90
    right_items = [
        ('system', 'System Prompt + Tools', 'medium', 35),
        ('user', '"幫我聯絡 Xfinity 砍價"', 'light', 35),
        ('...', '[ 同樣的軌跡內容 ]', '#e8e8e8', 90),
        ('user', '"能不能再打一次催一下？"', 'light', 35),
    ]
    for role, content, fill, h in right_items:
        s.rect(lx2, y, col_w, h, fill=fill, rx=4)
        s.text(lx2 + 8, y + h / 2, f'{role}:', size=FS_TINY, anchor='start', bold=True)
        s.mono(lx2 + 65, y + h / 2, content, size=FS_TINY - 2)
        y += h + 3

    # System hint block (highlighted)
    hint_y = y
    hint_h = 130
    s.rect(lx2, hint_y, col_w, hint_h, fill='medium', stroke='border', rx=4)
    s.text(lx2 + 10, hint_y + 18, '<agent_status>', size=FS_SMALL, bold=True, anchor='start')
    hints = [
        'phone_call 已呼叫 3 次 (Xfinity: 3)',
        '約束檢查: 已達上限 (3/3) ✗',
        'TODO: [✓]聯絡Xfinity [✓]確認降價',
        '當前時間: 2025-09-14 10:30',
        '當前狀態: 等待使用者確認',
    ]
    for i, h in enumerate(hints):
        s.mono(lx2 + 15, hint_y + 40 + i * 20, h, size=FS_TINY - 2)
    s.text(lx2 + col_w - 10, hint_y + hint_h - 12, '</agent_status>', size=FS_SMALL, bold=True, anchor='end')

    s.text(lx2 + col_w / 2, hint_y + hint_h + 18, '→ 模型直接讀取已提煉狀態', size=FS_SMALL, fill='text_light')
    s.text(lx2 + col_w / 2, hint_y + hint_h + 38, '準確遵守約束，不再撥打', size=FS_SMALL, fill='text_light')

    # VS divider
    s.text(lx1 + col_w + col_gap / 2, 300, 'VS', size=FS_BODY, bold=True)

    s.save(f'{OUT}/fig2-5.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-6: Context Compression Strategy Comparison (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_6():
    """Data visualization comparing 6 strategies with actual experiment numbers."""
    W, H = 820, 530
    s = SVG(W, H)

    s.text(410, 30, '上下文壓縮策略對比（OpenAI 創始人追蹤實驗）', size=FS_TITLE, bold=True)

    # Table layout
    tx = 30
    tw = 760

    # Column positions
    cols = [
        (tx, 145, '策略'),
        (tx + 150, 90, 'Token 用量'),
        (tx + 250, 65, '壓縮率'),
        (tx + 325, 55, '迭代次數'),
        (tx + 400, 65, '結果'),
        (tx + 475, 280, '視覺化（Token 用量對比）'),
    ]

    header_y = 65
    for cx, cw, label in cols:
        s.text(cx + cw / 2, header_y, label, size=FS_SMALL, bold=True)

    s.line(tx, header_y + 12, tx + tw, header_y + 12)

    strategies = [
        ('無壓縮', '> 110K', '100%', '5（失敗）', False, 110000),
        ('個體摘要', '123,205', '6.8%', '24', True, 123205),
        ('組合摘要', '55,462', '2.1%', '21', True, 55462),
        ('上下文感知', '25,198', '0.9%', '15', True, 25198),
        ('感知+引用', '45,544', '1.4%', '17', True, 45544),
        ('自適應視窗', '181,372', '—', '8', True, 181372),
    ]

    max_tokens = 190000
    bar_x = tx + 475
    bar_max_w = 280

    for i, (name, tokens, ratio, iters, success, token_val) in enumerate(strategies):
        y = header_y + 30 + i * 62

        # Strategy name
        s.text(tx + 72, y + 15, name, size=FS_SMALL, anchor='middle',
               bold=(name == '上下文感知'))

        # Token count
        s.text(tx + 195, y + 15, tokens, size=FS_SMALL)

        # Compression rate
        s.text(tx + 282, y + 15, ratio, size=FS_SMALL)

        # Iterations
        s.text(tx + 352, y + 15, iters, size=FS_SMALL)

        # Result
        result_text = '✓ 成功' if success else '✗ 失敗'
        result_color = 'text' if success else 'dark'
        s.text(tx + 432, y + 15, result_text, size=FS_SMALL, fill=result_color)

        # Bar
        bar_w = (token_val / max_tokens) * bar_max_w
        bar_fill = '#e8e8e8' if name != '上下文感知' else 'medium'
        if not success:
            bar_fill = 'white'
        s.rect(bar_x, y, bar_w, 30, fill=bar_fill, stroke='border', rx=3)

    # Highlight best strategy
    best_y = header_y + 30 + 3 * 62 - 5
    s.rect(tx - 2, best_y, tw + 4, 42, fill='white', stroke='border', rx=4, dash=True)

    # Bottom insight
    s.rect(100, H - 60, 620, 45, fill='code_bg', stroke='dark', rx=4)
    s.text(410, H - 45, '上下文感知壓縮：token 減少 77%，成功率最高，迭代次數最少', size=FS_SMALL, bold=True)
    s.text(410, H - 25, '關鍵：將查詢意圖和已有資訊納入壓縮決策', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-6.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-7: Context Compression Pipeline Variants (NEW — Exp 2.7)
# ════════════════════════════════════════════════════════════════════

def fig2_7():
    """6 compression strategies as pipeline variants."""
    W, H = 820, 600
    s = SVG(W, H)

    s.text(410, 30, '實驗 2.7：六種壓縮策略的處理流程', size=FS_TITLE, bold=True)

    # Input annotation
    s.text(410, 58, '每次搜尋返回 ~70K 字元 → 各策略以不同方式處理', size=FS_SMALL, fill='text_light')

    strategies = [
        ('① 無壓縮', '直接保留', '完整原文放入上下文', '> 110K tok → 溢位', False),
        ('② 個體摘要', '獨立摘要', '每個結果獨立生成 2-3 段摘要', '123K tok · 6.8%', True),
        ('③ 組合摘要', '合併摘要', '所有結果拼接後統一摘要', '55K tok · 2.1%', True),
        ('④ 上下文感知', '智慧壓縮', 'Given query + context → 針對性壓縮', '25K tok · 0.9%', True),
        ('⑤ 感知+引用', '智慧+溯源', '壓縮內容 + 保留 URL 引用標記', '45K tok · 1.4%', True),
        ('⑥ 自適應視窗', '延遲壓縮', '< 80% 視窗保留原文，超出批次壓縮', '181K tok · 最大保真', True),
    ]

    lx = 30
    row_h = 78
    start_y = 75

    for i, (name, method, desc, result, success) in enumerate(strategies):
        y = start_y + i * row_h

        # Strategy name badge
        fill = 'darker' if i == 3 else 'dark'
        s.badge(lx, y, 130, 26, name, fill=fill, font_size=FS_TINY)

        # Method box
        s.rect(lx, y + 30, 120, 40, fill='#e8e8e8', rx=4)
        s.text(lx + 60, y + 50, method, size=FS_SMALL)

        # Arrow
        s.arrow(lx + 122, y + 50, lx + 135, y + 50)

        # Description
        s.rect(lx + 138, y + 30, 330, 40, fill='code_bg', stroke='dark', rx=4)
        s.text(lx + 303, y + 50, desc, size=FS_TINY)

        # Arrow
        s.arrow(lx + 470, y + 50, lx + 483, y + 50)

        # Result
        res_fill = 'medium' if i == 3 else ('white' if not success else 'light')
        s.rect(lx + 486, y + 30, 275, 40, fill=res_fill, rx=4)
        s.text(lx + 623, y + 50, result, size=FS_TINY)

    s.save(f'{OUT}/fig2-7.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-8: Skills Progressive Disclosure (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_8():
    """Agent Skills with concrete PPTX example showing 3 layers."""
    W, H = 820, 540
    s = SVG(W, H)

    s.text(410, 30, 'Skills 漸進式披露機制（PPTX Skill 示例）', size=FS_TITLE, bold=True)

    # Layer 1: Metadata (always loaded)
    y1 = 70
    s.rect(40, y1, 740, 90, fill='medium')
    s.text(60, y1 + 20, '第一層：後設資料（啟動時載入，~200 tokens）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y1 + 40, 700, 40, fill='code_bg', rx=4)
    s.mono(70, y1 + 60, 'skills: [{name: "PPTX", desc: "Create PowerPoint presentations from content"}', size=FS_TINY)
    s.mono(70, y1 + 75, '        {name: "PDF",  desc: "Extract and analyze PDF documents"}, ...]', size=FS_TINY - 2)

    # Trigger arrow
    s.arrow(410, y1 + 92, 410, y1 + 115)
    s.text(430, y1 + 103, '任務觸發："從論文生成 PPT"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 2: Core SKILL.md
    y2 = y1 + 120
    s.rect(40, y2, 740, 130, fill='light')
    s.text(60, y2 + 20, '第二層：SKILL.md 核心流程（按需載入，~2K tokens）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y2 + 40, 700, 80, fill='code_bg', rx=4)
    lines2 = [
        'PPTX Skill 核心流程:',
        '1. markitdown 提取文字 → 2. 解壓 PPTX 訪問 XML',
        '3. 修改 slide{N}.xml 內容 → 4. 重新打包為 .pptx',
        '引用: → html2pptx.md | → reference.md | → scripts/',
    ]
    for i, line in enumerate(lines2):
        s.mono(70, y2 + 56 + i * 19, line, size=FS_TINY)

    # Trigger arrow
    s.arrow(410, y2 + 132, 410, y2 + 155)
    s.text(430, y2 + 143, '需要詳細方法："用 HTML 模板建立 PPT"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 3: Sub-documents
    y3 = y2 + 160
    s.rect(40, y3, 740, 130, fill='white', dash=True)
    s.text(60, y3 + 20, '第三層：子文件（選擇性深入，按需載入）', size=FS_BODY, bold=True, anchor='start')

    doc_w = 215
    docs = [
        ('html2pptx.md', 'HTML 模板 → PPT\n的完整工作流'),
        ('reference.md', 'XML 格式規範\n和技術細節'),
        ('scripts/*.py', '可執行工具:\nthumbnail.py 等'),
    ]
    for i, (name, desc) in enumerate(docs):
        dx = 60 + i * (doc_w + 20)
        s.rect(dx, y3 + 45, doc_w, 70, fill='code_bg', stroke='dark', rx=4)
        s.text(dx + doc_w / 2, y3 + 62, name, size=FS_SMALL, bold=True)
        desc_lines = desc.split('\n')
        for j, dl in enumerate(desc_lines):
            s.text(dx + doc_w / 2, y3 + 82 + j * 16, dl, size=FS_TINY, fill='text_light')

    # Bottom: KV Cache note
    s.rect(100, y3 + 140, 620, 35, fill='code_bg', stroke='dark', rx=4)
    s.text(410, y3 + 158, '後設資料固定 → KV Cache 友好 | 動態內容追加 → 不破壞快取', size=FS_SMALL)

    s.save(f'{OUT}/fig2-8.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-9: Mem0 Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_9():
    """Mem0 architecture with actual data flow and concrete memory examples."""
    W, H = 820, 530
    s = SVG(W, H)

    s.text(410, 30, 'Mem0 記憶管理架構', size=FS_TITLE, bold=True)

    # Input conversation
    s.rect(30, 70, 250, 80, fill='light')
    s.text(40, 88, '新對話輸入:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 110, 'user: "我搬到深圳了,', size=FS_TINY)
    s.mono(40, 128, '新地址是南山區科技園"', size=FS_TINY)

    # MemoryBase (center)
    s.rect(310, 65, 200, 100, fill='medium')
    s.text(410, 85, 'MemoryBase', size=FS_BODY, bold=True)
    s.text(410, 108, '記憶生命週期管理', size=FS_SMALL, fill='text_light')
    s.text(410, 130, '分析 → 分類 → 決策', size=FS_SMALL, fill='text_light')
    s.arrow(282, 110, 308, 110)

    # LLMBase (above MemoryBase)
    s.rect(330, 185, 160, 50, fill='#e8e8e8')
    s.text(410, 203, 'LLMBase', size=FS_SMALL, bold=True)
    s.text(410, 222, '語義分析 + 關係判斷', size=FS_TINY)
    s.arrow(410, 167, 410, 183, color='dark')
    s.arrow(410, 183, 410, 167, color='dark')

    # Decision output
    s.rect(310, 255, 200, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(320, 273, '決策結果:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(320, 293, '舊: "使用者住北京海淀"', size=FS_TINY)
    s.mono(320, 311, '→ UPDATE: "住深圳南山"', size=FS_TINY)
    s.mono(320, 329, '→ ADD: "搬家到深圳"', size=FS_TINY - 2)
    s.arrow(410, 237, 410, 253, color='dark')

    # EmbeddingBase (right)
    s.rect(560, 70, 220, 70, fill='light')
    s.text(670, 90, 'EmbeddingBase', size=FS_SMALL, bold=True)
    s.text(670, 112, '文字 → 向量 (計算密集型)', size=FS_TINY, fill='text_light')
    s.arrow(512, 95, 558, 90)

    # VectorStoreBase (right, below)
    s.rect(560, 160, 220, 100, fill='light')
    s.text(670, 180, 'VectorStoreBase', size=FS_SMALL, bold=True)
    s.text(670, 200, '持久化 + 檢索 (I/O密集)', size=FS_TINY, fill='text_light')
    s.text(670, 225, 'Chroma / Qdrant / Milvus', size=FS_TINY, fill='text_light')
    s.text(670, 248, '(HNSW / LSH 索引)', size=FS_TINY, fill='text_light')
    s.arrow(670, 142, 670, 158)

    # Stored memories example
    s.rect(560, 290, 220, 120, fill='code_bg', stroke='dark', rx=4)
    s.text(570, 310, '儲存的記憶條目:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(570, 332, '"住深圳南山科技園"', size=FS_TINY)
    s.mono(570, 352, '"郵箱: john@x.com"', size=FS_TINY)
    s.mono(570, 372, '"偏好: 中文溝通"', size=FS_TINY)
    s.mono(570, 392, '"工作: ML 工程師"', size=FS_TINY)
    s.arrow(670, 262, 670, 288, color='dark')

    # Plugin mechanism note
    s.rect(30, 170, 250, 60, fill='code_bg', stroke='dark', rx=4)
    s.text(155, 192, '外掛機制', size=FS_SMALL, bold=True)
    s.text(155, 212, '可替換 LLM / 嵌入模型 / 儲存後端', size=FS_TINY, fill='text_light')

    # Retrieval path
    s.rect(30, 390, 250, 80, fill='light')
    s.text(40, 408, '記憶檢索:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 430, 'query: "使用者住哪裡？"', size=FS_TINY)
    s.mono(40, 450, '→ 向量相似度匹配', size=FS_TINY)
    s.mono(40, 468, '→ "住深圳南山科技園"', size=FS_TINY)
    s.arrow_curved(282, 430, 558, 350, curve=-30, label='檢索', color='dark')

    s.save(f'{OUT}/fig2-10.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-11: Memobase Multi-type Memory Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_11_memobase():
    """Memobase 4 memory types with concrete examples."""
    W, H = 820, 560
    s = SVG(W, H)

    s.text(410, 30, 'Memobase 多型別記憶架構', size=FS_TITLE, bold=True)

    types = [
        ('情景記憶', 'Episodic', [
            '2025-09-10 使用者預訂上海→東京',
            '2025-09-12 航班改簽至 9/20',
            '2025-09-13 酒店變更為新宿店',
        ], '帶時間戳的事件序列'),
        ('語義記憶', 'Semantic', [
            '使用者 → 是 → ML 工程師',
            '使用者 → 對花生過敏',
            '使用者 → 偏好 → 靠窗座位',
        ], '實體-關係網路'),
        ('程式記憶', 'Procedural', [
            '旅行規劃模式:',
            '  目的地→預算→交通→住宿→活動',
            '(從多次互動中自動提取)',
        ], '可複用策略模式'),
        ('工作記憶', 'Working', [
            '當前任務: 預訂東京酒店',
            '已完成: 機票已訂 (ANA NH919)',
            '待處理: 選擇酒店 + 安排接機',
        ], '當前任務狀態'),
    ]

    col_w = 185
    gap = 10
    total = len(types) * col_w + (len(types) - 1) * gap
    start_x = (W - total) / 2

    for i, (name, eng, examples, desc) in enumerate(types):
        x = start_x + i * (col_w + gap)

        # Header
        s.rect(x, 65, col_w, 55, fill='medium')
        s.text(x + col_w / 2, 82, name, size=FS_BODY, bold=True)
        s.text(x + col_w / 2, 105, eng, size=FS_TINY, fill='text_light')

        # Examples
        ex_h = len(examples) * 20 + 20
        s.rect(x, 130, col_w, ex_h, fill='code_bg', stroke='dark', rx=4)
        for j, ex in enumerate(examples):
            s.mono(x + 8, 148 + j * 20, ex, size=FS_TINY - 2)

        # Description
        s.text(x + col_w / 2, 130 + ex_h + 18, desc, size=FS_TINY, fill='text_light')

    # Interaction arrows between working memory and long-term types
    arrow_y = 280
    wm_x = start_x + 3 * (col_w + gap) + col_w / 2

    for i in range(3):
        lt_x = start_x + i * (col_w + gap) + col_w / 2
        s.arrow_curved(wm_x - 20, arrow_y, lt_x + 20, arrow_y, curve=-30, dash=True, color='dark')

    s.text(410, arrow_y - 10, '工作記憶 ↔ 長期記憶 動態互動', size=FS_SMALL, fill='text_light')

    # Memory compression section (below)
    comp_y = 310
    s.rect(40, comp_y, 740, 110, fill='light')
    s.text(60, comp_y + 22, '記憶壓縮與整理', size=FS_BODY, bold=True, anchor='start')

    comp_stages = [
        ('重要性評分', ['訪問頻率 × 時間衰減', '× 情感強度 × 獨特性']),
        ('聚類壓縮', ['相似記憶分組', '→ 生成代表性摘要']),
        ('抽象泛化', ['情景記憶 → 語義記憶', '具體事件 → 一般規律']),
    ]

    stage_w = 220
    stage_gap = 15
    sx = 60
    for j, (title, desc_lines) in enumerate(comp_stages):
        cx = sx + j * (stage_w + stage_gap)
        s.rect(cx, comp_y + 45, stage_w, 55, fill='code_bg', stroke='dark', rx=4)
        s.text(cx + stage_w / 2, comp_y + 62, title, size=FS_SMALL, bold=True)
        for k, dl in enumerate(desc_lines):
            s.text(cx + stage_w / 2, comp_y + 78 + k * 15, dl, size=FS_TINY, fill='text_light')
        if j > 0:
            s.arrow(cx - stage_gap + 2, comp_y + 72, cx - 2, comp_y + 72, color='dark')

    # Privacy section
    priv_y = comp_y + 125
    s.rect(40, priv_y, 740, 90, fill='#e8e8e8')
    s.text(60, priv_y + 20, '隱私保護：分級資訊儲存', size=FS_BODY, bold=True, anchor='start')

    levels = [
        ('L1 公開', '姓名、郵箱', '明文'),
        ('L2 內部', '電話、地址', '部分掩碼'),
        ('L3 機密', '身份證、密碼', '佔位符替換'),
    ]

    lev_w = 230
    for j, (level, info, strategy) in enumerate(levels):
        lx = 55 + j * (lev_w + 10)
        s.rect(lx, priv_y + 38, lev_w, 40, fill='code_bg', stroke='dark', rx=4)
        s.text(lx + 8, priv_y + 58, f'{level}: {info} → {strategy}', size=FS_TINY, anchor='start')

    s.save(f'{OUT}/fig2-11.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-9: Memory Strategy Comparison (NEW — Exp 2.10)
# ════════════════════════════════════════════════════════════════════

def fig2_9_memory_comparison():
    """4 memory modes showing how the same info is stored differently."""
    W, H = 820, 620
    s = SVG(W, H)

    s.text(410, 30, '實驗 2.10：四種記憶策略對比', size=FS_TITLE, bold=True)

    # Input conversation example
    s.rect(40, 60, 740, 55, fill='light')
    s.text(50, 78, '原始對話:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(50, 98, '"我在 TechCorp 做高階工程師，帶5人團隊做推薦系統，用 ML 三年了"', size=FS_TINY)

    strategies = [
        ('Simple Notes', '原子化事實', [
            '"使用者公司: TechCorp"',
            '"使用者職位: 高階工程師"',
            '"使用者團隊: 5人"',
            '"使用者專長: 推薦系統"',
        ], '優點: O(1) 操作，極低開銷\n缺點: 關聯性完全丟失'),
        ('Enhanced Notes', '完整段落', [
            '"使用者在 TechCorp 擔任高階',
            '軟體工程師，專注 ML 三年,',
            '目前領導5人團隊負責推薦',
            '系統專案。"',
        ], '優點: 語義完整性\n缺點: 冗餘 + 更新複雜'),
        ('JSON Cards', '層次結構', [
            'work:',
            '  company: "TechCorp"',
            '  title: "高階工程師"',
            '  team_size: 5',
        ], '優點: 部分更新\n缺點: 剛性分類'),
        ('Adv. JSON Cards', '情境化知識', [
            '{category: "work",',
            ' title: "高階工程師",',
            ' backstory: "自我介紹",',
            ' ts: "09-14"}',
        ], '優點: 消歧 + 溯源\n缺點: 生成成本高'),
    ]

    col_w = 185
    gap = 10
    total = len(strategies) * col_w + (len(strategies) - 1) * gap
    start_x = (W - total) / 2

    for i, (name, approach, storage, tradeoff) in enumerate(strategies):
        x = start_x + i * (col_w + gap)

        # Header
        s.rect(x, 130, col_w, 50, fill='medium')
        s.text(x + col_w / 2, 148, name, size=FS_SMALL, bold=True)
        s.text(x + col_w / 2, 168, approach, size=FS_TINY, fill='text_light')

        # Arrow from input
        s.arrow(x + col_w / 2, 117, x + col_w / 2, 128, color='dark')

        # Storage representation
        storage_h = len(storage) * 18 + 16
        s.rect(x, 190, col_w, storage_h, fill='code_bg', stroke='dark', rx=4)
        for j, line in enumerate(storage):
            s.mono(x + 8, 205 + j * 18, line, size=FS_TINY - 2)

        # Tradeoff
        tradeoff_lines = tradeoff.split('\n')
        for j, tl in enumerate(tradeoff_lines):
            s.text(x + col_w / 2, 200 + storage_h + 18 + j * 18, tl, size=FS_TINY, fill='text_light')

    # Evaluation framework (bottom)
    eval_y = 420
    s.rect(40, eval_y, 740, 180, fill='light')
    s.text(60, eval_y + 22, '三層次評估框架', size=FS_BODY, bold=True, anchor='start')

    eval_levels = [
        ('第一層：基礎回憶', '儲存和檢索直接資訊', '"我的會員號是12345" → 精確返回', 'light'),
        ('第二層：多會話檢索', '跨會話關聯推理', '"為我的車預約保養" → 找出兩輛車', '#e8e8e8'),
        ('第三層：主動服務', '綜合多記憶，預見性幫助', '訂國際航班→發現護照即將過期', 'medium'),
    ]

    for i, (level, desc, example, fill) in enumerate(eval_levels):
        ey = eval_y + 45 + i * 45
        s.rect(60, ey, 180, 38, fill=fill, rx=4)
        s.text(150, ey + 19, level, size=FS_SMALL, bold=True)
        s.text(252, ey + 12, desc, size=FS_TINY, anchor='start')
        s.mono(252, ey + 29, example, size=FS_TINY - 2, anchor='start')

    s.save(f'{OUT}/fig2-9.svg')


# ════════════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    fig2_1()
    fig2_2()
    fig2_3()
    fig2_4()
    fig2_5()
    fig2_6()
    fig2_7()
    fig2_8()
    fig2_9_memory_comparison()
    print("Chapter 2: 9 figures generated.")
