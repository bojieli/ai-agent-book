# GPT-5 Native Tools Agent

An advanced AI agent leveraging GPT-5's native `web_search` and `code_interpreter` tools through the OpenRouter API, matching the exact implementation pattern from production Go code. This agent can search the internet for real-time information and run code for deep analysis using GPT-5's built-in capabilities, realizing the "搜索 → 阅读 → 分析 → 再搜索" Deep Research loop.

## 🌟 Features

- **Native Tool Support**: Utilizes GPT-5's built-in `web_search` and `code_interpreter` tools with OpenRouter-specific format
- **OpenRouter Integration**: Exact API format matching production Go implementation
- **Web Search Capability**: 
  - Real-time internet search for current information
  - Configurable search context size and user location
- **Reasoning Levels**: Support for low, medium, and high reasoning effort
- **Interactive CLI**: User-friendly command-line interface with reasoning controls
- **Agent Chaining**: Chain multiple requests for complex workflows
- **Comprehensive Testing**: Test suite demonstrating various use cases

## 📋 Prerequisites

- Python 3.8 or higher
- OpenRouter API key (get one at [https://openrouter.ai/keys](https://openrouter.ai/keys))
- Internet connection for web search functionality

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd projects/week1/search-codegen

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env

# Edit .env and add your OpenRouter API key
# OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

### 2. Configuration

Edit `.env` file with your settings:

```env
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
MODEL_NAME=openai/gpt-5.6-sol
DEFAULT_TEMPERATURE=0.3
DEFAULT_MAX_TOKENS=4000
```

> This experiment uses OpenRouter as its **primary** backend, so no fallback is
> needed. The same `OPENROUTER_API_KEY` doubles as the **universal fallback** for
> the other chapter1 experiments (`context`, `learning-from-experience`,
> `web-search-agent`) when their direct provider key is missing.

### 3. Run the Agent

#### Interactive Mode (Recommended)
```bash
python main.py
```

#### Single Request Mode
```bash
python main.py --mode single --request "Search for latest AI news and analyze the trends"
```

#### Run Tests
```bash
python main.py --mode test
```

### 命令行参数（CLI）

本实验对应书中 **实验 1.3 ★：GPT-5.6 原生 Deep Research 能力**，演示模型如何自主组合 `web_search`（网络搜索）与 `code_interpreter`（代码解释器）两个原生工具，完成“搜索 → 阅读 → 分析 → 再搜索”的迭代研究。运行 `python main.py --help` 查看中文帮助。

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--mode` | 运行模式：`interactive` 交互 / `single` 单次 / `test` 测试 | `interactive` |
| `--request` | `single` / `--dry-run` 模式下的任务或查询内容 | — |
| `--model` | 覆盖模型名称 | 配置中的 `MODEL_NAME` |
| `--reasoning` | 推理力度 Reasoning Effort（`low`/`medium`/`high`） | `low` |
| `--verbosity` | 输出详略程度 Verbosity（`low`/`medium`/`high`） | 跟随模型 |
| `--no-tools` | 禁用原生工具 | 启用 |
| `--output` | 将完整结果（含轨迹 / 请求体）保存为 JSON | — |
| `--dry-run` | 离线组装并打印请求体，不联网、无需 API Key | 关闭 |
| `--test` | `test` 模式下运行指定用例 | 运行全部 |

> **Reasoning Effort 与 Verbosity** 是书中强调的两个 GPT-5 原生参数：前者调节思考深度，后者控制回答详略。二者都已通过 CLI 暴露，并原样注入到发送给模型的请求体中。

示例：

```bash
# 书中示例任务：东盟 10 国首都最近的一对（搜索坐标 + 代码计算大圆距离）
python main.py --mode single --request "东盟 10 国首都之间距离最近的两个首都是？给出详细分析推理过程。" --reasoning high

# 书中示例任务：比特币技术分析（多源实时数据 + 指标计算）
python main.py --mode single --request "搜索比特币最近一个月走势，计算 MA、RSI、MACD 等技术指标" --verbosity high --output btc.json
```

### 离线查看请求体（dry-run）

无需 API Key 即可查看“模型即 Agent”范式下真正发送给模型的请求——包括两个原生工具的定义、`reasoning` 与 `verbosity` 参数。这直观展示了原生工具调用的结构，也便于调试：

```bash
python main.py --dry-run --request "东盟 10 国首都之间距离最近的两个首都是？" --reasoning high --verbosity high
```

输出的请求体中，`tools` 数组同时包含 `web_search` 和 `code_interpreter`，`reasoning.effort` 与 `verbosity` 反映所选档位——正是书中所述的原生工具 + 推理/详略参数的组合。

## 🛠️ Usage Examples

### Example 1: Web Search Only
```python
from agent import GPT5NativeAgent
from config import Config

agent = GPT5NativeAgent(
    api_key=Config.OPENROUTER_API_KEY,
    base_url=Config.OPENROUTER_BASE_URL
)

result = agent.process_request(
    "What are the latest developments in quantum computing?",
    use_tools=True
)
print(result["response"])
```

### Example 2: Web Search with High Reasoning
```python
result = agent.process_request(
    "Analyze the implications of quantum computing on encryption",
    use_tools=True,
    reasoning_effort="high"
)
```

### Example 3: Web Search with Analysis
```python
result = agent.process_request(
    """Search for current Bitcoin price and market data, 
    then analyze the volatility and predict trends""",
    use_tools=True,
    reasoning_effort="medium"
)
```

### Example 4: Search and Analyze Method
```python
analysis_code = """
import statistics
# Process search results
prices = [45000, 46000, 45500, 47000, 46500]
volatility = statistics.stdev(prices)
print(f"Volatility: ${volatility:.2f}")
"""

result = agent.search_and_analyze(
    topic="Current cryptocurrency market conditions",
    analysis_code=analysis_code
)
```

## 📁 Project Structure

```
search-codegen/
├── agent.py          # Core GPT-5 agent implementation
├── config.py         # Configuration management
├── main.py           # Interactive CLI and entry point
├── test_agent.py     # Comprehensive test suite
├── env.example       # Environment variables template
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 OpenRouter Tool Format

### web_search Tool Structure
The web_search tool uses OpenRouter's specific format:
```python
{
    "type": "web_search",
    "search_context_size": "medium",
    "user_location": {
        "type": "approximate",
        "country": "US"
    }
}
```

### Reasoning Configuration
Supports configurable reasoning effort:
- **low**: Fast responses with basic reasoning
- **medium**: Balanced reasoning and response time
- **high**: Deep reasoning for complex queries

## 🧪 Testing

The test suite includes comprehensive test cases:

1. **Basic Web Search**: Test internet search capabilities
2. **Web Search with Analysis**: Search with analytical insights
3. **Complex Research**: Deep research with high reasoning
4. **Search and Code**: Search with code generation
5. **Reasoning Comparison**: Compare different reasoning levels
6. **Search and Analyze Method**: Convenience method testing
7. **Agent Chain**: Multi-step workflow

Run specific tests:
```bash
# Run all tests
python test_agent.py

# Run specific test
python main.py --mode test --test basic
```

Available test names: `basic`, `analysis`, `complex`, `code`, `reasoning`, `search_analyze`, `chain`

## 🎯 Interactive CLI Commands

When running in interactive mode, the following commands are available:

- `/help` - Show help message
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/tools` - Toggle tools on/off
- `/search` - Enter web search mode
- `/code` - Enter code generation mode
- `/analyze` - Combined search + analysis mode
- `/config` - Show current configuration
- `/reasoning` - Set reasoning effort level
- `/exit` - Exit the application

## ⚙️ Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENROUTER_API_KEY` | Your OpenRouter API key | Required |
| `MODEL_NAME` | GPT-5 model identifier | `openai/gpt-5.6-sol` |
| `DEFAULT_TEMPERATURE` | Response randomness (0-1) | `0.3` |
| `DEFAULT_MAX_TOKENS` | Maximum response length | `4000` |
| `DEFAULT_TOOL_CHOICE` | Tool selection strategy | `auto` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

## 🤝 API Integration

This agent uses the OpenRouter API to access GPT-5. OpenRouter provides:
- Unified API for multiple models
- Automatic fallbacks for reliability
- Usage tracking and analytics
- Competitive pricing

Learn more at [OpenRouter Documentation](https://openrouter.ai/docs)

## 📊 Token Usage

The agent tracks token usage for each request:
- Prompt tokens: Input token count
- Completion tokens: Output token count
- Total tokens: Combined usage

Monitor costs based on OpenRouter's pricing:
- Input: $1.25 per million tokens
- Output: $10 per million tokens

## 🐛 Troubleshooting

### API Key Issues
```bash
# Verify your API key starts with 'sk-or-'
echo $OPENROUTER_API_KEY
```

### Rate Limiting
Adjust `RATE_LIMIT_RPM` in `.env` if encountering rate limits

### Tool Errors
- Ensure `use_tools=True` when calling `process_request`
- Set `tool_choice="required"` to force tool usage

## 📝 License

This project is part of the AI Agent实战训练营 curriculum.

## 🔗 Resources

- [OpenRouter GPT-5 API](https://openrouter.ai/openai/gpt-5.6-sol)
- [OpenAI Native Tools Documentation](https://platform.openai.com/docs/guides/tools)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [API Keys](https://openrouter.ai/keys)

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review test cases for usage examples
3. Consult the OpenRouter documentation

---

Built with GPT-5's native capabilities via OpenRouter API 🚀
