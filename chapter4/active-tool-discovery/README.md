# Active Tool Discovery / 主动工具发现

第一次做实验，可以先运行 `python demo.py --offline`：用 126 个教学工具比较全量加载、预筛选和主动发现，沿着调用轨迹观察模型每一步能看到哪些说明。要核对[正文实验 4-1 的结果](validation/experiment_4_1/rerun_20260825/summary.json)，请看下文的正式运行：`run_exact_experiment.py` 连接真实 MCP 服务，8 月 25 日的记录用 127 个工具比较全量加载与主动发现。

[English](#english)

[模型怎样发现缺少的工具](#learning-0) · [选教学目录或正式运行记录](#learning-1) · [对照工具定义的加载顺序](#learning-2) · [检查必需工具是否入选](#learning-3) · [实现与正式运行](#learning-4)

<a id="learning-0"></a>

## 模型怎样发现缺少的工具

用户问：“苹果公司最近股价怎么样？有没有相关新闻能解释一下原因？”报价工具能回答前半句，后半句还得查报道，看看有没有能解释这次变动的消息。全量加载让模型一开始就看到整个目录；预筛选用用户的原话查一次目录；主动发现允许模型查过股价后，再专门为新闻查一次。做实验时，把每次检索给出的候选与实际调用的工具并排看，才能分清工具是没被找到，还是找到了却没被使用。

### 目的

当一个 Agent 拥有上百个工具时，常见做法是把全部工具的 JSON schema 一次性塞进 system prompt。
做比较时，可以先问两个问题：

1. **目录占了多少输入**：教学目录中 126 个工具的完整 schema 约 **1.16 万 token**。如果每轮都传完整目录，这段文本会反复进入请求；实际费用取决于服务计价和前缀缓存。
2. **模型会选错吗**：措辞稍泛的任务下，模型可能"广撒网"地把通用兜底工具（`web_search` /
   `google_search` / `universal_search`）和专用工具一起调用，甚至用通用搜索替代专用工具。查股价的任务可以从这里入手：如果要求同时查询新闻，模型同时选报价工具和搜索工具就有理由；要看它有没有漏掉其中一项。

**主动发现**只在 system 里保留少量基础工具 + 一个 `discover_tools(need)` 元工具。模型遇到能力缺口时，
用自然语言描述需求，系统用嵌入相似度从工具库检索 3-5 个最相关的专用工具，把它们的 schema 作为
**user message** 追加进对话（保护 system 前缀的 KV Cache），并更新状态栏可用工具列表。

### 怎样分清是哪一步起了作用

先看[8 月 25 日运行协议](validation/experiment_4_1/rerun_20260825/protocol.json)。全量组把整份定义放在系统提示里；发现组先用嵌入检索挑出最多五项，再把定义随一条用户消息追加到历史末尾，还多了搜索轮次、发现指令和状态栏。目录的 50,597 是用 o200k 编码算出的定义 token 数。正式脚本给 Ollama 请求设置了 `num_ctx=131072`；这个设置和 o200k 数值均不足以判定 Qwen 是否启用了 YaRN，或者模型是否因为超过原生窗口而退化。

要研究**因果关系**，可以在同一模型、同一批题上另做以下配对试验。这些是后续实验设计，原报告只测了整套流程。

| 想检验什么 | 怎样配对，记录什么 |
| --- | --- |
| 输入变长，还是可选工具变多？ | 固定正确工具及其位置，用填充文本拉长同一份目录；再固定模型分词器测得的总长度，把相同长度的填充换成无关工具定义。记录实际入模长度、截断情况和选错工具的次数，并用多种填充复查结果。 |
| 检索器选得好，还是模型选得好？ | 先统计检索候选是否包含必需工具，再把保存的同一批候选交给模型选择。分别报告候选覆盖率，以及在必需工具入选条件下模型选对的比例。 |
| 定义出现的位置有没有影响？ | 固定候选、指令和预算，分别提前或临近选择时提供同一份定义；保持消息角色一致。再固定位置单独比较角色，避免把新近程度与消息角色混为一谈。 |
| 状态栏、发现提示和额外轮次各有什么用？ | 固定候选，依次只切换状态栏或发现指令；另给没有搜索动作的对照组同样多的推理机会。记录实用轮数、选择结果和总输入，再报告各项变化。 |

**动手固定候选，只改顺序。** 在本实验目录运行 `python3 compare_candidate_order.py`，观察同一批五个候选。脚本从 8 月 25 日的股价任务回执取出原问题和第一次发现时的能力描述，再按工具名去归档目录读取完整定义。A 沿用检索器的顺序，B 把第一个候选移到最后；`yfinance_quote` 因此从第三位移到了第二位。

```bash
python3 compare_candidate_order.py --json > candidate-order-pair.json
```

文件里有两个完整的 Ollama 请求，可以逐项比较。系统指令、消息角色、模型选项、问题和每条定义完全一致，两条用户消息的 UTF-8 字节数也相同。两组都是新构造的单步选择题；归档中后续的动作和答案都没有放进题面。脚本只生成输入，不请求模型。字节数相等也不能代替模型分词计数。若以后把两份请求交给同一个模型实例，可以比较它选中了谁，再换几种轮换顺序、换题重复，观察结果是否随候选的位置而变。

### 机制

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
两组都把 schema 作为文本交给模型，再从其回复解析 JSON 调用。这样可以保持调用格式一致，比较工具说明出现的位置和数量。若要判断原生 function calling 是否能减少选错工具，还需要在同一目录和任务上单独对照。

**怎样读一次检索的结果？** 在 `finance+news` 的离线轨迹中，预筛选列出的十个候选既有专用的 `get_stock_price`、`search_news`，也有通用的 `web_search`。候选来自相似度排序，通用工具也可能排在前面。先看候选里有没有办法完成任务，再读调用轨迹，看看模型用了哪一个。

**为什么还要允许再次查目录？** 如果第一次查找没找到报价接口，预筛选组只能从原来的清单里选。主动发现组可以把下一次查询缩小到“查询加密货币的实时价格”。两次查询会得到不同的候选；能否因此办成任务，要看检索结果和随后的调用。下面的离线对照给出了两种失败情形。

<a id="learning-1"></a>

## 选教学目录或正式运行记录

离线演示使用 126 个教学工具；正文实验用了 127 个。先在离线轨迹里找出新工具的定义从哪一步进入上下文，再用正式记录核对股票查询用了哪些工具。

<a id="learning-2"></a>

## 对照工具定义的加载顺序

先运行离线演示，观察查询如何映射到候选工具。选一个需要多个能力的任务，记录每次发现了哪些说明。之后按下文配置模型与真实工具，比较三条路径。

### 运行

```bash
# 在仓库根目录使用统一的第 4 章环境
uv sync --locked --python 3.12 --extra ch4

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch4]"

cd chapter4/active-tool-discovery

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

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

### 离线机制自检（本地嵌入 + mock 模型，`python demo.py --offline`）

下表为一次真实的 `--offline` 运行（8 任务 × 三策略）。**token/延迟是 tiktoken/wall-clock 真实测量**；
**准确率仅反映脚本化启发式路由，不代表真实模型能力**——mock 模型是"强路由器"，不会退化，所以全量注入也拿满分。

| 策略 | 精确选对 | 任务完成 | 平均注入 token | 总注入 token | 平均延迟(s) |
|---|---|---|---|---|---|
| 全量注入 | 8/8 | 8/8 | 11630 | 93040 | 0.008 |
| 检索预筛选 | 4/8 | 4/8 | 1030 | 8236 | 0.006 |
| 主动发现 | 8/8 | 8/8 | 974 | 7796 | 0.010 |

**先算目录开销。** 八个任务合计，全量组注入了 93,040 个工具定义 token，主动发现组注入了 7,796 个，前者约为后者的 11.9 倍。`injected_tokens` 只统计脚本加载的工具说明；要算整次任务的费用，还需要各轮的实际模型用量。保持八个任务不变，用 `--tool-set-size 20` 再跑一次。启动日志显示实际保留了 **27** 个工具，因为基础工具、通用工具和各题评分时接受的工具都要留下。此时两组分别注入 22,464 和 7,842 个 token，比值约为 **2.9**。

**再查预筛选组哪四题没做完。** 在 `crypto+news` 和 `academic(诱导)` 中，十个候选分别缺少能完成加密货币报价、学术检索的工具。另两题却有可用工具：`forex+weather` 有评分规则认可的 `convert_currency`，脚本只调用了天气工具；`opinion(诱导)` 有可用的新闻工具，脚本一次也没调用。可以打开 `tools_library.py` 的 `required_slots` 核对每题接受哪些替代工具。四次失败中，两次需要改候选检索，另两次即使用原来的候选，也还有改进选择的余地。主动发现组在这套脚本化任务中完成了八题。

### 模型 ↔ 脚手架此消彼长（弱模型 gpt-4o-mini vs 强模型 gpt-5.6-luna，均为真实运行）

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

#### 价值一：避免"错选通用工具"—— 随模型变强而**淡出**（fading）

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

#### 价值二：节省注入 token —— 与模型强弱**无关、始终存在**（persisting）

全量注入无论模型强弱都固定为 **11,630 token/任务**（把 126 个工具 schema 全塞进 system），
这是纯结构性开销。按需发现只注入几百到一千余 token：

- 弱模型 gpt-4o-mini：93,040 → 7,266，**~12.8×**；
- 强模型 gpt-5.6-luna：93,040 → 4,733，**~19.7×**（比值更大，部分是因为它常放弃、根本没触发 `discover_tools`，
  只注入 3 个基础工具）。

两个模型上 token 节省都稳稳成立，且随工具集变大而放大——**这份收益不因模型变强而消失**，
是脚手架在"强模型时代"仍然值得保留的硬理由。

#### 一句话小结

> **模型越强，脚手架"帮它别选错工具"的价值越淡（gpt-4o-mini 全量 5/8→发现 8/8 精确、零完成损失；
> gpt-5.6-luna 仅 3/8→4/8 且完成还降了，因为它的失分是"放弃"而非"错选"）；但"省 token"的价值
> 与模型强弱无关、始终存在（弱模型 ~12.8×、强模型 ~19.7×，全量注入恒为 11,630 token/任务）。
> 所以在强模型上，主动工具发现的主要理由从"纠正指令遵循退化"转向"控制上下文成本"。**

<a id="learning-3"></a>

## 检查必需工具是否入选

离线演示展示选择流程，不代表真实模型一定能选对。比较时同时检查工具覆盖、选择正确性、额外查找轮次和上下文消耗。

### 结论（基于一次真实运行，gpt-5.6-luna，2026-07）

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

### 检查自己的解释

如果所需工具从未进入候选列表，应该改目录说明、检索方法还是模型提示词？

<a id="learning-4"></a>

## 实现与正式运行

### 项目说明

> Companion code for *AI Agents in Depth*, Chapter 4 — **Experiment 4-1 ★★★: Proactive Tool Discovery**. The teaching demo compares three strategies on 126 tools. The August manuscript campaign compares full loading and active discovery on 127 MCP tools.
> 配套《深入理解 AI Agent》第 4 章 **实验 4-1 ★★★：主动工具发现**。126 个教学工具用于观察三种策略；正文的 8 月运行从真实 MCP 服务读取 127 个工具，在相同三个任务上对比两种策略。

← [Chapter 4 index / 返回第 4 章目录](../README.md)

### 如何适配 / 扩展

- **换模型**：`MODEL=gpt-4.1-mini python demo.py`（chat 模型）；`EMBED_MODEL=text-embedding-3-large` 换嵌入模型
  （换嵌入模型会因签名变化自动重建 `.cache/` 索引）。
- **换供应商 / 网关**：chat 与 embeddings 都走 OpenAI SDK，`OpenAI()` 会自动读取环境变量 `OPENAI_BASE_URL`，
  因此指向任意 **OpenAI 兼容**的网关/代理只需 `OPENAI_BASE_URL=https://your-gateway/v1`（该端点需同时提供 chat 与 embeddings）。
- **换任务 / 输入**：编辑 `tools_library.py` 里的 `TASKS`（每条含 `prompt` 与判分用的能力槽位），或用
  `--tasks` 只跑其中几条，或用 `--query` 传一句临时需求；想扩充工具库同样在 `tools_library.py` 的 `ALL_TOOLS` 中增删。
- **离线自检**：`--offline` 用 `offline_backend.py` 的本地哈希嵌入 + 脚本化 mock 模型，无需任何 key，
  适合 CI、无网环境或快速验证流水线；它复现的是 token/延迟结构与"检索预筛选一次性漏工具"的机制，
  不复现真实模型在长上下文工具墙下的选择行为（后者见下方 gpt-5.6-luna 真实结果）。

### 文件

- `tools_library.py` — 126 个工具定义 + `select_tools` 子集截取 + mock 执行 + 8 个评测任务与判分标准
- `discovery.py` — 可插拔嵌入后端（`OpenAIEmbedder`）+ 工具向量索引与相似度检索（`discover_tools`/预筛选的后端）
- `agent.py` — 三种策略（全量注入 / 检索预筛选 / 主动发现）的 ReAct 循环与 token 统计
- `offline_backend.py` — 离线后端：`LocalEmbedder` + `MockChatClient`，支撑 `--offline` 无 key 自检
- `demo.py` — 一键多策略对比演示（含 CLI：`--query/--tasks/--strategies/--tool-set-size/--offline/--output` 等）
- `requirements.txt` / `env.example`

---

### 代码阅读顺序

- **Run first:** `python demo.py --offline` (mechanism smoke without credentials); use `run_exact_experiment.py` only for the formal real-tool campaign.
- **Start here:** `discovery.py::ToolIndex` builds/searches the index; `agent.py::run_active_discovery` shows on-demand schema injection.
- **Core behavior:** compare `run_full_injection`, `run_retrieval_prefilter` and `run_active_discovery`; the formal runner’s task loop is in `run_exact_experiment.py::run_agent_task`.
- **State / protocol:** available-tool names, appended schemas, JSON action records and per-task receipts.
- **Verifier:** `test_exact_experiment.py`, `run_exact_experiment.py::derive_acceptance` and the manifest/receipt checks.
- **Experiment variable:** catalog size, retrieval `top_k`, strategy and task mix; compare latency, tokens and exact completion.
- **Skip on first pass:** embedding backends, MCP transport and failure-attempt archival.

### Canonical manuscript campaign / 正式实验活动

`run_exact_experiment.py` replaces the mechanism-only demo for formal
Experiment 4-1 acceptance. It reads the current catalog from the perception MCP server. The August 25 run recorded 127 distinct schemas (50,597 tokens with the shared `o200k` tokenizer). Both arms used local Ollama `qwen3:4b`; active discovery retrieved five candidates with `all-MiniLM-L6-v2`. The runner checked required capabilities and artifacts from adapter-assisted MCP calls. Runs are resumable and store the gzipped catalog, model receipts, MCP
receipts, artifacts, hashes, paired metrics, and an honest hypothesis result.

```bash
python run_exact_experiment.py --campaign-id my-qwen3-4b-run
# after an interruption:
python run_exact_experiment.py --campaign-id my-qwen3-4b-run --resume
```

`demo.py` and `offline_backend.py` remain useful teaching/CI paths, but their
lightweight tool outputs and scripted model do not count as formal evidence.

### 正式运行记录与指标口径

脚本在运行时读取工具目录。要知道这次一共读到了多少个不同的工具，可以查看目录回执的 `unique_tool_count`。当前采用的运行是 [`rerun_20260825/summary.json`](validation/experiment_4_1/rerun_20260825/summary.json)，使用本地 Ollama `qwen3:4b` 和真实 MCP 服务提供的 127 个工具。其 manifest SHA-256 为 `e5a70588804b8bc1a5ba38c18fe7f4537e8284e62f745d8a6e03401833046dae`。[7 月 30 日的目录回执](validation/experiment_4_1/qwen3_4b_exact_v2_20260730T130600Z/catalog_receipt.json)记录的是 126 个真实工具、50,120 个 schema token；教学目录虽然也是 126 个工具，定义内容不同。核对旧运行的调用与产物时，应从[该次汇总](validation/experiment_4_1/qwen3_4b_exact_v2_20260730T130600Z/summary.json)进入。

| 项目 | 全量加载 | 主动发现 |
| --- | ---: | ---: |
| 每任务初始系统提示词 token | 50,829 | 1,251 |
| 股价与新闻任务追加的定义 token | 0 | 3,939 |
| 论文检索与下载任务追加的定义 token | 0 | 1,853 |
| 贡献者图表任务追加的定义 token | 0 | 2,632 |
| 覆盖全部必需能力的任务 | 3/3 | 3/3 |
| 适配层执行后通过产物检查的任务 | 3/3 | 3/3 |
| 记录中的三任务耗时合计（秒） | 3,056.294 | 783.442 |

以上 token 使用 `o200k` 分词器统一计数，描述的是文本规模，Qwen 的实际分词量应读取模型运行记录。全目录的 schema 文本为 50,597 token，系统提示词还包含任务规则等内容。新增定义量也应与累计推理输入量分开统计：已加载定义会随历史进入后续请求。

先打开[苹果股价任务的主动发现回执](validation/experiment_4_1/rerun_20260825/treatment/apple_stock_news/receipt.json)。在 `discoveries[0].matches` 里从上往下数，实际调用的 `yfinance_quote` 排第三。再查 `initial_schema_names`，第二个实际调用的工具 `web_search` 从一开始就可用。这两次选择分别来自新发现的工具和已有工具。

现在遮住 `final_answer`，只看 `execution.receipts`。第一条工具回执足以复算涨幅：用（310.34 − 309.35）除以 309.35，约为 0.32%。第二条回执中的五个搜索摘要提供了哪些新闻线索？它们主要给出价格、成交量等行情。凭这些材料，可以向用户说明这次检索还没有找到涨价原因；要断定当天没有相关新闻，还需要更多证据。

运行器的 `grade_plan` 按每个任务的必需能力槽位计分：某槽位至少有一个工具被选中，就记为命中。回执中的 `accuracy=1.0` 表示全部必需能力均被覆盖；该指标不扣除无关调用，也不检查调用参数和最终答案。正文据此使用“必需能力覆盖”这一名称。

`_call_real_tool` 在执行前填写或替换参数：股票代码固定为 AAPL，新闻查询固定为 Apple AAPL stock，论文检索固定为 transformer，GitHub 仓库固定为 openai/openai-python；下载调用按搜索结果展开为三次下载，代码执行调用使用运行器根据贡献者数据生成的 SVG 绘图代码。因此，产物由模型选择能力与适配层组织执行共同完成。评估模型自主生成参数或程序时，需要另设保留原始参数的实验。

`_finalize_execution` 检查必需能力是否执行成功，并检查三份 PDF 的数量、文件签名与大小，以及图表的 SVG 签名与大小。论文相关性、新闻对股价变动的解释、图表内容正确性及最终回答质量需要独立评估。现有十二项门禁记录的是上述执行合同的通过情况。

当前运行仍出现解析错误：全量加载组三个任务分别为 1、1、2 次，主动发现组分别为 4、6、1 次（按股价、论文、贡献者顺序）。全量加载组的贡献者任务还包含重复查询和 `file_stat` 调用。主动发现组的股价任务选择了 `yfinance_quote` 与 `web_search`；旧记录中的空图表和过早结束属于先前运行，应查阅相应历史回执。表中耗时保留为本次运行记录，速度比较还受解析重试、模型运行环境、外部接口响应与执行适配层影响。

复现时依次检查 catalog、模型决策、适配后的 MCP 参数与产物；若要比较端到端任务质量，应补充任务相关性、参数正确性、额外调用和最终回答的评价标准。

---

## Notes / 说明

- Commands, paths, env vars, and measured tables are identical on both language sides.  
- 两侧命令、路径、环境变量与实测表格保持一致。  
- Offline path needs no API key; real-model tables are single-run, non-deterministic (temperature=1).  
- 离线路径无需 API Key；真实模型表为单次非确定性运行（temperature=1）。

## English

### Purpose

When an Agent has hundreds of tools, a common approach is to inject every tool JSON schema into the system prompt. That creates two problems:

1. **Token waste**: Full schemas for 126 tools are about **11.6k tokens**, re-billed on every reasoning step.
2. **Instruction-following degradation**: On slightly vague tasks, the model “casts a wide net” and calls generic fallbacks (`web_search` / `google_search` / `universal_search`) together with specialized tools—or even replaces specialized tools with generic search (e.g. looking up a stock price via generic `web_search`).

**Active discovery** keeps only a few base tools plus a `discover_tools(need)` meta-tool in the system prompt. When the model hits a capability gap, it describes the need in natural language; the system retrieves the 3–5 most relevant specialized tools via embedding similarity, appends their schemas as a **user message** (protecting the system-prefix KV cache), and updates the status bar of available tools.

### Mechanisms

```
tools_library.py   126 cross-domain teaching tools (finance/web/arxiv/github/geo/weather/media/...; 17 domains)
                   demo.py uses lightweight outputs; the formal runner instead uses perception MCP schemas/execution
                   Intentionally mixes 8 generic/near-synonym tools (web_search, etc.) with inflated descriptions
                   select_tools(size): subset by --tool-set-size to show full injection cost growing with catalog size
discovery.py       Pluggable embedding backend + tool vector index; OpenAIEmbedder uses text-embedding-3-small
                   and caches to .cache/; search(need) = embed need, cosine similarity vs tool vectors, return top-k
agent.py           Three ReAct strategies (text protocol: model outputs one JSON tool call per step)
                   - run_full_injection: all 126 schemas in system prompt
                   - run_retrieval_prefilter: one-shot top-n retrieve by initial query (book’s “retrieval prefilter”)
                   - run_active_discovery: base tools + discover_tools; retrieve-on-demand during execution
offline_backend.py Offline backend: LocalEmbedder (local bag-of-words hash) + MockChatClient (scripted mock)
                   so --offline runs end-to-end without any API key (token/latency real; accuracy = heuristic routing)
demo.py            Same tasks under selected strategies; prints token / latency / call traces / exact match; summary table
```

**Why “text inject + text parse” instead of native OpenAI function calling?**  
Native function-calling is heavily optimized for tool choice and rarely errs even with hundreds of tools, so it cannot demonstrate long-context instruction-following degradation. Putting schemas in the prompt as plain text and letting the model emit JSON tool calls is the control condition—and matches the book’s “inject schemas into the system prompt (tens of thousands of tokens)” setup.

**Why does embedding retrieval reduce wrong picks?** Generic tools like `web_search` claim to “do everything,” so their semantics are diluted; specialized tools (e.g. `search_news`) have focused descriptions. For a focused `need` (“recent Tesla news”), specialized tools score higher and rank first; generics often never enter top-k and are never loaded—retrieval acts as a precision filter.

**Why isn’t retrieval prefilter enough?** Prefilter (`run_retrieval_prefilter`) matches only the **initial query** once and injects top-n tools. On multi-step cross-domain tasks (e.g. stock price + news), the initial vector often favors the first domain; the second sub-task’s specialized tool may miss top-n. Active discovery defers discovery until each real `need` appears and retrieves separately (see the candidate lists and calls in the offline comparison below below).

### How to run

```bash
# From the repository root: use the shared Chapter 4 environment
uv sync --locked --python 3.12 --extra ch4

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch4]"

cd chapter4/active-tool-discovery

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

# Path A: offline mechanism self-check (no keys; token/latency real; accuracy = heuristic routing only)
python demo.py --offline

# Path B: real model (needed for small-model instruction-following degradation)
cp env.example .env    # set OPENAI_API_KEY (chat + embeddings both use OpenAI)
# Fallback: if OPENAI_API_KEY is unset but OPENROUTER_API_KEY is set, chat routes via OpenRouter
# (model mapped to openai/gpt-5.6-luna, etc.); tool retrieval falls back to local hash embeddings
# (OpenRouter has no embeddings API).
python demo.py                                   # all 8 tasks × three strategies
python demo.py --strategies full,discovery       # compare only two strategies
python demo.py --tasks finance+news,crypto+news  # selected tasks (comma-separated)
python demo.py --tasks 'opinion(诱导)'            # quote task ids that contain parentheses
python demo.py --tool-set-size 20                # smaller catalog: full-injection disadvantage shrinks
python demo.py --query '查英伟达股价再搜点相关新闻' --offline   # one-off natural-language task
python demo.py --offline --output results/offline.json         # export structured results
```

Default model `gpt-5.6-luna`; override with `--model` or env: `python demo.py --model gpt-5.6-luna`.  
First run builds tool embeddings and caches under `.cache/`. Full flags: `python demo.py --help`  
(`--query / --tasks / --strategies / --tool-set-size / --top-k / --prefilter-n / --model / --embed-model / --max-steps / --offline / --output`).

### Adaptation / extension

- **Swap chat model**: `MODEL=gpt-4.1-mini python demo.py`; swap embeddings with `EMBED_MODEL=text-embedding-3-large` (cache rebuilds automatically when the embed signature changes).
- **Swap provider / gateway**: chat and embeddings both use the OpenAI SDK; `OpenAI()` reads `OPENAI_BASE_URL`, so any **OpenAI-compatible** gateway works via `OPENAI_BASE_URL=https://your-gateway/v1` (endpoint must offer both chat and embeddings).
- **Swap tasks / inputs**: edit `TASKS` in `tools_library.py` (each has `prompt` and scoring capability slots), or use `--tasks` / `--query`; grow/shrink the catalog in `ALL_TOOLS` in the same file.
- **Offline self-check**: `--offline` uses `offline_backend.py` (local hash embeddings + scripted mock). Good for CI / offline / pipeline smoke tests. It reproduces token/latency structure and the distinction between missing candidates and unused alternatives, not real-model long-context choice behavior (see real gpt-5.6-luna results below).

### Offline mechanism self-check (`python demo.py --offline`)

One real `--offline` run (8 tasks × three strategies). **Token/latency are real tiktoken/wall-clock**; **accuracy only reflects scripted heuristic routing**, not a real model—the mock is a “strong router” and never degrades, so full injection also scores perfectly.

| Strategy | Exact match | Task complete | Avg inject tokens | Total inject tokens | Avg latency (s) |
|---|---|---|---|---|---|
| Full injection | 8/8 | 8/8 | 11630 | 93040 | 0.008 |
| Retrieval prefilter | 4/8 | 4/8 | 1030 | 8236 | 0.006 |
| Active discovery | 8/8 | 8/8 | 974 | 7796 | 0.010 |

Two **real, reproducible structural** takeaways:

1. **Tokens diverge as catalog size grows**: full injection is fixed at 11,630 tokens/task; prefilter and discovery inject ~1,000 (**~11.9×** smaller). With `--tool-set-size 20`, the eight tasks require 27 tools after the base tools, generic tools, and accepted alternatives are retained. The totals are 22,464 and 7,842 definition tokens, a ratio of about 2.9.
2. **Compare candidates with calls.** Prefilter missed a required capability in `crypto+news` and `academic(诱导)`. The other two failures had acceptable candidates: the mock router skipped `convert_currency` in `forex+weather` and made no news call in `opinion(诱导)`. Active discovery completed all eight scripted tasks.

### Conclusions (one real run, gpt-5.6-luna, 2026-07)

> One real LLM run (`python demo.py --model gpt-5.6-luna`, 8 tasks × three strategies, OpenAI chat + `text-embedding-3-small`). gpt-5.6-luna is a reasoning model that only supports default `temperature=1` (no `temperature=0`; code falls back on that error), so this is a **single non-deterministic** run. Scoring: ✅ exact match (all capability slots, no generic fallback misuse); ⚠️ completed but also picked a generic tool; ❌ failed (missed specialized tool, abandoned, or 0 tool calls).

| Task | Full | Prefilter | Discovery | Full tokens | Discovery tokens |
|---|---|---|---|---|---|
| finance+news | ✅ | ❌ | ✅ | 11630 | 883 |
| arxiv+download | ✅ | ❌ | ✅ | 11630 | 927 |
| github+viz | ❌ | ❌ | ❌ | 11630 | 295 |
| weather+calendar | ❌ | ✅ | ✅ | 11630 | 1055 |
| forex+weather | ✅ | ✅ | ❌ | 11630 | 295 |
| crypto+news | ❌ | ⚠️ | ❌ | 11630 | 295 |
| opinion(诱导) | ⚠️ | ❌ | ✅ | 11630 | 688 |
| academic(诱导) | ⚠️ | ⚠️ | ❌ | 11630 | 295 |
| **Exact match** | **3/8** | **2/8** | **4/8** | | |
| **Task complete** | **5/8** | **4/8** | **4/8** | | |
| **Total inject tokens** | | | | **93040** | **4733** |

(Prefilter avg 971 tokens/task, total 7768; mean latency ~11.5 / 9.6 / 10.7 s for the three strategies—measured this run.)

1. **Token savings remain robust**: full injection fixed at **11,630 tokens/task**; discovery **295–1,055**, total 93,040 → 4,733 (**~19.7×**). Part of the larger ratio is gpt-5.6-luna abandoning some tasks without `discover_tools` (only 3 base tools = 295 tokens). The structural gain still holds: full injection re-bills tens of thousands; on-demand injects thousands or fewer.

2. **Book core phenomenon on two “inducement” tasks**: with vague wording, full injection grabs generic fallbacks—
   - `opinion(诱导)`: full called `search_news, search_news, web_search, search_tweets` (⚠️ included generic **`web_search`**); discovery retrieved `search_news / get_news_by_source / ...` (**no** `web_search`) and only used specialized news tools (✅).
   - `academic(诱导)`: full called 8 tools including **`google_search / universal_search / ask_knowledge_base`** (⚠️); prefilter also misused `google_search / universal_search`.

3. **Another real behavior this run**: conservative reasoning models sometimes **`finish` with 0 tool calls** (“cannot access real-time data”), lowering absolute accuracy for all strategies. Main failure mode was abandon/skip steps—not only wrong tool choice—and it appears under both full injection and discovery.

4. **Boundaries**:
   - Control setup is “schemas as plain text + model emits JSON tool calls”; mock tools return placeholders, so conservative models may refuse—major source of low accuracy here.
   - With `temperature=1` only, per-task outcomes vary across runs; structural conclusions (token savings; full injection misusing generics on inducement tasks) stay directionally stable.
   - For cleaner, reproducible mechanism checks (definition tokens, latency, and candidate coverage), use the `--offline` table above.

> **One line:** On gpt-5.6-luna, active discovery’s steadiest win is still tokens (~19.7× this run); on vague inducement tasks, embedding retrieval keeps inflated generics (`web_search` / `google_search` / `universal_search`) out of the candidate set. Strong reasoners’ conservative “give up” behavior also lowers absolute accuracy for every strategy—read the table above as-is.

### Model ↔ scaffolding trade-off (weak gpt-4o-mini vs strong gpt-5.6-luna)

> Does stronger models make this scaffolding useless? Comparing the gpt-5.6-luna (strong) run with a gpt-4o-mini (weak) run on the same 8 tasks × three strategies (`python demo.py --model gpt-4o-mini`, 2026-07, same scoring). Scaffolding has two values: one **fades** as models strengthen; one is **model-independent**.

**Weak model gpt-4o-mini real summary:**

| Strategy | Exact match | Task complete | Total inject tokens | Avg latency (s) |
|---|---|---|---|---|
| Full injection | 5/8 | **8/8** | 93040 | 8.38 |
| Retrieval prefilter | 7/8 | 7/8 | 7768 | 4.90 |
| Active discovery | **8/8** | **8/8** | 7266 | 7.65 |

(token 93040 → 7266, **~12.8×**.)

#### Value 1: avoid misusing generic tools — **fades** with stronger models

- **Weak gpt-4o-mini:** under full injection never abandons (8/8 complete) but wide-nets generics on 3 tasks → **5/8 exact**. Discovery blocks inflated generics: **8/8 exact, 0 generic misuse, still 8/8 complete** (+3 exact tasks, zero completion loss).
- **Strong gpt-5.6-luna:** generic misuse only on 2 inducement tasks; discovery cleans those but exact only **3/8 → 4/8 (+1)** and completion **falls 5/8 → 4/8**. Main failure is abandon, not wrong pick—retrieval cannot fix “no tool call at all.” The weakness scaffolding targets is thin on strong models, so that value fades.

#### Value 2: inject-token savings — **persists** regardless of model strength

Full injection is always **11,630 tokens/task** (all 126 schemas in system). On-demand injects a few hundred to ~1k:

- Weak gpt-4o-mini: 93,040 → 7,266, **~12.8×**
- Strong gpt-5.6-luna: 93,040 → 4,733, **~19.7×** (larger partly because abandon skips `discover_tools`)

Token savings hold on both models and grow with catalog size—the hard reason to keep scaffolding in the strong-model era.

#### One-line summary

> **Stronger models weaken “help it not pick the wrong tool”** (gpt-4o-mini full 5/8→discovery 8/8 exact, zero completion loss; gpt-5.6-luna only 3/8→4/8 and completion drops, because losses are “abandon” not “wrong pick”). **Token savings stay** (~12.8× / ~19.7×). On strong models, the main case for active discovery shifts from “fix instruction-following degradation” to “control context cost.”

### Files

- `tools_library.py` — 126 tool defs + `select_tools` + mock execution + 8 eval tasks / scoring
- `discovery.py` — pluggable embedders (`OpenAIEmbedder`) + vector index / similarity search
- `agent.py` — three strategies (full / prefilter / discovery) ReAct loops + token stats
- `offline_backend.py` — `LocalEmbedder` + `MockChatClient` for `--offline`
- `demo.py` — multi-strategy CLI demo
- `requirements.txt` / `env.example`

---

### 实验 4-1 的工具选择对照

原实验比较两种完整的工具使用流程，同时改变了上下文、候选工具和交互历史。
要单独观察第一次选工具的表现，可以复用同一轮实验保存的工具目录和检索结果：

```bash
python selection_ablation.py > selection-results.json
```

使用与精确实验相同的 Python 环境和本地 Ollama 模型 `qwen3:4b`。
`--task apple_stock_news` 只运行一个任务，`--seed` 控制候选抽样和模型随机种子。
每种条件使用相同任务、指令和生成预算，每次独立发起单轮请求。所有条件都省略状态栏和发现工具的引导语。
检索候选来自历史运行针对该任务的第一次发现，重放时无需在线检索或执行工具。

| 比较 | 观测内容 |
| --- | --- |
| short 与 long | 保留同一组检索结果和位置，在系统消息前部加入无任务信息的填充，观察输入变长的影响。 |
| long 与 more_distractors | 保留原有候选，另加同等数量的非正确工具。在等长输入下观察干扰工具的影响。 |
| long 与 random_shortlist | 用从完整目录随机抽取的相同数量工具替换检索候选。在等长输入下比较两种筛选方式。 |
| long 与 user_schemas | 保留相同候选，把 schema 从系统消息移到任务后的用户消息，观察放置方式的影响。 |

后三组比较都以 Ollama 返回的实际输入长度 6144 token 为准，模型窗口固定为 8192。
填充校准请求的回复不进入评分或下一条消息。每行输出包含候选工具、标准答案是否在候选内
（`gold_available`）、模型选择、正确性、实际 token 数和请求哈希。分析检索效果时先看候选覆盖率，
再看有正确候选时模型是否选对。这里只有三个任务，结果描述的是第一步选择；
完整任务的执行和完成率仍由原实验单独测量。
