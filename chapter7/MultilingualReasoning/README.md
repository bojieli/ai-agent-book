# 多语言推理模型微调

本项目展示如何使用 Hugging Face 的 TRL 库对 OpenAI 的开源推理模型 `openai/gpt-oss-20b` 进行微调，使其能够在多种语言中进行有效推理。

## 项目简介

大型推理模型如 OpenAI o3 会生成思维链（chain-of-thought）来提高响应的准确性和质量。然而，大多数模型即使在其他语言提问时也用英语进行推理。

本项目通过以下方式解决这个问题：
- 在模型的系统提示中添加"推理语言"选项
- 使用多语言推理数据集进行监督微调（SFT）
- 支持英语、西班牙语、法语、意大利语、德语等多种语言的推理

## 功能特性

✨ **多语言推理**：模型可以用多种语言生成思维链
🔀 **混合语言支持**：可以用一种语言提问，用另一种语言推理，用第三种语言回答
🚀 **高效训练**：使用 Mxfp4Config 量化 + LoRA（低秩适应）技术进行内存高效的微调
🎯 **针对 MoE 优化**：专门配置混合专家（Mixture-of-Experts）架构的训练参数
📊 **实时监控**：训练过程中跟踪损失和指标
🌏 **强大的跨语言泛化能力**：虽然微调数据集中没有中文，但模型的泛化能力使其能够用中文生成推理过程！

## 系统要求

### ⚠️ 重要：显存需求

**训练过程中峰值显存占用约 97GB**

- **推荐配置**: H200 GPU（141GB 显存）
- **不推荐**: 单卡 80GB GPU（H100/A100）- 会出现 OOM（Out of Memory）错误
- **替代方案**: 
  - 使用多 GPU 训练（模型并行/数据并行）
  - 减小批次大小（batch_size）和序列长度（max_seq_length）
  - 使用梯度检查点（gradient checkpointing）
  - 使用 DeepSpeed ZeRO-3 等显存优化技术

### 其他要求

- CUDA: 12.8 或更高版本
- Python: 3.8+
- 存储空间: 至少 100GB（用于模型和检查点）

## 安装依赖

```bash
# 安装 PyTorch（CUDA 12.8）
pip install torch --index-url https://download.pytorch.org/whl/cu128

# 安装其他依赖
pip install "trl>=0.20.0" "peft>=0.17.0" "transformers>=4.55.0" trackio datasets accelerate
```

## 快速开始

### 1. 设置环境

首先，确保你已登录 Hugging Face：

```python
from huggingface_hub import notebook_login
notebook_login()
```

或使用命令行：

```bash
huggingface-cli login
```

### 2. 准备数据集

本项目使用 `HuggingFaceH4/Multilingual-Thinking` 数据集，该数据集包含多种语言的推理链：

```python
from datasets import load_dataset

dataset = load_dataset("HuggingFaceH4/Multilingual-Thinking")
```

**⚠️ 重要提示**：虽然该数据集中没有包含中文数据，但得益于模型的强大泛化能力，微调后的模型依然能够用中文进行推理！详见下方"关于中文推理的重要说明"章节。

### 3. 理解 Chat Template 和 Harmony 格式

`gpt-oss` 模型使用 **Harmony 响应格式**来定义对话结构、生成推理输出和构建函数调用。该格式模仿 OpenAI Responses API，包含以下消息类型：

#### 消息类型

| 类型 | 说明 |
|------|------|
| **developer** | 开发者消息，用于提供自定义指令（相当于系统角色） |
| **user** | 用户消息，用于提供输入 |
| **assistant** | 模型输出，可以是工具调用或消息输出。输出可能与特定"通道"（channel）关联，标识消息意图 |
| **analysis** | 用于模型思维链（chain-of-thought）的消息 |
| **final** | 标记在 final 通道中的消息，旨在显示给最终用户，代表模型的响应 |
| **messages** | 组合以上内容生成完整对话的消息列表 |

#### 重要特性

**Assistant 消息的特殊字段**：
- `thinking`：包含模型的推理过程
- `content`：包含给用户的最终响应

**两种系统消息**：
1. **默认 system 消息**：适用于所有消息（例如："You are ChatGPT, a large language model trained by OpenAI..."）
2. **特殊 developer 消息**：包含自定义指令（由 messages 对象中的 `system` 角色定义）

#### Chat Template 示例

使用 tokenizer 的 `apply_chat_template()` 方法格式化消息：

```python
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("openai/gpt-oss-20b")

# 示例消息
messages = [
    {"role": "system", "content": "reasoning language: German"},
    {"role": "user", "content": "¿Cuál es el capital de Australia?"}
]

# 应用 chat template
conversation = tokenizer.apply_chat_template(messages, tokenize=False)
print(conversation)
```

**输出格式特点**：
- 使用特殊 token：`<|start|>` 和 `<|end|>` 标记消息的开始和结束
- `<|return|>` token 标记对话结束
- 包含 `<|channel|>` 标记（如 `analysis`、`final`）来区分推理和最终响应

#### 格式化示例

```
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-10-03

Reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|>
<|start|>developer<|message|># Instructions

reasoning language: German

<|end|>
<|start|>user<|message|>¿Cuál es el capital de Australia?<|end|>
<|start|>assistant<|channel|>analysis<|message|>[模型的推理过程]<|end|>
<|start|>assistant<|channel|>final<|message|>[最终响应]<|return|>
```

TRL 库会自动处理数据集格式化、应用 chat template 和分词，因此训练时无需手动处理这些细节。

### 4. 运行微调

```bash
python gpt_oss_20b_sft.py
```

### 5. 推理测试

微调完成后，你可以使用模型进行多语言推理：

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载模型和分词器
tokenizer = AutoTokenizer.from_pretrained("openai/gpt-oss-20b")
model = AutoModelForCausalLM.from_pretrained("你的模型路径")

# 设置推理语言
REASONING_LANGUAGE = "German"
SYSTEM_PROMPT = f"reasoning language: {REASONING_LANGUAGE}"
USER_PROMPT = "¿Cuál es el capital de Australia?"  # 西班牙语：澳大利亚的首都是什么？

messages = [
    {"role": "system", "content": SYSTEM_PROMPT},
    {"role": "user", "content": USER_PROMPT},
]

# 生成响应
input_ids = tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt")
output_ids = model.generate(input_ids, max_new_tokens=512, temperature=0.6)
response = tokenizer.decode(output_ids[0])
print(response)
```

## 训练配置

### 超参数（与 OpenAI Cookbook 教程完全一致）

- **模型**: `openai/gpt-oss-20b`（20B 参数）
- **量化**: Mxfp4Config（针对 OpenAI 模型优化的 4-bit 浮点格式）
- **LoRA rank**: 8
- **LoRA alpha**: 16
- **批次大小**: 4（per_device_train_batch_size）
- **梯度累积步数**: 4
- **有效批次大小**: 16（4 × 4）
- **学习率**: 2e-4
- **学习率调度器**: cosine_with_min_lr（最小学习率为初始的 10%）
- **预热比例**: 0.03
- **训练轮数**: 1
- **最大序列长度**: 2048
- **梯度检查点**: True
- **显存峰值**: ~97GB

### LoRA 配置

使用 LoRA（Low-Rank Adaptation）技术，只训练少量参数：
- **目标模块**: `all-linear`（所有线性层）
- **MoE 专家层**: 额外训练第 7、15、23 层的 MLP 专家投影层（gate_up_proj 和 down_proj）
- **优势**: 
  - 显著减少训练时间和内存使用
  - 保持基础模型权重不变
  - 针对混合专家（MoE）架构优化

## 项目结构

```
MultilingualReasoning/
├── README.md                    # 项目文档
├── gpt_oss_20b_sft.py          # 完整的训练和推理脚本
└── requirements.txt             # 依赖列表（可选）
```

## 训练时间和资源消耗

### 标准配置（OpenAI Cookbook 测试结果）

- **GPU**: H100（80GB 显存）
- **训练时间**: 约 18 分钟
- **峰值显存**: ~97GB ⚠️ **会导致 OOM！**

### 实际建议配置

由于峰值显存超过 80GB，建议使用：
- **H200 GPU**（141GB 显存）- 可以完美运行
- **多 H100 GPU** - 使用模型并行
- **优化配置** - 见下方"性能优化建议"

### 影响因素

训练时间和显存占用取决于：
- GPU 型号和显存大小
- 批次大小（batch_size）
- 序列长度（max_seq_length）
- 梯度累积步数
- 是否使用混合精度训练

## 推理示例

以下示例展示了模型如何使用 Harmony 格式进行多语言推理。注意输出中的关键元素：
- `<|start|>` 和 `<|end|>`：标记消息边界
- `<|channel|>analysis`：推理过程（内部思考）
- `<|channel|>final`：最终响应（呈现给用户）
- `<|return|>`：对话结束标记

### 示例 1: 西班牙语提问 + 德语推理

这个示例展示了跨语言推理能力：用户用西班牙语提问，模型用德语思考，然后用英语回答。

```
生成响应...
推理语言: German
用户提问: ¿Cuál es el capital de Australia?
--------------------------------------------------------------------------------
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-10-03

Reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>developer<|message|># Instructions

reasoning language: German

<|end|><|start|>user<|message|>¿Cuál es el capital de Australia?<|end|><|start|>assistant<|channel|>analysis<|message|>Okay, der Benutzer fragt nach der Hauptstadt von Australien. Zunächst sollte ich daran denken, dass Australien ein Kontinent und ein Land ist, und seine Hauptstadt ist Canberra. Viele Leute denken fälschlicherweise, dass Sydney oder Melbourne die Hauptstadt ist, aber das ist nicht korrekt. Ich sollte sicherstellen, dass ich die richtige Antwort gebe.

Ich frage mich, ob der Benutzer vielleicht nach einer weniger bekannten Information fragt, aber die Frage ist ziemlich direkt. Ich sollte einfach die Hauptstadt nennen. Allerdings könnte der Benutzer nach weiteren Details fragen, wie zum Beispiel, wann Canberra zur Hauptstadt wurde oder warum es nicht Sydney ist. Ich sollte jedoch nur auf die Frage antworten, es sei denn, der Benutzer bittet um weitere Informationen.

Ich sollte auch sicherstellen, dass ich die Antwort klar und präzise formuliere. Also, die Hauptstadt von Australien ist Canberra. Ich kann das in einem Satz zusammenfassen. Es ist auch wichtig, die Frage des Benutzers zu berücksichtigen und sicherzustellen, dass ich keine Annahmen über sein Vorwissen treffe. Ich sollte nur die grundlegende Information geben, die er angefordert hat.<|end|><|start|>assistant<|channel|>final<|message|>The capital of Australia is Canberra.<|return|>
--------------------------------------------------------------------------------
```

### 🌏 关于中文推理的重要说明

**⚠️ 零样本泛化能力展示**

虽然训练数据集 `HuggingFaceH4/Multilingual-Thinking` 中**没有包含任何中文数据**，但模型依然能够在中文环境下生成高质量的推理过程！这是因为：

1. **基础模型的多语言能力**：GPT-OSS-20B 基础模型本身支持多种语言，包括中文
2. **推理模式的迁移**：通过在其他语言（英语、西班牙语、德语等）上学习推理模式，模型能够将这种能力泛化到未见过的语言
3. **系统提示的引导作用**：通过 `reasoning language: Chinese` 的系统提示，模型能够理解并切换到中文进行推理

这种**零样本跨语言泛化**是大型语言模型的重要特性，展示了即使没有特定语言的训练数据，模型仍能在新语言上表现出色。

**实际意义**：
- 无需为每种语言收集训练数据
- 降低了多语言模型的训练成本
- 证明了推理能力是可迁移的通用能力

下面的示例 2 和示例 3 展示了模型在中文环境下的推理能力：

### 示例 2: 英语提问 + 中文推理

这个示例展示了零样本跨语言泛化：虽然训练数据中没有中文，但模型仍能用中文进行推理。

```
生成响应...
推理语言: Chinese
用户提问: What is the national symbol of Canada?
--------------------------------------------------------------------------------
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-10-03

Reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>developer<|message|># Instructions

reasoning language: Chinese

<|end|><|start|>user<|message|>What is the national symbol of Canada?<|end|><|start|>assistant<|channel|>analysis<|message|>
我先思考一下加拿大的国家象征。加拿大的国旗是红白相间的，中央有一片枫叶。枫叶是加拿大的标志性符号，常被用来代表国家。枫叶在加拿大的文化和历史中占有重要地位，例如枫糖浆是加拿大的传统食品，枫叶也被用于许多官方徽章和纪
  品上。

我还记得加拿大的国徽和国旗都以枫叶为核心元素。枫叶象征着加拿大的自然景观和多样性，也体现了加拿大人对土地和自然的热爱。因此，我可以肯定地说，枫叶是加拿大的国家象征。<|end|><|start|>assistant<|channel|>final<|message|>The national symbol of Canada is the **maple leaf**. The maple leaf is prominently featured on Canada’s national flag (the Red Ensign), its coat of arms, and is widely used in government and cultural contexts to represent Canadian identity. The maple leaf symbolizes Canada's natural environment, its multicultural heritage, and its historical ties to the maple tree, which is abundant in the country.<|return|>
--------------------------------------------------------------------------------
```

### 示例 3: 中文提问 + 中文推理

这个示例展示了完全的中文推理：用中文提问数学问题，模型用中文进行详细的推理过程。

```
生成响应...
推理语言: Chinese
用户提问: 求解 x^2 - 2x + 1 = 0 的根
--------------------------------------------------------------------------------
<|start|>system<|message|>You are ChatGPT, a large language model trained by OpenAI.
Knowledge cutoff: 2024-06
Current date: 2025-10-03

Reasoning: medium

# Valid channels: analysis, commentary, final. Channel must be included for every message.<|end|><|start|>developer<|message|># Instructions

reasoning language: Chinese

<|end|><|start|>user<|message|>求解 x^2 - 2x + 1 = 0 的根<|end|><|start|>assistant<|channel|>analysis<|message|>
首先，我需要确认我理解了用户的输入。用户要求解方程 x^2 - 2x + 1 = 0 的根。

接下来，我回想一下求解二次方程的一般方法。二次方程的标准形式是 ax^2 + bx + c = 0。这里，a = 1，b = -2，c = 1。

我可以使用求根公式：x = [-b ± sqrt(b^2 - 4ac)] / (2a)。让我们代入数值：

b^2 = (-2)^2 = 4
4ac = 4 * 1 * 1 = 4
b^2 - 4ac = 4 - 4 = 0

由于判别式 (b^2 - 4ac) 为 0，方程有一个重根。计算根：

x = [-b ± sqrt(0)] / (2a) = [2 ± 0] / 2 = 2 / 2 = 1

因此，根是 x = 1。

我想再检查一次，确保没有错误。将 x = 1 代入原方程：

(1)^2 - 2*(1) + 1 = 1 - 2 + 1 = 0

这验证了我的答案。根是 x = 1，且由于判别式为 0，只有一个重根。

我应该在回答中说明根是 x = 1，并提到它是一个重根。
<|end|><|start|>assistant<|channel|>final<|message|>The equation \(x^2 - 2x + 1 = 0\) has a **double root** (also called a repeated root) at \(x = 1\).

**Solution:**

1. **Using the quadratic formula**:
   \[
   x = \frac{-b \pm \sqrt{b^2 - 4ac}}{2a}
   \]
   For the equation \(x^2 - 2x + 1 = 0\), we have \(a = 1\), \(b = -2\), and \(c = 1\).

   \[
   \Delta = b^2 - 4ac = (-2)^2 - 4 \cdot 1 \cdot 1 = 4 - 4 = 0
   \]

   Since the
--------------------------------------------------------------------------------
```

## 技术细节

### Harmony 响应格式和 Chat Template

`gpt-oss` 模型使用 **Harmony 响应格式**，这是一种专门为推理模型设计的对话格式。

#### 与标准对话格式的区别

传统对话格式中，assistant 只有一个简单的响应。而在 Harmony 格式中：

```python
# 传统格式
{"role": "assistant", "content": "答案是..."}

# Harmony 格式
{
    "role": "assistant",
    "thinking": "让我思考一下...首先...然后...",  # 推理过程
    "content": "答案是..."  # 最终响应
}
```

#### Channel（通道）机制

Harmony 格式使用"通道"来区分不同类型的输出：

- **analysis**：用于内部推理和思考过程
- **commentary**：用于辅助说明和评论
- **final**：用于最终呈现给用户的响应

#### Chat Template 的作用

`apply_chat_template()` 方法将结构化的消息转换为模型可以理解的文本格式：

```python
# 输入（结构化）
messages = [
    {"role": "system", "content": "reasoning language: Chinese"},
    {"role": "user", "content": "What is 2+2?"}
]

# 输出（格式化文本）
<|start|>system<|message|>You are ChatGPT...
<|start|>developer<|message|>reasoning language: Chinese<|end|>
<|start|>user<|message|>What is 2+2?<|end|>
```

这个过程包括：
- 添加特殊 token（`<|start|>`, `<|end|>`, `<|message|>`, `<|channel|>` 等）
- 注入默认系统提示
- 正确处理 developer 和 system 消息
- 设置推理级别和有效通道

### 数据集格式

`HuggingFaceH4/Multilingual-Thinking` 数据集已经采用 Harmony 格式，包含：
- 系统提示（指定推理语言）
- 用户消息（问题）
- 助手推理（思维链，通过 `thinking` 字段或 `analysis` 通道）
- 助手响应（最终答案，通过 `content` 字段或 `final` 通道）

### LoRA 优势

1. **内存效率**：只训练少量参数（通常 <1% 的模型参数）
2. **快速训练**：减少计算需求
3. **易于部署**：可以将 LoRA 权重与基础模型合并
4. **多适配器**：可以为不同任务训练多个 LoRA 适配器

## 性能优化建议

### 1. 减少显存使用（针对 80GB GPU）

由于峰值显存需求 97GB，以下是在 80GB GPU 上运行的优化策略：

```bash
# 方案 1: 进一步减小批次大小
python gpt_oss_20b_sft.py --batch_size 2 --max_seq_length 1536

# 方案 2: 减小序列长度
python gpt_oss_20b_sft.py --batch_size 3 --max_seq_length 1024

# 方案 3: 组合优化
python gpt_oss_20b_sft.py --batch_size 2 --max_seq_length 1024
```

**注意**: 这些修改会偏离 OpenAI Cookbook 的原始配置，可能影响训练效果。当前默认配置（batch_size=4, max_length=2048）已经与官方教程完全一致。

### 2. 使用多 GPU 训练

```bash
# 使用 DeepSpeed ZeRO-3（推荐）
deepspeed --num_gpus=2 gpt_oss_20b_sft.py --mode train

# 或使用 PyTorch FSDP
torchrun --nproc_per_node=2 gpt_oss_20b_sft.py --mode train
```

### 3. 梯度检查点（Gradient Checkpointing）

默认已启用（`gradient_checkpointing=True`），会降低训练速度但节省显存。

## 常见问题

**Q: 为什么需要 97GB 显存？我的 H100（80GB）够用吗？**
A: 不够用。训练过程中峰值显存会达到 97GB，单卡 80GB GPU 会出现 OOM 错误。建议使用 H200（141GB）或多 GPU 训练。

**Q: 显存不足怎么办？**
A: 有几个选择：
   1. 使用 H200 GPU（推荐，可完全按 notebook 配置运行）
   2. 使用多卡训练（2 张 H100）
   3. 减少批次大小和序列长度（会偏离原始配置）
   4. 使用 DeepSpeed ZeRO-3 或 FSDP

**Q: 可以使用 A100（80GB）训练吗？**
A: 不建议。A100 和 H100 都是 80GB 显存，都会遇到 OOM 问题。

**Q: 为什么官方教程说 H100 可以运行？**
A: 官方教程是理想情况的估计。实际运行时由于额外的开销（激活值、优化器状态等），峰值显存会超过 80GB。本项目基于实际测试经验建议使用 H200。

**Q: 可以训练其他语言吗？**
A: 可以！只需准备相应语言的推理数据集即可。由于模型具有强大的零样本泛化能力，即使某种语言不在训练数据中，模型也可能表现良好。

**Q: 什么是 Harmony 格式？为什么要使用它？**
A: Harmony 是 gpt-oss 模型使用的专门格式，它允许模型将推理过程（thinking/analysis）和最终响应（content/final）分开。这使得：
   - 推理过程透明可见
   - 可以用不同语言进行推理和回答
   - 支持更复杂的多步骤推理

**Q: 我需要手动处理 Chat Template 吗？**
A: 不需要。TRL 的 `SFTTrainer` 会自动调用 `apply_chat_template()` 来格式化数据集。你只需要确保数据集符合标准的消息格式（包含 `role` 和 `content` 字段）。

**Q: 训练后如何评估模型？**
A: 可以在多语言测试集上评估推理质量、准确性和流畅度。关注两个方面：
   1. 推理过程是否清晰、逻辑正确
   2. 最终答案是否准确

**Q: 修改超参数后会影响效果吗？**
A: 会的。当前默认配置已与官方教程完全一致（batch_size=4, learning_rate=2e-4, lora_rank=8 等）。进一步减小批次大小、序列长度等会偏离官方配置，可能影响最终模型质量。

## 参考资料

- [OpenAI Cookbook 官方教程](https://cookbook.openai.com/articles/gpt-oss/fine-tune-transfomers)
- [OpenAI GPT-OSS-20B 模型](https://huggingface.co/openai/gpt-oss-20b)
- [Multilingual-Thinking 数据集](https://huggingface.co/datasets/HuggingFaceH4/Multilingual-Thinking)
- [TRL 库文档](https://github.com/huggingface/trl)
- [LoRA 论文](https://arxiv.org/abs/2106.09685)

## 贡献

欢迎贡献代码、报告问题或提出改进建议！

## 许可证

本项目遵循相应开源许可证。使用时请遵守 OpenAI 模型的使用条款。

## 致谢

- OpenAI 团队发布的开源推理模型
- Hugging Face 团队提供的 TRL 库和数据集
- 原始教程作者：Edward Beeching、Quentin Gallouédec、Lewis Tunstall

