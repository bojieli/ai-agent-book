"""Chapter 3 grayscale teaching figures, preserving examples and mechanisms."""
from introduction import Figure


def roadmap():
    f = Figure('本章知识脉络', '用户记忆与共享知识库通过检索技术连接，并组合关键事实与按需细节。', 690)
    for x, title, lines in [
        (20, '用户记忆', '记录层次 · 三层次评估\n四种格式 · 可执行状态\n情景 · 语义 · 程序记忆\nMem0 · Memobase\n压缩整理 · 日志脱敏'),
        (470, '共享知识库', '文档分块 · 多模态材料\n稠密 / 稀疏 · 混合检索\nRAPTOR · GraphRAG\n目录导航 · Agentic RAG\n上下文前缀 · 案例知识提取'),
    ]:
        f.box(x,20,410,290,'#ffffff')
        f.box(x,20,410,60,'#dedede')
        f.text(x+205,59,title,25,True)
        f.text(x+205,120,lines,21)
        f.path([(x+205,310),(x+205,350)],True)
    f.box(20,350,860,100)
    f.text(450,386,'共同使用：检索与索引',24,True)
    f.text(450,425,'分块 · 向量 / 关键词 · 融合 · 重排序',22)
    f.path([(450,450),(450,490)],True)
    f.box(20,490,860,175,'#ffffff')
    f.text(450,530,'双层记忆',25,True)
    f.box(45,555,385,80)
    f.text(237,587,'结构化卡片',22,True)
    f.text(237,620,'关键事实与关系',20)
    f.box(470,555,385,80)
    f.text(662,587,'上下文感知检索',22,True)
    f.text(662,620,'按需取回原始细节',20)
    f.save('fig3-1.svg')


def formats():
    f = Figure('四种记忆策略对比', '四种记忆格式保留不同粒度的事实、背景、字段与关系。', 780)
    cards = [
        (20,20,'Simple Notes','用户邮箱：john@example.com\n公司：TechCorp\n职位：高级工程师','按键定位平均 O(1)\n关联需要标识或检索补充'),
        (470,20,'Enhanced Notes','在 TechCorp 任高级工程师，\n带领 5 人团队\n开发推荐系统。','段落保存事件背景\n重复内容需协调更新'),
        (20,410,'JSON Cards','work.company.name\n  = "TechCorp"\nwork.position.title\n  = "高级工程师"','类别 → 子类别 → 字段\n支持局部更新 · 需设计分类'),
        (470,410,'Advanced JSON Cards','person：用户父亲\nrelationship：父亲\nbackstory：心脏科就诊\n时间：2025-03-15','来源 · 主体 · 关系 · 时间\n消歧依据更完整 · 维护增加'),
    ]
    for x,y,title,example,tradeoff in cards:
        f.box(x,y,410,350,'#ffffff')
        f.box(x,y,410,62,'#dedede')
        f.text(x+205,y+40,title,23,True)
        f.text(x+205,y+103,example,21)
        f.path([(x+20,y+246),(x+390,y+246)])
        f.text(x+205,y+283,tradeoff,20)
    f.save('fig3-2.svg')


def memory_versions():
    f = Figure('Mem0 记忆管理架构', 'v2 在写入时比较和更新事实；v3 追加事实，在检索时结合语义、关键词、实体与时间背景。', 850)
    for x, title in [(20, 'v2：写入时协调事实'), (470, 'v3：追加事实与混合检索')]:
        f.box(x,20,410,65,'#dedede')
        f.text(x+205,61,title,23,True)
    left = [
        ('对话', '“我以前住北京，现在住上海。”'),
        ('LLM 提取候选事实', '当前居住地：上海'),
        ('向量检索已有记忆', '居住地：北京'),
        ('LLM 比较与决策', 'ADD · UPDATE · DELETE · NOOP'),
        ('更新存储', 'UPDATE：居住地 → 上海'),
    ]
    right = [
        ('对话', '“我以前住北京，现在住上海。”'),
        ('一次 LLM 提取', '事实及其时间背景'),
        ('ADD：追加存储', '过去：北京；现在：上海'),
        ('查询：现在住哪里？', '语义 · BM25 · 实体匹配'),
        ('排序后的相关事实', '结合时间背景确定当前居住地'),
    ]
    for x, rows in [(20,left),(470,right)]:
        for i,(title,detail) in enumerate(rows):
            y=115+i*145
            f.box(x,y,410,112,'#ffffff')
            f.text(x+205,y+38,title,23,True)
            f.text(x+205,y+81,detail,20)
            if i<4:f.path([(x+205,y+112),(x+205,y+145)],True)
    f.save('fig3-3.svg')


def memory_architecture():
    f = Figure('多类型记忆协同的参考架构', '工作记忆保存当前任务状态；情景、语义和程序记忆通过选择性写入及检索激活参与当前任务。', 660)
    f.box(210,20,480,150,'#dedede')
    f.text(450,60,'工作记忆',26,True)
    f.text(450,100,'当前目标 · 对话 · 工具结果',22)
    f.text(450,136,'任务状态与待执行步骤',22)
    f.path([(320,170),(320,280)],True)
    f.text(224,232,'选择性写入',21)
    f.path([(580,280),(580,170)],True)
    f.text(683,232,'检索与激活',21)
    f.box(20,280,860,350,'#ffffff')
    f.text(450,322,'长期记忆：跨会话保存',24,True)
    for x,title,lines in [
        (40,'情景记忆','事件与时间顺序\n人物 · 来源 · 状态\n“1 月预订了\n东京航班”'),
        (330,'语义记忆','稳定事实与偏好\n从陈述或经历提取\n“偏好靠窗座位”'),
        (620,'程序记忆','流程与操作经验\n步骤 · 条件 · 分支\n预订航班 → 酒店\n→ 检查证件'),
    ]:
        f.box(x,350,240,245)
        f.text(x+120,390,title,24,True)
        f.text(x+120,436,lines,21)
    f.save('fig3-4.svg')


def rag_flow():
    f = Figure('RAG 查询流程：检索、增强与生成', '退款问题经检索获得政策与操作片段，片段与问题共同构成模型输入，生成具体回答。', 950)
    f.box(20,20,290,110,'#dedede')
    f.text(165,58,'用户问题',24,True)
    f.text(165,99,'如何申请退款？',22)
    f.box(440,20,440,110)
    f.text(660,58,'知识库',24,True)
    f.text(660,99,'退款政策 · 操作指南 · 到账时间',22)
    f.path([(165,130),(165,175),(290,175)],True)
    f.path([(660,130),(660,175),(610,175)],True)
    f.box(290,145,320,100)
    f.text(450,183,'检索 Top-k 片段',24,True)
    f.text(450,222,'稠密向量 / BM25',22)
    f.path([(450,245),(450,280)],True)
    f.box(20,280,860,195,'#ffffff')
    f.text(450,317,'检索结果',24,True)
    f.text(450,361,'① 签收后 7 天内可申请全额退款，需提供订单号。',22)
    f.text(450,404,'退款将在 3–5 个工作日内到账。',22)
    f.text(450,447,'② 我的订单 → 选择订单 → 申请退款。',22)
    f.path([(450,475),(450,515)],True)
    f.box(20,515,860,125,'#dedede')
    f.text(450,554,'增强后的模型输入',24,True)
    f.text(450,601,'任务指令 + 用户问题 + 检索片段及来源标识',22)
    f.path([(450,640),(450,675)],True)
    f.box(290,675,320,65)
    f.text(450,717,'LLM 生成回答',24,True)
    f.path([(450,740),(450,780)],True)
    f.box(20,780,860,145,'#ffffff')
    f.text(450,818,'回答',24,True)
    f.text(450,861,'请在签收后 7 天内进入“我的订单”，选择订单并申请退款。',22)
    f.text(450,900,'申请时提供订单号，退款预计在 3–5 个工作日内到账。',22)
    f.save('fig3-5.svg')


def embedding_evolution():
    f = Figure('稠密嵌入技术演进', '从静态词向量、上下文词元表示，到面向相似度计算的句向量及多种检索表示。维度采用图内指定配置。', 900)
    rows = [
        ('2013', 'Word2Vec', '局部窗口中的词汇共现\n预测上下文或中心词', '静态词向量\n示例配置：300 维'),
        ('2014', 'GloVe', '全局词共现统计\n加权最小二乘目标', '静态词向量\n示例配置：300 维'),
        ('2018', 'BERT', 'Transformer · 掩码语言模型\n词元表示随所在上下文变化', '上下文词元表示\nBERT-base：768 维'),
        ('2019', 'Sentence-BERT', '孪生 / 三元组网络 · 池化\n句向量可用余弦比较', '句子表示\nbase 版本：768 维'),
        ('2024', 'BGE-M3', '多语言 · 最长 8192 token\n稠密 / 稀疏 / 多向量检索', '稠密表示\n1024 维'),
    ]
    for i,(year,title,mechanism,output) in enumerate(rows):
        y=20+i*175
        f.box(20,y,860,140,'#ffffff')
        f.box(20,y,220,140,'#dedede')
        f.text(130,y+43,year,22)
        f.text(130,y+90,title,22,True)
        f.text(440,y+57,mechanism,20)
        f.path([(640,y+20),(640,y+120)])
        f.text(761,y+57,output,20)
        if i<4:f.path([(450,y+140),(450,y+175)],True)
    f.save('fig3-6.svg')


def hnsw():
    f = Figure('HNSW 索引结构', '同一节点在不同层使用相同字母。搜索从高层入口出发，逐层下降，在底层扩展候选。深色箭头标记示例搜索路径。', 745)
    coords={'A':(200,0),'B':(300,-35),'C':(400,20),'D':(505,-30),'E':(620,10),'F':(755,-25),'G':(235,55),'H':(350,65),'I':(485,60),'J':(690,60)}
    layers=[(20,2,['A','D','F'],[('A','D'),('D','F')]),
            (245,1,['A','B','D','E','F'],[('A','B'),('A','D'),('B','D'),('D','E'),('D','F'),('E','F')]),
            (470,0,list(coords),[('A','B'),('A','G'),('A','C'),('B','C'),('B','D'),('C','D'),('C','H'),('C','I'),('D','E'),('D','I'),('E','I'),('E','F'),('E','J'),('F','J'),('G','H'),('H','I'),('I','J')])]
    positions={}
    for y,layer,nodes,edges in layers:
        f.box(20,y,860,205,'#ffffff')
        f.text(245,y+34, f'Layer {layer}：'+['全部节点 · 扩展候选','更多节点 · 缩小范围','少量节点 · 长程连接'][layer],21,True)
        for n in nodes:
            x,dy=coords[n];positions[layer,n]=(x,y+112+dy)
        for a,b in edges:
            (x1,y1),(x2,y2)=positions[layer,a],positions[layer,b]
            f.parts.append(f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="#aaaaaa" stroke-width="2"/>')
        for n in nodes:
            x,ny=positions[layer,n]
            f.parts.append(f'<circle cx="{x}" cy="{ny}" r="19" fill="#eeeeee" stroke="#333333" stroke-width="2"/>')
            f.text(x,ny+7,n,20,True)
    # Search proceeds along graph edges; each descent retains the same node.
    import math
    for layer,a,b in [(2,'A','D'),(1,'D','E'),(0,'E','J')]:
        (x1,y1),(x2,y2)=positions[layer,a],positions[layer,b]
        length=math.hypot(x2-x1,y2-y1);dx=(x2-x1)/length*22;dy=(y2-y1)/length*22
        f.parts.append(f'<path d="M{x1+dx} {y1+dy} L{x2-dx} {y2-dy}" fill="none" stroke="#222222" stroke-width="4" marker-end="url(#arrow)"/>')
    for upper,n in [(2,'D'),(1,'E')]:
        x,y1=positions[upper,n];_,y2=positions[upper-1,n]
        f.parts.append(f'<path d="M{x} {y1+22} L{x} {y2-22}" fill="none" stroke="#333333" stroke-width="2" stroke-dasharray="6 5" marker-end="url(#arrow)"/>')
    f.text(105,136,'入口',21)
    f.path([(140,130),(178,132)],True)
    f.text(450,720,'灰线：邻接边　　实线箭头：层内搜索　　虚线箭头：下降一层',20)
    f.save('fig3-7.svg')


def bm25():
    f=Figure('BM25 评分机制','查询词贡献相加；每项结合逆文档频率、词频饱和和长度归一化。数值例子与正文十篇文档的语料一致。',590)
    f.box(20,20,860,160,'#dedede')
    f.text(450,60,'Score(Q, D) = Σ IDF(qᵢ) ×',26,True)
    f.text(490,105,'TF(qᵢ, D) × (k₁ + 1)',25)
    f.path([(180,120),(800,120)])
    f.text(490,156,'TF(qᵢ, D) + k₁ × (1 − b + b × |D| / avgdl)',24)
    for x,title,lines in [
        (20,'词频饱和','k₁ 控制饱和程度\n文档长度固定时：\n词频增加，贡献增加\n每次增加的收益递减'),
        (315,'逆文档频率','N = 10\n“模型”：DF = 3\nIDF ≈ 0.762\n“蒸馏”：DF = 2\nIDF ≈ 1.224'),
        (610,'长度归一化','b ∈ [0, 1]\nb = 0：关闭校正\nb = 1：完全校正\n相同词频、b > 0 时\n长文档的贡献较低'),
    ]:
        f.path([(x+135,180),(x+135,220)],True)
        f.box(x,220,270,340,'#ffffff')
        f.text(x+135,263,title,24,True)
        f.text(x+135,318,lines,21)
    f.save('fig3-8.svg')


def hybrid():
    f=Figure('混合检索与重排序流水线','同一查询并行进入稠密与稀疏检索，合并候选后通过RRF融合，并可使用跨编码器重排序。图中分数为示例。',930)
    f.box(240,20,420,80,'#dedede')
    f.text(450,52,'用户查询',23,True)
    f.text(450,84,'kitty behavior',22)
    f.path([(450,100),(450,125),(225,125),(225,150)],True)
    f.path([(450,125),(675,125),(675,150)],True)
    branches=[(20,'稠密检索','语义：kitty ≈ cat / feline','余弦相似度（示例）',[
        'doc3：feline habits and cat play','0.87','doc7：cat grooming patterns','0.82','doc1：pet care basics','0.71']),
        (470,'稀疏检索 · BM25','词项：kitty / behavior','BM25 分数（示例）',[
        'doc5：kitty litter training','8.4','doc9：kitty adoption guide','6.1','doc2：kitty behavior and health','3.2'])]
    for x,title,mechanism,label,rows in branches:
        f.box(x,150,410,380,'#ffffff')
        f.text(x+205,190,title,24,True)
        f.text(x+205,232,mechanism,21)
        f.text(x+205,270,label,20)
        for i in range(3):
            f.text(x+205,317+i*72,rows[i*2],20)
            f.text(x+205,346+i*72,rows[i*2+1],21,True)
        f.path([(x+205,530),(x+205,560),(450,560)])
    f.path([(450,560),(450,590)],True)
    f.box(120,590,660,90,'#dedede')
    f.text(450,624,'合并去重 → RRF 融合',24,True)
    f.text(450,659,'6 个不同候选 → 按融合排名取前 5 个',22)
    f.path([(450,680),(450,715)],True)
    f.box(120,715,660,90)
    f.text(450,750,'可选：跨编码器重排序',24,True)
    f.text(450,785,'逐对输入“查询 + 候选文本”，重新评分',22)
    f.path([(450,805),(450,840)],True)
    f.box(240,840,420,65,'#ffffff')
    f.text(450,882,'最终排序 Top-N',24,True)
    f.save('fig3-9.svg')


def raptor():
    f=Figure('RAPTOR 树状层次索引','原始文档分块后，按嵌入聚类并生成摘要，再递归形成更高层摘要。箭头表示索引构建方向。',620)
    f.box(310,20,280,75,'#dedede');f.text(450,66,'全局摘要 · 根节点',24,True)
    for x,label in [(30,'A'),(330,'B'),(630,'C')]:
        f.box(x,185,240,75);f.text(x+120,232,'聚类摘要 '+label,23,True)
        f.path([(x+120,185),(x+120,135),(450,135),(450,95)],True)
    for i in range(7):
        x=20+i*125;parent=[150,150,450,450,450,750,750][i]
        f.box(x,370,110,70,'#ffffff');f.text(x+55,414,'文本块 '+str(i+1),20)
        f.path([(x+55,370),(x+55,310),(parent,310),(parent,260)],True)
    f.parts.append('<rect x="315" y="148" width="270" height="29" fill="white"/>')
    f.text(450,171,'摘要向量 → 再聚类与摘要',21)
    f.parts.append('<rect x="315" y="326" width="270" height="29" fill="white"/>')
    f.text(450,349,'文本块向量 → 聚类与摘要',21)
    f.box(20,535,860,60,'#dedede');f.text(450,573,'原始文档',24,True)
    f.path([(450,535),(450,490),(75,490),(75,440)],True)
    for i in range(1,7):
        x=75+i*125;f.path([(450,490),(x,490),(x,440)],True)
    f.parts.append('<rect x="380" y="499" width="140" height="29" fill="white"/>')
    f.text(450,522,'按边界分块',21)
    f.save('fig3-10.svg')


def graph_memory():
    f=Figure('GraphRAG 实体—关系知识图谱','两个张医生有不同实体标识和关系。牙医地址沿用户、医生、医院、地址依次检索。',655)
    f.box(20,20,860,65,'#dedede');f.text(450,62,'查询：我的牙医所在医院的地址？',25,True)
    f.box(340,120,220,60);f.text(450,160,'用户',25,True)
    for x,doctor,dept,relation,hospital in [
        (20,'张医生-A','牙科','我的牙医','仁爱口腔医院'),
        (470,'张医生-B','心内科','父亲的心脏科医生','华山医院 · 心血管中心')]:
        mid=x+205
        f.path([(450,180),(450,210),(mid,210),(mid,280)],True)
        f.text(mid+100,257,relation,22)
        f.box(x,280,410,90,'#ffffff');f.text(mid,315,doctor,24,True);f.text(mid,350,'科室：'+dept,22)
        f.path([(mid,370),(mid,430)],True);f.text(mid+65,409,'就职于',21)
        f.box(x,430,410,70);f.text(mid,474,hospital,22,True)
    f.path([(225,500),(225,560)],True);f.text(285,539,'地址',21)
    f.box(20,560,410,65);f.text(225,602,'徐汇区 XX 路',23)
    f.save('fig3-11.svg')


def rag_comparison():
    f=Figure('智能体化 RAG 与非智能体化 RAG 对比','左侧固定执行一次检索；右侧由模型根据返回观测决定继续查询或生成回答，Harness执行搜索预算。',740)
    for x,title in [(20,'单次检索 RAG'),(470,'Agentic RAG')]:
        f.box(x,20,410,65,'#dedede');f.text(x+205,62,title,25,True)
    for y,title,detail in [(125,'用户查询','原始问题'),(290,'检索一次','取回相关片段'),(455,'生成回答','问题 + 检索材料')]:
        f.box(50,y,350,115,'#ffffff');f.text(225,y+42,title,24,True);f.text(225,y+86,detail,22)
        if y<455:f.path([(225,y+115),(225,y+165)],True)
    for y,title,detail in [(125,'分析需求','选择或改写查询'),(290,'行动：调用检索工具','取得相关片段'),(455,'观测与判断','检查证据及信息缺口')]:
        f.box(500,y,350,115,'#ffffff');f.text(675,y+42,title,23,True);f.text(675,y+86,detail,22)
        if y<455:f.path([(675,y+115),(675,y+165)],True)
    f.path([(500,510),(450,510),(450,103),(675,103),(675,125)],True)
    f.text(675,607,'充分 / 预算耗尽',21)
    f.path([(675,570),(675,580)]);f.path([(675,615),(675,650)],True)
    f.box(500,650,350,65,'#dedede');f.text(675,692,'回答或请求补充信息',23,True)
    f.parts.append('<rect x="403" y="327" width="94" height="94" fill="white"/>')
    f.text(450,350,'证据不足\n预算可用\n继续检索',20)
    f.save('fig3-12.svg')


def agentic_architecture():
    f=Figure('智能体化 RAG 系统架构','Agent内的模型与Harness组织检索循环；外部工具执行搜索并返回观测。知识库检索接口可连接不同索引后端。',860)
    f.box(20,20,860,345,'#ffffff');f.text(450,59,'Agent',25,True)
    f.box(45,85,355,240,'#dedede');f.text(222,124,'Model',24,True)
    f.text(222,173,'分析需求 → 工具调用决策\n读取观测 → 检查信息缺口\n继续查询 / 生成回答',21)
    f.box(500,85,355,240);f.text(677,124,'Harness',24,True)
    f.text(677,173,'组织上下文与历史\n校验参数 · 调度工具\n维护状态 · 执行预算',21)
    f.path([(400,175),(500,175)],True);f.path([(500,270),(400,270)],True)
    f.text(450,157,'决策',20);f.text(450,303,'观测',20)
    f.path([(600,365),(600,440)],True);f.text(538,408,'调用',21)
    f.path([(770,440),(770,365)],True);f.text(820,408,'结果',21)
    f.box(20,440,860,115,'#ffffff');f.text(450,476,'工具执行层',23,True)
    for x,label in [(190,'knowledge_base_search'),(530,'web_search'),(760,'code_interpreter')]:f.text(x,524,label,20)
    f.path([(190,555),(190,600),(450,600),(450,645)],True)
    f.box(20,645,860,185,'#ffffff');f.text(450,683,'知识库后端',24,True)
    for x,title,detail in [(40,'retrieval-pipeline','混合检索'),(330,'structured-index','RAPTOR / GraphRAG'),(620,'contextual-retrieval','上下文感知检索')]:
        f.box(x,710,240,95);f.text(x+120,746,title,20,True);f.text(x+120,784,detail,20)
    f.save('fig3-13.svg')


def contextual():
    f=Figure('上下文感知检索','原始文档与目标块共同输入模型生成背景前缀，再把前缀与原文建立索引。示例保留ACME公司2025年第二季度收入增长3%的完整片段。',795)
    for x,title in [(20,'原始片段'),(470,'补充背景后的片段')]:
        f.box(x,20,410,340,'#ffffff');f.box(x,20,410,65,'#dedede');f.text(x+205,61,title,24,True)
    f.text(225,153,'该公司第二季度的收入增长了 3%，\n主要由新产品线驱动。',21)
    f.text(225,263,'待解析的指代：公司、年份',21,True)
    f.box(490,110,370,80);f.text(675,141,'ACME 公司 · 2025 年 Q2 财报\n关键业绩指标',21,True)
    f.text(675,239,'该公司第二季度的收入增长了 3%，\n主要由新产品线驱动。',21)
    f.text(675,323,'可匹配：ACME · Q2 · 收入',21)
    f.text(450,414,'索引构建',25,True)
    for x,title,detail in [(20,'原始文档','完整背景'),(470,'目标文本块','保留原始内容')]:
        f.box(x,450,410,90);f.text(x+205,487,title,23,True);f.text(x+205,524,detail,21)
        f.path([(x+205,540),(x+205,565),(450,565)])
    f.path([(450,565),(450,590)],True)
    f.box(180,590,540,85,'#dedede');f.text(450,625,'LLM 生成上下文前缀',24,True);f.text(450,660,'同一文档的调用可复用提示缓存',21)
    f.path([(450,675),(450,710)],True)
    f.box(20,710,860,65);f.text(450,752,'前缀 + 原始片段 → BM25 / 稠密向量索引',23,True)
    f.save('fig3-14.svg')


def knowledge_extraction():
    f=Figure('结构化知识提取流水线','从案例材料发现模块化字段，提取结构化记录，经编码、标准化和聚类形成原型，按簇中心差异解释特征权重。',1045)
    f.box(20,20,860,365,'#ffffff');f.text(450,60,'阶段一：知识提取与结构化',25,True)
    cards=[(40,'原始判例文书','CAIL2018\n按罪名抽样'),(335,'LLM 因素发现','自下而上整理字段\n定义取值与缺失状态'),(630,'结构化记录','自首：true\n赔偿：50 万元\n伤害：重伤二级')]
    for x,title,detail in cards:
        f.box(x,90,230,165);f.text(x+115,131,title,22,True);f.text(x+115,173,detail,20)
        if x<630:f.path([(x+230,165),(x+295,165)],True)
    f.box(40,285,820,75,'#dedede');f.text(450,317,'模块化 Schema：通用字段 + 罪名扩展',23,True)
    f.text(450,347,'自首 / 赔偿 / 前科；盗窃 → 涉案金额，伤害 → 伤害等级',21)
    f.path([(450,385),(450,425)],True)
    f.box(20,425,860,405,'#ffffff');f.text(450,465,'阶段二：特征分析与原型建模',25,True)
    f.box(40,495,820,90);f.text(450,531,'特征编码与标准化',23,True)
    f.text(450,567,'类别独热编码 · 布尔标记 · 数值对数变换 · 标准化',21)
    f.path([(450,585),(450,602),(230,602),(230,620)],True)
    f.box(40,620,380,175);f.text(230,659,'KMeans 聚类',24,True)
    f.text(230,703,'按罪名比较 2–5 个簇\n轮廓系数选择 → 案件原型\n特征 + 刑期分布摘要',21)
    f.path([(420,705),(470,705)],True)
    f.box(470,620,390,175);f.text(665,659,'特征权重',24,True)
    f.text(665,703,'比较标准化簇中心差异\n衡量特征对原型的区分作用\n辅助解释匹配结果',21)
    f.path([(450,830),(450,865)],True)
    f.box(20,865,860,155,'#dedede');f.text(450,906,'应用扩展：对话式案例查询',24,True)
    f.text(450,951,'补充关键事实 → 匹配案件原型 → 结合来源解释统计结果',22)
    f.text(450,989,'例：口角后徒手冲突，与预谋持械行为的特征组合',21)
    f.save('fig3-15.svg')


if __name__ == '__main__':
    roadmap()
    formats()
    memory_versions()
    memory_architecture()
    rag_flow()
    embedding_evolution()
    hnsw()
    bm25()
    hybrid()
    raptor()
    graph_memory()
    rag_comparison()
    agentic_architecture()
    contextual()
    knowledge_extraction()
