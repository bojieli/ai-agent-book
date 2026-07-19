# Mem0 Agent with Kimi K3 for LOCOMO Benchmark

A sophisticated AI agent implementation that combines the Mem0 memory framework with the Kimi K3 language model, specifically designed for the LOCOMO (Long-Context Multi-Agent) benchmark.

## Overview

This project implements an advanced conversational AI agent that:
- **Persistent Memory**: Uses Mem0 framework for long-term memory management across sessions
- **Advanced Language Model**: Integrates Kimi K3 model (1M-token context window; experiment caps usage at a smaller budget)
- **LOCOMO Benchmark**: Evaluates agent performance on long-context multi-agent communication tasks
- **Multi-Session Support**: Maintains context and consistency across multiple conversation sessions
- **Multi-Agent Collaboration**: Supports multiple agents working together with shared memory

## Features

### Core Capabilities
- **Dynamic Memory Management**: Automatically extracts, consolidates, and retrieves relevant information
- **Context Preservation**: Maintains conversation context across sessions and agents
- **Performance Metrics**: Tracks consistency, coherence, response time, and memory utilization
- **Flexible Backend**: Supports both local and cloud-based memory storage

### Benchmark Scenarios
The LOCOMO benchmark includes five scenario types:
1. **Collaborative Planning**: Multiple agents plan complex projects together
2. **Information Sharing**: Agents share and synthesize information across sessions
3. **Problem Solving**: Multi-step problem solving with memory retention
4. **Negotiation**: Multi-round negotiations with position tracking
5. **Teaching & Learning**: Educational dialogues with progress tracking

## Installation

### Prerequisites
- Python 3.8 or higher
- Kimi API key (from Moonshot AI)
- Optional: Mem0 cloud API key for cloud storage

### Setup

1. Clone the repository:
```bash
cd projects/week2/mem0
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp env.example .env
# Edit .env with your API keys and configuration
```

Required environment variables:
- `KIMI_API_KEY`: Your Kimi K3 API key
- `MODEL_NAME`: Model name (default: kimi-k3). This is the raw Moonshot model
  id (e.g. `kimi-k3`, `kimi-k2.5`, `kimi-k2.6`) passed straight to the API — do
  NOT use a `provider/model` slash form here; Mem0 is configured with the
  `openai` provider pointed at Moonshot's `base_url`, so it forwards the string
  verbatim and `kimi/k3` returns "Not found the model".
- `MEMORY_BACKEND`: Storage backend (local/cloud)
- `MAX_TOKENS`: Maximum token limit (default: 128000)

## Quick Start

### Basic Usage

Run the quickstart examples to see the agent in action:

```bash
python quickstart.py
```

This will demonstrate:
- Basic conversation with memory
- Multi-session memory persistence
- Multi-agent collaboration

### Memory Pipeline Demo (提取—对比—决策)

The single clearest demonstration of Mem0's value — its ADD / UPDATE / DELETE /
NOOP pipeline and cross-session recall — is the `demo` mode:

```bash
python main.py --mode demo --user-id demo_user
```

This reproduces the book's centerpiece example (chapter3.md): the user first
says they live in Beijing, a later turn says they moved to Shanghai, and Mem0
resolves the conflict with an **UPDATE** (revising the existing memory) instead
of storing two contradictory records. In between, a stored memory is recalled
via semantic search, showing memory being *used later*. (The same routine is
`memory_pipeline_example()` in `quickstart.py`, run first by `python quickstart.py`.)

### Direct Memory Operations CLI

Mem0's memory API is exposed directly so you can observe each pipeline decision
without the chat loop. All flags have Chinese `--help` (`python main.py --help`):

```bash
# ADD — write a conversation/utterance; prints the ADD/UPDATE/DELETE events
python main.py --mode memory --op add   --text "我住在北京，是一名后端工程师" --user-id u1

# SEARCH — semantic recall
python main.py --mode memory --op search --query "这个用户住在哪里？" --user-id u1

# GET-ALL — list every stored memory (optionally dump to JSON)
python main.py --mode memory --op get-all --user-id u1 --output mem.json

# HISTORY — the change/audit trail of one memory id (shows UPDATE/DELETE over time)
python main.py --mode memory --op history --memory-id <id>

# DELETE — remove one memory by id
python main.py --mode memory --op delete --memory-id <id>
```

Key flags: `--op {add,search,get-all,history,delete}`, `--text`, `--query`,
`--memory-id`, `--user-id`, `--agent-id`, `--model` (override `MODEL_NAME`),
`--output` (write result JSON). `--text` accepts either a raw string or a path
to a JSON message list.

> These operations, `demo` mode, and the chat modes all require a working LLM
> API key (`KIMI_API_KEY`) and a vector store — Mem0's fact extraction and
> semantic retrieval are online model calls. With no key the CLI parses
> arguments and then reports the missing key; no memory output is fabricated.

### Interactive Mode

Start an interactive conversation session:

```bash
python main.py --mode interactive
```

Available commands in interactive mode:
- `help` - Show available commands
- `memories` - Display stored memories
- `metrics` - Show performance metrics
- `save` - Save conversation state
- `load` - Load previous state
- `new` - Start a new session
- `exit` - Exit the program

### Batch Processing

Process multiple conversations from a JSON file:

```bash
python main.py --mode batch --input conversations.json --output results.json
```

Input format:
```json
[
  {
    "session_id": "session_001",
    "user_id": "user_001",
    "agent_id": "agent_001",
    "turns": [
      "First user message",
      "Second user message"
    ]
  }
]
```

## Running LOCOMO Benchmark

### Full Benchmark

Run the complete LOCOMO benchmark evaluation:

```bash
python experiment.py --scenarios 10 --output results/
```

This will:
1. Generate and run 10 benchmark scenarios
2. Evaluate agent performance on each scenario
3. Calculate metrics (consistency, coherence, memory utilization)
4. Generate detailed reports with visualizations

### Benchmark Metrics

The benchmark evaluates:
- **Consistency Score**: How well the agent maintains consistent information
- **Coherence Score**: Relevance and logical flow of responses
- **Memory Retention**: Effectiveness of memory storage and retrieval
- **Response Time**: Average generation time per turn
- **Context Utilization**: How well the agent uses available context

### Understanding Results

Results are saved in JSON format with the following structure:
```json
{
  "config": {...},
  "scenarios": [
    {
      "scenario": {...},
      "sessions": [...],
      "overall_metrics": {
        "avg_consistency": 0.92,
        "avg_coherence": 0.88,
        "memory_utilization": 42
      }
    }
  ],
  "overall_metrics": {...}
}
```

## Architecture

### Components

1. **Agent Module** (`agent.py`)
   - `Mem0Agent`: Main agent class with memory integration
   - `KimiK3Client`: Client for Kimi K3 model API
   - `AgentContext`: Context management for sessions

2. **Configuration** (`config.py`)
   - `KimiConfig`: Kimi model settings
   - `Mem0Config`: Memory system configuration
   - `LOCOMOConfig`: Benchmark parameters

3. **Experiment Framework** (`experiment.py`)
   - `LOCOMOBenchmark`: Benchmark implementation
   - Scenario generation and evaluation
   - Metrics calculation and reporting

### Memory System

The Mem0 framework provides:
- **Vector Storage**: Efficient semantic search using embeddings
- **Memory Consolidation**: Automatic extraction of key information
- **Context Retrieval**: Intelligent retrieval of relevant memories
- **Multi-level Organization**: User, agent, and session-level memories

## Advanced Usage

### Custom Scenarios

Create custom benchmark scenarios by modifying `experiment.py`:

```python
custom_scenario = {
    "type": "custom_type",
    "description": "Your scenario description",
    "topics": ["topic1", "topic2"],
    "context_requirements": ["requirement1", "requirement2"]
}
```

### Memory Backends

#### Local Storage (Chroma)
```python
config.mem0.backend = "local"
config.mem0.vector_store_config = {
    "provider": "chroma",
    "config": {
        "collection_name": "my_collection",
        "path": "./data/chroma_db"
    }
}
```

#### Cloud Storage (Mem0 Cloud)
```python
config.mem0.backend = "cloud"
config.mem0.api_key = "your_mem0_api_key"
```

### Performance Tuning

Optimize performance by adjusting:
- `MAX_TOKENS`: Reduce for faster responses
- `TEMPERATURE`: Lower for more consistent outputs
- `context_window_size`: Balance between context and speed
- Memory retrieval limit: Adjust in `_prepare_messages()`

## Troubleshooting

### Common Issues

1. **API Key Errors**
   - Ensure `KIMI_API_KEY` is set in `.env`
   - Check API key validity and permissions

2. **Memory Backend Issues**
   - For local: Ensure write permissions in `./data/`
   - For cloud: Verify `MEM0_API_KEY` is correct

3. **Performance Issues**
   - Reduce `MAX_TOKENS` for faster responses
   - Use local memory backend for lower latency
   - Adjust batch sizes in benchmark runs

### Debug Mode

Enable detailed logging:
```bash
export LOG_LEVEL=DEBUG
python main.py
```

## Development

### Project Structure
```
mem0/
├── agent.py           # Core agent implementation
├── config.py          # Configuration management
├── experiment.py      # LOCOMO benchmark
├── main.py           # Main entry point
├── quickstart.py     # Example demonstrations
├── requirements.txt  # Dependencies
├── env.example      # Environment template
└── README.md        # Documentation
```

### Testing

Run tests (when available):
```bash
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Performance Benchmarks

Typical performance metrics on standard hardware:
- Average response time: 1-3 seconds
- Memory retrieval: <100ms
- Consistency score: 0.85-0.95
- Coherence score: 0.80-0.90
- Memory utilization: 20-100 items per session

## Limitations

- Requires active internet connection for API calls
- Memory storage grows with usage (periodic cleanup recommended)
- Context window limited to 128K tokens
- Response quality depends on model availability

## License

This project is part of the AI Agent Book training materials.

## Acknowledgments

- Mem0 framework by Mem0 AI
- Kimi K3 model by Moonshot AI
- LOCOMO benchmark concept for long-context evaluation

## Support

For issues and questions:
- Check the troubleshooting section
- Review example code in `quickstart.py`
- Refer to the main AI Agent Book documentation


## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.

> Note: mem0's embedder still uses OpenAI embeddings (OpenRouter has no embeddings endpoint), so `OPENAI_API_KEY` is still required for storing/retrieving memories. The OpenRouter fallback only covers the chat LLM (fact extraction, ADD/UPDATE/DELETE decisions, and answering).
