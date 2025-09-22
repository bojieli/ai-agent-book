"""
Demonstration of Advanced Memory Integration
Shows how JSON Cards + Contextual RAG enable proactive service
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import json
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "week2" / "user-memory"))

from config import Config
from advanced_memory_integration import AdvancedMemoryIntegration, ProactiveInsight

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_complex_conversation_history():
    """
    Create a rich conversation history that demonstrates the need for both
    structured memory (cards) and detailed context (chunks)
    """
    conversations = []
    
    # Conversation 1: Initial setup and preferences
    conv1 = {
        "conversation_id": "CONV-ADV-001",
        "timestamp": (datetime.now() - timedelta(days=60)).isoformat(),
        "messages": [
            {"role": "user", "content": "I need help organizing my family's information"},
            {"role": "assistant", "content": "I'll help you organize your family's information. Let's start with the basics."},
            {"role": "user", "content": "I'm John Doe, married to Jane Doe. We have two kids: Sarah (8 years old) and Mike (12 years old)"},
            {"role": "assistant", "content": "Got it. John and Jane Doe with children Sarah (8) and Mike (12). What else would you like to track?"},
            {"role": "user", "content": "My passport number is A12345678, expires March 15, 2024"},
            {"role": "assistant", "content": "Passport A12345678 expiring March 15, 2024 noted. That's coming up soon."},
            {"role": "user", "content": "Jane's passport is B98765432, expires June 2025. Kids' passports expire December 2024"},
            {"role": "assistant", "content": "All passport information recorded. Your passport expires soonest (March 2024)."},
            {"role": "user", "content": "I work at TechCorp as Senior Engineer, salary $120,000/year"},
            {"role": "assistant", "content": "Employment at TechCorp as Senior Engineer, $120,000 annual salary noted."},
            {"role": "user", "content": "Jane works part-time at DesignStudio, makes about $40,000/year"},
            {"role": "assistant", "content": "Jane's part-time work at DesignStudio, $40,000 annual income recorded."},
            {"role": "user", "content": "We have State Farm auto insurance, $285/month for both cars"},
            {"role": "assistant", "content": "State Farm auto insurance at $285/month for both vehicles noted."},
            {"role": "user", "content": "2019 Honda Civic and 2021 Toyota Camry"},
            {"role": "assistant", "content": "Vehicles: 2019 Honda Civic and 2021 Toyota Camry, both on State Farm policy."},
            {"role": "user", "content": "Home insurance with Allstate, $200/month"},
            {"role": "assistant", "content": "Allstate home insurance at $200/month recorded."},
            {"role": "user", "content": "Our mortgage is with Chase, $2,500/month, 28 years remaining"},
            {"role": "assistant", "content": "Chase mortgage: $2,500/month with 28 years remaining noted."},
            {"role": "user", "content": "Sarah has a peanut allergy, very severe"},
            {"role": "assistant", "content": "Important: Sarah has severe peanut allergy. This is critical medical information."},
            {"role": "user", "content": "Mike plays soccer, practice every Tuesday and Thursday"},
            {"role": "assistant", "content": "Mike's soccer practice schedule: Tuesdays and Thursdays recorded."},
            {"role": "user", "content": "Sarah takes piano lessons on Wednesdays"},
            {"role": "assistant", "content": "Sarah's piano lessons on Wednesdays noted."},
            {"role": "user", "content": "Our family doctor is Dr. Smith at Valley Medical, been seeing him for 5 years"},
            {"role": "assistant", "content": "Family doctor: Dr. Smith at Valley Medical (5-year relationship) recorded."},
            {"role": "user", "content": "Sarah sees Dr. Johnson (pediatric allergist) every 3 months"},
            {"role": "assistant", "content": "Sarah's allergist: Dr. Johnson, quarterly appointments noted."},
            {"role": "user", "content": "I take metformin for diabetes, 500mg twice daily"},
            {"role": "assistant", "content": "Your medication: Metformin 500mg twice daily for diabetes recorded."},
            {"role": "user", "content": "Blood pressure medicine too - lisinopril 10mg daily"},
            {"role": "assistant", "content": "Lisinopril 10mg daily for blood pressure added to your medications."}
        ]
    }
    
    # Conversation 2: Travel planning (30 days ago)
    conv2 = {
        "conversation_id": "CONV-ADV-002",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "messages": [
            {"role": "user", "content": "I'm planning a family trip to Mexico in March"},
            {"role": "assistant", "content": "A family trip to Mexico sounds great! When in March are you planning to go?"},
            {"role": "user", "content": "March 20-27, 2024. Spring break for the kids"},
            {"role": "assistant", "content": "March 20-27, 2024 during spring break. Have you started looking at flights?"},
            {"role": "user", "content": "Yes, found flights for $2,800 total on United Airlines"},
            {"role": "assistant", "content": "United Airlines flights for $2,800 total. That's $700 per person for your family of four."},
            {"role": "user", "content": "Also looking at the Hilton Cancun, it's $350/night"},
            {"role": "assistant", "content": "Hilton Cancun at $350/night for 7 nights would be $2,450 total."},
            {"role": "user", "content": "That's about $5,250 total for flights and hotel"},
            {"role": "assistant", "content": "Correct: $2,800 (flights) + $2,450 (hotel) = $5,250 total for the trip."},
            {"role": "user", "content": "I should book soon, prices might go up"},
            {"role": "assistant", "content": "Yes, booking soon is wise, especially for spring break travel."},
            {"role": "user", "content": "Do we need any special documents for Mexico?"},
            {"role": "assistant", "content": "For Mexico, US citizens need valid passports. Tourist cards are usually provided on the plane."},
            {"role": "user", "content": "Good thing we all have passports"},
            {"role": "assistant", "content": "Yes, though you should verify all passports are valid for travel dates and have 6 months validity."},
            {"role": "user", "content": "I'll check everyone's expiration dates"},
            {"role": "assistant", "content": "Good idea to check now, as passport renewals can take 6-8 weeks."},
            {"role": "user", "content": "Sarah's allergist said we should bring extra EpiPens for travel"},
            {"role": "assistant", "content": "Smart advice from Dr. Johnson. Extra EpiPens for Sarah's severe peanut allergy during travel."},
            {"role": "user", "content": "I'll pack at least 3, plus her allergy medications"},
            {"role": "assistant", "content": "Three EpiPens plus regular allergy medications - good preparation for Sarah's safety."},
            {"role": "user", "content": "Should I get travel insurance?"},
            {"role": "assistant", "content": "With a $5,250 trip and Sarah's medical condition, travel insurance would be prudent."},
            {"role": "user", "content": "My Chase Sapphire card has some travel coverage"},
            {"role": "assistant", "content": "Chase Sapphire provides trip cancellation/interruption coverage when you book with the card."},
            {"role": "user", "content": "But maybe additional medical coverage for Sarah?"},
            {"role": "assistant", "content": "Yes, supplemental medical coverage specifically for Sarah's allergy condition would be wise."},
            {"role": "user", "content": "I'll research that this week"},
            {"role": "assistant", "content": "Good plan. Look for policies that cover pre-existing conditions like allergies."}
        ]
    }
    
    # Conversation 3: Financial review (15 days ago)
    conv3 = {
        "conversation_id": "CONV-ADV-003",
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "messages": [
            {"role": "user", "content": "I want to review our finances before the trip"},
            {"role": "assistant", "content": "Good idea to review finances before a major expense. What would you like to look at?"},
            {"role": "user", "content": "We have $8,000 in checking at Chase"},
            {"role": "assistant", "content": "Chase checking: $8,000 available. The trip is $5,250, leaving $2,750 buffer."},
            {"role": "user", "content": "Emergency fund has $25,000 in savings, earning almost nothing"},
            {"role": "assistant", "content": "$25,000 emergency fund earning minimal interest. That's about 5 months of expenses."},
            {"role": "user", "content": "Maybe I should move some to a high-yield savings?"},
            {"role": "assistant", "content": "High-yield savings accounts offer 4-5% vs regular savings at 0.1%. Significant difference."},
            {"role": "user", "content": "That's like $1,000+ more per year"},
            {"role": "assistant", "content": "Exactly. $25,000 at 4.5% yields $1,125/year vs $25 at 0.1%."},
            {"role": "user", "content": "I also have $15,000 in my 401k, contributing 6% with 3% match"},
            {"role": "assistant", "content": "401k: $15,000 balance, 6% contribution with 3% employer match (50% match rate)."},
            {"role": "user", "content": "Jane has $8,000 in hers, contributes 5% with no match"},
            {"role": "assistant", "content": "Jane's 401k: $8,000, 5% contribution, no employer match unfortunately."},
            {"role": "user", "content": "Kids have 529 accounts - Sarah $5,000, Mike $7,000"},
            {"role": "assistant", "content": "College savings: Sarah's 529 has $5,000 (10 years to college), Mike's has $7,000 (6 years to college)."},
            {"role": "user", "content": "We add $200/month to each 529"},
            {"role": "assistant", "content": "$200/month per child for college savings, $400/month total to 529 plans."},
            {"role": "user", "content": "Our monthly expenses are about $5,000 all-in"},
            {"role": "assistant", "content": "Monthly expenses: $5,000 total. Your emergency fund covers 5 months, which is good."},
            {"role": "user", "content": "That includes mortgage, insurance, utilities, food, everything"},
            {"role": "assistant", "content": "Comprehensive $5,000/month including mortgage ($2,500), insurance ($485), and living expenses."},
            {"role": "user", "content": "Combined income is $160,000, so we save about $3,000/month after taxes"},
            {"role": "assistant", "content": "Combined $160,000 income, ~$3,000/month savings after taxes and expenses. Strong savings rate."},
            {"role": "user", "content": "The Mexico trip will use about 2 months of savings"},
            {"role": "assistant", "content": "Yes, the $5,250 trip equals about 1.75 months of your $3,000/month savings."},
            {"role": "user", "content": "Worth it for family memories though"},
            {"role": "assistant", "content": "Absolutely. Family experiences and memories, especially with kids at 8 and 12, are invaluable."},
            {"role": "user", "content": "Insurance renewal is in April too, right after the trip"},
            {"role": "assistant", "content": "Auto insurance renewal in April, right after your March trip. Good time to shop for better rates."},
            {"role": "user", "content": "Maybe I should get quotes before renewal"},
            {"role": "assistant", "content": "Yes, get quotes in early March. With your clean record, you might find better than $285/month."}
        ]
    }
    
    # Conversation 4: Recent health update (7 days ago)
    conv4 = {
        "conversation_id": "CONV-ADV-004",
        "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
        "messages": [
            {"role": "user", "content": "Just had my annual checkup with Dr. Smith"},
            {"role": "assistant", "content": "How did your annual checkup go? Any updates from Dr. Smith?"},
            {"role": "user", "content": "Blood pressure is better controlled now, 125/80"},
            {"role": "assistant", "content": "125/80 is good blood pressure control. The lisinopril is working well."},
            {"role": "user", "content": "A1C is 6.8%, down from 7.2% last year"},
            {"role": "assistant", "content": "A1C of 6.8% is excellent improvement from 7.2%. Good diabetes management."},
            {"role": "user", "content": "He wants me to get blood work again in 3 months"},
            {"role": "assistant", "content": "Follow-up blood work in 3 months to monitor A1C and overall health."},
            {"role": "user", "content": "Also suggested I lose 10 pounds before the trip"},
            {"role": "assistant", "content": "10 pounds in about 6 weeks before March 20 trip - achievable with focus."},
            {"role": "user", "content": "Sarah's allergist appointment is next week"},
            {"role": "assistant", "content": "Sarah's quarterly appointment with Dr. Johnson coming up. Good timing before Mexico trip."},
            {"role": "user", "content": "Need to discuss travel precautions for her allergy"},
            {"role": "assistant", "content": "Important to review Mexico travel safety for Sarah's severe peanut allergy with Dr. Johnson."},
            {"role": "user", "content": "Mike needs a sports physical for next soccer season"},
            {"role": "assistant", "content": "Mike's sports physical needed for soccer. Can Dr. Smith handle that?"},
            {"role": "user", "content": "Yes, scheduled him for next month"},
            {"role": "assistant", "content": "Good planning - Mike's sports physical scheduled for next month before new season."},
            {"role": "user", "content": "Jane hasn't had a checkup in 2 years"},
            {"role": "assistant", "content": "Jane overdue for checkup (2 years). Should schedule soon for preventive care."},
            {"role": "user", "content": "She's been putting it off, always busy with work"},
            {"role": "assistant", "content": "Common challenge with part-time work and family. But preventive care is important."},
            {"role": "user", "content": "I'll encourage her to schedule this month"},
            {"role": "assistant", "content": "Good idea. Maybe she can schedule while booking Sarah's appointments."},
            {"role": "user", "content": "Our FSA has $1,200 left to use this year"},
            {"role": "assistant", "content": "FSA with $1,200 remaining. Use-it-or-lose-it, so plan medical expenses wisely."},
            {"role": "user", "content": "Maybe new glasses for everyone?"},
            {"role": "assistant", "content": "Glasses for family of four could easily use the $1,200 FSA balance."},
            {"role": "user", "content": "Or stock up on Sarah's EpiPens"},
            {"role": "assistant", "content": "EpiPens are FSA-eligible. Stocking up before Mexico trip makes sense."},
            {"role": "user", "content": "Each 2-pack costs about $300 with our insurance"},
            {"role": "assistant", "content": "At $300 per 2-pack, you could get 4 packs (8 EpiPens) with FSA funds."},
            {"role": "user", "content": "That would last us the whole year"},
            {"role": "assistant", "content": "Yes, 8 EpiPens would provide good supply for home, school, travel, and emergencies."}
        ]
    }
    
    return [conv1, conv2, conv3, conv4]


def demonstrate_dual_context_system():
    """
    Demonstrate how Advanced JSON Cards + Contextual RAG work together
    """
    logger.info("="*80)
    logger.info("ADVANCED MEMORY INTEGRATION DEMONSTRATION")
    logger.info("Combining Structured Memory Cards with Contextual Retrieval")
    logger.info("="*80)
    
    # Initialize system
    config = Config.from_env()
    config.verbose = True
    
    # Create unique user for demo
    demo_user = f"advanced_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize advanced memory integration
    memory_system = AdvancedMemoryIntegration(demo_user, config)
    
    # Phase 1: Learning - Process conversation histories
    logger.info("\n" + "="*60)
    logger.info("PHASE 1: LEARNING FROM CONVERSATIONS")
    logger.info("="*60)
    
    conversations = create_complex_conversation_history()
    
    for i, conv in enumerate(conversations, 1):
        logger.info(f"\nProcessing Conversation {i}: {conv['conversation_id']}")
        results = memory_system.process_conversation(conv, generate_cards=True)
        
        logger.info(f"  - Created {len(results['chunks_created'])} contextual chunks")
        logger.info(f"  - Updated {len(results['cards_updated'])} memory cards")
        logger.info(f"  - Generated {len(results['insights_generated'])} proactive insights")
    
    # Show memory statistics
    stats = memory_system.get_memory_statistics()
    logger.info("\n" + "-"*60)
    logger.info("MEMORY SYSTEM STATE:")
    logger.info(f"  Structured Memory Cards: {stats['structured_memory']['total_cards']}")
    logger.info(f"  Categories: {', '.join(stats['structured_memory']['categories'])}")
    logger.info(f"  Conversation Chunks: {stats['conversation_memory']['total_chunks']}")
    logger.info(f"  Proactive Insights: {stats['proactive_insights']['total_generated']}")
    
    # Phase 2: Demonstrate Proactive Service
    logger.info("\n" + "="*60)
    logger.info("PHASE 2: PROACTIVE SERVICE DEMONSTRATIONS")
    logger.info("="*60)
    
    # Test Case 1: Passport Expiry Warning
    logger.info("\n--- Test 1: Passport Expiry Detection ---")
    query1 = "I'm excited about our Mexico trip next month!"
    
    answer1, metadata1 = memory_system.answer_with_dual_context(query1, mode="proactive")
    
    logger.info(f"User: {query1}")
    logger.info(f"\nAgent Response (Proactive Mode):")
    logger.info(f"{answer1}")
    logger.info(f"\nMetadata: Cards used: {metadata1['cards_used']}, "
               f"Chunks retrieved: {metadata1['chunks_retrieved']}, "
               f"Insights provided: {metadata1['insights_provided']}")
    
    # Test Case 2: Financial Optimization
    logger.info("\n--- Test 2: Financial Optimization Opportunity ---")
    query2 = "Should I move money from savings before the trip?"
    
    answer2, metadata2 = memory_system.answer_with_dual_context(query2, mode="proactive")
    
    logger.info(f"User: {query2}")
    logger.info(f"\nAgent Response (Proactive Mode):")
    logger.info(f"{answer2}")
    
    # Test Case 3: Health Coordination
    logger.info("\n--- Test 3: Family Health Coordination ---")
    query3 = "What medical preparations do we need for the trip?"
    
    answer3, metadata3 = memory_system.answer_with_dual_context(query3, mode="proactive")
    
    logger.info(f"User: {query3}")
    logger.info(f"\nAgent Response (Proactive Mode):")
    logger.info(f"{answer3}")
    
    # Phase 3: Compare Proactive vs Reactive Modes
    logger.info("\n" + "="*60)
    logger.info("PHASE 3: PROACTIVE VS REACTIVE COMPARISON")
    logger.info("="*60)
    
    comparison_query = "What should I do this week to prepare for our trip?"
    
    # Reactive mode (just answers the question)
    logger.info("\n--- REACTIVE MODE (Traditional) ---")
    reactive_answer, reactive_meta = memory_system.answer_with_dual_context(
        comparison_query, mode="reactive"
    )
    logger.info(f"User: {comparison_query}")
    logger.info(f"\nAgent Response (Reactive):")
    logger.info(f"{reactive_answer}")
    
    # Proactive mode (provides insights and warnings)
    logger.info("\n--- PROACTIVE MODE (Advanced) ---")
    proactive_answer, proactive_meta = memory_system.answer_with_dual_context(
        comparison_query, mode="proactive"
    )
    logger.info(f"User: {comparison_query}")
    logger.info(f"\nAgent Response (Proactive):")
    logger.info(f"{proactive_answer}")
    
    # Phase 4: Demonstrate Complex Multi-Entity Understanding
    logger.info("\n" + "="*60)
    logger.info("PHASE 4: MULTI-ENTITY RELATIONSHIP UNDERSTANDING")
    logger.info("="*60)
    
    complex_query = "What are all the important dates and deadlines for my family in the next 3 months?"
    
    complex_answer, complex_meta = memory_system.answer_with_dual_context(
        complex_query, mode="proactive"
    )
    
    logger.info(f"User: {complex_query}")
    logger.info(f"\nAgent Response (Demonstrates understanding of multiple family members):")
    logger.info(f"{complex_answer}")
    
    # Phase 5: Show Memory Card Structure
    logger.info("\n" + "="*60)
    logger.info("PHASE 5: STRUCTURED MEMORY CARDS (Always in Context)")
    logger.info("="*60)
    
    memory_context = memory_system.cards_manager.get_context_string()
    logger.info("Sample Memory Cards Structure:")
    # Show first 1500 chars of memory cards
    logger.info(memory_context[:1500] + "..." if len(memory_context) > 1500 else memory_context)
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DEMONSTRATION SUMMARY")
    logger.info("="*80)
    logger.info("""
Key Insights from Dual-Context System:

1. STRUCTURED MEMORY (JSON Cards):
   - Always in context, no retrieval needed
   - Captures key facts, relationships, and metadata
   - Enables understanding of "who", "what", "why"
   
2. CONTEXTUAL RETRIEVAL (RAG):
   - Dynamically retrieves conversation details
   - Provides specific context and nuance
   - Enables understanding of "how" and "when"

3. PROACTIVE SERVICE:
   - Passport expiry detected before travel
   - Financial optimization opportunities identified
   - Health preparations coordinated across family
   - FSA deadline and usage recommendations
   
4. ADVANTAGES OVER SINGLE-SYSTEM:
   - Cards provide instant access to key facts
   - RAG provides detailed context when needed
   - Together enable true proactive assistance
   - Reduces both false positives and false negatives

This dual-context approach represents the future of AI assistants:
Not just answering questions, but actively helping users succeed.
    """)


def run_targeted_scenario(scenario: str):
    """Run a specific demonstration scenario"""
    
    config = Config.from_env()
    demo_user = f"scenario_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    memory_system = AdvancedMemoryIntegration(demo_user, config)
    
    logger.info(f"\n{'='*60}")
    logger.info(f"SCENARIO: {scenario.upper()}")
    logger.info(f"{'='*60}")
    
    result = memory_system.demonstrate_proactive_service(scenario)
    
    logger.info(f"\nScenario: {result.get('scenario', scenario)}")
    logger.info(f"Trigger: {result.get('trigger', 'N/A')}")
    logger.info(f"\nResponse:")
    logger.info(result.get('response', 'No response generated'))
    logger.info(f"\nExpected Insight: {result.get('expected_insight', 'N/A')}")
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--scenario":
        # Run specific scenario
        scenario = sys.argv[2] if len(sys.argv) > 2 else "passport_expiry"
        run_targeted_scenario(scenario)
    else:
        # Run full demonstration
        demonstrate_dual_context_system()
