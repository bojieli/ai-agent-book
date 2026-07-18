"""
Active Tool Discovery Agent.

Implements an LLM agent that actively requests tools on-demand rather than
having all tool schemas injected into the prompt. Inspired by MCP-Zero.
"""

from typing import List, Dict, Any, Optional
from openai import OpenAI

from tool_knowledge_base import ToolDefinition, ServerDefinition, create_tool_knowledge_base
from semantic_router import SemanticRouter, StructuredRequestParser
import config


class ActiveToolAgent:
    """
    Agent that actively discovers and requests tools as needed.
    
    Key principles:
    1. Maintains minimal context by not injecting all tools upfront
    2. Actively requests specific tools when capability gaps are identified
    3. Iteratively builds toolchain as task understanding evolves
    """
    
    def __init__(self, servers: Optional[List[ServerDefinition]] = None,
                 model: Optional[str] = None):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = model or config.OPENAI_MODEL

        # Initialize tool knowledge base (callers may inject a padded/custom catalog)
        self.servers = servers if servers is not None else create_tool_knowledge_base()
        self.router = SemanticRouter(self.servers)

        # Agent state
        self.conversation_history = []
        self.available_tools: List[ToolDefinition] = []  # Currently loaded tools
        self.tool_request_count = 0

        # Metrics
        self.metrics = {
            'tokens_used': 0,
            'tool_requests': 0,
            'tools_loaded': 0,
            'api_calls': 0,
            'tools_called': []  # Names of tools the model actually invoked
        }
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """
        Execute a task with active tool discovery.
        
        The agent will:
        1. Analyze the task
        2. Identify capability gaps
        3. Request specific tools
        4. Execute with discovered tools
        
        Returns execution results with metrics.
        """
        self.conversation_history = []
        self.available_tools = []
        self.tool_request_count = 0
        
        # Initial system message explaining active tool discovery
        system_message = self._create_system_message()
        self.conversation_history.append({
            "role": "system",
            "content": system_message
        })
        
        # Add user task
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        # Iterative tool discovery and execution
        max_iterations = config.MAX_TOOL_REQUESTS
        for iteration in range(max_iterations):
            # Get agent response
            response = self._call_llm()
            self.metrics['api_calls'] += 1
            
            # Check if agent is requesting tools
            tool_request = StructuredRequestParser.parse_request(response)
            
            if tool_request:
                # Agent is requesting tools - discover and provide them
                self._handle_tool_request(tool_request, response)
                self.tool_request_count += 1
                self.metrics['tool_requests'] += 1
            else:
                # Agent has what it needs and is responding
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response
                })
                break
        
        return {
            'response': response,
            'metrics': self.metrics,
            'tools_loaded': [t.name for t in self.available_tools],
            'conversation': self.conversation_history
        }
    
    def _create_system_message(self) -> str:
        """Create system message explaining active tool discovery."""
        return """You are an autonomous AI agent with active tool discovery capabilities.

Instead of having all possible tools available upfront, you can actively request tools as you need them. This allows you to:
1. Maintain a minimal context footprint
2. Focus on relevant capabilities for the current task
3. Iteratively build your toolchain as your understanding evolves

When you identify a capability gap, request tools using this format:

<tool_request>
server: [describe the platform/domain you need, e.g., "GitHub for repository operations" or "filesystem for local file access"]
tool: [describe the specific operation you need, e.g., "search repositories" or "read file contents"]
</tool_request>

After requesting tools, they will be provided to you. You can then use them to accomplish the task.

Process:
1. Analyze the task and identify what capabilities you need
2. Request specific tools if you don't have them yet
3. Once you have the necessary tools, use them to complete the task
4. Respond with your findings or results

Current available tools: None (request tools as needed)"""
    
    def _call_llm(self) -> str:
        """Call LLM with current context and available tools."""
        kwargs = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": config.AGENT_TEMPERATURE
        }

        # Add tools if available
        if self.available_tools:
            kwargs["tools"] = [tool.to_schema() for tool in self.available_tools]
            kwargs["tool_choice"] = "auto"
        
        response = self.client.chat.completions.create(**kwargs)
        
        # Track token usage
        if hasattr(response, 'usage'):
            self.metrics['tokens_used'] += response.usage.total_tokens
        
        # Extract response content
        message = response.choices[0].message
        
        # Handle tool calls if present
        if message.tool_calls:
            return self._handle_tool_calls(message)
        
        return message.content or ""
    
    def _handle_tool_request(self, tool_request: Dict[str, str], full_response: str):
        """
        Handle tool request from agent.
        
        Args:
            tool_request: Parsed tool request with 'server' and 'tool' fields
            full_response: Full response text from agent
        """
        # Combine server and tool descriptions for routing
        query = f"{tool_request['server']} {tool_request['tool']}"
        
        # Use semantic router to find relevant tools
        discovered_tools = self.router.route_request(query)
        
        if not discovered_tools:
            # No tools found
            feedback = f"""No tools found matching your request. Please refine your request or proceed without additional tools.

Your request was:
- Server: {tool_request['server']}
- Tool: {tool_request['tool']}"""
        else:
            # Add discovered tools to available tools
            new_tools = []
            for tool in discovered_tools:
                if tool not in self.available_tools:
                    self.available_tools.append(tool)
                    new_tools.append(tool)
                    self.metrics['tools_loaded'] += 1
            
            tool_list = "\n".join([f"- {t.name}: {t.description}" for t in new_tools])
            feedback = f"""Tools discovered and loaded ({len(new_tools)} new tools):

{tool_list}

You can now use these tools to complete the task. Please proceed."""
        
        # Add agent's request and system's response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": full_response
        })
        self.conversation_history.append({
            "role": "user",
            "content": feedback
        })
    
    def _handle_tool_calls(self, message) -> str:
        """Handle actual tool execution (simulated for demo)."""
        # For this educational demo, we simulate tool execution
        tool_results = []
        
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            self.metrics['tools_called'].append(func_name)

            # Simulate tool execution
            result = f"[Simulated] Tool '{func_name}' executed successfully with result: Success"
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": result
            })
        
        # Add tool call message to history
        self.conversation_history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })
        
        # Add tool results to history
        for result in tool_results:
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "content": result["output"]
            })
        
        # Get final response after tool execution
        return self._call_llm()
    
    def reset(self):
        """Reset agent state."""
        self.conversation_history = []
        self.available_tools = []
        self.tool_request_count = 0
        self.metrics = {
            'tokens_used': 0,
            'tool_requests': 0,
            'tools_loaded': 0,
            'api_calls': 0,
            'tools_called': []
        }


class RetrievalToolAgent:
    """
    One-shot retrieval agent (semantic tool retrieval / "工具检索").

    This is the RAG-style middle ground between passive injection and active
    discovery: before the very first LLM call, it retrieves the top-k tools most
    semantically relevant to the task and injects *only* those. There is no extra
    discovery round-trip — tool selection is delegated to the retriever, turning the
    "which of hundreds of tools" problem into a knowledge-retrieval problem.

    This directly embodies the mechanism the chapter attributes to Anthropic's
    on-demand tool retrieval experiment: fewer, more relevant tool schemas in
    context both cut token cost and reduce the model's selection errors.
    """

    def __init__(self, servers: Optional[List[ServerDefinition]] = None,
                 model: Optional[str] = None, top_k: Optional[int] = None):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = model or config.OPENAI_MODEL
        self.top_k = top_k if top_k is not None else config.TOP_K_TOOLS

        self.servers = servers if servers is not None else create_tool_knowledge_base()
        self.router = SemanticRouter(self.servers)

        self.conversation_history = []
        self.available_tools: List[ToolDefinition] = []
        self.metrics = {
            'tokens_used': 0,
            'tools_loaded': 0,
            'api_calls': 0,
            'tools_called': []
        }

    def execute_task(self, task: str) -> Dict[str, Any]:
        """Retrieve top-k relevant tools for the task, then execute in one shot."""
        self.conversation_history = []

        # Retrieval step (no LLM call): pick the top-k most relevant tools.
        self.available_tools = self.router.retrieve(task, self.top_k)
        self.metrics['tools_loaded'] = len(self.available_tools)

        tool_list = "\n".join(
            f"- {t.name}: {t.description}" for t in self.available_tools
        )
        system_message = f"""You are an AI agent. A retrieval system has pre-selected the \
{len(self.available_tools)} tools below as most relevant to the user's task.

{tool_list}

Analyze the task and call the appropriate tool(s) to complete it."""

        self.conversation_history.append({"role": "system", "content": system_message})
        self.conversation_history.append({"role": "user", "content": task})

        response = self._call_llm()
        self.metrics['api_calls'] += 1

        return {
            'response': response,
            'metrics': self.metrics,
            'tools_loaded': [t.name for t in self.available_tools],
            'conversation': self.conversation_history
        }

    def _call_llm(self) -> str:
        """Call LLM with only the retrieved tools injected."""
        kwargs = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": config.AGENT_TEMPERATURE
        }
        if self.available_tools:
            kwargs["tools"] = [tool.to_schema() for tool in self.available_tools]
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)

        if hasattr(response, 'usage'):
            self.metrics['tokens_used'] += response.usage.total_tokens

        message = response.choices[0].message
        if message.tool_calls:
            return self._handle_tool_calls(message)
        return message.content or ""

    def _handle_tool_calls(self, message) -> str:
        """Handle tool execution (simulated)."""
        tool_results = []
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            self.metrics['tools_called'].append(func_name)
            result = f"[Simulated] Tool '{func_name}' executed successfully"
            tool_results.append({"tool_call_id": tool_call.id, "output": result})

        self.conversation_history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })
        for result in tool_results:
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "content": result["output"]
            })
        return self._call_llm()

    def reset(self):
        """Reset agent state."""
        self.conversation_history = []
        self.available_tools = []
        self.metrics = {
            'tokens_used': 0,
            'tools_loaded': 0,
            'api_calls': 0,
            'tools_called': []
        }


class PassiveToolAgent:
    """
    Traditional agent with all tools injected upfront (for comparison).
    
    This approach:
    1. Injects all tool schemas into the initial prompt
    2. Massive context overhead
    3. Reduces agent to passive tool selector
    """
    
    def __init__(self, servers: Optional[List[ServerDefinition]] = None,
                 model: Optional[str] = None):
        self.client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL
        )
        self.model = model or config.OPENAI_MODEL

        # Load ALL tools upfront
        self.servers = servers if servers is not None else create_tool_knowledge_base()
        self.all_tools = []
        for server in self.servers:
            self.all_tools.extend(server.tools)

        self.conversation_history = []
        self.metrics = {
            'tokens_used': 0,
            'tools_loaded': len(self.all_tools),
            'api_calls': 0,
            'tools_called': []
        }
    
    def execute_task(self, task: str) -> Dict[str, Any]:
        """Execute task with all tools pre-loaded."""
        self.conversation_history = []
        
        # System message
        system_message = f"""You are an AI agent with access to {len(self.all_tools)} tools across multiple domains.

All available tools have been pre-loaded. Analyze the task and use the appropriate tools to complete it."""
        
        self.conversation_history.append({
            "role": "system",
            "content": system_message
        })
        
        self.conversation_history.append({
            "role": "user",
            "content": task
        })
        
        # Call LLM with ALL tools
        response = self._call_llm()
        self.metrics['api_calls'] += 1
        
        return {
            'response': response,
            'metrics': self.metrics,
            'tools_loaded': [t.name for t in self.all_tools],
            'conversation': self.conversation_history
        }
    
    def _call_llm(self) -> str:
        """Call LLM with ALL tools injected."""
        kwargs = {
            "model": self.model,
            "messages": self.conversation_history,
            "temperature": config.AGENT_TEMPERATURE,
            "tools": [tool.to_schema() for tool in self.all_tools],
            "tool_choice": "auto"
        }
        
        response = self.client.chat.completions.create(**kwargs)
        
        # Track token usage
        if hasattr(response, 'usage'):
            self.metrics['tokens_used'] += response.usage.total_tokens
        
        message = response.choices[0].message
        
        # Handle tool calls (simulated)
        if message.tool_calls:
            return self._handle_tool_calls(message)
        
        return message.content or ""
    
    def _handle_tool_calls(self, message) -> str:
        """Handle tool execution (simulated)."""
        tool_results = []
        
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            self.metrics['tools_called'].append(func_name)
            result = f"[Simulated] Tool '{func_name}' executed successfully"
            tool_results.append({
                "tool_call_id": tool_call.id,
                "output": result
            })

        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                }
                for tc in message.tool_calls
            ]
        })
        
        for result in tool_results:
            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": result["tool_call_id"],
                "content": result["output"]
            })
        
        return self._call_llm()
    
    def reset(self):
        """Reset agent state."""
        self.conversation_history = []
        self.metrics = {
            'tokens_used': 0,
            'tools_loaded': len(self.all_tools),
            'api_calls': 0,
            'tools_called': []
        }
