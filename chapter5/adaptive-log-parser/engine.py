"""
engine.py —— 自适应日志解析引擎（自愈闭环的“运行时”）

设计要点：
- 引擎维护一个**解析器注册表**（有序列表）。每来一行日志，依次尝试每个解析器，
  谁能解析（返回非空 dict）就用谁的结果；全部失败则抛出 ParseError —— 这就是
  “前端检测到无法解析的新格式”的信号，触发后续的自愈流程。
- 每个解析器就是一个纯函数 `parse(line: str) -> dict | None`：
    * 能解析 → 返回结构化字段（dict）
    * 不认识这行 → 返回 None（把机会让给别的解析器，避免“抢答”）
- 生成的解析器可以持久化成 parsers/*.py 模块，下次启动直接热加载复用，无需再问 Agent。

注意：这里对“可视化”做了降级——书中用虚拟浏览器 + Vision LLM 验证渲染效果，
本项目改为对解析函数做**数据结构断言**（见 tester.py），核心自愈闭环是真实实现的。
"""

from __future__ import annotations

import importlib.util
import json
import os
from typing import Callable, Dict, List, Optional, Tuple

# 一个解析器 = (名字, 解析函数)
ParserFn = Callable[[str], Optional[Dict]]


class ParseError(Exception):
    """所有已注册解析器都无法解析该行时抛出，携带原始样本供 Agent 分析。"""

    def __init__(self, line: str):
        self.line = line
        super().__init__(f"没有任何已注册解析器能解析该行：{line!r}")


def builtin_json_parser(line: str) -> Optional[Dict]:
    """内置的基础解析器：只认标准 JSON 行（JSON Lines）。

    形如：{"timestamp": "...", "level": "INFO", "message": "..."}
    不是 JSON，或不含基本字段，则返回 None（不是我的格式）。
    """
    line = line.strip()
    if not (line.startswith("{") and line.endswith("}")):
        return None
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict):
        return None
    # 至少要有一个基本字段，才认为是“合法的 JSON 日志”
    if not any(k in obj for k in ("timestamp", "level", "message")):
        return None
    return obj


class LogParserEngine:
    """日志解析系统：持有一组解析器，并支持热加载注册新解析器。"""

    def __init__(self) -> None:
        self._parsers: List[Tuple[str, ParserFn]] = []

    # -- 注册 / 查询 --------------------------------------------------------
    def register(self, name: str, fn: ParserFn) -> None:
        """注册（或替换同名）解析器。新解析器优先级更高，放到列表末尾后再尝试。"""
        # 若同名已存在则先移除，实现“热更新替换”
        self._parsers = [(n, f) for (n, f) in self._parsers if n != name]
        self._parsers.append((name, fn))

    @property
    def parser_names(self) -> List[str]:
        return [n for n, _ in self._parsers]

    # -- 解析 ---------------------------------------------------------------
    def parse_line(self, line: str) -> Dict:
        """尝试用每个解析器解析一行；成功则在结果里标注 _parser。全部失败抛 ParseError。"""
        for name, fn in self._parsers:
            try:
                result = fn(line)
            except Exception:
                # 某个解析器对这行报错，不代表别的不行，继续尝试
                continue
            if result is not None:
                return {**result, "_parser": name}
        raise ParseError(line)

    # -- 热加载：从 .py 文件加载 parse 函数 ----------------------------------
    @staticmethod
    def load_parser_from_file(path: str) -> ParserFn:
        """把一个 parsers/*.py 模块动态导入，取出其中的 parse 函数。"""
        module_name = "genparser_" + os.path.splitext(os.path.basename(path))[0]
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"无法加载模块：{path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # 执行模块，定义 parse
        fn = getattr(module, "parse", None)
        if not callable(fn):
            raise ImportError(f"{path} 中未找到可调用的 parse(line) 函数")
        return fn

    def load_persisted(self, parsers_dir: str) -> List[str]:
        """启动时把 parsers/ 目录下已持久化的解析器全部热加载注册（复用历史成果）。"""
        loaded: List[str] = []
        if not os.path.isdir(parsers_dir):
            return loaded
        for fname in sorted(os.listdir(parsers_dir)):
            if not fname.endswith(".py") or fname.startswith("_"):
                continue
            path = os.path.join(parsers_dir, fname)
            fn = self.load_parser_from_file(path)
            name = os.path.splitext(fname)[0]
            self.register(name, fn)
            loaded.append(name)
        return loaded
