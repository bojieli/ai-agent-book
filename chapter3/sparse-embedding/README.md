# Educational Sparse Vector Search Engine

An educational implementation of a sparse vector search engine using inverted index and BM25 algorithm. This project demonstrates the fundamental concepts of information retrieval with extensive logging and visualization features for learning purposes.

## Features

- **Full BM25 Implementation**: Complete implementation of the BM25 ranking algorithm
- **Advanced Tokenization**: Comprehensive tokenizer handling numbers, codes, technical terms, and mixed case
- **Inverted Index**: Efficient inverted index data structure for term lookup
- **HTTP API**: RESTful API built with FastAPI
- **Interactive Web UI**: Browser-based interface for indexing and searching
- **Extensive Logging**: Detailed educational logging throughout indexing and search operations
- **Index Visualization**: APIs to inspect the internal structure of the index
- **In-Memory Storage**: Simple in-memory storage for educational purposes

### Tokenization Capabilities

The TextProcessor now provides comprehensive tokenization for real-world text:

- **Numbers**: `404`, `3.14`, `2.0.1`
- **Codes**: `XK9-2B4-7Q1`, `API_KEY_123`
- **Technical Terms**: `C++`, `.NET`, `Node.js`
- **Mixed Case**: `JavaScript`, `PyTorch`, `iPhone`
- **Email**: `user@example.com`
- **Hex Codes**: `#FF5733`, `0x1234`
- **Acronyms**: `API`, `HTTP`, `NASA`
- **Alphanumeric**: `Python3`, `ES6`, `HTML5`

## Architecture

### Core Components

1. **TextProcessor**: Advanced tokenizer handling words, numbers, codes, technical terms, and mixed case
2. **InvertedIndex**: Maintains the inverted index structure with term frequencies and document frequencies
3. **BM25**: Implements the BM25 ranking algorithm for relevance scoring
4. **SparseSearchEngine**: Main engine coordinating all components
5. **HTTP Server**: FastAPI-based server exposing the search engine functionality

### BM25 Algorithm

BM25 (Best Matching 25) is a probabilistic ranking function that scores documents based on query terms. The algorithm uses:

- **Term Frequency (TF)**: How often a term appears in a document
- **Inverse Document Frequency (IDF)**: How rare or common a term is across all documents
- **Document Length Normalization**: Adjusts scores based on document length

Key parameters:
- `k1` (default 1.5): Controls term frequency saturation
- `b` (default 0.75): Controls length normalization

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

`cli.py`（下节的命令行工具）只依赖 Python 标准库，无需安装任何第三方包即可离线运行；`server.py` / `demo.py` 才需要上面的 FastAPI 等依赖。

## 命令行工具 cli.py（实验 3-5，推荐入口）

`cli.py` 提供一个完全离线的命令行入口：在一个内置的 10 篇小型语料上运行 BM25 稀疏检索、复现书中“逐词 IDF/TF/BM25 贡献”的日志，并在带标注的评测集上计算 recall/precision/MRR。所有参数都有中文 `--help`。

```bash
python cli.py --help                          # 查看全部参数（中文）
python cli.py                                 # 默认演示：查询 "model distillation"
python cli.py -q "model distillation" --explain   # 逐词展示 TF/IDF/BM25 贡献（对应书中日志）
python cli.py --eval                          # 在标注集上计算 recall@k / precision@k / MRR
python cli.py -q "cat"                        # 观察 BM25 读不懂同义词的短板（kitten/feline 漏召回）
python cli.py --corpus my.json -q "查询" -o out.json   # 自定义语料 + 结果落盘
python cli.py --k1 2.0 -b 0.5 -q "..."        # 调 BM25 参数 k1 / b
python cli.py --method splade -q "..."        # 学习型稀疏检索 SPLADE（需预先下载模型）
```

主要参数：

| 参数 | 说明 |
| --- | --- |
| `-q, --query` | 查询字符串（默认 `model distillation`） |
| `-c, --corpus` | 语料文件（`.json` 文档数组或 `.jsonl` 每行一篇）；缺省用内置示例语料 |
| `-m, --method` | `bm25`（默认，离线）或 `splade`（学习型稀疏，需下载模型） |
| `-k, --top-k` | 返回前 k 条（默认 5） |
| `-o, --output` | 把结果 / 评测指标写入 JSON 文件 |
| `--eval` | 在标注集上评测 recall@k / precision@k / MRR |
| `--labels` | 自定义评测标注 `{query: [相关doc_id,...]}` |
| `--explain` | 对命中文档逐词展示 TF / IDF / BM25 贡献 |
| `--k1` / `-b` | BM25 词频饱和参数 k1、文档长度归一化参数 b |
| `-v, --verbose` | 打开引擎 DEBUG 日志（分词、倒排索引构建、打分全过程） |

### 检索质量评测（--eval）

内置标注集覆盖精确关键词、错误码、专有名称与“只有同义表达”的查询。`python cli.py --eval` 的真实输出（k=5）：

```
查询 'model distillation'  recall@5=1.00  precision@5=1.00  RR=1.00
查询 'HTTP 404 error'       recall@5=1.00  precision@5=0.50  RR=1.00
查询 'XK9-2B4-7Q1'          recall@5=1.00  precision@5=1.00  RR=1.00
查询 'BM25 ranking function' recall@5=1.00  precision@5=1.00  RR=1.00
查询 'cat'                  recall@5=0.00  precision@5=0.00  RR=0.00   <- 漏召回(同义词短板)
宏平均  recall@5=0.800  precision@5=0.700  MRR=0.800  漏召回率(1-recall@5)=0.200
```

结果直观印证了书中的结论：BM25 在精确关键词、错误码、专有名称上表现极佳（recall=1.0），但读不懂同义词——查询 `cat` 无法命中只写了 `kitten` / `feline` 的文档（recall=0）。这一长一短正是引入混合检索（见实验 3-6 `retrieval-pipeline`）的动机。

### 学习型稀疏检索（--method splade）

`--method splade` 对应书中提到的学习型稀疏检索（SPLADE）：用掩码语言模型为每个词项打权重，并能为原文未出现但语义相关的词项补权重（术语扩展）。它需要下载预训练模型 `naver/splade-cocondenser-ensembledistil`（依赖 `torch`、`transformers`）。离线环境下无法下载权重时，命令会快速给出清晰提示（并说明 BM25 路径无需任何模型即可离线运行），不会卡在网络下载上。联网环境可先执行 `huggingface-cli download naver/splade-cocondenser-ensembledistil` 缓存模型后再运行。

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:4241`

### Web Interface

Open your browser and navigate to `http://localhost:4241` to access the interactive web UI.

### API Endpoints

#### Index a Document
```bash
POST /index
{
  "text": "Your document text here",
  "metadata": {"title": "Document Title", "category": "Category"}
}
```

#### Search Documents
```bash
POST /search
{
  "query": "your search query",
  "top_k": 10
}
```

#### Get Statistics
```bash
GET /stats
```

#### Get Index Structure
```bash
GET /index/structure
```

#### Retrieve Document by ID
```bash
GET /document/{doc_id}
```

#### Clear Index
```bash
DELETE /index
```

### Running the Demo

```bash
python demo.py
```

The demo script will:
1. Clear any existing index
2. Index sample documents about programming and computer science
3. Display index statistics
4. Show the internal index structure
5. Perform various search queries
6. Demonstrate document retrieval

## Educational Features

### Extensive Logging

The system provides detailed logging at every step:
- Document tokenization process
- Term frequency calculations
- IDF score computations
- BM25 scoring for each term
- Query processing steps
- Candidate document identification

### Index Visualization

The `/index/structure` endpoint returns:
- Inverted index mapping (terms to documents)
- Document statistics (length, unique terms, top terms)
- BM25 parameters
- Global term frequency distribution

### Debug Information in Search Results

Each search result includes debug information:
- Matched query terms
- Document length
- Term frequencies for query terms
- Individual term contributions to the final score

## Example Output

### Indexing Log
```
2024-01-15 10:30:45 - Indexing document with ID 0
2024-01-15 10:30:45 - Document text: Python is a high-level programming...
2024-01-15 10:30:45 - Tokenizing text of length 142
2024-01-15 10:30:45 - Found 23 raw tokens
2024-01-15 10:30:45 - After removing stop words: 15 tokens
2024-01-15 10:30:45 - Document 0: 15 tokens, 12 unique terms
2024-01-15 10:30:45 - Document 0 indexed successfully
```

### Search Log
```
2024-01-15 10:31:20 - Searching for: 'machine learning algorithms'
2024-01-15 10:31:20 - Query terms after processing: ['machine', 'learning', 'algorithms']
2024-01-15 10:31:20 - Term 'machine' appears in 2 documents
2024-01-15 10:31:20 - Term 'learning' appears in 3 documents
2024-01-15 10:31:20 - Term 'algorithms' appears in 1 document
2024-01-15 10:31:20 - Found 4 candidate documents
2024-01-15 10:31:20 - IDF for 'machine': N=10, df=2, idf=1.7918
2024-01-15 10:31:20 - Term 'machine' in doc 1: tf=2, dl=35, score=3.2451
2024-01-15 10:31:20 - Document 1 total score: 7.8923
2024-01-15 10:31:20 - Returning top 3 results
```

## API Documentation

Interactive API documentation is available at `http://localhost:4241/docs` when the server is running.

## Project Structure

```
sparse-embedding/
├── bm25_engine.py     # Core search engine implementation
├── cli.py             # Offline argparse CLI: BM25/SPLADE search + recall/precision eval
├── server.py          # FastAPI HTTP server
├── demo.py            # Demonstration script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Learning Resources

This implementation demonstrates:
- How inverted indices work in search engines
- The mathematics behind BM25 ranking
- Term frequency and document frequency concepts
- The importance of text preprocessing
- How sparse vectors represent documents
- RESTful API design for search systems

## Limitations

This is an educational implementation with some limitations:
- In-memory storage (not persistent)
- Basic tokenization (could be improved with lemmatization)
- English-only stop words
- No support for phrase queries
- No query expansion or synonyms
- Single-threaded processing

## Further Improvements

Potential enhancements for learning:
- Add persistence with a database
- Implement more advanced text processing (stemming, lemmatization)
- Add support for phrase queries
- Implement query expansion
- Add multi-language support
- Implement index compression techniques
- Add support for field-specific searching
- Implement more ranking algorithms (TF-IDF, Okapi BM25+)
