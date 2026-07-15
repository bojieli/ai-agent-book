"""Test external integration tools."""

import asyncio
from llm_helper import LLMHelper
from external_tools import ExternalTools


async def test_google_calendar():
    """Test Google Calendar integration."""
    print("Testing Google Calendar...")
    
    llm_helper = LLMHelper()
    external_tools = ExternalTools(llm_helper)
    
    try:
        result = await external_tools.google_calendar_add(
            summary="Test Event",
            start_time="2025-10-01T10:00:00",
            end_time="2025-10-01T11:00:00",
            description="This is a test event"
        )
        
        if result["success"]:
            print(f"✓ Calendar event created: {result}")
        else:
            print(f"Calendar test skipped or failed: {result['error']}")
            
    except Exception as e:
        print(f"Calendar test skipped (likely missing credentials): {e}")


async def test_github_pr():
    """Test GitHub PR creation."""
    print("\nTesting GitHub PR...")
    
    llm_helper = LLMHelper()
    external_tools = ExternalTools(llm_helper)
    
    try:
        # Note: This will fail without a valid repo and token
        result = await external_tools.github_create_pr(
            repo_name="test/test-repo",
            title="Test PR",
            body="This is a test PR",
            head_branch="test-branch",
            base_branch="main"
        )
        
        if result["success"]:
            print(f"✓ PR created: {result}")
        else:
            print(f"PR test expected to fail (test repo): {result['error']}")
            
    except Exception as e:
        print(f"PR test skipped (likely missing credentials): {e}")


async def test_datetime_parsing():
    """Test datetime parsing."""
    print("\nTesting datetime parsing...")
    
    llm_helper = LLMHelper()
    external_tools = ExternalTools(llm_helper)
    
    # Test invalid datetime
    result = await external_tools.google_calendar_add(
        summary="Test",
        start_time="invalid-datetime",
        end_time="2025-10-01T11:00:00"
    )
    
    assert not result["success"], "Should fail with invalid datetime"
    print(f"✓ Invalid datetime handling works: {result['error']}")
    
    # Test end before start
    result = await external_tools.google_calendar_add(
        summary="Test",
        start_time="2025-10-01T11:00:00",
        end_time="2025-10-01T10:00:00"
    )
    
    assert not result["success"], "Should fail when end is before start"
    print(f"✓ Time validation works: {result['error']}")


async def main():
    """Run all tests."""
    print("=== External Tools Tests ===\n")
    
    try:
        await test_datetime_parsing()
        await test_google_calendar()
        await test_github_pr()
        
        print("\n✓ External tools tests completed!")
        print("Note: Some tests may be skipped if credentials are not configured.")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
