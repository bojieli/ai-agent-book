"""Advanced Memory Manager with JSON Cards for User Memory System

This module implements the Advanced JSON Cards approach from week2/user-memory,
which stores structured, summarized core facts about users.
"""

import json
import os
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class AdvancedMemoryCard:
    """
    Represents an advanced memory card with complete metadata.
    
    Each card MUST include:
    - backstory: Context about when/why this information was learned
    - date_created: Timestamp when created
    - person: Who this relates to
    - relationship: Role/relationship to primary user
    - Additional fields based on information type
    """
    category: str
    card_key: str
    backstory: str
    date_created: str
    person: str
    relationship: str
    data: Dict[str, Any] = field(default_factory=dict)
    _metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        result = {
            "backstory": self.backstory,
            "date_created": self.date_created,
            "person": self.person,
            "relationship": self.relationship,
            **self.data
        }
        if self._metadata:
            result["_metadata"] = self._metadata
        return result
    
    @classmethod
    def from_dict(cls, category: str, card_key: str, data: Dict[str, Any]) -> 'AdvancedMemoryCard':
        """Create from dictionary"""
        metadata = data.pop("_metadata", {})
        return cls(
            category=category,
            card_key=card_key,
            backstory=data.get("backstory", ""),
            date_created=data.get("date_created", ""),
            person=data.get("person", ""),
            relationship=data.get("relationship", ""),
            data={k: v for k, v in data.items() 
                  if k not in ["backstory", "date_created", "person", "relationship"]},
            _metadata=metadata
        )


class AdvancedMemoryManager:
    """
    Advanced JSON Memory Manager for structured user information.
    
    This manager handles the persistent, structured memory that stays
    in the agent's context at all times (the "备忘录" or memo).
    """
    
    def __init__(self, user_id: str, storage_dir: str = "memory_storage"):
        """
        Initialize the advanced memory manager.
        
        Args:
            user_id: Unique user identifier
            storage_dir: Directory for storing memory files
        """
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.storage_dir / f"{user_id}_advanced_memory.json"
        self.categories: Dict[str, Dict[str, AdvancedMemoryCard]] = {}
        
        self.load_memory()
        logger.info(f"Initialized AdvancedMemoryManager for user {user_id}")
    
    def load_memory(self):
        """Load memory cards from storage"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Load categories and cards
                    for category, cards in data.get('categories', {}).items():
                        self.categories[category] = {}
                        for card_key, card_data in cards.items():
                            self.categories[category][card_key] = AdvancedMemoryCard.from_dict(
                                category, card_key, card_data
                            )
                    
                    logger.info(f"Loaded {sum(len(cards) for cards in self.categories.values())} memory cards")
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                self.categories = {}
        else:
            logger.info(f"No existing memory file for user {self.user_id}")
    
    def save_memory(self):
        """Save memory cards to storage"""
        try:
            data = {
                'user_id': self.user_id,
                'type': 'advanced_json_cards',
                'updated_at': datetime.now().isoformat(),
                'categories': {}
            }
            
            # Convert cards to dict format
            for category, cards in self.categories.items():
                data['categories'][category] = {}
                for card_key, card in cards.items():
                    data['categories'][category][card_key] = card.to_dict()
            
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved {sum(len(cards) for cards in self.categories.values())} memory cards")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_card(self, card: AdvancedMemoryCard) -> str:
        """
        Add a new memory card.
        
        Args:
            card: The memory card to add
            
        Returns:
            Memory ID in format category.card_key
        """
        if card.category not in self.categories:
            self.categories[card.category] = {}
        
        # Add metadata
        card._metadata = {
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        # Ensure required fields
        if not card.backstory:
            logger.warning("Memory card missing backstory")
        if not card.date_created:
            card.date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if not card.person:
            card.person = "Primary User"
        if not card.relationship:
            card.relationship = "primary account holder"
        
        self.categories[card.category][card.card_key] = card
        self.save_memory()
        
        memory_id = f"{card.category}.{card.card_key}"
        logger.info(f"Added memory card: {memory_id}")
        return memory_id
    
    def update_card(self, category: str, card_key: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing memory card.
        
        Args:
            category: Card category
            card_key: Card key
            updates: Fields to update
            
        Returns:
            True if successful
        """
        if category not in self.categories or card_key not in self.categories[category]:
            logger.warning(f"Card not found: {category}.{card_key}")
            return False
        
        card = self.categories[category][card_key]
        
        # Update fields
        for key, value in updates.items():
            if key in ["backstory", "date_created", "person", "relationship"]:
                setattr(card, key, value)
            elif key != "_metadata":
                card.data[key] = value
        
        # Update metadata
        if card._metadata:
            card._metadata['updated_at'] = datetime.now().isoformat()
        
        self.save_memory()
        logger.info(f"Updated memory card: {category}.{card_key}")
        return True
    
    def delete_card(self, category: str, card_key: str) -> bool:
        """
        Delete a memory card.
        
        Args:
            category: Card category
            card_key: Card key
            
        Returns:
            True if successful
        """
        if category in self.categories and card_key in self.categories[category]:
            del self.categories[category][card_key]
            
            # Clean up empty categories
            if not self.categories[category]:
                del self.categories[category]
            
            self.save_memory()
            logger.info(f"Deleted memory card: {category}.{card_key}")
            return True
        
        logger.warning(f"Card not found for deletion: {category}.{card_key}")
        return False
    
    def get_card(self, category: str, card_key: str) -> Optional[AdvancedMemoryCard]:
        """Get a specific memory card"""
        if category in self.categories and card_key in self.categories[category]:
            return self.categories[category][card_key]
        return None
    
    def search_cards(self, query: str) -> List[Tuple[str, AdvancedMemoryCard]]:
        """
        Search memory cards by query.
        
        Args:
            query: Search query
            
        Returns:
            List of (memory_id, card) tuples
        """
        query_lower = query.lower()
        results = []
        
        for category, cards in self.categories.items():
            for card_key, card in cards.items():
                memory_id = f"{category}.{card_key}"
                
                # Search in all card fields
                card_str = json.dumps(card.to_dict(), ensure_ascii=False).lower()
                
                if (query_lower in category.lower() or
                    query_lower in card_key.lower() or
                    query_lower in card_str):
                    
                    results.append((memory_id, card))
        
        return results
    
    def get_context_string(self, max_cards: Optional[int] = None) -> str:
        """
        Get memory cards as formatted string for LLM context.
        
        Args:
            max_cards: Maximum number of cards to include (None for all)
            
        Returns:
            Formatted string of memory cards
        """
        if not self.categories:
            return "No advanced memory cards available."
        
        lines = ["=== ADVANCED USER MEMORY CARDS ===\n"]
        
        card_count = 0
        for category, cards in self.categories.items():
            lines.append(f"\n[Category: {category}]")
            
            for card_key, card in cards.items():
                if max_cards and card_count >= max_cards:
                    remaining = sum(len(c) for c in self.categories.values()) - card_count
                    lines.append(f"\n... and {remaining} more memory cards")
                    break
                
                lines.append(f"\n  Card '{card_key}':")
                
                # Format card data nicely
                card_dict = card.to_dict()
                # Remove internal metadata from display
                card_dict.pop('_metadata', None)
                
                # Display key fields first
                lines.append(f"    - Backstory: {card.backstory}")
                lines.append(f"    - Person: {card.person}")
                lines.append(f"    - Relationship: {card.relationship}")
                lines.append(f"    - Date Created: {card.date_created}")
                
                # Display other data fields
                for key, value in card.data.items():
                    if isinstance(value, dict):
                        lines.append(f"    - {key}:")
                        for k, v in value.items():
                            lines.append(f"        {k}: {v}")
                    elif isinstance(value, list):
                        lines.append(f"    - {key}: {', '.join(str(v) for v in value)}")
                    else:
                        lines.append(f"    - {key}: {value}")
                
                card_count += 1
            
            if max_cards and card_count >= max_cards:
                break
        
        lines.append(f"\n\n[Total Memory Cards: {sum(len(cards) for cards in self.categories.values())}]")
        
        return "\n".join(lines)
    
    def summarize_for_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Summarize memory cards for a specific conversation.
        
        This creates a conversation-specific summary of relevant memory cards
        that can be stored alongside the conversation chunks.
        
        Args:
            conversation_id: The conversation identifier
            
        Returns:
            Summary dictionary
        """
        summary = {
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat(),
            "total_cards": sum(len(cards) for cards in self.categories.values()),
            "categories": {}
        }
        
        # Summarize by category
        for category, cards in self.categories.items():
            if cards:
                summary["categories"][category] = {
                    "count": len(cards),
                    "keys": list(cards.keys()),
                    "sample": {}
                }
                
                # Include first 2 cards as samples
                for i, (card_key, card) in enumerate(cards.items()):
                    if i >= 2:
                        break
                    summary["categories"][category]["sample"][card_key] = {
                        "person": card.person,
                        "backstory": card.backstory[:100] + "..." if len(card.backstory) > 100 else card.backstory
                    }
        
        return summary
    
    def clear_all_memories(self):
        """Clear all memory cards"""
        self.categories = {}
        self.save_memory()
        logger.info(f"Cleared all memory cards for user {self.user_id}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        stats = {
            "user_id": self.user_id,
            "total_cards": sum(len(cards) for cards in self.categories.values()),
            "categories": {}
        }
        
        for category, cards in self.categories.items():
            stats["categories"][category] = {
                "count": len(cards),
                "cards": list(cards.keys())
            }
        
        # Calculate average backstory length
        all_backstories = []
        for cards in self.categories.values():
            for card in cards.values():
                if card.backstory:
                    all_backstories.append(len(card.backstory))
        
        if all_backstories:
            stats["avg_backstory_length"] = sum(all_backstories) / len(all_backstories)
        else:
            stats["avg_backstory_length"] = 0
        
        return stats


def create_sample_cards() -> List[AdvancedMemoryCard]:
    """Create sample memory cards for testing"""
    cards = [
        AdvancedMemoryCard(
            category="financial",
            card_key="bank_account_primary",
            backstory="User shared their banking details while setting up automatic bill payments",
            date_created="2024-01-15 10:30:00",
            person="John Smith (primary)",
            relationship="primary account holder",
            data={
                "bank_name": "Chase Bank",
                "account_type": "checking",
                "account_ending": "4567",
                "routing_number": "021000021",
                "purpose": "primary checking for bills"
            }
        ),
        AdvancedMemoryCard(
            category="medical",
            card_key="doctor_dermatologist_sarah",
            backstory="User needed to schedule a dermatology appointment for their daughter's skin condition",
            date_created="2024-01-16 14:00:00",
            person="Sarah Smith (daughter)",
            relationship="family member",
            data={
                "doctor_name": "Dr. Emily Johnson",
                "specialty": "Pediatric Dermatology",
                "clinic": "Children's Health Center",
                "phone": "555-0123",
                "condition_treated": "eczema"
            }
        ),
        AdvancedMemoryCard(
            category="travel",
            card_key="passport_jessica",
            backstory="User mentioned passport expiration while planning international travel",
            date_created="2024-12-20 09:00:00",
            person="Jessica Thompson (primary)",
            relationship="primary account holder",
            data={
                "passport_number": "XXXXX1234",
                "expiration_date": "2025-02-18",
                "issuing_country": "USA",
                "needs_renewal": True
            }
        ),
        AdvancedMemoryCard(
            category="travel",
            card_key="tokyo_trip_january",
            backstory="User booked a trip to Tokyo for a business conference",
            date_created="2024-12-22 11:00:00",
            person="Jessica Thompson (primary)",
            relationship="primary account holder",
            data={
                "destination": "Tokyo, Japan",
                "departure_date": "2025-01-25",
                "return_date": "2025-02-01",
                "purpose": "business conference",
                "hotel": "Hilton Tokyo",
                "flight": "UA837"
            }
        )
    ]
    
    return cards
