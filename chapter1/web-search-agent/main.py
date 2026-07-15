"""
主程序 - Web Search Agent 使用示例
"""

import sys
import logging
from typing import Optional
from agent import WebSearchAgent
from config import Config

# 设置日志
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger(__name__)


def run_interactive_mode(agent: WebSearchAgent):
    """
    交互式模式 - 持续与 Agent 对话
    
    Args:
        agent: WebSearchAgent 实例
    """
    print("\n" + "="*60)
    print("🤖 Kimi Web Search Agent - 交互模式")
    print("="*60)
    print("输入您的问题，Agent 将自动搜索并回答")
    print("输入 'quit' 或 'exit' 退出")
    print("输入 'clear' 清空对话历史")
    print("="*60 + "\n")
    
    while True:
        try:
            # 获取用户输入
            user_input = input("您的问题: ").strip()
            
            # 检查退出命令
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 再见！")
                break
            
            # 检查清空命令
            if user_input.lower() == 'clear':
                agent.clear_history()
                print("✅ 对话历史已清空\n")
                continue
            
            # 检查空输入
            if not user_input:
                print("❌ 请输入一个问题\n")
                continue
            
            # 显示思考中
            print("\n🔍 Agent 正在搜索和思考...")
            
            # 获取答案
            answer = agent.search_and_answer(user_input)
            
            # 显示答案
            print("\n" + "="*60)
            print("📝 Agent 回答:")
            print("-"*60)
            print(answer)
            print("="*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 检测到中断，退出程序")
            break
        except Exception as e:
            logger.error(f"处理问题时出错: {str(e)}")
            print(f"\n❌ 出错了: {str(e)}\n")


def run_single_question(agent: WebSearchAgent, question: str):
    """
    单个问题模式 - 回答一个问题后退出
    
    Args:
        agent: WebSearchAgent 实例
        question: 要回答的问题
    """
    print("\n" + "="*60)
    print("🤖 Kimi Web Search Agent")
    print("="*60)
    print(f"问题: {question}")
    print("-"*60)
    print("🔍 搜索中...")
    
    try:
        answer = agent.search_and_answer(question)
        print("\n📝 答案:")
        print("-"*60)
        print(answer)
        print("="*60 + "\n")
    except Exception as e:
        logger.error(f"处理问题时出错: {str(e)}")
        print(f"\n❌ 出错了: {str(e)}\n")


def main(api_key: Optional[str] = None):
    """
    主函数
    
    Args:
        api_key: 可选的 API key
    """
    # 验证配置
    if not api_key and not Config.validate():
        sys.exit(1)
    
    # 创建 Agent
    try:
        agent = WebSearchAgent(
            api_key=Config.get_api_key(api_key),
            base_url=Config.KIMI_BASE_URL
        )
        logger.info("Agent 初始化成功")
    except Exception as e:
        logger.error(f"Agent 初始化失败: {str(e)}")
        sys.exit(1)
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        # 如果有参数，将其作为问题
        question = " ".join(sys.argv[1:])
        run_single_question(agent, question)
    else:
        # 否则进入交互模式
        run_interactive_mode(agent)


if __name__ == "__main__":
    # 示例问题列表
    example_questions = [
        "Nano Banana 是什么？",
        "今天北京的天气怎么样？",
        "今天比特币的价格是多少？",
    ]
    
    # 如果没有提供 API key，显示使用说明
    if not Config.MOONSHOT_API_KEY and len(sys.argv) == 1:
        print("\n" + "="*60)
        print("📚 使用说明")
        print("="*60)
        print("\n1. 设置 API Key:")
        print("   export MOONSHOT_API_KEY='your-api-key'")
        print("   (或使用: export KIMI_API_KEY='your-api-key')")
        print("\n2. 运行程序:")
        print("   python main.py                    # 交互模式")
        print("   python main.py '你的问题'         # 单次问答")
        print("\n3. 示例问题:")
        for i, q in enumerate(example_questions, 1):
            print(f"   {i}. {q}")
        print("\n" + "="*60)
        sys.exit(0)
    
    # 运行主程序
    main()
