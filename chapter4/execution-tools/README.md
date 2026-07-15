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
# MODEL=kimi-k2-0905-preview

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
- `kimi`/`moonshot`: kimi-k2-0905-preview
- `openrouter`: google/gemini-2.5-pro (or openai/gpt-5, anthropic/claude-sonnet-4)

## Usage

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

## Experiment 4.3

This project is part of Week 4 experiments focusing on execution tools with safety mechanisms.
