"""
Local implementation of Advanced JSON Memory Manager
Simplified version that doesn't require week2 dependencies
"""

import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class AdvancedMemoryCard:
    """Represents an advanced memory card with context"""
    category: str
    card_key: str
    facts: Dict[str, Any]
    backstory: str
    person: str
    relationship: str
    date_created: str
    date_updated: str
    source: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class AdvancedJSONMemoryManager:
    """
    Simplified Advanced JSON Memory Manager
    Manages structured memory cards with backstory and relationships
    """
    
    def __init__(self, user_id: str, storage_dir: str = "memory_storage"):
        """
        Initialize memory manager
        
        Args:
            user_id: User identifier
            storage_dir: Directory for storing memories
        """
        self.user_id = user_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        self.memory_file = self.storage_dir / f"{user_id}_advanced_memory.json"
        self.categories: Dict[str, Dict[str, Any]] = {}
        
        self.load_memory()
    
    def load_memory(self):
        """Load memories from storage"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.categories = data.get('categories', {})
                logger.info(f"Loaded {self._count_cards()} memory cards for user {self.user_id}")
            except Exception as e:
                logger.error(f"Error loading memory: {e}")
                self.categories = {}
        else:
            self.categories = {}
            logger.info(f"No existing memory file for user {self.user_id}")
    
    def save_memory(self):
        """Save memories to storage"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                data = {
                    'user_id': self.user_id,
                    'type': 'advanced_json_cards',
                    'updated_at': datetime.now().isoformat(),
                    'categories': self.categories
                }
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Saved {self._count_cards()} memory cards")
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
    
    def add_memory(self, content: Dict[str, Any], session_id: str, **kwargs) -> str:
        """
        Add a new memory card
        
        Args:
            content: Dict with category, card_key, and card
            session_id: Session identifier
            
        Returns:
            Memory ID
        """
        category = content.get('category', 'general')
        card_key = content.get('card_key', str(uuid.uuid4())[:8])
        card = content.get('card', {})
        
        # Ensure category exists
        if category not in self.categories:
            self.categories[category] = {}
        
        # Add metadata
        card['_metadata'] = {
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'source': session_id
        }
        
        # Ensure required fields
        card.setdefault('backstory', '')
        card.setdefault('person', 'Unknown')
        card.setdefault('relationship', 'primary account holder')
        card.setdefault('date_created', datetime.now().strftime('%Y-%m-%d'))
        
        self.categories[category][card_key] = card
        self.save_memory()
        
        return f"{category}.{card_key}"
    
    def update_memory(self, memory_id: str, content: Dict[str, Any], session_id: str, **kwargs) -> bool:
        """
        Update an existing memory card
        
        Args:
            memory_id: Memory ID (category.card_key)
            content: New content
            session_id: Session identifier
            
        Returns:
            Success status
        """
        parts = memory_id.split('.', 1)
        if len(parts) != 2:
            return False
        
        category, card_key = parts
        
        if category not in self.categories or card_key not in self.categories[category]:
            # Create if doesn't exist
            return self.add_memory({
                'category': category,
                'card_key': card_key,
                'card': content.get('card', content)
            }, session_id) is not None
        
        # Update existing
        card = content.get('card', content)
        
        # Preserve metadata
        if '_metadata' in self.categories[category][card_key]:
            old_metadata = self.categories[category][card_key]['_metadata']
            card['_metadata'] = {
                'created_at': old_metadata.get('created_at', datetime.now().isoformat()),
                'updated_at': datetime.now().isoformat(),
                'source': session_id
            }
        
        self.categories[category][card_key] = card
        self.save_memory()
        return True
    
    def delete_memory(self, memory_id: str):
        """Delete a memory card"""
        parts = memory_id.split('.', 1)
        if len(parts) != 2:
            return
        
        category, card_key = parts
        
        if category in self.categories and card_key in self.categories[category]:
            del self.categories[category][card_key]
            
            # Clean up empty categories
            if not self.categories[category]:
                del self.categories[category]
            
            self.save_memory()
    
    def get_context_string(self) -> str:
        """Get formatted string of all memories for LLM context"""
        if not self.categories:
            return "No previous memory cards available."
        
        context = "User Memory Cards (Advanced JSON Structure):\n\n"
        
        for category, cards in self.categories.items():
            context += f"Category: {category}\n"
            for card_key, card in cards.items():
                # Remove internal metadata from display
                display_card = {k: v for k, v in card.items() if k != '_metadata'}
                context += f"  Card '{card_key}':\n"
                
                # Format card fields
                for field, value in display_card.items():
                    if isinstance(value, dict):
                        context += f"    {field}:\n"
                        for k, v in value.items():
                            context += f"      {k}: {v}\n"
                    else:
                        context += f"    {field}: {value}\n"
                context += "\n"
        
        return context
    
    def search_memories(self, query: str) -> List[Tuple[str, Any]]:
        """Search memory cards"""
        query_lower = query.lower()
        results = []
        
        for category, cards in self.categories.items():
            for card_key, card in cards.items():
                memory_id = f"{category}.{card_key}"
                
                # Search in all fields
                card_str = json.dumps(card, ensure_ascii=False).lower()
                
                if query_lower in card_str:
                    results.append((memory_id, card))
        
        return results
    
    def _count_cards(self) -> int:
        """Count total number of memory cards"""
        return sum(len(cards) for cards in self.categories.values())
