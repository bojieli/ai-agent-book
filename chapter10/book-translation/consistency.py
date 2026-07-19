"""
术语一致性检查工具。

思路：对每个受关注的英文术语，预先列出它在中文里“几种常见但不同”的译法。
扫描全书各章译文，统计每个术语实际出现了几种不同译法：
  - 只出现 1 种  → 全书一致；
  - 出现 >= 2 种 → 术语漂移（不一致）。

这不是给模型评分，而是用确定性的字符串匹配，客观度量“同一术语是否全书统一”。
"""

# 每个术语：canonical 为推荐/术语表规定译法；variants 为若干“互不相同”的常见译法。
# 注意：variants 之间尽量不互为子串，避免重复计数（如“嵌入向量”归入“嵌入”一族）。
TRACKED_TERMS = [
    {"en": "token",       "canonical": "词元",  "variants": ["词元", "令牌", "标记", "token"]},
    {"en": "embedding",   "canonical": "嵌入",  "variants": ["嵌入", "词向量", "向量表示"]},
    {"en": "prompt",      "canonical": "提示词", "variants": ["提示词", "提示语", "提示"]},
    {"en": "inference",   "canonical": "推理",  "variants": ["推理", "推断"]},
    {"en": "latency",     "canonical": "时延",  "variants": ["延迟", "时延", "延时"]},
    {"en": "attention",   "canonical": "注意力", "variants": ["注意力", "关注度"]},
    {"en": "transformer", "canonical": "Transformer", "variants": ["Transformer", "变换器", "转换器"]},
    {"en": "throughput",  "canonical": "吞吐量", "variants": ["吞吐量", "吞吐率", "通量"]},
    {"en": "fine-tuning", "canonical": "微调",  "variants": ["微调", "精调"]},
]


import re


def _strip_code(text):
    """去掉围栏代码块与行内代码：代码按翻译指南原样保留英文，不应计入术语一致性统计。"""
    text = re.sub(r"```.*?```", " ", text, flags=re.DOTALL)
    text = re.sub(r"`[^`]*`", " ", text)
    return text


# 编辑部“指定术语”（house style）：为几个术语规定一个明确的、区别于模型默认译法的译名。
# 这些译法都是合法且更精确的选择，用来考察“共享术语表能否把指定译法贯彻到全书”。
#   mandated：术语表规定的译法；default：模型自由翻译时常用的默认译法。
MANDATED_TERMS = [
    {"en": "token",     "mandated": "词元",   "default": "标记"},
    {"en": "prompt",    "mandated": "提示词", "default": "提示"},
    {"en": "latency",   "mandated": "时延",   "default": "延迟"},
    {"en": "embedding", "mandated": "嵌入向量", "default": "嵌入"},
]


def check_adherence(translations):
    """
    术语表遵从率：对每个“指定术语”，统计在出现该概念的章节里，
    有多少章使用了术语表规定的译法（而非默认译法）。

    这是管理者模式的核心价值：共享术语表能把指定译法贯彻到每一章；
    单 Agent 看不到术语表，只能用自己的默认译法。
    """
    rows = []
    hit_total = 0
    concept_total = 0
    for t in MANDATED_TERMS:
        m, d = t["mandated"], t["default"]
        chapters_with_concept = 0
        chapters_adhered = 0
        for name, raw in translations.items():
            text = _strip_code(raw)
            has_m = m in text
            # default 若是 mandated 的子串（如“嵌入”是“嵌入向量”子串），需去掉 mandated 再判断
            has_d = (d in text.replace(m, "")) if d in m else (d in text)
            if has_m or has_d:
                chapters_with_concept += 1
                if has_m:
                    chapters_adhered += 1
        if chapters_with_concept:
            concept_total += chapters_with_concept
            hit_total += chapters_adhered
            rows.append({
                "en": t["en"], "mandated": m, "default": d,
                "adhered": chapters_adhered, "total": chapters_with_concept,
            })
    rate = hit_total / concept_total if concept_total else 1.0
    return {"rows": rows, "rate": rate}


def _variant_in_chapter(text, variant, other_variants):
    """
    判断某个 variant 是否在 text 中“独立”出现。
    对“提示”这种会成为“提示词/提示语”子串的情况：仅当去掉更长 variant 后仍出现才算。
    """
    longer = [v for v in other_variants if variant in v and v != variant]
    if not longer:
        return variant in text
    tmp = text
    for v in longer:
        tmp = tmp.replace(v, "")
    return variant in tmp


def analyze(translations):
    """
    translations：{chapter_name: 译文文本}
    返回：
      results：每个术语的分析（用到哪些译法、是否一致、各章用法）
      consistent_terms / total_terms / rate
    """
    results = []
    consistent = 0
    total = 0
    for term in TRACKED_TERMS:
        variants = term["variants"]
        used = {}  # variant -> [出现该译法的章节]
        for name, raw in translations.items():
            text = _strip_code(raw)
            for v in variants:
                others = [x for x in variants if x != v]
                if _variant_in_chapter(text, v, others):
                    used.setdefault(v, []).append(name)
        if not used:
            # 全书都没出现该术语，跳过统计
            continue
        total += 1
        distinct = list(used.keys())
        is_consistent = len(distinct) == 1
        if is_consistent:
            consistent += 1
        results.append(
            {
                "en": term["en"],
                "canonical": term["canonical"],
                "distinct_used": distinct,
                "consistent": is_consistent,
                "by_variant": used,
            }
        )
    rate = consistent / total if total else 1.0
    return {
        "results": results,
        "consistent_terms": consistent,
        "total_terms": total,
        "rate": rate,
    }
