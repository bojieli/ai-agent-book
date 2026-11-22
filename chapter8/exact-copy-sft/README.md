# 实验 8-19：特殊字符串的精确复述 SFT

编辑工具要求待替换字符串逐字匹配，而模型可能改动空格、引号或不可见字符。本实验先定位复制链路，再研究监督训练能否改善精确复述。

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

字符显示相同不代表字节相同。错误可能发生在模型生成、分词、序列化或工具参数处理，因此不能看到匹配失败就直接归因于模型。训练目标需要明确采用哪一种一致性标准。

本实验从 Coding Agent 的 `old_string` 匹配失败出发，区分模型复制错误与 tokenizer、序列化、Harness 和工具层错误，然后用未见过的随机字符串和工具参数任务训练 Qwen3-8B 的 LoRA 适配器。训练目标是 byte-exact 复制，而不是语义相似或“看起来一样”。

<a id="learning-1"></a>

## 准备环境与输入

阅读训练命令前，先确认基础模型、数据文件、适配器输出位置和显存要求。把数据准备、训练和评估看作三个独立步骤：前一步得到的文件，是后一步需要核对的输入。

### 数据与输入检查

扩容后先对三类任务、10 种语言上下文和 8 种文章体裁做分层人工抽查，记录见 [`validation/manual_audit.md`](validation/manual_audit.md)；再运行 tokenizer 审计，避免把 tokenizer/序列化损坏误判为模型能力问题。

如果模型在直接复述探针中正确、但工具调用仍失败，应修复 Harness 或工具协议，不应把系统层损坏误报为后训练收益。

<a id="learning-2"></a>

## 按照步骤完成实验

先查看随机字符串与工具参数样例，运行分词和序列化审计，确认输入输出链路保留内容。随后按下文训练模型，在未见长度、字符组合和包装上下文中评估。

### 运行

```bash
cd chapter8/exact-copy-sft
python generate_data.py
python train_sft.py --model Qwen/Qwen3-8B
python evaluate.py --model Qwen/Qwen3-8B --adapter output/adapter
python tokenizer_audit.py
```

<a id="learning-3"></a>

## 分析结果与形成判断

直接复述成功而工具调用失败，提示问题可能在接口层。评估应分别报告这些路径，并检查训练数据与测试字符串是否独立。

### 准备训练与评估环境

训练和评估必须使用本机 CUDA GPU 与开源 Hugging Face 模型。数据按随机种子、字符串长度、token 组合和上下文包装隔离；`validation/` 保存训练回执和独立回归报告。

### 已有训练结果

本机 RTX PRO 6000 实测：1024 条训练样本、256 条留出样本、256 条边界样本，训练 2 个 epoch、Qwen3-8B bf16 LoRA。留出集 byte-exact accuracy 从基座 37.5% 提升到 78.9%，独立边界集为 80.1%；平均首次字节分歧位置分别为 54.0 和 54.2。

另用 512 条留出/边界探针审计 3 个开源 tokenizer：Qwen3 与 Qwen2.5 round-trip 均为 80.1%，Mistral 为 100%，说明 tokenizer 层也必须单独设回归门禁。结果文件见 `validation/eval_base_eval.json`、`validation/eval_adapted_eval.json`、`validation/eval_adapted_boundary.json` 和 `validation/tokenizer_audit.json`。

### 检查自己的解释

如何用最小实验区分模型漏了一个空格与传输层进行了 Unicode 归一化？
