# Contextual Retrieval System - Educational Implementation

An educational implementation of Anthropic's Contextual Retrieval technique, demonstrating how contextualizing chunks before indexing dramatically improves retrieval accuracy in RAG systems.

## 🌟 Key Insight

**The Problem**: Traditional RAG systems lose context when chunking documents. A chunk saying "The company's revenue grew by 3%" loses meaning without knowing which company or time period.

**The Solution**: Contextual Retrieval prepends chunk-specific explanatory context to each chunk before embedding and indexing, preserving semantic meaning.

## 📊 核心实验：离线量化召回提升（实验 3-11）

上面的 Key Insight 是本项目要验证的核心主张。`compare_retrieval.py` 用一组
可控的对比实验**完全离线**地量化它：把同一批文本块分别以两种方式建 BM25 索引——
无上下文（只索引原始文本）与有上下文（索引 LLM 生成的前缀 + 原始文本）——
再在评测集 `evaluation/retrieval_eval.json`（15 条查询 + 人工标注 gold 文本块）
上比较 `recall@k`（命中率）。**无需任何 API 或检索服务**（BM25 + jieba 分词）。

```bash
# 跑完整对比表（默认语料 document_store.json，默认评测集）
python compare_retrieval.py

# 查看每条查询的命中排名明细
python compare_retrieval.py --per-query

# 临时单条查询：并排看无上下文 / 有上下文的 Top-K 结果
python compare_retrieval.py --query "国家主席有哪些职权？" --top-k 5

# 只看无上下文基线 / 另存机器可读结果
python compare_retrieval.py --mode plain
python compare_retrieval.py --output result.json

# 中文 --help
python compare_retrieval.py --help
```

真实运行输出（22 个《宪法》《检察官法》文本块，15 条查询，jieba 分词）：

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

结论与书中一致：为文本块补上上下文前缀显著提升 top-1 召回（60% → 86.7%，
失败率 1−recall@1 下降 67%），前缀为 BM25 注入了“身份标签”式的可匹配关键词。
这一提升在 recall@1 上最明显；`--query` 模式可直观看到前缀如何把“正确所属章节”
的文本块重新排到前面。

> `--method embedding` / `--method hybrid`（上下文向量嵌入 + RRF 融合）需要
> 调用 embedding API，无法离线运行；脚本会给出提示并回退到 BM25 离线结果。
> 稠密检索 + 重排序的完整实现见 `contextual_tools.py`。

同一对比逻辑也内建在 `ContextualChunker.compare_retrieval_methods()` 中（书中
`compare_retrieval_methods` 功能），可对任意一组 `ContextualChunk` 直接做并排检索对比。

## 📚 Educational Features

This implementation includes extensive logging and comparison capabilities to understand:

1. **How Context Generation Works**: Watch the LLM generate context for each chunk
2. **Dual Indexing Strategy**: See how both BM25 and embeddings benefit from context
3. **Comparison Mode**: Run with `use_contextual=False` to compare against standard chunking
4. **Performance Metrics**: Track improvements in retrieval accuracy
5. **Cost Analysis**: Understand the token usage and costs

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Document Input                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Basic Chunking                 │
│   (Respects paragraph boundaries)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Context Generation (Optional)       │
│         Using LLM API                   │
│   (Enabled with use_contextual=True)   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Enhanced Chunks                    │
│  • Contextual: Context + Original Text  │
│  • Standard: Original Text Only         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Retrieval Pipeline Indexing        │
│   • Sparse Index (BM25)                 │
│   • Dense Index (Embeddings)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Hybrid Search with Reranking         │
│   Combines BM25 + Embedding scores      │
│   Cross-encoder reranking for accuracy  │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env

# Edit .env and add your API keys:
# - MOONSHOT_API_KEY for Kimi
# - ARK_API_KEY for Doubao
# - OPENAI_API_KEY for OpenAI
# - etc.
```

### 3. Start the Retrieval Pipeline

```bash
# In a separate terminal, start the retrieval pipeline server
cd ../retrieval-pipeline
python main.py
# Server will run on http://localhost:4242
```

### 4. Index Documents

```bash
# Index Chinese law documents with contextual enhancement
python index_local_laws_contextual.py

# Or index without contextual enhancement for comparison
python index_local_laws_contextual.py --no-contextual
```

### 5. Run Queries

```bash
# Interactive mode with contextual retrieval
python main.py

# Query with specific mode
python main.py --query "宪法第一条是什么" --mode agentic

# Compare agentic vs non-agentic modes
python main.py --query "宪法第一条是什么" --mode compare
```

## Context Generation Process

The system generates context for each chunk by:

1. **Providing the full document** (or surrounding context) to the LLM
2. **Showing the specific chunk** to be contextualized
3. **Asking for concise context** (2-3 sentences) that situates the chunk

Example prompt template:
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

## 📚 References

- [Anthropic's Contextual Retrieval Blog Post](https://www.anthropic.com/engineering/contextual-retrieval)

## 🤝 Contributing

This is an educational implementation. Contributions welcome for:
- Additional chunking strategies
- Alternative context generation prompts
- Performance optimizations
- Evaluation metrics
- Visualization tools

## 📝 License

Educational project for learning purposes.

## 🙏 Acknowledgments

Based on research by Anthropic's engineering team on improving RAG retrieval accuracy through contextual enhancement.

## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.
