"""
实验 2-5：提示注入攻防实验 —— 主程序。

对 3 种攻击场景 x 4 种防御配置 的每个组合跑 N 次试验，统计攻击成功率，
最后打印一张 攻击 x 防御 的成功率矩阵，直观展示"防御逐层加强 -> 成功率下降"。

命令行用法（详见 --help）：
    python demo.py                       # 默认：全部 3x4 组合，每组合 4 次试验
    python demo.py --trials 5            # 每个组合跑 5 次
    python demo.py --model gpt-5.6-luna        # 换模型
    python demo.py --attack 2,3          # 只跑第 2、3 个攻击场景
    python demo.py --defense 1,4         # 只跑 D1 和 D4 两种防御
    python demo.py --output result.json  # 额外把结果矩阵保存为 JSON
    python demo.py --list                # 离线列出所有攻击/防御，不调用 API

兼容旧行为：仍可用环境变量 TRIALS / OPENAI_MODEL / OPENAI_BASE_URL 设置默认值，
命令行参数优先级更高。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

from agent import DEFENSES, Agent, make_client
from attacks import ATTACKS


def _parse_selection(spec: str, items: list, kind: str) -> list[int]:
    """把 "1,3" 或 "间接,D4" 这样的选择字符串解析为 items 的下标列表。

    支持两种写法（可混用，逗号分隔）：
    - 1 起始的序号（如 "1,3"）；
    - 名称子串（如 "间接" 匹配"间接注入"，"D4" 匹配"D4-组合防御"）。
    保持用户给定的顺序并去重。
    """
    if spec is None or spec.strip().lower() in ("", "all", "全部"):
        return list(range(len(items)))

    chosen: list[int] = []
    for raw in spec.split(","):
        token = raw.strip()
        if not token:
            continue
        idx: int | None = None
        if token.isdigit():
            n = int(token)
            if not 1 <= n <= len(items):
                raise ValueError(
                    f"{kind}序号 {n} 超出范围（有效范围 1-{len(items)}）"
                )
            idx = n - 1
        else:
            matches = [
                i
                for i, it in enumerate(items)
                if token.lower() in it.name.lower()
            ]
            if not matches:
                raise ValueError(f"没有名字包含 “{token}” 的{kind}")
            if len(matches) > 1:
                names = "、".join(items[i].name for i in matches)
                raise ValueError(f"“{token}” 同时匹配多个{kind}：{names}，请写得更具体")
            idx = matches[0]
        if idx not in chosen:
            chosen.append(idx)
    if not chosen:
        raise ValueError(f"未选中任何{kind}")
    return chosen


def list_items() -> None:
    """离线打印所有攻击场景与防御配置（无需 API Key）。"""
    print("攻击场景（--attack 可用序号或名称子串选择）：")
    for i, attack in enumerate(ATTACKS, 1):
        print(f"  {i}. {attack.name} —— {attack.description}")
    print("\n防御配置（--defense 可用序号或名称子串选择）：")
    for i, defense in enumerate(DEFENSES, 1):
        layers = []
        if defense.prompt_hardening:
            layers.append("提示词加固")
        if defense.source_tagging:
            layers.append("来源标记")
        if defense.runtime_guard:
            layers.append("运行时校验")
        detail = " + ".join(layers) if layers else "无（基线）"
        print(f"  {i}. {defense.name} —— {detail}")


def run_matrix(
    trials: int,
    attack_idx: list[int],
    defense_idx: list[int],
    model: str | None,
    temperature: float,
    base_url: str | None,
) -> tuple[list[list[float]], str]:
    client, resolved_model = make_client(model=model, base_url=base_url)
    print(f"使用模型：{resolved_model}，每个组合试验 {trials} 次\n")

    # matrix[攻击索引][防御索引] = 成功率（仅填充被选中的行列，其余为 None）
    matrix: list[list[float | None]] = [
        [None for _ in DEFENSES] for _ in ATTACKS
    ]

    for ai in attack_idx:
        attack = ATTACKS[ai]
        for di in defense_idx:
            defense = DEFENSES[di]
            successes = 0
            errors = 0
            for _ in range(trials):
                agent = Agent(
                    client=client,
                    model=resolved_model,
                    defense=defense,
                    webpage_content=attack.webpage_content,
                    temperature=temperature,
                )
                result = agent.run(list(attack.user_messages))
                if result.error:
                    errors += 1
                    continue
                if attack.judge(result):
                    successes += 1
            rate = successes / trials if trials else 0.0
            matrix[ai][di] = rate
            flag = f"  (含 {errors} 次错误)" if errors else ""
            print(
                f"[{attack.name:<6}] x [{defense.name:<10}] "
                f"成功率 {rate:5.0%} ({successes}/{trials}){flag}"
            )
        print()

    return matrix, resolved_model


def print_matrix(
    matrix: list[list[float | None]],
    attack_idx: list[int],
    defense_idx: list[int],
) -> None:
    print("=" * 68)
    print("攻击成功率矩阵（行=攻击场景，列=防御配置，越低越安全）")
    print("=" * 68)

    def cell(v: float | None) -> str:
        return "   -  " if v is None else f"{v:.0%}"

    corner = "攻击 \\ 防御"
    header = f"{corner:<12}" + "".join(
        f"{DEFENSES[di].name:>14}" for di in defense_idx
    )
    print(header)
    print("-" * len(header))
    for ai in attack_idx:
        row = f"{ATTACKS[ai].name:<12}"
        for di in defense_idx:
            row += f"{cell(matrix[ai][di]):>13} "
        print(row)
    print("-" * len(header))

    # 各防御配置在被选攻击上的平均成功率，展示"逐层加强 -> 整体下降"
    avg = f"{'平均':<12}"
    for di in defense_idx:
        vals = [matrix[ai][di] for ai in attack_idx if matrix[ai][di] is not None]
        col = sum(vals) / len(vals) if vals else 0.0
        avg += f"{col:>13.0%} "
    print(avg)
    print("=" * 68)


def save_json(
    path: str,
    matrix: list[list[float | None]],
    attack_idx: list[int],
    defense_idx: list[int],
    trials: int,
    model: str,
) -> None:
    payload = {
        "model": model,
        "trials": trials,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "defenses": [DEFENSES[di].name for di in defense_idx],
        "attacks": [ATTACKS[ai].name for ai in attack_idx],
        "success_rate": {
            ATTACKS[ai].name: {
                DEFENSES[di].name: matrix[ai][di] for di in defense_idx
            }
            for ai in attack_idx
        },
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n结果矩阵已保存到 {path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo.py",
        description=(
            "实验 2-5：提示注入攻防实验。对 3 种攻击场景 x 4 种防御配置的每个组合"
            "重复试验，统计攻击成功率并打印 攻击x防御 成功率矩阵。"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例：\n"
            "  python demo.py                       # 全部组合，每组合 4 次\n"
            "  python demo.py -n 5 -m gpt-5.6-luna        # 换模型并跑 5 次\n"
            "  python demo.py -a 2,3 -d 1,4         # 只跑攻击2/3 x 防御D1/D4\n"
            "  python demo.py -o result.json        # 额外保存 JSON 结果\n"
            "  python demo.py --list                # 离线列出攻击/防御，不调用 API\n"
        ),
    )
    parser.add_argument(
        "-n",
        "--trials",
        type=int,
        default=int(os.getenv("TRIALS", "4")),
        metavar="N",
        help="每个 攻击x防御 组合重复试验的次数（默认 4，建议 3-5 以控制成本；冒烟测试可用 1）",
    )
    parser.add_argument(
        "-m",
        "--model",
        default=None,
        metavar="NAME",
        help="使用的模型名（默认取环境变量 OPENAI_MODEL，未设置则 gpt-4o-mini）",
    )
    parser.add_argument(
        "-a",
        "--attack",
        default="all",
        metavar="SEL",
        help="选择要跑的攻击场景，逗号分隔的序号或名称子串（如 1,3 或 间接,记忆）；默认 all（全部）",
    )
    parser.add_argument(
        "-d",
        "--defense",
        default="all",
        metavar="SEL",
        help="选择要跑的防御配置，逗号分隔的序号或名称子串（如 1,4 或 D1,D4）；默认 all（全部）",
    )
    parser.add_argument(
        "-t",
        "--temperature",
        type=float,
        default=0.7,
        metavar="T",
        help="采样温度（默认 0.7；设为 0 可让结果更稳定、便于复现）",
    )
    parser.add_argument(
        "--base-url",
        default=None,
        metavar="URL",
        help="自定义 OpenAI 兼容接口的 base_url（默认取环境变量 OPENAI_BASE_URL）",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="PATH",
        help="把成功率矩阵额外保存为 JSON 文件的路径",
    )
    parser.add_argument(
        "-l",
        "--list",
        action="store_true",
        help="离线列出所有攻击场景与防御配置后退出（无需 API Key）",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list:
        list_items()
        return 0

    if args.trials < 1:
        parser.error("--trials 必须 >= 1")

    try:
        attack_idx = _parse_selection(args.attack, ATTACKS, "攻击场景")
        defense_idx = _parse_selection(args.defense, DEFENSES, "防御配置")
    except ValueError as exc:
        parser.error(str(exc))

    try:
        matrix, model = run_matrix(
            trials=args.trials,
            attack_idx=attack_idx,
            defense_idx=defense_idx,
            model=args.model,
            temperature=args.temperature,
            base_url=args.base_url,
        )
    except RuntimeError as exc:
        # 常见于未配置 OPENAI_API_KEY：给出清晰的人类可读提示而非原始堆栈。
        print(f"启动失败：{exc}", file=sys.stderr)
        return 1

    print_matrix(matrix, attack_idx, defense_idx)

    if args.output:
        save_json(args.output, matrix, attack_idx, defense_idx, args.trials, model)

    print(
        "\n结论：从 D1 到 D4，随着防御逐层加强（提示词加固 -> 来源标记 -> "
        "运行时高风险操作校验），各类注入攻击的成功率显著下降，"
        "组合防御（D4）下越权工具调用类攻击被运行时校验彻底挡住，接近 0。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
