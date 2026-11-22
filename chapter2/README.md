# 第 2 章 · 上下文工程

用户问“温哥华现在几点，天气怎样？”模型需要先向客户端索取时间和天气，再根据两条工具回执回答。读懂这样一次往返，就能继续追问：下一轮哪些内容可以复用，任务进行得很久以后，哪些记录还要留给模型？

[返回主目录](../README.md) · [读第二章正文](../book/chapter2.md) · [各实验的运行记录](EXPERIMENT_LEDGER.md)

## 从一次请求读到一段长任务

1. 在[实验 2-1](local_llm_serving/README.md)打开温哥华任务记录，找出模型请求的两个工具、客户端交回的结果，以及最后一句答复各自用了哪条信息。正文里的 API 循环就是这样把新观察接到已有消息之后的。
2. 到[实验 2-3](kv-cache/README.md)比较稳定基线和重排工具的两行。两组的命中率都显示为 100%，复用的输入却分别是 768 和 256 个 token。先按报告里的分母算一遍，再沿着请求查共同前缀在哪里结束。若要研究规则顺序怎样影响办事结果，可接着读[实验 2-4 的航空改签案例](prompt-engineering/README.md)。
3. 在[实验 2-10](context-compression/README.md)中，助理连续检索多位创始人的职业去向。先选一种压缩策略，读它最后交付的回答，再看压缩前后的字符数、主模型的 token 用量和窗口溢出次数。文本变短可以从记录中复算；人物和职业是否仍然对应，则要回到来源逐项核实。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 2-1 | [local_llm_serving](local_llm_serving/) | ✅ | 跨平台本地 LLM 部署，自动选 vLLM/Ollama 后端，展示 0.6B 小模型也能有出色工具调用 |
| 2-2 | [attention_visualization](attention_visualization/) | ✅ | 可视化 LLM 完整 token 序列与注意力权重分布，理解模型如何处理上下文、推理与调用工具 |
| 2-3 | [kv-cache](kv-cache/) | ✅ | 探索不同上下文管理模式对 KV Cache 的影响，比较前缀变化、历史裁剪和消息格式对缓存与任务推进的影响 |
| 2-4 | [prompt-engineering](prompt-engineering/) | ✅ | 扩展 Tau-Bench，量化语气风格、指令组织、工具描述等因素对任务完成率的影响 |
| 2-5 | [prompt-injection](prompt-injection/) | ✅ | 3 种攻击场景 × 4 种防御配置的对照实验，记录各配置的行为与外部影响；本次 60 次运行均未达成注入目标 |
| 2-6 | [agent-skills-ppt](agent-skills-ppt/) | ✅ | 固定 Anthropic 官方 PPTX Skill + 真实论文 PDF，运行时可为 Claude Code 或等价的 Kimi Code CLI（已实测通过：13 页演示文稿、4 张论文原图、完整渐进式披露轨迹），旧 python-pptx 同构 demo 不作为正文验收 |
| 2-7 | 正文实验 | 🚧 | 从个人范文创建“去 AI 味”写作 Skill；练习 Skill 的触发条件、规则、示例、作用域与迭代维护，不依赖独立代码项目 |
| 2-8 | [状态栏注意力对照](attention_visualization/README.md#status-bar-comparison) | ✅ | 在同一份催退款通话记录后加上或省略 3/3 提醒，对照两组回答和注意力图 |
| 2-9 | [system-hint](system-hint/) | ✅ | 研究系统提示对 Agent 行为的影响，探索如何通过优化系统提示提升性能 |
| 2-10 | [context-compression](context-compression/) | ✅ | 实现并对比摘要、关键信息提取、语义压缩等多种策略，比较六种压缩策略的用量、溢出与最终回复；可按[六组归档](context-compression/results/kimi_k3_real_20260718.json)核对最终回复与汇总用量 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
