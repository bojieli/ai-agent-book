"""
Agentic RAG System for User Memory Evaluation

Main agent that provides tools for querying indexed conversations and managing memories.
Uses ReAct pattern for reasoning and tool usage.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Generator, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from config import Config, AgentConfig, LLMConfig
from conversation_chunker import ConversationChunker, ConversationChunk
from rag_indexer import RAGIndexerFactory, SearchResult
from memory_integration import MemoryRAGIntegration, MemorySearchResult


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Message:
    """Represents a message in the conversation"""
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ToolHandler:
    """Handles tool execution for the agent"""
    
    def __init__(self, 
                 rag_indexer,
                 memory_integration: MemoryRAGIntegration,
                 chunker: ConversationChunker):
        """Initialize tool handler"""
        self.rag_indexer = rag_indexer
        self.memory_integration = memory_integration
        self.chunker = chunker
        
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions for the agent"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_conversations",
                    "description": "Search indexed conversation history for relevant information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query to find relevant conversation chunks"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function", 
                "function": {
                    "name": "search_memories",
                    "description": "Search user memories with conversation context",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Query to search memories"
                            },
                            "include_context": {
                                "type": "boolean",
                                "description": "Include conversation context in results",
                                "default": True
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_conversation_details",
                    "description": "Get detailed information about a specific conversation chunk",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "chunk_id": {
                                "type": "string",
                                "description": "ID of the conversation chunk"
                            }
                        },
                        "required": ["chunk_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "extract_memory_from_conversation",
                    "description": "Extract and save important information as memory from conversation",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "conversation_id": {
                                "type": "string",
                                "description": "ID of the conversation to extract from"
                            },
                            "memory_type": {
                                "type": "string",
                                "enum": ["auto", "note", "card"],
                                "description": "Type of memory to create",
                                "default": "auto"
                            }
                        },
                        "required": ["conversation_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "update_memory",
                    "description": "Update an existing memory with new information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {
                                "type": "string",
                                "description": "ID of the memory to update"
                            },
                            "new_content": {
                                "type": "string",
                                "description": "New content for the memory"
                            }
                        },
                        "required": ["memory_id", "new_content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "consolidate_memories",
                    "description": "Consolidate similar memories to reduce redundancy",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "similarity_threshold": {
                                "type": "number",
                                "description": "Similarity threshold for consolidation (0.0-1.0)",
                                "default": 0.8
                            }
                        }
                    }
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """Execute a tool and return the result"""
        try:
            if tool_name == "search_conversations":
                results = self.rag_indexer.search(
                    tool_args.get("query"),
                    tool_args.get("top_k", 5)
                )
                
                if not results:
                    return "No relevant conversation chunks found."
                
                formatted_results = []
                for idx, result in enumerate(results, 1):
                    formatted_results.append(
                        f"{idx}. Conversation {result.conversation_id} "
                        f"(Rounds {result.start_round}-{result.end_round}, Score: {result.score:.2f}):\n"
                        f"{result.text[:300]}..."
                    )
                
                return "\n\n".join(formatted_results)
            
            elif tool_name == "search_memories":
                results = self.memory_integration.search_memories_with_context(
                    tool_args.get("query"),
                    tool_args.get("include_context", True),
                    tool_args.get("top_k", 5)
                )
                
                if not results:
                    return "No relevant memories found."
                
                formatted_results = []
                for idx, result in enumerate(results, 1):
                    text = f"{idx}. {result.memory_type.upper()} (ID: {result.memory_id}, Score: {result.relevance_score:.2f}):\n"
                    text += f"Content: {result.content}\n"
                    
                    if result.conversation_context:
                        text += "Related conversations:\n"
                        for ctx in result.conversation_context[:2]:
                            text += f"  - {ctx['conversation_id']} (rounds {ctx['rounds']}): {ctx['text_preview'][:100]}...\n"
                    
                    formatted_results.append(text)
                
                return "\n\n".join(formatted_results)
            
            elif tool_name == "get_conversation_details":
                chunk_id = tool_args.get("chunk_id")
                
                # Load from index
                if hasattr(self.rag_indexer, 'chunks_store'):
                    chunk_data = self.rag_indexer.chunks_store.get(chunk_id)
                    if chunk_data:
                        return json.dumps(chunk_data, indent=2, ensure_ascii=False)
                
                return f"Chunk {chunk_id} not found in index."
            
            elif tool_name == "extract_memory_from_conversation":
                conversation_id = tool_args.get("conversation_id")
                memory_type = tool_args.get("memory_type", "auto")
                
                # Find conversation chunks
                chunks = []
                if hasattr(self.rag_indexer, 'chunks_store'):
                    for chunk_data in self.rag_indexer.chunks_store.values():
                        if chunk_data.get("conversation_id") == conversation_id:
                            chunks.append(chunk_data)
                
                if not chunks:
                    return f"No conversation found with ID: {conversation_id}"
                
                # Extract memories
                memory_ids = self.memory_integration.add_memory_from_conversation(
                    {"messages": self._reconstruct_messages(chunks)},
                    memory_type
                )
                
                if memory_ids:
                    return f"Successfully extracted {len(memory_ids)} memories: {', '.join(memory_ids)}"
                else:
                    return "No memories could be extracted from the conversation."
            
            elif tool_name == "update_memory":
                memory_id = tool_args.get("memory_id")
                new_content = tool_args.get("new_content")
                
                # Find memory
                if memory_id in self.memory_integration.memory_cache:
                    old_content = self.memory_integration.memory_cache[memory_id].get("content", "")
                    
                    # Create search result for update
                    search_result = MemorySearchResult(
                        memory_type="note",
                        memory_id=memory_id,
                        content=old_content,
                        relevance_score=1.0
                    )
                    
                    success = self.memory_integration.update_memory_from_query(
                        search_result,
                        new_content
                    )
                    
                    if success:
                        return f"Successfully updated memory {memory_id}"
                    else:
                        return f"Failed to update memory {memory_id}"
                else:
                    return f"Memory {memory_id} not found"
            
            elif tool_name == "consolidate_memories":
                threshold = tool_args.get("similarity_threshold", 0.8)
                report = self.memory_integration.consolidate_memories(threshold)
                
                return (f"Consolidation complete:\n"
                       f"- Consolidated {report['consolidated_count']} memories\n"
                       f"- Found {report['groups_found']} similar groups\n"
                       f"- Total memories: {report['total_memories']}")
            
            else:
                return f"Unknown tool: {tool_name}"
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool: {str(e)}"
    
    def _reconstruct_messages(self, chunks: List[Dict]) -> List[Dict]:
        """Reconstruct messages from chunks"""
        messages = []
        seen_rounds = set()
        
        for chunk in sorted(chunks, key=lambda x: x.get("start_round", 0)):
            for round_data in chunk.get("rounds", []):
                round_num = round_data.get("round_number")
                if round_num not in seen_rounds:
                    messages.append({
                        "role": "user",
                        "content": round_data.get("user_message", "")
                    })
                    messages.append({
                        "role": "assistant",
                        "content": round_data.get("assistant_message", "")
                    })
                    seen_rounds.add(round_num)
        
        return messages


class UserMemoryRAGAgent:
    """Main agent for user memory evaluation with RAG"""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the agent"""
        self.config = config or Config.from_env()
        
        # Initialize components
        self._init_llm_client()
        self._init_components()
        
        # Conversation history
        self.conversation_history: List[Dict[str, Any]] = []
        
        # Agent state
        self.iteration_count = 0
        self.max_iterations = self.config.agent.max_iterations
        
        logger.info(f"Initialized UserMemoryRAGAgent with provider: {self.config.llm.provider}")
    
    def _init_llm_client(self):
        """Initialize LLM client based on configuration"""
        if self.config.llm.provider == "openai":
            self.client = OpenAI(
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url
            )
        elif self.config.llm.provider in ["kimi", "moonshot"]:
            self.client = OpenAI(
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url or "https://api.moonshot.cn/v1"
            )
        elif self.config.llm.provider == "doubao":
            self.client = OpenAI(
                api_key=self.config.llm.api_key,
                base_url=self.config.llm.base_url or "https://ark.cn-beijing.volcanicengineapi.com/api/v3"
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config.llm.provider}")
    
    def _init_components(self):
        """Initialize RAG and memory components"""
        # Initialize chunker
        self.chunker = ConversationChunker(self.config.chunking)
        
        # Initialize RAG indexer
        self.rag_indexer = RAGIndexerFactory.create(self.config.rag, self.config.llm)
        
        # Initialize memory integration
        self.memory_integration = MemoryRAGIntegration(
            self.config.memory,
            self.config.rag
        )
        
        # Initialize tool handler
        self.tool_handler = ToolHandler(
            self.rag_indexer,
            self.memory_integration,
            self.chunker
        )
        
        # Get tool definitions
        self.tools = self.tool_handler.get_tool_definitions()
    
    def build_index_from_history(self, 
                                history_file: str,
                                save_chunks: bool = True) -> Dict[str, Any]:
        """
        Build RAG index from conversation history file.
        This is the learning phase where conversations are chunked and indexed.
        
        Args:
            history_file: Path to conversation history JSON file
            save_chunks: Whether to save chunks to file
            
        Returns:
            Indexing report
        """
        logger.info(f"Building index from history file: {history_file}")
        
        # Chunk the conversation history
        chunks, metadata = self.chunker.chunk_conversation_history(history_file)
        
        # Save chunks if requested
        if save_chunks:
            chunks_file = Path(self.config.rag.index_path) / "conversation_chunks.json"
            self.chunker.save_chunks(chunks, str(chunks_file))
        
        # Index chunks in RAG system
        index_result = self.rag_indexer.index_chunks(chunks)
        
        # Extract memories from conversations
        memory_count = 0
        for chunk in chunks[:5]:  # Process first 5 chunks as example
            conversation_data = {
                "messages": self._chunk_to_messages(chunk),
                "conversation_id": chunk.conversation_id
            }
            memory_ids = self.memory_integration.add_memory_from_conversation(
                conversation_data,
                "auto"
            )
            memory_count += len(memory_ids)
        
        report = {
            "chunks_created": len(chunks),
            "chunks_indexed": index_result.get("indexed", 0),
            "memories_extracted": memory_count,
            "metadata": metadata,
            "index_result": index_result
        }
        
        logger.info(f"Index built successfully: {report['chunks_indexed']} chunks indexed")
        return report
    
    def _chunk_to_messages(self, chunk: ConversationChunk) -> List[Dict[str, Any]]:
        """Convert chunk to messages format"""
        messages = []
        for round in chunk.rounds:
            messages.append({
                "role": "user",
                "content": round.user_message
            })
            messages.append({
                "role": "assistant",
                "content": round.assistant_message
            })
        return messages
    
    def query(self, user_query: str, stream: bool = False) -> Generator[str, None, None]:
        """
        Process user query with RAG-enhanced retrieval.
        This is the evaluation/inference phase.
        
        Args:
            user_query: User's question
            stream: Whether to stream the response
            
        Yields:
            Response chunks if streaming, otherwise complete response
        """
        logger.info(f"Processing query: {user_query[:100]}...")
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_query
        })
        
        # Reset iteration count
        self.iteration_count = 0
        
        # Build system prompt
        system_prompt = self._build_system_prompt()
        
        # Prepare messages for LLM
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_history
        
        # Generate response with tools
        if stream and self.config.agent.stream_response:
            yield from self._generate_streaming_response(messages)
        else:
            response = self._generate_response(messages)
            yield response
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for the agent"""
        return f"""You are an intelligent assistant with access to indexed conversation history and user memories.
        
Your task is to answer user questions by searching through historical conversations and memories.

Available tools:
1. search_conversations: Search indexed conversation chunks
2. search_memories: Search user memories with context
3. get_conversation_details: Get details of a specific conversation
4. extract_memory_from_conversation: Extract memories from conversations
5. update_memory: Update existing memories
6. consolidate_memories: Consolidate similar memories

Use the ReAct pattern:
1. Thought: Analyze what information is needed
2. Action: Use appropriate tools to gather information
3. Observation: Review tool results
4. Repeat as needed (max {self.max_iterations} iterations)
5. Final Answer: Provide comprehensive response

Guidelines:
- Search both conversations and memories for comprehensive answers
- Cite specific conversation rounds when referencing historical information
- Update memories when you find contradictions or new information
- Be precise and factual based on the indexed information
"""
    
    def _generate_response(self, messages: List[Dict[str, Any]]) -> str:
        """Generate non-streaming response"""
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            # Call LLM with tools
            response = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            message = response.choices[0].message
            
            # Add assistant message to history
            messages.append(message.model_dump())
            
            # Check for tool calls
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    # Execute tool
                    tool_result = self.tool_handler.execute_tool(
                        tool_call.function.name,
                        json.loads(tool_call.function.arguments)
                    )
                    
                    # Add tool result to messages
                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call.id
                    })
            else:
                # No more tool calls, return final response
                self.conversation_history.append(message.model_dump())
                return message.content
        
        return "Maximum iterations reached. Please refine your query."
    
    def _generate_streaming_response(self, messages: List[Dict[str, Any]]) -> Generator[str, None, None]:
        """Generate streaming response"""
        accumulated_response = ""
        
        while self.iteration_count < self.max_iterations:
            self.iteration_count += 1
            
            # Call LLM with tools
            stream = self.client.chat.completions.create(
                model=self.config.llm.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens,
                stream=True
            )
            
            # Process stream
            tool_calls = []
            current_tool_call = None
            
            for chunk in stream:
                if chunk.choices[0].delta.tool_calls:
                    # Handle tool calls
                    for tc in chunk.choices[0].delta.tool_calls:
                        if tc.index == 0 and not current_tool_call:
                            current_tool_call = {
                                "id": tc.id,
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments or ""
                                }
                            }
                        elif current_tool_call:
                            current_tool_call["function"]["arguments"] += tc.function.arguments or ""
                
                elif chunk.choices[0].delta.content:
                    # Stream content
                    content = chunk.choices[0].delta.content
                    accumulated_response += content
                    yield content
            
            # Process accumulated tool calls
            if current_tool_call:
                tool_calls.append(current_tool_call)
                
                # Execute tools
                for tool_call in tool_calls:
                    tool_result = self.tool_handler.execute_tool(
                        tool_call["function"]["name"],
                        json.loads(tool_call["function"]["arguments"])
                    )
                    
                    # Add to messages for next iteration
                    messages.append({
                        "role": "assistant",
                        "content": None,
                        "tool_calls": [tool_call]
                    })
                    messages.append({
                        "role": "tool",
                        "content": tool_result,
                        "tool_call_id": tool_call["id"]
                    })
            else:
                # No tool calls, we're done
                self.conversation_history.append({
                    "role": "assistant",
                    "content": accumulated_response
                })
                break
        
        if self.iteration_count >= self.max_iterations:
            yield "\n\n[Maximum iterations reached]"
    
    def reset(self):
        """Reset agent state"""
        self.conversation_history = []
        self.iteration_count = 0
        logger.info("Agent state reset")
    
    def save_state(self, filepath: str):
        """Save agent state to file"""
        state = {
            "conversation_history": self.conversation_history,
            "config": self.config.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Agent state saved to {filepath}")
    
    def load_state(self, filepath: str):
        """Load agent state from file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        self.conversation_history = state.get("conversation_history", [])
        logger.info(f"Agent state loaded from {filepath}")
