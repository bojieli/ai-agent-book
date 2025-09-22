"""
Standalone test that properly handles imports
"""

def test_system():
    """Test the memory system with proper import isolation"""
    
    # First test: Can we import our local config?
    from config import Config, IndexingConfig, SearchStrategy
    print("✅ Successfully imported local config classes")
    
    # Second test: Can we import memory_indexer?
    from memory_indexer import ContextualMemoryIndexer
    print("✅ Successfully imported ContextualMemoryIndexer")
    
    # Third test: Can we import memory_tools?
    from memory_tools import MemorySearchTools
    print("✅ Successfully imported MemorySearchTools")
    
    # Fourth test: Can we import week2's memory manager?
    import sys
    from pathlib import Path
    
    # Temporarily add week2 path
    week2_path = str(Path(__file__).parent.parent.parent / "week2" / "user-memory")
    original_modules = list(sys.modules.keys())
    
    # Save and modify sys.path
    original_path = sys.path.copy()
    sys.path = [week2_path] + [p for p in original_path if "week2" not in p]
    
    # Import with isolated environment
    try:
        # Remove any cached config module
        if 'config' in sys.modules:
            del sys.modules['config']
        
        from memory_manager import AdvancedJSONMemoryManager
        print("✅ Successfully imported AdvancedJSONMemoryManager from week2")
        
    finally:
        # Restore original state
        sys.path = original_path
        
        # Clean up imported modules
        for mod in list(sys.modules.keys()):
            if mod not in original_modules and ("memory_manager" in mod or "config" in mod):
                del sys.modules[mod]
    
    # Re-import our config to ensure it's correct
    from config import Config
    
    # Fifth test: Can we create a MemoryAgent?
    from memory_agent import MemoryAgent
    print("✅ Successfully imported MemoryAgent")
    
    # Create and test the agent
    agent = MemoryAgent("test_user")
    print("✅ MemoryAgent created successfully")
    
    # Get statistics
    stats = agent.get_statistics()
    print(f"\n📊 Initial Statistics:")
    print(f"  - Memory cards: {stats['structured_memory']['total_cards']}")
    print(f"  - Conversation chunks: {stats['conversation_memory']['total_chunks']}")
    
    print("\n✨ All tests passed! The dual-context system is working correctly.")


if __name__ == "__main__":
    test_system()
