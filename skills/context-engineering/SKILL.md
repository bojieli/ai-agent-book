---
name: context-engineering
description: 设计 Agent 系统提示词、上下文结构或按需加载的 Skill 时使用——覆盖 API 消息角色与「静态前缀 + 轨迹」结构、系统提示词写法（结构化、SOP、业务规则细化、few-shot）、Agent Skills 渐进式披露与 SKILL.md 编写、提示注入的上下文层防御，以及注意力位置偏好等布局原则。
---

# 上下文工程总纲

上下文是 Agent 在每个决策点实际「看到」的全部信息：系统提示词、工具定义、用户消息、模型回复、工具执行结果。上下文工程就是系统性设计、组织、供给这些信息——模型智力只是基础，**上下文质量才是 Agent 能力的真正关键**。一个中等能力的模型配上精心组织的上下文，往往胜过一个顶级模型在信息匮乏下的盲目摸索。

## 何时使用

- 设计或重构 Agent 的系统提示词、工具定义、消息列表结构
- 编写 / 审查一份 `SKILL.md`（元数据、路由描述、正文分层）
- 排查「Agent 行为不稳定、违反业务规则、重复犯错、忘记约束」
- 决定哪些知识该进系统提示词、哪些该做成按需加载的 Skill
- 评估外部内容（网页、文档、邮件）进入上下文后的安全风险

## 核心原则

- **API 无状态，上下文由框架每轮重建。** 模型不会「记住」上一轮，Agent 框架必须每次都把完整消息历史送回去。
- **上下文 = 四种消息角色 + `tools` 字段。** `system`（开发者规则，通常只有一条且在最前）、`user`（终端用户输入）、`assistant`（模型回复含 `tool_calls`）、`tool`（框架执行结果，靠 `tool_call_id` 与调用关联）；工具定义走请求顶层 `tools` 字段，不是消息角色。
- **静态前缀 + 动态轨迹。** system prompt 与 tool definitions 全程不变，对话历史（trajectory）随交互持续增长。所有后续技术都在优化这个列表的内容与结构。
- **模型决策、框架执行。** 模型只发出工具调用请求，真正执行工具的是 Agent 框架；循环「请求 → tool_calls → 执行 → 送回结果 → 再请求」就是 ReAct 循环的 API 实现。
- **最低信息需求三件套**：代码信息（结构、职责、规范）、流程规范（分支、提交、评审、CI/CD）、环境信息（配置、数据库、密钥管理）。缺哪一类，Agent 就在哪一类上出错。
- **新员工检验法**：如果一个聪明的新员工读完你的系统提示词还不知道该怎么做，Agent 也一样不知道。
- **上下文学习是检索而非推理**：模型擅长从已有内容中查找，不擅长在前向传播中归纳统计。位置偏好（Lost in the Middle）意味着开头和结尾注意力最高，中部易被忽视——关键信息放两端。
- **与模型厂商的训练方法保持一致**：选择 Agent 交互模式时优先采用厂商专门训练过的模式（Skills、tool_search 等），同生态内表现最佳。

## 实践模式

### 1. 系统提示词四维度

- **语气与风格**：用明确指令而非请求，如 `You MUST answer concisely with fewer than 4 lines`；无法完成任务时 `keep your response to 1-2 sentences` 且不要解释为什么不能做。大写（`NEVER do X`）比 `Please avoid doing X` 更能引起注意，但过度使用会稀释效果，只留给真正关键的约束。
- **结构化**：Markdown 标题（`#`、`##`）提供人可读的层次，XML 标签提供机器可解析的精确语义（`<file_operation>`、`<network_request>`），标签名本身携带语义。双层配合：Markdown 管组织逻辑，XML 管语义边界。
- **流程驱动而非规则堆砌**：写成带分支的 SOP（Step 1 Validation → Step 2 Classification → ... → Step 5 Verification），让模型任何时刻都知道自己在哪个阶段、异常时按阶段处理，而不是遍历上百条零散规则找匹配项。
- **业务规则细化到可执行**：把模糊规则（「根据任务情况选择合适的计费类型」）改写成布尔判断，例如 `NEVER use percentage_based_one_time for refunds and service cancellations. Use fixed_fee instead.`；成功率阈值直接映射到行为（>60% 可退款、<30% 拒绝任务）；计费粒度写死（每分钟 $0.05，汇总四舍五入到整数美元），并明确「节省」只基于现有账单计算。**提示词由产品经理基于线上数据设计，工程师负责准确编码，不擅自决定业务逻辑。**

### 2. few-shot 示例的两个决策点

- **位置**：放系统提示词 = 成为静态前缀对所有请求生效；或伪造一组 user/assistant 消息放在首轮对话中，适合按会话类型选用不同示例集。
- **稳定性**：无论放哪，示例都处于上下文靠前区域，一旦确定必须字节级稳定——按请求动态检索「最相关」的示例等于每轮改写前缀，缓存会持续失效。为每类任务准备固定示例集。
- **数量**：两三个精心挑选、覆盖边界情况的示例，胜过十个大同小异的示例——后者既占上下文，又稀释对规则本身的注意力。

### 3. Agent Skills：渐进式披露三层

- **第一层 元数据**：`SKILL.md` 顶部 YAML frontmatter 的 `name` + `description`，在正文加载前对 Agent 可见，用于路由判断。`description` 要写得像路由条件而非功能介绍：明确「何时使用」「何时不使用」的边界，给几条典型反例。写 `help with backend` 这种宽泛描述等于任何后端工作都能触发，路由必然失准。
- **第二层 核心流程**：模型判断需要该 Skill 时才加载完整 `SKILL.md`（斜杠命令由客户端本地拦截展开；模型自主触发则多一次 ReAct 往返，正文作为 user message 追加）。
- **第三层 细则**：通过文件引用深入到子文档（如 `html2pptx.md`、`reference.md`），Agent 按需选择性深入。
- **上下文成本**：所有 Harness 都遵循「少量目录常驻、完整正文按需加载」。Skill 正文在调用位置追加到轨迹末尾，不改写已建立的前缀，因此对 KV Cache 友好。
- **SKILL.md 四部分**（宝玉《图解 Skill》）：角色与读者；核心原则只留 3–5 条并配正反例；禁止清单记录高频错误、越权动作并写清合法例外；参考资料放术语表、模板、范文。规则写成「作用域 + 动作 + 例外 + 验证方式」，不要堆成越来越长的禁用词表。
- Skill 还可捆绑可执行代码工具和模板文件，自包含、可独立版本控制。

### 4. 上下文布局决策骨架

```python
stable_prefix = system_message            # 定了就不改
stable_tools  = core_tool_schemas         # 固定顺序
trajectory    = load_message_history(session)
status_message = make_status_message(derive_current_state(trajectory))

if estimated_tokens(stable_prefix, trajectory, status_message) > budget:
    trajectory = compress_old_evidence(
        trajectory, preserve=[decisions, constraints, failures, citations]
    )

request.messages = [stable_prefix] + trajectory + [status_message]
request.tools = stable_tools
```

### 5. 提示注入的上下文层防御

第一道防线是帮模型分清「指令」与「数据」：

- **来源标记**：外部内容注入前用 `<external_content source="webpage">...</external_content>` 包裹并标注来源。
- **结构化角色**：严格用 system/user/assistant/tool 角色体系传递信息，绝不把工具结果混入 user 消息——那等于亲手抹掉模型辨别来源的依据。
- **输入清洗**：过滤「忽略之前的指令」等常见注入短语，只能作辅助，易被措辞变体绕过。
- **把 Skill 和状态栏也当注入面**：Skill 本质是「把外部内容当作指令加载」的制度化形式，安装来源不明的 Skill 前必须审查内容；状态栏信息被模型高度信任，若摘要来自可被外部污染的数据源，信任会被反向利用。

## 常见陷阱

- **把时间戳、用户余额等动态信息写进 system prompt**——每轮改写前缀，缓存全失效（详见 `kv-cache-design`）。
- **规则堆砌而无组织结构**：实验 2-4 显示，保留全部规则内容但打乱组织、去掉标题层次，任务成功率下降超过 30%，Agent 经常违反关键业务规则。
- **清空工具描述**：保留函数签名但移除描述性文本，工具调用错误率增加 45%。
- **盲目追求语气风格**：风格显著改变表达方式，但对任务完成率影响相对有限，不必在此过度投入。
- **示例逐请求动态检索**：缓存持续失效，且不同示例集导致行为不可复现。
- **所有场景塞进一个系统提示词**：既浪费 token（大部分与当前任务无关），又稀释注意力——应拆成按需加载的 Skill。
- **让模型在业务规则上自由裁量**：模型优势在于遵循复杂指令和从长上下文提取信息，模糊规则会让同一任务在不同时间得到不同分类。
- **把上下文层防御当作万无一失**：它只能降低攻击成功率，权限控制、沙盒隔离、高风险操作独立审查是另一层。

## 配套代码

- `chapter1/context/` — 多 provider 上下文感知 Agent，消融实验 1-1 对比 full / no history / no reasoning / no tool calls / no tool results 五种上下文模式。
- `chapter2/prompt-engineering/` — 实验 2-4：基于 Tau-Bench 的提示工程消融框架，量化语气风格、指令组织、工具描述三个维度对任务完成率的影响。

## 深度阅读

- `book/chapter2.md`「上下文：决定 Agent 能力上限的关键」
- `book/chapter2.md`「Agent 如何调用大模型：理解 API 的上下文结构」
- `book/chapter2.md`「提示工程：优化系统提示词」
- `book/chapter2.md`「动态提示词与 Agent Skills」
