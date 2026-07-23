## English

# GAIA Experience Learning System

> Corresponds to Chapter 8 · Experiment 8-1 ★★ "Learning from Successful Experiences: Strategy Summarization" in *Deep Understanding of AI Agents*.
> This directory contains the top-level wrapper script for the experiment; `AWorld/` is a copy of the upstream framework — do not modify.

A modified version of AWorld that adds learning from experience capabilities for the GAIA benchmark. This system can capture successful task trajectories, summarize them into reusable experiences, and apply learned knowledge to improve performance on new tasks.

**Experiment highlights (why this matters)**: GAIA is a high-difficulty benchmark requiring multi-step reasoning and integrated use of browser/file/code interpreter tools.
This experiment demonstrates a "learn-apply" loop — each time an agent successfully solves a task, its trajectory is distilled into an experience and stored in a knowledge base. When encountering a new task, similar experiences are retrieved and injected into the prompt.
The hypothesis is: **Reusing accumulated experience improves GAIA performance**. Using `--compare`, you can run an A/B comparison on the same set of tasks to empirically test this hypothesis (see [A/B Comparison Experiment](#ab-comparison-experiment) below).

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

```text
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
# Fallback: if both LLM_API_KEY and OPENAI_API_KEY are missing but OPENROUTER_API_KEY is set, automatically use OpenRouter (mapped to openai/gpt-5.6-luna, etc.)
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
See [A/B Comparison Experiment](#ab-comparison-experiment) for the full workflow.

> The full Chinese `--help` (with runnable examples) is always available without
> installing the heavy stack: `python run_with_experience.py --help`.

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--learning-mode` | Enable learning from successful trajectories | False |
| `--apply-experience` | Apply learned experiences to new tasks | False |
| `--compare` | A/B mode: run the slice **with** and **without** experience, report accuracy delta | False |
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

### Key Configuration Sections

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

## A/B Comparison Experiment

The core hypothesis of this experiment is that **reusing accumulated experience improves GAIA scores**. The `--compare` mode turns this hypothesis into a runnable, reproducible controlled experiment: it runs the same set of questions twice—once with experience reuse **disabled** (baseline) and once with experience reuse **enabled** (with-experience)—and reports the difference in accuracy (delta) between the two.

**Recommended workflow (to avoid data leakage):** First accumulate experience on one batch of questions, then run the comparison on a **different, unseen batch** of questions. Directly using `--preload-kb` on the evaluation questions will inject the reference solutions from `gaia-validation.jsonl` into the knowledge base, which is equivalent to leaking the answers; the script will print a warning if it detects this situation.

```bash
# 1) Accumulate experience on questions 0-10 (learn only from successful trajectories)
python run_with_experience.py --learning-mode --start 0 --end 10

# 2) Run A/B comparison on questions 10-20 (unseen), reusing the experience learned in step 1
python run_with_experience.py --compare --start 10 --end 20 \
    --experience-db ./learned_experiences.json
#     Or: ./run.sh learn --start 0 --end 10 && ./run.sh compare --start 10 --end 20
```

**Output:** The console prints the following summary, while also writing per-question details to `comparison_results.json` (or a path specified by `--output`):

```text
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

**Expected results:** When the experience database contains transferable experiences relevant to the evaluation questions, the accuracy with experience should be **≥** the baseline and the delta should be non-negative; a positive delta indicates a gain from the "learn-apply loop." All numbers are computed by `question_scorer` from actual run results; the script does not hardcode any scores. If the experience database is empty or the experiences are irrelevant, the delta may be 0, which is normal (indicating no reusable relevant experience is available yet).

> ⚠️ Running the full comparison requires: a usable LLM API (`LLM_API_KEY` etc. in `.env`), an installed AWorld (`pip install -e ./AWorld`), the `sentence-transformers` / `faiss-cpu` dependencies, and the GAIA dataset (`GAIA_DATASET_PATH`). If you only want to verify that the command line works, you can run `python run_with_experience.py --help` without the above environment.

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

---

## 中文

# GAIA体验学习系统

> 对应*深入理解AI Agent*中的第8章·实验8-1 ★★“成功经验学习：策略总结”。
> 该目录包含实验的顶级包装脚本； `AWorld/` 是上游框架的副本 - 请勿修改。

AWorld 的修改版本，增加了针对 GAIA 基准的经验学习功能。该系统可以捕获成功的任务轨迹，将其总结为可重用的经验，并应用学到的知识来提高新任务的绩效。

**实验亮点（为什么这很重要）**：GAIA 是一个高难度的基准测试，需要多步骤推理和浏览器/文件/代码解释器工具的集成使用。
该实验演示了一个“学习-应用”循环——每次代理成功解决任务时，其轨迹都会被提炼成经验并存储在知识库中。当遇到新任务时，会检索相似的经验并将其注入到提示中。
假设是：**重用积累的经验可以提高 GAIA 的性能**。使用 `--compare`，您可以对同一组任务运行 A/B 比较，以凭经验检验该假设（请参阅下面的[A/B 比较实验](#ab-comparison-experiment)）。

## 🌟 特点

### 1. **从经验中学习**
- 捕获 AWorld 产生的**实际执行轨迹**（从
`TaskResponse.trajectory`) 当任务成功完成时
- 使用大语言模型将轨迹总结为自然语言体验
- 存储学到的经验（方法、关键见解、工具、步数）以供将来参考

### 2. **具有语义搜索的知识库**
- 索引 `gaia-validation.jsonl` 文件以获取预加载的体验
- 使用句子嵌入进行语义相似性搜索
- 支持语义检索和基于关键字的检索

### 3. **体验申请**
- 检索新查询的相关过去经验
- 增强系统提示相关体验
- 利用过去的成功经验提高任务绩效

## 📁 项目结构

```text
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

## 🚀 安装

### 先决条件
- Python 3.8+
- Conda（推荐用于环境管理）
- Node.js 22 LTS（用于 AWorld Web UI）

### 设置步骤

1. **克隆并设置环境：**
```bash
cd projects/week3/gaia-experience

# Create conda environment
conda create -n gaia-experience python=3.10
conda activate gaia-experience

# Install requirements
pip install -r requirements.txt
```

2. **设置 AWorld（如果尚未完成）：**
```bash
cd AWorld
python setup.py install
cd ..
```

3. **配置环境变量：**
创建 `.env` 文件：
```env
# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-5.6-luna
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # Optional
# Fallback: if both LLM_API_KEY and OPENAI_API_KEY are missing but OPENROUTER_API_KEY is set, automatically use OpenRouter (mapped to openai/gpt-5.6-luna, etc.)
# OPENROUTER_API_KEY=sk-or-...

# Dataset paths
GAIA_DATASET_PATH=./AWorld/examples/gaia/GAIA
AWORLD_WORKSPACE=./workspace
```

## 💡 用法

### 基本用法

#### 1. 以学习模式运行
捕捉成功轨迹并从中学习：
```bash
python run_with_experience.py \
    --learning-mode \
    --start 0 --end 5 \
    --split validation
```

#### 2. 运行体验应用程序
将学到的经验应用到新任务中：
```bash
python run_with_experience.py \
    --apply-experience \
    --preload-kb \
    --start 5 --end 10 \
    --split validation
```

#### 3. 组合模式
同时学习和应用经验：
```bash
python run_with_experience.py \
    --learning-mode \
    --apply-experience \
    --preload-kb \
    --start 0 --end 10
```

#### 4.A/B比较模式
对相同的任务进行两次评估——一次没有经验，一次有经验——并报告增量：
```bash
python run_with_experience.py --compare --start 10 --end 20 \
    --experience-db ./learned_experiences.json
```
请参阅[A/B 比较实验](#ab-comparison-experiment)了解完整的工作流程。

> 完整的中文 `--help`（带有可运行的示例）始终可用，无需
> 安装重型堆栈：`python run_with_experience.py --help`。

### 命令行参数

|论证|描述 |默认 |
|----------|-------------|---------|
| `--learning-mode` |能够从成功的轨迹中学习|假 |
| `--apply-experience` |将学到的经验应用到新任务中 |假 |
| `--compare` | A/B 模式：**有**和**没有**经验运行切片，报告准确度增量 |假 |
| `--preload-kb` |从 gaia-validation.jsonl 预加载知识库（可能泄漏答案，见下文）|假 |
| `--kb-path` |存储知识库索引的路径| ./kb_index |
| `--experience-db` |存储学到的经验的路径| ./learned_experiences.json |
| `--validation-file` | gaia-validation.jsonl 的路径 | gaia-validation.jsonl |
| `--embedding-model` |句子变压器模型| all-MiniLM-L6-v2 |
| `--summary-model` |轨迹总结模型| gpt-5.6-luna |
| `--model` |主代理模型（覆盖`LLM_MODEL_NAME`）|环境 / gpt-5.6-luna |
| `--output` |结果JSON输出路径| `$AWORLD_WORKSPACE/experience_results.json` |
| `--start` |数据集的起始索引 | 0 |
| `--end` |数据集结束索引 | 20 |
| `--q` |要运行的特定任务 ID |无 |
| `--skip` |跳过结果文件中已存在的任务 |假 |
| `--split` |数据集分割（验证/测试）|验证 |
| `--blacklist_file_path` |要跳过的 task_ids 可选文件 |无 |

### 演示脚本

运行交互式演示以探索所有功能：
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

## 🔧 配置

`config.yaml` 文件提供了详细的配置选项：

### 关键配置部分

1. **学习设置**
- Summarizer型号和温度
- 体验存储设置
- 最大轨迹步数

2. **知识库设置**
- 嵌入模型配置
- 搜索参数（top-k，相似度阈值）
- 索引存储路径

3. **应用程序设置**
- 经验整合策略
- 过滤标准（按级别、工具、新近度）
- 提示中的最大体验

## 📊 它是如何运作的

### 学习过程

1. **轨迹捕获**：任务运行后，从 AWorld 的 `TaskResponse.trajectory` 读回实际的逐步轨迹（工具、操作、参数）并为摘要器进行标准化
2. **成功检测**：当任务成功完成时，轨迹被标记用于学习
3. **总结**：由LLM分析轨迹以提取：
- 高层方法
- 关键见解和模式
- 有效使用工具
- 通用策略
4. **存储**：总结的经验与原始问题一起存储以供检索

### 检索与应用

1. **查询分析**：分析新问题与过去经验的相似性
2. **语义搜索**：知识库使用嵌入查找相关经验
3. **经验选择**：选择Top-k最相关的经验
4. **提示增强**：选定的体验被格式化并添加到系统提示中
5. **执行**：代理利用过去的经验来解决任务

### 知识库预加载

系统可以预加载`gaia-validation.jsonl`文件来引导知识库：
- 每个条目都会针对问题、方法和使用的工具进行解析
- 使用句子嵌入对经验进行索引
- 可以立即访问一组丰富的问题解决模式

## 📈 性能优势

1. **提高成功率**：代理从过去的成功中学习以避免重复错误
2. **更快解决问题**：相关经验指导座席高效解决问题
3. **知识转移**：类似问题的经验适用于新的挑战
4. **减少代币使用**：过去的见解可以减少探索和试错

## 🧪 A/B 对照实验（重现实验要点）

这个实验的核心假设是**重用积累的经验可以提高 GAIA 分数**。 `--compare` 模式将此假设转化为可运行、可重复的受控实验：它运行同一组问题两次，一次是经验重用**禁用**（基线），一次是经验重用**启用**（有经验），并报告两者之间的准确度差异（增量）。

**推荐的工作流程（以避免数据泄漏）：**首先积累一批问题的经验，然后对**不同的、看不见的批次**问题进行比较。直接在评估题上使用`--preload-kb`，会将`gaia-validation.jsonl`中的参考解注入到知识库中，相当于泄露答案；如果脚本检测到这种情况，它将打印一条警告。

```bash
# 1) Accumulate experience on questions 0-10 (learn only from successful trajectories)
python run_with_experience.py --learning-mode --start 0 --end 10

# 2) Run A/B comparison on questions 10-20 (unseen), reusing the experience learned in step 1
python run_with_experience.py --compare --start 10 --end 20 \
    --experience-db ./learned_experiences.json
#     Or: ./run.sh learn --start 0 --end 10 && ./run.sh compare --start 10 --end 20
```

**输出：** 控制台打印以下摘要，同时还将每个问题的详细信息写入 `comparison_results.json` （或 `--output` 指定的路径）：

```text
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

**预期结果：**当经验数据库包含与评估问题相关的可转移经验时，经验的准确性应**≥**基线，且增量应为非负；正增量表示“学习-应用循环”带来了提升。所有数字均由`question_scorer`根据实际运行结果计算得出；该脚本不会对任何分数进行硬编码。如果经验数据库为空或者经验不相关，则增量可能为0，这是正常的（表示还没有可重用的相关经验）。

> ⚠️ 运行完整比较需要：可用的 LLM API（`.env` 中的 `LLM_API_KEY` 等）、已安装的 AWorld (`pip install -e ./AWorld`)、`sentence-transformers` / `faiss-cpu` 依赖项以及 GAIA 数据集 (`GAIA_DATASET_PATH`)。如果您只想验证命令行是否有效，可以在没有上述环境的情况下运行`python run_with_experience.py --help`。

## 🔍 经验示例

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

## 🛠️ 扩展系统

### 添加自定义摘要器
通过扩展 `TrajectorySummarizer` 创建一个新的摘要器：
```python
class CustomSummarizer(TrajectorySummarizer):
    def _create_summary_prompt(self, question, answer, trajectory):
        # Custom prompt logic
        pass
```

### 自定义体验过滤器
在`ExperienceAgent._get_relevant_experiences()`中添加过滤逻辑：
```python
def filter_by_custom_criteria(experiences):
    # Custom filtering logic
    return filtered_experiences
```

### 替代嵌入模型
更改配置中的嵌入模型：
```yaml
knowledge_base:
  index:
    embedding_model: "all-mpnet-base-v2"  # Higher quality embeddings
    embedding_dim: 768  # Adjust dimension accordingly
```

## 📝 注释

- 系统需要 API 访问 LLM 进行总结
- 首次使用时下载嵌入模型（可能需要时间）
- 知识库索引是增量且持久的
- 每次成功任务后都会保存经验

## 🤝 贡献

随意扩展和改进系统：
- 添加更复杂的轨迹分析
- 实施经验融合和进化
- 新增多代理经验分享
- 通过混合搜索方法增强检索

## 📄 许可证

该项目扩展了 AWorld 并遵循其许可条款。

## 🙏致谢

- 由inclusionAI建立在AWorld框架之上
- 使用GAIA基准进行评估
- 利用句子转换器进行语义搜索
