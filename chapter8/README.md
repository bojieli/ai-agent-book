# 第 8 章 · Agent 的自我进化

> 不改权重也能成长：经验学习、主动工具发现、从使用者到创造者

← [返回主目录](../README.md) · 📖 [读本章正文](../book/chapter8.md)

## 配套项目

| 项目 | 类型 | 一句话说明 |
| --- | :--: | --- |
| [gaia-experience](gaia-experience/) | ✅ | 基于 AWorld + GAIA 的「学习-应用」闭环：自动总结成功轨迹为结构化经验，新任务中检索应用 |
| [browser-use-rpa](browser-use-rpa/) | ✅ | 浏览器工作流录制系统，把重复操作封装为参数化工具，从 LLM 推理切换到自动化执行 3–5 倍加速 |
| [prompt-distillation](prompt-distillation/) | ✅ | 将复杂提示的效果蒸馏进模型参数，减少推理提示长度，把上下文经验固化为参数化知识 |
| [prompt-auto-optimization](prompt-auto-optimization/) | ✅ | 以 tau-bench 航空客服「过度转接」为例，Coding Agent 读/改 prompt 文件 → 重新评测 → 验证闭环 |
| [active-tool-discovery](active-tool-discovery/) | ✅ | 对比「全量注入 120+ 工具 schema」与「少量基础工具 + discover_tools 元工具按需检索」，省 token 防错选 |
| [self-evolving-tools](self-evolving-tools/) | ✅ | Alita 式「最小预定义，最大自我进化」：五个通用元工具，自己上网找库/读文档/沙箱测试并封装复用 |
| [self-evolution-eval](self-evolution-eval/) | ✅ | 20 个跨领域任务 + 四层分层验证 harness + 可控参考 Agent，考察发现/创造/复用质量 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
