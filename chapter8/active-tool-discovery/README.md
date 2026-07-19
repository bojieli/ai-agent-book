# 实验 8-4：主动工具发现（Active Tool Discovery）

> 《深入理解 AI Agent》配套代码 · ★★★
>
> 在 **126 个跨领域工具**的工具库上，一次运行对比三种"工具发现"策略——**全量注入**、
> **检索预筛选**（一次性语义预选 top-n）、**主动发现**（执行中按需 `discover_tools`）——
> 并输出统一的对比表（准确率 / 注入 token / 延迟）。量化全量注入的 token 浪费，展示主动发现
> 如何用**嵌入向量相似度**把上百个工具收敛成几条精准候选，同时揭示"一次性预筛选"在多步跨领域
> 任务上的内在局限。**无 API key 也能跑**：`python demo.py --offline` 用本地嵌入 + mock 模型自检机制。

## 目的

当一个 Agent 拥有上百个工具时，常见做法是把全部工具的 JSON schema 一次性塞进 system prompt。
这会带来两个问题：

1. **token 浪费**：126 个工具的完整 schema 约 **1.16 万 token**，每一步推理都要重复计费。
2. **指令遵循退化**：措辞稍泛的任务下，模型会"广撒网"地把通用兜底工具（`web_search` /
   `google_search` / `universal_search`）和专用工具一起调用，甚至用通用搜索替代专用工具
   —— 即书中所说的"查股价却选了通用 web_search"。

**主动发现**只在 system 里保留少量基础工具 + 一个 `discover_tools(need)` 元工具。模型遇到能力缺口时，
用自然语言描述需求，系统用嵌入相似度从工具库检索 3-5 个最相关的专用工具，把它们的 schema 作为
**user message** 追加进对话（保护 system 前缀的 KV Cache），并更新状态栏可用工具列表。

## 机制

```
tools_library.py   126 个跨领域工具（finance/web/arxiv/github/geo/weather/media/... 共 17 个领域）
                   每个工具有真实 name/description/parameters；执行为轻量 mock（重点是"选对工具"）
                   其中故意混入 8 个"通用/近义"工具（web_search 等），它们的描述夸大自己无所不能
                   select_tools(size)：按 --tool-set-size 截取子集，演示"工具集越大全量注入越吃亏"
discovery.py       可插拔嵌入后端 + 工具向量索引；OpenAIEmbedder 用 text-embedding-3-small 生成向量
                   并缓存到 .cache/；search(need) = 把 need 向量化后与工具向量做余弦相似度返回 top-k
agent.py           三种策略的 ReAct 循环（文本协议：模型每步输出一个 JSON 工具调用）
                   - run_full_injection：126 个工具 schema 全部写进 system prompt
                   - run_retrieval_prefilter：按初始查询一次性检索 top-n 工具注入（书中"检索式预筛选"）
                   - run_active_discovery：基础工具 + discover_tools，执行中按需检索加载
offline_backend.py 离线后端：LocalEmbedder（本地哈希词袋嵌入）+ MockChatClient（脚本化 mock 模型），
                   让 --offline 无需任何 API key 即可跑通全流程（token/延迟真实，准确率仅反映启发式路由）
demo.py            对同一组任务分别跑所选策略，打印 token / 延迟 / 调用轨迹 / 是否精确选对，并汇总对比表
```

**为什么用"文本注入 + 文本解析"而不是 OpenAI 原生 function calling？**
原生 function-calling 接口对工具选择做了很强的约束优化，即使上百个工具也极少选错，无法体现书中
所述的"超长上下文指令遵循退化"。把 schema 当作纯文本塞进 prompt、让模型自己以 JSON 输出工具调用，
才是控制组的真实机制，也才能观察到退化。这也正是书中"把 schema 注入 system prompt（几万 token）"的写法。

**为什么嵌入检索能避免错选？** 通用工具 `web_search` 的描述"什么都能做"，语义被稀释；而专用工具
（如 `search_news`）描述聚焦。对一个聚焦的 `need`（"获取特斯拉最近的新闻"），聚焦的专用工具余弦相似度
更高、排在前面，通用工具往往进不了 top-k，于是根本不会被加载 —— 检索层天然起到了"精度过滤"作用。

**检索预筛选为什么不够？** 检索预筛选（`run_retrieval_prefilter`）只按**初始查询**做一次语义匹配、
一次性注入 top-n 工具。对"查股价 + 搜新闻"这类多步跨领域任务，初始查询的向量往往偏向第一个领域，
第二个子任务需要的专用工具可能挤不进 top-n，模型执行到一半才发现"想调用的工具根本没在清单里"——
这正是书中指出的一次性匹配的内在局限。主动发现把"发现"延后到执行中、按每个真实浮现的 `need` 分别检索，
从而补齐这一缺口（离线自检里可直接观察到：检索预筛选在半数多步任务上漏掉了第二个工具，见下表）。

## 运行

```bash
pip install -r requirements.txt

# 方式 A：离线机制自检（无需任何 key；token/延迟真实，准确率仅反映启发式路由）
python demo.py --offline

# 方式 B：真实模型（体现小模型"指令遵循退化"需要真实 LLM）
cp env.example .env    # 填入 OPENAI_API_KEY（chat 与 embeddings 都用 OpenAI）
# 兜底：若无 OPENAI_API_KEY 但设置了 OPENROUTER_API_KEY，chat 会自动改走 OpenRouter
#（模型映射到 openai/gpt-5.6-luna 等），工具检索退用本地哈希嵌入（OpenRouter 无 embeddings 接口）。
python demo.py                                   # 全部 8 任务 × 三种策略
python demo.py --strategies full,discovery       # 只跑其中两种策略对比
python demo.py --tasks finance+news,crypto+news  # 只跑指定任务（逗号分隔）
python demo.py --tasks 'opinion(诱导)'            # 含括号的任务 id 记得加引号
python demo.py --tool-set-size 20                # 缩小工具集，看全量注入的劣势如何随规模放大
python demo.py --query '查英伟达股价再搜点相关新闻' --offline   # 临时单条自然语言任务
python demo.py --offline --output results/offline.json         # 导出结构化结果
```

默认模型 `gpt-5.6-luna`，可用 `--model` 或 env 覆盖：`python demo.py --model gpt-5.6-luna`。
首次运行会为工具生成嵌入向量并缓存到 `.cache/`，之后复用。`python demo.py --help` 查看全部参数
（`--query / --tasks / --strategies / --tool-set-size / --top-k / --prefilter-n / --model / --embed-model / --max-steps / --offline / --output`）。

## 如何适配 / 扩展

- **换模型**：`MODEL=gpt-4.1-mini python demo.py`（chat 模型）；`EMBED_MODEL=text-embedding-3-large` 换嵌入模型
  （换嵌入模型会因签名变化自动重建 `.cache/` 索引）。
- **换供应商 / 网关**：chat 与 embeddings 都走 OpenAI SDK，`OpenAI()` 会自动读取环境变量 `OPENAI_BASE_URL`，
  因此指向任意 **OpenAI 兼容**的网关/代理只需 `OPENAI_BASE_URL=https://your-gateway/v1`（该端点需同时提供 chat 与 embeddings）。
- **换任务 / 输入**：编辑 `tools_library.py` 里的 `TASKS`（每条含 `prompt` 与判分用的能力槽位），或用
  `--tasks` 只跑其中几条，或用 `--query` 传一句临时需求；想扩充工具库同样在 `tools_library.py` 的 `ALL_TOOLS` 中增删。
- **离线自检**：`--offline` 用 `offline_backend.py` 的本地哈希嵌入 + 脚本化 mock 模型，无需任何 key，
  适合 CI、无网环境或快速验证流水线；它复现的是 token/延迟结构与"检索预筛选一次性漏工具"的机制，
  不复现真实模型在长上下文工具墙下的选择行为（后者见下方 gpt-5.6-luna 真实结果）。

## 离线机制自检（本地嵌入 + mock 模型，`python demo.py --offline`）

下表为一次真实的 `--offline` 运行（8 任务 × 三策略）。**token/延迟是 tiktoken/wall-clock 真实测量**；
**准确率仅反映脚本化启发式路由，不代表真实模型能力**——mock 模型是"强路由器"，不会退化，所以全量注入也拿满分。

| 策略 | 精确选对 | 任务完成 | 平均注入 token | 总注入 token | 平均延迟(s) |
|---|---|---|---|---|---|
| 全量注入 | 8/8 | 8/8 | 11630 | 93040 | 0.008 |
| 检索预筛选 | 4/8 | 4/8 | 1030 | 8236 | 0.006 |
| 主动发现 | 8/8 | 8/8 | 974 | 7796 | 0.010 |

离线自检要传达的**两个真实、可复现的结构性结论**：

1. **token 随工具集规模放大而分化**：全量注入固定 11,630 token/任务；检索预筛选与主动发现按需只注入
   约 1,000 token（**~11.9× 精简**）。用 `--tool-set-size 20` 缩小工具集，差距收敛到 ~1.8×——印证"工具越多、
   全量注入越吃亏"。
2. **检索预筛选在多步跨领域任务上结构性漏工具**：一次性 top-10 检索在 8 个任务里有 4 个漏掉了第二个子任务
   所需的专用工具（如 `academic(诱导)` 的 top-10 里根本没有 `arxiv_search`），模型执行到一半调不到工具 →
   子任务失败；主动发现按每个真实浮现的 `need` 分别检索，8/8 补齐。

## 结论（基于一次真实运行，gpt-5.6-luna，2026-07）

> 说明：下表是一次真实 LLM 运行（`python demo.py --model gpt-5.6-luna`，8 任务 × 三策略，OpenAI 直连
> chat + `text-embedding-3-small` 检索）。gpt-5.6-luna 是推理型模型，仅支持默认 `temperature=1`
> （不支持 `temperature=0`，代码遇到该报错会自动回退到默认温度），故本次为**单次、非确定性**运行；
> token/延迟为真实测量，逐任务的选择结果可能随采样波动。判定：✅=精确选对（覆盖全部能力槽位且未错选
> 通用兜底工具）；⚠️=完成但顺手错选了通用工具；❌=出错（漏用专用工具或中途放弃、0 次工具调用）。

| 任务 | 全量注入 | 检索预筛选 | 主动发现 | 全量 token | 发现 token |
|---|---|---|---|---|---|
| finance+news | ✅ | ❌ | ✅ | 11630 | 883 |
| arxiv+download | ✅ | ❌ | ✅ | 11630 | 927 |
| github+viz | ❌ | ❌ | ❌ | 11630 | 295 |
| weather+calendar | ❌ | ✅ | ✅ | 11630 | 1055 |
| forex+weather | ✅ | ✅ | ❌ | 11630 | 295 |
| crypto+news | ❌ | ⚠️ | ❌ | 11630 | 295 |
| opinion(诱导) | ⚠️ | ❌ | ✅ | 11630 | 688 |
| academic(诱导) | ⚠️ | ⚠️ | ❌ | 11630 | 295 |
| **精确选对** | **3/8** | **2/8** | **4/8** | | |
| **任务完成** | **5/8** | **4/8** | **4/8** | | |
| **总注入 token** | | | | **93040** | **4733** |

（检索预筛选平均 971 token/任务、总 7768；三策略平均延迟约 11.5 / 9.6 / 10.7 s，均为本次真实测量。）

1. **token 节省依旧稳健（且更悬殊）**：全量注入每任务固定注入 **11,630 token**；主动发现按需加载后仅
   **295~1,055 token**，合计 93,040 → 4,733（**~19.7×**）。需诚实说明：本次比值偏大，部分是因为
   gpt-5.6-luna 在若干任务上直接放弃、根本没触发 `discover_tools`（此时只注入 3 个基础工具 = 295 token）。
   即便如此，"全量注入固定重复计费上万 token、按需发现只注入千级 token"这一结构性收益不受影响。

2. **书中核心现象在两个"诱导任务"上如实复现**：措辞偏泛时，全量注入会顺手抓通用兜底工具——
   - `opinion(诱导)`（"特斯拉最近的新闻舆论风向"）：全量注入调用了 `search_news, search_news,
     web_search, search_tweets`，把通用的 **`web_search`** 也用上（⚠️ 错选）；主动发现检索到
     `search_news / get_news_by_source / ...`（**没有** `web_search`），只调用专用新闻工具，**干净选对（✅）**。
   - `academic(诱导)`（"量子计算最新科研进展"）：全量注入一口气调用了 8 个工具，其中
     **`google_search / universal_search / ask_knowledge_base`** 三个都是通用兜底（⚠️）；检索预筛选也错选了
     `google_search / universal_search`。这正是书中"上百工具的工具墙 + 措辞含糊 → 广撒网抓通用工具"的写照。

3. **本次运行暴露的另一类真实行为（与早期 gpt-4o-mini 运行不同，须如实记录）**：gpt-5.6-luna 是偏保守的
   推理型模型，在多个任务上**没有调用（mock）工具就提前 `finish`**，理由多为"无法访问实时数据/工具"
   （如 `github+viz`、`weather+calendar` 的全量注入，以及 `forex+weather`、`crypto+news`、`academic` 的
   主动发现，均出现 0 次工具调用）。这压低了三种策略的绝对准确率，也意味着本次**得不出**"清晰任务下模型
   面对工具墙一律选对"的结论——恰恰相反，放弃/漏步成了主要失分点，且这类失分在全量注入与主动发现上都存在。

4. **如实说明的边界**：
   - 本实验用"schema 当纯文本注入 + 模型自行输出 JSON 工具调用"的控制组机制来观察长上下文选择行为；
     mock 工具返回的是占位数据，保守的推理模型有时会识破并拒绝作答，这是本次准确率偏低的一大来源。
   - 因 gpt-5.6-luna 仅支持默认 `temperature=1`，逐任务结果具随机性；重复运行时哪些任务"放弃"、哪些
     "错选通用工具"会有波动，但两条结构性结论（token 节省、诱导任务下全量注入误用通用工具）方向稳定。
   - 想要更干净、可复现的机制自检（token/延迟结构 + 检索预筛选一次性漏工具），见上方 `--offline` 表。

> 一句话：**在 gpt-5.6-luna 上，主动工具发现最稳的收益仍是 token（本次 ~19.7×）；在措辞含糊、通用工具
> 易被误用的"诱导任务"上，嵌入检索确实把 `web_search / google_search / universal_search` 等夸大其词的
> 通用工具挡在候选之外。但这一版真实运行也提醒：强推理模型保守的"放弃"行为会同时拉低各策略的绝对准确率，
> 单次结果需按上表如实解读。**

## 模型 ↔ 脚手架此消彼长（弱模型 gpt-4o-mini vs 强模型 gpt-5.6-luna，均为真实运行）

> 这一节回答一个直接的问题：**模型变强，这套"主动工具发现"脚手架是不是就没用了？**
> 我们把上面的 gpt-5.6-luna（强）结果，与同样 8 任务 × 三策略、OpenAI 直连 chat +
> `text-embedding-3-small` 检索的 **gpt-4o-mini（弱）** 真实运行放在一起对照
> （`python demo.py --model gpt-4o-mini`，2026-07，判定口径同上）。结论是：脚手架有两种价值，
> 一种随模型变强而**淡出**，另一种与模型强弱**无关、始终存在**。

**弱模型 gpt-4o-mini 真实汇总：**

| 策略 | 精确选对 | 任务完成 | 总注入 token | 平均延迟(s) |
|---|---|---|---|---|
| 全量注入 | 5/8 | **8/8** | 93040 | 8.38 |
| 检索预筛选 | 7/8 | 7/8 | 7768 | 4.90 |
| 主动发现 | **8/8** | **8/8** | 7266 | 7.65 |

（token 93040 → 7266，**~12.8×** 精简。）

### 价值一：避免"错选通用工具"—— 随模型变强而**淡出**（fading）

- **弱模型 gpt-4o-mini：脚手架价值巨大且干净。** 全量注入下，gpt-4o-mini 从不放弃（任务完成 8/8），
  但在 3 个任务上"广撒网"抓了通用兜底工具——`crypto+news` 用了 `web_search`，两个诱导任务
  `opinion` / `academic` 各自把 `web_search / google_search / universal_search` 一并调用——
  于是全量注入只有 **5/8 精确**。主动发现让嵌入检索把这些夸大其词的通用工具**挡在候选之外**，
  gpt-4o-mini 根本无从误用：**8/8 精确、0 次通用工具误用、且任务完成不降（仍 8/8）**。
  即"全量 5/8 → 发现 8/8 精确，+3 个任务，零完成损失"——这正是书中"上百工具的工具墙 +
  措辞含糊 → 广撒网抓通用工具"的弱模型病症，脚手架把它一次性治好。
- **强模型 gpt-5.6-luna：同一价值明显缩水。** 它在全量注入下的"通用工具误用"只剩 2 个任务
  （`opinion` / `academic`），比 gpt-4o-mini 的 3 个更少；主动发现把这两处也擦干净，但精确率只从
  **3/8 提到 4/8（+1）**，而且**任务完成反而从 5/8 降到 4/8**。原因在于强推理模型的主要失分点
  **不是"选错工具"，而是"直接放弃"**：多个任务它 0 次工具调用就 `finish`（理由多为"无法访问实时数据"），
  这类失分检索层无法修复，工具可见得更少时甚至略微加剧。**换言之，脚手架专治的"错选通用工具"这一弱点，
  在强模型上本就稀薄，收益随之淡出。**

### 价值二：节省注入 token —— 与模型强弱**无关、始终存在**（persisting）

全量注入无论模型强弱都固定为 **11,630 token/任务**（把 126 个工具 schema 全塞进 system），
这是纯结构性开销。按需发现只注入几百到一千余 token：

- 弱模型 gpt-4o-mini：93,040 → 7,266，**~12.8×**；
- 强模型 gpt-5.6-luna：93,040 → 4,733，**~19.7×**（比值更大，部分是因为它常放弃、根本没触发 `discover_tools`，
  只注入 3 个基础工具）。

两个模型上 token 节省都稳稳成立，且随工具集变大而放大——**这份收益不因模型变强而消失**，
是脚手架在"强模型时代"仍然值得保留的硬理由。

### 一句话小结

> **模型越强，脚手架"帮它别选错工具"的价值越淡（gpt-4o-mini 全量 5/8→发现 8/8 精确、零完成损失；
> gpt-5.6-luna 仅 3/8→4/8 且完成还降了，因为它的失分是"放弃"而非"错选"）；但"省 token"的价值
> 与模型强弱无关、始终存在（弱模型 ~12.8×、强模型 ~19.7×，全量注入恒为 11,630 token/任务）。
> 所以在强模型上，主动工具发现的主要理由从"纠正指令遵循退化"转向"控制上下文成本"。**

## 文件

- `tools_library.py` — 126 个工具定义 + `select_tools` 子集截取 + mock 执行 + 8 个评测任务与判分标准
- `discovery.py` — 可插拔嵌入后端（`OpenAIEmbedder`）+ 工具向量索引与相似度检索（`discover_tools`/预筛选的后端）
- `agent.py` — 三种策略（全量注入 / 检索预筛选 / 主动发现）的 ReAct 循环与 token 统计
- `offline_backend.py` — 离线后端：`LocalEmbedder` + `MockChatClient`，支撑 `--offline` 无 key 自检
- `demo.py` — 一键多策略对比演示（含 CLI：`--query/--tasks/--strategies/--tool-set-size/--offline/--output` 等）
- `requirements.txt` / `env.example`
