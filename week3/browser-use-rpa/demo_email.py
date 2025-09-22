"""
Demo: Email sending with learning capability

This demo shows how the agent learns to send emails and reuses the learned workflow.
Uses Ethereal Email (ethereal.email) as a test email service.
"""

import asyncio
import logging
import time
from dotenv import load_dotenv

from browser_use import ChatOpenAI, ChatGoogle
from learning_agent import LearningAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


class EmailDemo:
    """Demo for email sending with learning capability."""
    
    def __init__(self, llm_model="gpt-4o-mini"):
        self.llm_model = llm_model
        self.knowledge_base_path = "./email_knowledge"
        
    async def run_full_demo(self):
        """Run complete email demo with learning and replay phases."""
        
        print("=" * 80)
        print("EMAIL SENDING DEMO - LEARNING AGENT")
        print("=" * 80)
        print("\nThis demo uses Ethereal Email (ethereal.email) for testing.")
        print("Note: This is a test service - emails won't actually be delivered.")
        print("=" * 80)
        
        # Phase 1: Learning
        await self.phase1_learning()
        
        # Wait before Phase 2
        print("\n⏳ Waiting 5 seconds before replay phase...")
        await asyncio.sleep(5)
        
        # Phase 2: Replay
        await self.phase2_replay()
        
        # Phase 3: Statistics
        self.show_statistics()
        
    async def phase1_learning(self):
        """Phase 1: Learn how to send an email."""
        
        print("\n" + "📚 PHASE 1: LEARNING - First Email Task ".ljust(70, "="))
        print("\nThe agent will learn how to send an email from scratch.")
        print("This requires multiple LLM calls to explore and understand the interface.")
        print("-" * 70)
        
        # Task with specific details
        task = """
        Go to https://ethereal.email and send a test email with:
        - To: test@example.com
        - Subject: Hello from Learning Agent
        - Message: This is a test email sent by the learning agent. The workflow will be captured for future reuse.
        """
        
        print(f"Task: Send email to test@example.com")
        print("Expected behavior:")
        print("  1. Navigate to Ethereal Email")
        print("  2. Create a test account (if needed)")
        print("  3. Compose and send the email")
        print("  4. Capture workflow for future reuse")
        
        # Create learning agent
        agent = LearningAgent(
            task=task,
            llm=self._get_llm(),
            knowledge_base_path=self.knowledge_base_path,
            headless=False  # Show browser for demo
        )
        
        print("\n🚀 Starting learning phase...")
        start_time = time.time()
        
        try:
            result = await agent.run(max_steps=20)
            
            elapsed = time.time() - start_time
            
            print("\n✅ Learning phase completed!")
            print(f"  📊 Results:")
            print(f"     - Success: {'✓' if result['success'] else '✗'}")
            print(f"     - Execution time: {elapsed:.2f} seconds")
            print(f"     - LLM calls made: {result['llm_calls']}")
            print(f"     - Workflow captured: {'Yes' if result['success'] else 'No'}")
            
            if result['success']:
                print("\n  💡 Workflow successfully learned and saved!")
                print("     The agent can now repeat similar tasks without LLM calls.")
            
            # Store metrics for comparison
            self.learning_metrics = {
                'time': elapsed,
                'llm_calls': result['llm_calls'],
                'success': result['success']
            }
            
        except Exception as e:
            print(f"\n❌ Learning phase failed: {e}")
            self.learning_metrics = {'time': 0, 'llm_calls': 0, 'success': False}
    
    async def phase2_replay(self):
        """Phase 2: Replay learned workflow with different parameters."""
        
        print("\n" + "🚀 PHASE 2: REPLAY - Second Email Task ".ljust(70, "="))
        print("\nThe agent will reuse the learned workflow with different parameters.")
        print("This should be much faster and require NO LLM calls.")
        print("-" * 70)
        
        # Different email parameters
        task = """
        Send an email to another@example.com with subject "Workflow Test" 
        and message "This email is sent using a learned workflow. No LLM calls needed!"
        """
        
        print(f"Task: Send email to another@example.com")
        print("Expected behavior:")
        print("  1. Match task to learned workflow")
        print("  2. Extract new parameters (recipient, subject, message)")
        print("  3. Replay workflow with new parameters")
        print("  4. Complete task without any LLM calls")
        
        # Create agent for replay
        agent = LearningAgent(
            task=task,
            llm=self._get_llm(),
            knowledge_base_path=self.knowledge_base_path,
            headless=False
        )
        
        print("\n🔄 Starting replay phase...")
        start_time = time.time()
        
        try:
            result = await agent.run(max_steps=20)
            
            elapsed = time.time() - start_time
            
            print("\n✅ Replay phase completed!")
            print(f"  📊 Results:")
            print(f"     - Success: {'✓' if result['success'] else '✗'}")
            print(f"     - Execution time: {elapsed:.2f} seconds")
            print(f"     - Workflow reused: {'Yes' if result['replay_used'] else 'No'}")
            
            if result['replay_used']:
                # Calculate improvements
                if hasattr(self, 'learning_metrics') and self.learning_metrics['success']:
                    speedup = self.learning_metrics['time'] / elapsed
                    calls_saved = self.learning_metrics['llm_calls']
                    
                    print(f"\n  🎯 Performance Improvements:")
                    print(f"     - Speed: {speedup:.1f}x faster")
                    print(f"     - LLM calls saved: {calls_saved}")
                    print(f"     - Time saved: {self.learning_metrics['time'] - elapsed:.1f} seconds")
            else:
                print(f"     - LLM calls made: {result.get('llm_calls', 0)}")
                print("\n  ⚠️ Workflow was not reused. Task may be too different.")
            
            # Store replay metrics
            self.replay_metrics = {
                'time': elapsed,
                'replay_used': result['replay_used'],
                'success': result['success']
            }
            
        except Exception as e:
            print(f"\n❌ Replay phase failed: {e}")
            self.replay_metrics = {'time': 0, 'replay_used': False, 'success': False}
    
    def show_statistics(self):
        """Show knowledge base statistics."""
        
        print("\n" + "📊 KNOWLEDGE BASE STATISTICS ".ljust(70, "="))
        
        from learning_agent import KnowledgeBase
        kb = KnowledgeBase(self.knowledge_base_path)
        stats = kb.get_statistics()
        
        print("\n  Current Knowledge Base Status:")
        for key, value in stats.items():
            formatted_key = key.replace('_', ' ').title()
            print(f"     - {formatted_key}: {value}")
        
        # Show comparison if both phases completed
        if hasattr(self, 'learning_metrics') and hasattr(self, 'replay_metrics'):
            if self.learning_metrics['success'] and self.replay_metrics['replay_used']:
                print("\n  📈 Performance Comparison:")
                print(f"     Phase 1 (Learning):")
                print(f"        - Time: {self.learning_metrics['time']:.2f}s")
                print(f"        - LLM Calls: {self.learning_metrics['llm_calls']}")
                print(f"     Phase 2 (Replay):")
                print(f"        - Time: {self.replay_metrics['time']:.2f}s")
                print(f"        - LLM Calls: 0")
                
                improvement = (1 - self.replay_metrics['time'] / self.learning_metrics['time']) * 100
                print(f"\n     🚀 Overall Improvement: {improvement:.0f}% faster with replay!")
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("=" * 70)
    
    def _get_llm(self):
        """Get LLM instance based on configuration."""
        if self.llm_model.startswith("gpt"):
            return ChatOpenAI(model=self.llm_model)
        elif self.llm_model.startswith("gemini"):
            return ChatGoogle(model=self.llm_model)
        else:
            return ChatOpenAI(model="gpt-4o-mini")


async def quick_test():
    """Quick test with simple task."""
    print("\n🧪 QUICK TEST - Simple Email Task")
    print("-" * 40)
    
    task = "Go to ethereal.email and send a test email to demo@test.com"
    
    agent = LearningAgent(
        task=task,
        llm=ChatOpenAI(model="gpt-4o-mini"),
        knowledge_base_path="./test_knowledge",
        headless=False
    )
    
    print(f"Task: {task}")
    result = await agent.run(max_steps=15)
    
    print(f"\nResult: {'Success' if result['success'] else 'Failed'}")
    print(f"Time: {result['execution_time']:.2f}s")
    print(f"LLM calls: {result.get('llm_calls', 0)}")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        # Run quick test
        asyncio.run(quick_test())
    else:
        # Run full demo
        demo = EmailDemo()
        asyncio.run(demo.run_full_demo())


if __name__ == "__main__":
    main()
