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
  old fig2-4: Prompt结构化 (text code examples already show this)
  old fig2-8: 工作记忆→长期记忆 (text explains clearly)
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

    s.text(410, 30, '上下文窗口的构成概览', size=FS_TITLE, bold=True)

    lx, lw = 40, 700
    layers = [
        ('系统提示词（System Prompt）', 'medium', [
            '"You are a helpful assistant. You MUST answer concisely."',
            '"Use tools when the user asks for real-time information."',
        ]),
        ('工具定义（Tool Definitions）', 'light', [
            '{"name": "web_search", "description": "Search the web",',
            ' "parameters": {"query": {"type": "string"}}}',
        ]),
        ('对话历史（Conversation History）', 'light', [
            'user: "北京今天天气怎么样？"',
            'assistant: [tool_call] → get_weather("北京")',
            'tool: {"temp": "23°C", "conditions": "晴"}',
        ]),
        ('推理轨迹（Reasoning Trace）', '#e8e8e8', [
            '<think>用户问天气，我已经获得了工具结果，',
            '可以直接汇总回答，无需再调用工具。</think>',
        ]),
        ('当前生成位置 →', 'white', [
            'assistant: "北京今天晴，气温 23°C..."  ← LLM 正在生成',
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
    s.text(lx + lw + 15, (brace_top + brace_bot) / 2 + 12, '窗口', size=FS_BODY, bold=True, anchor='start')

    # Bottom annotation
    s.rect(100, y + 15, 620, 50, fill='code_bg', stroke='dark', rx=4)
    s.text(410, y + 32, '窗口大小：Qwen3 = 32K tokens | Claude = 200K | Gemini = 2M', size=FS_SMALL)
    s.text(410, y + 52, '所有内容序列化为 token 流 → Transformer 注意力机制处理', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-1.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-2: Local LLM Tool Calling Architecture (NEW — Exp 2.1)
# ════════════════════════════════════════════════════════════════════

def fig2_2():
    """Qwen3-0.6B on local hardware + tool registry + ReAct loop."""
    W, H = 820, 540
    s = SVG(W, H)

    s.text(410, 30, '实验 2.1：本地 LLM 工具调用架构', size=FS_TITLE, bold=True)

    # Hardware box (left)
    s.group_box(30, 65, 220, 130, '本地硬件')
    s.box(50, 100, 180, 35, 'Apple M2 / 16GB', fill='light', font_size=FS_SMALL)
    s.box(50, 145, 180, 35, 'MLX 推理后端', fill='light', font_size=FS_SMALL)

    # Model box (center)
    s.rect(290, 65, 240, 130, fill='medium')
    s.text(410, 95, 'Qwen3-0.6B', size=FS_BODY, bold=True)
    s.text(410, 120, '0.6B 参数 · Q4 量化', size=FS_SMALL, fill='text_light')
    s.text(410, 145, '> 100 tokens/s', size=FS_SMALL, fill='text_light')
    s.text(410, 170, 'ReAct + 工具调用能力', size=FS_SMALL)

    # Tool registry (right)
    s.group_box(570, 65, 220, 130, '工具注册表')
    s.box(590, 100, 180, 35, 'get_current_time', fill='code_bg', font_size=FS_SMALL)
    s.box(590, 145, 180, 35, 'get_temperature', fill='code_bg', font_size=FS_SMALL)

    # Arrows hardware → model, model ↔ tools
    s.arrow(252, 130, 288, 130)
    s.arrow(532, 122, 568, 122)
    s.arrow(568, 138, 532, 138)

    # ReAct loop (below)
    s.group_box(50, 220, 720, 290, 'ReAct 循环')

    # Step 1: User query
    s.rect(80, 260, 300, 40, fill='light')
    s.text(90, 280, 'user: "What\'s the time and weather in Vancouver?"', size=FS_TINY, anchor='start')

    # Step 2: Think
    s.rect(80, 310, 300, 55, fill='#e8e8e8')
    s.text(90, 328, '<think>', size=FS_TINY, anchor='start', bold=True)
    s.text(90, 348, '需要调用 get_current_time', size=FS_TINY, anchor='start')
    s.text(90, 363, '和 get_temperature 两个工具', size=FS_TINY, anchor='start')
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
    # 循环箭头改走左侧外缘，避免遮挡左列内的文本
    s.arrow_curved(80, 455, 80, 280, curve=-40, color='dark')
    s.text(30, 367, '继续循环', size=FS_TINY, fill='text_light', bold=True)

    # Final output box
    s.rect(430, 280, 320, 55, fill='medium')
    s.text(440, 298, '最终输出:', size=FS_SMALL, bold=True, anchor='start')
    s.text(440, 318, '"Vancouver: 05:18 AM, 13.2°C,', size=FS_TINY, anchor='start')
    s.text(440, 335, '  clear sky, humidity 93%"', size=FS_TINY, anchor='start')

    # Streaming annotation
    s.rect(430, 360, 320, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(590, 378, '流式处理关键时序', size=FS_SMALL, bold=True)
    s.text(440, 400, '<think>...  → 隐藏，不显示给用户', size=FS_TINY, anchor='start')
    s.text(440, 418, '普通文本    → 实时流式展示', size=FS_TINY, anchor='start')
    s.text(440, 436, '<tool_call> → 解析并执行工具', size=FS_TINY, anchor='start')

    s.save(f'{OUT}/fig2-2.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-3: Chat Template Token Structure (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_3():
    """Chat template token structure with actual token content and larger fonts."""
    W, H = 920, 580
    s = SVG(W, H)

    s.text(W / 2, 30, 'Chat Template 的 Token 结构', size=FS_TITLE, bold=True)

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
            '"北京今天天气怎么样？"',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '<think>需要查询天气，调用 get_weather 工具</think>',
            '<tool_call>{"name":"get_weather","args":{"city":"北京"}}</tool_call>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>user', 'darker', 'white', [
            '<tool_response>{"temp":"23°C","sky":"晴"}</tool_response>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '← LLM 从这里开始生成新 token',
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
    s.text(lx + rw + 5, 100, '标记', size=FS_SMALL, anchor='start', bold=True)

    s.save(f'{OUT}/fig2-3.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-4: KV Cache Prefix Reuse (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_4():
    """KV Cache with concrete token sequences showing prefix reuse."""
    W, H = 820, 480
    s = SVG(W, H)

    s.text(410, 30, 'KV Cache 前缀复用机制', size=FS_TITLE, bold=True)

    lx = 40
    bw = 740

    # Request 1
    s.text(lx, 70, '请求 1', size=FS_BODY, bold=True, anchor='start')
    # System prompt portion (cached)
    s.rect(lx, 85, 380, 40, fill='medium')
    s.text(lx + 190, 105, 'System Prompt + Tools (1200 tokens)', size=FS_SMALL)
    # User message
    s.rect(lx + 385, 85, 180, 40, fill='light')
    s.text(lx + 475, 105, 'user: "天气如何？"', size=FS_SMALL)
    # KV computed
    s.rect(lx + 570, 85, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 105, '→ 生成回答', size=FS_SMALL)

    # Request 2 (cache hit)
    s.text(lx, 155, '请求 2', size=FS_BODY, bold=True, anchor='start')
    # Same prefix — cached
    s.rect(lx, 170, 380, 40, fill='medium')
    s.text(lx + 190, 190, 'System Prompt + Tools（缓存命中 ✓）', size=FS_SMALL)
    # Different user msg
    s.rect(lx + 385, 170, 180, 40, fill='light')
    s.text(lx + 475, 190, 'user: "时间几点？"', size=FS_SMALL)
    s.rect(lx + 570, 170, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 190, '→ 生成回答', size=FS_SMALL)

    # Cache reuse arrow
    s.arrow(lx + 190, 127, lx + 190, 168, label='KV 复用', color='dark')

    # Request 3 (cache miss)
    s.text(lx, 245, '请求 3', size=FS_BODY, bold=True, anchor='start')
    s.text(lx + 85, 245, '（系统提示变了）', size=FS_SMALL, anchor='start', fill='text_light')
    s.rect(lx, 260, 400, 40, fill='white', dash=True)
    s.text(lx + 200, 280, 'System + Tools + "Time: 10:30:45"', size=FS_SMALL)
    s.rect(lx + 405, 260, 160, 40, fill='light')
    s.text(lx + 485, 280, 'user: "天气如何？"', size=FS_SMALL)
    s.rect(lx + 570, 260, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 280, '→ 全部重算 ✗', size=FS_SMALL)

    # Performance comparison
    s.rect(80, 330, 660, 130, fill='code_bg', stroke='dark', rx=4)
    s.text(410, 355, '性能对比（3000 token 上下文）', size=FS_BODY, bold=True)

    # Table header
    s.line(100, 370, 720, 370, color='dark')
    s.text(230, 390, '缓存命中', size=FS_SMALL, bold=True)
    s.text(490, 390, '缓存失效', size=FS_SMALL, bold=True)
    s.line(100, 405, 720, 405, color='dark')

    # Rows
    s.text(130, 425, 'TTFT', size=FS_SMALL, anchor='start')
    s.text(230, 425, '~0.5 秒', size=FS_SMALL)
    s.text(490, 425, '3 - 5 秒', size=FS_SMALL)

    s.text(130, 450, '成本', size=FS_SMALL, anchor='start')
    s.text(230, 450, '仅新 token 计费', size=FS_SMALL)
    s.text(490, 450, '全部 token 重新计费', size=FS_SMALL)

    s.save(f'{OUT}/fig2-4.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-5: Agent 状态栏 Injection Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_5():
    """Show WHERE hints are inserted with actual hint text."""
    W, H = 820, 580
    s = SVG(W, H)

    s.text(410, 30, '系统提示注入架构', size=FS_TITLE, bold=True)

    # Left: WITHOUT hints
    col_w = 350
    col_gap = 70
    lx1 = 30
    lx2 = lx1 + col_w + col_gap

    s.text(lx1 + col_w / 2, 65, '无系统提示', size=FS_BODY, bold=True)
    s.text(lx2 + col_w / 2, 65, '有系统提示', size=FS_BODY, bold=True)

    # Left column: raw trajectory
    y = 90
    left_items = [
        ('system', 'System Prompt + Tools', 'medium', 35),
        ('user', '"帮我联系 Xfinity 砍价"', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 1 次', '#e8e8e8', 35),
        ('tool', '结果: 等待 45 分钟, 未接通', 'light', 35),
        ('assistant', 'web_search("Xfinity deals")', '#e8e8e8', 35),
        ('tool', '结果: [大量搜索内容...]', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 2 次', '#e8e8e8', 35),
        ('tool', '结果: 接通，报价 $65/月', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 第 3 次', '#e8e8e8', 35),
        ('tool', '结果: 确认降价到 $59/月', 'light', 35),
        ('user', '"能不能再打一次催一下？"', 'light', 35),
    ]

    for role, content, fill, h in left_items:
        s.rect(lx1, y, col_w, h, fill=fill, rx=4)
        s.text(lx1 + 8, y + h / 2, f'{role}:', size=FS_TINY, anchor='start', bold=True)
        s.mono(lx1 + 65, y + h / 2, content, size=FS_TINY - 2)
        y += h + 3

    s.text(lx1 + col_w / 2, y + 15, '→ 模型需扫描全部上下文来"数"', size=FS_SMALL, fill='text_light')
    s.text(lx1 + col_w / 2, y + 35, '拨打了几次电话，容易数错', size=FS_SMALL, fill='text_light')

    # Right column: with system hints
    y = 90
    right_items = [
        ('system', 'System Prompt + Tools', 'medium', 35),
        ('user', '"帮我联系 Xfinity 砍价"', 'light', 35),
        ('...', '[ 同样的轨迹内容 ]', '#e8e8e8', 90),
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
        'phone_call 已调用 3 次 (Xfinity: 3)',
        '约束检查: 已达上限 (3/3) ✗',
        'TODO: [✓]联系Xfinity [✓]确认降价',
        '当前时间: 2025-09-14 10:30',
        '当前状态: 等待用户确认',
    ]
    for i, h in enumerate(hints):
        s.mono(lx2 + 15, hint_y + 40 + i * 20, h, size=FS_TINY - 2)
    s.text(lx2 + col_w - 10, hint_y + hint_h - 12, '</agent_status>', size=FS_SMALL, bold=True, anchor='end')

    s.text(lx2 + col_w / 2, hint_y + hint_h + 18, '→ 模型直接读取已提炼状态', size=FS_SMALL, fill='text_light')
    s.text(lx2 + col_w / 2, hint_y + hint_h + 38, '准确遵守约束，不再拨打', size=FS_SMALL, fill='text_light')

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

    s.text(410, 30, '上下文压缩策略对比（OpenAI 创始人追踪实验）', size=FS_TITLE, bold=True)

    # Table layout
    tx = 30
    tw = 760

    # Column positions
    cols = [
        (tx, 145, '策略'),
        (tx + 150, 90, 'Token 用量'),
        (tx + 250, 65, '压缩率'),
        (tx + 325, 55, '迭代次数'),
        (tx + 400, 65, '结果'),
        (tx + 475, 280, '可视化（Token 用量对比）'),
    ]

    header_y = 65
    for cx, cw, label in cols:
        s.text(cx + cw / 2, header_y, label, size=FS_SMALL, bold=True)

    s.line(tx, header_y + 12, tx + tw, header_y + 12)

    strategies = [
        ('无压缩', '> 110K', '100%', '5（失败）', False, 110000),
        ('个体摘要', '123,205', '6.8%', '24', True, 123205),
        ('组合摘要', '55,462', '2.1%', '21', True, 55462),
        ('上下文感知', '25,198', '0.9%', '15', True, 25198),
        ('感知+引用', '45,544', '1.4%', '17', True, 45544),
        ('自适应窗口', '181,372', '—', '8', True, 181372),
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
        result_text = '✓ 成功' if success else '✗ 失败'
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
    s.text(410, H - 45, '上下文感知压缩：token 减少 77%，成功率最高，迭代次数最少', size=FS_SMALL, bold=True)
    s.text(410, H - 25, '关键：将查询意图和已有信息纳入压缩决策', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-6.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-7: Context Compression Pipeline Variants (NEW — Exp 2.7)
# ════════════════════════════════════════════════════════════════════

def fig2_7():
    """6 compression strategies as pipeline variants."""
    W, H = 820, 600
    s = SVG(W, H)

    s.text(410, 30, '实验 2.7：六种压缩策略的处理流程', size=FS_TITLE, bold=True)

    # Input annotation
    s.text(410, 58, '每次搜索返回 ~70K 字符 → 各策略以不同方式处理', size=FS_SMALL, fill='text_light')

    strategies = [
        ('① 无压缩', '直接保留', '完整原文放入上下文', '> 110K tok → 溢出', False),
        ('② 个体摘要', '独立摘要', '每个结果独立生成 2-3 段摘要', '123K tok · 6.8%', True),
        ('③ 组合摘要', '合并摘要', '所有结果拼接后统一摘要', '55K tok · 2.1%', True),
        ('④ 上下文感知', '智能压缩', 'Given query + context → 针对性压缩', '25K tok · 0.9%', True),
        ('⑤ 感知+引用', '智能+溯源', '压缩内容 + 保留 URL 引用标记', '45K tok · 1.4%', True),
        ('⑥ 自适应窗口', '延迟压缩', '< 80% 窗口保留原文，超出批量压缩', '181K tok · 最大保真', True),
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

    s.text(410, 30, 'Skills 渐进式披露机制（PPTX Skill 示例）', size=FS_TITLE, bold=True)

    # Layer 1: Metadata (always loaded)
    y1 = 70
    s.rect(40, y1, 740, 90, fill='medium')
    s.text(60, y1 + 20, '第一层：元数据（启动时加载，~200 tokens）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y1 + 40, 700, 40, fill='code_bg', rx=4)
    s.mono(70, y1 + 60, 'skills: [{name: "PPTX", desc: "Create PowerPoint presentations from content"}', size=FS_TINY)
    s.mono(70, y1 + 75, '        {name: "PDF",  desc: "Extract and analyze PDF documents"}, ...]', size=FS_TINY - 2)

    # Trigger arrow
    s.arrow(410, y1 + 92, 410, y1 + 115)
    s.text(430, y1 + 103, '任务触发："从论文生成 PPT"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 2: Core SKILL.md
    y2 = y1 + 120
    s.rect(40, y2, 740, 130, fill='light')
    s.text(60, y2 + 20, '第二层：SKILL.md 核心流程（按需加载，~2K tokens）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y2 + 40, 700, 80, fill='code_bg', rx=4)
    lines2 = [
        'PPTX Skill 核心流程:',
        '1. markitdown 提取文本 → 2. 解压 PPTX 访问 XML',
        '3. 修改 slide{N}.xml 内容 → 4. 重新打包为 .pptx',
        '引用: → html2pptx.md | → reference.md | → scripts/',
    ]
    for i, line in enumerate(lines2):
        s.mono(70, y2 + 56 + i * 19, line, size=FS_TINY)

    # Trigger arrow
    s.arrow(410, y2 + 132, 410, y2 + 155)
    s.text(430, y2 + 143, '需要详细方法："用 HTML 模板创建 PPT"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 3: Sub-documents
    y3 = y2 + 160
    s.rect(40, y3, 740, 130, fill='white', dash=True)
    s.text(60, y3 + 20, '第三层：子文档（选择性深入，按需加载）', size=FS_BODY, bold=True, anchor='start')

    doc_w = 215
    docs = [
        ('html2pptx.md', 'HTML 模板 → PPT\n的完整工作流'),
        ('reference.md', 'XML 格式规范\n和技术细节'),
        ('scripts/*.py', '可执行工具:\nthumbnail.py 等'),
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
    s.text(410, y3 + 158, '元数据固定 → KV Cache 友好 | 动态内容追加 → 不破坏缓存', size=FS_SMALL)

    s.save(f'{OUT}/fig2-8.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-9: Mem0 Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_9():
    """Mem0 architecture with actual data flow and concrete memory examples."""
    W, H = 820, 530
    s = SVG(W, H)

    s.text(410, 30, 'Mem0 记忆管理架构', size=FS_TITLE, bold=True)

    # Input conversation
    s.rect(30, 70, 250, 80, fill='light')
    s.text(40, 88, '新对话输入:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 110, 'user: "我搬到深圳了,', size=FS_TINY)
    s.mono(40, 128, '新地址是南山区科技园"', size=FS_TINY)

    # MemoryBase (center)
    s.rect(310, 65, 200, 100, fill='medium')
    s.text(410, 85, 'MemoryBase', size=FS_BODY, bold=True)
    s.text(410, 108, '记忆生命周期管理', size=FS_SMALL, fill='text_light')
    s.text(410, 130, '分析 → 分类 → 决策', size=FS_SMALL, fill='text_light')
    s.arrow(282, 110, 308, 110)

    # LLMBase (above MemoryBase)
    s.rect(330, 185, 160, 50, fill='#e8e8e8')
    s.text(410, 203, 'LLMBase', size=FS_SMALL, bold=True)
    s.text(410, 222, '语义分析 + 关系判断', size=FS_TINY)
    s.arrow(410, 167, 410, 183, color='dark')
    s.arrow(410, 183, 410, 167, color='dark')

    # Decision output
    s.rect(310, 255, 200, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(320, 273, '决策结果:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(320, 293, '旧: "用户住北京海淀"', size=FS_TINY)
    s.mono(320, 311, '→ UPDATE: "住深圳南山"', size=FS_TINY)
    s.mono(320, 329, '→ ADD: "搬家到深圳"', size=FS_TINY - 2)
    s.arrow(410, 237, 410, 253, color='dark')

    # EmbeddingBase (right)
    s.rect(560, 70, 220, 70, fill='light')
    s.text(670, 90, 'EmbeddingBase', size=FS_SMALL, bold=True)
    s.text(670, 112, '文本 → 向量 (计算密集型)', size=FS_TINY, fill='text_light')
    s.arrow(512, 95, 558, 90)

    # VectorStoreBase (right, below)
    s.rect(560, 160, 220, 100, fill='light')
    s.text(670, 180, 'VectorStoreBase', size=FS_SMALL, bold=True)
    s.text(670, 200, '持久化 + 检索 (I/O密集)', size=FS_TINY, fill='text_light')
    s.text(670, 225, 'Chroma / Qdrant / Milvus', size=FS_TINY, fill='text_light')
    s.text(670, 248, '(HNSW / LSH 索引)', size=FS_TINY, fill='text_light')
    s.arrow(670, 142, 670, 158)

    # Stored memories example
    s.rect(560, 290, 220, 120, fill='code_bg', stroke='dark', rx=4)
    s.text(570, 310, '存储的记忆条目:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(570, 332, '"住深圳南山科技园"', size=FS_TINY)
    s.mono(570, 352, '"邮箱: john@x.com"', size=FS_TINY)
    s.mono(570, 372, '"偏好: 中文沟通"', size=FS_TINY)
    s.mono(570, 392, '"工作: ML 工程师"', size=FS_TINY)
    s.arrow(670, 262, 670, 288, color='dark')

    # Plugin mechanism note
    s.rect(30, 170, 250, 60, fill='code_bg', stroke='dark', rx=4)
    s.text(155, 192, '插件机制', size=FS_SMALL, bold=True)
    s.text(155, 212, '可替换 LLM / 嵌入模型 / 存储后端', size=FS_TINY, fill='text_light')

    # Retrieval path
    s.rect(30, 390, 250, 80, fill='light')
    s.text(40, 408, '记忆检索:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 430, 'query: "用户住哪里？"', size=FS_TINY)
    s.mono(40, 450, '→ 向量相似度匹配', size=FS_TINY)
    s.mono(40, 468, '→ "住深圳南山科技园"', size=FS_TINY)
    s.arrow_curved(282, 430, 558, 350, curve=-30, label='检索', color='dark')

    s.save(f'{OUT}/fig2-10.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-11: Memobase Multi-type Memory Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_11_memobase():
    """Memobase 4 memory types with concrete examples."""
    W, H = 820, 560
    s = SVG(W, H)

    s.text(410, 30, 'Memobase 多类型记忆架构', size=FS_TITLE, bold=True)

    types = [
        ('情景记忆', 'Episodic', [
            '2025-09-10 用户预订上海→东京',
            '2025-09-12 航班改签至 9/20',
            '2025-09-13 酒店变更为新宿店',
        ], '带时间戳的事件序列'),
        ('语义记忆', 'Semantic', [
            '用户 → 是 → ML 工程师',
            '用户 → 对花生过敏',
            '用户 → 偏好 → 靠窗座位',
        ], '实体-关系网络'),
        ('程序记忆', 'Procedural', [
            '旅行规划模式:',
            '  目的地→预算→交通→住宿→活动',
            '(从多次交互中自动提取)',
        ], '可复用策略模式'),
        ('工作记忆', 'Working', [
            '当前任务: 预订东京酒店',
            '已完成: 机票已订 (ANA NH919)',
            '待处理: 选择酒店 + 安排接机',
        ], '当前任务状态'),
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

    s.text(410, arrow_y - 10, '工作记忆 ↔ 长期记忆 动态交互', size=FS_SMALL, fill='text_light')

    # Memory compression section (below)
    comp_y = 310
    s.rect(40, comp_y, 740, 110, fill='light')
    s.text(60, comp_y + 22, '记忆压缩与整理', size=FS_BODY, bold=True, anchor='start')

    comp_stages = [
        ('重要性评分', ['访问频率 × 时间衰减', '× 情感强度 × 独特性']),
        ('聚类压缩', ['相似记忆分组', '→ 生成代表性摘要']),
        ('抽象泛化', ['情景记忆 → 语义记忆', '具体事件 → 一般规律']),
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
    s.text(60, priv_y + 20, '隐私保护：分级信息存储', size=FS_BODY, bold=True, anchor='start')

    levels = [
        ('L1 公开', '姓名、邮箱', '明文'),
        ('L2 内部', '电话、地址', '部分掩码'),
        ('L3 机密', '身份证、密码', '占位符替换'),
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

    s.text(410, 30, '实验 2.10：四种记忆策略对比', size=FS_TITLE, bold=True)

    # Input conversation example
    s.rect(40, 60, 740, 55, fill='light')
    s.text(50, 78, '原始对话:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(50, 98, '"我在 TechCorp 做高级工程师，带5人团队做推荐系统，用 ML 三年了"', size=FS_TINY)

    strategies = [
        ('Simple Notes', '原子化事实', [
            '"用户公司: TechCorp"',
            '"用户职位: 高级工程师"',
            '"用户团队: 5人"',
            '"用户专长: 推荐系统"',
        ], '优点: O(1) 操作，极低开销\n缺点: 关联性完全丢失'),
        ('Enhanced Notes', '完整段落', [
            '"用户在 TechCorp 担任高级',
            '软件工程师，专注 ML 三年,',
            '目前领导5人团队负责推荐',
            '系统项目。"',
        ], '优点: 语义完整性\n缺点: 冗余 + 更新复杂'),
        ('JSON Cards', '层次结构', [
            'work:',
            '  company: "TechCorp"',
            '  title: "高级工程师"',
            '  team_size: 5',
        ], '优点: 部分更新\n缺点: 刚性分类'),
        ('Adv. JSON Cards', '情境化知识', [
            '{category: "work",',
            ' title: "高级工程师",',
            ' backstory: "自我介绍",',
            ' ts: "09-14"}',
        ], '优点: 消歧 + 溯源\n缺点: 生成成本高'),
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
    s.text(60, eval_y + 22, '三层次评估框架', size=FS_BODY, bold=True, anchor='start')

    eval_levels = [
        ('第一层：基础回忆', '存储和检索直接信息', '"我的会员号是12345" → 精确返回', 'light'),
        ('第二层：多会话检索', '跨会话关联推理', '"为我的车预约保养" → 找出两辆车', '#e8e8e8'),
        ('第三层：主动服务', '综合多记忆，预见性帮助', '订国际航班→发现护照即将过期', 'medium'),
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
