"""Chapter 6: grayscale interaction diagrams with concrete messages and state."""
from introduction import Figure
from chapter5 import panel, down


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
    f=Figure('异步事件处理的三种策略','取消、排队、并行中的任务状态与事件处理。',990)
    groups=[('取消式 · 停止当前任务',[('当前任务',['LLM 推理 / 工具执行']),('新事件',['user.interrupt：停止！']),('运行时',['停止派发 → 请求取消']),('后续状态',['确认停止，记录已完成动作'])]),('队列式 · 在处理节点接入',[('当前任务',['执行 search_web']),('用户补充',['只看最近一个月 → 入队']),('结果返回',['tool.result 与补充一起接入']),('模型继续',['按新时间范围整理结果'])]),('并行式 · 独立任务分别推进',[('主任务',['后台数据分析持续执行']),('新请求',['今天天气怎样？']),('独立上下文',['查询天气 → 回复用户']),('任务关联',['分别记录主任务与天气结果'])])]
    for k,(title,steps) in enumerate(groups):
        y=20+k*325
        f.box(20,y,860,52,'#dedede');f.text(450,y+35,title,24,True)
        for j,(t,ls) in enumerate(steps):
            x=20+(j%2 if j<2 else 1-j%2)*450;yy=y+77+j//2*105
            panel(f,x,yy,410,t,ls,90)
        f.path([(430,y+122),(470,y+122)],True)
        f.path([(675,y+167),(675,y+182)],True)
        f.path([(470,y+227),(430,y+227)],True)
    f.save('fig6-2.svg')


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
    f.save('fig6-3.svg')


def cancellation():
    f=Figure('实验 6-2 异步 Agent 打断与恢复','三项真实子进程任务的进度、取消与结果汇总。',760)
    panel(f,20,20,860,'运行时启动三个后台任务',['返回 task_id，保存 pending 状态'],100)
    for x,t,ls in [(20,'任务 A',['每个 tick 增长 3%','最先完成']),(320,'任务 B',['每个 tick 增长 2%','A 完成时约 66%']),(620,'任务 C',['每个 tick 增长 1%','A 完成时约 33%'])]:
        down(f,x+130,120,160);panel(f,x,160,260,t,ls,155)
    down(f,150,315,355)
    panel(f,20,355,860,'接收 A 完成事件 → 查询 B、C 进度',['B > 50%：继续运行','C ≤ 50%：cancel_tool(task_id) → 确认进程终止'],145)
    down(f,450,500,540)
    panel(f,20,540,860,'收集最终状态并生成报告',['A：完成结果 · B：完成结果 · C：取消记录','完成事件与原始任务标识关联；每项终态进入记录'],155)
    f.save('fig6-4.svg')


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
    f.save('fig6-5.svg')


def speech_pipeline():
    f=Figure('语音 Agent 串行流水线','采集、端点、识别、回复、合成与播放接口。',920)
    stages=[('音频采集与传输',['浏览器 AudioWorklet → WebSocket','音频块 → 重采样 / 格式转换']),('VAD 与端点逻辑',['Silero VAD：检测语音区间','静音阈值与上下文 → 提交一段音频']),('ASR → 文字',['Whisper / SenseVoice','音频 → 转录；保留端点与时间戳']),('LLM → 回复文本',['读取转录与任务上下文','生成可供 TTS 合成的文本']),('TTS 与播放',['Fish Audio S1：文本 → 音频块','网络传输 → 播放缓冲 → 扬声器'])]
    for i,(t,ls) in enumerate(stages):
        y=20+i*180;panel(f,100,y,700,t,ls,145)
        if i<4:down(f,450,y+145,y+180)
    f.save('fig6-6.svg')


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
    f.save('fig6-7.svg')


def queueing():
    f=Figure('排队延迟曲线','M/M/1 示例中利用率与平均系统逗留时间的关系。',640)
    panel(f,120,20,720,'M/M/1 单服务台模型',['泊松到达 · 指数服务时间 · 平均服务时间 S = 1 s','ρ = λS < 1；平均总时间 W = S / (1 − ρ)'],145)
    ox,oy,w,h=130,545,690,310
    f.path([(ox,oy),(850,oy)],True);f.path([(ox,oy),(ox,205)],True)
    for rho in [0,.2,.4,.6,.8,1]:
        x=ox+rho*w;f.path([(x,oy),(x,oy+6)]);f.text(x,oy+35,str(rho),20)
    for val in [0,2,4,6,8,10]:
        y=oy-val*h/10;f.path([(ox-5,y),(ox,y)]);f.text(100,y+7,str(val),20)
    pts=[(ox+r*w,oy-h/10/(1-r)) for r in [i/100 for i in range(91)]]
    f.path(pts)
    for r,label,dx,dy in [(.5,'ρ = 0.5：W = 2 s',-5,-27),(.8,'ρ = 0.8：W = 5 s',-105,-20)]:
        x=ox+r*w;y=oy-h/10/(1-r);f.box(x-3,y-3,6,6,'#333333');f.text(x+dx,y+dy,label,20)
    f.text(340,215,'平均总时间 W / s',22);f.text(700,620,'利用率 ρ',22)
    f.save('fig6-8.svg')


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
    f.save('fig6-10.svg')


def computer_loop():
    f=Figure('Computer Use Agent 的感知-思考-行动循环','截图、动作决策、执行及新观测回流。',720)
    panel(f,65,20,770,'① 获取观测',['桌面 / 浏览器 / 应用截图','记录画面尺寸与界面状态'],135)
    down(f,450,155,190)
    panel(f,65,190,770,'② 模型决策',['输入：截图 + 任务 + 历史与当前状态','输出示例：click(512, 250)，再输入 weather'],135)
    down(f,450,325,360)
    panel(f,65,360,770,'③ 执行动作',['工具层校验与调度 → xdotool / Playwright','鼠标：移动、点击、拖拽 · 键盘：输入、组合键','滚动：改变视口 · 等待：接收界面响应'],170)
    down(f,450,530,565)
    panel(f,65,565,770,'④ 读取动作后的状态',['界面变化 → 获取新截图 → 检查目标是否达成'],100)
    f.path([(65,615),(25,615),(25,85),(65,85)],True)
    f.save('fig6-11.svg')


def computer_tools():
    f=Figure('Computer Use 动作空间','图形界面、命令执行、文件编辑与表单操作示例。',1080)
    panel(f,20,20,860,'图形界面工具 computer',['鼠标：mouse_move · left / right / middle_click','double / triple_click · left_click_drag · left_mouse_down / up','键盘：type · key · hold_key','滚动：scroll（方向、步数与修饰键）','观测：screenshot · cursor_position；等待：wait'],265)
    panel(f,20,325,410,'命令执行 bash',['持久终端会话','完成标记与超时处理','stdout / stderr 与退出状态'],195)
    panel(f,470,325,410,'文件编辑接口',['view · create · str_replace','insert · undo_edit','匹配校验 → 修改 → 差异检查'],195)
    panel(f,20,560,860,'图像与坐标转换',['实际屏幕 → 工具输出图像 → 模型坐标','逆变换 → 桌面坐标 → 执行器'],140)
    down(f,450,700,735)
    panel(f,20,735,860,'填写表单示例',['① screenshot：获取页面','② 模型定位姓名框 → mouse_move(324, 156)','③ left_click：获取输入焦点','④ type("John Smith")：输入姓名','⑤ 新截图：确认字段内容'],290)
    f.save('fig6-12.svg')


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
    panel(f,20,510,860,'结构化候选列表',['[1] <input type="text" placeholder="Search"','      aria-label="Search" />','[2] <button id="submit-btn" aria-label="Submit form" />','[3] <input type="text" placeholder="Enter your name" value="" />','[4] <a href="/docs" aria-label="Documentation" />'],265)
    down(f,450,775,815)
    panel(f,20,815,860,'选择与执行',['模型选择 [2] → 解析元素引用或坐标','检查可见与可交互 → 点击 Submit → 获取新状态'],150)
    down(f,450,965,1000)
    panel(f,20,1000,860,'映射更新',['刷新、滚动或动态插入 → 更新候选与编号','缺少结构化信息 → 结合视觉标注或坐标预测'],150)
    f.save('fig6-13.svg')


def coordinates():
    f=Figure('分辨率匹配与双向坐标缩放','截图缩放、坐标逆映射与偏移参数。',925)
    panel(f,20,20,410,'实际屏幕',['2560 × 1440','桌面坐标原点与显示缩放'],145)
    panel(f,470,20,410,'工具输出截图',['1366 × 768','模型预测点：(683, 384)'],145)
    f.path([(430,90),(470,90)],True)
    panel(f,20,205,860,'分别按宽、高映射',['x = 683 × 2560 / 1366 = 1280','y = 384 × 1440 / 768 = 720'],145)
    down(f,450,350,390)
    panel(f,20,390,860,'执行与验证',['将桌面点 (1280, 720) 交给执行器','点击 → 界面更新 → 新截图'],140)
    panel(f,20,570,860,'参考目标尺寸',['XGA：1024 × 768 · WXGA：1280 × 800','FWXGA：1366 × 768'],145)
    panel(f,20,755,860,'等比缩放与留白时的逆变换',['先减填充偏移，再除缩放系数','裁剪与多显示器：继续加回对应原点偏移'],145)
    f.save('fig6-14.svg')


def audio_architecture():
    f=Figure('端到端多模态语音模型架构对比','转录级联、直接音频输入输出、模型内部模块与全双工时序。',1130)
    panel(f,20,20,860,'转录级联',['音频 → VAD / 端点 → ASR → 文本 → LLM → 文本 → TTS','检查接口：转录、回复文本、合成音频'],135)
    panel(f,20,195,860,'端到端音频路径',['音频与声学特征 → 模型 → 文本 / 音频输出','语速 · 音高 · 停顿 · 情绪 · 环境声'],135)
    panel(f,20,370,410,'OpenAI Realtime',['音频输入与生成','server_vad / semantic_vad','轮次结束 → 触发响应','打断 → 生成与播放状态协调'],215)
    panel(f,470,370,410,'Gemini Live',['音频输入与生成','自动活动检测 / 手动边界','检测用户活动与中途插话','已播与待播内容分别处理'],215)
    panel(f,20,625,410,'Qwen3-Omni',['多模态输入 → Thinker（MoE）','Talker → 多码本语音 token','流式解码 → 首帧起输出'],195)
    panel(f,470,625,410,'Step-Audio 2',['音频编码 → 语言模型','文本与音频 token → 语音','推理与工具调用参与对话'],195)
    panel(f,20,860,860,'全双工时序：Moshi',['用户音频流 ───────── 持续输入','模型音频流 ───────── 持续输出','文本流与音频流协调；时间对齐表示重叠与打断'],215)
    f.save('fig6-9.svg')


if __name__ == '__main__':
    events();strategies();email();cancellation();native_async()
    speech_pipeline();latency();queueing();audio_architecture();cognition()
    computer_loop();computer_tools();grounding();coordinates()
