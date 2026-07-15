#!/usr/bin/env python3
"""Demonstration of agent tool logging with full content"""

import os
import json
import logging
from rich.console import Console
from chunker import ConversationChunker, ConversationChunk, ConversationMessage
from indexer import MemoryIndexer
from agent import UserMemoryRAGAgent
from config import Config

# Set up logging to see agent logs
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format to show just the message
)

# Set dummy API key for demo
os.environ["KIMI_API_KEY"] = "test_key"

console = Console()


def create_demo_conversation():
    """Create a demo conversation with important information"""
    messages = [
        ConversationMessage(role="user", content="Hi, I'd like to open a checking account."),
        ConversationMessage(role="assistant", content="I'd be happy to help you open a checking account. May I have your full name?"),
        ConversationMessage(role="user", content="John Michael Smith"),
        ConversationMessage(role="assistant", content="Thank you, Mr. Smith. What's your date of birth?"),
        ConversationMessage(role="user", content="March 15, 1985"),
        ConversationMessage(role="assistant", content="Perfect. And your Social Security Number?"),
        ConversationMessage(role="user", content="123-45-6789"),
        ConversationMessage(role="assistant", content="Thank you. What's your current address?"),
        ConversationMessage(role="user", content="456 Oak Avenue, Springfield, IL 62701"),
        ConversationMessage(role="assistant", content="Great. And a phone number where we can reach you?"),
        ConversationMessage(role="user", content="555-0123"),
        ConversationMessage(role="assistant", content="Excellent. I've set up your account. Your new account number is 4429853327."),
        ConversationMessage(role="user", content="Great! What's the routing number?"),
        ConversationMessage(role="assistant", content="The routing number for our Springfield branch is 071000013."),
        ConversationMessage(role="user", content="Perfect, thank you for your help!"),
        ConversationMessage(role="assistant", content="You're welcome! Your debit card will arrive in 7-10 business days."),
    ]
    
    chunk = ConversationChunk(
        chunk_id="demo_bank_account_001",
        conversation_id="bank_conv_001",
        test_id="demo_test",
        chunk_index=0,
        start_round=1,
        end_round=8,
        messages=messages,
        metadata={
            "business": "First National Bank",
            "department": "New Accounts",
            "date": "2024-11-15",
            "agent": "Sarah Johnson"
        }
    )
    
    return [chunk]


def demonstrate_agent_logging():
    """Demonstrate how the agent logs tool calls and results"""
    console.print("\n[bold cyan]Agent Tool Logging Demonstration[/bold cyan]")
    console.print("="*80)
    console.print("[yellow]Note: Watch for tool call parameters and full results in the logs[/yellow]\n")
    
    # Initialize configuration
    config = Config.from_env()
    config.agent.enable_reasoning = True  # Enable reasoning for more detailed logs
    
    # Initialize indexer and add demo conversation
    indexer = MemoryIndexer(config.index)
    chunks = create_demo_conversation()
    
    # Manually add chunks without pipeline indexing for demo
    for chunk in chunks:
        indexer.chunks[chunk.chunk_id] = chunk
        indexer.chunk_texts[chunk.chunk_id] = chunk.to_text()
    
    # Initialize agent
    agent = UserMemoryRAGAgent(indexer, config)
    
    # Test question that will trigger tool usage
    test_question = "What is the customer's account number and when will they receive their debit card?"
    
    console.print(f"\n[bold]Test Question:[/bold] {test_question}")
    console.print("\n[yellow]Agent processing (watch the tool logs below):[/yellow]\n")
    console.print("="*80 + "\n")
    
    # This would normally call the LLM, but for demo we'll simulate tool calls
    # In a real scenario, the agent.answer_question() method would be called
    
    # Simulate what the agent would do:
    from tools import MemoryTools
    tools = MemoryTools(indexer)
    
    # Simulate search_memory call (this is what the agent would do)
    console.print("[dim]Agent would execute:[/dim]")
    result1 = agent._execute_tool("search_memory", {
        "query": "account number debit card",
        "top_k": 3,
        "filter_test_id": "demo_test"
    })
    
    # The logging happens automatically in _execute_tool
    
    console.print("\n[dim]Agent might also execute:[/dim]")
    result2 = agent._execute_tool("get_full_conversation", {
        "conversation_id": "bank_conv_001",
        "test_id": "demo_test"
    })
    
    console.print("\n" + "="*80)
    console.print("[green]Demonstration complete![/green]")
    console.print("\nKey observations:")
    console.print("  1. Tool call parameters are logged in full")
    console.print("  2. Tool results show complete content (not truncated)")
    console.print("  3. Each tool call is clearly separated with dividers")
    console.print("  4. JSON formatting makes results easy to read")


def main():
    """Run the demonstration"""
    console.print("\n[bold]Agentic RAG - Tool Logging Demonstration[/bold]")
    console.print("This shows how tool calls and results are logged to the console\n")
    
    try:
        demonstrate_agent_logging()
        
    except Exception as e:
        console.print(f"\n[red]Error during demonstration: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
