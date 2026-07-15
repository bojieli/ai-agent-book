"""
Quick start script to test the perception tools MCP server.
"""
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from search_tools import search_web, download_file
from multimodal_tools import read_webpage
from filesystem_tools import read_file, grep_search
from public_data_tools import get_weather, search_wikipedia, convert_currency


logging.basicConfig(level=logging.INFO)


async def test_tools():
    """Test various perception tools."""
    
    print("\n" + "="*80)
    print("PERCEPTION TOOLS MCP SERVER - QUICKSTART")
    print("="*80)
    
    # Test 1: Web Search
    print("\n📝 Test 1: Web Search")
    print("-" * 80)
    try:
        result = await search_web("Python programming", num_results=3)
        data = json.loads(result.text)
        if data['success']:
            print(f"✅ Found {data['message']['count']} results")
            if data['message']['results']:
                for idx, result_item in enumerate(data['message']['results'], 1):
                    print(f"\n[{idx}] {result_item['title']}")
                    print(f"    URL: {result_item['url']}")
                    if result_item.get('snippet'):
                        print(f"    Snippet: {result_item['snippet']}")
        else:
            print(f"⚠️  Search API not configured: {data['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Wikipedia Search
    print("\n📝 Test 2: Wikipedia Search")
    print("-" * 80)
    try:
        result = await search_wikipedia("Artificial Intelligence", sentences=3)
        data = json.loads(result.text)
        if data['success']:
            print(f"✅ Article: {data['message']['title']}")
            print(f"Summary: {data['message']['summary'][:200]}...")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Currency Conversion
    print("\n📝 Test 3: Currency Conversion")
    print("-" * 80)
    try:
        result = await convert_currency(100, "USD", "EUR")
        data = json.loads(result.text)
        if data['success']:
            converted = data['message']['converted_amount']
            print(f"✅ 100 USD = {converted:.2f} EUR")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Weather
    print("\n📝 Test 4: Weather Information")
    print("-" * 80)
    try:
        result = await get_weather("London")
        data = json.loads(result.text)
        if data['success']:
            temp = data['message']['temperature']
            desc = data['message']['description']
            print(f"✅ London: {temp}°C - {desc}")
        else:
            print(f"⚠️  Weather API not configured: {data['message']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 5: Web Page Reading
    print("\n📝 Test 5: Web Page Reading")
    print("-" * 80)
    try:
        result = await read_webpage("https://www.example.com", extract_text=True)
        data = json.loads(result.text)
        if data['success']:
            title = data['message']['title']
            text_len = data['message'].get('text_length', 0)
            print(f"✅ Page: {title}")
            print(f"Text length: {text_len} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 6: File Operations
    print("\n📝 Test 6: File Operations (Reading this script)")
    print("-" * 80)
    try:
        script_path = str(Path(__file__).resolve())
        result = await read_file(script_path, max_length=500)
        data = json.loads(result.text)
        if data['success']:
            size = data['message']['size_bytes']
            print(f"✅ Read {size} bytes from {Path(script_path).name}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*80)
    print("QUICKSTART COMPLETE")
    print("="*80)
    print("\nℹ️  Note: Some tests may fail if API keys are not configured.")
    print("   Check env.example and configure your .env file for full functionality.")
    print("\n")


if __name__ == "__main__":
    asyncio.run(test_tools())
