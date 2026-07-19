"""
离线后端：让整条流水线在**没有 OpenAI key** 时也能跑通，用于验证机制、
量化 token/延迟，并让读者零成本复现"三种策略"的对比结构。

包含两部分：
1) LocalEmbedder —— 本地哈希词袋嵌入（中文字 unigram/bigram + 英文词），
   无需联网即可支撑 discover_tools / 检索预筛选的语义相似度。
2) MockChatClient —— 一个确定性的"脚本化"模型，接口与 OpenAI 客户端一致
   （client.chat.completions.create(...).choices[0].message.content）。
   它按关键词把任务拆成若干子任务，遵循 ReAct 文本协议逐步调用工具。

重要边界说明：
- MockChatClient 是一个**强启发式路由器**，不代表真实小模型的能力，因此它**不会**复现
  书中"超长上下文下指令遵循退化、错选通用工具"的现象——那需要真实的小参数量模型。
- 离线模式下真实可复现的是：① 各策略注入的 token 量（tiktoken 真实计算）；
  ② 检索预筛选"一次性匹配"的结构性局限（若第二个子任务的专用工具没被初始检索选中，
  模型就调用不到它 → 该子任务失败）；③ 主动发现按需加载后仍能补齐工具、完成任务。
- 要观察真实模型在长上下文工具墙下的选择行为，请配置真实模型（见 README 中 gpt-5.6-luna 的真实结果表）。
"""

import hashlib
import json
import re
from types import SimpleNamespace
from typing import Dict, List, Tuple

from tools_library import TOOLS_BY_NAME

_DIM = 512


# ---------------------------------------------------------------------------
# 1) 本地嵌入后端
# ---------------------------------------------------------------------------

def _tokens(text: str) -> List[str]:
    """把中英文混合文本切成词袋 token：英文按词（并拆下划线），中文按字 unigram + bigram。"""
    text = text.lower()
    toks: List[str] = []
    for w in re.findall(r"[a-z0-9]+", text):
        toks.append(w)
    han = re.findall(r"[一-鿿]", text)
    toks += han
    toks += [han[i] + han[i + 1] for i in range(len(han) - 1)]
    return toks


class LocalEmbedder:
    """哈希词袋嵌入：确定性、无需联网。相似度由中英文关键词重叠驱动。"""

    name = "local-hash-%d" % _DIM

    def embed(self, texts: List[str]) -> List[List[float]]:
        out = []
        for t in texts:
            vec = [0.0] * _DIM
            for tok in _tokens(t):
                h = int(hashlib.md5(tok.encode()).hexdigest(), 16)
                vec[h % _DIM] += 1.0
            norm = sum(x * x for x in vec) ** 0.5 or 1.0
            out.append([x / norm for x in vec])
        return out


# ---------------------------------------------------------------------------
# 2) 脚本化 mock 模型
# ---------------------------------------------------------------------------
# 意图规则：把任务关键词映射到"应当使用的专用工具"及一句能力需求描述。
# 顺序有意义（如"预报"类天气须排在通用"天气"之前）。
INTENT_RULES: List[Tuple[str, str, str]] = [
    (r"股价|股票", "get_stock_price", "查询某股票的实时价格与涨跌幅"),
    (r"以太坊|比特币|加密|\beth\b|\bbtc\b", "get_crypto_price", "查询加密货币的实时价格"),
    (r"日元|汇率|美元.*换|换.*(日元|美元|欧元)|兑换", "get_forex_rate", "查询两种法定货币的外汇汇率"),
    (r"论文|arxiv|文献|量子计算|科研进展|研究进展", "arxiv_search", "在学术论文库检索最新论文"),
    (r"下载", "download_file", "从 URL 下载文件保存到本地"),
    (r"贡献", "github_list_contributors", "获取 GitHub 仓库的贡献者提交统计"),
    (r"图表|可视化|画个|画图|画一", "render_chart", "根据数据渲染可视化图表"),
    (r"预报|未来|周日|这周|明天|后天|下周", "get_weather_forecast", "查询某城市未来若干天的天气预报"),
    (r"天气", "get_current_weather", "查询某城市的实时天气"),
    (r"日历|日程|活动|记一个|记录一个", "create_calendar_event", "在日历上创建一个事件"),
    (r"新闻|舆论|消息|报道|风向", "search_news", "按关键词检索相关的最新新闻"),
]


def match_intents(prompt: str) -> List[Tuple[str, str]]:
    """返回任务涉及的 (专用工具名, 能力需求描述) 列表（去重、保序）。"""
    needed: List[Tuple[str, str]] = []
    seen = set()
    for pat, tool, phrase in INTENT_RULES:
        if re.search(pat, prompt, re.IGNORECASE) and tool not in seen:
            needed.append((tool, phrase))
            seen.add(tool)
    # 天气去重：若命中"预报"则不再单独要求"实时天气"。
    if "get_weather_forecast" in seen and "get_current_weather" in seen:
        needed = [(t, p) for t, p in needed if t != "get_current_weather"]
    return needed


_ARG_HINTS = {
    "symbol": "AAPL", "location": "北京", "query": "查询", "url": "https://example.com/f.pdf",
    "path": "/tmp/paper.pdf", "owner": "pytorch", "repo": "pytorch", "base": "USD",
    "quote": "JPY", "title": "户外徒步", "start": "2026-07-19T09:00", "end": "2026-07-19T12:00",
    "days": 3, "data": "[]", "chart_type": "bar", "code": "print('ok')", "max_results": 3,
}


def _fill_args(tool_name: str) -> Dict:
    tool = TOOLS_BY_NAME.get(tool_name)
    if not tool:
        return {}
    props = tool["function"]["parameters"]["properties"]
    args = {}
    for key, spec in props.items():
        if key in _ARG_HINTS:
            args[key] = _ARG_HINTS[key]
        elif spec.get("type") == "integer":
            args[key] = 1
        else:
            args[key] = "auto"
    return args


def _extract_json(text: str):
    text = text.strip()
    start = text.find("{")
    if start == -1:
        return None
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start:i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def _json(thought: str, tool: str, arguments: Dict) -> str:
    return json.dumps({"thought": thought, "tool": tool, "arguments": arguments},
                      ensure_ascii=False)


class MockChatClient:
    """确定性脚本模型；接口与 OpenAI 客户端子集兼容。"""

    def __init__(self):
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, model=None, messages=None, temperature=0, **kw):
        content = self._respond(messages or [])
        msg = SimpleNamespace(content=content)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)])

    def _respond(self, messages: List[Dict]) -> str:
        system = messages[0]["content"] if messages and messages[0]["role"] == "system" else ""
        task_prompt = next((m["content"] for m in messages if m["role"] == "user"), "")
        full_text = "\n".join(m.get("content", "") for m in messages)
        has_discover = "discover_tools" in system

        # 当前"可用工具" = 出现在对话文本中的工具名（system 注入 / discover 追加）。
        available = set(re.findall(r'"name":\s*"([a-zA-Z_][a-zA-Z0-9_]*)"', full_text))
        available.discard("discover_tools")

        prior = []
        for m in messages:
            if m["role"] == "assistant":
                a = _extract_json(m.get("content", ""))
                if a and "tool" in a:
                    prior.append(a)
        called_ok = {a["tool"] for a in prior if a["tool"] in available}
        discover_needs = [((a.get("arguments") or {}).get("need", ""))
                          for a in prior if a.get("tool") == "discover_tools"]
        attempted = [a["tool"] for a in prior
                     if a["tool"] not in available and a["tool"] not in ("discover_tools", "finish")]

        for tool, phrase in match_intents(task_prompt):
            if tool in called_ok:
                continue
            if tool in available:
                return _json(f"调用专用工具 {tool}", tool, _fill_args(tool))
            # 目标工具当前不可用
            if has_discover:
                if discover_needs.count(phrase) >= 1:
                    continue  # 已发现过仍未命中 -> 放弃该子任务
                return _json(f"我需要一个能『{phrase}』的工具，先发现它", "discover_tools",
                             {"need": phrase})
            else:
                if attempted.count(tool) >= 1:
                    continue  # 清单里没有该工具，尝试过一次即放弃
                return _json(f"任务需要 {tool}，尝试调用", tool, _fill_args(tool))
        return _json("所有子任务已处理", "finish", {"answer": "已完成可完成的子任务。"})
