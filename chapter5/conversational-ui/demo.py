"""实验 5-11：对话式界面定制系统 —— 端到端演示与自动验证。

本 demo 在"无浏览器"的环境里，把可验证性落在【自然语言 → 代码修改被正确应用】的闭环上：

  对每一条自然语言定制需求：
    1) 调用真实 OpenAI，让 Agent 定位并改写前端源码（agent.customize）；
    2) 打印改动前后的 diff 片段（difflib），并把改动写回 frontend/src；
    3) 读回源码做断言，确认改动"确实符合需求"（颜色值/字体/文案按要求变化）；
    4) 运行 `npm run build`（vite build），确认改动没有破坏应用（可编译通过）。

  连续跑多轮（本例 3 轮），验证多轮迭代定制均生效且不破坏构建。

注意：真正"浏览器内 HMR 的视觉即时刷新"需手动 `npm run dev` + 打开浏览器查看；
本 demo 自动验证的是"代码修改被正确应用，且构建始终通过"。

运行:
  python demo.py            # 跑全部 3 轮定制并做完整验证
  python demo.py --quick    # 只跑第 1 轮（省时，用于快速冒烟）
  python demo.py --rounds 2 # 只跑前 2 轮
  python demo.py --no-build # 跳过 vite build（仅验证"改动被正确应用"）
  python demo.py -h         # 查看全部参数
"""

import sys
import shutil
import difflib
import argparse
import subprocess
from pathlib import Path

import agent

HERE = Path(__file__).resolve().parent
FRONTEND = HERE / "frontend"
BASELINE = HERE / "baseline"  # 前端源码的初始快照，保证 demo 可重复运行


# ---------------------------------------------------------------------------
# 每一轮的定制需求 + 对应的验证函数。
# verify(sources) 接收 {相对路径: 改写后内容}，返回 (是否通过, 说明)。
# ---------------------------------------------------------------------------
def _all_text(sources: dict) -> str:
    return "\n".join(sources.values())


ROUNDS = [
    {
        "requirement": "把发送按钮和用户消息气泡的主题色从绿色改成蓝色，用 #2563eb 这个蓝。",
        "verify": lambda s: (
            "#2563eb" in _all_text(s).lower().replace("#2563EB".lower(), "#2563eb"),
            "源码中出现蓝色值 #2563eb",
        ),
    },
    {
        "requirement": "把整个界面的字体换成等宽字体（monospace）。",
        "verify": lambda s: (
            "monospace" in _all_text(s).lower(),
            "源码中出现 monospace 等宽字体",
        ),
    },
    {
        "requirement": "把顶部的标题文案改成“我的专属客服”。",
        "verify": lambda s: (
            "我的专属客服" in _all_text(s),
            "源码中出现新标题文案“我的专属客服”",
        ),
    },
]


def restore_baseline():
    """把 frontend/src 下的可编辑文件恢复为初始快照，保证可重复运行。"""
    for rel in agent.EDITABLE_FILES:
        src = BASELINE / rel
        dst = FRONTEND / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)


def ensure_node_modules():
    """确保依赖已安装；首次 npm install 较慢属正常现象。"""
    if (FRONTEND / "node_modules").exists():
        return
    print(">> 未发现 node_modules，正在执行 npm install（首次较慢，请耐心等待）…")
    r = subprocess.run(["npm", "install"], cwd=FRONTEND)
    if r.returncode != 0:
        raise SystemExit("npm install 失败，请检查 Node/npm 环境。")


def run_build() -> bool:
    """运行 vite build，返回是否编译通过。"""
    r = subprocess.run(
        ["npm", "run", "build"],
        cwd=FRONTEND,
        capture_output=True,
        text=True,
    )
    tail = (r.stdout + r.stderr).strip().splitlines()
    for line in tail[-6:]:
        print("   | " + line)
    return r.returncode == 0


def print_diff(rel: str, old: str, new: str):
    """打印一个文件改动前后的 unified diff 片段（最多若干行）。"""
    diff = list(
        difflib.unified_diff(
            old.splitlines(),
            new.splitlines(),
            fromfile=f"a/{rel}",
            tofile=f"b/{rel}",
            lineterm="",
        )
    )
    if not diff:
        print(f"   （{rel} 无变化）")
        return
    shown = 0
    for line in diff:
        if line.startswith("+++") or line.startswith("---") or line.startswith("@@"):
            print("   " + line)
        elif line.startswith("+"):
            print("   \033[32m" + line + "\033[0m")  # 绿：新增
            shown += 1
        elif line.startswith("-"):
            print("   \033[31m" + line + "\033[0m")  # 红：删除
            shown += 1
        else:
            continue  # 省略上下文行，只看真正改动
        if shown >= 20:
            print("   …（diff 片段已截断）")
            break


def parse_args(argv=None):
    """解析命令行参数：控制跑几轮、是否跳过构建。"""
    parser = argparse.ArgumentParser(
        description="实验 5-11：对话式界面定制系统 —— NL → 代码修改 闭环验证。"
        "对每条自然语言 UI 定制需求，让 Agent 改写前端源码，"
        "并断言改动生效、vite build 不被破坏。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="快速模式：只跑第 1 轮定制（等价于 --rounds 1）。",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=None,
        metavar="N",
        help=f"只跑前 N 轮定制（1..{len(ROUNDS)}）；默认跑全部。",
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="跳过 vite build，仅验证'改动被正确应用'（更快，但不校验构建）。",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    # 决定本次运行的轮次数：--quick 优先，其次 --rounds，默认全部。
    limit = len(ROUNDS)
    if args.quick:
        limit = 1
    elif args.rounds is not None:
        limit = max(1, min(args.rounds, len(ROUNDS)))
    rounds = ROUNDS[:limit]
    do_build = not args.no_build

    print("=" * 72)
    print("实验 5-11：对话式界面定制系统 —— NL → 代码修改 闭环验证")
    print("=" * 72)

    client, model = agent.build_client_and_model()
    print(f"模型: {model}")
    print(f"本次运行轮次: {limit}/{len(ROUNDS)}    构建验证: {'开启' if do_build else '关闭'}")

    restore_baseline()

    if do_build:
        ensure_node_modules()
        print("\n>> 基线构建校验（未定制前，确保应用本身可编译）…")
        if not run_build():
            raise SystemExit("基线构建失败，请先修复前端工程。")
        print("   基线构建：通过 ✅")

    all_pass = True
    for i, round_def in enumerate(rounds, 1):
        req = round_def["requirement"]
        print("\n" + "-" * 72)
        print(f"第 {i} 轮 NL 定制需求：{req}")
        print("-" * 72)

        old_sources = agent.read_editable_sources(FRONTEND)

        # 1) 调用 Agent（真实 OpenAI）得到改写方案
        result = agent.customize(client, model, FRONTEND, req)
        print(f"Agent 说明：{result.get('summary', '(无)')}")

        # 2) 写回 + 打印 diff
        changed = {}
        for f in result["files"]:
            rel = f["path"]
            new_content = f["content"]
            print(f"\n[改动文件] {rel}")
            print_diff(rel, old_sources[rel], new_content)
            (FRONTEND / rel).write_text(new_content, encoding="utf-8")
            changed[rel] = new_content

        # 3) 读回源码断言"改动符合需求"
        current = agent.read_editable_sources(FRONTEND)
        ok, desc = round_def["verify"](current)
        print(f"\n断言：{desc} -> {'通过 ✅' if ok else '失败 ❌'}")
        if not ok:
            all_pass = False

        # 4) 构建验证"没破坏应用"（--no-build 时跳过）
        if do_build:
            print("构建验证（vite build）：")
            build_ok = run_build()
            print(f"   构建结果：{'通过 ✅' if build_ok else '失败 ❌'}")
            if not build_ok:
                all_pass = False
        else:
            print("构建验证（vite build）：已跳过（--no-build）")

    print("\n" + "=" * 72)
    print(f"多轮定制总结：{'全部通过 ✅' if all_pass else '存在失败项 ❌'}")
    print("提示：手动 `npm run dev` + 打开 http://localhost:5173 可看到 HMR 视觉即时生效。")
    print("=" * 72)
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
