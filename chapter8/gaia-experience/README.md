# GAIA Experience Learning System

> 对应《深入理解 AI Agent》第 8 章 · 实验 8-1 ★★「从成功经验中学习：策略摘要」。
> 本目录是实验的顶层封装脚本；`AWorld/` 为上游框架副本，请勿修改。

A modified version of AWorld that adds learning from experience capabilities for the GAIA benchmark. This system can capture successful task trajectories, summarize them into reusable experiences, and apply learned knowledge to improve performance on new tasks.

**实验要点（why this matters）**：GAIA 是需要多步推理、综合使用浏览器/文件/代码解释器的高难度基准。
本实验演示一个「学习-应用」闭环——Agent 每成功解一题就把轨迹提炼为经验入库，遇到新题时检索相似经验注入提示词。
命题是：**复用积累的经验能提升 GAIA 成绩**。使用 `--compare` 可以在同一批题上做 A/B 对照来直观检验这一命题（见下文
[A/B 对照实验](#-ab-对照实验reproduce-the-experiments-point)）。

## 🌟 Features

### 1. **Learning from Experience**
- Captures the **actual execution trajectory** produced by AWorld (read back from
  `TaskResponse.trajectory`) when a task completes successfully
- Uses LLM to summarize trajectories into natural language experiences
- Stores learned experiences (approach, key insights, tools, step count) for future reference

### 2. **Knowledge Base with Semantic Search**
- Indexes the `gaia-validation.jsonl` file for preloaded experiences
- Uses sentence embeddings for semantic similarity search
- Supports both semantic and keyword-based retrieval

### 3. **Experience Application**
- Retrieves relevant past experiences for new queries
- Enhances system prompts with relevant experiences
- Improves task performance by leveraging past successes

## 📁 Project Structure

```
gaia-experience/
├── AWorld/                      # Original AWorld repository
├── experience_agent.py          # Extended agent with experience learning
├── knowledge_base.py           # Knowledge base for indexing and retrieval
├── trajectory_summarizer.py    # Summarizes trajectories into experiences
├── run_with_experience.py      # Main execution script with learning features
├── demo.py                     # Demo script showcasing all features
├── config.yaml                 # Configuration file
├── requirements.txt            # Python dependencies
├── gaia-validation.jsonl       # GAIA validation dataset
└── README.md                   # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Conda (recommended for environment management)
- Node.js 22 LTS (for AWorld web UI)

### Setup Steps

1. **Clone and setup the environment:**
```bash
cd projects/week3/gaia-experience

# Create conda environment
conda create -n gaia-experience python=3.10
conda activate gaia-experience

# Install requirements
pip install -r requirements.txt
```

2. **Setup AWorld (if not already done):**
```bash
cd AWorld
python setup.py install
cd ..
```

3. **Configure environment variables:**
Create a `.env` file:
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-5.6-luna
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # Optional
# 兜底：若 LLM_API_KEY/OPENAI_API_KEY 都缺失但设了 OPENROUTER_API_KEY，自动走 OpenRouter（映射到 openai/gpt-5.6-luna 等）
# OPENROUTER_API_KEY=sk-or-...

# Dataset paths
GAIA_DATASET_PATH=./AWorld/examples/gaia/GAIA
AWORLD_WORKSPACE=./workspace
```

## 💡 Usage

### Basic Usage

#### 1. Run with Learning Mode
Capture and learn from successful trajectories:
```bash
python run_with_experience.py \
    --learning-mode \
    --start 0 --end 5 \
    --split validation
```

#### 2. Run with Experience Application
Apply learned experiences to new tasks:
```bash
python run_with_experience.py \
    --apply-experience \
    --preload-kb \
    --start 5 --end 10 \
    --split validation
```

#### 3. Combined Mode
Learn and apply experiences simultaneously:
```bash
python run_with_experience.py \
    --learning-mode \
    --apply-experience \
    --preload-kb \
    --start 0 --end 10
```

#### 4. A/B Comparison Mode
Evaluate the same tasks twice — once without experience, once with — and report the delta:
```bash
python run_with_experience.py --compare --start 10 --end 20 \
    --experience-db ./learned_experiences.json
```
See [A/B 对照实验](#-ab-对照实验reproduce-the-experiments-point) for the full workflow.

> The full Chinese `--help` (with runnable examples) is always available without
> installing the heavy stack: `python run_with_experience.py --help`.

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--learning-mode` | Enable learning from successful trajectories | False |
| `--apply-experience` | Apply learned experiences to new tasks | False |
| `--compare` | A/B mode: run the slice with **and** without experience, report accuracy delta | False |
| `--preload-kb` | Preload knowledge base from gaia-validation.jsonl (can leak answers, see below) | False |
| `--kb-path` | Path to store knowledge base index | ./kb_index |
| `--experience-db` | Path to store learned experiences | ./learned_experiences.json |
| `--validation-file` | Path to gaia-validation.jsonl | gaia-validation.jsonl |
| `--embedding-model` | Sentence transformer model | all-MiniLM-L6-v2 |
| `--summary-model` | Model for trajectory summarization | gpt-5.6-luna |
| `--model` | Main agent model (overrides `LLM_MODEL_NAME`) | env / gpt-5.6-luna |
| `--output` | Results JSON output path | `$AWORLD_WORKSPACE/experience_results.json` |
| `--start` | Start index of dataset | 0 |
| `--end` | End index of dataset | 20 |
| `--q` | Specific task ID to run | None |
| `--skip` | Skip tasks already present in the results file | False |
| `--split` | Dataset split (validation/test) | validation |
| `--blacklist_file_path` | Optional file of task_ids to skip | None |

### Demo Script

Run the interactive demo to explore all features:
```bash
# Run complete workflow demo
python demo.py

# Interactive mode
python demo.py --interactive

# Specific demos
python demo.py --kb          # Knowledge base demo
python demo.py --summarize   # Summarization demo
python demo.py --agent       # Agent demo
```

## 🔧 Configuration

The `config.yaml` file provides detailed configuration options:

### Key Configuration Sections:

1. **Learning Settings**
   - Summarizer model and temperature
   - Experience storage settings
   - Maximum trajectory steps

2. **Knowledge Base Settings**
   - Embedding model configuration
   - Search parameters (top-k, similarity threshold)
   - Index storage path

3. **Application Settings**
   - Experience incorporation strategy
   - Filtering criteria (by level, tools, recency)
   - Maximum experiences in prompt

## 📊 How It Works

### Learning Process

1. **Trajectory Capture**: After a task runs, the actual step-by-step trajectory (tools, actions, params) is read back from AWorld's `TaskResponse.trajectory` and normalized for the summarizer
2. **Success Detection**: When a task completes successfully, the trajectory is marked for learning
3. **Summarization**: The trajectory is analyzed by an LLM to extract:
   - High-level approach
   - Key insights and patterns
   - Tools used effectively
   - Generalizable strategies
4. **Storage**: The summarized experience is stored with the original question for retrieval

### Retrieval and Application

1. **Query Analysis**: New questions are analyzed for similarity to past experiences
2. **Semantic Search**: The knowledge base finds relevant experiences using embeddings
3. **Experience Selection**: Top-k most relevant experiences are selected
4. **Prompt Enhancement**: Selected experiences are formatted and added to the system prompt
5. **Execution**: The agent solves the task with the benefit of past experiences

### Knowledge Base Preloading

The system can preload the `gaia-validation.jsonl` file to bootstrap the knowledge base:
- Each entry is parsed for question, approach, and tools used
- Experiences are indexed using sentence embeddings
- Enables immediate access to a rich set of problem-solving patterns

## 📈 Performance Benefits

1. **Improved Success Rate**: Agents learn from past successes to avoid repeating mistakes
2. **Faster Problem Solving**: Relevant experiences guide the agent to efficient solutions
3. **Knowledge Transfer**: Experiences from similar problems apply to new challenges
4. **Reduced Token Usage**: Past insights can reduce exploration and trial-and-error

## 🧪 A/B 对照实验（reproduce the experiment's point）

本实验的核心命题是「**复用积累的经验能提升 GAIA 成绩**」。`--compare` 模式把这个命题变成一个
可运行、可复现的对照实验：对同一批题目跑两遍——一遍**关闭**经验复用（baseline），一遍**打开**
经验复用（with-experience）——并报告两者的准确率之差（delta）。

**推荐工作流（避免数据泄漏）：** 先在一批题上积累经验，再在**另一批未见过的题**上做对照。
直接对评测题 `--preload-kb` 会把这些题在 `gaia-validation.jsonl` 中的参考解法灌入知识库，
等于泄漏答案；脚本检测到该情况会打印告警。

```bash
# 1) 在第 0~10 题上积累经验（仅从成功轨迹中学习）
python run_with_experience.py --learning-mode --start 0 --end 10

# 2) 在第 10~20 题（未见过）上做 A/B 对照，复用第 1 步学到的经验
python run_with_experience.py --compare --start 10 --end 20 \
    --experience-db ./learned_experiences.json
#    或： ./run.sh learn --start 0 --end 10 && ./run.sh compare --start 10 --end 20
```

**输出**：控制台打印如下汇总，同时把每题明细写入 `comparison_results.json`（或 `--output` 指定路径）：

```
============================================================
A/B COMPARISON: experience reuse vs. baseline
============================================================
  Tasks evaluated       : <N>  (split=validation, range=[10, 20))
  Reusable experiences  : <M> learned, <K> preloaded
  Baseline accuracy     : <c1>/<N> = <p1>%
  With-experience acc.  : <c2>/<N> = <p2>%
  Delta (with - base)   : <p2 - p1>%
============================================================
```

**预期结果**：当经验库中确有与评测题相关的可迁移经验时，with-experience 的准确率应 **≥** baseline，
delta 为正——这正是「学习-应用闭环」带来的增益。所有数字均由 `question_scorer` 对真实运行结果计算得到，
脚本不写死任何成绩；若经验库为空或经验不相关，delta 可能为 0，属于正常现象（说明还没有可复用的相关经验）。

> ⚠️ 运行完整对照需要：可用的 LLAPI（`.env` 中的 `LLM_API_KEY` 等）、已安装的 AWorld（`pip install -e ./AWorld`）、
> `sentence-transformers` / `faiss-cpu` 依赖，以及 GAIA 数据集（`GAIA_DATASET_PATH`）。
> 若只想确认命令行可用，无需上述环境即可运行 `python run_with_experience.py --help`。

## 🔍 Example Experience

```json
{
  "question": "Find AI regulation paper from June 2022 on arXiv",
  "answer": "egalitarian",
  "summary": "Successfully located paper by using advanced search with date filters",
  "approach": "Web search → Navigate to arXiv → Use advanced search → Filter by date",
  "tools_used": ["web_search", "browser_navigate", "browser_click"],
  "key_insights": [
    "Advanced search provides better filtering options",
    "Date range queries need specific format",
    "Multiple searches refined the query"
  ]
}
```

## 🛠️ Extending the System

### Adding Custom Summarizers
Create a new summarizer by extending `TrajectorySummarizer`:
```python
class CustomSummarizer(TrajectorySummarizer):
    def _create_summary_prompt(self, question, answer, trajectory):
        # Custom prompt logic
        pass
```

### Custom Experience Filters
Add filtering logic in `ExperienceAgent._get_relevant_experiences()`:
```python
def filter_by_custom_criteria(experiences):
    # Custom filtering logic
    return filtered_experiences
```

### Alternative Embedding Models
Change the embedding model in configuration:
```yaml
knowledge_base:
  index:
    embedding_model: "all-mpnet-base-v2"  # Higher quality embeddings
    embedding_dim: 768  # Adjust dimension accordingly
```

## 📝 Notes

- The system requires API access to an LLM for summarization
- Embedding models are downloaded on first use (may take time)
- Knowledge base indexing is incremental and persistent
- Experiences are saved after each successful task

## 🤝 Contributing

Feel free to extend and improve the system:
- Add more sophisticated trajectory analysis
- Implement experience merging and evolution
- Add multi-agent experience sharing
- Enhance retrieval with hybrid search methods

## 📄 License

This project extends AWorld and follows its licensing terms.

## 🙏 Acknowledgments

- Built on top of the AWorld framework by inclusionAI
- Uses the GAIA benchmark for evaluation
- Leverages sentence-transformers for semantic search
