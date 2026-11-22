# 第 1 章 · Agent 基础知识

本章从一条可见的执行轨迹开始，理解模型怎样读取上下文、调用工具并利用结果继续工作。先学会解释一次运行，再讨论不同设计的优劣。

← [返回主目录](../README.md) · [读本章正文](../book/chapter1.md)

<a id="从哪里开始"></a>

## 第一次阅读的顺序

1. 从[离线搜索轨迹](web-search-agent/README.md)开始。先找到模型提出的查询，再找到工具返回的内容，想想下一轮判断用到了哪条信息。演示中的搜索结果预先写好，无需 API Key。
2. 到[上下文消融实验](context/README.md)选定一个模型，给它同一道计算题，分别保留和移除工具结果。想弄清两次输入如何变化，可以从 `main.py` 跟到 `agent.py` 中组装消息的位置。
3. 读[服务端托管研究任务](search-codegen/README.md)，对比谁在执行搜索与计算。最后到[文生图实验](image-gen-workflow/README.md)，逐项核对用户要求的文案、画面和风格，判断多加一步改写有没有帮助。

这四个实验围绕正文的公式 **Agent = LLM + 上下文 + 工具** 展开。相同的模型能否得到有用的观测、继续上次的任务，取决于 Harness 怎样组织消息和衔接工具。笔者看重 Harness 工程，也正是因为这些设计会改变用户最终拿到的结果。

正文中的简化代码用于解释流程，实验目录中的代码负责实际运行。
如果你要核对书中的实验结论，再查看 [实验记录](EXPERIMENT_LEDGER.md)：其中列出了运行条件、
服务可用性和结果文件。例如，实验 1-1 的一次五组对照没有观察到“去掉推理内容必然退化”，
因此不要把预期现象当作每次都能复现的结论。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 1-1 | [context](context/) | ✅ | 系统性消融实验展示 Agent 上下文各组件的重要性；支持阿里云百炼直连 Qwen、SiliconFlow Qwen、字节 Doubao、月之暗面 Kimi 等多提供商 |
| 1-2 | [web-search-agent](web-search-agent/) | ✅ | Kimi K3 决定查询与后续步骤，客户端 Harness 维护循环，Formula 服务执行搜索 |
| 1-3 | [search-codegen](search-codegen/) | ✅ | 通过 Responses API 组织服务端托管搜索与代码执行；正文采用百炼 qwen3.7-plus 的首都距离和比特币分析记录，分别检查澄清、调用、计算与数据来源 |
| 1-4 | [image-gen-workflow](image-gen-workflow/) | ✅ | 五组具体或宽泛需求，对比 Kimi 改写后调用通义万相与 Gemini、GPT-Image 2 直接生图；检查提示词改写是否保留文案等明确要求，并分别评价场景补充与最终图片 |
| 8-1、8-2（第八章） | [learning-from-experience](learning-from-experience/) | ✅ | 10,000 局 Q-learning + 100 局评估与官方 Kimi K3 第一局双臂实测已验收；[证据](learning-from-experience/validation/20260730_011704/evidence.json)记录 Kimi 17 步成功、零 fallback 及历史点估计差异 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
