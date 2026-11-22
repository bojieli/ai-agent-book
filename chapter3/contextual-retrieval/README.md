# Contextual Retrieval System / 上下文感知检索系统

## 给同一段原文加一句背景，排名会怎样变？

查询“国家的根本任务是什么？”时，答案就在《宪法》序言的一段原文里。用 BM25 检索，这段排第二；把“中华人民共和国宪法—序言”以及“国家根本任务”等背景词加到片段开头，再用同一句话搜索，它就排到了第一。打开下面记录里的 `q02`，对照 `宪法_chunk_1` 的 `plain` 和 `prefix`：原文已经有答案，前缀改变的是读者能否先找到它。接下来可以用同样的方法检查其他题，看哪些片段获益，哪些反而往后排。

正式运行由 LLM 根据原文与目标块生成前缀，在相同 15 个查询上比较两套索引。BM25 recall@1 为 0.60 → 0.80，稠密检索为 0.867 → 0.933；混合检索 recall@5 为 0.933 → 1.0。下文离线 CLI 使用已准备的前缀，输出用于机制演示。正文另外引用的 Anthropic 49% / 67% 是其报告中的 top-20 检索失败率相对降幅，指标及测试资料与本项目分别记录。

运行索引：[validation/latest.json](validation/latest.json)；结果与请求记录：[20260729T205807Z-3_10-35531780](validation/runs/20260729T205807Z-3_10-35531780/)。


文档中的“该规定”或“上述方法”离开上下文后常常难以理解。本实验在建立索引前给片段补充简短背景，观察检索能否更准确地找到它。

[English](#english)

[孤立的片段缺了什么](#learning-0) · [选择已生成的前缀或重新生成](#learning-1) · [比较添加前缀前后的排名](#learning-2) · [判断背景信息帮了哪道题](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 孤立的片段缺了什么

背景前缀说明片段属于哪份文档、讨论什么主题。它可以让原本缺少关键词的片段更容易被检索，但生成的背景也可能错误，或让多个片段变得过于相似。因此需要同时检查召回变化与前缀内容。

### 给片段补充背景，为什么可能有帮助

一个片段只写着“该政策于次年生效”，脱离全文后便缺少政策名称和年份。上下文增强尝试为它补充这类定位信息，使查询更容易匹配到它。但新增的背景是模型生成的内容，必须回到原文核对。下面的流程应同时保留原始片段和增强文本，才能判断增益来自必要背景，还是混入了问题的答案或其他额外信息。

实现时，先把文档切成块，保留一份原文索引作为对照，再为同一批块生成前缀，建立第二份索引。检索时用同一个问题查两份索引，比较目标块的名次。完整流水线支持稀疏检索、稠密检索、混合检索与重排；用 `use_contextual=False` 可以切回原文对照。

<a id="learning-1"></a>

## 选择已生成的前缀或重新生成

离线对照使用随附的 [22 个文本块](document_store.json) 和 [15 个查询](evaluation/retrieval_eval.json)。运行 `compare_retrieval.py --per-query` 就能比较同一问题的排名；要研究前缀本身怎样生成，再配置模型。 使用这份已保存的前缀和 jieba 分词时，BM25 排第一的片段命中标注答案的查询由 9 道增至 13 道，前五名命中的查询则同为 14 道。页首正式运行重新生成了前缀，两个实验应各自对照自己的排名。

<a id="learning-2"></a>

## 比较添加前缀前后的排名

先运行逐查询比较，选择一条普通分块漏检、补充背景后命中的案例。阅读原文、分块和前缀，解释多出的文字为什么有帮助。再选择一条没有改善的案例，寻找这种方法的边界。

### 核心实验：离线量化召回提升（实验 3-10）

`compare_retrieval.py` **完全离线**量化：同一批文本块分别以无上下文 / 有上下文前缀两种方式建 BM25 索引，在 `evaluation/retrieval_eval.json`（15 查询 + 人工 gold 块）上比较 `recall@k`。**无需 API 或检索服务**（BM25 + jieba）。

```bash
python compare_retrieval.py
python compare_retrieval.py --per-query
python compare_retrieval.py --query "国家主席有哪些职权？" --top-k 5
python compare_retrieval.py --mode plain
python compare_retrieval.py --output result.json
python compare_retrieval.py --help
```

真实输出（22 个《宪法》《检察官法》文本块，15 查询）：

```
检索召回对比：无上下文分块  vs.  上下文感知检索（BM25）
====================================================================
方法                  recall@1    recall@3    recall@5
----------------------------------------------------
无上下文 (plain)          60.0%      86.7%      93.3%
有上下文 (ctx)            86.7%      86.7%      93.3%
----------------------------------------------------
提升 (Δpp)             +26.7pp      +0.0pp      +0.0pp
----------------------------------------------------
失败率下降                    67%          0%          0%
```

### 同样是十五道题，为什么有两个首位召回率？

用上面的 `--output result.json` 保存离线结果，再与正式运行逐题配对。离线脚本从 `document_store.json` 读取已经加好前缀的文本；正式运行的 `campaign.py` 根据文档和目标块重新生成了前缀。两份结果都可以复查：

```bash
python - <<'PYTHON'
import json
from pathlib import Path

local = json.loads(Path("result.json").read_text())["contextual"]["per_query"]
path = Path("validation/runs/20260729T205807Z-3_10-35531780/evidence.json")
saved = json.loads(path.read_text())["results"]["contextual_bm25"]["per_query"]
by_id = {row["id"]: row for row in saved}
for row in local:
    other = by_id[row["id"]]
    if row["rank"] != other["rank"]:
        print(row["id"], row["query"], "离线", row["rank"], "正式", other["rank"])
PYTHON
```

两份排名只有两题不同。问宪法通过和修正时间的 `q01` 在离线示例中排第一，在正式记录中排第二。问全国人大常委会职权的 `q08` 分别排第十四和第十二，都未进入前五。因此，两份结果首位命中数相差的一题就是 `q01`：离线为 13/15（86.7%），正式为 12/15（80%）。离线表中的“失败率下降 67%”也可以按题数核算：与原始分块相比，首位漏检从六题减为两题，少了六题中的四题。

这个离线脚本只实现了 BM25。指定 `--method embedding` 或 `hybrid` 时，它会提示并回退到 BM25；要查正式运行中的稠密与混合排名，可分别读上面同一份记录的 `contextual_dense` 和 `contextual_hybrid`。稠密检索与重排的实现见 [contextual_tools.py](contextual_tools.py)。

### 快速开始

```bash
# 在仓库根目录使用统一的第 3 章环境
uv sync --locked --python 3.12 --extra ch3

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch3]"

cd chapter3/contextual-retrieval

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env

# 另开一个终端运行完整检索流水线：
cd ../retrieval-pipeline
python main.py
# http://localhost:4242

# 回到本项目目录（或新开一个终端）：
cd ../contextual-retrieval

python index_local_laws_contextual.py
python index_local_laws_contextual.py --no-contextual

python main.py
python main.py --query "宪法第一条是什么" --mode agentic
python main.py --query "宪法第一条是什么" --mode compare
```

### 上下文生成流程

向 LLM 提供全文（或周边）+ 目标块，请求 2–3 句定位上下文。提示模板见 English 节。

<a id="learning-3"></a>

## 判断背景信息帮了哪道题

先从[正式运行的逐题记录](validation/runs/20260729T205807Z-3_10-35531780/evidence.json)里找“全国人民代表大会常务委员会有哪些职权？”。标注为答案来源的 `宪法_chunk_10` 从“（四）解释法律”开始，截在职权清单中途。生成的前缀把“全国人民代表大会常务委员会职权及工作机制”补到了块前。对照 `chunks` 中的原文和前缀，可以看到新增文字补出了谁的职权；具体有哪些职权，仍要读原文。

这个前缀有没有帮读者找到材料，取决于他们能看到几条结果。查看 `results` 中这道题的 `rank`：BM25 将目标块从第 16 名提到第 12 名，只展示前五条时仍然找不到。混合检索将它从第 6 名提到第 5 名，恰好跨过展示边界。这一题就解释了为什么混合检索的 recall@5 从 14/15 变成 15/15：每题只有一个标注目标块，有一题新进入前五即可。

再逐题核对同一种检索方法加前缀前后的名次。在这 15 题中，BM25 有 5 题提前，稠密检索有 1 题提前，混合检索有 3 题提前，其余持平，没有目标块跌到更靠后的位置。这只能说明这批查询中观察到了哪些变化；如果换一批问题，仍需逐题核对，特别留意相似前缀是否把其他块推到了目标块前面。

下方比较使用已有数据；它不能代表重新生成前缀的成本。需要评估完整流程时，还要计入前缀生成、重新索引和存储开销，并防止前缀包含测试问题的答案。

### 命中目标块以后，材料够用了吗？

把 `q08` 的两份混合检索结果并排看。加前缀前，`宪法_chunk_9` 已排在第二。读它的末尾，可以找到第六十七条的标题和第（一）至（四）项职权。即便评分记为漏检，读者手里也已经有了一部分材料。

加前缀后，第一个结果是 `宪法_chunk_9`，第五个是标注的 `宪法_chunk_10`。后一块从第（四）项接起，一直列到第（二十二）项。现在两块合起来才覆盖完整清单，整理答案时还要把重叠的第（四）项只算一次。可以据此检查自己的检索系统：如果任务要求列全，除了核对标注块的排名，还应逐项对照返回的原文。

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-10**: Anthropic-style contextual prefixes before indexing; offline BM25 recall@k compare.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-10**：索引前为分块生成上下文前缀；离线 BM25 recall@k 对比。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

<a id="learning-5"></a>

## 排错与参考

### 参考与许可

[Anthropic 博客](https://www.anthropic.com/engineering/contextual-retrieval) · 教学项目。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

Chat LLM falls back to OpenRouter when primary keys are missing and `OPENROUTER_API_KEY` is set. See `env.example`. Related: [`../contextual-retrieval-for-user-memory/`](../contextual-retrieval-for-user-memory/) (Exp. 3-11).

## English

### Canonical live campaign

`python campaign.py` regenerates every prefix live from the full source
document plus its target chunk, then compares the same 15 labeled queries over
plain/contextual BM25, dense Qwen3 embeddings, and RRF hybrid indexes. It records
recall@1/3/5, MRR, model revision, index-time usage/cost assumptions, source
hashes, and raw ARK receipts in `validation/runs/<run-id>/`; the canonical
pointer is `validation/latest.json`. `compare_retrieval.py` remains the small
offline demonstration and is not accepted as the canonical live result.

### Overview

Educational implementation of Anthropic’s Contextual Retrieval: prepend chunk-specific context before embedding/indexing to fix the “orphaned chunk” problem.

### Key insight

**Problem:** Traditional RAG loses context when chunking. “The company’s revenue grew by 3%” is meaningless without which company / which period.

**Solution:** Generate short explanatory context per chunk and prepend it before indexing so BM25 and embeddings keep identity signals.

### Core offline experiment (Experiment 3-10)

`compare_retrieval.py` quantifies the claim **fully offline**: same chunks indexed two ways—plain (raw text only) vs contextual (LLM-generated prefix + text)—then compares `recall@k` on `evaluation/retrieval_eval.json` (15 queries + human gold chunks). **No API or retrieval service** (BM25 + jieba).

```bash
python compare_retrieval.py
python compare_retrieval.py --per-query
python compare_retrieval.py --query "国家主席有哪些职权？" --top-k 5
python compare_retrieval.py --mode plain
python compare_retrieval.py --output result.json
python compare_retrieval.py --help   # Chinese help
```

Real run (22 Constitution / Prosecutor Law chunks, 15 queries, jieba):

```
检索召回对比：无上下文分块  vs.  上下文感知检索（BM25）
====================================================================
方法                  recall@1    recall@3    recall@5
----------------------------------------------------
无上下文 (plain)          60.0%      86.7%      93.3%
有上下文 (ctx)            86.7%      86.7%      93.3%
----------------------------------------------------
提升 (Δpp)             +26.7pp      +0.0pp      +0.0pp
----------------------------------------------------
失败率下降                    67%          0%          0%
```

In this offline example, top-1 recall rises from 60% to 86.7% (a 67% relative decrease in 1−recall@1). The manuscript uses the separate canonical live campaign described at the top of this page. Gain is strongest at recall@1; `--query` shows how the prefix re-ranks the correct section first.

> `--method embedding` / `--method hybrid` need embedding APIs (not offline); the script falls back to BM25 offline results. Full dense + rerank lives in `contextual_tools.py`.  
> Same logic is also in `ContextualChunker.compare_retrieval_methods()`.

### Educational features

1. Watch LLM context generation per chunk  
2. Dual indexing (BM25 + embeddings) benefits from context  
3. Compare with `use_contextual=False`  
4. Metrics and token/cost awareness  

### Architecture

```
Document → Basic Chunking → Context Generation (optional LLM)
  → Enhanced chunks (context+text vs text only)
  → Retrieval pipeline (sparse BM25 + dense embeddings)
  → Hybrid search + reranking
```

### Quick start

```bash
# From the repository root: use the shared Chapter 3 environment
uv sync --locked --python 3.12 --extra ch3

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch3]"

cd chapter3/contextual-retrieval

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# MOONSHOT_API_KEY / ARK_API_KEY / OPENAI_API_KEY / etc.

# Separate terminal for full e2e with pipeline:
cd ../retrieval-pipeline
python main.py
# http://localhost:4242

# Back in this project directory (or a second terminal):
cd ../contextual-retrieval

# Index with contextual enhancement
python index_local_laws_contextual.py
python index_local_laws_contextual.py --no-contextual

# Queries
python main.py
python main.py --query "宪法第一条是什么" --mode agentic
python main.py --query "宪法第一条是什么" --mode compare
```

### Context generation process

1. Provide full document (or surrounding context) to the LLM  
2. Show the specific chunk  
3. Ask for 2–3 sentence situating context  

Template sketch:

```
<document>
[Full document or surrounding context]
</document>

Here is the chunk we want to situate:
<chunk>
[Specific chunk text]
</chunk>

Please give a short, succinct context to situate this chunk within the overall document...
```

### References / license

- [Anthropic Contextual Retrieval](https://www.anthropic.com/engineering/contextual-retrieval)  
- Educational project for learning purposes. Acknowledgments: Anthropic engineering research.

---
