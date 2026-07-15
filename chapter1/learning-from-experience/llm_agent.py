"""
LLM-based Agent using In-Context Learning with Kimi K2 API.
This demonstrates how LLMs can generalize through reasoning without extensive training.
"""

import os
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import openai
from game_environment import TreasureHuntGame


@dataclass
class GameExperience:
    """Represents a single game interaction experience."""
    state_description: str
    action: str
    feedback: str
    reward: float
    success: bool  # Whether the action led to positive outcome


class LLMAgent:
    """
    LLM-based agent that uses in-context learning to play the game.
    Stores experiences and uses them to reason about future actions.
    """
    
    def __init__(self, 
                 api_key: str = None,
                 model: str = "kimi-k2-0905-preview",  # Kimi K2 model
                 base_url: str = "https://api.moonshot.cn/v1",
                 temperature: float = 0.7,
                 max_experiences: int = 50):
        """
        Initialize LLM agent with Kimi K2 API.
        
        Args:
            api_key: Kimi API key (or set MOONSHOT_API_KEY env var)
            model: Model name for Kimi K2
            base_url: API base URL
            temperature: Sampling temperature for generation
            max_experiences: Maximum number of experiences to store
        """
        # Set up API client
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError("Please provide Kimi API key or set MOONSHOT_API_KEY environment variable")
        
        self.client = openai.OpenAI(
            api_key=self.api_key,
            base_url=base_url
        )
        self.model = model
        self.temperature = temperature
        
        # Experience memory for in-context learning
        self.experiences: List[GameExperience] = []
        self.max_experiences = max_experiences
        
        # Statistics
        self.episode_rewards = []
        self.episode_lengths = []
        self.victories = 0
        self.total_episodes = 0
        self.api_calls = 0
        self.total_tokens = 0
    
    def _build_context(self, current_state: str, available_actions: List[str]) -> str:
        """
        Build context for the LLM including task description and past experiences.
        This is the key to in-context learning.
        """
        context = []
        
        # Task description
        context.append("""You are playing a text-based treasure hunt game. Your goal is to find and collect the dragon's treasure.

The game has hidden mechanics that you need to discover through experience:
- Certain items may be required to unlock doors or defeat guards
- Items might combine to create better items
- Different weapons have different effectiveness

You should reason about what you've learned from past experiences to make better decisions.""")
        
        # Add relevant past experiences
        if self.experiences:
            context.append("\n=== PAST EXPERIENCES ===")
            context.append("Here are some experiences from previous attempts that might help you:")
            
            # Group experiences by pattern
            successful_patterns = []
            failed_patterns = []
            
            for exp in self.experiences[-self.max_experiences:]:
                exp_text = f"State: {exp.state_description[:200]}...\nAction: {exp.action}\nResult: {exp.feedback}\nReward: {exp.reward:.1f}"
                
                if exp.success:
                    successful_patterns.append(exp_text)
                else:
                    failed_patterns.append(exp_text)
            
            if successful_patterns:
                context.append("\n** Successful actions:")
                for pattern in successful_patterns[-10:]:  # Last 10 successful
                    context.append(pattern)
            
            if failed_patterns:
                context.append("\n** Failed actions to avoid:")
                for pattern in failed_patterns[-5:]:  # Last 5 failed
                    context.append(pattern)
        
        # Current situation
        context.append("\n=== CURRENT SITUATION ===")
        context.append(current_state)
        context.append(f"\nAvailable actions: {', '.join(available_actions)}")
        
        return "\n".join(context)
    
    def _build_prompt(self, context: str) -> str:
        """Build the full prompt for the LLM."""
        prompt = f"""{context}

Based on your understanding of the game mechanics from past experiences and the current situation, reason step-by-step about what action to take:

1. What have you learned from past experiences that applies here?
2. What is your current goal or sub-goal?
3. Which available action best helps achieve that goal?

Think through this carefully, then provide your chosen action.

IMPORTANT: Your response must end with exactly one line starting with "ACTION:" followed by one of the available actions listed above.

Example format:
[Your reasoning here...]
ACTION: take red key
"""
        return prompt
    
    def choose_action(self, game: TreasureHuntGame, verbose: bool = True) -> str:
        """
        Choose an action using LLM reasoning with in-context learning.
        """
        # Get current state and available actions
        state_description = game.get_state_description()
        available_actions = game.get_available_actions()
        
        if not available_actions:
            return "look around"
        
        # Build context with past experiences
        context = self._build_context(state_description, available_actions)
        prompt = self._build_prompt(context)
        
        if verbose:
            print("\n" + "="*60)
            print("LLM DECISION PROCESS")
            print("="*60)
            print(f"📊 Experiences in memory: {len(self.experiences)}")
            print(f"🎮 Current room: {game.current_room.name}")
            print(f"🎯 Available actions: {len(available_actions)}")
            
            # Show some recent successful experiences if any
            successful = [e for e in self.experiences if e.success]
            if successful:
                print(f"\n💡 Recent successful patterns learned:")
                for exp in successful[-3:]:
                    print(f"   • {exp.action} → +{exp.reward:.1f} reward")
        
        try:
            print("\n🤔 LLM is thinking...")
            
            # Call Kimi K2 API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an intelligent game-playing agent that learns from experience."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=500
            )
            
            self.api_calls += 1
            if hasattr(response.usage, 'total_tokens'):
                self.total_tokens += response.usage.total_tokens
            
            # Extract action from response
            response_text = response.choices[0].message.content
            
            if verbose:
                print("\n📝 LLM Reasoning:")
                print("-" * 40)
                # Show the reasoning part (before ACTION:)
                reasoning_lines = []
                for line in response_text.split('\n'):
                    if line.startswith("ACTION:"):
                        break
                    if line.strip():
                        reasoning_lines.append(line)
                
                # Show last few lines of reasoning
                for line in reasoning_lines[-5:]:
                    print(f"  {line[:100]}...")  # Truncate long lines
                print("-" * 40)
            
            # Parse action from response
            lines = response_text.strip().split('\n')
            for line in reversed(lines):
                if line.startswith("ACTION:"):
                    action = line[7:].strip()
                    
                    # Validate action
                    if action in available_actions:
                        if verbose:
                            print(f"\n✅ Chosen action: {action}")
                        return action
                    else:
                        # Try to find closest matching action
                        action_lower = action.lower()
                        for available in available_actions:
                            if available.lower() == action_lower:
                                if verbose:
                                    print(f"\n✅ Chosen action (corrected): {available}")
                                return available
            
            # Fallback if no valid action found
            print(f"⚠️ Warning: Could not parse valid action from LLM response. Using fallback.")
            return available_actions[0]
            
        except Exception as e:
            print(f"❌ Error calling LLM API: {e}")
            # Fallback to first available action
            return available_actions[0]
    
    def update_experience(self, state: str, action: str, feedback: str, reward: float):
        """
        Store an experience for future in-context learning.
        """
        # Determine if action was successful based on reward
        success = reward > 0
        
        experience = GameExperience(
            state_description=state,
            action=action,
            feedback=feedback,
            reward=reward,
            success=success
        )
        
        self.experiences.append(experience)
        
        # Keep only recent experiences to manage context length
        if len(self.experiences) > self.max_experiences * 2:
            # Keep a mix of successful and failed experiences
            successful = [e for e in self.experiences if e.success]
            failed = [e for e in self.experiences if not e.success]
            
            # Keep recent ones and some diverse older ones
            self.experiences = (
                successful[-self.max_experiences:] + 
                failed[-self.max_experiences//2:]
            )[-self.max_experiences:]
    
    def play_episode(self, game: TreasureHuntGame, verbose: bool = True) -> Tuple[float, int, bool]:
        """
        Play one episode of the game.
        """
        game.reset()
        total_reward = 0
        steps = 0
        trajectory = []
        
        if verbose:
            print("\n" + "🎮"*30)
            print("STARTING NEW GAME EPISODE")
            print("🎮"*30)
        
        while not game.game_over:
            if verbose:
                print(f"\n{'='*60}")
                print(f"STEP {steps + 1}")
                print(f"{'='*60}")
                
                # Show current game state
                print("\n📍 Current State:")
                state_lines = game.get_state_description().split('\n')
                for line in state_lines:
                    if line.strip():
                        print(f"  {line}")
            
            # Get state before action
            state_before = game.get_state_description()
            
            # Choose action using LLM
            action = self.choose_action(game, verbose=verbose)
            
            # Execute action
            feedback, reward, done = game.execute_action(action)
            
            # Store experience
            self.update_experience(state_before, action, feedback, reward)
            
            # Record trajectory
            trajectory.append({
                "step": steps + 1,
                "action": action,
                "reward": reward,
                "feedback": feedback
            })
            
            total_reward += reward
            steps += 1
            
            if verbose:
                print(f"\n🎯 Action Result:")
                print(f"  Feedback: {feedback}")
                if reward > 0:
                    print(f"  Reward: ✨ +{reward:.1f}")
                else:
                    print(f"  Reward: 📉 {reward:.1f}")
                print(f"  Total reward so far: {total_reward:.1f}")
                
                # Add a pause between steps for readability
                if not done:
                    print("\n" + "."*60)
        
        # Update statistics
        self.episode_rewards.append(total_reward)
        self.episode_lengths.append(steps)
        if game.victory:
            self.victories += 1
        self.total_episodes += 1
        
        if verbose:
            print("\n" + "🏁"*30)
            if game.victory:
                print("🎉 VICTORY! The LLM found the treasure!")
            else:
                print("💀 GAME OVER! Better luck next time.")
            print(f"  Final Score: {total_reward:.1f}")
            print(f"  Total Steps: {steps}")
            print(f"  API Calls Used: {self.api_calls}")
            print("🏁"*30)
        
        return total_reward, steps, game.victory
    
    def train(self, num_episodes: int = 20, verbose: bool = True, stochastic: bool = False) -> Dict[str, Any]:
        """
        'Train' the agent through in-context learning over multiple episodes.
        Note: Unlike traditional RL, there's no explicit training - just experience accumulation.
        
        Args:
            num_episodes: Number of episodes to play
            verbose: Whether to print details
            stochastic: Whether to use stochastic environment
        """
        game = TreasureHuntGame(stochastic=stochastic)
        
        print("\n" + "🚀"*30)
        print("LLM IN-CONTEXT LEARNING EXPERIMENT")
        print("🚀"*30)
        print(f"\n📝 Will play {num_episodes} episodes to learn the game")
        print("🧠 The LLM learns by accumulating experiences in context")
        print("⚡ Each decision shows the full reasoning process")
        
        for episode in range(num_episodes):
            print(f"\n\n{'🎯'*30}")
            print(f"EPISODE {episode + 1} of {num_episodes}")
            print(f"{'🎯'*30}")
            print(f"📚 Experiences accumulated so far: {len(self.experiences)}")
            
            # Show full process for first 3 episodes, then reduce verbosity
            show_full = verbose and (episode < 3 or episode == num_episodes - 1)
            
            if not show_full and verbose:
                print("\n(Reducing verbosity for middle episodes to save space...)")
            
            reward, steps, victory = self.play_episode(game, verbose=show_full)
            
            if not show_full:
                # Still show summary even when not fully verbose
                print(f"\n📊 Episode {episode + 1} Summary:")
                print(f"  Result: {'🎉 Victory!' if victory else '💀 Failed'}")
                print(f"  Total Reward: {reward:.2f}")
                print(f"  Steps Taken: {steps}")
                print(f"  Total API Calls So Far: {self.api_calls}")
            
            # Show learning progress
            if len(self.episode_rewards) >= 3:
                recent_victories = sum(1 for r in self.episode_rewards[-3:] if r > 50)
                recent_avg = sum(self.episode_rewards[-3:]) / 3
                print(f"\n📈 Recent Performance (last 3 episodes):")
                print(f"  Victories: {recent_victories}/3")
                print(f"  Average Reward: {recent_avg:.2f}")
            
            # Add delay to respect rate limits
            if episode < num_episodes - 1:
                print("\n⏳ Waiting 1 second for API rate limits...")
                time.sleep(1)
        
        return {
            "total_episodes": self.total_episodes,
            "total_victories": self.victories,
            "victory_rate": self.victories / self.total_episodes if self.total_episodes > 0 else 0,
            "total_api_calls": self.api_calls,
            "total_tokens": self.total_tokens,
            "experiences_collected": len(self.experiences),
            "episode_rewards": self.episode_rewards,
            "episode_lengths": self.episode_lengths
        }
    
    def evaluate(self, num_episodes: int = 10, verbose: bool = False, stochastic: bool = False) -> Dict[str, Any]:
        """
        Evaluate the agent's performance using accumulated experiences.
        
        Args:
            num_episodes: Number of episodes to evaluate
            verbose: Whether to print details
            stochastic: Whether to use stochastic environment
        """
        game = TreasureHuntGame(stochastic=stochastic)
        eval_rewards = []
        eval_lengths = []
        eval_victories = 0
        
        for episode in range(num_episodes):
            reward, steps, victory = self.play_episode(game, verbose=verbose)
            
            eval_rewards.append(reward)
            eval_lengths.append(steps)
            if victory:
                eval_victories += 1
            
            if verbose:
                print(f"Episode {episode + 1}: Reward={reward:.2f}, Steps={steps}, Victory={victory}")
        
        return {
            "num_episodes": num_episodes,
            "victories": eval_victories,
            "victory_rate": eval_victories / num_episodes,
            "avg_reward": sum(eval_rewards) / len(eval_rewards),
            "avg_length": sum(eval_lengths) / len(eval_lengths),
            "total_api_calls": self.api_calls,
            "experiences_used": len(self.experiences)
        }
    
    def save_experiences(self, filepath: str):
        """Save experiences to file for analysis."""
        data = {
            "experiences": [asdict(exp) for exp in self.experiences],
            "statistics": {
                "total_episodes": self.total_episodes,
                "victories": self.victories,
                "api_calls": self.api_calls,
                "total_tokens": self.total_tokens
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_experiences(self, filepath: str):
        """Load experiences from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.experiences = [
            GameExperience(**exp) for exp in data["experiences"]
        ]
        
        stats = data.get("statistics", {})
        self.total_episodes = stats.get("total_episodes", 0)
        self.victories = stats.get("victories", 0)
        self.api_calls = stats.get("api_calls", 0)
        self.total_tokens = stats.get("total_tokens", 0)
