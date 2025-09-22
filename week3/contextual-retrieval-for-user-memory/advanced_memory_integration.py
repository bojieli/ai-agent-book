"""
Advanced Memory Integration: Combining JSON Cards with Contextual RAG
Implements dual-context system for proactive service
"""

import json
import logging
import uuid
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from openai import OpenAI

from config import Config, RetrievalMode
from memory_indexer import ContextualMemoryIndexer
from memory_tools import MemorySearchTools
from agentic_memory_agent import AgenticMemoryAgent, ToolCall, AgentTrajectory

# Import memory manager from week2/user-memory
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "week2" / "user-memory"))
from memory_manager import AdvancedJSONMemoryManager, BaseMemoryManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MemoryCard:
    """Enhanced memory card with full context"""
    category: str
    card_key: str
    facts: Dict[str, Any]  # Core facts/information
    backstory: str  # Narrative context of how this information was learned
    person: str  # Who this information is about
    relationship: str  # Relationship to the user
    date_created: str
    date_updated: str
    source_conversations: List[str] = field(default_factory=list)  # Links to conversation chunks
    confidence: float = 0.9  # Confidence in this information
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryCard':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ProactiveInsight:
    """Represents a proactive insight derived from memory synthesis"""
    insight_type: str  # warning, suggestion, reminder, opportunity
    message: str
    confidence: float
    supporting_cards: List[str]  # Memory card IDs
    supporting_chunks: List[str]  # Conversation chunk IDs
    action_items: List[str] = field(default_factory=list)
    priority: str = "medium"  # low, medium, high, critical


class AdvancedMemoryIntegration:
    """
    Dual-context memory system combining:
    1. Advanced JSON Cards (structured summary, always in context)
    2. Contextual RAG (dynamic retrieval of conversation details)
    """
    
    def __init__(self,
                 user_id: str,
                 config: Optional[Config] = None):
        """
        Initialize the advanced memory integration system
        
        Args:
            user_id: User identifier
            config: Configuration object
        """
        self.user_id = user_id
        self.config = config or Config.from_env()
        
        # Initialize Advanced JSON Cards manager (structured memory)
        self.cards_manager = AdvancedJSONMemoryManager(user_id)
        
        # Initialize Contextual Indexer (conversation details)
        self.indexer = ContextualMemoryIndexer(
            user_id=user_id,
            config=self.config,
            enable_contextual=True
        )
        
        # Initialize memory search tools
        self.search_tools = MemorySearchTools(
            user_id=user_id,
            indexer=self.indexer,
            config=self.config
        )
        
        # Initialize LLM client for synthesis
        self._init_llm_client()
        
        # Track proactive insights
        self.proactive_insights: List[ProactiveInsight] = []
        
        logger.info(f"Initialized AdvancedMemoryIntegration for user {user_id}")
    
    def _init_llm_client(self):
        """Initialize LLM client"""
        llm_config = self.config.llm
        api_key = llm_config.get_api_key()
        base_url = llm_config.get_base_url()
        
        if base_url:
            self.client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = OpenAI(api_key=api_key)
        
        self.model = llm_config.get_model_name()
    
    def process_conversation(self,
                           conversation: Dict[str, Any],
                           generate_cards: bool = True) -> Dict[str, Any]:
        """
        Process a conversation to update both memory systems
        
        Args:
            conversation: Conversation history
            generate_cards: Whether to generate/update memory cards
            
        Returns:
            Processing results
        """
        results = {
            "conversation_id": conversation.get("conversation_id"),
            "chunks_created": [],
            "cards_updated": [],
            "insights_generated": []
        }
        
        # Phase 1: Index conversation with contextual retrieval
        logger.info("Phase 1: Indexing conversation with contextual retrieval")
        chunk_ids = self.indexer.index_conversation(
            conversation,
            chunk_size=self.config.indexing.chunk_size,
            show_progress=True
        )
        results["chunks_created"] = chunk_ids
        
        # Phase 2: Extract and update memory cards
        if generate_cards:
            logger.info("Phase 2: Extracting memory cards from conversation")
            cards = self._extract_memory_cards(conversation)
            results["cards_updated"] = cards
        
        # Phase 3: Generate proactive insights
        logger.info("Phase 3: Generating proactive insights")
        insights = self._generate_proactive_insights(conversation)
        results["insights_generated"] = insights
        
        return results
    
    def _extract_memory_cards(self, conversation: Dict[str, Any]) -> List[str]:
        """
        Extract structured memory cards from conversation
        Uses LLM to identify key facts and create Advanced JSON Cards
        """
        messages = conversation.get("messages", [])
        conversation_text = "\n".join([
            f"{msg.get('role', 'unknown').upper()}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        prompt = f"""Analyze this conversation and extract key information to create or update memory cards.
For each significant piece of information, create a memory card with:

1. Category (e.g., personal, work, health, finance, family, preferences)
2. Card key (unique identifier for this information)
3. Facts (structured key-value pairs)
4. Backstory (1-2 sentences about how/why this information was learned)
5. Person (who this information is about - user or someone else)
6. Relationship (e.g., primary account holder, spouse, child, parent)

Focus on:
- Factual information that would be needed for future assistance
- Preferences and patterns
- Important dates, numbers, and identifiers
- Relationships and connections

Current Memory Cards:
{self.cards_manager.get_context_string()}

Conversation:
{conversation_text[:4000]}  # Limit for context

Return a JSON array of memory card operations:
[
  {{
    "operation": "create" or "update" or "delete",
    "category": "category_name",
    "card_key": "unique_key",
    "card": {{
      "facts": {{}},
      "backstory": "...",
      "person": "...",
      "relationship": "...",
      "date_created": "..."
    }}
  }}
]

IMPORTANT: Only return the JSON array, no other text."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content.strip()
            
            # Parse JSON response
            operations = json.loads(content)
            
            updated_cards = []
            for op in operations:
                operation = op.get("operation", "create")
                category = op.get("category", "general")
                card_key = op.get("card_key", str(uuid.uuid4())[:8])
                card = op.get("card", {})
                
                # Add metadata
                card["source_conversations"] = [conversation.get("conversation_id")]
                
                if operation == "create":
                    memory_id = self.cards_manager.add_memory(
                        content={
                            "category": category,
                            "card_key": card_key,
                            "card": card
                        },
                        session_id=conversation.get("conversation_id", "unknown")
                    )
                    updated_cards.append(memory_id)
                    logger.info(f"Created memory card: {memory_id}")
                    
                elif operation == "update":
                    memory_id = f"{category}.{card_key}"
                    success = self.cards_manager.update_memory(
                        memory_id=memory_id,
                        content={"card": card},
                        session_id=conversation.get("conversation_id", "unknown")
                    )
                    if success:
                        updated_cards.append(memory_id)
                        logger.info(f"Updated memory card: {memory_id}")
                        
                elif operation == "delete":
                    memory_id = f"{category}.{card_key}"
                    self.cards_manager.delete_memory(memory_id)
                    logger.info(f"Deleted memory card: {memory_id}")
            
            return updated_cards
            
        except Exception as e:
            logger.error(f"Error extracting memory cards: {e}")
            return []
    
    def _generate_proactive_insights(self, 
                                    conversation: Dict[str, Any]) -> List[ProactiveInsight]:
        """
        Generate proactive insights by synthesizing memory cards and conversation context
        This is where the magic happens - combining structured and unstructured memory
        """
        insights = []
        
        # Get all memory cards
        memory_context = self.cards_manager.get_context_string()
        
        # Search for related conversation chunks
        conversation_id = conversation.get("conversation_id")
        recent_chunks = self.search_tools.get_conversation_context(conversation_id)
        
        prompt = f"""Based on the user's memory cards and recent conversation, identify proactive insights.

Memory Cards (Structured Knowledge):
{memory_context}

Recent Conversation Context:
{json.dumps(recent_chunks[:5], indent=2)}

Identify opportunities for proactive assistance:
1. Warnings: Upcoming expirations, deadlines, or issues
2. Suggestions: Based on patterns and preferences
3. Reminders: Important tasks or follow-ups
4. Opportunities: Connections between different pieces of information

For each insight, provide:
- Type (warning/suggestion/reminder/opportunity)
- Message (clear, actionable message for the user)
- Priority (low/medium/high/critical)
- Action items (specific steps the user should take)
- Confidence (0.0-1.0)

Return as JSON array. Only include insights with confidence > 0.7."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content.strip()
            insights_data = json.loads(content)
            
            for insight_data in insights_data:
                if insight_data.get("confidence", 0) > 0.7:
                    insight = ProactiveInsight(
                        insight_type=insight_data.get("type", "suggestion"),
                        message=insight_data.get("message", ""),
                        confidence=insight_data.get("confidence", 0.8),
                        supporting_cards=[],  # Could be enhanced to link specific cards
                        supporting_chunks=recent_chunks[:3] if recent_chunks else [],
                        action_items=insight_data.get("action_items", []),
                        priority=insight_data.get("priority", "medium")
                    )
                    insights.append(insight)
                    self.proactive_insights.append(insight)
                    
                    logger.info(f"Generated {insight.priority} {insight.insight_type}: {insight.message[:100]}...")
            
        except Exception as e:
            logger.error(f"Error generating proactive insights: {e}")
        
        return insights
    
    def answer_with_dual_context(self,
                                query: str,
                                mode: str = "proactive") -> Tuple[str, Dict[str, Any]]:
        """
        Answer a query using both memory systems
        
        Args:
            query: User's question
            mode: "proactive" (with insights) or "reactive" (just answer)
            
        Returns:
            Tuple of (answer, metadata)
        """
        metadata = {
            "mode": mode,
            "cards_used": 0,
            "chunks_retrieved": 0,
            "insights_provided": 0
        }
        
        # Get structured memory context (always included)
        cards_context = self.cards_manager.get_context_string()
        metadata["cards_used"] = len(self.cards_manager.categories)
        
        # Search for relevant conversation chunks
        search_results = self.search_tools.memory_search(query, top_k=5)
        metadata["chunks_retrieved"] = len(search_results)
        
        # Build the dual context
        system_prompt = f"""You are an intelligent assistant with access to both:
1. STRUCTURED MEMORY (Always Available): User's key information organized in JSON cards
2. CONVERSATION DETAILS (Retrieved Dynamically): Specific conversation excerpts

Your task is to provide helpful, personalized responses that leverage both memory types.

STRUCTURED MEMORY:
{cards_context}

When answering:
- Use structured memory for key facts and relationships
- Use conversation details for specific context and nuance
- Be proactive when you identify opportunities to help
- Reference specific information to show you remember"""
        
        # Build conversation context from search results
        conversation_context = "RETRIEVED CONVERSATION DETAILS:\n"
        for i, result in enumerate(search_results, 1):
            conversation_context += f"\n[Detail {i}]:\n"
            conversation_context += f"From: {result['conversation_id']}\n"
            if result.get('context_description'):
                conversation_context += f"Context: {result['context_description']}\n"
            conversation_context += f"Content: {result['content_preview']}\n"
        
        # Add proactive insights if in proactive mode
        proactive_context = ""
        if mode == "proactive" and self.proactive_insights:
            relevant_insights = [
                i for i in self.proactive_insights 
                if i.priority in ["high", "critical"] or i.confidence > 0.85
            ][:3]
            
            if relevant_insights:
                proactive_context = "\n\nPROACTIVE INSIGHTS TO CONSIDER:\n"
                for insight in relevant_insights:
                    proactive_context += f"- [{insight.insight_type.upper()}] {insight.message}\n"
                    if insight.action_items:
                        proactive_context += f"  Actions: {', '.join(insight.action_items)}\n"
                
                metadata["insights_provided"] = len(relevant_insights)
        
        # Generate answer
        user_prompt = f"{conversation_context}\n{proactive_context}\nUser Question: {query}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.llm.temperature,
                max_tokens=self.config.llm.max_tokens
            )
            
            answer = response.choices[0].message.content
            
            # Add usage metadata
            if hasattr(response, "usage"):
                metadata["tokens_used"] = response.usage.total_tokens
            
            return answer, metadata
            
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return f"I encountered an error: {str(e)}", metadata
    
    def demonstrate_proactive_service(self, scenario: str = "default") -> Dict[str, Any]:
        """
        Demonstrate proactive service capabilities
        
        Args:
            scenario: Predefined scenario to demonstrate
            
        Returns:
            Demonstration results
        """
        demonstrations = {
            "passport_expiry": self._demo_passport_expiry,
            "insurance_optimization": self._demo_insurance_optimization,
            "health_reminders": self._demo_health_reminders,
            "financial_opportunities": self._demo_financial_opportunities
        }
        
        if scenario in demonstrations:
            return demonstrations[scenario]()
        
        # Default demonstration
        return self._demo_comprehensive()
    
    def _demo_passport_expiry(self) -> Dict[str, Any]:
        """Demonstrate passport expiry detection from flight booking"""
        # Simulate memory state
        self.cards_manager.add_memory(
            content={
                "category": "personal",
                "card_key": "passport",
                "card": {
                    "facts": {
                        "number": "A12345678",
                        "expiry_date": "2024-03-15",
                        "issuing_country": "USA"
                    },
                    "backstory": "User provided passport details during profile setup",
                    "person": "John Doe",
                    "relationship": "primary account holder",
                    "date_created": "2024-01-01"
                }
            },
            session_id="setup"
        )
        
        # User books international flight
        query = "I just booked a flight to Mexico City for March 20, 2024"
        
        answer, metadata = self.answer_with_dual_context(query, mode="proactive")
        
        return {
            "scenario": "Passport Expiry Detection",
            "trigger": query,
            "response": answer,
            "metadata": metadata,
            "expected_insight": "WARNING: Passport expires March 15, before travel date"
        }
    
    def _demo_insurance_optimization(self) -> Dict[str, Any]:
        """Demonstrate insurance optimization opportunities"""
        # Set up insurance cards
        self.cards_manager.add_memory(
            content={
                "category": "finance",
                "card_key": "auto_insurance",
                "card": {
                    "facts": {
                        "provider": "State Farm",
                        "premium": "$285/month",
                        "vehicles": ["2019 Honda Civic", "2021 Toyota Camry"],
                        "renewal_date": "2024-04-01"
                    },
                    "backstory": "User reviewed insurance policies in January",
                    "person": "John Doe",
                    "relationship": "primary account holder",
                    "date_created": "2024-01-15"
                }
            },
            session_id="insurance_review"
        )
        
        query = "My insurance renewal is coming up"
        answer, metadata = self.answer_with_dual_context(query, mode="proactive")
        
        return {
            "scenario": "Insurance Optimization",
            "trigger": query,
            "response": answer,
            "metadata": metadata,
            "expected_insight": "OPPORTUNITY: Compare quotes before April renewal, potential savings identified"
        }
    
    def _demo_health_reminders(self) -> Dict[str, Any]:
        """Demonstrate health appointment coordination"""
        # Set up health cards
        self.cards_manager.add_memory(
            content={
                "category": "health",
                "card_key": "medications",
                "card": {
                    "facts": {
                        "lisinopril": "10mg daily",
                        "metformin": "500mg twice daily",
                        "last_checkup": "2023-07-15",
                        "doctor": "Dr. Smith"
                    },
                    "backstory": "User manages diabetes and blood pressure",
                    "person": "John Doe",
                    "relationship": "primary account holder",
                    "date_created": "2024-01-10"
                }
            },
            session_id="health_info"
        )
        
        query = "What health tasks do I need to handle?"
        answer, metadata = self.answer_with_dual_context(query, mode="proactive")
        
        return {
            "scenario": "Health Management",
            "trigger": query,
            "response": answer,
            "metadata": metadata,
            "expected_insight": "REMINDER: Annual checkup overdue (last: July 2023)"
        }
    
    def _demo_financial_opportunities(self) -> Dict[str, Any]:
        """Demonstrate financial optimization insights"""
        # Set up financial cards
        for category, key, card in [
            ("finance", "checking", {
                "facts": {"balance": "$5,000", "bank": "Chase"},
                "backstory": "Primary checking account",
                "person": "John Doe",
                "relationship": "primary account holder"
            }),
            ("finance", "savings", {
                "facts": {"balance": "$25,000", "rate": "0.1%", "bank": "Chase"},
                "backstory": "Emergency fund in low-yield savings",
                "person": "John Doe",
                "relationship": "primary account holder"
            })
        ]:
            self.cards_manager.add_memory(
                content={"category": category, "card_key": key, "card": card},
                session_id="finance_setup"
            )
        
        query = "How can I optimize my finances?"
        answer, metadata = self.answer_with_dual_context(query, mode="proactive")
        
        return {
            "scenario": "Financial Optimization",
            "trigger": query,
            "response": answer,
            "metadata": metadata,
            "expected_insight": "OPPORTUNITY: Move savings to high-yield account for ~4% better returns"
        }
    
    def _demo_comprehensive(self) -> Dict[str, Any]:
        """Comprehensive demonstration of all capabilities"""
        results = {
            "passport": self._demo_passport_expiry(),
            "insurance": self._demo_insurance_optimization(),
            "health": self._demo_health_reminders(),
            "finance": self._demo_financial_opportunities()
        }
        
        return {
            "demonstration": "Comprehensive Proactive Service",
            "scenarios": results,
            "summary": "Demonstrated 4 proactive service scenarios using dual-context memory"
        }
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get statistics about both memory systems"""
        return {
            "structured_memory": {
                "total_cards": sum(len(cards) for cards in self.cards_manager.categories.values()),
                "categories": list(self.cards_manager.categories.keys()),
                "cards_by_category": {
                    cat: len(cards) for cat, cards in self.cards_manager.categories.items()
                }
            },
            "conversation_memory": self.indexer.get_statistics(),
            "proactive_insights": {
                "total_generated": len(self.proactive_insights),
                "by_type": self._count_by_type(self.proactive_insights),
                "by_priority": self._count_by_priority(self.proactive_insights)
            }
        }
    
    def _count_by_type(self, insights: List[ProactiveInsight]) -> Dict[str, int]:
        """Count insights by type"""
        counts = {}
        for insight in insights:
            counts[insight.insight_type] = counts.get(insight.insight_type, 0) + 1
        return counts
    
    def _count_by_priority(self, insights: List[ProactiveInsight]) -> Dict[str, int]:
        """Count insights by priority"""
        counts = {}
        for insight in insights:
            counts[insight.priority] = counts.get(insight.priority, 0) + 1
        return counts
