# Sparse Vector Search Engine (BM25) / 稀疏向量搜索引擎（BM25）

## 实验 3-5：怎样从两个查询词的贡献算出 BM25 总分？

搜索 `model distillation`，排在前两位的文档都包含这两个词，为什么第一篇能得 3.1216 分，第二篇只有 2.2197 分？你可以用本实验的 10 篇英文短文重新建立索引，从每个词在原文里出现了几次，一直算到最后的排名。正文里的中文手算题使用另一组假设数据：“模型蒸馏”在 `doc_1` 中的两项贡献约为 1.52 和 2.15，总分约为 3.67。文档编号只在各自的语料中有意义。

正式运行还用四篇短文单独核验了计算公式，并用英文语料检查检索质量。手算采用原始对数 IDF，评分实现给 IDF 设置了 1e-6 的下限。在这组有标注的查询中，四条精确关键词查询的平均 recall@5 为 1.0；同义词查询 `cat` 的 recall@5 为 0.0。下文的评估命令会列出每一条查询应当找到和实际找到的文档。

运行索引：[validation/latest.json](validation/latest.json)；结果与请求记录：[20260729T183232Z-3_5-f9f70b37](validation/runs/20260729T183232Z-3_5-f9f70b37/)。


[English](#english)

[一个查询词贡献多少分](#learning-0) · [准备 BM25 示例语料](#learning-1) · [逐词复算检索得分](#learning-2) · [解释精确词和同义词的差异](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 一个查询词贡献多少分

查一个少见的产品型号时，倒排索引可以直接告诉你哪些文档提到了这个型号。如果还有好几篇候选，才需要比较得分。BM25 会看这个词在每篇候选中出现了几次、在整个语料中有多常见，以及文档有多长。下面的命令行工具可以展开每一步；也可以启动服务，在网页上查看倒排表和评分日志。

### 功能特性

- **完整 BM25 实现**
- **高级分词**：数字、编码、技术术语、大小写混合
- **倒排索引**
- **HTTP API**（FastAPI）
- **交互式 Web UI**
- **教学日志**
- **索引结构可视化 API**
- **内存存储**（教学简化）

#### 分词能力

- **数字**：`404`、`3.14`、`2.0.1`
- **编码**：`XK9-2B4-7Q1`、`API_KEY_123`
- **技术术语**：`C++`、`.NET`、`Node.js`
- **大小写混合**：`JavaScript`、`PyTorch`、`iPhone`
- **邮箱**：`user@example.com`
- **十六进制**：`#FF5733`、`0x1234`
- **缩写**：`API`、`HTTP`、`NASA`
- **字母数字**：`Python3`、`ES6`、`HTML5`

### 架构

1. **TextProcessor**：分词  
2. **InvertedIndex**：词频 / 文档频率  
3. **BM25**：相关性打分  
4. **SparseSearchEngine**：总控  
5. **HTTP Server**：FastAPI  

BM25 使用 TF、IDF 与文档长度归一化。关键参数：`k1`（默认 1.5）、`b`（默认 0.75）。

### 教学特性

日志覆盖分词、TF、IDF、逐词 BM25、查询处理、候选文档。`/index/structure` 返回倒排映射、文档统计、BM25 参数、全局词频分布。检索结果含匹配词、文档长度、词频与分项得分。

<a id="learning-1"></a>

## 准备 BM25 示例语料

本地 CLI 自带十篇英文短文。先用 `model distillation` 查询，再加 `--explain` 查看每个词贡献的分数。书中的中文手算题用了另一份语料，文档编号也随之改变。

### 安装

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

cd chapter3/sparse-embedding

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt
```

`cli.py` 只依赖 Python 标准库，无需第三方包即可离线运行；`server.py` / `demo.py` 需要统一 `ch3` 环境或兼容 `requirements.txt` 路径提供的 FastAPI 等依赖。

<a id="learning-2"></a>

## 逐词复算检索得分

在本实验目录运行：

```bash
python cli.py -q "model distillation" --explain
```

先读第一条结果 `doc_3`。原文从 “Model distillation compresses a large teacher model” 开始，后面又提到 “a smaller student model”。数一数，`model` 出现了三次，`distillation` 只有一次。两个词在整套语料中都只出现在两篇文档里，因此 IDF 相同，都是 $\ln(8.5/2.5)\approx 1.2238$。

分词并去掉停用词之后，这篇文档长 13 词，语料平均长 11.4 词。把默认参数代入正文的 BM25 公式，分母里和文档长度有关的那一项是 $1.5(1-0.75+0.75\times13/11.4)\approx 1.658$。于是 `model` 贡献约 $1.2238\times(3\times2.5)/(3+1.658)\approx 1.9705$ 分；同一篇文档中的 `distillation` 只出现一次，贡献约 1.1511 分。两项相加就是第一篇的总分。复算时保留中间值的精度，最后再取四位小数。

再试一次只查 `distillation`。它在两篇文档中都只出现一次，默认设置下，13 词的 `doc_3` 得 1.1511 分，14 词的 `doc_4` 得 1.1099 分。如果分差来自文档长度，关闭长度校正后应该得到什么结果？

```bash
python cli.py -q distillation --explain
python cli.py -q distillation --explain -b 0
```

第二次运行，两篇都得到 1.2238 分。图 3-8 中固定词频、单独改变文档长度的那一行，就可以用这两篇示例文档来检验。

### 命令行工具 cli.py（实验 3-5，推荐入口）

完全离线：在内置 10 篇小语料上跑 BM25、在英文示例中逐词展开 IDF、TF 和 BM25 贡献，并在标注集上算 recall/precision/MRR。参数均有中文 `--help`。

```bash
python cli.py --help                          # 查看全部参数（中文）
python cli.py                                 # 默认演示：查询 "model distillation"
python cli.py -q "model distillation" --explain   # 逐词展示 TF/IDF/BM25 贡献
python cli.py --eval                          # recall@k / precision@k / MRR
python cli.py -q "cat"                        # 观察同义词短板（kitten/feline 漏召回）
python cli.py --corpus my.json -q "查询" -o out.json
python cli.py --k1 2.0 -b 0.5 -q "..."
python cli.py --method splade -q "..."        # SPLADE（需预先下载模型）
```

| 参数 | 说明 |
| --- | --- |
| `-q, --query` | 查询字符串（默认 `model distillation`） |
| `-c, --corpus` | 语料（`.json` 数组或 `.jsonl`）；缺省用内置示例 |
| `-m, --method` | `bm25`（默认，离线）或 `splade`（学习型稀疏，需模型） |
| `-k, --top-k` | 返回前 k 条（默认 5） |
| `-o, --output` | 结果 / 指标写入 JSON |
| `--eval` | 在标注集上评测 |
| `--labels` | 自定义标注 `{query: [doc_id,...]}` |
| `--explain` | 逐词 TF / IDF / BM25 |
| `--k1` / `-b` | BM25 参数 |
| `-v, --verbose` | DEBUG 日志 |

#### 检索质量评测（`--eval`）

内置标注覆盖精确关键词、错误码、专有名称与「只有同义表达」的查询。真实输出（k=5）：

```
查询 'model distillation'  recall@5=1.00  precision@5=1.00  RR=1.00
查询 'HTTP 404 error'       recall@5=1.00  precision@5=0.50  RR=1.00
查询 'XK9-2B4-7Q1'          recall@5=1.00  precision@5=1.00  RR=1.00
查询 'BM25 ranking function' recall@5=1.00  precision@5=1.00  RR=1.00
查询 'cat'                  recall@5=0.00  precision@5=0.00  RR=0.00   <- 漏召回(同义词短板)
宏平均  recall@5=0.800  precision@5=0.700  MRR=0.800  漏召回率(1-recall@5)=0.200
```

看第二行：同一次检索，召回率为什么是 1，精确率却只有 0.5？运行 `python cli.py --eval`，可以看到查询 `HTTP 404 error` 实际只返回了两篇文档。`doc_6` 解释 HTTP 404，是唯一标为相关的文档；排第二的 `doc_9` 讲存储控制器故障，因为也写了 `error` 而进入候选集。

标注的一篇相关文档已经找齐，所以召回率是 1/1。两条结果中有一条相关，所以精确率是 1/2。第一条结果就相关，倒数排名（RR）也是 1/1。表头里的 5 是最多取五条：[评分函数](cli.py)用实际返回的条数计算精确率。若另一份评测把空位也计入分母，同一查询就会得到 1/5；比较两个系统之前，要先确认它们怎样处理不足五条的结果。

#### 学习型稀疏检索（`--method splade`）

用掩码语言模型为词项打权，并可为语义相关词项补权。需下载 `naver/splade-cocondenser-ensembledistil`（依赖 `torch`、`transformers`）。离线无权重时会快速给出清晰提示。联网可先 `huggingface-cli download naver/splade-cocondenser-ensembledistil`。

### 服务端用法

```bash
python server.py
```

服务地址：`http://localhost:4241`。Web UI 打开该地址。API 文档：`http://localhost:4241/docs`。

#### API 端点

```bash
POST /index
{
  "text": "Your document text here",
  "metadata": {"title": "Document Title", "category": "Category"}
}

POST /search
{
  "query": "your search query",
  "top_k": 10
}

GET /stats
GET /index/structure
GET /document/{doc_id}
DELETE /index
```

#### 运行演示

```bash
python demo.py
```

演示：清空索引 → 示例文档 → 统计 → 索引结构 → 查询 → 按 ID 取文档。

<a id="learning-3"></a>

## 解释精确词和同义词的差异

再看查询 `cat`。标注把写有 `kitten` 的 `doc_7` 和写有 `feline` 的 `doc_8` 都列为相关，但这两篇都没有词项 `cat`。倒排索引中查不到这个词，候选集为空，调节词频权重或文档长度惩罚都无法把它们排进来。可以分别用 `kitten` 和 `feline` 再搜一次，观察哪一篇重新进入候选集。实验 3-6 会把词面匹配和稠密检索结合起来，给同义表达多一条进入候选集的途径。

### 检查自己的解释

搜索错误码时，关键词检索可能比语义检索更可靠，原因是什么？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-5**: educational BM25 / inverted-index sparse search with offline CLI evaluation.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-5**：从零理解 BM25 与倒排索引，含可离线评测的 CLI。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 项目结构

```
sparse-embedding/
├── bm25_engine.py     # 核心检索引擎
├── cli.py             # 离线 CLI：BM25/SPLADE + 指标
├── server.py          # FastAPI 服务
├── demo.py            # 演示脚本
├── requirements.txt
└── README.md
```

<a id="learning-5"></a>

## 排错与参考

### 局限

仅内存存储；分词较基础（无词形还原）；英文停用词；不支持短语查询 / 同义扩展 / 多线程。

---

## Notes / 说明

- Related next step / 相关后续：[`../retrieval-pipeline/`](../retrieval-pipeline/) hybrid dense+sparse pipeline (Exp. 3-6).  
- 相关后续：[`../retrieval-pipeline/`](../retrieval-pipeline/) 混合稠密+稀疏流水线（实验 3-6）。

## English

### Overview

An educational sparse vector search engine using an inverted index and BM25. It demonstrates core IR concepts with extensive logging and visualization.

### Features

- **Full BM25 implementation**
- **Advanced tokenization**: numbers, codes, technical terms, mixed case
- **Inverted index** for term lookup
- **HTTP API** (FastAPI)
- **Interactive Web UI** for index/search
- **Educational logging** through index and search
- **Index visualization** APIs
- **In-memory storage** (educational simplicity)

#### Tokenization capabilities

- **Numbers**: `404`, `3.14`, `2.0.1`
- **Codes**: `XK9-2B4-7Q1`, `API_KEY_123`
- **Technical terms**: `C++`, `.NET`, `Node.js`
- **Mixed case**: `JavaScript`, `PyTorch`, `iPhone`
- **Email**: `user@example.com`
- **Hex**: `#FF5733`, `0x1234`
- **Acronyms**: `API`, `HTTP`, `NASA`
- **Alphanumeric**: `Python3`, `ES6`, `HTML5`

### Architecture

1. **TextProcessor**: tokenizer for words, numbers, codes, technical terms, mixed case  
2. **InvertedIndex**: term/document frequencies  
3. **BM25**: ranking  
4. **SparseSearchEngine**: orchestration  
5. **HTTP Server**: FastAPI surface  

BM25 uses TF, IDF, and document-length normalization. Key params: `k1` (default 1.5), `b` (default 0.75).

### Installation

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

cd chapter3/sparse-embedding

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt
```

`cli.py` (below) uses only the Python standard library and runs offline with no third-party packages; `server.py` / `demo.py` need the shared `ch3` environment or the compatibility `requirements.txt` path.

### CLI tool `cli.py` (Experiment 3-5, recommended entry)

Fully offline CLI: BM25 on a built-in 10-doc corpus, per-term TF/IDF/BM25 contribution logs (as in the book), and labelled recall/precision/MRR. All flags have Chinese `--help`.

```bash
python cli.py --help                          # all flags (Chinese)
python cli.py                                 # default demo query "model distillation"
python cli.py -q "model distillation" --explain   # per-term TF/IDF/BM25
python cli.py --eval                          # recall@k / precision@k / MRR
python cli.py -q "cat"                        # synonym failure (kitten/feline miss)
python cli.py --corpus my.json -q "查询" -o out.json
python cli.py --k1 2.0 -b 0.5 -q "..."
python cli.py --method splade -q "..."        # SPLADE (needs downloaded model)
```

| Flag | Description |
| --- | --- |
| `-q, --query` | Query string (default `model distillation`) |
| `-c, --corpus` | Corpus (`.json` array or `.jsonl`); default built-in sample |
| `-m, --method` | `bm25` (default, offline) or `splade` (learned sparse; needs model) |
| `-k, --top-k` | Top-k (default 5) |
| `-o, --output` | Write results/metrics JSON |
| `--eval` | Evaluate recall@k / precision@k / MRR on labels |
| `--labels` | Custom labels `{query: [doc_id,...]}` |
| `--explain` | Per-term TF / IDF / BM25 on hits |
| `--k1` / `-b` | BM25 k1 and b |
| `-v, --verbose` | Engine DEBUG logs |

#### Retrieval quality (`--eval`)

Built-in labels cover exact keywords, error codes, proper names, and synonym-only queries. Real `python cli.py --eval` output (k=5):

```
查询 'model distillation'  recall@5=1.00  precision@5=1.00  RR=1.00
查询 'HTTP 404 error'       recall@5=1.00  precision@5=0.50  RR=1.00
查询 'XK9-2B4-7Q1'          recall@5=1.00  precision@5=1.00  RR=1.00
查询 'BM25 ranking function' recall@5=1.00  precision@5=1.00  RR=1.00
查询 'cat'                  recall@5=0.00  precision@5=0.00  RR=0.00   <- 漏召回(同义词短板)
宏平均  recall@5=0.800  precision@5=0.700  MRR=0.800  漏召回率(1-recall@5)=0.200
```

BM25 excels on exact keywords, codes, and names (recall=1.0) but misses synonyms—query `cat` does not hit docs that only say `kitten` / `feline`. That gap motivates hybrid search (Experiment 3-6 `retrieval-pipeline`).

#### Learned sparse (`--method splade`)

SPLADE weights terms with a masked LM and can expand semantically related terms. Needs pretrained `naver/splade-cocondenser-ensembledistil` (`torch`, `transformers`). Offline without weights, the command fails fast with a clear message (BM25 path needs no model). Online: `huggingface-cli download naver/splade-cocondenser-ensembledistil` then run.

### Server usage

```bash
python server.py
```

Server: `http://localhost:4241`. Web UI: open that URL. API docs: `http://localhost:4241/docs`.

#### API endpoints

```bash
POST /index
{
  "text": "Your document text here",
  "metadata": {"title": "Document Title", "category": "Category"}
}

POST /search
{
  "query": "your search query",
  "top_k": 10
}

GET /stats
GET /index/structure
GET /document/{doc_id}
DELETE /index
```

#### Demo

```bash
python demo.py
```

Demo: clear index → sample CS docs → stats → index structure → sample queries → document get.

### Educational features

Logging covers tokenization, TF, IDF, per-term BM25, query processing, candidates. `/index/structure` returns inverted map, doc stats, BM25 params, global TF distribution. Search results include matched terms, doc length, TFs, per-term score contributions.

### Project structure

```
sparse-embedding/
├── bm25_engine.py     # Core engine
├── cli.py             # Offline CLI: BM25/SPLADE + metrics
├── server.py          # FastAPI server
├── demo.py            # Demo script
├── requirements.txt
└── README.md
```

### Limitations

In-memory only; basic tokenization (no lemmatization); English stopwords; no phrase queries / synonyms / multi-thread.

---
