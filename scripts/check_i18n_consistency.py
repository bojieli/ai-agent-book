#!/usr/bin/env python3
"""检查多语言版本的结构完整性。

防止主页或某章 README 改动后，其它语言版本跟不上而漂移。CI 中运行；
本地也可直接 `python scripts/check_i18n_consistency.py` 跑。

核心原则：**自动发现语言，不硬编码**。下次有人加新语言（日语、韩语…）时，
CI 自动适配，无需改脚本。

严格规则：**只要某语言有自己的主 README，CI 就要求它完整**：
  - 10 章 chapterN/README.{lang}.md
  - docs/LEARNING.{lang}.md
  - 每章项目数与中文版对齐
  - git clone 命令数对齐
  - 内容速览表 ≥5 列

退出码：0 = 全部一致；1 = 发现不一致。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CHAPTERS = range(1, 11)


def lang_label(suffix: str) -> str:
    """''.en'' → 'en'，'' → 'zh'。"""
    return suffix.lstrip(".") or "zh"


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


def discover_main_readmes() -> list[str]:
    """扫描顶层 README*.md，返回所有语言后缀列表（含 "" 表示中文）。

    例如 ["", ".en", ".vi", ".ta", ".zhtw"]
    """
    suffixes = []
    for path in sorted(ROOT.glob("README*.md")):
        m = re.match(r"^README(\..*)?\.md$", path.name)
        if m:
            suffixes.append(m.group(1) or "")
    return suffixes


def main() -> int:
    errors: list[str] = []

    # ===== 自动发现语言 =====
    main_langs = discover_main_readmes()

    print("== 自动发现语言 ==")
    print(f"  发现 {len(main_langs)} 个主 README（全部要求完整翻译）:")
    for lang in main_langs:
        print(f"    {lang_label(lang)}")
    print()

    # ===== 检查 1：每个发现的主 README 都有完整结构 =====
    print("== 检查 1：主 README 内容速览表结构（≥5 列）==")
    for lang in main_langs:
        path = ROOT / f"README{lang}.md"
        cols = toc_table_columns(path)
        label = lang_label(lang)
        if cols < 5:
            errors.append(
                f"README{lang}.md ({label}) 内容速览表列数 {cols} < 5（应至少 5 列：章/主题/核心/正文/代码）"
            )
        else:
            print(f"  ✓ {label}: {cols} 列")
    print()

    # ===== 检查 2：git clone 命令数对齐（以中文版为基准）=====
    print("== 检查 2：主 README git clone 命令数 ==")
    zh_clones = count_git_clones(ROOT / "README.md")
    print(f"  中文基准：{zh_clones} 条")
    for lang in main_langs:
        if lang == "":
            continue
        path = ROOT / f"README{lang}.md"
        count = count_git_clones(path)
        label = lang_label(lang)
        if count != zh_clones:
            errors.append(
                f"README{lang}.md ({label}) git clone 数 {count} ≠ 中文版 {zh_clones}"
            )
        else:
            print(f"  ✓ {label}: {count} 条")
    print()

    # ===== 检查 3：每个主 README 语言必须有 docs/LEARNING.{lang}.md =====
    print("== 检查 3：docs/LEARNING.{lang}.md 齐全 ==")
    for lang in main_langs:
        path = ROOT / f"docs/LEARNING{lang}.md"
        label = lang_label(lang)
        if not path.exists():
            errors.append(
                f"docs/LEARNING{lang}.md 不存在（{label} 是主语言，需有学习建议文档）"
            )
        else:
            print(f"  ✓ docs/LEARNING{lang}.md ({label})")
    print()

    # ===== 检查 4：每个主 README 语言必须有全部 10 章 README =====
    print("== 检查 4：chapterN/README.{lang}.md 齐全 ==")
    for lang in main_langs:
        missing = []
        for n in CHAPTERS:
            path = ROOT / f"chapter{n}/README{lang}.md"
            if not path.exists():
                missing.append(str(n))
        label = lang_label(lang)
        if missing:
            errors.append(
                f"{label} 缺章节 README：第 {', '.join(missing)} 章"
            )
        else:
            print(f"  ✓ {label}: 10 章齐全")
    print()

    # ===== 检查 5：每章项目数对齐（所有主 README 语言）=====
    print("== 检查 5：每章项目数（所有语言对齐）==")
    zh_counts = {
        n: project_count_in_table(ROOT / f"chapter{n}/README.md") for n in CHAPTERS
    }
    total_zh = sum(zh_counts.values())
    print(f"  中文基准：{total_zh} 项目，分布 {[zh_counts[n] for n in CHAPTERS]}")
    for lang in main_langs:
        if lang == "":
            continue
        label = lang_label(lang)
        total = 0
        mismatches = []
        for n in CHAPTERS:
            path = ROOT / f"chapter{n}/README{lang}.md"
            count = project_count_in_table(path)
            total += max(count, 0)
            zh = zh_counts[n]
            if count != zh:
                mismatches.append(f"第{n}章 {count}≠{zh}")
        if mismatches:
            errors.append(
                f"{label} 项目数不一致（{len(mismatches)} 处）：{'; '.join(mismatches[:3])}"
            )
        else:
            print(f"  ✓ {label}: {total} 项目对齐")
    print()

    # ===== 检查 6：主 README 语言切换栏完整性 =====
    print("== 检查 6：主 README 语言切换栏列出所有语言 ==")
    # 中文版 README.md 的语言栏应该列出所有 main_langs
    zh_text = (ROOT / "README.md").read_text(encoding="utf-8")
    # 找语言切换栏（一般在文件开头）
    switcher_match = re.search(
        r"\*\*[^*]*中文[^*]*\*\*.*?(?=\n\n|\n[^*])", zh_text, re.DOTALL
    )
    if switcher_match:
        switcher = switcher_match.group(0)
        missing_in_switcher = []
        for lang in main_langs:
            if lang == "":
                continue
            # 找 README{lang}.md 链接
            if f"README{lang}.md" not in switcher:
                missing_in_switcher.append(lang_label(lang))
        if missing_in_switcher:
            errors.append(
                f"README.md 语言切换栏缺少：{', '.join(missing_in_switcher)}"
            )
        else:
            print(f"  ✓ README.md 列出全部 {len(main_langs)} 种语言")
    else:
        print("  ⚠️ 未找到语言切换栏（跳过此项检查）")
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
        print("  - 语言切换栏：参考 README.md 顶部，加入新语言链接")
        return 1
    print("✓ 所有语言版本结构一致/完整")
    return 0


if __name__ == "__main__":
    sys.exit(main())
