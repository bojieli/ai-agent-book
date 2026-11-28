# 3.0 版变更说明（相较 2.0 版）

本文汇总《深入理解 AI Agent：设计原理与工程实践》中文原版从 **2.0 版**升级至 **3.0 版（及当前 `main` 分支最新修订）**的实质性变化。

> 💡 **版本关系速览**：
> - **1.4 → 2.0**：章节结构重组——将原第四章“异步交互”与原第九章“多模态 Agent”合并重组为新的**第六章“交互：观察与动作空间的扩展”**，原第 6、7、8 章依次顺延为第 7、8、9 章。**目前除中文原版（`book/`）与俄语版（`book-ru/`）已升级至 3.0 版外，其余非中文社区翻译版对应 2.0 版章节结构。**
> - **2.0 → 3.0**：在 2.0 版十章结构的基础上，对中文原版（`book/`）进行了**全书出版级教学重订、技术事实与实验记录核验、115 幅黑白灰度矢量插图重绘**，并在第三章、第六章等章节新增了实质性的架构小节与实验（全书配套实验由 109 个扩展至 **110 个**，思考题由 93 道扩展至 **95 道**）。
> - 📖 **书内附录导航**：中文版 PDF、EPUB 与在线阅读站点已在**后记末尾**新增[《附录：3.0 版实质性变更与章节速查（面向 2.0 版读者）》](../book/afterword.md#附录30-版实质性变更与章节速查面向-20-版读者)，提供所有新增与实质性修订小节的书内超链接。

---

## 一、已读过 2.0 版的读者：建议重点补读的新增内容（附直达链接）

如果你已经读过 2.0 版，无需从头重读全书，建议优先阅读以下新增或大幅扩充的章节内容（提供 **🌐 Astro 在线阅读链接** 与 **📄 仓库源码锚点链接**）：

1. **第六章新增小节与实验（异步接入层 + 语音双模型工具调用路由）**
   - **新增小节「接入层：多种来源，一种事件」与「从邮件事件建立基本循环」**
     - 🌐 在线阅读：[接入层：多种来源，一种事件](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#接入层多种来源一种事件) · [事件处理机制](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#事件处理机制) · [从邮件事件建立基本循环](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#从邮件事件建立基本循环)
     - 📄 仓库源码：[`book/chapter6.md#接入层多种来源一种事件`](../book/chapter6.md#接入层多种来源一种事件) · [`book/chapter6.md#从邮件事件建立基本循环`](../book/chapter6.md#从邮件事件建立基本循环)
     - **核心内容**：系统梳理多渠道事件（邮件、日历、Slack、GitHub、定时任务、长耗时子进程）如何通过统一的 `IngressAdapter` 转换为标准化 `Event`，涵盖会话线程映射、乱序/晚到事件处理、幂等去重，以及 `dsh-superagent` 的主会话（Main Session）/执行会话（Executor Session）分离与工单（Ticket）生命周期管理。配套**实验 6-1** 扩充了多源接入与故障注入测试，新增**图 6-1**、两张接入层对比表及**思考题第 13 题**。
   - **新增实验与架构分析「实验 6-7 ★★：语音 Agent 的工具由前台还是后台调用」**
     - 🌐 在线阅读：[认知时序：实时交互与深度思考](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#认知时序实时交互与深度思考)
     - 📄 仓库源码：[`book/chapter6.md#认知时序实时交互与深度思考`](../book/chapter6.md#认知时序实时交互与深度思考) · 实验代码 [`chapter6/voice-tool-routing/`](../chapter6/voice-tool-routing/)
     - **核心内容**：针对双模型语音 Agent（前台快模型负责对话与倾听、后台慢模型负责推理与决策），量化对比三种工具调用路由方案的端到端延迟（$2L_f + T$、$2L_f + 2L_b + T$、$L_f + T$）、ASR 传话信息损耗与运行期记忆注入机制。原实验 6-7 至 6-14 顺延编号为 **实验 6-8 至 6-15**，并新增**思考题第 14 题**。
2. **第三章新增「知识的使用方式建模」**
   - 🌐 在线阅读：[结构化索引：建立层次与关联](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#结构化索引建立层次与关联)
   - 📄 仓库源码：[`book/chapter3.md#结构化索引建立层次与关联`](../book/chapter3.md#结构化索引建立层次与关联)
   - **核心内容**：在「为相关条目建立链接与索引」中，以台风航班取消通知草拟为例，区分检索命中的两类知识属性：**事实/规则的兼容性**（如品牌语气规范与隐私合规规范需同时生效约束输出）与**经验/预案（Playbook）的排他性**（如“已出票改签预案”与“未出票退订预案”共享同一触发问题但适用条件互斥，检索后必须先检查状态再择一加载），补齐了从“相关性排序”到“实际拼入上下文”之间的建模空白。
3. **第二章新增 Claude Preserved Thinking 与缓存前缀边界说明**
   - 🌐 在线阅读：[KV Cache 友好的上下文设计](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#kv-cache-友好的上下文设计) · [KV Cache 与 Prompt Cache：两个层级的缓存](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#kv-cache-与-prompt-cache两个层级的缓存) · [缓存作为架构约束](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#缓存作为架构约束)
   - 📄 仓库源码：[`book/chapter2.md#kv-cache-友好的上下文设计`](../book/chapter2.md#kv-cache-友好的上下文设计)
   - **核心内容**：补充推理模型跨轮次保留历史思考块（Preserved Thinking）与前缀稳定性的关系：改动历史消息前缀不仅会导致 KV Cache / Prompt Cache 失效，还会迫使模型丢弃已缓存的历史推理链；同时厘清了请求内 KV Cache 与跨请求 Prompt Cache（图 2-10）的边界。

---

## 二、全书核心概念与术语口径的统一

3.0 版对全书的技术概念边界进行了系统校准，主要术语变化如下表：

| 2.0 版表述 | 3.0 版表述 | 变更原因与技术考量 |
| :--- | :--- | :--- |
| 引言 | **前言**（新增 `## 本书的使命`） | 明确“实践 → 方法 → 原则”的写作主线与穿越模型迭代的工程原则 |
| 观察空间（Observation Space） | **观测空间** | 全书统一控制论与强化学习标准译法（第 1、6、8 章） |
| 工具：Agent 的手脚 | **工具：Agent 的感官和手脚** | 工具不仅负责改变外部状态（执行），也负责主动获取外部信息（感知） |
| 上下文：Agent 的眼睛 / 决定能力上限 | **上下文：Agent 的当前决策视野 / 让模型能力用于具体任务** | 区分外部环境的“观测空间”与当次推理实际送入模型的“当前决策视野” |
| 从提示工程到 Loop 工程 | **从提示工程到 Graph 工程：工程关注范围的扩展** | 覆盖提示词、上下文、Loop、多组件工作流与多 Agent 协作图的完整演进 |
| Harness 五要素与「构建」部分的对应 | **Harness 五项功能与全书的对应** | 将功能职责（供给上下文、提供工具、建立护栏、管理生命周期、可观测与评估）与生产实现分层 |
| 上下文学习的内部机制：检索而非推理 | （独立小节删除，内容并入「把重复计算的结果整理为可用知识」） | 不再断言“上下文学习是检索而非推理”；改为介绍 Dherin 等人的理论解释：注意力层与 MLP 的组合可表示为与上下文相关的低秩权重更新，推理时模型权重不变 |
| On-Policy 自蒸馏 | **在轨自蒸馏：用额外上下文构造教师** | 统一第 8 章强化学习与在轨蒸馏（On-Policy Distillation）中文术语 |
| Ticket（混合使用） | **工单** | 在第 6 章异步事件处理与第 10 章多 Agent 协作中统一译名与状态机口径 |

---

## 三、分章实质性变更与章节速查（含 Astro 在线阅读链接）

### 前言（[`book/introduction.md`](../book/introduction.md)）
- 新增小节 **「本书的使命」**，结合 Pine AI 三组真实业务演进案例，阐述为何“只补某一代模型短板的设计会被模型升级覆盖，深入复杂业务才能沉淀经得住模型迭代的工程方法”。
- 明确十章之间的递进教学主线，优化图 0-1（全书路线图）与图 0-2（评估驱动三种提升方向：改上下文与工具、改系统架构、做模型后训练）。

### 第一章：AI Agent 入门（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/) · [`book/chapter1.md`](../book/chapter1.md)）
- **概念边界澄清**（[观测空间与动作空间](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#观测空间与动作空间模型与世界的接口) · [工具：Agent 的感官和手脚](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#工具agent-的感官和手脚) · [上下文：Agent 的当前决策视野](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#上下文agent-的当前决策视野)）：明确模型（Model）与运行时（Harness）的分工，补充 RAG 场景下模型能力与 Harness 检索拼装的职责边界（`#1187`）；将“错误可由 Harness 约束、验证和纠正”贯穿全章（`#1124`）。
- **实验与产品事实核验**（[从提示工程到 Graph 工程](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#从提示工程到-graph-工程工程关注范围的扩展) · [编排模式：工作流与自主](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#编排模式工作流与自主)）：
  - **实验 1-2** 更新为「Kimi K3 的多轮搜索与查询调整」，引用一手技术报告，移除缺乏公开证据的“单任务 200～300 次调用”断言。
  - **实验 1-3** 更新为「Responses API 的托管研究闭环」，采用百炼实际运行记录，并将图 1-5 中“无需客户端 ReAct 循环”明确限定在服务端托管 Responses API 范围内（`#1115`）。
  - **实验 1-4** 更新为「文生图工作流与直接生成的对照」，按 Kimi + 通义万相实际工作流与海报负面提示词检查需求传递。
- **工程细节修正**（[护栏与安全性](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#护栏与安全性) · [Harness 五项功能与全书的对应](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#harness-五项功能与全书的对应)）：图 1-4 统一为四季度数据；补充 BTC 行情超时切换数据源后的交叉核验、退款超时重试前的状态查询与幂等性要求；按生效位置对安全护栏（提示层、执行层、数据层）分层说明。

### 第二章：上下文工程（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/) · [`book/chapter2.md`](../book/chapter2.md)）
- **API 与缓存机制精化**（[从 API 消息到模型 Token：Chat Template](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#从-api-消息到模型-tokenchat-template) · [KV Cache 与 Prompt Cache：两个层级的缓存](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#kv-cache-与-prompt-cache两个层级的缓存) · [缓存作为架构约束](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#缓存作为架构约束)）：
  - 区分请求内解码阶段的 KV Cache 复用与跨请求的 **Prompt Cache** 前缀复用（修正图 2-10 标注，`#1113`），解释为何向消息列表末尾追加内容不会破坏历史 token 的缓存键值（`#1126`）。
  - 补充 **Claude Preserved Thinking** 机制：说明修改历史前缀为何会导致已保留的推理链失效（`#1151`）。
  - 核对 Qwen（`tool_response` 判定）、DeepSeek（工具/非工具请求模板）、GLM（`clear_thinking`）、Claude（前缀绑定与裁剪协议）及 OpenAI Codex（线程级 `developer` 与轮次级上下文区分）的官方实现细节。
- **提示工程、状态栏与压缩修正**（[提示工程：优化系统提示词](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#提示工程优化系统提示词) · [Agent 状态栏](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#agent-状态栏通过元信息增强-agent-轨迹管理) · [上下文压缩策略](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#上下文压缩策略)）：
  - **实验 2-3**（「上下文管理方式的对照」）、**实验 2-4**（十任务六组提示词对照）、**实验 2-5**（Kimi K3 60 次提示注入防御测试）、**实验 2-6**（13 页 PPTX 与论文图表生成修正）、**实验 2-8**（注意力可视化观察状态栏）与 **实验 2-9**（五案例上下文压缩对照）全部对齐真实实验产物，移除无实验记录支撑的预设百分比断言。
  - **Agent 状态栏**：将理论解释从“强制改变注意力分配”修正为“增量维护显式状态、降低长轨迹检索负担”，并补充状态栏方法本身的取舍与局限（`#1170`）。
  - **上下文学习与压缩**：删除 2.0 版的「上下文学习的内部机制：检索而非推理」小节，相关解释并入[把重复计算的结果整理为可用知识](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#把重复计算的结果整理为可用知识)，改为介绍“与上下文相关的低秩权重更新”这一理论解释；补充 Claude Sonnet 4.5 的“上下文焦虑”观察，区分就地压缩与重置交接（Reset & Handoff）的适用场景。

### 第三章：用户记忆和知识库（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/) · [`book/chapter3.md`](../book/chapter3.md)）
- **新增「知识的使用方式建模」**（[结构化索引：建立层次与关联](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#结构化索引建立层次与关联)）：区分事实与经验（预案）、兼容约束与排他使用，指导检索后的知识组装与冲突消解（`#1246`）。
- **检索与记忆实验核验**（[用户记忆的四种存储格式](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#用户记忆的四种存储格式) · [记忆框架案例](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#记忆框架案例) · [混合检索](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#混合检索合并两路结果再重排) · [智能体化 RAG](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#智能体化-rag由-agent-控制检索过程) · [前沿探索：多模态与参数化记忆](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#前沿探索多模态与参数化记忆)）：
  - 校准余弦相似度取值范围 $[-1, 1]$ 与手算示例数值；明确召回率（Recall）与命中率（Hit Rate）统计口径，并在离线 BM25 与 RAG 评估中显式报告检索失败（`#1249`, `#1252`, `#1253`）。
  - 对齐 **Mem0** 最新官方迁移基准（91.6 / 93.4）及开源版与托管图记忆的功能边界；对齐 **OpenViking** 目录级 `.abstract.md` / `.overview.md` 与字符预算机制。
  - 重订 **实验 3-2 至 3-12** 的实验标题与结果分析（如实验 3-2 四种记忆格式在 48/52/51/49 通过数与全流程 token 上的真实取舍、实验 3-6 重排序 MRR 变化分析、实验 3-8 预算上限与法条覆盖率分析）。
  - 将“跨模态与参数化记忆”调整为「前沿探索：多模态与参数化记忆」，客观界定 User as Engram 的文本事实范围与训练前提。

### 第四章：工具（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/) · [`book/chapter4.md`](../book/chapter4.md)）
- **协议与披露机制边界**（[工具设计的通用原则](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#工具设计的通用原则) · [工具生态：MCP 与 Skill Hub](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#工具生态mcp-与-skill-hub) · [层次化组织与按需加载](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#层次化组织与按需加载)）：
  - 对齐 MCP 协议最新规范（`Streamable HTTP` 传输层演进、服务端工具发现与逐请求元数据），区分旧版 `HTTP+SSE` 与现行流式响应机制。
  - 为 MCP / Agent Skills 的渐进式披露（Progressive Disclosure）、工具描述优化收益（Anthropic 内部复杂参数测试 72% → 90%）、沙盒隔离与 Sidecar 安全检查补充明确的适用前提（`#1129`）：强调 JSON Schema 仅负责结构约束，业务合法性与权限仍须由执行层确定性校验。

### 第五章：Coding Agent 与通用 Agent（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/) · [`book/chapter5.md`](../book/chapter5.md)）
- **结构与安全边界校准**（[Harness 工程在 Coding Agent 中的实践](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#harness-工程在-coding-agent-中的实践) · [故障与错误恢复](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#故障与错误恢复) · [Coding Agent 的安全](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#coding-agent-的安全)）：
  - 修正章首阅读路线图与实际小节顺序的一致性；将“持久化终端”小节重构为 **「工具设计的粒度取舍」**，对比持久化会话与显式环境传参的工程利弊。
  - 明确沙盒机制的权限、网络、挂载与资源限额边界（移除“绝不影响宿主机”的绝对化表述）；补充持久记忆放大提示注入风险的防御分析。
- **16 个实验结果与代码核对**（[代码作为思考工具](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#代码作为思考工具) · [代码作为业务规则的约束](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#代码作为业务规则的约束) · [代码驱动的多媒体生成](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#代码驱动的多媒体生成) · [代码创造代码：Agent 自举](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#代码创造代码agent-自举)）：
  - 对齐 **实验 5-1 / 5-2**（故障恢复与幂等重放范围）、**实验 5-3 / 5-4**（代码思考在 30 题与 84 题基准上的真实得分 11/30 vs 16/30、63/84 vs 33/84，客观分析弱模型何时受益于代码工具）、**实验 5-5**（60 组业务规则代码约束对照）、**实验 5-6 / 5-7**（双 Agent PPT 生成峰值上下文 2.4 万 vs 9.3 万 token）。
  - 明确 **实验 5-15**（动态软件的数据访问边界）中进程内原型与生产级行级安全（RLS）/独立权限入口的差距。

### 第六章：交互：观察与动作空间的扩展（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/) · [`book/chapter6.md`](../book/chapter6.md)）
- **新增「接入层：多种来源，一种事件」与「从邮件事件建立基本循环」**（[接入层：多种来源，一种事件](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#接入层多种来源一种事件) · [事件处理机制](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#事件处理机制) · [从邮件事件建立基本循环](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#从邮件事件建立基本循环)）：
  - 详解多源异构事件归一化、会话路由、乱序与幂等处理、`dsh-superagent` 主/执行会话分离及工单（`工单`）机制；新增 **图 6-1**（全章插图更新为图 6-1 至 6-14）、两张接入层设计表、**实验 6-1** 多源故障注入扩展及**思考题第 13 题**（`#1239`, `#1242`, `#1244`, `#1245`）。
- **新增「实验 6-7 ★★：语音 Agent 的工具由前台还是后台调用」**（[认知时序：实时交互与深度思考](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#认知时序实时交互与深度思考)）：
  - 在「认知时序：实时交互与深度思考」小节中增加快慢双模型工具调用归属的定量分析与实验验证，原实验 6-7 至 6-14 顺延为 **实验 6-8 至 6-15**，新增**思考题第 14 题**（`#1250`, `#1251`）。
- **语音、GUI 与机器人部分精修**（[语音：最自然的人机接口](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#语音最自然的人机接口) · [Computer Use：GUI 自动化 Agent](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#computer-usegui-自动化-agent) · [机器人操作：以 XLeRobot 整理桌面为例](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#机器人操作以-xlerobot-整理桌面为例)）：
  - 核对 Moshi 全双工、Thinking Machines 微轮次、Step-Audio R1.1 / MPS 双模块、τ²-bench voice、SoM、AOI 消融与 Photon-1 世界模型的论文与官方资料，厘清状态模拟与动作学习的边界。

### 第七章：Agent 的评估（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/) · [`book/chapter7.md`](../book/chapter7.md)）
- **评估方法论强化**（[从一条任务理解评估：τ²-bench 的 telecom 领域](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#从一条任务理解评估τ²-bench-的-telecom-领域) · [端到端回归任务与轨迹前缀回归任务](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#端到端回归任务与轨迹前缀回归任务) · [从外部评估到内部评估：生产级 Agent 的评估基础设施](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#从外部评估到内部评估生产级-agent-的评估基础设施)）：
  - 突出生产系统**优先积累轨迹前缀回归（Trajectory Prefix Regression）**的工程判断，以及“提示词变更应按代码变更运行回归测试”的实践原则。
  - 核对 τ²-bench 电信案例（区分“每次只调用一个工具”的规则约束与调用顺序问题）、Verifiers v0.1.9 接口、GAIA / SWE-bench / OSWorld / AndroidWorld 官方基准维护细节。

### 第八章：模型后训练（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/) · [`book/chapter8.md`](../book/chapter8.md)）
- **算法推导与工程优先级厘清**（[何时选择 Mid-training、SFT 与 RL](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#何时选择-mid-trainingsft-与-rl) · [单轮强化学习：记忆与泛化的对照](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#单轮强化学习记忆与泛化的对照) · [路径约束与 RLVP](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#路径约束与-rlvp) · [在轨自蒸馏：用额外上下文构造教师](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#在轨自蒸馏用额外上下文构造教师)）：
  - 强调“先验 → 环境保真度 → 算法选择”的工程优先级；消除 Mid-training（中期训练）介入时机表述的歧义（`#1125`）。
  - 提前解释 `rollout` 概念，补入 GeneralPoints 新旧规则两条完整算式，拆分训练设计与输出格式分析，明确 RLVR 与 RLVP 路径惩罚对象；统一 **「在轨自蒸馏：用额外上下文构造教师」** 表述。
  - 区分精确复制任务（实验 8-19，37.5% → 78.9% / 80.1%）中模型生成能力与分词器（Tokenizer）的各自贡献。

### 第九章：Agent 的持续进化（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/) · [`book/chapter9.md`](../book/chapter9.md)）
- **四种更新载体与动态组合核验**（[将经验写成程序](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/#将经验写成程序) · [开放式任务中的证据与评价](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/#开放式任务中的证据与评价) · [持续进化的安全边界](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/#持续进化的安全边界)）：
  - 完善从运行轨迹评价到**知识、指令、程序、参数**四类载体更新的闭环论述，强调持续进化应遵循“假设—验证—回滚”的科学方法。
  - 核对 DeepSeek Harness（`dsh`）/ Cordis 的插件生命周期、时间/空间可组合性与可撤销效果（修正“所有组合均为静态”或“所有插件仅驻留内存”的绝对化表述）。
  - 补齐第 9 章思考题中缺失的历史发现树回放（History Replay）参考答案（`#1140`）。

### 第十章：多 Agent 协作（[🌐 在线阅读](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/) · [`book/chapter10.md`](../book/chapter10.md)）
- **协作收益与分布式机制校准**（[多 Agent 何时优于单 Agent](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#多-agent-何时优于单-agent) · [管理者模式：中心化协调](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#管理者模式中心化协调) · [跨组织协作：A2A 协议](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#跨组织协作a2a-协议) · [Moltbook：开放平台上的 Agent 交互](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#moltbook开放平台上的-agent-交互)）：
  - 将多 Agent 协作的判断标准从单一“信息增量”扩展为**信息增量、专业分工、并行搜索覆盖与通信/协调成本**的综合权衡。
  - 修正跨章节基准数字（`#1130`）：将搜索实验的真实加速比（1.872 倍）与示意时序图分开，移除不同工作量下直接外推“15 倍加速”的表述。
  - 校准 OpenAI Swarm（共享历史 vs 独立任务包）、Google A2A（组织内与跨组织通用、`Message/Part` 与流式推送）、MetaGPT 及 Moltbook 社区指标（区分注册规模与活跃指标，移除过度拟人化推断）。

### 后记、参考答案与全书插图（[`book/afterword.md`](../book/afterword.md)、[`book/reference-answers.md`](../book/reference-answers.md)、[`book/images/`](../book/images/)）
- **后记与书内变更附录**：统一首尾章节的“两套分解”与“Harness 五项功能”口径；区分 token 生成速度与端到端交互延迟；校准 Taalas 专用芯片公开指标（17,000 token/s）与开尔文勋爵历史典故；在后记末尾新增[《附录：3.0 版实质性变更与章节速查（面向 2.0 版读者）》](../book/afterword.md#附录30-版实质性变更与章节速查面向-20-版读者)。
- **参考答案**：全书思考题参考答案随正文同步重订，并新增第六章第 13、14 题参考答案（共 95 题）。
- **全书 115 幅矢量插图重绘**：由 `scripts/book_figures/` 统一生成黑白灰度出版级 SVG（正文字体 `Songti SC`、标题与图注 `Source Han Sans CN` 转曲、代码 `Menlo`），移除图顶/图底冗余解释框，保留完整技术字段、协议载荷与数值算例，提升 PDF / EPUB 与纸质印刷阅读体验。
