"""
阶段 2：结构化抽取 —— 用发现出来的 schema 从判例文本抽取结构化因子。

流程：
  1. 先判定案件罪名（从 schema 已知的罪名里选）；
  2. 按「核心通用因子 + 该罪名扩展因子」逐项抽取，输出结构化 JSON；
  3. 文本未提及的因子返回 null（供对话 Agent 判断"还缺什么信息"）；
  4. 带磁盘缓存（data/extracted.jsonl），一次性抽取后重跑几乎免费。

输出统一为 {"charge": <罪名>, <factor_key>: <值|null>, ...}。
"""
import json
import os

from config import MODEL, get_client
from discovery import factors_for_charge, load_schema

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_PATH = os.path.join(DATA_DIR, "extracted.jsonl")


def _factor_lines(factors):
    lines = []
    for f in factors:
        if f["kind"] == "numeric":
            t = "数值(整数，去掉单位)"
        elif f["kind"] == "bool":
            t = "true/false"
        else:
            t = "取值之一：" + "/".join(f.get("values", [])) if f.get("values") else "分类取值"
        lines.append(f'  - "{f["key"]}": {t}  # {f["name_cn"]}')
    return "\n".join(lines)


def _charges(schema):
    return list(schema.get("extensions", {}).keys())


def extract_one(fact_text, schema=None, client=None, charge=None):
    """从单条判例文本抽取 {charge, factors...}。缺失因子取 null。

    charge 已知时（数据集抽取）直接沿用，省一次调用；未知时（对话新案情）先让 LLM 判定。
    """
    schema = schema or load_schema()
    client = client or get_client()
    charges = _charges(schema)

    # 第 1 步：判定罪名（仅在未提供时调用 LLM）
    if charge is None:
        charge_resp = client.chat.completions.create(
            model=MODEL, temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content":
                    "判断下述刑事案件属于哪个罪名，只能从这些里选："
                    + "/".join(charges) + '。只输出 JSON：{"charge": "..."}。'},
                {"role": "user", "content": fact_text},
            ],
        )
        charge = json.loads(charge_resp.choices[0].message.content).get("charge")
    if charge not in charges:  # 兜底：默认第一个罪名
        charge = charges[0]

    # 第 2 步：按该罪名适用的因子抽取
    factors = factors_for_charge(schema, charge)
    sys = (
        "你是协助司法数据分析的信息抽取助手。请从判决书「事实」段落中抽取以下因子，"
        "只输出一个 JSON 对象：\n" + _factor_lines(factors) + "\n\n规则：\n"
        "1. 数值因子输出整数（去掉'元''人民币''名'等字样）。\n"
        "2. 是非因子：文本明确支持则 true，明确否定则 false。\n"
        "3. 分类因子只能取给定取值之一。\n"
        "4. 文本完全没有相关信息的因子取 null（不要臆测）。\n"
        "5. 只输出 JSON，不要解释。"
    )
    resp = client.chat.completions.create(
        model=MODEL, temperature=0,
        response_format={"type": "json_object"},
        messages=[{"role": "system", "content": sys},
                  {"role": "user", "content": f"判决书事实段落：\n{fact_text}"}],
    )
    raw = json.loads(resp.choices[0].message.content)
    return _normalize(raw, charge, factors)


def _normalize(raw, charge, factors):
    out = {"charge": charge}
    for f in factors:
        v = raw.get(f["key"])
        if v is None or v == "":
            out[f["key"]] = None
        elif f["kind"] == "numeric":
            if isinstance(v, str):
                digits = "".join(ch for ch in v if ch.isdigit())
                out[f["key"]] = int(digits) if digits else None
            else:
                try:
                    out[f["key"]] = int(v)
                except (TypeError, ValueError):
                    out[f["key"]] = None
        elif f["kind"] == "bool":
            out[f["key"]] = bool(v) if isinstance(v, bool) else str(v).lower() in ("true", "1", "是")
        else:  # categorical
            out[f["key"]] = str(v)
    return out


def load_dataset():
    path = os.path.join(DATA_DIR, "cases.jsonl")
    with open(path, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def extract_dataset(schema, use_cache=True, verbose=True):
    """对整个数据集抽取，带缓存。返回 list，每项含原案例字段 + `extracted`。"""
    cases = load_dataset()
    cache = {}
    if use_cache and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, encoding="utf-8") as fh:
            for line in fh:
                if line.strip():
                    rec = json.loads(line)
                    cache[rec["id"]] = rec["extracted"]

    client = get_client()
    results, n_called = [], 0
    for c in cases:
        if c["id"] in cache:
            extracted = cache[c["id"]]
        else:
            extracted = extract_one(c["fact"], schema=schema, client=client,
                                    charge=c.get("charge"))
            cache[c["id"]] = extracted
            n_called += 1
            if verbose:
                print(f"  抽取 {c['id']} ({extracted.get('charge')}) ... 完成")
        results.append({**c, "extracted": extracted})

    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        for r in results:
            fh.write(json.dumps({"id": r["id"], "extracted": r["extracted"]},
                                ensure_ascii=False) + "\n")
    if verbose:
        print(f"  本次实际调用 LLM {n_called} 次，其余命中缓存。")
    return results
