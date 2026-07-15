# Collaboration Tools MCP Server

A comprehensive Model Context Protocol (MCP) server that provides collaboration tools for AI agents, including browser automation, human-in-the-loop assistance, notifications, and timer management.

## Features

### 🌐 Browser Automation (using browser-use)
- Navigate to URLs and manage browser tabs
- Extract content from web pages
- Execute high-level browser tasks using AI agents
- Take screenshots
- Full virtual browser capabilities

### 👤 Human-in-the-Loop (HITL)
- Request admin approval for sensitive actions
- Request input from human administrators
- Manage pending approval requests
- Configurable timeout and notification channels

### 📧 Email Notifications
- Send emails via SMTP or SendGrid
- Support for HTML emails
- CC recipients and attachments
- Flexible configuration

### 💬 Instant Messaging
- Telegram bot integration
- Slack webhook support
- Discord webhook support
- Configurable default channels

### ⏰ Timer & Scheduling
- Set one-time timers
- Create recurring timers
- Cancel and manage timers
- Persistent timer storage
- Callback notifications when timers expire

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd projects/week4/collaboration-tools
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy the example environment file and configure it:
```bash
cp env.example .env
# Edit .env with your configuration
```

4. Install Playwright browsers (for browser automation):
```bash
playwright install chromium
```

## Configuration

Configure the server by setting environment variables in `.env`:

### Browser Settings
```env
BROWSER_HEADLESS=false
BROWSER_USER_DATA_DIR=~/.config/collaboration-tools/browser
```

### Email Configuration
```env
# SMTP (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your-email@gmail.com

# Or use SendGrid
SENDGRID_API_KEY=your-sendgrid-api-key
```

### Instant Messaging
```env
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_DEFAULT_CHAT_ID=your-chat-id
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/WEBHOOK
```

### HITL Settings
```env
HITL_ADMIN_EMAIL=admin@example.com
HITL_TIMEOUT_SECONDS=3600
```

### For Browser Tasks (AI Agent)
```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
```

## Usage

### Running the MCP Server

Start the server using stdio transport:
```bash
python src/main.py
```

Or use it as an MCP server with any MCP-compatible client.

### Quick Start Demo

Run the quickstart demo to see all features in action:
```bash
python quickstart.py
```

### Using with Claude Desktop

Add to your Claude Desktop configuration (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "collaboration-tools": {
      "command": "python",
      "args": ["/path/to/collaboration-tools/src/main.py"],
      "env": {
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

## Available Tools

### Browser Tools
- `mcp_browser_navigate` - Navigate to a URL
- `mcp_browser_get_content` - Get page content
- `mcp_browser_execute_task` - Execute AI-driven browser task
- `mcp_browser_screenshot` - Take a screenshot
- `mcp_browser_list_tabs` - List all open tabs

### Notification Tools
- `mcp_send_email` - Send email notification
- `mcp_send_telegram_message` - Send Telegram message
- `mcp_send_slack_message` - Send Slack message
- `mcp_send_discord_message` - Send Discord message

### Human-in-the-Loop Tools
- `mcp_request_admin_approval` - Request admin approval
- `mcp_request_admin_input` - Request admin input
- `mcp_respond_to_request` - Respond to approval request (admin)
- `mcp_list_pending_requests` - List pending requests

### Timer Tools
- `mcp_set_timer` - Set a one-time timer
- `mcp_set_recurring_timer` - Set a recurring timer
- `mcp_cancel_timer` - Cancel a timer
- `mcp_list_timers` - List all timers
- `mcp_get_timer_status` - Get timer status

## Example Usage

### Browser Automation
```python
# Navigate to a website
await mcp_browser_navigate(url="https://example.com")

# Execute a complex task
await mcp_browser_execute_task(
    task="Search for AI agent tutorials on Google and extract the top 5 results"
)

# Take a screenshot
await mcp_browser_screenshot(full_page=True)
```

### Notifications
```python
# Send email
await mcp_send_email(
    to_email="user@example.com",
    subject="Task Completed",
    body="Your task has finished successfully!"
)

# Send Slack message
await mcp_send_slack_message(
    message="🎉 Deployment successful!"
)
```

### Human-in-the-Loop
```python
# Request approval for sensitive action
result = await mcp_request_admin_approval(
    request_message="Delete 1000 records from database?",
    urgent=True,
    timeout_seconds=300
)

if result["approved"]:
    # Proceed with action
    pass
```

### Timers
```python
# Set a timer
await mcp_set_timer(
    duration_seconds=300,
    timer_name="Check website",
    callback_message="Time to check the website status"
)

# Set recurring timer
await mcp_set_recurring_timer(
    interval_seconds=3600,
    max_occurrences=24,
    timer_name="Hourly health check"
)
```

## Architecture

The server is organized into modular components:

```
collaboration-tools/
├── src/
│   ├── main.py              # MCP server entry point
│   ├── config.py            # Configuration management
│   ├── browser_tools.py     # Browser automation
│   ├── notification_tools.py # Email & IM notifications
│   ├── hitl_tools.py        # Human-in-the-loop
│   └── timer_tools.py       # Timer management
├── requirements.txt         # Python dependencies
├── env.example             # Example configuration
└── README.md               # This file
```

## Requirements

- Python 3.11+
- OpenAI API key (for browser AI agent tasks)
- Optional: Email/IM service credentials
- Playwright browsers for browser automation

## Troubleshooting

### Browser Issues
If browser automation fails:
```bash
# Reinstall Playwright browsers
playwright install chromium --force
```

### Email Issues
- For Gmail, use an [App Password](https://support.google.com/accounts/answer/185833)
- Ensure "Less secure app access" is NOT enabled (use App Passwords instead)

### Telegram Issues
- Create a bot via [@BotFather](https://t.me/botfather)
- Get your chat ID from [@userinfobot](https://t.me/userinfobot)

### LangChain/Pydantic Issues
If you see errors like "`ChatOpenAI` is not fully defined" or Pydantic validation errors:
- This is a known compatibility issue between LangChain and Pydantic v2
- The fix: ChatOpenAI is now initialized on-demand only when needed (in `browser_execute_task`)
- Simple browser navigation doesn't require OpenAI API key
- Only autonomous browser tasks (`browser_execute_task`) require `OPENAI_API_KEY`

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Support

For questions or issues, please open an issue on the repository.
