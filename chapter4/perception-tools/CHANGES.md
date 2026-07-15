# Perception Tools - Updates & Changes

## Summary

Updated the Perception Tools MCP Server to use **100% free, open APIs** that require **no API keys**. This makes the tool immediately usable without any setup or registration.

## Changes Made

### 1. **Weather API** - Replaced OpenWeather with Open-Meteo

**Previous**: OpenWeather API (required API key)
**New**: [Open-Meteo](https://open-meteo.com/) (free, no API key required)

**Benefits**:
- No registration or API key needed
- Automatic geocoding of city names
- High-quality weather data from national weather services
- Hourly resolution with up to 16-day forecasts
- 80 years of historical weather data available

**Implementation**:
- `get_weather(location, latitude=None, longitude=None)`
- Automatically geocodes location names to coordinates
- Returns temperature, humidity, wind speed, precipitation, and weather description

---

### 2. **Web Search** - Replaced Google Custom Search with DuckDuckGo

**Previous**: Google Custom Search API (required API key and CSE ID)
**New**: DuckDuckGo HTML search (free, no API key required)

**Benefits**:
- No registration or API key needed
- Privacy-focused search engine
- Clean, ad-free results
- No usage limits

**Implementation**:
- `search_web(query, num_results=5, region="wt-wt")`
- Scrapes DuckDuckGo HTML results
- Returns title, URL, and snippet for each result

---

### 3. **Cryptocurrency Prices** - NEW TOOL ✨

**API**: [CoinGecko](https://www.coingecko.com/) (free, no API key required)

**Features**:
- Real-time cryptocurrency prices
- Support for 15+ major cryptocurrencies (BTC, ETH, SOL, etc.)
- Market cap, 24h volume, and price change data
- Multi-currency support (USD, EUR, GBP, etc.)

**Implementation**:
- `get_crypto_price(symbol, vs_currency="usd")`
- Maps common symbols (btc → bitcoin, eth → ethereum)
- Returns comprehensive price and market data

**Example**:
```python
result = await get_crypto_price("btc", "usd")
# Returns: BTC price, market cap, 24h volume, 24h change
```

---

### 4. **Location Search** - NEW TOOL ✨

**API**: [Nominatim (OpenStreetMap)](https://nominatim.openstreetmap.org/) (free, no API key required)

**Features**:
- Geocode any location worldwide
- Search landmarks, cities, addresses
- Detailed address information
- Country filtering option

**Implementation**:
- `search_location(query, limit=5, country_code=None)`
- Returns latitude, longitude, and detailed address
- Importance ranking for result relevance

**Example**:
```python
result = await search_location("Eiffel Tower")
# Returns: coordinates, full address, location type
```

---

### 5. **Point of Interest (POI) Search** - NEW TOOL ✨

**API**: [Overpass API (OpenStreetMap)](https://overpass-api.de/) (free, no API key required)

**Features**:
- Find restaurants, cafes, hotels, ATMs, hospitals, etc.
- Search within specified radius
- Rich metadata (phone, website, opening hours, cuisine)
- Worldwide coverage from OpenStreetMap data

**Implementation**:
- `search_poi(query, latitude, longitude, radius=1000, limit=10)`
- Searches for amenities, shops, tourism POIs
- Returns name, type, coordinates, and metadata

**Example**:
```python
result = await search_poi("restaurant", 48.8584, 2.2945, radius=500)
# Returns: nearby restaurants with details
```

---

## Existing Free APIs (Already Implemented)

These tools were already using free APIs:

1. **Stock Prices** - Yahoo Finance (free, no API key)
2. **Currency Conversion** - ExchangeRate-API (free, no API key)
3. **Wikipedia** - Wikipedia API (free, no API key)
4. **ArXiv** - ArXiv API (free, no API key)
5. **Wayback Machine** - Internet Archive (free, no API key)

---

## Complete List of Free Tools

### 🔍 Search & Discovery
- ✅ Web Search (DuckDuckGo)
- ✅ Knowledge Base Search
- ✅ Wikipedia Search
- ✅ ArXiv Search
- ✅ Location Search (OpenStreetMap)
- ✅ POI Search (OpenStreetMap)

### 🌐 Public Data
- ✅ Weather (Open-Meteo)
- ✅ Stock Prices (Yahoo Finance)
- ✅ Crypto Prices (CoinGecko)
- ✅ Currency Conversion (ExchangeRate-API)

### 📄 Content Processing
- ✅ Web Page Reader
- ✅ Document Reader (PDF, DOCX, PPTX)
- ✅ File Operations
- ✅ Grep Search

### 🕰️ Historical Data
- ✅ Wayback Machine

---

## Testing

All new and updated tools have been tested and verified:

```bash
# Test original tools
python quickstart.py

# Test new tools
python test_new_tools.py
```

All tests pass successfully with no API keys required!

---

## Documentation Updates

- ✅ Updated README.md with new tool descriptions
- ✅ Updated env.example to reflect free APIs
- ✅ Added comprehensive parameter documentation
- ✅ Highlighted "No API Keys Required" throughout

---

## Benefits of These Changes

1. **Zero Setup** - Works immediately after `pip install -r requirements.txt`
2. **No Cost** - All APIs are free for reasonable use
3. **No Registration** - No need to sign up or manage API keys
4. **Privacy** - DuckDuckGo and OpenStreetMap don't track users
5. **Production Ready** - APIs are stable and well-maintained
6. **Global Coverage** - Weather, maps, and location data worldwide

---

## API Sources & Links

| Tool | API Provider | Documentation |
|------|-------------|---------------|
| Weather | Open-Meteo | https://open-meteo.com/ |
| Web Search | DuckDuckGo | https://duckduckgo.com/ |
| Crypto Prices | CoinGecko | https://www.coingecko.com/en/api |
| Location Search | Nominatim (OSM) | https://nominatim.openstreetmap.org/ |
| POI Search | Overpass API (OSM) | https://overpass-api.de/ |
| Stock Prices | Yahoo Finance | https://finance.yahoo.com/ |
| Currency | ExchangeRate-API | https://www.exchangerate-api.com/ |
| Wikipedia | Wikipedia API | https://www.mediawiki.org/wiki/API |
| ArXiv | ArXiv API | https://arxiv.org/help/api |

---

## Acknowledgments

Special thanks to:
- Open-Meteo for providing free, high-quality weather data
- OpenStreetMap community for maintaining global map data
- CoinGecko for free cryptocurrency market data
- DuckDuckGo for privacy-respecting search

---

## Next Steps

Potential future enhancements:
- Add rate limiting to respect API usage policies
- Implement caching for frequently accessed data
- Add more cryptocurrency exchanges
- Support for reverse geocoding
- Route planning with OpenStreetMap
