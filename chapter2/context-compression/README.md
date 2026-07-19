# Context Compression Strategies Experiment

This project demonstrates and compares different context compression strategies for LLM agents, using the task of researching OpenAI co-founders' current affiliations as a test case.

## Overview

As LLM context windows grow larger (128K+ tokens), managing context efficiently becomes crucial for:
- **Cost optimization** - Reducing token usage
- **Performance** - Faster response times
- **Reliability** - Avoiding context overflow errors
- **Relevance** - Maintaining focus on important information

This experiment implements and compares 6 different context compression strategies to understand their trade-offs.

## Compression Strategies

### 1. No Compression
- **Description**: Puts all original webpage content directly into agent context
- **Expected Result**: Fails after a few tool calls due to context overflow
- **Purpose**: Demonstrates the baseline problem

### 2. Non-Context-Aware: Individual Summaries
- **Description**: Summarizes each webpage independently using LLM, then concatenates all summaries
- **Expected Result**: Preserves page-specific details but may lose cross-page relationships
- **Trade-off**: Multiple LLM calls (one per page) but maintains page boundaries
- **Best for**: When each source should be treated independently

### 3. Non-Context-Aware: Combined Summary
- **Description**: Concatenates all webpage content first, then creates a single comprehensive summary
- **Expected Result**: Better understanding of overall content but may lose page-specific attribution
- **Trade-off**: Single LLM call but might hit token limits with many pages
- **Best for**: When looking for overarching themes across multiple sources

### 4. Context-Aware Summarization
- **Description**: Combines all search results and creates query-focused summary
- **Expected Result**: Better relevance preservation
- **Trade-off**: Requires additional LLM call for summarization

### 5. Context-Aware with Citations
- **Description**: Similar to #4 but includes citations and source links
- **Expected Result**: Enables follow-up questions with source tracking
- **Trade-off**: Slightly larger context but maintains traceability

### 6. Windowed Context
- **Description**: Keeps full content for last tool call, compresses older history
- **Expected Result**: Balance between detail and efficiency
- **Trade-off**: Recent detail vs. historical compression
- **Smart Compression**: Only compresses uncompressed messages (marked with [COMPRESSED] to prevent re-compression)

## Installation

1. Navigate to the project:
```bash
cd chapter2/context-compression
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp env.example .env
# Edit .env with your API keys
```

Required API keys:
- `MOONSHOT_API_KEY`: For the Kimi (Moonshot) model (required). The book's 实验 2-9 uses Kimi K3 (a reasoning
  model whose real context window is ~1M tokens; the demo deliberately caps context at a 128K budget via
  `CONTEXT_WINDOW_SIZE` so the overflow/compression behavior is observable). The model name is configurable via
  `MODEL_NAME` in `.env` or the `-m/--model` CLI flag (e.g. `kimi-k2.5`, `kimi-k3`, `moonshot-v1-128k`).
- `OPENROUTER_API_KEY`: 通用回退。未设置 `MOONSHOT_API_KEY` 时，只要配置了
  `OPENROUTER_API_KEY`，实验会自动改走 OpenRouter（`kimi-*` 映射为
  `moonshotai/kimi-k2`）。设置了 `MOONSHOT_API_KEY` 时行为完全不变。
- `SERPER_API_KEY`: For web search (optional, will use mock data if not provided)

Get API keys:
- Moonshot/Kimi: https://platform.moonshot.cn/
- Serper (free tier): https://serper.dev/

## Scripts Overview

| Script | Purpose | Output |
|--------|---------|--------|
| `main.py` | Interactive demo / single strategy runner | Console output |
| `experiment.py` | Automated comparison of strategies (token / compression / success table) | Results in `results/` |
| `run_all_strategies.py` | Run strategies with detailed per-round logging | Logs in `logs/` |
| `quickstart.py` | Menu wrapper that checks env and launches the above | Console output |

All three main entrypoints ship an `argparse` CLI (Chinese `--help`). Run any of them with `-h`
to see the full option list. The three most useful flags are shared:

- `-s/--strategy` — 选择要运行的一种或多种策略（默认全部 6 种）；取值见下方“Compression Strategies”或运行 `--list-strategies`
- `-m/--model` — 覆盖模型名（默认读取环境变量 `MODEL_NAME`）
- `-n/--max-iterations` — 每个策略允许的最大工具调用轮数

Strategy aliases accepted by `--strategy`: `no_compression`, `individual`, `combined`,
`context_aware`, `citations`, `windowed`.

## Usage

### Run Full Experiment (comparison table + JSON)

Compare all 6 strategies (default), or a subset:
```bash
python experiment.py                          # 运行全部 6 种策略并生成对比表
python experiment.py -s context_aware         # 只运行“上下文感知压缩”
python experiment.py -s individual combined   # 只对比两种非任务感知策略
python experiment.py -m moonshot-v1-128k -o results/run.json   # 换模型 + 指定输出路径
python experiment.py --list-strategies        # 查看可选策略名
```

This will:
- Test each selected compression strategy sequentially
- Research OpenAI co-founders' affiliations
- Print a comparison table (Success / Time / **Tokens** / Compression / Overflows)
- Save results to `results/experiment_TIMESTAMP.json` (or the path given by `-o/--output`)

Key flags: `-s/--strategy`, `-m/--model`, `-o/--output`, `-n/--max-iterations`, `--streaming`, `--list-strategies`.

### Run All Strategies with Logging

Run strategies with detailed logging and compression output:
```bash
python run_all_strategies.py                  # 全部 6 种策略
python run_all_strategies.py -s windowed      # 只跑自适应窗口化
python run_all_strategies.py --log-dir logs/k2 -m kimi-k2.5
```

Features:
- Runs the selected compression strategies sequentially
- Logs all compression summaries to file
- Shows streaming output in real-time
- Saves detailed logs to `<log-dir>/strategy_run_TIMESTAMP.log`
- Saves JSON results to `<log-dir>/strategy_results_TIMESTAMP.json`
- Generates comparison summary at the end

Key flags: `-s/--strategy`, `-m/--model`, `--log-dir`, `-n/--max-iterations`, `--list-strategies`.

### Interactive Demo

Test individual strategies with streaming output:
```bash
python main.py                    # Interactive: choose a strategy at the prompt
python main.py -s citations       # Run a specific strategy non-interactively
python main.py -s windowed --no-streaming  # Disable streaming output
```

Features:
- Choose any compression strategy (interactively, or with `-s/--strategy`)
- Streaming responses enabled by default (`--no-streaming` to disable)
- See real-time execution
- Try follow-up questions (for citation strategy)

### Custom Usage

```python
from agent import ResearchAgent
from compression_strategies import CompressionStrategy

# Create agent with specific strategy
agent = ResearchAgent(
    api_key="your_api_key",
    compression_strategy=CompressionStrategy.CONTEXT_AWARE_CITATIONS,
    enable_streaming=True
)

# Execute research
result = agent.execute_research()

# Access results
if result['success']:
    print(result['final_answer'])
    print(f"Tool calls: {len(result['trajectory'].tool_calls)}")
```

## Project Structure

```
context-compression/
├── config.py                  # Configuration management
├── web_tools.py              # Web search and fetch tools
├── compression_strategies.py  # Compression strategy implementations
├── agent.py                  # Main research agent with streaming
├── experiment.py             # Experiment runner for comparisons (CLI)
├── run_all_strategies.py     # Detailed per-round logging runner (CLI)
├── main.py                   # Interactive demo / single strategy runner (CLI)
├── quickstart.py             # Menu wrapper (env check + launcher)
├── requirements.txt          # Python dependencies
├── env.example              # Environment variables template
├── logs/                    # Detailed logs (created by run_all_strategies.py)
└── results/                 # Experiment results (created on run)
```

## Key Components

### Web Tools (`web_tools.py`)
- **search_web**: Searches using Serper API, crawls each result
- **fetch_webpage**: Fetches and converts HTML to clean text
- **Mock data**: Provides sample data when API key unavailable

### Compression Strategies (`compression_strategies.py`)
- **ContextCompressor**: Implements all 6 strategies
- **CompressedContent**: Data class for compressed results
- **Dynamic compression**: Based on query and context

### Research Agent (`agent.py`)
- **Streaming support**: Real-time response streaming
- **Tool integration**: Web search and fetch capabilities
- **Message management**: Handles conversation history
- **Windowed compression**: Dynamic history compression

### Experiment Runner (`experiment.py`)
- **Automated testing**: Runs all strategies
- **Metrics collection**: Execution time, compression ratio, success rate
- **Comparison report**: Visual comparison table
- **Results persistence**: JSON output for analysis

## Metrics Collected

- **Success Rate**: Whether task completed successfully
- **Execution Time**: Total time to complete research
- **Compression Ratio**: Compressed size / original size
- **Context Overflows**: Number of times context limit approached
- **Tool Calls**: Number of web searches performed
- **Final Answer Length**: Size of generated report

## Expected Results

Based on the compression strategies:

1. **No Compression**: ❌ Fails with context overflow
2. **Non-Context-Aware**: ⚠️ Completes but may miss details
3. **Context-Aware**: ✅ Good balance of size and relevance
4. **With Citations**: ✅ Best for follow-ups, slightly larger
5. **Windowed Context**: ✅ Most efficient for long conversations

## Measured Results (real run)

The numbers below are from a **real** end-to-end run — no mock data. Every strategy
used live Serper web search (real 2026 web pages fetched and crawled) and the current
Moonshot reasoning model.

- **Model**: `kimi-k3` (Moonshot reasoning model; real window ~1M tokens, but the demo caps
  the compression/overflow budget at `CONTEXT_WINDOW_SIZE = 128000`)
- **Search**: real Serper (`google.serper.dev`) web search + page crawling
- **Task**: 识别并追踪 OpenAI 联合创始人的职业状态 (track current affiliations of the ~11 OpenAI co-founders)
- **Run date**: 2026-07-18 · `MAX_ITERATIONS=15` · raw JSON: `results/kimi_k3_real_20260718.json`

Columns: **Tokens** = cumulative Kimi API token usage (prompt + completion across all
iterations); **Compress** = compressed chars / original chars (smaller = compressed harder);
**Overflows** = times the 128K budget was approached/exceeded.

| # | Strategy | Success | Iterations | Tokens | Compress | Overflows | Time |
|---|----------|---------|-----------|--------|----------|-----------|------|
| 1 | `no_compression` | ❌ (overflow at 165,227 tok > 128K) | 5 | 166,043 | 102.1% | 1 | 107s |
| 2 | `non_context_aware_individual_summary` | ✅ | 12 | 276,608 | 10.9% | 4 | 2980s |
| 3 | `non_context_aware_combined_summary` | ✅ | 10 | 93,449 | 4.3% | 0 | 1189s |
| 4 | `context_aware_summary` | ✅ | 7 | 40,157 | 3.0% | 0 | 967s |
| 5 | `context_aware_with_citations` | ✅ | 10 | 222,992 | 4.1% | 3 | 1235s |
| 6 | `windowed_context` | ✅ | 7 | 174,601 | 102.4% | 4 | 867s |

Notes:
- **No compression** fails exactly as designed: context overflows the 128K budget
  (165,227 tokens used) around the 5th iteration.
- **Context-aware summary (#4)** is the most token-efficient successful strategy
  (40,157 tokens, 3.0% char compression) — it compresses hardest while still solving the task.
- **Individual summaries (#2)** are by far the slowest (~50 min) because each fetched page
  is summarized separately by the reasoning model; token usage is also the highest.
- **Windowed context (#6)** only compresses when prompt usage crosses the 80% threshold
  (≈102,400 tokens), then batch-compresses all uncompressed tool messages at once; because
  it keeps recent full content, its char-level "compression ratio" stays ~100% while it
  still completes the task fastest among the compressing strategies.
- These are single-run measurements with a reasoning model and live web search, so absolute
  numbers will vary run to run; the relative ordering is the takeaway.

## Configuration

Edit `.env` or `config.py` for:

- `MODEL_NAME`: LLM model to use (default: kimi-k3)
- `MODEL_TEMPERATURE`: Response randomness (default: 0.3)
- `MAX_ITERATIONS`: Maximum tool calls (default: 50)
- `MAX_WEBPAGE_LENGTH`: Max chars per webpage (default: 50000)
- `SUMMARY_MAX_TOKENS`: Max tokens for summaries (default: 500)
- `CONTEXT_WINDOW_SIZE`: Context budget for the demo's overflow/compression trigger (default: 128000; note Kimi K3's real window is ~1M tokens — this is an intentionally smaller budget so compression is exercised)

## Troubleshooting

### No API Keys
The system will use mock data if SERPER_API_KEY is not set, allowing you to test the compression strategies without web search.

### Context Overflow
If you encounter context overflow with strategies other than "No Compression", try:
- Reducing `MAX_WEBPAGE_LENGTH`
- Decreasing `SUMMARY_MAX_TOKENS`
- Limiting search results with `num_results`

### Slow Execution
- Disable streaming in demo for faster output
- Reduce `MAX_ITERATIONS` for quicker experiments
- Use mock data instead of real web search

## Research Task

The experiment uses a specific research task:
> "Find the current affiliations of all OpenAI co-founders"

This task is ideal because it:
- Requires multiple searches (one per co-founder)
- Generates substantial content (biographical information)
- Tests context management (accumulating information)
- Has verifiable results (known affiliations)

## Extending the Project

To add new compression strategies:

1. Add strategy to `CompressionStrategy` enum
2. Implement in `ContextCompressor` class
3. Add handling in `compress_search_results()`
4. Update experiment runner if needed

To change the research task:

1. Modify system prompt in `agent.py`
2. Update mock data in `web_tools.py`
3. Adjust tool descriptions as needed

## License

This project is part of the AI Agent practical training course and is for educational purposes.
