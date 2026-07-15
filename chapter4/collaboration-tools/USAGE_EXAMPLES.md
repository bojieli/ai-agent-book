# Usage Examples

This document provides practical examples of using the Collaboration Tools MCP Server in various scenarios.

## Table of Contents

1. [Web Scraping with Notifications](#web-scraping-with-notifications)
2. [Scheduled Health Checks](#scheduled-health-checks)
3. [Admin Approval Workflow](#admin-approval-workflow)
4. [Multi-Channel Alerting](#multi-channel-alerting)
5. [Browser Automation Pipeline](#browser-automation-pipeline)

---

## Web Scraping with Notifications

Monitor a website and send alerts when specific content appears.

```python
async def monitor_for_keyword(agent, url, keyword, check_interval=3600):
    """Check website for keyword and alert if found."""
    
    # Set up recurring check
    timer = await agent.call_tool("mcp_set_recurring_timer", {
        "interval_seconds": check_interval,
        "timer_name": f"Monitor {keyword} on {url}",
        "callback_message": f"Check {url} for {keyword}"
    })
    
    # Initial check
    await agent.call_tool("mcp_browser_navigate", {"url": url})
    content = await agent.call_tool("mcp_browser_get_content", {})
    
    if keyword in content["content"]:
        # Keyword found! Alert via multiple channels
        await agent.call_tool("mcp_send_email", {
            "to_email": "team@example.com",
            "subject": f"🔍 Keyword '{keyword}' found on {url}",
            "body": f"The keyword '{keyword}' was detected on {url}"
        })
        
        await agent.call_tool("mcp_send_slack_message", {
            "message": f"🎯 Found '{keyword}' on {url}!"
        })
        
        # Take screenshot as evidence
        await agent.call_tool("mcp_browser_screenshot", {
            "full_page": True
        })
```

---

## Scheduled Health Checks

Perform regular health checks with escalation.

```python
async def health_check_workflow(agent, service_url):
    """Monitor service health and escalate issues."""
    
    # Check every 5 minutes
    await agent.call_tool("mcp_set_recurring_timer", {
        "interval_seconds": 300,
        "timer_name": "Health Check",
        "callback_message": "Perform health check"
    })
    
    # Navigate to health endpoint
    result = await agent.call_tool("mcp_browser_navigate", {
        "url": f"{service_url}/health"
    })
    
    if not result["success"]:
        # Service down - escalate to admin
        approval = await agent.call_tool("mcp_request_admin_approval", {
            "request_message": f"Service {service_url} is down. Restart service?",
            "context": {"service": service_url, "error": result["error"]},
            "timeout_seconds": 300,
            "urgent": True
        })
        
        if approval["approved"]:
            # Admin approved restart
            await agent.call_tool("mcp_send_telegram_message", {
                "message": f"🔧 Restarting {service_url}..."
            })
            # ... perform restart ...
        else:
            # Notify team of ongoing issue
            await agent.call_tool("mcp_send_email", {
                "to_email": "oncall@example.com",
                "subject": f"🚨 Service Down: {service_url}",
                "body": "Service is down and restart was not approved."
            })
```

---

## Admin Approval Workflow

Request human approval for sensitive operations.

```python
async def database_maintenance(agent):
    """Perform database maintenance with admin approval."""
    
    # Step 1: Analyze database
    print("Analyzing database...")
    # ... analysis code ...
    records_to_delete = 50000
    
    # Step 2: Request approval
    approval = await agent.call_tool("mcp_request_admin_approval", {
        "request_message": f"Delete {records_to_delete} old records from database?",
        "context": {
            "operation": "delete",
            "table": "logs",
            "count": records_to_delete,
            "estimated_time": "5 minutes"
        },
        "timeout_seconds": 600,
        "urgent": False
    })
    
    if not approval["approved"]:
        print("❌ Operation cancelled by admin")
        return
    
    # Step 3: Perform deletion with progress updates
    await agent.call_tool("mcp_send_slack_message", {
        "message": f"🗑️ Starting deletion of {records_to_delete} records..."
    })
    
    # Set timer to check progress
    await agent.call_tool("mcp_set_timer", {
        "duration_seconds": 300,
        "timer_name": "Deletion timeout",
        "callback_message": "Check if deletion completed"
    })
    
    # ... perform deletion ...
    
    # Step 4: Notify completion
    await agent.call_tool("mcp_send_email", {
        "to_email": approval["admin_email"],
        "subject": "✅ Database Maintenance Complete",
        "body": f"Successfully deleted {records_to_delete} records.\n\n"
                f"Notes: {approval['admin_notes']}"
    })
```

---

## Multi-Channel Alerting

Send alerts across multiple communication channels.

```python
async def critical_alert(agent, title, message, severity="high"):
    """Send critical alert via all available channels."""
    
    emoji = "🚨" if severity == "high" else "⚠️"
    full_message = f"{emoji} {title}\n\n{message}"
    
    # Send to all channels in parallel
    tasks = []
    
    # Email
    tasks.append(agent.call_tool("mcp_send_email", {
        "to_email": "alerts@example.com",
        "subject": f"{emoji} {title}",
        "body": message,
        "cc": ["oncall@example.com"]
    }))
    
    # Slack
    tasks.append(agent.call_tool("mcp_send_slack_message", {
        "message": full_message,
        "channel": "#alerts"
    }))
    
    # Telegram
    tasks.append(agent.call_tool("mcp_send_telegram_message", {
        "message": full_message,
        "parse_mode": None
    }))
    
    # Discord
    tasks.append(agent.call_tool("mcp_send_discord_message", {
        "message": full_message
    }))
    
    # Wait for all to complete
    results = await asyncio.gather(*tasks)
    
    success_count = sum(1 for r in results if r.get("success"))
    print(f"Alert sent via {success_count}/{len(tasks)} channels")
    
    # If high severity and email/Slack failed, request admin intervention
    if severity == "high" and success_count < 2:
        await agent.call_tool("mcp_request_admin_approval", {
            "request_message": "Alert delivery partially failed. Manual notification needed?",
            "context": {"title": title, "channels_failed": len(tasks) - success_count},
            "urgent": True
        })
```

---

## Browser Automation Pipeline

Complex multi-step browser automation workflow.

```python
async def competitor_research(agent, competitor_url):
    """Research competitor and compile report."""
    
    print("🔍 Starting competitor research...")
    
    # Step 1: Navigate and take initial screenshot
    await agent.call_tool("mcp_browser_navigate", {
        "url": competitor_url
    })
    
    screenshot1 = await agent.call_tool("mcp_browser_screenshot", {
        "full_page": True
    })
    
    # Step 2: Extract pricing information
    print("📊 Extracting pricing...")
    pricing_result = await agent.call_tool("mcp_browser_execute_task", {
        "task": f"Go to {competitor_url} and extract all pricing plans with their features",
        "max_steps": 30
    })
    
    # Step 3: Check their blog for recent posts
    print("📝 Checking blog...")
    await agent.call_tool("mcp_browser_execute_task", {
        "task": "Find the blog and extract titles of the 5 most recent posts",
        "max_steps": 20
    })
    
    blog_screenshot = await agent.call_tool("mcp_browser_screenshot", {
        "full_page": False
    })
    
    # Step 4: Request admin review of findings
    print("👤 Requesting admin review...")
    review = await agent.call_tool("mcp_request_admin_input", {
        "prompt": "Review competitor research findings. Any additional areas to investigate?",
        "input_type": "text",
        "timeout_seconds": 7200  # 2 hours
    })
    
    # Step 5: If admin provided additional areas, research them
    if review["success"] and review["input"]:
        print(f"🔍 Investigating additional area: {review['input']}")
        await agent.call_tool("mcp_browser_execute_task", {
            "task": f"Research: {review['input']}",
            "max_steps": 25
        })
    
    # Step 6: Compile and send report
    print("📧 Sending report...")
    await agent.call_tool("mcp_send_email", {
        "to_email": "team@example.com",
        "subject": f"Competitor Research: {competitor_url}",
        "body": f"""
Competitor Research Report

URL: {competitor_url}
Screenshots: {screenshot1['path']}, {blog_screenshot['path']}

Pricing Info:
{pricing_result['result']}

Admin Notes:
{review.get('input', 'None')}
        """,
        "html": False
    })
    
    # Schedule follow-up research in 30 days
    await agent.call_tool("mcp_set_timer", {
        "duration_seconds": 30 * 24 * 3600,  # 30 days
        "timer_name": f"Follow-up: {competitor_url}",
        "callback_message": f"Time to re-check {competitor_url}"
    })
    
    print("✅ Research complete!")
```

---

## Delayed Task Execution

Use timers for delayed or scheduled operations.

```python
async def scheduled_report(agent, report_type, delay_hours=24):
    """Generate and send report after a delay."""
    
    # Schedule report generation
    timer = await agent.call_tool("mcp_set_timer", {
        "duration_seconds": delay_hours * 3600,
        "timer_name": f"{report_type} Report",
        "callback_message": f"Generate {report_type} report",
        "callback_data": {"report_type": report_type}
    })
    
    print(f"📅 Report scheduled for {delay_hours} hours from now")
    print(f"   Timer ID: {timer['timer_id']}")
    
    # Send confirmation
    await agent.call_tool("mcp_send_slack_message", {
        "message": f"📊 {report_type} report scheduled for "
                   f"{delay_hours} hours from now\n"
                   f"Timer: {timer['timer_id']}"
    })
    
    return timer


async def recurring_backup_notification(agent):
    """Send backup reminders every week."""
    
    await agent.call_tool("mcp_set_recurring_timer", {
        "interval_seconds": 7 * 24 * 3600,  # 1 week
        "timer_name": "Weekly Backup Reminder",
        "callback_message": "Time to verify backups!",
        "max_occurrences": None  # Run indefinitely
    })
    
    print("✅ Weekly backup reminder configured")
```

---

## Error Recovery Workflow

Handle errors with admin escalation.

```python
async def resilient_task(agent, task_description):
    """Execute task with automatic retry and admin escalation."""
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # Attempt task
            result = await agent.call_tool("mcp_browser_execute_task", {
                "task": task_description,
                "max_steps": 30
            })
            
            if result["success"]:
                # Success! Notify and return
                await agent.call_tool("mcp_send_slack_message", {
                    "message": f"✅ Task completed: {task_description}"
                })
                return result
            
            retry_count += 1
            
            if retry_count < max_retries:
                # Wait before retry
                wait_seconds = 60 * retry_count
                print(f"⏳ Retry {retry_count}/{max_retries} in {wait_seconds}s...")
                
                await agent.call_tool("mcp_set_timer", {
                    "duration_seconds": wait_seconds,
                    "timer_name": f"Retry {retry_count}"
                })
                
                # Actual wait
                await asyncio.sleep(wait_seconds)
            
        except Exception as e:
            print(f"❌ Error: {e}")
            retry_count += 1
    
    # All retries failed - escalate to admin
    print("🚨 All retries failed, requesting admin assistance...")
    
    admin_help = await agent.call_tool("mcp_request_admin_approval", {
        "request_message": f"Task failed after {max_retries} retries. Manual intervention needed?",
        "context": {
            "task": task_description,
            "retries": retry_count,
            "last_error": str(result.get("error", "Unknown"))
        },
        "urgent": True,
        "timeout_seconds": 1800
    })
    
    if admin_help["approved"]:
        # Admin will handle manually
        await agent.call_tool("mcp_send_email", {
            "to_email": "admin@example.com",
            "subject": "Task Requires Manual Intervention",
            "body": f"Task: {task_description}\n"
                    f"Failed after {max_retries} retries\n"
                    f"Admin notes: {admin_help.get('admin_notes', 'None')}"
        })
    
    return None
```

---

## Tips for Effective Usage

1. **Combine Tools**: Use multiple tools together for powerful workflows
2. **Error Handling**: Always check `success` field in results
3. **Timeouts**: Set appropriate timeouts for HITL requests
4. **Notifications**: Use multiple channels for critical alerts
5. **Timers**: Leverage timers for retries and scheduled tasks
6. **Screenshots**: Take screenshots for audit trail
7. **Admin Context**: Provide rich context in HITL requests

---

For more examples, see `client_example.py` and `quickstart.py`.
