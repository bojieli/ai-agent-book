# Perception Tools MCP Server

A comprehensive MCP (Model Context Protocol) server providing various perception and data retrieval capabilities for AI agents.

## Features

> **✨ No API Keys Required!** Most features work out-of-the-box with free, open APIs.

### 🔍 Search Tools
- **Web Search**: DuckDuckGo search (free, no API key required)
- **Knowledge Base Search**: Search local document collections
- **File Download**: Download files from URLs with safety checks

### 📄 Multimodal Understanding Tools
- **Web Page Reader**: Extract text and links from web pages
- **Document Reader**: Extract content from PDF, DOCX, PPTX files
- **Image Parser**: Parse and analyze image files
- **Video Parser**: Extract metadata from video files

### 📁 File System Tools
- **File Reader**: Read files with encoding support
- **Grep Search**: Search for patterns in files (regex support)
- **Text Summarization**: Summarize long text content

### 🌐 Public Data Sources
- **Weather**: Current weather via [Open-Meteo](https://open-meteo.com/) (free, no API key)
- **Stock Prices**: Real-time stock data from Yahoo Finance (free, no API key)
- **Crypto Prices**: Cryptocurrency prices via [CoinGecko](https://www.coingecko.com/) (free, no API key)
- **Currency Conversion**: Convert between currencies (free, no API key)
- **Location Search**: Geocoding via [Nominatim (OpenStreetMap)](https://nominatim.openstreetmap.org/) (free, no API key)
- **POI Search**: Points of Interest via [Overpass API (OpenStreetMap)](https://overpass-api.de/) (free, no API key)
- **Wikipedia**: Search and retrieve Wikipedia articles (free, no API key)
- **ArXiv**: Search academic papers on ArXiv (free, no API key)
- **Wayback Machine**: Access archived web pages (free, no API key)

### 🔐 Private Data Sources
- **Google Calendar**: Query calendar events
- **Notion**: Search Notion workspace

## Installation

1. Clone the repository and navigate to the project directory:

```bash
cd projects/week3/perception-tools
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. **No additional configuration required!** The server works out-of-the-box with free APIs.

## Configuration

### ✅ Default Free APIs (No Setup Required)

The following features work immediately without any API keys:
- **Web Search**: DuckDuckGo
- **Weather**: Open-Meteo  
- **Stock Prices**: Yahoo Finance
- **Crypto Prices**: CoinGecko
- **Currency Conversion**: ExchangeRate-API
- **Location Search**: Nominatim (OpenStreetMap)
- **POI Search**: Overpass API (OpenStreetMap)
- **Wikipedia**: Wikipedia API
- **ArXiv**: ArXiv API
- **Wayback Machine**: Internet Archive

### Optional Private Data Integrations

#### Google Calendar
For Google Calendar integration, you need to set up OAuth2:

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Follow the [Google Calendar API quickstart](https://developers.google.com/calendar/api/quickstart/python) to set up OAuth2 credentials.

#### Notion
1. Create a Notion integration at [notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Get your integration token
3. Share your databases/pages with the integration
4. Add `NOTION_API_KEY` to `.env`

```bash
pip install notion-client
```

## Usage

### Running the MCP Server

```bash
cd src
python main.py
```

The server runs using stdio transport, suitable for integration with MCP clients.

### Command-Line Interface (`cli.py`)

除了以 MCP stdio 协议对外服务，仓库根目录提供了一个统一的命令行入口
`cli.py`，无需 MCP 客户端即可直接列出、查看、调用和演示各类感知工具。
工具按第四章「感知工具」的五类场景组织：搜索 / 多模态理解 / 文件系统 /
公开数据源 / 私有数据源（当前共 53 个工具）。

```bash
# 查看帮助（中文）
python cli.py --help

# 按五类列出全部感知工具（可用 --category 只看某一类）
python cli.py list
python cli.py list --category filesystem

# 查看某个工具的参数签名与调用示例
python cli.py info weather

# 直接调用某个工具，参数以 key=value 形式传入，结果为标准 ActionResponse JSON
python cli.py run grep 'pattern=async def' directory=src 'file_pattern=*.py'
python cli.py run currency_converter amount=100 from_currency=USD to_currency=CNY

# 运行端到端演示：串联「本地资料 + 外部信息」的研究助手 Agent 感知流程
python cli.py demo            # 完整演示（含联网步骤）
python cli.py demo --offline  # 离线演示（只跑文件系统 / 本地知识库等不联网步骤）
```

说明：

- 每个工具都是异步函数，返回统一的 `ActionResponse`（JSON）；CLI 负责运行事件
  循环、解析 JSON 并友好打印。
- 工具按需惰性导入：`list` / `info` / 离线 `demo` 在缺少可选依赖（如 `whisper`、
  `waybackpy`）时仍可正常工作，只有真正调用相关工具时才导入对应模块。
- 需要联网的工具在 `list` 中标注「联网」，需要授权/API Key 的工具标注了对应说明。

### Using with MCP Clients

Configure your MCP client (e.g., Claude Desktop) to connect to this server:

```json
{
  "mcpServers": {
    "perception-tools": {
      "command": "python",
      "args": ["/path/to/perception-tools/src/main.py"]
    }
  }
}
```

## Available Tools

### Search Tools

#### `web_search`
Search the web using DuckDuckGo (free, no API key required).

Parameters:
- `query` (str): Search query string
- `num_results` (int, default=5): Number of results (1-10)
- `region` (str, default="wt-wt"): Region code (e.g., "us-en", "uk-en", "wt-wt" for worldwide)

#### `download`
Download a file from a URL.

Parameters:
- `url` (str): URL to download from
- `output_path` (str): Local path to save the file
- `overwrite` (bool, default=False): Overwrite existing file
- `timeout` (int, default=180): Download timeout in seconds

#### `knowledge_base_search`
Search a local knowledge base directory.

Parameters:
- `query` (str): Search query
- `knowledge_base_path` (str): Path to knowledge base directory
- `top_k` (int, default=5): Number of top results

### Multimodal Understanding Tools

#### `webpage_reader`
Read and extract content from a webpage.

Parameters:
- `url` (str): URL of the webpage
- `extract_text` (bool, default=True): Extract text content
- `extract_links` (bool, default=False): Extract links

#### `document_reader`
Read and extract content from documents (PDF, DOCX, PPTX).

Parameters:
- `file_path` (str): Path to document file or URL
- `extract_images` (bool, default=False): Extract images

#### `image_parser`
Parse and analyze image files.

Parameters:
- `image_path` (str): Path to image file or URL
- `use_llm` (bool, default=True): Use LLM for analysis

#### `video_parser`
Parse and extract metadata from video files.

Parameters:
- `video_path` (str): Path to video file or URL
- `extract_frames` (bool, default=False): Extract sample frames
- `frame_interval` (int, default=30): Frame extraction interval

### File System Tools

#### `file_reader`
Read a file and return its contents.

Parameters:
- `file_path` (str): Path to the file
- `encoding` (str, default="utf-8"): File encoding
- `max_length` (int, default=50000): Maximum characters to read

#### `grep`
Search for patterns in files (grep-like functionality).

Parameters:
- `pattern` (str): Regular expression pattern
- `directory` (str): Directory to search in
- `file_pattern` (str, default="*"): File pattern (e.g., *.py)
- `recursive` (bool, default=True): Search recursively
- `case_sensitive` (bool, default=False): Case-sensitive search
- `max_results` (int, default=100): Maximum results

#### `text_summarizer`
Summarize long text content.

Parameters:
- `text` (str): Text to summarize
- `max_length` (int, default=500): Target summary length
- `use_llm` (bool, default=True): Use LLM for summarization

### Public Data Source Tools

#### `weather`
Get current weather information using Open-Meteo API (free, no API key required).

Parameters:
- `location` (str): City name (automatically geocoded)
- `latitude` (float, optional): Latitude coordinate
- `longitude` (float, optional): Longitude coordinate

#### `stock_price`
Get stock price and market information using Yahoo Finance (free, no API key required).

Parameters:
- `symbol` (str): Stock ticker symbol (e.g., AAPL, TSLA, GOOGL)
- `interval` (str, default="1d"): Data interval

#### `crypto_price`
Get cryptocurrency price information using CoinGecko API (free, no API key required).

Parameters:
- `symbol` (str): Cryptocurrency symbol or ID (e.g., bitcoin, ethereum, btc, eth)
- `vs_currency` (str, default="usd"): Target currency (usd, eur, gbp, etc.)

#### `currency_converter`
Convert between currencies.

Parameters:
- `amount` (float): Amount to convert
- `from_currency` (str): Source currency code (e.g., USD)
- `to_currency` (str): Target currency code (e.g., EUR)

#### `wikipedia_search`
Search Wikipedia and get article summary.

Parameters:
- `query` (str): Search query
- `language` (str, default="en"): Wikipedia language
- `sentences` (int, default=5): Summary sentence count

#### `arxiv_search`
Search ArXiv for academic papers.

Parameters:
- `query` (str): Search query
- `max_results` (int, default=5): Maximum results
- `sort_by` (str, default="relevance"): Sort method

#### `wayback_search`
Search Wayback Machine for archived web pages.

Parameters:
- `url` (str): URL to search for
- `year` (int, optional): Filter by year
- `limit` (int, default=10): Maximum snapshots

#### `location_search`
Search for locations using Nominatim (OpenStreetMap) API (free, no API key required).

Parameters:
- `query` (str): Location query (e.g., "Eiffel Tower", "New York", "Tokyo")
- `limit` (int, default=5): Maximum number of results (1-50)
- `country_code` (str, optional): Country code filter (e.g., "us", "gb", "fr")

#### `poi_search`
Search for Points of Interest near a location using Overpass API (free, no API key required).

Parameters:
- `query` (str): Type of POI (e.g., "restaurant", "cafe", "hospital", "atm", "hotel")
- `latitude` (float): Center latitude coordinate
- `longitude` (float): Center longitude coordinate
- `radius` (int, default=1000): Search radius in meters
- `limit` (int, default=10): Maximum number of results

### Private Data Source Tools

#### `calendar_events`
Get events from Google Calendar.

Parameters:
- `start_date` (str, optional): Start date (ISO format)
- `end_date` (str, optional): End date (ISO format)
- `calendar_id` (str, default="primary"): Calendar ID
- `max_results` (int, default=10): Maximum events

#### `notion_search`
Search Notion workspace.

Parameters:
- `query` (str): Search query
- `database_id` (str, optional): Specific database ID
- `page_size` (int, default=10): Results per page

## Architecture

The project follows SOLID principles with a modular architecture:

```
perception-tools/
├── src/
│   ├── main.py                  # MCP server entry point
│   ├── base.py                  # Base models and utilities
│   ├── search_tools.py          # Search functionality
│   ├── multimodal_tools.py      # Document/media processing
│   ├── filesystem_tools.py      # File operations
│   ├── public_data_tools.py     # Public APIs
│   └── private_data_tools.py    # Private data sources
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## Error Handling

All tools return a standardized `ActionResponse` format:

```json
{
  "success": true/false,
  "message": "Result data or error message",
  "metadata": {
    "additional": "context information"
  }
}
```

## Contributing

Contributions are welcome! Please ensure:
1. Code follows KISS, DRY, and SOLID principles
2. All tools return standardized ActionResponse format
3. Proper error handling and logging
4. Documentation for new tools

## License

This project is part of the AI Agent training camp materials.

## Support

For issues and questions, please refer to the main project documentation.
