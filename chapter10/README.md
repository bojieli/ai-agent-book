# 第 10 章 · 多 Agent 协作

把一本书分给多个 Agent 翻译，负责统稿的 Agent 只接收文件路径和进度，能省下多少上下文？全书会不会更早译完？这两个问题要看不同的记录。本章从角色切换讲到并行搜索和社会模拟，沿途考察每个 Agent 能看到什么、如何交接工作，以及谁来核对最后的结果。

[返回主目录](../README.md) · [读第十章正文](../book/chapter10.md)

## 第一次做实验

1. **先看一次角色交接。** [实验 10-1](multi-role-transfer/README.md)里有一道投资简报题。先找出加载写作规程的那一步，再看用户最终收到哪段文字。为什么四种角色都出场了，简报却没有交付？读完一条轨迹，再看[30 对任务的汇总](multi-role-transfer/validation/comparison/runs/exp10-1-qwen35flash-20260809-v2/REPORT.md)，比较两种做法的通过率、耗时和用量。
2. **再看两章书怎样交给多人翻译。** 打开[实验 10-2 的运行记录](book-translation/validation/real_20260730T061500Z_v4/evidence.json)，从两组的 `tracker.by_agent` 读起：单 Agent 最大一次请求用了 94,355 个输入 token，分工后最大一次请求是术语整理者的 49,807 个；完成整项工作的时间却从约 254 秒增至 271 秒。接着读 `markdown_fidelity`：第一单元原稿和协作译稿各有两个代码块、六幅插图，但代码内容和图片链接都未完全保留。交付时怎样逐项对照，可回到[翻译实验](book-translation/README.md)。
3. **最后看并行搜索何时可以结束。** [实验 10-4](parallel-web-research/README.md)让多个浏览器会话同时查找目标。一个成员先找到后，管理者还要防止重复结算，并确认其余成员已停止。沿四会话测试的记录查看一次终止广播、三个确认和浏览器关闭事件，再用十站点的串行与并行计时比较速度。

如果关心成员各自能看到哪些私有信息，可继续读[语音狼人杀](voice-werewolf/README.md)，对照法官掌握的完整状态与玩家在发言、投票时收到的消息。

## 配套项目

| 编号 | 项目 | 类型 | 一句话说明 |
| :--: | --- | :--: | --- |
| 10-1 | [multi-role-transfer](multi-role-transfer/) | ✅ | [正式 v2 对照](multi-role-transfer/validation/comparison/runs/exp10-1-qwen35flash-20260809-v2/REPORT.md)要求 Skill 路径先加载规程。按程序验收，加载 Skill 通过 15/30 项，切换角色通过 2/30 项；两组各通过 6/6 道边界题。报告保留了 289 份模型回执、31 份 Tavily 搜索回执，以及独立评审交换答案顺序后的 60 次盲评 |
| 10-2 | [book-translation](book-translation/) | ✅ | [正式 ARK v4](book-translation/validation/real_20260730T061500Z_v4/evidence.json)在英文版第 1–2 章的 242,090 字节、23 图、14 代码块上完成 26 单元双臂对照：12/12 门禁、39 份原始裁判回执和 37 个溯源 hash 均通过；单次输入峰值从 94,355 降至 49,807 个 token，总用量降至单 Agent 的约 1/6.48且匿名质量 4.654 > 4.481，但慢 6.57%，宽泛术语一致率与 Markdown 精确保真也出现明确负结果 |
| 10-3 | [autonomous-phone-registration](autonomous-phone-registration/)；固定并发的 [TalkAct 复现记录](talkact-reproduction/) | ✅ / 📖 | 主路径的 [WebRTC raw-v4](autonomous-phone-registration/validation/runs/exp10-3-webrtc-raw-20260731-v4/manifest.json)用真实 ARK 自主工具调用、Playwright、双向 RTP、本机 TTS/Whisper ASR 和一次 localhost 提交跑通 6 字段注册，9/9 行为门禁通过；固定拓扑基线的 [Anthropic-caller 运行](talkact-reproduction/validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2/acceptance.json)保留 16/16 局并通过 17/17 门禁。两类证据分别验证自主启动与并行协作，不合并统计 |
| 10-4 | [parallel-web-research](parallel-web-research/) | ✅ | [同一次真实验收运行](parallel-web-research/validation/runs/exp10-4-real-receipts-20260730-v2/manifest.json)覆盖 10 站点串并行与 4 会话级联：12/12 门禁通过、实测加速 1.872×、24 份完整浏览器观测、3 份带 response ID/usage 的 ARK 原始响应和 114 条总线事件均由运行时 manifest 绑定；7 个实际源码/输入 hash 与全部 artifact hash 已复核一致，凭据扫描为零 |
| 10-5 | [Generative Agents 正式复现](generative-agents/) + `generative_agents/` | 📖 | [Qwen 3.7 Flash 正式运行](generative-agents/validation/runs/exp10-5-qwen37flash-20260804-v1/acceptance.json)完成三组各 25 Agent、17,280 步、两个虚拟日的完整社会实验；148,856 份真实 provider 回执零逻辑错误，14/14 门禁通过。自定义气候韧性工作坊未扩散出发起人，是保留的负结果；关闭反思后证据关联反思为零，基线在 25 人盲评中以 17:8 获偏好且四项均分更高 |
| 10-6 | [voice-werewolf](voice-werewolf/) | ✅ | [同一次 v11 真实验收](voice-werewolf/validation/runs/exp10-6-simulated-user-openrouter-20260803-v11/acceptance_report.json)完成 3 个昼夜投票循环、6 次 LLM 工具→macOS `say`→OpenRouter 原生音频 ASR 回环、信息隔离和规则胜负；四项策略门禁全通过，13 个唯一响应 ID、1,650 音频 token、27 个非空 TTS 事件、动作历史和裁判溯源均保留，独立验证复核 6/6 音频动作边界 |

## 项目类型说明

| 图标 | 类型 | 含义 |
| :--: | --- | --- |
| ✅ | **可独立运行** | 本仓库自带完整代码，配置好 API Key 即可运行 |
| 📖 | **复现指南** | 依赖需自行 `git clone` 的**外部仓库**（训练框架、评测基准等） |
| 🚧 | **进行中** | 实现或实验要求的验收证据尚未完整；可能已有可运行代码，但不得视为完整验收 |
