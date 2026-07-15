# GAIA Experience Learning System

A modified version of AWorld that adds learning from experience capabilities for the GAIA benchmark. This system can capture successful task trajectories, summarize them into reusable experiences, and apply learned knowledge to improve performance on new tasks.

## 🌟 Features

### 1. **Learning from Experience**
- Captures execution trajectories when tasks are completed successfully
- Uses LLM to summarize trajectories into natural language experiences
- Stores learned experiences for future reference

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
LLM_MODEL_NAME=gpt-4o
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com/v1  # Optional

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

### Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--learning-mode` | Enable learning from successful trajectories | False |
| `--apply-experience` | Apply learned experiences to new tasks | False |
| `--preload-kb` | Preload knowledge base from gaia-validation.jsonl | False |
| `--kb-path` | Path to store knowledge base index | ./kb_index |
| `--experience-db` | Path to store learned experiences | ./learned_experiences.json |
| `--validation-file` | Path to gaia-validation.jsonl | gaia-validation.jsonl |
| `--embedding-model` | Sentence transformer model | all-MiniLM-L6-v2 |
| `--summary-model` | Model for trajectory summarization | gpt-4o-mini |
| `--start` | Start index of dataset | 0 |
| `--end` | End index of dataset | 20 |
| `--q` | Specific task ID to run | None |
| `--split` | Dataset split (validation/test) | validation |

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

1. **Trajectory Capture**: During task execution, all actions and their parameters are recorded
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
