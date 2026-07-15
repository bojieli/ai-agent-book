#!/usr/bin/env python3
"""
Test script to verify provider configuration
"""

import os
from agent import ContextAwareAgent, ContextMode

def test_providers():
    """Test different provider configurations"""
    
    print("\n" + "="*60)
    print("🧪 PROVIDER CONFIGURATION TEST")
    print("="*60)
    
    # Test SiliconFlow
    sf_key = os.getenv("SILICONFLOW_API_KEY")
    if sf_key:
        print("\n✅ SiliconFlow API key found")
        try:
            agent = ContextAwareAgent(sf_key, ContextMode.FULL, provider="siliconflow")
            print(f"   Provider: {agent.provider}")
            print(f"   Model: {agent.model}")
            print(f"   Base URL: {agent.client.base_url}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    else:
        print("\n⚠️ SiliconFlow API key not found (SILICONFLOW_API_KEY)")
    
    # Test Doubao
    ark_key = os.getenv("ARK_API_KEY")
    if ark_key:
        print("\n✅ Doubao/ARK API key found")
        try:
            agent = ContextAwareAgent(ark_key, ContextMode.FULL, provider="doubao")
            print(f"   Provider: {agent.provider}")
            print(f"   Model: {agent.model}")
            print(f"   Base URL: {agent.client.base_url}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    else:
        print("\n⚠️ Doubao/ARK API key not found (ARK_API_KEY)")
    
    # Test custom model
    if sf_key:
        print("\n🔧 Testing custom model specification:")
        try:
            agent = ContextAwareAgent(sf_key, ContextMode.FULL, 
                                    provider="siliconflow", 
                                    model="Qwen/QwQ-32B")
            print(f"   Provider: {agent.provider}")
            print(f"   Custom Model: {agent.model}")
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print("\n" + "="*60)
    print("Test complete!")
    
    # Show usage examples
    print("\n📖 Usage Examples:")
    print("-"*40)
    
    if sf_key:
        print("\n# Using SiliconFlow:")
        print("python main.py --provider siliconflow")
        print("python main.py --provider siliconflow --model Qwen/QwQ-32B")
    
    if ark_key:
        print("\n# Using Doubao:")
        print("python main.py --provider doubao")
        print("python main.py --provider doubao --model doubao-seed-1-6-thinking-250715")
    
    if not sf_key and not ark_key:
        print("\n⚠️ No API keys found. Please set one of:")
        print("   export SILICONFLOW_API_KEY=your_key")
        print("   export ARK_API_KEY=your_key")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_providers()
