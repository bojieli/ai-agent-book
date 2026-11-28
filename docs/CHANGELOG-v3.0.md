# 3.0 版相对 2.0 版的变更清单

本文说明《深入理解 AI Agent：设计原理与工程实践》中文原版从 **2.0 版**到 **3.0 版**改了什么，供读过 2.0 版的读者决定重读哪些部分。小节标题取自 3.0 版正文，链接直达[在线阅读站](https://bojieli.github.io/ai-agent-book/astro/)的对应位置。

> 一句话结论：**3.0 版不是修订，是按同一套十章框架重写。** 保留下来的小节与原稿的句子相似度大多在两成到五成之间，技术事实与实验记录重新核对过，115 幅插图重绘为适合印刷的黑白灰度矢量图。因此更实际的做法是**整章重读**，下表列出各章新增或大幅扩写、值得优先看的小节。

## 规模变化

| 项目 | 2.0 版 | 3.0 版 |
| :--- | :---: | :---: |
| 章数 | 10 | 10（框架不变） |
| 配套实验 | 109 | 110 |
| 思考题 | 93 | 96 |
| 插图 | 2.0 版插图 | 115 幅重绘为黑白灰度矢量图，随正文更新 |

## 各章重读指引

阅读站的链接直达对应小节；仓库内查看正文可用各章源码（`book/chapterN.md`）。

### 第 1 章　AI Agent 入门

- **[观测空间与动作空间：模型与世界的接口](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#观测空间与动作空间模型与世界的接口)**：把“观测空间”与“当前决策视野”分开：环境给出哪些信息，与这一次推理实际送进模型的信息，是两件事。
- **[工具：Agent 的感官和手脚](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#工具agent-的感官和手脚)**：工具既改变外部状态（执行），也主动获取外部信息（感知），由此补上 2.0 版只讲执行的一半。
- **[上下文：Agent 的当前决策视野](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#上下文agent-的当前决策视野)**：上下文决定的是本次决策能看到多少，而不是笼统的“能力上限”。
- **[从提示工程到 Graph 工程：工程关注范围的扩展](https://bojieli.github.io/ai-agent-book/astro/book/chapter1/#从提示工程到-graph-工程工程关注范围的扩展)**：把提示词、上下文、Loop 与多组件工作流放进同一条演进线。
- 编号变化：实验 1-2 至 1-4 换题：Kimi K3 多轮搜索、Responses API 托管闭环、文生图工作流对照。

### 第 2 章　上下文工程

- **[上下文：让模型能力用于具体任务](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#上下文让模型能力用于具体任务)**：开篇改用“让模型能力用于具体任务”定调，替换原来的“决定能力上限”。
- **[从 API 消息到模型 Token：Chat Template](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#从-api-消息到模型-tokenchat-template)**：按 Qwen、DeepSeek、GLM、Claude 与 Codex 的实际模板重新核对。
- **[KV Cache 与 Prompt Cache：两个层级的缓存](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#kv-cache-与-prompt-cache两个层级的缓存)**：区分请求内 KV Cache 与跨请求 Prompt Cache，并补 Claude Preserved Thinking：改动历史前缀会让已保留的思考链失效。
- **[缓存作为架构约束](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#缓存作为架构约束)**：把缓存边界从优化技巧上升为架构约束。
- **[压缩与 KV Cache 的取舍](https://bojieli.github.io/ai-agent-book/astro/book/chapter2/#压缩与-kv-cache-的取舍)**：新增小节：压缩发生在两次调用之间，替换历史会改变前缀；应优先保持系统指令与工具定义稳定，并把历史压缩成批进行，避免每轮改写同一段前缀。
- 编号变化：实验 2-3、2-8 换题；思考题不变。

### 第 3 章　用户记忆和知识库

- **[稠密嵌入：用向量表示文本](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#稠密嵌入用向量表示文本)**：新增小节，把嵌入从“工具”讲成“表示”。
- **[稀疏表示：从关键词到相关性评分](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#稀疏表示从关键词到相关性评分)**：新增小节，BM25 一路讲到相关性评分。
- **[混合检索：合并两路结果再重排](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#混合检索合并两路结果再重排)**：新增小节，明确两路结果如何合并再重排。
- **[知识的组织与检索](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#知识的组织与检索)**：新增的章节级小节，串起分块、索引与检索。
- **[结构化索引：建立层次与关联](https://bojieli.github.io/ai-agent-book/astro/book/chapter3/#结构化索引建立层次与关联)**：新增知识使用方式建模：兼容约束可以同时生效，排他预案必须先看状态再择一加载。
- 编号变化：实验 3-2 至 3-12 全部换题，与新增小节一一对应。

### 第 4 章　工具

- **[工具描述：说明用途、参数与反馈](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#工具描述说明用途参数与反馈)**：新增小节：先设想一条最容易误用它的请求，再按“什么时候用、要提供什么输入、结果能回答什么”写说明，并把相邻工具的分工写清楚。
- **[工具生态：MCP 与 Skill Hub](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#工具生态mcp-与-skill-hub)**：对齐 MCP Streamable HTTP 规范，补充渐进式披露。
- **[层次化组织与按需加载](https://bojieli.github.io/ai-agent-book/astro/book/chapter4/#层次化组织与按需加载)**：把“工具太多怎么办”从原则落实到组织方式。
- 编号变化：实验与思考题编号不变。

### 第 5 章　Coding Agent 与通用 Agent

- **[Harness 工程在 Coding Agent 中的实践](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#harness-工程在-coding-agent-中的实践)**：重构工具粒度取舍：哪种操作值得一个专门工具，哪种交给通用执行器。
- **[故障与错误恢复](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#故障与错误恢复)**：重写恢复的判断顺序：先问上一步留下了什么证据，再按 API 层、工具层、环境层分别决定重试、修正调用、从断点继续还是终止。
- **[Coding Agent 的安全](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#coding-agent-的安全)**：重写沙盒与权限边界，并对照生产级权限差距。
- **[代码作为思考工具](https://bojieli.github.io/ai-agent-book/astro/book/chapter5/#代码作为思考工具)**：改为“先把题意转成关系与约束，再交给解释器或求解器”，并用实验 5-3、5-4 的实测结果说明逐词生成错在哪里。
- 编号变化：实验 5-3 至 5-5 换题。

### 第 6 章　交互：观察与动作空间的扩展

- **[接入层：多种来源，一种事件](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#接入层多种来源一种事件)**：新增小节：邮件、日历、Slack、GitHub、定时任务如何归一化为同一种事件，含会话映射、乱序与幂等。
- **[从邮件事件建立基本循环](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#从邮件事件建立基本循环)**：新增小节：用邮件事件把异步循环从头搭一遍。
- **[可靠处理异步任务](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#可靠处理异步任务)**：新增小节：可靠的异步交互要同时检查结果归属（延迟结果如何映射回任务）、恢复与取消（用户改要求后哪些后台任务继续）、多条要求（预算、人数、地区、截止时间逐项核对）。
- **[认知时序：实时交互与深度思考](https://bojieli.github.io/ai-agent-book/astro/book/chapter6/#认知时序实时交互与深度思考)**：新增实验 6-7：双模型语音架构下，工具由前台还是后台调用，三种方案的端到端延迟差在哪里。
- 编号变化：实验 14→15 个，原 6-7 至 6-14 顺延为 6-8 至 6-15；思考题 12→14。

### 第 7 章　Agent 的评估

- **[从一条任务理解评估：τ²-bench 的 telecom 领域](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#从一条任务理解评估τ-bench-的-telecom-领域)**：开篇改为从一条真实任务读懂整套评估设计。
- **[沿着运行轨迹检查结果](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#沿着运行轨迹检查结果)**：新增小节：为什么只看最终答复不够，要看轨迹。
- **[LLM-as-a-Judge：把质量要求转成逐项评分](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#llm-as-a-judge把质量要求转成逐项评分)**：扩写为完整方法：评判模型要同时看到任务、评分标准与参考材料，才能指出漏答了哪一项；上线前需校准长度偏差，并用交换前后顺序的办法检查位置偏好。
- **[A/B 测试：区分改动机制与业务目标](https://bojieli.github.io/ai-agent-book/astro/book/chapter7/#ab-测试区分改动机制与业务目标)**：新增小节：先定随机分组单位，再区分机制指标（如计划长度）与目标指标（如会话级成本），并设置护栏指标，用整条任务结果判断价值。
- 编号变化：实验 7-2 换题；思考题 9→10。

### 第 8 章　模型后训练

- **[预训练：从下一个 token 学习文本规律](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#预训练从下一个-token-学习文本规律)**：新增小节，把三阶段训练的分工讲清楚。
- **[根据模型起点安排 SFT 与 RL](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#根据模型起点安排-sft-与-rl)**：新增小节：先看模型起点，再决定先 SFT 还是先 RL。
- **[奖励在什么时候给：结果与过程](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#奖励在什么时候给结果与过程)**：新增小节：结果奖励与过程奖励的取舍。
- **[路径约束与 RLVP](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#路径约束与-rlvp)**：新增小节：把结果奖励与可验证的路径惩罚结合，原则是奖励结果、惩罚路径。
- **[在轨自蒸馏：用额外上下文构造教师](https://bojieli.github.io/ai-agent-book/astro/book/chapter8/#在轨自蒸馏用额外上下文构造教师)**：改写自 2.0 的 On-Policy 自蒸馏。
- 编号变化：实验 8-9、8-10 换题；思考题不变。

### 第 9 章　Agent 的持续进化

- **[从更新产物到优化更新方法](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/#从更新产物到优化更新方法)**：新增小节：先判断错误出在知识、指令、程序还是参数哪一层，再把局部更新作为默认选择，便于检查影响和回滚。
- **[开放式任务中的证据与评价](https://bojieli.github.io/ai-agent-book/astro/book/chapter9/#开放式任务中的证据与评价)**：新增小节：研究型任务里，流程跑完不等于有结论；实现漂移、过早解释结果、研究判断不足是三类具体失败。
- 编号变化：实验与思考题编号不变。

### 第 10 章　多 Agent 协作

全章按设计问题重新组织，用合译一本书时一次跨章的术语变更贯穿始终。

- **[上下文经济学](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#上下文经济学)**：新增章首小节。保留背景要付出处理和维护成本，重新取得背景要检索和理解，交给另一位成员还要同步变化。由此引出两项选择：成员是否共享上下文，由谁决定下一步。
- **[多 Agent 何时优于单 Agent](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#多-agent-何时优于单-agent)**：先问新增的 Agent 带来什么信息增量（新证据、另一条搜索路径、不同的专业判断），再看并行与上下文隔离能带来多少收益。
- **[从任务依赖到角色与组织](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#从任务依赖到角色与组织)**：新增小节，讲哪些工作必须一起做、决策权怎样划分，以及按次外包、临时成员和常驻成员各适合什么情形。
- **[交接时传什么，以哪份记录为准](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#交接时传什么以哪份记录为准)**：新增小节，比较点对点、广播和“公告板加事件通知”三种交接方式。
- **[对等协作模式：围绕同一产物反复修订](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#对等协作模式围绕同一产物反复修订)** 与 **[管理者模式：集中分派与跨任务决策](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#管理者模式集中分派与跨任务决策)**：补充 Multica、LobeHub、dsh-superagent，以及黎曼猜想形式化证明的审核和 Navier–Stokes 反例搜索等案例。
- **[验收、取消与恢复](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#验收取消与恢复)**：新增小节，把 Loop 工程、并行分支的收尾、验证预算和失败模式放到同一个问题下。
- **[跨组织协作：A2A 协议](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#跨组织协作a2a-协议)**：按协议现状重写，移到章末与 Agent 社会一起讨论。
- **[Moltbook：开放平台上的 Agent 交互](https://bojieli.github.io/ai-agent-book/astro/book/chapter10/#moltbook开放平台上的-agent-交互)**：新增案例：2026 年 1 月上线，早期注册规模约 150 万；开放平台把用户设定、平台提示与模型生成混在同一条信息流里，传播行为难以归因。
- 编号变化：实验与思考题编号不变。

## 术语口径的变化

3.0 版统一了全书的概念边界，读数时可按新口径理解：

| 2.0 版 | 3.0 版 | 为什么要改 |
| :--- | :--- | :--- |
| 引言 | 前言 | 补写“本书的使命”，交代“实践 → 方法 → 原则”的主线。 |
| 观察空间 | 观测空间 | 统一控制论与强化学习的标准译法，与“当前决策视野”区分开。 |
| 工具：Agent 的手脚 | 工具：Agent 的感官和手脚 | 工具不仅执行动作，也主动获取信息。 |
| 从提示工程到 Loop 工程 | 从提示工程到 Graph 工程 | 覆盖提示词、上下文、Loop、工作流与多 Agent 协作图。 |
| Ticket（混用） | 工单 | 第 6 章异步事件与第 10 章多 Agent 协作统一译名与状态机口径。 |

## 书内怎么找

中文版 PDF、EPUB 与[在线阅读站](https://bojieli.github.io/ai-agent-book/astro/)的后记末尾附有本清单的精简版（[附录：3.0 版主要更新](../book/afterword.md)），PDF 与网页读者都可以从那里按章跳转。

## 非中文版本

各非中文社区翻译版此前对应 2.0 版结构，正在按 3.0 版正文重译，进度见各语种的下载入口说明。

