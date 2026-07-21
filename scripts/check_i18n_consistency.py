#!/usr/bin/env python3
"""检查多语言版本（中/繁/英/越/泰米尔）的结构完整性。

防止主页或某章 README 改动后，其它语言版本跟不上而漂移。CI 中运行；
本地也可直接 `python scripts/check_i18n_consistency.py` 跑。

设计原则：
  - **完整性检查**（缺文件就报错）：主 README、docs/LEARNING
  - **对齐检查**（中文版有什么，其它「主语言」也应有什么）：
      chapterN/README、git clone 命令数、内容速览表列数
  - 「共享」语言豁免：如繁体中文（zh-TW）代码页直接用中文版，是合理设计

退出码：0 = 全部一致；1 = 发现不一致。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 主 README 必须存在的语言（5 种）
MAIN_LANGS = ["", ".zhtw", ".en", ".vi", ".ta"]

# 「主语言」要完整对齐中文版（章节 README、LEARNING 等）。
# zh-TW 共享中文代码页，不算主语言。
FULL_LANGS = ["", ".en", ".vi", ".ta"]

LANG_LABELS = {
    "": "zh",
    ".zhtw": "zh-TW",
    ".en": "en",
    ".vi": "vi",
    ".ta": "ta",
}

CHAPTERS = range(1, 11)


def project_count_in_table(path: Path) -> int:
    """统计 chapter README 表格里项目数据行数（含 ✅/📖/🚧 类型列的行）。"""
    if not path.exists():
        return -1
    pattern = re.compile(r"^\|.*\| [✅📖🚧]+ \|")
    return sum(
        1 for line in path.read_text(encoding="utf-8").splitlines() if pattern.match(line)
    )


def count_git_clones(path: Path) -> int:
    if not path.exists():
        return -1
    return len(re.findall(r"^git clone ", path.read_text(encoding="utf-8"), re.MULTILINE))


def toc_table_columns(path: Path) -> int:
    """主 README 内容速览表第一个数据行的列数。"""
    if not path.exists():
        return -1
    for line in path.read_text(encoding="utf-8").splitlines():
        if re.match(r"^\| \d+ \|", line):
            return line.count("|") - 1
    return -1


def main() -> int:
    errors: list[str] = []

    # ===== 检查 1：5 种主 README 都存在 =====
    print("== 检查 1：主 README 存在（5 种语言）==")
    for lang in MAIN_LANGS:
        path = ROOT / f"README{lang}.md"
        if not path.exists():
            errors.append(f"README{lang}.md 不存在")
        else:
            print(f"  ✓ README{lang}.md ({path.stat().st_size} bytes)")
    print()

    # ===== 检查 2：内容速览表结构（≥5 列）=====
    print("== 检查 2：主 README 内容速览表结构（≥5 列）==")
    for lang in MAIN_LANGS:
        path = ROOT / f"README{lang}.md"
        if not path.exists():
            continue
        cols = toc_table_columns(path)
        label = LANG_LABELS[lang]
        if cols < 5:
            errors.append(
                f"README{lang}.md 内容速览表列数 {cols} < 5（应至少 5 列：章/主题/核心/正文/代码）"
            )
        else:
            print(f"  ✓ {label}: {cols} 列")
    print()

    # ===== 检查 3：git clone 命令数对齐（以中文版为基准）=====
    print("== 检查 3：主 README git clone 命令数 ==")
    zh_clones = count_git_clones(ROOT / "README.md")
    print(f"  中文基准：{zh_clones} 条")
    for lang in MAIN_LANGS[1:]:
        path = ROOT / f"README{lang}.md"
        if not path.exists():
            continue
        count = count_git_clones(path)
        label = LANG_LABELS[lang]
        if count != zh_clones:
            errors.append(
                f"README{lang}.md ({label}) git clone 数 {count} ≠ 中文版 {zh_clones}"
            )
        else:
            print(f"  ✓ {label}: {count} 条")
    print()

    # ===== 检查 4：docs/LEARNING.{md,en,vi,ta}.md 都存在（主语言）=====
    print("== 检查 4：docs/LEARNING.{{md,en,vi,ta}}.md 存在 ==")
    for lang in FULL_LANGS:
        path = ROOT / f"docs/LEARNING{lang}.md"
        if not path.exists():
            errors.append(f"docs/LEARNING{lang}.md 不存在")
        else:
            label = LANG_LABELS[lang]
            print(f"  ✓ docs/LEARNING{lang}.md ({label})")
    print()

    # ===== 检查 5：chapterN/README.{md,en,vi,ta}.md 都存在（主语言 × 10 章）=====
    print("== 检查 5：chapterN/README.{md,en,vi,ta}.md 齐全（40 个）==")
    missing = []
    for n in CHAPTERS:
        for lang in FULL_LANGS:
            path = ROOT / f"chapter{n}/README{lang}.md"
            if not path.exists():
                missing.append(f"chapter{n}/README{lang}.md")
    if missing:
        errors.append(
            f"缺失 {len(missing)} 个章节 README：{missing[:5]}{'...' if len(missing) > 5 else ''}"
        )
    else:
        print("  ✓ 40 个章节 README 齐全")
    print()

    # ===== 检查 6：每章项目数对齐（主语言）=====
    print("== 检查 6：每章项目数（主语言对齐）==")
    zh_counts = {
        n: project_count_in_table(ROOT / f"chapter{n}/README.md") for n in CHAPTERS
    }
    total_zh = sum(zh_counts.values())
    print(f"  中文基准：{total_zh} 项目，分布 {[zh_counts[n] for n in CHAPTERS]}")
    for lang in FULL_LANGS[1:]:
        label = LANG_LABELS[lang]
        for n in CHAPTERS:
            path = ROOT / f"chapter{n}/README{lang}.md"
            count = project_count_in_table(path)
            zh = zh_counts[n]
            if count == -1:
                # 已经在检查 5 报过了
                continue
            if count != zh:
                errors.append(
                    f"chapter{n}/README{lang}.md ({label}) 项目数 {count} ≠ 中文版 {zh}"
                )
        # 输出汇总
        total = sum(
            project_count_in_table(ROOT / f"chapter{n}/README{lang}.md") for n in CHAPTERS
        )
        if total == total_zh:
            print(f"  ✓ {label}: {total} 项目对齐")
    print()

    # ===== 汇总 =====
    if errors:
        print(f"❌ 发现 {len(errors)} 个问题：")
        for e in errors:
            print(f"   - {e}")
        print()
        print("修复提示：")
        print("  - 文件缺失：从中文版复制并翻译")
        print("  - 项目数不一致：参考中文版 chapterN/README.md 同步项目列表")
        print("  - git clone 不一致：参考 README.md 附录段同步")
        print("  - 内容速览表结构：参考 README.md 的 5 列模板")
        return 1
    print("✓ 所有语言版本结构一致/完整")
    return 0


if __name__ == "__main__":
    sys.exit(main())
