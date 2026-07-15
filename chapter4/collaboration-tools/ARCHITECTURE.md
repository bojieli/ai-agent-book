# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     MCP Client (AI Agent)                        │
│                  (Claude, Custom App, etc.)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ MCP Protocol (stdio)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                  Collaboration Tools MCP Server                  │
│                          (main.py)                               │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │               FastMCP Server Layer                        │  │
│  │  • Tool Registration                                      │  │
│  │  • Request Routing                                        │  │
│  │  • Response Formatting                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────┬────────────┬────────────┬────────────┐         │
│  │  Browser   │   HITL     │   Notify   │   Timer    │         │
│  │   Tools    │   Tools    │   Tools    │   Tools    │         │
│  └─────┬──────┴──────┬─────┴──────┬─────┴──────┬─────┘         │
│        │             │            │            │               │
└────────┼─────────────┼────────────┼────────────┼───────────────┘
         │             │            │            │
         ▼             ▼            ▼            ▼
┌────────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐
│  browser-  │ │  Admin   │ │   Email  │ │  asyncio │
│    use     │ │ Webhook/ │ │   SMTP/  │ │  Timer   │
│ (Playwright)│ │  Email/  │ │ SendGrid │ │  Tasks   │
│            │ │   IM     │ │          │ │          │
│  ┌──────┐  │ └──────────┘ │  ┌────┐  │ └──────────┘
│  │Chrome│  │              │  │ IM │  │
│  └──────┘  │              │  │Webhooks│
└────────────┘              │  └────┘  │
                            └──────────┘
```

## Component Architecture

### 1. MCP Server Layer (`main.py`)

```python
┌─────────────────────────────────────┐
│         FastMCP Server              │
│                                     │
│  @mcp.tool(...)                     │
│  async def mcp_tool_name(...) -> str│
│      result = await internal_func() │
│      return str(result)             │
│                                     │
│  @mcp.on_shutdown                   │
│  async def cleanup()                │
└─────────────────────────────────────┘
```

**Responsibilities:**
- Tool registration and exposure
- Request validation
- Response serialization
- Lifecycle management

### 2. Browser Tools Layer (`browser_tools.py`)

```
┌──────────────────────────────────────────┐
│         Browser Tools Module              │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Browser Session Manager           │  │
│  │  • Singleton pattern               │  │
│  │  • Lazy initialization             │  │
│  │  • Profile management              │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Navigation & Interaction          │  │
│  │  • browser_navigate()              │  │
│  │  • browser_get_content()           │  │
│  │  • browser_screenshot()            │  │
│  │  • browser_list_tabs()             │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  AI Agent Integration              │  │
│  │  • browser_execute_task()          │  │
│  │  • LangChain + OpenAI              │  │
│  │  • Autonomous task execution       │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
           │
           ▼
    ┌────────────┐
    │ browser-use│
    │  Library   │
    └────────────┘
```

### 3. Notification Layer (`notification_tools.py`)

```
┌────────────────────────────────────────┐
│      Notification Tools Module          │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Email Handler                   │  │
│  │  ┌────────────┬────────────┐     │  │
│  │  │   SMTP     │  SendGrid  │     │  │
│  │  │  Fallback  │  Primary   │     │  │
│  │  └────────────┴────────────┘     │  │
│  └──────────────────────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  IM Handler                      │  │
│  │  ┌──────────┬──────────┬──────┐  │  │
│  │  │ Telegram │  Slack   │Discord│  │  │
│  │  │ Bot API  │ Webhook  │Webhook│  │  │
│  │  └──────────┴──────────┴──────┘  │  │
│  └──────────────────────────────────┘  │
│                                         │
│  • Async delivery                       │
│  • Error handling                       │
│  • Multi-channel support                │
└────────────────────────────────────────┘
```

### 4. HITL Layer (`hitl_tools.py`)

```
┌─────────────────────────────────────────┐
│     Human-in-the-Loop Module             │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Request Manager                   │ │
│  │  • Generate unique request IDs     │ │
│  │  • Track pending requests          │ │
│  │  • Timeout handling                │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Notification Dispatcher           │ │
│  │  • Multi-channel alerts            │ │
│  │  • Email notifications             │ │
│  │  • IM notifications                │ │
│  │  • Webhook callbacks               │ │
│  └────────────────────────────────────┘ │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │  Response Handler                  │ │
│  │  • Wait for admin response         │ │
│  │  • Process approval/rejection      │ │
│  │  • Update request status           │ │
│  └────────────────────────────────────┘ │
│                                          │
│  In-Memory Storage:                      │
│  _pending_requests: Dict[str, Request]   │
└─────────────────────────────────────────┘
```

### 5. Timer Layer (`timer_tools.py`)

```
┌──────────────────────────────────────────┐
│         Timer Management Module           │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Timer Registry                    │  │
│  │  • Active timers storage           │  │
│  │  • Timer metadata tracking         │  │
│  │  • Status management               │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Timer Execution Engine            │  │
│  │  ┌──────────────┬──────────────┐   │  │
│  │  │  One-time    │  Recurring   │   │  │
│  │  │   Timers     │   Timers     │   │  │
│  │  │              │              │   │  │
│  │  │ asyncio.sleep│  While loop  │   │  │
│  │  └──────────────┴──────────────┘   │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Callback System                   │  │
│  │  • Notification dispatch           │  │
│  │  • Custom callback data            │  │
│  └────────────────────────────────────┘  │
│                                           │
│  ┌────────────────────────────────────┐  │
│  │  Persistence Layer                 │  │
│  │  • JSON file storage               │  │
│  │  • State restoration on restart    │  │
│  └────────────────────────────────────┘  │
│                                           │
│  In-Memory Storage:                       │
│  _active_timers: Dict[str, Timer]         │
│  _timer_tasks: Dict[str, asyncio.Task]    │
└──────────────────────────────────────────┘
```

## Data Flow

### 1. Browser Automation Flow

```
MCP Client
    │
    │ call: mcp_browser_execute_task(task="...")
    ▼
MCP Server (main.py)
    │
    │ await browser_execute_task()
    ▼
Browser Tools
    │
    │ 1. Initialize browser (if needed)
    │ 2. Create LangChain agent
    │ 3. Execute task
    ▼
browser-use Library
    │
    │ • Navigate pages
    │ • Interact with elements
    │ • Extract content
    ▼
Playwright (Chrome)
    │
    │ • Actual browser automation
    ▼
Result returned to client
```

### 2. HITL Approval Flow

```
Agent Request
    │
    │ request_admin_approval(message, urgent=True)
    ▼
HITL Tools
    │
    │ 1. Create request record
    │ 2. Generate unique ID
    ▼
Notification Dispatcher
    │
    ├─► Email → Admin
    ├─► Telegram → Admin
    ├─► Slack → Admin
    └─► Webhook → Admin Dashboard
    
Admin receives notifications
    │
    │ Reviews request
    │ Responds via API/interface
    ▼
Response Handler
    │
    │ Update request status
    ▼
Wait loop completes
    │
    │ Return approval result
    ▼
Agent receives response
```

### 3. Timer Execution Flow

```
Agent
    │
    │ set_timer(duration=300, callback="...")
    ▼
Timer Tools
    │
    │ 1. Create timer record
    │ 2. Generate timer ID
    │ 3. Save to storage
    ▼
Create asyncio.Task
    │
    │ async def _run_timer(timer_id, duration):
    │     await asyncio.sleep(duration)
    │     trigger_callback()
    ▼
Timer Expires
    │
    │ 1. Update status to "expired"
    │ 2. Execute callback
    ▼
Callback Handler
    │
    ├─► Send notification (if configured)
    ├─► Update storage
    └─► Log completion
```

## Configuration Flow

```
Environment Variables (.env)
    │
    ▼
config.py
    │
    │ Pydantic Models:
    │ • BrowserConfig
    │ • EmailConfig
    │ • IMConfig
    │ • HITLConfig
    │ • TimerConfig
    ▼
Loaded into Config object
    │
    ├─► browser_tools.py
    ├─► notification_tools.py
    ├─► hitl_tools.py
    └─► timer_tools.py
```

## Error Handling Pattern

```python
┌──────────────────────────────┐
│   Tool Function Entry        │
└──────────┬───────────────────┘
           │
           ▼
    ┌─────────────┐
    │ Try Block   │
    │             │
    │ • Validate  │
    │ • Execute   │
    │ • Return    │
    └──────┬──────┘
           │
    ┌──────▼──────┐
    │   Success   │
    │  Response   │
    │             │
    │ {           │
    │  success: T │
    │  data: ...  │
    │  message:..│
    │ }           │
    └─────────────┘

    Exception ▼
    
    ┌─────────────┐
    │   Error     │
    │  Response   │
    │             │
    │ {           │
    │  success: F │
    │  error: ... │
    │  message:..│
    │ }           │
    └─────────────┘
```

## State Management

### In-Memory State

```
┌─────────────────────────────────────┐
│      Application Memory              │
│                                      │
│  _browser_session: BrowserSession    │
│  _pending_requests: Dict[str, Req]   │
│  _active_timers: Dict[str, Timer]    │
│  _timer_tasks: Dict[str, Task]       │
└─────────────────────────────────────┘
```

### Persistent State

```
┌─────────────────────────────────────┐
│      Filesystem Storage              │
│                                      │
│  ~/.config/collaboration-tools/      │
│  ├── browser/                        │
│  │   └── (browser profile data)     │
│  ├── timers.json                     │
│  │   └── (active timers state)      │
│  └── screenshots/                    │
│      └── (captured screenshots)     │
└─────────────────────────────────────┘
```

## Security Considerations

```
┌─────────────────────────────────────┐
│         Security Layers              │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  Configuration Security       │  │
│  │  • .env file (gitignored)     │  │
│  │  • No hardcoded credentials   │  │
│  │  • Environment-based config   │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  Browser Security             │  │
│  │  • Isolated user data dir     │  │
│  │  • Optional domain whitelist  │  │
│  │  • Configurable security      │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  HITL Security                │  │
│  │  • Timeout on requests        │  │
│  │  • Multi-channel verification │  │
│  │  • Audit trail                │  │
│  └───────────────────────────────┘  │
│                                      │
│  ┌───────────────────────────────┐  │
│  │  API Security                 │  │
│  │  • API keys in env vars       │  │
│  │  • No secrets in logs         │  │
│  │  • Webhook validation ready   │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## Scaling Considerations

### Current Architecture (Single Process)
```
┌──────────────────────┐
│   MCP Server         │
│  ┌────────────────┐  │
│  │  All Tools     │  │
│  │  In-Memory     │  │
│  │  State         │  │
│  └────────────────┘  │
└──────────────────────┘
```

### Future Distributed Architecture
```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Browser    │    │     HITL     │    │    Timer     │
│   Service    │    │   Service    │    │   Service    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                    │
       └───────────────────┼────────────────────┘
                           │
                    ┌──────▼────────┐
                    │   MCP Server  │
                    │   (Gateway)   │
                    └───────────────┘
                           │
                    ┌──────▼────────┐
                    │   Database    │
                    │   (State)     │
                    └───────────────┘
```

## Performance Characteristics

- **Browser Initialization**: 2-5 seconds (one-time)
- **Navigation**: 1-3 seconds per page
- **Email Send**: 1-2 seconds
- **IM Webhook**: <500ms
- **Timer Accuracy**: ±1-2 seconds
- **Memory Usage**: ~100-200MB (with browser)
- **Concurrent Timers**: Thousands (asyncio-based)

## Extension Points

1. **New Tool Categories**: Add new `*_tools.py` modules
2. **New Notification Channels**: Extend `notification_tools.py`
3. **Custom Storage Backends**: Replace JSON persistence
4. **Advanced Browser Features**: Extend `browser_tools.py`
5. **Admin Dashboard**: Web UI for HITL management
6. **Analytics**: Tool usage tracking and monitoring
