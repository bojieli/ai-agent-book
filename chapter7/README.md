# 第 7 章 · 模型后训练

> 预训练/SFT/RL 三阶段：何时选 SFT、何时选 RL，工具调用内化、样本效率

← [返回主目录](../README.md) · 📖 [读本章正文](../book/chapter7.md)

## 配套项目

| 项目 | 类型 | 一句话说明 |
| --- | :--: | --- |
| [AdaptThink](AdaptThink/) | 📖 | 让推理模型按问题难度自适应选 Thinking/NoThinking，约束优化 + 重要性采样降成本 45–69% 同时提准确率 |
| [retool](retool/) | 📖 | 多轮对话 + 代码沙箱提升数学推理，SFT→RL 两阶段；Qwen2.5-32B + AIME 2024 + DAPO + SandboxFusion |
| `AWorld/` · [AWorld-train](AWorld-train/) | 📖 | 基于 AWorld 框架训练具身 Agent，在虚拟环境中执行任务并从经验中学习 |
| `SFTvsRL/` | 📖 | 系统性对比监督微调与强化学习在不同任务上的效果与适用场景 |
| `verl/` | 📖 | 为 LLM RLHF 设计的高效 RL 框架，支持 PPO/GRPO/DAPO 等 |
| [Intuitor](Intuitor/) | ✅ | 训练模型的直觉推理，快速做出合理判断而不依赖详细思考链 |
| [MultilingualReasoning](MultilingualReasoning/) | ✅ | 训练模型在多语言环境下的推理能力，提升跨语言任务表现 |
| [SpatialReasoning](SpatialReasoning/) | 📖 | 训练模型的空间推理能力，处理位置、方向、距离等空间关系 |
| [SimpleVLA-RL](SimpleVLA-RL/) | 📖 | 视觉-语言-动作 RL，让模型理解视觉输入并执行相应动作 |
| [continued-pretraining](continued-pretraining/) | ✅ | 在特定领域数据上持续预训练，提升目标领域表现 |
| [MiniMind-pretrain](MiniMind-pretrain/) | 📖 | 从零预训练小型 LLM/VLM，理解完整预训练流程与关键技术 |
| [sesame](sesame/) | ✅ | 专注于序列建模任务的训练和评估方法 |
| [orpheus](orpheus/) | ✅ | 训练模型的音乐生成与理解能力 |
| `tinker-cookbook/` | 📖 | 收集各种模型训练的实用技巧与最佳实践 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
