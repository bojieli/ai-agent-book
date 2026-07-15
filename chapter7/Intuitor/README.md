# Intuitor: 无需外部奖励的推理学习

基于论文：[Learning to Reason without External Rewards](https://arxiv.org/pdf/2505.19590)

[论文链接](https://arxiv.org/abs/2505.19590) | [Hugging Face](https://huggingface.co/collections/sunblaze-ucb/intuitor-676e1dc23b2d64a88b0b0b79)

## 📖 项目简介

Intuitor 是一种创新的强化学习方法，它使用**自我确定性（self-certainty）**——即模型自身的内部置信度——作为唯一的奖励信号来微调大语言模型（LLM）。这一方法建立在一个全新的训练范式之上：**内部反馈强化学习（Reinforcement Learning from Internal Feedback, RLIF）**。

### 🌊 LLM 能力提升的三条曲线

Intuitor 代表了大语言模型能力提升的**第三条曲线**：

#### 🔵 第一曲线：预训练（Pre-training）
- **核心**：在海量无标注文本上进行自监督学习
- **目标**：学习语言的统计规律和世界知识
- **代表**：GPT-3/4、LLaMA、Qwen 等基座模型
- **局限**：缺乏目标导向，难以完成复杂推理任务

#### 🟢 第二曲线：可验证奖励强化学习（RLVR）
- **核心**：使用可自动验证的奖励信号（如答案正确性、代码执行结果）
- **目标**：在特定领域（数学、代码）提升推理能力
- **代表**：DeepSeek-R1、OpenAI o1、Kimi K1.5、MiMo
- **局限**：
  - ❌ 需要金标答案或测试用例
  - ❌ 仅适用于有明确正确答案的任务（数学、代码、科学问题）
  - ❌ 现实世界的**大多数任务没有明确的 reward function**：
    - 写作质量如何量化？
    - 创意设计的好坏如何自动评估？
    - 对话是否有趣、有帮助如何验证？
    - 决策是否合理如何在事前判断？

#### 🔴 第三曲线：无监督强化学习（Unsupervised RL）✨ **Intuitor 所在的曲线**
- **核心**：无需金标答案或人工偏好标注，通过各种自动化信号进行强化学习
- **目标**：为无明确奖励函数的任务提供训练方法
- **代表方法**：
  - **内部反馈（Internal Feedback）**：Intuitor（self-certainty）
  - **规则奖励（Rubrics-based）**：基于预定义规则或评分标准
  - **新颖性（Novelty-based）**：鼓励探索未知区域
  - **多智能体辩论（Multi-agent Debate）**：通过讨论达成共识
- **优势**：
  - ✅ 完全无监督，无需标注数据
  - ✅ 适用于**任意任务**，包括无明确对错的任务
  - ✅ 更强的**跨领域泛化能力**
  - ✅ 为现实世界 90% 的任务提供解决方案

### 🧭 什么是 RLIF？

**RLIF（Reinforcement Learning from Internal Feedback）** 是本文提出的一种**无监督强化学习**方法，属于第三曲线的一种实现方式。

RLIF 的核心思想是：语言模型通过优化**内在信号**（如自我置信度、内部一致性）来自我提升，无需任何外部奖励、标准答案或验证器。

#### RLIF 在无监督 RL 生态中的定位

```
第三曲线：无监督强化学习（Unsupervised RL）
├─ 内部反馈（Internal Feedback）
│  └─ RLIF（本文方法）：使用 self-certainty 作为奖励
├─ 一致性（Consistency）
│  ├─ TTRL：使用 plurality voting
│  └─ Self-consistency：多次采样的一致性
├─ 规则奖励（Rubrics-based）
│  └─ 基于预定义评分标准
├─ 新颖性（Novelty-based）
│  └─ 鼓励探索未知区域
└─ 多智能体（Multi-agent）
   └─ 通过辩论或协作产生奖励
```

#### 三条曲线的本质

- **第一曲线（Pretrain）**：学什么？→ 知识获取
- **第二曲线（RLVR）**：怎么对？→ 特定任务的正确性
- **第三曲线（Unsupervised RL）**：怎么好？→ 无监督的通用质量提升

第三曲线使得 LLM 能够在人类反馈或可验证监督昂贵或不可用的场景下，实现可扩展且领域无关的微调。这对于未来 AI 系统在开放式、创造性、主观性任务上的发展至关重要。

### 💡 Intuitor 的核心思想

Intuitor 通过使用**自我确定性（Self-Certainty）**作为内在奖励，在 GRPO（Group Relative Policy Optimization）策略优化算法中实现了 RLIF。

**核心观察**：大语言模型在面对困难问题时通常表现出较低的置信度，而在熟悉任务上则展现更高的确定性。通过优化模型自身的置信度，可以引导模型学习更有效的推理路径，从而提升推理能力。

---

### ⚡ 为什么 Intuitor 如此重要？

#### 🎯 核心突破

Intuitor 不仅仅是"又一个推理模型"，它代表了 LLM 能力提升的**范式转变**：

```
第一曲线（Pretrain）          → 学习"是什么"（知识）
第二曲线（RLVR）              → 学习"对不对"（数学、代码的正确性）
第三曲线（Unsupervised RL）   → 学习"好不好"（通用质量提升）
  └─ Intuitor 使用内部反馈（self-certainty）实现
```

#### 🔥 现实痛点

**第二曲线的天花板**：
- DeepSeek-R1、o1 等模型在数学/代码上已接近人类专家
- 但这只占现实任务的 **< 10%**
- 90% 的任务**没有明确的对错标准**：
  - 📝 写作：什么样的文章算"好"？
  - 💬 对话：什么样的回复算"有帮助"？
  - 🎨 创意：什么样的设计算"优秀"？
  - 🤔 决策：什么样的策略算"合理"？

**Intuitor 的解决方案**：
- ✅ 不依赖外部评判标准
- ✅ 通过优化内在一致性提升质量
- ✅ 适用于**任意领域**，只需一个 prompt

#### 💪 实验证明

| 指标 | 结果 | 意义 |
|-----|------|-----|
| **数学（MATH500）** | 61.2% vs GRPO 63.6% | 无监督下性能相当 |
| **代码（LiveCodeBench）** | +65% vs GRPO -8% | **跨领域泛化碾压** |
| **指令遵循（AlpacaEval）** | 7.10 vs Base 3.72 | 通用能力显著提升 |

**关键发现**：在 MATH 上训练的 Intuitor 模型，自动学会了代码生成能力，且优于在 MATH 上训练的 GRPO！这证明了其学到的是**通用的推理能力**，而非特定任务的模式。

#### 🚀 未来意义

当 AI 能力超越人类（科学发现、战略决策）时：
- 人类无法提供可靠的"正确答案"作为监督
- RLIF 成为唯一可行的提升路径
- Intuitor 为通往 AGI 的"自我进化"提供了方法论

---

### 🎯 主要优势

根据论文实验结果（基于 Qwen2.5-3B，在 MATH 数据集上训练）：

1. **完全无监督学习**
   - ✅ 不需要标准答案或测试用例
   - ✅ 不需要人工标注或偏好数据
   - ✅ 不需要领域特定的验证器
   - ✅ 仅需清晰的任务提示词（prompt）

2. **域内性能相当**
   - **GSM8K**：Intuitor 79.2% vs GRPO 82.6%
   - **MATH500**：Intuitor 61.2% vs GRPO 63.6%
   - 在无需金标答案的情况下，性能接近有监督的 GRPO

3. **域外泛化显著更强**（这是关键优势）
   - **LiveCodeBench v6**（代码生成）
     - Base: 9.3% → Intuitor: 15.3%（**+65% 相对提升**）
     - Base: 9.3% → GRPO: 8.5%（**性能下降**）
   - **CRUXEval-O**（代码推理）
     - Base: 23.6% → Intuitor: 41.6%（**+76% 相对提升**）
     - Base: 23.6% → GRPO: 34.1%（**+44% 相对提升**）

4. **涌现能力**
   - **结构化推理**：模型自发产生长链推理（类似 R1 风格）
   - **指令遵循**：AlpacaEval 分数从 3.72 提升到 7.10
   - **自我理解**：Qwen2.5-1.5B 从产生乱码（0% on LiveCodeBench）进化到生成连贯代码（9.9%）

5. **快速学习**
   - 在训练早期（Step 10），Intuitor 在 GSM8K 和 MATH 上均优于 GRPO
   - 更快的初期学习速度表明内在信号提供了更有效的学习轨迹

## 🚀 已发布模型

我们已经发布了四个在 MATH 数据集上训练一个 epoch 的模型检查点：

| 模型名称 | 大小 | 方法 | Hugging Face 链接 |
|---------|------|------|-------------------|
| sunblaze-ucb/Qwen2.5-1.5B-Intuitor-MATH-1EPOCH | 1.5B | Intuitor | [查看模型](https://huggingface.co/sunblaze-ucb/Qwen2.5-1.5B-Intuitor-MATH-1EPOCH) |
| sunblaze-ucb/Qwen2.5-3B-Intuitor-MATH-1EPOCH | 3B | Intuitor | [查看模型](https://huggingface.co/sunblaze-ucb/Qwen2.5-3B-Intuitor-MATH-1EPOCH) |
| sunblaze-ucb/OLMo-2-7B-SFT-Intuitor-MATH-1EPOCH | 7B | Intuitor | [查看模型](https://huggingface.co/sunblaze-ucb/OLMo-2-7B-SFT-Intuitor-MATH-1EPOCH) |
| sunblaze-ucb/Qwen3-14B-Intuitor-MATH-1EPOCH | 14B | Intuitor | [查看模型](https://huggingface.co/sunblaze-ucb/Qwen3-14B-Intuitor-MATH-1EPOCH) |

## 📦 仓库结构

本教程使用 **verl-intuitor** 实现，这是基于 [VERL](https://github.com/volcengine/verl) 的高性能 RL 训练库，专为大语言模型设计。

原始仓库：[https://github.com/sunblaze-ucb/Intuitor](https://github.com/sunblaze-ucb/Intuitor)
- verl-intuitor 基于 VERL commit c26b0f2

## 🛠️ 环境安装

### 1. 克隆 Intuitor 仓库

```bash
git clone https://github.com/sunblaze-ucb/Intuitor.git
cd Intuitor/verl-intuitor
```

### 2. 安装依赖

首先安装 VERL 和相关依赖：

```bash
# 创建 Python 虚拟环境（推荐）
conda create -n intuitor python=3.10
conda activate intuitor

# 安装 PyTorch（根据你的 CUDA 版本调整）
pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cu118

# 安装 VERL
pip install -e .

# 安装其他依赖
pip install wandb transformers datasets accelerate
```

### 3. 准备 MATH 数据集

运行以下 Python 脚本下载并预处理 MATH 数据集：

```bash
python examples/data_preprocess/math_dataset_ours.py --model Qwen2.5-3B
```

## 🚀 训练模型

### 1. 配置 WANDB API Key

在运行训练之前，需要修改 `math_intuitor.sh` 脚本，添加你的 WANDB API Key：

```bash
# 编辑 math_intuitor.sh
vim math_intuitor.sh

# 在脚本开头添加以下行：
export WANDB_API_KEY=YOUR_WANDB_API_KEY
```

将 `YOUR_WANDB_API_KEY` 替换为你的实际 WANDB API Key（可在 [wandb.ai/authorize](https://wandb.ai/authorize) 获取）。

### 2. 开始训练

配置完成后，运行训练脚本：

```bash
bash math_intuitor.sh
```

**重要提示**：Intuitor 中唯一的启发式设计是用于查询模型的提示词（prompt）。因此，性能有时可能对提示词设计敏感。如果模型学习效果不佳，建议尝试替代的提示词，或使用我们设置中提供的原始提示词。

### 3. 多节点训练（可选）

如果需要使用 Ray 进行多节点训练，请查看 `./scripts_ray` 文件夹中的详细说明和脚本。

## 📊 模型评测

训练完成后，按照论文方法使用 **[lighteval](https://github.com/huggingface/lighteval)** 进行标准化评测。

> **为什么使用 lighteval？**
> - ✅ 论文使用的官方评测工具
> - ✅ Hugging Face Leaderboard 的标准评测框架
> - ✅ 支持 7,000+ 评测任务，覆盖数学、代码、多语言等
> - ✅ 统一的评测标准，结果可对比

### 1. 安装 lighteval

```bash
pip install lighteval
```

### 2. 转换模型格式

首先将训练检查点转换为 Hugging Face 格式：

```bash
python -m verl.model_merger merge \
    --backend fsdp \
    --local_dir /root/Intuitor/verl-intuitor/checkpoints/verl/math_intuitor/global_step_57 \
    --target_dir math_intuitor_model
```

**参数说明**：
- `--backend fsdp`：使用 FSDP（Fully Sharded Data Parallel）后端
- `--local_dir`：训练检查点的路径（根据实际路径调整）
- `--target_dir`：输出的 Hugging Face 格式模型目录

### 3. 修改 lighteval 源码（重要！）

**在评测前必须修改 lighteval 源码**，否则会遇到两个问题：
1. 默认的 256 token generation size 不足以让模型完成推理
2. 默认的 normalizer 无法识别 `\boxed{}` 格式的答案

#### 步骤 1：修改 generation_size

找到 lighteval 安装路径中的任务配置文件：

```bash
# 找到 lighteval 安装位置
python3 -c "import lighteval; print(lighteval.__file__)"
# 输出示例：/path/to/site-packages/lighteval/__init__.py

# 编辑任务配置文件
vim $(python3 -c "import lighteval.tasks.default_tasks as t; print(t.__file__)")
```

在 `default_tasks.py` 中找到 GSM8K Leaderboard 的配置（搜索 `"gsm8k_leaderboard"`），将 `generation_size` 从 `256` 修改为 `2048`：

```python
# 修改前：
LightevalTaskConfig(
    name="gsm8k",
    ...
    generation_size=256,  # ← 原始值太小
    ...
)

# 修改后：
LightevalTaskConfig(
    name="gsm8k",
    ...
    generation_size=2048,  # ← 改为 2048，为推理链提供足够的 token budget
    ...
)
```

#### 步骤 2：修改 gsm8k_normalizer 支持 \\boxed{} 格式

找到并编辑 normalizer 文件：

```bash
# 编辑 normalizations.py
vim $(python3 -c "import lighteval.metrics.normalizations as n; print(n.__file__)")
```

找到 `gsm8k_normalizer` 函数（约第 379 行），将其替换为以下代码：

```python
def gsm8k_normalizer(text: str) -> str:
    """From https://github.com/openai/grade-school-math/blob/3101c7d5072418e28b9008a6636bde82a006892c/grade_school_math/dataset.py#L28
    
    Extended to support \\boxed{} format commonly used by reasoning models.

    Args:
        text (str): input text

    Returns:
        str: Output text, either the number found in the text or "[invalid]" if
        no number was found
    """
    INVALID_ANS = "[invalid]"
    
    # Try to extract from \\boxed{} format first (for reasoning models like Intuitor)
    # This pattern matches both \boxed{number} and \(\boxed{number}\)
    boxed_match = re.search(r'\\boxed\{([^}]+)\}', text)
    if boxed_match:
        match_str = boxed_match.group(1).strip()
        match_str = match_str.replace(",", "")
        # Extract only the number part (remove any non-numeric trailing text)
        number_match = re.search(r'-?[0-9\.\,]+', match_str)
        if number_match:
            return number_match.group(0).replace(",", "")
    
    # Original #### format (for standard GSM8K format)
    ans_re = re.compile(r"#### (\-?[0-9\.\,]+)")
    match = ans_re.search(text)
    if match:
        match_str = match.group(1).strip()
        match_str = match_str.replace(",", "")
        return match_str
    
    # If no pattern matched, return invalid
    return INVALID_ANS
```

**修改说明**：
- ✅ **向后兼容**：保留了原有的 `####` 格式支持
- ✅ **支持 `\boxed{}`**：可识别 `\boxed{52}` 和 `\(\boxed{5}\)` 等 LaTeX boxed 格式
- ✅ **自动提取数字**：即使 boxed 中包含单位（如 `\boxed{52 WPM}`）也能提取数字

**为什么需要这两处修改？**
- **Generation size**：Intuitor 生成包含详细推理步骤的 CoT，256 tokens 会导致答案被截断
- **Normalizer**：Intuitor 输出 LaTeX `\boxed{}` 格式，与 GSM8K 标准的 `####` 格式不同

### 4. 使用 lighteval 评测

#### 评测 GSM8K（数学推理）

```bash
lighteval accelerate \
    "model_name=math_intuitor_model/" \
    "leaderboard|gsm8k|0"
```

### 5. 查看评测结果

lighteval 会自动生成详细的评测报告：

```bash
# 结果保存在指定的输出目录
ls ./eval_results/

# 查看详细结果（JSON 格式）
cat ./eval_results/results.json
```

#### 从缓存的 parquet 重新计算准确率

如果 lighteval 显示 0% 准确率（因为模型输出 `\boxed{}` 格式而非 `####` 格式），可以使用提供的脚本从缓存的 parquet 文件重新计算准确率：

```bash
# 找到缓存的 parquet 文件
# 路径格式：~/.cache/huggingface/lighteval/{model_name}/{hash}/leaderboard|gsm8k|0/{hash}/GENERATIVE.parquet
ls ~/.cache/huggingface/lighteval/math_intuitor_model/*/leaderboard\|gsm8k\|0/*/GENERATIVE.parquet

# 使用脚本重新计算准确率（支持 \boxed{} 格式）
python3 evaluate_from_cache.py \
    ~/.cache/huggingface/lighteval/math_intuitor_model/*/leaderboard\|gsm8k\|0/*/GENERATIVE.parquet

# 显示详细信息和错误样本
python3 evaluate_from_cache.py \
    ~/.cache/huggingface/lighteval/math_intuitor_model/*/leaderboard\|gsm8k\|0/*/GENERATIVE.parquet \
    -v

# 保存结果到 JSON 文件
python3 evaluate_from_cache.py \
    ~/.cache/huggingface/lighteval/math_intuitor_model/*/leaderboard\|gsm8k\|0/*/GENERATIVE.parquet \
    -o results.json
```

**脚本功能**：
- ✅ 支持 `\boxed{}` 格式答案提取（包括 `\(\boxed{}\)` 等变体）
- ✅ 自动从 Hugging Face 加载 GSM8K 金标答案
- ✅ 标准化数字格式（去除逗号、空格等）
- ✅ 显示详细的错误样本分析

**示例输出**：
```
📂 读取预测结果: /root/.cache/huggingface/lighteval/.../GENERATIVE.parquet
📊 总样本数: 1319
📥 加载 GSM8K 金标答案...

================================================================================
📈 评测结果
================================================================================
总样本数: 1319
正确数量: 623
错误数量: 696
准确率: 47.23%
================================================================================
```

### 6. 论文中的评测基准

根据论文，以下是主要的评测基准：

| 基准 | lighteval 任务名 | 类型 | 用途 |
|------|----------------|------|------|
| **GSM8K** | `leaderboard|gsm8k|0` | 数学推理 | 域内性能 |
| **MATH500** | `leaderboard|math500|0` | 高级数学 | 域内性能 |
| **LiveCodeBench** | `leaderboard|lcb|0` | 代码生成 | 域外泛化 |
| **CRUXEval-O** | `leaderboard|cruxeval|0` | 代码推理 | 域外泛化 |
| **MMLU-Pro** | `leaderboard|mmlu_pro|0` | 通用知识 | 通用能力 |
| **AlpacaEval** | 需单独工具 | 指令遵循 | 对话能力 |

**注意**：AlpacaEval 需要使用其[官方工具](https://github.com/tatsu-lab/alpaca_eval)进行评测，因为它需要 GPT-4 作为评判器。

## 📈 实验结果

### 论文结果

根据论文，在 Qwen2.5-3B base 模型上的实验结果：

#### 数学任务（MATH 数据集训练）
- **GSM8K**：Intuitor 与 GRPO 性能相当
- **MATH500**：Intuitor 与 GRPO 性能相当

#### 代码生成任务（域外泛化）
- **LiveCodeBench v6**：Intuitor 相对提升 **65%**（GRPO 无提升）
- **CRUXEval-O**：Intuitor 提升 **76%**（GRPO 仅提升 44%）

#### 涌现能力
对于 Qwen2.5-1.5B base 模型（原始模型在 LiveCodeBench 上得分 0%）：
- 训练后能够生成连贯的推理链和结构良好的代码
- LiveCodeBench 准确率达到 **9.9%**

---

### 复现结果（GSM8K 评测）

使用修改后的 lighteval（支持 `\boxed{}` 格式 + 2048 tokens generation size）进行评测：

#### Qwen2.5-3B 模型（训练后）

```bash
lighteval accelerate "model_name=math_intuitor_model" "leaderboard|gsm8k|0"
```

| 模型 | 准确率 | 正确数 | 总数 | 备注 |
|------|--------|--------|------|------|
| **Qwen2.5-3B + Intuitor** | **78.09%** | 1,030 | 1,319 | 使用 MATH 数据集训练 |

**结果分析**：
- ✅ 训练后的 3B 模型在 GSM8K 上达到了 **78.09%** 的准确率
- ✅ 模型能够生成完整的 CoT 推理链
- ✅ 答案格式正确（`\boxed{number}` 格式）

#### Qwen2.5-1.5B 模型训练前后对比

| 模型 | 准确率 | 正确数 | 总数 | 备注 |
|------|--------|--------|------|------|
| **Qwen2.5-1.5B Base** | **0.38%** | 5 | 1,319 | 原始基座模型，无训练 |
| **Qwen2.5-1.5B + Intuitor** | **70.13%** | 925 | 1,319 | 使用 MATH 数据集训练 |

**结果分析**：

**Base 模型（0.38%）**：
- ❌ 无法遵循指令格式
- ❌ 不会输出标准的 `\boxed{answer}` 格式
- 💡 **关键发现**：指令遵循能力是推理模型的基础

**训练后模型（70.13%）**：
- ✅ 答案格式规范（`\boxed{number}` 格式）
- ✅ 展现了 Intuitor 无监督强化学习的有效性

**1.5B vs 3B 对比**：
- 3B 模型（78.09%）比 1.5B 模型（70.13%）高约 **8 个百分点**
- 两者都成功学会了推理和格式遵循能力

---

## 🔬 算法原理详解

### 0. Intuitor vs DeepSeek R1-Zero：关键区别

很多人容易混淆 Intuitor 和 DeepSeek R1-Zero，因为两者都不使用人工标注的推理过程。但它们有本质区别：

#### DeepSeek R1-Zero（第二曲线：RLVR）

**训练流程**：
```
问题 → 模型生成推理链 + 答案 → 验证答案是否正确 → GRPO 更新
                                    ↑
                            需要金标答案！
```

**特点**：
- ✅ 不需要标注推理过程（与 R1 的区别）
- ❌ 仍需要**金标答案**来验证最终结果
- ❌ 奖励信号：`r = 1 if 答案正确 else 0`（二元奖励）
- ❌ 属于 **RLVR（可验证奖励）** 范畴
- 🎯 训练目标：让模型找到能得出正确答案的推理链
- 📍 代表作：DeepSeek-R1-Zero、Kimi K1.5、QwQ-32B

**论文描述**（DeepSeek R1 Technical Report）：
> "We first explore RL without supervised fine-tuning (SFT) data, termed RL from scratch (dubbed R1-Zero). Starting from Qwen base model with only a few prompt engineering trials, R1-Zero successfully developed strong reasoning capabilities comparable to R1 with SFT."

**关键点**：R1-Zero 的"Zero"指的是零 SFT 数据（无需标注推理过程），但仍然依赖于可验证的奖励函数（答案正确性）。

#### Intuitor（第三曲线：无监督 RL）

**训练流程**：
```
问题 → 模型生成推理链 + 答案 → 计算 self-certainty → GRPO 更新
                                    ↑
                        完全无需外部验证！
```

**特点**：
- ✅ 不需要标注推理过程
- ✅ 不需要金标答案
- ✅ 奖励信号：`u = Self-Certainty(输出)`（连续、token 级别）
- ✅ 属于 **无监督 RL** 范畴，使用**内部反馈（RLIF）**方法
- 🎯 训练目标：让模型生成自己确信的推理链
- 📍 第三曲线代表作：
  - 内部反馈：Intuitor、Absolute Zero
  - 一致性：TTRL（plurality voting）
  - 其他：Rubrics-based、Multi-agent debate 等

#### 详细对比表

| 维度 | DeepSeek R1-Zero | Intuitor |
|------|------------------|----------|
| **所属曲线** | 第二曲线（RLVR） | 第三曲线（无监督 RL） |
| **具体方法** | 可验证奖励 | 内部反馈（RLIF） |
| **是否需要金标答案** | ✅ 必须 | ❌ 不需要 |
| **是否需要标注推理** | ❌ 不需要 | ❌ 不需要 |
| **奖励来源** | 外部验证器 | 内在置信度 |
| **奖励类型** | 二元（对/错） | 连续（置信度分数） |
| **奖励粒度** | 答案级别 | Token 级别 |
| **训练数据要求** | 需要有答案的题目 | 只需问题描述 |
| **适用场景** | 数学、代码等可验证任务 | **任意任务** |
| **域内性能** | 优秀（84.4% GSM8K） | 相当（79.2% GSM8K） |
| **域外泛化** | 未报告 | **强（+65% LCB）** |

#### 为什么区分这两者很重要？

1. **应用场景差异**
   - R1-Zero：仅适用于有明确答案的任务（数学、代码、科学）
   - Intuitor：可用于写作、对话、创意等**无明确答案**的任务

2. **数据需求差异**
   - R1-Zero：需要构建包含金标答案的训练集（如 MATH 7,500 题）
   - Intuitor：可以用任何文本作为训练数据（甚至无标注的问题）

3. **研究意义差异**
   - R1-Zero：证明了不需要标注推理过程也能训练推理模型
   - Intuitor：证明了不需要**任何外部奖励**也能提升推理能力

4. **未来潜力**
   - R1-Zero：推向人类难以验证的领域时会遇到瓶颈
   - Intuitor：为 AI 自主学习、超越人类监督提供了路径

#### 第三曲线的方法谱系

第三曲线（无监督 RL）包含多种实现方式，它们的共同点是：**不需要金标答案或人工偏好标注**。

| 方法类型 | 代表工作 | 奖励信号来源 | 特点 |
|---------|---------|------------|------|
| **内部反馈** | Intuitor | Self-certainty（内部置信度） | ✅ 完全无监督，强泛化 |
| **内部反馈** | Absolute Zero | 内部信号 | ✅ 零数据学习 |
| **一致性** | TTRL | Plurality voting（多数投票） | ⚠️ 仍需题目（无需答案） |
| **一致性** | Genius | Self-consistency | ⚠️ 仍需题目（无需答案） |
| **规则奖励** | Rubrics-based | 预定义评分规则 | ⚠️ 需人工设计规则 |
| **新颖性** | Novelty-based | 探索未知区域 | ✅ 适合开放式任务 |
| **多智能体** | Multi-agent Debate | 智能体间达成共识 | ✅ 通过讨论提升质量 |

**Intuitor 论文的观点**：
> "Concurrent works like Genius, TTRL, and Absolute Zero leverage queries without labels for reinforcement learning but remain **constrained to specific task distributions**, primarily in mathematical reasoning. INTUITOR aligns with this direction but introduces a lightweight, general-purpose alternative: using self-certainty as a confidence-based intrinsic reward."

**关键区别**：
- **R1-Zero、GRPO**（第二曲线）：需要金标答案验证正确性
- **TTRL、Genius**（第三曲线）：不需要金标答案，但仍依赖题目分布和一致性假设
- **Intuitor**（第三曲线）：完全基于内在信号，适用范围最广，泛化能力最强

第三曲线的各种方法都在探索"如何在无明确奖励函数的情况下提升模型能力"，这是通向通用 AI 的关键路径。

### 1. 从外部监督到内部反馈

#### 传统方法的局限

**RLHF（人类反馈强化学习）**优化目标：
```
max E[r_φ(q, o) - β·KL(π_θ || π_ref)]
```
- `r_φ(q, o)`：由人类偏好数据训练的奖励模型
- 问题：需要大量人工标注，成本高昂，可能引入偏见和奖励黑客问题

**RLVR（可验证奖励强化学习）**优化目标：
```
max E[v(q, o) - β·KL(π_θ || π_ref)]
```
- `v(q, o)`：可验证的奖励函数（如答案正确性：正确=α，错误=0）
- 问题：需要金标答案或测试用例，仅适用于特定领域，难以跨任务泛化

#### 无监督 RL（第三曲线）

**通用优化目标**：
```
max E[u(q, o) - β·KL(π_θ || π_ref)]
```

**核心特点**：奖励信号 `u(q, o)` **不需要金标答案或人工标注**

其中：
- `q`：输入查询（问题）
- `o`：模型生成的输出（答案）
- `π_θ`：策略模型（待优化）
- `π_ref`：参考模型（初始模型）
- `β`：KL 散度惩罚系数

**不同方法的 `u(q, o)` 实现**：
- **RLIF（Intuitor）**：`u = Self-Certainty(o|q)` — 内部置信度
- **一致性方法（TTRL）**：`u = IsPlurality(o)` — 是否为多数答案
- **规则奖励**：`u = RubricsScore(o)` — 基于预定义规则
- **新颖性**：`u = Novelty(o)` — 探索度
- **多智能体**：`u = ConsensusScore(o)` — 智能体间共识度

### 2. 自我确定性（Self-Certainty）：Intuitor 的奖励信号

在无监督 RL 的众多可能奖励信号中，**Intuitor 选择了 Self-Certainty（自我确定性）**作为其奖励函数 `u(q, o)`。

这是一种**内部反馈（RLIF）**方法，完全基于模型自身的输出分布，无需任何外部信息。

#### 数学定义

自我确定性是模型输出分布与均匀分布之间的 KL 散度的平均值：

```
Self-Certainty(o|q) = 1/|o| · Σ(i=1 to |o|) KL(U || p_π(·|q, o<i))
                    = -1/(|o|·|V|) · Σ(i=1 to |o|) Σ(j=1 to |V|) log(|V| · p_π(j|q, o<i))
```

其中：
- `|o|`：生成序列的长度（token 数）
- `|V|`：词汇表大小
- `U`：均匀分布（每个 token 概率为 1/|V|）
- `p_π(j|q, o<i)`：模型在位置 i 预测 token j 的概率
- `o<i`：位置 i 之前已生成的 token

#### 关键特性

1. **Mode-Seeking（模式寻找）**
   - Self-Certainty 使用 `KL(U || p_model)`，这是 mode-seeking 的度量
   - 相比之下，熵（或反向 KL）是 mode-covering 的
   - Mode-seeking 鼓励模型对答案更有信心，而非覆盖所有可能性

2. **对长度偏差不敏感**
   - 与 perplexity 或 entropy 相比，self-certainty 更不容易被长文本偏置
   - 这使其更适合作为强化学习的奖励信号

3. **Token 级别的置信度**
   - 奖励整个**生成轨迹**，而非仅最终结果
   - 每个 token 的生成都对奖励有贡献
   - 这是 Intuitor 泛化能力强的关键原因

#### 直观理解

- **高 Self-Certainty**：模型对每个 token 的预测都很确定（分布尖锐，远离均匀分布）
  - 例如：模型在生成 "42" 时，对 "4" 和 "2" 都有很高的概率
- **低 Self-Certainty**：模型不确定，输出分布接近均匀（每个 token 概率接近）
  - 例如：模型在多个候选词之间摇摆不定

### 3. Intuitor 的实现：基于 GRPO

#### GRPO 算法核心

Intuitor 使用 **Group Relative Policy Optimization (GRPO)** 作为策略优化算法：

```
J_GRPO(θ) = E[1/G · Σ(i=1 to G) 1/|o_i| · Σ(t=1 to |o_i|) 
            min(c_i,t(θ)·Â_i,t, clip(c_i,t(θ), 1-ε, 1+ε)·Â_i,t) 
            - β·D_KL(π_θ || π_ref)]
```

其中：
- `G`：每个问题采样的候选答案数量（默认 7 个）
- `c_i,t(θ) = π_θ(o_i,t | q, o_i,<t) / π_θ_old(o_i,t | q, o_i,<t)`：重要性采样比率
- `Â_i,t`：优势函数（advantage）
- `clip(c, 1-ε, 1+ε)`：截断函数，防止策略更新过大

#### Intuitor 的关键创新

**将外部奖励替换为自我确定性**：

```python
# 1. 对每个问题 q，采样 G 个候选答案
outputs = [o_1, o_2, ..., o_G]

# 2. 计算每个答案的自我确定性分数
u_i = Self-Certainty(o_i | q)  # 内在奖励，无需外部验证！

# 3. 计算组内相对优势（归一化）
Â_i,t = (u_i - mean([u_1, ..., u_G])) / std([u_1, ..., u_G])

# 4. 使用 GRPO 更新策略
# 策略会倾向于生成高 self-certainty 的输出
```

#### 与 GRPO 的对比

| 特性 | GRPO | Intuitor |
|------|------|----------|
| **奖励来源** | 外部验证器（金标答案） | 内在信号（self-certainty） |
| **需要监督** | ✅ 需要标准答案 | ❌ 完全无监督 |
| **奖励粒度** | 结果级别（答案对错） | Token 级别（生成轨迹） |
| **域内性能** | 优秀 | 相当（略低 2-3%） |
| **域外泛化** | 较弱（甚至负迁移） | **强（+65% on LCB）** |
| **适用场景** | 有标准答案的任务 | 任意任务（仅需 prompt） |

### 4. 为什么 Intuitor 泛化更强？

#### 原因 1：奖励生成过程，而非结果

- **GRPO**：`v(q, o) = 1 if 答案正确 else 0`
  - 只关心最终答案，不管推理过程
  - 模型可能记住特定模式，但无法迁移

- **Intuitor**：`u(q, o) = avg(Self-Certainty per token)`
  - 奖励整个推理链，鼓励清晰、自信的表达
  - 学到的是"如何清晰推理"，这可以迁移到新任务

#### 原因 2：鼓励结构化推理

论文观察到，Intuitor 训练的模型会自发地：
1. 在代码前添加自然语言推理（即使 prompt 没要求）
2. 生成更长、更详细的推理链
3. 在 JSON 格式外先推理，再总结（见论文 Figure 5）

**为什么？** 因为详细的推理步骤让模型自己更有信心（更高的 self-certainty），从而获得更高奖励。

#### 原因 3：在线自我确定性防止奖励黑客

- **离线**评分器（固定模型）：容易被利用（见论文 Figure 7）
  - 模型学会"欺骗"固定的评分器，生成高分但无意义的输出
  
- **在线**评分器（Intuitor）：评分标准随策略模型共同进化
  - 模型无法"欺骗"自己，必须真正提升推理质量
  - 论文实验显示：Intuitor 训练的模型在区分正确/错误答案上更可靠（Figure 8）

### 5. 关键超参数

| 参数 | 1.5B/3B 模型 | 7B/14B 模型 | 作用 |
|------|-------------|------------|------|
| **β (KL penalty)** | 0.0005 | 0.01 | 防止偏离初始模型过远 |
| **Group Size (G)** | 7 | 14 | 每个问题的候选答案数 |
| **Learning Rate** | 3×10⁻⁶ | 1×10⁻⁶ | 策略更新步长 |
| **Batch Size** | 128 | 64 | 每次更新的问题数 |

**重要发现**（论文 Table 3）：
- KL penalty 对域外泛化**极其敏感**
- β=0（无 KL penalty）：域内好，但域外差
- β=0.005：域内外平衡最佳
- β=0.01：域外略降，但仍强于 GRPO

### 6. 核心洞察：为什么优化置信度能提升推理能力？

这是 Intuitor 最令人惊讶的发现：**仅通过优化模型对自己输出的置信度，就能显著提升推理能力**。

#### 理论解释

1. **置信度 ≈ 内部一致性**
   - 当模型对答案有信心时，意味着其内部表示是一致的、连贯的
   - 通过优化置信度，模型学会构建更连贯的推理链

2. **长链推理涌现**
   - 详细的推理步骤让模型"看清"自己的思路
   - 每一步都清晰，整体置信度就高
   - 结果：模型自发生成更长、更详细的推理（见论文 Figure 3, 6）

3. **自我解释循环**
   ```
   模型不确定 → 生成详细推理 → 自己更理解 → 置信度提升 → 获得奖励
   ```
   这形成了一个正反馈循环，促使模型学会"向自己解释"

4. **从特定到通用**
   - GRPO 学到的是"这类数学题的答案模式"（特定）
   - Intuitor 学到的是"如何清晰表达推理"（通用）
   - 后者自然可以迁移到代码、文本等其他领域

#### 实证证据

论文通过多个实验验证了这一机制：

1. **响应长度演变**（Figure 3）
   - Qwen2.5-1.5B: 训练初期长度降低（去除乱码），后期稳定
   - Qwen2.5-3B: 训练中持续增加，从 600 → 850 tokens
   - 表明模型学会通过详细推理提升置信度

2. **代码生成的推理涌现**（Figure 6）
   - Step 0-10: 无效代码 → Step 20-30: 有效代码（无推理）
   - Step 40-50: 有效代码 + 详细推理 + 解释
   - 推理是**自发涌现**的，prompt 并未要求！

3. **Mann-Whitney U 测试**（Figure 8）
   - Intuitor 模型在区分正确/错误答案时，self-certainty 分数差异最大
   - p-value = 1.7e-15, effect size r = 0.35
   - 表明模型学会了更可靠的自我评估

#### 哲学意义与现实意义

Intuitor 揭示了一个深刻的洞察：
> **智能系统无需外部奖励，可以通过优化内部一致性（置信度）来自我提升。**

这与人类学习类似：
- 我们解决难题时，常常"向自己解释"来加深理解
- 当我们能清晰表达一个想法时，通常意味着我们真正理解了它
- Intuitor 将这一机制形式化为强化学习算法

**关键观察**：
- RLVR（第二曲线）已经将数学推理推向极致（R1、o1）
- 但这只覆盖了 AI 应用的**一小部分**
- 真正的通用 AI 需要处理**没有明确对错**的任务
- Intuitor 为这些任务提供了训练方法

**未来展望**：
随着模型能力超越人类（如科学研究、战略决策），我们将越来越难以提供可靠的外部奖励。此时，**无监督 RL（第三曲线）**可能是唯一可行的提升路径。

#### 局限与未来方向

1. **对 Prompt 敏感**
   - Self-certainty 是唯一的启发式信号
   - Prompt 设计对性能影响较大
   - 未来：更鲁棒的 prompt 设计 or 自适应 prompt

2. **需要在线更新**
   - 纯离线训练会导致奖励黑客（Figure 7）
   - 未来：混合在线-离线训练策略

3. **与外部奖励结合**
   - 本文为了对比，只用单一奖励
   - 实践中可以结合：Self-Certainty + 正确性 + 格式规范

## 📝 引用

如果你在研究中使用了 Intuitor，请引用以下论文：

```bibtex
@article{zhao2025intuitor,
  title={Learning to Reason without External Rewards},
  author={Zhao, Xuandong and Kang, Zhewei and Feng, Aosong and Levine, Sergey and Song, Dawn},
  journal={arXiv preprint arXiv:2505.19590},
  year={2025}
}
```

## 📄 许可证

本项目基于 Apache 2.0 许可证开源。

## 🙏 致谢

- [VERL](https://github.com/volcengine/verl)：高性能 RL 训练框架
- [GSM8K-eval](https://github.com/Guangxuan-Xiao/GSM8K-eval)：数学推理评测工具
- [MATH Dataset](https://github.com/hendrycks/math)：数学问题数据集

## 📮 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues: [https://github.com/sunblaze-ucb/Intuitor/issues](https://github.com/sunblaze-ucb/Intuitor/issues)
- 论文作者：Xuandong Zhao (xuandongzhao@berkeley.edu), Zhewei Kang (waynekang@berkeley.edu)

---

**注意**：本 README 专注于 verl-intuitor 实现。如需了解 open-r1-intuitor 实现，请参考原始仓库。

