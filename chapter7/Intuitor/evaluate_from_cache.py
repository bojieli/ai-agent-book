#!/usr/bin/env python3
"""
从 lighteval 缓存的 parquet 文件中提取答案并计算 GSM8K 准确率
支持 \\boxed{} 和 #### 两种答案格式
"""

import re
import pandas as pd
import argparse
from pathlib import Path
from typing import Optional


def extract_answer_from_boxed(text: str) -> Optional[str]:
    """从 \\boxed{} 格式中提取答案（同时支持 \\(\\boxed{}\\) 形式）"""
    if not text:
        return None
    
    # 如果是 bytes，转换为字符串
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    # 确保是字符串
    text = str(text)
    
    # 匹配 \\boxed{number}，这个模式同时匹配 \boxed{} 和 \(\boxed{}\)
    match = re.search(r'\\boxed\{([^}]+)\}', text)
    if match:
        return match.group(1).strip()
    
    return None


def extract_answer_from_gsm8k_format(text: str) -> Optional[str]:
    """从 #### number 格式中提取答案"""
    if not text:
        return None
    
    # 如果是 bytes，转换为字符串
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    # 确保是字符串
    text = str(text)
    
    if "####" in text:
        parts = text.split("####")
        if len(parts) > 1:
            return parts[1].strip()
    
    return None


def normalize_number(text: str) -> Optional[str]:
    """标准化数字格式：去除逗号、空格、LaTeX 符号等"""
    if not text:
        return None
    
    # 如果是 bytes，转换为字符串
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    # 确保是字符串
    text = str(text)
    
    # 去除 LaTeX 符号
    text = text.replace("\\,", "")
    text = text.replace("\\text", "")
    text = text.replace("{", "").replace("}", "")
    
    # 去除逗号和空格
    text = text.replace(",", "").replace(" ", "")
    
    # 提取数字（包括小数和负数）
    match = re.search(r'-?\d+\.?\d*', text)
    if match:
        num_str = match.group(0)
        # 转换为浮点数再转回字符串，以标准化格式
        try:
            num = float(num_str)
            # 如果是整数，返回整数格式
            if num.is_integer():
                return str(int(num))
            else:
                return str(num)
        except ValueError:
            return None
    
    return None


def extract_and_normalize_answer(text: str) -> Optional[str]:
    """从模型输出中提取并标准化答案"""
    if not text:
        return None
    
    # 如果是 bytes，转换为字符串
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    # 确保是字符串
    text = str(text)
    
    # 先尝试提取 boxed 格式
    answer = extract_answer_from_boxed(text)
    
    # 如果没找到，尝试 GSM8K 格式
    if not answer:
        answer = extract_answer_from_gsm8k_format(text)
    
    # 如果还是没找到，尝试从最后一句话提取数字
    if not answer:
        # 取最后 200 个字符，避免提取到过程中的数字
        last_part = text[-200:] if len(text) > 200 else text
        answer = last_part
    
    # 标准化数字格式
    return normalize_number(answer)


def load_gsm8k_answers(split: str = "test") -> dict:
    """加载 GSM8K 数据集的金标答案
    
    返回一个字典，键是数据集中的原始索引（0-1318），值是标准化后的答案
    """
    try:
        from datasets import load_dataset
        dataset = load_dataset("gsm8k", "main", split=split)
        
        answers = {}
        # 注意：这里的索引是数据集中的顺序索引，不是 sample_id
        for idx in range(len(dataset)):
            item = dataset[idx]
            # GSM8K 答案格式：计算过程\n#### 答案
            gold_answer = item["answer"]
            # 提取 #### 后面的数字
            normalized = extract_answer_from_gsm8k_format(gold_answer)
            if normalized:
                normalized = normalize_number(normalized)
            answers[idx] = normalized
        
        print(f"✅ 加载了 {len(answers)} 个金标答案")
        return answers
    except ImportError:
        print("❌ 错误：需要安装 datasets 库")
        print("运行：pip install datasets")
        return {}
    except Exception as e:
        print(f"❌ 加载金标答案时出错: {e}")
        return {}


def evaluate_from_parquet(parquet_path: str, verbose: bool = False):
    """从 parquet 文件评测"""
    print(f"📂 读取预测结果: {parquet_path}")
    df = pd.read_parquet(parquet_path)
    
    print(f"📊 总样本数: {len(df)}")
    
    # 加载金标答案
    print("📥 加载 GSM8K 金标答案...")
    gold_answers = load_gsm8k_answers()
    
    if not gold_answers:
        print("❌ 无法加载金标答案，退出")
        return
    
    # 评测
    correct = 0
    total = 0
    errors = []
    
    # 调试：显示前几个 sample_id
    if verbose:
        print(f"\n前 5 个 sample_id: {df['sample_id'].head().tolist()}")
        print(f"金标答案的键范围: {min(gold_answers.keys()) if gold_answers else 'N/A'} - {max(gold_answers.keys()) if gold_answers else 'N/A'}")
    
    for idx, row in df.iterrows():
        sample_id = row['sample_id']
        sample_data = row['sample']
        
        # 转换 sample_id 为整数（如果它是字符串）
        if isinstance(sample_id, str):
            try:
                sample_id = int(sample_id)
            except ValueError:
                if verbose:
                    print(f"⚠️  样本 {sample_id}: 无法转换为整数")
                continue
        
        # 提取模型输出
        model_output = sample_data.get('text', [''])[0] if isinstance(sample_data.get('text'), list) else sample_data.get('text', '')
        
        # 确保 model_output 是字符串
        if isinstance(model_output, bytes):
            model_output = model_output.decode('utf-8', errors='ignore')
        model_output = str(model_output) if model_output else ''
        
        # 提取并标准化答案
        pred_answer = extract_and_normalize_answer(model_output)
        gold_answer = gold_answers.get(sample_id)
        
        if gold_answer is None:
            if verbose and idx < 5:
                print(f"⚠️  样本 {sample_id}: 找不到金标答案")
            continue
        
        total += 1
        is_correct = pred_answer == gold_answer
        
        if is_correct:
            correct += 1
        else:
            errors.append({
                'sample_id': sample_id,
                'predicted': pred_answer,
                'gold': gold_answer,
                'output': model_output[:200] + "..." if len(model_output) > 200 else model_output
            })
        
        if verbose and idx < 5:
            print(f"\n样本 {sample_id}:")
            print(f"  预测: {pred_answer}")
            print(f"  金标: {gold_answer}")
            print(f"  正确: {'✅' if is_correct else '❌'}")
    
    # 计算准确率
    accuracy = correct / total * 100 if total > 0 else 0
    
    print("\n" + "="*80)
    print("📈 评测结果")
    print("="*80)
    print(f"总样本数: {total}")
    print(f"正确数量: {correct}")
    print(f"错误数量: {total - correct}")
    print(f"准确率: {accuracy:.2f}%")
    print("="*80)
    
    # 显示部分错误样本
    if errors and verbose:
        print("\n❌ 前 10 个错误样本:")
        for i, error in enumerate(errors[:10], 1):
            print(f"\n{i}. 样本 {error['sample_id']}:")
            print(f"   预测: {error['predicted']}")
            print(f"   金标: {error['gold']}")
            print(f"   输出: {error['output']}")
    
    return {
        'total': total,
        'correct': correct,
        'accuracy': accuracy,
        'errors': errors
    }


def main():
    parser = argparse.ArgumentParser(description='从 lighteval 缓存评测 GSM8K 结果')
    parser.add_argument('parquet_file', type=str, help='Parquet 文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='显示详细信息和错误样本')
    parser.add_argument('-o', '--output', type=str, help='保存结果到 JSON 文件')
    
    args = parser.parse_args()
    
    if not Path(args.parquet_file).exists():
        print(f"❌ 错误：文件不存在: {args.parquet_file}")
        return
    
    results = evaluate_from_parquet(args.parquet_file, verbose=args.verbose)
    
    if args.output and results:
        import json
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 结果已保存到: {args.output}")


if __name__ == "__main__":
    main()

