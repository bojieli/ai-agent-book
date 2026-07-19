"""
三种工具发现策略的 Agent 循环（文本/ReAct 协议）。

为什么用"文本注入 + 文本解析工具调用"而不是 OpenAI 原生 function calling？
—— 本实验要复现的正是书中所述：把 120+ 工具 schema **一次性注入 system prompt（几万 token）**，
   模型在超长上下文下"指令遵循退化"。OpenAI 原生 function-calling 接口对工具选择做了很强的
   约束/优化，即使上百个工具也很少选错，无法体现该退化；而把 schema 当作纯文本塞进 prompt、
   让模型自己以 JSON 形式输出工具调用，才是书中控制组的真实机制，也才能观察到退化。

协议：模型每一步只输出一个 JSON：
    {"thought": "...", "tool": "工具名", "arguments": {...}}
任务完成时输出：
    {"thought": "...", "tool": "finish", "arguments": {"answer": "..."}}

1) run_full_injection —— 对照组（全量注入）
   system prompt 里以文本列出全部 126 个工具。injected_tokens = 该工具清单文本的 token 数。

2) run_retrieval_prefilter —— 对照组之二（检索预筛选）
   按用户初始查询做**一次性**语义检索，只把 top-n 个候选工具注入 system prompt。
   token 已大幅下降，但一次性匹配无法预见执行中才浮现的跨领域需求（书中所述局限）。

3) run_active_discovery —— 实验组（主动发现）
   system prompt 只列出少量基础工具 + discover_tools 元工具。
   模型调用 discover_tools(need) 时，用嵌入相似度返回 3-5 个候选工具，其文本清单作为
   **user message** 追加进对话（保护 system 前缀 KV Cache），并更新状态栏可用工具列表。
   injected_tokens = 基础工具 + discover_tools + 实际发现加载的工具清单的 token 数。
"""

import json
import re
from typing import Dict, List

import tiktoken

from discovery import ToolIndex  # noqa: F401  (类型提示用)
from tools_library import (ALL_TOOLS, BASE_TOOL_NAMES, TOOL_IMPLS,
                           TOOLS_BY_NAME)

try:
    _ENC = tiktoken.get_encoding("o200k_base")  # gpt-4o 系列编码
except Exception:
    _ENC = tiktoken.get_encoding("cl100k_base")


# ---------------------------------------------------------------------------
# 工具清单文本渲染 & token 统计
# ---------------------------------------------------------------------------

def render_tool(tool: Dict) -> str:
    """把单个工具渲染成完整 JSON schema 文本（与真实注入到 prompt 的形式一致）。"""
    return json.dumps(tool["function"], ensure_ascii=False, indent=2)


def render_tools(tools: List[Dict]) -> str:
    return "\n".join(render_tool(t) for t in tools)


def count_tokens(text: str) -> int:
    return len(_ENC.encode(text)) if text else 0


# discover_tools 元工具（也用文本形式呈现给模型）
DISCOVER_TOOL = {
    "type": "function",
    "function": {
        "name": "discover_tools",
        "description": ("发现新工具：当缺少合适的专用工具时调用它，用一句自然语言描述你需要的"
                        "『能力』(need)，系统会用语义检索返回最匹配的若干专用工具及其定义，之后即可调用它们。"),
        "parameters": {"type": "object",
                       "properties": {"need": {"type": "string"}}, "required": ["need"]},
    },
}

FINISH_TOOL_DESC = "- finish(answer: string): 所有子任务都完成后调用，给出最终回答。"


_PROTOCOL = (
    "你每一步都必须、且只能输出一个 JSON 对象，不要输出任何多余文字，格式为：\n"
    '{"thought": "简要思考", "tool": "工具名", "arguments": {参数键值}}\n'
    "系统会执行该工具并把结果返回给你，然后你再输出下一步。\n"
    "当且仅当任务的所有子任务都已用合适的工具完成后，输出："
    '{"thought": "...", "tool": "finish", "arguments": {"answer": "最终回答"}}\n'
    "注意：请为每个子任务选择最匹配的『专用工具』，而不是笼统的通用搜索工具。"
)


def _extract_json(text: str):
    """从模型回复里抽取第一个 JSON 对象。"""
    text = text.strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    # 找到第一个 { 到匹配的 }
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


def _run_loop(client, model, system_prompt, task_prompt, available_names,
              on_discover=None, max_steps=10):
    """
    文本 ReAct 循环。
    available_names: set，当前允许调用的工具名（不含 discover_tools/finish）。
      —— 主动发现模式下会随 discover_tools 动态增长。
    返回 (called_tools, trace, finished)。
    """
    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": task_prompt}]
    called: List[str] = []
    trace: List[str] = []
    finished = False

    for _ in range(max_steps):
        try:
            resp = client.chat.completions.create(
                model=model, messages=messages, temperature=0)
        except Exception as e:
            # 部分推理型模型（如 gpt-5.x）只支持默认 temperature=1，此时退回默认值重试。
            if "temperature" in str(e):
                resp = client.chat.completions.create(
                    model=model, messages=messages)
            else:
                raise
        content = resp.choices[0].message.content or ""
        messages.append({"role": "assistant", "content": content})

        action = _extract_json(content)
        if action is None or "tool" not in action:
            trace.append(f"[格式错误] 模型未输出合法 JSON: {content[:80]!r}")
            messages.append({"role": "user",
                             "content": "你的回复不是合法的 JSON，请只输出规定格式的 JSON 对象。"})
            continue

        name = action.get("tool")
        args = action.get("arguments") or {}

        if name == "finish":
            trace.append(f"[finish] {str(args.get('answer',''))[:100]}")
            finished = True
            break

        if name == "discover_tools" and on_discover is not None:
            need = args.get("need", "")
            result_text, new_names = on_discover(need)
            called.append(name)
            trace.append(f"[discover_tools] need='{need}' -> {new_names}")
            available_names.update(new_names)
            messages.append({"role": "user", "content": result_text})
            continue

        # 普通工具调用
        if name not in available_names:
            # 该工具当前不可用（主动发现里还没发现 / 预筛选没选中 / 或纯属幻觉）——
            # 不计入 called（未真正执行），判分因此能体现该子任务失败。
            trace.append(f"[不可用] {name}")
            hint = ("该工具当前不可用。"
                    + ("请先用 discover_tools 发现所需能力的工具。" if on_discover else
                       "请从工具清单中选择一个存在的工具。"))
            messages.append({"role": "user", "content": hint})
            continue

        called.append(name)
        impl = TOOL_IMPLS.get(name)
        result = impl(args) if impl else json.dumps({"error": f"unknown tool {name}"})
        trace.append(f"[call] {name}({json.dumps(args, ensure_ascii=False)})")
        messages.append({"role": "user", "content": f"工具 {name} 返回：{result}"})

    return called, trace, finished


# ---------------------------------------------------------------------------
# 对照组：全量注入
# ---------------------------------------------------------------------------

def run_full_injection(client, model, task_prompt: str, tools: List[Dict] = None,
                       max_steps: int = 10) -> Dict:
    tools = tools if tools is not None else ALL_TOOLS
    tools_text = render_tools(tools) + "\n" + FINISH_TOOL_DESC
    injected = count_tokens(tools_text)
    system = (
        f"你是一个智能助手。下面是你可以使用的全部工具清单（共 {len(tools)} 个），"
        "请根据任务选择最合适的工具来完成。若任务包含多个子任务，请确保每个子任务都被处理。\n\n"
        "【工具清单】\n" + tools_text + "\n\n" + _PROTOCOL
    )
    available = {t["function"]["name"] for t in tools}
    called, trace, finished = _run_loop(client, model, system, task_prompt, available,
                                        max_steps=max_steps)
    return {"mode": "full_injection", "injected_tokens": injected,
            "num_tools_exposed": len(tools), "called": called,
            "trace": trace, "finished": finished}


# ---------------------------------------------------------------------------
# 对照组之二：检索预筛选（书中"检索式预筛选"）
#   —— 按用户初始查询做**一次性**语义检索，只把 top-n 个候选工具注入 system prompt。
#      它介于"全量注入"与"主动发现"之间：token 已大幅下降，但只匹配一次，无法预见
#      任务执行中才浮现的跨领域需求（书中所述的内在局限）——若第二个子任务所需的
#      专用工具没被这一次检索选中，模型就无从调用它，导致该子任务失败。
# ---------------------------------------------------------------------------

def run_retrieval_prefilter(client, model, task_prompt: str, index, top_n: int = 10,
                            tools: List[Dict] = None, max_steps: int = 10) -> Dict:
    tools = tools if tools is not None else ALL_TOOLS
    tbn = {t["function"]["name"]: t for t in tools}
    hits = index.search(task_prompt, top_k=top_n)
    picked = [name for name, _ in hits if name in tbn]
    picked_tools = [tbn[n] for n in picked]
    tools_text = render_tools(picked_tools) + "\n" + FINISH_TOOL_DESC
    injected = count_tokens(tools_text)
    system = (
        f"你是一个智能助手。系统已根据你的任务预先检索出下列可能相关的工具（共 {len(picked_tools)} 个），"
        "请从中选择合适的工具完成任务。若某个子任务在清单中找不到合适的工具，请如实说明。\n\n"
        "【工具清单】\n" + tools_text + "\n\n" + _PROTOCOL
    )
    available = set(picked)
    called, trace, finished = _run_loop(client, model, system, task_prompt, available,
                                        max_steps=max_steps)
    return {"mode": "retrieval_prefilter", "injected_tokens": injected,
            "num_tools_exposed": len(picked_tools), "prefiltered": picked,
            "called": called, "trace": trace, "finished": finished}


# ---------------------------------------------------------------------------
# 实验组：主动发现
# ---------------------------------------------------------------------------

def run_active_discovery(client, model, task_prompt: str, index, top_k=4,
                         tools: List[Dict] = None, max_steps: int = 10) -> Dict:
    tools = tools if tools is not None else ALL_TOOLS
    tbn = {t["function"]["name"]: t for t in tools}
    base_tools = [tbn[n] for n in BASE_TOOL_NAMES]
    base_text = (render_tools(base_tools) + "\n"
                 + render_tool(DISCOVER_TOOL) + "\n" + FINISH_TOOL_DESC)

    discovered_names = set()          # 本轮实际发现加载的专用工具
    discovered_texts: List[str] = []  # 对应的文本清单（用于统计按需注入 token）
    available = set(BASE_TOOL_NAMES)

    def on_discover(need: str):
        hits = index.search(need, top_k=top_k)
        names, lines = [], []
        for name, score in hits:
            if name in BASE_TOOL_NAMES:
                continue
            names.append(name)
            lines.append(render_tool(tbn[name]) + f"   (相似度 {score:.3f})")
            if name not in discovered_names:
                discovered_names.add(name)
                discovered_texts.append(render_tool(tbn[name]))
        status = f"\n\n【状态栏｜当前可用工具】{sorted(available | set(names))}"
        body = ("discover_tools 匹配到以下专用工具，已加载，可直接调用：\n"
                + "\n".join(lines) + status)
        return body, names

    system = (
        "你是一个智能助手。你当前只掌握少量基础工具（见下）。"
        "当任务需要你没有的能力时，先调用 discover_tools，用自然语言描述你需要的能力，"
        "系统会返回并加载匹配的专用工具，然后你再调用它们。"
        "若任务包含多个子任务（如既要查询又要下载），请针对每一项能力分别调用 discover_tools，"
        "并在结束前确认每个子任务都已用合适的工具完成。\n\n"
        "【基础工具】\n" + base_text + "\n\n" + _PROTOCOL
    )
    called, trace, finished = _run_loop(client, model, system, task_prompt,
                                        available, on_discover=on_discover,
                                        max_steps=max_steps)

    injected = count_tokens(base_text) + count_tokens("\n".join(discovered_texts))
    return {"mode": "active_discovery", "injected_tokens": injected,
            "num_tools_exposed": len(BASE_TOOL_NAMES) + 1 + len(discovered_names),
            "discovered": sorted(discovered_names),
            "called": called, "trace": trace, "finished": finished}
