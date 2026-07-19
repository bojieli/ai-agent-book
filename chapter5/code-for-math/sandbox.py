"""子进程 Python 沙箱：在隔离的子进程中执行模型生成的代码，带超时限制。

预装 sympy / numpy / scipy（随本项目 requirements 一并安装）。
之所以用子进程而不是 exec()，是为了：
  1. 隔离：模型代码崩溃 / 死循环不会影响主进程；
  2. 超时：可强制杀掉执行过久的代码；
  3. 干净的命名空间：每次执行都是全新解释器。
"""

import subprocess
import sys
import tempfile
import os

# 在执行前注入的前置代码：预导入常用数学库，方便模型直接使用。
PREAMBLE = """
import math
import sympy
import numpy as np
import scipy
from sympy import *
"""


def run_python(code: str, timeout: int = 20) -> str:
    """在子进程沙箱中执行 Python 代码，返回 stdout/stderr 文本。

    参数:
        code: 待执行的 Python 源码（模型生成）。
        timeout: 超时秒数，超过则终止子进程。
    返回:
        执行输出（合并 stdout 与 stderr）。模型应通过 print() 输出结果。
    """
    full_code = PREAMBLE + "\n" + code

    # 写入临时文件，用当前解释器（已装好 sympy/numpy/scipy）执行。
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(full_code)
        path = f.name

    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout,
            # 在临时目录里执行，避免误读写项目文件（仍能访问已安装的库）。
            cwd=tempfile.gettempdir(),
        )
        out = proc.stdout
        if proc.stderr.strip():
            out += "\n[stderr]\n" + proc.stderr
        if not out.strip():
            out = "(代码没有任何输出，请记得用 print() 打印结果)"
        # 截断超长输出，避免撑爆上下文。
        return out[:4000]
    except subprocess.TimeoutExpired:
        return f"[错误] 代码执行超时（超过 {timeout} 秒），可能存在死循环或计算量过大。"
    except Exception as e:  # noqa: BLE001
        return f"[错误] 执行失败: {e}"
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


if __name__ == "__main__":
    # 简单自测
    print(run_python("from sympy import factorint; print(factorint(360))"))
    print(run_python("print(sum(1 for n in range(1,2025) if n%3 and n%5 and n%7))"))
