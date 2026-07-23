## English

# Browser-Use RPA with Learning Capability

An Agent that can operate a computer and improve with practice.

## Project Overview

This project implements a browser automation Agent with learning capabilities. The Agent can:

1. **Learning Phase**: Complete new tasks using multimodal LLMs (GPT-4o, Claude, Gemini, etc.) and capture successful operation workflows.
2. **Application Phase**: Recognize similar tasks and directly replay learned workflows without invoking the LLM again.
3. **Continuous Improvement**: Record execution metrics and continuously optimize the knowledge base.

## Architecture Design

```text
browser-use-rpa/
├── browser-use/          # Browser-use core library (unmodified)
├── learning_agent/       # Learning Agent wrapper layer
│   ├── agent.py         # Main Agent class, wrapping browser-use
│   ├── workflow.py      # Workflow data structure
│   ├── knowledge_base.py # Knowledge base management
│   └── replay.py        # Workflow replayer
├── demo_weather.py      # Weather query demo
├── demo_email.py        # Email sending demo
└── knowledge_base/      # Stores learned workflows
```

### Core Components

#### 1. LearningAgent (agent.py)
- Wraps the browser-use Agent class
- Intercepts and records each operation step
- Extracts stable XPath selectors
- Manages learning and replay modes

#### 2. Workflow (workflow.py)
- Defines the workflow data structure
- Supports parameterization (e.g., different recipients, subjects, etc.)
- Records element selectors and operation parameters

#### 3. KnowledgeBase (knowledge_base.py)
- Persistently stores workflows
- Intent matching algorithm
- Performance metric tracking

#### 4. WorkflowReplayer (replay.py)
- Uses Playwright to directly control the browser
- Intelligently waits for element loading
- Error recovery mechanism

## Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers
playwright install chromium

# 3. Configure environment variables
cp env.example .env
# Edit the .env file and add your API keys
```

## Usage Examples

### Basic Usage

```python
from learning_agent import LearningAgent
from llm_factory import make_llm  # Wrapper LLM factory: direct OpenAI, falls back to OpenRouter if key is missing

# Create a learning Agent
agent = LearningAgent(
    task="Send an email to test@example.com with subject 'Test' and body 'This is a test email'",
    llm=make_llm(),  # Default: gpt-5.6-luna; falls back to OpenRouter if OPENAI_API_KEY is not set
    knowledge_base_path="./knowledge_base",
    headless=False  # Show the browser window
)

# Execute the task
result = agent.run_sync(max_steps=20)

print(f"Task completed: {'Success' if result['success'] else 'Failed'}")
print(f"Execution time: {result['execution_time']:.2f} seconds")
print(f"Learned workflow used: {result['replay_used']}")
```

### Running Demos

`demo_email.py` is the main entry point for this experiment, demonstrating the core idea of "learn a workflow once → replay it at high speed with different parameters."
It provides a complete Chinese command-line interface. Run `python demo_email.py --help` to view all parameters:

```bash
# Run the full "learn → replay" comparison demo (default behavior, opens a browser)
python demo_email.py

# Quick smoke test: run a single simple task without learn/replay comparison
python demo_email.py --quick

# Headless mode + use Gemini model
python demo_email.py --model gemini-2.0-flash-exp --headless

# Customize tasks for both phases and write metric comparison to a JSON file
python demo_email.py \
    --task 'Send an email to a@b.com with subject "Report"' \
    --replay-task 'Send an email to c@d.com with subject "Weekly Report"' \
    --output results.json

# Weather query demo (another lighter example)
python demo_weather.py
```

**Command-line argument description (`demo_email.py`):**

| Argument | Description | Default Value |
|-----|------|-------|
| `--task` | Task description for the learning phase | Send a test email to test@example.com |
| `--replay-task` | Task description for the replay phase (different parameters, same workflow) | Send an email to another@example.com |
| `--model` | LLM; `gpt-*` uses OpenAI (falls back to OpenRouter if key is missing), `gemini-*` uses Google | `gpt-5.6-luna` |
| `--headless` | Run the browser in headless mode | Show window |
| `--knowledge-base` | Storage directory for the workflow knowledge base | `./email_knowledge` |
| `--max-steps` | Maximum number of operation steps for the learning phase | `20` |
| `--output` | Write learn/replay metrics and knowledge base statistics to a JSON file | Do not write |
| `--quick` | Quick smoke test mode | Off |

**Expected results:** On the first run, the Agent is in the learning phase. It will gradually explore and record the "send email" workflow using the multimodal LLM. This takes longer and generates multiple LLM calls. Subsequently, the replay phase reuses the same workflow with new recipient/subject parameters, almost never invoking the LLM again, resulting in significantly reduced time. At the end of the demo, the duration, number of LLM calls, and knowledge base statistics for both phases are printed. If `--output` is specified, this comparison is saved as structured JSON, facilitating a review of the cost-benefit of "learn once, reuse many times."

> Note: A complete run requires a valid model API Key (see `.env`) and a locally available browser (`playwright install chromium`).
> `--help` and argument parsing do not require these dependencies.

## Acceptance Criteria Tests

### 1. First Task Execution (Learning Phase)

Run `demo_email.py` and observe the first phase:

- The Agent completes the task through an "observe-think-act" loop
- Each step requires an LLM call
- Upon success, the workflow is automatically saved to the knowledge base
- Execution time and step count are displayed

**Example output:**
```text
📚 PHASE 1: LEARNING - First Email Task
Task: Send email to test@example.com
🚀 Starting learning phase...
✅ Learning phase completed!
   - Success: ✓
   - Execution time: 35.2 seconds
   - LLM calls made: 12
   - Workflow captured: Yes
```

### 2. Repeated Task Execution (Application Phase)

Continue observing the second phase:

- The Agent recognizes a similar task and matches a learned workflow
- Directly replays the operation steps without invoking the LLM
- Automatically fills in new parameters (recipient, subject, etc.)
- Execution speed is significantly improved

**Example output:**
```text
🚀 PHASE 2: REPLAY - Second Email Task
Task: Send email to another@example.com
🔄 Starting replay phase...
✅ Replay phase completed!
   - Success: ✓
   - Execution time: 8.5 seconds
   - Workflow reused: Yes

🎯 Performance Improvements:
   - Speed: 4.1x faster
   - LLM calls saved: 12
   - Time saved: 26.7 seconds
```

## Technical Features

### 1. Stable Element Location

- **XPath Priority**: Captures the complete XPath path of elements, providing good robustness against page structure changes.
- **Multiple Fallbacks**: Attempts CSS selectors, attribute selectors, etc., when XPath fails.
- **Intelligent Waiting**: Uses `wait_for(state='visible')` to ensure elements are loaded.

### 2. Workflow Capture Mechanism

```python
# Extract element information from browser-use's internal state
element = selector_map[index]
workflow_step = WorkflowStep(
    action_type=ActionType.CLICK,
    xpath=element.xpath,
    element_attributes={
        'id': element.attributes.get('id'),
        'class': element.attributes.get('class'),
        ...
    }
)
```

### 3. Intent Matching Algorithm

- Keyword matching
- Verb recognition (send, write, check, etc.)
- Success rate weighting
- Confidence scoring

## Performance Comparison

| Metric | Learning Phase | Replay Phase | Improvement |
|-----|---------|---------|-----|
| Execution Time | 30-40 seconds | 5-10 seconds | 3-5x |
| LLM Call Count | 10-15 times | 0 times | 100% |
| Success Rate | 85% | 95%+ | 10%+ |

## Knowledge Base Management

View knowledge base statistics:

```python
from learning_agent import KnowledgeBase

kb = KnowledgeBase("./knowledge_base")
stats = kb.get_statistics()
print(stats)
# {
#     'total_workflows': 5,
#     'total_executions': 23,
#     'success_rate': '91.3%',
#     'total_model_calls_saved': 156
# }
```

Clear the knowledge base:

```python
kb.clear_all()  # Use with caution
```

## Limitations and Notes

1. **Dynamic Content**: XPath may change for highly dynamic pages.
2. **Authentication State**: Login state is not saved; each run starts from scratch.
3. **Complex Interactions**: Drag-and-drop, right-click menus, and other complex operations are not yet supported.
4. **Multiple Tabs**: Tab handling is simplified in replay mode.

## Extension Suggestions

1. **Smarter Parameter Extraction**: Use NLP models to extract task parameters.
2. **Workflow Composition**: Combine multiple small workflows into complex tasks.
3. **Error Recovery**: Enhance recovery strategies for replay failures.
4. **Distributed Knowledge Base**: Support team sharing of learned results.

## Contributing

Issues and Pull Requests to improve this project are welcome.

## License

This project is developed based on browser-use and follows its open-source license agreement.

---

## 中文

# Browser-Use RPA with Learning Capability

能操作电脑，并且越做越熟练的 Agent

## 项目概述

本项目实现了一个具有学习能力的浏览器自动化Agent。该Agent能够：

1. **学习阶段**：通过多模态大模型（GPT-4o, Claude, Gemini等）完成新任务，并捕获成功的操作流程
2. **应用阶段**：识别相似任务，直接回放已学习的工作流，无需再次调用大模型
3. **持续改进**：记录执行指标，不断优化知识库

## 架构设计

```text
browser-use-rpa/
├── browser-use/          # Browser-use 核心库（未修改）
├── learning_agent/       # 学习Agent封装层
│   ├── agent.py         # 主Agent类，封装browser-use
│   ├── workflow.py      # 工作流数据结构
│   ├── knowledge_base.py # 知识库管理
│   └── replay.py        # 工作流回放器
├── demo_weather.py      # 天气查询演示
├── demo_email.py        # 邮件发送演示
└── knowledge_base/      # 存储学习到的工作流
```

### 核心组件

#### 1. LearningAgent (agent.py)
- 封装browser-use的Agent类
- 拦截并记录每个操作步骤
- 提取稳定的XPath选择器
- 管理学习和回放模式

#### 2. Workflow (workflow.py)
- 定义工作流数据结构
- 支持参数化（如不同的收件人、主题等）
- 记录元素选择器和操作参数

#### 3. KnowledgeBase (knowledge_base.py)
- 持久化存储工作流
- 意图匹配算法
- 性能指标跟踪

#### 4. WorkflowReplayer (replay.py)
- 使用Playwright直接控制浏览器
- 智能等待元素加载
- 错误恢复机制

## 安装

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 安装Playwright浏览器
playwright install chromium

# 3. 配置环境变量
cp env.example .env
# 编辑.env文件，添加你的API密钥
```

## 使用示例

### 基本用法

```python
from learning_agent import LearningAgent
from llm_factory import make_llm  # 包装层 LLM 工厂：OpenAI 直连，缺 Key 时 OpenRouter 兜底

# 创建学习Agent
agent = LearningAgent(
    task="发送邮件给test@example.com，主题是'测试'，内容是'这是一封测试邮件'",
    llm=make_llm(),  # 默认 gpt-5.6-luna；无 OPENAI_API_KEY 时走 OpenRouter 兜底
    knowledge_base_path="./knowledge_base",
    headless=False  # 显示浏览器界面
)

# 执行任务
result = agent.run_sync(max_steps=20)

print(f"任务完成: {'成功' if result['success'] else '失败'}")
print(f"执行时间: {result['execution_time']:.2f}秒")
print(f"是否使用已学习的工作流: {result['replay_used']}")
```

### 运行演示

`demo_email.py` 是本实验的主入口，演示「学习一次工作流 → 用不同参数高速回放」这一核心思想。
它提供了完整的中文命令行接口，运行 `python demo_email.py --help` 可查看所有参数：

```bash
# 运行完整的「学习 → 回放」对比演示（默认行为，会打开浏览器）
python demo_email.py

# 快速冒烟测试：只跑一次简单任务，不做学习/回放对比
python demo_email.py --quick

# 无界面模式 + 使用 Gemini 模型
python demo_email.py --model gemini-2.0-flash-exp --headless

# 自定义两个阶段的任务，并把指标对比写入 JSON 文件
python demo_email.py \
    --task '给 a@b.com 发主题为"报告"的邮件' \
    --replay-task '给 c@d.com 发主题为"周报"的邮件' \
    --output results.json

# 天气查询演示（另一个更轻量的例子）
python demo_weather.py
```

**命令行参数说明（`demo_email.py`）：**

| 参数 | 说明 | 默认值 |
|-----|------|-------|
| `--task` | 学习阶段的任务描述 | 向 test@example.com 发送测试邮件 |
| `--replay-task` | 回放阶段的任务描述（参数不同、流程相同） | 向 another@example.com 发送邮件 |
| `--model` | 大模型；`gpt-*` 走 OpenAI（缺 Key 时 OpenRouter 兜底），`gemini-*` 走 Google | `gpt-5.6-luna` |
| `--headless` | 以无界面模式运行浏览器 | 显示窗口 |
| `--knowledge-base` | 工作流知识库存储目录 | `./email_knowledge` |
| `--max-steps` | 学习阶段最大操作步数 | `20` |
| `--output` | 把学习/回放指标与知识库统计写入 JSON 文件 | 不写出 |
| `--quick` | 快速冒烟测试模式 | 关闭 |

**预期结果：** 第一次运行时，Agent 处于学习阶段，会通过多模态大模型逐步探索并录制「发送邮件」工作流，
耗时较长且产生多次 LLM 调用；随后回放阶段用新的收件人/主题参数复用同一工作流，几乎不再调用大模型，
耗时显著下降。演示结束会打印两个阶段的耗时、LLM 调用次数与知识库统计；若指定了 `--output`，
上述对比会以结构化 JSON 保存，便于复盘“学习一次、复用多次”带来的成本收益。

> 注意：完整运行需要有效的模型 API Key（见 `.env`）以及本地可用的浏览器（`playwright install chromium`）。
> `--help` 与参数解析本身无需上述依赖即可查看。

## 验收标准测试

### 1. 首次任务执行（学习阶段）

运行 `demo_email.py`，观察第一阶段：

- Agent通过"观察-思考-行动"循环完成任务
- 每步操作都需要调用大模型
- 成功后自动保存工作流到知识库
- 显示执行时间和步骤数

**示例输出：**
```text
📚 PHASE 1: LEARNING - First Email Task
Task: Send email to test@example.com
🚀 Starting learning phase...
✅ Learning phase completed!
   - Success: ✓
   - Execution time: 35.2 seconds
   - LLM calls made: 12
   - Workflow captured: Yes
```

### 2. 重复任务执行（应用阶段）

继续观察第二阶段：

- Agent识别相似任务，匹配已学习的工作流
- 直接回放操作步骤，无需调用大模型
- 自动填充新的参数（收件人、主题等）
- 执行速度显著提升

**示例输出：**
```text
🚀 PHASE 2: REPLAY - Second Email Task
Task: Send email to another@example.com
🔄 Starting replay phase...
✅ Replay phase completed!
   - Success: ✓
   - Execution time: 8.5 seconds
   - Workflow reused: Yes
   
🎯 Performance Improvements:
   - Speed: 4.1x faster
   - LLM calls saved: 12
   - Time saved: 26.7 seconds
```

## 技术特点

### 1. 稳定的元素定位

- **XPath优先**：捕获元素的完整XPath路径，对页面结构变化有较好的鲁棒性
- **多重回退**：XPath失败时尝试CSS选择器、属性选择器等
- **智能等待**：使用`wait_for(state='visible')`确保元素加载完成

### 2. 工作流捕获机制

```python
# 从browser-use的内部状态提取元素信息
element = selector_map[index]
workflow_step = WorkflowStep(
    action_type=ActionType.CLICK,
    xpath=element.xpath,
    element_attributes={
        'id': element.attributes.get('id'),
        'class': element.attributes.get('class'),
        ...
    }
)
```

### 3. 意图匹配算法

- 关键词匹配
- 动词识别（send, write, check等）
- 成功率加权
- 置信度评分

## 性能对比

| 指标 | 学习阶段 | 回放阶段 | 提升 |
|-----|---------|---------|-----|
| 执行时间 | 30-40秒 | 5-10秒 | 3-5倍 |
| LLM调用次数 | 10-15次 | 0次 | 100% |
| 成功率 | 85% | 95%+ | 10%+ |

## 知识库管理

查看知识库统计：

```python
from learning_agent import KnowledgeBase

kb = KnowledgeBase("./knowledge_base")
stats = kb.get_statistics()
print(stats)
# {
#     'total_workflows': 5,
#     'total_executions': 23,
#     'success_rate': '91.3%',
#     'total_model_calls_saved': 156
# }
```

清空知识库：

```python
kb.clear_all()  # 谨慎使用
```

## 限制和注意事项

1. **动态内容**：对于高度动态的页面，XPath可能会变化
2. **认证状态**：不会保存登录状态，每次都从头开始
3. **复杂交互**：暂不支持拖拽、右键菜单等复杂操作
4. **多标签页**：回放模式简化了标签页处理

## 扩展建议

1. **更智能的参数提取**：使用NLP模型提取任务参数
2. **工作流组合**：将多个小工作流组合成复杂任务
3. **错误恢复**：增强回放失败时的恢复策略
4. **分布式知识库**：支持团队共享学习成果

## 贡献

欢迎提交Issue和Pull Request来改进本项目。

## 许可

本项目基于browser-use开发，遵循其开源许可协议。
