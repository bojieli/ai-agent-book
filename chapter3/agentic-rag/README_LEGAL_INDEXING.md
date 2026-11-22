# 从法律原文建立可核对的检索索引

法律问答需要先找到适用于当前问题的条文。本教程沿“原文 → 片段 → 索引 → 查询结果”检查证据如何进入系统，再讨论检索是否充分。先准备两个能手工回答的问题和对应条文，便于判断返回结果。

## 理解切分与索引

普通索引先按段落边界切分文档，再把片段写入检索流水线。软长度为 1024 字符、硬上限为 2048 字符；软长度用于尽量保留段落，硬上限用于控制过长片段。边界附近的定义与例外条款尤其需要检查。

索引完成只说明数据被接收。要判断索引是否有用，还需检查来源标识、原文完整性和查询结果。对于“该规定适用于谁”这样的问题，只有一个包含关键词的片段通常不够，还应保留适用条件与例外。

## 准备服务和材料

先按[检索流水线教程](../retrieval-pipeline/README.md)启动稠密、稀疏与主流水线服务。当前服务入口位于相应检索目录；本页后部保留的早期英文 `dense_service.py`、`sparse_service.py` 示例不是当前可直接使用的脚本名。

在本实验目录检查 `laws` 的实际位置和分类子目录，例如宪法、民法典、行政法、刑法和诉讼程序法。上下文增强版本还需要配置生成背景的模型凭据，并确认法律目录或符号链接可以读取。

## 从十篇文档开始

脚本默认会清理已有索引。建议使用独立教学实例；以下命令限制为十篇，并保留已有索引。重复导入可能产生重复数据，正式比较应分别准备干净索引。

```bash
python index_local_laws.py --max-docs 10 --no-cleanup
```

先在原文中标出答案，再观察片段是否保留必要上下文。检查导入统计和失败文件，确认没有把“找到文件”误当作“完成索引”。随后用原问题和一种同义改写查询，逐项对照目标条文。

## 配置不同范围与比较条件

| 参数 | 作用与学习时的用法 |
| --- | --- |
| `--pipeline-url` | 指定实际检索流水线地址。 |
| `--max-docs` | 限制处理篇数，先用小样本检查流程。 |
| `--categories` | 只处理指定分类，核对名称与目录是否对应。 |
| `--no-cleanup` | 保留现有索引；重复运行时注意重复数据。 |
| `--verify` | 导入后执行验证查询。 |

```bash
python index_local_laws.py --categories "宪法" "民法典" --max-docs 10 --no-cleanup
```

比较增强与普通切分时，保持文档、问题、检索器和排序设置相同。记录返回文档、排名、来源与生成背景，而不只记录一次答案是否流畅。

## 解释失败并扩大实验

若没有命中，依次检查文档是否导入、切分是否丢失条件、索引是否更新、正确条文是否进入候选，以及排序是否靠后。对于上下文增强，再检查生成背景是否与原文一致。先定位环节，再修改一个条件重跑。

输出中的统计、文档存储与配置细节在下方完整英文说明中继续列出。价格和耗时属于记录时的条件；自己的运行应以实际 token 用量、服务价格和处理文档数量重新计算。

思考：一般规则和例外分别位于相邻条文时，怎样组织片段和查询，才能让读者同时看到两者？

## English

# Legal Document Indexing Script

This script indexes local Chinese legal documents from the `laws` directory into the retrieval pipeline.

## Features

- **Smart Chunking**: Respects paragraph boundaries with configurable soft (1024 chars) and hard limits (2048 chars)
- **Automatic Cleanup**: Cleans existing indexes before processing
- **Category Support**: Process specific legal categories or all documents
- **Progress Tracking**: Real-time progress updates and statistics
- **Verification**: Built-in test queries to verify indexing

## Prerequisites

1. Ensure the retrieval pipeline is running:
   ```bash
   # Terminal 1: Start dense service
   python dense_service.py
   
   # Terminal 2: Start sparse service  
   python sparse_service.py
   
   # Terminal 3: Start main pipeline
   python main.py
   ```

2. The `laws` directory should be present with legal documents organized by category:
   ```
   laws/
   ├── 1-宪法/
   ├── 2-宪法相关法/
   ├── 3-民法典/
   ├── 3-民法商法/
   ├── 4-行政法/
   ├── 5-经济法/
   ├── 6-社会法/
   ├── 7-刑法/
   └── 8-诉讼与非诉讼程序法/
   ```

## Usage

### Basic Usage
```bash
# Index all legal documents
python index_local_laws.py

# Index with verification tests
python index_local_laws.py --verify
```

### Advanced Options
```bash
# Index only first 10 documents
python index_local_laws.py --max-docs 10

# Index specific categories only
python index_local_laws.py --categories "宪法" "民法典" "刑法"

# Use custom pipeline URL
python index_local_laws.py --pipeline-url http://localhost:8080

# Skip cleanup (append to existing index)
python index_local_laws.py --no-cleanup
```

## Chunking Strategy

The script uses intelligent chunking that:
1. Accumulates paragraphs until soft limit (1024 chars) is exceeded
2. Continues adding if next paragraph fits within hard limit (2048 chars)  
3. Cuts at paragraph boundary when possible
4. Force splits oversized paragraphs at hard limit

This approach ensures:
- Legal provisions remain intact when possible
- Context is preserved within chunks
- Search relevance is optimized

## Output Statistics

After indexing, the script displays:
- Processing time
- Number of documents and categories processed
- Total chunks created and indexed
- Average chunks per document
- Processing speed
- Any errors encountered

## Verification

Use the `--verify` flag to run test searches:
```bash
python index_local_laws.py --verify
```

Test queries include:
- 民法典 (Civil Code)
- 合同法 (Contract Law)
- 劳动法 (Labor Law)
- 刑法 (Criminal Law)
- 宪法 (Constitution)

## Document Store

The script maintains a local `document_store.json` file tracking:
- Document metadata
- Number of chunks per document
- Indexing timestamps
- Category information

## Error Handling

- Documents that fail to read are skipped
- Failed chunk indexing is logged but doesn't stop processing
- Statistics track all errors for review
