#!/usr/bin/env python3
"""
快速开始脚本 - 一键体验 Kimi Web Search Agent
"""

import os
import sys
from agent import WebSearchAgent
from config import Config

# 彩色输出
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color):
    """打印彩色文本"""
    print(f"{color}{text}{Colors.END}")


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════╗
║         🤖 Kimi Web Search Agent - 快速体验              ║
║                                                          ║
║  基于 Kimi API 的智能搜索助手                             ║
║  能够自动搜索网络信息并生成智能答案                         ║
╚══════════════════════════════════════════════════════════╝
"""
    print_colored(banner, Colors.CYAN)


def check_api_key():
    """检查 API Key 配置"""
    api_key = os.getenv("MOONSHOT_API_KEY")
    if not api_key:
        # 向后兼容：尝试旧的环境变量名
        api_key = os.getenv("KIMI_API_KEY")
    
    if not api_key:
        print_colored("\n⚠️  未检测到 API Key", Colors.WARNING)
        print("\n请按以下步骤配置:")
        print("1. 访问 https://platform.moonshot.ai/ 获取 API Key")
        print("2. 设置环境变量:")
        print("   export MOONSHOT_API_KEY='your-api-key'")
        print("   (或使用: export KIMI_API_KEY='your-api-key')")
        print("\n或者直接输入 API Key (输入 'skip' 跳过):")
        
        user_input = input("> ").strip()
        
        if user_input.lower() == 'skip':
            return None
        elif user_input:
            return user_input
        else:
            return None
    
    print_colored("✅ API Key 已配置", Colors.GREEN)
    return api_key


def demo_search(agent):
    """演示搜索功能"""
    print_colored("\n📝 演示搜索功能", Colors.HEADER)
    print("-" * 60)
    
    demo_questions = [
        "OpenAI 最新发布了什么产品？",
        "2024年有哪些重要的AI突破？",
        "如何开始学习机器学习？",
    ]
    
    print("选择一个演示问题，或输入您自己的问题:")
    for i, q in enumerate(demo_questions, 1):
        print(f"{i}. {q}")
    print("0. 输入自定义问题")
    
    choice = input("\n请选择 (0-3): ").strip()
    
    try:
        choice = int(choice)
        if choice == 0:
            question = input("请输入您的问题: ").strip()
            if not question:
                print_colored("❌ 问题不能为空", Colors.FAIL)
                return
        elif 1 <= choice <= len(demo_questions):
            question = demo_questions[choice - 1]
        else:
            print_colored("❌ 无效的选择", Colors.FAIL)
            return
    except ValueError:
        print_colored("❌ 请输入数字", Colors.FAIL)
        return
    
    print_colored(f"\n🔍 正在搜索: {question}", Colors.BLUE)
    print("请稍候，Agent 正在搜索和分析...")
    print("-" * 60)
    
    try:
        answer = agent.search_and_answer(question)
        print_colored("\n📖 Agent 回答:", Colors.GREEN)
        print(answer)
    except Exception as e:
        print_colored(f"\n❌ 搜索失败: {str(e)}", Colors.FAIL)


def interactive_mode(agent):
    """交互模式"""
    print_colored("\n💬 进入交互模式", Colors.HEADER)
    print("您可以连续提问，输入 'quit' 退出")
    print("-" * 60)
    
    while True:
        question = input("\n您的问题: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print_colored("👋 感谢使用！", Colors.GREEN)
            break
        
        if not question:
            continue
        
        print_colored("🔍 搜索中...", Colors.BLUE)
        
        try:
            answer = agent.search_and_answer(question)
            print_colored("\n📖 回答:", Colors.GREEN)
            print(answer)
        except Exception as e:
            print_colored(f"❌ 错误: {str(e)}", Colors.FAIL)


def main():
    """主函数"""
    print_banner()
    
    # 检查 API Key
    api_key = check_api_key()
    if not api_key:
        print_colored("\n⚠️  无法继续，需要配置 API Key", Colors.WARNING)
        sys.exit(1)
    
    # 创建 Agent
    try:
        print_colored("\n🚀 初始化 Agent...", Colors.BLUE)
        agent = WebSearchAgent(api_key=api_key)
        print_colored("✅ Agent 已就绪", Colors.GREEN)
    except Exception as e:
        print_colored(f"❌ 初始化失败: {str(e)}", Colors.FAIL)
        sys.exit(1)
    
    # 选择模式
    print("\n选择使用模式:")
    print("1. 演示搜索 (快速体验)")
    print("2. 交互模式 (连续对话)")
    print("3. 退出")
    
    mode = input("\n请选择 (1-3): ").strip()
    
    if mode == "1":
        demo_search(agent)
        # 询问是否继续
        cont = input("\n是否进入交互模式？(y/n): ").strip().lower()
        if cont == 'y':
            interactive_mode(agent)
    elif mode == "2":
        interactive_mode(agent)
    elif mode == "3":
        print_colored("👋 再见！", Colors.GREEN)
    else:
        print_colored("❌ 无效的选择", Colors.FAIL)
    
    print_colored("\n感谢使用 Kimi Web Search Agent！", Colors.CYAN)
    print("更多功能请查看:")
    print("- README.md: 完整文档")
    print("- examples.py: 高级示例")
    print("- main.py: 主程序")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\n\n👋 程序被中断", Colors.WARNING)
    except Exception as e:
        print_colored(f"\n❌ 发生错误: {str(e)}", Colors.FAIL)
        sys.exit(1)
