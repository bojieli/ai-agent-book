"""
Test script for new perception tools: crypto prices, location search, and POI search.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from public_data_tools import get_crypto_price, search_location, search_poi

logging.basicConfig(level=logging.INFO)


async def test_new_tools():
    """Test the new perception tools."""
    
    print("\n" + "="*80)
    print("NEW PERCEPTION TOOLS - TEST")
    print("="*80)
    
    # Test 1: Crypto Price
    print("\n📝 Test 1: Cryptocurrency Price (Bitcoin)")
    print("-" * 80)
    try:
        result = await get_crypto_price("btc", "usd")
        data = json.loads(result.text)
        if data['success']:
            msg = data['message']
            print(f"✅ {msg['symbol']}: ${msg['current_price']:,.2f} USD")
            print(f"   24h Change: {msg['price_change_24h_percent']:.2f}%")
            print(f"   Market Cap: ${msg['market_cap']:,.0f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Crypto Price - Ethereum
    print("\n📝 Test 2: Cryptocurrency Price (Ethereum)")
    print("-" * 80)
    try:
        result = await get_crypto_price("eth", "eur")
        data = json.loads(result.text)
        if data['success']:
            msg = data['message']
            print(f"✅ {msg['symbol']}: €{msg['current_price']:,.2f} EUR")
            print(f"   24h Volume: €{msg['volume_24h']:,.0f}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Location Search
    print("\n📝 Test 3: Location Search (Eiffel Tower)")
    print("-" * 80)
    try:
        result = await search_location("Eiffel Tower", limit=3)
        data = json.loads(result.text)
        if data['success']:
            locations = data['message']['locations']
            print(f"✅ Found {len(locations)} locations:")
            for loc in locations[:2]:
                print(f"   - {loc['display_name']}")
                print(f"     Coordinates: ({loc['latitude']}, {loc['longitude']})")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Location Search with Country Filter
    print("\n📝 Test 4: Location Search (Paris, France only)")
    print("-" * 80)
    try:
        result = await search_location("Paris", limit=3, country_code="fr")
        data = json.loads(result.text)
        if data['success']:
            locations = data['message']['locations']
            print(f"✅ Found {len(locations)} locations in France:")
            for loc in locations[:2]:
                print(f"   - {loc['display_name']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: POI Search (Restaurants near Eiffel Tower)
    print("\n📝 Test 5: POI Search (Restaurants near Eiffel Tower)")
    print("-" * 80)
    try:
        # Eiffel Tower coordinates
        latitude = 48.8584
        longitude = 2.2945
        
        result = await search_poi("restaurant", latitude, longitude, radius=500, limit=5)
        data = json.loads(result.text)
        if data['success']:
            pois = data['message']['pois']
            print(f"✅ Found {len(pois)} restaurants:")
            for poi in pois[:3]:
                print(f"   - {poi['name']}")
                if poi.get('cuisine'):
                    print(f"     Cuisine: {poi['cuisine']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: POI Search (Coffee shops in San Francisco)
    print("\n📝 Test 6: POI Search (Coffee shops in San Francisco)")
    print("-" * 80)
    try:
        # San Francisco downtown coordinates
        latitude = 37.7749
        longitude = -122.4194
        
        result = await search_poi("cafe", latitude, longitude, radius=1000, limit=5)
        data = json.loads(result.text)
        if data['success']:
            pois = data['message']['pois']
            print(f"✅ Found {len(pois)} cafes:")
            for poi in pois[:3]:
                print(f"   - {poi['name']}")
                if poi.get('opening_hours'):
                    print(f"     Hours: {poi['opening_hours']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print("\nℹ️  All tests use free, open APIs - no API keys required!")
    print("\n")


if __name__ == "__main__":
    asyncio.run(test_new_tools())
