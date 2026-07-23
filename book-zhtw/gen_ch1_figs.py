"""Generate all Chapter 1 figures."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from svg_lib import *

OUT = os.path.join(os.path.dirname(__file__), 'images')


def fig1_4():
    """Kimi K3 / GPT-5.6 native agent architecture — caption 圖 1-4"""
    s = SVG(820, 520)

    # Title
    s.text(410, 30, '"模型即 Agent" 架構：原生工具呼叫', size=FS_TITLE, bold=True)

    # Central model box
    s.rect(260, 70, 300, 100, fill='medium')
    s.text(410, 100, 'LLM（Kimi K3 / GPT-5.6）', size=FS_BODY, bold=True)
    s.text(410, 130, 'RL 訓練後的原生 Agent 能力', size=FS_SMALL, fill='text_light')

    # Built-in tools on the right
    s.group_box(620, 70, 180, 210, '原生工具')
    s.box(635, 105, 150, 50, '$web_search', fill='light', font_size=FS_SMALL)
    s.box(635, 170, 150, 50, 'code_interpreter', fill='light', font_size=FS_SMALL)
    s.box(635, 235, 150, 50, '更多工具...', fill='white', font_size=FS_SMALL)

    s.arrow(560, 120, 633, 130)
    s.arrow(633, 195, 560, 145)

    # ReAct loop below
    s.group_box(100, 210, 460, 280, 'ReAct 迴圈（模型內部自主執行）')

    # Step 1: User input
    s.box(120, 250, 200, 55, '使用者：搜尋最近一個月\n的比特幣走勢', fill='light', font_size=FS_SMALL)

    # Step 2: Think
    s.box(120, 325, 200, 55, '思考：需要搜尋實時\n資料，再用程式碼分析', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(220, 307, 220, 323)

    # Step 3: Tool call
    s.box(340, 250, 200, 55, '呼叫 $web_search\n"BTC price last month"', fill='light', font_size=FS_SMALL)
    s.arrow(322, 277, 338, 277)

    # Step 4: Tool result
    s.box(340, 325, 200, 55, '結果：[價格資料]\n$67,230 → $71,450', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(440, 307, 440, 323)

    # Step 5: Code
    s.box(120, 400, 200, 55, '呼叫 code_interpreter\nRSI, MACD 計算程式碼', fill='light', font_size=FS_SMALL)
    s.arrow(340, 377, 220, 398, color='dark')

    # Step 6: Final
    s.box(340, 400, 200, 55, '最終輸出：技術分析\n報告 + 視覺化圖表', fill='medium', font_size=FS_SMALL)
    s.arrow(322, 427, 338, 427)

    # RL training signal — 走右側 ReAct/工具 間的空隙，避免遮擋內部內容
    s.arrow_curved(565, 480, 410, 172, curve=40, dash=True, color='dark')
    s.text(605, 330, 'RL 訓練訊號', size=FS_TINY, fill='text_light', bold=True, anchor='start')

    # Left side: what's different from traditional
    s.group_box(15, 70, 230, 120, '與傳統框架的區別')
    s.text(130, 110, '✗ 無需外部編排程式碼', size=FS_SMALL, anchor='middle')
    s.text(130, 135, '✗ 無需手寫 ReAct 迴圈', size=FS_SMALL, anchor='middle')
    s.text(130, 160, '✓ 模型自主決策全流程', size=FS_SMALL, anchor='middle')

    s.save(f'{OUT}/fig1-4.svg')  # 「模型即 Agent」架構 → 圖1-4


def fig1_1():
    """Three learning paradigms — caption 圖 1-1."""
    s = SVG(820, 480)

    s.text(410, 30, 'Agent 的三種學習正規化', size=FS_TITLE, bold=True)

    col_w = 240
    gap = 20
    x_start = (820 - 3 * col_w - 2 * gap) / 2

    for i, (title, subtitle, time_label, items, example) in enumerate([
        ('後訓練', 'Post-training', '訓練時', [
            '修改模型權重',
            '永久性 · 通用性',
            '成本高 · 更新慢',
        ], '例：學會"何時呼叫工具"'),
        ('上下文學習', 'In-Context Learning', '推理時', [
            '注意力機制軟更新',
            '臨時性 · 即時適應',
            '受限於視窗大小',
        ], '例：從 3 個示例學會新格式'),
        ('外部化學習', 'Externalized Learning', '執行時', [
            '知識庫 + 工具生成',
            '永續性 · 可更新',
            '高可靠 · 可驗證',
        ], '例：將流程固化為程式碼工具'),
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
    s.text(60, 455, '慢（數週）', size=FS_SMALL, fill='text_light', anchor='start')
    s.text(410, 455, '學習速度', size=FS_SMALL, fill='text_light')
    s.text(760, 455, '快（毫秒）', size=FS_SMALL, fill='text_light', anchor='end')

    s.save(f'{OUT}/fig1-1.svg')  # 三種學習正規化 → 圖1-1


def fig1_2():
    """Context ablation experiment design — caption 圖 1-2."""
    W = 980
    s = SVG(W, 500)

    s.text(W / 2, 30, '上下文消融實驗設計', size=FS_TITLE, bold=True)

    # Column headers（順序與正文實驗 1-1 移除順序一致）
    components = ['系統提示詞', '工具定義', '工具執行結果', '思考過程', '歷史訊息']
    comp_w = 105
    comp_gap = 10
    total_comp = len(components) * comp_w + (len(components) - 1) * comp_gap
    # 左側給行標籤留 110，右側給結果列留 170
    comp_x = 130

    for i, comp in enumerate(components):
        x = comp_x + i * (comp_w + comp_gap)
        s.text(x + comp_w / 2, 65, comp, size=FS_SMALL, bold=True)

    # 結果列表頭
    result_x = comp_x + len(components) * (comp_w + comp_gap) + 10  # = 705
    s.text(result_x + 80, 65, '結果', size=FS_SMALL, bold=True)

    # Experiment rows
    conditions = [
        ('完整基線', [True, True, True, True, True], '✓ 正常工作'),
        ('無工具定義', [True, False, True, True, True], '✗ 無法呼叫工具'),
        ('無工具執行結果', [True, True, False, True, True], '✗ 盲目迴圈'),
        ('無思考過程', [True, True, True, False, True], '△ 決策不連貫'),
        ('無歷史訊息', [True, True, True, True, False], '△ 重複操作'),
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

    s.save(f'{OUT}/fig1-2.svg')  # 上下文消融實驗 → 圖1-2


def fig1_3():
    """Agent trajectory — caption 圖 1-3."""
    s = SVG(820, 680)

    s.text(410, 30, 'Agent 軌跡：多幣種彙總任務的 ReAct 迴圈', size=FS_TITLE, bold=True)

    lx = 40  # left margin
    rw = 480  # box width
    code_w = 460

    y = 60

    # Round 1
    s.badge(lx, y, 80, 26, '第 1 輪', fill='darker')
    y += 36

    # User message
    s.rect(lx, y, rw, 50, fill='light')
    s.text(lx + 10, y + 16, 'user', size=FS_SMALL, bold=True, anchor='start')
    s.text(lx + 10, y + 38, '"計算年度總收入：Q1 $2.5M, Q2 €2.1M, Q3 £1.8M"', size=FS_TINY, anchor='start')
    y += 60

    # Assistant reasoning
    s.rect(lx, y, rw, 45, fill='#e8e8e8')
    s.text(lx + 10, y + 14, 'assistant.reasoning', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.text(lx + 10, y + 34, '"需要將 EUR 和 GBP 轉換為 USD，再彙總計算"', size=FS_TINY, anchor='start')
    y += 55

    # Tool calls
    s.rect(lx, y, rw, 70, fill='code_bg', stroke='dark', rx=4)
    s.text(lx + 10, y + 14, 'assistant.tool_calls', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'convert_currency(2100000, "EUR", "USD")', size=FS_TINY)
    s.mono(lx + 10, y + 54, 'convert_currency(1800000, "GBP", "USD")', size=FS_TINY)
    y += 80

    # Tool results
    s.rect(lx, y, rw, 55, fill='light')
    s.text(lx + 10, y + 14, 'tool (結果)', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'EUR→USD: 2,282,608.70', size=FS_TINY)
    s.mono(lx + 250, y + 36, 'GBP→USD: 2,278,481.01', size=FS_TINY)
    y += 65

    # Round 2
    s.badge(lx, y, 80, 26, '第 2 輪', fill='darker')
    y += 36

    # Assistant reasoning 2
    s.rect(lx, y, rw, 45, fill='#e8e8e8')
    s.text(lx + 10, y + 14, 'assistant.reasoning', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.text(lx + 10, y + 34, '"已獲得匯率，呼叫程式碼直譯器彙總"', size=FS_TINY, anchor='start')
    y += 55

    # Code interpreter call
    s.rect(lx, y, rw, 50, fill='code_bg', stroke='dark', rx=4)
    s.text(lx + 10, y + 14, 'assistant.tool_calls', size=FS_SMALL, bold=True, anchor='start', fill='darker')
    s.mono(lx + 10, y + 36, 'code_interpreter("total = 2.5M + 2.28M + 2.28M")', size=FS_TINY)
    y += 60

    # Round 3
    s.badge(lx, y, 80, 26, '第 3 輪', fill='darker')
    y += 36

    # Final answer
    s.rect(lx, y, rw, 45, fill='medium')
    s.text(lx + 10, y + 14, 'assistant.content（最終回答）', size=FS_SMALL, bold=True, anchor='start')
    s.text(lx + 10, y + 36, '"年度總收入 $7,061,089.71，季度均值 $2,353,696.57"', size=FS_TINY, anchor='start')
    y += 55

    # Right side: brace + annotation
    bx = 540
    s.brace_right(bx, 60, y - 10, '')
    s.text(600, 250, '軌跡', size=FS_BODY, bold=True, anchor='start')
    s.text(600, 280, '=', size=FS_BODY, anchor='start')
    s.text(600, 310, 'LLM 每次', size=FS_BODY, anchor='start')
    s.text(600, 340, '呼叫時看到', size=FS_BODY, anchor='start')
    s.text(600, 370, '的完整輸入', size=FS_BODY, anchor='start')

    # Key insight box on right
    s.group_box(570, 410, 230, 140, '關鍵特性')
    s.text(685, 445, '上下文累積', size=FS_SMALL, bold=True)
    s.text(685, 470, '每輪都看到全部歷史', size=FS_TINY, fill='text_light')
    s.text(685, 500, '結構化軌跡', size=FS_SMALL, bold=True)
    s.text(685, 525, 'user / assistant / tool', size=FS_TINY, fill='text_light')

    s.save(f'{OUT}/fig1-3.svg')  # Agent 軌跡 → 圖1-3


def fig1_wf_chaining():
    """Prompt chaining — workflow pattern (ch1 編排模式節)."""
    s = SVG(820, 300)

    s.text(410, 28, '提示鏈模式：多步驟內容創作', size=FS_TITLE, bold=True)

    # Nodes with concrete descriptions
    nodes = [
        ('需求文件', 'light', FS_SMALL),
        ('LLM: 生成大綱', '#e8e8e8', FS_SMALL),
        ('LLM: 撰寫正文', '#e8e8e8', FS_SMALL),
        ('LLM: 翻譯', '#e8e8e8', FS_SMALL),
        ('多語言文件', 'medium', FS_SMALL),
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
        s.diamond(gx, gate_y + 22, 60, 40, fill='white', label='門控', font_size=FS_TINY)
        s.line(gx, y + node_h, gx, gate_y + 2, dash=True, color='dark')

    # Example content snippets below
    snippet_y = gate_y + 60
    snippets = [
        (x_start + 15, '"產品釋出說明"'),
        (x_start + node_w + gap + 15, '→ 5節大綱'),
        (x_start + 2 * (node_w + gap) + 15, '→ 3000字文件'),
        (x_start + 3 * (node_w + gap) + 15, '→ EN / JP / KR'),
    ]
    for sx, txt in snippets:
        s.text(sx, snippet_y, txt, size=FS_TINY, fill='text_light', anchor='start')

    s.save(f'{OUT}/fig1-10.svg')  # 提示鏈工作流（本章未引用）→ 圖1-10


def fig1_wf_routing():
    """Routing — workflow pattern (ch1 編排模式節)."""
    s = SVG(820, 440)

    s.text(410, 28, '路由模式：客戶服務分類', size=FS_TITLE, bold=True)

    # Input
    s.box(30, 130, 150, 55, '使用者查詢', fill='medium', font_size=FS_BODY)

    # Router
    s.diamond(300, 157, 140, 80, fill='#e8e8e8', label='分類器', font_size=FS_SMALL)
    s.arrow(182, 157, 230, 157)

    # Branches
    branches = [
        (55, '退款請求', '退款策略 Prompt\n+ 訂單 API', 'light'),
        (155, '技術支援', '診斷 Prompt\n+ 日誌工具', 'light'),
        (255, '常見問題', 'FAQ Prompt\n+ 知識庫', 'light'),
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
    s.text(410, 425, '關鍵：分類可由 LLM 或傳統分類器完成，簡單/常見問題路由到小模型', size=FS_SMALL, fill='text_light')

    s.save(f'{OUT}/fig1-6.svg')


def fig1_wf_parallel():
    """Parallelization — workflow pattern (ch1 編排模式節)."""
    s = SVG(820, 360)

    s.text(410, 28, '並行化模式：多視角程式碼審查', size=FS_TITLE, bold=True)

    # Input
    s.box(30, 130, 150, 55, '程式碼提交\nPull Request', fill='medium', font_size=FS_SMALL)

    # Split
    s.text(220, 157, '分段', size=FS_SMALL, bold=True)

    # Parallel workers
    workers = [
        (70, '安全審查 LLM₁', 'SQL隱碼攻擊\nXSS\n許可權洩露'),
        (155, '風格審查 LLM₂', '命名規範\n程式碼重複\n複雜度'),
        (240, '邏輯審查 LLM₃', '邊界條件\n空指標\n併發問題'),
    ]

    wx = 290
    ww = 155
    for i, (wy, title, items) in enumerate(workers):
        s.box(wx, wy, ww, 55, title, fill='light', bold=True, font_size=FS_SMALL)
        s.box(wx + ww + 5, wy, 130, 55, items, fill='code_bg', font_size=FS_TINY)
        s.arrow(180, 157, wx - 2, wy + 28)

    # Aggregate
    s.box(640, 130, 150, 55, '聚合結果\n綜合審查報告', fill='medium', font_size=FS_SMALL)
    for i, (wy, _, _) in enumerate(workers):
        s.arrow(wx + ww + 135 + 2, wy + 28, 638, 157)

    s.save(f'{OUT}/fig1-7.svg')


def fig1_wf_orchestrator():
    """Orchestrator-workers — workflow pattern (ch1 編排模式節)."""
    s = SVG(820, 440)

    s.text(410, 28, '編排器-工作器模式：多檔案程式碼修改', size=FS_TITLE, bold=True)

    # Orchestrator at top: 標題 + 內部子描述縱向分開排布
    s.rect(260, 60, 300, 95, fill='medium')
    s.text(410, 82, '編排器 LLM', size=FS_BODY, bold=True)
    s.rect(270, 105, 280, 38, fill='#e8e8e8', rx=4)
    s.text(410, 124, '"分析 Issue → 定位檔案 → 分配子任務"', size=FS_TINY)

    # Workers
    workers = [
        (40, 'Worker 1', '修改 auth.py\n新增 OAuth2 支援', '讀取/編輯\n檔案工具'),
        (290, 'Worker 2', '修改 api.py\n新增新端點', '讀取/編輯\n檔案工具'),
        (540, 'Worker 3', '編寫 test_auth.py\n測試用例', '執行測試\n工具'),
    ]

    wy = 220
    ww = 230
    wh = 55
    for wx, title, task, tools in workers:
        s.box(wx, wy, ww, wh, f'{title}：{task}', fill='light', font_size=FS_SMALL)
        s.box(wx + 20, wy + wh + 10, ww - 40, 40, tools, fill='code_bg', font_size=FS_TINY)
        s.arrow(410, 157, wx + ww / 2, wy - 2)

    # Synthesize
    s.box(260, 370, 300, 55, '編排器：合併結果 → 驗證一致性', fill='medium', font_size=FS_SMALL)
    for wx, _, _, _ in workers:
        s.arrow(wx + ww / 2, wy + wh + 52, 410, 368)

    s.save(f'{OUT}/fig1-8.svg')


def fig1_wf_evaluator():
    """Evaluator-optimizer — workflow pattern (ch1 編排模式節)."""
    s = SVG(820, 380)

    s.text(410, 28, '評估器-最佳化器模式：文學翻譯迭代', size=FS_TITLE, bold=True)

    # Generator
    s.box(50, 100, 200, 65, '生成器 LLM\n生成初始翻譯', fill='light', font_size=FS_SMALL)

    # Output
    s.rect(50, 185, 200, 45, fill='code_bg', stroke='dark', rx=4)
    s.text(150, 208, '"春眠不覺曉" → v1 譯文', size=FS_TINY)
    s.arrow(150, 167, 150, 183)

    # Evaluator
    s.box(330, 100, 200, 65, '評估器 LLM\n多維度評分', fill='#e8e8e8', font_size=FS_SMALL)
    s.arrow(252, 207, 330, 160)

    # Evaluation criteria
    s.rect(330, 185, 200, 80, fill='code_bg', stroke='dark', rx=4)
    s.text(340, 205, '準確性: 4/5', size=FS_TINY, anchor='start')
    s.text(340, 225, '流暢性: 3/5 ←需改進', size=FS_TINY, anchor='start')
    s.text(340, 245, '文化適應: 4/5', size=FS_TINY, anchor='start')
    s.arrow(430, 167, 430, 183)

    # Feedback loop — 標籤放在弧頂上方避免遮擋評估器內容
    s.arrow_curved(430, 267, 150, 98, curve=80, dash=True, color='dark')
    s.text(290, 90, '反饋 + 改進建議', size=FS_TINY, fill='text_light', bold=True)

    # Iteration indicator
    s.box(610, 100, 170, 55, '迭代次數: n', fill='white', font_size=FS_SMALL)
    s.text(695, 170, '退出條件：', size=FS_SMALL, bold=True, anchor='start')
    s.text(695, 195, '① 所有維度 ≥ 4/5', size=FS_TINY, anchor='start', fill='text_light')
    s.text(695, 218, '② 達到最大輪次', size=FS_TINY, anchor='start', fill='text_light')

    # Final output
    s.box(220, 310, 380, 55, '最終輸出：經過 3 輪迭代的高質量翻譯', fill='medium', font_size=FS_SMALL)

    s.save(f'{OUT}/fig1-9.svg')


def fig1_5():
    """Autonomous Agent loop — caption 圖 1-5."""
    s = SVG(820, 500)

    s.text(410, 28, '自主 Agent 的執行迴圈', size=FS_TITLE, bold=True)

    # While loop structure
    s.rect(80, 60, 500, 380, fill='white', stroke='border', rx=8, dash=True)
    s.text(330, 82, 'while not done:', size=FS_BODY, bold=True)

    # Step 1: Think — 標題在框上方，程式碼在框內
    s.rect(120, 100, 420, 60, fill='#e8e8e8')
    s.text(130, 115, '① 思考（Reasoning）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 125, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 140, '"分析搜尋結果...資訊不足,需要進一步搜尋"', size=FS_TINY)

    # Step 2: Act
    s.rect(120, 175, 420, 60, fill='light')
    s.text(130, 190, '② 行動（Acting）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 200, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 215, 'web_search("Agent RL training techniques 2025")', size=FS_TINY)
    s.arrow(330, 162, 330, 173)

    # Step 3: Observe
    s.rect(120, 250, 420, 60, fill='light')
    s.text(130, 265, '③ 觀察（Observing）', size=FS_SMALL, bold=True, anchor='start')
    s.rect(130, 275, 400, 28, fill='code_bg', rx=4)
    s.mono(140, 290, 'tool_result: "Found 3 relevant papers..."', size=FS_TINY)
    s.arrow(330, 237, 330, 248)

    # Loop back arrow
    s.arrow_curved(540, 280, 540, 120, curve=-40, label='繼續迴圈', color='dark')

    # Exit conditions on the right
    s.group_box(610, 60, 190, 190, '退出條件')
    exits = [
        '① 任務完成',
        '② 呼叫 final_answer',
        '③ 無工具呼叫返回',
        '④ 達到最大輪次',
        '⑤ 錯誤次數超限',
    ]
    for i, ex in enumerate(exits):
        s.text(620, 100 + i * 32, ex, size=FS_SMALL, anchor='start')

    # Bottom: concrete iteration example
    s.rect(80, 360, 500, 70, fill='medium', rx=6)
    s.text(330, 380, '實際執行示例：SWE-bench 程式碼修復', size=FS_SMALL, bold=True)
    s.text(330, 405, '搜尋程式碼 → 定位 Bug → 編輯檔案 → 執行測試 → 修復失敗 → 再次編輯 → 測試透過 → 完成', size=FS_TINY)
    s.text(330, 425, '（5 輪迭代，12 次工具呼叫）', size=FS_TINY, fill='text_light')

    # Done arrow
    s.arrow(330, 312, 330, 358, label='done = True')

    s.save(f'{OUT}/fig1-5.svg')  # 自主 Agent 執行迴圈 → 圖1-5


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    # In-chapter figures (referenced as 圖 1-1 ~ 圖 1-5)
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
