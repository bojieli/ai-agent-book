"""
GPT-5 Native Tools Agent
An advanced agent leveraging GPT-5's native web_search and code_interpreter tools via OpenRouter API.
"""

import json
import os
from typing import List, Dict, Any, Optional, Literal
from openai import OpenAI
import logging
from dataclasses import dataclass
from enum import Enum
import requests

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ToolType(Enum):
    """Enum for GPT-5 native tool types"""
    WEB_SEARCH = "web_search"
    CODE_INTERPRETER = "code_interpreter"


@dataclass
class ToolResult:
    """Container for tool execution results"""
    tool_type: ToolType
    success: bool
    result: Any
    error: Optional[str] = None


class GPT5NativeAgent:
    """
    GPT-5 Agent with Native Tool Support
    
    This agent uses GPT-5's native web_search and code_interpreter capabilities
    through the OpenRouter API. These tools are built into GPT-5 and don't require
    manual implementation.
    
    Based on OpenAI's native tool support:
    - web_search: Native internet search capability
    - code_interpreter: Built-in code execution environment
    """
    
    def __init__(
        self, 
        api_key: str, 
        base_url: str = "https://openrouter.ai/api/v1",
        model: str = "openai/gpt-5-2025-08-07"
    ):
        """
        Initialize the GPT-5 agent with OpenRouter API
        
        Args:
            api_key: OpenRouter API key
            base_url: OpenRouter API base URL
            model: Model identifier (default: openai/gpt-5-2025-08-07)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = self._create_system_prompt()
        
    def _create_system_prompt(self) -> str:
        """
        Create the system prompt for the agent
        
        Returns:
            System prompt string
        """
        return """You are an advanced AI assistant powered by GPT-5 with native tool capabilities.

You have access to two powerful native tools:

1. **web_search**: Use this to search the internet for real-time information, current events, 
   documentation, or any information not in your training data.
   
2. **code_interpreter**: Use this to execute Python code, perform calculations, data analysis,
   generate visualizations, or solve computational problems.

Guidelines:
- Analyze the user's request carefully to determine which tools to use
- You can use multiple tools in sequence or combination to provide comprehensive answers
- When using code_interpreter, write clear, well-commented code
- When using web_search, search for authoritative and recent sources
- Always synthesize information from tools into clear, actionable responses
- Be proactive in using tools when they would enhance your answer quality

Remember: These are native tools built into your capabilities, use them naturally as part of your reasoning process."""
    
    def _build_openrouter_request(
        self,
        messages: List[Dict[str, Any]],
        use_tools: bool = True,
        reasoning_effort: str = "low",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Build the OpenRouter-specific request format matching the Go implementation
        
        Args:
            messages: Conversation messages
            use_tools: Whether to enable tools
            reasoning_effort: Reasoning effort level (low, medium, high)
            stream: Whether to stream the response
            
        Returns:
            Request dictionary
        """
        request = {
            "model": self.model,
            "messages": messages,
            "stream": stream
        }
        
        if use_tools:
            # Match the exact Go implementation structure
            request["tools"] = [
                {
                    "type": "web_search",
                    "search_context_size": "medium",
                    "user_location": {
                        "type": "approximate",
                        "country": "US"
                    }
                },
                {
                    "type": "code_interpreter",
                    "container": {"type": "auto"}
                },
            ]
            request["tool_choice"] = "auto"
            request["parallel_tool_calls"] = True
        
        # Add reasoning configuration
        request["reasoning"] = {
            "effort": reasoning_effort,
            "generate_summary": False
        }
        
        request["background"] = False
        
        return request
    
    def process_request(
        self, 
        user_request: str,
        use_tools: bool = True,
        tool_choice: Literal["auto", "none", "required"] = "auto",
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
        reasoning_effort: str = "low"
    ) -> Dict[str, Any]:
        """
        Process a user request with optional tool usage (OpenRouter format)
        
        Args:
            user_request: The user's request or question
            use_tools: Whether to enable native tools
            tool_choice: Tool selection strategy (for compatibility, internally uses "auto")
            temperature: Response temperature (0-1)
            max_tokens: Maximum tokens in response
            reasoning_effort: Reasoning effort level (low, medium, high)
            
        Returns:
            Dictionary containing the response and metadata
        """
        # Add system prompt if this is the first message
        if not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_request
        })
        
        logger.info(f"Processing request: {user_request[:100]}...")
        logger.info(f"Using OpenRouter format with reasoning effort: {reasoning_effort}")
        
        try:
            # Build the OpenRouter-specific request
            request_body = self._build_openrouter_request(
                messages=self.conversation_history,
                use_tools=use_tools,
                reasoning_effort=reasoning_effort,
                stream=False
            )
            
            # Add temperature and max_tokens if specified
            if temperature is not None:
                request_body["temperature"] = temperature
            if max_tokens:
                request_body["max_tokens"] = max_tokens
            
            logger.info(f"Request body: {json.dumps(request_body, indent=2)}")
            
            # Make the API call directly using requests (matching Go implementation)
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=request_body,
                timeout=600
            )
            
            logger.info(f"Response status: {response.status_code}")
            
            if response.status_code != 200:
                error_msg = f"API error (status {response.status_code}): {response.text}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "response": None,
                    "tool_calls": []
                }
            
            response_data = response.json()
            
            # Log usage information
            if "usage" in response_data:
                usage = response_data["usage"]
                logger.info(f"GPT-5 OpenRouter Usage - Input: {usage.get('input_tokens', 0)} tokens "
                          f"(cached: {usage.get('input_tokens_details', {}).get('cached_tokens', 0)}), "
                          f"Output: {usage.get('output_tokens', 0)} tokens "
                          f"(reasoning: {usage.get('output_tokens_details', {}).get('reasoning_tokens', 0)}), "
                          f"Total: {usage.get('total_tokens', 0)}")
            
            # Extract the message
            message_content = None
            if response_data.get("choices") and len(response_data["choices"]) > 0:
                message = response_data["choices"][0].get("message", {})
                message_content = message.get("content", "")
                
                # Add assistant response to history
                if message_content:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": message_content
                    })
            
            # Prepare the result
            result = {
                "success": True,
                "response": message_content or "No response generated",
                "tool_calls": [],  # GPT-5 handles tools internally
                "usage": response_data.get("usage", {}),
                "model": self.model
            }
            
            logger.info("Request processed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None,
                "tool_calls": []
            }
    
    def search_and_analyze(self, topic: str, analysis_code: Optional[str] = None) -> Dict[str, Any]:
        """
        Combine web search with code analysis
        
        This method demonstrates using both native tools together:
        1. Search for information on a topic
        2. Optionally analyze the results with code
        
        Args:
            topic: Topic to search and analyze
            analysis_code: Optional Python code to analyze the search results
            
        Returns:
            Combined results from both tools
        """
        # Construct a request that uses both tools
        if analysis_code:
            request = f"""Please help me with the following task:

1. First, search the web for current information about: {topic}
2. Then, analyze the findings using this code:

```python
{analysis_code}
```

Provide a comprehensive response combining the search results and code analysis."""
        else:
            request = f"""Search for current information about: {topic}

Then provide a data-driven analysis of the findings, using code to process or visualize 
any quantitative information if relevant."""
        
        return self.process_request(request, use_tools=True, reasoning_effort="medium")
    
    def clear_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get the current conversation history"""
        return self.conversation_history.copy()
    
    def set_system_prompt(self, prompt: str):
        """
        Update the system prompt
        
        Args:
            prompt: New system prompt
        """
        self.system_prompt = prompt
        if self.conversation_history and self.conversation_history[0]["role"] == "system":
            self.conversation_history[0]["content"] = prompt
        logger.info("System prompt updated")


class GPT5AgentChain:
    """
    Chain multiple GPT-5 agent calls for complex workflows
    """
    
    def __init__(self, agent: GPT5NativeAgent):
        """
        Initialize the agent chain
        
        Args:
            agent: GPT5NativeAgent instance
        """
        self.agent = agent
        self.chain_results = []
    
    def add_step(self, request: str, **kwargs) -> 'GPT5AgentChain':
        """
        Add a step to the chain
        
        Args:
            request: Request for this step
            **kwargs: Additional parameters for process_request
            
        Returns:
            Self for chaining
        """
        result = self.agent.process_request(request, **kwargs)
        self.chain_results.append({
            "request": request,
            "result": result
        })
        return self
    
    def execute(self) -> List[Dict[str, Any]]:
        """
        Execute the chain and return all results
        
        Returns:
            List of all chain results
        """
        return self.chain_results
    
    def clear(self):
        """Clear the chain results"""
        self.chain_results = []