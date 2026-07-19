"""Build evaluation dataset from Chinese legal documents"""

import json
import logging
from typing import List, Dict, Any
from pathlib import Path


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LegalDatasetBuilder:
    """Build evaluation dataset for Chinese legal Q&A"""
    
    def __init__(self):
        self.simple_cases = []
        self.complex_cases = []
        
    def create_simple_cases(self) -> List[Dict[str, Any]]:
        """Create simple direct legal questions"""
        simple_cases = [
            {
                "id": "simple_1",
                "question": "故意杀人罪判几年？",
                "expected_keywords": ["死刑", "无期徒刑", "十年以上有期徒刑"],
                "reference": "《中华人民共和国刑法》第二百三十二条",
                "difficulty": "easy"
            },
            {
                "id": "simple_2",
                "question": "盗窃罪的立案标准是什么？",
                "expected_keywords": ["一千元", "三千元", "数额较大"],
                "reference": "《中华人民共和国刑法》第二百六十四条",
                "difficulty": "easy"
            },
            {
                "id": "simple_3", 
                "question": "醉酒驾驶机动车如何处罚？",
                "expected_keywords": ["拘役", "罚金", "吊销驾照"],
                "reference": "《中华人民共和国刑法》第一百三十三条",
                "difficulty": "easy"
            },
            {
                "id": "simple_4",
                "question": "诈骗罪的量刑标准是什么？",
                "expected_keywords": ["三年以下", "三年以上十年以下", "十年以上"],
                "reference": "《中华人民共和国刑法》第二百六十六条",
                "difficulty": "easy"
            },
            {
                "id": "simple_5",
                "question": "故意伤害罪致人重伤的处罚是什么？",
                "expected_keywords": ["三年以上十年以下", "有期徒刑"],
                "reference": "《中华人民共和国刑法》第二百三十四条",
                "difficulty": "easy"
            },
            {
                "id": "simple_6",
                "question": "抢劫罪的加重情节有哪些？",
                "expected_keywords": ["入户抢劫", "多次抢劫", "抢劫数额巨大"],
                "reference": "《中华人民共和国刑法》第二百六十三条",
                "difficulty": "medium"
            },
            {
                "id": "simple_7",
                "question": "非法拘禁罪的构成要件是什么？",
                "expected_keywords": ["非法", "拘禁", "限制人身自由"],
                "reference": "《中华人民共和国刑法》第二百三十八条",
                "difficulty": "medium"
            },
            {
                "id": "simple_8",
                "question": "贪污罪的数额标准如何认定？",
                "expected_keywords": ["三万元", "二十万元", "三百万元"],
                "reference": "《中华人民共和国刑法》第三百八十三条",
                "difficulty": "medium"
            },
            {
                "id": "simple_9",
                "question": "交通肇事罪的立案标准是什么？",
                "expected_keywords": ["死亡一人", "重伤三人", "财产损失"],
                "reference": "《中华人民共和国刑法》第一百三十三条",
                "difficulty": "easy"
            },
            {
                "id": "simple_10",
                "question": "寻衅滋事罪如何处罚？",
                "expected_keywords": ["五年以下", "有期徒刑", "拘役", "管制"],
                "reference": "《中华人民共和国刑法》第二百九十三条",
                "difficulty": "easy"
            }
        ]
        
        return simple_cases
    
    def create_complex_cases(self) -> List[Dict[str, Any]]:
        """Create complex legal scenario questions"""
        complex_cases = [
            {
                "id": "complex_1",
                "question": """张某因与李某发生经济纠纷，持刀闯入李某家中，意图讨债。在争执过程中，张某用刀刺伤李某，
                            导致李某重伤。同时，张某还顺手拿走了李某家中的现金5万元。请问张某的行为应如何定性？
                            可能面临什么样的刑事处罚？""",
                "expected_analysis": ["入户抢劫", "故意伤害", "数罪并罚"],
                "reference": "《刑法》第二百三十四条、第二百六十三条",
                "difficulty": "hard",
                "requires_multi_query": True
            },
            {
                "id": "complex_2",
                "question": """王某系某国有企业财务主管，利用职务之便，通过虚开发票等手段，
                            将公司资金200万元转入其控制的账户。后王某用该资金进行股票投资，
                            获利50万元。案发后，王某主动退还全部赃款。请分析王某的法律责任。""",
                "expected_analysis": ["贪污罪", "挪用公款罪", "自首情节", "退赃"],
                "reference": "《刑法》第三百八十二条、第三百八十四条",
                "difficulty": "hard",
                "requires_multi_query": True
            },
            {
                "id": "complex_3",
                "question": """赵某酒后驾车，在市区超速行驶，撞倒正在过马路的行人陈某，
                            导致陈某当场死亡。赵某见状，驾车逃离现场。第二天，在家人劝说下，
                            赵某到公安机关投案自首。请问赵某涉嫌哪些犯罪？量刑时应考虑哪些因素？""",
                "expected_analysis": ["交通肇事罪", "危险驾驶罪", "逃逸", "自首"],
                "reference": "《刑法》第一百三十三条",
                "difficulty": "hard",
                "requires_multi_query": True
            },
            {
                "id": "complex_4",
                "question": """刘某通过网络平台发布虚假投资信息，声称可以保证高额回报，
                            先后骗取30名投资者共计500万元。其中，刘某将200万元用于个人挥霍，
                            300万元用于归还之前的债务。请问刘某的行为如何定性？可能的量刑是什么？""",
                "expected_analysis": ["诈骗罪", "数额特别巨大", "多人受害"],
                "reference": "《刑法》第二百六十六条",
                "difficulty": "hard",
                "requires_multi_query": True
            },
            {
                "id": "complex_5",
                "question": """孙某与钱某共谋盗窃某商场。孙某负责望风，钱某进入商场实施盗窃。
                            钱某在盗窃过程中被保安发现，为逃跑将保安打成轻伤。
                            最终二人盗窃财物价值8万元。请分析孙某和钱某各自的刑事责任。""",
                "expected_analysis": ["共同犯罪", "盗窃罪", "抢劫罪", "转化犯"],
                "reference": "《刑法》第二百六十四条、第二百六十九条",
                "difficulty": "hard",
                "requires_multi_query": True
            }
        ]
        
        return complex_cases
    
    def build_dataset(self, output_path: str = "legal_qa_dataset.json"):
        """Build and save the complete dataset"""
        dataset = {
            "simple_cases": self.create_simple_cases(),
            "complex_cases": self.create_complex_cases(),
            "metadata": {
                "total_cases": 15,
                "simple_count": 10,
                "complex_count": 5,
                "domain": "Chinese Criminal Law",
                "purpose": "Evaluate agentic vs non-agentic RAG performance"
            }
        }
        
        # Save dataset
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Dataset saved to {output_path}")
        return dataset


def create_legal_documents() -> List[Dict[str, str]]:
    """Create sample legal documents for the knowledge base"""
    documents = [
        {
            "doc_id": "criminal_law_homicide",
            "title": "刑法-故意杀人罪",
            "content": """第二百三十二条 【故意杀人罪】故意杀人的，处死刑、无期徒刑或者十年以上有期徒刑；
            情节较轻的，处三年以上十年以下有期徒刑。
            
            故意杀人罪是指故意非法剥夺他人生命的行为。该罪侵犯的客体是他人的生命权。
            法律依据是《中华人民共和国刑法》第二百三十二条。
            
            量刑标准：
            1. 情节严重的：死刑、无期徒刑或十年以上有期徒刑
            2. 情节较轻的：三年以上十年以下有期徒刑
            
            情节较轻通常包括：防卫过当、义愤杀人、被害人有过错等情形。"""
        },
        {
            "doc_id": "criminal_law_theft",
            "title": "刑法-盗窃罪",
            "content": """第二百六十四条 【盗窃罪】盗窃公私财物，数额较大的，或者多次盗窃、入户盗窃、
            携带凶器盗窃、扒窃的，处三年以下有期徒刑、拘役或者管制，并处或者单处罚金；
            数额巨大或者有其他严重情节的，处三年以上十年以下有期徒刑，并处罚金；
            数额特别巨大或者有其他特别严重情节的，处十年以上有期徒刑或者无期徒刑，并处罚金或者没收财产。
            
            盗窃罪的立案标准：
            1. 数额较大：一般为1000元至3000元以上
            2. 数额巨大：一般为3万元至10万元以上  
            3. 数额特别巨大：一般为30万元至50万元以上
            
            特殊情形：多次盗窃（2年内3次以上）、入户盗窃、携带凶器盗窃、扒窃的，
            不论数额大小，均构成盗窃罪。"""
        },
        {
            "doc_id": "criminal_law_fraud",
            "title": "刑法-诈骗罪",
            "content": """第二百六十六条 【诈骗罪】诈骗公私财物，数额较大的，处三年以下有期徒刑、
            拘役或者管制，并处或者单处罚金；数额巨大或者有其他严重情节的，
            处三年以上十年以下有期徒刑，并处罚金；数额特别巨大或者有其他特别严重情节的，
            处十年以上有期徒刑或者无期徒刑，并处罚金或者没收财产。
            
            诈骗罪的量刑标准：
            1. 数额较大（3千元至1万元以上）：三年以下有期徒刑、拘役或者管制
            2. 数额巨大（3万元至10万元以上）：三年以上十年以下有期徒刑
            3. 数额特别巨大（50万元以上）：十年以上有期徒刑或者无期徒刑
            
            诈骗罪是指以非法占有为目的，用虚构事实或者隐瞒真相的方法，
            骗取数额较大的公私财物的行为。"""
        },
        {
            "doc_id": "criminal_law_robbery",
            "title": "刑法-抢劫罪",
            "content": """第二百六十三条 【抢劫罪】以暴力、胁迫或者其他方法抢劫公私财物的，
            处三年以上十年以下有期徒刑，并处罚金；有下列情形之一的，
            处十年以上有期徒刑、无期徒刑或者死刑，并处罚金或者没收财产：
            
            （一）入户抢劫的；
            （二）在公共交通工具上抢劫的；
            （三）抢劫银行或者其他金融机构的；
            （四）多次抢劫或者抢劫数额巨大的；
            （五）抢劫致人重伤、死亡的；
            （六）冒充军警人员抢劫的；
            （七）持枪抢劫的；
            （八）抢劫军用物资或者抢险、救灾、救济物资的。
            
            抢劫罪的加重处罚情节包括上述八种情形，有其中之一的，
            最低刑期为十年有期徒刑。"""
        },
        {
            "doc_id": "criminal_law_injury",
            "title": "刑法-故意伤害罪",
            "content": """第二百三十四条 【故意伤害罪】故意伤害他人身体的，处三年以下有期徒刑、
            拘役或者管制。犯前款罪，致人重伤的，处三年以上十年以下有期徒刑；
            致人死亡或者以特别残忍手段致人重伤造成严重残疾的，处十年以上有期徒刑、
            无期徒刑或者死刑。
            
            故意伤害罪的量刑：
            1. 故意伤害致人轻伤的：三年以下有期徒刑、拘役或者管制
            2. 故意伤害致人重伤的：三年以上十年以下有期徒刑
            3. 故意伤害致人死亡或特别残忍手段致残的：十年以上有期徒刑、无期徒刑或死刑
            
            重伤标准：使人肢体残废或者毁人容貌；使人丧失听觉、视觉或者其他器官功能；
            其他对于人身健康有重大伤害的。"""
        },
        {
            "doc_id": "criminal_law_traffic",
            "title": "刑法-交通肇事罪与危险驾驶罪",
            "content": """第一百三十三条 【交通肇事罪】违反交通运输管理法规，因而发生重大事故，
            致人重伤、死亡或者使公私财产遭受重大损失的，处三年以下有期徒刑或者拘役；
            交通运输肇事后逃逸或者有其他特别恶劣情节的，处三年以上七年以下有期徒刑；
            因逃逸致人死亡的，处七年以上有期徒刑。
            
            第一百三十三条之一 【危险驾驶罪】在道路上驾驶机动车，有下列情形之一的，
            处拘役，并处罚金：
            （一）追逐竞驶，情节恶劣的；
            （二）醉酒驾驶机动车的；
            （三）从事校车业务或者旅客运输，严重超过额定乘员载客，
                  或者严重超过规定时速行驶的；
            （四）违反危险化学品安全管理规定运输危险化学品，危及公共安全的。
            
            醉酒驾驶的认定标准：血液酒精含量达到80毫克/100毫升以上。"""
        },
        {
            "doc_id": "criminal_law_corruption",
            "title": "刑法-贪污罪",
            "content": """第三百八十二条 【贪污罪】国家工作人员利用职务上的便利，侵吞、窃取、
            骗取或者以其他手段非法占有公共财物的，是贪污罪。
            
            第三百八十三条 【贪污罪的处罚规定】对犯贪污罪的，根据情节轻重，分别依照下列规定处罚：
            
            （一）贪污数额较大或者有其他较重情节的，处三年以下有期徒刑或者拘役，并处罚金。
            （二）贪污数额巨大或者有其他严重情节的，处三年以上十年以下有期徒刑，并处罚金或者没收财产。
            （三）贪污数额特别巨大或者有其他特别严重情节的，处十年以上有期徒刑或者无期徒刑，
                  并处罚金或者没收财产；数额特别巨大，并使国家和人民利益遭受特别重大损失的，
                  处无期徒刑或者死刑，并处没收财产。
            
            贪污数额标准：
            1. 数额较大：三万元以上不满二十万元
            2. 数额巨大：二十万元以上不满三百万元
            3. 数额特别巨大：三百万元以上"""
        }
    ]
    
    return documents


if __name__ == "__main__":
    # Build evaluation dataset
    builder = LegalDatasetBuilder()
    dataset = builder.build_dataset("legal_qa_dataset.json")
    
    print(f"Dataset created with {len(dataset['simple_cases'])} simple cases and {len(dataset['complex_cases'])} complex cases")
    
    # Create legal documents
    documents = create_legal_documents()
    
    # Save documents
    with open("legal_documents.json", 'w', encoding='utf-8') as f:
        json.dump(documents, f, ensure_ascii=False, indent=2)
    
    print(f"Created {len(documents)} legal documents for knowledge base")
