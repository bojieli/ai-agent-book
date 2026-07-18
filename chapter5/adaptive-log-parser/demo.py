"""
demo.py —— 自适应日志解析系统：自愈闭环演示

演示整条自愈流程（全流程自动化）：
  初始系统只认基础 JSON 日志 →
  遇到没见过的新格式 → 解析【失败】被检测到 →
  把失败样本 + 报错交给 Agent → Agent【生成解析代码】→
  【自动测试】（数据结构断言）→ 通过后【热加载注册 + 持久化】→
  系统【正确解析】了新格式。

运行：
  python demo.py            # 完整演示（两种新格式，两次 Agent 调用，需 API Key）
  python demo.py --offline  # 离线演示：用预置解析器跑完整机制，无需 API Key
  python demo.py --quick    # 快速模式：只演示 1 种新格式，省一次 API 调用
  python demo.py --help     # 查看全部参数

命令行参数见文件底部的 build_arg_parser()。
"""

from __future__ import annotations

import argparse
import json
import os
import textwrap
from typing import List, Tuple

from engine import LogParserEngine, ParseError, builtin_json_parser
from agent import CodeGenAgent, OfflineCodeGenAgent
from tester import run_tests

HERE = os.path.dirname(os.path.abspath(__file__))
PARSERS_DIR = os.path.join(HERE, "parsers")

MAX_ATTEMPTS = 3  # Agent 生成→测试的最大迭代修复次数


# ---------------------------------------------------------------------------
# 演示用的三种递进日志格式
# ---------------------------------------------------------------------------
# 格式 1：基础 JSON 行 —— 初始系统就支持
JSON_LOGS = [
    '{"timestamp": "2026-07-17T10:22:31Z", "level": "INFO", "message": "Agent started task planning"}',
    '{"timestamp": "2026-07-17T10:22:33Z", "level": "DEBUG", "message": "Loaded 12 tools into context"}',
]

# 格式 2：自定义竖线分隔格式 —— Agent 没见过
#   时间戳|级别|模块|step=N|消息
PIPE_LOGS = [
    "2026-07-17T10:23:01Z|INFO|agent.planner|step=3|Generated plan with 5 actions",
    "2026-07-17T10:23:04Z|WARNING|agent.executor|step=4|Tool call retried once",
    "2026-07-17T10:23:07Z|ERROR|agent.executor|step=5|Tool web_search returned empty result",
]
PIPE_REQUIRED = ["timestamp", "level", "module", "step", "message"]

# 格式 3：嵌套括号格式 —— Agent 也没见过
#   [时间] (级别) <tool=名字> {k=v k=v} :: 消息
BRACKET_LOGS = [
    "[2026-07-17 10:24:55] (ERROR) <tool=web_search> {latency_ms=812 status=timeout} :: upstream request failed",
    "[2026-07-17 10:25:01] (INFO) <tool=code_run> {latency_ms=134 status=ok} :: executed snippet successfully",
    "[2026-07-17 10:25:09] (WARN) <tool=file_read> {latency_ms=45 status=partial} :: file truncated at 1MB",
]
BRACKET_REQUIRED = ["timestamp", "level", "tool", "message"]


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def hr(title: str = "") -> None:
    print("\n" + "=" * 78)
    if title:
        print(title)
        print("=" * 78)


def try_parse_all(
    engine: LogParserEngine, logs: List[str]
) -> Tuple[bool, List[dict]]:
    """尝试解析一批日志，打印结果；返回 (是否全部成功, 成功解析出的结构化记录列表)。"""
    all_ok = True
    records: List[dict] = []
    for line in logs:
        try:
            result = engine.parse_line(line)
            records.append(result)
            print(f"  ✅ [{result['_parser']}] {result}")
        except ParseError:
            all_ok = False
            print(f"  ❌ 解析失败：{line}")
    return all_ok, records


def read_log_file(path: str) -> List[str]:
    """从外部日志文件读取日志（每行一条，忽略空行）。"""
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def write_output(path: str, records: List[dict]) -> None:
    """把解析出的结构化记录写成 JSONL（每行一条 JSON）。"""
    with open(path, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
# 自愈闭环：检测失败 → 生成 → 测试 → 热更新
# ---------------------------------------------------------------------------
def self_heal(
    engine: LogParserEngine,
    agent: "CodeGenAgent | OfflineCodeGenAgent",
    parser_name: str,
    samples: List[str],
    required_keys: List[str],
) -> bool:
    """针对一种新格式跑完整的自愈闭环，成功注册返回 True。"""
    # (a) 触发原因：拿一条样本让系统解析，确认确实失败
    failing_line = samples[0]
    try:
        engine.parse_line(failing_line)
        print("  （该格式已能解析，无需自愈）")
        return True
    except ParseError as exc:
        error_report = str(exc)
        print(f"  🔎 检测到无法解析的新格式，触发自愈。报错：{error_report}")

    target_path = os.path.join(PARSERS_DIR, f"{parser_name}.py")
    feedback = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"\n  --- 第 {attempt}/{MAX_ATTEMPTS} 次：Agent 生成解析代码 ---")
        code = agent.generate_parser_code(
            samples=samples,
            required_keys=required_keys,
            error_report=error_report,
            feedback=feedback,
        )
        print(textwrap.indent(code, "    | "))

        # 写入候选文件（parsers/），再热加载
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(code)

        # 热加载生成的 parse 函数
        try:
            fn = LogParserEngine.load_parser_from_file(target_path)
        except Exception as exc:
            feedback = f"代码无法导入/执行：{type(exc).__name__}: {exc}"
            print(f"  ⚠️ 热加载失败：{feedback}")
            continue

        # (b) 自动测试：数据结构断言
        print("  🧪 自动测试（数据结构断言）：")
        test = run_tests(fn, samples, required_keys)
        print(textwrap.indent(test["report"], "    "))

        if test["passed"]:
            # (c) 通过 → 热更新注册进引擎，文件已持久化到 parsers/
            engine.register(parser_name, fn)
            print(f"  ✅ 自动测试通过，已热更新注册解析器 '{parser_name}' 并持久化到 parsers/{parser_name}.py")
            return True

        feedback = "自动测试未通过，失败详情如下：\n" + test["report"]
        print("  ↻ 测试未通过，把失败报告反馈给 Agent 重试。")

    # 全部尝试失败：删除无效文件
    if os.path.exists(target_path):
        os.remove(target_path)
    print(f"  ❌ {MAX_ATTEMPTS} 次尝试后仍未通过，放弃该格式。")
    return False


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------
def main(args: argparse.Namespace) -> None:
    hr("自适应日志解析系统 —— 自愈闭环演示（实验 5-7）")
    print("初始系统只内置一个基础解析器：JSON 行解析器。")
    if args.quick:
        print("（--quick 快速模式：仅演示 1 种新格式，省一次 Agent/API 调用）")
    if args.offline:
        print("（--offline 离线模式：用预置解析器代替 OpenAI，无需 API Key，机制完全一致）")

    os.makedirs(PARSERS_DIR, exist_ok=True)  # 确保持久化目录存在（新克隆时可能只有 .gitkeep）

    engine = LogParserEngine()
    engine.register("builtin_json", builtin_json_parser)
    print(f"当前已注册解析器：{engine.parser_names}")

    # model=None 时回落到 MODEL 环境变量/默认 gpt-5.6-luna；离线模式不触碰 API
    agent = OfflineCodeGenAgent(args.model) if args.offline else CodeGenAgent(model=args.model)
    print(f"代码生成 Agent 使用模型：{agent.model}")

    # 步骤 0：基础 JSON 格式，系统本来就能解析
    hr("步骤 0：解析基础 JSON 日志（系统原生支持）")
    try_parse_all(engine, JSON_LOGS)

    # 步骤 1：自定义竖线分隔格式（Agent 没见过）
    hr("步骤 1：遇到新格式 A —— 自定义竖线分隔格式")
    print("原始日志样本：")
    for l in PIPE_LOGS:
        print(f"  {l}")
    print("\n(a) 先让系统解析，预期【失败】：")
    try_parse_all(engine, PIPE_LOGS)
    print("\n触发自愈闭环：")
    ok1 = self_heal(engine, agent, "pipe_parser", PIPE_LOGS, PIPE_REQUIRED)
    if ok1:
        print("\n(c) 热更新后重新解析同样的日志，预期【成功】：")
        try_parse_all(engine, PIPE_LOGS)

    # 步骤 2：嵌套括号格式（Agent 也没见过）—— 快速模式下跳过，省一次 API 调用
    ok2 = None
    if args.quick:
        hr("步骤 2：（--quick 模式已跳过新格式 B 的演示）")
    else:
        hr("步骤 2：遇到新格式 B —— 嵌套括号格式")
        print("原始日志样本：")
        for l in BRACKET_LOGS:
            print(f"  {l}")
        print("\n(a) 先让系统解析，预期【失败】：")
        try_parse_all(engine, BRACKET_LOGS)
        print("\n触发自愈闭环：")
        ok2 = self_heal(engine, agent, "bracket_parser", BRACKET_LOGS, BRACKET_REQUIRED)
        if ok2:
            print("\n(c) 热更新后重新解析同样的日志，预期【成功】：")
            try_parse_all(engine, BRACKET_LOGS)

    # 步骤 3：验证持久化复用 —— 新引擎直接加载 parsers/，无需再问 Agent
    hr("步骤 3：验证持久化复用（重启系统，直接加载已学会的解析器）")
    engine2 = LogParserEngine()
    engine2.register("builtin_json", builtin_json_parser)
    loaded = engine2.load_persisted(PARSERS_DIR)
    print(f"新引擎从 parsers/ 热加载了：{loaded}")
    if args.log_file:
        print(f"用学到的解析系统解析外部日志文件（不再调用 Agent）：{args.log_file}")
        mixed = read_log_file(args.log_file)
    else:
        print("直接解析之前的新格式（不再调用 Agent）：")
        mixed = [JSON_LOGS[0], PIPE_LOGS[0]]
        if not args.quick:
            mixed.append(BRACKET_LOGS[0])  # 快速模式没生成 bracket_parser，混合样本里也不放它
    all_ok, records = try_parse_all(engine2, mixed)

    if args.output:
        write_output(args.output, records)
        print(f"已将 {len(records)} 条结构化解析结果写入（JSONL）：{args.output}")

    hr("演示结束")
    print(f"新格式 A（竖线分隔）自愈结果：{'成功' if ok1 else '失败'}")
    if ok2 is None:
        print("新格式 B（嵌套括号）：--quick 模式已跳过")
    else:
        print(f"新格式 B（嵌套括号）自愈结果：{'成功' if ok2 else '失败'}")
    print(f"持久化复用（混合格式全部解析）：{'成功' if all_ok else '失败'}")
    print(f"已学会并持久化的解析器目录：{PARSERS_DIR}")


def build_arg_parser() -> argparse.ArgumentParser:
    """构造命令行参数解析器（提供 --help / --quick / --model）。"""
    parser = argparse.ArgumentParser(
        description="自适应日志解析系统：自愈闭环演示（检测失败 → Agent 生成解析代码 → "
        "自动测试 → 热加载注册 → 持久化复用）。默认走 OpenAI，需 OPENAI_API_KEY；"
        "加 --offline 用预置解析器演示同一套机制，无需 API Key。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="离线模式：用预置（canned）解析器代码代替调用 OpenAI，无需 API Key，"
        "确定性地演示“失败检测→生成→测试→热重载→持久化”整条机制。",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速模式：只演示 1 种新格式（竖线分隔），跳过嵌套括号格式，省一次 Agent/API 调用。",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="覆盖代码生成使用的模型；默认读取环境变量 MODEL，再回落到 gpt-5.6-luna。"
        "（--offline 下此项仅作展示，不影响预置解析器。）",
    )
    parser.add_argument(
        "--log-file",
        default=None,
        metavar="PATH",
        help="外部日志文件路径（每行一条日志）。给定后，步骤 3 改用学到的解析系统解析"
        "该文件，替代内置混合样本；用于验证学到的解析器可复用到真实日志流。",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="把步骤 3 解析出的结构化结果以 JSONL（每行一条 JSON）写入该文件。",
    )
    return parser


if __name__ == "__main__":
    main(build_arg_parser().parse_args())
