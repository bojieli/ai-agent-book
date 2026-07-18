# Execution Tools MCP Server

An MCP (Model Context Protocol) server that provides comprehensive execution tools with built-in safety mechanisms for AI agents.

## Features

### Safety Mechanisms

1. **LLM-Based Approval**: Irreversible operations require approval from a secondary LLM before execution
2. **Result Summarization**: Execution tool outputs larger than 10,000 characters are automatically summarized by an LLM for easier processing
3. **Automatic Verification**: Operations that can be verified (e.g., syntax checking) are automatically validated

### Tool Categories

#### File System Tools
- **file_write**: Write content to files with automatic syntax verification
- **file_edit**: Edit existing files with diff preview and verification

#### Generic Execution Tools
- **code_interpreter**: Execute Python code in a sandboxed environment with result analysis
- **virtual_terminal**: Execute shell commands with error summarization

#### External System Integration Tools
- **google_calendar_add**: Add events to Google Calendar
- **github_create_pr**: Create GitHub Pull Requests with validation

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `env.example` to `.env`:
```bash
cp env.example .env
```

2. Configure your environment variables:
```
# LLM Configuration (for safety checks and summarization)
PROVIDER=kimi

# API Keys (set the one for your provider)
KIMI_API_KEY=your_kimi_key
# SILICONFLOW_API_KEY=your_siliconflow_key
# DOUBAO_API_KEY=your_doubao_key
# OPENROUTER_API_KEY=your_openrouter_key

# Model (optional, defaults to provider's default)
# MODEL=kimi-k3

# Model parameters
TEMPERATURE=0.7
MAX_TOKENS=4096

# External Services (optional)
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GITHUB_TOKEN=your_github_token

# Safety Settings
REQUIRE_APPROVAL_FOR_DANGEROUS_OPS=true
AUTO_SUMMARIZE_COMPLEX_OUTPUT=true
AUTO_VERIFY_CODE=true
```

**Supported Providers:**
- `siliconflow`: Qwen/Qwen3-235B-A22B-Thinking-2507
- `doubao`: doubao-seed-1-6-thinking-250715  
- `kimi`/`moonshot`: kimi-k3
- `openrouter`: google/gemini-2.5-pro (or openai/gpt-5, anthropic/claude-sonnet-4)

## Usage

### 命令行入口 (CLI)

`cli.py` 是统一的命令行入口，用于列出、单独调用每个执行工具，并运行端到端演示。
它复用与 MCP 服务器相同的工具实现，因此行为完全一致。

```bash
# 查看总帮助与所有子命令
python cli.py --help

# 列出所有执行工具
python cli.py list

# 端到端离线演示（推荐先看这个；无需 API key 即可运行）
python cli.py demo

# 单独调用某个工具
python cli.py code --language python --code "print(2 ** 10)"
python cli.py shell "python3 --version"
python cli.py write --path notes.txt --content "hello" --overwrite
python cli.py edit --path notes.txt --search hello --replace world
```

全局开关（放在子命令之前）：

| 开关 | 作用 |
|------|------|
| `--provider` | 覆盖 LLM 提供商（`PROVIDER`） |
| `--workspace` | 覆盖工作目录（文件操作被限制在此目录内） |
| `--no-approval` | 关闭危险操作的 LLM 事前审批 |
| `--no-verify` | 关闭写文件/代码的自动语法校验 |
| `--no-summarize` | 关闭长输出的 LLM 总结（仍会截断并持久化） |

**离线运行**：`list`、`demo` 以及关闭了审批/总结/非 Python 校验的
`code`/`shell`/`write`/`edit` 均无需 API key。需要 API key 的场景为：LLM 事前审批、
长输出的 LLM 总结、非 Python 语法校验。`calendar` 与 `pr` 还额外需要相应外部凭据。

> **长输出的截断与持久化**：当 `code_interpreter` / `virtual_terminal` 的输出
> 超过阈值（默认 200 行或 10000 字符）时，工具只在上下文中保留头尾各 50 行，
> 完整输出落盘到临时文件，并在返回值的 `stdout_file` / `stderr_file` 字段给出路径。
> 该机制不依赖 LLM，可离线工作。

### Running the MCP Server

```bash
python server.py
```

### Using with MCP Client

```python
from mcp import Client

# Connect to the MCP server
client = Client("stdio://python server.py")

# Use file write tool
result = await client.call_tool("file_write", {
    "path": "test.py",
    "content": "print('Hello, World!')"
})

# Use code interpreter
result = await client.call_tool("code_interpreter", {
    "code": "import math\nprint(math.sqrt(16))"
})

# Use virtual terminal
result = await client.call_tool("virtual_terminal", {
    "command": "ls -la"
})
```

### Testing Individual Tools

```bash
# Test file operations
python test_file_tools.py

# Test execution tools
python test_execution_tools.py

# Test external integrations
python test_external_tools.py
```

## Architecture

The server implements a layered architecture:

1. **Safety Layer**: Intercepts dangerous operations and validates them
2. **Tool Layer**: Implements individual tool logic
3. **Verification Layer**: Validates outputs and provides feedback
4. **Integration Layer**: Connects to external services

## Examples

See `examples.py` for comprehensive usage examples.

## 实验 4-2：执行工具 MCP 服务器

本项目对应书中第 4 章「执行工具」一节的实验 4-2，聚焦执行工具的安全机制：
分层安全防护（输入验证、权限控制、LLM 事前审批）、自动语法验证与反馈闭环、
以及长输出的截断与持久化。推荐从 `python cli.py demo` 开始。
