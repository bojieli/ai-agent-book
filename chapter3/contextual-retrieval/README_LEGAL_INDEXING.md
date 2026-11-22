# 从法律原文建立可核对的检索索引

法律问答需要先找到适用于当前问题的条文。本教程沿“原文 → 片段 → 索引 → 查询结果”检查证据如何进入系统，再讨论检索是否充分。先准备两个能手工回答的问题和对应条文，便于判断返回结果。

## 理解切分与索引

上下文增强先用模型为片段生成背景，再把背景放到片段前面用于索引。背景可能补足法规名称或适用范围，也可能引入错误，因此应保留原片段并逐项核对。生成背景会消耗模型额度；缓存可以减少重复内容的生成，但不能证明检索质量提高。

索引完成只说明数据被接收。要判断索引是否有用，还需检查来源标识、原文完整性和查询结果。对于“该规定适用于谁”这样的问题，只有一个包含关键词的片段通常不够，还应保留适用条件与例外。

## 准备服务和材料

先按[检索流水线教程](../retrieval-pipeline/README.md)启动稠密、稀疏与主流水线服务。当前服务入口位于相应检索目录；本页后部保留的早期英文 `dense_service.py`、`sparse_service.py` 示例不是当前可直接使用的脚本名。

在本实验目录检查 `laws` 的实际位置和分类子目录，例如宪法、民法典、行政法、刑法和诉讼程序法。上下文增强版本还需要配置生成背景的模型凭据，并确认法律目录或符号链接可以读取。

## 从十篇文档开始

脚本默认会清理已有索引。建议使用独立教学实例；以下命令限制为十篇，并保留已有索引。重复导入可能产生重复数据，正式比较应分别准备干净索引。

```bash
python index_local_laws_contextual.py --max-docs 10 --no-cleanup
```

先在原文中标出答案，再观察片段是否保留必要上下文。检查导入统计和失败文件，确认没有把“找到文件”误当作“完成索引”。随后用原问题和一种同义改写查询，逐项对照目标条文。

## 配置不同范围与比较条件

| 参数 | 作用与学习时的用法 |
| --- | --- |
| `--pipeline-url` | 指定实际检索流水线地址。 |
| `--max-docs` | 限制处理篇数，先用小样本检查流程。 |
| `--categories` | 只处理指定分类，核对名称与目录是否对应。 |
| `--no-cleanup` | 保留现有索引；重复运行时注意重复数据。 |
| `--no-contextual` | 关闭上下文增强，用作普通切分对照。 |
| `--compare` | 索引后执行比较。 |
| `--llm-provider` / `--llm-model` | 选择生成背景的服务与模型。 |
| `--batch-size` | 每批索引的数量。 |

```bash
python index_local_laws_contextual.py --categories "宪法" "民法典" --max-docs 10 --no-cleanup
```

比较增强与普通切分时，保持文档、问题、检索器和排序设置相同。记录返回文档、排名、来源与生成背景，而不只记录一次答案是否流畅。

## 解释失败并扩大实验

若没有命中，依次检查文档是否导入、切分是否丢失条件、索引是否更新、正确条文是否进入候选，以及排序是否靠后。对于上下文增强，再检查生成背景是否与原文一致。先定位环节，再修改一个条件重跑。

输出中的统计、文档存储与配置细节在下方完整英文说明中继续列出。价格和耗时属于记录时的条件；自己的运行应以实际 token 用量、服务价格和处理文档数量重新计算。

思考：一般规则和例外分别位于相邻条文时，怎样组织片段和查询，才能让读者同时看到两者？

## English

# Contextual Legal Document Indexing

This script implements Anthropic's Contextual Retrieval approach for indexing Chinese legal documents.

## Key Innovation: Contextual Retrieval

Unlike traditional RAG that loses context when chunking, this script:
1. Generates contextual descriptions for each chunk using LLM
2. Prepends context to chunks before indexing
3. Significantly improves retrieval accuracy

## Features

- **Contextual Enhancement**: Uses LLM to generate chunk-specific context
- **Smart Chunking**: Paragraph-aware boundaries (soft: 1024, hard: 2048 chars)
- **Comparison Mode**: Run with/without context for performance comparison
- **Cache Optimization**: Caches context for similar chunks to reduce API costs
- **Detailed Statistics**: Token usage, generation time, and cost estimation

## Prerequisites

1. Set up your LLM API key:
   ```bash
   export MOONSHOT_API_KEY="your_api_key"  # Default: Kimi
   # Or use other providers:
   export OPENAI_API_KEY="your_api_key"
   export SILICONFLOW_API_KEY="your_api_key"
   ```

2. Ensure retrieval pipeline is running:
   ```bash
   # Terminal 1: Dense service
   python dense_service.py
   
   # Terminal 2: Sparse service
   python sparse_service.py
   
   # Terminal 3: Main pipeline
   python main.py
   ```

3. The `laws` directory should be linked/present (automatically created as symlink to agentic-rag/laws)

## Usage

### Basic Contextual Indexing
```bash
# Index with contextual enhancement (default)
python index_local_laws_contextual.py
```

### Advanced Options
```bash
# Process limited documents
python index_local_laws_contextual.py --max-docs 10

# Process specific categories
python index_local_laws_contextual.py --categories "宪法" "民法典"

# Use different LLM provider
python index_local_laws_contextual.py --llm-provider openai --llm-model gpt-5.6-luna

# Custom batch size for indexing
python index_local_laws_contextual.py --batch-size 20

# Skip cleanup
python index_local_laws_contextual.py --no-cleanup
```

## Cost Considerations

Context generation requires LLM API calls:
- ~150 tokens per chunk for context generation
- Costs vary by provider (OpenAI: ~$0.03/1K tokens, Others: ~$0.01/1K tokens)
- Cache reduces costs for duplicate content

Estimate for 288 legal documents:
- ~3000-5000 chunks total
- ~450K-750K tokens
- Cost: $5-15 depending on provider

## Document Store

Maintains `document_store.json` with:
- Document metadata
- Chunk statistics
- Context token usage
- Generation metrics
- Indexing timestamps
