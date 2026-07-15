#!/usr/bin/env python3
"""Simple startup test to verify the system can initialize"""

import os
# Set a dummy API key for testing initialization
os.environ["KIMI_API_KEY"] = "test_key"

from rich.console import Console

console = Console()

def test_imports():
    """Test all imports work"""
    try:
        from config import Config
        from chunker import ConversationChunker
        from indexer import MemoryIndexer
        from tools import MemoryTools
        from agent import UserMemoryRAGAgent
        from evaluator import UserMemoryEvaluator
        
        console.print("[green]✓ All imports successful[/green]")
        return True
    except Exception as e:
        console.print(f"[red]✗ Import error: {e}[/red]")
        return False

def test_initialization():
    """Test component initialization"""
    try:
        from config import Config
        from chunker import ConversationChunker
        from indexer import MemoryIndexer
        
        config = Config.from_env()
        console.print("[green]✓ Config loaded[/green]")
        
        chunker = ConversationChunker(config.chunking)
        console.print("[green]✓ Chunker initialized[/green]")
        
        indexer = MemoryIndexer(config.index)
        console.print("[green]✓ Indexer initialized[/green]")
        
        return True
    except Exception as e:
        console.print(f"[red]✗ Initialization error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    console.print("[bold]Testing Agentic RAG for User Memory - Startup[/bold]\n")
    
    imports_ok = test_imports()
    if imports_ok:
        init_ok = test_initialization()
        
        if init_ok:
            console.print("\n[bold green]✓ System startup successful![/bold green]")
            console.print("\nThe system is ready to use. To run the full demo:")
            console.print("1. Ensure the retrieval pipeline is running on port 4242")
            console.print("2. Set your API keys in .env file")
            console.print("3. Run: python main.py")
        else:
            console.print("\n[bold yellow]⚠ Initialization needs attention[/bold yellow]")
    else:
        console.print("\n[bold red]✗ Import errors need to be fixed[/bold red]")
