# System-Hint Enhanced AI Agent

> 对应书中 **实验 2-8：几种好用的 Agent 状态栏技术**（第二章“Agent 状态栏 / Agent Status Bar”一节）。本目录即书中所说的 `agent-status-bar` 实验框架——“system hint（系统提示）”与“Agent 状态栏（status bar）”是同一概念的两种叫法：在上下文末尾以一条 `role=user` 的消息注入动态状态摘要。

An advanced AI agent that demonstrates the power of system hints for improving agent trajectory and preventing common issues like infinite loops, poor context awareness, and inefficient task management, with automatic trajectory saving for debugging.

## ⚡ 先跑离线预览（无需 API Key）

想在不配置任何 API Key 的情况下直观看到状态栏如何改变模型看到的上下文，运行：

```bash
python main.py --mode preview
```

该命令在本地渲染书中五种状态栏技术（时间戳、工具调用计数器、TODO 列表、详细错误信息、系统状态感知），
对每一项做一次 **“无状态栏 vs 有状态栏”** 的前后对比，并打印最终追加到上下文末尾的完整状态栏消息。
配合 `--no-timestamps` / `--no-counter` / `--no-todo` / `--no-errors` / `--no-state` 可分别关闭某一类，
单独观察它对上下文的影响。整个过程不发起任何 LLM 调用。

## 🌟 Key Features

### 1. **Timestamp Tracking**
- Adds timestamps to user messages and tool call results
- Helps the agent understand temporal context
- Simulates time delays for realistic multi-day scenarios

### 2. **Tool Call Counter**
- Tracks how many times each tool has been called
- Prevents infinite loops and repetitive behavior
- Shows call number in tool responses (e.g., "Tool call #3 for 'read_file'")

### 3. **TODO List Management**
- Built-in task tracking system with management rules in system prompt
- Four states: pending, in_progress, completed, cancelled
- Persistent across conversation with rewrite and update capabilities
- Agent automatically creates TODO lists for complex tasks (3+ steps)
- Helps maintain focus and track progress systematically

### 4. **Detailed Error Messages**
- Provides comprehensive error information instead of generic messages
- Includes error type, arguments, traceback (in verbose mode)
- Offers suggestions for fixing common errors
- Helps agent learn from failures and adapt strategies

### 5. **System State Awareness**
- Tracks current directory, shell environment, and system information
- Updates dynamically as agent navigates filesystem
- Provides context for command execution

### 6. **Automatic Trajectory Saving**
- Saves full conversation history and state to `trajectory.json` after each iteration
- Captures complete debugging information even if execution fails
- Includes conversation history, tool calls, TODO lists, and configuration
- Provides `view_trajectory.py` utility for analyzing saved trajectories

## 🚀 Quick Start

### Installation

```bash
# Clone the repository (if not already done)
cd chapter2/system-hint

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment
cp env.example .env
# Edit .env with your KIMI_API_KEY
export KIMI_API_KEY='your-api-key-here'
```

> **通用回退（OpenRouter）**：未设置 `KIMI_API_KEY` 时，只要配置了
> `OPENROUTER_API_KEY`，实验会自动改走 OpenRouter（`kimi-*` 会映射为
> `moonshotai/kimi-k2`）。设置了 `KIMI_API_KEY` 时行为完全不变。

### Basic Usage

```bash
# Offline preview of the status bar (no API key required)
python main.py --mode preview

# Interactive mode (default)
python main.py

# Run the sample task (analyze week1/week2 projects)
python main.py --mode sample

# Execute a single task from command line
python main.py --mode single --task "Create a hello world Python script"

# Override provider / model, and choose the trajectory output file
python main.py --mode single --task "..." --provider kimi --model kimi-k3 --output run1.json

# Run demonstrations
python main.py --mode demo --demo basic
python main.py --mode demo --demo loop
python main.py --mode demo --demo comparison

# Disable specific features (works for both preview and live modes)
python main.py --mode single --no-todo --no-timestamps --task "Simple task"
# Or observe the effect offline (no API key):
python main.py --mode preview --no-todo --no-timestamps

# Quick start with sample task
python quickstart.py

# View saved trajectory after running any task
python view_trajectory.py

# View a specific trajectory file
python view_trajectory.py path/to/trajectory.json
```

### Programmatic Usage

```python
from agent import SystemHintAgent, SystemHintConfig

# Configure system hints
config = SystemHintConfig(
    enable_timestamps=True,
    enable_tool_counter=True,
    enable_todo_list=True,
    enable_detailed_errors=True,
    enable_system_state=True,
    save_trajectory=True,
    trajectory_file="my_trajectory.json"
)

# Create agent
agent = SystemHintAgent(
    api_key="your-api-key",
    provider="kimi",
    config=config,
    verbose=False
)

# Execute task
task = "Create a Python script that analyzes CSV files"
result = agent.execute_task(task, max_iterations=20)

print(f"Success: {result['success']}")
print(f"Final answer: {result['final_answer']}")
print(f"Trajectory saved to: {result['trajectory_file']}")
```

## 📂 Project Structure

```
system-hint/
├── agent.py          # Main agent implementation with system hints
├── main.py           # CLI interface with multiple modes
├── config.py         # Configuration management
├── quickstart.py     # Quick demo script
├── test_basic.py     # Basic tests
├── test_hint_behavior.py # System-hint behavior tests
├── view_trajectory.py # Trajectory viewing utility
├── requirements.txt  # Python dependencies
├── env.example       # Environment variable template
├── trajectory.json   # Auto-saved trajectory (created at runtime)
├── CHANGELOG.md      # Change log
├── NOTES.md          # Design notes
└── README.md        # This file
```

## 🔬 How System Hints Work

### System Hint Architecture

System hints are contextual information added to the conversation **as temporary user messages** before sending to the LLM. They are NOT stored in the conversation history, preventing context pollution while providing crucial state information.

```python
# System hint example (added as user message before LLM call):
=== SYSTEM STATE ===
Current Time: 2024-12-13 10:30:45
Current Directory: /home/user/projects
System: Linux (5.15.0)
Shell Environment: Linux Shell (bash)
Python Version: 3.10.0

=== CURRENT TASKS ===
TODO List:
  [1] 🔄 Read configuration file (in_progress)
  [2] ⏳ Process data (pending)
  [3] ✅ Initialize environment (completed)
```

### Management Rules in System Prompt

The system prompt includes explicit rules for TODO management, error handling, and tool usage patterns that guide the agent's behavior:

- Automatic TODO list creation for complex tasks
- Status management (only one in_progress at a time)
- Tool call awareness (check call numbers)
- Error recovery strategies

## 🛠 Configuration Options

### SystemHintConfig Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_timestamps` | `True` | Add timestamps to messages |
| `enable_tool_counter` | `True` | Track tool call counts |
| `enable_todo_list` | `True` | Enable TODO list management |
| `enable_detailed_errors` | `True` | Provide detailed error information |
| `enable_system_state` | `True` | Track system state |
| `timestamp_format` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format string |
| `simulate_time_delay` | `False` | Simulate time passing (demo) |
| `save_trajectory` | `True` | Save trajectory to file |
| `trajectory_file` | `"trajectory.json"` | Trajectory output file |

## 🔍 Demonstrations

### 0. Offline Status-Bar Preview (no API key)

Renders the five status-bar techniques as before/after comparisons, entirely offline:
```bash
python main.py --mode preview
```

### 1. Basic Features Demo

Shows all system hints working together:
```bash
python main.py --mode demo --demo basic
```

### 2. Loop Prevention Demo

Demonstrates how tool call counting prevents infinite loops:
```bash
python main.py --mode demo --demo loop
```

### 3. Comparison Demo

Shows the difference between with and without system hints:
```bash
python main.py --mode demo --demo comparison
```

## 🎯 Sample Tasks

The agent includes several pre-configured sample tasks:

1. **Project Analysis** - Analyze week1/week2 AI agent projects
2. **File Operations** - Create, read, and modify files
3. **Code Generation** - Generate Python scripts with specific functionality
4. **System Commands** - Execute shell commands and process results

## 📊 Analyzing Results

### Viewing Trajectories

After running any task, use the trajectory viewer:

```bash
python view_trajectory.py

# Output shows:
# - Total iterations
# - Tool usage statistics
# - TODO list progress
# - Conversation highlights
# - Configuration used
```

### Performance Metrics

The agent tracks:
- Number of iterations needed
- Tool calls made (with success/failure rates)
- TODO completion status
- Time taken (when timestamps enabled)
- Final success/failure state

## 🧪 Testing

```bash
# Run basic tests
python test_basic.py

# Test specific configurations
python -c "
from agent import SystemHintAgent, SystemHintConfig
config = SystemHintConfig(enable_todo_list=False)
agent = SystemHintAgent('api_key', config=config)
# Test without TODO lists
"
```

## 🔧 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```bash
   export KIMI_API_KEY='your-api-key-here'
   ```

2. **Tool Call Loops**
   - Enable tool counter: `enable_tool_counter=True`
   - Check tool call numbers in output

3. **Lost Context**
   - Enable timestamps: `enable_timestamps=True`
   - Enable system state: `enable_system_state=True`

4. **Task Management Issues**
   - Enable TODO list: `enable_todo_list=True`
   - Agent will automatically organize complex tasks

## 📝 Notes

- System hints are added as temporary user messages, not stored in history
- Trajectory files capture complete execution state for debugging
- TODO lists help agents maintain focus on multi-step tasks
- Tool call counters prevent infinite loops automatically
- Detailed errors with suggestions help agents self-correct

## 🤝 Contributing

Feel free to enhance the system hint features:
- Add new hint types
- Improve error suggestions
- Enhance TODO management rules
- Add visualization tools for trajectories

## 📄 License

MIT License - See LICENSE file for details
