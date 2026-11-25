#!/usr/bin/env python3
"""Render summary.json (produced by analyze.py) as Markdown tables: ``tables.md`` in the run directory."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROUTES = ["all_front", "all_back", "by_property_flight_front", "by_property_flight_back"]
ROUTE_LABEL = {
    "all_front": "全前台",
    "all_back": "全后台",
    "by_property_flight_front": "按性质（航班前台）",
    "by_property_flight_back": "按性质（航班后台）",
}
SINGLE = ["weather", "memory", "web_search", "flight_search", "self_correction"]
SCENARIO_LABEL = {
    "weather": "天气",
    "memory": "记忆",
    "web_search": "网页搜索",
    "flight_search": "航班查询",
    "self_correction": "口误更正（航班查询）",
    "pending_change": "等待中改口",
    "pending_aside": "等待中插问",
    "booking": "订票",
    "booking_dictated": "订票（口述乘机人）",
}


def mp(s: dict | None, digits: int = 2) -> str:
    if not s or s.get("median") is None:
        return "—"
    return f"{s['median']:.{digits}f} / {s['p90']:.{digits}f}"


def med(s: dict | None, digits: int = 2) -> str:
    return "—" if not s or s.get("median") is None else f"{s['median']:.{digits}f}"


def frac(r: dict | None) -> str:
    return "—" if not r or not r.get("n") else f"{r['true']}/{r['n']}"


def table(header: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(header) + " |", "| " + " | ".join(["---"] + ["---:"] * (len(header) - 1)) + " |"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines) + "\n"


def render(summary: dict) -> str:
    cells = summary["cells"]
    out = [
        f"# {summary['run_id']}\n",
        f"- 运行开始：{summary['started_at']}\n- 前台：{summary['front']['model']}，session.model = `{summary['front']['session_model']}`\n"
        f"- 后台：`{(summary['back'] or {}).get('model')}`（thinking={(summary['back'] or {}).get('thinking')}，temperature=0）\n"
        f"- 有效会话 {summary['sessions_ok']}，失败尝试 {len(summary['sessions_failed'])}\n- 工具全部为模拟实现，延迟为注入值。\n",
        "下列时间单位均为秒；`a / b` 表示 中位数 / P90（线性插值）。\n",
    ]

    out.append("## 表 1　单轮请求：从用户说完到实质回答首个音频\n")
    rows = []
    for scenario in SINGLE:
        for route in ROUTES:
            cell = cells.get(f"{route}/{scenario}")
            if not cell:
                continue
            turn = next(iter(cell["turns"].values()))
            rows.append(
                [
                    f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}",
                    str(turn["n"]),
                    mp(turn["answer_audio_s"]),
                    str(turn["no_answer"]),
                    f"{turn['filler_runs']}/{turn['n']}",
                    mp(turn["filler_audio_s"]),
                    mp(turn["llm_calls"], 0),
                    med(turn["front_llm_calls"], 0) + "+" + med(turn["back_llm_calls"], 0),
                    med(turn["asr_done_s"]),
                    med(turn["fc_after_asr_s"]),
                    med(turn["tool_latency_s"]),
                    med(turn["back_llm_seconds"]),
                    med(turn["answer_after_result_s"]),
                ]
            )
    out.append(
        table(
            ["场景 · 路线", "n", "实质回答首音频", "无回答", "有垫话", "垫话首音频", "LLM 调用数", "前台+后台", "判停", "判停→发出调用", "工具注入延迟", "后台 LLM 耗时", "结果回传→首音频"],
            rows,
        )
    )

    out.append("## 表 2　参数准确率（首次调用与标准答案精确匹配）\n")
    rows = []
    for scenario in SINGLE:
        for route in ROUTES:
            cell = cells.get(f"{route}/{scenario}")
            if not cell:
                continue
            rows.append(
                [
                    f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}",
                    str(cell["runs"]),
                    frac(cell["tool_called"]),
                    frac(cell["first_call_exact"]),
                    med(cell["n_calls"], 0),
                    frac(cell["key_fact_in_answer"]),
                    frac(cell["correction"]["called_pre_correction_date"]) if "correction" in cell else "—",
                ]
            )
    out.append(table(["场景 · 路线", "n", "调用了预期工具", "首次调用参数精确匹配", "调用次数（中位）", "回答含关键事实", "曾用更正前日期调用"], rows))

    out.append("## 表 3　航班查询：说了多少（实质回答文本）\n")
    rows = []
    for scenario in ("flight_search", "self_correction", "booking", "booking_dictated"):
        for route in ROUTES:
            cell = cells.get(f"{route}/{scenario}")
            if not cell or "readout" not in cell:
                continue
            r = cell["readout"]
            turn = next(iter(cell["turns"].values()))
            rows.append(
                [
                    f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}",
                    str(r["spoken_chars"]["n"]),
                    mp(r["spoken_chars"], 0),
                    str(r["speak_payload_chars"]),
                    str(r["display_payload_chars"]),
                    mp(r["flight_numbers_spoken"], 0),
                    frac(r["read_table_aloud"]),
                    str(r["offer_ids_spoken_runs"]),
                    mp(turn["answer_audio_seconds"], 1),
                ]
            )
    out.append(table(["场景 · 路线", "n", "口头回答字数", "speak 字数", "display JSON 字数", "念出的航班号数（共 6）", "念了 ≥4 个航班", "念出 offer_id 的次数", "回答音频时长"], rows))

    out.append("## 表 4　工具结果未返回时用户再次开口\n")
    rows = []
    for scenario in ("pending_change", "pending_aside"):
        for route in ROUTES:
            cell = cells.get(f"{route}/{scenario}")
            if not cell:
                continue
            p = cell["pending"]
            second = list(cell["turns"].values())[1] if len(cell["turns"]) > 1 else None
            rows.append(
                [
                    f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}",
                    str(cell["runs"]),
                    frac(p["pending_when_barge_started"]),
                    frac(p["heard"]),
                    frac(p.get("new_search_for_dec4")),
                    frac(p.get("spoke_dec4_result")),
                    frac(p.get("spoke_stale_dec3_result")),
                    frac(p.get("aside_answered")),
                    frac(p.get("original_flight_result_spoken")),
                    mp(p.get("corrected_answer_audio_s") or p.get("aside_answer_audio_s")),
                    mp(second["llm_calls"], 0) if second else "—",
                ]
            )
    out.append(
        table(
            ["场景 · 路线", "n", "开口时首个调用仍在等待", "被听到（有转写）", "按新日期重新查询", "说出新日期结果", "说出旧日期结果", "插问得到回答", "原航班结果最终被说出", "第二句说完→正确回答首音频（仅统计答对的运行）", "第二句之后的 LLM 调用数（含已被取代的调用）"],
            rows,
        )
    )

    out.append("## 表 5　订票（三轮：查航班 → 选择并提出订票 → 确认）\n")
    rows = []
    booking_cells = [(s, r) for s in ("booking", "booking_dictated") for r in ROUTES if f"{r}/{s}" in cells]
    for scenario, route in booking_cells:
        cell = cells[f"{route}/{scenario}"]
        b = cell["booking"]
        src = b["field_accuracy_by_source"]
        rows.append(
            [
                f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}",
                str(cell["runs"]),
                str(b["runs_with_booking"]),
                str(b["runs_booked_before_confirmation"]),
                str(b["runs_with_duplicate_booking"]),
                str(b["wrong_bookings"]),
                str(b["runs_correct_booking_after_confirmation"]),
                frac(b["whole_args_exact"]),
                frac(src.get("heard")),
                frac(src.get("heard_dictated")),
                frac(src.get("search_result")),
                frac(src.get("memory")),
                frac(b["readback_mentions_price"]),
            ]
        )
    out.append(
        table(
            ["路线", "n", "发生下单的次数", "确认前就下单", "重复下单", "错单数", "确认后且全对", "整包参数精确匹配", "字段：刚听到的（枚举/数量）", "字段：口述的姓名/证件/手机", "字段：来自查询结果", "字段：来自记忆/资料", "复述含票价"],
            rows,
        )
    )
    rows = []
    for scenario, route in booking_cells:
        cell = cells[f"{route}/{scenario}"]
        for name, turn in cell["turns"].items():
            rows.append(
                [
                    f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]} · {name}",
                    str(turn["n"]),
                    mp(turn["answer_audio_s"]),
                    str(turn["no_answer"]),
                    f"{turn['filler_runs']}/{turn['n']}",
                    mp(turn["llm_calls"], 0),
                    med(turn["front_llm_calls"], 0) + "+" + med(turn["back_llm_calls"], 0),
                    mp(turn["fc_after_asr_s"]),
                    med(turn["tool_latency_s"]),
                    med(turn["back_llm_seconds"]),
                ]
            )
    out.append("订票各轮时延：\n")
    out.append(table(["路线 · 轮次", "n", "实质回答首音频", "无回答", "有垫话", "LLM 调用数", "前台+后台", "判停→发出调用", "工具注入延迟", "后台 LLM 耗时"], rows))
    rows = []
    fields = None
    wrong = []
    for scenario, route in booking_cells:
        cell = cells[f"{route}/{scenario}"]
        acc = cell["booking"]["field_accuracy"]
        fields = fields or list(acc)
        rows.append([f"{SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}"] + [frac(acc[f]) for f in fields])
        for item in cell["booking"]["wrong_values"]:
            wrong.append(f"- {SCENARIO_LABEL[scenario]} · {ROUTE_LABEL[route]}：`{json.dumps(item, ensure_ascii=False)}`\n")
    if fields:
        out.append("订票逐字段准确率（分母为实际发生的下单调用数）：\n")
        out.append(table(["路线"] + fields, rows))
        if wrong:
            out.append("出错字段的实际取值：\n")
            out.extend(wrong)
    if summary["sessions_failed"]:
        out.append("## 失败或作废的尝试（已重跑补足，未计入上表）\n")
        for f in summary["sessions_failed"]:
            out.append(f"- {f['route']}/{f['scenario']}/run-{f['run']:02d} attempt {f['attempt']} [{f['status']}]: {f['error']}\n")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    args = parser.parse_args()
    summary = json.loads((args.run_dir / "summary.json").read_text(encoding="utf-8"))
    text = render(summary)
    (args.run_dir / "tables.md").write_text(text, encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
