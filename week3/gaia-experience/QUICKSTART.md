# Quick Start Guide - GAIA Experience Learning System

## 🚀 5-Minute Setup

### 1. Prerequisites Check
```bash
# Check Python (3.8+ required)
python --version

# Check pip
pip --version
```

### 2. Quick Install
```bash
# Clone if not already done
cd projects/week3/gaia-experience

# Install dependencies
pip install -r requirements.txt

# Setup AWorld (if needed)
cd AWorld && python setup.py install && cd ..
```

### 3. Configure API Keys
```bash
# Copy environment template
cp env.template .env

# Edit .env and add your OpenAI API key
# LLM_API_KEY=sk-your-key-here
```

### 4. Run Your First Demo
```bash
# Run the interactive demo
python demo.py

# Or use the shell script
./run.sh demo
```

## 📊 Quick Examples

### Example 1: Index Existing Knowledge
```bash
# Index the GAIA validation dataset
./run.sh index

# This creates a searchable knowledge base from gaia-validation.jsonl
```

### Example 2: Learn from Tasks
```bash
# Process first 5 tasks and learn from successes
./run.sh learn --start 0 --end 5

# Check learned experiences
ls experiences/
cat experiences/learned_experiences.json
```

### Example 3: Apply Learned Knowledge
```bash
# Use learned experiences on new tasks
./run.sh apply --start 5 --end 10

# This will:
# - Load past experiences
# - Find relevant ones for each new task
# - Add them to the prompt for better performance
```

### Example 4: Full Learning Loop
```bash
# Learn and apply simultaneously
./run.sh full --start 0 --end 20

# This enables both:
# - Learning from new successes
# - Applying past experiences
```

## 🎯 Common Use Cases

### Use Case 1: Bootstrap with Validation Data
```python
from knowledge_base import KnowledgeBase

kb = KnowledgeBase()
kb.index_gaia_validation('gaia-validation.jsonl')

# Now search for similar problems
results = kb.search("How to find papers on arXiv?", top_k=3)
for r in results:
    print(f"Q: {r['question'][:100]}...")
    print(f"A: {r['approach'][:100]}...")
```

### Use Case 2: Custom Task with Learning
```python
from experience_agent import ExperienceAgent
from AWorld.aworld.config.conf import AgentConfig, TaskConfig
from AWorld.aworld.core.task import Task
import asyncio

async def run_custom_task():
    # Setup agent with learning
    config = AgentConfig(
        llm_provider="openai",
        llm_model_name="gpt-4o",
        llm_api_key="your-key"
    )
    
    agent = ExperienceAgent(
        conf=config,
        learning_mode=True,
        apply_experience=True
    )
    
    # Create and run task
    task = Task(
        input="What is the capital of France?",
        agent=agent,
        conf=TaskConfig()
    )
    
    response = await agent.execute_task(task)
    print(f"Answer: {response.answer}")

asyncio.run(run_custom_task())
```

## 📝 Quick Tips

### Tip 1: Check Logs
```bash
# View latest logs
tail -f workspace/experience_agent_*.log

# Check for errors
grep ERROR workspace/*.log
```

### Tip 2: Monitor Learning
```bash
# Watch experiences being added
watch -n 5 'wc -l experiences/learned_experiences.json'
```

### Tip 3: Test Specific Task
```bash
# Run a specific task by ID
./run.sh test --task-id "c61d22de-5f6c-4958-a7f6-5e9707bd3466"
```

### Tip 4: Reset and Start Fresh
```bash
# Clear all learned experiences and indices
rm -rf kb_index/ experiences/ workspace/
mkdir -p kb_index experiences workspace

# Start fresh
./run.sh full
```

## ⚡ Performance Tips

1. **Batch Processing**: Process multiple questions at once for efficiency
   ```bash
   ./run.sh full --start 0 --end 50
   ```

2. **Preload Knowledge**: Always preload for better initial performance
   ```bash
   ./run.sh apply --preload-kb
   ```

3. **Use Appropriate Models**: 
   - Main agent: `gpt-4o` for complex reasoning
   - Summarization: `gpt-4o-mini` for cost efficiency

4. **Monitor Token Usage**: Check logs for token consumption
   ```bash
   grep "tokens" workspace/*.log
   ```

## 🔍 Troubleshooting

### Issue: "API key not found"
**Solution**: Ensure `.env` file exists and contains valid `LLM_API_KEY`

### Issue: "Module not found"
**Solution**: Install requirements: `pip install -r requirements.txt`

### Issue: "AWorld not found"
**Solution**: Install AWorld: `cd AWorld && python setup.py install`

### Issue: "Knowledge base empty"
**Solution**: Index validation data: `./run.sh index`

## 📚 Next Steps

1. Read the full [README.md](README.md) for detailed documentation
2. Explore [config.yaml](config.yaml) for advanced configuration
3. Check [demo.py](demo.py) for programmatic examples
4. Review the [GAIA benchmark](https://huggingface.co/gaia-benchmark) for context

## 🆘 Getting Help

- Check logs in `workspace/` directory
- Review error messages carefully
- Ensure all prerequisites are met
- Verify API keys are correct

Happy Learning! 🎉
