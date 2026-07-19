"""
参考被测 Agent（可控的最小版"自我进化"Agent）。

它不是要做出真实联网的强 Agent，而是一个"可控 mock"：能按不同"画像(profile)"
产出真实 / 半真实的运行轨迹（trajectory），用来把四层验证 harness 跑通并展示区分度。

关键点：
- 工具"创造"步骤是真实的：strong 画像会真的调用 LLM 生成工具代码，供第 3 层
  LLM-as-a-Judge 打分；weak 画像给一段粗糙 stub 以展示低分。
- 工具"发现"步骤按画像产出好 / 坏的搜索关键词与选库，供第 2 层启发式判定。
- 工具"复用"由共享的 ToolRegistry 支撑：strong 画像在第二次相似任务时会先查注册表，
  命中即直接检索复用（不再搜索）；weak 画像永远重新搜索与重建，供第 4 层区分。

轨迹(trajectory) schema：
{
  "task_id": str,
  "goal": str,
  "profile": str,
  "steps": [ {"action": "...", ...}, ... ],   # 见下方各 action
  "created_tools": [ {"name": str, "code": str} ],
  "final_answer": str
}
step 的 action 取值：
  search        {"action":"search","query":str}
  read_web      {"action":"read_web","url":str}
  select_library{"action":"select_library","library":str}
  create_tool   {"action":"create_tool","name":str,"code":str}
  register_tool {"action":"register_tool","name":str}
  retrieve_tool {"action":"retrieve_tool","name":str,"source":"registry"}
  call_tool     {"action":"call_tool","name":str,"args":dict,"result":str}
  final_answer  {"action":"final_answer","text":str}
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from config import Config


# ---------------------------------------------------------------------------
# 工具注册表：自我进化 Agent 把创造出来的工具持久化于此，供后续任务复用
# ---------------------------------------------------------------------------
class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, dict] = {}

    def has(self, name: str) -> bool:
        return name in self._tools

    def register(self, name: str, code: str, task_id: str):
        self._tools[name] = {"code": code, "task_id": task_id}

    def get(self, name: str) -> Optional[dict]:
        return self._tools.get(name)

    def names(self) -> List[str]:
        return list(self._tools)


# ---------------------------------------------------------------------------
# Agent 画像：把"好 / 坏"的行为参数化
# ---------------------------------------------------------------------------
@dataclass
class Profile:
    name: str
    discovery_quality: str  # "good" | "bad"
    tool_quality: str       # "good"(调 LLM 生成) | "sloppy"(粗糙 stub)
    reuse_registry: bool    # 相似任务是否先查注册表复用


STRONG = Profile("strong", discovery_quality="good", tool_quality="good", reuse_registry=True)
WEAK = Profile("weak", discovery_quality="bad", tool_quality="sloppy", reuse_registry=False)


_TOOL_GEN_SYSTEM = (
    "You are a senior Python engineer building a reusable utility tool. "
    "Return ONLY a single self-contained Python function (plus its imports). "
    "The function MUST have: a clear docstring (purpose, args, returns, raises), "
    "input validation, and try/except error handling with helpful messages. "
    "No example usage, no markdown fences, code only."
)


def _sloppy_tool_code(tool_name: str, library: str) -> str:
    """weak 画像使用的粗糙 stub：无 docstring、无校验、无错误处理。"""
    top = library.split("(")[0].split(">=")[0].strip().replace("-", "_")
    return (
        f"def {tool_name}(x):\n"
        f"    import {top or 'requests'}\n"
        f"    return {top or 'requests'}.run(x)\n"
    )


def _offline_good_tool_code(task: dict, library: str) -> str:
    """离线模式下 strong 画像使用的高质量工具模板（有 docstring / 参数校验 / try-except），
    无需调用 LLM，便于在没有 API Key 时演示 L1/L2/L4 三个确定性层的评分。

    模板刻意做到 L3 Rubric 的四个维度都齐备，因此即使联网跑 L3 也应得高分。"""
    top = library.split("(")[0].split(">=")[0].strip().replace("-", "_") or "requests"
    name = task["tool_name"]
    goal = task["goal"].replace('"', "'")
    return (
        f"import {top}\n\n\n"
        f"def {name}(query: str, timeout: int = 30):\n"
        f'    """{goal}\n\n'
        f"    Args:\n"
        f"        query: 目标标识（如 URL / ID / 查询串），非空字符串。\n"
        f"        timeout: 网络请求超时时间（秒），必须为正整数。\n"
        f"    Returns:\n"
        f"        工具执行结果。\n"
        f"    Raises:\n"
        f"        ValueError: 入参非法时抛出。\n"
        f"        RuntimeError: 底层调用失败时抛出。\n"
        f'    """\n'
        f"    if not isinstance(query, str) or not query.strip():\n"
        f"        raise ValueError('query 必须为非空字符串')\n"
        f"    if not isinstance(timeout, int) or timeout <= 0:\n"
        f"        raise ValueError('timeout 必须为正整数')\n"
        f"    try:\n"
        f"        return {top}.run(query, timeout=timeout)\n"
        f"    except Exception as exc:  # noqa: BLE001\n"
        f"        raise RuntimeError(f'{name} 执行失败: {{exc}}') from exc\n"
    )


class SelfEvolutionAgent:
    """可控的自我进化 Agent。同一个 registry 在多次 run 之间共享以支持复用。"""

    def __init__(self, registry: ToolRegistry, model: Optional[str] = None, offline: bool = False):
        self.registry = registry
        self.model = Config.resolve_default_model(model)
        self.offline = offline  # True 时用离线工具模板，不调用 LLM（用于无 Key 演示确定性层）
        self._client = None  # 懒加载，只有真正需要生成工具时才建连接

    @property
    def client(self):
        if self._client is None:
            self._client = Config.get_client()
        return self._client

    # -- 真实调用 LLM 生成工具代码（第 3 层 judge 的输入来源） --------------
    def _generate_tool_code(self, task: dict, library: str) -> str:
        prompt = (
            f"Write a Python function named `{task['tool_name']}` that accomplishes "
            f"this goal:\n{task['goal']}\n\n"
            f"Prefer using the library `{library}`."
        )
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=Config.TEMPERATURE,
            messages=[
                {"role": "system", "content": _TOOL_GEN_SYSTEM},
                {"role": "user", "content": prompt},
            ],
        )
        code = resp.choices[0].message.content or ""
        # 去掉可能出现的 markdown 代码围栏
        code = code.strip()
        if code.startswith("```"):
            code = code.split("```", 2)[1]
            if code.startswith("python"):
                code = code[len("python"):]
            code = code.strip("`").strip()
        return code

    # -- 发现阶段：产出搜索关键词、访问网页、选库 -------------------------
    def _discovery_steps(self, task: dict, profile: Profile):
        steps = []
        if profile.discovery_quality == "good":
            kws = task.get("discovery_keywords", [])[:3]
            query = " ".join(kws) if kws else task["goal"]
            steps.append({"action": "search", "query": f"{query} python library"})
            lib = task["reference_solution"]["libraries"][0]
            top = lib.split("(")[0].strip()
            steps.append({"action": "read_web", "url": f"https://pypi.org/project/{top}/"})
            steps.append({"action": "select_library", "library": lib})
            return steps, lib
        else:
            # 坏发现：关键词泛泛、且选了一个已废弃/需付费的库
            steps.append({"action": "search", "query": "how to do this quickly easy python"})
            pit = task.get("known_pitfalls", {})
            bad = (pit.get("deprecated_libraries") or pit.get("paid_or_registration_apis") or ["requests"])[0]
            steps.append({"action": "select_library", "library": bad})
            return steps, bad

    # -- 主流程 ----------------------------------------------------------
    def run(self, task: dict, profile: Profile, use_variant: bool = False) -> dict:
        """跑一个任务，返回轨迹。use_variant=True 表示这是"第二次相似任务"（复用探针）。"""
        goal = task["variant_goal"] if use_variant else task["goal"]
        tool_name = task["tool_name"]
        traj = {
            "task_id": task["id"],
            "goal": goal,
            "profile": profile.name,
            "is_variant": use_variant,
            "steps": [],
            "created_tools": [],
            "final_answer": "",
        }

        # 1) 复用检查：strong 画像先查注册表
        if profile.reuse_registry and self.registry.has(tool_name):
            traj["steps"].append({"action": "retrieve_tool", "name": tool_name, "source": "registry"})
            traj["steps"].append({
                "action": "call_tool", "name": tool_name, "args": {"goal": goal},
                "result": "(复用已注册工具，直接得到结果)",
            })
            traj["final_answer"] = task["mock_answer"]
            traj["steps"].append({"action": "final_answer", "text": traj["final_answer"]})
            return traj

        # 2) 发现阶段
        disc_steps, library = self._discovery_steps(task, profile)
        traj["steps"].extend(disc_steps)

        # 3) 创造阶段
        if profile.tool_quality == "good":
            code = (
                _offline_good_tool_code(task, library)
                if self.offline
                else self._generate_tool_code(task, library)
            )
        else:
            code = _sloppy_tool_code(tool_name, library)
        traj["steps"].append({"action": "create_tool", "name": tool_name, "code": code})
        traj["created_tools"].append({"name": tool_name, "code": code})

        # 4) 注册（供复用）
        self.registry.register(tool_name, code, task["id"])
        traj["steps"].append({"action": "register_tool", "name": tool_name})

        # 5) 调用并给出答案
        traj["steps"].append({
            "action": "call_tool", "name": tool_name, "args": {"goal": goal},
            "result": "(工具执行完成)",
        })
        traj["final_answer"] = task["mock_answer"]
        traj["steps"].append({"action": "final_answer", "text": traj["final_answer"]})
        return traj
