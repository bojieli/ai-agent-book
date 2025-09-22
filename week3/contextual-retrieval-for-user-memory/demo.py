"""
Quick demonstration of Contextual Retrieval for User Memory
Shows the dramatic improvement in retrieval accuracy with context
"""

import logging
from datetime import datetime, timedelta
from pathlib import Path
import json

from config import Config, RetrievalMode
from memory_indexer import ContextualMemoryIndexer
from agentic_memory_agent import AgenticMemoryAgent
from evaluation import TestCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_demo_conversations():
    """Create sample conversation histories for demonstration"""
    
    # Conversation 1: Insurance discussion
    conv1 = {
        "conversation_id": "CONV-001",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "messages": [
            {"role": "user", "content": "I need to review my insurance policies"},
            {"role": "assistant", "content": "I'll help you review your insurance policies. What types of insurance do you currently have?"},
            {"role": "user", "content": "I have auto insurance with State Farm, policy number SF-AUTO-123456"},
            {"role": "assistant", "content": "Got it. State Farm auto insurance, policy SF-AUTO-123456. What else?"},
            {"role": "user", "content": "Home insurance with Allstate, policy AL-HOME-789012"},
            {"role": "assistant", "content": "Noted. Allstate home insurance, policy AL-HOME-789012. Any other policies?"},
            {"role": "user", "content": "Yes, life insurance with MetLife, policy ML-LIFE-345678, coverage amount $500,000"},
            {"role": "assistant", "content": "I've recorded all three policies. Would you like to review coverage details or premiums?"},
            {"role": "user", "content": "Let's review premiums. Auto is $150/month, home is $200/month, life is $75/month"},
            {"role": "assistant", "content": "Total monthly insurance cost: $425. Would you like suggestions for optimization?"},
            {"role": "user", "content": "Yes, I think the auto insurance might be too high"},
            {"role": "assistant", "content": "For your auto insurance, you might consider: 1) Increasing deductibles, 2) Bundling with home insurance, 3) Shopping for quotes. Your State Farm policy might have bundle discounts available."},
            {"role": "user", "content": "Good idea. Also, my home insurance deductible is currently $1,000"},
            {"role": "assistant", "content": "A $1,000 deductible is fairly standard. Increasing it to $2,500 could reduce your premium by 10-15%."},
            {"role": "user", "content": "I'll consider that. My auto deductible is $500 for collision and $250 for comprehensive"},
            {"role": "assistant", "content": "Those are relatively low deductibles. Raising them to $1,000/$500 could save you significantly on premiums."},
            {"role": "user", "content": "What about my life insurance? Is $500k enough coverage?"},
            {"role": "assistant", "content": "The rule of thumb is 10x annual income. Is $500k approximately 10 times your annual income?"},
            {"role": "user", "content": "My annual income is $80,000, so I might need more coverage"},
            {"role": "assistant", "content": "Based on your $80,000 income, $800,000 coverage would be more appropriate. Consider getting quotes for additional term life insurance."},
            {"role": "user", "content": "I'll look into that. Can you remind me of all my policy renewal dates?"},
            {"role": "assistant", "content": "I'll need that information from you. When do each of your policies renew?"},
            {"role": "user", "content": "Auto renews in March, home in June, life insurance in September"},
            {"role": "assistant", "content": "Perfect. Auto (March), Home (June), Life (September). I'd recommend starting to shop for quotes 30-60 days before each renewal date."}
        ]
    }
    
    # Conversation 2: Vehicle registrations
    conv2 = {
        "conversation_id": "CONV-002", 
        "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
        "messages": [
            {"role": "user", "content": "I need help keeping track of my vehicle registrations"},
            {"role": "assistant", "content": "I'll help you track your vehicle registrations. How many vehicles do you have?"},
            {"role": "user", "content": "I have three vehicles: 2019 Honda Civic, 2021 Toyota Camry, and 2018 Ford F-150"},
            {"role": "assistant", "content": "Three vehicles noted. Let me get the registration details for each. Starting with the 2019 Honda Civic?"},
            {"role": "user", "content": "The Civic's plate is ABC-1234, registration expires April 2024, VIN ends in 5678"},
            {"role": "assistant", "content": "Honda Civic recorded. What about the 2021 Toyota Camry?"},
            {"role": "user", "content": "Camry has plate XYZ-9876, expires August 2024, VIN ends in 4321"},
            {"role": "assistant", "content": "Toyota Camry recorded. And the 2018 Ford F-150?"},
            {"role": "user", "content": "F-150 plate is TRK-5555, expires December 2023 - that's coming up soon!"},
            {"role": "assistant", "content": "The F-150 registration expires next month! You should renew it soon. What's the VIN?"},
            {"role": "user", "content": "VIN ends in 9999. Also, I should mention the F-150 needs an emissions test"},
            {"role": "assistant", "content": "Important note: F-150 needs emissions test before registration renewal. Schedule that ASAP since it expires in December 2023."},
            {"role": "user", "content": "What are the registration fees typically?"},
            {"role": "assistant", "content": "Registration fees vary by state and vehicle. What state are you in?"},
            {"role": "user", "content": "I'm in California. The Civic was $196 last year"},
            {"role": "assistant", "content": "In California, expect similar fees: around $196 for the Civic, potentially more for the newer Camry and the F-150 truck."},
            {"role": "user", "content": "The Camry was actually $215 and the F-150 was $320 due to weight"},
            {"role": "assistant", "content": "California fees noted: Civic $196, Camry $215, F-150 $320. Total annual registration cost: $731."},
            {"role": "user", "content": "I also need to update my address on all registrations. I moved to 123 Main St, San Jose, CA 95110"},
            {"role": "assistant", "content": "New address: 123 Main St, San Jose, CA 95110. You'll need to update this with the DMV within 10 days of moving."},
            {"role": "user", "content": "Do I need to update insurance too?"},
            {"role": "assistant", "content": "Yes, definitely update your auto insurance with State Farm (policy SF-AUTO-123456) with your new San Jose address."},
            {"role": "user", "content": "Good point. The Honda and Toyota are on that policy. The F-150 is on a separate commercial policy"},
            {"role": "assistant", "content": "So State Farm covers the Civic and Camry, while the F-150 has separate commercial coverage. Update addresses for both policies."}
        ]
    }
    
    # Conversation 3: Medical appointments and medications
    conv3 = {
        "conversation_id": "CONV-003",
        "timestamp": (datetime.now() - timedelta(days=7)).isoformat(),
        "messages": [
            {"role": "user", "content": "I need to organize my medical information and appointments"},
            {"role": "assistant", "content": "I'll help you organize your medical information. Let's start with your doctors and upcoming appointments."},
            {"role": "user", "content": "My primary care doctor is Dr. Smith at Valley Medical Center"},
            {"role": "assistant", "content": "Dr. Smith at Valley Medical Center noted as your primary care physician. Do you have any upcoming appointments?"},
            {"role": "user", "content": "Yes, annual physical on January 15, 2024 at 10:00 AM"},
            {"role": "assistant", "content": "Annual physical with Dr. Smith scheduled for January 15, 2024 at 10:00 AM. Any other specialists?"},
            {"role": "user", "content": "I see Dr. Johnson, cardiologist, every 6 months. Next appointment February 28, 2024"},
            {"role": "assistant", "content": "Dr. Johnson (cardiologist) appointment on February 28, 2024. How about medications?"},
            {"role": "user", "content": "I take lisinopril 10mg daily for blood pressure"},
            {"role": "assistant", "content": "Lisinopril 10mg daily for blood pressure noted. Any other medications?"},
            {"role": "user", "content": "Metformin 500mg twice daily for diabetes, and atorvastatin 20mg at night for cholesterol"},
            {"role": "assistant", "content": "Three medications recorded: Lisinopril 10mg daily, Metformin 500mg twice daily, Atorvastatin 20mg nightly."},
            {"role": "user", "content": "My pharmacy is CVS on First Street, pharmacy phone is 408-555-0100"},
            {"role": "assistant", "content": "CVS on First Street (408-555-0100) noted as your pharmacy. Do you have automatic refills set up?"},
            {"role": "user", "content": "Yes for all three medications. They usually refill around the 25th of each month"},
            {"role": "assistant", "content": "Auto-refills around the 25th monthly for all three medications. Any allergies I should note?"},
            {"role": "user", "content": "I'm allergic to penicillin and sulfa drugs"},
            {"role": "assistant", "content": "Important: Allergies to penicillin and sulfa drugs noted. This is critical information for any medical visits."},
            {"role": "user", "content": "Also, my blood pressure has been averaging 125/80 lately"},
            {"role": "assistant", "content": "Blood pressure averaging 125/80 - that's within acceptable range but something to monitor with Dr. Johnson."},
            {"role": "user", "content": "My last A1C was 6.8% and cholesterol was 185"},
            {"role": "assistant", "content": "A1C at 6.8% (good control for diabetes) and cholesterol at 185 (borderline high). Both worth discussing at upcoming appointments."}
        ]
    }
    
    return [conv1, conv2, conv3]


def run_demo():
    """Run the demonstration"""
    logger.info("="*80)
    logger.info("CONTEXTUAL RETRIEVAL FOR USER MEMORY - DEMONSTRATION")
    logger.info("="*80)
    logger.info("\nThis demo shows how contextual retrieval dramatically improves memory search")
    logger.info("by adding context to conversation chunks before indexing.\n")
    
    # Create config
    config = Config.from_env()
    config.verbose = True
    
    # Create demo conversations
    conversations = create_demo_conversations()
    logger.info(f"Created {len(conversations)} demo conversations:")
    logger.info("  1. Insurance policies discussion (30 days ago)")
    logger.info("  2. Vehicle registrations (15 days ago)")
    logger.info("  3. Medical information (7 days ago)")
    
    # Demo user ID
    demo_user = "demo_user_" + datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Phase 1: Index with contextual retrieval
    logger.info("\n" + "="*80)
    logger.info("PHASE 1: INDEXING WITH CONTEXTUAL RETRIEVAL")
    logger.info("="*80)
    
    # Create contextual indexer
    contextual_indexer = ContextualMemoryIndexer(
        user_id=demo_user,
        config=config,
        enable_contextual=True
    )
    
    # Index conversations
    total_chunks = 0
    for conv in conversations:
        logger.info(f"\nIndexing {conv['conversation_id']}...")
        chunks = contextual_indexer.index_conversation(conv, show_progress=False)
        total_chunks += len(chunks)
        logger.info(f"  Created {len(chunks)} chunks with contextual descriptions")
    
    logger.info(f"\nTotal chunks indexed: {total_chunks}")
    
    # Show example of contextual enhancement
    if contextual_indexer.chunks:
        example_chunk = contextual_indexer.chunks[0]
        logger.info("\n" + "-"*60)
        logger.info("EXAMPLE OF CONTEXTUAL ENHANCEMENT:")
        logger.info("-"*60)
        logger.info(f"\nOriginal chunk (first 200 chars):")
        logger.info(f"  {example_chunk.original_text[:200]}...")
        if example_chunk.context_description:
            logger.info(f"\nGenerated context:")
            logger.info(f"  {example_chunk.context_description}")
    
    # Phase 2: Create agents for comparison
    logger.info("\n" + "="*80)
    logger.info("PHASE 2: COMPARING RETRIEVAL MODES")
    logger.info("="*80)
    
    # Create agent with contextual retrieval
    contextual_agent = AgenticMemoryAgent(
        user_id=demo_user,
        config=config,
        indexer=contextual_indexer,
        mode=RetrievalMode.CONTEXTUAL
    )
    
    # Create non-contextual indexer with same data
    non_contextual_indexer = ContextualMemoryIndexer(
        user_id=demo_user + "_non_contextual",
        config=config,
        enable_contextual=False
    )
    
    # Index same conversations without context
    for conv in conversations:
        non_contextual_indexer.index_conversation(conv, show_progress=False)
    
    # Create agent without contextual retrieval
    non_contextual_agent = AgenticMemoryAgent(
        user_id=demo_user,
        config=config,
        indexer=non_contextual_indexer,
        mode=RetrievalMode.NON_CONTEXTUAL
    )
    
    # Phase 3: Test queries
    logger.info("\n" + "="*80)
    logger.info("PHASE 3: TESTING RETRIEVAL ACCURACY")
    logger.info("="*80)
    
    test_queries = [
        "What are all my insurance policy numbers and their monthly premiums?",
        "Which of my vehicles needs registration renewal soon and what's required?",
        "What medications do I take and what are my drug allergies?",
        "When is my next appointment with Dr. Johnson and what should I discuss?"
    ]
    
    for query_num, query in enumerate(test_queries, 1):
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST QUERY {query_num}: {query}")
        logger.info(f"{'='*80}")
        
        # Search with contextual retrieval
        logger.info("\n--- CONTEXTUAL RETRIEVAL ---")
        contextual_results = contextual_agent.memory_tools.memory_search(query, top_k=3)
        
        logger.info(f"Found {len(contextual_results)} relevant chunks")
        for i, result in enumerate(contextual_results[:2], 1):
            logger.info(f"\n  Result {i} (Score: {result['relevance_score']:.3f}):")
            if result.get('context_description'):
                logger.info(f"    Context: {result['context_description'][:150]}...")
            logger.info(f"    Content: {result['content_preview'][:150]}...")
        
        # Search without contextual retrieval
        logger.info("\n--- NON-CONTEXTUAL RETRIEVAL ---")
        non_contextual_results = non_contextual_agent.memory_tools.memory_search(query, top_k=3)
        
        logger.info(f"Found {len(non_contextual_results)} relevant chunks")
        for i, result in enumerate(non_contextual_results[:2], 1):
            logger.info(f"\n  Result {i} (Score: {result['relevance_score']:.3f}):")
            logger.info(f"    Content: {result['content_preview'][:150]}...")
        
        # Compare top results
        if contextual_results and non_contextual_results:
            ctx_ids = {r['chunk_id'] for r in contextual_results}
            non_ctx_ids = {r['chunk_id'] for r in non_contextual_results}
            overlap = len(ctx_ids & non_ctx_ids)
            logger.info(f"\n  Overlap in top results: {overlap}/{len(contextual_results)}")
    
    # Phase 4: Answer a complex question
    logger.info("\n" + "="*80)
    logger.info("PHASE 4: ANSWERING COMPLEX QUESTIONS")
    logger.info("="*80)
    
    complex_query = "What are my total monthly costs for insurance and when do I need to renew my vehicle registrations?"
    
    logger.info(f"\nComplex Query: {complex_query}")
    
    # Answer with contextual agent
    logger.info("\n--- CONTEXTUAL AGENT ANSWER ---")
    ctx_answer = contextual_agent.answer_with_memories(complex_query)
    logger.info(f"\n{ctx_answer}")
    
    # Show trajectory
    ctx_trajectory = contextual_agent.get_search_trajectory()
    if ctx_trajectory:
        logger.info(f"\n  Tool calls: {ctx_trajectory['total_tool_calls']}")
        logger.info(f"  Latency: {ctx_trajectory['latency_ms']}ms")
    
    # Answer with non-contextual agent
    logger.info("\n--- NON-CONTEXTUAL AGENT ANSWER ---")
    non_ctx_answer = non_contextual_agent.answer_with_memories(complex_query)
    logger.info(f"\n{non_ctx_answer}")
    
    # Show trajectory
    non_ctx_trajectory = non_contextual_agent.get_search_trajectory()
    if non_ctx_trajectory:
        logger.info(f"\n  Tool calls: {non_ctx_trajectory['total_tool_calls']}")
        logger.info(f"  Latency: {non_ctx_trajectory['latency_ms']}ms")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DEMONSTRATION SUMMARY")
    logger.info("="*80)
    logger.info("\nKey Observations:")
    logger.info("1. Contextual retrieval adds descriptive context to each chunk")
    logger.info("2. This context helps find relevant information even with indirect queries")
    logger.info("3. The agent can better synthesize information from multiple conversations")
    logger.info("4. Complex questions are answered more accurately with contextual retrieval")
    
    logger.info("\nBased on Anthropic's research:")
    logger.info("- Contextual embeddings reduce retrieval failures by 35%")
    logger.info("- Combined with BM25, reduction reaches 49%")
    logger.info("- With reranking, reduction can reach 67%")
    
    logger.info("\n" + "="*80)
    logger.info("DEMO COMPLETE")
    logger.info("="*80)


if __name__ == "__main__":
    run_demo()
