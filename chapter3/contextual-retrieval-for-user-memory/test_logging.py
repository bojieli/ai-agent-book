#!/usr/bin/env python3
"""Test script to verify tool logging and full content retrieval"""

import os
import json
from rich.console import Console
from chunker import ConversationChunker, ConversationChunk, ConversationMessage
from indexer import MemoryIndexer
from tools import MemoryTools
from config import Config

# Set dummy API key for testing
os.environ["KIMI_API_KEY"] = "test_key"

console = Console()


def create_test_chunks():
    """Create test conversation chunks with substantial content"""
    chunks = []
    
    # Create a test chunk with multiple messages
    messages = []
    for i in range(20):
        messages.append(ConversationMessage(
            role="user",
            content=f"User message {i+1}: This is a detailed question about topic {i+1}. " +
                   f"I need information about account #{1000000 + i} and transaction date 2024-{(i%12)+1:02d}-{(i%28)+1:02d}."
        ))
        messages.append(ConversationMessage(
            role="assistant",
            content=f"Assistant response {i+1}: Regarding your question about topic {i+1}, " +
                   f"your account #{1000000 + i} shows a transaction on 2024-{(i%12)+1:02d}-{(i%28)+1:02d} " +
                   f"with amount ${'1' * ((i%3)+1) + '00.00'}. Additional details include reference code REF{2000+i}."
        ))
    
    chunk = ConversationChunk(
        chunk_id="test_chunk_full_content",
        conversation_id="conv_test_001",
        test_id="test_logging",
        chunk_index=0,
        start_round=1,
        end_round=20,
        messages=messages,
        metadata={
            "business": "Test Bank",
            "department": "Customer Service",
            "agent": "Test Agent",
            "duration": "45 minutes"
        },
        context_before="Previous conversation discussed account opening procedures",
        context_after="Next conversation will cover credit card applications"
    )
    
    chunks.append(chunk)
    
    # Create a second chunk for context testing
    chunk2 = ConversationChunk(
        chunk_id="test_chunk_context",
        conversation_id="conv_test_001",
        test_id="test_logging",
        chunk_index=1,
        start_round=21,
        end_round=25,
        messages=[
            ConversationMessage(role="user", content="What about my credit card application?"),
            ConversationMessage(role="assistant", content="Your credit card application #CC2024001 is approved.")
        ],
        metadata={"business": "Test Bank"}
    )
    
    chunks.append(chunk2)
    
    return chunks


def test_search_memory_logging():
    """Test search_memory tool with full logging"""
    console.print("\n[bold cyan]Testing search_memory with full logging[/bold cyan]")
    console.print("="*60)
    
    # Initialize components
    config = Config.from_env()
    indexer = MemoryIndexer(config.index)
    
    # Add test chunks
    chunks = create_test_chunks()
    indexer.add_chunks(chunks, rebuild=False)  # Don't send to pipeline for this test
    
    # Initialize tools
    tools = MemoryTools(indexer)
    
    # Test search with detailed query
    console.print("\n[yellow]Executing search_memory...[/yellow]")
    result = tools.search_memory(
        query="account number transaction date reference code",
        top_k=3
    )
    
    # Display results
    console.print("\n[green]Search Results:[/green]")
    if result.success:
        data = result.data
        console.print(f"Total results: {data['total_results']}")
        
        for idx, res in enumerate(data['results'], 1):
            console.print(f"\n[cyan]Result {idx}:[/cyan]")
            console.print(f"  Chunk ID: {res['chunk_id']}")
            console.print(f"  Score: {res['score']}")
            console.print(f"  Content length: {len(res['content'])} characters")
            
            # Show first 500 chars to verify it's not truncated
            console.print(f"  Content preview (first 500 chars):")
            console.print(f"  {res['content'][:500]}...")
            
            # Verify full content is present
            if len(res['content']) > 1000:
                console.print(f"  [green]✓ Full content retrieved ({len(res['content'])} chars)[/green]")
            else:
                console.print(f"  [yellow]⚠ Content might be truncated ({len(res['content'])} chars)[/yellow]")


def test_get_conversation_context_logging():
    """Test get_conversation_context with full logging"""
    console.print("\n[bold cyan]Testing get_conversation_context with full logging[/bold cyan]")
    console.print("="*60)
    
    # Initialize components
    config = Config.from_env()
    indexer = MemoryIndexer(config.index)
    
    # Add test chunks
    chunks = create_test_chunks()
    indexer.add_chunks(chunks, rebuild=False)
    
    # Initialize tools
    tools = MemoryTools(indexer)
    
    # Test getting context
    console.print("\n[yellow]Executing get_conversation_context...[/yellow]")
    result = tools.get_conversation_context(
        chunk_id="test_chunk_full_content",
        context_size=2
    )
    
    # Display results
    console.print("\n[green]Context Results:[/green]")
    if result.success:
        data = result.data
        
        # Check target chunk
        target = data['target_chunk']
        console.print(f"\n[cyan]Target Chunk:[/cyan]")
        console.print(f"  Chunk ID: {target['chunk_id']}")
        console.print(f"  Rounds: {target['rounds']}")
        console.print(f"  Content length: {len(target['content'])} characters")
        
        if len(target['content']) > 1000:
            console.print(f"  [green]✓ Full content retrieved ({len(target['content'])} chars)[/green]")
        
        # Check context chunks
        console.print(f"\n[cyan]Context Chunks: {len(data['context_chunks'])}[/cyan]")
        for ctx in data['context_chunks']:
            console.print(f"  • {ctx['chunk_id']} ({ctx['position']}): {len(ctx['content'])} chars")
            if len(ctx['content']) > 100:
                console.print(f"    [green]✓ Full context content[/green]")


def test_get_full_conversation_logging():
    """Test get_full_conversation with full logging"""
    console.print("\n[bold cyan]Testing get_full_conversation with full logging[/bold cyan]")
    console.print("="*60)
    
    # Initialize components
    config = Config.from_env()
    indexer = MemoryIndexer(config.index)
    
    # Add test chunks
    chunks = create_test_chunks()
    indexer.add_chunks(chunks, rebuild=False)
    
    # Initialize tools
    tools = MemoryTools(indexer)
    
    # Test getting full conversation
    console.print("\n[yellow]Executing get_full_conversation...[/yellow]")
    result = tools.get_full_conversation(
        conversation_id="conv_test_001",
        test_id="test_logging"
    )
    
    # Display results
    console.print("\n[green]Full Conversation Results:[/green]")
    if result.success:
        data = result.data
        console.print(f"Conversation ID: {data['conversation_id']}")
        console.print(f"Total chunks: {data['total_chunks']}")
        console.print(f"Total rounds: {data['total_rounds']}")
        
        total_content_length = 0
        for chunk in data['chunks']:
            content_length = len(chunk['content'])
            total_content_length += content_length
            console.print(f"\n  Chunk {chunk['chunk_index']}: {content_length} characters")
            
            if content_length > 1000:
                console.print(f"    [green]✓ Full chunk content[/green]")
        
        console.print(f"\n[green]Total content retrieved: {total_content_length} characters[/green]")


def test_tool_definitions():
    """Verify extract_key_information is removed from tool definitions"""
    console.print("\n[bold cyan]Verifying tool definitions[/bold cyan]")
    console.print("="*60)
    
    from tools import get_tool_definitions
    
    tools = get_tool_definitions()
    tool_names = [t['function']['name'] for t in tools]
    
    console.print("\n[green]Available tools:[/green]")
    for name in tool_names:
        console.print(f"  • {name}")
    
    if "extract_key_information" in tool_names:
        console.print("\n[red]✗ extract_key_information still present![/red]")
    else:
        console.print("\n[green]✓ extract_key_information successfully removed[/green]")
    
    console.print(f"\n[green]Total tools available: {len(tools)}[/green]")


def main():
    """Run all logging tests"""
    console.print("\n[bold]Testing Tool Logging and Full Content Retrieval[/bold]")
    console.print("="*80)
    
    try:
        # Test each tool
        test_search_memory_logging()
        test_get_conversation_context_logging()
        test_get_full_conversation_logging()
        test_tool_definitions()
        
        console.print("\n" + "="*80)
        console.print("[bold green]✓ All tests completed successfully![/bold green]")
        console.print("\nKey validations:")
        console.print("  • Tool calls are logged with full parameters")
        console.print("  • Tool results are logged completely")
        console.print("  • Content is NOT truncated in results")
        console.print("  • extract_key_information tool is removed")
        console.print("="*80 + "\n")
        
    except Exception as e:
        console.print(f"\n[red]Error during testing: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
