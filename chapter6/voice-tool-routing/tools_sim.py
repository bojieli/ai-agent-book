"""SIMULATED tools for the voice tool-routing experiment.

Nothing in this module talks to a real weather, search, airline or memory
service.  Every result is a deterministic fixture and every latency is injected
with ``asyncio.sleep`` so that differences between routes come from the models
and the routing, not from live back ends.  All people, card numbers, document
numbers, offers and orders below are fictional.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import random
from typing import Any

SIMULATED = True
LATENCY_SEED = 20261125

# Fixed "today" given to every model so that reruns on another day are comparable.
TODAY = "2026-11-25"
CALENDAR_HINT = (
    "今天是2026年11月25日，星期三；明天是11月26日，星期四；"
    "下周三是12月2日，下周四是12月3日，下周五是12月4日。"
)

# ----------------------------------------------------------------- latencies
FIXED_LATENCY = {"get_weather": 0.2, "memory_lookup": 0.02, "web_search": 3.0}
SAMPLED_LATENCY = {"search_flights": (2.0, 5.0), "book_flight": (2.0, 5.0)}


def latency_for(tool: str, scenario: str, run_index: int, nth_call: int) -> float:
    """Injected latency in seconds.

    The 2-5 s latencies are drawn from a seeded generator keyed by scenario, run
    index, tool and the ordinal of the call inside the session.  The route is
    deliberately *not* part of the key: every route sees the same sequence.
    """
    if tool in FIXED_LATENCY:
        return FIXED_LATENCY[tool]
    low, high = SAMPLED_LATENCY[tool]
    rng = random.Random(f"{LATENCY_SEED}:{scenario}:{run_index}:{tool}:{nth_call}")
    return round(rng.uniform(low, high), 3)


# -------------------------------------------------------------------- memory
PROFILE = {
    "name": "周明远",
    "id_type": "passport",
    "id_number": "EK3927461",
    "phone": "13671928840",
    "email": "zhou.mingyuan@example.com",
}
MEMORY = {
    "passenger_profile": (
        "用户本人的乘机人资料：姓名 周明远；证件类型 护照(passport)；证件号 EK3927461；"
        "手机 13671928840；邮箱 zhou.mingyuan@example.com。"
    ),
    "frequent_flyer": "用户的国航凤凰知音常旅客卡号是 CA 8839 2201 57。",
    "seat_preference": "用户偏好靠过道的座位。",
}
MEMORY_TOPICS = list(MEMORY)
FREQUENT_FLYER_DIGITS = "8839220157"


def memory_block() -> str:
    """What the runtime injects in the by-property route (whole store; it is tiny)."""
    return "【运行时自动检索到的用户记忆，可直接使用】\n" + "\n".join(f"- {v}" for v in MEMORY.values())


# ------------------------------------------------------------------- weather
WEATHER = {
    ("杭州", "2026-11-26"): "杭州11月26日多云转晴，9到17度，东北风3级，降水概率10%。",
    ("上海", "2026-12-03"): "上海12月3日阴有小雨，8到13度，东风3到4级，降水概率70%。",
    ("上海", "2026-12-04"): "上海12月4日多云，7到14度，北风2级，降水概率20%。",
}

# ---------------------------------------------------------------- web search
WEB_SEARCH_RESULT = (
    "【模拟搜索结果，共4条】\n"
    "1. 出行攻略｜虹桥机场到国家会展中心（上海）怎么走：两地都在虹桥商务区，直线距离约3公里。"
    "最快的公共交通是地铁2号线：在虹桥2号航站楼站上车，往徐泾东方向坐2站，经虹桥火车站到终点徐泾东站，"
    "车程约6分钟，票价3元；徐泾东站4、5、6号口出站就是会展中心南广场，步行约5分钟。"
    "算上进站和候车，门到门大约20分钟。地铁首班车约5点半，末班车约22点45分。"
    "如果从1号航站楼出发，要先坐机场免费摆渡车或地铁10号线到2号航站楼换乘，多花15分钟左右。\n"
    "2. 网约车与出租车：不堵车时走崧泽高架约10到15分钟，费用25到35元；"
    "但大型展会期间（如进博会、车展）会展中心周边实行交通管制，上下客点离展馆入口较远，"
    "早晚高峰可能要40分钟以上，司机也常常不愿意接短途单。\n"
    "3. 论坛讨论：有网友说展会期间地铁徐泾东站会限流，建议避开9点到10点的入场高峰；"
    "也有人推荐从虹桥火车站沿二层步廊步行到会展中心，大约25到30分钟，全程有顶棚，下雨也不怕。"
    "还有人提到71路中运量公交可以到会展中心附近，但要绕行，不推荐赶时间的人坐。\n"
    "4. 广告：会展中心周边酒店特惠，四星级酒店展期每晚680元起，含双早，提前预订享免费接送机服务。"
)

# ------------------------------------------------------------------- flights
_FLIGHT_TABLE = {
    "2026-12-02": [
        ("CA1501", "07:30", "09:45", "首都T3", "虹桥T2", 700, 930, 2300, "3N8D"),
        ("MU5103", "09:00", "11:15", "首都T2", "虹桥T2", 740, 950, 2280, "5T1W"),
        ("HU7605", "11:20", "13:40", "首都T2", "浦东T2", 660, 890, 2190, "8C4J"),
        ("CZ8889", "14:10", "16:30", "大兴", "虹桥T2", 780, 1010, 2420, "2R9X"),
        ("MU5119", "18:00", "20:20", "首都T2", "虹桥T2", 810, 1040, 2480, "6H7M"),
        ("CA1885", "21:05", "23:20", "首都T3", "浦东T2", 690, 920, 2260, "9Q2B"),
    ],
    "2026-12-03": [
        ("CA1501", "07:30", "09:45", "首都T3", "虹桥T2", 720, 960, 2380, "4F6P"),
        ("MU5103", "09:00", "11:15", "首都T2", "虹桥T2", 680, 910, 2250, "7K2Q"),
        ("HU7605", "11:20", "13:40", "首都T2", "浦东T2", 760, 990, 2460, "1V5Z"),
        ("CZ8889", "14:10", "16:30", "大兴", "虹桥T2", 790, 1020, 2440, "8L3G"),
        ("MU5119", "18:00", "20:20", "首都T2", "虹桥T2", 830, 1060, 2520, "2Y9S"),
        ("CA1885", "21:05", "23:20", "首都T3", "浦东T2", 710, 940, 2300, "6D8N"),
    ],
    "2026-12-04": [
        ("CA1501", "07:30", "09:45", "首都T3", "虹桥T2", 750, 980, 2400, "5J2U"),
        ("MU5103", "09:00", "11:15", "首都T2", "虹桥T2", 770, 1000, 2350, "3A7E"),
        ("HU7605", "11:20", "13:40", "首都T2", "浦东T2", 650, 880, 2210, "9W4K"),
        ("CZ8889", "14:10", "16:30", "大兴", "虹桥T2", 800, 1030, 2460, "1M6R"),
        ("MU5119", "18:00", "20:20", "首都T2", "虹桥T2", 840, 1070, 2540, "7B3H"),
        ("CA1885", "21:05", "23:20", "首都T3", "浦东T2", 730, 950, 2320, "4X8C"),
    ],
}
_AIRLINES = {"CA": "国航", "MU": "东航", "HU": "海航", "CZ": "南航"}


def offer_id(date: str, flight_no: str, suffix: str) -> str:
    return f"OFR-{date[5:7]}{date[8:10]}-{flight_no}-{suffix}"


def flight_rows(date: str) -> list[dict[str, Any]]:
    rows = []
    for flight_no, dep, arr, dep_ap, arr_ap, basic, flex, business, suffix in _FLIGHT_TABLE[date]:
        rows.append(
            {
                "offer_id": offer_id(date, flight_no, suffix),
                "flight_no": flight_no,
                "airline": _AIRLINES[flight_no[:2]],
                "depart": dep,
                "arrive": arr,
                "from": dep_ap,
                "to": arr_ap,
                "fares": [
                    {"cabin": "economy", "fare_rule": "basic", "price_cny": basic, "note": "不可退改，含20公斤托运"},
                    {"cabin": "economy", "fare_rule": "flexible", "price_cny": flex, "note": "起飞前免费退改，含20公斤托运"},
                    {"cabin": "business", "fare_rule": "flexible", "price_cny": business, "note": "免费退改，含2件32公斤托运"},
                ],
            }
        )
    return rows


def flight_speak(date: str) -> str:
    rows = flight_rows(date)
    cheapest = min(rows, key=lambda r: r["fares"][0]["price_cny"])
    month, day = int(date[5:7]), int(date[8:10])
    return (
        f"{month}月{day}日北京到上海有{len(rows)}个直飞航班，最早{rows[0]['depart']}，最晚{rows[-1]['depart']}。"
        f"经济舱最低{cheapest['fares'][0]['price_cny']}元，是{cheapest['airline']}{cheapest['flight_no']}，"
        f"{cheapest['depart']}从{cheapest['from']}起飞，{cheapest['arrive']}到{cheapest['to']}。完整列表已经显示在屏幕上。"
    )


def cheapest_price(date: str) -> int:
    return min(r["fares"][0]["price_cny"] for r in flight_rows(date))


# ---------------------------------------------------------------- execution
ORDERS: "list[dict[str, Any]]" = []  # only used by offline tests; sessions keep their own ledger


def execute(name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Return the simulated result (without latency).  Never raises on bad args."""
    if name == "get_weather":
        text = WEATHER.get((str(args.get("city", "")).strip(), str(args.get("date", "")).strip()))
        if text is None:
            return {"error": f"模拟天气服务没有 {args.get('city')} {args.get('date')} 的数据"}
        return {"speak": text}
    if name == "memory_lookup":
        topic = str(args.get("topic", "")).strip()
        if topic not in MEMORY:
            return {"error": f"没有主题 {topic!r} 的记忆，可用主题：{', '.join(MEMORY_TOPICS)}"}
        return {"memory": MEMORY[topic]}
    if name == "web_search":
        return {"results": WEB_SEARCH_RESULT}
    if name == "search_flights":
        date = str(args.get("date", "")).strip()
        origin = str(args.get("origin", "")).strip()
        destination = str(args.get("destination", "")).strip()
        if date not in _FLIGHT_TABLE or origin != "北京" or destination != "上海":
            return {"error": f"模拟航班服务没有 {origin}->{destination} {date} 的数据", "speak": "没有查到符合条件的航班。", "display": []}
        return {"speak": flight_speak(date), "display": flight_rows(date)}
    if name == "book_flight":
        # Deliberately lenient: a wrong argument still produces an order, so that
        # wrong bookings show up in the ledger instead of being masked by a retry.
        digest = hashlib.sha256(json.dumps(args, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:8].upper()
        order_id = f"ORD-{digest}"
        return {
            "status": "confirmed",
            "order_id": order_id,
            "speak": f"订单已提交成功，订单号 {order_id}，电子行程单会发到联系人邮箱。",
            "side_effect": "模拟扣款并出票",
        }
    return {"error": f"未知工具 {name}"}


async def run_tool(name: str, args: dict[str, Any], latency: float) -> dict[str, Any]:
    await asyncio.sleep(latency)
    return execute(name, args)


# ------------------------------------------------------------- JSON schemas
def _fn(name: str, description: str, properties: dict[str, Any], required: list[str]) -> dict[str, Any]:
    return {
        "type": "function",
        "name": name,
        "description": description,
        "parameters": {"type": "object", "properties": properties, "required": required},
    }


TOOL_SCHEMAS: dict[str, dict[str, Any]] = {
    "get_weather": _fn(
        "get_weather",
        "【快，约0.2秒】查询某城市某一天的天气。",
        {
            "city": {"type": "string", "description": "城市名，不带“市”字，例如 杭州"},
            "date": {"type": "string", "description": "日期，格式 YYYY-MM-DD"},
        },
        ["city", "date"],
    ),
    "memory_lookup": _fn(
        "memory_lookup",
        "【快，约0.02秒】查询关于这位用户的长期记忆。passenger_profile=本人乘机人资料（姓名、证件、手机、邮箱）；"
        "frequent_flyer=常旅客卡号；seat_preference=座位偏好。",
        {"topic": {"type": "string", "enum": MEMORY_TOPICS, "description": "记忆主题"}},
        ["topic"],
    ),
    "web_search": _fn(
        "web_search",
        "【慢，约3秒】联网搜索，返回较长的网页摘要文本，需要你提炼后口头回答。",
        {"query": {"type": "string", "description": "搜索关键词"}},
        ["query"],
    ),
    "search_flights": _fn(
        "search_flights",
        "【慢，2到5秒】查询某天的直飞航班。返回 speak（给你念的一句话摘要）和 display（完整航班表，"
        "客户端会自动显示在用户屏幕上，不需要逐条朗读；其中的 offer_id 和价格在订票时要用）。",
        {
            "origin": {"type": "string", "description": "出发城市，不带“市”字，例如 北京"},
            "destination": {"type": "string", "description": "到达城市，不带“市”字，例如 上海"},
            "date": {"type": "string", "description": "出发日期，格式 YYYY-MM-DD"},
        },
        ["origin", "destination", "date"],
    ),
    "book_flight": _fn(
        "book_flight",
        "【慢，2到5秒；有副作用：会扣款并出票】为用户下单订票。只能在向用户复述订单并得到明确确认之后调用。",
        {
            "offer_id": {"type": "string", "description": "search_flights 结果中该航班的 offer_id，原样填写"},
            "cabin": {"type": "string", "enum": ["economy", "business"], "description": "舱位"},
            "fare_rule": {"type": "string", "enum": ["basic", "flexible"], "description": "basic=不可退改；flexible=可免费退改"},
            "quoted_price_cny": {"type": "integer", "description": "search_flights 结果中该航班、该舱位、该退改规则对应的票价（元）"},
            "baggage": {
                "type": "object",
                "description": "额外加购的托运行李；不加购则 extra_checked_pieces 为 0",
                "properties": {
                    "extra_checked_pieces": {"type": "integer", "description": "加购件数"},
                    "weight_kg": {"type": "integer", "description": "每件重量（公斤）"},
                },
                "required": ["extra_checked_pieces", "weight_kg"],
            },
            "passengers": {
                "type": "array",
                "description": "乘机人列表",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string", "description": "证件上的姓名"},
                        "id_type": {"type": "string", "enum": ["id_card", "passport"], "description": "证件类型"},
                        "id_number": {"type": "string", "description": "证件号"},
                        "phone": {"type": "string", "description": "手机号，11位数字"},
                    },
                    "required": ["name", "id_type", "id_number", "phone"],
                },
            },
            "contact": {
                "type": "object",
                "description": "订单联系人",
                "properties": {
                    "name": {"type": "string"},
                    "phone": {"type": "string", "description": "手机号，11位数字"},
                    "email": {"type": "string"},
                },
                "required": ["name", "phone", "email"],
            },
        },
        ["offer_id", "cabin", "fare_rule", "quoted_price_cny", "baggage", "passengers", "contact"],
    ),
}

DELEGATE_SCHEMA = _fn(
    "delegate",
    "【慢，需要等待】把任务交给后台助理处理。后台助理能看到完整的通话记录，并且可以{capabilities}。"
    "用一句话说清楚要办什么；后台办完会返回一段话，你把它转述给用户。",
    {"task": {"type": "string", "description": "要后台完成的任务，用自然语言描述，带上用户刚才提到的关键条件"}},
    ["task"],
)


def to_openai_tool(schema: dict[str, Any]) -> dict[str, Any]:
    return {
        "type": "function",
        "function": {"name": schema["name"], "description": schema["description"], "parameters": schema["parameters"]},
    }
