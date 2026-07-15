# GPT-5 Native Tools Agent

An advanced AI agent leveraging GPT-5's native `web_search` tool through the OpenRouter API, matching the exact implementation pattern from production Go code. This agent can search the internet for real-time information and provide code-based analysis using GPT-5's built-in capabilities.

## 🌟 Features

- **Native Tool Support**: Utilizes GPT-5's built-in `web_search` tool with OpenRouter-specific format
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
MODEL_NAME=openai/gpt-5-2025-08-07
DEFAULT_TEMPERATURE=0.3
DEFAULT_MAX_TOKENS=4000
```

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
python main.py --mode test --test combined
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
| `MODEL_NAME` | GPT-5 model identifier | `openai/gpt-5-2025-08-07` |
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

- [OpenRouter GPT-5 API](https://openrouter.ai/openai/gpt-5)
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
