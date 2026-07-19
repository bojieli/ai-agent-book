"""
极简 Code Interpreter 沙箱：在子进程中执行模型生成的 Python 代码。

- 用独立子进程运行，避免污染主进程、并可强制超时。
- 子进程使用与主程序相同的解释器(sys.executable)，因此已预装 python-constraint。
- 捕获 stdout / stderr 一并返回给模型，让它能看到求解结果或报错信息。
"""
import subprocess
import sys
import tempfile
import os


def run_python(code: str, timeout: int = 20) -> str:
    """在子进程沙箱中执行 code，返回合并后的 stdout/stderr 文本。"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False,
                                     encoding="utf-8") as f:
        f.write(code)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True, text=True, timeout=timeout,
        )
        out = proc.stdout
        if proc.stderr.strip():
            out += "\n[stderr]\n" + proc.stderr
        if not out.strip():
            out = "(代码已执行，但没有任何输出。记得用 print() 打印结果。)"
        return out.strip()
    except subprocess.TimeoutExpired:
        return f"[错误] 代码执行超时（超过 {timeout} 秒）。"
    finally:
        os.unlink(path)


if __name__ == "__main__":
    # 自测：用 python-constraint 求解一个最简单的 K&K 谜题
    demo = """
from constraint import Problem
p = Problem()
# True=骑士(说真话), False=无赖(说假话)
p.addVariable('A', [True, False])
p.addVariable('B', [True, False])
# A 说"B 是无赖"：A 的真值 == (B 是无赖) 即 A == (not B)
p.addConstraint(lambda a, b: a == (not b), ['A', 'B'])
# B 说"我们都不是骑士"：B == (not A and not B)
p.addConstraint(lambda a, b: b == ((not a) and (not b)), ['A', 'B'])
for s in p.getSolutions():
    print({k: 'knight' if v else 'knave' for k, v in s.items()})
"""
    print(run_python(demo))
