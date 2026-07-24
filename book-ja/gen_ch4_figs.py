#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 4 (Tools).

Figures (9 total):
  fig4-1:  MCP protocol sequence diagram (concrete message payloads)
  fig4-2:  Event-driven architecture (real event sources & payloads)
  fig4-3:  Async event processing (cancellation/queued/parallel timing)
  fig4-4:  Exp 4.4 — Event-driven agent architecture
  fig4-5:  Sync-async model contradiction (training vs deployment)
  fig4-6:  Exp 4.5 — Async agent with interruption
  fig4-7:  Tool discovery hierarchy (server→tool matching)
  fig4-8:  KV cache optimization (system prompt stability)
  fig4-9:  Context structure after dynamic tool discovery (schemas scattered in trajectory)
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


def _seq_msg(svg, x1, x2, y, label, note=None, dash=False, note_side='above'):
    """Draw a sequence diagram message arrow with label."""
    svg.arrow(x1, y, x2, y, dash=dash)
    mid = (x1 + x2) / 2
    if note_side == 'above':
        svg.text(mid, y - 12, label, size=FS_SMALL, bold=True)
    else:
        svg.text(mid, y + 18, label, size=FS_SMALL, bold=True)
    if note:
        ny = y + 18 if note_side == 'above' else y + 34
        svg.text(mid, ny, note, size=FS_TINY, fill='text_light')


# ──────────────────────── fig4-1 ────────────────────────

def fig4_1():
    """MCP protocol sequence diagram (concrete message payloads)"""
    w, h = 880, 620
    svg = SVG(w, h)
    svg.text(w / 2, 30, "MCP プロトコルのやり取りシーケンス", size=FS_TITLE, bold=True)

    cl_x, sv_x = 200, 680
    svg.box(cl_x - 80, 50, 160, 44, "MCP クライアント", fill='medium', bold=True)
    svg.box(sv_x - 80, 50, 160, 44, "MCP サーバー", fill='medium', bold=True)
    svg.line(cl_x, 94, cl_x, 600, color='dark', dash=True)
    svg.line(sv_x, 94, sv_x, 600, color='dark', dash=True)

    # 1 initialize
    y = 130
    svg.arrow(cl_x + 4, y, sv_x - 4, y)
    svg.text((cl_x + sv_x) / 2, y - 14, "initialize", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"method": "initialize",',
        ' "capabilities": {"tools": true}}',
    ], font_size=FS_TINY, line_h=18)

    # 2 initialize response
    y = 200
    svg.arrow(sv_x - 4, y, cl_x + 4, y, dash=True)
    svg.text((cl_x + sv_x) / 2, y - 14, "initialize レスポンス", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"serverInfo": {"name": "weather-server"},',
        ' "capabilities": {"tools": {"listChanged":true}}}',
    ], font_size=FS_TINY, line_h=18)

    # 3 tools/list
    y = 280
    svg.arrow(cl_x + 4, y, sv_x - 4, y)
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/list", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"method": "tools/list"}',
    ], font_size=FS_TINY, line_h=18)

    # 4 tools/list response
    y = 340
    svg.arrow(sv_x - 4, y, cl_x + 4, y, dash=True)
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/list レスポンス", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 10, y + 6, 400, [
        '{"tools": [{"name": "get_weather",',
        '  "inputSchema": {"city": "string"}}]}',
    ], font_size=FS_TINY, line_h=18)

    # 5 tools/call
    y = 420
    svg.arrow(cl_x + 4, y, sv_x - 4, y)
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/call", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"method": "tools/call",',
        ' "params": {"name": "get_weather",',
        '  "arguments": {"city": "Beijing"}}}',
    ], font_size=FS_TINY, line_h=18)

    # 6 tools/call response
    y = 510
    svg.arrow(sv_x - 4, y, cl_x + 4, y, dash=True)
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/call 結果", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"content": [{"type": "text",',
        '  "text": "Beijing: 22°C, sunny"}]}',
    ], font_size=FS_TINY, line_h=18)

    # Phase labels on the left
    svg.text(50, 165, "① ハンドシェイク", size=FS_SMALL, bold=True, fill='text_light')
    svg.text(50, 310, "② ディスカバリー", size=FS_SMALL, bold=True, fill='text_light')
    svg.text(50, 465, "③ 呼び出し", size=FS_SMALL, bold=True, fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-1.svg'))


# ──────────────────────── fig4-2 ────────────────────────

def fig4_2():
    """Event-driven architecture (specific event source and payload)"""
    w, h = 880, 540
    svg = SVG(w, h)
    svg.text(w / 2, 30, "イベント駆動型の非同期 Agent アーキテクチャ", size=FS_TITLE, bold=True)

    # Left: Event sources
    sources = [
        ("メール", 'on_email_reply', '{"from":"alice@...",\n "subject":"Re:meeting"}'),
        ("タイマー", 'on_timer_expire', '{"task_id":"daily_report",\n "scheduled":"09:00"}'),
        ("Webhook", 'on_webhook', '{"repo":"agent-lib",\n "event":"pr_merged"}'),
        ("ユーザー", 'on_user_message', '{"text":"Check tomorrow\'s weather for me\n"}'),
    ]

    src_x, src_w = 20, 155
    svg.text(src_x + src_w / 2, 65, "イベントソース", size=FS_BODY, bold=True)
    for i, (name, event_type, payload) in enumerate(sources):
        y = 85 + i * 110
        svg.box(src_x, y, src_w, 40, name, fill='medium', bold=True, font_size=FS_SMALL)
        svg.mono(src_x + 5, y + 56, event_type, size=FS_TINY)
        for j, pl in enumerate(payload.split('\n')):
            svg.mono(src_x + 5, y + 74 + j * 16, pl, size=11)

    # Middle: Event queue
    q_x, q_w = 215, 190
    svg.text(q_x + q_w / 2, 65, "イベントキュー", size=FS_BODY, bold=True)
    svg.rect(q_x, 85, q_w, 390, fill='white', stroke='border', dash=True)

    queue_events = [
        ("user.input", "優先度: 通常", 'light'),
        ("email.reply", "優先度: 通常", 'light'),
        ("user.interrupt", "優先度: 緊急！", 'dark'),
        ("timer.trigger", "優先度: 通常", 'light'),
    ]
    for i, (evt, pri, fill) in enumerate(queue_events):
        ey = 105 + i * 85
        svg.rect(q_x + 10, ey, q_w - 20, 60, fill=fill, rx=4)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(q_x + q_w / 2, ey + 22, evt, size=FS_SMALL, bold=True, fill=tc)
        svg.text(q_x + q_w / 2, ey + 44, pri, size=FS_TINY, fill='white' if fill == 'dark' else 'text_light')

    # Arrows from sources to queue
    for i in range(4):
        sy = 105 + i * 110
        svg.arrow(src_x + src_w + 2, sy, q_x - 2, 120 + i * 85)

    # Right: Agent processing
    ag_x = 450
    svg.text(ag_x + 200, 65, "Agent の処理フロー", size=FS_BODY, bold=True)

    svg.arrow(q_x + q_w + 2, 280, ag_x - 2, 280, label="イベント取得")

    steps = [
        ("ルーター", "LLM が緊急度を判定", 'medium'),
        ("トレースに追加", "構造化イベント形式", 'light'),
        ("LLM 推論", "観察 → 思考 → 実行", 'light'),
        ("ツール実行", "非同期/同期ディスパッチ", 'light'),
        ("結果処理", "通知/応答/保存", 'medium'),
    ]

    step_w, step_h = 360, 50
    for i, (title, desc, fill) in enumerate(steps):
        sy = 110 + i * 80
        svg.rect(ag_x, sy, step_w, step_h, fill=fill)
        svg.text(ag_x + 18, sy + step_h / 2, title, size=FS_SMALL, bold=True, anchor='start')
        svg.text(ag_x + step_w - 12, sy + step_h / 2, desc, size=FS_TINY, fill='text_light', anchor='end')
        if i < len(steps) - 1:
            svg.arrow(ag_x + step_w / 2, sy + step_h + 2, ag_x + step_w / 2, sy + 78)

    # Feedback loop
    svg.arrow_curved(ag_x + step_w, 450, ag_x + step_w, 130, curve=45, label="ループ", dash=True, color='dark')

    svg.save(os.path.join(OUT, 'fig4-2.svg'))


# ──────────────────────── fig4-3 ────────────────────────

def fig4_3():
    """Async event handling: timing comparison of three strategies"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "イベント処理の3つの戦略", size=FS_TITLE, bold=True)

    lane_x = 130
    lane_w = 720
    tl_x0 = lane_x + 10
    tl_w = lane_w - 20

    def time_bar(y, x_start_pct, x_end_pct, fill, label, h_bar=28):
        xs = tl_x0 + tl_w * x_start_pct
        xe = tl_x0 + tl_w * x_end_pct
        svg.rect(xs, y, xe - xs, h_bar, fill=fill, rx=4)
        svg.text((xs + xe) / 2, y + h_bar / 2, label, size=FS_TINY,
                 fill='white' if fill in ('dark', 'darker') else 'text')

    # Timeline header
    svg.text(tl_x0 + tl_w * 0.25, 55, "t₁", size=FS_SMALL, fill='text_light')
    svg.text(tl_x0 + tl_w * 0.50, 55, "t₂", size=FS_SMALL, fill='text_light')
    svg.text(tl_x0 + tl_w * 0.75, 55, "t₃", size=FS_SMALL, fill='text_light')

    # ── Lane 1: Cancellation ──
    y1 = 80
    svg.rect(lane_x, y1, lane_w, 140, fill='white', stroke='border', dash=True)
    svg.text(lane_x / 2, y1 + 70, "キャンセル", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y1 + 95, "（緊急）", size=FS_SMALL, fill='text_light')

    time_bar(y1 + 15, 0.0, 0.40, 'medium', 'LLM 推論中...')
    svg.line(tl_x0 + tl_w * 0.40, y1 + 10, tl_x0 + tl_w * 0.40, y1 + 130, color='border', dash=True)
    svg.text(tl_x0 + tl_w * 0.40, y1 + 10, "⚡ user.interrupt: \"停止！\"", size=FS_TINY, bold=True)
    time_bar(y1 + 15, 0.40, 0.45, 'dark', '×', h_bar=28)

    time_bar(y1 + 55, 0.0, 0.35, 'light', 'ツール実行中...')
    time_bar(y1 + 55, 0.40, 0.45, 'dark', '×', h_bar=28)

    time_bar(y1 + 95, 0.47, 1.0, 'medium', '新しい LLM 推論（割り込みイベントを含む + キューをクリア）')

    # ── Lane 2: Queued ──
    y2 = 240
    svg.rect(lane_x, y2, lane_w, 140, fill='white', stroke='border', dash=True)
    svg.text(lane_x / 2, y2 + 70, "キュー方式", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y2 + 95, "（通常）", size=FS_SMALL, fill='text_light')

    time_bar(y2 + 15, 0.0, 0.15, 'medium', 'LLM', h_bar=24)
    time_bar(y2 + 15, 0.18, 0.60, 'light', 'ツール実行（search_web）')
    time_bar(y2 + 15, 0.63, 0.90, 'medium', 'LLM による総合処理')

    svg.line(tl_x0 + tl_w * 0.35, y2 + 46, tl_x0 + tl_w * 0.35, y2 + 130, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * 0.35, y2 + 58, "user: \"直近1か月だけを見て\"", size=FS_TINY, fill='text_light')

    _pill(svg, tl_x0 + tl_w * 0.30, y2 + 65, 150, 24, "キューで待機", fill='light', font_size=FS_TINY)

    time_bar(y2 + 100, 0.63, 0.68, 'dark', '', h_bar=20)
    svg.text(tl_x0 + tl_w * 0.61, y2 + 110, "一括追加: tool.result + ユーザー入力", size=FS_TINY, fill='text_light', anchor='end')

    # ── Lane 3: Parallel ──
    y3 = 400
    svg.rect(lane_x, y3, lane_w, 140, fill='white', stroke='border', dash=True)
    svg.text(lane_x / 2, y3 + 70, "並列", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y3 + 95, "（独立）", size=FS_SMALL, fill='text_light')

    time_bar(y3 + 15, 0.0, 0.80, 'light', 'メインタスク: データ分析（長時間実行）')

    svg.line(tl_x0 + tl_w * 0.30, y3 + 50, tl_x0 + tl_w * 0.30, y3 + 130, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * 0.30, y3 + 58, "user: \"今日の天気は？\"", size=FS_TINY, fill='text_light')

    time_bar(y3 + 70, 0.32, 0.50, 'medium', '並列 LLM', h_bar=24)
    time_bar(y3 + 70, 0.52, 0.62, 'dark', '天気', h_bar=24)

    svg.text(tl_x0 + tl_w * 0.635, y3 + 82, "→ ユーザーへ即座に返信", size=FS_TINY, fill='text_light', anchor='start')
    svg.text(tl_x0 + tl_w * 0.50, y3 + 115, "タグ: [メインタスクと並列]", size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-3.svg'))


# ──────────────────────── fig4-4 ────────────────────────

def fig4_4():
    """Experiment 4.4: Event-driven Agent Architecture"""
    w, h = 880, 480
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 4.4: イベント駆動型 Agent アーキテクチャ", size=FS_TITLE, bold=True)

    # Event sources (left column)
    src_data = [
        ("on_user_message", "Web/App"),
        ("on_email_reply", "メールシステム"),
        ("on_github_pr_update", "GitHub"),
        ("on_timer_expire", "タイマー"),
        ("on_webhook_received", "Webhook"),
        ("on_resource_alert", "システムアラート"),
    ]
    svg.text(85, 65, "外部イベントソース", size=FS_BODY, bold=True)
    for i, (evt, src) in enumerate(src_data):
        y = 82 + i * 58
        svg.rect(10, y, 150, 44, fill='light')
        svg.text(85, y + 16, src, size=FS_SMALL, bold=True)
        svg.mono(15, y + 36, evt, size=11)

    # FastAPI Server (center)
    svg.rect(200, 80, 200, 390, fill='white', stroke='border', dash=True)
    svg.text(300, 100, "FastAPI サーバー", size=FS_BODY, bold=True)

    svg.rect(215, 120, 170, 50, fill='medium')
    svg.text(300, 137, "HTTP エンドポイント", size=FS_SMALL, bold=True)
    svg.text(300, 157, "POST /events/{type}", size=FS_TINY, fill='text_light')

    svg.rect(215, 190, 170, 50, fill='light')
    svg.text(300, 207, "イベントルーター", size=FS_SMALL, bold=True)
    svg.text(300, 227, "LLM が緊急度を判定", size=FS_TINY, fill='text_light')

    svg.rect(215, 260, 170, 50, fill='light')
    svg.text(300, 277, "イベントキュー", size=FS_SMALL, bold=True)
    svg.text(300, 297, "優先度によるソート", size=FS_TINY, fill='text_light')

    svg.rect(215, 330, 170, 50, fill='light')
    svg.text(300, 347, "Agent ループ", size=FS_SMALL, bold=True)
    svg.text(300, 367, "取得 → 推論 → 実行", size=FS_TINY, fill='text_light')

    svg.rect(215, 400, 170, 50, fill='medium')
    svg.text(300, 417, "セッション管理", size=FS_SMALL, bold=True)
    svg.text(300, 437, "マルチスレッドコンテキスト", size=FS_TINY, fill='text_light')

    for i in range(4):
        svg.arrow(300, 170 + i * 70, 300, 190 + i * 70)

    for i in range(6):
        svg.arrow(160, 104 + i * 58, 213, 145)

    # MCP Tools (right)
    svg.text(610, 65, "MCP ツールサーバー", size=FS_BODY, bold=True)

    tools = [
        ("知覚ツール", "search_web, read_file\nread_webpage, parse_image"),
        ("実行ツール", "code_interpreter\nvirtual_terminal, write_file"),
        ("協調ツール", "browser_use\nrequest_human_approval"),
        ("通知ツール", "send_email, send_slack\nsend_im_notification"),
    ]
    for i, (name, desc) in enumerate(tools):
        y = 82 + i * 100
        svg.rect(460, y, 250, 80, fill='light')
        svg.text(585, y + 22, name, size=FS_SMALL, bold=True)
        for j, line in enumerate(desc.split('\n')):
            svg.mono(470, y + 48 + j * 18, line, size=12)

    svg.arrow(400, 355, 458, 180)
    svg.arrow(458, 260, 400, 355)

    # Persistent store
    svg.rect(740, 82, 130, 380, fill='code_bg', stroke='dark', rx=4)
    svg.text(805, 115, "永続化レイヤー", size=FS_SMALL, bold=True)
    items = ["会話履歴", "イベントログ", "スケジュールタスク", "ツール状態", "監査証跡"]
    for i, item in enumerate(items):
        svg.text(805, 160 + i * 55, item, size=FS_SMALL)

    svg.save(os.path.join(OUT, 'fig4-4.svg'))


# ──────────────────────── fig4-5 ────────────────────────

def fig4_5():
    """sync-async model contradiction"""
    w, h = 880, 520
    svg = SVG(w, h)
    svg.text(w / 2, 30, "同期的な学習パラダイム vs 非同期なデプロイの現実", size=FS_TITLE, bold=True)

    # Top half: training pattern
    svg.rect(20, 55, w - 40, 195, fill='white', stroke='border', dash=True)
    svg.text(60, 78, "学習パラダイム（厳密に同期的なシーケンス）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 200, 64, 160, 28, "API の必須制約", fill='dark', font_size=FS_SMALL)

    steps_train = [
        ("観察", 'medium', "ユーザー: 北京の天気を確認"),
        ("思考", 'light', "天気ツールを呼び出す必要あり"),
        ("実行", 'medium', "get_weather(Beijing)"),
        ("観察", 'light', "22°C、晴れ"),
    ]
    bw, bh, gap = 180, 55, 22
    sx = (w - (4 * bw + 3 * gap)) / 2
    for i, (phase, fill, content) in enumerate(steps_train):
        x = sx + i * (bw + gap)
        svg.rect(x, 100, bw, bh, fill=fill)
        svg.text(x + bw / 2, 120, phase, size=FS_SMALL, bold=True)
        svg.text(x + bw / 2, 142, content, size=FS_TINY, fill='text_light')
        if i < 3:
            svg.arrow(x + bw + 2, 128, x + bw + gap - 2, 128)

    svg.rect(sx, 170, 4 * bw + 3 * gap, 30, fill='code_bg', stroke='dark', rx=4)
    svg.mono(sx + 10, 185,
             "tool_call → 次は必ず tool_result、そうでなければ API エラー", size=FS_TINY)

    # Separator
    svg.line(20, 262, w - 20, 262, color='dark', dash=True)
    svg.text(w / 2, 280, "矛盾", size=FS_BODY, bold=True, fill='darker')

    # Bottom half: async reality
    svg.rect(20, 295, w - 40, 210, fill='white', stroke='border', dash=True)
    svg.text(60, 318, "デプロイの現実（非同期イベントが交錯）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 200, 304, 160, 28, "フォーマット競合！", fill='dark', font_size=FS_SMALL)

    # Async timeline
    items = [
        ("アシスタント", 'medium', "tool_call:\nget_weather(Beijing)", 0.0, 0.20),
        ("待機中...", 'code_bg', "ツール実行 ~5s", 0.22, 0.50),
        ("ユーザーが割り込み", 'dark', "\"不要、\n上海のを確認\"", 0.40, 0.55),
        ("???", 'code_bg', "tool_result はいつ届く？ \nフォーマットをどう保証？", 0.57, 0.78),
        ("プレースホルダー", 'light', "[ツールはまだ実行中、 \n割り込みを優先]", 0.80, 1.0),
    ]

    tl_x0, tl_w = 50, w - 100
    for role, fill, txt, t0, t1 in items:
        x0 = tl_x0 + tl_w * t0
        x1 = tl_x0 + tl_w * t1
        svg.rect(x0, 340, x1 - x0, 50, fill=fill, rx=4)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text((x0 + x1) / 2, 355, role, size=FS_TINY, bold=True, fill=tc)
        for j, tl in enumerate(txt.split('\n')):
            svg.text((x0 + x1) / 2, 372 + j * 14, tl, size=11, fill=tc)

    svg.rect(50, 410, w - 100, 40, fill='code_bg', stroke='dark', rx=4)
    svg.mono(60, 430,
             "解決策: プレースホルダーでフォーマットを固定 + 非緊急イベントはキューに追加 + 本当に緊急なときだけ割り込み",
             size=FS_TINY)

    # Bottom insight
    svg.rect(140, 465, w - 280, 40, fill='dark')
    svg.text(w / 2, 485,
             "根本的な解決策: 次世代モデルは非同期環境で RL によって学習させる必要がある",
             size=FS_SMALL, fill='white', bold=True)

    svg.save(os.path.join(OUT, 'fig4-5.svg'))


# ──────────────────────── fig4-6 ────────────────────────

def fig4_6():
    """Experiment 4.5: Asynchronous Agent with Interruption Capability"""
    w, h = 880, 520
    svg = SVG(w, h)
    svg.text(w / 2, 30, "実験 4.5: 非同期 Agent の割り込みと復帰", size=FS_TITLE, bold=True)

    # Timeline
    tl_y, tl_h = 60, 440
    tl_x0, tl_w = 120, 740

    # Lanes
    lanes = [
        ("Agent", 80),
        ("ツール A", 180),
        ("ツール B", 260),
        ("ツール C", 340),
        ("軌跡", 420),
    ]
    for name, y in lanes:
        svg.text(55, y, name, size=FS_SMALL, bold=True)
        svg.line(tl_x0, y, tl_x0 + tl_w, y, color='dark', dash=True)

    def tbar(y, t0, t1, fill, label, h_bar=22):
        xs = tl_x0 + tl_w * t0
        xe = tl_x0 + tl_w * t1
        svg.rect(xs, y - h_bar / 2, xe - xs, h_bar, fill=fill, rx=3)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text((xs + xe) / 2, y, label, size=11, fill=tc)

    # Phase 1: Agent starts 3 tools
    tbar(80, 0.0, 0.12, 'medium', 'LLM: 3つのツールを起動')

    # Tools running
    tbar(180, 0.13, 0.45, 'light', 'スクリプト A: 毎秒3% → 33秒で完了')
    tbar(260, 0.13, 0.70, 'light', 'スクリプト B: 毎秒2% → 50秒...')
    tbar(340, 0.13, 0.90, 'code_bg', 'スクリプト C: 毎秒1% → 100秒...')

    # Event: tool A completes
    t_done = 0.45
    svg.line(tl_x0 + tl_w * t_done, 70, tl_x0 + tl_w * t_done, 450, color='border', dash=True)
    svg.text(tl_x0 + tl_w * t_done, 62, "A 完了", size=FS_TINY, bold=True)

    # Agent checks others
    tbar(80, 0.46, 0.58, 'medium', 'B、C の進捗を照会')
    tbar(420, 0.46, 0.58, 'light', 'B≈66% C≈33%')

    # Cancel C (< 50%)
    t_cancel = 0.60
    svg.line(tl_x0 + tl_w * t_cancel, 70, tl_x0 + tl_w * t_cancel, 450, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * t_cancel, 62, "C をキャンセル", size=FS_TINY, bold=True, fill='darker')

    tbar(340, 0.60, 0.65, 'dark', '×')

    # B finishes
    t_b_done = 0.70
    svg.line(tl_x0 + tl_w * t_b_done, 70, tl_x0 + tl_w * t_b_done, 450, color='border', dash=True)
    svg.text(tl_x0 + tl_w * t_b_done, 62, "B 完了", size=FS_TINY, bold=True)

    # Agent generates report
    tbar(80, 0.72, 0.95, 'medium', 'LLM: A+B の結果を統合してレポート生成')
    tbar(420, 0.72, 0.95, 'light', 'A の結果 + B の結果 + C のキャンセル記録')

    # Annotations
    svg.rect(tl_x0, 460, tl_w, 40, fill='code_bg', stroke='dark', rx=4)
    svg.mono(tl_x0 + 10, 480,
             "要点: プレースホルダー注入 + 非同期完了イベント + cancel_tool(task_id) API",
             size=FS_TINY)

    svg.save(os.path.join(OUT, 'fig4-6.svg'))


# ──────────────────────── fig4-7 ────────────────────────

def fig4_7():
    """Tool discovery hierarchy (server→tool matching)"""
    w, h = 880, 540
    svg = SVG(w, h)
    svg.text(w / 2, 30, "階層的なツールマッチング", size=FS_TITLE, bold=True)

    # Query at top
    svg.rect(250, 55, 380, 44, fill='medium')
    svg.text(440, 77, "Agent: \"GitHub リポジトリの貢献者統計を照会したい\"", size=FS_SMALL, bold=True)

    svg.arrow(440, 99, 440, 130)

    # discover_tools
    svg.rect(300, 132, 280, 44, fill='dark')
    svg.text(440, 154, "discover_tools(自然言語の要求)", size=FS_SMALL, fill='white', bold=True)

    svg.arrow(440, 176, 440, 210)

    # Layer 1: Server matching
    svg.rect(20, 210, w - 40, 110, fill='white', stroke='border', dash=True)
    svg.text(55, 233, "レイヤー1: サーバーマッチング（意味的類似度）", size=FS_BODY, bold=True, anchor='start')

    servers = [
        ("GitHub", 0.92, 'dark'),
        ("天気", 0.15, 'light'),
        ("金融", 0.23, 'light'),
        ("ArXiv", 0.18, 'light'),
        ("ファイルシステム", 0.31, 'light'),
    ]
    sx = 50
    for name, score, fill in servers:
        svg.rect(sx, 255, 145, 50, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(sx + 72, 272, name, size=FS_SMALL, bold=True, fill=tc)
        svg.text(sx + 72, 292, f"類似度: {score:.2f}", size=FS_TINY, fill='white' if fill == 'dark' else 'text_light')
        sx += 165

    # Arrow to layer 2
    svg.arrow(123, 305, 123, 345)
    svg.text(175, 330, "Top-1 サーバー", size=FS_SMALL, fill='text_light')

    # Layer 2: Tool matching within server
    svg.rect(20, 345, w - 40, 160, fill='white', stroke='border', dash=True)
    svg.text(55, 368, "レイヤー2: ツールマッチング（GitHub サーバー内の26ツール）", size=FS_BODY, bold=True, anchor='start')

    tools = [
        ("search_repositories", 0.41, "リポジトリ検索"),
        ("list_contributors", 0.89, "貢献者リスト"),
        ("get_repo_stats", 0.85, "リポジトリ統計"),
        ("create_issue", 0.12, "Issue 作成"),
        ("get_commit_history", 0.67, "コミット履歴"),
    ]
    tx = 30
    for name, score, desc in tools:
        is_top = score > 0.80
        fill = 'dark' if is_top else 'light'
        svg.rect(tx, 388, 155, 55, fill=fill)
        tc = 'white' if is_top else 'text'
        svg.mono(tx + 5, 406, name, size=11, fill=tc)
        svg.text(tx + 78, 428, f"{score:.2f} | {desc}", size=11, fill='white' if is_top else 'text_light')
        tx += 170

    # Bottom: result
    svg.rect(180, 468, 520, 30, fill='code_bg', stroke='dark', rx=4)
    svg.mono(190, 483, "Top-3 を返却: list_contributors, get_repo_stats, get_commit_history", size=12)

    svg.save(os.path.join(OUT, 'fig4-7.svg'))


# ──────────────────────── fig4-8 ────────────────────────

def fig4_8():
    """KV Cache Optimization (System Prompt Stability)"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "動的ツール読み込みのための KV Cache 最適化", size=FS_TITLE, bold=True)

    # Left: naive approach
    left_x = 30
    svg.text(220, 65, "素朴なアプローチ（キャッシュ無効化）", size=FS_BODY, bold=True)

    blocks_naive = [
        ("システムプロンプト", 120, 'medium', "あなたは AI アシスタントです...\n+ すべてのツールスキーマ", "~50K tokens"),
        ("ユーザーメッセージ", 100, 'light', "NVDA の株価を照会", ""),
        ("アシスタント", 80, 'light', "tool_call: ...", ""),
    ]
    ny = 85
    for label, bh, fill, content, note in blocks_naive:
        svg.rect(left_x, ny, 380, bh, fill=fill, rx=4)
        svg.text(left_x + 190, ny + 22, label, size=FS_SMALL, bold=True)
        for j, line in enumerate(content.split('\n')):
            svg.text(left_x + 190, ny + 44 + j * 20, line, size=FS_TINY, fill='text_light')
        if note:
            svg.text(left_x + 360, ny + 22, note, size=FS_TINY, fill='darker', anchor='end')
        ny += bh + 8

    svg.rect(left_x, ny + 5, 380, 40, fill='dark')
    svg.text(left_x + 190, ny + 25, "新しいツールを読み込むたびに → キャッシュ全体が無効化！", size=FS_SMALL, fill='white', bold=True)

    # Right: optimized approach
    right_x = 460
    svg.text(660, 65, "最適化アプローチ（キャッシュの安定性）", size=FS_BODY, bold=True)

    blocks_opt = [
        ("システムプロンプト（固定）", 75, 'medium',
         "あなたは AI アシスタントです...\n役割 + ルール + 基本ツール",
         "~2K tokens | KV Cache"),
        ("Agent ステータスバー（軽量）", 45, 'code_bg',
         "利用可能なツール: web_search, get_weather...",
         "~200 tokens"),
        ("ユーザー: discover_tools", 40, 'light',
         '"株価を確認したい"',
         ""),
        ("ツール結果", 55, 'light',
         "get_stock_quote スキーマを返却",
         "ここにツール定義"),
        ("ユーザーメッセージ", 40, 'light',
         "NVDA の株価を照会",
         ""),
        ("Agent ステータスバー（更新後）", 45, 'code_bg',
         "+get_stock_quote を追加",
         "~220 tokens"),
    ]
    oy = 85
    for label, bh, fill, content, note in blocks_opt:
        svg.rect(right_x, oy, 400, bh, fill=fill, rx=4)
        svg.text(right_x + 200, oy + 16, label, size=FS_SMALL, bold=True)
        for j, line in enumerate(content.split('\n')):
            svg.text(right_x + 200, oy + 32 + j * 16, line, size=FS_TINY, fill='text_light')
        if note:
            svg.text(right_x + 390, oy + 16, note, size=11, fill='darker', anchor='end')
        oy += bh + 5

    svg.rect(right_x, oy + 5, 400, 40, fill='medium')
    svg.text(right_x + 200, oy + 25, "システムプロンプト不変 → KV Cache を完全に再利用", size=FS_SMALL, bold=True)

    # Bottom comparison
    svg.line(30, 475, w - 30, 475, color='dark', dash=True)
    comps = [
        ("キャッシュヒット率", "~0%（ツール変更のたびに無効化）", "~95%（ヒントがわずかに変わるのみ）"),
        ("初回トークン遅延", "高い（毎回 50K トークンを再計算）", "低い（増分計算 ~200 トークン）"),
    ]
    cy = 495
    svg.text(250, cy, "比較の観点", size=FS_SMALL, bold=True)
    svg.text(500, cy, "素朴なアプローチ", size=FS_SMALL, bold=True)
    svg.text(740, cy, "最適化アプローチ", size=FS_SMALL, bold=True)
    for metric, naive, opt in comps:
        cy += 28
        svg.text(250, cy, metric, size=FS_TINY)
        svg.text(500, cy, naive, size=FS_TINY, fill='text_light')
        svg.text(740, cy, opt, size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-8.svg'))


# ──────────────────────── fig4-9 ────────────────────────

def fig4_9():
    """动态发现后的上下文结构：工具 schema 散落在轨迹各处"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "动态发现后的上下文结构：工具 schema 散落在轨迹各处", size=FS_TITLE, bold=True)

    col_x, col_w = 40, 520

    # 静态前缀组
    svg.rect(20, 50, col_w + 40, 118, fill='white', stroke='border', dash=True)
    svg.text(36, 72, "静态前缀（字节级不变，KV Cache 持续命中）", size=FS_SMALL, bold=True, anchor='start')
    svg.rect(col_x, 84, col_w, 34, fill='medium')
    svg.text(col_x + col_w / 2, 101, "System Prompt", size=FS_SMALL, bold=True)
    svg.rect(col_x, 124, col_w, 34, fill='medium')
    svg.text(col_x + col_w / 2, 141, "核心工具定义：web_search, code_interpreter, tool_search", size=FS_TINY, bold=True)

    # 轨迹组
    svg.rect(20, 180, col_w + 40, 386, fill='white', stroke='border', dash=True)
    svg.text(36, 202, "轨迹（只增不改，新内容追加在末尾）", size=FS_SMALL, bold=True, anchor='start')

    blocks = [
        ("User：查询 NVDA 股价", 'light', False),
        ("Assistant：tool_search_call(股价)", 'light', False),
        ("tool_search_output → 注入 get_stock_quote 完整 schema", '#d8e8d8', True),
        ("Assistant：调用 get_stock_quote → Tool Result", 'light', False),
        ("User：分析 GitHub 仓库的贡献者", 'light', False),
        ("Assistant：tool_search_call(GitHub)", 'light', False),
        ("tool_search_output → 注入 list_contributors 等 schema", '#d8e8d8', True),
        ("Assistant：调用 → Tool Result → 回复", 'light', False),
        ("…… 本轮最新内容", 'light', False),
    ]
    by = 214
    star_ys = []
    for label, fill, star in blocks:
        bh = 40 if star else 30
        svg.rect(col_x, by, col_w, bh, fill=fill)
        svg.text(col_x + col_w / 2, by + bh / 2, label, size=FS_TINY, bold=star)
        if star:
            star_ys.append(by + bh / 2)
        by += bh + 6

    # 右侧注释
    for sy in star_ys:
        svg.arrow(col_x + col_w + 2, sy, 592, sy, dash=True)
    svg.text(600, star_ys[0] - 12, "首次出现：prefill 一次（缓存写入）", size=FS_TINY, anchor='start', bold=True)
    svg.text(600, star_ys[0] + 10, "此后作为普通历史命中缓存", size=FS_TINY, anchor='start', fill='text_light')
    svg.text(600, star_ys[1] - 12, "不得移除/重排已加载工具", size=FS_TINY, anchor='start', bold=True)
    svg.text(600, star_ys[1] + 10, "否则缓存从变动点起失效", size=FS_TINY, anchor='start', fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-9.svg'))


# ──────────────────────── main ────────────────────────

def main():
    os.makedirs(OUT, exist_ok=True)
    figs = [
        fig4_1, fig4_2, fig4_3, fig4_4, fig4_5,
        fig4_6, fig4_7, fig4_8, fig4_9,
    ]
    for fn in figs:
        fn()
        print(f"  ✓ {fn.__name__}: {fn.__doc__}")
    print(f"\nGenerated {len(figs)} figures in {OUT}/")


if __name__ == '__main__':
    main()
