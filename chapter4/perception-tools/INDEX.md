# Perception Tools MCP Server - Complete Index

## Quick Navigation

### Getting Started
- [README.md](README.md) - Project overview and introduction
- [SETUP.md](SETUP.md) - Detailed setup and configuration instructions
- [quickstart.py](quickstart.py) - Demo script to test tools

### Documentation
- [TOOL_REFERENCE.md](TOOL_REFERENCE.md) - Complete API reference for all 18 tools
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture and design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Implementation summary

### Configuration
- [requirements.txt](requirements.txt) - Python dependencies
- [env.example](env.example) - Environment variables template

### Source Code
- [src/main.py](src/main.py) - MCP server entry point (18 tool registrations)
- [src/base.py](src/base.py) - Shared utilities and models
- [src/search_tools.py](src/search_tools.py) - Search functionality (3 tools)
- [src/multimodal_tools.py](src/multimodal_tools.py) - Multimodal processing (4 tools)
- [src/filesystem_tools.py](src/filesystem_tools.py) - File operations (3 tools)
- [src/public_data_tools.py](src/public_data_tools.py) - Public APIs (6 tools)
- [src/private_data_tools.py](src/private_data_tools.py) - Private data (2 tools)

### Testing
- [test_imports.py](test_imports.py) - Verify module imports

## Project Statistics

- **Total Files**: 17
- **Python Modules**: 8
- **Lines of Code**: ~2,128
- **Total Tools**: 18
- **Tool Categories**: 5
- **Documentation Pages**: 6
- **External APIs Integrated**: 8+

## Tool Categories Overview

### 🔍 Search Tools (3)
1. **web_search** - Google Custom Search
2. **download** - File downloads
3. **knowledge_base_search** - Local search

### 📄 Multimodal Understanding (4)
4. **webpage_reader** - Web content extraction
5. **document_reader** - PDF/DOCX/PPTX
6. **image_parser** - Image analysis
7. **video_parser** - Video metadata

### 📁 File System Tools (3)
8. **file_reader** - Read files
9. **grep** - Pattern search
10. **text_summarizer** - Summarization

### 🌐 Public Data Sources (6)
11. **weather** - Weather information
12. **stock_price** - Stock data
13. **currency_converter** - Currency conversion
14. **wikipedia_search** - Wikipedia
15. **arxiv_search** - Academic papers
16. **wayback_search** - Web archives

### 🔐 Private Data Sources (2)
17. **calendar_events** - Google Calendar
18. **notion_search** - Notion workspace

## API Dependencies

### Required (for core functionality)
- Google Custom Search API (web search)
- OpenWeather API (weather)

### Optional
- Google Calendar API (calendar events)
- Notion API (Notion search)

### No API Key Required
- Wikipedia
- ArXiv
- Yahoo Finance (stocks)
- Exchange Rate API (currency)
- Wayback Machine

## Common Tasks

### Installation
```bash
cd projects/week3/perception-tools
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
```

### Testing
```bash
python test_imports.py  # Verify imports
python quickstart.py    # Test functionality
```

### Running
```bash
cd src
python main.py  # Start MCP server
```

### Adding to Claude Desktop
Edit config file and add:
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

## Documentation Structure

### For Users
1. Start with [README.md](README.md)
2. Follow [SETUP.md](SETUP.md) for configuration
3. Run [quickstart.py](quickstart.py) to test
4. Reference [TOOL_REFERENCE.md](TOOL_REFERENCE.md) for API details

### For Developers
1. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design
2. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) for implementation
3. Study source code in `src/` directory
4. Follow patterns when adding new tools

## File Purposes

| File | Purpose | Audience |
|------|---------|----------|
| README.md | Overview, features, basic usage | End users |
| SETUP.md | Installation and configuration | End users |
| TOOL_REFERENCE.md | Complete API documentation | End users, Developers |
| ARCHITECTURE.md | System design and structure | Developers |
| PROJECT_SUMMARY.md | Implementation details | Developers, Reviewers |
| INDEX.md | This file - navigation aid | Everyone |
| requirements.txt | Python dependencies | Installation |
| env.example | Configuration template | Configuration |
| quickstart.py | Demo and testing | Testing |
| test_imports.py | Import verification | Testing |

## Module Purposes

| Module | Lines | Tools | Purpose |
|--------|-------|-------|---------|
| main.py | ~370 | 18 | MCP server and tool registration |
| base.py | ~150 | - | Shared utilities and models |
| search_tools.py | ~320 | 3 | Search and download operations |
| multimodal_tools.py | ~360 | 4 | Document and media processing |
| filesystem_tools.py | ~280 | 3 | File system operations |
| public_data_tools.py | ~550 | 6 | Public API integrations |
| private_data_tools.py | ~180 | 2 | Private data sources |

## Key Design Decisions

1. **Modular Architecture**: Separate files for each category
2. **Async Throughout**: All tools use async/await
3. **Standardized Responses**: ActionResponse format everywhere
4. **Comprehensive Error Handling**: Try-except with detailed errors
5. **Configuration via Environment**: No hardcoded credentials
6. **Optional Dependencies**: Core tools work without all APIs
7. **Type Hints**: Full type annotation for IDE support
8. **Documentation**: Extensive inline and external docs

## Supported Formats

### Documents
- PDF, DOCX, PPTX, TXT, MD, JSON

### Images
- JPG, PNG, GIF, BMP, TIFF, WEBP

### Videos
- MP4, AVI, MOV, MKV, WEBM

### Web
- HTML, HTTP/HTTPS URLs

## External Service Integration

| Service | Tool | API Required | Status |
|---------|------|--------------|--------|
| Google Search | web_search | Yes | Implemented |
| OpenWeather | weather | Yes | Implemented |
| Yahoo Finance | stock_price | No | Implemented |
| Exchange Rate API | currency_converter | No | Implemented |
| Wikipedia | wikipedia_search | No | Implemented |
| ArXiv | arxiv_search | No | Implemented |
| Wayback Machine | wayback_search | No | Implemented |
| Google Calendar | calendar_events | Yes (OAuth2) | Implemented |
| Notion | notion_search | Yes | Implemented |

## Development Timeline

✅ Phase 1: Project structure and base utilities
✅ Phase 2: Search tools implementation
✅ Phase 3: Multimodal tools implementation
✅ Phase 4: File system tools implementation
✅ Phase 5: Public data tools implementation
✅ Phase 6: Private data tools implementation
✅ Phase 7: Documentation and testing
✅ Phase 8: Integration and verification

## Next Steps for Users

1. ✅ Read README.md
2. ⬜ Install dependencies
3. ⬜ Configure API keys
4. ⬜ Run test_imports.py
5. ⬜ Run quickstart.py
6. ⬜ Integrate with MCP client
7. ⬜ Start using tools!

## Support Resources

- **Documentation**: All .md files in this directory
- **Source Code**: Well-commented code in src/
- **Testing**: test_imports.py and quickstart.py
- **Configuration**: env.example with detailed comments

## License & Attribution

Part of the AI Agent Training Camp materials.

---

**Last Updated**: 2024
**Version**: 1.0.0
**Status**: Complete and ready for use
