#!/usr/bin/env python3
"""
Quick start script for the Agentic RAG User Memory System

This script demonstrates the basic workflow:
1. Create sample conversation history
2. Chunk and index the conversations
3. Query the indexed data
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from config import Config
from agent import UserMemoryRAGAgent
from conversation_chunker import ConversationChunker


logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def create_sample_conversations():
    """Create sample conversation history for testing"""
    
    conversations = []
    
    # Conversation 1: Travel planning
    conv1 = {
        "conversation_id": "travel_planning_001",
        "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
        "messages": []
    }
    
    travel_rounds = [
        ("I'm planning a trip to Japan next month. Can you help me?", 
         "I'd be happy to help you plan your trip to Japan! When exactly are you planning to go, and what are your main interests?"),
        
        ("I'll be there from March 15-25. I love traditional culture and food.",
         "Great timing! March is beautiful in Japan. For traditional culture, I recommend visiting Kyoto for temples and gardens. For food, don't miss Tokyo's Tsukiji Outer Market."),
        
        ("What's the weather like in March?",
         "March in Japan is early spring with mild temperatures (10-15°C). Cherry blossoms might start blooming late March in some areas."),
        
        ("Should I book hotels in advance?",
         "Yes, definitely book hotels in advance, especially in popular areas like Kyoto and Tokyo. March is still tourist season."),
        
        ("What about the JR Pass?",
         "The JR Pass is worth it if you're traveling between cities. A 7-day pass costs around ¥29,650 and covers most JR trains including shinkansen."),
        
        ("I want to see Mount Fuji. What's the best way?",
         "In March, you can't climb Mount Fuji (closed until July), but you can view it from Hakone or take a day trip to the Fuji Five Lakes area."),
        
        ("How much money should I budget per day?",
         "Budget around ¥10,000-15,000 per day for meals, transportation within cities, and attractions. This is comfortable but not luxurious."),
        
        ("Are there any cultural etiquette rules I should know?",
         "Yes: remove shoes when entering homes/temples, don't tip, be quiet on trains, and bow as greeting. Also, eating while walking is considered impolite."),
        
        ("What about language barriers?",
         "Major tourist areas have English signs, but learning basic phrases helps. Download Google Translate offline for emergencies."),
        
        ("Can you recommend specific restaurants in Tokyo?",
         "Try Sukiyabashi Jiro for sushi (book far ahead), Ichiran for ramen, and Gonpachi in Roppongi (Kill Bill restaurant)."),
        
        ("What's the best area to stay in Tokyo?",
         "Shinjuku or Shibuya for first-timers - central, well-connected, lots of dining/shopping. Asakusa for traditional feel."),
        
        ("Should I get a pocket WiFi or SIM card?",
         "Pocket WiFi is convenient for multiple devices. Costs about ¥5000-8000 for 10 days. Pick up at airport."),
        
        ("Any day trip recommendations from Tokyo?",
         "Nikko for shrines and nature (2 hours), Kamakura for Great Buddha and temples (1 hour), or Hakone for hot springs and Fuji views (2 hours)."),
        
        ("What souvenirs should I buy?",
         "KitKat unique flavors, sake, Japanese pottery, furoshiki wrapping cloths, or high-quality chopsticks make great souvenirs."),
        
        ("Is it safe to travel alone?",
         "Japan is one of the safest countries for solo travelers. Crime rate is very low, and public transport is reliable."),
        
        ("What apps should I download?",
         "Hyperdia for trains, Google Maps (works offline), Tabelog for restaurants, and Line for messaging if making local friends."),
        
        ("Any hidden gems in Kyoto?",
         "Visit Daigo-ji temple (less crowded), Kurama-dera mountain temple, and the Philosopher's Path early morning for peaceful experience."),
        
        ("What about allergies and dietary restrictions?",
         "Vegetarian/vegan can be challenging. Learn to say allergies in Japanese or carry a card. Many places accommodate with advance notice."),
        
        ("Best way to get from airport to city?",
         "From Narita: Narita Express to Tokyo (¥3000, 1 hour). From Haneda: Monorail or Keikyu line (¥500, 30 minutes)."),
        
        ("Should I bring cash or cards?",
         "Japan is still cash-heavy. Bring cash and withdraw from 7-Eleven ATMs. Some places accept cards but not all."),
        
        ("What if I get sick?",
         "Pharmacies are common. For serious issues, major hospitals have English support. Consider travel insurance."),
        
        ("Any festivals in March?",
         "Hina Matsuri (Girls' Day) on March 3rd with doll displays. Early cherry blossom festivals might start late March."),
        
        ("Remember I mentioned I love traditional culture earlier",
         "Yes, you mentioned loving traditional culture! Based on that, I especially recommend the Gion district in Kyoto where you might see geishas."),
        
        ("Perfect! I'll book flights now. Remember all these tips for my March 15-25 trip.",
         "Great! Your March 15-25 Japan trip will be amazing. I've noted all your preferences: traditional culture, food focus, Tokyo and Kyoto focus. Safe travels!"),
        
        ("Thank you for all the help!",
         "You're welcome! Enjoy your trip to Japan. Don't forget to try the cherry blossom themed foods if the sakura starts blooming!")
    ]
    
    for user_msg, assistant_msg in travel_rounds:
        conv1["messages"].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg}
        ])
    
    conversations.append(conv1)
    
    # Conversation 2: Medical appointments
    conv2 = {
        "conversation_id": "medical_appointments_002",
        "timestamp": (datetime.now() - timedelta(days=20)).isoformat(),
        "messages": []
    }
    
    medical_rounds = [
        ("I need to schedule my annual checkup. What should I prepare?",
         "For your annual checkup, prepare: list of current medications, recent symptoms or concerns, family medical history updates, and insurance cards."),
        
        ("I take metformin 500mg twice daily and lisinopril 10mg once daily.",
         "Good to note. Metformin for diabetes management and lisinopril for blood pressure. Bring this list and mention any side effects during your checkup."),
        
        ("My last checkup was January 2023. Is annual enough?",
         "With diabetes and hypertension, annual checkups are minimum. Consider twice yearly if your doctor recommends based on your condition management."),
        
        ("What tests are usually included?",
         "Typical tests: blood pressure, blood work (glucose, cholesterol, kidney function), BMI, and possibly EKG given your medications."),
        
        ("Should I fast before the appointment?",
         "Yes, usually fast 8-12 hours before blood work for accurate glucose and cholesterol readings. Confirm with your doctor's office."),
        
        ("My doctor is Dr. Smith at Riverside Medical. Should I switch?",
         "If Dr. Smith manages your conditions well and you're comfortable, no need to switch. Continuity of care is valuable for chronic conditions."),
        
        ("What questions should I ask?",
         "Ask about: medication adjustments, target blood sugar/pressure goals, lifestyle modifications, and when to schedule follow-ups."),
        
        ("I've been having occasional dizziness. Related to meds?",
         "Dizziness could be from lisinopril (blood pressure) or low blood sugar. Definitely mention this - might need dosage adjustment."),
        
        ("My insurance is Blue Cross PPO. Coverage good?",
         "Blue Cross PPO typically covers preventive care fully. Annual checkups should be covered. Check if lab work needs separate authorization."),
        
        ("Should I see specialists too?",
         "With diabetes, consider annual eye doctor and podiatrist visits. Might need endocrinologist if primary care isn't sufficient."),
        
        ("My A1C was 7.2 last time. Is that okay?",
         "A1C of 7.2% is slightly above the typical target of <7%. Discuss with your doctor about adjusting treatment or lifestyle changes."),
        
        ("I've lost 10 pounds since last year. Mention it?",
         "Yes, definitely mention the weight loss! It could affect medication dosing and might be a positive sign or need investigation."),
        
        ("Best time to schedule appointments?",
         "Early morning appointments are good for fasting blood work. Also, consider scheduling at year start when deductibles reset."),
        
        ("Should I get vaccines during checkup?",
         "Yes, good time for flu shot, and check if you need pneumonia or shingles vaccines. Diabetes increases infection risk."),
        
        ("How about dental checkups?",
         "Important for diabetics! Diabetes increases gum disease risk. See dentist every 6 months, mention your diabetes."),
        
        ("My mom was recently diagnosed with heart disease. Relevant?",
         "Very relevant! Family history affects your risk profile. Your doctor might want additional cardiac screening."),
        
        ("I walk 30 minutes daily now. Good enough?",
         "Great start! For diabetes and hypertension, aim for 150 minutes moderate exercise weekly. Mention this improvement to your doctor."),
        
        ("Should I track anything before the appointment?",
         "Track blood pressure and glucose readings for 2 weeks before. Also log diet and exercise. Brings valuable data."),
        
        ("What if I need referrals?",
         "With PPO, you usually don't need referrals, but check your plan. Get referrals anyway for continuity of records."),
        
        ("Prescription refills running low. Handle during checkup?",
         "Yes, perfect time to request refills. Ask for 90-day supplies if your insurance allows - more convenient."),
        
        ("Any warning signs to watch for?",
         "Watch for: chest pain, severe headaches, vision changes, numbness in extremities, or excessive thirst/urination."),
        
        ("Remember I mentioned metformin and lisinopril earlier?",
         "Yes, I noted you take metformin 500mg twice daily and lisinopril 10mg daily. Make sure to discuss the dizziness you mentioned with these medications."),
        
        ("Thanks! I'll schedule for next month with Dr. Smith.",
         "Perfect! Schedule your appointment with Dr. Smith at Riverside Medical, remember to fast before, and bring your medication list and concerns about dizziness.")
    ]
    
    for user_msg, assistant_msg in medical_rounds[:25]:  # Take first 25 rounds
        conv2["messages"].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg}
        ])
    
    conversations.append(conv2)
    
    return conversations


def main():
    """Run the quickstart demo"""
    
    print("=" * 60)
    print("Agentic RAG User Memory System - Quick Start")
    print("=" * 60)
    
    # Initialize configuration
    config = Config.from_env()
    config.chunking.rounds_per_chunk = 20  # Set to 20 rounds per chunk
    
    # Create data directory
    data_dir = Path("./demo_data")
    data_dir.mkdir(exist_ok=True)
    
    # Step 1: Create sample conversations
    print("\n1. Creating sample conversation history...")
    conversations = create_sample_conversations()
    
    history_file = data_dir / "sample_history.json"
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump({"conversations": conversations}, f, ensure_ascii=False, indent=2)
    
    print(f"   Created {len(conversations)} conversations with {sum(len(c['messages'])//2 for c in conversations)} total rounds")
    print(f"   Saved to: {history_file}")
    
    # Step 2: Initialize agent and build index
    print("\n2. Building RAG index from conversations...")
    agent = UserMemoryRAGAgent(config)
    
    report = agent.build_index_from_history(str(history_file), save_chunks=True)
    
    print(f"   Chunks created: {report['chunks_created']}")
    print(f"   Chunks indexed: {report['chunks_indexed']}")
    print(f"   Memories extracted: {report['memories_extracted']}")
    
    # Step 3: Test queries
    print("\n3. Testing queries on indexed data...")
    print("-" * 40)
    
    test_queries = [
        "What medications does the user take?",
        "When is the user planning to travel to Japan?",
        "What health conditions does the user have?",
        "What did we discuss about hotels in Japan?",
        "What was my A1C level?",
        "What restaurants were recommended in Tokyo?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("Response: ", end="", flush=True)
        
        response = ""
        for chunk in agent.query(query, stream=True):
            response += chunk
            print(chunk, end="", flush=True)
        
        print("\n" + "-" * 40)
        
        # Save the response
        if response:
            results_file = data_dir / "query_results.json"
            if results_file.exists():
                with open(results_file, 'r') as f:
                    results = json.load(f)
            else:
                results = []
            
            results.append({
                "query": query,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
    
    print("\n" + "=" * 60)
    print("Quick start complete!")
    print("\nYou can now:")
    print("1. Run 'python main.py query' for interactive mode")
    print("2. Add more conversations to the index")
    print("3. Experiment with different queries")
    print("=" * 60)


if __name__ == "__main__":
    main()
