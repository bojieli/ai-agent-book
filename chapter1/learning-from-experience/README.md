# Learning from Experience: RL vs LLM In-Context Learning

This experiment compares traditional Reinforcement Learning (Q-learning) with LLM-based in-context learning, replicating the key insights from Shunyu Yao's blog post ["The Second Half"](https://ysymyth.github.io/The-Second-Half/).

## 🎯 Experiment Overview

The experiment demonstrates how LLMs can generalize through reasoning while traditional RL methods require extensive training to learn game mechanics. We use a text-based treasure hunt game with hidden mechanics that agents must discover through experience.

### Key Insights Being Tested

1. **Sample Efficiency**: LLMs can learn from far fewer examples than traditional RL
2. **Generalization**: LLMs use reasoning to understand patterns, while RL memorizes state-action mappings
3. **Prior Knowledge**: Language pre-training provides powerful priors for reasoning about new tasks
4. **Hidden Mechanics Discovery**: LLMs can form hypotheses and test them, while RL requires exhaustive exploration

### What You'll See

When running the LLM experiment, you'll see the **complete decision-making process**:

```
============================================================
LLM DECISION PROCESS
============================================================
📊 Experiences in memory: 15
🎮 Current room: hallway
🎯 Available actions: 8

💡 Recent successful patterns learned:
   • take red key → +5.0 reward
   • try crafting → +10.0 reward

🤔 LLM is thinking...

📝 LLM Reasoning:
----------------------------------------
  Based on my past experiences, I've learned that:
  1. The red key opens the locked door to the guard room
  2. Crafting rusty sword + magic crystal creates a silver sword
  3. The silver sword can defeat the strong guard
  
  Since I have the silver sword and I'm in the hallway...
----------------------------------------

✅ Chosen action: go north
```

This transparency shows exactly how the LLM learns and reasons, unlike the black-box nature of Q-learning!

## 🎮 The Game

A text-based treasure hunt game where agents must:
- Navigate through multiple rooms
- Collect items and keys
- Defeat guards using appropriate weapons
- Discover hidden mechanics through experience

### Hidden Mechanics (Not Revealed to Agents)

1. **Color-coded locks**: Specific colored keys open matching doors
2. **Weapon effectiveness**: Different weapons work against different enemies
3. **Crafting system**: Certain items combine to create better items
4. **Potion effects**: Temporary abilities from consuming potions

## 🚀 Quick Start

### Installation

```bash
# Navigate to the project directory
cd projects/week1/learning-from-experience

# Install dependencies
pip install -r requirements.txt
```

### Setting up Kimi K2 API

To run the LLM experiments, you need a Kimi (Moonshot) API key:

1. Get your API key from [Moonshot AI](https://platform.moonshot.cn/)
2. Set the environment variable:

```bash
export MOONSHOT_API_KEY="your-api-key-here"
```

Or create a `.env` file:
```bash
echo "MOONSHOT_API_KEY=your-api-key-here" > .env
```

### Running the Experiment

#### Quick Demo (See LLM Learning in Action)

```bash
python quick_demo.py
```

This shows a detailed view of how the LLM learns through reasoning, displaying:
- Complete thought process for each decision
- How experiences accumulate and influence future decisions
- The dramatic difference in learning speed vs traditional RL

#### Full Comparison (RL vs LLM)

```bash
python experiment.py
```

This will:
1. Train a Q-learning agent for 5000 episodes (takes ~3 seconds)
2. Train an LLM agent for 20 episodes with detailed reasoning display
3. Evaluate both agents
4. Generate comparison plots
5. Save results to the `results/` directory

**Note**: The LLM training shows the complete reasoning process for the first 3 episodes and the last episode, so you can see exactly how it learns!

#### Custom Parameters

```bash
# Adjust episode counts
python experiment.py --rl-episodes 10000 --llm-episodes 30

# Show detailed training output
python experiment.py --verbose

# Run only RL experiment (if no API key)
python experiment.py --skip-llm
```

#### Interactive Game Play

Test the game manually:

```python
from game_environment import TreasureHuntGame

game = TreasureHuntGame()
print(game.get_state_description())
print("Available actions:", game.get_available_actions())

# Try an action
feedback, reward, done = game.execute_action("take rusty sword")
print(f"Feedback: {feedback}")
print(f"Reward: {reward}")
```

## 📊 Experiment Results

The experiment generates several outputs:

### Metrics Compared

1. **Sample Efficiency**
   - Episodes needed to achieve good performance
   - Learning speed comparison

2. **Performance**
   - Victory rate in evaluation
   - Average rewards and episode lengths

3. **Computational Cost**
   - Training time
   - Memory usage (Q-table size vs. experience storage)
   - API calls for LLM

### Visualizations

The experiment creates comparison plots showing:
- Learning curves over time
- Victory rate progression
- Sample efficiency comparison
- Key insights summary

### Expected Results

Based on "The Second Half" insights and our testing:

- **Q-Learning**: 
  - Needs ~7000-8000 episodes to achieve consistent victories
  - 100% victory rate after 10,000 episodes
  - Learns through trial and error, memorizing state-action pairs
  
- **LLM In-Context**: 
  - Often solves the game within 5-10 episodes
  - Achieves 50-80% victory rate with just 20 episodes
  - Learns by reasoning about patterns and forming hypotheses
  
- **Sample Efficiency**: 
  - LLM is **250-400x more sample efficient**
  - LLM uses reasoning to generalize from few examples
  - Q-learning requires exhaustive exploration

## 🏗️ Project Structure

```
learning-from-experience/
├── game_environment.py    # Text-based game with hidden mechanics
├── rl_agent.py            # Q-learning implementation
├── llm_agent.py           # LLM with in-context learning
├── experiment.py          # Main experiment runner
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── results/              # Experiment outputs (created on run)
    └── [timestamp]/
        ├── rl_agent.pkl           # Trained Q-learning agent
        ├── llm_experiences.json   # LLM's collected experiences
        ├── experiment_results.json # Numerical results
        └── comparison_plots.png   # Visualization
```

## 🔬 Technical Details

### Q-Learning Agent

- **Algorithm**: Tabular Q-learning with ε-greedy exploration
- **State Representation**: Hashed combination of room, inventory, and game state
- **Learning Rate**: 0.1 (configurable)
- **Discount Factor**: 0.95
- **Exploration**: ε starts at 1.0, decays to 0.01

### LLM Agent (Kimi K2)

- **Model**: Moonshot-v1-auto (Kimi K2)
- **Learning Method**: In-context learning with experience memory
- **Context Management**: Stores successful and failed experiences
- **Reasoning**: Prompts LLM to reason about past experiences before acting
- **Temperature**: 0.7 for balanced exploration/exploitation

## 📈 Extending the Experiment

### Ideas for Further Research

1. **Different Games**: Try other hidden-mechanic games
2. **Hybrid Approaches**: Combine RL with LLM guidance
3. **Transfer Learning**: Test how well agents transfer to similar games
4. **Ablation Studies**: Remove reasoning prompts to isolate their impact
5. **Other LLMs**: Compare different language models

### Modifying the Game

Edit `game_environment.py` to:
- Add new rooms and items
- Create more complex hidden mechanics
- Adjust difficulty and rewards
- Add new types of puzzles

## 🎓 Educational Value

This experiment demonstrates:

1. **The Power of Priors**: How language pre-training provides useful knowledge
2. **Reasoning vs. Memorization**: Different approaches to learning
3. **Sample Efficiency**: Why it matters for real-world applications
4. **The Second Half Thesis**: Moving from "can we solve it?" to "how efficiently?"

## 📚 References

- [The Second Half](https://ysymyth.github.io/The-Second-Half/) by Shunyu Yao
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- Original Q-learning paper: Watkins & Dayan (1992)

## 🤝 Contributing

Feel free to:
- Add new hidden mechanics to the game
- Implement other RL algorithms (DQN, PPO, etc.)
- Try different LLM providers
- Create more sophisticated evaluation metrics

## 📝 License

This project is for educational purposes, inspired by academic research on AI and reinforcement learning.
