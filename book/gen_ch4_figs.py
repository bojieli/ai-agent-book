#!/usr/bin/env python3
"""Generate all SVG illustrations for Chapter 4 (工具).

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
    """MCP 协议时序图（具体消息载荷）"""
    w, h = 880, 620
    svg = SVG(w, h)
    svg.text(w / 2, 30, "MCP 协议交互时序", size=FS_TITLE, bold=True)

    cl_x, sv_x = 200, 680
    svg.box(cl_x - 80, 50, 160, 44, "MCP Client", fill='medium', bold=True)
    svg.box(sv_x - 80, 50, 160, 44, "MCP Server", fill='medium', bold=True)
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
    svg.text((cl_x + sv_x) / 2, y - 14, "initialize response", size=FS_BODY, bold=True)
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
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/list response", size=FS_BODY, bold=True)
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
    svg.text((cl_x + sv_x) / 2, y - 14, "tools/call result", size=FS_BODY, bold=True)
    svg.code_block(cl_x + 30, y + 6, 350, [
        '{"content": [{"type": "text",',
        '  "text": "Beijing: 22°C, sunny"}]}',
    ], font_size=FS_TINY, line_h=18)

    # Phase labels on the left
    svg.text(50, 165, "① 握手", size=FS_SMALL, bold=True, fill='text_light')
    svg.text(50, 310, "② 发现", size=FS_SMALL, bold=True, fill='text_light')
    svg.text(50, 465, "③ 调用", size=FS_SMALL, bold=True, fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-1.svg'))


# ──────────────────────── fig4-2 ────────────────────────

def fig4_2():
    """事件驱动架构（具体事件源和载荷）"""
    w, h = 880, 540
    svg = SVG(w, h)
    svg.text(w / 2, 30, "事件驱动的异步 Agent 架构", size=FS_TITLE, bold=True)

    # Left: Event sources
    sources = [
        ("Email", 'on_email_reply', '{"from":"alice@...",\n "subject":"Re:会议"}'),
        ("Timer", 'on_timer_expire', '{"task_id":"daily_report",\n "scheduled":"09:00"}'),
        ("Webhook", 'on_webhook', '{"repo":"agent-lib",\n "event":"pr_merged"}'),
        ("User", 'on_user_message', '{"text":"帮我查下\n 明天的天气"}'),
    ]

    src_x, src_w = 20, 155
    svg.text(src_x + src_w / 2, 65, "事件源", size=FS_BODY, bold=True)
    for i, (name, event_type, payload) in enumerate(sources):
        y = 85 + i * 110
        svg.box(src_x, y, src_w, 40, name, fill='medium', bold=True, font_size=FS_SMALL)
        svg.mono(src_x + 5, y + 56, event_type, size=FS_TINY)
        for j, pl in enumerate(payload.split('\n')):
            svg.mono(src_x + 5, y + 74 + j * 16, pl, size=11)

    # Middle: Event queue
    q_x, q_w = 215, 190
    svg.text(q_x + q_w / 2, 65, "事件队列", size=FS_BODY, bold=True)
    svg.rect(q_x, 85, q_w, 390, fill='white', stroke='border', dash=True)

    queue_events = [
        ("user.input", "优先级: 常规", 'light'),
        ("email.reply", "优先级: 常规", 'light'),
        ("user.interrupt", "优先级: 紧急!", 'dark'),
        ("timer.trigger", "优先级: 常规", 'light'),
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
    svg.text(ag_x + 200, 65, "Agent 处理流程", size=FS_BODY, bold=True)

    svg.arrow(q_x + q_w + 2, 280, ag_x - 2, 280, label="取出事件")

    steps = [
        ("路由器", "LLM 判定紧急度", 'medium'),
        ("追加到轨迹", "结构化事件格式", 'light'),
        ("LLM 推理", "观察→思考→行动", 'light'),
        ("工具执行", "异步/同步分派", 'light'),
        ("结果处理", "通知/响应/存储", 'medium'),
    ]

    step_w, step_h = 360, 50
    for i, (title, desc, fill) in enumerate(steps):
        sy = 110 + i * 80
        svg.rect(ag_x, sy, step_w, step_h, fill=fill)
        svg.text(ag_x + 90, sy + step_h / 2, title, size=FS_SMALL, bold=True, anchor='start')
        svg.text(ag_x + step_w - 10, sy + step_h / 2, desc, size=FS_TINY, fill='text_light', anchor='end')
        if i < len(steps) - 1:
            svg.arrow(ag_x + step_w / 2, sy + step_h + 2, ag_x + step_w / 2, sy + 78)

    # Feedback loop
    svg.arrow_curved(ag_x + step_w, 450, ag_x + step_w, 130, curve=-50, label="循环", dash=True, color='dark')

    svg.save(os.path.join(OUT, 'fig4-2.svg'))


# ──────────────────────── fig4-3 ────────────────────────

def fig4_3():
    """异步事件处理：三种策略时序对比"""
    w, h = 880, 580
    svg = SVG(w, h)
    svg.text(w / 2, 30, "事件处理的三种策略", size=FS_TITLE, bold=True)

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
    svg.text(lane_x / 2, y1 + 70, "取消式", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y1 + 95, "(紧急)", size=FS_SMALL, fill='text_light')

    time_bar(y1 + 15, 0.0, 0.40, 'medium', 'LLM 推理中...')
    svg.line(tl_x0 + tl_w * 0.40, y1 + 10, tl_x0 + tl_w * 0.40, y1 + 130, color='border', dash=True)
    svg.text(tl_x0 + tl_w * 0.40, y1 + 10, "⚡ user.interrupt: \"停止!\"", size=FS_TINY, bold=True)
    time_bar(y1 + 15, 0.40, 0.45, 'dark', '×', h_bar=28)

    time_bar(y1 + 55, 0.0, 0.35, 'light', '工具执行中...')
    time_bar(y1 + 55, 0.40, 0.45, 'dark', '×', h_bar=28)

    time_bar(y1 + 95, 0.47, 1.0, 'medium', '新 LLM 推理（含中断事件 + 清空队列）')

    # ── Lane 2: Queued ──
    y2 = 240
    svg.rect(lane_x, y2, lane_w, 140, fill='white', stroke='border', dash=True)
    svg.text(lane_x / 2, y2 + 70, "队列式", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y2 + 95, "(常规)", size=FS_SMALL, fill='text_light')

    time_bar(y2 + 15, 0.0, 0.15, 'medium', 'LLM', h_bar=24)
    time_bar(y2 + 15, 0.18, 0.60, 'light', '工具执行 (search_web)')
    time_bar(y2 + 15, 0.63, 0.90, 'medium', 'LLM 综合处理')

    svg.line(tl_x0 + tl_w * 0.35, y2 + 46, tl_x0 + tl_w * 0.35, y2 + 130, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * 0.35, y2 + 46, "user: \"只看最近1个月\"", size=FS_TINY, fill='text_light')

    _pill(svg, tl_x0 + tl_w * 0.30, y2 + 65, 150, 24, "入队等待", fill='light', font_size=FS_TINY)

    time_bar(y2 + 100, 0.63, 0.68, 'dark', '', h_bar=20)
    svg.text(tl_x0 + tl_w * 0.72, y2 + 110, "批量追加: tool.result + user补充", size=FS_TINY, fill='text_light')

    # ── Lane 3: Parallel ──
    y3 = 400
    svg.rect(lane_x, y3, lane_w, 140, fill='white', stroke='border', dash=True)
    svg.text(lane_x / 2, y3 + 70, "并行式", size=FS_BODY, bold=True)
    svg.text(lane_x / 2, y3 + 95, "(独立)", size=FS_SMALL, fill='text_light')

    time_bar(y3 + 15, 0.0, 0.80, 'light', '主任务: 数据分析 (长时间执行)')

    svg.line(tl_x0 + tl_w * 0.30, y3 + 50, tl_x0 + tl_w * 0.30, y3 + 130, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * 0.30, y3 + 50, "user: \"今天天气怎样?\"", size=FS_TINY, fill='text_light')

    time_bar(y3 + 70, 0.32, 0.50, 'medium', '并行 LLM', h_bar=24)
    time_bar(y3 + 70, 0.52, 0.62, 'dark', '天气', h_bar=24)

    svg.text(tl_x0 + tl_w * 0.66, y3 + 82, "→ 立即回复用户", size=FS_TINY, fill='text_light')
    svg.text(tl_x0 + tl_w * 0.50, y3 + 115, "标记: [与主任务并行]", size=FS_TINY, fill='text_light')

    svg.save(os.path.join(OUT, 'fig4-3.svg'))


# ──────────────────────── fig4-4 ────────────────────────

def fig4_4():
    """实验 4.4：事件驱动 Agent 架构"""
    w, h = 880, 480
    svg = SVG(w, h)
    svg.text(w / 2, 30, "实验 4.4：事件驱动 Agent 架构", size=FS_TITLE, bold=True)

    # Event sources (left column)
    src_data = [
        ("on_user_message", "Web/App"),
        ("on_email_reply", "邮件系统"),
        ("on_github_pr_update", "GitHub"),
        ("on_timer_expire", "定时器"),
        ("on_webhook_received", "Webhook"),
        ("on_resource_alert", "系统告警"),
    ]
    svg.text(85, 65, "外部事件源", size=FS_BODY, bold=True)
    for i, (evt, src) in enumerate(src_data):
        y = 82 + i * 58
        svg.rect(10, y, 150, 44, fill='light')
        svg.text(85, y + 16, src, size=FS_SMALL, bold=True)
        svg.mono(15, y + 36, evt, size=11)

    # FastAPI Server (center)
    svg.rect(200, 80, 200, 390, fill='white', stroke='border', dash=True)
    svg.text(300, 100, "FastAPI 服务器", size=FS_BODY, bold=True)

    svg.rect(215, 120, 170, 50, fill='medium')
    svg.text(300, 137, "HTTP 端点", size=FS_SMALL, bold=True)
    svg.text(300, 157, "POST /events/{type}", size=FS_TINY, fill='text_light')

    svg.rect(215, 190, 170, 50, fill='light')
    svg.text(300, 207, "事件路由器", size=FS_SMALL, bold=True)
    svg.text(300, 227, "LLM 判定紧急度", size=FS_TINY, fill='text_light')

    svg.rect(215, 260, 170, 50, fill='light')
    svg.text(300, 277, "事件队列", size=FS_SMALL, bold=True)
    svg.text(300, 297, "优先级排序", size=FS_TINY, fill='text_light')

    svg.rect(215, 330, 170, 50, fill='light')
    svg.text(300, 347, "Agent 循环", size=FS_SMALL, bold=True)
    svg.text(300, 367, "取出→推理→执行", size=FS_TINY, fill='text_light')

    svg.rect(215, 400, 170, 50, fill='medium')
    svg.text(300, 417, "会话管理", size=FS_SMALL, bold=True)
    svg.text(300, 437, "多线程上下文", size=FS_TINY, fill='text_light')

    for i in range(4):
        svg.arrow(300, 170 + i * 70, 300, 190 + i * 70)

    for i in range(6):
        svg.arrow(160, 104 + i * 58, 213, 145)

    # MCP Tools (right)
    svg.text(610, 65, "MCP 工具服务器", size=FS_BODY, bold=True)

    tools = [
        ("感知工具", "search_web, read_file\nread_webpage, parse_image"),
        ("执行工具", "code_interpreter\nvirtual_terminal, write_file"),
        ("协作工具", "browser_use\nrequest_human_approval"),
        ("通知工具", "send_email, send_slack\nsend_im_notification"),
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
    svg.text(805, 115, "持久层", size=FS_SMALL, bold=True)
    items = ["对话历史", "事件日志", "定时任务", "工具状态", "审计追踪"]
    for i, item in enumerate(items):
        svg.text(805, 160 + i * 55, item, size=FS_SMALL)

    svg.save(os.path.join(OUT, 'fig4-4.svg'))


# ──────────────────────── fig4-5 ────────────────────────

def fig4_5():
    """同步-异步模型矛盾"""
    w, h = 880, 520
    svg = SVG(w, h)
    svg.text(w / 2, 30, "同步训练范式 vs 异步部署现实", size=FS_TITLE, bold=True)

    # Top half: training pattern
    svg.rect(20, 55, w - 40, 195, fill='white', stroke='border', dash=True)
    svg.text(60, 78, "训练范式（严格同步序列）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 200, 64, 160, 28, "API 强制约束", fill='dark', font_size=FS_SMALL)

    steps_train = [
        ("Observation", 'medium', "用户: 查北京天气"),
        ("Thinking", 'light', "需要调天气工具"),
        ("Action", 'medium', "get_weather(Beijing)"),
        ("Observation", 'light', "22°C, 晴"),
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
             "tool_call → 必须下一条是 tool_result，否则 API 报错", size=FS_TINY)

    # Separator
    svg.line(20, 262, w - 20, 262, color='dark', dash=True)
    svg.text(w / 2, 280, "矛盾", size=FS_BODY, bold=True, fill='darker')

    # Bottom half: async reality
    svg.rect(20, 295, w - 40, 210, fill='white', stroke='border', dash=True)
    svg.text(60, 318, "部署现实（异步事件穿插）", size=FS_BODY, bold=True, anchor='start')
    _pill(svg, w - 200, 304, 160, 28, "格式冲突!", fill='dark', font_size=FS_SMALL)

    # Async timeline
    items = [
        ("Assistant", 'medium', "tool_call:\nget_weather(Beijing)", 0.0, 0.20),
        ("等待中...", 'code_bg', "工具执行 ~5s", 0.22, 0.50),
        ("User 打断", 'dark', "\"不用了,\n查上海的\"", 0.40, 0.55),
        ("???", 'code_bg', "tool_result 何时到？\n格式如何保证？", 0.57, 0.78),
        ("占位符", 'light', "[工具仍在执行,\n优先处理打断]", 0.80, 1.0),
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
             "解决: 占位符修复格式 + 非紧急事件入队 + 只在真正紧急时打断",
             size=FS_TINY)

    # Bottom insight
    svg.rect(140, 465, w - 280, 40, fill='dark')
    svg.text(w / 2, 485,
             "根本解法：下一代模型需在异步环境中通过 RL 训练",
             size=FS_SMALL, fill='white', bold=True)

    svg.save(os.path.join(OUT, 'fig4-5.svg'))


# ──────────────────────── fig4-6 ────────────────────────

def fig4_6():
    """实验 4.5：带打断能力的异步 Agent"""
    w, h = 880, 520
    svg = SVG(w, h)
    svg.text(w / 2, 30, "实验 4.5：异步 Agent 打断与恢复", size=FS_TITLE, bold=True)

    # Timeline
    tl_y, tl_h = 60, 440
    tl_x0, tl_w = 120, 740

    # Lanes
    lanes = [
        ("Agent", 80),
        ("工具 A", 180),
        ("工具 B", 260),
        ("工具 C", 340),
        ("轨迹", 420),
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
    tbar(80, 0.0, 0.12, 'medium', 'LLM: 启动3个工具')

    # Tools running
    tbar(180, 0.13, 0.45, 'light', '脚本A: 每秒3% → 33s完成')
    tbar(260, 0.13, 0.70, 'light', '脚本B: 每秒2% → 50s...')
    tbar(340, 0.13, 0.90, 'code_bg', '脚本C: 每秒1% → 100s...')

    # Event: tool A completes
    t_done = 0.45
    svg.line(tl_x0 + tl_w * t_done, 70, tl_x0 + tl_w * t_done, 450, color='border', dash=True)
    svg.text(tl_x0 + tl_w * t_done, 62, "A 完成", size=FS_TINY, bold=True)

    # Agent checks others
    tbar(80, 0.46, 0.58, 'medium', '查询 B,C 进度')
    tbar(420, 0.46, 0.58, 'light', 'B≈66% C≈33%')

    # Cancel C (< 50%)
    t_cancel = 0.60
    svg.line(tl_x0 + tl_w * t_cancel, 70, tl_x0 + tl_w * t_cancel, 450, color='dark', dash=True)
    svg.text(tl_x0 + tl_w * t_cancel, 62, "取消 C", size=FS_TINY, bold=True, fill='darker')

    tbar(340, 0.60, 0.65, 'dark', '×')

    # B finishes
    t_b_done = 0.70
    svg.line(tl_x0 + tl_w * t_b_done, 70, tl_x0 + tl_w * t_b_done, 450, color='border', dash=True)
    svg.text(tl_x0 + tl_w * t_b_done, 62, "B 完成", size=FS_TINY, bold=True)

    # Agent generates report
    tbar(80, 0.72, 0.95, 'medium', 'LLM: 整合 A+B 结果生成报告')
    tbar(420, 0.72, 0.95, 'light', 'A结果 + B结果 + C取消记录')

    # Annotations
    svg.rect(tl_x0, 460, tl_w, 40, fill='code_bg', stroke='dark', rx=4)
    svg.mono(tl_x0 + 10, 480,
             "关键: 占位符注入 + 异步完成事件 + cancel_tool(task_id) API",
             size=FS_TINY)

    svg.save(os.path.join(OUT, 'fig4-6.svg'))


# ──────────────────────── fig4-7 ────────────────────────

def fig4_7():
    """工具发现层次结构（server→tool 匹配）"""
    w, h = 880, 540
    svg = SVG(w, h)
    svg.text(w / 2, 30, "层次化工具匹配", size=FS_TITLE, bold=True)

    # Query at top
    svg.rect(250, 55, 380, 44, fill='medium')
    svg.text(440, 77, "Agent: \"我需要查询 GitHub 仓库的贡献者统计\"", size=FS_SMALL, bold=True)

    svg.arrow(440, 99, 440, 130)

    # discover_tools
    svg.rect(300, 132, 280, 44, fill='dark')
    svg.text(440, 154, "discover_tools(自然语言需求)", size=FS_SMALL, fill='white', bold=True)

    svg.arrow(440, 176, 440, 210)

    # Layer 1: Server matching
    svg.rect(20, 210, w - 40, 110, fill='white', stroke='border', dash=True)
    svg.text(55, 233, "第一层：服务器匹配（语义相似度）", size=FS_BODY, bold=True, anchor='start')

    servers = [
        ("GitHub", 0.92, 'dark'),
        ("Weather", 0.15, 'light'),
        ("Finance", 0.23, 'light'),
        ("ArXiv", 0.18, 'light'),
        ("File System", 0.31, 'light'),
    ]
    sx = 50
    for name, score, fill in servers:
        svg.rect(sx, 255, 145, 50, fill=fill)
        tc = 'white' if fill in ('dark', 'darker') else 'text'
        svg.text(sx + 72, 272, name, size=FS_SMALL, bold=True, fill=tc)
        svg.text(sx + 72, 292, f"相似度: {score:.2f}", size=FS_TINY, fill='white' if fill == 'dark' else 'text_light')
        sx += 165

    # Arrow to layer 2
    svg.arrow(123, 305, 123, 345)
    svg.text(175, 330, "Top-1 服务器", size=FS_SMALL, fill='text_light')

    # Layer 2: Tool matching within server
    svg.rect(20, 345, w - 40, 160, fill='white', stroke='border', dash=True)
    svg.text(55, 368, "第二层：工具匹配（GitHub 服务器内 26 个工具）", size=FS_BODY, bold=True, anchor='start')

    tools = [
        ("search_repositories", 0.41, "搜索仓库"),
        ("list_contributors", 0.89, "贡献者列表"),
        ("get_repo_stats", 0.85, "仓库统计"),
        ("create_issue", 0.12, "创建 Issue"),
        ("get_commit_history", 0.67, "提交历史"),
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
    svg.mono(190, 483, "返回 Top-3: list_contributors, get_repo_stats, get_commit_history", size=12)

    svg.save(os.path.join(OUT, 'fig4-7.svg'))


# ──────────────────────── fig4-8 ────────────────────────

def fig4_8():
    """KV 缓存优化（系统提示词稳定性）"""
    w, h = 880, 560
    svg = SVG(w, h)
    svg.text(w / 2, 30, "工具动态加载的 KV Cache 优化", size=FS_TITLE, bold=True)

    # Left: naive approach
    left_x = 30
    svg.text(220, 65, "朴素方案（缓存失效）", size=FS_BODY, bold=True)

    blocks_naive = [
        ("System Prompt", 120, 'medium', "你是一个AI助手...\n+ 全部工具 schema", "~50K tokens"),
        ("User Message", 100, 'light', "查询 NVDA 股价", ""),
        ("Assistant", 80, 'light', "tool_call: ...", ""),
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
    svg.text(left_x + 190, ny + 25, "每次加载新工具 → 整个缓存失效!", size=FS_SMALL, fill='white', bold=True)

    # Right: optimized approach
    right_x = 460
    svg.text(660, 65, "优化方案（缓存稳定）", size=FS_BODY, bold=True)

    blocks_opt = [
        ("System Prompt (固定)", 75, 'medium',
         "你是一个AI助手...\n角色 + 规则 + 基础工具",
         "~2K tokens | KV 缓存"),
        ("Agent 状态栏 (轻量)", 45, 'code_bg',
         "可用工具: web_search, get_weather...",
         "~200 tokens"),
        ("User: discover_tools", 40, 'light',
         '"我需要查股票价格"',
         ""),
        ("Tool Result", 55, 'light',
         "返回 get_stock_quote schema",
         "工具定义在此"),
        ("User Message", 40, 'light',
         "查询 NVDA 股价",
         ""),
        ("Agent 状态栏 (更新)", 45, 'code_bg',
         "+get_stock_quote 已添加",
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
    svg.text(right_x + 200, oy + 25, "System Prompt 不变 → KV Cache 完全复用", size=FS_SMALL, bold=True)

    # Bottom comparison
    svg.line(30, 475, w - 30, 475, color='dark', dash=True)
    comps = [
        ("缓存命中率", "~0%（每次工具变化失效）", "~95%（仅 hint 微变）"),
        ("首 Token 延迟", "高（每次重算 50K tokens）", "低（增量计算 ~200 tokens）"),
    ]
    cy = 495
    svg.text(250, cy, "对比维度", size=FS_SMALL, bold=True)
    svg.text(500, cy, "朴素方案", size=FS_SMALL, bold=True)
    svg.text(740, cy, "优化方案", size=FS_SMALL, bold=True)
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
