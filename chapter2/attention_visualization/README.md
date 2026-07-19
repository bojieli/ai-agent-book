# Attention Visualization

Interactive visualization tool for exploring attention mechanisms in language models. Each agent run creates a unique trajectory that can be viewed and compared in the frontend.

## Overview

This project provides an interactive way to understand how language models allocate attention when processing different types of queries. Each run of the agent creates a new trajectory file that captures:
- The input query and model response
- Token-by-token attention weights
- Attention patterns across layers and heads
- Statistical analysis of attention distribution

## Architecture

The system follows a simple architecture:
1. **Agent generates trajectories**: Run `agent.py` or `main.py` to generate new trajectories
2. **JSON storage**: Each trajectory is saved as a unique JSON file in `frontend/public/trajectories/`
3. **Frontend visualization**: React app loads and displays all trajectories with tab navigation

## Quick Start (Standalone CLI)

The fastest way to reproduce the attention patterns described in Chapter 2
(实验 2-2) is the standalone command-line tool `attention_cli.py`. It runs a
real model, captures its self-attention, and writes a heatmap PNG directly —
no frontend needed.

```bash
# Single heatmap for the default prompt (last layer, heads averaged)
python attention_cli.py

# Custom prompt, inspect a specific layer/head, choose the output path
python attention_cli.py --prompt "北京 的 天气 怎么样" \
    --layer 0 --head 3 --output layer0_head3.png

# Generate a short continuation first, then visualize the whole sequence
python attention_cli.py --prompt "Explain attention in one sentence." \
    --max-new-tokens 40

# Compare how the attention sink emerges across layers, side by side
python attention_cli.py --compare-layers 0 13 -1 --output layer_compare.png
```

Run `python attention_cli.py --help` for the full flag list. Key flags:

| Flag | Meaning | Default |
| --- | --- | --- |
| `-p, --prompt` | Text to visualize | `北京 的 天气 怎么样` |
| `-o, --output` | Output PNG path | `attention_heatmap.png` |
| `-m, --model` | HF model name or local path | `Qwen/Qwen3-0.6B` |
| `--device` | `cuda` / `mps` / `cpu` | auto-detect |
| `-l, --layer` | Layer index (`-1` = last) | `-1` |
| `--head` | Head index (`-1` = average over heads) | `-1` |
| `--compare-layers` | Render several layers side by side | off |
| `--max-new-tokens` | Generate N tokens before capturing attention | `0` |
| `--no-chat-template` | Feed the raw prompt (no `<|im_start|>` markers) | off |
| `--cmap` | Matplotlib colormap | `viridis` |

**What the heatmap shows.** Rows are Query positions (the token attending)
and columns are Key positions (the token attended to). The tool measures and
prints the **attention-sink share** — the fraction of each row's attention
that lands on the first token — directly from the model's own weights. On
`Qwen3-0.6B` the last-layer sink typically absorbs ~75–85% of every row (the
Chapter 2 "注意力储存池 / Attention Sink" phenomenon), while layer 0 is close
to a local diagonal pattern. The masked upper triangle makes the causal
"triangle" structure explicit: each token only attends to itself and the
tokens before it.

> First run downloads the model weights (~1–2 GB). GPU/MPS is recommended but
> CPU works for these short prompts.

## Interactive Frontend Workflow

The visualization process can also be split into two manual steps: generating trajectories and viewing them in the frontend.

### Step 1: Generate Trajectories

Choose one of the following options to generate trajectory data:

```bash
# Option A: Run basic attention tracking demo
python agent.py

# Option B: Run ReAct agent with tool calling (demonstrates multi-step reasoning)
python main.py
```

Each run creates a new trajectory file with a unique timestamp in `frontend/public/trajectories/`.

### Step 2: Start the Frontend

In a separate terminal, start the frontend server:

```bash
cd frontend
npm install  # First time only
npm run dev
```

### Step 3: View Visualizations

Open your browser and navigate to http://localhost:3000

You can keep the frontend running and generate new trajectories in the first terminal - they'll automatically appear in the interface.

## Project Structure

```
attention_visualization/
├── attention_cli.py      # Standalone CLI: prompt -> attention heatmap PNG
├── agent.py               # Core attention tracking agent
├── main.py               # ReAct agent with tool calling
├── tools.py              # Tool implementations
├── visualization.py      # Visualization utilities (heatmap / comparison)
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── env.example          # Environment variable template
├── frontend/            # Next.js frontend
│   ├── pages/          # React pages
│   ├── components/     # Visualization components
│   └── public/
│       └── trajectories/  # Stored trajectory JSONs
│           ├── trajectory_YYYYMMDD_HHMMSS.json
│           └── manifest.json  # Index of all trajectories
└── attention_data/      # Additional trajectory storage
```

## How It Works

### 1. Trajectory Generation

#### Using `agent.py`
- Runs a basic attention tracking demo with various query types
- Captures attention weights for single-step responses
- Good for understanding basic attention patterns

#### Using `main.py`
- Implements a ReAct agent with tool calling capabilities
- Demonstrates multi-step reasoning with structured thought process
- Shows how attention shifts when the agent uses tools
- Better for understanding complex reasoning patterns

Both scripts:
- Generate unique trajectory files with timestamps
- Save results to `frontend/public/trajectories/`
- Update the manifest file for frontend discovery

### 2. Data Format
Each trajectory JSON contains:
```json
{
  "id": "20250914_123456",
  "timestamp": "2025-09-14 12:34:56",
  "test_case": {
    "category": "Math",
    "query": "What is 25 * 37?",
    "description": "Agent trajectory from..."
  },
  "response": "The answer is...",
  "tokens": ["What", "is", "25", ...],
  "attention_data": {
    "tokens": [...],
    "attention_matrix": [[...]],
    "num_layers": 1,
    "num_heads": 16
  },
  "metadata": {...}
}
```

### 3. Frontend Visualization
The React frontend:
- Loads all trajectories from the manifest
- Provides tabs to switch between different runs
- Displays attention heatmaps, token analysis, and statistics
- Updates automatically when new trajectories are generated

## Features

- **Multiple Trajectories**: Each agent run creates a new trajectory file
- **Tab Navigation**: Easy switching between different agent runs
- **Attention Heatmap**: Interactive visualization of token-to-token attention
- **Token Analysis**: View individual tokens and their attention patterns
- **Statistical Metrics**: Average attention, maximum attention, and entropy
- **Category Support**: Queries are categorized (Math, Knowledge, Reasoning, Code, Creative)
- **Persistent Storage**: All trajectories are saved and can be revisited

## Generating Custom Trajectories

### Using agent.py
Edit the `demonstrate_attention_tracking()` function to add custom queries:

```python
test_prompts = [
    ("Your custom query here", "Category"),
    # Add more queries...
]
```

### Using main.py
The ReAct agent demonstrates tool use and multi-step reasoning. Edit the test queries in `demonstrate_react_agent()`.

### Manual Generation
You can also use the agent programmatically:

```python
from agent import AttentionVisualizationAgent

agent = AttentionVisualizationAgent()
result = agent.generate_with_attention(
    "Your query here",
    max_new_tokens=100,
    temperature=0.3,
    save_trajectory=True,
    category="Custom"
)
```

## Requirements

### Python
- Python 3.10+
- PyTorch
- Transformers
- See `requirements.txt` for full list

### Frontend
- Node.js 14+
- npm or yarn
- See `frontend/package.json` for dependencies

## Installation

1. **Clone the repository**

2. **Set up environment variables (optional):**
```bash
cp env.example .env
# Edit .env to customize model, device, and visualization settings
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies:**
```bash
cd frontend
npm install
```

## Tips

- **First Time Setup**: The initial run will download the model (1~2 GB). GPU/MPS recommended for better performance
- **Generate Multiple Runs**: Run both `agent.py` and `main.py` to see different attention patterns
- **Compare Trajectories**: Use the tab interface to compare how the model handles similar queries
- **Tool vs. No-Tool**: Compare `main.py` (with tools) vs `agent.py` (without tools) to see how tool use affects attention
- **Analyze Patterns**: Look for attention focus differences in:
  - Math calculations
  - Knowledge queries
  - Reasoning tasks
  - Code generation
  - Creative writing
- **Frontend Auto-Discovery**: The frontend automatically detects new trajectories via the manifest file

## Troubleshooting

### No trajectories showing in frontend
1. Ensure you've run either `agent.py` or `main.py` at least once
2. Check that trajectory files exist in `frontend/public/trajectories/`
3. Verify `manifest.json` is present and contains trajectory entries

### Frontend not starting
1. Ensure Node.js is installed (version 14+)
2. Run `npm install` in the frontend directory
3. Check for port conflicts (default port 3000)

### Slow generation
- First run downloads the model (1~2 GB)
- Use GPU/MPS if available for faster generation
- Set smaller `max_new_tokens` in test queries for quicker demos

## Notes

- Each trajectory is timestamped to ensure uniqueness
- The manifest keeps track of the last 50 trajectories
- Trajectories persist between sessions
- The frontend automatically discovers new trajectories via the manifest
- Both `agent.py` and `main.py` can be run multiple times to generate different trajectories