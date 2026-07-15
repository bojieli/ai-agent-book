# Quick Start Guide - Perception Tools

## 🚀 Zero Setup Required!

All tools work immediately with **no API keys** needed.

## Installation

```bash
cd projects/week4/perception-tools
pip install -r requirements.txt
```

## Run Tests

```bash
# Test original tools
python quickstart.py

# Test new crypto/location/POI tools
python test_new_tools.py
```

## Usage Examples

### 1. Cryptocurrency Prices 💰

```python
from public_data_tools import get_crypto_price

# Get Bitcoin price in USD
result = await get_crypto_price("btc", "usd")

# Get Ethereum price in EUR
result = await get_crypto_price("eth", "eur")

# Supported: btc, eth, sol, ada, doge, bnb, xrp, usdt, usdc, etc.
```

### 2. Location Search 📍

```python
from public_data_tools import search_location

# Search any location
result = await search_location("Eiffel Tower", limit=5)

# Filter by country
result = await search_location("Paris", country_code="fr")

# Search businesses
result = await search_location("Starbucks in Seattle")
```

### 3. POI Search 🗺️

```python
from public_data_tools import search_poi

# Find restaurants near a location
result = await search_poi(
    query="restaurant",
    latitude=48.8584,
    longitude=2.2945,
    radius=500,  # meters
    limit=10
)

# Find cafes
result = await search_poi("cafe", 37.7749, -122.4194, radius=1000)

# Find hotels, hospitals, ATMs, etc.
result = await search_poi("hotel", lat, lon)
```

### 4. Weather ⛅

```python
from public_data_tools import get_weather

# Get weather by city name
result = await get_weather("London")

# Get weather by coordinates
result = await get_weather("Paris", latitude=48.8566, longitude=2.3522)
```

### 5. Web Search 🔍

```python
from search_tools import search_web

# Search the web
result = await search_web("Python programming", num_results=5)

# Regional search
result = await search_web("news", region="us-en")
```

### 6. Stock Prices 📈

```python
from public_data_tools import get_stock_price

# Get stock price
result = await get_stock_price("AAPL")
result = await get_stock_price("TSLA")
```

## All Available Free APIs

| Tool | Use Case | Example |
|------|----------|---------|
| 🔍 **Web Search** | Search the internet | `search_web("AI news")` |
| 🌤️ **Weather** | Current weather | `get_weather("Tokyo")` |
| 💰 **Crypto Prices** | Cryptocurrency data | `get_crypto_price("btc")` |
| 📈 **Stock Prices** | Stock market data | `get_stock_price("GOOGL")` |
| 💱 **Currency** | Exchange rates | `convert_currency(100, "USD", "EUR")` |
| 📍 **Location Search** | Find places | `search_location("Eiffel Tower")` |
| 🗺️ **POI Search** | Find nearby places | `search_poi("restaurant", lat, lon)` |
| 📚 **Wikipedia** | Encyclopedia | `search_wikipedia("AI")` |
| 🔬 **ArXiv** | Academic papers | `search_arxiv("deep learning")` |
| 🕰️ **Wayback Machine** | Archived pages | `search_wayback("example.com")` |

## Common Use Cases

### Travel Planning

```python
# 1. Find a city
location = await search_location("Paris, France")
lat, lon = location['latitude'], location['longitude']

# 2. Check weather
weather = await get_weather("Paris")

# 3. Find hotels
hotels = await search_poi("hotel", lat, lon, radius=2000)

# 4. Find restaurants
restaurants = await search_poi("restaurant", lat, lon, radius=1000)

# 5. Convert currency
cost = await convert_currency(100, "USD", "EUR")
```

### Investment Research

```python
# 1. Get stock price
stock = await get_stock_price("AAPL")

# 2. Get crypto prices
btc = await get_crypto_price("btc")
eth = await get_crypto_price("eth")

# 3. Check currency rates
rate = await convert_currency(1, "USD", "EUR")

# 4. Research on Wikipedia
info = await search_wikipedia("Apple Inc")
```

### Content Research

```python
# 1. Web search
results = await search_web("climate change 2024")

# 2. Academic papers
papers = await search_arxiv("climate change")

# 3. Wikipedia
wiki = await search_wikipedia("Climate change")

# 4. Historical data
archive = await search_wayback("ipcc.ch", year=2020)
```

## Response Format

All tools return a standardized JSON response:

```json
{
  "success": true,
  "message": {
    // Tool-specific data here
  },
  "metadata": {
    "provider": "API name",
    "api_key_required": false
  }
}
```

## Tips & Best Practices

1. **Rate Limiting**: Be respectful of free APIs - don't make excessive requests
2. **Caching**: Cache results when possible to reduce API calls
3. **Error Handling**: Always check the `success` field in responses
4. **User Agent**: Tools use appropriate User-Agent headers for API compliance

## Need Help?

- 📖 See `README.md` for full documentation
- 🔄 See `CHANGES.md` for what's new
- 🧪 Run `python test_new_tools.py` to verify everything works

## API Credits

- [Open-Meteo](https://open-meteo.com/) - Weather data
- [CoinGecko](https://www.coingecko.com/) - Crypto prices
- [OpenStreetMap](https://www.openstreetmap.org/) - Maps & POI data
- [DuckDuckGo](https://duckduckgo.com/) - Web search
- [Yahoo Finance](https://finance.yahoo.com/) - Stock prices
- [ExchangeRate-API](https://www.exchangerate-api.com/) - Currency rates
