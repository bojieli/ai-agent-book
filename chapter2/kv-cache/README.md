# KV Cache Demonstration with ReAct Agent

A comprehensive demonstration of KV (Key-Value) cache importance in LLMs using a ReAct pattern agent with local file system tools. This project shows how different implementation patterns can significantly impact performance through their effect on KV cache utilization.

## 🎯 Overview

This project implements a ReAct (Reasoning and Acting) agent that uses a current Moonshot Kimi model (default `kimi-k2.6`) to analyze code projects. The agent uses the standard OpenAI tool calling format and demonstrates six different implementation patterns - one correct and five incorrect - showing how seemingly minor changes can invalidate KV cache and dramatically impact performance.

> **Model note.** On the live Moonshot endpoint the whole current Kimi family (`kimi-k2.5` / `kimi-k2.6` / `kimi-k2.7*` / `kimi-k3`) are *reasoning* models: they emit `reasoning_content` and only accept `temperature=1` (the code handles this automatically). They **do** report `cached_tokens`, which is exactly what this experiment measures. The legacy non-reasoning `moonshot-v1-*` chat models, by contrast, do **not** report `cached_tokens`, so they cannot demonstrate the cache effect. We default to `kimi-k2.6` because it reports cache hits like the rest of the family but has the lightest reasoning footprint, which keeps TTFT the least noisy. Because any reasoning model adds variable thinking latency, the **cache hit rate / cache ratio** columns (which are deterministic) are the robust signal here; treat TTFT as secondary.

### What is KV Cache?

KV cache stores the key-value pairs from the attention mechanism of transformer models. When the conversation context remains stable, these cached values can be reused, significantly reducing computation time and improving response latency (especially Time to First Token - TTFT).

## 🚀 Features

- **ReAct Pattern Agent**: Implements reasoning and acting pattern for systematic task execution
- **Standard Tool Calling**: Uses OpenAI's standard tool calling format (no manual parsing)
- **Local File System Tools**: Safe implementations of `read_file`, `find`, and `grep` commands
- **Robust Error Handling**: Continues execution when tools fail, passing errors as results
- **Six Implementation Modes**: Demonstrates correct and incorrect KV cache patterns
- **Comprehensive Metrics**: Tracks TTFT, total time, cache hits/misses, and token usage
- **Offline Comparison Report** (`--report`): Renders the cross-strategy table from saved result files without an API key
- **Cost Estimate**: Comparison table adds an illustrative billable-token / savings column (configurable via `--cache-price-ratio`)
- **Detailed Logging**: Provides insights into cache behavior and performance impact
- **Smart Completion**: Automatically considers responses without tool calls as final answers
- **Argument Filtering**: Safely handles unexpected tool arguments without breaking

## 📦 Implementation Modes

### 1. ✅ Correct Implementation (`correct`)
Maintains stable context throughout the conversation:
- Fixed system prompt
- Consistent tool ordering
- Stable message history format
- No unnecessary context changes

### 2. ❌ Dynamic System Prompt (`dynamic_system`)
Adds a timestamp to the system prompt on each request:
- **Recreates entire message context each iteration**
- Invalidates entire cache on every call
- Significantly increases TTFT
- Wastes computational resources

### 3. ❌ Shuffled Tools (`shuffled_tools`)
Randomly reorders the tool list for each request:
- **Recreates context with shuffled tools each iteration**
- Breaks cache even though functionality is identical
- Demonstrates importance of consistent ordering
- Shows how minor changes affect caching

### 4. ❌ Dynamic User Profile (`dynamic_profile`)
Includes changing user credits in the context:
- **Recreates context with updated credits each iteration**
- Adds unnecessary dynamic information
- Forces cache invalidation for irrelevant changes
- Simulates common anti-patterns in production

### 5. ❌ Sliding Window (`sliding_window`)
Keeps only the most recent 5 messages:
- **Recreates context with different message window each iteration**
- Appears to reduce context length
- Actually breaks cache continuity
- Demonstrates why truncation strategies can backfire

### 6. ❌ Text Format (`text_format`)
Formats conversation history as plain text instead of structured messages:
- **Recreates context in text format each iteration**
- Breaks the expected message format
- Prevents proper cache utilization
- Shows importance of following API conventions

### 🔑 Critical Implementation Details

**For KV cache to be properly invalidated in the incorrect modes, the entire message context must be recreated from scratch at the START of EACH iteration.** 

The implementation ensures this by:

1. **CORRECT mode**: 
   - Builds messages list **once** on first iteration
   - **Keeps using the same list** throughout execution
   - Appends new messages (assistant responses, tool results) to this persistent list
   - Result: Stable context → KV cache works efficiently

2. **Incorrect modes**:
   - **Recreates the entire messages list** from conversation history at the **start of each iteration**
   - Within an iteration, still appends tool results to ensure proper API flow
   - But next iteration starts fresh with recreated context
   - Result: Context changes → KV cache invalidated

**Important**: Both modes append tool results within an iteration to ensure the API sees the complete conversation flow. The key difference is that incorrect modes throw away the messages list and rebuild it at the start of each new iteration, which forces cache invalidation.

## 🛠️ Installation

```bash
# Navigate to the project directory
cd chapter2/kv-cache

# Install dependencies
pip install -r requirements.txt

# Set your Kimi API key
export MOONSHOT_API_KEY="your-api-key-here"
```

> **通用回退（OpenRouter）**：未设置 `MOONSHOT_API_KEY` / `KIMI_API_KEY` 时，只要
> 配置了 `OPENROUTER_API_KEY`，实验会自动改走 OpenRouter（`kimi-*` 会映射为
> `moonshotai/kimi-k2`）。设置了 Moonshot key 时行为完全不变。

## 📖 Usage

### Interactive Mode (Default)

```bash
# Run interactive mode selection menu
python main.py

# You'll see a menu like:
# ============================================================
# KV CACHE DEMONSTRATION - MODE SELECTION
# ============================================================
# 
# Select a mode to run:
# 
#   1. ✅ Correct Implementation - Optimal KV cache usage
#   2. ❌ Dynamic System Prompt - Adds timestamps
#   3. ❌ Shuffled Tools - Randomizes tool order
#   4. ❌ Dynamic Profile - Updates user credits
#   5. ❌ Sliding Window - Keeps only recent messages
#   6. ❌ Text Format - Plain text instead of structured
#   7. 📊 Compare All - Run all modes and compare
# 
#   0. Exit
```

### Command Line Options

The CLI ships Chinese `--help`; run `python main.py --help` for the full list. Key flags:

| Flag | 说明 |
|------|------|
| `--mode MODE` | 运行单个策略（correct / dynamic_system / shuffled_tools / dynamic_profile / sliding_window / text_format） |
| `--compare` | 依次运行全部策略并打印横向对比表（需要 API Key） |
| `--report` | **离线**：从已保存的 `result_*.json` / `comparison_*.json` 生成对比表，**无需 API Key** |
| `--input ...` | 配合 `--report` 指定结果文件 / 通配符 / 目录（默认扫描当前目录） |
| `--model MODEL` | 选择模型（默认 `kimi-k2.6`；同族 `kimi-k2.5` / `kimi-k3` 亦可，均会上报 `cached_tokens`） |
| `--output PATH` | 指定结果 JSON 的输出路径（默认按模式 + 时间戳自动命名） |
| `--cache-price-ratio R` | 成本估算中缓存 token 相对正常 token 的计费比例（默认 `0.1`，即一折），仅作示意 |
| `--task`, `--root-dir` | 自定义任务 / 文件工具根目录 |

```bash
# Run specific mode directly (bypasses menu)
python main.py --mode correct

# Pick a model and write to a named file
python main.py --mode sliding_window --model kimi-k2.6 --output run.json

# Run comparison across all modes (needs API key)
python main.py --compare

# Disable interactive mode
python main.py --no-interactive --mode correct
```

### Offline Comparison Report (no API key)

Live runs need a Moonshot/Kimi API key. To read the **already-saved** result files
and print the cross-strategy comparison table in one command:

```bash
# Uses the result_*.json files already in this directory
python main.py --report

# Or point at specific files / a directory, and change the assumed cache discount
python main.py --report --input result_correct_*.json result_text_format_*.json
python main.py --report --cache-price-ratio 0.5
```

The table compares **cache hit rate, cache ratio, TTFT latency, total time, and an
illustrative billable-token / savings estimate** across strategies. The report parses
both the legacy single-mode files (metrics stored as an `AgentMetrics(...)` string) and
the newer dict-format files, so pre-existing results remain usable.

> The `Bill.Tok` / `Save%` columns are a transparent function of the *measured* token
> counts and the `--cache-price-ratio` you supply — they are an illustration of the cost
> impact, not a specific provider's price quote.

### Custom Tasks

```bash
# Provide custom task via command line
python main.py --mode correct --task "Read all README files and summarize their contents"

# Use different root directory
python main.py --mode correct --root-dir ../.. --task "Analyze the project structure"
```

## 📊 Metrics Explained

### Performance Metrics
- **TTFT (Time to First Token)**: Time until the first token is generated - critical for user experience
  - Tracked per iteration to show cache benefits
  - First iteration: Cold start (no cache)
  - Subsequent iterations: Should show improvement with cache
- **TTFT Analysis**: 
  - Per-iteration tracking shows cache effectiveness
  - Average TTFT demonstrates overall performance
  - Improvement percentage quantifies cache benefits
- **Total Execution Time**: Complete time for task execution
- **Iterations**: Number of ReAct cycles performed
- **Tool Calls**: Number of tool invocations made

### Cache Statistics
- **Cached Tokens**: Number of tokens retrieved from cache
- **Cache Hits**: Successful cache retrievals
- **Cache Misses**: Failed cache retrievals requiring recomputation
- **Cache Hit Rate**: Percentage of successful cache usage

### Token Usage
- **Prompt Tokens**: Tokens in the input prompt
- **Completion Tokens**: Tokens generated by the model
- **Cache Ratio**: Percentage of prompt tokens served from cache

## 📈 Expected Results

When comparing implementations, you should observe:

1. **Correct Implementation**: 
   - Every iteration after the first reports cached tokens (the stable prefix is reused)
   - Low, steady first-token latency
   - The prefix (system prompt + tools + prior turns) is served from cache

2. **Incorrect Implementations**:
   - A collapsing **cache ratio** — e.g. shuffling the tool list drops the share of
     prompt tokens served from cache to roughly a third of the correct run
   - Consistently higher TTFT (reformatting history as text or shuffling tools
     more than doubles first-token latency in the measured run)
   - Longer total time (up to ~2.4x the correct run for `text_format`)

> **On a reasoning model** (the whole current Kimi family reasons) TTFT carries
> extra variance from hidden thinking tokens, so the **cache ratio** column is the
> cleanest evidence of the effect. Note also that appending dynamic data at the
> *end* of an otherwise-stable prefix (as `dynamic_system` / `dynamic_profile` do)
> only invalidates the cache *from that point on* — the base prefix before it still
> caches — so their headline cache ratio can look close to `correct` while their
> **total time still regresses**. The lesson: keep dynamic data out of the prefix
> entirely.

## 🔍 Example Output

```
📊 Performance Metrics:
  • Time to First Token (TTFT): 0.823 seconds
  • TTFT per iteration:
      Iteration 1: 0.823s
      Iteration 2: 0.234s (with cache)
      Iteration 3: 0.198s (with cache)
      Iteration 4: 0.187s (with cache)
      Iteration 5: 0.192s (with cache)
  • TTFT Analysis:
      First iteration: 0.823s
      Last iteration: 0.192s
      Average (after first): 0.203s
      Improvement: 76.7%

```

### Comparison Table (`--report` on the saved result files in this directory)

These are the **actual measured numbers** from a single `--compare` run — all six
strategies under one task (`kimi-k2.6`, root dir = this folder, task = "find all
Python files, read `main.py` + `agent.py`, summarize in 3 sentences"), then read
back with `python main.py --report`:

```
Mode             Iters  1st TTFT   Avg TTFT   Total(s)   Prompt    Cached    Hit%    Cache%   Bill.Tok   Save%
----------------------------------------------------------------------------------------------------------------
correct          3      2.328      6.054      18.163     7,567     768       100.0   10.1     6,876      9.1
dynamic_profile  3      2.206      5.986      17.962     7,652     768       100.0   10.0     6,961      9.0
dynamic_system   3      2.497      8.085      24.260     7,639     768       100.0   10.1     6,948      9.0
shuffled_tools   3      7.818      11.122     33.369     7,568     256       100.0   3.4      7,338      3.0
sliding_window   5      2.234      3.649      14.704     2,224     1,510     100.0   67.9     865        61.1
text_format      3      6.189      14.432     43.297     7,430     674       100.0   9.1      6,823      8.2
```

Reading the table: `shuffled_tools` reorders the tool definitions that sit near the
front of the prefix, so its **cache ratio collapses from 10.1% to 3.4%** and its
first-token latency jumps from ~2.3s to ~7.8s. `text_format` rebuilds history as one
plain-text blob every turn, roughly **2.4x the correct total time**. `sliding_window`
shows a high cache ratio only because truncation shrinks the prompt itself (fewer,
mostly-cached tokens) — a reminder that a high ratio on a tiny prompt is not the same
as an efficient run.

`Cache%` is the share of prompt tokens served from cache; `Hit%` is the share of
*iterations* that saw any cache. `Bill.Tok`/`Save%` assume cached tokens bill at
`--cache-price-ratio` (default 0.1) of a normal token — an illustration, not a
provider quote. All six rows come from one `--compare` run, so they are directly
comparable; regenerate with `python main.py --compare` to reproduce.

## 💡 Key Insights

1. **Stable Context is Critical**: Any change to the message context invalidates KV cache
2. **Order Matters**: Even reordering identical content breaks caching
3. **Avoid Dynamic Metadata**: Timestamps, counters, and other changing data harm performance
4. **Proper Formatting**: Use the API's expected message format for optimal caching
5. **Context Continuity**: Maintaining full history often performs better than truncation

## 🏗️ Architecture

```
kv-cache/
├── agent.py                # ReAct agent implementation with different modes
├── main.py                 # Main script for running experiments
├── demo_quick.py           # Quick demonstration script
├── test_tools.py           # Test local file system tools
├── test_error_handling.py  # Test error recovery capabilities
├── test_completion.py      # Test final answer detection
├── requirements.txt        # Project dependencies
├── README.md              # This file
└── *.log                  # Generated log files
```

### Components

- **KVCacheAgent**: Main agent class implementing ReAct pattern
- **LocalFileTools**: Safe file system operations (read, find, grep)
- **KVCacheMode**: Enum defining different implementation patterns
- **AgentMetrics**: Dataclass for tracking performance metrics

### Error Handling

The agent implements robust error handling:
- **Tool Errors**: When a tool fails (e.g., file not found), the error is returned as a tool result
- **Argument Errors**: Unexpected tool arguments are filtered out automatically
- **Continuation**: The agent continues execution even when tools fail
- **Error Reporting**: Errors are passed to the model, which can acknowledge and work around them
- **Security**: Access outside the root directory is denied with clear error messages

## 🔧 Advanced Configuration

### Environment Variables

```bash
# API Configuration
export MOONSHOT_API_KEY="your-key"

# Logging Level
export LOG_LEVEL="DEBUG"  # INFO, WARNING, ERROR
```

### Custom Implementation Modes

You can extend the `KVCacheMode` enum in `agent.py` to add new patterns:

```python
class KVCacheMode(Enum):
    CUSTOM = "custom"  # Your new mode
```

Then implement the behavior in the corresponding methods:
- `_get_system_prompt()`
- `_get_tools()`
- `_format_messages()`

## 📝 Best Practices for KV Cache

Based on this demonstration, follow these practices:

1. **Keep System Prompts Stable**: Avoid adding timestamps or request-specific data
2. **Maintain Consistent Tool Order**: Don't shuffle or reorder tools dynamically
3. **Avoid Unnecessary Metadata**: Don't include counters, credits, or changing values
4. **Use Proper Message Format**: Follow the API's expected conversation structure
5. **Preserve Context Continuity**: Avoid aggressive truncation strategies
6. **Cache-Aware Design**: Design your prompts and context with caching in mind

## 🐛 Troubleshooting

### High TTFT with Correct Implementation
- Check if this is the first request (cold start)
- Verify API key and model availability
- Ensure stable network connection

### Zero Cache Hits
- Confirm using a current Kimi model (`kimi-k2.5` / `kimi-k2.6` / `kimi-k3`) — these
  report `cached_tokens`. The non-reasoning `moonshot-v1-*` models do **not** report
  cached tokens, so this metric will read 0 even when caching happens server-side.
- Check if context is actually stable
- Review logs for cache invalidation patterns

### Tool Execution Errors
- Verify root directory permissions
- Check file paths are within root directory
- Ensure files exist and are readable

## 📚 References

- [Kimi API Documentation](https://platform.moonshot.cn/docs/api-reference)
- [ReAct Pattern Paper](https://arxiv.org/abs/2210.03629)
- [Transformer KV Cache Explanation](https://huggingface.co/docs/transformers/kv_cache)

## 📄 License

This project is part of the AI Agent Book educational materials.
