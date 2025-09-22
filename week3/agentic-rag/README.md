# Agentic RAG System

An educational implementation of an Agentic Retrieval-Augmented Generation (RAG) system with ReAct pattern, supporting multiple LLM providers and knowledge base backends.

## Features

- **Agentic RAG with ReAct Pattern**: Uses reasoning and tool-calling to iteratively search and retrieve information
- **Non-Agentic RAG Mode**: Simple retrieval + LLM response for comparison
- **Multiple LLM Provider Support**: 
  - Kimi/Moonshot
  - Doubao
  - SiliconFlow
  - OpenAI
  - OpenRouter
  - Groq
  - Together AI
  - DeepSeek
- **Flexible Knowledge Base**:
  - Local retrieval pipeline (week3/retrieval-pipeline)
  - Dify knowledge base API
  - RAPTOR tree-based index (week3/structured-index)
  - GraphRAG knowledge graph index (week3/structured-index)
- **Document Chunking**: Configurable chunking with paragraph boundary respect
- **Evaluation Framework**: Comprehensive evaluation with Chinese legal dataset
- **Conversation History**: Support for follow-up questions

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables in `.env` file:

```bash
# LLM API Keys (set the one you're using)
MOONSHOT_API_KEY=your_kimi_api_key
ARK_API_KEY=your_doubao_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key
OPENAI_API_KEY=your_openai_api_key

# Knowledge Base Configuration
KB_TYPE=local  # Options: "local", "dify", "raptor", "graphrag"
DIFY_API_KEY=your_dify_api_key  # if using Dify
DIFY_DATASET_ID=your_dataset_id  # optional

# Structured Index Configuration (for RAPTOR/GraphRAG)
RAPTOR_BASE_URL=http://localhost:8080  # RAPTOR API endpoint
GRAPHRAG_BASE_URL=http://localhost:8080  # GraphRAG API endpoint

# LLM Configuration
LLM_PROVIDER=kimi  # default provider
LLM_MODEL=kimi-k2-0905-preview  # optional, uses provider defaults
```

## Usage

### 1. Index Documents

First, index your documents into the knowledge base:

```bash
# Index a single file
python chunking.py path/to/document.txt

# Index a directory
python chunking.py path/to/documents/ --extensions .txt .md

# Custom chunk size
python chunking.py documents/ --chunk-size 2048 --max-chunk-size 4096
```

For the evaluation dataset, first generate and index the legal documents:

```bash
# Generate legal documents
cd evaluation
python dataset_builder.py

# Index them
cd ..
python chunking.py evaluation/legal_documents.json
```

### 2. Start Knowledge Base Backend

#### For Local Retrieval Pipeline:
```bash
cd ../retrieval-pipeline
python main.py
```

#### For RAPTOR or GraphRAG:
```bash
cd ../structured-index

# Build index first (example with Intel manual)
python main.py build path/to/intel_manual.pdf --type both

# Start API server
python main.py serve
```

### 3. Run the Agentic RAG System

#### Interactive Mode (Default)

```bash
# Agentic mode
python main.py

# Non-agentic mode  
python main.py --mode non-agentic

# Compare both modes
python main.py --mode compare --query "故意杀人罪判几年？"
```

#### Single Query

```bash
python main.py --query "盗窃罪的立案标准是什么？" --mode agentic
```

#### Batch Processing

```bash
# Create a file with queries (one per line)
echo "故意杀人罪判几年？
盗窃罪的立案标准是什么？
醉酒驾驶如何处罚？" > queries.txt

# Run batch
python main.py --batch queries.txt --output results.json
```

#### With Different Providers

```bash
python main.py --provider openai --model gpt-4o-2024-11-20
python main.py --provider doubao --model doubao-seed-1-6-thinking-250715
```

#### With Structured Index Backends

```bash
# Using RAPTOR tree-based index
KB_TYPE=raptor python main.py --query "What are Intel x86 registers?"

# Using GraphRAG knowledge graph
KB_TYPE=graphrag python main.py --query "Show relationships between CPU instructions"

# Test structured backends
python test_structured_backends.py
```

### 4. Run Evaluation

```bash
# Generate evaluation dataset and documents
cd evaluation
python dataset_builder.py

# Run evaluation
python evaluate.py --dataset legal_qa_dataset.json --output results

# With specific configuration
python evaluate.py --provider kimi --kb-type local
```

## Project Structure

```
agentic-rag/
├── config.py              # Configuration classes
├── agent.py               # Main AgenticRAG implementation
├── tools.py               # Knowledge base tools (with RAPTOR/GraphRAG support)
├── chunking.py            # Document chunking and indexing
├── main.py                # Main entry point
├── test_structured_backends.py  # Test RAPTOR/GraphRAG integration
├── requirements.txt       # Dependencies
├── README.md              # This file
├── document_store.json    # Local document storage
└── evaluation/
    ├── dataset_builder.py # Build evaluation dataset
    ├── evaluate.py        # Evaluation framework
    ├── legal_qa_dataset.json    # Evaluation questions
    ├── legal_documents.json     # Legal knowledge base
    └── results/           # Evaluation results
```

## How It Works

### Agentic RAG Mode

1. **ReAct Pattern**: The agent reasons about what information is needed
2. **Tool Calling**: Uses `knowledge_base_search` to find relevant chunks
3. **Iterative Refinement**: May perform multiple searches with different queries
4. **Document Retrieval**: Can fetch full documents with `get_document` for context
5. **Answer Synthesis**: Combines retrieved information to answer the question
6. **Citations**: Always includes source citations

### Knowledge Base Backends

#### RAPTOR (Tree-Based Index)
- **Hierarchical Structure**: Creates multi-level tree with recursive summarization
- **Level-Aware Search**: Searches across different abstraction levels
- **Clustering**: Groups similar content using Gaussian Mixture Models
- **Best For**: Long technical documents with hierarchical information

#### GraphRAG (Knowledge Graph)
- **Entity Extraction**: Identifies entities and relationships using LLMs
- **Community Detection**: Groups related entities into communities
- **Graph Search**: Searches entities, relationships, and communities
- **Best For**: Documents with complex relationships between concepts

### Non-Agentic RAG Mode

1. **Simple Retrieval**: Searches once with the user's exact query
2. **Context Injection**: Puts top results in LLM context
3. **Direct Answer**: LLM answers based on provided context
4. **No Iteration**: Single-shot approach without refinement

## Evaluation Results

The evaluation framework compares both modes across:

- **Simple Cases**: Direct legal questions (e.g., "故意杀人罪判几年？")
- **Complex Cases**: Multi-faceted legal scenarios requiring analysis

Metrics include:
- Success rate
- Response time
- Keyword/concept recall
- Citation quality
- Difficulty-specific performance

### Expected Results

Agentic RAG typically shows:
- **Better recall** for complex multi-aspect questions
- **More complete answers** through iterative search
- **Better citations** through explicit tool use
- **Slower response time** due to multiple LLM calls

Non-Agentic RAG typically shows:
- **Faster responses** with single retrieval
- **Good performance** on simple direct questions  
- **Limited ability** to handle complex scenarios
- **Less comprehensive** coverage of topics

## Troubleshooting

### Local Retrieval Pipeline Not Responding

```bash
# Check if the service is running
curl http://localhost:8002/health

# Start the service
cd ../retrieval-pipeline
python main.py
```

### Structured Index API Not Responding

```bash
# Check if the API is running
curl http://localhost:8080/status

# Start the API server
cd ../structured-index
python main.py serve

# Verify indexes are built
curl http://localhost:8080/statistics
```

### API Key Issues

Ensure environment variables are set:
```bash
export MOONSHOT_API_KEY=your_key
# or use .env file
```

### Indexing Errors

- Ensure the retrieval pipeline is running before indexing
- Check file encodings (UTF-8 expected)
- Verify chunk sizes are appropriate

## Educational Notes

This implementation demonstrates:

1. **Agent Design Patterns**: ReAct pattern with tool use
2. **RAG Architecture**: Retrieval, ranking, and generation
3. **Evaluation Methodology**: Systematic comparison of approaches
4. **Multi-Provider Support**: Abstraction for different LLMs
5. **Chinese NLP**: Handling Chinese text and legal domain

Key learning points:
- Agentic approaches trade speed for quality
- Tool use enables more sophisticated reasoning
- Evaluation should consider multiple dimensions
- Domain-specific knowledge requires careful indexing

## License

This is an educational project for learning purposes.

## Contributing

Feel free to extend this project with:
- Additional evaluation metrics
- More sophisticated chunking strategies
- Better reranking algorithms
- Additional knowledge base backends
- Multi-language support
- Custom entity extraction for GraphRAG
- Alternative clustering algorithms for RAPTOR
- Hybrid retrieval combining multiple backends
