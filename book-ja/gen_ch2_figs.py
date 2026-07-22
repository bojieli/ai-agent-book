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
  old fig2-4: Prompt structured (text code examples already show this)
  old fig2-8: Working memory → long-term memory (text explains clearly)
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

    s.text(410, 30, 'コンテキストウィンドウの構成概要', size=FS_TITLE, bold=True)

    lx, lw = 40, 700
    layers = [
        ('システムプロンプト', 'medium', [
            '"あなたは有能なアシスタントです。必ず簡潔に答えてください。"',
            '"ユーザーがリアルタイム情報を求めたらツールを使ってください。"',
        ]),
        ('ツール定義', 'light', [
            '{"name": "web_search", "description": "ウェブを検索",',
            ' "parameters": {"query": {"type": "string"}}}',
        ]),
        ('会話履歴', 'light', [
            'user: "今日の北京の天気は？"',
            'assistant: [tool_call] → get_weather("Beijing")',
            'tool: {"temp": "23°C", "conditions": "clear"}',
        ]),
        ('推論トレース', '#e8e8e8', [
            '<think>ユーザーは天気について尋ねています。すでにツールの結果があるので、',
            'ツールを再度呼び出さずに直接まとめて応答できます。</think>',
        ]),
        ('現在の生成位置 →', 'white', [
            'assistant: "北京は今日晴れ、気温23°C..."  ← LLM が生成中',
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
    s.text(lx + lw + 15, (brace_top + brace_bot) / 2 - 12, 'コンテキスト', size=FS_BODY, bold=True, anchor='start')
    s.text(lx + lw + 15, (brace_top + brace_bot) / 2 + 12, 'ウィンドウ', size=FS_BODY, bold=True, anchor='start')

    # Bottom annotation
    s.rect(100, y + 15, 620, 50, fill='code_bg', stroke='dark', rx=4)
    s.text(410, y + 32, 'ウィンドウサイズ: Qwen3 = 32K トークン | Claude = 200K | Gemini = 2M', size=FS_SMALL)
    s.text(410, y + 52, 'すべての内容がトークンストリームに直列化 → Transformer のアテンション機構で処理', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-1.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-2: Local LLM Tool Calling Architecture (NEW — Exp 2.1)
# ════════════════════════════════════════════════════════════════════

def fig2_2():
    """Qwen3-0.6B on local hardware + tool registry + ReAct loop."""
    W, H = 820, 540
    s = SVG(W, H)

    s.text(410, 30, '実験 2.1: ローカル LLM のツール呼び出しアーキテクチャ', size=FS_TITLE, bold=True)

    # Hardware box (left)
    s.group_box(30, 65, 220, 130, 'ローカルハードウェア')
    s.box(50, 100, 180, 35, 'Apple M2 / 16GB', fill='light', font_size=FS_SMALL)
    s.box(50, 145, 180, 35, 'MLX 推論バックエンド', fill='light', font_size=FS_SMALL)

    # Model box (center)
    s.rect(290, 65, 240, 130, fill='medium')
    s.text(410, 95, 'Qwen3-0.6B', size=FS_BODY, bold=True)
    s.text(410, 120, '0.6B パラメータ · Q4 量子化', size=FS_SMALL, fill='text_light')
    s.text(410, 145, '> 100 tokens/s', size=FS_SMALL, fill='text_light')
    s.text(410, 170, 'ReAct + ツール呼び出し機能', size=FS_SMALL)

    # Tool registry (right)
    s.group_box(570, 65, 220, 130, 'ツールレジストリ')
    s.box(590, 100, 180, 35, 'get_current_time', fill='code_bg', font_size=FS_SMALL)
    s.box(590, 145, 180, 35, 'get_temperature', fill='code_bg', font_size=FS_SMALL)

    # Arrows hardware → model, model ↔ tools
    s.arrow(252, 130, 288, 130)
    s.arrow(532, 122, 568, 122)
    s.arrow(568, 138, 532, 138)

    # ReAct loop (below)
    s.group_box(50, 220, 720, 290, 'ReAct ループ')

    # Step 1: User query
    s.rect(80, 260, 300, 40, fill='light')
    s.text(90, 280, 'user: "バンクーバーの時刻と天気は？"', size=FS_TINY, anchor='start')

    # Step 2: Think
    s.rect(80, 310, 300, 55, fill='#e8e8e8')
    s.text(90, 328, '<think>', size=FS_TINY, anchor='start', bold=True)
    s.text(90, 348, 'get_current_time と', size=FS_TINY, anchor='start')
    s.text(90, 363, 'get_temperature ツールを呼ぶ必要がある', size=FS_TINY, anchor='start')
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
    # Loop arrow goes along the left outer edge to avoid blocking text inside the left column
    s.arrow_curved(80, 455, 80, 280, curve=-40, color='dark')
    s.text(30, 367, 'ループ継続', size=FS_TINY, fill='text_light', bold=True)

    # Final output box
    s.rect(430, 280, 320, 55, fill='medium')
    s.text(440, 298, '最終出力:', size=FS_SMALL, bold=True, anchor='start')
    s.text(440, 318, '"バンクーバー: 午前05:18、13.2°C、', size=FS_TINY, anchor='start')
    s.text(440, 335, '  快晴、湿度93%"', size=FS_TINY, anchor='start')

    # Streaming annotation
    s.rect(430, 360, 320, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(590, 378, 'ストリーミングの主要タイミング', size=FS_SMALL, bold=True)
    s.text(440, 400, '<think>... → 非表示、ユーザーには見せない', size=FS_TINY, anchor='start')
    s.text(440, 418, 'プレーンテキスト → リアルタイムでストリーミング表示', size=FS_TINY, anchor='start')
    s.text(440, 436, '<tool_call> → ツールを解析して実行', size=FS_TINY, anchor='start')

    s.save(f'{OUT}/fig2-2.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-3: Chat Template Token Structure (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_3():
    """Chat template token structure with actual token content and larger fonts."""
    W, H = 920, 580
    s = SVG(W, H)

    s.text(W / 2, 30, 'チャットテンプレートのトークン構造', size=FS_TITLE, bold=True)

    lx = 40
    rw = 800

    y = 65
    segments = [
        ('<|im_start|>system', 'darker', 'white', [
            '# Tools',
            '1つ以上の関数を呼び出せます...',
            '<tools>{"name":"get_weather",...}</tools>',
            '<tool_call>{"name":..., "arguments":...}</tool_call>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>user', 'darker', 'white', [
            '"今日の北京の天気はどうですか？"',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '<think>天気を照会する必要がある、get_weather ツールを呼ぶ</think>',
            '<tool_call>{"name":"get_weather","args":{"city":"Beijing"}}</tool_call>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>user', 'darker', 'white', [
            '<tool_response>{"temp":"23°C","sky":"clear"}</tool_response>',
        ]),
        ('<|im_end|>', 'dark', 'white', []),
        ('<|im_start|>assistant', 'darker', 'white', [
            '← LLM はここから新しいトークンを生成し始める',
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
    s.text(lx + rw + 5, 100, 'トークン', size=FS_SMALL, anchor='start', bold=True)

    s.save(f'{OUT}/fig2-3.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-4: KV Cache Prefix Reuse (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_4():
    """KV Cache with concrete token sequences showing prefix reuse."""
    W, H = 820, 480
    s = SVG(W, H)

    s.text(410, 30, 'KV Cache のプレフィックス再利用の仕組み', size=FS_TITLE, bold=True)

    lx = 40
    bw = 740

    # Request 1
    s.text(lx, 70, 'リクエスト 1', size=FS_BODY, bold=True, anchor='start')
    # System prompt portion (cached)
    s.rect(lx, 85, 380, 40, fill='medium')
    s.text(lx + 190, 105, 'システムプロンプト + ツール（1200 トークン）', size=FS_SMALL)
    # User message
    s.rect(lx + 385, 85, 180, 40, fill='light')
    s.text(lx + 475, 105, 'user: "天気はどう？"', size=FS_SMALL)
    # KV computed
    s.rect(lx + 570, 85, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 105, '→ 応答を生成', size=FS_SMALL)

    # Request 2 (cache hit)
    s.text(lx, 155, 'リクエスト 2', size=FS_BODY, bold=True, anchor='start')
    # Same prefix — cached
    s.rect(lx, 170, 380, 40, fill='medium')
    s.text(lx + 190, 190, 'システムプロンプト + ツール（キャッシュヒット ✓）', size=FS_SMALL)
    # Different user msg
    s.rect(lx + 385, 170, 180, 40, fill='light')
    s.text(lx + 475, 190, 'user: "今何時？"', size=FS_SMALL)
    s.rect(lx + 570, 170, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 190, '→ 応答を生成', size=FS_SMALL)

    # Cache reuse arrow
    s.arrow(lx + 190, 127, lx + 190, 168, label='KV 再利用', color='dark')

    # Request 3 (cache miss)
    s.text(lx, 245, 'リクエスト 3', size=FS_BODY, bold=True, anchor='start')
    s.text(lx + 85, 245, '（システムプロンプトが変化）', size=FS_SMALL, anchor='start', fill='text_light')
    s.rect(lx, 260, 400, 40, fill='white', dash=True)
    s.text(lx + 200, 280, 'System + Tools + "Time: 10:30:45"', size=FS_SMALL)
    s.rect(lx + 405, 260, 160, 40, fill='light')
    s.text(lx + 485, 280, 'user: "天気はどう？"', size=FS_SMALL)
    s.rect(lx + 570, 260, 170, 40, fill='#e8e8e8')
    s.text(lx + 655, 280, '→ 全体を再計算 ✗', size=FS_SMALL)

    # Performance comparison
    s.rect(80, 330, 660, 130, fill='code_bg', stroke='dark', rx=4)
    s.text(410, 355, 'パフォーマンス比較（3000 トークンのコンテキスト）', size=FS_BODY, bold=True)

    # Table header
    s.line(100, 370, 720, 370, color='dark')
    s.text(230, 390, 'キャッシュヒット', size=FS_SMALL, bold=True)
    s.text(490, 390, 'キャッシュミス', size=FS_SMALL, bold=True)
    s.line(100, 405, 720, 405, color='dark')

    # Rows
    s.text(130, 425, 'TTFT', size=FS_SMALL, anchor='start')
    s.text(230, 425, '約0.5秒', size=FS_SMALL)
    s.text(490, 425, '3〜5秒', size=FS_SMALL)

    s.text(130, 450, 'コスト', size=FS_SMALL, anchor='start')
    s.text(230, 450, '新規トークンのみ課金', size=FS_SMALL)
    s.text(490, 450, '全トークンを再課金', size=FS_SMALL)

    s.save(f'{OUT}/fig2-4.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-5: Agent Status Bar Injection Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_5():
    """Show WHERE hints are inserted with actual hint text."""
    W, H = 820, 580
    s = SVG(W, H)

    s.text(410, 30, 'システムプロンプト注入アーキテクチャ', size=FS_TITLE, bold=True)

    # Left: WITHOUT hints
    col_w = 350
    col_gap = 70
    lx1 = 30
    lx2 = lx1 + col_w + col_gap

    s.text(lx1 + col_w / 2, 65, 'システムプロンプトなし', size=FS_BODY, bold=True)
    s.text(lx2 + col_w / 2, 65, 'システムプロンプトあり', size=FS_BODY, bold=True)

    # Left column: raw trajectory
    y = 90
    left_items = [
        ('system', 'システムプロンプト + ツール', 'medium', 35),
        ('user', '"Xfinity に連絡して交渉するのを手伝って"', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 1回目の試行', '#e8e8e8', 35),
        ('tool', '結果: 45分待ったがつながらず', 'light', 35),
        ('assistant', 'web_search("Xfinity deals")', '#e8e8e8', 35),
        ('tool', '結果: [大量の検索内容...]', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 2回目の試行', '#e8e8e8', 35),
        ('tool', '結果: つながった、月額$65を提示', 'light', 35),
        ('assistant', 'phone_call(Xfinity) → 3回目の試行', '#e8e8e8', 35),
        ('tool', '結果: 月額$59への値下げを確認', 'light', 35),
        ('user', '"もう一度電話してフォローしてくれる？"', 'light', 35),
    ]

    for role, content, fill, h in left_items:
        s.rect(lx1, y, col_w, h, fill=fill, rx=4)
        s.text(lx1 + 8, y + h / 2, f'{role}:', size=FS_TINY, anchor='start', bold=True)
        s.mono(lx1 + 65, y + h / 2, content, size=FS_TINY - 2)
        y += h + 3

    s.text(lx1 + col_w / 2, y + 15, '→ モデルは「数える」ためにコンテキスト全体を走査する必要がある', size=FS_SMALL, fill='text_light')
    s.text(lx1 + col_w / 2, y + 35, '呼び出し回数を数え間違えやすい', size=FS_SMALL, fill='text_light')

    # Right column: with system hints
    y = 90
    right_items = [
        ('system', 'システムプロンプト + ツール', 'medium', 35),
        ('user', '"Xfinity に連絡して交渉するのを手伝って"', 'light', 35),
        ('...', '[ 同じ軌跡の内容 ]', '#e8e8e8', 90),
        ('user', '"もう一度電話してフォローしてくれる？"', 'light', 35),
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
        'phone_call を3回呼び出し（Xfinity: 3）',
        '制約チェック: 上限到達（3/3）✗',
        'TODO: [✓]Xfinity に連絡 [✓]値下げを確認',
        '現在時刻: 2025-09-14 10:30',
        '現在の状態: ユーザーの確認待ち',
    ]
    for i, h in enumerate(hints):
        s.mono(lx2 + 15, hint_y + 40 + i * 20, h, size=FS_TINY - 2)
    s.text(lx2 + col_w - 10, hint_y + hint_h - 12, '</agent_status>', size=FS_SMALL, bold=True, anchor='end')

    s.text(lx2 + col_w / 2, hint_y + hint_h + 18, '→ モデルは整理された状態を直接読み取る', size=FS_SMALL, fill='text_light')
    s.text(lx2 + col_w / 2, hint_y + hint_h + 38, '制約を正確に守り、これ以上呼び出さない', size=FS_SMALL, fill='text_light')

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

    s.text(410, 30, 'コンテキスト圧縮戦略の比較（OpenAI 創業者追跡実験）', size=FS_TITLE, bold=True)

    # Table layout
    tx = 30
    tw = 760

    # Column header centers aligned to the data columns below (concise labels
    # so nothing overlaps in the narrow columns).
    header_y = 68
    headers = [
        (tx + 72, '戦略'),
        (tx + 195, 'トークン'),
        (tx + 282, '圧縮率'),
        (tx + 352, '反復'),
        (tx + 432, '結果'),
        (tx + 475 + 90, 'トークン使用量'),
    ]
    for cx, label in headers:
        s.text(cx, header_y, label, size=FS_SMALL, bold=True)

    s.line(tx, header_y + 12, tx + tw, header_y + 12)

    strategies = [
        ('圧縮なし', '> 110K', '100%', '5（失敗）', False, 110000),
        ('個別要約', '123,205', '6.8%', '24', True, 123205),
        ('統合要約', '55,462', '2.1%', '21', True, 55462),
        ('コンテキスト認識', '25,198', '0.9%', '15', True, 25198),
        ('認識 + 引用', '45,544', '1.4%', '17', True, 45544),
        ('適応ウィンドウ', '181,372', '—', '8', True, 181372),
    ]

    max_tokens = 190000
    bar_x = tx + 475
    bar_max_w = 280

    for i, (name, tokens, ratio, iters, success, token_val) in enumerate(strategies):
        y = header_y + 30 + i * 62

        # Strategy name
        s.text(tx + 72, y + 15, name, size=FS_SMALL, anchor='middle',
               bold=(name == 'コンテキスト認識'))

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
        bar_fill = '#e8e8e8' if name != 'コンテキスト認識' else 'medium'
        if not success:
            bar_fill = 'white'
        s.rect(bar_x, y, bar_w, 30, fill=bar_fill, stroke='border', rx=3)

    # Highlight best strategy
    best_y = header_y + 30 + 3 * 62 - 5
    s.rect(tx - 2, best_y, tw + 4, 42, fill='white', stroke='border', rx=4, dash=True)

    # Bottom insight
    s.rect(100, H - 60, 620, 45, fill='code_bg', stroke='dark', rx=4)
    s.text(410, H - 45, 'コンテキスト認識圧縮: トークン77%削減、最高の成功率、最少の反復回数', size=FS_SMALL, bold=True)
    s.text(410, H - 25, 'ポイント: クエリの意図と既存情報を圧縮判断に組み込む', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig2-6.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-7: Context Compression Pipeline Variants (NEW — Exp 2.7)
# ════════════════════════════════════════════════════════════════════

def fig2_7():
    """6 compression strategies as pipeline variants."""
    W, H = 820, 600
    s = SVG(W, H)

    s.text(410, 30, '実験 2.7: 6つの圧縮戦略の処理フロー', size=FS_TITLE, bold=True)

    # Input annotation
    s.text(410, 58, '各検索は約70K文字を返す → 各戦略が異なる方法で処理する', size=FS_SMALL, fill='text_light')

    strategies = [
        ('① 圧縮なし', 'そのまま保持', '原文全体をコンテキストへ', '> 110K tok → オーバーフロー', False),
        ('② 個別要約', '個別に要約', '各結果を独立に2〜3段落の要約にする', '123K tok · 6.8%', True),
        ('③ 統合要約', 'まとめて要約', '全結果を連結してから一括で要約', '55K tok · 2.1%', True),
        ('④ コンテキスト認識', 'インテリジェント圧縮', 'クエリ + コンテキストに基づき対象を絞って圧縮', '25K tok · 0.9%', True),
        ('⑤ 認識 + 引用', 'インテリジェント + 追跡可能性', '圧縮内容 + URL 引用マーカーを保持', '45K tok · 1.4%', True),
        ('⑥ 適応ウィンドウ', '圧縮を遅延', 'ウィンドウの80%未満は原文を保持、超えたら一括圧縮', '181K tok · 最大忠実度', True),
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

    s.text(410, 30, 'Skills の段階的開示メカニズム（PPTX Skill の例）', size=FS_TITLE, bold=True)

    # Layer 1: Metadata (always loaded)
    y1 = 70
    s.rect(40, y1, 740, 90, fill='medium')
    s.text(60, y1 + 20, 'レイヤー1: メタデータ（起動時に読み込み、約200トークン）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y1 + 40, 700, 40, fill='code_bg', rx=4)
    s.mono(70, y1 + 60, 'skills: [{name: "PPTX", desc: "コンテンツから PowerPoint プレゼンテーションを作成"}', size=FS_TINY)
    s.mono(70, y1 + 75, '        {name: "PDF",  desc: "PDF ドキュメントを抽出・分析"}, ...]', size=FS_TINY - 2)

    # Trigger arrow
    s.arrow(410, y1 + 92, 410, y1 + 115)
    s.text(430, y1 + 103, 'タスクトリガー: "論文から PPT を生成"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 2: Core SKILL.md
    y2 = y1 + 120
    s.rect(40, y2, 740, 130, fill='light')
    s.text(60, y2 + 20, 'レイヤー2: SKILL.md のコアフロー（オンデマンドで読み込み、約2Kトークン）', size=FS_BODY, bold=True, anchor='start')
    s.rect(60, y2 + 40, 700, 80, fill='code_bg', rx=4)
    lines2 = [
        'PPTX Skill のコアフロー:',
        '1. markitdown でテキストを抽出 → 2. PPTX を解凍して XML にアクセス',
        '3. slide{N}.xml の内容を修正 → 4. .pptx として再パッケージ',
        '参照: → html2pptx.md | → reference.md | → scripts/',
    ]
    for i, line in enumerate(lines2):
        s.mono(70, y2 + 56 + i * 19, line, size=FS_TINY)

    # Trigger arrow
    s.arrow(410, y2 + 132, 410, y2 + 155)
    s.text(430, y2 + 143, '詳細な手法が必要: "HTML テンプレートで PPT を作成"', size=FS_SMALL, anchor='start', fill='text_light')

    # Layer 3: Sub-documents
    y3 = y2 + 160
    s.rect(40, y3, 740, 130, fill='white', dash=True)
    s.text(60, y3 + 20, 'レイヤー3: サブドキュメント（選択的に深掘り、オンデマンドで読み込み）', size=FS_BODY, bold=True, anchor='start')

    doc_w = 215
    docs = [
        ('html2pptx.md', 'HTML テンプレート → PPT\n の完全なワークフロー'),
        ('reference.md', 'XML 形式の仕様\n と技術詳細'),
        ('scripts/*.py', '実行可能なツール:\nthumbnail.py など'),
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
    s.text(410, y3 + 158, '固定メタデータ → KV Cache に優しい | 動的内容は追記 → キャッシュを壊さない', size=FS_SMALL)

    s.save(f'{OUT}/fig2-8.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-9: Mem0 Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_9():
    """Mem0 architecture with actual data flow and concrete memory examples."""
    W, H = 820, 530
    s = SVG(W, H)

    s.text(410, 30, 'Mem0 のメモリ管理アーキテクチャ', size=FS_TITLE, bold=True)

    # Input conversation
    s.rect(30, 70, 250, 80, fill='light')
    s.text(40, 88, '新しい会話の入力:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 110, 'user: "深センに引っ越しました、', size=FS_TINY)
    s.mono(40, 128, '新しい住所は南山サイエンスパークです"', size=FS_TINY)

    # MemoryBase (center)
    s.rect(310, 65, 200, 100, fill='medium')
    s.text(410, 85, 'MemoryBase', size=FS_BODY, bold=True)
    s.text(410, 108, 'メモリのライフサイクル管理', size=FS_SMALL, fill='text_light')
    s.text(410, 130, '分析 → 分類 → 判断', size=FS_SMALL, fill='text_light')
    s.arrow(282, 110, 308, 110)

    # LLMBase (above MemoryBase)
    s.rect(330, 185, 160, 50, fill='#e8e8e8')
    s.text(410, 203, 'LLMBase', size=FS_SMALL, bold=True)
    s.text(410, 222, '意味解析 + 関係判定', size=FS_TINY)
    s.arrow(410, 167, 410, 183, color='dark')
    s.arrow(410, 183, 410, 167, color='dark')

    # Decision output
    s.rect(310, 255, 200, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(320, 273, '判断結果:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(320, 293, 'Old: "ユーザーは北京の海淀に住んでいる"', size=FS_TINY)
    s.mono(320, 311, '→ UPDATE: "深センの南山に住んでいる"', size=FS_TINY)
    s.mono(320, 329, '→ ADD: "深センに引っ越した"', size=FS_TINY - 2)
    s.arrow(410, 237, 410, 253, color='dark')

    # EmbeddingBase (right)
    s.rect(560, 70, 220, 70, fill='light')
    s.text(670, 90, 'EmbeddingBase', size=FS_SMALL, bold=True)
    s.text(670, 112, 'テキスト → ベクトル（計算集約的）', size=FS_TINY, fill='text_light')
    s.arrow(512, 95, 558, 90)

    # VectorStoreBase (right, below)
    s.rect(560, 160, 220, 100, fill='light')
    s.text(670, 180, 'VectorStoreBase', size=FS_SMALL, bold=True)
    s.text(670, 200, '永続化 + 検索（I/O集約的）', size=FS_TINY, fill='text_light')
    s.text(670, 225, 'Chroma / Qdrant / Milvus', size=FS_TINY, fill='text_light')
    s.text(670, 248, '(HNSW / LSH インデックス)', size=FS_TINY, fill='text_light')
    s.arrow(670, 142, 670, 158)

    # Stored memories example
    s.rect(560, 290, 220, 120, fill='code_bg', stroke='dark', rx=4)
    s.text(570, 310, '保存されたメモリエントリ:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(570, 332, '"深センの南山サイエンスパークに住んでいる"', size=FS_TINY)
    s.mono(570, 352, '"Email: john@x.com"', size=FS_TINY)
    s.mono(570, 372, '"好み: 中国語でのやり取り"', size=FS_TINY)
    s.mono(570, 392, '"職業: ML エンジニア"', size=FS_TINY)
    s.arrow(670, 262, 670, 288, color='dark')

    # Plugin mechanism note
    s.rect(30, 170, 250, 60, fill='code_bg', stroke='dark', rx=4)
    s.text(155, 192, 'プラグイン機構', size=FS_SMALL, bold=True)
    s.text(155, 212, 'LLM / 埋め込みモデル / ストレージバックエンドを差し替え可能', size=FS_TINY, fill='text_light')

    # Retrieval path
    s.rect(30, 390, 250, 80, fill='light')
    s.text(40, 408, 'メモリ検索:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(40, 430, 'query: "ユーザーはどこに住んでいる？"', size=FS_TINY)
    s.mono(40, 450, '→ ベクトル類似度マッチング', size=FS_TINY)
    s.mono(40, 468, '→ "深センの南山サイエンスパークに住んでいる"', size=FS_TINY)
    s.arrow_curved(282, 430, 558, 350, curve=-30, label='検索', color='dark')

    s.save(f'{OUT}/fig2-10.svg')


# ════════════════════════════════════════════════════════════════════
#  fig2-11: Memobase Multi-type Memory Architecture (reworked)
# ════════════════════════════════════════════════════════════════════

def fig2_11_memobase():
    """Memobase 4 memory types with concrete examples."""
    W, H = 820, 560
    s = SVG(W, H)

    s.text(410, 30, 'Memobase の多種メモリアーキテクチャ', size=FS_TITLE, bold=True)

    types = [
        ('エピソード記憶', 'Episodic', [
            '2025-09-10 ユーザーが上海→東京を予約',
            '2025-09-12 フライトを9/20に変更',
            '2025-09-13 ホテルを新宿店に変更',
        ], 'タイムスタンプ付きイベント列'),
        ('意味記憶', 'Semantic', [
            'ユーザー → 職業 → ML エンジニア',
            'ユーザー → ピーナッツアレルギー',
            'ユーザー → 好み → 窓側の席',
        ], 'エンティティ関係ネットワーク'),
        ('手続き記憶', 'Procedural', [
            '旅行計画のパターン:',
            '  目的地→予算→交通→宿泊→アクティビティ',
            '（複数のやり取りから自動抽出）',
        ], '再利用可能な戦略パターン'),
        ('ワーキングメモリ', 'Working', [
            '現在のタスク: 東京でホテルを予約',
            '完了: フライト予約済み（ANA NH919）',
            '保留: ホテル選択 + 空港送迎の手配',
        ], '現在のタスク状態'),
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

    s.text(410, arrow_y - 10, 'ワーキングメモリ ↔ 長期記憶の動的なやり取り', size=FS_SMALL, fill='text_light')

    # Memory compression section (below)
    comp_y = 310
    s.rect(40, comp_y, 740, 110, fill='light')
    s.text(60, comp_y + 22, 'メモリの圧縮と整理', size=FS_BODY, bold=True, anchor='start')

    comp_stages = [
        ('重要度スコアリング', ['アクセス頻度 × 時間減衰', '× 感情の強さ × 独自性']),
        ('クラスタリング圧縮', ['類似したメモリをグループ化', '→ 代表的な要約を生成']),
        ('抽象化と一般化', ['エピソード記憶 → 意味記憶', '具体的な出来事 → 一般的な規則']),
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
    s.text(60, priv_y + 20, 'プライバシー保護: 階層的な情報の保存', size=FS_BODY, bold=True, anchor='start')

    levels = [
        ('L1 公開', '氏名、メール', '平文'),
        ('L2 内部', '電話、住所', '部分マスキング'),
        ('L3 機密', 'ID番号、パスワード', 'プレースホルダー置換'),
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

    s.text(410, 30, '実験 2.10: 4つのメモリ戦略の比較', size=FS_TITLE, bold=True)

    # Input conversation example
    s.rect(40, 60, 740, 55, fill='light')
    s.text(50, 78, '元の対話:', size=FS_SMALL, bold=True, anchor='start')
    s.mono(50, 98, '"私は TechCorp のシニアエンジニアで、5人のチームを率いて推薦システムを構築しており、ML を3年間使っています"', size=FS_TINY)

    strategies = [
        ('シンプルノート', '原子的な事実', [
            '"ユーザーの会社: TechCorp"',
            '"ユーザーの役職: シニアエンジニア"',
            '"ユーザーのチーム: 5人"',
            '"ユーザーの専門: 推薦システム"',
        ], 'メリット: O(1)操作、極めて低いオーバーヘッド\nデメリット: 関連性が完全に失われる'),
        ('拡張ノート', '段落全体', [
            '"TechCorp のシニア',
            'エンジニア、5人のチームを',
            '率いて推薦システムを',
            '構築、ML歴3年"',
        ], 'メリット: 意味的な完全性\nデメリット: 冗長 + 更新が複雑'),
        ('JSON カード', '階層構造', [
            'work:',
            '  company: "TechCorp"',
            '  title: "Senior Engineer"',
            '  team_size: 5',
        ], 'メリット: 部分的な更新\nデメリット: 分類が硬直的'),
        ('高度な JSON カード', '文脈化された知識', [
            '{category: "work",',
            ' title: "Senior Engineer",',
            ' backstory: "Self-introduction",',
            ' ts: "09-14"}',
        ], 'メリット: 曖昧性の解消 + 追跡可能性\nデメリット: 生成コストが高い'),
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

        # Tradeoff (Pros/Cons) — wrapped so long lines don't collide with neighbours
        s.text_block(x + col_w / 2, 200 + storage_h + 6, col_w - 6,
                     tradeoff.split('\n'), size=FS_TINY, min_size=9, line_gap=1.25)

    # Evaluation framework (bottom)
    eval_y = 420
    s.rect(40, eval_y, 740, 180, fill='light')
    s.text(60, eval_y + 22, '3段階の評価フレームワーク', size=FS_BODY, bold=True, anchor='start')

    eval_levels = [
        ('レベル1: 基本的な想起', '直接的な情報の保存と取得', '"私の会員番号は12345" → 正確に返す', 'light'),
        ('レベル2: マルチセッション検索', 'セッションをまたぐ連想推論', '"私の車のメンテナンスを予約" → 2台の車を識別', '#e8e8e8'),
        ('レベル3: 能動的なサービス', '複数のメモリを統合し、先回りして支援', '国際線を予約 → パスポートの期限切れが近いことを発見', 'medium'),
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
