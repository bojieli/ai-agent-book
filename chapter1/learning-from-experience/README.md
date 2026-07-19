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
cd chapter1/learning-from-experience

# Install dependencies
pip install -r requirements.txt
```

> 对应书中**实验 7-1（Q-learning 在寻宝游戏中的表现）**与**实验 7-2（传统 RL 与 LLM Agent 的对比研究）**。
> Q-learning 部分完全离线运行、无需任何 API Key；LLM 部分需要 Moonshot/Kimi API Key。

### Setting up Kimi K3 API

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

**通用兜底（OpenRouter）**：若未设置 `MOONSHOT_API_KEY` 但设置了 `OPENROUTER_API_KEY`，
LLM 部分会自动改走 OpenRouter。由于 Kimi 模型在 OpenRouter 上不稳定可用，兜底时会使用
`OPENROUTER_MODEL`（默认 `openai/gpt-5.6-luna`）：
```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
python quick_demo.py   # MOONSHOT_API_KEY 缺失时自动经 OpenRouter 运行
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

#### Command-Line Interface (`experiment.py`)

`experiment.py` 现在提供带中文帮助的完整 CLI。查看所有参数：

```bash
python experiment.py --help
```

主要参数：

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `--mode {both,qlearning,rl,llm}` | 运行哪种智能体：`qlearning`/`rl` 只跑 Q-learning（离线）、`llm` 只跑 LLM Agent、`both` 两者对比 | `both` |
| `--rl-episodes` | Q-learning 训练局数（实验 7-1 用 10000） | `10000` |
| `--llm-episodes` | LLM Agent 训练局数 | `20` |
| `--eval-episodes` | Q-learning 训练后贪婪评估局数 | `100` |
| `--checkpoint-interval` | 学习曲线采样间隔（每 N 局记录一次胜率/Q 表规模） | `1000` |
| `--model` | LLM 模型名（也可用 `MOONSHOT_MODEL` 环境变量） | `kimi-k3` |
| `--output` | 结果输出目录 | `results` |
| `--seed` | 随机种子，用于复现 Q-learning 学习曲线 | 不固定 |
| `--learning-rate` / `--discount` / `--epsilon-decay` / `--epsilon-min` | Q-learning 超参数 | `0.2 / 0.99 / 0.9995 / 0.1` |
| `--stochastic` | 使用随机环境 | 确定性 |
| `--skip-llm` | 兼容旧用法，等价于 `--mode qlearning` | — |

#### Q-Learning Only (实验 7-1，离线，无需 API)

```bash
python experiment.py --mode qlearning --rl-episodes 10000 --seed 42
```

训练不到 3 秒即可完成，并打印**学习曲线表格**，直观展现智能体如何在近万局试错中从
0% 胜率逐步学会通关（见下方"Experiment Results"）。

#### Full Comparison (RL vs LLM，实验 7-2)

```bash
python experiment.py --mode both --model kimi-k3
```

This will:
1. Train a Q-learning agent for 10000 episodes (takes ~3 seconds) and print its learning curve
2. Train an LLM agent for 20 episodes with detailed reasoning display
3. Evaluate both agents
4. Generate comparison plots
5. Save results to the `results/` directory

**Note**: The LLM training shows the complete reasoning process for the first 3 episodes and the last episode, so you can see exactly how it learns! Each LLM episode takes ~1-2 minutes (real API calls), matching the cost trade-off discussed in 实验 7-2.

#### LLM Only

```bash
python experiment.py --mode llm --llm-episodes 20
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

#### Q-Learning learning curve (measured locally, `--mode qlearning --rl-episodes 10000 --seed 42`)

实测学习曲线（确定性环境，胜率按最近 1000 局滑动窗口统计，整段训练约 3 秒）：

| Episodes | Victory rate | Q-table states | epsilon |
| ---: | ---: | ---: | ---: |
| 1000 | 0.1% | 124 | 0.606 |
| 2000 | 0.0% | 129 | 0.368 |
| 3000 | 0.0% | 130 | 0.223 |
| 5000 | 0.0% | 132 | 0.100 |
| 7000 | 0.0% | 138 | 0.100 |
| 8000 | 0.0% | 140 | 0.100 |
| 9000 | 9.3% | 143 | 0.100 |
| 10000 | **99.8%** | 143 | 0.100 |

训练后贪婪评估（`--eval-episodes 100`）胜率为 **100%**，平均 15 步通关。这正是实验 7-1
的核心现象：前 8000 局几乎 0% 胜率、只在盲目探索，价值信号需要近万局试错才传播到位。
（因随机探索有方差，未固定 `--seed` 时各次运行的拐点会略有不同，但整体形态一致。）

#### RL vs LLM（实验 7-2 的对比结论）

- **Q-Learning**: 需要近 10000 局才达到稳定通关；把"门/钥匙/剑"当作无意义符号，只能靠统计式暴力探索。
- **LLM In-Context**: 携带预训练先验，往往第一局就能在十几步内通关；靠推理理解游戏概念结构。
- **Sample Efficiency**: LLM 的样本效率高出 2-3 个数量级；但单局推理慢（API 调用 ~1-2 分钟），
  Q-learning 跑 10000 局只需约 3 秒——权衡取决于交互成本，详见书中实验 7-2。

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
- **Learning Rate**: 0.2 (configurable via `--learning-rate`)
- **Discount Factor**: 0.99 (configurable via `--discount`)
- **Exploration**: ε starts at 1.0, decays by `--epsilon-decay` (0.9995) to `--epsilon-min` (0.1)

### LLM Agent (Kimi K3)

- **Model**: `kimi-k3` (Kimi K3; override with `--model` or `MOONSHOT_MODEL`)
- **Reasoning model**: Kimi K3 emits a chain-of-thought (`message.reasoning_content`) before its
  final answer (`message.content`), so the code uses a generous `max_tokens=2048` to make sure the
  `ACTION:` line is not truncated by the reasoning budget.
- **Learning Method**: In-context learning with experience memory (up to 50 experiences)
- **Context Management**: Stores successful and failed experiences
- **Reasoning**: Prompts LLM to reason about past experiences before acting
- **Temperature**: requested 0.7, but reasoning models (Kimi K3, GPT-5) only accept
  `temperature=1`, so the code auto-forces `1` for those (see `_reasoning_safe_temperature`)

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
