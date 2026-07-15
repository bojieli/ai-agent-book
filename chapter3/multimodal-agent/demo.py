"""
Demo script showcasing different extraction techniques
"""

import asyncio
import sys
from pathlib import Path
from typing import List, Tuple

from agent import MultimodalAgent, MultimodalContent
from config import ExtractionMode


async def compare_extraction_modes(file_path: str, query: str):
    """Compare different extraction modes for the same content"""
    
    print(f"\n{'='*80}")
    print(f"COMPARING EXTRACTION MODES")
    print(f"File: {file_path}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Determine content type
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        content_type = "pdf"
    elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        content_type = "image"
    elif suffix in ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg']:
        content_type = "audio"
    else:
        print(f"Unsupported file type: {suffix}")
        return
    
    # Test with native mode (Gemini)
    print("\n" + "-"*60)
    print("1. NATIVE MULTIMODAL MODE (Gemini 2.5 Pro)")
    print("-"*60)
    
    agent_native = MultimodalAgent(
        model="gemini-2.5-pro",
        mode=ExtractionMode.NATIVE,
        enable_tools=False
    )
    
    content = MultimodalContent(type=content_type, path=file_path)
    
    try:
        result = await agent_native.process_multimodal_content(content, query)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with extract-to-text mode
    print("\n" + "-"*60)
    print("2. EXTRACT TO TEXT MODE")
    print("-"*60)
    
    agent_extract = MultimodalAgent(
        model="gemini-2.5-pro",
        mode=ExtractionMode.EXTRACT_TO_TEXT,
        enable_tools=False
    )
    
    try:
        # First extract the content
        print("Extracting content to text...")
        extracted = await agent_extract._extract_single_content(content)
        print("\nExtracted text:")
        print(extracted)
        
        # Then answer the query
        print(f"\nAnswering query with extracted text...")
        result = await agent_extract._answer_with_context(extracted, query)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    
    # Test with extract-to-text + tools mode
    print("\n" + "-"*60)
    print("3. EXTRACT TO TEXT + MULTIMODAL TOOLS")
    print("-"*60)
    
    agent_tools = MultimodalAgent(
        model="gemini-2.5-pro",
        mode=ExtractionMode.EXTRACT_TO_TEXT,
        enable_tools=True
    )
    
    try:
        print("Using extract-to-text with tools enabled for follow-up questions...")
        
        # Initial processing
        extracted = await agent_tools._extract_single_content(content)
        print(f"Extracted {len(extracted)} characters")
        
        # Simulate a conversation with follow-up
        async for chunk in agent_tools.chat(query, content, stream=True):
            print(chunk, end="", flush=True)
        print()
        
        # Follow-up question that might use tools
        if content_type == "image":
            follow_up = f"What colors are dominant in the image at {file_path}?"
        elif content_type == "pdf":
            follow_up = f"What specific data or figures are mentioned in the PDF at {file_path}?"
        else:  # audio
            follow_up = f"What is the tone or mood of the audio at {file_path}?"
            
        print(f"\nFollow-up question: {follow_up}")
        async for chunk in agent_tools.chat(follow_up, None, stream=True):
            print(chunk, end="", flush=True)
        print()
        
    except Exception as e:
        print(f"Error: {e}")


async def compare_models(file_path: str, query: str):
    """Compare different models for the same task"""
    
    print(f"\n{'='*80}")
    print(f"COMPARING MODELS")
    print(f"File: {file_path}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    # Determine content type
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    if suffix == '.pdf':
        content_type = "pdf"
    elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
        content_type = "image"
    elif suffix in ['.mp3', '.wav', '.m4a', '.flac', '.aac', '.ogg']:
        content_type = "audio"
    else:
        print(f"Unsupported file type: {suffix}")
        return
        
    content = MultimodalContent(type=content_type, path=file_path)
    
    # Test with different models
    models = ["gemini-2.5-pro", "gpt-4o", "doubao-1.6"]
    
    for model in models:
        print("\n" + "-"*60)
        print(f"Model: {model}")
        print("-"*60)
        
        try:
            # Skip if API key not configured
            from config import Config
            config = Config()
            
            if model == "gemini-2.5-pro" and not config.gemini_api_key:
                print("Skipping: Gemini API key not configured")
                continue
            elif model in ["gpt-4o", "gpt-5"] and not config.openai_api_key:
                print("Skipping: OpenAI API key not configured")
                continue
            elif model == "doubao-1.6" and not config.doubao_api_key:
                print("Skipping: Doubao API key not configured")
                continue
            
            agent = MultimodalAgent(
                model=model,
                mode=ExtractionMode.NATIVE if content_type != "audio" or model == "gemini-2.5-pro" else ExtractionMode.EXTRACT_TO_TEXT,
                enable_tools=False
            )
            
            result = await agent.process_multimodal_content(content, query)
            print(result)
            
        except Exception as e:
            print(f"Error: {e}")


async def demo_conversation_with_tools():
    """Demonstrate a conversation with multimodal tools"""
    
    print(f"\n{'='*80}")
    print("DEMO: CONVERSATION WITH MULTIMODAL TOOLS")
    print(f"{'='*80}\n")
    
    agent = MultimodalAgent(
        model="gemini-2.5-pro",
        mode=ExtractionMode.EXTRACT_TO_TEXT,
        enable_tools=True
    )
    
    # Simulate a conversation
    conversations = [
        ("I need help analyzing some documents. I have PDFs, images, and audio files.", None),
        ("Can you analyze the image at test_files/sample.jpg and tell me what you see?", None),
        ("Now analyze the PDF at test_files/document.pdf and summarize its main points.", None),
        ("What's in the audio file at test_files/recording.mp3?", None),
        ("Based on all these files, what's the common theme?", None)
    ]
    
    for message, content in conversations:
        print(f"\nUser: {message}")
        print("Assistant: ", end="", flush=True)
        
        try:
            async for chunk in agent.chat(message, content, stream=True):
                print(chunk, end="", flush=True)
            print()
        except Exception as e:
            print(f"\nError: {e}")
            print("(File might not exist - this is a demo)")


async def main():
    """Run all demos"""
    
    import sys
    
    print("="*80)
    print("MULTIMODAL AGENT DEMO")
    print("="*80)
    
    # Check for command line arguments
    if len(sys.argv) > 2:
        file_path = sys.argv[1]
        query = sys.argv[2]
        
        # Run comparison demos
        await compare_extraction_modes(file_path, query)
        await compare_models(file_path, query)
        
    else:
        print("\nUsage: python demo.py <file_path> <query>")
        print("Example: python demo.py document.pdf 'What is the main topic?'")
        print("\nRunning demo conversation instead...\n")
        
        # Run conversation demo
        await demo_conversation_with_tools()


if __name__ == "__main__":
    asyncio.run(main())
