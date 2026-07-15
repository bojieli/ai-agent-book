"""
Test cases for ExitPlanMode tool
Tests all features from tools.json
"""

import pytest
from tools.exit_plan_mode_tool import ExitPlanModeTool


class TestExitPlanModeTool:
    """Test ExitPlanMode tool functionality"""
    
    def test_basic_plan_submission(self, system_state):
        """Test submitting a plan"""
        tool = ExitPlanModeTool(system_state)
        
        plan = """
## Implementation Plan
1. Create database schema
2. Implement API endpoints
3. Write tests
"""
        
        result = tool.execute({
            "plan": plan
        })
        
        assert result.success
        assert result.data["action"] == "exit_plan_mode"
        assert result.data["plan"] == plan
        assert "message" in result.data
    
    def test_markdown_plan(self, system_state):
        """Test that plan supports markdown"""
        tool = ExitPlanModeTool(system_state)
        
        plan = """
# Implementation Plan

## Phase 1
- [ ] Task 1
- [ ] Task 2

## Phase 2
- [ ] Task 3

**Note**: This is a markdown plan
"""
        
        result = tool.execute({
            "plan": plan
        })
        
        assert result.success
        assert "# Implementation Plan" in result.data["plan"]
        assert "**Note**" in result.data["plan"]
    
    def test_empty_plan(self, system_state):
        """Test with empty plan"""
        tool = ExitPlanModeTool(system_state)
        
        result = tool.execute({
            "plan": ""
        })
        
        assert result.success
        assert result.data["plan"] == ""

