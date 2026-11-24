"""Chapter 6: grayscale interaction diagrams with concrete messages and state."""
from introduction import Figure
from chapter5 import panel, down


def ingress():
    f=Figure('接入层：适配器、统一信封与接入日志','各来源经各自的适配器写入接入日志，路由分派给运行时，回复经出站适配器回到对话渠道。',720)
    for x,t,ls in [(20,'对话渠道',['App · IM · 邮件','可回到原处答复']),(313,'回调',['支付服务 · GitHub','验签 · 可能重投']),(607,'消息总线',['SQS · Kafka','确认 · 保留 · 重读'])]:
        panel(f,x,20,273,t,ls,136)
    f.path([(156,156),(156,180),(744,180),(744,156)])
    f.path([(450,156),(450,210)],True)
    panel(f,20,210,860,'适配器（每个来源一个）',['验证来源 · 生成信封 · 按来源语义去重','写入接入日志之后，才确认来源'],136)
    down(f,450,346,380)
    panel(f,20,380,860,'接入日志',['只增不改 · 按线程分区 · 线程内有序','信封：来源 · 去重键 · 线程 · 关联对象 · 回复能力'],136)
    f.path([(450,516),(450,533),(156,533),(156,550)],True)
    panel(f,20,550,273,'路由',['分派到任务与会话','过期 · 合并 · 限流'],136)
    panel(f,313,550,273,'运行时',['事件循环 · 任务状态','取消 · 恢复'],136)
    panel(f,607,550,273,'出站适配器',['先记发送意图','收到回执再标记完成'],136)
    f.path([(293,618),(313,618)],True)
    f.path([(586,618),(607,618)],True)
    f.path([(744,686),(744,704),(6,704),(6,88),(20,88)],True)
    f.save('fig6-2.svg')


def events():
    f=Figure('事件驱动的异步 Agent 架构','事件源、可信路由、队列与工具结果回流。',1010)
    data=[('Email · on_email_reply',['from: alice@example.com','subject: Re:会议']),('Timer · on_timer_expire',['task_id: daily_report','scheduled: 09:00']),('Webhook · on_webhook',['repo: agent-lib','event: pr_merged']),('User · on_user_message',['text: 帮我查明天天气','channel: chat'])]
    for i,(t,ls) in enumerate(data):panel(f,20+i%2*450,20+i//2*175,410,t,ls,145)
    f.path([(225,340),(225,365),(675,365),(675,340)])
    f.path([(225,165),(225,180),(675,180),(675,165)])
    f.path([(450,180),(450,365),(225,365),(225,395)],True)
    panel(f,20,395,410,'事件队列',['user.input：常规','email.reply：常规','user.interrupt：紧急','timer.trigger：常规'],225)
    panel(f,470,395,410,'运行时路由与调度',['校验来源、会话与事件类型','可信规则确定基础优先级','语义判断辅助任务分类','排队 · 取消 · 并行'],225)
    f.path([(430,505),(470,505)],True)
    down(f,675,620,655)
    panel(f,470,655,410,'上下文与模型决策',['结构化事件追加到当前上下文','未处理事件与任务状态汇总','LLM 选择回复或工具调用'],190)
    panel(f,20,655,410,'工具执行与结果',['同步执行 / 后台任务句柄','完成结果与取消状态','通知 · 响应 · 存储'],190)
    f.path([(470,740),(430,740)],True)
    f.path([(20,750),(6,750),(6,500),(20,500)],True)
    f.save('fig6-1.svg')


def strategies():
    f=Figure('异步事件处理的三种策略','从新事件到处理时机，再比较原任务与新事件的去向。',755)
    f.text(450,48,'新事件到达时，原任务怎么办？',28,True)
    groups=[
        ('取消','用户说“停止”','停止派发新动作，请求取消','确认已执行到哪一步，记录终态'),
        ('排队','用户补充“只看最近一个月”','搜索未结束，先将补充要求入队','收到搜索结果后，按新时间范围整理'),
        ('并行','后台分析时，用户又问天气','另开上下文查天气，主任务继续','分别保存天气答复和分析结果'),
    ]
    for i,(policy,event,action,result) in enumerate(groups):
        y=82+i*220
        f.box(20,y,210,184,'#dedede')
        f.text(125,y+95,policy,26,True)
        f.box(240,y,640,184,'#ffffff')
        f.text(560,y+40,event,22,True)
        f.text(560,y+93,action,22)
        f.text(560,y+149,result,22)
    f.save('fig6-3.svg')


def email():
    f=Figure('实验 6-1 事件驱动 Agent 架构','邮件处理案例及可扩展的事件、工具和持久化接口。',1020)
    panel(f,20,20,860,'事件入口',['邮件回复 · Web / App 消息 · GitHub PR 更新','定时器 · Webhook · 系统告警'],140)
    down(f,450,160,195)
    panel(f,20,195,860,'FastAPI 事件接入',['POST /events/{type} → 校验来源与会话 → 事件入队'],110)
    f.path([(450,305),(450,322),(225,322),(225,340)],True)
    panel(f,20,340,410,'事件循环与会话',['按策略取出事件','组织上下文 → LLM 决策','调度工具 → 接入结果','保存会话状态'],215)
    panel(f,470,340,410,'邮件任务示例',['会议邮件 → 检查冲突与草稿','投诉邮件 → 提取问题并通知','营销邮件 → 归档并查询确认','处理状态 → 用户通知'],215)
    f.path([(430,440),(470,440)],True)
    f.path([(225,555),(225,572),(675,572),(675,590)],True)
    down(f,225,572,590)
    panel(f,20,590,410,'MCP：感知与执行',['search_web · read_file','read_webpage · parse_image','code_interpreter · write_file','virtual_terminal'],225)
    panel(f,470,590,410,'MCP：协作与通知',['browser_use','request_human_approval','send_email · send_slack','send_im_notification'],225)
    f.path([(225,815),(225,832),(675,832),(675,815)])
    down(f,450,832,850)
    panel(f,20,850,860,'持久层',['对话历史 · 事件日志 · 定时任务','工具状态 · 审计追踪 · 邮件处理标记'],145)
    f.save('fig6-4.svg')


def cancellation():
    f=Figure('实验 6-2 异步 Agent 打断与恢复','三项真实子进程任务的进度、取消与结果汇总。',760)
    panel(f,20,20,860,'运行时启动三个后台任务',['返回 task_id，保存 pending 状态'],100)
    for x,t,ls in [(20,'任务 T1',['每个 tick 增长 3%','最先完成']),(320,'任务 T2',['每个 tick 增长 2%','实测进度 68%']),(620,'任务 T3',['每个 tick 增长 1%','实测进度 34%'])]:
        down(f,x+130,120,160);panel(f,x,160,260,t,ls,155)
    down(f,150,315,355)
    panel(f,20,355,860,'接收 T1 完成事件 → 查询 T2、T3 进度',['T2 > 50%：继续运行','T3 ≤ 50%：cancel_tool(task_id) → 确认进程终止'],145)
    down(f,450,500,540)
    panel(f,20,540,860,'收集最终状态并生成报告',['T1、T2 返回完成结果，T3 返回取消记录','完成事件与原始任务标识关联；每项终态进入记录'],155)
    f.save('fig6-5.svg')


def native_async():
    f=Figure('同步接口兼容与模型原生异步','后台任务句柄、原始调用标识与中途引导。',1010)
    panel(f,20,20,410,'同步接口的运行时适配',['工具返回 task_id 与 pending','本次调用结果与请求配对','模型处理其他消息','后台完成 → 新事件','按 task_id 恢复任务上下文'],275)
    panel(f,470,20,410,'模型原生异步工具',['声明工具 async: true','工具执行期间模型继续工作','返回结果关联原始 call_id','结果接入最新响应状态','模型综合新结果继续决策'],275)
    panel(f,20,340,860,'场地查询：执行期间接收用户更新',['初始条件：预算 2000 元、20 人','A：1800 元 / 30 人 · B：900 元 / 12 人 · C：600 元 / 8 人'],150)
    f.path([(450,490),(450,510),(225,510),(225,530)],True)
    f.path([(450,510),(675,510),(675,530)],True)
    panel(f,20,530,410,'查询尚未完成',['后台继续查询场地','前台整理议程与准备清单'],145)
    panel(f,470,530,410,'用户中途引导',['更新：预算 1000 元、10 人','记录更新来源与接入状态'],145)
    f.path([(225,675),(225,710),(675,710),(675,675)])
    down(f,450,710,750)
    panel(f,20,750,860,'结果与更新共同进入决策',['按初始条件可选 A；按新条件选择 B','运行时管理工具状态；模型采用更新后的任务条件'],150)
    f.save('fig6-6.svg')


def speech_pipeline():
    f=Figure('语音 Agent 串行流水线','采集、端点、识别、回复、合成与播放接口。',920)
    stages=[('音频采集与传输',['浏览器 AudioWorklet → WebSocket','音频块 → 重采样 / 格式转换']),('VAD 与端点逻辑',['Silero VAD：检测语音区间','静音阈值与上下文 → 提交一段音频']),('ASR → 文字',['Whisper / SenseVoice','音频 → 转录；保留端点与时间戳']),('LLM → 回复文本',['读取转录与任务上下文','生成可供 TTS 合成的文本']),('TTS 与播放',['Fish Audio S1：文本 → 音频块','网络传输 → 播放缓冲 → 扬声器'])]
    for i,(t,ls) in enumerate(stages):
        y=20+i*180;panel(f,100,y,700,t,ls,145)
        if i<4:down(f,450,y+145,y+180)
    f.save('fig6-7.svg')


def latency():
    f=Figure('延迟瀑布：串行累积总响应时间','示例配置中，从用户说完到首段播放的阶段耗时。',610)
    x0=235;scale=0.42
    stages=[('端点确认',500),('ASR 转录',100),('LLM 首段等待',200),('文本片段生成',200),('TTS 首包合成',300),('传输与播放缓冲',100)]
    t=0
    for i,(name,ms) in enumerate(stages):
        y=65+i*72;f.text(112,y+26,name,20)
        f.box(x0+t*scale,y,ms*scale,38,'#bdbdbd' if i%2 else '#e0e0e0')
        f.text(x0+(t+ms/2)*scale,y-10,f'{ms} ms',20)
        t+=ms
    f.path([(x0,510),(865,510)],True)
    for ms in [0,500,1000,1400]:
        x=x0+ms*scale;f.path([(x,505),(x,517)]);f.text(x,546,str(ms),20)
    f.text(540,585,'示例时间 / ms',22)
    f.save('fig6-8.svg')


def queueing():
    f=Figure('利用率与平均总时间','M/M/1 示例中，请求从进入队列到完成服务的平均用时随利用率上升。',640)
    panel(f,120,20,720,'M/M/1 单服务台模型',['泊松到达 · 指数服务时间 · 平均服务时间 S = 1 s','ρ = λS < 1；平均总时间 W = S / (1 − ρ)'],145)
    ox,oy,w,h=130,545,690,310
    f.path([(ox,oy),(850,oy)],True);f.path([(ox,oy),(ox,205)],True)
    for rho in [0,.2,.4,.6,.8,1]:
        x=ox+rho*w;f.path([(x,oy),(x,oy+6)]);f.text(x,oy+35,str(rho),20)
    for val in [0,2,4,6,8,10]:
        y=oy-val*h/10;f.path([(ox-5,y),(ox,y)]);f.text(100,y+7,str(val),20)
    # Service time is constant. The vertical gap up to the curve is queueing time.
    service_y = oy - h / 10
    f.parts.append(f'<path d="M {ox} {service_y} L {ox+w} {service_y}" fill="none" stroke="#777777" stroke-width="1.8" stroke-dasharray="7 5"/>')
    f.text(675, service_y-8, '虚线：平均服务时间 1 s', 20)
    pts=[(ox+r*w,oy-h/10/(1-r)) for r in [i/100 for i in range(91)]]
    f.path(pts)
    for r,label,dx,dy in [(.5,'ρ = 0.5：W = 2 s',-5,-27),(.8,'ρ = 0.8：W = 5 s',-105,-20)]:
        x=ox+r*w;y=oy-h/10/(1-r);f.box(x-3,y-3,6,6,'#333333');f.text(x+dx,y+dy,label,20)
    f.text(340,215,'平均总时间 W / s',22);f.text(700,620,'利用率 ρ',22)
    f.save('fig6-9.svg')


def cognition():
    f=Figure('快/慢思考架构与方案对比','任务确认、后台建议、构思与表达的三种安排。',1130)
    panel(f,20,20,860,'① 快回应 + 慢回答',['用户：这个套餐适合我吗？'],100)
    panel(f,20,155,410,'前台立即回应',['我来核对国际漫游功能','简单问题可直接回答'],140)
    panel(f,470,155,410,'后台深入分析',['查询功能与价格','结果：缺少所需国际漫游'],140)
    f.path([(225,295),(225,325),(675,325),(675,295)])
    down(f,450,325,350)
    panel(f,20,350,860,'综合回复',['核对后给出建议；追踪此前已向用户表达的内容'],95)
    panel(f,20,485,860,'② 前台交互 + 后台建议',['用户补充条件 → 后台更新任务 → 前台接收建议'],100)
    panel(f,20,620,410,'前台对话',['持续接收追问、说明进展','结合当前话题组织表达'],140)
    panel(f,470,620,410,'后台推理与工具',['传递任务、条件、证据、状态','条件变化 → 旧建议失效'],140)
    f.path([(430,650),(470,650)],True);f.path([(470,725),(430,725)],True)
    panel(f,20,800,860,'③ MPS：构思与表达协同',['Step-Audio R1.1 · 按可用内容与进度推进'],100)
    panel(f,20,935,410,'Formulation Brain',['推进构思与推理','提供可表达的中间内容'],140)
    panel(f,470,935,410,'Articulation Brain',['结合此前输出组织表达','持续生成语音片段'],140)
    f.path([(430,1005),(470,1005)],True)
    f.save('fig6-11.svg')


def computer_loop():
    f=Figure('Computer Use Agent 的感知-思考-行动循环','截图、动作决策、执行及新观测回流。',720)
    panel(f,65,20,770,'① 获取观测',['桌面 / 浏览器 / 应用截图','记录画面尺寸与界面状态'],135)
    down(f,450,155,190)
    panel(f,65,190,770,'② 模型决策',['输入：截图 + 任务 + 历史与当前状态','输出示例：点击收件地址框 click(512, 250)'],135)
    down(f,450,325,360)
    panel(f,65,360,770,'③ 执行动作',['工具层校验与调度 → xdotool / Playwright','鼠标：移动、点击、拖拽 · 键盘：输入、组合键','滚动：改变视口 · 等待：接收界面响应'],170)
    down(f,450,530,565)
    panel(f,65,565,770,'④ 读取动作后的状态',['重新截图：地址框获得焦点，还是弹出了登录框？'],100)
    f.path([(65,615),(25,615),(25,85),(65,85)],True)
    f.save('fig6-12.svg')


def computer_tools():
    f=Figure('Computer Use 动作空间','图形界面、命令执行、文件编辑与表单操作示例。',1080)
    panel(f,20,20,860,'图形界面工具 computer',['鼠标：mouse_move · left / right / middle_click','double / triple_click · left_click_drag · left_mouse_down / up','键盘：type · key · hold_key','滚动：scroll（方向、步数与修饰键）','观测：screenshot · cursor_position；等待：wait'],265)
    panel(f,20,325,410,'命令执行 bash',['持久终端会话','完成标记与超时处理','stdout / stderr 与退出状态'],195)
    panel(f,470,325,410,'文件编辑接口',['view · create · str_replace','insert · undo_edit','匹配校验 → 修改 → 差异检查'],195)
    panel(f,20,560,860,'图像与坐标转换',['实际屏幕 → 工具输出图像 → 模型坐标','逆变换 → 桌面坐标 → 执行器'],140)
    down(f,450,700,735)
    panel(f,20,735,860,'填写表单示例',['① screenshot：获取页面','② 模型定位姓名框 → mouse_move(324, 156)','③ left_click：获取输入焦点','④ type("John Smith")：输入姓名','⑤ 新截图：确认字段内容'],290)
    f.save('fig6-13.svg')


def grounding():
    f=Figure('Set-of-Mark 与结构化元素索引（browser-use 实现）','视觉候选与DOM候选共享可引用标记，并保留元素示例。',1200)
    panel(f,20,20,410,'视觉标注 SoM',['截图 → 分割或检测区域','为候选区域分配编号'],140)
    panel(f,470,20,410,'DOM / 无障碍元素索引',['CDP → DOM、布局与语义','筛选可交互元素 → 分配编号'],140)
    f.path([(225,160),(225,185),(675,185),(675,160)])
    down(f,450,185,220)
    f.box(20,220,860,250);f.box(40,240,820,42,'#dedede');f.text(450,270,'www.example.com',22)
    f.box(80,305,525,48);f.text(330,338,'[1] Search',22)
    f.box(650,305,180,48);f.text(740,338,'[2] Submit',22)
    f.box(80,382,525,48);f.text(330,415,'[3] Enter your name…',22)
    f.text(735,410,'[4] Docs →',22)
    down(f,450,470,511)
    panel(f,20,511,860,'模型选择编号 [2]',['本次 DOM 映射：[2] → 按钮 submit-btn','无障碍名称为 Submit form'],151)
    down(f,450,662,703)
    panel(f,20,703,860,'执行器检查目标是否可见、可交互',['点击 Submit，再读取更新后的页面'],115)
    down(f,450,818,859)
    panel(f,20,859,860,'页面刷新，重新收集候选并编号',['滚动、插入元素也可能改变映射','缺少结构化信息时，结合视觉标注或坐标预测'],150)
    f.save('fig6-14.svg')


def coordinates():
    f=Figure('分辨率匹配与双向坐标缩放','在桌面与工具截图中标出同一中心点并演示如何逆向换算。',760)
    f.text(215,48,'实际屏幕',25,True)
    f.text(705,48,'工具输出截图',25,True)
    for cx,top,w,h,label in [(215,75,368,207,'2560 × 1440'),(705,112,232,130,'1366 × 768')]:
        cy=top+h/2
        f.box(cx-w/2,top,w,h,'#ffffff')
        f.path([(cx-14,cy),(cx+14,cy)])
        f.path([(cx,cy-14),(cx,cy+14)])
        f.text(cx,top+h+34,label,22)
    f.path([(410,176),(575,176)],True)
    f.text(494,148,'缩放',22)
    f.path([(790,242),(790,350),(65,350),(65,282)],True)
    f.text(455,389,'模型点 (683, 384) 映回桌面中心',22,True)
    panel(f,20,420,860,'按两个方向的实际比例换算',['x = 683 × 2560 / 1366 = 1280','y = 384 × 1440 / 768 = 720'],150)
    down(f,450,570,606)
    panel(f,20,606,860,'点击 (1280, 720)，重新截图检查结果',['有留白时先减填充偏移，再除缩放系数','有裁剪或多个屏幕时，再加对应的原点偏移'],145)
    f.save('fig6-15.svg')


def duplex_timeline():
    f = Figure('全双工交互中的 200 毫秒微轮次',
               '上半部按时间对齐用户输入和助手输出。第二段里用户插话时助手仍在说话，第三段助手停下。下半部按模型处理顺序展开同一组输入和输出。', 410)
    left, width = 166, 174
    f.text(80, 60, '时间（ms）', 21)
    f.path([(left, 65), (881, 65)], arrow=True)
    for index in range(5):
        x = left + index * width
        f.path([(x, 60), (x, 72)])
        f.text(x, 49, str(index * 200), 21)
    for row, (label, chunks) in enumerate([
        ('用户输入', ['静音', '“不”', '“周”', '“五”']),
        ('助手输出', ['“周”', '“四”', '静音', '静音']),
    ]):
        y = 90 + row * 72
        f.text(84, y + 39, label, 24, True)
        for index, chunk in enumerate(chunks):
            x = left + index * width
            f.box(x + 2, y, width - 4, 58, '#ffffff' if chunk == '静音' else '#dedede')
            f.text(x + width / 2, y + 39, chunk, 24)
    f.text(450, 267, '同一段对话在模型中的处理顺序', 25, True)
    for i in range(8):
        x = 25 + 107 * i
        label = ('入' if i % 2 == 0 else '出') + str(i // 2 + 1)
        f.box(x, 295, 85, 58, '#dedede' if i % 2 == 0 else '#ffffff')
        f.text(x + 42.5, 333, label, 23)
        if i < 7:
            f.path([(x + 86, 324), (x + 104, 324)], arrow=True)
    f.text(450, 394, '入、出分别表示一块输入和输出，数字对应上方的时间格。', 21)
    f.save('fig6-10.svg')


if __name__ == '__main__':
    ingress();events();strategies();email();cancellation();native_async()
    speech_pipeline();latency();queueing();duplex_timeline();cognition()
    computer_loop();computer_tools();grounding();coordinates()
