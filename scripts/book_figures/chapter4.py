"""Chapter 4 grayscale diagrams retaining protocol and tool details."""
from introduction import Figure


def mcp_sequence():
    f=Figure('MCP 协议交互时序', 'MCP 2026-07-28：客户端可先发现服务器能力，再列举并调用天气工具。每次请求均携带所需协议元数据；图中展开业务方法与参数。', 910)
    for x,title,detail in [(20,'MCP Client','宿主内的协议客户端'),(600,'MCP Server','提供天气查询工具')]:
        f.box(x,20,280,90,'#dedede')
        f.text(x+140,57,title,25,True)
        f.text(x+140,93,detail,21)
    for x in [160,740]:
        f.parts.append(f'<path d="M{x} 110 L{x} 890" fill="none" stroke="#777777" stroke-width="2" stroke-dasharray="7 5"/>')
    for y,title in [(135,'① 能力发现（客户端可选）'),(365,'② 工具发现'),(635,'③ 工具调用')]:
        f.box(20,y,860,45,'#eeeeee');f.text(450,y+31,title,22,True)
    def message(y,label,reply=False):
        f.text(450,y-15,label,22)
        f.path([(740 if reply else 160,y),(160 if reply else 740,y)],True)
    message(235,'server/discover')
    message(310,'支持的协议版本与服务器能力',True)
    message(450,'tools/list')
    message(535,'工具定义：get_weather',True)
    f.box(240,555,420,60,'#ffffff');f.text(450,581,'输入：城市（字符串）',20);f.text(450,608,'用途：查询指定城市天气',20)
    message(720,'tools/call：get_weather')
    f.text(450,754,'arguments：{"location": "Beijing"}',20)
    message(850,'工具结果：Beijing，22°C，晴',True)
    f.save('fig4-1.svg')


def hierarchical_discovery():
    f=Figure('层次化工具匹配（服务器级→工具级两层语义搜索）',
             '示意分数：先选GitHub服务器，再按工具相似度返回三个候选。服务器工具数与分数用于展示流程。', 1020)
    f.box(20,20,860,100,'#ffffff')
    f.text(450,56,'Agent：我需要查询 GitHub 仓库的贡献者统计',24,True)
    f.text(450,94,'discover_tools（自然语言需求）',22)
    f.path([(450,120),(450,155)],True)
    f.box(20,155,860,50,'#dedede');f.text(450,189,'① 服务器匹配 · 相似度（示意）',23,True)
    for i,(name,score) in enumerate([('GitHub','0.92'),('Weather','0.15'),('Finance','0.23'),('ArXiv','0.18'),('File System','0.31')]):
        x=20+i*175
        f.box(x,225,160,90,'#dedede' if i==0 else '#ffffff')
        f.text(x+80,260,name,21,i==0);f.text(x+80,295,score,22,i==0)
    f.path([(100,315),(100,345),(450,345),(450,390)],True)
    f.text(560,371,'Top-1：GitHub',21,True)
    f.box(20,390,860,50,'#dedede');f.text(450,424,'② 工具匹配 · GitHub 服务器内 26 个工具（示意）',22,True)
    for i,(name,score,desc,chosen) in enumerate([
        ('search_repositories','0.41','搜索仓库',False),
        ('list_contributors','0.89','贡献者列表',True),
        ('get_repo_stats','0.85','仓库统计',True),
        ('create_issue','0.12','创建 Issue',False),
        ('get_commit_history','0.67','提交历史',True)]):
        y=460+i*70
        f.box(80,y,740,55,'#dedede' if chosen else '#ffffff')
        f.text(270,y+36,name,22,chosen);f.text(520,y+36,score,22,chosen);f.text(690,y+36,desc,22)
    f.path([(450,795),(450,835)],True)
    f.box(80,835,740,165,'#eeeeee');f.text(450,870,'返回 Top-3 工具定义',23,True)
    f.text(450,907,'list_contributors',22);f.text(450,941,'get_repo_stats',22);f.text(450,975,'get_commit_history',22)
    f.save('fig4-2.svg')


def cache_loading():
    f=Figure('工具动态加载的 KV Cache 优化',
             '左侧展示修改前部工具清单导致从变动点重算；右侧展示保留前缀并在历史末尾追加发现结果。缓存命中还受服务策略影响。',1050)
    for x,title in [(20,'修改前部工具清单'),(470,'在历史末尾追加定义')]:
        f.box(x,20,410,55,'#dedede');f.text(x+205,57,title,24,True)
    def row(x,y,h,title,detail,fill='#ffffff'):
        f.box(x,y,410,h,fill);f.text(x+205,y+34,title,22,True)
        if detail:f.text(x+205,y+70,detail,20)
    row(20,95,100,'System Prompt','角色与规则','#eeeeee')
    row(20,215,135,'工具清单：本轮有变动','已有工具定义\n＋ get_stock_quote','#dedede')
    row(20,380,100,'User','查询 NVDA 股价')
    row(20,510,100,'Assistant','调用 get_stock_quote')
    row(20,640,100,'Tool Result','股价查询结果')
    f.path([(225,195),(225,215)],True)
    for y,end in [(350,380),(480,510),(610,640)]:f.path([(225,y),(225,end)],True)
    row(20,795,125,'缓存复用边界','变动点之前可复用\n其后重新计算','#eeeeee')
    row(470,95,150,'稳定前缀','角色与规则\nweb_search、code_interpreter\ndiscover_tools','#eeeeee')
    row(470,265,90,'User','查询 NVDA 股价')
    row(470,375,110,'Assistant：discover_tools','我需要查询股票价格的能力')
    row(470,505,110,'发现结果','get_stock_quote 完整 schema','#dedede')
    row(470,635,110,'新增状态记录','可用工具：web_search …\n＋ get_stock_quote')
    row(470,765,110,'Assistant → Tool Result','调用 get_stock_quote\n返回股价查询结果')
    for y,end in [(245,265),(355,375),(485,505),(615,635),(745,765)]:f.path([(675,y),(675,end)],True)
    row(470,900,125,'后续请求','已有定义保留原位\n新内容继续追加','#eeeeee')
    f.save('fig4-3.svg')


def context_history():
    f=Figure('动态发现后的上下文结构：工具 schema 散落在轨迹各处',
             '以股价查询和GitHub贡献者分析展示两轮工具发现。新增定义随tool_search_output进入历史，并在后续请求中保留位置。',1030)
    f.box(20,20,860,160,'#dedede');f.text(450,55,'稳定前缀',24,True)
    f.text(450,93,'System Prompt',22)
    f.text(450,129,'核心工具：web_search、code_interpreter',22)
    f.text(450,162,'工具搜索：tool_search',22)
    f.path([(450,180),(450,210)],True)
    rows=[
        ('User','查询 NVDA 股价',False),
        ('Assistant','tool_search_call（股价）',False),
        ('tool_search_output','get_stock_quote 完整 schema',True),
        ('Assistant → Tool Result','调用 get_stock_quote → 返回股价',False),
        ('User','分析 GitHub 仓库的贡献者',False),
        ('Assistant','tool_search_call（GitHub）',False),
        ('tool_search_output','list_contributors 等工具的完整 schema',True),
        ('Assistant → Tool Result → 回复','调用工具 → 获取贡献者 → 分析结果',False),
    ]
    for i,(role,detail,loaded) in enumerate(rows):
        y=210+i*90
        f.box(70,y,760,74,'#dedede' if loaded else '#ffffff')
        f.text(450,y+29,role,22,True);f.text(450,y+59,detail,21)
        if i<7:f.path([(450,y+74),(450,y+90)],True)
    f.path([(450,914),(450,945)],True)
    f.box(70,945,760,60,'#eeeeee');f.text(450,984,'下一轮：在现有历史末尾追加消息',23,True)
    f.save('fig4-4.svg')


if __name__ == '__main__':
    mcp_sequence()
    hierarchical_discovery()
    cache_loading()
    context_history()
