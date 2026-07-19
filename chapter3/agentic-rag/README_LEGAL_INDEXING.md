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
