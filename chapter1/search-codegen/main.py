"""
Main entry point for GPT-5 Native Tools Agent
Interactive CLI for using web_search and code_interpreter tools
"""

import sys
import json
import logging
from typing import Optional
from agent import GPT5NativeAgent, GPT5AgentChain
from config import Config
import argparse

# Set up logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


class InteractiveCLI:
    """Interactive command-line interface for GPT-5 Agent"""
    
    def __init__(self):
        """Initialize the CLI"""
        if not Config.validate():
            raise ValueError("Invalid configuration. Please check your .env file")
        
        self.agent = GPT5NativeAgent(
            api_key=Config.OPENROUTER_API_KEY,
            base_url=Config.OPENROUTER_BASE_URL,
            model=Config.MODEL_NAME
        )
        
        self.commands = {
            "/help": self.show_help,
            "/clear": self.clear_history,
            "/history": self.show_history,
            "/tools": self.toggle_tools,
            "/search": self.search_mode,
            "/code": self.code_mode,
            "/analyze": self.analyze_mode,
            "/config": self.show_config,
            "/reasoning": self.set_reasoning_effort,
            "/exit": self.exit_cli,
            "/quit": self.exit_cli,
        }
        
        self.use_tools = True
        self.tool_choice = "auto"
        self.reasoning_effort = "low"  # Default reasoning effort
    
    def show_help(self):
        """Display help information"""
        help_text = """
Commands:                                              
  /help     - Show this help message                    
  /clear    - Clear conversation history                
  /history  - Show conversation history                 
  /tools    - Toggle tools on/off                       
  /search   - Enter web search mode                     
  /code     - Enter code interpreter mode               
  /analyze  - Combined search + analysis mode           
  /config   - Show current configuration                
  /reasoning - Set reasoning effort (low/medium/high)   
  /exit     - Exit the application                      
                                                        
Native Tools:                                           
  • web_search - Search the internet for real-time info 
  • code_interpreter - Execute Python code and analyze  
                                                        
Usage:                                                  
  Simply type your request and the agent will use       
  appropriate tools automatically.                      
                                                        
Examples:                                               
  "东盟 10 国首都之间，距离最近的两个首都是？给出你的详细分析推理过程。"
  "搜索最近一年比特币的价格，计算收益率、最大回撤、年化波动等重要指标"
        """
        print(help_text)
    
    def clear_history(self):
        """Clear conversation history"""
        self.agent.clear_history()
        print("✅ Conversation history cleared")
    
    def show_history(self):
        """Display conversation history"""
        history = self.agent.get_history()
        if not history:
            print("📭 No conversation history")
            return
        
        print("\n" + "="*60)
        print("CONVERSATION HISTORY")
        print("="*60)
        
        for i, msg in enumerate(history, 1):
            role = msg["role"].upper()
            content = msg["content"][:200] + "..." if len(msg["content"]) > 200 else msg["content"]
            print(f"\n[{i}] {role}:\n{content}")
        
        print("="*60)
    
    def toggle_tools(self):
        """Toggle tool usage on/off"""
        self.use_tools = not self.use_tools
        status = "enabled" if self.use_tools else "disabled"
        print(f"🔧 Tools {status}")
    
    def search_mode(self):
        """Enter web search mode"""
        print("\n🔍 Web Search Mode")
        print("Enter your search query (or 'back' to return):")
        
        query = input("> ").strip()
        if query.lower() == "back":
            return
        
        request = f"Search the web for: {query}"
        self._process_request(request, force_tools=True)
    
    def code_mode(self):
        """Enter code interpreter mode"""
        print("\n💻 Code Interpreter Mode")
        print("Enter your code or computational request (or 'back' to return):")
        
        request = input("> ").strip()
        if request.lower() == "back":
            return
        
        enhanced_request = f"Use the code interpreter to: {request}"
        self._process_request(enhanced_request, force_tools=True)
    
    def analyze_mode(self):
        """Combined search and analysis mode"""
        print("\n🔬 Search & Analyze Mode")
        print("Enter topic to research and analyze (or 'back' to return):")
        
        topic = input("> ").strip()
        if topic.lower() == "back":
            return
        
        print("\nOptional: Enter Python code for analysis (press Enter to skip):")
        code = input("> ").strip()
        
        if code:
            result = self.agent.search_and_analyze(topic, code)
        else:
            result = self.agent.search_and_analyze(topic)
        
        self._display_result(result)
    
    def show_config(self):
        """Display current configuration"""
        Config.display()
        print(f"\nCurrent Settings:")
        print(f"  Tools Enabled: {self.use_tools}")
        print(f"  Tool Choice: {self.tool_choice}")
        print(f"  Reasoning Effort: {self.reasoning_effort}")
    
    def set_reasoning_effort(self):
        """Set the reasoning effort level"""
        print("\n🧠 Set Reasoning Effort")
        print("Options: low, medium, high")
        print(f"Current: {self.reasoning_effort}")
        
        effort = input("Enter new effort level: ").strip().lower()
        if effort in ["low", "medium", "high"]:
            self.reasoning_effort = effort
            print(f"✅ Reasoning effort set to: {effort}")
        else:
            print(f"❌ Invalid effort level. Must be low, medium, or high")
    
    def exit_cli(self):
        """Exit the application"""
        print("\n👋 Goodbye!")
        sys.exit(0)
    
    def _process_request(self, request: str, force_tools: bool = False):
        """
        Process a user request
        
        Args:
            request: User request
            force_tools: Force tool usage regardless of settings
        """
        use_tools = force_tools or self.use_tools
        
        result = self.agent.process_request(
            request,
            use_tools=use_tools,
            tool_choice=self.tool_choice if use_tools else "none",
            temperature=Config.DEFAULT_TEMPERATURE,
            max_tokens=Config.DEFAULT_MAX_TOKENS,
            reasoning_effort=self.reasoning_effort
        )
        
        self._display_result(result)
    
    def _display_result(self, result: dict):
        """
        Display the result of a request
        
        Args:
            result: Result dictionary from agent
        """
        print("\n" + "="*60)
        
        if result["success"]:
            # Display tool usage
            if result["tool_calls"]:
                print("🔧 Tools Used:")
                for tool in result["tool_calls"]:
                    print(f"  • {tool.tool_type.value}")
                print()
            
            # Display response
            print("📝 Response:")
            print("-"*60)
            print(result["response"])
            print("-"*60)
            
            # Display token usage
            if result.get("usage"):
                usage = result["usage"]
                total = usage.get("total_tokens", 0)
                if total:
                    print(f"\n📊 Tokens used: {total}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
        
        print("="*60)
    
    def run(self):
        """Run the interactive CLI"""
        print("\n" + "="*60)
        print("     🤖 GPT-5 Native Tools Agent")
        print("     Powered by OpenRouter API")
        print("="*60)
        
        self.show_help()
        
        while True:
            try:
                print("\n💬 Enter your request (or /help for commands):")
                user_input = input("> ").strip()
                
                if not user_input:
                    continue
                
                # Check for commands
                if user_input.startswith("/"):
                    command = user_input.split()[0].lower()
                    if command in self.commands:
                        self.commands[command]()
                    else:
                        print(f"❌ Unknown command: {command}")
                        print("Type /help for available commands")
                else:
                    # Process as regular request
                    self._process_request(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted. Type /exit to quit or continue chatting.")
            except Exception as e:
                logger.error(f"Error: {str(e)}")
                print(f"❌ An error occurred: {str(e)}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="GPT-5 Native Tools Agent - Web Search & Code Interpreter"
    )
    
    parser.add_argument(
        "--mode",
        choices=["interactive", "single", "test"],
        default="interactive",
        help="Execution mode"
    )
    
    parser.add_argument(
        "--request",
        type=str,
        help="Request for single mode"
    )
    
    parser.add_argument(
        "--no-tools",
        action="store_true",
        help="Disable tools"
    )
    
    parser.add_argument(
        "--test",
        type=str,
        help="Run specific test (for test mode)"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    if not Config.validate():
        print("❌ Configuration error!")
        print("Please create a .env file with your OPENROUTER_API_KEY")
        print("\nExample .env file:")
        print("OPENROUTER_API_KEY=sk-or-v1-your-key-here")
        sys.exit(1)
    
    if args.mode == "interactive":
        # Run interactive CLI
        cli = InteractiveCLI()
        cli.run()
        
    elif args.mode == "single":
        # Single request mode
        if not args.request:
            print("❌ --request required for single mode")
            sys.exit(1)
        
        agent = GPT5NativeAgent(
            api_key=Config.OPENROUTER_API_KEY,
            base_url=Config.OPENROUTER_BASE_URL,
            model=Config.MODEL_NAME
        )
        
        result = agent.process_request(
            args.request,
            use_tools=not args.no_tools,
            temperature=Config.DEFAULT_TEMPERATURE,
            reasoning_effort="low"  # Default for single mode
        )
        
        if result["success"]:
            print(result["response"])
        else:
            print(f"Error: {result.get('error')}")
            sys.exit(1)
            
    elif args.mode == "test":
        # Run tests
        from test_agent import TestGPT5Agent, run_single_test
        
        if args.test:
            run_single_test(args.test)
        else:
            tester = TestGPT5Agent()
            tester.run_all_tests()


if __name__ == "__main__":
    main()
