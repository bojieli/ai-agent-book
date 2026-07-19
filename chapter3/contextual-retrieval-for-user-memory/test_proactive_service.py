#!/usr/bin/env python3
"""Test script to demonstrate the agent's proactive service (主动服务) capabilities"""

import logging
from datetime import datetime, timedelta
from contextual_indexer import ContextualMemoryIndexer
from contextual_agent import ContextualUserMemoryAgent
from advanced_memory_manager import AdvancedMemoryCard
from config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_proactive_service():
    """Test the agent's ability to provide proactive service"""
    
    print("\n" + "="*80)
    print("测试主动服务 (Testing Proactive Service)")
    print("="*80)
    
    # Initialize system
    config = Config.from_env()
    user_id = "proactive_test_user"
    
    indexer = ContextualMemoryIndexer(
        user_id=user_id,
        index_config=config.index,
        chunking_config=config.chunking,
        use_contextual=False
    )
    
    # Add test memory cards with potential issues
    current_date = datetime.now()
    
    # 1. Passport expiring soon
    passport_card = AdvancedMemoryCard(
        category="travel",
        card_key="passport_info",
        backstory="User mentioned passport details when booking international travel",
        date_created=current_date.strftime('%Y-%m-%d %H:%M:%S'),
        person="Jessica Thompson (primary)",
        relationship="primary account holder",
        data={
            "passport_number": "XXXXX1234",
            "expiration_date": (current_date + timedelta(days=45)).strftime('%Y-%m-%d'),
            "issuing_country": "USA"
        }
    )
    indexer.memory_manager.add_card(passport_card)
    
    # 2. Upcoming travel plan
    travel_card = AdvancedMemoryCard(
        category="travel",
        card_key="tokyo_trip_jan_2025",
        backstory="User booked a trip to Tokyo for late January",
        date_created=current_date.strftime('%Y-%m-%d %H:%M:%S'),
        person="Jessica Thompson (primary)",
        relationship="primary account holder",
        data={
            "destination": "Tokyo, Japan",
            "departure_date": (current_date + timedelta(days=30)).strftime('%Y-%m-%d'),
            "return_date": (current_date + timedelta(days=37)).strftime('%Y-%m-%d'),
            "airline": "United Airlines",
            "booking_reference": "UA1234567"
        }
    )
    indexer.memory_manager.add_card(travel_card)
    
    # 3. Medical appointment
    medical_card = AdvancedMemoryCard(
        category="medical",
        card_key="annual_checkup_2025",
        backstory="User scheduled annual physical exam",
        date_created=current_date.strftime('%Y-%m-%d %H:%M:%S'),
        person="Jessica Thompson (primary)",
        relationship="primary account holder",
        data={
            "appointment_type": "Annual Physical",
            "doctor": "Dr. Sarah Chen",
            "clinic": "Portland Medical Center",
            "date": (current_date + timedelta(days=5)).strftime('%Y-%m-%d'),
            "time": "09:00 AM",
            "fasting_required": True
        }
    )
    indexer.memory_manager.add_card(medical_card)
    
    # 4. Insurance card
    insurance_card = AdvancedMemoryCard(
        category="insurance",
        card_key="travel_insurance_2024",
        backstory="User has annual travel insurance that needs renewal",
        date_created=current_date.strftime('%Y-%m-%d %H:%M:%S'),
        person="Jessica Thompson (primary)",
        relationship="primary account holder",
        data={
            "provider": "SafeTravel Insurance",
            "policy_number": "ST-2024-789456",
            "expiration_date": (current_date + timedelta(days=20)).strftime('%Y-%m-%d'),
            "coverage": "International travel medical and trip cancellation"
        }
    )
    indexer.memory_manager.add_card(insurance_card)
    
    # Initialize agent
    agent = ContextualUserMemoryAgent(
        indexer=indexer,
        config=config
    )
    
    print("\n" + "="*80)
    print("Scenario: User asks about Tokyo trip preparation")
    print("Expected: Agent should proactively identify passport expiration risk")
    print("="*80)
    
    # Test questions that should trigger proactive service
    test_questions = [
        "我一月底的东京之行，还有什么要准备的吗？",
        "What do I need for my Tokyo trip?",
        "我下周有什么安排吗？",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {question}")
        print('='*60)
        
        trajectory = agent.answer_question(
            question=question,
            test_id=f"proactive_test_{i}",
            max_iterations=5,
            stream=False
        )
        
        print("\n📝 Agent Response:")
        print("-" * 40)
        print(trajectory.final_answer)
        print("-" * 40)
        
        # Check if agent identified key issues
        if trajectory.final_answer:
            answer_lower = trajectory.final_answer.lower()
            
            print("\n✅ Proactive Service Check:")
            
            # Check if passport expiration was mentioned
            if "passport" in answer_lower and ("expir" in answer_lower or "过期" in answer_lower):
                print("  ✓ Identified passport expiration risk")
            else:
                print("  ✗ Missed passport expiration risk")
            
            # Check if insurance was mentioned
            if "insurance" in answer_lower or "保险" in answer_lower:
                print("  ✓ Mentioned travel insurance status")
            else:
                print("  ✗ Missed insurance consideration")
            
            # Check if medical appointment was mentioned (for weekly schedule question)
            if i == 3 and ("appointment" in answer_lower or "physical" in answer_lower or "医生" in answer_lower):
                print("  ✓ Reminded about medical appointment")
            
            # Check for urgency markers
            if any(marker in trajectory.final_answer for marker in ["⚠️", "🔴", "⏰", "需要立即", "urgent", "ASAP"]):
                print("  ✓ Used urgency markers for time-sensitive items")
        
        print(f"\nMemory Cards Used: {trajectory.memory_cards_used}")
        print(f"Iterations: {len(trajectory.iterations)}")

    print("\n" + "="*80)
    print("主动服务测试完成 (Proactive Service Test Complete)")
    print("="*80)
    print("\nKey Features Demonstrated:")
    print("1. Risk Detection: Identifying passport expiration before travel")
    print("2. Comprehensive Assistance: Connecting travel with insurance needs")
    print("3. Proactive Reminders: Highlighting upcoming appointments")
    print("4. Urgency Indicators: Using markers for time-sensitive matters")

if __name__ == "__main__":
    test_proactive_service()
