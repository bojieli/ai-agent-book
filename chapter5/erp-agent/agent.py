"""
NL -> SQL Agent（artifact 模式）。

Agent 只负责「生成 SQL 制品」，不亲自搬运数据：
真正的数据查询由系统（demo.py）用生成的 SQL 在 SQLite 上执行，结果表直接呈现。
"""

import os
import re
from datetime import date

from openai import OpenAI

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.6-luna")

# --- 通用 OpenRouter 兜底 ---
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _map_to_openrouter_model(model: str) -> str:
    """把直连模型名映射为 OpenRouter 上的 id（非可映射 id 统一兜底到当前廉价旗舰）。"""
    if not model or "/" in model:
        return model or "openai/gpt-5.6-luna"
    m = model.lower()
    if m.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai/" + model
    if m.startswith("claude"):
        if "haiku" in m:
            return "anthropic/claude-haiku-4.5"
        if "sonnet" in m:
            return "anthropic/claude-sonnet-4.6"
        return "anthropic/claude-opus-4.8"
    if m.startswith("gemini"):
        return "google/" + model
    return "openai/gpt-5.6-luna"


def _make_client_and_model(model: str):
    """构造客户端并解析模型名，含通用 OpenRouter 兜底。返回 (client, resolved_model)。

    - 有 OPENAI_API_KEY：直连；但 model 为 gpt-5.x 且同时设置了 OPENROUTER_API_KEY
      时优先走 OpenRouter（直连 gpt-5.6 需组织实名认证）。
    - 无 OPENAI_API_KEY 但有 OPENROUTER_API_KEY：改走 OpenRouter（模型名自动映射）。
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    base_url = os.environ.get("OPENAI_BASE_URL")
    orkey = os.environ.get("OPENROUTER_API_KEY")
    prefer_or = bool(orkey) and (model or "").lower().startswith("gpt-5")
    if prefer_or or (not api_key and orkey):
        api_key, base_url, model = orkey, OPENROUTER_BASE_URL, _map_to_openrouter_model(model)
    kw = {}
    if api_key:
        kw["api_key"] = api_key
    if base_url:
        kw["base_url"] = base_url
    return OpenAI(**kw), model

SYSTEM_PROMPT = """你是一个「自然语言转 SQL」的 ERP 数据助手。
用户给你一个中文问题，你只输出一条可直接执行的 **SQLite** SQL 查询，不要任何解释、不要 markdown 代码块。

今天的日期是 {today}。但**严禁在 SQL 里硬编码年份数字**（如 '2024'、'2022-01-01'），
一律用 strftime(...,'now',...) 从数据库当前日期推导，避免年份猜错。

数据库 schema（SQLite）：
  employees(emp_id INTEGER 主键, name 姓名, department 部门, level 级别[数字越大越高],
            hire_date 入职日期'YYYY-MM-DD', leave_date 离职日期'YYYY-MM-DD'，NULL 表示在职)
  salaries(emp_id, pay_date 发薪日期'YYYY-MM-01'[每月一条], salary 当月工资)
  salaries.emp_id 关联 employees.emp_id。

业务与方言约定：
  - 「今年」= strftime('%Y','now')，「去年」= strftime('%Y','now','-1 year')，
    「前年」= strftime('%Y','now','-2 years')。
  - 计算「今天」请用 date('now')（不要带时间部分）；两个日期相差天数用
    julianday(date('now')) - julianday(hire_date)。
  - 「A部门」= 研发部，「B部门」= 销售部。
  - 「在职」指 leave_date IS NULL。
  - 发薪月份可用 strftime('%Y-%m', pay_date) 得到 'YYYY-MM'。
  - 只输出一条 SELECT（可含 WITH/CTE），不要写多条语句或 DDL/DML。

严格按用户附带的「返回列」要求组织 SELECT 的列与顺序。
"""


class SQLAgent:
    def __init__(self, model: str = MODEL):
        self.client, self.model = _make_client_and_model(model)

    def generate_sql(self, nl_question: str, hint: str) -> str:
        user = f"问题：{nl_question}\n要求：{hint}\n请只输出一条 SQLite SQL。"
        # 推理模型（gpt-5 / o 系列等）不接受 temperature=0。
        _reasoning = any(k in (self.model or "").lower()
                         for k in ("gpt-5", "o1", "o3", "o4", "thinking", "reasoner", "kimi-k3"))
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=1 if _reasoning else 0,
            messages=[
                {"role": "system",
                 "content": SYSTEM_PROMPT.format(today=date.today().isoformat())},
                {"role": "user", "content": user},
            ],
        )
        return _clean_sql(resp.choices[0].message.content)


def _clean_sql(text: str) -> str:
    """去掉 markdown 代码块围栏等杂质，只留 SQL。"""
    text = text.strip()
    # 去掉 ```sql ... ``` 或 ``` ... ```
    fence = re.match(r"^```(?:sql)?\s*(.*?)\s*```$", text, re.DOTALL | re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    # 去掉可能残留的前缀反引号
    text = text.strip("`").strip()
    return text
