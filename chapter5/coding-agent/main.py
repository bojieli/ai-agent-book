#!/usr/bin/env python3
"""
Interactive CLI for the Coding Agent
Provides a command-line interface for chatting with the agent
"""

import os
import sys
from pathlib import Path
from agent import CodingAgent
from config import Config


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright foreground colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'


class CodingAgentCLI:
    """Interactive CLI for the Coding Agent"""
    
    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors
        self.agent = None
        self.running = True
        
    def color(self, text: str, color_code: str) -> str:
        """Apply color to text if colors are enabled"""
        if self.use_colors:
            return f"{color_code}{text}{Colors.RESET}"
        return text
    
    def print_header(self):
        """Print CLI header"""
        print()
        print(self.color("=" * 80, Colors.CYAN))
        print(self.color("🤖 CODING AGENT - Interactive CLI", Colors.BOLD + Colors.CYAN))
        print(self.color("=" * 80, Colors.CYAN))
        print()
        print(self.color("Commands:", Colors.YELLOW))
        print(self.color("  /help", Colors.BRIGHT_BLACK) + "    - Show this help message")
        print(self.color("  /quit", Colors.BRIGHT_BLACK) + "    - Exit the CLI")
        print(self.color("  /exit", Colors.BRIGHT_BLACK) + "    - Exit the CLI")
        print(self.color("  /reset", Colors.BRIGHT_BLACK) + "   - Reset the agent (clear conversation history)")
        print(self.color("  /clear", Colors.BRIGHT_BLACK) + "   - Clear the screen")
        print(self.color("  /status", Colors.BRIGHT_BLACK) + "  - Show agent status")
        print()
        print(self.color("Type your message and press Enter. Use Ctrl+C to interrupt.", Colors.DIM))
        print(self.color("-" * 80, Colors.CYAN))
        print()
    
    def print_status(self):
        """Print agent status"""
        if not self.agent:
            print(self.color("❌ Agent not initialized", Colors.RED))
            return
        
        state = self.agent.system_state
        print()
        print(self.color("📊 Agent Status:", Colors.CYAN))
        print(self.color("━" * 40, Colors.CYAN))
        print(f"  Model: {self.color(self.agent.model, Colors.GREEN)}")
        print(f"  Working Directory: {self.color(state.current_directory, Colors.BLUE)}")
        print(f"  OS: {self.color(state.os_type, Colors.BLUE)}")
        print(f"  Python: {self.color(state.python_version, Colors.BLUE)}")
        print(f"  Messages in History: {self.color(str(len(self.agent.messages)), Colors.YELLOW)}")
        
        if state.tool_call_counts:
            print(f"\n  {self.color('Tool Calls:', Colors.MAGENTA)}")
            for tool, count in sorted(state.tool_call_counts.items()):
                print(f"    • {tool}: {self.color(str(count), Colors.YELLOW)}")
        
        if state.todos:
            print(f"\n  {self.color('TODO List:', Colors.MAGENTA)}")
            for todo in state.todos:
                status_icons = {
                    "pending": "⬜",
                    "in_progress": "🔄",
                    "completed": "✅"
                }
                icon = status_icons.get(todo['status'], '?')
                status_color = {
                    "pending": Colors.BRIGHT_BLACK,
                    "in_progress": Colors.YELLOW,
                    "completed": Colors.GREEN
                }.get(todo['status'], Colors.WHITE)
                print(f"    {icon} [{todo['id']}] {self.color(todo['content'], status_color)}")
        
        print(self.color("━" * 40, Colors.CYAN))
        print()
    
    def initialize_agent(self):
        """Initialize the agent"""
        try:
            Config.validate()
            
            # Get provider and configuration
            provider = Config.get_provider()
            api_key = Config.get_api_key()
            base_url = Config.get_base_url()
            
            # Initialize agent
            self.agent = CodingAgent(
                api_key=api_key,
                model=Config.DEFAULT_MODEL,
                base_url=base_url,
                provider=provider
            )
            
            print(self.color("✓ Agent initialized successfully", Colors.GREEN))
            print(self.color(f"  Provider: {provider}", Colors.DIM))
            print(self.color(f"  Model: {Config.DEFAULT_MODEL}", Colors.DIM))
            if base_url:
                print(self.color(f"  Base URL: {base_url}", Colors.DIM))
            print()
        except Exception as e:
            print(self.color(f"❌ Failed to initialize agent: {str(e)}", Colors.RED))
            print()
            print(self.color("Please check your .env file configuration:", Colors.YELLOW))
            print(self.color("Example:", Colors.DIM))
            print(self.color("  PROVIDER=anthropic", Colors.DIM))
            print(self.color("  ANTHROPIC_API_KEY=sk-ant-api03-...", Colors.DIM))
            print(self.color("  DEFAULT_MODEL=claude-sonnet-4-20250514", Colors.DIM))
            print()
            print(self.color("Supported providers: anthropic, openai, openrouter", Colors.DIM))
            print()
            sys.exit(1)
    
    def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns True if it was a command, False otherwise."""
        command = command.strip().lower()
        
        if command in ['/quit', '/exit']:
            print()
            print(self.color("👋 Goodbye!", Colors.CYAN))
            print()
            self.running = False
            return True
        
        elif command == '/help':
            self.print_header()
            return True
        
        elif command == '/reset':
            if self.agent:
                self.agent.reset()
                print()
                print(self.color("✓ Agent reset - conversation history cleared", Colors.GREEN))
                print()
            return True
        
        elif command == '/clear':
            os.system('clear' if os.name != 'nt' else 'cls')
            self.print_header()
            return True
        
        elif command == '/status':
            self.print_status()
            return True
        
        return False
    
    def run_agent(self, user_input: str):
        """Run the agent with user input and display results"""
        print()
        print(self.color("━" * 80, Colors.BRIGHT_BLACK))
        
        iteration_count = 0
        tool_call_count = 0
        
        try:
            for event in self.agent.run(user_input, max_iterations=50):
                
                if event["type"] == "iteration_start":
                    iteration_count = event["iteration"]
                    if iteration_count > 1:
                        print()
                        print(self.color(f"[Iteration {iteration_count}]", Colors.DIM))
                
                elif event["type"] == "text_delta":
                    # Print streaming text
                    print(event["delta"], end="", flush=True)
                
                elif event["type"] == "tool_call":
                    tool_call_count += 1
                    tool_name = event["tool"]
                    print(f"\n\n{self.color('🔧', Colors.CYAN)} {self.color(f'Calling tool:', Colors.CYAN)} {self.color(tool_name, Colors.BOLD + Colors.YELLOW)}")
                    
                    # Show tool input (abbreviated)
                    tool_input = event["input"]
                    if len(str(tool_input)) > 100:
                        input_preview = str(tool_input)[:100] + "..."
                    else:
                        input_preview = str(tool_input)
                    print(self.color(f"   Input: {input_preview}", Colors.DIM))
                
                elif event["type"] == "tool_execution_complete":
                    result = event["result"]
                    metadata = result.get("_metadata", {})
                    call_num = metadata.get("call_number", "?")
                    
                    # Show completion status
                    if "error" in result:
                        print(self.color(f"   ✗ Error: {result['error']}", Colors.RED))
                    else:
                        print(self.color(f"   ✓ Completed (call #{call_num})", Colors.GREEN))
                        
                        # Show important results
                        if "output" in result and event["tool"] == "Bash":
                            output = result["output"]
                            if len(output) > 200:
                                output = output[:200] + "..."
                            if output.strip():
                                print(self.color(f"   Output:", Colors.DIM))
                                for line in output.split('\n')[:5]:
                                    print(self.color(f"     {line}", Colors.BRIGHT_BLACK))
                        
                        # Show lint check results
                        if "lint_check" in result:
                            lint = result["lint_check"]
                            if lint.get("has_errors"):
                                print(self.color(f"   ⚠️  Lint errors detected!", Colors.YELLOW))
                            else:
                                print(self.color(f"   ✓ No lint errors", Colors.GREEN))
                        
                        # Show file operations
                        if "file_path" in result:
                            file_path = result["file_path"]
                            # Shorten path if too long
                            if len(file_path) > 50:
                                file_path = "..." + file_path[-47:]
                            print(self.color(f"   File: {file_path}", Colors.BLUE))
                
                elif event["type"] == "done":
                    print()
                    print(self.color("━" * 80, Colors.BRIGHT_BLACK))
                    print()
                    print(self.color(f"✅ Task completed!", Colors.GREEN))
                    print(self.color(f"   Iterations: {iteration_count}", Colors.DIM))
                    print(self.color(f"   Tool calls: {tool_call_count}", Colors.DIM))
                    print()
                
                elif event["type"] == "error":
                    print()
                    print(self.color("━" * 80, Colors.BRIGHT_BLACK))
                    print()
                    print(self.color(f"❌ Error: {event['error']}", Colors.RED))
                    print()
                
                elif event["type"] == "max_iterations_reached":
                    print()
                    print(self.color("━" * 80, Colors.BRIGHT_BLACK))
                    print()
                    print(self.color(f"⚠️  Reached maximum iterations ({event['max_iterations']})", Colors.YELLOW))
                    print()
        
        except KeyboardInterrupt:
            print()
            print()
            print(self.color("⚠️  Interrupted by user", Colors.YELLOW))
            print()
        except Exception as e:
            print()
            print(self.color(f"❌ Unexpected error: {str(e)}", Colors.RED))
            print()
    
    def get_user_input(self) -> str:
        """Get user input with a nice prompt"""
        try:
            prompt = self.color("You: ", Colors.BOLD + Colors.GREEN)
            return input(prompt).strip()
        except EOFError:
            return "/quit"
        except KeyboardInterrupt:
            print()
            return "/quit"
    
    def run(self):
        """Main CLI loop"""
        # Check if colors are supported
        if not sys.stdout.isatty() or os.getenv('NO_COLOR'):
            self.use_colors = False
        
        # Print header
        self.print_header()
        
        # Initialize agent
        self.initialize_agent()
        
        # Main loop
        while self.running:
            try:
                # Get user input
                user_input = self.get_user_input()
                
                # Skip empty input
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    self.handle_command(user_input)
                    continue
                
                # Run agent
                self.run_agent(user_input)
                
            except KeyboardInterrupt:
                print()
                print()
                confirm = input(self.color("Are you sure you want to quit? (y/n): ", Colors.YELLOW))
                if confirm.lower() in ['y', 'yes']:
                    print()
                    print(self.color("👋 Goodbye!", Colors.CYAN))
                    print()
                    break
                else:
                    print()
                    continue
            except Exception as e:
                print()
                print(self.color(f"❌ Unexpected error: {str(e)}", Colors.RED))
                print()


def main():
    """Entry point"""
    # Check for --no-color flag
    use_colors = '--no-color' not in sys.argv
    
    # Create and run CLI
    cli = CodingAgentCLI(use_colors=use_colors)
    cli.run()


if __name__ == "__main__":
    main()

