# 第 4 章 · 工具

本章把工具看作模型与环境之间的接口。感知提供观测，执行完成计算或改变状态，协作让任务在不同参与者之间继续。工具数量增加后，还需要解决发现与选择。

← [返回主目录](../README.md) · [读本章正文](../book/chapter4.md)

<a id="如何阅读实验"></a>

## 第一次阅读的顺序

1. 从[感知工具](perception-tools/README.md)读取一份本地文件。先找工具名称和参数，再到返回值里找文件内容。换成读取日历时，即使客户端收到响应，也可能只读到缺少授权的错误消息。
2. 在[执行工具](execution-tools/README.md)目录运行 `python cli.py demo`，沿本地写入与编辑过程检查参数、操作风险和执行回执。遇到“校验通过”时，看看它实际检查的是语法、文件内容，还是用户要求的功能。
3. 工具多了以后，比较[主动发现](active-tool-discovery/README.md)怎样检索候选并把选中的工具定义加入上下文。如果任务还需交给别人，去[协作工具](collaboration-tools/README.md)查看主 Agent 怎样接收答复或处理超时。

跑通本地流程后，再看 MCP 传输、Web 界面和提供商适配。想追查打断与取消，可以接着读[第六章的异步运行时](../chapter6/async-agent/)中的 `AgentRuntime._dispatcher` 与 `_handle_interrupt`。核对生产环境的权限策略、沙盒清理、取消确认和服务端回执时，可从[实验记录](EXPERIMENT_LEDGER.md)找到对应场景。

## Skill 分发与安装入口

正文介绍 skills.sh 与 ClawHub 的分发方式。使用 skills.sh 的安装工具时，将下列占位符替换为所选技能仓库的所有者与仓库名：

```bash
npx skills add <owner>/<repo>
```

技能目录见 [skills.sh](https://skills.sh)，安装方式见 [Vercel 发布说明](https://vercel.com/changelog/introducing-skills-the-open-agent-skills-ecosystem)；OpenClaw 的技能查找和版本管理见 [ClawHub 文档](https://docs.openclaw.ai/clawhub)。安装后检查宿主实际加载的元数据、操作说明与脚本权限。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 4-1 | [active-tool-discovery](active-tool-discovery/) | ✅ | Qwen3-4B、127 个工具：两组均覆盖三个任务的必需能力，并在适配层补齐参数和代码后通过产物检查；主动发现减少定义文本量，完整任务质量需另行评估 |
| 4-2 | [perception-tools](perception-tools/) | ✅ | 感知工具 MCP：搜索、文档与多模态、文件系统及公共数据已留存调用；日历与 Notion 等待授权配置 |
| 4-3 | [multimodal-agent](multimodal-agent/) | ✅ | 对比原生多模态、提取为文本、工具化分析三种策略在保真度、成本和灵活性上的权衡 |
| 4-4 | [execution-tools](execution-tools/) | ✅ | 执行工具 MCP：20 次正式调用已通过 13/15 门禁，含 GitHub PR、Xvfb 桌面操作与 KVM Android 模拟器操作；仅真实日历/邮件授权仍阻塞 |
| 4-5 | [collaboration-tools](collaboration-tools/) | ✅ | 协作工具 MCP：子 Agent 生命周期、两种上下文交接、人工答复与超时；Email/Telegram/Slack 真实通知等待服务配置 |
| — | [active-tool-selection](active-tool-selection/) | ✅ | 让 Agent 根据任务需求主动选择最合适的工具组合，而非被动接受预定义工具集 |

> 此外，[`chapter4/docker-compose.yml`](docker-compose.yml) 与 [`chapter4/DOCKER_DEPLOYMENT.md`](DOCKER_DEPLOYMENT.md) 提供了将上述 MCP 工具服务器容器化部署的参考方案。

## 正式实验验收

真实运行、回执、哈希和逐项验收范围记录在 [EXPERIMENT_LEDGER.md](EXPERIMENT_LEDGER.md)。实验 4-1 统计适配层辅助执行下的必需能力覆盖；实验 4-2、4-4、4-5 的私有数据、外部变更或通知仍有授权配置缺口。实验 4-2 的 45 个普通文件哈希一致，一条历史符号链接的目标与清单记录不一致，已在台账中注明。实验 4-3 保留了同一图表下三条处理路径的完整回答与调用记录。

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **设计文档** | 仅包含架构与实现方案，可运行代码仍在完善中 |
