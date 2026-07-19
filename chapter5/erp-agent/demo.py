"""
实验 5-10：自然语言交互的 ERP Agent（NL -> SQL，artifact 模式）命令行入口。

核心思想（artifact 模式）：Agent 只负责「生成 SQL 制品」，不亲自搬运数据；
真正的查询由系统用生成的 SQL 在数据库上执行，结果表直达用户界面。

子命令：
  run     在线：Agent 生成 SQL -> 执行 -> 与参考实现比对（需 OPENAI_API_KEY，默认子命令）
  gold    离线：执行内置「标准 SQL」跑 10 题 -> 与参考实现比对（无需 API，用于自检/演示）
  ask     在线：单条自然语言查询 -> 生成 SQL -> 执行并打印结果表（需 OPENAI_API_KEY）
  initdb  建表并把可复现的种子数据灌入一个 SQLite 文件（离线，便于用 sqlite3 手工查看）

不带子命令时等价于 `run`，保持与旧版 `python demo.py` 相同的默认行为。
完整用法见 `python demo.py --help`，或某个子命令的 `python demo.py <子命令> --help`。
"""

import argparse
import json
import os
import sqlite3
import sys
from datetime import date

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

import seed
import reference
import gold
from questions import QUESTIONS
from agent import SQLAgent, MODEL


# ---------------- 结果比对 ----------------
def _norm(v):
    """把单个值归一化为 ('n', 数值) 或 ('s', 字符串)，便于容差比对。"""
    if isinstance(v, bool):
        return ("n", float(v))
    if isinstance(v, (int, float)):
        return ("n", round(float(v), 2))
    return ("s", str(v).strip())


def _row_match(a, b, tol):
    if len(a) != len(b):
        return False
    for x, y in zip(a, b):
        if x[0] != y[0]:
            return False
        if x[0] == "n":
            if abs(x[1] - y[1]) > tol:
                return False
        else:
            if x[1] != y[1]:
                return False
    return True


def compare(expected, actual, tol=0.1):
    """按多重集合（忽略行顺序）比对期望与实际结果，数值带容差。"""
    exp = [tuple(_norm(v) for v in r) for r in expected]
    act = [tuple(_norm(v) for v in r) for r in actual]
    if len(exp) != len(act):
        return False, f"行数不一致：期望 {len(exp)} 行，实际 {len(act)} 行"
    remaining = list(act)
    for er in exp:
        for i, ar in enumerate(remaining):
            if _row_match(er, ar, tol):
                remaining.pop(i)
                break
        else:
            return False, f"缺少匹配行：{_readable(er)}"
    return True, "结果一致"


def _readable(norm_row):
    return tuple(v[1] for v in norm_row)


# ---------------- 结果表打印 ----------------
def print_table(rows, max_rows=12):
    if not rows:
        print("    (空结果)")
        return
    for r in rows[:max_rows]:
        cells = []
        for v in r:
            if isinstance(v, float):
                cells.append(f"{v:.2f}")
            else:
                cells.append(str(v))
        print("    | " + " | ".join(cells) + " |")
    if len(rows) > max_rows:
        print(f"    ... 共 {len(rows)} 行")


# ---------------- 逐题执行主循环（在线/离线共用） ----------------
def run_questions(conn, employees, salaries, today, sql_provider,
                  qids=None, print_sql=True, max_rows=12):
    """对每个问题：取 SQL -> 执行 -> 与 Python 参考实现比对，逐题打印。

    sql_provider(q) -> str：给出该题的 SQL；可能抛异常（如在线调用 LLM 失败）。
      在线模式传入 `lambda q: agent.generate_sql(q["nl"], q["hint"])`，
      离线模式传入 `lambda q: gold.GOLD[q["id"]]`。
    qids：只跑这些题号（None 表示全部）。
    返回 (passed, total, results)，results 为逐题明细 dict，便于 --output 导出。
    """
    results = []
    passed = 0
    total = 0
    for q in QUESTIONS:
        if qids and q["id"] not in qids:
            continue
        total += 1
        qid, nl, hint = q["id"], q["nl"], q["hint"]
        print(f"\n【问题 {qid}】{nl}")
        rec = {"id": qid, "nl": nl, "sql": None, "rows": None,
               "passed": False, "error": None}

        # 1) 取 SQL 制品（在线由 Agent 生成，离线取内置 gold SQL）
        try:
            sql = sql_provider(q)
        except Exception as e:
            print(f"  [生成 SQL 失败] {e}")
            rec["error"] = f"生成 SQL 失败：{e}"
            results.append(rec)
            continue
        rec["sql"] = sql
        if print_sql:
            print("  生成的 SQL：")
            for line in sql.splitlines():
                print("    " + line)

        # 2) 系统执行 SQL
        try:
            cur = conn.cursor()
            cur.execute(sql)
            actual = cur.fetchall()
        except Exception as e:
            print(f"  [SQL 执行出错] {e}")
            print("  结果：不通过 ✗")
            rec["error"] = f"SQL 执行出错：{e}"
            results.append(rec)
            continue
        rec["rows"] = [list(r) for r in actual]

        print("  查询结果：")
        print_table(actual, max_rows=max_rows)

        # 3) 与参考实现比对
        expected = reference.REFERENCE[qid](employees, salaries, today)
        ok, msg = compare(expected, actual)
        rec["passed"] = ok
        if ok:
            passed += 1
            print(f"  校验：通过 ✓（{msg}）")
        else:
            print(f"  校验：不通过 ✗（{msg}）")
            print(f"       参考期望：{[tuple(r) for r in expected][:12]}")
        results.append(rec)

    return passed, total, results


# ---------------- 公用：建库、题号过滤、导出、页眉页脚 ----------------
def _build_db(db_path, today):
    """按固定种子生成数据并灌入指定的 SQLite 库（':memory:' 或文件路径）。

    每次都重新灌入，保证与 reference.py 的期望答案严格对齐、结果可复现。
    """
    employees, salaries = seed.generate(today)
    conn = sqlite3.connect(db_path)
    seed.create_db(conn, employees, salaries)
    return conn, employees, salaries


def _parse_only(only):
    """把 '1,5,10' 解析成 {1,5,10}；空/None 表示全部题目。"""
    if not only:
        return None
    ids = set()
    for part in only.split(","):
        part = part.strip()
        if part:
            ids.add(int(part))
    unknown = ids - {q["id"] for q in QUESTIONS}
    if unknown:
        raise SystemExit(f"未知题号：{sorted(unknown)}（有效题号 1~{len(QUESTIONS)}）")
    return ids


def _header(mode, today, employees, salaries, model=None):
    print("=" * 70)
    tail = f"  |  模型：{model}" if model else "  |  离线（不调用 API）"
    print(f"ERP Agent 实验 5-10  |  {mode}{tail}")
    print(f"今天：{today.isoformat()}  |  员工 {len(employees)} 人，"
          f"工资记录 {len(salaries)} 条")
    print("=" * 70)


def _footer(passed, total):
    print("\n" + "=" * 70)
    rate = (passed / total * 100) if total else 0
    print(f"总通过率：{passed}/{total}  ({rate:.0f}%)")
    print("=" * 70)


def _write_output(path, mode, today, passed, total, results):
    payload = {
        "experiment": "5-10 ERP Agent NL->SQL",
        "mode": mode,
        "date": today.isoformat(),
        "passed": passed,
        "total": total,
        "results": results,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"\n已写出结果 JSON：{path}")


def _require_api():
    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")):
        print("请先设置 OPENAI_API_KEY（或 OPENROUTER_API_KEY 兜底）环境变量（可复制 env.example 为 .env）。")
        print("若只想离线跑通、不调用 API，请改用：python demo.py gold")
        sys.exit(1)


# ---------------- 子命令 ----------------
def cmd_run(args):
    """在线：Agent 生成 SQL -> 执行 -> 比对。"""
    _require_api()
    today = date.today()
    conn, emps, sals = _build_db(args.db, today)
    model = args.model or os.environ.get("OPENAI_MODEL", MODEL)
    _header("在线（Agent 生成 SQL）", today, emps, sals, model=model)
    agent = SQLAgent(model=model)
    qids = _parse_only(args.only)
    passed, total, results = run_questions(
        conn, emps, sals, today,
        sql_provider=lambda q: agent.generate_sql(q["nl"], q["hint"]),
        qids=qids, max_rows=args.max_rows,
    )
    _footer(passed, total)
    if args.output:
        _write_output(args.output, "run", today, passed, total, results)


def cmd_gold(args):
    """离线：执行内置标准 SQL -> 比对（无需 API）。"""
    today = date.today()
    conn, emps, sals = _build_db(args.db, today)
    _header("离线自检（内置 gold SQL）", today, emps, sals, model=None)
    qids = _parse_only(args.only)
    passed, total, results = run_questions(
        conn, emps, sals, today,
        sql_provider=lambda q: gold.GOLD[q["id"]],
        qids=qids, max_rows=args.max_rows,
    )
    _footer(passed, total)
    if args.output:
        _write_output(args.output, "gold", today, passed, total, results)


def cmd_ask(args):
    """在线：单条自然语言查询 -> 生成 SQL -> 执行并打印结果表。"""
    _require_api()
    today = date.today()
    conn, emps, sals = _build_db(args.db, today)
    model = args.model or os.environ.get("OPENAI_MODEL", MODEL)
    agent = SQLAgent(model=model)
    hint = args.hint or "自行判断需要返回的列；只输出一条 SELECT。"
    print(f"【问题】{args.query}")
    try:
        sql = agent.generate_sql(args.query, hint)
    except Exception as e:
        print(f"[Agent 生成 SQL 失败] {e}")
        sys.exit(1)
    print("生成的 SQL：")
    for line in sql.splitlines():
        print("  " + line)
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
    except Exception as e:
        print(f"[SQL 执行出错] {e}")
        sys.exit(1)
    print("查询结果：")
    print_table(rows, max_rows=args.max_rows)


def cmd_initdb(args):
    """建表并把种子数据灌入一个 SQLite 文件，便于手工用 sqlite3 查看。"""
    today = date.today()
    if args.db == ":memory:":
        raise SystemExit("initdb 需要一个文件路径，例如：python demo.py initdb --db erp.db")
    if os.path.exists(args.db):
        os.remove(args.db)
    conn, emps, sals = _build_db(args.db, today)
    conn.close()
    print(f"已写入 SQLite 库：{args.db}")
    print(f"  员工 {len(emps)} 人，工资记录 {len(sals)} 条，基准日期 {today.isoformat()}")
    print(f"  手工查看： sqlite3 {args.db} \"SELECT * FROM employees LIMIT 5;\"")
    print(f"  离线复跑： python demo.py gold --db {args.db}")


# ---------------- argparse CLI ----------------
def build_parser():
    p = argparse.ArgumentParser(
        prog="demo.py",
        description="实验 5-10：自然语言交互的 ERP Agent（NL -> SQL，artifact 模式）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="不带子命令时等价于 run（保持旧版默认行为）。"
               "离线自检不需要 API：python demo.py gold",
    )
    sub = p.add_subparsers(dest="cmd", metavar="子命令")

    def add_common(sp, with_model=False):
        sp.add_argument("--db", default=":memory:",
                        help="SQLite 库：':memory:'（默认，内存库）或文件路径")
        sp.add_argument("--only", default=None, metavar="题号列表",
                        help="只跑指定题号，逗号分隔，如 1,5,10（默认全部）")
        sp.add_argument("--max-rows", type=int, default=12, dest="max_rows",
                        help="每题结果表最多打印多少行（默认 12）")
        sp.add_argument("--output", default=None, metavar="路径",
                        help="把逐题结果写成 JSON 文件")
        if with_model:
            sp.add_argument("--model", default=None,
                            help=f"覆盖模型（默认读 OPENAI_MODEL，否则 {MODEL}）")

    sp_run = sub.add_parser("run", help="在线：Agent 生成 SQL 跑 10 题并校验（需 API）")
    add_common(sp_run, with_model=True)
    sp_run.set_defaults(func=cmd_run)

    sp_gold = sub.add_parser("gold", help="离线：执行内置标准 SQL 跑 10 题并校验（无需 API）")
    add_common(sp_gold, with_model=False)
    sp_gold.set_defaults(func=cmd_gold)

    sp_ask = sub.add_parser("ask", help="在线：单条自然语言查询 -> SQL -> 结果表（需 API）")
    sp_ask.add_argument("query", help="要查询的自然语言问题，如“研发部现在有多少在职员工？”")
    sp_ask.add_argument("--hint", default=None, help="可选：补充业务口径/期望返回列")
    sp_ask.add_argument("--db", default=":memory:",
                        help="SQLite 库：':memory:'（默认）或文件路径")
    sp_ask.add_argument("--max-rows", type=int, default=20, dest="max_rows",
                        help="结果表最多打印多少行（默认 20）")
    sp_ask.add_argument("--model", default=None,
                        help=f"覆盖模型（默认读 OPENAI_MODEL，否则 {MODEL}）")
    sp_ask.set_defaults(func=cmd_ask)

    sp_init = sub.add_parser("initdb", help="建表并把种子数据灌入 SQLite 文件（离线）")
    sp_init.add_argument("--db", default="erp.db",
                         help="目标 SQLite 文件路径（默认 erp.db）")
    sp_init.set_defaults(func=cmd_initdb)

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd is None:
        # 不带子命令 -> 沿用旧版默认行为：在线跑全部 10 题
        args = parser.parse_args((argv or []) + ["run"])
    args.func(args)


if __name__ == "__main__":
    main()
