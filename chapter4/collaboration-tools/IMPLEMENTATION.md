# Implementation Details

## Architecture Overview

The Collaboration Tools MCP Server is built with a modular architecture that separates concerns into distinct tool categories:

1. **Browser Automation** - Virtual browser operations using browser-use
2. **Notifications** - Email and instant messaging integrations
3. **Human-in-the-Loop** - Admin approval and input request system
4. **Timers** - Scheduling and delayed task execution

## Core Components

### 1. Browser Tools (`browser_tools.py`)

The browser automation module integrates the `browser-use` library to provide AI-driven web automation capabilities.

**Key Features:**
- Singleton browser session management
- Integration with browser-use Agent for autonomous tasks
- Support for multiple tabs
- Screenshot capture
- Content extraction with CSS selectors

**Implementation Details:**
```python
# Browser session is initialized lazily and reused
_browser_session = None

async def init_browser():
    global _browser_session
    if _browser_session is not None:
        return _browser_session
    # Create browser with profile and settings
    profile = BrowserProfile(...)
    browser = Browser(browser_profile=profile)
    await browser.start()
    _browser_session = browser
    return browser
```

### 2. Notification Tools (`notification_tools.py`)

Provides multi-channel notification capabilities with fallback support.

**Supported Channels:**
- **Email**: SMTP or SendGrid API
- **Telegram**: Bot API integration
- **Slack**: Webhook-based messaging
- **Discord**: Webhook-based messaging

**Implementation Pattern:**
```python
async def send_email(...):
    # Check if SendGrid is configured (preferred)
    if config.email.sendgrid_api_key:
        return await _send_email_sendgrid(...)
    # Fall back to SMTP
    elif config.email.smtp_username:
        return await _send_email_smtp(...)
    else:
        return {"success": False, "error": "No email service configured"}
```

### 3. Human-in-the-Loop Tools (`hitl_tools.py`)

Enables AI agents to request human assistance when needed.

**Key Features:**
- Async request/response pattern
- Multiple notification channels for admin alerts
- Timeout handling
- Request tracking and status management

**Request Flow:**
1. Agent creates approval request
2. System notifies admin via configured channels
3. System waits for admin response (with timeout)
4. Admin responds through API or interface
5. Result returned to agent

**Storage:**
```python
# In-memory storage of pending requests
_pending_requests: Dict[str, Dict[str, Any]] = {}

# Each request has:
# - request_id: Unique identifier
# - message: What needs approval
# - context: Additional data
# - status: pending/approved/rejected/timeout
# - admin_notes: Admin's response
```

### 4. Timer Tools (`timer_tools.py`)

Provides scheduling capabilities for delayed task execution.

**Timer Types:**
- **One-time timers**: Execute once after delay
- **Recurring timers**: Execute at intervals

**Implementation:**
```python
# Active timers stored in-memory and persisted to disk
_active_timers: Dict[str, Dict[str, Any]] = {}
_timer_tasks: Dict[str, asyncio.Task] = {}

async def _run_timer(timer_id: str, duration_seconds: int):
    await asyncio.sleep(duration_seconds)
    # Timer expired - trigger callback
    await _trigger_timer_callback(timer_data)
```

**Persistence:**
- Timers are saved to JSON file on disk
- Active timers are restored on server restart
- Remaining time is recalculated on restore

### 5. Configuration (`config.py`)

Centralized configuration management using Pydantic models.

**Configuration Hierarchy:**
```python
Config
├── BrowserConfig (browser settings)
├── EmailConfig (email service settings)
├── IMConfig (IM service settings)
├── HITLConfig (HITL settings)
└── TimerConfig (timer storage settings)
```

**Environment Variable Mapping:**
- All settings can be configured via environment variables
- Defaults provided for most settings
- Sensitive credentials loaded from .env file

## MCP Server Implementation

The main server (`main.py`) uses FastMCP to expose all tools via the MCP protocol.

**Server Structure:**
```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("collaboration-tools")

@mcp.tool(description="...")
async def mcp_tool_name(...) -> str:
    result = await internal_function(...)
    return str(result)
```

**Lifecycle Management:**
```python
@mcp.on_shutdown
async def cleanup():
    # Close browser sessions
    await close_browser()
    # Save timer state
    await _save_timers()
```

## Error Handling

All tools follow a consistent error handling pattern:

```python
try:
    # Perform operation
    result = await operation()
    return {
        "success": True,
        "data": result,
        "message": "Operation successful"
    }
except Exception as e:
    logger.error(f"Operation failed: {e}")
    return {
        "success": False,
        "error": str(e),
        "message": "Operation failed"
    }
```

## Integration Patterns

### Using with Claude Desktop

Add to `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "collaboration-tools": {
      "command": "python",
      "args": ["/path/to/src/main.py"]
    }
  }
}
```

### Using as Python Client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_tools():
    server_params = StdioServerParameters(
        command="python",
        args=["src/main.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Call tools
            result = await session.call_tool("mcp_set_timer", {
                "duration_seconds": 60,
                "timer_name": "Test"
            })
```

## Security Considerations

1. **Browser Security**:
   - Option to restrict allowed domains
   - Configurable security settings
   - Isolated user data directory

2. **Credentials**:
   - All secrets loaded from environment variables
   - No hardcoded credentials
   - .env file excluded from version control

3. **HITL**:
   - Timeout on all approval requests
   - Admin notification via multiple channels
   - Request tracking and audit trail

4. **Timer Persistence**:
   - Timers stored in user's home directory
   - JSON format for easy inspection
   - State recovery on restart

## Performance Considerations

1. **Browser Session**:
   - Lazy initialization (only when needed)
   - Single shared session (reduces memory)
   - Proper cleanup on shutdown

2. **Async Operations**:
   - All I/O operations are async
   - Non-blocking timer implementation
   - Concurrent notification delivery

3. **Resource Management**:
   - Browser tabs can be closed individually
   - Expired timers cleaned up
   - Temporary files managed

## Testing

The implementation includes:
- `quickstart.py` - Functional demo of all tools
- `client_example.py` - Real-world workflow example
- Modular design enables unit testing of individual components

## Future Enhancements

Potential improvements:
1. Database storage for HITL requests and timers
2. Web dashboard for admin management
3. More notification channels (SMS, push notifications)
4. Browser recording/replay capabilities
5. Advanced scheduling (cron-like expressions)
6. Tool usage analytics and monitoring
