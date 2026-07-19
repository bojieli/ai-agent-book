"""
tester.py —— 自动测试（对生成的解析器做数据结构断言）

书中原方案：把生成的可视化代码放进虚拟浏览器渲染，再用 Vision LLM 检查图像。
本机没有 playwright/浏览器，因此**降级**为对解析函数做单元测试：
用一批样本日志喂给生成的 parse 函数，断言它能解析出预期的结构化字段。
这保证了“生成的代码确实能正确解析新格式”，是自愈闭环里真正的质量闸门。
"""

from __future__ import annotations

from typing import Callable, Dict, List, Optional

ParserFn = Callable[[str], Optional[Dict]]


def run_tests(
    parse_fn: ParserFn,
    samples: List[str],
    required_keys: List[str],
) -> Dict:
    """对 parse_fn 跑一组断言，返回 {passed: bool, report: str, results: [...]}。

    通过条件（对每一条样本都要满足）：
      1. parse_fn(line) 不抛异常；
      2. 返回值是非空 dict；
      3. required_keys 中的每个字段都存在，且值不为空（非 None、非空字符串）。
    """
    lines: List[str] = []
    results: List[Optional[Dict]] = []
    all_passed = True

    for i, sample in enumerate(samples, 1):
        try:
            out = parse_fn(sample)
        except Exception as exc:  # 生成的代码在样本上直接崩了
            all_passed = False
            results.append(None)
            lines.append(f"[样本{i}] 解析抛出异常：{type(exc).__name__}: {exc}")
            continue

        if not isinstance(out, dict) or not out:
            all_passed = False
            results.append(out)
            lines.append(f"[样本{i}] 未返回非空 dict，实际返回：{out!r}")
            continue

        missing = [k for k in required_keys if k not in out or out[k] in (None, "")]
        if missing:
            all_passed = False
            lines.append(
                f"[样本{i}] 缺少/为空的必需字段：{missing}；实际解析出：{out}"
            )
        else:
            lines.append(f"[样本{i}] 通过，解析出字段：{sorted(out.keys())}")
        results.append(out)

    report = "\n".join(lines)
    return {"passed": all_passed, "report": report, "results": results}
