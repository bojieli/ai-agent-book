# Chapter 7 · Model Post-Training

> A comprehensive view of the three stages: pre-training, SFT, and RL. When to choose SFT vs. RL, RLHF, algorithm comparison, data and environments, and cutting-edge exploration into teaching models tool calling and improving sample efficiency.

← [Back to main README](../README.en.md) · 📖 [Read chapter text](../book-en/chapter7.md)

## Companion Projects

| Project | Type | Description |
| --- | :--: | --- |
| [AdaptThink](AdaptThink/) | 📖 | Teaches reasoning models to adaptively choose their reasoning mode (Thinking vs NoThinking) based on problem difficulty. Through constrained optimization and importance sampling, it significantly reduces reasoning costs (45-69%) while improving accuracy. Based on the DeepSeek-R1-Distill-Qwen model, trained using the DAPO algorithm. |
| [retool](retool/) | 📖 | Uses multi-turn dialogue and a code sandbox to enhance the mathematical reasoning ability of large language models. Through a two-stage training process of SFT and RL, the model learns to use a code execution environment to assist in solving mathematical problems. Based on Qwen2.5-32B-Instruct, trained on the AIME 2024 dataset, using the DAPO algorithm and SandboxFusion sandbox. |
| `AWorld/` · [AWorld-train](AWorld-train/) | 📖 | Trains embodied agents based on the AWorld framework, enabling agents to perform complex tasks in a virtual environment and learn from experience. |
| `SFTvsRL/` | 📖 | Systematically compares the effectiveness of Supervised Fine-Tuning (SFT) and Reinforcement Learning (RL) on different tasks, analyzing the strengths, weaknesses, and suitable application scenarios of both methods. |
| `verl/` | 📖 | verl is an efficient reinforcement learning framework specifically designed for RLHF training of large language models, supporting various algorithms such as PPO, GRPO, and DAPO. |
| [Intuitor](Intuitor/) | ✅ | Trains the intuitive reasoning ability of models, enabling them to make quick, reasonable judgments without requiring detailed chains of thought. |
| [MultilingualReasoning](MultilingualReasoning/) | ✅ | Trains the reasoning ability of models in multiple language environments, improving performance on cross-lingual tasks. |
| [SpatialReasoning](SpatialReasoning/) | 📖 | Focuses on training the spatial reasoning ability of models to handle problems involving spatial relationships such as position, direction, and distance. |
| [SimpleVLA-RL](SimpleVLA-RL/) | 📖 | Combines vision, language, and action in reinforcement learning training, enabling models to understand visual input and execute corresponding actions. |
| [continued-pretraining](continued-pretraining/) | ✅ | Performs continued pretraining on domain-specific data to improve model performance in the target domain. |
| [MiniMind-pretrain](MiniMind-pretrain/) | 📖 | Pretrains a small language model from scratch to understand the complete pretraining process and key technologies. |
| [sesame](sesame/) | ✅ | Focuses on training and evaluation methods for sequence modeling tasks. |
| [orpheus](orpheus/) | ✅ | Trains models for music generation and understanding. |
| `tinker-cookbook/` | 📖 | Collects various practical tips and best practices for model training. |
## Project Types

| Icon | Type | Meaning |
| :--: | --- | --- |
| ✅ | **Standalone** | Full code in this repo, runs after configuring API Key |
| 📖 | **Reproduction Guide** | Detailed doc depending on **external repos** to `git clone` |
| 🚧 | **Design Doc** | Architecture/implementation plan only, runnable code still WIP |
