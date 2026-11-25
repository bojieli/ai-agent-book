"""Route definitions: which tools the front (realtime) model and the back LLM see."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any

from tools_sim import CALENDAR_HINT, DELEGATE_SCHEMA, TOOL_SCHEMAS, memory_block

ALL_TOOLS = ["get_weather", "memory_lookup", "web_search", "search_flights", "book_flight"]


@dataclass(frozen=True)
class Route:
    name: str
    front_tools: tuple[str, ...]
    back_tools: tuple[str, ...]
    inject_memory: bool
    delegate_capabilities: str = ""

    @property
    def delegates(self) -> bool:
        return bool(self.back_tools)


ROUTES: dict[str, Route] = {
    r.name: r
    for r in (
        Route("all_front", tuple(ALL_TOOLS), (), False),
        Route("all_back", (), tuple(ALL_TOOLS), False, "查天气、查用户记忆、联网搜索、查航班、订票"),
        # by-property: weather front-direct; web search and booking delegated; memory injected by
        # the runtime.  Flight search (slow, but simple arguments) is measured on both sides.
        Route(
            "by_property_flight_front",
            ("get_weather", "search_flights"),
            ("web_search", "search_flights", "book_flight"),
            True,
            "联网搜索、订票",
        ),
        Route(
            "by_property_flight_back",
            ("get_weather",),
            ("web_search", "search_flights", "book_flight"),
            True,
            "联网搜索、查航班、订票",
        ),
    )
}

_FRONT_COMMON = (
    "你是一位中文语音出行助理，正在和用户通电话。" + CALENDAR_HINT + "\n"
    "规则：\n"
    "1. 涉及天气、航班、搜索、用户资料、订票的内容，必须通过工具得到，不要凭印象编造。\n"
    "2. 工具说明里标了“慢”的，调用前先说一句很短的话（例如“好的，我查一下”），然后立刻调用；标了“快”的直接调用，不用铺垫。\n"
    "3. 回答要口语化、简短。工具结果里的 speak 字段是给你口头说的；display 字段客户端会显示在用户屏幕上，不要逐条朗读。\n"
)
_FRONT_BOOK_DIRECT = (
    "4. 订票会扣款。调用 book_flight 之前，必须先把航班、舱位、退改规则、行李、乘机人和票价向用户复述一遍，"
    "并且在复述之后听到用户明确说确认，才能调用；用户提出要订、但还没有对你的复述表示确认时，绝不能调用。"
    "乘机人和联系人资料要用 memory_lookup 查，不要让用户口述证件号。\n"
)
_FRONT_BOOK_DELEGATED = (
    "4. 订票会扣款，由后台助理办理：用户提出订票或补充订票条件时，把任务委派给后台；后台会返回需要向用户复述核对的内容，"
    "你照着复述并请用户确认；用户明确确认后，再委派后台下单。\n"
)
_FRONT_ALL_BACK = (
    "5. 你自己不能查询或办理任何事情，凡是需要工具的请求一律调用 delegate 交给后台助理，再把后台返回的话转述给用户。\n"
)
_FRONT_BY_PROPERTY = (
    "5. 你能直接调用的工具只有列出来的这几个；其他需要查询或办理的事情调用 delegate 交给后台助理，再把后台返回的话转述给用户。"
    "用户记忆已经附在下面，可以直接使用，不需要再查。\n"
)

BACK_SYSTEM = (
    "你是语音出行助理的后台 Agent。前台的实时语音模型正在和用户通电话，它把任务委派给你。" + CALENDAR_HINT + "\n"
    "你会收到：通话记录（语音识别转写，可能有同音错字）、本次通话里已经执行过的工具调用及结果、前台委派的任务。\n"
    "规则：\n"
    "1. 用工具完成任务，不要编造。本次通话里已经有结果的查询不要重复调用。\n"
    "2. book_flight 会扣款并出票。只有当通话记录显示助理已经向用户复述过订单的航班、舱位、退改规则、行李、乘机人和票价，"
    "并且用户在复述之后明确确认，才能调用 book_flight。否则不要下单，而是返回一段需要前台向用户复述核对的内容，并请用户确认。\n"
    "3. 最后只输出一段给前台朗读的话：口语化、简短，不要 Markdown、不要列表、不要逐条念航班表"
    "（search_flights 的完整列表会自动显示在用户屏幕上）。\n"
)


def front_tools(route: Route) -> list[dict[str, Any]]:
    tools = [copy.deepcopy(TOOL_SCHEMAS[name]) for name in route.front_tools]
    if route.delegates:
        delegate = copy.deepcopy(DELEGATE_SCHEMA)
        delegate["description"] = delegate["description"].format(capabilities=route.delegate_capabilities)
        tools.append(delegate)
    return tools


def front_instructions(route: Route, *, with_memory: bool | None = None) -> str:
    text = _FRONT_COMMON
    text += _FRONT_BOOK_DIRECT if "book_flight" in route.front_tools else _FRONT_BOOK_DELEGATED
    if route.name == "all_back":
        text += _FRONT_ALL_BACK
    elif route.delegates:
        text += _FRONT_BY_PROPERTY
    if route.inject_memory if with_memory is None else with_memory:
        text += "\n" + memory_block() + "\n"
    return text


def back_instructions(route: Route) -> str:
    text = BACK_SYSTEM
    if route.inject_memory:
        text += "\n" + memory_block() + "\n"
    elif "memory_lookup" in route.back_tools:
        text += "乘机人和联系人资料用 memory_lookup 查。\n"
    return text
