"""
四层分层验证 harness。

输入：一条被测 Agent 的运行轨迹（trajectory，schema 见 agent.py），以及对应的任务定义。
输出：四层各自的分数与总评。

四层：
  L1 任务正确性        —— 用 dataset 的 correctness_criteria（规则/判据）核对最终答案。
  L2 工具发现有效性    —— 启发式分析搜索关键词 / 访问网页 / 选库，判断发现是否切题且避开陷阱。
  L3 工具创造质量      —— LLM-as-a-Judge，按 Rubric 给创造出的工具代码打分（错误处理/参数校验/文档）。
  L4 工具复用能力      —— 分析"第二次相似任务"轨迹，是否直接检索已注册工具而非重复搜索创建。
"""

import json
import re
from typing import Optional

from config import Config


# 各层在总评中的权重（若某层 N/A 则在可用层间按比例重新归一）
LAYER_WEIGHTS = {"L1": 0.35, "L2": 0.25, "L3": 0.25, "L4": 0.15}

# 全部四层，供 CLI / 上层选择使用
ALL_LAYERS = ("L1", "L2", "L3", "L4")


# ---------------------------------------------------------------------------
# L1 任务正确性
# ---------------------------------------------------------------------------
def layer1_correctness(task: dict, trajectory: dict) -> dict:
    answer = trajectory.get("final_answer", "") or ""
    crit = task["correctness_criteria"]
    check = crit["check"]
    passed = False
    if check == "regex":
        passed = re.search(crit["pattern"], answer) is not None
    elif check == "contains_any":
        low = answer.lower()
        passed = any(v.lower() in low for v in crit["values"])
    return {
        "score": 1.0 if passed else 0.0,
        "passed": passed,
        "detail": f"判据[{check}] -> {'通过' if passed else '未通过'}；{crit['description']}",
    }


# ---------------------------------------------------------------------------
# L2 工具发现有效性
# ---------------------------------------------------------------------------
def _selected_libraries(trajectory: dict):
    return [s["library"] for s in trajectory["steps"] if s["action"] == "select_library"]


def _search_queries(trajectory: dict):
    return [s["query"] for s in trajectory["steps"] if s["action"] == "search"]


def layer2_discovery(task: dict, trajectory: dict) -> dict:
    steps = trajectory["steps"]
    reused = any(s["action"] == "retrieve_tool" for s in steps)
    did_discovery = any(s["action"] in ("search", "select_library", "create_tool") for s in steps)
    if reused and not did_discovery:
        # 本次是复用，没有新的发现活动 —— 该层不适用
        return {"score": None, "detail": "本次直接复用已注册工具，无新发现活动，L2 不适用。"}

    queries = _search_queries(trajectory)
    selected = _selected_libraries(trajectory)
    kws = [k.lower() for k in task.get("discovery_keywords", [])]
    recommended = [l.lower() for l in task["reference_solution"]["libraries"]]
    pit = task.get("known_pitfalls", {})
    bad_libs = [b.lower() for b in (pit.get("deprecated_libraries", []) + pit.get("paid_or_registration_apis", []))]

    # 各项启发式指标
    on_topic = any(any(k in q.lower() for k in kws) for q in queries) if queries else False
    visited_web = any(s["action"] == "read_web" for s in steps)

    def _match(lib, pool):
        lo = lib.lower()
        return any(p.split("(")[0].strip() in lo or lo in p for p in pool)

    selected_recommended = any(_match(l, recommended) for l in selected)
    hit_pitfall = any(_match(l, bad_libs) for l in selected)
    avoided_pitfalls = not hit_pitfall

    score = (
        0.40 * selected_recommended
        + 0.25 * on_topic
        + 0.25 * avoided_pitfalls
        + 0.10 * visited_web
    )
    return {
        "score": round(score, 3),
        "components": {
            "on_topic_search": on_topic,
            "visited_web": visited_web,
            "selected_recommended_lib": selected_recommended,
            "avoided_pitfalls": avoided_pitfalls,
        },
        "selected_libraries": selected,
        "detail": (
            f"搜索切题={on_topic} 访问网页={visited_web} 选中推荐库={selected_recommended} "
            f"避开陷阱={avoided_pitfalls}（选库：{selected}）"
        ),
    }


# ---------------------------------------------------------------------------
# L3 工具创造质量（LLM-as-a-Judge，按 Rubric）
# ---------------------------------------------------------------------------
_JUDGE_SYSTEM = (
    "你是一名严格的代码评审专家，负责评估一个自我进化 Agent 自动创造的 Python 工具函数的质量。"
    "请只依据给定的代码本身打分，按下面 4 个维度各打 0-3 分（0=完全没有，1=很弱，2=一般，3=优秀）：\n"
    "  error_handling  错误处理：是否用 try/except 处理网络/IO/解析等异常，给出有用信息。\n"
    "  input_validation 参数校验：是否检查入参类型/取值/边界，非法输入是否报错。\n"
    "  documentation   文档完整性：是否有清晰 docstring 说明用途、参数、返回、异常。\n"
    "  robustness      健壮性与契合度：实现是否契合任务目标、是否考虑边界与失败情形。\n"
    "只返回 JSON，形如："
    '{"error_handling":int,"input_validation":int,"documentation":int,"robustness":int,"comment":"简短中文点评"}'
)


def _parse_judge_json(text: str) -> Optional[dict]:
    """Parse judge output as a rubric object. Arrays/scalars → None (not crash)."""
    def _as_dict(obj):
        return obj if isinstance(obj, dict) else None

    try:
        return _as_dict(json.loads(text))
    except Exception:
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if m:
            try:
                return _as_dict(json.loads(m.group(0)))
            except Exception:
                return None
    return None


def _rubric_dimension_total(rubric: dict) -> int:
    """Sum 0-3 rubric dims; missing/None count as 0 (not other falsy JSON)."""
    dims = ["error_handling", "input_validation", "documentation", "robustness"]
    return sum(int(v) if v is not None else 0 for v in (rubric.get(d) for d in dims))


def layer3_tool_quality(task: dict, trajectory: dict, judge_model: Optional[str] = None) -> dict:
    created = trajectory.get("created_tools", [])
    if not created:
        return {"score": None, "detail": "本次轨迹未创造新工具（可能为复用），L3 不适用。"}

    tool = created[0]
    model = Config.map_model(judge_model or Config.JUDGE_MODEL)
    client = Config.get_client()
    user = (
        f"任务目标：{task['goal']}\n\n"
        f"Agent 创造的工具函数 `{tool['name']}` 代码如下：\n```python\n{tool['code']}\n```"
    )
    kwargs = dict(
        model=model,
        temperature=0.0,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": user},
        ],
    )
    try:
        resp = client.chat.completions.create(response_format={"type": "json_object"}, **kwargs)
    except Exception:
        resp = client.chat.completions.create(**kwargs)  # 部分模型不支持 json_object
    raw = resp.choices[0].message.content or ""
    rubric = _parse_judge_json(raw)
    if not rubric:
        return {"score": 0.0, "rubric": None, "judge_text": raw, "detail": "judge 输出无法解析为 JSON。"}

    dims = ["error_handling", "input_validation", "documentation", "robustness"]
    total = _rubric_dimension_total(rubric)
    score = round(total / (3 * len(dims)), 3)
    return {
        "score": score,
        "rubric": rubric,
        "judge_text": raw,
        "tool_name": tool["name"],
        "detail": (
            f"Rubric 4 维合计 {total}/12 -> 归一 {score}；"
            f"点评：{rubric.get('comment', '')}"
        ),
    }


# ---------------------------------------------------------------------------
# L4 工具复用能力（分析第二次相似任务的轨迹）
# ---------------------------------------------------------------------------
def layer4_reuse(task: dict, variant_trajectory: dict) -> dict:
    if variant_trajectory is None:
        return {"score": None, "detail": "未提供第二次相似任务轨迹，L4 未测。"}
    steps = variant_trajectory["steps"]
    retrieved = any(
        s["action"] == "retrieve_tool" and s.get("name") == task["tool_name"] for s in steps
    )
    re_searched = any(s["action"] == "search" for s in steps)
    re_created = any(s["action"] == "create_tool" for s in steps)

    if retrieved and not re_searched and not re_created:
        score, verdict = 1.0, "直接检索并复用已注册工具（未重复搜索/创建）"
    elif retrieved and (re_searched or re_created):
        score, verdict = 0.5, "检索到工具但仍有重复搜索/创建"
    else:
        score, verdict = 0.0, "未复用，重复了搜索与工具创建"
    return {
        "score": score,
        "retrieved_from_registry": retrieved,
        "re_searched": re_searched,
        "re_created": re_created,
        "detail": verdict,
    }


# ---------------------------------------------------------------------------
# 汇总
# ---------------------------------------------------------------------------
def aggregate(layers: dict) -> dict:
    avail = {k: v["score"] for k, v in layers.items() if v.get("score") is not None}
    if not avail:
        return {"overall": None, "used_layers": []}
    wsum = sum(LAYER_WEIGHTS[k] for k in avail)
    overall = sum(LAYER_WEIGHTS[k] * s for k, s in avail.items()) / wsum
    return {"overall": round(overall, 3), "used_layers": list(avail)}


class FourLayerEvaluator:
    """把四层封装到一起。variant_trajectory 用于 L4。

    layers 指定实际运行哪些层（默认四层全跑）。只有 L3 需要联网调用 LLM，
    因此离线场景可传 layers=("L1","L2","L4") 跳过 L3——未选中的层记 N/A，不参与总评。"""

    def __init__(self, judge_model: Optional[str] = None, layers=ALL_LAYERS):
        self.judge_model = judge_model or Config.JUDGE_MODEL
        self.layers = tuple(layers)

    def evaluate(self, task: dict, trajectory: dict, variant_trajectory: Optional[dict] = None) -> dict:
        skipped = {"score": None, "detail": "（本次未选择该层，记 N/A）"}
        layers = {
            "L1": layer1_correctness(task, trajectory) if "L1" in self.layers else dict(skipped),
            "L2": layer2_discovery(task, trajectory) if "L2" in self.layers else dict(skipped),
            "L3": (
                layer3_tool_quality(task, trajectory, self.judge_model)
                if "L3" in self.layers else dict(skipped)
            ),
            "L4": layer4_reuse(task, variant_trajectory) if "L4" in self.layers else dict(skipped),
        }
        return {
            "task_id": task["id"],
            "domain": task["domain"],
            "profile": trajectory.get("profile"),
            "layers": layers,
            "summary": aggregate(layers),
        }
