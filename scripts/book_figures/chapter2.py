"""Chapter 2 diagrams, retaining concrete examples in print-friendly grayscale."""
from introduction import Figure


def local_model_tools():
    f = Figure('本地 LLM 工具调用架构',
               '温哥华时间与天气任务：客户端维护消息、调用本地模型并调度两个工具，再将观测回传模型。', 640)
    f.box(20,20,860,80,'#dedede')
    f.text(450,52,'用户请求',24,True)
    f.text(450,83,'查询温哥华当前时间与天气',22)
    f.path([(195,100),(195,150)],True)
    f.box(20,150,350,470,'#f2f2f2')
    f.text(195,188,'客户端 Harness',25,True)
    f.text(195,240,'组织 messages 与 tools',22)
    f.text(195,289,'保存模型回复与调用 ID',21)
    f.text(195,395,'解析与校验参数',22)
    f.text(195,441,'调度独立调用',22)
    f.text(195,537,'追加工具结果',22)
    f.text(195,583,'再次调用模型 → 最终回复',21)
    f.box(520,150,360,190,'#dedede')
    f.text(700,188,'本地 LLM 服务',25,True)
    f.text(700,229,'vLLM / Ollama',23)
    f.text(700,269,'Qwen3-0.6B',24,True)
    f.text(700,311,'推理 · 生成工具调用或回答',21)
    f.path([(370,220),(520,220)],True)
    f.text(445,207,'模型请求',20)
    f.path([(520,300),(370,300)],True)
    f.text(445,287,'模型响应',20)
    f.box(520,380,360,240,'#ffffff')
    f.text(700,419,'工具执行',25,True)
    f.text(700,462,'时间：America/Vancouver',21)
    f.text(700,502,'天气：Vancouver、celsius',21)
    f.text(700,550,'函数 / 外部 API',22)
    f.text(700,591,'返回时间、气温等观测',21)
    f.path([(370,447),(520,447)],True)
    f.text(445,433,'调用请求',20)
    f.path([(520,550),(370,550)],True)
    f.text(445,536,'执行结果',20)
    f.save('fig2-5.svg')


def context_example():
    f = Figure('上下文窗口的构成概览', '北京天气示例：系统指令、天气工具定义、带调用ID的历史、当前推理和回答生成位置。', 885)
    f.box(20,20,795,825,'#ffffff')
    sections = [
        (35,120,'系统提示词（System Prompt）',[
            'You are a helpful assistant. Answer concisely.',
            'Use tools for real-time information.']),
        (170,205,'工具定义（Tool Definitions）',[
            '{"name": "get_weather", "description": "查询城市天气",',
            ' "parameters": {"type": "object", "properties": {',
            '   "city": {"type": "string"}}, "required": ["city"]}}']),
        (390,220,'对话历史（Conversation History）',[
            'user：北京今天天气怎么样？',
            'assistant：call_1 → get_weather(city="北京")',
            'tool（call_1）：{"temp": "23°C", "conditions": "晴"}']),
        (625,125,'本轮推理（Reasoning）',[
            '<think>已获得北京天气，接下来汇总回答。</think>']),
    ]
    for y,h,title,lines in sections:
        f.box(35,y,765,h,'#f2f2f2')
        f.text(417,y+33,title,24,True)
        for j,line in enumerate(lines):
            f.text(417,y+72+j*34,line,20)
    f.box(35,765,765,65,'#dedede')
    f.text(417,805,'assistant：北京今天晴，气温 23°C…',22,True)
    f.path([(835,35),(855,35),(855,750),(835,750)])
    f.text(879,335,'上',20)
    f.text(879,370,'下',20)
    f.text(879,405,'文',20)
    f.text(879,440,'窗',20)
    f.text(879,475,'口',20)
    f.text(450,872,'当前生成位置',20)
    f.path([(450,850),(450,831)],True)
    f.save('fig2-1.svg')


def api_exchange():
    f = Figure('单轮 API 调用的请求与响应结构', 'Harness发送系统指令与用户问题，模型返回assistant消息。', 320)
    f.box(20,20,360,280)
    f.text(200,60,'请求 · Harness 构造',24,True)
    f.box(40,85,320,85,'#ffffff')
    f.text(200,118,'system',23,True)
    f.text(200,150,'助手身份与回答规则',21)
    f.box(40,190,320,85,'#ffffff')
    f.text(200,222,'user',23,True)
    f.text(200,255,'Hello, who are you?',22)
    f.path([(380,160),(520,160)],True)
    f.text(450,143,'模型 API',20)
    f.box(520,20,360,280,'#dedede')
    f.text(700,60,'响应 · 模型生成',24,True)
    f.box(540,100,320,160,'#ffffff')
    f.text(700,142,'assistant',23,True)
    f.text(700,192,"Hi! I’m a coding assistant…",20)
    f.save('fig2-2.svg')


def two_round_tools():
    f = Figure('两次模型 API 调用的完整交互序列', '温哥华时间与天气：模型产生两项独立调用，Harness执行并回传带ID的结果，模型再生成最终回答。', 780)
    f.box(20,20,860,100)
    f.text(450,56,'第一次模型调用',25,True)
    f.text(450,93,'messages：system + user    tools：时间工具 + 天气工具',22)
    f.path([(450,120),(450,157)],True)
    f.box(20,157,860,145,'#dedede')
    f.text(450,193,'assistant：tool_calls',24,True)
    f.text(450,235,'call_abc123 → get_current_time(timezone="America/Vancouver")',20)
    f.text(450,276,'call_def456 → get_weather(city="Vancouver", unit="celsius")',20)
    f.path([(450,302),(450,325),(230,325),(230,360)],True)
    f.path([(450,325),(670,325),(670,360)],True)
    for x,label,call,result in [(20,'时间工具','call_abc123','返回温哥华当前时间'),(460,'天气工具','call_def456','返回气温与天气状况')]:
        f.box(x,360,420,125,'#ffffff')
        f.text(x+210,394,label,23,True)
        f.text(x+210,431,call,21)
        f.text(x+210,466,result,21)
    f.text(450,348,'独立调用 · Harness 并行调度',20)
    f.path([(230,485),(230,516),(450,516)])
    f.path([(670,485),(670,516),(450,516),(450,550)],True)
    f.box(20,550,860,100)
    f.text(450,585,'第二次模型调用 · tools 保持不变',25,True)
    f.text(450,625,'原有 messages + assistant 调用消息 + 两条带 tool_call_id 的结果',20)
    f.path([(450,650),(450,683)],True)
    f.box(20,683,860,77,'#dedede')
    f.text(450,714,'assistant：最终回复（结束循环）',23,True)
    f.text(450,747,'“温哥华现在是……，天气……”',21)
    f.save('fig2-3.svg')


def context_layout():
    f = Figure('Agent 每次调用模型时的上下文构成', '相对稳定的系统指令与工具定义，以及按轮次追加的消息历史。', 340)
    f.box(20,20,860,120,'#dedede')
    f.text(450,55,'相对稳定的前缀',24,True)
    f.box(40,77,400,45,'#ffffff')
    f.box(460,77,400,45,'#ffffff')
    f.text(240,108,'System Prompt · 系统指令',21)
    f.text(660,108,'Tool Definitions · 工具定义',21)
    f.box(20,170,860,150,'#ffffff')
    f.text(450,205,'消息历史',24,True)
    labels=[('user',105),('assistant',277),('tool 结果',449),('user',621),('…',793)]
    for label,x in labels:
        f.box(x-65,232,130,60)
        f.text(x,270,label,21)
        if x<793: f.path([(x+65,262),(x+107,262)],True)
    f.save('fig2-4.svg')


def attention_example():
    f = Figure('注意力机制的直观理解', '四个语义单元示意：当前查询对各Key的权重为0.35、0.05、0.55、0.05；矩阵保留因果下三角。', 830)
    f.text(450,40,'① 当前查询与四个 Key',25,True)
    words=['北京','的','天气','怎么样']
    weights=[0.35,0.05,0.55,0.05]
    for j,(word,w) in enumerate(zip(words,weights)):
        x=20+j*225
        f.box(x,72,185,112,'#dedede' if j==2 else '#f2f2f2')
        f.text(x+92.5,109,word,25,True)
        f.text(x+92.5,154,f'Key · {w:.2f}',22)
        f.path([(x+92.5,184),(x+92.5,219),(450,219)])
    f.path([(450,267),(450,219)],True)
    f.box(310,267,280,75)
    f.text(450,297,'Query',21,True)
    f.text(450,327,'怎么样',24)
    f.text(450,395,'② 因果注意力矩阵',25,True)
    f.text(475,434,'Key →',21)
    f.text(78,491,'Query ↓',21)
    rows=[[1.0],[.3,.7],[.2,.1,.7],[.35,.05,.55,.05]]
    for j,word in enumerate(words): f.text(290+j*145,479,word,22)
    for i,row in enumerate(rows):
        y=505+i*76
        f.text(125,y+45,words[i],22)
        for j in range(4):
            x=220+j*145
            if j<=i:
                value=row[j];shade=round(248-95*value);color=f'#{shade:02x}{shade:02x}{shade:02x}'
                f.box(x,y,140,70,color)
                f.text(x+70,y+44,f'{value:.2f}',22,True)
            else:
                f.box(x,y,140,70,'#ffffff')
                f.text(x+70,y+44,'×',22)
    f.save('fig2-6.svg')


def template_sequence():
    f=Figure('Chat Template 的 Token 结构','保留北京天气示例与Qwen消息起止标记。',500)
    f.box(20,20,375,460)
    f.text(207,58,'结构化 API 消息',25,True)
    for y,role,body in [(100,'system','You are a helpful assistant.'),(220,'user','北京今天天气怎么样？'),(340,'assistant','待生成')]:
        f.box(40,y,335,100,'#ffffff')
        f.text(207,y+35,role,23,True)
        f.text(207,y+75,body,20)
    f.path([(395,250),(500,250)],True)
    f.text(447,205,'Chat',20)
    f.text(447,234,'Template',20)
    f.box(500,20,380,460,'#dedede')
    f.text(690,58,'线性 token 序列',25,True)
    lines=['<|im_start|>system','You are a helpful assistant.','<|im_end|>','<|im_start|>user','北京今天天气怎么样？','<|im_end|>','<|im_start|>assistant']
    for j,line in enumerate(lines): f.text(690,114+j*49,line,20)
    f.save('fig2-8.svg')


def template_boundaries():
    f=Figure('API 消息到模型 Token 流的转换','两条消息经模板序列化，角色和起止标记界定边界，assistant标记后开始生成。',550)
    f.box(20,20,860,140)
    f.text(450,56,'API 消息',24,True)
    f.text(450,101,'{"role": "system", "content": "你是助手"}',22)
    f.text(450,139,'{"role": "user", "content": "你好"}',22)
    f.path([(450,160),(450,225)],True)
    f.text(595,201,'Chat Template',21)
    f.box(20,225,860,305,'#ffffff')
    f.text(450,263,'模型输入',24,True)
    for y,role,body in [(285,'system','你是助手'),(370,'user','你好')]:
        f.box(40,y,240,55,'#dedede');f.text(160,y+36,'<|im_start|>'+role,20)
        f.box(305,y,290,55);f.text(450,y+36,body,23)
        f.box(620,y,240,55,'#dedede');f.text(740,y+36,'<|im_end|>',20)
        f.path([(280,y+27),(305,y+27)],True);f.path([(595,y+27),(620,y+27)],True)
    f.text(265,491,'<|im_start|>assistant',22,True)
    f.path([(430,484),(525,484)],True)
    f.text(665,491,'从此处开始生成',22)
    f.save('fig2-9.svg')


def prefix_reuse():
    f=Figure('Prompt Cache：跨请求复用前缀的 KV Cache','三次请求对比：共同系统指令和工具定义可复用；在最前部插入时间戳改变后续前缀。',600)
    rows=[(20,'请求 1','System Prompt + Tools','user：天气如何？','首次处理（示例前缀：1200 token）','#ffffff'),
          (210,'请求 2','System Prompt + Tools','user：时间几点？','复用共同前缀','#dedede'),
          (400,'请求 3','10:30:45 + System Prompt + Tools','user：天气如何？','前缀改变，重新处理','#ffffff')]
    for y,title,prefix,query,status,fill in rows:
        f.box(20,y,860,160)
        f.text(96,y+35,title,23,True)
        f.box(40,y+55,545,57,fill);f.text(312,y+92,prefix,22)
        f.box(610,y+55,250,57,'#ffffff');f.text(735,y+92,query,21)
        f.text(312,y+145,status,21)
        f.text(735,y+145,'→ 生成回答',21)
    f.path([(312,180),(312,210)],True)
    f.path([(312,370),(312,400)],True)
    f.save('fig2-10.svg')


def skills_disclosure():
    f=Figure('Skills 渐进式披露机制','PPTX示例：从能力目录选择制作流程，继续读取HTML指南、XML参考或调用预览脚本。',760)
    f.box(20,20,860,145,'#dedede')
    f.text(450,56,'第一层 · 元数据目录',25,True)
    f.text(450,100,'pptx：创建、编辑 PowerPoint 演示文稿',22)
    f.text(450,139,'pdf：提取、分析 PDF 文档',22)
    f.path([(450,165),(450,225)],True)
    f.text(655,203,'任务：从论文生成 PPT',21)
    f.box(20,225,860,230)
    f.text(450,261,'第二层 · SKILL.md 核心流程',25,True)
    f.text(450,304,'读取文本：markitdown',22)
    f.text(450,348,'编辑已有 PPTX：解包 → 修改 XML → 重新打包',22)
    f.text(450,392,'新建 PPTX：读取 HTML 转换指南 → 生成演示文稿',22)
    f.text(450,435,'预览与检查：调用捆绑脚本',22)
    f.path([(450,455),(450,505)])
    f.path([(160,545),(160,505),(740,505),(740,545)],True)
    f.path([(450,505),(450,545)],True)
    f.path([(160,505),(160,545)],True)
    for x,title,body in [(20,'html2pptx.md','HTML 模板\n转换流程'),(310,'格式参考','XML 结构\n编辑细则'),(600,'捆绑脚本','生成缩略图\n检查版面')]:
        f.box(x,545,280,190,'#ffffff')
        f.text(x+140,583,'第三层 · 按需使用',21)
        f.text(x+140,631,title,22,True)
        f.text(x+140,678,body,21)
    f.save('fig2-11.svg')


def skills_trajectory():
    f=Figure('启用 Skills 后 Agent Trajectory 的完整结构','以模型自主激活PPTX为例，目录先可见，激活后正文进入会话，再读取论文与生成HTML。',900)
    f.box(20,20,860,100,'#dedede')
    f.text(450,53,'系统指令与工具定义',24,True)
    f.text(450,94,'system：助手规则    tools：Skill、Read、Bash、Write…',21)
    rows=[
        ('user','帮我从论文 PDF 生成 PPT'),
        ('Harness 目录','可用 Skills：pdf、pptx…'),
        ('assistant','call_1 → Skill(skill="pptx")'),
        ('tool · call_1','确认激活 PPTX Skill'),
        ('user · Harness 注入','PPTX Skill 正文：流程、详细指南与脚本入口'),
        ('assistant','call_2 → Read（论文 PDF）'),
        ('tool · call_2','论文的文本与图表内容'),
        ('assistant','call_3 → Write（演示文稿 HTML）'),
        ('tool · call_3','写入结果：12,345 bytes'),
    ]
    for j,(role,body) in enumerate(rows):
        y=151+j*78
        f.box(20,y,860,62,'#dedede' if j in [1,4] else '#f2f2f2')
        f.text(165,y+38,role,20,True)
        f.path([(305,y+10),(305,y+52)])
        f.text(593,y+38,body,20)
        if j<8: f.path([(450,y+62),(450,y+78)],True)
    f.text(450,884,'… 后续工具交互 …',21)
    f.save('fig2-12.svg')


def skills_cache():
    f=Figure('KV Cache 随 Agent Trajectory 增长的演化','三次请求保留已加载的目录与Skill正文，后续追加论文读取与HTML写入结果；区分复用前缀和新增内容。',790)
    labels=['system','tools','用户任务','Skill 目录','Skill(pptx) 调用','激活结果','Skill 正文','读取论文调用','读取结果','写入 HTML 调用','写入结果']
    for col,(title,subtitle,limit,old) in enumerate([('请求 1','加载 Skill 后',7,0),('请求 2','读取论文后',9,7),('请求 3','写入 HTML 后',11,9)]):
        x=20+col*295
        f.text(x+135,40,title,24,True)
        f.text(x+135,76,subtitle,21)
        for j,label in enumerate(labels):
            y=100+j*54
            if j>=limit:
                f.text(x+135,y+32,'—',22)
                continue
            f.box(x,y,270,47,'#dedede' if j<old else '#ffffff')
            f.text(x+104,y+31,label,20)
            f.text(x+239,y+31,'复用' if j<old else '新增',20)
    f.box(40,720,28,28,'#dedede');f.text(213,742,'可复用的稳定前缀',20)
    f.box(430,720,28,28,'#ffffff');f.text(590,742,'本次新增内容',20)
    f.save('fig2-13.svg')


def status_comparison():
    f=Figure('Agent 状态栏架构','Xfinity砍价示例：保留原始电话与搜索轨迹，运行时汇总次数、任务状态和时间。',790)
    for x,title in [(20,'原始轨迹'),(470,'轨迹 + 状态摘要')]:
        f.box(x,20,410,745,'#ffffff');f.text(x+205,58,title,25,True)
    events=[('system','助手规则 + 工具定义'),('user','联系 Xfinity 砍价'),('phone_call · 第 1 次','等待 45 分钟，未接通'),('web_search','Xfinity deals → 搜索结果'),('phone_call · 第 2 次','接通，报价 $65/月'),('phone_call · 第 3 次','确认降价至 $59/月'),('user','能不能再打一次催一下？')]
    for j,(role,body) in enumerate(events):
        y=87+j*92;f.box(35,y,380,80)
        f.text(225,y+30,role,21,True);f.text(225,y+62,body,20)
    for y,title,body in [(87,'system / user','相同规则与砍价任务'),(188,'assistant / tool','相同电话与搜索记录'),(289,'user','能不能再打一次催一下？')]:
        f.box(485,y,380,80);f.text(675,y+30,title,21,True);f.text(675,y+62,body,20)
    f.path([(675,369),(675,403)],True)
    f.box(485,403,380,337,'#dedede')
    for j,line in enumerate(['<agent_status>','phone_call：3 次','Xfinity：3/3，已达上限','TODO：联系商家 ✓','TODO：确认降价 ✓','当前时间：2025-09-14 10:30','当前状态：等待用户确认','</agent_status>']):
        f.text(675,442+j*39,line,20,j in [0,7])
    f.save('fig2-14.svg')


def status_position():
    f=Figure('Agent 状态栏在 API 消息列表中的插入位置','取消Xfinity套餐示例：原始交互与用户追问后，Harness追加当前状态摘要。',770)
    f.box(20,20,860,95,'#dedede')
    f.text(450,54,'系统指令与工具定义',24,True)
    f.text(450,93,'system：客服规则    tools：phone_call、web_search…',21)
    rows=[('user','帮我取消 Xfinity 套餐'),('assistant','call_1 → phone_call(company="Xfinity")'),('tool · call_1','通话记录：套餐仍在合约期内'),('assistant','说明合约条件与下一步安排'),('…','后续电话与搜索交互'),('user','能不能再打一次催一下？')]
    for j,(role,body) in enumerate(rows):
        y=139+j*68;f.box(20,y,860,56)
        f.text(135,y+35,role,20,True);f.text(563,y+35,body,21)
    f.path([(450,535),(450,566)],True)
    f.box(20,566,860,140,'#dedede')
    f.text(450,599,'user · Harness 生成的状态摘要',23,True)
    f.text(450,637,'<agent_status> Xfinity 已呼叫 3/3 次',21)
    f.text(450,677,'TODO：取消套餐（in_progress） </agent_status>',21)
    f.path([(450,706),(450,738)],True)
    f.text(450,762,'模型继续生成',22)
    f.save('fig2-15.svg')


def compression_results():
    f=Figure('上下文压缩策略对比','六组既有运行汇总；token用量、字符比率、轮数及最终回复状态分列呈现。',570)
    headers=[(135,'策略'),(330,'累计 token'),(490,'字符比率'),(615,'轮数'),(765,'最终回复')]
    f.box(20,20,860,70,'#dedede')
    for x,label in headers:f.text(x,63,label,22,True)
    rows=[('无压缩','166,043','102.1%','5','未生成'),('个体摘要','276,608','10.9%','12','已生成'),('组合摘要','93,449','4.3%','10','已生成'),('上下文感知','40,157','3.0%','7','已生成'),('感知 + 引用','222,992','4.1%','10','已生成'),('自适应窗口','174,601','102.4%','7','已生成')]
    for j,row in enumerate(rows):
        y=100+j*74;f.box(20,y,860,64,'#f2f2f2' if j%2==0 else '#ffffff')
        for (x,_),value in zip(headers,row):f.text(x,y+40,value,22)
    f.save('fig2-16.svg')


def compression_flows():
    f=Figure('六种压缩策略的处理流程','六种策略保留各自的材料组织、任务上下文、来源链接和窗口阈值处理。',850)
    rows=[('① 无压缩','原始搜索结果','直接保留','完整结果'),('② 个体摘要','各页面内容','分别生成 2–3 段摘要','逐页摘要'),('③ 组合摘要','一批搜索结果','合并、去重与摘要','综合摘要'),('④ 上下文感知','搜索结果 + 查询 + 已知信息','按任务提取','相关事实与缺口'),('⑤ 感知 + 引用','搜索结果 + 查询 + 已知信息','摘要并保留 URL','事实与来源'),('⑥ 自适应窗口','当前输入占用','≤80% 保留；>80% 批量摘要','标记已压缩结果')]
    for j,(name,inp,action,out) in enumerate(rows):
        y=20+j*137
        f.box(20,y,860,120,'#ffffff')
        f.text(160,y+34,name,23,True)
        f.text(605,y+34,action,21)
        f.box(40,y+52,365,50);f.text(222,y+85,inp,20)
        f.path([(405,y+77),(490,y+77)],True)
        f.box(490,y+52,370,50,'#dedede');f.text(675,y+85,out,21)
    f.save('fig2-17.svg')


if __name__ == '__main__':
    local_model_tools()
    context_example()
    api_exchange()
    two_round_tools()
    context_layout()
    attention_example()
    template_sequence()
    template_boundaries()
    prefix_reuse()
    skills_disclosure()
    skills_trajectory()
    skills_cache()
    status_comparison()
    status_position()
    compression_results()
    compression_flows()
