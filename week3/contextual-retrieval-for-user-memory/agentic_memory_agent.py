"""
Agentic Memory Agent with ReAct Pattern
Uses contextual retrieval to answer questions about user memories
"""

import json
import logging
from typing import List, Dict, Any, Optional, Generator, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from openai import OpenAI

from config import Config, RetrievalMode
from memory_indexer import ContextualMemoryIndexer
from memory_tools import MemorySearchTools, get_tool_definitions

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ToolCall:
    """Represents a tool call in the agent's trajectory"""
    tool_name: str
    arguments: Dict[str, Any]
    result: Any
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    reasoning: Optional[str] = None


@dataclass
class AgentTrajectory:
    """Tracks the agent's reasoning and tool use trajectory"""
    user_query: str
    iterations: List[Dict[str, Any]] = field(default_factory=list)
    tool_calls: List[ToolCall] = field(default_factory=list)
    final_answer: Optional[str] = None
    total_tokens: int = 0
    latency_ms: int = 0
    mode: str = "agentic"


class AgenticMemoryAgent:
    """
    Agentic RAG system for user memory retrieval using ReAct pattern
    """
    
    def __init__(self,
                 user_id: str,
                 config: Optional[Config] = None,
                 indexer: Optional[ContextualMemoryIndexer] = None,
                 mode: RetrievalMode = RetrievalMode.CONTEXTUAL):
        """
        Initialize the agentic memory agent
        
        Args:
            user_id: User identifier
            config: Configuration
            indexer: Pre-initialized memory indexer
            mode: Retrieval mode (contextual, non_contextual, baseline)
        """
        self.user_id = user_id
        self.config = config or Config.from_env()
        self.mode = mode
        
        # Initialize indexer with appropriate mode
        enable_contextual = (mode == RetrievalMode.CONTEXTUAL)
        self.indexer = indexer or ContextualMemoryIndexer(
            user_id=user_id,
            config=self.config,
            enable_contextual=enable_contextual
        )
        
        # Initialize memory tools
        self.memory_tools = MemorySearchTools(
            user_id=user_id,
            indexer=self.indexer,
            config=self.config
        )
        
        # Initialize LLM client
        self._init_llm_client()
        
        # Get tool definitions
        self.tools = get_tool_definitions()
        
        # Track trajectories
        self.trajectories: List[AgentTrajectory] = []
        
        logger.info(f"Initialized AgenticMemoryAgent for user {user_id} in {mode.value} mode")
    
    def _init_llm_client(self):
        """Initialize the LLM client"""
        llm_config = self.config.llm
        api_key = llm_config.get_api_key()
        base_url = llm_config.get_base_url()
        
        if not api_key:
            raise ValueError(f"No API key found for provider {llm_config.provider}")
        
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.model = llm_config.get_model_name()
        logger.info(f"Using LLM: {llm_config.provider}/{self.model}")
    
    def answer_with_memories(self,
                            query: str,
                            conversation_context: Optional[List[Dict[str, str]]] = None,
                            stream: bool = False) -> str:
        """
        Answer a query using memories with agentic RAG
        
        Args:
            query: User's question
            conversation_context: Optional recent conversation for context
            stream: Whether to stream the response
            
        Returns:
            Agent's answer based on memories
        """
        # Start trajectory tracking
        trajectory = AgentTrajectory(
            user_query=query,
            mode="agentic" if self.config.agent.enable_tool_calling else "direct"
        )
        start_time = datetime.now()
        
        try:
            if self.config.agent.enable_tool_calling:
                # Agentic mode with ReAct pattern
                answer = self._answer_agentic(query, conversation_context, trajectory)
            else:
                # Direct retrieval mode (baseline)
                answer = self._answer_direct(query, conversation_context, trajectory)
            
            # Record final answer and metrics
            trajectory.final_answer = answer
            trajectory.latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            self.trajectories.append(trajectory)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            trajectory.final_answer = f"I encountered an error while searching memories: {str(e)}"
            self.trajectories.append(trajectory)
            return trajectory.final_answer
    
    def _answer_agentic(self,
                       query: str,
                       conversation_context: Optional[List[Dict[str, str]]],
                       trajectory: AgentTrajectory) -> str:
        """
        Answer using agentic RAG with ReAct pattern and tool use
        """
        # Build initial messages
        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": self._format_user_query(query, conversation_context)}
        ]
        
        # ReAct loop
        for iteration in range(self.config.agent.max_iterations):
            iteration_data = {
                "iteration": iteration + 1,
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                # Get LLM response with tool calling
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.config.llm.temperature,
                    max_tokens=self.config.llm.max_tokens
                )
                
                assistant_message = response.choices[0].message
                messages.append(assistant_message.model_dump())
                
                # Track token usage
                if hasattr(response, "usage"):
                    trajectory.total_tokens += response.usage.total_tokens
                
                # Check if assistant wants to use tools
                if assistant_message.tool_calls:
                    tool_results = []
                    
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        tool_args = json.loads(tool_call.function.arguments)
                        
                        # Execute tool
                        result = self._execute_tool(tool_name, tool_args)
                        
                        # Track tool call
                        tc = ToolCall(
                            tool_name=tool_name,
                            arguments=tool_args,
                            result=result,
                            reasoning=assistant_message.content
                        )
                        trajectory.tool_calls.append(tc)
                        
                        # Add tool result to messages
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, indent=2)
                        }
                        messages.append(tool_message)
                        tool_results.append(result)
                    
                    iteration_data["tool_calls"] = len(assistant_message.tool_calls)
                    iteration_data["tools_used"] = [tc.function.name for tc in assistant_message.tool_calls]
                    
                    # Log reasoning if available
                    if assistant_message.content and self.config.agent.enable_reasoning:
                        logger.info(f"Iteration {iteration + 1} reasoning: {assistant_message.content}")
                    
                else:
                    # No tool calls, assistant is providing final answer
                    iteration_data["final_answer"] = True
                    trajectory.iterations.append(iteration_data)
                    
                    if self.config.verbose:
                        logger.info(f"Final answer after {iteration + 1} iterations")
                    
                    return assistant_message.content
                
                trajectory.iterations.append(iteration_data)
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {e}")
                iteration_data["error"] = str(e)
                trajectory.iterations.append(iteration_data)
                break
        
        # Max iterations reached, force a conclusion
        logger.warning(f"Max iterations ({self.config.agent.max_iterations}) reached")
        
        # Get final answer
        messages.append({
            "role": "user",
            "content": "Based on the information you've gathered, please provide your final answer to the original question."
        })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            return response.choices[0].message.content
        except:
            return "I've searched through the available memories but couldn't find enough information to fully answer your question."
    
    def _answer_direct(self,
                      query: str,
                      conversation_context: Optional[List[Dict[str, str]]],
                      trajectory: AgentTrajectory) -> str:
        """
        Answer using direct retrieval without agentic behavior (baseline)
        """
        # Simple retrieval
        search_results = self.memory_tools.memory_search(query)
        
        # Track the search
        trajectory.tool_calls.append(
            ToolCall(
                tool_name="memory_search",
                arguments={"query": query},
                result=search_results
            )
        )
        
        # Build context from search results
        context_chunks = []
        for result in search_results[:self.config.agent.max_memory_context]:
            context_chunks.append(f"[Memory from {result['conversation_id']}]:\n{result['content_preview']}")
        
        if not context_chunks:
            return "I couldn't find any relevant memories to answer your question."
        
        # Generate answer with retrieved context
        context_text = "\n\n".join(context_chunks)
        
        prompt = f"""Based on the following memories, answer the user's question.

User Question: {query}

Retrieved Memories:
{context_text}

Please provide a comprehensive answer based only on the information in the retrieved memories. If the memories don't contain enough information, say so."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions based on retrieved memories."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            if hasattr(response, "usage"):
                trajectory.total_tokens = response.usage.total_tokens
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I encountered an error while generating an answer: {str(e)}"
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute a tool and return results"""
        try:
            if tool_name == "memory_search":
                return self.memory_tools.memory_search(**arguments)
            
            elif tool_name == "get_full_memory":
                return self.memory_tools.get_full_memory(**arguments)
            
            elif tool_name == "get_conversation_context":
                return self.memory_tools.get_conversation_context(**arguments)
            
            elif tool_name == "expand_search":
                return self.memory_tools.expand_search(**arguments)
            
            else:
                return {"error": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error for {tool_name}: {e}")
            return {"error": str(e)}
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for the agent"""
        mode_context = ""
        if self.mode == RetrievalMode.CONTEXTUAL:
            mode_context = """
Note: The memory search uses contextual retrieval, which means each memory chunk has been enhanced 
with contextual descriptions that explain its place in the broader conversation. Pay attention to 
these context descriptions when evaluating relevance."""
        
        return f"""You are an intelligent assistant with access to a user's conversation history and memories.
Your task is to answer questions by searching through and synthesizing information from these memories.

## Important Guidelines:

1. **Use Tools Systematically**:
   - Start with `memory_search` to find relevant information
   - Use `get_full_memory` to retrieve complete details when needed
   - Use `get_conversation_context` to understand the broader context
   - Use `expand_search` if initial results are insufficient

2. **ReAct Pattern**:
   - Reason about what information you need
   - Act by calling appropriate tools
   - Observe the results
   - Iterate until you have sufficient information

3. **Be Thorough**:
   - Don't stop at the first result
   - Look for multiple relevant memories
   - Cross-reference information across conversations
   - Consider temporal aspects (when things were said)

4. **Accuracy**:
   - Only use information found in the memories
   - If information is incomplete or unclear, say so
   - Don't make assumptions beyond what's explicitly stated

5. **Synthesis**:
   - Combine information from multiple sources
   - Resolve any contradictions by noting the most recent information
   - Provide a comprehensive answer that addresses all aspects of the question

{mode_context}

Remember: Your credibility depends on providing accurate, well-researched answers based on the user's actual memories."""
    
    def _format_user_query(self, 
                          query: str, 
                          conversation_context: Optional[List[Dict[str, str]]]) -> str:
        """Format the user query with optional context"""
        formatted = f"User Question: {query}"
        
        if conversation_context:
            formatted += "\n\nRecent Conversation Context:\n"
            for msg in conversation_context[-5:]:  # Last 5 messages
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                formatted += f"{role}: {content[:200]}...\n" if len(content) > 200 else f"{role}: {content}\n"
        
        return formatted
    
    def compare_modes(self,
                     query: str,
                     modes: Optional[List[RetrievalMode]] = None) -> Dict[str, Any]:
        """
        Compare different retrieval modes on the same query
        
        Args:
            query: User question
            modes: Modes to compare (default: contextual vs non-contextual)
            
        Returns:
            Comparison results
        """
        modes = modes or [RetrievalMode.CONTEXTUAL, RetrievalMode.NON_CONTEXTUAL]
        results = {}
        
        for mode in modes:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {mode.value} mode")
            logger.info(f"{'='*60}")
            
            # Create agent with specific mode
            agent = AgenticMemoryAgent(
                user_id=self.user_id,
                config=self.config,
                mode=mode
            )
            
            # Copy the same indexed data
            agent.indexer = self.indexer
            
            # Get answer
            start_time = datetime.now()
            answer = agent.answer_with_memories(query)
            latency = (datetime.now() - start_time).total_seconds()
            
            # Get trajectory
            trajectory = agent.trajectories[-1] if agent.trajectories else None
            
            results[mode.value] = {
                "answer": answer,
                "latency_seconds": latency,
                "tool_calls": len(trajectory.tool_calls) if trajectory else 0,
                "iterations": len(trajectory.iterations) if trajectory else 0,
                "total_tokens": trajectory.total_tokens if trajectory else 0,
                "trajectory": trajectory
            }
        
        # Calculate differences
        if len(results) == 2:
            keys = list(results.keys())
            results["comparison"] = {
                "latency_diff": results[keys[1]]["latency_seconds"] - results[keys[0]]["latency_seconds"],
                "tool_calls_diff": results[keys[1]]["tool_calls"] - results[keys[0]]["tool_calls"],
                "tokens_diff": results[keys[1]]["total_tokens"] - results[keys[0]]["total_tokens"]
            }
        
        return results
    
    def get_search_trajectory(self, session_index: int = -1) -> Optional[Dict[str, Any]]:
        """
        Get the search trajectory for analysis
        
        Args:
            session_index: Which trajectory to get (-1 for most recent)
            
        Returns:
            Trajectory details
        """
        if not self.trajectories:
            return None
        
        trajectory = self.trajectories[session_index]
        
        # Format for display
        formatted = {
            "user_query": trajectory.user_query,
            "mode": trajectory.mode,
            "total_iterations": len(trajectory.iterations),
            "total_tool_calls": len(trajectory.tool_calls),
            "total_tokens": trajectory.total_tokens,
            "latency_ms": trajectory.latency_ms,
            "tool_sequence": [
                {
                    "tool": tc.tool_name,
                    "query": tc.arguments.get("query") or tc.arguments.get("chunk_id"),
                    "results_count": len(tc.result) if isinstance(tc.result, list) else 1
                }
                for tc in trajectory.tool_calls
            ],
            "final_answer_preview": trajectory.final_answer[:500] if trajectory.final_answer else None
        }
        
        return formatted
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get analytics about agent performance"""
        if not self.trajectories:
            return {"message": "No trajectories recorded yet"}
        
        total = len(self.trajectories)
        avg_latency = sum(t.latency_ms for t in self.trajectories) / total
        avg_tool_calls = sum(len(t.tool_calls) for t in self.trajectories) / total
        avg_tokens = sum(t.total_tokens for t in self.trajectories) / total
        
        # Tool usage distribution
        tool_usage = {}
        for t in self.trajectories:
            for tc in t.tool_calls:
                tool_usage[tc.tool_name] = tool_usage.get(tc.tool_name, 0) + 1
        
        return {
            "total_queries": total,
            "average_latency_ms": round(avg_latency, 2),
            "average_tool_calls": round(avg_tool_calls, 2),
            "average_tokens": round(avg_tokens),
            "tool_usage": tool_usage,
            "modes_used": list(set(t.mode for t in self.trajectories)),
            "search_analytics": self.memory_tools.get_search_analytics()
        }
