"""
Kimi Web Search Agent
一个基于 Kimi API 的智能搜索 Agent，能够理解用户问题，通过搜索引擎获取信息，并总结出答案。
"""

import json
from typing import List, Dict, Any, Optional
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
import logging
import os

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def search_impl(arguments: Dict[str, Any]) -> Any:
    """
    When using the search tool provided by Moonshot AI, you just need to return the arguments as they are,
    without any additional processing logic.
 
    But if you want to use other models and keep the internet search functionality, you just need to modify 
    the implementation here (for example, calling search and fetching web page content), the function signature 
    remains the same and still works.
 
    This ensures maximum compatibility, allowing you to switch between different models without making 
    destructive changes to the code.
    """
    return arguments


class WebSearchAgent:
    """
    Web Search Agent - 使用 Kimi API 的内置搜索工具
    
    根据官方文档: https://platform.moonshot.ai/docs/guide/use-web-search
    Kimi 提供了内置的 $web_search 工具
    """
    
    def __init__(self, api_key: str = None, base_url: str = "https://api.moonshot.cn/v1"):
        """
        初始化 Agent
        
        Args:
            api_key: Kimi API key (如果不提供，从环境变量获取)
            base_url: API 基础 URL
        """
        # 优先使用传入的 api_key，否则从环境变量获取
        api_key = api_key or os.environ.get("MOONSHOT_API_KEY")
        if not api_key:
            raise ValueError("API key is required. Set MOONSHOT_API_KEY environment variable or pass api_key parameter.")
        
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model = "kimi-k2-0905-preview"
        self.conversation_history = []
        self.temperature = 0.6
        
    def _get_tools(self) -> List[Dict[str, Any]]:
        """
        定义可用的工具
        根据 Kimi 文档，$web_search 是内置工具
        """
        return [
            {
                "type": "builtin_function",
                "function": {
                    "name": "$web_search",
                }
            }
        ]
    
    def _get_system_prompt(self) -> str:
        """
        获取系统提示
        """
        return f"""你是 Kimi，一个智能搜索助手。

请按照以下步骤处理：
1. 分析用户问题，识别关键信息需求
2. 使用 $web_search 工具搜索相关信息
3. 如果需要更多信息，可以多次调用搜索工具
4. 综合所有信息，生成准确、全面的答案

注意：
- 搜索时使用精准的关键词
- 优先获取最新、最权威的信息
- 答案要结构清晰，有理有据
"""
    
    def _chat(self, messages: List[Dict[str, Any]]) -> Choice:
        """
        调用 Kimi API 进行对话
        
        Args:
            messages: 消息列表
            
        Returns:
            API 响应的 Choice 对象
        """
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            tools=self._get_tools()
        )
        return completion.choices[0]

    def search_and_answer(self, user_question: str, max_iterations: int = 5) -> str:
        """
        执行搜索并生成答案
        
        Args:
            user_question: 用户问题
            max_iterations: 最大搜索迭代次数（防止无限循环）
            
        Returns:
            最终答案
        """
        # 构建系统提示
        system_prompt = self._get_system_prompt()
        
        # 重置对话历史并添加新的系统提示
        self.conversation_history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_question}
        ]
        logger.info("开始调用 Kimi 搜索工具...")

        try:
            finish_reason = None
            iteration = 0
            
            # 循环处理，直到获得最终答案或达到最大迭代次数
            while (finish_reason is None or finish_reason == "tool_calls") and iteration < max_iterations:
                iteration += 1
                logger.info(f"迭代 {iteration}/{max_iterations}")
                
                # 调用 Kimi API
                choice = self._chat(self.conversation_history)
                finish_reason = choice.finish_reason
                
                if finish_reason == "tool_calls":
                    # 处理工具调用
                    logger.info(f"模型请求调用 {len(choice.message.tool_calls)} 个工具")
                    
                    # 添加助手的消息（包含工具调用）到历史
                    self.conversation_history.append(choice.message)
                    
                    # 执行每个工具调用
                    for tool_call in choice.message.tool_calls:
                        tool_call_name = tool_call.function.name
                        tool_call_arguments = json.loads(tool_call.function.arguments)
                        
                        logger.info(f"执行工具: {tool_call_name}, 参数: {tool_call_arguments}")
                        
                        if tool_call_name == "$web_search":
                            # 调用搜索实现
                            tool_result = search_impl(tool_call_arguments)
                        else:
                            tool_result = f"Error: unable to find tool by name '{tool_call_name}'"
                        
                        # 构建工具响应消息并添加到历史
                        self.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call_name,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })
                else:
                    # 获得最终答案
                    if choice.message.content:
                        answer = choice.message.content
                        logger.info("成功生成答案")
                        
                        # 添加最终答案到历史
                        self.conversation_history.append({
                            "role": "assistant",
                            "content": answer
                        })
                        
                        return answer
            
            # 如果达到最大迭代次数仍未完成
            if iteration >= max_iterations:
                logger.warning(f"达到最大迭代次数 {max_iterations}")
                return "抱歉，搜索过程超过了最大迭代次数，请稍后重试。"
            
            return "抱歉，我无法获取足够的信息来回答您的问题。"
                
        except Exception as e:
            logger.error(f"搜索过程中出现错误: {str(e)}")
            return f"搜索过程中出现错误: {str(e)}"
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []
        logger.info("对话历史已清空")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.conversation_history
    
    def set_temperature(self, temperature: float):
        """
        设置温度参数
        
        Args:
            temperature: 温度值 (0.0 - 2.0)
        """
        if 0.0 <= temperature <= 2.0:
            self.temperature = temperature
            logger.info(f"温度设置为: {temperature}")
        else:
            logger.warning(f"无效的温度值: {temperature}，应在 0.0 到 2.0 之间")


# 独立运行示例
def main():
    """
    独立运行示例，演示基本用法
    """
    # 设置 API key (确保已设置环境变量 MOONSHOT_API_KEY)
    agent = WebSearchAgent()
    
    # 示例问题
    test_question = "请搜索 Moonshot AI Context Caching 技术，告诉我这是什么。"
    
    print(f"问题: {test_question}")
    print("-" * 60)
    print("搜索中...")
    
    # 获取答案
    answer = agent.search_and_answer(test_question)
    
    print("\n答案:")
    print("-" * 60)
    print(answer)


if __name__ == '__main__':
    main()