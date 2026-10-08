"""Chapter 10 grayscale figures, preserving roles, messages and concrete examples."""
from introduction import Figure
from chapter5 import panel, down


def contexts():
    f=Figure('共享上下文与不共享上下文对比','CSV脚本角色切换与书籍翻译的独立上下文交接。',1060)
    f.text(225,35,'沿用历史：CSV 分析脚本',24,True)
    f.text(675,35,'独立上下文：章节翻译',24,True)
    left=[('需求分析师',['指令：确认需求与输入条件','工具：ask_question / save_req','用户：写一个 CSV 分析脚本','提问：需要处理哪些文件类型？']),('软件工程师',['指令：按已确认需求实现','工具：write_file / execute_code','写入 analyze.py','执行测试，读取结果']),('代码审查员',['指令：检查代码质量与安全性','工具：run_linter / run_tests','linter → 2 条警告','检查警告、测试与修复结果'])]
    right=[('Glossary Agent',['指令：识别术语与约定译法','工具：search_dict / write_file','产物：术语表 glossary.json']),('Translation Agent',['指令：按术语表翻译本章','工具：read_file / write_file','输入：章节 + 术语表 + 指南','产物：章节译文']),('Proofreading Agent',['指令：检查术语与行文','工具：read_file / write_file','输入：译文 + 术语表','产物：审校报告'])]
    for i in range(3):
        y=65+i*270
        panel(f,20,y,410,*left[i],230);panel(f,470,y,410,*right[i],230)
        if i<2:down(f,225,y+230,y+270);down(f,675,y+230,y+270)
    f.save('fig10-1.svg')


def filesystem():
    f=Figure('Agent 虚拟文件系统的四类区域挂载结构','统一文件接口与四类权限和生命周期，以及用户和外部资源入口。',1030)
    panel(f,20,20,410,'Agent A / Agent B',['按身份与任务获得访问范围'],110)
    panel(f,470,20,410,'用户',['上传材料 / 下载交付物'],110)
    down(f,225,130,180);down(f,675,130,180)
    panel(f,20,180,860,'虚拟文件系统',['统一接口：read_file · write_file · list_dir','挂载与授权 → 分区访问'],145)
    for x in [225,675]:down(f,x,325,370)
    panel(f,20,370,410,'专属工作区 · Scratchpad',['临时文件 · 草稿 · 日志','默认限所属 Agent 读写','随实例清理或按策略归档','各实例独立目录'],205)
    panel(f,470,370,410,'协作空间 · Shared Workspace',['术语表 · 代码 · 交付物','获授权成员与用户可见','随任务持久保存','版本检查 / 锁 / worktree'],205)
    panel(f,20,620,410,'外部挂载资源',['Google Drive / Notion','适配器调用源系统 API','按授权读取或写回','超时 · 缓存 · 版本检查'],205)
    panel(f,470,620,410,'系统内置资源',['Skills · 模板 · 手册','固定版本 · 只读共享','先目录，后按需读取','版本切换时保持任务一致'],205)
    f.path([(450,325),(450,590),(225,590),(225,620)],True)
    f.path([(450,590),(675,590),(675,620)],True)
    f.save('fig10-2.svg')


def proposer_reviewer():
    f=Figure('提议者—审核者循环','论文内容、渲染、逐页反馈和三轮修改示例。',1060)
    panel(f,20,20,410,'Proposer · 生成与修改',['输入：论文扩展摘要（2000字）','Slidev：theme: academic','内容：Transformer 自注意力','公式：Q · Kᵀ / √d','展开：多头注意力及其作用'],245)
    panel(f,470,20,410,'Reviewer · 视觉审核',['Slidev → PDF / PNG','Vision LLM 检查逐页渲染','输出：页码 / 问题 / 严重程度','当前轮：截图与检查要求','下一轮：检查修改后的页面'],245)
    f.path([(225,265),(225,310),(675,310),(675,265)],True);f.text(450,298,'渲染页面',20)
    f.path([(870,220),(890,220),(890,380),(10,380),(10,220),(20,220)],True);f.text(450,367,'结构化反馈',20)
    panel(f,20,425,860,'第一轮审核反馈示例',['P3：文字过密 · 高 → 拆分内容','P7：字号偏小 · 中 → 增大字号并调整布局','P11：颜色区分弱 · 低 → 增加线型与标签'],180)
    for i,(t,ls) in enumerate([('第 1 轮',['12 页','5 个问题']),('第 2 轮',['14 页','2 个问题']),('第 3 轮',['14 页','0 个问题'])]):
        panel(f,20+i*300,650,260,t,ls,145)
        if i<2:f.path([(280+i*300,725),(320+i*300,725)],True)
    f.save('fig10-3.svg')


def sequential():
    f=Figure('Manager 顺序协调','Manager 分别调用收集、分析和写作成员，并接收其结果。',990)
    panel(f,20,20,860,'Manager · 规划与调度',['工具：call_agent_A / call_agent_B / call_agent_C','辅助工具：search / write_file','根据返回结果决定下一步'],180)
    roles=[('Agent A · 资料收集',['搜索技术文档','提取关键事实与来源'],'资料与来源'),('Agent B · 数据分析',['对比方案与统计数据','整理结论及其依据'],'分析结果'),('Agent C · 报告生成',['组织报告结构','按要求排版与写入'],'报告文件')]
    f.path([(125,200),(125,930)])
    for i,(title,lines,result) in enumerate(roles):
        y=255+i*225
        panel(f,300,y,550,title,lines,150)
        f.path([(125,y+30),(300,y+30)],True)
        f.text(210,y+15,f'{i+1}. 调用',20)
        f.path([(300,y+120),(125,y+120)],True)
        f.text(210,y+155,result,20)
    f.save('fig10-4.svg')


def translation():
    f=Figure('书籍翻译 Agent 架构','术语、分章翻译、审校与共享交付物。',1080)
    panel(f,20,20,860,'Manager',['拆分章节 · 跟踪进度 · 处理错误 · 汇总译文'],110)
    f.path([(450,130),(450,150),(225,150),(225,175)],True)
    f.path([(450,150),(675,150),(675,175)],True)
    panel(f,20,175,410,'Glossary Agent',['输入：原书与术语要求','attention → 注意力','transformer → Transformer','backprop → 反向传播','输出：JSON 术语表'],245)
    panel(f,470,175,410,'Translation Agent × N',['输入：章节 + 术语表 + 指南','逐章独立组织上下文','例：Query · Keyᵀ','计算查询与键之间的相似度','输出：章节译文'],245)
    f.path([(430,300),(470,300)],True)
    down(f,675,420,465)
    panel(f,470,465,410,'Proofreading Agent',['按章节和索引读取材料','P3：注意力误译为“关注”','P8：长句拆分建议','输出：定位明确的审校报告'],220)
    panel(f,20,465,410,'译文修订',['译者读取对应章节反馈','结合原文核对术语','修改译文并记录版本','审校员复查修改结果'],220)
    f.path([(470,590),(430,590)],True)
    panel(f,20,745,860,'共享产物',['术语表：glossary.json','章节译文：chapter{n}_zh.md','审校报告：review_report.md','翻译指南：translation_guide.md'],215)
    for x in [225,675]:down(f,x,685,745)
    f.save('fig10-5.svg')


def parallel():
    f=Figure('Manager 并行协调','并行成员状态、消息队列与后续任务依赖。',1010)
    panel(f,20,20,860,'Manager',['分配任务 · 接收事件 · 更新依赖 · 汇总结果'],110)
    down(f,450,130,175)
    panel(f,20,175,860,'消息队列 / 事件总线',['消息字段：type · source · target · task_id · payload'],110)
    for x in [125,345,565,785]:down(f,x,285,335)
    for i,(title,lines) in enumerate([('Agent 1',['资料收集','运行中']),('Agent 2',['数据分析','运行中']),('Agent 3',['图表生成','已完成']),('Agent 4',['格式校验','等待依赖'])]):
        panel(f,20+i*220,335,200,title,lines,150)
    panel(f,20,545,860,'事件与状态变化示例',['start_task → Agent 1：检索 arXiv，主题 LLM Agent','data_ready：Agent 1 → Agent 2，file: raw_data.json','task_completed ← Agent 3：图表已保存','start_task → Agent 4：depends_on: [agent_2, agent_3]'],220)
    f.save('fig10-6.svg')


def phone_computer():
    f=Figure('Phone 与 Computer 双 Agent 架构','两条独立运行循环通过结构化事件交换字段与执行结果。',1130)
    panel(f,20,20,410,'Phone Agent · Node.js',['WebRTC：双向语音','语音 → Silero VAD → ASR','LLM：理解意图与提取字段','TTS：合成追问和确认','持续处理通话事件'],245)
    panel(f,470,20,410,'Computer Agent · Python',['截图 → Vision LLM','读取表单与当前页面状态','规划字段与操作顺序','click / type / submit','读取页面反馈并验证'],245)
    f.path([(675,265),(675,320),(225,320),(225,265)],True)
    f.text(450,307,'发起通话：purpose / required_info',20)
    panel(f,20,370,860,'WebSocket · 双向消息通道',['任务标识 · 消息类型 · 字段数据 · 当前状态'],110)
    for x in [225,675]:
        f.path([(x,265),(x,285),(10 if x==225 else 890,285),(10 if x==225 else 890,425),(20 if x==225 else 880,425)],True)
    panel(f,20,530,410,'Phone → Computer',['info_collected','姓名：张三（示例）','已取得：姓名、联系方式','继续收集：证件号码'],220)
    panel(f,470,530,410,'Computer → Phone',['fill_error / format_invalid','字段：证件号码','问题：位数与格式不符','请求：请用户再次确认'],220)
    panel(f,470,805,410,'Phone Agent 的下一步',['向用户澄清所需字段','回读并确认识别结果','发送已确认的字段值','收集完成：task_completed'],220)
    panel(f,20,805,410,'Computer Agent 的下一步',['按确认值更新表单','检查页面校验结果','按授权提交并核对回执','保存提交结果并结束任务'],220)
    down(f,225,750,805);down(f,675,750,805)
    f.save('fig10-7.svg')


def search_cancel():
    f=Figure('并行 Web Scraping 架构','十个成员搜索、首个有效结果结算、取消与回执。',1120)
    panel(f,20,20,860,'Manager',['目标：查找符合条件的教师','派发：10 个成员，各自搜索一个学院网站'],145)
    down(f,450,165,205)
    panel(f,20,205,860,'并行搜索成员',['Agent 1 … Agent 10：独立浏览器会话','Agent 1：计算机 · Agent 2：数学 · Agent 3：物理'],145)
    panel(f,20,395,860,'协作时序示例',['0 s：Manager 启动 10 个搜索任务','12 s：Agent 2 返回无匹配，其余成员继续','18 s：Agent 3 发送 target_found，附候选与来源','Manager 验证候选 → 原子结算首个有效结果','18.1 s：广播 terminate，取消其余运行中的任务','19 s：收到取消回执，回收浏览器与任务资源'],280)
    down(f,450,350,395)
    panel(f,20,725,410,'有效结果示例',['姓名：张伟（示例）','院系：物理学院 · 职位：教授','方向：量子计算','附：来源页面与匹配依据'],220)
    panel(f,470,725,410,'结束状态',['完成：已找到并验证目标','无匹配：已完成分配范围','超时：达到两分钟上限','取消：确认停止并释放资源'],220)
    f.save('fig10-8.svg')


def metagpt():
    f=Figure('MetaGPT 多 Agent 协作网络','五种角色通过共享产物和消息订阅推进任务，测试反馈返回工程师。',1110)
    roles=[('产品经理',['PRD：用户故事、优先级、验收条件','示例：5 条用户故事']),('架构师',['架构：FastAPI + React','接口：OpenAPI · 数据库 Schema']),('项目经理',['拆分任务、目标文件与依赖','按模块分配开发工作']),('工程师 × 3',['用户模块 · 订单模块 · 支付模块','读取接口与任务，编写代码']),('QA 工程师',['pytest 单元测试 · API 集成测试','输出测试结果与问题报告'])]
    for i,(title,lines) in enumerate(roles):
        y=20+i*175
        panel(f,20,y,630,title,lines,145)
        if i<4:down(f,335,y+145,y+175)
    f.path([(650,790),(675,790),(675,617),(650,617)],True)
    f.text(785,788,'测试失败',20);f.text(785,820,'返回修复',20)
    f.save('fig10-9.svg')


def town():
    f=Figure('AI 小镇架构','Isabella 的记忆条目、跨事件反思及一天计划示例。',1090)
    panel(f,20,20,860,'Isabella Rodriguez · Hobbs 咖啡馆店主',['性格：友善、热情 · 当前目标：筹备情人节派对'],110)
    down(f,450,130,175)
    panel(f,20,175,860,'记忆流 · 条目示例',['08:30 开店：重要性 4，近因性 0.60','09:15 与 Klaus 交谈：重要性 5，近因性 0.70','10:00 筹划派对：重要性 9，近因性 0.80','11:30 邀请 Maria：重要性 8，近因性 0.85','14:00 请 Maria 帮忙：重要性 7，近因性 0.90','检索：综合近因性、重要性及与当前问题的相关性'],280)
    f.path([(450,455),(450,475),(225,475),(225,500)],True)
    f.path([(450,475),(675,475),(675,500)],True)
    panel(f,20,500,410,'反思 · 跨事件归纳',['谁常来咖啡店？','Maria、Klaus、Tom','谁可能参加派对？','常客及其朋友','谁能协助准备？Maria'],245)
    panel(f,470,500,410,'规划 · 一天安排示例',['08:00 早餐 · 08:30 开店','12:00 邀请朋友','14:00 装饰场地','16:00 准备食物','18:00 举办派对'],245)
    f.path([(430,625),(470,625)],True)
    panel(f,20,805,860,'小镇中的社会互动',['25 个 Agent，模拟两天的生活','对话传播：派对邀请、Sam 竞选市长','记忆与关系：认出熟人、延续摄影项目的话题','行动：安排活动、邀请朋友、按约赴会'],220)
    down(f,675,745,805)
    f.save('fig10-10.svg')


def werewolf():
    f=Figure('语音狼人杀 Agent 系统','裁判维护规则和私有信息，玩家通过语音与角色动作参与游戏。',1150)
    panel(f,20,20,860,'裁判 · 确定性游戏代码',['夜晚 → 白天 → 投票 → 结算','维护角色、存活状态、行动权限与胜负条件'],145)
    f.path([(450,165),(450,185),(225,185),(225,205)],True)
    f.path([(450,185),(675,185),(675,205)],True)
    f.path([(450,185),(450,410),(225,410),(225,435)],True)
    f.path([(450,410),(675,410),(675,435)],True)
    panel(f,20,205,410,'狼人 × 2',['可见：自身身份与狼队友','夜间：共同选择目标','策略：伪装村民、跟票保护'],185)
    panel(f,470,205,410,'预言家 × 1',['可见：自身身份与查验结果','夜间：选择一名玩家查验','策略：择机公开身份与查验'],185)
    panel(f,20,435,410,'女巫 × 1',['可见：身份、药剂及规则内提示','夜间：按规则使用解药或毒药','策略：根据局势决定用药时机'],185)
    panel(f,470,435,410,'村民 × 2',['可见：自身身份与公开信息','依据：发言、投票、公布的结果','白天：推理、讨论与投票'],185)
    panel(f,20,675,860,'信息分发与动作检查',['公开频道：发言、投票及按规则公布的结果','角色私有频道：查验、狼队协商、女巫提示','裁判按身份、阶段、存活状态检查动作','每位玩家的上下文仅接收其有权获取的信息'],220)
    panel(f,20,945,860,'语音交互 · 六人配置示例',['1 名真人 + 5 名 AI，随机分配上述角色','玩家语音 → ASR → Agent / 裁判 → TTS → 音频','按阶段轮流发言与行动；满足胜负条件即结算'],175)
    f.save('fig10-11.svg')


if __name__=='__main__':
    contexts();filesystem();proposer_reviewer();sequential();translation()
    parallel();phone_computer();search_cancel();metagpt();town();werewolf()
