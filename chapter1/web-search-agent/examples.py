"""
高级示例 - 展示 Web Search Agent 的各种用法
"""

import asyncio
import json
from typing import List, Dict, Any
from agent import WebSearchAgent
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedWebSearchAgent(WebSearchAgent):
    """
    高级 Web Search Agent - 扩展功能
    """
    
    def batch_search(self, questions: List[str]) -> List[Dict[str, str]]:
        """
        批量搜索多个问题
        
        Args:
            questions: 问题列表
            
        Returns:
            答案列表
        """
        results = []
        for i, question in enumerate(questions, 1):
            logger.info(f"处理问题 {i}/{len(questions)}: {question}")
            try:
                answer = self.search_and_answer(question)
                results.append({
                    "question": question,
                    "answer": answer,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "question": question,
                    "answer": str(e),
                    "status": "error"
                })
            # 清空历史，避免上下文混淆
            self.clear_history()
        return results
    
    def search_with_context(self, question: str, context: str) -> str:
        """
        带上下文的搜索
        
        Args:
            question: 用户问题
            context: 额外的上下文信息
            
        Returns:
            答案
        """
        # 构建带上下文的问题
        contextualized_question = f"""
背景信息：{context}

基于上述背景，请回答以下问题：
{question}
"""
        return self.search_and_answer(contextualized_question)
    
    def comparative_search(self, items: List[str], aspect: str) -> str:
        """
        比较搜索 - 搜索并比较多个项目
        
        Args:
            items: 要比较的项目列表
            aspect: 比较的方面
            
        Returns:
            比较结果
        """
        # 构建比较问题
        items_str = "、".join(items)
        question = f"请搜索并比较 {items_str} 在 {aspect} 方面的差异和优劣"
        
        return self.search_and_answer(question)
    
    def fact_check(self, statement: str) -> Dict[str, Any]:
        """
        事实核查 - 验证陈述的真实性
        
        Args:
            statement: 需要验证的陈述
            
        Returns:
            验证结果
        """
        question = f"""
请验证以下陈述的真实性：
"{statement}"

请提供：
1. 这个陈述是否准确（真/假/部分真实）
2. 相关的事实和证据
3. 信息来源
"""
        answer = self.search_and_answer(question)
        
        # 简单解析结果
        is_true = "真" in answer[:100]
        return {
            "statement": statement,
            "is_true": is_true,
            "explanation": answer
        }


def example_basic_search():
    """基础搜索示例"""
    print("\n" + "="*60)
    print("📌 示例 1: 基础搜索")
    print("="*60)
    
    agent = WebSearchAgent(Config.get_api_key())
    
    questions = [
        "OpenAI 最新发布的 GPT 模型有什么特点？",
        "如何学习机器学习？推荐一些资源",
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        print("-"*40)
        answer = agent.search_and_answer(q)
        print(f"答案: {answer}")


def example_batch_search():
    """批量搜索示例"""
    print("\n" + "="*60)
    print("📌 示例 2: 批量搜索")
    print("="*60)
    
    agent = AdvancedWebSearchAgent(Config.get_api_key())
    
    questions = [
        "React 和 Vue 的主要区别是什么？",
        "Python 最适合做什么类型的项目？",
        "如何开始学习人工智能？",
    ]
    
    results = agent.batch_search(questions)
    
    for result in results:
        print(f"\n问题: {result['question']}")
        print(f"状态: {result['status']}")
        print(f"答案: {result['answer'][:200]}...")  # 只显示前200字符


def example_contextual_search():
    """带上下文的搜索示例"""
    print("\n" + "="*60)
    print("📌 示例 3: 带上下文的搜索")
    print("="*60)
    
    agent = AdvancedWebSearchAgent(Config.get_api_key())
    
    context = "我是一个刚开始学习编程的大学生，主要对 Web 开发感兴趣"
    question = "我应该先学习哪种编程语言？"
    
    print(f"上下文: {context}")
    print(f"问题: {question}")
    print("-"*40)
    
    answer = agent.search_with_context(question, context)
    print(f"答案: {answer}")


def example_comparative_search():
    """比较搜索示例"""
    print("\n" + "="*60)
    print("📌 示例 4: 比较搜索")
    print("="*60)
    
    agent = AdvancedWebSearchAgent(Config.get_api_key())
    
    # 比较不同的技术框架
    items = ["TensorFlow", "PyTorch", "JAX"]
    aspect = "性能和易用性"
    
    print(f"比较项目: {', '.join(items)}")
    print(f"比较方面: {aspect}")
    print("-"*40)
    
    result = agent.comparative_search(items, aspect)
    print(f"比较结果:\n{result}")


def example_fact_check():
    """事实核查示例"""
    print("\n" + "="*60)
    print("📌 示例 5: 事实核查")
    print("="*60)
    
    agent = AdvancedWebSearchAgent(Config.get_api_key())
    
    statements = [
        "Python 是世界上最流行的编程语言",
        "量子计算机已经可以破解所有现代加密算法",
        "GPT-4 有 1.76 万亿个参数",
    ]
    
    for statement in statements:
        print(f"\n陈述: {statement}")
        result = agent.fact_check(statement)
        print(f"真实性: {'✅ 真' if result['is_true'] else '❌ 假/存疑'}")
        print(f"解释: {result['explanation'][:200]}...")


def example_research_assistant():
    """研究助手示例 - 深度研究某个主题"""
    print("\n" + "="*60)
    print("📌 示例 6: 研究助手 - 深度研究")
    print("="*60)
    
    agent = AdvancedWebSearchAgent(Config.get_api_key())
    
    topic = "大语言模型的发展历程"
    
    # 构建研究问题序列
    research_questions = [
        f"什么是{topic}？请提供详细定义",
        f"{topic}的关键里程碑和重要事件有哪些？",
        f"{topic}面临的主要挑战是什么？",
        f"{topic}的未来发展趋势如何？",
    ]
    
    print(f"研究主题: {topic}")
    print("="*60)
    
    research_report = []
    for i, q in enumerate(research_questions, 1):
        print(f"\n研究问题 {i}: {q}")
        print("-"*40)
        answer = agent.search_and_answer(q)
        research_report.append({
            "section": i,
            "question": q,
            "findings": answer
        })
        print(f"发现: {answer[:300]}...")
        agent.clear_history()  # 清空历史，确保每个问题独立
    
    # 保存研究报告
    with open("research_report.json", "w", encoding="utf-8") as f:
        json.dump(research_report, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 研究报告已保存到 research_report.json")


def main():
    """运行所有示例"""
    
    if not Config.validate():
        print("请先设置 KIMI_API_KEY 环境变量")
        return
    
    examples = [
        ("基础搜索", example_basic_search),
        ("批量搜索", example_batch_search),
        ("带上下文搜索", example_contextual_search),
        ("比较搜索", example_comparative_search),
        ("事实核查", example_fact_check),
        ("研究助手", example_research_assistant),
    ]
    
    print("\n" + "="*60)
    print("🎯 Kimi Web Search Agent - 高级示例")
    print("="*60)
    print("\n选择要运行的示例:")
    
    for i, (name, _) in enumerate(examples, 1):
        print(f"{i}. {name}")
    print(f"{len(examples) + 1}. 运行所有示例")
    print("0. 退出")
    
    try:
        choice = input("\n请输入选项 (0-7): ").strip()
        choice = int(choice)
        
        if choice == 0:
            print("退出程序")
            return
        elif 1 <= choice <= len(examples):
            examples[choice - 1][1]()
        elif choice == len(examples) + 1:
            for name, func in examples:
                try:
                    func()
                except Exception as e:
                    logger.error(f"运行 {name} 时出错: {str(e)}")
        else:
            print("无效的选项")
    except ValueError:
        print("请输入有效的数字")
    except KeyboardInterrupt:
        print("\n程序被中断")
    except Exception as e:
        logger.error(f"运行示例时出错: {str(e)}")


if __name__ == "__main__":
    main()
