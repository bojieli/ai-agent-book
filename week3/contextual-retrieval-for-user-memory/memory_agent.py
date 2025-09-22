"""
Enhanced Memory Agent with Embedded Dual-Context System
Combines Advanced JSON Cards (always in context) with Contextual RAG (dynamic retrieval)
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# Import local modules
from config import Config
from memory_indexer import ContextualMemoryIndexer
from memory_tools import MemorySearchTools, get_tool_definitions
from json_memory_manager import AdvancedJSONMemoryManager

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
    cards_used: int = 0
    chunks_retrieved: int = 0
    insights_generated: int = 0


class MemoryAgent:
    """
    Unified Memory Agent with embedded dual-context system
    Always uses both Advanced JSON Cards and Contextual RAG
    """
    
    def __init__(self,
                 user_id: str,
                 config: Optional[Config] = None):
        """
        Initialize the memory agent with dual-context system
        
        Args:
            user_id: User identifier
            config: Configuration
        """
        self.user_id = user_id
        self.config = config or Config.from_env()
        
        # Initialize Advanced JSON Cards manager (structured memory - always in context)
        self.cards_manager = AdvancedJSONMemoryManager(user_id)
        
        # Initialize Contextual Indexer (conversation details - retrieved dynamically)
        self.indexer = ContextualMemoryIndexer(
            user_id=user_id,
            config=self.config,
            enable_contextual=True  # Always use contextual retrieval
        )
        
        # Initialize memory search tools
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
        
        # Track proactive insights
        self.proactive_insights = []
        
        logger.info(f"Initialized MemoryAgent for user {user_id} with dual-context system")
    
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
    
    def process_conversation(self, conversation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a conversation to update both memory systems
        
        Args:
            conversation: Conversation history
            
        Returns:
            Processing results
        """
        results = {
            "conversation_id": conversation.get("conversation_id"),
            "chunks_created": [],
            "cards_updated": [],
            "insights": []
        }
        
        # Index conversation with contextual retrieval
        logger.info("Indexing conversation with contextual retrieval...")
        chunk_ids = self.indexer.index_conversation(
            conversation,
            chunk_size=self.config.indexing.chunk_size,
            show_progress=False
        )
        results["chunks_created"] = chunk_ids
        
        # Extract and update memory cards
        logger.info("Extracting memory cards from conversation...")
        cards = self._extract_memory_cards(conversation)
        results["cards_updated"] = cards
        
        # Generate proactive insights
        insights = self._generate_insights(conversation)
        results["insights"] = insights
        self.proactive_insights.extend(insights)
        
        logger.info(f"Processed conversation: {len(chunk_ids)} chunks, {len(cards)} cards, {len(insights)} insights")
        
        return results
    
    def answer(self,
              query: str,
              conversation_context: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Answer a query using the dual-context system with proactive insights
        
        Args:
            query: User's question
            conversation_context: Optional recent conversation for context
            
        Returns:
            Agent's answer with proactive insights when relevant
        """
        # Start trajectory tracking
        trajectory = AgentTrajectory(user_query=query)
        start_time = datetime.now()
        
        try:
            # Get structured memory context (always included)
            cards_context = self.cards_manager.get_context_string()
            trajectory.cards_used = sum(len(cards) for cards in self.cards_manager.categories.values())
            
            # Check for relevant proactive insights
            relevant_insights = self._find_relevant_insights(query)
            
            # Build system prompt with dual context
            system_prompt = self._build_system_prompt(cards_context, relevant_insights)
            
            # Build messages for agent interaction
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._format_user_query(query, conversation_context)}
            ]
            
            # ReAct loop with tool calling
            answer = self._execute_react_loop(messages, trajectory)
            
            # Record final metrics
            trajectory.final_answer = answer
            trajectory.latency_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            trajectory.insights_generated = len(relevant_insights)
            self.trajectories.append(trajectory)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            trajectory.final_answer = f"I encountered an error while searching memories: {str(e)}"
            self.trajectories.append(trajectory)
            return trajectory.final_answer
    
    def _extract_memory_cards(self, conversation: Dict[str, Any]) -> List[str]:
        """Extract structured memory cards from conversation"""
        messages = conversation.get("messages", [])
        if not messages:
            return []
        
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}"
            for msg in messages[:50]  # Limit to first 50 messages
        ])
        
        prompt = f"""Analyze this conversation and extract key information for memory cards.
Focus on facts that would be needed for future assistance.

Current Memory Cards Summary:
{self.cards_manager.get_context_string()[:1000]}

Conversation:
{conversation_text[:3000]}

Return JSON array of memory operations:
[
  {{
    "operation": "create" or "update",
    "category": "personal/work/health/finance/family/preferences",
    "card_key": "unique_key",
    "card": {{
      "facts": {{}},
      "backstory": "1-2 sentences about context",
      "person": "who this is about",
      "relationship": "relationship to user",
      "date_created": "YYYY-MM-DD"
    }}
  }}
]

Only return JSON, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            
            # Find JSON array in response
            start = content.find('[')
            end = content.rfind(']') + 1
            if start >= 0 and end > start:
                content = content[start:end]
            
            operations = json.loads(content)
            
            updated_cards = []
            for op in operations:
                if op.get("operation") == "create":
                    memory_id = self.cards_manager.add_memory(
                        content={
                            "category": op.get("category", "general"),
                            "card_key": op.get("card_key", str(datetime.now().timestamp())[:10]),
                            "card": op.get("card", {})
                        },
                        session_id=conversation.get("conversation_id", "unknown")
                    )
                    updated_cards.append(memory_id)
            
            return updated_cards
            
        except Exception as e:
            logger.error(f"Error extracting memory cards: {e}")
            return []
    
    def _generate_insights(self, conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate proactive insights from conversation and memory"""
        insights = []
        
        # Simple heuristic-based insights
        messages_text = " ".join([
            msg.get("content", "") for msg in conversation.get("messages", [])
        ]).lower()
        
        # Check for travel mentions
        if any(word in messages_text for word in ["flight", "trip", "travel", "mexico", "international"]):
            if any(word in messages_text for word in ["passport", "expire", "march"]):
                insights.append({
                    "type": "warning",
                    "message": "Passport expiry should be checked before international travel",
                    "priority": "high"
                })
        
        # Check for insurance mentions
        if any(word in messages_text for word in ["insurance", "renewal", "premium"]):
            insights.append({
                "type": "opportunity",
                "message": "Consider comparing insurance quotes before renewal",
                "priority": "medium"
            })
        
        # Check for health mentions
        if any(word in messages_text for word in ["medication", "doctor", "checkup", "allergy"]):
            insights.append({
                "type": "reminder",
                "message": "Regular health checkups and medication reviews are important",
                "priority": "medium"
            })
        
        return insights
    
    def _find_relevant_insights(self, query: str) -> List[Dict[str, Any]]:
        """Find proactive insights relevant to the query"""
        query_lower = query.lower()
        relevant = []
        
        for insight in self.proactive_insights:
            # Simple keyword matching for relevance
            if any(word in query_lower for word in insight.get("message", "").lower().split()):
                relevant.append(insight)
        
        return relevant[:3]  # Limit to top 3 most relevant
    
    def _build_system_prompt(self, cards_context: str, insights: List[Dict[str, Any]]) -> str:
        """Build system prompt with dual context"""
        insights_text = ""
        if insights:
            insights_text = "\n\nPROACTIVE INSIGHTS TO CONSIDER:\n"
            for insight in insights:
                priority = insight.get("priority", "medium").upper()
                type_str = insight.get("type", "info").upper()
                message = insight.get("message", "")
                insights_text += f"- [{priority} {type_str}] {message}\n"
        
        return f"""You are an intelligent assistant with dual-context memory:

1. STRUCTURED MEMORY (Advanced JSON Cards - Always Available):
{cards_context}

2. CONVERSATION DETAILS (Retrieved Dynamically via Tools):
Use the memory_search tool to find specific conversation details when needed.

{insights_text}

Key Behaviors:
- Use structured memory for key facts, relationships, and metadata
- Use tool searches for specific conversation details and context
- Be proactive when you identify opportunities to help
- Reference specific information to show you remember
- Provide warnings about potential issues (expired documents, deadlines, etc.)
- Suggest optimizations and opportunities based on patterns you observe

Remember: You have both instant access to structured knowledge AND the ability to search for detailed context."""
    
    def _format_user_query(self, query: str, conversation_context: Optional[List[Dict[str, str]]]) -> str:
        """Format the user query with optional context"""
        formatted = f"User Question: {query}"
        
        if conversation_context:
            formatted += "\n\nRecent Conversation Context:\n"
            for msg in conversation_context[-5:]:
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:200]
                formatted += f"{role}: {content}...\n" if len(content) == 200 else f"{role}: {content}\n"
        
        return formatted
    
    def _execute_react_loop(self, messages: List[Dict[str, Any]], trajectory: AgentTrajectory) -> str:
        """Execute ReAct pattern with tool calling"""
        for iteration in range(self.config.agent.max_iterations):
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
                        
                        # Track chunks retrieved
                        if tool_name == "memory_search" and isinstance(result, list):
                            trajectory.chunks_retrieved += len(result)
                        
                        # Add tool result to messages
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result, indent=2)
                        }
                        messages.append(tool_message)
                
                else:
                    # No tool calls, assistant is providing final answer
                    return assistant_message.content
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration + 1}: {e}")
                break
        
        # Max iterations reached or error, force conclusion
        messages.append({
            "role": "user",
            "content": "Based on the information gathered, provide your final answer."
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
            return "I've searched through available memories but couldn't fully answer your question."
    
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
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the memory system"""
        return {
            "user_id": self.user_id,
            "structured_memory": {
                "total_cards": sum(len(cards) for cards in self.cards_manager.categories.values()),
                "categories": list(self.cards_manager.categories.keys()),
                "sample_card": self._get_sample_card()
            },
            "conversation_memory": self.indexer.get_statistics(),
            "agent_performance": {
                "total_queries": len(self.trajectories),
                "avg_chunks_retrieved": sum(t.chunks_retrieved for t in self.trajectories) / len(self.trajectories) if self.trajectories else 0,
                "avg_tool_calls": sum(len(t.tool_calls) for t in self.trajectories) / len(self.trajectories) if self.trajectories else 0,
                "proactive_insights": len(self.proactive_insights)
            }
        }
    
    def _get_sample_card(self) -> Optional[Dict[str, Any]]:
        """Get a sample memory card for display"""
        for category, cards in self.cards_manager.categories.items():
            for card_key, card in cards.items():
                return {"category": category, "key": card_key, "card": card}
        return None
