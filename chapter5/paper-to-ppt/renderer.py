"""
Slidev 渲染器：把 Proposer 生成的 slides.md 真正渲染成“每页一张 PNG”。

这是本实验的关键——Reviewer 之所以能看到 Proposer 看不到的“新信息”，
正是因为我们真的把代码跑起来、渲染出了像素级的截图。

实现：调用本地安装的 Slidev CLI
    npx slidev export slides.md --format png --output <dir> --timeout 60000
Slidev 的 PNG 导出底层用 playwright-chromium 打开每一页并截图。
"""
import glob
import os
import shutil
import subprocess

WORKSPACE = os.path.join(os.path.dirname(__file__), "slidev_workspace")


class RenderError(RuntimeError):
    pass


def render_slides(slides_md: str, out_subdir: str) -> list[str]:
    """
    将 slides_md 文本写入工作区并导出为逐页 PNG。

    参数:
        slides_md:  完整的 Slidev markdown 源码
        out_subdir: 输出子目录名（如 'proposer_iter1'）

    返回:
        按页码排序的 PNG 绝对路径列表。
    """
    os.makedirs(WORKSPACE, exist_ok=True)
    slides_path = os.path.join(WORKSPACE, "slides.md")
    with open(slides_path, "w", encoding="utf-8") as f:
        f.write(slides_md)

    out_dir = os.path.join(WORKSPACE, "exports", out_subdir)
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    # Slidev 的 PNG 导出会在 output 目录下生成 1.png, 2.png ...
    cmd = [
        "npx", "--no-install", "slidev", "export", "slides.md",
        "--format", "png",
        "--output", out_dir,
        "--timeout", "60000",
        "--dark", "false",
    ]
    env = dict(os.environ)
    # 让 playwright 使用项目内安装的 chromium（package.json 里的 playwright-chromium）
    proc = subprocess.run(
        cmd, cwd=WORKSPACE, env=env,
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        raise RenderError(
            "Slidev export 失败:\n"
            f"stdout:\n{proc.stdout[-2000:]}\n"
            f"stderr:\n{proc.stderr[-2000:]}"
        )

    pngs = sorted(
        glob.glob(os.path.join(out_dir, "*.png")),
        key=lambda p: _page_num(p),
    )
    if not pngs:
        raise RenderError(
            f"Slidev export 未产出 PNG。stdout:\n{proc.stdout[-2000:]}"
        )
    return pngs


def _page_num(path: str) -> int:
    base = os.path.splitext(os.path.basename(path))[0]
    digits = "".join(ch for ch in base if ch.isdigit())
    return int(digits) if digits else 0


if __name__ == "__main__":
    # 自检：渲染一个最小的两页 slidev
    demo = """---
theme: default
---

# Hello Slidev

第一页

---

# 第二页

- 渲染自检成功
"""
    paths = render_slides(demo, "selftest")
    print("渲染出的 PNG：")
    for p in paths:
        print("  ", p)
