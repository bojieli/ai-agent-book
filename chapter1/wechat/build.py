#!/usr/bin/env python3
"""构建微信公众号笔记：注入真实源码 + 把 Mermaid 渲染成独立 PNG。

模板（`*.template.md`）里有两类标记：

1. 代码占位符

       <!--INCLUDE context/agent.py 44 51-->

   构建后变成一段 ```python 围栏代码，内容是该文件第 44–51 行（含端点，1-based），
   围栏里以注释标注文件路径，方便读者到仓库对照。

2. Mermaid 图

       ```mermaid
       flowchart LR
         A --> B
       ```

   构建后渲染成 `images/<篇名>-fig<N>-<内容哈希>.png`，模板里的代码块替换成
   图片引用。公众号不解析 Mermaid，必须用图片；文件名带内容哈希，所以改了图
   一定会生成新文件、不会拿到旧缓存。

用法：
    python build.py                  # 生成 *.md 与 images/ 下的 PNG
    python build.py --check          # 只校验占位符能否解析，不写文件、不渲染
    python build.py --keep-mermaid   # 保留 mermaid 代码块（不渲染图片）

环境变量：
    MMDC_CHROME   Chrome/Chromium 可执行文件路径；不设则自动探测常见位置。

这样做的原因：公众号无法上传附件、也不解析 Mermaid，代码和图都必须内嵌成成品；
而手抄代码会引入错误，所以所有代码都从仓库原文注入，保证与运行结果一一对应。
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]  # ai-agent-book/
CHAPTER = HERE.parent  # chapter1/
IMAGES = HERE / "images"

MMDC_VERSION = "11"
CHROME_CANDIDATES = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    shutil.which("google-chrome") or "",
    shutil.which("chromium") or "",
)

PLACEHOLDER = re.compile(
    r"^[ \t]*<!--\s*INCLUDE\s+(\S+)(?:\s+(\d+)\s+(\d+))?\s*-->[ \t]*$",
    re.MULTILINE,
)
MERMAID = re.compile(r"^```mermaid\n([\s\S]*?)^```[ \t]*$", re.MULTILINE)


def _resolve(rel: str) -> Path:
    """占位符里的路径相对 chapter1/ 解析。"""
    candidate = (CHAPTER / rel).resolve()
    if not candidate.is_file():
        candidate = (REPO / rel).resolve()
    if not candidate.is_file():
        raise FileNotFoundError(f"占位符引用的文件不存在: {rel}")
    return candidate


def expand_code(text: str) -> tuple[str, int]:
    """替换所有代码占位符，返回 (新文本, 替换次数)。"""
    count = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count
        rel, start, end = match.group(1), match.group(2), match.group(3)
        path = _resolve(rel)
        lines = path.read_text(encoding="utf-8").splitlines()
        if start is None:
            selected = lines
            label = rel
        else:
            first, last = int(start), int(end)
            if first < 1 or last > len(lines) or first > last:
                raise ValueError(
                    f"{rel}: 行号范围 {first}-{last} 越界（文件共 {len(lines)} 行）"
                )
            selected = lines[first - 1:last]
            label = f"{rel}:{first}-{last}"
        count += 1
        body = "\n".join(selected).rstrip("\n")
        return f"```python\n# {label}\n{body}\n```"

    return PLACEHOLDER.sub(repl, text), count


def _chrome_path() -> str | None:
    override = os.getenv("MMDC_CHROME")
    if override and Path(override).exists():
        return override
    for candidate in CHROME_CANDIDATES:
        if candidate and Path(candidate).exists():
            return candidate
    return None


def render_mermaid(source: str, out_png: Path) -> None:
    """把一段 Mermaid 源码渲染为 PNG（经 mmdc + 本机 Chrome）。"""
    chrome = _chrome_path()
    if chrome is None:
        raise RuntimeError(
            "找不到 Chrome/Chromium。请设置 MMDC_CHROME 指向可执行文件，"
            "或改用 --keep-mermaid 保留 Mermaid 代码块。"
        )
    out_png.parent.mkdir(parents=True, exist_ok=True)
    mmd = out_png.with_suffix(".mmd")
    mmd.write_text(source, encoding="utf-8")
    cfg = out_png.with_suffix(".puppeteer.json")
    cfg.write_text(
        '{"executablePath": %s, "args": ["--no-sandbox"]}'
        % _json_str(chrome),
        encoding="utf-8",
    )
    cmd = [
        "npx", "-y", f"@mermaid-js/mermaid-cli@{MMDC_VERSION}",
        "-i", mmd.name, "-o", out_png.name, "-p", cfg.name,
        "-q", "-b", "white", "-w", "1400",
    ]
    result = subprocess.run(
        cmd, cwd=out_png.parent, capture_output=True, text=True, timeout=300
    )
    mmd.unlink(missing_ok=True)
    cfg.unlink(missing_ok=True)
    if result.returncode != 0 or not out_png.exists():
        raise RuntimeError(
            f"Mermaid 渲染失败 ({out_png.name}): "
            f"{(result.stderr or result.stdout).strip()[:400]}"
        )


def _json_str(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def expand_mermaid(text: str, stem: str, *, keep: bool) -> tuple[str, int, int]:
    """把 Mermaid 代码块替换为 PNG 图片引用。

    Returns:
        (新文本, 图片数量, 新渲染数量)。`keep=True` 时原样返回。
    """
    if keep:
        return text, 0, 0
    count = 0
    rendered_now = 0

    def repl(match: re.Match[str]) -> str:
        nonlocal count, rendered_now
        source = match.group(1).rstrip("\n")
        digest = hashlib.sha256(source.encode("utf-8")).hexdigest()[:8]
        count += 1
        png = IMAGES / f"{stem}-fig{count}-{digest}.png"
        if not png.exists():
            render_mermaid(source, png)
            rendered_now += 1
        return f"![图 {count}](images/{png.name})"

    return MERMAID.sub(repl, text), count, rendered_now


def prune_images(keep: set[str], *, apply: bool) -> list[str]:
    """删除不再被任何成品引用的 PNG（内容哈希变了会留下旧文件）。"""
    if not IMAGES.is_dir():
        return []
    stale = [p.name for p in IMAGES.glob("*.png") if p.name not in keep]
    if apply:
        for name in stale:
            (IMAGES / name).unlink()
    return sorted(stale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="只校验不写文件")
    parser.add_argument(
        "--keep-mermaid", action="store_true",
        help="保留 Mermaid 代码块，不渲染 PNG",
    )
    args = parser.parse_args()

    templates = sorted(HERE.glob("*.template.md"))
    if not templates:
        print("没有找到 *.template.md")
        return 1

    total_code = total_figs = total_new = 0
    used_images: set[str] = set()

    for template in templates:
        stem = template.name.replace(".template.md", "")
        try:
            text, n_code = expand_code(template.read_text(encoding="utf-8"))
            text, n_fig, n_new = expand_mermaid(
                text, stem, keep=args.keep_mermaid
            )
        except (FileNotFoundError, ValueError, RuntimeError) as exc:
            print(f"✗ {template.name}: {exc}")
            return 1

        out = HERE / f"{stem}.md"
        for m in re.finditer(r"!\[[^\]]*\]\(images/([^)]+)\)", text):
            used_images.add(m.group(1))

        new_note = f"（新渲染 {n_new}）" if n_new else ""
        print(
            f"✓ {out.name}: {n_code} 段代码，{n_fig} 张图{new_note}，"
            f"{len(text)} 字符"
        )
        total_code += n_code
        total_figs += n_fig
        total_new += n_new
        if not args.check:
            out.write_text(text, encoding="utf-8")

    if not args.check and not args.keep_mermaid:
        stale = prune_images(used_images, apply=True)
        if stale:
            print(f"\n清理 {len(stale)} 个不再引用的 PNG：{', '.join(stale)}")

    print(
        f"\n合计注入 {total_code} 段代码、{total_figs} 张 Mermaid 图"
        f"（本次新渲染 {total_new} 张）。"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
