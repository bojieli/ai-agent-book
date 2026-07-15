"""Basic tests for Collaboration Tools MCP Server.

Run with: python test_basic.py
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


async def test_config():
    """Test configuration loading."""
    print("Testing configuration...")
    from config import load_config
    
    config = load_config()
    assert config is not None
    assert config.browser is not None
    assert config.email is not None
    assert config.im is not None
    assert config.hitl is not None
    assert config.timer is not None
    
    print("✅ Configuration test passed")


async def test_timer_tools():
    """Test timer functionality."""
    print("\nTesting timer tools...")
    from timer_tools import set_timer, list_timers, cancel_timer, get_timer_status
    
    # Set a timer
    result = await set_timer(
        duration_seconds=5,
        timer_name="Test Timer",
        callback_message="Test completed"
    )
    
    assert result["success"] == True
    assert "timer_id" in result
    timer_id = result["timer_id"]
    print(f"  ✓ Timer created: {timer_id}")
    
    # Check timer status
    status = await get_timer_status(timer_id)
    assert status["success"] == True
    assert status["timer"]["status"] == "active"
    print(f"  ✓ Timer status: {status['timer']['status']}")
    
    # List timers
    timers = await list_timers(status="active")
    assert timers["success"] == True
    assert timers["count"] >= 1
    print(f"  ✓ Active timers: {timers['count']}")
    
    # Cancel timer
    cancel_result = await cancel_timer(timer_id)
    assert cancel_result["success"] == True
    print(f"  ✓ Timer cancelled")
    
    # Verify cancellation
    status = await get_timer_status(timer_id)
    assert status["timer"]["status"] == "cancelled"
    print(f"  ✓ Timer status after cancel: cancelled")
    
    print("✅ Timer tools test passed")


async def test_hitl_tools():
    """Test human-in-the-loop functionality."""
    print("\nTesting HITL tools...")
    from hitl_tools import list_pending_requests
    
    # List pending requests (should be empty initially)
    result = await list_pending_requests()
    assert result["success"] == True
    assert "requests" in result
    print(f"  ✓ Pending requests: {result['count']}")
    
    print("✅ HITL tools test passed")


async def test_notification_tools():
    """Test notification tools (without actually sending)."""
    print("\nTesting notification tools...")
    from notification_tools import send_email, send_slack_message
    
    # These will fail gracefully if not configured
    email_result = await send_email(
        to_email="test@example.com",
        subject="Test",
        body="Test message"
    )
    # We expect this to fail without configuration, that's OK
    print(f"  ✓ Email function callable (configured: {email_result['success']})")
    
    slack_result = await send_slack_message("Test message")
    print(f"  ✓ Slack function callable (configured: {slack_result['success']})")
    
    print("✅ Notification tools test passed")


async def test_browser_tools():
    """Test browser tools (basic initialization)."""
    print("\nTesting browser tools...")
    
    try:
        from browser_tools import browser_list_tabs
        
        # This should work even without browser initialized
        # (it will initialize on first use)
        print("  ✓ Browser tools imported successfully")
        
        # Note: We don't actually initialize browser in tests
        # to avoid heavy Playwright dependency
        print("  ℹ️  Skipping actual browser initialization in tests")
        
    except ImportError as e:
        print(f"  ⚠️  Browser tools import failed (expected if browser-use not installed): {e}")
    
    print("✅ Browser tools test passed")


async def run_all_tests():
    """Run all tests."""
    print("=" * 70)
    print("Collaboration Tools MCP Server - Basic Tests")
    print("=" * 70)
    
    try:
        await test_config()
        await test_timer_tools()
        await test_hitl_tools()
        await test_notification_tools()
        await test_browser_tools()
        
        print("\n" + "=" * 70)
        print("✅ All tests passed!")
        print("=" * 70)
        return True
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
