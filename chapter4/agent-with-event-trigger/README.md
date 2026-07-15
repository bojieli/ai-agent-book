# Event-Triggered AI Agent with MCP Tools

A modern AI agent with **native async support** that responds to events from various sources. Built with **FastAPI** and integrated with **42 MCP tools** for enhanced capabilities including browser automation, web search, document processing, and more.

## 🌟 Features

### Core Capabilities
- ✅ **Native Async** - FastAPI with clean async/await support
- ✅ **42 MCP Tools** - Automatically loaded from 3 MCP servers
- ✅ **Event-Driven** - Responds to web messages, emails, GitHub updates, timers
- ✅ **System Hints** - Timestamps, tool counters, TODO management
- ✅ **Auto API Docs** - Interactive Swagger UI at `/docs`
- ✅ **Background Tasks** - Process monitoring and system alerts

### MCP Tool Categories

**Collaboration Tools** (18 tools):
- Browser automation (navigate, screenshot, execute tasks)
- Notifications (email, Telegram, Slack, Discord)
- Human-in-the-loop (admin approval, input requests)
- Timer management (one-time, recurring)

**Execution Tools** (6 tools):
- File operations (write, edit with verification)
- Code execution (Python interpreter, shell commands)
- External integrations (Google Calendar, GitHub PRs)

**Perception Tools** (18 tools):
- Web search and content extraction
- Document reading (PDF, DOCX, PPTX)
- Multimodal parsing (images, videos, webpages)
- Public data (weather, stocks, Wikipedia, ArXiv)
- Private data (Google Calendar, Notion)

## 🚀 Quick Start

### Installation

```bash
cd projects/week4/agent-with-event-trigger

# Install dependencies (includes FastAPI, uvicorn, MCP SDK)
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env and add your API key
export KIMI_API_KEY='your-api-key-here'
```

### Start the Server

```bash
python server.py
```

Output:
```
🤖 EVENT-TRIGGERED AGENT SERVER (FastAPI)
✅ Starting server on port 8000
📡 API Documentation: http://localhost:8000/docs
📊 ReDoc: http://localhost:8000/redoc

🚀 Starting Event-Triggered Agent Server (FastAPI)
✅ Agent initialized with kimi provider
🔄 MCP tools enabled (default) - loading asynchronously...
✅ Discovered tools from 'collaboration': 18 tools
✅ Discovered tools from 'execution': 6 tools
✅ Discovered tools from 'perception': 18 tools
✅ MCP tools loaded: 42 tools available
✅ Server ready to receive events

INFO: Uvicorn running on http://0.0.0.0:8000
```

### Interactive API Documentation

Visit **http://localhost:8000/docs** to:
- 📖 Browse all available endpoints
- 🧪 Test API calls interactively
- 📝 See request/response schemas
- ⚡ Send events with one click

## 📡 API Endpoints

### Core Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Check MCP tools status
curl http://localhost:8000/mcp/status

# Send an event
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "web_message",
    "content": "Search the web for Python async best practices",
    "metadata": {"user": "demo"}
  }'

# Get agent status
curl http://localhost:8000/agent/status

# Reset agent state
curl -X POST http://localhost:8000/agent/reset

# Reload MCP tools
curl -X POST http://localhost:8000/mcp/reload
```

### Using the Interactive Docs

1. Open http://localhost:8000/docs
2. Click on any endpoint (e.g., `POST /event`)
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. See the response instantly!

## 🎯 Usage Examples

### Running the Standalone Example

For a complete demonstration of MCP integration without the server, run:

```bash
python example_with_mcp.py
```

This standalone script:
- Initializes the agent with MCP tools enabled
- Loads all 42 tools from the 3 MCP servers
- Processes a sample event (web search task)
- Shows the complete flow from tool discovery to execution
- Properly cleans up MCP connections

Output:
```
================================================================================
Event-Triggered Agent with MCP Tools Example
================================================================================

Initializing agent...
✅ Agent initialized with kimi provider

Loading MCP tools...
✅ Discovered tools from 'collaboration': 18 tools
✅ Discovered tools from 'execution': 6 tools  
✅ Discovered tools from 'perception': 18 tools
✅ MCP tools loaded: 42 tools available

Testing Event Processing
================================================================================
📥 RECEIVED EVENT: Search the web for 'Python async best practices'...
```

This is useful for:
- Testing MCP integration without running a server
- Understanding the async tool loading flow
- Debugging MCP connection issues
- Learning how to use the agent programmatically

### Example 1: Web Search Task

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "web_message",
    "content": "Search for the latest FastAPI features and summarize them",
    "metadata": {"user": "demo"}
  }'
```

The agent will:
1. Use `perception_web_search` to find results
2. Parse the content with `perception_webpage_reader`
3. Summarize findings in the response

### Example 2: Browser Automation

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "web_message",
    "content": "Navigate to example.com and take a screenshot",
    "metadata": {}
  }'
```

Uses:
- `collaboration_mcp_browser_navigate`
- `collaboration_mcp_browser_screenshot`

### Example 3: Document Processing

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "web_message",
    "content": "Download and summarize the PDF from https://example.com/doc.pdf",
    "metadata": {}
  }'
```

Uses:
- `perception_download`
- `perception_document_reader`

### Example 4: Email Notification

```bash
curl -X POST http://localhost:8000/event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "timer_trigger",
    "content": "Send daily report to admin@example.com",
    "metadata": {"scheduled": true}
  }'
```

Uses:
- `collaboration_mcp_send_email`

## ⚙️ Configuration

### Environment Variables

```bash
# Required
export KIMI_API_KEY="your-key"

# Optional
export LLM_PROVIDER="kimi"              # kimi, siliconflow, doubao, openrouter
export LLM_MODEL="kimi-k2-0905-preview" # Override default model
export AGENT_PORT="8000"                # Server port (default: 8000)
export ENABLE_MCP_TOOLS="true"          # Enable MCP (default: true)
```

### Disable MCP Tools

If you only want built-in tools:

```bash
ENABLE_MCP_TOOLS=false python server.py
```

### Custom Port

```bash
AGENT_PORT=9000 python server.py
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Server                        │
│                   (Native Async)                         │
└───────────┬─────────────────────────────────────────────┘
            │
            ├─► Lifespan Events (Startup/Shutdown)
            │   └─► Load MCP Tools Asynchronously
            │
            ├─► Event Handler (Process incoming events)
            │   └─► EventTriggeredAgent
            │       ├─► System Hints (timestamps, TODOs)
            │       ├─► Tool Execution (MCP + built-in)
            │       └─► Trajectory Saving
            │
            └─► MCP Server Manager
                ├─► Collaboration Tools (18 tools)
                ├─► Execution Tools (6 tools)
                └─► Perception Tools (18 tools)
```

## 📂 Project Structure

```
agent-with-event-trigger/
├── agent.py                 # Event-triggered agent with system hints
├── event_types.py           # Event type definitions
├── server.py                # FastAPI server (main entry point)
├── requirements.txt         # Dependencies (FastAPI, uvicorn, MCP)
├── env.example              # Environment template
├── README.md                # This file
├── FASTAPI_GUIDE.md         # Detailed FastAPI guide
├── MCP_INTEGRATION.md       # MCP tools documentation
└── example_with_mcp.py      # Standalone MCP example
```

## 🔧 MCP Tools Reference

### Check Available Tools

```bash
curl http://localhost:8000/mcp/status
```

Response shows:
- `tools`: List of all 42 tool names
- `tools_by_server`: Tools grouped by server
- `tools_count`: Total count
- `loaded`: Whether MCP tools are active

### Tool Naming Convention

MCP tools use underscore prefixes:
- `collaboration_*` - Collaboration tools
- `execution_*` - Execution tools  
- `perception_*` - Perception tools

Built-in tools (no prefix):
- `read_file`
- `write_file`
- `code_interpreter`
- `execute_command`
- `rewrite_todo_list`
- `update_todo_status`

## 🚦 Event Types

```python
class EventType(Enum):
    # External input events
    WEB_MESSAGE = "web_message"           # Web interface
    IM_MESSAGE = "im_message"             # Instant messaging
    EMAIL_REPLY = "email_reply"           # Email responses
    GITHUB_PR_UPDATE = "github_pr_update" # PR notifications
    TIMER_TRIGGER = "timer_trigger"       # Scheduled tasks
    
    # System reminder events
    USER_TIMEOUT = "user_timeout"         # No user activity
    PROCESS_TIMEOUT = "process_timeout"   # Long-running process
    SYSTEM_ALERT = "system_alert"         # System warnings
```

### Event Format

```json
{
  "event_type": "web_message",
  "content": "Your task description",
  "metadata": {
    "user_id": "user123",
    "session_id": "session456"
  }
}
```

## 🎨 Using the Client

The included client provides easy testing:

```bash
# Interactive mode
python client.py --mode interactive

# Test scenarios
python client.py --mode test

# Direct command
python client.py --message "Create a Python hello world script"
```

## 🔐 Security Considerations

For production deployment:

1. **HTTPS**: Use a reverse proxy (nginx, Caddy)
2. **Authentication**: Add API key validation
3. **Rate Limiting**: Prevent abuse
4. **Input Validation**: Sanitize all inputs
5. **CORS**: Configure allowed origins
6. **Environment**: Use secrets management

## 🆚 Comparison: Flask vs FastAPI

| Feature | Old (Flask) | New (FastAPI) |
|---------|-------------|---------------|
| Framework | Flask (WSGI) | FastAPI (ASGI) |
| Async Support | ❌ Threads | ✅ Native async/await |
| MCP Integration | ⚠️ Complex | ✅ Clean |
| API Docs | ❌ Manual | ✅ Auto-generated |
| Performance | Good | **Better** (2-3x) |
| Port | 4242 | 8000 |
| Deprecation Warnings | N/A | ✅ Fixed (lifespan) |

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Check what's using port 8000
lsof -i :8000

# Use different port
AGENT_PORT=8001 python server.py
```

### MCP Tools Not Loading

```bash
# Check status
curl http://localhost:8000/mcp/status

# Look for error in response
# Common issue: Missing API keys for MCP servers

# Reload tools
curl -X POST http://localhost:8000/mcp/reload
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Verify FastAPI installed
python -c "import fastapi; print(fastapi.__version__)"
```

### Agent Not Responding

```bash
# Check health
curl http://localhost:8000/health

# View logs in server terminal
# Check trajectory file: event_agent_trajectory.json
```

## 📚 Additional Documentation

- **FASTAPI_GUIDE.md** - Complete FastAPI setup guide
- **MCP_INTEGRATION.md** - MCP tools technical details
- **QUICKSTART_MCP.md** - Quick start with MCP
- **README_MCP.md** - MCP overview and troubleshooting

## 🔄 Migration from Old Version

If upgrading from Flask version:

1. **Port changed**: 4242 → 8000
2. **No deprecation warnings**: Using modern lifespan events
3. **MCP enabled by default**: Set `ENABLE_MCP_TOOLS=false` to disable
4. **Same API contracts**: Endpoints work the same way
5. **Better performance**: Native async for MCP calls

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- Additional MCP servers
- More event types
- Enhanced monitoring
- Production-ready authentication
- Kubernetes deployment configs

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- Built with [FastAPI](https://fastapi.tiangolo.com/)
- MCP protocol by [Model Context Protocol](https://modelcontextprotocol.io/)
- Tool servers: collaboration-tools, execution-tools, perception-tools