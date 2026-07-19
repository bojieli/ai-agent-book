"""
实验 8-4 工具库：120+ 个跨领域工具定义。

设计要点：
1) 每个工具都有真实可读的 name / description / parameters（OpenAI function schema）。
2) 领域覆盖 finance / news / web / arxiv / file / github / code / geo / weather /
   media / language / email / db / ecommerce / social / crypto / util 等。
3) 故意混入大量"通用/近义"工具（web_search / universal_search / quick_answer ...），
   它们在全量注入时会与"专用工具"竞争，诱导模型错选（如查股价用 web_search）。
4) 工具执行只做轻量 mock —— 本实验关心的是"能否选对工具"，不是工具真实结果。

对外导出：
- ALL_TOOLS          : List[dict]  OpenAI tools 数组（126 个）
- TOOLS_BY_NAME      : Dict[str, dict]
- TOOL_IMPLS         : Dict[str, callable]  mock 执行函数
- BASE_TOOL_NAMES    : 主动发现模式下 system 里保留的少量基础工具
- GENERIC_TOOL_NAMES : 通用/兜底工具集合（用于统计"是否用通用工具替代了专用工具"）
- select_tools       : 按 --tool-set-size 截取工具子集（演示工具集规模的影响）
- TASKS              : List[dict]  评测任务及其判分标准
"""

from typing import Dict, List


def _tool(name: str, description: str, params: Dict) -> Dict:
    """构造一个 OpenAI function-calling tool schema。"""
    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": {
                "type": "object",
                "properties": params,
                "required": list(params.keys()),
            },
        },
    }


def _s(desc: str) -> Dict:
    return {"type": "string", "description": desc}


def _i(desc: str) -> Dict:
    return {"type": "integer", "description": desc}


# ---------------------------------------------------------------------------
# 工具定义（按领域分组）
# ---------------------------------------------------------------------------

_DEFS: List[Dict] = []

# --- finance（金融专用，10）---
_DEFS += [
    _tool("get_stock_price", "获取指定股票代码的实时最新股价、涨跌幅与成交量（专业金融数据源）。",
          {"symbol": _s("股票代码，如 AAPL、TSLA")}),
    _tool("get_stock_history", "获取某支股票的历史 K 线行情数据。",
          {"symbol": _s("股票代码"), "range": _s("时间范围，如 1mo/1y")}),
    _tool("get_company_financials", "获取上市公司的财报数据（营收、利润、资产负债表）。",
          {"symbol": _s("股票代码")}),
    _tool("get_forex_rate", "获取两种法定货币之间的实时外汇汇率。",
          {"base": _s("基准货币，如 USD"), "quote": _s("报价货币，如 JPY")}),
    _tool("get_crypto_price", "获取指定加密货币的实时价格（USD 计价）。",
          {"symbol": _s("加密货币代码，如 BTC、ETH")}),
    _tool("get_market_index", "获取股票市场指数的实时点位，如标普500、纳斯达克。",
          {"index": _s("指数代码，如 SPX、IXIC")}),
    _tool("get_earnings_calendar", "查询某公司的财报发布日历。", {"symbol": _s("股票代码")}),
    _tool("get_analyst_ratings", "获取分析师对某股票的评级与目标价。", {"symbol": _s("股票代码")}),
    _tool("get_dividend_history", "获取某股票的历史分红派息记录。", {"symbol": _s("股票代码")}),
    _tool("convert_currency", "按最新汇率把一笔金额从一种货币换算为另一种货币。",
          {"amount": {"type": "number", "description": "金额"},
           "from_currency": _s("源货币"), "to_currency": _s("目标货币")}),
]

# --- news（新闻专用，4）---
_DEFS += [
    _tool("search_news", "按关键词检索最新新闻文章，返回标题、来源、时间与摘要（新闻聚合源）。",
          {"query": _s("检索关键词"), "lang": _s("语言，如 zh/en")}),
    _tool("get_top_headlines", "获取某分类/国家的头条新闻。",
          {"category": _s("分类，如 business/tech"), "country": _s("国家代码，如 us/cn")}),
    _tool("get_news_by_source", "获取指定新闻媒体源的最新报道。", {"source": _s("媒体源，如 reuters")}),
    _tool("summarize_article", "抓取并总结一篇新闻文章的核心内容。", {"url": _s("文章 URL")}),
]

# --- web / generic（通用检索，诱导错选，8）---
_DEFS += [
    _tool("web_search", "通用联网搜索，可查询几乎任何实时信息并给出答案，"
                        "包括股票价格、汇率、天气、新闻、百科、代码、地理等各类问题——一个工具满足大部分查询需求。",
          {"query": _s("搜索关键词")}),
    _tool("universal_search", "万能搜索助手，可回答任何主题的问题，"
                             "覆盖金融、科技、生活、学术等所有领域的信息查询。", {"query": _s("查询")}),
    _tool("quick_answer", "对任意问题给出快速简短的答案，适用于价格、天气、新闻、常识等各种即时提问。",
          {"question": _s("问题")}),
    _tool("google_search", "使用 Google 搜索网页，可查询任意主题的最新信息。", {"query": _s("查询")}),
    _tool("bing_search", "使用 Bing 搜索网页，可查询任意主题的最新信息。", {"query": _s("查询")}),
    _tool("fetch_url", "抓取给定 URL 的网页原始内容。", {"url": _s("网页 URL")}),
    _tool("scrape_webpage", "抓取网页并按 CSS 选择器提取结构化内容。",
          {"url": _s("网页 URL"), "selector": _s("CSS 选择器")}),
    _tool("ask_knowledge_base", "向通用知识库提问，返回百科式答案。", {"question": _s("问题")}),
]

# --- arxiv / academic（学术专用，5）---
_DEFS += [
    _tool("arxiv_search", "在 arXiv 论文库中检索论文，按相关度/时间返回论文标题、作者、摘要与 PDF 链接。",
          {"query": _s("检索关键词"), "max_results": _i("返回论文数量")}),
    _tool("arxiv_get_paper", "根据 arXiv ID 获取单篇论文的详细信息。", {"arxiv_id": _s("arXiv 编号")}),
    _tool("semantic_scholar_search", "在 Semantic Scholar 检索学术论文。", {"query": _s("关键词")}),
    _tool("get_citations", "获取某篇论文的引用列表。", {"paper_id": _s("论文 ID")}),
    _tool("search_pubmed", "在 PubMed 检索生物医学文献。", {"query": _s("关键词")}),
]

# --- file / download（文件下载，10）---
_DEFS += [
    _tool("download_file", "从给定 URL 下载文件（PDF/图片/压缩包等）并保存到本地。",
          {"url": _s("文件 URL"), "path": _s("本地保存路径")}),
    _tool("upload_file", "把本地文件上传到远端存储。", {"path": _s("本地文件路径")}),
    _tool("read_file", "读取本地文本文件内容。", {"path": _s("文件路径")}),
    _tool("write_file", "把内容写入本地文件。", {"path": _s("文件路径"), "content": _s("写入内容")}),
    _tool("list_directory", "列出目录下的文件。", {"path": _s("目录路径")}),
    _tool("delete_file", "删除本地文件。", {"path": _s("文件路径")}),
    _tool("convert_document", "转换文档格式，如 docx→pdf。",
          {"path": _s("文件路径"), "target_format": _s("目标格式")}),
    _tool("extract_text_from_pdf", "从 PDF 文件中抽取文本。", {"path": _s("PDF 路径")}),
    _tool("compress_files", "把多个文件压缩为一个压缩包。", {"paths": _s("逗号分隔的文件路径")}),
    _tool("unzip_archive", "解压压缩包。", {"path": _s("压缩包路径")}),
]

# --- github / dev（代码托管专用，8）---
_DEFS += [
    _tool("github_get_repo", "获取 GitHub 仓库的基本信息（stars、语言、描述等）。",
          {"owner": _s("仓库所有者"), "repo": _s("仓库名")}),
    _tool("github_list_contributors", "列出 GitHub 仓库的贡献者及各自的提交数（专用 GitHub API）。",
          {"owner": _s("仓库所有者"), "repo": _s("仓库名")}),
    _tool("github_list_issues", "列出 GitHub 仓库的 issues。",
          {"owner": _s("仓库所有者"), "repo": _s("仓库名")}),
    _tool("github_get_commits", "获取 GitHub 仓库的提交历史。",
          {"owner": _s("仓库所有者"), "repo": _s("仓库名")}),
    _tool("github_search_code", "在 GitHub 上按关键词搜索代码。", {"query": _s("搜索关键词")}),
    _tool("github_get_pull_requests", "列出 GitHub 仓库的 PR。",
          {"owner": _s("仓库所有者"), "repo": _s("仓库名")}),
    _tool("github_get_user", "获取 GitHub 用户资料。", {"username": _s("用户名")}),
    _tool("gitlab_get_project", "获取 GitLab 项目信息。", {"project_id": _s("项目 ID")}),
]

# --- code / analysis（代码执行与可视化，6）---
_DEFS += [
    _tool("code_interpreter", "在沙箱中执行 Python 代码，可做数据分析、统计并绘制/生成可视化图表。",
          {"code": _s("要执行的 Python 代码")}),
    _tool("render_chart", "根据给定数据直接渲染柱状图/折线图/饼图等可视化图表。",
          {"data": _s("JSON 数据"), "chart_type": _s("图表类型，如 bar/line/pie")}),
    _tool("run_shell_command", "在服务器上执行 shell 命令。", {"command": _s("命令")}),
    _tool("lint_code", "对代码做静态检查。", {"code": _s("代码"), "language": _s("语言")}),
    _tool("format_code", "格式化代码。", {"code": _s("代码"), "language": _s("语言")}),
    _tool("execute_sql", "执行 SQL 查询。", {"query": _s("SQL 语句")}),
]

# --- geo / maps（地理，6）---
_DEFS += [
    _tool("geocode_address", "把地址转换为经纬度坐标。", {"address": _s("地址")}),
    _tool("reverse_geocode", "把经纬度转换为地址。", {"lat": _s("纬度"), "lon": _s("经度")}),
    _tool("get_directions", "获取两地之间的导航路线。", {"origin": _s("起点"), "destination": _s("终点")}),
    _tool("get_distance", "计算两地之间的距离。", {"origin": _s("起点"), "destination": _s("终点")}),
    _tool("search_places", "在指定位置附近搜索地点/商户。",
          {"query": _s("关键词"), "location": _s("位置")}),
    _tool("get_timezone", "根据坐标获取时区。", {"lat": _s("纬度"), "lon": _s("经度")}),
]

# --- weather（天气专用，3）---
_DEFS += [
    _tool("get_current_weather", "获取指定城市的实时天气（气温、湿度、天气状况）。", {"location": _s("城市名")}),
    _tool("get_weather_forecast", "获取指定城市未来若干天的天气预报（专业气象数据源）。",
          {"location": _s("城市名"), "days": _i("预报天数")}),
    _tool("get_air_quality", "获取指定城市的空气质量指数 AQI。", {"location": _s("城市名")}),
]

# --- media（多媒体，6）---
_DEFS += [
    _tool("generate_image", "根据文字提示生成图片。", {"prompt": _s("图片描述")}),
    _tool("caption_image", "为图片生成文字描述。", {"url": _s("图片 URL")}),
    _tool("transcribe_audio", "把音频转写为文字。", {"url": _s("音频 URL")}),
    _tool("text_to_speech", "把文字合成为语音。", {"text": _s("文本")}),
    _tool("video_summarize", "总结一段视频的内容。", {"url": _s("视频 URL")}),
    _tool("ocr_image", "识别图片中的文字。", {"url": _s("图片 URL")}),
]

# --- language / NLP（文本处理，8）---
_DEFS += [
    _tool("translate_text", "把文本翻译为目标语言。", {"text": _s("文本"), "target_lang": _s("目标语言")}),
    _tool("detect_language", "检测文本语言。", {"text": _s("文本")}),
    _tool("summarize_text", "对一段文本做摘要。", {"text": _s("文本")}),
    _tool("paraphrase_text", "改写/润色一段文本。", {"text": _s("文本")}),
    _tool("correct_grammar", "纠正文本语法错误。", {"text": _s("文本")}),
    _tool("sentiment_analysis", "分析文本情感倾向。", {"text": _s("文本")}),
    _tool("extract_keywords", "从文本中抽取关键词。", {"text": _s("文本")}),
    _tool("named_entity_recognition", "识别文本中的命名实体。", {"text": _s("文本")}),
]

# --- email / comm / calendar（通讯与日程，7）---
_DEFS += [
    _tool("send_email", "发送一封电子邮件。",
          {"to": _s("收件人"), "subject": _s("主题"), "body": _s("正文")}),
    _tool("read_inbox", "读取邮箱中的邮件。", {"folder": _s("文件夹，如 inbox")}),
    _tool("create_calendar_event", "在用户日历上创建一个日程/事件（专用日历服务）。",
          {"title": _s("事件标题"), "start": _s("开始时间"), "end": _s("结束时间")}),
    _tool("list_calendar_events", "列出某日期的日历事件。", {"date": _s("日期 YYYY-MM-DD")}),
    _tool("send_slack_message", "向 Slack 频道发送消息。", {"channel": _s("频道"), "text": _s("内容")}),
    _tool("send_sms", "发送短信。", {"number": _s("手机号"), "text": _s("内容")}),
    _tool("make_phone_call", "拨打电话并播报脚本。", {"number": _s("电话"), "script": _s("话术")}),
]

# --- database / storage（存储，7）---
_DEFS += [
    _tool("query_database", "在业务数据库上执行只读查询。", {"sql": _s("SQL 查询")}),
    _tool("insert_record", "向数据表插入记录。", {"table": _s("表名"), "data": _s("JSON 数据")}),
    _tool("get_record", "按主键读取一条记录。", {"table": _s("表名"), "id": _s("主键")}),
    _tool("redis_get", "读取 Redis 键值。", {"key": _s("键")}),
    _tool("redis_set", "写入 Redis 键值。", {"key": _s("键"), "value": _s("值")}),
    _tool("s3_upload", "上传文件到 S3。", {"bucket": _s("桶"), "key": _s("对象键"), "path": _s("本地路径")}),
    _tool("s3_download", "从 S3 下载文件。", {"bucket": _s("桶"), "key": _s("对象键")}),
]

# --- ecommerce / travel（电商与出行，8）---
_DEFS += [
    _tool("search_products", "在电商平台搜索商品。", {"query": _s("关键词")}),
    _tool("get_product_details", "获取商品详情。", {"product_id": _s("商品 ID")}),
    _tool("add_to_cart", "把商品加入购物车。", {"product_id": _s("商品 ID"), "qty": _i("数量")}),
    _tool("track_shipment", "查询快递物流。", {"tracking_no": _s("运单号")}),
    _tool("search_flights", "搜索航班。",
          {"origin": _s("出发地"), "destination": _s("目的地"), "date": _s("日期")}),
    _tool("search_hotels", "搜索酒店。",
          {"location": _s("城市"), "checkin": _s("入住日"), "checkout": _s("离店日")}),
    _tool("book_restaurant", "预订餐厅。",
          {"name": _s("餐厅名"), "time": _s("时间"), "party": _i("人数")}),
    _tool("get_product_reviews", "获取商品评价。", {"product_id": _s("商品 ID")}),
]

# --- social（社交，5）---
_DEFS += [
    _tool("post_tweet", "发布一条推文。", {"text": _s("内容")}),
    _tool("search_tweets", "搜索推文。", {"query": _s("关键词")}),
    _tool("get_user_profile", "获取社交平台用户资料。",
          {"platform": _s("平台"), "username": _s("用户名")}),
    _tool("get_trending_topics", "获取热门话题。", {"region": _s("地区")}),
    _tool("get_reddit_posts", "获取某 subreddit 的帖子。", {"subreddit": _s("版块")}),
]

# --- crypto / blockchain（区块链，3）---
_DEFS += [
    _tool("get_wallet_balance", "查询链上钱包余额。", {"address": _s("钱包地址")}),
    _tool("get_gas_price", "查询链上 gas 价格。", {"chain": _s("链名，如 ethereum")}),
    _tool("get_nft_metadata", "获取 NFT 元数据。", {"contract": _s("合约地址"), "token_id": _s("token ID")}),
]

# --- misc util（杂项工具，10）---
_DEFS += [
    _tool("calculator", "做数学表达式计算。", {"expression": _s("数学表达式")}),
    _tool("get_current_time", "获取指定时区的当前时间。", {"timezone": _s("时区，如 Asia/Shanghai")}),
    _tool("generate_uuid", "生成一个 UUID。", {"version": _i("UUID 版本")}),
    _tool("get_random_number", "生成一个区间内的随机数。", {"min": _i("最小值"), "max": _i("最大值")}),
    _tool("url_shortener", "生成短链接。", {"url": _s("原始 URL")}),
    _tool("qr_code_generator", "生成二维码。", {"data": _s("二维码内容")}),
    _tool("password_generator", "生成随机密码。", {"length": _i("密码长度")}),
    _tool("get_ip_info", "查询 IP 归属地信息。", {"ip": _s("IP 地址")}),
    _tool("dns_lookup", "查询域名 DNS 记录。", {"domain": _s("域名")}),
    _tool("ping_host", "测试主机连通性。", {"host": _s("主机名")}),
]


# --- 更多领域工具（补足 120+，12）---
_DEFS += [
    _tool("get_commodity_price", "获取大宗商品（黄金/原油等）实时价格。", {"commodity": _s("商品名，如 gold/oil")}),
    _tool("get_bond_yield", "获取国债收益率。", {"country": _s("国家"), "maturity": _s("期限，如 10y")}),
    _tool("get_flight_status", "查询航班实时状态。", {"flight_no": _s("航班号")}),
    _tool("get_traffic_info", "查询某路段的实时路况。", {"road": _s("路段/城市")}),
    _tool("book_taxi", "叫一辆出租车/网约车。", {"pickup": _s("上车地点"), "dropoff": _s("目的地")}),
    _tool("get_horoscope", "获取星座运势。", {"sign": _s("星座")}),
    _tool("get_recipe", "根据食材/菜名获取菜谱。", {"dish": _s("菜名")}),
    _tool("get_definition", "查询词语释义。", {"word": _s("词语")}),
    _tool("currency_list", "列出支持的货币代码。", {"region": _s("地区")}),
    _tool("get_holidays", "查询某国某年的法定节假日。", {"country": _s("国家"), "year": _i("年份")}),
    _tool("unit_convert", "单位换算（长度/重量/温度等）。",
          {"value": {"type": "number", "description": "数值"}, "from_unit": _s("源单位"), "to_unit": _s("目标单位")}),
    _tool("get_wikipedia_summary", "获取维基百科词条摘要。", {"title": _s("词条标题")}),
]


# ---------------------------------------------------------------------------
# 导出结构
# ---------------------------------------------------------------------------

ALL_TOOLS: List[Dict] = _DEFS
TOOLS_BY_NAME: Dict[str, Dict] = {t["function"]["name"]: t for t in ALL_TOOLS}
assert len(ALL_TOOLS) == len(TOOLS_BY_NAME), "工具名有重复！"

# 主动发现模式下 system 保留的少量基础工具（不含任何专用领域工具）。
BASE_TOOL_NAMES = ["calculator", "get_current_time"]

# 通用/兜底工具：若在需要专用工具的任务中调用了这些，视为"用通用工具替代了专用工具"。
GENERIC_TOOL_NAMES = {
    "web_search", "universal_search", "quick_answer", "google_search",
    "bing_search", "fetch_url", "scrape_webpage", "ask_knowledge_base",
}


def select_tools(size: int = None, tasks: "List[Dict]" = None) -> List[Dict]:
    """按 --tool-set-size 截取一个工具子集，用于演示"工具集规模"对各策略的影响。

    子集**始终**包含：基础工具、全部通用/兜底工具（诱导项）、以及所选任务判分槽位涉及的
    专用工具；其余名额按 ALL_TOOLS 原顺序补足，直到达到 size 个。
    size 为空或 >= 全库规模时返回全部工具（默认行为）。
    """
    if size is None or size >= len(ALL_TOOLS):
        return ALL_TOOLS
    keep = set(BASE_TOOL_NAMES) | set(GENERIC_TOOL_NAMES)
    for task in (tasks if tasks is not None else TASKS):
        for slot in task["required_slots"]:
            keep.update(slot)
    size = max(size, len(keep))
    required = [t for t in ALL_TOOLS if t["function"]["name"] in keep]
    others = [t for t in ALL_TOOLS if t["function"]["name"] not in keep]
    return required + others[: size - len(required)]


# ---------------------------------------------------------------------------
# mock 执行
# ---------------------------------------------------------------------------

def _mock_result(name: str, args: Dict) -> str:
    """为常用工具返回像样的 mock 结果，其余返回通用占位结果。"""
    import json
    canned = {
        "get_stock_price": {"symbol": args.get("symbol"), "price": 227.52,
                            "change_pct": -1.83, "currency": "USD", "source": "NASDAQ"},
        "get_crypto_price": {"symbol": args.get("symbol"), "price": 3125.4, "currency": "USD"},
        "get_forex_rate": {"base": args.get("base"), "quote": args.get("quote"), "rate": 156.7},
        "convert_currency": {"amount": args.get("amount"), "from": args.get("from_currency"),
                             "to": args.get("to_currency"), "result": 15670.0, "rate": 156.7},
        "search_news": {"results": [
            {"title": "Apple shares slip on iPhone demand concerns", "source": "Reuters"},
            {"title": "Analysts weigh in on AAPL pullback", "source": "Bloomberg"}]},
        "arxiv_search": {"results": [
            {"id": "2406.00001", "title": "Efficient Transformers Revisited",
             "pdf": "https://arxiv.org/pdf/2406.00001"},
            {"id": "2406.00002", "title": "Sparse Attention Transformers",
             "pdf": "https://arxiv.org/pdf/2406.00002"},
            {"id": "2406.00003", "title": "Transformer Scaling Laws 2024",
             "pdf": "https://arxiv.org/pdf/2406.00003"}]},
        "download_file": {"saved": args.get("path"), "bytes": 482113, "status": "ok"},
        "github_list_contributors": {"contributors": [
            {"login": "alice", "commits": 1240}, {"login": "bob", "commits": 830},
            {"login": "carol", "commits": 617}]},
        "code_interpreter": {"stdout": "chart saved to /tmp/contrib.png", "status": "ok"},
        "render_chart": {"chart": "/tmp/contrib.png", "status": "ok"},
        "get_weather_forecast": {"location": args.get("location"),
                                 "forecast": [{"day": "Sun", "cond": "Sunny", "high": 31}]},
        "get_current_weather": {"location": args.get("location"), "cond": "Clear", "temp": 28},
        "create_calendar_event": {"event": args.get("title"), "status": "created"},
    }
    if name in canned:
        return json.dumps(canned[name], ensure_ascii=False)
    return json.dumps({"tool": name, "args": args, "status": "ok",
                       "result": f"<{name} 的 mock 结果>"}, ensure_ascii=False)


# 所有工具共用一个 mock 分发器
TOOL_IMPLS: Dict[str, callable] = {
    name: (lambda args, n=name: _mock_result(n, args)) for name in TOOLS_BY_NAME
}


# ---------------------------------------------------------------------------
# 评测任务及判分标准
# ---------------------------------------------------------------------------
# required_slots: List[List[str]]
#   每个内层 list 是"一个能力槽位"的可接受工具集合（任一命中即算填上该槽位）。
#   一个任务判为"选对"，当且仅当所有槽位都被填上。
# 这些任务都需要跨领域协作，且都存在"通用工具易被误选"的陷阱。

TASKS: List[Dict] = [
    {
        "id": "finance+news",
        "prompt": "苹果公司最近股价怎么样？帮我看看有没有相关新闻能解释一下原因。",
        "required_slots": [
            ["get_stock_price"],
            ["search_news", "get_top_headlines", "get_news_by_source"],
        ],
    },
    {
        "id": "arxiv+download",
        "prompt": "我想看看 transformer 领域最新的研究论文，帮我找几篇最新的，并把排在前三的下载下来。",
        "required_slots": [
            ["arxiv_search"],
            ["download_file"],
        ],
    },
    {
        "id": "github+viz",
        "prompt": "帮我看看 pytorch/pytorch 这个仓库都有谁贡献最多，最好能画个各人提交量的图表。",
        "required_slots": [
            ["github_list_contributors"],
            ["code_interpreter", "render_chart"],
        ],
    },
    {
        "id": "weather+calendar",
        "prompt": "这周日北京天气怎么样？要是晴天的话，帮我在日历里记一个'户外徒步'的活动。",
        "required_slots": [
            ["get_weather_forecast"],
            ["create_calendar_event"],
        ],
    },
    {
        "id": "forex+weather",
        "prompt": "100 美元现在能换多少日元？顺便告诉我东京现在的天气怎么样。",
        "required_slots": [
            ["get_forex_rate", "convert_currency"],
            ["get_current_weather"],
        ],
    },
    {
        "id": "crypto+news",
        "prompt": "以太坊现在多少钱一个？另外有什么最新的相关消息吗？",
        "required_slots": [
            ["get_crypto_price"],
            ["search_news", "get_top_headlines", "get_news_by_source"],
        ],
    },
    # 下面两个是"通用工具诱导"任务：措辞偏泛，容易让模型误用 web_search 等通用兜底工具，
    # 而其实存在更合适的专用工具。用来体现"全量注入错选通用工具、主动发现选对专用工具"。
    {
        "id": "opinion(诱导)",
        "prompt": "帮我了解一下特斯拉这家公司最近的新闻舆论风向。",
        "required_slots": [
            ["search_news", "get_news_by_source", "get_top_headlines"],
        ],
    },
    {
        "id": "academic(诱导)",
        "prompt": "帮我了解一下最近'量子计算'方面有什么新的科研进展。",
        "required_slots": [
            ["arxiv_search", "semantic_scholar_search", "search_pubmed"],
        ],
    },
]


def grade(task: Dict, called_tools: List[str]) -> Dict:
    """根据实际调用的工具给某个任务打分。"""
    called = set(called_tools)
    filled = []
    missed = []
    for slot in task["required_slots"]:
        if any(t in called for t in slot):
            filled.append(slot)
        else:
            missed.append(slot)
    used_generic = sorted(called & GENERIC_TOOL_NAMES)
    correct = len(missed) == 0
    return {
        "correct": correct,                       # 是否覆盖了全部能力槽位
        # 精确选对 = 覆盖全部能力槽位 且 没有误用通用兜底工具（web_search 等）
        "precise": correct and not used_generic,
        "filled_slots": len(filled),
        "total_slots": len(task["required_slots"]),
        "missed_slots": missed,
        "used_generic_substitute": used_generic,
    }


if __name__ == "__main__":
    print(f"工具总数: {len(ALL_TOOLS)}")
    print(f"基础工具: {BASE_TOOL_NAMES}")
    print(f"任务数: {len(TASKS)}")
