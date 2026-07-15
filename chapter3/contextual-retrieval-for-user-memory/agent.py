"""Agentic RAG Agent for User Memory Evaluation

This agent uses RAG-indexed conversation memories to answer questions
about user interactions, following the ReAct pattern.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Generator
from dataclasses import dataclass, field
from datetime import datetime
from openai import OpenAI

from config import Config
from tools import MemoryTools, get_tool_definitions
from indexer import MemoryIndexer


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentTrajectory:
    """Tracks the agent's reasoning and tool usage"""
    test_id: str
    question: str
    iterations: List[Dict[str, Any]] = field(default_factory=list)
    final_answer: Optional[str] = None
    tool_calls: List[Dict[str, Any]] = field(default_factory=list)
    total_time: Optional[float] = None
    success: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_id": self.test_id,
            "question": self.question,
            "iterations": self.iterations,
            "final_answer": self.final_answer,
            "tool_calls": self.tool_calls,
            "total_time": self.total_time,
            "success": self.success,
            "total_iterations": len(self.iterations),
            "total_tool_calls": len(self.tool_calls)
        }


class UserMemoryRAGAgent:
    """Agent that uses RAG to answer questions about user conversation history"""
    
    def __init__(self, 
                 indexer: MemoryIndexer,
                 config: Optional[Config] = None):
        """
        Initialize the agent
        
        Args:
            indexer: The memory indexer with loaded conversations
            config: Configuration object
        """
        self.config = config or Config.from_env()
        self.indexer = indexer
        self.memory_tools = MemoryTools(indexer)
        
        # Initialize LLM client
        self._init_llm_client()
        
        # Tool definitions
        self.tools = get_tool_definitions()
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized UserMemoryRAGAgent with provider: {self.config.llm.provider}")
    
    def _init_llm_client(self):
        """Initialize the LLM client based on provider"""
        client_config, model = self.config.llm.get_client_config()
        
        # Extract base_url if present
        base_url = client_config.pop("base_url", None)
        
        # Create OpenAI client
        if base_url:
            self.client = OpenAI(base_url=base_url, **client_config)
        else:
            self.client = OpenAI(**client_config)
        
        self.model = model
        logger.info(f"Using model: {self.model}")
    
    def _get_system_prompt(self, test_id: str) -> str:
        """Generate the system prompt"""
        return f"""You are an AI assistant with access to indexed conversation memories from user interactions. 
Your task is to answer questions about these conversations accurately based ONLY on the information you can find in the indexed memories.

Current Test Case: {test_id}

## Important Guidelines:

1. **Memory Search Only**: You MUST only answer based on information found through the memory search tools. If the information is not available in the indexed conversations, clearly state that you cannot find it.

2. **Use Tools Effectively**:
   - Use `search_memory` to find relevant information across all conversations
   - Use `get_conversation_context` when you need more context around a search result
   - Use `get_full_conversation` to review entire conversation histories when needed

3. **Multiple Searches**: Don't hesitate to perform multiple searches with different queries to find all relevant information. Different phrasings may yield different results.

4. **Citations Required**: Always mention which conversation or chunk you found the information in when providing answers.

5. **Be Thorough**: For complex questions, gather information from multiple chunks and conversations before formulating your answer.

6. **Handle Ambiguity**: If you find conflicting information or multiple possible answers, report all of them with their sources.

Remember: Your credibility depends on providing accurate, well-sourced information from the conversation memories only."""
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return the result"""
        try:
            # Log tool call parameters to console
            logger.info("="*80)
            logger.info(f"TOOL CALL: {tool_name}")
            logger.info(f"PARAMETERS: {json.dumps(arguments, indent=2, ensure_ascii=False)}")
            logger.info("-"*80)
            
            if tool_name == "search_memory":
                query = arguments.get("query", "")
                filter_test_id = arguments.get("filter_test_id")
                
                result = self.memory_tools.search_memory(query, filter_test_id)
                
                # Log result to console
                result_dict = result.to_dict()
                logger.info("TOOL RESULT:")
                logger.info(json.dumps(result_dict, indent=2, ensure_ascii=False))
                logger.info("="*80)
                
                return result_dict
            
            elif tool_name == "get_conversation_context":
                chunk_id = arguments.get("chunk_id", "")
                context_size = arguments.get("context_size", 2)
                
                result = self.memory_tools.get_conversation_context(chunk_id, context_size)
                
                # Log result to console
                result_dict = result.to_dict()
                logger.info("TOOL RESULT:")
                logger.info(json.dumps(result_dict, indent=2, ensure_ascii=False))
                logger.info("="*80)
                
                return result_dict
            
            elif tool_name == "get_full_conversation":
                conversation_id = arguments.get("conversation_id", "")
                test_id = arguments.get("test_id", "")
                
                result = self.memory_tools.get_full_conversation(conversation_id, test_id)
                
                # Log result to console
                result_dict = result.to_dict()
                logger.info("TOOL RESULT:")
                logger.info(json.dumps(result_dict, indent=2, ensure_ascii=False))
                logger.info("="*80)
                
                return result_dict
            
            else:
                return {"status": "error", "error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"status": "error", "error": str(e)}
    
    def answer_question(self, 
                       question: str,
                       test_id: str,
                       stream: bool = False) -> Dict[str, Any]:
        """
        Answer a question about user conversation history using RAG
        
        Args:
            question: The question to answer
            test_id: The test case ID for context
            stream: Whether to stream the response
            
        Returns:
            Dictionary containing the answer and trajectory
        """
        start_time = datetime.now()
        trajectory = AgentTrajectory(test_id=test_id, question=question)
        
        # Build initial messages
        messages = [
            {"role": "system", "content": self._get_system_prompt(test_id)},
            {"role": "user", "content": question}
        ]
        
        # Track iterations
        iterations = 0
        max_iterations = self.config.evaluation.max_iterations
        
        # Process with ReAct loop
        while iterations < max_iterations:
            iterations += 1
            iteration_data = {"iteration": iterations, "timestamp": datetime.now().isoformat()}
            
            if self.config.agent.enable_reasoning:
                logger.info(f"\n{'='*60}")
                logger.info(f"Iteration {iterations}/{max_iterations}")
                logger.info(f"{'='*60}")
            
            try:
                # Call LLM with tools
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.config.llm.temperature,
                    max_tokens=self.config.llm.max_tokens,
                    stream=False
                )
                
                message = response.choices[0].message
                iteration_data["assistant_message"] = message.content or ""
                
                # Log the LLM response content
                if message.content:
                    logger.info("-"*60)
                    logger.info(f"LLM Response: {message.content}")
                    logger.info("-"*60)
                
                # Add assistant message to history
                assistant_msg = {"role": "assistant", "content": message.content or ""}
                if message.tool_calls:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        } for tc in message.tool_calls
                    ]
                    iteration_data["tool_calls"] = []
                
                messages.append(assistant_msg)
                
                # Process tool calls if present
                if message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}
                        
                        
                        # Execute tool
                        result = self._execute_tool(tool_name, arguments)
                        
                        # Track tool call
                        tool_call_data = {
                            "tool": tool_name,
                            "arguments": arguments,
                            "result": result,
                            "timestamp": datetime.now().isoformat()
                        }
                        iteration_data["tool_calls"].append(tool_call_data)
                        trajectory.tool_calls.append(tool_call_data)
                        
                        # Add tool result to messages
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, ensure_ascii=False)
                        }
                        messages.append(tool_message)
                    
                    # Continue loop for next iteration
                    trajectory.iterations.append(iteration_data)
                    continue
                else:
                    # No tool calls, we have final answer
                    trajectory.iterations.append(iteration_data)
                    trajectory.final_answer = message.content or ""
                    trajectory.success = True
                    
                    # Calculate total time
                    end_time = datetime.now()
                    trajectory.total_time = (end_time - start_time).total_seconds()
                    
                    # Return result
                    result = {
                        "answer": trajectory.final_answer,
                        "success": True,
                        "iterations": iterations,
                        "tool_calls": len(trajectory.tool_calls),
                        "trajectory": trajectory.to_dict() if self.config.evaluation.save_trajectories else None
                    }
                    
                    if stream:
                        return self._stream_response(result)
                    else:
                        return result
                        
            except Exception as e:
                logger.error(f"Error in iteration {iterations}: {e}")
                trajectory.iterations.append({
                    "iteration": iterations,
                    "error": str(e)
                })
                
                # Continue to next iteration
                continue
        
        # Max iterations reached
        logger.warning(f"Max iterations ({max_iterations}) reached")
        
        # Calculate total time
        end_time = datetime.now()
        trajectory.total_time = (end_time - start_time).total_seconds()
        trajectory.success = False
        
        final_msg = "I was unable to find sufficient information to answer your question within the iteration limit. Please try rephrasing or breaking down your query."
        
        return {
            "answer": final_msg,
            "success": False,
            "iterations": iterations,
            "tool_calls": len(trajectory.tool_calls),
            "trajectory": trajectory.to_dict() if self.config.evaluation.save_trajectories else None
        }
    
    def _stream_response(self, result: Dict[str, Any]) -> Generator[str, None, None]:
        """Stream response content"""
        # Stream the answer character by character
        answer = result.get("answer", "")
        for char in answer:
            yield char
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
    
    def save_trajectory(self, trajectory: AgentTrajectory, filepath: str):
        """
        Save agent trajectory to file
        
        Args:
            trajectory: The trajectory to save
            filepath: Path to save the trajectory
        """
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(trajectory.to_dict(), f, ensure_ascii=False, indent=2)
        logger.info(f"Trajectory saved to {filepath}")
