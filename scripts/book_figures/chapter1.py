"""Chapter 1 figures: retain technical content, using print-friendly grayscale."""
import base64
import struct

from introduction import Figure, ROOT


def agent_environment():
    f = Figure('Agent 与 Environment 的闭环交互，以及 Agent 内部的 Model–Harness 结构',
               'Agent 包含并列的 Model 与 Harness。Harness 组织上下文、调度工具并管理运行；环境接收行动、更新状态并返回观测。', 730)
    f.box(20, 20, 550, 690, '#ffffff')
    f.text(295, 58, 'Agent（智能体）', 26, True)
    f.box(45, 100, 220, 185, '#dedede')
    f.text(155, 140, 'Model', 26, True)
    f.text(155, 185, '理解 · 推理', 22)
    f.text(155, 221, '选择下一步行动', 22)
    f.box(295, 100, 250, 580, '#f2f2f2')
    f.text(420, 140, 'Harness', 25, True)
    f.box(310, 165, 220, 185, '#ffffff')
    f.text(420, 199, '上下文管理', 23, True)
    f.text(420, 236, '指令 · 工具定义\n观测 · 历史 · 记忆\n任务状态', 20)
    f.box(310, 430, 220, 80, '#ffffff')
    f.text(420, 463, '工具接口', 23, True)
    f.text(420, 494, '调用校验 · 调度', 20)
    f.box(310, 540, 220, 115, '#ffffff')
    f.text(420, 575, '循环 · 状态管理', 21, True)
    f.text(420, 618, '约束 · 验证 · 纠正', 20)
    # Context enters Model; tool requests return to Harness for dispatch.
    f.path([(310, 260), (265, 260)], True)
    f.text(185, 350, '工具调用请求', 20)
    f.path([(70, 285), (70, 470), (310, 470)], True)
    f.box(690, 100, 190, 580, '#dedede')
    f.text(785, 140, 'Environment', 23, True)
    f.text(785, 175, '环境', 23, True)
    f.box(705, 210, 160, 110, '#ffffff')
    f.text(785, 248, '当前状态', 22, True)
    f.text(785, 287, '状态转移', 20)
    f.text(785, 378, '文件 · 数据库\n网页 · API\n应用程序\n用户\n其他 Agent\n物理或仿真世界', 20)
    f.path([(690, 260), (530, 260)], True)
    f.text(610, 241, '观测', 22, True)
    f.path([(530, 470), (690, 470)], True)
    f.text(610, 450, '行动', 22, True)
    f.save('fig1-1.svg')


def learning_paths():
    f = Figure('Agent 能力更新的三个层次', '上下文、外部产物与模型参数的载体、方法和更新特性。', 490)
    items = [
        ('上下文适应', '当前上下文', '示例 · 状态 · 检索结果', '即时调整 · 低成本', '跨任务使用需保存并加载'),
        ('外部产物更新', '知识 · 指令 · 程序', '文档 · Prompt / Skill\nHarness', '跨任务保存 · 可审计', '通过上下文或工具使用'),
        ('模型参数更新', '模型权重', 'SFT · 偏好训练 · RL', '内化模式 · 泛化到新任务', '训练 · 评估 · 部署'),
    ]
    for i,(title,carrier,method,feature,cost) in enumerate(items):
        x = 20 + i*290
        f.box(x,20,280,450,'#ffffff')
        f.box(x,20,280,70,'#dedede')
        f.text(x+140,64,title,25,True)
        f.text(x+140,136,'主要载体',20)
        f.text(x+140,175,carrier,23,True)
        f.text(x+140,222,method,20)
        f.path([(x+20,300),(x+260,300)])
        f.text(x+140,341,'更新特性',20)
        f.text(x+140,382,feature,20)
        f.text(x+140,425,cost,20)
    f.save('fig1-2.svg')


def context_ablation():
    f = Figure('实验 1-1——上下文消融实验设计', '五组条件均保留系统提示词和当前任务。工具定义、历史调用、历史推理与工具结果按各组条件保留或移除。', 680)
    f.box(150,20,600,65,'#dedede')
    f.text(450,60,'固定输入：系统提示词 + 当前用户任务',23,True)
    f.path([(450,85),(450,115)],True)
    widths=[200,100,110,110,110,230]
    xs=[20]
    for w in widths: xs.append(xs[-1]+w)
    headers=['实验条件','工具\n定义','历史\n调用','历史\n推理','工具\n结果','本次运行结果']
    for j,h in enumerate(headers):
        f.box(xs[j],115,widths[j],80,'#dedede')
        f.text(xs[j]+widths[j]/2,146 if '\n' in h else 164,h,21,True)
    rows=[
        ('完整基线',['保留']*4,'正确完成\n3 轮 · 4 次调用'),
        ('无历史推理',['保留','保留','移除','保留'],'正确完成\n3 轮 · 4 次调用'),
        ('无工具定义',['移除','保留','保留','保留'],'告知缺少工具\n1 轮 · 0 次调用'),
        ('无工具结果',['保留','保留','保留','移除'],'重复调用，达轮数上限\n5 轮 · 9 次调用'),
        ('无历史消息',['保留','移除','移除','移除'],'重复换汇，达轮数上限\n5 轮 · 15 次调用'),
    ]
    for i,(label,values,result) in enumerate(rows):
        y=195+i*90
        for j,value in enumerate([label]+values+[result]):
            f.box(xs[j],y,widths[j],90,'#ffffff' if value=='移除' else '#f2f2f2')
            f.text(xs[j]+widths[j]/2,y+(33 if '\n' in value else 53),value,20,j==0)
    f.save('fig1-3.svg')


def revenue_trajectory():
    f = Figure('Agent 轨迹——多币种汇总任务的 ReAct 循环', '系统提示词和工具定义作为稳定前缀，每轮接入累积的消息历史。三轮分别换汇、计算、交付结果。', 1210)
    f.box(20,20,860,90,'#dedede')
    f.text(450,57,'相对稳定的前缀',24,True)
    f.text(450,91,'系统提示词 + 工具定义：convert_currency、code_interpreter',20)
    # Each panel preserves the actual message sequence and intermediate values.
    f.box(110,135,770,130,'#ffffff')
    f.text(495,168,'user',22,True)
    f.text(495,203,'Q1：250 万 USD；Q2：210 万 EUR',21)
    f.text(495,236,'Q3：180 万 GBP；Q4：3.8 亿 JPY；求年度总额与季度均值',21)
    f.text(60,320,'第 1 轮',20,True)
    f.box(110,285,770,235,'#f2f2f2')
    f.text(495,320,'assistant.reasoning',22,True)
    f.text(495,355,'将 EUR、GBP、JPY 收入换算为 USD',21)
    f.text(495,394,'assistant.tool_calls',22,True)
    f.text(495,430,'convert_currency(2100000, "EUR", "USD")',21)
    f.text(495,463,'convert_currency(1800000, "GBP", "USD")',21)
    f.text(495,496,'convert_currency(380000000, "JPY", "USD")',21)
    f.box(110,535,770,110,'#ffffff')
    f.text(495,570,'tool：换汇结果',22,True)
    f.text(495,605,'EUR → 2,282,608.70 USD；GBP → 2,278,481.01 USD',21)
    f.text(495,636,'JPY → 2,541,806.02 USD',21)
    f.text(60,700,'第 2 轮',20,True)
    f.box(110,670,770,235,'#f2f2f2')
    f.text(495,706,'assistant.reasoning',22,True)
    f.text(495,741,'读取换汇结果，求和后除以 4',21)
    f.text(495,780,'assistant.tool_calls → code_interpreter',22,True)
    f.text(495,818,'total = 2500000 + 2282608.70 + 2278481.01 + 2541806.02',21)
    f.text(495,851,'average = total / 4',21)
    f.text(495,884,'print(round(total, 2), round(average, 2))',21)
    f.box(110,920,770,85,'#ffffff')
    f.text(495,953,'tool：计算结果',22,True)
    f.text(495,988,'9602895.73    2400723.93',21)
    f.text(60,1060,'第 3 轮',20,True)
    f.box(110,1030,770,150,'#f2f2f2')
    f.text(495,1065,'assistant.content',22,True)
    f.text(495,1106,'年度总收入：9,602,895.73 USD',22)
    f.text(495,1146,'季度平均收入：2,400,723.93 USD',22)
    for a,b in [(110,135),(265,285),(520,535),(645,670),(905,920),(1005,1030)]:
        f.path([(495,a),(495,b)],True)
    f.save('fig1-4.svg')


def hosted_tools():
    f = Figure('模型主导的工具调用：客户端循环与服务端托管循环', 'Kimi 搜索由客户端组织循环；托管搜索与代码执行由服务端组织循环。保留任务、查询、返回结果与分析步骤。', 1240)
    f.box(20,20,860,70,'#dedede')
    f.text(450,62,'后训练（包括强化学习）→ 模型的工具调用策略',24,True)
    f.box(20,115,860,410,'#ffffff')
    f.text(450,153,'实验 1-2：客户端组织搜索循环',25,True)
    for x,title,body in [(40,'客户端 Harness','任务：核查成员资格\n与首都状态'),(330,'Kimi K3','查询决策\n补查缺失证据'),(620,'Formula 服务','web_search\n执行搜索')]:
        f.box(x,180,240,110,'#f2f2f2')
        f.text(x+120,211,title,22,True)
        f.text(x+120,245,body,20)
    f.path([(280,210),(330,210)],True)
    for x in [160,450,740]:
        f.path([(x,290),(x,340 if x == 450 else 500)])
    f.path([(450,330),(160,330)],True)
    f.text(305,320,'调用请求',20)
    f.path([(160,390),(740,390)],True)
    f.text(450,378,'客户端调度：查询成员名单、法规与总统令',20)
    f.path([(740,465),(160,465)],True)
    f.text(450,451,'返回搜索结果 → 追加上下文 → 再次调用模型',20)
    f.box(20,550,860,665,'#ffffff')
    f.text(450,590,'实验 1-3：服务端托管搜索与计算循环',25,True)
    f.box(40,615,820,85,'#f2f2f2')
    f.text(450,648,'客户端：提交任务与用户补充信息',22,True)
    f.text(450,681,'BTC/USD 日线；MA7、MA20、RSI14、MACD(12,26,9)',20)
    f.path([(450,700),(450,725)],True)
    f.box(40,725,820,370,'#dedede')
    f.text(450,759,'模型服务：Harness 调度模型与托管工具',23,True)
    f.box(60,785,260,285,'#ffffff')
    f.text(190,821,'qwen3.7-plus',23,True)
    f.text(190,861,'读取任务与结果\n选择搜索或代码执行\n检查并调整下一步',20)
    f.box(480,785,360,115,'#ffffff')
    f.text(660,820,'web_search',23,True)
    f.text(660,857,'BTC/USD 日线数据与来源\n返回相关资料',20)
    f.box(480,930,360,140,'#ffffff')
    f.text(660,965,'code_interpreter',23,True)
    f.text(660,1002,'价格序列 → 均线、RSI、MACD\n区间收益 · 最大回撤\n计算结果 · 沙盒内生成图表',20)
    f.path([(320,820),(480,820)],True)
    f.text(400,805,'查询',20)
    f.path([(480,885),(320,885)],True)
    f.text(400,875,'观测',20)
    f.path([(320,960),(480,960)],True)
    f.text(400,948,'代码',20)
    f.path([(480,1045),(320,1045)],True)
    f.text(400,1033,'结果',20)
    f.path([(450,1095),(450,1120)],True)
    f.box(180,1120,540,65,'#f2f2f2')
    f.text(450,1160,'客户端接收：分析报告 + 执行日志',22,True)
    f.save('fig1-5.svg')


def autonomous_loop():
    f = Figure('自主 Agent 的执行循环', '保留推理、行动、观测与全部退出条件；任务完成经验证交付，错误或预算超限保存进度并报告。', 880)
    f.box(190,30,360,105,'#dedede')
    f.text(370,65,'检查运行预算与错误状态',23,True)
    f.text(370,100,'最大轮数 · 错误次数\n不可恢复错误',20)
    f.box(630,30,240,105,'#ffffff')
    f.text(750,65,'停止运行',23,True)
    f.text(750,100,'保存进度\n报告未完成部分／转人工',20)
    f.path([(550,80),(630,80)],True)
    f.text(590,65,'需停止',20)
    f.path([(370,135),(370,205)],True)
    f.text(440,176,'可继续',20)
    f.box(190,205,360,110,'#f2f2f2')
    f.text(370,241,'推理与决策（Reasoning）',23,True)
    f.text(370,281,'“还需更多信息”／准备回答',21)
    f.path([(275,315),(275,385)],True)
    f.text(320,359,'工具请求',20)
    f.box(90,385,370,120,'#f2f2f2')
    f.text(275,426,'行动（Acting）',23,True)
    f.text(275,463,'web_search(...)\nHarness 校验并调度执行',20)
    f.path([(275,505),(275,580)],True)
    f.box(90,580,370,125,'#ffffff')
    f.text(275,620,'观测（Observation）',23,True)
    f.text(275,660,'tool_result: "..."\n结果或错误追加到上下文',20)
    f.path([(90,642),(35,642),(35,80),(190,80)],True)
    f.path([(550,260),(570,260),(570,360),(680,360),(680,385)],True)
    f.text(705,306,'final_answer 或\n不含工具调用的回复',20)
    f.box(520,385,320,120,'#f2f2f2')
    f.text(680,426,'验证完成条件',23,True)
    f.text(680,468,'任务结果 · 必要产物',21)
    f.path([(680,505),(680,580)],True)
    f.text(727,550,'通过',20)
    f.box(520,580,320,85,'#dedede')
    f.text(680,631,'交付最终结果',23,True)
    f.path([(840,445),(875,445),(875,790),(370,790),(370,705)],True)
    f.text(670,775,'未通过：反馈差距，继续执行',21)
    f.save('fig1-6.svg')


def n8n_print_view():
    """Embed the unaltered product screenshot in a grayscale SVG print view."""
    original = (ROOT / 'n8n-workflow.png').read_bytes()
    width, height = struct.unpack('>II', original[16:24])
    encoded = base64.b64encode(original).decode('ascii')
    (ROOT / 'n8n-workflow-grayscale.svg').write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
        f'width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">\n'
        '<title id="title">n8n 工作流编辑器界面</title>\n'
        '<desc id="desc">原始产品截图的灰度印刷视图，保留全部节点与连线。</desc>\n'
        '<defs><filter id="grayscale" color-interpolation-filters="sRGB">'
        '<feColorMatrix type="saturate" values="0"/></filter></defs>\n'
        f'<image width="{width}" height="{height}" filter="url(#grayscale)" '
        f'xlink:href="data:image/png;base64,{encoded}"/>\n</svg>\n'
    )


if __name__ == '__main__':
    agent_environment()
    learning_paths()
    context_ablation()
    revenue_trajectory()
    hosted_tools()
    autonomous_loop()
    n8n_print_view()
