# Setup Guide

## Quick Setup

1. **Navigate to the project directory:**
   ```bash
   cd projects/week3/perception-tools
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

4. **Test the installation:**
   ```bash
   python test_imports.py
   ```

5. **Run the quickstart demo:**
   ```bash
   python quickstart.py
   ```

6. **Start the MCP server:**
   ```bash
   python src/main.py
   ```

## Detailed API Setup

### Google Custom Search (Required for web search)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable "Custom Search API"
4. Create an API key in "Credentials"
5. Go to [Programmable Search Engine](https://programmablesearchengine.google.com/)
6. Create a new search engine
7. Configure it to search the entire web
8. Get your Search Engine ID (cx parameter)
9. Add to `.env`:
   ```
   GOOGLE_API_KEY=your_api_key
   GOOGLE_CSE_ID=your_search_engine_id
   ```

### OpenWeather API (Required for weather)

1. Sign up at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your API key from the dashboard
3. Add to `.env`:
   ```
   OPENWEATHER_API_KEY=your_api_key
   ```

### Notion API (Optional)

1. Go to [Notion Integrations](https://www.notion.so/my-integrations)
2. Create a new integration
3. Copy the "Internal Integration Token"
4. Share your databases/pages with the integration
5. Install the Notion SDK:
   ```bash
   pip install notion-client
   ```
6. Add to `.env`:
   ```
   NOTION_API_KEY=your_integration_token
   ```

### Google Calendar API (Optional)

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable "Google Calendar API"
3. Create OAuth 2.0 credentials
4. Download the credentials JSON file
5. Install required packages:
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```
6. Run the OAuth flow (first time only):
   ```python
   # This will open a browser for authentication
   # The token will be saved to ~/.perception-tools/google_token.pickle
   ```

## Using with MCP Clients

### Claude Desktop Configuration

Edit your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the server configuration:

```json
{
  "mcpServers": {
    "perception-tools": {
      "command": "python",
      "args": ["/absolute/path/to/perception-tools/src/main.py"],
      "env": {
        "GOOGLE_API_KEY": "your_key",
        "GOOGLE_CSE_ID": "your_cse_id",
        "OPENWEATHER_API_KEY": "your_key"
      }
    }
  }
}
```

### Other MCP Clients

The server uses stdio transport and can be integrated with any MCP-compatible client. Refer to your client's documentation for configuration details.

## Troubleshooting

### Import Errors

If you see import errors, make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### API Errors

If API calls fail:
1. Check that your API keys are correctly set in `.env`
2. Verify your API quotas haven't been exceeded
3. Check the API service status

### File Permission Errors

Ensure the script has write permissions for:
- Download directory (for file downloads)
- `~/.perception-tools/` (for OAuth tokens)

### Module Not Found

If Python can't find modules, ensure you're running from the correct directory or adjust your PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/perception-tools/src"
```

## Development

### Running Tests

```bash
# Test imports
python test_imports.py

# Test tools
python quickstart.py
```

### Adding New Tools

1. Choose the appropriate module (or create a new one)
2. Implement the tool function following the pattern:
   ```python
   async def my_tool(param: str) -> Union[str, TextContent]:
       try:
           # Implementation
           return TextContent(...)
       except Exception as e:
           # Error handling
           return TextContent(...)
   ```
3. Register the tool in `main.py` using `@mcp.tool` decorator
4. Update documentation

### Code Style

- Follow KISS, DRY, and SOLID principles
- Use type hints
- Include docstrings for all functions
- Return standardized ActionResponse format
- Include comprehensive error handling

## Support

For issues and questions:
1. Check this setup guide
2. Review the main README.md
3. Check tool-specific documentation
4. Review API provider documentation
