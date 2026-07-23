"""Generate all Chapter 1 figures."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import *

OUT = os.path.join(os.path.dirname(__file__), 'images')


def fig1_4():
    """Kimi K3 / GPT-5.6 native agent architecture — caption 图 1-4"""
    s = SVG(820, 520)

    # Title
    s.text(410, 30, '"模型即 Agent" 架构：原生工具调用', size=FS_TITLE, bold=True)

    # Central model box
    s.rect(260, 70, 300, 100, fill='medium')
    s.text(410, 100, 'LLM（Kimi K3 / GPT-5.6）', size=FS_BODY, bold=True)
    s.text(410, 130, 'RL 训练后的原生 Agent 能力', size=FS_SMALL, fill='text_light')

    # Built-in tools on the right
    s.group_box(620, 70, 180, 210, '原生工具')
    s.box(635, 105, 150, 50, '$web_search', fill='light', font_size=FS_SMALL)
    s.box(635, 170, 150, 50, 'code_interpreter', fill='light', font_size=FS_SMALL)
    s.box(635, 235, 150, 50, '更多工具...', fill='white', font_size=FS_SMALL)

    s.arrow(560, 120, 633, 130)
    s.arrow(633, 195, 560, 145)

    # ReAct loop below
    s.group_box(100, 210, 460, 280, 'ReAct 循环（模型内部自主执行）')

    # Step 1: User input
    s.box(120, 250, 200, 55, '用户：搜索最近一个月\n的比特币走势', fill='light', font_size=FS_SMALL)

    # Step 2: Think
    s.box(120, 325, 200, 55, '思考：需要搜索实时\n数据，再用代码分析', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(220, 307, 220, 323)

    # Step 3: Tool call
    s.box(340, 250, 200, 55, '调用 $web_search\n"BTC price last month"', fill='light', font_size=FS_SMALL)
    s.arrow(322, 277, 338, 277)

    # Step 4: Tool result
    s.box(340, 325, 200, 55, '结果：[价格数据]\n$67,230 → $71,450', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(440, 307, 440, 323)

    # Step 5: Code
    s.box(120, 400, 200, 55, '调用 code_interpreter\nRSI, MACD 计算代码', fill='light', font_size=FS_SMALL)
    s.arrow(340, 377, 220, 398, color='dark')

    # Step 6: Final
    s.box(340, 400, 200, 55, '最终输出：技术分析\n报告 + 可视化图表', fill='medium', font_size=FS_SMALL)
    s.arrow(322, 427, 338, 427)

    # RL training signal — 走右侧 ReAct/工具 间的空隙，避免遮挡内部内容
    s.arrow_curved(565, 480, 410, 172, curve=40, dash=True, color='dark')
    s.text(605, 330, 'RL 训练信号', size=FS_TINY, fill='text_light', bold=True, anchor='start')

    # Left side: what's different from traditional
    s.group_box(15, 70, 230, 120, '与传统框架的区别')
    s.text(130, 110, '✗ 无需外部编排代码', size=FS_SMALL, anchor='middle')
    s.text(130, 135, '✗ 无需手写 ReAct 循环', size=FS_SMALL, anchor='middle')
    s.text(130, 160, '✓ 模型自主决策全流程', size=FS_SMALL, anchor='middle')

    s.save(f'{OUT}/fig1-4.svg')  # “模型即 Agent”架构 → 图1-4


def fig1_1():
    """Three learning paradigms — caption 图 1-1."""
    s = SVG(820, 480)

    s.text(410, 30, 'Agent 的三种学习范式', size=FS_TITLE, bold=True)

    col_w = 240
    gap = 20
    x_start = (820 - 3 * col_w - 2 * gap) / 2

    for i, (title, subtitle, time_label, items, example) in enumerate([
        ('后训练', 'Post-training', '训练时', [
            '修改模型权重',
            '永久性 · 通用性',
            '成本高 · 更新慢',
        ], '例：学会"何时调用工具"'),
        ('上下文学习', 'In-Context Learning', '推理时', [
            '注意力机制软更新',
            '临时性 · 即时适应',
            '受限于窗口大小',
        ], '例：从 3 个示例学会新格式'),
        ('外部化学习', 'Externalized Learning', '运行时', [
            '知识库 + 工具生成',
            '持久性 · 可更新',
            '高可靠 · 可验证',
        ], '例：将流程固化为代码工具'),
    ]):
        x = x_start + i * (col_w + gap)

        # Header
        s.box(x, 65, col_w, 65, f'{title}\n{subtitle}', fill='medium', bold=True, font_size=FS_BODY)

        # Time badge
        s.badge(x + col_w / 2 - 40, 140, 80, 28, time_label, fill='darker')

        # Items
        for j, item in enumerate(items):
            y = 185 + j * 45
            s.box(x, y, col_w, 38, item, fill='light', font_size=FS_SMALL)

        # Example
        s.rect(x, 330, col_w, 45, fill='code_bg', stroke='dark', rx=4)
        s.text(x + col_w / 2, 352, example, size=FS_SMALL, fill='text_light')

    # Timeline arrow at bottom
    s.arrow(60, 430, 760, 430, color='dark')
    s.text(60, 455, '慢（数周）', size=FS_SMALL, fill='text_light', anchor='start')
    s.text(410, 455, '学习速度', size=FS_SMALL, fill='text_light')
    s.text(760, 455, '快（毫秒）', size=FS_SMALL, fill='text_light', anchor='end')

    s.save(f'{OUT}/fig1-1.svg')  # 三种学习范式 → 图1-1


def fig1_2():
    """Context ablation experiment design — caption 图 1-2."""
    W = 980
    s = SVG(W, 500)

    s.text(W / 2, 30, '上下文消融实验设计', size=FS_TITLE, bold=True)

    # Column headers（标签已缩短以避免溢出）
    components = ['系统指令', '工具定义', '推理过程', '历史记录', '工具结果']
    comp_w = 105
    comp_gap = 10
    total_comp = len(components) * comp_w + (len(components) - 1) * comp_gap
    # 左侧给行标签留 110，右侧给结果列留 170
    comp_x = 130

    for i, comp in enumerate(components):
        x = comp_x + i * (comp_w + comp_gap)
        s.text(x + comp_w / 2, 65, comp, size=FS_SMALL, bold=True)

    # 结果列表头
    result_x = comp_x + len(components) * (comp_w + comp_gap) + 10  # = 705
    s.text(result_x + 80, 65, '结果', size=FS_SMALL, bold=True)

    # Experiment rows
    conditions = [
        ('完整基线', [True, True, True, True, True], '✓ 正常工作'),
        ('无工具定义', [True, False, True, True, True], '✗ 无法调用工具'),
        ('无推理过程', [True, True, False, True, True], '△ 决策不连贯'),
        ('无历史记录', [True, True, True, False, True], '△ 重复操作'),
        ('无工具结果', [True, True, True, True, False], '✗ 盲目循环'),
    ]

    for j, (label, flags, result) in enumerate(conditions):
        y = 95 + j * 72

        # Row label
        s.text(115, y + 28, label, size=FS_SMALL, bold=True, anchor='end')

        for i, present in enumerate(flags):
            x = comp_x + i * (comp_w + comp_gap)
            fill = 'light' if present else 'white'
            stroke = 'border' if present else 'dark'
            s.rect(x, y, comp_w, 55, fill=fill, stroke=stroke, dash=not present)
            if present:
                s.text(x + comp_w / 2, y + 28, '✓', size=FS_BODY)
            else:
                s.text(x + comp_w / 2, y + 28, '✗', size=FS_BODY, fill='dark')

        # Result (in its own column to the right of the check grid)
        s.text(result_x + 80, y + 28, result, size=FS_SMALL,
               fill='text' if '✓' in result else ('text_light' if '△' in result else 'dark'))

    s.save(f'{OUT}/fig1-2.svg')  # 上下文消融实验 → 图1-2


def fig1_3():
    """Agent trajectory — caption 图 1-3."""
    s = SVG(820, 680)

    s.text(410, 30, 'Agent 轨迹：多币种汇总任务的 ReAct 循环', size=FS_TITLE, bold=True)

    lx = 40  # left margin
    rw = 480  # box width
    code_w = 460

    y = 60

    # Round 1
    s.badge(lx, y, 80, 26, '第 1 轮', fill='darker')
    y += 36

    # User message
    s.rect(lx, y, rw, 50, fill='light')
    s.text(lx + 10, y + 16, 'user', size=FS_SMALL, bold=True, anchor='start')
    s.text(lx + 10, y + 38, '"计算年度总收入：Q1 $2.5M, Q2 €2.1M, Q3 £1.8M"', size=FS_TINY, anchor='start')
    y += 60

    # Assistant reasoning
    s.rect(lx, y, rw, 45, fill='#e8e8e8')
    s.text(lx + 10, y + 14, 'assistant.reasoning', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.text(lx + 10, y + 34, '"需要将 EUR 和 GBP 转换为 USD，再汇总计算"', size=FS_TINY, anchor='start')
    y += 55

    # Tool calls
    s.rect(lx, y, rw, 70, fill='code_bg', stroke='dark', rx=4)
    s.text(lx + 10, y + 14, 'assistant.tool_calls', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'convert_currency(2100000, "EUR", "USD")', size=FS_TINY)
    s.mono(lx + 10, y + 54, 'convert_currency(1800000, "GBP", "USD")', size=FS_TINY)
    y += 80

    # Tool results
    s.rect(lx, y, rw, 55, fill='light')
    s.text(lx + 10, y + 14, 'tool (结果)', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'EUR→USD: 2,282,608.70', size=FS_TINY)
    s.mono(lx + 250, y + 36, 'GBP→USD: 2,278,481.01', size=FS_TINY)
    y += 65

    # Round 2
    s.badge(lx, y, 80, 26, '第 2 轮', fill='darker')
    y += 36

    # Assistant reasoning 2
    s.rect(lx, y, rw, 45, fill='#e8e8e8')
    s.text(lx + 10, y + 14, 'assistant.reasoning', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.text(lx + 10, y + 34, '"已获得汇率，调用代码解释器汇总"', size=FS_TINY, anchor='start')
    y += 55

    # Code interpreter call
    s.rect(lx, y, rw, 50, fill='code_bg', stroke='dark', rx=4)
    s.text(lx + 10, y + 14, 'assistant.tool_calls', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'code_interpreter("total = 2.5M + 2.28M + 2.28M")', size=FS_TINY)
    y += 60

    # Round 3
    s.badge(lx, y, 80, 26, '第 3 轮', fill='darker')
    y += 36

    # Final answer
    s.rect(lx, y, rw, 45, fill='medium')
    s.text(lx + 10, y + 14, 'assistant.content（最终回答）', size=FS_SMALL, bold=True, anchor='start')
    s.text(lx + 10, y + 36, '"年度总收入 $7,061,089.71，季度均值 $2,353,696.57"', size=FS_TINY, anchor='start')
    y += 55

    # Right side: brace + annotation
    bx = 540
    s.brace_right(bx, 60, y - 10, '')
    s.text(600, 250, '轨迹', size=FS_BODY, bold=True, anchor='start')
    s.text(600, 280, '=', size=FS_BODY, anchor='start')
    s.text(600, 310, 'LLM 每次', size=FS_BODY, anchor='start')
    s.text(600, 340, '调用时看到', size=FS_BODY, anchor='start')
    s.text(600, 370, '的完整输入', size=FS_BODY, anchor='start')

    # Key insight box on right
    s.group_box(570, 410, 230, 140, '关键特性')
    s.text(685, 445, '上下文累积', size=FS_SMALL, bold=True)
    s.text(685, 470, '每轮都看到全部历史', size=FS_TINY, fill='text_light')
    s.text(685, 500, '结构化轨迹', size=FS_SMALL, bold=True)
    s.text(685, 525, 'user / assistant / tool', size=FS_TINY, fill='text_light')

    s.save(f'{OUT}/fig1-3.svg')  # Agent 轨迹 → 图1-3


def fig1_wf_chaining():
    """Prompt chaining — workflow pattern (ch1 编排模式节)."""
    s = SVG(820, 300)

    s.text(410, 28, '提示链模式：多步骤内容创作', size=FS_TITLE, bold=True)

    # Nodes with concrete descriptions
    nodes = [
        ('需求文档', 'light', FS_SMALL),
        ('LLM: 生成大纲', '#e8e8e8', FS_SMALL),
        ('LLM: 撰写正文', '#e8e8e8', FS_SMALL),
        ('LLM: 翻译', '#e8e8e8', FS_SMALL),
        ('多语言文档', 'medium', FS_SMALL),
    ]

    node_w = 130
    node_h = 55
    gap = 15
    total = len(nodes) * node_w + (len(nodes) - 1) * gap
    x_start = (820 - total) / 2
    y = 65

    for i, (label, fill, fs) in enumerate(nodes):
        x = x_start + i * (node_w + gap)
        s.box(x, y, node_w, node_h, label, fill=fill, font_size=fs)
        if i > 0:
            px = x_start + (i - 1) * (node_w + gap) + node_w
            s.arrow(px + 2, y + node_h / 2, x - 2, y + node_h / 2)

    # Gate symbols between steps
    gate_y = y + node_h + 15
    for i in [1, 2]:
        gx = x_start + i * (node_w + gap) + node_w / 2
        s.diamond(gx, gate_y + 22, 60, 40, fill='white', label='门控', font_size=FS_TINY)
        s.line(gx, y + node_h, gx, gate_y + 2, dash=True, color='dark')

    # Example content snippets below
    snippet_y = gate_y + 60
    snippets = [
        (x_start + 15, '"产品发布说明"'),
        (x_start + node_w + gap + 15, '→ 5节大纲'),
        (x_start + 2 * (node_w + gap) + 15, '→ 3000字文档'),
        (x_start + 3 * (node_w + gap) + 15, '→ EN / JP / KR'),
    ]
    for sx, txt in snippets:
        s.text(sx, snippet_y, txt, size=FS_TINY, fill='text_light', anchor='start')

    s.save(f'{OUT}/fig1-10.svg')  # 提示链工作流（本章未引用）→ 图1-10


def fig1_wf_routing():
    """Routing — workflow pattern (ch1 编排模式节)."""
    s = SVG(820, 440)

    s.text(410, 28, '路由模式：客户服务分类', size=FS_TITLE, bold=True)

    # Input
    s.box(30, 130, 150, 55, '用户查询', fill='medium', font_size=FS_BODY)

    # Router
    s.diamond(300, 157, 140, 80, fill='#e8e8e8', label='分类器', font_size=FS_SMALL)
    s.arrow(182, 157, 230, 157)

    # Branches
    branches = [
        (55, '退款请求', '退款策略 Prompt\n+ 订单 API', 'light'),
        (155, '技术支持', '诊断 Prompt\n+ 日志工具', 'light'),
        (255, '常见问题', 'FAQ Prompt\n+ 知识库', 'light'),
        (355, '其他', 'Haiku（低成本）\n+ 通用 Prompt', 'white'),
    ]

    bx = 490
    bw = 160
    for i, (by_offset, label, desc, fill) in enumerate(branches):
        by = by_offset
        s.box(bx, by, bw, 50, label, fill=fill, bold=True, font_size=FS_SMALL)
        s.box(bx + bw + 10, by, 140, 50, desc, fill='code_bg', font_size=FS_TINY)
        s.arrow(370, 157, bx - 2, by + 25)

    # Annotation
    s.text(410, 425, '关键：分类可由 LLM 或传统分类器完成，简单/常见问题路由到小模型', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig1-6.svg')


def fig1_wf_parallel():
    """Parallelization — workflow pattern (ch1 编排模式节)."""
    s = SVG(820, 360)

    s.text(410, 28, '并行化模式：多视角代码审查', size=FS_TITLE, bold=True)

    # Input
    s.box(30, 130, 150, 55, '代码提交\nPull Request', fill='medium', font_size=FS_SMALL)

    # Split
    s.text(220, 157, '分段', size=FS_SMALL, bold=True)

    # Parallel workers
    workers = [
        (70, '安全审查 LLM₁', 'SQL注入\nXSS\n权限泄露'),
        (155, '风格审查 LLM₂', '命名规范\n代码重复\n复杂度'),
        (240, '逻辑审查 LLM₃', '边界条件\n空指针\n并发问题'),
    ]

    wx = 290
    ww = 155
    for i, (wy, title, items) in enumerate(workers):
        s.box(wx, wy, ww, 55, title, fill='light', bold=True, font_size=FS_SMALL)
        s.box(wx + ww + 5, wy, 130, 55, items, fill='code_bg', font_size=FS_TINY)
        s.arrow(180, 157, wx - 2, wy + 28)

    # Aggregate
    s.box(640, 130, 150, 55, '聚合结果\n综合审查报告', fill='medium', font_size=FS_SMALL)
    for i, (wy, _, _) in enumerate(workers):
        s.arrow(wx + ww + 135 + 2, wy + 28, 638, 157)

    s.save(f'{OUT}/fig1-7.svg')


def fig1_wf_orchestrator():
    """Orchestrator-workers — workflow pattern (ch1 编排模式节)."""
    s = SVG(820, 440)

    s.text(410, 28, '编排器-工作器模式：多文件代码修改', size=FS_TITLE, bold=True)

    # Orchestrator at top: 标题 + 内部子描述纵向分开排布
    s.rect(260, 60, 300, 95, fill='medium')
    s.text(410, 82, '编排器 LLM', size=FS_BODY, bold=True)
    s.rect(270, 105, 280, 38, fill='#e8e8e8', rx=4)
    s.text(410, 124, '"分析 Issue → 定位文件 → 分配子任务"', size=FS_TINY)

    # Workers（Worker 3 首行较长，字号缩小以避免溢出）
    workers = [
        (40, 'Worker 1', '修改 auth.py\n添加 OAuth2 支持', '读取/编辑\n文件工具', None),
        (290, 'Worker 2', '修改 api.py\n添加新端点', '读取/编辑\n文件工具', None),
        (540, 'Worker 3', '编写 test_auth.py\n测试用例', '执行测试\n工具', FS_SMALL - 1),
    ]

    wy = 220
    ww = 230
    wh = 55
    for wx, title, task, tools, first_fs in workers:
        s.box(wx, wy, ww, wh, f'{title}：{task}', fill='light', font_size=FS_SMALL,
              first_line_font_size=first_fs)
        s.box(wx + 20, wy + wh + 10, ww - 40, 40, tools, fill='code_bg', font_size=FS_TINY)
        s.arrow(410, 157, wx + ww / 2, wy - 2)

    # Synthesize
    s.box(260, 370, 300, 55, '编排器：合并结果 → 验证一致性', fill='medium', font_size=FS_SMALL)
    for wx, _, _, _, _ in workers:
        s.arrow(wx + ww / 2, wy + wh + 52, 410, 368)

    s.save(f'{OUT}/fig1-8.svg')


def fig1_wf_evaluator():
    """Evaluator-optimizer — workflow pattern (ch1 编排模式节)."""
    s = SVG(820, 380)

    s.text(410, 28, '评估器-优化器模式：文学翻译迭代', size=FS_TITLE, bold=True)

    # Generator
    s.box(50, 100, 200, 65, '生成器 LLM\n生成初始翻译', fill='light', font_size=FS_SMALL)

    # Output
    s.rect(50, 185, 200, 45, fill='code_bg', stroke='dark', rx=4)
    s.text(150, 208, '"春眠不觉晓" → v1 译文', size=FS_TINY)
    s.arrow(150, 167, 150, 183)

    # Evaluator
    s.box(330, 100, 200, 65, '评估器 LLM\n多维度评分', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(252, 207, 330, 160)

    # Evaluation criteria
    s.rect(330, 185, 200, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(340, 205, '准确性: 4/5', size=FS_TINY, anchor='start')
    s.text(340, 225, '流畅性: 3/5 ←需改进', size=FS_TINY, anchor='start')
    s.text(340, 245, '文化适应: 4/5', size=FS_TINY, anchor='start')
    s.arrow(430, 167, 430, 183)

    # Feedback loop — 标签放在弧顶上方避免遮挡评估器内容
    s.arrow_curved(430, 267, 150, 98, curve=80, dash=True, color='dark')
    s.text(290, 90, '反馈 + 改进建议', size=FS_TINY, fill='text_light', bold=True)

    # Iteration indicator
    s.box(610, 100, 170, 55, '迭代次数: n', fill='white', font_size=FS_SMALL)
    s.text(695, 170, '退出条件：', size=FS_SMALL, bold=True, anchor='start')
    s.text(695, 195, '① 所有维度 ≥ 4/5', size=FS_TINY, anchor='start', fill='text_light')
    s.text(695, 218, '② 达到最大轮次', size=FS_TINY, anchor='start', fill='text_light')

    # Final output
    s.box(220, 310, 380, 55, '最终输出：经过 3 轮迭代的高质量翻译', fill='medium', font_size=FS_SMALL)

    s.save(f'{OUT}/fig1-9.svg')


def fig1_5():
    """Autonomous Agent loop — caption 图 1-5."""
    s = SVG(820, 500)

    s.text(410, 28, '自主 Agent 的执行循环', size=FS_TITLE, bold=True)

    # While loop structure
    s.rect(80, 60, 500, 380, fill='white', stroke='border', rx=8, dash=True)
    s.text(330, 82, 'while not done:', size=FS_BODY, bold=True)

    # Step 1: Think — 标题在框上方，代码在框内
    s.rect(120, 100, 420, 60, fill='#e8e8e8')
    s.text(130, 115, '① 思考（Reasoning）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 125, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 140, '"分析搜索结果...信息不足,需要进一步搜索"', size=FS_TINY)

    # Step 2: Act
    s.rect(120, 175, 420, 60, fill='light')
    s.text(130, 190, '② 行动（Acting）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 200, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 215, 'web_search("Agent RL training techniques 2025")', size=FS_TINY)
    s.arrow(330, 162, 330, 173)

    # Step 3: Observe
    s.rect(120, 250, 420, 60, fill='light')
    s.text(130, 265, '③ 观察（Observing）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 275, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 290, 'tool_result: "Found 3 relevant papers..."', size=FS_TINY)
    s.arrow(330, 237, 330, 248)

    # Loop back arrow
    s.arrow_curved(540, 280, 540, 120, curve=-40, label='继续循环', color='dark')

    # Exit conditions on the right
    s.group_box(610, 60, 190, 190, '退出条件')
    exits = [
        '① 任务完成',
        '② 调用 final_answer',
        '③ 无工具调用返回',
        '④ 达到最大轮次',
        '⑤ 错误次数超限',
    ]
    for i, ex in enumerate(exits):
        s.text(620, 100 + i * 32, ex, size=FS_SMALL, anchor='start')

    # Bottom: concrete iteration example
    s.rect(80, 360, 500, 70, fill='medium', rx=6)
    s.text(330, 380, '实际执行示例：SWE-bench 代码修复', size=FS_SMALL, bold=True)
    s.text(330, 405, '搜索代码 → 定位 Bug → 编辑文件 → 运行测试 → 修复失败 → 再次编辑 → 测试通过 → 完成', size=FS_TINY)
    s.text(330, 425, '（5 轮迭代，12 次工具调用）', size=FS_TINY, fill='text_light')

    # Done arrow
    s.arrow(330, 312, 330, 358, label='done = True')

    s.save(f'{OUT}/fig1-5.svg')  # 自主 Agent 执行循环 → 图1-5


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # In-chapter figures (referenced as 图 1-1 ~ 图 1-5)
    fig1_1()
    fig1_2()
    fig1_3()
    fig1_4()
    fig1_5()
    # Workflow pattern figures (currently unused in chapter1.md;
    # kept for potential future use)
    fig1_wf_chaining()
    fig1_wf_routing()
    fig1_wf_parallel()
    fig1_wf_orchestrator()
    fig1_wf_evaluator()
    print("Chapter 1: 5 in-chapter + 5 workflow figures generated.")
